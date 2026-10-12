# English test build 0.1.12

This document records the historical 0.1.12 local installation. The current released distribution is 0.1.13, with whole-PKG patching and isolated native installation verification. See [current installation instructions](patch-installation.md) and [Vita3K testing](vita3k-testing.md).

Build 0.1.12 is installed in the user's existing Vita3K. It translates the remaining seven tutorial pictures and uses compact battle-result time labels, retaining the briefing/unit-label fixes. All ten identified tutorial pictures now have English text, including their embedded samples. New layout still needs an in-game check. GenEi LateGo v2 Medium, proportional advances and all 30 chapter/prologue heading variants are retained.

The user's 0.1.8 captures confirm startup reached gameplay, dialogue appeared in its panel, and the story progressed into battle. This confirms the prior missing font-terminator startup fix. The extra Naomi eye-animation tile in the battle screenshot remains unresolved; see [investigation and reversible comparison](portrait-animation-issue.md).

| Text | Inserted targets |
| --- | ---: |
| Scenario dialogue and choices, across 462 files | 13,214 |
| UI table | 1,716 |
| Battle-partner captions | 861 |
| Navigator captions | 1,155 |
| Gallery fields | 203 |
| System titles | 2 |

All **17,151 identified structured targets** are inserted, retaining all 13,277 original scenario rows, IDs and voice references. Dialogue wraps to a 670-pixel limit using installed glyph advances. Most records use normal size and two lines; 88 long records use native 80% size and at most three lines. Eighteen speaker records are fitted to the 212-pixel nameplate. The revised classroom wording retains realized ideals, the end of any need for conflict and achieved peace.

Both native fonts use 197 GenEi Latin/punctuation slots, including safe control-boundary aliases. Unrelated glyph records remain byte-exact. All 46,048 font records pass the native zero-token termination check. The colon derivative retains the source font's period shapes. Copyright, the OFL 1.1 license and typography attribution accompany the build; see [font notes](english-font.md).

All ten identified tutorial textures (EBG_106–112 and ECG_043–045) are inserted as native indexed textures, with 84 explicit text rectangles covering 76 original source regions. Both chapter atlases contain 30 additional title regions. There are 106 inserted source regions out of 130 reading drafts; the remaining 24 source regions, original manual prose and movie logos remain pending. Header, palette and pixels outside the repair bounds are preserved. Exact placement and emitted native previews are recorded in `work/ui/tutorial-layout.json` and `work/ui/chapter-title-layout.json`.

Twenty checks passed: thirteen translation/font/UI checks, four native tutorial texture checks and three branding checks. All 48 installed game files were hash-verified, and all 483 replacement members, 46,048 native glyph records and 13 compact UI fields were independently checked using `tools/verify_vita3k_build.py`. The manifest and `installed-readback.json` retain the evidence.

The footer and final manual credits page both show version 0.1.12; the changelog records this build. The prior 0.1.11 app is preserved at the location recorded in the installation record. Earlier backups remain available. Use the desktop **Cross Ange - Test Build** shortcut. See [testing instructions](vita3k-testing.md). No GitHub release was created.

On 2026-10-12, the deleted emulator data and mismatched executable/settings were repaired. The current v0.1.12 app lives under `E:\Emu\vita3k\fs\ux0\app\PCSG00597`; all 48 files were hash-verified on reinstallation. The Play shortcut was visually verified at the English difficulty-selection screen, around 30 FPS. Earlier C: app backups no longer exist; the earlier backup moved to E: remains preserved. See [the updated testing instructions](vita3k-testing.md). This startup check does not verify all dialogue, chapter titles or the unresolved portrait issue.
