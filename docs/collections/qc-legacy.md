# QC of legacy collections (2026-11-12)

Scope: the rule that every section links the manuscript page carrying its text, with verbatim
original-language text and verbatim English. Three tasks: (1) Poetic Edda page mapping and
Old Norse/English alignment, (2) manuscript transcriptions for Codex Vaticanus, Bezae,
Alexandrinus and Washingtonianus, (3) a scan_pages audit of every legacy collection.

No git commit, build or deploy was done. `data/texts.json` was not edited; the catalog changes it
needs are listed at the end.

## 1. Poetic Edda (verified-edda-*, Codex Regius GKS 2365 4to)

Script: `scripts/qc_edda_pages.py` (re-runnable; rebuilds all 11 entries from cached sources).
Sources cached in `data/sources/qc-legacy/edda/`.

### What was wrong

- Pages: the old entries spread the stanzas evenly over the leaves (16 per page for Hávamál,
  12 for Alvíssmál, and so on) and used the wrong leaves for most poems. Alvíssmál pointed at
  fol. 23r-24r and Völundarkviða at 21r-23r, which carry heroic poems; the eleven poems actually
  fill fol. 1r-20r (manuscript pages 1-39).
- English alignment: Thorpe's English was paired with the Old Norse by stanza number. That put
  the wrong English beside the Old Norse in Völuspá from stanza 21 on (Thorpe follows a different
  stanza order), in Völundarkviða from 16 on, in Hávamál at 62-63 and from 103 on, in Hymiskviða
  at 6-9, in Þrymskviða from 7 on and in Alvíssmál from 9 on. Gutenberg misprints (Vafþrúðnismál "33" twice, Hárbarðsljóð "36" and
  "39") made the old import drop or misplace stanzas. Völuspá 66 and Völundarkviða 41 were missing.
  Speaker labels (e.g. "_Harbard_.") were attached to the wrong stanza.

### Mapping method

- Wimmer and Finnur Jónsson, *Håndskriftet Nr. 2365 4to ... (Codex regius af den ældre Edda) i
  fototypisk og diplomatisk gengivelse* (København 1891), archive.org `handskriftetnr2300kben`,
  prints each manuscript page's text with a caption of the stanzas on it. The captions use Bugge's
  numbering, which differs from the Old Norse text used here (e.g. Völuspá), so each page break
  was located by the words of the text in the diplomatic page (OCR cached as
  `wj1891_dipl_pages.json`).
- Every image used (handrit.is image 10-48 = manuscript pages 1-39, fol. 1r-20r) was viewed: the
  first line of each page and the page number written in the top corner agree with the 1891 page.
- Sections: one per manuscript page, holding the stanzas that begin on it; a stanza that runs onto
  the next page lists both pages. Each `scan_note` names the folio, the 1891 page and caption, and
  the first-line words checked on the image.

### Alignment method

Each Thorpe stanza was matched to the Old Norse stanza it translates by reading both
(concordance table `CONC` in the script, with asserts that every Old Norse stanza and every Thorpe
stanza is used once). English stanzas carry the Old Norse stanza number; Thorpe's own numbers are
listed in each entry's `translator_notes` where they differ. Where Thorpe's stanza breaks fall
mid-stanza, the stanzas are shown as one numbered block (e.g. Völundarkviða 19-26).

### Known limits

- The Old Norse is Guðni Jónsson's normalized edition (heimskringla.no), not a transcription of
  the manuscript. It adds material from other manuscripts in places. Recorded per section:
  Völuspá 65 and the refrain at 54 are not in Codex Regius (Hauksbók); Völuspá 15 has names not in
  R; Grímnismál 23 and 24 stand in reverse order in R; Völuspá 48 stands after 51 in R.
  Thorpe's Alvíssmál stanza 9 is not in R and is not shown.
- Licence of the Old Norse: heimskringla.no states none; the old "public domain" claim is not
  verified (Guðni Jónsson died 1974). Recorded in `verification.original_text_license`.
- Prose passages of the manuscript are not included (as before).
- Images are the original 3,200 x 4,900 px handrit.is files (larger than the 2,600 px spec).

## 2. NT manuscripts: diplomatic transcriptions

Script: `scripts/qc_swap_ntvmr_transcriptions.py` (re-runnable; `--force`, `--dry-run`,
`--allow-all-rights-reserved`), helpers `qc_ntvmr_fetch.py`, `qc_ntvmr_parse.py`,
`qc_ntvmr_check_w.py`. Cache in `data/sources/qc-legacy/ntvmr/`.

The manuscript transcription is now `original_text` (verse-aligned, `<sup>` verse numbers);
Tischendorf 8 is kept per section as `edition_text`. `verification.primary_greek` is
`ntvmr_transcription` or `igntp_transcription`; source and licence (CC BY 4.0) are recorded.

| Manuscript | Swapped | Left on Tischendorf, and why |
|---|---|---|
| Vaticanus (NTVMR 20003) | 220 / 220 | none |
| Bezae (NTVMR 20005, Greek pages only) | 39 / 45 | Matt 1-5, John 18: NTVMR files say "All rights reserved by the INTF" |
| Alexandrinus (NTVMR 20002) | 226 / 228 | Luke 15-16: same restriction (fol. 58r) |
| Washingtonianus | 36 / 88 | Mark 16 chapters from NTVMR 20032; John 20 chapters from the IGNTP John transcription (CC BY 4.0, GitHub copy vanja-ivancevic/gospel-of-john-tc, IGNTP site certificate expired). Matthew and Luke: NTVMR files "All rights reserved", and Luke partly misaligned with the page index |

Transcription policy: first hand only (later correctors dropped); no accents; nomina sacra as
written without the overline; restored letters in `[ ]`; a dot below uncertain letters; `[...]`
for gaps; words split across pages rejoined. Verses a manuscript omits show `[not in Codex X]`
and are listed in a "Manuscript note" (checked on images: Alexandrinus 1 Cor 6:3-6, Rom 11:12;
W Mark 10:48). Bezae: only the Greek (verso) pages are used; the Latin column is not included.

Page fixes from the transcription's page attribution: 372 verses crossing a page break sat whole
in sections linking one page (262 Vaticanus, 110 Bezae); Alexandrinus Heb 7:9-16 lacked fol. 141v
(NTVMR labels two leaves "141r/141v"; pages now matched by facsimile leaf); W John 4:1-10, Mark
10:1-10 and 12:1-10 listed pages without their text, and John 9:41 and 18:16 lacked their page;
Bezae Matt 18:11 (on fol. 59v) had been dropped and is restored.

Removed for lack of an image: Vaticanus Jude 8-25 (p. 1444) and Bezae John 20:14-31
(fol. 177v-178v) are not shown, because those page images are not in the repo; each entry's
introduction says so. Adding the images would allow these verses back.

Integration needed: `scripts/render_verified.py` labels these four manuscripts' Greek column
"Greek · Tischendorf 8" regardless of content; it should read `verification.primary_greek` as the
Sinaiticus branch does. `data/texts.json` rows for the 521 swapped ids need `language`, `source`
and `description` copied from the JSON (list in
`data/sources/qc-legacy/ntvmr/texts_json_row_changes.json`).

## 3. scan_pages audit of all legacy collections

Script: `scripts/qc_scan_audit.py`; full machine-readable list in
`data/sources/qc-legacy/audit/problems.json` (summary in `summary.json`, image checks in
`visual_checks.json`).

| Collection | Sections checked | Data used | Result |
|---|---|---|---|
| Sinaiticus | 2,609 with verses | CSP folio cache, `scan_folio_ranges` | 33 sections link a page with none of their text; 3 miss a page with their text; 98 miss the second page for one verse at a page break |
| Venetus A (Iliad) | 639 | Homer Multitext 2024c line-to-image index | 472 sections miss the page that holds most or part of their lines (each 25-line section links only its first line's page); Butler English misaligned |
| Leningrad | 3,084 | tanach.us LCIndex.xml | no problems |
| 1QIsa-a | 185 | 54-column verse map | no problems |
| Quran (BnF Arabe 328) | 159 | Corpus Coranicum page data | no problems |
| Gilgamesh | 185 | one tablet photo per entry | no problems (one label error) |
| Josephus | 3 | Schmidt folio list | consistent; Vat. gr. 984 152v/153r run-over unsettled |
| Edda | all | Wimmer and Jónsson 1891 | fixed (section 1) |

Not fixed (files outside this QC's write scope):

- Sinaiticus: `prov-24` 24.25-34 and all sections of `prov-25` to `prov-29` point at
  Q65_4r_B285 (fol. 139r holds only Prov 24:14-24 and 30:1-14); chapter 25 begins on fol. 140r
  (`prov-25-Q65_5r_B287.jpg`, on disk, linked by no section). `sirach-31`, `sirach-32` and 33.1-16
  point at Q69_7r_B355 (fol. 174r holds Sir 30:1-24 and 33:16-22). Cause: the folio fixer treats
  CSP's first/last verse of a page as a continuous range, which fails where the LXX order differs
  from chapter order. `john-7` 7.51-53 should link 252r (Q80_6r_B531). Sirach 30:25 and 33:17-24
  are marked "Not present" though 33:16-22 are visible on fol. 174r.
- Venetus A: every section links only the page of its first line (e.g. 1.276-300 links 17r, but
  17v begins at 1.277). `import_homer.py` split Butler's English by paragraph count, so Greek and
  English do not line up (1.76-100's English starts at 1.43).
- Gilgamesh K.2252 section "SB XI 10-81": label says col. i 10-24 but the section also holds lines
  53-57 and 81 (image correct).

## Catalog changes needed in data/texts.json (not made)

Edda rows (`scans.pages` and `description`):

| id | folios | scan files (codex-regius/codex-regius-pN.jpg) |
|---|---|---|
| verified-edda-voluspa | 1r-3r | p10-p14 |
| verified-edda-havamal | 3r-7v | p14-p23 |
| verified-edda-vafthrudnismal | 7v-8v | p23-p25 |
| verified-edda-grimnismal | 9r-11r | p26-p30 |
| verified-edda-skirnismal | 11r-12r | p30-p32 |
| verified-edda-harbardsljod | 12r-13v | p32-p35 |
| verified-edda-hymiskvida | 13v-15r | p35-p38 |
| verified-edda-lokasenna | 15r-17r | p38-p42 |
| verified-edda-thrymskvida | 17r-18r | p42-p44 |
| verified-edda-volundarkvida | 18r-19v | p44-p47 |
| verified-edda-alvissmal | 19v-20r | p47-p48 |

Old descriptions ("N sections across N folios") should take the new `description` from each JSON.
After the rows change, `codex-regius-p49.jpg` to `p56.jpg` are used by nothing and can be removed.
`scripts/render_verified.py` labels the Edda original column "Old Norse · heimskringla.no"; a
fuller label would be "Old Norse · Guðni Jónsson (heimskringla.no)".
