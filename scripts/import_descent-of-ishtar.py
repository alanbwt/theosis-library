#!/usr/bin/env python3
"""
import_descent-of-ishtar.py -- The Descent of Ishtar to the Netherworld, from the electronic
Babylonian Library corpus edition L I.8 (ed. A. Setälä; English by B. R. Foster).

Uses the shared engine in import_gilgamesh.py; read its docstring for the chain of evidence.
  python3 scripts/import_descent-of-ishtar.py --candidates
  python3 scripts/import_descent-of-ishtar.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_gilgamesh as engine  # noqa: E402

CHECKS = {
    "K.162": "Photograph checked: obverse, reverse and edges of a tall single-column tablet, ink number K.162 and 'W.A.I. IV 31' on the right edge; the obverse is fully inscribed and the reverse ends with a ruling, one more line and an uninscribed area, consistent with eBL's obverse (80 lines) and reverse (58 lines). Each face is shown as a crop of the British Museum photograph.",
}

ENTRIES = [{
    "chapter": ("SB", "-"),
    "slug": "standard-babylonian",
    "title": "Descent of Ishtar to the Netherworld (Standard Babylonian version)",
    "description": ("The Akkadian Descent of Ishtar to the Netherworld: {covered} of {lines} lines, each shown on a "
                    "photographed cuneiform tablet ({tablets} tablets), with the eBL transliteration of that tablet and "
                    "B. R. Foster's English translation."),
    "intro": ("<p>Ishtar decides to go down to the Netherworld, the 'Land of No Return' ruled by her sister "
              "Ereshkigal. At each of the seven gates the gatekeeper removes one of her garments or ornaments, until "
              "she stands naked before Ereshkigal, who has her struck with diseases. While Ishtar is below, all "
              "mating on earth stops. Ea creates a being who obtains the water of life; Ishtar is sprinkled with "
              "it and returns, but a substitute must be given, and the text ends with instructions concerning "
              "Dumuzi and a ritual for the dead.</p>"
              "<p>The poem is an Akkadian adaptation of the Sumerian 'Inana's Descent'. The main copies are a "
              "Neo-Assyrian tablet from Nineveh (K.162) and tablets from Ashur. This page follows the line numbering "
              "of the electronic Babylonian Library edition.</p>"),
    "date_approx": "composed 2nd millennium BCE; tablets 8th-7th c. BCE",
}]

WORK = engine.simple_work(
    key="descent-of-ishtar", ebl_text=("L", 1, 8),
    ebl_name="eBL corpus edition L I.8, Descent of Ishtar (ed. A. Setälä, rev. Z. J. Földi, A. Hätinen, E. Jiménez, G. Rozzi)",
    label="Descent of Ishtar", entries=ENTRIES,
    translator="B. R. Foster", translator_short="B. R. Foster (eBL edition)",
    translation_source="B. R. Foster, English translation of the Descent of Ishtar in the eBL corpus edition (electronic Babylonian Library, LMU Munich, 2022 and later)",
    author_id="anonymous-babylonian-poet", date_approx="composed 2nd millennium BCE; tablets 8th-7th c. BCE",
    century=-12, date_sort=-1100,
    themes=["descent-of-ishtar", "ishtar", "ereshkigal", "netherworld", "mesopotamian", "akkadian", "cuneiform"],
    search_terms="descent of ishtar inanna ereshkigal netherworld land of no return dumuzi tammuz seven gates",
    shelf_description=("The Akkadian Descent of Ishtar to the Netherworld, read line by line on photographed clay "
                       "tablets, with each tablet's own transliteration and B. R. Foster's English translation from the "
                       "electronic Babylonian Library."),
    author_name="Anonymous Babylonian poet (2nd millennium BCE; tablets 8th-7th c. BCE)",
    checks=CHECKS,
    authors=[{"id": "anonymous-babylonian-poet", "name": "Anonymous (Babylonian poets)", "dates": "2nd-1st millennium BCE",
              "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian",
              "bio": "Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets."}],
)

# K.162 is a tall tablet photographed as obverse, edges and reverse stacked vertically (14191 px tall);
# each face is published as its own crop so the script stays legible.  Bands measured on the photograph:
# obverse with its side edges y 359-5911, lower edge 6071-6639, reverse 6871-12343 (of 14191).  The upper
# face is fully inscribed and the lower face ends in an uninscribed area, consistent with eBL's 80 obverse
# and 58 reverse lines, so the upper face is the obverse.
WORK["crops"] = {"K.162": {"obverse": (0.0, 0.020, 1.0, 0.421), "reverse": (0.0, 0.480, 1.0, 0.874)}}

if __name__ == "__main__":
    engine.build_work(WORK)
