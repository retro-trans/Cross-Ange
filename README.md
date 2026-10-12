# Cross Ange: Rondo of Angel and Dragon tr. — English patch

English fan translation of the PS Vita game **CROSS ANGE Rondo of Angel and Dragon tr.** (**PCSG00597**, Japanese release). The local PKG patcher takes your original game package and matching license and creates an English PKG for Vita3K. This repository contains English translation text, glossaries, layout records and tools; game packages, extracted artwork, licenses and local Japanese scripts stay outside Git.

## Applying the patch

The preferred Vita3K workflow is **original PKG + matching NoNpDrm `work.bin` or `.rif` → English PKG → install in Vita3K with the same license**. Download [Retro Trans 0.5.11 or newer](https://github.com/retro-trans/retro-trans-tools/releases/latest). In **Automatic**, browse to your original package, select its matching license, choose a new **Translated PKG** filename and click **Patch**. The app downloads the matching translation ZIP automatically. No existing installation or manual CPK editing is required. See [direct PKG patching](docs/pkg-patching.md) for the verified edition and CLI alternative. This custom emulator package is not Sony-signed.

**The repository and releases remain private.** Automatic downloads require a GitHub account with access; Retro Trans can use your existing GitHub CLI sign-in. Version 0.1.13 includes a declarative Vita PKG profile and a small ZIP containing both translation patches, credits and font attribution. Users supply their own game package and license; the release includes neither. For a local override, download `Cross-Ange-English-0.1.13-Vita-PKG-patches.zip`, open **Vita → Vita3K PKG**, select it under **Local patch (optional)** and click **Create translated PKG**. The existing decrypted-file Automatic and Apply xdelta routes remain available.

For the existing decrypted-file workflow, use [Retro Trans](https://github.com/retro-trans/retro-trans-tools/releases/latest):

1. From your own original decrypted game, copy `cpk/Ange.cpk` and `sce_sys/param.sfo` into one new working folder. Keep their names and preserve the originals.
2. Open **Automatic**, click **Refresh catalog**, then use **Folder…** to select that working folder. Choose **Cross Ange English components (PCSG00597)**, leave **Target** on **Latest**, and choose a new output folder.
3. Retro Trans downloads both matching patches and verifies the resulting files. Download the matching **extras ZIP** from [Releases](https://github.com/retro-trans/Cross-Ange/releases/latest) for the credits page and font license.
4. Follow [installation instructions](docs/patch-installation.md) to place the two output files and extras in the right directories. Restart the game and check the title-screen version.

Use Retro Trans 0.4.1 or newer for the grouped two-file solution; the latest version is recommended. This component workflow takes decrypted files. Use the preferred PKG workflow above to supply a PKG and license directly. The Vita tab also provides hardware rePatch for games with independently verified hardware profiles. The component catalog is refreshed after release publication; if a release has not appeared yet, use the manual steps below.

For manual patching, download both `.xdelta` files and the extras ZIP from [Releases](https://github.com/retro-trans/Cross-Ange/releases/latest). Use Retro Trans's **Apply xdelta**, Delta Patcher, or xdelta3:

```text
xdelta3 -d -s original/Ange.cpk Cross-Ange-English-0.1.13-Ange.xdelta english/Ange.cpk
xdelta3 -d -s original/param.sfo Cross-Ange-English-0.1.13-param.xdelta english/param.sfo
```

Create the `english` folder first. The patches require the exact original files listed in the release's `BUILD-MANIFEST.json`; existing local English builds are not supported upgrade inputs. [Release notes](https://github.com/retro-trans/Cross-Ange/releases) include source/output hashes, changes and known limitations. GitHub's source ZIP contains project files, not a playable game or the patch assets.

## Release status

**v0.1.13 is an early English local test build requiring proofreading and full playtesting.** Its rebuilt PKG passed an isolated Vita3K installation and all 48 installed file hashes matched the English build. Gameplay of this PKG has not been tested. Translation content is retained from 0.1.12: all 17,151 identified structured targets, including scenario dialogue and choices, speaker labels, UI, battle/navigation captions, gallery fields and system titles. All 15 chapter/prologue headings appear in both graphic variants, and all ten identified tutorial pictures have English text, including their embedded samples.

The build uses **GenEi LateGo v2 Medium**, native proportional character advances and pixel-width dialogue wrapping. Title branding and the appended manual credits page share the build version. Briefing/unit labels use compact display wording, and result time fields use **s** and **Left** to fit their fixed spaces.

File/patch verification does not establish that every scene renders correctly. New tutorial and battle-result layouts need live confirmation. A duplicate Naomi eye-animation tile remains unresolved; 24 other raster reading regions, the original manual prose and movie logos are pending. Some long dialogue uses native 80% size. There are 139 provisional equipment-name proposals requiring further review. Counts describe identified resources, not a whole-game completion percentage. See [build checks](docs/english-build.md), [current progress](docs/translation-progress.json) and [changelog](CHANGELOG.md).

## Check the translation

Use your own original game for comparison. The public [scenario](work/translation/en/corpus.en.json), [UI](work/translation/en/interface.en.json), [battle/gallery](work/translation/en/additional.en.json), [raster](work/translation/en/raster.en.json) and [system-title](work/translation/en/metadata.en.json) catalogs contain English, source IDs, hashes and review notes. Japanese dialogue is read from local extracted files, rather than distributed in Git.

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
