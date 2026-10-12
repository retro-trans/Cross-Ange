"""Render tutorial screens into original indexed SHTXFS assets.

All text uses GenEi LateGo v2 Medium. Original palette and every index outside
explicit repair rectangles are retained. No game archive is written here.
"""
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw
from build_english_font import face
from shtx_extract import png

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'work/source/archive/assets'
PREVIEWS = ROOT / 'work/ui/local/tutorial-fixes'
SOURCE_SHA256 = {
    'data/_cg/EBG_106.btx': 'f73a112daef32fff4ffead68ee5ac2908fd794b71f9f90f6fcbb1370300d9b71',
    'data/_cg/EBG_107.btx': '87f4b9ff7630d8d3020612953952aa59808243ed4bb745ab94b4ceefc8a0f736',
    'data/_cg/EBG_109.btx': '42e172763f20c1967321909af74444de5f336cd41b83c4e360a8182937219002',
    'data/_cg/EBG_108.btx': 'afc0622cacc557ca285f282ab9934e5c359c611d8eab3407be930b1a7fb9a35b',
    'data/_cg/EBG_110.btx': 'c0818a99d4faadc7cb04470d73a8fdbee2cbb793d9aafa9763dddc3b6c0189d5',
    'data/_cg/EBG_111.btx': 'dc03a6fe6ba313aff540803b8b748aab4cb54406c0c2e700c7b088af0ab0f995',
    'data/_cg/EBG_112.btx': '1088ce7af27c73869046fc2053b97bd52609cb12f3150c9cfc91ca6583b12191',
    'data/_cg/ECG_043.btx': '1f45e76a7e3d19bed8c750213135bcd4c6349b88317ef616b6a2714a11c3e483',
    'data/_cg/ECG_044.btx': 'c8e5ff99b71bc4afe290feec51136d1f362434c7ad9b057d66323e60c3bf9491',
    'data/_cg/ECG_045.btx': 'cdcb79a3de4888f0d12cc63e263a8b909299c70e4ed8a58f37174b79e57dd552',
}


def label(identifier, erase, draw, text, size=16, sample=20, align='left'):
    return dict(id=identifier, erase=list(erase), draw=list(draw), text=text,
                size=size, background_sample_x=sample, align=align)


LAYOUT = {
    'data/_cg/EBG_106.btx': [
        label('lock', (157,139,262,155),(157,139,294,155),'Toggle Lock-On',15),
        label('freeze', (60,195,250,214),(60,195,250,214),'Freeze Bullet (Destroyer Mode only)',13),
        label('twice', (56,225,120,244),(56,225,155,244),'Press twice',17),
        label('quick', (28,250,233,271),(28,250,237,271),'Quick Turn (Destroyer Mode only)',14),
        label('weapon', (29,309,90,328),(29,309,157,328),'Switch Weapon',15),
        label('pilot', (93,423,154,443),(93,423,223,443),'Pilot Machine',16),
        label('accelerate', (768,140,800,156),(728,140,800,156),'Accelerate',14,align='right'),
        label('melee', (835,196,868,214),(786,196,868,214),'Melee Attack',14,align='right'),
        label('ranged', (898,252,931,273),(828,252,931,273),'Ranged Attack',15,align='right'),
        label('transform', (898,309,931,329),(828,309,931,329),'Transform',16,align='right'),
        label('decelerate', (835,367,868,385),(786,367,868,385),'Decelerate',14,align='right'),
        label('target', (762,423,868,443),(754,423,868,443),'Switch Target',16,align='right'),
    ],
    'data/_cg/EBG_107.btx': [
        label('sight',(315,54,402,74),(315,54,443,74),'Targeting Sight'),
        label('marker',(558,53,710,74),(558,53,710,74),'Target Marker',17),
        label('operator',(93,113,198,132),(93,113,220,132),'Operator',17),
        label('speed',(93,168,181,187),(93,168,220,187),'Your Speed',17),
        label('freeze',(93,226,195,246),(93,226,238,246),'Freeze Bullet',17),
        label('radar',(93,282,165,301),(93,282,220,301),'Radar',17),
        label('center',(95,310,220,328),(95,310,239,328),'Center: Your machine',13),
        label('goal',(114,331,162,347),(114,331,225,347),': Objective',14),
        label('enemy',(114,349,149,365),(114,349,225,365),': Enemy',14),
        label('ally',(114,367,163,383),(114,367,225,383),': Ally',14),
        label('energy',(204,396,342,418),(204,396,342,418),'Energy Gauge',17),
        label('boost',(420,397,536,418),(420,397,551,418),'Boost Gauge',17),
        label('talk',(619,398,755,418),(619,398,783,418),'Operator Conversation',15),
        label('timer',(805,113,868,132),(782,113,868,132),'Timer',17,align='right'),
        label('ranged',(796,226,869,246),(747,226,869,246),'Ranged Weapon',16,align='right'),
        label('kills',(814,339,868,359),(773,339,868,359),'Kill Count',17,align='right'),
        label('one',(837,369,868,388),(830,369,899,388),'1 enemy',14),
        label('ten',(823,397,868,418),(823,397,911,418),'10 enemies',14),
        label('embedded',(383,330,584,343),(383,330,585,343),'Radar contact. New enemies approaching.',10,sample=604),
    ],
    'data/_cg/EBG_109.btx': [
        label('lounge',(221,55,490,73),(221,55,680,73),': Talk with the heroines in the lounge.',16,sample=800),
        label('config',(377,370,633,387),(377,370,810,387),': Save, load, and change settings.',16,sample=800),
        label('title',(266,96,368,108),(266,95,502,109),'A New Posting, and Then...',12,sample=480),
        label('embedded',(401,335,599,348),(401,335,704,348),'Come here to meet everyone and talk.',12,sample=702),
    ],
    'data/_cg/EBG_108.btx': [
        label('shop',(211,51,370,68),(211,51,530,69),': Buy weapons.',16,sample=800),
        label('hangar',(373,96,589,113),(373,96,740,114),': Customize your machine.',16,sample=800),
        label('briefing',(358,419,549,436),(358,419,775,437),': Return to the briefing.',16,sample=800),
        label('sortie',(229,481,405,499),(229,481,640,499),': Deploy on a mission.',16,sample=800),
        label('embedded',(251,393,398,403),(251,392,625,405),'Adjust settings for your frame.',11,sample=704),
        label('view',(617,151,643,161),(617,150,646,163),'Form',9,sample=596),
        label('view-rotate',(664,151,717,161),(664,150,717,163),'Rotate',10,sample=596),
    ],
    'data/_cg/EBG_110.btx': [
        label('deck',(280,55,708,74),(280,55,922,75),': Customize your machine and buy weapons on the deck.',16,sample=800),
        label('title',(266,96,368,109),(266,95,502,109),'Why I Fight',12,sample=480),
        label('embedded',(401,335,618,348),(401,335,704,349),'Customize your machine on the deck.',12,sample=702),
    ],
    'data/_cg/EBG_111.btx': [
        label('mission',(308,55,530,74),(308,55,820,75),': Take on training missions.',16,sample=800),
        label('title',(266,96,331,109),(266,95,502,109),'A Pleasant Meal',12,sample=480),
        label('embedded',(401,335,626,348),(401,335,704,349),'Come here to take missions and train.',12,sample=702),
    ],
    'data/_cg/EBG_112.btx': [
        label('cash',(360,29,884,49),(360,29,941,49),'Cash Earned: Your highest cash reward for this mission.',16,sample=20),
        label('rank',(530,60,944,79),(530,60,952,80),'Clear Rank: Your rank after completing the mission.',16,sample=20),
        label('mission',(239,375,625,393),(239,374,905,394),'Mission: Shows the missions currently available.',17,sample=800),
        label('title',(266,96,331,109),(266,95,502,109),'A Pleasant Meal',12,sample=480),
        label('power',(262,148,352,160),(262,147,459,162),'The Power of Para-mail',12,sample=454),
        label('time',(262,172,414,185),(262,172,459,187),'Time Attack: DRAGONs',12,sample=454),
        label('transport',(262,196,394,210),(262,195,459,211),'Rescue the Transport Again',12,sample=454),
        label('defense1',(262,221,394,234),(262,220,459,235),'Defense of Arzenal I',12,sample=454),
        label('defense2',(262,245,394,258),(262,244,459,259),'Defense of Arzenal II',12,sample=454),
        label('embedded',(407,335,594,348),(401,335,704,349),'(Which mission should I take this time...?)',12,sample=702),
    ],
    'data/_cg/ECG_043.btx': [
        label('affection',(221,40,798,59),(221,40,948,61),'Affection Gauge: Marker type and tap timing affect how much it rises.',17,sample='edges'),
        label('timer',(739,123,924,142),(739,122,952,144),'Timer: Time limit.',17,sample='edges'),
        label('markers',(32,165,213,186),(32,164,225,186),'Touch Markers',19,sample='edges'),
        label('large',(87,210,217,227),(87,210,235,228),': Large increase',15,sample='edges'),
        label('small',(87,250,217,267),(87,250,235,268),': Small increase',15,sample='edges'),
        label('down',(87,290,202,307),(87,290,235,308),': Decrease',15,sample='edges'),
        label('window',(58,345,214,365),(58,344,236,366),'Conversation Window:',16,sample='edges'),
        label('window-toggle',(78,377,340,393),(78,377,474,393),'Show / hide the conversation window.',14,sample='edges'),
        label('window-hidden',(58,396,278,416),(58,399,474,416),'(Normally hidden.)',14,sample='edges'),
        label('condition',(495,376,649,391),(495,375,692,393),'Condition:',17,sample='edges'),
        label('condition-help',(494,400,890,415),(494,400,944,419),'Stronger waves mean a better chance to raise affection.',15,sample='edges'),
        label('reaction',(283,236,332,250),(283,236,397,252),"That's nice.",11,sample=399),
    ],
    'data/_cg/ECG_044.btx': [
        label('window',(40,193,181,216),(40,193,233,215),'Conversation Window',17,sample='edges'),
        label('timer',(739,123,924,142),(739,122,952,144),'Timer: Time limit.',17,sample='edges'),
        label('options',(504,372,656,391),(504,372,740,393),'Show Choices:',17,sample='edges'),
        label('options-help',(505,398,758,435),(505,401,901,436),'With the conversation window visible,\npress Square to display the choices.',15,sample='edges'),
        label('dialogue',(278,209,389,277),(278,208,390,278),"Hey, Ange, what\ndo you do when\nyou're not\ntraining?",12,sample=(390,205)),
        label('wait',(546,313,628,327),(546,313,630,327),'Wait a second!',11,sample=631),
    ],
    'data/_cg/ECG_045.btx': [
        label('options',(381,376,448,395),(381,376,453,396),'Choices:',19,sample='edges'),
        label('options-select',(511,378,612,394),(511,378,617,395),'Select choice.',14,sample='edges'),
        label('options-confirm',(642,378,690,394),(641,378,697,395),'Confirm.',13,sample='edges'),
        label('options-close',(721,378,855,394),(721,378,915,395),'Close choices.',14,sample='edges'),
        label('dialogue',(278,186,389,237),(278,186,390,239),'Why do I have\nto do something\nso troublesome?',12,sample=(390,182)),
        label('choice1',(429,284,632,299),(429,283,637,300),'So strong without even trying. Amazing.',11,sample=633),
        label('choice2',(379,312,593,326),(379,311,611,328),"Secret training? That's Ange for you.",12,sample=608),
        label('choice3',(410,339,551,352),(410,338,592,354),'I wonder how much Ange weighs.',11,sample=582),
    ],
}


def _premult(color):
    r, g, b, a = color
    return (r*a/255, g*a/255, b*a/255, a)


def generate():
    """Return ({archive member: native texture bytes}, verification report)."""
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    replacements, reports = {}, []
    for member, labels in LAYOUT.items():
        raw = (SOURCE/member).read_bytes()
        if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256[member]:
            raise ValueError('Tutorial source SHA256 mismatch: '+member)
        if raw[:12] != b'SHTXFS\x00\x04\x00\x04\x0a\x0a' or len(raw) != 1049612:
            raise ValueError('Unexpected tutorial texture format: '+member)
        original = Image.open(io.BytesIO(png(raw,1024,1024))).convert('RGBA')
        edited = original.copy()
        canvas = ImageDraw.Draw(edited)
        allowed = Image.new('1', edited.size)
        bounds = ImageDraw.Draw(allowed)
        placements = []
        for item in labels:
            x0,y0,x1,y1 = item['erase']
            sample = item['background_sample_x']
            for y in range(y0,y1):
                if sample == 'edges':
                    left = original.getpixel((x0-3,y))
                    right = original.getpixel((x1+3,y))
                    for x in range(x0,x1):
                        fraction = (x-x0)/(x1-x0)
                        edited.putpixel((x,y), tuple(round(a+(b-a)*fraction) for a,b in zip(left,right)))
                else:
                    color = original.getpixel(tuple(sample) if isinstance(sample,(tuple,list)) else (sample,y))
                    canvas.line((x0,y,x1-1,y),fill=color)
            bounds.rectangle((x0,y0,x1-1,y1-1),fill=1)
            dx,dy,rx,by = item['draw']
            for size in range(item['size'],8,-1):
                font = face(size)
                box = canvas.multiline_textbbox((0,0),item['text'],font=font,spacing=2)
                if box[2]-box[0] <= rx-dx and box[3]-box[1] <= by-dy:
                    break
            else:
                raise ValueError('Tutorial text does not fit: '+item['id'])
            tx = rx-box[2] if item['align']=='right' else dx-box[0]
            canvas.multiline_text((tx,dy-box[1]), item['text'],font=font,fill='white',spacing=2)
            drawn = canvas.multiline_textbbox((tx,dy-box[1]),item['text'],font=font,spacing=2)
            if drawn[0]<dx or drawn[1]<dy or drawn[2]>rx or drawn[3]>by:
                raise ValueError('Tutorial text exceeded its permitted rectangle: '+item['id'])
            bounds.rectangle((dx,dy,rx-1,by-1),fill=1)
            placements.append({**item,'id':Path(member).stem+'-'+item['id'],
                               'status':'inserted_texture','font_size':size,'text_bounds':list(drawn)})
        palette = [tuple(raw[12+4*i:16+4*i]) for i in range(256)]
        colors = [_premult(c) for c in palette]
        lookup = {c:i for i,c in enumerate(palette)}
        encoded = bytearray(raw[1036:])
        # A 1-bit image is packed; use pixel iteration for strict region guard.
        region_pixels = allowed.getdata()
        changed_pixels = 0
        for i,(pixel,old_pixel,permit) in enumerate(zip(edited.getdata(),original.getdata(),region_pixels)):
            if not permit:
                if pixel != old_pixel:
                    raise ValueError('Pixel outside tutorial region changed')
                continue
            if pixel == old_pixel:
                continue
            if pixel not in lookup:
                value = _premult(pixel)
                lookup[pixel] = min(range(256),key=lambda n:sum((a-b)**2 for a,b in zip(value,colors[n])))
            index = lookup[pixel]
            changed_pixels += index != encoded[i]
            encoded[i] = index
        native = raw[:1036]+bytes(encoded)
        decoded = Image.open(io.BytesIO(png(native,1024,1024))).convert('RGBA')
        if decoded.tobytes() != bytes(c for index in encoded for c in palette[index]):
            raise ValueError('Native indexed encoding did not round-trip')
        for i,permit in enumerate(allowed.getdata()):
            if not permit and native[1036+i] != raw[1036+i]:
                raise ValueError('Native texture changed outside repair regions')
        if native[:1036] != raw[:1036] or len(native)!=len(raw):
            raise ValueError('Native tutorial palette/header changed')
        preview = PREVIEWS/(Path(member).stem+'.png')
        decoded.crop((0,0,960,544)).save(preview)
        replacements[member] = native
        reports.append({'member':member,'source_sha256':hashlib.sha256(raw).hexdigest(),
                        'output_sha256':hashlib.sha256(native).hexdigest(),
                        'changed_pixels':changed_pixels,'original_palette_preserved':True,
                        'outside_regions_unchanged':True,'decoded_preview':str(preview.relative_to(ROOT)),
                        'labels':placements})
    report = {'font':'GenEi LateGo v2 Medium','assets':reports,
              'textures_inserted':len(reports),
              'raster_regions_inserted':sum(len(r['labels']) for r in reports),
              'inserted_region_ids':[label['id'] for r in reports for label in r['labels']],
              'scope':'All ten identified tutorial textures are inserted. Other raster drafts, movie logos and original manual prose remain pending.',
              'validation':'Native header, palette, dimensions and outside-region indices preserved; previews decoded from emitted bytes.'}
    (ROOT/'work/ui/tutorial-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return replacements, report


if __name__=='__main__':
    _, report = generate()
    print(json.dumps(report,indent=2))
