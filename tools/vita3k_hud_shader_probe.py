"""Check GXP texture-animation indexing and stage an isolated OpenGL experiment.

No game/firmware/license/save/global configuration file is modified. With
--write, only already-cached vertex GLSL files in the reviewed isolated emulator
are replaced, after native-parameter checks and glslang validation. The original
cache files are backed up. This is a title-specific experiment, not a general
emulator fix or a verified gameplay workaround.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EMU = ROOT/'work/source/hud-runtime-20261025/emulator'
PROBE = ROOT/'work/source/hud-shader-probe'
INDEX = re.compile(r'\(idx\[(\d)\] \* 2\) \+ (\d+)')
I16_FIELDS = [('opcode',5),('pred',2),('abs',1),('skipinv',1),('nosched',1),
              ('src2_neg',1),('sel1h_upper8',1),('dest_bank_ext',1),('end',1),
              ('src1_bank_ext',1),('src2_bank_ext',1),('unused',1),('repeat_count',3),
              ('mode',2),('src2_format',2),('src1_format',2),('sel2h_upper8',1),
              ('or_shift',2),('src0_bank',1),('dest_bank',2),('src1_bank',2),
              ('src2_bank',2),('dest_n',7),('src0_n',7),('src1_n',7),('src2_n',7)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parameters(data):
    if data[:4] != b'GXP\0':
        raise ValueError('Not a native GXP shader')
    count,offset = struct.unpack_from('<II',data,36)
    if count > 256:
        raise ValueError('Unexpected GXP parameter count')
    result = {}
    container_count,container_offset = struct.unpack_from('<II',data,144)
    if container_count>64:
        raise ValueError('Unexpected native container count')
    containers={}
    for i in range(container_count):
        number,unknown,base,size=struct.unpack_from('<4H',data,148+container_offset+8*i)
        containers[number]=base
    for i in range(count):
        start = 40+offset+16*i
        name_offset = struct.unpack_from('<i',data,start)[0]
        name = data[start+name_offset:data.index(b'\0',start+name_offset)].decode('ascii')
        array_size,resource_index = struct.unpack_from('<II',data,start+8)
        container_index=data[start+5]>>4
        base=containers.get(container_index,0)
        result[name] = dict(components=data[start+5]&15,array_size=array_size,resource_index=resource_index,
                            container_index=container_index,container_base=base,first_scalar_register=base+resource_index)
    return result


def native_index_bias(data):
    """Decode the actual I16MAD index assignment, independently of cached GLSL."""
    count,offset=struct.unpack_from('<II',data,60)
    instructions=struct.unpack_from('<'+'Q'*count,data,64+offset)
    assignments=[]
    for word in instructions:
        if word>>59 != 0b10100:
            continue
        fields={}
        position=64
        for name,width in I16_FIELDS:
            position-=width
            fields[name]=(word>>position)&((1<<width)-1)
        assert position==0
        if fields['dest_bank_ext']!=1 or fields['dest_bank']!=2:
            continue
        required=dict(dest_n=1,src1_bank_ext=1,src2_bank_ext=1,src1_bank=2,
                      src2_bank=2,src1_n=1,src1_format=1,src2_format=1,
                      src2_neg=0,abs=0,repeat_count=0,or_shift=0)
        if any(fields[k]!=v for k,v in required.items()):
            raise ValueError('Unreviewed native index-register arithmetic')
        assignments.append(fields['src2_n'])
    if len(assignments)!=1:
        raise ValueError('Native index assignment missing or ambiguous')
    return assignments[0]


def candidate(source, native):
    """Require the shader's own tanm declaration to justify every index edit."""
    matches = list(INDEX.finditer(source))
    if not matches:
        return None
    param = parameters(native)['tanm']
    if param['components'] != 2 or param['array_size'] < 1:
        raise ValueError('Expected the native float2 texture-animation array')
    if len(matches)!=2 or len({m[1] for m in matches})!=1:
        raise ValueError('Unreviewed indexed shader shape')
    idx = matches[0][1]
    offsets = [int(m[2]) for m in matches]
    if offsets[1] != offsets[0]+1:
        raise ValueError('Expected adjacent texture-coordinate components')
    # The native shader shifts the animation index left by one and then adds a
    # constant with IMA16. Its register offset plus that constant must equal
    # the GXP's independently declared first scalar register for tanm.
    assignment = re.search(r'idx\['+idx+r'\] = \(\(.*? \* 1\) \+ (\d+)\) & 65535;',source)
    if assignment is None:
        raise ValueError('Unreviewed indexed-register assignment')
    bias = int(assignment[1])
    if bias!=native_index_bias(native):
        raise ValueError('GLSL index assignment differs from native I16MAD')
    first = param['first_scalar_register']
    if bias+offsets[0] != first:
        raise ValueError('Candidate index base does not match native GXP declaration')
    # Check both components of every declared array entry, not just element 0.
    cases=[]
    for element in range(param['array_size']):
        for component,add in enumerate(offsets):
            index_register = 2*element+bias
            expected = first+2*element+component
            before = 2*index_register+add
            after = index_register+add
            if after != expected:
                raise ValueError('Native array reference mismatch')
            cases.append(dict(element=element,component=component,expected=expected,before=before,after=after))
    changed = INDEX.sub(lambda m:'idx['+m[1]+'] + '+m[2],source)
    if INDEX.search(changed):
        raise ValueError('An indexed lookup was not reviewed')
    return changed,dict(native_parameter=param,index_bias=bias,native_instruction_bias_verified=True,lookup_offsets=offsets,
                        edits=len(matches),native_scalar_reference_cases=len(cases),
                        incorrect_original_cases=sum(r['before']!=r['expected'] for r in cases),
                        first_cases=cases[:4],all_candidate_cases_match=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    cache=EMU/'cache/shaders/PCSG00597/eboot.bin'
    shaderlog=EMU/'shaderlog/PCSG00597/eboot.bin'
    validator=PROBE/'vendor/glslang-16.6.0/bin/glslang.exe'
    if not validator.is_file():
        raise ValueError('Reviewed Khronos glslang 16.6.0 validator is required')
    stage=PROBE/('candidate-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    stage.mkdir(parents=True,exist_ok=False)
    changes=[]
    checked=[]
    for path in sorted(cache.glob('v13-*.vert')):
        data=path.read_bytes()
        if not INDEX.search(data.decode('utf-8')):
            continue
        native=(shaderlog/(path.stem+'.gxp')).read_bytes()
        revised,proof=candidate(data.decode('utf-8'),native)
        # Cached GLSL and logged native GXP must identify the same program.
        program=path.stem.split('-',1)[1]
        if sha(native)!=program:
            raise ValueError('Native program hash mismatch')
        target=stage/path.name
        target.write_bytes(revised.encode('utf-8'))
        check=subprocess.run([str(validator),'-S','vert',str(target)],capture_output=True,text=True,check=False)
        if check.returncode:
            raise ValueError('Candidate GLSL compile failed: '+check.stdout+check.stderr)
        changes.append((path,data,target.read_bytes()))
        checked.append(dict(shader=program,cache_file=path.name,before_sha256=sha(data),
                            after_sha256=sha(target.read_bytes()),glslang_compile=True,**proof))
    if len(changes)!=12:
        raise ValueError('Unexpected indexed shader inventory; review before applying')
    report=dict(status='candidate_compiled_awaiting_gameplay',write=args.write,
                target='Isolated original Japanese game, OpenGL only',emulator=str(EMU),
                shaders=len(changes),lookup_edits=sum(r['edits'] for r in checked),
                reference_cases=sum(r['native_scalar_reference_cases'] for r in checked),
                validator='Khronos glslang 16.6.0',shader_records=checked,
                runtime_fix_verified=False,game_or_save_changed=False,
                user_emulator_changed=False,source_pushed=False,release_published=False)
    if args.write:
        # Readback guard prevents silently replacing files changed since preview.
        if not all(path.read_bytes()==before for path,before,after in changes):
            raise ValueError('Shader cache changed during validation')
        backup=stage/'original-cache'
        backup.mkdir()
        for path,before,after in changes:
            (backup/path.name).write_bytes(before)
            path.write_bytes(after)
            if path.read_bytes()!=after:
                raise ValueError('Shader-cache write did not verify')
        report['backup']=str(backup)
        report['rollback']='Restore these 12 original-cache files with the isolated emulator closed.'
    (stage/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (ROOT/'docs/vita3k-hud-shader-candidate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='shader_records'},indent=2))


if __name__=='__main__':
    main()
