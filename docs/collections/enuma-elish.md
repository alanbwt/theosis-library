# Enuma Elish (key `enuma-elish`)

Built by `scripts/import_enuma-elish.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (7 entries, 88 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Enuma Elish, Tablet I: the birth of the gods and Tiamat's army | 162 | 162 | 162 | 17 | 12 |
| Enuma Elish, Tablet II: the gods seek a champion | 162 | 162 | 140 | 12 | 9 |
| Enuma Elish, Tablet III: the assembly of the gods | 138 | 138 | 138 | 7 | 3 |
| Enuma Elish, Tablet IV: Marduk defeats Tiamat | 146 | 146 | 138 | 12 | 9 |
| Enuma Elish, Tablet V: the ordering of the universe | 158 | 158 | 135 | 9 | 5 |
| Enuma Elish, Tablet VI: the creation of humankind and of Babylon | 166 | 166 | 125 | 17 | 12 |
| Enuma Elish, Tablet VII: the fifty names of Marduk | 166 | 166 | 142 | 14 | 11 |

Total: 980 of the 1098 lines in the eBL edition (89%); 980 of the 1098 lines that survive on any manuscript. (Before the QC fix round: 999 lines in 130 sections.)

## Sources

- Original: eBL corpus edition L I.2, Poem of Creation (Enuma elish) (ed. A. C. Heinrich, rev. Z. J. Földi and E. Jiménez), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Enuma Elish, Tablet II: the gods seek a champion: 71-74: no photograph in eBL: VAT.14037 (Vorderasiatisches Museum, Berlin), IM.unn.7 (Iraq Museum); 75-76: no photograph in eBL: IM.unn.7 (Iraq Museum); 77-78: no photograph in eBL: VAT.14037 (Vorderasiatisches Museum, Berlin), IM.unn.7 (Iraq Museum); 79: no photograph in eBL: IM.unn.7 (Iraq Museum); 88-91: no photograph in eBL: VAT.14037 (Vorderasiatisches Museum, Berlin), IM.unn.7 (Iraq Museum); 110-115: no photograph in eBL: VAT.14037 (Vorderasiatisches Museum, Berlin), IM.unn.7 (Iraq Museum); photograph does not show these lines (visual check): BM.48270; 123-125: no photograph in eBL: VAT.9971 (Vorderasiatisches Museum, Berlin), VAT.14037 (Vorderasiatisches Museum, Berlin), IM.unn.7 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): NMS.1909,405.36; photograph does not show these lines (visual check): BM.48270
- Enuma Elish, Tablet IV: Marduk defeats Tiamat: 8: no photograph in eBL: SU-1951.58 (Museum of Anatolian Civilizations, Ankara), SU-1951.23.A (Museum of Anatolian Civilizations, Ankara), BM.93016; quotation in another text: K.1353; 25: no photograph in eBL: VAT.10552 (Vorderasiatisches Museum, Berlin), SU-1951.58 (Museum of Anatolian Civilizations, Ankara), SU-1951.47 (Museum of Anatolian Civilizations, Ankara), BM.93016; 130: no photograph in eBL: SU-1951.58 (Museum of Anatolian Civilizations, Ankara), SU-1951.47 (Museum of Anatolian Civilizations, Ankara), SU-1952.243 (Museum of Anatolian Civilizations, Ankara), BM.93016; 131-132: no photograph in eBL: SU-1951.58 (Museum of Anatolian Civilizations, Ankara), SU-1951.47 (Museum of Anatolian Civilizations, Ankara), SU-1952.243 (Museum of Anatolian Civilizations, Ankara), BM.93016; commentary: K.4657, BM.66606; 133-135: no photograph in eBL: SU-1951.58 (Museum of Anatolian Civilizations, Ankara), SU-1951.47 (Museum of Anatolian Civilizations, Ankara), SU-1952.243 (Museum of Anatolian Civilizations, Ankara), BM.93016
- Enuma Elish, Tablet V: the ordering of the universe: 64: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); commentary: BM.66606; 65-69: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); 70: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); commentary: Rm.395, BM.66606; 71-76: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); 81-82: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); quotation in another text: 79.B.1/30, BM.38706; 83: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); commentary: BM.66606; quotation in another text: BM.32206; 84: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); commentary: BM.66606; 85-89: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara); 90: no photograph in eBL: SU-1951.98 (Museum of Anatolian Civilizations, Ankara), VAT.12915 (Vorderasiatisches Museum, Berlin); commentary: Rm.395
- Enuma Elish, Tablet VI: the creation of humankind and of Babylon: 8: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), VAT.11363 (Vorderasiatisches Museum, Berlin), BM.92629, Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 9-12: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), BM.92629, Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 13-20: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1951.237 (Museum of Anatolian Civilizations, Ankara), BM.92629, Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 61-64: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1952.60 (Şanlıurfa Museum), Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; unnumbered manuscript: unnumbered; 65-67: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1952.60 (Şanlıurfa Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; unnumbered manuscript: unnumbered; 71-73: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1952.60 (Şanlıurfa Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; unnumbered manuscript: unnumbered; 111-112: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1952.60 (Şanlıurfa Museum), Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 113: no photograph in eBL: SU-1952.60 (Şanlıurfa Museum), Ashm-1924.1828 (Ashmolean Museum), VAT.9676 (Vorderasiatisches Museum, Berlin); not in the eBL Fragmentarium (no photograph there): IM.121284; 114-116: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1952.60 (Şanlıurfa Museum), Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 127-129: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), SU-1952.60 (Şanlıurfa Museum), Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 158-165: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), Ist-A.512 (Istanbul Archaeological Museum), BM.92629, Ashm-1924.1828 (Ashmolean Museum); not in the eBL Fragmentarium (no photograph there): IM.121284; 166: no photograph in eBL: VAT.9676 (Vorderasiatisches Museum, Berlin), Ist-A.512 (Istanbul Archaeological Museum), BM.92629; not in the eBL Fragmentarium (no photograph there): IM.121284
- Enuma Elish, Tablet VII: the fifty names of Marduk: 48-49: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara); commentary: Rm.366; 50-52: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara); 53: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara); commentary: Rm.395, K.8585, K.13866; 54: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara); 78: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); 100: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); quotation in another text: K.8519; 101: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); quotation in another text: K.8519, K.7658; 102: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: Sm.11; 103: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: Sm.11; quotation in another text: K.8519, K.7658; 104: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: Sm.11; 105: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); quotation in another text: K.8519, K.7658; 106: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); 107: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: Sm.11; quotation in another text: K.8519, K.7658; 108: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: K.4657, Sm.11, VAT.10616, BM.54228; 109: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: K.4657, Sm.11, VAT.10616; quotation in another text: K.7658; 110: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: K.4657, Sm.11, VAT.10616; 111: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: Sm.11; 112: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara); commentary: Rm.366; 121a: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), SU-1951.62 (Museum of Anatolian Civilizations, Ankara), VAT.14511 (Vorderasiatisches Museum, Berlin); commentary: K.4657, Sm.11, VAT.10616; 121b: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), VAT.14511 (Vorderasiatisches Museum, Berlin); commentary: Sm.11; 122: no photograph in eBL: Ist-A.154 (Istanbul Archaeological Museum), SU-1951.63 (Museum of Anatolian Civilizations, Ankara), VAT.14511 (Vorderasiatisches Museum, Berlin); commentary: Sm.11; quotation in another text: K.7658

## QC fix round (2026-11-12)

- Lines shown 999 -> 980; sections 130 -> 88.
- tablet-i 36: now on BM.45528 (was K.4657).
- tablet-i 76: now on BM.37287 (was K.4657).
- tablet-i 103: now on BM.45571 (was K.4657).
- tablet-i 121-122: now on BM.38024 (was K.4657).
- tablet-ii 1: now on BM.40559 (was K.4657).
- tablet-ii 130: now on BM.38864 (was K.4657).
- tablet-iii 53-55: now on K.3473 (was K.4657).
- tablet-iv 1: now on K.3473 (was BM.33891).
- tablet-iv 17: now on K.16706 (was K.7361).
- tablet-v 17: now on K.3567 (was K.2164).
- tablet-v 127: now on K.3445 (was BM.43969).
- tablet-vi 48-50: now on K.5923 (was BM.33690).
- tablet-vi 151-153: now on K.13865 (was BM.54311).
- tablet-vii 1-4: now on K.2854 (was Sm.11).
- tablet-vii 9-12: now on K.2854 (was Rm.366).
- tablet-vii 17: now on K.8522 (was K.2854).
- tablet-vii 18-21, 126-132: now on K.8522 (was Sm.11).
- tablet-vii 64-66: now on BM.37379 (was Rm.366).
- tablet-vii 67: now on BM.39798 (was Rm.366).
- tablet-vii 77: now on BM.39798 (was BM.38706).
- tablet-vii 82-86, 94-95: now on K.13761 (was Sm.11).
- tablet-vii 91-92: now on K.13761 (was Rm.366).
- tablet-vii 93: now on K.13761 (was K.8519).
- tablet-vii 96-98: now on BM.37981 (was Sm.11).
- tablet-vii 99: now on BM.37981 (was K.8519).
- tablet-vii 113-114: now on K.12830 (was Rm.366).
- tablet-vii 115-118: now on K.12830 (was Sm.11).
- tablet-vii 119-120: now on K.12830 (was K.7658).
- tablet-vii 135-138: now on K.8522 (was Rm.366).
- tablet-ii 116-122: newly shown on K.19822.
- tablet-iv 8: no longer shown (was on K.1353, a commentary or quotation; now listed as a gap).
- tablet-iv 131-132: no longer shown (was on K.4657, a commentary or quotation; now listed as a gap).
- tablet-v 70, 90: no longer shown (was on Rm.395, a commentary or quotation; now listed as a gap).
- tablet-v 81-82: no longer shown (was on BM.38706, a commentary or quotation; now listed as a gap).
- tablet-v 83: no longer shown (was on BM.32206, a commentary or quotation; now listed as a gap).
- tablet-vii 48-49, 112: no longer shown (was on Rm.366, a commentary or quotation; now listed as a gap).
- tablet-vii 53: no longer shown (was on Rm.395, a commentary or quotation; now listed as a gap).
- tablet-vii 100-101: no longer shown (was on K.8519, a commentary or quotation; now listed as a gap).
- tablet-vii 102-104, 109, 111, 121b: no longer shown (was on Sm.11, a commentary or quotation; now listed as a gap).
- tablet-vii 105, 107, 122: no longer shown (was on K.7658, a commentary or quotation; now listed as a gap).
- tablet-vii 108, 110, 121a: no longer shown (was on K.4657, a commentary or quotation; now listed as a gap).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- Commentaries (K.4657, Sm.11 + K.4406 + K.11169 + 1882,0323.151, Rm.366 + K.2053 + BM.134499, Rm.395, VAT.10616, BM.54228 and others) and quotations in other texts (the Triple Column God List K.7658 and K.8519, the Kislimu ritual BM.32206, the treatise BM.38706, the letter K.10908, K.1353, K.7361, K.2164, BM.54311) are no longer used as witnesses (QC 2026-11-12): they carry the line with explanations or inside another text. Lines found only there are listed as gaps. Catch-lines on library copies (IV 1 on K.3473, VI 1 on K.3567) are used.
- eBL's photograph filed under K.15650 (a piece joined to K.2854) shows K.16050 and is not used; K.15650 itself is visible in the K.2854 photograph. BM.48270 and K.5661 are left out because their worn reverses do not show the lines eBL attributes to them.
- QC round 2: VI 1 on K.3567 is the damaged catch-line row on the broken top of the reverse, eBL r 2' (eBL's corpus label r 1' is corrected from its own transcription of K.3567); the two clear lines below it are Ashurbanipal's colophon. VII 42-47 on K.9267: eBL labels the lines 3'-5' and 32'-34', but the photograph shows one block of consecutive lines; the section says so.
- Many Babylonian school tablets are used for Tablets I-VII: under the new rule only where no photographed library copy preserves the line as well; each such section names the tablet as a school tablet.
