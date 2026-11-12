# 1 Enoch (Ethiopic, Rylands MS 23): `enoch-ethiopic`

Importer: `scripts/import_enoch-ethiopic.py` (re-runnable; `--mapping` prints the column map, `--force` re-downloads the page images).

## Contents

The complete Book of Enoch (1 Enoch 1-108) in 5 entries and 108 sections (one section per chapter).

| Entry | Chapters | Folios of Rylands Ethiopic MS 23 |
|---|---|---|
| `verified-enoch-ethiopic-watchers` | 1-36 (Book of the Watchers) | 2r-5r |
| `verified-enoch-ethiopic-parables` | 37-71 (Book of Parables) | 5r-9r |
| `verified-enoch-ethiopic-luminaries` | 72-82 (Astronomical Book) | 9r-11v |
| `verified-enoch-ethiopic-dream-visions` | 83-90 (Dream Visions, Animal Apocalypse) | 11v-14r |
| `verified-enoch-ethiopic-epistle` | 91-108 (Epistle of Enoch, Birth of Noah, ch. 108) | 14r-16v |

Nothing is missing: every chapter has Ge'ez, English and the page image(s) that carry it.

## Sources

- **Photographs**: Manchester, John Rylands Library, Ethiopic MS 23 (18th c., parchment, 3 columns of 40 lines; Enoch, Job, Kings).
  Manchester Digital Collections IIIF manifest `https://www.digitalcollections.manchester.ac.uk/iiif/MS-ETHIOPIC-00023`
  (saved as `data/sources/enoch-ethiopic/manchester_ethiopic23_manifest.json`). The library's logical structure puts
  Enoch on fol. 1r-16v; fol. 1r-1v hold pen trials and a contents note, so the text runs fol. 2r-16v (30 page images,
  `site/assets/scans/enoch-ethiopic/rylands-eth23-f02r.jpg` ... `f16v.jpg`, 2000 px tall). Licence: CC BY-NC 4.0 for
  downloaded images.
- **Ge'ez**: A. Dillmann, *Liber Henoch Aethiopice* (Leipzig 1851), digital text of M. Jerabek (Library of Ethiopian
  Texts, 1995) in R. HaCohen's Unicode version (Tel Aviv University, 2011), one HTML file per chapter
  (`data/sources/enoch-ethiopic/dillmann/`). Terms: free for non-commercial use with the copyright notice. The digital
  text has chapter numbers but no verse numbers.
- **English**: R. H. Charles, *The Book of Enoch* (SPCK 1917), Project Gutenberg #77935, public domain
  (`data/sources/enoch-ethiopic/charles/pg77935.html`). The parsed chapters are also saved as
  `data/sources/enoch-ethiopic/charles_1917_chapters.json` (E = Ethiopic column, G = Akhmim Greek column where Charles
  prints both), which the Akhmim importer reuses.

## Mapping method

Visual. The first line of each of the 90 text columns (fol. 2r col. a to fol. 16v col. c) was read on full-resolution
IIIF crops and transcribed (`COLUMN_STARTS` in the importer). Each reading is located in Dillmann's text with a
consonant-skeleton match that merges the Ge'ez homophone letters; every match scores at least 0.85, the 90 positions
run in text order, and the script fails if either condition breaks. A chapter points at every page whose columns it
touches. Boundaries that fall at a column edge were checked on the image: chapter 30 begins at the top of fol. 4v
col. c; chapter 61 begins in the last line of fol. 7v col. a after a red section mark; chapter 106 begins in line 1
of fol. 16r col. c after a red section mark; the book ends in line 4 of fol. 16v col. c, followed by a one-line
scribal note and a decorated band. Each section's `scan_note` gives the column where the chapter begins and ends and
the words read at the top of those columns.

## Known differences and open questions

- The Ge'ez is Dillmann's critical text, not a transcription of Rylands MS 23. The scribe's spelling and some
  wording differ (for example fol. 2v col. c reads ‹እግዚአብሔር፡ ሑር፡ አይድዕ› where Dillmann has ‹እግዚአብሔር ፡ አይድዕ›).
- Charles translated his own critical text (1906), which differs from Dillmann's in places. His signs are kept
  (⌜ ⌝ Greek only, 〚 〛 Ethiopic only, ‹ › restored, [ ] interpolation, ( ) supplied, † † corrupt); words he printed in
  thick type (emended) are in italics.
- Charles prints chapter 92 before 91 and moves 91:12-17 after chapter 93; here each chapter's verses are gathered
  under their own number, in Charles's order. The two parallel columns of 90:13-18 are given in verse order.
- In chapters 22, 27 and 32 Charles gives the Ethiopic and the Akhmim Greek side by side; the Ethiopic column is used.
- Jerabek's digitization was cleaned by HaCohen without collation against the printed book; it has not been
  re-collated with Dillmann's 1851 print here.
- The manuscript marks many section openings with red signs and numbers; these were not used for the mapping.
- Another witness considered: Bodleian MS. Bruce 74 (the manuscript James Bruce brought to Europe), but Digital
  Bodleian has photographed only fol. 1-33, and Enoch continues past fol. 33v (fol. 33v is at 93:8).
