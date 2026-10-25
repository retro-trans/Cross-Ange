"""Exercise the built fork's real shader translator against local native inputs.

Requires a separate test executable below work/output and an empty portable
data directory. No user emulator, game, save, license or cached shader is edited.
Native inputs and generated GLSL/logs remain in ignored local working folders.
"""
import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess

from vita3k_hud_shader_probe import ROOT, EMU, PROBE, candidate, sha


def main():
    if os.name == 'nt':
        # A missing test-build DLL must fail the child, not open a modal dialog.
        ctypes.windll.kernel32.SetErrorMode(0x8003)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--expect-upstream', action='store_true',
                        help='Check that the official baseline reproduces extra scaling')
    args = parser.parse_args()
    executable = args.exe.resolve(strict=True)
    if not executable.is_relative_to((ROOT / 'work/output').resolve()):
        raise ValueError('Use the separate test executable in work/output')
    portable = executable.parent / 'portable'
    if portable.exists() and any(portable.rglob('*')):
        raise ValueError('The test portable directory must be empty')
    portable.mkdir(exist_ok=True)
    stage = PROBE / ('fork-validation-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    stage.mkdir(parents=True, exist_ok=False)
    validator = PROBE / 'vendor/glslang-16.6.0/bin/glslang.exe'
    inventory = json.loads((ROOT / 'docs/vita3k-hud-shader-candidate.json').read_text(encoding='utf-8'))
    version = subprocess.run([str(executable), '--version'], cwd=executable.parent,
                             capture_output=True, timeout=30, check=True)
    (stage / 'version.txt').write_bytes(version.stdout + version.stderr)
    records = []
    for row in inventory['shader_records']:
        native_path = EMU / 'shaderlog/PCSG00597/eboot.bin' / (Path(row['cache_file']).stem + '.gxp')
        native = native_path.read_bytes()
        if sha(native) != row['shader']:
            raise ValueError('Native program identity mismatch')
        result = subprocess.run([str(executable), '--recompile-shader', str(native_path)],
                                cwd=executable.parent, capture_output=True, timeout=60, check=True)
        output = result.stdout + result.stderr
        log_path = portable / 'vita3k.log'
        if b'Generated GLSL:' not in output and log_path.is_file():
            output = log_path.read_bytes()
        (stage / (row['shader'] + '.log')).write_bytes(output)
        text = output.decode('utf-8', errors='replace')
        marker = text.find('Generated GLSL:')
        start = text.find('#version', marker) if marker >= 0 else -1
        end = text.rfind('}')
        if start < 0 or end < start:
            raise ValueError('The built emulator did not emit GLSL')
        source = text[start:end + 1] + '\n'
        if args.expect_upstream:
            revised = candidate(source, native)
            if revised is None:
                raise ValueError('Official baseline no longer has the reviewed extra scaling')
            _, proof = revised
        else:
            if re.search(r'idx\[\d\]\s*\*\s*2', source):
                raise ValueError('The built translator still doubles the index')
            # Feed actual emitted scalar offsets into the independently parsed
            # native-array reference checks used by the cache experiment.
            reads = list(re.finditer(r'\bidx\[(\d)\] \+ (\d+)', source))
            if len(reads) != 2:
                raise ValueError('Unexpected generated indexed-read shape')
            old_form = re.sub(r'\bidx\[(\d)\] \+ (\d+)',
                              lambda m: '(idx[' + m[1] + '] * 2) + ' + m[2], source)
            corrected, proof = candidate(old_form, native)
            if corrected != source:
                raise ValueError('Generated scalar reads disagree with the reference')
        glsl = stage / (row['shader'] + '.vert')
        glsl.write_text(source, encoding='utf-8')
        check = subprocess.run([str(validator), '-S', 'vert', str(glsl)],
                               capture_output=True, timeout=30)
        (stage / (row['shader'] + '.glslang.log')).write_bytes(check.stdout + check.stderr)
        if check.returncode:
            raise ValueError('Generated GLSL failed independent compilation')
        records.append(dict(shader=row['shader'], native_sha256=sha(native),
                            generated_glsl_sha256=sha(source.encode()),
                            emitted_scalar_reference_mismatches=(proof['incorrect_original_cases']
                                                                 if args.expect_upstream else 0),
                            glslang_compile=True, **proof))
    if len(records) != 12 or sum(r['native_scalar_reference_cases'] for r in records) != 256:
        raise ValueError('Incomplete native reference inventory')
    report = dict(status=('official_upstream_extra_scaling_reproduced' if args.expect_upstream
                          else 'built_translator_reference_checks_passed'),
                  checked_at=datetime.now(timezone.utc).isoformat(),
                  executable=str(executable), executable_sha256=sha(executable.read_bytes()),
                  version=version.stdout.decode('utf-8', errors='replace').strip(),
                  shaders=len(records), scalar_cases=256, stage=str(stage),
                  emitted_scalar_reference_mismatches=sum(r['emitted_scalar_reference_mismatches']
                                                          for r in records),
                  validator='Khronos glslang 16.6.0', shader_records=records,
                  gameplay_verified=False, user_emulator_changed=False,
                  game_or_save_changed=False, release_published=False)
    (stage / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    report_name = ('vita3k-hud-upstream-validation.json' if args.expect_upstream
                   else 'vita3k-hud-fork-validation.json')
    (ROOT / 'docs' / report_name).write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'shader_records'}, indent=2))


if __name__ == '__main__':
    main()
