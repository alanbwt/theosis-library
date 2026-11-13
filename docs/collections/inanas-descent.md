# inanas-descent

**Entry:** `verified-inanas-descent-ob` (1 entry, 57 sections)

## Contents
Inana's Descent to the Netherworld (ETCSL 1.4.1). Coverage: 349 of the 440 ETCSL composite lines are shown on at least one photographed tablet; lines of shown paragraphs that are not on the tablets are named in the section notes.

## Sources
- Photos: CDLI (https://cdli.earth/dl/photo/P....jpg), whole tablet (fat-cross) unless noted, long side <= 2600 px, never upscaled; non-commercial use. Tablets: CBS 13932 (P268937, Nippur); CBS 02198 + CBS 09800 + Ist Ni 00368 (P345344, Nippur); CBS 12638 + CBS 12684 + CBS 12702 + CBS 12752 (+) CBS 12685 (+) CBS 12686 (P267276, Nippur); CBS 13908 + unn. (P268918, Nippur); BM 080054 (P274244, Sippar-Amnanum); UET 6 8 (P346093, Ur); BM 080094 (P469280, Sippar-Amnanum); CBS 11064 + CBS 11088 (P266238, Nippur); UET 6 9 = U 16873 (P346094, Ur); CBS 08146 + CBS 15212 (P269767, Nippur); UET 6 10 + 0433 (P346095, Ur); N 0983 + N 7710 (P275001, Nippur); CBS 13902 (P268913, Nippur); CBS 15162 + N 0953 + N 3200 + unn. (P269717, Nippur); N 2986 (P275004, Nippur); CBS 06894 (P264321, Nippur).
- Sumerian: each tablet's own CDLI transliteration (ATF) rendered in Unicode (sz = š, indices subscript).
- English: ETCSL 1.4.1 translation, CC BY-NC-SA 3.0 (Oxford Text Archive 2518). It renders the composite text.

## Mapping
Sections are ETCSL translation paragraphs. Tablet lines are placed by CDLI's own links to composite Q000343 (ETCSL numbering). Every link is checked against the ETCSL composite text by sign sequence (CDLI and ETCSL spellings brought to one form first: ku3 = kug, sza3 = šag4, gesz = ĝiš, u4 = ud, du10/du11 = dug3/dug4 and similar). CDLI also writes links through an alias defined in the ATF header (`#link: def A = Q...`, then `>>A n`); both forms are read (before 2026-11-12 the alias form was ignored, which lost lines). The placement kept for each tablet is the best-matching chain that runs in composite order, with a preference for CDLI's own link: a link may move to a neighbouring ETCSL line (within 3) that matches clearly better, and a run of links off by the same amount (common with formulaic lines) moves together; a line too broken to be scored keeps CDLI's link and moves with its neighbours; a line confirmed at its own link but out of composite order is kept in the scribe's order; a mistyped link is replaced when the line fits the one ETCSL line free between its neighbours; a line CDLI does not link (or links to a label ETCSL does not have) may take an ETCSL line just after the previous link on a close match (>= 0.6). Linked lines with 3+ signs that still match under 0.25 are dropped. Tablets without any CDLI links are aligned by sign sequence in composite order (best order-preserving chain of matches >= 0.45, each match under 0.6 supported by a neighbouring line; up to three lines between two aligned lines are placed one to one in the ETCSL lines left free there when their signs agree, >= 0.3); repeated refrains are placed by their neighbours. Every moved or sign-placed line is named in its section note. Per paragraph the tablets carrying most lines are chosen (max 4; on a tie the one preserving more signs); a paragraph is shown only if they carry at least half of its lines. Tablets catalogued with a cast, or whose photo has a long side under 1200 px, are not used. Every photograph used was looked at (montages) to confirm it shows the tablet itself.

## Gaps
Paragraphs left out: 48-56, 108-113, 217-225, 226-235, 354-358, 359-367, 368-375. Two Iraq Museum tablets (IM 058380, IM 058522) were dropped because their CDLI photographs are too small to read (long side under 1200 px). N 0983 + N 7710, N 2986 and UET 6 10 are shown in older black-and-white photographs in which the clay looks white (probably whitened for photography).

## Open questions
- Lines whose CDLI link was dropped or moved by the checks are printed by the importer (`python3 scripts/import_inanas_descent.py`).

## QC fixes (2026-11-12)
CBS 06894 rev 2-6 are linked by CDLI one line too high: now rev 2-6 = 380-384 (rev 6 = 384, 'Holy Inana wept bitterly for her husband'), so 384 is shown and 383 is rev 5. UET 6 8 obv ii' 5-12 are now all shown for 164-172 (line 7's CDLI link is mistyped '16'; lines 9-10 = 169-170). CBS 13932 obv 10-13 write lines 13, 12, 8, 11 in their own order; they are shown in that order (before, two of them were wrongly labelled 13A and 13B). Coverage 329 -> 349 of 440 lines, 55 -> 57 sections (173-175 and 295-305 now shown). Review: docs/qc/review-near-east.md; fixes: docs/qc/fixes-near-east.md.
