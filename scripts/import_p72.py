#!/usr/bin/env python3
"""
import_p72.py: P72, the papyrus codex of 1 Peter, 2 Peter and Jude (Papyrus
Bodmer VIII and VII, 3rd/4th century). One section per papyrus page, one entry
per chapter (pages grouped by the chapter in which they begin), 43 pages.

Chain of evidence
  1. GREEK    NTVMR (INTF Muenster) page transcriptions of GA P72 (docID 10072),
              43 pages (pageID 10-430), every file headed "Creative Commons
              Attribution 4.0". Cached in data/sources/p72/ntvmr/10072/.
              Rendering: scripts/import_p52.py (shared machinery).
  2. SCANS    1-2 Peter (P. Bodmer VIII, papyrus pages 1-36): Biblioteca
              Apostolica Vaticana, DigiVatLib, IIIF manifest MSS_Pap.Bodmer.VIII
              (cached data/sources/p72/digivatlib/manifest.json). Each image
              shows one side of a glass frame holding a sheet (two facing pages,
              e.g. canvas "12-1" = page 12 on the left, page 1 on the right) or a
              single leaf (pages 13, 14, 35, 36). Each page is cropped from its
              sheet at the fold (crop boxes below, chosen by eye on the images).
              Terms: "Images Copyright Biblioteca Apostolica Vaticana".
              Jude (P. Bodmer VII, papyrus pages 62-68): Fondation Martin Bodmer,
              Bodmer Lab (University of Geneva), the Bodmer Miscellaneous Codex
              ("PB C", barcode 1072205366), IIIF manifest
              https://bodmerlab.unige.ch/fr/constellations/papyri/manifest/1072205366
              (cached data/sources/p72/bodmer/), canvases 049-055, licence CC BY-NC 4.0.
  3. MAPPING  Vatican: the typed label on each frame names the papyrus page
              numbers and verses, e.g. "p. 1 (A) 1 Petri 1, 1-4"; the papyrus page
              numbers (A, B, ...) are written at the head of the pages. These agree
              with the NTVMR page index (NTVMR "folio" = papyrus page number).
              Bodmer: the printed caption on each glass plate ("PB VII Epître de
              Jude, 4-6", ...) for pages 62-67; page 68 (canvas 055, no caption)
              carries the page number ξη (68) and the end of Jude. Every page was
              then checked on the image (first and last lines), recorded in
              data/sources/p72/visual_check.json and in each section's scan_note.
  4. ENGLISH  King James Version (eBible.org eng-kjv USFM, public domain).

Usage (from the repo root):
    python3 -I scripts/import_p72.py [--force]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_p52 as L  # noqa: E402

KEY, DOC, PREFIX = "p72", 10072, "verified-p72-"
VAT_SVC = "https://digi.vatlib.it/iiifimage/MSS_Pap.Bodmer.VIII/Pap.Bodmer.VIII_{n:04d}_pa_{lab}.jp2"
VAT_VIEW = "https://digi.vatlib.it/view/MSS_Pap.Bodmer.VIII/{n:04d}"
VAT_MANIFEST = "https://digi.vatlib.it/iiif/MSS_Pap.Bodmer.VIII/manifest.json"
BOD_SVC = "https://iiif.hedera.unige.ch/iiif/2/bodmerlab/1072205366/1072205366_{c}.jpg"
BOD_VIEW = "https://bodmerlab.unige.ch/fr/constellations/papyri/mirador/1072205366"
BOD_MANIFEST = "https://bodmerlab.unige.ch/fr/constellations/papyri/manifest/1072205366"
BOD_PAGE = "https://bodmerlab.unige.ch/fr/constellations/papyri/barcode/1072205366"

# DigiVatLib canvases: (canvas number, label, left page, right page, fold x in full-resolution px).
# Image size 2882 x 2929. The fold was located by eye on each image.
SHEETS = [
    (1, "0002-11", 2, 11, 1392), (2, "0012-1", 12, 1, 1480), (3, "0010-3", 10, 3, 1476),
    (4, "0004-9", 4, 9, 1412), (5, "0008-5", 8, 5, 1432), (6, "0006-7", 6, 7, 1412),
    (7, "0013", None, 13, None), (8, "0014", 14, None, None),
    (9, "0030-15", 30, 15, 1426), (10, "0016-29", 16, 29, 1440), (11, "0028-17", 28, 17, 1432),
    (12, "0018-27", 18, 27, 1484), (13, "0026-19", 26, 19, 1440), (14, "0020-25", 20, 25, 1456),
    (15, "0024-21", 24, 21, 1432), (16, "0022-23", 22, 23, 1432), (17, "0034-31", 34, 31, 1540),
    (18, "0032-33", 32, 33, 1460), (19, "0035", None, 35, 1514), (20, "0036", 36, None, 1500),
]
# Typed frame labels as read on the images (page: label text).
FRAME_LABEL = {
    12: "I recto = p. 12 (IB) 1 Petri 3, 1-6", 1: "p. 1 (A) 1 Petri 1, 1-4",
    2: "I verso = p. 2 (B) 1 Petri 1, 5-9", 11: "p. 11 (IA) 1 Petri 2, 22-3, 1",
    10: "II recto = p. 10 (I) 1 Petri 2, 17-21", 3: "p. 3 (Γ) 1 Petri 1, 10-13",
    4: "II verso = p. 4 (Δ) 1 Petri 1, 13-18", 9: "p. 9 (Θ) 1 Petri 2, 12-17",
    8: "III recto = p. 8 (H) 1 Petri 2, 7-12", 5: "p. 5 (E) 1 Petri 1, 18-22",
    6: "III verso = p. 6 (ς) 1 Petri 1, 22-2, 1", 7: "p. 7 (Z) 1 Petri 2, 2-7",
    13: "IV recto = p. 13 (IΓ) 1 Petri 3, 6-10", 14: "IV verso = p. 14 (IΔ) 1 Petri 3, 11-16",
    30: "V recto = p. 30 (Λ) 2 Petri 2, 12-16", 15: "p. 15 (IE) 1 Petri 3, 17-22",
    16: "V verso = p. 16 (Iς) 1 Petri 3, 22-4, 4", 29: "p. 29 (KΘ) 2 Petri 2, 8-12",
    28: "VI recto = p. 28 (KH) 2 Petri 2, 2-7", 17: "p. 17 (IZ) 1 Petri 4, 4-11",
    18: "VI verso = p. 18 (IH) 1 Petri 4, 11-16", 27: "p. 27 (KZ) 2 Petri 1, 19-2, 1",
    26: "VII recto = p. 26 (Kς) 2 Petri 1, 16-19", 19: "p. 19 (IΘ) 1 Petri 4, 16-5, 2",
    20: "VII verso = p. 20 (K) 1 Petri 5, 2-6", 25: "p. 25 (KE) 2 Petri 1, 10-15",
    24: "VIII recto = p. 24 (KΔ) 2 Petri 1, 5-10", 21: "p. 21 (KA) 1 Petri 5, 7-11",
    22: "VIII verso = p. 22 (KB) 1 Petri 5, 12-14", 23: "p. 23 (KΓ) 2 Petri 1, 1-5",
    34: "IX recto = p. 34 (ΛΔ) 2 Petri 3, 9-11", 31: "p. 31 (ΛA) 2 Petri 2, 16-21",
    32: "IX verso = p. 32 (ΛB) 2 Petri 2, 21-3, 3", 33: "p. 33 (ΛΓ) 2 Petri 3, 3-8",
    35: "p. 35 (ΛE) 2 Petri 3, 12-16", 36: "X verso = p. 36 (Λς) 2 Petri 3, 16-18",
}
# Single-leaf frames: explicit x ranges (full-resolution px).
SINGLE_X = {13: (760, 2200), 14: (720, 2080)}
Y0, Y1 = 260, 1840          # frame label strip to below the papyrus
XL, XR = 300, 2580          # inside the side tapes

# Jude, Bodmer Lab canvases (page: canvas id, caption read on the plate)
JUDE = {
    62: ("049", "PB XI Onzième ode de Salomon, 24 / PB VII Jude 1-4"),
    63: ("050", "PB VII Epître de Jude, 4-6"),
    64: ("051", "PB VII Epître de Jude, 7-10"),
    65: ("052", "PB VII Epître de Jude, 10-13"),
    66: ("053", "PB VII Epître de Jude, 13-18"),
    67: ("054", "PB VII Epître de Jude, 18-24"),
    68: ("055", None),
}


def vat_specs():
    specs = {}
    for n, lab, left, right, fold in SHEETS:
        svc = VAT_SVC.format(n=n, lab=lab)
        for side, page in (("left", left), ("right", right)):
            if page is None:
                continue
            if page in SINGLE_X:
                x0, x1 = SINGLE_X[page]
            elif side == "left":
                x0, x1 = XL, fold + 24
            else:
                x0, x1 = fold - 24, XR
            region = f"{x0},{Y0},{x1 - x0},{Y1 - Y0}"
            where = "the single leaf in the frame" if page in SINGLE_X or left is None or right is None \
                else f"the {side}-hand page of the opening, cropped at the fold"
            specs[page] = {
                "url": f"{svc}/{region}/full/0/default.jpg",
                "file": f"p72-p{page:02d}.jpg",
                "scan_note": (f"Vatican Library, Pap. Bodmer VIII, DigiVatLib image {n} ({VAT_VIEW.format(n=n)}), "
                              f"{where}. The typed label on the glass frame reads \"{FRAME_LABEL[page]}\"."),
                "src": f"DigiVatLib Pap.Bodmer.VIII image {n}",
            }
    return specs


def jude_specs():
    specs = {}
    for page, (c, cap) in JUDE.items():
        if c == "055":
            url = f"{BOD_SVC.format(c=c)}/pct:12,0,68,100/,2400/0/default.jpg"
            note = (f"Fondation Martin Bodmer, Bodmer Miscellaneous Codex (PB C), Bodmer Lab image {c} ({BOD_VIEW}), "
                    "cropped to the leaf (ruler and colour chart cut away). The plate has no caption; the page number ξη "
                    "(68) is written at the head of the page.")
        else:
            url = f"{BOD_SVC.format(c=c)}/full/,2400/0/default.jpg"
            note = (f"Fondation Martin Bodmer, Bodmer Miscellaneous Codex (PB C), Bodmer Lab image {c} ({BOD_VIEW}), "
                    f"the leaf in its glass plate. The printed caption under the plate reads \"{cap}\".")
        specs[page] = {"url": url, "file": f"p72-p{page:02d}.jpg", "scan_note": note,
                       "src": f"Bodmer Lab PB C image {c}"}
    return specs


INTRO_COMMON = (
    "<p>P72 is a papyrus codex copied in Egypt in the 3rd or early 4th century. It holds the oldest known copies of "
    "1 Peter, 2 Peter and Jude. The pages are numbered by the scribe. 1-2 Peter (papyrus pages 1-36) are Papyrus "
    "Bodmer VIII, given by Martin Bodmer to Pope Paul VI in 1969 and now in the Vatican Library; Jude (pages 62-68) "
    "is Papyrus Bodmer VII, still at the Fondation Martin Bodmer, Cologny (Geneva). Both belong to the Bodmer "
    "\"Miscellaneous\" or \"Composite\" codex, which also contains the Nativity of Mary, the apocryphal correspondence "
    "of Paul with the Corinthians, the 11th Ode of Solomon, Melito's sermon On the Pascha, a hymn fragment and other "
    "texts. 1-2 Peter seem to have formed a separate booklet before being bound with the rest.</p>\n\n"
    "<p>Each section below is one papyrus page: the photograph, the NTVMR diplomatic transcription of that page line "
    "by line, and the King James Version of every verse on it. The scribe's spelling is irregular (ει for ι, ε for αι, "
    "and so on) and is kept as written.</p>"
)


def entry_intro(pages):
    first, last = pages[0], pages[-1]
    b = first["verses"][0][0]
    rng = L.entry_range_title(pages)
    s = (f"<p>This entry covers papyrus pages {first['page']}-{last['page']} ({rng}). "
         if len(pages) > 1 else f"<p>This entry covers papyrus page {first['page']} ({rng}). ")
    if b in (21, 22):
        s += "The photographs are from the Vatican Library (Pap. Bodmer VIII).</p>"
    else:
        s += "The photographs are from the Fondation Martin Bodmer (Pap. Bodmer VII), via the Bodmer Lab of the University of Geneva.</p>"
    if b == 22 and first["verses"][0][1] == 1:
        s += ("\n\n<p>2 Peter 1:4 is on papyrus page 23 (lines 13-17). The KJV renders it \"that by these ye might be partakers "
              "of the divine nature\"; P72 reads ινα δια τουτων γενησθε θειας κοινωνοι φυσεως. It is the New Testament "
              "verse from which the Greek fathers drew the doctrine of theosis.</p>")
    return INTRO_COMMON + "\n\n" + s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    checks = L.load_checks(KEY)
    specs = {**vat_specs(), **jude_specs()}
    scan_dir = L.SCANS / KEY
    pages = []
    for p in L.ntvmr_pages(KEY, DOC):
        if not p.get("transcriptions"):
            continue
        page = int(p["folio"])
        sp = specs[page]
        L.get_image(scan_dir / sp["file"], sp["url"], force=a.force)
        pg = L.build_page(KEY, DOC, {"pid": p["pageID"], "sec": f"p{page}", "page": page,
                                     "ref_label": f"P72 page {page}", **sp})
        pages.append(pg)
    missing = [pg["sec"] for pg in pages if pg["sec"] not in checks]
    if missing:
        print("WARNING: no visual check recorded for", missing)

    rows, keep = [], set()
    groups = L.group_pages_by_chapter(pages)
    for order, grp in enumerate(groups, 1):
        b, k, _ = grp[0]["verses"][0]
        slug = f"{PREFIX}{L.BOOK_SLUG[b]}-{k}" if b != 26 else f"{PREFIX}jude"
        rng = L.entry_range_title(grp)
        pp = f"page {grp[0]['page']}" if len(grp) == 1 else f"pages {grp[0]['page']}-{grp[-1]['page']}"
        ms = "Papyrus Bodmer VIII" if b in (21, 22) else "Papyrus Bodmer VII"
        title = f"P72 ({ms}): {rng} ({pp})"
        sections = [L.make_section(KEY, pg, checks.get(pg["sec"], "")) for pg in grp]
        is_vat = b in (21, 22)
        desc = (f"{rng} in P72, the 3rd/4th-century papyrus codex of 1-2 Peter and Jude: {pp} of the papyrus, "
                "each with its photograph, the Greek transcription and the King James Version.")
        entry = {
            "id": slug, "slug": slug, "title": title,
            "language": "Greek (NTVMR transcription) / English (KJV)",
            "source": (f"{ms} ({'Vatican Library' if is_vat else 'Fondation Martin Bodmer, Cologny'}): photographs from "
                       f"{'DigiVatLib' if is_vat else 'Bodmer Lab, University of Geneva'}; Greek from the INTF NTVMR "
                       "transcription of P72; English from the King James Version"),
            "description": desc,
            "introduction": entry_intro(grp),
            "translator_notes": [L.GREEK_NOTE, L.ENGLISH_NOTE],
            "translation": sections,
            "verification": {
                "scan_source": (f"Biblioteca Apostolica Vaticana, DigiVatLib, Pap.Bodmer.VIII ({VAT_MANIFEST})" if is_vat else
                                f"Fondation Martin Bodmer, Bodmer Lab (Université de Genève), PB C ({BOD_PAGE}; IIIF manifest {BOD_MANIFEST})"),
                "scan_license": ("Images Copyright Biblioteca Apostolica Vaticana (as stated in the IIIF manifest); "
                                 "reproduced with credit for non-commercial reference use" if is_vat else
                                 "CC BY-NC 4.0 (IIIF manifest licence; attribution: Fondation Martin Bodmer, numérisation Bodmer Lab, UNIGE)"),
                "scan_manuscript": (f"{ms}, Gregory-Aland P72, papyrus codex, 3rd/4th century, Egypt; "
                                    f"{'Vatican City, Biblioteca Apostolica Vaticana' if is_vat else 'Cologny, Fondation Martin Bodmer'}"),
                "scan_mapping": ("Typed frame labels on the Vatican images and printed plate captions on the Bodmer images name "
                                 "the papyrus page numbers and verses; they agree with the NTVMR page index (folio = papyrus page). "
                                 "First and last lines of every page read on the cropped images."),
                "scan_mapping_urls": [L.META_URL.format(doc=DOC), VAT_MANIFEST if is_vat else BOD_MANIFEST],
                "scan_local_paths": [f"{KEY}/{pg['file']}" for pg in grp],
                "original_text_source": ("INTF, New Testament Virtual Manuscript Room, transcription of GA P72 (docID 10072), pages "
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
            "id": slug, "slug": slug, "order": order, "title": title, "author_id": "p72-scribe",
            "language": "Greek", "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": "3rd/4th century AD (NTVMR: 200-399)", "century": 3,
            "source": entry["source"], "description": desc,
            "themes": ["new-testament", "papyrus", "p72", "bodmer-papyri", L.BOOK_SLUG[b], "greek", "verified"]
                      + (["theosis", "divine-nature"] if b == 22 and k == 1 else []),
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{pg['file']}", "caption": f"P72 page {pg['page']}"} for pg in grp]},
        })
        print(f"  {slug}: {title}, {len(sections)} sections")
    L.remove_stale(PREFIX, keep)
    collection = {
        "key": KEY, "prefix": PREFIX, "label": "P72 (Papyrus Bodmer VII-VIII)", "group": "New Testament",
        "date_sort": 300,
        "author_name": "Papyrus P72, Egypt (3rd/4th century AD)",
        "source_url": "https://digi.vatlib.it/view/MSS_Pap.Bodmer.VIII",
        "critical_edition": "INTF NTVMR diplomatic transcription (CC BY 4.0)",
        "translator_name": "King James Version (1611)",
        "original_lang_label": "Greek · NTVMR transcription",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "p72 bodmer papyrus 1 peter 2 peter jude partakers of the divine nature theosis",
        "description": "The oldest copies of 1 Peter, 2 Peter and Jude, page by page on a 3rd/4th-century papyrus codex in the Vatican Library and the Bodmer Foundation, including 2 Peter 1:4, \"partakers of the divine nature\".",
    }
    authors = [{"id": "p72-scribe", "name": "Papyrus P72 (scribe)", "dates": "3rd/4th century AD", "century": 3,
                "era": "Apostolic", "tradition": "christian", "language": "Greek",
                "bio": "Unknown Egyptian scribe who copied 1-2 Peter and Jude in the papyrus codex now split between the Vatican Library and the Bodmer Foundation."}]
    L.write_collection(KEY, collection, rows, authors)
    print(f"wrote {len(rows)} entries, {sum(len(r['scans']['pages']) for r in rows)} pages")


if __name__ == "__main__":
    main()
