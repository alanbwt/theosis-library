# sanchuniathon

**Entries:** 6 entries, 66 sections (`verified-sanchuniathon-*`), shelf Levant & Israel.
Philo of Byblos' Phoenician History ("Sanchuniathon") as quoted by Eusebius, Praeparatio evangelica
1.9.20-1.10.55, complete, one section per Dindorf section.

## Contents
| order | entry | PE sections | Paris gr. 451 |
|---|---|---|---|
| 1 | `testimony` | 1.9.20-30 (Porphyry's testimony, Philo's preface) | fols. 204v-206v |
| 2 | `cosmogony` | 1.10.1-8 (chaos, Mot, Zophasemin, first worship) | 206v-207v |
| 3 | `first-inventors` | 1.10.9-14 (fire, huts, ships, iron, salt, writing) | 207v-208v |
| 4 | `kronos` | 1.10.15-30 (Uranus and Ge, Kronos, Byblos) | 208v-210r |
| 5 | `astarte-and-taautus` | 1.10.31-41 (Astarte, Taautus' symbols, the Greeks) | 210r-211v |
| 6 | `taautus-and-the-serpent` | 1.10.42-55 (royal sacrifice, the serpent, Eusebius' conclusion) | 211v-213v |

## Sources
- Scan: Paris, BnF, grec 451 (914 AD, scribe Baanes for Arethas; PE books 1-5 on fols. 188-322),
  Gallica ark:/12148/btv1b84701396, colour, IIIF openapi.bnf.fr, 19 pages fol. 204v-213v saved at
  2400 px height. Gallica non-commercial terms with credit.
- Greek: Dindorf, Eusebii Caesariensis opera I (Teubner 1867) pp. 37-53, from First1KGreek
  tlg2018.tlg001.1st1K-grc1 (CC BY-SA 4.0). The digital text had many errors (OCR misreadings such as
  "πριγεγραννέβα", dropped words, a garbled line in 1.10.39, page-margin letters c/d/b inside words,
  missing parentheses). Every section was proofread against the printed pages (archive.org
  bub_gb_5yRMTBxhA74C); the 133 corrections are in `data/sources/sanchuniathon/dindorf-proofread-fixes.txt`
  and asserted by the importer.
- English: Gifford 1903 (PD), tertullian.org transcription (PD) diffed word by word against the OCR of
  the 1903 printing on archive.org; disagreements settled on the page images (Thöyth, Môt, Ousöus,
  Agruëros, Gé, Demarûs, "he consecrated", "Hypsuranius", "born", "Rhea", "Iedud", "uncreate").

## Mapping
By eye: the first and last words of all 19 pages (fol. 204v to 213v) were read on the images and located
in Dindorf's text; recorded per page in `FOLIO_NOTES` and in each section's `scan_note`. A section that
crosses a page break lists both pages (18 sections). The four section openings inside fol. 213r are
also located by line.

## Gaps
- None within 1.9.20-1.10.55. Other Philo fragments (PE 4.16.11, Porphyry De abstinentia 2.56,
  Lydus, Stephanus of Byzantium) are not included.

## Open questions
- The Greek is the edition, not a transcription of the manuscript; the manuscript differs in small
  details (e.g. "παλαιότατος" where Dindorf prints "παλαίτατος" in 1.9.20).
- English is divided at clause boundaries where a Greek section starts mid-sentence (1.10.2, 1.10.19,
  1.10.24, 1.10.47 and similar).
