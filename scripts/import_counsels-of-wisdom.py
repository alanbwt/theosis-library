#!/usr/bin/env python3
"""
import_counsels-of-wisdom.py -- The Counsels of Wisdom, from the electronic Babylonian Library corpus edition L 
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_counsels-of-wisdom.py --candidates
  python3 scripts/import_counsels-of-wisdom.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    'K.13770': "Photograph checked: a fragment about 2 cm across, with one face carrying about 8 to 9 lines, consistent with eBL's 9 obverse lines. The back is uninscribed; ink K 13770 is on an edge.",
    'BM.41931': "Photograph checked: one face with about 13 to 15 lines of large signs, consistent with eBL's 15 lines (no face given). The back is uninscribed and carries ink 41931.",
    'BM.51070': "Photograph checked: obverse, reverse and edges, with about 8 lines on each face, well over eBL's 4 obverse lines. Registration D 82-3-23,2066 is on the lower edge and reverse; a faded number on the obverse is not legible.",
    'K.8282': "Photograph checked: obverse, reverse and edges, ink number K.8282; a wide column of about 35-40 lines and a narrow column of about 20 on the obverse, consistent with eBL's columns i (35) and ii (14); the reverse shows about 6 lines, the rest of eBL's 13 reverse lines being on the joined piece K.18284 (about 7 lines), whose separate photograph is linked as well.",
    'K.3364': "Photograph checked: obverse, reverse and edges, with about 30 lines on each face, consistent with eBL's 29 obverse and 31 reverse lines. Break and join lines cross both faces; ink K.3364 is on both side edges.",
    'BM.41682': "Photograph checked: both faces are inscribed with about 10 lines each, consistent with eBL's ii 11, iii 9. Ink 81-6-25,300 and 41682 are on the edge.",
    'BM.33851': "Photograph checked: a join with plaster fill. Ink numbers are 33851 and Rm.IV.411, plus 76672 and AH 83-1-18,2043 on a second piece. There are about 25 lines on the obverse pieces, about 20 on the reverse, and an inscribed edge, consistent with eBL's i 18, ii 17, iii 10, iv 1.",
    'K.7897': "Photograph checked: about 25 lines on the obverse and about 22 on the reverse, consistent with eBL's ii 24, iii 19. Ink K.7897 is on the right edge.",
    'K.8231': 'Photograph checked: two columns on each face. The obverse has about 10 and 6 lines in its lower half (eBL 14). The reverse has about 14 and 8 lines (eBL 28, the rest presumably on the joined piece K.8638). Ink K.8231 is on the obverse and the edge.',
    '1882,0522.555': "Photograph checked: both faces are inscribed, with about 11 and about 13 lines, consistent with eBL's iii 10, iv 13. Ink 82-5-22,555 is on the edge.",
    'F.144': "Photograph checked: one face, about 5 cm high, with about 13 to 16 lines of large signs, close to eBL's 17 lines (no face given). The back has flaked away; ink F 144 is on the face.",
    'BM.33496': "Photograph checked: a join of several pieces. Ink numbers are 33496, 33819 and 33595, plus Rm.IV 51, Rm.IV 151 and Rm.IV 379. The obverse has three pieces with a column ruling and the reverse four pieces, together about 75 to 80 lines, consistent with eBL's i 19, ii 18, iii 16, iv 24.",
    'K.10652': "Photograph checked: only one face is photographed, with about 10 to 11 lines, consistent with eBL's 12 reverse lines. Ink K.10652.",
}
EXCLUDED = {
}
SPLIT = {
    'K.8282': ['K.18284'],
    'BM.33851': ['BM.32989'],
    'K.8231': ['K.8638'],
    'BM.33496': ['BM.48897', 'BM.48908', 'F.60'],
}

GENERAL = ('The Counsels of Wisdom is a collection of Babylonian moral advice in about 160 lines, addressed by a father, perhaps a royal official, to his son: on speech, companions, kindness, worship and conduct. This page follows the line numbering of the electronic Babylonian Library edition.')

ENTRIES = [
    {'chapter': ('SB', '-'), 'slug': 'counsels', 'title': 'Counsels of Wisdom (Babylonian moral advice)', 'short': 'text', 'summary': "The advice warns against evil companions, careless and slanderous speech, quarrels and marrying a prostitute, and urges kindness to the needy, daily worship of one's god, and honest service."},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Counsels of Wisdom, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key='counsels-of-wisdom', ebl_text=('L', 2, 3),
    ebl_name='eBL corpus edition L II.3, Counsels of Wisdom (ed. Z. J. Földi)',
    label='Counsels of Wisdom (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of the Counsels of Wisdom in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id='anonymous-babylonian-poet', date_approx='composed late 2nd millennium BCE; tablets 7th-1st c. BCE',
    century=-12, date_sort=-1100,
    themes=['wisdom', 'counsels', 'instruction', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='counsels of wisdom babylonian wisdom literature advice father son',
    shelf_description="The Babylonian Counsels of Wisdom, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian author (late 2nd millennium BCE)',
    authors=[{'id': 'anonymous-babylonian-poet', 'name': 'Anonymous (Babylonian poets)', 'dates': '2nd-1st millennium BCE', 'century': -12, 'era': 'Ancient Near East', 'tradition': 'mesopotamian', 'language': 'Akkadian', 'bio': 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
