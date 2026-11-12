# Erra and Ishum (cuneiform tablets) (key `erra-and-ishum`)

Built 2026-11-12 by `scripts/import_erra-and-ishum.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (1 entry, 11 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Erra and Ishum, Tablet I: Erra roused to war | 191 | 191 | 134 | 11 | 8 |

Total: 134 of the 191 lines in the eBL edition (70%); 134 of the 191 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.5, Erra and Ishum, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): BM.35931 (+ Sp-III.855), K.8571 (+ K.19050), BM.36974 (+ 1880,0617.2683)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Erra and Ishum, Tablet I: Erra roused to war: 20-27: only on VAT.9162, SU-1951.122; 28-29: only on VAT.9162, IM.95180, SU-1951.122, IM.74442; 30: only on VAT.9162, IM.95180, SU-1951.122; 31-33: only on VAT.9162, SU-1951.122; 86-91: only on VAT.9162, SU-1951.122; 117-120: only on SU-1951.122; 121-125: only on SU-1951.122, VAT.10174; 126-129: only on SU-1951.122, VAT.9162, VAT.10174; 166-176: only on VAT.9162, IM.95180, SU-1951.122; 177-180: only on VAT.9162, SU-1951.122; 183-191: only on VAT.9162, SU-1951.122

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. eBL has edited only Tablet I so far (Tablets II-V have no lines in eBL), so Tablets II-V are not included. Lines only on the Ashur tablets (Berlin, Istanbul) are omitted.
