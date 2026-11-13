# Great Hymn to Shamash (cuneiform tablets) (key `great-hymn-to-shamash`)

Built by `scripts/import_great-hymn-to-shamash.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (1 entry, 19 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Great Hymn to Shamash (Babylonian hymn to the sun god) | 200 | 200 | 200 | 19 | 11 |

Total: 200 of the 200 lines in the eBL edition (100%); 200 of the 200 lines that survive on any manuscript. (Before the QC fix round: 200 lines in 18 sections.)

## Sources

- Original: eBL corpus edition L III.4, Great Prayer to Shamash (ed. G. Rozzi), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- none: every line of the eBL edition is shown.

## QC fix round (2026-11-12)

- Lines shown 200 -> 200; sections 18 -> 19.
- hymn 7: now on BM.98732 (was BM.36296).
- hymn 8: now on BM.98732 (was K.3182).
- hymn 71-73: now on K.3182 (was BM.33514).
- hymn 74-75: now on K.3182 (was BM.35077).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- All 200 lines of the eBL edition are shown. The school tablet BM.33514 (+ three separately photographed pieces) is no longer needed for 71-73 (the library copy K.3182 carries them); lines 7-8 now come from the library copy BM.98732 instead of the school tablet BM.36296.
- Lines 1-6 and 76-77 remain on school tablets (BM.36296, BM.35077) because no photographed library copy preserves them as well; the sections say so.
