"""Preview verified strings.bnd rows and BDC IDs; optional ignored-source export.

Schema was reconstructed from this game's local tables, not arbitrary strings.
"""
import argparse
import json
import re
import struct
from pathlib import Path

JP = re.compile(r'[\u3041-\u3096\u30a1-\u30fa\u3400-\u9fff]')


def parse(root):
    binary = (root / 'strings.bnd').read_bytes()
    labels = (root / 'strings_src.bdc').read_bytes()
    groups, payload_size, unknown, table_offset, count = struct.unpack_from('<5I', binary)
    if groups != 1 or table_offset != 20:
        raise ValueError('Unexpected string table header')
    label_count, label_base = struct.unpack_from('<2I', labels)
    names = {}
    for index in range(label_count):
        entry = 16 + index * 16
        relative, identifier = struct.unpack_from('<2I', labels, entry + 8)
        start = label_base + relative + 4
        end = labels.index(b'\0', start)
        name = labels[start:end].decode('ascii')
        if name in ('STRINGS_IDX', 'STRINGS_NUM'):
            continue
        if identifier in names:
            raise ValueError('Duplicate BDC numeric ID')
        names[identifier] = {'key':name,'label_offset':start,'label_entry_offset':entry}
    rows = []
    data_start = table_offset + count * 8
    for identifier in range(count):
        record_offset = table_offset + identifier * 8
        pointers = struct.unpack_from('<2I', binary, record_offset)
        fields = []
        for column,pointer in enumerate(pointers):
            if pointer == 0:
                fields.append(None)
                continue
            if pointer < data_start or pointer >= len(binary) or pointer % 2:
                raise ValueError(f'Invalid string pointer {pointer:x}')
            end = pointer
            while binary[end:end+2] != b'\0\0':
                end += 2
                if end >= len(binary):
                    raise ValueError('Unterminated string')
            text = binary[pointer:end].decode('utf-16le')
            fields.append({'column':column,'source_offset':pointer,'source_bytes':end-pointer,
                           'text':text,'contains_japanese':bool(JP.search(text))})
        rows.append({'id':identifier,'record_offset':record_offset,
                     **names.get(identifier,{}),'fields':fields})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_directory',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    rows = parse(args.data_directory)
    japanese = [row for row in rows if any(field and field['contains_japanese'] for field in row['fields'])]
    summary = {'table_rows':len(rows),'nonempty_rows':sum(any(x is not None for x in row['fields']) for row in rows),
               'japanese_rows':len(japanese),'japanese_fields':sum(field is not None and field['contains_japanese'] for row in rows for field in row['fields']),
               'symbolic_keys':sum(bool(row.get('key')) for row in rows),
               'second_pointer_nonzero':sum(row['fields'][1] is not None for row in rows),
               'preview':japanese[:8]}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf-8') as output:
            json.dump({'source':'data/_dat/strings.bnd','summary':summary,'rows':rows},output,ensure_ascii=False,indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
