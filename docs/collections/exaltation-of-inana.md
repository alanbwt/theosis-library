# exaltation-of-inana

**Entry:** `verified-exaltation-of-inana-ob` (1 entry, 14 sections)

## Contents
Enheduanna's Exaltation of Inana (nin-me-šara, ETCSL 4.07.2 'Inana B'). Coverage: 147 of the 154 ETCSL composite lines are shown on at least one photographed tablet; lines of shown paragraphs that are not on the tablets are named in the section notes.

## Sources
- Photos: CDLI (https://cdli.earth/dl/photo/P....jpg), whole tablet (fat-cross) unless noted, long side <= 2600 px, never upscaled; non-commercial use. Tablets: UET 6 107b = U 16900a (P464307, Ur); UET 6 108 (P346193, Ur); UET 6 107a = U 07750 (P346192, Ur); HMA 9-01808 (P247905, Tutub); UET 6 109 = U 16879F (P346194, Ur); UET 6 110 (P346195, Ur).
- Sumerian: each tablet's own CDLI transliteration (ATF) rendered in Unicode (sz = š, indices subscript).
- English: ETCSL 4.07.2 translation, CC BY-NC-SA 3.0 (Oxford Text Archive 2518). It renders the composite text.

## Mapping
Sections are ETCSL translation paragraphs. Tablet lines are placed by CDLI's own links to composite Q000623 (ETCSL numbering). Every link is checked against the ETCSL composite text by sign sequence (CDLI and ETCSL spellings brought to one form first: ku3 = kug, sza3 = šag4, gesz = ĝiš, u4 = ud, du10/du11 = dug3/dug4 and similar). CDLI also writes links through an alias defined in the ATF header (`#link: def A = Q...`, then `>>A n`); both forms are read (before 2026-11-12 the alias form was ignored, which lost lines). The placement kept for each tablet is the best-matching chain that runs in composite order, with a preference for CDLI's own link: a link may move to a neighbouring ETCSL line (within 3) that matches clearly better, and a run of links off by the same amount (common with formulaic lines) moves together; a line too broken to be scored keeps CDLI's link and moves with its neighbours; a line confirmed at its own link but out of composite order is kept in the scribe's order; a mistyped link is replaced when the line fits the one ETCSL line free between its neighbours; a line CDLI does not link (or links to a label ETCSL does not have) may take an ETCSL line just after the previous link on a close match (>= 0.6). Linked lines with 3+ signs that still match under 0.25 are dropped. Tablets without any CDLI links are aligned by sign sequence in composite order (best order-preserving chain of matches >= 0.45, each match under 0.6 supported by a neighbouring line; up to three lines between two aligned lines are placed one to one in the ETCSL lines left free there when their signs agree, >= 0.3); repeated refrains are placed by their neighbours. Every moved or sign-placed line is named in its section note. Per paragraph the tablets carrying most lines are chosen (max 4; on a tie the one preserving more signs); a paragraph is shown only if they carry at least half of its lines. Tablets catalogued with a cast, or whose photo has a long side under 1200 px, are not used. Every photograph used was looked at (montages) to confirm it shows the tablet itself.

## Gaps
Every ETCSL paragraph is shown. Lines 125-128 and 131-133 are not on the photographed tablets; the section notes name them.

## Open questions
- Lines whose CDLI link was dropped or moved by the checks are printed by the importer (`python3 scripts/import_exaltation_of_inana.py`).

## QC fixes (2026-11-12)
Re-run with the revised engine: coverage 141 -> 147 of 154 lines (21-22, 45, 49, 65 and 148 now shown). UET 6 108 newly used (photo checked: label 'UET 6/108'); Kress 047 and UET 6 567 no longer needed. Review: docs/qc/review-near-east.md; fixes: docs/qc/fixes-near-east.md.
