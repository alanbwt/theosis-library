# qumran-1qphab: Pesher Habakkuk (1QpHab), columns I-XIII (complete)

Built by `scripts/import_qumran_1qphab.py` (re-runnable; `--force` re-downloads and re-crops the images).

## Contents

Two entries, 13 sections (one per scroll column):

| Entry | Section | Scroll lines | Habakkuk | Image(s) |
|---|---|---|---|---|
| `verified-qumran-1qphab-columns-1-5` | I | 1-17 | 1:1-5 | 1qphab-cols-1-3.jpg |
| | II | 1-17 | 1:5-6 | 1qphab-cols-1-3.jpg |
| | III | 1-17 | 1:6-9 | 1qphab-cols-1-3.jpg (right half of the lines) + 1qphab-col-03-left.jpg (left half) |
| | IV | 1-17 | 1:10-11 | 1qphab-col-04.jpg |
| | V | 1-16 | 1:12-16 | 1qphab-col-05.jpg |
| `verified-qumran-1qphab-columns-6-13` | VI | 1-16 | 1:16-2:2 | 1qphab-col-06.jpg |
| | VII | 1-17 | 2:2-4 | 1qphab-col-07.jpg |
| | VIII | 1-17 | 2:5-8 | 1qphab-col-08.jpg |
| | IX | 1-17 | 2:8-11 | 1qphab-col-09.jpg |
| | X | 1-17 | 2:10-14 | 1qphab-col-10.jpg |
| | XI | 1-17 | 2:15-17 | 1qphab-col-11.jpg |
| | XII | 1-17 | 2:17-19 | 1qphab-col-12.jpg |
| | XIII | 1-4 | 2:20 | 1qphab-col-13.jpg |

(Line counts are the transcription's, which includes wholly restored lines at the foot of some columns.)

## Sources

- **Photographs, columns I-V** (unchanged from the first build): Israel Museum, Jerusalem, inv. 95.57/28, via Wikimedia Commons, both tagged `{{PD-Art}}`: `File:Habakkuk_Pesher.png` (760 x 633; columns I, II and the right half of III) and the Google Art Project file (3001 x 1663; photo David Harris; left half of III, IV, V), cropped at the blank strips between columns.
- **Photographs, columns VI-XIII** (added 2026-11-12): the Israel Museum's own photograph of the whole scroll, Digital Dead Sea Scrolls site (http://dss.collections.imj.org.il/habakkuk). The viewer configuration (`/viewer/data/habakkuk.json`, cached in `data/sources/qumran-1qphab/imj/`) serves it as 290 px tiles from `tiles.imj.org.il/tiles/habakuk/{zoom}_{x}_{y}.jpg`. Zoom 7 (65 x 7 tiles, 18576 x 1977 px) was fetched with a plain HTTP client identifying itself as TheosisLibrary (no bot check or access control on the tile server; nothing bypassed) and stitched (`imj/habakuk_z7.jpg`, data only). One crop per column, full height, at the column positions in the viewer's own column table (ids 1-13 = columns I-XIII; id 14 is the blank last sheet), scaled from its 5650 px overview. Terms as stated by the museum: "Website, text, and photos (c) The Israel Museum, Jerusalem, 2011. All rights reserved ... with the exception of single copies for research or private study." Used with credit under COLLECTION_SPEC rule 9 (owner's instruction of 2026-11-12); recorded in `scan_license`.
- **Hebrew**: ETCBC `dss` Text-Fabric dataset, tf/2.0, commit `f051578775b77b36164cfa16c402563d7d211a55` (Abegg, Bowley, Cook transcriptions; CC BY-NC 4.0). Features cached in `data/sources/qumran-1qphab/etcbc/`. Rendering as in `import_1qisaa.py`. `load_words()` now takes the scroll name and cache directory as parameters (used by `import_qumran_1qs.py`); output for 1QpHab is unchanged.
- **English**: W. H. Brownlee, "The Jerusalem Habakkuk Scroll", BASOR 112 (Dec. 1948), pp. 8-18, Internet Archive item `sim_bulletin-of-the-american-schools-of-oriental-research_1948-12_112`. Columns 1-5: `brownlee1948_cols1-5.txt` (first build). Columns 6-13 (pp. 12-16): `brownlee1948_cols6-13.txt`, transcribed by hand from the page images (`basor112_pages/leaf11-15.jpg`) and proofread line by line against them; then compared word by word with the issue's OCR: every difference was an OCR misreading (e.g. "abundaut", "inseri", "rebel" for "rebelled") or a word the OCR dropped that is on the page ("I keep my station", "are to be marvellous", checked again on the image).
- **Copyright of the English**: published in the US in 1948; no renewal (Online Books Page serial record for BASOR: no issue or contribution renewals in CCE or CPRS; NYPL CCE renewal transcriptions 1975-1991 hold none by Brownlee). Public domain in the US.

## Mapping method

- **Columns**: the ETCBC transcription gives every word its column and line. Each column crop was read on screen and its first and last legible words, line count and distinctive features (short lines, blank spaces, words written above the line, the divine name in Old Hebrew letters) matched to the transcription; recorded per section in `scan_note`.
- **English line numbers**: Brownlee prints, in his margin, the number of each scroll line beside the printed line on which it begins, and marks the exact line division in the running English with "/". Shown at the start of the printed line, the margin numbers sit up to a line early, which is why the first build's columns I-II looked off by one or two. For columns I-II and VI-XIII the transcription now carries markers `{n}` at the exact start of scroll line n (after Brownlee's "/"; where he printed none, before the English word rendering the first Hebrew word of the line), each checked against the Hebrew line by line, and the importer asserts that every marker is in order and within the column's lines. Places without a "/" are listed in `NO_SLASH` and in the section notes (I 13, II 12, VII 7 and 9, X 16, XII 11; in XIII the "/" after "all the earth!" is not a line division). Columns III-V still show Brownlee's printed margin numbers, as in the first build (the brief was to keep I-V otherwise unchanged).
- Columns I-V are otherwise unchanged: same images, same Hebrew, same English words (the only text change is the line numbers in I-II; the first line of column I is now set in italics as a quotation of Habakkuk, as Brownlee printed it).

## Gaps

- None in coverage: all 13 columns of the scroll are built. Columns I and II, and the lower lines of columns I-XII, are damaged on the scroll itself; Brownlee shows lacunae as rows of dots (one ellipsis here).

## Open questions

- The photograph of columns I-III (Commons, 760 px) is small. The Israel Museum photograph now used for VI-XIII also covers I-V at 1977 px height (crops at the same viewer positions would work); the images for I-V were left as they were because the brief said to keep I-V unchanged. Swapping them is a one-line change to `IMAGES`/`COLUMNS` if wanted.
- Columns III-V could be given the same exact line markers as I-II and VI-XIII for consistency.

## Other Dead Sea Scrolls (checked 2026-11-12)

See `docs/collections/qumran-1qs.md` for the Community Rule (now built) and the status of 1QM, 1QHa, 1QapGen, 11QT and 3Q15.
