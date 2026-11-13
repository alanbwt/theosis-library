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

CHECKS = {
    'IM.67628': 'Photograph checked (eBL photograph of the Iraq Museum): obverse with both side edges and the reverse of a tall tablet from Kalhu. eBL numbers 68 obverse lines and 53 reverse lines (the last a catch-line after a ruling) on a tablet 20.2 cm high, but the photograph (about 13 cm by its scale bar) shows only about 44 obverse lines, from the top edge down to a diagonal break, and on the reverse about 38 lines, a ruling and one line. Obverse lines are therefore counted from the top edge of the obverse; the reverse lines cannot be located on this photograph with certainty, so no reverse line of this tablet is used.',
    '2024,6004.283': "Photograph checked: two views of a small wedge-shaped fragment about 2 cm long, no ink number visible; the upper view carries about five lines of signs, the lower view is broken surface. Consistent with eBL's five reverse lines.",
    'K.9392': "Photograph checked: obverse, reverse and edges of two joined pieces, ink K.9392 and a second, partly legible K.98.. number (eBL: K.9392+K.9810). About 12 lines on the obverse and a patch of several lines on the reverse, consistent with eBL's obverse 12 and reverse 2 + 1.",
    'BM.36320': "Photograph checked: obverse, reverse and edges, ink 36320 on the edge. About 25 lines of small script on each face, consistent with eBL's obverse 26 and reverse 19.",
    'K.10503': "Photograph checked: two views of an irregular fragment, no ink number visible. One face has about 8 or 9 lines; the other side has about 6 lines on a projecting piece and about 6 more at the edge. With the linked flake K.22794 this is broadly consistent with eBL's obverse 14 and reverse 13.",
    'K.3291': "Photograph checked: obverse, reverse and edges of a large, mostly complete tablet, ink K.3291 on the edges. About 60 lines on each face, which easily holds eBL's 67 lines from Ludlul I to V on both faces.",
    'K.9237': "Photograph checked: obverse, reverse and edges of a triangular fragment, ink K.9237 on the left edge. About 20 lines on each face, consistent with eBL's obverse 19 and reverse 19.",
    '1880,0617.2642': "Photograph checked: fragment about 2 cm high with 4 or 5 lines on one face and a blank other face; no ink number visible. Consistent with eBL's reverse 5.",
    'BM.38790': "Photograph checked: obverse, reverse and edges of a narrow fragment, ink 38790. About 20 lines on the obverse, about 14 on the reverse and text on the edge; consistent with eBL's obverse 22 and reverse 14 together with the linked piece BM.39238.",
    'BM.32208': "Photograph checked: obverse, reverse and edges of a large tablet rebuilt from many joined pieces with plaster fill. Inks 32208, 32214, 32371, 32378, 32449, 32659 and 32694 are visible on the pieces, plus 76-11-17 registration numbers, matching eBL's join list, which also names four unnumbered fragments. The obverse has columns of up to about 45 lines and the reverse two columns of about 25 and 35; consistent with eBL's 112 lines in obverse columns i to iii and reverse columns i' and ii'.",
    'K.2518': "Photograph checked: obverse and reverse side by side, with no scale bar and no ink number visible. About 50 dense lines on the obverse; the reverse has about 40 line-beginnings in a column plus a few lines across the bottom, the rest broken away. Consistent with eBL's obverse 47 and reverse 25 + 1.",
    'K.8396': "Photograph checked: obverse, reverse and edges, ink K.8396 on the edge. About 22 lines on the obverse (left part of the surface lost) and about 25 on the reverse, consistent with eBL's obverse 22 and reverse 26.",
    'K.6935': "Photograph checked: one face only of a fragment about 3.5 cm wide with 9 or 10 dense lines; no ink number visible. Consistent with eBL's reverse 10.",
    'K.3972': 'Photograph checked: obverse, reverse and edges of a nearly complete tablet, ink "W.A.I. IV 67 No 2. K.3972" on the left edge. About 45 lines on the obverse and about 40 on the reverse, consistent with eBL\'s obverse 48 and reverse 23.',
    'DT.151': "Photograph checked: obverse, reverse and edges, ink D.T.151 on the bottom edge. About 12 lines on the obverse and 4 ruled lines on the reverse, consistent with eBL's single reverse line.",
    'BM.48732': "Photograph checked: obverse, reverse and edges of a narrow fragment, ink 48732. About 11 lines on one face and 8 or 9 on the other, consistent with eBL's obverse 13 and reverse 8 + 1.",
    'BM.55481': "Photograph checked: obverse, reverse and edges, inks 55481 and 82-7-4,54. About 20 lines on the obverse and about 17 on the reverse, consistent with eBL's obverse 21 and reverse 19.",
    'BM.54821': "Photograph checked: obverse, reverse and edges, inks 54821 and 82-5-25,1150 on the edge. About 15 to 17 lines on each face, consistent with eBL's obverse 17 and reverse 15.",
    'BM.46826': "Photograph checked: obverse, reverse and edges of a fragment about 4 cm long, ink 46826 on the edge and 81-8-30,292 on the blank reverse. About 15 lines on the obverse, consistent with eBL's obverse 15.",
    'BM.39320': "Photograph checked: obverse, reverse and edges of a fragment about 3 cm wide, ink 39320 on the edge. About 7 or 8 lines on the obverse and faint traces of about 8 to 10 lines on the worn reverse; consistent with eBL's obverse 8 and reverse 10, though the reverse is very faint.",
    'BM.45732': "Photograph checked: both faces of a fragment about 3.5 cm across, inks 45732 and 81-7-6,140 on the blank face. About 10 lines on the inscribed face (upper lines faint), consistent with eBL's reverse 12.",
    'BM.46282': "Photograph checked: obverse and reverse of a school tablet of several joined pieces, ink 46282 on the reverse. About 10 lines of running text across the upper obverse, with list entries in vertical columns below and on the reverse; consistent with eBL's obverse 10.",
    'K.9724': "Photograph checked: one face only of a fragment about 4 cm high with about 15 lines; no ink number visible. Consistent with eBL's 17 lines (no column given).",
    'BM.123392': "Photograph checked: all faces of a fragment about 5 cm wide, inks 123392 and Th 1932-12-10,335. About 10 lines on one face and a few signs on the other, consistent with eBL's uncertain reverse 10.",
    'BM.34650': "Photograph checked: obverse, reverse and edges of a narrow fragment, inks Sp II,133 and 34650. About 20 lines on the obverse and about 14 on the reverse, consistent with eBL's obverse 22 and reverse 14.",
    'BM.38002': "Photograph checked: obverse and reverse of a fragment about 3 cm high, ink 38002 on the blank reverse. About 7 or 8 lines in large script on the obverse, consistent with eBL's obverse 7.",
}
EXCLUDED = {
}
SPLIT = {
    'K.10503': ['K.22794'],
    'BM.38790': ['BM.39238'],
    'K.3972': ['K.9973', 'DT.151'],
}

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

# QC round 2: the eBL photograph of IM.67628 shows only part of the tablet (see CHECKS); reverse lines are not used.
WORK["excluded_faces"] = {"IM.67628": {"r": "the photograph shows only part of the reverse"}}

if __name__ == "__main__":
    engine.build_work(WORK)
