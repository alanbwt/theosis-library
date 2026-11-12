# Daodejing (Mawangdui silk manuscripts)

Key `daodejing`, prefix `verified-daodejing-`, shelf China, importer `scripts/import_daodejing.py`.

## Contents

81 entries, one per chapter in received order (`verified-daodejing-01` to `-81`), 162 sections:
every chapter has a section for each of the two Mawangdui silk manuscripts.

- **Mawangdui A** (Laozi A, 甲本): 169 columns, script between seal and clerical, does not avoid
  the name 邦; commonly dated before 195 BCE.
- **Mawangdui B** (Laozi B, 乙本): 78 columns, clerical script, avoids 邦; commonly dated 194-180 BCE.
  Each column was photographed in two halves (上/下) on facing plates.

Both come from Tomb 3 at Mawangdui, Changsha (sealed 168 BCE). They are the oldest nearly complete
copies of the work. Guodian (c. 300 BCE) is older but holds only about a third of the text and has
no openly licensed photographs.

## Sources

| Layer | Source | Licence |
|---|---|---|
| Photographs | Plates of *Changsha Mawangdui Han mu jianbo jicheng* vol. 1 (Zhonghua Shuju 2014): Laozi A pp. 95-102, Laozi B pp. 142-149, from the two Wikimedia Commons PDFs (see importer). JPEGs extracted unchanged (902 x 1360 px). | Public domain on Commons |
| Silk transcription | Wikisource (zh) Page transcriptions of those PDFs, transcluded as 老子 (帛書甲本) / 老子 (帛書乙本); column numbers follow the Jicheng. Revision ids in `data/sources/daodejing/wikisource-revisions.json`. | CC BY-SA 4.0 |
| Received text (edition_text) | Wang Bi recension (Huating Zhang edition), Wikisource 道德經 (王弼本), main text only | PD text, CC BY-SA transcription |
| English | James Legge, *The Tao Teh King*, SBE 39 (1891), Project Gutenberg #216 | Public domain |

## Mapping method

1. Chapter to columns: the `{{transclude pages}}` templates of the two Wikisource chapter pages
   (every Page section is used exactly once; asserted by the importer).
2. Column to plate: the Wikisource Page number, which matches the plate. Three Laozi A columns at
   plate edges are on a different plate than the Wikisource split says; found on the images and
   corrected in `PLATE_OVERRIDE_A`: col. 22 is on p. 96, col. 108 on p. 100, col. 130 on p. 101.
   Laozi B plate boundaries (16/17, 40/41, 64/65) were checked and match.
3. Visual check: each plate was viewed in magnified strips and every chapter's opening (or, where
   the opening is lost or unreadable, the first readable characters) was found in the stated column.
   All 162 readings are logged in `data/sources/daodejing/visual-checks.tsv` and quoted in each
   section's scan_note.

## Gaps and uncertainties

- Image resolution: the Commons PDFs carry 902 x 1360 px plates, below the 1600 px target. No
  higher-resolution open images were found. They are used unscaled.
- Two Laozi B sections (chapter 43, columns 7上/下; chapter 79, column 43) could not be read at this
  resolution. Their position rests on the Jicheng column numbers plus checked neighbouring
  boundaries (chapter 42 and 44 openings; chapter 78 end and chapter 1). The scan_notes say this.
- For 33 Laozi A and 13 Laozi B chapters the opening is lost or not readable on the image; the
  scan_note gives the first characters that were confirmed.
- Many chapters are partly lost on one witness (□ in the transcription). Every chapter has
  readable text on at least one witness, and in nearly all cases on both.
- The Wikisource Page transcriptions are marked "not proofread" on Wikisource. Spot readings on the
  plates agreed with them; they were not proofread character by character.
- Legge translated the received text. The English therefore matches the edition_text (Wang Bi), not
  the silk wording. The intro and each scan_note say this; main systematic variants (恆/常, 也,
  loan characters, chapter order 24-22-23, 41-40, 66-80-81-67) are noted in the introduction and
  the per-chapter order notes.
- B's tail titles (《德》三千𠦜一 after ch. 79, 《道》二千四百廿六 after ch. 37) are mentioned in the
  scan_notes but left out of the chapter text.
- Not built: Dunhuang Daodejing manuscripts (Gallica and IDP block automated access from here);
  Guodian (no open photographs).
