#!/usr/bin/env python3
"""
import_1qisaa.py — Great Isaiah Scroll (1QIsa-a) importer for Theosis Library.

Every chapter of Isaiah is built from three verified, openly licensed sources:

  1. SCAN  — the Google Art Project / Israel Museum photograph of the whole
     scroll, as uploaded to Wikimedia Commons in five maximum-zoom tiles
     ("The Great Isaiah Scroll MS A (1QIsa) - Google Art Project-x{0..4}-y0.jpg",
     together 127,488 x 5,013 px; Commons license tag: Public domain / PD-Art).
     The 54 columns are located by an ink-projection profile across the whole
     composite; the 53 inter-column gaps are stored in COLUMN_GAPS (full-res x
     coordinates in the composite) and every column image is a crop of exactly
     that column.  Three columns were checked letter-for-letter against the
     transcription before scaling (col. 1 = Isa 1:1 "חזון ישעיהו בן אמוץ",
     col. 28 = Isa 34:1 "קרובו גואים לשמוע", col. 44 = Isa 52:13 "הנה ישכיל עבדי").

  2. HEBREW — the scroll's own text (not the Masoretic/Leningrad text) from the
     ETCBC "dss" Text-Fabric dataset (github.com/ETCBC/dss, tf/2.0), converted
     by Jarod Jacobs, Martijn Naaijer and Dirk Roorda from Martin G. Abegg Jr.'s
     Qumran transcriptions.  Data license: CC BY-NC 4.0.  Every word carries the
     scroll column ("fragment") and line it stands on, so the column-to-verse
     map is derived from the transcription itself, not from a secondary index.
     The raw .tf files are parsed directly (no text-fabric dependency).

  3. ENGLISH — King James Version via bible-api.com (public domain).

Versification: the transcription follows the Masoretic chapter/verse division;
this importer re-numbers to the KJV where they differ (MT 8:23 = KJV 9:1,
MT 9:n = KJV 9:n+1; MT 63:19b = KJV 64:1, MT 64:n = KJV 64:n+1).

Usage:
    python3 scripts/import_1qisaa.py --chapter 53          # prove one chapter
    python3 scripts/import_1qisaa.py --all                 # all 66 chapters
    python3 scripts/import_1qisaa.py --all --force         # rebuild everything

Outputs:
    translations/published/verified-1qisaa-isa-<ch>.json
    site/assets/scans/1qisaa/1qisaa-col-<NN>.jpg
    data/pending/1qisaa_texts.json   (metadata rows for data/texts.json)

Re-runnable; every HTTP fetch is cached under $THEOSIS_CACHE or
~/.cache/theosis-1qisaa.
"""

import argparse
import importlib.util
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "1qisaa"
PENDING = ROOT / "data" / "pending" / "1qisaa_texts.json"
CACHE = Path(os.environ.get("THEOSIS_CACHE", Path.home() / ".cache" / "theosis-1qisaa"))
USER_AGENT = "TheosisLibrary/1.0 (https://theosislibrary.com; contact@theosislibrary.com)"

# Reuse the KJV fetcher from the main pipeline.
_spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
iv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(iv)

# ----------------------------------------------------------------------------
# Sources
# ----------------------------------------------------------------------------
ETCBC_COMMIT = "f051578775b77b36164cfa16c402563d7d211a55"  # ETCBC/dss master, 2026-09-05
ETCBC_RAW = f"https://raw.githubusercontent.com/ETCBC/dss/{ETCBC_COMMIT}/tf/2.0/"
TF_FEATURES = ["otype", "oslots", "scroll", "fragment", "line", "chapter", "verse", "full", "after"]

# Five maximum-zoom tiles of the Google Art Project scan on Wikimedia Commons.
COMMONS_TILES = [
    ("https://upload.wikimedia.org/wikipedia/commons/b/ba/The_Great_Isaiah_Scroll_MS_A_%281QIsa%29_-_Google_Art_Project-x0-y0.jpg", 29696),
    ("https://upload.wikimedia.org/wikipedia/commons/6/66/The_Great_Isaiah_Scroll_MS_A_%281QIsa%29_-_Google_Art_Project-x1-y0.jpg", 29696),
    ("https://upload.wikimedia.org/wikipedia/commons/6/67/The_Great_Isaiah_Scroll_MS_A_%281QIsa%29_-_Google_Art_Project-x2-y0.jpg", 29696),
    ("https://upload.wikimedia.org/wikipedia/commons/b/ba/The_Great_Isaiah_Scroll_MS_A_%281QIsa%29_-_Google_Art_Project-x3-y0.jpg", 29696),
    ("https://upload.wikimedia.org/wikipedia/commons/c/ce/The_Great_Isaiah_Scroll_MS_A_%281QIsa%29_-_Google_Art_Project-x4-y0.jpg", 8704),
]
COMMONS_PAGE = "https://commons.wikimedia.org/wiki/File:The_Great_Isaiah_Scroll_MS_A_(1QIsa)_-_Google_Art_Project.jpg"
COMPOSITE_W = sum(w for _, w in COMMONS_TILES)  # 127488
COMPOSITE_H = 5013

# Centre x (full-res composite pixels) of the 53 gaps between the 54 columns,
# listed left-to-right in the photograph, i.e. from the gap between col. 54/53
# to the gap between col. 2/1 (the scroll reads right to left, so col. 1 is at
# the right-hand end of the image).  Derived by the ink-projection procedure in
# locate_gaps() and checked by eye on every one of the 53 boundaries.
COLUMN_GAPS = [
    2524, 4746, 6490, 8964, 11342, 14386, 17074, 19510, 21890, 23962, 26110,
    28504, 31390, 34196, 37030, 39630, 42226, 45082, 47774, 50016, 52658,
    55030, 57218, 59750, 62402, 64618, 67486, 69564, 71674, 73968, 76292,
    79044, 81098, 82962, 85042, 87186, 89166, 91290, 93342, 95754, 97706,
    99798, 102070, 105034, 107736, 109804, 112106, 114260, 116394, 118546,
    120678, 122702, 124730,
]
SCAN_SCALE = 0.5  # stored column images are half the Commons resolution (~1250 x 2506)

KJV_BOOK = "Isaiah"


# ----------------------------------------------------------------------------
# HTTP with on-disk cache
# ----------------------------------------------------------------------------
def cached_get(url, name, timeout=120, min_size=1):
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / name
    if local.exists() and local.stat().st_size >= min_size:
        return local
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            resp = urllib.request.urlopen(req, timeout=timeout)
            try:
                data = resp.read()
            finally:
                resp.close()
            local.write_bytes(data)
            return local
        except Exception as e:  # noqa
            print(f"  retry {attempt + 1} for {url}: {e}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"could not fetch {url}")


# ----------------------------------------------------------------------------
# Minimal Text-Fabric (.tf) reader — node features and the oslots edge
# ----------------------------------------------------------------------------
def _set_from_spec(spec):
    out = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return out


def read_tf(path, is_edge=False, is_int=False):
    """Return {node: value} (node feature) or {node: set(slots)} (oslots)."""
    data = {}
    implicit = 1
    with open(path, encoding="utf-8") as fh:
        # header: lines starting with @, terminated by a blank line
        for line in fh:
            if line.startswith("@"):
                continue
            if line.strip() == "":
                break
        for line in fh:
            fields = line.rstrip("\n").split("\t")
            if is_edge:
                if len(fields) == 2:
                    nodes, spec = _set_from_spec(fields[0]), fields[1]
                else:
                    nodes, spec = {implicit}, fields[0]
                slots = _set_from_spec(spec)
                for n in nodes:
                    data.setdefault(n, set()).update(slots)
            else:
                if len(fields) == 2:
                    nodes, val = _set_from_spec(fields[0]), fields[1]
                else:
                    nodes, val = {implicit}, fields[0]
                if is_int:
                    v = int(val) if val.isdigit() else (val or None)
                else:
                    v = val.replace("\\t", "\t").replace("\\n", "\n")
                for n in nodes:
                    if v is not None:
                        data[n] = v
            implicit = max(nodes) + 1
    return data


def load_scroll_words():
    """Parse the ETCBC dataset and return the 1QIsaa words in slot order.

    Each word: dict(chapter, verse, column, line, full, after)."""
    files = {f: cached_get(ETCBC_RAW + f + ".tf", f"etcbc_{ETCBC_COMMIT[:8]}_{f}.tf", min_size=100)
             for f in TF_FEATURES}
    otype = read_tf(files["otype"])
    oslots = read_tf(files["oslots"], is_edge=True)
    scroll = read_tf(files["scroll"])
    fragment = read_tf(files["fragment"])
    line = read_tf(files["line"])
    chapter = read_tf(files["chapter"], is_int=True)
    verse = read_tf(files["verse"], is_int=True)
    full = read_tf(files["full"])
    after = read_tf(files["after"])

    # otype.tf is stored as ranges: node ranges -> type
    type_ranges = []
    with open(files["otype"], encoding="utf-8") as fh:
        for ln in fh:
            if ln.startswith("@") or not ln.strip():
                continue
            spec, typ = ln.rstrip("\n").split("\t")
            a, b = (spec.split("-") + [spec])[:2] if "-" in spec else (spec, spec)
            type_ranges.append((int(a), int(b), typ))

    def nodes_of(typ):
        for a, b, t in type_ranges:
            if t == typ:
                return range(a, b + 1)
        raise KeyError(typ)

    scroll_node = [n for n in nodes_of("scroll") if scroll.get(n) == "1Qisaa"]
    if len(scroll_node) != 1:
        raise RuntimeError("scroll 1Qisaa not found in ETCBC data")
    scroll_node = scroll_node[0]
    scroll_slots = oslots[scroll_node]
    lo, hi = min(scroll_slots), max(scroll_slots)

    # slot -> column (fragment) and slot -> line, restricted to this scroll
    slot_col, slot_line = {}, {}
    for n in nodes_of("fragment"):
        sl = oslots.get(n, ())
        if sl and lo <= min(sl) <= hi:
            for s in sl:
                slot_col[s] = int(fragment[n])
    for n in nodes_of("line"):
        sl = oslots.get(n, ())
        if sl and lo <= min(sl) <= hi:
            for s in sl:
                slot_line[s] = int(line[n])

    words = []
    for n in nodes_of("word"):
        sl = oslots.get(n)
        if not sl:
            continue
        s0 = min(sl)
        if not (lo <= s0 <= hi):
            continue
        words.append({
            "node": n, "slot": s0,
            "chapter": chapter.get(n), "verse": verse.get(n),
            "column": slot_col.get(s0), "line": slot_line.get(s0),
            "full": full.get(n, ""), "after": after.get(n, ""),
        })
    words.sort(key=lambda w: w["slot"])
    return words


# ----------------------------------------------------------------------------
# Rendering the transcription for display
# ----------------------------------------------------------------------------
# Abegg/ETCBC "full" encoding (Unicode representation):
#   ׳          morpheme divider (editorial, not on the leather)  -> removed
#   ׃          verse-end mark supplied by the editor              -> removed
#   x#  x?     uncertain letter (degrees 1-4 use # and ? combos)  -> x + U+0323
#   [ x ]      modern reconstruction of lost text                 -> [x]
#   (^ x ^)    letters added above the line by an ancient scribe  -> ⟨x⟩
#   {{ x }}    letters cancelled/erased by an ancient scribe      -> {{x}}
#   (<< x >>)  correction by an ancient scribe                    -> ⟪x⟫
#   (- x -)    vacat / margin sign as encoded in the source        -> (-x-)
#   יייי       Tetrapuncta (four dots for the divine name)          -> ····
DOT_BELOW = "̣"


def render_word(full):
    t = full or ""
    t = t.replace("׳", "")            # morpheme divider
    t = t.replace("׃", "")            # editorial verse mark
    t = t.replace("\xa0", " ")
    t = t.replace("(^", "⟨").replace("^)", "⟩")      # ⟨ ⟩ supralinear
    t = t.replace("(<<", "⟪").replace(">>)", "⟫")    # ⟪ ⟫ ancient correction
    # uncertainty flags -> dot below the preceding letter (one dot per letter)
    t = re.sub(r"([א-ת])[#?]+", lambda m: m.group(1) + DOT_BELOW, t)
    t = re.sub(r"[#?]+", "", t)
    # Tetrapuncta: the source writes the four dots used for the divine name as four yods
    t = re.sub(r"(?<![א-ת])(י{4,})(?![א-ת])", lambda m: "·" * len(m.group(1)), t)
    # tidy bracket interiors: "[ י ]" -> "[י]", "[   ]" -> "[…]"
    for o, c in (("[", "]"), ("{{", "}}"), ("⟨", "⟩"), ("⟪", "⟫"), ("(-", "-)")):
        pat = re.escape(o) + r"\s*(.*?)\s*" + re.escape(c)
        t = re.sub(pat, lambda m, o=o, c=c: o + (m.group(1).strip() or "…") + c, t)
    return t.strip()


def verse_text(words):
    out = []
    for w in words:
        r = render_word(w["full"])
        if not r:
            continue
        out.append(r + (" " if w["after"] else ""))
    s = "".join(out)
    s = re.sub(r"\s+", " ", s).strip()
    # brackets that open in one word and close in a later one ("(^ כי … אלוהינו ^)")
    for o in ("⟨", "⟪", "[", "{{", "(-"):
        s = s.replace(o + " ", o)
    for c in ("⟩", "⟫", "]", "}}", "-)"):
        s = s.replace(" " + c, c)
    return s


# ----------------------------------------------------------------------------
# Versification MT -> KJV
# ----------------------------------------------------------------------------
def kjv_ref(mt_ch, mt_v):
    """Map a Masoretic (ETCBC) chapter:verse to the KJV chapter:verse."""
    if mt_ch == 8 and mt_v == 23:
        return 9, 1
    if mt_ch == 9:
        return 9, mt_v + 1
    if mt_ch == 64:
        return 64, mt_v + 1
    return mt_ch, mt_v


def build_kjv_verses(words):
    """Return {(kjv_ch, kjv_v): [words]} with the MT 63:19 -> KJV 63:19 + 64:1 split."""
    verses = {}
    for w in words:
        if w["chapter"] is None or w["verse"] is None:
            continue
        verses.setdefault(kjv_ref(w["chapter"], w["verse"]), []).append(w)
    # KJV 64:1 = second half of MT 63:19, beginning "לוא קרעתה שמים" (Oh that thou wouldest rend the heavens)
    v = verses.get((63, 19), [])
    for i, w in enumerate(v):
        if render_word(w["full"]).startswith("קרעת") and i > 0 and render_word(v[i - 1]["full"]) in ("לוא", "לו", "לא"):
            verses[(64, 1)] = v[i - 1:]
            verses[(63, 19)] = v[:i - 1]
            break
    else:
        raise RuntimeError("could not split MT 63:19 for KJV 64:1")
    return verses


# ----------------------------------------------------------------------------
# Column images
# ----------------------------------------------------------------------------
def tile_images():
    ims = []
    for i, (url, w) in enumerate(COMMONS_TILES):
        p = cached_get(url, f"commons_gap_x{i}.jpg", timeout=600, min_size=1_000_000)
        im = Image.open(p)
        if im.size != (w, COMPOSITE_H):
            raise RuntimeError(f"tile {i} has unexpected size {im.size}")
        ims.append(im)
    return ims


def crop_composite(tiles, x0, x1):
    out = Image.new("RGB", (x1 - x0, COMPOSITE_H))
    off = 0
    for im, (_, w) in zip(tiles, COMMONS_TILES):
        a, b = off, off + w
        lo, hi = max(x0, a), min(x1, b)
        if lo < hi:
            out.paste(im.crop((lo - a, 0, hi - a, COMPOSITE_H)), (lo - x0, 0))
        off += w
    return out


def column_bounds(col):
    """Full-res x range in the composite for column `col` (1..54)."""
    edges = [0] + COLUMN_GAPS + [COMPOSITE_W]
    return edges[54 - col], edges[55 - col]


def column_file(col):
    return f"1qisaa/1qisaa-col-{col:02d}.jpg"


def ensure_column_image(col, tiles_holder, force=False):
    dest = ROOT / "site" / "assets" / "scans" / column_file(col)
    if dest.exists() and dest.stat().st_size > 50_000 and not force:
        return dest
    if tiles_holder[0] is None:
        tiles_holder[0] = tile_images()
    x0, x1 = column_bounds(col)
    im = crop_composite(tiles_holder[0], x0, x1)
    im = im.resize((round(im.width * SCAN_SCALE), round(im.height * SCAN_SCALE)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=86, optimize=True)
    return dest


def locate_gaps(tiles):
    """(Diagnostic) Recompute inter-column gap centres from an ink projection.

    Not used by the build; kept so the COLUMN_GAPS table can be regenerated and
    audited.  Returns a list of candidate gap centres in full-res pixels."""
    import numpy as np
    small = [t.reduce(8) for t in tiles]
    W = sum(t.width for t in small)
    ov = Image.new("L", (W, small[0].height))
    x = 0
    for t in small:
        ov.paste(t.convert("L"), (x, 0))
        x += t.width
    g = np.asarray(ov).astype(float)
    c = np.asarray(ov.filter(ImageFilter.MaxFilter(9))).astype(float)
    ink = ((c - g) > 45)[30:600]
    s = np.convolve(ink.mean(axis=0), np.ones(15) / 15, mode="same")
    cands = []
    for xx in range(30, W - 30):
        win = s[max(0, xx - 90):xx + 90]
        if s[xx] == win.min() and s[xx] < 0.5 * win.max():
            if not cands or xx - cands[-1] >= 60:
                cands.append(xx)
    return [cc * 8 for cc in cands]


# ----------------------------------------------------------------------------
# Entry builder
# ----------------------------------------------------------------------------
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def roman(n):
    out = ""
    for val, sym in ((50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= val:
            out += sym
            n -= val
    return out


def fetch_kjv(chapter):
    p = CACHE / f"kjv_isa_{chapter}.json"
    if p.exists():
        return {int(k): v for k, v in json.loads(p.read_text(encoding="utf-8")).items()}
    time.sleep(1.5)  # be polite to bible-api.com (429s otherwise)
    for attempt in range(6):
        try:
            data = iv.fetch_kjv_chapter(KJV_BOOK, chapter)
            break
        except Exception as e:  # noqa
            print(f"  KJV retry {attempt + 1}: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"KJV fetch failed for Isaiah {chapter}")
    verses = {int(v["verse"]): re.sub(r"\s+", " ", (v["text"] or "")).strip() for v in data["verses"]}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(verses, ensure_ascii=False), encoding="utf-8")
    return {int(k): v for k, v in verses.items()}


def balanced_groups(nums, target):
    """Split verse numbers into near-equal groups of about `target` verses (never a 1-verse tail)."""
    n = len(nums)
    k = max(1, round(n / target))
    base, extra = divmod(n, k)
    out, i = [], 0
    for j in range(k):
        size = base + (1 if j < extra else 0)
        out.append(nums[i:i + size])
        i += size
    return out


def ranges_str(ch, nums):
    out, start, prev = [], None, None
    for n in nums:
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append((start, prev))
            start = prev = n
    if start is not None:
        out.append((start, prev))
    return ", ".join(f"{ch}:{a}" if a == b else f"{ch}:{a}-{b}" for a, b in out)


def intro_html(chapter, cols, absent, numbering_note):
    col_list = ", ".join(f"col. {roman(c)} ({c})" for c in cols)
    html = (
        f"<p>Isaiah {chapter} from the <strong>Great Isaiah Scroll</strong> (1QIsa<sup>a</sup>), the complete copy of Isaiah "
        f"found in Cave 1 at Qumran in 1947 and now in the Shrine of the Book, Israel Museum, Jerusalem. "
        f"Copied around 125 BCE, it is roughly a thousand years older than the Leningrad Codex, the oldest complete "
        f"Masoretic manuscript. This chapter stands in {col_list} of the scroll's 54 columns.</p>"
        "<ol>"
        "<li><strong>Scan:</strong> each section is shown with the actual column of the scroll that carries it, cropped "
        "from the Israel Museum / Google Art Project photograph of the whole scroll published on Wikimedia Commons "
        "(public domain). The column for every verse comes from the transcription itself, which records the column "
        "and line of each word.</li>"
        "<li><strong>Hebrew:</strong> the scroll's own text, verbatim from the ETCBC <em>dss</em> Text-Fabric dataset "
        "(Jacobs, Naaijer and Roorda, from Martin G. Abegg Jr.'s transcription; CC BY-NC 4.0). This is not the "
        "Masoretic text: 1QIsa<sup>a</sup> uses a fuller spelling (for example <span dir=\"rtl\">לוא</span> for "
        "<span dir=\"rtl\">לא</span>, <span dir=\"rtl\">כיא</span> for <span dir=\"rtl\">כי</span>) and differs from "
        "the Masoretic text in a number of readings. No vowel points exist in the scroll and none are added. "
        "Marks: ⟨x⟩ letters the scribe added above the line, [x] modern reconstruction of text lost to damage, "
        "{{x}} letters cancelled by an ancient scribe, ⟪x⟫ an ancient correction, a dot under a letter (x̣) an "
        "uncertain reading, ···· four dots written in place of the divine name (Tetrapuncta).</li>"
        "<li><strong>English:</strong> the King James Version (1611, public domain), verbatim from bible-api.com. "
        "The KJV translates the Masoretic text, so where the scroll reads differently the English will not match "
        "the Hebrew shown; the scroll's reading can be checked on the column image.</li>"
        "</ol>"
    )
    if numbering_note:
        html += f"<p><strong>Numbering:</strong> {numbering_note}</p>"
    if absent:
        refs = ranges_str(chapter, absent)
        html += (f"<p><strong>Manuscript note:</strong> KJV verse{'s' if len(absent) > 1 else ''} {refs} "
                 f"{'are' if len(absent) > 1 else 'is'} not present in 1QIsa<sup>a</sup> as transcribed. The English is "
                 "shown for reference with no Hebrew beside it; the omission can be checked on the column image.</p>")
    return html


NUMBERING_NOTES = {
    9: "The scroll and the Masoretic text number KJV 9:1 as 8:23 and KJV 9:2-21 as 9:1-20. The Hebrew here is "
       "re-numbered to the KJV so the verses line up; no text is added or removed.",
    8: "KJV 9:1 is Masoretic 8:23; it is shown in chapter 9.",
    63: "KJV 64:1 is the second half of Masoretic 63:19; it is shown in chapter 64.",
    64: "KJV 64:1 is the second half of Masoretic 63:19, and KJV 64:2-12 are Masoretic 64:1-11. The Hebrew here is "
        "re-numbered to the KJV so the verses line up; no text is added or removed.",
}


def build_chapter(chapter, verses_by_ref, tiles_holder, force=False, group_size=7):
    entry_id = f"verified-1qisaa-isa-{chapter}"
    out_path = PUB / f"{entry_id}.json"
    kjv = fetch_kjv(chapter)
    kjv_nums = sorted(kjv)
    heb = {v: verses_by_ref.get((chapter, v), []) for v in kjv_nums}
    extra = sorted(v for (c, v) in verses_by_ref if c == chapter and v not in kjv)
    if extra:
        raise RuntimeError(f"Isaiah {chapter}: Hebrew verses with no KJV counterpart: {extra}")
    absent = [v for v in kjv_nums if not heb[v]]

    sections, all_cols = [], []
    for grp in balanced_groups(kjv_nums, group_size):
        cols, lines = [], {}
        orig_parts, eng_parts = [], []
        for v in grp:
            ws = heb[v]
            for w in ws:
                if w["column"] not in cols:
                    cols.append(w["column"])
                lines.setdefault(w["column"], []).append(w["line"])
            if ws:
                orig_parts.append(f"<sup>{v}</sup>{verse_text(ws)}")
            eng_parts.append(f"<sup>{v}</sup>{kjv[v]}")
        if not cols:
            raise RuntimeError(f"Isaiah {chapter}:{grp[0]}-{grp[-1]}: no column for any verse")
        loc = "; ".join(f"col. {roman(c)} line {min(lines[c])}" if min(lines[c]) == max(lines[c])
                        else f"col. {roman(c)} lines {min(lines[c])}-{max(lines[c])}" for c in cols)
        for c in cols:
            ensure_column_image(c, tiles_holder, force=force)
            if c not in all_cols:
                all_cols.append(c)
        sec = {
            "section": f"{chapter}.{grp[0]}-{grp[-1]}" if len(grp) > 1 else f"{chapter}.{grp[0]}",
            "original_ref": f"Isaiah {chapter}:{grp[0]}-{grp[-1]} (1QIsa-a {loc})" if len(grp) > 1
            else f"Isaiah {chapter}:{grp[0]} (1QIsa-a {loc})",
            "original_text": " ".join(orig_parts),
            "text": " ".join(eng_parts),
            "scan_pages": [column_file(c) for c in cols],
        }
        sections.append(sec)

    col_map = {}
    for c in all_cols:
        vs = sorted(v for v in kjv_nums for w in heb[v][:1] if w["column"] == c)
        vs = sorted({v for v in kjv_nums if any(w["column"] == c for w in heb[v])})
        x0, x1 = column_bounds(c)
        col_map[column_file(c)] = {
            "column": c,
            "verses_in_this_chapter": ranges_str(chapter, vs),
            "crop_x_full_res": [x0, x1],
            "crop_y_full_res": [0, COMPOSITE_H],
        }

    entry = {
        "id": entry_id,
        "title": f"Isaiah, Chapter {chapter} (Great Isaiah Scroll, 1QIsa-a)",
        "slug": entry_id,
        "language": "Hebrew (1QIsa-a transcription) / English (KJV)",
        "source": "Great Isaiah Scroll 1QIsa-a: Israel Museum / Google Art Project photograph (Wikimedia Commons, PD) + ETCBC dss transcription (Abegg; CC BY-NC 4.0) + KJV (bible-api.com)",
        "description": (
            f"Isaiah {chapter} as written in the Great Isaiah Scroll (1QIsa-a, c. 125 BCE, Qumran Cave 1, Israel Museum), "
            f"shown with the specific scroll column(s) {', '.join(str(c) for c in all_cols)} that carry each section. "
            "Hebrew is the scroll's own transcription (ETCBC dss / Abegg), not the Masoretic text; English is the King James Version."
        ),
        "introduction": intro_html(chapter, all_cols, absent, NUMBERING_NOTES.get(chapter)),
        "translation": sections,
        "translator_notes": [],
        "verification": {
            "scan_source": "Wikimedia Commons, 'The Great Isaiah Scroll MS A (1QIsa) - Google Art Project' maximum-zoom tile set (x0..x4-y0), photograph by the Israel Museum / Google Cultural Institute",
            "scan_source_url": COMMONS_PAGE,
            "scan_license": "Public domain (Commons PD-Art: faithful reproduction of a public-domain 2nd-century BCE manuscript)",
            "scan_manuscript": "Great Isaiah Scroll, 1QIsa-a (c. 125 BCE), Shrine of the Book, Israel Museum, Jerusalem",
            "scan_mapping": "Column per verse taken from the ETCBC dss transcription's own fragment (= column) and line features; column images are crops of the Commons composite at the x ranges recorded in scan_columns (full-resolution composite pixels, 127488 x 5013), stored at half resolution",
            "scan_columns": col_map,
            "scan_local_paths": [column_file(c) for c in all_cols],
            "original_text_source": f"ETCBC dss Text-Fabric dataset v2.0 (github.com/ETCBC/dss @ {ETCBC_COMMIT[:8]}), scroll 1Qisaa, feature 'full' rendered for display; based on Martin G. Abegg Jr.'s transcription",
            "original_text_license": "CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)",
            "original_text_versification": "Masoretic verse numbers re-mapped to KJV (MT 8:23 = KJV 9:1; MT 9:n = KJV 9:n+1; MT 63:19b = KJV 64:1; MT 64:n = KJV 64:n+1)",
            "translation_source": "bible-api.com (KJV)",
            "translation_license": "public domain",
            "verified_date": date.today().isoformat(),
        },
    }
    if absent:
        entry["verification"]["absent_in_manuscript"] = [f"{chapter}:{v}" for v in absent]
    PUB.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return entry, all_cols, absent


def texts_row(entry, cols):
    m = re.match(r"verified-1qisaa-isa-(\d+)$", entry["id"])
    ch = int(m.group(1))
    return {
        "id": entry["id"],
        "title": f"Isaiah {ch} (Great Isaiah Scroll)",
        "author_id": "biblical-authors",
        "language": entry["language"],
        "era": "Old Testament",
        "tradition": "orthodox",
        "category": "sacred-text",
        "date_approx": "8th-6th c. BCE (composition); c. 125 BCE (1QIsa-a)",
        "century": -8,
        "source": entry["source"],
        "description": entry["description"],
        "themes": ["bible", "old-testament", "isaiah", "dead-sea-scrolls", "1qisaa", "verified"],
        "is_first_translation": False,
        "status": "published",
        "slug": entry["slug"],
        "scans": {"pages": [{"file": column_file(c), "caption": f"Great Isaiah Scroll, column {roman(c)} ({c})"} for c in cols]},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, action="append")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--locate-gaps", action="store_true", help="print recomputed gap candidates and exit")
    args = ap.parse_args()

    if args.locate_gaps:
        print(locate_gaps(tile_images()))
        return

    chapters = list(range(1, 67)) if args.all else (args.chapter or [53])
    print("parsing ETCBC dss data …")
    words = load_scroll_words()
    print(f"  1Qisaa words: {len(words)}; columns: {len({w['column'] for w in words})}")
    verses = build_kjv_verses(words)

    tiles_holder = [None]
    rows, absent_all = [], {}
    for ch in chapters:
        entry, cols, absent = build_chapter(ch, verses, tiles_holder, force=args.force)
        rows.append(texts_row(entry, cols))
        if absent:
            absent_all[ch] = absent
        print(f"Isaiah {ch}: {len(entry['translation'])} sections, columns {cols}"
              + (f", absent {absent}" if absent else ""))

    # merge into pending metadata file
    PENDING.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if PENDING.exists():
        for r in json.loads(PENDING.read_text(encoding="utf-8")).get("texts", []):
            existing[r["id"]] = r
    for r in rows:
        existing[r["id"]] = r
    ordered = sorted(existing.values(), key=lambda r: int(r["id"].rsplit("-", 1)[1]))
    PENDING.write_text(json.dumps({"texts": ordered}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(rows)} entries; pending metadata rows: {len(ordered)} -> {PENDING}")
    if absent_all:
        print("verses absent from the scroll:", absent_all)


if __name__ == "__main__":
    main()
