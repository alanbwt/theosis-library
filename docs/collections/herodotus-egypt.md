# herodotus-egypt

**Entries:** 11 entries, 54 sections (`verified-herodotus-egypt-*`), shelf Egypt. Herodotus, Histories 2.99-2.146,
complete.

## Contents
| order | entry | chapters | folios of Laur. Plut. 70.3 |
|---|---|---|---|
| 1 | `min-and-the-330-kings` | 2.99-101 (Min, Nitocris, Moeris) | 78v-79v |
| 2 | `sesostris` | 2.102-110 | 79v-81v |
| 3 | `pheros` | 2.111 | 81v-82r |
| 4 | `proteus-and-helen` | 2.112-120 | 82r-84v |
| 5 | `rhampsinitus` | 2.121, 121a-f, 122-123 | 84v-86v |
| 6 | `cheops-and-chephren` | 2.124-128 | 86v-88r |
| 7 | `mycerinus` | 2.129-135 (with Rhodopis) | 88r-89v |
| 8 | `asychis` | 2.136 | 89v-90r |
| 9 | `anysis-and-sabacos` | 2.137-140 | 90r-91r |
| 10 | `sethos` | 2.141 | 91r-91v |
| 11 | `the-priests-chronology` | 2.142-146 (341 generations, 11,340 years) | 91v-92v |

One section per chapter; Godley's subdivisions of the Rhampsinitus story (121a-f) are separate sections.

## Sources
- Scans: Florence, Biblioteca Medicea Laurenziana, Plut. 70.3 (codex A, 10th c., 374 fols.), the oldest
  manuscript of Herodotus, colour images from the Teca Digitale IIIF (record plutei 1358114, access
  "Pubblico"; spec rule 9). 29 pages, fols. 78v-92v, 1800 px wide.
- Greek: Perseus canonical-greekLit tlg0016.tlg001.perseus-grc2, which is the Greek printed in Godley's
  Loeb (1920), CC BY-SA 4.0. Spot-checked against the printed page for 2.99.2-4 (archive.org
  historiesvolumei00hero_249, leaf n411): wording identical. `<del>` shown in square brackets; Perseus
  note markers and Homer citation tags omitted; Homer's verses in 2.116 kept as lines.
- English: A. D. Godley, Loeb vol. 1 (1920), public domain. The Perseus English (perseus-eng2) is
  "Modernized by Perseus" (S. Ott), not Godley's wording, so it was not used. The verbatim text is the
  Wikisource transcription "Herodotus The Persian Wars (Godley)/Book II", diffed word by word against the
  OCR of the 1920 printing: all disagreements were OCR faults except two Wikisource typos, corrected
  ("Sal ting-places" to "Salting-places" in 2.113, "Any sis" to "Anysis" in 2.137). Godley's footnotes
  are omitted.

## Mapping
By eye on every page image: the first and last words of each page from fol. 78v to 92v were read and
located in the Greek (accent-free matching in the importer, which asserts each location). The starts of
2.99 (fol. 78v line 24), 2.146 (fol. 92v line 11) and 2.147 (fol. 92v line 27) were also read. Each
chapter's page list is computed from these verified page breaks; a chapter crossing a page break lists
every page it touches. The breaks are quoted in each `scan_note`.

## Gaps
None in 2.99-2.146. Several pages have readers' notes in the lower margin (e.g. on Cheops, Asychis,
Anysis, Heracles and Pan); these are not part of the text and are noted where they occur.

## Open questions
- The manuscript's wording differs from the edition in places (e.g. ἐγένετο for ἐγίνετο at 2.103.2,
  ἵστη for ἵστα at 2.106.1, and a different word order at 2.145.1); the Greek shown is the edition.
- `data/authors.json` already has a `herodotus` author (tradition "neoplatonist", bio "Herodotus"); this
  collection reuses that id without redefining it. The integrator may want to correct that record.
