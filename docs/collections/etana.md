# Etana (cuneiform tablets) (key `etana`)

Built 2026-11-12 by `scripts/import_etana.py` (re-runnable; engine in `scripts/import_gilgamesh.py`, whose docstring gives the chain of evidence).

## Contents (3 entries, 17 sections)

| Entry | eBL lines | lines with any manuscript | published | sections | tablets used |
|---|---|---|---|---|---|
| Etana, Standard Babylonian Tablet I: the founding of kingship at Kish | 40 | 40 | 40 | 2 | 2 |
| Etana, Standard Babylonian Tablet II: the eagle and the serpent | 152 | 152 | 98 | 7 | 3 |
| Etana, Standard Babylonian Tablet III: the flight to heaven | 131 | 131 | 131 | 8 | 5 |

Total: 269 of the 323 lines in the eBL edition (83%); 269 of the 323 lines that survive on any manuscript.

## Sources

- Original: eBL corpus edition L I.9, Etana, manuscript-level ATF only (the transliteration of the signs on the photographed tablet), CC BY-NC-SA 4.0.
- English: B. R. Foster (eBL edition), line by line, CC BY-NC-SA 4.0. It renders eBL's composite text; every section's scan_note says bracketed restorations may come from other tablets.
- Photographs: British Museum photographs from the eBL fragment photo API ((c) The Trustees of the British Museum, CC BY-NC-SA 4.0, as stated by eBL).

## Mapping method

eBL's corpus edition lists, for every line, each manuscript carrying it with that manuscript's own column and line numbers. For each line the importer takes the checked, photographed British Museum manuscript with the most preserved signs, with a switching penalty so sections are runs on one column of one tablet (max 30 lines). Every photograph used was looked at (labelled contact sheets, full views where needed) and the result is recorded per tablet in `CHECKS` in the importer and in each section's scan_note.

Excluded after checking:

- K.8572: eBL treats K.8572 (+) BMC-T.236 (+) BkMus.7.6 as one manuscript (119 lines); the eBL photograph shows only K.8572, a small piece with 7 lines.

## Gaps (and why)

Lines not shown survive only on tablets without an openly licensed photograph (Iraq Museum, Berlin, Istanbul, Ankara and other holders whose images eBL shows by permission only), on tablets eBL has not photographed, or on joins whose photograph does not show the lines.

- Etana, Standard Babylonian Tablet II: the eagle and the serpent: 1-43: only on K.8572; 120-127: only on K.8572; 148-150: only on K.8572

## Notes

Old Babylonian (Morgan Library, Louvre) and Middle Assyrian (Berlin, Istanbul) versions are not included: eBL has no open photographs of those tablets. K.8572 is excluded (see above), which leaves Tablet II lines 1-43, 120-127 and 148-150 without a witness here.
