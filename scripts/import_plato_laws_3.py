#!/usr/bin/env python3
"""
import_plato_laws_3.py - Plato, Laws book 3, 676a-683a: the floods that destroy civilization, the
survivors on the mountain tops, and the slow rebirth of society from households to cities, on the
pages of Paris gr. 1807 (Plato "A", 9th century).

Two entries, 34 sections (one per Stephanus section 676a ... 683a).

Chain of evidence:
  1. SCAN     Paris, BnF, grec 1807 (copied c. 850-875 at Constantinople, the "philosophical
              collection"; Laws on fols. 155r-291r, book 3 on fols. 174r-184v), two columns of 44
              lines. Gallica ark:/12148/btv1b8419248n, IIIF via openapi.bnf.fr, colour, digitized
              from the original. Gallica terms: non-commercial reuse with credit.
  2. MAPPING  By eye on the downloaded images: the first and last words of both columns of fols.
              174r-176r and the opening of fol. 176v were read and found in Burnet's text
              (COLUMN_NOTES). Each section points at the page(s) carrying it; the notes give the
              column(s). Sections running across a page break list both pages.
  3. GREEK    J. Burnet, Platonis opera vol. 5 (Oxford, 1907; 1915 printing), Perseus canonical-greekLit
              tlg0059.tlg034.perseus-grc2 (CC BY-SA 4.0). Compared with the archive.org OCR of
              Burnet's printed page (p1platonisopera05platuoft): every difference was an OCR fault.
  4. ENGLISH  R. G. Bury, Plato: Laws, vol. 1 (Loeb Classical Library, 1926), Perseus
              tlg0059.tlg034.perseus-eng2. Public domain in the US (published 1926). Compared word by
              word with the OCR of the 1926 printing (archive.org bwb_C0-AUM-876_9); Perseus'
              American spellings were restored to the printed forms and verse lines run together
              were separated (EN_FIXES); "household system" was checked on the page image.

Usage:
    python3 scripts/import_plato_laws_3.py           # build
    python3 scripts/import_plato_laws_3.py --force   # re-download scans
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

ROOT = Path(__file__).resolve().parent.parent
KEY = "plato-laws-3"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
ARK = "btv1b8419248n"
GALLICA = f"https://gallica.bnf.fr/ark:/12148/{ARK}"
PERSEUS = "https://github.com/PerseusDL/canonical-greekLit/tree/master/data/tlg0059/tlg034"
BURNET_SCAN = "https://archive.org/details/p1platonisopera05platuoft"
BURY_SCAN = "https://archive.org/details/bwb_C0-AUM-876_9"

FOLIOS = ["174r", "174v", "175r", "175v", "176r", "176v"]
COLUMN_NOTES = {
    "174r": "Fol. 174r: the title 'πλάτωνος νόμοι ἢ νομοθεσίαι με´' stands over column a, which begins 'ταῦτα μὲν οὖν δὴ ταύτῃ· πολιτείας δὲ ἀρχὴν' (676a) and ends in 677a '...κατακλυσμοῖς τε καὶ νόσοις καὶ ἄλ-'; column b begins '-λοις πολλοῖς, ἐν οἷς βραχύ τι τῶν ἀνθρώπων' and ends in 677d '...Μαρσύᾳ καὶ Ὀλύμπῳ, περὶ'.",
    "174v": "Fol. 174v: column a begins 'λύραν δὲ Ἀμφίονι' (677d) and ends in 678b '...οὐκοῦν προϊόντος μὲν τοῦ χρό-'; column b begins '-νου, πληθύοντος δ’ ἡμῶν τοῦ γένους' and ends in 678e '...ἐφιλοφρονοῦντο ἀλλήλους δι’ ἐρημίαν'.",
    "175r": "Fol. 175r: column a begins 'ἔπειτα οὐ περιμάχητος ἦν αὐτοῖς ἡ τροφή' (678e) and ends in 679c '...ἀληθῆ νομίζοντες ἔζων κατὰ ταῦτα'; column b begins 'διόπερ ἦσαν τοιοῦτοι παντάπασιν' and ends in 680b '...καὶ νῦν ἔτι πολλαχοῦ καὶ ἐν Ἕλλη-'.",
    "175v": "Fol. 175v: column a begins '-σι καὶ κατὰ βαρβάρους ἐστίν' (680b) and ends in 680e '...πόλεις πλείους συνέρχον-'; column b begins '-ται, καὶ ἐπὶ γεωργίας τὰς ἐν ταῖς ὑπωρείαις' and ends in 681d '...οἷον βασιλεῦσι φανερὰ δείξαντες'.",
    "176r": "Fol. 176r: column a begins 'ἑλέσθαι τε δόντες, αὐτοὶ μὲν νομοθέται κληθήσονται' (681d) and ends in 682b '...ἐν πολλοῖς τισι χρόνοις τοῖς με-'; column b begins '-τὰ τὸν κατακλυσμὸν τοῦτο οἰόμεθα γεγονέναι' and ends in 682e '...ὅθεν δὴ κατ’ ἀρχὰς ἐξετραπόμεθα περὶ νόμων'.",
    "176v": "Fol. 176v: column a begins 'διαλεγόμενοι, περιπεσόντες μουσικῇ τε καὶ ταῖς μέθαις' (682e); 683a begins on line 7 'κατοίκισιν αὐτήν' and ends on line 24 '...καὶ νῦν κατῳκισμένον', where 683b 'ἐξ ὧν' follows.",
}
# Stephanus section -> [(folio, columns)]
LOC = {
    "676a": [("174r", "a")], "676b": [("174r", "a")], "676c": [("174r", "a")],
    "677a": [("174r", "a-b")], "677b": [("174r", "b")], "677c": [("174r", "b")],
    "677d": [("174r", "b"), ("174v", "a")], "677e": [("174v", "a")], "678a": [("174v", "a")],
    "678b": [("174v", "a-b")], "678c": [("174v", "b")], "678d": [("174v", "b")],
    "678e": [("174v", "b"), ("175r", "a")], "679a": [("175r", "a")], "679b": [("175r", "a")],
    "679c": [("175r", "a-b")], "679d": [("175r", "b")], "679e": [("175r", "b")], "680a": [("175r", "b")],
    "680b": [("175r", "b"), ("175v", "a")], "680c": [("175v", "a")], "680d": [("175v", "a")],
    "680e": [("175v", "a-b")], "681a": [("175v", "b")], "681b": [("175v", "b")], "681c": [("175v", "b")],
    "681d": [("175v", "b"), ("176r", "a")], "681e": [("176r", "a")], "682a": [("176r", "a")],
    "682b": [("176r", "a-b")], "682c": [("176r", "b")], "682d": [("176r", "b")],
    "682e": [("176r", "b"), ("176v", "a")], "683a": [("176v", "a")],
}
SECTIONS = list(LOC)
EN_FIXES = [("connection", "connexion"), ("neighbors", "neighbours"), ("men of today", "men of to-day"),
             ("name of headship to", "name of \u201cheadship\u201d to")]

ENTRIES = [
    ("floods-and-survivors", 1, "676a", "679e",
     "Plato, Laws 3.676a-679e: the floods and the survivors on the mountains",
     "The Athenian stranger on the vast age of human society: thousands of cities founded and destroyed, floods and plagues that left only a few herdsmen alive on the mountain tops, the loss of all arts and tools, and the simple, peaceful and honest life of the survivors, shown on the pages of Paris gr. 1807 that carry it."),
    ("rebirth-of-cities", 2, "680a", "683a",
     "Plato, Laws 3.680a-683a: from households to cities, Troy and the Dorians",
     "How government grew again after the flood: rule by the eldest in scattered households like Homer's Cyclopes, larger settlements in the foothills with the first lawgivers, the city in the plain at Troy, the Trojan War and the return of the exiles as Dorians, shown on the pages of Paris gr. 1807 that carry it."),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def canvas_index():
    m = json.loads((SRC / "grec1807-manifest.json").read_text(encoding="utf-8"))
    return {c["label"].get("fr", c["label"].get("none", [""]))[0]: i + 1 for i, c in enumerate(m["items"])}


def scan(folio, force, idx):
    path = SCAN_DIR / f"paris-gr-1807-f{folio}.jpg"
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"https://openapi.bnf.fr/iiif/image/v3/ark:/12148/{ARK}/f{idx[folio]}/full/,2400/0/default.jpg")))
    img.convert("RGB").save(path, quality=85)
    return path


def sections(version):
    root = ET.parse(SRC / f"tlg0059.tlg034.perseus-{version}.xml").getroot()
    book = [b for b in root.iter(f"{TEI}div") if b.get("subtype") == "book" and b.get("n") == "3"][0]
    out, state = {}, {"cur": None, "buf": []}

    def flush():
        if state["cur"]:
            out[state["cur"]] = out.get(state["cur"], "") + "".join(state["buf"])
        state["buf"] = []

    def walk(e):
        tag = e.tag.replace(TEI, "")
        if tag == "milestone" and e.get("unit") == "section":
            flush()
            state["cur"] = e.get("n")
            return
        if tag in ("note", "bibl"):
            return
        if tag == "label":
            state["buf"].append(f"[{''.join(e.itertext()).strip()}] ")
            return
        if tag == "l":
            state["buf"].append(" ")
        if e.text:
            state["buf"].append(e.text)
        for c in e:
            walk(c)
            if c.tail:
                state["buf"].append(c.tail)
        if tag in ("l", "p", "said", "sp"):
            state["buf"].append(" ")

    walk(book)
    flush()
    return {k: re.sub(r"\s+", " ", v).strip() for k, v in out.items() if k in LOC}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    g, e = sections("grc2"), sections("eng2")
    assert set(g) == set(LOC) == set(e), (set(LOC) - set(g), set(LOC) - set(e))
    text = "\u0000".join(e[k] for k in SECTIONS)
    for a, b in EN_FIXES:
        assert text.count(a) == 1, a
        text = text.replace(a, b)
    e = dict(zip(SECTIONS, text.split("\u0000")))
    for k in SECTIONS:
        assert not re.search(r"Hom\.|[a-z][A-Z]", e[k]), (k, e[k])
        assert not re.search(r"[A-Za-z]", re.sub(r"\[[^\]]*\]", "", g[k])), (k, g[k])
    idx = canvas_index()
    rel = {f: f"{KEY}/{scan(f, args.force, idx).name}" for f in FOLIOS}

    intro = (
        "<p>In book 3 of the <em>Laws</em>, Plato's last and longest dialogue (c. 350 BCE), an unnamed Athenian, the Cretan Clinias and the Spartan Megillus ask where political society began. "
        "The Athenian's answer is a history of the human race on a scale of tens of thousands of years: civilization has been destroyed many times by floods, plagues and other disasters, "
        "and after the last great flood only a few herdsmen survived on the mountain tops, without tools, metals or writing. "
        "He traces how they lived, how households under the rule of the eldest joined into villages and then into cities with lawgivers, and how the first city was built in the plain at Troy. "
        "The passage is the fullest statement in Plato of the cyclical destruction of civilization that the Egyptian priests describe to Solon in the <em>Timaeus</em> and <em>Critias</em>.</p>\n\n"
        "<p>The manuscript is Paris, Bibliothèque nationale de France, grec 1807 (Plato \"A\"), written at Constantinople in the third quarter of the 9th century, one of the two oldest and most authoritative manuscripts of the <em>Laws</em>. "
        "Book 3 begins on fol. 174r; the passage occupies fols. 174r-176v, two columns to the page. Each section is one Stephanus section and points at the page(s) that carry it; the column breaks were read on the images and are recorded in each note.</p>"
    )
    notes = [
        "Greek: John Burnet's Oxford text (1907), from Perseus. Speaker names are given in brackets as in the digital edition (ΑΘ. the Athenian, ΚΛ. Clinias, ΜΕ. Megillus). The manuscript's wording differs from the edition in small details.",
        "English: R. G. Bury's Loeb translation (1926), from Perseus, with the spellings of the printed book restored. Bury's section letters are placed in his margin and do not always fall at the same word as the Greek; the English sections follow Bury's letters.",
    ]
    rows = []
    for slug, order, a, b, title, desc in ENTRIES:
        keys = SECTIONS[SECTIONS.index(a):SECTIONS.index(b) + 1]
        fols = [f for f in FOLIOS if any(f == x for k in keys for x, _ in LOC[k])]
        secs = []
        for k in keys:
            loc = LOC[k]
            where = " and ".join(f"fol. {f} col. {c}" for f, c in loc)
            secs.append({
                "section": k,
                "original_ref": f"Plato, Laws 3.{k} (Burnet); Paris gr. 1807 {where}",
                "original_text": f"<sup>{k}</sup>{g[k]}",
                "text": f"<sup>{k}</sup>{e[k]}",
                "scan_pages": [rel[f] for f, _ in loc],
                "scan_note": f"{k} is on {where}. " + " ".join(COLUMN_NOTES[f] for f, _ in loc)
                             + f" Checked on the image. Viewer: {GALLICA}/f{idx[loc[0][0]]}.item",
            })
        tid = PREFIX + slug
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Greek (Burnet) / English (Bury 1926)",
            "source": "Paris gr. 1807 (9th c.) via Gallica + Burnet Greek (Perseus) + Bury English (Loeb 1926, Perseus)",
            "description": desc,
            "introduction": intro + f"\n\n<p>This entry covers Laws 3.{a}-{b} on fols. {fols[0]}-{fols[-1]}.</p>",
            "translator_notes": notes,
            "translation": secs,
            "verification": {
                "scan_source": f"Bibliothèque nationale de France, Gallica: Grec 1807, {GALLICA} (IIIF openapi.bnf.fr), fols. {fols[0]}-{fols[-1]}",
                "scan_license": "Gallica terms: free non-commercial reuse with the credit 'Source gallica.bnf.fr / BnF'",
                "scan_manuscript": "Paris, BnF, grec 1807 (Constantinople, c. 850-875), Plato tetralogies VIII-IX; Laws on fols. 155r-291r, book 3 on fols. 174r-184v",
                "scan_mapping": "Checked on the images: the first and last words of each column of fols. 174r-176r and the opening of fol. 176v were read and found in Burnet's text; each section's page(s) and column(s) follow from those breaks (see scan_note)",
                "scan_mapping_urls": [f"{GALLICA}/f{idx[f]}.item" for f in fols],
                "scan_local_paths": [rel[f] for f in fols],
                "original_text_source": f"J. Burnet, Platonis opera vol. 5 (Oxford: Clarendon Press, 1907; 1915 printing), Perseus tlg0059.tlg034.perseus-grc2 ({PERSEUS}); compared with {BURNET_SCAN}",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"R. G. Bury, Plato: Laws, vol. 1 (Loeb Classical Library; London: Heinemann / New York: Putnam, 1926), Perseus tlg0059.tlg034.perseus-eng2; compared with {BURY_SCAN}",
                "translation_license": "public domain in the US (published 1926); Perseus digital text CC BY-SA 4.0",
                "translator": "R. G. Bury (1926)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order, "title": title, "author_id": "plato",
            "language": "Greek", "era": "Classical", "tradition": "greek", "category": "philosophy",
            "date_approx": "c. 350 BCE (composition); c. 850-875 AD (Paris gr. 1807)", "century": -4,
            "source": entry["source"], "description": desc,
            "themes": ["plato", "laws", "flood", "deluge", "cataclysm", "origin-of-civilization", "troy", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": rel[f], "caption": f"Paris gr. 1807, fol. {f}"} for f in fols]},
        })
        print(f"  {tid}: {len(secs)} sections, fols {fols[0]}-{fols[-1]}")
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Plato, Laws book 3: the floods and the rebirth of civilization",
            "group": "Greece", "date_sort": -350,
            "author_name": "Plato (c. 350 BCE), Paris gr. 1807 (9th c.)",
            "source_url": GALLICA,
            "critical_edition": "J. Burnet, Platonis opera V (Oxford 1907), via Perseus",
            "translator_name": "R. G. Bury (1926)",
            "original_lang_label": "Greek · Burnet",
            "original_lang_code": "grc", "edition_label": "",
            "search_terms": "plato laws book 3 flood deluge cataclysm survivors mountains origin of government cyclopes troy dorians",
            "description": "Plato's account in Laws 3 of the floods that repeatedly destroyed civilization, the herdsmen who survived on the mountains, and the slow regrowth of society from households to cities, on the pages of the 9th-century Paris manuscript of Plato.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
