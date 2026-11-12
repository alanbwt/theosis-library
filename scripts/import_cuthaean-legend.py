#!/usr/bin/env python3
"""
import_cuthaean-legend.py -- The Cuthaean Legend of Naram-Sin, from the electronic Babylonian Library corpus edition L 
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_cuthaean-legend.py --candidates
  python3 scripts/import_cuthaean-legend.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    'K.1351': "Photograph checked: a complete small tablet with obverse, reverse and all edges inscribed, more than 20 lines per face, easily holding eBL's 2 obverse lines. Ink K.1351 is on the edge.",
    '1881,0204.219': "Photograph checked: the obverse has two columns of about 18 and 21 lines. The reverse has a right column of about 17 lines and a worn left column of about 7. This matches eBL's o i 19, o ii 21, r iii 18, r iv 7. Ink 81-2-4,219 is on the obverse and the edge.",
    'K.5640': "Photograph checked: about 25 lines on the obverse and about 21 on the reverse, with an inscribed left edge, consistent with eBL's o i 24, r iv 21. Ink K.5640 is on the edge.",
    'K.5418.A': "Photograph checked: obverse, reverse and edges, with two columns per face of about 20 to 25 lines each, consistent with eBL's 19, 25, 24 and 25 lines. Ink K.5418.A is on the right edge, alongside yellow stickers.",
    'K.8582': "Photograph checked: one face with about 10 to 11 lines, consistent with eBL's 11 lines in reverse column iii(?). No ink number is visible.",
    'K.21047': "Photograph checked: one face, mostly covered by a bubbly burnt crust, with about 4 to 5 legible lines in the uncovered lower part, close to eBL's 6 lines in reverse column iv. Ink Rm 2,II(?) and K 21047.",
    '1881,0727.271': "Photograph checked: one face with about 3 to 4 lines above a double ruling, consistent with eBL's 4 lines in reverse column iv(?); the back is uninscribed. Ink 81-7-27,271.",
}
EXCLUDED = {
    'BM.36765': "visual check: the obverse matches well: two columns divided by a double ruling, with 3 lines each (eBL o i 3, o ii 3). The reverse shows only about 6 lines and no visible column ruling, against eBL's iii 5 and iv 8. The ink number on the edge is written across a crack, and its last digit looks most like a 5 but could be read as 36766.",
}
SPLIT = {
}

GENERAL = ('The Cuthaean Legend presents itself as an inscription of Naram-Sin, king of Akkad (23rd century BCE), written for his successors. Hordes of strange warriors invade his land; ignoring the omens he attacks them and suffers three defeats, and he learns to trust the gods and to wait. The Standard Babylonian version is the best preserved. This page follows the line numbering of the electronic Babylonian Library edition.')

ENTRIES = [
    {'chapter': ('SB', '-'), 'slug': 'standard-babylonian', 'title': 'Cuthaean Legend of Naram-Sin (Standard Babylonian version)', 'short': 'Standard Babylonian version', 'summary': 'Naram-Sin describes the enemy hordes created by the gods, his failure to consult the omens, the destruction of his armies, his despair, and the advice he leaves to future rulers: keep calm, guard the land, and do not go out to fight.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Cuthaean Legend of Naram-Sin, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key='cuthaean-legend', ebl_text=('L', 1, 12),
    ebl_name='eBL corpus edition L I.12, Cuthaean Legend of Naram-Sin (ed. T. D. N. Mitto)',
    label='Cuthaean Legend of Naram-Sin (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of the Cuthaean Legend of Naram-Sin in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id='anonymous-babylonian-poet', date_approx='composed early 2nd millennium BCE; tablets 7th c. BCE',
    century=-18, date_sort=-1800,
    themes=['naram-sin', 'akkad', 'cuthah', 'narû', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='cuthaean legend naram-sin akkad cutha kutha naru inscription umman-manda',
    shelf_description="The Cuthaean Legend of Naram-Sin, Standard Babylonian version, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian poet (early 2nd millennium BCE)',
    authors=[{'id': 'anonymous-babylonian-poet', 'name': 'Anonymous (Babylonian poets)', 'dates': '2nd-1st millennium BCE', 'century': -12, 'era': 'Ancient Near East', 'tradition': 'mesopotamian', 'language': 'Akkadian', 'bio': 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
