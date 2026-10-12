"""Preview verified battle-callout and gallery table text; --write saves local source."""
import argparse,hashlib,json,struct,re
from pathlib import Path
from extract_script import ROOT,JP,CONTROL

def string_at(raw,offset,encoding='utf-16le'):
    if offset==0:return None
    if not 0<=offset<len(raw):raise ValueError('Pointer outside file')
    if encoding=='ascii':
        end=raw.index(b'\0',offset);return raw[offset:end].decode('ascii'),end-offset
    if offset%2:raise ValueError('Unaligned UTF-16 pointer')
    end=offset
    while end+2<=len(raw) and raw[end:end+2]!=b'\0\0':end+=2
    if end+2>len(raw):raise ValueError('Unterminated UTF-16 text')
    text=raw[offset:end].decode('utf-16le')
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Unexpected text control')
    return text,end-offset

def extract():
    entries=[];tables=[]
    for name in ('BtlFriendEvt.bnd','BtlNavigatorEvt.bnd','GalleryDef.bnd'):
        src=ROOT/'work/source/archive/assets/data/_dat'/name;raw=src.read_bytes();groups,payload,unknown=struct.unpack_from('<3I',raw)
        assert groups==(4 if name=='GalleryDef.bnd' else 18)
        assert 0<payload<=len(raw) and unknown==0
        digest=hashlib.sha256(raw).hexdigest();table_records=0;field_records=0
        for group in range(groups):
            offset,count=struct.unpack_from('<2I',raw,12+group*8);table_records+=count
            if count==0:continue
            if name=='BtlFriendEvt.bnd' and group>=16:
                # Group 16 is an ASCII portrait-asset table; group 17 stores event indexes.
                if group==16:
                    for ptr in struct.unpack_from('<'+str(count*8)+'I',raw,offset):
                        if ptr:assert string_at(raw,ptr,'ascii')[0].endswith('.btx')
                continue
            stride=([28,16,68,8][group] if name=='GalleryDef.bnd' else 28)
            assert offset>=12+groups*8 and offset+count*stride<=len(raw)
            for index in range(count):
                record_offset=offset+index*stride;words=struct.unpack_from('<'+str(stride//4)+'I',raw,record_offset)
                if name=='GalleryDef.bnd':
                    # Other pointers are ASCII asset IDs or numeric flags, preserved as game data.
                    cols=([0,5,6] if group==0 else [0] if group in (1,3) else [0]+list(range(3,9))+[15])
                    if group==2:
                        for asset_col in [1]+list(range(9,15)):
                            if words[asset_col]:
                                assert string_at(raw,words[asset_col],'ascii')[0].endswith(('.btx','.model.json','.bsw'))
                else:cols=[2,4,6]
                for col in cols:
                    pointer=words[col]
                    if pointer==0:continue
                    try:text,size=string_at(raw,pointer)
                    except ValueError as e:raise ValueError(f'{name} group {group} row {index} col {col} pointer {pointer}: {e}') from e
                    field_records+=1
                    if not JP.search(text):continue
                    ident=f'{name}:g{group}:r{index}:c{col}'
                    entries.append({'id':ident,'global_row':len(entries)+1,'source_file':'data/_dat/'+name,'source_asset_kind':'bnd_text','source_sha256':digest,'source_group':group,'source_row':index,'source_column':col,'record_offset':record_offset,'record_words':list(words),'source_offset':pointer,'source_bytes':size,'source_encoding':'utf-16le','jp':text,'en':'','control_codes':CONTROL.findall(text),'voice_word':words[col-1] if name!='GalleryDef.bnd' else None,'status':'untranslated','category':'gallery_text' if name=='GalleryDef.bnd' else 'battle_callout','speaker_identity':'unverified_table_group','review_flags':['runtime_display_and_table_group_identity_pending']})
        tables.append({'source_file':'data/_dat/'+name,'groups':groups,'table_records':table_records,'nonzero_text_fields':field_records,'japanese_targets':sum(r['source_file'].endswith(name) for r in entries)})
    return {'schema_version':1,'project_version':'0.1.3','language':'en','summary':{'japanese_targets':len(entries),'unique_japanese_strings':len({r['jp'] for r in entries}),'japanese_characters':sum(len(JP.findall(r['jp'])) for r in entries),'tables':tables,'scope':'Battle voice/caption fields and gallery text; runtime occurrence and speaker mapping require verification.'},'entries':entries}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--refresh-source',action='store_true');args=p.parse_args();d=extract()
    print(json.dumps({'summary':d['summary'],'sample':d['entries'][:2],'gallery_sample':[r for r in d['entries'] if r['category']=='gallery_text'][:4],'write':args.write},ensure_ascii=True,indent=2))
    if args.write:
        target=ROOT/'work/source/additional-text.json';assert args.refresh_source or not target.exists(),'Refuse overwrite without explicit --refresh-source'
        target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
