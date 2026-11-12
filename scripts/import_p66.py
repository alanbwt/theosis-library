#!/usr/bin/env python3
"""
import_p66.py: P66 (Papyrus Bodmer II, with the Chester Beatty and Cologne
fragments transcribed with it), the Gospel of John, c. 200. One section per
papyrus page, one entry per chapter (pages grouped by the chapter in which they
begin), 148 pages (John 1:1-21:9 with gaps).

Chain of evidence
  1. GREEK    NTVMR (INTF Muenster) page transcriptions of GA P66 (docID 10066),
              148 pages (pageID 10-1480), every file headed "Creative Commons
              Attribution 4.0". Cached in data/sources/p66/ntvmr/10066/.
              Rendering: import_p52.py. Two files have a broken verse id where
              some letters were typed into the id attribute (page 120, John 16:29,
              id "B04K16V[νυν"; page 128, John 18:16, id "B04K18Vω̣σ̣"): the text that
              follows is kept with the preceding verse and the defect is noted on
              the page.
  2. SCANS    Fondation Martin Bodmer, Bodmer Lab (Université de Genève), PB 2
              (barcode 1072205287), IIIF manifest
              https://bodmerlab.unige.ch/fr/constellations/papyri/manifest/1072205287
              (cached data/sources/p66/bodmer/), licence CC BY-NC 4.0. Pages still in
              the bound book block (John 1:1-14:26) are shown on the photographic
              plates of V. Martin and J. W. B. Barns, Papyrus Bodmer II, Supplément,
              nouvelle édition (Cologny-Genève 1962), as scanned by Bodmer Lab;
              the leaves kept between glass are shown in colour photographs.
              Images on the current server iiif.hedera.unige.ch.
  3. MAPPING  NTVMR's page index links every page (pageID) to its Bodmer Lab
              image (canvas index in the manifest, image 1072205287_NNN). Each plate
              also carries a printed caption with the verses ("I, 1-14";
              "PB II Evangile de Jean, supplément 20, 25-26"). Every page was checked
              on the image: caption and first and last legible lines compared with
              the transcription (data/sources/p66/visual_check.json, quoted in each
              scan_note).
  4. ENGLISH  King James Version (eBible.org eng-kjv USFM, public domain).

Usage (from the repo root):
    python3 -I scripts/import_p66.py [--force]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_p52 as L  # noqa: E402

KEY, DOC, PREFIX = "p66", 10066, "verified-p66-"
IMG = "https://iiif.hedera.unige.ch/iiif/2/bodmerlab/1072205287/1072205287_{n}.jpg"
MANIFEST = "https://bodmerlab.unige.ch/fr/constellations/papyri/manifest/1072205287"
VIEW = "https://bodmerlab.unige.ch/fr/constellations/papyri/mirador/1072205287"
PAGE = "https://bodmerlab.unige.ch/fr/constellations/papyri/barcode/1072205287"

DEFECT_NOTES = {
    "p120": ("The NTVMR file for this page is defective at John 16:29: some letters were typed into the verse "
             "identifier (\"B04K16V[νυν\") instead of the text, so the transcription jumps from ι]δ̣ε̣ at the end of "
             "line 1 to α̣ι παρο̣[ιμ]ιαν; the Greek shown follows the file."),
    "p128": ("The NTVMR file for this page is defective at John 18:16: the letters ω̣σ̣ of γνωστος were typed into the "
             "verse identifier (\"B04K18Vω̣σ̣\"), so the word appears as γν τος; the Greek shown follows the file."),
}
VARIANT_NOTES = {
    "p2": "John 1:18: P66 reads μονογενης θ̅ς̅ (θεος, \"God\") where the KJV has \"the only begotten Son\".",
}


def image_number(page_meta):
    im = page_meta.get("images", {}).get("image") if page_meta.get("images") else None
    im = [im] if isinstance(im, dict) else (im or [])
    for x in im:
        u = x.get("uri", "")
        if u.startswith("iiif://"):
            return re.search(r"_(\d{3})$", u.split("|")[3]).group(1)
    return None


INTRO_COMMON = (
    "<p>P66 is a papyrus codex of the Gospel of John copied in Egypt around 200, the most complete early copy of John. "
    "Most of it is Papyrus Bodmer II in the Fondation Martin Bodmer, Cologny (Geneva); small pieces are in the Chester "
    "Beatty Library, Dublin, and the Institut für Altertumskunde, Cologne. The first five quires (John 1:1-14:26) "
    "survive as a bound book of numbered pages; later leaves, from John 14:29 to 21:9, are damaged and kept between "
    "glass. The scribe made many corrections, some of them his own; only the first hand is shown here.</p>\n\n"
    "<p>Each section below is one page: the photograph, the NTVMR diplomatic transcription line by line, and the King "
    "James Version of every verse on the page. Pages of the bound book are shown on the photographic plates published "
    "by Victor Martin and J. W. B. Barns in 1962 (scanned by the Bodmer Lab), the glass-mounted leaves on colour "
    "photographs. Lost: John 6:12-34 (pages 35-38) and parts of chapters 14-21; the transcription ends at 21:9. Where "
    "P66 lacks a verse that the KJV has (John 5:4, the account of the adulteress at 7:53-8:11, 16:15), the section "
    "says so.</p>"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    checks = L.load_checks(KEY)
    scan_dir = L.SCANS / KEY
    pages = []
    for p in L.ntvmr_pages(KEY, DOC):
        if not p.get("transcriptions"):
            continue
        page = int(p["folio"])
        n = image_number(p)
        f = f"p66-p{page:03d}.jpg"
        L.get_image(scan_dir / f, f"{IMG.format(n=n)}/full/,2400/0/default.jpg", force=a.force)
        plate = "photographic plate of the 1962 Martin-Barns edition" if page <= 108 else "colour photograph of the glass-mounted leaf"
        spec = {"pid": p["pageID"], "sec": f"p{page}", "page": page, "file": f, "img": n,
                "ref_label": f"P66 page {page}",
                "scan_note": (f"Fondation Martin Bodmer, Papyrus Bodmer II, Bodmer Lab image 1072205287_{n} ({VIEW}), "
                              f"{plate}, shown whole. NTVMR page {p['pageID']} (page {page}) is linked to this image in "
                              "NTVMR's page index.")}
        pages.append(L.build_page(KEY, DOC, spec))
    missing = [pg["sec"] for pg in pages if pg["sec"] not in checks]
    if missing:
        print("WARNING: no visual check recorded for", missing)

    rows, keep = [], set()
    for order, grp in enumerate(L.group_pages_by_chapter(pages), 1):
        b, k, _ = grp[0]["verses"][0]
        slug = f"{PREFIX}{L.BOOK_SLUG[b]}-{k}"
        rng = L.entry_range_title(grp)
        pp = f"page {grp[0]['page']}" if len(grp) == 1 else f"pages {grp[0]['page']}-{grp[-1]['page']}"
        title = f"P66 (Papyrus Bodmer II): {rng} ({pp})"
        sections = []
        for pg in grp:
            extra = " ".join(x for x in (DEFECT_NOTES.get(pg["sec"], ""), VARIANT_NOTES.get(pg["sec"], "")) if x)
            sections.append(L.make_section(KEY, pg, checks.get(pg["sec"], ""), extra))
        desc = (f"{rng} in P66 (Papyrus Bodmer II), the papyrus codex of John copied around 200: {pp}, each with its "
                "photograph, the Greek transcription and the King James Version.")
        intro = INTRO_COMMON + f"\n\n<p>This entry covers {pp} ({rng}).</p>"
        entry = {
            "id": slug, "slug": slug, "title": title,
            "language": "Greek (NTVMR transcription) / English (KJV)",
            "source": ("Papyrus Bodmer II (P66), Fondation Martin Bodmer: images from the Bodmer Lab, University of Geneva; "
                       "Greek from the INTF NTVMR transcription of P66; English from the King James Version"),
            "description": desc,
            "introduction": intro,
            "translator_notes": [L.GREEK_NOTE, L.ENGLISH_NOTE],
            "translation": sections,
            "verification": {
                "scan_source": f"Fondation Martin Bodmer, Bodmer Lab (Université de Genève), PB 2 ({PAGE}; IIIF manifest {MANIFEST})",
                "scan_license": "CC BY-NC 4.0 (IIIF manifest licence; attribution: Fondation Martin Bodmer, numérisation Bodmer Lab, UNIGE)",
                "scan_manuscript": ("Cologny, Fondation Martin Bodmer, Papyrus Bodmer II (with Dublin, Chester Beatty Library, and "
                                    "Cologne fragments); Gregory-Aland P66; papyrus codex, c. 200 (NTVMR: 200-225), Egypt. "
                                    "Pages 1-108 shown on the photographic plates of Martin and Barns, Papyrus Bodmer II, "
                                    "Supplément (1962); later leaves in colour photographs."),
                "scan_mapping": ("NTVMR page index links each page to its Bodmer Lab image; the printed caption on each plate "
                                 "names the verses; first and last legible lines of every page read on the images"),
                "scan_mapping_urls": [L.META_URL.format(doc=DOC), MANIFEST],
                "scan_local_paths": [f"{KEY}/{pg['file']}" for pg in grp],
                "original_text_source": ("INTF, New Testament Virtual Manuscript Room, transcription of GA P66 (docID 10066), pages "
                                         + ", ".join(str(pg["pid"]) for pg in grp) + ": "
                                         + L.TRANSCRIPT_URL.format(doc=DOC, pid=grp[0]["pid"])),
                "original_text_license": "CC BY 4.0 (Institut fuer Neutestamentliche Textforschung, as stated in each page file)",
                "translation_source": "King James Version (1611), eBible.org eng-kjv USFM",
                "translation_license": "public domain",
                "translator": "King James Version (1611)",
                "verified_date": L.TODAY,
            },
        }
        L.write_entry(entry)
        keep.add(slug)
        rows.append({
            "id": slug, "slug": slug, "order": order, "title": title, "author_id": "p66-scribe",
            "language": "Greek", "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": "c. 200 AD (NTVMR: 200-225)", "century": 3,
            "source": entry["source"], "description": desc,
            "themes": ["new-testament", "papyrus", "p66", "bodmer-papyri", "gospel-of-john", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{pg['file']}", "caption": f"P66 page {pg['page']}"} for pg in grp]},
        })
        print(f"  {slug}: {title}, {len(sections)} sections")
    L.remove_stale(PREFIX, keep)
    collection = {
        "key": KEY, "prefix": PREFIX, "label": "P66 (Papyrus Bodmer II)", "group": "New Testament",
        "date_sort": 200,
        "author_name": "Papyrus P66, Egypt (c. 200 AD)",
        "source_url": PAGE,
        "critical_edition": "INTF NTVMR diplomatic transcription (CC BY 4.0)",
        "translator_name": "King James Version (1611)",
        "original_lang_label": "Greek · NTVMR transcription",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "p66 papyrus bodmer ii gospel of john",
        "description": "The most complete early copy of the Gospel of John: the papyrus codex P66 (c. 200), page by page from the Bodmer Foundation.",
    }
    authors = [{"id": "p66-scribe", "name": "Papyrus P66 (scribe)", "dates": "c. 200 AD", "century": 3,
                "era": "Apostolic", "tradition": "christian", "language": "Greek",
                "bio": "Unknown Egyptian scribe of the papyrus codex of John now in the Bodmer Foundation, who corrected his own copy many times."}]
    L.write_collection(KEY, collection, rows, authors)
    print(f"wrote {len(rows)} entries, {len(pages)} pages")


if __name__ == "__main__":
    main()
