"""Preview installation into an existing Vita3K; --write installs a fresh game.

Preserves the original decrypted app and test build. License bytes stay local.
Firmware/fonts must already be installed. Existing app directories are refused.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from extract_sfo import read_sfo

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'PCSG00597'
CONTENT = 'JP0700-PCSG00597_00-CROSSANGEGAME000'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vita3k', type=Path, required=True)
    parser.add_argument('--build', default='0.1.4')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--update', action='store_true', help='Back up an existing app before replacing it with the selected build')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.[0-9]+\.[0-9]+', args.build):
        raise ValueError('Invalid build version')
    vendor = args.vita3k.resolve()
    exe = vendor / 'Vita3K.exe'
    config = vendor / 'config.yml'
    if not exe.is_file() or not config.is_file():
        raise ValueError('Existing Vita3K executable and configuration required')
    old_config = config.read_text(encoding='utf-8-sig')
    portable = vendor / 'portable'
    if portable.is_dir():
        fs = portable / 'fs'
        config = portable / 'config.yml'
        old_config = config.read_text(encoding='utf-8-sig')
    else:
        match = re.search(r'^pref-path:\s*(.*?)\s*$', old_config, re.M)
        if not match or not match.group(1).strip('"\''):
            raise ValueError('Inspect the active Vita3K data path first')
        fs = Path(match.group(1).strip('"\'')).resolve()
    fonts = sorted((fs / 'sa0/data/font/pvf').glob('*.pvf'))
    modules = sorted((fs / 'vs0/sys/external').glob('*.suprx'))
    if not fonts or not modules:
        raise ValueError('Install firmware and fonts before installing the game')
    source = ROOT / 'work/source/decrypted'
    build = ROOT / 'work/output' / ('cross-ange-' + args.build)
    manifest = json.loads((build / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['version'] != args.build:
        raise ValueError('Build version mismatch')
    metadata = read_sfo(source / 'sce_sys/param.sfo')['metadata']
    if metadata['TITLE_ID'] != TITLE or metadata['CONTENT_ID'] != CONTENT:
        raise ValueError('Game metadata mismatch')
    license_source = ROOT / 'tools/pkg_vendor/vita3k-20261010/portable/fs/ux0/license' / TITLE / (CONTENT + '.rif')
    rif = license_source.read_bytes()
    if len(rif) not in (512, 1024) or rif[16:64].rstrip(b'\0').decode('ascii') != CONTENT:
        raise ValueError('Matching local license required')
    target = fs / 'ux0/app' / TITLE
    if target.exists() and not args.update:
        raise ValueError('Preserve existing app; inspect before updating: ' + str(target))
    with (build / 'game/cpk/Ange.cpk').open('rb') as stream:
        if stream.read(4) != b'CPK ':
            raise ValueError('Invalid test archive')
    # New app only; existing installed titles, saves and firmware stay untouched.
    originals = {p.relative_to(source): p for p in source.rglob('*') if p.is_file()}
    replacements = {p.relative_to(build / 'game'): p for p in (build / 'game').rglob('*') if p.is_file()}
    files = {**originals, **replacements}
    required = sum(p.stat().st_size for p in files.values())
    if shutil.disk_usage(fs).free < required + 256*1024*1024:
        raise ValueError('Insufficient free space for a new game installation')
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = ROOT / 'work/source/vita3k-install-backups' / stamp
    report = {'version': args.build, 'title_id': TITLE, 'executable': str(exe),
              'app_directory': str(target), 'firmware_modules': len(modules), 'font_files': len(fonts),
              'files_to_install': len(files), 'bytes_to_install': required,
              'changed_files': sorted(str(p) for p in replacements),
              'license': 'Matching local license copied without printing its contents',
              'configuration_backup': str(backup), 'original_game_preserved': str(source),
              'existing_app_will_be_backed_up': target.exists(),
              'runtime_tested': False, 'write': args.write}
    print(json.dumps(report, indent=2), flush=True)
    if not args.write:
        return
    running = subprocess.run(['powershell', '-NoProfile', '-Command',
                              "@(Get-Process Vita3K -ErrorAction SilentlyContinue).Count"],
                             capture_output=True, text=True, check=True,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if int(running.stdout.strip()) > 0:
        raise ValueError('Close Vita3K before installing')
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(config, backup / 'config.yml')
    license_target = fs / 'ux0/license' / TITLE / license_source.name
    if license_target.exists():
        shutil.copy2(license_target, backup / 'existing-license.rif')
    staging = fs / 'ux0' / ('.' + TITLE + '-install-' + stamp)
    staging.mkdir(parents=True, exist_ok=False)
    records = []
    for relative, path in sorted(files.items()):
        destination = staging / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        expected = digest(path)
        if digest(destination) != expected:
            raise ValueError('Installed file hash mismatch: ' + str(relative))
        records.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': expected})
    if len(list((staging / 'sce_sys/manual').glob('*.png'))) != 25:
        raise ValueError('Credits page missing from staged installation')
    license_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(license_source, license_target)
    if license_target.read_bytes() != rif:
        raise ValueError('Local license copy failed')
    # Same-volume atomic rename presents a fully verified app to the emulator.
    previous = fs / 'ux0' / ('.' + TITLE + '-before-' + args.build + '-' + stamp)
    # Validate absolute paths before moving either directory on Windows.
    boundary = (fs / 'ux0').resolve()
    for path in (staging, target, previous):
        if boundary not in path.resolve().parents:
            raise ValueError('App move would leave the intended Vita3K data directory')
    if target.exists():
        if previous.exists():
            raise ValueError('Preserve existing app backup')
        target.rename(previous)
        report['previous_app_backup'] = str(previous)
    try:
        staging.rename(target)
    except Exception:
        if previous.exists() and not target.exists():
            previous.rename(target)
        raise
    updated = re.sub(r'^show-live-area-screen:.*$', 'show-live-area-screen: true', old_config, flags=re.M)
    config.write_text(updated, encoding='utf-8')
    report['installed_files'] = records
    report['status'] = 'installed-and-hash-verified'
    report['manual_pages'] = 25
    record = build / 'vita3k-install.json'
    if record.exists():
        record = build / ('vita3k-install-' + stamp + '.json')
    record.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'installed': str(target),
                      'verified_files': len(records), 'record': str(record)}, indent=2))


if __name__ == '__main__':
    main()
