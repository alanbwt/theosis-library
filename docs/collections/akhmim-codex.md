# Akhmim Codex (Gospel of Peter): `akhmim-codex`

Importer: `scripts/import_akhmim-codex.py` (re-runnable; `--force` re-cuts the page images; plates are cached in
`$THEOSIS_CACHE` or `~/.cache/theosis-akhmim`).

## Contents

1 entry, `verified-akhmim-codex-gospel-of-peter`: the whole surviving Gospel of Peter (Akhmim codex pages 2-10) in
14 sections, one per chapter of J. Armitage Robinson's division. Each section shows Lods's lines for that chapter
(numbered page.line, part-lines where a chapter begins or ends mid-line) and points at the page(s) carrying them.

| Chapter | Codex lines | Chapter | Codex lines |
|---|---|---|---|
| 1 | 2.1-2.5 | 8 | 5.9-6.13 |
| 2 | 2.5-2.12 | 9 | 6.14-7.5 |
| 3 | 2.13-3.4 | 10 | 7.5-7.16 |
| 4 | 3.4-3.15 | 11 | 7.16-8.15 |
| 5 | 3.15-4.8 | 12 | 8.15-9.14 |
| 6 | 4.9-4.17 | 13 | 9.14-10.6 |
| 7 | 4.17-5.9 | 14 | 10.6-10.14 |

## Sources

- **Images**: A. Lods, *Mémoires publiés par les membres de la Mission archéologique française au Caire* IX.3
  (Paris 1893), heliogravure plates made from photographs of the manuscript taken at the Gizeh Museum
  (photographic facsimile; public domain). Internet Archive item `MMAF9.3`, images 0027-0031 = plates II-VI.
  Each plate prints two codex pages sideways with Lods's page number under each; the pages are cut out and turned
  upright (`site/assets/scans/akhmim-codex/akhmim-p01.jpg` ... `p10.jpg`; page 1, the cross, is in the catalogue row
  only).
- **Greek**: Lods's diplomatic transcription (same volume, pp. 219-224), with his page and line numbers, transcribed
  line by line from the printed pages into `data/sources/akhmim-codex/lods1893_gospel_of_peter.txt` and checked
  word by word against a Tesseract OCR of the same pages (all differences traced to OCR errors). Lacuna dots were
  counted on the full-resolution page images. Bars over nomina sacra and over a final letter standing for nu are
  combining overlines.
- **English**: J. Armitage Robinson, "The Gospel according to Peter", *Ante-Nicene Fathers* IX (1896), Wikisource
  transcription (`anf9_gospel_of_peter.wiki`), public domain. Robinson revised it against the photographic facsimile.

## Mapping method

Page and line numbers are printed by Lods for every line. Plate and page identification: Lods's page numbers under
each plate page, plus the first line of each page read on the plate (recorded per section). Chapter openings were
located in Lods's lines by their Greek words (table `CHAPTERS` in the importer) and checked against the beginning
and end of each of Robinson's English chapters.

## Gaps and open questions

- **Apocalypse of Peter** (codex pages 19-14, Lods pp. 224-227) not built yet. Its transcription is full of lacunae
  marked by runs of dots whose exact number must be counted on the print; this was started (page 19) but not
  finished. Plates VII-X of the same item carry the pages. English: M. R. James (1924, public domain in the US) or
  A. Rutherfurd (ANF IX, 1896).
- **Greek 1 Enoch 1-32** (codex pages 21-66) not built. The only open digital Greek text found is Swete's 1905 text
  in First1KGreek (CC BY-SA), which has many OCR errors (for example πρδγμα, μυνος, δετε) and would need full
  proofreading against Swete's printed pages; Lods 1893 prints only corrections to Bouriant's text, plus a useful
  page/line/chapter/verse list. The 1 Enoch text itself is complete in `enoch-ethiopic`.
- At 7.7 Lods prints the bracketed restoration as `[αν οι]` (editions read αυτοι); it is kept as printed.
- Dates proposed for the codex vary from the 6th to the 9th century; the introduction says so.
