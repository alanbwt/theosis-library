# Bhagavad Gita (key `bhagavad-gita`)

The complete Bhagavad Gita, 18 chapters, on one dated Sanskrit manuscript, page by page.

- Entries: 18 (`verified-bhagavad-gita-01` to `-18`, one per chapter, order 1-18)
- Sections: 201 (183 page sections + 18 colophon sections), 701 verses
- Scans: 173 page images (fol. 4r to 90r), 65 MB, `site/assets/scans/bhagavad-gita/upenn559-fNNN{r,v}.jpg`
- Importer: `scripts/import_bhagavad_gita.py` (re-runnable; `--download` re-fetches)
- Check: `python3 scripts/check_collection.py bhagavad-gita` gives 18 entries, 201 sections, 0 hard failures, 0 warnings

## Manuscript

University of Pennsylvania, Kislak Center, Ms. Coll. 390 Item 559 ("Athabhagavadgītāprārambhaḥ"),
90 paper leaves, 7 lines per leaf, Devanagari with speaker headings, colophons and verse-end marks in
red. The final colophon on fol. 90r reads "... mokṣasaṃnyāsayogo nāma aṣṭādaśo 'dhyāyaḥ ||18||
saṃvat 1851 ... caitra sudi 3 dine saṃpūrṇaṃ" (Saṃvat 1851, 1794 CE). Images from OPenn
(https://openn.library.upenn.edu/Data/0002/html/mscoll390_item559.html), Creative Commons Public
Domain Mark. Contents: fol. 1r title; fol. 1v-4r Gītā-nyāsa and nine dhyāna verses (not reproduced);
fol. 4r-90r the 18 chapters; fol. 90v blank.

Why this copy: of the 15 Bhagavadgītā items on OPenn, Item 2390 (Saṃvat 1757, 1700 CE) is older but
lacks its first leaf and folios 17-35 are badly damaged; Item 2336 (Saṃvat 1841, 1784 CE) is complete
but its ink is worn toward the end and it runs to 164 leaves of 5 lines. Item 559 is complete, dated,
clean and legible on every page.

Foliation: the scribe wrote the number 41 twice; the cataloguer labels the following leaves
"41r =42r" ... "51v =52v", and the numbering is regular again from 53r. File names use the physical
leaf count (image k = verso of leaf k above recto of leaf k+1); scan notes quote the catalogue label.

## Mapping method

Every page from fol. 1r to 90v was read on the OPenn images (openings downscaled to about 660 px per
page for reading, spot-checked at full size). For each page the log records the scribe's verse
numbers with the line where each ends, speaker headings and chapter colophons:
`data/sources/bhagavad-gita/mapping_log.json`. A section is the run of verses whose text ends on one
page; if its first verse began on the previous page, both pages are listed. The script asserts that
every chapter's sections cover verses 1..N exactly once, in order. Each opening was cut into its two
pages at the shadow line between the leaves; all 173 crops were produced and a sample was viewed to
confirm each shows one whole leaf.

Points read on the images:
- Chapter 1: the scribe wrote no number after verse 28 (fol. 7r line 7); the verse is placed by its words.
- Chapter 13: the manuscript counts Arjuna's question "prakṛtiṃ puruṣaṃ caiva" as verse 1 (fol. 63v),
  giving 35 verses, exactly as Besant does. Total 701 verses.
- 18.48: its text ends at the foot of fol. 86r; its number "48" stands at the top of 86v. It is placed on 86r.
- Speaker headings that fall on the previous page (11.15 on 54v, 16.1 "śrī-" on 73v) bring that page into the section.
- Colophons of chapters 5 and 16 run over two pages (31r-31v, 76v-77r); chapter 4's colophon is on 28r.

## Texts

Sanskrit (Devanagari) and English: Annie Besant, The Bhagavad-Gita, 4th edition (Madras: G. A.
Natesan, 1922), English Wikisource "Bhagavad-Gita (Besant 4th)", Discourse 1-18, transcription
validated (revision ids in `data/sources/bhagavad-gita/besant/revids.json`). Public domain (1922;
Besant died 1933); Wikisource transcription CC BY-SA 4.0. Besant prints each verse in Sanskrit with
its English and a number, so the two languages align verse for verse. Footnote markers are dropped.
The colophon section of each chapter uses Besant's printed colophon (his Sanskrit is mostly
abbreviated with ॰; the manuscript writes it out in full and its chapter names differ in places,
noted in each scan note).

Departures from the brief, and why:
- English: K. T. Telang (SBE 8, 1882) was the requested first choice. It is continuous prose with
  no verse division (checked on the sacred-texts edition), so it cannot be split per page or per verse
  without guessing. Edwin Arnold (1885) has the same problem. Besant's 1922 verse-numbered prose
  translation is used.
- Sanskrit: GRETIL's TEI `sa_bhagavadgItA-4comm.xml` (CC BY-NC-SA) was parsed first; its markup
  interleaves the root text with four commentaries irregularly (missing or misplaced verse markers,
  commentary blocks ending in verse numbers) and it numbers chapter 1 with 46 verses. GRETIL's plain
  BORI text files carry no licence beyond "for reference purposes only". Besant's Devanagari is used
  instead, which also keeps the Sanskrit and English numbering identical to the manuscript's.

## Known gaps and uncertainties

- No verse is missing. The manuscript's preliminary nyāsa and dhyāna verses (fol. 1v-4r) are not
  reproduced because no cited text and translation of them was prepared.
- The Sanskrit shown is Besant's printed text, not a transcription of the manuscript; the scribe's
  spelling and occasional readings differ in small details (as the introductions say).
- The Wikisource transcription has irregular verse-number labels at 10.31 (missing), 11.8 (missing),
  17.19 (printed "20") and 18.14 (printed "15"); the script counts verses in sequence and checks each
  against Besant's Devanagari verse number, which is regular. Noted in the affected entries.
- Besant's English colophon of chapter 8 reads "INDESCTRUCTIBLE"; reproduced as transcribed (entry title corrected).
