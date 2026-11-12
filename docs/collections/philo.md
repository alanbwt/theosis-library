# philo: Philo of Alexandria, Creation and the Logos

Importer: `scripts/import_philo.py` (re-runnable; scans cached in `site/assets/scans/philo/`).
Shelf: Dead Sea Scrolls & Second Temple. Era Second Temple, tradition jewish, category philosophy.
3 entries, 176 sections (one per Cohn-Wendland section). Author row `philo` is in the collection file.

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-philo-on-the-creation` (De opificio mundi, complete) | 172 (1-172) | Pal. gr. 248 fol. 40v-56v (33 pages) |
| 2 | `verified-philo-confusion-of-tongues-146-147` (Logos as firstborn and image) | 2 | Pal. gr. 248 fol. 205r, lines 2-10 |
| 3 | `verified-philo-who-is-the-heir-205-206` (Logos between Creator and creation) | 2 | Pal. gr. 248 fol. 293r, lines 18 ff. |

## Sources

- Scans: Vatican City, BAV, Pal. gr. 248 (14th-15th c., paper, Philo corpus), DigiVatLib IIIF colour images at 2000 px. Terms: (c) Biblioteca Apostolica Vaticana, notice on each image; used with credit (spec rule 9). Folio ranges of the treatises from Pinakes diktyon 65980.
- Greek: Cohn (Opif., 1896) and Wendland (Conf. 1897, Her. 1898), Philonis Alexandrini opera quae supersunt, via First1KGreek `tlg0018.tlg001/013/015.1st1K-grc1` (CC BY-SA 4.0).
- English: C. D. Yonge, The Works of Philo Judaeus, vols. 1-2 (Bohn, 1854), public domain, via First1KGreek `1st1K-eng1` (Scholer sectioning).

## Why this manuscript

Vat. gr. 381 (suggested) does not contain De opificio (Pinakes 67012) and is online only as a black-and-white microfilm. Paris gr. 435 is on Gallica, which returns HTTP 403 to automated requests. The BML server for Laur. Plut. 10.20 did not answer. Munich Cod. graec. 459 (13th c., Cohn-Wendland's A, De opificio fols. 163-181) is online only as a microfilm and is hard to read reliably. Pal. gr. 248 has colour images and carries all three texts.

## Mapping method

For every page the first and last lines were read on the image (crops at full 2000 px width) and matched to the Greek; the words read are stored in `OPIF_PAGES` and quoted in each scan_note. The last words of each page were checked against the first words of the next, so no line was missed (this caught one faulty automatic crop on fol. 53r, corrected by reading the whole top of the page). A section is linked to every page whose first-to-last-line span contains part of it. For Conf. 146-147 and Her. 205-206 the line positions on the page are given.

## Text checks

- Greek: the whole of De opificio was compared word by word, accents included, with a second digital Cohn text (Khazarzar, cached as `data/sources/philo/opificig.htm`). They agree except for two First1KGreek OCR faults, checked on the printed page (archive.org `philonisalexand05wendgoog`, Cohn pp. 7 and 36) and corrected: §24 `ἤδη τὴν [νοητὴν] πόλιν`, §104 `ἔχουσ’`. Conf. 146-147 and Her. 205-206 agree with the second text.
- First1KGreek places Cohn's numbers at the start of the printed line, so many sections began mid-sentence. The importer re-splits the text at the sentence where each section begins (Khazarzar/TLG placement, which also matches Yonge's sectioning in nearly every case).
- English: the digital Yonge of On the Creation was diffed against the OCR of the 1854 printing (`worksphilojudaeu01philuoft`); four real differences were restored to the 1854 wording ("and fish", "fulness", "pre-eminent", "beforementioned"). Conf. and Her. passages agree with vol. 2.

## Notes and gaps

- The Greek is the critical text, not a transcription of Pal. gr. 248; the manuscript's spelling and some words differ (e.g. the title reads `περὶ τῆς τοῦ Μωσέως κοσμοποιίας`).
- Yonge translated from Mangey's edition (1742) and sometimes condenses; he omits the Hippocrates sentence at the start of §124. His section breaks (Scholer edition) sometimes differ from the Greek by a clause (e.g. §82 begins in his English with "I have now mentioned the second reason", which the Greek places at the end of §81; §92 differs by one clause).
- Three different hands write the three treatises in Pal. gr. 248; the Conf. hand is the most cursive.
- Not built: complete Conf. and Her. (only the Logos passages were asked for).
