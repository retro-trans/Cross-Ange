"""Replace all 15 chapter/prologue headings in both native title atlases.

The original SSAD title AREA is 344x64. Title selection uses a three-column,
five-row atlas; the final column has 336 available pixels. Captions, chapter
numbers, bars and animations are preserved byte-for-byte.
"""
import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from build_english_font import face
from dr12ae_extract import unwrap
from shtx_extract import png

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'work/source/archive/assets'
DEST = ROOT/'work/ui/local/chapter-titles'
GUARDS = {
    'data/_ssa/sub_title_b.btx':'c12accd4626bcf75574d7761d4cf0825848869334bd5df6c2a966782759a14ab',
    'data/_ssa/sub_title_b_.btx':'98f532ef5665af2b45a7be97e626d21007eaa8af3bfb1519f2374b8aeace91ee',
    'data/_ssa/sub_title_a.btx':'e2d6a27cd62660866507ccb61564b22441570d2d1099ef60c068f7876630061b',
    'data/_ssa/sub_title.bsa':'782ec452d9aaa6c5b95b65ab86ad359917313b8ff878cd0a9e32f45866ba86b9',
    'data/_ssa/sub_title_.bsa':'58ce62c281b2e4fa24682008da7e93a011eba5ca53d46e3b15faa08313b30c91',
    'data/_dat/sub_title.bsw':'51d5fab0c91bf1fd0092d4b7326d39ef15613e733b7405695cd15646c7a64b86',
    'data/_dat/sub_title_.bsw':'51d5fab0c91bf1fd0092d4b7326d39ef15613e733b7405695cd15646c7a64b86',
}
ATLAS_MEMBERS = ('data/_ssa/sub_title_b.btx','data/_ssa/sub_title_b_.btx')
SCALE = 4


def _caption_glow(color):
    # This palette family is exclusive to existing Chapter/Prologue captions.
    # Their glow reaches one pixel above/below the 36..64 caption band.
    return color[:3] in ((1,54,252),(1,54,253))


def _layout(text,width):
    candidates = [([text],size,2) for size in range(26,17,-1)]
    words = text.split()
    splits = [(words[:i],words[i:]) for i in range(1,len(words))]
    for size in range(16,13,-1):
        font = face(size*SCALE)
        balanced = sorted(splits,key=lambda pair:max(font.getlength(' '.join(line)) for line in pair))
        candidates.extend(([ ' '.join(line) for line in pair],size,1) for pair in balanced)
    for lines,size,stroke in candidates:
        font = face(size*SCALE)
        boxes = [font.getbbox(line,stroke_width=stroke*SCALE) for line in lines]
        heights = [box[3]-box[1] for box in boxes]
        # Tight line spacing keeps two complete English lines inside the heading.
        height = sum(heights)
        if max(box[2]-box[0] for box in boxes)<=(width-8)*SCALE and height<=34*SCALE:
            return lines,size,stroke,boxes,heights
    raise ValueError('Complete English chapter heading cannot fit: '+text)


def _paint(text,width,outline,align='center'):
    lines,size,stroke,boxes,heights = _layout(text,width)
    image = Image.new('RGBA',(width*SCALE,36*SCALE))
    draw = ImageDraw.Draw(image)
    font = face(size*SCALE)
    top = (36*SCALE-sum(heights))//2
    placements=[]
    for line,box,height in zip(lines,boxes,heights):
        left = ((width*SCALE-(box[2]-box[0]))//2 if align=='center'
                else (width-6)*SCALE-(box[2]-box[0]))
        draw.text((left-box[0],top-box[1]),line,font=font,fill='white',
                  stroke_width=stroke*SCALE,stroke_fill=(*outline,255))
        placements.append([left/SCALE,top/SCALE,(left+box[2]-box[0])/SCALE,(top+height)/SCALE])
        top+=height
    # Modest original-style blue halo on a transparent background.
    glow=Image.new('RGBA',image.size,(*outline,0))
    glow.putalpha(image.getchannel('A').filter(ImageFilter.GaussianBlur(SCALE*.55)).point(lambda a:a//3))
    image=Image.alpha_composite(glow,image).resize((width,36),Image.Resampling.LANCZOS)
    return image,dict(lines=lines,font_size=size,stroke_width=stroke,line_bounds=placements,alignment=align)


def _premult(color):
    r,g,b,a=color
    return r*a/255,g*a/255,b*a/255,a


def animation_info(raw):
    decoded,layers=unwrap(raw)
    if layers!=1 or decoded[:4]!=b'SSAD':
        raise ValueError('Unsupported chapter-title animation')
    token=b'AREA\x10\0\0\0'
    offsets=[i for i in range(len(decoded)-24) if decoded[i:i+8]==token]
    areas=[struct.unpack_from('<4i',decoded,i+8) for i in offsets]
    if areas.count((0,0,344,64))!=1:
        raise ValueError('Original chapter title sampling AREA changed')
    return dict(original_title_area=[0,0,344,64],all_area_keys=[list(x) for x in areas],
                ssad_layers=layers,animation_modified=False,
                reachability='SSAD supplies the 344x64 title sample; runtime selection offsets follow the existing 3x5 atlas grid. Static animation contains the initial sample only.')


def generate():
    """Return ({native archive member: bytes}, report), without writing a build."""
    originals={}
    for member,expected in GUARDS.items():
        raw=(SOURCE/member).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:
            raise ValueError('Chapter title source SHA256 mismatch: '+member)
        originals[member]=raw
    inventory=set(p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*sub_title*') if p.is_file())
    if inventory!=set(GUARDS):
        raise ValueError('Chapter title inventory changed: '+str(sorted(inventory-set(GUARDS))))
    titles=json.loads((ROOT/'work/translation/en/chapter-titles.en.json').read_text(encoding='utf-8'))['entries']
    if len(titles)!=15 or [entry['ui_id'] for entry in titles]!=list(range(28,43)):
        raise ValueError('Chapter heading manifest must contain UI IDs 28..42 exactly once')
    interface=json.loads((ROOT/'work/translation/en/interface.en.json').read_text(encoding='utf-8'))
    expected_english={row['id']:row['en'] for row in interface['entries']}
    if any(row['en']!=expected_english[row['ui_id']] for row in titles):
        raise ValueError('Chapter heading manifest differs from canonical interface English')
    DEST.mkdir(parents=True,exist_ok=True)
    replacements,reports={},[]
    for member in ATLAS_MEMBERS:
        raw=originals[member]
        if raw[:12]!=b'SHTXFS\x00\x04\x00\x02\x0a\x09' or len(raw)!=525324:
            raise ValueError('Unsupported chapter-title atlas format')
        palette=[tuple(raw[12+4*i:16+4*i]) for i in range(256)]
        transparent=next(i for i,color in enumerate(palette) if color[3]==0)
        original=Image.open(io.BytesIO(png(raw,1024,512))).convert('RGBA')
        encoded=bytearray(raw[1036:])
        lookup={}
        colors=[_premult(c) for c in palette]
        regions=[]
        variant=Path(member).stem
        outline=(0,87,160) if variant.endswith('_') else (23,66,230)
        for number,title in enumerate(titles):
            col,row=number%3,number//3
            x,y=col*344,row*64
            width=min(344,1024-x)
            # Original Japanese glow has a few low-alpha tail pixels at dy=36.
            # Preserve caption-family pixels while clearing those final tails.
            region=(x,y,x+width,y+37)
            layer,placement=_paint(title['en'],width,outline,'right' if variant.endswith('_') else 'center')
            source_bounds=original.crop(region).getchannel('A').getbbox()
            for py in range(37):
                for px in range(width):
                    offset=(y+py)*1024+x+px
                    # Preserve original English caption glow, even in adjacent bands.
                    if _caption_glow(original.getpixel((x+px,y+py))):
                        continue
                    color=layer.getpixel((px,py)) if py<36 else (0,0,0,0)
                    if not color[3]:
                        encoded[offset]=transparent
                        continue
                    if color not in lookup:
                        value=_premult(color)
                        lookup[color]=min(range(256),key=lambda i:sum((a-b)**2 for a,b in zip(value,colors[i])))
                    encoded[offset]=lookup[color]
            regions.append(dict(id=f'{variant}-chapter-{title["ui_id"]}',ui_id=title['ui_id'],
                                en=title['en'],status='inserted_texture',heading_rect=list(region),
                                original_nonzero_alpha_bounds=list(source_bounds) if source_bounds else None,
                                sampling_rect=[x,y,x+344,y+64],effective_sampling_width=width,
                                caption_glow_preserved=True,**placement))
        native=raw[:1036]+bytes(encoded)
        # Explicit guards retain caption bands, bars and other atlas pixels.
        for offset,(before,after) in enumerate(zip(raw[1036:],encoded)):
            y=offset//1024
            if not (y<293 and y%64<37) and before!=after:
                raise ValueError('Chapter atlas pixel outside heading band changed')
        decoded=Image.open(io.BytesIO(png(native,1024,512))).convert('RGBA')
        if decoded.tobytes()!=bytes(channel for index in encoded for channel in palette[index]):
            raise ValueError('Chapter indexed texture did not round-trip')
        preview=DEST/(variant+'.png')
        decoded.save(preview)
        # A dark backdrop makes transparent white/blue title artwork reviewable.
        dark=Image.new('RGBA',decoded.size,(13,22,38,255))
        Image.alpha_composite(dark,decoded).save(DEST/(variant+'-on-dark.png'))
        replacements[member]=native
        reports.append(dict(member=member,source_sha256=GUARDS[member],output_sha256=hashlib.sha256(native).hexdigest(),
                            native_palette_preserved=True,outside_heading_bands_unchanged=True,
                            decoded_preview=preview.relative_to(ROOT).as_posix(),regions=regions))
    report=dict(category='chapter_and_prologue_title_cards',unique_titles=15,textures_inserted=2,
                raster_regions_inserted=30,font='GenEi LateGo v2 Medium',assets=reports,
                inserted_region_ids=[region['id'] for asset in reports for region in asset['regions']],
                category_inventory=[dict(member=member,sha256=GUARDS[member],modified=member in replacements,
                                         role='heading atlas' if member in replacements else 'original supporting asset') for member in sorted(GUARDS)],
                animations={member:animation_info(originals[member]) for member in GUARDS if member.endswith('.bsa')},
                scope='All 15 unique titles in both chapter/prologue atlas variants; original captions, numbers, animation and supporting artwork retained.')
    (ROOT/'work/ui/chapter-title-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return replacements,report


if __name__=='__main__':
    _,report=generate()
    print(json.dumps(report,ensure_ascii=False,indent=2))
