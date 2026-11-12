# Counsels of Wisdom (cuneiform tablets) (key `counsels-of-wisdom`)

Built 2026-11-12 by `scripts/import_counsels-of-wisdom.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (1 entry, 17 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Counsels of Wisdom (Babylonian moral advice) | 159 | 159 | 157 | 17 | 13 |

Total: 157 of the 159 lines in the eBL edition (99%); 157 of the 159 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L II.3, Counsels of Wisdom (ed. Z. J. Földi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): K.8282 (+ K.18284), BM.33851 (+ BM.32989), K.8231 (+ K.8638), BM.33496 (+ BM.48897, BM.48908, F.60)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Counsels of Wisdom (Babylonian moral advice): A+1: only on VAT.17157, CBS.6059; A+2: only on CBS.6059

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. K.8282 shows only part of the reverse lines eBL attributes to it; the rest is on the joined piece K.18284, whose photograph is linked with it.
