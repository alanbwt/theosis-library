# QC 2: Codex Sinaiticus pages and the Venetus A Iliad (2026-11-12)

Rule checked: every section links the manuscript page(s) that carry its text (all of them when it
crosses a page), with verbatim original-language text and verbatim English aligned to it.
Input: `data/sources/qc-legacy/audit/problems.json` (Task 3 of `docs/collections/qc-legacy.md`).
No git commit, build or deploy. `data/texts.json` and shared scripts were not edited; the catalog
changes needed are listed at the end.

## A. Codex Sinaiticus (verified-sinaiticus-*, 699 entries, 2,624 sections)

Script: `scripts/qc2_sinaiticus_folios.py` (`index`, `fix`, `check`, `greek`, `legacy-audit`;
re-runnable, `fix` is idempotent). Data and reports: `data/sources/qc-sinaiticus-venetus/`.

### Source of the page data

codexsinaiticus.org did not answer during this work (connections timed out, also outside the
sandbox). The Codex Sinaiticus Project transcription itself is published as TEI XML by its
partner ITSEE (University of Birmingham): github.com/itsee-birmingham/codex-sinaiticus,
`sinaiticus_full_v195.xml` (v1.95, 30.8.2024, CC BY-NC-SA 3.0; cached as
`sinaiticus_full_v195.xml.gz`). It marks every page, column and line break and every verse, so the
page, column and line of each verse can be read directly (`sinaiticus_xml_index.json`). A verse counts
on a page only if some of its letters are there.

This replaces the CSP website's page summaries ("first verse - last verse") used before. Those
summaries caused both kinds of error in the earlier audit: (1) where the Greek order differs from the
chapter order (Proverbs 24-31; Sirach 30-36) a summary is a min/max pair, not a range; (2) a verse
that ends on the last line of a page is named as the first verse of the next page.

### What changed

- 135 sections in 104 entries got new `scan_pages`, all in codex order. Among them: Proverbs 24.25-34
  and all of Proverbs 25-29 (now fol. 139v-142v instead of 139r); Sirach 31, 32 and 33.1-16 (now fol.
  175v-176v, Q69_8v, Q70_1r, Q70_1v); John 7.51-53 (251v + 252r, not 252v); Jeremiah 8.19-23 (fol. 73r
  only); 91 sections gained the second page of a verse that runs over a page break, including
  four found only by the XML (Jer 10:25 onto Leipzig fol. xx, Prov 29:27 onto 142v, Ps 71 and 80).
- Every section has a `scan_note` giving folio, column and lines (e.g. "fol. 140r (Q65_5r_B287), col. 1
  line 25 to col. 2 line 1"), with verse ranges per page when a section spans pages.
- Sections for verses absent from the manuscript now link the page where the text passes over them
  (Hermas 68.6-9 had pointed at a Genesis fragment and a Hermas 91 page; it now points at Q95_1v).
- Duplicate image: 2 John now uses `1john-5-Q89_8r_B675.jpg` (same photograph as
  `2john-1-Q89_8r_B675.jpg`, which no section uses now).
- Verification fields rewritten per entry: `scan_local_paths`, `scan_folio_ids`, `scan_folio_ranges`
  (from the XML), `section_folios_source: csp_xml_v1.95`, `section_folios_note`.

### New images (7)

CSP tiles could not be fetched, so the script used a GitHub copy of the same CSP photographs
(github.com/0x53616D75656C/Codex-Sinaiticus, images/uncompressed, about 2000 px). That copy is not
numbered by folio; each file was identified on the image (folio number in the corner, recto/verso,
first words, and the preceding file being identical to our image of the preceding page):
`sirach-31-Q70_1r_B359.jpg` (475), `sirach-32-Q70_1v_B360.jpg` (476), `hermas-27-Q93_7r_B721.jpg`
(817), `jer-10-Q47_1r_L020.jpg` (223), `prov-29-Q65_7v_B292.jpg` (408), `ps-71-Q61_4r_B221.jpg` (337),
`ps-80-Q61_7v_B228.jpg` (344). CSP image ids: Q47_1r_L020 and Q93_7r_B721-P007 from archived CSP pages
(web.archive.org, 2024); the others follow from their neighbours. When codexsinaiticus.org is back,
`fix` will fetch CSP tiles for any page still missing; these seven can be replaced the same way.

### Greek

Every verse was compared with the first-hand text of the XML. Fixed (folio-walker bugs: the walker
assumed 8 leaves per quire and stopped at the first page without the chapter):
Barnabas 14:4 (cut off at the foot of Q91_6v) and 14:5-9 (shown as not present); Sirach 30:25, 33:16a-33
and 36:10a-27 (shown as not present or missing); Zechariah 2:4 (empty); Judith 12:11 (lacked οϲ ην
εφεϲτηκωϲ επι παντων των αυτου). Sirach 33 and 36 were re-sectioned so each Greek verse stands beside
the KJV verse that translates it (the numbering differs; mapping in each introduction), and Sirach
30-36 got a note on the manuscript order. Remaining differences: 582 verses differ by a letter or two
(transcription version 1.05 on the website vs 1.95), 17 where the site shows a correction written over
an erasure (as the CSP website does), and Hermas 91:3, of which only νοηϲε survives (not shown).

### Checks

- `check` (XML, letter level): 0 problems.
- The earlier audit's own logic, run read-only (`legacy-audit`): 19 items, none a real error. 11 are
  verses that end on the last line of a page (CSP summary artefact; e.g. Mark 5:10 / 5:11 and Prov
  24:24 / 24:25 checked on the images: 5:11 and 24:25 begin their pages). 6 come from that script's own
  hand-made range for Q69_8v, which leaves out Sirach 31:1-18. 2 are sections whose labels 16a/10a it
  skips.
- Read on the images: Prov 25:1 (140r col. 1 l. 25) and 25:8 end (col. 2 l. 1); Sirach 31:25 and 31:31
  end (176r); 33:15/16a/36:10b transposition point (176v col. 2 ll. 27-29); Hermas 27:7 (347r strip,
  l. 3); Jer 10:25 end (Leipzig xx, ll. 1-8); John 7:51-52 and 8:12 (252r col. 1 ll. 1-12).

## B. Iliad on Venetus A (verified-venetus-iliad-1..24, 638 sections)

Script: `scripts/qc2_venetus.py` (`build`, `check`, `crops`). Each section is now the text of one page;
it links exactly that page.

- Page of each line: Homer Multitext 2024c DSE index (`hmt-2024c.cex`). Lines the index omits were
  placed by text order when both neighbours are on the same page (2.89, 7.34, 8.549, 13.422, 13.522,
  13.749, 14.147a, 23.622) or read on the photograph (11.275, 16.276-300 = fol. 211v, which the index
  lacks, 16.401, 16.627-628, 16.704-705, 18.604_605, 18.617). The index gives 13.281 the image of fol.
  172r; the photograph of 169v shows it as the first line.
- Greek: HMT diplomatic edition of Venetus A (`original_text`, release licence CC BY-NC 4.0);
  Munro and Allen (Perseus) as `edition_text`. Lines of the standard text not in Venetus A (e.g. 1.265;
  40 lines in all) are in the edition text with the page where they would stand, and listed in the
  introduction.
- English: Murray (Loeb 1924-1925, Perseus) for Books 2-24, cut only at his line marks; a block crossing
  a page break goes with the page holding most of its lines. Each section states its English range
  (`original_ref`, `scan_note`); 634 sections start and end within 3 lines of the Greek, 4 within 5.
  **Book 1:** the Perseus "Murray" Book 1 is a later modernised revision, not the 1924 text (1924:
  "The wrath do thou sing, O goddess"; checked on archive.org `iliadmurray01homeuoft`, p. 3), so it was
  not used. Book 1 keeps Butler (1898), now cut at each page break by reading Butler against the Greek.
- 10 images added from HMT IIIF at 1024 px like the others (154r, 163v, 190v, 205v, 211v, 223r, 238v,
  251r, 257r, 259v); all 630 images in `venetus-a/` are used.
- Verified on the images: first and last line of one page per book (18r, 33r, 46v, 56v, 71r, 85v,
  96r, 106r, 118v, 131v, 146r, 159r, 172r, 185v, 198v, 214v, 231r, 245r, 255v, 265r, 276r, 287v, 301v,
  318v) plus 17v, 169v and the 12 pages around the placed lines (`venetus_visual_checks.json`).
- `check`: 0 problems (one page per section, every manuscript line, every edition line and every
  English block exactly once). The earlier audit's test leaves 15 items, all the placed lines above.

## Open items

- Transcribe Murray's 1924 Book 1 (archive.org `iliadmurray01homeuoft`, leaves 29-75) to replace Butler.
- Hermas 28-31 (fol. 347r-v, Q93_7r/7v) have Greek in the XML but no entries.
- `scripts/render_verified.py` (venetus branch) labels the Greek "Munro & Allen" and the edition text
  "Tischendorf"; it should read e.g. "Greek · Venetus A (Homer Multitext diplomatic edition)" and
  edition label "Munro & Allen (1920)"; translator comes from `verification.translator`.

## Catalog changes needed in data/texts.json (not made)

- Sinaiticus `scans.pages`: `data/sources/qc-sinaiticus-venetus/sinaiticus_texts_json_rows.json`.
  Caused by this QC: 2john-1 (use `1john-5-Q89_8r_B675.jpg`), sirach-31 (`sirach-35-Q69_8v_B358.jpg`
  first), sirach-32 (`sirach-31-Q70_1r_B359.jpg` first). The other 101 rows already pointed at a second
  copy of the right folio under another file name; they can switch to the file the sections use, after
  which the duplicate copies can be deleted.
- Venetus: all 24 rows, `source`, `description` and `scans.pages` (all pages, captions "Venetus A,
  fol. Nr"): `data/sources/qc-sinaiticus-venetus/venetus_texts_json_rows.json`.
