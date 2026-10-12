# English translation workflow — 0.1.5

Follow `AGENTS.md` and `BASE_RULES.md`. **Build and consult the glossary before further translation.** The package is decrypted and the glossary foundation is established. Translation has resumed with source-ID mappings and explicit uncertainty flags; new terminology is researched and added as it appears.

## Glossary before drafting

Read [glossary notes](glossary-notes.md), [speaker research](speaker-glossary.md), [equipment research](equipment-glossary.md) and the statuses in `work/glossary/`. Use exact source IDs for UI, exact speaker forms for speakers and sourced character profiles for identity/role. Do not infer gender from a name. Unknown or provisional names must be researched or flagged before affected rows are treated as settled.

```powershell
python tools/glossary_lookup.py --source-id 710
python tools/glossary_audit.py
```

Historical proposed UI suggestions are excluded from lookup. Preserve model codes, IDs, asset labels, paths, placeholders and formatting controls exactly. A plain glossary term is not an inserted string: retain the source's formatting separately. Extend the registry when new terminology appears.

## Verified extraction and assignments

The canonical source is `work/source/archive/assets`, with all 462 TXT/CSV pairs and the parsed UI table in ignored `work/source/ui-strings.json`. Never re-count duplicate partial expansions. [Text inventory](text-inventory.md) separates known structured targets from uncounted image text.

Each dialogue assignment has **80 consecutive rows**, with neighboring context on both sides. Report rows examined versus assigned. Consult [current progress](translation-progress.json) and existing slice filenames before assigning a range. All scenario and UI assignments are complete; previous range reservations are historical. Use new assignments only for an identified correction or review, and never allocate overlapping work.

```powershell
# Substitute a genuinely unassigned start row, preview and inspect first.
python tools/extract_script.py --slice-start <unassigned-row> --slice-only
python tools/extract_script.py --slice-start <unassigned-row> --slice-only --write
```

Settle speaker, listener, referent, tone and the line's response context before drafting. Keep one row per source row and match deliberate sentence cuts/interruption boundaries. Restore grammatical subjects and verbs when context establishes them, keep unknown referents neutral, and flag every retained source omission or uncertain decision. Carry the original force of insults, threats and crude language.

Draft complete spoken English without an artificial byte budget. Visible limits come from measured screens and fonts. Build 0.1.5 relocates binary strings and inserts full dialogue, preserving source line-break controls. The two reported source screens have approximate measurements in `work/ui/reported-text-screens.json`; English layout remains unverified. The build's long-line flags are review candidates, not measured limits or permission to truncate text.

## Review, normalize and export

Use agents for meaning review, then scripts for glossary spelling. Scan the whole corpus for a reported wrong name. Apply agent edits first and normalization second; normalized names enter the do-not-touch list in `name-policy.json`. Exact speaker-label lookup preserves composites and display prefixes. Do not replace words blindly in asset IDs or ordinary vocabulary.

```powershell
# Every mutation script defaults to preview; inspect its actual samples first.
python tools/normalize_names.py work/translation/en/slice-00001-00080.working.json
python tools/validate_translation.py work/translation/en/slice-00001-00080.working.json
python tools/merge_translation.py work/translation/en/slice-00001-00080.working.json work/translation/en/slice-00081-00160.working.json
python tools/strip_jp.py work/translation/en/slice-00001-00080.working.json
```

Only after reviewing the relevant previews, add `--write` for normalization, merge or export. Validate IDs, source fields, controls, row counts and unresolved statuses afterward. `strip_jp.py` removes source/context fields and rejects Japanese leakage in ordinary exported fields. Commit only `*.en.json` copies; extensive Japanese dialogue remains in ignored local working files. Short glossary names/UI terms are allowed.

Completed scenario/UI slices and metadata have English-only exports. `interface.en.json` consolidates all UI rows. Untranslated scenario entries stay in the local working corpus; do not describe blank targets as completed exports. Checkpoints validate all completed slices before merging and preserve pending agent files.

```powershell
python tools/translation_checkpoint.py
# After inspecting the preview:
python tools/translation_checkpoint.py --write
python tools/project_inventory.py
python tools/project_inventory.py --write
```

## Local build and publication

Milestone **0.1.3** completed translation drafts and exports. **0.1.5** inserts all identified structured targets and is installed as a local Vita3K test candidate. See [English insertion checks](english-build.md). Always include `--translations` when building an English candidate; omitting it builds only branding. Preview before writing:

```powershell
python tools/build_branding.py --translations
python tools/test_translation_build.py
python tools/test_build_branding.py
python tools/build_branding.py --translations --write
```

Each successful build automatically increments `VERSION`, updates the changelog and regenerates title/credits. Artifacts belong under `work/output/`. Actual English rendering, layout and further meaning review remain pending. A GitHub release requires an explicit user request and must support Retro Trans Tools.

## Changelog

- **0.1.5 — 2026-10-11:** Inserted and locally installed all structured English targets; verified source structure, relocation, font punctuation and installed replacement bytes.
- **0.1.3 — 2026-10-11:** Resumed dialogue and completed UI drafts after the glossary foundation; added validated, source-free checkpoint/export workflow.
- **0.1.2 — 2026-10-11:** Updated prerequisites to decrypted source, established the glossary-first gate and documented preview/lookup/review/export safeguards.
- **0.1.0 — 2026-10-10:** Initial preparation and encrypted-source workflow.
