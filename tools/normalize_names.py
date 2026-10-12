"""Preview glossary name corrections after meaning review; never edit source/IDs/assets."""
import argparse
import json
import re
from pathlib import Path

from extract_script import ROOT, JP


def normalize(data):
    glossary=json.loads((ROOT/'work/glossary/characters.json').read_text(encoding='utf-8'))
    policy=json.loads((ROOT/'work/glossary/name-policy.json').read_text(encoding='utf-8'))
    names={alias:row['short_name'] for row in glossary['characters'] for alias in row['japanese']}
    labels_path=ROOT/'work/glossary/speaker-labels.json'
    if labels_path.exists():
        labels=json.loads(labels_path.read_text(encoding='utf-8'))
        names.update({row['japanese']:row['english'] for row in labels['labels']})
    corrections=policy['english_alias_corrections']
    changes=[]
    for row in data['entries']:
        if 'speaker_jp' in row and row['speaker_jp'] in names:
            before=row['speaker'];row['speaker']=names[row['speaker_jp']]
            if before!=row['speaker']:changes.append({'id':row['id'],'field':'speaker','before':before,'after':row['speaker']})
        for item in [row]+[field for field in row.get('fields',[]) if field]:
            value=item.get('en')
            if not isinstance(value,str):continue
            # A name immediately after #n/#b4 is still at a text boundary.
            # Preserve controls verbatim and normalize only the text segments.
            parts=re.split(r'(#(?:[A-Za-z]|=)[0-9]*)',value)
            for index in range(0,len(parts),2):
                for alias,name in corrections.items():
                    parts[index]=re.sub(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',name,parts[index])
            updated=''.join(parts)
            if updated!=value:
                changes.append({'id':row['id'],'field':'en','before':value,'after':updated});item['en']=updated
        if isinstance(row.get('jp'),str) and 'japanese_text_characters' in row:
            row['japanese_text_characters']=len(JP.findall(row['jp']))
            row['japanese_speaker_characters']=len(JP.findall(row.get('speaker_jp','')))
    data['name_normalization']={'policy':'work/glossary/name-policy.json','status':'applied_after_meaning_review','target_changes':len(changes)}
    return changes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths',nargs='+',type=Path)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    for path in args.paths:
        data=json.loads(path.read_text(encoding='utf-8-sig'))
        changes=normalize(data)
        print(json.dumps({'path':str(path),'changes':changes,'sample_speakers':[{'id':r['id'],'speaker':r['speaker']} for r in data['entries'] if 'speaker' in r][:3],
                          'metric_refresh':'Strict Japanese-letter metric, matching inventory.','write':args.write},ensure_ascii=True,indent=2))
        if args.write:
            path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
