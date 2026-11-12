#!/usr/bin/env python3
"""
qc_ntvmr_parse.py: parse IGNTP-style TEI transcriptions into verse text with
page attribution. Two inputs share one walker:

  - NTVMR per-page files (data/sources/qc-legacy/ntvmr/<docID>/<pageID>.xml,
    fetched by qc_ntvmr_fetch.py): one <pb/> per file.
  - IGNTP whole-book files for John (data/sources/qc-legacy/ntvmr/igntp-john/
    04_<GA>.xml): many <pb/>, and a verse that crosses a page carries the
    <pb/> inside its <ab>.

Rendering policy (identical for every manuscript):
  - First hand only: inside <app>, the <rdg type="orig"> (hand firsthand or
    firsthandV) is printed; corrector readings are dropped. If an <app> has no
    "orig" reading, the first <rdg> is used. An omission (&om;) prints nothing.
  - Nomina sacra (<abbr type="nomSac">) and numerals (<abbr type="num">) are
    printed as the contracted letters the scribe wrote (e.g. ις, θυ), without
    the overline, as the Codex Sinaiticus entries already do.
  - <supplied> letters (not legible on the page, restored by the transcriber)
    are printed in square brackets: [αμ].
  - <unclear> letters carry a combining dot below (U+0323).
  - <gap> is printed as [...] (or one dot per lost letter when the extent is a
    small number of characters).
  - <note>, <fw> and verse-0 divisions (inscriptio, subscriptio, incipit,
    explicit) are skipped. Line and column breaks are dropped; a word broken
    over a line is joined. Spelling is kept exactly as transcribed; no accents
    or breathings are added.

Run from the repo root with python3 -I (it reads downloaded data).
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "sources" / "qc-legacy" / "ntvmr"
DOT = "̣"
PB = "\x00"  # page-break marker inside rendered text
JI, JF = "\ue000", "\ue001"  # a word split over a page/column: end of first piece, start of second


def join_parts(texts):
    """Join the per-page pieces of one verse; a word split over the break
    (marked <w part="I"> ... <w part="F">, or a <pb/> inside a <w>) is
    rejoined without a space."""
    s = " ".join(t for t in texts if t)
    s = s.replace(JI + " " + JF, "")
    return strip_joins(s)


def strip_joins(s):
    return s.replace(JI, "").replace(JF, "")
AB_RE = re.compile(r"^B(\d+)K(\d+)V(\d+)$")
OSIS_RE = re.compile(r"^([1-3]?[A-Za-z]*)\.(\d+)\.(\d+)$")
OSIS_BOOKS = {"Matt": 1, "Mark": 2, "Luke": 3, "John": 4, "Acts": 5, "Rom": 6, "1Cor": 7, "2Cor": 8,
              "Gal": 9, "Eph": 10, "Phil": 11, "Col": 12, "1Thess": 13, "2Thess": 14, "1Tim": 15,
              "2Tim": 16, "Titus": 17, "Phlm": 18, "Heb": 19, "Jas": 20, "1Pet": 21, "2Pet": 22,
              "1John": 23, "2John": 24, "3John": 25, "Jude": 26, "Rev": 27}
# Documented corrections of verse ids in the NTVMR files (checked against the
# NTVMR page index and the Greek words themselves):
#   20002 page 910 (fol. 110r): ids ".1.N" carry no book; the page index and
#     the text (πρεσβυτερος γαιω ...) are 3 John 1:N.
#   20002 page 1260 (fol. 144r): after the Hebrews subscriptio the ids read
#     "Heb.1.N" but the page index says 1 Tim 1:1-15 and the text is 1 Tim 1
#     (παυλος αποστολος ... κατ επιταγην).
ID_FIXES = {(20002, 910, ""): 25, (20002, 1260, "Heb.1"): 15}


def parse_id(n, fix_key=None):
    """Return (book, chapter, verse) or None for an <ab n> value."""
    m = AB_RE.match(n)
    if m:
        return tuple(int(x) for x in m.groups())
    m = OSIS_RE.match(n)
    if not m:
        return None
    name, k, v = m.group(1), int(m.group(2)), int(m.group(3))
    if fix_key is not None:
        doc, pid = fix_key
        for key in ((doc, pid, f"{name}.{k}"), (doc, pid, name)):
            if key in ID_FIXES:
                return (ID_FIXES[key], k, v)
    if name not in OSIS_BOOKS:
        return None
    return (OSIS_BOOKS[name], k, v)


def _local(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _pick_rdg(app):
    rdgs = [c for c in app if _local(c.tag) == "rdg"]
    for r in rdgs:
        if r.get("type") == "orig":
            return r
    return rdgs[0] if rdgs else None


def _dots(s):
    return "".join(ch + DOT if not ch.isspace() and ch != PB else ch for ch in s)


def render(el, out):
    """Append the rendered content of `el` (not its tail) to list `out`.
    Page and column breaks become markers: PB+'P'+label+PB and PB+'C'+n+PB."""
    tag = _local(el.tag)
    if tag == "pb":
        out.append(f"{PB}P{el.get('n', '')}{PB}")
        return
    if tag == "cb":
        out.append(f"{PB}C{el.get('n', '')}{PB}")
        return
    if tag in ("note", "fw", "lb"):
        return
    if tag == "app":
        r = _pick_rdg(el)
        if r is not None:
            render(r, out)
        return
    if tag == "gap":
        ext = el.get("extent") or ""
        if el.get("unit") == "char" and ext.isdigit() and 0 < int(ext) <= 12:
            out.append("[" + "." * int(ext) + "]")
        else:
            out.append("[...]")
        return
    if tag == "w":
        # a word never contains whitespace: render it apart and squeeze out
        # the line-end newlines that sit before <lb break="no"/>
        sub = [el.text or ""]
        for c in el:
            render(c, sub)
            if c.tail:
                sub.append(c.tail)
        pieces = "".join(sub).split(PB)
        for i in range(0, len(pieces), 2):
            pieces[i] = re.sub(r"\s+", "", pieces[i])
        # a break inside the word: mark both sides so the pieces can be rejoined
        for i in range(1, len(pieces), 2):
            if pieces[i - 1] and i + 1 < len(pieces) and pieces[i + 1]:
                pieces[i - 1] += JI
                pieces[i + 1] = JF + pieces[i + 1]
        word = PB.join(pieces)
        if el.get("part") == "I":
            word += JI
        elif el.get("part") == "F":
            word = JF + word
        out.append(" " + word + " ")
        return
    pre, post = ("[", "]") if tag == "supplied" else ("", "")
    out.append(pre)
    if el.text:
        out.append(_dots(el.text) if tag == "unclear" else el.text)
    for c in el:
        render(c, out)
        if c.tail and tag in ("supplied", "unclear", "hi", "abbr", "seg", "num"):
            out.append(_dots(c.tail) if tag == "unclear" else c.tail)
    out.append(post)
    if tag == "pc":
        out.append(" ")


def _clean(s):
    s = re.sub("[\u200b\u200c\u200d\ufeff]", "", s)
    s = s.replace("][", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _has_text(t):
    return bool(re.sub(r"\[\.+\]|\s", "", strip_joins(t)))


def render_ab_parts(ab, page, col):
    """Render an <ab>; return ([(page, col, text), ...], page_after, col_after)."""
    buf = []
    for c in ab:
        render(c, buf)
    pieces = "".join(buf).split(PB)
    parts = [[page, col, pieces[0]]]
    i = 1
    while i + 1 < len(pieces):
        mark = pieces[i]
        if mark.startswith("P"):
            page, col = mark[1:], ""
        elif mark.startswith("C"):
            col = mark[1:]
        if parts[-1][0] == page and parts[-1][1] == col:
            parts[-1][2] += pieces[i + 1]
        else:
            parts.append([page, col, pieces[i + 1]])
        i += 2
    parts = [(a, b, _clean(t)) for a, b, t in parts]
    # drop fragments with no letters (a break at the very start or end of a
    # verse, or a lone [...] next to a lost leaf), but keep one entry if the
    # whole verse is empty (a verse the scribe did not write)
    nonempty = [x for x in parts if _has_text(x[2])]
    return (nonempty or parts[:1]), page, col


def parse_file(path, default_page="", fix_key=None):
    """Return [(page, col, book, chapter, verse, part_attr, text), ...] in document order."""
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"<!DOCTYPE[^\[>]*(\[.*?\])?\s*>", "", raw, count=1, flags=re.S)
    raw = raw.replace("&om;", "")
    root = ET.fromstring(raw.encode("utf-8"))
    out = []
    state = {"page": default_page, "col": ""}

    def walk(el):
        tag = _local(el.tag)
        if tag == "pb":
            state["page"], state["col"] = el.get("n", ""), ""
            return
        if tag == "cb":
            state["col"] = el.get("n", "")
            return
        if tag == "teiHeader":
            return
        if tag == "ab":
            ident = parse_id(el.get("n") or "", fix_key)
            parts, state["page"], state["col"] = render_ab_parts(el, state["page"], state["col"])
            if ident:
                b, k, v = ident
                if v and k:
                    for pg, col, txt in parts:
                        out.append((pg, col, b, k, v, el.get("part") or "", txt))
            return
        for c in el:
            walk(c)

    walk(root)
    return out


def load_meta(doc):
    m = json.loads((CACHE / f"meta-{doc}.json").read_text(encoding="utf-8"))["data"]["manuscript"]
    return m["pages"]["page"]


def page_license(path):
    head = path.read_text(encoding="utf-8")[:6000]
    a = re.search(r"<availability>(.*?)</availability>", head, re.S)
    if not a:
        return ""
    s = re.sub(r"<[^>]+>|<!\[CDATA\[|\]\]>", " ", a.group(1))
    s = re.sub(r"\s+", " ", s).strip()
    if "Creative Commons Attribution 4.0" in s:
        return "CC BY 4.0"
    if "All rights reserved" in s:
        return "All rights reserved by the INTF"
    return s[:80]


def parse_ntvmr_doc(doc):
    """NTVMR per-page cache. Returns (pages, verses):
    pages:  ordered [{pid, folio, label, content, license, verses:[(b,k,v)]}]
    verses: {(b,k,v): [(pid, col, text), ...]} in page order (text '' = verse
            present in the index but empty, i.e. not written by the scribe)."""
    pages, verses = [], {}
    for p in load_meta(doc):
        pid = p["pageID"]
        f = CACHE / str(doc) / f"{pid}.xml"
        if not f.exists() or f.stat().st_size < 300:
            continue
        try:
            rows = parse_file(f, fix_key=(doc, pid))
        except ET.ParseError:
            continue
        if not rows:
            continue
        pages.append({"pid": pid, "folio": str(p.get("folio") or "").strip(), "label": rows[0][0],
                      "content": p.get("biblicalContent") or "", "license": page_license(f),
                      "verses": []})
        for _pg, col, b, k, v, _part, text in rows:
            pages[-1]["verses"].append((b, k, v))
            verses.setdefault((b, k, v), []).append((pid, col, text))
    return pages, verses


def parse_igntp_book(paths):
    """IGNTP whole-book files. Returns (pages, verses) like parse_ntvmr_doc,
    with pid = the folio label from <pb n>."""
    pages, verses, seen = [], {}, {}
    for path in paths:
        lic = page_license(path)
        for pg, col, b, k, v, _part, text in parse_file(path):
            if pg not in seen:
                seen[pg] = {"pid": pg, "folio": pg, "label": pg, "content": "", "license": lic,
                            "verses": [], "file": path.name}
                pages.append(seen[pg])
            seen[pg]["verses"].append((b, k, v))
            verses.setdefault((b, k, v), []).append((pg, col, text))
    return pages, verses


if __name__ == "__main__":
    import sys
    for doc in [int(a) for a in sys.argv[1:]] or [20003]:
        pages, verses = parse_ntvmr_doc(doc)
        print(doc, "pages with text:", len(pages), "verses:", len(verses))
