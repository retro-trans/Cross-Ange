# Local test build 0.1.14

This build fixes the briefing overflow reported against 0.1.13. It is local;
no GitHub release was requested or published. The published release remains
0.1.13.

All 65 operation, heroine and side-mission descriptions are audited. Forty-two
needed reflow. Each generated line is at most 580 native advance pixels, and
each description has at most eight lines. The conservative panel dimensions
come from the supplied captures; blank paragraphs, complete wording and red
partner warnings are preserved. Only these description fields can change
line-break controls during BND relocation; other UI controls remain strict.

Terminology now uses **Light of Mana** for the named power and **Mana user**
for a person. Naomi's line is “The Light of Mana!?”; Chris's line is “She's a
Mana user, right?” Related mentions were corrected across 24 scenario records,
including sample-script counterparts. Glossary notes distinguish contextual
person references from the power itself. The [official setting reference](https://www.sunrise-world.net/titles/pickup_362.php)
supports that distinction; “Mana user” is our English translation choice.

Sixteen translation/font/layout checks, three branding checks and the glossary
audit passed. Both component deltas roundtrip exactly. The packaged Retro Trans
Tools 0.5.16 converted the local ZIP and verified all 48 files in an isolated
native Vita3K installation. All 46,048 native font records passed termination
checks. Original PKG/license, the user's installed game and saves were not
modified. Title footer and credits both show 0.1.14.

Actual gameplay and visual layout still need confirmation. The generated
native-glyph previews are layout proofs, not in-game captures. The existing
Naomi portrait-animation issue remains unresolved.

## Test locally

The installable package is
`work/output/cross-ange-0.1.14/Cross-Ange-English-0.1.14.pkg`.
Close the game and back up saves, then install that package in Vita3K using
Cross Ange's matching work.bin / compatible NoNpDrm .rif. Check v0.1.14 on
the title screen, then revisit Search for Ange and Time Attack: DRAGONs.

To reproduce the package with Retro Trans Tools 0.5.16, open **Vita → Vita3K
PKG**, select the original Japanese PKG, matching license, a new output
filename, and the local override
`work/output/cross-ange-0.1.14/local-patches/Cross-Ange-English-0.1.14-Vita-PKG-patches.zip`.
Automatic's online release discovery still selects published 0.1.13.

See [validation](local-build-0.1.14-validation.json),
[briefing geometry](../work/ui/briefing-body-layout.json) and
[terminology review](../work/ui/mana-terminology-review.json).
