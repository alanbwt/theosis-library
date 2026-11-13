# Counsels of Wisdom (cuneiform tablets) (key `counsels-of-wisdom`)

Built by `scripts/import_counsels-of-wisdom.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 18 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Counsels of Wisdom (Babylonian moral advice) | 159 | 159 | 159 | 18 | 14 |

Total: 159 of the 159 lines in the eBL edition (100%); 159 of the 159 lines that survive on any manuscript. (Before the QC fix round: 157 lines in 17 sections.)

## Sources

- Original: eBL corpus edition L II.3, Counsels of Wisdom (ed. Z. J. Földi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)
  - Photograph of the Penn Museum (University of Pennsylvania Museum of Archaeology and Anthropology) as served by eBL; terms not stated beyond eBL: 'The images cannot be reproduced without the explicit consent of the funding projects and institutions, as well as the institutions in which the cuneiform tablets are kept.' Used with credit under the library's photo rule (non-commercial).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- none: every line of the eBL edition is shown.

## QC fix round (2026-11-12)

- Lines shown 157 -> 159; sections 17 -> 18.
- counsels 19: now on K.8282 (was BM.51070).
- counsels 27-32: now on K.8282 (was K.3364).
- counsels A+1-A+2: newly shown on CBS.6059.
- counsels 20-26 on K.8282: linked photographs corrected (joined pieces).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- A+1-A+2 were omitted as 'not openly licensed'; they now come from the Nippur school tablet CBS.6059 (Penn Museum photograph served by eBL, used under spec rule 9). VAT.17157 (Berlin) has no photograph in eBL.
- BM.51070 and BM.41682 keep the British Museum's own catalogue labels in scan_manuscript ('HAR.ra = Hubullu VIIA', 'Astronomical?'); eBL identifies the Counsels of Wisdom on them, and those labels describe other text on the same school tablets or are out of date.
- K.8282 shows only about six of the 13 lines of column iv that eBL attributes to it; the rest is on the joined piece K.18284 (photographed separately). QC round 2: K.18284 is now linked only to column iv lines, so it no longer appears beside column i (19-32, now all on K.8282); no column iv line of K.8282 is currently chosen.
