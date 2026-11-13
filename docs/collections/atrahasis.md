# Atrahasis (cuneiform tablets) (key `atrahasis`)

Built by `scripts/import_atrahasis.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (4 entries, 15 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Atrahasis, Old Babylonian Tablet I: the rebellion of the gods and the creation of humankind | 321 | 295 | 31 | 2 | 1 |
| Atrahasis, Standard Babylonian Tablet I | 123 | 123 | 43 | 4 | 4 |
| Atrahasis, Standard Babylonian Tablet II | 116 | 116 | 62 | 6 | 5 |
| Atrahasis, Standard Babylonian Tablet III | 60 | 56 | 54 | 3 | 1 |

Total: 190 of the 620 lines in the eBL edition (31%); 190 of the 590 lines that survive on any manuscript. (Before the QC fix round: 185 lines in 14 sections.)

## Sources

- Original: eBL corpus edition L I.1, Story of the Flood (Atrahasis) (ed. E. Jiménez and G. Rozzi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)
  - Photograph of the Penn Museum (University of Pennsylvania Museum of Archaeology and Anthropology) as served by eBL; terms not stated beyond eBL: 'The images cannot be reproduced without the explicit consent of the funding projects and institutions, as well as the institutions in which the cuneiform tablets are kept.' Used with credit under the library's photo rule (non-commercial).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Atrahasis, Old Babylonian Tablet I: the rebellion of the gods and the creation of humankind: 1-26: no photograph in eBL: BM.78941; 37-102: no photograph in eBL: BM.78941; 125-143: no photograph in eBL: BM.78941, BM.92608; 144-146: no photograph in eBL: BM.78941, BM.92608, BM.78257; 147-148 to 153: no photograph in eBL: BM.78941, BM.78257; 154-170: no photograph in eBL: BM.78941; 171-173: no manuscript preserves it; 174-179: no photograph in eBL: BM.78257; 180-181: no photograph in eBL: BM.92608, BM.78257; 182: no photograph in eBL: BM.92608; 183-185: no photograph in eBL: BM.78257; 186-190: no photograph in eBL: BM.92608, BM.78257; 191: no photograph in eBL: BM.78257, BM.22714.B; 192: no photograph in eBL: BM.92608, BM.78257, BM.22714.B; 193-195: no photograph in eBL: BM.92608, BM.22714.B; 196-201: no photograph in eBL: BM.92608; 202-204: no photograph in eBL: BM.92608, BM.22714.B; 205-211: no photograph in eBL: BM.78941, BM.92608, BM.22714.B; 212 to 215-216: no photograph in eBL: BM.78941, BM.92608; 217 to 233-234: no photograph in eBL: BM.78941; 235-246: no photograph in eBL: BM.78941, BM.78257; 247: no photograph in eBL: BM.78941; 248-270: no manuscript preserves it; 271-280: no photograph in eBL: BM.92608; 281-300: no photograph in eBL: BM.78941, BM.92608; 301-333: no photograph in eBL: BM.78941
- Atrahasis, Standard Babylonian Tablet I: 1-40: not in the eBL Fragmentarium (no photograph there): IM.124646; 48-58: not in the eBL Fragmentarium (no photograph there): IM.124646; 76: not in the eBL Fragmentarium (no photograph there): IM.124646; 81-97: not in the eBL Fragmentarium (no photograph there): IM.124646; 112-120: not in the eBL Fragmentarium (no photograph there): IM.124646; parallel text: IM.124649
- Atrahasis, Standard Babylonian Tablet II: 1-29: not in the eBL Fragmentarium (no photograph there): IM.124649; 44-47: not in the eBL Fragmentarium (no photograph there): IM.124649; 75-84: not in the eBL Fragmentarium (no photograph there): IM.124649; 92-101: not in the eBL Fragmentarium (no photograph there): IM.124649; 116: no photograph in eBL: Ist-B.116 (Istanbul Archaeological Museum); not in the eBL Fragmentarium (no photograph there): IM.124649
- Atrahasis, Standard Babylonian Tablet III: 1: no photograph in eBL: Ist-B.116 (Istanbul Archaeological Museum); not in the eBL Fragmentarium (no photograph there): IM.124649; 2: no photograph in eBL: Ist-B.116 (Istanbul Archaeological Museum); 66-68: no manuscript preserves it; 132: no manuscript preserves it

## QC fix round (2026-11-12)

- Lines shown 185 -> 190; sections 14 -> 15.
- sb-tablet-i 75, 77-80: newly shown on UM.55-21-29.
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- Old Babylonian Tablet I: the Ipiq-Aya tablets (BM.78941, BM.92608, BM.78257, BM.22714.B) are in the British Museum but eBL holds no photograph of them (eBL and CDLI have only hand copies). The British Museum's own collection website refuses automated access (HTTP 403), and spec rule 8 forbids getting around that, so no photograph could be obtained in this round; 290 lines of OB Tablet I remain unshown for that reason (open item).
- eBL has not yet edited OB Tablets II-III or SB Tablets IV-X (chapters without lines), so the Flood episode of the Old Babylonian version is not included. The Middle Babylonian fragments (Montserrat; National Museum of World Writing Systems, Incheon; Ugarit) are not in the chapters built here.
- QC round 2: the UM.55-21-29 note now says where the lines are: the upper-left block of the lower central view (the reverse in eBL's layout).
- SB I 75-80 now come from the Nippur school tablet UM.55-21-29 (Penn Museum photograph served by eBL, used under spec rule 9 because no British Museum photograph carries these lines).
