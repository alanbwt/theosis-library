#!/usr/bin/env python3
"""
import_p75.py: P75 (Papyrus Hanna 1 (Mater Verbi), formerly P. Bodmer XIV-XV),
Luke and John, c. 175-225. One section per papyrus page, one entry per chapter
(pages grouped by the chapter in which they begin), 102 pages.

Chain of evidence
  1. GREEK    NTVMR (INTF Muenster) page transcriptions of GA P75 (docID 10075):
              the 102 pages with a folio number (7r ... 64v), every file headed
              "Creative Commons Attribution 4.0". Not used: pageID 10 (an older
              duplicate of folio 7r) and 1030 (a duplicate working copy of 64v),
              and the empty fragment pages 1021, 1022, 1040, 1050.
              Cached in data/sources/p75/ntvmr/10075/. Rendering: import_p52.py.
  2. SCANS    Biblioteca Apostolica Vaticana, DigiVatLib, Pap.Hanna.1(Mater.Verbi),
              IIIF manifest https://digi.vatlib.it/iiif/MSS_Pap.Hanna.1(Mater.Verbi)/manifest.json
              (cached data/sources/p75/digivatlib/manifest.json). One image per
              page side, in glass frames labelled 1A.1r ... 3A.6v. Each page is
              cropped to its frame (colour charts cut away).
              Terms: "Images Copyright Biblioteca Apostolica Vaticana".
  3. MAPPING  The frames are in codex order: frame n of the Vatican sequence
              (1A.1-1A.12, 1B.1-12, 2A.1-12, 2B.1-12, 3A.1-3) holds the n-th
              surviving leaf, recto then verso; the pencilled label on frame 1A.4r
              reads "Luc VI: 16-28" = NTVMR folio 12r. Exception: the first three
              frames hold the fragments of folios 7, 9 and 11 in another order
              (FRAME_OVERRIDE below). Every page was then checked
              on the image: the first and last legible lines at the top and foot
              of the papyrus were read and compared with the transcription
              (data/sources/p75/visual_check.json, quoted in each scan_note).
              Frames 3A.4-3A.6 hold small fragments not used here.
  4. ENGLISH  King James Version (eBible.org eng-kjv USFM, public domain).

Usage (from the repo root):
    python3 -I scripts/import_p75.py [--force]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_p52 as L  # noqa: E402

KEY, DOC, PREFIX = "p75", 10075, "verified-p75-"
MANIFEST_FILE = L.SRCROOT / KEY / "digivatlib" / "manifest.json"
MANIFEST = "https://digi.vatlib.it/iiif/MSS_Pap.Hanna.1(Mater.Verbi)/manifest.json"
VIEW = "https://digi.vatlib.it/view/MSS_Pap.Hanna.1(Mater.Verbi)/{n:04d}"
BBOX_FILE = L.SRCROOT / KEY / "digivatlib" / "papyrus_boxes.json"   # papyrus bounding boxes (1600 px wide previews)

# Readings of P75 that differ materially from the text the KJV translates, verified in the
# NTVMR transcription (folio: note).
VARIANT_NOTES = {
    "17v": "Luke 8:43: P75 does not have the words the KJV renders \"which had spent all her living upon physicians\".",
    "20r": "Luke 9:54-56: P75 does not have the words the KJV renders \"even as Elias did\" (9:54), \"and said, Ye know not "
           "what manner of spirit ye are of\" (9:55) and \"For the Son of man is not come to destroy men's lives, but to "
           "save them\" (9:56).",
    "22v": "Luke 11:2-4: P75 has the shorter form of the Lord's Prayer (πατερ αγιασθητω το ονομα σου ελθετω η βασιλεια σου ...), "
           "without the words the KJV renders \"Our\", \"which art in heaven\", \"Thy will be done, as in heaven, so in earth\" "
           "and \"but deliver us from evil\".",
    "32r": "Luke 16:19: P75 gives the rich man a name, ονοματι νευης (\"named Neues\"), which the KJV and almost all other "
           "manuscripts do not have.",
    "41v": "Luke 23:34: P75 does not have the words the KJV renders \"Then said Jesus, Father, forgive them; for they know not "
           "what they do\"; the verse begins διαμεριζομενοι δε τα ιματια αυτου.",
    "44v": "John 1:18: P75 reads ο μονογενης θ̅ς̅ (θεος, \"God\") where the KJV has \"the only begotten Son\".",
    "57v": "John 10:7: P75 reads εγω ειμι ο ποιμην των προβατων, with ποιμην (\"shepherd\") where the KJV has \"the door of the sheep\".",
}


# The first frames do not follow the one-leaf-per-frame order: frame 1A.1 holds two detached
# pieces of folio 7 (pencilled "Luc III, 19. 21-22"), frame 1A.2 holds the main fragment of
# folio 7 (front: Luke 3:19-21) together with folio 11 (back: Luke 6:12-14), and frame 1A.3
# is folio 9 (pencilled "Luc IV, 34-42"). Checked on the images.
FRAME_OVERRIDE = {"7r": ["1A.2r", "1A.1r"], "9r": ["1A.3r"], "9v": ["1A.3v"], "11v": ["1A.2v"]}
# Pages whose text could not be matched on the images with certainty (left out; see docs):
# 7v and 11r (fragments of folios 7 and 11 scattered over frames 1A.1-1A.2), and 39v, 58r, 58v,
# 64v (frames 2A.3v, 2B.10r, 2B.10v, 3A.3v: too damaged or faded to read at the resolution checked).
EXCLUDE = {"7v", "11r", "39v", "58r", "58v", "64v"}


def canvases():
    m = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    out = []
    for i, c in enumerate(m["sequences"][0]["canvases"], 1):
        out.append({"n": i, "label": c["label"], "w": c["width"], "h": c["height"],
                    "svc": c["images"][0]["resource"]["service"]["@id"]})
    return out


def region(cv, box):
    """Crop to the frame around the papyrus: colour charts at the sides and the
    copyright band at the foot cut away; the pencilled frame label kept."""
    s = cv["w"] / box[4]
    W, H = cv["w"], cv["h"]
    x0 = max(int(0.17 * W), int(box[0] * s - 0.03 * W))
    x1 = min(int(0.82 * W), int(box[2] * s + 0.03 * W))
    y0 = int(0.015 * H)
    y1 = min(int(0.93 * H), int(box[3] * s + 0.03 * H))
    return f"{x0},{y0},{x1 - x0},{y1 - y0}"


INTRO_COMMON = (
    "<p>P75 is a papyrus codex of Luke and John copied in Egypt around 175-225, the oldest known copy of Luke and one of "
    "the oldest of John. It was bought by Martin Bodmer in the 1950s and published as Papyrus Bodmer XIV-XV; in 2006 it "
    "was given to the Vatican Library, where it is kept as Papyrus Hanna 1 (Mater Verbi). Its text is very close to that "
    "of Codex Vaticanus, written some 150 years later. Where Luke ends and John begins (folio 44r) both titles stand on "
    "the same page.</p>\n\n"
    "<p>About 51 leaves survive, many damaged at the top and edges, especially in Luke 3-7. Lost: Luke 1:1-3:17, most of "
    "3:23-4:33, 5:11-36, 6:5-10, 7:33-34 and 7:44-45 (and parts of 7:36-49), 17:16-19, 18:19-22:3; John 11:46-47, 12:1-2, "
    "13:11-14:7 and everything after 15:10 except small fragments. Each section below is one page: the photograph, the "
    "NTVMR diplomatic transcription line by line, and the King James Version of every verse on the page. Where P75 lacks "
    "a verse or words that the KJV has (for example John 5:4 or the account of the adulteress, John 7:53-8:11), the "
    "section says so. Six damaged pages (folios 7v, 11r, 39v, 58r, 58v and 64v) are left out because their text "
    "could not be matched to the photographs with certainty.</p>"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    checks = L.load_checks(KEY)
    boxes = json.loads(BBOX_FILE.read_text(encoding="utf-8"))
    cvs = canvases()
    npages = [p for p in L.ntvmr_pages(KEY, DOC) if p.get("transcriptions") and (p.get("folio") or "").strip()]
    assert len(npages) == 102, len(npages)
    scan_dir = L.SCANS / KEY
    pages = []
    by_label = {cv["label"]: cv for cv in cvs}
    for p, cv in zip(npages, cvs):
        fol = p["folio"].strip()
        if fol in EXCLUDE:
            continue
        frames = [by_label[x] for x in FRAME_OVERRIDE.get(fol, [cv["label"]])]
        files = []
        for j, fr in enumerate(frames):
            f = f"p75-f{fol}.jpg" if j == 0 else f"p75-f{fol}-{fr['label'].replace('.', '')}.jpg"
            url = f"{fr['svc']}/{region(fr, boxes[fr['label']])}/,2400/0/default.jpg"
            L.get_image(scan_dir / f, url, force=a.force)
            files.append(f)
        fl = " and ".join(f"DigiVatLib image {fr['n']}, frame {fr['label']} ({VIEW.format(n=fr['n'])})" for fr in frames)
        spec = {"pid": p["pageID"], "sec": f"f{fol}", "folio": fol, "file": files[0], "files": files,
                "ref_label": f"P75 fol. {fol} (Vatican frame {' + '.join(fr['label'] for fr in frames)})",
                "scan_note": (f"Vatican Library, Pap. Hanna 1 (Mater Verbi), {fl}, cropped to the frame. "
                              f"NTVMR page {p['pageID']} (folio {fol})."),
                "frame": " + ".join(fr["label"] for fr in frames), "canvas": frames[0]["n"]}
        pages.append(L.build_page(KEY, DOC, spec))
    missing = [pg["sec"] for pg in pages if pg["sec"] not in checks]
    if missing:
        print("WARNING: no visual check recorded for", missing)

    rows, keep = [], set()
    for order, grp in enumerate(L.group_pages_by_chapter(pages), 1):
        b, k, _ = grp[0]["verses"][0]
        slug = f"{PREFIX}{L.BOOK_SLUG[b]}-{k}"
        rng = L.entry_range_title(grp)
        ff = f"fol. {grp[0]['folio']}" if len(grp) == 1 else f"fols. {grp[0]['folio']}-{grp[-1]['folio']}"
        title = f"P75 (Papyrus Hanna 1): {rng} ({ff})"
        sections = [L.make_section(KEY, pg, checks.get(pg["sec"], ""), VARIANT_NOTES.get(pg["folio"], "")) for pg in grp]
        desc = (f"{rng} in P75 (Papyrus Hanna 1), the papyrus codex of Luke and John copied around 175-225: "
                f"{ff}, each page with its photograph, the Greek transcription and the King James Version.")
        intro = INTRO_COMMON + (f"\n\n<p>This entry covers {ff} ({rng}), shown on the Vatican Library's photographs "
                                f"(frames {grp[0]['frame']} to {grp[-1]['frame']}).</p>" if len(grp) > 1 else
                                f"\n\n<p>This entry covers {ff} ({rng}), shown on the Vatican Library's photograph "
                                f"(frame {grp[0]['frame']}).</p>")
        entry = {
            "id": slug, "slug": slug, "title": title,
            "language": "Greek (NTVMR transcription) / English (KJV)",
            "source": ("Papyrus Hanna 1 (Mater Verbi), Vatican Library: photographs from DigiVatLib; Greek from the INTF NTVMR "
                       "transcription of P75; English from the King James Version"),
            "description": desc,
            "introduction": intro,
            "translator_notes": [L.GREEK_NOTE, L.ENGLISH_NOTE],
            "translation": sections,
            "verification": {
                "scan_source": f"Biblioteca Apostolica Vaticana, DigiVatLib, Pap.Hanna.1(Mater.Verbi) ({MANIFEST})",
                "scan_license": ("Images Copyright Biblioteca Apostolica Vaticana (as stated in the IIIF manifest); reproduced "
                                 "with credit for non-commercial reference use"),
                "scan_manuscript": ("Vatican City, Biblioteca Apostolica Vaticana, Pap. Hanna 1 (Mater Verbi), formerly P. Bodmer "
                                    "XIV-XV; Gregory-Aland P75; papyrus codex, c. 175-225 (NTVMR: 3rd c., 200-225), Egypt"),
                "scan_mapping": ("From frame 1A.4 on, the Vatican frames follow the codex order (frame n = n-th surviving "
                                 "leaf; frame 1A.4r is pencilled 'Luc VI: 16-28' = NTVMR folio 12r); frames 1A.1-1A.3 "
                                 "hold the fragments of folios 7, 9 and 11, placed by their pencilled labels and text; "
                                 "lines near the top and foot of every page read on the images and matched to the NTVMR "
                                 "transcription"),
                "scan_mapping_urls": [L.META_URL.format(doc=DOC), MANIFEST],
                "scan_local_paths": [f"{KEY}/{pg['file']}" for pg in grp],
                "original_text_source": ("INTF, New Testament Virtual Manuscript Room, transcription of GA P75 (docID 10075), pages "
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
            "id": slug, "slug": slug, "order": order, "title": title, "author_id": "p75-scribe",
            "language": "Greek", "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": "c. 175-225 AD", "century": 3,
            "source": entry["source"], "description": desc,
            "themes": ["new-testament", "papyrus", "p75", "bodmer-papyri", L.BOOK_SLUG[b], "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{pg['file']}", "caption": f"P75 fol. {pg['folio']}"} for pg in grp]},
        })
        print(f"  {slug}: {title}, {len(sections)} sections")
    L.remove_stale(PREFIX, keep)
    collection = {
        "key": KEY, "prefix": PREFIX, "label": "P75 (Papyrus Hanna 1)", "group": "New Testament",
        "date_sort": 200,
        "author_name": "Papyrus P75, Egypt (c. 175-225 AD)",
        "source_url": "https://digi.vatlib.it/view/MSS_Pap.Hanna.1(Mater.Verbi)",
        "critical_edition": "INTF NTVMR diplomatic transcription (CC BY 4.0)",
        "translator_name": "King James Version (1611)",
        "original_lang_label": "Greek · NTVMR transcription",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "p75 papyrus hanna mater verbi bodmer xiv xv luke john vatican",
        "description": "The oldest copy of Luke and one of the oldest of John: the papyrus codex P75 (c. 175-225) in the Vatican Library, page by page.",
    }
    authors = [{"id": "p75-scribe", "name": "Papyrus P75 (scribe)", "dates": "c. 175-225 AD", "century": 3,
                "era": "Apostolic", "tradition": "christian", "language": "Greek",
                "bio": "Unknown Egyptian scribe of the papyrus codex of Luke and John now called Papyrus Hanna 1 (Mater Verbi), a careful copyist whose text is close to Codex Vaticanus."}]
    L.write_collection(KEY, collection, rows, authors)
    print(f"wrote {len(rows)} entries, {len(pages)} pages")


if __name__ == "__main__":
    main()
