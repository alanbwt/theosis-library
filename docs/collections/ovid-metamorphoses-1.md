# ovid-metamorphoses-1: Ovid, Metamorphoses 1.1-415

Importer: `scripts/import_ovid-metamorphoses-1.py` (re-runnable; sources cached in `data/sources/ovid-metamorphoses-1/`, scans in `site/assets/scans/ovid-metamorphoses-1/`).
Shelf: Rome. Era Imperial, tradition roman, category literature. Author id `ovid` (already in `data/authors.json`; no author row added).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-ovid-metamorphoses-1-creation-to-flood` (Met. 1.1-415, complete) | 27 line groups | Florence, Laur. Plut. 36.12 fol. 1r-4v; plus Vat. Urb. lat. 341 fol. 1v-2r for 1.1-75 |

Sections: proem 1-4; chaos 5-20; separation of the elements 21-31; earth, waters, zones 32-51; air, winds, ether 52-68; stars and creatures 69-75; making of man 76-88; golden age 89-112; silver 113-124; bronze and iron, Astraea 125-150; giants 151-162; Lycaon 163-252 (six sections); flood 253-347 (five sections); Deucalion and Pyrrha 348-415 (four sections).

## Sources

- Main witness: Florence, Biblioteca Medicea Laurenziana, Plut. 36.12 ("Ovidii Metamorph"), parchment, 72 leaves, 140 x 275 mm, library dating 1001-1100. Teca digitale BML (CONTENTdm IIIF), manifest `https://cdm21059.contentdm.oclc.org/iiif/2/plutei:671758/manifest.json`. Terms recorded as for the other BML collections (access "Pubblico", non-commercial study with credit).
- Second witness for 1.1-75 only: Vatican City, BAV, Urb. lat. 341 (Metamorphoses with commentary, Beneventan script), DigiVatLib IIIF `https://digi.vatlib.it/iiif/MSS_Urb.lat.341/manifest.json`. Added because fol. 1r of the Laurentianus is abraded in its lower half. The BAV images are only 1775 px wide at full size and carry the library's copyright line.
- Latin: Magnus (1892), Perseus `phi0959.phi006.perseus-lat2` (CC BY-SA 4.0).
- English: Brookes More (1922), Perseus `phi0959.phi006.perseus-eng3` (CC BY-SA 4.0 digital text; public domain in the US). Miller's 1916 Loeb was not used because no clean public digital text was at hand; More's blank verse is clean on Perseus.

## Mapping method

The first and last verse of every page used were read on IIIF crops and identified in Magnus' text (words in `PAGES` and in every scan_note). Laur. Plut. 36.12 page spans: 1r 1.1-55, 1v 56-118, 2r 119-178, 2v 179-238, 3r 239-296, 3v 297-354, 4r 355-412, 4v lines 1-3 = 413-415 (line 4 begins the Python episode, 1.416). Urb. lat. 341: 1v 1.1-37, 2r 38-75. A section lists every page whose span contains one of its lines.

English sections: More's lines do not match Ovid's one to one. Each English section starts at the More line that begins the rendering of the section's first Latin line (`SECTIONS`, found by comparing the texts). More's line 479 ("Deucalion's plaint to Pyrrha;—and they wept") renders the start of 1.367 but closes the section 1.348-366; a translator note says so.

## Notes and gaps

- Complete: 1.1-415.
- Laur. Plut. 36.12 fol. 1r: the lower half is abraded; the last line (1.55) is legible only at its end ("...tonitrua mentes"), but the line above (1.54 "...consistere nubes") and the first line of fol. 1v (1.56) fix the page break.
- Manuscript readings noticed while reading page edges (noted in scan_notes): 1.56 "frigora" (Magnus "fulgura"); 1.173 "a fronte potentes" (Magnus "hac parte potentes"); 1.296 word order "piscem deprendit summa".
- Uncertain: the date of Urb. lat. 341. DigiVatLib gives no date; the wording "11th-12th century, Beneventan script" rests on the script and on the literature listed by the BAV (Lowe's list of Beneventan manuscripts, Cavallo). Not used: Florence, San Marco 225 and Naples IV F 3 (not in the downloadable Teca/IIIF sets found).
