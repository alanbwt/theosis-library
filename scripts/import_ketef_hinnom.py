#!/usr/bin/env python3
"""
import_ketef_hinnom.py -- the smaller Ketef Hinnom silver amulet (KH2), Israel Museum,
Jerusalem, late 7th or early 6th century BCE, with the priestly blessing of Numbers 6:24-26.

One entry, one section with the twelve preserved lines of KH2 as given in English Wikipedia:
the text in Hebrew letters, Wikipedia's transliteration and Wikipedia's English, with a
photograph of the unrolled amulet. The larger amulet (KH1) is not published: Wikipedia gives
only an English rendering of it, with no original-language text.

Chain of evidence
-----------------
1. ORIGINAL TEXT  English Wikipedia, "Ketef Hinnom scrolls", section KH2 (revision REVID below),
                  "Text in Hebrew letters" and "Transliteration", twelve lines each; saved as
                  data/sources/ketef-hinnom/enwiki_kh.wiki. Licence CC BY-SA 4.0.
                  Two bracket fixes (BRACKET_FIX): in lines 5 and 12 the square brackets of the
                  Hebrew-letter text are displaced in the Wikipedia markup (bidirectional typing);
                  they are placed as in Wikipedia's own transliteration of the same lines
                  ("[r]ʕ ybrk", "[l]m"). No letter is changed.
2. ENGLISH        Same section, the numbered English lines 1-12 (CC BY-SA 4.0).
3. PHOTOGRAPH     Wikimedia Commons, "Ketef Hinnom KH2 Scroll.jpg", the unrolled amulet mounted on a
                  plate; source given there as archive.org item ketef-hinnom-kh-2; photographer not
                  named; tagged public domain on Commons.
4. MAPPING        The twelve lines are the preserved lines of the one inscribed side of the strip,
                  written across its width and numbered from the top as in Wikipedia; the photograph
                  shows the whole strip (checked on the image: the strip with its broken top, faint
                  scratched letters across it, and the detached lower fragments).

Usage:
    python3 scripts/import_ketef_hinnom.py
"""

import json
import re
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "ketef-hinnom"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "kh2"

WIKI = "https://en.wikipedia.org/wiki/Ketef_Hinnom_scrolls"
REVID = 1378179986
PH_PAGE = "https://commons.wikimedia.org/wiki/File:Ketef_Hinnom_KH2_Scroll.jpg"
PH_SRC = "https://archive.org/details/ketef-hinnom-kh-2"
PHOTO = ("Ketef_Hinnom_KH2_Scroll.jpg", (880, 150, 2080, 4000), f"{KEY}/ketef-hinnom-kh2.jpg")
BRACKET_FIX = {5: ("ר] ע יברך]", "[ר]ע יברך"), 12: ("] ל]ם", "[ל]ם")}


def parse():
    w = (SRC / "enwiki_kh.wiki").read_text(encoding="utf-8")
    i = w.index("===KH2===")
    seg = w[i:w.index("====Biblical parallels====", i)]
    heb = [m.group(1).strip() for m in re.finditer(r"\{\{script/Hebrew\|(.*?)\}\}", seg)]
    eng_block = seg[:seg.index("{{col-4}}")]
    eng = [l[1:].strip() for l in eng_block.splitlines() if l.startswith("#")]
    tr_block = seg[seg.index("Transliteration:"):seg.index("Transcription:")]
    tr = [l[1:].strip() for l in tr_block.splitlines() if l.startswith("#")]
    tr = [t.replace("[[Yahweh|yhw[h]]]", "yhw[h]") for t in tr]
    assert len(heb) == len(eng) == len(tr) == 12, (len(heb), len(eng), len(tr))
    heb = {n + 1: h for n, h in enumerate(heb)}
    for n, (old, new) in BRACKET_FIX.items():
        assert heb[n] == old, (n, heb[n])
        heb[n] = new
    return heb, {n + 1: t for n, t in enumerate(tr)}, {n + 1: e for n, e in enumerate(eng)}


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    src, box, out = PHOTO
    dest = ROOT / "site" / "assets" / "scans" / out
    if not dest.exists():
        im = Image.open(SRC / "photos" / src).convert("RGB").crop(box)
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(dest, quality=90)
    heb, tr, eng = parse()
    orig = "".join(
        f'<span class="native-rtl"><sup>{n}</sup> {heb[n]}</span><span class="translit"><sup>{n}</sup> {tr[n]}</span>'
        for n in range(1, 13))
    text = "<br>".join(f"<sup>{n}</sup>{eng[n]}" for n in range(1, 13))
    sections = [{
        "section": "1-12",
        "original_ref": "Ketef Hinnom amulet KH2, preserved lines 1-12 (lines 5-12: Numbers 6:24-26)",
        "original_text": orig,
        "text": text,
        "scan_pages": [out],
        "scan_note": (
            "The twelve preserved lines are on the one inscribed side of the unrolled silver strip, which the photograph shows "
            "whole (checked on the image: the strip mounted on a plate, broken at the top, with fine scratched letters running "
            "across its width; the letters are very small and faint, the strip being about 11 mm wide, and the detached pieces "
            "at the bottom come from the lower end). Lines are numbered from the top of the preserved text as in Wikipedia. "
            "Square brackets are restorations, not visible on the silver."),
    }]
    intro = (
        "<p>The <strong>Ketef Hinnom amulets</strong> are two tiny rolled strips of silver found in 1979 by Gabriel Barkay in a "
        "burial cave at Ketef Hinnom, on the slope above the Hinnom valley in Jerusalem. They date from the late 7th or early "
        "6th century BCE, before the Babylonian destruction of Jerusalem, and were worn as amulets. Unrolled and read, both "
        "carry words of the priestly blessing of Numbers 6:24-26, 'The LORD bless thee, and keep thee: The LORD make his face "
        "shine upon thee', which makes them the oldest surviving text that is also found in the Old Testament. They are in the "
        "Israel Museum, Jerusalem.</p>"
        "<p>This entry gives the smaller amulet, KH2 (about 11 by 39 mm): its twelve preserved lines in Hebrew letters, a "
        "transliteration and an English rendering, all from Wikipedia. Lines 5-12 contain the blessing. The top of the strip "
        "is lost. The larger amulet, KH1, is not included here because no openly licensed original-language text of it was "
        "available.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Ketef Hinnom silver amulet KH2 (the priestly blessing), Israel Museum",
        "language": "Hebrew (Hebrew letters and transliteration) / English (Wikipedia)",
        "source": "Ketef Hinnom amulet KH2, Israel Museum: photograph via Wikimedia Commons + text, transliteration and English from English Wikipedia (CC BY-SA 4.0)",
        "description": "The smaller Ketef Hinnom silver amulet (about 600 BCE), whose twelve surviving lines include the priestly blessing "
                       "of Numbers 6:24-26, with its text, transliteration and translation and a photograph of the unrolled amulet.",
        "introduction": intro,
        "translator_notes": [
            "The English renders word-divisions across line ends as the amulet has them ('h/sh-', 'YH-/-[W]H', 'g-/-rant', 'p-/-[ea]ce'); a slash gives two possible readings.",
            "Lines 5-12 correspond to Numbers 6:24-25 and the last words of 6:26: 'The LORD bless thee, and keep thee: The LORD make his face shine upon thee ... and give thee peace' (KJV).",
            "In lines 5 and 12 the square brackets of the Hebrew-letter text are placed as in Wikipedia's transliteration of the same lines; the Wikipedia markup has them displaced.",
            f"Text, transliteration and English from English Wikipedia, 'Ketef Hinnom scrolls', revision {REVID} ({WIKI}), under CC BY-SA 4.0.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Wikimedia Commons, {PH_PAGE} (source given there as {PH_SRC})",
            "scan_license": "Tagged public domain on Commons (PD-Art / PD-old-70); photographer not named; used with credit under the owner's rule for scholarly photographs",
            "scan_manuscript": "Israel Museum, Jerusalem: Ketef Hinnom amulet KH2, rolled silver strip, about 11 x 39 mm, from a burial cave at Ketef Hinnom (found 1979); late 7th or early 6th century BCE",
            "scan_mapping": "Single inscribed side of the strip shown whole; one section with the twelve preserved lines, numbered from the top as in Wikipedia",
            "scan_mapping_urls": [PH_PAGE, WIKI],
            "scan_local_paths": [out],
            "original_text_source": f"English Wikipedia, 'Ketef Hinnom scrolls', section KH2, 'Text in Hebrew letters' and 'Transliteration' (revision {REVID}): {WIKI}",
            "original_text_license": "CC BY-SA 4.0 (Wikipedia article text)",
            "translation_source": f"English Wikipedia, 'Ketef Hinnom scrolls', section KH2, numbered English lines (revision {REVID}): {WIKI}",
            "translation_license": "CC BY-SA 4.0 (Wikipedia article text)",
            "translator": "Wikipedia contributors",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "ketef-hinnom-scribe",
        "language": "Hebrew", "era": "Ancient Near East", "tradition": "jewish", "category": "inscription",
        "date_approx": "late 7th or early 6th century BCE", "century": -7, "source": entry["source"], "description": entry["description"],
        "themes": ["ketef-hinnom", "amulet", "priestly-blessing", "numbers-6", "yhwh", "jerusalem", "hebrew-inscription", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": out, "caption": "Ketef Hinnom amulet KH2, unrolled"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Ketef Hinnom Amulet",
            "group": "Levant & Israel", "date_sort": -600,
            "author_name": "Burial cave at Ketef Hinnom, Jerusalem (about 600 BCE)",
            "source_url": WIKI,
            "critical_edition": "Wikipedia, 'Ketef Hinnom scrolls' (text and transliteration of KH2)",
            "translator_name": "Wikipedia contributors",
            "original_lang_label": "Hebrew · Hebrew letters and transliteration",
            "original_lang_code": "hbo",
            "edition_label": "",
            "search_terms": "ketef hinnom silver amulet scroll kh2 priestly blessing numbers 6:24-26 birkat kohanim barkay jerusalem yhwh",
            "description": "The smaller of the two Ketef Hinnom silver amulets (about 600 BCE), carrying the priestly blessing of Numbers "
                           "6:24-26, the oldest surviving words also found in the Old Testament.",
        },
        "texts": [row],
        "authors": [{"id": "ketef-hinnom-scribe", "name": "Engraver of the Ketef Hinnom amulets", "dates": "about 600 BCE",
                     "century": -7, "era": "Ancient Near East", "tradition": "jewish", "language": "Hebrew",
                     "bio": "The unnamed engraver of the two silver amulets found in a burial cave at Ketef Hinnom, Jerusalem."}],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} section)")


if __name__ == "__main__":
    main()
