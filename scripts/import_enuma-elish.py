#!/usr/bin/env python3
"""
import_enuma-elish.py -- Enuma Elish (Babylonian Poem of Creation), Tablets I-VII, from the
electronic Babylonian Library corpus edition L I.2 (ed. A. C. Heinrich, rev. Z. J. Földi,
E. Jiménez; English by B. R. Foster), one entry per tablet.

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence
(manuscript-level eBL ATF + eBL English + photograph of the same manuscript,
eBL's line-to-manuscript attribution, visual check of every photograph used).

Usage:
  python3 scripts/import_enuma-elish.py --candidates   # list the tablets the selection would use
  python3 scripts/import_enuma-elish.py                # build
"""
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

KEY = "enuma-elish"

# Visual checks of the eBL photographs used (2026-11-12).
CHECKS = {
    'K.19822': "Photograph checked: one face of a small fragment about 2.5 cm across, no ink number visible; about seven short lines of signs at the left, the right part broken away. Consistent with eBL's seven reverse lines.",
    'K.12830': "Photograph checked: one face of a small fragment about 2 cm across, no ink number visible; about seven or eight lines of signs, all broken at both ends. Consistent with eBL's eight reverse lines (the British Museum description counts six).",
    'BM.37981': "Photograph checked: obverse, reverse and edges of a small school-tablet fragment about 3 cm across, ink 37981 on the left edge; one face carries about six short lines in its left part and the other a few lines, consistent with eBL's six obverse lines. The joined piece 1880,0617.2892 (about 1.5 cm, a few signs on two faces) is photographed separately and is linked as well.",
    'K.5419.C': "Photograph checked: obverse, reverse and edges, ink K.5419.c on the bottom edge. About 14 to 16 lines on the obverse and a few lines along the left side of the reverse, consistent with eBL's 16 obverse lines of Tablet I and one reverse line of Tablet II.",
    'BM.45528': "Photograph checked: obverse, reverse and edges of a tall tablet (about 17 cm) built from many joined pieces, some with plaster, ink 45528 on the left edge and 47197 (81-8-30,719) and 47150 on joined pieces on the right edge. Both faces densely inscribed in small script, consistent with eBL's 58 obverse and 39 reverse lines.",
    'BM.36726': "Photograph checked: obverse, reverse and edges of a joined tablet, ink 36726 on the right edge. The obverse carries 15 or more lines and the reverse ruled sections of text, easily enough for eBL's six obverse lines.",
    'K.4657': "Photograph checked: obverse, reverse and edges of a tablet made of many joined pieces, ink K.4657, S.747 and K.168.. on the bottom edge, K.9427 on the obverse, and K.10008 and K.12102 on the reverse. The obverse is densely inscribed with well over 30 lines and the reverse has about 12 to 15 lines in its upper part, consistent with eBL's excerpts from Tablets I to V on the obverse and 14 reverse lines of Tablet VII.",
    'BM.36681': "Photograph checked: obverse, reverse and edges of two joined pieces, ink 36681 on the left edge and a faint, illegible number on the joined piece. About eight lines on the obverse, consistent with eBL's seven; the reverse is mostly worn with a few signs.",
    '1881,0727.80': "Photograph checked: obverse, reverse and edges, ink 81-7-27,80 on the left edge. Both faces of this tablet (about 8 cm wide) are covered in small, worn script with about 25 to 30 lines each, consistent with eBL's 28 obverse and 26 reverse lines.",
    'BM.46803': "Photograph checked: obverse, reverse and edges, ink 46803 on the bottom edge. A fragment about 5 cm square in small script: the obverse is worn but shows text in its upper and lower parts and the reverse has about 15 to 18 lines; the area can hold eBL's 23 obverse and 21 reverse lines, though fewer are clearly legible.",
    'K.13299': "Photograph checked: obverse, reverse and edges of two joined pieces, ink K.13299 on one and Rm 504 on the other (right edge). About 15 to 16 lines on the obverse and four or five lines at the top corner of the reverse plus edge, broadly consistent with eBL's 19 obverse and 7 reverse lines.",
    'BM.37287': "Photograph checked: obverse and reverse only, with a faint ink number on the obverse margin. About five lines of large signs on the obverse, consistent with eBL's four; the reverse is uninscribed.",
    'Rm.982': "Photograph checked: obverse, reverse and edges of two joined pieces, ink Rm 982 and 80-7-19,178 on the left edge. About 20 lines on the obverse; the reverse surface is mostly lost but a narrow strip of signs runs down its left side for most of its height, so eBL's 20 obverse and 22 reverse lines are physically plausible, the reverse ones as fragments only.",
    'BM.45571': "Photograph checked: two faces only (no edges), with a faint, partly hidden ink number on the lower edge of the uninscribed face. One face has about eight or nine lines in its upper part, consistent with eBL's nine reverse lines; the other face is uninscribed.",
    'BM.38024': "Photograph checked: obverse, reverse and edges, ink 38024 on the bottom edge. About nine lines on the obverse and about seven or eight on the reverse, matching eBL's 9 and 8.",
    'BM.37969': "Photograph checked: obverse, reverse and edges, ink 37969 on the right edge. About six lines on the obverse (with a ruling) and a few lines on the reverse, enough for eBL's four obverse lines.",
    'BM.40559': "Photograph checked: obverse, reverse and edges of a nearly complete small tablet, ink 40559 on the bottom edge. Both faces are covered in very small script with about 30 to 40 lines each, consistent with eBL's 40 obverse and 30 reverse lines of Tablet II and one line of Tablet III.",
    'K.4832': "Photograph checked: obverse, reverse and edges, ink K.4832 and a yellow label on the right edge. A narrow fragment about 7.5 cm tall in small script with about 25 to 30 lines on each face, consistent with eBL's 27 obverse and 35 reverse lines.",
    'K.9511': "Photograph checked: obverse, reverse and edges, ink K.9511 on the reverse. The obverse has about 25 lines of small, partly worn script down its right half and the reverse a patch of about 10 to 12 lines, consistent with eBL's 27 obverse and 12 reverse lines.",
    'BM.38167': "Photograph checked: obverse, reverse and edges, ink 38167 on the left edge (on a paper label). About 15 lines on the obverse, easily enough for eBL's five; the reverse is worn with no clear lines.",
    'BM.44205': "Photograph checked: two faces only (no edges), with a partly visible, illegible ink number at the top of the inscribed face. About five lines on one face, matching eBL's five (uncertain) reverse lines; the other face is uninscribed.",
    '1879,0708.178': "Photograph checked: obverse, reverse and edges, ink 79-7-8,178 on the obverse margin and the bottom edge. About six to eight lines at the lower part of the obverse and about eight to ten at the top of the reverse, consistent with eBL's 8 and 10.",
    'BM.38864': "Photograph checked: obverse and reverse only, ink 38864 on the reverse. About 15 lines on the obverse (two columns in its lower part), easily enough for eBL's five; the reverse is uninscribed.",
    'BM.38396': "Photograph checked: obverse, reverse and edges, ink 38396 on the left and top edges. Both faces of this fragment (about 7.5 cm wide) are covered in small script with about 20 to 25 lines each, consistent with eBL's 19 obverse and 28 reverse lines.",
    'K.3473': "Photograph checked: obverse, reverse and edges of a tall tablet (about 17 cm) of several joined pieces, ink K.3473 on the right edge and Rm 615 and 79-7-8,296 on the left edge. Both faces are packed with very small script, about 80 or more lines on the obverse and 50 or more on the reverse, consistent with eBL's 85 and 53.",
    'BM.42285': "Photograph checked: obverse, reverse and edges, ink 42285 on the right edge and 81-7-1,45 on the top edge. About 20 to 23 lines on the obverse and about 18 to 20 on the reverse, consistent with eBL's 23 and 19.",
    'K.8575': "Photograph checked: obverse, reverse and edges, ink K.8575 on the bottom edge. About seven or eight lines on the obverse and about eight or nine at the top of the reverse, matching eBL's 8 and 9.",
    'BM.33891': "Photograph checked: obverse, reverse and edges, ink 33891 and Rm IV 453 on the left edge. About eight or nine lines on the obverse, consistent with eBL's seven; the reverse also carries about ten lines.",
    'K.1353': "Photograph checked: obverse, reverse and all edges of a complete small tablet, ink K.1353 on the top edge. Every surface is covered in small script (about 30 lines per face), so eBL's single reverse line is easily accommodated.",
    'BM.36667': "Photograph checked: obverse, reverse and edges, ink 36667 on the left edge. About six lines on the obverse, consistent with eBL's five; the reverse is worn and uninscribed.",
    'K.16706': "Photograph checked: one face of a small fragment about 2.5 cm tall, ink K.16706 along the right edge. About ten lines of signs, consistent with eBL's eleven obverse lines.",
    'K.7361': "Photograph checked: obverse, reverse and edges, ink K.7361 on the reverse and a partly visible number on the left edge. About 12 lines on the obverse and about ten along the right side of the reverse, easily enough for eBL's one obverse line.",
    'F.2': "Photograph checked: two faces of a narrow fragment about 4.5 cm long (no edges, no ink number visible). About eight to ten lines on one face and about five to seven on the other, broadly consistent with eBL's 10 obverse and 7 reverse lines.",
    'BM.36387': "Photograph checked: obverse, reverse and edges, ink 36387 on the bottom edge (which also carries a line of signs). About nine lines on the obverse with rulings, enough for eBL's five; the reverse also carries about eight lines.",
    'K.3437': 'Photograph checked: obverse, reverse and edges of a large tablet of joined pieces (about 14 cm tall), ink "K.3437, Rm 641, joined" on the left edge, Rm 641 on the obverse and another Rm number on the left edge. Both faces are covered in small script with about 45 to 50 lines each, consistent with eBL\'s 48 obverse and 46 reverse lines.',
    'K.5420.C': "Photograph checked: obverse, reverse and edges, ink K.5420c and a yellow label on the top edge. The obverse is worn at the top but has about 15 to 19 lines in its lower part, and the reverse about 25 lines, consistent with eBL's 19 and 27.",
    'K.11863': "Photograph checked: both faces and edges, ink K.11863 on the uninscribed face. The inscribed face has about ten lines (photographed in the obverse position, which eBL calls the reverse), broadly consistent with eBL's eleven lines of Tablet IV plus one line of Tablet V.",
    'K.3567': "Photograph checked: obverse, reverse and edges, ink K.3567 on the bottom edge and K.8588 on a joined piece. About 25 to 27 lines on the obverse, consistent with eBL's 27 obverse lines of Tablet V. The reverse is broken at the top: a damaged row of signs along the broken upper part is eBL's reverse 1'-2' (V 158 lost at r 1', then the catch-line VI 1 at r 2'); after a blank space, the two clear lines in the middle of the reverse are Ashurbanipal's colophon (eBL r 3'-4', 'tup-pi 5.KAM2.ME e-nu-ma e-lis'), as eBL's record of K.3567 for Tablet V (colophon field) gives them.",
    'K.2164': "Photograph checked: obverse, reverse and edges of a tablet of several joined pieces, ink K.2164 on the left edge, K.2195 on the right edge and K.3510 on the bottom edge. Both faces carry many lines (20 or more each), easily enough for eBL's two obverse lines.",
    'K.3445': "Photograph checked: obverse, reverse and edges of a tall tablet (about 15 cm) of joined pieces, ink K.3445, Rm 396 and a yellow label on the left edge and K.171.. (partly legible) on a small reddish piece at the top. The reverse is covered in very small script, about 60 or more lines, consistent with eBL's 68; the obverse surface is lost in its upper half but keeps line beginnings down its left side and about 20 to 25 full lines below, enough for eBL's 40.",
    'BM.38049': "Photograph checked: obverse, reverse and edges, ink 38049 on the reverse. About six to eight worn lines on the obverse below a ruling, enough for eBL's five; the reverse is uninscribed.",
    'Rm.395': "Photograph checked: obverse, reverse and edges, ink Rm 395 on the left edge and the obverse margin. About nine or ten lines on the obverse and about ten lines in the upper right of the reverse, consistent with eBL's nine obverse lines (Tablet V) and ten reverse lines (one of Tablet VI, nine of Tablet VII).",
    '1879,0708.47': "Photograph checked: obverse, reverse and four edges, ink number 79-7-8,47 on the reverse and lower edge. The obverse is badly worn with signs from about four or five lines surviving only along its right side, consistent with eBL's four obverse lines; the reverse is uninscribed.",
    'BM.38706': "Photograph checked: obverse, reverse and edges of two pieces joined with white plaster, ink 38706 on one piece and 39843 with an 80-11-.. registration number on the other. About 15 lines on the obverse and eight to ten on the reverse, easily enough for eBL's two obverse lines of Tablet V and one of Tablet VII.",
    'BM.32206': "Photograph checked: obverse, reverse and all edges of a large multi-piece tablet with plaster fill, ink numbers 32206 (76-11-17,1933) and 34723 on the top edge and 32237 on the left edge. Both faces are densely inscribed in small script, so eBL's single line in column ii is easily accommodated.",
    'BM.43969': "Photograph checked: obverse, reverse and edges, ink 43969 on the reverse and 81-7-1,1730 on the left edge. About eight lines on the obverse, enough for eBL's four; the reverse is uninscribed.",
    'BM.33572': "Photograph checked: obverse, reverse and edges of a small fragment about 2.5 cm wide, ink 33572 on the obverse and Rm IV 128 on an edge. About seven lines on the obverse, consistent with eBL's six; traces on the reverse.",
    'K.12000.B': "Photograph checked: obverse, reverse and edges of a joined fragment, ink K.12000 B and K.16062 on the left edge, K.13886 and K.138.. on the reverse. The obverse has about 27 lines of small script across three joined pieces, consistent with eBL's 27; the reverse is uninscribed.",
    'BM.33690': "Photograph checked: inscribed face and uninscribed back only (no edges), ink 33690 on the back. The fragment is about 3.5 cm wide and very worn, with about five or six lines still recognisable; enough surface for eBL's seven obverse lines.",
    'BM.54855': "Photograph checked: obverse and reverse only, ink 54855 and 82-5-22,1184 on the reverse. About nine lines on the obverse, matching eBL's nine; the reverse has a few lines in narrow columns.",
    'BM.38043': "Photograph checked: obverse, reverse and edges, ink 38043 on the left edge. About three to four lines of large signs at the top of the obverse plus ruled divisions; consistent with eBL's three obverse lines. The other face also carries about eight lines.",
    'K.3449.A': "Photograph checked: obverse, reverse and edges, ink K.3449 A on the top edge and reverse. About 9 to 10 lines along the left of the obverse and about 13 lines across the reverse, matching eBL's 9 and 13.",
    'K.9883': "Photograph checked: obverse, reverse and edges, ink K.9883 on the reverse and bottom edge. About 12 to 13 lines on each face, consistent with eBL's 13 and 13.",
    'K.13867': "Photograph checked: several angled views of a curved fragment (corner of a tablet), ink K.13867 on the edge and K.10614 on a joined piece. About nine to ten lines on each inscribed face, consistent with eBL's 9 obverse and 10 reverse.",
    'BM.55380': "Photograph checked: obverse, reverse and all edges, ink 55380 on the edges and 82-5-22,1713 on the reverse. About seven to eight lines on the obverse, consistent with eBL's seven plus one unplaced line; reverse uninscribed.",
    'K.5923': 'Photograph checked: one face of K.5923 alone, a fragment about 2.5 cm tall with about 12 lines; the joined pieces K.8512 (two columns on the obverse, text on the reverse, ink number K.8512) and K.18305 (about 5 lines) are photographed separately and are linked as well.',
    'K.13865': "Photograph checked: one face of a fragment made of two joined pieces (join line visible), about 3.5 cm wide; no ink number visible. About nine lines, matching eBL's nine reverse lines.",
    'BM.54311': "Photograph checked: obverse, reverse and edges, ink 54311 on the bottom edge. Both faces densely inscribed with 20 or more lines each, easily enough for eBL's three reverse lines.",
    'Sm.11': "Photograph checked: obverse, reverse and edges of a joined tablet laid out in ruled boxes, ink S.11 and S.1416 on the left edge and S.980 on a reverse piece. About four narrow columns of short lines on each face, consistent with eBL's eight columns of 3 to 11 lines.",
    '1882,0323.151': 'Photograph checked: obverse, reverse and edges, ink 82-3-23,151 on the obverse. One face has about seven short lines in ruled boxes; the reverse is uninscribed. A real fragment, separately photographed piece of Sm.11.',
    'BM.32574': "Photograph checked: obverse, reverse and edges, ink 32574 on the bottom edge and 76-11-17,2317 on the left edge. Both faces densely inscribed with 15 or more lines, easily enough for eBL's one obverse line.",
    'BM.55114': "Photograph checked: obverse, reverse and edges of a tablet of two joined pieces, ink 55114 and 82-5-22,1446 on the left edge and 55194 on the joined piece. About ten lines on the obverse, enough for eBL's seven.",
    'Rm.366': "Photograph checked: obverse, reverse and edges of a joined tablet in ruled boxes, ink Rm 366 on the left edge and 80-7-19,288 and 80-7-19,293 on joined pieces. Several narrow columns with short lines on both faces, consistent with eBL's columns of 3 to 10 lines.",
    'K.2854': "Photograph checked: obverse, reverse and edges, ink K.2854 and K.17249 on the bottom edge, K.17249 on the obverse corner and K.15650 on a small joined piece. About 18 to 20 lines on the obverse across the joined pieces, broadly consistent with eBL's 23; the reverse is uninscribed. The small piece K.15650 is visibly joined in this photograph (eBL's separate photograph filed under K.15650 shows K.16050 and is not used).",
    'K.8522': "Photograph checked: obverse, reverse and edges, ink K.8522 on the left edge. Both faces are covered in small script with about 30 lines each, consistent with eBL's 31 obverse and 33 reverse.",
    'K.9267': "Photograph checked: obverse, reverse and edges of two joined pieces, ink K.9267 on the obverse. About eight lines at the upper left of the obverse and about 20 lines across the reverse and its edge, broadly consistent with eBL's 8 and 24.",
    'K.17095': "Photograph checked: one face of a small flake about 3 cm wide; no ink number visible. About four or five lines of worn signs survive, broadly consistent with eBL's six obverse lines.",
    'BM.37379': "Photograph checked: obverse, reverse and edges, ink 37379 on the reverse. About ten lines on the obverse, consistent with eBL's nine; the reverse is uninscribed.",
    'BM.39798': "Photograph checked: obverse, reverse and edges, ink 39798 on the reverse. About 13 lines on the obverse, matching eBL's 13; the reverse is uninscribed.",
    'K.13761': "Photograph checked: two faces and edges, ink K.13761 on the top and bottom edges. The face shown on top has about 12 lines and the face shown below about five, matching eBL's 5 and 12 in total, though the photograph lays the faces out in the opposite order to eBL's obverse and reverse.",
    'K.8519': "Photograph checked: obverse, reverse and edges, ink K.8519 on the bottom edge. About eight lines on each face, enough for eBL's four obverse and eight reverse lines.",
    'K.7658': "Photograph checked: one face of a fragment about 6 cm tall with a smaller darker piece joined at the upper left; no ink number visible. Two columns with about 18 to 20 lines, consistent with eBL's 13 reverse lines.",
    'K.18576': "Photograph checked: one face of a small fragment about 2.5 cm across; no ink number visible. About five to six lines, matching eBL's six reverse lines.",
    'BM.34384': 'Photograph checked: BM.34384 alone, a narrow fragment with ink numbers 34384 and Sp. 503 and about eight worn lines; the joined pieces BM.35506 + BM.99642 (both faces densely inscribed) and BM.36146 are photographed separately and are linked as well.',
}
EXCLUDED = {
    'BM.48270': "visual check: photograph shows obverse, reverse and edges, ink 48270 on the right edge. The obverse has about eight to ten worn lines, enough for eBL's five, but the reverse surface is almost entirely worn away with only one small patch of two or three signs visible, so eBL's 21 reverse lines cannot be confirmed from this photograph.",
    'K.5661': "visual check: photograph shows obverse, reverse and edges, ink K.5661 on the left edge and K.11641 on the top edge (a joined piece). The obverse has several patches of text, perhaps 15 to 20 lines in all, but the reverse surface is largely lost, with only three small patches of signs (about six to eight lines' worth), so eBL's 14 reverse lines, and possibly all 22 obverse lines, cannot be confirmed from this photograph.",
}
SPLIT = {
    'BM.37981': ['1880,0617.2892'],
    'K.4832': ['K.23609'],
    'BM.32206': ['F.220'],
    'K.5923': ['K.8512', 'K.18305'],
    'Sm.11': ['K.4406', 'K.11169', '1882,0323.151'],
    'Rm.366': ['K.2053', 'BM.134499'],
    'BM.34384': ['BM.35506', 'BM.36146'],
}

TABLETS = {
    "I": ("Tablet I: the birth of the gods and Tiamat's army",
          "Before heaven and earth were named, Apsu and Tiamat mingled their waters and the gods were born. "
          "Disturbed by their noise, Apsu plans to destroy them; Ea puts him to sleep and kills him, and in his "
          "dwelling Marduk is born. Tiamat, urged on by other gods, creates monsters for battle and gives "
          "Qingu the Tablet of Destinies."),
    "II": ("Tablet II: the gods seek a champion",
           "Ea learns of Tiamat's preparations and reports to Anshar. Ea and then Anu go out against her and turn "
           "back. Marduk agrees to fight Tiamat on condition that the gods make his word supreme."),
    "III": ("Tablet III: the assembly of the gods",
            "Anshar sends his vizier Kakka to Lahmu and Lahamu to summon the gods, repeating the account of "
            "Tiamat's army and Marduk's demand. The gods gather, feast, and decree Marduk's destiny."),
    "IV": ("Tablet IV: Marduk defeats Tiamat",
           "The gods give Marduk kingship and weapons. He rides out on his storm chariot, catches Tiamat in his "
           "net, kills her with an arrow, binds her helpers and Qingu, takes the Tablet of Destinies, and splits "
           "Tiamat's body in two to form the sky."),
    "V": ("Tablet V: the ordering of the universe",
          "Marduk sets the stars, the year and the moon in their courses, forms features of the world from "
          "Tiamat's body, returns to the gods, is acclaimed king, and announces the building of Babylon."),
    "VI": ("Tablet VI: the creation of humankind and of Babylon",
           "Ea creates humankind from the blood of the guilty god Qingu to bear the gods' labour. The gods build "
           "Babylon and the temple Esagil for Marduk, hold a banquet, and begin to proclaim his fifty names."),
    "VII": ("Tablet VII: the fifty names of Marduk",
            "The gods continue to proclaim the names of Marduk with their meanings. An epilogue asks that the "
            "names be remembered, taught and pondered by later generations."),
}


def entries():
    out = []
    for t, (title, summary) in TABLETS.items():
        out.append({
            "chapter": ("SB", t),
            "slug": f"tablet-{t.lower()}",
            "title": f"Enuma Elish, {title}",
            "description": ("Enuma Elish (the Babylonian Poem of Creation), Tablet " + t + ": {covered} of {lines} lines, "
                            "each shown on a photographed cuneiform tablet ({tablets} tablets), with the eBL "
                            "transliteration of that tablet and B. R. Foster's English translation."),
            "intro": (f"<p>{summary}</p>"
                      "<p><em>Enuma Elish</em> ('When on high'), the Babylonian Poem of Creation, tells how Marduk, "
                      "god of Babylon, defeated Tiamat, created the ordered world and became king of the gods. It was "
                      "written on seven tablets and recited in Babylon during the New Year festival. The date of "
                      "composition is debated (proposals range from the 18th to the 12th century BCE); the surviving "
                      "copies date from the 9th to the 2nd century BCE and come from Ashur, Nineveh, Kish, Babylon, "
                      "Sippar, Uruk and other sites. This page follows the line numbering of the electronic "
                      "Babylonian Library edition.</p>"),
            "themes": [f"tablet-{t.lower()}"],
        })
    return out


WORK = {
    "key": KEY,
    "ebl_text": ("L", 1, 2),
    "ebl_name": "eBL corpus edition L I.2, Poem of Creation (Enuma elish) (ed. A. C. Heinrich, rev. Z. J. Földi and E. Jiménez)",
    "chapter_prefix": lambda ch: f"{ch['_stage_abbr']} {ch['name']}",
    "chapter_url": lambda ch: f"{engine.EBL_WEB}/corpus/L/1/2/{ch['_stage_abbr']}/{urllib.parse.quote(ch['name'])}",
    "siglum_label": "Lambert 2013 ms.",
    "siglum_re": r"Lambert 2013: Ms\. ([^;.]+)",
    "photo_checks": CHECKS,
    "excluded": EXCLUDED,
    "split_photos": SPLIT,
    "entries": entries(),
    "make_entry": engine.standard_entry,
    "author_id": "enuma-elish-author",
    "date_approx": "composed 2nd millennium BCE (date debated); tablets 9th-2nd c. BCE",
    "century": -12,
    "themes": ["enuma-elish", "creation", "marduk", "tiamat", "mesopotamian", "akkadian", "cuneiform"],
    "translator_short": "B. R. Foster (eBL edition)",
    "translator_line": ("The English is B. R. Foster's translation in the eBL edition (CC BY-NC-SA 4.0), one line of "
                        "English per line of the poem; italics mark uncertain renderings, as in the source."),
    "translation_source": "B. R. Foster, English translation of Enuma elish in the eBL corpus edition (electronic Babylonian Library, LMU Munich, 2021 and later)",
    "translator_notes": [
        "Akkadian: eBL transliteration of the signs on the photographed tablet (manuscript-level ATF), not a composite text.",
        "English: B. R. Foster's translation in the eBL edition; it renders eBL's composite text, including restorations from other tablets.",
        "Line numbers: eBL edition. Each section also gives the tablet's own column and line numbers.",
    ],
    "collection": {
        "key": KEY,
        "prefix": f"verified-{KEY}-",
        "label": "Enuma Elish",
        "group": "Mesopotamia",
        "date_sort": -1150,
        "author_name": "Babylonian Poem of Creation (2nd millennium BCE; tablets 9th-2nd c. BCE)",
        "source_url": "https://www.ebl.lmu.de/corpus/L/1/2",
        "critical_edition": "electronic Babylonian Library, Poem of Creation (ed. A. C. Heinrich), manuscript transliterations",
        "translator_name": "B. R. Foster (eBL edition)",
        "original_lang_label": "Akkadian · eBL transliteration of each tablet",
        "original_lang_code": "akk",
        "edition_label": "",
        "search_terms": "enuma elish enuma elis babylonian creation epic marduk tiamat apsu qingu seven tablets of creation",
        "description": ("Enuma Elish, the Babylonian Poem of Creation, Tablets I-VII, read line by line on photographed "
                        "clay tablets: each section shows one tablet's own transliteration with B. R. Foster's English "
                        "translation from the electronic Babylonian Library."),
    },
}

# QC round 2 (2026-11-12): eBL's corpus attribution numbers VI 1 on K.3567 "r 1'", the label it also gives V 158;
# eBL's own transcription of K.3567 (colophon field of its Tablet V manuscript record) numbers V 158 r 1' and the
# catch-line VI 1 r 2', then the colophon r 3'-4'.  Checked on the photograph: one damaged row on the broken top
# of the reverse, a blank space, then two clear colophon lines.
WORK["ms_line_fix"] = {("SB:VI", "1", "K.3567"): ("2'", (
    "eBL's corpus edition labels this line r 1', the label it also gives V 158; eBL's own transcription of K.3567 "
    "(colophon field of its Tablet V record) numbers it r 2', after V 158 at r 1', so it is given here as r 2'. On the "
    "photograph it is the damaged row of signs along the broken top of the reverse, not the two clear lines below the "
    "blank space, which are Ashurbanipal's colophon."))}
# K.9267: eBL labels VII 40-44 as obverse 1'-5' and VII 45-47 as 32'-34'.  The photograph shows one block of about
# eight lines at the upper left of the obverse (eBL attributes eight obverse lines, VII 40-47), so the lines are
# consecutive on the tablet.
WORK["extra_notes"] = {("SB:VII", "K.9267"): (
    "The photograph shows the obverse text as one block of about eight lines at its upper left (eBL attributes eight "
    "obverse lines to K.9267, VII 40-47), so these lines are consecutive on the tablet; eBL's labels 32'-34' for lines "
    "45-47 are probably a slip for 6'-8'. Count down from the top line of that block.")}

if __name__ == "__main__":
    engine.build_work(WORK)
