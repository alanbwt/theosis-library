# Epic of Gilgamesh (key `gilgamesh`)

Built by `scripts/import_gilgamesh.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence). Rebuilt 2026-11-12 after the independent QC review (`docs/qc/review-near-east.md`); the changes are summarised below and in `docs/qc/fixes-akkadian.md`.

## Contents (13 entries, 177 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Epic of Gilgamesh, Tablet I: Gilgamesh and the creation of Enkidu | 300 | 300 | 231 | 15 | 6 |
| Epic of Gilgamesh, Tablet II: Enkidu comes to Uruk | 187 | 186 | 118 | 13 | 6 |
| Epic of Gilgamesh, Tablet III: preparations for the journey | 209 | 208 | 164 | 15 | 8 |
| Epic of Gilgamesh, Tablet IV: the journey to the Forest of Cedar | 175 | 121 | 81 | 9 | 7 |
| Epic of Gilgamesh, Tablet V: the killing of Humbaba | 274 | 260 | 121 | 11 | 5 |
| Epic of Gilgamesh, Tablet VI: Ishtar and the Bull of Heaven | 183 | 183 | 182 | 14 | 7 |
| Epic of Gilgamesh, Tablet VII: the death of Enkidu | 219 | 216 | 202 | 20 | 14 |
| Epic of Gilgamesh, Tablet VIII: the funeral of Enkidu | 206 | 205 | 197 | 15 | 8 |
| Epic of Gilgamesh, Tablet IX: Gilgamesh's wandering | 137 | 135 | 135 | 7 | 2 |
| Epic of Gilgamesh, Tablet X: Shiduri, Ur-shanabi and Uta-napishti | 325 | 306 | 301 | 12 | 4 |
| Epic of Gilgamesh, Tablet XI: the Flood | 329 | 329 | 329 | 19 | 5 |
| Epic of Gilgamesh, Tablet XII: Enkidu and the Netherworld | 139 | 135 | 135 | 15 | 7 |
| Epic of Gilgamesh, Old Babylonian version: the Yale tablet (Gilgamesh and Enkidu plan the journey to the Forest of Cedar) | 219 | 218 | 218 | 12 | 1 |

Total: 2414 of the 2902 lines in the eBL edition (83%); 2414 of the 2802 lines that survive on any manuscript. (Before the QC fix round: 2389 lines in 176 sections.)

## Sources

- Original: eBL corpus edition L I.4, Poem of Gilgamesh (ed. A. R. George, rev. G. Rozzi and E. Jiménez), manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0. eBL's layout codes are written out in words and each entry's notes carry a key to the signs used.
- English: A. R. George (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; each section's scan_note names the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, so the reader knows which English is not on that tablet.
- Photographs (terms as recorded in scan_license):
  - (c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)
  - Photograph by A. A. Fadhil and N. Jabbar (Iraq Museum - eBL Project), displayed by eBL by permission of the State Board of Antiquities and Heritage and The Iraq Museum; eBL: 'The images cannot be reproduced without the explicit consent of the funding projects and institutions, as well as the institutions in which the cuneiform tablets are kept.' Used with credit under the library's photo rule (non-commercial).
  - CC0 1.0 (IIIF manifest 'rights'; Yale Peabody Museum open access, http://hdl.handle.net/10079/8931zqj)

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. Only copies of the work are witnesses: eBL's manuscript type decides (commentaries, quotations in other texts and parallel texts are never used, nor any line written with commentary or quotation markup; catch-lines on library copies are used; school, excerpt, amulet and 'Varia' tablets only where no photographed library copy preserves the line as well). Photographs of holders other than the British Museum that eBL serves are used under spec rule 9 only for lines no British Museum photograph carries. For each line the importer takes the usable witness with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at; the result is recorded per tablet in `CHECKS` in the importer and repeated in each section's scan_note.

Joins that the British Museum photographed in pieces: a section links only the pieces that carry its lines when eBL documents that (the piece's own transliteration, its parallel-line references, notes naming the piece); otherwise all piece photographs are linked and the section says that eBL does not say which piece carries which line.

## Gaps (and why)

Each entry's introduction and `verification.lines_not_published` give, for every line not shown, the manuscripts that carry it and why each cannot be used (no photograph in eBL, not in the eBL Fragmentarium, commentary, quotation in another text, photograph does not show the lines).

- Epic of Gilgamesh, Tablet I: Gilgamesh and the creation of Enkidu: 19-47: no photograph in eBL: IM.67577 (Iraq Museum); photograph does not show these lines (visual check): BM.34916; 48-51: no photograph in eBL: IM.67577 (Iraq Museum); photograph does not show these lines (visual check): K.913, BM.34916; 52: no photograph in eBL: IM.67577 (Iraq Museum); photograph does not show these lines (visual check): BM.34916; 82: no photograph in eBL: VAT.17234 (Vorderasiatisches Museum, Berlin); photograph does not show these lines (visual check): BM.34916; 86: no photograph in eBL: VAT.17234 (Vorderasiatisches Museum, Berlin); photograph does not show these lines (visual check): BM.34916; 145-154: no photograph in eBL: K.2756.A; 208a-208b: not in the eBL Fragmentarium (no photograph there): IM.76973; 247-248: photograph does not show these lines (visual check): K.913; 265-271: photograph does not show these lines (visual check): K.913, BM.34916; 272: photograph does not show these lines (visual check): BM.34916; 273-279: photograph does not show these lines (visual check): K.913, BM.34916; 280: photograph does not show these lines (visual check): BM.34916; 281-283: photograph does not show these lines (visual check): K.913, BM.34916
- Epic of Gilgamesh, Tablet II: Enkidu comes to Uruk: 26-36: no photograph in eBL: IM.76941 (Iraq Museum); 37-41: no photograph in eBL: ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago), IM.76941 (Iraq Museum); 56-58: photograph does not show these lines (visual check): BM.34964; a+1'-a+4': no photograph in eBL: ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago); 212-217: no photograph in eBL: IM.76854 (Iraq Museum); 218b-220: no photograph in eBL: IM.76854 (Iraq Museum); 225-226: no photograph in eBL: IM.76854 (Iraq Museum); photograph does not show these lines (visual check): BM.34964; 231: no photograph in eBL: ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago); 243: no photograph in eBL: IM.76854 (Iraq Museum); 247-268: no photograph in eBL: IM.76941 (Iraq Museum); 269-272: no photograph in eBL: IM.76941 (Iraq Museum), IM.76854 (Iraq Museum); 281-285: no photograph in eBL: IM.76854 (Iraq Museum); 286: no photograph in eBL: ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago), IM.76854 (Iraq Museum); 294: no photograph in eBL: IM.76854 (Iraq Museum); 297: no photograph in eBL: ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago), IM.76854 (Iraq Museum); 300: no photograph in eBL: BM.72719, ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago), IM.76854 (Iraq Museum); 301-302: no photograph in eBL: ISACM-A.3444 (Institute for the Study of Ancient Cultures, Chicago), IM.76854 (Iraq Museum); 322: no manuscript preserves it
- Epic of Gilgamesh, Tablet III: preparations for the journey: 23: no photograph in eBL: BM.34191; 29-30: no photograph in eBL: BM.34191; 59: no photograph in eBL: IM.76873 (Iraq Museum); 85: no photograph in eBL: VAT.19286 (Vorderasiatisches Museum, Berlin), IM.76873 (Iraq Museum); 109-116: no photograph in eBL: IM.76873 (Iraq Museum); 122a: no photograph in eBL: IM.76873 (Iraq Museum); 133-136: no photograph in eBL: IM.76873 (Iraq Museum); 164-165: no photograph in eBL: K.8573; 166-173: no photograph in eBL: K.8573, BM.34191; 207-222: no photograph in eBL: BM.34191; 244: no manuscript preserves it
- Epic of Gilgamesh, Tablet IV: the journey to the Forest of Cedar: 1-5: no photograph in eBL: VAT.14512 (Vorderasiatisches Museum, Berlin); 6-21: no manuscript preserves it; 44-55: no manuscript preserves it; 69-75: no photograph in eBL: BM.93052; 78-83: no manuscript preserves it; a+1'-a+9': no photograph in eBL: BM.93052; 130-142: no manuscript preserves it; 155-157: no photograph in eBL: VAT.14513 (Vorderasiatisches Museum, Berlin); 158: no photograph in eBL: VAT.14513 (Vorderasiatisches Museum, Berlin); not in the eBL Fragmentarium (no photograph there): Private.1; 165: no photograph in eBL: VAT.14513 (Vorderasiatisches Museum, Berlin); not in the eBL Fragmentarium (no photograph there): Private.1; 166-176: no photograph in eBL: VAT.14513 (Vorderasiatisches Museum, Berlin); 177-183: no manuscript preserves it; c+1': no photograph in eBL: VAT.14512 (Vorderasiatisches Museum, Berlin); c+2': not in the eBL Fragmentarium (no photograph there): Private.1; d+1': no photograph in eBL: VAT.14512 (Vorderasiatisches Museum, Berlin)
- Epic of Gilgamesh, Tablet V: the killing of Humbaba: 20-27: not in the eBL Fragmentarium (no photograph there): T.1447; 85-90: not in the eBL Fragmentarium (no photograph there): T.1447; 115-135: no photograph in eBL: IM.76985 (Iraq Museum); 143-151: no manuscript preserves it; 152-183: no photograph in eBL: IM.76985 (Iraq Museum); 184-187: no manuscript preserves it; 190-194: no photograph in eBL: IM.76985 (Iraq Museum); 199: no photograph in eBL: IM.76985 (Iraq Museum); 202-204: no photograph in eBL: IM.76985 (Iraq Museum); 207: no manuscript preserves it; 247-252: not in the eBL Fragmentarium (no photograph there): T.1447; 253-267: no photograph in eBL: IM.76985 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): T.1447; 268: not in the eBL Fragmentarium (no photograph there): T.1447; 269-270: no photograph in eBL: IM.76985 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): T.1447; 271-272: no photograph in eBL: IM.76985 (Iraq Museum); 273: no photograph in eBL: IM.76985 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): T.1447; 274-276: not in the eBL Fragmentarium (no photograph there): T.1447; 284-285: no photograph in eBL: IM.76985 (Iraq Museum); 286: no photograph in eBL: IM.76985 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): T.1447; 287-298: no photograph in eBL: IM.76985 (Iraq Museum); 299-309a: not in the eBL Fragmentarium (no photograph there): T.1447; 309b: no photograph in eBL: IM.76985 (Iraq Museum); 310-317: no photograph in eBL: IM.76985 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): T.1447; 323: no photograph in eBL: IM.76985 (Iraq Museum); not in the eBL Fragmentarium (no photograph there): T.1447
- Epic of Gilgamesh, Tablet VI: Ishtar and the Bull of Heaven: 144: no photograph in eBL: VAT.9667 (Vorderasiatisches Museum, Berlin)
- Epic of Gilgamesh, Tablet VII: the death of Enkidu: 51-55: no photograph in eBL: SU-1951.129.A (Museum of Anatolian Civilizations, Ankara); 82-90: no photograph in eBL: SU-1951.129.A (Museum of Anatolian Civilizations, Ankara); 124-125: no manuscript preserves it; 298: no manuscript preserves it
- Epic of Gilgamesh, Tablet VIII: the funeral of Enkidu: 31-36: no photograph in eBL: SU-1951.7 (Şanlıurfa Museum); 47a: no photograph in eBL: SU-1951.7 (Şanlıurfa Museum); 68: no photograph in eBL: SU-1951.7 (Şanlıurfa Museum); 250: no manuscript preserves it
- Epic of Gilgamesh, Tablet IX: Gilgamesh's wandering: 146-147: no manuscript preserves it
- Epic of Gilgamesh, Tablet X: Shiduri, Ur-shanabi and Uta-napishti: 47-60: no manuscript preserves it; 126-130: no manuscript preserves it; 257: no photograph in eBL: Rm.751; 292'-295: no photograph in eBL: Rm.751
- Epic of Gilgamesh, Tablet XII: Enkidu and the Netherworld: 114-117: no manuscript preserves it
- Epic of Gilgamesh, Old Babylonian version: the Yale tablet (Gilgamesh and Enkidu plan the journey to the Forest of Cedar): 295: no manuscript preserves it

## QC fix round (2026-11-12)

- Lines shown 2389 -> 2414; sections 176 -> 177.
- tablet-vii 258: now on Sm.2132 (was K.3588).
- tablet-x 266-273: now on K.3382 (was BM.34160).
- tablet-x 196-220: newly shown on IM.67564.
- tablet-x 23-46, 274-294 on BM.34160: linked photographs corrected (joined pieces).
- tablet-x 61-125, 131-195, 221-256, 258-265 on K.3382: linked photographs corrected (joined pieces).
- eBL's raw ATF codes (!bs, !cm, !qt, !zz, ($___$), &, &n, {( )}, °..\..°, %n) are written out in plain form; each entry's notes end with a key to the signs used on that page.
- Each section's scan_note now lists the lines that are entirely broken, keep only one to three signs, or are partly broken on its tablet, and says that the English of those lines renders eBL's composite text.
- Gap reasons give the real cause per manuscript instead of 'not openly licensed'.

## Notes

- Excluded after the visual check: K.913 (eBL notes its photograph shows K.11913); BM.34916 (+BM.35419) and BM.34964 (+BM.35567), whose photographs show only a small piece with a handful of lines while eBL attributes 139 and 31 lines to the joins.
- Catch-lines: eBL lists the catch-line of a tablet (the first line of the next tablet, written at the end of a library copy) among its 'quotations'. These are the poem's own line on a copy of the poem, so they are used (II 1 on BM.38538, VII 1 on K.4579.A) and the section says so.
- Old Babylonian: only the Yale tablet (OB III) is built. eBL also edits OB II (the Pennsylvania tablet CBS 7771) and other OB/MB pieces; eBL holds no photograph of CBS 7771, and these chapters were not built in this round (open: Penn Museum or CDLI photographs could qualify under spec rule 9).
- Nineveh fragments with only columns i-iii or iii-iv in eBL are not given a face (only the column), because the six-column layout is not proven from eBL data for them. BM.38538 col. i (2 lines) could not be seen on the photograph; only its column vi is used. Some British Museum photographs show the reverse above the obverse (K.8584, K.2756.D); the section names the face.
- `data/pending/gilgamesh_texts.json` (written by the old importer) still lists the 19 old IDs; it is outside this collection's files and was left untouched.
