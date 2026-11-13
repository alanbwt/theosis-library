#!/usr/bin/env python3
"""
import_orphic-gold-tablets.py: the Orphic gold tablets ('Totenpässe') for which a photograph of the
tablet, a public-domain Greek text and a public-domain English translation could all be found.
Built: the Petelia tablet (British Museum 1843,0816.1). See docs/collections/orphic-gold-tablets.md
for the tablets that could not be built and why.

Chain of evidence (Petelia)
  1. PHOTOGRAPH  Wikimedia Commons, 'Orphic Gold Tablet (Petelia - British Museum, London).jpg'
     (Jononmac46, 2014, CC BY-SA 3.0), 4000 x 3000 px, showing the tablet with its gold chain and
     cylinder case in the British Museum display; cropped here to the tablet. The British Museum's own
     collection pages answer scripts with a bot check and were not used.
  2. MAPPING  The tablet is one small sheet carrying the whole text, so every section points at the one
     photograph. The identity of the tablet was checked on the photograph (shape, the museum number
     3155 painted on the gold), and part of line 3, 'ΕΔΟΝ ΕΜΠΕΛΑΣΕΙ', was read on it.
  3. GREEK    The reading of Cecil Smith (British Museum), printed in Jane Ellen Harrison, Prolegomena to
     the Study of Greek Religion (Cambridge 1903), p. 574 n. 1, transcribed from the page image of
     archive.org prolegomenatostu00harruoft (leaf 597; the OCR of the Greek is unusable) and checked
     letter by letter. Public domain (1903).
  4. ENGLISH  Gilbert Murray's translation in his 'Critical Appendix on the Orphic Tablets' in the same
     book, pp. 660-661, checked against the page images (leaves 683-684). Public domain (1903; Murray
     died 1957, but the book was published in 1903, before 1931, so it is public domain in the US).

Usage:
    python3 scripts/import_orphic-gold-tablets.py
"""
import html as H
import io
import json
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image

KEY = "orphic-gold-tablets"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"

PETELIA_PHOTO = ("https://upload.wikimedia.org/wikipedia/commons/f/f1/"
                 "Orphic_Gold_Tablet_%28Petelia_-_British_Museum%2C_London%29.jpg")
PETELIA_PAGE = "https://commons.wikimedia.org/wiki/File:Orphic_Gold_Tablet_(Petelia_-_British_Museum,_London).jpg"
HARRISON = "https://archive.org/details/prolegomenatostu00harruoft"

# Cecil Smith's reading, Harrison 1903 p. 574 n. 1 (line by line as printed; dots and brackets as printed).
PETELIA_GRC = [
    "Εὑρήσσεις δ’ Ἀίδαο δόμων ἐπ’ ἀριστερὰ κρήνην",
    "πὰρ δ’ αὐτῆι λευκὴν ἑστηκυῖαν κυπάρισσον·",
    "ταύτης τῆς κρήνης μηδὲ σχεδὸν ἐμπελάσειας.",
    "Εὑρήσεις δ’ ἑτέραν τῆς Μνημοσύνης ἀπὸ λίμνης",
    "ψυχρὸν ὕδωρ προρέον· φύλακες δ’ ἐπίπροσθεν ἔασιν.",
    "Εἰπεῖν· γῆς παῖς εἰμι καὶ οὐρανοῦ ἀστερόεντος,",
    "αὐτὰρ ἐμοὶ γένος οὐράνιον· τόδε δ’ ἴστε καὶ αὐτοί·",
    "δίψηι δ’ εἰμὶ αὔη καὶ ἀπόλλυμαι· ἀλλὰ δότ’ αἶψα",
    "ψυχρὸν ὕδωρ προρέον τῆς Μνημοσύνης ἀπὸ λίμνης·",
    "καὐ[τοί σο]ι δώσουσι πιεῖν θείης ἀπ[ὸ κρήν]ης",
    "καὶ τότ’ ἔπειτ’ ἄ[λλοισι μεθ’] ἡρώεσσιν ἀνάξει[ς]",
    "............ιης τόδε.................................θανεῖ[σ]θαι",
    "......................τοδ’ ἔγραψ[εν ?]...",
    "..............................σκότος ἀμφικαλύψας.",
]
# Gilbert Murray, Harrison 1903 pp. 660-661 (lines as printed; Murray translates lines 1-11).
PETELIA_ENG = [
    "‘Thou shalt find to the left of the House of Hades a Well-spring,",
    "And by the side thereof standing a white cypress.",
    "To this Well-spring approach not near.",
    "But thou shalt find another by the Lake of Memory,",
    "Cold water flowing forth, and there are Guardians before it.",
    "Say: “I am a child of Earth and of Starry Heaven;",
    "But my race is of Heaven (alone). This ye know yourselves.",
    "And lo, I am parched with thirst and I perish. Give me quickly",
    "The cold water flowing forth from the Lake of Memory.”",
    "And of themselves they will give thee to drink from the holy Well-spring,",
    "And thereafter among the other Heroes thou shalt have lordship....’",
]
SECTIONS = [  # (section id, first line, last line, English last line)
    ("1-3", 1, 3, 3),
    ("4-9", 4, 9, 9),
    ("10-14", 10, 14, 11),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def petelia_scan():
    out = SCAN_DIR / "petelia-bm-1843-0816-1.jpg"
    if not out.exists():
        src = SRC / "commons-petelia-4000.jpg"
        if not src.exists():
            SRC.mkdir(parents=True, exist_ok=True)
            src.write_bytes(fetch(PETELIA_PHOTO))
        im = Image.open(io.BytesIO(src.read_bytes())).convert("RGB")
        im.crop((1450, 820, 2790, 1640)).save(out, quality=88)   # the tablet, at the original resolution
    return out


def lines_html(lines, a, b):
    return "<p>" + "<br>".join(f"<sup>{n}</sup>{H.escape(lines[n - 1], quote=False)}" for n in range(a, b + 1)) + "</p>"


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    scan = petelia_scan()
    rel = f"{KEY}/{scan.name}"
    note_common = ("The whole text stands on one small sheet of gold, shown in the photograph (cropped from the Wikimedia Commons image of the British Museum display). "
                   "Checked on the image: the tablet's outline with its two curved lower cut-outs and the number 3155 painted on the gold at the right identify it; "
                   "in line 3 the letters 'ΕΔΟΝ ΕΜΠΕΛΑΣΕΙ' (σχεδὸν ἐμπελάσειας) can be read in the upper right half. ")
    secs = []
    for sid, a, b, eb in SECTIONS:
        note = note_common + f"Lines {a}-{b} of the Greek, numbered as in Cecil Smith's reading printed by Harrison."
        if sid == "10-14":
            note += (" Lines 12-14 are fragments; line 14 is written along the right edge of the tablet (Harrison p. 574). "
                     "Murray's translation stops after line 11.")
        secs.append({
            "section": sid,
            "original_ref": f"Petelia tablet, lines {a}-{b} (Kaibel, IGSI 641); British Museum 1843,0816.1",
            "original_text": lines_html(PETELIA_GRC, a, b),
            "text": lines_html(PETELIA_ENG, a, eb),
            "scan_pages": [rel],
            "scan_note": note,
        })
    tid = PREFIX + "petelia"
    title = "Orphic gold tablet from Petelia: the springs of Forgetfulness and Memory"
    desc = ("A gold tablet of the 4th century BCE from a grave near Petelia in southern Italy, instructing the dead soul to avoid the first spring "
            "by the white cypress and to ask the guardians of the Lake of Memory for water: 'I am a child of Earth and of Starry Heaven, but my race is of Heaven (alone)'.")
    intro = (
        "<p>The Orphic or Bacchic gold tablets are thin sheets of gold, inscribed with short hexameter texts and buried with the dead in Greek graves "
        "in southern Italy, Thessaly and Crete from the late 5th century BCE to the 2nd century AD. They give the soul directions for the journey in the "
        "underworld and the words it must say. The tablet from Petelia (near Strongoli in Calabria), in the British Museum since 1843, is one of the earliest "
        "and fullest. It tells the soul that it will find a spring on the left of the house of Hades, with a white cypress beside it, and must not go near it; "
        "it should go on to the cold water flowing from the Lake of Memory (Mnemosyne) and say to the guardians: 'I am a child of Earth and of Starry Heaven; "
        "but my race is of Heaven (alone)'. Then they will let it drink, and it will rule among the other heroes (in Gilbert Murray's translation). "
        "The tablet had been rolled up and kept in a gold cylinder hung on a chain, worn as an amulet.</p>\n\n"
        "<p>The photograph shows the tablet on its clear display mount in the British Museum (registration number 1843,0816.1); it is cropped from a wider photograph that also shows the chain and case, which are outside the crop. "
        "The letters are very small and the gold is crumpled, so only parts can be made out on the photograph; the text is divided here into three groups of lines, "
        "all on the one tablet. The Greek is the reading of Cecil Smith of the British Museum as printed by Jane Ellen Harrison in 1903; "
        "the English is Gilbert Murray's translation from his appendix to the same book. Lines 12-14 survive only in fragments, the last written along the right edge.</p>"
    )
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Greek (Cecil Smith's reading, 1903) / English (Gilbert Murray, 1903)",
        "source": "British Museum 1843,0816.1 (photograph Wikimedia Commons, CC BY-SA 3.0) + Greek and English from J. E. Harrison, Prolegomena to the Study of Greek Religion (1903)",
        "description": desc,
        "introduction": intro,
        "translator_notes": [
            "Greek: reading of Cecil Smith, printed in J. E. Harrison, Prolegomena to the Study of Greek Religion (Cambridge 1903), p. 574 note 1. Square brackets mark letters restored where the gold is damaged; dots mark illegible letters.",
            "English: Gilbert Murray, 'Critical Appendix on the Orphic Tablets', in Harrison 1903, pp. 660-661. Murray's words in round brackets are his own.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": f"Wikimedia Commons, {PETELIA_PAGE} (photograph by Jononmac46, 24 April 2014, in the British Museum)",
            "scan_license": "CC BY-SA 3.0 (photographer Jononmac46, via Wikimedia Commons); object British Museum",
            "scan_manuscript": "Gold tablet, British Museum 1843,0816.1, from a grave near Petelia (Strongoli, Calabria), 4th century BCE (Kaibel, IGSI 641)",
            "scan_mapping": "Single tablet carrying the whole text; identity checked on the photograph (shape, painted number 3155) and part of line 3 read on it.",
            "scan_mapping_urls": [PETELIA_PAGE, HARRISON],
            "scan_local_paths": [rel],
            "original_text_source": f"Cecil Smith's reading in J. E. Harrison, Prolegomena to the Study of Greek Religion (Cambridge 1903), p. 574 n. 1, {HARRISON} (transcribed from the page image)",
            "original_text_license": "public domain (published 1903)",
            "translation_source": f"Gilbert Murray, Critical Appendix on the Orphic Tablets, in Harrison 1903, pp. 660-661, {HARRISON}",
            "translation_license": "public domain in the US (published 1903)",
            "translator": "Gilbert Murray (1903)",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": 1, "title": title, "author_id": "orphic",
        "language": "Greek", "era": "Classical", "tradition": "greek", "category": "inscription",
        "date_approx": "4th century BCE", "century": -4,
        "source": entry["source"], "description": desc,
        "themes": ["orphic", "gold-tablets", "afterlife", "mnemosyne", "memory", "underworld", "child-of-earth-and-starry-heaven", "theosis", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": rel, "caption": "Petelia tablet, British Museum 1843,0816.1"}]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Orphic gold tablets",
            "group": "Greece", "date_sort": -350,
            "author_name": "Orphic or Bacchic initiates, southern Italy (4th century BCE)",
            "source_url": PETELIA_PAGE,
            "critical_edition": "Cecil Smith's reading in Harrison, Prolegomena (1903)",
            "translator_name": "Gilbert Murray (1903)",
            "original_lang_label": "Greek",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "orphic gold tablets lamellae totenpass petelia mnemosyne memory lethe cypress child of earth and starry heaven underworld harrison murray",
            "description": ("Gold tablets buried with Orphic or Bacchic initiates, telling the soul which spring to avoid in the underworld and what to say "
                            "to the guardians of Memory, shown on a photograph of the tablet with a public-domain Greek text and translation."),
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(secs)} sections)")


if __name__ == "__main__":
    main()
