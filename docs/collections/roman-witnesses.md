# Roman witnesses to Christ and the Christians (`roman-witnesses`)

Importer: `scripts/import_roman_witnesses.py` (re-runnable; `--force` re-downloads scans).
Shelf: Rome. Era: Imperial. Tradition: roman. Category: historical-witness. Language: Latin (`la`).

## Contents

| order | entry | sections | manuscript page(s) |
|---|---|---|---|
| 1 | `verified-roman-witnesses-tacitus-annals-15-44` | 5 (the chapter cut at sentence breaks) | Laur. Plut. 68.2, fol. 38r col. b lines 9-35, fol. 38v col. a lines 1-4 |
| 2 | `verified-roman-witnesses-suetonius-claudius-25-4` | 1 (Claud. 25.4) | Cod. Guelf. 268 Gud. lat., fol. 109v lines 24-26, fol. 110r lines 1-3 |
| 3 | `verified-roman-witnesses-suetonius-nero-16-2` | 1 (Nero 16.2) | Cod. Guelf. 268 Gud. lat., fol. 121r lines 8-16 |

Totals: 3 entries, 7 sections, 5 scan images (`site/assets/scans/roman-witnesses/`, long side 2600 px).

## Sources

- **Tacitus scans**: Florence, Biblioteca Medicea Laurenziana, Plut. 68.2 (second Medicean, Beneventan, 11th c.),
  Teca Digitale on CONTENTdm IIIF (item plutei:1335097; fol. 38r = plutei:1334785, 38v = plutei:1334786).
  The old host tecadigitale.bmlonline.it no longer resolves; the library now links to tecabml.contentdm.oclc.org.
  Access marked "Pubblico"; used for non-commercial scholarly reproduction with credit.
- **Suetonius scans**: Wolfenbuettel, Herzog August Bibliothek, Cod. Guelf. 268 Gud. lat. (Suetonius, 173 fols,
  11th c.), Wolfenbuetteler Digitale Bibliothek `/max/` JPEGs (00222 = 109v, 00223 = 110r, 00245 = 121r).
  HAB publishes its images as public domain (usage notes page).
- **Latin**: Fisher 1906 (Tacitus) and Ihm 1908 (Suetonius) from Perseus canonical-latinLit (CC BY-SA 4.0).
- **English**: Church and Brodribb 1869 (Perseus, public domain); J. C. Rolfe, Loeb 1914, from LacusCurtius
  (marked public domain).

## Mapping method

All mappings were made by reading the manuscripts on the images (2026-11-12) and are recorded with opening and
closing words and line numbers in each `scan_note`. Line counts were cross-checked with an ink-projection count
(Plut. 68.2 fol. 38r col. b: 35 lines; Gudianus pages: 26 lines). For Tacitus, fol. 38r is also the folio given in
the Wikimedia Commons description of the photograph of that page.

- Tacitus 15.44 begins at fol. 38r col. b line 9 "Et hec q(ui)de(m) huma|nis" and ends at fol. 38v col. a line 4
  "absumeren|tur", before 15.45 "Interea". Part 5 straddles both pages and lists both images.
- Claudius 25.4 begins at fol. 109v line 24 "Iudeos impulsore chresto" and ends at fol. 110r line 3 "predicantes",
  before 25.5 "Druidarum".
- Nero 16.2 begins at fol. 121r line 8 "Multa sub eo" (red initial) and ends on line 16 "relegate", before 17
  "Aduersus falsarios"; the copyist writes "xpiani" (line 13).

The Latin shown is the critical edition, not a diplomatic transcription; notable manuscript readings (Plut. 68.2:
"chri stianos" with a correction, "coniuncti", "circulo") are noted in the scan notes.

## Gaps and decisions

- **Suetonius witness**: the brief asked for Paris, BnF lat. 6115 (Memmianus, 9th c., Gallica ark:/12148/btv1b9066860v).
  Gallica's IIIF manifest and image server returned HTTP 403 (Cloudflare block) to automated requests and to
  WebFetch on 2026-11-12, so the 11th-century Wolfenbuettel Gudianus was used. If Gallica access is available
  later, the Memmianus folios could be added as second witnesses (folios still to be found by reading the pages).
- **Pliny the Younger, Letters 10.96-97**: not built. No manuscript of book 10 survives; the text rests on the
  printed editions of 1502 (Avantius) and 1508 (Aldus), made from a lost Paris manuscript. A printed book is not a
  photograph of the original object (spec rule 5).
- Vat. lat. 1904 was checked as a possible Suetonius witness; fol. 58r carries Sallust's Catiline, so it was not used.

## Open questions

- Tacitus section labels are "15.44 (1)" to "(5)", cut at sentence breaks; they were not checked against the
  section numbers of a modern edition, so the labels avoid claiming those numbers.
- The statement that the "i" in "chri stianos" corrects an original "e" is attributed to scholars since
  G. Andresen (1902); the erasure itself is not clearly visible at the resolution of the Teca Digitale image.
- BML reuse terms: no explicit licence is shown on the IIIF manifest beyond "Pubblico"; the credit line and the
  non-commercial basis (Codice dei beni culturali art. 108 c. 3-bis) should be confirmed by the integrator.
- Authors `tacitus` and `suetonius` already exist in `data/authors.json` (with placeholder bios and tradition
  "neoplatonist"); this collection reuses those ids and does not add an `authors` block.
