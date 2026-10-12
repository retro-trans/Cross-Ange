# Whole-PKG patching for Vita3K

The current v0.1.13 release applies one xdelta to your original encrypted PKG.
Patching does not read a license or run Vita3K. The matching license is needed
separately when installing the translated result in Vita3K. You must have
**Cross Ange PCSG00597's matching `work.bin`** (or compatible `.rif`); a license
from another game will not work. Licenses are never included or downloaded.
For hardware Vita, use the separate [rePatch route](repatch-installation.md).

## Automatic

Use your local Retro Trans **0.5.12** app or a later compatible build. Open
**Automatic**, browse to the original PKG, select a new output filename and click
**Patch**. The app downloads the matching whole-PKG ZIP and verifies source,
patch and complete output identities before saving. No license field is shown.

This release is public. Automatic downloads do not require a GitHub sign-in. Use the local Retro Trans 0.5.14 build for testing.
The tools 0.5.12 build is local; no tools release is implied by this game release
update. The older published tools 0.5.4 does not support this Automatic flow.

The release contains `VITA-PKG-XDELTA.json` and exactly one
`Cross-Ange-English-0.1.13-Vita-PKG-xdelta.zip`. Its flat inventory is the same
profile and `Cross-Ange-English-0.1.13-PKG.xdelta`. The approximately 945 MB ZIP
is large because rebuilding encrypted package data makes the binary delta large.
Allow about 3 GB free for the download, extracted delta and translated PKG if
they use the same drive, plus normal system headroom.

For a downloaded ZIP override, use **Vita → Vita3K PKG → Local patch (optional)**.
Do not select the retired `Vita-PKG-patches.zip`; the CPK/component route and old
license-based profile have been removed from the current release.

## Manual without Retro Trans

Download the whole-PKG ZIP and verify its hash against `SHA256SUMS.txt`.
Extract its `.xdelta`. In DeltaPatcher, set Original file to your Japanese PKG,
XDelta patch to the extracted whole-PKG delta, and Output file to a new English
PKG. With xdelta3:

```text
xdelta3 -d -s Original.pkg Cross-Ange-English-0.1.13-PKG.xdelta English.pkg
```

Neither method needs a license while patching. Compare the completed output
with `VITA-PKG-XDELTA.json`, then follow [installation](patch-installation.md).

## Supported original and output

| Property | Value |
| --- | --- |
| Title ID | `PCSG00597` |
| Content ID | `JP0700-PCSG00597_00-CROSSANGEGAME000` |
| Original bytes | `925548400` |
| Original SHA-256 | `962498429645bf92d0171280b075629ff6dc8100f365ce43805d2cd3e897ebcb` |
| English bytes | `944821248` |
| English SHA-256 | `59bd8f558f8b657d6a298fa0760b7867f67475c579d531fbfffa9c69143d7c8d` |

Existing English packages and other source revisions are not supported inputs.
The output includes the versioned footer, credits and font attribution already;
no separate extras installation is needed.

## Verification and limits

The English package was installed in isolated Vita3K and all 48 installed game
files matched the build. The whole-PKG delta reproduces that exact package.
See [native verification](pkg-patching-validation-0.1.13.json) and the release's
`VALIDATION.json` and `AUTOMATIC-VALIDATION.json`. Tools 0.5.12 passed 260 tests,
with four platform-specific skips, frozen startup and local complete-PKG checks.

Hashes and native installation do not establish full gameplay compatibility.
Existing translation/layout issues remain. The custom PKG is for Vita3K;
Sony signatures cannot be regenerated and physical-Vita installation is untested.

For maintainers, `tools/patch_pkg.py --build` can prepare an encrypted English
PKG from a local translation build using a matching local license. This is a
publisher-side operation, separate from the player patching flow above.
