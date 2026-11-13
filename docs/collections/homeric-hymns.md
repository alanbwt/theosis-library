# Homeric Hymns, Leiden manuscript (`homeric-hymns`)

6 entries, 82 sections (one per page column). Importer: `scripts/import_homeric-hymns.py` (column map in `COLUMNS`). Scans: `site/assets/scans/homeric-hymns/` (39 pages, fols. 31r-50r).

## Contents

| Entry | Lines in M | Folios |
|---|---|---|
| Hymn 1, To Dionysus (the end) | 10-21 | 31r |
| Hymn 2, To Demeter | 1-495 | 31r-36r |
| Hymn 3, To Apollo | 1-22, 74-546 | 36r-40v |
| Hymn 4, To Hermes | 1-580 | 40v-46r |
| Hymn 5, To Aphrodite | 1-67, 113-293 | 46v-48v |
| Hymns 6-18 (shorter hymns, in M's order 6, 7, 8, 9, 11, 10, 12-17, 18) | 6-17 complete; 18.1-4 | 48v-50r |

## Sources

- Manuscript: Leiden, Universiteitsbibliotheek, BPG 33 H ("Moscow" manuscript, M; paper, first half of the 15th century; found in Moscow in 1777 by C. F. Matthaei). The only witness of the Hymn to Demeter. IIIF manifest `https://digitalcollections.universiteitleiden.nl/iiif_manifest/item:1615207/manifest` (cached in `data/sources/homeric-hymns/leiden-bpg-33h-manifest.json`), Public Domain Mark. The library catalogue gives the hymn-level folio ranges.
- Greek: Evelyn-White, Loeb 1914, Perseus `tlg0013.tlg001-018.perseus-grc2` (CC BY-SA 4.0). Text the edition marks as lost in M is shown in square brackets (`<span class="lacuna">`).
- English: Evelyn-White 1914 (public domain), Perseus `perseus-eng2`.

## Mapping method

Two columns per page (a = left, b = right), 25-30 verses each. For every column the first and last verse were read on the image (top and bottom crops; full-column views where the text is irregular) and matched to the Greek, and every column boundary was checked from both sides. A later hand has written verse numbers in the margins; they follow an older numbering and were used only as a cross-check. English in five-line blocks placed by middle line (or the first line of the block that M has).

## What M lacks (not shown)

- Hymn 1: 1-9 (from Diodorus, not in M).
- Hymn 3, Apollo: 23-73 (M passes from 22 to 74; a marginal note marks the place); 136-138 (bracketed alternative to 139, not in M).
- Hymn 4, Hermes: 499.
- Hymn 5, Aphrodite: 68-112 (M passes from 67 to 113).
- Hymn 18: 5-12 (the manuscript ends at 18.4 on fol. 50r; 50v is blank).
- Hymns 19-33 are not in the collection: M breaks off at 18.4, so it does not carry them (they survive in other manuscripts). Every entry's introduction now says so (QC fix 2026-11-12).
- Lines the Loeb numbers with letters (Demeter 137a, 236a, 403a; Apollo 81a, 317a, 325a, 402a, 539a-b; Hermes 91a, 409a-b, 526a, 568a-b) are editorial supplements or variants and are left out. 137a, 236a, 317a and 526a were checked as absent on the page; the others were not checked one by one.
- Demeter 387-411 and 462-481 (fol. 35, badly damaged and repaired) survive only in part; the edition's restorations are in brackets.

## Other notes

- Apollo 376-378 are written twice in M (fol. 39r b), marked with χ.
- Gaps could be filled from other manuscripts (for Apollo 23-73 and Aphrodite 68-112, e.g. Florence, Laur. Plut. 31.32 or 32.45, both in the Teca Digitale). Not done.
