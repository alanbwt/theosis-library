# Mesha Stele (Moabite Stone), Louvre AO 5066

Collection key: `mesha-stele` · importer: `scripts/import_mesha_stele.py` · shelf: Levant & Israel

## Contents (1 entry, 8 sections)

`verified-mesha-stele-ao5066`, all 34 lines in eight groups: 1-4, 5-9, 10-13, 14-18, 19-21, 22-25, 26-30, 31-34.
Complete as far as the stele is preserved (the last lines are broken; gaps are shown).

## Sources

- **Moabite text**: H. F. B. Compston, *The Inscription on the Stele of Mesa, commonly called the Moabite Stone*
  (SPCK 1919), pp. 11-13, "The Text in Hebrew square script" (public domain). I transcribed it line by line from the
  printed page images (Commons djvu), using the Wikisource transcription as a base; it is saved in
  `data/sources/mesha-stele/compston_hebrew_verified.txt`. Wikisource errors corrected from the print include line 1
  הד (not הר), line 3 ב[מת · י] (Wikisource ב[נס), line 8 מהדבא, line 16 זה, final letter forms as printed.
- **English**: Compston 1919, pp. 14-16, printed line for line with the stele. Wikisource pages 14-15 are validated;
  page 16 was checked against its page image (line 22 corrected to "ʿōp̄el"). Compston's footnotes are kept as notes.
- **Photograph**: Wikimedia Commons "F4171 Louvre stele de Mesha AO5066 rwk.jpg" (Mbzt, 2020, CC BY-SA 4.0), the
  whole inscribed face, 1677 x 2600 px.

## Mapping

One inscribed face, shown whole in the photograph. Sections are consecutive line groups in Compston's numbering,
which follows the stele line for line. No line-group crops were made, so every section points at the same image
(the checker's one-image warning is expected).

## Limits and open points

- Much of the visible text is on the Louvre's plaster restoration, made from the squeeze taken before the stone was
  broken in 1869; every section note says so.
- Compston's Phoenician-letter text (pp. 7-10) is not used. Its Wikisource transcription has errors (line 3 b[ns for
  b[mt, line 16 missing h, line 30 w for n, line 33 r/d) and was not fully re-proofread; a later pass could add it
  as the native-script layer after a letter-by-letter check against pp. 7-10.
- Compston's reading is of 1919. Later editions read some words differently (for example the end of line 1, the name
  of Mesha's father, now read Kemosh-yat); this is not reflected in the text.

## QC fixes (2026-11-12)
The square-script lines were plain left-aligned text in an RTL script. Each line is now a <span class="native-rtl"> (right to left) followed by a <span class="translit"> with a letter-for-letter Latin transliteration of the same line (the scheme of the Siloam and Gezer entries; mechanical, adds no reading). A translator note explains the transliteration and the dividers. Review: docs/qc/review-near-east.md; fixes: docs/qc/fixes-near-east.md.
