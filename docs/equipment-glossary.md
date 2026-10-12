# Equipment glossary — 0.1.3

Prepared 2026-10-10–11. The glossary foundation preceded resumed translation. All equipment-name UI slots now have draft targets and source-free exports; research-open names remain explicitly provisional.

## Complete source coverage

`work/glossary/equipment.json` represents **all 402 `STR_ITM_*` rows**, numeric IDs **745–1146**, from the verified `strings.bnd` localization table. Every name has its exact source key, numeric ID, record offset, string offset, source byte length, and observed Japanese UI name/alias. No asset names or source IDs were translated. All **402 have English mappings**, including **139 provisional proposals**. The 21 previously null entries now have tentative literal or phonetic renderings with their research limitations recorded.

The glossary also contains **55 short equipment/category/stat labels** and **36 short name-component terms**. It includes **zero item descriptions or dialogue rows**. Long equipment help sentences were examined for category context and excluded from the glossary.

| Category | Source rows | Project conventions | Preserved literals | Wiki-verified names | Provisional names | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| Weapons and weapon gadgets | 165 | 0 | 27 | 2 | 136 | 0 |
| Parts | 60 | 60 | 0 | 0 | 0 | 0 |
| DRAGON attacks | 3 | 3 | 0 | 0 | 0 | 0 |
| Paints | 102 | 102 | 0 | 0 | 0 | 0 |
| Decals | 71 | 51 | 17 | 0 | 3 | 0 |
| None option | 1 | 1 | 0 | 0 | 0 | 0 |
| **Total** | **402** | **217** | **44** | **2** | **139** | **0** |

These statuses distinguish evidence levels. A project convention is a consistent English rendering of ordinary equipment terminology or a composite label using existing researched names; it is not a claim of official game localization. A provisional name is an explicit tentative spelling for a game-specific nickname or ornate weapon name. Having a target does not resolve its research status. The **402 mapped names are not 402 externally confirmed canonical names**.

Parts cover six families with ten original grades apiece: engine, main-wing controller, battery, transformer, coating, and actuator. Grade literals `ClassI`, `ClassH`, `ClassG`, `ClassF`, `ClassE`, `ClassD`, `ClassC`, `ClassB`, `ClassA`, and `ClassS` are retained exactly. `I` is retained as the source grade character, not converted to the number 1. Material/upgrade components distinguish prototype, initial type, modified type, Type Zero, custom, multilayer, composite, forged/refined materials, and scale-cutting blades. No new grade hierarchy or performance statistics were invented.

## Researched names and conventions

The existing character, term, and observed-term glossaries supply names for paint schemes and personal decals. The updated **Howitzer** convention replaces the older Hauser spelling throughout this equipment glossary, following the root agent's dedicated mecha/wiki and decrypted-manual comparison. The equipment file does not modify the base mecha glossary.

The [Villkiss wiki page](https://crossange.fandom.com/wiki/AW-CBX007_%28AG%29_Villkiss) verifies **Raziel**, **Ariel Mode**, and **Michael Mode**. The [official merchandise page](https://www.crossange.com/goods/69.html) independently establishes the Japanese Raziel short name. [Soryugo's dedicated page](https://crossange.fandom.com/wiki/Soryugo) supplies **Tenrai** and its photon-blade terminology. These references support the matching name components; they do not establish every game-exclusive weapon variant as canonical. In particular, the distinct source spellings at IDs793–794 are not silently merged with Type Zero Raziel at ID795.

[Victoria's dedicated page](https://crossange.fandom.com/wiki/EM-CBX005_Victoria) verifies Victoria for the corresponding paint entry. The wiki's [pilot index](https://crossange.fandom.com/wiki/Category%3APilots) supplies Mary and Marika Bellucci spellings, while [Nonna's page](https://crossange.fandom.com/wiki/Nonna) directly provides Nonna's Japanese and English name. Paint labels use short names without inventing full-name variants or gender information. Wiki name components and existing project glossary choices take precedence over speculative romanizations.

Broad searches did not establish reliable canonical English names for many game-specific weapons. Ordinary English nickname proposals such as Dragon Pain, Big Mama, and descriptive fantasy weapon names are therefore explicitly `provisional_name`. Mythological-looking names are not presented as independently verified etymologies. Peaky, Hazy Skull, and Drago decal interpretations are also provisional until their artwork is inspected.

## Remaining name research

The 21 previously unmapped rows are IDs **758, 760–763, 772, 832, 836, 839–840, 846, 848, 852, 854, 884, 890–891, 896, 898–899, and 904**. They cover an unverified beam-rifle entity name, ornate Japanese cannon/blade readings, and ambiguous weapon nicknames. Their provisional targets preserve distinctions and model codes without asserting an unsupported English etymology. The file records each specific reason. Shared variants use the same proposed base nickname.

Use the source keys and IDs to investigate related weapon models, readable game art/manuals, or stronger franchise references. Review provisional name proposals before using them as settled terminology. Equipment descriptions and actual in-game fit remain separate future translation tasks.

## Verification and local provenance

The source was the canonical archive export `work/source/ui-strings.json`; source-script content stays under ignored `work/source/`. The glossary was generated with an ignored local helper, previewed before writing, then validated against all 402 exact source rows. Checks confirmed complete/unique ID and key coverage, exact source offsets, retained model/grade/code substrings, and unchanged controls. Every stored preferred English value keeps all original ASCII model tokens, including combined suffixes such as `GBU-14G`, `IIG`, `IVH`, and `R/C`. Paint entries retain the literal `#z73` prefix where present.

The name list is allowed Japanese UI terminology under project rules; extensive Japanese script text stays in ignored local files. Equipment UI translations are now exported. No playable build, commit or release was produced.

## Changelog

- 0.1.3 (2026-10-11): Added 21 research-open proposals, completed all equipment-name drafts, preserved uncertainty flags and corrected three missing model/name spaces.
- 0.1.2 (2026-10-10): Indexed every equipment-name row, added category/stat/material/grade terminology, reused researched character/mecha names, documented model/control preservation, and recorded provisional and unresolved name decisions.
