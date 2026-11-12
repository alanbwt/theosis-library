#!/usr/bin/env python3
"""
import_tel_dan_stele.py -- the Tel Dan stele ("House of David" inscription), Israel Museum,
Jerusalem (IAA 1993-3162 and 1996-125), Aramaic, second half of the 9th century BCE.

One entry, two sections (lines 1-7 and 8-13). Each section has, per line, the Biran-Naveh text
in Phoenician (Old Aramaic) letters as given in English Wikipedia, the same letters converted
one-for-one to Hebrew square letters, and Wikipedia's romanization; the English is Biran's 1995
translation as quoted in Wikipedia. The photograph shows the three fragments as joined in Jerusalem.

Chain of evidence
-----------------
1. ORIGINAL TEXT  English Wikipedia, "Tel Dan stele", section "Text" (revision REVID below):
                  "the transcription ... text inside square brackets is reconstructed by Biran and
                  Naveh", lines 1-13 in Phoenician Unicode letters, and the "Romanized" list.
                  Saved as data/sources/tel-dan-stele/enwiki_tel_dan.wiki. Licence CC BY-SA 4.0.
                  The square-script line is a mechanical one-for-one letter conversion of the
                  Phoenician-letter line (table PHN2HEB below, no final forms); it adds no reading.
2. ENGLISH        Same article: "The 1995 translation by Biran reads" (A. Biran and J. Naveh,
                  "The Tel Dan Inscription: A New Fragment", Israel Exploration Journal 45, 1995),
                  numbered 1-13. Wikipedia text CC BY-SA 4.0; the translation itself is quoted there
                  from Biran and Naveh, as the owner's instruction for post-1929 finds allows.
3. PHOTOGRAPH     Wikimedia Commons, "Aramaic Inscription on Basalt Monument, Dan, 9th Century BC
                  (43167226572).jpg" (Gary Todd, Israel Museum, 5 July 2018, CC0), cropped to the stone.
4. MAPPING        All thirteen lines are on the one inscribed face, shown whole with all three
                  fragments (A on the right, B1 and B2 on the left). Checked on the image: thirteen
                  lines on fragment A, with the letters of bytdwd in line 9 picked out in white.

Usage:
    python3 scripts/import_tel_dan_stele.py
"""

import json
import re
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "tel-dan-stele"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "israel-museum"

WIKI = "https://en.wikipedia.org/wiki/Tel_Dan_stele"
REVID = 1380893880
PH_PAGE = "https://commons.wikimedia.org/wiki/File:Aramaic_Inscription_on_Basalt_Monument,_Dan,_9th_Century_BC_(43167226572).jpg"
PHOTO = ("Tel_Dan_Gary_Todd.jpg", (820, 230, 4560, 3850), f"{KEY}/tel-dan-stele-israel-museum.jpg")
GROUPS = [(1, 7, "the death of the king's father; Hadad makes him king; seventy kings slain"),
          (8, 13, "the king of Israel and the House of David; the land laid waste; Jehu")]

PHN = "𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕"
HEB = "אבגדהוזחטיכלמנסעפצקרשת"
PHN2HEB = dict(zip(PHN, HEB))


def strip_templates(t):
    t = re.sub(r"\{\{not a typo\|(.*?)\}\}", r"\1", t)
    t = re.sub(r"\{\{Script/Phoenician \|(.*?)\}\}", r"\1", t)
    t = t.replace("'''", "")
    return re.sub(r"\s+", " ", t).strip()


def parse():
    w = (SRC / "enwiki_tel_dan.wiki").read_text(encoding="utf-8")
    sec = w[w.index("===Text==="):w.index("===Content===")]
    phn = {}
    for m in re.finditer(r"^(\d+)\. \{\{Script/Phoenician \|(.*?)\}\}", sec, flags=re.M):
        phn[int(m.group(1))] = re.sub(r"\s+", " ", m.group(2)).strip()
    rom_block = sec[sec.index("Romanized:"):sec.index("The 1995 translation by Biran")]
    rom = [strip_templates(l[1:]) for l in rom_block.splitlines() if l.startswith("#")]
    eng_block = sec[sec.index("The 1995 translation by Biran"):sec.index("Other scholars have presented")]
    eng = [strip_templates(l[1:]) for l in eng_block.splitlines() if l.startswith("#")]
    assert sorted(phn) == list(range(1, 14)) and len(rom) == 13 and len(eng) == 13, (len(phn), len(rom), len(eng))
    return phn, {i + 1: r for i, r in enumerate(rom)}, {i + 1: e for i, e in enumerate(eng)}


def to_square(t):
    return "".join(PHN2HEB.get(ch, ch) for ch in t)


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    src, box, out = PHOTO
    dest = ROOT / "site" / "assets" / "scans" / out
    if not dest.exists():
        im = Image.open(SRC / "photos" / src).convert("RGB").crop(box)
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(dest, quality=88)
    phn, rom, eng = parse()

    sections = []
    for a, b, topic in GROUPS:
        orig = "".join(
            f'<span class="native-rtl"><sup>{n}</sup> {phn[n]}</span>'
            f'<span class="native-rtl"><sup>{n}</sup> {to_square(phn[n])}</span>'
            f'<span class="translit"><sup>{n}</sup> {rom[n]}</span>'
            for n in range(a, b + 1))
        text = "<br>".join(f"<sup>{n}</sup>{eng[n]}" for n in range(a, b + 1))
        sections.append({
            "section": f"{a}-{b}",
            "original_ref": f"Tel Dan stele (KAI 310) lines {a}-{b}: {topic}",
            "original_text": orig,
            "text": text,
            "scan_pages": [out],
            "scan_note": (
                f"Lines {a}-{b} of the thirteen lines on the inscribed face, which the photograph shows whole with all three "
                "fragments: fragment A on the right carries the right-hand part of every line (the text runs right to left), "
                "fragments B1 and B2 on the left carry the left-hand ends of lines 1-8 in Biran and Naveh's join. Checked on the image: thirteen "
                "lines on fragment A, line 9 beginning k.bytdwd with the letters of bytdwd picked out in white by the museum. "
                "Square brackets mark Biran and Naveh's restorations, which are not on the stone; their join of fragment B "
                "to fragment A, followed in the museum display, is not accepted by every scholar."),
        })

    intro = (
        "<p>The <strong>Tel Dan stele</strong> is a broken basalt monument in Old Aramaic, set up at Dan in northern Israel in "
        "the second half of the 9th century BCE by a king of Aram-Damascus, usually identified as Hazael. Fragment A was found in "
        "1993 and fragments B1 and B2 in 1994 in the excavations of Avraham Biran. The speaker says that the king of Israel had "
        "entered his father's land, that the god Hadad made him king, and that he killed the king of Israel and the king of the "
        "'House of David'. The phrase <em>bytdwd</em> in line 9 is the oldest mention of the dynasty of David outside the Old "
        "Testament. Biran and Naveh restore the names as Joram son of Ahab, king of Israel, and Ahaziah son of Joram, of the "
        "House of David, the two kings killed by Jehu in 2 Kings 9; the restorations and the join of the fragments are "
        "debated. The stele is in the Israel Museum, Jerusalem.</p>"
        "<p>Each line is given in three forms: the Phoenician (Old Aramaic) letters as transcribed by Biran and Naveh, the same "
        "letters in Hebrew square script, and a romanization. Dots divide words as on the stone; square brackets are restorations. "
        "The English is Biran's translation of 1995. Lines 10-13 survive only in their first few words.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Tel Dan stele (House of David inscription), Israel Museum",
        "language": "Old Aramaic (Phoenician letters, square script and romanization, Biran and Naveh) / English (Biran 1995)",
        "source": "Israel Museum, Jerusalem: photograph by Gary Todd (CC0) + Biran and Naveh's text and Biran's 1995 translation as given in English Wikipedia (CC BY-SA 4.0)",
        "description": "The Tel Dan stele (9th century BCE), an Aramaean king's victory inscription naming the king of Israel and the "
                       "'House of David', line by line with Biran and Naveh's text and translation and a photograph of the stone.",
        "introduction": intro,
        "translator_notes": [
            "The square-script line is a one-for-one letter conversion of the Phoenician-letter line, without final letter forms; it adds no reading of its own.",
            "Wikipedia also quotes Andre Lemaire's translation (1998), which reads 'two powerful kings' with 'two thousand chariots and two thousand horsemen' in lines 6-7 where Biran reads 'seventy kings' and 'thousands'.",
            f"Text and translation taken from English Wikipedia, 'Tel Dan stele', revision {REVID} ({WIKI}), under CC BY-SA 4.0.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Wikimedia Commons, {PH_PAGE} (Gary Todd, Israel Museum, 5 July 2018)",
            "scan_license": "CC0 1.0 (as stated on Commons)",
            "scan_manuscript": "Israel Museum, Jerusalem: Tel Dan stele, fragments A (found 1993) and B1, B2 (found 1994), basalt, Old Aramaic, second half of the 9th century BCE",
            "scan_mapping": "Single inscribed face shown whole with all three fragments; sections are consecutive line groups numbered 1-13 as in Biran and Naveh",
            "scan_mapping_urls": [PH_PAGE, WIKI],
            "scan_local_paths": [out],
            "original_text_source": f"A. Biran and J. Naveh's transcription as given in English Wikipedia, 'Tel Dan stele', section Text (revision {REVID}): {WIKI}",
            "original_text_license": "CC BY-SA 4.0 (Wikipedia article text)",
            "translation_source": f"A. Biran (and J. Naveh), Israel Exploration Journal 45 (1995), as quoted in English Wikipedia, 'Tel Dan stele', revision {REVID}: {WIKI}",
            "translation_license": "Not openly licensed: Biran and Naveh's 1995 translation (Israel Exploration Journal 45), quoted on English Wikipedia. Reproduced here as a short scholarly quotation of a 13-line inscription, by the owner's decision (2026-11-12); replace if an open translation appears.",
            "translator": "A. Biran (1995), via Wikipedia",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "hazael-aram",
        "language": "Aramaic", "era": "Ancient Near East", "tradition": "canaanite", "category": "inscription",
        "date_approx": "second half of the 9th century BCE", "century": -9, "source": entry["source"], "description": entry["description"],
        "themes": ["tel-dan", "house-of-david", "david", "israel", "aram", "hazael", "jehu", "2-kings", "aramaic-inscription", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": out, "caption": "Tel Dan stele, Israel Museum"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Tel Dan Stele",
            "group": "Levant & Israel", "date_sort": -830,
            "author_name": "A king of Aram-Damascus, probably Hazael (9th century BCE)",
            "source_url": WIKI,
            "critical_edition": "A. Biran and J. Naveh, IEJ 43 (1993) and 45 (1995), via Wikipedia",
            "translator_name": "A. Biran (1995)",
            "original_lang_label": "Old Aramaic · Phoenician letters, square script and romanization",
            "original_lang_code": "arc",
            "edition_label": "",
            "search_terms": "tel dan stele house of david bytdwd hazael aram damascus jehu joram ahaziah 2 kings 9 kai 310 israel museum",
            "description": "The Tel Dan stele (9th century BCE), in which an Aramaean king claims victory over the king of Israel and the "
                           "'House of David': Biran and Naveh's text and Biran's translation with a photograph of the stone.",
        },
        "texts": [row],
        "authors": [{"id": "hazael-aram", "name": "Hazael of Aram-Damascus (attributed)", "dates": "reigned about 842-800 BCE",
                     "century": -9, "era": "Ancient Near East", "tradition": "canaanite", "language": "Aramaic",
                     "bio": "King of Aram-Damascus, named in 1 and 2 Kings, usually taken to be the author of the Tel Dan stele."}],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
