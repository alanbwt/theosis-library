#!/usr/bin/env python3
"""
import_enuma-elish.py -- Enuma Elish (Babylonian Poem of Creation), Tablets I-VII, from the
electronic Babylonian Library corpus edition L I.2 (ed. A. C. Heinrich, rev. Z. J. Földi,
E. Jiménez; English by B. R. Foster), one entry per tablet.

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence
(manuscript-level eBL ATF + eBL English + British Museum photograph of the same manuscript,
eBL's line-to-manuscript attribution, visual check of every photograph used).

Usage:
  python3 scripts/import_enuma-elish.py --candidates   # list the tablets the selection would use
  python3 scripts/import_enuma-elish.py                # build
"""
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

KEY = "enuma-elish"

# Visual checks of the eBL photographs used (2026-11-12).
CHECKS = {}
EXCLUDED = {}
SPLIT = {}

TABLETS = {
    "I": ("Tablet I: the birth of the gods and Tiamat's army",
          "Before heaven and earth were named, Apsu and Tiamat mingled their waters and the gods were born. "
          "Disturbed by their noise, Apsu plans to destroy them; Ea puts him to sleep and kills him, and in his "
          "dwelling Marduk is born. Tiamat, urged on by other gods, creates monsters for battle and gives "
          "Qingu the Tablet of Destinies."),
    "II": ("Tablet II: the gods seek a champion",
           "Ea learns of Tiamat's preparations and reports to Anshar. Ea and then Anu go out against her and turn "
           "back. Marduk agrees to fight Tiamat on condition that the gods make his word supreme."),
    "III": ("Tablet III: the assembly of the gods",
            "Anshar sends his vizier Kakka to Lahmu and Lahamu to summon the gods, repeating the account of "
            "Tiamat's army and Marduk's demand. The gods gather, feast, and decree Marduk's destiny."),
    "IV": ("Tablet IV: Marduk defeats Tiamat",
           "The gods give Marduk kingship and weapons. He rides out on his storm chariot, catches Tiamat in his "
           "net, kills her with an arrow, binds her helpers and Qingu, takes the Tablet of Destinies, and splits "
           "Tiamat's body in two to form the sky."),
    "V": ("Tablet V: the ordering of the universe",
          "Marduk sets the stars, the year and the moon in their courses, forms features of the world from "
          "Tiamat's body, returns to the gods, is acclaimed king, and announces the building of Babylon."),
    "VI": ("Tablet VI: the creation of humankind and of Babylon",
           "Ea creates humankind from the blood of the guilty god Qingu to bear the gods' labour. The gods build "
           "Babylon and the temple Esagil for Marduk, hold a banquet, and begin to proclaim his fifty names."),
    "VII": ("Tablet VII: the fifty names of Marduk",
            "The gods continue to proclaim the names of Marduk with their meanings. An epilogue asks that the "
            "names be remembered, taught and pondered by later generations."),
}


def entries():
    out = []
    for t, (title, summary) in TABLETS.items():
        out.append({
            "chapter": ("SB", t),
            "slug": f"tablet-{t.lower()}",
            "title": f"Enuma Elish, {title}",
            "description": ("Enuma Elish (the Babylonian Poem of Creation), Tablet " + t + ": {covered} of {lines} lines, "
                            "each shown on a photographed cuneiform tablet ({tablets} tablets), with the eBL "
                            "transliteration of that tablet and B. R. Foster's English translation."),
            "intro": (f"<p>{summary}</p>"
                      "<p><em>Enuma Elish</em> ('When on high'), the Babylonian Poem of Creation, tells how Marduk, "
                      "god of Babylon, defeated Tiamat, created the ordered world and became king of the gods. It was "
                      "written on seven tablets and recited in Babylon during the New Year festival. The date of "
                      "composition is debated (proposals range from the 18th to the 12th century BCE); the surviving "
                      "copies date from the 9th to the 2nd century BCE and come from Ashur, Nineveh, Kish, Babylon, "
                      "Sippar, Uruk and other sites. This page follows the line numbering of the electronic "
                      "Babylonian Library edition.</p>"),
            "themes": [f"tablet-{t.lower()}"],
        })
    return out


WORK = {
    "key": KEY,
    "ebl_text": ("L", 1, 2),
    "ebl_name": "eBL corpus edition L I.2, Poem of Creation (Enuma elish) (ed. A. C. Heinrich, rev. Z. J. Földi and E. Jiménez)",
    "chapter_prefix": lambda ch: f"{ch['_stage_abbr']} {ch['name']}",
    "chapter_url": lambda ch: f"{engine.EBL_WEB}/corpus/L/1/2/{ch['_stage_abbr']}/{urllib.parse.quote(ch['name'])}",
    "siglum_label": "Lambert 2013 ms.",
    "siglum_re": r"Lambert 2013: Ms\. ([^;.]+)",
    "photo_checks": CHECKS,
    "excluded": EXCLUDED,
    "split_photos": SPLIT,
    "entries": entries(),
    "make_entry": engine.standard_entry,
    "author_id": "enuma-elish-author",
    "date_approx": "composed 2nd millennium BCE (date debated); tablets 9th-2nd c. BCE",
    "century": -12,
    "themes": ["enuma-elish", "creation", "marduk", "tiamat", "mesopotamian", "akkadian", "cuneiform"],
    "translator_short": "B. R. Foster (eBL edition)",
    "translator_line": ("The English is B. R. Foster's translation in the eBL edition (CC BY-NC-SA 4.0), one line of "
                        "English per line of the poem; italics mark uncertain renderings, as in the source."),
    "translation_source": "B. R. Foster, English translation of Enuma elish in the eBL corpus edition (electronic Babylonian Library, LMU Munich, 2021 and later)",
    "translator_notes": [
        "Akkadian: eBL transliteration of the signs on the photographed tablet (manuscript-level ATF), not a composite text.",
        "English: B. R. Foster's translation in the eBL edition; it renders eBL's composite text, including restorations from other tablets.",
        "Line numbers: eBL edition. Each section also gives the tablet's own column and line numbers.",
    ],
    "collection": {
        "key": KEY,
        "prefix": f"verified-{KEY}-",
        "label": "Enuma Elish (cuneiform tablets)",
        "group": "Mesopotamia",
        "date_sort": -1150,
        "author_name": "Babylonian Poem of Creation (2nd millennium BCE; tablets 9th-2nd c. BCE)",
        "source_url": "https://www.ebl.lmu.de/corpus/L/1/2",
        "critical_edition": "electronic Babylonian Library, Poem of Creation (ed. A. C. Heinrich), manuscript transliterations",
        "translator_name": "B. R. Foster (eBL edition)",
        "original_lang_label": "Akkadian · eBL transliteration of each tablet",
        "original_lang_code": "akk",
        "edition_label": "",
        "search_terms": "enuma elish enuma elis babylonian creation epic marduk tiamat apsu qingu seven tablets of creation",
        "description": ("Enuma Elish, the Babylonian Poem of Creation, Tablets I-VII, read line by line on photographed "
                        "clay tablets: each section shows one tablet's own transliteration with B. R. Foster's English "
                        "translation from the electronic Babylonian Library."),
    },
}

if __name__ == "__main__":
    engine.build_work(WORK)
