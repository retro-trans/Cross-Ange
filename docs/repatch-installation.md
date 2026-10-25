# Hardware Vita rePatch — Cross Ange PCSG00597

Use the original Japanese game **PCSG00597 v01.00**, installed on a hardware Vita
with a compatible [rePatch plugin](https://github.com/SonicMastr/rePatch-reLoaded).
The plugin redirects game file reads to `ux0:rePatch/<TITLE_ID>`; installation and
plugin setup are described by [the rePatch project](https://github.com/dots-tb/rePatch-reDux0/wiki).

You must have **Cross Ange's matching `work.bin`** (or compatible NoNpDrm `.rif`)
to extract the original PKG with the tools. A different game's license will not
work. A license is not supplied or downloaded. An already licensed cartridge or
official installation uses its existing license; the overlay does not install or
license the base game. Vita3K local PKG rebuilding and installation also require this game's matching license;
manual installed CPK patching does not.

1. Use **Retro Trans 0.5.18** and open **Vita → Hardware rePatch**.
2. Select the original Japanese PCSG00597 `.pkg` and its matching `work.bin`.
3. Choose a new output folder, with at least **6 GB free** for temporary work.
4. Leave **Local patch** blank to download the game's hardware patch automatically.
   This public release can be downloaded without GitHub sign-in.
   Alternatively select `Cross-Ange-English-0.1.16-Vita-rePatch-patches.zip`.
5. Click **Create rePatch** and wait for successful verification. The tools use
   an isolated official Vita3K runtime to decrypt your original locally, apply
   the archive delta and create the overlay. Emulator settings and saves remain
   untouched. Tools 0.5.18 is available from the [tools release page](https://github.com/retro-trans/retro-trans-tools/releases/tag/v0.5.18).
6. Close the game, back up saves and any existing overlay, then copy the generated
   `rePatch/PCSG00597` into **`ux0:rePatch/PCSG00597`** using VitaShell. Keep the
   existing game installation; do not merge an older translation or other mods.
7. Launch your installed original game with rePatch enabled. Check **v0.1.16**
   in the title footer. To remove the translation, move this overlay out of rePatch.

The download is about **5.4 MB**. Cross Ange loads its assets from a single archive,
so the generated overlay contains the complete translated `cpk/Ange.cpk`
(**902,331,208 bytes**), plus generated credit/attribution files. Allow about
1 GB on the Vita for it. The tool builds that archive from your own game; the
release contains a delta, not a full archive. Users do not manually patch a CPK.
The executable, original game files, licenses and save data are preserved.

This is a hardware overlay, separate from local PKG rebuilding or replacing the installed CPK in Vita3K.
No modified executable or `self_auth.bin` is needed for this asset-only translation.
The manual credit image and font attribution accompany the overlay, but access
to manual page 25 through the Vita's system viewer has not been verified.
Physical-Vita gameplay remains untested; file checks do not establish runtime
compatibility. Keep the original licensed game available for comparison.
