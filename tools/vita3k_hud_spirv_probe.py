"""Carry the reviewed indexed-uniform experiment into isolated Vulkan SPIR-V.

The main emulator is read-only. The closed, isolated comparison receives the
same-feature Vulkan cache and 12 patched vertex modules, with a complete backup.
Every changed module is validated before installation. Game/save/license bytes
are never written. This remains an unverified partial HUD-fix experiment.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import struct
import subprocess

from vita3k_hud_shader_probe import ROOT, EMU, PROBE, sha, candidate

MAIN = Path('E:/Emu/vita3k')


def instructions(words):
    if len(words)<5 or words[0]!=0x07230203:
        raise ValueError('Invalid SPIR-V header')
    offset=5
    while offset<len(words):
        size,opcode=words[offset]>>16,words[offset]&65535
        if size<1 or offset+size>len(words):
            raise ValueError('Truncated SPIR-V instruction')
        yield offset,opcode,words[offset+1:offset+size]
        offset+=size


def patch_module(data):
    if len(data)%4:
        raise ValueError('SPIR-V byte alignment mismatch')
    words=list(struct.unpack('<'+'I'*(len(data)//4),data))
    ops=list(instructions(words))
    names={a[0]:struct.pack('<'+'I'*(len(a)-1),*a[1:]).split(b'\0')[0].decode('utf-8')
           for _,op,a in ops if op==5}
    indexes=[identifier for identifier,name in names.items() if name=='idx']
    if len(indexes)!=1:
        raise ValueError('Missing or ambiguous native index-register array')
    constants={a[1]:a[2] for _,op,a in ops if op==43 and len(a)==3}
    chains={a[1]:a for _,op,a in ops if op==65 and a[2]==indexes[0]}
    loads={a[1]:a for _,op,a in ops if op==61 and a[2] in chains}
    multiplications={}
    for offset,opcode,args in ops:
        if opcode!=132 or len(args)!=4:
            continue
        value=None
        if args[2] in loads and constants.get(args[3])==2:value=args[2]
        if args[3] in loads and constants.get(args[2])==2:value=args[3]
        if value is not None:multiplications[args[1]]=(offset,args,value)
    if len(multiplications)!=2:
        raise ValueError('Expected exactly two reviewed index multiplications')
    offsets=[]
    for result,(at,args,value) in multiplications.items():
        uses=[a for _,op,a in ops if op==128 and result in a[2:]]
        if len(uses)!=1:
            raise ValueError('Indexed multiplication has an unreviewed use')
        other=[operand for operand in uses[0][2:] if operand!=result]
        if len(other)!=1 or constants.get(other[0]) not in (14,15):
            raise ValueError('Indexed lookup has an unreviewed scalar offset')
        if constants.get(chains[loads[value][2]][3])!=0:
            raise ValueError('Expected the reviewed idx[0] register')
        offsets.append(constants[other[0]])
    if sorted(offsets)!=[14,15]:
        raise ValueError('Expected adjacent native UV components')
    patched=words[:]
    changes=[]
    for result,(at,args,value) in multiplications.items():
        # OpIMul is five words. OpCopyObject preserves its type/result ID and
        # copies the unscaled index in four; one OpNop keeps offsets/size fixed.
        replacement=[(4<<16)|83,args[0],args[1],value,1<<16]
        patched[at:at+5]=replacement
        changes.append(dict(word_offset=at,old_words=words[at:at+5],new_words=replacement))
    output=struct.pack('<'+'I'*len(patched),*patched)
    list(instructions(patched))
    allowed={i for row in changes for i in range(row['word_offset'],row['word_offset']+5)}
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(words,patched))):
        raise ValueError('Unrelated SPIR-V word changed')
    return output,changes


def require_closed():
    command="Get-CimInstance Win32_Process -Filter \"Name = 'Vita3K.exe'\" | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],
                          capture_output=True,text=True,check=True)
    if not result.stdout.strip():return
    rows=json.loads(result.stdout)
    if isinstance(rows,dict):rows=[rows]
    for row in rows:
        path=row.get('ExecutablePath')
        if not path or Path(path).resolve()==(EMU/'Vita3K.exe').resolve():
            raise ValueError('Close the isolated comparison emulator before writing its cache')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    validator=PROBE/'vendor/spirv-tools-build/tools/Release/spirv-val.exe'
    if not validator.is_file():raise ValueError('Reviewed SPIRV-Tools validator is required')
    source=MAIN/'cache/shaders/PCSG00597/eboot.bin'
    destination=EMU/'cache/shaders/PCSG00597/eboot.bin'
    stage=PROBE/('vulkan-candidate-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    stage.mkdir(parents=True,exist_ok=False)
    baseline=json.loads((ROOT/'docs/vita3k-hud-shader-candidate.json').read_text(encoding='utf-8'))
    expected={row['shader']:row for row in baseline['shader_records']}
    header=(source/'hashs-vk.dat').read_bytes()
    count,version,features=struct.unpack_from('<QII',header)
    if (version,features)!=(13,25) or len(header)!=16+count*64:
        raise ValueError('Source cache does not match Vulkan High/Mapping Disabled on the reviewed GPU')
    prepared={p.name:p.read_bytes() for p in source.glob('vk13-*.spv')}
    if not set(p.name for p in destination.glob('vk13-*.spv'))<=prepared.keys():
        raise ValueError('Destination has unmatched Vulkan modules; preserve and review them')
    records=[]
    for program,metadata in expected.items():
        name='vk13-'+program+'.spv'
        data=prepared[name]
        native=(MAIN/'shaderlog/PCSG00597/eboot.bin'/('vk13-'+program+'.gxp')).read_bytes()
        if sha(native)!=program:raise ValueError('Native program hash mismatch')
        glsl=(Path(baseline['backup'])/metadata['cache_file']).read_text(encoding='utf-8')
        _,reference=candidate(glsl,native)
        changed,edits=patch_module(data)
        target=stage/name
        target.write_bytes(changed)
        for label,blob in [('original',data),('candidate',changed)]:
            file=target if label=='candidate' else stage/('original-'+name)
            if label=='original':file.write_bytes(blob)
            check=subprocess.run([str(validator),'--target-env','vulkan1.1',str(file)],capture_output=True,text=True)
            if check.returncode:raise ValueError(label+' validation failed: '+check.stdout+check.stderr)
        prepared[name]=changed
        records.append(dict(program=program,file=name,before_sha256=sha(data),after_sha256=sha(changed),
                            original_and_candidate_spirv_valid=True,edits=edits,
                            native_reference_cases=reference['native_scalar_reference_cases']))
    report=dict(status='validated_vulkan_candidate_awaiting_battle_test',write=args.write,
                target=str(EMU),renderer='Vulkan',high_accuracy=True,memory_mapping='disabled',
                native_shader_cache_version=version,features_mask=features,seeded_modules=len(prepared),
                patched_vertex_modules=len(records),index_edits=sum(len(r['edits']) for r in records),
                reference_cases=sum(r['native_reference_cases'] for r in records),shader_records=records,
                runtime_fix_verified=False,partial_opengl_improvement_reported=True,
                game_or_save_changed=False,main_emulator_changed=False,new_game_build=False,
                source_pushed=False,release_published=False)
    if args.write:
        require_closed()
        import shutil
        backup=stage/'previous-cache'
        shutil.copytree(destination,backup)
        # Retain the last tested GL candidate as well as a complete cache backup.
        for name,data in prepared.items():(destination/name).write_bytes(data)
        (destination/'hashs-vk.dat').write_bytes(header)
        pipeline=destination/'pipeline-cache-vk13.dat'
        if pipeline.exists():
            pipeline.replace(stage/'previous-pipeline-cache-vk13.dat')
        for name,data in prepared.items():
            if (destination/name).read_bytes()!=data:raise ValueError('Cache write did not verify')
        report['backup']=str(backup)
        report['pipeline_cache_quarantined_only_in_isolation']=True
    (stage/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (ROOT/'docs/vita3k-hud-vulkan-shader-candidate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='shader_records'},indent=2))


if __name__=='__main__':main()
