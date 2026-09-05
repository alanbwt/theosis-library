#!/usr/bin/env python3
"""
import_alexandrinus.py -- Import the New Testament of Codex Alexandrinus
(GA 02, 5th c., British Library Royal MS 1 D. VIII) at chapter level.

Chain of evidence for every section
-----------------------------------
1. Scan: the page of the 1909 British Museum photographic facsimile
   ("The Codex Alexandrinus (Royal MS. 1 D. V-VIII) in reduced photographic
   facsimile: New Testament and Clementine Epistles", ed. F. G. Kenyon,
   London 1909). The facsimile reproduces each manuscript page in order and
   prints the verse range of the page beneath it (e.g. "Matt. xxvi. 46-73").
   Digitised by the Getty Research Institute, hosted by the Internet Archive
   (item codexalexandrinu01unse). Published 1909 -> public domain.
2. Page mapping: NTVMR (ntvmr.uni-muenster.de, INTF Muenster) verse-level page
   index for docID 20002, CC BY 4.0. Each NTVMR page (folio r/v) maps to one
   facsimile leaf (leaf = 17 + NTVMR page ordinal); the mapping is verified
   page by page by OCR-reading the caption the facsimile prints beneath each
   plate and by CSNTM's independent verse -> image index (manuscriptId 203).
   Only pages where the facsimile caption agrees with NTVMR are used.
3. Greek: Tischendorf 8th ed. (1869) via bolls.life TISCH -- an edition, not
   the manuscript's own reading (stated in every introduction).
4. English: King James Version via bible-api.com.

Run:
  python3 scripts/import_alexandrinus.py --prove john 1     # one chapter, prints evidence
  python3 scripts/import_alexandrinus.py --all              # everything
  python3 scripts/import_alexandrinus.py --verify-only      # just the OCR cross-check

Outputs:
  site/assets/scans/alexandrinus/alex-<folio>.jpg   (one file per manuscript page,
                                                     shared by every chapter on it)
  translations/published/verified-alexandrinus-<book>-<chapter>.json
  data/pending/alexandrinus_texts.json               (metadata; NOT merged into
                                                     data/texts.json by this script)
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_verified import (  # noqa: E402
    CSP_BOOKS_NT,
    NT_BOOK_PRETTY,
    clean_strongs,
    fetch_kjv_chapter,
    fetch_tisch_chapter,
)

ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "alexandrinus"
PENDING = ROOT / "data" / "pending" / "alexandrinus_texts.json"
CACHE = Path(
    os.environ.get(
        "ALEX_CACHE",
        "/private/tmp/claude-501/-Users-mattimore/08116b0f-d4b1-43b3-972f-f6da24760f6d/scratchpad/alex_cache",
    )
)
CACHE.mkdir(parents=True, exist_ok=True)
(CACHE / "ia").mkdir(exist_ok=True)
(CACHE / "text").mkdir(exist_ok=True)

USER_AGENT = "TheosisLibraryBot/1.0 (+https://theosislibrary.com)"
NTVMR_DOCID = 20002
NTVMR_URL = (
    "https://ntvmr.uni-muenster.de/community/vmr/api/metadata/manuscript/get/"
    f"?docID={NTVMR_DOCID}&format=json"
)
IA_ITEM = "codexalexandrinu01unse"
IA_PAGE = (
    "https://archive.org/download/{item}/{item}_jp2.zip/{item}_jp2%2F{item}_{leaf:04d}.jp2&ext=jpg"
)
IA_LEAF_OFFSET = 17  # facsimile leaf 17 = NTVMR page ordinal 0 (fol. 26r, Matt 25:6)
CSNTM_MS_ID = 203
CSNTM_REFERER = "https://manuscripts.csntm.org/manuscript/View/GA_02"

SCAN_LICENSE = (
    "Public domain: 1909 British Museum photographic facsimile (ed. F. G. Kenyon), "
    "digitised by the Getty Research Institute for the Internet Archive"
)
SCAN_SOURCE = (
    "Internet Archive, 'The Codex Alexandrinus (Royal MS. 1 D. V-VIII) in reduced "
    "photographic facsimile', vol. 1: New Testament (British Museum, 1909), "
    "item codexalexandrinu01unse"
)

# NTVMR index corrections (documented; applied only where the index is
# self-evidently mistyped and the facsimile caption confirms the fix).
NTVMR_FIXES = {
    # page 801 (fol. 99v) is indexed "Acts 25:16-27; Acts 27:1-11" but the next
    # page (fol. 100r) begins at Acts 26:11 and Acts 27:1-3 comes after 26:32
    # on that same page. The facsimile caption reads "Acts xxv. 16 - xxvi. 11".
    801: "Acts 25:16-27; Acts 26:1-11",
}

# Captions that tesseract could not read cleanly, transcribed by eye from the
# facsimile plate (contact sheets of the caption strips were inspected on
# 2026-09-05). Each is parsed and compared to NTVMR exactly like OCR output.
MANUAL_CAPTIONS = {
    35: "Mark vii. 24-viii. 14", 57: "Luke ii. 38-iii. 11", 82: "Luke xvi. 1-24",
    101: "John iii. 20-iv. 13", 114: "John xiii. 5-36", 141: "Acts xii. 10-xiii. 7",
    147: "Acts xvi. 15-38", 155: "Acts xxi. 27-xxii. 10", 161: "Acts xxvi. 11-xxvii. 3",
    170: "1 Peter i. 13-ii. 16", 172: "1 Peter iii. 16-v. 1", 178: "1 John iii. 5-iv. 4",
    187: "Rom. v. 3-vi. 9", 196: "Rom. xv. 11-xvi. 4", 199: "1 Cor. i. 31-iii. 13",
    200: "1 Cor. iii. 13-iv. 18", 201: "1 Cor. iv. 18-vi. 18", 207: "1 Cor. xii. 3-xiii. 3",
    213: "2 Cor. i. 16-iii. 5", 215: "2 Cor. xii. 7-xiii. 9", 216: "2 Cor. xiii. 9-Gal. i. 14",
    219: "Gal. iii. 24-iv. 30", 226: "Eph. v. 33-vi. 24", 232: "Col. ii. 8-iii. 15",
    233: "Col. iii. 15-iv. 18", 239: "2 Thess. iii. 11-Heb. i. 13", 259: "Tit. i. 1-ii. 12",
    260: "Tit. ii. 13-iii. 15", 263: "Rev. i. 1-ii. 7", 264: "Rev. ii. 8-iii. 5",
    265: "Rev. iii. 5-iv. 8", 266: "Rev. iv. 8-vi. 7",
}

# NTVMR book abbreviations -> our book keys
NTVMR_BOOKS = {
    "Matt": "matt", "Mark": "mark", "Luke": "luke", "John": "john", "Acts": "acts",
    "Rom": "romans", "1Cor": "1cor", "2Cor": "2cor", "Gal": "gal", "Eph": "eph",
    "Phil": "phil", "Col": "col", "1Thess": "1thess", "2Thess": "2thess",
    "1Tim": "1tim", "2Tim": "2tim", "Titus": "titus", "Phlm": "philemon",
    "Heb": "hebrews", "Jas": "james", "1Pet": "1peter", "2Pet": "2peter",
    "1John": "1john", "2John": "2john", "3John": "3john", "Jude": "jude", "Rev": "rev",
}
# OSIS ids for CSNTM
OSIS = {
    "matt": "Matt", "mark": "Mark", "luke": "Luke", "john": "John", "acts": "Acts",
    "romans": "Rom", "1cor": "1Cor", "2cor": "2Cor", "gal": "Gal", "eph": "Eph",
    "phil": "Phil", "col": "Col", "1thess": "1Thess", "2thess": "2Thess",
    "1tim": "1Tim", "2tim": "2Tim", "titus": "Titus", "philemon": "Phlm",
    "hebrews": "Heb", "james": "Jas", "1peter": "1Pet", "2peter": "2Pet",
    "1john": "1John", "2john": "2John", "3john": "3John", "jude": "Jude", "rev": "Rev",
}
# Facsimile caption abbreviations (as printed by Kenyon 1909, OCR-normalised)
CAPTION_BOOKS = {
    "matt": "matt", "mark": "mark", "luke": "luke", "john": "john", "acts": "acts",
    "rom": "romans", "1cor": "1cor", "2cor": "2cor", "gal": "gal", "eph": "eph",
    "phil": "phil", "col": "col", "1thess": "1thess", "2thess": "2thess",
    "1tim": "1tim", "2tim": "2tim", "tit": "titus", "philem": "philemon",
    "heb": "hebrews", "jas": "james", "1pet": "1peter", "2pet": "2peter",
    "1john": "1john", "2john": "2john", "3john": "3john", "jude": "jude",
    "rev": "rev", "apoc": "rev",
}


# ---------------------------------------------------------------------------
# HTTP (explicit close; retries)
# ---------------------------------------------------------------------------
def http_bytes(url: str, headers: dict | None = None, timeout: int = 60, tries: int = 4) -> bytes:
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    last = None
    for attempt in range(tries):
        try:
            resp = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout)
            try:
                return resp.read()
            finally:
                resp.close()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed after {tries} tries: {url}: {last}")


def http_json(url: str, headers=None, timeout=60):
    return json.loads(http_bytes(url, headers, timeout).decode("utf-8"))


def cached_json(name: str, fetch):
    p = CACHE / name
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    data = fetch()
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


# ---------------------------------------------------------------------------
# NTVMR page index
# ---------------------------------------------------------------------------
def ntvmr_pages() -> list[dict]:
    """Ordered list of NTVMR pages from fol. 26r onward:
    {ordinal, pageID, folio, content, leaf}"""
    raw = cached_json("ntvmr_20002.json", lambda: http_json(NTVMR_URL))
    pages = raw["data"]["manuscript"]["pages"]["page"]
    out = []
    ordinal = 0
    for p in pages:
        pid = int(p["pageID"])
        if pid < 90:
            continue  # prefatory leaves (canon tables etc.), nothing indexed
        content = NTVMR_FIXES.get(pid, p.get("biblicalContent", "") or "")
        out.append(
            {
                "ordinal": ordinal,
                "pageID": pid,
                "folio": p.get("folio") or "",
                "content": content,
                "content_raw": p.get("biblicalContent", "") or "",
                "leaf": IA_LEAF_OFFSET + ordinal,
            }
        )
        ordinal += 1
    return out


RANGE_RE = re.compile(r"^(\S+)\s+(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?$")


def parse_content(content: str) -> list[tuple[str, int, int, int, int]]:
    """'Mark 15:37-47; Mark 16:1-16' -> [(book, c1, v1, c2, v2), ...]
    Ignores 'inscriptio'/'subscriptio'."""
    out = []
    for part in [x.strip() for x in content.split(";") if x.strip()]:
        if "inscriptio" in part or "subscriptio" in part:
            continue
        m = RANGE_RE.match(part)
        if not m:
            raise ValueError(f"cannot parse NTVMR content part: {part!r}")
        bk, c1, v1, c2, v2 = m.groups()
        c1, v1 = int(c1), int(v1)
        c2 = int(c2) if c2 else c1
        v2 = int(v2) if v2 else v1
        out.append((NTVMR_BOOKS[bk], c1, v1, c2, v2))
    return out


# ---------------------------------------------------------------------------
# Internet Archive facsimile leaves
# ---------------------------------------------------------------------------
def ia_leaf_path(leaf: int) -> Path:
    return CACHE / "ia" / f"leaf_{leaf:04d}.jpg"


def fetch_leaf(leaf: int) -> Path:
    p = ia_leaf_path(leaf)
    if p.exists() and p.stat().st_size > 50_000:
        return p
    data = http_bytes(IA_PAGE.format(item=IA_ITEM, leaf=leaf), timeout=120)
    Image.open(io.BytesIO(data)).verify()  # raises if not an image
    p.write_bytes(data)
    return p


def fetch_leaves(leaves: list[int], workers: int = 4):
    todo = [l for l in leaves if not ia_leaf_path(l).exists()]
    if not todo:
        return
    print(f"  downloading {len(todo)} facsimile leaves from archive.org ({workers} workers)")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_leaf, l): l for l in todo}
        for i, f in enumerate(as_completed(futs), 1):
            f.result()
            if i % 25 == 0:
                print(f"    {i}/{len(todo)}")


# ---------------------------------------------------------------------------
# OCR of the printed caption beneath each plate ("Matt. xxvi. 46-73")
# ---------------------------------------------------------------------------
ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}


def roman_to_int(s: str) -> int:
    s = s.lower()
    total, prev = 0, 0
    for ch in reversed(s):
        val = ROMAN[ch]
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total


OCR_STRATEGIES = [
    # (y0, y1, x0, x1, psm, autocontrast)
    (0.875, 0.958, 0.12, 0.88, 6, False),
    (0.80, 0.98, 0.10, 0.90, 11, False),
    (0.80, 0.98, 0.10, 0.90, 11, True),
    (0.80, 0.98, 0.10, 0.90, 6, True),
    (0.84, 0.97, 0.00, 1.00, 11, True),
    (0.86, 0.96, 0.15, 0.85, 7, True),
    (0.80, 0.98, 0.10, 0.90, 4, False),
]


def _caption_bands(im) -> list[tuple[int, int]]:
    """Locate the printed caption line on the paper margin below the plate by
    scanning row darkness in the bottom fifth of the leaf."""
    import numpy as np

    w, h = im.size
    y0 = int(h * 0.78)
    g = np.asarray(im.crop((int(w * 0.1), y0, int(w * 0.9), int(h * 0.99))).convert("L"), dtype=np.float32)
    rowmean = g.mean(axis=1)
    paper = rowmean > np.percentile(rowmean, 60)
    dark = (g < 110).sum(axis=1)
    cand = [i for i in range(len(rowmean)) if paper[i] and dark[i] > 3]
    if not cand:
        return []
    bands, start, prev = [], cand[0], cand[0]
    for i in cand[1:]:
        if i - prev > 6:
            bands.append((start, prev))
            start = i
        prev = i
    bands.append((start, prev))
    return [(y0 + a - 25, y0 + b + 25) for a, b in bands if 10 <= b - a <= 80]


def ocr_caption_variants(leaf: int) -> list[str]:
    """OCR the caption printed beneath a facsimile plate with several crops and
    contrast settings (its position and print density vary). Returns the list
    of OCR outputs. Cached."""
    cp = CACHE / "text" / f"caption_{leaf:04d}.json"
    if cp.exists():
        return json.loads(cp.read_text(encoding="utf-8"))
    from PIL import ImageFilter, ImageOps

    im = Image.open(fetch_leaf(leaf))
    w, h = im.size
    outs = []
    tmp = CACHE / "text" / f"strip_{leaf:04d}.png"

    def run(strip, psm):
        strip.save(tmp)
        try:
            res = subprocess.run(
                ["tesseract", str(tmp), "-", "-l", "eng", "--psm", str(psm)],
                capture_output=True, text=True, timeout=90,
            )
            outs.append(res.stdout)
        except Exception as e:  # noqa: BLE001
            outs.append(f"<<ocr failed: {e}>>")

    for (a, b) in _caption_bands(im):
        strip = im.crop((int(w * 0.1), a, int(w * 0.9), b)).convert("L")
        strip = ImageOps.autocontrast(strip, cutoff=1)
        strip = strip.resize((strip.width * 3, strip.height * 3), Image.LANCZOS).filter(ImageFilter.SHARPEN)
        run(strip, 7)
    for (y0, y1, x0, x1, psm, ac) in OCR_STRATEGIES:
        strip = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1))).convert("L")
        if ac:
            strip = ImageOps.autocontrast(strip, cutoff=2)
        strip = strip.resize((strip.width * 2, strip.height * 2), Image.LANCZOS)
        run(strip, psm)
    tmp.unlink(missing_ok=True)
    cp.write_text(json.dumps(outs, ensure_ascii=False), encoding="utf-8")
    return outs


TOKEN_RE = re.compile(
    r"(?:(?P<num>[1-3IrtT])\s?)?(?P<name>[A-Z][A-Za-z]{1,8})\.?\s*"
    r"(?:(?P<c>[ivxlcuIVXLC1]+)\.\s*)?(?P<v>[0-9IloOgQSz]{1,3})"
    r"|(?P<c2>[ivxlcuIVXLC1]+)\.\s*(?P<v2>[0-9IloOgQSz]{1,3})"
    r"|(?P<v3>[0-9IloOgQSz]{1,3})"
)
DIGIT_FIX = str.maketrans({"I": "1", "l": "1", "o": "0", "O": "0", "g": "9", "Q": "9", "S": "5", "z": "2"})
NUMBERED = {"cor": "cor", "thess": "thess", "thes": "thess", "tim": "tim", "pet": "pet", "peter": "pet", "john": "john"}
PLAIN = {
    "matt": "matt", "matth": "matt", "mat": "matt", "mark": "mark", "luke": "luke", "john": "john",
    "acts": "acts", "act": "acts", "rom": "romans", "roma": "romans", "gal": "gal", "eph": "eph",
    "ephes": "eph", "phil": "phil", "philem": "philemon", "philemon": "philemon", "col": "col",
    "colos": "col", "tit": "titus", "titus": "titus", "heb": "hebrews", "hebr": "hebrews",
    "jas": "james", "james": "james", "jude": "jude", "rev": "rev", "rey": "rev", "apoc": "rev",
}
NUMBERED_KEYS = {"cor": {"1": "1cor", "2": "2cor"}, "thess": {"1": "1thess", "2": "2thess"},
                 "tim": {"1": "1tim", "2": "2tim"}, "pet": {"1": "1peter", "2": "2peter"},
                 "john": {"1": "1john", "2": "2john", "3": "3john"}}
SINGLE_CHAPTER = {"philemon", "2john", "3john", "jude"}


def _roman(tok: str) -> int:
    # Old-style type + OCR: 'l', '1', 'I' inside a chapter numeral are 'i'; 'u' is 'ii'
    tok = tok.lower().replace("l", "i").replace("1", "i").replace("u", "ii")
    return roman_to_int(tok)


def _digits(tok: str) -> int:
    return int(tok.translate(DIGIT_FIX))


def _book(num: str | None, name: str) -> str | None:
    n = name.lower().rstrip(".")
    if num:
        d = {"I": "1", "r": "1", "t": "1", "T": "1"}.get(num, num)
        base = NUMBERED.get(n)
        return NUMBERED_KEYS[base].get(d) if base else None
    return PLAIN.get(n)


def parse_caption(txt: str) -> list[tuple[str, int, int, int, int]]:
    return _parse_caption(txt)[0]


def caption_span(txt: str) -> str:
    """The part of an OCR output that is the caption itself (noise trimmed)."""
    refs, start, end = _parse_caption(txt)
    t = " ".join(txt.split())
    return t[start:end] if refs else ""


def _parse_caption(txt: str):
    """Parse the OCR text of a facsimile caption ("Mark xv. 37—xvi. 16",
    "James v. 9—1 Peter i. 13", "3 John 1—Jude 12", "Philemon") into
    [(book, c1, v1, c2, v2)] with one tuple per book, first and last verse.
    Old-style figures and OCR confusions (I/l = 1, o = 0, g = 9, S = 5) are
    normalised. Bookless tokens inherit the book of the preceding token and
    must follow it within a few separator characters."""
    t = " ".join(txt.split())
    if re.search(r"Philemon", t) and not re.search(r"\d", t):
        i = t.index("Philemon")
        return [("philemon", 1, 1, 1, 25)], i, i + len("Philemon")
    refs: list[tuple[str, int, int]] = []
    last_end = None
    span_start = span_end = 0
    for m in TOKEN_RE.finditer(t):
        if m.group("name") and not (re.fullmatch(r"[ivxlcuIVXLC1]+", m.group("name")) and not m.group("num")):
            bk = _book(m.group("num"), m.group("name"))
            if not bk:
                continue
            try:
                c = _roman(m.group("c")) if m.group("c") else (1 if bk in SINGLE_CHAPTER else None)
                v = _digits(m.group("v"))
            except (KeyError, ValueError):
                continue
            if c is None:
                continue
            if not refs:
                span_start = m.start()
            refs.append((bk, c, v))
            last_end = span_end = m.end()
        elif refs and last_end is not None:
            gap = t[last_end:m.start()]
            if len(gap) > 5 or re.search(r"[A-Za-z0-9]", gap) or (gap and not re.search(r"[-\u2013\u2014]", gap)):
                last_end = None
                continue
            bk = refs[-1][0]
            try:
                if m.group("name"):  # an uppercase roman numeral read as a 'name' (e.g. 'XXI. 5')
                    c, v = _roman(m.group("name")), _digits(m.group("v"))
                elif m.group("c2"):
                    c, v = _roman(m.group("c2")), _digits(m.group("v2"))
                else:
                    if not re.search(r"[0-9I]", m.group("v3")):
                        last_end = None
                        continue
                    c, v = refs[-1][1], _digits(m.group("v3"))
            except (KeyError, ValueError):
                last_end = None
                continue
            refs.append((bk, c, v))
            last_end = span_end = m.end()
    if not refs:
        return [], 0, 0
    out = []
    # group consecutive refs by book: first ref and last ref of each book
    i = 0
    while i < len(refs):
        j = i
        while j + 1 < len(refs) and refs[j + 1][0] == refs[i][0]:
            j += 1
        out.append((refs[i][0], refs[i][1], refs[i][2], refs[j][1], refs[j][2]))
        i = j + 1
    return out, span_start, span_end


def _by_book(parts):
    d = {}
    for (bk, c1, v1, c2, v2) in parts:
        if bk in d:
            d[bk] = (d[bk][0], d[bk][1], c2, v2)
        else:
            d[bk] = (c1, v1, c2, v2)
    return d


def caption_matches(ntvmr: list, cap: list) -> bool:
    """The facsimile prints one overall range per page ("Mark xv. 37 - xvi. 16",
    "James v. 9 - 1 Peter i. 13"); NTVMR splits by chapter and book. The set of
    books must agree; the caption's first reference must equal NTVMR's first
    reference for that book and the caption's last reference NTVMR's last, with
    chapters exact and verses within one (a verse straddling two pages is
    credited to both pages by NTVMR but to only one by the caption)."""
    if not ntvmr or not cap:
        return False
    n = _by_book(ntvmr)
    books_c = []
    for x in cap:
        if x[0] not in books_c:
            books_c.append(x[0])
    if set(n) != set(books_c):
        return False
    first_b, last_b = cap[0][0], cap[-1][0]
    nc1, nv1 = n[first_b][0], n[first_b][1]
    nc2, nv2 = n[last_b][2], n[last_b][3]
    cc1, cv1 = cap[0][1], cap[0][2]
    cc2, cv2 = cap[-1][3], cap[-1][4]
    if (nc1, nc2) != (cc1, cc2):
        return False
    return abs(nv1 - cv1) <= 1 and abs(nv2 - cv2) <= 1


def verify_pages(pages: list[dict], verbose: bool = False) -> dict[int, dict]:
    """For every NTVMR page with biblical content, OCR the facsimile caption and
    compare. Returns {pageID: {"ok": bool, "caption": str, "parsed": [...]}}"""
    results = {}
    with_content = [p for p in pages if p["content"]]
    fetch_leaves([p["leaf"] for p in with_content])
    for p in with_content:
        want = parse_content(p["content"])
        variants = ocr_caption_variants(p["leaf"])
        ok, parsed, txt, method = False, [], "", "ocr"
        for txt_v in variants:
            parsed_v = parse_caption(txt_v)
            if caption_matches(want, parsed_v):
                ok, parsed, txt = True, parsed_v, caption_span(txt_v)
                break
            if parsed_v and not parsed:
                parsed, txt = parsed_v, txt_v
        if not ok and p["leaf"] in MANUAL_CAPTIONS:
            txt_m = MANUAL_CAPTIONS[p["leaf"]]
            parsed_m = parse_caption(txt_m)
            if caption_matches(want, parsed_m):
                ok, parsed, txt, method = True, parsed_m, txt_m, "read by eye"
        results[p["pageID"]] = {
            "ok": ok, "caption": " ".join(txt.split()), "parsed": parsed, "want": want, "method": method,
        }
        if verbose or not ok:
            print(f"  leaf {p['leaf']:3d} fol.{p['folio']:>5} NTVMR={p['content']!r:55} "
                  f"caption={' '.join(txt.split())[:80]!r} ({method}) -> {'OK' if ok else 'MISMATCH'}")
    n_ok = sum(1 for r in results.values() if r["ok"])
    print(f"  caption cross-check: {n_ok}/{len(results)} pages agree with NTVMR")
    return results


# ---------------------------------------------------------------------------
# CSNTM independent verse -> image index (second cross-check)
# ---------------------------------------------------------------------------
def csntm_lookup(book_key: str, chapter: int, verse: int) -> list[int]:
    key = f"{OSIS[book_key]}.{chapter}.{verse}"
    p = CACHE / "csntm_osis.json"
    idx = json.loads(p.read_text()) if p.exists() else {}
    if key in idx:
        return idx[key]
    url = (
        "https://manuscripts.csntm.org/manuscript/SearchForImageByOsis"
        f"?manuscriptId={CSNTM_MS_ID}&osis={urllib.parse.quote(key)}"
    )
    try:
        ids = http_json(url, headers={"Referer": CSNTM_REFERER}, timeout=20, )
    except Exception:  # noqa: BLE001
        ids = None
    idx[key] = ids
    p.write_text(json.dumps(idx))
    time.sleep(0.1)
    return ids


def csntm_image_names() -> dict[int, str]:
    p = CACHE / "csntm_ga02_images.json"
    if p.exists():
        return {int(k): v for k, v in json.loads(p.read_text()).items()}
    html = http_bytes(CSNTM_REFERER).decode("utf-8", errors="replace")
    names = re.findall(r'imageId="(\d+)" imageName="(GA_02_[^"]+)"', html)
    m = {int(i): n.strip() for i, n in names}
    p.write_text(json.dumps(m))
    return m


# ---------------------------------------------------------------------------
# Verse -> page map
# ---------------------------------------------------------------------------
def build_verse_map(pages: list[dict], verified: dict[int, dict]):
    """Return verse_pages[(book, ch)][verse] = [page dict, ...] using only pages
    whose facsimile caption agrees with NTVMR. Needs chapter verse counts for
    ranges that span chapters ('Mark 15:37-47; Mark 16:1-16' never spans, but
    'Rev 1:1-2:7' does)."""
    vm: dict[tuple[str, int], dict[int, list[dict]]] = {}
    spans = []
    for p in pages:
        if not p["content"] or not verified.get(p["pageID"], {}).get("ok"):
            continue
        for (bk, c1, v1, c2, v2) in parse_content(p["content"]):
            if c1 == c2:
                for v in range(v1, v2 + 1):
                    vm.setdefault((bk, c1), {}).setdefault(v, []).append(p)
            else:
                spans.append((p, bk, c1, v1, c2, v2))
    return vm, spans


def apply_spans(vm, spans, verse_count):
    for (p, bk, c1, v1, c2, v2) in spans:
        for v in range(v1, verse_count(bk, c1) + 1):
            vm.setdefault((bk, c1), {}).setdefault(v, []).append(p)
        for c in range(c1 + 1, c2):
            for v in range(1, verse_count(bk, c) + 1):
                vm.setdefault((bk, c), {}).setdefault(v, []).append(p)
        for v in range(1, v2 + 1):
            vm.setdefault((bk, c2), {}).setdefault(v, []).append(p)


# ---------------------------------------------------------------------------
# Scan file production
# ---------------------------------------------------------------------------
def folio_slug(p: dict) -> str:
    f = p["folio"] or f"p{p['pageID']}"
    m = re.match(r"^(\d+)([rv]?)([a-z]?)$", f)
    if m:
        num, side, extra = m.groups()
        return f"{int(num):03d}{extra}{side or ''}"
    return re.sub(r"[^a-z0-9]", "", f.lower())


def scan_name(p: dict) -> str:
    return f"alexandrinus/alex-f{folio_slug(p)}-leaf{p['leaf']:03d}.jpg"


def produce_scan(p: dict) -> Path:
    dest = SCAN_DIR.parent / scan_name(p)
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(fetch_leaf(p["leaf"])).convert("RGB")
    if im.width > 1800:
        im.thumbnail((1800, 1800 * 3))
    im.save(dest, "JPEG", quality=84, optimize=True)
    return dest


# ---------------------------------------------------------------------------
# Texts
# ---------------------------------------------------------------------------
def greek_chapter(book_key: str, chapter: int) -> dict[int, str]:
    bolls = CSP_BOOKS_NT[book_key][1]
    data = cached_json(f"text/tisch_{book_key}_{chapter}.json", lambda: fetch_tisch_chapter(bolls, chapter))
    return {int(v["verse"]): clean_strongs(v.get("text", "")) for v in data}


def kjv_chapter(book_key: str, chapter: int) -> dict[int, str]:
    name = CSP_BOOKS_NT[book_key][2]
    data = cached_json(f"text/kjv_{book_key}_{chapter}.json", lambda: fetch_kjv_chapter(name, chapter))
    return {int(v["verse"]): (v.get("text") or "").strip() for v in data.get("verses", [])}


def group_size(n: int) -> int:
    if n <= 20:
        return 5
    if n <= 40:
        return 8
    return 10


def fmt_range(nums: list[int]) -> str:
    return f"{nums[0]}-{nums[-1]}" if nums[0] != nums[-1] else str(nums[0])


def missing_ranges(missing: list[int]) -> str:
    if not missing:
        return ""
    runs, start, prev = [], missing[0], missing[0]
    for v in missing[1:]:
        if v == prev + 1:
            prev = v
            continue
        runs.append((start, prev))
        start = prev = v
    runs.append((start, prev))
    return ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in runs)


# ---------------------------------------------------------------------------
# Chapter builder
# ---------------------------------------------------------------------------
def build_chapter(book_key: str, chapter: int, vm, csntm_names, verified, force=False, prove=False):
    pretty = NT_BOOK_PRETTY[book_key]
    tid = f"verified-alexandrinus-{book_key}-{chapter}"
    pub_path = PUB_DIR / f"{tid}.json"
    if pub_path.exists() and not force:
        return ("skip", tid)

    pages_for = vm.get((book_key, chapter), {})
    if not pages_for:
        return ("absent", f"{tid}: no verified page carries any verse of this chapter")

    greek = greek_chapter(book_key, chapter)
    kjv = kjv_chapter(book_key, chapter)
    if not greek or not kjv:
        return ("fail", f"{tid}: Greek or KJV fetch empty")
    # KJV versification governs (it is what NTVMR and the facsimile captions use).
    all_verses = sorted(kjv)
    present = [v for v in all_verses if v in pages_for]
    missing = [v for v in all_verses if v not in pages_for]
    if not present:
        return ("absent", f"{tid}: chapter entirely missing from the manuscript")
    greek_extra = sorted(v for v in greek if v > max(all_verses))  # Tischendorf verses beyond KJV count
    numbering_differs = (sorted(greek) != all_verses)
    # Sections: contiguous runs of present verses, chunked.
    runs, cur = [], []
    for v in present:
        if cur and v != cur[-1] + 1:
            runs.append(cur)
            cur = []
        cur.append(v)
    if cur:
        runs.append(cur)
    gs = group_size(len(present))
    # chunk each run; a chunk with no Tischendorf verse at all (KJV has a verse
    # Tischendorf's numbering lacks, e.g. John 21:25) is merged into the
    # previous chunk so no section is left without Greek.
    chunks: list[list[int]] = []
    for run in runs:
        for i in range(0, len(run), gs):
            nums = run[i : i + gs]
            if chunks and not any(n in greek for n in nums) and chunks[-1][-1] == nums[0] - 1:
                chunks[-1] = chunks[-1] + nums
            else:
                chunks.append(nums)
    sections = []
    used_pages: dict[int, dict] = {}
    csntm_checks = []
    for nums in chunks:
        sec_pages: list[dict] = []
        for v in nums:
            for p in pages_for[v]:
                if p["pageID"] not in {q["pageID"] for q in sec_pages}:
                    sec_pages.append(p)
        for p in sec_pages:
            used_pages[p["pageID"]] = p
        # independent CSNTM cross-check on the first verse of the chapter's
        # first section (CSNTM answers slowly, ~20 s per lookup)
        if not csntm_checks:
            ids = csntm_lookup(book_key, chapter, nums[0])
            csntm_checks.append((nums[0], ids, [csntm_names.get(i, "?") for i in (ids or [])]))
        gnums = nums + (greek_extra if nums[-1] == present[-1] and present[-1] == all_verses[-1] else [])
        sections.append(
            {
                "section": f"{chapter}.{fmt_range(nums)}",
                "original_ref": f"{pretty} {chapter}:{fmt_range(nums)}",
                "original_text": " ".join(f"<sup>{n}</sup>{greek[n]}" for n in gnums if n in greek),
                "text": " ".join(f"<sup>{n}</sup>{kjv[n]}" for n in nums if n in kjv),
                "scan_pages": [scan_name(p) for p in sec_pages],
                "scan_folios": [
                    f"fol. {p['folio']} (facsimile leaf {p['leaf']}; NTVMR index: {p['content']}; "
                    f"printed caption: {verified[p['pageID']]['caption']})"
                    for p in sec_pages
                ],
            }
        )

    # scans
    for p in used_pages.values():
        dest = produce_scan(p)
        if dest.stat().st_size < 10_000:
            return ("fail", f"{tid}: scan too small {dest}")

    folios = [p["folio"] for p in sorted(used_pages.values(), key=lambda q: q["ordinal"])]
    lacuna_note = ""
    if missing:
        lacuna_note = (
            f"<p><strong>Lacuna:</strong> verses {missing_ranges(missing)} of this chapter are "
            f"not extant in Codex Alexandrinus (the leaves are lost); only the verses that "
            f"survive on the pages shown are published here.</p>"
        )
    numbering_note = ""
    if numbering_differs:
        numbering_note = (
            f"<p><strong>Numbering:</strong> Tischendorf's verse numbering in this chapter differs "
            f"from the KJV's ({len(greek)} Greek verses against {len(all_verses)} English); the Greek "
            f"verse numbers are Tischendorf's own and are not re-aligned.</p>"
        )
    intro = (
        f"<p>{pretty} {chapter} from <strong>Codex Alexandrinus</strong> (GA 02), a fifth-century "
        f"Greek Bible held by the British Library (Royal MS 1 D. VIII). In the New Testament it is "
        f"the chief witness to the Byzantine text in the Gospels and to the Alexandrian text in the "
        f"rest of the New Testament. Its New Testament volume lacks Matthew 1:1-25:5, John 6:50-8:52 "
        f"and 2 Corinthians 4:13-12:6.</p>"
        f"{lacuna_note}{numbering_note}"
        f"<p>This entry meets the strict three-criteria standard of the Theosis Library:</p><ol>"
        f"<li><strong>Manuscript scan:</strong> the actual page(s) of Codex Alexandrinus containing "
        f"this passage (folio{'s' if len(folios) > 1 else ''} {', '.join(folios)}), reproduced from "
        f"the British Museum's 1909 photographic facsimile edited by F. G. Kenyon, as digitised by the "
        f"Getty Research Institute for the Internet Archive. The facsimile prints the verse range "
        f"beneath each plate; that printed range was read for every page used and agrees with the "
        f"INTF's NTVMR verse-level page index (CC BY 4.0), which supplies the page for each section.</li>"
        f"<li><strong>Original text:</strong> Greek from Tischendorf's 8th critical edition (1869, "
        f"public domain). This is an edition, not a transcription of the manuscript: Alexandrinus is "
        f"written in unaccented majuscules with nomina sacra, and its readings differ from Tischendorf "
        f"in places. Where the two differ, the page image is what the manuscript actually says.</li>"
        f"<li><strong>English translation:</strong> the King James Version (1611), retrieved verbatim "
        f"from the public-domain bible-api.com endpoint.</li></ol>"
    )
    today = str(date.today())
    entry = {
        "id": tid,
        "title": f"{pretty}, Chapter {chapter} (Codex Alexandrinus)",
        "slug": tid,
        "language": "Greek (Tischendorf) / English (KJV)",
        "source": "Codex Alexandrinus via 1909 British Museum facsimile (Internet Archive) + NTVMR verse mapping + Tischendorf + KJV",
        "description": (
            f"{pretty} {chapter} from Codex Alexandrinus (5th c.). Page-specific folios via NTVMR, "
            f"verified against the facsimile's printed verse captions."
        ),
        "introduction": intro,
        "translator_notes": [],
        "translation": sections,
        "verification": {
            "scan_source": SCAN_SOURCE,
            "scan_license": SCAN_LICENSE,
            "scan_manuscript": "Codex Alexandrinus (British Library Royal MS 1 D. VIII, GA 02, 5th c.)",
            "scan_mapping": (
                "NTVMR verse-level page index for docID 20002 (INTF, CC BY 4.0), each page "
                "confirmed by OCR of the verse caption printed under the facsimile plate; "
                "first verse of the chapter also checked against CSNTM's GA_02 verse index"
            ),
            "scan_folios": folios,
            "scan_facsimile_leaves": [p["leaf"] for p in sorted(used_pages.values(), key=lambda q: q["ordinal"])],
            "scan_local_paths": [scan_name(p) for p in sorted(used_pages.values(), key=lambda q: q["ordinal"])],
            "page_captions": [
                {
                    "folio": p["folio"],
                    "facsimile_leaf": p["leaf"],
                    "ntvmr_index": p["content"],
                    "printed_caption": verified[p["pageID"]]["caption"],
                    "caption_read_by": verified[p["pageID"]]["method"],
                }
                for p in sorted(used_pages.values(), key=lambda q: q["ordinal"])
            ],
            "csntm_cross_check": [
                {
                    "verse": v,
                    "image_ids": ids,
                    "images": names,
                    **({} if ids else {"note": "CSNTM's GA_02 verse index has no entry for this verse (its index is incomplete for this book); the NTVMR index and the printed facsimile caption stand on their own"}),
                }
                for v, ids, names in csntm_checks
            ],
            "verses_absent_from_manuscript": missing_ranges(missing) if missing else "",
            "original_text_source": "bolls.life (TISCH = Tischendorf 8)",
            "original_text_license": "public domain (1869)",
            "original_text_note": "Critical edition text, not a transcription of the manuscript",
            "translation_source": "bible-api.com (KJV)",
            "translation_license": "public domain (1611)",
            "verified_date": today,
        },
    }
    if prove:
        print(json.dumps({k: v for k, v in entry.items() if k != "translation"}, indent=1, ensure_ascii=False))
        for s in sections:
            print("SECTION", s["section"], s["scan_pages"], s["scan_folios"])
            print("  GREEK:", s["original_text"][:300])
            print("  KJV  :", s["text"][:300])
        for p in used_pages.values():
            print("IMAGE URL:", IA_PAGE.format(item=IA_ITEM, leaf=p["leaf"]))
    pub_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return ("ok", tid)


def pending_meta(tid: str) -> dict:
    pub = json.loads((PUB_DIR / f"{tid}.json").read_text(encoding="utf-8"))
    return {
        "id": tid,
        "title": pub["title"],
        "author_id": "biblical-authors",
        "language": pub["language"],
        "era": "Apostolic",
        "tradition": "orthodox",
        "category": "sacred-text",
        "date_approx": "5th c. AD (Codex Alexandrinus)",
        "century": 5,
        "source": pub["source"],
        "description": pub["description"],
        "themes": ["bible", "new-testament", "alexandrinus", "verified"],
        "is_first_translation": False,
        "status": "published",
        "slug": tid,
        "scans": {
            "pages": [{"file": f, "caption": "Codex Alexandrinus"} for f in pub["verification"]["scan_local_paths"]]
        },
    }


def write_pending(ids: list[str]):
    PENDING.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if PENDING.exists():
        for t in json.loads(PENDING.read_text(encoding="utf-8"))["texts"]:
            existing[t["id"]] = t
    for tid in ids:
        existing[tid] = pending_meta(tid)
    PENDING.write_text(json.dumps({"texts": list(existing.values())}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  {PENDING} now lists {len(existing)} entries")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove", nargs=2, metavar=("BOOK", "CHAPTER"))
    ap.add_argument("--book")
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    pages = ntvmr_pages()
    print(f"NTVMR: {len(pages)} pages from fol. 26r; {sum(1 for p in pages if p['content'])} with biblical content")
    verified = verify_pages(pages, verbose=args.verbose)
    if args.verify_only:
        return

    vm, spans = build_verse_map(pages, verified)

    def verse_count(bk, ch):
        return max(kjv_chapter(bk, ch))

    apply_spans(vm, spans, verse_count)
    csntm_names = csntm_image_names()

    if args.prove:
        bk, ch = args.prove[0], int(args.prove[1])
        status, msg = build_chapter(bk, ch, vm, csntm_names, verified, force=True, prove=True)
        print(status, msg)
        if status == "ok":
            write_pending([msg])
        return

    todo = []
    if args.book and args.chapter:
        todo = [(args.book, args.chapter)]
    elif args.book:
        todo = [(args.book, c) for c in range(1, CSP_BOOKS_NT[args.book][3] + 1)]
    elif args.all:
        for bk, spec in CSP_BOOKS_NT.items():
            todo += [(bk, c) for c in range(1, spec[3] + 1)]
    ok, skip, absent, fail = [], [], [], []
    for bk, ch in todo:
        status, msg = build_chapter(bk, ch, vm, csntm_names, verified, force=args.force)
        {"ok": ok, "skip": skip, "absent": absent, "fail": fail}[status].append(msg)
        if status in ("ok",):
            print(f"  OK   {msg}")
        elif status == "fail":
            print(f"  FAIL {msg}")
    print(f"\nPublished: {len(ok)}  Skipped(existing): {len(skip)}  Absent: {len(absent)}  Failed: {len(fail)}")
    for a in absent:
        print("  absent:", a)
    for f in fail:
        print("  fail:", f)
    if ok:
        write_pending(ok)


if __name__ == "__main__":
    main()
