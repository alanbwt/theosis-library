#!/usr/bin/env python3
"""
import_p52.py: P52 (Rylands Library Papyrus, Gr. P. 457), John 18:31-33 and
18:37-38, the oldest known fragment of a New Testament manuscript. One entry,
two sections (recto and verso of the one surviving fragment).

This file also holds the shared machinery used by the other early-papyrus
importers (import_p72.py, import_p75.py, import_p66.py, import_p46.py,
import_p45.py): NTVMR page parsing and diplomatic rendering, KJV lookup,
image download, and entry / collection writing.

Chain of evidence (P52)
  1. GREEK    NTVMR (INTF Muenster) page transcriptions of GA P52 (docID 10052),
              pageID 10 (folio 001r) and 20 (folio 001v):
                https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID=10052&pageID=<p>&format=txt
              Both files carry the header "Creative Commons Attribution 4.0".
              Cached in data/sources/p52/ntvmr/.
  2. SCAN     Manchester Digital Collections, IIIF manifest MS-GREEK-P-00457
              (canvas 1 = recto, canvas 2 = verso), images CC BY-NC 4.0
              (University of Manchester Library). Cached manifest in
              data/sources/p52/mdc/manifest.json.
  3. MAPPING  NTVMR page metadata (meta-10052.json) gives folio 001r = John
              18:31-33 and 001v = John 18:37-38, and links 001r to the Rylands
              image jrl020153tr and 001v to jrl020154tr. Manchester's record
              says recto = 18:31-33, verso = 18:37-38. Both sides were read on
              the downloaded images (see the scan_note of each section).
  4. ENGLISH  King James Version (1611; eBible.org eng-kjv USFM, public
              domain), cached in data/sources/ebible-eng-kjv/.

Rendering of the Greek (shared by all papyrus importers): line by line as the
transcription gives the lines (<br> at each line beginning); first hand only
(corrections in <app> are dropped); letters the transcribers restored
(<supplied>) in square brackets; doubtful letters (<unclear>) with a dot
below; <gap> as [...]; nomina sacra and numerals keep their overline as a
combining overline (U+0305); words broken over a line end stay broken as on
the papyrus; <note> elements are left out; book titles (incipit, inscriptio,
subscriptio, explicit) are shown in italics on their own lines.

Usage (from the repo root):
    python3 -I scripts/import_p52.py           # build
    python3 -I scripts/import_p52.py --force   # re-download scans
"""
import argparse
import io
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import qc_ntvmr_parse as NP  # noqa: E402  (parse_id, page_license: read-only reuse)

PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
COLL = ROOT / "data" / "collections"
SRCROOT = ROOT / "data" / "sources"
KJV_DIR = SRCROOT / "ebible-eng-kjv"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (static reference library)"
API = "https://ntvmr.uni-muenster.de/community/vmr/api"
TRANSCRIPT_URL = API + "/transcript/get/?docID={doc}&pageID={pid}&format=txt"
META_URL = API + "/metadata/manuscript/get/?docID={doc}&format=json"

BOOK_NAMES = {1: "Matthew", 2: "Mark", 3: "Luke", 4: "John", 5: "Acts", 6: "Romans", 7: "1 Corinthians",
              8: "2 Corinthians", 9: "Galatians", 10: "Ephesians", 11: "Philippians", 12: "Colossians",
              13: "1 Thessalonians", 14: "2 Thessalonians", 15: "1 Timothy", 16: "2 Timothy", 17: "Titus",
              18: "Philemon", 19: "Hebrews", 20: "James", 21: "1 Peter", 22: "2 Peter", 23: "1 John",
              24: "2 John", 25: "3 John", 26: "Jude", 27: "Revelation"}
BOOK_SLUG = {b: n.lower().replace(" ", "") for b, n in BOOK_NAMES.items()}
KJV_FILE = {1: "70-MAT", 2: "71-MRK", 3: "72-LUK", 4: "73-JHN", 5: "74-ACT", 6: "75-ROM", 7: "76-1CO",
            8: "77-2CO", 9: "78-GAL", 10: "79-EPH", 11: "80-PHP", 12: "81-COL", 13: "82-1TH", 14: "83-2TH",
            15: "84-1TI", 16: "85-2TI", 17: "86-TIT", 18: "87-PHM", 19: "88-HEB", 20: "89-JAS", 21: "90-1PE",
            22: "91-2PE", 23: "92-1JN", 24: "93-2JN", 25: "94-3JN", 26: "95-JUD", 27: "96-REV"}

TEI_NS = "{http://www.tei-c.org/ns/1.0}"
OVER = "\u0305"
DOT = "\u0323"
LB, VS, TON, TOFF = "\x01", "\x02", "\x03", "\x04"


# ---------------------------------------------------------------------------
# network
# ---------------------------------------------------------------------------
def fetch(url, timeout=180):
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # network hiccup: back off and retry
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def ntvmr_pages(key, doc):
    """NTVMR page index for docID (cached in data/sources/<key>/ntvmr/meta-<doc>.json)."""
    p = SRCROOT / key / "ntvmr" / f"meta-{doc}.json"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(META_URL.format(doc=doc)))
    pages = json.loads(p.read_text(encoding="utf-8"))["data"]["manuscript"]["pages"]["page"]
    return [pages] if isinstance(pages, dict) else pages


def ntvmr_page_file(key, doc, pid):
    f = SRCROOT / key / "ntvmr" / str(doc) / f"{pid}.xml"
    if not f.exists() or f.stat().st_size < 300:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(fetch(TRANSCRIPT_URL.format(doc=doc, pid=pid)))
        time.sleep(0.3)
    return f


def save_jpeg(data, path, region_px=None, long_side=None, quality=86):
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("RGB")
    if region_px:
        img = img.crop(region_px)
    if long_side and max(img.size) > long_side:
        s = long_side / max(img.size)
        img = img.resize((round(img.size[0] * s), round(img.size[1] * s)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=quality, optimize=True)
    return img.size


# ---------------------------------------------------------------------------
# TEI rendering (line by line)
# ---------------------------------------------------------------------------
def _local(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _pick_rdg(app):
    rdgs = [c for c in app if _local(c.tag) == "rdg"]
    for r in rdgs:
        if r.get("type") == "orig":
            return r
    for r in rdgs:
        if (r.get("hand") or "").startswith("firsthand"):
            return r
    return rdgs[0] if rdgs else None


def _dots(s):
    return "".join(ch + DOT if not ch.isspace() and ch not in (LB,) else ch for ch in s)


def _overline(s):
    out = []
    for ch in s:
        out.append(ch)
        if ch.isalpha():
            out.append(OVER)
    # a combining dot that followed a letter must stay attached to it: move
    # the overline after any dot (letter, DOT, OVER is fine either way)
    return "".join(out).replace(OVER + DOT, DOT + OVER)


def _render(el, out):
    """Append the rendered content of el (children and own text, not its tail)."""
    tag = _local(el.tag)
    if tag == "lb":
        out.append(LB)
        return
    if tag in ("pb", "cb", "note", "fw"):
        return
    if tag == "app":
        r = _pick_rdg(el)
        if r is not None:
            _render(r, out)
        return
    if tag == "gap":
        ext = el.get("extent") or ""
        if el.get("unit") == "char" and ext.isdigit() and 0 < int(ext) <= 12:
            out.append("[" + "." * int(ext) + "]")
        else:
            out.append(" [...] ")
        return
    if tag == "w":
        sub = []
        _children(el, sub, inside="w")
        word = "".join(sub)
        word = "".join(re.sub(r"\s+", "", piece) if piece not in (LB,) else piece
                       for piece in re.split(f"({LB})", word))
        out.append(" " + word + " ")
        return
    if tag == "hi" and el.get("rend") == "overline":
        sub = []
        _children(el, sub, inside="hi")
        out.append(_overline("".join(sub)))
        return
    if tag == "ex":
        sub = []
        _children(el, sub, inside="ex")
        out.append("(" + "".join(sub) + ")")
        return
    pre, post = ("[", "]") if tag == "supplied" else ("", "")
    out.append(pre)
    if tag == "unclear":
        sub = []
        _children(el, sub, inside="unclear")
        out.append(_dots("".join(sub)))
    else:
        _children(el, out, inside=tag)
    out.append(post)
    if tag == "pc":
        out.append(" ")


def _children(el, out, inside):
    if el.text:
        out.append(el.text)
    for c in el:
        _render(c, out)
        if c.tail:
            out.append(c.tail)


def parse_page(path, fix_key=None):
    """Parse one NTVMR page file. Returns dict with
       tokens: list of str (text with LB/VS/TON/TOFF markers),
       verses: [(b,k,v)] in order of first appearance,
       parts: {(b,k,v): set of part attrs},
       titles: [str] rendered title texts,
       license: str."""
    raw = path.read_text(encoding="utf-8")
    raw2 = re.sub(r"<!DOCTYPE[^\[>]*(\[.*?\])?\s*>", "", raw, count=1, flags=re.S).replace("&om;", "")
    root = ET.fromstring(raw2.encode("utf-8"))
    body = root.find(f".//{TEI_NS}body")
    toks, verses, parts, titles, absent = [], [], {}, [], []

    def walk(el, title=False):
        tag = _local(el.tag)
        if tag == "lb":
            toks.append(LB)
            return
        if tag in ("pb", "cb", "note", "fw"):
            return
        if tag == "div":
            t = el.get("type") or ""
            is_title = title or t in ("incipit", "inscriptio", "subscriptio", "explicit")
            if el.text and el.text.strip():
                toks.append(el.text)
            for c in el:
                walk(c, is_title)
                if c.tail and c.tail.strip():
                    toks.append(c.tail)
            return
        if tag == "ab":
            ident = NP.parse_id(el.get("n") or "", fix_key)
            cont = False
            if ident is None and re.match(r"^B\d+K\d+V\D", el.get("n") or "") and verses and not title:
                # malformed id in the source (e.g. P66 "B04K16V[νυν", "B04K18Vω̣σ̣"): the text
                # continues the preceding verse (checked against the Greek), so keep it there
                ident, cont = verses[-1], True
            if ident and ident[1] and ident[2] and not title:
                sub = []
                _children(el, sub, inside="ab")
                body_txt = "".join(x for x in sub if x != LB)
                if not any(ch.isalpha() for ch in body_txt) and not re.search(r"\[\.+\]", body_txt):
                    # an empty <ab>: a verse the scribe did not write (keep its line breaks)
                    if ident not in parts and ident not in absent:
                        absent.append(ident)
                    toks.extend(x for x in sub if x == LB)
                    return
                if ident not in parts:
                    verses.append(ident)
                    parts[ident] = set()
                parts[ident].add(el.get("part") or "")
                if not cont:
                    toks.append(f"{VS}{ident[0]}.{ident[1]}.{ident[2]}{VS}")
                toks.extend(sub)
            else:
                sub = []
                _children(el, sub, inside="ab")
                titles.append(re.sub(r"\s+", " ", "".join(x for x in sub if x != LB)).strip())
                toks.append(TON)
                toks.extend(sub)
                toks.append(TOFF)
            return
        if el.text and el.text.strip():
            toks.append(el.text)
        for c in el:
            walk(c, title)

    walk(body)
    absent = [a for a in absent if a not in parts]
    return {"tokens": toks, "verses": verses, "parts": parts, "titles": titles, "absent": absent,
            "license": NP.page_license(path)}


def verse_labels(verses):
    """Label for each verse in page order: 'c:v' for the first verse and at a
    chapter change, 'Book c:v' at a book change, else 'v'."""
    labels, prev = {}, None
    for (b, k, v) in verses:
        if prev is None:
            labels[(b, k, v)] = f"{k}:{v}"
        elif b != prev[0]:
            labels[(b, k, v)] = f"{BOOK_NAMES[b]} {k}:{v}"
        elif k != prev[1] or v != prev[2] + 1:
            labels[(b, k, v)] = f"{k}:{v}" if (k != prev[1] or v < prev[2]) else f"{v}"
        else:
            labels[(b, k, v)] = f"{v}"
        prev = (b, k, v)
    return labels


def render_lines(page, labels):
    """Return list of HTML lines for the page."""
    s = "".join(page["tokens"])
    # verse markers -> placeholders resolved after whitespace cleanup
    lines = s.split(LB)
    out = []
    depth = 0
    in_title = False
    for line in lines:
        seg = line
        # resolve verse starts
        def vrep(m):
            b, k, v = (int(x) for x in m.group(1).split("."))
            return f" <sup>{labels[(b, k, v)]}</sup>"
        seg = re.sub(f"{VS}([0-9.]+){VS}", vrep, seg)
        # titles in italics
        pieces = re.split(f"([{TON}{TOFF}])", seg)
        html = ""
        if in_title:
            html += "<em>"
        for p in pieces:
            if p == TON:
                if not in_title:
                    html += "<em>"
                in_title = True
            elif p == TOFF:
                if in_title:
                    html += "</em>"
                in_title = False
            else:
                html += p
        if in_title:
            html += "</em>"
        html = re.sub("[\u200b\u200c\u200d\ufeff]", "", html)
        html = re.sub(r"\s+", " ", html).strip()
        html = re.sub(r"<em>\s*</em>", "", html).strip()
        html = re.sub(r"<em>\s+", "<em>", html)
        html = re.sub(r"\s+</em>", "</em>", html)
        if depth > 0:
            html = "[" + html
        # balance square brackets per line ([...] gaps are balanced already)
        d = 0
        for ch in html:
            if ch == "[":
                d += 1
            elif ch == "]":
                d = max(0, d - 1)
        depth = d
        if depth > 0:
            html = html + "]" * depth
        html = html.replace("][", "")
        html = re.sub(r"\]\s+\[(?!\.)", " ", html)  # [a] [b] -> [a b], but keep [...] separate
        html = re.sub(r"\[\]", "", html)
        html = re.sub(r"\s+", " ", html).strip()
        html = re.sub(r"(?<=[^\s\]>]) ([·:.,;](?= |$|<))", r"\1", html)  # punctuation joins its word
        if html and re.sub(r"<[^>]+>", "", html).strip():
            out.append(html)
        elif html:
            out.append(html)
    # drop empty leading/trailing lines
    while out and not re.sub(r"<[^>]+>|\s", "", out[0]):
        out.pop(0)
    while out and not re.sub(r"<[^>]+>|\s", "", out[-1]):
        out.pop()
    return out


def visible_letters(html):
    """Letters actually read on the papyrus (outside brackets), for checks."""
    t = re.sub(r"<sup>.*?</sup>", " ", html)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# KJV
# ---------------------------------------------------------------------------
_kjv = {}


def kjv_book(b):
    if b in _kjv:
        return _kjv[b]
    txt = (KJV_DIR / f"{KJV_FILE[b]}eng-kjv.usfm").read_text(encoding="utf-8")
    out, ch = {}, 0
    for line in txt.splitlines():
        m = re.match(r"\\c (\d+)", line)
        if m:
            ch = int(m.group(1))
            continue
        parts = re.split(r"\\v (\d+)\s*", line)
        for i in range(1, len(parts), 2):
            v = int(parts[i])
            t = parts[i + 1]
            t = re.sub(r"\\f\s.*?\\f\*", "", t)
            t = re.sub(r"\\x\s.*?\\x\*", "", t)
            t = re.sub(r'\|[a-zA-Z-]+="[^"]*"', "", t)
            t = re.sub(r"\\\+?[a-z]+\d*\*?", " ", t)
            t = re.sub(r"\s+", " ", t).strip()
            t = re.sub(r"\s+([,.;:?!’)])", r"\1", t)
            t = re.sub(r"([(‘])\s+", r"\1", t)
            if t:
                out.setdefault(ch, {})[v] = (out.get(ch, {}).get(v, "") + " " + t).strip()
    _kjv[b] = out
    return out


def kjv(b, k, v):
    return kjv_book(b).get(k, {}).get(v)


def kjv_html(verses, labels):
    out = []
    for (b, k, v) in verses:
        t = kjv(b, k, v)
        if t is None:
            raise SystemExit(f"KJV has no {BOOK_NAMES[b]} {k}:{v}")
        out.append(f"<sup>{labels[(b, k, v)]}</sup>{t}")
    return " ".join(out)


# ---------------------------------------------------------------------------
# references
# ---------------------------------------------------------------------------
def ref_range(verses, parts=None):
    """'John 18:31-33' / 'Luke 3:18-22; 3:33-4:2' style reference for an ordered verse list.
    parts (optional) marks a first verse that began on the previous page ('end')
    and a last verse that continues on the next page."""
    if not verses:
        return ""
    groups = [[verses[0]]]
    for x in verses[1:]:
        p = groups[-1][-1]
        cont = (x[0] == p[0] and ((x[1] == p[1] and x[2] == p[2] + 1) or (x[1] == p[1] + 1 and x[2] == 1)))
        if cont:
            groups[-1].append(x)
        else:
            groups.append([x])
    out, prevb = [], None
    for g in groups:
        a, z = g[0], g[-1]
        head = f"{BOOK_NAMES[a[0]]} " if a[0] != prevb else ""
        if a == z:
            out.append(f"{head}{a[1]}:{a[2]}")
        elif a[1] == z[1]:
            out.append(f"{head}{a[1]}:{a[2]}-{z[2]}")
        else:
            out.append(f"{head}{a[1]}:{a[2]}-{z[1]}:{z[2]}")
        prevb = z[0]
    return "; ".join(out)


def missing_between(verses):
    """KJV verses that fall inside the page's range but have no text on the page."""
    miss = []
    for i in range(len(verses) - 1):
        (b, k, v), (b2, k2, v2) = verses[i], verses[i + 1]
        if b != b2:
            continue
        if k == k2 and v2 > v + 1:
            miss += [(b, k, x) for x in range(v + 1, v2) if kjv(b, k, x)]
        elif k2 == k + 1:
            last = max(kjv_book(b).get(k, {}) or {0: 0})
            miss += [(b, k, x) for x in range(v + 1, last + 1)]
            miss += [(b, k2, x) for x in range(1, v2)]
    return miss


# ---------------------------------------------------------------------------
# entries and collection
# ---------------------------------------------------------------------------
GREEK_NOTE = ("Greek: the NTVMR diplomatic transcription, line by line as on the papyrus. Square brackets enclose "
              "letters that are lost or illegible and were supplied by the transcribers; a dot under a letter marks "
              "it as uncertain; [...] marks a gap. Nomina sacra and numerals keep the scribe's overline. Spelling is "
              "the scribe's (no accents or breathings). Words broken at a line end stay broken as on the papyrus. "
              "Corrections are not shown: the text is the first hand.")
ENGLISH_NOTE = ("English: the King James Version (1611), whole verses, for every verse that has text on the page. "
                "A verse that begins on one page and ends on the next is given in full on both. The KJV translates "
                "a later form of the Greek text, so its wording does not always match the papyrus; material "
                "differences (such as verses the papyrus does not have) are noted in the section.")


def write_entry(entry):
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / f"{entry['id']}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_collection(key, collection, rows, authors):
    d = {"collection": collection, "texts": rows, "authors": authors}
    (COLL / f"{key}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def remove_stale(prefix, keep_ids):
    for f in PUB.glob(f"{prefix}*.json"):
        if f.stem not in keep_ids:
            f.unlink()


def group_pages_by_chapter(pages):
    """Group consecutive pages into entries: a page belongs to the chapter in
    which its first verse lies (book, chapter). Returns list of lists."""
    groups, cur, curkey = [], [], None
    for pg in pages:
        b, k, _ = pg["verses"][0]
        key = (b, k)
        if curkey is None or key != curkey:
            if cur:
                groups.append(cur)
            cur, curkey = [pg], key
        else:
            cur.append(pg)
    if cur:
        groups.append(cur)
    return groups


def get_image(path, url, force=False, long_side=2400):
    """Download url (an IIIF image request) to path as JPEG; never upscales."""
    if path.exists() and not force:
        return path
    save_jpeg(fetch(url), path, long_side=long_side)
    return path


def load_checks(key):
    """Per-page visual checks recorded by hand: data/sources/<key>/visual_check.json
    {section_id: "Checked on the image: ..."}."""
    f = SRCROOT / key / "visual_check.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def build_page(key, doc, spec):
    """spec: {pid, sec, ...}. Parses the NTVMR page and renders it."""
    f = ntvmr_page_file(key, doc, spec["pid"])
    pg = parse_page(f, fix_key=(doc, spec["pid"]))
    if pg["license"] != "CC BY 4.0":
        raise SystemExit(f"{key} page {spec['pid']}: transcription licence is '{pg['license']}', not CC BY 4.0")
    if not pg["verses"]:
        raise SystemExit(f"{key} page {spec['pid']}: no verses")
    labels = verse_labels(pg["verses"])
    lines = render_lines(pg, labels)
    return {**spec, "verses": pg["verses"], "parts": pg["parts"], "titles": pg["titles"],
            "absent": pg["absent"], "labels": labels, "lines": lines}


def page_ref(pg):
    """Reference with partial verses marked: 'John 1:1-14' / '2 Peter 1:5 (end)-10 (beginning)'."""
    vs = pg["verses"]
    ref = ref_range(vs)
    marks = []
    if "F" in pg["parts"].get(vs[0], set()):
        marks.append(f"{vs[0][1]}:{vs[0][2]} begins on the previous page")
    if "I" in pg["parts"].get(vs[-1], set()):
        marks.append(f"{vs[-1][1]}:{vs[-1][2]} continues on the next page")
    return ref, marks


def make_section(key, pg, check, extra_note=""):
    ref, marks = page_ref(pg)
    note = pg["scan_note"].rstrip()
    if marks:
        note += " " + "; ".join(m[0].upper() + m[1:] for m in marks) + "."
    if pg.get("titles"):
        note += (" The page also carries a book title, shown in italics in the Greek ("
                 + " / ".join(pg["titles"]) + "); the KJV has no English for it.")
    if pg.get("absent"):
        note += (" Not written in this papyrus: " + ref_range(pg["absent"]) + ". The NTVMR transcription marks "
                 + ("this verse" if len(pg["absent"]) == 1 else "these verses")
                 + " as empty at this point of the text, so the English leaves "
                 + ("it" if len(pg["absent"]) == 1 else "them") + " out.")
    vs = pg["verses"]
    jumps = [(vs[i], vs[i + 1]) for i in range(len(vs) - 1)
             if vs[i + 1][0] == vs[i][0] and (vs[i + 1][1], vs[i + 1][2]) < (vs[i][1], vs[i][2])]
    for x, y in jumps:
        note += (f" On this page {BOOK_NAMES[y[0]]} {y[1]}:{y[2]} follows {x[1]}:{x[2]}: the papyrus has the verses in a "
                 "different order from the KJV; the English follows the papyrus.")
    lost = [v for v in missing_between(pg["verses"]) if v not in pg.get("absent", [])
            and not any(j[1][1:] <= v[1:] <= j[0][1:] for j in jumps)]
    if lost:
        note += (" " + ref_range(lost) + (" falls" if len(lost) == 1 else " fall")
                 + " in the damaged part of the page (lines lost or unreadable), so the English skips "
                 + ("it." if len(lost) == 1 else "them."))
    note += " " + check.strip()
    if extra_note:
        note += " " + extra_note.strip()
    return {
        "section": pg["sec"],
        "original_ref": f"{pg['ref_label']}: {ref}",
        "original_text": "<br>".join(pg["lines"]),
        "text": kjv_html(pg["verses"], pg["labels"]),
        "scan_pages": [f"{key}/{f}" for f in (pg.get("files") or [pg["file"]])],
        "scan_note": note,
    }


def entry_range_title(pages):
    vs = [v for pg in pages for v in pg["verses"]]
    a, z = vs[0], vs[-1]
    bk = BOOK_NAMES[a[0]]
    if a[0] != z[0]:
        return f"{bk} {a[1]}:{a[2]}-{BOOK_NAMES[z[0]]} {z[1]}:{z[2]}"
    if a[1] == z[1]:
        return f"{bk} {a[1]}:{a[2]}-{z[2]}"
    return f"{bk} {a[1]}:{a[2]}-{z[1]}:{z[2]}"


# ---------------------------------------------------------------------------
# P52
# ---------------------------------------------------------------------------
KEY = "p52"
DOC = 10052
PREFIX = "verified-p52-"
MANIFEST = "https://www.digitalcollections.manchester.ac.uk/iiif/MS-GREEK-P-00457"
VIEWER = "https://www.digitalcollections.manchester.ac.uk/view/MS-GREEK-P-00457/1"
IIIF = "https://image.digitalcollections.manchester.ac.uk/iiif/MS-GREEK-P-00457-000-000{n}.jp2"
# Crop: the fragment with a margin, cutting away most of the colour chart (IIIF pct region).
SIDES = [
    {"pid": 10, "sec": "recto", "canvas": 1, "folio": "001r", "file": "p52-recto.jpg",
     "region": "pct:18,8,78,86",
     "check": "Checked on the image: 7 lines, fibres running across (the recto). Line 1 οι ιουδαι at the left and "
              "ημ on the detached piece at the right (John 18:31); line 2 ουδενα ινα ο λ; line 3 πεν σημαιν; line 4 "
              "θνησκειν ι; line 5 ριον ο π; line 6 και ειπ; line 7 (bottom) αιω, from ιουδαιων at the end of 18:33."},
    {"pid": 20, "sec": "verso", "canvas": 2, "folio": "001v", "file": "p52-verso.jpg",
     "region": "pct:18,8,78,86",
     "check": "Checked on the image: 7 lines, fibres running down (the verso). Line 1 υτο γ at the left and μαι "
              "at the right (εις τουτο γεγεννημαι, John 18:37); line 2 σμον ινα μαρτυ; line 3 εκ της αληθε; line 4 "
              "λεγει αυτω (18:38); line 5 ι τουτο; line 6 τους ι; line 7 (bottom) εμι, from ουδεμιαν."},
]


def build_p52(force=False):
    scan_dir = SCANS / KEY
    pages = []
    for s in SIDES:
        path = scan_dir / s["file"]
        if force or not path.exists():
            url = f"{IIIF.format(n=s['canvas'])}/{s['region']}/,2200/0/default.jpg"
            save_jpeg(fetch(url), path)
        f = ntvmr_page_file(KEY, DOC, s["pid"])
        pg = parse_page(f)
        assert pg["license"] == "CC BY 4.0", (s, pg["license"])
        labels = verse_labels(pg["verses"])
        lines = render_lines(pg, labels)
        pages.append({**s, "verses": pg["verses"], "parts": pg["parts"], "labels": labels, "lines": lines})
        print(f"  P52 {s['sec']}: {ref_range(pg['verses'])}, {len(lines)} lines, image {path.stat().st_size} bytes")

    sections = []
    for pg in pages:
        ref = ref_range(pg["verses"])
        sections.append({
            "section": pg["sec"],
            "original_ref": f"P52 {pg['sec']} (NTVMR folio {pg['folio']}): {ref}",
            "original_text": "<br>".join(pg["lines"]),
            "text": kjv_html(pg["verses"], pg["labels"]),
            "scan_pages": [f"{KEY}/{pg['file']}"],
            "scan_note": (f"Manchester Digital Collections, Greek P 457, image {pg['canvas']} ({pg['sec']}), cropped to the "
                          f"fragment. NTVMR page {pg['pid']} (folio {pg['folio']}) indexes this side as {ref}. {pg['check']} "
                          "Almost all of each line is lost: the letters outside square brackets are the ones on the "
                          "fragment, and the bracketed text and the English cover the complete verses."),
        })

    tid = f"{PREFIX}john-18"
    title = "P52 (John Rylands fragment): John 18:31-33, 37-38"
    desc = ("The oldest known piece of a New Testament manuscript: a scrap of a papyrus codex of John, written in the "
            "2nd century, with John 18:31-33 on one side and 18:37-38 on the other.")
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Greek (NTVMR transcription) / English (KJV)",
        "source": "John Rylands Library, Manchester, Greek P 457 (P52): photographs from Manchester Digital Collections; "
                  "Greek from the INTF NTVMR transcription; English from the King James Version",
        "description": desc,
        "introduction": (
            "<p>P52 is a fragment of a papyrus leaf, 8.9 by 6.0 cm, from a codex of the Gospel of John. Bernard Grenfell "
            "bought it in Egypt in 1920 for the John Rylands Library, Manchester, and Colin H. Roberts identified it in "
            "1935. It is usually dated to the 2nd century (the library's catalogue gives mid to late 2nd century; NTVMR "
            "gives 125-175), which makes it the oldest known manuscript of any part of the New Testament. Its "
            "provenance is Upper Egypt, possibly Oxyrhynchus.</p>\n\n"
            "<p>One side (the recto, with the papyrus fibres running across) carries parts of John 18:31-33, where "
            "Jesus is brought before Pilate; the other side (the verso) carries parts of 18:37-38, Pilate's question "
            "\"What is truth?\". Seven lines survive on each side out of about eighteen. Because text runs on from "
            "one side to the other, the leaf was part of a book (a codex), not a roll.</p>\n\n"
            "<p>Each section below shows one side of the fragment. The Greek is the diplomatic transcription made by "
            "the Institute for New Testament Textual Research (INTF, Muenster) for its New Testament Virtual "
            "Manuscript Room. Only a few letters of each line are preserved; the transcribers' restorations of the "
            "lost letters are in square brackets.</p>"
        ),
        "translator_notes": [GREEK_NOTE, ENGLISH_NOTE,
                             "Restorations: the length of the lost parts of the lines fits the standard text of "
                             "John 18:31-33 and 37-38. Scholars have debated whether the repeated words εις τουτο in "
                             "18:37 fit the line length; the restoration shown is the NTVMR transcribers'."],
        "translation": sections,
        "verification": {
            "scan_source": f"University of Manchester Library, Manchester Digital Collections, Greek P 457 ({VIEWER}; IIIF manifest {MANIFEST})",
            "scan_license": "Images CC BY-NC 4.0 (University of Manchester Library), per the IIIF manifest: \"Images made available for download are licensed under a Creative Commons Attribution-NonCommercial 4.0 International License\"",
            "scan_manuscript": "Manchester, John Rylands Library, Greek P 457 (P. Ryl. Gr. 3.457; Gregory-Aland P52; Trismegistos 61624), papyrus codex fragment, 2nd century, Egypt",
            "scan_mapping": "NTVMR page index for GA P52 (folio 001r = John 18:31-33, 001v = John 18:37-38) and the Manchester catalogue record (recto 18:31-33, verso 18:37-38); every line on both sides read on the downloaded images",
            "scan_mapping_urls": [META_URL.format(doc=DOC), MANIFEST, VIEWER],
            "scan_local_paths": [f"{KEY}/{s['file']}" for s in SIDES],
            "original_text_source": "INTF, New Testament Virtual Manuscript Room, transcription of GA P52 (docID 10052, pages 10 and 20): " + TRANSCRIPT_URL.format(doc=DOC, pid=10),
            "original_text_license": "CC BY 4.0 (Institut fuer Neutestamentliche Textforschung, as stated in each page file)",
            "translation_source": "King James Version (1611), eBible.org eng-kjv USFM",
            "translation_license": "public domain",
            "translator": "King James Version (1611)",
            "verified_date": TODAY,
        },
    }
    write_entry(entry)
    remove_stale(PREFIX, {tid})

    row = {
        "id": tid, "slug": tid, "order": 1, "title": title, "author_id": "p52-scribe",
        "language": "Greek", "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
        "date_approx": "c. 125-175 AD (NTVMR); mid to late 2nd century (Rylands catalogue)", "century": 2,
        "source": entry["source"], "description": desc,
        "themes": ["new-testament", "papyrus", "gospel-of-john", "pilate", "p52", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{s['file']}", "caption": f"P52 {s['sec']}"} for s in SIDES]},
    }
    collection = {
        "key": KEY, "prefix": PREFIX, "label": "P52 (John Rylands fragment)", "group": "New Testament",
        "date_sort": 150,
        "author_name": "Papyrus P52, Egypt (c. 125-175 AD)",
        "source_url": VIEWER,
        "critical_edition": "INTF NTVMR diplomatic transcription (CC BY 4.0)",
        "translator_name": "King James Version (1611)",
        "original_lang_label": "Greek · NTVMR transcription",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "p52 rylands papyrus john 18 pilate oldest new testament fragment",
        "description": "The oldest known New Testament manuscript: a 2nd-century papyrus scrap of John 18 in the John Rylands Library, Manchester, both sides.",
    }
    authors = [{"id": "p52-scribe", "name": "Papyrus P52 (scribe)", "dates": "2nd century AD", "century": 2,
                "era": "Apostolic", "tradition": "christian", "language": "Greek",
                "bio": "Unknown scribe of a 2nd-century papyrus codex of the Gospel of John, of which one fragment (P52) survives in Manchester."}]
    write_collection(KEY, collection, [row], authors)
    print(f"wrote {tid} ({len(sections)} sections) and data/collections/{KEY}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    build_p52(a.force)


if __name__ == "__main__":
    main()
