"""Native chapter atlas regressions: full category, pixels, captions and fit."""
import io
import struct
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw
import build_chapter_titles as chapters
from shtx_extract import png


class ChapterTitleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.members,cls.report=chapters.generate()

    def test_complete_category_and_original_animation_sampling(self):
        self.assertEqual(set(self.members),set(chapters.ATLAS_MEMBERS))
        self.assertEqual(self.report['unique_titles'],15)
        self.assertEqual(self.report['textures_inserted'],2)
        self.assertEqual(self.report['raster_regions_inserted'],30)
        self.assertEqual(len(set(self.report['inserted_region_ids'])),30)
        self.assertEqual(len(self.report['category_inventory']),7)
        self.assertEqual(sum(x['modified'] for x in self.report['category_inventory']),2)
        for animation in self.report['animations'].values():
            self.assertEqual(animation['original_title_area'],[0,0,344,64])
            self.assertFalse(animation['animation_modified'])
        for asset in self.report['assets']:
            self.assertEqual([r['ui_id'] for r in asset['regions']],list(range(28,43)))

    def test_native_encoding_palette_and_decoded_preview(self):
        for member,native in self.members.items():
            source=(chapters.SOURCE/member).read_bytes()
            self.assertEqual(native[:1036],source[:1036])
            self.assertEqual(len(native),len(source))
            self.assertEqual(struct.unpack_from('<HH',native,6),(1024,512))
            palette=[tuple(native[12+4*i:16+4*i]) for i in range(256)]
            image=Image.open(io.BytesIO(png(native,1024,512))).convert('RGBA')
            self.assertEqual(list(image.getdata()),[palette[index] for index in native[1036:]])
            preview=Image.open(chapters.DEST/(Path(member).stem+'.png')).convert('RGBA')
            self.assertEqual(image.tobytes(),preview.tobytes())

    def test_outside_regions_and_original_english_captions_preserved(self):
        for asset in self.report['assets']:
            member=asset['member']
            raw=(chapters.SOURCE/member).read_bytes()
            before=Image.frombytes('L',(1024,512),raw[1036:])
            after=Image.frombytes('L',(1024,512),self.members[member][1036:])
            permitted=Image.new('L',before.size)
            draw=ImageDraw.Draw(permitted)
            for region in asset['regions']:
                x,y,right,bottom=region['heading_rect']
                draw.rectangle((x,y,right-1,bottom-1),fill=255)
            diff=ImageChops.difference(before,after)
            self.assertIsNone(ImageChops.multiply(diff,ImageChops.invert(permitted)).getbbox())
            self.assertIsNotNone(diff.getbbox())
            # All main Chapter/Prologue caption strokes and numeric labels stay exact.
            for row in range(5):
                rectangle=(0,row*64+37,1024,row*64+64)
                self.assertEqual(before.crop(rectangle).tobytes(),after.crop(rectangle).tobytes())
            # Caption blue glow reaches into heading/adjacent rows; retain it too.
            colors=[tuple(raw[12+4*i:16+4*i]) for i in range(256)]
            caption_indices={i for i,color in enumerate(colors) if color[:3] in ((1,54,252),(1,54,253))}
            for i,index in enumerate(raw[1036:]):
                if index in caption_indices:
                    self.assertEqual(index,self.members[member][1036+i])
            self.assertEqual(before.crop((0,326,1024,512)).tobytes(),after.crop((0,326,1024,512)).tobytes())

    def test_full_english_text_fits_existing_samples_with_transparency(self):
        for asset in self.report['assets']:
            image=Image.open(chapters.DEST/(Path(asset['member']).stem+'.png')).convert('RGBA')
            for region in asset['regions']:
                self.assertEqual(' '.join(region['lines']),region['en'])
                self.assertGreaterEqual(region['font_size'],14)
                self.assertEqual(region['status'],'inserted_texture')
                self.assertEqual(region['effective_sampling_width'],336 if region['ui_id'] in (30,33,36,39,42) else 344)
                for left,top,right,bottom in region['line_bounds']:
                    self.assertTrue(0<=left<right<=region['effective_sampling_width'])
                    self.assertTrue(0<=top<bottom<=36)
                x,y,right,bottom=region['heading_rect']
                crop=image.crop((x,y,right,y+34))
                self.assertEqual(crop.getpixel((0,0))[3],0)
                self.assertGreater(max(crop.getchannel('A').getdata()),240)
            pictured=next(r for r in asset['regions'] if r['ui_id']==29)
            self.assertEqual(pictured['en'],'Welcome to the First Squadron of Death')
            self.assertEqual(len(pictured['lines']),2)


if __name__=='__main__':
    unittest.main()
