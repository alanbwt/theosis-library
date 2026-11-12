#!/usr/bin/env python3
"""
import_qumran_1qphab.py -- Pesher Habakkuk (1QpHab), all 13 columns, for Theosis Library.

Collection key: qumran-1qphab   (prefix verified-qumran-1qphab-)

Two entries: columns I-V (Habakkuk 1) and columns VI-XIII (Habakkuk 1:16-2:20).

Chain of evidence
-----------------
1. SCANS  a. Columns I-V: two photographs of the original scroll (Israel Museum, Jerusalem,
             inv. 95.57/28) on Wikimedia Commons with the license tag {{PD-Art}}:
             "Habakkuk Pesher.png" (760 x 633 px; from the Israel Museum Digital Dead Sea
             Scrolls project), showing column I, column II and the right half of column III,
             stored unchanged as 1qphab-cols-1-3.jpg; and "The Commentary on Habakkuk Scroll
             (1QpHab) Written in Hebrew - Google Art Project.jpg" (3001 x 1663 px; photo David
             Harris), showing the left half of column III and columns IV and V, cropped into
             three files.
          b. Columns VI-XIII: the Israel Museum's own photograph of the whole scroll on the
             Digital Dead Sea Scrolls site (dss.collections.imj.org.il/habakkuk). The site's
             viewer (/viewer/data/habakkuk.json, cached in data/sources/qumran-1qphab/imj/)
             serves the photograph as 290 px tiles from tiles.imj.org.il; zoom level 7
             (18576 x 1977 px, 65 x 7 tiles) is fetched with a plain, honestly identified HTTP
             client (no access control on the tile server), stitched, and cached as
             data/sources/qumran-1qphab/imj/habakuk_z7.jpg. The same viewer file lists each
             column's position (ids 1-13 = columns I-XIII, id 14 = the blank last sheet) in
             a 5650 px overview; those positions scaled by 18576/5650 give the crop boxes
             below, one file per column. Terms (dss.collections.imj.org.il/terms): "Website,
             text, and photos (c) The Israel Museum, Jerusalem, 2011. All rights reserved ...
             with the exception of single copies for research or private study." Used with
             credit under the library owner's instruction of 2026-11-12 (COLLECTION_SPEC rule 9).
          Every column was identified on its image by reading the Hebrew and matching it to the
          transcription (first and last legible words and line count, recorded in each
          section's scan_note).
2. HEBREW The scroll's own text, column by column and line by line, from the ETCBC "dss"
          Text-Fabric dataset (github.com/ETCBC/dss, tf/2.0, commit pinned below), converted
          by Jarod Jacobs, Martijn Naaijer and Dirk Roorda from the Qumran transcriptions of
          Martin G. Abegg Jr., James E. Bowley and Edward M. Cook. License CC BY-NC 4.0.
          Every word carries its column ("fragment") and line, so the column mapping comes
          from the transcription itself. Rendering follows scripts/import_1qisaa.py; the
          dataset's sign for a missing letter (epsilon) is shown as an ellipsis.
3. ENGLISH W. H. Brownlee, "The Jerusalem Habakkuk Scroll", Bulletin of the American Schools
          of Oriental Research 112 (December 1948), pp. 8-18: a complete translation
          arranged by the same 13 extant columns with Brownlee's line numbers in the margin.
          Public domain in the United States: published 1948, copyright not renewed (The
          Online Books Page serial record for BASOR, onlinebooks.library.upenn.edu/webbin/
          cinfo/asorbulletin: "no issue renewals found in CCE or CPRS", "no contribution
          renewals found"; NYPL CCE renewal data 1975-1991 holds no renewal by Brownlee).
          The page images are open on the Internet Archive (item below). Transcribed by hand
          from those page images into data/sources/qumran-1qphab/brownlee1948_cols1-5.txt
          and brownlee1948_cols6-13.txt (formats documented in the file headers).
          LINE NUMBERS: Brownlee marks each line division of the scroll with "/" in the
          running English and prints, in his margin, the number of a scroll line beside the
          printed line on which that scroll line begins. Shown at the start of the printed
          line, those numbers sit up to a line early (the "off by one or two" noted in the
          first build for columns I-II). For columns I-II and VI-XIII the transcription
          carries markers {n} at the exact point where scroll line n begins (after
          Brownlee's "/", or where he printed none, before the English word that renders the
          first Hebrew word of the line), each checked against the Hebrew line by line, and
          those are displayed. Columns III-V still display Brownlee's printed margin numbers
          (unchanged from the first build). Places without a "/" are listed in NO_SLASH.

Usage:
    python3 scripts/import_qumran_1qphab.py           # build
    python3 scripts/import_qumran_1qphab.py --force   # re-download / re-crop images
"""
import argparse
import io
import json
import re
import urllib.request
from collections import OrderedDict
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "qumran-1qphab"
PREFIX = f"verified-{KEY}-"
TID = f"{PREFIX}columns-1-5"
TID2 = f"{PREFIX}columns-6-13"
SRC = ROOT / "data" / "sources" / KEY
TF_DIR = SRC / "etcbc"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
ENGLISH = SRC / "brownlee1948_cols1-5.txt"
ENGLISH2 = SRC / "brownlee1948_cols6-13.txt"
IMJ_DIR = SRC / "imj"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (https://theosislibrary.com; non-commercial research)"

ETCBC_COMMIT = "f051578775b77b36164cfa16c402563d7d211a55"  # same pin as import_1qisaa.py
ETCBC_RAW = f"https://raw.githubusercontent.com/ETCBC/dss/{ETCBC_COMMIT}/tf/2.0/"
TF_FEATURES = ["otype", "oslots", "scroll", "fragment", "line", "full", "after"]
SCROLL = "1QpHab"

COMMONS_PNG = "https://upload.wikimedia.org/wikipedia/commons/0/0b/Habakkuk_Pesher.png"
COMMONS_PNG_PAGE = "https://commons.wikimedia.org/wiki/File:Habakkuk_Pesher.png"
COMMONS_GAP = ("https://upload.wikimedia.org/wikipedia/commons/8/8a/"
               "The_Commentary_on_Habakkuk_Scroll_%281QpHab%29_Written_in_Hebrew_-_Google_Art_Project.jpg")
COMMONS_GAP_PAGE = ("https://commons.wikimedia.org/wiki/File:The_Commentary_on_Habakkuk_Scroll_(1QpHab)"
                    "_Written_in_Hebrew_-_Google_Art_Project.jpg")
IMJ_PAGE = "http://dss.collections.imj.org.il/habakkuk"
IMJ_TERMS = "http://dss.collections.imj.org.il/terms"
IMJ_VIEWER_JSON = "http://dss.collections.imj.org.il/viewer/data/habakkuk.json"
IMJ_TILES = "http://tiles.imj.org.il/tiles/habakuk/"
IMJ_ZOOM, IMJ_TILE, IMJ_W, IMJ_H = 7, 290, 18576, 1977   # zoom 7 = half of fullSize 37152 x 3954
IMJ_STITCHED = IMJ_DIR / "habakuk_z7.jpg"
BASOR_ITEM = "https://archive.org/details/sim_bulletin-of-the-american-schools-of-oriental-research_1948-12_112"
OBP_BASOR = "https://onlinebooks.library.upenn.edu/webbin/cinfo/asorbulletin"

# Output images: (file name, source key, crop box or None). Boxes are in pixels of the
# source image. "gap" = the Commons Google Art Project file (3001 x 1663): the cut lines are
# the middles of the two blank vertical strips between the columns (x 1282-1367 between
# columns V and IV, x 2398-2470 between columns IV and III), found by an ink profile over
# rows 300-1300 and checked by eye on the image. "imj" = the stitched Israel Museum
# photograph at zoom 7 (18576 x 1977): x0/x1 are the column positions of the museum's own
# viewer table (habakkuk.json "columns": x and width in its 5650 px overview) multiplied by
# 18576/5650 and rounded; full height. Each crop was read on screen (see COLUMNS notes).
IMAGES = [
    ("1qphab-cols-1-3.jpg", "png", None),
    ("1qphab-col-03-left.jpg", "gap", (2434, 0, 3001, 1663)),
    ("1qphab-col-04.jpg", "gap", (1325, 0, 2434, 1663)),
    ("1qphab-col-05.jpg", "gap", (0, 0, 1325, 1663)),
    ("1qphab-col-06.jpg", "imj", (10998, 0, 12448, 1977)),
    ("1qphab-col-07.jpg", "imj", (9466, 0, 10998, 1977)),
    ("1qphab-col-08.jpg", "imj", (7739, 0, 9466, 1977)),
    ("1qphab-col-09.jpg", "imj", (6355, 0, 7739, 1977)),
    ("1qphab-col-10.jpg", "imj", (4892, 0, 6355, 1977)),
    ("1qphab-col-11.jpg", "imj", (3725, 0, 4892, 1977)),
    ("1qphab-col-12.jpg", "imj", (2269, 0, 3725, 1977)),
    ("1qphab-col-13.jpg", "imj", (871, 0, 2269, 1977)),
]

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
         11: "XI", 12: "XII", 13: "XIII"}

# Where a scroll line starts in Brownlee's English without a "/" before it (marker placed
# before the English word that renders the first Hebrew word of the line), and other
# remarks on his line marks. Checked against the Hebrew line by line.
NO_SLASH = {
    1: "Line 13 starts at a new printed line after a quotation, with no / before it.",
    2: "Line 12 starts at a new printed line after a quotation, with no / before it.",
    7: "Lines 7 and 9 start at new printed lines after quotations, with no / before them.",
    10: "Line 16 starts at a new printed line with no / before it.",
    12: "Line 11 has no / in Brownlee; its number is placed at “A molten image”, the rendering of "
        "מס[י]כה, the first word of line 11.",
    13: "Brownlee's / after “all the earth!” does not mark a line of the scroll (line 1 continues with "
        "פשרו על כול הגוים); line 2 begins after the / following “nations”.",
}

# Per column: images, Habakkuk passage, and what was checked on the image.
COLUMNS = {
    1: {
        "images": ["1qphab-cols-1-3.jpg"],
        "hab": "Habakkuk 1:1-5",
        "note": "Image 1qphab-cols-1-3.jpg, right-hand column of the larger (right) piece. Only the left ends of the lines "
                "survive. Checked on the image: line 1 ends שועתי ולוא, line 6 reads אל בעשק ומעל, line 10 על כן תפוג תורה, "
                "line 11 ends מאשו בתורת אל, line 13 ends הוא מורה הצדק, line 14 ends ל כן יצא המשפט.",
    },
    2: {
        "images": ["1qphab-cols-1-3.jpg"],
        "hab": "Habakkuk 1:5-6",
        "note": "Image 1qphab-cols-1-3.jpg. Column II runs across the crack between the two pieces: the right half of each line "
                "is the left-hand column of the right piece, the left half is the right-hand column of the left piece. "
                "Checked on the image: line 1 begins יסופר and ends הבוגדים עם איש, line 2 ends מורה הצדקה מפיא, "
                "line 4 begins האמינו בברית אל, line 12 begins פשרו על הכתיאים and ends קלים וגבורים, line 14 ends ולוא יאמינו.",
    },
    3: {
        "images": ["1qphab-cols-1-3.jpg", "1qphab-col-03-left.jpg"],
        "hab": "Habakkuk 1:6-9",
        "note": "Column III is split between two photographs. The beginnings of its lines (right half) are the left-hand column "
                "of the left piece on 1qphab-cols-1-3.jpg: line 1 begins ובמישור, line 4 פשרו על ה[כתיאים], line 8 יעופו כנשר, "
                "line 12 ואין שבעה. The ends of its lines (left half) are on 1qphab-col-03-left.jpg (right edge of the Google Art "
                "Project photograph): line 1 ends את ערי הארץ, line 2 ends משכנות לוא לו איום, line 13 ends הוא אשר, line 14 ends שבי.",
    },
    4: {
        "images": ["1qphab-col-04.jpg"],
        "hab": "Habakkuk 1:10-11",
        "note": "Image 1qphab-col-04.jpg (middle column of the Google Art Project photograph). Checked on the image: line 1 "
                "reads יקלס ורזנים משחק לו פשרו אשר, line 2 ילעיגו על רבים ובזו על נכבדים במלכים, line 10 לאלוהו פשרו על מושלי "
                "הכתיאים, line 13 begins לשחית את; only the first word of line 14 (פשרו) survives above the torn lower edge.",
    },
    5: {
        "images": ["1qphab-col-05.jpg"],
        "hab": "Habakkuk 1:12-16",
        "note": "Image 1qphab-col-05.jpg (left-hand column of the Google Art Project photograph). Checked on the image: line 1 "
                "reads למשפט שמתו וצור למוכיחו יסדתו טהור עינים, line 10 ואנשי עצתם אשר נדמו בתוכחת מורה הצדק, line 11 ends "
                "אשר מאס את, line 14 ends לחרמו על כן ישמח; the lowest lines are broken off along the torn lower edge.",
    },
    6: {
        "images": ["1qphab-col-06.jpg"],
        "hab": "Habakkuk 1:16-2:2",
        "note": "Image 1qphab-col-06.jpg (Israel Museum photograph, column VI). Checked on the image: line 1 reads הכתיאים "
                "ויוסיפו את הונם עם כול שללם, line 2 ends יזבח לחרמו, line 9 is the short line להרוג גוים ולוא יחמל, line 13 "
                "ends לראות מה ידבר, line 14 ends with the divine name written in Old Hebrew letters, line 15 ends על הלוחות "
                "למען ירוץ; of line 16 only the tops of a few letters survive at the torn lower edge (15 lines with text).",
    },
    7: {
        "images": ["1qphab-col-07.jpg"],
        "hab": "Habakkuk 2:2-4",
        "note": "Image 1qphab-col-07.jpg (Israel Museum photograph, column VII). Checked on the image: line 1 reads וידבר אל "
                "חבקוק לכתוב את הבאות על with a second אל written above the line, line 3 ואשר אמר למען הקורא בו with ירוץ "
                "above the line, line 10 has יאחר, a blank space, then פשרו על אנשי האמת, line 14 ends הנה עופלה לוא יושרה, "
                "line 15 reads פשרו אשר יכפלו עליהם; line 16 survives in part on the torn lower edge (16 lines).",
    },
    8: {
        "images": ["1qphab-col-08.jpg"],
        "hab": "Habakkuk 2:5-8",
        "note": "Image 1qphab-col-08.jpg (Israel Museum photograph, column VIII; the stitched seam between two sheets runs "
                "down its right edge). Checked on the image: line 1 reads פשרו על כול עושי התורה בבית יהודה אשר, line 8 "
                "begins עבטט, then a blank space and פשרו על הכוהן הרשע אשר, line 13 ends הלוא פתאום ויקומו, line 15 reads "
                "כי אתה שלותה גוים רבים וישלוכה כול יתר עמים, line 16 survives in part (הכוהן אשר מרד), and traces of line 17 "
                "remain at the torn lower edge.",
    },
    9: {
        "images": ["1qphab-col-09.jpg"],
        "hab": "Habakkuk 2:8-11",
        "note": "Image 1qphab-col-09.jpg (Israel Museum photograph, column IX). Checked on the image: line 1 reads נגועו "
                "במשפטי רשעה ושערוריות מחלים, line 4 יתר עמים, a blank space, פשרו על כוהני ירושלם, line 8 has יושבי written "
                "above the line, line 14 reads לביתכה קצוות עמים רבים וחוטא נפשכה כיא, line 15 begins אבן מקיר תזעק; line 16 "
                "survives in part on the torn lower edge.",
    },
    10: {
        "images": ["1qphab-col-10.jpg"],
        "hab": "Habakkuk 2:10-14",
        "note": "Image 1qphab-col-10.jpg (Israel Museum photograph, column X). Checked on the image: line 1 reads להיות אבניה "
                "בעשק וכפיס עצה בגזל ואשר, line 7 has the divine name in Old Hebrew letters before צבאות, line 8 is the short "
                "line ולאומים בדי ריק ייעפו, line 14 ends כבוד יהוה כמים (divine name in Old Hebrew letters), line 15 begins "
                "יכסו על הים; only the first word of line 16 (בשובם) survives at the right edge.",
    },
    11: {
        "images": ["1qphab-col-11.jpg"],
        "hab": "Habakkuk 2:15-17",
        "note": "Image 1qphab-col-11.jpg (Israel Museum photograph, column XI). Checked on the image: line 1 reads הכזב ואחר "
                "תגלה להם הדעת כמי, line 4 is the short line פשרו על הכוהן הרשע אשר, line 7 begins יום הכפורים, line 11 is "
                "על כבודכה alone, line 14 reads הרויה למען ספות הצמאה וכוס חמת, line 15 begins אל תבלענו on the torn lower "
                "edge (15 lines with text).",
    },
    12: {
        "images": ["1qphab-col-12.jpg"],
        "hab": "Habakkuk 2:17-19",
        "note": "Image 1qphab-col-12.jpg (Israel Museum photograph, column XII). Checked on the image: line 1 reads יחתה מדמי "
                "אדם וחמס ארץ קריה וכול יושבי בה, line 5 is the short line התורה אשר ישופטנו אל לכלה, line 8 has הרשע written "
                "above the line, line 14 reads להםה והמה לוא יצילום ביום המשפט הוי, line 15 survives in part on the torn "
                "lower edge (15 lines with text).",
    },
    13: {
        "images": ["1qphab-col-13.jpg"],
        "hab": "Habakkuk 2:20",
        "note": "Image 1qphab-col-13.jpg (Israel Museum photograph, column XIII, the last column). Checked on the image: the "
                "column has four lines, the rest of the sheet is ruled but blank: line 1 reads הס מלפניו כול הרץ, a blank space, "
                "פשרו על כול הגוים, line 4 reads ואת הרשעים מן הארץ.",
    },
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


# ---------------------------------------------------------------------------
# Text-Fabric reading (same minimal reader as scripts/import_1qisaa.py)
# ---------------------------------------------------------------------------
def _set_from_spec(spec):
    out = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return out


def read_tf(path, is_edge=False):
    data = {}
    implicit = 1
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("@"):
                continue
            if line.strip() == "":
                break
        for line in fh:
            fields = line.rstrip("\n").split("\t")
            if len(fields) == 2:
                nodes, val = _set_from_spec(fields[0]), fields[1]
            else:
                nodes, val = {implicit}, fields[0]
            if is_edge:
                slots = _set_from_spec(val)
                for n in nodes:
                    data.setdefault(n, set()).update(slots)
            else:
                v = val.replace("\\t", "\t").replace("\\n", "\n")
                for n in nodes:
                    data[n] = v
            implicit = max(nodes) + 1
    return data


def load_words(scroll_name=SCROLL, tf_dir=TF_DIR):
    """Words of one scroll as (slot, column, line, full, after); tf_dir caches the features."""
    tf_dir.mkdir(parents=True, exist_ok=True)
    for f in TF_FEATURES:
        p = tf_dir / f"{f}.tf"
        if not p.exists() or p.stat().st_size < 100:
            p.write_bytes(fetch(ETCBC_RAW + f + ".tf"))
    type_ranges = []
    for ln in open(tf_dir / "otype.tf", encoding="utf-8"):
        if ln.startswith("@") or not ln.strip():
            continue
        spec, typ = ln.rstrip("\n").split("\t")
        a, b = spec.split("-") if "-" in spec else (spec, spec)
        type_ranges.append((int(a), int(b), typ))

    def nodes_of(typ):
        for a, b, t in type_ranges:
            if t == typ:
                return range(a, b + 1)
        raise KeyError(typ)

    oslots = read_tf(tf_dir / "oslots.tf", is_edge=True)
    scroll = read_tf(tf_dir / "scroll.tf")
    fragment = read_tf(tf_dir / "fragment.tf")
    line = read_tf(tf_dir / "line.tf")
    full = read_tf(tf_dir / "full.tf")
    after = read_tf(tf_dir / "after.tf")
    sn = [n for n in nodes_of("scroll") if scroll.get(n) == scroll_name]
    assert len(sn) == 1, sn
    sl = oslots[sn[0]]
    lo, hi = min(sl), max(sl)
    slot_col, slot_line = {}, {}
    for n in nodes_of("fragment"):
        s = oslots.get(n, ())
        if s and lo <= min(s) <= hi:
            for x in s:
                slot_col[x] = int(fragment[n])
    for n in nodes_of("line"):
        s = oslots.get(n, ())
        if s and lo <= min(s) <= hi:
            for x in s:
                slot_line[x] = int(line[n])
    words = []
    for n in nodes_of("word"):
        s = oslots.get(n)
        if not s:
            continue
        s0 = min(s)
        if lo <= s0 <= hi:
            words.append((s0, slot_col.get(s0), slot_line.get(s0), full.get(n, ""), after.get(n, "")))
    words.sort()
    return words


# ---------------------------------------------------------------------------
# Rendering (conventions of scripts/import_1qisaa.py, plus epsilon -> ellipsis)
# ---------------------------------------------------------------------------
DOT_BELOW = "̣"


def render_word(full):
    t = full or ""
    t = t.replace("׳", "").replace("׃", "").replace("\xa0", " ")
    t = t.replace("ε", "…")                   # missing sign(s) -> …
    t = t.replace("(^", "⟨").replace("^)", "⟩")
    t = t.replace("(<<", "⟪").replace(">>)", "⟫")
    t = re.sub(r"([א-ת])[#?]+", lambda m: m.group(1) + DOT_BELOW, t)
    t = re.sub(r"[#?]+", "", t)
    t = re.sub(r"(?<![א-ת])(י{4,})(?![א-ת])", lambda m: "·" * len(m.group(1)), t)
    for o, c in (("[", "]"), ("{{", "}}"), ("⟨", "⟩"), ("⟪", "⟫"), ("(-", "-)")):
        pat = re.escape(o) + r"\s*(.*?)\s*" + re.escape(c)
        t = re.sub(pat, lambda m, o=o, c=c: o + (m.group(1).strip() or "…") + c, t)
    return t.strip()


def line_text(ws):
    s = "".join(render_word(f) + (" " if a else "") for f, a in ws if render_word(f))
    s = re.sub(r"\s+", " ", s).strip()
    for o in ("⟨", "⟪", "[", "{{", "(-"):
        s = s.replace(o + " ", o)
    for c in ("⟩", "⟫", "]", "}}", "-)"):
        s = s.replace(" " + c, c)
    s = re.sub(r"…(\s*…)+", "…", s)
    s = s.replace("[]", "[…]")
    return s


def hebrew_columns(words):
    cols = OrderedDict()
    for _s0, c, ln, f, a in words:
        cols.setdefault(c, OrderedDict()).setdefault(ln, []).append((f, a))
    out = {}
    for c, lines in cols.items():
        parts = [f"<sup>{ln}</sup>{line_text(ws)}" for ln, ws in lines.items()]
        out[c] = {"html": "<br>".join(parts), "lines": len(lines)}
    return out


# ---------------------------------------------------------------------------
# English (Brownlee 1948, hand transcription)
# ---------------------------------------------------------------------------
def parse_brownlee(path):
    """Rows per column: (margin number, poetry flag, text) from a Brownlee transcription file."""
    cols, cur = {}, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("## "):
            cur = int(raw[3:])
            cols[cur] = []
            continue
        if raw.startswith("#") or not raw.strip():
            continue
        num, txt = raw.split("|", 1)
        poetry = txt.startswith(">")
        cols[cur].append([num.strip(), poetry, txt[1:] if poetry else txt])
    return cols


MARK = re.compile(r"\{(\d+)\}")


def render_column(rows):
    """HTML for one column. Columns with {n} markers show the markers as line numbers
    (Brownlee's printed margin numbers are then not shown); other columns show the margin
    numbers at the start of the printed line, as in the first build."""
    marked = any(MARK.search(t) for _n, _p, t in rows)
    if marked:
        # join a printed line ending in "=" (divided word) or "-" (hyphenated compound) to the next
        joined = []
        for num, poetry, txt in rows:
            if joined and joined[-1][2].endswith(("=", "-")) and not joined[-1][2].endswith("—"):
                prev = joined[-1]
                prev[2] = (prev[2][:-1] if prev[2].endswith("=") else prev[2]) + txt
                continue
            joined.append([num, poetry, txt])
        rows = joined
    blocks, prose = [], []

    def flush():
        if prose:
            blocks.append(("p", " ".join(prose)))
            prose.clear()

    for num, poetry, txt in rows:
        if marked:
            item = MARK.sub(lambda m: f"<sup>{m.group(1)}</sup>", txt)
        else:
            item = (f"<sup>{num}</sup>" if num else "") + txt
        if poetry:
            flush()
            if blocks and blocks[-1][0] == "v":
                blocks[-1][1].append(item)
            else:
                blocks.append(("v", [item]))
        else:
            prose.append(item)
    flush()
    html = []
    for kind, val in blocks:
        html.append(f"<p>{val}</p>" if kind == "p" else "<p><em>" + "<br>".join(val) + "</em></p>")
    out = "".join(html)
    out = re.sub(r"…( …)+", "…", out)
    return out


def english_columns():
    cols = {}
    for path in (ENGLISH, ENGLISH2):
        for c, rows in parse_brownlee(path).items():
            cols[c] = render_column(rows)
    return cols


def english_markers(c):
    """Line numbers carried by the English of column c (markers or margin numbers)."""
    rows = {**parse_brownlee(ENGLISH), **parse_brownlee(ENGLISH2)}[c]
    nums = [int(m) for _n, _p, t in rows for m in MARK.findall(t)]
    return nums


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def stitch_imj(force=False):
    """The Israel Museum photograph of the whole scroll at zoom 7, stitched from its tiles."""
    IMJ_DIR.mkdir(parents=True, exist_ok=True)
    if IMJ_STITCHED.exists() and not force:
        return Image.open(IMJ_STITCHED).convert("RGB")
    import time
    canvas = Image.new("RGB", (IMJ_W, IMJ_H), (0, 0, 0))
    nx, ny = -(-IMJ_W // IMJ_TILE), -(-IMJ_H // IMJ_TILE)
    for y in range(ny):
        for x in range(nx):
            tile = Image.open(io.BytesIO(fetch(f"{IMJ_TILES}{IMJ_ZOOM}_{x}_{y}.jpg"))).convert("RGB")
            canvas.paste(tile, (x * IMJ_TILE, y * IMJ_TILE))
            time.sleep(0.15)
    canvas.save(IMJ_STITCHED, quality=92)
    return canvas


def build_images(force):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}
    for name, srckey, box in IMAGES:
        dest = SCAN_DIR / name
        if dest.exists() and not force:
            continue
        if srckey not in cache:
            if srckey == "imj":
                Image.MAX_IMAGE_PIXELS = None
                cache[srckey] = stitch_imj(force)
            else:
                cache[srckey] = Image.open(io.BytesIO(fetch(COMMONS_PNG if srckey == "png" else COMMONS_GAP))).convert("RGB")
        im = cache[srckey]
        if srckey == "gap":
            assert im.size == (3001, 1663), im.size
        if srckey == "imj":
            assert im.size == (IMJ_W, IMJ_H), im.size
        if box:
            im = im.crop(box)
        im.save(dest, quality=88 if srckey == "imj" else 90)
        print(f"  {name}: {im.size}")


HEB_INTRO = (
    "The Hebrew is the scroll's own text with its column and line numbers, from the transcription of Martin G. Abegg Jr. "
    "and colleagues in the ETCBC \"dss\" dataset. Square brackets mark letters lost from the leather and restored by "
    "the editors; a dot under a letter marks an uncertain reading; ⟨ ⟩ marks letters written above the line; "
    "an ellipsis marks lost letters that are not restored."
)
ENG_INTRO = (
    "The English is the complete translation of the scroll by William H. Brownlee, published in "
    "December 1948. Brownlee kept the scroll's columns. In his notation a diagonal line (/) marks the start of a new "
    "line of the scroll, words in parentheses are his conjectural restorations, a row of dots (shown here as …) is a "
    "lacuna, ? marks traces of letters, # marks letters that can be read but not translated, and words between "
    "asterisks were moved across a line division. His quotations of Habakkuk are set in italics."
)
SCROLL_INTRO = (
    "The Habakkuk Commentary (Pesher Habakkuk, 1QpHab) is one of the seven scrolls found in Qumran Cave 1 in 1947. "
    "It quotes the first two chapters of the book of Habakkuk a phrase at a time and explains each quotation with the "
    "word <em>pesher</em> (\"its meaning\"), applying the prophet's words to the community's own time: the Teacher of "
    "Righteousness, the Wicked Priest, the Man of the Lie, and the Kittim, a foreign power usually identified with Rome. "
    "The scroll is about 1.48 m long and is kept in the Shrine of the Book at the Israel Museum, Jerusalem "
    "(inv. 95.57/28). On the evidence of its handwriting it is usually dated to the late first century BCE."
)
MARKED_NOTE = (" Column and line numbers of the Hebrew come from the ETCBC/Abegg transcription. The English line numbers "
               "mark the point where each line of the scroll begins in Brownlee's translation, at his / marks, and were "
               "checked against the Hebrew line by line, so both texts carry the same numbers.")
MARGIN_NOTE = (" Column and line numbers of the Hebrew come from the ETCBC/Abegg transcription; the English line numbers are "
               "the numbers Brownlee (1948) printed in his margin, each at the start of the printed line on which that line "
               "of the scroll begins (the line itself may begin after a / later in that printed line).")
TRANSLATION_SOURCE = (f"W. H. Brownlee, \"The Jerusalem Habakkuk Scroll\", Bulletin of the American Schools of "
                      f"Oriental Research 112 (December 1948), pp. 8-18; page images {BASOR_ITEM}, transcribed by hand")
TRANSLATION_LICENSE = ("Public domain in the United States: published 1948 and not renewed (no issue or contribution "
                       f"renewals for BASOR, {OBP_BASOR}; no renewal by Brownlee in the 1975-1991 renewal records)")
COMMON_NOTES = [
    "Brownlee's translation of 1948 predates later work on the scroll; his restorations in parentheses sometimes differ "
    "from the restorations in square brackets in the Hebrew transcription.",
    "Footnote numbers in Brownlee's text are omitted. Each printed row of dots is shown as a single ellipsis.",
]


def make_section(c, heb, eng):
    meta = COLUMNS[c]
    nums = english_markers(c)
    marked = bool(nums)
    if marked:
        assert nums == sorted(nums) and len(set(nums)) == len(nums), (c, nums)
        assert max(nums) <= heb[c]["lines"], (c, nums, heb[c]["lines"])
    note = meta["note"] + (MARKED_NOTE if marked else MARGIN_NOTE)
    if c in NO_SLASH:
        note += " " + NO_SLASH[c]
    return {
        "section": ROMAN[c],
        "original_ref": f"1QpHab col. {ROMAN[c]}, lines 1-{heb[c]['lines']} ({meta['hab']} with commentary)",
        "original_text": heb[c]["html"],
        "text": eng[c],
        "scan_pages": [f"{KEY}/{f}" for f in meta["images"]],
        "scan_note": note,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    build_images(args.force)

    heb = hebrew_columns(load_words())
    eng = english_columns()
    assert sorted(heb) == list(range(1, 14)), sorted(heb)
    assert sorted(eng) == list(range(1, 14)), sorted(eng)
    # spot checks that tie the transcription to what was read on the images
    first = {c: heb[c]["html"].split("<br>")[0] for c in heb}
    assert "יסופר" in first[2]
    assert "ובמישור" in first[3]
    assert "יקלס ורזנים משחק לו" in first[4]
    assert "למשפט שמתו וצור למוכיחו" in first[5]
    assert "הכתיאים ויוסיפו את הונם עם כול שללם" in first[6]
    assert "וידבר אל" in first[7] and "חבקוק לכתוב את הבאות על" in first[7]
    assert "פשרו על כול עושי התורה בבית יהודה אשר" in first[8]
    assert "נגועו במשפטי רשעה שערוריות מחלים" in first[9]
    assert "להיות אבניה בעשק" in first[10]
    assert "הכזב ואחר תגלה להם הדעת כמי" in first[11]
    assert "יחתה מדמי אדם וחמס ארץ קריה" in first[12]
    assert "הס מלפניו כול הרץ" in first[13] and heb[13]["lines"] == 4
    assert eng[2].startswith("<p><sup>1</sup>it be related.") and eng[4].startswith("<p><em><sup>1</sup>(At kings)")
    assert eng[6].startswith("<p><sup>1</sup>the Chittiim;") and "<sup>4</sup>and from off the earth" in eng[13]

    # ---- entry 1: columns I-V ------------------------------------------------
    sections = [make_section(c, heb, eng) for c in range(1, 6)]
    entry = {
        "id": TID,
        "slug": TID,
        "title": "Pesher Habakkuk (1QpHab), columns I-V",
        "language": "Hebrew (Qumran transcription) / English (W. H. Brownlee, 1948)",
        "source": "Israel Museum scroll 1QpHab photographs (Wikimedia Commons, PD-Art) + ETCBC dss transcription "
                  "(Abegg; CC BY-NC 4.0) + English of W. H. Brownlee, BASOR 112 (1948), public domain",
        "description": "The first five columns of the Habakkuk Commentary from Qumran Cave 1, a line-by-line explanation of "
                       "Habakkuk 1 that names the Teacher of Righteousness, the Wicked Priest and the Kittim, each column "
                       "shown on the photograph of the scroll.",
        "introduction": (
            f"<p>{SCROLL_INTRO}</p>\n\n"
            "<p>This entry gives columns I to V of the 13 surviving columns (Habakkuk 1:1-16); columns VI to XIII "
            "(Habakkuk 1:16 to 2:20) follow in the next entry. Each section is one column. " + HEB_INTRO + "</p>\n\n"
            "<p>" + ENG_INTRO + " Superscript numbers give the lines of the scroll. In columns I and II they stand where "
            "each line of the scroll begins in the English, checked against the Hebrew line by line; in columns III to V "
            "they are the numbers Brownlee printed in his margin, beside the printed line on which each line of the "
            "scroll begins.</p>\n\n"
            "<p>Columns I and II, and the lower lines of every column, are damaged on the scroll itself.</p>"
        ),
        "translator_notes": COMMON_NOTES + [
            "The photograph of columns I-III (1qphab-cols-1-3.jpg) is 760 pixels wide, the largest openly licensed photograph of "
            "the opening columns that was found; it is shown at its original size, not enlarged.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Wikimedia Commons: {COMMONS_PNG_PAGE} (from the Israel Museum Digital Dead Sea Scrolls project, "
                           f"{IMJ_PAGE}) and {COMMONS_GAP_PAGE} (Google Art Project, Israel Museum, photo by David Harris)",
            "scan_license": "Public domain as tagged on Wikimedia Commons ({{PD-Art|PD-old-100}} and {{PD-Art|PD-old-100-expired}}: "
                            "faithful photographs of a two-dimensional public-domain work). The Israel Museum states "
                            "\"Photo (c) Israel Museum, Jerusalem\" for its own site.",
            "scan_manuscript": "1QpHab, Pesher Habakkuk, Qumran Cave 1; Israel Museum, Jerusalem, Shrine of the Book, inv. 95.57/28; "
                               "parchment, 13 columns, late 1st century BCE",
            "scan_mapping": "Columns identified by reading the Hebrew on each photograph and matching it to the column/line "
                            "data of the ETCBC transcription; first and last legible words of each column are recorded in "
                            "the section notes. Image crops cut in the blank margins between columns.",
            "scan_mapping_urls": [COMMONS_PNG_PAGE, COMMONS_GAP_PAGE, IMJ_PAGE],
            "scan_local_paths": [f"{KEY}/{n}" for n, s_, _b in IMAGES if s_ != "imj"],
            "original_text_source": f"ETCBC dss Text-Fabric dataset tf/2.0 (github.com/ETCBC/dss, commit {ETCBC_COMMIT}), "
                                    "scroll 1QpHab, from the transcriptions of M. G. Abegg Jr., J. E. Bowley and E. M. Cook",
            "original_text_license": "CC BY-NC 4.0",
            "translation_source": TRANSLATION_SOURCE + " (pp. 8, 10, 11, 12)",
            "translation_license": TRANSLATION_LICENSE,
            "translator": "W. H. Brownlee (1948)",
            "verified_date": TODAY,
        },
    }

    # ---- entry 2: columns VI-XIII --------------------------------------------
    sections2 = [make_section(c, heb, eng) for c in range(6, 14)]
    entry2 = {
        "id": TID2,
        "slug": TID2,
        "title": "Pesher Habakkuk (1QpHab), columns VI-XIII",
        "language": "Hebrew (Qumran transcription) / English (W. H. Brownlee, 1948)",
        "source": "Israel Museum photograph of scroll 1QpHab (Digital Dead Sea Scrolls) + ETCBC dss transcription "
                  "(Abegg; CC BY-NC 4.0) + English of W. H. Brownlee, BASOR 112 (1948), public domain",
        "description": "Columns VI to XIII of the Habakkuk Commentary from Qumran Cave 1, on Habakkuk 1:16 to 2:20: the "
                       "Teacher of Righteousness, the Wicked Priest, the Day of Atonement and the end of days, each column "
                       "shown on the Israel Museum's photograph of the scroll.",
        "introduction": (
            f"<p>{SCROLL_INTRO}</p>\n\n"
            "<p>This entry gives columns VI to XIII, the second half of the scroll (Habakkuk 1:16 to 2:20); columns I to V "
            "are in the previous entry. Column VII explains that God made known to the Teacher of Righteousness \"all the "
            "mysteries of the words of His servants the prophets\"; columns VIII to XII describe the Wicked Priest, his "
            "pursuit of the Teacher on the Day of Atonement and his punishment; column XIII, of four lines, ends the work, "
            "and the rest of the last sheet is ruled but left blank. Each section is one column. " + HEB_INTRO + "</p>\n\n"
            "<p>" + ENG_INTRO + " Superscript numbers give the lines of the scroll: they stand where each line of the "
            "scroll begins in the English, at Brownlee's / marks, checked against the Hebrew line by line.</p>\n\n"
            "<p>The photographs are the Israel Museum's own images of the scroll from its Digital Dead Sea Scrolls site, "
            "one image per column. The lowest lines of columns VI to XII are broken off along the torn lower edge of the "
            "scroll; the transcription restores some of them in square brackets, and Brownlee's English marks them as "
            "lacunae.</p>"
        ),
        "translator_notes": COMMON_NOTES + [
            "In column XII Brownlee's \"(The spoil of the beasts) /\" before line 1 renders words he restored at the foot of "
            "column XI; line 1 of column XII begins at \"he seized\".",
        ],
        "translation": sections2,
        "verification": {
            "scan_source": f"Israel Museum, Jerusalem, The Digital Dead Sea Scrolls: {IMJ_PAGE} (viewer data "
                           f"{IMJ_VIEWER_JSON}; image tiles {IMJ_TILES}, zoom level 7, stitched)",
            "scan_license": "As stated by the Israel Museum (" + IMJ_TERMS + "): \"Website, text, and photos (c) The Israel "
                            "Museum, Jerusalem, 2011. All rights reserved. No part of this website may be downloaded, copied, "
                            "or reproduced in any form, analog or digital, without the permission of the Israel Museum, "
                            "Jerusalem, with the exception of single copies for research or private study.\" Shown here with "
                            "credit, \"Photo (c) The Israel Museum, Jerusalem\", in a non-commercial reference library.",
            "scan_manuscript": "1QpHab, Pesher Habakkuk, Qumran Cave 1; Israel Museum, Jerusalem, Shrine of the Book, inv. 95.57/28; "
                               "parchment, 13 columns, late 1st century BCE",
            "scan_mapping": "The museum viewer's own column table (habakkuk.json: ids 1-13 = columns I-XIII, each with its x "
                            "position and width) gives the crop of each column; every crop was then read on screen and its "
                            "first and last legible words and line count matched to the ETCBC transcription (recorded in the "
                            "section notes).",
            "scan_mapping_urls": [IMJ_PAGE, IMJ_VIEWER_JSON],
            "scan_local_paths": [f"{KEY}/{n}" for n, s_, _b in IMAGES if s_ == "imj"],
            "original_text_source": f"ETCBC dss Text-Fabric dataset tf/2.0 (github.com/ETCBC/dss, commit {ETCBC_COMMIT}), "
                                    "scroll 1QpHab, from the transcriptions of M. G. Abegg Jr., J. E. Bowley and E. M. Cook",
            "original_text_license": "CC BY-NC 4.0",
            "translation_source": TRANSLATION_SOURCE + " (pp. 12-16)",
            "translation_license": TRANSLATION_LICENSE,
            "translator": "W. H. Brownlee (1948)",
            "verified_date": TODAY,
        },
    }
    PUB.mkdir(parents=True, exist_ok=True)
    for e in (entry, entry2):
        (PUB / f"{e['id']}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")

    def row(e, order, themes, pages):
        return {
            "id": e["id"], "slug": e["id"], "order": order, "title": e["title"],
            "author_id": "qumran-community", "language": "Hebrew", "era": "Second Temple", "tradition": "jewish",
            "category": "sacred-text", "date_approx": "1st century BCE (composition and copy)", "century": -1,
            "source": e["source"], "description": e["description"],
            "themes": themes, "is_first_translation": False, "status": "published",
            "scans": {"pages": pages},
        }

    coll = {
        "collection": {
            "key": KEY,
            "prefix": PREFIX,
            "label": "Pesher Habakkuk (1QpHab)",
            "group": "Dead Sea Scrolls & Second Temple",
            "date_sort": -30,
            "author_name": "Qumran Cave 1 scroll (late 1st century BCE)",
            "source_url": IMJ_PAGE,
            "critical_edition": "ETCBC dss Text-Fabric transcription (Abegg, Bowley, Cook)",
            "translator_name": "W. H. Brownlee (1948)",
            "original_lang_label": "Hebrew · Qumran transcription (Abegg, ETCBC)",
            "original_lang_code": "hbo",
            "edition_label": "",
            "search_terms": "dead sea scrolls qumran pesher habakkuk commentary 1qphab teacher of righteousness wicked priest "
                            "kittim day of atonement man of the lie",
            "description": "The Habakkuk Commentary from Qumran Cave 1, all 13 columns, on photographs of the scroll, with the "
                           "scroll's own Hebrew and W. H. Brownlee's 1948 English.",
        },
        "texts": [
            row(entry, 1, ["dead-sea-scrolls", "qumran", "pesher", "habakkuk", "teacher-of-righteousness", "verified"], [
                {"file": f"{KEY}/1qphab-cols-1-3.jpg", "caption": "1QpHab columns I, II and right half of III"},
                {"file": f"{KEY}/1qphab-col-03-left.jpg", "caption": "1QpHab column III, left half"},
                {"file": f"{KEY}/1qphab-col-04.jpg", "caption": "1QpHab column IV"},
                {"file": f"{KEY}/1qphab-col-05.jpg", "caption": "1QpHab column V"},
            ]),
            row(entry2, 2, ["dead-sea-scrolls", "qumran", "pesher", "habakkuk", "teacher-of-righteousness",
                            "wicked-priest", "verified"],
                [{"file": f"{KEY}/1qphab-col-{c:02d}.jpg", "caption": f"1QpHab column {ROMAN[c]} (Israel Museum)"}
                 for c in range(6, 14)]),
        ],
        "authors": [{
            "id": "qumran-community",
            "name": "Qumran community (Dead Sea Scrolls)",
            "dates": "2nd century BCE - 1st century CE",
            "century": -1,
            "era": "Second Temple",
            "tradition": "jewish",
            "language": "Hebrew",
            "bio": "The Jewish community whose library of scrolls was found in the caves near Khirbet Qumran on the Dead Sea from 1947.",
        }],
    }
    COLL.parent.mkdir(parents=True, exist_ok=True)
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections), {TID2} ({len(sections2)} sections) and {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
