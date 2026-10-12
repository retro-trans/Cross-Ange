# Tutorial artwork and battle-result spacing — 0.1.12

The reported tutorial Japanese was inside native indexed textures. Translating structured dialogue did not replace that artwork. Seven previously drafted tutorial textures are now inserted, completing all ten identified tutorial pictures. The Japanese prose and embedded sample text in the deck and ROOM Part 2 captures are translated. GenEi LateGo v2 Medium is used throughout.

| Newly inserted texture | Content | Rendered text rectangles |
| --- | --- | ---: |
| EBG_108 | Deck: Shop, Hangar, Briefing, Sortie and embedded frame controls/help | 7 |
| EBG_110 | ROOM Part 2: Deck and embedded chapter/caption | 3 |
| EBG_111 | ROOM Part 3: Mission and embedded chapter/caption | 3 |
| EBG_112 | Mission selection: cash, rank, mission names and caption | 10 |
| ECG_043 | Touch markers, affection, condition and conversation window | 12 |
| ECG_044 | Conversation window, choices and embedded dialogue | 6 |
| ECG_045 | Choosing responses, controls and embedded choices | 8 |

These 49 rectangles represent 41 original draft regions; some prose and controls require multiple bounded rectangles. With the prior 35 tutorial rectangles and 30 chapter-title rectangles, 106 source regions are inserted into 114 rendering rectangles. All source hashes are guarded, every native palette/header is preserved, and every outside-region pixel index is unchanged. Emitted native previews were visually inspected. Tiny embedded text fits its original sample rather than using the full-screen dialogue font size.

The battle-result capture shows the full English time units colliding with neighboring fields. Shared UI ID 1481 now displays ** s** with a leading separator; ID 1480 displays **Left**. Full canonical translations remain **Seconds** and **Remaining**. Screenshot-derived checks allow 50 pixels for the seconds label and 68 pixels for the remaining label, conservatively measured at 18-pixel type size. Both fit. The same string-table IDs apply to all results using these time labels; numeric values, rewards and native font sizes are retained.

Twenty checks passed: thirteen translation/font/UI checks, four tutorial checks and three branding checks. The installer verified all 48 files, and independent installed-archive readback verified 483 replacement members, all 46,048 native font records, all ten tutorial textures and 13 display adaptations. Build footer and credits both show v0.1.12. Actual tutorial and result rendering need an in-game check. Source captures and decoded previews remain under ignored `work/ui/local/`; exact bounds are in `work/ui/tutorial-layout.json` and `work/ui/briefing-label-layout.json`.

The 24 other drafted raster regions, original manual prose and movie logos are still pending. No GitHub release was created.
