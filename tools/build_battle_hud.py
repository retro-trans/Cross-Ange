"""Render legible battle labels/digits within the original atlas sampling cells.

This does not alter HUD models, counters, animation or executable code. The
reported displaced sprites still require an original/English runtime comparison.
"""
import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw

from build_english_font import face
from build_tutorial_textures import _premult
from shtx_extract import png

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'work/source/archive/assets'
PREVIEWS = ROOT / 'work/ui/local/battle-hud'
HASHES = {
    'UI01_BT_FRA01_00': 'b41fe692c6cf694555cbc67e7c9cb64ee1a55662f329b4df7e74d7fa0bb7f346',
    'UI01_BT_FRA02_00': '95f2894b234f832663502242b4228bc5569b30059d844ddd1eec90d1ce230a92',
    'UI01_BT_NUM01_00': '024e55e491e9b36d269a2a320bfa65746762d745095de1fcb3d43e4f503e4e29',
}


def regions(name):
    if name == 'UI01_BT_FRA01_00':
        result = []
        for dy in (0, 128):
            for text, box, size in [
                ('TIME', (178, 4, 223, 28), 22),
                ('SPEED', (178, 34, 240, 55), 20),
                ('km/h', (178, 58, 223, 74), 16),
                ('FREEZING', (178, 81, 255, 95), 14),
                ('BULLETS', (178, 103, 247, 117), 14),
            ]:
                result.append(dict(text=text, rect=[box[0], box[1]+dy, box[2], box[3]+dy],
                                   font_size=size, color='light'))
        return result
    if name == 'UI01_BT_FRA02_00':
        return [dict(text='KILLS', rect=[143, 356, 229, 370], font_size=16, color='dark')]
    result = []
    for digit in range(10):
        for dx in (0, 64):
            for box, size in [((6, 2, 27, 38), 30), ((40, 12, 57, 38), 22)]:
                result.append(dict(text=str(digit),
                                   rect=[box[0]+dx, box[1]+40*digit,
                                         box[2]+dx, box[3]+40*digit],
                                   font_size=size, color='red' if dx else 'cyan'))
    return result


def mask_for(item):
    x0, y0, x1, y1 = item['rect']
    width, height = x1-x0, y1-y0
    # Pixel margins keep bilinear filtering inside the existing cell. No
    # horizontal compression: digits retain the requested font's proportions.
    for size in range(item['font_size'], 8, -1):
        font = face(size*4)
        box = font.getbbox(item['text'], stroke_width=3)
        if box[2]-box[0] <= (width-2)*4 and box[3]-box[1] <= (height-2)*4:
            break
    else:
        raise ValueError('HUD label cannot fit its native sample cell')
    mask = Image.new('L', (width*4, height*4))
    draw = ImageDraw.Draw(mask)
    draw.text(((width*4-(box[2]-box[0]))//2-box[0],
               (height*4-(box[3]-box[1]))//2-box[1]),
              item['text'], font=font, fill=255, stroke_width=3, stroke_fill=255)
    return mask.resize((width, height), Image.Resampling.LANCZOS), size


def generate():
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    replacements, reports = {}, []
    for name, expected in HASHES.items():
        member = 'data/_tex/'+name+'.btx'
        raw = (SOURCE/member).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected or raw[:6] != b'SHTXFS':
            raise ValueError('Battle HUD source identity mismatch: '+member)
        width, height = struct.unpack_from('<HH', raw, 6)
        if len(raw) != 1036+width*height:
            raise ValueError('Unexpected HUD native texture length')
        palette = [tuple(raw[12+4*i:16+4*i]) for i in range(256)]
        premult = [_premult(c) for c in palette]
        original = Image.open(io.BytesIO(png(raw,width,height))).convert('RGBA')
        edited = original.copy()
        indices = bytearray(raw[1036:])
        permitted = set()
        placements = []
        for item in regions(name):
            x0,y0,x1,y1 = item['rect']
            if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
                raise ValueError('HUD cell exceeds texture')
            mask, size = mask_for(item)
            if item['color'] == 'dark':
                background, ink = (170,245,255,255), (0,20,40,255)
            else:
                background = (0,0,0,0)
                ink = {'red':(255,180,205,255), 'cyan':(160,250,255,255),
                       'light':(240,255,255,255)}[item['color']]
            tile = Image.new('RGBA', mask.size, background)
            tile.alpha_composite(Image.composite(Image.new('RGBA',mask.size,ink),
                                                Image.new('RGBA',mask.size),mask))
            cache = {}
            for y in range(y0,y1):
                for x in range(x0,x1):
                    pixel = tile.getpixel((x-x0,y-y0))
                    if pixel not in cache:
                        value = _premult(pixel)
                        cache[pixel] = min(range(256), key=lambda i:sum((a-b)**2 for a,b in zip(value,premult[i])))
                    index = cache[pixel]
                    offset = y*width+x
                    if offset in permitted:
                        raise ValueError('HUD cells overlap')
                    permitted.add(offset)
                    indices[offset] = index
            placements.append({**item, 'fitted_font_size':size, 'mask_bounds':mask.getbbox()})
        native = raw[:1036]+bytes(indices)
        if any(a != b and i not in permitted for i,(a,b) in enumerate(zip(raw[1036:],indices))):
            raise ValueError('HUD pixel changed outside label cells')
        output = Image.open(io.BytesIO(png(native,width,height))).convert('RGBA')
        preview = PREVIEWS/(name+'.png')
        output.save(preview)
        # Neutral dark plate for inspection, not a screenshot or runtime proof.
        comparison = Image.new('RGB',(width*4+40,height*2+40),(12,30,48))
        for i,im in enumerate((original,output)):
            bg = Image.new('RGBA',im.size,(12,30,48,255));bg.alpha_composite(im)
            comparison.paste(bg.resize((width*2,height*2)),(i*(width*2+20),20))
        comparison.save(PREVIEWS/(name+'-comparison.png'))
        replacements[member] = native
        reports.append(dict(member=member, source_sha256=expected,
                            output_sha256=hashlib.sha256(native).hexdigest(),
                            dimensions=[width,height], labels=placements,
                            header_palette_preserved=True, outside_indices_preserved=True,
                            preview=str(preview.relative_to(ROOT))))
    report = dict(font='GenEi LateGo v2 Medium', assets=reports,
                  scope='Readability only; atlas cell bounds and all HUD models/animations preserved.',
                  displaced_sprite_bug_fixed=False, runtime_verified=False)
    (ROOT/'work/ui/battle-hud-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return replacements, report


if __name__ == '__main__':
    _, report = generate()
    print(json.dumps(report,indent=2))
