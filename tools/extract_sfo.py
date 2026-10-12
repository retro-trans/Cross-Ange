"""Read Vita PARAM.SFO metadata; preview Japanese-bearing fields before export."""
import argparse
import json
import re
import struct
from pathlib import Path

JP = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9d]")


def read_sfo(path):
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"\x00PSF":
        raise ValueError("Expected plaintext SFO signature")
    _, key_start, value_start, count = struct.unpack_from("<4I", data, 4)
    fields = {}
    entries = []
    for index in range(count):
        key_offset, fmt, length, capacity, value_offset = struct.unpack_from("<HHIII", data, 20 + index * 16)
        start = key_start + key_offset
        end = data.find(b"\0", start)
        if end < start or value_start + value_offset + length > len(data):
            raise ValueError("Invalid SFO field bounds")
        key = data[start:end].decode("ascii")
        raw = data[value_start + value_offset:value_start + value_offset + length]
        if fmt == 0x204:
            value = raw.rstrip(b"\0").decode("utf-8")
        elif fmt == 0x404 and length == 4:
            value = struct.unpack("<I", raw)[0]
        else:
            value = {"bytes": length, "format": fmt}
        if isinstance(value, str) and JP.search(value):
            entries.append({"id": "param_sfo:" + key, "source_file": "sce_sys/param.sfo",
                            "source_field": key, "source_offset": value_start + value_offset,
                            "source_encoding": "utf-8", "jp": value, "en": "",
                            "japanese_characters": len(JP.findall(value)),
                            "category": "system_metadata_title", "status": "untranslated",
                            "note": "Metadata row only; no game reinsertion has been performed."})
            fields[key] = {"japanese_characters": len(JP.findall(value))}
        else:
            fields[key] = value
    return {"schema_version": 1, "language": "en", "metadata": fields, "entries": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("work/translation/en/metadata.working.json"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = read_sfo(args.path)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    print("Preview only." if not args.write else "Writing local working JSON: " + str(args.output))
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
