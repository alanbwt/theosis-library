# virgil: Virgil, Eclogue 4 and Aeneid 6.724-751

Importer: `scripts/import_virgil.py` (re-runnable; sources cached in `data/sources/virgil/`, scans in `site/assets/scans/virgil/`).
Shelf: Rome. Tradition roman, category literature. Author id `virgil` (already in `data/authors.json`; no author row added).

## Contents

| order | entry | era | sections | manuscript pages |
|---|---|---|---|---|
| 1 | `verified-virgil-eclogue-4` (Eclogue 4, complete, 63 lines) | Late Republic | 11 line groups | Vergilius Romanus, Vat. lat. 3867 fol. 9v, 10r, 10v, 11r |
| 2 | `verified-virgil-aeneid-6-724-751` (Anchises on the world-soul, purification, Lethe) | Imperial | 3 (724-732, 733-742, 743-751) | Vergilius Vaticanus, Vat. lat. 3225 fol. 55r, 55v |

## Sources

- Scans (DigiVatLib IIIF, BAV; copyright line on each image; reproduced for non-commercial study with credit):
  - Vat. lat. 3867 (Vergilius Romanus, 5th century, 18 lines a page), manifest `https://digi.vatlib.it/iiif/MSS_Vat.lat.3867/manifest.json`. Eclogue 4 has the red title SAECULI NOVI INTERPRETATIO on fol. 9v. Saved at 1800 px wide.
  - Vat. lat. 3225 (Vergilius Vaticanus, BAV "sec. IV", 21 lines a page), manifest `https://digi.vatlib.it/iiif/MSS_Vat.lat.3225/manifest.json`. The BAV catalogue lists Aeneid 6 fragments on fol. 45r-57v, including 6.589-755. Saved at full size (1780 px).
- Latin: Greenough (Ginn), Perseus `phi0690.phi001.perseus-lat2` and `phi0690.phi003.perseus-lat2` (CC BY-SA 4.0).
- English: James Rhoades, The Poems of Vergil (Oxford, 1921), Perseus `phi0690.phi001.perseus-eng2`; Theodore C. Williams, The Aeneid of Virgil (1910), Perseus `phi0690.phi003.perseus-eng2`. Both public domain in the US. Fairclough's 1916 Loeb was not used because no clean digital text with line references was at hand.

## Mapping method

First and last line of each page read on IIIF crops (rustic capitals, fully legible):
- Romanus: 9v = Ecl. 4.1-17, 10r = 18-35, 10v = 36-53, 11r = 54-63 (then a miniature). Ecl. 5 begins on 11v.
- Vaticanus: 55r = Aen. 6.719-739 (724 is its sixth line), 55v = 740-755 (751 is its twelfth line).
Words read are in `PAGES` and in every scan_note.

English sections: both translations are in verse with more lines than the Latin (Rhoades 79 lines for 63; Williams lines 942-977 for 724-751). In Eclogue 4 each English section starts at the translator's line that begins the rendering of the section's first Latin line (`sections`), so a half line can sit on the neighbouring side. In Aeneid 6 (QC fix 2026-11-12) the English is cut at the end of Williams' sentences: his sentence for 728-734 ("Thence man and beast ... on the radiant world.") runs across the 732/733 break and is given whole with 724-732 (English 724-734), so 733-742 has the English of 735-742; his line 966 is divided at the full stop, "Or burned away in fire." ending 733-742 and "Each man receives" opening 743-751. Each section's scan_note gives the Latin lines its English renders.

## Notes and gaps

- Complete: Eclogue 4. The Aeneid entry covers 724-751 only, as asked.
- Manuscript reading noted: Ecl. 4.53 Romanus TUM (Greenough "tam").
- The Perseus Rhoades file lowercases three line-initial words (Muses, Apollo, O); the importer restores the capitals (`CAPS_FIXES`) and says so in a translator note. This is the only change to a source text.
- The Vergilius Vaticanus has no Eclogues, so Eclogue 4 uses the Romanus; Aeneid 6.724-751 is not checked in the Romanus or the Palatinus.
