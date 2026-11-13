# josephus: Josephus, Jewish Antiquities 18.63-64 (Testimonium Flavianum)

Importer: `scripts/import_josephus.py` (re-runnable; `--force` re-downloads the scans).
Collection file: `data/collections/josephus.json`. Shelf: Dead Sea Scrolls & Second Temple.
Era Apostolic, tradition jewish, category historical-witness. Author row `josephus`.
1 entry, 3 sections (one per manuscript witness), 3 images.

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-josephus-antiquities-18-63` (Ant. 18.63-64, the Testimonium Flavianum) | 3 | Vat. gr. 148 fol. 214v; Vat. gr. 342 fol. 282v; Vat. gr. 984 fol. 152v |

Each section gives the same passage (18.63-64) beside a different Greek manuscript:

| section | manuscript | date | kind | folio, lines | image |
|---|---|---|---|---|---|
| 18.63-64 (Vat. gr. 148, fol. 214v) | Vat. gr. 148 | 10th/11th c. | excerpt headed "From the 18th book of the Jewish Antiquities: testimony concerning Christ" | 214v, lines 3-13 | `josephus/vatgr148-f214v.jpg` (DigiVatLib image 226) |
| 18.63-64 (Vat. gr. 342, fol. 282v) | Vat. gr. 342 | 1087/1088 | excerpt copied after the Psalter, introduced "Ἰουδαῖος Ἰώσηππος" | 282v, lines 11-24 | `josephus/vatgr342-f282v.jpg` (DigiVatLib image 580) |
| 18.63-64 (Vat. gr. 984, fol. 152v) | Vat. gr. 984 | 1354 | complete text of the Antiquities (fol. 1r-173r), the passage in its place in book 18 | 152v, lines 27-31 | `josephus/vatgr984-f152v.jpg` (DigiVatLib image 311, left page of the opening) |

## Sources

- Scans: Biblioteca Apostolica Vaticana, DigiVatLib IIIF (digi.vatlib.it), fetched at 1600 px width.
  Vat. gr. 148 is a black-and-white microfilm image (the only one the library has published of this page);
  Vat. gr. 342 is a Polonsky Foundation colour image; Vat. gr. 984 image 311 shows the opening 152v-153r and
  is cut to the left page by the IIIF region `0,0,4700,6772`. Terms: (c) Biblioteca Apostolica Vaticana,
  non-commercial use with credit (spec rule 9), recorded in `verification.scan_license`.
- Greek: Benedikt Niese, Flavii Iosephi opera (Weidmann, 1885-1890), via Perseus canonical-greekLit
  `tlg0526.tlg001.perseus-grc2` (CC BY-SA 4.0), cached in `data/sources/josephus/`. Sections 63 and 64 of book 18.
- English: William Whiston, The Works of Flavius Josephus (1737), Perseus `tlg0526.tlg001.perseus-eng2`
  (from the Alden and Beardsley 1856 printing), public domain. Whiston prints 18.63-64 as one paragraph;
  the importer splits it at "And when Pilate," where 18.64 begins.

## Mapping method

The folio and line numbers come from T. C. Schmidt's manuscript list, published with his book *Josephus and
Jesus: New Evidence for the One Called Christ* (Oxford University Press, 2025):
https://josephusandjesus.com/manuscript-images/ (documented source, spec rule 4). Each page was then checked by
eye on the downloaded image for the opening words of 18.63, Γίνεται δὲ κατὰ τοῦτον τὸν χρόνον Ἰησοῦς σοφὸς ἀνήρ.
The QC review of 2026-11-12 read all three pages again: the heading of the excerpt at the top of 148 fol. 214v
with the passage below it to about line 13; the passage after the Psalter matter on 342 fol. 282v (about lines
11-24); and on 984 fol. 152v the red initial Γ with the marginal note περὶ τοῦ Χ(ριστο)ῦ, the passage ending
οὐκ ἐπέλιπε τὸ φῦλον within five lines, with no run-over to 153r.

## Notes and gaps

- The Greek is Niese's critical text, not a transcription of any of the three manuscripts; each scan_note says
  that the copyist's wording on the page differs in small details. Niese prints the whole passage in brackets as
  suspect; the brackets are editorial and are not shown (translator note).
- Whiston's "[the] Christ" brackets are his own.
- The oldest Greek manuscript of book 18, Milan, Biblioteca Ambrosiana F 128 sup. (11th c., fol. 274r-v), is not
  included.
- The images keep the Vatican Library's copyright bar, and the 984 and 342 images keep a narrow strip of the facing
  page; they were not re-cropped.
- The introduction cites Schmidt's argument that the passage is substantially authentic and may rest on people
  close to the trial of Jesus (Ananus II); the source is given in the translator notes. Two statements about
  "October 2026" news coverage, which had no cited source, were removed in the 2026-11-12 QC
  (`scripts/qc3_fix_entries.py`).
- Check: `python3 scripts/check_collection.py josephus` = 1 entry, 3 sections, 0 hard failures, 0 warnings.
