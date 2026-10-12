"""Experimental Vita3K PKG writer with encrypted PFS and complete integrity tables.

This makes emulator test packages, not Sony-signed packages for a physical Vita.
Format references: Vita3K/psvpfsparser (PfsCryptEngineSelectors.cpp,
SecretGenerator.cpp, FilesDbParser.h, NodeIcvCalculator.cpp, UnicvDbTypes.h),
and mmozeiko/pkg2zip. Public format constants are loaded from ignored upstream
checkouts; no personal license or derived key is embedded in this source.
"""
import hashlib
import hmac
import re
import struct
from pathlib import Path, PurePosixPath

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
PAGE = 0x400
SECTOR = 0x8000
CONTENT = 'JP0700-PCSG00597_00-CROSSANGEGAME000'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def constant(path, name):
    text = Path(path).read_text(encoding='utf-8')
    match = re.search(r'\b' + re.escape(name) + r'\s*\[[^\]]*\]\s*=\s*\{([^}]+)\}', text)
    require(match is not None, 'Missing upstream format constant: ' + name)
    return bytes(int(token, 16) for token in re.findall(r'0x([0-9a-fA-F]{2})\b', match.group(1)))


def constants():
    pfs = ROOT / 'tools/pkg_vendor/psvpfsparser-repack-probe'
    pkg = ROOT / 'tools/pkg2zip/pkg2zip.c'
    return {
        'contract': constant(pfs / 'F00DNativeKeyEncryptor.cpp', 'contract_key0'),
        'hmac0': constant(pfs / 'PfsKeys.cpp', 'hmac_key0'),
        'hmac1': constant(pfs / 'PfsKeys.cpp', 'hmac_key1'),
        'iv': constant(pfs / 'PfsKeys.cpp', 'iv0'),
        'pkg2': constant(pkg, 'pkg_vita_2'),
    }


def aes(data, key, mode, decrypt=False):
    context = Cipher(algorithms.AES(key), mode).decryptor() if decrypt else Cipher(algorithms.AES(key), mode).encryptor()
    return context.update(data) + context.finalize()


def mac(key, data):
    return hmac.new(key, data, hashlib.sha1).digest()


def cbc_tail(data, key, iv, decrypt=False):
    """PFS CBC plus XOR tail, as implemented by the native PFS library."""
    boundary = len(data) & ~15
    head = aes(data[:boundary], key, modes.CBC(iv), decrypt) if boundary else b''
    if boundary:
        iv = data[boundary-16:boundary] if decrypt else head[-16:]
    tail = data[boundary:]
    mask = aes(iv, key, modes.ECB()) if tail else b''
    return head + bytes(left ^ right for left, right in zip(tail, mask))


def pfs_secret(license_key, files_salt, icv_salt, values):
    derived = aes(license_key, values['contract'], modes.ECB(), True)
    salts = struct.pack('<II', files_salt, icv_salt) if files_salt else struct.pack('<I', icv_salt)
    return cbc_tail(mac(values['hmac1'], salts), derived, values['iv'])


def sector_cipher(data, derived_key, tweak_mask, sector, decrypt=False):
    offset = struct.pack('<Q', sector * SECTOR) + bytes(8)
    iv = bytes(left ^ right for left, right in zip(offset, tweak_mask))
    return cbc_tail(data, derived_key, iv, decrypt)


def safe_name(name):
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and '\\' not in name and ':' not in name,
            'Unsafe package member path')
    require(all(part not in ('', '.', '..') for part in name.split('/')), 'Unsafe package member path')
    require(str(path) == name and all(len(part.encode('ascii')) < 68 for part in path.parts),
            'Unsupported PFS member name')
    return name


def read_pkg(path, values):
    """Read only metadata and the encrypted item/name table; never log keys."""
    with Path(path).open('rb') as stream:
        header = stream.read(256)
        require(header[:4] == b'\x7fPKG' and header[192:196] == b'\x7fext', 'Invalid PKG header')
        require(header[231] & 7 == 2, 'Only Vita key-type 2 packages are supported')
        require(header[48:96].rstrip(b'\0').decode('ascii') == CONTENT, 'Wrong PKG content identity')
        total, offset, encrypted_size = struct.unpack_from('>QQQ', header, 24)
        require(total == Path(path).stat().st_size and offset + encrypted_size <= total, 'Truncated PKG')
        require(offset < 16 * 1024 * 1024, 'Unexpected PKG metadata size')
        stream.seek(0)
        prefix = bytearray(stream.read(offset))
        iv = header[112:128]
        key = aes(iv, values['pkg2'], modes.ECB())
        metadata_offset, metadata_count = struct.unpack_from('>II', header, 8)
        metadata = {}
        for _ in range(metadata_count):
            kind, length = struct.unpack_from('>II', prefix, metadata_offset)
            require(metadata_offset + 8 + length <= len(prefix), 'Invalid PKG metadata record')
            metadata[kind] = (metadata_offset + 8, bytes(prefix[metadata_offset+8:metadata_offset+8+length]))
            metadata_offset += 8 + length
        require(struct.unpack_from('>I', metadata[2][1])[0] == 0x15, 'Not a Vita base application PKG')
        items_offset, items_size = struct.unpack_from('>II', metadata[13][1])
        count = struct.unpack_from('>I', header, 20)[0]
        require(count < 10000 and items_offset % 16 == 0, 'Unsupported PKG item table')
        stream.seek(offset + items_offset)
        table = aes(stream.read(count * 32), key, modes.CTR((int.from_bytes(iv, 'big') + items_offset//16).to_bytes(16, 'big')))
        entries = []
        names = set()
        for index in range(count):
            name_offset, name_size, data_offset, size, kind, padding = struct.unpack_from('>IIQQII', table, index*32)
            require(name_size < 2048 and name_offset % 16 == 0 and data_offset % 16 == 0,
                    'Invalid PKG member alignment')
            require(name_offset + name_size <= encrypted_size and data_offset + size <= encrypted_size,
                    'PKG member extends beyond payload')
            stream.seek(offset + name_offset)
            name = aes(stream.read(name_size), key,
                       modes.CTR((int.from_bytes(iv, 'big') + name_offset//16).to_bytes(16, 'big'))).decode('ascii')
            safe_name(name)
            require(name.casefold() not in names, 'Duplicate PKG path')
            names.add(name.casefold())
            entries.append(dict(name=name, offset=data_offset, bytes=size, type=kind, directory=(kind & 255) in (4, 18)))
    return dict(prefix=prefix, offset=offset, iv=iv, key=key, metadata=metadata, entries=entries)


def small_member(package, parsed, name):
    row = next((entry for entry in parsed['entries'] if entry['name'] == name), None)
    require(row is not None and not row['directory'] and row['bytes'] <= 1024*1024,
            'Required small PKG member is missing or oversized')
    counter = (int.from_bytes(parsed['iv'], 'big') + row['offset']//16).to_bytes(16, 'big')
    with Path(package).open('rb') as stream:
        stream.seek(parsed['offset'] + row['offset'])
        data = stream.read(row['bytes'])
    require(len(data) == row['bytes'], 'Truncated PKG member')
    return aes(data, parsed['key'], modes.CTR(counter))


class Node:
    def __init__(self, records=None, children=None):
        self.records = records or []
        self.children = children or []


def file_tree(records):
    """Order-10 B-tree: at most nine names and ten child hashes per page."""
    root = Node()

    def split(parent, index):
        old = parent.children[index]
        right = Node(old.records[5:], old.children[5:] if old.children else [])
        median = old.records[4]
        old.records = old.records[:4]
        old.children = old.children[:5] if old.children else []
        parent.records.insert(index, median)
        parent.children.insert(index+1, right)

    def insert(node, record):
        index = 0
        while index < len(node.records) and node.records[index]['path'] < record['path']:
            index += 1
        if not node.children:
            node.records.insert(index, record)
        else:
            if len(node.children[index].records) == 9:
                split(node, index)
                if record['path'] > node.records[index]['path']:
                    index += 1
            insert(node.children[index], record)

    for record in sorted(records, key=lambda row: row['path']):
        if len(root.records) == 9:
            root = Node(children=[root])
            split(root, 0)
        insert(root, record)
    return root


def files_database(records, template_header, license_key, values):
    require(template_header[:8] == b'SCENGPFS' and struct.unpack_from('<I', template_header, 8)[0] == 5,
            'Only PFS files.db version 5 is supported')
    require(struct.unpack_from('<HH', template_header, 12) == (1, 0), 'Unsupported PFS image/key type')
    files_salt = struct.unpack_from('<I', template_header, 28)[0]
    secret = pfs_secret(license_key, files_salt, 0, values)
    root = file_tree(records)
    nodes = []

    def enumerate_nodes(node, parent):
        node.page = len(nodes)
        node.parent = parent
        nodes.append(node)
        for child in node.children:
            enumerate_nodes(child, node.page)

    enumerate_nodes(root, 0xFFFFFFFF)
    pages = {}

    def encode(node):
        page = bytearray(PAGE)
        struct.pack_into('<IIII', page, 0, node.parent, int(bool(node.children)), len(node.records), 0)
        for index in range(10):
            struct.pack_into('<I', page, 16+9*72+index*16, 0xFFFFFFFF)
        for index, record in enumerate(node.records):
            info_offset = 16+9*72+index*16
            name_offset = 16+index*72
            struct.pack_into('<I', page, name_offset, record['parent'])
            name = PurePosixPath(record['path']).name.encode('ascii')
            page[name_offset+4:name_offset+4+len(name)] = name
            struct.pack_into('<IHHII', page, info_offset, record['id'], 0x8000 if record['directory'] else 7,
                             0, record['bytes'], 0)
        for index, child in enumerate(node.children):
            digest = encode(child)
            page[824+index*20:844+index*20] = digest
        pages[node.page] = bytes(page)
        return mac(secret, page[4:])

    root_digest = encode(root)
    header = bytearray(template_header)
    # An emulator package cannot retain a valid Sony RSA signature after edits.
    header[96:608] = bytes(512)
    struct.pack_into('<I', header, 24, root.page)
    struct.pack_into('<Q', header, 40, len(nodes)*PAGE)
    header[56:76] = root_digest
    header[76:96] = bytes(20)
    header[76:96] = mac(secret, header[:0x160])
    return bytes(header) + b''.join(pages[index] for index in range(len(nodes)))


def inventory(files):
    paths = set(files)
    directories = set()
    for name in files:
        safe_name(name)
        for parent in PurePosixPath(name).parents:
            if str(parent) != '.':
                directories.add(str(parent))
    require(not paths & directories, 'Conflicting file/directory path')
    names = sorted(paths | directories)
    require(len({name.casefold() for name in names}) == len(names), 'Case-colliding PFS paths')
    ids = {name: index+1 for index, name in enumerate(names)}
    records = []
    for name in names:
        parent = str(PurePosixPath(name).parent)
        directory = name in directories
        size = 0 if directory else Path(files[name]).stat().st_size
        require(size < 2**32, 'PFS file exceeds supported size')
        records.append(dict(path=name, id=ids[name], parent=ids.get(parent, 0), directory=directory, bytes=size))
    return records


def make_pfs(files, template_header, license_key, destination, values):
    destination = Path(destination)
    require(not destination.exists(), 'Preserve existing PFS output')
    destination.mkdir(parents=True)
    records = inventory(files)
    files_salt = struct.unpack_from('<I', template_header, 28)[0]
    derived_key = aes(license_key, values['contract'], modes.ECB(), True)
    unicv = bytearray(PAGE)
    expected = {}
    for record in records:
        path = destination / record['path']
        if record['directory']:
            path.mkdir(parents=True, exist_ok=True)
        sectors = (record['bytes'] + SECTOR-1) // SECTOR
        salt = len(unicv) // PAGE
        # Stable per-file seed. Not a license or secret; drives the PFS IV mask.
        seed = hashlib.sha1(record['path'].encode('ascii')).digest() if sectors else bytes(20)
        header = bytearray(PAGE)
        struct.pack_into('<8sIIIIII', header, 0, b'SCEIFTBL', 2, PAGE, 50, sectors, SECTOR, 0)
        header[52:72] = seed
        unicv.extend(header)
        if record['directory'] or not sectors:
            if not record['directory']:
                path.touch()
                expected[record['path']] = dict(bytes=0, sha256=hashlib.sha256(b'').hexdigest())
            continue
        secret = pfs_secret(license_key, files_salt, salt, values)
        mask = mac(values['hmac0'], seed)[:16]
        signatures = []
        source_hash = hashlib.sha256()
        path.parent.mkdir(parents=True, exist_ok=True)
        with Path(files[record['path']]).open('rb') as source, path.open('xb') as target:
            for sector in range(sectors):
                data = source.read(SECTOR)
                source_hash.update(data)
                encrypted = sector_cipher(data, derived_key, mask, sector)
                # Check every sector's inverse before allowing publication.
                require(sector_cipher(encrypted, derived_key, mask, sector, True) == data,
                        'PFS sector encryption roundtrip failed')
                target.write(encrypted)
                signatures.append(mac(mac(secret, struct.pack('<I', sector)), encrypted))
        expected[record['path']] = dict(bytes=record['bytes'], sha256=source_hash.hexdigest())
        for start in range(0, len(signatures), 50):
            subset = signatures[start:start+50]
            block = bytearray(PAGE)
            struct.pack_into('<IIII', block, 0, 0x3F8, 20, len(subset), 0)
            block[16:16+len(subset)*20] = b''.join(subset)
            unicv.extend(block)
    struct.pack_into('<8sIIIIQ', unicv, 0, b'SCEIRODB', 2, PAGE, 0xFFFFFFFF, 0xFFFFFFFF, len(unicv)-PAGE)
    pfs = destination / 'sce_pfs'
    pfs.mkdir()
    (pfs / 'unicv.db').write_bytes(unicv)
    (pfs / 'files.db').write_bytes(files_database(records, template_header, license_key, values))
    return expected


def align(value, boundary=16):
    return (value + boundary-1) // boundary * boundary


def write_pkg(original, files, output, values, plaintext_sfo):
    """Rebuild item offsets, names, encrypted payload and plaintext SFO metadata."""
    parsed = read_pkg(original, values)
    records = inventory(files)
    prefix = parsed['prefix']
    metadata = parsed['metadata']
    sfo = Path(plaintext_sfo).read_bytes()
    require(sfo[:4] == b'\x00PSF', 'Plaintext package metadata SFO required')
    # Allocate a new plaintext SFO slot after existing metadata, before payload.
    sfo_offset = align(len(prefix))
    prefix.extend(sfo)
    prefix.extend(bytes(align(len(prefix), PAGE)-len(prefix)))
    encrypted_offset = len(prefix)
    struct.pack_into('>II', prefix, metadata[14][0], sfo_offset, len(sfo))
    # Update metadata digests consumed by other PKG inspectors as well.
    if len(metadata[14][1]) == 56:
        prefix[metadata[14][0]+24:metadata[14][0]+56] = hashlib.sha256(sfo).digest()
    names = bytearray()
    count = len(records)
    name_start = count * 32
    name_offsets = {}
    for record in records:
        name_offsets[record['path']] = name_start + len(names)
        encoded = record['path'].encode('ascii')
        names.extend(encoded)
        names.extend(bytes(align(len(names))-len(names)))
    content_start = align(name_start + len(names))
    content_offset = content_start
    table = bytearray()
    for record in records:
        path = record['path']
        table.extend(struct.pack('>IIQQII', name_offsets[path], len(path.encode('ascii')), content_offset,
                                 record['bytes'], 18 if record['directory'] else 3, 0))
        if not record['directory']:
            content_offset = align(content_offset + record['bytes'])
    encrypted_size = content_offset
    struct.pack_into('>I', prefix, 20, count)
    struct.pack_into('>QQQ', prefix, 24, encrypted_offset+encrypted_size, encrypted_offset, encrypted_size)
    struct.pack_into('>II', prefix, metadata[13][0], 0, content_start)
    if len(metadata[13][1]) == 40:
        prefix[metadata[13][0]+8:metadata[13][0]+40] = hashlib.sha256(table+names).digest()
    output = Path(output)
    require(not output.exists(), 'Preserve existing PKG output')
    context = Cipher(algorithms.AES(parsed['key']), modes.CTR(parsed['iv'])).encryptor()
    with output.open('xb') as stream:
        stream.write(prefix)
        stream.write(context.update(table + names))
        position = content_start
        for record in records:
            if record['directory']:
                continue
            with Path(files[record['path']]).open('rb') as source:
                for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
                    stream.write(context.update(chunk))
                    position += len(chunk)
            padding = align(position)-position
            stream.write(context.update(bytes(padding)))
            position += padding
        stream.write(context.finalize())
    require(output.stat().st_size == encrypted_offset+encrypted_size, 'PKG output length mismatch')
    readback = read_pkg(output, values)
    require(len(readback['entries']) == count, 'PKG item table readback failed')
    # Check every outer-encrypted file against its fully rebuilt PFS bytes.
    with output.open('rb') as stream:
        for row in readback['entries']:
            if row['directory']:
                continue
            ctr = (int.from_bytes(parsed['iv'], 'big') + row['offset']//16).to_bytes(16, 'big')
            decoder = Cipher(algorithms.AES(parsed['key']), modes.CTR(ctr)).decryptor()
            stream.seek(encrypted_offset + row['offset'])
            digest = hashlib.sha256()
            left = row['bytes']
            while left:
                chunk = stream.read(min(left, 4*1024*1024))
                require(chunk, 'PKG payload truncated')
                digest.update(decoder.update(chunk))
                left -= len(chunk)
            digest.update(decoder.finalize())
            require(digest.hexdigest() == sha256(files[row['name']]), 'PKG payload hash mismatch')
    return dict(bytes=output.stat().st_size, sha256=sha256(output), members=count,
                encrypted_pfs=True, sony_signed=False, target='Vita3K')
