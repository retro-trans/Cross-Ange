# Naomi eye-animation issue

The user's 0.1.8 capture shows a second 128-pixel Naomi eye-animation tile near (443,456) during the scream in `C000_EPI_000:314`. The complete speaker portrait remains visible on the left. This is unresolved; build 0.1.9 does not claim to fix it.

The active `avc0` actor uses `NL_PLY_06_P000.btx` and `NL_PLY_02_P000_WINDOW_EYE.bsa`. Neither asset, its BSW references, nor the source episode command stream is changed by the translation. The line has no inline bitmap control. Native font glyph quads are 26x26 and cannot directly explain the 128-pixel tile. The English name `Naomi` matches localized string ID 664 and still selects `avc0`. The voice-animation update takes a fixed value, without text widths. `ADV_QUAKE` precedes the scream; its handler updates timers/offsets without creating a sprite. These findings narrow the investigation but do not establish that Vita3K causes the glitch.

The desktop testing helper failed twice to initialize with `failed to write kernel assets: The system cannot find the path specified. (os error 3)`. The agent could not perform a controlled runtime comparison.

With Vita3K closed, `tools/vita3k_portrait_compare.py` can select the original Japanese archive for the same scene, then restore the installed English archive. It verifies the current archive against the original and immutable English build before writing, refuses unknown edits or a running emulator, stages and hash-checks the replacement, and leaves saves, license, executable and configuration untouched. Switching between existing archives is a diagnostic selection, not a new build.

Two shortcuts in `work/output/cross-ange-0.1.9/` make this test available without typing commands: **Test Original Portrait** selects and opens the original archive; **Restore English Build** returns to English and launches it. Close Vita3K before each switch. Compare the same Naomi scream, then restore English. The shortcuts are prepared; the original archive has not been selected by the agent.

```powershell
python tools/vita3k_portrait_compare.py --mode original
python tools/vita3k_portrait_compare.py --mode original --write --launch
# Close Vita3K after comparing the same Naomi scream.
python tools/vita3k_portrait_compare.py --mode english --write --launch
```

If both modes show the eye tile, compare emulator rendering settings. If only English shows it, bisect the episode's text replacement and then fonts/kerning. Record the outcome before altering the original animation assets.
