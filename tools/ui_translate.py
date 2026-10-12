"""Preview authored UI mappings with exact source structure; --write creates new slices."""
import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

from extract_script import ROOT,JP
from glossary_audit import records

CONTROL=re.compile(r'#(?:[A-Za-z]|=)[0-9]*')
PREFIX=re.compile(r'^(?:#(?:[A-Za-z]|=)[0-9]*)*')


def glossary_mapping():
    slots={}
    for row in records():
        if row['section']=='name_component_terms':continue
        if not row['english']:continue
        ids=row['source_ids']+ [r['id'] for r in row['entry'].get('provenance',{}).get('ui_records',[])]
        for identifier in ids:
            if not isinstance(identifier,int):continue
            mapping={'en':row['english'],'glossary':row['file']+':'+row['id'],'glossary_status':row['status']}
            if 'provisional' in row['status']:mapping['flags']=['provisional_glossary_name_requires_research']
            slots[identifier]=mapping
    return slots


def build(start,end,authored):
    source=json.loads((ROOT/'work/source/ui-strings.json').read_text(encoding='utf-8'))['rows']
    mappings=glossary_mapping();mappings.update({int(k):({'en':v} if isinstance(v,str) else v) for k,v in authored.items()})
    entries=[]
    for raw in source[start:end+1]:
        fields=copy.deepcopy(raw['fields']);first=raw['fields'][0]
        japanese=any(f and JP.search(f['text']) for f in fields)
        proposal=mappings.get(raw['id'])
        en=first['text'] if first else None
        flags=[];status='unchanged_existing_english' if first and any(c.isalpha() for c in en) else 'unchanged_nonlinguistic'
        if japanese:
            status='untranslated';en=''
            if proposal:
                en=proposal['en'];prefix=PREFIX.match(first['text']).group()
                if prefix and not CONTROL.search(en):en=prefix+en
                if CONTROL.findall(en)!=CONTROL.findall(first['text']):raise ValueError('Control mismatch '+str(raw['id']))
                if JP.search(en):raise ValueError('Japanese target '+str(raw['id']))
                flags=proposal.get('flags',[]);status='translated_needs_review' if flags else 'translated_draft'
        for f in fields:
            if f:
                f['jp']=f.pop('text');f['text_jp']=f['jp']
                f['en']=en if f['column']==0 else f['jp']
        context=('Internal monologue/conversation displayed by this menu; preserve the speaker and scene context.' if 'COMMENT' in raw.get('key','') else
                 'Player-visible label, confirmation, help text or name; neighboring source entries checked for category.')
        row={'id':raw['id'],'key':raw.get('key'),'source_file':'data/_dat/strings.bnd',
             'record_offset':raw['record_offset'],'label_offset':raw.get('label_offset'),
             'source_offset':first['source_offset'] if first else None,'source_bytes':first['source_bytes'] if first else None,
             'jp':first['text'] if first else None,'en':en,'fields':fields,'status':status,
             'context':proposal.get('context',context) if proposal else context,
             'decisions':proposal.get('decisions','Complete English; source pointers/IDs/nulls/controls preserved; no source-byte budget.') if proposal else 'No authored or settled glossary mapping yet.',
             'control_codes':CONTROL.findall(first['text']) if first else [],'review_flags':flags}
        if proposal and proposal.get('glossary'):row['glossary_reference']=proposal['glossary'];row['glossary_status']=proposal['glossary_status']
        if proposal and proposal.get('omission_retained'):row['source_omission_retained']=True
        entries.append(row)
    return {'schema_version':1,'project_version':'0.1.3','language':'en',
            'slice':{'first_id':start,'last_id':end,'rows_assigned':len(entries),
                     'rows_examined':min(len(source),end+11)-max(0,start-10),'context_ids':[max(0,start-10),min(len(source)-1,end+10)]},
            'glossaries':['work/glossary/'+p.name for p in (ROOT/'work/glossary').glob('*.json')],
            'status_counts':dict(Counter(r['status'] for r in entries)),
            'japanese_source_rows':sum(any(f and JP.search(f['jp']) for f in r['fields']) for r in entries),
            'meaning_review':{'reviewer':'root','status':'Authored against source and neighboring category/context; flagged uncertainties retained.','rows_assigned':len(entries)},
            'entries':entries}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start',type=int,required=True);parser.add_argument('--end',type=int,required=True)
    parser.add_argument('--mappings',type=Path);parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    if not 80<=args.start<=args.end<1792:parser.error('Range must lie within remaining UI source.')
    authored=json.loads(args.mappings.read_text(encoding='utf-8')) if args.mappings else {}
    paths=[]
    for start in range(args.start,args.end+1,80):
        end=min(start+79,args.end);result=build(start,end,authored)
        output=ROOT/f'work/translation/en/ui-{start:05d}-{end:05d}.working.json';paths.append(str(output))
        print(json.dumps({'path':str(output),'counts':result['status_counts'],'untranslated_ids':[r['id'] for r in result['entries'] if r['status']=='untranslated'],
                          'flagged_ids':[r['id'] for r in result['entries'] if r['review_flags']],
                          'samples':[{'id':r['id'],'en':r['en'],'status':r['status']} for r in result['entries'][:5]],'write':args.write},ensure_ascii=True,indent=2))
        if args.write:
            if output.exists():raise ValueError('Preserve existing working slice: '+str(output))
            output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
