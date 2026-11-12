# Didache (key `didache`)

Built 2026-11-12 by `scripts/import_didache.py`.

## Contents

One entry, `verified-didache-teaching-of-the-twelve-apostles`, 16 sections (chapters 1-16, the
complete text). Ten page images: Codex Hierosolymitanus 54 fol. 76r-80v.

## Sources

| Layer | Source | License |
|---|---|---|
| Photograph | Library of Congress microfilm, "Panagios Taphos 54. John Chrysostom: Synopsis of the Testaments; Apostolic Fathers. 1056 A.D. 120 f." (Microfilm 5017), https://www.loc.gov/item/00279389694-jo/ , frames 78-83 via IIIF | LoC: "These collections are in the public domain" |
| Greek | Kirsopp Lake, The Apostolic Fathers I (Loeb, 1912), First1KGreek `tlg1311.tlg001.1st1K-grc1` | edition PD; digital text CC BY-SA 4.0 |
| English | J. B. Lightfoot, The Apostolic Fathers (1891), transcription at earlychristianwritings.com | public domain |

Harris 1887 (facsimile) was not needed: the LoC microfilm photographs every page of the
manuscript, so the scans are photographs of the object itself.

## Mapping method

Each microfilm frame is an opening (verso left, recto right); frame n = fol. (n-3)v + fol. (n-2)r,
confirmed by the folio numbers 76-80 written on the rectos. The first and last words of each of the
ten pages were read on the images and located in the Greek (table `PAGES` in the importer):

| Folio | Didache |
|---|---|
| 76r | heading Διδαχὴ τῶν δώδεκα ἀποστόλων (after the end of 2 Clement and a list of Old Testament books), 1.1-1.2 |
| 76v | 1.2-2.3 |
| 77r | 2.4-3.10 |
| 77v | 3.10-5.1 (marginal δ', ε') |
| 78r | 5.1-7.4 |
| 78v | 7.4-10.2 (marginal η', ι') |
| 79r | 10.2-11.7 |
| 79v | 11.7-13.6 |
| 80r | 13.6-16.2 (marginal ιϛ') |
| 80v | 16.2-16.8, rest of page blank |

Each chapter section lists every page that carries part of it.

## Text notes

- The First1KGreek text was read against Lake's printed pages (pp. 308-332, archive.org
  `theapostolicfath00unknuoft`). Eleven digitization errors were corrected (listed in
  `GREEK_FIXES` and in the entry's translator notes), e.g. 1.5 λαμβάνονται -> λαμβάνοντι,
  14.2 ὁ??ʼ -> οὗ, 12.2 ἡ -> ἢ. Lake's own misprints (μια 1.1, τούτωι 5.2) are kept.
  Accents and breathings were not proofread mark by mark (e.g. 2.7 ὦν, 9.2 ἦς follow the digital text).
- Elision encodings of the digital text (καθ̓, παῤ, δἰ) are written with an apostrophe; the
  colon used for the Greek raised dot is shown as ·.
- English: the ECW transcription numbers its own short lines (1:1-1:23 etc.), which do not match the
  Greek sections, so the English is given per chapter without numbers. Braces in the transcription
  (scriptural quotations and allusions) are shown as italics. Lightfoot's title line is not in the
  transcription, so section 1's English starts at "There are two ways".

## Gaps and open questions

- None in coverage: the whole Didache is in this manuscript and every page is shown.
- The Greek is Lake's edition, not a diplomatic transcription of the manuscript.
- The microfilm images are black and white; the date of the filming is not stated on the LoC item
  page and was not verified.
