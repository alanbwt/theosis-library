# Rosetta Stone (Greek text)

Key `rosetta-stone`, importer `scripts/import_rosetta_stone.py`, shelf Egypt.

## Contents

| Entry | Sections | Lines | Photographs |
|---|---|---|---|
| `verified-rosetta-stone-greek-decree` | 9 (lines 1-6, 7-12, ... 49-54) | Greek 1-54, complete | `greek-lines-NN-NN.jpg` (one per section), `greek-register.jpg` (all sections), `rosetta-stone-hillewaert.jpg` (overview) |

Complete Greek text. The hieroglyphic and Demotic versions are not included: no openly licensed digital text of either was found.

## Sources

- **Object**: British Museum EA 24, decree of the synod at Memphis, 27 March 196 BCE.
- **Photographs**: the British Museum's own photograph in Budge, *The Rosetta Stone* (BM, 1922; photo Donald Macbeth), Wikimedia Commons `File:The_Rosetta_Stone.jpg`, 4911 x 6000, public domain. Overview: Hans Hillewaert, `File:Rosetta_Stone.JPG`, CC BY-SA 4.0. (Five CC0 close-ups by Gary Todd on Commons were looked at; each shows only part of the register, so they were not used.)
- **Greek**: E. A. Wallis Budge, *The Decrees of Memphis and Canopus* vol. 2 (1904), pp. 101-123, "Transcript", printed line by line with the stone's numbering. Public domain. **Typed from the page images** (archive.org `decreesofmemphis02budg`, pages saved in `data/sources/rosetta-stone/budge1904/`) and proofread word by word against the printed page; then compared letter by letter with the open-greek-corpus FHG OCR (Müller/Letronne 1841, `data/sources/rosetta-stone/ogc_marmor_rosettanum.jsonl`) and every difference rechecked on Budge's page. Remaining differences are Budge's (misprints such as ὑπὰ l. 10, ἐτάσσοντα l. 16, ἀποκατέστηοεν l. 18, καταπορευομένος l. 19, ἀγδόου l. 29; different restorations in ll. 36, 40, 41, 43, 52-53) and are kept as printed. Data file `data/sources/rosetta-stone/transcribed/budge1904_greek.txt`.
- **English**: Budge's "English Rendering" (same volume, pp. 100-122), numbered by the same Greek lines. Typed from the page images, checked word by word against the archive.org OCR (only OCR errors differed). Data file `.../budge1904_english.txt`.
- Not used: OGIS 90 (Dittenberger) was not needed because Budge prints a line-numbered text; Greek Wikisource has an unsourced uppercase transcription with errors; PHI has no license.

## Mapping method

1. Line numbers come from Budge (stone numbering).
2. On the 1922 photograph (turned -0.4 degrees) the vertical position of all 54 lines was read by eye on calibrated strips at x 550, 1700 and 3900 (and x 3075 for lines 46-54, whose right ends are broken). The lines bow by up to about 45 px, so an automatic line tracker failed (it slipped a line in the lower left) and was not used.
3. Each six-line image is cut along those positions and straightened by shifting pixel columns up or down (at most 61 px, nothing else changed). It shows the left half of the lines above and the right half below, with 300 px overlap. Said in every scan note. The unstraightened whole register is the second image of every section.
4. Every group image was opened and its first and last lines checked letter by letter at both ends (recorded in `GROUP_CHECKS` and the scan notes).

## Known gaps and caveats

- The ends of lines 28-54 are broken off. The Greek shows Budge's restorations in square brackets, and his English translates them.
- Budge's English is a 1904 rendering: "Under the reign of the young [god]" and so on. Words in square brackets are his additions.
- Era is set to "Ancient Near East" to match the other Egypt collections; "Hellenistic" would also fit (196 BCE).
