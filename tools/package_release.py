"""Preview or package an existing English build as a verified Retro Trans release.

Requires a local checkout of retro-trans/retro-trans-tools and Git. No game build
is generated, no license keys are read, and no GitHub publication happens here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'retro-trans/Cross-Ange'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def configuration(version, commit):
    original = ROOT/'work/source/decrypted'
    game = ROOT/'work/output'/('cross-ange-'+version)/'game'
    patches = []
    for relative, label in [('cpk/Ange.cpk','Ange'),('sce_sys/param.sfo','param')]:
        patches.append(dict(patch=f'Cross-Ange-English-{version}-{label}.xdelta',
                            edition='Japan PCSG00597 / '+relative,language='en',
                            source_version='original',source_format=Path(relative).suffix[1:],
                            target_format=Path(relative).suffix[1:],
                            source=str(original/relative),target=str(game/relative)))
    return dict(game_id='cross-ange',game_name='CROSS ANGE Rondo of Angel and Dragon tr.',
                platform='PS Vita',version=version,source_commit=commit,patches=patches,
                solutions=[dict(id='pcsg00597-english-components',
                                name='Cross Ange English components (PCSG00597)',
                                edition='Japan PCSG00597',language='en',
                                files=[dict(edition=p['edition'],output_name=Path(p['target']).name)
                                       for p in patches])])


def package(version, checkout, write=False):
    build = ROOT/'work/output'/('cross-ange-'+version)
    local = json.loads((build/'manifest.json').read_text(encoding='utf-8'))
    if local['version'] != version or not local['translation_drafts_inserted']:
        raise ValueError('Choose an existing English build')
    if not local['checks']['original_payload_bytes_preserved']:
        raise ValueError('Build preservation checks are missing')
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    config = configuration(version,commit)
    output = ROOT/'work/output/releases'/('v'+version)
    print(json.dumps(dict(version=version,source_commit=commit,output=str(output),
                          components=[dict(patch=p['patch'],source=p['source'],target=p['target'])
                                      for p in config['patches']],
                          extras=['sce_sys/manual/025.png','sce_sys/font-license.txt'],
                          includes_full_game_files=False,write=write),indent=2),flush=True)
    if not write:
        return
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
        raise ValueError('Commit the reviewed public sources before packaging')
    if not (checkout/'retro_trans/release.py').is_file():
        raise ValueError('Supply the Retro Trans Tools checkout')
    sys.path.insert(0,str(checkout.resolve()))
    from retro_trans.release import build_release,validate_directory
    private = ROOT/'work/source/release-packaging'/('v'+version)
    private.mkdir(parents=True,exist_ok=True)
    config_path = private/'release-local.json'
    config_path.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    manifest = build_release(config_path,output,cache=private/'engine-cache')
    extras = {relative:(build/'game'/relative).read_bytes()
              for relative in ['sce_sys/manual/025.png','sce_sys/font-license.txt']}
    extras['INSTALL.md'] = (ROOT/'docs/patch-installation.md').read_bytes()
    extras['EXTRAS-MANIFEST.json'] = (json.dumps(dict(version=version,title_id='PCSG00597',
        files=[dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
               for name,raw in extras.items()]),indent=2)+'\n').encode('utf-8')
    archive = output/f'Cross-Ange-English-{version}-extras.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as bundle:
        for name,raw in extras.items():
            entry = zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry,raw)
    with zipfile.ZipFile(archive) as bundle:
        if set(bundle.namelist()) != set(extras) or any(bundle.read(name)!=raw for name,raw in extras.items()):
            raise ValueError('Extras ZIP readback failed')
    (output/'EXTRAS-SHA256SUMS.txt').write_text(digest(archive)+'  '+archive.name+'\n',encoding='utf-8')
    # The application owns the PKG encryption code. This ZIP carries only a
    # declarative profile, verified translation deltas and generated extras.
    from retro_trans.vita_translation import validate,archive_description,SCHEMA
    original_pkg = dict(bytes=925548400,sha256='962498429645bf92d0171280b075629ff6dc8100f365ce43805d2cd3e897ebcb')
    source_files = []
    original = ROOT/'work/source/decrypted'
    for path in sorted(original.rglob('*')):
        if path.is_file():
            source_files.append(dict(path=path.relative_to(original).as_posix(),bytes=path.stat().st_size,sha256=digest(path)))
    profile = dict(schema=SCHEMA,name='Cross Ange English '+version,build=version,title_id='PCSG00597',
        content_id='JP0700-PCSG00597_00-CROSSANGEGAME000',target='Vita3K',minimum_app_version='0.5.8',
        package=original_pkg,engine='pfs-v5-pkg-key2',source_files=source_files,files=[],extras=[])
    for row in manifest['patches']:
        profile['files'].append(dict(path=row['edition'].split(' / ',1)[1],
            source=dict(bytes=row['source_bytes'],sha256=row['source_sha256']),
            target=dict(bytes=row['target_bytes'],sha256=row['target_sha256']),
            patch=dict(name=row['patch'],bytes=row['patch_bytes'],sha256=row['patch_sha256'])))
    for relative,name in [('sce_sys/manual/025.png','credits.png'),('sce_sys/font-license.txt','font-license.txt')]:
        raw = extras[relative]
        profile['extras'].append(dict(path=relative,name=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    validate(profile)
    profile_file = output/'VITA-PKG.json'
    profile_file.write_text(json.dumps(profile,indent=2)+'\n',encoding='utf-8')
    vita_zip = output/f'Cross-Ange-English-{version}-Vita-PKG-patches.zip'
    inventory = {'VITA-PKG.json':profile_file.read_bytes()}
    inventory.update({row['patch']['name']:(output/row['patch']['name']).read_bytes() for row in profile['files']})
    inventory.update({row['name']:extras[row['path']] for row in profile['extras']})
    with zipfile.ZipFile(vita_zip,'x',compression=zipfile.ZIP_DEFLATED) as bundle:
        for name,raw in inventory.items():
            entry = zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry,raw)
    with archive_description(vita_zip) as (checked,temporary):
        if checked != profile:
            raise ValueError('Vita PKG profile readback mismatch')
    (output/'VITA-PKG-SHA256SUMS.txt').write_text(''.join(digest(path)+'  '+path.name+'\n'
        for path in (profile_file,vita_zip)),encoding='utf-8')
    validate_directory(output)
    print(json.dumps(dict(status='verified-release-package',version=version,
                          patch_roundtrips=len(manifest['patches']),extras_zip_verified=True,
                          output=str(output)),indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',required=True)
    parser.add_argument('--retro-trans-tools',type=Path,default=ROOT.parent/'retro-trans-tools')
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    package(args.build,args.retro_trans_tools,args.write)
