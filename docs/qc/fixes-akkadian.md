# QC fixes: 13 eBL (Akkadian) collections, 2026-11-12

Engine `scripts/import_gilgamesh.py` changed; all 13 importers re-run. Detail per collection: `docs/collections/<key>.md`, "QC fix round".

**Engine**
1. Witnesses follow eBL's manuscript type. Commentaries, quotations, parallels and lines marked !bs/!cm/!qt/!zz are never used. Catch-lines on library copies are used. School and excerpt tablets serve only where no library copy preserves the line as well, and the note says so.
2. ATF written out in plain form, with a sign key in each entry's notes. eBL defines `&2` as "spans 2 columns", so it renders as a divider.
3. Joined pieces link only the lines eBL documents. Erra 92-116 became 92-94, 95-101 (+K.19050), 102-116.
4. Adapa e+16-e+17 realigned, markers corrected. No other mismatch found.
5. Scan notes list each broken, 1-3-sign or partial line (Atrahasis II 110).
6. Gap reasons are real. Rule 9: eBL photos of other holders fill otherwise empty lines. Yale CC0 photos cover Anzu YBC 9842.

**Per collection** (lines before -> after; sections re-witnessed)
- Gilgamesh 2389 -> 2414; 3. Unplaced pieces unlinked from 9.
- Enuma Elish 999 -> 980; 23
- Atrahasis 185 -> 190; 1
- Erra 134 -> 143; 2
- Anzu 271 -> 352; 9
- Ludlul 459 -> 453; 22 (K.3291 commentary dropped)
- Theodicy 258 -> 258; 2 (K.4267 letter dropped)
- Great Hymn 200 -> 200; 2
- Counsels 157 -> 159; 2
- Cuthaean 175 -> 175; 2 (K.1351 dropped)
- Descent of Ishtar 138, Etana 269, Adapa 73: unchanged
- Total 5707 -> 5804

**Open**
- 36 lines once shown from commentaries or quotations are now gaps. Their other copies have no photograph.
- Atrahasis OB I (290 lines): eBL has no photograph, and the British Museum site returns 403.
- 33 joined-piece sections still link every piece photograph. They need visual mapping.

**Check**: `check_collection.py` reports 0 hard failures for all 13. The one warning (Gilgamesh V §278) predates this round. I looked at the image for every re-witnessed section.

## Round 2 (after docs/qc/review-round2.md)

- **Gilgamesh VII Sm.2132.** The faces were swapped in the note. The upper view holds column iv? (249-261); the lower view holds the line-beginnings of column i (56-68).
- **Gilgamesh X IM.67564.** The ink reads "N.D. 4381", a Nimrud excavation number, and column i runs to 40'.
- **Enuma Elish VI 1.** The ref is now r 2', per eBL's own K.3567 transcription. The note points to the damaged catch-line row on the top edge, not to the colophon.
- **Enuma Elish VII 42-47.** The engine now prints eBL's line-number jumps (3'-5' and 32'-34'). The note says the photo shows one consecutive block.
- **Ludlul IM.67628.** The note gives eBL's 68 obverse and 53 reverse lines and says the photo shows only part of the tablet. The reverse is no longer used, so I 85 and 92 are gaps again (451 lines).
- **Theodicy.** The gap list now reads "109-110, 111-119".
- **Atrahasis UM.55-21-29.** The note now names the reverse view and where the five lines sit.
- **Joined pieces.** K.19835 (Great Hymn) can't be placed and is no longer linked. Without it, K.3182 now carries 7-16, 69-77, 113-160 and 169-182 (41 lines re-witnessed, 15 sections). K.18284 (Counsels) is linked only to column iv; 27-32 moved to K.8282.
- **"Only illegible traces (x) survive"** is now separate from "entirely broken" (Adapa f+10, Counsels A+1 and 54). A script confirms that no "entirely broken" line keeps an x.

`check_collection.py` reports 0 hard failures for all 13 (the Gilgamesh V §278 warning predates this). I checked every changed section on its image (Sm.2132, IM.67564 ink, K.3567 reverse, UM.55-21-29, K.3182, K.8282).

Total lines: 5707 originally, 5804 after round 1, **5802** now.
