# Descent of Ishtar (key `descent-of-ishtar`)

Built by `scripts/import_descent-of-ishtar.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 5 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Descent of Ishtar to the Netherworld (Standard Babylonian version) | 148 | 148 | 138 | 5 | 1 |

Total: 138 of the 148 lines in the eBL edition (93%); 138 of the 148 lines that survive on any manuscript. (Before the QC fix round: 138 lines in 5 sections.)

## Sources

- Original: eBL corpus edition L I.8, Descent of Ishtar (ed. A. Setälä, rev. Z. J. Földi, A. Hätinen, E. Jiménez, G. Rozzi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Descent of Ishtar to the Netherworld (Standard Babylonian version): 11a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 12a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 18a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 23a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 97a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 103a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 118a-118c: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin); 137a: no photograph in eBL: VAT.9729 (Vorderasiatisches Museum, Berlin)

## QC fix round (2026-11-12)

- Lines shown 138 -> 138; sections 5 -> 5.
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- K.162 is published as two crops (obverse, reverse) of the British Museum photograph so the script stays legible; the crop boxes and the reason the upper face is the obverse are recorded in the importer.
- The short Neo-Assyrian version from Ashur (VAT.13833, 11 lines in eBL's NA chapter) is not included, and lines only on VAT.9729 (Ashur) are omitted: eBL holds no photograph of either Berlin tablet.
- The '&' that eBL uses to divide each line into its two half-lines is now shown as '|' and explained in the entry's key.
