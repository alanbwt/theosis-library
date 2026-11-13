# plato-dialogues: Plato on becoming like god

Importer: `scripts/import_plato-dialogues.py` (re-runnable; scans cached in `site/assets/scans/plato-dialogues/`).
Shelf: Greece. Era Classical, tradition greek. 5 entries, 143 sections (one per Stephanus subsection).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-plato-dialogues-theaetetus-172c-177c` (digression, homoiosis theoi 176a-b) | 26 | Bodleian, MS. E. D. Clarke 39 fol. 96v-99r |
| 2 | `verified-plato-dialogues-symposium-201d-212c` (Diotima) | 55 | Clarke 39 fol. 213r-218r |
| 3 | `verified-plato-dialogues-phaedrus-245c-250c` (immortal soul, chariot, place beyond heaven) | 26 | Clarke 39 fol. 232v-235r |
| 4 | `verified-plato-dialogues-phaedo-78b-84b` (affinity of soul and divine) | 31 | Clarke 39 fol. 37r-40v |
| 6 | `verified-plato-dialogues-laws-715e-716d` (god the measure) | 5 | Paris, BnF, grec 1807 fol. 189v |

Order 5 is left free for a Republic entry (see gaps); the Republic passages are now built as their own collection, `plato-republic`.

## Sources

- Scans: Digital Bodleian IIIF, MS. E. D. Clarke 39 (Plato B, 895), CC BY-NC 4.0. Gallica IIIF, Paris gr. 1807 (Plato A, 9th c.), non-commercial reuse with credit.
- Greek: Burnet, Platonis Opera, Perseus canonical-greekLit `perseus-grc2` (CC BY-SA 4.0). `<del>` shown as [ ], `<add>` as < >.
- English (all public domain in the US, Loeb printings before 1929, Perseus `perseus-eng2`): Fowler 1914 (Phaedo, Phaedrus), Fowler 1921 (Theaetetus), Lamb 1925 (Symposium), Bury 1926 (Laws).

## Mapping method

Folio ranges per dialogue from Pinakes (diktyon 47776) and the BnF description. For each page the first and last lines were read on full-resolution IIIF crops and matched to Burnet's text; the words read are stored in `PAGES` and quoted in every scan_note. A Stephanus subsection is assigned to each page whose first-to-last-line span contains part of it, so subsections cut by a page break list both pages. Laws 715e-716d stands on one two-column page (fol. 189v); its scan_note gives the column and line positions read.

## Notes and gaps

- The Greek is Burnet's critical text, not a diplomatic transcription. Known manuscript differences noted in scan_notes (Theaetetus 173e B φέρεται for πέτεται; 176a B has ἀληθῆ, bracketed by Burnet; Laws A writes ξυν- for συν-).
- English section breaks follow each translator's own Stephanus milestones; a few words can sit on the neighbouring side of a break.
- Perseus repeats speaker labels at paragraph breaks inside a speech; the importer prints a label only when the speaker changes.
- Clarke 39 fol. 38v (Phaedo 80c-81b): the inner ends of lines 1-7 are damaged and repaired, some letters retraced by a later hand.
- Republic 6.509b and the Cave (7.514a-521b) are not in this collection. They are now built as a separate collection, `plato-republic` (docs/collections/plato-republic.md), on Laur. Plut. 80.19 with Shorey's Loeb English (1935), after a check of the 1962-1963 renewal lists found no renewal. (Updated 2026-11-12; this note had said the Republic was not built because Shorey's renewal status was unconfirmed.)
- Not built: complete dialogues (only the key passages are mapped).
