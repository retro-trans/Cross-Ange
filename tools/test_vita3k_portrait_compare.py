"""Verify comparison switching cannot overwrite unknown edits or touch saves."""
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import vita3k_portrait_compare as compare
from install_vita3k import digest


class PortraitComparisonChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'VERSION').write_text('0.1.9\n')
        self.build = self.root / 'work/output/cross-ange-0.1.9'
        self.english = self.build / 'game/cpk/Ange.cpk'
        self.original = self.root / 'work/source/decrypted/cpk/Ange.cpk'
        self.app = self.root / 'emulator/ux0/app/PCSG00597'
        self.target = self.app / 'cpk/Ange.cpk'
        self.save = self.root / 'emulator/ux0/user/00/savedata/PCSG00597/save.bin'
        self.license = self.root / 'emulator/ux0/license/PCSG00597/work.bin'
        for path, value in [(self.english,b'CPK English'),(self.original,b'CPK Original'),
                            (self.target,b'CPK English'),(self.save,b'save remains'),
                            (self.license,b'license remains')]:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(value)
        (self.build/'vita3k-install.json').write_text(json.dumps({
            'version':'0.1.9','title_id':'PCSG00597','app_directory':str(self.app),
            'installed_files':[{'path':'cpk/Ange.cpk','sha256':digest(self.english)}]}))
        original_guard = patch.object(compare,'ORIGINAL_SHA256',digest(self.original))
        original_guard.start()
        self.addCleanup(original_guard.stop)

    def run_mode(self, mode, write=False, running=False):
        args = ['compare','--mode',mode] + (['--write'] if write else [])
        with patch.object(compare,'ROOT',self.root), patch('sys.argv',args), \
             patch.object(compare.subprocess,'run',return_value=subprocess.CompletedProcess([],0,str(int(running)))), \
             contextlib.redirect_stdout(io.StringIO()):
            compare.main()

    def test_preview_does_not_change_installed_archive(self):
        self.run_mode('original')
        self.assertEqual(self.target.read_bytes(),self.english.read_bytes())
        self.assertFalse((self.root/'work/source/portrait-comparison/state.json').exists())

    def test_switch_restore_preserves_saves_license_and_immutable_archives(self):
        self.run_mode('original',True)
        self.assertEqual(self.target.read_bytes(),b'CPK Original')
        self.run_mode('english',True)
        self.assertEqual(self.target.read_bytes(),b'CPK English')
        self.assertEqual(self.original.read_bytes(),b'CPK Original')
        self.assertEqual(self.english.read_bytes(),b'CPK English')
        self.assertEqual(self.save.read_bytes(),b'save remains')
        self.assertEqual(self.license.read_bytes(),b'license remains')

    def test_unknown_edits_are_preserved(self):
        self.target.write_bytes(b'CPK User changes')
        with self.assertRaisesRegex(ValueError,'unknown changes'):
            self.run_mode('original',True)
        self.assertEqual(self.target.read_bytes(),b'CPK User changes')

    def test_running_emulator_is_refused(self):
        with self.assertRaisesRegex(ValueError,'Close Vita3K'):
            self.run_mode('original',True,True)
        self.assertEqual(self.target.read_bytes(),b'CPK English')


if __name__=='__main__':
    unittest.main()
