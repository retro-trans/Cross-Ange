"""Fetch the pinned user-requested font into ignored local build dependencies."""
import hashlib
import shutil
import subprocess
import urllib.request
from pathlib import Path

from build_english_font import FONT_FILE, FONT_SHA256, ROOT

URL = 'https://okoneya.jp/font/GenEiLatin-Separate_v2.1.zip'
ARCHIVE_SHA256 = '2e0bf6f454b10fd668fe420ef947b7e6a46284f728baa66501b7b6107ac68279'


def main():
    if FONT_FILE.exists():
        if hashlib.sha256(FONT_FILE.read_bytes()).hexdigest() != FONT_SHA256:
            raise ValueError('Preserve unexpected local font file; inspect it first')
        print('Pinned GenEi LateGo v2 font is already available.')
        return
    archive = ROOT / 'incoming/fonts/GenEiLatin-Separate_v2.1.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('Font download hash mismatch')
    # The author's ZIP uses Deflate64, unsupported by Python's zipfile module.
    seven = shutil.which('7z') or str(Path('C:/Program Files/7-Zip/7z.exe'))
    if not Path(seven).is_file():
        raise ValueError('7-Zip is required to extract the font archive')
    destination = ROOT / 'tools/fonts/genei-latin'
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run([seven, 'x', str(archive), '-o' + str(destination), '-y',
                    'GenEiLatin-Separate_v2.1/GenEiLateGoN_v2.ttf',
                    'GenEiLatin-Separate_v2.1/LICENSE.txt'], check=True,
                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if hashlib.sha256(FONT_FILE.read_bytes()).hexdigest() != FONT_SHA256:
        raise ValueError('Extracted font hash mismatch')
    print('Pinned GenEi LateGo v2 font is ready.')


if __name__ == '__main__':
    main()
