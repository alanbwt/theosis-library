# Babylonian Theodicy (cuneiform tablets) (key `theodicy`)

Built by `scripts/import_theodicy.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 18 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| The Babylonian Theodicy (dialogue of the sufferer and his friend) | 288 | 284 | 258 | 18 | 10 |

Total: 258 of the 288 lines in the eBL edition (90%); 258 of the 284 lines that survive on any manuscript. (Before the QC fix round: 258 lines in 18 sections.)

## Sources

- Original: eBL corpus edition L II.1, Theodicy, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- The Babylonian Theodicy (dialogue of the sufferer and his friend): 89: no manuscript preserves it; 109-110-111-119: no manuscript preserves it; 157: no manuscript preserves it; 158-171: photograph does not show these lines (visual check): K.5932; 172: photograph does not show these lines (visual check): K.5932; quotation in another text: K.4267; 173-174: photograph does not show these lines (visual check): K.5932; 192: no photograph in eBL: VAT.10567 (Vorderasiatisches Museum, Berlin); commentary: BM.66882; 290-293: no photograph in eBL: BM.34773, BM.34633; 294-297: no photograph in eBL: BM.34773, BM.34633; commentary: BM.66882

## QC fix round (2026-11-12)

- Lines shown 258 -> 258; sections 18 -> 18.
- dialogue 125: now on K.9290 (was BM.40098).
- dialogue 175: newly shown on K.17235.
- dialogue 172: no longer shown (was on K.4267, a commentary or quotation; now listed as a gap).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- K.4267 is a letter to the king (eBL type 'Quotation') that quotes line 172; it is no longer used, so line 172 is a gap. K.5932 is left out: its photograph shows one face with about 11 lines while eBL attributes 45 lines on both faces to the join, and two pieces of the join (K.8491, K.13929) have no photograph.
- Each line of the Theodicy is written in four parts set out in columns; eBL's '&' column divider is shown as '|' and explained in the key. Twenty-three lines of the poem have no English in eBL; where they appear, they are marked as such.
