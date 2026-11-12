# cicero-dream-of-scipio: Cicero, The Dream of Scipio

Importer: `scripts/import_cicero-dream-of-scipio.py` (re-runnable; sources cached in `data/sources/cicero-dream-of-scipio/`, scans in `site/assets/scans/cicero-dream-of-scipio/`).
Shelf: Rome. Era Late Republic, tradition roman, category philosophy. Author id `cicero` (already in `data/authors.json`, so no author row is added).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-cicero-dream-of-scipio-somnium-scipionis` (De re publica 6.9-29, complete) | 21 (6.9 to 6.29) | Bamberg, Staatsbibliothek, Msc.Class.38 fol. 1r-3r |

"Know, then, that you are a god" (deum te igitur scito esse) is section 6.26, fol. 3r column a line 17.

## Sources

- Scans: Bamberg, Staatsbibliothek, Msc.Class.38 (Cicero, Somnium Scipionis + Macrobius' commentary; end of the 10th century, Italy; 36 leaves), digitised by the Bayerische Staatsbibliothek. IIIF manifest `https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00140750/manifest`, canvases 5-9. The manifest states Public Domain Mark 1.0; the Deutsche Digitale Bibliothek record states CC BY-NC-SA 4.0. Both are recorded in `scan_license`. Images saved at 1700 px wide.
- Latin: Mueller, De re publica (Teubner 1889), Perseus `phi0474.phi043.perseus-lat2` (CC BY-SA 4.0).
- English: C. W. Keyes, Loeb Classical Library 213 (1928), pp. 261-283, public domain in the US (published 1928). Taken from the archive.org OCR (`cicero-in-28-volumes.-vol.-16-loeb-213`, Public Domain Mark) and corrected against the page images of the same scan (leaves n144-n155); every OCR correction is listed in `OCR_FIXES` in the importer. Keyes's Roman chapter numbers and footnote marks are left out. The attalus.org copy of Keyes was used only as a cross-check: it modernises "thee/ye" to "you" and has other small changes, so it was not used as the text.

## Mapping method

In this manuscript the Somnium is copied as a separate text at the head of the codex, under a red title ("Somnium Scip(ionis) M. T. C. excerptum ex libro sexto de re publica"), in two columns, fol. 1r col. a to fol. 3r col. b, closed by a red EXPLICIT SOMNIUM; the title of Macrobius' commentary follows in the same column. The first and last lines of each of the ten columns were read on full-resolution IIIF crops (words in `COLUMNS` and in each scan_note). A section is linked to every page whose columns contain part of it: 6.12, 6.17, 6.20 and 6.25 cross a page break and list two pages.

English section breaks: Keyes's English has only Roman chapter numbers; the breaks follow the Arabic section numbers printed beside his facing Latin, at the English sentence that renders the first Latin words of each section (`EN_STARTS`). These are the same section breaks as Mueller's.

## Notes and gaps

- Complete: all of 6.9-29.
- The Latin is Mueller's critical text, not a transcription of the Bamberg copy. Differences noticed while reading the column edges are noted in scan_notes: the title, "Manlio" for "Manilio" (6.9), "et quaeso" for "St! quaeso" (6.12), "acute et excitatio movetur sono" for "acuto et excitato movetur sono" (6.18).
- Older witnesses of the Somnium exist (e.g. Paris, BnF lat. 6370, 9th century), but Gallica blocks scripted access, so they were not used. Bamberg Msc.Class.37 is a Saturnalia manuscript, not the commentary.
- The manuscript leaves are stained and wormholed, but every column edge used for the mapping was legible.
