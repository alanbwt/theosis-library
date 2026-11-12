#!/usr/bin/env python3
"""
import_p46.py: P46, the papyrus codex of the letters of Paul (Chester Beatty
Biblical Papyrus II + University of Michigan P.Mich. inv. 6238), c. 200. One
section per page side, one entry per chapter in which a page begins.

Chain of evidence
  1. GREEK    NTVMR (INTF Muenster) page transcriptions of GA P46 (docID 10046),
              172 page files, every one headed "Creative Commons Attribution 4.0".
              Cached in data/sources/p46/ntvmr/10046/. Rendering: import_p52.py.
  2. SCANS    The photographs NTVMR links to each page in its page index
              (meta-10046.json), served publicly (accessLevel 0) from
              https://ntmss.info/images/webfriendly/10046/<file>: Chester Beatty
              Library photographs (files T000....jpg; attribution "Chester Beatty
              Library") for the Dublin leaves, University of Michigan Library
              photographs (files 10046x6238_..._UMich.jpg; attribution "University of
              Michigan Library") for the Ann Arbor leaves. Where NTVMR also links an
              INTF image (10046_NNN_INTF.jpg) the holding library's photograph is
              used. Reduced to 2400 px on the long side. Not used: the U-M APIS
              server and CSNTM's IIIF server (the first answered with a bot
              challenge, the second returned empty or broken images).
  3. MAPPING  NTVMR's page index (folio -> image file). Every page was checked on
              the image (data/sources/p46/visual_check.json, quoted in each
              scan_note).
  4. ENGLISH  King James Version (eBible.org eng-kjv USFM, public domain).

Usage (from the repo root):
    python3 -I scripts/import_p46.py [--force]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_p52 as L  # noqa: E402

KEY, DOC, PREFIX = "p46", 10046, "verified-p46-"
IMG = "https://ntmss.info/images/webfriendly/10046/{f}"
VIEW = "https://ntvmr.uni-muenster.de/community/modules/papyri/?site=VMR&image=10046/{pid}/10"
CBL = "https://viewer.cbl.ie/viewer/"

VARIANT_NOTES = {}


def page_images(p):
    """The holding library's photograph for the page (Chester Beatty or Michigan)."""
    im = p.get("images", {}).get("image") if p.get("images") else None
    im = [im] if isinstance(im, dict) else (im or [])
    out = []
    for x in im:
        u = x.get("uri", "")
        if "ntmss.info" in u and x.get("accessLevel") == 0:
            fn = u.split("/10046/")[-1]
            if fn.endswith("_INTF.jpg"):
                continue
            who = "University of Michigan Library" if "UMich" in fn else "Chester Beatty Library"
            out.append((fn, who))
    return out[:1]


INTRO_COMMON = (
    "<p>P46 is a papyrus codex of the letters of Paul copied in Egypt around 200, the oldest surviving collection of "
    "Paul's letters. 86 of its 104 leaves survive: 56 in the Chester Beatty Library, Dublin (Biblical Papyrus II, "
    "published by Frederic Kenyon in 1934-1937) and 30 in the University of Michigan Library, Ann Arbor (P.Mich. inv. "
    "6238, published by Henry Sanders in 1935). The letters run in the order Romans, Hebrews, 1 and 2 Corinthians, "
    "Ephesians, Galatians, Philippians, Colossians and 1 Thessalonians; the first seven leaves (Romans 1:1-5:17) and the "
    "end of the book are lost. Hebrews standing after Romans, and the doxology of Romans (16:25-27) standing after "
    "15:33, are among its best-known features.</p>\n\n"
    "<p>Each section below is one page side: the holding library's photograph, the NTVMR diplomatic transcription line "
    "by line, and the King James Version of every verse that has text on the page. The lower lines of many leaves "
    "are lost; the transcribers' restorations are in square brackets.</p>"
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
        fol = (p.get("folio") or "").strip().lstrip("0")
        imgs = page_images(p)
        if not imgs:
            skipped.append(fol)
            continue
        files = []
        for j, (fn, who) in enumerate(imgs):
            f = f"p46-f{fol}.jpg"
            L.get_image(scan_dir / f, IMG.format(f=fn), force=a.force)
            files.append(f)
        src = "; ".join(f"{who} photograph {fn} ({IMG.format(f=fn)})" for fn, who in imgs)
        spec = {"pid": p["pageID"], "sec": f"f{fol}", "folio": fol, "file": files[0], "files": files,
                "ref_label": f"P46 fol. {fol}",
                "scan_note": f"{src}, linked to NTVMR page {p['pageID']} (folio {fol}) in NTVMR's page index.",
                "holder": imgs[0][1]}
        pages.append(L.build_page(KEY, DOC, spec))
    print("skipped (no image):", skipped)
    # Only pages whose image has been checked by eye are published.
    unchecked = [pg["sec"] for pg in pages if pg["sec"] not in checks]
    if unchecked:
        print(f"not published (no visual check recorded yet, {len(unchecked)}):", " ".join(unchecked))
    pages = [pg for pg in pages if pg["sec"] in checks]

    rows, keep = [], set()
    for order, grp in enumerate(L.group_pages_by_chapter(pages), 1):
        b, k, _ = grp[0]["verses"][0]
        slug = f"{PREFIX}{L.BOOK_SLUG[b]}-{k}"
        rng = L.entry_range_title(grp)
        ff = f"fol. {grp[0]['folio']}" if len(grp) == 1 else f"fols. {grp[0]['folio']}-{grp[-1]['folio']}"
        hold = sorted({pg["holder"] for pg in grp})
        tag = " + ".join("Chester Beatty II" if h.startswith("Chester") else "P.Mich. inv. 6238" for h in hold)
        title = f"P46 ({tag}): {rng} ({ff})"
        sections = [L.make_section(KEY, pg, checks.get(pg["sec"], ""), VARIANT_NOTES.get(pg["sec"], "")) for pg in grp]
        desc = (f"{rng} in P46, the papyrus codex of Paul's letters copied around 200: "
                f"{ff}, each page with its photograph, the Greek transcription and the King James Version.")
        cbl = any(h.startswith("Chester") for h in hold); um = any(h.startswith("University") for h in hold)
        entry = {
            "id": slug, "slug": slug, "title": title,
            "language": "Greek (NTVMR transcription) / English (KJV)",
            "source": ("P46 (" + " and ".join((["Chester Beatty Biblical Papyrus II, Chester Beatty Library, Dublin"] if cbl else [])
                                              + (["P.Mich. inv. 6238, University of Michigan Library"] if um else []))
                       + "): photographs as published in the INTF New Testament Virtual Manuscript Room; Greek from the "
                         "INTF NTVMR transcription of P46; English from the King James Version"),
            "description": desc,
            "introduction": INTRO_COMMON + f"\n\n<p>This entry covers {ff} ({rng}).</p>",
            "translator_notes": [L.GREEK_NOTE, L.ENGLISH_NOTE],
            "translation": sections,
            "verification": {
                "scan_source": (" and ".join((["Chester Beatty Library, Dublin"] if cbl else []) + (["University of Michigan Library, Ann Arbor"] if um else []))
                                + ": photographs served by the INTF New Testament Virtual Manuscript Room at "
                                  "https://ntmss.info/images/webfriendly/10046/ and linked to each page in the NTVMR page index"),
                "scan_license": ("; ".join((["Images © The Trustees of the Chester Beatty Library"] if cbl else [])
                                           + (["Images: University of Michigan Library"] if um else []))
                                 + " (attribution as given in the NTVMR page index; no other terms stated); reproduced with "
                                   "credit for non-commercial reference use"),
                "scan_manuscript": ("; ".join((["Dublin, Chester Beatty Library, Biblical Papyrus II (CBL BP II)"] if cbl else [])
                                              + (["Ann Arbor, University of Michigan Library, P.Mich. inv. 6238"] if um else []))
                                    + "; Gregory-Aland P46; papyrus codex, c. 200 (NTVMR: 200-225), Egypt"),
                "scan_mapping": "NTVMR page index links each folio to its photograph; every page checked on the image",
                "scan_mapping_urls": [L.META_URL.format(doc=DOC)] + [VIEW.format(pid=pg["pid"]) for pg in grp],
                "scan_local_paths": [f"{KEY}/{f}" for pg in grp for f in pg["files"]],
                "original_text_source": ("INTF, New Testament Virtual Manuscript Room, transcription of GA P46 (docID 10046), pages "
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
            "id": slug, "slug": slug, "order": order, "title": title, "author_id": "p46-scribe",
            "language": "Greek", "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": "c. 200 AD (NTVMR: 200-225)", "century": 3,
            "source": entry["source"], "description": desc,
            "themes": ["new-testament", "papyrus", "p46", "paul", L.BOOK_SLUG[b], "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{f}", "caption": f"P46 fol. {pg['folio']}"} for pg in grp for f in pg["files"]]},
        })
        print(f"  {slug}: {title}, {len(sections)} sections")
    L.remove_stale(PREFIX, keep)
    collection = {
        "key": KEY, "prefix": PREFIX, "label": "P46 (Chester Beatty II + Michigan)", "group": "New Testament",
        "date_sort": 200,
        "author_name": "Papyrus P46, Egypt (c. 200 AD)",
        "source_url": "https://ntvmr.uni-muenster.de/manuscript-workspace?docID=10046",
        "critical_edition": "INTF NTVMR diplomatic transcription (CC BY 4.0)",
        "translator_name": "King James Version (1611)",
        "original_lang_label": "Greek · NTVMR transcription",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "p46 chester beatty michigan papyrus paul romans hebrews corinthians ephesians galatians philippians colossians thessalonians",
        "description": "The oldest collection of Paul's letters: the papyrus codex P46 (c. 200), split between Dublin and Ann Arbor, page by page.",
    }
    authors = [{"id": "p46-scribe", "name": "Papyrus P46 (scribe)", "dates": "c. 200 AD", "century": 3,
                "era": "Apostolic", "tradition": "christian", "language": "Greek",
                "bio": "Unknown Egyptian scribe of the papyrus codex of Paul's letters now divided between the Chester Beatty Library and the University of Michigan."}]
    L.write_collection(KEY, collection, rows, authors)
    print(f"wrote {len(rows)} entries, {len(pages)} pages")


if __name__ == "__main__":
    main()
