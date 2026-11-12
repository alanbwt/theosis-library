#!/usr/bin/env python3
"""
import_qumran_1qs.py -- the Community Rule (Serekh ha-Yahad, 1QS), all 11 columns, for Theosis Library.

Collection key: qumran-1qs   (prefix verified-qumran-1qs-)

One entry, one section per scroll column (I-XI).

Chain of evidence
-----------------
1. SCANS  The Israel Museum's photograph of the whole scroll on its Digital Dead Sea Scrolls site
          (dss.collections.imj.org.il/community). The site's viewer (/viewer/data/community.json,
          cached in data/sources/qumran-1qs/imj/) serves the photograph as 250 px tiles from
          tiles.imj.org.il; zoom level 7 (16022 x 2250 px, 65 x 9 tiles) is fetched with a plain,
          honestly identified HTTP client (no access control on the tile server), stitched and
          cached as data/sources/qumran-1qs/imj/community_z7.jpg.
          Column crops: the viewer's own column table (ids 1-11) puts its cut lines through the
          edges of some columns, so the cut lines used here are the blank strips between the
          columns, found by an ink profile (count of dark pixels per x over rows 150-2150,
          smoothed over 25 px; minimum within 300 px of each viewer boundary) and checked by eye:
          x = 1515, 3143, 4548, 5944, 7413, 8996, 10726, 12450, 13691, 14774 (left to right:
          between columns XI|X, X|IX, ... II|I). Each crop keeps 80 px of margin on both sides.
          Every crop was read on screen: the first and last lines, the line count and distinctive
          short lines and blank spaces were matched to the transcription (recorded per section).
          Terms (dss.collections.imj.org.il/terms): "Website, text, and photos (c) The Israel
          Museum, Jerusalem, 2011. All rights reserved ... with the exception of single copies for
          research or private study." Used with credit under the library owner's instruction of
          2026-11-12 (COLLECTION_SPEC rule 9).
2. HEBREW The scroll's own text, column by column and line by line, from the ETCBC "dss"
          Text-Fabric dataset (github.com/ETCBC/dss, tf/2.0, the same pinned commit as
          scripts/import_1qisaa.py and scripts/import_qumran_1qphab.py), from the transcriptions
          of Martin G. Abegg Jr., James E. Bowley and Edward M. Cook; CC BY-NC 4.0. Every word
          carries its column and line. Reading and rendering reuse the functions of
          import_qumran_1qphab.py; in addition an editor's deletion "{ x }" followed by the
          editor's correction "(< y >)" is shown as {x} <y> (HTML-escaped).
3. ENGLISH W. H. Brownlee, "The Dead Sea Manual of Discipline: Translation and Notes",
          BASOR Supplementary Studies 10-12, New Haven: American Schools of Oriental Research,
          1951 (foreword dated July 1951). Brownlee translates the eleven columns line by line,
          prints the scroll's line numbers in his margin and marks each line division of the
          scroll with "|" in the running English. Transcribed by hand from the page images of the
          Internet Archive item american-schools-of-oriental-research-bulletin_1951_10-12 into
          data/sources/qumran-1qs/brownlee1951_translation.txt (conventions in its header) and
          proofread against the images; then compared word by word with the item's OCR
          (brownlee1951_djvu.txt): every difference was an OCR misreading or an OCR omission of
          words that are on the page.
          COPYRIGHT: published in the United States in 1951 (New Haven), so a renewal was due in
          1978 or 1979. No renewal exists: (a) The Online Books Page record for BASOR Supplementary
          Studies (onlinebooks.library.upenn.edu/webbin/cinfo/asorbulsup, checked 2026-11-12):
          "First renewed issue: no issue renewals found in CCE or CPRS"; "First renewed
          contribution in: no contribution renewals found in CCE or CPRS"; (b) the NYPL
          transcriptions of the Copyright Office renewal records (github.com/NYPL/cce-renewals,
          files 1976-1 to 1991-from-db, which hold 17,919 renewals of 1951 works) have no renewal
          by Brownlee, none for "Manual of Discipline" and none for the American Schools of
          Oriental Research. (The Stanford renewal database could not be queried: it serves a
          JavaScript bot check, which is not bypassed.) Public domain in the United States.
          LINE NUMBERS: the transcription carries markers {n} at the point where line n of the
          scroll begins (after Brownlee's "|", or where he printed none, before the English word
          that renders the first Hebrew word of the line), checked against the ETCBC Hebrew line
          by line; they are displayed as superscripts so Hebrew and English share one numbering.

GAPS: 1QS is complete in 11 columns, but the scroll began with at least one more column, now lost
(the top lines of column I are damaged). The Rule of the Congregation (1QSa) and the Rule of
Blessings (1QSb), once sewn to the end of the same scroll, are separate manuscripts in the
transcription and were not translated by Brownlee; they are not included.

Usage:
    python3 scripts/import_qumran_1qs.py           # build
    python3 scripts/import_qumran_1qs.py --force   # re-stitch / re-crop images
"""
import argparse
import html
import io
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_qumran_1qphab as qp  # noqa: E402  (shared Text-Fabric reader and Hebrew rendering)

ROOT = Path(__file__).resolve().parent.parent
KEY = "qumran-1qs"
PREFIX = f"verified-{KEY}-"
TID = f"{PREFIX}community-rule"
SRC = ROOT / "data" / "sources" / KEY
TF_DIR = SRC / "etcbc"
IMJ_DIR = SRC / "imj"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
ENGLISH = SRC / "brownlee1951_translation.txt"
TODAY = date.today().isoformat()
SCROLL = "1QS"

IMJ_PAGE = "http://dss.collections.imj.org.il/community"
IMJ_TERMS = "http://dss.collections.imj.org.il/terms"
IMJ_VIEWER_JSON = "http://dss.collections.imj.org.il/viewer/data/community.json"
IMJ_TILES = "http://tiles.imj.org.il/tiles/community/"
IMJ_ZOOM, IMJ_TILE, IMJ_W, IMJ_H = 7, 250, 16022, 2250   # zoom 7 = half of fullSize 32043 x 4500
IMJ_STITCHED = IMJ_DIR / "community_z7.jpg"
IA_ITEM = "https://archive.org/details/american-schools-of-oriental-research-bulletin_1951_10-12"
OBP_RECORD = "https://onlinebooks.library.upenn.edu/webbin/cinfo/asorbulsup"
NYPL_CCE = "https://github.com/NYPL/cce-renewals"

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI"}

# Blank strips between columns (left to right on the photograph: XI | X | ... | II | I).
GAPS = [1515, 3143, 4548, 5944, 7413, 8996, 10726, 12450, 13691, 14774]
MARGIN = 80


def crop_box(col):
    edges = [0] + GAPS + [IMJ_W]
    i = 11 - col                       # column XI is leftmost
    x0 = edges[i] - (MARGIN if i > 0 else 0)
    x1 = edges[i + 1] + (MARGIN if i < 10 else 0)
    return (max(0, x0), 0, min(IMJ_W, x1), IMJ_H)


# Per column: Brownlee's printed page(s), content, and what was checked on the image.
COLUMNS = {
    1: {"pages": "6, 8", "subject": "admission to the covenant of the Community; the covenant ceremony begins",
        "note": "Checked on the image: line 1 is broken along the top edge (ל at the right, ...היחד לדרוש at the left); "
                "line 20 is a short line ending אמן אמן with blank space after it; line 21 (והכוהנים מספרים) is indented; "
                "26 lines, the last (…משפטו בנו ובאבותינו) partly lost at the torn lower edge."},
    2: {"pages": "8, 10, 11", "subject": "blessings and curses of the covenant ceremony; the yearly order of entry",
        "note": "Checked on the image: line 1 begins ורחמי חסדו גמל עלינו; line 10 ends אמן אמן; line 11 (והוסיפו הכוהנים "
                "והלויים) is indented; line 18 is the short line וכול באי הברית יענו ואמרו אחריהם אמן אמן; 26 lines, the "
                "last partly lost at the torn lower edge."},
    3: {"pages": "11, 12, 14", "subject": "the one who refuses to enter; the Instruction on the Two Spirits begins",
        "note": "Checked on the image: line 1 begins נפשו ביסורי דעת משפטי צדק and ends לוא יתחשב; line 12 is the two words "
                "יחד עולמים alone; line 13 (למשכיל להבין וללמד) is indented after a blank space; 26 lines, the last "
                "(…אחת אהב אל לכול) partly lost at the torn lower edge."},
    4: {"pages": "14, 16, 18", "subject": "the ways of the spirits of truth and of perversion and their end",
        "note": "Checked on the image: line 1 begins עדי עולמים ובכול עלילותיה and ends שנא לנצח; line 8 is the short line "
                "עם מדת הדר באור עולמים; line 14 is the short line כלותם לאין שרית ופליטה למו; 26 lines, the last "
                "(…וינחילן לבני איש לדעת טוב) along the torn lower edge."},
    5: {"pages": "18, 20, 22", "subject": "the rule of the men of the Community; the oath of entry; separation from outsiders",
        "note": "Checked on the image: line 1 begins וזה הסרך לאנשי היחד המתנדבים; line 13 has a blank space before אל יבוא "
                "במים; 26 lines, the last (או בעורפ … ואל ישנאהו … יוכיחנו ולוא) on the torn lower edge. A seam of the "
                "scroll's sheets runs down the left edge of the crop."},
    6: {"pages": "22, 24, 26, 28", "subject": "common life, meals and study; sessions of the Many; admission of new members; the penal code begins",
        "note": "Checked on the image: line 1 begins ישא עליו עוון with a letter א written above the line near its end; "
                "line 23 is the short line ליחד ומשפטו; line 24 (ואלה המשפטים אשר ישפטו בם) is indented; 27 lines, the "
                "last (…הושיעה ידו) at the torn lower edge."},
    7: {"pages": "28, 30", "subject": "the penal code",
        "note": "Checked on the image: line 1 begins ואם קלל and ends והבדילהו; line 7 is the single word ברושו, followed by "
                "a wide uninscribed space before line 8, which has words written above it (ששים יום, שנה אחת); lines 22-23 "
                "are partly erased; 25 lines, the last (עמו בטהרתו או בהונו … לשלח) at the torn lower edge."},
    8: {"pages": "30, 32, 34", "subject": "the council of the Community; the way in the wilderness; rules for the men of perfect holiness",
        "note": "Checked on the image: line 1 reads בעצת היחד שנים עשר איש וכוהנים שלושה תמימים; a long addition is written "
                "above line 10; line 14 has four dots in place of the divine name (פנו דרך ····); the column ends with "
                "the single word ימים (line 27) at the lower right."},
    9: {"pages": "34, 36, 38", "subject": "end of the rules; until the prophet and the anointed ones of Aaron and Israel; the duties of the wise man",
        "note": "Checked on the image: line 1 begins כיא על … שגגה אחת יענש שנתים; line 11 is the short line עד בוא נביא "
                "ומשיחי אהרון וישראל; line 12 (אלה החוקים למשכיל) is indented after a blank space; 26 lines, the last "
                "(…יברך עושיו … שפתים יברכנו) at the torn lower edge."},
    10: {"pages": "38, 40, 41, 42", "subject": "the times of prayer; the closing hymn begins",
         "note": "Checked on the image: line 1 begins עם קצים אשר חקקא ברשית ממשלת אור; line 19 has words added above the line; "
                 "26 lines, the last (חוק בקו עתים … לניכנעים וחזוק ידים לנמהרי) at the torn lower edge."},
    11: {"pages": "42, 43, 44, 45, 46", "subject": "the closing hymn",
         "note": "Checked on the image: line 1 begins לתועי רוח בינה ולהשכיל רוכנים בלקח; line 22, the last of the column "
                 "and of the Community Rule, reads חמר קורצ ולעפר תשוקתו מה ישיב חמר ויוצר יד ולעצת מה יבין; the rest of "
                 "the sheet below it is uninscribed, and a row of stitch holes runs down the right edge of the sheet."},
}

# Places where a line of the scroll starts in Brownlee's English without a "|" before it,
# and other remarks on his line marks (checked against the Hebrew).
LINE_REMARKS = {
    3: "Lines 3, 13 and 16 begin at a new printed line or sentence of Brownlee's without a | before them.",
    8: "Line 10 carries a long addition written above it in the scroll; Brownlee translates it after the line (his "
       "margin numbers 10a, 9½, 10b, with | marks around the addition), so it all falls under line 10 here.",
    10: "In lines 1-26 Brownlee sets the text as verse; where a scroll line begins at the start of a verse line he "
        "printed the | at the end of the verse line before it.",
    11: "Line 21 has no | in Brownlee; its number is placed at “And [what is] that born of woman”, the "
        "rendering of וילוד אשה, the first words of line 21.",
}


def fetch(url):
    return qp.fetch(url)


# ---------------------------------------------------------------------------
# Hebrew
# ---------------------------------------------------------------------------
def tidy_hebrew(s):
    s = html.escape(s, quote=False)
    s = s.replace("{ }", "{…}")
    s = re.sub(r"(?<!\{)\{ ", "{", s)                       # { x } -> {x} (single braces only;
    s = re.sub(r" \}(?!\})", "}", s)                        # may span lines or hold {{ }})
    s = re.sub(r"\(&lt;\s*(.*?)\s*&gt;\)", r"&lt;\1&gt;", s)  # (< y >) -> <y>
    return s


def hebrew_columns():
    words = qp.load_words(SCROLL, TF_DIR)
    cols = {}
    for _s0, c, ln, f, a in words:
        cols.setdefault(c, {}).setdefault(ln, []).append((f, a))
    out = {}
    for c, lines in cols.items():
        parts = [f"<sup>{ln}</sup>{tidy_hebrew(qp.line_text(ws))}" for ln, ws in sorted(lines.items())]
        out[c] = {"html": "<br>".join(parts), "lines": len(lines), "nums": sorted(lines),
                  "first": qp.line_text(lines[min(lines)]), "last": qp.line_text(lines[max(lines)])}
    return out


# ---------------------------------------------------------------------------
# English
# ---------------------------------------------------------------------------
MARK = re.compile(r"\{(\d+)\}")


def parse_english():
    cols, cur = {}, None
    for raw in ENGLISH.read_text(encoding="utf-8").splitlines():
        if raw.startswith("## "):
            cur = int(raw[3:])
            cols[cur] = []
            continue
        if raw.startswith("#") or not raw.strip():
            continue
        _num, txt = raw.split("|", 1)
        kind = "p"
        if txt.startswith(">+"):
            kind, txt = "cont", txt[2:]
        elif txt.startswith(">"):
            kind, txt = "v", txt[1:]
        cols[cur].append([kind, txt])
    return cols


def _join(a, b):
    if a.endswith("="):
        return a[:-1] + b
    if a.endswith("-") and not a.endswith("—"):
        return a + b
    return a + " " + b


def render_column(rows):
    blocks = []          # ("p", text) or ("v", [lines])
    for kind, txt in rows:
        para = txt.startswith("¶")
        txt = txt.lstrip("¶")
        if kind == "cont":
            assert blocks and blocks[-1][0] == "v", txt
            blocks[-1][1][-1] = _join(blocks[-1][1][-1], txt)
        elif kind == "v":
            if blocks and blocks[-1][0] == "v" and not para:
                blocks[-1][1].append(txt)
            else:
                blocks.append(("v", [txt]))
        else:
            if blocks and blocks[-1][0] == "p" and not para:
                blocks[-1] = ("p", _join(blocks[-1][1], txt))
            else:
                blocks.append(("p", txt))
    out = []
    for kind, val in blocks:
        body = val if kind == "p" else "<br>".join(val)
        body = MARK.sub(lambda m: f"<sup>{m.group(1)}</sup>", body)
        out.append(f"<p>{body}</p>")
    return "".join(out)


def english_columns():
    parsed = parse_english()
    eng = {c: render_column(rows) for c, rows in parsed.items()}
    nums = {c: [int(n) for _k, t in rows for n in MARK.findall(t)] for c, rows in parsed.items()}
    return eng, nums


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def stitch_imj(force=False):
    IMJ_DIR.mkdir(parents=True, exist_ok=True)
    Image.MAX_IMAGE_PIXELS = None
    if IMJ_STITCHED.exists() and not force:
        return Image.open(IMJ_STITCHED).convert("RGB")
    canvas = Image.new("RGB", (IMJ_W, IMJ_H), (0, 0, 0))
    nx, ny = -(-IMJ_W // IMJ_TILE), -(-IMJ_H // IMJ_TILE)
    for y in range(ny):
        for x in range(nx):
            tile = Image.open(io.BytesIO(fetch(f"{IMJ_TILES}{IMJ_ZOOM}_{x}_{y}.jpg"))).convert("RGB")
            canvas.paste(tile, (x * IMJ_TILE, y * IMJ_TILE))
            time.sleep(0.15)
    canvas.save(IMJ_STITCHED, quality=92)
    return canvas


def image_name(c):
    return f"1qs-col-{c:02d}.jpg"


def build_images(force):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    todo = [c for c in range(1, 12) if force or not (SCAN_DIR / image_name(c)).exists()]
    if not todo:
        return
    im = stitch_imj(force)
    assert im.size == (IMJ_W, IMJ_H), im.size
    for c in todo:
        cr = im.crop(crop_box(c))
        cr.save(SCAN_DIR / image_name(c), quality=88)
        print(f"  {image_name(c)}: {cr.size}")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    build_images(args.force)

    heb = hebrew_columns()
    eng, eng_nums = english_columns()
    assert sorted(heb) == list(range(1, 12)), sorted(heb)
    assert sorted(eng) == list(range(1, 12)), sorted(eng)
    # every line of every column carries its number in both texts, in order
    for c in range(1, 12):
        assert heb[c]["nums"] == list(range(1, heb[c]["lines"] + 1)), (c, heb[c]["nums"])
        assert eng_nums[c] == heb[c]["nums"], (c, eng_nums[c], heb[c]["nums"])
    # spot checks that tie the transcription to what was read on the images
    assert "לחיו" in heb[1]["first"] and "לדרוש" in heb[1]["first"]
    assert heb[2]["first"].startswith("ורחמי חסדו")
    assert heb[3]["first"].startswith("נפשו ביסורי דעת")
    assert heb[4]["first"].startswith("עדי עולמים ובכול עלילותיה")
    assert heb[5]["first"].startswith("וזה הסרך לאנשי היחד")
    assert heb[6]["first"].startswith("ישא עליו עוון")
    assert heb[7]["first"].startswith("ואם קלל")
    assert heb[8]["first"].startswith("בעצת היחד שנים עשר איש")
    assert heb[8]["last"] == "ימים"
    assert heb[9]["first"].startswith("כיא על")
    assert heb[10]["first"].startswith("עם קצים")
    assert heb[11]["first"].startswith("לתועי רוח בינה") and heb[11]["last"].endswith("ולעצת מה יבין")
    assert eng[1].startswith("<p>[These are the ordinances] | <sup>1</sup>for [the whole assembly, including children")
    assert eng[11].endswith("And what counsel does he understand?</p>")

    sections = []
    for c in range(1, 12):
        meta = COLUMNS[c]
        note = (f"Image {image_name(c)} (Israel Museum photograph, column {ROMAN[c]}). " + meta["note"]
                + " Column and line numbers of the Hebrew come from the ETCBC/Abegg transcription. The English line "
                  "numbers stand where each line of the scroll begins in Brownlee's translation, at his | marks, and were "
                  "checked against the Hebrew line by line, so both texts carry the same numbers. English from Brownlee "
                  f"1951, pp. {meta['pages']}.")
        if c in LINE_REMARKS:
            note += " " + LINE_REMARKS[c]
        sections.append({
            "section": ROMAN[c],
            "original_ref": f"1QS col. {ROMAN[c]}, lines 1-{heb[c]['lines']} ({meta['subject']})",
            "original_text": heb[c]["html"],
            "text": eng[c],
            "scan_pages": [f"{KEY}/{image_name(c)}"],
            "scan_note": note,
        })

    entry = {
        "id": TID,
        "slug": TID,
        "title": "The Community Rule (1QS), columns I-XI",
        "language": "Hebrew (Qumran transcription) / English (W. H. Brownlee, 1951)",
        "source": "Israel Museum photograph of scroll 1QS (Digital Dead Sea Scrolls) + ETCBC dss transcription "
                  "(Abegg; CC BY-NC 4.0) + English of W. H. Brownlee, The Dead Sea Manual of Discipline (1951), public domain",
        "description": "The Community Rule from Qumran Cave 1, complete in eleven columns: the covenant ceremony, the "
                       "teaching on the two spirits, the rules and penal code of the Community and its closing hymn, each "
                       "column shown on the Israel Museum's photograph of the scroll.",
        "introduction": (
            "<p>The Community Rule (Hebrew <em>Serekh ha-Yahad</em>, 1QS; first published as the \"Manual of Discipline\") "
            "is one of the seven scrolls found in Qumran Cave 1 in 1947. It sets out how a man enters the covenant of the "
            "Community (the <em>yahad</em>), the yearly ceremony of blessings and curses, a teaching on the two spirits of "
            "truth and perversion that God set in mankind until the time of visitation, the rules for the common life, "
            "the sessions of \"the Many\" and the admission of new members, a penal code, the founding of the council of "
            "the Community as a \"house of holiness\" that prepares \"the way\" in the wilderness (Isaiah 40:3), and the "
            "duties of the wise man, and it closes with a long hymn. Column IX looks forward to \"the coming of a Prophet "
            "and the anointed ones of Aaron and Israel\". The scroll is kept in the Shrine of the Book at the Israel "
            "Museum, Jerusalem; on the evidence of its handwriting it is usually dated to about 100-75 BCE.</p>\n\n"
            "<p>Each section is one column of the scroll, shown on the Israel Museum's photograph. The Hebrew is the "
            "scroll's own text with its column and line numbers, from the transcription of Martin G. Abegg Jr. and "
            "colleagues in the ETCBC \"dss\" dataset. Square brackets mark letters lost from the leather and restored by "
            "the editors; a dot under a letter marks an uncertain reading; ⟨ ⟩ marks letters written above the line by "
            "the scribe; {{ }} marks letters the scribe cancelled; {x} &lt;y&gt; marks a slip of the scribe that the "
            "editors delete ({x}) and correct (&lt;y&gt;), and braces alone (VI 5-6) mark words written twice by mistake; an ellipsis marks lost letters that are not restored; four "
            "dots stand in the scroll in place of the divine name (VIII 14).</p>\n\n"
            "<p>The English is the complete translation of the scroll by William H. Brownlee, published by the American "
            "Schools of Oriental Research in 1951. Brownlee followed the scroll line by line and marked each line "
            "division with a vertical stroke (|) and the end of a column with a double stroke (||); the superscript "
            "numbers placed at his strokes give the line numbers of the scroll, the same as in the Hebrew. In his "
            "notation square brackets enclose words he supplied or restored, parentheses enclose parenthetical words "
            "of the Hebrew, and words between asterisks belong in the Hebrew to the line before. Words he printed in "
            "italics are written twice in the scroll; words struck through are words the scribe cancelled and "
            "replaced.</p>\n\n"
            "<p>Gaps: the scroll once began with at least one further column, now lost, and the top lines of column I "
            "are damaged; the lowest lines of most columns are broken along the torn lower edge. Two shorter works once "
            "sewn to the end of the same scroll, the Rule of the Congregation (1QSa) and the Rule of Blessings (1QSb), "
            "are separate manuscripts and are not included here.</p>"
        ),
        "translator_notes": [
            "Brownlee's translation of 1951 was made before the publication of the Cave 4 copies of the Community Rule; "
            "his restorations in square brackets sometimes differ from the restorations in the Hebrew transcription.",
            "Footnote numbers in Brownlee's text are omitted, as are the section headings he supplied (he says so in his "
            "table of contents). The line in capitals in column XI (\"TO PRAISE GOD FOR HIS RIGHTEOUSNESS ...\") "
            "translates the scroll's own words and is kept.",
            "Brownlee calls the document DSD (Dead Sea Discipline); the name Community Rule and the siglum 1QS came later.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Israel Museum, Jerusalem, The Digital Dead Sea Scrolls: {IMJ_PAGE} (viewer data "
                           f"{IMJ_VIEWER_JSON}; image tiles {IMJ_TILES}, zoom level 7, stitched)",
            "scan_license": "As stated by the Israel Museum (" + IMJ_TERMS + "): \"Website, text, and photos (c) The Israel "
                            "Museum, Jerusalem, 2011. All rights reserved. No part of this website may be downloaded, copied, "
                            "or reproduced in any form, analog or digital, without the permission of the Israel Museum, "
                            "Jerusalem, with the exception of single copies for research or private study.\" Shown here with "
                            "credit, \"Photo (c) The Israel Museum, Jerusalem\", in a non-commercial reference library.",
            "scan_manuscript": "1QS, Community Rule (Serekh ha-Yahad), Qumran Cave 1; Israel Museum, Jerusalem, Shrine of the "
                               "Book; parchment, 11 columns, about 100-75 BCE",
            "scan_mapping": "Each column was cropped at the blank strips between columns (found by an ink profile over the "
                            "stitched photograph and checked by eye), then read on screen: its first and last lines, its line "
                            "count and its distinctive short lines and blank spaces were matched to the column/line data of the "
                            "ETCBC transcription (recorded in the section notes).",
            "scan_mapping_urls": [IMJ_PAGE, IMJ_VIEWER_JSON],
            "scan_local_paths": [f"{KEY}/{image_name(c)}" for c in range(1, 12)],
            "original_text_source": f"ETCBC dss Text-Fabric dataset tf/2.0 (github.com/ETCBC/dss, commit {qp.ETCBC_COMMIT}), "
                                    "scroll 1QS, from the transcriptions of M. G. Abegg Jr., J. E. Bowley and E. M. Cook",
            "original_text_license": "CC BY-NC 4.0",
            "translation_source": "W. H. Brownlee, The Dead Sea Manual of Discipline: Translation and Notes (Bulletin of the "
                                  "American Schools of Oriental Research, Supplementary Studies 10-12), New Haven: American "
                                  f"Schools of Oriental Research, 1951, pp. 6-46; page images {IA_ITEM}, transcribed by hand",
            "translation_license": "Public domain in the United States: published in New Haven in 1951 and not renewed "
                                   "(renewal was due 1978-1979; Online Books Page record for the series, "
                                   f"{OBP_RECORD}: no issue or contribution renewals in CCE or CPRS; no renewal by Brownlee "
                                   f"or the ASOR in the Copyright Office renewal records 1976-1991 as transcribed by NYPL, {NYPL_CCE})",
            "translator": "W. H. Brownlee (1951)",
            "verified_date": TODAY,
        },
    }
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

    coll = {
        "collection": {
            "key": KEY,
            "prefix": PREFIX,
            "label": "The Community Rule (1QS)",
            "group": "Dead Sea Scrolls & Second Temple",
            "date_sort": -90,
            "author_name": "Qumran Cave 1 scroll (about 100-75 BCE)",
            "source_url": IMJ_PAGE,
            "critical_edition": "ETCBC dss Text-Fabric transcription (Abegg, Bowley, Cook)",
            "translator_name": "W. H. Brownlee (1951)",
            "original_lang_label": "Hebrew · Qumran transcription (Abegg, ETCBC)",
            "original_lang_code": "hbo",
            "edition_label": "",
            "search_terms": "dead sea scrolls qumran community rule manual of discipline serekh hayahad 1qs yahad two spirits "
                            "sons of light sons of darkness maskil many covenant essenes",
            "description": "The Community Rule (Manual of Discipline) from Qumran Cave 1, complete in eleven columns, on the "
                           "Israel Museum's photograph of the scroll, with the scroll's own Hebrew and W. H. Brownlee's 1951 "
                           "English.",
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
            "date_approx": "c. 100-75 BCE (copy); composition 2nd century BCE",
            "century": -1,
            "source": entry["source"],
            "description": entry["description"],
            "themes": ["dead-sea-scrolls", "qumran", "community-rule", "two-spirits", "covenant", "verified"],
            "is_first_translation": False,
            "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{image_name(c)}", "caption": f"1QS column {ROMAN[c]} (Israel Museum)"}
                                for c in range(1, 12)]},
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
