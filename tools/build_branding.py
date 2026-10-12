"""Preview title branding; --write builds a fresh, versioned local test candidate.

Pillow renders new UI text. Original atlas pixels and palette remain intact.
The CPK writer relocates two changed members and the existing ETOC without
changing other payloads. This is a local test candidate, not a verified release.
"""
import argparse
import hashlib
import io
import json
import re
import shutil
import struct
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from cpk_extract import table, utf
from dr12ae_extract import MAGIC, unwrap
from shtx_extract import png

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'work/source/archive/assets'
CPK = ROOT / 'work/source/decrypted/cpk/Ange.cpk'
ATLAS = 'data/_ssa/title_set.btx'
ANIMATION = 'data/_ssa/title_copyright.bsa'
RECT = (0, 300, 960, 387)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def version_tuple(value):
    if not re.fullmatch(r'0\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError('Version must have the form 0.x.y without leading zeros')
    return tuple(map(int, value.split('.')))


def next_version(current, requested=None):
    parts = version_tuple(current)
    target = requested or f'0.{parts[1]}.{parts[2] + 1}'
    if version_tuple(target) <= parts:
        raise ValueError('Every build must use a newer version')
    return target


def font(size, bold=False):
    from build_english_font import face
    return face(size)


def literal_wrapper(data):
    # FCAA literal tokens: five high length bits and optional low length byte.
    body = bytearray()
    for start in range(0, len(data), 8191):
        block = data[start:start + 8191]
        n = len(block)
        body.extend(bytes([n]) if n < 32 else bytes([32 | (n >> 8), n & 255]))
        body.extend(block)
    result = MAGIC + struct.pack('<II', len(data), len(body) + 12) + body
    if unwrap(result)[0] != data:
        raise ValueError('Compressed animation did not round-trip')
    return result


def footer_assets(version, credits):
    original = (SOURCE / ATLAS).read_bytes()
    if original[:12] != b'SHTXFS\x00\x04\x00\x04\x0a\x0a':
        raise ValueError('Unsupported title atlas dimensions or signature')
    if len(original) != 12 + 1024 + 1024 * 1024:
        raise ValueError('Unexpected title atlas length')
    indices = Image.frombytes('L', (1024, 1024), original[1036:])
    if indices.crop(RECT).getbbox() is not None:
        raise ValueError('Reserved footer area contains original artwork')
    layer = Image.new('RGBA', (960, 87))
    draw = ImageDraw.Draw(layer)
    lines = [(f'v{version}', 15, 23), (credits['project_url'], 14, 45)]
    line_boxes = []
    for text, size, top in lines:
        face = font(size)
        box = draw.textbbox((944, top), text, font=face, anchor='rt', stroke_width=1)
        if box[0] < 0 or box[2] > 946 or box[3] >= 64:
            raise ValueError('Footer text would overlap the copyright notice')
        draw.text((944, top), text, font=face, anchor='rt', fill='white',
                  stroke_width=1, stroke_fill=(0, 0, 0, 255))
        line_boxes.append({'text': text, 'screen_bounds': [box[0], 446 + box[1], box[2], 446 + box[3]]})
    # Palette-preserving quantization: match premultiplied colors, including alpha.
    palette = [tuple(original[12 + i*4:16 + i*4]) for i in range(256)]
    def premult(color):
        r, g, b, a = color
        return (r*a/255, g*a/255, b*a/255, a)
    colors = [premult(c) for c in palette]
    lookup = {(0, 0, 0, 0): 0}
    encoded = bytearray()
    for color in layer.getdata():
        if color not in lookup:
            value = premult(color)
            lookup[color] = min(range(256), key=lambda i: sum((a-b)**2 for a, b in zip(value, colors[i])))
        encoded.append(lookup[color])
    replacement = Image.frombytes('L', layer.size, bytes(encoded))
    # Copyright moves within the atlas, but stays at exactly its original screen coordinates.
    replacement.paste(indices.crop((0, 233, 960, 256)), (0, 64))
    indices.paste(replacement, (0, 300))
    modified = original[:1036] + indices.tobytes()
    if modified[:1036] != original[:1036]:
        raise ValueError('Original texture palette changed')
    for y in range(1024):
        a, b = original[1036+y*1024:1036+(y+1)*1024], modified[1036+y*1024:1036+(y+1)*1024]
        if (not 300 <= y < 387 and a != b) or (300 <= y < 387 and a[960:] != b[960:]):
            raise ValueError('Original texture pixels changed outside the reserved rectangle')
    image = Image.open(io.BytesIO(png(modified, 1024, 1024))).convert('RGBA')
    original_image = Image.open(io.BytesIO(png(original, 1024, 1024))).convert('RGBA')
    if image.crop((0, 364, 960, 387)).tobytes() != original_image.crop((0, 233, 960, 256)).tobytes():
        raise ValueError('Copyright pixel preservation failed')

    packed = (SOURCE / ANIMATION).read_bytes()
    decoded, layers = unwrap(packed)
    if layers != 1 or len(decoded) != 1188 or decoded[:4] != b'SSAD':
        raise ValueError('Unexpected title copyright animation')
    changed = bytearray(decoded)
    if changed[0x1ac:0x1b4] != b'AREA\x10\x00\x00\x00' or struct.unpack_from('<4i', changed, 0x1b4) != (0, 233, 960, 256):
        raise ValueError('Copyright source rectangle changed')
    if changed[0x1d0:0x1d8] != b'ORGY\x04\x00\x00\x00' or struct.unpack_from('<i', changed, 0x1d8)[0] != 11:
        raise ValueError('Copyright source origin changed')
    struct.pack_into('<4i', changed, 0x1b4, *RECT)
    struct.pack_into('<i', changed, 0x1d8, 75)
    allowed = set(range(0x1b4, 0x1c4)) | set(range(0x1d8, 0x1dc))
    if any(a != b and i not in allowed for i, (a, b) in enumerate(zip(decoded, changed))):
        raise ValueError('Animation keys or hierarchy changed')
    preview = Image.new('RGBA', (960, 100), (12, 17, 26, 255))
    preview.alpha_composite(image.crop(RECT), (0, 5))
    return {ATLAS: modified, ANIMATION: literal_wrapper(bytes(changed))}, image, preview, line_boxes


def credits_page(version, credits):
    image = Image.new('RGB', (960, 544), '#101823')
    draw = ImageDraw.Draw(image)
    draw.line((56, 130, 904, 130), fill='#66bdcf', width=2)
    draw.text((56, 38), credits['title'], fill='white', font=font(30, True))
    draw.text((56, 80), credits['subtitle'], fill='#b7cbd9', font=font(20))
    draw.text((56, 153), credits['heading'], fill='white', font=font(26, True))
    y = 199
    for section in credits['sections']:
        draw.text((56, y), section['heading'], fill='#66bdcf', font=font(18, True))
        y += 25
        for line in section['lines']:
            box = draw.textbbox((56, y), line, font=font(19))
            if box[2] > 904 or box[3] > 440:
                raise ValueError('Credits content exceeds page; add another page')
            draw.text((56, y), line, fill='white', font=font(19))
            y += 22
        y += 10
    draw.line((56, 469, 904, 469), fill='#344858')
    draw.text((56, 488), credits['footer'], fill='#b7cbd9', font=font(14))
    draw.text((904, 488), f'v{version}', fill='white', font=font(15), anchor='rt')
    return image


def fields(data):
    """Locate numeric UTF cells without rebuilding strings or table schemas."""
    if data[:4] != b'@UTF':
        raise ValueError('Only the verified unencrypted CPK tables are supported')
    rows, strings, _, _, count, width, row_count = struct.unpack_from('>IIIIHHI', data, 8)
    rows += 8
    strings += 8
    schema, p, row_p = {}, 32, 0
    formats = {0:'B', 1:'b', 2:'H', 3:'h', 4:'I', 5:'i', 6:'Q', 7:'q', 8:'f', 9:'d', 10:'I', 11:'II'}
    for _ in range(count):
        flags, name = struct.unpack_from('>BI', data, p)
        p += 5
        start = strings + name
        name = data[start:data.index(b'\0', start)].decode('utf-8')
        storage, kind = flags & 240, flags & 15
        size = struct.calcsize('>' + formats[kind])
        if storage == 80:
            schema[name] = (rows + row_p, width, formats[kind])
            row_p += size
        elif storage == 48:
            schema[name] = (p, 0, formats[kind])
            p += size
        elif storage != 16:
            raise ValueError('Unsupported table storage')
    if row_p != width:
        raise ValueError('UTF row layout mismatch')
    return schema, row_count


def set_cell(data, schema, name, row, value):
    pos, width, fmt = schema[name]
    if fmt not in ('B', 'H', 'I', 'Q') or row and not width:
        raise ValueError('Unsafe metadata update')
    struct.pack_into('>' + fmt, data, pos + row * width, value)


def archive_plan(replacements):
    with CPK.open('rb') as stream:
        header = table(stream, 0)[0]
        members = table(stream, header['TocOffset'])
        if header['EnableTocCrc'] or header['EnableFileCrc'] or header['ItocOffset']:
            raise ValueError('Unsupported archive checksums or ITOC')
        etoc = header['EtocOffset']
        if etoc != header['ContentOffset'] + header['ContentSize'] or not header['EtocSize']:
            raise ValueError('Expected trailing ETOC after the content area')
        if etoc + header['EtocSize'] != CPK.stat().st_size:
            raise ValueError('Unexpected trailing metadata')
        base = min(header['ContentOffset'], header['TocOffset'])
        cursor, changes = etoc, []
        for path, data in replacements.items():
            matches = [(i, row) for i, row in enumerate(members)
                       if '/'.join((row['DirName'], row['FileName'])) == path]
            if len(matches) != 1:
                raise ValueError('Replacement must match one existing member: ' + path)
            i, row = matches[0]
            cursor = ((cursor + header['Align'] - 1) // header['Align']) * header['Align']
            changes.append({'path': path, 'row': i, 'offset': cursor,
                            'size': len(data), 'old_stored_size': row['FileSize'],
                            'old_expanded_size': row['ExtractSize'], 'sha256': sha(data)})
            cursor += len(data)
        end = ((cursor + header['Align'] - 1) // header['Align']) * header['Align']
        return header, members, changes, end


def repack(destination, replacements, plan):
    header, members, changes, end = plan
    with CPK.open('rb') as source, destination.open('xb') as target:
        # Preserve every original content byte; append replacements before the relocated ETOC.
        remaining = header['EtocOffset']
        while remaining:
            block = source.read(min(8*1024*1024, remaining))
            if not block:
                raise ValueError('Truncated original archive')
            target.write(block)
            remaining -= len(block)
        for item in changes:
            target.write(b'\0' * (item['offset'] - target.tell()))
            target.write(replacements[item['path']])
        target.write(b'\0' * (end - target.tell()))
        shutil.copyfileobj(source, target)
        for offset, patch_kind in [(0, 'header'), (header['TocOffset'], 'toc')]:
            source.seek(offset)
            packet = source.read(16)
            length = struct.unpack_from('<Q', packet, 8)[0]
            data = bytearray(source.read(length))
            schema, _ = fields(data)
            if patch_kind == 'toc':
                for item in changes:
                    set_cell(data, schema, 'FileSize', item['row'], item['size'])
                    set_cell(data, schema, 'ExtractSize', item['row'], item['size'])
                    set_cell(data, schema, 'FileOffset', item['row'], item['offset'] - min(header['ContentOffset'], header['TocOffset']))
            else:
                set_cell(data, schema, 'EtocOffset', 0, end)
                set_cell(data, schema, 'ContentSize', 0, end - header['ContentOffset'])
                for name, old in [('EnabledPackedSize', 'old_stored_size'), ('EnabledDataSize', 'old_expanded_size')]:
                    set_cell(data, schema, name, 0, header[name] + sum(v['size'] - v[old] for v in changes))
            target.seek(offset + 16)
            target.write(data)
    # Verify the archive as the extractor sees it; unaffected TOC rows stay exact.
    with destination.open('rb') as built, CPK.open('rb') as source:
        new_header = table(built, 0)[0]
        new_members = table(built, header['TocOffset'])
        changed_rows = {v['row'] for v in changes}
        if len(new_members) != len(members) or new_header['EtocOffset'] != end:
            raise ValueError('Archive metadata verification failed')
        for i, row in enumerate(new_members):
            if i not in changed_rows and row != members[i]:
                raise ValueError('Unrelated archive member changed')
        for item in changes:
            row = new_members[item['row']]
            pos = row['FileOffset'] + min(new_header['ContentOffset'], new_header['TocOffset'])
            built.seek(pos)
            if built.read(row['FileSize']) != replacements[item['path']] or row['ExtractSize'] != item['size']:
                raise ValueError('Replacement payload verification failed')
        source.seek(header['EtocOffset'])
        built.seek(end)
        if source.read() != built.read():
            raise ValueError('ETOC content changed')
        # Compare all preserved source bytes except explicitly updated UTF packets.
        spans = [(header['TocOffset'] + header['TocSize'], header['EtocOffset'])]
        for start, stop in spans:
            source.seek(start)
            built.seek(start)
            while start < stop:
                size = min(8*1024*1024, stop-start)
                if source.read(size) != built.read(size):
                    raise ValueError('Original archive payload changed')
                start += size
    return {'member_count': len(members), 'replaced_members': len(changes),
            'unchanged_toc_rows': len(members) - len(changes),
            'original_payload_bytes_preserved': True, 'etoc_preserved': True,
            'runtime_tested': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--version', help='Optional newer 0.x.y; default increments patch')
    parser.add_argument('--translations', action='store_true', help='Insert all identified structured English text and system titles')
    parser.add_argument('--summary', help='Short description for this build in the changelog')
    args = parser.parse_args()
    if args.summary and any(c in args.summary for c in '\r\n'):
        raise ValueError('Build summary must be a single line')
    current = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    version = next_version(current, args.version)
    credits = json.loads((ROOT / 'work/translation/en/credits.en.json').read_text(encoding='utf-8'))
    replacements, atlas_image, preview, boxes = footer_assets(version, credits)
    extra_game_files, translation_report = {}, None
    if args.translations:
        from build_translation_text import generate
        text_members, extra_game_files, translation_report = generate()
        if set(text_members) & set(replacements):
            raise ValueError('Translation and branding members overlap')
        replacements.update(text_members)
    credits_image = credits_page(version, credits)
    manual = ROOT / 'work/source/decrypted/sce_sys/manual'
    pages = sorted(manual.glob('*.png'))
    numbers = [int(p.stem) for p in pages]
    if numbers != list(range(1, len(pages) + 1)):
        raise ValueError('Manual page numbering must be checked before appending credits')
    credit_file = f'sce_sys/manual/{len(pages)+1:03}.png'
    plan = archive_plan(replacements)
    output = ROOT / 'work/output' / f'cross-ange-{version}'
    if output.exists():
        raise ValueError('Preserve existing build: ' + str(output))
    report = {'version': version, 'previous_version': current,
              'build_type': 'structured-english-test-candidate' if args.translations else 'title-branding-test-candidate', 'runtime_tested': False,
              'translation_drafts_inserted': args.translations, 'translation': translation_report,
              'footer_lines': [f'v{version}', credits['project_url']],
              'footer_bounds': boxes, 'credits_page': credit_file,
              'credits_sections': credits['sections'], 'copyright_preserved': True,
              'output': str(output), 'archive_replacements': plan[2], 'write': args.write}
    display = dict(report)
    display['archive_replacements'] = {'count': len(plan[2]), 'samples': plan[2][:3]}
    if translation_report:
        display['translation'] = dict(translation_report)
        display['translation']['scenario'] = dict(translation_report['scenario'])
        ids = display['translation']['scenario']['layout_review_ids']
        display['translation']['scenario']['layout_review_ids'] = {'count': len(ids), 'first_ids': ids[:5]}
        display['translation']['tables'] = [
            {key: value for key, value in item.items() if key != 'ui_layout'}
            for item in translation_report['tables']]
        if 'tutorials' in translation_report:
            tutorials = translation_report['tutorials']
            display['translation']['tutorials'] = {
                'textures_inserted': tutorials['textures_inserted'],
                'raster_regions_inserted': tutorials['raster_regions_inserted'],
                'assets': [{'member': item['member'], 'preview': item['decoded_preview']}
                          for item in tutorials['assets']], 'scope': tutorials['scope']}
        if 'chapter_titles' in translation_report:
            chapters = translation_report['chapter_titles']
            display['translation']['chapter_titles'] = {
                'unique_titles': chapters['unique_titles'],
                'textures_inserted': chapters['textures_inserted'],
                'raster_regions_inserted': chapters['raster_regions_inserted'],
                'assets': [{'member': item['member'], 'preview': item['decoded_preview']}
                          for item in chapters['assets']], 'scope': chapters['scope']}
        if 'ui_layout' in translation_report:
            display['translation']['ui_layout'] = {
                'display_adaptations': translation_report['ui_layout']['display_adaptations'],
                'label_width_checks': len(translation_report['ui_layout']['measurements']),
                'layout_record': translation_report['ui_layout']['layout_record'],
                'runtime_verified': translation_report['ui_layout']['runtime_verified']}
    print(json.dumps(display, indent=2))
    if not args.write:
        return
    output.mkdir(parents=True)
    for path, data in replacements.items():
        target = output / 'archive-members' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    game = output / 'game'
    (game / 'cpk').mkdir(parents=True)
    (game / credit_file).parent.mkdir(parents=True)
    credits_image.save(game / credit_file)
    for path, data in extra_game_files.items():
        target = game / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    report['checks'] = repack(game / 'cpk/Ange.cpk', replacements, plan)
    ui = ROOT / 'work/ui/local/branding' / version
    ui.mkdir(parents=True, exist_ok=False)
    credits_image.save(ui / 'credits.png')
    preview.convert('RGB').save(ui / 'title-footer.png')
    atlas_image.save(ui / 'title-atlas.png')
    report['previews'] = {'credits': str(ui / 'credits.png'), 'footer': str(ui / 'title-footer.png')}
    report['source_sha256'] = {path: sha((SOURCE / path).read_bytes()) for path in replacements}
    (output / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    # Finalize version only after archive and preservation checks pass.
    log = ROOT / 'CHANGELOG.md'
    content = log.read_text(encoding='utf-8')
    subject = args.summary or ('English text and artwork' if args.translations else 'Title footer and translation credits')
    scope = ('- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.\n'
             '- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, non-layout controls, nulls and relocation footers.\n'
             '- Replaced Latin glyphs in both game fonts with GenEi LateGo v2 Medium from the requested Genei Latin package; installed matching native proportional widths, including narrower spaces and control-boundary aliases. Retained unrelated glyphs. Included font copyright and OFL 1.1 license.\n'
             '- Validated all native font-record terminators; retained GenEi proportional widths and control-boundary aliases. Adjusted the colon to Latin dot spacing using GenEi period dots.\n'
             '- Reflowed dialogue by glyph advances to a 670-pixel line limit. Long records use native 80% text size and at most three lines; speaker names are fitted to 212 pixels. Canonical wording, IDs, voices and non-layout commands are retained. Rendered layout still requires an in-game test.\n'
             '- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.\n'
             '- Reworded the classroom peace explanation to fit at normal font size without losing its meaning.\n'
             '- Replaced Japanese labels and embedded sample captions on the room-menu, battle-controls and battle-HUD tutorial images (EBG_109, EBG_106, EBG_107). Preserved native palettes and all pixels outside the text regions.\n'
             '- Inserted all 15 unique chapter/prologue headings in both title atlas variants: 30 title regions. Matched save-menu naming, preserved English chapter labels/numbers, native animation and support artwork, and fitted complete English headings to the original sampling rectangles.\n'
             '- Fitted shared mission-condition and unit-stat labels to the columns measured in actual game captures; used compact display wording while retaining canonical drafts. Separated the numeric time limit from its appended English unit.\n'
             '- New changes need an in-game check. Other raster artwork, movie and original manual prose remain pending. The duplicate Naomi eye-animation tile is under investigation. No GitHub release.\n' if args.translations else
             '- Runtime title layout, manual-page access and archive loading still require an in-game test. English translation drafts are not inserted in this branding candidate. No GitHub release.\n')
    entry = (f'## {version} — {date.today().isoformat()} — {subject}\n\n'
             f'- Built a local test candidate with white, right-aligned `v{version}` above `github.com/retro-trans`.\n'
             '- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.\n'
             '- Automatically incremented the build version; regenerated the footer and credits from the same version.\n'
             f'- Repacked {len(replacements)} archive members, preserving original payloads and {report["checks"]["unchanged_toc_rows"]:,} unaffected TOC rows; verified replacement bytes and relocated ETOC.\n'
             + scope + '\n')
    if not content.startswith('# Changelog\n'):
        raise ValueError('Unexpected changelog format')
    log.write_text('# Changelog\n\n' + entry + content[len('# Changelog\n'):].lstrip(), encoding='utf-8')
    (ROOT / 'VERSION').write_text(version + '\n', encoding='utf-8')
    print(json.dumps({'built': str(output), 'version': version, 'checks': report['checks']}, indent=2))


if __name__ == '__main__':
    main()
