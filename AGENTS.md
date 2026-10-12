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
- The user restored original-PKG Automatic with small component downloads and local decryption/re-encryption. Users supply the original PKG and matching local work.bin/.rif during patching, then use that license during Vita3K installation. Distribute VITA-PKG.json and the approximately 5.4 MB component/extras ZIP; never revive the approximately 945 MB whole-PKG xdelta. Retain manual installed CPK deltas and hardware rePatch. This explicitly supersedes the prior CPK-only and license-free whole-PKG preferences. Preserve originals, licenses, emulator data/saves, game bytes/version and the currently authorized repository visibility.
- The active Retro Trans Tools checkout is ../retro-trans-tools. Keep original-PKG Automatic/local profile rebuilding, hardware rePatch and binary CPK routes generic through reviewed manifests. PKG rebuilding/extraction needs the matching local license; direct CPK patching does not. Licenses are never bundled/downloaded. Local builds do not authorize tools source pushes or release publication.

- Use https://github.com/retro-trans/ACE-3 as the README and release template. Publish under retro-trans/Cross-Ange using binhlt0402 only when explicitly requested. Current authorized distribution is small verified component patches/extras for local licensed PKG rebuilding, manual installed CPK deltas and a hardware rePatch bundle. Keep whole-PKG xdelta profiles/downloads withdrawn. Installation requires the matching game work.bin/.rif; another title's license will not work. Preserve the original executable; physical-Vita gameplay remains unverified.
- Match the section order in https://github.com/retro-trans/ACE-3/releases for game releases: Apply (recommended app route, manual source/patch table, commands and identities), What's included (first public release; no change-history section), Release status, How it was translated, Acknowledgements, Source code and Contribute. Use this game's facts, credits and supported inputs; retain verified limitations and the current visibility authorized by the user.
- The user explicitly authorized making retro-trans/Cross-Ange and its existing v0.1.13 release public after restoring small-download local PKG rebuilding. This supersedes the prior request to keep it private. Keep release notes concise and describe this as the first public release: replace change history with What's included. Public patch downloads do not require GitHub sign-in. Preserve small-download/manual/rePatch assets and historical visibility evidence. The user subsequently explicitly authorized publishing tools 0.5.16, including its source push. Future versions still need explicit release permission.

- Retro Trans Tools 0.5.16 is explicitly authorized for public Windows release; current game instructions should link that published version rather than describe it as local-only. Preserve game build 0.1.13 and the existing patch assets.
