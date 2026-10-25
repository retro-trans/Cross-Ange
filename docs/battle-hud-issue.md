# Battle HUD readability and displaced sprites

The user reported three cropped battle views: a difficult-to-read Freeze Bullet
counter, a red timer/counter with cramped units, and a kill panel with displaced
rectangular pieces. The originating game build is unknown. Original crops and
their hashes are kept locally in `work/ui/local/screenshots/hud-report-20261019/`.

The live artwork is in `data/_tex/UI01_BT_FRA01_00.btx` (timer, speed and Freeze
Bullet labels), `UI01_BT_FRA02_00.btx` (radar and kill panel), and
`UI01_BT_NUM01_00.btx` (two sizes of cyan/red counter digits). These are indexed
SHTXFS textures. The corresponding original `data/_chr/UI01_B*_*.bnp` models use
PSCa geometry with 72-byte vertex records and UVs at byte offsets 24/28. The
kill model includes repeated skinned icon quads; altering its texture alone does
not establish a fix for displaced geometry or incorrect runtime texture selection.

Build 0.1.15 replaces the labels and digits with GenEi LateGo v2 Medium, using
stronger raster strokes for small HUD text, and changes the low-contrast DESTROY
heading to dark KILLS on a light header. It retains both digit sizes and color
families, all native sampling cells, headers, complete palettes and every pixel
index outside the recorded cells. Radar and icon artwork, model positions, UVs,
skinning, animations, counters and the executable remain unchanged. Existing
0.1.14 briefing and Mana fixes are included. See `work/ui/battle-hud-layout.json`.

Three HUD regression checks verify complete native decode, unchanged unrelated
indices, counter slot size/color consistency and previews decoded from generated
bytes. The previews are atlas comparisons on a neutral background, not in-game
captures. They cannot establish final legibility at the game's projected HUD size.

At investigation time the installed `E:/Emu/vita3k/fs/ux0/app/PCSG00597/cpk/Ange.cpk`
matched the original archive SHA-256
`e04d94fac7ba1bc21acfd98c9ea8352995e32229c642485fb2537cd0d53213de`.
Vita3K 4188 was opened for a baseline check. The computer-use helper reached the
original LiveArea, then input and the one recovery attempt both failed with
`foreground window did not report a process id`. No battle comparison was
completed. The user could not check at this time. No emulator settings or game
files were changed; the local 0.1.15 package is prepared separately.

The displaced-panel bug remains open. Compare the same battle with the original
archive first, then with 0.1.15. If the original also glitches, compare renderer
accuracy/cache settings in a backed-up configuration. If only English glitches,
bisect the shared text/font changes before editing original model data. Neither
Vita3K nor the translation has been established as the cause.

## Mission-start report — 2026-10-25

The new user capture confirms that 0.1.15's artwork changes did not resolve the
missing left labels or flashing/incorrect kill-icon display. Eighteen installed
HUD members were read back: all five texture members match the 0.1.15 candidate,
and all thirteen model members remain identical to the original game. Evidence
is local in `work/source/hud-runtime-20261025/installed-hud-members.json` and
`work/ui/local/screenshots/hud-report-20261025/`. The numeric kill value cannot
be established from the corrupt display.

The active emulator is Vita3K 4188 (`86b8e2eb`), Vulkan, Standard accuracy with
Double buffer memory mapping. Its [synchronization handler](https://github.com/Vita3K/Vita3K/blob/86b8e2eb/vita3k/renderer/src/sync.cpp#L48)
waits for a GPU synchronization signal with mapped memory only when High Accuracy
is enabled. Otherwise it signals completion immediately. Its [renderer setup](https://github.com/Vita3K/Vita3K/blob/86b8e2eb/vita3k/renderer/src/vulkan/renderer.cpp#L933)
also changes framebuffer access and texture-viewport behavior with that option.
Buffer reuse/synchronization is a source-backed hypothesis for the symptoms,
not a confirmed cause.

An isolated copy of the original game, firmware, emulator and current save was
prepared. Both Qt and SDL reached the original title screen, but injected confirm
inputs did not advance it; a controlled battle comparison remains incomplete.
The test instance loaded a game-specific High Accuracy profile successfully:
the Qt status bar showed HIGH, and the log confirmed accurate framebuffer-fetch
emulation. The isolated process was then closed. This proves the profile is
accepted, not that it fixes the battle HUD.

`tools/vita3k_hud_accuracy.py` previews and, with `--write`, applies that profile
to `E:/Emu/vita3k/config/config_PCSG00597.xml`. Only effective `high-accuracy`
changes to true; the other GPU values are retained from the current configuration.
Other configuration sections continue to inherit the global values. The global
configuration, game, saves, licenses and caches are not written. The previous
profile, if any, and global configuration are backed up locally with a record.
The user's profile was applied on 2026-10-25 and takes effect when the game is
fully stopped and relaunched. The current session was left running.

The game remains 0.1.15; there is no new game build, release or source push.
High Accuracy may cost performance. Battle HUD stability/readability and the
actual zero-kill state still need confirmation after restarting the mission.

## Follow-up: speed, counter and radio corruption — 2026-10-25

The next user capture shows displaced speed/Freeze Bullet backgrounds, the
top-right counter and radio portrait. The radar and kill panel are malformed
as well. These are graphical panel/portrait defects beyond English word wrapping.
The exact cause remains unconfirmed.

The user's log at 18:23:28 confirms accurate framebuffer-fetch emulation with
Double buffer mapping, so High Accuracy was loaded in the later session. It
did not establish a complete HUD fix. A fresh readback of 18 installed HUD
members matches the prior audit: all 13 models remain original; the five
textures match the 0.1.15 candidate. The log also reports an invalid fragment
texture pointer at 18:33:20; this is recorded as evidence without attributing
the HUD defect to that error.

Prepared a single-setting diagnostic: keep High Accuracy on and change only
this game's Memory Mapping from Double Buffer to Disabled. The native
[settings list](https://github.com/Vita3K/Vita3K/blob/86b8e2eb/vita3k/gui-qt/src/settings_dialog.cpp#L336)
supports that value, and the
[renderer switch](https://github.com/Vita3K/Vita3K/blob/86b8e2eb/vita3k/renderer/src/vulkan/renderer.cpp#L1023)
selects a different memory-upload path. This is a hypothesis test, not a verified
fix; performance may differ. The custom profile and global configuration were
backed up, and global configuration is unchanged. Game files, saves, licenses
and caches were not written. No user process was interrupted.

The saved profile applies after fully exiting and reopening Vita3K. A battle
retest is pending. See [diagnostic evidence](vita3k-hud-mapping-20261025.json).
Restore Double Buffer with:

```powershell
python tools/vita3k_hud_accuracy.py --vita3k E:/Emu/vita3k --memory-mapping double-buffer --write
```

Game version remains 0.1.16; no new build, release or source push.

## Disabled mapping failed; OpenGL comparison prepared — 2026-10-25

The user retested and reported "Still displaced". The restarted 19:01 session
log explicitly confirms Memory Mapping Disabled and accurate framebuffer-fetch
emulation. This rules out a missed restart/profile load for that test; it does
not establish the underlying cause. The full retest log is retained locally,
and the [mapping record](vita3k-hud-mapping-20261025.json) now marks the test failed.

Changed only this game's `backend-renderer` from Vulkan to OpenGL after backing
up its current profile. Global configuration and every other profile field are
unchanged; the retained accuracy/mapping controls apply to Vulkan. This provides
a renderer comparison using the same English game and battle. Fully exit and
reopen Vita3K before retesting. OpenGL's startup and HUD result remain pending;
this is not yet a fix or proof that Vulkan causes the corruption.

See [OpenGL diagnostic record](vita3k-hud-opengl-20261025.json). Restore the earlier
Vulkan/Double Buffer profile with:

```powershell
python tools/vita3k_hud_accuracy.py --vita3k E:/Emu/vita3k --backend-renderer Vulkan --memory-mapping double-buffer --write
```

No cache deletion, game/save/license writes, process interruption, new game
build, release or source push occurred.

## OpenGL also failed; original-game comparison ready — 2026-10-25

The user reports "Still displaced on OpenGL" and supplies a capture with a large
dark panel over the left side, a detached radar background, malformed counter
and kill panels. The 19:23 startup log confirms an OpenGL 4.6 context, so this
is a completed renderer retest. Both Vulkan mapping configurations and OpenGL
have failed; the defect is not established as Vulkan-specific.

Prepared a separate original Japanese game using the same Vita3K executable
and OpenGL profile. All 46 original game files were checked byte for byte
against the decrypted source. The emulator binary matches the user's executable.
Both current save files were copied into the comparison filesystem and checked
for stability; its previous save/configuration was backed up. The user's game,
save files, configuration, caches and running process were preserved. No new
game build or release was created.

Open `Compare Original - Cross Ange.lnk` in the project folder after closing
the translated game. Load the copied save and reproduce the same battle. If the
original also glitches, the symptom reproduces without the translation; if the
original is correct, investigate the translation's changed members through
bisection. Original-game versus emulator behavior would still need a physical
Vita comparison. The original battle test is pending.

See [comparison identities and save snapshot](original-hud-comparison-20261025.json).
The local original copy is under `work/source/hud-runtime-20261025/emulator/`.

## Original Japanese game reproduces corruption — 2026-10-25

The user reports "Original HUD is also broken" and supplies a Japanese-captioned
capture with the same malformed radio portrait, radar, counters and large dark
panel. The isolated 20:19 log confirms OpenGL 4.6 and the original Japanese
title. All 46 original game files were reverified after the battle. The same
invalid fragment-texture-pointer error appears in this original-game run.

The modified game files are therefore not required to reproduce this symptom.
The game/emulator rendering path is the investigation target. This does not
prove an original-game hardware bug; no physical Vita or fresh original save
has been tested. Both tests used the same copied save for controlled comparison.
Evidence is in [the completed original comparison](original-hud-comparison-20261025.json).

Both renderer tests had Surface Sync disabled. Source review shows this setting
skips synchronization work in `renderer/src/scene.cpp` and the Vulkan surface
cache. Enabled Surface Sync **only in the isolated Japanese copy**, retaining
OpenGL and every other field. This is one controlled follow-up test, awaiting
a fresh launch through `Compare Original - Cross Ange.lnk`. No fix is claimed.

Restored the user's English profile to Vulkan, High Accuracy and Double Buffer
mapping after the unsuccessful OpenGL/Disabled tests. Its previous profile is
backed up. Global configuration, game files, saves, licenses and caches remain
untouched. See [surface-sync diagnostic and restoration](vita3k-hud-surface-sync-20261025.json).
No game build, release, upstream report or source push was created.

## Surface Sync retest also failed — 2026-10-25

The user reports "Still broken" in the isolated original game with Surface Sync
enabled. Its 20:38 startup log confirms OpenGL 4.6 after the profile change, and
the saved custom profile retains `disable-surface-sync="false"`. The log again
contains the invalid fragment-texture-pointer error. The option itself has no
explicit startup-log confirmation, so the record distinguishes saved profile
state and a fresh launch from a direct runtime flag readback.

No tested configuration has fixed the HUD. The English profile remains on the
restored Vulkan/High Accuracy/Double Buffer settings. The isolated copy retains
its last tested Surface Sync setting for reproducibility. No further settings
were changed after this failed retest.

Prepared a [local upstream report draft](vita3k-hud-bug-report.md) with the test
matrix and evidence links. No report was posted. The game/emulator/driver cause
remains unresolved; fresh-save and physical-Vita comparisons remain untested.

## Indexed shader candidate: partial improvement — 2026-10-25

Source/native-shader analysis identified an extra factor of two in indexed
uniform loads that disagrees with Cross Ange's float2 array declarations and
index-register arithmetic. An isolated OpenGL cache experiment corrected 24
lookups across 12 vertex programs. All 256 native reference cases and the GLSL
compiler checks pass. The user reports the top-right HUD looks better, while
the dark panel and malformed radar remain. This is partial runtime evidence.

At the user's request, returned the isolated comparison to Vulkan and ported
the same change to its SPIR-V modules. Both original and edited modules validate;
the native cache feature mask/profile is matched and old isolated pipelines are
backed up. Vulkan gameplay confirmation is pending. See the
[shader investigation](vita3k-hud-shader-investigation.md) for exact scope,
remaining defects, evidence and rollback. The user's main emulator and all game
and save files are unchanged. No full emulator executable was built or released.

## Vulkan improvement confirmed; English workaround installed — 2026-10-25

The user reports "much better now" and supplies a Vulkan capture with the timer,
speed panel and circular radar background aligned, and the large dark block
absent. The 21:24 startup log confirms Vulkan High Accuracy/Mapping Disabled;
all 12 changed modules retain their verified identities. Radio portrait and
all kill-count/icon states are not established by this capture. A white outlined
quad remains visible near the upper right; its role/cause is unconfirmed.

Applied the same cached-shader correction and successful GPU profile to the
closed main English emulator, with complete cache/profile backups and readback.
Global configuration, executable, game files, licenses and saves were preserved.
The running comparison copy was left intact. English battle confirmation is
pending. The usual Play shortcut uses this English installation.

See [English installation record](vita3k-hud-english-install-20261025.json).
Vita3K updates, cache resets and GPU-feature changes can discard the workaround;
a persistent emulator build remains future work. No game build or release.

## Experimental emulator and game releases — 2026-10-25

The subsequent [Vita3K fork release](https://github.com/retro-trans/Vita3K/releases/tag/v0.2.1-cross-ange-hud.1)
contains the persistent source correction. Windows compilation, both upstream
CTest suites and all 256 native reference reads pass. Its built translator's
12 generated shaders also compile independently. This rebuilt executable still
needs battle testing; the remaining quad and all radio/counter states are
unverified.

[Cross Ange v0.1.16](https://github.com/retro-trans/Cross-Ange/releases/tag/v0.1.16)
is published separately with the unchanged game executable. Its patch bundles
do not include the emulator correction. Published Tools 0.5.18 Automatic
reproduces the exact native-verified PKG and all 48 game files. Game layout,
full gameplay and physical-hardware testing remain outstanding.
