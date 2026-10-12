"""List CRI CPK/UTF members first; --extract writes only to a fresh directory.

Format reference: https://github.com/kamikat/cpktools/blob/master/cpk/utf.py
CRILAYLA reference: https://github.com/kamikat/cpktools/blob/master/cpk/crilayla.py
"""
import argparse
import collections
import fnmatch
import json
import struct
from pathlib import Path, PurePosixPath


def utf(data):
    if data[:4] != b'@UTF':
        decoded = bytearray(data)
        key = 0x5f
        for i in range(len(decoded)):
            decoded[i] ^= key
            key = key * 0x15 & 255
        data = bytes(decoded)
    if data[:4] != b'@UTF':
        raise ValueError('Invalid UTF signature')
    rows_offset, strings_offset, binary_offset, name_offset, columns, width, count = struct.unpack_from('>IIIIHHI', data, 8)
    rows_offset = (rows_offset & 0xffff) + 8
    strings_offset += 8
    binary_offset += 8
    def string(offset):
        start = strings_offset + offset
        return data[start:data.index(b'\0', start)].decode('utf-8')
    formats = {0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'Q',7:'q',8:'f',9:'d',10:'I',11:'II'}
    def value(kind, position):
        fmt = '>' + formats[kind]
        values = struct.unpack_from(fmt, data, position)
        result = values[0]
        if kind == 10:
            result = string(result)
        elif kind == 11:
            result = data[binary_offset + values[0]:binary_offset + values[0] + values[1]]
        return result, struct.calcsize(fmt)
    schema, position = [], 32
    for _ in range(columns):
        flags, offset = struct.unpack_from('>BI', data, position)
        position += 5
        storage, kind = flags & 0xf0, flags & 15
        constant = 0
        if storage == 0x30:
            constant, size = value(kind, position)
            position += size
        elif storage not in (0x10, 0x50):
            raise ValueError(f'Unknown UTF storage {storage:x}')
        schema.append((string(offset),storage,kind,constant))
    rows = []
    for index in range(count):
        position = rows_offset + index * width
        row = {}
        for name, storage, kind, constant in schema:
            if storage == 0x50:
                result, size = value(kind, position)
                position += size
            else:
                result = constant
            row[name] = result
        rows.append(row)
    return rows


def table(stream, offset):
    stream.seek(offset)
    tag, unknown, length = struct.unpack('<4sIQ', stream.read(16))
    if length > 64 * 1024 * 1024:
        raise ValueError('Unexpected metadata size')
    return utf(stream.read(length))


def crilayla(data):
    size, compressed_length = struct.unpack_from('<II', data, 8)
    accelerator = Path(__file__).with_name('cpk_crilayla.dll')
    import ctypes
    if accelerator.exists() and ctypes.sizeof(ctypes.c_void_p) == 8:
        library = ctypes.CDLL(str(accelerator.resolve()))
        routine = library.cpk_crilayla
        routine.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
        routine.restype = ctypes.c_int
        output = ctypes.create_string_buffer(size + 256)
        result = routine(data, len(data), output, size + 256)
        if result:
            raise ValueError(f'Native CRILAYLA validation failed: {result}')
        return output.raw
    source, bits, available = 16 + compressed_length - 1, 0, 0
    output = bytearray(size + 256)
    output[:256] = data[16 + compressed_length:16 + compressed_length + 256]
    position = len(output) - 1
    def read(count):
        nonlocal source, bits, available
        result = 0
        for _ in range(count):
            if available == 0:
                if source < 16:
                    raise ValueError('Truncated CRILAYLA bits')
                bits = data[source]
                source -= 1
                available = 8
            result = (result << 1) | ((bits >> (available - 1)) & 1)
            available -= 1
        return result
    while position >= 256:
        if read(1) == 0:
            output[position] = read(8)
            position -= 1
        else:
            offset = read(13) + 3
            length = 3
            for count in (2,3,5,8):
                extra = read(count)
                length += extra
                if extra != (1 << count) - 1:
                    break
            else:
                while True:
                    extra = read(8)
                    length += extra
                    if extra != 255:
                        break
            if length > position - 255:
                raise ValueError('Invalid CRILAYLA match length')
            # Copy only already produced bytes; repeated chunks preserve overlap.
            while length:
                chunk = min(length, offset)
                start = position - chunk + 1
                output[start:position + 1] = output[start + offset:position + offset + 1]
                position -= chunk
                length -= chunk
    return bytes(output)


def inventory(stream):
    header = table(stream, 0)[0]
    toc_offset, content_offset = header['TocOffset'], header['ContentOffset']
    base = min(toc_offset, content_offset)
    members = table(stream, toc_offset)
    for row in members:
        name = '/'.join(x for x in (row.get('DirName',''),row['FileName']) if x and x != '<NULL>')
        path = PurePosixPath(name.replace('\\','/'))
        if path.is_absolute() or '..' in path.parts or ':' in name:
            raise ValueError(f'Unsafe member path {name!r}')
        row['path'] = str(path)
        row['absolute_offset'] = base + row['FileOffset']
        stream.seek(row['absolute_offset'])
        row['magic'] = stream.read(8).hex()
        row['compressed'] = row['magic'] == b'CRILAYLA'.hex()
    return header, members


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cpk',type=Path)
    parser.add_argument('--extract',type=Path)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--include',action='append',default=[],help='Restrict extraction to matching member paths')
    args = parser.parse_args()
    with args.cpk.open('rb') as stream:
        header, members = inventory(stream)
        summary = {'members':len(members),'compressed':sum(x['compressed'] for x in members),
                   'stored_bytes':sum(x['FileSize'] for x in members),
                   'expanded_bytes':sum(x['ExtractSize'] for x in members),
                   'extensions':dict(collections.Counter(Path(x['path']).suffix.lower() for x in members)),
                   'sample':members[:12]}
        print(json.dumps(summary,ensure_ascii=False,indent=2))
        if args.manifest:
            args.manifest.parent.mkdir(parents=True,exist_ok=True)
            args.manifest.write_text(json.dumps(members,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if args.extract:
            args.extract.mkdir(parents=True,exist_ok=False)
            for row in members:
                if args.include and not any(fnmatch.fnmatch(row['path'], pattern) for pattern in args.include):
                    continue
                stream.seek(row['absolute_offset'])
                data = stream.read(row['FileSize'])
                if len(data) != row['FileSize']:
                    raise ValueError('Truncated payload')
                if row['compressed']:
                    data = crilayla(data)
                if len(data) != row['ExtractSize']:
                    raise ValueError(f"Size mismatch: {row['path']}")
                target = args.extract.joinpath(*PurePosixPath(row['path']).parts)
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as output:
                    output.write(data)


if __name__ == '__main__':
    main()
