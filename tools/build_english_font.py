"""Convert the requested OFL font into native 26x26, 4-bit BNF glyphs.

Only Latin glyphs and common English punctuation change. Existing Japanese
glyphs remain byte-exact. Widths are installed in the game's native table.
"""
import hashlib
import math
import re
import struct
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_branding import ROOT, SOURCE
from bnf_codec import decode_record, encode_record

FONT_FILE = ROOT / 'tools/fonts/genei-latin/GenEiLatin-Separate_v2.1/GenEiLateGoN_v2.ttf'
FONT_SHA256 = '39f4f7a7bf92586ab40df059d08f6202c0b28472c6cd4374bf3dd3a9ad2b70f7'
FONT_SIZE = 22
BASELINE = 20
CELL = 26
ALIASES = {c + 0xfee0: c for c in range(33, 127)}
CHARACTERS = set(range(32, 127)) | {0x2013, 0x2014, 0x2015, 0x2018, 0x2019, 0x201c, 0x201d, 0x2026}
CONTROL = re.compile(r'#n|#(?:[A-Za-z]|=)[0-9]*')
BODY_WIDTH = 670
NAME_WIDTH = 212


@lru_cache(None)
def face(size=FONT_SIZE):
    if hashlib.sha256(FONT_FILE.read_bytes()).hexdigest() != FONT_SHA256:
        raise ValueError('Requested font file hash mismatch')
    return ImageFont.truetype(str(FONT_FILE), size)


@lru_cache(None)
def glyph(character):
    """Antialiased mask, low nibble first, with the game's fixed baseline."""
    scale = 4
    font = face(FONT_SIZE * scale)
    bbox = font.getbbox(chr(character), anchor='ls')
    # The pipe extends above/below the normal Latin em box. Fit oversized
    # symbols into the existing cell without cropping their strokes.
    fitted_size = FONT_SIZE * scale
    while bbox[3] - bbox[1] > CELL * scale:
        fitted_size -= 1
        font = face(fitted_size)
        bbox = font.getbbox(chr(character), anchor='ls')
    baseline = max(-bbox[1], min(BASELINE * scale, CELL * scale - bbox[3]))
    left = max(0, -bbox[0])
    if left + bbox[2] > CELL * scale or baseline + bbox[1] < 0 or baseline + bbox[3] > CELL * scale:
        raise ValueError('Glyph exceeds native cell: ' + hex(character))
    image = Image.new('L', (CELL * scale, CELL * scale))
    draw = ImageDraw.Draw(image)
    if character == ord(':'):
        # GenEi's colon has its upper dot above the Latin x-height. Use two
        # of the same font's period dots at Latin colon heights instead.
        for offset in (0, -9 * scale):
            draw.text((left, baseline + offset), '.', font=font, anchor='ls', fill=255)
    else:
        draw.text((left, baseline), chr(character), font=font, anchor='ls', fill=255)
    image = image.resize((CELL, CELL), Image.Resampling.LANCZOS)
    values = [(v + 8) // 17 for v in image.tobytes()]
    raw = bytes(a | b << 4 for a, b in zip(values[::2], values[1::2]))
    if len(raw) != 338:
        raise ValueError('Invalid glyph bitmap length')
    return raw


@lru_cache(None)
def widths():
    result = {c: max(1, round(face().getlength(chr(c)))) for c in CHARACTERS}
    result.update({target: result[source] for target, source in ALIASES.items()})
    return result


def kerning():
    raw = (SOURCE / 'data/_dat/kerning.bnd').read_bytes()
    groups, payload, unknown, table, count, other, other_count = struct.unpack_from('<7I', raw)
    if (groups, unknown, table, count, other_count) != (2, 0, 28, 167, 14):
        raise ValueError('Unexpected kerning layout')
    relocation_count = struct.unpack_from('<I', raw, payload)[0]
    if payload + 4 + relocation_count * 4 != len(raw):
        raise ValueError('Invalid kerning footer')
    cells = set(struct.unpack_from('<' + str(relocation_count) + 'I', raw, payload + 4))
    records = {}
    for i in range(count):
        cell = table + i * 12
        pointer, flags, dimensions = struct.unpack_from('<III', raw, cell)
        if not pointer:
            if i != count - 1 or flags or dimensions or cell in cells:
                raise ValueError('Invalid kerning sentinel')
            continue
        if cell not in cells:
            raise ValueError('Missing kerning relocation')
        records[struct.unpack_from('<H', raw, pointer)[0]] = (pointer, flags, dimensions)
    modified = bytearray(raw[:payload])
    for character, width in sorted(widths().items()):
        if character in records:
            pointer = records[character][0]
        else:
            pointer = len(modified)
            modified.extend(struct.pack('<HH', character, 0))
        records[character] = (pointer, 0, width | width << 16)
    new_table = len(modified)
    # The native loader stops filling ASCII widths at the first >255 character.
    # In particular, the new ASCII space record must precede all Unicode records.
    for character, record in sorted(records.items()):
        cells.add(len(modified))
        modified.extend(struct.pack('<III', *record))
    modified.extend(bytes(12))
    struct.pack_into('<I', modified, 4, len(modified))
    struct.pack_into('<II', modified, 12, new_table, len(records) + 1)
    footer = struct.pack('<I', len(cells)) + struct.pack('<' + str(len(cells)) + 'I', *sorted(cells))
    if modified[20:payload] != raw[20:payload]:
        raise ValueError('Unrelated kerning bytes changed')
    return bytes(modified) + footer


@lru_cache(None)
def advances():
    raw = kerning()
    table, count = struct.unpack_from('<II', raw, 12)
    result = {}
    for i in range(count - 1):
        pointer, flags, dimensions = struct.unpack_from('<III', raw, table + i * 12)
        result[struct.unpack_from('<H', raw, pointer)[0]] = max(struct.unpack('<hh', struct.pack('<I', dimensions)))
    return result


def measure(text, percentage=100):
    return sum(advances().get(ord(c), 26) for c in CONTROL.sub('', text)) * percentage / 100


def _wrap(words, width):
    lines, line = [], ''
    for word in words:
        candidate = (line + ' ' + word) if line else word
        if measure(candidate) <= width:
            line = candidate
        else:
            if not line or measure(word) > width:
                raise ValueError('English word exceeds dialogue width')
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def layout_dialogue(text):
    if not text:
        return text, 0, 100
    words = text.replace('#n', ' ').split()
    lines = _wrap(words, BODY_WIDTH)
    percentage = 100
    if len(lines) > 2:
        # #z80 sets the native size to 800/1000. Three 36px source line
        # advances plus a 26px cell then occupy <=79px at the source position.
        percentage = 80
        lines = _wrap(words, BODY_WIDTH / .8)
    if len(lines) > 3:
        raise ValueError('English dialogue exceeds three fitted lines')
    prefix = '#z80' if percentage == 80 else ''
    result = prefix + '#n'.join(lines)
    if CONTROL.findall(text.replace('#n', '')) != CONTROL.findall(result[len(prefix):].replace('#n', '')):
        raise ValueError('Non-layout dialogue control changed')
    if re.sub(r'\s+', '', CONTROL.sub('', result)) != re.sub(r'\s+', '', CONTROL.sub('', text)):
        raise ValueError('Dialogue wording changed by layout')
    return result, len(lines), percentage


def layout_name(name):
    match = re.search(r'#z([0-9]+)', name)
    percentage = int(match[1]) if match else 100
    width = measure(name, percentage)
    if width <= NAME_WIDTH:
        return name, percentage
    percentage = min(percentage, math.floor(NAME_WIDTH / measure(name) * 100))
    if match:
        name = name[:match.start()] + '#z' + str(percentage) + name[match.end():]
    else:
        name = '#z' + str(percentage) + name
    return name, percentage


def generate_fonts():
    replacements = {}
    for filename in ['data/_font/zenfont.bnf', 'data/_font/zenfont_deco.bnf']:
        raw = (SOURCE / filename).read_bytes()
        ranges = [struct.unpack_from('<II', raw, i * 8) for i in range(5)]
        characters = [c for first, last in ranges for c in range(first, last + 1)]
        count = len(characters)
        offsets = list(struct.unpack_from('<' + str(count) + 'I', raw, 40)) + [len(raw)]
        if offsets[0] != 40 + count * 4 or any(a >= b for a, b in zip(offsets, offsets[1:])):
            raise ValueError('Unexpected font glyph offsets')
        modified = bytearray(raw[:40] + bytes(count * 4))
        for i, character in enumerate(characters):
            source = ALIASES.get(character, character)
            if source in CHARACTERS:
                bitmap = glyph(source)
                packed = encode_record(bitmap)
                if decode_record(packed) != bitmap:
                    raise ValueError('Font glyph did not round trip')
            else:
                packed = raw[offsets[i]:offsets[i + 1]]
            decode_record(packed)
            struct.pack_into('<I', modified, 40 + i * 4, len(modified))
            modified.extend(packed)
        replacements[filename] = bytes(modified)
    return replacements


def report():
    return {'family': 'GenEi LateGo v2', 'weight': 'Medium',
            'bitmap_derivative_name': 'Cross Ange English Bitmap',
            'source': 'https://okoneya.jp/font/genei-latin.html',
            'download': 'https://okoneya.jp/font/GenEiLatin-Separate_v2.1.zip',
            'source_file': FONT_FILE.relative_to(ROOT).as_posix(), 'source_sha256': FONT_SHA256,
            'license': 'SIL Open Font License 1.1', 'license_file': 'sce_sys/font-license.txt',
            'raster_size': FONT_SIZE, 'glyph_cell': [CELL, CELL], 'baseline': BASELINE,
            'supersampling': 4, 'pixel_format': '4-bit alpha, low nibble first',
            'native_zero_token_terminators': True,
            'native_proportional_advances': True, 'native_line_width': BODY_WIDTH,
            'latin_colon': 'GenEi period dots, baseline and nine pixels above baseline',
            'changed_glyphs_per_font': len(CHARACTERS) + len(ALIASES),
            'runtime_tested': False}
