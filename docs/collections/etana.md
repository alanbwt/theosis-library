# Etana (cuneiform tablets) (key `etana`)

Built by `scripts/import_etana.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (3 entries, 17 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Etana, Standard Babylonian Tablet I: the founding of kingship at Kish | 40 | 40 | 40 | 2 | 2 |
| Etana, Standard Babylonian Tablet II: the eagle and the serpent | 152 | 152 | 98 | 7 | 3 |
| Etana, Standard Babylonian Tablet III: the flight to heaven | 131 | 131 | 131 | 8 | 5 |

Total: 269 of the 323 lines in the eBL edition (83%); 269 of the 323 lines that survive on any manuscript. (Before the QC fix round: 269 lines in 17 sections.)

## Sources

- Original: eBL corpus edition L I.9, Etana, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Etana, Standard Babylonian Tablet II: the eagle and the serpent: 1-43: photograph does not show these lines (visual check): K.8572; 120-127: photograph does not show these lines (visual check): K.8572; 148-150: photograph does not show these lines (visual check): K.8572

## QC fix round (2026-11-12)

- Lines shown 269 -> 269; sections 17 -> 17.
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- Old Babylonian (Morgan Library, Louvre) and Middle Assyrian (Berlin, Istanbul) versions are not included: eBL holds no photographs of those tablets. K.8572 is excluded (see the importer), which leaves Tablet II lines 1-43, 120-127 and 148-150 without a witness here.
- Tablet III line 1 is the catch-line written at the end of K.2606's copy of Tablet II; it is shown and the section says so.
