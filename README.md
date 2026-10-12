# Cross Ange: Rondo of Angel and Dragon tr. — English patch

English fan translation of the PS Vita game **CROSS ANGE Rondo of Angel and Dragon tr.** (**PCSG00597**, Japanese release). Apply a whole-PKG xdelta to your original package to create an English PKG for Vita3K. Patching does not need a license; Vita3K requests your matching license during installation. This repository contains English text, glossaries, layout records and tools; full game packages, extracted artwork, licenses and local Japanese scripts stay outside Git.

## Applying the patch

**Installation requirement:** you must have your own `work.bin` for **Cross Ange PCSG00597** (or its matching compatible `.rif`). A license from another game will not work. It is not included in the patch and is never downloaded by the tools. Whole-PKG patching does not read it; supply it when installing the result in Vita3K.

Use the local **Retro Trans 0.5.14** build:

1. Open **Automatic** and browse to your original Japanese PCSG00597 `.pkg`.
2. Choose a new **Translated PKG** filename and click **Patch**. The matching whole-PKG translation ZIP downloads automatically; there is no license input.
3. In Vita3K, use **File → Install .pkg** to install the output and supply your matching `work.bin`/`.rif` when requested.
4. Restart the game and check **v0.1.13** on the title screen. Credits and the font license are included in the translated package.

**The repository and release are private again.** Automatic downloads require your existing GitHub CLI sign-in with repository access. Use the local Retro Trans 0.5.14 build to test both Vita routes. Tools 0.5.14 is currently a local test build, not a published tools release; the remaining published tools 0.5.4 does not support this Automatic PKG route. Tools v0.5.11 has been withdrawn. The [game release](https://github.com/retro-trans/Cross-Ange/releases/tag/v0.1.13) supplies `VITA-PKG-XDELTA.json` and `Cross-Ange-English-0.1.13-Vita-PKG-xdelta.zip` for the new flow. The ZIP is approximately **945 MB**. No full `.pkg` file or license is included.

For a local override, download that ZIP and select it under **Vita → Vita3K PKG → Local patch (optional)**. The original PKG remains unchanged. The release no longer supplies decrypted-component patches or a CPK replacement workflow. See [installation instructions](docs/patch-installation.md).

**Manual patching without our tools:** download the same ZIP, extract its `Cross-Ange-English-0.1.13-PKG.xdelta`, and use [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) or xdelta3 with your original PKG:

```text
xdelta3 -d -s Original.pkg Cross-Ange-English-0.1.13-PKG.xdelta English.pkg
```

Keep a new output filename. The exact original and output sizes/hashes are recorded in `VITA-PKG-XDELTA.json`; `SHA256SUMS.txt` covers downloads. This is not an upgrade patch for an existing English PKG. [Release notes](https://github.com/retro-trans/Cross-Ange/releases) include changes and known limitations. GitHub's source ZIP contains project files, not the translation ZIP or a playable game.

**Hardware Vita rePatch:** use the local **Retro Trans 0.5.14** build. In **Vita**, choose **Hardware rePatch**, select the original Japanese PCSG00597 PKG and its matching `work.bin`, and choose a new output folder. Leave **Local patch** blank to download the hardware patch ZIP, or select `Cross-Ange-English-0.1.13-Vita-rePatch-patches.zip`. Click **Create rePatch**, then copy the generated `rePatch/PCSG00597` to `ux0:rePatch/PCSG00597` with VitaShell. Your original game must already be installed and a compatible rePatch plugin enabled. See [hardware instructions](docs/repatch-installation.md).

The hardware ZIP is about **5.4 MB**. The tools create the complete translated archive locally; rePatch overlays whole files, so this game needs about **902 MB** for its archive on the Vita. The overlay leaves the original executable, installed game and license unchanged. Physical-Vita gameplay and the manual credits page still need testing. This option does not use the custom Vita3K PKG.

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
