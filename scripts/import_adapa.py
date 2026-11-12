#!/usr/bin/env python3
"""
import_adapa.py -- Adapa, from the electronic Babylonian Library corpus edition L I.7
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_adapa.py --candidates
  python3 scripts/import_adapa.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    'K.15072': 'Photograph checked: one face with the ink number K.15072 and about 9 lines; eBL gives no column for this fragment.',
    'K.9994': "Photograph checked: obverse, reverse and edges, ink number K.9994 on the edges; text on both faces, consistent with eBL's obverse column i (13 lines) and reverse column iv (10 lines).",
    'K.8743': "Photograph checked: one face with about 19 lines and the inscribed side edge, ink number K.8743 on the upper edge, consistent with eBL's column ii.",
    'K.8214': "Photograph checked: one face of two joined pieces with about 22 lines, consistent with eBL's reverse column iii.",
}
EXCLUDED = {}
SPLIT = {}

GENERAL = ("Adapa, a sage of Eridu and servant of Ea, breaks the wing of the South Wind and is summoned to heaven by Anu. On Ea's advice he refuses the bread and water offered to him, which would have given him eternal life. The story is known from a Middle Babylonian tablet found at el-Amarna in Egypt and from later fragments. This page follows the line numbering of the electronic Babylonian Library edition.")

ENTRIES = [
    {'chapter': ('SB', '-'), 'slug': 'standard-babylonian', 'title': 'Adapa (Standard Babylonian fragments)', 'short': 'Standard Babylonian version', 'summary': 'The later fragments of the story: Adapa as sage of Eridu, the fishing trip on which he breaks the wing of the South Wind, and the scene before Anu.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "Adapa, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="adapa", ebl_text=('L', 1, 7),
    ebl_name='eBL corpus edition L I.7, Adapa',
    label='Adapa (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of Adapa in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="anonymous-babylonian-poet", date_approx='composed 2nd millennium BCE; tablets 14th-7th c. BCE',
    century=-14, date_sort=-1400,
    themes=['adapa', 'eridu', 'ea', 'anu', 'immortality', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='adapa eridu south wind anu ea bread of life water of life immortality sage',
    shelf_description="The story of Adapa, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian poet (2nd millennium BCE)',
    authors=[{"id": 'anonymous-babylonian-poet', "name": 'Anonymous (Babylonian poets)', "dates": '2nd-1st millennium BCE', "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
