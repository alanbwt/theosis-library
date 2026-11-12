# Homer, Odyssey, Florence manuscript (`odyssey`)

Partial: books 1-2 built (2 entries, 36 sections, one per page). Books 3-24 are not built yet.
Importer: `scripts/import_odyssey.py`; page map: `data/sources/odyssey/page_map.json` (only books listed in `complete_books` are built). Scans: `site/assets/scans/odyssey/` (36 pages so far, about 660 KB each).

## Contents

| Entry | Lines | Folios |
|---|---|---|
| Book 1, Athena visits Telemachus | 1-444 | 2r (with the later copy on 1v) to 10v |
| Book 2, The assembly in Ithaca | 1-434 | 10v to 19r |

## Sources

- Manuscript: Florence, Biblioteca Medicea Laurenziana, Plut. 32.24 (parchment, 10th century, 234 folios), the oldest Odyssey manuscript with published images. BML Teca Digitale IIIF, manifest `https://cdm21059.contentdm.oclc.org/iiif/plutei:735325/manifest.json` (cached as `data/sources/odyssey/laur-32-24-manifest.json`); CC BY-NC-SA per the record. Text on fols. 1v-233v; about 24-28 lines a page.
- Greek: A. T. Murray, Loeb 1919, Perseus `tlg0012.tlg002.perseus-grc2` (CC BY-SA 4.0).
- English: A. T. Murray, Loeb 1919 (public domain in the US), Perseus `tlg0012.tlg002.perseus-eng3`, which marks every fifth line; the prose is cut there and each block goes to the page with its middle line.

## Mapping method

For every page, strips of the first and last lines (and zoomed crops where the leaf edge is curled or stained) were read and matched to the Greek; each page boundary was checked from both sides. Book 1 pages: 2r 1-19, 2v 20-46, 3r 47-74, 3v 75-100, 4r 101-126, 4v 127-154, 5r 155-180, 5v 181-206, 6r 207-232, 6v 233-256, 7r 257-284, 7v 285-310, 8r 311-336, 8v 337-362, 9r 363-388, 9v 389-414, 10r 415-440, 10v 441-444. Book 2: 10v 1-16, 11r 17-41, 11v 42-66, 12r 67-91, 12v 92-116, 13r 117-141, 13v 142-166, 14r 167-192, 14v 193-217, 15r 218-243, 15v 244-268, 16r 269-293, 16v 294-319, 17r 320-344, 17v 345-369, 18r 370-395, 18v 396-421, 19r 422-434 (then book 3.1-8).

## Notes

- fol. 1v is a later replacement page in a different hand repeating 1.1-19 of the worn original first page, fol. 2r; the section for 1.1-19 shows 2r first and 1v second.
- fol. 7r: the top edge is curled in the photograph; 1.257 is hidden and only the end of 258 shows. 257-258 are assigned to 7r because 6v ends with 256.
- No omitted or added lines were found in books 1-2.

## Remaining work

Books 3-24 (fols. 19r-233v, about 430 pages). All page images are already downloaded to the session scratchpad (`od/`), and a brief for page-mapping agents is at the session scratchpad `ODYSSEY_BRIEF.md`; append verified pages to `page_map.json`, add the book to `complete_books`, copy the scans, and re-run the importer.
