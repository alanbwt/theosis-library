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

CHECKS = {
    'UM.55-21-29': "Photograph checked (eBL photograph of the Penn Museum): obverse, reverse and edges of a fragment about 5 x 6 cm, ink 55-21-29 and a Nippur field number on the right edge; about 10 to 11 lines on each face, consistent with the Penn catalogue's 11 x 11 lines and with eBL's five reverse lines.",
    'BM.17596.A': "Photograph checked: inscribed face and blank back (inks 17596A and 94-1-15,310A on the back), fragment about 5 cm high. A double vertical ruling with line-end traces to its left (column i) and about 15 lines to its right; broadly consistent with eBL's columns i (10) and ii (21) once broken lines are counted.",
    'K.10082': "Photograph checked: one face only, fragment about 5 cm wide with about 8 lines and a column ruling near the right edge with a few signs beyond it; no ink number visible. Consistent with eBL's column i (8) and the start of column ii (4).",
    'K.6235': "Photograph checked: obverse, reverse and edges of a fragment about 3 x 5 cm, about 10 lines on each face, no ink number visible. Alone it holds about 20 of eBL's 37 lines; with the linked piece K.7109+K.9979 (about 16 lines) the total fits eBL's column ii and reverse column i.",
    'K.6831': "Photograph checked: obverse and reverse of a fragment about 5 x 6 cm, no ink number visible. About 12 to 14 worn lines on the obverse and a patch of about 8 on the reverse, consistent with eBL's obverse 14 and reverse 8.",
    'BM.41330': "Photograph checked: obverse, reverse and edges of a narrow fragment about 3.5 cm long, ink 41330 on the edge. About 14 faint lines on one face and about 9 on the other, consistent with eBL's obverse 14 and reverse 9.",
    'K.6634': "Photograph checked: obverse, reverse and edges, ink K.6634 on the edge. About 7 lines on the obverse of a fragment about 4 cm wide, consistent with eBL's obverse 7.",
    'K.17853': "Photograph checked: one face of a fragment about 2 cm high with 6 or 7 lines; no ink number visible. Consistent with eBL's 7 lines.",
    'K.14697': "Photograph checked: one face of a fragment about 2.5 cm high with about 9 lines, ink K.14697 on the left edge. Consistent with eBL's 10 lines.",
    'K.4539': "Photograph checked: one face only, a fragment about 3.5 cm wide with about 9 lines; no legible ink number. Alone it cannot carry eBL's 54 lines (obverse column ii 37, reverse column iii 17), but with the three linked pieces (K.5902, K.7816+K.13863, K.17752) the set shows about 45 to 50 lines on both faces.",
}
EXCLUDED = {
}
SPLIT = {
    'K.6235': ['K.7109'],
    'K.4539': ['K.5902', 'K.7816', 'K.17752'],
}

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

# eBL translates OB I 214 and 215-216 in English word order: the English under 214 is marked "(215-216)" and
# the English under 215-216 is marked "(214)".  Both are shown together, with eBL's own (correct) markers.
WORK["translation_spans"] = {"OB:I": {"214": {
    "through": "215-216",
    "replace": [],
    "note": ("eBL translates lines 214 and 215-216 together in English word order; its markers (215-216) and (214) "
             "show which words belong to which line, and the English is shown once for these lines."),
}}}

if __name__ == "__main__":
    engine.build_work(WORK)
