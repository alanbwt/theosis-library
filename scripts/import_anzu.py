#!/usr/bin/env python3
"""
import_anzu.py -- Anzu, from the electronic Babylonian Library corpus edition L I.10
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_anzu.py --candidates
  python3 scripts/import_anzu.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {}
EXCLUDED = {}
SPLIT = {}

GENERAL = ('The Epic of Anzu tells how the lion-headed bird Anzu stole the Tablet of Destinies from Enlil, and how the god Ninurta, after other gods refused, defeated Anzu and recovered it. The Standard Babylonian version has three tablets. This page follows the line numbering of the electronic Babylonian Library edition.')

ENTRIES = [
    {'chapter': ('SB', 'I'), 'slug': 'sb-tablet-i', 'title': 'Anzu, Standard Babylonian Tablet I: the theft of the Tablet of Destinies', 'short': 'Standard Babylonian Tablet I', 'summary': "A hymn to Ninurta introduces the poem. Anzu, set to guard Enlil's bath, seizes the Tablet of Destinies and flies off; the gods look for a champion, and Adad, Gerra and Shara refuse."},
    {'chapter': ('SB', 'II'), 'slug': 'sb-tablet-ii', 'title': 'Anzu, Standard Babylonian Tablet II: Ninurta goes to war', 'short': 'Standard Babylonian Tablet II', 'summary': 'The mother goddess persuades her son Ninurta to fight Anzu. His first attack fails because Anzu uses the power of the Tablet of Destinies; Ea sends him new advice.'},
    {'chapter': ('SB', 'III'), 'slug': 'sb-tablet-iii', 'title': 'Anzu, Standard Babylonian Tablet III: the defeat of Anzu', 'short': 'Standard Babylonian Tablet III', 'summary': 'Ninurta defeats and kills Anzu, recovers the Tablet of Destinies, and is praised by the gods with many names.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Epic of Anzu, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="anzu", ebl_text=('L', 1, 10),
    ebl_name='eBL corpus edition L I.10, Anzu',
    label='Anzu (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of Anzu in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="anonymous-babylonian-poet", date_approx='composed early 2nd millennium BCE; tablets 18th-7th c. BCE',
    century=-18, date_sort=-1750,
    themes=['anzu', 'ninurta', 'tablet-of-destinies', 'enlil', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='anzu anzud imdugud ninurta tablet of destinies enlil epic',
    shelf_description="The Epic of Anzu, Standard Babylonian version, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian poet (early 2nd millennium BCE)',
    authors=[{"id": 'anonymous-babylonian-poet', "name": 'Anonymous (Babylonian poets)', "dates": '2nd-1st millennium BCE', "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
