# Erra and Ishum (cuneiform tablets) (key `erra-and-ishum`)

Built by `scripts/import_erra-and-ishum.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 14 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Erra and Ishum, Tablet I: Erra roused to war | 191 | 191 | 143 | 14 | 9 |

Total: 143 of the 191 lines in the eBL edition (75%); 143 of the 191 lines that survive on any manuscript. (Before the QC fix round: 134 lines in 11 sections.)

## Sources

- Original: eBL corpus edition L I.5, Erra and Ishum, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)
  - Photograph of the Vorderasiatisches Museum, Staatliche Museen zu Berlin, as served by eBL; eBL: 'The images cannot be reproduced without the explicit consent of the funding projects and institutions, as well as the institutions in which the cuneiform tablets are kept.' Used with credit under the library's photo rule (non-commercial).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Erra and Ishum, Tablet I: Erra roused to war: 20-27: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 28-29: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), IM.95180 (Iraq Museum), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); quotation in another text: IM.74442; 30: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), IM.95180 (Iraq Museum), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 31-33: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 86-91: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 117-120: no photograph in eBL: SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 166-176: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), IM.95180 (Iraq Museum), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 177-180: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), SU-1951.122 (Museum of Anatolian Civilizations, Ankara); 183-191: no photograph in eBL: VAT.9162 (Vorderasiatisches Museum, Berlin), SU-1951.122 (Museum of Anatolian Civilizations, Ankara)

## QC fix round (2026-11-12)

- Lines shown 134 -> 143; sections 11 -> 14.
- tablet-i 136: now on BM.36974 (was K.16694).
- tablet-i 121-129: newly shown on VAT.10174.
- tablet-i 34-58, 92-94, 102-116, 181-182 on K.8571: linked photographs corrected (joined pieces).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- eBL has edited only Tablet I so far (Tablets II-V have no lines in eBL), so Tablets II-V are not included.
- K.8571 + K.19050: eBL's notes and its own transliteration of K.19050 put line-ends of lines 95-101 on K.19050, a small piece with about six lines. The former section 92-116 linked K.19050 for all 25 lines; it is now cut into 92-94 and 102-116 (K.8571 only) and 95-101 (K.8571 + K.19050), and K.19050 is no longer linked to sections 34-58 and 181-182.
- Lines 121-129 now come from the Assur school tablet VAT.10174 (Berlin photograph served by eBL, used under spec rule 9 because no British Museum photograph carries these lines).
