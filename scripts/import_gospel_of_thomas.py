#!/usr/bin/env python3
"""
import_gospel_of_thomas.py: the Gospel of Thomas in Nag Hammadi Codex II
(Cairo, Coptic Museum, inv. 10544; tractate II,2, codex pages 32-51).

Collection key: gospel-of-thomas.  One entry per codex page (32-51); each entry
holds the sayings that BEGIN on that page, one section per saying (plus the
incipit on page 32 and the subscript title on page 51).  A saying that runs
onto the next page lists both page photographs.

Chain of evidence
-----------------
1. SCAN     Claremont Colleges Digital Library, Nag Hammadi Archive (collection
            "nha", CONTENTdm/IIIF at ccdl.claremont.edu).  For 19 pages the
            A-Series negatives (photographer Basile Psiroukis; one page per
            negative, published in The Facsimile Edition of the Nag Hammadi
            Codices: Codex II, Leiden: Brill, 1974).  For page 34, whose A-Series
            negative shows only loose fragments, the September 1975 P-Series
            negative no. 191 ("P II, 34+109"), cropped to the left page (34).
            Rights statement of the holder: "Physical rights are retained by the
            institution. Copyright is retained in accordance with U. S.
            Copyright laws."  Images are fetched through the public IIIF image
            API and reduced to 2400 px high.
2. MAPPING  Page and line breaks come from the Coptic SCRIPTORIUM edition
            (Paul C. Dilley), whose markup records every page break (pb) and
            line break (lb) of the codex; Dilley made the edition from these same
            Facsimile Edition photographs.  The first and last line of every
            page were then read on the downloaded photograph and compared with
            the edition (recorded per page in PAGE_CHECKS and in each scan_note).
            Page 32: the edition numbers the Thomas lines 1-18; on the page they
            are lines 10-27 (lines 1-9 hold the end of the Apocryphon of John and
            its title), so 9 is added to every page-32 line number.
3. COPTIC   Coptic SCRIPTORIUM, "Gospel of Thomas" (urn:cts:copticLit:nh.thomas.
            NHAM02:0-114), edition and annotation by Paul Dilley, Lydia
            Bremer-McCollum, Caroline T. Schroeder, Amir Zeldes, version 6.2.0
            (2025-11-25), CC BY 4.0.  The TreeTagger (.tt) export is parsed; the
            text is shown in the edition's original spelling (orig layer), word
            by word (bound groups), line by line with codex page.line numbers.
            Brackets, sublinear dots and other editorial signs are the edition's.
4. ENGLISH  Mark M. Mattison, The Gospel of Thomas (gospels.net), "committed to
            the public domain and may be freely copied and used, changed or
            unchanged, for any purpose".  Saying headings are Mattison's.

Usage:
    python3 scripts/import_gospel_of_thomas.py            # build
    python3 scripts/import_gospel_of_thomas.py --force    # re-download sources and scans
"""

import argparse
import html
import io
import json
import re
import urllib.request
from collections import OrderedDict
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "gospel-of-thomas"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"

CS_COMMIT = "e624efd798e3b49530472c7a4258db636222a826"  # CopticScriptorium/corpora, V6.2.0
TT_URL = f"https://raw.githubusercontent.com/CopticScriptorium/corpora/{CS_COMMIT}/thomas-gospel/thomas.gospel_TT/thomas_gospel.tt"
CS_PAGE = "https://data.copticscriptorium.org/texts/thomasgospel/gospel-of-thomas/norm"
CS_REPO = "https://github.com/CopticScriptorium/corpora/tree/master/thomas-gospel"
MATTISON_URL = "https://www.gospels.net/thomas"
CCDL = "https://ccdl.claremont.edu"
CCDL_COLL = "https://ccdl.claremont.edu/digital/collection/nha"
RIGHTS = ("Claremont Colleges Digital Library, Nag Hammadi Archive. Rights statement: 'Physical rights are retained "
          "by the institution. Copyright is retained in accordance with U. S. Copyright laws.' Reproduced for "
          "non-commercial scholarly reference with credit to the Institute for Antiquity and Christianity, Claremont.")

# codex page -> (CONTENTdm pointer, IIIF region, series note)
# Region "pct:x,y,w,h" trims the black negative border; page 34 is cut out of a two-page negative.
SCANS = {
    32: (2859, "A"), 33: (2943, "A"), 34: (2569, "P"), 35: (2893, "A"), 36: (2899, "A"),
    37: (2898, "A"), 38: (2881, "A"), 39: (2884, "A"), 40: (2877, "A"), 41: (2885, "A"),
    42: (2871, "A"), 43: (2914, "A"), 44: (2930, "A"), 45: (2822, "A"), 46: (2870, "A"),
    47: (2863, "A"), 48: (2895, "A"), 49: (2903, "A"), 50: (2853, "A"), 51: (2842, "A"),
}
REGION_A = "pct:6,2,88,96"
# Page of The Facsimile Edition of the Nag Hammadi Codices: Codex II (Leiden: Brill, 1974) on which each
# photograph was published, as stated in the CCDL record ("notes" field; saved in ccdl_item_metadata.json).
FACS_PAGE = {pg: pg + 10 for pg in range(32, 51)}
FACS_PAGE[51] = 63
REGION_P34 = "pct:17,12,34.5,77"

# Page-32 line numbers in the edition start at 1 for the first line of Thomas (codex line 10).
LINE_OFFSET = {32: 9}

# Short summaries of Mattison's own notes on his rendering (gospels.net, "Notes on Translation").
MATTISON_NOTES = {
    13: "Mattison notes that 'three things' could also be 'three words'; the Coptic word for 'word' also means 'saying', as in the incipit.",
    16: "Mattison renders monachos as 'one'; it is usually translated 'single', 'solitary' or 'alone'.",
    49: "Mattison renders monachos as 'one'; it is usually translated 'single', 'solitary' or 'alone'.",
    61: "Mattison's 'equal' follows a one-letter correction; the Coptic as written reads 'destroyed'.",
    65: "Mattison's 'creditor' fills a gap in the papyrus; 'a good person' has also been proposed (M. W. Grondin).",
    75: "Mattison renders monachos as 'one'; it is usually translated 'single', 'solitary' or 'alone'.",
    105: "Mattison notes that 'a bastard' is literally 'the son of a prostitute'.",
    114: "Mattison discusses the rendering 'manly' in his book The Gospel of Thomas: A New Translation for Spiritual Seekers (2015), pp. 25-26.",
}

# Notes from the visual check that concern single sayings.
EXTRA_NOTES = {
    13: "On the photograph the name Matthew is divided between the pages: ⲙⲁⲑ⳿ ends page 34 line 34 and ⲑⲁⲓⲟⲥ begins page 35; "
        "the edition puts the whole name on 35.1.",
}

# Visual check of every page (2026-11-12): the first and the last line of Thomas text on each
# photograph were read and compared with the edition's line of the same number.  Value =
# (first codex line, last codex line, what was seen).  main() asserts these against the edition.
PAGE_CHECKS = {
    32: (10, 27, "the end of the Apocryphon of John (lines 1-6) and its title (lines 7-9) stand above; Thomas begins on the line below the title and runs 18 lines to the foot of the text"),
    33: (1, 35, "full page; the last line ends at the break in the lower right"),
    34: (1, 34, "shown from the P-Series negative, since the A-Series negative of this page shows only loose fragments; the name Matthew is divided, ⲙⲁⲑ⳿ at the end of line 34 and ⲑⲁⲓⲟⲥ at the start of page 35, where the edition puts the whole name on 35.1"),
    35: (1, 36, "the last line runs into the break at the right"),
    36: (1, 35, "the last line stands just above the lower break"),
    37: (1, 35, "the last line runs into the lower break"),
    38: (1, 34, "the beginning of the last line is damaged"),
    39: (1, 34, "the last line breaks off at a hole in the papyrus"),
    40: (1, 34, "the left part of the last line is at the edge of the lower break"),
    41: (1, 35, "the last line breaks off at the lower right"),
    42: (1, 35, "the top line is damaged at the left; the last line begins after a break"),
    43: (1, 35, "the top line is damaged at the right; the last line breaks off at a hole"),
    44: (1, 35, "the top line is damaged at the left; the last line begins after a break"),
    45: (1, 35, "the lower lines break off at a hole on the right"),
    46: (1, 32, "the beginnings of the first and last lines are damaged; the page ends with ⲙⲛ̄ⲛⲉⲧⲙ̄ⲙⲉⲅⲓ, continued as ⲥⲧⲁⲛⲟⲥ on page 47"),
    47: (1, 34, "holes interrupt the top lines and the right side of the last lines"),
    48: (1, 35, "the left part of the top line and of the last lines is lost"),
    49: (1, 36, "the right side of the lower lines is lost"),
    50: (1, 35, "the left part of the top lines is lost; the last line begins after a break"),
    51: (1, 28, "the last saying ends on line 26; the title stands on lines 27-28 between ornamental bands, and the Gospel of Philip begins below"),
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def cached(name, url, force=False):
    p = SRC / name
    if force or not p.exists() or p.stat().st_size < 1000:
        p.write_bytes(fetch(url))
    return p


# ---------------------------------------------------------------------------
# Coptic SCRIPTORIUM TreeTagger export
# ---------------------------------------------------------------------------
TAG_RE = re.compile(r'^<([a-z_]+)(?: ([a-zA-Z_:]+)="(.*)")?')


def parse_tt(path):
    """Return a list of text pieces in document order, each a dict with
    page, folio, line, saying, group (bound-group instance id), text."""
    cur = {}
    group_id = 0
    pieces = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("</"):
            name = line[2:-1]
            cur.pop(name, None)
            continue
        if line.startswith("<"):
            m = TAG_RE.match(line)
            if not m:
                continue
            name = m.group(1)
            if name == "meta":
                continue
            # first attribute only is needed for the layers used here
            attrs = dict(re.findall(r'([a-zA-Z_:]+)="([^"]*)"', line))
            if name == "orig_group":
                group_id += 1
                cur[name] = group_id
            else:
                cur[name] = attrs.get(name, attrs.get("xml:id", ""))
            continue
        pieces.append({
            "page": int(cur["pb_xml_id"].split(".")[-1]),
            "folio": cur.get("pb_n", ""),
            "line": int(cur["lb_n"]),
            "saying": int(cur["chapter_n"]) if cur["chapter_n"].isdigit() else cur["chapter_n"],
            "group": cur.get("orig_group", -1),
            "text": html.unescape(line),
        })
    return pieces


def codex_line(page, line):
    return line + LINE_OFFSET.get(page, 0)


def build_lines(pieces):
    """[(page, codex_line, text)] for a run of pieces; bound groups separated by spaces."""
    out = []
    last_key, last_group, buf = None, None, []
    for p in pieces:
        key = (p["page"], codex_line(p["page"], p["line"]))
        if key != last_key:
            if buf:
                out.append((last_key[0], last_key[1], "".join(buf).strip()))
            buf, last_group = [], None
            last_key = key
        if last_group is not None and p["group"] != last_group:
            buf.append(" ")
        buf.append(p["text"])
        last_group = p["group"]
    if buf:
        out.append((last_key[0], last_key[1], "".join(buf).strip()))
    return out


def lines_html(lines):
    return "<br>".join(f"<sup>{pg}.{ln}</sup>{html.escape(t, quote=False)}" for pg, ln, t in lines)


def span(lines):
    (p0, l0, _), (p1, l1, _) = lines[0], lines[-1]
    return f"{p0}.{l0}-{l1}" if p0 == p1 else f"{p0}.{l0}-{p1}.{l1}"


# ---------------------------------------------------------------------------
# Mattison translation
# ---------------------------------------------------------------------------
def parse_mattison(path):
    t = path.read_text(encoding="utf-8")
    start = t.index("Prologue")
    end = t.index("Notes on Translation")
    body = t[t.rfind("<p", 0, start):t.rfind("<p", 0, end)]
    notes_html = t[end:]
    paras = re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)
    clean = []
    for p in paras:
        s = html.unescape(re.sub(r"<br\s*/?>", "\n", p))
        s = re.sub(r"<[^>]+>", "", s).replace("\xa0", " ").strip()
        if s:
            clean.append(s)
    out = OrderedDict()
    titles = {}
    cur = None
    for s in clean:
        m = re.fullmatch(r"Saying (\d+): (.+)", s.replace("\n", " "))
        if s == "Prologue":
            cur = "prologue"; out[cur] = []; continue
        if m:
            cur = int(m.group(1)); titles[cur] = m.group(2).strip(); out[cur] = []; continue
        if s.replace("\n", " ") == "The Gospel According to Thomas":
            cur = "subscript"; out[cur] = ["The Gospel According to Thomas"]; continue
        out[cur].append(s)
    assert list(k for k in out if isinstance(k, int)) == list(range(1, 115)), "Mattison sayings incomplete"
    notes = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", notes_html, re.S):
        s = html.unescape(re.sub(r"<[^>]+>", "", p)).replace("\xa0", " ").strip()
        if s.startswith("Saying"):
            notes.append(s)
    return out, titles, notes


def english_html(paras):
    return "".join(f"<p>{html.escape(p, quote=False)}</p>" for p in paras)


# ---------------------------------------------------------------------------
# Scans
# ---------------------------------------------------------------------------
def scan_rel(page):
    return f"{KEY}/nhc2-p{page}.jpg"


def get_scan(page, force=False):
    path = SCAN_DIR / f"nhc2-p{page}.jpg"
    if path.exists() and not force:
        return path
    ptr, series = SCANS[page]
    region = REGION_P34 if page == 34 else REGION_A
    img = Image.open(io.BytesIO(fetch(f"{CCDL}/iiif/2/nha:{ptr}/{region}/,2400/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def viewer(page):
    return f"{CCDL}/digital/collection/nha/id/{SCANS[page][0]}"


def photo_desc(page):
    ptr, series = SCANS[page]
    if series == "P":
        return (f"Codex II page {page}, left half of P-Series negative no. 191 of September 1975 ('P II, 34+109'), "
                f"Facsimile Edition p. {FACS_PAGE[page]}, CCDL nha {ptr}")
    return (f"Codex II page {page}, A-Series negative by Basile Psiroukis, Facsimile Edition p. {FACS_PAGE[page]}, "
            f"CCDL nha {ptr}")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SRC.mkdir(parents=True, exist_ok=True)
    SCAN_DIR.mkdir(parents=True, exist_ok=True)

    tt = cached("thomas_gospel.tt", TT_URL, args.force)
    mt = cached("mattison_gospels_net_thomas.html", MATTISON_URL, args.force)
    pieces = parse_tt(tt)
    eng, titles, _ = parse_mattison(mt)

    # all lines of the text, for the page checks
    all_lines = build_lines(pieces)
    by_page = OrderedDict()
    for pg, ln, t in all_lines:
        by_page.setdefault(pg, []).append((ln, t))
    assert list(by_page) == list(range(32, 52)), list(by_page)
    for pg, lines in by_page.items():
        nums = [ln for ln, _ in lines]
        assert nums == list(range(nums[0], nums[0] + len(nums))), (pg, nums)
    for pg in by_page:
        first_ln, last_ln, _ = PAGE_CHECKS[pg]
        first, last = by_page[pg][0], by_page[pg][-1]
        assert (first_ln, last_ln) == (first[0], last[0]), (pg, PAGE_CHECKS[pg], first[0], last[0])

    # sections
    sayings = OrderedDict()
    for p in pieces:
        sayings.setdefault(p["saying"], []).append(p)
    assert list(sayings) == list(range(0, 115)) + ["subtitle"], list(sayings)

    sections_by_page = OrderedDict((pg, []) for pg in range(32, 52))
    for n, ps in sayings.items():
        lines = build_lines(ps)
        pages = sorted({l[0] for l in lines})
        if n == "subtitle":
            assert [l[2] for l in lines] == ["ⲡⲉⲩⲁⲅⲅⲉⲗⲓⲟⲛ", "ⲡⲕⲁⲧⲁ ⲑⲱⲙⲁⲥ"], lines
            sections_by_page[51].append({
                "section": "subscript",
                "original_ref": f"Subscript title; NHC II {span(lines)}",
                "original_text": lines_html(lines),
                "text": english_html(eng["subscript"]),
                "scan_pages": [scan_rel(51)],
                "scan_note": (f"On page 51 lines {lines[0][1]}-{lines[-1][1]} ({photo_desc(51)}): the title stands on two "
                              "centred lines below the last saying, between ornamental bands; checked on the photograph. "
                              "Line numbers from the Coptic SCRIPTORIUM edition."),
            })
            continue
        if n == 0:
            sid, ref = "prologue", f"Incipit (prologue); NHC II {span(lines)}"
            en = eng["prologue"]
        else:
            sid, ref = str(n), f"Saying {n} (Mattison: '{titles[n]}'); NHC II {span(lines)}"
            en = eng[n]
        lines_on = "; ".join(
            f"page {pg} lines {min(l[1] for l in lines if l[0] == pg)}-{max(l[1] for l in lines if l[0] == pg)}"
            for pg in pages)
        note = (f"On {lines_on} ({'; '.join(photo_desc(pg) for pg in pages)}). "
                f"Opens '{lines[0][2]}' at {lines[0][0]}.{lines[0][1]}; ends '{lines[-1][2]}' at {lines[-1][0]}.{lines[-1][1]}. "
                "Page and line breaks from the Coptic SCRIPTORIUM edition (pb/lb markup); the first and last line of each "
                "page were checked on the photograph.")
        if n in EXTRA_NOTES:
            note += " " + EXTRA_NOTES[n]
        sections_by_page[lines[0][0]].append({
            "section": sid,
            "original_ref": ref,
            "original_text": lines_html(lines),
            "text": english_html(en),
            "scan_pages": [scan_rel(pg) for pg in pages],
            "scan_note": note,
        })

    for pg in range(32, 52):
        p = get_scan(pg, args.force)
        print(f"  scan p{pg}: {p.stat().st_size} bytes")

    rows, written = [], []
    for order, (pg, secs) in enumerate(sections_by_page.items(), 1):
        nums = [int(s["section"]) for s in secs if s["section"].isdigit()]
        pages = sorted({int(re.search(r"p(\d+)", sp).group(1)) for s in secs for sp in s["scan_pages"]})
        page_label = f"page {pages[0]}" if len(pages) == 1 else f"pages {pages[0]}-{pages[-1]}"
        if pg == 32:
            what = f"prologue and sayings {nums[0]}-{nums[-1]}"
        elif len(nums) == 1:
            what = f"saying {nums[0]}"
        else:
            what = f"sayings {nums[0]}-{nums[-1]}"
        if pg == 51:
            what += " and subscript title"
        slug = f"{PREFIX}page-{pg}"
        title = f"Gospel of Thomas, {what} (Nag Hammadi Codex II, {page_label})"
        first_ln, last_ln, seen = PAGE_CHECKS[pg]
        first_txt, last_txt = by_page[pg][0][1], by_page[pg][-1][1]
        intro = (
            "<p>The Gospel of Thomas is a collection of 114 sayings attributed to Jesus, introduced as the hidden sayings "
            "written down by Didymos Judas Thomas. The only complete copy is the second tractate of Nag Hammadi Codex II, "
            "a papyrus book in Coptic copied in the 4th century and found near Nag Hammadi in Upper Egypt in 1945; it is "
            "now in the Coptic Museum, Cairo (inv. 10544). Greek fragments of the work survive in three Oxyrhynchus papyri "
            "(P. Oxy. 1, 654 and 655), which are not shown here.</p>"
            f"<p>This entry covers {'' if what.startswith('saying ') else 'the '}{what}, which {'begins' if what.startswith('saying ') else 'begin'} on codex page {pg}"
            + (f"; the end of saying {nums[-1]} is on page {pages[-1]}" if len(pages) > 1 else "")
            + ". The Coptic is given line by line; the small numbers are codex page and line (for example 33.5), so each line "
            "can be found on the photograph. Page and line breaks follow the Coptic SCRIPTORIUM edition by Paul Dilley, which "
            "he made from the photographs of The Facsimile Edition of the Nag Hammadi Codices, the negatives shown here.</p>"
            f"<p>Photograph: {photo_desc(pg)}; Nag Hammadi Archive of the Institute for Antiquity and Christianity, "
            "Claremont Colleges Digital Library. Checked on the photograph: page "
            f"{pg} line {first_ln} begins '{first_txt}' and line {last_ln} reads '{last_txt}' ({seen}).</p>"
        )
        tnotes = [
            "Coptic: Coptic SCRIPTORIUM edition (Paul C. Dilley), version 6.2.0, CC BY 4.0, shown in the manuscript's own "
            "spelling with words grouped as bound groups. Editorial signs are the edition's: square brackets mark letters lost "
            "in a gap (restored by the editor, or dots for the number of lost letters), a dot under a letter marks an uncertain "
            "reading, round brackets write out a letter abbreviated by a stroke at a line end, angle brackets mark letters "
            "added by the editor, curly brackets letters the editor removes, double square brackets letters erased by the scribe.",
            "The small numbers in the Coptic are codex page and line (page.line) as marked in the edition. Where a word is "
            "divided between two lines on the papyrus, the edition sometimes keeps the word whole on one line, so a line can "
            "begin a few letters earlier or later on the photograph (for example 39.33-34, and the page change inside saying 13).",
            "English: Mark M. Mattison, The Gospel of Thomas (public domain). Mattison's symbols: [ ] gap in the text, "
            "( ) editorial insertion, / \\ editorial correction of a scribal error. The saying headings are his.",
        ]
        for s in secs:
            if s["section"].isdigit() and int(s["section"]) in MATTISON_NOTES:
                tnotes.append(f"Saying {s['section']}: {MATTISON_NOTES[int(s['section'])]}")
        entry = {
            "id": slug, "slug": slug, "title": title,
            "language": "Coptic (Sahidic with Lycopolitan features) / English",
            "source": ("Nag Hammadi Codex II page photographs (Claremont Colleges Digital Library, Nag Hammadi Archive) + "
                       "Coptic SCRIPTORIUM edition by Paul Dilley (CC BY 4.0) + English by Mark M. Mattison (public domain)"),
            "description": (f"Gospel of Thomas, {what}, in the Coptic of Nag Hammadi Codex II, {page_label}, with each saying "
                            "linked to the photograph of the papyrus page and an English translation."),
            "introduction": intro,
            "translator_notes": tnotes,
            "translation": secs,
            "verification": {
                "scan_source": f"Claremont Colleges Digital Library, Nag Hammadi Archive ({CCDL_COLL}), IIIF image service; "
                               + "; ".join(f"page {p}: {viewer(p)}" for p in pages),
                "scan_license": RIGHTS,
                "scan_manuscript": "Nag Hammadi Codex II (Cairo, Coptic Museum, inv. 10544), papyrus codex, 4th century; "
                                   f"Gospel of Thomas = tractate II,2, pages 32.10-51.28; this entry: {page_label}",
                "scan_mapping": ("Codex page and line breaks from the Coptic SCRIPTORIUM edition (Dilley), which marks every page "
                                 "and line break of the codex; the first and last line of each page checked by eye on the "
                                 "photograph (recorded in the introduction and in the importer's page_checks.json). Page 32 "
                                 "edition line n = codex line n+9."),
                "scan_mapping_urls": [CS_PAGE, CS_REPO] + [viewer(p) for p in pages],
                "scan_local_paths": [scan_rel(p) for p in pages],
                "original_text_source": ("Coptic SCRIPTORIUM, Gospel of Thomas (urn:cts:copticLit:nh.thomas.NHAM02:0-114), "
                                         "edition and annotation by Paul Dilley, Lydia Bremer-McCollum, Caroline T. Schroeder, "
                                         f"Amir Zeldes, version 6.2.0 (2025-11-25); TreeTagger export {TT_URL}"),
                "original_text_license": "CC BY 4.0 (Coptic SCRIPTORIUM)",
                "translation_source": f"Mark M. Mattison, The Gospel of Thomas, {MATTISON_URL}",
                "translation_license": ("public domain: 'committed to the public domain and may be freely copied and used, "
                                        "changed or unchanged, for any purpose' (translator's statement)"),
                "translator": "Mark M. Mattison",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{slug}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(slug)
        rows.append({
            "id": slug, "slug": slug, "order": order, "title": title,
            "author_id": "gospel-of-thomas", "language": "Coptic",
            "era": "Apostolic", "tradition": "gnostic", "category": "sacred-text",
            "date_approx": "composed 1st/2nd c. AD (Greek); Coptic copy 4th c. (Nag Hammadi Codex II)",
            "century": 2,
            "source": entry["source"], "description": entry["description"],
            "themes": ["gospel-of-thomas", "nag-hammadi", "sayings-of-jesus", "coptic", "gnostic", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": scan_rel(p), "caption": f"Nag Hammadi Codex II, page {p}"} for p in pages]},
        })

    # remove stale published files of this collection
    for f in PUB.glob(f"{PREFIX}*.json"):
        if f.stem not in written:
            f.unlink()

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Gospel of Thomas (Nag Hammadi Codex II)",
            "group": "Early Christian",
            "date_sort": 140,
            "author_name": "Gospel of Thomas (Nag Hammadi Codex II, 4th c.)",
            "source_url": CCDL_COLL,
            "critical_edition": "Coptic SCRIPTORIUM edition by Paul Dilley (v6.2.0, CC BY 4.0)",
            "translator_name": "Mark M. Mattison (public domain)",
            "original_lang_label": "Coptic · Coptic SCRIPTORIUM (Dilley)",
            "original_lang_code": "cop",
            "edition_label": "",
            "search_terms": "gospel of thomas nag hammadi codex ii coptic sayings of jesus didymos judas thomas logia",
            "description": ("The Gospel of Thomas, 114 sayings attributed to Jesus, in the only complete copy: the Coptic text "
                            "of Nag Hammadi Codex II (4th century), pages 32-51, each saying linked to the photograph of its page."),
        },
        "texts": rows,
        "authors": [{
            "id": "gospel-of-thomas", "name": "Gospel of Thomas", "dates": "1st/2nd c. AD (composition)", "century": 2,
            "era": "Apostolic", "tradition": "gnostic", "language": "Coptic",
            "bio": "Anonymous early Christian collection of sayings of Jesus, attributed to Didymos Judas Thomas; complete only in Coptic in Nag Hammadi Codex II.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    nsec = sum(len(s) for s in sections_by_page.values())
    print(f"wrote {len(rows)} entries, {nsec} sections")


if __name__ == "__main__":
    main()
