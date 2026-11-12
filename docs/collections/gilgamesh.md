# Epic of Gilgamesh (key `gilgamesh`)

Rebuilt 2026-11-12 by `scripts/import_gilgamesh.py` (re-runnable). Replaces the 19 earlier
per-tablet entries (Tablets I, VI and XI only, English by R. Campbell Thompson 1928); those
IDs now redirect to the new tablet entries (`redirects` in `data/collections/gilgamesh.json`).
The old entry JSON files and the old importer are kept as data in
`data/sources/gilgamesh/legacy/`.

## Contents (13 entries, 191 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| SB Tablet I | 300 | 300 | 231 | 18 | 6 |
| SB Tablet II | 187 | 186 | 118 | 17 | 6 |
| SB Tablet III | 209 | 208 | 164 | 17 | 8 |
| SB Tablet IV | 175 | 121 | 81 | 9 | 7 |
| SB Tablet V | 274 | 260 | 121 | 14 | 5 |
| SB Tablet VI | 183 | 183 | 182 | 14 | 7 |
| SB Tablet VII | 219 | 216 | 202 | 20 | 14 |
| SB Tablet VIII | 206 | 205 | 197 | 16 | 8 |
| SB Tablet IX | 137 | 135 | 135 | 7 | 2 |
| SB Tablet X | 325 | 306 | 276 | 13 | 3 |
| SB Tablet XI | 329 | 329 | 329 | 19 | 5 |
| SB Tablet XII | 139 | 135 | 135 | 15 | 7 |
| OB Yale tablet (YBC 2178) | 219 | 218 | 218 | 12 | 1 |

Standard Babylonian total: 2,171 of the 2,683 lines in the eBL edition (81%), or 2,171 of
the 2,584 lines that survive on any manuscript (84%). "eBL lines" counts the lines eBL edits;
lines lost on every manuscript are not in eBL's line list at all.

## Sources

- Original: eBL corpus edition L I.4 (ed. A. R. George, rev. G. Rozzi, E. Jiménez), manuscript-level
  ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: A. R. George's line-by-line translation in the same eBL edition, CC BY-NC-SA 4.0. It
  renders eBL's composite text; every section's scan_note says that bracketed restorations may come
  from other tablets. Thirteen lines of the SB chapters have no English in eBL; where they are published they are marked as such.
- Photographs: British Museum photographs served by the eBL fragment photo API
  ("(c) The Trustees of the British Museum, CC BY-NC-SA 4.0" per eBL); the Yale tablet from the
  Yale Peabody Museum IIIF service (CC0, manifest https://manifests.collections.yale.edu/ypm/nat/1833370).

## Mapping method

eBL lists, for every line of the poem, each manuscript carrying it with that manuscript's own column
and line numbers. For each line the importer takes the checked, photographed manuscript with the
most preserved signs, with a switching penalty so sections are runs on one column of one tablet
(max 30 lines). Faces are named only when certain (explicit o/r labels, or a six-column manuscript).

Every one of the 93 eBL photographs considered was looked at (contact sheets, plus full views of
K.3375, K.4465, K.2252, K.231, K.3252, K.3389, K.6899, K.2360, K.3382, K.8589, BM.34160, K.2774,
Rm.289, K.3423, K.8586, and the doubtful cases) and the result is recorded per tablet in
`GILG_CHECKS` and repeated in each section's scan_note.

Excluded after the visual check:
- K.913: eBL notes its photograph shows K.11913.
- BM.34916 (+BM.35419) and BM.34964 (+BM.35567): the photograph shows only a small piece
  with a handful of lines, while eBL attributes 139 and 31 lines to the joins.

Joins photographed in separate pieces (all piece photographs are linked, and the section says the
lines are on one of them): BM.34160, BM.35380, BM.34423, K.15193, K.3382, BM.34449, K.17343.
These are used only where no single-photo witness exists for a line (score penalty).

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph: Iraq Museum
(IM.67577, IM.76854, IM.76873, IM.76941, IM.76985, IM.67564), Berlin (VAT.17234, VAT.19286,
VAT.14512, VAT.14513, VAT.9667), Chicago (ISACM-A.3444), Ankara/Sanliurfa (Sultantepe tablets
SU-1951.129.A, SU-1951.7), the Sulaymaniyah tablet T.1447 (Tablet V 20-27, 85-90, 247-309),
a private tablet, and BM tablets whose eBL photograph is wrong or partial (K.913, K.2756.A,
BM.34916, BM.34964, BM.34191, K.8573, Rm.751, BM.93052 have no usable eBL photograph). The full
list per tablet is in each entry's introduction and `verification.lines_not_published`.

Old Babylonian: only the Yale tablet is included. The Pennsylvania tablet (CBS 7771, OB II) is in
the Penn Museum, whose image terms could not be confirmed (site refused automated access), and the
other OB pieces are in Baghdad, Chicago, the Schøyen Collection or Berlin.

## Open questions

- Nineveh fragments with only columns i-iii or iii-iv in eBL are not given a face (only the column),
  because the six-column layout is not proven from eBL data for them.
- BM.38538 col. i (2 lines) could not be seen on the photograph; only its column vi is used.
- Some British Museum photographs show the reverse above the obverse (K.8584, K.2756.D); the
  section names the face, so this does not affect the mapping.
- `data/pending/gilgamesh_texts.json` (written by the old importer) still lists the 19 old IDs;
  it is outside this collection's files and was left untouched.
