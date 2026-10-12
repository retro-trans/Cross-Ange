# Title version and credits

The title footer follows the user's reference: white text, right aligned, with `v0.x.y` above `github.com/retro-trans`. The added text uses GenEi LateGo v2 Medium from the user’s requested Genei Latin package. A dedicated Retro Trans credits page is appended to the game manual as page 25. Existing game credits and copyright remain intact. Names beyond the requested group have not been invented.

`VERSION` records the last successful local build. `tools/build_branding.py` increments its patch component for each new build, regenerates the title footer and credits from that one version, and appends a changelog entry after verification. An explicit newer minor version can be passed with `--version 0.2.0`. Existing builds cannot be overwritten and old or equal versions are rejected. A preview does not reserve a version or write assets.

```powershell
python tools/build_branding.py
python tools/test_build_branding.py
python tools/build_branding.py --write
```

Inspect the preview's version, text, coordinates and affected members before the write command. Each output is under `work/output/cross-ange-<version>/`:

- `game/cpk/Ange.cpk`: replacement archive for a local test installation.
- `game/sce_sys/manual/025.png`: appended credits page.
- `archive-members/`: the two replacement title assets before packing.
- `manifest.json`: version, source hashes, text coordinates, verification results and runtime status.

Without `--translations`, these are branding-only candidates containing the original script. **Use `python tools/build_branding.py --translations` and then `--translations --write` for an English candidate.** Build 0.1.10 includes the two title members, credits page, 469 text/font/kerning members, three tutorial textures, both chapter-title textures and English system titles; all 476 archive replacements are verified. See [English build](english-build.md). Generated previews under `work/ui/local/branding/<version>/` show the decoded footer strip, atlas and credits page. The footer strip is an asset reconstruction with a plain background, not a game screenshot. Final placement over the animated title background and manual access must be checked in-game before calling a candidate tested.

## Asset changes and checks

The source copyright sprite samples atlas rectangle `(0,233)-(960,256)`, with origin `(480,11)` and position keys `(480,521)`. Its screen rectangle is consequently `(0,510)-(960,533)`. The replacement uses the previously empty atlas rectangle `(0,300)-(960,387)` and origin `(480,75)`. Its bottom edge and the copyright pixels remain in the same screen positions. Version and URL occupy the added area above the copyright, ending before y=510. The footer inherits the original copyright sprite's fade and visibility; its placement is derived from animation data and remains unverified at runtime.

The writer retains the entire original palette and original atlas pixels. New glyphs use the existing palette, matched with alpha-aware color distances. It copies the original copyright strip into the new sprite unchanged. Only the sprite's source rectangle and vertical origin change; IDs, hierarchy, frame count, position, scale, transparency and other animation keys stay intact. The FCAA animation wrapper is regenerated with literal tokens and decoded again to verify every byte.

The local CPK writer preserves the original member data area, appends the two replacements, relocates the unchanged ETOC, and adjusts their TOC offsets and sizes plus header content/size totals. It refuses unsupported checksums, ITOC or trailing layouts. The source archive is read-only. Verification compares all 4,484 unaffected TOC rows, both replacement payloads, preserved source payload bytes and ETOC content. This establishes binary preservation, not runtime compatibility with every CPK reader.

The appended manual page uses the existing 960×544 page size and sequential numbering. The [Vita3K manual viewer implementation](https://github.com/Vita3K/Vita3K/blob/master/vita3k/gui-qt/src/live_area_widget.cpp) loads `001.png` onward until the first missing page, supporting the appended `025.png`, and provides a LiveArea manual entry and page navigation. Its bottom navigation strip starts at y=512; credits text and version remain above that area. Hardware recognition of the added page still requires checking. This is a manual credits page; a title-menu entry has not been added.

The permanent build rule is recorded in `AGENTS.md`. No GitHub release is authorized by this work.
