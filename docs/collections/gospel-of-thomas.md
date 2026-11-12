# Gospel of Thomas (Nag Hammadi Codex II): `gospel-of-thomas`

Importer: `scripts/import_gospel_of_thomas.py` (re-runnable; `--force` re-downloads sources and scans).

## Contents

20 entries, one per codex page of Nag Hammadi Codex II, pages 32-51 (Cairo, Coptic Museum, inv. 10544,
tractate II,2, 4th century). Each entry holds the sayings that begin on that page; 116 sections in all:
the incipit (prologue), sayings 1-114, and the subscript title (51.27-28). A saying that runs onto the
next page lists both page photographs. The whole text is covered; there are no missing sayings.

| Entry | Sayings | Pages |
|---|---|---|
| page-32 | prologue, 1-3 | 32-33 |
| page-33 | 4-8 | 33-34 |
| page-34 | 9-13 | 34-35 |
| page-35 | 14-16 | 35-36 |
| page-36 | 17-21 | 36-37 |
| page-37 | 22 | 37 |
| page-38 | 23-29 | 38-39 |
| page-39 | 30-37 | 39-40 |
| page-40 | 38-45 | 40-41 |
| page-41 | 46-50 | 41-42 |
| page-42 | 51-57 | 42-43 |
| page-43 | 58-62 | 43-44 |
| page-44 | 63-64 | 44 |
| page-45 | 65-71 | 45 |
| page-46 | 72-78 | 46-47 |
| page-47 | 79-86 | 47-48 |
| page-48 | 87-95 | 48-49 |
| page-49 | 96-101 | 49-50 |
| page-50 | 102-109 | 50-51 |
| page-51 | 110-114, subscript | 51 |

## Sources

- **Photographs**: Claremont Colleges Digital Library, Nag Hammadi Archive (Institute for Antiquity and
  Christianity), IIIF image API at ccdl.claremont.edu. Pages 32-33 and 35-51: A-Series negatives
  (photographer Basile Psiroukis), each published in *The Facsimile Edition of the Nag Hammadi Codices:
  Codex II* (Brill 1974), pp. 42-63 per the CCDL records (saved in `data/sources/gospel-of-thomas/ccdl_item_metadata.json`).
  Page 34: the A-Series negative shows only loose fragments, so the left half of P-Series negative no. 191
  (September 1975, "P II, 34+109") is used. Holder's rights statement: "Physical rights are retained by the
  institution. Copyright is retained in accordance with U. S. Copyright laws." Used for non-commercial
  scholarly reference with credit; no open licence is stated.
- **Coptic**: Coptic SCRIPTORIUM, *Gospel of Thomas*, edition and annotation by Paul Dilley (with
  L. Bremer-McCollum, C. T. Schroeder, A. Zeldes), version 6.2.0, CC BY 4.0; TreeTagger export pinned to
  CopticScriptorium/corpora commit e624efd. Shown in the manuscript's spelling (orig layer), as bound
  groups, line by line with the edition's page.line numbers. Editorial signs are the edition's.
- **English**: Mark M. Mattison, *The Gospel of Thomas* (gospels.net/thomas), dedicated by the translator
  to the public domain. Saying headings are Mattison's (given in each section's `original_ref`).

## Mapping method

Page and line breaks come from the edition's pb/lb markup (Dilley made the edition from the Facsimile
Edition photographs, the same negatives). Page 32: the edition numbers the Thomas lines 1-18; on the page
they are lines 10-27 (lines 1-9 carry the end and title of the Apocryphon of John), so 9 is added. Every
page (32-51) was then checked by eye: the first and last line of Thomas text on each photograph was read
and matched to the edition's line of the same number; results are in `PAGE_CHECKS` in the importer and in
each entry's introduction. Saying 3 thus begins at 32.19 and ends at 33.5, as in the standard citations.

## Known issues and open questions

- Where a word is divided between two lines on the papyrus, the edition sometimes keeps the word whole on
  one line (seen at 35.30-31, 39.33-34 and the page change in saying 13, where the photograph has ⲙⲁⲑ⳿ at
  the end of 34.34 and ⲑⲁⲓⲟⲥ at the start of 35.1). Line numbers in the Coptic can therefore be a few
  letters off within a line; page assignments of sections are not affected. Noted in every entry.
- The Coptic and the English do not share verse numbers (Mattison gives none); sections are per saying.
- The Greek Oxyrhynchus fragments (P. Oxy. 1, 654, 655) are not included.
- The edition contains a few unusual markup strings kept verbatim (for example `\bⲉ/` for a letter
  written above the line).
- Image terms are "copyright retained" rather than an open licence; the integrator may want to confirm
  this is acceptable alongside the BAV-style non-commercial use elsewhere in the library.

## Check

`python3 scripts/check_collection.py gospel-of-thomas` → 20 entries, 116 sections, 0 hard failures,
2 warnings (entries page-45 and page-51 have all sections on their single page, as intended).
