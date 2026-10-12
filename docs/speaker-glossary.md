# Speaker and character glossary — 0.1.2

Scanned all 13,277 parsed corpus rows: 57 unique speaker forms, including 551 narration rows with an empty speaker field. [speaker-labels.json](../work/glossary/speaker-labels.json) maps all 56 nonempty forms and two additional UI-only labels. All 39 character-name slots, UI IDs 664–702, have mappings. The glossary stores names, short roles, controls and provenance; no dialogue excerpts.

[characters.json](../work/glossary/characters.json) now contains 38 profiles, up from 32. Added Pamela, Perolina, Mary, Marika, Nonna and Tanya. Short aliases now resolve Momoka, Emma, Julio, Sylvia and other abbreviated names to their existing full-name profiles. Each label has a unique ID, corpus frequency, source-file counts, sample row IDs and matching UI slot offsets where present. Composite names preserve member order.

The exact `#z` and `#y` display prefixes remain in the `english` value; `english_label` contains only the readable label. DRAGON Vivian is a form of Vivian, and Jill (Base Broadcast) is Jill with a delivery qualifier. Neither gets a new character identity.

## Unresolved identities

- **Eunice / Eunice M:** 130 and 31 occurrences respectively, exclusively in `samplescript.txt`; one composite adds another Eunice mention. The [Naomi wiki](https://crossange.fandom.com/wiki/Naomi) calls the prototype-name interpretation unconfirmed. Possible link to Naomi is recorded separately, never asserted as fact. All 31 M rows are unvoiced parenthetical thoughts, suggesting an internal variant; the meaning of M needs runtime or stronger asset evidence. Preserve the suffix meanwhile. No separate Eunice character or inferred gender.
- **???**: 21 occurrences retain their concealed identity.
- **Perolina:** [official terminology](https://www.crossange.com/word/) establishes the mascot. [Vivian](https://crossange.fandom.com/wiki/Vivian) supplies the English spelling, while [Naomi](https://crossange.fandom.com/wiki/Naomi) describes a game costume wearer. Mascot gender stays unknown; identify the wearer per scene.
- **Generic roles:** only Female Teacher and International Rescue Fleet Woman state gender in their wording. Children, child soldiers, citizens, soldiers and radio operator remain gender-unspecified. The source fleet woman and UI fleet radio operator are distinct labels; shared identity is unverified.

## Research corrections and referenced names

[Vulcan](https://crossange.fandom.com/wiki/Vulcan) explicitly lists Male. [Riza Randog](https://crossange.fandom.com/wiki/Riza_Randog) explicitly lists Female and the alias Lizardia; her surname is verified. [Jurai Asuka Misurugi](https://crossange.fandom.com/wiki/Jurai_Asuka_Misurugi) confirms the canonical Jurai spelling and Male gender.

UI references establish **Mary** (1021), **Marika** (984), **Nonna** (1045) and **Tanya** (86; also 516). Each has a dedicated wiki gender citation and official personality/role citation in the profile: [Mary](https://www.crossange.com/character/me/), [Marika](https://www.crossange.com/character/ma/), [Nonna](https://www.crossange.com/character/no/) and [Tanya](https://www.crossange.com/character/t/). Later anime outcomes are not projected onto alternate game routes.

**Sylphis** is a DRAGON clan, not a character: [Lamia](https://crossange.fandom.com/wiki/Lamia) identifies her membership in the Sylphis Clan. The two observed references in `C081_PRO_000` belong in world terminology. No gender or invented mother named Sylphis is added. **Irma** and the nickname **Salako** had no exact-name hits in the scanned corpus/UI; no new observed profile/alias is claimed.

## Change log

- **0.1.2 — 2026-10-10:** Expanded profiles from 32 to 38; completed coverage of 56 nonempty speaker forms and 39 UI name slots; preserved controlled/composite labels; documented prototype and concealed identities; verified Vulcan/Riza genders and Riza/Jurai spellings. Translation remains paused.
