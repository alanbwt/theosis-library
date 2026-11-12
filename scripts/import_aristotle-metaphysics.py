#!/usr/bin/env python3
"""
import_aristotle-metaphysics.py: Aristotle, Metaphysics 12 (Lambda) chapters 6-10
(1071b3-1076a4): the eternal unmoved mover, 'thought thinking itself', the life of god.

One entry; one section per chapter (12.6-12.10), each linked to the manuscript pages
that carry it. Chapters are the finest division that the Greek and the English share
here: the English has chapter divisions but no Bekker line markers.

Chain of evidence
  1. MANUSCRIPT  Paris, Bibliotheque nationale de France, grec 1853 (siglum E,
     10th c.), Gallica IIIF ark:/12148/btv1b84192492 (colour digitization of the
     original). Contents from the BnF description in the manifest: Metaphysics from
     fol. 225v. Pinakes diktyon 51479.
  2. MAPPING  First and last lines of every page read on the images and matched to
     Ross's Greek (PAGES below, quoted in each scan_note); no page placed by counting.
  3. GREEK    W. D. Ross, Aristotle's Metaphysics (Oxford, 1924), Perseus
     canonical-greekLit tlg0086.tlg025.perseus-grc2 (CC BY-SA 4.0).
  4. ENGLISH  W. D. Ross, Metaphysica, The Works of Aristotle translated into English,
     vol. VIII, revised edition (Oxford, 1928), as given by the MIT Internet Classics
     Archive (classics.mit.edu/Aristotle/metaphysics.12.xii.html). Public domain in
     the US (published before 1931). The archive wraps each paragraph in double
     quotation marks; those wrapper marks are removed, nothing else is changed.

Usage:
    python3 scripts/import_aristotle-metaphysics.py [--force]
"""

import argparse
import html
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

KEY = "aristotle-metaphysics"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TID = PREFIX + "lambda-6-10"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
PERSEUS = "https://github.com/PerseusDL/canonical-greekLit/tree/master/data/tlg0086/tlg025"
MIT = "https://classics.mit.edu/Aristotle/metaphysics.12.xii.html"
ARK = "https://gallica.bnf.fr/ark:/12148/btv1b84192492"

PAGES = {
    "293r": "Paris gr. 1853 fol. 293r begins 'ἄνθρωπος μὲν γὰρ ἀνθρώπου καθόλου, ἀλλʼ οὐκ ἔστιν οὐδείς, ἀλλὰ Πηλεὺς Ἀχιλλέως' (1071a20-22) and ends 'οἷον Λεύκιππος καὶ Πλάτων· ἀεὶ γὰρ εἶναί φασι κίνησιν' (1071b32-33); chapter 6 ('ἐπεὶ δʼ ἦσαν τρεῖς οὐσίαι') begins on this page.",
    "293v": "Paris gr. 1853 fol. 293v begins 'ἀλλὰ διὰ τί καὶ τίνα οὐ λέγουσιν, οὐδʼ ὡδί, οὐδὲ τὴν αἰτίαν' (1071b33-35) and ends 'φορὰ γὰρ ἡ πρώτη τῶν μεταβολῶν, ταύτης δὲ ἡ κύκλῳ· ταύτην δὲ τοῦτο κινεῖ' (1072b8-10).",
    "294r": "Paris gr. 1853 fol. 294r begins 'ἐξ ἀνάγκης ἄρα ἐστὶν ὄν· καὶ ᾗ ἀνάγκῃ, καλῶς, καὶ οὕτως ἀρχή' (1072b10-11) and ends 'ἡ μὲν γὰρ ἀρχὴ καὶ τὸ πρῶτον τῶν ὄντων ἀκί(νητον)' (1073a23-24); chapter 8 ('πότερον δὲ μίαν θετέον', 1073a14) begins on this page.",
    "294v": "Paris gr. 1853 fol. 294v begins '(ἀκί)νητον καὶ καθʼ αὑτὸ καὶ κατὰ συμβεβηκός, κινοῦν δὲ τὴν πρώτην ἀΐδιον καὶ μίαν κίνησιν' (1073a24-25) and ends 'τοῦ δὲ τῆς Ἀφροδίτης καὶ τοῦ Ἑρμοῦ τοὺς αὐτούς. Κάλλιππος δὲ τὴν' (1073b31-33).",
    "295r": "Paris gr. 1853 fol. 295r begins 'μὲν θέσιν τῶν σφαιρῶν τὴν αὐτὴν ἐτίθετο Εὐδόξῳ' (1073b33) and ends 'παραδέδοται δὲ ... ἐν μύθου σχήματι καταλελειμμένα τοῖς ὕστερον' (1074b1-3).",
    "295v": "Paris gr. 1853 fol. 295v begins 'ὅτι θεοί τέ εἰσιν οὗτοι καὶ περιέχει τὸ θεῖον τὴν ὅλην φύσιν' (1074b3) and ends with the opening of chapter 10, 'ἐπισκεπτέον δὲ καὶ ποτέρως ἔχει ἡ τοῦ ὅλου φύσις τὸ ἀγαθὸν καὶ τὸ ἄριστον' (1075a11-12); chapter 9 lies wholly on this page.",
    "296r": "Paris gr. 1853 fol. 296r begins '(πότερον) κεχωρισμένον τι καὶ αὐτὸ καθʼ αὑτό, ἢ τὴν τάξιν, ἢ ἀμφοτέρως' (1075a12-13) and ends 'καὶ τοῖς μὲν ἄλλοις ἀνάγκη τῇ σοφίᾳ καὶ τῇ τιμιωτάτῃ ἐπιστήμῃ εἶναί τι ἐναντίον, ἡμῖν δʼ οὔ· οὐ γάρ ἐστιν' (1075b20-21).",
    "296v": None,  # filled in PAGE_296V below after reading
}
PAGE_296V = ("Paris gr. 1853 fol. 296v begins 'ἐναντίον τῷ πρώτῳ οὐθέν. πάντα γὰρ τὰ ἐναντία ὕλην ἔχει' (1075b22) and ends in the first chapter of book 13 (Mu, 1076a), "
             "so the end of book 12 ('εἷς κοίρανος ἔστω', 1076a4) is on this page.")

# chapter -> pages
CHAPTERS = [
    ("12.6", "6", "Metaphysics 12.6, 1071b3-1072a18", ["293r", "293v"]),
    ("12.7", "7", "Metaphysics 12.7, 1072a19-1073a13", ["293v", "294r"]),
    ("12.8", "8", "Metaphysics 12.8, 1073a14-1074b14", ["294r", "294v", "295r", "295v"]),
    ("12.9", "9", "Metaphysics 12.9, 1074b15-1075a10", ["295v"]),
    ("12.10", "10", "Metaphysics 12.10, 1075a11-1076a4", ["295v", "296r", "296v"]),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def services():
    m = json.loads((SRC / "grec1853-manifest.json").read_text(encoding="utf-8"))
    return {c["label"]["fr"][0]: c["items"][0]["items"][0]["body"]["service"][0]["id"] for c in m["items"]}


def get_scan(folio, svc, force):
    path = SCAN_DIR / f"grec1853-f{folio}.jpg"
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"{svc[folio]}/full/1700,/0/default.jpg"))).convert("RGB")
    if max(img.size) > 2600:
        img.thumbnail((2600, 2600))
    img.save(path, quality=85)
    return path


def greek_chapters(path, book):
    root = ET.parse(path).getroot()
    body = root.find(f".//{TEI}body")
    out, st = {}, {"book": None, "ch": None, "buf": []}

    def flush():
        t = re.sub(r"\s+", " ", "".join(st["buf"])).strip()
        if t and st["book"] == book:
            out[st["ch"]] = (out.get(st["ch"], "") + " " + t).strip()
        st["buf"] = []

    def walk(el):
        tag = el.tag.replace(TEI, "")
        if tag == "div" and el.get("subtype") == "book":
            flush(); st["book"] = el.get("n")
        elif tag == "div" and el.get("subtype") in ("section", "chapter"):
            flush(); st["ch"] = el.get("n")
        if tag in ("milestone", "note", "bibl", "head"):
            return
        if tag == "del":
            st["buf"].append("[")
        if el.text:
            st["buf"].append(el.text)
        for ch in el:
            walk(ch)
            if ch.tail:
                st["buf"].append(ch.tail)
        if tag == "del":
            st["buf"].append("]")
        if tag in ("p", "l"):
            st["buf"].append(" ")

    walk(body)
    flush()
    return {k: re.sub(r"\s+([,.;·:?!])", r"\1", v) for k, v in out.items()}


def english_parts(path):
    s = path.read_text(encoding="latin-1")
    s = s[s.find("<B>Part 1</B>"):s.find('<A NAME="end">')]
    parts = re.split(r"<B>Part (\d+)</B>", s)
    out = {}
    for i in range(1, len(parts), 2):
        n, body = parts[i], parts[i + 1]
        paras = []
        for chunk in re.split(r"<BR><BR>", body):
            t = html.unescape(re.sub(r"<[^>]+>", " ", chunk))
            t = re.sub(r"\s+", " ", t).strip()
            if t.startswith('"'):
                t = t[1:].strip()
            if t.endswith('"'):
                t = t[:-1].strip()
            if t:
                paras.append(t)
        out[n] = paras
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    assert PAGE_296V, "fol. 296v note missing"
    PAGES["296v"] = PAGE_296V
    grc = greek_chapters(SRC / "tlg0086.tlg025.perseus-grc2.xml", "12")
    eng = english_parts(SRC / "mit-metaphysics-12.html")
    svc = services()
    files = {f: get_scan(f, svc, args.force) for f in PAGES}
    for f, p in files.items():
        print(f"  fol. {f}: {p.stat().st_size} bytes")
    sections = []
    for sid, ch, cite, pages in CHAPTERS:
        note = " ".join(PAGES[p] for p in pages)
        note += (" Checked on the images; viewer " + " , ".join(f"{ARK}/{svc[p].rsplit('/', 1)[1]}.item" for p in pages) +
                 " . The Greek shown is Ross's critical text; the copyist's wording differs from it in places.")
        sections.append({
            "section": sid,
            "original_ref": f"Aristotle, {cite}; Paris gr. 1853 fol. " + ", ".join(pages),
            "original_text": esc(grc[ch]),
            "text": "<br><br>".join(esc(p) for p in eng[ch]),
            "scan_pages": [f"{KEY}/{files[p].name}" for p in pages],
            "scan_note": note,
        })
    entry = {
        "id": TID, "slug": TID,
        "title": "Aristotle, Metaphysics 12.6-10 (Lambda): the unmoved mover and the life of god",
        "language": "Greek (Ross 1924) / English (W. D. Ross 1928)",
        "source": "Paris gr. 1853 fol. 293r-296v (Gallica, 10th c.) + Ross Greek (Perseus) + W. D. Ross English (1928, MIT Internet Classics Archive)",
        "description": "Aristotle's account of the first principle: an eternal, unmoved substance whose activity is thought, 'thought thinking itself'; its life is 'the best and eternal', and 'this is God' (1072b). Shown on Paris gr. 1853, a 10th-century manuscript.",
        "introduction": (
            "<p>Book 12 (Lambda) of the <em>Metaphysics</em> is Aristotle's theology. Chapter 6 argues that since motion and time are eternal there must be an eternal substance that is pure activity, without matter. "
            "Chapter 7 describes it: it moves the heavens without being moved, 'as the object of love moves'; its activity is thinking, and 'the activity of thought is life, and God is that activity; "
            "and God's essential activity is life most good and eternal' (1072b26-28). Chapter 8 asks how many such movers there are, using the astronomy of Eudoxus and Callippus, and mentions the ancient tradition that the heavenly bodies are gods. "
            "Chapter 9 concludes that divine thought thinks itself, 'its thinking is a thinking on thinking' (1074b34). Chapter 10 asks how the good is present in the universe, both as its order and as its ruler, and ends with Homer's line 'The rule of many is not good; one ruler let there be.' "
            "Ancient and medieval readers, pagan, Jewish, Christian and Muslim, built on these chapters when they spoke of God as mind and of the human mind's likeness to him.</p>\n\n"
            "<p>The pages shown are from Paris, Bibliotheque nationale de France, grec 1853 (siglum E), a 10th-century collection of Aristotle's works with scholia, fol. 293r-296v, about 47 lines to the page. "
            "Each section below is one chapter, linked to the pages that carry it; the pages were identified by reading the first and last lines of each page on the images. "
            "Chapters are used because the English translation used here has no Bekker line markers. The Greek is Ross's critical text, not a transcription of the manuscript.</p>"
        ),
        "translator_notes": [
            "Greek: W. D. Ross, Aristotle's Metaphysics (Oxford, 1924), Perseus digital text. Square brackets mark words Ross deletes.",
            "English: W. D. Ross's translation in the revised Oxford edition (1928), as given by the MIT Internet Classics Archive. The archive's quotation marks around each paragraph are formatting and have been removed.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Bibliotheque nationale de France, Gallica (IIIF), grec 1853 fol. 293r-296v: {ARK}",
            "scan_license": "Source gallica.bnf.fr / BnF. Non-commercial reuse is free with credit under the Gallica terms of use.",
            "scan_manuscript": "Paris, Bibliotheque nationale de France, grec 1853 (Aristotle E), parchment, 10th century, physical works, Metaphysics (from fol. 225v), Ethics, with scholia; former owner Cardinal Niccolo Ridolfi",
            "scan_mapping": "First and last lines of every page read on the images and matched to Ross's Greek (quoted per page in each scan_note); contents from the BnF description in the Gallica manifest and Pinakes diktyon 51479",
            "scan_mapping_urls": [ARK, "https://pinakes.irht.cnrs.fr/notices/cote/51479/"],
            "scan_local_paths": [f"{KEY}/{p.name}" for p in files.values()],
            "original_text_source": f"W. D. Ross, Aristotle's Metaphysics (Oxford, 1924), Perseus canonical-greekLit tlg0086.tlg025.perseus-grc2 ({PERSEUS})",
            "original_text_license": "edition public domain in the US (1924); Perseus digital text CC BY-SA 4.0",
            "translation_source": f"W. D. Ross, Metaphysica, The Works of Aristotle vol. VIII, 2nd ed. (Oxford: Clarendon Press, 1928), text from the MIT Internet Classics Archive: {MIT}",
            "translation_license": "public domain in the US (published 1928)",
            "translator": "W. D. Ross (1928)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.joinpath(f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "aristotle",
        "language": "Greek", "era": "Classical", "tradition": "greek", "category": "philosophy",
        "date_approx": "c. 340s-330s BCE (composition); manuscript 10th c.", "century": -4,
        "source": entry["source"], "description": entry["description"],
        "themes": ["aristotle", "metaphysics", "lambda", "unmoved-mover", "nous", "thought-thinking-itself", "theology", "theosis", "philosophy", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{p.name}", "caption": f"Paris gr. 1853 fol. {f}"} for f, p in files.items()]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Aristotle: the unmoved mover",
            "group": "Greece", "date_sort": -335,
            "author_name": "Aristotle (384-322 BCE); Paris manuscript of the 10th century",
            "source_url": ARK,
            "critical_edition": "Ross, Aristotle's Metaphysics (1924), via Perseus",
            "translator_name": "W. D. Ross (1928)",
            "original_lang_label": "Greek · Ross",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "aristotle metaphysics lambda unmoved mover thought thinking itself noesis noeseos god",
            "description": "Aristotle's theology in Metaphysics Lambda, shown on a 10th-century Paris manuscript.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
