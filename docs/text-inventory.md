# Japanese text inventory — 0.1.3

Checked **2026-10-11**, target language **English**. The package is decrypted and all 4,486 archive members are extracted. All **17,151 identified structured Japanese targets**, containing **335,060 Japanese letters/ideographs**, now have English drafts. Raster text, internal annotations with unverified runtime use, and executable text remain outside this lower bound.

| Category | Japanese targets | Japanese letters/ideographs | English draft status |
|---|---:|---:|---:|
| Scenario dialogue, narration and choices | 13,214 | 288,310 | All drafted and exported |
| Structured UI table | 1,716 | 21,695 | All 1,716 drafted and exported |
| System TITLE and STITLE | 2 | 28 | 2 |
| Battle-partner fields | 861 | 7,914 | All drafted and exported |
| Navigator fields | 1,155 | 13,381 | All drafted and exported |
| Gallery profiles, specs, labels and music titles | 203 | 3,732 | All drafted and exported |
| **Known structured total** | **17,151** | **335,060** | **17,151 drafted; zero remaining identified targets** |
| Texture text | Separate region units | Unknown | 130 readable regions drafted; five marking groups unresolved |
| 24 manual pages | Separate grouped reading units | Unknown | 166 main-text reading blocks drafted |
| Embedded manual screenshots | Separate region units | Unknown | 126 matches to 100 targets; two new labels drafted; 32 microtext notes unresolved |
| Opening movie | Separate region units | Unknown | Two logo regions drafted; 180 sampled frames examined |

The strict character metric counts kana letters and CJK ideographs, excluding punctuation, prolonged-sound marks, whitespace, Latin text and control syntax. Speaker names add **42,348 Japanese letters/ideographs** separately; they are not extra dialogue targets. Duplicate records are retained as insertion workload.

## Scenario evidence

All **462 TXT/CSV pairs** were parsed: **13,277 records**, including 13,257 nonempty records, 20 empty sentinels and 43 nonempty symbol/music/punctuation records. There are **329 choice records**, all referenced by choice commands. Every nonempty text record has a message or choice reference; there are zero unresolved references or duplicate stable IDs.

There are **11,896 distinct Japanese-bearing text strings**, 11,903 distinct strings overall and 12,025 distinct speaker/text pairs. Source order is filename then record order, not one continuous narrative route. Leftover prototype/sample scripts are included in the extraction count; active in-game reachability is not proven for every record.

The command streams contain 2,219 Japanese-bearing fields, mainly labels, expressions and asset references. These are not additional dialogue targets and remain unchanged until their engine function is established. This count is independent of the coincidentally equal 2,219 additional battle/gallery targets.

All 166 scenario assignments have source-free exports. Their 13,277 rows retain the 20 empty sentinels and 43 non-Japanese symbol/music/punctuation records; all 13,257 nonempty rows have targets. The [consolidated scenario export](../work/translation/en/corpus.en.json) preserves stable IDs, order, speakers, voices, controls and command references.

## UI and other assets

The verified `strings.bnd` / `strings_src.bdc` table contains **1,792 rows**, 1,790 nonempty rows and 1,788 named localization entries. Japanese appears in 1,716 rows; there are 1,553 unique Japanese field strings. The 27,791 source characters in Japanese-bearing fields include punctuation, Latin text and controls; that broader number is not the Japanese-letter metric above. Two engine-format rows have second-field pointers and retain their structure.

The additional BND extraction verifies text-column pointers and voice/numeric fields in `BtlFriendEvt.bnd`, `BtlNavigatorEvt.bnd` and `GalleryDef.bnd`. The gallery's model/portrait paths are ASCII game resources and remain unchanged; they are excluded from the 203 human-text targets. Twenty-six existing non-Japanese music titles also remain unchanged. All 2,219 targets are drafted in 29 validated slices and the [consolidated additional export](../work/translation/en/additional.en.json). Battle speaker-group identities and runtime occurrence remain unverified.

The archive contains **1,875 BTX textures** and 100 Live2D JSON files. All decoded textures and eight external save/launcher PNGs received an initial visual scan. [130 texture-region drafts](../work/translation/en/raster.en.json) and [166 manual blocks](../work/translation/en/manual.en.json) cover identified readable text; five texture marking groups remain uncertain. [Manual screenshot coverage](manual-screenshot-coverage.json) records every examined screenshot, matches to existing drafts and specific unreadable microtext. [Two new screenshot labels](../work/translation/en/manual-screenshots.en.json) and [two movie-logo regions](../work/translation/en/video.en.json) have separate exports. The movie was sampled every 0.5 seconds across 90.112 seconds; sampled frames contain no observed Japanese subtitle or credit overlays. Sampling cannot rule out an overlay between frames, and audio is outside written-text scope.

The [additional asset audit](additional-asset-audit.json) checked 627 Japanese labels in character resources, parameters and maps. The [remaining candidate audit](dat-candidate-audit.json) checked 978 heuristic hits across 99 files and 182 effect/portrait annotation fields. Most hits were ASCII or numeric bytes misdecoded as UTF-16. The genuine annotations appear internal, but consumer/runtime evidence is still needed; they were preserved rather than counted as translated player text. Live2D configuration strings likewise remain resource data. UI includes debug, error and prototype rows; actual reachability needs testing. The executable is still an SCE/SELF wrapper and has not received a compiled-text audit.

## Translation status

The [glossary foundation](glossary-notes.md) is indexed: 38 profiles, all 56 nonempty speaker forms, 39 UI character-name slots, 402 equipment names, 42 mecha/target slots and 30 location slots. The [audit](glossary-status.json) passes; 139 equipment names remain provisional even though all now have targets. Glossary records are not completed translation rows.

Translation resumed after the glossary foundation. The registry now contains 941 entries including intentional overlap, and its conflict/coverage audit passes. All 1,792 UI-table rows are examined: 1,716 Japanese targets drafted and 76 English, symbol or format rows preserved. [Current progress](translation-progress.json) and [inventory JSON](text-inventory.json) record complete identified structured draft coverage and retained review flags. Source/control and export checks pass. Full-game completeness, meaning review, live layout, font support and reinsertion remain separate work.

## Reproduction and limits

Canonical expanded assets are `work/source/archive/assets`; do not count duplicate partial extraction folders. [PC decryption](pc-decryption.md), [archive analysis](archive-analysis.md) and [UI analysis](ui-analysis.md) document provenance. Preview `python tools/project_inventory.py` before writing with `--write`; the result is [text-inventory.json](text-inventory.json).

Actual game screenshots, text rectangles, font metrics, relocation and playable testing remain pending. No playable patch, Git commit or GitHub release exists.

## Changelog

- **0.1.3 — 2026-10-11:** Completed all 17,151 identified structured Japanese drafts; added battle/gallery extraction, image/video reading drafts, screenshot matching, remaining-asset classification and source-free consolidated exports.
- **0.1.2 — 2026-10-11:** Replaced encrypted/unknown inventory with verified extraction counts, strict metrics, preliminary draft status and glossary-first coverage.
- **0.1.0 — 2026-10-10:** Recorded the initially readable metadata and encrypted-asset limitations.
