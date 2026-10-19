# Vita release packaging

The recommended Vita3K route downloads small translation patches and rebuilds an English PKG locally from the user's original package and matching license. Manual installed CPK patches and hardware rePatch remain available. The user authorized public access for the first public release; whole-PKG xdelta downloads remain withdrawn.

Use `tools/package_release.py --build 0.1.13 --write` to package the local-rebuild profile/ZIP, or `--format cpk` for component assets. These delegate to `package_pkg_release.py` and `package_cpk_release.py`. Both preview by default and preserve existing outputs. Local-rebuild packaging validates all declared source/English/patch identities and the exact ZIP inventory, including credits/font attribution. It publishes nothing and does not include original game files or licenses.

Current assets: VITA-PKG.json, Cross-Ange-English-0.1.13-Vita-PKG-patches.zip, VITA-PKG-SHA256SUMS.txt and PKG-REBUILD-VALIDATION.json; the eight installed CPK/component assets (including standard VALIDATION.json); and the five hardware rePatch assets. Do not publish VITA-PKG-XDELTA.json or the package-size whole-PKG ZIP.

Catalog repair deployed after explicit approval: added standard `VALIDATION.json`, bound to the
exact `BUILD-MANIFEST.json` bytes with one verified roundtrip per patch, and
included it in `SHA256SUMS.txt`. The custom `CPK-VALIDATION.json` remains useful
UI evidence but does not replace the standard report. Component packaging now
generates both and runs the shared release validator before completing. Published metadata passed readback and strict catalog validation; all other
release assets are unchanged.

Upload/re-read the small profile/ZIP, then verify actual Automatic discovery and complete local conversion with a matching license. A second isolated native Vita3K installation must verify all 48 output files and the original/license must remain unchanged. Retain earlier verification records as historical provenance. Game bytes, title footer and credits remain 0.1.13 for this distribution update. The user separately authorized publishing tools 0.5.16; future game-release updates still do not implicitly authorize tools releases.

The full unscoped catalog refresh on 2026-10-19 completed with 77 releases and
zero rejections. See [deployment verification](catalog-repair-0.1.13.json).
