"""Preview current verified workload/progress; write a source-free inventory with --write."""
import argparse
import json
from pathlib import Path

from extract_script import ROOT, JP
from extract_script import extract
from glossary_audit import build as audit_glossary


def build():
    corpus=json.loads((ROOT/'work/translation/en/corpus.working.json').read_text(encoding='utf-8'))
    ui=json.loads((ROOT/'work/source/ui-strings.json').read_text(encoding='utf-8'))
    metadata=json.loads((ROOT/'work/translation/en/metadata.working.json').read_text(encoding='utf-8'))
    manual_path=ROOT/'work/translation/en/manual.working.json'
    manual=json.loads(manual_path.read_text(encoding='utf-8')) if manual_path.exists() else None
    screenshot_path=ROOT/'work/translation/en/manual-screenshots.working.json'
    screenshots=json.loads(screenshot_path.read_text(encoding='utf-8')) if screenshot_path.exists() else None
    raster_path=ROOT/'work/translation/en/raster.working.json'
    raster=json.loads(raster_path.read_text(encoding='utf-8')) if raster_path.exists() else None
    inspection_path=ROOT/'work/ui/image-inspection.json'
    inspection=json.loads(inspection_path.read_text(encoding='utf-8')) if inspection_path.exists() else {}
    video_path=ROOT/'work/translation/en/video.working.json'
    video=json.loads(video_path.read_text(encoding='utf-8')) if video_path.exists() else None
    from additional_text_extract import extract as extract_additional
    additional=extract_additional()
    extra_drafts={}
    for path in sorted((ROOT/'work/translation/en').glob('additional-slice-*.working.json')):
        for row in json.loads(path.read_text(encoding='utf-8'))['entries']:
            if row['id'] in extra_drafts:raise ValueError('Overlapping additional assignments')
            extra_drafts[row['id']]=row
    extra_translated=sum(bool(r.get('en')) for r in extra_drafts.values())
    fields=[field['text'] for row in ui['rows'] for field in row['fields'] if field]
    ui_drafts={}
    for path in sorted((ROOT/'work/translation/en').glob('ui-*.working.json')):
        for row in json.loads(path.read_text(encoding='utf-8'))['entries']:
            if row['id'] in ui_drafts:
                raise ValueError('Overlapping UI assignments')
            ui_drafts[row['id']]=row
    japanese_ui=sum(any(field and JP.search(field['text']) for field in row['fields']) for row in ui['rows'])
    ui_translated=sum(row['status'].startswith('translated_') for row in ui_drafts.values())
    script_translated=sum(bool(row['en']) and bool(JP.search(row['jp'])) for row in corpus['entries'])
    metadata_translated=sum(bool(row['en']) for row in metadata['entries'])
    characters=json.loads((ROOT/'work/glossary/characters.json').read_text(encoding='utf-8'))
    glossary_report=audit_glossary()
    source_summary=extract(ROOT/'work/source/archive/assets/data/_scr')['summary']
    meta_jp=sum(len(JP.findall(row['jp'])) for row in metadata['entries'])
    known=corpus['summary']['japanese_bearing_text_records']+japanese_ui+len(metadata['entries'])+additional['summary']['japanese_targets']
    drafted=script_translated+ui_translated+metadata_translated+extra_translated
    return {
        'schema_version':2,'project_version':'0.1.3','checked_on':'2026-10-11',
        'target_language':'en','title_id':'PCSG00597','status':'all_identified_structured_text_drafted' if known==drafted else 'translation_in_progress',
        'source':{'decrypted_app':'work/source/decrypted','canonical_archive':'work/source/archive/assets',
                  'archive_members':4486,'compressed_members':2927,'expanded_member_bytes':1591898258,
                  'manual_image_files':24,'game_assets_readable':True},
        'scenario':{**source_summary,
                    'unique_japanese_text_strings':len({row['jp'] for row in corpus['entries'] if JP.search(row['jp'])}),
                    'drafted_japanese_records':script_translated,
                    'drafted_nonempty_records':sum(bool(row['en']) for row in corpus['entries']),
                    'preserved_empty_sentinels':sum(row['status']=='not_translatable_empty' for row in corpus['entries']),
                    'first_untranslated_global_row':next((r['global_row'] for r in corpus['entries'] if r['jp'] and not r['en']),None)},
        'ui_table':{'table_rows':len(ui['rows']),'named_localization_entries':1788,
                    'japanese_records':japanese_ui,'japanese_characters':sum(len(JP.findall(text)) for text in fields),
                    'japanese_field_source_characters_including_controls':sum(len(text) for text in fields if JP.search(text)),
                    'unique_japanese_text_strings':len({text for text in fields if JP.search(text)}),
                    'drafted_japanese_records':ui_translated,'examined_table_records':len(ui_drafts),
                    'unchanged_examined_records':len(ui_drafts)-ui_translated,
                    'remaining_japanese_ids':[r['id'] for r in ui['rows'] if any(f and JP.search(f['text']) for f in r['fields']) and (r['id'] not in ui_drafts or not ui_drafts[r['id']]['status'].startswith('translated_'))],
                    'reachability':'Includes debug/error rows; live-screen occurrence not verified.'},
        'system_title_metadata':{'records':len(metadata['entries']),'japanese_characters':meta_jp,'drafted_records':metadata_translated},
        'additional_tables':{**additional['summary'],'drafted_japanese_records':extra_translated,
            'remaining_japanese_records':additional['summary']['japanese_targets']-extra_translated,
            'remaining_ids':[r['id'] for r in additional['entries'] if not extra_drafts.get(r['id'],{}).get('en')]},
        'manual':{'pages_examined':manual['pages_examined'],'drafted_reading_blocks':len(manual['entries']),
                  'coverage':manual['coverage'],'image_replacement':manual['layout_status'],
                  'included_in_structured_target_count':False,
                  'additional_screenshot_reading_regions':len(screenshots['entries']) if screenshots else 0,
                  'screenshot_coverage_report':'docs/manual-screenshot-coverage.json'} if manual else {'pages_examined':0},
        'raster':{'drafted_reading_regions':len(raster['entries']),
                  'coverage':raster['coverage'],'image_replacement':raster['layout_status'],
                  'included_in_structured_target_count':False,
                  'decoded_archive_textures':1875,
                  'initial_visual_scan_complete':inspection.get('initial_visual_scan_complete',False),
                  'readability_verification_complete':inspection.get('readability_verification_complete',False),
                  'pending_marking_groups':inspection.get('pending_marking_groups')} if raster else {'drafted_reading_regions':0},
        'video':{'drafted_reading_regions':len(video['entries']),'frames_examined':video['frames_examined'],
                 'sampling_interval_seconds':video['sampling_interval_seconds'],'coverage':video['coverage'],
                 'image_replacement':video['layout_status'],'included_in_structured_target_count':False} if video else {'drafted_reading_regions':0},
        'known_structured_text':{'japanese_records':known,'japanese_characters':corpus['summary']['japanese_text_characters']+sum(len(JP.findall(text)) for text in fields)+meta_jp+additional['summary']['japanese_characters'],
                                 'drafted_records':drafted,'remaining_japanese_records':known-drafted,
                                 'draft_percentage_of_known_records':round(100*drafted/known,2),
                                 'full_game_percentage':None,'image_text_records':None,
                                 'notes':'Per insertion target; duplicate strings retained. Speaker-name repetitions are counted separately, not added as separate dialogue records. Raster text and other unverified assets remain outside this lower bound.'},
        'glossary':{'character_profiles':len(characters['characters']),
                    'indexed_entries_including_intentional_overlap':glossary_report['indexed_entries_including_intentional_overlap'],
                    'coverage':glossary_report['coverage'],'equipment_resolution':glossary_report['equipment_resolution'],
                    'validation':glossary_report['validation'],
                    'historical_proposed_ui_terms_excluded_from_lookup':20,'names_and_terms_are_not_completed_game_rows':True},
        'validation':{'source_ids_and_controls':'See translation-progress.json for validated checkpoint.',
                       'english_export_files':len(list((ROOT/'work/translation/en').glob('*.en.json'))),
                       'english_exports':'Completed slices and consolidated scenario, UI and additional-table drafts have source-free exports. Draft status does not establish a playable translation.',
                       'screen_measurements':'pending','reinsertion':'pending','playable_build':'not_created'},
        'license_status':'User-supplied matching license successfully decrypted the package; key remains local and ignored.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    from build_status import attach
    result=attach(build())
    print(json.dumps(result,ensure_ascii=True,indent=2))
    if args.write:
        (ROOT/'docs/text-inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
