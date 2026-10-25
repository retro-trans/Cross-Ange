"""Widen the timed-conversation bubble and fit its complete English comments.

The original executable, text scale, vertical animation, choice bars and timer
are preserved. Only the bubble body's horizontal keys and side tail move.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import struct

from PIL import Image, ImageDraw

import build_english_font as font
from build_branding import literal_wrapper, SOURCE
from dr12ae_extract import unwrap
from shtx_extract import png

ROOT = Path(__file__).resolve().parents[1]
MEMBER = 'data/_ssa/talk_battle_window.bsa'
SOURCE_SHA256 = 'fe77cac021a45a80bc1f15c2c4fcc3bf2180e35c0d919640655a561038bbecc2'
KEY = re.compile(r'STR_TMG_(?:COMMENT|REACTION)_(?:[A-Z]{3}_)?\d\d')
SCALE_X = 1333
BODY_WIDTH = 252*SCALE_X/1000
NATIVE_TEXT_WIDTH = 340
TEXT_PERCENTAGE = 85
MAX_LINES = 4
EXPECTED_COMMENTS = 211


def fit(text):
    lines = font._wrap(text.replace('#n',' ').split(),NATIVE_TEXT_WIDTH)
    result = '#n'.join(lines)
    if not lines or len(lines) > MAX_LINES:
        raise ValueError('Timed comment exceeds enlarged bubble height')
    if any(font.measure(line) > NATIVE_TEXT_WIDTH for line in lines):
        raise ValueError('Timed comment exceeds enlarged bubble width')
    if re.sub(r'\s+','',font.CONTROL.sub('',result)) != re.sub(r'\s+','',font.CONTROL.sub('',text)):
        raise ValueError('Timed layout changed comment wording')
    if font.CONTROL.findall(result.replace('#n',' ')) != font.CONTROL.findall(text.replace('#n',' ')):
        raise ValueError('Timed layout changed non-layout controls')
    return result


def comments(interface):
    overrides, rows = {}, []
    for row in interface['entries']:
        if not KEY.fullmatch(row.get('key') or ''):
            continue
        field = row['fields'][0]
        text = field['en']
        fitted = fit(text)
        overrides[row['id'],0] = fitted
        rows.append(dict(id=row['id'],key=row['key'],canonical_en=text,display_en=fitted,
                         changed=fitted!=text,lines=fitted.count('#n')+1,
                         maximum_native_width=max(map(font.measure,fitted.split('#n'))),
                         maximum_screen_width=max(font.measure(s,TEXT_PERCENTAGE) for s in fitted.split('#n'))))
    if len(rows) != EXPECTED_COMMENTS:
        raise ValueError('Timed comment inventory changed; review all users of the bubble')
    return overrides, dict(comments_checked=len(rows),
                          primary_comments=sum('_COMMENT_' in r['key'] for r in rows),
                          reactions=sum('_REACTION_' in r['key'] for r in rows),
                          reflowed=sum(r['changed'] for r in rows),
                          native_text_width=NATIVE_TEXT_WIDTH,text_percentage=TEXT_PERCENTAGE,
                          maximum_lines=MAX_LINES,body_width=BODY_WIDTH,
                          wording_and_non_layout_controls_preserved=True,
                          runtime_verified=False,entries=rows)


def sections(raw):
    starts = [m.start() for m in re.finditer(re.escape(b'PART\x04\0\0\0'),raw)]
    if raw[:4] != b'SSAD' or not starts or starts[0] != 32:
        raise ValueError('Unexpected native bubble animation')
    result = {}
    for start,end in zip(starts,starts[1:]+[len(raw)]):
        if raw[start+12:start+20] != b'NAME\x20\0\0\0':
            raise ValueError('Unexpected native part name')
        name = raw[start+20:start+52].rstrip(b'\0').decode('ascii')
        if name in result:
            raise ValueError('Duplicate animation part')
        result[name] = start,end
    return result


def curve(raw, bounds, tag):
    start,end = bounds
    offset = raw.find(tag,start,end)
    if offset < 0 or raw.find(tag,offset+4,end) >= 0:
        raise ValueError('Missing or ambiguous bubble curve')
    size = struct.unpack_from('<I',raw,offset+4)[0]
    mode,units,count = struct.unpack_from('<3I',raw,offset+8)
    if mode != 1 or units != 10000 or size != 4+28*count or not 1<=count<=3:
        raise ValueError('Unexpected native curve layout')
    return [(offset+24+i*28,struct.unpack_from('<i',raw,offset+24+i*28)[0]) for i in range(count)]


def animation():
    packed = (SOURCE/MEMBER).read_bytes()
    if hashlib.sha256(packed).hexdigest() != SOURCE_SHA256:
        raise ValueError('Original timed bubble hash mismatch')
    raw,layers = unwrap(packed)
    if layers != 1 or len(raw) != 6492:
        raise ValueError('Unexpected timed bubble animation identity')
    parts = sections(raw)
    changed = bytearray(raw)
    changes = []
    # 252px * 1.333 = 335.916px. Shift the center by half the added width
    # so the left edge and the existing text origin remain exactly fixed.
    center = 126*SCALE_X
    tail = 263000 + (252*SCALE_X-252000)
    for name in ('fukidashi_waku a','fukidashi_waku b','fukidashi_waku c'):
        for tag,old,new in ((b'SCAX',1000,SCALE_X),(b'POSX',126000,center)):
            for offset,value in curve(raw,parts[name],tag):
                if value != old:
                    raise ValueError('Native bubble horizontal key changed')
                struct.pack_into('<i',changed,offset,new)
                changes.append(dict(part=name,property=tag.decode(),offset=offset,before=old,after=new))
    for offset,value in curve(raw,parts['fukidashi_r_side'],b'POSX'):
        if value != 263000:
            raise ValueError('Native side tail position changed')
        struct.pack_into('<i',changed,offset,tail)
        changes.append(dict(part='fukidashi_r_side',property='POSX',offset=offset,before=value,after=tail))
    allowed = {i for row in changes for i in range(row['offset'],row['offset']+4)}
    if len(changes)!=12 or any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(raw,changed))):
        raise ValueError('Unexpected bubble changes outside horizontal keys')
    native = literal_wrapper(bytes(changed))
    if unwrap(native)[0] != changed:
        raise ValueError('Native bubble wrapper did not round-trip')
    report = dict(member=MEMBER,source_sha256=SOURCE_SHA256,
                  output_sha256=hashlib.sha256(native).hexdigest(),
                  original_body_width=252,body_width=BODY_WIDTH,left_edge_preserved=True,
                  text_origin_preserved=True,vertical_animation_preserved=True,
                  tail_width_preserved=True,changed_keys=changes,
                  executable_unchanged=True,runtime_verified=False)
    return {MEMBER:native},report


def write_report(layout, native):
    report = dict(text=layout,animation=native,
                  scope='Timed conversations only; source BSW audit found one user of the bubble animation.',
                  runtime_verified=False)
    report['preview'] = preview(layout)
    (ROOT/'work/ui/timed-dialogue-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def preview(layout):
    """Native slices/glyphs on a neutral plate; not a gameplay screenshot."""
    raw = (SOURCE/'data/_ssa/timing_select_parts.btx').read_bytes()
    width,height = struct.unpack_from('<HH',raw,6)
    atlas = Image.open(io.BytesIO(png(raw,width,height))).convert('RGBA')
    plate = Image.new('RGBA',(764,266),(20,31,47,255))
    draw = ImageDraw.Draw(plate)
    draw.text((20,10),'Layout preview - not in-game',font=font.face(18),fill='white')
    for column,identifier in enumerate((1402,1405)):
        row = next(r for r in layout['entries'] if r['id']==identifier)
        count = row['lines']
        w = round(BODY_WIDTH)
        h = 32*count+40
        x,y = 20+column*372,50
        body = Image.new('RGBA',(w,h))
        body.alpha_composite(atlas.crop((3,0,255,32)).resize((w,32)),(0,0))
        body.alpha_composite(atlas.crop((3,33,255,35)).resize((w,h-72)),(0,32))
        body.alpha_composite(atlas.crop((3,57,255,97)).resize((w,40)),(0,h-40))
        plate.alpha_composite(body,(x,y))
        plate.alpha_composite(atlas.crop((258,1,280,20)),(x+w,y+39))
        canvas = Image.new('RGBA',(NATIVE_TEXT_WIDTH+26,(count-1)*42+26))
        for line,text in enumerate(row['display_en'].split('#n')):
            cursor = 0
            for character in font.CONTROL.sub('',text):
                packed = font.glyph(ord(character))
                alpha = bytes(n*17 for b in packed for n in (b&15,b>>4))
                glyph = Image.new('RGBA',(26,26),'white')
                glyph.putalpha(Image.frombytes('L',(26,26),alpha))
                canvas.alpha_composite(glyph,(cursor,line*42))
                cursor += font.advances().get(ord(character),26)
        scaled = canvas.resize((round(canvas.width*.85),round(canvas.height*.85)),Image.Resampling.LANCZOS)
        plate.alpha_composite(scaled,(x+20,y+20))
    path = ROOT/'work/ui/local/timed-dialogue/layout-preview.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    plate.convert('RGB').save(path)
    return dict(path=path.relative_to(ROOT).as_posix(),
                source='Original atlas slices and native GenEi glyphs; nominal line-dependent height.',
                actual_game_capture=False)
