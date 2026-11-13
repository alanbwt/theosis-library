#!/usr/bin/env python3
"""
import_theodicy.py -- The Babylonian Theodicy, from the electronic Babylonian Library corpus edition L II.1
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_theodicy.py --candidates
  python3 scripts/import_theodicy.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    'K.17235': "Photograph checked: one face of a small fragment about 2 cm across, no ink number visible; about seven or eight line-ends along the preserved right edge. Consistent with eBL's seven line-ends of column iii.",
    'K.8463': "Photograph checked: obverse, reverse and edges of three joined pieces, inks K.8463, K.103.. and K.20280 (eBL: K.8463+K.10301+K.20280). Two obverse columns of about 17 and 10 lines, and about 6 lines at the lower right of the mostly blank reverse; consistent with eBL's columns i (17), ii (10) and iii (8).",
    'BM.35405': "Photograph checked: obverse, reverse and edges of two joined pieces, ink 35405 with Sp II 988 and Sp II 1001 (eBL: BM.35405+Sp-II.1001). About 40 lines with vertical rulings on the obverse and a blank reverse, consistent with eBL's column i (40).",
    'K.9290': "Photograph checked: obverse, reverse and edges of two joined pieces, inks K.9290 and K.9297. Two columns on each face, about 33 and 19 lines on the obverse and 35 and 16 on the reverse; consistent with eBL's 103 lines in columns i to iv.",
    'BM.36704': "Photograph checked: obverse, reverse and edges of a fragment about 4.5 cm long, ink 36704 on the reverse and edge. About 15 lines in large script with vertical rulings on the obverse and a blank reverse; close to eBL's column ii (19) once broken lines at the edges are counted.",
    'BM.40098': "Photograph checked: obverse, reverse and edges of a fragment about 6 cm wide, ink 40098 on the bottom edge. About 14 lines on the obverse, about 12 on the reverse, and a strip of about 8 lines from another column beyond a vertical ruling; with the linked piece BM.40124+BM.77255 the set comes close to eBL's 64 lines in columns i to iv.",
    'K.4267': 'Photograph checked: obverse, reverse and all edges of a large tablet, ink K.4267 on the right edge. About 40 lines on each face, which easily holds the single reverse line eBL attributes.',
    'K.1743': "Photograph checked: obverse, reverse and edges of two joined pieces, inks K.1743 and K.10858 on the edge (eBL: K.1743+K.10858). About 18 lines on one face and a blank other face, consistent with eBL's column iii (19).",
    'BM.47745': "Photograph checked: obverse, reverse and edges of a fragment about 8 cm wide, ink 47745 on the side edge. About 13 lines with vertical rulings on the obverse, and about 10 on the reverse plus 2 on the bottom edge; broadly consistent with eBL's columns ii (14) and iii (18).",
    'BM.94273': "Photograph checked: obverse, reverse and edges of two joined pieces, inks 94273 and 94331 (eBL: BM.94273+BM.94331). About 22 lines of small script on the obverse and about 12 on the upper reverse, consistent with eBL's columns i (22) and iv (12).",
    'K.3452': "Photograph checked: obverse, reverse and edges of several joined pieces, inks K.3452, S.147 and 17578 (eBL: K.3452+K.17474+K.17578+Sm.147). About 35 lines on the obverse and about 25 on the reverse across the joined pieces; with the linked piece K.17474 this is consistent with eBL's columns i (24) and iv (32).",
}
EXCLUDED = {
    'K.5932': "visual check: only one face is photographed: a fragment about 4.5 cm wide with about 11 lines and no ink number visible. eBL attributes 45 lines in columns i, iii and iv, which must be on both faces. The linked pieces K.13859 (about 8 lines) and K.17598 (about 4) also show one face each, and two other parts of eBL's join (K.8491 and K.13929) have no photograph in this set, so only about 23 of the 45 lines are visible and the second face is not confirmed.",
}
SPLIT = {
    'BM.40098': ['BM.40124'],
    'K.3452': ['K.17474'],
}

GENERAL = ("The Babylonian Theodicy is a dialogue in 27 stanzas of 11 lines between a sufferer and his friend about the injustice of the world. Each stanza begins with the same sign, and the initial signs together form an acrostic that names the author, Saggil-kinam-ubbib, an incantation priest, as a worshipper of god and king. This page follows the line numbering of the electronic Babylonian Library edition.")

ENTRIES = [
    {'chapter': ('SB', '-'), 'slug': 'dialogue', 'title': 'The Babylonian Theodicy (dialogue of the sufferer and his friend)', 'short': 'dialogue', 'summary': 'The sufferer complains that he is an orphan, poor and oppressed while the wicked prosper; his friend answers that the ways of the gods are unknowable and that the pious are rewarded in the end. At the close the friend concedes that the gods made humans prone to falsehood, and the sufferer asks for mercy from his god and goddess.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Babylonian Theodicy, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key="theodicy", ebl_text=('L', 2, 1),
    ebl_name='eBL corpus edition L II.1, Theodicy',
    label='Babylonian Theodicy (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of the Babylonian Theodicy in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id="saggil-kinam-ubbib", date_approx='composed c. 1000 BCE; tablets 7th-2nd c. BCE',
    century=-10, date_sort=-1000,
    themes=['theodicy', 'wisdom', 'dialogue', 'acrostic', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='babylonian theodicy saggil-kinam-ubbib acrostic dialogue sufferer friend wisdom',
    shelf_description="The Babylonian Theodicy, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Saggil-kinam-ubbib (c. 1000 BCE)',
    authors=[{"id": 'saggil-kinam-ubbib', "name": 'Saggil-kinam-ubbib', "dates": 'c. 1000 BCE', "century": -10, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian", "bio": 'Babylonian incantation priest whose name is spelled out by the acrostic of the Babylonian Theodicy.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

if __name__ == "__main__":
    engine.build_work(WORK)
