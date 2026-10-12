"""Package an existing native-verified English PKG as a whole-PKG xdelta ZIP.

Never reads licenses or publishes to GitHub. The ZIP contains only its profile
and one delta. Preview by default; --write saves a new verified release folder.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'JP0700-PCSG00597_00-CROSSANGEGAME000'


def package(version, original, translated, checkout, delta=None, output=None, write=False):
    if not re.fullmatch(r'0\.\d+\.\d+', version):
        raise ValueError('Choose an existing 0.x.y English build.')
    sys.path.insert(0, str(checkout.resolve()))
    from retro_trans import vita_binary as v
    from retro_trans.core import decode, encode, engine_context, sha256_file
    from retro_trans.vita_downloads import package_content
    from retro_trans.vita_repatch import no_links, require, verify

    original, translated = no_links(original).resolve(), no_links(translated).resolve()
    output = no_links(output or ROOT/'work/output/releases'/('v'+version+'-whole-pkg'))
    require(not output.exists(), 'Preserve the existing release folder.')
    require(package_content(original) == package_content(translated) == CONTENT,
            'Both PKGs must belong to Cross Ange PCSG00597.')
    native = json.loads((ROOT/'docs'/('pkg-patching-validation-'+version+'.json')).read_text(encoding='utf-8'))
    require(native['version'] == version and native['native_pkg_install_verified'] is True and
            type(native['verified_files']) is int and native['verified_files'] > 0,
            'The translated game needs prior native installation verification.')

    def identity(path):
        return dict(bytes=path.stat().st_size, sha256=sha256_file(path))

    source_id, target_id = identity(original), identity(translated)
    require(source_id['sha256'] == native['original_package_sha256'] and
            target_id == {key:native[key] for key in ('bytes','sha256')},
            'PKG inputs differ from the native-verified game build.')
    print(json.dumps(dict(version=version, route='whole-PKG xdelta', license_used=False,
        source=source_id, target=target_id, output=str(output), write=write), indent=2), flush=True)
    if not write:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='whole-pkg-release-', dir=output.parent) as temporary:
        root = Path(temporary)
        stage = root/'release'
        stage.mkdir()
        delta_name = 'Cross-Ange-English-'+version+'-PKG.xdelta'
        with engine_context(cache=ROOT/'work/source/release-packaging/engine-cache') as engine:
            if delta:
                patch = no_links(delta).resolve()
                require(patch != original and patch != translated, 'Choose the existing whole-PKG delta.')
            else:
                patch = root/delta_name
                encode(engine, original, translated, patch)
            delta_id = identity(patch)
            profile = v.validate(dict(schema=v.SCHEMA, name='Cross Ange English '+version,
                build=version, title_id='PCSG00597', content_id=CONTENT, target='Vita3K',
                minimum_app_version='0.5.12', package=source_id, output=target_id,
                patch=dict(name=delta_name, **delta_id)))
            candidate = root/'roundtrip.pkg'
            decode(engine, original, patch, candidate, target_id['bytes'])
            verify(candidate, target_id)
        verify(original, source_id)
        verify(translated, target_id)
        manifest = stage/v.MANIFEST
        manifest.write_text(json.dumps(profile, indent=2)+'\n', encoding='utf-8')
        archive = stage/('Cross-Ange-English-'+version+v.ZIP_SUFFIX)
        with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_STORED) as bundle:
            for path, name in ((manifest,v.MANIFEST),(patch,delta_name)):
                entry = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
                entry.external_attr = 0o100644 << 16
                with path.open('rb') as source, bundle.open(entry,'w',force_zip64=True) as destination:
                    shutil.copyfileobj(source,destination,1024*1024)
        with v.archive_description(archive) as (checked, _):
            require(checked == profile, 'Whole-PKG ZIP readback mismatch.')
        validation = dict(schema_version=1, version=version, route='whole-PKG xdelta',
            package=source_id, output=target_id, patch=dict(name=delta_name,**delta_id),
            patch_zip=dict(name=archive.name,**identity(archive)),
            delta_roundtrip_verified=True, zip_profile_inventory_verified=True,
            original_pkg_unchanged=True, translated_pkg_unchanged=True, license_used_for_patching=False,
            minimum_app_version='0.5.12', native_pkg_install_verified=True,
            verified_installed_files=native['verified_files'], native_runtime=native['native_runtime'],
            native_proof='docs/pkg-patching-validation-'+version+'.json',
            sony_signed=False, gameplay_tested=False, physical_vita_tested=False,
            includes_full_pkg_file=False, includes_license=False)
        (stage/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
        checksums = ''.join(sha256_file(path)+'  '+path.name+'\n' for path in sorted(stage.iterdir()))
        (stage/'SHA256SUMS.txt').write_text(checksums,encoding='utf-8')
        require(not output.exists(), 'Release output appeared during packaging.')
        stage.rename(output)
    print('Verified whole-PKG release package: '+str(output),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True)
    parser.add_argument('--package', type=Path, required=True, help='Original Japanese PKG')
    parser.add_argument('--translated-pkg', type=Path, required=True, help='Previously native-verified English PKG')
    parser.add_argument('--delta', type=Path, help='Reuse an existing whole-PKG delta after a complete decode/hash check')
    parser.add_argument('--output', type=Path, help='New release asset directory')
    parser.add_argument('--retro-trans-tools', type=Path, default=ROOT.parent/'retro-trans-tools')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    package(args.build,args.package,args.translated_pkg,args.retro_trans_tools,args.delta,args.output,args.write)
