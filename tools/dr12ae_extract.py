"""Preview bounded FCAA55A7/GX3 decompression; --write saves separate local files.

Format reference: BlackDragonHunt's dr12ae/dr_dec.py in Danganronpa-Tools.
This implementation validates each read, back-reference and declared output size.
"""
import argparse, hashlib, json, struct
from collections import Counter
from extract_script import ROOT

MAGIC=b'\xfc\xaa\x55\xa7'
SOURCE=ROOT/'work/source/archive/assets'
DEST=ROOT/'work/ui/local/unwrapped-textures'

def decode(data):
    if data[:4]==b'GX3\0':data=data[4:]
    if data[:4]!=MAGIC:raise ValueError('Missing compressed magic')
    size,packed=struct.unpack_from('<II',data,4)
    if packed>len(data) or packed<12 or size>64*1024*1024:raise ValueError('Invalid declared sizes')
    if any(data[packed:]):raise ValueError('Unexpected nonzero trailing data')
    p=12;out=bytearray();previous=1
    def read(count):
        nonlocal p
        if p+count>packed:raise ValueError('Truncated token')
        result=data[p:p+count];p+=count;return result
    while p<packed:
        token=read(1)[0]
        if token&128:
            count=((token>>5)&3)+4;offset=((token&31)<<8)+read(1)[0];previous=offset
        elif token&64 and token&32:
            count=token&31;offset=previous
        else:
            if token&64:
                count=token&15
                if token&16:count=(count<<8)+read(1)[0]
                count+=4;out.extend(read(1)*count)
            else:
                count=token&31
                if token&32:count=(count<<8)+read(1)[0]
                out.extend(read(count))
            if len(out)>size:raise ValueError('Output exceeds declared size')
            continue
        if offset==0 or offset>len(out):raise ValueError('Invalid backward offset')
        if len(out)+count>size:raise ValueError('Output exceeds declared size')
        for _ in range(count):out.append(out[-offset])
    if len(out)!=size:raise ValueError('Output size mismatch')
    return bytes(out)

def unwrap(data):
    layers=0
    while data[:4] in (MAGIC,b'GX3\0'):
        if layers>=4:raise ValueError('Excessive nesting')
        data=decode(data);layers+=1
    return data,layers

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    items=[];signatures=Counter()
    for path in sorted(SOURCE.rglob('*.btx')):
        raw=path.read_bytes()
        if raw[:4] not in (MAGIC,b'GX3\0'):continue
        data,layers=unwrap(raw);signatures[data[:6].hex()]+=1
        items.append({'source_file':path.relative_to(SOURCE).as_posix(),'source_sha256':hashlib.sha256(raw).hexdigest(),
                      'packed_bytes':len(raw),'decoded_bytes':len(data),'layers':layers,'signature':data[:16].hex(),
                      'decoded_sha256':hashlib.sha256(data).hexdigest()})
    report={'project_version':'0.1.3','decoded_members':len(items),'signatures':dict(signatures),'samples':items[:5],
            'reference':'https://github.com/yukinogatari/Danganronpa-Tools/blob/master/dr12ae/dr_dec.py','write':args.write}
    print(json.dumps(report,indent=2))
    if args.write:
        if DEST.exists():raise ValueError('Preserve existing exports')
        for item in items:
            path=DEST/item['source_file'];path.parent.mkdir(parents=True,exist_ok=True)
            data,_=unwrap((SOURCE/item['source_file']).read_bytes());path.write_bytes(data)
        (DEST/'manifest.json').write_text(json.dumps({'report':report,'members':items},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
