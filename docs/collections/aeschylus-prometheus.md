# aeschylus-prometheus: Aeschylus, Prometheus Bound 436-525

Importer: `scripts/import_aeschylus-prometheus.py` (re-runnable; sources cached in `data/sources/aeschylus-prometheus/`, scans in `site/assets/scans/aeschylus-prometheus/`).
Shelf: Greece. Era Classical, tradition greek, category literature. Author id `aeschylus` (already in `data/authors.json`; no author row added).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 9 (436-446, 447-458, 459-468, 469-471, 472-475, 476-483, 484-499, 500-506, 507-525) | Florence, Laur. Plut. 32.9 fol. 152v, 153r, 153v |

## Sources

- Scans: Florence, Biblioteca Medicea Laurenziana, Plut. 32.9 (Medicean manuscript, Aeschylus M, 10th century), Teca digitale BML (CONTENTdm IIIF), manifest `https://cdm21059.contentdm.oclc.org/iiif/2/plutei:711140/manifest.json` (fol. 152v = id 710908, 153r = 710909, 153v = 710910). The play begins on fol. 147v (id 710898: title, hypothesis, list of characters). Terms as recorded for the other BML collections.
- Greek: Smyth, Aeschylus I (Loeb 1922), Perseus `tlg0085.tlg003.perseus-grc2` (CC BY-SA 4.0). Speaker names from the Perseus `<sp>` markup.
- English: Smyth, Aeschylus I (Loeb 1922), pp. 255-263, public domain in the US. Taken from the archive.org scan `aeschyluswithan00smytgoog` (OCR, then checked against the page images n301-n309). The Perseus English (`perseus-eng2`) was not used: its header says it was modernised in 1988 (archaisms removed), so it is not Smyth's printed text.

## Mapping method

First and last verse of each page read on IIIF crops: fol. 152v runs 408-453 (436 begins in the lower half, marked with a dash), fol. 153r runs 454-501 (459 is its sixth line), fol. 153v runs 502-561 (525 mid-page, then the first stasimon; the last line is Io's entry, 561). Words read are in `PAGES` and in every scan_note. Sections 447-458 and 500-506 cross page breaks and list two pages.

## Notes and gaps

- Partial: only 436-525 is built. The whole play (1-1093) would run over about 24 pages, fol. 147v to about 160; it was not attempted in this pass. The same method (page edges read on the Teca images, Smyth 1922 English from the archive.org scan) would extend it.
- The Greek is Smyth's edited text, not M's; Smyth's apparatus (in the 1922 printing, not reproduced here) records where M differs.
- Smyth's English has no line numbers, so English and Greek are matched by speech and sense unit, not line by line.
