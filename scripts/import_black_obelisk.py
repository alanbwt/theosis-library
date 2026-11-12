#!/usr/bin/env python3
"""
import_black_obelisk.py -- the Black Obelisk of Shalmaneser III (British Museum, BM 118885),
Nimrud, about 825 BCE: the five epigraphs over the tribute reliefs, including the tribute of
Jehu of Israel.

One entry, five sections, one per epigraph (RIMA 3 A.0.102.87-91). Each epigraph is a single
line of Akkadian written above one of the five registers of reliefs, running round the four
faces of the obelisk above the four panels of that register.

Not included: the 190-line annals text (RIMA 3 A.0.102.14) written above and below the reliefs.
Neither ORACC nor CDLI divides its lines by face, no open source gives that division, and the
available face photographs (about 1,000 px wide) are too small to fix the line starts by eye.

Chain of evidence
-----------------
1. ORIGINAL TEXT  ORACC RIAo (Royal Inscriptions of Assyria online), Shalmaneser III 087-091
                  (Q004692-Q004696), from A. K. Grayson, RIMA 3 (1996), adapted by J. Novotny and
                  N. Morello; the HTML pages are saved in data/sources/black-obelisk/. Licence: CC BY-SA
                  3.0 (page credits); the RIAo JSON metadata states CC0.
2. ENGLISH        The same ORACC pages (English translation, CC BY-SA 3.0).
3. PHOTOGRAPHS    Wikimedia Commons, "Black Obelisk of Shalmaneser III - A side.jpg" ... "D side.jpg"
                  (Szilas, British Museum, 30 July 2010, CC BY-SA 4.0), each cropped to the five relief
                  registers with the epigraph lines between them; and "Jehu of the House of Omri bows
                  before the Assyrian king Shalmaneser III ... .JPG" (Osama Shukir Muhammed Amin,
                  2014, CC BY-SA 4.0), the second register of side A with its epigraph.
4. MAPPING        Epigraph n stands in the single line of signs directly above register n; each
                  register's scene "occupies four panels around the monument and is described by a
                  cuneiform script above them" (Wikipedia, 'Black Obelisk of Shalmaneser III'); the
                  order of the epigraphs follows RIMA 3 (87 Sua of Gilzanu, 88 Jehu, 89 Musri,
                  90 Marduk-apla-usur of Suhu, 91 Qalparunda of Patina), which matches the scenes in
                  the photographs (checked on the images: register 1 a prostrate ruler before the king,
                  2 the king under a parasol with a prostrate ruler (side A), 3 two-humped camels,
                  4 lions and a stag among trees, 5 tribute bearers; one line of signs above each
                  register on all four faces, continuing round the corner in the side A close-up).

Usage:
    python3 scripts/import_black_obelisk.py
"""

import html
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "black-obelisk"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "epigraphs"

ORACC = "https://oracc.museum.upenn.edu/riao/"
COMMONS = "https://commons.wikimedia.org/wiki/File:"
FACES = {  # face: (source file, crop box covering registers 1-5 with the epigraph lines)
    "A": ("szilas_A.jpg", (40, 500, 1249, 3080)),
    "B": ("szilas_B.jpg", (60, 520, 1051, 3100)),
    "C": ("szilas_C.jpg", (60, 430, 1010, 2950)),
    "D": ("szilas_D.jpg", (60, 340, 864, 2900)),
}
FACE_PAGES = {f: f"{COMMONS}Black_Obelisk_of_Shalmaneser_III_-_{f}_side.jpg" for f in FACES}
JEHU = ("osama_jehu_panel.jpg", f"{KEY}/black-obelisk-side-a-register-2-jehu.jpg")
JEHU_PAGE = (f"{COMMONS}Jehu_of_the_House_of_Omri_bows_before_the_Assyrian_king_Shalmaneser_III,"
             "_The_Black_Obelisk_of_Shalmaneser_III,_from_Nimrud,_Iraq._The_British_Museum.jpg")
WIKI = "https://en.wikipedia.org/wiki/Black_Obelisk_of_Shalmaneser_III"

EPIGRAPHS = [  # (register, ORACC Q, RIMA no., short title, what the register shows)
    (1, "Q004692", "A.0.102.87", "Sua of Gilzanu", "a ruler prostrate before the king, and tribute bearers with horses"),
    (2, "Q004693", "A.0.102.88", "Jehu of Israel", "the king under a parasol with a ruler prostrate at his feet (side A), and the Israelite tribute bearers"),
    (3, "Q004694", "A.0.102.89", "Musri", "two-humped camels and other animals"),
    (4, "Q004695", "A.0.102.90", "Marduk-apla-usur of Suhu", "lions and a stag among trees (side A), and tribute bearers"),
    (5, "Q004696", "A.0.102.91", "Qalparunda of Patina", "tribute bearers"),
]


def render_tlit(cell):
    """ORACC transliteration cell -> HTML: determinatives kept as superscripts, all other markup dropped."""
    cell = re.sub(r"<sup[^>]*>(.*?)</sup>", lambda m: "\x01" + m.group(1) + "\x02", cell, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
    t = t.replace("&", "&amp;").replace("<", "&lt;")
    return re.sub(r"\s+", " ", t).replace("\x01", "<sup>").replace("\x02", "</sup>")


def oracc(q):
    h = (SRC / f"{q}.html").read_text(encoding="utf-8")
    tl = [render_tlit(m.group(1)) for m in re.finditer(r'<td class="tlit">(.*?)</td>', h, flags=re.S)]
    tl = [t for t in tl if t]
    en = [html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1)))).strip()
          for m in re.finditer(r'<td class="t1 xtr"[^>]*>(.*?)</td>', h, flags=re.S)]
    assert len(tl) == 1 and len(en) == 1, (q, tl, en)
    en = re.sub(r"^\(1\)\s*", "", en[0])
    return tl[0], en


def save_scan(src, box, out, max_side=2600):
    dest = ROOT / "site" / "assets" / "scans" / out
    if not dest.exists():
        im = Image.open(SRC / "photos" / src).convert("RGB")
        if box:
            im = im.crop(box)
        s = min(1.0, max_side / max(im.size))
        if s < 1:
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(dest, quality=88)
    return out


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    faces = {f: save_scan(src, box, f"{KEY}/black-obelisk-side-{f.lower()}-registers.jpg") for f, (src, box) in FACES.items()}
    jehu = save_scan(JEHU[0], None, JEHU[1])

    sections = []
    for reg, q, rima, who, scene in EPIGRAPHS:
        akk, eng = oracc(q)
        scans = [faces[f] for f in "ABCD"]
        note = (f"Epigraph {reg} ({who}) is the single line of signs directly above register {reg} (counting from the top), "
                f"which shows {scene}. The line runs round the obelisk above the four panels of the register, so all four "
                f"face photographs (sides A-D) are given; on each, register {reg} is the {['first', 'second', 'third', 'fourth', 'fifth'][reg - 1]} "
                f"framed relief from the top and the epigraph is the band of signs immediately above its frame.")
        if reg == 1:
            note += (" Above register 1 the epigraph is the lowest line of the inscribed zone over the reliefs; the lines above it "
                     "belong to the annals text, which is not given here.")
        if reg == 2:
            scans = [jehu] + scans
            note += (" The first image is a close view of side A, register 2 (Jehu prostrate before Shalmaneser III), with the "
                     "epigraph line above the panel continuing round the corner onto the next face.")
        sections.append({
            "section": f"ep{reg}",
            "original_ref": f"RIMA 3 {rima} (ORACC RIAo Shalmaneser III {int(rima.split('.')[-1]):03d}), epigraph over register {reg}: {who}",
            "original_text": f"<sup>1</sup>{akk}",
            "text": f"<sup>1</sup>{eng}",
            "scan_pages": scans,
            "scan_note": note,
        })

    intro = (
        "<p>The <strong>Black Obelisk</strong> of Shalmaneser III, king of Assyria (858-824 BCE), is a four-sided pillar of black "
        "limestone about two metres high with a stepped top, set up at Nimrud (ancient Kalhu) about 825 BCE and found there by "
        "Austen Henry Layard in 1846. It is in the British Museum (BM 118885). Five registers of reliefs run round its four sides, "
        "each showing the tribute of one land; above each register a single line of cuneiform, an epigraph, names the ruler and "
        "lists what he brought. A long annals text of 190 lines, recording the king's campaigns year by year, is written above "
        "and below the reliefs.</p>"
        "<p>The second epigraph records the tribute of 'Jehu (Iāūa) of Bīt-Ḫumrî', that is Jehu, king of Israel (2 Kings 9-10), "
        "described as 'son of Omri' because the Assyrians called Israel 'the house of Omri'; the relief beneath it on side A "
        "shows him, or his envoy, prostrate before the Assyrian king. It is often cited as the only known ancient picture of "
        "an Israelite king.</p>"
        "<p>This entry gives the five epigraphs in the Akkadian transliteration and English of ORACC (based on A. K. Grayson, "
        "RIMA 3, 1996), each with photographs of the four faces. The annals text is not included: no openly available edition "
        "divides its 190 lines by face, so its lines cannot yet be matched to the photographs.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Black Obelisk of Shalmaneser III: the five epigraphs (Jehu's tribute), BM 118885",
        "language": "Akkadian (ORACC transliteration) / English (ORACC, after Grayson)",
        "source": "British Museum BM 118885, photographs on Wikimedia Commons (CC BY-SA 4.0) + ORACC RIAo text and translation (CC BY-SA 3.0)",
        "description": "The five tribute captions of Shalmaneser III's Black Obelisk (about 825 BCE), including the tribute of Jehu of "
                       "Israel, with ORACC's Akkadian and English and photographs of the four sides.",
        "introduction": intro,
        "translator_notes": [
            "ORACC renders the epithet of Jehu, literally 'son of Omri', as '(Bīt)-Ḫumrî (Israel; lit. \"son of Omri\")'.",
            "The transliteration follows ORACC: Sumerian word-signs in capitals; determinatives are raised (m before a man's name), and KUR (land) and GIŠ (wood) are written before the word with a full stop.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": (f"Wikimedia Commons: {FACE_PAGES['A']}, {FACE_PAGES['B']}, {FACE_PAGES['C']}, {FACE_PAGES['D']} "
                            f"(Szilas, British Museum, 30 July 2010); {JEHU_PAGE} (Osama Shukir Muhammed Amin, 30 January 2014)"),
            "scan_license": "CC BY-SA 4.0 (all five photographs, as stated on Commons)",
            "scan_manuscript": "London, British Museum BM 118885 (Black Obelisk of Shalmaneser III, black limestone, Nimrud, about 825 BCE; found by A. H. Layard 1846)",
            "scan_mapping": ("Each epigraph is the line directly above its relief register (registers numbered from the top, order as in RIMA 3 "
                             "A.0.102.87-91 and as shown by the scenes); the line runs round all four faces, so each section lists the four face crops"),
            "scan_mapping_urls": list(FACE_PAGES.values()) + [JEHU_PAGE, WIKI] + [f"{ORACC}{q}/" for _, q, *_ in EPIGRAPHS],
            "scan_local_paths": [faces[f] for f in "ABCD"] + [jehu],
            "original_text_source": "ORACC RIAo Shalmaneser III 087-091 (Q004692-Q004696), after A. K. Grayson, RIMA 3 (1996): " + ", ".join(f"{ORACC}{q}/" for _, q, *_ in EPIGRAPHS),
            "original_text_license": "CC BY-SA 3.0 (ORACC page credits; RIAo JSON metadata states CC0)",
            "translation_source": "ORACC RIAo Shalmaneser III 087-091, English translation (after Grayson, RIMA 3, adapted by J. Novotny and N. Morello)",
            "translation_license": "CC BY-SA 3.0 (ORACC page credits)",
            "translator": "A. K. Grayson / ORACC RIAo",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "shalmaneser-iii",
        "language": "Akkadian", "era": "Ancient Near East", "tradition": "mesopotamian", "category": "inscription",
        "date_approx": "about 825 BCE", "century": -9, "source": entry["source"], "description": entry["description"],
        "themes": ["black-obelisk", "shalmaneser-iii", "jehu", "omri", "israel", "assyria", "tribute", "2-kings", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": jehu, "caption": "Black Obelisk, side A, register 2: Jehu"}] +
                  [{"file": faces[f], "caption": f"Black Obelisk, side {f}, registers 1-5"} for f in "ABCD"]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Black Obelisk of Shalmaneser III",
            "group": "Mesopotamia", "date_sort": -825,
            "author_name": "Shalmaneser III, king of Assyria (858-824 BCE)",
            "source_url": f"{ORACC}Q004693/",
            "critical_edition": "A. K. Grayson, RIMA 3 (1996), A.0.102.87-91, via ORACC RIAo",
            "translator_name": "A. K. Grayson / ORACC RIAo",
            "original_lang_label": "Akkadian · ORACC transliteration",
            "original_lang_code": "akk",
            "edition_label": "",
            "search_terms": "black obelisk shalmaneser iii jehu omri israel tribute nimrud kalhu layard british museum bm 118885 sua musri patina suhu",
            "description": "The five tribute captions of Shalmaneser III's Black Obelisk (about 825 BCE), among them the tribute of Jehu of "
                           "Israel, with ORACC's text and translation and photographs of the four sides.",
        },
        "texts": [row],
        "authors": [{"id": "shalmaneser-iii", "name": "Shalmaneser III", "dates": "reigned 858-824 BCE", "century": -9,
                     "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian",
                     "bio": "King of Assyria whose annals record battles with Ahab and the tribute of Jehu of Israel."}],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
