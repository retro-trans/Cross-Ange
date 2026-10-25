# Local 0.1.16 candidate

This build was subsequently [published as v0.1.16](https://github.com/retro-trans/Cross-Ange/releases/tag/v0.1.16).
The notes below describe its original local preparation. See the current
[release notes](releases/v0.1.16.md) and
[published Automatic check](releases/v0.1.16-automatic-validation.json).

Timed-conversation bubbles are widened from 252 to approximately 336 pixels.
All 145 comments and 66 reactions using that bubble were checked; 161 entries
were rewrapped. Complete wording and thought markers are retained, with no
font reduction. All entries fit within four lines using the native GenEi
advances and the existing 85% timed-conversation text scale.

The animation changes only 12 horizontal width/position keys. Its left edge,
vertical animation, text origin, timer and choice bars are retained. All scene
anchors remain within the 960-pixel screen. The original executable is retained.
The title footer and credits were regenerated with version 0.1.16.

The [layout record](../work/ui/timed-dialogue-layout.json) documents all fitted
entries and changed native keys. The local preview at
`work/ui/local/timed-dialogue/layout-preview.png` uses original atlas slices
and native English glyphs. Its height is an estimate based on line count;
it is not an in-game capture. Runtime appearance still needs confirmation.

Local test files are under `work/output/cross-ange-0.1.16/`: the English PKG
and the small translation ZIP in `local-patches/`. The package uses published
Retro Trans Tools 0.5.16 with the original PKG and matching local license.
Install in Vita3K with this game's work.bin/.rif and check v0.1.16 on the title
screen, then revisit both reported timed-conversation lines and right-side
bubbles. No license is distributed.

The previous briefing/Mana and HUD artwork changes are retained. The existing
[battle HUD issue](battle-hud-issue.md) remains open; High Accuracy testing is
pending. This is a local candidate, with no release or source push. The user's
installed game, saves and running emulator are not updated by these build checks.
