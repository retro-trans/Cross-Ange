"""Read back installed archive replacements and validate native fonts and UI labels."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from cpk_extract import table
from bnf_codec import decode_record
from build_translation_text import FONT_RANGES
from additional_text_extract import string_at

ROOT = Path(__file__).resolve().parents[1]


def verify(version):
    folder = ROOT / 'work/output' / ('cross-ange-' + version)
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    install = json.loads((folder/'vita3k-install.json').read_text(encoding='utf-8'))
    if manifest['version'] != version or install['version'] != version:
        raise ValueError('Build and installation versions disagree')
    app = Path(install['app_directory'])
    glyphs = 0
    compact = 0
    with (app/'cpk/Ange.cpk').open('rb') as archive:
        header = table(archive,0)[0]
        rows = table(archive,header['TocOffset'])
        base = min(header['ContentOffset'],header['TocOffset'])
        for item in manifest['archive_replacements']:
            row = rows[item['row']]
            path = row['DirName'] + '/' + row['FileName']
            if path != item['path'] or row['FileSize'] != item['size']:
                raise ValueError('Installed member identity/size mismatch: '+item['path'])
            archive.seek(base+row['FileOffset'])
            raw = archive.read(row['FileSize'])
            if hashlib.sha256(raw).hexdigest() != item['sha256'] or raw != (folder/'archive-members'/path).read_bytes():
                raise ValueError('Installed member bytes mismatch: '+path)
            if path in manifest['translation']['font_members']:
                count = sum(b-a+1 for a,b in FONT_RANGES)
                offsets = list(struct.unpack_from('<'+str(count)+'I',raw,40))+[len(raw)]
                for a,b in zip(offsets,offsets[1:]):
                    if len(decode_record(raw[a:b])) != 338:
                        raise ValueError('Invalid native glyph: '+path)
                    glyphs += 1
            if path == 'data/_dat/strings.bnd':
                for entry in manifest['translation']['ui_layout']['entries']:
                    pointer = struct.unpack_from('<I',raw,20+entry['id']*8+entry['column']*4)[0]
                    if string_at(raw,pointer)[0] != entry['display_en']:
                        raise ValueError('Installed compact UI label mismatch: '+entry['key'])
                    compact += 1
    if (app/'sce_sys/font-license.txt').read_bytes() != (folder/'game/sce_sys/font-license.txt').read_bytes():
        raise ValueError('Installed font license mismatch')
    return dict(version=version,independent_installed_archive_readback=True,
                replacement_members_verified=len(manifest['archive_replacements']),
                font_records_native_validated=glyphs,font_license_verified=True,
                compact_ui_fields_verified=compact,
                tutorial_textures_verified=manifest['translation']['tutorials']['textures_inserted'],
                tutorial_text_rectangles=manifest['translation']['tutorials']['raster_regions_inserted'],
                runtime_tested=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',required=True)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    result = verify(args.build)
    if args.write:
        (ROOT/'work/output'/('cross-ange-'+args.build)/'installed-readback.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
