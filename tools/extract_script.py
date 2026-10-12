"""Preview and export verified four-field UTF-16 script records; sources stay local."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JP = re.compile(r"[\u3041-\u3096\u309d-\u309f\u30a1-\u30fa\u30fd-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9d]")
CONTROL = re.compile(r"#[A-Za-z][0-9]*")


def extract(source):
    glossary = json.loads((ROOT / "work/glossary/characters.json").read_text(encoding="utf-8"))
    names = {jp: character["short_name"] for character in glossary["characters"]
             for jp in character["japanese"]}
    labels_path = ROOT / "work/glossary/speaker-labels.json"
    if labels_path.exists():
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
        names.update({row["japanese"]: row["english"] for row in labels["labels"]})
    entries, file_metrics, failures = [], [], []
    command_count, unresolved_refs = Counter(), []
    for path in sorted(source.glob("*.txt")):
        data = path.read_bytes()
        if data[:2] != b"\xff\xfe":
            raise ValueError("Expected UTF-16LE BOM: " + str(path))
        rows = list(csv.reader(io.StringIO(data.decode("utf-16"), newline="")))
        ids = [row[0] for row in rows if len(row) == 4]
        if len(set(ids)) != len(ids) or any(len(row) != 4 for row in rows):
            raise ValueError("Duplicate record ID or non-four-field row: " + str(path))
        command_path = path.with_suffix(".csv")
        if not command_path.is_file():
            raise ValueError("Missing command stream: " + str(command_path))
        command_bytes = command_path.read_bytes()
        try:
            command_text = command_bytes.decode("utf-8-sig")
            command_encoding = "utf-8-sig"
        except UnicodeDecodeError:
            command_text = command_bytes.decode("cp932")
            command_encoding = "cp932"
        commands = list(csv.reader(io.StringIO(command_text, newline="")))
        refs, select_refs = Counter(), Counter()
        japanese_command_fields = 0
        for command in commands:
            if not command:
                continue
            command_count[command[0]] += 1
            japanese_command_fields += sum(bool(JP.search(field)) for field in command)
            if command[0] == "ADV_MSG" and len(command) > 1:
                refs[command[1]] += 1
            elif command[0] == "ADV_SELECT_TEXT" and len(command) > 1:
                select_refs[command[1]] += 1
        if any(identifier not in ids for identifier in select_refs):
            raise ValueError("Unresolved choice reference: " + str(command_path))
        unresolved_refs.extend({"file": command_path.name, "message_id": message_id}
                               for message_id in refs if message_id not in ids)
        for row_index, (record_id, speaker, text, voice) in enumerate(rows, 1):
            entries.append({"id": path.stem + ":" + record_id,
                            "global_row": len(entries) + 1,
                            "source_file": "data/_scr/" + path.name,
                            "source_row": row_index, "source_record_id": record_id,
                            "source_encoding": "utf-16le-bom", "speaker_jp": speaker,
                            "speaker": names.get(speaker, ""), "jp": text, "en": "",
                            "voice_id": voice, "status": "untranslated",
                            "category": "choice" if select_refs[record_id] else "spoken_text" if speaker else "narration_or_system",
                            "control_codes": CONTROL.findall(text),
                            "speaker_control_codes": CONTROL.findall(speaker),
                            "japanese_text_characters": len(JP.findall(text)),
                            "japanese_speaker_characters": len(JP.findall(speaker)),
                            "adv_msg_references": refs[record_id],
                            "adv_select_references": select_refs[record_id]})
        file_metrics.append({"file": "data/_scr/" + path.name, "rows": len(rows),
                             "sha256": hashlib.sha256(data).hexdigest(), "command_encoding": command_encoding,
                             "japanese_command_fields": japanese_command_fields})
    if not entries:
        raise ValueError("No verified script records found.")
    if len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Duplicate stable IDs across files.")
    texts = [entry["jp"] for entry in entries]
    summary = {"files": len(file_metrics), "records": len(entries),
               "nonempty_records": sum(bool(text) for text in texts),
               "empty_records": sum(not text for text in texts),
               "symbol_only_nonempty_records": sum(bool(text) and not JP.search(text) for text in texts),
               "japanese_bearing_text_records": sum(bool(JP.search(text)) for text in texts),
               "unique_text_strings": len(set(texts)),
               "unique_speaker_text_pairs": len({(entry["speaker_jp"], entry["jp"]) for entry in entries}),
               "japanese_text_characters": sum(entry["japanese_text_characters"] for entry in entries),
               "japanese_speaker_characters": sum(entry["japanese_speaker_characters"] for entry in entries),
               "records_without_adv_msg_reference": sum(entry["adv_msg_references"] == 0 for entry in entries),
               "choice_records": sum(entry["adv_select_references"] > 0 for entry in entries),
               "unreferenced_nonempty_records": sum(bool(entry["jp"]) and not (entry["adv_msg_references"] or entry["adv_select_references"]) for entry in entries),
               "unresolved_adv_msg_references": len(unresolved_refs),
               "japanese_command_fields": sum(item["japanese_command_fields"] for item in file_metrics),
               "all_game_text_total": None,
               "japanese_character_metric": "Kana letters and CJK ideographs; excludes punctuation, prolonged-sound marks, whitespace, controls and Latin text.",
               "coverage": "All four-field records in 462 scenario TXT files; UI binaries/images and manual raster text are separate."}
    return {"schema_version": 1, "project_version": "0.1.2", "language": "en",
            "source_order": "Filename ascending, then CSV record order; not a single narrative route.",
            "summary": summary, "source_files": file_metrics,
            "command_counts": dict(command_count), "unresolved_references": unresolved_refs,
            "entries": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "work/source/archive/assets/data/_scr")
    parser.add_argument("--output", type=Path, default=ROOT / "work/translation/en/corpus.working.json")
    parser.add_argument("--slice-start", type=int, default=1)
    parser.add_argument("--slice-size", type=int, default=80)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--slice-only", action="store_true", help="Create a new slice without overwriting the corpus.")
    args = parser.parse_args()
    result = extract(args.source)
    start = args.slice_start - 1
    end = min(start + args.slice_size, len(result["entries"]))
    if start < 0 or start >= len(result["entries"]) or args.slice_size < 1:
        parser.error("Slice lies outside the corpus.")
    selected = result["entries"][start:end]
    print(json.dumps({"summary": result["summary"], "write": args.write,
                      "slice": {"start": start + 1, "end": end, "rows": len(selected)},
                      "sample": [{key: value for key, value in row.items() if key not in {"jp", "speaker_jp"}}
                                 for row in selected[:3]]}, ensure_ascii=True, indent=2))
    if args.write:
        slice_path = args.output.parent / f"slice-{start + 1:05d}-{end:05d}.working.json"
        if slice_path.exists():
            parser.error("Slice already exists; preserve its translation work.")
        if args.output.exists() and not args.slice_only:
            old = json.loads(args.output.read_text(encoding="utf-8-sig"))
            if any(row.get("en") for row in old.get("entries", [])):
                parser.error("Corpus contains translations; use merge_translation.py instead of overwriting.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not args.slice_only:
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        slice_data = {"schema_version": 1, "project_version": "0.1.2", "language": "en",
                      "slice_start": start + 1, "slice_end": end, "rows_in_slice": len(selected),
                      "rows_examined": 0, "context_before": result["entries"][max(0, start - 10):start],
                      "context_after": result["entries"][end:end + 10], "entries": selected}
        slice_path.write_text(json.dumps(slice_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Local working slice: " + str(slice_path))


if __name__ == "__main__":
    main()
