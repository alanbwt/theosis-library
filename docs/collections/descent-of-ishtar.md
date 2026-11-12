# Descent of Ishtar (cuneiform tablets) (key `descent-of-ishtar`)

Built 2026-11-12 by `scripts/import_descent-of-ishtar.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (1 entry, 5 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Descent of Ishtar to the Netherworld (Standard Babylonian version) | 148 | 148 | 138 | 5 | 1 |

Total: 138 of the 148 lines in the eBL edition (93%); 138 of the 148 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.8, Descent of Ishtar (ed. A. Setälä, rev. Z. J. Földi, A. Hätinen, E. Jiménez, G. Rozzi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Descent of Ishtar to the Netherworld (Standard Babylonian version): 11a: only on VAT.9729; 12a: only on VAT.9729; 18a: only on VAT.9729; 23a: only on VAT.9729; 97a: only on VAT.9729; 103a: only on VAT.9729; 118a-118c: only on VAT.9729; 137a: only on VAT.9729

## Notes

K.162 is published as two crops (obverse, reverse) of the British Museum photograph so the script stays legible; the crop boxes and the reason the upper face is the obverse are recorded in the importer. The short Neo-Assyrian version from Ashur (VAT.13833, 11 lines in eBL's NA chapter) is not included: it is in Berlin and eBL has no open photograph of it. Lines only on VAT.9729 (Ashur) are omitted for the same reason.
