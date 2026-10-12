# Installing the English PKG — PCSG00597

Patch your original Japanese package through Retro Trans 0.5.12's **Automatic**
tab, or use the whole-PKG delta with an external patcher. See [PKG instructions](pkg-patching.md).
Patching does not request `work.bin`/`.rif`. You must have the **PCSG00597 game's matching `work.bin`** (or compatible `.rif`) to install the result; another title's license will not work. The hardware Vita route is documented separately in [rePatch instructions](repatch-installation.md).

1. Back up any existing Cross Ange saves before installation and close the game.
2. In Vita3K, select **File → Install .pkg** and choose the translated English PKG.
3. Supply your own matching Cross Ange `work.bin` or `.rif` when Vita3K asks for
   its license. A license for a different title will not work.
4. Restart the game and confirm **v0.1.13** in the title-screen footer.
5. Open the Manual and go to page 25 for translation credits. Credits and GenEi
   font attribution are already inside the translated package.

Do not replace extracted game archives or install separate extras. The patcher
preserves its original input and rejects existing output filenames. It does not
modify the user's emulator installation, firmware, licenses or saves.

This custom PKG is intended for Vita3K. It is not Sony-signed or verified for
physical-Vita installation. Full playtesting and proofreading remain pending.
