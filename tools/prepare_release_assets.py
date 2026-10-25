"""Package an existing native-verified build; never publish or bundle game inputs."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / 'retro-trans-tools'))
from retro_trans import vita_translation as vita
from retro_trans.catalog import validate_manifest
from retro_trans.core import decode, engine_context, sha256_file
from retro_trans.release import validate_directory
from retro_trans.vita_repatch import require, verify


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def prepare(version, write=False):
    require(re.fullmatch(r'0\.\d+\.\d+', version), 'Expected an existing 0.x.y build.')
    build = ROOT / 'work/output' / ('cross-ange-' + version)
    local = build / 'local-patches'
    output = ROOT / 'work/output/releases' / ('v' + version)
    require(not output.exists(), 'Preserve existing release assets.')
    profile = vita.validate(json.loads((local / 'VITA-PKG.json').read_text(encoding='utf-8')))
    native = json.loads((ROOT / 'docs' / ('local-build-' + version + '-validation.json')).read_text(encoding='utf-8'))
    require(profile['build'] == native['version'] == version and native['native_pkg_install_verified']
            and native['verified_files'] == 48 and native['original_pkg_unchanged']
            and native['license_unchanged'], 'Missing verified build provenance.')
    verify(build / ('Cross-Ange-English-' + version + '.pkg'), native)
    for row in profile['source_files']:
        verify(ROOT / 'work/source/decrypted' / row['path'], row)
    for row in profile['files']:
        verify(build / 'game' / row['path'], row['target'])
        verify(local / row['patch']['name'], row['patch'])
    for row in profile['extras']:
        verify(build / 'game' / row['path'], row)
    bundle_name = 'Cross-Ange-English-' + version + '-Vita-PKG-patches.zip'
    with vita.archive_description(local / bundle_name) as (description, _):
        require(description == profile, 'Local ZIP differs from its profile.')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    manifest = dict(schema_version=2, game_id='cross-ange',
                    game_name='CROSS ANGE Rondo of Angel and Dragon tr.', platform='PS Vita',
                    version=version, source_commit=commit, patches=[], solutions=[dict(
                        id='pcsg00597-english-components', name='Cross Ange English components (PCSG00597)',
                        edition='Japan PCSG00597', language='en', files=[
                            dict(edition='Japan PCSG00597 / ' + row['path'], output_name=Path(row['path']).name)
                            for row in profile['files']])])
    for row in profile['files']:
        fmt = 'cpk' if row['path'].endswith('.cpk') else 'sfo'
        entry = dict(patch=row['patch']['name'], edition='Japan PCSG00597 / ' + row['path'],
                     language='en', source_version='original', source_format=fmt, target_format=fmt)
        for prefix, identity in (('source', row['source']), ('target', row['target']), ('patch', row['patch'])):
            entry.update({prefix + '_' + key: identity[key] for key in ('bytes', 'sha256')})
        manifest['patches'].append(entry)
    validate_manifest(manifest)
    print(json.dumps(dict(version=version, source_commit=commit, output=str(output), write=write)), flush=True)
    if not write:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.prepare-release-', dir=output.parent) as temporary:
        stage = Path(temporary)
        for name in ['VITA-PKG.json', bundle_name] + [r['patch']['name'] for r in profile['files']]:
            shutil.copyfile(local / name, stage / name)
        write_json(stage / 'BUILD-MANIFEST.json', manifest)
        roundtrips = []
        with engine_context() as engine:
            for row in profile['files']:
                target = stage / 'roundtrip.part'
                decode(engine, ROOT / 'work/source/decrypted' / row['path'],
                       stage / row['patch']['name'], target, row['target']['bytes'])
                verify(target, row['target'])
                target.unlink()
                roundtrips.append(dict(patch=row['patch']['name'], roundtrip_verified=True,
                                       target_sha256=row['target']['sha256']))
        write_json(stage / 'VALIDATION.json', dict(schema_version=1, version=version,
                   manifest_sha256=sha256_file(stage / 'BUILD-MANIFEST.json'), patches=roundtrips))
        extra_manifest = dict(schema_version=1, version=version, title_id=profile['title_id'],
                             files=[{k: r[k] for k in ('path', 'bytes', 'sha256')} for r in profile['extras']])
        extra_name = 'Cross-Ange-English-' + version + '-extras.zip'
        with zipfile.ZipFile(stage / extra_name, 'x', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('INSTALL.md', 'Close the game and back up its installed files.\n'
                             'Copy sce_sys/manual/025.png and sce_sys/font-license.txt into the\n'
                             'corresponding folders of your patched PCSG00597 installation.\n'
                             'These provide translation credits and required font attribution.\n')
            archive.writestr('EXTRAS-MANIFEST.json', json.dumps(extra_manifest, indent=2) + '\n')
            for row in profile['extras']:
                archive.write(build / 'game' / row['path'], row['path'])
        (stage / 'EXTRAS-SHA256SUMS.txt').write_text(
            sha256_file(stage / extra_name) + '  ' + extra_name + '\n', encoding='ascii')
        write_json(stage / 'CPK-VALIDATION.json', dict(schema_version=1, version=version,
                   verified_at=datetime.now(timezone.utc).isoformat(), component_roundtrips_verified=2,
                   route='installed components through Retro Trans xdelta engine',
                   source_ui_worker_tested=False, original_files_unchanged=True,
                   credits_and_font_attribution_match_game_build=True, license_read_during_cpk_patching=False,
                   gameplay_tested=False, physical_vita_tested=False))
        proof = dict(native, original_package_sha256=profile['package']['sha256'],
                     frozen_app_local_patch_verified=True, public_automatic_download_verified=False)
        write_json(stage / 'PKG-REBUILD-VALIDATION.json', proof)
        write_json(ROOT / 'docs' / ('pkg-patching-validation-' + version + '.json'), proof)
        pkg_names = ['VITA-PKG.json', bundle_name, 'PKG-REBUILD-VALIDATION.json']
        (stage / 'VITA-PKG-SHA256SUMS.txt').write_text(''.join(
            sha256_file(stage / name) + '  ' + name + '\n' for name in pkg_names), encoding='ascii')
        (stage / 'SHA256SUMS.txt').write_text(''.join(
            sha256_file(p) + '  ' + p.name + '\n' for p in sorted(stage.iterdir())), encoding='ascii')
        validate_directory(stage)
        stage.rename(output)
    print('Verified small release assets prepared; nothing published.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    prepare(args.build, args.write)
