#!/usr/bin/env python3
"""
import_p45.py: P45 (Chester Beatty Biblical Papyrus I, with the Vienna fragment
Pap. G. 31974), the Gospels and Acts, 3rd century. One section per page side,
one entry per chapter in which a page begins; 60 pages.

Chain of evidence
  1. GREEK    NTVMR (INTF Muenster) page transcriptions of GA P45 (docID 10045),
              64 page files, every one headed "Creative Commons Attribution 4.0".
              Cached in data/sources/p45/ntvmr/10045/. Rendering: import_p52.py.
  2. SCANS    The photographs NTVMR links to each page in its page index
              (meta-10045.json), served publicly (accessLevel 0) from
              https://ntmss.info/images/webfriendly/10045/<file>:
              Chester Beatty Library photographs ("Images © The Trustees of the
              Chester Beatty Library") and, for folio 2, also the Austrian National
              Library's photograph of Pap. G. 31974 ("Images © ÖNB"). Downloaded
              and reduced to 2400 px on the long side. Not used: the Chester Beatty
              online viewer (its IIIF API refused automated access).
  3. MAPPING  NTVMR's page index (folio -> image file). Every page was checked on
              the image (data/sources/p45/visual_check.json, quoted in each
              scan_note).
  4. ENGLISH  King James Version (eBible.org eng-kjv USFM, public domain).

Not built: NTVMR pages Br, Cr, Bv, Cv (John 4:51-5:2, 5:21-25; small fragments
with no image linked in NTVMR).

Usage (from the repo root):
    python3 -I scripts/import_p45.py [--force]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_p52 as L  # noqa: E402

KEY, DOC, PREFIX = "p45", 10045, "verified-p45-"
IMG = "https://ntmss.info/images/webfriendly/10045/{f}"
VIEW = "https://ntvmr.uni-muenster.de/community/modules/papyri/?site=VMR&image=10045/{pid}/10"
CBL = "https://viewer.cbl.ie/viewer/"

VARIANT_NOTES = {}


def page_images(p):
    im = p.get("images", {}).get("image") if p.get("images") else None
    im = [im] if isinstance(im, dict) else (im or [])
    out = []
    for x in im:
        u = x.get("uri", "")
        if "ntmss.info" in u and x.get("accessLevel") == 0:
            fn = u.split("/10045/")[-1]
            who = "ÖNB" if "OENB" in fn else "Chester Beatty Library"
            out.append((fn, who))
    # Chester Beatty leaf first, Vienna fragment second
    out.sort(key=lambda t: t[1] != "Chester Beatty Library")
    return out


INTRO_COMMON = (
    "<p>P45 is a papyrus codex of the four Gospels and Acts copied in Egypt in the 3rd century, the oldest surviving "
    "book to have held all four Gospels together. It was bought by Alfred Chester Beatty in the early 1930s and "
    "published by Frederic Kenyon in 1933; the leaves are in the Chester Beatty Library, Dublin (Biblical Papyrus I), "
    "and a small piece of Matthew 25-26 is in the Austrian National Library, Vienna (Pap. G. 31974). About 30 damaged "
    "leaves survive out of some 220: parts of Matthew 20-26, Mark 4-12, Luke 6-14, John 4-5 and 10-11, and Acts 4-17. "
    "The order of the Gospels in the codex was Matthew, John, Luke, Mark, Acts; the folio numbers used here are those "
    "of the NTVMR transcription, which follows the order of the books in printed Bibles.</p>\n\n"
    "<p>Each section below is one page side: the Chester Beatty Library's photograph, the NTVMR diplomatic transcription "
    "line by line, and the King James Version of every verse that has text on the page. Most lines are broken at "
    "both ends; the transcribers' restorations are in square brackets. Verses that P45 does not have (Luke 12:9, "
    "Acts 8:37) are noted on their pages.</p>"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    checks = L.load_checks(KEY)
    scan_dir = L.SCANS / KEY
    pages, skipped = [], []
    for p in L.ntvmr_pages(KEY, DOC):
        if not p.get("transcriptions"):
            continue
        fol = (p.get("folio") or "").strip()
        imgs = page_images(p)
        if not imgs:
            skipped.append(fol)
            continue
        files = []
        for j, (fn, who) in enumerate(imgs):
            f = f"p45-f{fol}.jpg" if j == 0 else f"p45-f{fol}-vienna.jpg"
            L.get_image(scan_dir / f, IMG.format(f=fn), force=a.force)
            files.append(f)
        src = "; ".join(f"{who} photograph {fn} ({IMG.format(f=fn)})" for fn, who in imgs)
        spec = {"pid": p["pageID"], "sec": f"f{fol}", "folio": fol, "file": files[0], "files": files,
                "ref_label": f"P45 fol. {fol}",
                "scan_note": (f"{src}, linked to NTVMR page {p['pageID']} (folio {fol}) in NTVMR's page index"
                              + ("; the first image is the Chester Beatty leaf, the second the Vienna fragment of the same page"
                                 if len(files) > 1 else "") + ".")}
        pages.append(L.build_page(KEY, DOC, spec))
    print("skipped (no image):", skipped)
    # Only pages whose image has been checked by eye are published (none yet: see docs/collections/p45.md).
    unchecked = [pg["sec"] for pg in pages if pg["sec"] not in checks]
    if unchecked:
        print(f"not published (no visual check recorded yet, {len(unchecked)}):", " ".join(unchecked))
    pages = [pg for pg in pages if pg["sec"] in checks]
    if not pages:
        print("nothing to publish")
        return

    rows, keep = [], set()
    for order, grp in enumerate(L.group_pages_by_chapter(pages), 1):
        b, k, _ = grp[0]["verses"][0]
        slug = f"{PREFIX}{L.BOOK_SLUG[b]}-{k}"
        rng = L.entry_range_title(grp)
        ff = f"fol. {grp[0]['folio']}" if len(grp) == 1 else f"fols. {grp[0]['folio']}-{grp[-1]['folio']}"
        title = f"P45 (Chester Beatty I): {rng} ({ff})"
        sections = [L.make_section(KEY, pg, checks.get(pg["sec"], ""), VARIANT_NOTES.get(pg["sec"], "")) for pg in grp]
        desc = (f"{rng} in P45 (Chester Beatty Biblical Papyrus I), the 3rd-century papyrus codex of the Gospels and Acts: "
                f"{ff}, each page with its photograph, the Greek transcription and the King James Version.")
        has_vienna = any(len(pg["files"]) > 1 for pg in grp)
        entry = {
            "id": slug, "slug": slug, "title": title,
            "language": "Greek (NTVMR transcription) / English (KJV)",
            "source": ("Chester Beatty Biblical Papyrus I (P45), Chester Beatty Library, Dublin"
                       + (", and Pap. G. 31974, Austrian National Library" if has_vienna else "")
                       + ": photographs as published in the INTF New Testament Virtual Manuscript Room; Greek from the "
                         "INTF NTVMR transcription of P45; English from the King James Version"),
            "description": desc,
            "introduction": INTRO_COMMON + f"\n\n<p>This entry covers {ff} ({rng}).</p>",
            "translator_notes": [L.GREEK_NOTE, L.ENGLISH_NOTE],
            "translation": sections,
            "verification": {
                "scan_source": ("Chester Beatty Library, Dublin (and Austrian National Library for Pap. G. 31974), photographs "
                                "served by the INTF New Testament Virtual Manuscript Room at https://ntmss.info/images/webfriendly/10045/ "
                                "and linked to each page in the NTVMR page index"),
                "scan_license": ("Images © The Trustees of the Chester Beatty Library" + ("; Images © ÖNB" if has_vienna else "")
                                 + " (attribution as given in the NTVMR page index; no other terms stated); reproduced with "
                                   "credit for non-commercial reference use"),
                "scan_manuscript": ("Dublin, Chester Beatty Library, Biblical Papyrus I (CBL BP I)"
                                    + (" + Vienna, Österreichische Nationalbibliothek, Pap. G. 31974" if has_vienna else "")
                                    + "; Gregory-Aland P45; papyrus codex, 3rd century, Egypt"),
                "scan_mapping": "NTVMR page index links each folio to its photograph; every page checked on the image",
                "scan_mapping_urls": [L.META_URL.format(doc=DOC)] + [VIEW.format(pid=pg["pid"]) for pg in grp],
                "scan_local_paths": [f"{KEY}/{f}" for pg in grp for f in pg["files"]],
                "original_text_source": ("INTF, New Testament Virtual Manuscript Room, transcription of GA P45 (docID 10045), pages "
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
            "id": slug, "slug": slug, "order": order, "title": title, "author_id": "p45-scribe",
            "language": "Greek", "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": "3rd century AD (NTVMR: 200-299)", "century": 3,
            "source": entry["source"], "description": desc,
            "themes": ["new-testament", "papyrus", "p45", "chester-beatty", L.BOOK_SLUG[b], "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{f}", "caption": f"P45 fol. {pg['folio']}"} for pg in grp for f in pg["files"]]},
        })
        print(f"  {slug}: {title}, {len(sections)} sections")
    L.remove_stale(PREFIX, keep)
    collection = {
        "key": KEY, "prefix": PREFIX, "label": "P45 (Chester Beatty I)", "group": "New Testament",
        "date_sort": 250,
        "author_name": "Papyrus P45, Egypt (3rd century AD)",
        "source_url": "https://ntvmr.uni-muenster.de/manuscript-workspace?docID=10045",
        "critical_edition": "INTF NTVMR diplomatic transcription (CC BY 4.0)",
        "translator_name": "King James Version (1611)",
        "original_lang_label": "Greek · NTVMR transcription",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "p45 chester beatty papyrus gospels acts matthew mark luke john",
        "description": "The oldest book of the four Gospels and Acts: the damaged 3rd-century papyrus codex P45 in the Chester Beatty Library, page by page.",
    }
    authors = [{"id": "p45-scribe", "name": "Papyrus P45 (scribe)", "dates": "3rd century AD", "century": 3,
                "era": "Apostolic", "tradition": "christian", "language": "Greek",
                "bio": "Unknown Egyptian scribe of the papyrus codex of the Gospels and Acts now in the Chester Beatty Library, Dublin."}]
    L.write_collection(KEY, collection, rows, authors)
    print(f"wrote {len(rows)} entries, {len(pages)} pages")


if __name__ == "__main__":
    main()
