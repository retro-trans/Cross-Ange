"""Preview GXT swizzled BC1/BC3 texture metadata; --write renders the base level.

Header and Vita block ordering follow Scarlet's Sony/PSVita.cs, GXT.cs and
ImageBinary.cs. BCn decoding uses Pillow; source textures and mipmaps are untouched.
"""
import argparse,hashlib,json,struct
from collections import Counter
from pathlib import Path
from PIL import Image
from extract_script import ROOT
SOURCE=ROOT/'work/ui/local/unwrapped-textures'
DEST=ROOT/'work/ui/local/textures-gxt'

def inspect(path):
    return inspect_bytes(path.read_bytes(),str(path))

def inspect_bytes(raw,label='<bytes>'):
    if raw[:4]!=b'GXT\0':return None
    version,count,offset,size,p4,p8,padding=struct.unpack_from('<7I',raw,4)
    if (version,count,p4,p8)!=(0x10000003,1,0,0):raise ValueError('Unsupported GXT header: '+label)
    data_offset,data_size,palette,flags,kind,fmt,dimensions,mips=struct.unpack_from('<8I',raw,32)
    width=dimensions&65535;height=dimensions>>16
    if kind!=0 or fmt not in (0x85000000,0x87000000):raise ValueError('Unsupported format/type')
    if not width or not height or width&(width-1) or height&(height-1):raise ValueError('Unexpected dimensions')
    if width<4 or height<4:raise ValueError('Tiny base level requires separate handling')
    block_size=8 if fmt==0x85000000 else 16
    level_bytes=(width//4)*(height//4)*block_size
    if data_offset!=offset or data_size!=size or offset+size>len(raw) or level_bytes>size:raise ValueError('Texture bounds mismatch')
    return raw,{'width':width,'height':height,'format':'BC1' if block_size==8 else 'BC3','block_bytes':block_size,
                'data_offset':offset,'data_bytes':size,'base_level_bytes':level_bytes,'mip_levels':mips}

def compact(code):
    code&=0x55555555;code=(code^(code>>1))&0x33333333;code=(code^(code>>2))&0x0f0f0f0f
    code=(code^(code>>4))&0x00ff00ff;return (code^(code>>8))&0x0000ffff

def render(raw,info):
    width=info['width'];height=info['height'];bw=width//4;bh=height//4;block=info['block_bytes'];offset=info['data_offset']
    small=min(bw,bh);k=small.bit_length()-1;linear=bytearray(info['base_level_bytes']);seen=set()
    for i in range(bw*bh):
        upper=(i>>(2*k))<<(2*k)
        if bh<bw:
            j=upper|((compact(i>>1)&(small-1))<<k)|(compact(i)&(small-1));x=j//bh;y=j%bh
        else:
            j=upper|((compact(i)&(small-1))<<k)|(compact(i>>1)&(small-1));x=j%bw;y=j//bw
        target=y*bw+x
        if x>=bw or y>=bh or target in seen:raise ValueError('Block permutation is invalid')
        seen.add(target);linear[target*block:(target+1)*block]=raw[offset+i*block:offset+(i+1)*block]
    image=Image.frombytes('RGBA',(width,height),bytes(linear),'bcn',(1 if block==8 else 3,'DXT1' if block==8 else 'DXT5'))
    return image.convert('RGB') if block==8 else image

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--limit',type=int);a=p.parse_args()
    items=[]
    for path in sorted(SOURCE.rglob('*.btx')):
        result=inspect(path)
        if result is None:continue
        raw,info=result;items.append({'source_file':path.relative_to(SOURCE).as_posix(),'decoded_sha256':hashlib.sha256(raw).hexdigest(),**info})
    selected=items[:a.limit] if a.limit else items
    print(json.dumps({'project_version':'0.1.3','gxt_textures':len(items),'selected':len(selected),'formats':dict(Counter(r['format'] for r in items)),
                      'samples':selected[:3],'scope':'Base-level preview only; complete visual inspection pending.','write':a.write},indent=2))
    if a.write:
        if DEST.exists():raise ValueError('Preserve existing previews')
        for info in selected:
            raw=(SOURCE/info['source_file']).read_bytes();image=render(raw,info);out=DEST/Path(info['source_file']).with_suffix('.png')
            out.parent.mkdir(parents=True,exist_ok=True);image.save(out)
        (DEST/'manifest.json').write_text(json.dumps({'project_version':'0.1.3','members':selected,'all_gxt_members':len(items)},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
