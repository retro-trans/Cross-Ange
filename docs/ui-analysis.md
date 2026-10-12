# Structured UI text investigation — 0.1.2

Checked 2026-10-10 against the canonical extracted assets at `work/source/archive/assets/`. No duplicate partial extraction directories were scanned.

## Verified localization table

`data/_dat/strings.bnd` contains a structured UTF-16LE string table, while `strings_src.bdc` supplies its symbolic keys and numeric IDs. This pairing supports reliable extraction without searching arbitrary binary bytes.

The BND header declares one table, starting at byte 20, with **1,792 rows**. Each row holds two little-endian 32-bit string pointers. Nonzero pointers resolve to aligned, bounded, zero-terminated UTF-16LE strings. The BDC index begins at byte 16 with 16-byte records; each supplies an ID and a relative reference into its ASCII label block. Its terminal `STRINGS_IDX` and `STRINGS_NUM` records are constants, not display-string IDs. They are excluded from label mapping.

Verified totals:

- **1,790 nonempty table rows**.
- **1,773 `STR_` entries**, distinct from other keys and format controls.
- Another **15 `CHAPTER_TITLE_` entries** give **1,788 named localization entries** after excluding ROOT and format controls.
- **1,716 rows containing Japanese letters or CJK characters**. Symbol-only strings are excluded from this count.
- **1,791 mapped symbolic keys**; the final BND row is empty and has no symbolic key.
- Two early format-control rows have a second pointer; none of the second fields contain Japanese text.

The table includes menu prompts, settings, item information, mission titles/descriptions, character names, help text, selection text, and debug/error strings. These counts measure actual structured localization entries, not the number of strings confirmed reachable in normal gameplay. Runtime reachability needs executable-reference and screen validation.

Examples verified through both the pointer table and key index: numeric ID 3 is `STR_YES`, ID 4 is `STR_NO`, and ID 11 is `STR_DIFFICULT_SELECT`. Their source strings are respectively the Japanese Yes, No, and difficulty-selection labels. No extensive Japanese source is reproduced in this document.

Key families include ITM (402), TMG (332), BRIEFING (239), SELECT (210), HANGAR (100), LOUNGE (77), MISSION (66), SHOP (51), CHR (39), and HELP (27). These family counts are based on the symbolic keys; they do not prove how every entry is used on screen. In particular, choices, battle messages, and briefing prose may require scene context rather than isolated menu translation.

## Extraction and source provenance

`tools/ui_table_extract.py` defaults to a read-only summary and eight Japanese entry previews. It was run in this mode and the samples checked before export. The optional export creates a new file and refuses to overwrite an existing one. Input assets are read-only.

The ignored local export is `work/source/ui-strings.json`. Each record preserves:

- Numeric ID and symbolic key.
- BND record offset and each field's exact string offset/byte length.
- BDC label offset and index-record offset.
- Both pointer fields, preserving null fields and format controls.
- Full source text and control markers.

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python tools/ui_table_extract.py work/source/archive/assets/data/_dat
python tools/ui_table_extract.py work/source/archive/assets/data/_dat --output work/source/ui-strings.json
```

The existing source byte lengths are provenance, not English translation budgets. Rebuilding translated tables must relocate enlarged UTF-16LE strings and update pointers rather than truncating text. The precise header size fields and all consumer assumptions still need a round-trip test before a playable patch is produced. Keep the numeric IDs and BDC symbolic keys unchanged. Preserve `#n` and other runtime controls exactly.

## Other inspected assets and remaining uncertainty

Small `_dat/*.bsw` samples are structured resource lists containing paths such as texture and animation asset names; these labels must not be translated. `_ui/*.inc` are button constant definitions. `_ui/*.bnu` samples contain fixed-size numeric/texture-coordinate records, not an established string table. These observations do not prove that every member of those formats lacks text.

`_ui/*.btx` contain textures and may hold image-based UI labels. No texture decoding, visual text count, or actual game screenshot measurement was completed in this bounded investigation. Other `.bnd` files hold gameplay data and may refer to IDs in `strings.bnd`; their schemas and runtime references were not fully reconstructed. No additional translation count is asserted for them. Live display limits, glyph coverage, and the relation between compiled scenario `.bin` assets and editable TXT sources remain separate patch-validation tasks.

## Changelog

- 0.1.2 (2026-10-10): Validated the BND/BDC localization pairing, exported IDs/offsets and counted Japanese rows. The first 80 table records have 61 Japanese drafts and 19 unchanged records; runtime concatenation and mission/chapter ambiguities are flagged. No playable build or release.
