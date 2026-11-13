#!/usr/bin/env python3
"""
import_hyperborea.py — ancient testimonia on the Hyperboreans, one entry per passage, every
section linked to the manuscript page(s) that carry it.

This file also holds the shared builder and text helpers used by import_atlantis.py.

Chain of evidence (per passage, details in PASSAGES below and in docs/collections/hyperborea.md):
  SCAN     a medieval manuscript of the work, photographed by its library (IIIF). Each section's
           folio/line position was established by reading the page image: the opening and closing
           words of the passage (and of each section, where sections are linked separately) were
           read on the photograph and are quoted in the section's scan_note.
  ORIGINAL Greek/Latin from Perseus canonical-greekLit / canonical-latinLit (CC BY-SA 4.0; the
           underlying editions are public domain), edition named per passage.
  ENGLISH  public-domain translations only, source named per passage:
           Macaulay 1890 (Herodotus, Project Gutenberg), Myers 1874 (Pindar, PG),
           Oldfather 1935 (Diodorus, Loeb vol. II, via LacusCurtius; copyright not renewed: the
           1962-1963 renewal lists, data/sources/hyperborea/renewals/, contain no Diodorus or
           Pausanias entry), Jones 1935 (Pausanias, Loeb vol. IV, Perseus; same check),
           Hamilton & Falconer 1854-57 (Strabo, Perseus), Evelyn-White 1914 (Homeric Hymns, PG),
           Seaton 1912 (Apollonius, PG), Mair 1921 (Callimachus, via theoi.com),
           Bostock & Riley 1855 (Pliny, Perseus), Stanley 1665 (Aelian, penelope.uchicago.edu).

Usage:
    python3 scripts/import_hyperborea.py [--force]
"""
import argparse
import concurrent.futures as cf
import html as H
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "hyperborea"
SRC_ATL = ROOT / "data" / "sources" / "atlantis"
PUB_DIR = ROOT / "translations" / "published"
COLL_DIR = ROOT / "data" / "collections"
SCANS = ROOT / "site" / "assets" / "scans"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"
GREEK = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/{tg}/{w}/{tg}.{w}.{ed}.xml"
LATIN = "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/data/{tg}/{w}/{tg}.{w}.{ed}.xml"


# ------------------------------------------------------------------ fetching
def fetch(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def cached(name, url, folder=SRC):
    p = folder / name
    if not p.exists():
        folder.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url))
    return p


def perseus(urn_file):
    """'tlg0016.tlg001.perseus-grc2' -> local path (downloaded once)."""
    tg, w, ed = urn_file.split(".")
    tpl = LATIN if tg.startswith(("phi", "stoa")) else GREEK
    return cached(f"{urn_file}.xml", tpl.format(tg=tg, w=w, ed=ed))


# ------------------------------------------------------------------ text helpers
_roots = {}


def _root(path):
    if path not in _roots:
        _roots[path] = ET.parse(path).getroot()
    return _roots[path]


def _text(el, keep_lines=False):
    out = []

    def walk(e):
        tag = e.tag.split("}")[-1]
        if tag in ("note", "head", "bibl", "teiHeader", "figure"):
            if e.tail:
                out.append(e.tail)
            return
        if tag == "milestone" and e.get("unit") == "para":
            out.append("\n")
        if tag in ("p", "l", "quote") and out:
            out.append("\n")
        if e.text:
            out.append(e.text)
        for c in e:
            walk(c)
        if tag in ("quote", "lg"):
            out.append("\n")
        if e.tail:
            out.append(e.tail)

    walk(el)
    s = re.sub(r"[ \t\r]+", " ", "".join(out))
    s = re.sub(r" *\n[\s]*", "\n", s).strip()
    return s


def cts_div(path, *ns, levels=("book", "chapter", "section")):
    cur = _root(path).find(f".//{TEI}body")
    for lev, n in zip(levels, ns):
        found = None
        for d in cur.iter(f"{TEI}div"):
            if d is not cur and d.get("subtype") == lev and d.get("n") == str(n):
                found = d
                break
        if found is None:
            raise KeyError(f"{path.name}: no {lev} {n} in {ns}")
        cur = found
    return cur


def cts_text(path, *ns, levels=("book", "chapter", "section")):
    return _text(cts_div(path, *ns, levels=levels))


def cts_sections(path, book, chapter, levels=("book", "chapter")):
    """[(section n, text)] of a chapter."""
    ch = cts_div(path, book, chapter, levels=levels)
    out = []
    for d in ch.iter(f"{TEI}div"):
        if d is not ch and d.get("subtype") == "section":
            out.append((d.get("n"), _text(d)))
    return out


def verse_lines(path, *ns, levels=("poem",), first=None, last=None):
    """[(n, line)] from <l n=...> inside the addressed div (or the whole body)."""
    el = cts_div(path, *ns, levels=levels) if ns else _root(path).find(f".//{TEI}body")
    out, cur = [], None
    for l in el.iter(f"{TEI}l"):
        n = l.get("n")
        cur = int(re.match(r"\d+", n).group()) if n and re.match(r"\d+", n) else (cur + 1 if cur else None)
        if cur is None:
            continue
        if (first is None or cur >= first) and (last is None or cur <= last):
            out.append((cur, re.sub(r"\s+", " ", _text(l)).strip()))
    return out


def para_html(text):
    paras = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    return "\n".join(f"<p>{H.escape(p, quote=False)}</p>" for p in paras)


def lines_html(lines):
    return "<p>" + "<br>\n".join(f"<sup>{n}</sup>{H.escape(t, quote=False)}" for n, t in lines) + "</p>"


def numbered_html(pairs):
    """[(label, text)] -> one paragraph with <sup>label</sup> markers."""
    return "<p>" + " ".join(f"<sup>{H.escape(str(k))}</sup>{H.escape(t, quote=False)}" for k, t in pairs) + "</p>"


# --- Project Gutenberg texts
def gutenberg(n):
    return cached(f"pg{n}.txt", f"https://www.gutenberg.org/cache/epub/{n}/pg{n}.txt").read_text(encoding="utf-8")


def macaulay_book(book_roman):
    """Macaulay's Herodotus (PG 2707 = books I-IV), chapters of one book, footnote numbers removed."""
    lines = gutenberg(2707).split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith(f"BOOK {book_roman}."))
    notes = next(i for i, l in enumerate(lines) if i > start and l.startswith(f"NOTES TO BOOK {book_roman}"))
    body = "\n".join(lines[start + 1:notes]).replace("\r", "")
    tok = re.compile(r"(?<=[\s\w,;:.!?)\]'\"—])(\d{1,5})(?=[\s,;:.!?)'\"—]|$)")
    out, n, pos = [], 1, 0
    for m in tok.finditer(body):
        v = int(m.group(1))
        extra = n > 1 and v != n and v == (n - 1) * 100 + 1     # inserted notes such as "3701"
        if v != n and not extra:
            continue
        line_start = body.rfind("\n", 0, m.start(1)) + 1
        if body[line_start:m.start(1)].strip() == "" and body[m.end(1):m.end(1) + 1] == ".":
            continue                                             # chapter number at line start
        out.append(body[pos:m.start(1)].rstrip(" ") + (" " if body[m.end(1):m.end(1) + 1] == " " else ""))
        pos = m.end(1) + (1 if body[m.end(1):m.end(1) + 1] == " " else 0)
        n += 0 if extra else 1
    out.append(body[pos:])
    clean = "".join(out)
    chapters = {}
    for m in re.finditer(r"(?m)^(\d+)\. (.*?)(?=^\d+\. |\Z)", clean, re.S):
        chapters[int(m.group(1))] = re.sub(r"\s+", " ", m.group(2)).strip()
    return chapters


def gutenberg_block(n, start_marker, end_marker):
    """Text between two exact markers in a PG file (end exclusive), paragraphs kept, endnote numbers and [n] removed."""
    t = gutenberg(n).replace("\r", "")
    i = t.index(start_marker)
    j = t.index(end_marker, i)
    block = t[i:j]
    block = re.sub(r"\[\d+\]", "", block)
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
    return paras


# --- LacusCurtius (Oldfather's Diodorus)
def lacus_sections(path):
    s = Path(path).read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", s)
    s = re.sub(r'(?is)<A CLASS="ref".*?</A>', "", s)
    s = re.sub(r'(?is)<A ID="p\d+"><SPAN CLASS="pagenum">.*?</SPAN></A>', "", s)
    s = re.sub(r'(?is)<SPAN CLASS="pagenum">.*?</SPAN>', "", s)
    marks = []
    for m in re.finditer(r'(?is)<A CLASS="sec" NAME="([\d.]+)">\d+</A>|<A CLASS="chapter" NAME="(\d+)">\d+</A>', s):
        marks.append((m.group(1) or f"{m.group(2)}.1", m.start(), m.end(), bool(m.group(2))))
    out = {}
    for i, (name, a, b, is_ch) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(s)
        chunk = re.split(r'(?is)<HR|<DIV CLASS="endnotes"|<TABLE', s[b:end])[0]
        t = H.unescape(re.sub(r"<[^>]+>", " ", chunk)).replace("\u2060", "").replace("\u00a0", " ")
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            out[name] = t
    return out


def milestone_sections(path, book, first, last):
    """Latin texts numbered by section milestones (Pliny): {section: text} for first..last of a book."""
    b = cts_div(path, book, levels=("book",))
    toks = []

    def walk(e):
        tag = e.tag.split("}")[-1]
        if tag in ("note", "head", "bibl"):
            if e.tail:
                toks.append(("t", e.tail))
            return
        if tag == "milestone" and e.get("unit") == "section":
            toks.append(("ms", e.get("n")))
        if e.text and tag != "milestone":
            toks.append(("t", e.text))
        for c in e:
            walk(c)
        if e.tail:
            toks.append(("t", e.tail))

    walk(b)
    out, cur = {}, None
    for k, v in toks:
        if k == "ms":
            n = re.match(r"\d+", v or "")
            cur = int(n.group()) if n else cur
            if cur is not None and first <= cur <= last:
                out.setdefault(cur, [])
        elif cur is not None and first <= cur <= last:
            out[cur].append(v)
    return {k: re.sub(r"\s+", " ", "".join(v)).strip() for k, v in out.items()}


def bostock_chapter(book, chapter):
    """Bostock & Riley's Pliny (Perseus phi0978.phi001.perseus-eng1, TEI P4 with HTML entities): chapter text, notes removed."""
    s = perseus("phi0978.phi001.perseus-eng1").read_text(encoding="utf-8")
    b = re.search(r'<div1 type="book" n="%s">(.*?)(?=<div1 |</body>)' % book, s, re.S).group(1)
    c = re.search(r'<div2 type="chapter" n="%s">(.*?)(?=<div2 |\Z)' % chapter, b, re.S).group(1)
    c = re.sub(r"<note.*?</note>", "", c, flags=re.S)
    c = re.sub(r"<pb[^>]*/>", "", c)
    head = re.search(r"<head>(.*?)</head>", c, re.S)
    c = re.sub(r"<head>.*?</head>", "", c, flags=re.S)
    c = re.sub(r"</p>", "\n", c)
    c = H.unescape(re.sub(r"<[^>]+>", "", c))
    paras = [re.sub(r"\s+", " ", p).strip() for p in c.split("\n") if p.strip()]
    return (H.unescape(re.sub(r"<[^>]+>|\s+", " ", head.group(1))).strip() if head else ""), paras


def stanley_chapter(path, roman):
    """Thomas Stanley's Aelian (penelope.uchicago.edu): the text of CHAP. <roman> (heading kept separately)."""
    s = Path(path).read_text(encoding="utf-8")
    t = H.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", s)))
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r" ([,;:.!?)])", r"\1", t)
    m = re.search(r"CHAP\. %s\. (.*?) CHAP\. " % roman, t)
    return m.group(1).strip()


# ------------------------------------------------------------------ images
def get_image(coll, img, force=False):
    """img = {file, service, region ('full' or 'x,y,w,h' or 'pct:...'), width}"""
    from PIL import Image
    out = SCANS / coll / img["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 30_000 and not force:
        return out
    url = f"{img['service']}/{img.get('region', 'full')}/{img.get('width', 1600)},/0/default.jpg"
    im = Image.open(io.BytesIO(fetch(url))).convert("RGB")
    im.save(out, quality=85)
    return out


# ------------------------------------------------------------------ builder
def build(collection, passages, force=False):
    key = collection["key"]
    imgs = {}
    for p in passages:
        for k, v in p["images"].items():
            imgs[v["file"]] = v
    with cf.ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda v: get_image(key, v, force), imgs.values()))

    rows, n_sec = [], 0
    for order, p in enumerate(passages, 1):
        tid = f"verified-{key}-{p['slug']}"
        secs = []
        for s in p["sections"]:
            secs.append({
                "section": s["section"],
                "original_ref": s["ref"],
                "original_text": s["original"],
                "text": s["english"],
                "scan_pages": [f"{key}/{p['images'][k]['file']}" for k in s["images"]],
                "scan_note": s["note"],
            })
        n_sec += len(secs)
        used = []
        for s in p["sections"]:
            for k in s["images"]:
                if k not in used:
                    used.append(k)
        ms = p["ms"]
        entry = {
            "id": tid, "slug": tid, "title": p["title"],
            "language": p["language"],
            "source": p["source"],
            "description": p["description"],
            "introduction": "\n\n".join(p["intro"]),
            "translator_notes": p.get("notes", []),
            "translation": secs,
            "verification": {
                "scan_source": ms["scan_source"],
                "scan_license": ms["license"],
                "scan_manuscript": ms["manuscript"],
                "scan_mapping": ms["mapping"],
                "scan_mapping_urls": ms["urls"],
                "scan_local_paths": [f"{key}/{p['images'][k]['file']}" for k in used],
                "original_text_source": p["original_source"],
                "original_text_license": p["original_license"],
                "translation_source": p["translation_source"],
                "translation_license": p["translation_license"],
                "translator": p["translator"],
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order, "title": p["title"], "author_id": p["author_id"],
            "language": p["lang_name"], "era": p["era"], "tradition": p["tradition"], "category": p["category"],
            "date_approx": p["date_approx"], "century": p["century"], "source": p["source"],
            "description": p["description"], "themes": p["themes"] + ["verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{key}/{p['images'][k]['file']}", "caption": p["images"][k]["caption"]} for k in used]},
        })
    for f in PUB_DIR.glob(f"verified-{key}-*.json"):
        if f.stem not in {r["id"] for r in rows}:
            f.unlink()
    out = {"collection": collection, "texts": rows}
    if collection.get("_authors"):
        out["authors"] = collection.pop("_authors")
    (COLL_DIR / f"{key}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{key}: {len(rows)} entries, {n_sec} sections, {len(imgs)} images")


# ------------------------------------------------------------------ passages
# Manuscript images. Positions (folio, column, line) were read on these images; see each scan_note.
LEIDEN_SVC = "https://eu-img02.ext.exlibrisgroup.com/iiif/2/"
LEIDEN = {   # Leiden, UB, VLF 4 (Pliny "A"), Ex Libris IIIF service ids for the pages used
    "4v": "eyJyZWdpb24iOiJldS1jZW50cmFsLTEiLCJidWNrZXQiOiJldS1zdDAxLmV4dC5leGxpYnJpc2dyb3VwLmNvbSIsImtleSI6IjMxVUtCX0xFVS9zdG9yYWdlL2FsbWEvRjIvMUQvQTMvOTIvMUYvMzcvNzgvOEEvRTEvQzcvNzIvODkvQzIvRTAvM0YvM0QvMTg4N18xX2l0ZW1fNDIzNzczNF8wMjMuanAyIiwicmVwX2lkIjoiMTI1MjQwMjc4ODAwMDI3MTEiLCJpbnN0YW5jZSI6ImV1IiwiaW5zdGl0dXRpb24iOiIzMVVLQl9MRVUiLCJ3aWR0aCI6IjM1MTEiLCJoZWlnaHQiOiI1MjA2Iiwid21LZXkiOm51bGwsIndtV2lkdGgiOm51bGwsIndtSGVpZ2h0IjpudWxsLCJ3bVBvc2l0aW9uIjpudWxsLCJ3bVJlcGVhdCI6ZmFsc2UsIm5hOTEiOm51bGx9",
    "5r": "eyJyZWdpb24iOiJldS1jZW50cmFsLTEiLCJidWNrZXQiOiJldS1zdDAxLmV4dC5leGxpYnJpc2dyb3VwLmNvbSIsImtleSI6IjMxVUtCX0xFVS9zdG9yYWdlL2FsbWEvRjIvMUQvQTMvOTIvMUYvMzcvNzgvOEEvRTEvQzcvNzIvODkvQzIvRTAvM0YvM0QvMTg4N18xX2l0ZW1fNDIzNzczNF8wMjQuanAyIiwicmVwX2lkIjoiMTI1MjQwMjc4ODAwMDI3MTEiLCJpbnN0YW5jZSI6ImV1IiwiaW5zdGl0dXRpb24iOiIzMVVLQl9MRVUiLCJ3aWR0aCI6IjM2ODciLCJoZWlnaHQiOiI1MTc4Iiwid21LZXkiOm51bGwsIndtV2lkdGgiOm51bGwsIndtSGVpZ2h0IjpudWxsLCJ3bVBvc2l0aW9uIjpudWxsLCJ3bVJlcGVhdCI6ZmFsc2UsIm5hOTEiOm51bGx9",
    "27r": "eyJyZWdpb24iOiJldS1jZW50cmFsLTEiLCJidWNrZXQiOiJldS1zdDAxLmV4dC5leGxpYnJpc2dyb3VwLmNvbSIsImtleSI6IjMxVUtCX0xFVS9zdG9yYWdlL2FsbWEvRjIvMUQvQTMvOTIvMUYvMzcvNzgvOEEvRTEvQzcvNzIvODkvQzIvRTAvM0YvM0QvMTg4N18xX2l0ZW1fNDIzNzczNF8wNjguanAyIiwicmVwX2lkIjoiMTI1MjQwMjc4ODAwMDI3MTEiLCJpbnN0YW5jZSI6ImV1IiwiaW5zdGl0dXRpb24iOiIzMVVLQl9MRVUiLCJ3aWR0aCI6IjM2NzAiLCJoZWlnaHQiOiI1MTMyIiwid21LZXkiOm51bGwsIndtV2lkdGgiOm51bGwsIndtSGVpZ2h0IjpudWxsLCJ3bVBvc2l0aW9uIjpudWxsLCJ3bVJlcGVhdCI6ZmFsc2UsIm5hOTEiOm51bGx9",
    "27v": "eyJyZWdpb24iOiJldS1jZW50cmFsLTEiLCJidWNrZXQiOiJldS1zdDAxLmV4dC5leGxpYnJpc2dyb3VwLmNvbSIsImtleSI6IjMxVUtCX0xFVS9zdG9yYWdlL2FsbWEvRjIvMUQvQTMvOTIvMUYvMzcvNzgvOEEvRTEvQzcvNzIvODkvQzIvRTAvM0YvM0QvMTg4N18xX2l0ZW1fNDIzNzczNF8wNjkuanAyIiwicmVwX2lkIjoiMTI1MjQwMjc4ODAwMDI3MTEiLCJpbnN0YW5jZSI6ImV1IiwiaW5zdGl0dXRpb24iOiIzMVVLQl9MRVUiLCJ3aWR0aCI6IjM1MDIiLCJoZWlnaHQiOiI1MDUwIiwid21LZXkiOm51bGwsIndtV2lkdGgiOm51bGwsIndtSGVpZ2h0IjpudWxsLCJ3bVBvc2l0aW9uIjpudWxsLCJ3bVJlcGVhdCI6ZmFsc2UsIm5hOTEiOm51bGx9",
}
LEIDEN_HANDLE = "https://hdl.handle.net/1887.1/item:4237734"
LEIDEN_MANIFEST = "https://iiif-endpoint.universiteitleiden.nl/iiif_manifest/item:4237734/manifest"
VAT = "https://digi.vatlib.it/iiifimage/"
BAV_LICENSE = "© Biblioteca Apostolica Vaticana; reproduced for non-commercial scholarly use with credit"
BNF_LICENSE = "rightsstatements.org NoC-NC (no copyright, non-commercial use); credit: Source gallica.bnf.fr / BnF"
LEIDEN_LICENSE = "Public Domain Mark 1.0 (Leiden University Libraries, IIIF manifest rights statement)"
PERSEUS_LIC = "edition public domain; Perseus digital text CC BY-SA 4.0"


def leiden_img(folio, caption):
    return {"file": f"leiden-vlf4-f{folio}.jpg", "service": LEIDEN_SVC + LEIDEN[folio], "caption": caption}


def tcp_paragraph(path, start, end):
    """EEBO-TCP XML -> plain text between two exact phrases (end inclusive), line-end hyphens joined."""
    s = Path(path).read_text(encoding="utf-8")
    s = re.sub(r'<g ref="char:EOLhyphen"/>\s*', "", s)
    s = re.sub(r'<g ref="char:cmbAbbrStroke">(.)</g>', r"\1", s)
    s = re.sub(r'<g ref="char:punc">(.)</g>', r"\1", s)
    s = re.sub(r"<note.*?</note>", "", s, flags=re.S)
    t = H.unescape(re.sub(r"<[^>]+>", "", s))
    t = re.sub(r"\s+", " ", t)
    i = t.index(start)
    j = t.index(end, i) + len(end)
    return t[i:j]


def split_at(text, starts):
    """Split text at the given opening phrases (each must occur, in order)."""
    pos = [text.index(x) for x in starts]
    assert pos == sorted(pos), starts
    return [text[a:b].strip() for a, b in zip(pos, pos[1:] + [len(text)])]


# --- Frick's Teubner text of Mela 3.36-37 (Leipzig 1880, pp. 63-64), transcribed from the page images of the
#     archive.org scan (pomponiimelaede04melagoog, leaves n77-n78) and checked against them line by line.
MELA_FRICK = {
    "3.36": ("Inde Asiae confinia nisi ubi perpetuae hiemes sedent et intolerabilis rigor. Scythici populi incolunt, "
             "fere omnes et in unum Belcae adpellati. in Asiatico litore primi Hyperborei super aquilonem Riphaeosque "
             "montes sub ipso siderum cardine iacent; ubi sol non cotidie ut nobis sed primum verno aequinoctio exortus "
             "autumnali demum occidit; ideo sex mensibus dies et totidem aliis nox usque continua est."),
    "3.37": ("terra angusta aprica per se fertilis. cultores iustissimi et diutius quam ulli mortalium et beatius vivunt. "
             "quippe festo semper otio laeti non bella novere non iurgia, sacris operati maxime Apollinis, quorum primitias "
             "Delon misisse initio per virgines suas, deinde per populos subinde tradentes ulterioribus, moremque eum diu "
             "et donec vitio gentium temeratus est servasse referuntur. habitant lucos silvasque, et ubi eos vivendi "
             "satietas magis quam taedium cepit, hilares redimiti sertis semet ipsi in pelagus ex certa rupe praecipites "
             "dant. id eis funus eximium est."),
}


def pliny_4_88_91():
    lat = milestone_sections(perseus("phi0978.phi001.perseus-lat2"), "4", 88, 91)
    _, ch26 = bostock_chapter(4, 26)
    _, ch27 = bostock_chapter(4, 27)
    t26 = " ".join(ch26)
    t26 = t26[t26.index("Leaving Taphr"):]
    eng = split_at(t26, ["Leaving Taphr", "Behind these mountains", "Some writers have placed", "Nor are we at liberty"])
    first27 = " ".join(ch27)
    cut = first27.index("As for its seas, we have already made mention of them.") + len("As for its seas, we have already made mention of them.")
    eng[3] = eng[3] + " " + first27[:cut]
    notes = {
        88: ("fol. 27r col. a lines 21-36", ["27r"],
             "4.88 begins mid-line at fol. 27r col. a line 21 with ‹a tapris per continentem› (Mayhoff 'a Taphris'); line 22 reads "
             "‹introssus tenent auchetae apud quos›; the section ends with the last line of the column, ‹re gelidisque aquilonis conceptaculis›."),
        89: ("fol. 27r col. b lines 1-19", ["27r"],
             "4.89 opens fol. 27r col. b: line 1 ‹pone eos montes ultraque aquilo-›, line 2 ‹nem gens felix si credimus quos›, "
             "line 3 ‹hyperboreos appellavere annoso› (margin gloss 'hyperborei'); it ends at line 19 with ‹beatissimum›."),
        90: ("fol. 27r col. b lines 19-31", ["27r"],
             "4.90 begins mid-line at fol. 27r col. b line 19, ‹quidam eos in prima›, and ends at line 31 with ‹tradiderunt›."),
        91: ("fol. 27r col. b line 31 to fol. 27v col. a line 13", ["27r", "27v"],
             "4.91 begins mid-line at fol. 27r col. b line 31, ‹nec licet dubitare› (line 32 ‹de gente ex tot auctores produnt›, the scribe's "
             "'ex' for 'ea:'); col. b ends ‹pitiis gentium per annos aliquot› and fol. 27v col. a begins ‹venerabiles donec violata fide›; "
             "the section ends at fol. 27v col. a line 13 with ‹nuncupavimus›, followed on the same line by 4.92 ‹hellespontum insulas›."),
    }
    sections = []
    for i, n in enumerate((88, 89, 90, 91)):
        where, imgs, note = notes[n]
        sections.append({
            "section": f"4.{n}", "ref": f"Pliny, Natural History 4.{n}; Leiden, VLF 4, {where}",
            "original": f"<p>{H.escape(lat[n], quote=False)}</p>", "english": f"<p>{H.escape(eng[i], quote=False)}</p>",
            "images": imgs,
            "note": note + " Read on the Leiden University Libraries images (full pages 27r and 27v and column crops); Mayhoff's apparatus cites this manuscript (A) for the passage.",
        })
    return {
        "slug": "pliny-natural-history-4-88-91",
        "title": "Pliny the Elder, Natural History 4.88-91: the Rhipaean mountains and the Hyperboreans",
        "author_id": "pliny-elder", "era": "Imperial", "tradition": "roman", "category": "history",
        "lang_name": "Latin", "language": "Latin (Mayhoff) / English (Bostock and Riley 1855)",
        "date_approx": "77 AD (composition); 8th century (Leiden VLF 4)", "century": 1,
        "themes": ["hyperborea", "hyperboreans", "pliny", "natural-history", "latin", "delos", "apollo"],
        "description": ("Pliny the Elder on the Hyperboreans beyond the north wind (Natural History 4.88-91), on the 8th-century "
                        "Northumbrian manuscript Leiden VLF 4, fol. 27r-27v, with Mayhoff's Latin and Bostock and Riley's English."),
        "source": "Leiden, UB, VLF 4 (Pliny A, 8th c.) fol. 27r-27v + Mayhoff's Latin (Perseus) + Bostock and Riley's English (1855, Perseus)",
        "intro": [
            "<p>Pliny the Elder (23/24-79 AD) dedicated his <em>Natural History</em> to Titus in 77 AD. In book 4, after the peoples north of the "
            "Black Sea and the snowy Rhipaean mountains (4.88), he describes the Hyperboreans: a happy people beyond the north wind, 'if we "
            "believe it', where the hinges of the world turn and the sun rises once and sets once in the year; they live in woods and groves, "
            "know no discord or disease, and when sated with life leap from a rock into the sea (4.89). Some place them in Asia (4.90); their "
            "first-fruits, sent to Apollo at Delos, show that they existed (4.91).</p>",
            "<p>The manuscript is Leiden, Universiteitsbibliotheek, VLF 4 (Voss. Lat. F. 4), the oldest manuscript of these books of the "
            "<em>Natural History</em>, written in an insular (Northumbrian) hand in the first half of the 8th century; the Pliny leaves hold parts of "
            "books 2-6. Each page has two columns of 36-37 lines. 4.88-91 stand on fol. 27r and the top of 27v; the positions of each section, "
            "read on the images, are given in the notes.</p>",
            "<p>The Latin is Karl Mayhoff's Teubner text (via Perseus), not a transcription of the manuscript, whose spelling differs (e.g. "
            "'a tapris', 'ex tot'). The English is the translation of John Bostock and H. T. Riley (1855), divided here at Mayhoff's section breaks "
            "by its opening words; its last sentence (4.91) stands at the head of their chapter 27.</p>",
        ],
        "notes": ["Bostock and Riley's footnotes are omitted.",
                  "Pliny returns to the Hyperboreans at 6.34 and 6.55 (not included)."],
        "images": {"27r": leiden_img("27r", "Leiden VLF 4 fol. 27r"), "27v": leiden_img("27v", "Leiden VLF 4 fol. 27v")},
        "sections": sections,
        "ms": {
            "scan_source": f"Leiden University Libraries, VLF 4 ({LEIDEN_HANDLE}), IIIF manifest {LEIDEN_MANIFEST}; fol. 27r (canvas 68), 27v (canvas 69)",
            "license": LEIDEN_LICENSE,
            "manuscript": "Leiden, Universiteitsbibliotheek, VLF 4 (Voss. Lat. F. 4), Pliny siglum A, England (Northumbria), 8th c. first half (CLA X 1578)",
            "mapping": "Own visual check: section starts and ends read line by line on the full pages and column crops (see each scan_note)",
            "urls": [LEIDEN_HANDLE, LEIDEN_MANIFEST],
        },
        "original_source": "C. Mayhoff, C. Plini Secundi Naturalis Historiae libri XXXVII (Teubner, 1892-1909), Perseus canonical-latinLit phi0978.phi001.perseus-lat2",
        "original_license": PERSEUS_LIC,
        "translation_source": "John Bostock and H. T. Riley, The Natural History of Pliny (London, 1855), book 4 chapters 26-27, Perseus phi0978.phi001.perseus-eng1",
        "translation_license": "public domain (1855); Perseus digital text CC BY-SA 4.0",
        "translator": "John Bostock and H. T. Riley (1855)",
    }


def mela_3_36_37():
    eng = tcp_paragraph(SRC / "golding1585-A07401.xml", "FRom thence-foorth", "honourablest buriall that can be.")
    e36, e37 = split_at(eng, ["FRom thence-foorth", "The Land is narrowe"])
    base = "https://digi.vatlib.it/view/MSS_Vat.lat.4929/"
    sections = [
        {"section": "3.36", "ref": "Pomponius Mela, Chorographia 3.36; Vat. lat. 4929, fol. 179v col. b lines 9-21",
         "original": f"<p>{MELA_FRICK['3.36']}</p>", "english": f"<p>{H.escape(e36, quote=False)}</p>", "images": ["179v"],
         "note": ("3.36 begins mid-line at fol. 179v col. b line 9: ‹tas. Inde asiae confinia nisi ubi› (the end of 'virginitas' and the "
                  "start of 3.36); lines 13-14 read ‹belcae appellati. In asiatico li- / tore primi hyperborei super›; the section ends at line 21 "
                  "with ‹nox usque continua est›. Checked on the DigiVatLib image (full page and column crops). Viewer: " + base + "0364")},
        {"section": "3.37", "ref": "Pomponius Mela, Chorographia 3.37; Vat. lat. 4929, fol. 179v col. b lines 21-22 and fol. 180r col. a lines 1-17",
         "original": f"<p>{MELA_FRICK['3.37']}</p>", "english": f"<p>{H.escape(e37, quote=False)}</p>", "images": ["179v", "180r"],
         "note": ("3.37 begins mid-line at fol. 179v col. b line 21 (‹Terra›), line 22 ‹angusta aprica per se fertilis› ends the page; "
                  "fol. 180r col. a begins ‹cultores iustissimi et diutius quam› ('olim', corrected to 'ulli' above the line, on line 2) and "
                  "the section ends at line 17 with ‹funus eximium est›, followed on the same line by 3.38 ‹Mare caspium›. Checked on the "
                  "DigiVatLib images. Viewers: " + base + "0364 , " + base + "0365")},
    ]
    return {
        "slug": "pomponius-mela-3-36-37",
        "title": "Pomponius Mela, Chorographia 3.36-37: the Hyperboreans under the pole",
        "author_id": "pomponius-mela", "era": "Imperial", "tradition": "roman", "category": "history",
        "lang_name": "Latin", "language": "Latin (Frick 1880) / English (Arthur Golding 1585)",
        "date_approx": "c. 43-44 AD (composition); 9th century (Vat. lat. 4929)", "century": 1,
        "themes": ["hyperborea", "hyperboreans", "pomponius-mela", "geography", "latin", "delos", "apollo"],
        "description": ("Pomponius Mela's description of the Hyperboreans (Chorographia 3.36-37), on the 9th-century manuscript Vat. lat. 4929, "
                        "the only independent witness to his work, with Frick's Latin and Arthur Golding's English of 1585."),
        "source": "Vatican Library, Vat. lat. 4929 (9th c.) fol. 179v-180r via DigiVatLib + Frick's Latin (Teubner 1880) + Golding's English (1585, EEBO-TCP)",
        "intro": [
            "<p>Pomponius Mela, from Tingentera in southern Spain, wrote his <em>Chorographia</em>, the oldest surviving Latin geography, in the "
            "early 40s AD. Following the northern shore of Asia, he places the Hyperboreans first, beyond the north wind and the Rhipaean "
            "mountains under the very pole, where day and night each last six months (3.36). Their land is narrow, sunny and fertile; they are "
            "the most just of men and live longer and more happily than any, at peace, devoted to Apollo, to whom they sent first-fruits at "
            "Delos; when sated with life they crown themselves and leap from a rock into the sea (3.37).</p>",
            "<p>The manuscript is Vatican, Biblioteca Apostolica Vaticana, Vat. lat. 4929, written in the 9th century at Auxerre, the sole "
            "independent witness to Mela's text (siglum A). Each page has two columns of 22 lines. 3.36-37 run from fol. 179v col. b to fol. 180r "
            "col. a; the positions, read on the images, are given in the notes.</p>",
            "<p>The Latin is Carl Frick's Teubner edition (Leipzig, 1880), whose apparatus collates this manuscript; it was transcribed for this "
            "entry from the printed page images. The English is Arthur Golding's translation, <em>The worke of Pomponius Mela, the cosmographer</em> "
            "(London, 1585), in the Early English Books Online Text Creation Partnership edition, with its original spelling.</p>",
        ],
        "notes": ["Golding's English keeps the 1585 spelling as keyed by EEBO-TCP (e.g. 'vnder', 'buste' for 'busie'); the mark ▪ is TCP's sign for an unidentified punctuation mark in the print.",
                  "Frick's section numbers are used; the Latin Library text numbers these sections differently."],
        "images": {
            "179v": {"file": "vatlat4929-f179v.jpg", "service": VAT + "MSS_Vat.lat.4929/Vat.lat.4929_0364_fa_0179v.jp2", "caption": "Vat. lat. 4929 fol. 179v"},
            "180r": {"file": "vatlat4929-f180r.jpg", "service": VAT + "MSS_Vat.lat.4929/Vat.lat.4929_0365_fa_0180r.jp2", "caption": "Vat. lat. 4929 fol. 180r"},
        },
        "sections": sections,
        "ms": {
            "scan_source": "Biblioteca Apostolica Vaticana, DigiVatLib IIIF, Vat. lat. 4929 images 364-365 (https://digi.vatlib.it/iiif/MSS_Vat.lat.4929/manifest.json)",
            "license": BAV_LICENSE,
            "manuscript": "Vatican City, BAV, Vat. lat. 4929, 9th c., Auxerre; Mela siglum A (Frick)",
            "mapping": "Own visual check: section starts and ends read line by line on the full pages and column crops (see each scan_note)",
            "urls": [base + "0364", base + "0365", "https://digi.vatlib.it/iiif/MSS_Vat.lat.4929/manifest.json"],
        },
        "original_source": "C. Frick, Pomponii Melae De chorographia libri tres (Leipzig: Teubner, 1880), pp. 63-64, scan https://archive.org/details/pomponiimelaede04melagoog",
        "original_license": "public domain (1880)",
        "translation_source": "Arthur Golding, The vvorke of Pomponius Mela, the cosmographer (London, 1585; STC 17785), book 3 chapter 5, EEBO-TCP A07401 https://github.com/textcreationpartnership/A07401",
        "translation_license": "public domain (1585); EEBO-TCP Phase I transcription CC0 1.0",
        "translator": "Arthur Golding (1585)",
    }


def pliny_2_205():
    """For the atlantis collection: Pliny NH 2.205 (Plato's submerged land in the Atlantic)."""
    lat = milestone_sections(perseus("phi0978.phi001.perseus-lat2"), "2", 205, 205)[205]
    _, c91 = bostock_chapter(2, 91)
    _, c92 = bostock_chapter(2, 92)
    _, c93 = bostock_chapter(2, 93)
    t91 = " ".join(c91)
    eng = t91[t91.index("while Epidaurus and Oricum"):] + " " + " ".join(c92) + " " + " ".join(c93)
    return {
        "slug": "pliny-natural-history-2-205",
        "title": "Pliny the Elder, Natural History 2.205: lands taken by the sea, 'if we believe Plato' in the Atlantic",
        "author_id": "pliny-elder", "era": "Imperial", "tradition": "roman", "category": "history",
        "lang_name": "Latin", "language": "Latin (Mayhoff) / English (Bostock and Riley 1855)",
        "date_approx": "77 AD (composition); 8th century (Leiden VLF 4)", "century": 1,
        "themes": ["atlantis", "plato", "pliny", "natural-history", "latin"],
        "description": ("Pliny the Elder on lands swallowed by the sea, first of all, 'if we believe Plato', a vast space where the Atlantic now "
                        "is (Natural History 2.205), on the 8th-century manuscript Leiden VLF 4, fol. 4v-5r."),
        "source": "Leiden, UB, VLF 4 (Pliny A, 8th c.) fol. 4v-5r + Mayhoff's Latin (Perseus) + Bostock and Riley's English (1855, Perseus)",
        "intro": [
            "<p>In book 2 of the <em>Natural History</em> (77 AD) Pliny lists changes of land and sea. At 2.205 he writes that the sea has "
            "taken whole lands, 'first of all, if we believe Plato, over an immense space where the Atlantic sea now is', then nearer home "
            "Acarnania, Achaea and the shores of the Propontis and Pontus, and that the earth also swallows itself. It is the only reference "
            "to Plato's Atlantis in Pliny, who names neither the island nor the war.</p>",
            "<p>The manuscript is Leiden, Universiteitsbibliotheek, VLF 4, the 8th-century Northumbrian copy that is the oldest witness for "
            "this part of the work (Pliny siglum A). 2.205 runs from fol. 4v col. b line 28 to fol. 5r col. a line 9; the Atlantis sentence "
            "is fol. 4v col. b lines 30-32, opening with an enlarged I.</p>",
            "<p>The Latin is Mayhoff's Teubner text (Perseus). The English is Bostock and Riley (1855): the end of their chapter 91 and their "
            "chapters 92-93, which together render 2.205.</p>",
        ],
        "notes": ["Bostock and Riley's footnotes are omitted. Their chapter heading for the Atlantis sentence is 'Lands which have been totally changed into seas'."],
        "images": {"4v": leiden_img("4v", "Leiden VLF 4 fol. 4v"), "5r": leiden_img("5r", "Leiden VLF 4 fol. 5r")},
        "sections": [{
            "section": "2.205", "ref": "Pliny, Natural History 2.205; Leiden, VLF 4, fol. 4v col. b line 28 to fol. 5r col. a line 9",
            "original": f"<p>{H.escape(lat, quote=False)}</p>", "english": f"<p>{H.escape(eng, quote=False)}</p>", "images": ["4v", "5r"],
            "note": ("2.205 begins mid-line at fol. 4v col. b line 28, after ‹vicinam ei magnesia›, with ‹epidaurus et ori-› (line 29 "
                     "‹cum insulae esse desierunt›). The Atlantis sentence is lines 30-32, with an enlarged I: ‹In totum abstulit terras primum om- / "
                     "nium ubi athlanticum mare est si platoni / credimus immenso spatio mox inter-›. Col. b ends (line 37) ‹antirrhium hellespontum "
                     "bosphorus›; fol. 5r col. a begins ‹duos atque ut sinus et stagna praeteri-›, and the section ends at line 9 with "
                     "‹non infida grassarentur et litora›, followed by 2.206 ‹pyrram et antissam›. Read on the Leiden images (full pages and "
                     "column crops)."),
        }],
        "ms": {
            "scan_source": f"Leiden University Libraries, VLF 4 ({LEIDEN_HANDLE}), IIIF manifest {LEIDEN_MANIFEST}; fol. 4v (canvas 23), 5r (canvas 24)",
            "license": LEIDEN_LICENSE,
            "manuscript": "Leiden, Universiteitsbibliotheek, VLF 4 (Voss. Lat. F. 4), Pliny siglum A, England (Northumbria), 8th c. first half",
            "mapping": "Own visual check: start, Atlantis sentence, page break and end read line by line on the images (see scan_note)",
            "urls": [LEIDEN_HANDLE, LEIDEN_MANIFEST],
        },
        "original_source": "C. Mayhoff, Naturalis Historiae (Teubner), Perseus canonical-latinLit phi0978.phi001.perseus-lat2",
        "original_license": PERSEUS_LIC,
        "translation_source": "John Bostock and H. T. Riley, The Natural History of Pliny (London, 1855), book 2 chapters 91-93, Perseus phi0978.phi001.perseus-eng1",
        "translation_license": "public domain (1855); Perseus digital text CC BY-SA 4.0",
        "translator": "John Bostock and H. T. Riley (1855)",
    }


def passage(**kw):
    """Assemble a passage dict; sections = [(id, ref, original_html, english_html, [image keys], note)]."""
    kw["sections"] = [{"section": a, "ref": b, "original": c, "english": d, "images": e, "note": f}
                      for a, b, c, d, e, f in kw["sections"]]
    return kw


def greek_sections_html(path, book, chapter, levels=("book", "chapter")):
    """Greek chapter with its section numbers as <sup> markers."""
    secs = cts_sections(path, book, chapter, levels=levels)
    if not secs:
        return f"<p>{H.escape(_text(cts_div(path, book, chapter, levels=levels)), quote=False)}</p>"
    return numbered_html([(f"{chapter}.{n}" if n not in ("0",) else str(chapter), re.sub(r"\s*\n\s*", " ", t)) for n, t in secs])


def esc_p(text):
    return f"<p>{H.escape(text, quote=False)}</p>"


def svarlien_chunks(urn_file, ode):
    """Svarlien's line-grouped translation: [(first_line, last_line, text)]; Perseus' '«' for an apostrophe restored."""
    lines = verse_lines(perseus(urn_file), ode)
    out = []
    for i, (n, t) in enumerate(lines):
        last = lines[i + 1][0] - 1 if i + 1 < len(lines) else None
        out.append((n, last, t.replace("«", "’")))
    return out


def verse_sections(greek, chunks, pages, label, ref_prefix, total_last):
    """Group translation chunks into sections whose Greek lines sit on the same manuscript page(s).

    greek: [(n, line)]; chunks: [(first, last, english)]; pages: [(page key, first line, last line)].
    Returns (section id, line range, greek html, english html, [page keys])."""
    def pages_for(a, b):
        return [k for k, f, l in pages if not (b < f or a > l)]
    groups = []
    for a, b, text in chunks:
        b = b if b is not None else total_last
        pk = pages_for(a, b)
        if groups and groups[-1]["pages"] == pk:
            groups[-1]["last"] = b
            groups[-1]["eng"].append(text)
        else:
            groups.append({"first": a, "last": b, "pages": pk, "eng": [text]})
    out = []
    for g in groups:
        gl = [(n, t) for n, t in greek if g["first"] <= n <= g["last"]]
        rng = f"{g['first']}-{g['last']}" if g["first"] != g["last"] else str(g["first"])
        out.append((rng, rng, lines_html(gl), "<p>" + " ".join(H.escape(t, quote=False) for t in g["eng"]) + "</p>", g["pages"]))
    return out


def evelyn_white_hymn7():
    """Evelyn-White's Homeric Hymn 7 (PG 348): [(first line, last line, text)] from his '(ll. a-b)' paragraphs; PG endnote numbers removed."""
    t = gutenberg(348).replace("\r", "")
    i = t.index("VII. TO DIONYSUS\n\n(ll. 1-16)")
    j = t.index("VIII. TO ARES", i)
    block = t[i + len("VII. TO DIONYSUS"):j]
    out = []
    for m in re.finditer(r"\(ll\. (\d+)-(\d+)\) (.*?)(?=\n\s*\n\(ll\.|\Z)", block, re.S):
        txt = re.sub(r"\s+", " ", m.group(3)).strip()
        txt = re.sub(r" \d{4} ", " ", txt)          # PG endnote numbers such as 2530
        out.append((int(m.group(1)), int(m.group(2)), txt))
    return out


def seaton_paragraph(start, end):
    """Seaton's Argonautica (PG 830): the text from `start` to `end` (inclusive)."""
    t = re.sub(r"\s+", " ", gutenberg(830).replace("\r", ""))
    i = t.index(start)
    j = t.index(end, i) + len(end)
    return re.sub(r"\[\d+\]", "", t[i:j])


MAIR_FIXES = [  # theoi.com transcription -> Mair 1921 print (checked on the 1921 scan, archive.org callimachuslycop00calluoft)
    ("the northern shore", "the Northern shore"),
    ("couch upon the ground ,", "couch upon the ground,"),
    ("fro the fair-haired", "from the fair-haired"),
    ("returned no home again", "returned not home again"),
    ("sweet-sounded marriage", "sweet-sounding marriage"),
    ("never silent \u2013 far", "never silent\u2014far"),
]


def mair_delos_275_299():
    s = (SRC / "theoi-CallimachusHymns2.html").read_text(encoding="utf-8", errors="replace")
    i = s.index("[275]")
    j = s.index("[300]", i)
    t = s[i + len("[275]"):j]
    t = re.sub(r"<sup>.*?</sup>", "", t, flags=re.S)
    t = H.unescape(re.sub(r"<[^>]+>", "", t))
    t = re.sub(r"\s+", " ", t).strip()
    for a, b in MAIR_FIXES:
        assert a in t, a
        t = t.replace(a, b)
    return t


def diodorus_greek(book, chapter):
    return [(f"{book}.{chapter}.{n}", re.sub(r"\s*\n\s*", " ", t)) for n, t in cts_sections(perseus("tlg0060.tlg001.perseus-grc5"), book, chapter)]


def oldfather(pages, book, chapter):
    eng = {}
    for pg in pages:
        eng.update(lacus_sections(pg))
    keys = sorted([k for k in eng if k.split(".")[0] == str(chapter)], key=lambda k: int(k.split(".")[1]))
    return [(f"{book}.{k}", eng[k]) for k in keys]


# --- Herodotus on Florence, Laur. Plut. 70.3 (A, 10th c.), Teca digitale BML (CONTENTdm IIIF)
BML_SVC = "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:"
BML_VIEW = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/"
LAUR703_PAGES = {"150r": 1357654, "150v": 1357655, "151r": 1357656, "154r": 1357662, "154v": 1357663,
                 "155r": 1357664, "155v": 1357665, "193r": 1357740, "193v": 1357741}
BML_LICENSE = ("Biblioteca Medicea Laurenziana, Teca digitale (access 'Pubblico'); su concessione del Ministero della Cultura; "
               "reproduced for non-commercial study with credit (Italian Code of Cultural Heritage, art. 108 c. 3-bis)")
LAUR703_MS = {
    "scan_source": "Biblioteca Medicea Laurenziana, Teca digitale (CONTENTdm), Plut. 70.3, IIIF manifest https://tecabml.contentdm.oclc.org/iiif/2/plutei:1358114/manifest.json",
    "license": BML_LICENSE,
    "manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 70.3 (Herodotus siglum A), parchment, 374 leaves, 10th century (library dating 901-1000), 31 lines a page",
    "mapping": "Own visual check: the first and last words of every chapter, and every page break inside a chapter, were read on the page images line by line (see each scan_note)",
    "urls": ["https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/1358114",
             "https://tecabml.contentdm.oclc.org/iiif/2/plutei:1358114/manifest.json"],
}


def laur_img(folio):
    return {"file": f"laur70-3-f{folio}.jpg", "service": BML_SVC + str(LAUR703_PAGES[folio]),
            "caption": f"Laur. Plut. 70.3 fol. {folio}"}


HDT_COMMON = dict(
    author_id="herodotus", era="Classical", tradition="greek", category="history", lang_name="Greek",
    language="Greek (Godley 1920) / English (G. C. Macaulay 1890)", century=-5,
    date_approx="c. 430-425 BCE (composition); 10th century (Laur. Plut. 70.3)",
    original_source="A. D. Godley, Herodotus (Loeb, 1920-1925), Greek text, Perseus canonical-greekLit tlg0016.tlg001.perseus-grc2",
    original_license=PERSEUS_LIC,
    translation_source="G. C. Macaulay, The History of Herodotus (London: Macmillan, 1890), vol. 1, Project Gutenberg #2707",
    translation_license="public domain (1890)", translator="G. C. Macaulay (1890)",
    notes=["Greek: A. D. Godley's Loeb text (1920), via Perseus, not a transcription of the manuscript.",
           "English: G. C. Macaulay (1890), from Project Gutenberg; his footnote numbers are removed. Godley's own English on Perseus is a modernized revision and is not used.",
           "Sections follow Herodotus' chapters; the small numbers in the Greek are the sub-sections of the modern editions."],
)


def hdt_section(ch, where, folios, note):
    g = perseus("tlg0016.tlg001.perseus-grc2")
    return (f"4.{ch}", f"Herodotus 4.{ch}; Laur. Plut. 70.3, {where}", greek_sections_html(g, "4", str(ch)),
            esc_p(macaulay_book("IV")[ch]), folios, note + " Read on the BML images (line-numbered full pages and crops).")


def herodotus_4_13_16():
    secs = [
        hdt_section(13, "fol. 150r line 26 to fol. 150v line 7", ["150r", "150v"],
                    "4.13 begins at fol. 150r line 26, ‹ἔφη δὲ ἀριστέης ὁ καϊστροβίου›, after ‹λεγόμενος λόγος εἴρηται›; fol. 150v begins ‹ἐπὶ θάλασσαν· τούτους ὦν πάντας πλὴν ὑπερβορέων›; the chapter ends at 150v line 7, ‹περὶ τῆς χώρης ταύτης σκύθῃσι›."),
        hdt_section(14, "fol. 150v lines 7-26", ["150v"],
                    "4.14 begins at fol. 150v line 7, ‹καὶ ὅθεν μὲν ἦν ἀριστέης ὁ ταῦτα ποιήσας› (the manuscript has ποιήσας where the edition prints εἴπας), and ends at line 26, ‹ἀφανισθῆναι›."),
        hdt_section(15, "fol. 150v line 26 to fol. 151r line 16", ["150v", "151r"],
                    "4.15 begins at fol. 150v line 26, ‹ταῦτα μὲν αἱ πόλιες αὗται λέγουσι›; fol. 151r begins ‹φανέντα σφι ἐς τὴν χώρην›; the chapter ends at 151r line 16, ‹ἀριστέω μέν νυν πέρι τοσαῦτα εἰρήσθω›."),
        hdt_section(16, "fol. 151r lines 16-26", ["151r"],
                    "4.16 begins at fol. 151r line 16, ‹τῆς δὲ γῆς τῆς πέρι ὅδε ὁ λόγος›, and ends at line 26, ‹πᾶν εἰρήσεται›, followed on the same line by 4.17."),
    ]
    return passage(
        slug="herodotus-4-13-16", title="Herodotus, Histories 4.13-16: Aristeas of Proconnesus, the Arimaspians and the Hyperboreans",
        themes=["hyperborea", "hyperboreans", "herodotus", "aristeas", "arimaspians", "greek"],
        description=("Herodotus on the poet Aristeas of Proconnesus, who placed the Hyperboreans beyond the one-eyed Arimaspians and the "
                     "gold-guarding griffins (Histories 4.13-16), on the 10th-century manuscript Laur. Plut. 70.3, fol. 150r-151r."),
        source="Florence, Laur. Plut. 70.3 (Herodotus A, 10th c.) fol. 150r-151r via Teca digitale BML + Godley's Greek (Perseus) + Macaulay's English (1890, Project Gutenberg)",
        intro=["<p>Herodotus of Halicarnassus wrote his <em>Histories</em> in the 430s-420s BCE. In book 4, describing Scythia and the lands to "
               "its north, he reports what the poet Aristeas of Proconnesus said in his lost epic, the <em>Arimaspea</em>: that beyond the "
               "Issedonians lived the one-eyed Arimaspians, beyond them the gold-guarding griffins, and beyond them the Hyperboreans, reaching "
               "to the sea (4.13). He then tells how Aristeas died at Proconnesus and vanished, reappeared seven years later, and 240 years "
               "afterwards appeared at Metapontum in Italy, where he ordered an altar to Apollo (4.14-15), and adds that no one knows by sight "
               "what lies beyond (4.16).</p>",
               "<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 70.3, the oldest manuscript of the <em>Histories</em> "
               "(siglum A), written in the 10th century, 31 lines to the page. 4.13-16 run from fol. 150r line 26 to fol. 151r line 26.</p>"],
        images={k: laur_img(k) for k in ("150r", "150v", "151r")}, sections=secs, ms=LAUR703_MS, **HDT_COMMON)


def herodotus_4_32_36():
    secs = [
        hdt_section(32, "fol. 154r line 26 to fol. 154v line 2", ["154r", "154v"],
                    "4.32 begins at fol. 154r line 26, ‹ὑπερβο-|ρέων δὲ πέρι ἀνθρώπων›, after ‹μακρότατα εἴρηται›; fol. 154v begins ‹ἔστι δὲ καὶ ὁμήρῳ ἐν ἐπιγόνοισι›; the chapter ends at 154v line 2, ‹ταῦτα τὰ ἔπεα ἐποίησε›."),
        hdt_section(33, "fol. 154v lines 2-31", ["154v"],
                    "4.33 begins at fol. 154v line 2, ‹πολλῷ δέ τι πλεῖστα περὶ αὐτῶν δήλιοι λέγουσι›, and ends at line 31, the last line of the page, ‹καλάμης ἐχούσας τὰ ἱρά›."),
        hdt_section(34, "fol. 154v line 31 to fol. 155r line 9", ["154v", "155r"],
                    "4.34 begins at fol. 154v line 31, ‹καὶ ταῦτα δὴ ταύτας οἶδα ποιεύσας›; fol. 155r begins ‹τῇσι δὲ παρθένοισι ταύτῃσι τῇσι ἐξ ὑπερβορέων›; the chapter ends at 155r line 9, ‹οὗτοι ἐπὶ τὸ σῆμα›."),
        hdt_section(35, "fol. 155r lines 9-30", ["155r"],
                    "4.35 begins at fol. 155r line 9, ‹αὗται μὲν δὴ ταύτην τιμὴν ἔχουσι›, and ends at line 30, ‹ἀγχοτάτω τοῦ κηΐων ἱστιητορίου›."),
        hdt_section(36, "fol. 155r line 30 to fol. 155v line 11", ["155r", "155v"],
                    "4.36 begins at fol. 155r line 30, ‹καὶ ταῦτα μὲν ὑπερβορέων πέρι εἰρήσθω›; fol. 155v begins ‹-ριος λόγον τοῦ λεγομένου εἶναι ὑπερβορέου› (the end of Ἀβάριος); the chapter ends at 155v line 11, ‹ἐς γραφὴν ἑκάστη›."),
    ]
    return passage(
        slug="herodotus-4-32-36", title="Herodotus, Histories 4.32-36: the Hyperboreans and their offerings to Delos",
        themes=["hyperborea", "hyperboreans", "herodotus", "delos", "apollo", "abaris", "greek"],
        description=("Herodotus' chapters on the Hyperboreans: their sacred offerings wrapped in wheat straw, the maidens Hyperoche, Laodice, "
                     "Arge and Opis who came to Delos, and Abaris with his arrow (Histories 4.32-36), on Laur. Plut. 70.3, fol. 154r-155v."),
        source="Florence, Laur. Plut. 70.3 (Herodotus A, 10th c.) fol. 154r-155v via Teca digitale BML + Godley's Greek (Perseus) + Macaulay's English (1890, Project Gutenberg)",
        intro=["<p>In <em>Histories</em> 4.32-36 Herodotus collects what was said about the Hyperboreans. The Scythians know nothing of them, "
               "though Hesiod and the epic <em>Epigoni</em> mention them (4.32). The Delians tell most: offerings wrapped in wheat straw travel "
               "from the Hyperboreans through Scythia to the Adriatic, Dodona, the Malian gulf, Euboea and Tenos to Delos (4.33). The "
               "Hyperboreans first sent two maidens, Hyperoche and Laodice, with five escorts who never returned, and the Delians still cut "
               "their hair for them (4.33-34); earlier still Arge and Opis came with the gods themselves (4.35). Herodotus declines to tell the "
               "story of Abaris, who carried an arrow round the earth without eating, and ends by laughing at the round maps of his day (4.36).</p>",
               "<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 70.3, the oldest manuscript of the <em>Histories</em> "
               "(siglum A), 10th century. 4.32-36 run from fol. 154r line 26 to fol. 155v line 11.</p>"],
        images={k: laur_img(k) for k in ("154r", "154v", "155r", "155v")}, sections=secs, ms=LAUR703_MS, **HDT_COMMON)


def herodotus_4_184_185():
    secs = [
        hdt_section(184, "fol. 193r lines 1-22", ["193r"],
                    "4.184 begins with the first line of fol. 193r, ‹ἀπὸ δὲ γαραμάντων δι' ἀλλέων δέκα ἡμερέων› (fol. 192v ends 4.183); at lines 3-4 the manuscript reads ‹ἄτλαν|τες› where the edition prints Ἀτάραντες; the chapter ends at line 22, ‹οὔτε ἐνύπνια ὁρᾶν›."),
        hdt_section(185, "fol. 193r line 22 to fol. 193v line 5", ["193r", "193v"],
                    "4.185 begins at fol. 193r line 22, ‹μέχρι μὲν δὴ τῶν ἀτλάντων›; fol. 193v begins ‹ὁ δὲ ἅλς αὐτόθι καὶ λευκὸς καὶ πορφύρεος›; the chapter ends at 193v line 5, ‹καὶ ἰκμάδος ἐστὶ ἐν αὐτῇ οὐδέν›."),
    ]
    return passage(
        slug="herodotus-4-184-185", title="Herodotus, Histories 4.184-185: Mount Atlas and the Atlantes",
        themes=["atlantis", "atlas", "atlantes", "herodotus", "libya", "greek"],
        description=("Herodotus on Mount Atlas, 'the pillar of heaven', and the Atlantes of Libya who eat no living thing and never dream "
                     "(Histories 4.184-185), on the 10th-century manuscript Laur. Plut. 70.3, fol. 193r-193v."),
        source="Florence, Laur. Plut. 70.3 (Herodotus A, 10th c.) fol. 193r-193v via Teca digitale BML + Godley's Greek (Perseus) + Macaulay's English (1890, Project Gutenberg)",
        intro=["<p>At the end of his survey of the peoples along the sand belt of Libya, Herodotus (c. 430 BCE) describes a salt hill near "
               "Mount Atlas, so high that its summit is never seen for clouds, which the natives call the pillar of heaven. The people "
               "there are named after the mountain, the Atlantes; they are said to eat nothing that has life and to have no dreams (4.184). "
               "Beyond them the sand belt runs on to the Pillars of Heracles and beyond (4.185). This is the oldest surviving mention of a "
               "people named after Atlas in the far west, written some seventy years before Plato's Atlantis (Herodotus c. 430 BCE, the Timaeus and Critias c. 360 BCE).</p>",
               "<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 70.3 (Herodotus A, 10th century). 4.184 opens fol. 193r; "
               "4.185 ends at fol. 193v line 5. Where the edition prints Ἀτάραντες (the nameless people of 4.184.1), this manuscript reads "
               "ἄτλαντες.</p>"],
        images={k: laur_img(k) for k in ("193r", "193v")}, sections=secs, ms=LAUR703_MS, **HDT_COMMON)


# --- Strabo on Paris gr. 1397 (A, books 1-9) and Paris gr. 1393 (C, books 10-17), BnF via openapi.bnf.fr
GR1397 = "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b10721749w/f"
GR1393 = "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b8468312f/f"
STRABO_IMAGES = {
    "1397-34v": {"file": "bnf-gr1397-f34v.jpg", "service": GR1397 + "41", "region": "pct:0,0,50,100", "caption": "Paris gr. 1397 fol. 34v"},
    "1397-58r": {"file": "bnf-gr1397-f58r.jpg", "service": GR1397 + "64", "region": "pct:50,0,50,100", "caption": "Paris gr. 1397 fol. 58r"},
    "1397-155v": {"file": "bnf-gr1397-f155v.jpg", "service": GR1397 + "162", "region": "pct:0,0,50,100", "caption": "Paris gr. 1397 fol. 155v"},
    "1397-156r": {"file": "bnf-gr1397-f156r.jpg", "service": GR1397 + "162", "region": "pct:50,0,50,100", "caption": "Paris gr. 1397 fol. 156r"},
    "1393-132v": {"file": "bnf-gr1393-f132v.jpg", "service": GR1393 + "274", "caption": "Paris gr. 1393 fol. 132v"},
    "1393-207v": {"file": "bnf-gr1393-f207v.jpg", "service": GR1393 + "424", "caption": "Paris gr. 1393 fol. 207v"},
}
STRABO_A = {
    "scan_source": "Bibliothèque nationale de France, Gallica https://gallica.bnf.fr/ark:/12148/btv1b10721749w (IIIF via openapi.bnf.fr; black-and-white images made from microfilm, each image a two-page opening, cropped here to the page)",
    "license": BNF_LICENSE,
    "manuscript": "Paris, BnF, grec 1397 (Strabo siglum A), parchment palimpsest, 232 fol., books 1-9, 11th century (BnF dating 1001-1100; often dated 10th c.)",
    "mapping": "Own visual check: first and last words and line numbers read on the page images (line-numbered pages and crops); image fN shows fol. (N-7)v and (N-6)r, confirmed from the modern foliation",
    "urls": ["https://gallica.bnf.fr/ark:/12148/btv1b10721749w", "http://archivesetmanuscrits.bnf.fr/ark:/12148/cc214890"],
}
STRABO_C = {
    "scan_source": "Bibliothèque nationale de France, Gallica https://gallica.bnf.fr/ark:/12148/btv1b8468312f (IIIF via openapi.bnf.fr)",
    "license": BNF_LICENSE,
    "manuscript": "Paris, BnF, grec 1393 (Strabo siglum C), bombycin, 260 fol., books 1-17, 13th-14th century (BnF dating 1250-1350)",
    "mapping": "Own visual check: first and last words and line numbers read on the page images (line-numbered pages and crops)",
    "urls": ["https://gallica.bnf.fr/ark:/12148/btv1b8468312f", "http://archivesetmanuscrits.bnf.fr/ark:/12148/cc214851"],
}
STRABO_COMMON = dict(
    author_id="strabo", era="Imperial", tradition="greek", category="history", lang_name="Greek",
    language="Greek (Meineke) / English (H. C. Hamilton and W. Falconer 1854-1857)", century=1,
    original_source="A. Meineke, Strabonis Geographica (Teubner, 1877), Perseus canonical-greekLit tlg0099.tlg001.perseus-grc2",
    original_license=PERSEUS_LIC,
    translation_source="H. C. Hamilton and W. Falconer, The Geography of Strabo (London: Bohn, 1854-1857), Perseus tlg0099.tlg001.perseus-eng4",
    translation_license="public domain (1854-1857); Perseus digital text CC BY-SA 4.0", translator="H. C. Hamilton and W. Falconer (1854-1857)",
)


def strabo_text(b, c, s):
    g = cts_text(perseus("tlg0099.tlg001.perseus-grc2"), b, c, s)
    e = cts_text(perseus("tlg0099.tlg001.perseus-eng4"), b, c, s)
    return para_html(g), para_html(e)


def strabo_passage(ref, slug, title, description, intro, imgs, where, note, ms, ms_name, date_ms, themes):
    b, c, s = ref.split(".")
    g, e = strabo_text(b, c, s)
    return passage(
        slug=slug, title=title, themes=themes, description=description,
        source=f"{ms_name} via Gallica (BnF) + Meineke's Greek (Perseus) + Hamilton and Falconer's English (1854-1857, Perseus)",
        intro=intro, images={k: STRABO_IMAGES[k] for k in imgs},
        sections=[(ref, f"Strabo, Geography {ref}; {where}", g, e, imgs, note + " Read on the BnF images (line-numbered page and crops).")],
        ms=ms, date_approx=f"c. 20 AD (composition); {date_ms}",
        notes=["Greek: Meineke's Teubner text (Perseus), not a transcription of the manuscript.",
               "English: Hamilton and Falconer (Bohn, 1854-1857), who translated the earlier text of Kramer; small differences from Meineke's Greek result."],
        **STRABO_COMMON)


def strabo_1_3_22():
    return strabo_passage(
        "1.3.22", "strabo-1-3-22", "Strabo, Geography 1.3.22: Eratosthenes, Herodotus and the Hyperboreans",
        "Strabo reports Eratosthenes' reply to Herodotus' remark that if there are Hyperboreans there must be Hypernotians (Geography 1.3.22), on the manuscript Paris gr. 1397, fol. 34v.",
        ["<p>Strabo of Amaseia wrote his <em>Geography</em> under Augustus and Tiberius. At 1.3.22 he reports how Eratosthenes answered "
         "Herodotus' joke (Hdt. 4.36) that if there are Hyperboreans there must also be Hypernotians, and adds his own view that "
         "Herodotus' error lay in thinking the Hyperboreans were so called because the north wind does not blow on them; the poets' "
         "commentators, he says, meant simply the most northerly people.</p>",
         "<p>The manuscript is Paris, BnF, grec 1397 (Strabo A), the oldest manuscript of books 1-9, a palimpsest of the 10th-11th century, "
         "here in the BnF's black-and-white microfilm images. 1.3.22 stands on fol. 34v, lines 16-34.</p>"],
        ["1397-34v"], "Paris gr. 1397, fol. 34v lines 16-34",
        ("1.3.22 begins at fol. 34v line 16, after ‹οἰκείαν ἱστορίαν›: ‹ἐπάνιμεν δ' ἐπὶ τὰ ἑξῆς· ἀφ' ὧν παρέ-|βημεν›; line 17 has "
         "‹τοῦ γὰρ ἡροδότου μηδένας ὑπερβορείους›; the section ends at line 34, ‹ἀνέμων δ' ὁ αὐτὸς ὅρος›. "
         "The page begins ‹μάδυός τε τοῦ σκυθικοῦ› (in 1.3.21); its torn lower edge does not touch lines 16-34."),
        STRABO_A, "Paris, BnF, grec 1397 (Strabo A) fol. 34v", "10th-11th century (Paris gr. 1397)",
        ["hyperborea", "hyperboreans", "strabo", "eratosthenes", "herodotus", "geography", "greek"])


def strabo_7_3_1():
    return strabo_passage(
        "7.3.1", "strabo-7-3-1", "Strabo, Geography 7.3.1: ignorance of the north and the tales of the Rhipaean mountains and the Hyperboreans",
        "Strabo on the lands beyond the Elbe and the Danube, where ignorance gave credit to the fables of the Rhipaean mountains and the Hyperboreans (Geography 7.3.1), on Paris gr. 1397, fol. 155v-156r.",
        ["<p>At 7.3.1, turning from the Germans to the Getae beyond the Danube, Strabo says that lack of knowledge of these northern regions "
         "is what gave credit to those who invented the Rhipaean mountains and the Hyperboreans, and to Pytheas' fabrications about the "
         "northern ocean, which he sets aside.</p>",
         "<p>The manuscript is Paris, BnF, grec 1397 (Strabo A), 10th-11th century. 7.3.1 runs from fol. 155v line 18 to fol. 156r line 2; "
         "the Hyperboreans are named on 155v line 27.</p>"],
        ["1397-155v", "1397-156r"], "Paris gr. 1397, fol. 155v line 18 to fol. 156r line 2",
        ("7.3.1 begins at fol. 155v line 18, ‹τὸ δὲ νότιον μέρος τῆς γερμανίας τὸ πέραν τοῦ ἄλ-|βιος›; line 27 reads ‹ὄρη καὶ τοὺς "
         "ὑπερβορείους μυθοποιοῦντες›; fol. 155v ends (line 36) ‹ἀλλ' ἐατέον ὥσπερ καὶ ἐν τῷ› and fol. 156r begins ‹φαίδρῳ ὁ "
         "σωκράτης›; the section ends at 156r line 2, ‹παρειλήφαμεν· ταῦτα λέγωμεν›."),
        STRABO_A, "Paris, BnF, grec 1397 (Strabo A) fol. 155v-156r", "10th-11th century (Paris gr. 1397)",
        ["hyperborea", "hyperboreans", "strabo", "rhipaean-mountains", "geography", "greek"])


def strabo_11_6_2():
    return strabo_passage(
        "11.6.2", "strabo-11-6-2", "Strabo, Geography 11.6.2: the northern peoples whom earlier writers called Hyperboreans",
        "Strabo on the peoples around the Caspian, and the older Greek writers who called those above the Euxine, the Danube and the Adriatic Hyperboreans (Geography 11.6.2), on Paris gr. 1393, fol. 132v.",
        ["<p>At 11.6.2, sailing into the Caspian Sea, Strabo lists the Scythian peoples on either hand and notes that the early Greek "
         "historians called all the northern peoples Scythians or Celto-Scythians, while writers still earlier called those living above "
         "the Euxine, the Danube and the Adriatic Hyperboreans, Sauromatians and Arimaspians.</p>",
         "<p>Paris gr. 1397 breaks off in book 9, so books 10-17 are shown on Paris, BnF, grec 1393 (Strabo C), a complete Strabo of the late "
         "13th or early 14th century in a heavily abbreviated cursive. 11.6.2 stands on fol. 132v, lines 12-25; the Hyperboreans are named on line 19.</p>"],
        ["1393-132v"], "Paris gr. 1393, fol. 132v lines 12-25",
        ("11.6.2 begins at fol. 132v line 12, after ‹καὶ μάλιστα περὶ τῶν διαστημάτων›: ‹εἰσπλέ-|οντι δ' ἐν δεξιᾷ μὲν τοῖς εὐρωπαίοις›; "
         "line 19 reads ‹καὶ τοῦ ἀδρίου κατοικοῦντας, ὑπερβορέους ἔλεγον καὶ σαυρομάτ(ας)›; the section ends at line 25, "
         "‹ἁπλότητα καὶ τὴν φιλομυθίαν›, followed by 11.6.3. The page begins ‹ἀρχὴ αὕτη ἀπὸ τῆς κασπίας θαλάττης› (in 11.6.1). "
         "Line numbers on this page carry a margin of one line (a flourish above the text)."),
        STRABO_C, "Paris, BnF, grec 1393 (Strabo C) fol. 132v", "13th-14th century (Paris gr. 1393)",
        ["hyperborea", "hyperboreans", "strabo", "arimaspians", "geography", "greek"])


def strabo_15_1_57():
    return strabo_passage(
        "15.1.57", "strabo-15-1-57", "Strabo, Geography 15.1.57: Megasthenes' marvels and the thousand-year Hyperboreans",
        "Strabo rejects the marvels Megasthenes told of India, among them the Hyperboreans who live a thousand years, as Simonides and Pindar also said (Geography 15.1.57), on Paris gr. 1393, fol. 207v.",
        ["<p>At 15.1.57 Strabo lists, and dismisses, the marvels told by Megasthenes about India: men of three spans who fight cranes, "
         "men with ears they sleep in, and, he says, the Hyperboreans who live a thousand years, described as Simonides, Pindar and other "
         "myth-writers described them.</p>",
         "<p>The manuscript is Paris, BnF, grec 1393 (Strabo C), late 13th or early 14th century. 15.1.57 stands on fol. 207v, lines 7-28.</p>"],
        ["1393-207v"], "Paris gr. 1393, fol. 207v lines 7-28",
        ("15.1.57 begins at fol. 207v line 7, ‹ὑπερεκπίπτων δ' ἐπὶ τὸ μυθῶδες πεν-|τασπιθάμους›, after ‹τοὺς δὲ διπλασίους›; "
         "‹περὶ δὲ τῶν χιλιετῶν ὑπερβορέων› closes line 24 and line 25 reads ‹τὰ αὐτὰ λέγει σιμωνίδῃ καὶ πινδάρῳ›; Megasthenes is named on "
         "line 27; the section ends at line 28, ‹καὶ ἐν ἰβηρίᾳ συμβαίνει›, followed by 15.1.58."),
        STRABO_C, "Paris, BnF, grec 1393 (Strabo C) fol. 207v", "13th-14th century (Paris gr. 1393)",
        ["hyperborea", "hyperboreans", "strabo", "megasthenes", "pindar", "geography", "greek"])


def strabo_2_3_6():
    """For the atlantis collection."""
    return strabo_passage(
        "2.3.6", "strabo-2-3-6", "Strabo, Geography 2.3.6: Posidonius on Plato's Atlantis",
        "Strabo reports that Posidonius rightly cited Plato's view that the story of the island of Atlantis, told to Solon by the Egyptian priests, may not be a fiction (Geography 2.3.6), on Paris gr. 1397, fol. 58r.",
        ["<p>In book 2 of his <em>Geography</em> Strabo reviews the work of the Stoic Posidonius (c. 135-51 BCE). Posidonius was right, he "
         "says, about the risings and sinkings of the earth caused by earthquakes, and did well to cite Plato, that the story of the island "
         "of Atlantis may not be an invention: Solon, on the authority of the Egyptian priests, said it once existed and vanished, an island "
         "no smaller than a continent. Posidonius thought this better than saying that its inventor made it vanish, as the poet did the "
         "Achaean wall. This is the earliest surviving discussion of whether Plato's Atlantis was real.</p>",
         "<p>The manuscript is Paris, BnF, grec 1397 (Strabo A), the oldest manuscript of books 1-9, 10th-11th century, in the BnF's "
         "black-and-white microfilm images. 2.3.6 stands on fol. 58r, lines 11-29; the words on Plato and Atlantis are on lines 15-17.</p>"],
        ["1397-58r"], "Paris gr. 1397, fol. 58r lines 11-29",
        ("2.3.6 begins at fol. 58r line 11, after ‹ταῦτα μὲν οὖν οὐκ εὖ›: ‹τὸ δὲ ἐξαίρεσθαι τὴν | γῆν ποτε›; the words "
         "‹τὸ τοῦ πλάτωνος εὖ παρατίθησιν ... τῆς ἀτλαντίδος› run over lines 15-17; the section ends at line 29, ‹ἐν τοσαύταις "
         "μυριάσιν ἔλθοι ἂν | εἰς ἰνδούς›, followed on the same line by 2.3.7 ‹ἐπιχειρήσας δὲ αἰτιᾶσθαι›. The page begins ‹τῶν "
         "τοιούτων· οὐ καὶ δυνατὸν μέν›."),
        STRABO_A, "Paris, BnF, grec 1397 (Strabo A) fol. 58r", "10th-11th century (Paris gr. 1397)",
        ["atlantis", "plato", "posidonius", "solon", "strabo", "geography", "greek"])


def verse_passage_sections(greek, chunks, pages, label, ref_name, ms_name, page_notes, total_last):
    """pages: [(image key, first line, last line)]; page_notes: {image key: text}. One section per group of
    translation chunks lying on the same page(s)."""
    out = []
    for sid, rng, g_html, e_html, keys in verse_sections(greek, chunks, pages, label, ref_name, total_last):
        a, b = (int(x) for x in (rng.split("-") + [rng])[:2])
        where = "; ".join(f"{k}: {page_notes[k]}" for k in keys)
        note = (f"Lines {rng} stand on {ms_name} " + " and ".join(k for k in keys) + ". Checked on the images: " + where)
        out.append((sid, f"{ref_name} {rng}; {ms_name} " + ", ".join(keys), g_html, e_html, keys, note))
    return out


def pausanias_sections(book, chapter, subs, placements, ms_name):
    """placements: {sub: (where, [image keys], note)}"""
    g = perseus("tlg0525.tlg001.perseus-grc2")
    e = perseus("tlg0525.tlg001.perseus-eng2")
    out = []
    for n in subs:
        where, keys, note = placements[n]
        out.append((f"{book}.{chapter}.{n}", f"Pausanias {book}.{chapter}.{n}; {ms_name}, {where}",
                    para_html(cts_text(g, book, chapter, n)), para_html(cts_text(e, book, chapter, n)), keys, note))
    return out


PAUS_COMMON = dict(
    author_id="pausanias", era="Imperial", tradition="greek", category="history", lang_name="Greek",
    language="Greek (Spiro 1903) / English (W. H. S. Jones and H. A. Ormerod 1918-1935)", century=2,
    original_source="F. Spiro, Pausaniae Graeciae descriptio (Teubner, 1903), Perseus canonical-greekLit tlg0525.tlg001.perseus-grc2",
    original_license=PERSEUS_LIC,
    translation_source="W. H. S. Jones (and H. A. Ormerod), Pausanias, Description of Greece (Loeb, 4 vols., 1918-1935), Perseus tlg0525.tlg001.perseus-eng2",
    translation_license=("public domain in the US: vols. 1-2 published 1918 and 1926; vol. 4 (1935, book 10) not renewed, no entry in the "
                         "1962-1963 renewal lists (data/sources/hyperborea/renewals/); Perseus digital text CC BY-SA 4.0"),
    translator="W. H. S. Jones (1918-1935)",
    notes=["Greek: Spiro's Teubner text via Perseus, not a transcription of the manuscript.",
           "English: Jones's Loeb translation via Perseus; Jones's footnotes are omitted."],
)


# --- Greek poetry. POETRY holds, per poem, the manuscript, its page images and which lines each page carries
#     (filled from the readings of the page images; see each scan_note).
POETRY = {}


def pindar_passage(key, ode_book, ode, urn_g, urn_e, slug, title, description, intro, themes, date_approx, first=None, last=None):
    P = POETRY[key]
    greek = verse_lines(perseus(urn_g), str(ode))
    total = greek[-1][0]
    chunks = [(a, b if b is not None else total, t) for a, b, t in svarlien_chunks(urn_e, str(ode))]
    if first or last:
        lo, hi = first or 1, last or total
        chunks = [c for c in chunks if c[0] >= lo and c[1] <= hi]
        assert chunks and chunks[0][0] == lo and chunks[-1][1] == hi, (lo, hi, chunks[0][:2], chunks[-1][:2])
        greek = [(n, t) for n, t in greek if lo <= n <= hi]
    secs = verse_passage_sections(greek, chunks, P["pages"], f"{ode_book} {ode}", f"Pindar, {ode_book} {ode}", P["ms_short"], P["page_notes"], total)
    return passage(
        slug=slug, title=title, themes=themes, description=description,
        source=f"{P['ms_short']} via {P['library']} + Sandys' Greek (Perseus) + D. A. Svarlien's English (Perseus, CC BY-SA)",
        intro=intro + [P["ms_intro"]], images=P["images"], sections=secs, ms=P["ms"],
        author_id="pindar", era="Classical", tradition="greek", category="literature", lang_name="Greek",
        language="Greek (Sandys) / English (Diane Arnson Svarlien 1990)", century=-5, date_approx=date_approx,
        original_source=f"J. Sandys, The Odes of Pindar (Loeb, 1915; 1937 reprint), Perseus canonical-greekLit {urn_g}",
        original_license=PERSEUS_LIC,
        translation_source=f"Diane Arnson Svarlien, Pindar's Odes (1990), made for the Perseus Digital Library, {urn_e}",
        translation_license="Creative Commons BY-SA 4.0 (Perseus Digital Library); openly licensed",
        translator="Diane Arnson Svarlien (1990)",
        notes=["Line numbers are those of the modern editions; the manuscript divides Pindar's verse into shorter cola, so its lines do not match them one for one. The scan_notes give the words that begin and end each page as read.",
               "English: Svarlien's line-grouped translation (Perseus), which keeps the editions' line numbers and so can be divided at the manuscript's page breaks. Perseus prints '«' for an apostrophe in a few words; it is restored here.",
               "Greek: Sandys' Loeb text (Perseus), not a transcription of the manuscript."])


def hymn7_passage():
    P = POETRY["hh7"]
    greek = verse_lines(perseus("tlg0013.tlg007.perseus-grc2"))
    chunks = [(a, b, t) for a, b, t in evelyn_white_hymn7()]
    secs = verse_passage_sections(greek, chunks, P["pages"], "HH 7", "Homeric Hymn 7", P["ms_short"], P["page_notes"], 59)
    return passage(
        slug="homeric-hymn-7-dionysus", title="Homeric Hymn 7, To Dionysus: the pirates, 'to Egypt or Cyprus or the Hyperboreans'",
        themes=["hyperborea", "hyperboreans", "homeric-hymns", "dionysus", "greek", "poetry"],
        description=("The seventh Homeric Hymn, Dionysus and the Tyrrhenian pirates, whose master guesses the captive god is bound for Egypt, "
                     "Cyprus or the Hyperboreans (lines 28-29), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Evelyn-White's Greek and English (1914; Perseus and Project Gutenberg)",
        intro=["<p>The seventh <em>Homeric Hymn</em>, to Dionysus, probably of the 6th century BCE, tells how Tyrrhenian pirates seized the "
               "young god on a headland. The helmsman warns that he is a god; the master scoffs that the captive is bound for Egypt or Cyprus "
               "or the Hyperboreans or further still (lines 28-29), the Hyperboreans standing for the farthest edge of the world. Wine "
               "flows through the ship, a vine and ivy cover the mast, the god becomes a lion, and the sailors leap overboard and become "
               "dolphins; only the helmsman is spared.</p>", P["ms_intro"]],
        images=P["images"], sections=secs, ms=P["ms"],
        author_id="homer", era="Classical", tradition="greek", category="literature", lang_name="Greek",
        language="Greek and English (H. G. Evelyn-White 1914)", century=-6,
        date_approx=f"6th century BCE (probable composition); {P['ms_date']}",
        original_source="H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Greek text, Perseus canonical-greekLit tlg0013.tlg007.perseus-grc2",
        original_license=PERSEUS_LIC,
        translation_source="H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Project Gutenberg #348",
        translation_license="public domain (1914)", translator="H. G. Evelyn-White (1914)",
        notes=["The Homeric Hymns are anonymous; they were transmitted under Homer's name.",
               "Evelyn-White's English is divided by his own line references, '(ll. 1-16)' and so on; each section here is one or more of his paragraphs, linked to the page(s) carrying those lines.",
               "Project Gutenberg's endnote numbers are removed; '...' in lines 55-57 marks a lacuna in the Greek, as in Evelyn-White."])


def apollonius_passage():
    P = POETRY["ar"]
    greek = verse_lines(perseus("tlg0001.tlg001.perseus-grc2"), "4", levels=("book",), first=592, last=626)
    eng = seaton_paragraph("Thus Argo cried through the darkness", "drops of oil.")
    keys = [k for k, f, l in P["pages"]]
    note = "Lines 4.592-626 stand on " + P["ms_short"] + ". Checked on the images: " + "; ".join(f"{k}: {P['page_notes'][k]}" for k in keys)
    return passage(
        slug="apollonius-argonautica-4-592-626", title="Apollonius of Rhodes, Argonautica 4.592-626: the Eridanus, amber, and Apollo's tears among the Hyperboreans",
        themes=["hyperborea", "hyperboreans", "apollonius", "argonautica", "apollo", "eridanus", "greek", "poetry"],
        description=("The Argonauts enter the Eridanus, where the Heliades weep amber; the Celts say these are the tears Apollo shed when he went "
                     "to the sacred race of the Hyperboreans (Argonautica 4.592-626), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Mooney's Greek (Perseus) + Seaton's English (1912, Project Gutenberg)",
        intro=["<p>Apollonius of Rhodes wrote the <em>Argonautica</em> in Alexandria in the 3rd century BCE. In book 4 the Argo, sailing home "
               "by the rivers of Europe, enters the Eridanus, where Phaethon fell burning from the chariot of the Sun and his sisters, turned "
               "into poplars, weep tears of amber. The Celts tell another story: that these are the tears of Apollo, shed when he left heaven "
               "for the sacred race of the Hyperboreans, banished by Zeus in his anger over the death of his son Asclepius (lines 611-617).</p>",
               P["ms_intro"]],
        images=P["images"],
        sections=[("4.592-626", "Apollonius, Argonautica 4.592-626; " + P["ms_short"], lines_html(greek), esc_p(eng), keys, note)],
        ms=P["ms"], author_id="apollonius-rhodes", era="Hellenistic", tradition="greek", category="literature", lang_name="Greek",
        language="Greek (Mooney 1912) / English (R. C. Seaton 1912)", century=-3,
        date_approx=f"3rd century BCE (composition); {P['ms_date']}",
        original_source="G. W. Mooney, The Argonautica of Apollonius Rhodius (London, 1912), Perseus canonical-greekLit tlg0001.tlg001.perseus-grc2",
        original_license=PERSEUS_LIC,
        translation_source="R. C. Seaton, Apollonius Rhodius: The Argonautica (Loeb, 1912), Project Gutenberg #830",
        translation_license="public domain (1912)", translator="R. C. Seaton (1912)",
        notes=["Seaton's prose paragraph renders lines 592-626 as a whole, so the passage is one section linked to every page that carries it; the scan_note gives the lines on each page."])


def callimachus_passage():
    P = POETRY["call"]
    greek = verse_lines(perseus("tlg0533.tlg018.perseus-grc4"), first=275, last=299)
    eng = mair_delos_275_299()
    keys = [k for k, f, l in P["pages"]]
    note = "Lines 275-299 stand on " + P["ms_short"] + ". Checked on the images: " + "; ".join(f"{k}: {P['page_notes'][k]}" for k in keys)
    return passage(
        slug="callimachus-hymn-delos-275-299", title="Callimachus, Hymn to Delos 275-299: the offerings of the Hyperboreans",
        themes=["hyperborea", "hyperboreans", "callimachus", "delos", "apollo", "greek", "poetry"],
        description=("Callimachus on the first-fruits sent to Delos by the Hyperboreans, 'a very long-lived race', and the daughters of Boreas "
                     "who first brought them (Hymn 4.275-299), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Wilamowitz's Greek (1897, Perseus) + A. W. Mair's English (1921)",
        intro=["<p>Callimachus of Cyrene wrote his <em>Hymn to Delos</em> in Alexandria in the 3rd century BCE. Near its end he tells how "
               "every year all cities send tithes and choirs to Delos, among them the peoples beyond the north wind, a very long-lived race. "
               "Their offerings of corn-sheaves pass through the Pelasgians of Dodona, the Malian land and Euboea; they were first brought from "
               "the Arimaspians by Upis, Loxo and Hecaerge, daughters of Boreas, who never went home, and in whose honour the girls and boys "
               "of Delos still offer their hair.</p>", P["ms_intro"]],
        images=P["images"],
        sections=[("275-299", "Callimachus, Hymn 4 (Delos) 275-299; " + P["ms_short"], lines_html(greek), esc_p(eng), keys, note)],
        ms=P["ms"], author_id="callimachus", era="Hellenistic", tradition="greek", category="literature", lang_name="Greek",
        language="Greek (Wilamowitz 1897) / English (A. W. Mair 1921)", century=-3,
        date_approx=f"3rd century BCE (composition); {P['ms_date']}",
        original_source="U. von Wilamowitz-Moellendorff, Callimachi hymni et epigrammata (Berlin, 1897), Perseus canonical-greekLit tlg0533.tlg018.perseus-grc4",
        original_license=PERSEUS_LIC,
        translation_source=("A. W. Mair, Callimachus and Lycophron (Loeb, 1921), Hymn IV lines 275-299, from the theoi.com transcription "
                            "corrected against the 1921 print (archive.org callimachuslycop00calluoft)"),
        translation_license="public domain (1921)", translator="A. W. Mair (1921)",
        notes=["Mair's English is one paragraph for lines 275-299, so the passage is one section linked to every page that carries it.",
               "Five slips in the theoi.com transcription were corrected to the printed 1921 text (e.g. 'returned not home', 'sweet-sounding'); Mair's notes are omitted."])


# --- Greek prose read by section: PROSE holds per passage the manuscript, images and per-section placements.
PROSE = {}

DIOD_COMMON = dict(
    author_id="diodorus", era="Late Republic", tradition="greek", category="history", lang_name="Greek",
    language="Greek (Bekker, Dindorf, Vogel) / English (C. H. Oldfather 1935)", century=-1,
    original_source="Diodori Bibliotheca historica, ed. I. Bekker, L. Dindorf, F. Vogel (Teubner, 1888-1906), Perseus canonical-greekLit tlg0060.tlg001.perseus-grc5",
    original_license=PERSEUS_LIC,
    translator="C. H. Oldfather (1935)",
)
OLDFATHER_LIC = ("public domain in the US: Loeb Diodorus vol. II (1935) was not renewed (no Diodorus or Oldfather entry in the "
                 "1962-1963 renewal lists, data/sources/hyperborea/renewals/; LacusCurtius states the same)")


def diodorus_2_47():
    P = PROSE["diod2"]
    g = dict(diodorus_greek("2", "47"))
    e = dict(oldfather([SRC / "lacus-diodorus-2B.html"], 2, 47))
    secs = []
    for sid, gkeys, ekey in [("2.47.1", ["2.47.1"], "2.47.1"), ("2.47.2", ["2.47.2"], "2.47.2"), ("2.47.3", ["2.47.3"], "2.47.3"),
                             ("2.47.4", ["2.47.4"], "2.47.4"), ("2.47.5", ["2.47.5"], "2.47.5"), ("2.47.6-7", ["2.47.6", "2.47.7"], "2.47.6")]:
        where, keys, note = P["place"][sid]
        secs.append((sid, f"Diodorus 2.47 ({sid}); {P['ms_short']}, {where}", numbered_html([(k, g[k]) for k in gkeys]),
                     numbered_html([(ekey, e[ekey])]), keys, note))
    return passage(
        slug="diodorus-2-47", title="Diodorus of Sicily, Library 2.47: Hecataeus on the Hyperboreans, their island and Apollo's round temple",
        themes=["hyperborea", "hyperboreans", "diodorus", "hecataeus", "apollo", "delos", "abaris", "greek"],
        description=("Diodorus' account, after Hecataeus of Abdera, of the Hyperboreans' island beyond the land of the Celts, with its "
                     "precinct and round temple of Apollo (Library 2.47), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Vogel's Greek (Perseus) + Oldfather's English (Loeb 1935, LacusCurtius)",
        intro=["<p>Diodorus of Sicily compiled his <em>Library of History</em> between about 60 and 30 BCE. At 2.47, after Asia's northern "
               "lands, he gives the fullest ancient description of the Hyperboreans, taken from Hecataeus of Abdera (c. 300 BCE) and others: "
               "an island in the ocean beyond the land of the Celts, no smaller than Sicily, fertile, with two harvests a year; Leto was born "
               "there, so Apollo is honoured above all gods, in a magnificent precinct and a notable temple, spherical in shape; a city of "
               "harpers sings his praise. The Hyperboreans are friends of the Greeks, especially the Athenians and Delians; Abaris came from "
               "them to Greece; the moon seen from the island looks close; the god visits every nineteen years, the cycle of Meton, and "
               "dances from the spring equinox to the rising of the Pleiades; its rulers, the Boreadae, descend from Boreas.</p>",
               P["ms_intro"]],
        images=P["images"], sections=secs, ms=P["ms"], date_approx=f"c. 60-30 BCE (composition); {P['ms_date']}",
        translation_source="C. H. Oldfather, Diodorus of Sicily vol. II (Loeb, 1935), 2.47, transcription by Bill Thayer, LacusCurtius https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Diodorus_Siculus/2B*.html",
        translation_license=OLDFATHER_LIC,
        notes=["Vogel's Greek divides 2.47 into seven sub-sections, Oldfather's English into six; the last English section covers Greek 6-7.",
               "English from Bill Thayer's LacusCurtius transcription of Oldfather, with his note markers removed; 2.47.4 reads 'we informed' in that transcription and is left as it stands.",
               "Greek: Teubner text via Perseus, not a transcription of the manuscript."],
        **DIOD_COMMON)


def diodorus_3_53_61():
    """For the atlantis collection: one section per chapter."""
    P = PROSE["diod3"]
    pages = [SRC_ATL / f"lacus-diodorus-{x}.html" for x in ("3C", "3D", "3E")]
    secs = []
    for ch in range(53, 62):
        where, keys, note = P["place"][ch]
        secs.append((f"3.{ch}", f"Diodorus 3.{ch}; {P['ms_short']}, {where}", numbered_html(diodorus_greek("3", str(ch))),
                     numbered_html(oldfather(pages, 3, ch)), keys, note))
    return passage(
        slug="diodorus-3-53-61", title="Diodorus of Sicily, Library 3.53-61: the Amazons of Libya and the myths of the Atlantians",
        themes=["atlantis", "atlantians", "atlas", "amazons", "diodorus", "libya", "uranus", "greek"],
        description=("Diodorus on the Amazons of western Libya who conquered the Atlantians, and the Atlantians' own myths of Uranus, Atlas "
                     "and the birth of the gods (Library 3.53-61), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Vogel's Greek (Perseus) + Oldfather's English (Loeb 1935, LacusCurtius)",
        intro=["<p>In book 3 of his <em>Library of History</em> (c. 60-30 BCE) Diodorus retells, from the mythographer Dionysius Scytobrachion, "
               "the story of the Amazons of western Libya, who lived on the island of Hespera in the marsh Tritonis near Ocean, and under "
               "their queen Myrina conquered the Atlantians, 'the most civilized men among the inhabitants of those regions', who had a "
               "prosperous country and great cities (3.53-55). He then gives the Atlantians' account of the gods: their first king Uranus, his children the Titans, "
               "Basileia, Hyperion and Helios, and Atlas, who received the lands along the ocean, named his people Atlantians and the greatest mountain Atlas, and first taught the doctrine of the sphere; it ends with Cronus and Zeus (3.56-61). "
               "It is a Hellenistic myth of a western people named after Atlas, not Plato's sunken island.</p>",
               P["ms_intro"]],
        images=P["images"], sections=secs, ms=P["ms"], date_approx=f"c. 60-30 BCE (composition); {P['ms_date']}",
        translation_source="C. H. Oldfather, Diodorus of Sicily vol. II (Loeb, 1935), 3.53-61, transcription by Bill Thayer, LacusCurtius https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Diodorus_Siculus/3D*.html",
        translation_license=OLDFATHER_LIC,
        notes=["One section per chapter; the small numbers are the sub-sections, which match in the Greek and the English.",
               "English from Bill Thayer's LacusCurtius transcription of Oldfather, note markers removed.",
               "Greek: Teubner text via Perseus, not a transcription of the manuscript."],
        **DIOD_COMMON)


def pausanias_10_5():
    P = PROSE["paus10"]
    secs = pausanias_sections("10", "5", ["7", "8", "9", "10"], P["place"], P["ms_short"])
    return passage(
        slug="pausanias-10-5-7-10", title="Pausanias, Description of Greece 10.5.7-10: the Delphic oracle founded by men from the Hyperboreans",
        themes=["hyperborea", "hyperboreans", "pausanias", "delphi", "apollo", "olen", "greek"],
        description=("Pausanias on Boeo's hymn, which said the oracle at Delphi was founded by Hyperboreans, Olen first among them, and on the "
                     "temple of wax and feathers sent by Apollo to the Hyperboreans (10.5.7-10), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Spiro's Greek (Perseus) + Jones's English (Loeb, Perseus)",
        intro=["<p>Pausanias wrote his <em>Description of Greece</em> in the 2nd century AD. In book 10, on Delphi, he reports that shepherds "
               "first came on the oracle, that Phemonoe was the first prophetess, and that Boeo, a local poetess, said in a hymn that the "
               "oracle was founded by men from the Hyperboreans, Pagasus and Agyieus, and that Olen, also a Hyperborean, was Apollo's first "
               "prophet and the first to sing in hexameters (10.5.7-8). Of the early temples, the second, of bees' wax and feathers, was said "
               "to have been sent by Apollo to the Hyperboreans (10.5.9); another story names as its builder a Delphian called Pteras (10.5.10).</p>",
               P["ms_intro"]],
        images=P["images"], sections=secs, ms=P["ms"], date_approx=f"c. 160-175 AD (composition); {P['ms_date']}", **PAUS_COMMON)


def pausanias_1_31_2():
    P = PROSE["paus1"]
    secs = pausanias_sections("1", "31", ["2"], P["place"], P["ms_short"])
    return passage(
        slug="pausanias-1-31-2", title="Pausanias, Description of Greece 1.31.2: the route of the Hyperborean first-fruits to Delos",
        themes=["hyperborea", "hyperboreans", "pausanias", "delos", "prasiae", "arimaspians", "greek"],
        description=("Pausanias on the first-fruits of the Hyperboreans, passed by the Arimaspi, Issedones and Scythians to Sinope and through "
                     "Greece to Prasiae in Attica, and taken by the Athenians to Delos (1.31.2), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Spiro's Greek (Perseus) + Jones's English (Loeb, Perseus)",
        intro=["<p>Describing the Attic deme of Prasiae, Pausanias reports that the first-fruits of the Hyperboreans are sent there: the "
               "Hyperboreans hand them to the Arimaspi, these to the Issedones, the Scythians bring them to Sinope, Greeks carry them on to "
               "Prasiae, and the Athenians take them to Delos, hidden in wheat straw. Herodotus (4.33) and Callimachus (Hymn 4) give other "
               "routes.</p>", P["ms_intro"]],
        images=P["images"], sections=secs, ms=P["ms"], date_approx=f"c. 160-175 AD (composition); {P['ms_date']}", **PAUS_COMMON)


def aelian_vh_3_18():
    """For the atlantis collection."""
    P = PROSE["aelian"]
    g = cts_text(perseus("tlg0545.tlg002.perseus-grc2"), "3", "18", levels=("book", "chapter"))
    e = stanley_chapter(SRC_ATL / "penelope-aelian-varhist3.html", "XVIII")
    e = e[e.index("Theopompus relates"):]        # drop Stanley's chapter heading
    where, keys, note = P["place"]["3.18"]
    return passage(
        slug="aelian-varia-historia-3-18", title="Aelian, Varia Historia 3.18: Theopompus' tale of Midas and Silenus, the continent beyond Ocean and Meropis",
        themes=["atlantis", "meropis", "theopompus", "aelian", "silenus", "hyperboreans", "greek"],
        description=("Aelian's summary of Theopompus' story told by Silenus to Midas: a vast continent beyond the Ocean, the cities Eusebes and "
                     "Machimos, an invasion that turned back at the Hyperboreans, and the Meropes (Varia Historia 3.18), on " + P["ms_short"] + "."),
        source=f"{P['ms_short']} via {P['library']} + Hercher's Greek (Perseus) + Thomas Stanley's English (1665)",
        intro=["<p>Claudius Aelianus (c. 175-235 AD) collected curiosities in his <em>Varia Historia</em>. At 3.18 he summarizes a story from "
               "the 4th-century BCE historian Theopompus of Chios: Silenus told King Midas that Europe, Asia and Libya are islands in the "
               "Ocean, and that beyond it lies the only true continent, of boundless size, with two great cities, Eusebes (the Pious) and "
               "Machimos (the Warlike). The warriors of Machimos once crossed the Ocean with ten million men, but when they reached the "
               "Hyperboreans and learned that these were thought the happiest people here, they despised us and went home. Further off live "
               "the Meropes, at the edge of whose land is a place of no return. Aelian calls Theopompus a teller of fables. The story is "
               "often read as a parody of Plato's Atlantis.</p>", P["ms_intro"]],
        images=P["images"],
        sections=[("3.18", f"Aelian, Varia Historia 3.18; {P['ms_short']}, {where}", para_html(g), esc_p(e), keys, note)],
        ms=P["ms"], author_id="aelian", era="Imperial", tradition="greek", category="historical-witness", lang_name="Greek",
        language="Greek (Hercher 1866) / English (Thomas Stanley 1665)", century=3,
        date_approx=f"early 3rd century AD (composition); {P['ms_date']}",
        original_source="R. Hercher, Claudii Aeliani Varia historia (Teubner, 1866), Perseus canonical-greekLit tlg0545.tlg002.perseus-grc2",
        original_license=PERSEUS_LIC,
        translation_source="Thomas Stanley, Claudius Aelianus his Various history (London, 1665), book 3 chapter 18, transcription at https://penelope.uchicago.edu/aelian/varhist3.xhtml",
        translation_license="public domain (1665)", translator="Thomas Stanley (1665)",
        notes=["Stanley's English keeps his 1665 spelling ('farre', 'Voiage'); his chapter heading is omitted.",
               "Theopompus (4th c. BCE) is known here only through Aelian; Aelian himself wrote after 200 AD, but the passage reports a 4th-century BCE text."])


POETRY["hh7"] = {
    "ms_short": "Leiden, UB, BPG 33 H (M), fol.",
    "library": "Leiden University Libraries (IIIF)",
    "ms_date": "first half of the 15th century (Leiden BPG 33 H)",
    "images": {
        "49r": {"file": "leiden-bpg33h-f49r.jpg", "service": "https://eu-img02.ext.exlibrisgroup.com/iiif/2/eyJyZWdpb24iOiJldS1jZW50cmFsLTEiLCJidWNrZXQiOiJldS1zdDAxLmV4dC5leGxpYnJpc2dyb3VwLmNvbSIsImtleSI6IjMxVUtCX0xFVS9zdG9yYWdlL2FsbWEvNjAvOTMvMEQvOTEvNjIvN0MvQTgvMzIvOUUvNzMvRjcvODUvMEUvRjcvN0QvQ0EvMTg4N18xX2l0ZW1fMTYxNTIwN18wOTkuanAyIiwicmVwX2lkIjoiMTI1MjM2Njg4NzAwMDI3MTEiLCJpbnN0YW5jZSI6ImV1IiwiaW5zdGl0dXRpb24iOiIzMVVLQl9MRVUiLCJ3aWR0aCI6IjI5MjEiLCJoZWlnaHQiOiIzODczIiwid21LZXkiOm51bGwsIndtV2lkdGgiOm51bGwsIndtSGVpZ2h0IjpudWxsLCJ3bVBvc2l0aW9uIjpudWxsLCJ3bVJlcGVhdCI6ZmFsc2UsIm5hOTEiOm51bGx9", "caption": "Leiden BPG 33 H fol. 49r"},
        "49v": {"file": "leiden-bpg33h-f49v.jpg", "service": "https://eu-img02.ext.exlibrisgroup.com/iiif/2/eyJyZWdpb24iOiJldS1jZW50cmFsLTEiLCJidWNrZXQiOiJldS1zdDAxLmV4dC5leGxpYnJpc2dyb3VwLmNvbSIsImtleSI6IjMxVUtCX0xFVS9zdG9yYWdlL2FsbWEvNjAvOTMvMEQvOTEvNjIvN0MvQTgvMzIvOUUvNzMvRjcvODUvMEUvRjcvN0QvQ0EvMTg4N18xX2l0ZW1fMTYxNTIwN18xMDAuanAyIiwicmVwX2lkIjoiMTI1MjM2Njg4NzAwMDI3MTEiLCJpbnN0YW5jZSI6ImV1IiwiaW5zdGl0dXRpb24iOiIzMVVLQl9MRVUiLCJ3aWR0aCI6IjMwOTQiLCJoZWlnaHQiOiIzODczIiwid21LZXkiOm51bGwsIndtV2lkdGgiOm51bGwsIndtSGVpZ2h0IjpudWxsLCJ3bVBvc2l0aW9uIjpudWxsLCJ3bVJlcGVhdCI6ZmFsc2UsIm5hOTEiOm51bGx9", "caption": "Leiden BPG 33 H fol. 49v"},
    },
    "pages": [("49r", 1, 38), ("49v", 39, 59)],
    "page_notes": {
        "49r": ("the hymn begins at col. 1 line 15, \u2039\u1f00\u03bc\u03c6\u1f76 \u0394\u03b9\u03ce\u03bd\u03c5\u03c3\u03bf\u03bd \u03c3\u03b5\u03bc\u03ad\u03bb\u03b7\u03c2 \u1f10\u03c1\u03b9\u03ba\u03c5\u03b4\u03ad\u03bf\u03c2 \u03c5\u1f31\u03cc\u03bd\u203a, under the red title "
                "\u2039\u03c4\u03bf\u1fe6 \u03b1\u1f50\u03c4\u03bf\u1fe6 \u03b5\u1f30\u03c2 \u0394\u03b9\u03cc\u03bd\u03c5\u03c3\u03bf\u03bd\u203a (line 14); col. 1 ends at line 26 with v. 12; col. 2 carries vv. 13-38, from \u2039\u03c4\u1f78\u03bd \u03b4' \u03bf\u1f50\u03ba \u1f34\u03c3\u03c7\u03b1\u03bd\u03b5 \u03b4\u03b5\u03c3\u03bc\u03ac\u203a; "
                "the Hyperboreans are col. 2 lines 16-17, \u2039\u1f14\u03bb\u03c0\u03bf\u03bc\u03b1\u03b9, \u1f22 \u03b1\u1f34\u03b3\u03c5\u03c0\u03c4\u03bf\u03bd\u203a and \u2039\u1f22 \u1f10\u03c2 \u1f51\u03c0\u03b5\u03c1\u03b2\u03bf\u03c1\u03ad\u03bf\u03c5\u03c2\u203a (vv. 28-29); the scribe numbers every fifth line in the margin"),
        "49v": ("col. 1 begins with v. 39, \u2039\u1f04\u03bc\u03c0\u03b5\u03bb\u03bf\u03c2 \u1f14\u03bd\u03b8\u03b1 \u03ba\u03b1\u1f76 \u1f14\u03bd\u03b8\u03b1\u203a, and the hymn ends at line 21 with v. 59, \u2039\u03c3\u03b5\u1fd6\u03bf \u03b3\u03b5 \u03bb\u03b7\u03b8\u03cc\u03bc\u03b5\u03bd\u03bf\u03bd "
                "\u03b3\u03bb\u03c5\u03ba\u03b5\u03c1\u1f74\u03bd \u03ba\u03bf\u03c3\u03bc\u1fc6\u03c3\u03b1\u03b9 \u1f00\u03bf\u03b9\u03b4\u03ae\u03bd\u203a; line 22 is the faded red title of the hymn to Ares"),
    },
    "ms_intro": ("<p>The manuscript is Leiden, Universiteitsbibliotheek, BPG 33 H, the 'Moscow' manuscript of the Homeric Hymns (M), written "
                 "in the first half of the 15th century and found in Moscow in 1777; it is the only manuscript that preserves the Hymn to Demeter. "
                 "Hymn 7 fills fol. 49r and the first column of 49v, two columns of 26 lines to the page.</p>"),
    "ms": {
        "scan_source": "Leiden University Libraries, BPG 33 H, IIIF manifest https://digitalcollections.universiteitleiden.nl/iiif_manifest/item:1615207/manifest (fol. 49r canvas 99, 49v canvas 100)",
        "license": LEIDEN_LICENSE,
        "manuscript": "Leiden, Universiteitsbibliotheek, BPG 33 H (Homeric Hymns siglum M), Greece?, first half of the 15th century; Hymns on fol. 31r-50r",
        "mapping": "Own visual check: first and last lines of each column read on the images, cross-checked with the scribe's marginal line numbers (see scan_notes)",
        "urls": ["https://digitalcollections.universiteitleiden.nl/iiif_manifest/item:1615207/manifest"],
    },
}

POETRY["ar"] = {
    "ms_short": "Florence, Laur. Plut. 32.9 (L), fol. 249r-249v",
    "library": "Teca digitale BML",
    "ms_date": "10th century (Laur. Plut. 32.9)",
    "images": {
        "249r": {"file": "laur32-9-f249r.jpg", "service": BML_SVC + "711101", "caption": "Laur. Plut. 32.9 fol. 249r"},
        "249v": {"file": "laur32-9-f249v.jpg", "service": BML_SVC + "711102", "caption": "Laur. Plut. 32.9 fol. 249v"},
    },
    "pages": [("249r", 592, 597), ("249v", 598, 626)],
    "page_notes": {
        "249r": ("the page has one column of 39 lines, line 1 = 4.559 \u2039\u03b1\u1f30\u03b1\u03af\u03b7\u03c2 \u03b4' \u1f40\u03bb\u03bf\u1f78\u03bd \u03c4\u03b5\u03ba\u03bc\u03ae\u03c1\u03b1\u03c4\u03bf\u203a, so 4.592-597 are lines 34-39 "
                 "(line 34 = 592 \u2039\u1f30\u03ac\u03c7\u03b7\u03c3\u03b5\u03bd \u1f51\u03c0\u1f78 \u03ba\u03bd\u03ad\u03c6\u03b1\u03c2\u00b7 \u03bf\u1f31 \u03b4' \u1f00\u03bd\u03cc\u03c1\u03bf\u03c5\u03c3\u03b1\u03bd\u203a, marked with a stroke in the margin; line 36 = 594 \u2039\u03b5\u1f50\u03c7\u03cc\u03bc\u03b5\u03bd\u03bf\u03b9 \u03c4\u1f70 \u1f15\u03ba\u03b1\u03c3\u03c4\u03b1\u203a, line 39 = 597 \u2039\u1f14\u03bd\u03b8\u03b1 \u03c0\u03bf\u03c4' \u03b1\u1f30\u03b8\u03b1\u03bb\u03cc\u03b5\u03bd\u03c4\u03b9\u203a)"),
        "249v": ("line 1 = 598 \u2039\u1f21\u03bc\u03b9\u03b4\u03b1\u1f74\u03c2 \u03c6\u03b1\u03ad\u03b8\u03c9\u03bd \u03c0\u03ad\u03c3\u03b5\u03bd \u1f05\u03c1\u03bc\u03b1\u03c4\u03bf\u03c2 \u1f20\u03b5\u03bb\u03af\u03bf\u03b9\u03bf\u203a; line 14 = 611 \u2039\u03ba\u03b5\u03bb\u03c4\u03bf\u1f76 \u03b4'\u203a; line 17 = 614 "
                 "\u2039\u1f26\u03bc\u03bf\u03c2 \u1f51\u03c0\u03b5\u03c1\u03b2\u03bf\u03c1\u03ad\u03c9\u03bd \u1f31\u03b5\u03c1\u1f78\u03bd \u03b3\u03ad\u03bd\u03bf\u03c2\u203a; the passage ends at line 29 = 626 \u2039\u03bf\u1f37\u03bf\u03bd \u1f10\u03bb\u03b1\u03b9\u03b7\u03c1\u03b1\u1f76 \u03c3\u03c4\u03ac\u03b3\u03b5\u03c2 \u1f55\u03b4\u03b1\u03c3\u03b9\u03bd \u1f10\u03bc\u03c6\u03bf\u03c1\u03ad\u03bf\u03bd\u03c4\u03bf\u203a"),
    },
    "ms_intro": ("<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 32.9 (L), the famous 10th-century codex of Aeschylus, "
                 "Sophocles and Apollonius, the oldest manuscript of the <em>Argonautica</em>. One column of 39 lines a page; 4.592-626 run "
                 "from fol. 249r line 34 to fol. 249v line 29.</p>"),
    "ms": {
        "scan_source": "Biblioteca Medicea Laurenziana, Teca digitale (CONTENTdm), Plut. 32.9, IIIF manifest https://cdm21059.contentdm.oclc.org/iiif/2/plutei:711140/manifest.json (fol. 249r canvas 505, 249v canvas 506)",
        "license": BML_LICENSE,
        "manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 32.9 (Apollonius siglum L), parchment, 10th century (library dating 901-1000)",
        "mapping": "Own visual check: line numbers counted on the images from the first line of each page and checked at the Hyperborean lines (see scan_note)",
        "urls": ["http://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/711140", "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:711140/manifest.json"],
    },
}


LAUR3252_MS = {
    "scan_source": "Biblioteca Medicea Laurenziana, Teca digitale (CONTENTdm), Plut. 32.52, IIIF manifest https://cdm21059.contentdm.oclc.org/iiif/2/plutei:477619/manifest.json",
    "license": BML_LICENSE,
    "manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 32.52 (Pindar siglum D), 14th century (library dating 1301-1400); text block of cola in two columns surrounded by scholia",
    "mapping": "Own visual check: the verse rows at the top and foot of each page's text block read on the images and matched to the edition's lines (see scan_notes)",
    "urls": ["https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/477619", "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:477619/manifest.json"],
}
POETRY["o3"] = {
    "ms_short": "Florence, Laur. Plut. 32.52 (D), fol.",
    "library": "Teca digitale BML",
    "ms_date": "14th century (Laur. Plut. 32.52)",
    "images": {
        "6v": {"file": "laur32-52-f6v.jpg", "service": BML_SVC + "477352", "caption": "Laur. Plut. 32.52 fol. 6v"},
        "7r": {"file": "laur32-52-f7r.jpg", "service": BML_SVC + "477353", "caption": "Laur. Plut. 32.52 fol. 7r"},
        "7v": {"file": "laur32-52-f7v.jpg", "service": BML_SVC + "477354", "caption": "Laur. Plut. 32.52 fol. 7v"},
    },
    "pages": [("6v", 1, 14), ("7r", 15, 29), ("7v", 29, 45)],
    "page_notes": {
        "6v": ("the ode begins in the upper text block, written in rows of cola across two columns: row 1 ‹Τυνδαρίδαις τε φιλοξείνοις ἁδεῖν | "
               "καλλιπλοκάμῳ θ' ἑλένᾳ› (v. 1); the last row on the page ends ‹ἀμφιτρυωνιάδας› (v. 14)"),
        "7r": ("row 1 ‹μνᾶμα τῶν οὐλυμπίᾳ κάλλιστον ἀέθλων | δᾶμον ὑπερβορέων πείσαις ἀπόλ-› (vv. 15-16); "
               "the last row is ‹εὐρυσθέος ἔντυ' ἀνάγκα πατρόθεν | χρυσόκερων ἔλαφον θήλειαν ἄξονθ'› (vv. 28-29)"),
        "7v": ("row 1 ‹ἅν ποτε ταϊγέτα | ἀντιθεῖσ' ὀρθωσίᾳ ἔγραψεν ἱράν› (vv. 29-30); the ode ends on the last row, "
               "‹κἀσόφοις· οὔ νιν διώξω· | κεινὸς εἴην› (v. 45), followed by an end mark"),
    },
    "ms_intro": ("<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 32.52 (Pindar D), 14th century, with the odes "
                 "written in a central block of short cola, two to a row, surrounded by scholia. Olympian 3 runs over fol. 6v, 7r and 7v. "
                 "The two oldest Pindar manuscripts were also checked: Vat. gr. 1312 (B, 12th c.) is legible here only in parts, and the "
                 "Ambrosian manuscript C 222 inf. (A) is published with a no-download restriction, so neither is used for this ode.</p>"),
    "ms": LAUR3252_MS,
}
POETRY["p10"] = {
    "ms_short": "Vatican, Vat. gr. 1312 (B), fol.",
    "library": "DigiVatLib",
    "ms_date": "12th century (Vat. gr. 1312)",
    "images": {
        "164v": {"file": "vatgr1312-f164v.jpg", "service": "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.1312.pt.2/Vat.gr.1312.pt.2_0076_fa_0164v.jp2", "caption": "Vat. gr. 1312 fol. 164v"},
        "165r": {"file": "vatgr1312-f165r.jpg", "service": "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.1312.pt.2/Vat.gr.1312.pt.2_0077_fa_0165r.jp2", "caption": "Vat. gr. 1312 fol. 165r"},
        "165v": {"file": "vatgr1312-f165v.jpg", "service": "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.1312.pt.2/Vat.gr.1312.pt.2_0078_fa_0165v.jp2", "caption": "Vat. gr. 1312 fol. 165v"},
    },
    "pages": [("164v", 25, 26), ("165r", 26, 33), ("165v", 34, 44)],
    "page_notes": {
        "164v": ("the last two rows of the right-hand text column read ‹καὶ ζώων ἔτι νεαρὸν› (v. 25) and ‹κατ' αἶσαν υἱὸν ἴδῃ τυχόντα› (v. 26)"),
        "165r": ("the page begins ‹στεφάνων πυθίων› (end of v. 26), then ‹ὁ χάλκεος οὐρανὸς οὔ ποτ' ἀμβατὸς αὐτῷ› (27); the Hyperborean passage opens with "
                 "‹πλόον· ναυσὶ δ' οὔτε πεζὸς ἰών κεν εὕροις› (29) and ‹ἐς ὑπερβορέων ἀγῶνα | θαυματὰν ὁδόν› (30); after a block of scholia "
                 "‹παρ' οἷς ποτε περσεὺς ἐδαίσατο λαγέτας› (31-32) and ‹κλειτὰς ὄνων ἑκατόμβας | ἐπιτόσσαις θεῷ› (33) end the page"),
        "165v": ("the right-hand column begins ‹ῥέζοντας· ὧν θαλίαις ἔμπεδον› (34), with ‹χαίρει, γελᾷ θ' ὁρῶν ὕβριν | ὀρθίαν κνωδάλων› (36), and ends "
                 "‹ὑπέρδικον νέμεσιν· θρασείᾳ | δὲ πνέων καρδίᾳ› (44)"),
    },
    "ms_intro": ("<p>The manuscript is Vatican, Biblioteca Apostolica Vaticana, Vat. gr. 1312 (Pindar B), 12th century, the oldest manuscript "
                 "of the Pythians. Its leaves are darkened and stained, and in the published images only some of the pages of this ode can be "
                 "read with confidence. This entry therefore gives the part of the ode that could be placed line by line, 25-44, which holds "
                 "the whole description of the Hyperboreans, on fol. 164v (last rows), 165r and 165v. The rest of the ode (1-24 and 45-72) is "
                 "not included.</p>"),
    "ms": {
        "scan_source": "Biblioteca Apostolica Vaticana, DigiVatLib IIIF, Vat. gr. 1312 pt. 2 (https://digi.vatlib.it/iiif/MSS_Vat.gr.1312.pt.2/manifest.json), fol. 164v-165v",
        "license": BAV_LICENSE,
        "manuscript": "Vatican City, BAV, Vat. gr. 1312 (Pindar siglum B), 12th century; the Pythians on fol. 95v-174v (Pinakes)",
        "mapping": "Own visual check on contrast-enhanced images: the rows of verse at the head and foot of each page read and matched to the edition's lines (see scan_notes)",
        "urls": ["https://digi.vatlib.it/view/MSS_Vat.gr.1312.pt.2/0076", "https://digi.vatlib.it/view/MSS_Vat.gr.1312.pt.2/0077", "https://digi.vatlib.it/view/MSS_Vat.gr.1312.pt.2/0078"],
    },
}
GR2763 = "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b10722967x/f"
POETRY["call"] = {
    "ms_short": "Paris, BnF, grec 2763, fol. 79v-80v",
    "library": "Gallica (BnF)",
    "ms_date": "1470-1500 (Paris gr. 2763)",
    "images": {
        "79v": {"file": "bnf-gr2763-f79v.jpg", "service": GR2763 + "87", "region": "pct:0,0,50,100", "caption": "Paris gr. 2763 fol. 79v"},
        "80r": {"file": "bnf-gr2763-f80r.jpg", "service": GR2763 + "87", "region": "pct:50,0,50,100", "caption": "Paris gr. 2763 fol. 80r"},
        "80v": {"file": "bnf-gr2763-f80v.jpg", "service": GR2763 + "88", "region": "pct:0,0,50,100", "caption": "Paris gr. 2763 fol. 80v"},
    },
    "pages": [("79v", 275, 277), ("80r", 278, 297), ("80v", 298, 299)],
    "page_notes": {
        "79v": "the last three lines of the page are 275-277, ‹τῷ καὶ νήσων ἁγιωτάτη ἐξέτι κείνου› to ‹οὐδ' ἀΐδης, οὐδ' ἵπποι ἐπιστείβουσιν ἄρηος›",
        "80r": ("the page begins with 278, ‹ἀλλά τοι ἀμφιετεῖς δεκατηφόροι αἰὲν ἀπαρχαί›; line 4 is 281 ‹κλήρους ἐστήσαντο, καὶ οἳ καθύπερθε "
                "βορείης›; the last line is 297, ‹ἤθεα κουράων μορμύσσεται, ἥλικα χαίτην›"),
        "80v": "the first two lines are 298-299, ‹παρθενικαῖς, παῖδες δὲ θέρος› and ‹ἄρσενες ἠιθέοισιν ἀπαρχόμενοι φορέουσιν›, followed by 300 ‹Ἀστερίη θυόεσσα›",
    },
    "ms_intro": ("<p>The manuscripts of Callimachus' hymns are all of the 15th century or later. The one shown is Paris, BnF, grec 2763, "
                 "copied about 1470-1500 by Niccolò Leonico Tomeo, with the hymns on fol. 61r-88v (images from the BnF's microfilm, each a "
                 "two-page opening, cropped here to the page). Lines 275-299 run from the foot of fol. 79v over 80r to the top of 80v. "
                 "The Ambrosian manuscript B 98 sup. was also checked but is published with a no-download restriction.</p>"),
    "ms": {
        "scan_source": "Bibliothèque nationale de France, Gallica https://gallica.bnf.fr/ark:/12148/btv1b10722967x (IIIF via openapi.bnf.fr; microfilm images, image 87 = fol. 79v-80r, image 88 = fol. 80v-81r)",
        "license": BNF_LICENSE,
        "manuscript": "Paris, BnF, grec 2763, paper, 1470-1500, copied by Niccolò Leonico Tomeo (BnF catalogue); Callimachus' hymns with scholia on fol. 61r-88v",
        "mapping": "Own visual check: the lines at the foot of 79v, the whole of 80r and the head of 80v read on the images and matched to the edition's line numbers (see scan_note)",
        "urls": ["https://gallica.bnf.fr/ark:/12148/btv1b10722967x"],
    },
}


def pindar_o3():
    return pindar_passage(
        "o3", "O.", 3, "tlg0033.tlg001.perseus-grc2", "tlg0033.tlg001.perseus-eng2", "pindar-olympian-3",
        "Pindar, Olympian 3: Heracles brings the olive from the land of the Hyperboreans",
        "Pindar's third Olympian ode (476 BCE), in which Heracles fetches the wild olive for Olympia from the Hyperboreans who serve Apollo, on the manuscript Laur. Plut. 32.52, fol. 6v-7v.",
        ["<p>Pindar wrote his third Olympian ode for Theron of Acragas, victor in the chariot race at Olympia in 476 BCE, for a feast of "
         "the Dioscuri. Its myth tells how the olive came to Olympia: Heracles, having founded the games, found the place bare of trees, "
         "and remembering the land beyond the cold north wind that he had seen while hunting the golden-horned hind, persuaded the "
         "Hyperboreans, Apollo's servants, to give him a shoot of the wild olive from the shady springs of the Ister, to shade the "
         "sanctuary and crown the victors (lines 11-34).</p>"],
        ["hyperborea", "hyperboreans", "pindar", "olympia", "heracles", "olive", "greek", "poetry"],
        "476 BCE (composition); 14th century (Laur. Plut. 32.52)")


def pindar_p10():
    return pindar_passage(
        "p10", "P.", 10, "tlg0033.tlg002.perseus-grc2", "tlg0033.tlg002.perseus-eng3", "pindar-pythian-10-25-44",
        "Pindar, Pythian 10.25-44: no road by ship or on foot to the Hyperboreans",
        "The Hyperborean passage of Pindar's tenth Pythian ode (498 BCE): Perseus feasting with them, their music, and their life without sickness, age or toil (lines 25-44), on the 12th-century manuscript Vat. gr. 1312, fol. 164v-165v.",
        ["<p>Pindar's tenth Pythian ode, his earliest datable poem, was written in 498 BCE for Hippocleas of Thessaly, winner of the boys' "
         "double foot race at Delphi. After praising the man who sees his son crowned, Pindar reaches the limit of mortal fortune: no one "
         "can find the marvellous road to the Hyperboreans, by ship or on foot. Perseus once feasted among them as they sacrificed "
         "hecatombs of asses to Apollo, who delights in their festivals; the Muse is never absent from their dances; crowned with golden "
         "laurel they feast, and neither disease nor old age touches that holy race, which lives without toil or battle, beyond the reach "
         "of Nemesis.</p>"],
        ["hyperborea", "hyperboreans", "pindar", "perseus", "apollo", "greek", "poetry"],
        "498 BCE (composition); 12th century (Vat. gr. 1312)", first=25, last=44)


VAT130 = "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.130/Vat.gr.130_{:04d}.jp2"


def vat130_img(canvas, side, folio):
    return {"file": f"vatgr130-f{folio}.jpg", "service": VAT130.format(canvas),
            "region": "pct:0,0,50,100" if side == "L" else "pct:50,0,50,100", "width": 1184,
            "caption": f"Vat. gr. 130 fol. {folio}"}


VAT130_MS = {
    "scan_source": "Biblioteca Apostolica Vaticana, DigiVatLib IIIF, Vat. gr. 130 (https://digi.vatlib.it/iiif/MSS_Vat.gr.130/manifest.json); each image is a two-page opening (image N = fol. (N-4)v and (N-3)r, folio numbers read on the pages at 167r and 169r-174r), cropped here to the page",
    "license": BAV_LICENSE,
    "manuscript": "Vatican City, BAV, Vat. gr. 130 (Diodorus books 1-5, siglum C), parchment, 10th century, copied by the priest Ioannes (Pinakes diktyon 66761)",
    "mapping": "Own visual check: the first words of every numbered section and every page break read on the images, with line numbers counted on each 28-line page (see scan_notes)",
    "urls": ["https://digi.vatlib.it/view/MSS_Vat.gr.130", "https://pinakes.irht.cnrs.fr/notices/cote/getPdf/66761"],
}
VAT130_INTRO = ("<p>The manuscript is Vatican, Biblioteca Apostolica Vaticana, Vat. gr. 130, a 10th-century copy of books 1-5 of the "
                "<em>Library</em> made by the priest Ioannes (siglum C), the oldest manuscript of these books with published images "
                "(the early 10th-century Naples manuscript has none online). The Vatican Library's images are black-and-white "
                "(made from microfilm), each showing an opening of two pages; they are cropped here to the single page. Each page has 28 lines.</p>")

PROSE["diod2"] = {
    "ms_short": "Vat. gr. 130", "library": "DigiVatLib", "ms_date": "10th century (Vat. gr. 130)",
    "ms_intro": VAT130_INTRO.replace("</p>", " 2.47 runs from fol. 114v line 20 to fol. 115v line 15.</p>"),
    "images": {"114v": vat130_img(118, "L", "114v"), "115r": vat130_img(118, "R", "115r"), "115v": vat130_img(119, "L", "115v")},
    "ms": VAT130_MS,
    "place": {
        "2.47.1": ("fol. 114v line 20 to fol. 115r line 5", ["114v", "115r"],
                   "2.47.1 begins at fol. 114v line 20, ‹ἀρχαιολογίας. ἡμεῖς δ' ἐπεὶ τὰ πρὸς ἄρκτους› (the page begins in 2.46); fol. 115r begins ‹δ' ὑπὸ τῶν ὀνομαζομένων ὑπερβορέων›; the section ends in line 5. Read on the DigiVatLib images (image 118)."),
        "2.47.2": ("fol. 115r lines 5-13", ["115r"], "2.47.2 begins in fol. 115r line 5, ‹μυθολογοῦσι δ' ἐν αὐτῇ›, and ends in line 13 with ‹σφαιροειδῆ τῷ σχήματι› (the round temple). Read on the DigiVatLib image 118."),
        "2.47.3": ("fol. 115r lines 13-18", ["115r"], "2.47.3 begins in fol. 115r line 13, ‹καὶ πόλιν›, and ends in line 18. Read on the DigiVatLib image 118."),
        "2.47.4": ("fol. 115r lines 18-26", ["115r"], "2.47.4 begins in fol. 115r line 18, ‹ἔχειν δὲ τοὺς ὑπερβο-›, and ends in line 26. Read on the DigiVatLib image 118."),
        "2.47.5": ("fol. 115r line 26 to fol. 115v line 4", ["115r", "115v"], "2.47.5 begins in fol. 115r line 26, ‹ὡσαύτως δὲ καὶ ἐκ τῶν ὑπερβο-›; fol. 115v begins ‹καὶ συγγένειαν. φασὶ δὲ καὶ τὴν σελήνην›; the section ends in line 4. Read on the DigiVatLib images 118-119."),
        "2.47.6-7": ("fol. 115v lines 4-15", ["115v"], "2.47.6 begins at fol. 115v line 4, ‹λέγεται δὲ καὶ τὸν θεὸν δι' ἐτῶν ιθ'› (the nineteen years written as a numeral), 2.47.7 in line 8, ‹κατὰ δὲ τὴν ἐπιφάνειαν›, and the chapter ends in line 15, ‹διαδέχεσθαι τὰς ἀρχάς›, followed by 2.48. Read on the DigiVatLib image 119."),
    },
}

_D3 = [(169, "165v", "166r"), (170, "166v", "167r"), (171, "167v", "168r"), (172, "168v", "169r"), (173, "169v", "170r"),
       (174, "170v", "171r"), (175, "171v", "172r"), (176, "172v", "173r"), (177, "173v", "174r")]
_D3_IMAGES = {}
for _c, _l, _r in _D3:
    _D3_IMAGES[_l] = vat130_img(_c, "L", _l)
    _D3_IMAGES[_r] = vat130_img(_c, "R", _r)
PROSE["diod3"] = {
    "ms_short": "Vat. gr. 130", "library": "DigiVatLib", "ms_date": "10th century (Vat. gr. 130)",
    "ms_intro": VAT130_INTRO.replace("</p>", " 3.53-61 run from fol. 165v line 11 to fol. 174r line 18; on fol. 170r the lower half (from about line 16) is in a different hand.</p>"),
    "images": _D3_IMAGES, "ms": VAT130_MS,
    "place": {
        53: ("fol. 165v line 11 to fol. 166v line 10", ["165v", "166r", "166v"],
             "3.53 begins at the end of fol. 165v line 11 with ‹φασὶ› (line 12 ‹ὑπάρξαι τῆς λιβύης›); 3.53.2 begins in 165v line 22, 3.53.3 at fol. 166r line 1 (‹κατὰ δὲ τὰς γενέσεις›), 3.53.4 in line 10 (‹μυθολογοῦσι δ' αὐτὰς ᾠκηκέναι νῆσον›), 3.53.5 at the end of line 19, 3.53.6 in line 27; fol. 166v begins ‹τὰς ἐν τῇ νήσῳ πόλεις καταστρέψασθαι› and the chapter ends in line 10."),
        54: ("fol. 166v line 10 to fol. 167v line 7", ["166v", "167r", "167v"],
             "3.54 begins in fol. 166v line 10, ‹χερρόνησον. ἐκ δὲ ταύτης ὁρμωμένας›; 3.54.2 at the end of line 19, 3.54.3 in line 24; fol. 167r (folio number read) has 3.54.4 in line 1, 3.54.5 in line 9 (‹τῆς δὲ περὶ τοὺς κερναίους συμφορᾶς›), 3.54.6 in line 17, 3.54.7 at the end of line 21; fol. 167v begins ‹τῶν ἀμφιταχθεισῶν παμπληθεῖς› and the chapter ends in line 7."),
        55: ("fol. 167v line 7 to fol. 169r line 4", ["167v", "168r", "168v", "169r"],
             "3.55 begins at fol. 167v line 7, ‹τῶν δὲ ἀμαζόνων νυκτὸς›; 3.55.2 in line 13, 3.55.3 in line 16; fol. 168r: 3.55.4 line 1, 3.55.5 line 11, 3.55.6 line 16, 3.55.7 end of line 21, 3.55.8 line 26; fol. 168v begins ‹τῆς σωτηρίας. προσενεχθῆναι νήσῳ›, 3.55.9 at the end of line 9, 3.55.10 at the end of line 17, 3.55.11 in line 24; the chapter ends at fol. 169r line 4, ‹τὸ πέρας›."),
        56: ("fol. 169r line 4 to fol. 169v line 15", ["169r", "169v"],
             "3.56 begins in fol. 169r line 4 (folio number read), ‹ἡμεῖς δ' ἐπεὶ περὶ τῶν ἀτλαντίων›; 3.56.2 in line 8, ‹οἱ τοίνυν ἀτλάντιοι›; 3.56.3 in line 17, 3.56.4 in line 25; fol. 169v begins ‹κινήσεως. τοὺς δὲ μῆνας›, 3.56.5 in line 2, and the chapter ends in line 15."),
        57: ("fol. 169v line 15 to fol. 170v line 22", ["169v", "170r", "170v"],
             "3.57 begins in fol. 169v line 15, ‹οὐρανοῦ δὲ μυθολογοῦσι›; 3.57.2 in line 20, 3.57.3 in line 27; fol. 170r (folio number read) begins ‹διαφέρουσαν›, 3.57.4 in line 10, 3.57.5 at the end of line 15 (the rest of the page is in a different hand); fol. 170v: 3.57.6 line 2, 3.57.7 line 6, 3.57.8 line 11, and the chapter ends in line 22."),
        58: ("fol. 170v line 22 to fol. 171r line 28", ["170v", "171r"],
             "3.58 begins at the end of fol. 170v line 22, ‹παρα-|δέδοται δὲ τῆς θεοῦ›; fol. 171r (folio number read): 3.58.2 line 3, 3.58.3 line 12 (‹διὸ καὶ τῶν βρεφῶν›), 3.58.4 line 23; the chapter ends with the last line, 28."),
        59: ("fol. 171v line 1 to fol. 172v line 15", ["171v", "172r", "172v"],
             "3.59 begins at the top of fol. 171v, ‹διόπερ ἀναχθείσης αὐτῆς›; 3.59.2 line 12, 3.59.3 line 23; fol. 172r (folio number read): 3.59.4 line 6, 3.59.5 line 11, 3.59.6 line 18, 3.59.7 line 24; fol. 172v: 3.59.8 line 5, and the chapter ends in line 15."),
        60: ("fol. 172v line 15 to fol. 173v line 1", ["172v", "173r", "173v"],
             "3.60 begins in fol. 172v line 15, ‹μετὰ δὲ τὴν ὑπερίονος›; 3.60.2 line 22 (‹φασὶ δ' αὐτὸν τὰ περὶ τὴν ἀστρολογίαν›); fol. 173r (folio number read): 3.60.3 line 2 (‹τοῦτον δ' ἐπὶ τὴν κορυφὴν›), 3.60.4 line 8, 3.60.5 line 21; the chapter ends in fol. 173v line 1, ‹γυναῖκας νύμφας προσαγορεύειν›."),
        61: ("fol. 173v line 1 to fol. 174r line 18", ["173v", "174r"],
             "3.61 begins in fol. 173v line 1, ‹κρόνον δὲ μυ-›; 3.61.2 line 7, 3.61.3 line 14, 3.61.4 line 24; fol. 174r (folio number read): 3.61.5 line 6, 3.61.6 line 11, and the chapter ends in line 18, ‹τὰ κεφάλαια. ταῦτ' ἐστίν›, followed by 3.62 ‹ἡμεῖς δ' ἐπεὶ προειρήκα-›."),
    },
}

GR1410 = "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b10721707b/f"
GR1410_MS = {
    "scan_source": "Bibliothèque nationale de France, Gallica https://gallica.bnf.fr/ark:/12148/btv1b10721707b (IIIF via openapi.bnf.fr; microfilm images, each a two-page opening, cropped to the page)",
    "license": BNF_LICENSE,
    "manuscript": "Paris, BnF, grec 1410 (Pausanias siglum Pa), paper, 307 fol., copied in 1491 by Michael Souliardos (BnF catalogue; Pinakes 51026)",
    "mapping": "Own visual check: section starts and ends read on the images with line numbers counted on each 30-line page (see scan_notes)",
    "urls": ["https://gallica.bnf.fr/ark:/12148/btv1b10721707b", "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc21505j"],
}
GR1410_INTRO = ("<p>All manuscripts of Pausanias are late, of the 15th century. The one shown is Paris, BnF, grec 1410, copied in 1491 by "
                "Michael Souliardos (siglum Pa); the older Venice manuscript (Marc. gr. 413) has no published images. The BnF's images are "
                "made from microfilm, each showing an opening of two pages, cropped here to the page; each page has 30 lines.")
PROSE["paus10"] = {
    "ms_short": "Paris gr. 1410", "library": "Gallica (BnF)", "ms_date": "1491 (Paris gr. 1410)",
    "ms_intro": GR1410_INTRO + " 10.5.7-10 run from fol. 275r line 29 to fol. 275v line 22.</p>",
    "images": {"275r": {"file": "bnf-gr1410-f275r.jpg", "service": GR1410 + "284", "region": "pct:50,0,50,100", "caption": "Paris gr. 1410 fol. 275r"},
               "275v": {"file": "bnf-gr1410-f275v.jpg", "service": GR1410 + "285", "region": "pct:0,0,50,100", "caption": "Paris gr. 1410 fol. 275v"}},
    "ms": GR1410_MS,
    "place": {
        "7": ("fol. 275r line 29 to fol. 275v line 6", ["275r", "275v"],
              "10.5.7 begins in fol. 275r line 29 (folio number read), ‹ἤκουσα δὲ καὶ ὡς ἄνδρες›, line 30 ‹ποιμαίνοντες ἐπιτύχοιεν τῷ μαντείῳ›; fol. 275v begins ‹καὶ ἐμαντεύσαντο ἐξ ἀπόλλωνος›; the section ends in line 6. Read on the BnF images (verse lines in faint red ink counted by hand)."),
        "8": ("fol. 275v lines 6-11", ["275v"],
              "10.5.8 begins in fol. 275v line 6, ‹πεποίηκε δὲ ἡ βοιὼ τοιάδε· ἔνθα τοι εὔμνη-›; Boeo's verses and the naming of Olen (‹ὠλήν θ' ὃς γένετο›, line 9) follow; the section ends in line 11. Read on the BnF image."),
        "9": ("fol. 275v lines 11-16", ["275v"],
              "10.5.9 begins in fol. 275v line 11, ‹ποιηθῆναι δὲ τὸν ναὸν›, and ends in line 16 with ‹ὑπὸ τοῦ ἀπόλλωνος› (the wax temple sent to the Hyperboreans). Read on the BnF image."),
        "10": ("fol. 275v lines 16-22", ["275v"],
               "10.5.10 begins in fol. 275v line 16, ‹λέγεται δὲ καὶ ἕ-›, and ends in line 22, ‹διεπλέξαντο ναόν· οὐδὲ ἀρχὴν προσίεμαι τὸν λόγον›, followed by 10.5.11. Read on the BnF image."),
    },
}
PROSE["paus1"] = {
    "ms_short": "Paris gr. 1410", "library": "Gallica (BnF)", "ms_date": "1491 (Paris gr. 1410)",
    "ms_intro": GR1410_INTRO + " 1.31.2 stands at the foot of fol. 26v (the folio number is taken from the neighbouring openings: the next opening's recto reads 28).</p>",
    "images": {"26v": {"file": "bnf-gr1410-f26v.jpg", "service": GR1410 + "34", "region": "pct:0,0,50,100", "caption": "Paris gr. 1410 fol. 26v"}},
    "ms": GR1410_MS,
    "place": {
        "2": ("fol. 26v lines 23-30", ["26v"],
              "1.31.2 begins in fol. 26v line 23, ‹ἐν δὲ πρασιεῦσιν ἀπόλλωνός ἐστι ναός›, and ends with the last line of the page (30); the facing fol. 27r begins with 1.31.3, "
              "‹κραναὸν δὲ τὸν βασιλεύσαντα ἀθηναίων›. Lines 21-30 were checked by eye; the count from the top of the page is by line detection. Read on the BnF image (image 34)."),
    },
}

SUPPL352 = "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b11000151s/f"
PROSE["aelian"] = {
    "ms_short": "Paris suppl. gr. 352", "library": "Gallica (BnF)", "ms_date": "13th century (Paris suppl. gr. 352)",
    "ms_intro": ("<p>The manuscript is Paris, BnF, Supplément grec 352, a 13th-century bombycin codex with the <em>Varia Historia</em> on fol. "
                 "106v-132, the oldest complete witness of the work with published images (the 12th-century Vat. gr. 96 has only excerpts). "
                 "The scribe gives each story a title between crosses. 3.18 runs from fol. 113r line 30 to fol. 113v line 18; inside it the "
                 "scribe adds subtitles for the city Machimos and for the place called Anostos.</p>"),
    "images": {"113r": {"file": "bnf-suppl-gr352-f113r.jpg", "service": SUPPL352 + "230", "caption": "Paris suppl. gr. 352 fol. 113r"},
               "113v": {"file": "bnf-suppl-gr352-f113v.jpg", "service": SUPPL352 + "231", "caption": "Paris suppl. gr. 352 fol. 113v"}},
    "ms": {
        "scan_source": "Bibliothèque nationale de France, Gallica https://gallica.bnf.fr/ark:/12148/btv1b11000151s (IIIF via openapi.bnf.fr; images 230-231)",
        "license": BNF_LICENSE,
        "manuscript": "Paris, BnF, Supplément grec 352, bombycin, 182 fol., 13th century (BnF dating 1201-1300); Varia Historia on fol. 106v-132 (Pinakes 53102)",
        "mapping": "Own visual check: the start, page break and end read on the images, with the 37 text lines of fol. 113r counted by hand (recounted on a ruled crop 2026-11-12; see scan_note)",
        "urls": ["https://gallica.bnf.fr/ark:/12148/btv1b11000151s", "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc24612m"],
    },
    "place": {
        "3.18": ("fol. 113r line 30 to fol. 113v line 18", ["113r", "113v"],
                 "3.18 begins in fol. 113r line 30 (text lines counted from the top; the folio number above them is not counted; recounted 2026-11-12), after the end of 3.17 ‹ἐπιδραμών›, with the title ‹Περὶ συνουσίας μίδου καὶ σιληνοῦ› between crosses and ‹Περιηγεῖταί τινα θεόπομπος "
                 "συνουσίαν›; the last line of the page (37) ends ‹γεωργεῖν δὲ καὶ σπείρειν οὐδὲν αὐτοῖς ἔργον εἶναι›; fol. 113v begins ‹καὶ διατελοῦσιν ὑγιεῖς καὶ ἄνοσοι›, "
                 "with subtitles in lines 2 and 8, the Meropes in line 9, and the chapter ends in line 18, ‹ἐμοὶ δὲ δεινὸς εἶναι δοκεῖ μυθολόγος›, followed by the title of 3.19. Read on the BnF images at full resolution."),
    },
}


PASSAGE_BUILDERS = [hymn7_passage, pindar_p10, pindar_o3, herodotus_4_13_16, herodotus_4_32_36, callimachus_passage,
                    apollonius_passage, diodorus_2_47, strabo_1_3_22, strabo_7_3_1, strabo_11_6_2, strabo_15_1_57, mela_3_36_37,
                    pliny_4_88_91, pausanias_1_31_2, pausanias_10_5]

COLLECTION = {
    "key": "hyperborea",
    "prefix": "verified-hyperborea-",
    "label": "Hyperborea: the ancient testimonia",
    "group": "Greece",
    "date_sort": -450,
    "author_name": "Greek and Latin writers, 5th c. BCE - 2nd c. AD (medieval manuscripts)",
    "source_url": "https://www.perseus.tufts.edu/",
    "critical_edition": "Perseus editions named per passage",
    "translator_name": "Public-domain translators named per passage",
    "original_lang_label": "Greek / Latin",
    "original_lang_code": "grc",
    "edition_label": "",
    "search_terms": "hyperborea hyperboreans apollo delos abaris aristeas arimaspians boreas north wind rhipaean",
    "description": ("What the ancient writers said about the Hyperboreans, the people 'beyond the North Wind' "
                    "beloved of Apollo, each passage shown on the medieval manuscript page that carries it."),
    "_authors": [
        {"id": "pomponius-mela", "name": "Pomponius Mela", "dates": "fl. c. 43 AD", "century": 1, "era": "Imperial",
         "tradition": "roman", "language": "Latin", "name_latin": "Pomponius Mela",
         "bio": "Roman geographer from Tingentera in southern Spain, author of the Chorographia, the oldest surviving Latin geography."},
        {"id": "callimachus", "name": "Callimachus", "dates": "c. 305-240 BCE", "century": -3, "era": "Hellenistic",
         "tradition": "greek", "language": "Greek", "name_latin": "Callimachus",
         "bio": "Poet and scholar of Cyrene who worked at the library of Alexandria; author of hymns, epigrams and the Aetia."},
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    build(COLLECTION, [f() for f in PASSAGE_BUILDERS], args.force)


if __name__ == "__main__":
    main()
