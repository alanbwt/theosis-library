# Papyrus Prisse (Kagemni and Ptahhotep)

Key `papyrus-prisse`, importer `scripts/import_papyrus_prisse.py`, shelf Egypt.

## Contents

| Entry | Sections | Papyrus pages | Photographs |
|---|---|---|---|
| `verified-papyrus-prisse-kagemni`: Instruction for Kagemni (end) | 7 (Gunn 1-5, closing narrative, colophon) | 1-2 | `kagemni-p01.jpg`, `kagemni-p02.jpg` (frame 183 cut at the column gap) |
| `verified-papyrus-prisse-ptahhotep`: Instruction of Ptahhotep (complete) | 48 (Gunn A, B, 1-37, C, 38-43, D, colophon) | 4-19 | `ptahhotep-p04.jpg` ... `ptahhotep-p19.jpg`, one per column |

Both texts are complete as far as the papyrus goes. The beginning of Kagemni is lost (the roll starts with its end); pages 3 and the frames 184-185 hold an erased text that has no edition and is not included.

## Sources

- **Object**: Paris, BnF, Département des Manuscrits, Égyptien 183-194 (Papyrus Prisse), 12th Dynasty, c. 1850 BCE, from Thebes. Catalogue: https://archivesetmanuscrits.bnf.fr/ark:/12148/cc12921q
- **Photographs**: Wikimedia Commons, Category:Prisse Papyrus, photographs by the user Zunkir (own work at the BnF exhibition "L'aventure Champollion", 2022), CC BY-SA 4.0. One photograph per column for frames 186 and 189-194 ("right part" = first column), one each for 187 and 188, one for 183 (cropped into two pages).
- **Egyptian**: Thesaurus Linguae Aegyptiae, edition by Peter Dils (after Jéquier 1911), TLA database extract January 2018 (urn:nbn:de:kobv:b4-opus4-29190) in the TEI conversion AED-TEI by S. D. Schweitzer (texts DKAFDVSXYFADJDS3Z3AOISAP4U, KI7QRD7K55C6PJRUN5AFW6OFLI), CC BY-SA 4.0. Transliteration with page,line numbers; Unicode hieroglyphs (TLA transcription of the hieratic) as `edition_text` for Ptahhotep (3,020 of 3,060 words encoded; the others are shown in italic transliteration). Kagemni has no hieroglyphic encoding in the TLA.
- **English**: Battiscombe G. Gunn, *The Instruction of Ptah-hotep and the Instruction of Ke'gemni* (Wisdom of the East, John Murray, 1906), Project Gutenberg #30508. Public domain. Footnote markers and page numbers removed.

## Mapping method

1. Frame to column: BnF catalogue (183: two columns of 12 and 9 lines; 186: end of erased part and two columns; 187: one column of 11 lines; 188: one column of 12 lines; 189-194: two columns each). With the TLA page numbering this fixes page 4-5 = 186, 6 = 187, 7 = 188, 8-9 = 189, ... 18-19 = 194. TLA line counts per page agree (page 6: 11 lines, page 7: 12 lines).
2. Every photograph was opened and checked: line counts and the positions of the red rubrics against the TLA lines where a maxim opens (e.g. page 7: rubrics on lines 3, 5, 7, 9, 10 = maxim openings at 7,3, 7,5, 7,7, 7,9, 7,10; page 15: rubrics on lines 2, 5, 6, 8). The check for each page is written in the section `scan_note`.
3. English to Egyptian: each Gunn section was matched to a run of TLA sentences by reading Gunn against the TLA German sentence translations (table `PTAH_SECTIONS` / `KAG_SECTIONS` in the importer, with anchor assertions on the opening words). Sections that cross a column break list both photographs.

## Known gaps and caveats

- Maxim 32 (Gunn §32): Gunn printed only the heading "[Concerning continence]" and did not translate it. The Egyptian is given; the English is only Gunn's heading, flagged in the scan note and translator notes.
- Gunn (1906) is an early translation; some passages are now read differently, and he marks doubtful places with (?) and untranslated phrases with dots.
- The TLA edition opens with two lacuna marks before line 4,1; they are kept.
- The TLA text skips a few line numbers (e.g. 18,3-18,4 fall inside one sentence); line numbers are shown exactly as the TLA gives them.

## Open questions

- None on mapping. A later TLA release (v19+) may revise the transliteration; the 2018 AED-TEI data were used because they are the openly published raw data (the TLA website itself is behind a bot check).
