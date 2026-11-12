#!/usr/bin/env python3
"""
import_etana.py -- The Legend of Etana, from the electronic Babylonian Library corpus edition L I.9
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_etana.py --candidates
  python3 scripts/import_etana.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    'K.2606': "Photograph checked: obverse, reverse and edges, ink number K.2606 on the edge; a column of about 29 lines on the obverse and a few lines on the reverse, consistent with eBL's attribution.",
    'K.8563': "Photograph checked: obverse, reverse and edges, ink number K.8563 on the edge; text on both faces, consistent with eBL's columns i (11 lines) and iv (18 lines).",
    'K.2527': "Photograph checked: obverse, reverse and edges of the join K.2527 + K.5299 (two pieces on each face); text on both faces, consistent with eBL's obverse (36 lines) and reverse (40 lines).",
    'K.1547': "Photograph checked: obverse, reverse and edges; text on both faces and the side edges, consistent with eBL's obverse (22 lines) and reverse (20 lines).",
    'K.3651': "Photograph checked: obverse, reverse and edges of the join K.3651 + K.8578 (ink numbers on the edges); a long column on the obverse and text on the reverse, consistent with eBL's obverse (39 lines) and reverse (19 lines).",
    'K.19530': "Photograph checked: obverse, reverse and edges of the join K.19530 + Rm-II.454 + 1879,0708.180 (ink numbers 79-7-8,180 and K.19530 on the edges); text on both faces, consistent with eBL's obverse (26 lines) and reverse (40 lines).",
    '1882,0323.6': "Photograph checked: obverse, reverse and edges, ink number 82-3-23,6 on the edge; about a dozen lines on each face, consistent with eBL's obverse (11 lines) and reverse (12 lines).",
}
EXCLUDED = {
    "K.8572": "eBL treats K.8572 (+) BMC-T.236 (+) BkMus.7.6 as one manuscript (119 lines); the eBL photograph shows only K.8572, a small piece with 7 lines.",
}
SPLIT = {}

GENERAL = ('The Legend of Etana tells of an early king of Kish, chosen by the gods, who has no son. An eagle that betrayed its friend the serpent is thrown into a pit; Etana rescues it, and the eagle carries him up towards heaven to find the plant of birth. The story is known from Old Babylonian, Middle Assyrian and Standard Babylonian versions; the end is lost. This page follows the line numbering of the electronic Babylonian Library edition.')

ENTRIES = [
    {'chapter': ('SB', 'I'), 'slug': 'sb-tablet-i', 'title': 'Etana, Standard Babylonian Tablet I: the founding of kingship at Kish', 'short': 'Standard Babylonian Tablet I', 'summary': 'The gods plan the city of Kish and seek a king; Ishtar and Enlil choose Etana.'},
    {'chapter': ('SB', 'II'), 'slug': 'sb-tablet-ii', 'title': 'Etana, Standard Babylonian Tablet II: the eagle and the serpent', 'short': 'Standard Babylonian Tablet II', 'summary': "The eagle and the serpent swear friendship before Shamash. The eagle eats the serpent's young; on Shamash's advice the serpent traps the eagle in a pit. Etana prays for a son, and Shamash sends him to the eagle."},
    {'chapter': ('SB', 'III'), 'slug': 'sb-tablet-iii', 'title': 'Etana, Standard Babylonian Tablet III: the flight to heaven', 'short': 'Standard Babylonian Tablet III', 'summary': 'Etana rescues the eagle and, after a series of dreams, rides on its back towards the heaven of Anu. The text breaks off.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Legend of Etana, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="etana", ebl_text=('L', 1, 9),
    ebl_name='eBL corpus edition L I.9, Etana',
    label='Etana (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of Etana in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="anonymous-babylonian-poet", date_approx='composed early 2nd millennium BCE; tablets 18th-7th c. BCE',
    century=-18, date_sort=-1800,
    themes=['etana', 'eagle', 'serpent', 'kish', 'kingship', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='etana eagle serpent kish plant of birth flight to heaven shamash',
    shelf_description="The Legend of Etana, Standard Babylonian version, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian poet (early 2nd millennium BCE; tablets to 7th c. BCE)',
    authors=[{"id": 'anonymous-babylonian-poet', "name": 'Anonymous (Babylonian poets)', "dates": '2nd-1st millennium BCE', "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
