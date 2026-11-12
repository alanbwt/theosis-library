# qumran-1qphab: Pesher Habakkuk (1QpHab), columns I-V

Built by `scripts/import_qumran_1qphab.py` (re-runnable; `--force` re-downloads the images).

## Contents

One entry, `verified-qumran-1qphab-columns-1-5`, five sections (one per scroll column):

| Section | Scroll lines | Habakkuk | Image(s) |
|---|---|---|---|
| I | 1-17 | 1:1-5 | 1qphab-cols-1-3.jpg |
| II | 1-17 | 1:5-6 | 1qphab-cols-1-3.jpg |
| III | 1-17 | 1:6-9 | 1qphab-cols-1-3.jpg (right half of the lines) + 1qphab-col-03-left.jpg (left half) |
| IV | 1-17 | 1:10-11 | 1qphab-col-04.jpg |
| V | 1-16 | 1:12-16 | 1qphab-col-05.jpg |

## Sources

- **Photographs**: Israel Museum, Jerusalem, inv. 95.57/28, via Wikimedia Commons, both tagged `{{PD-Art}}`:
  - `File:Habakkuk_Pesher.png` (760 x 633; from the Israel Museum Digital Dead Sea Scrolls project): columns I, II and the right half of III. Kept at its original size.
  - `File:The_Commentary_on_Habakkuk_Scroll_(1QpHab)_Written_in_Hebrew_-_Google_Art_Project.jpg` (3001 x 1663; photo David Harris): left half of III, IV, V. Cropped at the middle of the blank strips between columns (x 1282-1367 and 2398-2470, found by an ink profile and checked by eye).
- **Hebrew**: ETCBC `dss` Text-Fabric dataset, tf/2.0, commit `f051578775b77b36164cfa16c402563d7d211a55` (Abegg, Bowley, Cook transcriptions; CC BY-NC 4.0). Features cached in `data/sources/qumran-1qphab/etcbc/`. Rendering as in `import_1qisaa.py`; the dataset's missing-sign mark (epsilon) shown as an ellipsis; an empty restoration `[ ]` shown as `[…]`. Brackets that open on one line and close on a later line are left as the source has them.
- **English**: W. H. Brownlee, "The Jerusalem Habakkuk Scroll", BASOR 112 (Dec. 1948), pp. 8-18, Internet Archive item `sim_bulletin-of-the-american-schools-of-oriental-research_1948-12_112` (open access). Columns 1-5 transcribed by hand from the page images (leaves 7, 9, 10, 11) into `data/sources/qumran-1qphab/brownlee1948_cols1-5.txt`; the file header documents the conventions (footnote numbers dropped, rows of dots shown as one ellipsis, Brownlee's signs / ( ) ? # * * kept, margin line numbers kept as superscripts, quotations of Habakkuk in italics). The ABBYY OCR of the issue (`basor112_djvu.txt`) is kept for reference only; it was not used for the text.
- **Copyright of the English**: published in the US in 1948; renewal would have been due in 1975-1976. The Online Books Page serial record for BASOR (https://onlinebooks.library.upenn.edu/webbin/cinfo/asorbulletin) reports no issue renewals and no contribution renewals in CCE or CPRS; the NYPL CCE renewal transcriptions (github.com/NYPL/cce-renewals, 1975-1991) contain no renewal by Brownlee. Treated as public domain in the US.

## Mapping method

The ETCBC transcription gives every word its column and line. Each column was located on the photographs by reading the Hebrew and matching first and last legible words of several lines (recorded in each section's `scan_note`). Brownlee's translation is printed column by column with the same 13 extant columns, so the English is assigned by his own "Column n" headings; nothing is aligned by length.

## Gaps

- Columns VI-XIII (Habakkuk 1:16-2:20) are not built. The only complete photographs (Israel Museum Digital Dead Sea Scrolls site, dss.collections.imj.org.il) are "All rights reserved" with reproduction limited to research or private study. Wikimedia Commons has no openly licensed photograph of those columns of the original; `File:Pesher_Habakkuk_Scroll.JPG` (a visitor photograph of columns VI-VII in a display case) could not be confirmed to show the original rather than a facsimile, and the Library of Congress Matson slide of "The Habakkuk Commentary" (matpc.22898) is marked "copyright Y. Yadin" on the slide and appears to show a mounted reproduction. If a reusable photograph of the whole scroll is found, the English for columns 6-13 is on pp. 12-16 of the same BASOR issue.
- Columns I-II and the lower lines of all columns are damaged on the scroll.

## Open questions

- The photograph of columns I-III is small (760 px wide); a larger openly licensed copy would be better.
- Brownlee's line numbers in columns I-II follow his 1948 restoration and differ by a line or two from the ETCBC numbering (noted in each section).

## Other Dead Sea Scrolls in scope that were not built

Checked on 2026-11-12. None could be built to the spec:

| Scroll | English translation | Photographs | Result |
|---|---|---|---|
| 1QS Community Rule | W. H. Brownlee, The Dead Sea Manual of Discipline (BASOR Supplementary Studies 10-12, 1951), public domain (OBP: no renewals for the series; no 1978-79 renewal found); open copy at archive.org item `american-schools-of-oriental-research-bulletin_1951_10-12` | None reusable: Israel Museum images all rights reserved; nothing on Commons; Burrows 1951 plates (ASOR, not renewed) exist only as lending copies on archive.org | Skipped (no image) |
| 1QM War Scroll | No public-domain English found: Burrows 1958 renewed (RE288878), Gaster 1956 renewed (RE200228), Yadin 1962 (Israel/Oxford, restored foreign work), Dupont-Sommer (foreign) | Only single Matson photographs | Skipped |
| 1QHa Thanksgiving Hymns | Mansoor 1961 (Brill, Leiden, and Eerdmans; country of first publication unclear, only lending copies), Holm-Nielsen 1960 (Denmark, restored foreign work); Burrows 1955/1958 and Gaster 1956 renewed | None reusable | Skipped |
| 11QT Temple Scroll (11Q19) | Only Yadin 1977/1983 and later, in copyright | Only one Commons portion | Skipped |
| 1QapGen Genesis Apocryphon | Avigad and Yadin 1956 (Jerusalem, restored foreign work), Fitzmyer 1966 (Rome), later ones in copyright | Only a small Commons image | Skipped |
