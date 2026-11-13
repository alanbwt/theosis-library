# Anzu (cuneiform tablets) (key `anzu`)

Built by `scripts/import_anzu.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (3 entries, 29 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Anzu, Standard Babylonian Tablet I: the theft of the Tablet of Destinies | 201 | 186 | 183 | 12 | 4 |
| Anzu, Standard Babylonian Tablet II: Ninurta goes to war | 154 | 151 | 72 | 10 | 5 |
| Anzu, Standard Babylonian Tablet III: the defeat of Anzu | 155 | 154 | 97 | 7 | 4 |

Total: 352 of the 510 lines in the eBL edition (69%); 352 of the 491 lines that survive on any manuscript. (Before the QC fix round: 271 lines in 22 sections.)

## Sources

- Original: eBL corpus edition L I.10, Anzu, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)
  - CC0 1.0 (IIIF manifest 'rights'; Yale Peabody Museum open access, http://hdl.handle.net/10079/8931zqj)
  - Photograph of the Hatay Archaeology Museum, Antakya, as served by eBL; eBL: 'The images cannot be reproduced without the explicit consent of the funding projects and institutions, as well as the institutions in which the cuneiform tablets are kept.' Used with credit under the library's photo rule (non-commercial).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Anzu, Standard Babylonian Tablet I: the theft of the Tablet of Destinies: b+110-b+124: no manuscript preserves it; b+181-b+182: its photographs do not show which lines these are: YBC.9842; c+190: its photographs do not show which lines these are: YBC.9842
- Anzu, Standard Babylonian Tablet II: Ninurta goes to war: 2-22: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), IM.95180 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): A.144; 23-25: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara); not in the eBL Fragmentarium (no photograph there): A.144; 26: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), SU-1952.218 (Museum of Anatolian Civilizations, Ankara); not in the eBL Fragmentarium (no photograph there): A.144; 44-45: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), SU-1952.232 (Museum of Anatolian Civilizations, Ankara); not in the eBL Fragmentarium (no photograph there): A.144; 56-58: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), SU-1952.232 (Museum of Anatolian Civilizations, Ankara), IM.95180 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): A.144; 59: no photograph in eBL: K.18740, SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), SU-1952.232 (Museum of Anatolian Civilizations, Ankara), IM.95180 (Iraq Museum); 60-64: no photograph in eBL: K.18740, SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), SU-1952.232 (Museum of Anatolian Civilizations, Ankara), IM.95180 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): A.144; 83-89: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), SU-1952.232 (Museum of Anatolian Civilizations, Ankara); not in the eBL Fragmentarium (no photograph there): A.144; 90: no manuscript preserves it; 92: no manuscript preserves it; 96-99: not in the eBL Fragmentarium (no photograph there): A.144; 100: no manuscript preserves it; 101-102: not in the eBL Fragmentarium (no photograph there): A.144; 103-122: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara); not in the eBL Fragmentarium (no photograph there): A.144; 132: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara); not in the eBL Fragmentarium (no photograph there): A.144; 146-147: no photograph in eBL: IM.95180 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): A.144; 148-152: no photograph in eBL: SU-1951.102.A (Museum of Anatolian Civilizations, Ankara), IM.95180 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): A.144; 153-154: no photograph in eBL: IM.95180 (Iraq Museum)
- Anzu, Standard Babylonian Tablet III: the defeat of Anzu: 1-5: no photograph in eBL: IM.95180 (Iraq Museum); 22-40: no photograph in eBL: IM.95180 (Iraq Museum); b+103: no photograph in eBL: IM.95180 (Iraq Museum); b+118-b+131: no photograph in eBL: IM.95180 (Iraq Museum); b+150-b+167: no photograph in eBL: IM.95180 (Iraq Museum); b+168: no manuscript preserves it

## QC fix round (2026-11-12)

- Lines shown 271 -> 352; sections 22 -> 29.
- sb-tablet-i 12-15: now on YBC.9842 (was K.7257).
- sb-tablet-i 16-21, b+150-b+161: now on YBC.9842 (was K.3454).
- sb-tablet-i c+196-c+197: now on YBC.9842 (was BM.38797).
- sb-tablet-i 22-b+57, b+167-b+180, b+183-b+189, c+191-c+195, c+198-c+201: newly shown on YBC.9842.
- sb-tablet-ii 1: newly shown on YBC.9842.
- sb-tablet-iii b+104-b+117: newly shown on Ant.11000.
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- YBC 9842 (Yale Peabody Museum YPM BC 023841, three fragments A, B, C of a Late Babylonian tablet from Nippur) was listed as a gap because eBL holds no photograph of it. The Yale Peabody Museum publishes CC0 photographs of it (IIIF manifest https://manifests.collections.yale.edu/ypm/nat/1840405); the six overview shots carry label cards (Y9842a/b/c). Which fragment face carries which of eBL's lines follows from the Yale catalogue's line counts per face, which match eBL's numbering blocks; the mapping and the visual checks are recorded in `import_anzu.py`. The three left-edge lines are not used (the edge photographs do not show which lines they are).
- BM.38797 is a quotation (eBL type 'Quotation'); I c+196-c+197 are no longer shown on it.
- III b+104-b+117 now come from Ant.11000 (Hatay Archaeology Museum photograph served by eBL, used under spec rule 9).
- The Old Babylonian tablets from Susa (Louvre) and the Sultantepe tablets (Ankara) have no photograph in eBL.
