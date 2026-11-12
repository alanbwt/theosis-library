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
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
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
    marks = list(re.finditer(r'(?is)<A CLASS="sec" NAME="([\d.]+)">\d+</A>', s))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(s)
        chunk = re.split(r'(?is)<A CLASS="chapter"|<HR|<DIV CLASS="endnotes"|<TABLE', s[m.end():end])[0]
        t = H.unescape(re.sub(r"<[^>]+>", " ", chunk)).replace("⁠", "").replace(" ", " ")
        out[m.group(1)] = re.sub(r"\s+", " ", t).strip()
    return out


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
            imgs[k] = v
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
PASSAGES = []

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
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    build(COLLECTION, PASSAGES, args.force)


if __name__ == "__main__":
    main()
