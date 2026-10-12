** Organize folder like this **
work - work folder
    output - contains the file for testing (iso, zip, etc...)
    glossary - contains the one or many json files for glossary
    ui - contains screenshot of actual UI element ingame with label on screenshot if possible, contains files (json,py,...) describe the coordinate, width and height, id and other attributes
    translation/<language code> - contains the target translation of ui element or dialogues or anything that need translation
docs - documents
tools - any tools help with translation
incoming - outside files that need agent to look into

** SOME RULES **
- Avoid contains extensive Japanese scripts (UI elements is fine)
- Identified each build with version 0.x.y (start at 0.1.0)
- Always write change log
- If user told you to remember anything write it down here, make sure to ask user if the new one conflict with old one
- Do not create or publish a GitHub release until the user explicitly requests a release for that build. Translation and local builds do not imply release permission.
- Be conscious of subscription limit before creating sub-agents
- Consider using https://github.com/nationalsecurityagency/ghidra if applicable

** REMEMBER **
- Native BNF font records must end with a zero token. Validate every glyph with `tools/bnf_codec.py` and the native termination regression; a length-bounded FCAA decode alone misses this requirement and caused the 0.1.7 startup crash.
- Use GenEi LateGo v2 Medium from the user's requested Genei Latin package (https://okoneya.jp/font/genei-latin.html) for English game glyphs, title footer and translation credits. Generate native proportional advances with the glyphs, fit English dialogue by pixel width, retain its OFL 1.1 license and attribution, and preserve unrelated original glyphs.
- Use Latin colon spacing in English dialogue; its bitmap uses two GenEi period dots at the baseline and nine pixels above it.
- Include a translation credits page and a white, right-aligned title-screen footer with `v0.x.y` above `github.com/retro-trans`, following the user's reference. Keep the original game copyright notice. Every new build must increment the version and regenerate both the footer and credits from the same version; use `tools/build_branding.py` and record the build in the changelog.
- Every new github release must work with [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools).
- Japanese script text must never be committed to git. Keeping it in local working files is fine: `.gitignore` covers `work/source/` and the translation working files. Commit only the `*.en.json` copies written by `tools/strip_jp.py` (run it before committing). Names and UI terms in Japanese are allowed.
- The user prefers direct PKG input and PKG output for Vita3K, with whole-PKG xdelta applied to encrypted bytes. Player patching must not request or read work.bin/.rif; the matching license is supplied separately during Vita3K installation. Publisher-side local game builds may still use `tools/patch_pkg.py` and a matching local license to prepare and verify encrypted output. Preserve originals and existing emulator data. Keep full PKGs local; explicitly requested releases distribute verified translation deltas/tools with Retro Trans Tools compatibility. Custom PKGs are not Sony-signed or verified on hardware. The user authorized updating the existing 0.1.13 release to the whole-PKG flow and removing its CPK/component assets. Disclose its approximately 945 MB download; do not describe this package-size delta as a small patch. Verify published Automatic discovery and patching before retiring the old assets.
- The active Retro Trans Tools checkout is `../retro-trans-tools`. Keep Vita flow generic for future games: destination selection and release profiles rather than game-specific UI. Whole-PKG mode uses VITA-PKG-XDELTA.json and a flat ZIP containing that profile and its delta; old VITA-PKG.json is the withdrawn per-file flow. Licenses are never bundled or downloaded automatically. A local tools build does not authorize source pushes or release publication.

- Use https://github.com/retro-trans/ACE-3 as the README and GitHub release presentation template. Publish this project under retro-trans/Cross-Ange using binhlt0402 when publication is explicitly requested. Release only verified whole-PKG deltas, profiles and verification records, compatible with Retro Trans Tools; retire the public CPK/component and separate extras route.
- Match the section order in https://github.com/retro-trans/ACE-3/releases for game releases: Apply (recommended app route, manual source/patch table, commands and identities), What changed since the previous release, Release status, What's included, How it was translated, Acknowledgements, Source code and Contribute. Use this game's facts, credits and supported inputs; retain verified limitations and privacy.
