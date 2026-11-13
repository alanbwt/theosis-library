# Adapa (cuneiform tablets) (key `adapa`)

Built by `scripts/import_adapa.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 5 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Adapa (Standard Babylonian fragments) | 97 | 97 | 73 | 5 | 4 |

Total: 73 of the 97 lines in the eBL edition (75%); 73 of the 97 lines that survive on any manuscript. (Before the QC fix round: 73 lines in 5 sections.)

## Sources

- Original: eBL corpus edition L I.7, Adapa, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Adapa (Standard Babylonian fragments): a+1-a+14: no photograph in eBL: MLC.1296 (Morgan Library); a+17: no photograph in eBL: MLC.1296 (Morgan Library); d+1-d+9: no photograph in eBL: MLC.1296 (Morgan Library)

## QC fix round (2026-11-12)

- Lines shown 73 -> 73; sections 5 -> 5.
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- The Middle Babylonian Amarna tablet (VAT.348, Berlin) and the Morgan Library fragment (MLC.1296) have no photograph in eBL, so the Middle Babylonian chapter is not included and lines only on MLC.1296 are omitted.
- e+16-e+17: eBL gives one English sentence for both lines (stored under e+16), with internal markers '(e+16)' and '(e+15)' that are one lower than the Akkadian lines they translate. The English is now shown once for both lines with the markers corrected to (e+17) and (e+16), and the scan_note explains it. No other entry of the 13 collections has English whose line markers disagree with the Akkadian (checked by script; the numbers in brackets in Enuma Elish VI-VII are Marduk's fifty names, not line numbers). Atrahasis OB I 214/215-216, where eBL swaps the English of two lines with correct markers, is handled the same way but is not on a photographed tablet.
