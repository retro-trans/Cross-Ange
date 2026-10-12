# Briefing and shared unit-label layout — 0.1.11

The 0.1.10 game captures show mission-condition headings overlapping their bullet lists and long unit-stat labels reaching into the next column. The time limit also concatenates its number and English unit without a space.

The native UI strings are shared by other briefing missions and hangar/shop stat panels. This build uses compact display wording for eight stat labels and two condition headings, plus a leading separator in the appended time unit. Canonical translations, condition descriptions, equipment names, values and native font sizes are retained.

| ID | Canonical wording | Compact display |
| --- | --- | --- |
| 321 | Attack Power | Attack |
| 323 | Shooting Accuracy | Accuracy |
| 324 | Shot Grouping | Grouping |
| 325 | Effective Range | Range |
| 329 | Boost Capacity | Boost |
| 330 | Turning Performance | Turning |
| 332 | Heat Recovery | Cooling |
| 335 | Support Type | Support |
| 457 | Success Conditions | Success |
| 458 | Failure Conditions | Failure |
| 460 | Minutes | Minutes (with a leading space) |

All 16 stat fields were checked against a conservative 84-pixel label allowance; the two condition headings use an 85-pixel allowance. Coordinates come from actual 960×544 captures; validation font sizes are conservative checks rather than confirmed native renderer sizes. Source captures and a label-width preview remain in ignored local storage. The English adaptation inventory is `work/translation/en/ui-compact-labels.en.json`, and coordinates are in `work/ui/briefing-label-layout.json`.

Thirteen translation/font/layout checks and three branding checks passed. Independent comparison with 0.1.10 found exactly 11 changed UI fields and confirmed every other table field and translation member is identical. Only the UI table and version-footer atlas differ among archive replacements; the credits page is regenerated for the new version. All 46,048 native glyph records pass zero-token validation.

Build 0.1.11 was installed and its title footer was observed in Vita3K. Computer Use was stopped by the user before inspecting briefing panels; no live overlap pass was recorded. Build 0.1.12 retains those fixes and adds two battle-result time-label adaptations. See [the result audit](tutorial-result-fixes.md). Briefing and result layout still need live verification.
