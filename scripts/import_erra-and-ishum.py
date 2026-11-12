#!/usr/bin/env python3
"""
import_erra-and-ishum.py -- Erra and Ishum, from the electronic Babylonian Library corpus edition L I.5
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_erra-and-ishum.py --candidates
  python3 scripts/import_erra-and-ishum.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {}
EXCLUDED = {}
SPLIT = {}

GENERAL = ('Erra and Ishum, written on five tablets by Kabti-ilani-Marduk (probably 8th century BCE), tells how Erra, god of war and plague, persuades Marduk to leave his throne and then devastates Babylonia, until his vizier Ishum calms him. Copies of the poem were used as amulets against plague. The eBL edition so far covers Tablet I only. This page follows the line numbering of the electronic Babylonian Library edition.')

ENTRIES = [
    {'chapter': ('SB', 'I'), 'slug': 'tablet-i', 'title': 'Erra and Ishum, Tablet I: Erra roused to war', 'short': 'Tablet I', 'summary': 'After a hymn to Ishum, the poem shows Erra lying idle. The Seven, his weapons, urge him to war. Erra goes to Babylon and persuades Marduk to leave his dwelling so that his insignia may be cleaned, promising to keep order while he is away.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "Erra and Ishum, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="erra-and-ishum", ebl_text=('L', 1, 5),
    ebl_name='eBL corpus edition L I.5, Erra and Ishum',
    label='Erra and Ishum (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of Erra and Ishum in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="kabti-ilani-marduk", date_approx='composed c. 8th c. BCE; tablets 8th-7th c. BCE',
    century=-8, date_sort=-750,
    themes=['erra', 'ishum', 'marduk', 'plague', 'babylon', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='erra ishum irra poem of erra kabti-ilani-marduk plague war marduk babylon seven',
    shelf_description="Erra and Ishum, Tablet I, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Kabti-ilani-Marduk (c. 8th c. BCE)',
    authors=[{"id": 'kabti-ilani-marduk', "name": 'Kabti-ilani-Marduk', "dates": 'c. 8th c. BCE', "century": -8, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": "Babylonian scholar named in the poem's epilogue as the author of Erra and Ishum, who says the text was revealed to him in a dream."}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
