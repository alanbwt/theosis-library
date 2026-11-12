#!/usr/bin/env python3
"""
import_qumran_1qphab.py -- Pesher Habakkuk (1QpHab), columns I-V, for Theosis Library.

Collection key: qumran-1qphab   (prefix verified-qumran-1qphab-)

The scroll has 13 columns. Only columns I-V are built, because only those columns
have a photograph that is openly reusable (see GAPS below).

Chain of evidence
-----------------
1. SCANS  Two photographs of the original scroll (Israel Museum, Jerusalem, inv. 95.57/28),
          both on Wikimedia Commons with the license tag {{PD-Art}}:
            a. "Habakkuk Pesher.png" (760 x 633 px), source given on Commons as the Israel
               Museum Digital Dead Sea Scrolls project (dss.collections.imj.org.il/habakkuk).
               It shows column I, column II and the right-hand half of column III.
               Stored unchanged in size (never upscaled) as 1qphab-cols-1-3.jpg.
            b. "The Commentary on Habakkuk Scroll (1QpHab) Written in Hebrew - Google Art
               Project.jpg" (3001 x 1663 px; Google Art Project, "Photo (c) Israel Museum,
               Jerusalem, by David Harris"). It shows the left-hand half of column III and
               columns IV and V. Cropped here into three files, one per column.
          The column on each image was identified by reading the Hebrew on the image and
          matching it to the transcription (first and last legible words, recorded in each
          section's scan_note).
2. HEBREW The scroll's own text, column by column and line by line, from the ETCBC "dss"
          Text-Fabric dataset (github.com/ETCBC/dss, tf/2.0, commit pinned below), converted
          by Jarod Jacobs, Martijn Naaijer and Dirk Roorda from the Qumran transcriptions of
          Martin G. Abegg Jr., James E. Bowley and Edward M. Cook. License CC BY-NC 4.0.
          Every word carries its column ("fragment") and line, so the column mapping comes
          from the transcription itself. Rendering follows scripts/import_1qisaa.py; the
          dataset's sign for a missing letter (epsilon) is shown as an ellipsis.
3. ENGLISH W. H. Brownlee, "The Jerusalem Habakkuk Scroll", Bulletin of the American
          Schools of Oriental Research 112 (December 1948), pp. 8-18: a complete translation
          arranged by the same 13 extant columns with Brownlee's line numbers in the margin.
          Public domain in the United States: published 1948, copyright not renewed (The
          Online Books Page serial record for BASOR, onlinebooks.library.upenn.edu/webbin/
          cinfo/asorbulletin: "no issue renewals found in CCE or CPRS", "no contribution
          renewals found"; NYPL CCE renewal data 1975-1991 holds no renewal by Brownlee).
          The page images are open on the Internet Archive (item below). Columns 1-5 were
          transcribed by hand from those page images into
          data/sources/qumran-1qphab/brownlee1948_cols1-5.txt (format documented there).

GAPS: columns VI-XIII are not built. The only complete photographs (Israel Museum Digital
Dead Sea Scrolls site) are "All rights reserved" with reproduction limited to research or
private study, and no openly licensed photograph of those columns of the original was found
on Wikimedia Commons (a visitor's photograph of columns VI-VII in a display case could not
be confirmed to show the original rather than a facsimile).

Usage:
    python3 scripts/import_qumran_1qphab.py           # build
    python3 scripts/import_qumran_1qphab.py --force   # re-download images
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
SRC = ROOT / "data" / "sources" / KEY
TF_DIR = SRC / "etcbc"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
ENGLISH = SRC / "brownlee1948_cols1-5.txt"
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
BASOR_ITEM = "https://archive.org/details/sim_bulletin-of-the-american-schools-of-oriental-research_1948-12_112"
OBP_BASOR = "https://onlinebooks.library.upenn.edu/webbin/cinfo/asorbulletin"

# Output images: (file name, source key, crop box or None). Boxes are in pixels of the
# Commons original (3001 x 1663 for the Google Art Project file). The cut lines are the
# middles of the two blank vertical strips between the columns (x 1282-1367 between
# columns V and IV, x 2398-2470 between columns IV and III), found by an ink profile over
# rows 300-1300 and checked by eye on the image.
IMAGES = [
    ("1qphab-cols-1-3.jpg", "png", None),
    ("1qphab-col-03-left.jpg", "gap", (2434, 0, 3001, 1663)),
    ("1qphab-col-04.jpg", "gap", (1325, 0, 2434, 1663)),
    ("1qphab-col-05.jpg", "gap", (0, 0, 1325, 1663)),
]

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}

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


def load_words():
    TF_DIR.mkdir(parents=True, exist_ok=True)
    for f in TF_FEATURES:
        p = TF_DIR / f"{f}.tf"
        if not p.exists() or p.stat().st_size < 100:
            p.write_bytes(fetch(ETCBC_RAW + f + ".tf"))
    type_ranges = []
    for ln in open(TF_DIR / "otype.tf", encoding="utf-8"):
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

    oslots = read_tf(TF_DIR / "oslots.tf", is_edge=True)
    scroll = read_tf(TF_DIR / "scroll.tf")
    fragment = read_tf(TF_DIR / "fragment.tf")
    line = read_tf(TF_DIR / "line.tf")
    full = read_tf(TF_DIR / "full.tf")
    after = read_tf(TF_DIR / "after.tf")
    sn = [n for n in nodes_of("scroll") if scroll.get(n) == SCROLL]
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
def english_columns():
    cols, cur = {}, None
    for raw in ENGLISH.read_text(encoding="utf-8").splitlines():
        if raw.startswith("## "):
            cur = int(raw[3:])
            cols[cur] = []
            continue
        if raw.startswith("#") or not raw.strip():
            continue
        num, txt = raw.split("|", 1)
        poetry = txt.startswith(">")
        cols[cur].append((num.strip(), poetry, txt[1:] if poetry else txt))
    out = {}
    for c, rows in cols.items():
        blocks, prose = [], []

        def flush():
            if prose:
                blocks.append(("p", " ".join(prose)))
                prose.clear()

        for num, poetry, txt in rows:
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
        out[c] = re.sub(r"\u2026( \u2026)+", "\u2026", "".join(html))
    return out


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def build_images(force):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}
    for name, srckey, box in IMAGES:
        dest = SCAN_DIR / name
        if dest.exists() and not force:
            continue
        if srckey not in cache:
            cache[srckey] = Image.open(io.BytesIO(fetch(COMMONS_PNG if srckey == "png" else COMMONS_GAP))).convert("RGB")
        im = cache[srckey]
        if srckey == "gap":
            assert im.size == (3001, 1663), im.size
        if box:
            im = im.crop(box)
        im.save(dest, quality=90)
        print(f"  {name}: {im.size}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    build_images(args.force)

    heb = hebrew_columns(load_words())
    eng = english_columns()
    assert sorted(heb)[:5] == [1, 2, 3, 4, 5] and len(heb) == 13, sorted(heb)
    # spot checks that tie the transcription to what was read on the images
    assert "יסופר" in heb[2]["html"].split("<br>")[0]
    assert "ובמישור" in heb[3]["html"].split("<br>")[0]
    assert "יקלס ורזנים משחק לו" in heb[4]["html"].split("<br>")[0]
    assert "למשפט שמתו וצור למוכיחו" in heb[5]["html"].split("<br>")[0]
    assert eng[2].startswith("<p><sup>1</sup>it be related.") and eng[4].startswith("<p><em><sup>1</sup>(At kings)")

    sections = []
    for c in range(1, 6):
        meta = COLUMNS[c]
        sections.append({
            "section": ROMAN[c],
            "original_ref": f"1QpHab col. {ROMAN[c]}, lines 1-{heb[c]['lines']} ({meta['hab']} with commentary)",
            "original_text": heb[c]["html"],
            "text": eng[c],
            "scan_pages": [f"{KEY}/{f}" for f in meta["images"]],
            "scan_note": meta["note"] + " Column and line numbers of the Hebrew come from the ETCBC/Abegg transcription; "
                         "the English line numbers are Brownlee's (1948), which follow the same 13 columns but his own "
                         "restoration of the broken lines, so a few line numbers differ in columns I and II.",
        })

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
            "<p>The Habakkuk Commentary (Pesher Habakkuk, 1QpHab) is one of the seven scrolls found in Qumran Cave 1 in 1947. "
            "It quotes the first two chapters of the book of Habakkuk a phrase at a time and explains each quotation with the "
            "word <em>pesher</em> (\"its meaning\"), applying the prophet's words to the community's own time: the Teacher of "
            "Righteousness, the Wicked Priest, the Man of the Lie, and the Kittim, a foreign power usually identified with Rome. "
            "The scroll is about 1.48 m long and is kept in the Shrine of the Book at the Israel Museum, Jerusalem "
            "(inv. 95.57/28). On the evidence of its handwriting it is usually dated to the late first century BCE.</p>\n\n"
            "<p>This entry gives columns I to V of the 13 surviving columns (Habakkuk 1:1-16). Each section is one column. "
            "The Hebrew is the scroll's own text with its column and line numbers, from the transcription of Martin G. Abegg Jr. "
            "and colleagues in the ETCBC \"dss\" dataset. Square brackets mark letters lost from the leather and restored by "
            "the editors; a dot under a letter marks an uncertain reading; ⟨ ⟩ marks letters written above the line; "
            "an ellipsis marks lost letters that are not restored.</p>\n\n"
            "<p>The English is the complete translation of the scroll by William H. Brownlee, published in "
            "December 1948. Brownlee kept the scroll's columns and printed its line numbers in his margin; they appear here "
            "as superscript numbers. In his notation a diagonal line (/) marks the start of a new line of the scroll, words in "
            "parentheses are his conjectural restorations, a row of dots (shown here as …) is a lacuna, ? marks traces of "
            "letters, # marks letters that can be read but not translated, and words between asterisks were moved across a "
            "line division. His quotations of Habakkuk are set in italics.</p>\n\n"
            "<p>Gaps: columns VI to XIII (Habakkuk 1:16 to 2:20) are not included, because no photograph of those columns "
            "is available under terms that allow reuse here. Columns I and II, and the lower lines of every column, are damaged "
            "on the scroll itself.</p>"
        ),
        "translator_notes": [
            "Brownlee's translation of 1948 predates later work on the scroll; his restorations in parentheses sometimes differ "
            "from the restorations in square brackets in the Hebrew transcription.",
            "Footnote numbers in Brownlee's text are omitted. Each printed row of dots is shown as a single ellipsis.",
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
            "scan_local_paths": [f"{KEY}/{n}" for n, _s, _b in IMAGES],
            "original_text_source": f"ETCBC dss Text-Fabric dataset tf/2.0 (github.com/ETCBC/dss, commit {ETCBC_COMMIT}), "
                                    "scroll 1QpHab, from the transcriptions of M. G. Abegg Jr., J. E. Bowley and E. M. Cook",
            "original_text_license": "CC BY-NC 4.0",
            "translation_source": f"W. H. Brownlee, \"The Jerusalem Habakkuk Scroll\", Bulletin of the American Schools of "
                                  f"Oriental Research 112 (December 1948), pp. 8-18; page images {BASOR_ITEM} (pp. 8, 10, 11, 12), "
                                  "transcribed by hand",
            "translation_license": "Public domain in the United States: published 1948 and not renewed (no issue or contribution "
                                   f"renewals for BASOR, {OBP_BASOR}; no renewal by Brownlee in the 1975-1991 renewal records)",
            "translator": "W. H. Brownlee (1948)",
            "verified_date": TODAY,
        },
    }
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

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
            "search_terms": "dead sea scrolls qumran pesher habakkuk commentary 1qphab teacher of righteousness wicked priest kittim",
            "description": "The Habakkuk Commentary from Qumran Cave 1, columns I-V, on photographs of the scroll, with the "
                           "scroll's own Hebrew and W. H. Brownlee's 1948 English.",
        },
        "texts": [{
            "id": TID,
            "slug": TID,
            "order": 1,
            "title": entry["title"],
            "author_id": "qumran-community",
            "language": "Hebrew",
            "era": "Second Temple",
            "tradition": "jewish",
            "category": "sacred-text",
            "date_approx": "1st century BCE (composition and copy)",
            "century": -1,
            "source": entry["source"],
            "description": entry["description"],
            "themes": ["dead-sea-scrolls", "qumran", "pesher", "habakkuk", "teacher-of-righteousness", "verified"],
            "is_first_translation": False,
            "status": "published",
            "scans": {"pages": [
                {"file": f"{KEY}/1qphab-cols-1-3.jpg", "caption": "1QpHab columns I, II and right half of III"},
                {"file": f"{KEY}/1qphab-col-03-left.jpg", "caption": "1QpHab column III, left half"},
                {"file": f"{KEY}/1qphab-col-04.jpg", "caption": "1QpHab column IV"},
                {"file": f"{KEY}/1qphab-col-05.jpg", "caption": "1QpHab column V"},
            ]},
        }],
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
    print(f"wrote {TID} ({len(sections)} sections) and {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
