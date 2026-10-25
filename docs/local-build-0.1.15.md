# Local 0.1.15 candidate

This build improves battle HUD artwork readability and retains the 0.1.14
briefing/Mana fixes. It regenerates the version footer and credits together.
The scrambled HUD panels and cramped runtime counter units remain unverified;
this candidate does not claim to fix them. See [HUD investigation](battle-hud-issue.md).

Local files are in `work/output/cross-ange-0.1.15/`. The English PKG is rebuilt
from the original package through published Retro Trans Tools 0.5.16 using the
matching local game license. Its validation JSON records isolated installation
checks. The small component ZIP is available in `local-patches/` for the same
original-PKG workflow. These are local testing outputs, not a GitHub release.

Install the PKG in Vita3K with the matching game work.bin/.rif, retaining a copy
of your saves. Check v0.1.15 on the title screen. Compare the Freeze Bullet,
timer/speed and kill-count widgets during the same battle. The original game
currently installed in the user's emulator was preserved for a controlled check.

On 2026-10-25 the user's installed HUD assets matched this candidate, and the
new mission-start capture still showed missing left labels and flashing kill
icons. Readability was not established in game. A game-specific Vita3K High
Accuracy profile was applied separately for the next launch; its HUD result is
pending. It changes emulator settings without changing the 0.1.15 game files.
