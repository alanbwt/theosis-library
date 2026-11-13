# plato-republic: Plato, Republic 6.506d-511e and 7.514a-521b

Importer: `scripts/import_plato-republic.py` (re-runnable; scans cached in `site/assets/scans/plato-republic/`).
Shelf: Greece. Era Classical, tradition greek, category philosophy, author `plato` (already in authors.json).
2 entries, 56 sections (Stephanus subsections).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-plato-republic-sun-and-divided-line` (506d-511e, the Sun and the Divided Line, to the end of book 6) | 25 | Laur. Plut. 80.19 fol. 72v-75r (7 pages) |
| 2 | `verified-plato-republic-allegory-of-the-cave` (514a-521b, the Cave and the return of the philosopher) | 31 | Laur. Plut. 80.19 fol. 75r-78v (8 pages) |

## Sources

- Scans: Florence, BML, Plut. 80.19 (parchment, 247 leaves, 12th century by the library's dating; Republic and Timaeus, then Synesius), Teca digitale IIIF via CONTENTdm (`cdm21059.contentdm.oclc.org`, item 950763), 1800 px. Rights statement in the manifest: CC BY-NC-SA, access 'Pubblico'; used with credit.
  - Why this manuscript: Paris gr. 1807 (A, 9th c.) was not used because Gallica's own pages refused scripts when this collection was built. Its images can be had through the BnF IIIF API (openapi.bnf.fr), which the plato-timaeus, plato-critias and plato-laws-3 collections use, so moving these Republic passages to Paris gr. 1807, the older witness, is possible later (correction 2026-11-12: this note had said Paris gr. 1807 could not be used at all). Vat. gr. 1 (9th-10th c.) contains Laws, Epinomis and Letters, not the Republic (DigiVatLib manifest ranges); Laur. Plut. 85.6 (12th c.) has only Republic books 1-2; Laur. Plut. 85.7 is 15th century; no online images of Marc. gr. 185 (D, 12th c.) were found. Vat. gr. 229 (DigiVatLib, black-and-white openings) was not examined further.
- Greek: Burnet, Platonis Opera IV (1902), Perseus `tlg0059.tlg030.perseus-grc2` (cached in `data/sources/plato-republic/`).
- English: Paul Shorey, Plato: The Republic vol. 2 (Loeb, 1935), Perseus `tlg0059.tlg030.perseus-eng2`.
  - Copyright check: the Catalog of Copyright Entries renewal lists for 1962 and 1963 (the 28th year after 1935), Project Gutenberg transcriptions pg11825-pg11828 cached in `data/sources/hyperborea/renewals/`, contain no entry for Shorey and no Plato Republic (the only Plato renewal in 1961-1964 is Random House's Jowett introduction, 1964). Not renewed, so public domain in the US. The Stanford Copyright Renewal Database could not be queried (it serves scripts a bot-check page; not bypassed).

## Section method

- Burnet's Stephanus letters stand at the start of a printed line, usually inside a sentence. Each section begins with the first sentence or speech that starts at or after the letter (split at '.', ';' and change of speaker). Subsections in which no sentence begins are joined to the one before: 509d-e, 510d-e, 514b-c, 516c-d, 518d-e, 520a-b. Page 514 has only a-c because book 7 begins there.
- English cut points (`ENG_CUTS`) were chosen by reading Greek and English side by side: each English section begins at the words that translate the first Greek sentence of the section. Where Shorey joins two Greek sentences into one English sentence, the cut falls inside his sentence (515d 'do you not think that he would be at a loss', 518d-e 'do we not?', 520d 'when the truth is that the city').

## Text checks

- English: the Perseus text was compared word by word with the OCR of the 1935 printing (archive.org `republicshorey02platuoft`, cached in `data/sources/plato-republic/shorey/`). Perseus americanises the spelling; the printing's forms were restored (to-day, colour(s), honour(s), honoured, labours, theatre, court-rooms). Also fixed in `FIX_ENG`: a Perseus markup slip ('said I,” do many others'), 'by no men strange' (print: 'by no means'), two missing closing quotation marks (507b, 507c), 'Yes, it does.' (print has a full stop), the missing full stop after 'image holds', and 'We predicate ‘to be’ of many' (quotation marks checked on the page image, p. 97). Shorey's italics are not reproduced; punctuation elsewhere follows Perseus (the OCR is too noisy around footnote markers for a full punctuation check).
- Greek: Perseus Burnet used as is.

## Mapping method

The first and last lines of all 13 pages (72v-78v) were read on crops of the images and matched to Burnet's text; every page join was checked (the last words of each page continue on the first line of the next). A section is linked to every page whose span contains part of its Greek, so 12 sections that cross a page break list two pages. Points recorded in the scan notes:
- 72v: 506d begins in line 13 ('μὴ πρὸς Διός, ἦ δ' ὅς').
- 73v: the scribe skipped part of 509a ('ἐπιστήμην δὲ καὶ ἀλήθειαν ... ἀμήχανον κάλλος ἔφη λέγεις') and wrote it in the left margin and across the foot of the page.
- 74r: below the text, a table of the divided line ('ὁρατόν'/'νοητόν'; 'εἰκασία', 'πίστις', 'διάνοια', 'νόησις').
- 75r: book 6 ends mid-page; title 'Πλάτωνος πολιτείας ἑβδόμη'; book 7 begins with the initial left blank.
- 77v: a line and a half left blank with a drawn stroke inside 519b-c; no words are missing.
- 78v: 521b ends at the end of a line ('οὐδένας ἄλλους, ἔφη'); 521c begins the next line.
A later hand wrote Stephanus page numbers in the margins (506-510, 515-521); they agree with the readings.

## Notes and gaps

- The Greek is Burnet's critical text, not a transcription of Laur. Plut. 80.19 (which writes, e.g., ξυν- for συν- in places).
- No gap between the entries: Stephanus numbering has no pages 512-513 in the Republic (book 6 ends at 511e and book 7 begins at 514a), and on fol. 75r book 7 follows book 6 directly. Together the two entries run without a break from 506d to 521b.
