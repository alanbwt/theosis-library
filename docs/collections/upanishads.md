# Principal Upanishads (`upanishads`)

Importer: `scripts/import_upanishads.py` (re-runnable; `--tif-dir DIR` may be given more than once to reuse downloaded OPenn TIFFs;
scans that already exist are not remade unless `--force`).
Shelf: India. Era: Axial Age. Tradition: hindu. Language code: `sa`.

## Contents (23 entries, 184 sections)

| Order | Entry | Sections | Manuscript pages |
|---|---|---|---|
| 1 | Isa Upanishad (18 verses, Kanva recension) | 2 | Item 869 fol. 1v-2r |
| 2-7 | Katha Upanishad, vallis I.1-I.3, II.1-II.3 (119 verses) | 15 | Item 869 fol. 3v-8v |
| 8-13 | Prasna Upanishad, questions 1-6 (67 paragraphs) | 11 | Item 869 fol. 8v-12v |
| 14 | Mandukya Upanishad (12 paragraphs) | 2 | Item 869 fol. 16r-16v |
| 15 | Aitareya Upanishad (33 verses, Samkara's division) | 12 | Item 1216 fol. 1v-7r |
| 16-20 | Chandogya Upanishad, prapathakas 1-5 | 19+18+17+18+16 | Item 945 fol. 1v-47v |
| 21 | Chandogya Upanishad, prapathaka 6 ("tat tvam asi") | 26 | Item 1213 fol. 1v-7v |
| 22-23 | Chandogya Upanishad, prapathakas 7-8 | 15+11 | Item 945 fol. 56r-74v |

The Isa, Katha, Prasna, Mandukya, Aitareya and Chandogya are complete, apart from the gaps listed below.

## Sources

- **Images.** University of Pennsylvania Libraries, Kislak Center, via OPenn (Public Domain Mark 1.0). Each OPenn photograph shows
  an opening (verso above, recto below); the importer crops each leaf from the master TIFF.
  - Ms. Coll. 390 Item 869, "Six early upanisads", 16 leaves, 13 x 27 cm, undated (catalogued 18th/19th c.).
  - Ms. Coll. 390 Item 1216, Aitareyopanisad, 7 leaves, 10 x 24 cm, undated.
  - Ms. Coll. 390 Item 945, Chandogyopanisad complete, 74 leaves, 11 x 17 cm, blue machine-made paper, undated.
  - Ms. Coll. 390 Item 1213, Chandogya prapathaka 6, 7 leaves, dated saka 1758 (1836 CE).
  Files: `site/assets/scans/upanishads/penn{869,1216,945,1213}-fNN[rv].jpg` (179 files, about 121 MB).
- **Sanskrit.** GRETIL TEI files (CC BY-NC-SA 4.0), cached in `data/sources/upanishads/gretil/`: Isa (Kanva, mula of the file with
  Samkara's commentary; Sansknet input checked against Limaye and Vadekar 1958), Katha (Vienna student team after Olivelle 1998),
  Prasna, Aitareya and Chandogya (mula of the files with Samkara's commentary; Sansknet input), Mandukya (input by Jeff Samuels).
- **English.** F. Max Müller, The Upanishads, SBE 1 (1879: Isa, Aitareya, Chandogya) and SBE 15 (1884: Katha, Prasna); R. E. Hume,
  The Thirteen Principal Upanishads (1921) for the Mandukya. All public domain. Isa, Katha, Prasna and Chandogya come from the
  proofread English Wikisource transcription (`english/ws_*.json`). The Aitareya (SBE 1 pp. 237-246) and the Mandukya (Hume
  pp. 391-393) are not transcribed elsewhere and were transcribed from the page images for this collection
  (`english/muller1879_aitareya.json`, `english/hume1921_mandukya.json`).

## Mapping method

None of the manuscripts numbers verses or paragraphs. Every page used was read on the image.
- Items 869, 1213, 1216: every verse was located by its words; chapter ends by the scribe's colophons and khanda numbers.
  Line-by-line readings: `data/sources/upanishads/mapping_notes_869.txt`, `mapping_notes_1213.txt`, `mapping_notes_1216.txt`.
- Item 945 (131 pages): the first and last words of every page were read on the image (`mapping_945.json`, transliterated) and
  located in the GRETIL text by string matching; the page boundaries follow from them. A few pages matched less closely because
  of variant wording, a page break inside a word, or words the copyist skipped; each of these was reviewed against the edition text
  and, where text is missing, on the image.
- A section holds the verses or paragraphs that end on one page, listed with every page they occupy.
- The OPenn catalogue's folio ranges for Item 869 are off (Katha ends and Prasna begins on fol. 8v, the Mundaka ends on 15v and the
  Mandukya fills 16r-16v); the marginal running titles and colophons confirm the ranges used.
- The Wikisource English was compared word by word with the archive.org OCR of the printed SBE volumes, and disagreements were
  checked on the page images. Nine transcription slips and one stray heading were corrected to the printed page (listed in each entry's notes).

## Gaps and known issues

- **Kena and Mundaka not published.** Both are in Item 869 (Kena fol. 2r-3v, Mundaka fol. 12v-15v) and are fully mapped in
  `mapping_notes_869.txt`. No usable openly licensed Sanskrit text was found. GRETIL has none. The TITUS texts (Gippert, after
  Albino and Limaye-Vadekar) state "no parts of this document may be republished without prior permission". The Sanskrit Library
  lists CC BY-NC-SA 3.0 XML editions of both, but the texts cannot be downloaded from its public site. The Sanskrit Wikisource texts
  have many misprints (Mundaka: tāpaḥ for tapaḥ, jāyāte for jāyate, praṇo for prāṇo, śraddha for śraddhā and others).
- **Taittiriya, Svetasvatara, Brihadaranyaka not built.** Müller's SBE 15 English for these exists online only as uncorrected OCR,
  so it has to be transcribed from the page images first, as was done for the Aitareya (Taittiriya about 25 printed pages,
  Svetasvatara about 30, Brihadaranyaka about 150). The Sanskrit is on GRETIL (Taittiriya with Samkarabhasya, Svetasvatara, Kanva
  Brihadaranyaka). Candidate Penn manuscripts: Taittiriya 868, 876, 923, 955, 1102; Svetasvatara 723, 848, 1101, 1203;
  Brihadaranyaka 722, 847, 994-999, 1099, 1104, 1223, 1238.
- **Prasna 2.9:** GRETIL prints Samkara's paraphrase in place of the verse, so its Sanskrit is shown as [...]; the verse is on
  Item 869 fol. 10r lines 7-8.
- **Chandogya 5.1.8-14:** the copyist of Item 945 skipped from the middle of 5.1.7 to 5.1.15 (fol. 38v line 8). These seven paragraphs
  are not on any page and are not shown.
- **Chandogya 3.18.5-6:** Item 945 passes from the end of fol. 28v (3.18.5) to the close of 3.18.6 (fol. 29r line 1). The edition text
  is shown in full and the scan notes say which words are missing from the pages. Smaller omissions are noted where they occur
  (3.17.7 repetition, 5.17.2).
- **Chandogya, Müller's paragraph division:** in 15 khandas Müller divides the text into a different number of paragraphs than the
  Sanskrit edition (for example 1.3, 2.13, 3.11, 4.17, 8.2). Each such khanda stands whole in one section with his numbers, which makes
  some sections cover several pages (up to six for 8.4-8.7).
- **Aitareya:** Item 1216 has "apakrāmantu garbhiṇyaḥ" before 2.1 and "yathāsthānaṃ garbhiṇyaḥ" before 3.1, and the closing prayer
  "vāṅ me manasi" after 3.4. GRETIL lacks all three. Müller translates the first two, so his sentences are kept in the English; the
  prayer (his seventh adhyaya) is not shown.
- **Manuscript readings differ from the editions** in places (noted per section where noticeable). The Sanskrit shown is the edition
  text, not a transcription of the manuscript.
- **Dates:** Items 869, 945 and 1216 are undated; Item 1213 is dated 1836. Item 945 also carries prapathaka 6 (fol. 48r-55v), which
  is not used because the dated Item 1213 was mapped first.

## Open questions

- Prasna 6.8 in Müller ends "Tat sat. Harih, Om!", which is not in the GRETIL Sanskrit; kept as printed.
- Chandogya 1.2.1 in Müller reads "Whent he Devas" (a misprint in the 1879 book, marked [sic] on Wikisource); kept as printed.
