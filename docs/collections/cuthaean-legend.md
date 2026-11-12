# Cuthaean Legend of Naram-Sin (cuneiform tablets) (key `cuthaean-legend`)

Built 2026-11-12 by `scripts/import_cuthaean-legend.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (1 entry, 13 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Cuthaean Legend of Naram-Sin (Standard Babylonian version) | 180 | 180 | 175 | 13 | 7 |

Total: 175 of the 180 lines in the eBL edition (97%); 175 of the 180 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.12, Cuthaean Legend of Naram-Sin (ed. T. D. N. Mitto), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Excluded after checking:

- BM.36765: visual check: the obverse matches well: two columns divided by a double ruling, with 3 lines each (eBL o i 3, o ii 3). The reverse shows only about 6 lines and no visible column ruling, against eBL's iii 5 and iv 8. The ink number on the edge is written across a crack, and its last digit looks most like a 5 but could be read as 36766.

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Cuthaean Legend of Naram-Sin (Standard Babylonian version): 20-21: only on SU-1951.67.A; 169-171: only on SU-1951.67.A

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. BM.36765 was left out: its reverse shows about 6 lines with no column ruling where eBL attributes two columns (5 and 8 lines), and its ink number is hard to read. The Old Babylonian and Middle Babylonian versions are not included (no open photographs on eBL).
