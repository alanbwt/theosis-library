# diodorus-egypt

**Entries:** 6 entries, 21 sections (`verified-diodorus-egypt-*`), shelf Egypt. One section per chapter.

## Contents
| order | entry | chapters | Vat. gr. 130 pages (DigiVatLib image, side) |
|---|---|---|---|
| 1 | `origins` | 1.10-13: first men from the Nile mud, Osiris and Isis as sun and moon, the elements as gods, the god-kings | 0012 R - 0015 R |
| 2 | `isis-osiris-hermes` | 1.14-16: Isis and grain and law, Osiris and Thebes and the vine, Hermes the inventor | 0015 R - 0017 L |
| 3 | `osiris-campaign` | 1.17-20: the campaign of Osiris through the world | 0017 L - 0019 R |
| 4 | `death-of-osiris` | 1.21-22: Typhon, Isis and Horus, the tombs at Memphis and Philae | 0019 R - 0021 R |
| 5 | `colonies-and-claims` | 1.23-29: 10,000+ years from Osiris to Alexander, the Egyptian Heracles, Isis the healer, lunar years, the giants, the stelae of Isis and Osiris, the colonies | 0021 R - 0026 R |
| 6 | `reign-lengths` | 1.44: gods and heroes nearly 18,000 years, then mortal kings | 0040 L-R |

## Sources
- Scans: Vat. gr. 130 (parchment, mid-10th c., siglum C; books 1-5), DigiVatLib IIIF, black-and-white
  microfilm openings, each split at the gutter into single pages, caption bar cropped. Chosen as the
  oldest witness; Laur. Plut. 70.1 is 14th c. and abbreviated, Paris gr. 1665 has books 16-20 only.
  No folio numbers are legible, so pages are cited by DigiVatLib image number and side. Terms as shown
  on the images: "© Biblioteca Apostolica Vaticana, all rights reserved" (spec rule 9).
- Greek: Vogel (Teubner 1888) via Perseus tlg0060.tlg001.perseus-grc5 (CC BY-SA 4.0). Machine-collated
  with the OCR of the printed volume (archive.org diodoribibliothe01diod_0); flagged places checked on
  the page images. Five fixes: dropped πράξεις (26.7), broken word (26.8), Vogel's square brackets
  restored at 28.5 [ἱεροποιοὶ] and 44.1 [ἀπὸ Μοίριδος], Αἰθίοκας > Αἰθίοπας (44.2).
- English: Oldfather, Loeb vol. 1 (1933). Public domain: the 1933 copyright would have had to be
  renewed in 1960-1961; the renewal registrations for 1959-1962 (NYPL cce-renewals TSV, cached in
  `data/sources/diodorus-egypt/cce-renewals/`) contain no entry for Oldfather or Diodorus, while other
  1933 Harvard books were renewed (e.g. R272802, R272801, 20 Mar 1961). LacusCurtius states the same.
  Text from Thayer's LacusCurtius transcription, collated with the OCR of the 1933 printing
  (archive.org in.gov.ignca.2849) and every real disagreement checked on the page images. Thayer's
  text follows a later printing in 17 places ("he says" for "they say", "dykes", "Selenê", etc.);
  the 1933 wording is restored (`EN_FIXES` in the importer). Thayer's added "of" (21.4) removed.

## Mapping
For every page from image 0012 right to 0026 right, and both pages of image 0040, the first and last
two lines were read on the image and located in Vogel (log in
`data/sources/diodorus-egypt/vat-gr-130-page-breaks.txt` and `PAGE_BREAKS` in the importer). Each
chapter lists the pages that carry it; each scan_note records the opening and closing words of every
page it uses and which sections they belong to.

## Gaps
- 1.30-43 (geography of Egypt, the Nile, animal life, early diet) and 1.45 onward (the mortal kings)
  are outside this collection's scope. 5.55-58 (Telchines, Rhodian flood) not attempted.
- Chapter-level sections: a chapter spanning three pages lists all three; the notes say which
  sub-sections fall on which page.

## Open questions
- The Greek is Vogel's edition, not a transcription; the copy differs in small details (e.g. 12.7
  'εἶναι τὸν ἀέρα' without φύσει on image 0014 right).
- Folio numbers: image 0004 shows book 1 beginning on its right-hand page after the paper leaf with the
  Photius note, but without legible foliation the images are cited by number only.
- The English collation relied on OCR plus page images; places where the OCR was illegible were read
  on the images page by page (pp. 35-95, 157-159).

## QC fixes (2026-11-12)
Page note for DigiVatLib image 0021, right page (sections 1.22 and 1.23): it quoted the edition ('τιμᾶν τοῦτο τὸ μόριον'); the page begins 'τοῦτο τὸ μόριον ἔν τε τοῖς μυστηρίοις', and the edition's 'τιμᾶν' is not on it nor at the end of the previous page (checked on the images). The note now quotes the page and says so. Review: docs/qc/review-near-east.md; fixes: docs/qc/fixes-near-east.md.
