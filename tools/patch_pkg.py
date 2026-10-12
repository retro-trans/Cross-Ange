"""Original Cross Ange PKG + matching license -> verified English Vita3K PKG.

No installed game is needed. Default previews; --write creates a new local PKG.
Every operation uses isolated temporary folders. Nothing is published or installed
into the user's Vita3K. Requires cryptography and the ignored upstream dependencies
described in docs/pkg-patching.md. Output is for Vita3K, not a Sony-signed package.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from decrypt_game import CONTENT_ID, load_license
from pkg_probe import sfo_fields
from vita_pkg_repack import (ROOT, constants, make_pfs, read_pkg, require,
                             sha256, small_member, write_pkg)

ORIGINAL = dict(bytes=925548400, sha256='962498429645bf92d0171280b075629ff6dc8100f365ce43805d2cd3e897ebcb')
COMPONENTS = {
    'cpk/Ange.cpk': dict(bytes=882846536, sha256='e04d94fac7ba1bc21acfd98c9ea8352995e32229c642485fb2537cd0d53213de'),
    'sce_sys/param.sfo': dict(bytes=1328, sha256='04924d2566147471c89464d568c8ae8708b43cc296b370c6b8f208317cebf603'),
}
RUNTIME = ROOT / 'tools/pkg_vendor/vita3k-20261010'


def regular(path):
    path = Path(path).absolute()
    for item in (path,) + tuple(path.parents):
        if os.path.lexists(item):
            require(not item.is_symlink() and not (getattr(item.lstat(), 'st_file_attributes', 0) & 0x400),
                    'Use ordinary paths, not symlinks or junctions')
    return path.resolve()


def check_file(path, identity):
    require(path.is_file() and path.stat().st_size == identity['bytes'] and sha256(path) == identity['sha256'],
            'File identity mismatch: ' + path.name)


def isolated_runtime(source, destination):
    require((source/'Vita3K.exe').is_file(), 'Official local Vita3K runtime is missing')
    destination.mkdir()
    for file in source.iterdir():
        if file.is_file() and file.suffix.lower() in ('.exe', '.dll'):
            shutil.copyfile(file, destination/file.name)
    for name in ('data', 'icons', 'plugins', 'shaders-builtin', 'translations'):
        if (source/name).is_dir():
            shutil.copytree(source/name, destination/name)
    portable = destination/'portable'
    portable.mkdir()
    fs = portable/'fs'
    fs.mkdir()
    (portable/'config.yml').write_text('pref-path: '+json.dumps(str(fs))+
        '\ncheck-for-updates: false\ncheck-for-updates-mode: 0\nlog-level: 6\n', encoding='utf-8')
    env = os.environ.copy()
    for name in ('APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP'):
        path = portable/name.lower()
        path.mkdir()
        env[name] = str(path)
    for name in ('QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
        env.pop(name, None)
    return destination/'Vita3K.exe', fs, env


def install(exe, package, encoded_license, env):
    # Native PFS diagnostics can contain derived keys. Discard all native output.
    # Vita3K's CLI takes the license in transient local argv; never log argv.
    process = subprocess.run([str(exe), '--pkg', str(package), '--zrif', encoded_license],
                             cwd=str(exe.parent), env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=1800)
    require(process.returncode == 0, 'Vita3K package conversion failed; no output was published')
    return exe.parent/'portable/fs/ux0/app/PCSG00597'


def read_patch_directory(folder):
    manifest = json.loads((folder/'BUILD-MANIFEST.json').read_text(encoding='utf-8'))
    require(manifest.get('game_id') == 'cross-ange' and re.fullmatch(r'0\.\d+\.\d+', manifest.get('version','')),
            'Expected a versioned Cross Ange release manifest')
    require(len(manifest.get('patches',[])) == 2, 'Expected the two Cross Ange patch components')
    return manifest


def apply_release(source, folder, xdelta, output):
    manifest = read_patch_directory(folder)
    output.mkdir()
    targets = {}
    for row in manifest['patches']:
        matches = [name for name in COMPONENTS if row.get('edition') == 'Japan PCSG00597 / '+name]
        require(len(matches) == 1, 'Unsupported Cross Ange patch component')
        name = matches[0]
        require(row.get('language') == 'en' and row.get('source_version') == 'original', 'Unsupported translation route')
        original_identity = dict(bytes=row['source_bytes'],sha256=row['source_sha256'])
        require(original_identity == COMPONENTS[name], 'Patch source differs from original game')
        patch = dict(name=row['patch'],bytes=row['patch_bytes'],sha256=row['patch_sha256'])
        require(Path(patch['name']).name == patch['name'] and '\\' not in patch['name'], 'Unsafe patch filename')
        check_file(folder/patch['name'], patch)
        destination = output/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        delta_env = os.environ.copy()
        delta_env.pop('XDELTA', None)
        result = subprocess.run([str(xdelta), '-d', '-D', '-R', '-s', str(source/name), str(folder/patch['name']), str(destination)],
                                env=delta_env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=600)
        require(result.returncode == 0, 'Applying the translation delta failed')
        check_file(destination, dict(bytes=row['target_bytes'],sha256=row['target_sha256']))
        targets[name] = destination
    require(set(targets) == set(COMPONENTS), 'Missing Cross Ange component')
    extras = folder/('Cross-Ange-English-'+manifest['version']+'-extras.zip')
    checksum_rows = (folder/'EXTRAS-SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
    expected_sha = next((line.split()[0] for line in checksum_rows if line.split()[-1] == extras.name), None)
    require(expected_sha and sha256(extras) == expected_sha, 'Extras archive checksum mismatch')
    wanted = {'sce_sys/manual/025.png','sce_sys/font-license.txt'}
    with zipfile.ZipFile(extras) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and set(names) == wanted | {'INSTALL.md','EXTRAS-MANIFEST.json'},
                'Unexpected extras archive inventory')
        require(sum(info.file_size for info in archive.infolist()) < 4*1024*1024, 'Oversized extras archive')
        extra_manifest = json.loads(archive.read('EXTRAS-MANIFEST.json'))
        require(extra_manifest.get('version') == manifest['version'] and extra_manifest.get('title_id') == 'PCSG00597',
                'Extras identity mismatch')
        declared = {row['path']:row for row in extra_manifest['files']}
        for name in wanted:
            data = archive.read(name)
            destination = output/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            check_file(destination, declared[name])
            targets[name] = destination
    return manifest['version'], targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--license', type=Path, required=True, help='Matching local NoNpDrm work.bin or .rif')
    parser.add_argument('--output', type=Path, required=True, help='NEW .pkg path')
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--build', help='Developer: existing local 0.x.y build')
    choice.add_argument('--patch-directory', type=Path, help='Player: locally downloaded release assets')
    parser.add_argument('--xdelta', type=Path, help='Required with --patch-directory')
    parser.add_argument('--runtime', type=Path, default=RUNTIME, help='Official Vita3K tool distribution, copied into isolation')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    package, license_path, output = regular(args.package), regular(args.license), regular(args.output)
    require(not output.exists() and not output.with_suffix('.validation.json').exists(), 'Preserve existing output')
    require(output.suffix.lower() == '.pkg' and output.parent.is_dir(), 'Choose a new .pkg in an existing folder')
    require(package != output and license_path != output, 'Output cannot replace either input')
    check_file(package, ORIGINAL)
    license_bytes = license_path.read_bytes()
    require(len(license_bytes) == 512 and license_bytes[16:64].rstrip(b'\0').decode('ascii') == CONTENT_ID,
            'Select the matching Cross Ange 512-byte NoNpDrm license')
    require(structured_license(license_bytes), 'Use a NoNpDrm license, not an account-bound license')
    zrif = load_license(license_path)
    values = constants()
    parsed = read_pkg(package, values)
    template = small_member(package, parsed, 'sce_pfs/files.db')[:1024]
    targets = None
    if args.build:
        require(re.fullmatch(r'0\.\d+\.\d+', args.build), 'Invalid build version')
        build = ROOT/'work/output'/('cross-ange-'+args.build)
        manifest = json.loads((build/'manifest.json').read_text(encoding='utf-8'))
        require(manifest['version'] == args.build, 'Build version mismatch')
        targets = {p.relative_to(build/'game').as_posix():p for p in (build/'game').rglob('*') if p.is_file()}
        require(set(targets) == set(COMPONENTS) | {'sce_sys/manual/025.png','sce_sys/font-license.txt'}, 'Incomplete English build')
        version = args.build
    else:
        require(args.xdelta and regular(args.xdelta).is_file(), 'Provide the trusted local xdelta executable')
        version = read_patch_directory(regular(args.patch_directory))['version']
    print(json.dumps(dict(version=version,input='original PKG + matching local license',
                          output=str(output),target='Vita3K',sony_signed=False,write=args.write)), flush=True)
    if not args.write:
        return
    require(shutil.disk_usage(output.parent).free > 6*1024**3, 'At least 6 GB free space required')
    with tempfile.TemporaryDirectory(prefix='.cross-ange-pkg-', dir=str(output.parent)) as temporary:
        stage = Path(temporary)
        exe, fs, env = isolated_runtime(regular(args.runtime), stage/'runtime')
        print('Decrypting the original package locally...', flush=True)
        source = install(exe, package, zrif, env)
        for name, identity in COMPONENTS.items():
            check_file(source/name, identity)
        if targets is None:
            version, targets = apply_release(source, regular(args.patch_directory), regular(args.xdelta), stage/'english')
        files = {p.relative_to(source).as_posix():p for p in source.rglob('*') if p.is_file()}
        require(len(files) == 46, 'Unexpected decrypted original game inventory')
        files.update(targets)
        sfo = sfo_fields(targets['sce_sys/param.sfo'].read_bytes())
        require(sfo['TITLE_ID'] == 'PCSG00597' and sfo['CONTENT_ID'] == CONTENT_ID and sfo['CATEGORY'] == 'gd',
                'English metadata differs from the base game identity')
        print('Applying translation and rebuilding encrypted PFS...', flush=True)
        expected = make_pfs(files, template, license_bytes[0x50:0x60], stage/'pfs', values)
        payload = {p.relative_to(stage/'pfs').as_posix():p for p in (stage/'pfs').rglob('*') if p.is_file()}
        candidate = stage/output.name
        report = write_pkg(package, payload, candidate, values, targets['sce_sys/param.sfo'])
        print('Verifying installation of the rebuilt PKG in isolated Vita3K...', flush=True)
        installed = install(exe, candidate, zrif, env)
        actual = {p.relative_to(installed).as_posix():p for p in installed.rglob('*') if p.is_file()}
        require(set(actual) == set(expected), 'Installed PKG file inventory differs from English build')
        for name, identity in expected.items():
            check_file(actual[name], identity)
        check_file(package, ORIGINAL)
        require(license_path.read_bytes() == license_bytes, 'License changed during conversion')
        report.update(version=version,native_pkg_install_verified=True,verified_files=len(expected),
                      original_pkg_unchanged=True,license_unchanged=True,gameplay_tested=False)
        require(not output.exists(), 'Output appeared during conversion; preserve it')
        # Publication happens only after the native installer and all file hashes pass.
        candidate.rename(output)
        output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Verified translated PKG created: '+str(output), flush=True)


def structured_license(data):
    import struct
    return (struct.unpack_from('>HHH',data) == (1,1,1) and
            struct.unpack_from('<Q',data,8)[0] == 0x0123456789abcdef and any(data[0x50:0x60]))


if __name__ == '__main__':
    main()
