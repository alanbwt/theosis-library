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

CHECKS = {
    'VAT.10174': "Photograph checked (eBL photograph of the Vorderasiatisches Museum, Berlin): obverse, reverse and edges of a complete landscape tablet from Assur, ink VAT 10174 on the right edge; both faces are filled with about 17 to 20 long lines. Consistent with eBL's reverse lines 7a-15 (Erra I 121-131) on this school tablet, which also carries an excerpt of the Great Hymn to Shamash on the obverse.",
    'BM.35931': "Photograph checked: obverse, reverse and edges of a fragment about 3 cm wide, ink 35931 on two edges. About 10 lines of small script on the obverse and a blank reverse, consistent with eBL's column i (8).",
    'BM.36197': "Photograph checked: obverse, reverse and edges of a narrow fragment, ink 36197 on the edge. About 15 lines on one face and only a few signs on the other, consistent with eBL's column i (15).",
    'K.8571': "Photograph checked: obverse, reverse and edges of two joined pieces, ink K.8571 on the left edge. Two obverse columns with a double ruling between them, about 27 and 25 lines, and a small patch of traces on the worn reverse; consistent with eBL's columns i (27), ii (25) and iv (2).",
    'K.16694': "Photograph checked: obverse, reverse and edges of a narrow fragment of joined pieces, inks K.16694 and two Rm 2 numbers (328 and, less clearly, 477), matching eBL's K.16694+Rm-II.328+Rm-II.477. About 25 lines in one column on one face and about 15 on the other, consistent with eBL's columns ii (27) and iii (14).",
    'BM.36974': "Photograph checked: obverse, reverse and edges of a fragment about 2.5 cm across, ink 36974 on the edges. About 7 or 8 lines in large script on the obverse and a blank reverse; with the linked piece 1880,0617.2683 (about 5 lines) this fits eBL's column iii (12).",
    'BM.37217': "Photograph checked: obverse, reverse and edges, ink 37217 on the blank reverse and on an edge. About 12 lines in large script on the obverse, consistent with eBL's column iii (12).",
    'K.10023': "Photograph checked: one face only of a fragment about 4 cm high with about 12 lines; no ink number visible. Consistent with eBL's column iii (11).",
    'K.13361': "Photograph checked: one face only of a fragment about 2.5 cm across with 8 or 9 lines; no ink number visible. Consistent with eBL's column iii (8).",
}
EXCLUDED = {
}
SPLIT = {
    'BM.35931': ['Sp-III.855'],
    'K.8571': ['K.19050'],
    'BM.36974': ['1880,0617.2683'],
}

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
