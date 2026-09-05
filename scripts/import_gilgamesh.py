#!/usr/bin/env python3
"""
import_gilgamesh.py -- Strict primary-source import for the Epic of Gilgamesh
(Standard Babylonian version), at the level of individual cuneiform tablets.

One "page" = one physical tablet (or joined tablet) from Ashurbanipal's library
at Nineveh, now in the British Museum.  For every published entry the chain is:

  1. SCAN      British Museum photograph of that very tablet (obverse + reverse
               where the tablet has text on both faces), served by the
               Electronic Babylonian Library (eBL, LMU Munich) fragment API.
               Licence as stated by eBL for BM objects:
               (c) The Trustees of the British Museum, CC BY-NC-SA 4.0.
  2. ORIGINAL  The eBL corpus edition of Gilgamesh (L.1.4, Standard Babylonian)
               gives, for every line of the poem, the ATF transliteration of
               each manuscript that carries the line, together with that
               manuscript's own column and line number.  We take ONLY the
               manuscript-level ATF of the photographed tablet -- i.e. the
               transliteration of the signs on that object -- never the
               composite reconstruction.  Licence: eBL editions are published
               under CC BY-NC-SA 4.0 (ebl.lmu.de/about/library).
  3. ENGLISH   R. Campbell Thompson, The Epic of Gilgamish (Luzac, London,
               1928): the last complete English translation that is public
               domain (published 1928 -> US public domain since 1 Jan 2024;
               Thompson d. 1941 -> UK/EU public domain since 2012).  Text taken
               from the sacred-texts.com transcription (via the Wayback
               Machine, because sacred-texts.com sits behind a bot challenge).
               Thompson's marginal line numbers are kept as <sup>T n</sup>.

Line-number honesty
-------------------
Modern line numbering follows A. R. George, The Babylonian Gilgamesh Epic
(OUP 2003) as used by eBL.  Thompson's 1928/1930 numbering differs:
  * Tablet I  : Thompson numbers by column (i 1 ...).  eBL records the Thompson
                1930 column/line for each modern line ("oldLineNumbers",
                reference RN2980), so the concordance is eBL's own.
  * Tablets VI, XI : Thompson numbers continuously per tablet, and the count
                drifts from George's by up to ~20 lines because of lines
                restored since 1930.  The concordance used here is an explicit
                anchor table (ANCHORS below), one anchor per Thompson marginal
                number, established by comparing Thompson's verse with the eBL
                normalised text line by line.  Sections are cut ONLY at anchor
                points, so every section's English is exactly the Thompson
                block(s) whose start and end lines correspond to the section's
                Akkadian lines.  Where a tablet's preserved text starts or ends
                inside a Thompson block, the whole block is given and the
                section note says so.
  * Tablet X  : NOT imported.  Thompson's Tablet X interleaves the Old
                Babylonian Meissner tablet with the Nineveh text and leaves
                columns IV-VI largely untranslated; an honest concordance was
                not achievable in this pass.

Usage:
  python3 scripts/import_gilgamesh.py --prove        # Tablet XI, K.3375 only, print evidence
  python3 scripts/import_gilgamesh.py                # all configured tablets
  python3 scripts/import_gilgamesh.py --tablets XI I # subset

Writes:
  translations/published/verified-gilgamesh-tablet-<N>-<museum>.json
  site/assets/scans/gilgamesh/gilgamesh-<museum>.jpg
  data/pending/gilgamesh_texts.json      (metadata to merge into data/texts.json)

Does NOT touch data/texts.json, templates, other entries, or run the renderer.
"""

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = PROJECT_ROOT / "translations" / "published"
SCAN_DIR = PROJECT_ROOT / "site" / "assets" / "scans" / "gilgamesh"
PENDING = PROJECT_ROOT / "data" / "pending" / "gilgamesh_texts.json"
CACHE = PROJECT_ROOT / ".cache" / "gilgamesh"
for d in (PUB_DIR, SCAN_DIR, PENDING.parent, CACHE):
    d.mkdir(parents=True, exist_ok=True)

EBL_API = "https://www.ebl.lmu.de/api"
# Thompson 1928 chapters on sacred-texts.com (Wayback snapshot; the live site
# serves a JavaScript challenge to non-browser clients).
THOMPSON_PAGES = {
    "I": "eog03.htm",
    "VI": "eog08.htm",
    "X": "eog12.htm",
    "XI": "eog13.htm",
}
WAYBACK = "https://web.archive.org/web/2024id_/https://sacred-texts.com/ane/eog/"

MAX_SCAN_SIDE = 3000  # px, longest side of the stored scan

# --------------------------------------------------------------------------
# Tablets and manuscripts.  Only Nineveh (Kuyunjik) tablets in the British
# Museum whose eBL photograph was inspected and shows every inscribed face
# that carries the columns transliterated for that manuscript.
# --------------------------------------------------------------------------
TABLETS = {
    "XI": {
        "title": "Tablet XI (the Flood)",
        "numbering": "continuous",
        "manuscripts": [
            # museum number, George 2003 siglum, note
            ("K.3375", "J₁", "The 'Flood Tablet' (BM K.3375), unjoined; columns ii-v"),
            ("K.2252", "C", "K.2252 + K.2602 + K.3321 + K.4486 + Sm.1881 (joined)"),
            ("K.8517", "W₁", "K.8517 + K.8518 + K.8569 + K.8593 + K.8595 (joined)"),
            ("K.7752", "T₁", "K.7752 + 1881,0204.245 + .296 + .460 (joined)"),
            ("Sm.2131", "T₂", "Sm.2131 + Sm.2196 + Rm-II.383 + Rm-II.390 + 1882,0522.316 (joined)"),
            ("Rm.616", "J₂", "Rm.616, column i"),
            ("K.8594", "W₂", "K.8594 + K.21502, column iii"),
            ("K.17343", "W₃", "K.17343 + K.21790 + Sm.1541, column iii"),
        ],
    },
    "I": {
        "title": "Tablet I (Gilgamesh and the creation of Enkidu)",
        "numbering": "columns",
        "manuscripts": [
            ("K.4465", "P", "K.4465 + K.9245 + K.22153 + Sm.2133 (joined)"),
            ("K.2756.D", "F₁", "K.2756D + K.20778 (joined)"),
            ("K.8584", "F₃", "K.8584, columns i-ii"),
            ("K.2756.C", "B₃", "K.2756C, column i"),
            ("K.7017", "F₂", "K.7017, columns iii-iv"),
            # K.913 (George B1) deliberately excluded: the eBL photograph shows one
            # face of the K.913 piece only, while the manuscript transliteration
            # (K.913 + K.2756 + K.2756E/F + K.6541 + 1881,0727.93) spans six
            # columns on both faces; text-to-photograph mapping not verifiable.
        ],
    },
    "VI": {
        "title": "Tablet VI (Ishtar and the Bull of Heaven)",
        "numbering": "continuous",
        "manuscripts": [
            ("K.231", "A₁", "K.231, six columns"),
            ("K.3990", "O₁", "K.3990 + K.4579 + DT.2 + Rm.578 + Rm-II.197 (joined)"),
            ("K.4579.A", "Q₁", "K.4579A + K.8018 (joined)"),
            ("Sm.2112", "O₂", "Sm.2112 + DT.unn.1 (joined)"),
            ("K.15193", "Q₃", "K.15193 + Sm.401 + Sm.423 + Sm.2194 (joined)"),
            ("K.5335", "A₂", "K.5335, columns iii-iv"),
        ],
    },
}

# Thompson marginal line number -> George/eBL line number (leading integer).
# Established by reading Thompson's verse against the eBL normalised text.
ANCHORS = {
    "XI": {
        1: 1, 5: 5, 10: 10, 20: 20, 25: 25, 30: 29, 35: 34, 40: 40, 45: 44,
        55: 55, 60: 60, 65: 65, 70: 70, 80: 81, 85: 86, 90: 90, 95: 95,
        100: 100, 105: 105, 115: 116, 120: 120, 125: 125, 130: 132, 135: 137,
        140: 141, 145: 147, 150: 151, 155: 157, 160: 160, 165: 167, 170: 172,
        175: 179, 180: 184, 185: 194, 190: 199, 195: 204, 200: 210, 205: 215,
        210: 220, 215: 225, 220: 232, 225: 237, 230: 243, 235: 248, 240: 253,
        245: 259, 250: 264, 255: 270, 260: 275, 265: 280, 270: 285, 275: 292,
        280: 297, 285: 303, 290: 308, 295: 312, 300: 318, 305: 326,
    },
    "VI": {
        1: 1, 5: 5, 10: 10, 15: 15, 20: 20, 25: 25, 30: 30, 35: 35, 40: 40,
        45: 45, 50: 50, 55: 55, 60: 60, 65: 65, 70: 70, 75: 75, 80: 80,
        85: 84, 90: 90, 95: 95, 100: 100, 105: 105, 110: 110, 130: 124,
        147: 141, 153: 147, 155: 149, 160: 153, 165: 156, 170: 160, 175: 164,
        180: 170, 185: 175, 190: 179,
    },
}

ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6}
ROMAN_R = {v: k for k, v in ROMAN.items()}
COL_WORDS = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}

TODAY = date.today().isoformat()


# --------------------------------------------------------------------------
# HTTP (curl: Python's urllib hangs ~75 s on this host trying IPv6 to ebl.lmu.de)
# --------------------------------------------------------------------------
def http_get(url, cache_name, binary=False, timeout=300):
    p = CACHE / cache_name
    if not p.exists() or p.stat().st_size == 0:
        subprocess.run(
            ["curl", "-4", "-sL", "--compressed", "-m", str(timeout),
             "-A", "Mozilla/5.0 TheosisLibrary/1.0 (+https://theosislibrary.com)",
             "-o", str(p), url],
            check=True,
        )
        if not p.exists() or p.stat().st_size == 0:
            raise RuntimeError(f"empty download: {url}")
    return p.read_bytes() if binary else p.read_text(encoding="utf-8", errors="replace")


def ebl_chapter(tablet):
    return json.loads(http_get(f"{EBL_API}/texts/L/1/4/chapters/SB/{tablet}", f"sb_{tablet}.json"))


def ebl_fragment(museum):
    return json.loads(http_get(f"{EBL_API}/fragments/{museum}", f"frag_{museum}.json"))


def ebl_photo(museum):
    return http_get(f"{EBL_API}/fragments/{museum}/photo", f"photo_{museum}.jpg", binary=True)


# --------------------------------------------------------------------------
# eBL corpus -> per-manuscript lines
# --------------------------------------------------------------------------
def lead_int(num):
    m = re.match(r"(\d+)", num)
    return int(m.group(1)) if m else None


def clean_atf(atf):
    """Manuscript ATF as printed by eBL, minus editorial '#note:' lines."""
    keep = [ln for ln in atf.split("\n") if ln.strip() and not ln.lstrip().startswith("#")]
    s = " ".join(keep)
    # eBL layout markers that are not signs: "$ line continues", "($___$)" (blank space)
    s = s.replace("$ line continues", "").replace("($___$)", "")
    s = re.sub(r"\$ (single|double|triple) ruling", "", s)
    s = re.sub(r"\s+", " ", s).strip(" :|").strip()
    return s


def manuscript_lines(chapter, museum):
    """[(idx, george_number, column_label, ms_line, atf, old_numbers)] for one manuscript."""
    mid = None
    for m in chapter["manuscripts"]:
        if m["museumNumber"] == museum:
            mid = m["id"]
            meta = m
    if mid is None:
        raise KeyError(f"{museum} not in chapter manuscripts")
    out = []
    for idx, line in enumerate(chapter["lines"]):
        for v in line["variants"]:
            for m in v["manuscripts"]:
                if m["manuscriptId"] != mid:
                    continue
                if not m["atf"].strip() or m["atf"].lstrip().startswith("$"):
                    continue
                atf = clean_atf(m["atf"])
                if not atf:
                    continue
                out.append({
                    "idx": idx,
                    "george": line["number"],
                    "col": " ".join(m["labels"]),
                    "ms_line": m["number"],
                    "atf": atf,
                    "old": [o["number"] for o in line.get("oldLineNumbers", [])
                            if o.get("reference", {}).get("id") == "RN2980"],
                })
    return meta, out


# --------------------------------------------------------------------------
# Thompson 1928 -> stream of items
# --------------------------------------------------------------------------
def thompson_stream(tablet):
    raw = http_get(WAYBACK + THOMPSON_PAGES[tablet], f"thompson_{tablet}.htm")
    body = re.split(r"<h3>Footnotes</h3>|<p><a name=\"fn_", raw, flags=re.I)[0]
    body = re.sub(r'<A NAME="page_\d+">.*?</A>', "", body, flags=re.S)
    body = re.sub(r'<A NAME="fr_\d+"></A><A HREF="#fn_\d+"><FONT SIZE="1">\d+</FONT></A>', "", body)
    body = re.sub(r'<A HREF="errata.htm#\d+">(.*?)</A>', r"\1", body)
    body = body.replace('<span class="margnote"><FONT SIZE="-1" COLOR="GREEN">', "\n@@").replace("</FONT></span>", "@@ ")
    body = re.sub(r"<br>", "\n", body)
    body = re.sub(r"</p>", "\n\n", body)
    body = re.sub(r'<p align="center">', "\n@C ", body)
    text = html.unescape(re.sub(r"<[^>]+>", "", body))
    for a, b in {"\x96": "-", "\x97": "—", "\x91": "‘", "\x92": "’", "\x93": "“", "\x94": "”"}.items():
        text = text.replace(a, b)

    items = []
    started = False
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if not started:
            if re.match(r"^THE .* TABLET", ln):
                started = True
            continue
        if ln == "Footnotes" or ln.startswith("Next:"):
            break
        if ln.startswith("@C"):
            body_ = ln[2:].strip()
            m = re.match(r"^Column ([IVX]+)\.?$", body_)
            if m:
                items.append(("col", COL_WORDS[m.group(1)]))
            elif body_ and not set(body_) <= set("_"):
                items.append(("note", body_))
            continue
        m = re.match(r"^@@(\d+)\.?@@\s*(.*)$", ln)
        if m:
            items.append(("marker", int(m.group(1))))
            if m.group(2).strip():
                items.append(("line", m.group(2).strip()))
            continue
        m = re.match(r"^(\d{1,3})\.?\s+(.*)$", ln)
        if m:  # marginal number that lost its span in the transcription
            items.append(("marker", int(m.group(1))))
            items.append(("line", m.group(2).strip()))
            continue
        if ln.startswith("(") and ln.endswith(")") and len(ln) > 40 and "Column" in ln:
            items.append(("note", ln))
            continue
        items.append(("line", ln))
    # monotonic repair of marginal numbers within a column (OCR slips such as
    # "150." for 180 in Tablet XI)
    fixed, prev = [], 0
    for kind, val in items:
        if kind == "col":
            prev = 0
        if kind == "marker":
            if val <= prev:
                new = prev + 5
                print(f"    [thompson {tablet}] marker {val} after {prev}: read as {new}")
                val = new
            prev = val
        fixed.append((kind, val))
    return fixed


# --------------------------------------------------------------------------
# Concordance -> blocks
# --------------------------------------------------------------------------
def build_blocks(tablet, chapter, stream):
    """Split Thompson's stream into blocks that start at an anchored marginal
    number.  Each block: {'tkey': label, 'g_idx': chapter line index where the
    block starts, 'items': [...]}.  Unanchored markers are absorbed into the
    preceding block (so blocks only ever begin at a verified anchor)."""
    lines = chapter["lines"]
    first_idx_by_int = {}
    for i, l in enumerate(lines):
        n = lead_int(l["number"])
        if n is not None and n not in first_idx_by_int:
            first_idx_by_int[n] = i
    idx_by_old = {}
    for i, l in enumerate(lines):
        for o in l.get("oldLineNumbers", []):
            if o.get("reference", {}).get("id") == "RN2980":
                idx_by_old.setdefault(o["number"], i)

    numbering = TABLETS[tablet]["numbering"]
    col = 0
    blocks = []
    cur = None

    def anchor_for(col, n):
        if numbering == "columns":
            key = f"{ROMAN_R[col]} {n}"
            if key in idx_by_old:
                return idx_by_old[key], f"{ROMAN_R[col]} {n}"
            return None, None
        g = ANCHORS[tablet].get(n)
        if g is None:
            return None, None
        return first_idx_by_int.get(g), str(n)

    for kind, val in stream:
        if kind == "col":
            col = val
            g_idx, label = anchor_for(col, 1)
            if g_idx is not None:
                cur = {"tkey": label, "g_idx": g_idx, "items": [], "col": col}
                blocks.append(cur)
            continue
        if kind == "marker":
            if numbering == "continuous" and val == 1:
                continue
            g_idx, label = anchor_for(col, val)
            if g_idx is not None and (cur is None or g_idx > cur["g_idx"]):
                cur = {"tkey": label, "g_idx": g_idx, "items": [], "col": col}
                blocks.append(cur)
            elif cur is not None:
                cur["items"].append(("marker", val))
            continue
        if cur is None:
            if numbering == "continuous" and not blocks:
                cur = {"tkey": "1", "g_idx": first_idx_by_int[1], "items": [], "col": col}
                blocks.append(cur)
            else:
                continue  # text before the first anchor of a column: unusable
        cur["items"].append((kind, val))

    blocks.sort(key=lambda b: b["g_idx"])
    for i, b in enumerate(blocks):
        b["g_end"] = blocks[i + 1]["g_idx"] - 1 if i + 1 < len(blocks) else len(lines) - 1
        b["has_verse"] = any(k == "line" for k, _ in b["items"])
        # Thompson-side end label: next block's marginal number minus one (same column)
        b["t_end"] = "end"
        if i + 1 < len(blocks):
            nxt = blocks[i + 1]
            a = re.match(r"^(?:([ivx]+) )?(\d+)$", b["tkey"])
            c = re.match(r"^(?:([ivx]+) )?(\d+)$", nxt["tkey"])
            if a and c and a.group(1) == c.group(1):
                b["t_end"] = str(int(c.group(2)) - 1)
            elif c and c.group(1):
                b["t_end"] = f"end of col. {a.group(1) if a and a.group(1) else ''}".strip()
    return blocks


def render_block_english(block, marker_prefix):
    """Thompson block -> HTML.  <sup>T n</sup> marks his marginal numbers."""
    parts = []
    cur_lines = []
    label = block["tkey"]

    def flush():
        if cur_lines:
            parts.append("<p>" + "<br>\n".join(cur_lines) + "</p>")
            cur_lines.clear()

    first = True
    for kind, val in block["items"]:
        if kind == "note":
            flush()
            parts.append(f"<p><i>{html.escape(val, quote=False)}</i></p>")
        elif kind == "marker":
            cur_lines.append(f"<sup>{marker_prefix}{val}</sup>")
        elif kind == "line":
            txt = html.escape(val, quote=False)
            if first:
                txt = f"<sup>{marker_prefix}{label}</sup>" + txt
                first = False
            elif cur_lines and cur_lines[-1].startswith("<sup>") and cur_lines[-1].endswith("</sup>"):
                cur_lines[-1] = cur_lines[-1] + txt
                continue
            cur_lines.append(txt)
    flush()
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Scans
# --------------------------------------------------------------------------
def save_scan(museum):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    dest = SCAN_DIR / f"gilgamesh-{museum}.jpg"
    if dest.exists() and dest.stat().st_size > 10000:
        return dest
    src = CACHE / f"photo_{museum}.jpg"
    ebl_photo(museum)
    im = Image.open(src)
    im = im.convert("RGB")
    im.thumbnail((MAX_SCAN_SIDE, MAX_SCAN_SIDE))
    im.save(dest, "JPEG", quality=85, optimize=True)
    return dest


# --------------------------------------------------------------------------
# Entry assembly
# --------------------------------------------------------------------------
def face_of(col):
    n = ROMAN.get(col)
    if n is None:
        return ""
    return "obverse" if n <= 3 else "reverse"


def build_entry(tablet, museum, siglum, ms_note, chapter, blocks, prove=False):
    meta, lines = manuscript_lines(chapter, museum)
    if not lines:
        print(f"  !! {museum}: no manuscript lines in eBL chapter, skipping")
        return None
    frag = ebl_fragment(museum)
    if not frag.get("hasPhoto"):
        print(f"  !! {museum}: eBL has no photograph, skipping")
        return None
    if frag.get("museum") != "THE_BRITISH_MUSEUM":
        print(f"  !! {museum}: not a British Museum object ({frag.get('museum')}), licence not established, skipping")
        return None
    scan = save_scan(museum)
    if scan.stat().st_size < 10000:
        print(f"  !! {museum}: scan too small, skipping")
        return None
    scan_rel = f"gilgamesh/{scan.name}"

    # group the manuscript's lines by column, then cut at every second block start
    by_col = {}
    for l in lines:
        by_col.setdefault(l["col"], []).append(l)
    block_starts = sorted(b["g_idx"] for b in blocks)
    cut_points = set(block_starts[::2])

    def block_range_for(a_idx, b_idx):
        return [b for b in blocks if b["g_idx"] <= b_idx and b["g_end"] >= a_idx]

    sections = []
    dropped = []
    for col, col_lines in by_col.items():
        col_lines.sort(key=lambda l: l["idx"])
        chunk = []
        chunks = []
        for l in col_lines:
            if chunk and l["idx"] in cut_points:
                chunks.append(chunk)
                chunk = []
            chunk.append(l)
        if chunk:
            chunks.append(chunk)
        for ch in chunks:
            a, b = ch[0]["idx"], ch[-1]["idx"]
            bl = block_range_for(a, b)
            bl_verse = [x for x in bl if x["has_verse"]]
            g_first, g_last = ch[0]["george"], ch[-1]["george"]
            joiner = " to " if ("-" in g_first or "-" in g_last) else "-"
            ref_lines = f"SB {tablet} {g_first}" + (f"{joiner}{g_last}" if g_last != g_first else "")
            if not bl_verse:
                dropped.append((col, ref_lines))
                continue
            english = "\n".join(render_block_english(x, "T ") for x in bl)
            t_first, t_last = bl[0]["tkey"], bl[-1]["t_end"]
            t_label = f"Thompson ll. {t_first} to {t_last}" if t_last != "end" else f"Thompson ll. {t_first} to end"
            notes = []
            spill_before = bl[0]["g_idx"] < a
            spill_after = bl[-1]["g_end"] > b
            if spill_before or spill_after:
                notes.append(
                    "Thompson's numbered block(s) extend "
                    + ("before " if spill_before else "")
                    + ("and " if spill_before and spill_after else "")
                    + ("after " if spill_after else "")
                    + "the lines preserved on this tablet; the whole block is given so that no English line is cut mid-block."
                )
            orig = "<br>\n".join(f"<sup>{html.escape(l['george'], quote=False)}</sup>{html.escape(l['atf'], quote=False)}" for l in ch)
            ms_first, ms_last = ch[0]["ms_line"], ch[-1]["ms_line"]
            face = face_of(col)
            section_label = f"{museum} col. {col or '?'} ({face}) ll. {ms_first}-{ms_last}" if col else f"{museum} ll. {ms_first}-{ms_last}"
            sections.append({
                "section": ref_lines,
                "original_ref": f"{section_label} = {ref_lines} (George/eBL numbering); English: {t_label} (Thompson 1928 numbering)",
                "original_text": orig,
                "text": english + ("\n<p><i>" + " ".join(notes) + "</i></p>" if notes else ""),
                "scan_pages": [scan_rel],
                "_sort": a,
            })
    sections.sort(key=lambda s: s["_sort"])
    for s in sections:
        del s["_sort"]
    if not sections:
        print(f"  !! {museum}: no publishable sections")
        return None

    cols = sorted({l["col"] for l in lines if l["col"]}, key=lambda c: ROMAN.get(c, 9))
    n_lines = len(lines)
    tid = f"verified-gilgamesh-tablet-{tablet}-{museum.replace('.', '-').lower()}"
    title = f"Epic of Gilgamesh, {TABLETS[tablet]['title']}: tablet {museum}"
    desc = (f"Standard Babylonian Epic of Gilgamesh, Tablet {tablet}, as written on British Museum tablet {museum} "
            f"(Nineveh, Library of Ashurbanipal, 7th c. BCE; George 2003 manuscript {siglum}; {ms_note}). "
            f"{n_lines} lines preserved in column(s) {', '.join(cols)}. Akkadian is the eBL transliteration of this tablet; "
            f"English is R. Campbell Thompson (1928).")
    intro = (
        f"<p>Tablet {tablet} of the <strong>Epic of Gilgamesh</strong> (Standard Babylonian version, attributed to "
        f"Sin-leqi-unninni) as it survives on one physical object: British Museum tablet <strong>{museum}</strong> "
        f"({ms_note}), excavated at Nineveh from the library of Ashurbanipal (7th c. BCE). It is manuscript "
        f"{siglum} in A. R. George's 2003 edition. The photograph is the British Museum's, showing the inscribed "
        f"face(s) and edges; column(s) {', '.join(cols)} are preserved ({n_lines} lines).</p>"
        "<p>Three criteria are met for every section:</p><ol>"
        f"<li><strong>Manuscript scan</strong>: the British Museum photograph of {museum} itself (served by the "
        "Electronic Babylonian Library, LMU Munich). Each section names the column and face (obverse = columns "
        "i-iii, reverse = columns iv-vi) and the tablet's own line numbers, so the reader can find the lines on "
        "the photograph.</li>"
        "<li><strong>Original text</strong>: the eBL manuscript-level ATF transliteration of the signs on this "
        "tablet (not the composite text). Brackets [ ] mark broken signs, x an illegible sign, # a damaged sign. "
        "Superscript numbers are the modern line numbers of George 2003 / eBL.</li>"
        "<li><strong>Public-domain English</strong>: R. Campbell Thompson, <em>The Epic of Gilgamish</em> "
        "(London, 1928), verbatim, with his marginal line numbers as <sup>T n</sup>.</li></ol>"
        "<p><strong>On line numbers.</strong> Thompson's 1928 numbering is not George's. "
        + ("For Tablet I the eBL edition records Thompson's 1930 column/line number for each modern line, and that "
           "concordance is used here." if tablet == "I" else
           "For this tablet the correspondence was established one anchor per Thompson marginal number by reading his "
           "verse against the Akkadian; sections are cut only at those anchors, so each section's English is the "
           "block of Thompson's lines that renders exactly these Akkadian lines.")
        + " Where the tablet's text begins or ends inside a Thompson block, the whole block is given and the "
        "section says so. Thompson's readings reflect the state of knowledge in 1928: modern editions "
        "(George 2003; the eBL edition, updated continuously) supersede him and are not public domain, so they "
        "are not reproduced here beyond the transliteration of this tablet's signs.</p>"
    )
    entry = {
        "id": tid,
        "title": title,
        "slug": tid,
        "language": "Akkadian (transliteration) / English",
        "source": f"British Museum {museum} photograph via eBL + eBL manuscript ATF (L.1.4 SB {tablet}) + R. Campbell Thompson 1928",
        "description": desc,
        "introduction": intro,
        "translator_notes": [],
        "translation": sections,
        "verification": {
            "scan_source": f"Electronic Babylonian Library fragment photo API: {EBL_API}/fragments/{museum}/photo (British Museum photograph); eBL page https://www.ebl.lmu.de/library/{museum}; CDLI {frag.get('externalNumbers', {}).get('cdliNumber', '')}",
            "scan_license": "(c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (as stated by eBL for British Museum objects)",
            "scan_manuscript": f"British Museum {museum} ({ms_note}), Nineveh, Neo-Assyrian, 7th c. BCE; George 2003 ms. {siglum}",
            "scan_local_paths": [scan_rel],
            "scan_mapping": "eBL corpus edition L.1.4 (Poem of Gilgamesh), Standard Babylonian, chapter "
                            f"{tablet}: every poem line lists the manuscripts carrying it with the manuscript's own column and line number; "
                            f"this entry uses only the lines attributed to {museum}. Obverse = cols i-iii, reverse = cols iv-vi.",
            "original_text_source": f"eBL corpus API {EBL_API}/texts/L/1/4/chapters/SB/{tablet}, manuscript ATF for {museum}; edition based on George 2003 with later joins",
            "original_text_license": "CC BY-NC-SA 4.0 (eBL editions, https://www.ebl.lmu.de/about/library)",
            "translation_source": "R. Campbell Thompson, The Epic of Gilgamish (Luzac, London, 1928); sacred-texts.com transcription "
                                  f"via Wayback Machine ({WAYBACK}{THOMPSON_PAGES[tablet]})",
            "translation_license": "public domain (published 1928: US PD since 2024; author d. 1941: UK/EU PD since 2012)",
            "translation_concordance": ("eBL oldLineNumbers (Thompson 1930, RN2980) per line" if tablet == "I"
                                        else "explicit anchor table in scripts/import_gilgamesh.py (ANCHORS), one anchor per Thompson marginal number"),
            "dropped_line_ranges_without_pd_english": [f"col. {c}: {r}" for c, r in dropped],
            "verified_date": TODAY,
        },
    }
    if prove:
        print("\n===== PROOF OF CHAIN =====")
        print(f"Tablet {tablet}, manuscript {museum} (George {siglum})")
        print(f"Photo URL   : {EBL_API}/fragments/{museum}/photo  -> {scan}  ({scan.stat().st_size} bytes)")
        print(f"Fragment    : https://www.ebl.lmu.de/library/{museum}  museum={frag.get('museum')} hasPhoto={frag.get('hasPhoto')} CDLI={frag.get('externalNumbers', {}).get('cdliNumber')}")
        print(f"BM licence  : {entry['verification']['scan_license']}")
        print(f"Columns     : {cols}; {n_lines} lines; first={lines[0]['george']} (col {lines[0]['col']} ms line {lines[0]['ms_line']}), last={lines[-1]['george']}")
        s = sections[0]
        print(f"Section 1   : {s['original_ref']}")
        print("Akkadian    :\n" + html.unescape(re.sub(r'<br>', '', s['original_text']))[:900])
        print("English     :\n" + re.sub(r'<[^>]+>', '', s['text'])[:900])
        if dropped:
            print(f"Dropped (no Thompson English): {dropped}")
        print("==========================\n")
    return entry, dropped


def texts_entry(entry, tablet, museum):
    return {
        "id": entry["id"],
        "title": entry["title"],
        "author_id": "sin-leqi-unninni",
        "language": "Akkadian",
        "era": "Ancient Near East",
        "tradition": "mesopotamian",
        "category": "literature",
        "date_approx": "c. 1200 BCE (composition); tablet 7th c. BCE (Nineveh)",
        "century": -12,
        "source": entry["source"],
        "description": entry["description"],
        "themes": ["gilgamesh", "mesopotamian", "akkadian", "cuneiform", "nineveh", "ashurbanipal", f"tablet-{tablet.lower()}", "verified"],
        "is_first_translation": False,
        "status": "published",
        "slug": entry["slug"],
        "scans": {"pages": [{"file": p, "caption": f"British Museum {museum}"} for p in entry["verification"]["scan_local_paths"]]},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tablets", nargs="*", default=list(TABLETS.keys()))
    ap.add_argument("--prove", action="store_true", help="only Tablet XI / K.3375, print the evidence chain")
    args = ap.parse_args()

    pending = []
    report = []
    targets = {"XI": [TABLETS["XI"]["manuscripts"][0]]} if args.prove else {t: TABLETS[t]["manuscripts"] for t in args.tablets}
    for tablet, mss in targets.items():
        print(f"== Tablet {tablet}")
        chapter = ebl_chapter(tablet)
        stream = thompson_stream(tablet)
        blocks = build_blocks(tablet, chapter, stream)
        print(f"   eBL lines: {len(chapter['lines'])}; Thompson blocks anchored: {len(blocks)} "
              f"({sum(1 for b in blocks if b['has_verse'])} with verse)")
        for museum, siglum, note in mss:
            res = build_entry(tablet, museum, siglum, note, chapter, blocks, prove=args.prove)
            if not res:
                report.append((tablet, museum, "SKIPPED"))
                continue
            entry, dropped = res
            out = PUB_DIR / f"{entry['id']}.json"
            out.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
            pending.append(texts_entry(entry, tablet, museum))
            n_sec = len(entry["translation"])
            n_lines = sum(s["original_text"].count("<sup>") for s in entry["translation"])
            report.append((tablet, museum, f"{n_sec} sections, {n_lines} Akkadian lines, dropped={len(dropped)}"))
            print(f"   {museum:10} -> {out.name}: {n_sec} sections, {n_lines} lines; dropped {len(dropped)} range(s) lacking PD English")

    if pending and not args.prove:
        existing = {"texts": []}
        if PENDING.exists():
            existing = json.loads(PENDING.read_text(encoding="utf-8"))
        ids = {p["id"] for p in pending}
        merged = [t for t in existing["texts"] if t["id"] not in ids] + pending
        PENDING.write_text(json.dumps({"texts": merged}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWrote {len(merged)} metadata entries to {PENDING}")
    print("\nSummary:")
    for r in report:
        print("  ", *r)


if __name__ == "__main__":
    main()
