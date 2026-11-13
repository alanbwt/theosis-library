#!/usr/bin/env python3
"""
import_siloam_inscription.py -- the Siloam inscription from Hezekiah's tunnel, Jerusalem
(Istanbul Archaeology Museums, inv. 2195 T), late 8th century BCE.

One entry, one section with all six lines: Driver's 1913 text in Hebrew square letters,
a letter-for-letter Latin transliteration of that same text, Driver's line-by-line English,
and photographs of the inscribed panel in Istanbul.

Chain of evidence
-----------------
1. ORIGINAL TEXT  S. R. Driver, Notes on the Hebrew Text and the Topography of the Books of
                  Samuel, 2nd ed. (Oxford 1913), p. ix, "the Inscription, transliterated into
                  modern Hebrew characters" (public domain: published 1913, Driver d. 1914).
                  Transcribed by hand from the page image (archive.org
                  notesonthehebrew00drivuoft, leaf n38) into
                  data/sources/siloam-inscription/driver1913_siloam_verified.txt; Driver's
                  overlined (uncertain) letters are kept with a combining overline, his asterisks
                  (letters lost) and square brackets are kept as printed.
                  The Latin line under each Hebrew line is a mechanical letter-for-letter
                  romanization of Driver's square script (table HEB2LAT below); it adds no reading.
2. ENGLISH        Driver 1913, pp. ix-x, "I.e. 1. [Behold] the piercing through! ...", printed
                  line for line with the inscription; transcribed from the page images (leaves
                  n38-n39) into driver1913_siloam_english.txt.
3. PHOTOGRAPHS    Wikimedia Commons, "Siloam Inscription from Hezekiahs Tunnel Istanbul
                  Archaeology Museums.jpg" (ywpark2003, 2010, CC0) and "Siloam inscription.jpg"
                  (oncenawhile, 2014, CC0): the inscribed panel as displayed in Istanbul, cropped
                  to the stone.
4. MAPPING        The inscription is a single panel of six lines; both photographs show the whole
                  surviving panel. Line numbers are Driver's, which follow the stone line by line.

Usage:
    python3 scripts/import_siloam_inscription.py
"""

import json
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "siloam-inscription"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "istanbul-2195"

DRIVER = "https://archive.org/details/notesonthehebrew00drivuoft"
PH1_PAGE = "https://commons.wikimedia.org/wiki/File:Siloam_Inscription_from_Hezekiahs_Tunnel_Istanbul_Archaeology_Museums.jpg"
PH2_PAGE = "https://commons.wikimedia.org/wiki/File:Siloam_inscription.jpg"
# (source file, crop box in source pixels, output name)
PHOTOS = [
    ("Siloam_Inscription_ywpark.jpg", (100, 670, 3120, 2010), f"{KEY}/siloam-panel-ywpark.jpg"),
    ("Siloam_inscription_oncenawhile.jpg", (335, 225, 2795, 1020), f"{KEY}/siloam-panel-oncenawhile.jpg"),
]

HEB2LAT = {
    "א": "ʾ", "ב": "b", "ג": "g", "ד": "d", "ה": "h", "ו": "w", "ז": "z", "ח": "ḥ", "ט": "ṭ",
    "י": "y", "כ": "k", "ך": "k", "ל": "l", "מ": "m", "ם": "m", "נ": "n", "ן": "n", "ס": "s",
    "ע": "ʿ", "פ": "p", "ף": "p", "צ": "ṣ", "ץ": "ṣ", "ק": "q", "ר": "r", "ש": "š", "ת": "t",
}


def romanize(heb):
    out = []
    for ch in heb:
        if ch in HEB2LAT:
            out.append(HEB2LAT[ch])
        elif ch in " .·*[]̅":
            out.append(ch)
        else:
            raise ValueError(f"unexpected character {ch!r} in {heb!r}")
    return "".join(out)


def read_lines(name):
    out = {}
    for ln in (SRC / name).read_text(encoding="utf-8").splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        n, t = ln.split("|", 1)
        out[int(n)] = t.strip()
    return out


def lac(t):
    """Driver's asterisks (lost letters) shown in the lacuna style."""
    import re
    return re.sub(r"(\*(?: \*)*)", r'<span class="lacuna">\1</span>', t)


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    scans = []
    for src, box, out in PHOTOS:
        dest = ROOT / "site" / "assets" / "scans" / out
        if not dest.exists():
            im = Image.open(SRC / "photos" / src).convert("RGB").crop(box)
            s = min(1.0, 2600 / max(im.size))
            if s < 1:
                im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            im.save(dest, quality=88)
        scans.append(out)

    heb = read_lines("driver1913_siloam_verified.txt")
    eng = read_lines("driver1913_siloam_english.txt")
    assert sorted(heb) == list(range(1, 7)) and sorted(eng) == list(range(1, 7))

    orig = "".join(
        f'<span class="native-rtl"><sup>{n}</sup> {lac(heb[n])}</span>'
        f'<span class="translit"><sup>{n}</sup> {lac(romanize(heb[n]))}</span>'
        for n in range(1, 7))
    text = "<br>".join(f"<sup>{n}</sup>{eng[n]}" for n in range(1, 7))

    sections = [{
        "section": "1-6",
        "original_ref": "Siloam inscription (KAI 189) lines 1-6",
        "original_text": orig,
        "text": text,
        "scan_pages": scans,
        "scan_note": (
            "All six lines are on the one inscribed panel, which both photographs show whole (checked on the images: the "
            "smoothed panel cut from the tunnel wall in 1891, cracked and with pieces reset at its left end, and the incised "
            "letters running right to left across it). Line numbers are Driver's, who prints the text line for line with the stone. "
            "Where the text is on the photographs: the panel is the inscribed area itself, and the six lines run across its whole "
            "width, each beginning at the right-hand edge (the script reads right to left), line 1 at the top and line 6 near the "
            "foot. Line 1, the damaged line, runs through the network of cracks across the upper part of the panel, and its "
            "left-hand end is lost at the broken top-left corner; the plaster-filled gap at the top edge and the crack that runs "
            "down from it, a quarter of the way in from the left, cut through all the lines (compare the line-by-line facsimile "
            "from a squeeze published by the Palestine Exploration Fund, Library of Congress matpc.04121). The letters are shallow incisions on a light, cracked surface and are "
            "hard to see at this resolution; with the contrast raised they show as rows of short strokes in the middle of the "
            "panel, to the right of that crack. No sharper open photograph of the stone itself was found (Wikimedia Commons, "
            "searched 2026-11-12: the other open images show casts, the squeeze or drawings)."),
    }]

    intro = (
        "<p>The <strong>Siloam inscription</strong> was cut into the rock wall of the water tunnel that brings the water of the "
        "Gihon spring under the City of David to the Pool of Siloam in Jerusalem. In six lines of Hebrew in the old Hebrew "
        "script it tells how two teams of miners, digging from opposite ends, heard each other's voices through the rock and "
        "broke through, and how the water then flowed 1200 cubits from the spring to the pool. The tunnel is generally "
        "identified with the work of Hezekiah, king of Judah (late 8th century BCE), recorded in the Old Testament: "
        "'he made a pool, and a conduit, and brought water into the city' (2 Kings 20:20; compare 2 Chronicles 32:30).</p>"
        "<p>The inscription was noticed in 1880 near the southern end of the tunnel. In 1891 it was cut out of the wall, "
        "breaking in the process, and it was taken to Constantinople; it is now in the Istanbul Archaeology Museums "
        "(inv. 2195 T).</p>"
        "<p>The text is S. R. Driver's of 1913 in Hebrew square letters, with a letter-for-letter Latin transliteration of "
        "the same text and Driver's line-by-line English translation. Asterisks mark letters lost at the broken start of "
        "the inscription, square brackets Driver's restorations, and a line over a letter an uncertain reading. Driver's "
        "English carries words over the line ends as the stone does ('call-/ing', 'hun-/dred').</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Siloam inscription (Hezekiah's tunnel), Istanbul 2195 T",
        "language": "Hebrew (square script and transliteration, Driver 1913) / English (Driver 1913)",
        "source": "Istanbul Archaeology Museums 2195 T, photographs on Wikimedia Commons (CC0) + S. R. Driver's 1913 text and translation (public domain)",
        "description": "The Siloam inscription from Hezekiah's tunnel in Jerusalem (late 8th century BCE), six lines on the meeting of the "
                       "two tunnelling teams, with Driver's 1913 Hebrew text and translation and photographs of the stone.",
        "introduction": intro,
        "translator_notes": [
            "Driver's line over a letter means 'the reading is not quite certain' (Notes, p. viii, note 2); it is shown here as a line over the letter.",
            "The Latin transliteration is a mechanical letter-for-letter rendering of Driver's square-script text (ʾ b g d h w z ḥ ṭ y k l m n s ʿ p ṣ q r š t); it adds no reading of its own.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Wikimedia Commons: {PH1_PAGE} (ywpark2003, 2010) and {PH2_PAGE} (oncenawhile, 2014)",
            "scan_license": "CC0 1.0 (both photographs, as stated on Commons)",
            "scan_manuscript": "Istanbul Archaeology Museums, inv. 2195 T (Siloam inscription, limestone, from Hezekiah's tunnel, Jerusalem; late 8th century BCE; removed 1891)",
            "scan_mapping": "Single inscribed panel shown whole in both photographs; one section with all six lines, numbered as Driver prints them line for line with the stone",
            "scan_mapping_urls": [PH1_PAGE, PH2_PAGE, DRIVER],
            "scan_local_paths": scans,
            "original_text_source": f"S. R. Driver, Notes on the Hebrew Text and the Topography of the Books of Samuel, 2nd ed. (Oxford 1913), p. ix, transcribed from the page image ({DRIVER}, leaf n38)",
            "original_text_license": "public domain (published 1913; Driver died 1914)",
            "translation_source": f"S. R. Driver, Notes on the Hebrew Text ... of Samuel, 2nd ed. (1913), pp. ix-x, transcribed from the page images ({DRIVER}, leaves n38-n39)",
            "translation_license": "public domain (published 1913; Driver died 1914)",
            "translator": "S. R. Driver (1913)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "siloam-tunnel-scribe",
        "language": "Hebrew", "era": "Ancient Near East", "tradition": "jewish", "category": "inscription",
        "date_approx": "late 8th century BCE", "century": -8, "source": entry["source"], "description": entry["description"],
        "themes": ["siloam", "hezekiah", "jerusalem", "tunnel", "2-kings", "2-chronicles", "hebrew-inscription", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": scans[0], "caption": "Siloam inscription, Istanbul 2195 T"},
                            {"file": scans[1], "caption": "Siloam inscription, second view"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Siloam Inscription",
            "group": "Levant & Israel", "date_sort": -701,
            "author_name": "Hezekiah's tunnel, Jerusalem (late 8th century BCE)",
            "source_url": PH1_PAGE,
            "critical_edition": "S. R. Driver, Notes on the Hebrew Text ... of Samuel, 2nd ed. (1913), p. ix",
            "translator_name": "S. R. Driver (1913)",
            "original_lang_label": "Hebrew · square script (Driver) and transliteration",
            "original_lang_code": "hbo",
            "edition_label": "",
            "search_terms": "siloam inscription hezekiah tunnel shiloah gihon jerusalem 2 kings 20:20 2 chronicles 32:30 kai 189 istanbul",
            "description": "The Siloam inscription (late 8th century BCE) from the water tunnel under the City of David, which tells how the "
                           "miners met in the rock: Driver's 1913 text and translation with photographs of the stone in Istanbul.",
        },
        "texts": [row],
        "authors": [{"id": "siloam-tunnel-scribe", "name": "Scribe of Hezekiah's tunnel", "dates": "late 8th century BCE",
                     "century": -8, "era": "Ancient Near East", "tradition": "jewish", "language": "Hebrew",
                     "bio": "The unnamed writer of the inscription cut into the wall of the Siloam water tunnel in Jerusalem."}],
    }
    COLL.parent.mkdir(parents=True, exist_ok=True)
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} section)")


if __name__ == "__main__":
    main()
