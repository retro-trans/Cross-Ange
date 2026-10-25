# Vita3K upstream check and experimental fork

Checked upstream on 2026-10-25. GitHub and a fresh fetch agree that `master` is
`92bda548f3aa0691102471a72725587e00676383`, committed at 02:08:19 UTC that day
(09:08:19 Asia/Saigon). Its indexed-load translator still calculates
`idx * 2 + operand_offset`; the disassembler still describes that scaling.
Upstream shader cache version is 15. The locally tested correction is absent.

Also reviewed changes to the shader/renderer directories since the installed
`86b8e2eb` build and the existing
[Cross Ange compatibility report](https://github.com/Vita3K/compatibility/issues/655).
That report remains open, was last updated on 2024-04-08 and has no comments
confirming a HUD correction. New upstream renderer changes may affect other
artifacts; absence of this correction is a source finding, not a fresh runtime
test of upstream `master`.

Then downloaded official Windows build 4232 (`92bda548`) from
[Vita3K-builds](https://github.com/Vita3K/Vita3K-builds/releases/tag/4232) to
`work/output/vita3k-upstream-4232` and used its real `--recompile-shader` command
on all 12 local native programs. It emits the extra index scaling in every
program; all 256 scalar reads disagree with the native reference declarations.
All 12 emitted shaders compile independently with glslang. This verifies the
defect in the latest official binary's translator, without claiming a battle
retest. The executable, logs and configuration are isolated from user data.
See [the binary validation record](vita3k-hud-upstream-validation.json).

Created [retro-trans/Vita3K](https://github.com/retro-trans/Vita3K), authenticated
as binhlt0402, at the user's request. The branch
[`fix/cross-ange-indexed-uniforms`](https://github.com/retro-trans/Vita3K/tree/fix/cross-ange-indexed-uniforms)
starts from that exact upstream revision. Source commit
[`3da691c2`](https://github.com/retro-trans/Vita3K/commit/3da691c2)
removes the second index scaling, updates the disassembler and bumps the cache
version to 16. Fork documentation records the native reference evidence and
the limits of the cached-shader experiment.

CI commit `fbbdf3d3bab64e8f373bbabb962da42bc9c7f08f` adds a Windows-only test
artifact build using upstream's toolchain, build, CTest and packaging scripts.
The inherited multi-platform build excludes this experiment branch. No release
job was added; the new workflow has read-only repository permissions.

The four local reference/rejection regressions were rerun successfully,
including 256 scalar reads from the independently parsed native declarations.
Previously verified GLSL/SPIR-V results and the user's Vulkan improvement are
documented in [the investigation](vita3k-hud-shader-investigation.md). Full
emulator compilation and runtime validation are separate from those checks.

Successful Windows run:
[40204605165](https://github.com/retro-trans/Vita3K/actions/runs/40204605165).
The full emulator built successfully, both upstream CTest suites passed, and
the Windows artifact uploaded successfully (artifact ID `12604717171`,
38,704,992 bytes). The inherited formatting checks also passed.

Downloaded the artifact to `work/output/vita3k-hud-fix-fbbdf3d3`. Its actual
`Vita3K.exe --version` reports
`Vita3K v0.2.1 4234-fbbdf3d3-retro-trans/fix/cross-ange-indexed-uniforms`.
Ran that executable's real `--recompile-shader` command against the same 12
native programs in an empty portable directory. All 256 emitted scalar reads
now match the native references, and all 12 generated GLSL programs compile
independently with glslang 16.6.0. The official build's corresponding mismatch
count is 256; the fork's count is zero. The
[compiled-fork validation record](vita3k-hud-fork-validation.json) includes the
executable hash and per-program evidence. The repeatable local check is
`tools/verify_vita3k_hud_fork.py`.

The local executable is `work/output/vita3k-hud-fix-fbbdf3d3/bin/Vita3K.exe`.
It has not been installed over either existing emulator or tested in battle.
The remaining outlined quad, all radio and kill-counter states, other games
and physical hardware remain unverified. The portable validation directory
contains diagnostic output, not a configured game installation.

The old prototype checkout and emulator/cache backups are preserved. The new
source checkout is `work/source/vita3k-latest-hud-fix`. This work changes no game
bytes, licenses, saves, game version, translation assets or existing releases.
That build/validation stage created no upstream issue/PR or GitHub release.

## Subsequent release publication

At the user's explicit request, published
[`v0.2.1-cross-ange-hud.1`](https://github.com/retro-trans/Vita3K/releases/tag/v0.2.1-cross-ange-hud.1)
as an experimental Windows x64 prerelease. Its tag points to the exact tested
source commit `fbbdf3d3bab64e8f373bbabb962da42bc9c7f08f`.

The ZIP is the unmodified original CI artifact, not the local directory used
for shader testing. Its SHA-256 is
`e5a6dbe82886676340d2b486bffcd5d2d536218e53f9e3d27242fbbee6e2592b`.
The executable hash matches the validated build; `bin/COPYING.txt` is present
and no portable test data is included. The release also provides
`SHA256SUMS.txt`. Anonymous checksum download matches, and the public ZIP
returns HTTP 200 with the expected 38,704,992-byte length.

The [publication record](vita3k-hud-release-20261025.json) contains the release
identity, asset hashes and public download checks. The release notes retain
the gameplay/testing limits. No existing emulator, game, license or save was
modified, and no upstream issue/PR was posted.
