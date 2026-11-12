# qumran-1qs: The Community Rule (1QS), columns I-XI (complete)

Built by `scripts/import_qumran_1qs.py` (re-runnable; `--force` re-stitches and re-crops the images). It imports the Text-Fabric reader and Hebrew rendering from `scripts/import_qumran_1qphab.py`.

## Contents

One entry, `verified-qumran-1qs-community-rule`, 11 sections (one per scroll column):

| Section | Lines | Subject | Image | Brownlee pp. |
|---|---|---|---|---|
| I | 1-26 | admission to the covenant; the covenant ceremony begins | 1qs-col-01.jpg | 6, 8 |
| II | 1-26 | blessings and curses; yearly order of entry | 1qs-col-02.jpg | 8, 10, 11 |
| III | 1-26 | the one who refuses to enter; the Two Spirits begins | 1qs-col-03.jpg | 11, 12, 14 |
| IV | 1-26 | the ways of the two spirits and their end | 1qs-col-04.jpg | 14, 16, 18 |
| V | 1-26 | rule of the men of the Community; oath; separation | 1qs-col-05.jpg | 18, 20, 22 |
| VI | 1-27 | common life; sessions of the Many; admission; penal code begins | 1qs-col-06.jpg | 22-28 |
| VII | 1-25 | penal code | 1qs-col-07.jpg | 28, 30 |
| VIII | 1-27 | council of the Community; the way in the wilderness | 1qs-col-08.jpg | 30-34 |
| IX | 1-26 | until the Prophet and the anointed ones; the wise man | 1qs-col-09.jpg | 34-38 |
| X | 1-26 | times of prayer; closing hymn | 1qs-col-10.jpg | 38-42 |
| XI | 1-22 | closing hymn | 1qs-col-11.jpg | 42-46 |

## Sources

- **Photographs**: the Israel Museum's photograph of the whole scroll, Digital Dead Sea Scrolls site (http://dss.collections.imj.org.il/community). Viewer configuration `/viewer/data/community.json` (cached in `data/sources/qumran-1qs/imj/`); tiles `tiles.imj.org.il/tiles/community/{zoom}_{x}_{y}.jpg`, zoom 7 = 65 x 9 tiles of 250 px = 16022 x 2250 px, fetched with a plain, honestly identified HTTP client (no access control; nothing bypassed) and stitched (`imj/community_z7.jpg`, data only). Terms as stated: "Website, text, and photos (c) The Israel Museum, Jerusalem, 2011. All rights reserved ... with the exception of single copies for research or private study." Used with credit under COLLECTION_SPEC rule 9.
- **Hebrew**: ETCBC `dss` Text-Fabric dataset tf/2.0, same pinned commit as `import_1qisaa.py` (Abegg, Bowley, Cook; CC BY-NC 4.0); features copied into `data/sources/qumran-1qs/etcbc/`. Extra rendering for 1QS: the editors' deletion `{ x }` and correction `(< y >)` are shown as `{x} <y>` (HTML-escaped); scribal cancellations `{{ }}` and supralinear additions `⟨ ⟩` as in 1QpHab.
- **English**: W. H. Brownlee, *The Dead Sea Manual of Discipline: Translation and Notes* (BASOR Supplementary Studies 10-12), New Haven: American Schools of Oriental Research, 1951; Internet Archive item `american-schools-of-oriental-research-bulletin_1951_10-12` (open, not a lending copy). The translation (pp. 6-46, above the notes) was transcribed by hand from the page images into `data/sources/qumran-1qs/brownlee1951_translation.txt` (conventions in the file header) and proofread against the images; then compared word by word with the item's OCR (`brownlee1951_djvu.txt`): all differences were OCR misreadings or words the OCR dropped. Footnote numbers, Brownlee's supplied section headings and running heads are omitted; his italics (doublets written twice by the scribe) are kept as `<em>`, his struck-through words (scribal cancellations, VII 20, VIII 10, X 24) as `<del>`.
- **Copyright of the English (renewal check)**: published in the US (New Haven) in 1951, so renewal was due in 1978-1979.
  - Online Books Page, record for *BASOR Supplementary Studies* (https://onlinebooks.library.upenn.edu/webbin/cinfo/asorbulsup, checked 2026-11-12): "First renewed issue: no issue renewals found in CCE or CPRS"; "First renewed contribution in: no contribution renewals found in CCE or CPRS".
  - NYPL transcriptions of the Copyright Office renewal records (https://github.com/NYPL/cce-renewals, files 1976-1 through 1991-from-db; 17,919 renewals of 1951 works): no renewal by W. H. Brownlee, none titled *Manual of Discipline*, none claimed by the American Schools of Oriental Research. (The only Brownlee entries are other people: William Brownlee Owens, O. H. Brownlee, etc.)
  - The Stanford Copyright Renewal Database was not usable from this machine (it serves a JavaScript bot check; not bypassed).
  - Conclusion: public domain in the US.

## Mapping method

- **Columns**: the viewer's own column table put some cut lines through the edges of columns (e.g. column II), so the crops are cut at the blank strips between columns, found by an ink profile of the stitched image (dark pixels per x, rows 150-2150, minimum within 300 px of each viewer boundary) and checked by eye: x = 1515, 3143, 4548, 5944, 7413, 8996, 10726, 12450, 13691, 14774; 80 px margin each side. Each crop was read on screen: first and last lines, line count, short lines, blank spaces, supralinear additions, the four dots for the divine name (VIII 14), the blank sheet below XI 22. Recorded per section in `scan_note`.
- **Line numbers**: Brownlee marks every line division of the scroll with "|" (column ends with "||") and prints the line numbers in his margin. The transcription carries markers `{n}` at the start of each scroll line (after his "|", or where he printed none, before the English that renders the line's first Hebrew word), checked against the ETCBC Hebrew line by line. The importer asserts that the English of every column carries exactly the numbers 1..n of the Hebrew, in order. Remarks: III 3, 13, 16 and XI 21 have no "|" in Brownlee; at VIII 10 the long supralinear addition is translated after the line (his margin 10a, 9½, 10b) and stays under line 10.

## Gaps

- The Community Rule as preserved in 1QS is complete. The scroll once began with at least one more column (lost); the top lines of column I and the lowest lines of most columns are damaged.
- The Rule of the Congregation (1QSa) and the Rule of Blessings (1QSb), once sewn to the same scroll, are separate manuscripts (not in the IMJ photograph, not translated by Brownlee) and are not included.

## Open questions

- Brownlee (1951) worked before the Cave 4 copies were published; his bracketed restorations differ in places from the ETCBC restorations. This is stated in the entry's notes.

## Other Dead Sea Scrolls in scope (checked 2026-11-12)

| Scroll | English | Photographs | Result |
|---|---|---|---|
| 1QM War Scroll | No PD or open English found. Burrows 1955 renewed (RE175736) and 1958 renewed (RE288878); Gaster 1956 renewed (RE200228); Yadin's English (Oxford 1962, Israeli author) is a restored foreign work. Vanonen, *War Traditions from the Qumran Caves* (Brill 2022, open access) is a study, not a translation, and its PDF hosts (OAPEN, Brill) serve bot checks to this machine. | IMJ site has the scroll (`/war`) | Skipped (no usable English) |
| 1QHa Thanksgiving Hymns | Mansoor 1961 (Leiden: Brill / Grand Rapids: Eerdmans): no US renewal found in the NYPL records, but country of first publication is unclear and only lending copies exist on archive.org, so it cannot be transcribed; Holm-Nielsen 1960 (Denmark) restored foreign work; Burrows/Gaster renewed | Not on the IMJ DSS site | Skipped |
| 1QapGen Genesis Apocryphon | Avigad and Yadin 1956 (Jerusalem: Magnes Press; Israeli authors, d. 1992 and 1984): a foreign work restored under the URAA, so not PD in the US. Fitzmyer 1966 (Rome) falls under the automatic renewal of 1964-1977 works. | Small Commons image only | Skipped |
| 11QT Temple Scroll | Yadin 1977/1983 and later, in copyright; no open translation found | IMJ site has it (`/temple`) | Skipped |
| 3Q15 Copper Scroll | J. M. Allegro, *The Treasure of the Copper Scroll* (Doubleday, 1960) was renewed: RE375959, 1988-02-03, claimant John Marco Allegro (NYPL CCE 1988 file). In copyright. | Jordan Museum; no column photographs found | Skipped |
