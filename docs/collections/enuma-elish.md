# Enuma Elish (cuneiform tablets) (key `enuma-elish`)

Built 2026-11-12 by `scripts/import_enuma-elish.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (7 entries, 130 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Enuma Elish, Tablet I: the birth of the gods and Tiamat's army | 162 | 162 | 162 | 22 | 13 |
| Enuma Elish, Tablet II: the gods seek a champion | 162 | 162 | 133 | 13 | 9 |
| Enuma Elish, Tablet III: the assembly of the gods | 138 | 138 | 138 | 8 | 4 |
| Enuma Elish, Tablet IV: Marduk defeats Tiamat | 146 | 146 | 141 | 15 | 11 |
| Enuma Elish, Tablet V: the ordering of the universe | 158 | 158 | 140 | 15 | 9 |
| Enuma Elish, Tablet VI: the creation of humankind and of Babylon | 166 | 166 | 125 | 18 | 13 |
| Enuma Elish, Tablet VII: the fifty names of Marduk | 166 | 166 | 160 | 39 | 16 |

Total: 999 of the 1098 lines in the eBL edition (91%); 999 of the 1098 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.2, Poem of Creation (Enuma elish) (ed. A. C. Heinrich, rev. Z. J. Földi and E. Jiménez), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Excluded after checking:

- BM.48270: visual check: photograph shows obverse, reverse and edges, ink 48270 on the right edge. The obverse has about eight to ten worn lines, enough for eBL's five, but the reverse surface is almost entirely worn away with only one small patch of two or three signs visible, so eBL's 21 reverse lines cannot be confirmed from this photograph.
- K.5661: visual check: photograph shows obverse, reverse and edges, ink K.5661 on the left edge and K.11641 on the top edge (a joined piece). The obverse has several patches of text, perhaps 15 to 20 lines in all, but the reverse surface is largely lost, with only three small patches of signs (about six to eight lines' worth), so eBL's 14 reverse lines, and possibly all 22 obverse lines, cannot be confirmed from this photograph.

Joins whose pieces were photographed separately (all photographs linked; the lines are on one of them): K.4832 (+ K.23609), BM.32206 (+ F.220), K.5923 (+ K.8512, K.18305), Sm.11 (+ K.4406, K.11169, 1882,0323.151), Rm.366 (+ K.2053, BM.134499), BM.34384 (+ BM.35506, BM.36146)

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Enuma Elish, Tablet II: the gods seek a champion: 71-74: only on VAT.14037, IM.unn.7; 75-76: only on IM.unn.7; 77-78: only on VAT.14037, IM.unn.7; 79: only on IM.unn.7; 88-91: only on VAT.14037, IM.unn.7; 110-115: only on VAT.14037, IM.unn.7, BM.48270; 116-117: only on VAT.14037, IM.unn.7, BM.48270, K.19822; 118-119: only on VAT.14037, NMS.1909,405.36, IM.unn.7, BM.48270, K.19822; 120-122: only on VAT.9971, VAT.14037, NMS.1909,405.36, IM.unn.7, BM.48270, K.19822; 123-125: only on VAT.9971, VAT.14037, NMS.1909,405.36, IM.unn.7, BM.48270
- Enuma Elish, Tablet IV: Marduk defeats Tiamat: 25: only on VAT.10552, SU-1951.58, SU-1951.47, BM.93016; 130: only on SU-1951.58, SU-1951.47, SU-1952.243, BM.93016; 133-135: only on SU-1951.58, SU-1951.47, SU-1952.243, BM.93016
- Enuma Elish, Tablet V: the ordering of the universe: 64: only on SU-1951.98, BM.66606; 65-69: only on SU-1951.98; 71-76: only on SU-1951.98; 84: only on SU-1951.98, BM.66606; 85-89: only on SU-1951.98
- Enuma Elish, Tablet VI: the creation of humankind and of Babylon: 8: only on VAT.9676, VAT.11363, IM.121284, BM.92629, Ashm-1924.1828; 9-12: only on VAT.9676, IM.121284, BM.92629, Ashm-1924.1828; 13-20: only on VAT.9676, SU-1951.237, IM.121284, BM.92629, Ashm-1924.1828; 61-64: only on VAT.9676, SU-1952.60, IM.121284, Ashm-1924.1828, unnumbered; 65-67: only on VAT.9676, SU-1952.60, IM.121284, unnumbered; 71-73: only on VAT.9676, SU-1952.60, IM.121284, unnumbered; 111-112: only on VAT.9676, SU-1952.60, IM.121284, Ashm-1924.1828; 113: only on SU-1952.60, IM.121284, Ashm-1924.1828, VAT.9676; 114-116: only on VAT.9676, SU-1952.60, IM.121284, Ashm-1924.1828; 127-129: only on VAT.9676, SU-1952.60, IM.121284, Ashm-1924.1828; 158-165: only on VAT.9676, Ist-A.512, IM.121284, BM.92629, Ashm-1924.1828; 166: only on VAT.9676, Ist-A.512, IM.121284, BM.92629
- Enuma Elish, Tablet VII: the fifty names of Marduk: 50-52: only on Ist-A.154, SU-1951.63; 54: only on Ist-A.154, SU-1951.63; 78: only on Ist-A.154, SU-1951.62; 106: only on Ist-A.154, SU-1951.63, SU-1951.62

## Notes

The 79 eBL photographs proposed by the witness selection were checked on labelled contact sheets and full views (a delegated visual pass, with my own spot checks of K.3473, BM.40559 and K.15650). eBL's photograph filed under K.15650 (a piece joined to K.2854) shows K.16050 and is not used; K.15650 itself is visible in the K.2854 photograph. Many Babylonian copies of Tablets I-VII and the Ashur copies (Berlin, Istanbul) have no open photograph; the gaps listed above survive only on such tablets, or on British Museum tablets that eBL has not photographed (for example BM.92629). BM.48270 and K.5661 were left out because their worn reverses do not show the lines eBL attributes to them. Commentary tablets (Sm.11, Rm.366) that quote lines of Tablet VII are used where they are the best photographed witness.
