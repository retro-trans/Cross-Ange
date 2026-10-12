"""Reversible original/English archive comparison; preview unless --write.

Only the already installed Cross Ange archive changes. The installed executable,
save data, license, emulator configuration and immutable builds stay untouched.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from install_vita3k import ROOT, TITLE, digest

ORIGINAL_SHA256 = 'e04d94fac7ba1bc21acfd98c9ea8352995e32229c642485fb2537cd0d53213de'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('original', 'english'), required=True)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--launch', action='store_true', help='Open Vita3K after a verified switch')
    args = parser.parse_args()
    if args.launch and not args.write:
        raise ValueError('--launch requires --write')
    version = (ROOT / 'VERSION').read_text().strip()
    folder = ROOT / 'work/output' / ('cross-ange-' + version)
    install = json.loads((folder / 'vita3k-install.json').read_text(encoding='utf-8'))
    if install['version'] != version or install['title_id'] != TITLE:
        raise ValueError('Installed build identity mismatch')
    app = Path(install['app_directory']).resolve()
    if app.name != TITLE or app.parent.name != 'app' or app.parent.parent.name != 'ux0':
        raise ValueError('Unexpected installed app boundary')
    target = (app / 'cpk/Ange.cpk').resolve()
    if app not in target.parents:
        raise ValueError('Archive leaves installed app boundary')
    english = folder / 'game/cpk/Ange.cpk'
    original = ROOT / 'work/source/decrypted/cpk/Ange.cpk'
    expected_english = next(r['sha256'] for r in install['installed_files'] if r['path'] == 'cpk/Ange.cpk')
    if digest(english) != expected_english:
        raise ValueError('Immutable English build differs from verified installation')
    expected_original = digest(original)
    if expected_original != ORIGINAL_SHA256:
        raise ValueError('Original Cross Ange archive hash mismatch')
    for path in (original, english, target):
        with path.open('rb') as stream:
            if stream.read(4) != b'CPK ':
                raise ValueError('Not a CPK archive: ' + str(path))
    current = digest(target)
    if current not in (expected_original, expected_english):
        raise ValueError('Installed archive contains unknown changes; preserve and inspect them first')
    source, expected = (original, expected_original) if args.mode == 'original' else (english, expected_english)
    report = {'version': version, 'mode': args.mode, 'archive': str(target),
              'original_sha256': expected_original, 'english_sha256': expected_english,
              'saves_and_license_untouched': True, 'write': args.write,
              'changes_needed': current != expected}
    print(json.dumps(report, indent=2), flush=True)
    if not args.write:
        return
    running = subprocess.run(['powershell', '-NoProfile', '-Command',
                              '@(Get-Process Vita3K -ErrorAction SilentlyContinue).Count'],
                             capture_output=True, text=True, check=True,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if int(running.stdout.strip()):
        raise ValueError('Close Vita3K before switching the diagnostic archive')
    if current != expected:
        staging = target.with_name('Ange.portrait-comparison-staging.cpk')
        if staging.exists():
            raise ValueError('Preserve existing diagnostic staging file: ' + str(staging))
        shutil.copy2(source, staging)
        if digest(staging) != expected:
            raise ValueError('Diagnostic staging hash mismatch')
        os.replace(staging, target)
        if digest(target) != expected:
            raise ValueError('Diagnostic installed hash mismatch')
    state = ROOT / 'work/source/portrait-comparison/state.json'
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Original game archive selected.' if args.mode == 'original' else 'English build restored.', flush=True)
    if args.launch:
        subprocess.Popen([install['executable'], '-r', TITLE], cwd=str(Path(install['executable']).parent))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Comparison stopped: ' + str(error), file=sys.stderr)
        sys.exit(1)
