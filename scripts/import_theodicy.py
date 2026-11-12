#!/usr/bin/env python3
"""
import_theodicy.py -- The Babylonian Theodicy, from the electronic Babylonian Library corpus edition L II.1
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_theodicy.py --candidates
  python3 scripts/import_theodicy.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {}
EXCLUDED = {}
SPLIT = {}

GENERAL = ("The Babylonian Theodicy is a dialogue in 27 stanzas of 11 lines between a sufferer and his friend about the injustice of the world. Each stanza begins with the same sign, and the initial signs together form an acrostic that names the author, Saggil-kinam-ubbib, an incantation priest, as a worshipper of god and king. This page follows the line numbering of the electronic Babylonian Library edition.")

ENTRIES = [
    {'chapter': ('SB', '-'), 'slug': 'dialogue', 'title': 'The Babylonian Theodicy (dialogue of the sufferer and his friend)', 'short': 'dialogue', 'summary': 'The sufferer complains that he is an orphan, poor and oppressed while the wicked prosper; his friend answers that the ways of the gods are unknowable and that the pious are rewarded in the end. At the close the friend concedes that the gods made humans prone to falsehood, and the sufferer asks for mercy from his god and goddess.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Babylonian Theodicy, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="theodicy", ebl_text=('L', 2, 1),
    ebl_name='eBL corpus edition L II.1, Theodicy',
    label='Babylonian Theodicy (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of the Babylonian Theodicy in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="saggil-kinam-ubbib", date_approx='composed c. 1000 BCE; tablets 7th-2nd c. BCE',
    century=-10, date_sort=-1000,
    themes=['theodicy', 'wisdom', 'dialogue', 'acrostic', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='babylonian theodicy saggil-kinam-ubbib acrostic dialogue sufferer friend wisdom',
    shelf_description="The Babylonian Theodicy, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Saggil-kinam-ubbib (c. 1000 BCE)',
    authors=[{"id": 'saggil-kinam-ubbib', "name": 'Saggil-kinam-ubbib', "dates": 'c. 1000 BCE', "century": -10, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Babylonian incantation priest whose name is spelled out by the acrostic of the Babylonian Theodicy.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
