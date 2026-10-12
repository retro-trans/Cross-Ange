"""Read-only PKG header/SFO probe; never decrypts or rewrites a package."""
import argparse
import json
import struct
from pathlib import Path


def exact(stream, offset, size):
    stream.seek(offset)
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("Truncated package")
    return data


def sfo_fields(data):
    if data[:4] != b"\x00PSF":
        raise ValueError("Invalid SFO signature")
    _, keys, values, count = struct.unpack_from("<4I", data, 4)
    fields = {}
    for index in range(count):
        key_offset, kind, length, maximum, value_offset = struct.unpack_from(
            "<HHIII", data, 20 + 16 * index
        )
        start = keys + key_offset
        key = data[start:data.index(b"\0", start)].decode("utf-8")
        value = data[values + value_offset:values + value_offset + length]
        if kind == 0x204:
            fields[key] = value.rstrip(b"\0").decode("utf-8")
        elif kind == 0x404 and length == 4:
            fields[key] = struct.unpack("<I", value)[0]
        else:
            fields[key] = {"format": kind, "length": length}
    return fields


def probe(path):
    with path.open("rb") as stream:
        header = exact(stream, 0, 256)
        if header[:4] != b"\x7fPKG" or header[192:196] != b"\x7fext":
            raise ValueError("Not a supported extended PKG")
        be32 = lambda offset: struct.unpack_from(">I", header, offset)[0]
        be64 = lambda offset: struct.unpack_from(">Q", header, offset)[0]
        metadata_offset, metadata_count = be32(8), be32(12)
        result = {
            "file": path.name,
            "size_bytes": path.stat().st_size,
            "declared_size_bytes": be64(24),
            "content_id": header[48:96].split(b"\0", 1)[0].decode("ascii"),
            "item_count_including_directories": be32(20),
            "encrypted_offset": be64(32),
            "encrypted_size": be64(40),
            "key_type": header[231] & 7,
        }
        for _ in range(metadata_count):
            kind, size = struct.unpack(">II", exact(stream, metadata_offset, 8))
            payload = exact(stream, metadata_offset + 8, size)
            if kind == 2:
                result["content_type"] = struct.unpack_from(">I", payload)[0]
            elif kind == 14:
                offset, length = struct.unpack_from(">II", payload)
                result["sfo"] = sfo_fields(exact(stream, offset, length))
            metadata_offset += 8 + size
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--metadata-output", type=Path,
                        help="Optional new JSON file; default only prints a dry-run sample")
    args = parser.parse_args()
    result = probe(args.package)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.metadata_output:
        args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
        with args.metadata_output.open("x", encoding="utf-8") as stream:
            stream.write(rendered + "\n")


if __name__ == "__main__":
    main()
