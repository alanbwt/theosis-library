# Atlantis: the ancient testimonia

Key `atlantis`, prefix `verified-atlantis-`, shelf Greece. Importer: `scripts/import_atlantis.py`, which uses
the builder, text helpers and some passage definitions in `scripts/import_hyperborea.py`. Shared source caches
are in `data/sources/hyperborea/`; Atlantis-only caches (LacusCurtius Diodorus book 3, Stanley's Aelian) in
`data/sources/atlantis/`.

Plato's own account is in the collections `plato-timaeus` (Tim. 20d-25d, entries 20-25) and `plato-critias`
(complete).

## Contents

| # | Entry | Manuscript (pages) | Original | English | Sections |
|---|---|---|---|---|---|
| 1 | `herodotus-4-184-185`: Herodotus, Histories 4.184-185: Mount Atlas and the Atlantes | Florence, Biblioteca Medicea Laurenziana, Plut. 70.3 (Herodotus siglum A) (fol. 193r, 193v) | A. D. Godley | G. C. Macaulay (1890) | 2 |
| 2 | `diodorus-3-53-61`: Diodorus of Sicily, Library 3.53-61: the Amazons of Libya and the myths of the Atlantians | Vatican City, BAV, Vat. gr. 130, Diodorus siglum C (fol. 165v, 166r, 166v, 167r, 167v, 168r, 168v, 169r, 169v, 170r, 170v, 171r, 171v, 172r, 172v, 173r, 173v, 174r) | Bekker, Dindorf, Vogel (Teubner) | C. H. Oldfather (1935) | 9 |
| 3 | `strabo-2-3-6`: Strabo, Geography 2.3.6: Posidonius on Plato's Atlantis | Paris, BnF, grec 1397 (Strabo siglum A) (fol. 58r) | A. Meineke | H. C. Hamilton and W. Falconer (1854-1857) | 1 |
| 4 | `pliny-natural-history-2-205`: Pliny the Elder, Natural History 2.205: lands taken by the sea, 'if we believe Plato' in the Atlantic | Leiden, Universiteitsbibliotheek, VLF 4 (Voss. Lat. F. 4) (fol. 4v, 5r) | C. Mayhoff | John Bostock and H. T. Riley (1855) | 1 |
| 5 | `aelian-varia-historia-3-18`: Aelian, Varia Historia 3.18: Theopompus' tale of Midas and Silenus, the continent beyond Ocean and Meropis | Paris, BnF, Supplément grec 352 (fol. 113r, 113v) | R. Hercher | Thomas Stanley (1665) | 1 |

## Method

Same as `hyperborea` (see `docs/collections/hyperborea.md`): the oldest manuscript with downloadable page
images; every section's start, end and page breaks read on the images and quoted in its `scan_note`;
original-language text from named public-domain editions; English from public-domain translations only.

## Not included, and why

- Proclus, *In Timaeum* (5th c. AD; Crantor, Marcellus' *Aethiopica*): later than the 200 AD limit of this
  round.
- Plutarch, *Solon* 26.1 and 31.6-32.2 (Solon's unfinished Atlantis poem; Plato's attempt to finish it), c. 100 AD:
  not placed on a manuscript. The witnesses checked were not usable in the time available: Vat. gr. 138 is online
  only as a black-and-white microfilm, and Paris gr. 1671 (1296) holds all the Lives in two volumes under one
  manifest with repeating folio labels and no folio index. Worth a later round.
- Pliny, NH 6.199 (an island called Atlantis facing Mount Atlas): Leiden VLF 4 ends in book 5, so another
  witness (e.g. Paris lat. 6795) would be needed.

## Notes and uncertainties

- English: Macaulay 1890 (Herodotus), Oldfather 1935 (Diodorus; non-renewal check in docs/collections/hyperborea.md),
  Hamilton & Falconer 1854-57 (Strabo), Bostock & Riley 1855 (Pliny), Thomas Stanley 1665 (Aelian, keeping his spelling).

- Herodotus 4.184: where the edition prints the nameless "Atarantes", Laur. Plut. 70.3 reads "Atlantes"; the
  English (Macaulay) follows the edition. Noted in the entry.
- Diodorus 3.53-61 is a Hellenistic myth of a western people named after Atlas (via Dionysius Scytobrachion), not
  Plato's sunken island; Aelian VH 3.18 (Theopompus' Meropis, 4th c. BCE, told by an early 3rd-century AD author) is
  often read as a parody of Plato. Both are labelled as such in their introductions.
- Strabo 2.3.6: Hamilton and Falconer translated the older text of Kramer; in the sentence on the Cimbri their
  English says the migration was caused by the sea, where Meineke's Greek says it was not.
- Paris gr. 1397 is online only in black-and-white microfilm images (two-page openings, cropped to the page).
- Image licences: BnF NoC-NC; Leiden Public Domain Mark; Biblioteca Medicea Laurenziana images reproduced for
  non-commercial study with credit (Teca digitale access "Pubblico"; the integrator may wish to confirm the
  BML's current reuse wording).
