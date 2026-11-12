#!/usr/bin/env python3
"""
import_rigveda.py - Rigveda hymns, each group of verses linked to the manuscript page that carries it.

One entry per hymn (sukta). Inside an entry, one section per manuscript page: the verses whose
last syllable stands on that page. A verse that begins on the previous page lists both pages.

Chain of evidence
  1. SCANS     University of Pennsylvania, Kislak Center, Ms. Coll. 390 (Indic manuscripts),
               photographed by Penn Libraries and published on OPenn with the Creative Commons
               Public Domain Mark. Web JPEGs (one image per opening; a pothi leaf is turned
               top to bottom, so the verso is the upper leaf and the next recto the lower leaf).
               Witnesses used are listed in WITNESSES below with their OPenn ids.
  2. MAPPING   Read on the images by eye. For every page the opening words of the first line
               were transcribed (data/sources/rigveda/readings/<witness>.txt, IAST, one line per
               page, with notes on khila insertions, colophons and lacunae). Each reading is
               located in Aufrecht's text by an alignment search that runs forward from the
               previous page (no positions are extrapolated: every page boundary is a reading
               from the image). A page carries the text from its own start to the start of the
               next page that carries Rigveda text. Pages whose whole text is khila (apocryphal
               supplements written into the manuscript) are marked KHILA and carry no verses.
               Places where the text runs on unevenly were checked on the full page image and
               the result is written into the readings file (khila blocks, a lost leaf).
               Varga (aṣṭaka-adhyāya-varga) concordance from the Sansknet padapāṭha (GRETIL).
  3. SANSKRIT  Ṛgveda-Saṃhitā, Aufrecht's edition (Bonn 1877), accented text entered by
               B. A. van Nooten and G. B. Holland, revised by D. Eichler, GRETIL TEI
               sa_Rgveda-edAufrecht.xml (CC BY-NC-SA 4.0).
  4. ENGLISH   Ralph T. H. Griffith, The Hymns of the Rigveda (Benares: E. J. Lazarus,
               1889-1892), public domain; digital text from the VedaWeb project, University
               of Cologne (rigveda/translations/eng/griffith.csv, CC BY-NC-SA 4.0). Griffith
               left RV 10.86.16-17 untranslated; those verses are not published.
               ERRATA lists OCR slips of the digital text corrected against the printed page.
  5. TITLES    Addressee of each hymn from VedaWeb info/addressees.json (CC BY 4.0).

Usage:
    python3 scripts/import_rigveda.py            # build everything
    python3 scripts/import_rigveda.py --report   # print page map and coverage only
"""

import argparse
import difflib
import io
import json
import re
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "rigveda"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "rigveda"
PUB_DIR = ROOT / "translations" / "published"
COLL_FILE = ROOT / "data" / "collections" / "rigveda.json"
TODAY = date.today().isoformat()
KEY = "rigveda"
PREFIX = "verified-rigveda-"
TEI = "{http://www.tei-c.org/ns/1.0}"
OPENN = "https://openn.library.upenn.edu/Data/0002"
UA = {"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"}

WITNESSES = {
    "penn48": {
        "shelfmark": "Penn Ms. Coll. 390 Item 48",
        "openn": "mscoll390_item48",
        "imgbase": "3593",
        "title": "Ṛgvedasaṃhitā, aṣṭaka 8",
        "date": "1711 CE (colophon: Saṃvat 1768)",
        "year": 1711,
        "desc": ("a paper manuscript of the eighth aṣṭaka (RV 10.46-10.191) of the Ṛgveda Saṃhitā "
                 "in Devanāgarī, 158 leaves, 6 lines to the page, with the accents marked in red; "
                 "the scribe's colophon on fol. 158 gives Saṃvat 1768 (1711 CE)"),
        "form": "samhita",
        "readings": "readings/penn48.txt",
        "start": (10, 46, 1),
        # page whose verses stop early because the following leaf is lost: page -> first verse NOT on it
        "cut": {"60v": (10, 87, 20)},
    },
}

# Names used in titles for well-known hymns.
HYMN_NAMES = {
    (10, 85): "Surya's wedding (Vivaha Sukta)",
    (10, 86): "Indra, Indrani and Vrishakapi",
    (10, 90): "Purusha Sukta",
    (10, 95): "Pururavas and Urvashi",
    (10, 97): "Hymn to the healing plants (Oshadhi Sukta)",
    (10, 108): "Sarama and the Panis",
    (10, 117): "In praise of giving",
    (10, 121): "Hiranyagarbha, the golden germ",
    (10, 125): "Devi Sukta, the speech of Vac",
    (10, 127): "Hymn to Night (Ratri Sukta)",
    (10, 129): "Nasadiya Sukta, the hymn of creation",
    (10, 136): "The long-haired ascetic (Keshin)",
    (10, 146): "Hymn to the forest (Aranyani)",
    (10, 151): "Hymn to faith (Shraddha)",
    (10, 154): "To the departed",
    (10, 190): "Cosmic order and creation (Aghamarshana)",
    (10, 191): "Hymn of concord (Samjnana)",
    (10, 71): "Hymn on knowledge (Jnana Sukta)",
    (10, 72): "The birth of the gods",
    (10, 75): "Praise of the rivers (Nadistuti)",
    (10, 81): "Vishvakarman",
    (10, 82): "Vishvakarman",
    (10, 119): "The song of the drunken Indra (Laba)",
    (10, 168): "Hymn to the wind (Vata)",
    (10, 173): "Hymn for a king",
}

MANDALA_DESC = {
    1: "book (maṇḍala) 1, a collection of hymns by many families of poets",
    2: "book (maṇḍala) 2, the family book of Gṛtsamada",
    3: "book (maṇḍala) 3, the family book of Viśvāmitra",
    4: "book (maṇḍala) 4, the family book of Vāmadeva",
    5: "book (maṇḍala) 5, the family book of the Atri clan",
    6: "book (maṇḍala) 6, the family book of Bharadvāja",
    7: "book (maṇḍala) 7, the family book of Vasiṣṭha",
    8: "book (maṇḍala) 8, the book of the Kaṇva and Aṅgiras poets",
    9: "book (maṇḍala) 9, the hymns to Soma Pavamāna",
    10: "book (maṇḍala) 10, the last and latest book",
}

ERRATA = {
    # verse id: [(text in digital copy, text of the printed page)], each checked on the printed book
}


# ----------------------------------------------------------------------------- utilities

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def norm(s):
    """Loose phonetic normalisation used only for locating page readings in the edition."""
    s = unicodedata.normalize("NFD", s)
    s = re.sub(r"[̀-ͯ]", "", s)
    s = unicodedata.normalize("NFC", s).lower()
    s = s.replace("ḻh", "ḍh").replace("ḻ", "ḍ").replace("ḷ", "ḍ")
    s = re.sub(r"[^a-zāīūṛṝḷḹṃṁḥṅñṭḍṇśṣ]", "", s)
    s = unicodedata.normalize("NFD", s)
    s = re.sub(r"[̀-ͯ]", "", s)
    s = re.sub(r"[m](?=[kgcjtdpbsyrlvh])", "M", s)
    s = re.sub(r"[n](?=[kgcjtdpbsyrlvh])", "M", s)
    s = re.sub(r"([kgcjtdpbsyrlv])\1", r"\1", s)
    return s


# ----------------------------------------------------------------------------- texts

def load_samhita():
    root = ET.parse(SRC / "sa_Rgveda-edAufrecht.xml").getroot()
    verses = {}
    order = []
    for lg in root.iter(TEI + "lg"):
        vid = lg.get("{http://www.w3.org/XML/1998/namespace}id") or ""
        if not vid.startswith("RV_"):
            continue
        m, h, v = (int(x) for x in vid[3:].split("."))
        padas = []
        for l in lg.findall(TEI + "l"):
            acc = re.sub(r"\s+", " ", "".join(l.itertext())).strip()
            parts = [l.text or ""]
            for c in l:
                if c.tag != TEI + "orig":
                    parts.append("".join(c.itertext()))
                parts.append(c.tail or "")
            plain = re.sub(r"\s+", " ", "".join(parts)).strip()
            padas.append((l.get("n"), acc, plain))
        verses[(m, h, v)] = padas
        order.append((m, h, v))
    return verses, order


class Stream:
    """Normalised running text of the samhita with a char -> (verse, pada) index."""

    def __init__(self, verses, order):
        chars, idx = [], []
        self.vstart, self.vend, self.pstart = {}, {}, {}
        for key in order:
            self.vstart[key] = len(chars)
            for pid, acc, plain in verses[key]:
                self.pstart.setdefault(pid, len(chars))
                n = norm(plain)
                chars.extend(n)
                idx.extend([(key, pid)] * len(n))
            self.vend[key] = len(chars)
        self.s = "".join(chars)
        self.idx = idx
        self.plain = {pid: plain for key in order for pid, acc, plain in verses[key]}

    def words_at(self, p, n=4):
        """The edition's words at normalised position p (plain text, no accents)."""
        key, pid = self.idx[p]
        off = p - self.pstart[pid]
        words = [w for w in self.plain[pid].split() if w not in ("|", "||")]
        acc = 0
        for i, w in enumerate(words):
            ln = len(norm(w))
            if off < acc + ln:
                lead = "" if off == acc else "-"
                return lead + " ".join(words[i:i + n])
            acc += ln
        return " ".join(words[-n:])

    def find(self, reading, lo, hi):
        r = norm(reading)
        L = len(r)
        best = (0.0, None)
        sm = difflib.SequenceMatcher(autojunk=False)
        sm.set_seq2(r)
        for p in range(max(0, lo), min(len(self.s) - L, hi)):
            sm.set_seq1(self.s[p:p + L])
            if sm.quick_ratio() < best[0]:
                continue
            sc = sm.ratio()
            if sc > best[0]:
                best = (sc, p)
        sc, p = best
        # refine the start with the first 14 normalised characters of the reading
        head = r[:14]
        rb = (0.0, p)
        for q in range(max(lo, p - 90), p + 90):
            rr = difflib.SequenceMatcher(None, self.s[q:q + len(head)], head, autojunk=False).ratio()
            if rr > rb[0] + 1e-9:
                rb = (rr, q)
        if rb[0] >= 0.75:
            p = rb[1]
        return sc, p


def load_concordance():
    """(m,h,v) -> (astaka, adhyaya, varga, verse-in-varga) from the Sansknet padapatha markers."""
    body = (SRC / "sa_RgvedasaMhitApadapATha.xml").read_text(encoding="utf-8")
    body = body[body.find("<body"):]
    toks = re.findall(r"-RV_(\d+):(\d+)/(\d+)-|// RV_(\d+),(\d+)\.(\d+) //", body)
    out, cur, vin, prev = {}, None, 0, None
    for t in toks:
        if t[0]:
            cur, vin = (int(t[0]), int(t[1]), int(t[2])), 0
            continue
        vin += 1
        key = (int(t[3]), int(t[4]), int(t[5]))
        if key in out and key == (9, 97, 36) and prev == (9, 97, 34):
            key = (9, 97, 35)  # the GRETIL file labels 9.97.35 as a second 9.97.36
        out[key] = cur + (vin,)
        prev = key
    return out


def load_griffith():
    out = {}
    for line in (SRC / "vedaweb" / "griffith.csv").read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        ref, text = line.split("\t", 1)
        m, h, v = (int(x) for x in ref.split("."))
        text = text.strip()
        if text.startswith("[Griffith:"):
            continue  # stanza Griffith did not translate
        for wrong, right in ERRATA.get((m, h, v), []):
            assert wrong in text, ((m, h, v), wrong)
            text = text.replace(wrong, right)
        out[(m, h, v)] = text
    return out


def load_addressees():
    d = json.loads((SRC / "vedaweb" / "addressees.json").read_text(encoding="utf-8"))
    out = {}
    for k, v in d.items():
        m, h = (int(x) for x in k.split("."))
        out[(m, h)] = v[0][1].strip().rstrip(".")
    return out


# ----------------------------------------------------------------------------- manuscript pages

def tei_pages(w):
    """Ordered page list for a Penn witness: id (sequential foliation), label, image index, position."""
    tei = SRC / w["key"] / f"{w['openn']}_TEI.xml"
    if not tei.exists():
        tei.parent.mkdir(parents=True, exist_ok=True)
        tei.write_bytes(fetch(f"{OPENN}/{w['openn']}/data/{w['openn']}_TEI.xml"))
    s = tei.read_text(encoding="utf-8")
    pages = []
    for n, body in re.findall(r'<surface[^>]*n="([^"]*)"[^>]*>(.*?)</surface>', s, re.S):
        web = re.findall(r'url="(web/[^"]+)"', body)[0]
        idx = int(re.findall(r"_(\d{4})_web", web)[0])
        halves = [x.strip() for x in n.split("-")] if re.search(r"\d[rv]\s*(=\s*\d+[rv])?\s*-", n) else [n.strip()]
        for pos, half in zip(("upper", "lower") if len(halves) == 2 else ("single",), halves):
            m = re.match(r"^(\d+[rv])(?:\s*=\s*(\d+[rv]))?$", half)
            if not m:
                continue
            written, seq = m.group(1), m.group(2) or m.group(1)
            label = f"{seq} (numbered {written} by the scribe)" if m.group(2) else seq
            pages.append({"id": seq, "label": label, "image": idx, "web": web, "pos": pos})
    return pages


def leaf_boxes(img):
    a = np.asarray(img.convert("L"), dtype=np.float32)
    H, W = a.shape
    light = a > 90
    rowfrac = light.mean(axis=1)
    bands, start = [], None
    for i, v in enumerate(rowfrac > 0.35):
        if v and start is None:
            start = i
        if not v and start is not None:
            bands.append((start, i)); start = None
    if start is not None:
        bands.append((start, H))
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < H * 0.04:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    boxes = []
    for y0, y1 in merged:
        if y1 - y0 < H * 0.12:
            continue
        col = light[y0:y1].mean(axis=0) > 0.5
        xs = np.where(col)[0]
        boxes.append((int(xs.min()), y0, int(xs.max()) + 1, y1))
    return boxes


def web_image(w, page):
    cache = SRC / w["key"] / "web" / Path(page["web"]).name
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(fetch(f"{OPENN}/{w['openn']}/data/{page['web']}"))
    return Image.open(cache).convert("RGB")


def page_scan(w, page, force=False):
    """Crop one leaf from the opening and save it under site/assets/scans/rigveda/."""
    name = f"{w['key']}-f{int(page['id'][:-1]):03d}{page['id'][-1]}.jpg"
    out = SCAN_DIR / name
    if out.exists() and not force:
        return f"{KEY}/{name}"
    img = web_image(w, page)
    boxes = leaf_boxes(img)
    if page["pos"] == "single" or len(boxes) == 1:
        box = boxes[0]
    else:
        assert len(boxes) == 2, (page, boxes)
        box = boxes[0] if page["pos"] == "upper" else boxes[1]
    x0, y0, x1, y1 = box
    pad = 24
    crop = img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    crop.save(out, quality=85)
    return f"{KEY}/{name}"


# ----------------------------------------------------------------------------- page map

def read_readings(w):
    rows = []
    for line in (SRC / w["readings"]).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        rows.append({"page": parts[0], "reading": parts[1], "note": parts[2] if len(parts) > 2 else ""})
    return rows


def page_map(w, S):
    """Locate every page start in the edition. Returns samhita-bearing pages with [start, end)."""
    rows = read_readings(w)
    m, h, v = w["start"]
    pos = S.vstart[(m, h, v)] - 50
    located = []
    for r in rows:
        if r["reading"] == "KHILA":
            r["khila"] = True
            continue
        if r["reading"].startswith("@"):
            p, sc = S.pstart[r["reading"][1:]], 1.0
        else:
            sc, p = S.find(r["reading"], pos, pos + 3500)
        # snap to a verse start when the page begins on one
        key = S.idx[p][0]
        for k in (key, S.idx[max(0, p - 3)][0]):
            if abs(S.vstart[k] - p) <= 2:
                p = S.vstart[k]
        r.update(start=p, score=round(sc, 3), pada=S.idx[p][1])
        located.append(r)
        pos = p + 1
    for i, r in enumerate(located):
        r["end"] = located[i + 1]["start"] if i + 1 < len(located) else S.vend[max(k for k in S.vend if k[0] == 10)]
        cut = w.get("cut", {}).get(r["page"])
        if cut:
            r["end"] = S.vstart[cut]
            r["cut"] = cut
    # sanity: starts strictly increasing
    for a, b in zip(located, located[1:]):
        assert b["start"] > a["start"], (a["page"], b["page"])
    return rows, located


def assign_verses(located, S, order, first, last):
    """verse -> (end page index, start page index) for verses wholly carried by contiguous pages."""
    def page_of(p):
        for i, r in enumerate(located):
            if r["start"] <= p < r["end"]:
                return i
        return None
    out = {}
    for key in order:
        if key < first or key > last:
            continue
        vs, ve = S.vstart[key], S.vend[key]
        i0, i1 = page_of(vs), page_of(ve - 1)
        if i0 is None or i1 is None:
            continue
        if any(located[j]["end"] != located[j + 1]["start"] for j in range(i0, i1)):
            continue
        out[key] = (i1, i0)
    return out


# ----------------------------------------------------------------------------- entries

def padref(pid):
    m, h, rest = pid.split(".")
    return f"{int(m)}.{int(h)}.{int(rest[:-1])}"


def iast_title(m, h, addressee):
    name = HYMN_NAMES.get((m, h))
    if name:
        return f"Rigveda {m}.{h}: {name}"
    return f"Rigveda {m}.{h}: to {addressee}" if addressee else f"Rigveda {m}.{h}"


def build(args):
    verses, order = load_samhita()
    S = Stream(verses, order)
    conc = load_concordance()
    eng = load_griffith()
    addr = load_addressees()
    entries = []
    report = []
    for wkey, w in WITNESSES.items():
        w["key"] = wkey
        pages = {p["id"]: p for p in tei_pages(w)}
        rows, located = page_map(w, S)
        for r in rows:
            r["label"] = pages[r["page"]]["label"]
        ids = [r["page"] for r in rows]
        first = w["start"]
        last = max(k for k in order if k[0] == 10)
        assign = assign_verses(located, S, order, first, last)
        if args.report:
            for r in located:
                print(f"{wkey} {r['page']:>6} {r['score']:.2f} {r['pada']:>12} {r['start']:>7}-{r['end']:<7} {r['reading'][:40]}")
        hymns = sorted({(k[0], k[1]) for k in assign})
        for (m, h) in hymns:
            hv = [k for k in order if k[:2] == (m, h)]
            on_ms = [k for k in hv if k in assign]
            pub = [k for k in on_ms if k in eng]
            missing_ms = [k for k in hv if k not in assign]
            missing_en = [k for k in on_ms if k not in eng]
            groups = {}
            for k in pub:
                groups.setdefault(assign[k][0], []).append(k)
            sections = []
            for pi in sorted(groups):
                ks = groups[pi]
                start_pi = assign[ks[0]][1]
                pg = located[pi]
                scan_pages = []
                for j in range(start_pi, pi + 1):
                    scan_pages.append(page_scan(w, pages[located[j]["page"]], args.force_scans))
                vr = f"{ks[0][2]}" if len(ks) == 1 else f"{ks[0][2]}-{ks[-1][2]}"
                orig = "<br>".join(f"<sup>{k[2]}</sup>" + " ".join(p[1] for p in verses[k]) for k in ks)
                text = "<br>".join(f"<sup>{k[2]}</sup>{eng[k]}" for k in ks)
                nxt = located[pi + 1] if pi + 1 < len(located) else None
                pgl = pages[pg["page"]]
                note = (f"{w['shelfmark']}, fol. {pgl['label']} (OPenn image {pgl['image']}, "
                        f"{'upper' if pgl['pos'] == 'upper' else 'lower' if pgl['pos'] == 'lower' else 'single'} leaf). "
                        f"Checked on the image: the Rigveda text on this page begins in RV {padref(pg['pada'])} "
                        f"‹{S.words_at(pg['start'])}›.")
                if pg.get("note"):
                    note += f" {pg['note'][0].upper() + pg['note'][1:]}."
                if nxt is not None and not pg.get("cut"):
                    note += (f" The next page with Rigveda text, fol. {pages[nxt['page']]['label']}, begins in "
                             f"RV {padref(nxt['pada'])} ‹{S.words_at(nxt['start'])}›.")
                if pg.get("cut"):
                    c = pg["cut"]
                    note += (f" This page breaks off in RV {c[0]}.{c[1]}.{c[2]}; the following leaf is lost "
                             f"(the next surviving page, fol. {pages[nxt['page']]['label']}, begins in RV {padref(nxt['pada'])}).")
                note += f" Verse{'s' if len(ks) > 1 else ''} {m}.{h}.{vr} end{'' if len(ks) > 1 else 's'} on this page"
                if start_pi < pi:
                    note += f"; {m}.{h}.{ks[0][2]} begins on fol. {pages[located[start_pi]['page']]['label']}"
                note += "."
                a = conc.get(ks[0])
                ref = f"RV {m}.{h}.{vr}"
                if a:
                    ref += f" (aṣṭaka {a[0]}, adhyāya {a[1]}, varga {a[2]})"
                ref += f"; {w['shelfmark']} fol. {pg['page']}"
                sections.append({
                    "section": vr,
                    "original_ref": ref,
                    "original_text": orig,
                    "text": text,
                    "scan_pages": scan_pages,
                    "scan_note": note,
                })
            if not sections:
                continue
            entries.append(make_entry(m, h, hv, sections, missing_ms, missing_en, w, addr, located, pages))
            report.append((m, h, len(hv), len(pub)))
    write_all(entries)
    return report


def make_entry(m, h, hv, sections, missing_ms, missing_en, w, addr, located, pages):
    tid = f"{PREFIX}{m}-{h}"
    adr = addr.get((m, h), "")
    title = iast_title(m, h, adr)
    nver = len(hv)
    gaps = []
    if missing_ms:
        gaps.append(f"verse{'s' if len(missing_ms) > 1 else ''} {', '.join(f'{k[0]}.{k[1]}.{k[2]}' for k in missing_ms)} "
                    f"{'are' if len(missing_ms) > 1 else 'is'} not in this manuscript (a leaf is lost) and {'are' if len(missing_ms) > 1 else 'is'} not shown")
    if missing_en:
        gaps.append(f"verse{'s' if len(missing_en) > 1 else ''} {', '.join(f'{k[0]}.{k[1]}.{k[2]}' for k in missing_en)} "
                    f"{'were' if len(missing_en) > 1 else 'was'} left untranslated by Griffith and {'are' if len(missing_en) > 1 else 'is'} not shown")
    fols = []
    for s in sections:
        for p in s["scan_pages"]:
            f = p.split("-f")[-1][:-4].lstrip("0")
            if f not in fols:
                fols.append(f)
    folrange = fols[0] if len(fols) == 1 else f"{fols[0]}-{fols[-1]}"
    intro = (
        f"<p>Rigveda {m}.{h} is a hymn of {nver} verses"
        + (f" addressed to {adr}" if adr else "") + f", in {MANDALA_DESC[m]} of the Rigveda, "
        "the oldest collection of Sanskrit hymns, composed in the second half of the second millennium BCE "
        "and handed down orally for many centuries before it was written down.</p>"
        f"<p>The manuscript shown is {w['shelfmark']} (University of Pennsylvania), {w['desc']}. "
        f"This hymn stands on fol. {folrange}. Each section below gives the verses that end on one page; "
        "the page boundaries were read on the images (the opening words of every page), not counted out. "
        "Like most Rigveda manuscripts, this one writes a repeated refrain in short form after its first occurrence "
        "(for example kasmai° for kasmai devāya haviṣā vidhema); the Sanskrit shown is the full text of Aufrecht's edition.</p>"
    )
    if gaps:
        intro += "<p>Gaps: " + "; ".join(gaps) + ".</p>"
    notes = [
        "Sanskrit: Aufrecht's edition (1877) with the Vedic accents, as entered by van Nooten and Holland (GRETIL).",
        "English: Ralph T. H. Griffith, The Hymns of the Rigveda (1889-1892), from the VedaWeb digital text.",
    ]
    khila = [s for s in sections if "khila" in s["scan_note"]]
    if khila:
        notes.append("This manuscript inserts khila verses (supplementary hymns outside Aufrecht's text) at some hymn ends; "
                     "they are noted in the section notes and not reproduced.")
    sc_pages = []
    for s in sections:
        for p in s["scan_pages"]:
            if p not in sc_pages:
                sc_pages.append(p)
    desc = (f"{title}: Sanskrit text and Griffith's English, each verse linked to the page of a {w['year']} "
            f"Rigveda manuscript ({w['shelfmark']}) that carries it.")
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Vedic Sanskrit / English",
        "source": f"{w['shelfmark']} ({w['date']}, OPenn, Public Domain Mark) + Aufrecht's accented text (GRETIL) + Griffith's English (VedaWeb)",
        "description": desc,
        "introduction": intro,
        "translator_notes": notes,
        "translation": sections,
        "verification": {
            "scan_source": f"University of Pennsylvania Libraries, OPenn: {OPENN}/html/{w['openn']}.html",
            "scan_license": "Creative Commons Public Domain Mark 1.0 (as stated by Penn Libraries on OPenn)",
            "scan_manuscript": f"{w['shelfmark']}, {w['title']}, {w['date']}",
            "scan_mapping": ("Page boundaries read on the images: the opening words of every page were transcribed and located in "
                             "Aufrecht's text (data/sources/rigveda/readings); khila insertions, colophons and the lost leaf were "
                             "checked on the full page images. A section holds the verses that end on its page."),
            "scan_mapping_urls": [f"{OPENN}/html/{w['openn']}.html", f"{OPENN}/{w['openn']}/data/{w['openn']}_TEI.xml"],
            "scan_local_paths": sc_pages,
            "original_text_source": "Ṛgveda-Saṃhitā, ed. Th. Aufrecht (Bonn 1877), accented e-text by B. A. van Nooten and G. B. Holland, rev. D. Eichler, GRETIL: https://gretil.sub.uni-goettingen.de/gretil/corpustei/sa_Rgveda-edAufrecht.xml",
            "original_text_license": "CC BY-NC-SA 4.0 (GRETIL)",
            "translation_source": "Ralph T. H. Griffith, The Hymns of the Rigveda (Benares: E. J. Lazarus, 1889-1892); digital text VedaWeb, University of Cologne: https://github.com/VedaWebProject/vedaweb-data/blob/main/rigveda/translations/eng/griffith.csv",
            "translation_license": "translation public domain (published 1889-1892); VedaWeb digital text CC BY-NC-SA 4.0",
            "translator": "Ralph T. H. Griffith (1889-1892)",
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "title": title, "author_id": "vedic-rishi", "language": "Vedic Sanskrit",
        "era": "Vedic", "tradition": "vedic", "category": "sacred-text",
        "date_approx": f"c. 1500-1000 BCE (composition); manuscript {w['year']} CE ({w['shelfmark']})",
        "century": -12,
        "source": entry["source"], "description": desc,
        "themes": ["rigveda", "veda", "vedic", "hymn", f"mandala-{m}", "sanskrit", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p, "caption": f"{w['shelfmark']}, fol. {p.split('-f')[-1][:-4].lstrip('0')}"} for p in sc_pages]},
        "order_key": (m, h),
    }
    return entry, row


def write_all(entries):
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for entry, row in sorted(entries, key=lambda e: e[1]["order_key"]):
        (PUB_DIR / f"{entry['id']}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(row)
    for i, r in enumerate(rows, 1):
        r.pop("order_key")
        r["order"] = i
    keep = {r["id"] for r in rows}
    for f in PUB_DIR.glob(f"{PREFIX}*.json"):
        if f.stem not in keep:
            f.unlink()
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Rigveda",
            "group": "India", "date_sort": -1200,
            "author_name": "Vedic seers (c. 1500-1000 BCE); manuscripts 17th-18th c.",
            "source_url": f"{OPENN}/html/mscoll390_item48.html",
            "critical_edition": "Aufrecht (1877), accented e-text via GRETIL",
            "translator_name": "Ralph T. H. Griffith (1889-1892)",
            "original_lang_label": "Vedic Sanskrit · Aufrecht (accented)",
            "original_lang_code": "sa",
            "edition_label": "",
            "search_terms": "rigveda rig veda rgveda vedic hymns sanskrit agni indra soma purusha nasadiya hiranyagarbha gayatri",
            "description": ("The Rigveda, the oldest collection of Sanskrit hymns, hymn by hymn: Aufrecht's accented text, "
                            "Griffith's English, and the page of a dated Devanagari manuscript in the University of Pennsylvania "
                            "collection that carries each verse."),
        },
        "texts": rows,
    }
    COLL_FILE.parent.mkdir(parents=True, exist_ok=True)
    COLL_FILE.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(rows)} entries, {sum(len(e[0]['translation']) for e in entries)} sections")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--force-scans", action="store_true")
    args = ap.parse_args()
    rep = build(args)
    full = sum(1 for r in rep if r[2] == r[3])
    print(f"hymns: {len(rep)}, complete: {full}, partial: {[f'{m}.{h} {n}/{t}' for m, h, t, n in rep if t != n]}")


if __name__ == "__main__":
    main()
