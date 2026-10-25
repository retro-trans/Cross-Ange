# Vita release packaging

The current translation is **0.1.16**. Package the existing verified build;
publication does not rebuild its game bytes, footer or credits. The recommended
route downloads approximately 5.4 MB of patches and rebuilds an English PKG
locally from the original Japanese PKG and matching work.bin/.rif. Retain manual
installed CPK deltas and hardware rePatch. Never publish a complete game,
license, or whole-PKG xdelta.

Recommend published **Retro Trans 0.5.18** for Automatic discovery. Version
0.5.16's 128 KiB profile limit rejects an unrelated larger SRW-Z3 profile while
scanning the organization. The released 0.5.18 supports 256 KiB profiles. The
Cross Ange local ZIP and hardware route remain compatible with 0.5.16; their
minimum-version metadata and earlier native validation remain valid.

1. Run the translation/native-font/branding/HUD/timed-dialogue checks and export
   local translations using `tools/strip_jp.py`. Commit the English-only source
   and tools before generating a manifest that pins the source commit.
2. Run `python tools/prepare_release_assets.py --build 0.1.16` to preview, then
   add `--write`. This checks the existing native-installation proof, original
   and English identities, both component round trips and the exact local ZIP.
   It generates `BUILD-MANIFEST.json`, manifest-bound `VALIDATION.json`, deltas,
   credits/font extras, the small `VITA-PKG.json`/ZIP and verification/checksums
   under `work/output/releases/v0.1.16`.
3. Run `python tools/package_repatch.py --build 0.1.16 --write`. Its separate
   hardware bundle uses the same verified CPK delta and generated credits/font
   attribution; the original executable is retained.
4. Verify the hardware flow with published Retro Trans Tools 0.5.16, collect the
   two routes into a clean publication folder and recompute checksum lists.
   Run the shared strict release/catalog validators. Keep native game files,
   licenses and all testing workspaces outside the publication folder.
5. Publish only after explicit user authorization. Check the tag/source commit,
   all uploaded asset hashes, anonymous downloads and actual Automatic
   discovery/rebuilding with published tools. The rebuilt PKG must pass native
   installation and all 48 file hashes, preserving the original and license.

The public release retains the eight standard component assets, four small
PKG-rebuild assets and five hardware rePatch assets. File verification does not
establish gameplay or physical-Vita compatibility. The experimental
[Vita3K HUD correction](https://github.com/retro-trans/Vita3K/releases/tag/v0.2.1-cross-ange-hud.1)
is a separate emulator download.

The older `package_release.py` wrappers preserve their historical verified-input
contract. The 0.1.13 catalog metadata repair and its successful full refresh are
recorded in [the historical repair report](catalog-repair-0.1.13.json); do not
rewrite those older game assets while publishing a new version.
