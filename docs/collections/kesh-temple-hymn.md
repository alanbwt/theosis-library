# kesh-temple-hymn

**Entry:** `verified-kesh-temple-hymn-ob` (1 entry, 19 sections)

## Contents
The Keš Temple Hymn, Old Babylonian version (ETCSL 4.80.2), on the Walters Art Museum prism WAM 48.1802 (one object carries the whole standard text), cropped face by face; face order a-d checked on the image by the blank spaces after the house rubrics. Coverage: 133 of the 165 ETCSL composite lines are shown on at least one photographed tablet; lines of shown paragraphs that are not on the tablets are named in the section notes.

## Sources
- Photos: CDLI (https://cdli.earth/dl/photo/P....jpg), whole tablet (fat-cross) unless noted, long side <= 2600 px, never upscaled; non-commercial use. Tablets: WAM 48.1802 (P272905, provenance uncertain).
- Sumerian: each tablet's own CDLI transliteration (ATF) rendered in Unicode (sz = š, indices subscript).
- English: ETCSL 4.80.2 translation, CC BY-NC-SA 3.0 (Oxford Text Archive 2518). It renders the composite text.

## Mapping
Sections are ETCSL translation paragraphs. Tablet lines are placed by CDLI's own links to composite Q000751 (ETCSL numbering). Every link is checked against the ETCSL composite text by sign sequence (CDLI and ETCSL spellings brought to one form first: ku3 = kug, sza3 = šag4, gesz = ĝiš, u4 = ud, du10/du11 = dug3/dug4 and similar). CDLI also writes links through an alias defined in the ATF header (`#link: def A = Q...`, then `>>A n`); both forms are read (before 2026-11-12 the alias form was ignored, which lost lines). The placement kept for each tablet is the best-matching chain that runs in composite order, with a preference for CDLI's own link: a link may move to a neighbouring ETCSL line (within 3) that matches clearly better, and a run of links off by the same amount (common with formulaic lines) moves together; a line too broken to be scored keeps CDLI's link and moves with its neighbours; a line confirmed at its own link but out of composite order is kept in the scribe's order; a mistyped link is replaced when the line fits the one ETCSL line free between its neighbours; a line CDLI does not link (or links to a label ETCSL does not have) may take an ETCSL line just after the previous link on a close match (>= 0.6). Linked lines with 3+ signs that still match under 0.25 are dropped. Tablets without any CDLI links are aligned by sign sequence in composite order (best order-preserving chain of matches >= 0.45, each match under 0.6 supported by a neighbouring line; up to three lines between two aligned lines are placed one to one in the ETCSL lines left free there when their signs agree, >= 0.3); repeated refrains are placed by their neighbours. Every moved or sign-placed line is named in its section note. Per paragraph the tablets carrying most lines are chosen (max 4; on a tie the one preserving more signs); a paragraph is shown only if they carry at least half of its lines. Tablets catalogued with a cast, or whose photo has a long side under 1200 px, are not used. Every photograph used was looked at (montages) to confirm it shows the tablet itself.

## Gaps
Paragraphs left out: D 58A-58Q, D 58R, H 103A-103K, H 103L. Lettered lines D 58A-58R and H 103A-103L are additions found in one other manuscript, not on the prism; not shown. The Abu Salabikh copies (c. 2600-2500 BCE) are not included.

## Open questions
- Lines whose CDLI link was dropped or moved by the checks are printed by the importer (`python3 scripts/import_kesh_temple_hymn.py`).

## QC fixes (2026-11-12)
Re-run with the revised engine: no change in lines or coverage (133 of 165). Review: docs/qc/review-near-east.md; fixes: docs/qc/fixes-near-east.md.

## QC fixes, round 2 (2026-11-12)
Re-run with the round-2 engine; lines and coverage unchanged. Engine (all Sumerian importers): tablet lines that match no ETCSL line are no longer dropped; a run of up to 3 is shown where it stands, marked + and named in the note, with the ETCSL line it would stand for when exactly one is free. A second copy of a line is added when the first copy shown keeps no readable sign and the other keeps 3 or more. Lines whose signs differ from the composite (similarity under 0.35) are flagged as variants. ATF sign modifiers such as @t are explained in the key. CDLI links written as '>>A n' without an alias definition are read as links to the composite when the file links to no other. The text matcher also places a line next to an aligned run, and the second half of a line written over two tablet lines. The photo boilerplate no longer claims a fat-cross layout. Coverage now 133 of 165. Review: docs/qc/review-round2.md.
