#!/usr/bin/env python3
"""
import_hesiod-works-and-days.py: Hesiod, Works and Days, on Florence, Biblioteca Medicea
Laurenziana, Plut. 32.16 (late 13th century), fols. 233r-239v.

Chain of evidence
  1. SCAN     BML Teca Digitale (CONTENTdm IIIF), manifest
              https://cdm21059.contentdm.oclc.org/iiif/plutei:596036/manifest.json
              (record: "V. Hesiodi Opera et dies", rights CC BY-NC-SA).
              Older witnesses exist: Paris gr. 2771 (10th/11th c.; Gallica, which refused automated
              access during this work) and Laur. Plut. 31.39 (12th c.; online, but its opening
              leaves are too faded in the photographs to read every page's first and last verse).
              Plut. 32.16 was chosen because every page could be verified, and because it carries
              all three Hesiodic poems in one late 13th-century hand.
  2. MAPPING  Each page's first and last verse were read on the page image (zoomed crops
              of the top and bottom rows) and matched against the Greek; consecutive pages
              were checked for continuity. Verses run two to a row across the page (one in
              the left column, the next in the right), surrounded by marginal scholia.
              Results are in PAGES below; every section's scan_note repeats them.
  3. GREEK    H. G. Evelyn-White (Loeb, 1914), Perseus canonical-greekLit
              tlg0020.tlg002.perseus-grc2 (CC BY-SA 4.0). Lines the editor brackets as
              spurious (<del>) are shown in square brackets. Lines 169a-169d (from a papyrus,
              not in the medieval manuscripts) are left out.
  4. ENGLISH  H. G. Evelyn-White (1914, public domain), Perseus tlg0020.tlg002.perseus-eng2.
              The prose is divided into blocks of about five lines (Perseus <l n>); each
              block is placed in the section that holds the middle line of the block.

Usage:  python3 scripts/import_hesiod-works-and-days.py [--force]   (--force re-downloads scans)
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

KEY = "hesiod-works-and-days"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "hesiod"
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"

GREEK_XML = SRC / "tlg0020.tlg002.perseus-grc2.xml"
ENGLISH_XML = SRC / "tlg0020.tlg002.perseus-eng2.xml"
GITHUB = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0020/tlg002/"
MANIFEST = "https://cdm21059.contentdm.oclc.org/iiif/plutei:596036/manifest.json"
RECORD = "https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/596036"
TOTAL = 828
MS = "Laur. Plut. 32.16"
MS_LONG = ("Florence, Biblioteca Medicea Laurenziana, Plut. 32.16 (paper, late 13th century; a large "
           "collection of Greek poetry that also holds letters of Maximus Planudes), Works and Days on fols. 233r-239v")

# folio -> IIIF image service (from the manifest)
IIIF = {"233r": 595683, "233v": 595684, "234r": 595685, "234v": 595686, "235r": 595687, "235v": 595688,
        "236r": 595689, "236v": 595690, "237r": 595691, "237v": 595692, "238r": 595693, "238v": 595694,
        "239r": 595695, "239v": 595696}
EXCLUDE = {"169a", "169b", "169c", "169d"}
NOT_ON_PAGE = {120: "234r"}   # edition lines inside a page's range that the page does not carry

# Verified on the images (see docstring).  first/last = edition line numbers on the page.
PAGES = [
    {"folio": "233r", "first": 1, "last": 58,
     "note": "The poem begins under a faded red title with a large red initial M; scholia in the upper and lower margins and down the right side."},
    {"folio": "233v", "first": 59, "last": 117, "note": ""},
    {"folio": "234r", "first": 118, "last": 183,
     "note": "Line 120 (ἀφνειοὶ μήλοισι, φίλοι μακάρεσσι θεοῖσιν) is not on the page: the first row has 118-119 and the second begins with 121. The verse is known from an ancient quotation and is missing from most medieval manuscripts."},
    {"folio": "234v", "first": 184, "last": 239, "note": ""},
    {"folio": "235r", "first": 240, "last": 301, "note": ""},
    {"folio": "235v", "first": 302, "last": 361,
     "note": "The page ends with 360 and 361 in the traditional order; the Loeb text moves 363 before 361, so 363 is on the next page."},
    {"folio": "236r", "first": 362, "last": 414,
     "note": "The verse block ends about two thirds of the way down; the lower part of the page is filled with scholia."},
    {"folio": "236v", "first": 415, "last": 474, "note": ""},
    {"folio": "237r", "first": 475, "last": 536, "note": ""},
    {"folio": "237v", "first": 537, "last": 598, "note": ""},
    {"folio": "238r", "first": 599, "last": 660, "note": ""},
    {"folio": "238v", "first": 661, "last": 724, "note": ""},
    {"folio": "239r", "first": 725, "last": 775, "note": ""},
    {"folio": "239v", "first": 776, "last": 828,
     "note": "The poem ends with 828 about three quarters of the way down the page, followed by a faded red subscription."},
]
FIRST_LAST_WORDS = {}

# Episodes (boundaries fall on Evelyn-White's paragraph blocks)
ENTRIES = [
    (1, 41, "proem-two-strifes", "Proem: Zeus, and the two kinds of Strife",
     "Hesiod calls on the Muses to sing of Zeus, then tells his brother Perses that there are two Strifes: one breeds war, the other good competition."),
    (42, 108, "prometheus-pandora", "Prometheus and Pandora",
     "Why men must work: Prometheus steals fire, and Zeus sends Pandora, who opens the jar of evils and leaves only Hope inside."),
    (109, 201, "five-ages", "The Five Ages of mankind",
     "The golden, silver, bronze and heroic races, and the present race of iron, with its prophecy of decline."),
    (202, 319, "hawk-nightingale-justice", "The hawk and the nightingale; Justice",
     "The fable of the hawk and the nightingale, the blessings of the just city and the curse on the unjust, and the hard road to excellence."),
    (320, 404, "wealth-and-neighbours", "Wealth, neighbours and the household",
     "Wealth gained by violence does not last; advice on gods, neighbours, gifts, thrift and the household."),
    (405, 503, "ploughing", "The farmer's year: the house, the plough and sowing",
     "What a farmer needs, how to build a plough, and when to plough and sow at the cry of the crane."),
    (504, 608, "winter-spring-summer", "Winter, spring and summer; harvest and threshing",
     "The month of Lenaeon and the north wind, pruning and digging in spring, summer rest, and threshing."),
    (609, 705, "vintage-and-sailing", "Vintage and sailing",
     "The grape harvest, the season for sailing, Hesiod's one voyage from Aulis to Euboea, and advice on marriage."),
    (706, 764, "friends-and-customs", "Friends and rules of conduct",
     "Advice on friends and guests, and a list of religious and everyday rules."),
    (765, 828, "the-days", "The Days",
     "Which days of the month are lucky or unlucky for work, birth and marriage."),
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
                parts[-1][1] += c.tail or ""
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

    # English block -> (entry index, folio) by the block's middle line
    def entry_of(k):
        for i, (a, b, *_rest) in enumerate(ENTRIES):
            if a <= k <= b:
                return i
    blocks = []
    for i, (n, t) in enumerate(eng):
        a = int(n)
        b = max(a, starts[i + 1] - 1) if i + 1 < len(starts) else TOTAL
        mid = (a + b) // 2
        ei = entry_of(a)
        assert entry_of(b) == ei, f"English block {a}-{b} crosses an entry boundary"
        blocks.append((a, b, ei, page_of[mid], t))

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
            eb = [blk for blk in blocks if blk[2] == ei and blk[3] == f]
            e = "<p>" + " ".join(f"<sup>{x[0]}</sup>{esc(x[4])}" for x in eb) + "</p>" if eb else ""
            if not eb:
                e = "<p><em>The English for these lines is given with the neighbouring section (Evelyn-White's prose runs in blocks of about five lines).</em></p>"
            ms_last = p.get("ms_last", p["last"])
            first_w = " ".join(gtext[p["first"]].split()[:4])
            last_w = " ".join(gtext[ms_last].split()[-4:])
            part = "" if (lo, hi) == (p["first"], p["last"]) else f" This section shows lines {lo}-{hi} of that page; the rest of the page belongs to the {'previous' if lo > p['first'] else 'next'} part of the poem."
            if (lo, hi) != (p["first"], p["last"]) and lo > p["first"] and hi < p["last"]:
                part = f" This section shows lines {lo}-{hi} of that page."
            eng_range = f" English blocks here: {eb[0][0]}-{eb[-1][1]}." if eb else ""
            note = (f"{MS}, fol. {f}: lines {p['first']}-{ms_last}, begins ‹{first_w}›, ends ‹{last_w}›. "
                    "Checked on the image: first and last verse rows read and matched to the Greek"
                    + (f"; the page before ends at line {p['first'] - 1}" if p['first'] > 1 else "; this is the first page of the poem")
                    + (f" and the page after begins at line {ms_last + 1}." if ms_last < TOTAL else " and this is its last page.") + part
                    + (" " + p["note"] if p["note"] else "") + eng_range)
            sections.append({
                "section": f"fol. {f}",
                "original_ref": f"Works and Days {lo}-{hi}; {MS}, fol. {f}",
                "original_text": g,
                "text": e,
                "scan_pages": [f"{KEY}/{scan_name(f)}"],
                "scan_note": note,
            })
        n_lines = b - a + 1
        folios = [s["section"].replace("fol. ", "") for s in sections]
        intro = (
            f"<p>Hesiod's <em>Works and Days</em> (c. 700 BCE) is a poem of advice to his brother Perses on justice, work and the farmer's year. "
            f"It contains the myth of Prometheus and Pandora and the Five Ages of mankind, from the golden race to the race of iron. This part: <strong>{esc(title)}</strong> "
            f"(lines {a}-{b}, {n_lines} lines). {esc(blurb)}</p>"
            f"<p>The page photographs are from {esc(MS_LONG)}, in the Biblioteca Medicea Laurenziana's Teca Digitale. "
            "Older manuscripts of the poem exist (Paris gr. 2771, 10th/11th century; Florence, Laur. Plut. 31.39, 12th century), but this copy is legible on every page and holds Hesiod's three poems together. "
            f"This part is on fol. {', '.join(folios)}. "
            "The scribe writes two verses to a row, one in each column, so a page is read across the columns, row by row; the margins are filled with scholia (ancient and Byzantine notes). "
            "Each section below is one page; its note gives the page's first and last verse as read on the photograph.</p>"
            "<p>The Greek is Evelyn-White's Loeb text (1914) via Perseus, not a transcription of this manuscript, whose wording differs here and there. "
            "Verses the editor brackets as later additions are shown in square brackets. "
            "The English is Evelyn-White's prose translation (1914); it runs in blocks of about five lines, so at a page break a block can start a line or two before or after the page.</p>"
        )
        pub = {
            "id": tid, "slug": tid,
            "title": f"Hesiod, Works and Days {a}-{b}: {title}",
            "language": "Ancient Greek / English",
            "source": f"{MS} (BML Teca Digitale IIIF) + Evelyn-White Greek (Loeb 1914, Perseus) + Evelyn-White English (1914, Perseus)",
            "description": f"Hesiod's Works and Days, lines {a}-{b} ({title}), on the pages of the late 13th-century Florence manuscript Laur. Plut. 32.16, with Greek and English.",
            "introduction": intro,
            "translator_notes": [
                "Greek: H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb Classical Library, 1914), via Perseus. Square brackets mark verses the editor regards as interpolated.",
                "English: H. G. Evelyn-White's translation in the same volume; his footnotes are omitted.",
                "Lines 169a-169d of the Loeb text (fragments from a papyrus on Cronos and the fifth race) are not in the medieval manuscripts and are not included.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF): {RECORD} ; manifest {MANIFEST}",
                "scan_license": "CC BY-NC-SA, as stated in the Teca Digitale record; images © Biblioteca Medicea Laurenziana, Florence",
                "scan_manuscript": MS_LONG,
                "scan_mapping": "Each page's first and last verse read on the page image and matched to the Greek, with continuity checked between consecutive pages (details in each section's scan_note).",
                "scan_mapping_urls": [RECORD, MANIFEST],
                "scan_local_paths": [s["scan_pages"][0] for s in sections],
                "original_text_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus canonical-greekLit tlg0020.tlg001.perseus-grc2 ({GITHUB}tlg0020.tlg001.perseus-grc2.xml)",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus tlg0020.tlg001.perseus-eng2 ({GITHUB}tlg0020.tlg001.perseus-eng2.xml)",
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
            "date_approx": "c. 700 BCE (composition); manuscript late 13th c.", "century": -7,
            "source": pub["source"], "description": pub["description"],
            "themes": ["hesiod", "works-and-days", "five-ages", "golden-age", "greek-myth", "agriculture", "greek", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": s["scan_pages"][0], "caption": f"{MS}, {s['section']}"} for s in sections]},
        })
        print(f"wrote {tid}: {len(sections)} sections")

    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-",
            "label": "Hesiod, Works and Days",
            "group": "Greece", "date_sort": -700,
            "author_name": "Hesiod (c. 700 BCE; Florence manuscript, late 13th c.)",
            "source_url": RECORD,
            "critical_edition": "Evelyn-White, Loeb 1914, via Perseus",
            "translator_name": "H. G. Evelyn-White (1914)",
            "original_lang_label": "Ancient Greek · Evelyn-White",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "hesiod works and days five ages golden age iron race prometheus pandora perses farming justice",
            "description": "Hesiod's Works and Days, with the Five Ages of mankind and the myth of Pandora, complete, on the pages of the late 13th-century Florence manuscript Laur. Plut. 32.16.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    build(ap.parse_args().force)
