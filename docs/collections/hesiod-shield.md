# [Hesiod], Shield of Heracles (`hesiod-shield`)

Complete poem (lines 1-480), 4 entries, 11 sections (one per manuscript page within each entry).
Importer: `scripts/import_hesiod-shield.py` (page map in `PAGES`). Scans: `site/assets/scans/hesiod-shield/` (8 pages).

## Contents

| Entry | Lines | Pages |
|---|---|---|
| Alcmene and the birth of Heracles; Cycnus at Pagasae | 1-77 | 248r, 248v |
| Heracles and Iolaus; the arming of Heracles | 78-153 | 248v, 249r |
| The Shield: its scenes | 154-326 | 249r, 249v, 250r |
| The fight with Cycnus and Ares | 327-480 | 250r, 250v, 251r, 251v |

## Sources

- Manuscript: Florence, BML, Plut. 32.16 (late 13th century), fols. 248r-251v, directly after the Theogony (Pinakes gives "249-253"; the poem in fact begins on 248r and ends on 251v). BML Teca Digitale IIIF, CC BY-NC-SA.
- Greek: Evelyn-White, Loeb 1914, Perseus `tlg0020.tlg003.perseus-grc2` (CC BY-SA 4.0). (The entries' verification fields cited the Theogony's id `tlg001` until the QC fix of 2026-11-12.)
- English: Evelyn-White 1914 (public domain), Perseus `tlg0020.tlg003.perseus-eng2`.

## Mapping method

Two verses to a row; first and last verse rows read on every page, continuity checked at every break. All page edges were re-read on the photographs on 2026-11-12 (`read_first` / `read_last` in `PAGES`). Page ranges: 248r 1-64, 248v 65-130, 249r 131-194, 249v 195-262, 250r 263-328, 250v 329-393, 251r 394-457, 251v 458-480 (corrected: 248v had been given 65-128 and 249r 129-194; the last row of 248v is 129 | 130). Also recorded: 250r row 1 has a struck-through repeat of 253 beside 263, and its lower-margin writing is a list of names (a genealogy for 327), not a verse; the line below the last row of 250v is verse 378, left out of the column, not a note.

English (QC fix 2026-11-12): at every page break the English is cut at the end of one of Evelyn-White's sentences (`ENGLISH_CUTS` in the importer, each chosen by reading his English against the Greek; shared code in `scripts/qc4_hesiod_english.py`). Where his sentence runs across the break it goes whole to the side nearer its end (ties stay with the page where it begins), so at most one sentence crosses a break; each section's scan_note gives the exact English line range. Spaces lost where Perseus footnotes were removed (e.g. "quick-glancingAphrodite", "capof") are restored: 27 places in the Theogony, 5 in the Shield.

## Notes and gaps

- fols. 250r and 250v each have a one-line note in the lower margin; they are not verses and were not transcribed.
- The edition has no line 298.
- The poem is usually dated to the 6th century BCE; the collection uses date_sort -580 and era "Classical".
