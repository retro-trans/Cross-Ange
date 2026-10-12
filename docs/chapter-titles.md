# Chapter-title artwork

The reported Chapter 1 heading means **Welcome to the First Squadron of Death**. Its English wording is already used by the translated save-menu title; the chapter card uses a separate image atlas.

The category contains **15 unique headings**, each present in two graphical variants: **30 title regions across two atlases**. They include the prologue, chapters 1–7, three Chapter 8 branches, two Chapter 9 branches and two Chapter 10 branches. The seven matching category assets are `sub_title_b.btx`, `sub_title_b_.btx`, their two BSA animation files, two BSW wrapper files and `sub_title_a.btx`, which contains background bars without Japanese text.

| Chapter | English title |
| --- | --- |
| Prologue (00) | A New Posting, and Then— |
| Chapter 1 (01) | Welcome to the First Squadron of Death |
| Chapter 2 (02) | Why I Fight |
| Chapter 3 (03) | A Cheerful Meal |
| Chapter 4 (04) | The First Squadron on the Brink of Annihilation! |
| Chapter 5 (05) | To Protect Smiles |
| Chapter 6 (06) | Infiltration! The Empire of Misurugi |
| Chapter 7 (07) | A Place for Each of Us |
| Chapter 8 (08A) | Those Who Know the Truth |
| Chapter 8 (08B) | Rebels Beneath the Sea |
| Chapter 8 (08C) | The World's Restorer |
| Chapter 9 (09A) | Joining Forces, Standing Together |
| Chapter 9 (09C) | Where Possibilities Converge |
| Chapter 10 (10A) | To the Other Side of the World |
| Chapter 10 (10C) | Trill—An Ever-Swaying Melody |

`work/translation/en/chapter-titles.en.json` links the title inventory to existing UI and raster draft IDs. Original English chapter labels/numbers, animation, background bars and pixels outside the title regions are retained. All 30 title regions are built and installed in **0.1.10**. Four chapter-title checks passed. Independent installed-archive readback verified both replacements and confirmed the five support assets are unchanged. The native animation samples a 344×64 rectangle; the last atlas column has 336 visible pixels. Longer English headings use two lines. Decoded previews and exact bounds are in `work/ui/chapter-title-layout.json`. The artwork is statically verified; in-game appearance is still pending.
