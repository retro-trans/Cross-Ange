# Installed CPK release packaging

Current player flow: install the original licensed game in Vita3K, close it, patch its installed CPK to a new file, verify and replace with a backup. Keep the project private. The user explicitly requested restoring this flow and withdrawing whole-PKG downloads because their approximately 945 MB delta is too large.

`tools/package_release.py --build 0.1.13 --write` prepares the verified component distribution from retained local deltas and English build data. It checks both complete delta round trips, exact profile identities, credits/font attribution and checksums before generating a fresh output folder. Packaging alone does not authorize publication or change game branding.

The component release allowlist is BUILD-MANIFEST.json, the Ange/param xdelta files, the extras ZIP, SHA256SUMS.txt, EXTRAS-SHA256SUMS.txt and CPK-VALIDATION.json. Keep the five separate hardware rePatch assets. Remove VITA-PKG-XDELTA.json, the whole-PKG ZIP and their old current verification/checksum assets. Do not reintroduce the legacy PKG-rebuilding profile or ZIP.

Verify uploaded component bytes and a complete Apply xdelta UI round trip before retiring the old whole-PKG downloads. Preserve historical native PKG, private/public Automatic and hardware proof records. Game bytes/version remain 0.1.13. No full game/archive or license is distributed. The existing published tools 0.5.4 handles manual Apply xdelta; replacement local source changes do not authorize tools publication or source pushes.
