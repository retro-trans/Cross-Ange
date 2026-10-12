"""Validate scenario drafts against source and merge into local corpus. Preview first."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from extract_script import ROOT, extract, JP

IMMUTABLE = ('id', 'global_row', 'source_file', 'source_row', 'source_record_id',
             'source_encoding', 'speaker_jp', 'jp', 'voice_id', 'control_codes',
             'speaker_control_codes', 'adv_msg_references')
SOURCE_FIELDS = set(IMMUTABLE) | {'japanese_text_characters', 'japanese_speaker_characters', 'speaker', 'category'}
CONTROL = re.compile(r'#[A-Za-z][0-9]*')


def merge(slices, corpus_path):
    corpus = extract(ROOT / 'work/source/archive/assets/data/_scr')
    sources = {row['id']:row for row in corpus['entries']}
    seen = set()
    inputs = []
    if corpus_path.exists():
        inputs.append(('existing corpus', json.loads(corpus_path.read_text(encoding='utf-8-sig'))))
    inputs.extend((str(path), json.loads(path.read_text(encoding='utf-8-sig'))) for path in slices)
    for label, data in inputs:
        assigned = data.get('rows_in_slice')
        if assigned is not None and len(data['entries']) != assigned:
            raise ValueError('Assigned row count changed: ' + label)
        for draft in data['entries']:
            source = sources.get(draft['id'])
            if source is None:
                raise ValueError('Unknown source ID: ' + draft['id'])
            if label != 'existing corpus':
                if draft['id'] in seen:
                    raise ValueError('Overlapping slice IDs: ' + draft['id'])
                seen.add(draft['id'])
            for key in IMMUTABLE:
                if draft.get(key) != source.get(key):
                    raise ValueError('Source mismatch: ' + draft['id'] + ':' + key)
            target = draft.get('en', '')
            status = draft.get('status', 'untranslated')
            if target:
                if CONTROL.findall(target) != source['control_codes']:
                    raise ValueError('Control mismatch: ' + draft['id'])
                if JP.search(target):
                    raise ValueError('Japanese target leakage: ' + draft['id'])
            elif status != 'untranslated' and not (status == 'not_translatable_empty' and source['jp'] == ''):
                raise ValueError('Unexpected empty target: ' + draft['id'])
            for key, value in draft.items():
                if key not in SOURCE_FIELDS:
                    source[key] = value
            # Speaker spelling is refreshed from the current glossary, not a stale slice.
    corpus['translation_progress'] = {
        'drafted_nonempty_records':sum(bool(row['en']) for row in corpus['entries']),
        'remaining_nonempty_records':sum(bool(row['jp']) and not row['en'] for row in corpus['entries']),
        'preserved_empty_records':sum(row['status'] == 'not_translatable_empty' for row in corpus['entries']),
        'status_counts':dict(Counter(row['status'] for row in corpus['entries'])),
        'flagged_draft_rows':[row['global_row'] for row in corpus['entries'] if row.get('review_flags')],
        'insertion_status':'not_inserted_or_tested_in_game'}
    return corpus


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slices', nargs='+', type=Path)
    parser.add_argument('--corpus', type=Path, default=ROOT / 'work/translation/en/corpus.working.json')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = merge(args.slices, args.corpus)
    print(json.dumps({'summary':result['summary'],'progress':result['translation_progress'],
                      'sample':[{key:row[key] for key in ('id','speaker','en','status')} for row in result['entries'] if row['en']][:3],
                      'write':args.write}, ensure_ascii=True, indent=2))
    if args.write:
        args.corpus.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
