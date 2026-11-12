# Ludlul bel nemeqi (cuneiform tablets) (key `ludlul`)

Built 2026-11-12 by `scripts/import_ludlul.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (5 entries, 68 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Ludlul bel nemeqi, Tablet I: the anger of Marduk and the loss of favour | 120 | 120 | 117 | 17 | 8 |
| Ludlul bel nemeqi, Tablet II: illness and despair | 120 | 120 | 120 | 16 | 5 |
| Ludlul bel nemeqi, Tablet III: the dreams of deliverance | 121 | 120 | 108 | 19 | 7 |
| Ludlul bel nemeqi, Tablet IV: restoration | 53 | 52 | 42 | 9 | 4 |
| Ludlul bel nemeqi, Tablet V: thanksgiving at Esagil | 120 | 120 | 72 | 7 | 4 |

Total: 459 of the 534 lines in the eBL edition (86%); 459 of the 532 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L II.2, Righteous Sufferer (Ludlul bel nemeqi) (ed. A. Hätinen), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): K.10503 (+ K.22794), BM.38790 (+ BM.39238), K.3972 (+ K.9973, DT.151)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Ludlul bel nemeqi, Tablet I: the anger of Marduk and the loss of favour: 38: only on SU-1951.10, IM.67628, BM.73592, BM.68444, IM.132669; 85: only on VAT.11100, SU-1951.10, IM.67628, BM.73592, IM.132669, VAT.10756; 92: only on VAT.11100, SU-1951.10, IM.67628, BM.73592, IM.132669, BM.61433
- Ludlul bel nemeqi, Tablet III: the dreams of deliverance: 2-4: only on VAT.9954; 64: no manuscript preserves it; 65: only on Si.55; 76-78: only on Si.55, BM.68435; 79-83: only on Si.55
- Ludlul bel nemeqi, Tablet IV: restoration: a+1-a+2: only on Si.728; a+4-a+6: only on Si.728; a+8-a+12: only on Si.728; a+22: no manuscript preserves it
- Ludlul bel nemeqi, Tablet V: thanksgiving at Esagil: 24: only on BM.77253; 54: only on VAT.9303, VAT.9442, BM.74201, Ashm-1924.1795; 55: only on VAT.9303, VAT.9442, BM.74201; 56: only on VAT.9303, VAT.9442; 57-60: only on VAT.9303, VAT.9442, BM.74201; 61-63: only on VAT.9442; 64: only on VAT.9303, VAT.9442; 65-67: only on VAT.9303; 68-69: only on VAT.9303, VAT.10538; 70: only on VAT.9303; 71-80: only on VAT.9303, VAT.10538, SU-1952.212; 81-82: only on VAT.9303, VAT.10538, BM.77253, SU-1952.212; 83-86: only on VAT.9303, VAT.10538, BM.77253; 87-90: only on VAT.10538, BM.77253; 91-100: only on VAT.unn.1, BM.77253

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. K.3291 is a Nineveh extract tablet with passages from several tablets of the poem; it is used where it is the best photographed witness. Lines only on tablets in Berlin, Baghdad, Ankara, Birmingham or Oxford are omitted.
