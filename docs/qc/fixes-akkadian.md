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
