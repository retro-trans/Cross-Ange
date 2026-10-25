# Cross Ange PCSG00597: displaced HUD geometry and dark panels

Local report draft; not submitted upstream.

The same battle HUD corruption reproduces with the original Japanese game
files and the English translation. The speed/Freeze Bullet panel, timer,
operator portrait, radar and kill display contain displaced or incorrectly
sampled pieces. OpenGL additionally shows a large dark rectangle over the left
of the viewport. Kill icons flash or appear inconsistent with mission progress.
The true numeric kill count cannot be read reliably from the broken panel.

## Environment

- Vita3K v0.2.1, build 4188, commit `86b8e2eb`.
- Windows 11, NVIDIA GeForce RTX 3070 Ti.
- OpenGL log: `4.6.0 NVIDIA 610.88`.
- Cross Ange: Rondo of Angels and Dragons tr., `PCSG00597`, original v1.00.
- Internal resolution multiplier 1; Bilinear output filter.
- Original and English comparison executables have identical emulator hashes.
- All 46 original game files match the decrypted source before and after testing.

## Reproduction observed

1. Launch the original Japanese game in the isolated comparison installation.
2. Load the copied save and enter the same battle used for the English test.
3. Observe the speed/counter widgets, operator portrait, radar and kill panel.

Expected: panel backgrounds, digits, portrait and icons remain aligned, and the
radar has its circular background. Observed: displaced pieces and a large dark
panel, visible in the supplied Japanese-captioned capture. Exact mission ID
was not captured; an escort-target operator caption is visible.

| Game | Renderer/settings | Result |
| --- | --- | --- |
| English, installed 0.1.15 HUD artwork | Vulkan, High Accuracy, Double Buffer | Displaced HUD |
| Same English game | Vulkan, High Accuracy, Mapping Disabled | Displaced HUD; setting confirmed in restarted log |
| Same English game | OpenGL | Displaced HUD plus dark panel; OpenGL context confirmed |
| Verified original Japanese game | Same OpenGL settings, Surface Sync disabled | Same corruption; Japanese screenshot and original files verified |
| Same original Japanese game | OpenGL, Surface Sync enabled | User reports still broken after fresh launch |

The original comparison uses a copy of the same save for controlled progress.
A fresh original-game save and physical Vita have not been tested. Reproduction
without patched game files establishes that those files are not required for
the symptom; it does not isolate every possible save/game/driver/emulator cause.

## Logs and evidence

Both original and English runs emit:

```text
sceGxmSetFragmentTexture returned SCE_GXM_ERROR_INVALID_POINTER (0x805B0004)
```

This error is correlated evidence; its causal role is unconfirmed.

- [Original-file comparison and screenshot identities](original-hud-comparison-20261025.json).
- [Vulkan Disabled mapping retest](vita3k-hud-mapping-20261025.json).
- [OpenGL retest](vita3k-hud-opengl-20261025.json).
- [Surface Sync retest](vita3k-hud-surface-sync-20261025.json).
- Local screenshot: `work/ui/local/screenshots/hud-report-20261025/original-japanese-also-broken.png`.
- Local final original log: `work/source/hud-runtime-20261025/original-surface-sync-failed-battle.log`.

No game package, license or save is included in this draft. Logs and screenshots
remain local. A later indexed-uniform cache experiment now shows a confirmed
Vulkan improvement: aligned timer/speed/radar background and no large dark block.
It is not a complete or persistent emulator fix; English installation testing
and remaining artifacts are still open. See the
[shader investigation](vita3k-hud-shader-investigation.md).
The existing [compatibility report](https://github.com/Vita3K/compatibility/issues/655)
is a possible upstream destination; this draft has not been sent there.
