# corpus-hermeticum: Corpus Hermeticum I (Poimandres) and XIII (On Rebirth)

Importer: `scripts/import_corpus-hermeticum.py` (re-runnable; scans cached in `site/assets/scans/corpus-hermeticum/`).
Shelf: Greece. Era Imperial, tradition hermetic, category sacred-text, author `hermes-trismegistus` (already in authors.json).
2 entries, 54 sections (the standard sections of CH I and Parthey's 22 sections of CH XIII).

## Contents

| order | entry | sections | manuscript pages |
|---|---|---|---|
| 1 | `verified-corpus-hermeticum-poimandres` (CH I, complete) | 32 | Laur. Plut. 71.33 fol. 123r-125v (6 pages) |
| 2 | `verified-corpus-hermeticum-on-rebirth` (CH XIII, complete, with the secret hymn) | 22 | Laur. Plut. 71.33 fol. 141v-144r (6 pages) |

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
- sacred-texts.com is behind a Cloudflare block; not used.

## CH XIII (added 2026-11-12)

- Manuscript: the same Laur. Plut. 71.33. CH XIII begins in the middle of fol. 141v under a red title that lacks Parthey's words 'ἐν ὄρει λόγος ἀπόκρυφος' (Mead's commentary notes that A has no main title) and ends in the middle of fol. 144r, followed on the same line by the red title of CH XIV. The hymn has the red heading 'ὑμνῳδία' on fol. 143v. First and last lines of all six pages read on the images; all page joins checked. Sections crossing a page: 2, 6, 10, 15, 19.
- Greek: Parthey 1854, cap. 13, pp. 114-128. Not on Wikisource and the archive.org OCR of the Greek is unusable, so the 15 pages were transcribed from the page images of `poemander00trisgoog` (leaves 140-154, 1600 px; two words checked at 3000 px: 'ἁμαρτήσεις' p. 123 and 'θεὲ,' p. 127, the latter printed with a grave) and each line was proofread against the image. The transcription keeps Parthey's line breaks, page numbers and marginal section numbers: `data/sources/corpus-hermeticum/parthey/parthey1854-ch13.txt`. Speaker names (Τάτ., Ἑρμῆς.) as printed. Pen marks of a former reader on the scan (underlines on pp. 116, 117, 124, 126) are not part of the print.
- English: Mead, Thrice-Greatest Hermes vol. 2, pp. 219-233. Toronto OCR compared with the OCRs of two other scans of the same printing; OCR faults fixed in `FIX13_ENG` (Rebirth, Race, Rashness, Righteousness, Receive, Æon, O for 0, stray footnote numbers, a footnote from p. 229 that runs onto p. 230). The four lacunae marked with dots were checked on the page images (pp. 222, 224, 225).
- Section numbering: Mead follows Reitzenstein, whose sections 8, 9 and 19 begin one or two sentences away from Parthey's (Parthey 8 'ἀφίστανται δὲ αὗται', 9 'δύναμιν καλῶ ἐπὶ χαρᾷ', 19 'ταῦτα βοῶσιν'). Sections here follow Parthey; the English is cut at the words that translate those openings ('But they depart', 'The Power that follows Joy', 'Thus cry the Powers in me'), and Mead's numerals are dropped.
- Open: Mead translated Reitzenstein's text, so some phrases have no exact counterpart in Parthey (e.g. section 2, where Parthey reads 'σοφία νοερὰ ἐν σιγῇ' and Mead adds in brackets 'such is the matter and the womb').
