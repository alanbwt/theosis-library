#!/usr/bin/env python3
"""
import_aristotle-ethics.py: Aristotle, Nicomachean Ethics 10.7-10.8 (1177a12-1179a32),
the life of contemplation as the divine life in man.

One entry; one section per Bekker column within a chapter (e.g. 10.7, 1177b), each
linked to the manuscript page(s) that carry its words.

Chain of evidence
  1. MANUSCRIPTS
     Florence, Biblioteca Medicea Laurenziana, Plut. 81.11 (siglum Kb, 10th c.),
     Teca Digitale IIIF manifest
     https://tecabml.contentdm.oclc.org/iiif/2/plutei:917185/manifest.json
     (Pinakes diktyon 16748: Ethica Nicomachea fol. 1-128).
     Kb has lost the text 1176a10-1177a30 between fol. 121r and fol. 121v (fol. 121r
     ends 'τὰς δὲ τῶν αὐτῶν ἀδιαφόρους εὔλογον εἶναι. διαλλάττουσι', 1176a10;
     fol. 121v begins '-μένων ὁ μὲν δίκαιος δεῖται πρὸς οὓς', 1177a30), so the
     opening of 10.7 (1177a12-30) is shown on
     Paris, BnF, grec 1854 (siglum Lb, 12th c.), Gallica IIIF ark:/12148/btv1b52511833m
     (colour digitization of the original; Pinakes diktyon 51480: Ethica fol. 1-188).
  2. MAPPING  First and last lines of every page read on the images and matched to
     Bywater's text (PAGES below; quoted in each scan_note). No page was placed by
     counting or by text length.
  3. GREEK    I. Bywater, Aristotelis Ethica Nicomachea (Oxford Classical Texts, 1894),
     Perseus canonical-greekLit tlg0086.tlg010.perseus-grc2 (CC BY-SA 4.0). Split at the
     chapter divisions and the Bekker page/column milestones of the digital text.
  4. ENGLISH  H. Rackham, Aristotle: The Nicomachean Ethics (Loeb Classical Library,
     1926; public domain in the US, published before 1930), Perseus
     tlg0086.tlg010.perseus-eng2 (CC BY-SA 4.0 digital text). Split at the same
     chapter divisions and at Rackham's own Bekker page milestones.

Usage:
    python3 scripts/import_aristotle-ethics.py [--force]
"""

import argparse
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

KEY = "aristotle-ethics"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TID = PREFIX + "nicomachean-10-7-8"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
PERSEUS = "https://github.com/PerseusDL/canonical-greekLit/tree/master/data/tlg0086/tlg010"

MSS = {
    "kb": {"manifest": SRC / "laur81.11-manifest.json", "short": "Laur. Plut. 81.11 (Kb)", "file": "laur81.11",
           "viewer": "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/917185"},
    "lb": {"manifest": SRC / "grec1854-manifest.json", "short": "Paris gr. 1854 (Lb)", "file": "grec1854",
           "viewer": "https://gallica.bnf.fr/ark:/12148/btv1b52511833m/{f}.item"},
}

PAGES = {
    ("lb", "177r"): "Paris gr. 1854 fol. 177r: the first line of text reads '(εὐδαι)μονικωτέρα ἤδη. ἀπολαύσειε' (1177a6); chapter 10.7 begins at the end of line 9 ('εἰ δʼ', with 'ἐστὶν ἡ εὐδαιμονία κατʼ ἀρετὴν ἐνέργεια' on line 10). The page ends in 1177a21, just before 'θεωρεῖν τε γὰρ δυνάμεθα', the first words of fol. 177v. The margins and the spaces between the lines carry scholia.",
    ("lb", "177v"): "Paris gr. 1854 fol. 177v begins 'θεωρεῖν τε γὰρ δυνάμεθα συνεχῶς μᾶλλον ἢ πράττειν ὁτιοῦν' (1177a21-22) and ends 'δόξειε δʼ ἂν αὐτὴ μόνη διʼ αὑτὴν ἀγαπᾶσθαι· οὐδὲν γὰρ' (1177b1-2).",
    ("kb", "121v"): "Laur. Plut. 81.11 fol. 121v begins '(κεχορηγη)μένων ὁ μὲν δίκαιος δεῖται πρὸς οὓς δικαιοπραγήσει' (1177a29-30) and ends 'αὗται δʼ ἄσχολοι καὶ τέλους τινὸς ἐφίενται καὶ' (1177b17-18).",
    ("kb", "122r"): "Laur. Plut. 81.11 fol. 122r begins 'οὐ διʼ αὑτὰς αἱρεταί εἰσιν, ἡ δὲ τοῦ νοῦ ἐνέργεια σπουδῇ' (1177b18-19) and ends 'καὶ τῷ ἀνθρώπῳ δὴ ὁ κατὰ τὸν νοῦν βίος, εἴπερ τοῦτο' (1178a6-7).",
    ("kb", "122v"): "Laur. Plut. 81.11 fol. 122v begins 'μάλιστα ἄνθρωπος. οὗτος ἄρα καὶ εὐδαιμονέστατος' (1178a7-8); chapter 10.8 begins on line 2 ('δευτέρως δʼ ὁ κατὰ τὴν ἄλλην ἀρετήν'); the page ends 'προσποιοῦνται δὲ καὶ οἱ μὴ δίκαιοι βούλεσθαι δι(καιοπραγεῖν)' (1178a30-31).",
    ("kb", "123r"): "Laur. Plut. 81.11 fol. 123r begins '(δι)καιοπραγεῖν ... δυνάμεως, εἴπερ ἐπιτελεῖ τι' (1178a31-32) and ends 'καθεύδειν ὥσπερ τὸν Ἐνδυμίωνα. τῷ δὴ ζῶντι τοῦ πράτ(τειν)' (1178b19-20).",
    ("kb", "123v"): "Laur. Plut. 81.11 fol. 123v begins '(πράτ)τειν ἀφαιρουμένου, ἔτι δὲ μᾶλλον τοῦ ποιεῖν, τί λείπεται πλὴν θεωρία' (1178b20-21) and ends 'οὐχ ἧττον δοκοῦσι τὰ ἐπιεικῆ πράττειν, ἀλλὰ' (1179a7-8).",
    ("kb", "124r"): "Laur. Plut. 81.11 fol. 124r begins '(καὶ) μᾶλλον. ἱκανὸν δὲ τοσαῦθʼ ὑπάρχειν· ἔσται γὰρ' (1179a8-9) and ends 'σοφῷ μάλισθʼ ὑπάρχει, οὐκ ἄδηλον. θεοφιλέστατος' (1179a29-30).",
    ("kb", "124v"): "Laur. Plut. 81.11 fol. 124v begins 'ἄρα. τὸν αὐτὸν δʼ εἰκὸς καὶ εὐδαιμονέστατον· ὥστε κἂν οὕτως' (1179a30-31); chapter 10.8 ends on line 2 ('εἴη ὁ σοφὸς μάλιστʼ εὐδαίμων'), where chapter 10.9 begins ('ἆρʼ οὖν εἰ περὶ τούτων').",
}

# section -> (chapter, bekker column, citation, pages)
SECTIONS = [
    ("10.7-1177a", "7", "1177a", "NE 10.7, 1177a12-35", [("lb", "177r"), ("lb", "177v"), ("kb", "121v")],
     "Kb lacks 1177a12-30 (loss between fol. 121r and 121v), so the start of the chapter is shown on Lb fol. 177r-177v; from 1177a30 ('-μένων ὁ μὲν δίκαιος') the text is on Kb fol. 121v."),
    ("10.7-1177b", "7", "1177b", "NE 10.7, 1177b1-34", [("kb", "121v"), ("kb", "122r")],
     "The words 'we must, as far as we can, make ourselves immortal' (ἐφʼ ὅσον ἐνδέχεται ἀθανατίζειν, 1177b33) are on fol. 122r."),
    ("10.7-1178a", "7", "1178a", "NE 10.7, 1178a1-8", [("kb", "122r"), ("kb", "122v")], ""),
    ("10.8-1178a", "8", "1178a", "NE 10.8, 1178a9-35", [("kb", "122v"), ("kb", "123r")], ""),
    ("10.8-1178b", "8", "1178b", "NE 10.8, 1178b1-35", [("kb", "123r"), ("kb", "123v")], ""),
    ("10.8-1179a", "8", "1179a", "NE 10.8, 1179a1-32", [("kb", "123v"), ("kb", "124r"), ("kb", "124v")], ""),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def services(ms):
    m = json.loads(MSS[ms]["manifest"].read_text(encoding="utf-8"))
    if "items" in m:
        return {c["label"]["fr"][0]: c["items"][0]["items"][0]["body"]["service"][0]["id"] for c in m["items"]}
    return {c["label"].replace("Carta: ", ""): c["images"][0]["resource"]["service"]["@id"] for c in m["sequences"][0]["canvases"]}


def get_scan(ms, folio, svc, force):
    path = SCAN_DIR / f"{MSS[ms]['file']}-f{folio}.jpg"
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"{svc[folio]}/full/1700,/0/default.jpg"))).convert("RGB")
    if max(img.size) > 2600:
        img.thumbnail((2600, 2600))
    img.save(path, quality=85)
    return path


def bekker_segments(path, book):
    """Split at chapter divs and Bekker page milestones -> {(chapter, page): text}."""
    root = ET.parse(path).getroot()
    body = root.find(f".//{TEI}body")
    out = {}
    st = {"book": None, "ch": None, "page": None, "buf": []}

    def flush():
        t = re.sub(r"\s+", " ", "".join(st["buf"])).strip()
        if t and st["book"] == book:
            k = (st["ch"], st["page"])
            out[k] = (out.get(k, "") + " " + t).strip()
        st["buf"] = []

    def walk(el):
        tag = el.tag.replace(TEI, "")
        if tag == "div" and el.get("subtype") == "book":
            flush(); st["book"] = el.get("n")
        elif tag == "div" and el.get("subtype") == "section":
            flush(); st["ch"] = el.get("n")
        if tag == "milestone":
            if el.get("unit") == "page":
                flush(); st["page"] = el.get("n")
            return
        if tag in ("note", "bibl", "head"):
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


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    grc = bekker_segments(SRC / "tlg0086.tlg010.perseus-grc2.xml", "10")
    eng = bekker_segments(SRC / "tlg0086.tlg010.perseus-eng2.xml", "10")
    svc = {ms: services(ms) for ms in MSS}
    files = {}
    for (ms, f) in PAGES:
        files[(ms, f)] = get_scan(ms, f, svc[ms], args.force)
        print(f"  {ms} {f}: {files[(ms, f)].stat().st_size} bytes")

    def viewer(ms, f):
        return MSS[ms]["viewer"].format(f=svc[ms][f].rsplit("/", 1)[1]) if ms == "lb" else MSS[ms]["viewer"]

    sections = []
    for sid, ch, page, cite, pages, extra in SECTIONS:
        g, e = grc[(ch, page)], eng[(ch, page)]
        note = " ".join(PAGES[p] for p in pages)
        if extra:
            note = extra + " " + note
        note += " Checked on the images. The Greek shown is Bywater's critical text; the copyists' wording differs from it in small details."
        sections.append({
            "section": sid,
            "original_ref": f"Aristotle, {cite}; " + "; ".join(f"{MSS[ms]['short']} fol. {f}" for ms, f in pages),
            "original_text": esc(g),
            "text": esc(e),
            "scan_pages": [f"{KEY}/{files[p].name}" for p in pages],
            "scan_note": note,
        })
    all_pages = list(PAGES)
    entry = {
        "id": TID, "slug": TID,
        "title": "Aristotle, Nicomachean Ethics 10.7-10.8: the life of the mind as a divine life",
        "language": "Greek (Bywater) / English (Rackham 1926)",
        "source": "Laur. Plut. 81.11 fol. 121v-124v (Teca Digitale, 10th c.) and Paris gr. 1854 fol. 177r-177v (Gallica, 12th c.) + Bywater Greek (Perseus) + H. Rackham English (Perseus)",
        "description": "Aristotle's argument that the highest happiness is the activity of contemplation, a life 'higher than human' lived by the divine element in us: 'we must, as far as we can, make ourselves immortal' (1177b33). Shown on the oldest manuscript, Laur. Plut. 81.11 (10th c.), with its lost leaf supplied from Paris gr. 1854.",
        "introduction": (
            "<p>In the last book of the <em>Nicomachean Ethics</em> Aristotle asks what the happiest life is. Happiness is activity in accordance with the highest virtue, "
            "and the highest part of us is the intellect (<em>nous</em>), 'whether it be itself divine or only the most divine element in us'. "
            "Its activity, contemplation (<em>theoria</em>), is the most continuous, the most pleasant, the most self-sufficient and the only activity loved for its own sake. "
            "Such a life 'would be higher than the human level': a man lives it not in so far as he is human but in so far as something divine is present in him. "
            "So we should not follow those who advise us to think human thoughts because we are human, 'but we must, as far as we can, make ourselves immortal' (1177b33). "
            "Chapter 8 adds that the gods are blessed because they contemplate, and that the wise man, whose activity is most like theirs, is the one most loved by the gods. "
            "Later Greek Christian writers drew on these chapters when they spoke of contemplation and deification.</p>\n\n"
            "<p>The main witness is Florence, Biblioteca Medicea Laurenziana, Plut. 81.11 (siglum Kb), written in the 10th century, the oldest manuscript of the Ethics. "
            "Between its fol. 121r and fol. 121v the text 1176a10-1177a30 is missing (fol. 121r ends at 1176a10 and fol. 121v begins at 1177a30), "
            "so the opening of chapter 7 (1177a12-30) is shown on Paris, BnF, grec 1854 (siglum Lb, 12th century), fol. 177r-177v, a large-format copy with scholia around and between the lines. "
            "Each section is one Bekker column within a chapter; the pages listed for it were identified by reading the first and last lines of each page on the images. "
            "The Greek is Bywater's critical text, not a transcription of either manuscript. Chapter 6 (1176a30-1177a11), which falls in the gap in Kb, is not included.</p>"
        ),
        "translator_notes": [
            "Greek: I. Bywater, Aristotelis Ethica Nicomachea (Oxford Classical Texts, 1894), Perseus digital text. Square brackets mark words Bywater deletes.",
            "English: H. Rackham, The Nicomachean Ethics (Loeb Classical Library, 1926), Perseus digital text. The English is divided at Rackham's own Bekker page markers, so a few words may fall on the neighbouring side of a break compared with the Greek.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": "Biblioteca Medicea Laurenziana, Teca Digitale (IIIF), Plut. 81.11 fol. 121v-124v: https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/917185 ; Bibliotheque nationale de France, Gallica (IIIF), grec 1854 fol. 177r-177v: https://gallica.bnf.fr/ark:/12148/btv1b52511833m",
            "scan_license": "Laurenziana: access rights stated as 'Pubblico' in the Teca Digitale record; reproduced for non-commercial scholarly use with credit to the Biblioteca Medicea Laurenziana (MiC). Gallica: source gallica.bnf.fr / BnF, non-commercial reuse free with credit under the Gallica terms of use.",
            "scan_manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 81.11 (Kb), parchment, 10th century, Nicomachean Ethics fol. 1-128 (former owner Francesco Filelfo); Paris, Bibliotheque nationale de France, grec 1854 (Lb), parchment, 12th century, Nicomachean Ethics with scholia fol. 1-188",
            "scan_mapping": "First and last lines of every page read on the images and matched to Bywater's text (quoted per page in each scan_note); folio ranges of the Ethics in both manuscripts from Pinakes (diktyon 16748, 51480)",
            "scan_mapping_urls": ["https://pinakes.irht.cnrs.fr/notices/cote/16748/", "https://pinakes.irht.cnrs.fr/notices/cote/51480/",
                                  MSS["kb"]["viewer"], "https://gallica.bnf.fr/ark:/12148/btv1b52511833m"],
            "scan_local_paths": [f"{KEY}/{files[p].name}" for p in all_pages],
            "original_text_source": f"I. Bywater, Aristotelis Ethica Nicomachea (Oxford, 1894), Perseus canonical-greekLit tlg0086.tlg010.perseus-grc2 ({PERSEUS})",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": f"H. Rackham, Aristotle: The Nicomachean Ethics (Loeb Classical Library, Harvard University Press / Heinemann, 1926), Perseus tlg0086.tlg010.perseus-eng2 ({PERSEUS})",
            "translation_license": "public domain in the US (published 1926); Perseus digital text CC BY-SA 4.0",
            "translator": "H. Rackham (1926)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.joinpath(f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "aristotle",
        "language": "Greek", "era": "Classical", "tradition": "greek", "category": "philosophy",
        "date_approx": "c. 330s BCE (composition); manuscripts 10th and 12th c.", "century": -4,
        "source": entry["source"], "description": entry["description"],
        "themes": ["aristotle", "nicomachean-ethics", "contemplation", "theoria", "nous", "immortality", "becoming-like-god", "theosis", "philosophy", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[p].name}", "caption": f"{MSS[p[0]]['short']} fol. {p[1]}"} for p in all_pages]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Aristotle: the contemplative life",
            "group": "Greece", "date_sort": -330,
            "author_name": "Aristotle (384-322 BCE); Laurenziana manuscript of the 10th century",
            "source_url": MSS["kb"]["viewer"],
            "critical_edition": "Bywater, Ethica Nicomachea (1894), via Perseus",
            "translator_name": "H. Rackham (1926)",
            "original_lang_label": "Greek · Bywater",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "aristotle nicomachean ethics contemplation theoria nous divine immortal athanatizein",
            "description": "Aristotle on contemplation as the most divine human activity, shown on the oldest manuscript of the Nicomachean Ethics.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
