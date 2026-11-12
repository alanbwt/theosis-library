# Homer, Odyssey, Florence manuscript (`odyssey`)

All 24 books built: 24 entries, 482 sections (one per manuscript page). Books 1-23 are complete. Book 24 is given for lines 1-103 only, because the manuscript ends there (see Gaps).
Importer: `scripts/import_odyssey.py`; page map: `data/sources/odyssey/page_map.json` (`complete_books` 1-23; `partial_books` 24, ending at 24.103). Scans: `site/assets/scans/odyssey/` (465 pages, about 280 MB).

## Contents

| Entry | Lines | Folios | Pages |
|---|---|---|---|
| Book 1, Athena visits Telemachus | 1-444 | 2r (with the later copy on 1v) to 10v | 18 |
| Book 2, The assembly in Ithaca | 1-434 | 10v to 19r | 18 |
| Book 3, Telemachus at Pylos | 1-497 | 19r to 29r | 21 |
| Book 4, Telemachus at Sparta | 1-847 | 29r to 45v | 34 |
| Book 5, Calypso and the raft | 1-493 | 45v to 55v | 21 |
| Book 6, Nausicaa | 1-331 | 55v to 62r | 14 |
| Book 7, The palace of Alcinous | 1-347 | 62v to 69v | 15 |
| Book 8, The games of the Phaeacians | 1-586 | 69v to 81r | 24 |
| Book 9, The Cyclops | 1-566 | 81v to 92v | 23 |
| Book 10, Aeolus, the Laestrygonians and Circe | 1-574 | 92v to 103v | 23 |
| Book 11, The land of the dead | 1-640 | 103v to 116r | 26 |
| Book 12, The Sirens, Scylla and Charybdis | 1-453 | 116r to 125r | 19 |
| Book 13, Odysseus reaches Ithaca | 1-440 | 125r to 134r | 19 |
| Book 14, In the hut of Eumaeus | 1-533 | 134r to 144v | 22 |
| Book 15, Telemachus returns | 1-557 | 144v to 155v | 23 |
| Book 16, Father and son | 1-481 | 155v to 164v | 19 |
| Book 17, Odysseus in his own hall as a beggar | 1-606 | 165r to 177r | 25 |
| Book 18, The beggar Irus | 1-428 | 177r to 185r | 17 |
| Book 19, Penelope and the beggar; the scar | 1-604 | 185v to 197v | 25 |
| Book 20, Portents for the suitors | 1-394 | 197v to 205r | 16 |
| Book 21, The bow | 1-434 | 205v to 214r | 18 |
| Book 22, The slaying of the suitors | 1-501 | 214r to 224r | 21 |
| Book 23, Penelope and Odysseus | 1-372 | 224r to 231v | 16 |
| Book 24, The suitors in Hades (lines 1-103) | 1-103 | 231v to 233v | 5 |

## Sources

- Manuscript: Florence, Biblioteca Medicea Laurenziana, Plut. 32.24 (parchment, 10th century), the oldest Odyssey manuscript with published images. BML Teca Digitale IIIF, manifest `https://cdm21059.contentdm.oclc.org/iiif/plutei:735325/manifest.json` (cached as `data/sources/odyssey/laur-32-24-manifest.json`); CC BY-NC-SA per the record. Text on fols. 1v-233v; mostly 24-28 lines a page.
- Greek: A. T. Murray, Loeb 1919, Perseus `tlg0012.tlg002.perseus-grc2` (CC BY-SA 4.0).
- English: A. T. Murray, Loeb 1919 (public domain in the US), Perseus `tlg0012.tlg002.perseus-eng3`, which marks every fifth line; the prose is cut there and each block goes to the page with its middle line.

## Mapping method

For every page, strips of the first and last lines were read on the photograph and matched to Murray's Greek; every page break was checked from both sides (last line of one page, first line of the next). A line counter flagged pages whose physical line count differed from the edition range; each flagged page was viewed in full and the verses were counted by eye, which is how the omitted, added, marginal and reordered lines below were found. Pages with headings, ornaments or scholia were viewed in full. The page-by-page ranges are in `page_map.json`; each section's `scan_note` gives the first and last line, the neighbouring pages' boundaries and any peculiarity of the page.

Where the scribe omits an edition line, the line stays in the page's range (the Greek and English shown are Murray's full text) and the note says it is not on the page. Where an omitted line falls at a page edge (15.63, 23.127-128 moved to the foot of 226v, 10.482), `page_map.json` records the first or last line actually written as `begins` or `ends`.

## Scribal omissions, additions, marginal and reordered lines (books 3-24)

- Omitted (not on the page at all): 3.78, 3.493; 4.399, 4.432; 5.91, 5.157, 5.179, 5.479; 6.21, 6.313-315 (a different line beginning ὣς ἄρα φωνήσασ(α) stands in their place on 62r); 8.27, 8.58, 8.303, 8.335; 9.489, 9.531; 10.201-202, 10.253, 10.265, 10.315, 10.368-372, 10.430, 10.469-470, 10.482 (the last line of 101v repeats the end of 10.481 instead), 10.504; 11.60, 11.92, 11.407; 13.271; 14.154, 14.369-370, 14.515-517; 15.63, 15.139, 15.295; 16.224; 17.547; 18.318, 18.393; 19.291-292; 21.276, 21.308; 22.43, 22.191; 23.320; 24.32.
- Written in the margin rather than in the column: 3.19, 3.308, 3.396, 3.402; 4.303, 4.783; 8.265; 10.21, 10.35; 11.442-443; 12.6, 12.105, 12.239-241; 13.289; 14.429; 15.65, 15.345, 15.450-451; 16.14, 16.317; 17.381; 18.83, 18.158; 19.153; 21.293. Faded marginal additions seem to supply 7.161, 7.213 and 9.30, which are missing from the column.
- Squeezed in between lines or joined to the previous line: 4.294, 11.356, 12.55, 12.207, 13.347-348, 17.574, 19.122, 19.219, 20.331 (split), 21.292, 22.420, 8.541.
- Added lines not in Murray's text: after 4.228 (begins Αἰγυπτίη, ends εὐρεῖα χθών), after 18.111 (ὧδε δέ τις εἴπεσκε νέων ὑπερηνορεόντων), after 20.244 (Νίσου φαίδιμος υἱὸς ἀγορήσατο καὶ μετέειπε).
- Order: 3.304 before 3.305 (Murray prints 305 first); 8.535 before 8.534 (marked β α); 16.455 written after 16.451; 23.127-128 written after 23.131 (marked).
- Repeated or cancelled lines: 19.177-179 written twice on 189r; 19.290 written twice (repeat struck through); 23.105-107 written by mistake after 23.69 on 225v and cancelled; false starts struck through on 127v and 149r.

## Changes to books 1-2

- fol. 6v ends with 1.258 and fol. 7r begins with 1.259 (the earlier map gave 6v 233-256 and 7r 257-284). Rechecked on the images: 1.257-258 are the last two lines of 6v; the faint letters on the curled top edge of 7r are not a line of the column.
- No other changes to books 1-2; as before, fol. 1v is a later replacement page repeating 1.1-19.

## Gaps and open questions

- The codex ends with fol. 233v at 24.103. Lines 24.104-548 are not in this manuscript and are not published. Covering them needs another witness (another Odyssey manuscript with published images); not done here.
- 103v: the curled top edge shows part of one more line of writing above 10.561 that cannot be read.
- 62r: the line standing in place of 6.313-315 begins ὣς ἄρα φωνήσασ(α); the rest was not identified.
- 65v, 66v, 82r: the faded marginal additions are read as 7.161, 7.213 and 9.30 from their position and first letters only.
- Curled top edges hide part of the first line on 7r, 70r, 98v and 139r; the first line was identified from the visible part and from the previous page.
- 188v: the last three verses (19.170-172) are in fainter ink and 19.170 has a stroke through it.
- 185v and 197v have headings and notes in later hands at the top of the page; they are not Odyssey text.
- Murray's English for 24.100-104 is shown with 233v although 24.104 is not on the page (said in that section's note).
