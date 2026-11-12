#!/usr/bin/env python3
"""
import_ludlul.py -- Ludlul bel nemeqi (the Poem of the Righteous Sufferer), from the electronic Babylonian Library corpus edition L II.2
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_ludlul.py --candidates
  python3 scripts/import_ludlul.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {}
EXCLUDED = {}
SPLIT = {}

GENERAL = ("Ludlul bel nemeqi ('I will praise the lord of wisdom'), the Poem of the Righteous Sufferer, is a monologue in five tablets by Shubshi-meshre-Shakkan, a nobleman who lost the favour of his king and his gods, was struck by illness, and was restored by Marduk. It was composed in the late second millennium BCE and copied widely in the first millennium. This page follows the line numbering of the electronic Babylonian Library edition.")

ENTRIES = [
    {'chapter': ('SB', 'I'), 'slug': 'tablet-i', 'title': 'Ludlul bel nemeqi, Tablet I: the anger of Marduk and the loss of favour', 'short': 'Tablet I', 'summary': 'A hymn to Marduk, whose anger is fearful and whose mercy is great. The speaker tells how his gods abandoned him, omens turned against him, the king turned away, and courtiers plotted against him.'},
    {'chapter': ('SB', 'II'), 'slug': 'tablet-ii', 'title': 'Ludlul bel nemeqi, Tablet II: illness and despair', 'short': 'Tablet II', 'summary': 'The sufferer reflects that he has done his duty to the gods and still suffers; he describes in detail the diseases that afflict him and the failure of the diviners and exorcists to help.'},
    {'chapter': ('SB', 'III'), 'slug': 'tablet-iii', 'title': 'Ludlul bel nemeqi, Tablet III: the dreams of deliverance', 'short': 'Tablet III', 'summary': 'In a series of dreams messengers of Marduk appear and announce his recovery; the illnesses are driven away.'},
    {'chapter': ('SB', 'IV'), 'slug': 'tablet-iv', 'title': 'Ludlul bel nemeqi, Tablet IV: restoration', 'short': 'Tablet IV', 'summary': 'The sufferer is restored and praises Marduk.'},
    {'chapter': ('SB', 'V'), 'slug': 'tablet-v', 'title': 'Ludlul bel nemeqi, Tablet V: thanksgiving at Esagil', 'short': 'Tablet V', 'summary': 'The restored man passes through the gates of Esagil in Babylon, gives thanks and offerings, and the people of Babylon praise Marduk.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "Ludlul bel nemeqi, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="ludlul", ebl_text=('L', 2, 2),
    ebl_name='eBL corpus edition L II.2, Righteous Sufferer (Ludlul bel nemeqi) (ed. A. Hätinen)',
    label='Ludlul bel nemeqi (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of Ludlul bel nemeqi in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="shubshi-meshre-shakkan", date_approx='composed late 2nd millennium BCE; tablets 8th-1st c. BCE',
    century=-12, date_sort=-1200,
    themes=['ludlul', 'righteous-sufferer', 'wisdom', 'marduk', 'theodicy', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='ludlul bel nemeqi righteous sufferer babylonian job shubshi-meshre-shakkan marduk wisdom',
    shelf_description="Ludlul bel nemeqi, the Babylonian Poem of the Righteous Sufferer, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Shubshi-meshre-Shakkan (late 2nd millennium BCE)',
    authors=[{"id": 'shubshi-meshre-shakkan', "name": 'Shubshi-meshre-Shakkan', "dates": 'late 2nd millennium BCE', "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Babylonian official named as the speaker of Ludlul bel nemeqi; a man of this name is attested in the time of the Kassite king Nazi-Maruttash (13th c. BCE).'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
