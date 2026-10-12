"""Read authoritative glossary mappings by source slot, exact speaker label or term."""
import argparse
import json

from glossary_audit import records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query',nargs='?')
    parser.add_argument('--source-id',type=int)
    parser.add_argument('--speaker',help='Exact source speaker form including any controls.')
    args=parser.parse_args()
    if args.query is None and args.source_id is None and args.speaker is None:
        parser.error('Supply a query, --source-id, or --speaker.')
    results=[]
    for row in records():
        if args.source_id is not None:
            match=args.source_id in row['source_ids'] or any(r['id']==args.source_id for r in row['entry'].get('provenance',{}).get('ui_records',[]))
        elif args.speaker is not None:
            match=row['section']=='labels' and args.speaker in row['aliases']
        else:
            needle=args.query.casefold()
            haystack=[row['id'],row['english'] or '']+row['aliases']
            match=any(needle in value.casefold() for value in haystack)
        if match:results.append({'database':row['file'],'section':row['section'],'record':row['entry']})
    print(json.dumps({'matches':len(results),'policy':'Source-slot mappings take precedence for UI. Preserve controls separately when a glossary entry is a plain term. Provisional/unresolved names require review. Historical proposed UI terms excluded.','results':results},ensure_ascii=True,indent=2))


if __name__=='__main__':main()
