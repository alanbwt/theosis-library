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

CHECKS = {
    'K.7257': "Photograph checked: one face of a fragment about 4 cm wide with about 15 lines, ink K.7257 on the right edge. Consistent with eBL's obverse 15.",
    'K.3454': "Photograph checked: obverse, reverse and edges of a tall tablet of several joined pieces, inks K.3454 on the side edge and DT.292 on the top edge (eBL: K.3454+K.3935+DT.292). About 35 to 45 lines on the obverse and two columns of about 55 and 30 on the reverse, consistent with eBL's 114 lines in columns i to iii.",
    'K.22880': "Photograph checked: one face of a flake about 1.5 cm across with about 3 lines; no ink number visible. Alone far too small for eBL's 26 lines (obverse 6, reverse 20), but eBL records it as joined to Sm.1807+Sm.2195, whose linked photograph shows about 20 lines on one face and about 8 worn lines on the other.",
    'BM.38797': "Photograph checked: obverse, reverse and edges of a fragment about 3 cm across, ink 38797 on the blank reverse and on an edge. About 9 lines on the obverse, consistent with eBL's obverse 5.",
    'K.3008': "Photograph checked: obverse, reverse and edges of a fragment about 5 x 6 cm, ink K.3008 on the left edge. About 18 lines on the obverse and about 15 on the reverse, consistent with eBL's columns i (17) and iv (13).",
    'K.21072': 'Photograph checked: eight views of a curved fragment about 2 x 3 cm in large script, ink K21072 on the broken back and 81-2-4 on the inscribed surface (eBL notes "Marked, 81-2-4"). About 6 or 7 line-ends per view with a ruling after every second line, as eBL describes; about enough for eBL\'s 9 + 9 short line-ends in columns ii and iii, though fewer than 19 are clearly countable.',
    'BM.121060': "Photograph checked: obverse, reverse and edges of a fragment about 5 cm wide, inks 121060 and Th 1929-10-12,56 on the edge. About 12 lines on the obverse and about 4 in the upper corner of the reverse, consistent with eBL's obverse 12 and reverse 6.",
    'K.19368': "Photograph checked: one face of a flake about 2 cm wide with 3 or 4 lines; no ink number visible. Consistent with eBL's column iii (4).",
    'K.7923': "Photograph checked: one face of a fragment of several joined pieces (eBL: K.7923+K.11565+K.14211+Sm.454), two columns with a double ruling between them, about 15 and 25 lines; no ink number visible. Consistent with eBL's columns i (16) and ii (26).",
    'BM.38886': "Photograph checked: obverse with two columns of about 10 and 11 lines, blank reverse with ink 38886, fragment about 3 cm across. Consistent with eBL's columns i (11) and ii' (12).",
    'BM.36072': "Photograph checked: obverse with about 18 lines and a blank reverse with ink 36072. Consistent with eBL's column i' (18).",
}
EXCLUDED = {
}
SPLIT = {
    'K.22880': ['Sm.1807'],
}

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
