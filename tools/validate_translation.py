"""Validate English exports and working translations against immutable scenario/UI source."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from extract_script import ROOT
from merge_translation import merge
from strip_jp import strip

CONTROL = re.compile(r'#(?:[A-Za-z]|=)[0-9]*')


def validate(path):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if data['entries'] and data['entries'][0].get('source_asset_kind') == 'bnd_text':
        from additional_text_extract import extract
        original={row['id']:row for row in extract()['entries']}
        assert len({row['id'] for row in data['entries']})==len(data['entries'])
        for row in data['entries']:
            source=original[row['id']]
            for key in source:
                if key not in ('en','status','review_flags'):
                    assert row[key]==source[key],(row['id'],key)
            assert row['en'],row['id']
            assert CONTROL.findall(row['en'])==CONTROL.findall(row['jp']),row['id']
        translated=len(data['entries'])
    elif data['entries'] and data['entries'][0].get('source_asset_kind') == 'video_raster':
        assert len({row['id'] for row in data['entries']})==len(data['entries'])
        cache={}
        for row in data['entries']:
            assert row['source_asset_kind']=='video_raster',row['id']
            root=(ROOT/'work/source/decrypted').resolve();src=(root/row['source_file']).resolve()
            assert root in src.parents,row['id']
            if src not in cache:
                info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','format=duration:stream=width,height','-of','json',str(src)]))
                cache[src]=(hashlib.sha256(src.read_bytes()).hexdigest(),info)
            digest,info=cache[src];assert digest==row['source_sha256'],row['id']
            dimensions=info['streams'][0];w=dimensions['width'];h=dimensions['height']
            assert row['frame_dimensions']=={'width':w,'height':h},row['id']
            assert 0<=row['time_interval_seconds']['start']<row['time_interval_seconds']['end']<=float(info['format']['duration']),row['id']
            region=row['region'];assert 0<=region['x']<w and 0<=region['y']<h,row['id']
            assert region['width']>0 and region['height']>0,row['id']
            assert region['x']+region['width']<=w and region['y']+region['height']<=h,row['id']
            assert row['en'],row['id']
        translated=len(data['entries'])
    elif data['entries'] and data['entries'][0]['source_file']=='sce_sys/param.sfo':
        from extract_sfo import read_sfo
        source=read_sfo(ROOT/'work/source/decrypted/sce_sys/param.sfo')
        originals={row['id']:row for row in source['entries']}
        assert len(data['entries'])==len(originals)
        assert len({row['id'] for row in data['entries']})==len(data['entries'])
        for row in data['entries']:
            for key in ('jp','source_file','source_field','source_offset','source_encoding'):
                assert row[key]==originals[row['id']][key],(row['id'],key)
            assert row['en'],row['id']
            assert CONTROL.findall(row['jp'])==CONTROL.findall(row['en']),row['id']
        translated=len(data['entries'])
    elif data['entries'] and data['entries'][0].get('source_asset_kind') in ('texture_raster','png_raster'):
        assert len({row['id'] for row in data['entries']})==len(data['entries'])
        for row in data['entries']:
            assert row['source_asset_kind'] in ('texture_raster','png_raster'),row['id']
            asset_root=(ROOT/('work/source/decrypted' if row['source_asset_kind']=='png_raster' else 'work/source/archive/assets')).resolve()
            image_path=(asset_root/row['source_file']).resolve()
            assert asset_root in image_path.parents,row['id']
            raw=image_path.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==row['source_sha256'],row['id']
            if row['source_asset_kind']=='png_raster':
                assert raw[:8]==b'\x89PNG\r\n\x1a\n',row['id']
                width=int.from_bytes(raw[16:20],'big');height=int.from_bytes(raw[20:24],'big')
            else:
                from dr12ae_extract import unwrap
                raw,_=unwrap(raw)
            if row['source_asset_kind']=='png_raster':pass
            elif raw[:6]==b'SHTXFS':
                width=int.from_bytes(raw[6:8],'little');height=int.from_bytes(raw[8:10],'little')
            else:
                from gxt_extract import inspect_bytes
                checked=inspect_bytes(raw,row['id']);assert checked is not None,row['id']
                info=checked[1];width=info['width'];height=info['height']
            assert row['texture_dimensions']=={'width':width,'height':height},row['id']
            region=row['region'];assert 0<=region['x']<width and 0<=region['y']<height,row['id']
            assert region['width']>0 and region['height']>0,row['id']
            assert region['x']+region['width']<=width and region['y']+region['height']<=height,row['id']
            assert row['en'],row['id']
        translated=len(data['entries'])
    elif data['entries'] and data['entries'][0]['source_file'].startswith('sce_sys/manual/'):
        assert len({row['id'] for row in data['entries']}) == len(data['entries'])
        for row in data['entries']:
            image_path = ROOT / 'work/source/decrypted' / row['source_file']
            assert image_path.resolve().parent == (ROOT / 'work/source/decrypted/sce_sys/manual').resolve(), row['id']
            assert hashlib.sha256(image_path.read_bytes()).hexdigest() == row['source_sha256'], row['id']
            raw=image_path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n',row['id']
            w=int.from_bytes(raw[16:20],'big');h=int.from_bytes(raw[20:24],'big')
            assert row['image_width']==w and row['image_height']==h,row['id']
            if 'region' in row:
                box=row['region'];assert 0<=box['x']<w and 0<=box['y']<h,row['id']
                assert box['width']>0 and box['height']>0,row['id']
                assert box['x']+box['width']<=w and box['y']+box['height']<=h,row['id']
            assert row['en'], row['id']
        translated = len(data['entries'])
    elif data['entries'] and data['entries'][0]['source_file'] == 'data/_dat/strings.bnd':
        source = json.loads((ROOT / 'work/source/ui-strings.json').read_text(encoding='utf-8'))
        by_id = {row['id']:row for row in source['rows']}
        assert len({row['id'] for row in data['entries']}) == len(data['entries'])
        for row in data['entries']:
            original = by_id[row['id']]
            for key in ('key','record_offset','label_offset'):
                assert row.get(key) == original.get(key), (row['id'],key)
            assert len(row['fields']) == len(original['fields']) == 2, row['id']
            for field, raw in zip(row['fields'],original['fields']):
                assert (field is None) == (raw is None), row['id']
                if field is not None:
                    for key in ('column','source_offset','source_bytes'):
                        assert field[key] == raw[key], (row['id'],key)
                    assert field['jp'] == raw['text'], row['id']
                    assert CONTROL.findall(field['en']) == CONTROL.findall(field['jp']), row['id']
                    if row['status'].startswith('unchanged_'):
                        assert field['en'] == field['jp'], row['id']
            assert row['en'] == (row['fields'][0]['en'] if row['fields'][0] else None), row['id']
            assert row['control_codes'] == CONTROL.findall(row['jp'] or ''), row['id']
        translated = sum(row['status'].startswith('translated_') for row in data['entries'])
    else:
        merge([path], ROOT / 'work/translation/en/corpus.working.json')
        translated = sum(bool(row['en']) for row in data['entries'])
    target = path.with_name(path.name.replace('.working.json','.en.json'))
    expected = strip(data)
    if target.exists():
        assert json.loads(target.read_text(encoding='utf-8-sig')) == expected, 'Export differs from working draft: ' + str(target)
    return {'file':str(path),'rows':len(data['entries']),'translated':translated,'source_and_controls':'pass','english_export':'pass' if target.exists() else 'not_written'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths',nargs='+',type=Path)
    args=parser.parse_args()
    for path in args.paths:
        print(json.dumps(validate(path),ensure_ascii=True))


if __name__=='__main__':
    main()
