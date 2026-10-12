# Direct PKG patching for Vita3K

The recommended player workflow uses [Retro Trans 0.5.11 or newer](https://github.com/retro-trans/retro-trans-tools/releases/latest):

1. Open **Automatic** and browse to your original Japanese PCSG00597 `.pkg`.
2. Select its matching local NoNpDrm `work.bin` or `.rif` in **Matching license**.
3. Choose a new **Translated PKG** filename and click **Patch**. The matching translation ZIP downloads automatically.
4. Install the resulting package in Vita3K with the same license and check **v0.1.13** on the title screen.

The translation release is private, so automatic downloads need a GitHub account with repository access. An existing GitHub CLI sign-in is used automatically; public releases of other games need no sign-in. The app downloads translation assets and the official Vita3K tool, never your game or license. Use Windows x64 and at least 6 GB of free space. For a downloaded ZIP override, use **Vita → Vita3K PKG → Local patch (optional)** instead.

The standalone local tool workflow is:

1. Select your original Japanese PCSG00597 `.pkg` and its matching 512-byte NoNpDrm `work.bin` or `.rif`.
2. Select either a prepared local English build or a folder containing the translation release assets.
3. Create a new English `.pkg` with `tools/patch_pkg.py`.
4. In Vita3K, choose **File → Install .pkg**, select the English PKG and supply the same matching license when prompted. Restart the game and check its title-screen version.

You do not have to install the original game first or edit a CPK manually. The tool decrypts the original in temporary storage, applies the English changes, rebuilds encrypted PFS and writes a real PKG container. It installs that candidate into an isolated Vita3K directory and compares every installed file against the English build before saving the final output. Original package and license inputs are checked again after conversion. The user's emulator installation and saves are untouched by conversion.

The English PKG still requires the matching license. Renaming an unrelated `.rif` does not make it usable. The initial implementation accepts matching NoNpDrm licenses; account-bound retail RIFs and text zRIF files are not accepted by this patcher.

## Current availability

Version 0.1.13 supplies the `VITA-PKG.json` profile and `Cross-Ange-English-0.1.13-Vita-PKG-patches.zip` used by Retro Trans's automatic downloads. The profile identifies the game and exact original edition; future supported games use different profiles without new UI options. Full game PKGs and licenses stay on the user's computer. The repository and releases remain private. Retro Trans's existing two-file Automatic workflow remains supported as an alternative.

The rebuilt package is intended for **Vita3K**. Its encrypted sector data and integrity tables are regenerated, but Sony signatures cannot be regenerated. It is not an official signed package or a verified physical-Vita installation method. On hardware, follow the separate [rePatch installation instructions](patch-installation.md).

## Dependencies

Run from the repository root on Windows. Use Python 3.11 or later with `cryptography`, at least **6 GB free space** and an official Vita3K Windows distribution. The verified local runtime is `tools/pkg_vendor/vita3k-20261010` (Vita3K 0.2.1, commit `4154b75d5e62`); another runtime directory can be selected with `--runtime`.

Public format constants are read from ignored upstream source checkouts, not copied personal licenses. Set these up before using the tool:

```text
py -3.11 -m pip install cryptography
git clone https://github.com/Vita3K/psvpfsparser.git tools/pkg_vendor/psvpfsparser-repack-probe
git -C tools/pkg_vendor/psvpfsparser-repack-probe checkout d14381f871a69009bd18b2aaec2213a6738bebba
git clone https://github.com/mmozeiko/pkg2zip.git tools/pkg2zip
git -C tools/pkg2zip checkout 9222c4e00235dfe7914e9db0cc352da07e63d9f9
```

Skip cloning a checkout that already exists and verify its revision instead. Place the complete official Vita3K distribution in the runtime folder, or pass its directory with `--runtime`. The tool copies its executable, libraries and resources into temporary storage and configures a separate filesystem. It never uses an existing game's files.

## Prepared local build

For this workspace's already prepared version 0.1.13, substitute the actual original package path:

```text
python tools/patch_pkg.py --package "original.pkg" --license "incoming/work.bin" --build 0.1.13 --output "work/output/cross-ange-0.1.13/Cross-Ange-English-0.1.13.pkg"
```

This previews the selected route. Append `--write` to perform conversion. The parent output directory must exist; choose a new output name because existing files are never overwritten. Running this command requires the existing local build, including its manifest, translated archive, English metadata, versioned credits page and font license. A source-only checkout does not contain those game assets.

## Translation release assets

For a player using downloaded translation patches, put the matching `BUILD-MANIFEST.json`, two `.xdelta` files, extras ZIP and `EXTRAS-SHA256SUMS.txt` in one directory. Supply a trusted local xdelta3 executable:

```text
python tools/patch_pkg.py --package "original.pkg" --license "work.bin" --patch-directory "translation-assets" --xdelta "xdelta3.exe" --output "English.pkg"
```

Append `--write` after preview. The tool verifies the original component identities, both patch hashes, both resulting file hashes and the extras ZIP. It retains credits and font attribution. The current compatible assets are 0.1.12; conversion preserves the version declared by the assets. Repackaging an existing version does not increment the title footer or change the translated game files.

## Accepted original package

| Property | Required value |
| --- | --- |
| Title ID | `PCSG00597` |
| Content ID | `JP0700-PCSG00597_00-CROSSANGEGAME000` |
| Package bytes | `925548400` |
| Package SHA-256 | `962498429645bf92d0171280b075629ff6dc8100f365ce43805d2cd3e897ebcb` |

Other regions, revisions, patched inputs and different package encodings are rejected by the initial tool. No package input is modified in place.

## Verification and limits

The 0.1.13 PKG installed successfully in isolated Vita3K and all **48 game files** matched the English build, including credits and the OFL font license. The separate player route also converted the existing 0.1.12 release assets and passed native installation and all 48 file comparisons. Eight package regressions and twenty translation/font/tutorial/branding checks passed. The source PKG and license were unchanged. See [validation record](pkg-patching-validation-0.1.13.json).

Each conversion writes an adjacent `.validation.json` with output size, SHA-256 and installation checks. Installer success is followed by an exact inventory and complete-file hash comparison; an exit code alone is insufficient. Native diagnostics are discarded because the upstream PFS library can print derived keys. Temporary license data, decrypted files and candidate packages are removed after conversion or an ordinary failure.

These checks establish format and installation correctness. They do not establish gameplay compatibility or resolve the existing translation/layout issues. Gameplay of the new PKG and physical-Vita behavior remain untested.

Format references: [Vita3K PKG installer](https://github.com/Vita3K/Vita3K/blob/b75d5e62/vita3k/packages/src/pkg.cpp), [Vita3K PFS parser](https://github.com/Vita3K/psvpfsparser), [pkg2zip](https://github.com/mmozeiko/pkg2zip).
