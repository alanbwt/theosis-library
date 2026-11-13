# Pyramid Texts of Unas

Key `pyramid-texts-unas`, importer `scripts/import_pyramid_texts_unas.py`, shelf Egypt.

## Contents

17 entries, one per inscribed surface, 231 sections (one per TLA text = one utterance, or one copy of an utterance), 227 different utterance numbers. Every column W 1-649 (Sethe's numbering has no W 129 or W 318) is covered except PT 271 (end of W 492, W 493, top of W 494; see gaps); W 646 has no column mark in the TLA text and its words stand under W 645.

| Entry (`verified-pyramid-texts-unas-…`) | Columns (Sethe W) | Sections | Photograph |
|---|---|---|---|
| `sarcophagus-north-wall-register-1` | 1-55 | 28 (PT 23-57, PT 32 twice) | `sarc-north-register-1.jpg` |
| `sarcophagus-north-wall-register-2` | 56-109 + 61+1 | 35 (PT 72-116 with PT 25, 32) | `sarc-north-register-2.jpg` |
| `sarcophagus-north-wall-register-3` | 110-165 (no 129) | 55 (PT 117-171) | `sarc-north-register-3.jpg` |
| `sarcophagus-east-gable` | 166-205 | 7 (PT 204-212) | `sarc-east-gable.jpg` |
| `sarcophagus-south-wall` | 206-261 | 7 (PT 213-219; 219 runs on to the east wall) | `sarc-south-wall.jpg` (+ east wall for 219) |
| `sarcophagus-east-wall` | 262-299 | 5 (PT 220-224) | `sarc-east-wall.jpg` |
| `sarcophagus-west-gable` | 300-340 (no 318) | 18 (PT 226-243) | `sarc-west-gable.jpg` |
| `passage-north-wall` | 341-359 | 5 (PT 199, 32, 23, 25, 200) | `passage-north-wall.jpg` |
| `passage-south-wall` | 360-378 | 3 (PT 244-246) | `passage-south-wall.jpg` |
| `antechamber-west-gable` | 379-415 | 7 (PT 247-253) | `ante-west-gable.jpg` |
| `antechamber-west-wall` | 416-452 | 5 (PT 254-258) | `ante-west-wall.jpg` |
| `antechamber-south-wall` | 453-495 | 9 (PT 260-272, without 271) | `ante-south-wall.jpg` (+ west wall for 260) |
| `antechamber-east-gable` | 496-531 | 3 (PT 273+274, 275, 276) | `ante-east-gable.jpg` |
| `antechamber-east-wall` | 532-566 + 544+1 | 24 (PT 277-301) | `ante-east-wall.jpg` |
| `antechamber-north-wall` | 567-609 | 11 (PT 302-312) | `ante-north-wall.jpg` |
| `corridor-west-wall` | 610-629 | 5 (PT 313-317) | `corridor-west-wall.jpg` |
| `corridor-east-wall` | 630-649 | 4 (PT 318-321) | `corridor-east-wall.jpg` |

## Sources

- **Object**: the burial apartments of the pyramid of Unas, Saqqara, in situ (end of the 5th Dynasty, c. 2350 BCE).
- **Photographs**: the wall montages on Pyramid Texts Online (Vincent Brown, pyramidtextsonline.com, pages `*h.html`), made from the black and white photographs taken by L. F. Husson under the direction of Natacha Rambova for A. Piankoff, *The Pyramid of Unas* (Bollingen Series XL.5, 1968), as credited on the site's contact page. No terms stated; used with credit under rule 9. The bytes are kept as published (no re-encoding). The gable montages carry a small caption in the black background added by Pyramid Texts Online.
- **Egyptian**: Thesaurus Linguae Aegyptiae, Pyramid Texts of Unas, ed. Doris Topmann, TLA extract of January 2018 (urn:nbn:de:kobv:b4-opus4-29190), AED-TEI commit 462c722e, CC BY-SA 4.0. Transliteration only: the TLA has Unicode hieroglyphs for only 529 of 11,035 words of these texts, so none are shown.
  - Finding: the earlier Egypt pass saw only 144 Unas texts because `concordance_name_text_id.csv` in the AED-TEI repository is incomplete. The `files/` folder holds 230 texts dated "Unas" at Saqqara plus PT 219 (undated), found by their TEI headers. The Hugging Face TLA set (`tla-Earlier_Egyptian_original-v18-premium`) is a filtered sentence set without text ids and cannot rebuild whole texts; Zenodo has no fuller TLA corpus release.
- **English**: S. A. B. Mercer, *The Pyramid Texts in Translation and Commentary* vol. 1 (Longmans, Green, 1952), sacred-texts.com transcription. sacred-texts.com blocks automated access (Cloudflare), so the 2019 Wayback Machine captures were used (`data/sources/pyramid-texts-unas/mercer/cdx.txt`). Public domain in the US (no renewal on record, per the earlier pass; the Stanford renewal database could not be queried because it answers with a bot check).

## Mapping method

1. Column numbers and wall of every utterance from the TLA text (Sethe's Unas W numbering in the `<lb>` markers, wall in `msName`), cross-checked against the wall lists on Pyramid Texts Online (all utterances agree; PTO also lists 206 and 208, which are Sethe's numbers for duplicates of 205 and 207, not separate Unas texts).
2. On every photograph the columns were counted by eye on zoomed bands with a pixel ruler (an automatic divider fit was used only as a first guide; it drifts on the montages and was not trusted), and the count compared with the column numbers of that wall. All 17 counts agree with the TLA numbering, including the numbering gaps W 129 and W 318 (no column on the wall), the extra columns 61+1 and 544+1, and W 493 (PT 271).
3. The edge where the text starts was fixed by content: cartouche patterns (which columns have the Unas cartouche and where), distinctive signs (three ankhs ending W 206, repeated "m Jtm" in W 207, stars of Sꜣḥ/Spd,t/dwꜣ,t in W 221, three ibises in W 298, goose and bull of "j Gbb kꜣ Nw,t" in W 452, stars in W 496, four cartouches in W 616) and the offering-count strokes at the column feet of register 3. The checks for each wall are in that entry's `scan_mapping` and in every section's `scan_note`.
4. Each section's note gives its columns as positions counted from the start edge of the photograph (e.g. "W 206-208 are columns 1-3 of the 56 columns ... counted from the right-hand (west) edge").
5. English: Mercer's utterance of the same number. Mercer's separate headings ("Heading to Utterances 72-78" etc.), postscripts and variants from other pyramids are left out; "Utterances 79-80" line 54d is attached to PT 79 because the Unas text of PT 79 contains it (TLA German: "Grüne Schminke, schwarze Augenschminke, je ein Beutel"). Formatting slips in the sacred-texts HTML are handled explicitly (96, 116, 273-274, 299, 306).

## Known gaps and caveats

- **PT 271** (end of W 492, W 493, top of W 494, antechamber south wall) is not in the 2018 TLA extract, so it is not published. Mercer's English exists; an open transliteration is needed.
- W 610 (start of PT 313, corridor west wall) is broken away on the photograph; the TLA restores most of it in brackets.
- The TLA has no line break for W 646 (PT 320); its words stand under 645.
- Mercer translates Sethe's composite text from all pyramids, so some English clauses are not in the Unas copy; said in every scan note and in the introductions. The three copies of PT 25 and four of PT 32 get the same English.
- Mercer's text uses the sacred-texts characters (ȝ for aleph, ‘ for ayin); underlined letters were converted to ḏ ṯ ẖ. Misprinted section numbers of that transcription are kept (e.g. "146." for 141b, "43m" for 431a).
- The passage and corridor photographs are small (about 830-890 px wide); no larger version was found.

## Open questions

- Per-utterance crops were not made; each section points at the whole wall and names its columns. Column positions were counted by eye; the start and end of every wall and several interior anchors were checked, not every single column.

## QC fixes (2026-11-12)
The shared introduction of all 17 entries said 'this library gives every column'. It now says that Sethe's numbering runs W 1-649 without W 129 and W 318, that PT 271 (end of W 492, W 493, top of W 494) is missing because it is not in the TLA data used, and that the words of W 646 are given under W 645 because the TLA text has no column mark for it. The 139 checker warnings (one image per wall or register) are unchanged. Still open from the review: the US renewal check for Mercer 1952 (spec rule 6). Review: docs/qc/review-near-east.md.
