# Dhammapada (`dhammapada`)

The complete Dhammapada (423 verses), one entry per chapter (vagga): `verified-dhammapada-<nn>-<vagga>`, 26 entries,
47 sections. Inside each entry, one section per manuscript page (one side of a palm leaf): the verses whose last
syllable stands on that side. A verse begun on the previous side lists both sides.

## Contents

| Ch. | Vagga | Verses | Sides (fol.) |
|---|---|---|---|
| 1 | Yamakavagga, The Twin-Verses | 1-20 | 5a, 5b |
| 2 | Appamādavagga, On Earnestness | 21-32 | 5b |
| 3 | Cittavagga, Thought | 33-43 | 5b, 6a |
| 4 | Pupphavagga, Flowers | 44-59 | 6a, 6b |
| 5 | Bālavagga, The Fool | 60-75 | 6b, 7a |
| 6 | Paṇḍitavagga, The Wise Man | 76-89 | 7a |
| 7 | Arahantavagga, The Venerable | 90-99 | 7a, 7b |
| 8 | Sahassavagga, The Thousands | 100-115 | 7b, 8a |
| 9 | Pāpavagga, Evil | 116-128 | 8a, 8b |
| 10 | Daṇḍavagga, Punishment | 129-145 | 8b, 9a |
| 11-26 | Jarā ... Brāhmaṇavagga | 146-423 | 9a-16b |

(Exact side for every verse: `READINGS` and the section headings in each entry.)

## Sources

| Layer | Source | License |
|---|---|---|
| Images | Manchester, John Rylands Library, Pali MS 19 (Dhammapada), Sinhalese-script ola leaf, 70 x 620 mm, leaves 5a-16b of a bundle of eleven Khuddakanikāya texts (Pali MSS 18-28); undated; former owner T. W. Rhys Davids. LUNA IIIF image service, each side published as two halves 2600 px wide (48 JPEGs, 14 MB) | CC BY-NC-SA 4.0 (LUNA record) |
| Pali | SuttaCentral bilara-data root text, Mahāsaṅgīti edition (API `bilarasuttas`), chapter-closing lines and the closing summary left out | CC0 (bilara-data LICENSE.md) |
| English | F. Max Müller, The Dhammapada, Sacred Books of the East X part I (1881), Wikisource "Dhammapada (Muller)" | public domain |

Access note: the LUNA HTML item pages now show a reCAPTCHA check. They were not used. The LUNA search API (which returned
the record ids and catalogue data, saved in `data/sources/dhammapada/ms19/`) and the IIIF image API answer without any
check and were used at a low rate. If the integrator considers this too close to rule 8, the images can be re-sourced
from Manchester Digital Collections once Pali MS 19 is published there (it is not yet; MS 9 and 71 are).

## Mapping method

For every one of the 24 sides I read, on the image at full resolution, the opening words of line 1 and the closing words
of the last line, and located them in the Pali text (`READINGS` in `scripts/import_dhammapada.py`, quoted in each
scan_note). Every side's opening continues the words that close the previous side: all 23 joins were checked, so every
page boundary is a reading. One first reading was wrong and was caught this way (the opening of 11a, first taken for
v.234, is v.222). Sides 5a, 5b, 9a, 12a, 15a and 15b begin with a new verse; the others begin inside a verse, which is
then shown with both sides.

Irregularity found: at the foot of fol. 13b, after v.326, the scribe wrote v.408-412 (Brāhmaṇavagga) out of place, then
a row of 'e'-shaped marks, then the first word of v.327 (appamādaratā). The same verses stand in their place on 16a. The
section notes for 13b/14a and the introductions of chapters 23 and 26 say so.

## English

Wikisource text compared word by word with two OCR texts of separate scans of the 1881 printing (archive.org
`dhammapadacollection01ml`, `thedhammapada00unknuoft`), ignoring footnotes and OCR noise. Three places where both scans
agree against Wikisource were corrected (v.70 "yet is he not", v.98 "(Arahanta)", v.338 "this pain"). The Wikisource
transcription drops the diacritics of the printed book in names (Nirvâṇa, Brâhmaṇa, Mâra); this is stated in the
translator notes. Müller translates some verse pairs together (58-59, 87-88, 104-105, 153-154, 195-196, 229-230, 256-257,
268-269, 271-272); no pair is split across a page.

## Gaps and open questions

- The Pali shown is the Mahāsaṅgīti edition, not a transcription of the manuscript; the scribe's spellings and small
  variants are not recorded.
- The manuscript is undated (the LUNA record gives "[date not identified]"); no colophon date was read.
- Fol. 5a also carries the opening invocation "namo tassa bhagavato arahato sammāsambuddhassa", not reproduced.

## Check

`python3 scripts/check_collection.py dhammapada` -> `dhammapada: 26 entries, 47 sections, 0 hard failures, 0 warnings`
