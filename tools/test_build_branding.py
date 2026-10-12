"""Checks for binary-wrapper boundaries, version progression and UI preservation."""
import json
import unittest
from build_branding import ROOT, SOURCE, ATLAS, ANIMATION, footer_assets, literal_wrapper, next_version, version_tuple
from dr12ae_extract import unwrap


class BrandingChecks(unittest.TestCase):
    def test_version_progression(self):
        self.assertEqual(next_version('0.1.3'), '0.1.4')
        self.assertEqual(next_version('0.1.99'), '0.1.100')
        self.assertEqual(next_version('0.1.3', '0.2.0'), '0.2.0')
        for target in ('0.1.3', '0.1.2', '1.0.0', '0.01.4', '../0.1.4'):
            with self.assertRaises(ValueError):
                next_version('0.1.3', target)

    def test_wrapper_boundaries(self):
        for size in (1, 31, 32, 255, 256, 1188, 8191, 8192, 16382, 16383):
            data = bytes(i % 256 for i in range(size))
            with self.subTest(size=size):
                self.assertEqual(unwrap(literal_wrapper(data)), (data, 1))

    @unittest.skipUnless((SOURCE / ATLAS).exists(), 'Local title assets required')
    def test_title_assets(self):
        credits = json.loads((ROOT / 'work/translation/en/credits.en.json').read_text(encoding='utf-8'))
        first, _, _, boxes = footer_assets('0.1.4', credits)
        second, _, _, _ = footer_assets('0.1.5', credits)
        self.assertNotEqual(first[ATLAS], second[ATLAS])
        self.assertEqual(first[ANIMATION], second[ANIMATION])
        source = (SOURCE / ATLAS).read_bytes()
        self.assertEqual(first[ATLAS][:1036], source[:1036])
        self.assertEqual(first[ATLAS][1036+233*1024:1036+256*1024], source[1036+233*1024:1036+256*1024])
        self.assertTrue(all(box['screen_bounds'][3] < 510 for box in boxes))
        self.assertEqual(unwrap(first[ANIMATION])[0][:32], unwrap((SOURCE / ANIMATION).read_bytes())[0][:32])


if __name__ == '__main__':
    unittest.main()
