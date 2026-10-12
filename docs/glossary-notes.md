# Translation glossary — 0.1.3

Prepared 2026-10-10–11. **Build the glossary first, then translate.** The foundation preceded the resumed translation. The registry now contains **941 indexed records**, including intentional overlap between entity profiles, source labels and name components; [the audit](glossary-status.json) passes with no conflicts. This is not a count of unique canonical names or translated game rows.

## Database coverage

| Database | Contents |
|---|---|
| `characters.json` | 38 profiles: Japanese aliases, English names, sourced gender, personality and introductory role |
| `speaker-labels.json` | 58 exact labels: all 56 nonempty scenario forms plus two UI-only forms; all 39 UI character-name slots covered |
| `terms.json` | 32 base title/world/mecha terms; 20 historical proposed UI suggestions kept outside authoritative lookup |
| `observed-terms.json` | 3 additional scenario terms |
| `scenario-terms-a.json`, `scenario-terms-b.json`, `scenario-terms-c.json`, `scenario-terms-root.json` | Newly encountered terms, titles and roles, with occurrence references and evidence status |
| `gallery-terms.json` | Gallery specifications, outfit labels, observed ending names and music-title conventions |
| `manual-terms.json` | 14 original voice-credit names, Discord Phaser and No Makeup, observed in the manual |
| `world.json` | 23 world, organization, event and recurring game terms |
| `mecha.json` | All 42 mecha, enemy-class and other target-name slots, IDs 703–744 |
| `ui-terms.json` | 146 short labels, including all 30 location slots, stats, settings and result terminology |
| `equipment.json` | All 402 equipment names, 55 short category/stat labels and 36 name components |
| `name-policy.json` | Spelling locks, correction aliases and fields excluded from replacement |

The [coverage audit](glossary-status.json) checks exact source IDs/keys, frequencies, controls, equipment literals and overlapping source-slot names. It passes with no missing expected slots or source-slot conflicts. Short/full character-label differences are recorded as context variants. Japanese names and short UI terms are allowed by AGENTS.md; no Japanese dialogue is included.

## Lookup and source policy

Use an exact source-slot entry for UI, an exact speaker-label entry for speaker fields, and the researched entity profile for identity, gender and role. Component mappings help compose names but cannot replace a complete source-slot mapping. Keep all formatting codes, IDs, paths, model tokens and grades from the source. Plain glossary terms omit formatting prefixes for lookup; they are not ready-to-insert UI strings.

```powershell
python tools/glossary_lookup.py --source-id 710
python tools/glossary_lookup.py Howitzer
python tools/glossary_audit.py
# Read the preview before saving the audit.
python tools/glossary_audit.py --write
```

Follow the dedicated franchise wiki when source spellings disagree, as BASE_RULES requires. Primary Japanese pages establish source names and context; an English rendering remains a project convention unless its English spelling is directly supported. A citation for a base name does not verify every game variant. Historical proposed UI terms are excluded from lookup and never counted as observed or translated rows.

## Locked spelling and identity decisions

**Maggie, Villkiss, Salamandinay, Howitzer, Iaria, Dracunium, Dawn Pillar, Raziya, Theodra, Cleopatra, Victoria and Eirene** are preferred project spellings. The dedicated [Howitzer profile](https://crossange.fandom.com/wiki/AW-ZZR520_%28CR%29_Howitzer_Chris_Custom) wins over older Hauser prose. [Arzenal](https://crossange.fandom.com/wiki/Arzenal) and [DRAGON](https://crossange.fandom.com/wiki/DRAGON) support **Singularity** for the portal phenomenon. Short **Sala** is preserved in the source speaker label; it does not introduce a different character.

**Sylphis Clan** is a group, not a person: [Lamia's profile](https://crossange.fandom.com/wiki/Lamia) establishes clan membership. **Riza Randog** and **Jurai Asuka Misurugi** have dedicated spelling evidence. **Vulcan** is explicitly male in the dedicated wiki; unknown mascot or generic-role genders remain unknown. Profiles describe introductory roles, not every alternate game route.

The [official terminology page](https://www.crossange.com/word/) supplies Mana, Norma, Empire of Misurugi, Arzenal, Para-mail, Ragna-mail and Ryuu-Shin-Ki. DRAGON capitalization is the project convention. Use generic lower-case dragon only when scene context calls for it. Naomi's King of Debt nickname and intentional Radish Knights wordplay need scene-specific treatment.

## Uncertainties during translation

Equipment has **402 mapped names: 217 project conventions, 44 preserved literals, two wiki-verified full names and 139 provisional proposals**. The 21 names previously lacking English now have explicitly tentative literal/phonetic drafts. See [equipment research](equipment-glossary.md) for IDs and remaining research. Never silently treat a provisional proposal as verified.

Eunice and Eunice M occur only in leftover `samplescript.txt`. Their possible connection to Naomi is unconfirmed; keep their labels and uncertainty rather than inventing a new character or silently renaming them. Concealed ??? speakers remain concealed. See [speaker research](speaker-glossary.md).

The glossary is an extensible foundation. Image text and untranslated sentences may introduce additional terminology. New names must be researched and added before use. All drafts require meaning review and checking against this database. Scripted name normalization follows meaning review, and its locks become the reviewers' do-not-touch list. Scenario occurrence IDs document evidence; only integer UI IDs define exclusive display-slot mappings.

**Libertus**, **Para-mail** and **mail-rider** were normalized across finished drafts after meaning fixes; formatting codes remain untouched, including names immediately following a line-break code. Creature references use **DRAGON/DRAGONs**, while the **Dragon Princess** nickname remains unchanged. **Cooling Bullet** and **Freeze Bullet** remain separate observed terms pending gameplay evidence that they are the same weapon. The three literal gallery soundtrack renderings remain provisional; the [official soundtrack listings](https://www.crossange.com/bd_dvd/) establish Japanese-title provenance rather than official English spellings. Namahage is retained as a culturally specific name with [museum evidence](https://namahage.co.jp/namahagekan/en/oga_shinzan_folklore_museum/).

## Title convention

Use **CROSS ANGE Rondo of Angel and Dragon tr.**, combining [Sunrise's official singular English franchise title](https://www.sunrise-inc.co.jp/international/work/detail.php?cid=362) with the [game title](https://crossange.fandom.com/wiki/CROSS_ANGE_Rondo_of_Angel_and_Dragon_tr.). This is a project convention, not evidence of an official English game localization. TITLE retains the source newline after CROSS ANGE; STITLE is single-line. Metadata limits, font metrics and actual screen layout still require testing.

## Changelog

- **0.1.3 — 2026-10-11:** Completed the identified structured draft after establishing the glossary; expanded to 941 records with gallery/music, manual and scenario terms, retained provisional distinctions and applied checked canonical spelling fixes.
- **0.1.2 — 2026-10-10–11:** Expanded full-corpus glossary coverage, reconciled source-slot disagreements, verified spelling/identity corrections, added lookup/audit tools, and prioritized glossary before further translation.
- **0.1.0 — 2026-10-10:** Created the starter profiles and terminology with citations, a singular English title convention and separate unobserved UI suggestions.
