"""Prepare a small translation ZIP for local Vita3K PKG rebuilding.

Only component deltas, credits and font attribution are bundled. The user
supplies the original PKG and matching local license to the player tools.
Preview by default. Publication requires a separate explicit instruction.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent/'retro-trans-tools'))
from retro_trans import vita_translation as v
from retro_trans.core import sha256_file
from retro_trans.vita_repatch import verify, require

def package(build, output=None, write=False):
    original = ROOT/'work/output/releases'/('v'+build)
    data = json.loads((original/'VITA-PKG.json').read_text(encoding='utf-8'))
    require(data['build'] == build, 'Retained profile differs from requested game build.')
    data['minimum_app_version'] = '0.5.16'
    v.validate(data)
    native = json.loads((ROOT/'docs'/('pkg-patching-validation-'+build+'.json')).read_text(encoding='utf-8'))
    require(native['native_pkg_install_verified'] and native['verified_files'] ==
            len(data['source_files'])+len(data['extras']), 'Missing native-output provenance.')
    manifest = json.loads((original/'BUILD-MANIFEST.json').read_text(encoding='utf-8'))
    component = {r['edition'].split(' / ',1)[1]:r for r in manifest['patches']}
    for row in data['source_files']:
        verify(ROOT/'work/source/decrypted'/row['path'],row)
    for row in data['files']:
        declared = component[row['path']]
        require(row['target']['sha256'] == declared['target_sha256'] and
                row['patch']['sha256'] == declared['patch_sha256'], 'Component profile differs from verified delta.')
        verify(original/row['patch']['name'],row['patch'])
        verify(ROOT/'work/output'/('cross-ange-'+build)/'game'/row['path'],row['target'])
    output = Path(output) if output else ROOT/'work/output/releases'/('v'+build+'-local-pkg')
    require(not output.exists(), 'Preserve existing output folder.')
    print(json.dumps(dict(build=build,route='small patches + local licensed PKG rebuilding',
        minimum_app_version=data['minimum_app_version'],output=str(output),write=write),indent=2))
    if not write:return
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.pkg-release-',dir=output.parent) as temporary:
        stage=Path(temporary)
        encoded=(json.dumps(data,indent=2)+'\n').encode()
        (stage/v.MANIFEST).write_bytes(encoded)
        archive=stage/('Cross-Ange-English-'+build+'-Vita-PKG-patches.zip')
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
            bundle.writestr(v.MANIFEST,encoded)
            for row in data['files']:
                bundle.write(original/row['patch']['name'],row['patch']['name'])
            for row in data['extras']:
                source=ROOT/'work/output'/('cross-ange-'+build)/'game'/row['path']
                verify(source,row)
                bundle.write(source,row['name'])
        with v.archive_description(archive) as (profile, patches):
            require(profile==data,'ZIP and separate profile differ.')
        names=[v.MANIFEST,archive.name]
        (stage/'VITA-PKG-SHA256SUMS.txt').write_bytes(''.join(sha256_file(stage/name)+'  '+name+'\n' for name in names).encode())
        stage.rename(output)
    print('Small ZIP/profile verified locally. No complete game or license bundled.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    require(args.build.startswith('0.') and args.build.count('.')==2 and
            all(part.isdigit() for part in args.build.split('.')),'Expected version 0.x.y.')
    package(args.build,args.output,args.write)

if __name__ == '__main__':main()
