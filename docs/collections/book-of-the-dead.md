# Book of the Dead (papyrus of Iuefankh, Turin)

Key `book-of-the-dead`, importer `scripts/import_book_of_the_dead.py`, shelf Egypt.

## Contents

159 entries, one per spell (`verified-book-of-the-dead-spell-NNN`), 163 sections. Every spell of the roll with text is
built except 20, 111 and 121 (see gaps). Spell 125 has five sections, following the TLA: 125A (title, address to the god,
first declaration of innocence), 125B (the 42 declarations to the judges), 125C (address to the gods of the hall and the
questioning at the door), 125D (rubric), 125V (captions of the judgment vignette). Spells that the TLA splits into parts
with continuous column numbers (15 a-i, 101, 110 with its vignette captions, 145, 146, 149) are one section each, because
Birch's English is not divided at the same points.

Priority spells: 1, 17, 30, 64, 110 (with the Field of Offerings vignette), 125 (all parts and the vignette) are built.
175 is not in this papyrus (Turin 1791 ends with 165).

| Photograph (scan file `turin1791-photo-NN.jpg`) | Commons file `..._C_1791_pNN.jpg` | Spells |
|---|---|---|
| 1 | p034 | 1-7 |
| 2 | p033 | 7-15 |
| 3 | p032 | 15-17 (16 is a vignette only) |
| 4 | p031 | 17 |
| 5 | p030 | 17-19 |
| 6 | p029 | 19-31 (20 not published) |
| 7 | p028 | 30-40 |
| 8 | p027 | 40-51 |
| 9 | p026 | 50-64 |
| 10 | p025 | 64-71 |
| 11 | p024 | 71-78 |
| 12 | p023 | 78-85 |
| 13 | p022 | 85-93 |
| 14 | p021 | 93-99 |
| 15 | p020 | 99-109 |
| 16 | p019 | 109-110 (Field of Offerings vignette) |
| 17 | p018 | 110-120 (111 not published) |
| 18 | p017 | 119-125B (121 not published) |
| 19 | p016 | 125B-125V |
| 20 | p015 | 125V-128 |
| 21 | p014 | 128-133 |
| 22 | p013 | 133-140 |
| 23 | p012 | 140-144 (143 is a vignette only) |
| 24 | p011 | 144-145 |
| 25 | p010 | 145-146 |
| 26 | p09 | 145-147 |
| 27 | p08 | 147-149 |
| 28 | p07 | 149 (150 is a vignette only) |
| 29 | p06 | 151-160 |
| 30 | p05 | 160-164 |
| 31 | p04 | 164-165 |
| detail | p02 | judgment vignette of 125 (`turin1791-spell125-vignette-detail.jpg`, section 125V) |

## Sources

- **Object**: Turin, Museo Egizio, Cat. 1791, the Book of the Dead of Iuefankh, Ptolemaic period (TLA: 332-31 BCE), from
  Thebes. Published by R. Lepsius, *Das Todtenbuch der Aegypter nach dem hieroglyphischen Papyrus in Turin* (1842), 79
  plates; Lepsius's 165 chapter numbers are the standard spell numbers. Plates read on the BSB/MDZ scan (bsb10801356).
- **Photographs**: Museo Egizio, CC0, on Wikimedia Commons (Category: Book of the Dead of Iuefankh - Museo Egizio
  (Turin) C. 1791). The 31 files p04-p034 (6048 x 4032) run from the end of the roll (p04) to its beginning (p034); the
  stitched strip p03 of the same series confirms the order. The "papyurs" series on Commons is the same 31 photographs
  under other numbers (matched by image comparison) and is not used. Scans are resized to 2600 px wide, no cropping.
- **Egyptian**: Thesaurus Linguae Aegyptiae, Totenbuch, pTurin 1791, ed. Burkhard Backes, TLA extract of January 2018,
  AED-TEI commit 462c722e, CC BY-SA 4.0: 182 texts. Transliteration only (the hieroglyph files of these texts are empty).
  The TLA's German position labels (Titelzeile, n. Tor, Beischrift zu ...) are translated in the line labels.
- **English**: Samuel Birch, "The Funereal Ritual or Book of the Dead", in Bunsen, *Egypt's Place in Universal History*
  vol. V (1867), public domain. Birch translated Lepsius's edition of this same papyrus (his note 60), so English and
  Egyptian come from one manuscript. Text from three Internet Archive OCRs (bub_gb_fCSiSJ7OxSIC = base,
  egyptsplaceinun00cottgoog, india.history.resource.41142), cleaned of running heads, signatures and footnotes, aligned
  word by word and settled by agreement (a word of the base text is replaced only when both other scans agree on a similar,
  more frequent reading). A short table of OCR fixes (`FIXES`, `PHRASE_FIXES`) is in the importer. Birch's numbers equal
  Lepsius's up to 144; his CXLV is the rubric of 144, so his CXLVI-CLXVI are Lepsius 145-165. Every pairing was checked
  against the first sentences of the TLA German translations.

## Mapping method

1. Spell order, plate numbers and column numbers from Lepsius 1842 (plate headers carry chapter numbers; the TLA uses the
   same chapter and column numbers).
2. Each of the 31 photographs was compared by eye with Lepsius's plates (top band with titles and vignettes, at 2000 px):
   distinctive vignettes and red titles fix which spells are on it and where (positions measured from the left edge).
   These anchors are in `PHOTOS` in the importer and are quoted in every scan note.
3. Spells between two identified spells on the same photograph are on that photograph (the roll is continuous); the note
   says so.
4. Neighbouring photographs overlap. The overlaps were checked side by side for 13 boundaries (1/2, 4/5, 5/6, 13/14,
   14/15, 17/18, 20/21, 21/22, 22/23, 26/27, 27/28, 29/30, 30/31); a spell that crosses an edge lists both photographs.
   One misidentification was caught this way and corrected (the shrine-and-man vignette at the right edge of photograph
   18 is Spell 119, not 121).

## Known gaps and caveats

- **Not published**: Spell 20 (Birch summarises the table of the fourteen tribunals and translates only the rubric),
  Spell 111 (Birch: "a repetition of Chapter CVIII"), Spell 121 (Birch: "Same as Chapter XIII"). The TLA text and the
  photographs are ready; an open English is needed. Spells 16, 143 and 150 are vignettes without text.
- **Spell 175** (Osiris and Atum on the end of the world) is not in Turin 1791. The TLA has it from the papyrus of Kha
  (Turin S. 8438, 65 columns, text PHHTCP56KNFFXCKMBRE6SCOCGU) and Commons has CC0 Museo Egizio photographs of that roll
  (Category: Book of the Dead of Kha - Museo Egizio (Turin) S. 08316.3, 8438, 32 photos + strip). Not built: the columns
  of 175 still have to be located on those photographs by reading, and the only open English is Budge's (1898/1901),
  translated from the papyrus of Ani, which would have to be extracted from a single noisy OCR.
- **Other papyri**: pNu (BM EA 10477, 136 TLA texts incl. 1, 17, 30B, 64, 125) has no open photographs reachable without
  the British Museum website (Commons has none). Yuya (Cairo CG 51189, 38 texts) has only some visitor photographs of parts of
  the roll on Commons, Maiherperi (CG 24095, 27 texts) and BM 10793 (75 texts) no open photo series that was found. Turin 1791 is the only witness
  with complete text, translation from the same manuscript and complete photographs.
- **Birch's English** is the first complete English version (1867) and is out of date in many readings; it uses Hades,
  Aahlu, Tum, Seb, Anup. OCR errors remain, chiefly in proper names; some punctuation follows the scans. In Spell 104 Birch
  prints a variant from Pap. BM 9900 beside the Turin text; both are given as he printed them.
- In Spell 125, section V gives Birch's English of the vignette captions in his order, which differs from the TLA's.
- Each photograph shows a long stretch of the roll; at 2600 px the hieroglyphs are legible but small. Positions in the
  notes are measured on the published photographs.

## Open questions

- Plate L (the large judgment vignette) has a header without a readable chapter number on the scan; it is assigned to 125
  because L lies between XLIX (125) and LI (126-128).
- Plate LIX's header shows "143." at its edge (the scan is cut); TLA and Birch put the names-of-Osiris table there as 142.
