"""Regression checks for native bubble anchors and complete timed comments."""
import re
import struct
import unittest

import build_english_font as font
from build_translation_text import load
from dr12ae_extract import unwrap
import timed_dialogue_layout as timed


class TimedBubbleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overrides,cls.text = timed.comments(load('interface'))
        cls.assets,cls.animation = timed.animation()
        cls.before = unwrap((timed.SOURCE/timed.MEMBER).read_bytes())[0]
        cls.after = unwrap(cls.assets[timed.MEMBER])[0]

    def test_only_reviewed_horizontal_native_keys_change(self):
        self.assertEqual(len(self.animation['changed_keys']),12)
        allowed = set()
        for row in self.animation['changed_keys']:
            self.assertIn(row['property'],['POSX','SCAX'])
            self.assertEqual(struct.unpack_from('<i',self.before,row['offset'])[0],row['before'])
            self.assertEqual(struct.unpack_from('<i',self.after,row['offset'])[0],row['after'])
            allowed.update(range(row['offset'],row['offset']+4))
        self.assertEqual(len(self.before),len(self.after))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(self.before,self.after))))
        # AREA, ORGY, vertical keys, font part, frame times, hierarchies, user
        # callback IDs and opacity all lie outside these allowed words.
        self.assertEqual(set(self.assets),{timed.MEMBER})

    def test_body_and_tail_anchors_and_both_screen_columns(self):
        parts = timed.sections(self.after)
        for name in ['fukidashi_waku a','fukidashi_waku b','fukidashi_waku c']:
            positions = [v for _,v in timed.curve(self.after,parts[name],b'POSX')]
            scales = [v for _,v in timed.curve(self.after,parts[name],b'SCAX')]
            self.assertEqual(len(set(positions)),1)
            self.assertEqual(len(set(scales)),1)
            center = positions[0]/1000
            extent = 126*scales[0]/1000
            self.assertAlmostEqual(center-extent,0)
            self.assertAlmostEqual(center+extent,timed.BODY_WIDTH)
        # Validate all scene anchors and referenced comment/reaction IDs from
        # the native TimingSelect records, including the two debug scenes.
        source = (timed.SOURCE/'data/_dat/TimingSelect.bnd').read_bytes()
        self.assertEqual(struct.unpack_from('<II',source,12),(20,8))
        referenced = set()
        for scene in range(8):
            for index in range(27):
                row = struct.unpack_from('<7i',source,20+scene*1012+256+index*28)
                if row[0]:
                    referenced.add(row[0])
                    self.assertIn((row[0],0),self.overrides)
                    self.assertLessEqual(row[5]+timed.BODY_WIDTH,960)
        self.assertEqual(len(referenced),209)
        for x in (50,60,100,600,620):
            self.assertLessEqual(x+timed.BODY_WIDTH,960)
        for _,value in timed.curve(self.after,parts['fukidashi_r_side'],b'POSX'):
            self.assertAlmostEqual(value/1000-11,timed.BODY_WIDTH)

    def test_all_comments_fit_without_wording_or_thought_control_changes(self):
        self.assertEqual(self.text['comments_checked'],211)
        self.assertEqual(self.text['primary_comments'],145)
        self.assertEqual(self.text['reactions'],66)
        for row in self.text['entries']:
            before,after = row['canonical_en'],row['display_en']
            clean = lambda t:re.sub(r'\s+','',font.CONTROL.sub('',t))
            self.assertEqual(clean(before),clean(after))
            self.assertEqual(font.CONTROL.findall(before.replace('#n',' ')),
                             font.CONTROL.findall(after.replace('#n',' ')))
            self.assertLessEqual(row['lines'],4)
            self.assertLessEqual(row['maximum_native_width'],340)
            self.assertLessEqual(20+row['maximum_screen_width']+20,timed.BODY_WIDTH)

    def test_reported_lines_and_thoughts(self):
        rows = {r['id']:r for r in self.text['entries']}
        self.assertEqual(rows[1402]['lines'],4)
        self.assertIn('bookworms',rows[1402]['display_en'])
        self.assertEqual(rows[1405]['lines'],2)
        self.assertGreater(20+rows[1405]['maximum_screen_width'],252)
        self.assertLess(20+rows[1405]['maximum_screen_width'],timed.BODY_WIDTH-20)
        self.assertTrue(self.overrides[1406,0].startswith('#b0'))
        with self.assertRaises(ValueError):
            timed.fit('overlong '*100)

    def test_word_and_inventory_failures_are_not_silently_truncated(self):
        with self.assertRaises(ValueError):
            timed.fit('W'*100)
        with self.assertRaises(ValueError):
            timed.comments({'entries':[]})


if __name__=='__main__':
    unittest.main()
