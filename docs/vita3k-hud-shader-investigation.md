# Indexed uniform correction: Vulkan improvement confirmed

Vita3K 4188 translates an indexed scalar register load as `idx * 2 + offset`.
In 12 Cross Ange vertex programs, the native shader already calculates the
float2 array displacement before writing `idx`. The extra scaling changes
both the first array entry and the stride. For the HUD shader beginning
`8a204ef9`, native `tanm` starts at scalar register 20; the original translation
reads 26 for element 0 and advances by four instead of two.

The experiment removes that second scaling. Its reference calculation parses
the original GXP parameter/container declarations and the actual I16MAD index
assignment. All 256 scalar lookups match the declared arrays after the change.
These are native-program reference checks, not a full hardware ISA conformance
test. A general emulator fix still needs broader testing.

## OpenGL result

Changed 24 expressions in 12 cached vertex shaders in the isolated original-game
copy only. All candidates compile with Khronos glslang 16.6.0, and four local
regression checks pass. The user reports that the top-right timer looks better;
the new capture also shows an aligned operator header. The large dark panel
and malformed radar remain. This is a partial improvement, not a complete fix.
The user asked to return to Vulkan.

## Vulkan candidate

The comparison profile is now Vulkan with High Accuracy and Memory Mapping
Disabled, matching the source cache's verified feature mask 25. Surface Sync
remains enabled from the previous isolated test. The source Vulkan cache came
from the user's read-only emulator cache; no user cache files were written.

In the same 12 vertex SPIR-V modules, replaced each of the two reviewed index
multiplications with an unscaled copy. Result IDs, module size and all unrelated
words are preserved; an OpNop fills the one-word instruction-size difference.
The patch matches only loads from `idx[0]` feeding the adjacent scalar offsets
14 and 15, and checks the native shader identity/array reference first.
Both original and edited modules pass Khronos SPIRV-Tools v2026.4 validation
for Vulkan 1.1. The validator was built locally from its pinned upstream tag
and pinned SPIRV-Headers dependency.

The isolated cache was backed up completely. Its old pipeline cache was moved
aside for a fresh pipeline load. The compatible 42-module cache was seeded and
the 12 changed modules read back exactly. The main emulator, game files,
firmware, licenses and save files are unchanged. No new game build, emulator
executable, release or source push was created.

Open `Compare Original - Cross Ange.lnk` in the project root and reproduce the
same battle. The user subsequently reports "much better now" on Vulkan: the
timer and speed panels align, the radar background is circular, and the large
dark block is absent. The 21:24 log confirms Vulkan High Accuracy and Mapping
Disabled. All 12 cached modules still match the candidate identities. This
confirms an improvement; a white outlined quad remains visible near the upper
right, and radio portrait/counter behavior across all states is not established. See
[OpenGL evidence](vita3k-hud-shader-candidate.json) and
[Vulkan module checks](vita3k-hud-vulkan-shader-candidate.json).

## Source prototype and rollback

The user subsequently requested a fork and a check of latest upstream. The
[upstream check and fork record](vita3k-upstream-check-20261025.md) documents the
current source branch and build status. The latest official build 4232 was
also checked through its real shader translator and retains all 256 incorrect
reads. The fork now compiles, passes both CTest suites and emits 256 correct
reads across the 12 affected programs; all generated GLSL compiles. This is
automated translator validation, with the rebuilt emulator's battle test still
pending. The older prototype below is preserved
for comparison.

The ignored checkout `work/source/vita3k-hud-fix` is pinned to
`86b8e2eb5cabd9be9d937e29b22dddf3904dd661`. A prototype changes indexed-load
arithmetic, its disassembly text and shader cache version. It has not been built
as a full emulator or submitted upstream. Its patch is local at
`work/source/hud-shader-probe/indexed-uniform-candidate.patch`.

The JSON evidence records backup folders. With the isolated emulator closed,
restore the recorded original shader files/cache and previous custom profile
to undo the experiments. Preserve the backups for comparison. The existing
main English profile is now Vulkan/High Accuracy/Mapping Disabled with Surface
Sync enabled, matching the successful comparison.

## English installation

After confirming the main English emulator was closed, backed up its complete
game-specific shader cache and profile. Applied the 12 verified Vulkan modules,
read them back, quarantined its old pipeline cache, and matched the successful
comparison GPU profile. The native cache header has version 13 and feature mask
25, so it matches this configuration. Global configuration, executable, game,
license and save files are unchanged. The running comparison was not interrupted.

The usual `Play Cross Ange.lnk` now starts the English installation with this
workaround. English battle confirmation is pending. See the
[installation and backup record](vita3k-hud-english-install-20261025.json).

This is a cached-shader workaround, not a rebuilt emulator executable. A
Vita3K update, cache reset or GPU-feature change can discard it. The source
prototype and backups are retained for a durable fix and rollback. That cache
installation did not produce a release or source push; the later emulator fork
is recorded separately above.

## Packaging boundary

All 12 affected native GXP programs were found byte-for-byte inside the original
executable ELF, with unique offsets; they are not standalone CPK shader assets.
The [location evidence](vita3k-hud-fix-packaging-boundary.json) contains hashes and
offsets only. Neither executable nor native programs were changed.

The current fix edits the code generated by Vita3K, so adding it to the existing
CPK/rePatch asset delta does not apply it. A future translation download can carry
an optional, version/feature-checked Vita3K compatibility component beside the
game patch. That installer is not yet packaged. The current cached-shader route
can be reset by cache or GPU-feature changes. A corrected emulator executable
would generate the right code after such resets. A corrected experimental
Windows binary has now been built and its translator checked, as recorded in
the [upstream/fork record](vita3k-upstream-check-20261025.md); it has not been
tested in battle or included in the game release.
Retain the original game executable and normal hardware rePatch route.
