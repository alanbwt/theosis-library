#!/usr/bin/env python3
"""
import_gezer_calendar.py -- the Gezer calendar (Istanbul Archaeology Museums, inv. 2089 T),
a small limestone tablet found at Gezer in 1908, about the 10th century BCE.

One entry, one section with all seven lines: Driver's 1913 text (Lidzbarski's reading) in
Hebrew square letters, a letter-for-letter Latin transliteration of that same text, Driver's
English, and two photographs of the tablet.

Chain of evidence
-----------------
1. ORIGINAL TEXT  S. R. Driver, Notes on the Hebrew Text and the Topography of the Books of
                  Samuel, 2nd ed. (Oxford 1913), p. vii, "The Inscription reads (Lidzbarski)"
                  (public domain: published 1913, Driver d. 1914). Transcribed by hand from the
                  page image (archive.org notesonthehebrew00drivuoft, leaf n34) into
                  data/sources/gezer-calendar/driver1913_gezer_verified.txt, with Driver's printed
                  ERRATA slip (leaf n32): "Page vii, ll. 3, 5 of the inscription: for ירחו read ירח".
                  The overlined letter in line 1 (uncertain reading) is kept with a combining overline.
                  The Latin line is a mechanical letter-for-letter romanization of Driver's square
                  script (table HEB2LAT); it adds no reading.
2. ENGLISH        Driver 1913, p. vii, "I.e. 1 The month of ingathering [Tishri]. ...", with his line
                  numbers; transcribed from the page image.
3. PHOTOGRAPHS    (a) Driver 1913, Plate I, "Hebrew inscribed tablet from Gezer (Reproduced by
                  permission of the Palestine Exploration Fund)": a halftone photograph of the tablet
                  (leaf n31), public domain; (b) Wikimedia Commons, "The Gezer Calendar tablet, early
                  iron age, 10th century BCE, Museum of Archaeology, Istanbul, Turkey.jpg" (Osama Shukir
                  Muhammed Amin, 2018, CC BY-SA 4.0).
4. MAPPING        One inscribed face of seven lines, shown whole in both photographs. Checked on the
                  images: seven lines under the broken top edge, read right to left, and a few letters
                  written apart at the lower left corner.

Usage:
    python3 scripts/import_gezer_calendar.py
"""

import json
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "gezer-calendar"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = PREFIX + "istanbul-2089"

DRIVER = "https://archive.org/details/notesonthehebrew00drivuoft"
PH_PAGE = ("https://commons.wikimedia.org/wiki/File:The_Gezer_Calendar_tablet,_early_iron_age,_10th_century_BCE,"
           "_Museum_of_Archaeology,_Istanbul,_Turkey.jpg")
PHOTOS = [
    ("driver1913_plateI_n31.jpg", (50, 230, 1850, 2800), f"{KEY}/gezer-tablet-driver-1913-plate-i.jpg"),
    ("Gezer_Calendar_Osama_Amin.jpg", (600, 300, 3000, 3500), f"{KEY}/gezer-tablet-istanbul.jpg"),
]

HEB2LAT = {
    "א": "ʾ", "ב": "b", "ג": "g", "ד": "d", "ה": "h", "ו": "w", "ז": "z", "ח": "ḥ", "ט": "ṭ",
    "י": "y", "כ": "k", "ך": "k", "ל": "l", "מ": "m", "ם": "m", "נ": "n", "ן": "n", "ס": "s",
    "ע": "ʿ", "פ": "p", "ף": "p", "צ": "ṣ", "ץ": "ṣ", "ק": "q", "ר": "r", "ש": "š", "ת": "t",
}

ENGLISH = ("<sup>1</sup>The month of ingathering [Tishri]. The month of <sup>2</sup>sowing. The month of late sowing. "
           "<sup>3</sup>The month of cutting (or hoeing up ?) flax. <sup>4</sup>The month of barley-harvest. "
           "<sup>5</sup>The month of the general harvest. <sup>6</sup>The month of (vine-)pruning. "
           "<sup>7</sup>The month of summer-fruits.")


def romanize(heb):
    out = []
    for ch in heb:
        if ch in HEB2LAT:
            out.append(HEB2LAT[ch])
        elif ch in " ̅":
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

    heb = read_lines("driver1913_gezer_verified.txt")
    assert sorted(heb) == list(range(1, 8))
    orig = "".join(
        f'<span class="native-rtl"><sup>{n}</sup> {heb[n]}</span>'
        f'<span class="translit"><sup>{n}</sup> {romanize(heb[n])}</span>'
        for n in range(1, 8))

    sections = [{
        "section": "1-7",
        "original_ref": "Gezer calendar (KAI 182) lines 1-7",
        "original_text": orig,
        "text": ENGLISH,
        "scan_pages": scans,
        "scan_note": (
            "All seven lines are on the one inscribed face, which both photographs show whole (checked on the images: seven "
            "lines of large incised letters under the broken top edge, read right to left; line 1 begins at the right with "
            "yrḥw, the circle of ʿayin stands near the right end of line 2 in rʿ, and the last two lines are short; a few "
            "letters are written apart at the lower left corner). The first image is the photographic plate in Driver's book "
            "(1913), the second a recent photograph in Istanbul. Line numbers are Driver's."),
    }]

    intro = (
        "<p>The <strong>Gezer calendar</strong> is a small tablet of soft limestone, about 11 cm high, found in 1908 by "
        "R. A. S. Macalister in his excavations at Gezer for the Palestine Exploration Fund. Its seven short lines list the "
        "months of the farming year by their work: ingathering, sowing, late sowing, cutting flax, barley harvest, the "
        "general harvest, pruning the vines and summer fruit. It is usually dated to about the 10th century BCE, and it is "
        "one of the oldest known inscriptions in a language close to the Hebrew of the Old Testament; the tablet may have "
        "been a writing exercise. It is now in the Istanbul Archaeology Museums (inv. 2089 T).</p>"
        "<p>The text is Mark Lidzbarski's reading as printed by S. R. Driver in 1913, in Hebrew square letters, with a "
        "letter-for-letter Latin transliteration of the same text and Driver's English. Driver's printed errata are applied "
        "(lines 3 and 5 begin ירח, not ירחו). A line over a letter marks an uncertain reading. The letters written apart at "
        "the lower left corner, which Lidzbarski read as the beginning of a name, are not part of the seven lines given "
        "here.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Gezer calendar, Istanbul 2089 T",
        "language": "Hebrew (square script and transliteration, Lidzbarski/Driver 1913) / English (Driver 1913)",
        "source": "Gezer tablet, Istanbul 2089 T: Driver 1913 Plate I (public domain) and a Commons photograph (CC BY-SA 4.0) + Driver's 1913 text and translation (public domain)",
        "description": "The Gezer calendar (about 10th century BCE), seven lines naming the months of the farming year, with Lidzbarski's "
                       "reading and Driver's 1913 translation and photographs of the tablet.",
        "introduction": intro,
        "translator_notes": [
            "Driver's line over a letter means 'the reading is not quite certain' (Notes, p. viii, note 2).",
            "Driver on line 4: 'The ם is placed below the line for want of space.'",
            "The Latin transliteration is a mechanical letter-for-letter rendering of the square-script text (ʾ b g d h w z ḥ ṭ y k l m n s ʿ p ṣ q r š t); it adds no reading of its own.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"S. R. Driver, Notes on the Hebrew Text ... of Samuel (1913), Plate I ({DRIVER}, leaf n31); Wikimedia Commons {PH_PAGE} (Osama Shukir Muhammed Amin, 24 April 2018)",
            "scan_license": "Plate I: public domain (published 1913; photograph credited to the Palestine Exploration Fund); Commons photograph: CC BY-SA 4.0",
            "scan_manuscript": "Istanbul Archaeology Museums, inv. 2089 T (Gezer calendar, limestone tablet, found at Gezer 1908; about 10th century BCE)",
            "scan_mapping": "Single inscribed face shown whole in both photographs; one section with all seven lines, numbered as in Driver/Lidzbarski",
            "scan_mapping_urls": [DRIVER, PH_PAGE],
            "scan_local_paths": scans,
            "original_text_source": f"S. R. Driver, Notes on the Hebrew Text ... of Samuel, 2nd ed. (Oxford 1913), p. vii (Lidzbarski's reading) with the errata slip, transcribed from the page images ({DRIVER}, leaves n32, n34)",
            "original_text_license": "public domain (published 1913; Driver died 1914, Lidzbarski 1928)",
            "translation_source": f"S. R. Driver, Notes on the Hebrew Text ... of Samuel, 2nd ed. (1913), p. vii, transcribed from the page image ({DRIVER}, leaf n34)",
            "translation_license": "public domain (published 1913; Driver died 1914)",
            "translator": "S. R. Driver (1913)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "gezer-scribe",
        "language": "Hebrew", "era": "Ancient Near East", "tradition": "jewish", "category": "inscription",
        "date_approx": "about 10th century BCE", "century": -10, "source": entry["source"], "description": entry["description"],
        "themes": ["gezer", "calendar", "agriculture", "hebrew-inscription", "palestine-exploration-fund", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": scans[0], "caption": "Gezer calendar, Driver 1913 Plate I"},
                            {"file": scans[1], "caption": "Gezer calendar, Istanbul 2089 T"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Gezer Calendar",
            "group": "Levant & Israel", "date_sort": -925,
            "author_name": "Gezer (about 10th century BCE)",
            "source_url": PH_PAGE,
            "critical_edition": "M. Lidzbarski's reading, in S. R. Driver, Notes on the Hebrew Text ... of Samuel, 2nd ed. (1913), p. vii",
            "translator_name": "S. R. Driver (1913)",
            "original_lang_label": "Hebrew · square script (Lidzbarski/Driver) and transliteration",
            "original_lang_code": "hbo",
            "edition_label": "",
            "search_terms": "gezer calendar tablet macalister lidzbarski agricultural months kai 182 istanbul old hebrew",
            "description": "The Gezer calendar (about 10th century BCE), a small limestone tablet listing the farming months, with "
                           "Lidzbarski's reading, Driver's 1913 translation and photographs of the tablet.",
        },
        "texts": [row],
        "authors": [{"id": "gezer-scribe", "name": "Writer of the Gezer calendar", "dates": "about 10th century BCE",
                     "century": -10, "era": "Ancient Near East", "tradition": "jewish", "language": "Hebrew",
                     "bio": "The unnamed writer of the farming calendar scratched on a limestone tablet found at Gezer."}],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} section)")


if __name__ == "__main__":
    main()
