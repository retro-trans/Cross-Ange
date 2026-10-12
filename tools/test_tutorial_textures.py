"""Regression checks for all ten identified tutorial raster repairs."""
import io
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw
import build_tutorial_textures as tutorials
from shtx_extract import png


class TutorialTextureChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.members, cls.report = tutorials.generate()

    def test_native_palette_and_decoded_output(self):
        self.assertEqual(set(self.members), set(tutorials.SOURCE_SHA256))
        for member, native in self.members.items():
            source = (tutorials.SOURCE/member).read_bytes()
            self.assertEqual(native[:1036], source[:1036])
            self.assertEqual(len(native),len(source))
            self.assertEqual(struct.unpack_from('<HH',native,6),(1024,1024))
            decoded = Image.open(io.BytesIO(png(native,1024,1024))).convert('RGBA')
            palette = [tuple(native[12+i*4:16+i*4]) for i in range(256)]
            self.assertEqual(list(decoded.getdata()),[palette[index] for index in native[1036:]])
            preview = Image.open(tutorials.PREVIEWS/(Path(member).stem+'.png')).convert('RGBA')
            self.assertEqual(preview.tobytes(),decoded.crop((0,0,960,544)).tobytes())

    def test_preserves_diagrams_screenshots_and_every_outside_index(self):
        for asset in self.report['assets']:
            member = asset['member']
            before = (tutorials.SOURCE/member).read_bytes()[1036:]
            after = self.members[member][1036:]
            permitted = Image.new('L',(1024,1024))
            draw = ImageDraw.Draw(permitted)
            for label in asset['labels']:
                for key in ('erase','draw'):
                    x0,y0,x1,y1 = label[key]
                    draw.rectangle((x0,y0,x1-1,y1-1),fill=255)
            diff = ImageChops.difference(Image.frombytes('L',(1024,1024),before),
                                        Image.frombytes('L',(1024,1024),after))
            self.assertIsNone(ImageChops.multiply(diff,ImageChops.invert(permitted)).getbbox())
            self.assertIsNotNone(diff.getbbox())
        # The large controller, battle view and character artwork are retained.
        for member, rectangle in [('data/_cg/EBG_106.btx',(320,159,630,378)),
                                  ('data/_cg/EBG_107.btx',(242,112,718,328)),
                                  ('data/_cg/EBG_109.btx',(510,110,718,329))]:
            source = (tutorials.SOURCE/member).read_bytes()[1036:]
            output = self.members[member][1036:]
            self.assertEqual(Image.frombytes('L',(1024,1024),source).crop(rectangle).tobytes(),
                             Image.frombytes('L',(1024,1024),output).crop(rectangle).tobytes())

    def test_scope_glossary_and_fit(self):
        self.assertEqual(self.report['textures_inserted'],10)
        self.assertEqual(self.report['raster_regions_inserted'],84)
        self.assertEqual(len(set(self.report['inserted_region_ids'])),84)
        labels = {label['id']:label for asset in self.report['assets'] for label in asset['labels']}
        self.assertEqual(labels['EBG_106-freeze']['text'],'Freeze Bullet (Destroyer Mode only)')
        self.assertEqual(labels['EBG_106-quick']['text'],'Quick Turn (Destroyer Mode only)')
        self.assertEqual(labels['EBG_110-title']['text'],'Why I Fight')
        self.assertIn('Buy weapons', labels['EBG_108-shop']['text'])
        for label in labels.values():
            x,y,right,bottom = label['draw']
            bx,by,br,bb = label['text_bounds']
            self.assertTrue(x<=bx<br<=right and y<=by<bb<=bottom,label['id'])
            self.assertEqual(label['status'],'inserted_texture')

    def test_changed_source_rejected_before_rendering(self):
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder)
            member = 'data/_cg/EBG_106.btx'
            path = fake/member
            path.parent.mkdir(parents=True)
            data = bytearray((tutorials.SOURCE/member).read_bytes())
            data[-1] ^= 1
            path.write_bytes(data)
            with patch.object(tutorials,'SOURCE',fake):
                with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                    tutorials.generate()


if __name__=='__main__':
    unittest.main()
