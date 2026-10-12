# Contributing

Read `AGENTS.md`, `BASE_RULES.md`, the translation workflow and the relevant glossary before editing. Keep source IDs, voice references, formatting controls and source hashes intact. Review adjoining dialogue and flag uncertainty rather than inventing missing context.

Original game files, license keys, extracted artwork and Japanese scripts belong in ignored local folders. Export translations with `tools/strip_jp.py` before committing. Only English `*.en.json` catalogs are public; short Japanese glossary names and UI terms are allowed.

Run checks relevant to an edit, and describe what they establish. Native font edits must pass zero-token termination checks. UI/artwork changes need bounded pixel/layout checks and a live game test; passing static checks does not establish runtime correctness. New game builds must increment version, footer and credits together and record a changelog.

Report bugs through GitHub Issues with version, location, steps, device/emulator and a screenshot. Release publication requires an explicit maintainer request. The release assets must follow the Retro Trans standard and contain patches rather than full game binaries.
