"""Preview strict indexed SHTXFS texture decoding; --write exports original pixels as PNG."""
import argparse,hashlib,json,struct,zlib
from collections import Counter
from pathlib import Path
from extract_script import ROOT

SOURCE=ROOT/'work/source/archive/assets'
DEST=ROOT/'work/ui/local/textures'

def inspect(path):
    data=path.read_bytes()
    if data[:6]!=b'SHTXFS':return None
    width,height=struct.unpack('<HH',data[6:10])
    if not width or not height or len(data)!=12+1024+width*height:
        raise ValueError('Unexpected indexed texture size: '+str(path))
    if (1<<data[10],1<<data[11])!=(width,height):
        raise ValueError('Unexpected dimension exponents: '+str(path))
    if not any(data[12:1036]):raise ValueError('Blank palette needs separate direct-color handling')
    return data,width,height

def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)

def png(data,width,height):
    palette=data[12:1036];pixels=data[1036:]
    scan=b''.join(b'\0'+pixels[y*width:(y+1)*width] for y in range(height))
    rgb=b''.join(palette[i:i+3] for i in range(0,1024,4))
    alpha=palette[3::4]
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,3,0,0,0))+
            chunk(b'PLTE',rgb)+chunk(b'tRNS',alpha)+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b''))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true')
    parser.add_argument('--source',type=Path,default=SOURCE);parser.add_argument('--output',type=Path,default=DEST);args=parser.parse_args()
    source_root=args.source;destination=args.output
    if source_root.resolve()==destination.resolve():raise ValueError('Source and destination must differ')
    files=sorted(source_root.rglob('*.btx'));decoded=[];unsupported=[]
    for path in files:
        result=inspect(path)
        if result is None:unsupported.append(path.relative_to(source_root).as_posix());continue
        data,width,height=result
        decoded.append({'source_file':path.relative_to(source_root).as_posix(),'width':width,'height':height,
                        'bytes':len(data),'source_sha256':hashlib.sha256(data).hexdigest(),
                        'preview_png':path.relative_to(source_root).with_suffix('.png').as_posix()})
    report={'project_version':'0.1.3','texture_members':len(files),'decoded_indexed_textures':len(decoded),
            'unsupported_textures':len(unsupported),
            'palette_order':'RGBA, following the original SHTXFS decoder; original ENERGY/BOOST labels visually verified.',
            'reference':'https://github.com/yukinogatari/Danganronpa-Tools/blob/master/dr12ae/shtx_conv.py',
            'samples':decoded[:5],'write':args.write}
    print(json.dumps(report,indent=2))
    if args.write:
        if destination.exists():raise ValueError('Preserve existing texture export: '+str(destination))
        destination.mkdir(parents=True)
        for item in decoded:
            source=source_root/item['source_file'];data,width,height=inspect(source)
            target=destination/item['preview_png'];target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(png(data,width,height))
        (destination/'manifest.json').write_text(json.dumps({'report':report,'decoded':decoded,'unsupported':unsupported},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
