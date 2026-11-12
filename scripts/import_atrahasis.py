#!/usr/bin/env python3
"""
import_atrahasis.py -- Atrahasis (the Babylonian Story of the Flood), from the electronic Babylonian Library corpus edition L I.1
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_atrahasis.py --candidates
  python3 scripts/import_atrahasis.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {}
EXCLUDED = {}
SPLIT = {}

GENERAL = ("Atrahasis ('Exceedingly Wise') is the Babylonian story of humanity from its creation to the Flood. The lesser gods rebel against their labour; humankind is created from clay and the flesh and blood of a slain god to do the work instead; when people multiply and their noise disturbs Enlil, he sends plague, drought and famine, and finally the Flood, which Atrahasis survives in a boat on the advice of Enki (Ea). The oldest near-complete copy was written at Sippar by the scribe Ipiq-Aya in the 17th century BCE. This page follows the line numbering of the electronic Babylonian Library edition.")

ENTRIES = [
    {'chapter': ('OB', 'I'), 'slug': 'old-babylonian-tablet-i', 'title': 'Atrahasis, Old Babylonian Tablet I: the rebellion of the gods and the creation of humankind', 'short': 'Old Babylonian Tablet I', 'summary': "When the gods worked like men, the lesser gods dug the rivers and canals for the great gods. They rebel and surround Enlil's house. Enki proposes that a human being be made to bear the work; the mother goddess forms humankind from clay mixed with the flesh and blood of the slain god We. People multiply, their noise disturbs Enlil, and he sends a plague, which Atrahasis averts on Enki's advice.", 'date_approx': 'Old Babylonian tablet written by Ipiq-Aya at Sippar, c. 1635 BCE'},
    {'chapter': ('SB', 'I'), 'slug': 'sb-tablet-i', 'title': 'Atrahasis, Standard Babylonian Tablet I', 'short': 'Standard Babylonian Tablet I', 'summary': 'The later (first-millennium) version of the opening of the story: the labour of the gods, their rebellion and the creation of humankind.'},
    {'chapter': ('SB', 'II'), 'slug': 'sb-tablet-ii', 'title': 'Atrahasis, Standard Babylonian Tablet II', 'short': 'Standard Babylonian Tablet II', 'summary': "The later version of the middle of the story: the noise of humankind, and Enlil's plagues, drought and famine."},
    {'chapter': ('SB', 'III'), 'slug': 'sb-tablet-iii', 'title': 'Atrahasis, Standard Babylonian Tablet III', 'short': 'Standard Babylonian Tablet III', 'summary': 'The later version of the Flood episode.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "Atrahasis, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="atrahasis", ebl_text=('L', 1, 1),
    ebl_name='eBL corpus edition L I.1, Story of the Flood (Atrahasis) (ed. E. Jiménez and G. Rozzi)',
    label='Atrahasis (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of Atrahasis in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="anonymous-babylonian-poet", date_approx='composed c. 1700 BCE or earlier; tablets 17th-7th c. BCE',
    century=-17, date_sort=-1700,
    themes=['atrahasis', 'flood', 'creation-of-humankind', 'enki', 'enlil', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='atrahasis atra-hasis flood deluge creation of man igigi enlil enki ea mami nintu ipiq-aya sippar',
    shelf_description="Atrahasis, the Babylonian story of the creation of humankind and the Flood, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian poet (copy of Ipiq-Aya, c. 1635 BCE)',
    authors=[{"id": 'anonymous-babylonian-poet', "name": 'Anonymous (Babylonian poets)', "dates": '2nd-1st millennium BCE', "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
