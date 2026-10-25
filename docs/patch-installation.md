# Install or patch Cross Ange — PCSG00597

Use **[Retro Trans 0.5.18](https://github.com/retro-trans/retro-trans-tools/releases/tag/v0.5.18)**'s **Automatic** tab. It downloads about **5.4 MB of translation patches**, decrypts your original game locally, applies the CPK/metadata patches and credits, then rebuilds and verifies an English PKG on your computer. The package-size whole-PKG xdelta route remains withdrawn.

1. Select your original Japanese **PCSG00597 v01.00 `.pkg`** in **Automatic**.
2. Select **Cross Ange's matching `work.bin`** (or compatible NoNpDrm `.rif`). A license from another game will not work. **This flow needs the license during patching and installation.** No license is included or downloaded.
3. Choose a **new Translated PKG filename** and click **Patch**. Allow at least **6 GB free** for temporary extraction, rebuilding and verification. The tools also download the official Vita3K runtime on first use; this is separate from the 5.4 MB translation bundle.
4. Wait for the output to pass a second isolated Vita3K installation and complete file checks. Your original PKG, license, existing emulator data and saves are preserved.
5. Back up existing saves and close the game. In your own Vita3K, use **File → Install .pkg** for the new English package and supply the same matching license when asked. Restart and check **v0.1.16** in the title footer; translation credits are on manual page 25.

The game repository and release are **public**; translation downloads do not require GitHub sign-in. Automatic discovers the matching `VITA-PKG.json` and `Cross-Ange-English-0.1.16-Vita-PKG-patches.zip` independently of the public binary catalog. For offline/local testing, select that ZIP under **Vita → Vita3K PKG → Local patch (optional)** with the original PKG and matching license.

Tools 0.5.18 provides this Automatic flow in its published Windows build. The rebuilt PKG is intended for Vita3K; it is not Sony-signed or verified for hardware installation. Full gameplay and proofreading remain outstanding. Hardware uses the separate rePatch bundle.

## Manual installed CPK alternative

**Install the original game first, then patch its installed files.** You need your own Japanese **PCSG00597 v01.00** PKG and that game's matching `work.bin` (or compatible `.rif`) for installation in Vita3K. Licenses are never included or downloaded. Patching the installed files does not read a license.

Download the small CPK delta, optional metadata delta and extras from the [v0.1.16 release](https://github.com/retro-trans/Cross-Ange/releases/tag/v0.1.16). The CPK delta is **5,388,565 bytes (about 5.39 MB)**. The whole-PKG xdelta ZIP and profile remain withdrawn; the small local-rebuild ZIP/profile are separate.

1. Install the original PKG in Vita3K with its matching license, then close Vita3K and back up your saves and original game files.
2. Locate `<Vita3K data folder>/ux0/app/PCSG00597/cpk/Ange.cpk`. With this computer's configuration it is `E:\Emu\vita3k\fs\ux0\app\PCSG00597\cpk\Ange.cpk`. Other computers may use a different data folder.
3. In **Retro Trans → Apply xdelta**, select that original `Ange.cpk`, `Cross-Ange-English-0.1.16-Ange.xdelta`, and a **new output filename** outside the installed game folder. The existing published tools **0.5.4** supports this manual binary route; tools 0.5.18 supports this alternative as well as small-download PKG rebuilding. External DeltaPatcher/xdelta3 also work.
4. Verify the output SHA-256 below, then replace the installed `cpk/Ange.cpk` with the patched output, keeping the original backup. Never patch an already translated archive.
5. Optionally patch the original `sce_sys/param.sfo` with `Cross-Ange-English-0.1.16-param.xdelta` to a new file, verify its hash, then replace that installed file. This updates the displayed game title.
6. Extract `Cross-Ange-English-0.1.16-extras.zip` and copy its `sce_sys/manual/025.png` and `sce_sys/font-license.txt` into the installed game's corresponding folders. Read `INSTALL.md`; these extras contain translation credits and required font attribution.
7. Restart Vita3K, launch Cross Ange and check **v0.1.16** in the title footer. Translation credits are on manual page 25.

**Manual commands:**

```text
xdelta3 -d -s Ange.cpk Cross-Ange-English-0.1.16-Ange.xdelta Ange-English.cpk
xdelta3 -d -s param.sfo Cross-Ange-English-0.1.16-param.xdelta param-English.sfo
```

| File | Original SHA-256 | English SHA-256 |
| --- | --- | --- |
| `Ange.cpk` | `e04d94fac7ba1bc21acfd98c9ea8352995e32229c642485fb2537cd0d53213de` | `e75631ba8d1e33cb155e55a99b3a050f53d8b3a53f5e1085ece52157dc6367bd` |
| `param.sfo` | `04924d2566147471c89464d568c8ae8708b43cc296b370c6b8f208317cebf603` | `6d4414054f46e25b14e5ef25ae9d4c655f9c1111155cc51e43cf6e7c46d00c10` |

The original archive is **882,846,536 bytes**; the English archive is **902,331,208 bytes**. `BUILD-MANIFEST.json` pins sources, patches and outputs; `SHA256SUMS.txt` covers the downloads. Local file replacement requires enough space for the original backup and patched archive. If your original hash differs, stop and check the game revision or whether a translation/mod is already installed.

Installed CPK recognition in Automatic depends on a catalog entry accessible to the app. For this manual alternative, use **Apply xdelta** with the downloaded patch. Original-PKG Automatic uses separate Vita profile discovery and works without GitHub sign-in for this public release. Hardware rePatch remains a separate [small-download route](repatch-installation.md). Older whole-PKG tools builds 0.5.12–0.5.14 are withdrawn; tools 0.5.18 is available from the tools release page.
