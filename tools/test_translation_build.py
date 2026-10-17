"""Check reinsertion against original rows, relocation tables and glyphs."""
import csv
import io
import struct
import unicodedata
import re
import unittest
from unittest.mock import patch
from pathlib import Path

from build_translation_text import generate, ROOT, SOURCE, FONT_RANGES, relocate_bnd, ASCII_GLYPH_ALIASES
from dr12ae_extract import MAGIC, decode
from extract_sfo import read_sfo
from additional_text_extract import string_at
import build_english_font as english_font
from build_translation_text import load
from extract_script import JP
from bnf_codec import decode_record, encode_record


class TranslationBuildChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.members, cls.game, cls.report = generate()

    def test_full_coverage_and_screenshot_targets(self):
        self.assertEqual(self.report['structured_targets_inserted'], 17151)
        self.assertEqual(self.report['scenario']['files'], 462)
        self.assertEqual(len(self.members), 481)
        self.assertEqual(self.report['chapter_titles']['unique_titles'], 15)
        self.assertEqual(self.report['chapter_titles']['raster_regions_inserted'], 30)
        rows = list(csv.reader(io.StringIO(self.members['data/_scr/C000_PRO_000.txt'].decode('utf-16'), newline='')))
        teacher = next(r for r in rows if r[0] == '771')
        self.assertEqual([unicodedata.normalize('NFKC', s) for s in teacher], ['771', 'Female Teacher',
                                 'The Light of Mana was a new power brought to humanity#nseveral hundred years ago.', '11184'])
        bnd = self.members['data/_dat/strings.bnd']
        pointer = struct.unpack_from('<I', bnd, 20 + 11 * 8)[0]
        self.assertEqual(string_at(bnd, pointer)[0], 'Select Difficulty')
        normal_size = next(r for r in rows if r[0] == '774')[2]
        self.assertFalse(normal_size.startswith('#z'))
        self.assertEqual(len(normal_size.split('#n')), 2)

    def test_latin_colon_dot_positions(self):
        raw = english_font.glyph(ord(':'))
        pixels = [n for byte in raw for n in (byte & 15, byte >> 4)]
        occupied = [y for y in range(26) if max(pixels[y*26:(y+1)*26]) >= 8]
        # Upper dot fits Latin x-height; lower dot sits at the baseline.
        self.assertEqual(occupied, [8, 9, 10, 17, 18, 19])

    def test_shared_labels_do_not_cross_adjacent_columns(self):
        layout = self.report['ui_layout']
        self.assertEqual(layout['display_adaptations'], 13)
        self.assertEqual(len(layout['measurements']), 20)
        raw = self.members['data/_dat/strings.bnd']
        for measured in layout['measurements']:
            pointer = struct.unpack_from('<I', raw, 20 + measured['id'] * 8)[0]
            displayed = string_at(raw, pointer)[0]
            self.assertEqual(displayed, measured['display_en'])
            self.assertLessEqual(measured['width'], measured['available_width'])
        pointer = struct.unpack_from('<I', raw, 20 + 460 * 8)[0]
        self.assertEqual('5' + string_at(raw, pointer)[0], '5 Minutes')
        pointer = struct.unpack_from('<I', raw, 20 + 1481 * 8)[0]
        self.assertEqual('390.5' + string_at(raw, pointer)[0], '390.5 s')
        pointer = struct.unpack_from('<I', raw, 20 + 1480 * 8)[0]
        self.assertEqual(string_at(raw, pointer)[0], 'Left')

    def test_compact_label_changes_leave_other_ui_text_unchanged(self):
        raw = self.members['data/_dat/strings.bnd']
        from build_translation_text import display_text
        from collections import Counter
        substitutions = {'latin_display_aliases': Counter()}
        overrides = {(entry['id'], entry['column']): entry['display_en']
                     for entry in self.report['ui_layout']['entries']}
        overrides.update({(entry['id'], 0): entry['display_en']
                          for entry in self.report['briefing_layout']['entries']})
        for row in load('interface')['entries']:
            for column, field in enumerate(row['fields']):
                if field is None or not field['contains_japanese']:
                    continue
                pointer = struct.unpack_from('<I', raw, row['record_offset'] + column * 4)[0]
                expected = overrides.get((row['id'], column), field['en'])
                self.assertEqual(string_at(raw, pointer)[0], display_text(expected, substitutions))

    def test_all_operation_briefings_fit_emitted_native_widths(self):
        from briefing_layout import non_layout_controls, visible
        raw = self.members['data/_dat/strings.bnd']
        layout = self.report['briefing_layout']
        self.assertEqual(layout['descriptions_checked'], 65)
        self.assertGreater(layout['reflowed'], 20)
        rows = {r['id']: r for r in load('interface')['entries']}
        for entry in layout['entries']:
            source = rows[entry['id']]['fields'][0]['en']
            pointer = struct.unpack_from('<I', raw, rows[entry['id']]['record_offset'])[0]
            actual = string_at(raw, pointer)[0]
            self.assertEqual(visible(actual), visible(source), entry['key'])
            self.assertEqual(non_layout_controls(actual), non_layout_controls(source), entry['key'])
            self.assertLessEqual(len(actual.split('#n')), 8, entry['key'])
            for line in actual.split('#n'):
                self.assertLessEqual(english_font.measure(line), 580, entry['key'])
            if '#c600' in source:
                self.assertIn('#n#c600', actual, entry['key'])
        for identifier in (470, 511):
            entry = next(r for r in layout['entries'] if r['id'] == identifier)
            self.assertGreater(entry['original_maximum_width'], layout['width_limit'])
            self.assertTrue(entry['changed'])

    def test_briefing_reflow_rejects_vertical_overflow_and_preserves_warnings(self):
        from briefing_layout import fit, non_layout_controls, visible
        source = ('Small and medium DRAGONs have appeared near Arzenal. ' * 2 +
                  '#n #nThis is a solo mission.#n#c600(You cannot select a partner.)')
        actual = fit(source, 580, 8)
        self.assertEqual(visible(actual), visible(source))
        self.assertEqual(non_layout_controls(actual), ['#c600'])
        self.assertIn('#n #n', actual)
        self.assertIn('#n#c600', actual)
        with self.assertRaises(ValueError):
            fit('A large DRAGON has appeared. ' * 100, 580, 8)
        with self.assertRaises(ValueError):
            fit('W' * 1000, 580, 8)

    def test_mana_power_and_person_terms(self):
        canonical = {r['id']: r['en'] for r in load('corpus')['entries']}
        self.assertEqual(canonical['C030_PRO_000:3381'], 'The Light of Mana!?')
        self.assertIn("She's a Mana user, right?", canonical['C030_PRO_000:3406'])
        self.assertIn('A Mana user working for a Norma', canonical['C030_PRO_000:3422'])
        for identifier, text in canonical.items():
            visible = text.replace('#n', ' ')
            self.assertIsNone(re.search(r"\bMana(?:'s)? light\b|\b[aA] Mana\b(?! user)", visible), identifier)

    def test_relocation_preserves_unrelated_fields(self):
        original = (SOURCE / 'data/_dat/strings.bnd').read_bytes()
        payload = struct.unpack_from('<I', original, 4)[0]
        ptr = struct.unpack_from('<I', original, 108)[0]
        jp = string_at(original, ptr)[0]
        text = 'A much longer relocated label that does not fit its original allocation'
        result = relocate_bnd(original, [(108, ptr, jp, text)])
        new_payload = struct.unpack_from('<I', result, 4)[0]
        self.assertGreater(new_payload, payload)
        self.assertEqual(result[new_payload:], original[payload:])
        self.assertEqual(result[12:108], original[12:108])
        self.assertEqual(result[112:payload], original[112:payload])
        self.assertEqual(string_at(result, struct.unpack_from('<I', result, 108)[0])[0], text)
        with self.assertRaises(ValueError):
            relocate_bnd(original, [(109, ptr, jp, text)])

    def test_scenario_no_new_csv_delimiters(self):
        for filename, data in self.members.items():
            if not filename.endswith('.txt'):
                continue
            for line in data.decode('utf-16').splitlines():
                self.assertEqual(line.count(','), 3, filename)
                self.assertNotIn('"', line, filename)

    def test_requested_font_glyphs_and_unchanged_other_glyphs(self):
        characters = [c for a, b in FONT_RANGES for c in range(a, b + 1)]
        indexes = {c: i for i, c in enumerate(characters)}
        def glyph(raw, c):
            i = indexes[c]
            a, b = struct.unpack_from('<2I', raw, 40 + i * 4)
            body = raw[a:b]
            return decode(MAGIC + struct.pack('<II', 338, len(body) + 12) + body)
        for filename in self.report['font_members']:
            original, modified = (SOURCE / filename).read_bytes(), self.members[filename]
            for target, source in ASCII_GLYPH_ALIASES.items():
                self.assertEqual(glyph(modified, target), glyph(modified, source))
            self.assertNotEqual(glyph(modified, 65), glyph(original, 65))
            self.assertEqual(glyph(modified, 65), english_font.glyph(65))
            changed = english_font.CHARACTERS | set(ASCII_GLYPH_ALIASES)
            for i, c in enumerate(characters[:-1]):
                if c in changed:
                    continue
                a, b = struct.unpack_from('<2I', original, 40 + i*4)
                x, y = struct.unpack_from('<2I', modified, 40 + i*4)
                self.assertEqual(original[a:b], modified[x:y], hex(c))

    def test_alias_kerning_and_unrelated_records(self):
        original = (SOURCE / 'data/_dat/kerning.bnd').read_bytes()
        modified = self.members['data/_dat/kerning.bnd']
        def rows(raw):
            table, count = struct.unpack_from('<II', raw, 12)
            records = {}
            for i in range(count):
                pointer, flags, sizes = struct.unpack_from('<III', raw, table + i * 12)
                if pointer:
                    records[struct.unpack_from('<H', raw, pointer)[0]] = (flags, sizes)
            self.assertEqual(raw[table + (count - 1)*12:table + count*12], bytes(12))
            return records
        before, after = rows(original), rows(modified)
        for target, source in ASCII_GLYPH_ALIASES.items():
            self.assertEqual(after[target], after[source])
        for c, dimensions in before.items():
            if c not in english_font.widths():
                self.assertEqual(after[c], dimensions)
        self.assertEqual(after[ord('i')], (0, 7 | 7 << 16))
        self.assertEqual(after[ord('W')], (0, 22 | 22 << 16))
        self.assertEqual(after[ord(' ')], (0, 7 | 7 << 16))
        payload = struct.unpack_from('<I', modified, 4)[0]
        count = struct.unpack_from('<I', modified, payload)[0]
        relocations = set(struct.unpack_from('<' + str(count) + 'I', modified, payload + 4))
        table, rows_count = struct.unpack_from('<II', modified, 12)
        for i in range(rows_count - 1):
            self.assertIn(table + i*12, relocations)
        # Model the native loader's early stop at the first Unicode record.
        loaded_ascii = set()
        for i in range(rows_count - 1):
            pointer = struct.unpack_from('<I', modified, table+i*12)[0]
            c = struct.unpack_from('<H', modified, pointer)[0]
            if c > 255:
                break
            loaded_ascii.add(c)
        self.assertEqual(loaded_ascii, set(range(32, 127)))

    def test_scenario_control_scans_stop_before_terminator(self):
        # Reproduce the game's <=125 loop at 0x81019d76/0x81019d94.
        # Input includes NUL deliberately: reaching it is the regression.
        def scan(text, start):
            words = [ord(c) for c in text] + [0]*264
            i = start + 1
            while words[i] <= 125:
                if words[i] == 0:
                    return False
                i += 1
            return i < len(text)
        unsafe = 'The Light of Mana was a new power brought to humanity#nseveral hundred years ago.'
        self.assertFalse(scan(unsafe, unsafe.index('#')))
        checked = 0
        for filename, data in self.members.items():
            if not filename.endswith('.txt'):
                continue
            for row in csv.reader(io.StringIO(data.decode('utf-16'), newline='')):
                self.assertLess(len(row[1].encode('utf-16le')) // 2, 32)
                self.assertLess(len(row[2].encode('utf-16le')) // 2, 256)
                for text in row[1:3]:
                    for i, c in enumerate(text):
                        if c == '#':
                            self.assertTrue(scan(text, i), (filename, row[0]))
                            checked += 1
        self.assertGreater(checked, 4000)

    def test_all_scenario_wording_ids_and_voices_survive_reflow(self):
        canonical = {r['id']: r for r in load('corpus')['entries']}
        def visible(value):
            value = unicodedata.normalize('NFKC', value).replace('é', 'e').replace('ô', 'o').replace('#n', ' ')
            return re.sub(r'\s+', '', english_font.CONTROL.sub('', value))
        for filename, data in self.members.items():
            if not filename.endswith('.txt'):
                continue
            stem = Path(filename).stem
            for row in csv.reader(io.StringIO(data.decode('utf-16'), newline='')):
                source = canonical[stem + ':' + row[0]]
                expected = source['en'] if JP.search(source['jp']) else source['jp']
                self.assertEqual(row[0], source['source_record_id'])
                self.assertEqual(row[3], source['voice_id'])
                self.assertEqual(visible(row[2]), visible(expected), (stem, row[0]))
                controls = lambda text: english_font.CONTROL.findall(unicodedata.normalize('NFKC', text).replace('#n', ' '))
                actual = row[2][5:] if row[2].startswith('#z80') else row[2]
                self.assertEqual(controls(actual), controls(expected), (stem, row[0]))

    def test_native_width_table_fits_all_scenarios(self):
        raw = self.members['data/_dat/kerning.bnd']
        table, count = struct.unpack_from('<II', raw, 12)
        advances = {}
        for i in range(count-1):
            pointer, _, a, b = struct.unpack_from('<IIhh', raw, table + i*12)
            advances[chr(struct.unpack_from('<H', raw, pointer)[0])] = max(a, b)
        for filename, data in self.members.items():
            if not filename.endswith('.txt'):
                continue
            for row in csv.reader(io.StringIO(data.decode('utf-16'), newline='')):
                body = row[2]
                scale = .8 if body.startswith('#z80') else 1
                lines = body.split('#n') if body else []
                self.assertLessEqual(len(lines), 3 if scale == .8 else 2)
                for line in lines:
                    width = sum(advances.get(c, 26) for c in english_font.CONTROL.sub('', line))*scale
                    self.assertLessEqual(width, 670, (filename, row[0], width))
                if lines:
                    self.assertLessEqual(((len(lines)-1)*36 + 26)*scale, 79)
                name_scale = re.search(r'#z([0-9]+)', row[1])
                name_scale = int(name_scale[1])/100 if name_scale else 1
                width = sum(advances.get(c, 26) for c in english_font.CONTROL.sub('', row[1]))*name_scale
                self.assertLessEqual(width, 212, (filename, row[0], width))

    def test_native_font_reader_requires_end_markers(self):
        # A 0.1.7 glyph passed the length-bounded FCAA decoder, but the native
        # reader consumed all 338 literal bytes and then needed another token.
        from build_branding import literal_wrapper
        bitmap = english_font.glyph(ord('A'))
        old_record = literal_wrapper(bitmap)[12:]
        with self.assertRaisesRegex(ValueError, 'missing native terminator'):
            decode_record(old_record)
        self.assertEqual(decode_record(encode_record(bitmap)), bitmap)
        self.assertEqual(encode_record(bitmap)[-1], 0)
        for filename in self.report['font_members']:
            modified = self.members[filename]
            count = sum(b-a+1 for a, b in FONT_RANGES)
            offsets = list(struct.unpack_from('<' + str(count) + 'I', modified, 40)) + [len(modified)]
            for a, b in zip(offsets, offsets[1:]):
                self.assertEqual(len(decode_record(modified[a:b])), 338, (filename, a))

    def test_system_title_and_identity(self):
        original = read_sfo(ROOT / 'work/source/decrypted/sce_sys/param.sfo')['metadata']
        with patch.object(Path, 'read_bytes', return_value=self.game['sce_sys/param.sfo']):
            translated = read_sfo(Path('in-memory.sfo'))['metadata']
        self.assertEqual(translated['STITLE'], 'CROSS ANGE Rondo of Angel and Dragon tr.')
        for key in original:
            if key not in ('STITLE', 'TITLE'):
                self.assertEqual(translated[key], original[key], key)


if __name__ == '__main__':
    unittest.main()
