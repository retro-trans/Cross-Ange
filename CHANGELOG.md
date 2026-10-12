# Changelog

### 0.1.13 — Restore small-download PKG Automatic

- Verification: the frozen local tools 0.5.16 app downloaded the small published ZIP with an empty cache and rebuilt the exact native-verified English PKG; the actual Automatic UI worker passed too. Both native installations verified all 48 files, originals/licenses stayed unchanged, and the 257-test suite passed with four platform skips. See PKG-REBUILD-VALIDATION.json.

- Restored original-PKG Automatic using small component patches and local decryption/re-encryption. Requires the same game's matching local work.bin/.rif during patching and installation; no licenses are bundled/downloaded. Private profile discovery uses existing GitHub CLI access.
- Whole-PKG xdelta remains withdrawn. Manual CPK patching, generic hardware rePatch, safe workspace cleanup and unchanged originals/licenses/emulator data remain supported. This is a local tools update; no tools release/source push is authorized.
- Cross Ange translation bytes, game version/footer/credits and repository privacy remain unchanged. The refreshed translation ZIP is about 5.4 MB; official native runtime download and 6 GB temporary space are separate requirements. Gameplay and hardware testing remain outstanding.

### 0.1.13 — Restore installed CPK patching

- Verification: the actual Apply xdelta UI reproduced the complete English CPK, metadata and extras matched their expected identities, and all seven restored component downloads were verified after upload. The replacement app passed its 251-test suite with four platform skips and frozen startup. Prior local app bundles are archived outside active build outputs.

- At the user's request, restored the approximately 5.35 MB CPK delta, optional metadata delta and credits/font attribution extras. Users install their original licensed game in Vita3K, close it, patch installed files to new outputs and replace with backups.
- Removed the approximately 945 MB whole-PKG ZIP/profile and their current verification assets. Keep the repository/release private, matching licenses required for original installation and hardware extraction, and preserve all historical proof records.
- Withdrew local whole-PKG tools builds 0.5.12–0.5.14. Published tools 0.5.4 still handles Apply xdelta; local replacement source 0.5.15 removes PKG patch options and retains hardware rePatch. No new tools release is published.
- Component output identities and native-verified English game bytes remain unchanged; version/footer/credits remain 0.1.13. Full gameplay and physical-Vita testing remain outstanding.

### 0.1.13 — Restore private access

- Restored repository and existing release privacy at the user's request because the approximately 945 MB whole-PKG download is too large. Updated current instructions to require repository access through GitHub CLI sign-in.
- Preserved the game version, all ten release assets and prior public verification as historical evidence. This visibility change does not reduce the download size or publish a new tools build.

### 0.1.13 — Public Automatic testing

- Made the repository and existing game release public at the user's request. Automatic downloads no longer require GitHub sign-in; current instructions recommend the local tools 0.5.14 build for testing.
- Verified anonymous organization discovery and both matching release profiles/bundles. Hardware used a fresh downloaded ZIP; whole-PKG reused the previously verified large ZIP cache. Preserved all ten asset identities, game bytes and version; no new tools release was published.
- Retained prior private-download evidence and added `docs/public-release-0.1.13.json`. Matching game licenses remain required for installation and hardware extraction; whole-PKG patching remains license-free.

### 0.1.13 — Hardware rePatch support

- Added a separate rePatch profile/ZIP for PCSG00597 v01.00 and generic hardware discovery in the local tools 0.5.14 build. The overlay uses the existing English archive and includes generated credits/font attribution, preserving the original executable and authentication.
- Explicitly require this game's matching work.bin for installation and for hardware PKG extraction; another title's license is unsuitable. Whole-PKG patching remains license-free. No licenses or full archives are published.
- The hardware patch download is about 5.4 MB and generates an approximately 902 MB archive overlay locally. Game bytes and version stay 0.1.13; physical-Vita gameplay and manual credits are not verified.
- The frozen local tools 0.5.14 app passed the published automatic hardware route, including isolated native PKG extraction and all three overlay-file hashes, preserving the original and license. Its suite passed 270 tests with four platform-specific skips. The existing whole-PKG assets remain unchanged; tools publication is not part of this update.

### 0.1.13 — Whole-PKG release distribution

- Updated the existing private game release to `VITA-PKG-XDELTA.json` and one whole-PKG xdelta ZIP. Automatic in the local Retro Trans 0.5.12 build downloads the ZIP and patches the original encrypted PKG without a license. Manual patching uses the delta extracted from that same ZIP. Vita3K still requires the user's matching license during installation.
- Removed the CPK/component deltas, component manifest, old license-based profile, separate extras and superseded release verification assets. Updated the README, installation instructions and release packager for the PKG-only player route.
- Verified a fresh published download and complete patch through the frozen app, then the actual Automatic UI worker. Both outputs match the previously native-verified 48-file English package, with the original unchanged. Published `AUTOMATIC-VALIDATION.json` records these checks; gameplay and physical-Vita testing remain outstanding.
- Disclosed the approximately 945 MB download. Preserved game bytes, 0.1.13 branding and repository privacy. This distribution update does not publish or push the local tools 0.5.12 build.

### 0.1.13 — Local whole-PKG test for tools 0.5.12

- The local frozen tools executable passed startup checks and applied the whole-PKG ZIP without a license argument. Output matches the previously native-verified 48-file build exactly, and the original PKG is unchanged. The app suite passed 260 tests with four platform-specific skips; local proof is in `work/output/cross-ange-0.1.13/whole-pkg-local/RT-0.5.12-VALIDATION.json`.
- Prepared a local VITA-PKG-XDELTA.json and whole-PKG test ZIP for Retro Trans Tools 0.5.12. The player patcher uses encrypted bytes and does not need a license; Vita3K installation still requires the user's matching license.
- Retained the existing game bytes and 0.1.13 branding. The test delta is 944,873,399 bytes and reproduces the previously verified English package exactly. It remains local; no game or tools release update is requested.

### 0.1.13 — Withdraw the recommended tools release

- Removed Retro Trans Tools v0.5.11 and its downloads at the user's request because its PKG flow required a license during patching. Removed that recommendation from current game documentation and release instructions.
- Retained this private game release, its existing translation assets and historical verification records. The whole-PKG route without a patch-time license is not yet published; the remaining tools v0.5.4 release does not support Automatic Vita PKG patching.
- A local whole-PKG delta round trip reproduced the verified English package exactly, but the delta was 944,873,399 bytes. It was kept local because it is almost the entire package; it is not a release asset.

### 0.1.13 — ACE-3 release presentation

- Reformatted the existing private release using ACE-3's section order: Apply, changes since the previous build, release status, included content, translation method, acknowledgements, source code and contribution links. Added a manual component-patch table and commands, and preserved the verified PKG identities and Automatic instructions.
- Updated release presentation only; retained the game version, all patch assets, verification records and repository privacy.

### 0.1.13 — Published Retro Trans 0.5.11 workflow

- Updated the README, PKG instructions and existing private release notes to use the published Retro Trans 0.5.11 Windows app: Automatic takes the original PKG and matching local license, then downloads the translation ZIP on Patch. Kept the Vita tab's local ZIP override.
- Added supplementary published-app verification without changing the game patches, profile, branding or build version. The app release workflow passed 247 tests with four platform-specific skips, standalone checks and a real packaged update; the published executable's conversion record covers all 48 installed game files.
- Retained the original 0.5.8 verification record and all existing game assets. The game repository and release remain private; no game package or license is distributed.

### 0.1.13 — Generic Retro Trans integration verification

- Verified the local Retro Trans 0.5.8 Windows app against the release ZIP and original PKG: native installation verified all 48 game files, and output matched the standalone package exactly.
- Verified standard Automatic recognition and both complete-file patch outputs. Recorded the 226-test Retro Trans suite, with four platform-specific skips, and generic profiles for a second title.
- Added `RETRO-TRANS-VALIDATION.json` to the private release assets. Retro Trans app publication, physical-Vita installation and full gameplay testing remain pending.
- Published the explicitly requested private v0.1.13 release and downloaded all 11 uploaded assets again; sizes, SHA-256 identities, standard manifests and the generic Vita ZIP profile passed. Repository visibility remains private.

## 2026-10-12 — v0.1.13 private release preparation

- User requested changing the release to original-PKG input and adding a generic Vita option to sibling `../retro-trans-tools`. Prepared a declarative VITA-PKG profile and a verified ZIP containing only translation deltas, credits and font attribution; retained the standard Automatic/Apply xdelta assets.
- Retro Trans 0.5.8 selects a destination and reads game identities and inventories from release profiles. New supported games need profiles rather than game-specific UI. Added authenticated outer/inner path checks and output-installation verification; retained hardware rePatch and its Z3 fallback.
- The sibling app suite passed 226 tests with four platform-specific skips. Prepared a local Windows app build; its source remains local, including preserved earlier diagnostics changes. No Retro Trans app publication is implied.
- Exported all 226 English-only catalogs before committing. No Japanese scripts, full PKGs, original artwork, executables or licenses enter Git or the translation release. Repository privacy remains unchanged.

## 0.1.13 — 2026-10-12 — Direct PKG patching for Vita3K

- Added `tools/patch_pkg.py`: original Japanese PKG plus the user's matching NoNpDrm license produces a new English PKG, without an existing game installation or manual CPK editing. Accepts prepared local builds or the existing Retro Trans-compatible translation delta/extras assets.
- Rebuilds native encrypted PFS sectors, file database, sector integrity tables, PKG offsets and plaintext metadata. Validates all encrypted payloads, then performs an isolated native Vita3K install and exact inventory/hash comparison before saving the output. Preserves original PKG, license, real emulator installation and saves.
- Incremented to 0.1.13 and regenerated title footer and credits together. Retained 0.1.12 translation content, GenEi LateGo v2 Medium and OFL attribution. Repacked 483 archive members; preserved original payloads and 4,003 unaffected TOC rows.
- Eight package regressions and twenty existing translation/font/tutorial/branding checks passed. Confirmed compatibility against original PFS header authentication and byte-identical original CPK sector encryption, rather than relying only on inverse round trips.
- The 0.1.13 PKG installed successfully in isolated Vita3K; all 48 decrypted game files matched the English build. Separately converted the existing 0.1.12 release assets through the player route, with the same successful installation and 48-file verification. Recorded non-secret reports and repeatable setup in `docs/pkg-patching.md`.
- Custom PKGs are for Vita3K, are not Sony-signed, and still need the matching license at installation. Gameplay of the new PKG and physical-Vita behavior are untested. Existing translation/layout limitations, remaining raster/manual/video text and the duplicate Naomi eye-animation tile remain unresolved.
- Repository remains private following the user's request to unpublish. Full PKGs stay local; no 0.1.13 GitHub release was created or published.

## 2026-10-12 — v0.1.12 public release

- Adopted retro-trans/ACE-3's README and release presentation: applying patches, review status, source workflow, repository layout and credits.
- Prepared verified xdelta packaging for the existing 0.1.12 archive and system-title files, using Retro Trans's schema-2 grouped solution. Credits and font-license additions are separate generated extras. Game bytes and build version are unchanged.
- Exported all 226 local working translation files with `tools/strip_jp.py`; public sources exclude Japanese scripts, game binaries, artwork, packages and license keys. Retained permitted short glossary names/UI terms and added project MIT licensing alongside the existing font OFL attribution.
- Both release deltas passed complete-file round trips. Retro Trans's grouped Automatic implementation recognized both source files and applied/verified both outputs locally; the extras ZIP passed readback. Recorded the manifest and compatibility report. Created public retro-trans/Cross-Ange and published v0.1.12 under binhlt0402 after downloading and hash-verifying all eight uploaded assets. The Retro Trans catalog refresh succeeded; independently verified the published two-component solution and manifest in the central catalog. Game bytes and the v0.1.12 tag are unchanged.

## 0.1.12 — 2026-10-12 — Remaining tutorial artwork and battle-result spacing

- Inserted seven previously drafted tutorial textures: EBG_108, EBG_110–112 and ECG_043–045. All ten identified tutorial pictures now have English text, including embedded sample menu headings, mission names, captions and choices. Added 49 bounded text rectangles covering 41 source regions.
- Shortened battle-result time labels to `Left` and ` s`, retaining canonical drafts and numeric fields. Checked the fixed label spaces from the user capture; retained the briefing/unit label fixes.
- Retained GenEi LateGo v2 Medium and validated all native glyph terminators. Preserved original tutorial palettes, headers, diagrams, controller icons and all indices outside explicit text bounds. Visually inspected decoded native previews.
- Twenty translation/font/UI/texture/branding checks passed. Repacked and independently checked all 483 replacement archive members; preserved original payloads and 4,003 unaffected TOC rows. Installed and hash-verified all 48 game files, then read back all 46,048 native glyph records and 13 display adaptations. Preserved the prior 0.1.11 app and saves.
- Incremented version to 0.1.12; regenerated title footer and credits from that version. New result/tutorial layout still needs a live game check. Other raster regions, original manual prose and video remain pending; no GitHub release.

## 0.1.11 — 2026-10-12 — Briefing and unit-label spacing

- Thirteen translation/font/layout checks and three branding checks passed. Compared all UI fields against 0.1.10: exactly 11 fields changed; all other UI fields and translation members are identical. Checked all 16 shared stat-label widths and both condition headings against screenshot-derived column limits.
- Installed and hash-verified all 48 files; independently read back 476 archive replacements, 46,048 native glyph records and 11 compact UI fields. The v0.1.11 title footer was observed. The user stopped Computer Use before reaching briefing panels; those panels still need a live check. See `docs/briefing-label-layout.md`.
- Built a local test candidate with white, right-aligned `v0.1.11` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 476 archive members, preserving original payloads and 4,010 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, non-layout controls, nulls and relocation footers.
- Replaced Latin glyphs in both game fonts with GenEi LateGo v2 Medium from the requested Genei Latin package; installed matching native proportional widths, including narrower spaces and control-boundary aliases. Retained unrelated glyphs. Included font copyright and OFL 1.1 license.
- Validated all native font-record terminators; retained GenEi proportional widths and control-boundary aliases. Adjusted the colon to Latin dot spacing using GenEi period dots.
- Reflowed dialogue by glyph advances to a 670-pixel line limit. Long records use native 80% text size and at most three lines; speaker names are fitted to 212 pixels. Canonical wording, IDs, voices and non-layout commands are retained. Rendered layout still requires an in-game test.
- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.
- Reworded the classroom peace explanation to fit at normal font size without losing its meaning.
- Replaced Japanese labels and embedded sample captions on the room-menu, battle-controls and battle-HUD tutorial images (EBG_109, EBG_106, EBG_107). Preserved native palettes and all pixels outside the text regions.
- Inserted all 15 unique chapter/prologue headings in both title atlas variants: 30 title regions. Matched save-menu naming, preserved English chapter labels/numbers, native animation and support artwork, and fitted complete English headings to the original sampling rectangles.
- Fitted shared mission-condition and unit-stat labels to the columns measured in actual game captures; used compact display wording while retaining canonical drafts. Separated the numeric time limit from its appended English unit.
- New changes need an in-game check. Other raster artwork, movie and original manual prose remain pending. The duplicate Naomi eye-animation tile is under investigation. No GitHub release.

## 2026-10-12 — Local launch repair (existing 0.1.10 build)

- Repaired the Play shortcut launch by restoring the matching, already downloaded Vita3K 4154 distribution; preserved the prior 4095 executable, changed resources and settings in a local repair backup. The older executable stopped while reading the newer settings.
- The configured C: data directory was empty after user cleanup. Restored Sony firmware/modules, system fonts, the matching local license and all 48 game files to `E:\Emu\vita3k\fs`; all installed game files were hash-verified. Controls were retained. Deleted saves were not recovered.
- Launched through `Play Cross Ange.lnk` and visually confirmed the English difficulty-selection screen at about 30 FPS. Left the game running there. This verifies startup, not every translated scene or chapter-title animation.
- Updated current installation records and testing paths. Reinstalled existing v0.1.10 without generating a new game build or publishing a release.

## 0.1.10 — 2026-10-11 — All chapter and prologue title cards

- Installed in the closed Vita3K; hash-verified 48 files and independently read back all 476 replacement members, 46,048 native font records and five unchanged chapter support assets. Eighteen relevant checks passed. New title cards await an in-game check.
- Preserved the prior 0.1.9 app; moved an earlier 48-file test backup to E: with verified hashes to make room on C:. Updated its installation record with the recoverable backup location.
- Built a local test candidate with white, right-aligned `v0.1.10` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 476 archive members, preserving original payloads and 4,010 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, non-layout controls, nulls and relocation footers.
- Replaced Latin glyphs in both game fonts with GenEi LateGo v2 Medium from the requested Genei Latin package; installed matching native proportional widths, including narrower spaces and control-boundary aliases. Retained unrelated glyphs. Included font copyright and OFL 1.1 license.
- Validated all native font-record terminators; retained GenEi proportional widths and control-boundary aliases. Adjusted the colon to Latin dot spacing using GenEi period dots.
- Reflowed dialogue by glyph advances to a 670-pixel line limit. Long records use native 80% text size and at most three lines; speaker names are fitted to 212 pixels. Canonical wording, IDs, voices and non-layout commands are retained. Rendered layout still requires an in-game test.
- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.
- Reworded the classroom peace explanation to fit at normal font size without losing its meaning.
- Replaced Japanese labels and embedded sample captions on the room-menu, battle-controls and battle-HUD tutorial images (EBG_109, EBG_106, EBG_107). Preserved native palettes and all pixels outside the text regions.
- Inserted all 15 unique chapter/prologue headings in both title atlas variants: 30 title regions. Matched save-menu naming, preserved English chapter labels/numbers, native animation and support artwork, and fitted complete English headings to the original sampling rectangles.
- New changes need an in-game check. Other raster artwork, movie and original manual prose remain pending. The duplicate Naomi eye-animation tile is under investigation. No GitHub release.

## 0.1.9 — 2026-10-11 — English text and tutorial artwork

- Installed in the closed Vita3K; verified all 48 file hashes, independently read back all 474 replacement members and validated all 46,048 installed font records. Twenty-two checks passed. Prior app preserved; new changes await runtime review.
- User 0.1.8 captures confirmed the prior startup fix and progress into battle. Traced the extra Naomi tile to eye animation; its cause remains unresolved. Prepared a hash-guarded original/English comparison with restoration shortcuts; desktop runtime automation failed to initialize.
- Built a local test candidate with white, right-aligned `v0.1.9` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 474 archive members, preserving original payloads and 4,012 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, non-layout controls, nulls and relocation footers.
- Replaced Latin glyphs in both game fonts with GenEi LateGo v2 Medium from the requested Genei Latin package; installed matching native proportional widths, including narrower spaces and control-boundary aliases. Retained unrelated glyphs. Included font copyright and OFL 1.1 license.
- Validated all native font-record terminators; retained GenEi proportional widths and control-boundary aliases. Adjusted the colon to Latin dot spacing using GenEi period dots.
- Reflowed dialogue by glyph advances to a 670-pixel line limit. Long records use native 80% text size and at most three lines; speaker names are fitted to 212 pixels. Canonical wording, IDs, voices and non-layout commands are retained. Rendered layout still requires an in-game test.
- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.
- Reworded the classroom peace explanation to fit at normal font size without losing its meaning.
- Replaced Japanese labels and embedded sample captions on the room-menu, battle-controls and battle-HUD tutorial images (EBG_109, EBG_106, EBG_107). Preserved native palettes and all pixels outside the text regions.
- New changes need an in-game check. Other raster artwork, movie and original manual prose remain pending. The duplicate Naomi eye-animation tile is under investigation. No GitHub release.

## 0.1.8 — 2026-10-11 — Terminate native font records

- Installed into the closed Vita3K; verified all 48 file hashes and independently read back all 471 replacement members. All 46,048 installed glyphs passed native termination validation. Thirteen build checks passed. Preserved the previous app; startup retest is pending.
- Built a local test candidate with white, right-aligned `v0.1.8` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 471 archive members, preserving original payloads and 4,015 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, non-layout controls, nulls and relocation footers.
- Replaced Latin glyphs in both game fonts with GenEi LateGo v2 Medium from the requested Genei Latin package; installed matching native proportional widths, including narrower spaces and control-boundary aliases. Retained unrelated glyphs. Included font copyright and OFL 1.1 license.
- Included the zero-token terminator required by the native glyph reader; validated every glyph with its termination rules. This fixes the 0.1.7 font-record overrun implicated by the black-screen crash before difficulty selection.
- Reflowed dialogue by glyph advances to a 670-pixel line limit. Long records use native 80% text size and at most three lines; speaker names are fitted to 212 pixels. Canonical wording, IDs, voices and non-layout commands are retained. Rendered layout still requires an in-game test.
- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.
- English layout needs in-game review; raster artwork, movie and original manual prose remain untranslated in this candidate. No GitHub release.

## 0.1.7 — 2026-10-11 — Genei font and fitted English dialogue

- User startup test failed with a black screen before difficulty selection. Vita3K logged font-path memory errors and stack corruption. The native glyph decoder rejected 394 new records because they lacked the separate zero-token terminator; 0.1.8 corrects the encoder.
- Installed in the existing Vita3K after it was closed. Verified all 48 files and independently read back all 471 replacement archive members; confirmed the bundled font license. Preserved the previous 0.1.6 app. Twelve build checks passed. Runtime font/line-fit confirmation is pending.
- Built a local test candidate with white, right-aligned `v0.1.7` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 471 archive members, preserving original payloads and 4,015 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, non-layout controls, nulls and relocation footers.
- Replaced Latin glyphs in both game fonts with GenEi LateGo v2 Medium from the requested Genei Latin package; installed matching native proportional widths, including narrower spaces and control-boundary aliases. Retained unrelated glyphs. Included font copyright and OFL 1.1 license.
- Reflowed dialogue by glyph advances to a 670-pixel line limit. Long records use native 80% text size and at most three lines; speaker names are fitted to 212 pixels. Canonical wording, IDs, voices and non-layout commands are retained. Rendered layout still requires an in-game test.
- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.
- English layout needs in-game review; raster artwork, movie and original manual prose remain untranslated in this candidate. No GitHub release.

## 0.1.6 — 2026-10-11 — Protect English dialogue control boundaries

- Installed into the existing Vita3K; all 47 files were hash-verified and all 471 archive replacements independently read back. Preserved the 0.1.5 app as a backup. Dialogue rendering awaits a new in-game test.
- Built a local test candidate with white, right-aligned `v0.1.6` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 471 archive members, preserving original payloads and 4,015 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, control order, nulls and relocation footers.
- Protected scenario control scans with fullwidth Latin codepoint aliases that render as the original ASCII glyphs and use matching advances in both fonts and the kerning table. This addresses the 0.1.5 dialogue panel disappearing and text moving to the screen origin.
- Kept the unquoted scenario format using those aliases for commas and quotes; used ASCII display aliases for eleven unsupported accent occurrences. Shortened seven speaker labels to stay below the 32-word name buffer. Canonical drafts are unchanged.
- English layout needs in-game review; raster artwork, movie and original manual prose remain untranslated in this candidate. No GitHub release.

## 0.1.5 — 2026-10-11 — Structured English text inserted

- User runtime test found dialogue and speaker text at the screen origin, with the dialogue panel missing, from the first classroom line. Difficulty selection displays normally. Recorded the original capture and issue bounds; 0.1.5 is not a passing layout candidate.
- Installed into the user's existing Vita3K after the emulator was closed; verified all 47 installed file hashes and independently read back all 470 replacement archive members. Preserved the previous 0.1.4 app, configuration and license backups. Confirmed the reported difficulty and classroom targets are English in the installed files; rendered English layout remains untested.
- Built a local test candidate with white, right-aligned `v0.1.5` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked 470 archive members, preserving original payloads and 4,016 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Inserted all 17,151 identified structured targets: 13,214 Japanese scenario records across 462 files, 1,716 UI fields, 2,219 battle/gallery fields and two system titles; included English speaker labels.
- Relocated UTF-16 BND strings with updated pointers; preserved source record IDs, voice IDs, control order, nulls and relocation footers.
- Kept the unquoted scenario format using dedicated Unicode punctuation slots with the original ASCII glyphs in both fonts. Used ASCII display aliases for eleven unsupported Latin-1 accent occurrences; original drafts are unchanged.
- English layout needs in-game review; raster artwork, movie and original manual prose remain untranslated in this candidate. No GitHub release.

## 0.1.4 — 2026-10-11 — Title footer and translation credits

- Installed this existing test build into the user's `E:\Emu\vita3k` data directory, verified all 47 installed file hashes and matching local license, confirmed Vita3K recognizes PCSG00597, and created launch shortcuts. Reused the installed firmware/fonts and preserved original game files and configuration backup. Installation did not create a new build version.
- Built a local title-branding test candidate with white, right-aligned `v0.1.4` above `github.com/retro-trans`.
- Added a Retro Trans credits page as the final game-manual page; retained original copyright text and pixels.
- Automatically incremented the build version; regenerated the footer and credits from the same version.
- Repacked two title assets, preserving all other archive payloads and 4,484 unaffected TOC rows; verified replacement bytes and relocated ETOC.
- Runtime title layout, manual-page access and archive loading still require an in-game test. English translation drafts are not inserted in this branding candidate. No GitHub release.

## 0.1.3 — 2026-10-11 — Translation resumed after glossary foundation

- Drafted all 1,716 Japanese UI-table entries: menus, room/location prompts, mission briefings and conditions, names, equipment, branching conversations, treatment reactions, settings and button legends. Preserved all 1,792 rows, including 76 unchanged English, symbol and format rows.
- Validated exact UI IDs, source fields, pointers, nulls and formatting-control order; exported 23 source-free slices and the consolidated `interface.en.json`.
- Completed all 13,214 Japanese scenario targets in 166 assignments covering 13,277 source rows. Retained 20 empty sentinels and 43 non-Japanese symbol/music/punctuation rows. Read neighboring context and recorded examined/assigned counts, uncertain referents, route contradictions, wordplay and retained interruptions; consolidated `corpus.en.json`.
- Verified and drafted another 2,219 BND text targets: 861 battle-partner fields, 1,155 navigator fields and 203 gallery profiles, specifications, outfit/event labels and music titles. Preserved voice words, numeric records, pointers and ASCII resource paths. Exported 29 slices and consolidated `additional.en.json`; the known structured total is now 17,151 targets and 335,060 Japanese letters/ideographs, all drafted.
- Added provisional literal/phonetic proposals for 21 previously unmapped equipment names. All 402 are mapped, with 139 explicitly provisional; these are not claims of canonical English spellings.
- Extended the glossary with observed dialogue terms and generic roles. Fixed auditing to distinguish integer UI slots from scenario occurrence references, where one dialogue row can contain multiple terms.
- Added preview-first UI authoring and checkpoint tools, consolidated completed dialogue drafts, refreshed inventory reporting and checked normalization after meaning review.
- Read all 24 illustrated manual pages; drafted 166 reading blocks for main prose, headings, captions, profiles, credits, controls and terminology. Added original voice-credit spellings, Discord Phaser and the No Makeup nickname before drafting. Matched 126 visible-text instances to 100 translation targets across 45 embedded screenshots, added two platform load-label drafts, and retained 32 unreadable microtext notes. Corrected the Freeze Bullet defeat-bonus condition and Norma's possible destruction of society.
- Decoded and initially inspected all 1,875 textures: 1,104 indexed and 771 GXT images, including all 794 successfully decompressed wrappers. Added 130 raster reading regions covering notices, logos, IOU heading, chapter atlases, tutorial prose/labels, emblems, save/launcher credit and Naomi's swimsuit tag. Five blurred/tiny/uncertain marking groups remain unresolved. Source hashes and approximate texture coordinates validate; original artwork is unchanged.
- Inspected 180 sampled opening-movie frames at 0.5-second intervals; drafted its two Japanese logo regions with source hash, time range and coordinates. Original video/audio remains unchanged.
- Expanded the glossary to 941 indexed records including intentional overlap. Applied independent meaning corrections, then canonical Libertus/Para-mail/mail-rider and source-confirmed DRAGON casing. Fixed normalization at formatting-control boundaries and checked control preservation.
- Classified all remaining DAT heuristic candidates from actual bytes: 978 hits in 99 files, including 852 decoding artifacts and 126 annotation matches. Documented 627 Japanese character/parameter/map labels and 182 effect/portrait annotation fields as likely internal with runtime consumers unresolved; no resource identifiers changed.

Unclear artwork, screenshot microtext, further meaning review, executable text audit, measured game layout, font support and reinsertion remain pending. No playable build, Git commit or GitHub release was created.

## 0.1.2 — 2026-10-10–11 — Decryption, inventory and glossary foundation

- Successfully decrypted the package with the matching user-supplied PCSG00597 license using isolated portable Vita3K; preserved originals and kept license values local.
- Extracted all 4,486 CPK members, including 2,927 CRILAYLA-compressed members; verified expanded sizes and native/Python text agreement.
- Parsed all 462 scenario/command pairs: 13,277 records, 13,214 Japanese targets, 329 choices. All nonempty records have message/choice references.
- Reconstructed the BND/BDC localization table: 1,792 rows, 1,788 named entries, 1,716 Japanese entries; preserved IDs, pointers and null fields.
- Counted 14,932 known Japanese structured targets and 310,033 Japanese letters/ideographs; texture and manual raster text remain uncounted.
- Prioritized glossary completion before further translation as requested. Expanded to 38 character profiles and all 56 nonempty speaker forms, including composites, control prefixes, generic roles and prototype labels; covered all 39 UI character-name slots.
- Indexed all 402 equipment names, 42 mecha/target slots and 30 location labels; added recurring world, stat, control, result and equipment-component terminology. Equipment includes 381 mappings (118 provisional) and 21 explicitly unresolved names.
- Verified Howitzer and Singularity spelling; recorded Sylphis as a clan; confirmed Vulcan/Riza gender evidence and Riza/Jurai names. Kept Eunice prototype links and concealed identities uncertain.
- Added source-ID glossary lookup and coverage/conflict audit. Reconciled ten duplicate UI-label disagreements; audit passes. The registry has 835 entries including intentional overlap, excluding 20 historical proposed UI suggestions.
- Drafted and reviewed 159 scenario records, 61 UI entries and two system titles; preserved one empty scenario sentinel and 19 unchanged UI records. Recorded route changes, source contradictions, interruptions, wordplay and layout uncertainties.
- Added preview-first extraction, source/control validation, safe corpus merging, glossary normalization and source-free inventory generation. Only metadata has an English export; existing scenario/UI drafts remain preliminary local working files pending glossary review.
- Confirmed readable manual images; actual game layout, font metrics and relocation/reinsertion remain pending.

No playable build, Git commit or GitHub release was created.

## 0.1.1 — 2026-10-10 — PC decryption preparation

- Downloaded the official psvpfstools Windows decryptor and verified its help output.
- Downloaded and checked the official Vita3K Windows distribution against its published SHA-256; verified version, package installation options and portable isolation.
- Added `tools/decrypt_game.py` with read-only preview, matching content-ID and nonempty-key checks, source preservation, refusal to overwrite existing output, and decrypted CPK signature verification.
- Selected Vita3K's native F00D route so an online key-conversion service is not needed.
- Checked project files, the added ZIP and standard matching Vita3K license locations; no PCSG00597 license was found. Decryption and dialogue translation remain pending that input.
- Validated the user-supplied license as belonging to PCSG00264, rejected the title mismatch, and confirmed with the user that a Cross Ange license is unavailable. No decryption run occurred.
- Ignored ZIP game archives and documented tool provenance and the runnable PC workflow.

No decrypted corpus, playable build or release was created.

## 0.1.0 — 2026-10-10 — Preparation

- Read project rules and inspected the supplied PCSG00597 Vita package; the folder has no Git checkout.
- Compiled the upstream pkg2zip extractor and unpacked 54 files into ignored local source storage.
- Verified that the main game archive, images and other protected assets remain PFS encrypted. Full script, UI and Japanese-character totals are unknown.
- Began a cited English glossary of character names, world terms and terminology conventions. Unobserved UI suggestions are kept separate from confirmed game text.
- Extracted and drafted English for both readable system-title fields, preserving the title line break. Saved English-only exports using `tools/strip_jp.py`.
- Added a readable-text inventory tool, SFO reader, package probe, inventory report, UI constraint placeholders and translation workflow.
- Verified source stripping, Japanese leakage rejection, exported row identity and preserved line boundaries.

No playable build, Git commit or GitHub release was created. Dialogue translation and UI verification need decrypted source assets.
