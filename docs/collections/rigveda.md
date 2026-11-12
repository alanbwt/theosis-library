# Rigveda (`rigveda`)

The complete Rigveda, one entry per hymn (sukta): `verified-rigveda-<mandala>-<hymn>`, 1,028 entries,
2,623 sections. Inside each entry, one section per manuscript page: the verses whose last syllable stands on
that page. A verse that begins on the previous page lists both pages.

## Contents

| Book | Hymns | Manuscript pages |
|---|---|---|
| 1 | 1.1-1.191 (191) | Item 41, fol. 1v-149r |
| 2 | 2.1-2.43 (43) | Item 41 |
| 3 | 3.1-3.62 (62) | Item 41; 3.62 (the Gāyatrī, 3.62.10) on Item 35, fol. 33r-34r |
| 4 | 4.1-4.58 (58) | Item 41 |
| 5 | 5.1-5.87 (87) | Item 41 |
| 6 | 6.1-6.75 (75) | Item 41 |
| 7 | 7.1-7.104 (104) | Item 41 |
| 8 | 8.1-8.103 (103, with the Vālakhilya 8.49-8.59) | Item 41 |
| 9 | 9.1-9.114 (114) | Item 41 |
| 10 | 10.1-10.191 (191) | 10.1-10.45 on Item 41; 10.46-10.191 on Item 48, with 10.87.20-25 and 10.88.1-4 (a leaf lost in Item 48) from Item 41, fol. 828v-829r |

Every hymn is complete except for three groups of verses that Griffith did not translate into English: 1.179.3-4 and
10.61.5-8 (rendered in Latin) and 10.86.16-17 (left untranslated). Those verses are not shown; the entry says so.

## Sources

| Layer | Source | License |
|---|---|---|
| Scans | University of Pennsylvania, Kislak Center, Ms. Coll. 390 Items 41, 48, 35 (OPenn web JPEGs; a single leaf is cropped from each opening) | Public Domain Mark 1.0 (Penn) |
| Sanskrit | Aufrecht, Die Hymnen des Rigveda (1877), accented e-text by van Nooten and Holland, rev. Eichler, GRETIL `sa_Rgveda-edAufrecht.xml` | CC BY-NC-SA 4.0 |
| Padapāṭha (edition text, Item 41 sections) | Sansknet padapāṭha, GRETIL `sa_RgvedasaMhitApadapATha.xml` | CC BY-NC-SA 4.0 |
| English | R. T. H. Griffith, The Hymns of the Rigveda (Benares 1889-1892; 2nd ed. 1896-1897), VedaWeb `griffith.csv` | translation public domain; VedaWeb text CC BY-NC-SA 4.0 |
| Titles | VedaWeb `addressees.json` | CC BY 4.0 |

### The manuscripts

- Item 41: padapāṭha (word-by-word recitation text) of the whole Rigveda, 884 leaves in fascicles, Devanāgarī,
  7-9 lines a page, accents in red, undated (the catalogue's "Saṃvat 1205 [?]" for aṣṭaka 5 is doubtful and not
  used). Sections from it show Aufrecht's saṃhitā text and, as edition text, the padapāṭha of the same verses.
  At each adhyāya break the scribe writes an anukramaṇī (list of seers, deities and metres) and an invocation;
  these pages carry no verses and are marked INDEX in the readings. Penn's running foliation is used; it repeats
  two numbers, corrected in `LABEL_FIX` (image 191 upper leaf is 189v, image 233 lower leaf is 232r).
- Item 48: saṃhitā of aṣṭaka 8 (RV 10.46-10.191), 158 leaves, 6 lines a page, colophon Saṃvat 1768 (1711).
  The scribe's leaf 60 is lost; khila verses are inserted after several hymns (noted, not reproduced).
- Item 35: saṃhitā of aṣṭaka 3, colophon Saṃvat 1794 (1737), Vārāṇasī. Only fol. 33r-34v were read, for RV 3.62.

## Mapping method

1. The opening words of line 1 of every page were transcribed from the images (`data/sources/rigveda/readings/`).
   Item 48 and Item 35 were read by me directly. Item 41 was read from first-line strips of every page by
   reading assistants, one group of pages each (`readings/transcriptions/read_*.tsv`, brief in
   `readings/tools/reading_brief.txt`), and merged with hand-checked lines for invocations, anukramaṇī pages,
   colophons, blank pages, deletions and pages the strips missed (`readings/penn41_handchecked.tsv`) into
   `readings/penn41.txt` (`readings/transcriptions/assemble41.txt`).
2. Each reading is located in the edition text (saṃhitā for Items 48/35, padapāṭha for Item 41) by an alignment
   search that runs forward from the previous page. No page position is extrapolated: every page boundary is a
   reading from the image. The build stops if any page inside a run of read pages is missing.
3. The step between successive page starts was checked for every page. Irregular steps were explained on the
   full page image: anukramaṇī pages, khila insertions, a deleted (yellow-painted) repeat on fol. 418r-418v,
   blacked-out lines, refrains the scribes abbreviate, and the lost leaf of Item 48. In Item 41, all 42 places where the
   scribe opens a new adhyāya with an invocation or an anukramaṇī fall exactly at adhyāya starts of the standard
   aṣṭaka division, which confirms the run.
4. Verses whose text is not wholly on contiguous surviving pages are not published.
5. Spot checks: I compared the first line of many pages (all of Item 48, Item 35, and samples across Item 41)
   with the scan notes on the published crops.

## English

Griffith's English comes from VedaWeb, whose transcription has OCR slips. It was compared word by word with an
independent OCR of the printed 2nd edition (archive.org in.ernet.dli.2015.104118, .104119); every disagreement
that could be an error was checked on the printed page image (by me for book 10 and parts of book 1, by
checking assistants for the rest, brief in `readings/tools/flag_brief.txt`), and only confirmed slips were
corrected: 707 corrections in `data/sources/rigveda/griffith_errata.json`, each with its page image. Where the
2nd-edition scan lacks a page, the first edition (archive.org hymnsrigveda00grifgoog, hymnsrigveda02grifgoog)
was used. 40 verses could not be compared with any printed page in these scans
(`griffith_scan/unchecked_verses.json`); their English is the VedaWeb text as published. One VedaWeb row
(10.132.4) repeated the whole of 10.132.5; the repeat was removed.

## Gaps and open questions

- Item 41 is undated. The dated witnesses are Item 48 (1711) and Item 35 (1737).
- The Sanskrit shown is Aufrecht's text, not a transcription of the manuscripts; the scribes' small variants
  (abbreviated refrains, omitted words, spellings) are not recorded verse by verse.
- Khila verses in Item 48 and the anukramaṇī pages of Item 41 are not reproduced.
- Scan footprint: 1,848 JPEG crops, about 410 MB (above the ~1,500-file guide, because the whole Rigveda is
  mapped page by page). The OPenn web-image caches were deleted after the build; the importer refetches them
  if scans are regenerated (`--force-scans`).

## Check

`python3 scripts/check_collection.py rigveda` -> `rigveda: 1028 entries, 2623 sections, 0 hard failures, 0 warnings`
