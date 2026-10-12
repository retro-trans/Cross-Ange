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
- The user returned to installed CPK patching: install the original Japanese PCSG00597 game in Vita3K with its matching work.bin/.rif, close the emulator, patch the installed Ange.cpk to a new file using the small delta, verify it and replace with a backup. Restore the optional param.sfo delta and credits/font-attribution extras. Withdraw whole-PKG profiles/downloads and local tools 0.5.12–0.5.14 builds because their approximately 945 MB delta is too large. Keep historical native PKG proofs, game build bytes/version and repository privacy. This supersedes the earlier direct-PKG preference. Never modify user saves or the real installed game without installation authorization.
- The active Retro Trans Tools checkout is ../retro-trans-tools. Keep standard binary Apply xdelta/Automatic generic and hardware rePatch profile-based for future games. Installed CPK patching needs no license; original-game installation and hardware PKG extraction need the matching local license. Licenses are never bundled or downloaded. A local build does not authorize tools source pushes or release publication.

- Use https://github.com/retro-trans/ACE-3 as the README and release template. Publish under retro-trans/Cross-Ange using binhlt0402 only when explicitly requested. Current authorized distribution is verified installed CPK/component deltas plus credits/font extras for Vita3K, and a separate hardware rePatch bundle. Keep whole-PKG and legacy license-based PKG profiles withdrawn. Installation requires the matching game work.bin/.rif; another title's license will not work. Preserve the original executable; physical-Vita gameplay remains unverified.
- Match the section order in https://github.com/retro-trans/ACE-3/releases for game releases: Apply (recommended app route, manual source/patch table, commands and identities), What changed since the previous release, Release status, What's included, How it was translated, Acknowledgements, Source code and Contribute. Use this game's facts, credits and supported inputs; retain verified limitations and the current visibility authorized by the user.
- The user reversed temporary public access and explicitly requested making retro-trans/Cross-Ange and its existing v0.1.13 release private again because the approximately 945 MB whole-PKG download is too large. Keep the repository and release private until explicitly instructed otherwise. Private release downloads require an account with repository access. Hardware Automatic can use GitHub CLI sign-in; private CPK patches use manually downloaded deltas in Apply xdelta. Retain public/private verification records as historical evidence. This request does not authorize a new tools release or source push.
