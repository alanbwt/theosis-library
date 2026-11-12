# Babylonian Theodicy (cuneiform tablets) (key `theodicy`)

Built 2026-11-12 by `scripts/import_theodicy.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (1 entry, 18 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| The Babylonian Theodicy (dialogue of the sufferer and his friend) | 288 | 284 | 258 | 18 | 10 |

Total: 258 of the 288 lines in the eBL edition (90%); 258 of the 284 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L II.1, Theodicy, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Excluded after checking:

- K.5932: visual check: only one face is photographed: a fragment about 4.5 cm wide with about 11 lines and no ink number visible. eBL attributes 45 lines in columns i, iii and iv, which must be on both faces. The linked pieces K.13859 (about 8 lines) and K.17598 (about 4) also show one face each, and two other parts of eBL's join (K.8491 and K.13929) have no photograph in this set, so only about 23 of the 45 lines are visible and the second face is not confirmed.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): BM.40098 (+ BM.40124), K.3452 (+ K.17474)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- The Babylonian Theodicy (dialogue of the sufferer and his friend): 89: no manuscript preserves it; 109-110-111-119: no manuscript preserves it; 157: no manuscript preserves it; 158-171: only on K.5932; 173-174: only on K.5932; 175: only on K.5932, K.17235; 192: only on VAT.10567, BM.66882; 290-293: only on BM.34773, BM.34633; 294-297: only on BM.34773, BM.34633, BM.66882

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. K.5932 was left out: its photograph shows one face with about 11 lines while eBL attributes 45 lines on both faces to the join, and two pieces of the join (K.8491, K.13929) have no photograph. Twenty-three lines of the poem have no English in eBL; where they appear, they are marked as such.
