# Installing the English patch — PCSG00597

Use your own original Japanese PCSG00597 game. Obtain decrypted game files locally; do not patch the encrypted PKG. Neither GitHub nor the patcher needs your license or `work.bin`.

## Patch the two components

Copy original `cpk/Ange.cpk` and `sce_sys/param.sfo` into one empty working folder, preserving their names. In the latest Retro Trans app, refresh the catalog and select that folder in Automatic mode. Choose **Cross Ange English components (PCSG00597)** and a new output folder. Both components are verified and patched as a group. The returned folder contains `Ange.cpk` and `param.sfo`; it is a set of translated components, not a complete game folder.

If the refreshed catalog does not list the release yet, download both xdelta assets and apply each through **Apply xdelta**, using the matching original source file. Compare the source and output hashes with `BUILD-MANIFEST.json`. The patches support the exact original source hashes; they are not upgrade patches for prior local builds.

Download the matching `Cross-Ange-English-<version>-extras.zip`, verify it against `EXTRAS-SHA256SUMS.txt`, then extract it into a separate folder. It includes only the newly generated manual credits page, font license, instructions and file hashes.

## Vita3K

1. Install your own game normally and close Vita3K. Back up the game's app folder and saves.
2. In the existing `ux0/app/PCSG00597` folder, replace `cpk/Ange.cpk` with the patched `Ange.cpk`, and `sce_sys/param.sfo` with the patched `param.sfo`.
3. Copy the extras' `sce_sys/manual/025.png` and `sce_sys/font-license.txt` to those same relative paths in the app folder. Keep original manual pages 001–024 and every other original file.
4. Restart Vita3K, launch the game and check the release version in the title-screen footer. Open the game Manual and navigate to page 25 for translation credits.

Keep license files, firmware, system fonts and savedata. The release does not provide or replace them. If restoring an earlier backup, close Vita3K first and preserve your current saves.

## Physical PS Vita

Physical-Vita runtime testing is not yet confirmed for this build. Use your own installed game and a compatible rePatch setup. Put the patched archive at `ux0:rePatch/PCSG00597/cpk/Ange.cpk`, and retain font attribution beside the overlay. Do not replace encrypted base app files with decrypted files. The translated `param.sfo` and appended manual page are tested as Vita3K app replacements; their physical-console metadata/manual placement is unverified. An existing official update or another mod may override the base archive and needs separate compatibility checking.

The Retro Trans **Vita rePatch — Z3** panel supports PCSG00264, not Cross Ange. Use Automatic or Apply xdelta with decrypted Cross Ange files as described above. No executable, authentication data, complete game package or license key is distributed.
