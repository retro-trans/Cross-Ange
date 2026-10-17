"""Generate and verify relocated English scenario/UI/battle/gallery members.

Called by build_branding.py --translations. No source or draft file is modified.
Source dialogue and generated binary/text assets remain in ignored work folders.
"""
import csv
import io
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

from build_branding import ROOT, SOURCE, sha
from extract_script import JP
from extract_sfo import read_sfo
from strip_jp import strip
from ui_table_extract import parse as parse_ui
from additional_text_extract import extract as extract_additional, string_at
import build_english_font as english_font

CONTROL = re.compile(r'#(?:[A-Za-z]|=)[0-9]*')
FONT_RANGES = [(32, 127), (8192, 9839), (12288, 12543), (19968, 40895), (65280, 65375)]
ASCII_GLYPH_ALIASES = {c + 0xfee0: c for c in range(33, 127)}


def control_boundaries(value, substitutions):
    # ADV typewriter at 0x81019d76 scans all codepoints <=125 after '#',
    # including NUL. A Latin glyph alias above that range ends the scan as
    # Japanese did. Keep the visible glyph and its advance identical to ASCII.
    result = list(value)
    for marker in CONTROL.finditer(value):
        position = marker.end()
        while position < len(value) and value[position] in ' \t':
            position += 1
        if position == len(value):
            raise ValueError('Control has no safe following glyph: ' + marker.group())
        if CONTROL.match(value, position):
            continue
        c = ord(value[position])
        if 33 <= c <= 125:
            result[position] = chr(c + 0xfee0)
            substitutions['control_boundary_glyphs'][value[position]] += 1
    return ''.join(result)


def load(name):
    folder = ROOT / 'work/translation/en'
    working = json.loads((folder / (name + '.working.json')).read_text(encoding='utf-8-sig'))
    english = json.loads((folder / (name + '.en.json')).read_text(encoding='utf-8-sig'))
    if strip(working) != english:
        raise ValueError('English export does not match reviewed working file: ' + name)
    return working


def display_text(value, substitutions, csv_field=False):
    # BNF has no Latin-1 range. Keep canonical drafts; use ASCII display aliases.
    for character, replacement in [('é', 'e'), ('ô', 'o')]:
        substitutions['latin_display_aliases'][character] += value.count(character)
        value = value.replace(character, replacement)
    if csv_field:
        # Shipped scenario files never use CSV quoting. Keep exactly three ASCII
        # delimiters per row; these Unicode slots receive the original ASCII glyphs.
        for character, replacement in [(',', '\uff0c'), ('"', '\uff02')]:
            substitutions['csv_punctuation_slots'][character] += value.count(character)
            value = value.replace(character, replacement)
    if csv_field:
        value = control_boundaries(value, substitutions)
    if JP.search(value):
        raise ValueError('Japanese remains in an English display field')
    unsupported = {ord(c) for c in value if c != '\t' and not any(a <= ord(c) <= b for a, b in FONT_RANGES)}
    if unsupported:
        raise ValueError('Unsupported font codepoints: ' + repr(sorted(unsupported)))
    return value


def checked_controls(source, target, identifier):
    if CONTROL.findall(source) != CONTROL.findall(target):
        raise ValueError('Control markers changed: ' + str(identifier))


def scenarios(substitutions):
    corpus = load('corpus')
    grouped = defaultdict(list)
    for row in corpus['entries']:
        grouped[row['source_file']].append(row)
    metrics = {r['file']: r for r in corpus['source_files']}
    replacements, targets, speakers, samples = {}, 0, 0, []
    max_line = 0
    layout = {'reflowed_records': 0, 'scaled_dialogue_records': 0,
              'scaled_speaker_records': 0, 'maximum_estimated_line_width': 0,
              'maximum_lines': 0, 'body_width_limit': english_font.BODY_WIDTH}
    long_lines = []
    for filename, translations in sorted(grouped.items()):
        raw = (SOURCE / filename).read_bytes()
        if sha(raw) != metrics[filename]['sha256']:
            raise ValueError('Scenario source hash changed: ' + filename)
        original = list(csv.reader(io.StringIO(raw.decode('utf-16'), newline='')))
        if len(original) != len(translations):
            raise ValueError('Scenario row count mismatch: ' + filename)
        output = []
        for source, row in zip(original, translations):
            if source != [row['source_record_id'], row['speaker_jp'], row['jp'], row['voice_id']]:
                raise ValueError('Scenario source row mismatch: ' + row['id'])
            if JP.search(source[2]) and not row['en']:
                raise ValueError('Missing English dialogue: ' + row['id'])
            text = row['en'] if JP.search(source[2]) else source[2]
            name = row['speaker'] if source[1] else ''
            for full, label in [('International Rescue Fleet Woman', 'Intl. Rescue Fleet Woman'),
                                ('Pamela & Olivier & Hikaru', 'Pamela, Olivier & Hikaru')]:
                if full in name:
                    substitutions['speaker_display_aliases'][full] += 1
                    name = name.replace(full, label)
            if source[1] and not name:
                raise ValueError('Missing English speaker: ' + row['id'])
            checked_controls(source[2], text, row['id'])
            checked_controls(source[1], name, row['id'] + ':speaker')
            text = display_text(text, substitutions, True)
            name = display_text(name, substitutions, True)
            before = text
            try:
                text, lines, percentage = english_font.layout_dialogue(text)
            except ValueError as error:
                raise ValueError(str(error) + ': ' + row['id']) from error
            layout['reflowed_records'] += text != before
            layout['scaled_dialogue_records'] += percentage != 100
            layout['maximum_lines'] = max(layout['maximum_lines'], lines)
            layout['maximum_estimated_line_width'] = max(layout['maximum_estimated_line_width'],
                max((english_font.measure(line, percentage) for line in text.split('#n')), default=0))
            before = name
            name, name_percentage = english_font.layout_name(name)
            layout['scaled_speaker_records'] += name != before
            # Reflowed line breaks and added native size commands need the same
            # safe codepoint boundaries as the original formatting commands.
            text = control_boundaries(text, substitutions)
            name = control_boundaries(name, substitutions)
            if len(text.encode('utf-16le')) // 2 >= 256 or len(name.encode('utf-16le')) // 2 >= 32:
                raise ValueError('Runtime dialogue/name buffer capacity exceeded: ' + row['id'])
            result = [source[0], name, text, source[3]]
            if any(',' in item or '"' in item or '\n' in item or '\r' in item for item in result):
                raise ValueError('Scenario delimiter unsafe: ' + row['id'])
            output.append(result)
            targets += bool(JP.search(source[2]))
            speakers += bool(source[1])
            width = max(len(CONTROL.sub('', line)) for line in text.split('#n')) if text else 0
            max_line = max(max_line, width)
            # A diagnostic only: font/engine wrapping must be measured in-game.
            if max(map(len, text.split('#n'))) > 65:
                long_lines.append(row['id'])
            if row['id'] == 'C000_PRO_000:771' or len(samples) < 2:
                samples.append({'id': row['id'], 'speaker': name, 'en': text})
        encoded = b'\xff\xfe' + (''.join(','.join(row) + '\r\n' for row in output)).encode('utf-16le')
        restored = list(csv.reader(io.StringIO(encoded.decode('utf-16'), newline='')))
        if restored != output or any(len(row) != 4 for row in restored):
            raise ValueError('Scenario serialization failed: ' + filename)
        replacements[filename] = encoded
    if len(replacements) != 462 or targets != 13214:
        raise ValueError('Incomplete scenario coverage')
    return replacements, {'files': len(replacements), 'rows': len(corpus['entries']),
                           'japanese_targets_inserted': targets, 'english_speaker_fields': speakers,
                           'source_ids_and_voices_preserved': True,
                           'source_non_layout_controls_preserved': True,
                           'line_breaks_reflowed_for_english': True,
                           'pixel_layout': layout,
                           'samples': samples, 'layout_review_ids': long_lines,
                           'longest_line_character_diagnostic': max_line}


def relocate_bnd(raw, changes, reflow_cells=()):
    payload = struct.unpack_from('<I', raw, 4)[0]
    count = struct.unpack_from('<I', raw, payload)[0]
    if payload % 4 or payload + 4 + count * 4 != len(raw):
        raise ValueError('Unsupported BND relocation footer')
    footer = raw[payload:]
    relocations = set(struct.unpack_from('<' + str(count) + 'I', raw, payload + 4))
    modified, cached, expected, changed_bytes = bytearray(raw[:payload]), {}, {}, set(range(4, 8))
    for pointer_cell, source_offset, source_text, english in changes:
        if pointer_cell not in relocations or pointer_cell in expected:
            raise ValueError('Missing or duplicated BND pointer relocation')
        if struct.unpack_from('<I', raw, pointer_cell)[0] != source_offset or string_at(raw, source_offset)[0] != source_text:
            raise ValueError('BND source pointer/text mismatch')
        if pointer_cell in reflow_cells:
            checked_controls(source_text.replace('#n', ''), english.replace('#n', ''), pointer_cell)
        else:
            checked_controls(source_text, english, pointer_cell)
        if english not in cached:
            cached[english] = len(modified)
            modified.extend(english.encode('utf-16le') + b'\0\0')
        struct.pack_into('<I', modified, pointer_cell, cached[english])
        expected[pointer_cell] = english
        changed_bytes.update(range(pointer_cell, pointer_cell + 4))
    modified.extend(b'\0' * (-len(modified) % 4))
    struct.pack_into('<I', modified, 4, len(modified))
    result = bytes(modified) + footer
    if any(a != b and i not in changed_bytes for i, (a, b) in enumerate(zip(raw[:payload], result[:payload]))):
        raise ValueError('Unrelated BND field changed')
    for cell, text in expected.items():
        if string_at(result, struct.unpack_from('<I', result, cell)[0])[0] != text:
            raise ValueError('Relocated BND string failed verification')
    if result[len(modified):] != footer:
        raise ValueError('BND relocation footer changed')
    return result


def tables(substitutions):
    replacements, report = {}, []
    interface = load('interface')
    from ui_label_layout import compact_labels
    compact, ui_layout = compact_labels(interface)
    from briefing_layout import descriptions
    briefings, briefing_report = descriptions(interface)
    originals = parse_ui(SOURCE / 'data/_dat')
    if len(originals) != len(interface['entries']):
        raise ValueError('UI row count mismatch')
    changes, sample, reflow_cells = [], None, set()
    for source, row in zip(originals, interface['entries']):
        if source['id'] != row['id'] or source.get('key') != row.get('key') or source['record_offset'] != row['record_offset']:
            raise ValueError('UI identity mismatch')
        for field, target in zip(source['fields'], row['fields']):
            if field is None:
                if target is not None:
                    raise ValueError('UI null field changed')
                continue
            if field['source_offset'] != target['source_offset'] or field['text'] != target['jp']:
                raise ValueError('UI source field changed')
            if not field['contains_japanese']:
                continue
            english = target.get('en')
            if not english:
                raise ValueError('Missing English UI field')
            english = compact.get((row['id'], field['column']), english)
            if (row['id'], field['column']) in briefings:
                english = briefings[row['id'], field['column']]
                reflow_cells.add(row['record_offset'] + field['column'] * 4)
            english = display_text(english, substitutions)
            cell = row['record_offset'] + field['column'] * 4
            changes.append((cell, field['source_offset'], field['text'], english))
            if row['key'] == 'STR_DIFFICULT_SELECT':
                sample = {'id': row['id'], 'key': row['key'], 'en': english}
    filename = 'data/_dat/strings.bnd'
    replacements[filename] = relocate_bnd((SOURCE / filename).read_bytes(), changes, reflow_cells)
    report.append({'file': filename, 'japanese_targets_inserted': len(changes), 'sample': sample,
                   'ui_layout': ui_layout, 'briefing_layout': briefing_report})
    if len(changes) != 1716:
        raise ValueError('Incomplete UI coverage')
    additional = load('additional')
    originals = {r['id']: r for r in extract_additional()['entries']}
    grouped = defaultdict(list)
    for row in additional['entries']:
        source = originals[row['id']]
        for key in ['source_file', 'record_offset', 'source_column', 'source_offset', 'jp', 'record_words', 'source_sha256']:
            if row[key] != source[key]:
                raise ValueError('Additional source field changed')
        if not row['en']:
            raise ValueError('Missing battle/gallery translation')
        grouped[row['source_file']].append((row['record_offset'] + row['source_column'] * 4,
                                           row['source_offset'], row['jp'], display_text(row['en'], substitutions)))
    for filename, changes in sorted(grouped.items()):
        replacements[filename] = relocate_bnd((SOURCE / filename).read_bytes(), changes)
        report.append({'file': filename, 'japanese_targets_inserted': len(changes)})
    if sum(r['japanese_targets_inserted'] for r in report) != 3935:
        raise ValueError('Incomplete structured table coverage')
    return replacements, report


def metadata():
    data = load('metadata')
    source = ROOT / 'work/source/decrypted/sce_sys/param.sfo'
    raw = source.read_bytes()
    _, key_start, value_start, count = struct.unpack_from('<4I', raw, 4)
    modified = bytearray(raw)
    targets = {r['source_field']: r for r in data['entries']}
    seen = set()
    for i in range(count):
        entry = 20 + i * 16
        key, fmt, size, capacity, value = struct.unpack_from('<HHIII', raw, entry)
        name_start = key_start + key
        name = raw[name_start:raw.index(b'\0', name_start)].decode('ascii')
        if name not in targets:
            continue
        row = targets[name]
        if fmt != 0x204 or raw[value_start + value:value_start + value + size].rstrip(b'\0').decode('utf-8') != row['jp']:
            raise ValueError('System title source mismatch')
        new = row['en'].encode('utf-8') + b'\0'
        modified.extend(b'\0' * (-len(modified) % 4))
        struct.pack_into('<III', modified, entry + 4, len(new), len(new), len(modified) - value_start)
        modified.extend(new)
        seen.add(name)
    if seen != set(targets):
        raise ValueError('System title coverage mismatch')
    return bytes(modified), [{'id': r['id'], 'en': r['en']} for r in data['entries']]


def generate():
    substitutions = {k: Counter() for k in ['latin_display_aliases', 'csv_punctuation_slots',
                                           'control_boundary_glyphs', 'speaker_display_aliases']}
    dialogue, scenario_report = scenarios(substitutions)
    bnd, table_report = tables(substitutions)
    fonts = english_font.generate_fonts()
    from build_tutorial_textures import generate as generate_tutorials
    tutorials, tutorial_report = generate_tutorials()
    from build_chapter_titles import generate as generate_chapters
    chapters, chapter_report = generate_chapters()
    sfo, metadata_report = metadata()
    replacements = {**dialogue, **bnd, **fonts, **tutorials, **chapters,
                    'data/_dat/kerning.bnd': english_font.kerning()}
    report = {'structured_targets_inserted': scenario_report['japanese_targets_inserted'] + sum(r['japanese_targets_inserted'] for r in table_report) + len(metadata_report),
              'scenario': scenario_report, 'tables': table_report, 'metadata': metadata_report,
              'font_members': sorted(fonts), 'display_adaptations': {k: dict(v) for k, v in substitutions.items()},
              'control_scan_boundary_protection': True,
              'font': english_font.report(),
              'drafts_modified': False, 'tutorials': tutorial_report, 'chapter_titles': chapter_report,
              'ui_layout': table_report[0]['ui_layout'],
              'briefing_layout': table_report[0]['briefing_layout'],
              'raster_and_manual_translation_inserted': False,
              'selected_tutorial_artwork_inserted': True,
              'layout_runtime_tested': False}
    if report['structured_targets_inserted'] != 17151:
        raise ValueError('Structured coverage count mismatch')
    return replacements, {'sce_sys/param.sfo': sfo,
                          'sce_sys/font-license.txt': (ROOT / 'docs/licenses/genei-latin-OFL.txt').read_bytes()}, report
