# Cross Ange: Rondo of Angel and Dragon tr. — English patch

English fan translation of the PS Vita game **CROSS ANGE Rondo of Angel and Dragon tr.** (**PCSG00597**, Japanese release). Use small translation patches to rebuild an English PKG locally for Vita3K, supplying your original game and matching license. Installed CPK patching is also available. This repository contains English text, glossaries, layout records and tools; full game packages, extracted artwork, licenses and local Japanese scripts stay outside Git.

## Applying the patch

Use the local **Retro Trans 0.5.16** build's **Automatic** tab. It downloads about **5.4 MB of translation patches**, decrypts your original game locally, applies the CPK/metadata patches and credits, then rebuilds and verifies an English PKG on your computer. The package-size whole-PKG xdelta route remains withdrawn.

1. Select your original Japanese **PCSG00597 v01.00 `.pkg`** in **Automatic**.
2. Select **Cross Ange's matching `work.bin`** (or compatible NoNpDrm `.rif`). A license from another game will not work. **This flow needs the license during patching and installation.** No license is included or downloaded.
3. Choose a **new Translated PKG filename** and click **Patch**. Allow at least **6 GB free** for temporary extraction, rebuilding and verification. The tools also download the official Vita3K runtime on first use; this is separate from the 5.4 MB translation bundle.
4. Wait for the output to pass a second isolated Vita3K installation and complete file checks. Your original PKG, license, existing emulator data and saves are preserved.
5. Back up existing saves and close the game. In your own Vita3K, use **File → Install .pkg** for the new English package and supply the same matching license when asked. Restart and check **v0.1.13** in the title footer; translation credits are on manual page 25.

The game repository and release are **public**; translation downloads do not require GitHub sign-in. Automatic discovers the matching `VITA-PKG.json` and `Cross-Ange-English-0.1.13-Vita-PKG-patches.zip` independently of the public binary catalog. For offline/local testing, select that ZIP under **Vita → Vita3K PKG → Local patch (optional)** with the original PKG and matching license.

This tools build remains local; published tools 0.5.4 does not provide this Automatic Vita PKG flow. No new tools release is published. The rebuilt PKG is intended for Vita3K; it is not Sony-signed or verified for hardware installation. Full gameplay and proofreading remain outstanding. Hardware uses the separate rePatch bundle.

### Manual installed CPK alternative

**Install the original game first, then patch its installed files.** You need your own Japanese **PCSG00597 v01.00** PKG and that game's matching `work.bin` (or compatible `.rif`) for installation in Vita3K. Licenses are never included or downloaded. Patching the installed files does not read a license.

Download the small CPK delta, optional metadata delta and extras from the [v0.1.13 release](https://github.com/retro-trans/Cross-Ange/releases/tag/v0.1.13). The CPK delta is **5,349,702 bytes (about 5.35 MB)**. The whole-PKG xdelta ZIP and profile remain withdrawn; the small local-rebuild ZIP/profile are separate.

1. Install the original PKG in Vita3K with its matching license, then close Vita3K and back up your saves and original game files.
2. Locate `<Vita3K data folder>/ux0/app/PCSG00597/cpk/Ange.cpk`. With this computer's configuration it is `E:\Emu\vita3k\fs\ux0\app\PCSG00597\cpk\Ange.cpk`. Other computers may use a different data folder.
3. In **Retro Trans → Apply xdelta**, select that original `Ange.cpk`, `Cross-Ange-English-0.1.13-Ange.xdelta`, and a **new output filename** outside the installed game folder. The existing published tools **0.5.4** supports this manual binary route; local tools 0.5.16 supports this alternative as well as small-download PKG rebuilding. External DeltaPatcher/xdelta3 also work.
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

Installed CPK recognition in Automatic depends on a catalog entry accessible to the app. For this manual alternative, use **Apply xdelta** with the downloaded patch. Original-PKG Automatic uses separate Vita profile discovery and works without GitHub sign-in for this public release. Hardware rePatch remains a separate [small-download route](docs/repatch-installation.md). Older whole-PKG tools builds 0.5.12–0.5.14 are withdrawn; no new tools release is published by this update.

## Release status

**v0.1.13 is an early English local test build requiring proofreading and full playtesting.** Its rebuilt PKG passed an isolated Vita3K installation and all 48 installed file hashes matched the English build. Gameplay of this PKG has not been tested. Translation content is retained from 0.1.12: all 17,151 identified structured targets, including scenario dialogue and choices, speaker labels, UI, battle/navigation captions, gallery fields and system titles. All 15 chapter/prologue headings appear in both graphic variants, and all ten identified tutorial pictures have English text, including their embedded samples.

The build uses **GenEi LateGo v2 Medium**, native proportional character advances and pixel-width dialogue wrapping. Title branding and the appended manual credits page share the build version. Briefing/unit labels use compact display wording, and result time fields use **s** and **Left** to fit their fixed spaces.

File/patch verification does not establish that every scene renders correctly. New tutorial and battle-result layouts need live confirmation. A duplicate Naomi eye-animation tile remains unresolved; 24 other raster reading regions, the original manual prose and movie logos are pending. Some long dialogue uses native 80% size. There are 139 provisional equipment-name proposals requiring further review. Counts describe identified resources, not a whole-game completion percentage. See [build checks](docs/english-build.md), [current progress](docs/translation-progress.json) and [changelog](CHANGELOG.md).

## Check the translation

Use your own original game for comparison. The [scenario](work/translation/en/corpus.en.json), [UI](work/translation/en/interface.en.json), [battle/gallery](work/translation/en/additional.en.json), [raster](work/translation/en/raster.en.json) and [system-title](work/translation/en/metadata.en.json) catalogs contain English, source IDs, hashes and review notes. Japanese dialogue is read from local extracted files, rather than distributed in Git.

Use [Vita3K testing instructions](docs/vita3k-testing.md) to reproduce a problem. Report the build version, screen or chapter, exact text, emulator/device and a screenshot. Distinguish a translation issue from text clipping, missing artwork or animation problems. Restart the game after changing patch files.

## Translate it

Fork the project to improve the English or add another language. Start with the [translation workflow](docs/translation-workflow.md), [glossary notes](docs/glossary-notes.md) and [contribution guide](CONTRIBUTING.md). Builders require your own locally extracted game assets and working translations; a fresh source checkout alone is not a buildable game.

```text
python tools/glossary_audit.py
python tools/validate_translation.py work/translation/en/corpus.working.json
python tools/strip_jp.py work/translation/en/corpus.working.json --write
python tools/build_branding.py --translations
python tools/build_branding.py --translations --write
```

Preview and review changes before using `--write`. Keep Japanese scripts in ignored working files; commit English-only `*.en.json` exports. Every new game build increments the version, footer, credits and changelog together. [Release packaging](docs/release-packaging.md) wraps an existing build without changing its game bytes or version.

## Repository layout

- `docs/` — workflow, format/font/layout notes, installation and release documentation
- `tools/` — extraction, translation, native texture/font builders, verification and packaging tools
- `work/glossary/` — researched names and terms, including provisional entries and sources
- `work/translation/en/` — English-only catalogs and reviewed translation slices
- `work/ui/` — resource identities, coordinates and layout records; screenshots remain local
- `work/output/` — ignored local builds and release packages
- `incoming/` — ignored external files for inspection

## How it was translated

The translation was drafted with large language models, then reviewed and edited against scene context and a researched glossary. Source IDs, voice references and non-layout controls are preserved. Review flags and uncertain names remain visible; human proofreading and playtesting are welcome through [Issues](https://github.com/retro-trans/Cross-Ange/issues).

## Credits

| Role | Contributor |
| --- | --- |
| Translation project | Retro Trans |
| Font | GenEi LateGo v2 Medium by o_tamon and upstream contributors |
| Patch tooling | Retro Trans Tools; xdelta3 |

Original game: SUNRISE / PROJECT ANGE and BANDAI NAMCO Entertainment Inc. The game retains its original copyright notice.

## License

Original project translation contributions and tools are under [MIT](LICENSE). The font uses [SIL OFL 1.1](docs/licenses/genei-latin-OFL.txt); retain its license and attribution with patched files. The game and its assets remain with their original rights holders and are not covered by the project license. No game package, executable or license key is included in a release.
