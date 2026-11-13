#!/usr/bin/env python3
"""
import_cyrus_cylinder.py -- the Cyrus Cylinder (British Museum BM 90920), Babylon, after 539 BCE.
PARTIAL: lines 6-36 of 45 (46 in ARIo), the part that the available photographs show.

One entry, nine sections, one per paragraph of the ARIo English (lines 6-8, 9-14, 15-17, 18-19,
20-22, 23-25, 26-29, 30-32, 33-36; 9-14 joins ARIo's paragraphs 9-10 and 11b-14), each with the ARIo
Akkadian of those lines, the ARIo English and the photograph(s) of the side of the cylinder that
carries them.  Sections break at line boundaries in both columns (see A_PARTS).

Chain of evidence
-----------------
1. ORIGINAL TEXT  ORACC ARIo (Achaemenid Royal Inscriptions online) Q006653, "Cyrus II 1"
                  (I. Finkel's text adapted by A. Bartelmus and J. Novotny), saved as
                  data/sources/cyrus-cylinder/Q006653.html. Licence CC BY-SA 3.0 (page credits).
                  Determinatives are kept as superscripts; nothing else is changed.
2. ENGLISH        Same page, translation by J. Novotny (CC BY-SA 3.0). ARIo divides its English into
                  paragraphs; a paragraph sometimes begins inside a line (e.g. "(23b)"); the clause that renders
                  the first part of that line is moved to the section that carries the line (A_PARTS).
3. PHOTOGRAPHS    Wikimedia Commons, "Cyrus Cylinder front.jpg" and "Cyrus Cylinder back.jpg"
                  (Prioryman, British Museum, CC BY-SA 3.0). The back view was taken from behind the
                  display case, so its text is upside down; it is turned 180 degrees here so that the
                  text stands upright. Each is cropped to the cylinder.
4. MAPPING        The lines run along the length of the cylinder and follow one another round it, so
                  each photograph shows a band of lines. The bands were identified by matching the
                  damage on the photographs with H. C. Rawlinson's line-numbered copy of the cylinder
                  (V R 35, 1880, public domain; Commons "Barrel cylinder of Cyrus (transcription).jpg",
                  saved as rawlinson_1880_VR35_copy.jpg), and with ARIo's brackets:
                  - back view (turned upright): the break that runs down from the upper edge between
                    about one third and two thirds of the line length is the lacuna of lines 5-11 in
                    Rawlinson (lines 5-8 broken in the middle with the line starts preserved, narrowing
                    in lines 9-11; ARIo brackets in the middle of lines 6-11). At the upper edge the
                    preserved start of line 5 stands at the left and the ends of lines 3-5 at the right.
                    Below the break about a dozen further lines are visible, which are lines 12 to about 22.
                  - front view: the large break with a crack running down from it, at about 57-76 % of
                    the line length, is the lacuna of lines 21-31 in Rawlinson (narrow in 21-23, widest
                    in 24-29, narrowing in 30-31; ARIo brackets at that point in lines 24-31). Its tip is
                    at the upper edge (line 21); the lines below the break are lines 32 onward.
                  Lines 20-22 lie at the lower edge of the back view and the upper edge of the front
                  view; that section lists both photographs.
   NOT PUBLISHED  Lines 1-5 (only line 5 and the ends of lines 3-4 reach the edge of the back view)
                  and lines 37-46 (on the underside of the cylinder as displayed, not shown in any
                  openly available photograph; the British Museum's own images are behind a bot check).
                  ARIo's text of lines 36-45 also draws on the Yale fragment NBC 2504, which is not part
                  of the British Museum cylinder.

Usage:
    python3 scripts/import_cyrus_cylinder.py
"""

import html
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "cyrus-cylinder"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "bm-90920"

ARIO = "https://oracc.museum.upenn.edu/ario/Q006653/"
FRONT_PAGE = "https://commons.wikimedia.org/wiki/File:Cyrus_Cylinder_front.jpg"
BACK_PAGE = "https://commons.wikimedia.org/wiki/File:Cyrus_Cylinder_back.jpg"
RAWL_PAGE = "https://commons.wikimedia.org/wiki/File:Barrel_cylinder_of_Cyrus_(transcription).jpg"
BACK = f"{KEY}/cyrus-cylinder-back-view-lines-5-22.jpg"
FRONT = f"{KEY}/cyrus-cylinder-front-view-lines-20-36.jpg"

# first line of each section -> (last line, images, where).  A section is one ARIo paragraph, except 9-14
# (ARIo 9-10 and 11b-14: its English for lines 10 and 11 is interwoven, so the two are kept together).
SECTIONS = {
    6: (8, [BACK], "in the band of lines broken in the middle by the break that runs down from the upper edge (Rawlinson's lacuna in lines 5-11); the starts of these lines are preserved at the left of the break"),
    9: (14, [BACK], "lines 9-10 where the break narrows towards its lower end (Rawlinson's lacuna in lines 9-11), line 11 at the lower end of the break, lines 12-14 the first complete lines below it"),
    15: (17, [BACK], "the fourth to sixth complete lines below the break, in the middle of the photograph"),
    18: (19, [BACK], "the seventh and eighth lines below the break, in the lower half of the photograph"),
    20: (22, [BACK, FRONT], "at the lower edge of the back view and at the upper edge of the front view, where line 21 is the first line touched by the tip of the large break"),
    23: (25, [FRONT], "the upper part of the large break (Rawlinson's lacuna in lines 21-31) interrupts these lines at about 60-75 % of their length"),
    26: (29, [FRONT], "the widest part of the large break interrupts these lines at about 57-76 % of their length"),
    30: (32, [FRONT], "lines 30-31 are interrupted by the lower end of the large break, line 32 is the first complete line below it"),
    33: (36, [FRONT], "the second to fifth lines below the large break, crossed by the crack that runs down from it"),
}


# ARIo begins some paragraphs inside a line ('(23b)') and translates the first part of that line (23a) at
# the end of the previous paragraph.  These are the clauses that render the a-parts (checked against the
# Akkadian: 23a i-na ul-ṣi ù ri-ša-a-tim i-na É.GAL ma-al-ki ar-ma-a šu-bat be-lu-tú; 26a an-ḫu-ut-su-un
# ú-pa-áš-ši-ḫa ú-ša-ap-ṭi-ir sa-ar-ma-šu-nu; 30a bi-lat-su-nu ka-bi-it-tim ú-bi-lu-nim-ma qé-er-ba šu-an-na.KI
# ú-na-áš-ši-qu še-pu-ú-a).  They are moved to the section that carries the line, so that every section's
# English covers the same lines as its Akkadian (QC 2026-11-12).
A_PARTS = {
    23: "amidst joy and happiness, I took up (my) lordly residence in the palace of the ruler.",
    26: "I allowed (them) to find rest for their exhaustion (and) I relieved (them) off their ...",
    30: "brought their substantial tribute inside Šuanna (Babylon) (and) kissed my feet.",
}


def render_tlit(cell):
    """ORACC transliteration cell -> HTML: determinatives kept as superscripts, all other markup dropped."""
    cell = re.sub(r"<sup[^>]*>(.*?)</sup>", lambda m: "\x01" + m.group(1) + "\x02", cell, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
    t = t.replace("&", "&amp;").replace("<", "&lt;")
    return re.sub(r"\s+", " ", t).replace("\x01", "<sup>").replace("\x02", "</sup>")


def parse():
    h = (SRC / "Q006653.html").read_text(encoding="utf-8")
    lines, paras = {}, {}
    for m in re.finditer(r'<tr id="Q006653\.\d+" class="l"[^>]*>(.*?)</tr>', h, flags=re.S):
        r = m.group(1)
        n = int(re.search(r'<span class="xlabel ">([^<]*)</span>', r).group(1))
        lines[n] = render_tlit(re.search(r'<td class="tlit">(.*?)</td>', r, flags=re.S).group(1))
        tr = re.search(r'<td class="t1 xtr"[^>]*rowspan="(\d+)"[^>]*>(.*?)</td>', r, flags=re.S)
        if tr:
            en = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", tr.group(2)))).strip()
            paras[n] = (n + int(tr.group(1)) - 1, en)
    assert sorted(lines) == list(range(1, 47)), sorted(lines)
    return lines, paras


def save(src, box, out, rotate=False):
    dest = ROOT / "site" / "assets" / "scans" / out
    if not dest.exists():
        im = Image.open(SRC / "photos" / src).convert("RGB")
        if rotate:
            im = im.rotate(180)
        im = im.crop(box)
        s = min(1.0, 2600 / max(im.size))
        if s < 1:
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(dest, quality=88)


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    save("Cyrus_Cylinder_back_Prioryman.jpg", (70, 520, 2930, 1800), BACK, rotate=True)
    save("Cyrus_Cylinder_front_Prioryman.jpg", (90, 120, 2910, 1330), FRONT)
    lines, paras = parse()

    sections = []
    for a, (b, scans, where) in SECTIONS.items():
        parts = [k for k in sorted(paras) if a <= k <= b]
        assert parts[0] == a and paras[parts[-1]][0] == b, (a, b, parts)
        en = " ".join(paras[k][1] for k in parts)
        en = re.sub(r"\((\d+[ab]?)\)\s*", lambda m: f"<sup>{m.group(1)}</sup>", en)
        carry = ""
        if a in A_PARTS:  # the a-part of the first line, which ARIo translates in the previous paragraph
            en = f"<sup>{a}</sup>{A_PARTS[a]} " + en
            carry += (f" ARIo begins its paragraph inside line {a} ('({a}b)') and translates the first part of line {a} "
                      f"at the end of the previous paragraph; that clause ('{A_PARTS[a]}') is given here, with line {a}.")
        if b + 1 in A_PARTS:
            assert en.endswith(" " + A_PARTS[b + 1]), (a, en[-120:])
            en = en[: -len(A_PARTS[b + 1]) - 1]
            carry += (f" The last clause of ARIo's paragraph, which renders the first part of line {b + 1}, is given in the "
                      f"next section with that line.")
        sections.append({
            "section": f"{a}-{b}",
            "original_ref": f"Cyrus Cylinder (ARIo Cyrus II 1) lines {a}-{b}",
            "original_text": "<br>".join(f"<sup>{n}</sup>{lines[n]}" for n in range(a, b + 1)),
            "text": en,
            "scan_pages": scans,
            "scan_note": (f"Lines {a}-{b}: {where}. The lines run along the cylinder and follow one another round it; the bands "
                          f"shown in each photograph were identified by matching the breaks with Rawlinson's line-numbered copy "
                          f"(V R 35, 1880) and with the brackets of the ARIo text (see the importer). Brackets mark restorations "
                          f"that are not on the cylinder." + carry),
        })

    intro = (
        "<p>The <strong>Cyrus Cylinder</strong> is a barrel-shaped clay cylinder inscribed in Babylonian cuneiform for Cyrus II "
        "(the Great), king of Persia, after he took Babylon in 539 BCE. It was buried in the foundations of the city wall of "
        "Babylon, where it was found in 1879 by Hormuzd Rassam; it is in the British Museum (BM 90920). The text says that "
        "Nabonidus, the last king of Babylon, neglected the cult of Marduk, that Marduk chose Cyrus, who entered Babylon "
        "without a battle, and that Cyrus returned the gods of many cities to their shrines and gathered their peoples back "
        "to their settlements. This policy is often compared with the decree of Cyrus in the Old Testament that allowed the "
        "Jews to return to Jerusalem and rebuild the temple (Ezra 1:1-4; 2 Chronicles 36:22-23), although the cylinder names "
        "only Mesopotamian cities and gods.</p>"
        "<p>This entry is <strong>partial</strong>. It gives lines 6-36, which the two available photographs show: the side "
        "with lines 5-22 and the side with lines 20-36. Lines 1-5 and 37-46 are not included, because no openly available "
        "photograph shows them (the beginning of the text is badly broken, and the last lines are on the side that rests on "
        "the stand). The Akkadian and English are ARIo's edition (after I. Finkel), divided into ARIo's paragraphs.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Cyrus Cylinder, lines 6-36 (BM 90920)",
        "language": "Akkadian (ARIo transliteration) / English (ARIo, J. Novotny)",
        "source": "British Museum BM 90920, photographs by Prioryman on Wikimedia Commons (CC BY-SA 3.0) + ORACC ARIo text and translation (CC BY-SA 3.0)",
        "description": "The Cyrus Cylinder (after 539 BCE), Cyrus the Great's account of his entry into Babylon and the return of the "
                       "gods and peoples, lines 6-36 with ARIo's text and translation and photographs of the cylinder.",
        "introduction": intro,
        "translator_notes": [
            "ARIo's English is divided into paragraphs that do not always begin at a line start; a number such as 23b marks a paragraph that begins inside line 23. ARIo translates the first part of such a line (23a) at the end of the previous paragraph; that clause is moved to the section that carries the line, so each section's English covers the same lines as its Akkadian. Lines 9-14 form one section because ARIo's English for lines 10 and 11 is interwoven.",
            "The transliteration follows ARIo: Sumerian word-signs in capitals, determinatives raised (m before a man's name, d before a god's name), half brackets for damaged signs, square brackets for restorations.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Wikimedia Commons: {BACK_PAGE} and {FRONT_PAGE} (Prioryman, British Museum)",
            "scan_license": "CC BY-SA 3.0 (both photographs, as stated on Commons)",
            "scan_manuscript": "London, British Museum BM 90920 (1880,0617.1941), Cyrus Cylinder, clay, Babylon, after 539 BCE",
            "scan_mapping": ("Bands of lines on each photograph identified by matching the breaks with Rawlinson's line-numbered copy "
                             "(V R 35, 1880) and with ARIo's brackets: back view (turned upright) lacuna of lines 5-11, front view "
                             "lacuna of lines 21-31; lines counted outward from those breaks"),
            "scan_mapping_urls": [BACK_PAGE, FRONT_PAGE, RAWL_PAGE, ARIO],
            "scan_local_paths": [BACK, FRONT],
            "original_text_source": f"ORACC ARIo Q006653 (Cyrus II 1), adapted from I. Finkel by A. Bartelmus and J. Novotny: {ARIO}",
            "original_text_license": "CC BY-SA 3.0 (ORACC page credits)",
            "translation_source": f"ORACC ARIo Q006653, English translation by J. Novotny: {ARIO}",
            "translation_license": "CC BY-SA 3.0 (ORACC page credits)",
            "translator": "J. Novotny (ARIo)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "cyrus-ii",
        "language": "Akkadian", "era": "Ancient Near East", "tradition": "persian", "category": "inscription",
        "date_approx": "after 539 BCE", "century": -6, "source": entry["source"], "description": entry["description"],
        "themes": ["cyrus", "cyrus-cylinder", "babylon", "marduk", "nabonidus", "persia", "ezra", "return-from-exile", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": BACK, "caption": "Cyrus Cylinder, side with lines 5-22 (turned upright)"},
                            {"file": FRONT, "caption": "Cyrus Cylinder, side with lines 20-36"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Cyrus Cylinder",
            "group": "Persia", "date_sort": -539,
            "author_name": "Cyrus II (the Great), king of Persia (559-530 BCE)",
            "source_url": ARIO,
            "critical_edition": "ORACC ARIo Cyrus II 1 (after I. Finkel)",
            "translator_name": "J. Novotny (ARIo)",
            "original_lang_label": "Akkadian · ARIo transliteration",
            "original_lang_code": "akk",
            "edition_label": "",
            "search_terms": "cyrus cylinder cyrus the great babylon marduk nabonidus british museum bm 90920 ezra return persia achaemenid",
            "description": "The Cyrus Cylinder (after 539 BCE), Cyrus the Great's account of taking Babylon and restoring its gods and "
                           "peoples: lines 6-36 with ARIo's text and translation and photographs of the cylinder.",
        },
        "texts": [row],
        "authors": [{"id": "cyrus-ii", "name": "Cyrus II (the Great)", "dates": "reigned 559-530 BCE", "century": -6,
                     "era": "Ancient Near East", "tradition": "persian", "language": "Old Persian",
                     "bio": "Founder of the Achaemenid Persian empire, who took Babylon in 539 BCE; named in Isaiah and Ezra."}],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
