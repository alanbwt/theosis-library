# Manetho, History of Egypt (`manetho`)

Manetho of Sebennytus wrote the *Aegyptiaca* in Greek about 280 BCE. The work is lost; it survives in
quotations. This collection shows those quotations on the medieval manuscript pages that carry them.

Importer: `scripts/import_manetho.py` (re-runnable; `--force` re-downloads scans). Shelf: Egypt.

## Contents

| order | entry | witness (photographed) | sections |
|---|---|---|---|
| 1 | `verified-manetho-gods-and-demigods-syncellus` (Waddell fr. 3) | Paris gr. 1711, pp. 11-12 | 3 |
| 2 | `verified-manetho-dynasties-1-11-syncellus` (Book I, fr. 6-32) | Paris gr. 1764, fols. 2r-4v | 23 |
| 3 | `verified-manetho-dynasties-12-19-syncellus` (Book II, fr. 34-48, 52-53, 55-56) | Paris gr. 1764, fols. 4v-5v, 9r-10v | 20 |
| 4 | `verified-manetho-hyksos-josephus-apion-1-73-105` (fr. 42, 50) | Laur. Plut. 69.22, fols. 6v-8v | 8 |
| 5 | `verified-manetho-osarseph-josephus-apion-1-227-251` (fr. 54, first part) | Laur. Plut. 69.22, fols. 16r-18r | 7 |
| 6 | `verified-manetho-dynasties-20-31-syncellus` (Book III, fr. 57-75) | Paris gr. 1764, fols. 10v-11v | 24 |

Total: 6 entries, 85 sections, 25 images.

## Sources

- **Images.** Florence, Biblioteca Medicea Laurenziana, Plut. 69.22 (10th c., Contra Apionem only),
  Teca Digitale IIIF. Paris, BnF grec 1711 (11th c.; Syncellus on pp. 1-230) and grec 1764
  (11th c.; Syncellus, acephalous, ed. reg. pp. 51-341), Gallica IIIF (microfilm; single pages are
  cropped from the double-page openings at the gutter).
- **Greek, Josephus.** Niese, *Flavii Iosephi opera* vol. 5 (1889), Perseus tlg0526.tlg003 (CC BY-SA).
- **Greek, Syncellus.** C. Müller, *FHG* II (1848), from the Digital FHG (dfhg-project.org, CC BY-NC-SA 4.0),
  every fragment used compared with the printed page (archive.org `fragmentahistori02mueluoft`) and
  corrected (`DFHG_FIXES` in the importer: lost numeral signs ͵ ϛ ϟ ϡ, OCR slips, two lost kings in
  Eusebius' 29th dynasty). Müller's inline apparatus in parentheses (sigla, references, sums) is removed;
  his square brackets are kept.
- **English, Josephus.** Whiston (1737), Perseus tlg0526.tlg003.perseus-eng2, footnotes removed, split at
  the Niese sections; five e-text slips corrected against the printed 1860 Whiston.
- **English, Syncellus.** W. G. Waddell, *Manetho* (Loeb 350, 1940), LacusCurtius transcription, checked
  word-window by word-window against the OCR of the printed Loeb (archive.org `manethowithengli00maneuoft`);
  two transcription slips fixed (`WADDELL_FIXES`).

## Licence decision for Waddell

Waddell's Loeb was published in 1940 (Harvard / Heinemann). A US renewal would have been due in 1967 or
1968. The Copyright Office renewal records for 1966-1969 (NYPL `cce-renewals` data, files 1966-1, 1967-1,
1968-1, 1969-1) contain no entry for Waddell or Manetho and no Loeb Classical Library entry at all, while
other Harvard 1940 books do appear as renewed. LacusCurtius (Bill Thayer) states the same conclusion.
Waddell died in January 1945, so the translation is also out of copyright in life+70 countries.
Treated as public domain.

Gallica and BML photographs: non-commercial reuse with credit, accepted under spec rule 9.

## Mapping method

Every page was opened and read. For Josephus each Niese section start was found on the page and recorded
with its line number (the copyist marks Manetho's quoted words with marginal strokes). For Syncellus each
dynasty list was located by its heading, the marginal dynasty numeral (Book III) and its opening words;
the section notes record what was read. Lists that run across a page break name both folios. The copyist's
transpositions (end of Africanus' 2nd dynasty joined to Eusebius' 2nd; end of Eusebius' 2nd after
Africanus' 4th) are recorded in the notes.

## Gaps

- No gaps remain in the thirty-one dynasties (both versions). **Dynasty XVIII** is given as six sections, three per
  version, because Syncellus splits each list into three passages between his own arguments: Africanus on fol. 5v
  lines 3-5, fol. 9r (below 'Οἱ λοιποὶ βασιλεῖς ...') and fol. 10r lines 8-14; Eusebius on fol. 5v lines 6-8
  (repeated fol. 9r lines 3-4), fol. 10r lines 1-7, and fol. 10r lower half to 10v line 3. Müller's composite
  fr. 52-53 is split at those boundaries. B lacks the words Müller brackets after Achencherses
  ('ἔτη ιβ'. Ἄθωρις ἔτη λθ'. Κενχέρης'). Paris gr. 1711 was not needed.
- In B, Africanus' Dynasty XII stands on fol. 4v before the Eusebian Book I (Goar prints it at p. 69).
- **Panodorus on the gods' years (Waddell fr. 2)** and the Old Chronicle / Book of Sothis (Waddell
  appendices) are not included; fr. 2 is in Paris gr. 1711 before p. 30 but was not located.
- **Josephus, Against Apion 1.227-251** (Osarseph and the lepers) is built, mapped like 1.73-105 (every section
  start read on fols. 16r-18r, line numbers in the notes); English is Whiston (Perseus e-text) with eleven slips
  corrected against the 1860 printing. Josephus' refutation (1.252-287, which quotes Manetho again in places) is
  not included.
- Fragments preserved only in the Armenian Eusebius or in Latin (Excerpta Barbari) are out of scope
  (no Greek).
- Syncellus' remark after Eusebius' 6th dynasty and the line on the Macedonian kings after the 31st are
  Syncellus' own words and are omitted.

## Open questions

- Müller's Greek is a critical text; this manuscript differs in spellings and some numbers (e.g. B writes
  Ὄβνος for Onnos, σοζ' for the 4th dynasty total). The notes mention the differences seen.
- Paris gr. 1711 p. 11 also carries Berossus' table of the ten antediluvian Chaldean kings (for the
  `berossus` collection).
