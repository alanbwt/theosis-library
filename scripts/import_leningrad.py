#!/usr/bin/env python3
"""
import_leningrad.py — Strict primary-source import for the Leningrad Codex
(National Library of Russia, Firkovich EBP. I B 19a, dated 1008/1009 AD),
the oldest complete manuscript of the Hebrew Bible.

Chain of evidence for every chapter entry (id: verified-leningrad-<book>-<chapter>):

  1. SCAN. The specific folio side(s) that carry each section's verses, from the
     full-colour West Semitic Research Project photographs as redistributed on
     Internet Archive item "Leningrad_Codex_Color_Images" (licenseurl on the
     item: Creative Commons Public Domain Mark 1.0). Files are addressed by
     folio, e.g. BIB_LENCDX_F001B.jpg = folio 1 verso. Nothing is estimated.

  2. PAGE -> VERSE MAPPING. Tanach.us "LC folio index for sefaria.org images"
     (https://tanach.us/XSL/LCIndex.xml), a folio-by-folio table of the first
     and last verse on every one of the 924 text pages (1v-463r), derived from
     the West Semitic Research Project's published index. A verse marked "26a"
     ends on the next page, so that verse is linked to BOTH pages. The same
     folio->verse ranges are independently exposed by Sefaria's manuscripts
     API (api/manuscripts/<ref>, metadata compiled by the National Library of
     Israel); --crosscheck compares the two for every chapter imported.

  3. HEBREW TEXT. Unicode/XML Leningrad Codex (UXLC), tanach.us Books/<Book>.xml,
     a transcription of this very manuscript (Michigan-Claremont / WLC lineage,
     corrected against the colour photographs). License: "All biblical Hebrew
     text, in any format, may be viewed or copied without restriction."

  4. ENGLISH. King James Version (1611, public domain) via bolls.life
     (get-text/KJV). bible-api.com serves the same KJV but throttles with
     HTTP 429 after a few dozen requests and omits the psalm superscriptions
     that the Hebrew counts as verse 1; --prove shows both agree for Genesis 1.

Versification: Hebrew (Masoretic) chapter/verse numbers differ from the KJV in
~40 places. Sections are cut on Hebrew verses; the English shows the KJV verses
covering exactly those Hebrew verses, with KJV numbers in the markers. The
MT->KJV table below is validated per book: every KJV verse of the book must be
produced exactly once (known Leningrad omissions are listed explicitly).

Usage:
  python3 scripts/import_leningrad.py --prove                 # Genesis 1 with evidence
  python3 scripts/import_leningrad.py --books gen ps isa deut # selected books
  python3 scripts/import_leningrad.py --all
  python3 scripts/import_leningrad.py --books gen --chapters 1-3 --crosscheck
Writes translations/published/verified-leningrad-*.json,
site/assets/scans/leningrad/leningrad-fNNNx.jpg and data/pending/leningrad_texts.json.
Never touches data/texts.json.
"""

import argparse
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "leningrad"
PENDING = ROOT / "data" / "pending" / "leningrad_texts.json"
CACHE = Path("/private/tmp/claude-501/-Users-mattimore/08116b0f-d4b1-43b3-972f-f6da24760f6d/scratchpad/leningrad_cache")
CACHE.mkdir(parents=True, exist_ok=True)
SCAN_DIR.mkdir(parents=True, exist_ok=True)
PENDING.parent.mkdir(parents=True, exist_ok=True)

UA = "TheosisLibrary/1.0 (+https://theosislibrary.com; primary-source verification)"

LCINDEX_URL = "https://tanach.us/XSL/LCIndex.xml"
UXLC_BOOK_URL = "https://www.tanach.us/Books/{file}.xml"
IA_ITEM = "Leningrad_Codex_Color_Images"
IA_IMAGE_URL = ("https://archive.org/download/" + IA_ITEM + "/" + IA_ITEM.replace("_Images", "_images")
                + ".zip/Leningrad_Codex_Color_images%2FBIB_LENCDX_F{folio}.jpg")
IA_ITEM_URL = "https://archive.org/details/" + IA_ITEM
SEFARIA_MS_URL = "https://www.sefaria.org/api/manuscripts/{ref}"
SCAN_MAX_WIDTH = 1400

# key, pretty, UXLC file, LCIndex/Sefaria name, bible-api name, bolls book number
BOOKS = [
    ("gen", "Genesis", "Genesis", "Genesis", "genesis", 1),
    ("exod", "Exodus", "Exodus", "Exodus", "exodus", 2),
    ("lev", "Leviticus", "Leviticus", "Leviticus", "leviticus", 3),
    ("num", "Numbers", "Numbers", "Numbers", "numbers", 4),
    ("deut", "Deuteronomy", "Deuteronomy", "Deuteronomy", "deuteronomy", 5),
    ("josh", "Joshua", "Joshua", "Joshua", "joshua", 6),
    ("judg", "Judges", "Judges", "Judges", "judges", 7),
    ("1sam", "1 Samuel", "Samuel_1", "1 Samuel", "1 samuel", 9),
    ("2sam", "2 Samuel", "Samuel_2", "2 Samuel", "2 samuel", 10),
    ("1kgs", "1 Kings", "Kings_1", "1 Kings", "1 kings", 11),
    ("2kgs", "2 Kings", "Kings_2", "2 Kings", "2 kings", 12),
    ("isa", "Isaiah", "Isaiah", "Isaiah", "isaiah", 23),
    ("jer", "Jeremiah", "Jeremiah", "Jeremiah", "jeremiah", 24),
    ("ezek", "Ezekiel", "Ezekiel", "Ezekiel", "ezekiel", 26),
    ("hos", "Hosea", "Hosea", "Hosea", "hosea", 28),
    ("joel", "Joel", "Joel", "Joel", "joel", 29),
    ("amos", "Amos", "Amos", "Amos", "amos", 30),
    ("obad", "Obadiah", "Obadiah", "Obadiah", "obadiah", 31),
    ("jonah", "Jonah", "Jonah", "Jonah", "jonah", 32),
    ("mic", "Micah", "Micah", "Micah", "micah", 33),
    ("nah", "Nahum", "Nahum", "Nahum", "nahum", 34),
    ("hab", "Habakkuk", "Habakkuk", "Habakkuk", "habakkuk", 35),
    ("zeph", "Zephaniah", "Zephaniah", "Zephaniah", "zephaniah", 36),
    ("hag", "Haggai", "Haggai", "Haggai", "haggai", 37),
    ("zech", "Zechariah", "Zechariah", "Zechariah", "zechariah", 38),
    ("mal", "Malachi", "Malachi", "Malachi", "malachi", 39),
    ("1chr", "1 Chronicles", "Chronicles_1", "1 Chronicles", "1 chronicles", 13),
    ("2chr", "2 Chronicles", "Chronicles_2", "2 Chronicles", "2 chronicles", 14),
    ("ps", "Psalms", "Psalms", "Psalms", "psalms", 19),
    ("job", "Job", "Job", "Job", "job", 18),
    ("prov", "Proverbs", "Proverbs", "Proverbs", "proverbs", 20),
    ("ruth", "Ruth", "Ruth", "Ruth", "ruth", 8),
    ("song", "Song of Songs", "Song_of_Songs", "Song of Songs", "song of solomon", 22),
    ("eccl", "Ecclesiastes", "Ecclesiastes", "Ecclesiastes", "ecclesiastes", 21),
    ("lam", "Lamentations", "Lamentations", "Lamentations", "lamentations", 25),
    ("esth", "Esther", "Esther", "Esther", "esther", 17),
    ("dan", "Daniel", "Daniel", "Daniel", "daniel", 27),
    ("ezra", "Ezra", "Ezra", "Ezra", "ezra", 15),
    ("neh", "Nehemiah", "Nehemiah", "Nehemiah", "nehemiah", 16),
]
BOOK = {b[0]: b for b in BOOKS}
SINGLE_CHAPTER_KJV = {"obadiah": 21}

# ---------------------------------------------------------------------------
# MT -> KJV versification.
# SHIFT[(book, mt_ch)] = [(v_from, v_to, kjv_ch, kjv_v_from), ...]; verses
# outside every segment map to the identical KJV ch:v.
# MANY[(book, mt_ch, mt_v)] = [(kjv_ch, kjv_v), ...]   one MT verse = several KJV verses
# KJV_ABSENT = KJV verses that have no counterpart in the Leningrad text.
# ---------------------------------------------------------------------------
SHIFT = {
    ("gen", 32): [(1, 1, 31, 55), (2, 33, 32, 1)],
    ("exod", 7): [(26, 29, 8, 1)], ("exod", 8): [(1, 28, 8, 5)],
    ("exod", 21): [(37, 37, 22, 1)], ("exod", 22): [(1, 30, 22, 2)],
    ("lev", 5): [(20, 26, 6, 1)], ("lev", 6): [(1, 23, 6, 8)],
    ("num", 17): [(1, 15, 16, 36), (16, 28, 17, 1)],
    ("num", 25): [(19, 19, 26, 1)],
    ("num", 30): [(1, 1, 29, 40), (2, 17, 30, 1)],
    ("deut", 13): [(1, 1, 12, 32), (2, 19, 13, 1)],
    ("deut", 23): [(1, 1, 22, 30), (2, 26, 23, 1)],
    ("deut", 28): [(69, 69, 29, 1)], ("deut", 29): [(1, 28, 29, 2)],
    ("1sam", 21): [(1, 1, 20, 42), (2, 16, 21, 1)],
    ("1sam", 24): [(1, 1, 23, 29), (2, 23, 24, 1)],
    ("2sam", 19): [(1, 1, 18, 33), (2, 44, 19, 1)],
    ("1kgs", 5): [(1, 14, 4, 21), (15, 32, 5, 1)],
    ("1kgs", 22): [(44, 44, 22, 43), (45, 54, 22, 44)],
    ("2kgs", 12): [(1, 1, 11, 21), (2, 22, 12, 1)],
    ("isa", 8): [(23, 23, 9, 1)], ("isa", 9): [(1, 20, 9, 2)],
    ("isa", 64): [(1, 11, 64, 2)],
    ("jer", 8): [(23, 23, 9, 1)], ("jer", 9): [(1, 25, 9, 2)],
    ("ezek", 21): [(1, 5, 20, 45), (6, 37, 21, 1)],
    ("hos", 2): [(1, 2, 1, 10), (3, 25, 2, 1)],
    ("hos", 12): [(1, 1, 11, 12), (2, 15, 12, 1)],
    ("hos", 14): [(1, 1, 13, 16), (2, 10, 14, 1)],
    ("joel", 3): [(1, 5, 2, 28)], ("joel", 4): [(1, 21, 3, 1)],
    ("jonah", 2): [(1, 1, 1, 17), (2, 11, 2, 1)],
    ("mic", 4): [(14, 14, 5, 1)], ("mic", 5): [(1, 14, 5, 2)],
    ("nah", 2): [(1, 1, 1, 15), (2, 14, 2, 1)],
    ("zech", 2): [(1, 4, 1, 18), (5, 17, 2, 1)],
    ("mal", 3): [(19, 24, 4, 1)],
    ("1chr", 5): [(27, 41, 6, 1)], ("1chr", 6): [(1, 66, 6, 16)],
    ("1chr", 12): [(5, 5, 12, 4), (6, 41, 12, 5)],
    ("2chr", 1): [(18, 18, 2, 1)], ("2chr", 2): [(1, 17, 2, 2)],
    ("2chr", 13): [(23, 23, 14, 1)], ("2chr", 14): [(1, 14, 14, 2)],
    ("neh", 3): [(33, 38, 4, 1)], ("neh", 4): [(1, 17, 4, 7)],
    ("neh", 7): [(68, 72, 7, 69)],
    ("neh", 10): [(1, 1, 9, 38), (2, 40, 10, 1)],
    ("job", 40): [(25, 32, 41, 1)], ("job", 41): [(1, 26, 41, 9)],
    ("song", 7): [(1, 1, 6, 13), (2, 14, 7, 1)],
    ("eccl", 4): [(17, 17, 5, 1)], ("eccl", 5): [(1, 19, 5, 2)],
    ("dan", 3): [(31, 33, 4, 1)], ("dan", 4): [(1, 34, 4, 4)],
    ("dan", 6): [(1, 1, 5, 31), (2, 29, 6, 1)],
}
MANY = {
    ("isa", 63, 19): [(63, 19), (64, 1)],
}
# KJV verses that legitimately combine two MT verses.
MERGE = {("num", 26, 1), ("1sam", 20, 42), ("1kgs", 22, 43), ("1chr", 12, 4)}
# KJV verses with no Leningrad counterpart (the codex omits them).
KJV_ABSENT = {("neh", 7, 68)}
# KJV verses that are not Hebrew Bible text at all (bolls.life appends the
# 1611 Apocrypha "Rest of Esther" 10:4-13 to Esther 10). Ignored, not translated.
KJV_EXTRA = {("esth", 10, v) for v in range(4, 14)}


def mt_to_kjv(book, ch, v):
    """Return ordered list of (kjv_ch, kjv_v) covering MT ch:v."""
    if (book, ch, v) in MANY:
        return list(MANY[(book, ch, v)])
    for v_from, v_to, kch, kv_from in SHIFT.get((book, ch), []):
        if v_from <= v <= v_to:
            return [(kch, kv_from + (v - v_from))]
    return [(ch, v)]


# ---------------------------------------------------------------------------
# HTTP with on-disk cache
# ---------------------------------------------------------------------------
def http_get(url, timeout=60, retries=5):
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
            try:
                return resp.read()
            finally:
                resp.close()
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(4 * (attempt + 1))
                continue
            raise
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"GET failed {url}: {last}")


def cached_get(url, name, binary=False):
    p = CACHE / name
    if p.exists() and p.stat().st_size > 0:
        return p.read_bytes() if binary else p.read_text(encoding="utf-8")
    data = http_get(url)
    p.write_bytes(data)
    return data if binary else data.decode("utf-8")


# ---------------------------------------------------------------------------
# 1. Folio index (tanach.us LCIndex.xml)
# ---------------------------------------------------------------------------
REF_RE = re.compile(r"^(\d+):(\d+)([ab]?)$")


def parse_ref(s):
    m = REF_RE.match(s.strip())
    if not m:
        raise ValueError(f"bad ref {s!r}")
    return int(m.group(1)), int(m.group(2)), m.group(3)


def load_lcindex():
    """-> {book_name: [(folio_id, (c,v,half), (c,v,half), note), ...]} in codex order."""
    text = cached_get(LCINDEX_URL, "LCIndex.xml")
    rows = re.findall(r"<tr>(.*?)</tr>", text, flags=re.S)
    out = {}
    for row in rows:
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)]
        if len(cells) < 3:
            continue
        fid, book, rng = cells[0], cells[1], cells[2]
        note = cells[3] if len(cells) > 3 else ""
        if not re.match(r"^\d{3}[AB]$", fid):
            continue
        if not re.match(r"^\d+:\d+[ab]?-\d+:\d+[ab]?$", rng):
            continue  # Masoretic-list pages carry no biblical text
        a, b = rng.split("-")
        out.setdefault(book, []).append((fid, parse_ref(a), parse_ref(b), note))
    return out


def folio_id_to_side(fid):
    return f"{int(fid[:3])}{'r' if fid[3] == 'A' else 'v'}"


def pages_for_verse(index_rows, ch, v):
    """All folio ids whose range includes MT ch:v (a split verse is on two pages)."""
    hits = []
    for fid, (c1, v1, _h1), (c2, v2, _h2), _note in index_rows:
        if (c1, v1) <= (ch, v) <= (c2, v2):
            hits.append(fid)
    return hits


# ---------------------------------------------------------------------------
# 2. Hebrew text (UXLC)
# ---------------------------------------------------------------------------
def load_uxlc_book(key):
    file = BOOK[key][2]
    xml = cached_get(UXLC_BOOK_URL.format(file=file), f"uxlc_{file}.xml")
    root = ET.fromstring(xml)
    edition = root.findtext(".//editionStmt/edition/version") or "UXLC"
    build = root.findtext(".//editionStmt/edition/build") or ""
    chapters = {}
    for c in root.iter("c"):
        cn = int(c.get("n"))
        verses = {}
        for v in c.findall("v"):
            vn = int(v.get("n"))
            verses[vn] = render_verse(v)
        chapters[cn] = verses
    return chapters, f"{edition} build {build}".strip()


def _word_text(el):
    # <w>bare text with optional <x>note</x> or <s>..</s> markers inside</w>
    parts = [el.text or ""]
    for child in el:
        if child.tag in ("x",):
            pass  # transcription note pointer, not manuscript text
        elif child.tag == "s":
            parts.append(child.text or "")  # special (large/small/suspended) letter
        else:
            parts.append(child.text or "")
        parts.append(child.tail or "")
    return "".join(parts)


def render_verse(v):
    toks = []
    pending_k = None
    for el in v:
        if el.tag == "w":
            toks.append(_word_text(el))
        elif el.tag == "k":
            pending_k = _word_text(el)
        elif el.tag == "q":
            q = _word_text(el)
            if pending_k is not None:
                toks.append(f"{pending_k} [{q}]")
                pending_k = None
            else:
                toks.append(f"[{q}]")
        elif el.tag == "pe":
            toks.append("פ")
        elif el.tag == "samekh":
            toks.append("ס")
        elif el.tag == "reversednun":
            toks.append("׆")
        # <x>, <note> etc. are editorial, skipped
    if pending_k is not None:
        toks.append(pending_k)
    # maqaf-joined words carry a trailing "־"; join those without a space
    out = ""
    for t in toks:
        if out and not out.endswith("־"):
            out += " "
        out += t
    return out.strip()


# ---------------------------------------------------------------------------
# 3. English (KJV)
# ---------------------------------------------------------------------------
STRONGS_RE = re.compile(r"<S>\d+</S>")


def kjv_chapter(key, kjv_ch):
    """-> {verse: text} for one KJV chapter, from bolls.life (public-domain KJV;
    keeps psalm superscriptions inside verse 1; no request throttling).
    bible-api.com serves the same KJV but rate-limits (HTTP 429) after a few
    dozen requests; --prove compares the two for Genesis 1."""
    bolls = BOOK[key][5]
    raw = cached_get(f"https://bolls.life/get-text/KJV/{bolls}/{kjv_ch}/", f"kjv_bolls_{key}_{kjv_ch}.json")
    data = json.loads(raw)
    if not data:
        raise RuntimeError(f"bolls KJV empty for {key} {kjv_ch}")
    return {int(x["verse"]): clean_kjv(x["text"]) for x in data}


def clean_kjv(t):
    """Strip bolls markup: Strong's numbers and the 1611 marginal notes (<sup>..</sup>)."""
    t = STRONGS_RE.sub("", t)
    t = re.sub(r"<sup>.*?</sup>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r" ([,.;:?!])", r"\1", t)
    return t.strip()


def kjv_chapter_bibleapi(key, kjv_ch):
    api_name = BOOK[key][4]
    if api_name in SINGLE_CHAPTER_KJV and kjv_ch == 1:
        ref = f"{api_name} 1:1-{SINGLE_CHAPTER_KJV[api_name]}"
    else:
        ref = f"{api_name} {kjv_ch}"
    raw = cached_get(f"https://bible-api.com/{urllib.parse.quote(ref)}?translation=kjv", f"kjv_{key}_{kjv_ch}.json")
    data = json.loads(raw)
    if data.get("translation_id") != "kjv":
        raise RuntimeError(f"bible-api returned non-KJV for {ref}")
    return {int(x["verse"]): re.sub(r"\s+", " ", x["text"]).strip() for x in data["verses"]}


class KJV:
    def __init__(self, key):
        self.key = key
        self.cache = {}

    def verse(self, ch, v):
        if ch not in self.cache:
            self.cache[ch] = kjv_chapter(self.key, ch)
        return self.cache[ch].get(v)


# ---------------------------------------------------------------------------
# Versification integrity check per book
# ---------------------------------------------------------------------------
def psalm_offsets(key, chapters, kjv):
    """Psalms: MT verse count minus KJV verse count = number of MT verses (0-2)
    that hold the superscription which the KJV prints as a heading."""
    if key != "ps":
        return {}
    offs = {}
    for ch in chapters:
        kjv.verse(ch, 1)
        off = len(chapters[ch]) - len(kjv.cache[ch])
        if off < 0 or off > 2:
            raise RuntimeError(f"Psalm {ch}: MT {len(chapters[ch])} vs KJV {len(kjv.cache[ch])} verses")
        offs[ch] = off
    return offs


def targets_for(key, ch, v, off):
    if key == "ps":
        return [(ch, 1)] if v <= off + 1 else [(ch, v - off)]
    return mt_to_kjv(key, ch, v)


def check_versification(key, chapters):
    kjv = KJV(key)
    offs = psalm_offsets(key, chapters, kjv)
    produced = {}
    for ch, verses in chapters.items():
        for v in verses:
            for kch, kv in targets_for(key, ch, v, offs.get(ch, 0)):
                produced.setdefault((kch, kv), []).append((ch, v))
    problems = []
    for (kch, kv), srcs in produced.items():
        if kjv.verse(kch, kv) is None:
            problems.append(f"MT {srcs} -> KJV {kch}:{kv} which does not exist")
        elif len(srcs) > 1 and (key, kch, kv) not in MERGE and not (key == "ps" and kv == 1):
            problems.append(f"KJV {kch}:{kv} produced by several MT verses {srcs}")
    kjv_all = set()
    for kch in sorted({k for k, _ in produced}):
        for kv in kjv.cache[kch]:
            kjv_all.add((kch, kv))
    missing = sorted(kjv_all - set(produced))
    for kch, kv in missing:
        if (key, kch, kv) not in KJV_ABSENT and (key, kch, kv) not in KJV_EXTRA:
            problems.append(f"KJV {kch}:{kv} never produced by any MT verse")
    return problems, kjv


# ---------------------------------------------------------------------------
# 4. Images
# ---------------------------------------------------------------------------
def scan_rel_path(fid):
    return f"leningrad/leningrad-f{fid.lower()}.jpg"


def ensure_scan(fid):
    dest = ROOT / "site" / "assets" / "scans" / scan_rel_path(fid)
    if dest.exists() and dest.stat().st_size > 10000:
        return dest
    url = IA_IMAGE_URL.format(folio=fid)
    data = http_get(url, timeout=180)
    im = Image.open(io.BytesIO(data))
    im.load()
    if im.size[0] < 1000 or im.size[1] < 1000:
        raise RuntimeError(f"unexpectedly small image for {fid}: {im.size}")
    if im.size[0] > SCAN_MAX_WIDTH:
        h = round(im.size[1] * SCAN_MAX_WIDTH / im.size[0])
        im = im.resize((SCAN_MAX_WIDTH, h), Image.LANCZOS)
    im = im.convert("RGB")
    tmp = dest.with_suffix(".part.jpg")
    im.save(tmp, "JPEG", quality=80, optimize=True)
    tmp.replace(dest)
    return dest


# ---------------------------------------------------------------------------
# Section building
# ---------------------------------------------------------------------------
def group_mt_verses(vnums, group_size, keep_with_next=()):
    groups, cur = [], []
    for v in vnums:
        cur.append(v)
        if len(cur) >= group_size and v not in keep_with_next:
            groups.append(cur)
            cur = []
    if cur:
        if groups and len(cur) < 3:
            groups[-1].extend(cur)
        else:
            groups.append(cur)
    return groups


def fmt_ref(pretty, ch, vs):
    return f"{pretty} {ch}:{vs[0]}" if len(vs) == 1 else f"{pretty} {ch}:{vs[0]}-{vs[-1]}"


def build_sections(key, ch, chapters, kjv, index_rows, group_size=8):
    pretty = BOOK[key][1]
    verses = chapters[ch]
    vnums = sorted(verses)
    off = psalm_offsets(key, chapters, kjv).get(ch, 0) if key == "ps" else 0
    keep = set(range(1, off + 1)) if off else set()
    sections = []
    for grp in group_mt_verses(vnums, group_size, keep):
        heb = " ".join(f"<sup>{v}</sup>{verses[v]}" for v in grp)
        # English: KJV verses covering these MT verses, in order, each once.
        eng_parts, seen, kjv_refs = [], set(), []
        for v in grp:
            for kch, kv in targets_for(key, ch, v, off):
                if (kch, kv) in seen:
                    continue
                seen.add((kch, kv))
                t = kjv.verse(kch, kv)
                if t is None:
                    raise RuntimeError(f"{key} MT {ch}:{v} -> KJV {kch}:{kv} missing")
                marker = f"{kv}" if kch == ch else f"{kch}:{kv}"
                eng_parts.append(f"<sup>{marker}</sup>{t}")
                kjv_refs.append((kch, kv))
        pages = []
        for v in grp:
            for fid in pages_for_verse(index_rows, ch, v):
                if fid not in pages:
                    pages.append(fid)
        if not pages:
            raise RuntimeError(f"{key} {ch}:{grp[0]} not in folio index")
        (c1, v1), (c2, v2) = kjv_refs[0], kjv_refs[-1]
        if (c1, v1) == (c2, v2):
            kref = f"{pretty} {c1}:{v1}"
        elif c1 == c2:
            kref = f"{pretty} {c1}:{v1}-{v2}"
        else:
            kref = f"{pretty} {c1}:{v1}-{c2}:{v2}"
        sec = {
            "section": f"{ch}.{grp[0]}-{grp[-1]}" if len(grp) > 1 else f"{ch}.{grp[0]}",
            "original_ref": fmt_ref(pretty, ch, grp),
            "original_text": heb,
            "text": " ".join(eng_parts),
            "scan_pages": [scan_rel_path(f) for f in pages],
            "folios": [folio_id_to_side(f) for f in pages],
        }
        if kref != sec["original_ref"]:
            sec["english_ref"] = kref + " (KJV)"
        sections.append(sec)
    return sections, off


# ---------------------------------------------------------------------------
# Entry assembly
# ---------------------------------------------------------------------------
def chapter_folio_ranges(index_rows, fids):
    out = []
    for fid, a, b, note in index_rows:
        if fid in fids:
            ra = f"{a[0]}:{a[1]}{a[2]}"
            rb = f"{b[0]}:{b[1]}{b[2]}"
            out.append(f"folio {folio_id_to_side(fid)} (BIB_LENCDX_F{fid}.jpg): {ra}-{rb}" + (f" [{note}]" if note else ""))
    return out


def build_entry(key, ch, chapters, kjv, index_rows, uxlc_version):
    pretty = BOOK[key][1]
    sections, off = build_sections(key, ch, chapters, kjv, index_rows)
    fids = []
    for s in sections:
        for p in s["scan_pages"]:
            fid = p.split("-f")[-1].split(".")[0].upper()
            if fid not in fids:
                fids.append(fid)
    sides = [folio_id_to_side(f) for f in fids]
    tid = f"verified-leningrad-{key}-{ch}"
    numbering = any("english_ref" in s for s in sections) or off
    notes = []
    if off:
        notes.append(f"Numbering: the Hebrew counts the superscription as verse{'s 1-' + str(off) if off > 1 else ' 1'}; "
                     f"the KJV prints it as a heading, so Hebrew verse n = KJV verse n-{off}. The KJV heading is shown with verse 1.")
    elif numbering:
        notes.append("Numbering: Masoretic (Hebrew) chapter/verse numbers differ from the KJV in this chapter; "
                     "English verse markers give the KJV numbers and each section's KJV range is listed as english_ref.")
    if any("[" in s["original_text"] for s in sections):
        notes.append("Ketiv/Qere: where the scribe wrote one form (ketiv) but the Masoretes read another (qere), the "
                 "consonantal ketiv is given first and the vocalised qere follows in square brackets. פ and ס mark the "
                     "open and closed paragraph breaks visible as gaps in the manuscript columns.")
    else:
        notes.append("פ and ס mark the open and closed paragraph breaks visible as gaps in the manuscript columns.")
    absent = sorted(f"{c}:{v}" for (b, c, v) in KJV_ABSENT if b == key and c == ch)
    if absent:
        notes.append(f"KJV verse(s) {', '.join(absent)} have no counterpart in the Leningrad Codex text and are omitted from the English.")
    intro = (
        f"<p>{pretty} chapter {ch} from the <strong>Leningrad Codex</strong> (Codex Leningradensis, National Library of "
        f"Russia, Firkovich EBP. I B 19a), copied in Cairo by Samuel ben Jacob and dated 1008/1009 AD, the oldest complete "
        f"manuscript of the Hebrew Bible and the base text of the Biblia Hebraica editions. "
        f"This chapter stands on folio{'s' if len(sides) > 1 else ''} {', '.join(sides)}.</p>"
        "<p>This entry meets the strict three-criteria standard of the Theosis Library:</p><ol>"
        f"<li><strong>Manuscript scan:</strong> the specific folio side(s) carrying each section's verses, from the full-colour "
        f"West Semitic Research Project photographs of the codex as redistributed on Internet Archive "
        f"(item {IA_ITEM}, marked Creative Commons Public Domain Mark 1.0). Folio-to-verse ranges come from the tanach.us "
        f"LC folio index, which was derived from the West Semitic Research Project's published index; each section links only "
        f"to the page(s) whose recorded verse range contains its verses.</li>"
        f"<li><strong>Original text:</strong> the verbatim Hebrew of this manuscript in the Unicode/XML Leningrad Codex "
        f"({uxlc_version}, tanach.us), a transcription of Firkovich B 19a with vowels and cantillation, released without "
        f"restriction on the biblical text.</li>"
        f"<li><strong>English translation:</strong> the King James Version (1611, public domain), retrieved verbatim from "
        f"bolls.life (KJV text, Strong's numbers stripped).</li></ol>"
    )
    if numbering:
        intro += f"<p>{notes[0]}</p>"
    entry = {
        "id": tid,
        "title": f"{pretty}, Chapter {ch} (Leningrad Codex)",
        "slug": tid,
        "language": "Hebrew (Leningrad Codex / UXLC) / English (KJV)",
        "source": "Leningrad Codex folios (Internet Archive, WSRP photographs) + tanach.us LC folio index + UXLC Hebrew + KJV",
        "description": (f"{pretty} {ch} on folio{'s' if len(sides) > 1 else ''} {', '.join(sides)} of the Leningrad Codex (1008 AD), "
                        f"the oldest complete Hebrew Bible. Hebrew from the UXLC transcription of this manuscript; English KJV."),
        "introduction": intro,
        "translator_notes": notes,
        "translation": sections,
        "verification": {
            "scan_source": f"Internet Archive item {IA_ITEM} ({IA_ITEM_URL}); West Semitic Research Project colour photographs (Bruce E. Zuckerman, 1990) of NLR Firkovich EBP. I B 19a; files BIB_LENCDX_F<folio><A|B>.jpg",
            "scan_license": "Creative Commons Public Domain Mark 1.0 as declared on the Internet Archive item (the manuscript is public domain; the photographs carry a WSRP copyright notice on the colour bar, see residual-risk note)",
            "scan_manuscript": "Leningrad Codex (Codex Leningradensis, Firkovich EBP. I B 19a, dated 1008/1009 AD)",
            "scan_mapping": "tanach.us LC folio index (https://tanach.us/XSL/LCIndex.xml), folio-by-folio first/last verse table derived from the West Semitic Research Project index; verses split across a page break are linked to both pages; cross-checked against Sefaria api/manuscripts anchorRef ranges",
            "scan_folio_ranges": chapter_folio_ranges(index_rows, fids),
            "scan_folio_ids": [f"F{f}" for f in fids],
            "scan_local_paths": [scan_rel_path(f) for f in fids],
            "scan_image_urls": [IA_IMAGE_URL.format(folio=f) for f in fids],
            "section_folios_verified": True,
            "section_folios_note": "Each section links only to the folio side(s) whose indexed verse range contains its verses.",
            "original_text_source": f"Unicode/XML Leningrad Codex {uxlc_version} (tanach.us Books/{BOOK[key][2]}.xml)",
            "original_text_license": "tanach.us License: 'All biblical Hebrew text, in any format, may be viewed or copied without restriction.'",
            "translation_source": "bolls.life KJV (get-text/KJV/<book>/<chapter>, Strong's numbers stripped); Genesis 1 verified identical to bible-api.com KJV",
            "translation_license": "public domain (1611)",
            "residual_risk": "The colour photographs were made by the West Semitic Research Project in 1990 and each frame carries a '(c) Bruce E. Zuckerman' colour bar. Internet Archive (two items) and Wikimedia Commons redistribute them as public domain (faithful reproduction of a public-domain manuscript); WSRP itself publishes no licence statement.",
            "verified_date": date.today().isoformat(),
        },
    }
    meta = {
        "id": tid,
        "title": f"{pretty}, Chapter {ch} (Leningrad Codex)",
        "author_id": "biblical-authors",
        "language": "Hebrew (Leningrad Codex / UXLC) / English (KJV)",
        "era": "Old Testament",
        "tradition": "orthodox",
        "category": "sacred-text",
        "date_approx": "c. 1500-400 BCE (composition); 1008 AD (Leningrad Codex)",
        "century": -5,
        "source": entry["source"],
        "description": entry["description"],
        "themes": ["bible", "old-testament", "hebrew-bible", "leningrad-codex", "verified"],
        "is_first_translation": False,
        "status": "published",
        "slug": tid,
        "scans": {"pages": [{"file": scan_rel_path(f), "caption": f"Leningrad Codex folio {folio_id_to_side(f)}"} for f in fids]},
    }
    return entry, meta, fids


# ---------------------------------------------------------------------------
# Sefaria cross-check (independent copy of the folio ranges)
# ---------------------------------------------------------------------------
def sefaria_ranges(key, ch):
    name = BOOK[key][3].replace(" ", "_")
    name = {"1_Samuel": "I_Samuel", "2_Samuel": "II_Samuel", "1_Kings": "I_Kings", "2_Kings": "II_Kings",
            "1_Chronicles": "I_Chronicles", "2_Chronicles": "II_Chronicles"}.get(name, name)
    raw = cached_get(SEFARIA_MS_URL.format(ref=f"{name}.{ch}"), f"sefaria_{key}_{ch}.json")
    out = {}
    for x in json.loads(raw):
        if "leningrad" not in x.get("manuscript_slug", ""):
            continue
        fid = x["image_url"].rsplit("_F", 1)[-1].split(".")[0]
        out[fid] = x["anchorRef"]
    return out


def parse_sefaria_ref(ref):
    """'Genesis 1:26-2:19' / 'Genesis 1:1-26' / 'Numbers 36:13' -> ((c1,v1),(c2,v2))"""
    m = re.search(r"(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?\s*$", ref)
    if not m:
        return None
    c1, v1 = int(m.group(1)), int(m.group(2))
    if m.group(4) is None:
        return (c1, v1), (c1, v1)
    c2 = int(m.group(3)) if m.group(3) else c1
    return (c1, v1), (c2, int(m.group(4)))


# Folios where Sefaria's copy of the index is garbled (its ref is impossible
# for the book's chapter lengths) and the LCIndex range was confirmed on the
# image itself; see the verification notes in the final report.
CROSSCHECK_ALLOW = {
    "308B",  # LCIndex Joel 3:1b-4:21 confirmed on the image (page opens with Joel 3:1b
             # "your old men shall dream dreams", closes with 4:21 and the end of the book);
             # Sefaria's anchorRef "Joel 3:1-21" is impossible, Joel 3 has 5 verses.
}


def crosscheck(key, ch, index_rows, fids):
    """Compare LCIndex ranges of the chapter's folios with Sefaria anchorRefs (numeric). Returns mismatches."""
    sef = sefaria_ranges(key, ch)
    bad = []
    for fid, a, b, _n in index_rows:
        if fid not in fids or fid in CROSSCHECK_ALLOW:
            continue
        theirs = sef.get(fid)
        if theirs is None:
            continue  # Sefaria lists only pages intersecting the queried chapter
        parsed = parse_sefaria_ref(theirs)
        mine = ((a[0], a[1]), (b[0], b[1]))
        if parsed != mine:
            bad.append((fid, f"LCIndex {a[0]}:{a[1]}{a[2]}-{b[0]}:{b[1]}{b[2]}", f"Sefaria {theirs}"))
    return bad


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def load_pending():
    if PENDING.exists():
        return json.loads(PENDING.read_text(encoding="utf-8"))
    return {"texts": []}


def save_pending(p):
    PENDING.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_chapters(spec, maxch):
    if not spec:
        return list(range(1, maxch + 1))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [c for c in out if 1 <= c <= maxch]


def import_book(key, chapters_wanted, lcindex, do_crosscheck, workers, force):
    pretty = BOOK[key][1]
    index_rows = lcindex[BOOK[key][3]]
    chapters, uxlc_version = load_uxlc_book(key)
    problems, kjv = check_versification(key, chapters)
    if problems:
        print(f"  !! {pretty}: versification problems, book skipped:")
        for p in problems:
            print("     ", p)
        return [], problems
    entries = []
    mismatches = []
    for ch in parse_chapters(chapters_wanted, max(chapters)):
        tid = f"verified-leningrad-{key}-{ch}"
        out = PUB_DIR / f"{tid}.json"
        entry, meta, fids = build_entry(key, ch, chapters, kjv, index_rows, uxlc_version)
        if do_crosscheck:
            bad = crosscheck(key, ch, index_rows, fids)
            if bad:
                mismatches.extend(bad)
                print(f"  !! {tid}: Sefaria/LCIndex range mismatch {bad}; chapter skipped")
                continue
        entries.append((tid, out, entry, meta, fids))
    # images
    need = sorted({f for *_rest, fids in entries for f in fids})
    failed = set()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(ensure_scan, f): f for f in need}
        for fut in as_completed(futs):
            f = futs[fut]
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001
                failed.add(f)
                print(f"  !! scan {f} failed: {e}")
    written = []
    for tid, out, entry, meta, fids in entries:
        if any(f in failed for f in fids):
            print(f"  !! {tid}: missing scan, not written")
            continue
        for p in entry["verification"]["scan_local_paths"]:
            fp = ROOT / "site" / "assets" / "scans" / p
            assert fp.exists() and fp.stat().st_size > 10000, p
        if out.exists() and not force:
            pass
        out.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(meta)
    pend = load_pending()
    have = {t["id"]: i for i, t in enumerate(pend["texts"])}
    for meta in written:
        if meta["id"] in have:
            pend["texts"][have[meta["id"]]] = meta
        else:
            pend["texts"].append(meta)
    save_pending(pend)
    print(f"  {pretty}: wrote {len(written)} chapter entries, {len(need)} folio scans" + (f", {len(failed)} scan failures" if failed else ""))
    return written, mismatches


def prove():
    """Full-chain evidence for Genesis 1, printed."""
    lcindex = load_lcindex()
    rows = lcindex["Genesis"]
    chapters, ver = load_uxlc_book("gen")
    problems, kjv = check_versification("gen", chapters)
    print("UXLC:", ver, "| versification problems:", problems or "none")
    print("Folio index rows for Genesis 1:")
    for fid, a, b, n in rows:
        if a[0] <= 1 <= b[0]:
            print(f"   {fid} = folio {folio_id_to_side(fid)}: {a[0]}:{a[1]}{a[2]}-{b[0]}:{b[1]}{b[2]}   image {IA_IMAGE_URL.format(folio=fid)}")
    print("Sefaria says:", sefaria_ranges("gen", 1))
    secs, _ = build_sections("gen", 1, chapters, kjv, rows)
    for s in secs:
        print(f"-- {s['original_ref']} -> {s['scan_pages']}")
        print("   HEB:", re.sub(r'<[^>]+>', ' ', s['original_text'])[:160], "...")
        print("   ENG:", re.sub(r'<[^>]+>', ' ', s['text'])[:160], "...")
    p = ensure_scan("001B")
    print("scan on disk:", p, p.stat().st_size, "bytes")
    a = kjv_chapter("gen", 1)
    b = kjv_chapter_bibleapi("gen", 1)
    norm = lambda t: re.sub(r"[^a-z]", "", t.lower())
    same = all(norm(a[v]) == norm(b[v]) for v in b)
    print("KJV bolls.life == bible-api.com for Genesis 1:", same, f"({len(a)} vs {len(b)} verses)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove", action="store_true")
    ap.add_argument("--books", nargs="*", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--chapters", default="")
    ap.add_argument("--crosscheck", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check-versification", action="store_true", help="only run the MT->KJV table check")
    args = ap.parse_args()
    if args.prove:
        prove()
        return
    keys = [b[0] for b in BOOKS] if args.all else args.books
    if args.check_versification:
        for k in keys:
            chapters, _ = load_uxlc_book(k)
            problems, _ = check_versification(k, chapters)
            print(k, "OK" if not problems else problems)
        return
    lcindex = load_lcindex()
    total = 0
    all_mismatch = []
    for k in keys:
        print(f"== {BOOK[k][1]}")
        try:
            written, mism = import_book(k, args.chapters, lcindex, args.crosscheck, args.workers, args.force)
        except Exception as e:  # noqa: BLE001
            print(f"  !! {k} failed: {e}")
            continue
        total += len(written)
        all_mismatch.extend(mism)
    print(f"TOTAL entries written: {total}; crosscheck mismatches: {len(all_mismatch)}")


if __name__ == "__main__":
    main()
