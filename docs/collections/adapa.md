# Adapa (cuneiform tablets) (key `adapa`)

Built 2026-11-12 by `scripts/import_adapa.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (1 entry, 5 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Adapa (Standard Babylonian fragments) | 97 | 97 | 73 | 5 | 4 |

Total: 73 of the 97 lines in the eBL edition (75%); 73 of the 97 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.7, Adapa, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Adapa (Standard Babylonian fragments): a+1-a+14: only on MLC.1296; a+17: only on MLC.1296; d+1-d+9: only on MLC.1296

## Notes

The Middle Babylonian Amarna tablet (VAT.348, Berlin) and the Morgan Library fragment (MLC.1296) have no open photograph on eBL, so the Middle Babylonian chapter is not included and lines only on MLC.1296 are omitted.
