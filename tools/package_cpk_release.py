"""Prepare retained verified installed-file CPK patches, without publishing."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / 'retro-trans-tools'))
from retro_trans.catalog import validate_manifest
from retro_trans.core import decode, engine_context, sha256_file, PatchError

def require(condition, message):
    if not condition:
        raise PatchError(message)

def package(build, output=None, write=False):
    assets = ROOT/'work/output/releases'/('v'+build)
    manifest = json.loads((assets/'BUILD-MANIFEST.json').read_text(encoding='utf-8'))
    validate_manifest(manifest)
    require(manifest['version'] == build, 'Component manifest version differs from build.')
    proof = json.loads((ROOT/'docs'/('cpk-restoration-'+build+'.json')).read_text(encoding='utf-8'))
    require(proof['actual_apply_xdelta_ui_worker_passed'] and proof['optional_metadata_delta_passed'],
            'The installed-component route needs complete verification first.')
    output = Path(output) if output else ROOT/'work/output/releases'/('v'+build+'-cpk')
    require(not output.exists(), 'Preserve existing release folder.')
    names = ['BUILD-MANIFEST.json', 'Cross-Ange-English-'+build+'-extras.zip', 'EXTRAS-SHA256SUMS.txt']
    for row in manifest['patches']:
        require(Path(row['patch']).name == row['patch'], 'Unsafe delta name.')
        patch = assets/row['patch']
        require(patch.stat().st_size == row['patch_bytes'] and sha256_file(patch) == row['patch_sha256'],
                'Retained delta identity differs from manifest.')
        names.append(row['patch'])
    with zipfile.ZipFile(assets/names[1]) as bundle:
        require(set(bundle.namelist()) == {'INSTALL.md','EXTRAS-MANIFEST.json',
            'sce_sys/manual/025.png','sce_sys/font-license.txt'}, 'Unexpected extras inventory.')
        for name in ('sce_sys/manual/025.png', 'sce_sys/font-license.txt'):
            require(bundle.read(name) == (ROOT/'work/output'/('cross-ange-'+build)/'game'/name).read_bytes(),
                    'Credits or font attribution differ from this game build.')
    print(json.dumps(dict(build=build, route='installed CPK components', output=str(output),
                          patch_bytes=sum(r['patch_bytes'] for r in manifest['patches']), write=write), indent=2))
    if not write:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.cpk-release-', dir=output.parent) as temporary:
        stage = Path(temporary)
        with engine_context() as engine:
            for index, row in enumerate(manifest['patches']):
                name = row['edition'].split(' / ', 1)[1]
                require(name in ('cpk/Ange.cpk', 'sce_sys/param.sfo'), 'Unsupported component.')
                original = ROOT/'work/source/decrypted'/name
                require(original.stat().st_size == row['source_bytes'] and sha256_file(original) == row['source_sha256'],
                        'Original component identity differs.')
                target = stage/('roundtrip-'+str(index))
                decode(engine, original, assets/row['patch'], target, row['target_bytes'])
                require(target.stat().st_size == row['target_bytes'] and sha256_file(target) == row['target_sha256'],
                        'Component round trip failed.')
                target.unlink()
        for name in names:
            shutil.copyfile(assets/name, stage/name)
        (stage/'CPK-VALIDATION.json').write_bytes((json.dumps(proof, indent=2)+'\n').encode())
        names.append('CPK-VALIDATION.json')
        (stage/'SHA256SUMS.txt').write_bytes(''.join(sha256_file(stage/name)+'  '+name+'\n' for name in names).encode())
        stage.rename(output)
    print('Verified component release prepared. Nothing published.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    require(args.build.count('.') == 2 and all(p.isdigit() for p in args.build.split('.'))
            and args.build.startswith('0.'), 'Expected version 0.x.y.')
    package(args.build, args.output, args.write)

if __name__ == '__main__':
    main()
