# Cuthaean Legend of Naram-Sin (cuneiform tablets) (key `cuthaean-legend`)

Built by `scripts/import_cuthaean-legend.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 12 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Cuthaean Legend of Naram-Sin (Standard Babylonian version) | 180 | 180 | 175 | 12 | 5 |

Total: 175 of the 180 lines in the eBL edition (97%); 175 of the 180 lines that survive on any manuscript. (Before the QC fix round: 175 lines in 13 sections.)

## Sources

- Original: eBL corpus edition L I.12, Cuthaean Legend of Naram-Sin (ed. T. D. N. Mitto), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Cuthaean Legend of Naram-Sin (Standard Babylonian version): 20-21: no photograph in eBL: SU-1951.67.A (Museum of Anatolian Civilizations, Ankara); 169-171: no photograph in eBL: SU-1951.67.A (Museum of Anatolian Civilizations, Ankara)

## QC fix round (2026-11-12)

- Lines shown 175 -> 175; sections 13 -> 12.
- standard-babylonian 1-2: now on 1881,0204.219 (was K.1351).
- standard-babylonian 175-176: now on 1881,0204.219 (was K.21047).
- standard-babylonian 177-180: now on 1881,0204.219 (was 1881,0727.271).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- K.1351 is not a manuscript of the Legend: eBL types it 'Quotation' (a court text, SAA 3 29, that quotes the incipit). It is no longer used; lines 1-2 now come from the library copy 1881,0204.219.
- BM.36765 is left out: its reverse shows about 6 lines with no column ruling where eBL attributes two columns (5 and 8 lines). SU-1951.67.A (Sultantepe, Ankara) has no photograph in eBL. The Old Babylonian and Middle Babylonian versions are not included (no photographs in eBL).
- The '| ($___$)' marks in eBL's transliteration (a line that runs on to the next line of the tablet, indented) are now written out as '(line break) (blank space)' and explained in the key.
