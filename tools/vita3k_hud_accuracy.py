"""Preview/apply a reversible, game-only High Accuracy/memory-mapping profile.

No game, save, license, shader cache or global configuration file is written.
The profile schema was checked against Vita3K 4188 config/src/settings.cpp.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'PCSG00597'
GPU_DEFAULTS = {
    'backend-renderer': 'Vulkan', 'gpu-idx': '0', 'high-accuracy': 'false',
    'resolution-multiplier': '1', 'disable-surface-sync': 'true',
    'screen-filter': 'Bilinear', 'memory-mapping': 'double-buffer',
    'v-sync': 'true', 'anisotropic-filtering': '1',
    'async-pipeline-compilation': 'true', 'import-textures': 'false',
    'export-textures': 'false', 'export-as-png': 'true',
    'fps-hack': 'false', 'shader-cache': 'true', 'spirv-shader': 'false',
    'texture-cache': 'true',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def make_profile(global_data, existing=None, memory_mapping=None, backend_renderer=None, surface_sync=None):
    """Retain other settings; optionally test a different memory-mapping path."""
    if memory_mapping not in (None, 'disabled', 'double-buffer'):
        raise ValueError('Unreviewed memory mapping method')
    if backend_renderer not in (None, 'OpenGL', 'Vulkan'):
        raise ValueError('Unreviewed renderer')
    if surface_sync not in (None, 'enabled', 'disabled'):
        raise ValueError('Unreviewed surface sync setting')
    doc = ET.fromstring(existing) if existing else ET.Element('config')
    if doc.tag != 'config':
        raise ValueError('Unexpected custom configuration root; preserve it')
    gpu = doc.find('gpu')
    if gpu is None:
        gpu = ET.SubElement(doc, 'gpu')
        values = dict(GPU_DEFAULTS)
        text = global_data.decode('utf-8-sig')
        for key in values:
            match = re.search(r'^'+re.escape(key)+r':\s*(.*?)\s*$',text,re.M)
            if match:
                value = match[1].strip()
                if value[:1] in ('"', "'"):
                    value = value[1:-1]
                values[key] = value
        gpu.attrib.update(values)
    before = dict(gpu.attrib)
    gpu.set('high-accuracy', 'true')
    if memory_mapping is not None:
        gpu.set('memory-mapping', memory_mapping)
    if backend_renderer is not None:
        gpu.set('backend-renderer', backend_renderer)
    if surface_sync is not None:
        gpu.set('disable-surface-sync', 'false' if surface_sync=='enabled' else 'true')
    after = dict(gpu.attrib)
    allowed = {'high-accuracy'} | ({'memory-mapping'} if memory_mapping is not None else set())
    allowed |= {'backend-renderer'} if backend_renderer is not None else set()
    allowed |= {'disable-surface-sync'} if surface_sync is not None else set()
    assert {k:v for k,v in before.items() if k not in allowed} == {
        k:v for k,v in after.items() if k not in allowed}
    ET.indent(doc)
    output = ET.tostring(doc, encoding='utf-8', xml_declaration=True)+b'\n'
    assert ET.fromstring(output).find('gpu').get('high-accuracy') == 'true'
    return output, before, after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vita3k', type=Path, required=True, help='Emulator program folder')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--memory-mapping', choices=['disabled', 'double-buffer'],
                        help='Optional game-only diagnostic; other settings remain unchanged')
    parser.add_argument('--backend-renderer', choices=['OpenGL', 'Vulkan'],
                        help='Optional game-only renderer comparison')
    parser.add_argument('--surface-sync', choices=['enabled', 'disabled'],
                        help='Optional game-only CPU/GPU surface synchronization comparison')
    args = parser.parse_args()
    vendor = args.vita3k.resolve()
    if not (vendor/'Vita3K.exe').is_file() or (vendor/'portable').exists():
        raise ValueError('Expected the reviewed, non-portable Vita3K installation')
    global_path = vendor/'config.yml'
    global_data = global_path.read_bytes()
    destination = vendor/'config'/('config_'+TITLE+'.xml')
    if vendor not in destination.resolve().parents:
        raise ValueError('Profile leaves selected emulator folder')
    existing = destination.read_bytes() if destination.exists() else None
    output, before, after = make_profile(global_data,existing,args.memory_mapping,args.backend_renderer,args.surface_sync)
    changed = [k for k in after if before.get(k) != after[k]]
    report = dict(title_id=TITLE, profile=str(destination), write=args.write,
                  settings_before=before, settings_after=after,
                  only_effective_setting_changed=changed[0] if len(changed)==1 else None,
                  changed_settings=changed,
                  global_config_sha256=digest(global_data),
                  previous_profile_sha256=digest(existing) if existing else None,
                  profile_sha256=digest(output), restart_required=True,
                  game_bytes_changed=False, saves_and_license_written=False,
                  runtime_hud_fix_verified=False)
    if args.write:
        if global_path.read_bytes() != global_data:
            raise ValueError('Global configuration changed during preparation; retry')
        if (destination.read_bytes() if destination.exists() else None) != existing:
            raise ValueError('Custom profile changed during preparation; retry')
        backup = ROOT/'work/source/vita3k-install-backups'/('hud-accuracy-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        backup.mkdir(parents=True,exist_ok=False)
        (backup/'global-config.yml').write_bytes(global_data)
        if existing:
            (backup/destination.name).write_bytes(existing)
        report['backup'] = str(backup)
        destination.parent.mkdir(parents=True,exist_ok=True)
        staging = destination.with_suffix('.xml.hud-staging')
        with staging.open('xb') as stream:
            stream.write(output)
        assert staging.read_bytes() == output
        staging.replace(destination)
        assert destination.read_bytes() == output
        assert global_path.read_bytes() == global_data
        (backup/'record.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
