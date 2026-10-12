"""Export translation JSON without Japanese source text. Preview by default."""
import argparse
import json
import re
from pathlib import Path

JP = re.compile(r"[\u3041-\u3096\u309d-\u309f\u30a1-\u30fa\u30fd-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9d]")
SOURCE_KEYS = {"jp", "ja", "japanese", "source_text", "text_jp", "source_context", "context_before", "context_after"}
PATH_KEYS = {"source_file", "asset_path", "preserved_tokens"}


def strip(value, location="$", key=""):
    if isinstance(value, dict):
        return {k: strip(v, location + "." + k, k)
                for k, v in value.items()
                if k.lower() not in SOURCE_KEYS and not k.lower().endswith("_jp")}
    if isinstance(value, list):
        return [strip(v, f"{location}[{i}]", key) for i, v in enumerate(value)]
    if isinstance(value, str) and JP.search(value) and key not in PATH_KEYS:
        raise ValueError(f"Japanese remains in exported field {location}; move source into 'jp'.")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--write", action="store_true", help="Write after reviewing preview.")
    args = parser.parse_args()
    for path in args.paths:
        if path.name.endswith(".en.json"):
            parser.error("Input must be a local working JSON, not an English export.")
        original = json.loads(path.read_text(encoding="utf-8-sig"))
        clean = strip(original)
        base = path.stem[:-8] if path.stem.endswith(".working") else path.stem
        target = path.with_name(base + ".en.json")
        entries = clean.get("entries", []) if isinstance(clean, dict) else clean
        print(json.dumps({"input": str(path), "output": str(target),
                          "rows": len(entries) if isinstance(entries, list) else None,
                          "sample": entries[:3] if isinstance(entries, list) else clean,
                          "write": args.write}, ensure_ascii=True, indent=2))
        if args.write:
            target.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
