# Anzu (cuneiform tablets) (key `anzu`)

Built 2026-11-12 by `scripts/import_anzu.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (3 entries, 22 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Anzu, Standard Babylonian Tablet I: the theft of the Tablet of Destinies | 201 | 186 | 117 | 8 | 4 |
| Anzu, Standard Babylonian Tablet II: Ninurta goes to war | 154 | 151 | 71 | 9 | 4 |
| Anzu, Standard Babylonian Tablet III: the defeat of Anzu | 155 | 154 | 83 | 5 | 3 |

Total: 271 of the 510 lines in the eBL edition (53%); 271 of the 491 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.10, Anzu, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): K.22880 (+ Sm.1807)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Anzu, Standard Babylonian Tablet I: the theft of the Tablet of Destinies: 22-a+32: only on YBC.9842; a+33: only on YBC.9842, Di.2258; a+34: only on YBC.9842; a+35: only on YBC.9842, Di.2258; a+36: only on YBC.9842; a+37: only on YBC.9842, Di.2258; a+38-a+47: only on YBC.9842, IM.58821; a+48: only on YBC.9842; a+49-a+54: only on YBC.9842, Di.2258; a+55-b+57: only on YBC.9842; b+110-b+124: no manuscript preserves it; b+167-c+195: only on YBC.9842; c+198: only on YBC.9842; c+199-c+201: only on IM.95180, YBC.9842
- Anzu, Standard Babylonian Tablet II: Ninurta goes to war: 1: only on A.144, SU-1951.102.A, IM.95180, YBC.9842; 2-22: only on A.144, SU-1951.102.A, IM.95180; 23-25: only on A.144, SU-1951.102.A; 26: only on A.144, SU-1951.102.A, SU-1952.218; 44-45: only on A.144, SU-1951.102.A, SU-1952.232; 56-58: only on A.144, SU-1951.102.A, SU-1952.232, IM.95180; 59: only on K.18740, SU-1951.102.A, SU-1952.232, IM.95180; 60-64: only on K.18740, A.144, SU-1951.102.A, SU-1952.232, IM.95180; 83-89: only on A.144, SU-1951.102.A, SU-1952.232; 90: no manuscript preserves it; 92: no manuscript preserves it; 96-99: only on A.144; 100: no manuscript preserves it; 101-102: only on A.144; 103-122: only on A.144, SU-1951.102.A; 132: only on A.144, SU-1951.102.A; 146-147: only on A.144, IM.95180; 148-152: only on A.144, SU-1951.102.A, IM.95180; 153-154: only on IM.95180
- Anzu, Standard Babylonian Tablet III: the defeat of Anzu: 1-5: only on IM.95180; 22-40: only on IM.95180; b+103: only on IM.95180; b+104-b+117: only on IM.95180, Ant.11000; b+118-b+131: only on IM.95180; b+150-b+167: only on IM.95180; b+168: no manuscript preserves it

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. The Old Babylonian tablets from Susa (Louvre) and the Sultantepe tablets (Ankara) have no open photograph on eBL; lines found only there are omitted.
