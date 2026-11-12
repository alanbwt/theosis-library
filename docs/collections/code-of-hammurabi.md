# Code of Hammurabi (Louvre Sb 8)

Collection key: `code-of-hammurabi` · importer: `scripts/import_code_of_hammurabi.py` · shelf: Mesopotamia

## Contents (7 entries, 257 sections)

| order | entry | sections | stele |
|---|---|---|---|
| 1 | `verified-code-of-hammurabi-prologue` | 5 (one per column) | obv. i 1 - v 25 |
| 2 | `verified-code-of-hammurabi-laws-1-65` | 65 (one per law) | obv. v 26 - xvi 76 (+ restored xvii 1) |
| 3 | `verified-code-of-hammurabi-laws-100-149` | 50 | rev. i - ix |
| 4 | `verified-code-of-hammurabi-laws-150-199` | 50 | rev. ix - xvii |
| 5 | `verified-code-of-hammurabi-laws-200-249` | 49 (242-243 is one law) | rev. xvii - xxi |
| 6 | `verified-code-of-hammurabi-laws-250-282` | 33 | rev. xxi - xxiii |
| 7 | `verified-code-of-hammurabi-epilogue` | 5 (one per column) | rev. xxiv - xxviii |

Everything that is on the stele is published: prologue, laws 1-65 and 100-282, epilogue.

## Sources

- **Akkadian**: CDLI P249253 ATF (https://cdli.earth/inscriptions/2346002/atf). CDLI terms allow re-use with credit.
  ATF letters are rendered in Unicode form (š ṣ ṭ ḫ, subscript indices, Sumerograms in capitals); breaks `[ ]`,
  damage `#`, corrections `!` and editorial `< >` are kept as in the source.
- **English**: R. F. Harper, *The Code of Hammurabi* (Chicago 1904), public domain. Base text from Wikisource,
  corrected against the printed book in 73 places (listed in `CORRECTIONS` in the importer). Method: the Wikisource
  text was aligned word by word with four independent readings of the printed pages (three archive.org OCR texts and a
  Tesseract OCR of the Toronto scan's page images, kept in `data/sources/code-of-hammurabi/harper_pages/`). Every place
  where two or more readings agreed against Wikisource was checked; the final text was re-aligned and the only
  remaining differences are OCR noise and line-end hyphens (wine-shop, one-half, ham-string, Sinmu-ballit). Several
  Wikisource errors were substantive (law 166 had the ending of law 165; law 248 an extra phrase; law 223 'builder' for
  'physician'; a clause missing from the prologue). Punctuation follows Wikisource (spot-checked on page images).
- **Photographs**:
  - obverse colour crops `obv-colNN.jpg`: Wikimedia Commons, Francesco Bini/Sailko "SB 8, 03" (CC BY-SA 4.0) for
    columns i-x, Rama "IMG 7764" (CC BY-SA 3.0 FR) for xi-xvi;
  - column strips `obv-colNN-montage.jpg`, `rev-colNN-montage.jpg`: the photographic montage of the whole inscription
    that CDLI distributes with P249253 (https://cdli.earth/dl/photo/P249253_d.jpg, credited to M. Richardson,
    *A Comprehensive Grammar to Hammurabi's Stele*; CDLI: "Photo (detail) © Louvre Museum"; non-commercial use).
  60 files, about 37 MB.

## Mapping method

1. Law -> column/line: CDLI ATF (`@column`, `@law`). Reverse column i lines 1-7 (no `@law` marker) are the end of law 100.
2. Obverse column -> colour photograph: the stele's columns are horizontal bands, read right to left, starting under
   the relief. I counted the ruled band boundaries by eye on the photographs (strips rendered with a pixel grid):
   16 bands, then the polished erasure. Checks: the horizontal crack lies at the x/xi boundary (CDLI damage in
   obv. x 24-58 and xi 12-66), and L. Zhiltsova's plan of the stele (NABU 2023/3 no. 62, pp. 122-123; copy in
   `data/sources/code-of-hammurabi/NABU-2023-3.pdf`) shows the same 16 bands, crack and line counts per column
   (66, 70, 72, 70, 68, ... identical to CDLI). Each crop holds one band in its middle with margins, because the ruling
   lines tilt across the curved face.
3. Column -> montage strip: the montage prints column labels i-xvi (front) and i-xxviii (rear) over the strips; label
   centres were located in the image and each crop is centred on its label, with the label row kept. Labels were
   checked against the damage in the CDLI ATF: front crack between x and xi; rear flake in xxii-xxiii (ATF rev. 22
   29-54, 23 22-46), crack and flake in xx-xxi (rev. 20 59-67, 21 52-96), flake at the start of v-vi (rev. 5 5-10,
   6 11-19). All 44 crops were inspected on contact sheets.
4. Prologue and epilogue English are cut at Harper's own printed markers "(Col. II)" ... "(Col. V)" and
   "(Col. 41.)" ... "(Col. 44.)" (Harper numbers reverse columns continuously: rev. xxv = col. 41), which are kept in the text.

## Gaps and limits

- Laws 66-99 and the opening of law 100 stood on the seven erased obverse columns; they survive only on later
  clay-tablet copies and are not published here. CDLI restores the last word of law 65 in the erased column xvii;
  it is shown in brackets and the section note says it is not on any photograph.
- Montage crops are 518-700 px wide at 2600 px height (spec maximum long side), so signs are small; the obverse
  colour crops are the better view for the front.
- Harper splits laws 133 and 176 into A/B parts (133A, 176A); CDLI keeps one number, so each section carries both
  parts of Harper's English, labelled.
- Harper's English follows his 1904 understanding (e.g. "devotee", "NER.SE.GA", "bennu fever"); it is reproduced as printed.

## Open questions

- The CDLI montage's photographic source is credited to Richardson's grammar and "© Louvre Museum"; it is used under
  CDLI's non-commercial terms, like the Vatican images in the Josephus collection. If the integrator prefers only
  openly licensed images, the reverse sections would need another column-labelled photographic source.
