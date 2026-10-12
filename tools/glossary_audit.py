"""Audit glossary coverage and terminology conflicts; preview first, --write saves report."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'work/glossary'
SECTIONS=('characters','labels','terms','equipment','short_ui_terms','name_component_terms')
CONTROL=re.compile(r'#[A-Za-z][0-9]*')


def records():
    for path in sorted(FOLDER.glob('*.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        for section in SECTIONS:
            for index,row in enumerate(data.get(section,[])):
                aliases=row.get('japanese',[])
                if isinstance(aliases,str):aliases=[aliases]
                yield {'file':path.name,'section':section,'entry':row,
                       'id':row.get('id',section+'_'+str(index)),
                       'aliases':aliases,'english':row.get('short_name') if section=='characters' else row.get('english'),
                       'source_ids':([row['source']['id']] if 'source' in row and isinstance(row['source'],dict) and 'id' in row['source'] else row.get('source_ids',[])),
                       'status':row.get('status',row.get('resolution_status','sourced_profile'))}


def build():
    items=list(records());errors=[]
    for key,group in _groups(items,lambda r:(r['file'],r['section'])).items():
        ids=[r['id'] for r in group]
        if len(ids)!=len(set(ids)):errors.append('Duplicate IDs in '+str(key))
    corpus=json.loads((ROOT/'work/translation/en/corpus.working.json').read_text(encoding='utf-8'))
    ui=json.loads((ROOT/'work/source/ui-strings.json').read_text(encoding='utf-8'))['rows']
    labels={r['entry']['japanese']:r['entry'] for r in items if r['section']=='labels'}
    speakers=Counter(r['speaker_jp'] for r in corpus['entries'] if r['speaker_jp'])
    missing_speakers=[s for s in speakers if s not in labels]
    if missing_speakers:errors.append('Unindexed speaker forms: '+str(len(missing_speakers)))
    for speaker,count in speakers.items():
        label=labels.get(speaker)
        if not label:continue
        if label['speaker_frequency']!=count:errors.append('Speaker frequency mismatch: '+label['id'])
        if CONTROL.findall(speaker)!=CONTROL.findall(label['english']):errors.append('Speaker control mismatch: '+label['id'])
    def slots(section,file,start,end):
        covered=set()
        for r in items:
            if r['section']!=section or r['file']!=file:continue
            covered.update(x['id'] for x in r['entry'].get('provenance',{}).get('ui_records',[]))
            covered.update(r['source_ids'])
        expected=set(range(start,end+1));missing=sorted(expected-covered)
        if missing:errors.append('Missing slots in '+file+': '+str(missing))
        return {'expected':len(expected),'indexed':len(expected&covered),'missing_ids':missing}
    coverage={'scenario_speaker_forms':{'expected':len(speakers),'indexed':len(speakers)-len(missing_speakers),'narration_rows':sum(not r['speaker_jp'] for r in corpus['entries'])},
              'ui_character_slots':slots('labels','speaker-labels.json',664,702),
              'ui_mecha_and_target_slots':slots('terms','mecha.json',703,744),
              'ui_equipment_name_slots':slots('equipment','equipment.json',745,1146),
              'ui_location_slots':slots('terms','ui-terms.json',161,190)}
    for r in items:
        entry=r['entry']
        if r['english'] is None and r['section'] not in ('equipment',):errors.append('Unexpected null English: '+r['file']+':'+r['id'])
        if r['section']=='equipment':
            identifier=entry['source_ids'][0];source=ui[identifier]
            if entry['source_keys']!=[source['key']]:errors.append('Equipment source key mismatch: '+r['id'])
            if source['fields'][0]['text'] not in r['aliases']:errors.append('Equipment source name mismatch: '+r['id'])
            if r['english']:
                if CONTROL.findall(source['fields'][0]['text'])!=CONTROL.findall(r['english']):errors.append('Equipment control mismatch: '+r['id'])
                for literal in entry['protected_literals']:
                    if literal not in r['english']:errors.append('Lost equipment literal: '+r['id'])
        if r['file'] in ('mecha.json','ui-terms.json'):
            identifier=entry['source']['id'];source=ui[identifier]
            if entry['source']['key']!=source['key'] or entry['source_display_label_jp']!=source['fields'][0]['text']:errors.append('UI glossary source mismatch: '+r['id'])
    # Disagreements at the same UI slot are defects. Other aliases can have context-dependent short/full labels.
    by_slot=defaultdict(list)
    for r in items:
        if r['section']=='name_component_terms':continue
        for identifier in r['source_ids']:
            # Integer IDs identify UI slots; scenario references identify occurrences.
            if isinstance(identifier,int):by_slot[identifier].append(r)
    slot_conflicts=[]
    for identifier,group in by_slot.items():
        names={r['english'] for r in group if r['english'] is not None}
        if len(names)>1:
            slot_conflicts.append({'source_id':identifier,'mappings':[{'file':r['file'],'id':r['id'],'english':r['english']} for r in group]})
    if slot_conflicts:errors.append('Conflicting display names at '+str(len(slot_conflicts))+' source slots')
    by_alias=defaultdict(list)
    for r in items:
        for alias in r['aliases']:by_alias[alias].append(r)
    variants=[]
    for alias,group in by_alias.items():
        names={r['english'] for r in group if r['english'] is not None}
        if len(names)>1:
            variants.append({'alias_sha256':hashlib.sha256(alias.encode('utf-8')).hexdigest(),
                             'mappings':[{'file':r['file'],'id':r['id'],'english':r['english'],'source_ids':r['source_ids']} for r in group],
                             'policy':'Match source ID, entity and scene context; never use blind alias substitution.'})
    per_file={}
    for key,group in _groups(items,lambda r:r['file']).items():
        per_file[key]={'entries':len(group),'sections':dict(Counter(r['section'] for r in group)),
                       'status_counts':dict(Counter(r['status'] for r in group))}
    equipment=json.loads((FOLDER/'equipment.json').read_text(encoding='utf-8'))['equipment']
    return {'schema_version':1,'project_version':'0.1.3','checked_on':'2026-10-11',
            'phase':'translation_in_progress','coverage':coverage,'databases':per_file,
            'indexed_entries_including_intentional_overlap':len(items),
            'equipment_resolution':{'mapped':sum(r['english'] is not None for r in equipment),
                                     'provisional':sum(r['status']=='provisional_name' for r in equipment),
                                     'unresolved':sum(r['english'] is None for r in equipment),
                                     'unresolved_source_ids':[r['source_ids'][0] for r in equipment if r['english'] is None]},
            'excluded_historical_ui_proposals':20,'source_slot_conflicts':slot_conflicts,
            'context_dependent_alias_variants':variants,'errors':errors,
            'validation':'passed' if not errors else 'failed',
            'limitations':['Equipment/game-specific names with provisional or unresolved status require research before treating them as canonical.',
                           'Prototype Eunice labels and concealed identities remain uncertain.',
                           'Raster text and remaining sentence-level vocabulary can add terminology; registry is extensible.',
                           'Glossary entries are not completed game translation rows; translation drafts are tracked separately and no playable build exists yet.']}


def _groups(rows,key):
    groups=defaultdict(list)
    for row in rows:groups[key(row)].append(row)
    return groups


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true');args=parser.parse_args()
    report=build();print(json.dumps(report,ensure_ascii=True,indent=2))
    if report['errors']:raise SystemExit(1)
    if args.write:(ROOT/'docs/glossary-status.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
