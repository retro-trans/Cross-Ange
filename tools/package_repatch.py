"""Generate a hardware rePatch delta bundle from the existing English build.

Preview by default. No licenses, original game files or executable are bundled.
"""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package(version,checkout,output=None,write=False):
    sys.path.insert(0,str(checkout.resolve()))
    from retro_trans import vita_repatch as v
    from retro_trans.core import decode,engine_context,sha256_file
    from retro_trans.vita_repatch import require,verify,no_links
    # This is a distribution variant of a previously verified build.
    native = json.loads((ROOT/'docs'/('pkg-patching-validation-'+version+'.json')).read_text(encoding='utf-8'))
    require(native['version'] == version and native['native_pkg_install_verified'], 'Native build verification is required.')
    build = ROOT/'work/output'/('cross-ange-'+version)/'game'
    old = ROOT/'work/output/releases'/('v'+version)
    metadata = json.loads((old/'BUILD-MANIFEST.json').read_text(encoding='utf-8'))
    row = next(r for r in metadata['patches'] if r['source_format'] == 'cpk')
    source = ROOT/'work/source/decrypted/cpk/Ange.cpk'
    target = build/'cpk/Ange.cpk'
    patch = old/row['patch']
    source_id = dict(bytes=row['source_bytes'],sha256=row['source_sha256'])
    target_id = dict(bytes=row['target_bytes'],sha256=row['target_sha256'])
    delta_id = dict(bytes=row['patch_bytes'],sha256=row['patch_sha256'])
    verify(source,source_id);verify(target,target_id);verify(patch,delta_id)
    def ident(path):
        return dict(bytes=path.stat().st_size,sha256=sha256_file(path))
    profile = v.validate(dict(schema=v.SCHEMA,title_id='PCSG00597',app_version='01.00',
        name='Cross Ange English '+version+' hardware rePatch',build=version,auth=None,minimum_app_version='0.5.14',
        package=dict(bytes=925548400,sha256=native['original_package_sha256'],
            content_id='JP0700-PCSG00597_00-CROSSANGEGAME000'),
        files=[dict(path='cpk/Ange.cpk',source=source_id,target=target_id,
            patch=dict(name='VITA-Cross-Ange-'+version+'-archive.xdelta',**delta_id))],
        extras=[dict(path=name,asset=dict(name=asset,**ident(build/name))) for name,asset in
            [('sce_sys/manual/025.png','VITA-credits-025.png'),('sce_sys/font-license.txt','VITA-font-license.txt')]]))
    output = no_links(output or ROOT/'work/output/releases'/('v'+version+'-repatch'))
    require(not output.exists(), 'Preserve the existing rePatch release folder.')
    print(json.dumps(dict(version=version,route='hardware rePatch',patch_bytes=delta_id['bytes'],
        executable_replaced=False,license_bundled=False,output=str(output),write=write),indent=2),flush=True)
    if not write: return
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='repatch-release-',dir=output.parent) as temp:
        stage = Path(temp)/'release';stage.mkdir()
        with engine_context(cache=ROOT/'work/source/release-packaging/engine-cache') as engine:
            candidate = Path(temp)/'Ange.cpk'
            decode(engine,source,patch,candidate,target_id['bytes'])
            verify(candidate,target_id)
        verify(source,source_id);verify(target,target_id)
        manifest = stage/v.MANIFEST
        manifest.write_bytes((json.dumps(profile,indent=2)+'\n').encode('utf-8'))
        archive = stage/('Cross-Ange-English-'+version+v.ZIP_SUFFIX)
        payloads = [(manifest,v.MANIFEST),(patch,profile['files'][0]['patch']['name'])]
        payloads += [(build/r['path'],r['asset']['name']) for r in profile['extras']]
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as bundle:
            for path,name in payloads:
                bundle.write(path,name)
        with v.archive_description(archive,profile): pass
        record = dict(version=version,route='hardware rePatch',minimum_app_version='0.5.14',
            zip=dict(name=archive.name,**ident(archive)),files={r['path']:r['target'] for r in profile['files']},
            extras={r['path']:r['asset'] for r in profile['extras']},native_game_build_verified=True,
            delta_roundtrip_verified=True,zip_inventory_verified=True,originals_unchanged=True,
            executable_replaced=False,license_included=False,full_archive_included=False,
            physical_vita_tested=False,manual_credits_on_hardware_verified=False)
        (stage/'REPATCH-VALIDATION.json').write_bytes((json.dumps(record,indent=2)+'\n').encode('utf-8'))
        (stage/'REPATCH-SHA256SUMS.txt').write_bytes(''.join(sha256_file(p)+'  '+p.name+'\n'
            for p in sorted(stage.iterdir())).encode('utf-8'))
        stage.rename(output)
    print('Verified rePatch package: '+str(output),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',required=True)
    parser.add_argument('--retro-trans-tools',type=Path,default=ROOT.parent/'retro-trans-tools')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    import re
    if not re.fullmatch(r'0\.\d+\.\d+',args.build): parser.error('Choose an existing 0.x.y build.')
    package(args.build,args.retro_trans_tools,args.output,args.write)
