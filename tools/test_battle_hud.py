"""Guard the native atlas cells used by animated battle HUD counters."""
import hashlib
import io
import unittest

from PIL import Image

import build_battle_hud as hud
from shtx_extract import png


class BattleHudChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.members, cls.report = hud.generate()

    def test_headers_palette_and_every_unrelated_index_preserved(self):
        for asset in self.report['assets']:
            name = asset['member']
            before = (hud.SOURCE/name).read_bytes()
            after = self.members[name]
            self.assertEqual(before[:1036], after[:1036])
            self.assertEqual(len(before), len(after))
            width, height = asset['dimensions']
            allowed = set()
            for item in asset['labels']:
                x0,y0,x1,y1 = item['rect']
                allowed.update(y*width+x for y in range(y0,y1) for x in range(x0,x1))
            self.assertTrue(any(a != b for a,b in zip(before,after)))
            for index,(a,b) in enumerate(zip(before[1036:],after[1036:])):
                if index not in allowed:
                    self.assertEqual(a,b)
            decoded = Image.open(io.BytesIO(png(after,width,height))).convert('RGBA')
            palette = [tuple(after[12+i*4:16+i*4]) for i in range(256)]
            self.assertEqual(list(decoded.getdata()),[palette[i] for i in after[1036:]])

    def test_counter_slots_keep_same_font_size_and_color_families(self):
        asset = self.report['assets'][2]
        self.assertEqual(len(asset['labels']),40)
        for slot in range(4):
            labels = asset['labels'][slot::4]
            self.assertEqual([r['text'] for r in labels],list('0123456789'))
            self.assertEqual(len({r['fitted_font_size'] for r in labels}),1)
        native = self.members[asset['member']]
        decoded = Image.open(io.BytesIO(png(native,128,512))).convert('RGBA')
        for item in asset['labels']:
            opaque = [p for p in decoded.crop(item['rect']).getdata() if p[3]>220]
            self.assertTrue(opaque)
            for r,g,b,a in opaque:
                self.assertGreater(b,r) if item['color']=='cyan' else self.assertGreater(r,g)

    def test_preview_is_decoded_native_bytes_and_no_geometry_changes(self):
        self.assertEqual(set(self.members),{'data/_tex/'+n+'.btx' for n in hud.HASHES})
        for asset in self.report['assets']:
            native = self.members[asset['member']]
            expected = Image.open(io.BytesIO(png(native,*asset['dimensions']))).convert('RGBA')
            preview = Image.open(hud.ROOT/asset['preview']).convert('RGBA')
            self.assertEqual(expected.tobytes(),preview.tobytes())
            self.assertEqual(hashlib.sha256(native).hexdigest(),asset['output_sha256'])
        self.assertFalse(self.report['displaced_sprite_bug_fixed'])
        self.assertFalse(self.report['runtime_verified'])


if __name__ == '__main__':
    unittest.main()
