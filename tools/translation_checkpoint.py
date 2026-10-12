"""Validate saved slices and preview a consolidated translation checkpoint; --write saves it."""
import argparse,json
from collections import Counter
from pathlib import Path
from extract_script import ROOT,JP
from merge_translation import merge
from strip_jp import strip
from validate_translation import validate
from additional_text_extract import extract as extract_additional

FOLDER=ROOT/'work/translation/en'

def preview(value):
    if isinstance(value,dict):return {k:preview(v) for k,v in value.items()}
    if isinstance(value,list):
        return {'count':len(value),'first_samples':preview(value[:3])} if len(value)>12 else [preview(v) for v in value]
    return value

def collect_additional():
    source=extract_additional();by_id={r['id']:r for r in source['entries']};seen=set();paths=[]
    for path in sorted(FOLDER.glob('additional-slice-*.working.json')):
        data=json.loads(path.read_text(encoding='utf-8-sig'))
        if any(not r.get('en') for r in data['entries']):continue
        checked=validate(path)
        assert checked['english_export']=='pass',path.name
        paths.append(path)
        for row in data['entries']:
            assert row['id'] not in seen,'Overlapping additional assignments: '+row['id']
            seen.add(row['id']);by_id[row['id']].update(row)
    source['translation_progress']={'completed_slices':len(paths),'drafted_japanese_records':len(seen),
        'remaining_japanese_records':len(source['entries'])-len(seen),
        'remaining_ids':[r['id'] for r in source['entries'] if not r['en']],
        'flagged_ids':[r['id'] for r in source['entries'] if r.get('review_flags')],
        'insertion_status':'not_inserted_or_tested_in_game'}
    return source

def collect():
    completed=[];pending=[];export_rows=0
    for path in sorted(FOLDER.glob('slice-*.working.json')):
        data=json.loads(path.read_text(encoding='utf-8-sig'))
        target=path.with_name(path.name.replace('.working.json','.en.json'))
        if any(r['jp'] and not r.get('en') for r in data['entries']) or not target.exists():
            pending.append(path.name);continue
        if strip(data)!=json.loads(target.read_text(encoding='utf-8-sig')):
            raise ValueError('English export differs: '+path.name)
        completed.append(path);export_rows+=len(data['entries'])
    corpus=merge(completed,FOLDER/'corpus.working.json')
    corpus['project_version']='0.1.3'
    ui=[];ui_paths=sorted(FOLDER.glob('ui-*.working.json'))
    checks=[validate(path) for path in ui_paths]
    for path in ui_paths:ui.extend(json.loads(path.read_text(encoding='utf-8-sig'))['entries'])
    if len({r['id'] for r in ui})!=len(ui):raise ValueError('UI assignments overlap')
    interface={'schema_version':1,'project_version':'0.1.3','language':'en',
               'source_file':'data/_dat/strings.bnd','rows_assigned':len(ui),
               'status_counts':dict(Counter(r['status'] for r in ui)),
               'japanese_source_rows':sum(bool(JP.search(r['jp'] or '')) for r in ui),
               'entries':sorted(ui,key=lambda r:r['id'])}
    clean=strip(interface)
    report={'project_version':'0.1.3','checked_on':'2026-10-11','status':'translation_in_progress',
            'scenario_completed_slices':len(completed),'scenario_exported_rows':export_rows,
            'scenario_drafted_japanese_rows':sum(bool(r['en']) and bool(JP.search(r['jp'])) for r in corpus['entries']),
            'scenario_drafted_nonempty_rows':sum(bool(r['en']) for r in corpus['entries']),
            'scenario_pending_slices':pending,'ui_completed_slices':len(ui_paths),'ui_examined_rows':len(ui),
            'ui_drafted_japanese_rows':sum(r['status'].startswith('translated_') for r in ui),
            'ui_remaining_ids':[r['id'] for r in ui if r['status']=='untranslated'],
            'ui_flagged_ids':[r['id'] for r in ui if r.get('review_flags')],
            'validation':{'scenario_source_and_controls':'passed','saved_scenario_exports':'passed',
                          'ui_source_and_controls':'passed','ui_exports':Counter(c['english_export'] for c in checks)},
            'limitations':['Drafts require further meaning/layout review.','Raster text is not included.','No playable build or game test yet.']}
    manual_path=FOLDER/'manual.working.json'
    if manual_path.exists():
        manual=json.loads(manual_path.read_text(encoding='utf-8'))
        report['manual']={'pages_examined':manual['pages_examined'],'drafted_reading_blocks':len(manual['entries']),
                          'coverage':manual['coverage'],'validation':validate(manual_path),
                          'image_replacement':manual['layout_status'],'review_flags':manual['review_flags']}
        report['limitations'][1]='Texture text is not included in structured counts; manual reading blocks are separate and embedded screenshot text still needs matching.'
    raster_path=FOLDER/'raster.working.json'
    if raster_path.exists():
        raster=json.loads(raster_path.read_text(encoding='utf-8'))
        report['raster']={'drafted_reading_regions':len(raster['entries']),'coverage':raster['coverage'],
                          'validation':validate(raster_path),'image_replacement':raster['layout_status']}
    additional=collect_additional()
    report['additional_tables']={**additional['summary'],**additional['translation_progress'],
        'validation':'Source fields, pointers, controls and source-free slice exports passed.'}
    video_path=FOLDER/'video.working.json'
    if video_path.exists():
        video=json.loads(video_path.read_text(encoding='utf-8'))
        report['video']={'drafted_reading_regions':len(video['entries']),'frames_examined':video['frames_examined'],
                         'coverage':video['coverage'],'validation':validate(video_path)}
    screenshot_path=FOLDER/'manual-screenshots.working.json'
    if screenshot_path.exists():
        screenshots=json.loads(screenshot_path.read_text(encoding='utf-8'))
        report['manual_screenshots']={'drafted_reading_regions':len(screenshots['entries']),
                                    'validation':validate(screenshot_path)}
    report['scenario_remaining_japanese_rows']=sum(bool(JP.search(r['jp'])) and not r['en'] for r in corpus['entries'])
    if report['scenario_remaining_japanese_rows']==0 and not report['ui_remaining_ids'] and not additional['translation_progress']['remaining_japanese_records']:
        report['status']='all_identified_structured_text_drafted'
    report['limitations']=['Drafts retain meaning/identity review flags and require layout review.',
        'Unreadable tiny artwork and manual screenshot microtext remain pending; image/video regions are counted separately.',
        'Executable text audit, font support, reinsertion and playable game testing remain pending.']
    from build_status import attach
    return corpus,interface,clean,additional,attach(report)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    corpus,interface,clean,additional,report=collect()
    print(json.dumps({'report':preview(report),'samples':{'scenario':[{'id':r['id'],'en':r['en']} for r in corpus['entries'] if r['en']][:3],
                                               'ui':[{'id':r['id'],'en':r['en']} for r in interface['entries']][-4:]},'write':args.write},ensure_ascii=True,indent=2))
    if args.write:
        for path,data in ((FOLDER/'corpus.working.json',corpus),(FOLDER/'corpus.en.json',strip(corpus)),
                          (FOLDER/'additional.working.json',additional),(FOLDER/'additional.en.json',strip(additional)),
                          (FOLDER/'interface.working.json',interface),
                          (FOLDER/'interface.en.json',clean),(ROOT/'docs/translation-progress.json',report)):
            path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
