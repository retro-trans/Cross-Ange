"""Inventory readable Japanese text files; binary/image/script extraction is separate.

Default is a read-only preview. Candidate counts never claim the full game total.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

JP = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9d]")
EXTENSIONS = {".txt", ".json", ".csv", ".tsv", ".xml", ".ini", ".yaml", ".yml"}


def decode(data):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16"), "utf-16"
    if b"\x00" in data:
        raise ValueError("NUL bytes: needs format-specific extraction")
    for encoding in ("utf-8-sig", "cp932"):
        try:
            text = data.decode(encoding)
            if any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                raise ValueError("Non-text controls: needs format-specific extraction")
            return text, encoding
        except UnicodeDecodeError:
            pass
    raise ValueError("Cannot decode reliably")


def json_strings(value, location="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from json_strings(child, location + "." + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from json_strings(child, f"{location}[{index}]")
    elif isinstance(value, str):
        yield location, value


def inventory(root):
    rows, skipped = [], []
    counts = Counter({"all_files": 0, "readable_text_files": 0,
                      "files_needing_format_or_image_review": 0})
    files = sorted(root.rglob("*")) if root.exists() else []
    for path in files:
        if not path.is_file():
            continue
        counts["all_files"] += 1
        if path.suffix.lower() not in EXTENSIONS:
            counts["files_needing_format_or_image_review"] += 1
            continue
        relative = path.relative_to(root).as_posix()
        try:
            text, encoding = decode(path.read_bytes())
            strings = (list(json_strings(json.loads(text))) if path.suffix.lower() == ".json"
                       else [(f"line:{i}", line) for i, line in enumerate(text.splitlines(), 1)])
        except (ValueError, UnicodeError) as error:
            skipped.append({"source_file": relative, "reason": str(error)})
            continue
        counts["readable_text_files"] += 1
        for location, value in strings:
            jp_chars = len(JP.findall(value))
            if not jp_chars:
                continue
            identity = relative + "#" + location
            rows.append({"id": hashlib.sha256(identity.encode()).hexdigest()[:20],
                         "source_file": relative, "source_location": location,
                         "source_encoding": encoding, "jp": value, "en": "",
                         "japanese_characters": jp_chars, "status": "candidate_unverified"})
    summary = dict(counts)
    summary.update({"candidate_rows": len(rows),
                    "source_root_exists": root.exists(),
                    "unique_candidate_strings": len({r["jp"] for r in rows}),
                    "candidate_japanese_characters": sum(r["japanese_characters"] for r in rows),
                    "rejected_text_files": len(skipped), "full_game_total": None,
                    "coverage": "Readable text candidates only; binary text and images not counted."})
    return {"schema_version": 1, "language": "en", "summary": summary,
            "skipped": skipped, "entries": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path("work/source/decrypted"))
    parser.add_argument("--output", type=Path, default=Path("work/translation/en/inventory.working.json"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = inventory(args.source_root)
    sample = [{k: v for k, v in row.items() if k != "jp"} for row in result["entries"][:3]]
    print(json.dumps({"source_root": str(args.source_root), "summary": result["summary"],
                      "sample_without_japanese": sample, "write": args.write}, indent=2))
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
