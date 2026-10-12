"""Preview an inspection sheet inventory; --write renders labeled local thumbnails."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
from extract_script import ROOT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',default='data/_ssa');p.add_argument('--prefix',default='');p.add_argument('--source',type=Path,default=ROOT/'work/ui/local/textures');p.add_argument('--tag',default='');p.add_argument('--all',action='store_true',help='Include background, portrait and gallery groups.');p.add_argument('--skip-inspected',action='store_true',help='Skip files already listed in earlier inspection sheets.');p.add_argument('--write',action='store_true');a=p.parse_args()
    source=a.source.resolve()/a.folder
    files=sorted(source.glob(a.prefix+'*.png'))
    if not a.prefix and not a.all:files=[f for f in files if not f.name.startswith(('NL_','menu_loungebg_','gallery_','mission_enemy_','item_'))]
    if a.skip_inspected:
        previous=set()
        for manifest in (ROOT/'work/ui/local/inspection').glob('*/files.json'):
            previous.update((ROOT/name).resolve() for name in json.loads(manifest.read_text(encoding='utf-8')))
        files=[f for f in files if f.resolve() not in previous]
    target=ROOT/'work/ui/local/inspection'/((a.tag+'-'+a.folder.split('/')[-1]+'-'+(a.prefix or 'widgets')).strip('-'))
    print(json.dumps({'images':len(files),'samples':[f.name for f in files[:8]],'output':str(target),'write':a.write},indent=2))
    if a.write:
        if target.exists():raise ValueError('Preserve existing inspection sheets')
        target.mkdir(parents=True)
        for start in range(0,len(files),20):
            group=files[start:start+20];sheet=Image.new('RGB',(1200,220*math.ceil(len(group)/5)),(50,50,50));draw=ImageDraw.Draw(sheet)
            for i,f in enumerate(group):
                im=Image.open(f).convert('RGBA');im.thumbnail((232,190));x=(i%5)*240;y=(i//5)*220
                sheet.paste(im,(x,y),im);draw.text((x+3,y+195),f.name,fill='white')
            sheet.save(target/('%04d.png'%start))
        (target/'files.json').write_text(json.dumps([str(f.relative_to(ROOT)) for f in files],indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
