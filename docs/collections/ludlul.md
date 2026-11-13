# Ludlul bel nemeqi (cuneiform tablets) (key `ludlul`)

Built by `scripts/import_ludlul.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (5 entries, 39 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Ludlul bel nemeqi, Tablet I: the anger of Marduk and the loss of favour | 120 | 120 | 117 | 13 | 8 |
| Ludlul bel nemeqi, Tablet II: illness and despair | 120 | 120 | 120 | 6 | 4 |
| Ludlul bel nemeqi, Tablet III: the dreams of deliverance | 121 | 120 | 105 | 12 | 8 |
| Ludlul bel nemeqi, Tablet IV: restoration | 53 | 52 | 38 | 4 | 4 |
| Ludlul bel nemeqi, Tablet V: thanksgiving at Esagil | 120 | 120 | 71 | 4 | 2 |

Total: 451 of the 534 lines in the eBL edition (84%); 451 of the 532 lines that survive on any manuscript. (Before the QC fix round: 459 lines in 68 sections.)

## Sources

- Original: eBL corpus edition L II.2, Righteous Sufferer (Ludlul bel nemeqi) (ed. A. Hätinen), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)
  - Photograph by A. A. Fadhil and N. Jabbar (Iraq Museum - eBL Project), displayed by eBL by permission of the State Board of Antiquities and Heritage and The Iraq Museum; eBL: 'The images cannot be reproduced without the explicit consent of the funding projects and institutions, as well as the institutions in which the cuneiform tablets are kept.' Used with credit under the library's photo rule (non-commercial).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Ludlul bel nemeqi, Tablet I: the anger of Marduk and the loss of favour: 85: no photograph in eBL: VAT.11100 (Vorderasiatisches Museum, Berlin), SU-1951.10 (Şanlıurfa Museum), BM.73592, VAT.10756 (Vorderasiatisches Museum, Berlin); not in the eBL Fragmentarium (no photograph there): IM.132669; its photograph shows only part of this face, and the lines cannot be located on it: IM.67628; 86: no photograph in eBL: VAT.11100 (Vorderasiatisches Museum, Berlin), SU-1951.10 (Şanlıurfa Museum), BM.73592; not in the eBL Fragmentarium (no photograph there): IM.132669; commentary: K.3291; quotation in another text: BM.41286; 92: no photograph in eBL: VAT.11100 (Vorderasiatisches Museum, Berlin), SU-1951.10 (Şanlıurfa Museum), BM.73592, BM.61433; not in the eBL Fragmentarium (no photograph there): IM.132669; its photograph shows only part of this face, and the lines cannot be located on it: IM.67628
- Ludlul bel nemeqi, Tablet III: the dreams of deliverance: 2-4: no photograph in eBL: VAT.9954 (Vorderasiatisches Museum, Berlin); 64: no manuscript preserves it; 65: no photograph in eBL: Si.55 (Istanbul Archaeological Museum); 76-78: no photograph in eBL: Si.55 (Istanbul Archaeological Museum), BM.68435; 79-83: no photograph in eBL: Si.55 (Istanbul Archaeological Museum); a+1-b+1: commentary: K.3291
- Ludlul bel nemeqi, Tablet IV: restoration: a+1-a+2: no photograph in eBL: Si.728 (Istanbul Archaeological Museum); a+3: no photograph in eBL: Si.728 (Istanbul Archaeological Museum); commentary: K.3291; a+4-a+6: no photograph in eBL: Si.728 (Istanbul Archaeological Museum); a+7: no photograph in eBL: Si.728 (Istanbul Archaeological Museum); commentary: K.3291; a+8-a+12: no photograph in eBL: Si.728 (Istanbul Archaeological Museum); a+22: no manuscript preserves it; a+30-b+1: commentary: K.3291
- Ludlul bel nemeqi, Tablet V: thanksgiving at Esagil: 23: no photograph in eBL: BM.77253; commentary: K.3291; 24: no photograph in eBL: BM.77253; 54: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.9442 (Vorderasiatisches Museum, Berlin), BM.74201, Ashm-1924.1795 (Ashmolean Museum); 55: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.9442 (Vorderasiatisches Museum, Berlin), BM.74201; 56: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.9442 (Vorderasiatisches Museum, Berlin); 57-60: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.9442 (Vorderasiatisches Museum, Berlin), BM.74201; 61-63: no photograph in eBL: VAT.9442 (Vorderasiatisches Museum, Berlin); 64: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.9442 (Vorderasiatisches Museum, Berlin); 65-67: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin); 68-69: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.10538 (Vorderasiatisches Museum, Berlin); 70: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin); 71-80: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.10538 (Vorderasiatisches Museum, Berlin), SU-1952.212 (Museum of Anatolian Civilizations, Ankara); 81-82: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.10538 (Vorderasiatisches Museum, Berlin), BM.77253, SU-1952.212 (Museum of Anatolian Civilizations, Ankara); 83-86: no photograph in eBL: VAT.9303 (Vorderasiatisches Museum, Berlin), VAT.10538 (Vorderasiatisches Museum, Berlin), BM.77253; 87-90: no photograph in eBL: VAT.10538 (Vorderasiatisches Museum, Berlin), BM.77253; 91-100: no photograph in eBL: VAT.unn.1 (Vorderasiatisches Museum, Berlin), BM.77253

## QC fix round (2026-11-12)

- Lines shown 459 -> 451; sections 68 -> 39.
- tablet-i 47-48, 87: now on K.10503 (was K.3291).
- tablet-i 49-50: now on K.10503 (was K.9237).
- tablet-i 71: now on K.9237 (was K.3291).
- tablet-i 93: now on 1880,0617.2642 (was K.3291).
- tablet-i 105-106: now on BM.36320 (was K.3291).
- tablet-ii 43: now on K.2518 (was K.3291).
- tablet-ii 44, 69-70, 90: now on K.8396 (was K.3291).
- tablet-ii 96-98: now on K.6935 (was K.3291).
- tablet-ii 99: now on K.6935 (was K.2518).
- tablet-ii 100-101, 107: now on K.3972 (was K.3291).
- tablet-iii 1: now on K.2518 (was K.3291).
- tablet-iii 35: now on BM.54821 (was K.3291).
- tablet-iii 84-85: now on 2024,6004.283 (was K.3291).
- tablet-iii 86-87: now on 2024,6004.283 (was BM.54821).
- tablet-iii 95: now on BM.55481 (was BM.54821).
- tablet-iii 96-97, 106: now on BM.55481 (was K.3291).
- tablet-iii 107: now on BM.55481 (was BM.45732).
- tablet-iii 118: now on BM.48732 (was K.3291).
- tablet-iv 1: now on BM.48732 (was K.3291).
- tablet-iv a+20: now on BM.46282 (was K.3291).
- tablet-iv c+16: now on K.9724 (was K.3291).
- tablet-v 14-17: now on BM.34650 (was K.3291).
- tablet-v 18-22: now on BM.34650 (was BM.38002).
- tablet-i 38: newly shown on IM.67628.
- tablet-i 86: no longer shown (was on K.3291, a commentary or quotation; now listed as a gap).
- tablet-iii a+1-b+1: no longer shown (was on K.3291, a commentary or quotation; now listed as a gap).
- tablet-iv a+3, a+7, a+30-b+1: no longer shown (was on K.3291, a commentary or quotation; now listed as a gap).
- tablet-v 23: no longer shown (was on K.3291, a commentary or quotation; now listed as a gap).
- tablet-i 39-40, 42-46, 88-91 on K.10503: linked photographs corrected (joined pieces).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- K.3291 is a commentary (eBL type 'Commentary'): it quotes words of lines from all five tablets, each followed by an explanation. It was wrongly described here as an extract tablet and used for 21 sections; it is no longer used (QC 2026-11-12). Quotations (BM.41286 and others) are not used either. Catch-lines on library copies (III 1 on K.2518, IV 1 on BM.48732) are used.
- Line I 38 now comes from the obverse of IM.67628 (Kalhu; Iraq Museum photograph served by eBL, used under spec rule 9 because no British Museum photograph carries it); III 84-87 from 2024,6004.283 (British Museum). QC round 2: eBL numbers 68 obverse and 53 reverse lines on IM.67628, but its photograph shows only about 44 and 38 of them, so its reverse lines cannot be located; I 85 and 92 (reverse) are therefore gaps again.
- Lines only on tablets in Berlin, Ankara, Birmingham or Oxford, or Iraq Museum tablets without an eBL photograph, are omitted.
