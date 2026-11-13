#!/usr/bin/env python3
"""
import_great-hymn-to-shamash.py -- The Great Hymn (Great Prayer) to Shamash, from the electronic Babylonian Library corpus edition L 
(English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_great-hymn-to-shamash.py --candidates
  python3 scripts/import_great-hymn-to-shamash.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    'BM.98732': "Photograph checked: obverse, reverse and edges of a narrow fragment about 4 cm tall, ink 98732 and Th.1905-4-9,238 on the edge; one face carries about 13 line-ends along its right side, the other is worn. Consistent with the British Museum's '13 lines of inscription' and eBL's line-ends 4'-13' of column i.",
    'VAT.10174': "Photograph checked (eBL photograph of the Vorderasiatisches Museum, Berlin): obverse, reverse and edges of a complete landscape tablet from Assur, ink VAT 10174 on the right edge; both faces are filled with about 17 to 20 long lines. Consistent with eBL's obverse lines 12'a-17'b on this school tablet, which also carries an excerpt of Erra and Ishum on the reverse.",
    'BM.36296': "Photograph checked: obverse, reverse and edges, with about 13 lines on the obverse and 12 on the reverse, well above eBL's 7 obverse lines. Ink numbers 36296 and 80-6-17,22 are on the edges, and a joined piece at the right is marked 38070 (join line visible).",
    'K.3182': "Photograph checked: obverse, reverse and all four edges of a large reconstructed tablet (about 10 x 17 cm), made of many fragments set in tan fill, with two columns per face in small script that leave room for 50 to 60 lines per column, consistent with eBL's i 56, ii 40, iii 53, iv 24. Ink numbers visible: K.3182 (right edge), K.5459 (left edge), K.3187, K.3312, S.311 and S.1398 (lower edge), plus further partly legible numbers on reverse pieces.",
    'Sm.1033': "Photograph checked: obverse, reverse and edges. One face is inscribed with two columns divided by a ruling: about 19 lines on the left and the beginnings of lines in a narrow right column, consistent with eBL's i 19, ii 7. The back is broken away; ink S.1033 is on the back.",
    'K.3474': "Photograph checked: the obverse has two columns in small script, about 40 to 45 and about 27 lines. On the reverse, a joined piece marked K.8233 sits across a column ruling with about 9 lines on each side, and an upper piece has about 12 lines in the left column. This fits eBL's i 42, ii 27, iii 10, iv 22. Ink K.3474 and S.372 are on the edges.",
    'K.3650': "Photograph checked: both faces are inscribed, each with a narrow and a wide column. One face has about 8 and 12 lines, the other about 2 and 13 lines, with rulings every two lines. Ink K.3650. This is consistent with eBL's i 9, ii 12, iii 12 if the lower face in the photo is the obverse.",
    'BM.33514': 'Photograph checked: obverse, reverse and edges of a join of ten or more pieces. Ink numbers include 33514, 33719, 33531, 33738, 33744, 33766, 48918 and Rm.IV 69, 87, 277 and 302. Both faces carry far more than the 16 obverse lines eBL attributes.',
    'BM.35077': "Photograph checked: one inscribed face with about 6 to 7 legible lines in its lower part. The upper part (about 1.4 cm) is worn and has room for the rest of eBL's 9 obverse lines. Ink 35077 is on the right edge; the other faces are eroded.",
    'BM.38849': "Photograph checked: one inscribed face with about 13 to 15 lines of small script, consistent with eBL's 15 obverse lines. Ink 38849 is at a corner; the other face is worn.",
    '1883,0118.472': "Photograph checked: both faces are inscribed, one with about 13 to 14 lines and the other with about 12, consistent with eBL's columns ii 12 and iii 13. Ink 83-1-18,472 is on the face margin and the edge.",
    'BM.134517': "Photograph checked: one face has two columns divided by a ruling, with about 8 to 9 lines each; the other face has about 3 worn lines. This is consistent with eBL's ii 9, iii 3. Ink 134517 and 1932-12-12,512 are on the edge.",
    'BM.98631': "Photograph checked: one inscribed face with 5 ruled lines, consistent with eBL's column iv, 5 lines; the back is uninscribed. Ink 98631 and Th.1905-4-9,137 are on both long edges.",
}
EXCLUDED = {
}
SPLIT = {
    'K.3182': ['K.19835'],
    'BM.33514': ['BM.33465', 'BM.33516', 'BM.48914'],
}

GENERAL = ('The Great Hymn to Shamash is a Babylonian hymn of about 200 lines to the sun god as the judge who sees everything under heaven and the protector of travellers, merchants, the poor and the oppressed. It survives mainly on copies from the libraries of Nineveh and from Babylonian cities. This page follows the line numbering of the electronic Babylonian Library edition.')

ENTRIES = [
    {'chapter': ('SB', '-'), 'slug': 'hymn', 'title': 'Great Hymn to Shamash (Babylonian hymn to the sun god)', 'short': 'hymn', 'summary': 'The hymn praises Shamash, whose light illuminates heaven and earth, who watches over all peoples and creatures, judges the dishonest judge, the false merchant and the oppressor, rewards the honest, and hears the prayers of the weak and of travellers on land and sea.'},
]
for e in ENTRIES:
    e["intro"] = "<p>" + e.pop("summary") + "</p><p>" + GENERAL + "</p>"
    e.setdefault("description", "The Great Hymn to Shamash, " + e.pop("short") + ": {covered} of {lines} lines, each shown on a "
                 "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                 "B. R. Foster's English translation.")

WORK = engine.simple_work(
    key='great-hymn-to-shamash', ebl_text=('L', 3, 4),
    ebl_name='eBL corpus edition L III.4, Great Prayer to Shamash (ed. G. Rozzi)',
    label='Great Hymn to Shamash (cuneiform tablets)', entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of the Great Hymn to Shamash in the eBL corpus edition (electronic Babylonian Library, LMU Munich)",
    author_id='anonymous-babylonian-poet', date_approx='composed late 2nd millennium BCE; tablets 7th-1st c. BCE',
    century=-12, date_sort=-1100,
    themes=['shamash', 'sun-god', 'hymn', 'justice', 'mesopotamian', 'akkadian', 'cuneiform'],
    search_terms='great hymn to shamash utu sun god justice prayer hymn babylonian',
    shelf_description="The Great Hymn to Shamash, read line by line on photographed clay tablets, with each tablet's own transliteration and B. R. Foster's English translation from the electronic Babylonian Library.",
    author_name='Anonymous Babylonian poet (late 2nd millennium BCE)',
    authors=[{'id': 'anonymous-babylonian-poet', 'name': 'Anonymous (Babylonian poets)', 'dates': '2nd-1st millennium BCE', 'century': -12, 'era': 'Ancient Near East', 'tradition': 'mesopotamian', 'language': 'Akkadian', 'bio': 'Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.'}],
    checks=CHECKS, excluded=EXCLUDED, split=SPLIT,
)

# QC round 2: K.19835 (joined to K.3182, photographed separately) is a flake about 2 cm across with two or three
# lines and a ruling; eBL does not say which lines it carries and it cannot be placed by eye, so its photograph is
# not linked to any section.
WORK["piece_lines"] = {"K.3182": {"K.19835": {"labels": [], "note": (
    "K.3182 is joined to K.19835, a flake about 2 cm across with two or three lines and a ruling, photographed "
    "separately; eBL does not say which lines it carries and it cannot be placed on the photograph, so its photograph "
    "is not linked, and a few signs of two or three lines of the hymn may be on it rather than on the K.3182 "
    "photograph.")}}}

if __name__ == "__main__":
    engine.build_work(WORK)
