# QC fixes: Near Eastern collections (2026-11-12)

All 19 touched keys: `check_collection.py` 0 hard failures; warnings unchanged (proto 1, mesha 1, unas 139).

**Sumerian engine (every copy, plus the king list).** Changes:
- reads `#link: def A` / `>>A n` alias links;
- normalises CDLI/ETCSL spellings;
- order-preserving best fit, so off-by-one runs move together, mistyped links are fixed and scribal order is kept;
- unlinked tablets are aligned in order, so refrains are kept;
- shows ETCSL gap rows.

Moved lines are named in their notes. Weak placements and 10 new photos checked by eye. Kesh, eridu, king list unchanged.

| key | lines (before -> after) | notes |
|---|---|---|
| gilgamesh-huwawa | 157 -> 203/324 | line 2; 68-75 complete; 4-7, 13-16, 62-67, 136-144, 201-202 added |
| lament-for-ur | 137 -> 245/442 | F 135, G 136-160; K244, K249 |
| inanas-descent | 329 -> 349/440 | 383/384 = rev 5/6; 164-172 complete |
| shuruppak | 269 -> 276/288 | |
| exaltation | 141 -> 147/154 | |
| enki | unchanged | 133-141 and 5 other ETCSL gaps marked |

**Other keys.**
- proto-cuneiform: MSVO 1, 3 is now Ashm 1924-0577 (the ink number), with CDLI's 1926-0577 noted.
- manetho: note on ζʹ vs "six": Paris gr. 1711 has ζ; Waddell (not Cory) emends to ϛʹ.
- sanchuniathon: "Kronos." corrected to "Kronos," per the 1903 printing, with a note.
- cyrus: the 23a, 26a and 30a clauses moved; 9-14 joined.
- unas: intro names the PT 271 gap and W 646's place.
- diodorus: the note quotes the page.
- mesha: native-rtl lines plus a transliteration.
- vendidad: §12-14/43 short-form note; 7 page-join breaks removed.
- siloam: the note says where the text is; no sharper open photo exists.
- ketef-hinnom: full-resolution detail image added, plus a placement note.

**Open.**
- P343683: the photo shows the Penn pieces, but the ATF was made from the Istanbul pieces (caution added).
- MSVO 1, 3's CDLI number needs confirming.
- Trace-only lines with no fixable position stay hidden.
- Mercer renewal check not done.
- vendidad is not built.

## Round 2 (docs/qc/review-round2.md)

All 9 Sumerian keys: 0 hard failures, 0 warnings.

Engine changes, in every copy:
- Tablet lines that match no ETCSL line are shown marked `+` and noted, including the ETCSL slot they stand in where exactly one is free.
- A better copy is added when the first copy shown is unreadable.
- Variant wording (similarity under 0.35) is flagged.
- `@t`-type modifiers are explained in the key.
- Undefined `>>A n` aliases are read as composite links.
- Edge and two-line continuation alignment.
- The fat-cross boilerplate is gone.

| key | lines | fix |
|---|---|---|
| shuruppak | 276 -> 277 | 271 moved to 271-273 (ETCSL label off by one); 273A shown (N 3757 rev 1') |
| lament | 245 -> 244 | A26 moved to its English (section A 18A-25); obv 1-2, 6, 20-22 and K239-slot obv 32 shown as +; F 134 note; @t keyed |
| inanas | 349 | rev 13-15 (391a-c) shown; 380 also from CBS 06894; 150 pectoral variant flagged |
| exaltation | 147 | 154's second line (UET 6 110 rev 9) shown |
| gilgamesh-huwawa | 203 -> 202 | P343683 dropped (photo shows Penn pieces, text is Istanbul pieces); 1-3 from UET 6 49, 4-7 from CBS 07914 (images checked); 166 lost |
