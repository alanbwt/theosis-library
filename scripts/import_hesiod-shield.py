#!/usr/bin/env python3
"""
import_hesiod-shield.py: [Hesiod], Shield of Heracles, on Florence, Biblioteca Medicea Laurenziana,
Plut. 32.16 (late 13th century), fols. 248r-251v.

Chain of evidence
  1. SCAN     BML Teca Digitale (CONTENTdm IIIF), manifest
              https://cdm21059.contentdm.oclc.org/iiif/plutei:596036/manifest.json
              (record: "VII. Eiusdem [Hesiodi] Scutum Herculis", rights CC BY-NC-SA). The poem
              begins on fol. 248r directly after the Theogony (247v) and ends on 251v.
  2. MAPPING  Each page's first and last verse were read on the page image (zoomed crops of the
              top and bottom rows) and matched to the Greek; consecutive pages were checked for
              continuity. Verses run two to a row across the page (one in the left column, the
              next in the right). Results are in PAGES below; every section's scan_note repeats them.
  3. GREEK    H. G. Evelyn-White (Loeb, 1914), Perseus canonical-greekLit
              tlg0020.tlg003.perseus-grc2 (CC BY-SA 4.0). Lines the editor brackets as spurious
              (<del>) are shown in square brackets. The edition has no line 298.
  4. ENGLISH  H. G. Evelyn-White (1914, public domain), Perseus tlg0020.tlg003.perseus-eng2,
              in blocks of about five lines; at each page break the English is cut at the end of
              Evelyn-White's sentence (ENGLISH_CUTS, chosen by reading the English against the Greek;
              scripts/qc4_hesiod_english.py), so a sentence that runs across a page break goes whole
              to one page and the scan_note gives the exact range.

Usage:  python3 scripts/import_hesiod-shield.py [--force]   (--force re-downloads scans)
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

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from qc4_hesiod_english import cut_english, english_note  # noqa: E402

KEY = "hesiod-shield"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "hesiod"
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"

GREEK_XML = SRC / "tlg0020.tlg003.perseus-grc2.xml"
ENGLISH_XML = SRC / "tlg0020.tlg003.perseus-eng2.xml"
GITHUB = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0020/tlg003/"
MANIFEST = "https://cdm21059.contentdm.oclc.org/iiif/plutei:596036/manifest.json"
RECORD = "https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/596036"
TOTAL = 480
MS = "Laur. Plut. 32.16"
MS_LONG = ("Florence, Biblioteca Medicea Laurenziana, Plut. 32.16 (paper, late 13th century; a large "
           "collection of Greek poetry that also holds letters of Maximus Planudes), Shield of Heracles on fols. 248r-251v")

# folio -> IIIF image service (from the manifest)
IIIF = {"248r": 595713, "248v": 595714, "249r": 595715, "249v": 595716, "250r": 595717, "250v": 595718,
        "251r": 595719, "251v": 595720}
EXCLUDE = set()
NOT_ON_PAGE = {}

# Verified on the images (see docstring).  first/last = edition line numbers on the page.
# Every page edge was re-read on the photograph on 2026-11-12 (QC fix: 248v ends at 130 and 249r
# begins at 131, not 128/129); read_first / read_last record the first and last row as read.
PAGES = [
    {"folio": "248r", "first": 1, "last": 64,
     "read_first": "1 | 2: Ἢ οἵη προλιποῦσα δόμους ... | ἤλυθεν ἐς Θήβας ...",
     "read_last": "63 | 64: ... ὑφ' ἅρμασι καὶ ποσὶν ἵππων | ... ἄντυγες ἀμφαράβιζον",
     "note": "The poem begins at the head of the page under the red title Ἡσιόδου ἀσπίς, with a large initial, directly after the Theogony on the previous page."},
    {"folio": "248v", "first": 65, "last": 130,
     "read_first": "65 | 66: ἵππων ἱεμένων κεχάρητο δὲ Κύκνος ἀμύμων | ἐλπόμενος Διὸς υἱὸν ...",
     "read_last": "129 | 130: δεινὸς ἀνήρ κοίλην δὲ ... φαρέτρην | κάββαλε τ' ἐξόπιθεν ... ὀϊστοί",
     "note": "The row above the last holds 127 | 128. (Corrected 2026-11-12: the page map had ended this page at 128.)"},
    {"folio": "249r", "first": 131, "last": 194,
     "read_first": "131 | 132: ῥιγηλοὶ θανάτοιο λαθιφθόγγοιο δοτῆρες | πρόσθεν μὲν θάνατόν τ' εἶχον ...",
     "read_last": "193 | 194: αἰχμὴν ἐν χείρεσσιν ἔχων ... | αἵματι φοινικόεις ... ἐναρίζων",
     "note": "A Latin pen note in the lower margin, in a later hand, is not part of the poem."},
    {"folio": "249v", "first": 195, "last": 262,
     "read_first": "195 | 196: δίφρου ἐπεμβεβαὼς παρὰ δὲ Δεῖμος ... | ἕστασαν ἱέμενοι ...",
     "read_last": "261 | 262: πᾶσαι δ' ἀμφ' ἑνὶ φωτὶ μάχην ... | δεινὰ δ' ἐς ἀλλήλας δράκον ...", "note": ""},
    {"folio": "250r", "first": 263, "last": 328,
     "read_first": "263 | a struck-through line: ἐν δ' ὄνυχας χεῖράς τε ... | (a cancelled repeat of 253, ... ἢ πίπτοντα νεούτατον ἀμφὶ μὲν αὐτῷ); row 2 is 264 | 265",
     "read_last": "327 | 328: χαίρετε Λυγκῆος γενεὴ τηλεκλειτοῖο | νῦν δὴ Ζεὺς κράτος ὔμμι ...",
     "note": "In the first row the right-hand verse is a repeat of 253, struck through by the scribe. The writing in the lower margin is not a verse: as far as it can be read it is a list of names (Lynceus, Abas, Acrisius, Danae, Perseus, Alcaeus, Amphitryon), a genealogy explaining Λυγκῆος γενεή in 327, which carries a mark."},
    {"folio": "250v", "first": 329, "last": 393,
     "read_first": "329 | 330: Κύκνον τ' ἐξεναρεῖν ... | ἄλλο δέ τοί τι ἔπος ἐρέω ...",
     "read_last": "392 | 393: τῷ ἴκελος Διὸς υἱὸς ... δίφρου | ἦμος δὲ χλοερῷ κυανόπτερος ἠχέτα τέττιξ",
     "note": "Verse 378 (ῥίμφα κυλινδομένων εἵως πεδίονδ' ἀφίκωνται) is left out of the column, where the row reads 377 | 379, and written below the last row, keyed by the sign that follows 377; the Greek shows it in its place. (Corrected 2026-11-12: this line had been described as a note.)"},
    {"folio": "251r", "first": 394, "last": 457,
     "read_first": "394 | 395: ὄζῳ ἐφεζόμενος θέρος ... | ἄρχεται ᾧ τε πόσις ...",
     "read_last": "456 | 457: ἔγχεος ὁρμὴν ἔτραπ' ὀρεξαμένη ... | δριμὺ δ' Ἄρην ἄχος εἷλε ... ἄορ ὀξύ", "note": ""},
    {"folio": "251v", "first": 458, "last": 480,
     "read_first": "458 | 459: ἔσσυτ' ἐφ' Ἡρακλῆα κρατερόφρονα ... | Ἀμφιτρυωνιάδης δεινῆς ἀκόρητος ἀυτῆς",
     "read_last": "480 | subscription: ὅστις ἄγοι Πυθοῖδε βίῃ σύλασκε δοκεύων | τέλος ἀσπίδος Ἡσιόδου",
     "note": "The poem ends with 480 in the twelfth row, in the upper part of the page, beside the subscription."},
]

# Evelyn-White's English is cut at the end of his sentences at each page break (QC fix 2026-11-12;
# scripts/qc4_hesiod_english.py). folio: (opening words of the sentence that begins the page's English,
# occurrence, first line it renders, last line of the previous page's English). Where his sentence runs
# across the break it goes whole to the side nearer its end; ties stay with the page where it begins.
ENGLISH_CUTS = {
    "248v": ("And blameless Cycnus was glad", 0, 65, 65),                  # sentence break inside 65
    "249r": ("Within it were many chilling arrows", 0, 130, 130),          # sentence break inside 130
    "249v": ("Beside him stood Fear and Flight", 0, 195, 195),             # sentence break inside 195
    "250r": ("By them stood Darkness of Death", 0, 264, 263),
    "250v": ("Yet I will tell you something besides", 0, 330, 329),        # 328-329: tie, kept with 250r
    "251r": ("And when the dark-winged whirring grasshopper", 0, 393, 392),
    "251v": ("But as he came on, the son of Amphitryon", 0, 458, 458),     # sentence break inside 458
}
ENGLISH_SPLITS = []
FIRST_LAST_WORDS = {}

# Episodes (boundaries fall on Evelyn-White's paragraph blocks)
ENTRIES = [
    (1, 77, "alcmene-and-the-birth-of-heracles", "Alcmene and the birth of Heracles; Cycnus at Pagasae",
     "Alcmene, wife of Amphitryon, bears Heracles to Zeus and Iphicles to her husband; Heracles finds Cycnus, son of Ares, at the grove of Apollo."),
    (78, 153, "the-arming-of-heracles", "Heracles and Iolaus; the arming of Heracles",
     "Heracles speaks with his charioteer Iolaus and puts on the armour given by the gods, and takes up his shield."),
    (154, 326, "the-shield", "The Shield: its scenes",
     "The scenes on the shield: Fear and Strife, boars and lions, the Lapiths and Centaurs, Perseus and the Gorgons, a city at war and a city at peace."),
    (327, 480, "the-fight-with-cycnus-and-ares", "The fight with Cycnus and Ares",
     "Athena advises Heracles, who kills Cycnus, wounds Ares and returns home; the burial of Cycnus."),
]


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


def scan_name(folio):
    return f"laur-32-16-f{folio}.jpg"


def get_scan(folio, force=False):
    path = SCAN_DIR / scan_name(folio)
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"https://cdm21059.contentdm.oclc.org/iiif/2/plutei:{IIIF[folio]}/full/1800,/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def lnum(n):
    m = re.match(r"\d+", n or "")
    return int(m.group()) if m else None


def greek_lines():
    """[(n, html)] in edition order; <del> rendered as [..]."""
    body = ET.parse(GREEK_XML).getroot().find(f".//{TEI}body")
    out = []
    for l in body.iter(f"{TEI}l"):
        def walk(e):
            s = e.text or ""
            for c in e:
                inner = walk(c)
                tag = c.tag.replace(TEI, "")
                if tag == "del":
                    s += "[" + inner.strip() + "]"
                elif tag in ("note", "milestone"):
                    pass
                else:
                    s += inner
                s += c.tail or ""
            return s
        txt = re.sub(r"\s+", " ", walk(l)).strip()
        out.append((l.get("n"), txt))
    return out


def english_blocks():
    """[(n, text)] Evelyn-White blocks in document order, notes removed. A block is split where a
    Perseus card milestone (a paragraph start) falls inside it, so the card's line starts a block;
    a card milestone standing just before a block (within 4 lines) relabels that block."""
    body = ET.parse(ENGLISH_XML).getroot().find(f".//{TEI}body")
    out = []
    pending = [None]

    def do_l(l):
        start = l.get("n")
        if pending[0] and start.isdigit() and pending[0].isdigit() and 0 < int(pending[0]) - int(start) <= 4:
            start = pending[0]
        pending[0] = None
        parts = [[start, ""]]

        def walk(e):
            parts[-1][1] += e.text or ""
            for c in e:
                tag = c.tag.replace(TEI, "")
                if tag == "milestone" and c.get("unit") == "card":
                    if parts[-1][1].strip():
                        parts.append([c.get("n"), ""])
                elif tag != "note":
                    walk(c)
                tail = c.tail or ""
                # a footnote anchored between two words leaves no space in the Perseus XML
                # ("quick-glancing<note>..</note>Aphrodite"); the printed text has one
                if tag == "note" and tail[:1].strip() and parts[-1][1][-1:].strip() and tail[0] not in ",.;:!?)]’”—":
                    tail = " " + tail
                parts[-1][1] += tail
        walk(l)
        if len(parts) > 1 and not parts[-1][1].strip():
            pending[0] = parts[-1][0]          # card milestone at the very end of the block
        out.extend((n, re.sub(r"\s+", " ", t).strip()) for n, t in parts if t.strip())

    def visit(e):
        for c in e:
            tag = c.tag.replace(TEI, "")
            if tag == "l":
                do_l(c)
            elif tag == "milestone" and c.get("unit") == "card":
                pending[0] = c.get("n")
            else:
                visit(c)
    visit(body)
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(force=False):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    grc = greek_lines()
    grc = [(n, t) for n, t in grc if n not in EXCLUDE]
    gtext = {int(n): t for n, t in grc}
    assert min(gtext) == 1 and max(gtext) == TOTAL, len(gtext)
    eng = []
    for n, t in english_blocks():
        if n in EXCLUDE:
            continue
        if n == "769a":                     # "To begin with, the first, the fourth, and the seventh" = Greek 770
            n = "770"
        if eng and eng[-1][0] == n:
            eng[-1] = (n, eng[-1][1] + " " + t)
        else:
            eng.append((n, t))
    eng = [(n, t) for n, t in eng if re.fullmatch(r"\d+", n)]
    merged = []
    for n, t in eng:
        if merged and merged[-1][0] == n:
            merged[-1] = (n, merged[-1][1] + " " + t)
        else:
            merged.append((n, t))
    eng = merged
    starts = [int(n) for n, _ in eng]

    page_of = {}
    for p in PAGES:
        for k in range(p["first"], p["last"] + 1):
            assert k not in page_of, k
            page_of[k] = p["folio"]
    assert sorted(page_of) == sorted(range(1, TOTAL + 1)), set(range(1, TOTAL + 1)) ^ set(page_of)

    paths = {p["folio"]: get_scan(p["folio"], force) for p in PAGES}
    for f, pth in paths.items():
        print(f"  {f}: {pth.stat().st_size} bytes")

    # English: cut at Evelyn-White's sentence ends at every page break (ENGLISH_CUTS, qc4_hesiod_english)
    def entry_of(k):
        for i, (a, b, *_rest) in enumerate(ENTRIES):
            if a <= k <= b:
                return i
    pieces = cut_english([(int(n), t) for n, t in eng], PAGES, ENGLISH_CUTS, ENGLISH_SPLITS, TOTAL)
    for pc in pieces:
        pc["entry"] = entry_of(pc["start"])
        assert entry_of(pc["end"]) == pc["entry"], f"English piece {pc['start']}-{pc['end']} crosses an entry boundary"

    rows, pubs = [], []
    for ei, (a, b, slug, title, blurb) in enumerate(ENTRIES):
        tid = f"verified-{KEY}-{slug}"
        sections = []
        for p in PAGES:
            lo, hi = max(a, p["first"]), min(b, p["last"])
            if lo > hi:
                continue
            f = p["folio"]
            g = "<br>".join(f"<sup>{k}</sup>{esc(gtext[k])}" for k in range(lo, hi + 1) if k in gtext and NOT_ON_PAGE.get(k) != f)
            eb = [pc for pc in pieces if pc["entry"] == ei and pc["folio"] == f]
            e = "<p>" + " ".join(f"<sup>{pc['mark']}</sup>{esc(pc['text'])}" for pc in eb) + "</p>" if eb else ""
            if not eb:
                e = "<p><em>The English for these lines is given with the neighbouring section (Evelyn-White's sentence runs across the page break).</em></p>"
            ms_last = p.get("ms_last", p["last"])
            first_w = " ".join(gtext[p["first"]].split()[:4])
            last_w = " ".join(gtext[ms_last].split()[-4:])
            part = "" if (lo, hi) == (p["first"], p["last"]) else f" This section shows lines {lo}-{hi} of that page; the rest of the page belongs to the {'previous' if lo > p['first'] else 'next'} part of the poem."
            if (lo, hi) != (p["first"], p["last"]) and lo > p["first"] and hi < p["last"]:
                part = f" This section shows lines {lo}-{hi} of that page."
            eng_range = (" " + english_note(eb, PAGES, ENGLISH_CUTS, f)) if eb else ""
            note = (f"{MS}, fol. {f}: lines {p['first']}-{ms_last}, begins ‹{first_w}›, ends ‹{last_w}›. "
                    "Checked on the image: first and last verse rows read and matched to the Greek (re-read on the image 2026-11-12: first row ‹" + p["read_first"] + "›, last row ‹" + p["read_last"] + "›)"
                    + (f"; the page before ends at line {p['first'] - 1}" if p['first'] > 1 else "; this is the first page of the poem")
                    + (f" and the page after begins at line {ms_last + 1}." if ms_last < TOTAL else " and this is its last page.") + part
                    + (" " + p["note"] if p["note"] else "") + eng_range)
            sections.append({
                "section": f"fol. {f}",
                "original_ref": f"Shield of Heracles {lo}-{hi}; {MS}, fol. {f}",
                "original_text": g,
                "text": e,
                "scan_pages": [f"{KEY}/{scan_name(f)}"],
                "scan_note": note,
            })
        n_lines = b - a + 1
        folios = [s["section"].replace("fol. ", "") for s in sections]
        intro = (
            f"<p>The <em>Shield of Heracles</em> is a short epic handed down under Hesiod's name, probably composed in the 6th century BCE. "
            f"It tells of Heracles' fight with Cycnus, son of Ares, and describes the hero's shield at length. This part: <strong>{esc(title)}</strong> "
            f"(lines {a}-{b}, {n_lines} lines). {esc(blurb)}</p>"
            f"<p>The page photographs are from {esc(MS_LONG)}, in the Biblioteca Medicea Laurenziana's Teca Digitale. "
            "It follows the Works and Days and the Theogony in the same manuscript. "
            f"This part is on fol. {', '.join(folios)}. "
            "The scribe writes two verses to a row, one in each column, so a page is read across the columns, row by row; a few short notes stand in the margins. "
            "Each section below is one page; its note gives the page's first and last verse as read on the photograph.</p>"
            "<p>The Greek is Evelyn-White's Loeb text (1914) via Perseus, not a transcription of this manuscript, whose wording differs here and there. "
            "Verses the editor brackets as later additions are shown in square brackets. "
            "The English is Evelyn-White's prose translation (1914); it is cut at the end of his sentences, so where a sentence runs across a page break it is given whole to one page; each section's note gives the exact lines its English covers.</p>"
        )
        pub = {
            "id": tid, "slug": tid,
            "title": f"Hesiod, Shield of Heracles {a}-{b}: {title}",
            "language": "Ancient Greek / English",
            "source": f"{MS} (BML Teca Digitale IIIF) + Evelyn-White Greek (Loeb 1914, Perseus) + Evelyn-White English (1914, Perseus)",
            "description": f"The Shield of Heracles, lines {a}-{b} ({title}), on the pages of the late 13th-century Florence manuscript Laur. Plut. 32.16, with Greek and English.",
            "introduction": intro,
            "translator_notes": [
                "Greek: H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb Classical Library, 1914), via Perseus. Square brackets mark verses the editor regards as interpolated.",
                "English: H. G. Evelyn-White's translation in the same volume; his footnotes are omitted.",
                "The Loeb text has no line 298; the numbering is the editor's.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF): {RECORD} ; manifest {MANIFEST}",
                "scan_license": "CC BY-NC-SA, as stated in the Teca Digitale record; images © Biblioteca Medicea Laurenziana, Florence",
                "scan_manuscript": MS_LONG,
                "scan_mapping": "Each page's first and last verse read on the page image and matched to the Greek, with continuity checked between consecutive pages (details in each section's scan_note).",
                "scan_mapping_urls": [RECORD, MANIFEST],
                "scan_local_paths": [s["scan_pages"][0] for s in sections],
                "original_text_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus canonical-greekLit tlg0020.tlg003.perseus-grc2 ({GITHUB}tlg0020.tlg003.perseus-grc2.xml)",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus tlg0020.tlg003.perseus-eng2 ({GITHUB}tlg0020.tlg003.perseus-eng2.xml)",
                "translation_license": "public domain (published 1914); Perseus digital text CC BY-SA 4.0",
                "translator": "H. G. Evelyn-White (1914)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False), encoding="utf-8")
        pubs.append(pub)
        rows.append({
            "id": tid, "slug": tid, "order": ei + 1,
            "title": pub["title"], "author_id": "hesiod", "language": "Ancient Greek",
            "era": "Classical", "tradition": "greek", "category": "literature",
            "date_approx": "c. 6th c. BCE (composition); manuscript late 13th c.", "century": -6,
            "source": pub["source"], "description": pub["description"],
            "themes": ["hesiod", "shield-of-heracles", "heracles", "greek-myth", "epic", "greek", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": s["scan_pages"][0], "caption": f"{MS}, {s['section']}"} for s in sections]},
        })
        print(f"wrote {tid}: {len(sections)} sections")

    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-",
            "label": "Hesiod, Shield of Heracles",
            "group": "Greece", "date_sort": -700,
            "author_name": "Attributed to Hesiod (c. 6th c. BCE; Florence manuscript, late 13th c.)",
            "source_url": RECORD,
            "critical_edition": "Evelyn-White, Loeb 1914, via Perseus",
            "translator_name": "H. G. Evelyn-White (1914)",
            "original_lang_label": "Ancient Greek · Evelyn-White",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "hesiod shield of heracles scutum cycnus ares alcmene iolaus",
            "description": "The Shield of Heracles, handed down under Hesiod's name, complete, on the pages of the late 13th-century Florence manuscript Laur. Plut. 32.16.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    build(ap.parse_args().force)
