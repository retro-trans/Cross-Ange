"""Native-GXP references for the isolated indexed-uniform experiment."""
import json
from pathlib import Path
import struct
import unittest

from vita3k_hud_shader_probe import candidate,parameters,EMU,ROOT


class ShaderIndexReferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((ROOT/'docs/vita3k-hud-shader-candidate.json').read_text(encoding='utf-8'))
        cls.backup=Path(cls.report['backup'])

    def inputs(self,row):
        name=row['cache_file']
        source=(self.backup/name).read_text(encoding='utf-8')
        native=(EMU/'shaderlog/PCSG00597/eboot.bin'/(Path(name).stem+'.gxp')).read_bytes()
        return source,native

    def test_every_array_component_matches_independent_native_declaration(self):
        cases=0
        for row in self.report['shader_records']:
            source,native=self.inputs(row)
            after,proof=candidate(source,native)
            self.assertTrue(proof['native_instruction_bias_verified'])
            self.assertTrue(proof['all_candidate_cases_match'])
            self.assertEqual(proof['incorrect_original_cases'],proof['native_scalar_reference_cases'])
            self.assertEqual(after,(EMU/'cache/shaders/PCSG00597/eboot.bin'/row['cache_file']).read_text(encoding='utf-8'))
            cases+=proof['native_scalar_reference_cases']
        self.assertEqual(cases,256)
        hud=next(r for r in self.report['shader_records'] if r['shader'].startswith('8a204ef9'))
        source,native=self.inputs(hud)
        self.assertEqual(parameters(native)['tanm']['first_scalar_register'],20)
        self.assertEqual(candidate(source,native)[1]['first_cases'][0],
                         dict(element=0,component=0,expected=20,before=26,after=20))

    def test_unrelated_shader_has_no_candidate_change(self):
        self.assertIsNone(candidate('void main() {}',b''))

    def test_changed_native_uniform_contract_is_rejected(self):
        source,native=self.inputs(self.report['shader_records'][0])
        changed=bytearray(native)
        count,offset=struct.unpack_from('<II',changed,36)
        for i in range(count):
            start=40+offset+16*i
            relative=struct.unpack_from('<i',changed,start)[0]
            name=changed[start+relative:changed.index(0,start+relative)]
            if name==b'tanm':
                resource=struct.unpack_from('<I',changed,start+12)[0]
                struct.pack_into('<I',changed,start+12,resource+1)
                break
        else:self.fail('Missing test parameter')
        with self.assertRaisesRegex(ValueError,'native GXP declaration'):
            candidate(source,changed)

    def test_unreviewed_extra_lookup_is_rejected(self):
        source,native=self.inputs(self.report['shader_records'][0])
        with self.assertRaisesRegex(ValueError,'shader shape'):
            candidate(source+'\nint unexpected = (idx[0] * 2) + 14;',native)


if __name__=='__main__':
    unittest.main()
