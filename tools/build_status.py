"""Attach the latest local build record to progress reports; preview before --write."""
import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def attach(report):
    version = (ROOT / 'VERSION').read_text().strip()
    folder = ROOT / 'work/output' / ('cross-ange-' + version)
    path = folder / 'manifest.json'
    if not path.exists():
        return report
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if not manifest.get('translation_drafts_inserted'):
        return report
    translation = manifest['translation']
    report.setdefault('draft_milestone_version', report['project_version'])
    report['project_version'] = version
    report['checked_on'] = date.today().isoformat()
    report['status'] = 'structured_english_local_test_build_available'
    report['latest_local_build'] = {
        'version': version,
        'manifest': path.relative_to(ROOT).as_posix(),
        'structured_targets_inserted': translation['structured_targets_inserted'],
        'scenario_files': translation['scenario']['files'],
        'scenario_layout_review_rows': len(translation['scenario']['layout_review_ids']),
        'runtime_tested': manifest['runtime_tested'],
        'scope': 'Build snapshot; later draft edits require a new build. Selected raster artwork is inserted; other raster, manual prose and movie text remain pending.'}
    if 'tutorials' in translation:
        report['latest_local_build']['tutorial_textures_inserted'] = translation['tutorials']['textures_inserted']
        report['latest_local_build']['tutorial_regions_inserted'] = translation['tutorials']['raster_regions_inserted']
    if 'chapter_titles' in translation:
        report['latest_local_build']['unique_chapter_titles_inserted'] = translation['chapter_titles']['unique_titles']
        report['latest_local_build']['chapter_title_regions_inserted'] = translation['chapter_titles']['raster_regions_inserted']
        report['latest_local_build']['chapter_title_textures_inserted'] = translation['chapter_titles']['textures_inserted']
    if 'ui_layout' in translation:
        report['latest_local_build']['compact_ui_labels_inserted'] = translation['ui_layout']['display_adaptations']
        report['latest_local_build']['ui_label_layout_record'] = translation['ui_layout']['layout_record']
    if 'font' in translation:
        report['latest_local_build']['font'] = translation['font']['family']
        report['latest_local_build']['pixel_layout'] = translation['scenario']['pixel_layout']
    install = folder / 'vita3k-install.json'
    if install.exists():
        record = json.loads(install.read_text(encoding='utf-8'))
        report['latest_local_build']['installation_status'] = record['status']
        report['latest_local_build']['installation_record'] = install.relative_to(ROOT).as_posix()
    issue_path = ROOT / 'work/ui/dialogue-layout-issue.json'
    if issue_path.exists():
        issue = json.loads(issue_path.read_text(encoding='utf-8'))
        if issue['build'] == version and not issue.get('fix_runtime_verified'):
            report['status'] = 'structured_english_dialogue_layout_failed'
            report['latest_local_build']['runtime_tested'] = True
            report['latest_local_build']['runtime_test_result'] = 'failed_dialogue_layout'
            report['latest_local_build']['runtime_issue'] = issue_path.relative_to(ROOT).as_posix()
        elif issue.get('fix_build') == version and not issue.get('fix_runtime_verified'):
            report['latest_local_build']['runtime_test_result'] = 'parser_fix_awaiting_in_game_confirmation'
            report['latest_local_build']['runtime_issue'] = issue_path.relative_to(ROOT).as_posix()
    startup_path = ROOT / 'work/ui/font-startup-issue.json'
    if startup_path.exists():
        startup = json.loads(startup_path.read_text(encoding='utf-8'))
        if startup.get('fix_build') == version and not startup.get('fix_runtime_verified'):
            report['latest_local_build']['runtime_test_result'] = 'font_termination_fix_awaiting_in_game_confirmation'
            report['latest_local_build']['runtime_issue'] = startup_path.relative_to(ROOT).as_posix()
    runtime_path = folder / 'runtime-test.json'
    if runtime_path.exists():
        runtime = json.loads(runtime_path.read_text(encoding='utf-8'))
        report['latest_local_build']['runtime_tested'] = runtime['runtime_tested']
        report['latest_local_build']['runtime_test_result'] = runtime['runtime_result']
        if runtime['runtime_result'].startswith('failed'):
            report['status'] = 'structured_english_runtime_test_failed'
    if 'limitations' in report:
        report['limitations'] = [
            'Draft meaning/identity flags and provisional glossary entries still require review.',
            ('All ten identified tutorial images and both chapter-title atlas variants are inserted; other artwork, original manual prose, movie logos and unclear microtext remain pending.'
             if 'chapter_titles' in translation else
             'Three tutorial images are inserted; other artwork, original manual prose, movie logos and unclear microtext remain pending.'),
            'The extra Naomi eye-animation tile reported in 0.1.8 remains unresolved; a reversible original/English comparison is prepared.',
            'Structured English is inserted in the latest local test build; executable text audit and English runtime layout/testing remain pending.']
    if 'additional_tables' in report and 'insertion_status' in report['additional_tables']:
        report['additional_tables']['insertion_status'] = 'inserted_in_' + version + '_runtime_unverified'
    if 'playable_build' in report.get('validation', {}):
        report['validation'].update(
            screen_measurements='Two source captures measured approximately; English layout unverified.',
            reinsertion='All identified structured targets inserted in ' + version,
            playable_build='Local test candidate built; English runtime unverified.')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for name in ('translation-progress', 'text-inventory'):
        path = ROOT / 'docs' / (name + '.json')
        report = attach(json.loads(path.read_text(encoding='utf-8-sig')))
        print(json.dumps({'report': name, 'status': report['status'], 'latest_local_build': report.get('latest_local_build'), 'write': args.write}, indent=2))
        if args.write:
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
