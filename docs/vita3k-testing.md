# Vita3K testing

## Current package — 0.1.13

The complete English PKG passed an isolated native Vita3K installation and comparison of all 48 installed files, recorded in `pkg-patching-validation-0.1.13.json`. The whole-PKG delta reproduces that exact package. Install it through Vita3K's **File → Install .pkg**, supplying your matching local license during installation, and check **v0.1.13** on the title screen. The patching step needs no license. See [installation instructions](patch-installation.md).

This distribution update does not install or launch the game in the user's emulator. Full gameplay and physical-Vita testing remain outstanding. The records below describe earlier local installations.

## Historical local installation — 0.1.12

Build 0.1.12 is installed in `E:\Emu\vita3k\fs\ux0\app\PCSG00597`, using `E:\Emu\vita3k\Vita3K.exe`. All 48 installed files were hash-verified. Independent readback verified all 483 replacement archive members, 46,048 native font records, 13 compact UI fields and all ten tutorial replacements. Saves, licenses, firmware and other titles were preserved.

Launch **Cross Ange - Test Build** on the desktop or **Play Cross Ange** in the project folder. Check **v0.1.12** on the title screen. Check the deck tutorial's Shop, Hangar, Briefing and Sortie explanations, and ROOM Part 2's Deck explanation and sample caption. The mission-menu and touch-conversation tutorials also now have English text. Check that the battle-result time row displays separated values with **s** and **Left**, without overlap. Existing briefing condition/stat-label fixes also need a live check. Static placement checks do not substitute for those game screens.

All 15 chapter/prologue title cards and their branch variants remain translated. Chapter 1 should read **Welcome to the First Squadron of Death**; the full list is in [chapter titles](chapter-titles.md). Some long dialogue uses native 80% size. Open the Manual from LiveArea and navigate to page 25 for translation credits. The remaining 24 raster reading regions, original manual prose and movie logos are pending.

The duplicate Naomi eye-animation tile remains unresolved. See [the original/English portrait comparison](portrait-animation-issue.md). Diagnostic shortcuts in `work/output/cross-ange-0.1.9/` select the current build automatically; close Vita3K before comparing the same scene, then return to English.

The current installation and independent readback records are `work/output/cross-ange-0.1.12/vita3k-install.json` and `installed-readback.json`. The prior 0.1.11 app is preserved at `E:\Emu\vita3k\fs\ux0\.PCSG00597-before-0.1.12-20261012-065811`. The title footer was observed in 0.1.11, but that check was stopped before reaching briefing panels. No live result or tutorial check is claimed for 0.1.12.

The 2026-10-12 launch repair restored Vita3K 4154, Sony firmware/fonts and the earlier 0.1.10 build to E: after the C: data folder was deleted. The English difficulty screen was observed at about 30 FPS. Deleted saves were not recovered. Historical repair records remain under `work/output/cross-ange-0.1.10/` and `work/source/vita3k-launch-repair/20261012`.

For a future local build, use `tools/build_branding.py --translations` to increment the version, footer, credits and changelog together. Preview installation before writing, and close Vita3K. This build is already installed; reinstalling it does not create a new version. No GitHub release has been created.
