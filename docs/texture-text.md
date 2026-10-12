# Texture text inspection — 0.1.12

Build 0.1.12 inserts all ten identified tutorial pictures: EBG_106–112 and ECG_043–045. The 84 tutorial text rectangles cover 76 original source regions, including embedded sample captions and choices. All 30 chapter/prologue heading variants remain inserted, for 106 of the 130 source reading regions represented by 114 rendered rectangles. The remaining 24 source regions are reading drafts. Four native tutorial checks pass, with decoded previews visually inspected. Native headers, palettes and every pixel outside explicit text regions are preserved. Exact placement records are in `work/ui/tutorial-layout.json` and `work/ui/chapter-title-layout.json`. New screens need an in-game check. See [the tutorial/result audit](tutorial-result-fixes.md). The inspection history below records the original 0.1.3 milestone.

The archive contains 1,875 BTX textures. `tools/shtx_extract.py` decodes indexed SHTXFS pixels without changing the game files. Its palette/header interpretation follows the [original SHTXFS decoder](https://github.com/yukinogatari/Danganronpa-Tools/blob/master/dr12ae/shtx_conv.py); recognizable ENERGY/BOOST interface graphics and the Japanese startup notice have been visually checked.

There are 1,081 direct indexed textures and 794 wrapped textures. `tools/dr12ae_extract.py` handles FCAA55A7 and nested GX3 compression, following the [original decompressor](https://github.com/yukinogatari/Danganronpa-Tools/blob/master/dr12ae/dr_dec.py) and checking token bounds, backward references, declared sizes and zero trailing padding. All 794 decompress successfully: 23 indexed textures and 771 GXT files. All 1,875 textures now have local PNG previews.

`tools/gxt_extract.py` renders the base mip level of 665 BC1 and 106 BC3 textures. GXT headers, block bounds and the full Morton block permutation are checked. The layout follows [Scarlet's Vita texture implementation](https://github.com/xdanieldzd/Scarlet/blob/master/Scarlet/Platform/Sony/PSVita.cs). All decoded textures have received an initial visual scan; that does not establish readability of every tiny marking. Original compressed textures and mip levels remain intact.

Inspection manifests cover the union of all 1,875 decoded archive textures without duplicate-count inflation: widgets, equipment icons, event/ending illustrations, backgrounds, Live2D textures and remaining model/effect textures. Every listed inspection sheet was visually examined. Event illustrations ECG_043–045 and EBG_106–112 contain tutorial instructions and labels, now inserted. All eight external save/launcher PNGs were inspected, including white copyright text against a dark background. [The inspection record](../work/ui/image-inspection.json) retains five pending marking groups and distinguishes initial scanning from complete readability verification.

Local game pixels stay under ignored `work/ui/local/`. Inspection sheets are labeled thumbnails, not actual game captures. Coordinates in `work/ui/raster-regions.json` refer to the source texture, so they cannot establish screen widths or layout limits.

`work/translation/en/raster.en.json` contains **130 English reading drafts**, including the startup notice, game/logo/loading titles, IOU heading, chapter atlases, tutorial instructions and embedded labels, emblems, save/launcher regions and Naomi's swimsuit name tag. Chapter headings reference corresponding UI-table drafts by source ID. Five unresolved marking groups remain: the blurred IOU body, `mark_per_25`, `item_136`, the classroom notices in EBG_022/ECG_024, and stylized effect lettering in `ef_e021`. Their text must not be reconstructed from dialogue or presumed identities. These region units are separate from the 17,151 structured targets; 106 source regions are now inserted, with the other 24 remaining as reading drafts.

All 24 manual pages have 166 main reading blocks. [Manual screenshot coverage](manual-screenshot-coverage.json) records 45 embedded screenshots, 126 matches to 100 translated targets, two new platform labels and 32 specific unresolved microtext notes. Texture coordinates and printed screenshot rectangles do not establish live game layout limits.

The 90.112-second opening movie was visually sampled at 0.5-second intervals (180 frames). Its two readable Japanese logo regions have [separate drafts](../work/translation/en/video.en.json) with original hash, time interval and approximate coordinates. No Japanese credit or subtitle overlay was observed in the sampled frames; short overlays between samples are not ruled out. Audio and original video remain unchanged.

## Preview and verification

```powershell
python tools/shtx_extract.py
python tools/dr12ae_extract.py
python tools/gxt_extract.py
python tools/texture_contact_sheet.py
python tools/validate_translation.py work/translation/en/raster.working.json
```

Inspect previews before adding `--write`. Raster drafts validate immutable compressed-texture or PNG source hashes, dimensions, coordinate bounds and the source-free English export. Video drafts additionally validate duration and time range. Remaining work includes unreadable tiny markings, manual screenshot microtext, artwork reflow, font support and live game checks.

## Changelog

- **0.1.3 — 2026-10-11:** Added strict indexed and GXT texture decoding, nested decompression, local inspection sheets and initial raster reading translations.
