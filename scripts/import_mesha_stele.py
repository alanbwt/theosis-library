#!/usr/bin/env python3
"""
import_mesha_stele.py -- the Mesha Stele (Moabite Stone), Louvre AO 5066, c. 840 BCE.

One entry, eight sections of consecutive lines (34 lines in all), each with
Compston's Hebrew-letter text of those lines, his line-by-line English, and the
photograph of the inscribed face.

Chain of evidence
-----------------
1. ORIGINAL TEXT  H. F. B. Compston, The Inscription on the Stele of Mesa, commonly
                  called the Moabite Stone (SPCK, London, 1919), pp. 11-13,
                  "II. The Text in Hebrew square script" (public domain: published
                  1919; Compston d. 1931). Transcribed line by line by hand from the
                  printed page images (Wikimedia Commons djvu of the book, pages
                  11-13) into data/sources/mesha-stele/compston_hebrew_verified.txt.
                  The Wikisource transcription of these pages was used as a base and
                  corrected where it departs from the print (e.g. line 1 הד not הר,
                  line 3 ב[מת · י] not ב[נס, line 8 מהדבא, line 16 זה).
                  Overlined (uncertain) letters are shown with a combining overline,
                  restorations in [ ], blank space in the print as "…".
                  Compston's text in Phoenician letters (pp. 7-10) is not used: the
                  Wikisource transcription of it has errors (lines 3, 16, 30, 33) and
                  was not fully re-proofread.
2. ENGLISH        Compston 1919, pp. 14-16, "III. Translation", which is printed line
                  for line with the stele. Text from Wikisource (pages 14-15 validated,
                  page 16 proofread); page 16 checked against the page image
                  (line 22 corrected to "ʿōp̄el"). Compston's notes are kept as
                  translator notes.
3. PHOTOGRAPH     Wikimedia Commons, "F4171 Louvre stele de Mesha AO5066 rwk.jpg"
                  (Mbzt, 22 Oct 2020, CC BY-SA 4.0): the whole inscribed face.
4. MAPPING        Every section is on the one inscribed face, which the photograph
                  shows whole; the lines run right to left from the top. The line
                  numbers are Compston's, which follow the stele line for line.

Usage:
    python3 scripts/import_mesha_stele.py
"""

import json
import re
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "mesha-stele"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "ao5066"

PHOTO = SRC / "photos" / "F4171_Louvre_stele_de_Mesha_AO5066_rwk.jpg"
PHOTO_PAGE = "https://commons.wikimedia.org/wiki/File:F4171_Louvre_stele_de_Mesha_AO5066_rwk.jpg"
LOUVRE = "https://collections.louvre.fr/ark:/53355/cl010120339"
WS_BOOK = "https://en.wikisource.org/wiki/The_Inscription_on_the_Stele_of_M%C3%A9%C5%A1a%CA%BF"
DJVU = "https://commons.wikimedia.org/wiki/File:The_Inscription_on_the_Stele_of_M%C3%A9%C5%A1a_commonly_called_the_Moabite_Stone.djvu"
SCAN = f"{KEY}/mesha-stele-ao5066.jpg"

GROUPS = [
    (1, 4, "Mesha, king of Moab, and the high place for Chemosh"),
    (5, 9, "Omri king of Israel oppresses Moab; Medeba recovered"),
    (10, 13, "The capture of Ataroth from the men of Gad"),
    (14, 18, "The taking of Nebo; the vessels of YHWH dragged before Chemosh"),
    (19, 21, "Jahaz taken from the king of Israel"),
    (22, 25, "Building works at Qarhoh"),
    (26, 30, "Aroer, the Arnon road, Beth-bamoth, Bezer and other towns"),
    (31, 34, "Horonen (the end of the stele is broken)"),
]

# Wikisource text -> printed page (checked on the page image of p. 16)
TR_CORRECTIONS = [
    (22, "ʿōel", "ʿōp̄el"),
    (23, "reser[voirs? for wa]ter", "reser[voirs ? for wa]ter"),
]

SUP = {"e": "ᵉ", "a": "ᵃ", "é": "ᵉ́", "ǎ": "ᵃ̌"}


def wiki_inline(t):
    t = re.sub(r"\{\{[Ss]up\|([^}]*)\}\}", lambda m: SUP.get(m.group(1), m.group(1)), t)
    t = re.sub(r"\{\{\.\.\.\|\d+\}\}", '<span class="lacuna">…</span>', t)
    t = re.sub(r"''(.+?)''", r"<em>\1</em>", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def parse_np2(raw):
    """Parse {{np2|N|...}} with nested templates."""
    out = {}
    i = 0
    while True:
        j = raw.find("{{np2|", i)
        if j < 0:
            break
        k = j + 2
        depth = 1
        while depth and k < len(raw):
            if raw.startswith("{{", k):
                depth += 1
                k += 2
            elif raw.startswith("}}", k):
                depth -= 1
                k += 2
            else:
                k += 1
        inner = raw[j + 6:k - 2]
        n, body = inner.split("|", 1)
        out[int(n)] = body
        i = k
    return out


def translation():
    notes, lines = [], {}
    for n in (14, 15, 16):
        raw = (SRC / f"page_{n}.wiki").read_text(encoding="utf-8")
        raw = re.sub(r"<noinclude>.*?</noinclude>", "", raw, flags=re.S)
        # repair malformed ref tags in the Wikisource pages (missing closing quotes)
        raw = re.sub(r'<ref name="([^"/>]+?) ?/>', r'<ref name="\1"/>', raw)
        raw = re.sub(r'<ref name="([^"/>]+?)>', r'<ref name="\1">', raw)
        for m in re.finditer(r'<ref(?: name="[^"]*")?>(.*?)</ref>', raw, flags=re.S):
            notes.append(wiki_inline(m.group(1)))
        raw = re.sub(r"<ref[^>]*?/>", "", raw)
        raw = re.sub(r"<ref[^>]*>.*?</ref>", "", raw, flags=re.S)
        lines.update(parse_np2(raw))
    lines = {n: wiki_inline(t).replace(" & ", " &amp; ") for n, t in lines.items()}
    for n, old, new in TR_CORRECTIONS:
        assert lines[n].count(old) == 1, (n, old, lines[n])
        lines[n] = lines[n].replace(old, new)
    assert sorted(lines) == list(range(1, 35)), sorted(lines)
    return lines, notes


def hebrew():
    out = {}
    for ln in (SRC / "compston_hebrew_verified.txt").read_text(encoding="utf-8").splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        n, t = ln.split("|", 1)
        t = t.replace("…", '<span class="lacuna">…</span>')
        out[int(n)] = t
    assert sorted(out) == list(range(1, 35))
    return out


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    out = ROOT / "site" / "assets" / "scans" / SCAN
    if not out.exists():
        im = Image.open(PHOTO).convert("RGB")
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(out, quality=86)
    heb = hebrew()
    eng, notes = translation()

    sections = []
    for a, b, topic in GROUPS:
        orig = "<br>".join(f"<sup>{n}</sup>{heb[n]}" for n in range(a, b + 1))
        text = "<br>".join(f"<sup>{n}</sup>{eng[n]}" for n in range(a, b + 1))
        sections.append({
            "section": f"{a}-{b}",
            "original_ref": f"Mesha Stele (KAI 181) lines {a}-{b}: {topic}",
            "original_text": orig,
            "text": text,
            "scan_pages": [SCAN],
            "scan_note": (f"Lines {a}-{b} of the 34 lines on the inscribed face, which the photograph shows whole; the text runs "
                          f"right to left, line 1 under the rounded top. The stele was broken in 1869; the surviving pieces (rough, "
                          f"darker surface) are set in a plaster restoration (smooth surface) whose letters were supplied from the "
                          f"paper squeeze taken before the breakage, so part of these lines is on restored plaster rather than on "
                          f"the ancient stone. Line numbering follows Compston, who prints the text line for line with the stele."),
        })

    intro = (
        "<p>The <strong>Mesha Stele</strong>, or Moabite Stone, is a black basalt stele set up about 840 BCE by Mesha, king of Moab, "
        "at Dibon (Dhiban in Jordan). In 34 lines of Moabite, written in the old Hebrew-Phoenician alphabet, Mesha says that Omri, "
        "king of Israel, and his son oppressed Moab because the god Chemosh was angry with his land, and that Chemosh then gave "
        "Mesha victory: he took Ataroth, Nebo and Jahaz from Israel and dragged 'the vessels of YHWH' before Chemosh, and he "
        "rebuilt the towns of his kingdom. It is the longest Iron Age inscription from the lands east of the Jordan and names Omri, "
        "Israel and the God of Israel. Its story runs parallel to the account of Mesha's revolt in the Old Testament, 2 Kings 3:4-27.</p>"
        "<p>The stele was seen by the missionary F. A. Klein in 1868. Before it could be removed, a paper squeeze was taken for "
        "Charles Clermont-Ganneau, and in 1869 the stone was broken up by the local people. The larger pieces were recovered and are "
        "now in the Louvre (AO 5066), set in a plaster restoration based on the squeeze.</p>"
        "<p>The text is H. F. B. Compston's edition of 1919 in Hebrew square letters, with his line-by-line English translation. "
        "Square brackets mark his restorations, overlined letters are uncertain, and dots in the English mark words lost at the "
        "broken end of the stele. Each section groups a few lines and shows the photograph of the whole inscribed face.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Mesha Stele (Moabite Stone), Louvre AO 5066",
        "language": "Moabite (Hebrew square script, Compston 1919) / English (Compston 1919)",
        "source": "Louvre AO 5066 photograph (Wikimedia Commons, CC BY-SA 4.0) + H. F. B. Compston's 1919 text and translation (public domain)",
        "description": "The Mesha Stele (c. 840 BCE), in which Mesha king of Moab tells of his revolt against Omri's house of Israel and names YHWH, "
                       "line by line with Compston's 1919 text and translation and the photograph of the stele.",
        "introduction": intro,
        "translator_notes": [
            "Compston's English is printed line for line with the stele, so words broken between lines are hyphenated as he prints them.",
            "Compston: \"Words in italics are required by English idiom: they are not in the original. Words and letters within square brackets are restored conjecturally. Words within curved brackets are alternative renderings.\"",
        ] + [f"Compston's note: {re.sub(r'<[^>]+>', '', n)}" for n in notes],
        "translation": sections,
        "verification": {
            "scan_source": f"Wikimedia Commons, {PHOTO_PAGE} (photograph of Louvre AO 5066 by Mbzt, 22 October 2020)",
            "scan_license": "CC BY-SA 4.0 (photographer Mbzt)",
            "scan_manuscript": "Paris, Musée du Louvre AO 5066 (Mesha Stele, basalt, c. 840 BCE, from Dhiban, Jordan; reassembled pieces in plaster restoration)",
            "scan_mapping": "Single inscribed face shown whole in the photograph; sections are consecutive line groups (lines 1-34, top to bottom) as numbered by Compston, who follows the stele line for line",
            "scan_mapping_urls": [PHOTO_PAGE, LOUVRE, DJVU],
            "scan_local_paths": [SCAN],
            "original_text_source": f"H. F. B. Compston, The Inscription on the Stele of Mesa (SPCK 1919), pp. 11-13, transcribed from the page images ({DJVU}); Wikisource base text {WS_BOOK}",
            "original_text_license": "public domain (published 1919; Compston died 1931)",
            "translation_source": f"H. F. B. Compston, The Inscription on the Stele of Mesa (SPCK 1919), pp. 14-16, via Wikisource ({WS_BOOK}/Translation), page 16 checked against the page image",
            "translation_license": "public domain (published 1919; Compston died 1931)",
            "translator": "H. F. B. Compston (1919)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "mesha-moab",
        "language": "Moabite", "era": "Ancient Near East", "tradition": "canaanite", "category": "inscription",
        "date_approx": "c. 840 BCE", "century": -9, "source": entry["source"], "description": entry["description"],
        "themes": ["mesha", "moab", "omri", "israel", "yhwh", "chemosh", "2-kings", "stele", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": SCAN, "caption": "Mesha Stele, Louvre AO 5066"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Mesha Stele",
            "group": "Levant & Israel", "date_sort": -840,
            "author_name": "Mesha, king of Moab (c. 840 BCE)",
            "source_url": LOUVRE,
            "critical_edition": "H. F. B. Compston, The Inscription on the Stele of Mesa (1919)",
            "translator_name": "H. F. B. Compston (1919)",
            "original_lang_label": "Moabite · Hebrew square script (Compston)",
            "original_lang_code": "obm",
            "edition_label": "",
            "search_terms": "mesha stele moabite stone dibon omri israel yhwh chemosh kemosh 2 kings 3 louvre ao 5066 kai 181",
            "description": "The Mesha Stele (Moabite Stone, c. 840 BCE): Mesha of Moab's account of his revolt against the house of Omri, "
                           "line by line with Compston's 1919 text and translation and the photograph of the stele in the Louvre.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
