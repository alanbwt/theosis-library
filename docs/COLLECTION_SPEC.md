# Theosis Library — collection builder spec

Theosis Library (theosislibrary.com, repo `/Users/mattimore/projects/theosis-library`) is a static
reference library of ancient primary sources. **Every section of every entry shows three layers:**

1. a **photograph of the original source document** (tablet, stele, papyrus, scroll, wall, codex page)
   that carries exactly that section's text,
2. the **verbatim original-language text** of that section (from a named scholarly digital source),
3. a **verbatim English translation** of that section (from a named published translation).

This spec is the contract for anyone adding a collection. Read it fully before starting.

## The iron rules (each has been broken before; each break forced mass deletions)

1. **Never invent text.** Never write, paraphrase, machine-translate or "reconstruct" original-language
   text or English. Every character comes from a cited source. If a source has a gap, show the gap.
2. **Never put English (or a modern-language translation) in `original_text`.** If you have no real
   original-language text for a section, that section does not get published.
3. **Every section links to the specific image that shows its text.** A 40-page work is not illustrated
   by one "representative" page. If a text spans pages/columns/faces, each section points at the page(s)
   that carry it. A section that straddles two pages lists both.
4. **No estimated mappings.** Text-to-image mapping must come from (a) a documented source (catalogue,
   edition with folio/column/line references, project data such as eBL/CDLI/HMT/NTVMR/TLA), or
   (b) your own direct visual check of the image, recorded in `scan_note` (e.g. "checked on the image:
   column ii begins ‹first words›, ends ‹last words›"). Never interpolate pages by text length.
   The checker fails on the words estimated / approximate / proportional / roughly / assumed / guess
   in scan mapping fields and scan notes.
5. **Photographs of the original object only** as `scan_pages`. A modern hand copy, a printed edition,
   or a drawing is not a scan of the original. Photographic facsimile plates in old publications
   (collotype, heliogravure, photolithograph of the actual object) do count; say so in `scan_note`.
   If the only image of an object is a hand copy, skip the object or use a different witness.
6. **English translations must be public domain or openly licensed** (CC BY, CC BY-SA, CC BY-NC(-SA),
   explicit open-access terms). The site is public. Do not reproduce in-copyright translations
   (e.g. Lichtheim, Faulkner, Vermes, Jacobsen, Kramer, Allen, Lattimore, Loeb after 1929 unless
   verified PD). Check US copyright renewal (Stanford renewal DB, onlinebooks) for 1929-1963 works
   before treating them as PD. If no usable translation exists, do not publish the text; report it.
   Bible books use KJV (Douay-Rheims for Latin Vulgate).
   Recorded exception (owner's decision, 2026-11-12): the Tel Dan stele (13 lines, found 1993) uses the
   Biran and Naveh 1995 translation as quoted on Wikipedia, as a short scholarly quotation, because no
   open translation exists; its translation_license says so. No other exceptions.
7. **Show lacunae honestly.** Broken signs stay in brackets as the source gives them. If the English
   translates a restored or composite text that is not on the photographed witness, say so in the
   section's `scan_note`.
8. **Never get around access controls.** No CAPTCHA solving, no Cloudflare/bot-check bypass, no
   browser impersonation (curl-impersonate, TLS spoofing), no rate-limit evasion. If a site blocks
   automated access, use another source (Wikimedia Commons copies, archive.org, another library,
   another manuscript) or report the gap.
9. **Photograph licensing (owner's instruction, 2026-11-12):** the library is non-commercial and the
   owner accepts restrictive or unstated photo terms. Museum, library and scholarly photographs of the
   ancient object may be used with credit even when the terms are non-commercial or unstated; record the
   terms as stated in `scan_license`. Translation licensing (rule 6) is unchanged.
10. **Cover the whole work.** Aim for the complete text of each work. Where one witness is incomplete,
   cover the gaps with other witnesses (other tablets, other manuscripts). State any remaining gaps
   in the introduction.

## Files you may write (and nothing else)

| Path | What |
|---|---|
| `scripts/import_<key>.py` | your importer, re-runnable, documents the chain of evidence in its docstring |
| `data/sources/<key>/` | downloaded source texts/caches (data only; never .py files) |
| `site/assets/scans/<key>/` | processed scan images (JPEG) |
| `translations/published/verified-<key>-*.json` | one JSON per entry |
| `data/collections/<key>.json` | collection config + catalog rows (+ optional authors, redirects) |
| `docs/collections/<key>.md` | short report: contents, sources, mapping method, gaps, open questions |

Do **not** edit `data/texts.json`, `data/authors.json`, any other script, the templates, CSS, or the
site pages; do not run the site build or deploy; do not `git commit`. The integrator merges collections.
Never save downloaded files into `scripts/` or the repo root. Run Python that parses downloaded files
from the repo root as `python3 scripts/import_<key>.py`.

Reserved legacy prefixes (do not reuse): `verified-sinaiticus-`, `verified-vaticanus-`, `verified-bezae-`,
`verified-alexandrinus-`, `verified-washingtonianus-`, `verified-leningrad-`, `verified-1qisaa-`,
`verified-dss-`, `verified-venetus-`, `verified-edda-`, `verified-parisino-petropolitanus-`,
`verified-josephus-` (and `verified-gilgamesh-` unless you own the Gilgamesh rebuild).

## Entry JSON — `translations/published/verified-<key>-<slug>.json`

```json
{
  "id": "verified-<key>-<slug>",
  "slug": "verified-<key>-<slug>",
  "title": "Pyramid Texts of Unas: Utterances 213-219 (sarcophagus chamber, west wall)",
  "language": "Egyptian (transliteration) / English",
  "source": "one line: object + where the photo, the original text and the English come from",
  "description": "1-2 plain sentences for search results and social cards.",
  "introduction": "<p>What this text is, why it matters, what the object is, date, findspot, how the sections map to the images, gaps.</p>",
  "translator_notes": ["optional notes, plain sentences"],
  "translation": [
    {
      "section": "213",                         // unique within the entry; short (used in anchors)
      "original_ref": "PT 213 (§§134-135); W/F/W 1-6",
      "original_text": "<sup>1</sup>... verbatim original (HTML: <sup>, <br>, <span class=\"lacuna\">)",
      "text": "<sup>1</sup>... verbatim English",
      "scan_pages": ["<key>/unas-w-west-01.jpg"],   // relative to site/assets/scans/
      "scan_note": "Which part of the image shows this section and how the mapping was established.",
      "edition_text": "optional second original-language text (e.g. a critical edition when original_text is a diplomatic transcription); label it via collection.edition_label"
    }
  ],
  "verification": {
    "scan_source": "institution + URL(s) of the images",
    "scan_license": "license / terms as stated by the holder",
    "scan_manuscript": "shelfmark / museum number, date, provenance",
    "scan_mapping": "how text-to-image mapping was established (source or visual check)",
    "scan_mapping_urls": ["..."],
    "scan_local_paths": ["<key>/...jpg", "..."],
    "original_text_source": "edition + URL",
    "original_text_license": "...",
    "translation_source": "translator, title, year + URL of the copy used",
    "translation_license": "public domain (reason) / CC ...",
    "translator": "Short name shown on the page, e.g. 'E. A. Wallis Budge (1895)'",
    "verified_date": "YYYY-MM-DD"
  }
}
```

Section granularity: one section per mapping unit (a page, a column, a face, a group of lines on one
image), small enough that a reader can find the text on the image. Use `<sup>n</sup>` line/verse numbers
in BOTH original and English with the same numbering wherever the sources allow, so lines can be
matched. Keep HTML minimal (`<p>`, `<br>`, `<sup>`, `<em>`, `<span class="lacuna">`). No scripts.

## Images

- JPEG, long side 1600-2600 px, quality ~85, never upscaled, each file 10 KB-8 MB.
- Crop a multi-page spread to the one page; crop a huge object to the region holding the section,
  keeping enough margin to recognise it. Name files descriptively (`k3375-obv.jpg`, `f214v.jpg`).
- Prefer IIIF (`.../full/2000,/0/default.jpg` or a region) over full-resolution TIFF downloads.
- One file per distinct image; reuse the same file for every section on that page.
- Keep the total per collection reasonable (< ~1,500 files, < ~400 MB); the site deploys to
  Cloudflare Pages (25 MiB/file, 20,000 files total across the site).

## Collection file — `data/collections/<key>.json`

```json
{
  "collection": {
    "key": "<key>",
    "prefix": "verified-<key>-",
    "label": "Pyramid Texts of Unas",
    "group": "Egypt",            // one of SHELVES in scripts/collections_lib.py
    "date_sort": -2350,          // year (BCE negative) of the text/object, for shelf order
    "author_name": "Pyramid of Unas, Saqqara (c. 2350 BCE)",
    "source_url": "https://... canonical page for the object or manuscript",
    "critical_edition": "where the original text comes from (short)",
    "translator_name": "who made the English (short)",
    "original_lang_label": "Egyptian · TLA transliteration",
    "original_lang_code": "egy",  // grc, la, hbo, arc, akk, sux, egy, peo, ae, sa, lzh, gez, cop, phn, uga, hit
    "edition_label": "",
    "search_terms": "pyramid texts unas saqqara utterance",
    "description": "One paragraph for the library shelf."
  },
  "texts": [
    {
      "id": "verified-<key>-<slug>", "slug": "verified-<key>-<slug>", "order": 1,
      "title": "...", "author_id": "<author id>", "language": "Egyptian",
      "era": "Ancient Near East",   // Ancient Near East | Vedic | Old Testament | Axial Age | Classical | Hellenistic | Second Temple | Late Republic | Imperial | Apostolic
      "tradition": "egyptian",       // egyptian, mesopotamian, sumerian, canaanite, jewish, persian, zoroastrian, hindu, vedic, taoist, confucian, chinese, greek, roman, christian, gnostic, ethiopian
      "category": "sacred-text",     // sacred-text | literature | law | history | inscription | philosophy | historical-witness
      "date_approx": "c. 2350 BCE (pyramid of Unas)", "century": -24,
      "source": "...", "description": "...",
      "themes": ["pyramid-texts", "unas", "afterlife", "verified"],
      "is_first_translation": false, "status": "published",
      "scans": {"pages": [{"file": "<key>/....jpg", "caption": "short caption"}]}
    }
  ],
  "authors": [
    {"id": "<author id>", "name": "...", "dates": "...", "century": -24, "era": "...", "tradition": "...",
     "language": "...", "bio": "one sentence"}
  ]
}
```

`order` sets prev/next reading order inside the collection (1..N, the work's natural order).

## Checking your work

```bash
python3 scripts/check_collection.py <key>      # must end with 0 hard failures
```

Then **look at the images**: open scans with the Read tool and confirm, for every entry (every page if
you mapped by eye), that the image shows the section's text (first and last words, line counts,
column). Record what you checked in `scan_note`. Write `docs/collections/<key>.md` with the contents
list, sources, mapping method, known gaps and anything uncertain.

When you finish, report: entries and sections built, what is complete vs partial, every gap and why,
anything you were unsure about, and the exact check_collection result.
