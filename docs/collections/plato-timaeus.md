# Plato, Timaeus (Paris gr. 1807)

Key `plato-timaeus`, prefix `verified-plato-timaeus-`, shelf Greece. Importer: `scripts/import_plato_timaeus.py`
(also holds the builder reused by `scripts/import_plato_critias.py`).

## Contents

The complete *Timaeus*, Stephanus 17a-92c: 76 entries (one per Stephanus page, `verified-plato-timaeus-17` to
`-92`), 364 sections (one per Stephanus section, 17a, 17b ...). Every section shows the folio side(s) of the
manuscript that carry it, Burnet's Greek and R. G. Bury's English.

The Atlantis account is Tim. 20d-25d, entries `-20` to `-25` (themes include `atlantis`); the
*Critias* is a separate collection (`plato-critias`).

## Sources

| Layer | Source | Licence |
|---|---|---|
| Scan | Paris, BnF grec 1807 ("Plato A"), Constantinople c. 850-875, fol. 114r-144v (62 page images). BnF IIIF via `openapi.bnf.fr`, Gallica ark:/12148/btv1b8419248n | rightsstatements.org NoC-NC; credit "Source gallica.bnf.fr / BnF" |
| Greek | J. Burnet, Platonis Opera IV (Oxford 1902), Perseus canonical-greekLit `tlg0059.tlg031.perseus-grc2` | edition PD; digital text CC BY-SA 4.0 |
| English | R. G. Bury, Plato IX (Loeb 1929), Perseus `tlg0059.tlg031.perseus-eng2` | US public domain since 1 Jan 2025 (published 1929); digital text CC BY-SA 4.0 |

Paris gr. 1807 is the oldest medieval manuscript of the Timaeus and Critias (papyrus fragments aside). Folio range per the BnF description in the
IIIF manifest (Timaeus 114r-144v, Critias 145r-151r). Each page has two columns of 44 lines.

## Mapping method

Own visual check, no interpolation. For every column from 114r col. b (title and first words under it) to
144v col. b, the first line(s) were cropped from the full-resolution BnF images and read, and the words were
located in Burnet's text. The script's `COLUMNS` table records each column's opening words in Burnet's
spelling (the scribe's spelling and accentuation differ). A section is linked to every folio side whose columns
contain any of its text, so a section that crosses a page break lists both pages. Every section's `scan_note`
quotes the opening words of each column it spans; each entry's introduction lists the openings for the page.

Checks made on the images: the Timaeus title and "eis dyo treis" open 114r col. b; the last words "eis ouranos
hode monogenes on" followed by the end title "timaios e peri physeos" stand at the foot of 144v col. b.
Column lengths between consecutive openings run 886-1,013 letters of Burnet's text, a consistency check on
the readings.

## Gaps and notes

- None in the text: all 364 Stephanus sections are present in Greek and English and linked to images.
- The Greek is Burnet's critical text, not a diplomatic transcription of Paris gr. 1807; readings differ in
  places (e.g. 135r col. b reads "hoti de dia pyros" where Burnet has "hoti dia pyros").
- Bury's footnotes are omitted. Quotation marks are added where Perseus marks quoted speech (`<q>`), since the
  Loeb prints these as quotations; Perseus' emphasis/foreign-word tags are shown in italics.
- Speaker labels (ΣΩ./Soc., ΤΙ./Tim., ΚΡ./Crit., ΕΡ./Herm.) are shown only where the speaker changes, the same way in
  Greek and English. Perseus repeats the label at each of its card breaks inside one speech; those repeats are not shown
  (QC fix 2026-11-12: they had put labels inside Timaeus' and Critias' monologues, sometimes mid-sentence).
- Quotation marks: where Perseus continues one quotation across a card break (`rend="merge"`), no new opening or
  closing mark is added; a quotation inside a quotation (the Egyptian priest's words inside Critias' tale) takes single
  marks.
- Stephanus section breaks in Bury's English can fall a few words from Burnet's because English word order
  differs (as in the printed Loeb). Where Bury's milestone put a whole reply on the wrong side (17a/17b, 18a/18b), the
  reply is moved to the section that holds the Greek and the scan_note says so. Elsewhere the English milestones are
  Perseus' word positions; a few sections (e.g. 36a/36b, 50b/50c) carry part of a sentence that Burnet prints in the
  neighbouring section.
- Scholia and marginal notes on the pages are not transcribed.
