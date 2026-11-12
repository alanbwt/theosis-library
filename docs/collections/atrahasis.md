# Atrahasis (cuneiform tablets) (key `atrahasis`)

Built 2026-11-12 by `scripts/import_atrahasis.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (4 entries, 14 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Atrahasis, Old Babylonian Tablet I: the rebellion of the gods and the creation of humankind | 321 | 295 | 31 | 2 | 1 |
| Atrahasis, Standard Babylonian Tablet I | 123 | 123 | 38 | 3 | 3 |
| Atrahasis, Standard Babylonian Tablet II | 116 | 116 | 62 | 6 | 5 |
| Atrahasis, Standard Babylonian Tablet III | 60 | 56 | 54 | 3 | 1 |

Total: 185 of the 620 lines in the eBL edition (30%); 185 of the 590 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.1, Story of the Flood (Atrahasis) (ed. E. Jiménez and G. Rozzi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): K.6235 (+ K.7109), K.4539 (+ K.5902, K.7816, K.17752)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Atrahasis, Old Babylonian Tablet I: the rebellion of the gods and the creation of humankind: 1-26: only on BM.78941; 37-102: only on BM.78941; 125-143: only on BM.78941, BM.92608; 144-146: only on BM.78941, BM.92608, BM.78257; 147-148-153: only on BM.78941, BM.78257; 154-170: only on BM.78941; 171-173: no manuscript preserves it; 174-179: only on BM.78257; 180-181: only on BM.92608, BM.78257; 182: only on BM.92608; 183-185: only on BM.78257; 186-190: only on BM.92608, BM.78257; 191: only on BM.78257, BM.22714.B; 192: only on BM.92608, BM.78257, BM.22714.B; 193-195: only on BM.92608, BM.22714.B; 196-201: only on BM.92608; 202-204: only on BM.92608, BM.22714.B; 205-211: only on BM.78941, BM.92608, BM.22714.B; 212-215-216: only on BM.78941, BM.92608; 217-233-234: only on BM.78941; 235-246: only on BM.78941, BM.78257; 247: only on BM.78941; 248-270: no manuscript preserves it; 271-280: only on BM.92608; 281-300: only on BM.78941, BM.92608; 301-333: only on BM.78941
- Atrahasis, Standard Babylonian Tablet I: 1-40: only on IM.124646; 48-58: only on IM.124646; 75: only on IM.124646, UM.55-21-29; 76: only on IM.124646; 77-80: only on IM.124646, UM.55-21-29; 81-97: only on IM.124646; 112-120: only on IM.124646, IM.124649
- Atrahasis, Standard Babylonian Tablet II: 1-29: only on IM.124649; 44-47: only on IM.124649; 75-84: only on IM.124649; 92-101: only on IM.124649; 116: only on IM.124649, Ist-B.116
- Atrahasis, Standard Babylonian Tablet III: 1: only on Ist-B.116, IM.124649; 2: only on Ist-B.116; 66-68: no manuscript preserves it; 132: no manuscript preserves it

## Notes

The photographs proposed by the witness selection were checked on labelled contact sheets and full-resolution views in a delegated visual pass; every verdict is recorded in CHECKS in the importer and repeated in the section scan_notes. Partial: the great Old Babylonian copy of Tablet I by Ipiq-Aya (BM.78941, BM.92608, BM.78257, BM.22714.B) has no photograph on eBL, so only the 31 lines on BM.17596.A are shown for OB Tablet I. eBL has not yet edited OB Tablets II-III or SB Tablets IV-X (chapters without lines), so the Flood episode of the Old Babylonian version is not included. The Middle Babylonian fragments (Montserrat; National Museum of World Writing Systems, Incheon; Ugarit) have no open photograph.
