# Patch the installed game — PCSG00597

**Install the original game first, then patch its installed files.** You need your own Japanese **PCSG00597 v01.00** PKG and that game's matching `work.bin` (or compatible `.rif`) for installation in Vita3K. Licenses are never included or downloaded. Patching the installed files does not read a license.

The repository and release remain **private**. Download the small CPK delta, optional metadata delta and extras from the [v0.1.13 release](https://github.com/retro-trans/Cross-Ange/releases/tag/v0.1.13) using an account with repository access. The CPK delta is **5,349,702 bytes (about 5.35 MB)**. The whole-PKG ZIP and its profile have been withdrawn.

1. Install the original PKG in Vita3K with its matching license, then close Vita3K and back up your saves and original game files.
2. Locate `<Vita3K data folder>/ux0/app/PCSG00597/cpk/Ange.cpk`. With this computer's configuration it is `E:\Emu\vita3k\fs\ux0\app\PCSG00597\cpk\Ange.cpk`. Other computers may use a different data folder.
3. In **Retro Trans → Apply xdelta**, select that original `Ange.cpk`, `Cross-Ange-English-0.1.13-Ange.xdelta`, and a **new output filename** outside the installed game folder. The existing published tools **0.5.4** supports this manual binary route; local source 0.5.15 removes the withdrawn PKG options. External DeltaPatcher/xdelta3 also work.
4. Verify the output SHA-256 below, then replace the installed `cpk/Ange.cpk` with the patched output, keeping the original backup. Never patch an already translated archive.
5. Optionally patch the original `sce_sys/param.sfo` with `Cross-Ange-English-0.1.13-param.xdelta` to a new file, verify its hash, then replace that installed file. This updates the displayed game title.
6. Extract `Cross-Ange-English-0.1.13-extras.zip` and copy its `sce_sys/manual/025.png` and `sce_sys/font-license.txt` into the installed game's corresponding folders. Read `INSTALL.md`; these extras contain translation credits and required font attribution.
7. Restart Vita3K, launch Cross Ange and check **v0.1.13** in the title footer. Translation credits are on manual page 25.

**Manual commands:**

```text
xdelta3 -d -s Ange.cpk Cross-Ange-English-0.1.13-Ange.xdelta Ange-English.cpk
xdelta3 -d -s param.sfo Cross-Ange-English-0.1.13-param.xdelta param-English.sfo
```

| File | Original SHA-256 | English SHA-256 |
| --- | --- | --- |
| `Ange.cpk` | `e04d94fac7ba1bc21acfd98c9ea8352995e32229c642485fb2537cd0d53213de` | `4d6b444ee37994d5282a8fd377cee964f056a68e7a2be9a1f0b075b761601a3a` |
| `param.sfo` | `04924d2566147471c89464d568c8ae8708b43cc296b370c6b8f208317cebf603` | `6d4414054f46e25b14e5ef25ae9d4c655f9c1111155cc51e43cf6e7c46d00c10` |

The original archive is **882,846,536 bytes**; the English archive is **902,054,728 bytes**. `BUILD-MANIFEST.json` pins sources, patches and outputs; `SHA256SUMS.txt` covers the downloads. Local file replacement requires enough space for the original backup and patched archive. If your original hash differs, stop and check the game revision or whether a translation/mod is already installed.

Automatic catalog recognition depends on a catalog entry accessible to the app. This private release does not add an entry to the public catalog: use **Apply xdelta** with the downloaded patch. Hardware rePatch remains a separate [small-download route](repatch-installation.md). Older whole-PKG tools builds 0.5.12–0.5.14 are withdrawn; no new tools release is published by this update.
