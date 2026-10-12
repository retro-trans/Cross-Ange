"""Crypto vectors, original PFS compatibility, paths and PKG metadata regressions."""
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import modes
import vita_pkg_repack as pkg
from patch_pkg import structured_license


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = pkg.constants()

    def test_aes_cbc_known_vector(self):
        key = bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')
        iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
        plain = bytes.fromhex('6bc1bee22e409f96e93d7e117393172a')
        encrypted = bytes.fromhex('7649abac8119b246cee98e9b12e9197d')
        self.assertEqual(pkg.cbc_tail(plain,key,iv),encrypted)
        self.assertEqual(pkg.cbc_tail(encrypted,key,iv,True),plain)

    def test_short_and_partial_sector_inverse(self):
        key, iv = bytes(range(16)),bytes(range(16,32))
        for size in (1,15,16,17,31,32,32767,32768):
            data = bytes(index % 251 for index in range(size))
            encrypted = pkg.sector_cipher(data,key,iv,37)
            self.assertEqual(pkg.sector_cipher(encrypted,key,iv,37,True),data)

    def test_rejects_unsafe_member_paths(self):
        for name in ('../a','a/../b','/a','a\\b','a:b','a//b','a/./b','a/'+'x'*68):
            with self.assertRaises(ValueError):
                pkg.safe_name(name)

    def test_rejects_account_bound_license(self):
        self.assertFalse(structured_license(bytes(512)))

    def test_original_pfs_header_hmac(self):
        source = pkg.ROOT/'work/source/pkg/app/PCSG00597/sce_pfs/files.db'
        license_path = pkg.ROOT/'incoming/work.bin'
        if not source.exists() or not license_path.exists():
            self.skipTest('Local original PFS/license unavailable')
        header = bytearray(source.read_bytes()[:1024])
        expected = bytes(header[76:96])
        header[76:96] = bytes(20)
        header[96:352] = bytes(256)
        secret = pkg.pfs_secret(license_path.read_bytes()[0x50:0x60],struct.unpack_from('<I',header,28)[0],0,self.values)
        self.assertEqual(pkg.mac(secret,header[:0x160]),expected)

    def test_original_cpk_sector_reencryption(self):
        base = pkg.ROOT/'work/source/pkg/app/PCSG00597'
        license_path = pkg.ROOT/'incoming/work.bin'
        plaintext = pkg.ROOT/'work/source/decrypted/cpk/Ange.cpk'
        if not base.exists() or not license_path.exists() or not plaintext.exists():
            self.skipTest('Local game sources unavailable')
        with (base/'cpk/Ange.cpk').open('rb') as stream:
            original = stream.read(pkg.SECTOR)
        key = license_path.read_bytes()[0x50:0x60]
        db = (base/'sce_pfs/unicv.db').read_bytes()
        fs_header = (base/'sce_pfs/files.db').read_bytes()
        salt = struct.unpack_from('<I',fs_header,28)[0]
        offset = pkg.PAGE
        found = None
        while offset < len(db):
            if db[offset:offset+8] == b'SCEIFTBL':
                sectors = struct.unpack_from('<I',db,offset+20)[0]
                if sectors:
                    secret = pkg.pfs_secret(key,salt,offset//pkg.PAGE,self.values)
                    signature = pkg.mac(pkg.mac(secret,struct.pack('<I',0)),original)
                    if signature == db[offset+pkg.PAGE+16:offset+pkg.PAGE+36]:
                        found = db[offset+52:offset+72]
                        break
                offset += pkg.PAGE*(1+(sectors+49)//50)
            else:
                offset += pkg.PAGE
        self.assertIsNotNone(found,'Original CPK signature-table match')
        derived = pkg.aes(key,self.values['contract'],modes.ECB(),True)
        with plaintext.open('rb') as stream:
            plain = stream.read(pkg.SECTOR)
        self.assertEqual(pkg.sector_cipher(plain,derived,pkg.mac(self.values['hmac0'],found)[:16],0),original)

    def test_btree_header_and_all_child_hashes(self):
        template = bytearray(1024)
        struct.pack_into('<8sIHHIIIIQQQ',template,0,b'SCENGPFS',5,1,0,1024,10,0,123,0xFFFFFFFFFFFFFFFF,0,0)
        records = [dict(path='file'+str(index).zfill(3),id=index+1,parent=0,directory=False,bytes=index+5) for index in range(120)]
        key = bytes(range(16))
        data = pkg.files_database(records,template,key,self.values)
        secret = pkg.pfs_secret(key,123,0,self.values)
        root = struct.unpack_from('<I',data,24)[0]
        pages = [data[index:index+1024] for index in range(1024,len(data),1024)]
        self.assertEqual(pkg.mac(secret,pages[root][4:]),data[56:76])
        visited_records = 0
        for index,page in enumerate(pages):
            parent,kind,count,_ = struct.unpack_from('<IIII',page)
            visited_records += count
            if parent != 0xFFFFFFFF:
                self.assertIn(pkg.mac(secret,page[4:]),[pages[parent][offset:offset+20] for offset in range(824,1024,20)])
            self.assertLessEqual(count,9)
        self.assertEqual(visited_records,120)

    def test_pkg_plaintext_sfo_and_payload_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            original = folder/'original.pkg'
            header = bytearray(512)
            header[:4] = b'\x7fPKG'
            header[192:196] = b'\x7fext'
            header[231] = 2
            header[48:48+len(pkg.CONTENT)] = pkg.CONTENT.encode()
            struct.pack_into('>II',header,8,256,3)
            struct.pack_into('>QQQ',header,24,512,512,0)
            struct.pack_into('>III',header,256,2,4,0x15)
            struct.pack_into('>IIII',header,268,13,8,0,0)
            struct.pack_into('>IIII',header,284,14,8,400,4)
            header[400:404] = b'\x00PSF'
            original.write_bytes(header)
            encrypted = folder/'encrypted-sfo'
            encrypted.write_bytes(b'not plaintext')
            plain = folder/'plain-sfo'
            plain.write_bytes(b'\x00PSFtest fixture')
            extra = folder/'extra'
            extra.write_bytes(bytes(range(255))*35)
            result = pkg.write_pkg(original,{'sce_sys/param.sfo':encrypted,'data/test.bin':extra},
                                   folder/'translated.pkg',self.values,plain)
            parsed = pkg.read_pkg(folder/'translated.pkg',self.values)
            offset,length = struct.unpack_from('>II',parsed['metadata'][14][1])
            self.assertEqual(parsed['prefix'][offset:offset+length],plain.read_bytes())
            self.assertEqual(pkg.small_member(folder/'translated.pkg',parsed,'sce_sys/param.sfo'),encrypted.read_bytes())
            self.assertEqual(pkg.small_member(folder/'translated.pkg',parsed,'data/test.bin'),extra.read_bytes())
            self.assertFalse(result['sony_signed'])
            with self.assertRaises(ValueError):
                pkg.write_pkg(original,{'sce_sys/param.sfo':encrypted},folder/'invalid.pkg',self.values,encrypted)


if __name__ == '__main__':
    unittest.main()
