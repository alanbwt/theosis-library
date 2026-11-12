# corpus-hermeticum: Corpus Hermeticum I (Poimandres)

Importer: `scripts/import_corpus-hermeticum.py` (re-runnable; scans cached in `site/assets/scans/corpus-hermeticum/`).
Shelf: Greece. Era Imperial, tradition hermetic, category sacred-text, author `hermes-trismegistus` (already in authors.json).
1 entry, 32 sections (the standard sections of CH I).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-corpus-hermeticum-poimandres` (CH I, complete) | 32 | Laur. Plut. 71.33 fol. 123r-125v (6 pages) |

## Sources

- Scans: Florence, BML, Plut. 71.33 (14th c., paper; siglum A, the oldest witness of the Corpus), Teca digitale IIIF via CONTENTdm (`cdm21059.contentdm.oclc.org`, item 1210396), 1800 px. Access marked 'Pubblico', no licence stated; used with credit (spec rule 9). Hermetica on fols. 123-145v (Pinakes 16627).
- Greek: G. Parthey, Hermetis Trismegisti Poemander (Berlin 1854), pp. 1-18, from the Greek Wikisource transcription (pages djvu/25-42, all at proofread level 3; wikitext and revision ids cached in `data/sources/corpus-hermeticum/wikisource-parthey-pp24-43.json`). Templates resolved by the importer, including words split across pages (`σλβα`/`σλβτ`).
- English: G. R. S. Mead, Thrice-Greatest Hermes vol. 2 (1906), pp. 3-20, public domain. OCR of archive.org `thricegreatesthe02hermuoft`; page heads, footnotes and footnote numbers removed by the importer.

## Text checks

- English: the cleaned OCR was compared word by word with the OCR of a second scan of the same printing (`thricegreatesth02meadgoog`); each difference was settled with the gnosis.org transcription (which modernises Mead in places, so it was used only to break ties) and the fixes are listed in `FIX_ENG` (Reason, Æther, Right, Rashness, gavest, happen'st, and one leaked footnote block). Line-end hyphens: kept when the second part is capitalised (Man-Shepherd) or the hyphenated form occurs in the gnosis.org text (all-masterhood, de-energized); otherwise joined.
- Greek: relies on Wikisource's proofreading; not re-proofread against the 1854 page images here (Wikimedia rate-limited the API during this session).

## Mapping method

First and last lines of every page read on the image and matched to Parthey's Greek, with the end of each page checked against the start of the next (all five page joins agree). Fol. 125v: the treatise ends on line 22, followed by the red title of the next treatise; the line where sections 30, 31 and 32 begin is recorded.

## Notes and gaps

- Parthey's Greek differs from the manuscript and from Reitzenstein/Nock in places; in sections 4-5 the manuscript has blank spaces where its exemplar was defective. Mead translated Reitzenstein's text (1904), so a few phrases in the English have no exact counterpart in Parthey's Greek.
- Not built: CH XIII (the rebirth dialogue). Greek Wikisource has transcribed only the opening part of Parthey's book (djvu pages 1-57 and 159-162), not CH XIII; the only digital PD Greek found is Walter Scott's 1924 text in First1KGreek (`tlg1286.tlg013`), which rearranges and brackets the text heavily and still has OCR errors, so it cannot be mapped to the manuscript reliably. A transcription of Parthey's (or Reitzenstein's 1904) CH XIII from the page scans is needed. Mead's English for CH XIII is in the same OCR file (line ~9408, "1. Tat. [Now] in the General Sermons"); in Laur. 71.33 CH XIII lies within fols. 126-145v (not yet located).
- sacred-texts.com is behind a Cloudflare block; not used.
