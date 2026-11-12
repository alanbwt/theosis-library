#!/usr/bin/env python3
"""
import_odyssey.py: Homer, Odyssey, on Florence, Biblioteca Medicea Laurenziana, Plut. 32.24
(10th century, parchment, 234 folios), the oldest Odyssey manuscript with published images.

One entry per book; one section per manuscript page. Only books whose every page has been
verified (data/sources/odyssey/page_map.json, "complete_books") are built.

Chain of evidence
  1. SCAN     BML Teca Digitale (CONTENTdm IIIF), manifest
              https://cdm21059.contentdm.oclc.org/iiif/plutei:735325/manifest.json
              ("Homeri Odyssea", 901-1000; rights CC BY-NC-SA). Folio labels are taken from the
              manifest; images are requested at 1800 px wide.
  2. MAPPING  data/sources/odyssey/page_map.json: for every page the first and last verse were
              read on the image (strips of the top and bottom lines, zoomed crops where the
              edge is curled or stained) and matched to the Greek; consecutive pages were checked
              for continuity. Most pages carry 24-28 lines.
  3. GREEK    A. T. Murray, Homer: The Odyssey (Loeb, 1919), Perseus canonical-greekLit
              tlg0012.tlg002.perseus-grc2 (CC BY-SA 4.0).
  4. ENGLISH  A. T. Murray (Loeb, 1919; public domain in the US), Perseus
              tlg0012.tlg002.perseus-eng3, which marks every fifth line; the prose is cut at
              those marks and each five-line block is placed with the page holding its middle line.

Usage:  python3 scripts/import_odyssey.py [--force]   (--force re-downloads scans)
"""
import argparse
import io
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image

KEY = "odyssey"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
GREEK_XML = SRC / "tlg0012.tlg002.perseus-grc2.xml"
ENGLISH_XML = SRC / "tlg0012.tlg002.perseus-eng3.xml"
GITHUB = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0012/tlg002/"
MANIFEST = "https://cdm21059.contentdm.oclc.org/iiif/plutei:735325/manifest.json"
RECORD = "https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/735325"
MS = "Laur. Plut. 32.24"
MS_LONG = ("Florence, Biblioteca Medicea Laurenziana, Plut. 32.24 (parchment, 10th century, 234 folios; "
           "the oldest manuscript of the Odyssey with published images)")
BOOK_TITLES = {
    1: "Athena visits Telemachus", 2: "The assembly in Ithaca", 3: "Telemachus at Pylos",
    4: "Telemachus at Sparta", 5: "Calypso and the raft", 6: "Nausicaa", 7: "The palace of Alcinous",
    8: "The games of the Phaeacians", 9: "The Cyclops", 10: "Aeolus, the Laestrygonians and Circe",
    11: "The land of the dead", 12: "The Sirens, Scylla and Charybdis, the cattle of the Sun",
    13: "Odysseus reaches Ithaca", 14: "In the hut of Eumaeus", 15: "Telemachus returns",
    16: "Father and son", 17: "Odysseus in his own hall as a beggar", 18: "The beggar Irus",
    19: "Penelope and the beggar; the scar", 20: "Portents for the suitors", 21: "The bow",
    22: "The slaying of the suitors", 23: "Penelope and Odysseus", 24: "The suitors in Hades; Laertes; peace",
}


def fetch(url, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) > 20000:
                return data
        except Exception:
            pass
        time.sleep(3 + 4 * i)
    raise RuntimeError(f"download failed: {url}")


def services():
    cache = SRC / "laur-32-24-manifest.json"
    if not cache.exists():
        cache.write_bytes(fetch(MANIFEST))
    d = json.loads(cache.read_text(encoding="utf-8"))
    out = {}
    for c in d["sequences"][0]["canvases"]:
        m = re.search(r"Carta(?: bianca)?: (\d+[rv])$", c["label"])
        if m:
            out[m.group(1)] = c["images"][0]["resource"]["service"]["@id"]
    return out


def scan_name(folio):
    return f"laur-32-24-f{folio}.jpg"


def get_scan(folio, svc, force=False):
    path = SCAN_DIR / scan_name(folio)
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"{svc[folio]}/full/1800,/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def greek_book(book):
    root = ET.parse(GREEK_XML).getroot()
    for d in root.iter(f"{TEI}div"):
        if d.get("subtype") == "book" and d.get("n") == str(book):
            out = {}
            for l in d.iter(f"{TEI}l"):
                n = l.get("n")
                if n and n.isdigit():
                    txt = "".join(t for e in [l] for t in e.itertext())
                    out[int(n)] = re.sub(r"\s+", " ", txt).strip()
            return out
    raise KeyError(book)


def english_book(book):
    """[(start_line, text)] blocks cut at Murray's line milestones and card (paragraph) starts."""
    root = ET.parse(ENGLISH_XML).getroot()
    bdiv = next(d for d in root.iter(f"{TEI}div") if d.get("subtype") == "book" and d.get("n") == str(book))
    blocks = [[1, ""]]

    def walk(e):
        for c in e:
            tag = c.tag.replace(TEI, "")
            if tag == "milestone" and c.get("unit") == "line":
                n = int(c.get("n"))
                if blocks[-1][1].strip():
                    blocks.append([n, ""])
                else:
                    blocks[-1][0] = n
            elif tag == "div" and c.get("subtype") == "card":
                n = int(c.get("n"))
                if blocks[-1][1].strip():
                    blocks.append([n, ""])
                else:
                    blocks[-1][0] = n
                walk(c)
            elif tag == "note":
                pass
            else:
                blocks[-1][1] += c.text or ""
                walk(c)
            blocks[-1][1] += c.tail or ""
    walk(bdiv)
    out = []
    for n, t in blocks:
        t = re.sub(r"\s+", " ", t).strip()
        if not t:
            continue
        if out and out[-1][0] == n:
            out[-1] = (n, out[-1][1] + " " + t)
        else:
            out.append((n, t))
    return out


def build(force=False):
    pm = json.loads((SRC / "page_map.json").read_text(encoding="utf-8"))
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    svc = services()
    rows, books = [], pm["complete_books"]
    pages = pm["pages"]
    for book in books:
        G = greek_book(book)
        E = english_book(book)
        bpages = [p for p in pages if any(s["book"] == book for s in p["segments"])]
        main = [p for p in bpages if not p.get("replacement")]
        # every edition line of the book is on exactly one (original) page
        where = {}
        for p in main:
            for s in p["segments"]:
                if s["book"] == book:
                    for k in range(s["first"], s["last"] + 1):
                        assert k not in where, (book, k)
                        where[k] = p["folio"]
        missing = sorted(set(G) - set(where))
        assert not missing, (book, missing[:10])
        for p in bpages:
            get_scan(p["folio"], svc, force)
        # English blocks -> page by middle line
        eng_at = {}
        for i, (a, t) in enumerate(E):
            b = (E[i + 1][0] - 1) if i + 1 < len(E) else max(G)
            b = max(a, b)
            mid = (a + b) // 2
            f = where.get(mid) or where.get(a)
            eng_at.setdefault(f, []).append((a, b, t))
        sections = []
        for idx, p in enumerate(main):
            f = p["folio"]
            seg = next(s for s in p["segments"] if s["book"] == book)
            ks = [k for k in range(seg["first"], seg["last"] + 1) if k in G]
            gtxt = "<br>".join(f"<sup>{k}</sup>{esc(G[k])}" for k in ks)
            eb = eng_at.get(f, [])
            etxt = "<p>" + " ".join(f"<sup>{a}</sup>{esc(t)}" for a, b, t in eb) + "</p>" if eb else \
                "<p><em>The English for these lines is given with the neighbouring page (Murray's prose is divided every five lines).</em></p>"
            scans = [f"{KEY}/{scan_name(f)}"]
            extra = ""
            rep = [r for r in bpages if r.get("replacement") and any(s["book"] == book and s["first"] <= seg["first"] <= s["last"] for s in r["segments"])]
            for r in rep:
                scans.append(f"{KEY}/{scan_name(r['folio'])}")
                extra += f" The same lines are also on fol. {r['folio']}, shown second: {r['note']}"
            others = [f"{s['book']}.{s['first']}-{s['last']}" for s in p["segments"]]
            fw = " ".join(G[seg["first"]].split()[:4])
            lw = " ".join(G[seg["last"]].split()[-4:])
            prev_p = main[idx - 1] if idx > 0 else None
            next_p = main[idx + 1] if idx + 1 < len(main) else None
            cont = ""
            if prev_p:
                ps = prev_p["segments"][-1]
                cont += f" Fol. {prev_p['folio']} ends with {ps['book']}.{ps['last']}."
            if next_p:
                ns = next_p["segments"][0]
                cont += f" Fol. {next_p['folio']} begins with {ns['book']}.{ns['first']}."
            onpage = f" The page holds {', '.join(others)}." if len(p["segments"]) > 1 else ""
            note = (f"{MS}, fol. {f}: Odyssey {book}.{seg['first']}-{seg['last']}, begins ‹{fw}›, ends ‹{lw}›. "
                    f"Checked on the image: first and last lines read and matched to the Greek.{cont}{onpage}"
                    + (f" {p['note']}" if p.get("note") else "") + extra
                    + (f" English blocks here: {', '.join(f'{a}-{b}' for a, b, t in eb)}." if eb else ""))
            sections.append({
                "section": f"fol. {f}",
                "original_ref": f"Odyssey {book}.{seg['first']}-{seg['last']}; {MS}, fol. {f}",
                "original_text": gtxt, "text": etxt,
                "scan_pages": scans, "scan_note": note,
            })
        tid = f"verified-{KEY}-book-{book}"
        title = f"Homer, Odyssey, Book {book}: {BOOK_TITLES[book]}"
        fols = [s["section"].replace("fol. ", "") for s in sections]
        intro = (
            f"<p>The <em>Odyssey</em>, composed around 700 BCE and attributed to Homer, tells of Odysseus' ten-year journey home from Troy and his return to Ithaca. "
            f"<strong>Book {book}</strong> ({len(G)} lines): {esc(BOOK_TITLES[book])}.</p>"
            f"<p>The page photographs are from {esc(MS_LONG)}, in the Biblioteca Medicea Laurenziana's Teca Digitale. "
            f"This book is on fol. {fols[0]}-{fols[-1]}; each section below is one page, with its first and last line as read on the photograph. "
            "Many pages carry interlinear glosses and a few marginal notes in later hands.</p>"
            "<p>The Greek is A. T. Murray's Loeb text (1919) via Perseus, not a transcription of this manuscript, whose wording differs in places. "
            "The English is Murray's prose translation (1919), divided every five lines; at a page break a five-line block goes with the page holding most of it.</p>"
        )
        pub = {
            "id": tid, "slug": tid, "title": title,
            "language": "Ancient Greek / English",
            "source": f"{MS} (BML Teca Digitale IIIF) + Murray Greek (Loeb 1919, Perseus) + Murray English (Loeb 1919, Perseus)",
            "description": f"Book {book} of Homer's Odyssey ({BOOK_TITLES[book]}), page by page on the 10th-century Florence manuscript Laur. Plut. 32.24, with Greek and English.",
            "introduction": intro,
            "translator_notes": [
                "Greek: A. T. Murray, Homer: The Odyssey (Loeb Classical Library, 1919), via Perseus.",
                "English: A. T. Murray's translation in the same edition; his footnotes are omitted.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF): {RECORD} ; manifest {MANIFEST}",
                "scan_license": "CC BY-NC-SA, as stated in the Teca Digitale record; images © Biblioteca Medicea Laurenziana, Florence",
                "scan_manuscript": MS_LONG,
                "scan_mapping": "First and last line of every page read on the page image and matched to the Greek, with continuity checked between consecutive pages (data/sources/odyssey/page_map.json; details in each section's scan_note).",
                "scan_mapping_urls": [RECORD, MANIFEST],
                "scan_local_paths": list(dict.fromkeys(x for s in sections for x in s["scan_pages"])),
                "original_text_source": f"A. T. Murray, Homer: The Odyssey (Loeb, 1919), Perseus canonical-greekLit tlg0012.tlg002.perseus-grc2 ({GITHUB}tlg0012.tlg002.perseus-grc2.xml)",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"A. T. Murray, Homer: The Odyssey (Loeb, 1919), Perseus tlg0012.tlg002.perseus-eng3 ({GITHUB}tlg0012.tlg002.perseus-eng3.xml)",
                "translation_license": "public domain in the US (published 1919); Perseus digital text CC BY-SA 4.0",
                "translator": "A. T. Murray (1919)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": book, "title": title, "author_id": "homer",
            "language": "Ancient Greek", "era": "Classical", "tradition": "greek", "category": "literature",
            "date_approx": "c. 700 BCE (composition); manuscript 10th c.", "century": -8,
            "source": pub["source"], "description": pub["description"],
            "themes": ["homer", "odyssey", "odysseus", "epic", "greek", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": x, "caption": f"{MS}, fol. {x.split('-f')[-1][:-4]}"} for x in pub["verification"]["scan_local_paths"]]},
        })
        print(f"wrote {tid}: {len(sections)} sections")
    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-", "label": "Homer, Odyssey (Florence manuscript)",
            "group": "Greece", "date_sort": -700,
            "author_name": "Homer (c. 700 BCE; Florence manuscript, 10th c.)",
            "source_url": RECORD,
            "critical_edition": "Murray, Loeb 1919, via Perseus",
            "translator_name": "A. T. Murray (1919)",
            "original_lang_label": "Ancient Greek · Murray",
            "original_lang_code": "grc", "edition_label": "",
            "search_terms": "homer odyssey odysseus telemachus penelope athena ithaca epic",
            "description": "Homer's Odyssey page by page on the oldest Odyssey manuscript with published images, Florence, Laur. Plut. 32.24 (10th century). Books are added as their pages are verified.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    build(ap.parse_args().force)
