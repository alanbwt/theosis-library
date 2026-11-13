# Vendidad, Fargards 1-2 (`vendidad`)

## Contents

| Order | Entry | Section | Pages |
|---|---|---|---|
| 1 | `verified-vendidad-fargard-1`: the sixteen lands, beginning with Airyana Vaejah | Vd 1.1-21 (one section) | fol. 60r-63v (8 pages) |
| 2 | `verified-vendidad-fargard-2`: Yima, the spreading of the earth, and the vara | Vd 2.1-43 (one section) | fol. 63v-71v (17 pages) |

2 entries, 2 sections, 24 page images (fol. 63v is shared).

## Sources

- **Manuscript:** Columbia University, Rare Book & Manuscript Library, MS Or 320 - FOLIO, a Vendidad Sade (the Vendidad in pure Avestan, arranged for recitation with the Yasna and Visperad). It has 322 leaves with 17 lines to the page, and a Persian verse heading before each fargard. The colophon (fol. 320r-320v) says it was completed at Surat by Herbed Darab Framroz Minochehr on day Asman, month Adar, 1131 AY (1762 CE). The manuscript was formerly owned by A. V. Williams Jackson. Images come from OPenn (https://openn.library.upenn.edu/Data/0032/html/ms_or_320.html) under the Creative Commons Public Domain Mark. The scans are the OPenn web JPEGs (1800 px), unaltered except for re-encoding.
- **Avestan:** Geldner's text (Avesta, 1886-1896) in the avesta.org transliteration by Joseph H. Peterson (https://www.avesta.org/vendidad/vd.htm). The edition is public domain; the site states no license. Abbreviated repeats ("...") are kept as given.
- **English:** James Darmesteter, *The Zend-Avesta, Part I: The Vendidad* (Sacred Books of the East 4, 2nd edition, 1895), which is public domain. The text comes from the validated English Wikisource transcription (CC BY-SA 4.0), with footnotes omitted. Five transcription slips were corrected against the printed page images; each correction is listed in the entry's translator notes and in `ERRATA` in the script.

## Mapping method

The Persian verse headings, which are readable, fix the fargard boundaries:

- **fol. 60r:** the verses name the Vendidad and "the first fargard".
- **fol. 63v:** the verses name "the second fargard", which "tells the story of Jamshid".
- **fol. 71v:** the verses name the third fargard.

Fargard 1 therefore runs from below the heading on fol. 60r to line 4 of fol. 63v. Fargard 2 runs from below the heading on fol. 63v to the row of rosettes on fol. 71v. The readings are logged in `data/sources/vendidad/mapping_log.json`.

The opening words of the pages inside each fargard were compared with renderings of Geldner's text in an Avestan font, but the matches could not be confirmed with certainty in this hand. No page start inside a fargard is accepted, and no paragraph is placed on a single page. Each fargard is one section that lists all its pages in order, and the scan note says so.

## Numbering

- **Fargard 1:** Darmesteter's 2nd edition follows Geldner (1, 3-21). Geldner's 1.2 is a set of Avestan quotations from the Pahlavi commentary that appears in Vendidad Sade manuscripts; Darmesteter does not translate it and avesta.org omits it. The avesta.org paragraph numbers 2-20 are renumbered to Geldner's 3-21 so the Avestan and English numbers match.
- **Fargard 2:** the avesta.org numbers agree with Geldner. Darmesteter prints 6-7 as one paragraph numbered 7, prints 20-21 as one paragraph numbered 21, and gives 32 in brackets.

## Gaps and open questions

- The mapping is at fargard level only. A reader of Avestan script could split each fargard by page using the opening words of each page; the importer's structure would then allow one section per page.
- The Vendidad Sade adds liturgical formulas in red at fargard ends, and in Fargard 1 the clause-2 quotations; these are not in the Avestan text shown.
- Era is given as "Axial Age" because the Vendidad is a Young Avestan text of the first millennium BCE; its date is disputed.
- **The Gathas (key `avesta-gathas`) were not built.** The only witness with a documented page-level mapping is Oxford J2 (1323), through the page labels of the TITUS digitisation of Mills's 1893 collotype facsimile, but TITUS forbids republication of its images. In MS Or 320 the chapter openings of the Gathas could not be verified on the images. Bodleian MS. Zend e. 1 (J3) is laminated under tissue and illegible in its images.
- Source caches for the Gathas (avesta.org Avestan text, the sacred-texts transcription of Mills's SBE 31, and OCR lines of the 1887 archive.org scan) are kept in `data/sources/avesta-gathas/` for a later attempt.

## QC fixes (2026-11-12)
Fargard 2: the Avestan gives paragraphs 12-14 as one abbreviated line ('âat ýimâi xshathrâi xshvash-satô-zima hañjaseñti, âat hê îm zå bvat perene ... mashyânãmca'), as in the avesta.org transliteration of Geldner, while Darmesteter's English gives 12, 13 and 14 in full (and 43 likewise: 'dâtare ... ashâum'). The scan_note now says so; the Avestan is not expanded. The stray line breaks the review found in the English (2.14 'southwards<br>,', 2.40 'The one<br>thing missed') were made by the importer when it joined Wikisource pages at a page break inside a sentence; pages are now joined without a break there, which removes seven such breaks (one in Fargard 1, six in Fargard 2) and changes no word. Still open: the collection is not in the local build (a build step, outside this fix). Review: docs/qc/review-near-east.md; fixes: docs/qc/fixes-near-east.md.
