#!/usr/bin/env python3
"""
import_ashoka_edicts.py -- the Edicts of Ashoka (c. 260-232 BCE), site by site, on E. Hultzsch's
collotype plates of inked impressions of the rocks and pillars (and, where a photograph of the
stone can be mapped line by line, on that photograph).

One entry per inscribed rock or pillar (Girnar, Kalsi, ...). Inside each entry, one section per edict
(or per face, where an edict runs over two faces). Each section shows Hultzsch's transliteration of
exactly the lines of that edict at that site (his line numbers), Hultzsch's English for the same
edict at that site, and the plate (or photograph) that carries those lines.

Chain of evidence
-----------------
1. ORIGINAL TEXT  E. Hultzsch, Inscriptions of Asoka. New edition. Corpus Inscriptionum Indicarum,
                  vol. I (Oxford: Clarendon Press for the Government of India, 1925).
                  Scan: archive.org item InscriptionsOfAsoka.NewEditionByE.Hultzsch (300 ppi,
                  digitized by Artur Karp, University of Warsaw; Public Domain Mark 1.0).
                  The transliteration was transcribed from the page images: the archive.org OCR
                  (HultzschCorpusAsokaSearchable_djvu.txt), which loses most diacritics, was used
                  only as a starting point; every line was read and corrected on the printed page
                  image (bands of the page cut out at 0.75 of the 300 ppi scan, doubtful letters at
                  full resolution), and the result was compared word by word with the OCR to catch
                  omissions (scratch tool qc.py; every disagreement other than OCR noise was looked
                  up on the image again). The transcriptions are kept in
                  data/sources/ashoka-edicts/proofread/<site>.txt, one block per edict, with the
                  printed pages and archive.org leaf numbers.
                  Kept as printed: Hultzsch's brackets [ ] (letters damaged or uncertain on the
                  stone), dots for lost letters, his section letters (A), (B) ..., the punctuation
                  strokes | of the Kalsi rock, and his spelling. Hultzsch's footnote numbers are left
                  out; his footnotes (alternative readings of Senart and Buhler, corrections such as
                  "read ...") are not reproduced. Wrapped lines are joined to their numbered line.
2. ENGLISH        Hultzsch's own translation in the same volume, printed after each text, read from
                  the same page images (footnote numbers left out). Section letters as printed.
3. IMAGES         a) Hultzsch's plates: collotype reproductions of inked impressions (estampages)
                     taken on the rocks and pillars for the Archaeological Survey of India (preface,
                     p. iii; postscript, p. iv). An inked impression is a direct contact copy of the
                     stone; it is labelled as such on every section. The plates are leaves of the same
                     archive.org scan, fetched at full resolution through the archive.org BookReader
                     image service, and cropped to the band that holds the edict, keeping the plate's
                     margin labels (edict numerals and line numbers).
                  b) Rummindei (Lumbini) only: a colour photograph of the inscribed pillar, Wikimedia Commons
                     'Lumbini inscription (complete)' (Photo Dharma / Charlie Phillips, CC BY 2.0), on which the
                     five lines were counted and their first and last signs read.
4. MAPPING        Edict -> lines at a site: Hultzsch's line numbers in the transcription.
                  Lines -> plate: the plate's own margin labels (Roman numeral at the first line of
                  each edict, line numbers every second line), checked on each crop by counting the
                  lines of the band against the transcription. Nothing is interpolated.

Usage:
    python3 scripts/import_ashoka_edicts.py            # build entries + scans
    python3 scripts/import_ashoka_edicts.py --force-scans
"""

import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
KEY = "ashoka-edicts"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
LEAVES = SRC / "hultzsch" / "leaves"
PROOF = SRC / "proofread"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
FORCE = "--force-scans" in sys.argv

IA_ID = "InscriptionsOfAsoka.NewEditionByE.Hultzsch"
IA_FILE = "HultzschCorpusAsokaSearchable"
IA_PAGE = f"https://archive.org/details/{IA_ID}"
UA = "TheosisLibrary/1.0 (non-commercial research)"

HULTZSCH = ("E. Hultzsch, Inscriptions of Asoka. New Edition (Corpus Inscriptionum Indicarum, vol. I), "
            "Oxford: Clarendon Press for the Government of India, 1925")


def leaf_url(n):
    return (f"https://ia601005.us.archive.org/BookReader/BookReaderImages.php?zip=/32/items/{IA_ID}/{IA_FILE}_jp2.zip"
            f"&file={IA_FILE}_jp2/{IA_FILE}_{n:04d}.jp2&id={IA_ID}&scale=1&rotate=0")


def leaf_view(n):
    return f"https://archive.org/details/{IA_ID}/page/n{n}/mode/1up"


def fetch_leaf(n):
    p = LEAVES / f"leaf_{n:04d}_s1.jpg"
    if not p.exists() or p.stat().st_size < 5000:
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sL", "-m", "600", "-A", UA, "-o", str(p), leaf_url(n)], check=True)
    return p


# ---------------------------------------------------------------------------
# Plates: archive.org leaf, Hultzsch's caption, the page it faces.
# ---------------------------------------------------------------------------
PLATES = {
    "girnar-1": (138, "First and second rock-edicts: Girnar", "facing p. 4"),
    "girnar-2": (145, "Third to fifth rock-edicts: Girnar", "facing p. 10"),
    "girnar-3": (150, "Sixth to eighth rock-edicts: Girnar", "facing p. 14"),
    "girnar-4": (159, "Ninth to twelfth rock-edicts: Girnar", "facing p. 22"),
    "girnar-5": (164, "Thirteenth and fourteenth rock-edicts: Girnar", "facing p. 26"),
    "kalsi-east": (183, "Kalsi rock: East face", "facing p. 44"),
    "kalsi-south": (190, "Kalsi rock: South face / Kalsi rock: North face", "facing p. 50"),
    "dhauli-left": (245, "Dhauli rock: left column", "facing p. 94"),
    "dhauli-right": (252, "Dhauli rock: right column", "facing p. 100"),
    "topra-north": (279, "Delhi-Topra pillar: North face", "facing p. 122"),
    "topra-west": (281, "Delhi-Topra pillar: West face", "facing p. 123"),
    "topra-south": (287, "Delhi-Topra pillar: South face", "facing p. 128"),
    "topra-east": (288, "Delhi-Topra pillar: East face", "facing p. 129"),
    "topra-circular": (295, "Delhi-Topra pillar: circular inscription", "facing p. 134"),
    "rummindei": (339, "Rummindei pillar-inscription / Nigali Sagar pillar-inscription", "facing p. 164"),
    "calcutta-bairat": (351, "Calcutta-Bairat rock-inscription", "facing p. 173"),
}

# Photographs of the stones (Wikimedia Commons), used where the lines can be read on the photograph.
PHOTOS = {
    "lumbini": {
        "path": SRC / "photos" / "Lumbini_inscription_complete.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/43/Lumbini_inscription_%28complete%29.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Lumbini_inscription_(complete).jpg",
        "credit": "Wikimedia Commons, 'Lumbini inscription (complete)', photographs by Photo Dharma (Anandajoti Bhikkhu, Penang) "
                  "and Charlie Phillips, joined into one image",
        "license": "CC BY 2.0 (as stated on Wikimedia Commons)",
    },
}

# ---------------------------------------------------------------------------
# Sites. For each section (edict name as in the proofread file): crop = (plate, x0, y0, x1, y1) in
# full-resolution leaf pixels, and a note on what the crop shows (checked on the image).
# ---------------------------------------------------------------------------
SITES = [
    {
        "slug": "girnar",
        "proof": "girnar.txt",
        "title": "Edicts of Ashoka at Girnar: the fourteen Major Rock Edicts",
        "place": "Girnar, near Junagadh (Gujarat)",
        "script": "Brahmi",
        "date_approx": "c. 256 BCE (edicts dated 12 and 13 years after Ashoka's consecration)",
        "manuscript": "Girnar rock, near Junagadh (Gujarat): the fourteen Major Rock Edicts of Ashoka in Brahmi script, c. 256 BCE; "
                      "impressions taken for the Archaeological Survey of India and reproduced in Hultzsch 1925",
        "desc": "Ashoka's fourteen Major Rock Edicts on the Girnar rock in Gujarat (c. 256 BCE): Hultzsch's transliteration of the "
                "Prakrit text and his 1925 English, edict by edict, each with the impression of the lines that carry it.",
        "themes": ["rock-edicts", "major-rock-edicts", "kalinga"],
        "sections": {
            "I": (("girnar-1", 0, 120, 2834, 2040), "the upper band of the plate, marked I in the left margin and numbered 2 to 12 in both margins: 12 lines, as in the transcription"),
            "II": (("girnar-1", 0, 1960, 2834, 3060), "the lower band of the plate, below the ruled line, marked II and numbered 2 to 8: 8 lines"),
            "III": (("girnar-2", 300, 330, 4342, 1140), "the top band of the plate, marked III and numbered 2 to 6: 6 lines"),
            "IV": (("girnar-2", 300, 1060, 4342, 2440), "the middle band, between the ruled lines, marked IV and numbered 2 to 12: 12 lines"),
            "V": (("girnar-2", 200, 2380, 4342, 3300), "the lowest band, marked V and numbered 2 to 8; the broken lower edge of the rock cuts the band, and only a few letters of line 9 survive at the right; line 10 is lost"),
            "VI": (("girnar-3", 300, 560, 3826, 2160), "the upper band, marked VI and numbered 2 to 14: 14 lines"),
            "VII": (("girnar-3", 300, 1950, 3826, 2630), "the narrow band marked VII between two ruled lines (3 lines, numbered 2 in the margins); the last line of VI shows above it and the first line of VIII below"),
            "VIII": (("girnar-3", 300, 2380, 3826, 3110), "the lowest band, marked VIII and numbered 2 and 4: 5 lines"),
            "IX": (("girnar-4", 100, 480, 5313, 1620), "the top band, marked IX and numbered 2 to 8: 9 lines"),
            "X": (("girnar-4", 100, 1250, 5313, 2300), "the band in the middle of the crop, marked X in the left margin and numbered 2 and 4 (4 lines), between the ruled lines; the end of IX shows above it and the start of XI below"),
            "XI": (("girnar-4", 100, 1650, 5313, 2700), "the band in the middle of the crop, marked XI and numbered 2 and 4 (4 lines); the end of X shows above it and the start of XII below"),
            "XII": (("girnar-4", 100, 2300, 5313, 3350), "the lowest band, marked XII and numbered 2 to 8: 9 lines"),
            "XIII": (("girnar-5", 250, 330, 5905, 2300), "the upper part of the plate, marked XIII and numbered 2 to 12: the two fragments on the left (recovered pieces of the left part of the edict, the second holding the beginnings of lines 11-12) and the main surface on the right; the gap between them is the part of the rock destroyed in the nineteenth century, which Hultzsch marks with dots"),
            "XIV": (("girnar-5", 1600, 2560, 4300, 3420), "the separate band at the foot of the plate, marked XIV and numbered 2 to 6: 6 lines"),
        },
    },
    {
        "slug": "kalsi",
        "proof": "kalsi.txt",
        "title": "Edicts of Ashoka at Kalsi: the fourteen Major Rock Edicts",
        "place": "Kalsi, near Dehradun (Uttarakhand)",
        "script": "Brahmi",
        "date_approx": "c. 256 BCE (edicts dated 12 and 13 years after Ashoka's consecration)",
        "manuscript": "Kalsi rock, near Dehradun (Uttarakhand), now in an ASI shelter: the fourteen Major Rock Edicts of Ashoka in "
                      "Brahmi script, c. 256 BCE; impressions taken for the Archaeological Survey of India and reproduced in Hultzsch 1925",
        "desc": "Ashoka's fourteen Major Rock Edicts on the Kalsi rock (c. 256 BCE), with the fullest Brahmi text of Edict XIII on the "
                "conquest of Kalinga and the Greek kings: Hultzsch's transliteration and 1925 English, each edict with the impression "
                "of the lines that carry it.",
        "themes": ["rock-edicts", "major-rock-edicts", "kalinga", "greek-kings"],
        "sections": {
            "I": (("kalsi-east", 600, 350, 5850, 1360), "the top of the east face: the edict begins at the numeral I in the left margin and runs over lines 1-4 (line numbers every second line in both margins)"),
            "II": (("kalsi-east", 600, 550, 5850, 1560), "lines 4-6 of the east face, from the numeral II in the left margin (part of line 4) to the numeral III"),
            "III": (("kalsi-east", 600, 650, 5850, 1660), "lines 6-8 of the east face, from the numeral III in the left margin to the end of line 8 (the numeral IV stands at line 9)"),
            "IV": (("kalsi-east", 600, 800, 5850, 1810), "lines 9-13 of the east face, from the numeral IV to the numeral V"),
            "V": (("kalsi-east", 600, 1100, 5850, 2110), "lines 13-17 of the east face, from the numeral V to the numeral VI"),
            "VI": (("kalsi-east", 600, 1450, 5850, 2460), "lines 17-21 of the east face, from the numeral VI to the numeral VII"),
            "VII": (("kalsi-east", 600, 1650, 5850, 2660), "lines 21-22 of the east face, from the numeral VII to the numeral VIII"),
            "VIII": (("kalsi-east", 600, 1750, 5850, 2760), "lines 22-23 of the east face, from the numeral VIII to the numeral IX"),
            "IX": (("kalsi-east", 600, 1950, 5850, 2960), "lines 24-27 of the east face, from the numeral IX to the numeral X"),
            "X": (("kalsi-east", 600, 2150, 5850, 3160), "lines 27-29 of the east face, from the numeral X to the numeral XI"),
            "XI": (("kalsi-east", 600, 2300, 5850, 3310), "lines 29-30 of the east face, from the numeral XI to the numeral XII"),
            "XII": (("kalsi-east", 600, 2450, 5850, 3460), "lines 30-35 of the east face, from the numeral XII to the numeral XIII"),
            "XIII-east": (("kalsi-east", 600, 2600, 5850, 3650), "lines 35-39 at the foot of the east face, from the numeral XIII in the left margin to the last line (38 is the last number printed in the margin; line 39 is the row below it)"),
            "XIII-south": (("kalsi-south", 550, 380, 2450, 1720), "the upper part of the south-face impression, numbered 4 to 18 in both margins. The impression begins at line 4; lines 1-3, of which only the syllables [ney]u (O) ichha of line 3 survive, are not on the plate"),
            "XIV": (("kalsi-south", 550, 1500, 2450, 2250), "the lower part of the south-face impression, from the numeral XIV in the left margin (line 19) to line 23, numbered 20 and 22"),
            "elephant": (("kalsi-south", 750, 2400, 2250, 3450), "the impression of the north face (lower figure of the plate): the outline of an elephant with the word gajatame written between its legs"),
        },
    },
    {
        "slug": "dhauli",
        "proof": "dhauli.txt",
        "title": "Edicts of Ashoka at Dhauli: the two Separate Edicts to the officers of Tosali",
        "place": "Dhauli, near Bhubaneswar (Odisha)",
        "script": "Brahmi",
        "ref_names": {"Sep-I": "First Separate Rock Edict", "Sep-II": "Second Separate Rock Edict"},
        "date_approx": "c. 256 BCE (undated; issued with the Major Rock Edicts in conquered Kalinga)",
        "manuscript": "Dhauli rock, near Bhubaneswar (Odisha), ancient Tosali in Kalinga: the two Separate Rock Edicts of Ashoka in "
                      "Brahmi script, cut beside the Major Rock Edicts I-X and XIV; impressions taken for the Archaeological Survey "
                      "of India and reproduced in Hultzsch 1925",
        "desc": "The two Separate Edicts at Dhauli in Kalinga, in which Ashoka tells the officers of Tosali that all men are his "
                "children and how to treat prisoners and the unconquered border peoples: Hultzsch's transliteration and 1925 "
                "English, each with the inked impression of the rock.",
        "themes": ["separate-edicts", "kalinga", "tosali", "justice"],
        "sections": {
            "Sep-I": (("dhauli-left", 150, 380, 2720, 3360), "the whole left column of the rock, headed 'Sep. ed. I' in the margin and numbered 2 to 26 at the left (2 to 24 at the right): 26 lines. The upper left corner of the rock is broken away, so the first lines begin further right"),
            "Sep-II": (("dhauli-right", 120, 2330, 3260, 3520), "the lower part of the right column, from the label 'Sep. ed. II' in the left margin to the last line, numbered 2 to 10 in both margins: 11 lines. Above it on the plate are the ends of Rock Edicts VII-X and XIV"),
        },
    },
    {
        "slug": "delhi-topra",
        "proof": "delhi-topra.txt",
        "title": "Edicts of Ashoka on the Delhi-Topra pillar: the seven Pillar Edicts",
        "place": "Delhi-Topra pillar, Firoz Shah Kotla, Delhi (originally at Topra, Haryana)",
        "object": "pillar",
        "script": "Brahmi",
        "ref_kind": "Pillar Edict",
        "ref_names": {"VII-east": "Pillar Edict VII (east face)", "VII-round": "Pillar Edict VII (round the pillar)"},
        "date_approx": "c. 243-242 BCE (edicts dated 26 and 27 years after Ashoka's consecration)",
        "manuscript": "Delhi-Topra pillar, Firoz Shah Kotla, Delhi (brought from Topra, Haryana, by Firoz Shah Tughluq): the seven "
                      "Pillar Edicts of Ashoka in Brahmi script, c. 243-242 BCE; impressions taken for the Archaeological Survey of "
                      "India and reproduced in Hultzsch 1925",
        "desc": "The seven Pillar Edicts of Ashoka on the Delhi-Topra pillar (c. 243-242 BCE), the only pillar with all seven, "
                "including the long seventh edict on the Dharma-mahamatras and the religious communities: Hultzsch's transliteration "
                "and 1925 English, each edict with the impression of the face that carries it.",
        "themes": ["pillar-edicts", "delhi"],
        "sections": {
            "I": (("topra-north", 640, 470, 2120, 1800), "the upper part of the north face, from the numeral I in the left margin to line 10 (numbered 2 to 10): 10 lines"),
            "II": (("topra-north", 640, 1600, 2120, 2590), "lines 10-16 of the north face. The edict begins in the second half of line 10, after the last words of edict I; Hultzsch sets the numeral II in the margin at line 11. The crop ends with line 16, above the numeral III"),
            "III": (("topra-north", 640, 2470, 2120, 3260), "the foot of the north face, from the numeral III in the left margin (line 17) to line 22: 6 lines"),
            "IV": (("topra-west", 780, 560, 2200, 3100), "the whole west face, from the numeral IV in the left margin (line 1) to line 20"),
            "V": (("topra-south", 600, 480, 2150, 3150), "the whole south face, from the numeral V in the left margin (line 1) to line 20; the pale patch at lines 7-8 is a flaw of the impression, where Hultzsch's text has dots"),
            "VI": (("topra-east", 750, 470, 2200, 1810), "the upper part of the east face, from the numeral VI in the left margin (line 1) to line 10"),
            "VII-east": (("topra-east", 750, 1720, 2200, 3240), "the lower part of the east face, from the numeral VII in the left margin (line 11) to line 21"),
            "VII-round": (("topra-circular", 120, 850, 5850, 2450), "the band that runs round the whole shaft below the four faces, lines 22-32 (numbered 22 to 32 in both margins); line 32 is short and ends near the middle of the impression"),
        },
    },
    {
        "slug": "rummindei",
        "proof": "rummindei.txt",
        "title": "Ashoka's Rummindei (Lumbini) pillar inscription: the birthplace of the Buddha",
        "place": "Rummindei (Lumbini), Nepal",
        "object": "pillar",
        "script": "Brahmi",
        "ref_names": {"Rummindei": "Rummindei pillar inscription"},
        "date_approx": "c. 249 BCE (20 years after Ashoka's consecration)",
        "manuscript": "Ashoka pillar at Rummindei (Lumbini), Rupandehi district, Nepal, beside the Maya Devi temple: five-line "
                      "Brahmi inscription, c. 249 BCE, uncovered in 1896",
        "desc": "Ashoka's five-line inscription on the pillar at Lumbini (c. 249 BCE), recording his visit to the birthplace of the "
                "Buddha Sakyamuni: Hultzsch's transliteration and 1925 English, with a photograph of the inscription on the pillar "
                "and an inked impression.",
        "themes": ["lumbini", "buddha", "birthplace", "minor-pillar-inscriptions"],
        "mapping": ("The inscription has five lines (Hultzsch's line numbers). On the photograph the five lines were counted and "
                    "their first and last signs read in Brahmi against the transcription; on the plate the line numbers 2 and 4 "
                    "are printed in the margins."),
        "photos": {
            "Rummindei": ("lumbini", (0, 150, 3217, 3000), "the five lines of the inscription. Checked on the photograph: "
                          "line 1 begins with de-vā-na-pi-ye-na and ends with -bhi-si-te-na; line 2 ends sa-kya-mu-nī ti; "
                          "line 4 ends u-ba-li-ke ka-ṭe; the short line 5 (a-ṭha-bhā-gi-ye cha) stands alone at the foot. "
                          "The image joins two photographs: the seam runs above line 5"),
        },
        "sections": {
            "Rummindei": (("rummindei", 480, 380, 2420, 1760), "the upper figure of the plate (headed Rummindei pillar-inscription), with the line numbers 2 and 4 in both margins: 5 lines, the last one short"),
        },
    },
    {
        "slug": "nigali-sagar",
        "proof": "nigali-sagar.txt",
        "title": "Ashoka's Nigali Sagar pillar inscription: the stupa of the Buddha Konakamana",
        "place": "Nigali Sagar (Nigliva), Nepal",
        "object": "pillar",
        "script": "Brahmi",
        "ref_names": {"Nigali-Sagar": "Nigali Sagar pillar inscription"},
        "date_approx": "c. 254 BCE and c. 249 BCE (14 and [20] years after Ashoka's consecration)",
        "manuscript": "Lower fragment of the Ashoka pillar at Nigali Sagar near Nigliva, Kapilvastu district, Nepal (found 1895): "
                      "four-line Brahmi inscription; impression reproduced in Hultzsch 1925",
        "desc": "Ashoka's four-line inscription on the Nigali Sagar pillar in Nepal, recording that he enlarged the stupa of the "
                "Buddha Konakamana: Hultzsch's transliteration and 1925 English, with the inked impression of the stone.",
        "themes": ["konakamana", "stupa", "buddha", "minor-pillar-inscriptions"],
        "sections": {
            "Nigali-Sagar": (("rummindei", 500, 2000, 2400, 3200), "the lower figure of the plate (headed Nigali Sagar pillar-inscription), with the line numbers 2 and 4 in the margins: 4 lines, the beginnings of lines 3 and 4 broken away at the left"),
        },
    },
    {
        "slug": "calcutta-bairat",
        "proof": "calcutta-bairat.txt",
        "title": "Ashoka's Calcutta-Bairat (Bhabru) inscription: the edict that names Buddhist texts",
        "place": "Calcutta-Bairat boulder, Asiatic Society, Kolkata (found near Bairat, Rajasthan)",
        "object": "boulder",
        "script": "Brahmi",
        "ref_names": {"Calcutta-Bairat": "Calcutta-Bairat rock inscription"},
        "date_approx": "c. 260-232 BCE (undated; reign of Ashoka)",
        "manuscript": "Calcutta-Bairat (Bhabru) inscription, granite block found in 1840 near Bairat (Rajasthan), Asiatic Society, "
                      "Kolkata: eight-line Brahmi inscription of Ashoka; impression reproduced in Hultzsch 1925",
        "desc": "Ashoka's letter to the Buddhist Sangha on the Calcutta-Bairat stone, the only edict that names Buddhist scriptures: "
                "Hultzsch's transliteration and 1925 English, with the inked impression of the stone.",
        "themes": ["sangha", "buddhist-scripture", "minor-rock-inscriptions"],
        "rotate": {"Calcutta-Bairat": -90},
        "sections": {
            "Calcutta-Bairat": (("calcutta-bairat", 850, 620, 2100, 3260), "the whole impression; Hultzsch prints it sideways, and the crop is turned a quarter turn clockwise so that the lines run across the image, line 1 at the top, with his line numbers 2, 4, 6, 8 now in the left and right margins: 8 lines"),
        },
    },
]

SECTION_REF_NAMES = {
    "XIII-east": "Rock Edict XIII (east face)", "XIII-south": "Rock Edict XIII (south face)",
    "elephant": "Label under the elephant (north face)",
}

EDICT_TOPICS = {
    "I": "ban on animal sacrifice and festival gatherings; the royal kitchen",
    "II": "medical care for men and animals; herbs, wells and trees",
    "III": "five-yearly tours of officials; duties of the dharma",
    "IV": "the sound of the drum becomes the sound of the dharma",
    "V": "appointment of the Dharma-mahamatras",
    "VI": "the king always available for public business",
    "VII": "all sects may live everywhere; self-control",
    "VIII": "tours of dharma replace pleasure tours; the visit to Sambodhi",
    "IX": "ceremonies of little fruit and the ceremony of dharma",
    "X": "the only glory the king seeks",
    "XI": "the gift of dharma",
    "XII": "honour for all sects; restraint of speech",
    "XIII": "the conquest of Kalinga and conquest by dharma",
    "XIV": "the edicts written in short, middle and full form",
}


# ---------------------------------------------------------------------------
def parse_proof(path):
    """Return ordered list of (name, pages, leaves, lines[(num, text)], english[paragraphs])."""
    out = []
    cur = None
    mode = None
    for ln in path.read_text(encoding="utf-8").split("\n"):
        if ln.startswith("#") or not ln.strip():
            continue
        if ln.startswith("@edict"):
            parts = [p.strip() for p in ln[len("@edict"):].split("|")]
            cur = {"name": parts[0], "pages": parts[1], "leaves": parts[2], "lines": [], "en": []}
            out.append(cur)
            mode = "orig"
            continue
        if ln.startswith("@en"):
            mode = "en"
            continue
        if ln.startswith("@end"):
            mode = None
            continue
        if mode == "orig":
            m = re.match(r"^(\d+) (.*)$", ln)
            assert m, (path.name, ln)
            cur["lines"].append((m.group(1), m.group(2).strip()))
        elif mode == "en":
            cur["en"].append(ln.strip())
    return out


def esc(t):
    # keep <em> tags written in the transcription; escape everything else
    t = html.escape(t, quote=False)
    return t.replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>")


def orig_html(lines):
    return "<br>".join(f"<sup>{n}</sup>{esc(t)}" for n, t in lines)


def en_html(paras):
    return "".join(f"<p>{esc(p)}</p>" for p in paras)


def save_crop(src, box, out, rotate=0, mode="L"):
    if out.exists() and not FORCE:
        return
    im = Image.open(src).convert(mode)
    c = im.crop(box)
    if rotate:
        c = c.rotate(rotate, expand=True)
    s = min(1.0, 2600 / max(c.size))
    if s < 1:
        c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    c.save(out, quality=86)


def scan_file(site, sec):
    s = sec.lower().replace(" ", "-")
    return f"{KEY}/{site}-{s}.jpg"


def plate_desc(pk):
    leaf, cap, facing = PLATES[pk]
    return f"Hultzsch 1925, plate '{cap}' ({facing}; archive.org leaf {leaf})"


def section_ref(name, site=None):
    if name in SECTION_REF_NAMES:
        return SECTION_REF_NAMES[name]
    if site and site.get("ref_names", {}).get(name):
        return site["ref_names"][name]
    kind = (site or {}).get("ref_kind", "Rock Edict")
    return f"{kind} {name}"


def short_place(site):
    return site["place"].split(",")[0]


# ---------------------------------------------------------------------------
def intro_for(site, eds):
    slug = site["slug"]
    if slug == "girnar":
        body = (
            "<p>The Girnar rock stands at the foot of Mount Girnar, east of Junagadh in Gujarat. Its north-eastern face carries "
            "the fourteen Major Rock Edicts of the Maurya king Ashoka, who calls himself Devanampriya Priyadarsin "
            "('Beloved of the Gods', 'of gracious appearance'). They were cut in Brahmi script in the middle of the third century BCE: "
            "edicts III and IV say they were written twelve years after his consecration, and edict V refers to the thirteenth year. "
            "Girnar has the western version of the series. Its dialect keeps r where the eastern versions at Kalsi, Dhauli and "
            "Jaugada have l (<em>rājā</em> against <em>lājā</em>), and keeps some groups of consonants that they simplify "
            "(<em>prāṇa</em> against <em>pāna</em>).</p>"
            "<p>The edicts are laid out in two columns of ruled bands (I-V on the left, VI-XII on the right) with XIII and XIV below. "
            "Much of the thirteenth edict, which tells of the conquest of Kalinga, was blasted away during road building in the "
            "nineteenth century; two pieces of it were later recovered. The fourteen sections of this entry follow the edicts in order. "
            "Two short fragments below the thirteenth edict, one naming 'the entirely white elephant', are not included here.</p>")
    elif slug == "kalsi":
        body = (
            "<p>The Kalsi rock stands near the meeting of the Yamuna and Tons rivers, west of Dehradun in Uttarakhand, and is now "
            "kept in a shelter of the Archaeological Survey of India. It carries the most complete Brahmi copy of the fourteen "
            "Major Rock Edicts of Ashoka (Devanampriya Priyadarsin), cut in the middle of the third century BCE. Edicts I to XII "
            "and the first part of XIII fill the east face (39 lines); the rest of XIII and the whole of XIV are on the south face "
            "(23 lines); the north face bears the outline of an elephant labelled <em>gajatame</em>, 'the best elephant'.</p>"
            "<p>The thirteenth edict is complete here except for the opening lines of the south face, and it is the fullest Brahmi "
            "account of the conquest of Kalinga, Ashoka's remorse, and his 'conquest by dharma' reaching the Greek kings "
            "Antiyoga (Antiochus II), Tulamaya (Ptolemy II), Antekina (Antigonus Gonatas), Maka (Magas of Cyrene) and "
            "Alikyashudala (Alexander of Epirus or of Corinth). From edict X onwards the writer uses the letters s, sh and ś "
            "interchangeably for one sound, and separates words with a short stroke (shown |), as Hultzsch prints them.</p>")
    elif slug == "dhauli":
        body = (
            "<p>The Dhauli rock stands on a low hill south of Bhubaneswar in Odisha, the ancient Tosali, capital of the province of "
            "Kalinga that Ashoka conquered (Rock Edict XIII). Here, and at Jaugada, the series of Major Rock Edicts leaves out XI-XIII, "
            "the edict of the Kalinga war among them, and adds two Separate Edicts addressed to the king's officers in the conquered "
            "land. Above the inscription the rock is carved into the forepart of an elephant.</p>"
            "<p>The First Separate Edict is addressed to the <em>Mahāmātras</em> of Tosali who are judicial officers of the city: "
            "'All men are my children'; they must judge impartially, avoid anger and haste, and not let anyone be imprisoned or "
            "harshly treated without cause; inspectors will come every five years from the capital, and every three years from Ujjayini "
            "and Taxila. The Second Separate Edict, to the prince and the <em>Mahāmātras</em> of Tosali, concerns the unconquered peoples "
            "on the border: they should not fear the king, who wishes them only happiness and will forgive what can be forgiven. "
            "Both edicts are to be read out on the days of the Tishya constellation. This entry gives these two edicts; Dhauli's "
            "version of the Major Rock Edicts I-X and XIV is not yet included. The rock is weathered and many letters are "
            "uncertain or lost; Hultzsch marks them with brackets and dots.</p>")
    elif slug == "delhi-topra":
        body = (
            "<p>The Delhi-Topra pillar is a polished sandstone column that Ashoka set up at Topra (Haryana); the sultan Firoz Shah "
            "Tughluq (r. 1351-1388) had it brought to Delhi and raised on the roof of his palace citadel, the Firoz Shah Kotla. It is the only pillar that "
            "carries all seven Pillar Edicts. Edicts I-VI repeat the text found on the other Ashokan pillars; the seventh, the "
            "latest of Ashoka's dated edicts, is found only here. Edicts I, IV, V and VI are dated 26 years after his "
            "consecration and VII 27 years after it (c. 243-242 BCE).</p>"
            "<p>The edicts run round the four faces of the shaft: I-III on the north face, IV on the west, V on the south, and VI "
            "with the first part of VII on the east face; the rest of VII is a single band of eleven long lines running round the "
            "whole pillar below them. The pillar edicts speak of the king's officers, the <em>Lajūkas</em>, of the protection of "
            "animals, of mercy to prisoners condemned to death, and of the <em>Dharma-mahāmātras</em> sent to the Buddhist "
            "<em>Saṁgha</em>, the Brahmins, the Ājīvikas and the Jains (Nirgranthas). The whole text survives; small breaks are "
            "marked with dots and brackets.</p>")
    elif slug == "rummindei":
        body = (
            "<p>The Rummindei pillar stands at Lumbini in the Nepal Terai, beside the Maya Devi temple. Its inscription, five lines "
            "of Brahmi cut high on the polished shaft, records that Ashoka came in person to worship here twenty years after his "
            "consecration (c. 249 BCE) 'because the Buddha Śākyamuni was born here', set up a stone and the pillar, and reduced the "
            "village's tax. The pillar was uncovered in 1896, and the inscription fixed the site of the Buddha's birth, named "
            "Lumbini (Lummini) in Buddhist tradition. The inscription is complete.</p>"
            "<p>The section shows two images: a recent colour photograph of the inscription on the pillar, and Hultzsch's plate of "
            "an inked impression.</p>")
    elif slug == "nigali-sagar":
        body = (
            "<p>The Nigali Sagar (Nigliva) pillar lies in the Nepal Terai about thirteen miles (21 km) north-west of Lumbini; it is not "
            "in its original place, and only two pieces of its shaft survive. Its inscription records that Ashoka enlarged to double its size the stupa of the Buddha Konakamana "
            "(Kanakamuni, one of the Buddhas held to have preceded Gautama) fourteen years after his consecration, and later came "
            "to worship there. It is the oldest datable witness to the belief in earlier Buddhas. The beginnings of lines 3 and 4 "
            "are broken away; Hultzsch's English supplies the lost words in square brackets from the Rummindei inscription.</p>")
    elif slug == "calcutta-bairat":
        body = (
            "<p>The Calcutta-Bairat inscription (also called the Bhabru edict) is on a granite block found in 1840 by Captain Burt on a "
            "hill near Bairat in Rajasthan and taken to the Asiatic Society of Bengal in Calcutta. It is a letter from 'the Magadha king Priyadarśin' to the "
            "Buddhist <em>Saṁgha</em>: he declares his reverence for the Buddha, the Dharma and the Saṁgha, and names seven "
            "passages of scripture that he wishes monks, nuns and lay followers to hear and reflect on. It is the only Ashokan "
            "edict that names Buddhist texts, and the earliest list of Buddhist scripture. Several of the seven have been "
            "identified with suttas of the Pali canon (for example the Lāghulovāda with the Ambalaṭṭhika-Rāhulovāda Sutta, which "
            "speaks of lying). The eight lines are complete except for a few damaged letters.</p>")
    else:
        body = ""
    obj = site.get("object", "rock")
    common = (
        f"<p><strong>Sources.</strong> Original text and English: {html.escape(HULTZSCH)}, transcribed from the page images of "
        f"the archive.org scan (public domain). Images: Hultzsch's collotype plates of inked impressions (estampages) of the "
        f"{html.escape(short_place(site))} {obj}, taken on the stone for the Archaeological Survey of India. An impression is a contact copy pressed on paper from the "
        "inscribed surface itself, not a drawing; each section's image is the part of the plate that carries that text, "
        "with the plate's own numerals and line numbers in the margins.</p>"
        "<p><strong>Reading the text.</strong> Line numbers are Hultzsch's lines on the stone. Letters in square brackets are "
        "damaged or uncertain on the stone; dots mark lost letters. The capital letters in brackets, (A), (B) ..., are "
        "Hultzsch's sentence divisions and are the same in the transliteration and the English. Hultzsch's footnotes, which "
        "record other scholars' readings and his corrections, are not reproduced.</p>")
    return body + common


# ---------------------------------------------------------------------------
def build():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for pk, (leaf, cap, facing) in PLATES.items():
        fetch_leaf(leaf)
    for k, ph in PHOTOS.items():
        if not ph["path"].exists():
            ph["path"].parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["curl", "-sL", "-m", "600", "-A", UA, "-o", str(ph["path"]), ph["url"]], check=True)

    common_verif = {
        "scan_source": f"Collotype plates of inked impressions in {HULTZSCH}; archive.org scan {IA_PAGE} "
                       "(digitized by Artur Karp, University of Warsaw), page images fetched at full resolution from the "
                       "archive.org BookReader image service",
        "scan_license": "Public Domain Mark 1.0 (archive.org item); plates published 1925, public domain",
        "original_text_source": f"Hultzsch's transliteration in {HULTZSCH}, transcribed from the page images of {IA_PAGE} "
                                "(the archive.org OCR used as a starting point and corrected line by line on the images)",
        "original_text_license": "public domain (published 1925; E. Hultzsch died 1927)",
        "translation_source": f"Hultzsch's English translation in {HULTZSCH}, read from the page images of {IA_PAGE}",
        "translation_license": "public domain (published 1925; E. Hultzsch died 1927)",
        "translator": "E. Hultzsch (1925)",
        "verified_date": TODAY,
    }

    rows = []
    for order, site in enumerate(SITES, 1):
        eds = parse_proof(PROOF / site["proof"])
        sections = []
        local = []
        plate_keys = []
        place = short_place(site)
        obj = site.get("object", "rock")
        for ed in eds:
            name = ed["name"]
            if name not in site["sections"]:
                raise SystemExit(f"{site['slug']}: no image config for section {name}")
            (pk, x0, y0, x1, y1), what = site["sections"][name]
            leaf = PLATES[pk][0]
            if pk not in plate_keys:
                plate_keys.append(pk)
            first, last = ed["lines"][0][0], ed["lines"][-1][0]
            lines_ref = f"line {first}" if first == last else f"lines {first}-{last}"
            pages, notes = [], []
            ph = site.get("photos", {}).get(name)
            if ph:
                pkey, box, pwhat = ph
                out_p = scan_file(site["slug"], name + "-photo")
                save_crop(PHOTOS[pkey]["path"], box, ROOT / "site" / "assets" / "scans" / out_p, mode="RGB")
                pages.append(out_p)
                notes.append(f"Photograph of the stone: {PHOTOS[pkey]['credit']}, cropped to {pwhat}.")
            out_rel = scan_file(site["slug"], name)
            save_crop(fetch_leaf(leaf), (x0, y0, x1, y1), ROOT / "site" / "assets" / "scans" / out_rel,
                      rotate=site.get("rotate", {}).get(name, 0))
            pages.append(out_rel)
            notes.append(f"Inked impression (estampage) of the {place} {obj}, not a photograph of the stone: "
                         f"{plate_desc(pk)}, cropped to {what}.")
            for p_ in pages:
                if p_ not in local:
                    local.append(p_)
            note = " ".join(notes) + (f" Checked on the image against the transcription ({lines_ref}). "
                                      f"Text and English: Hultzsch 1925, {ed['pages']} (archive.org {ed['leaves']}).")
            sections.append({
                "section": name,
                "original_ref": f"{section_ref(name, site)}, {place}, {lines_ref} (Hultzsch 1925, {ed['pages']})",
                "original_text": orig_html(ed["lines"]),
                "text": en_html(ed["en"]),
                "scan_pages": pages,
                "scan_note": note,
            })
        tid = PREFIX + site["slug"]
        verif = dict(common_verif)
        photo_keys = [v[0] for v in site.get("photos", {}).values()]
        if photo_keys:
            verif["scan_source"] = (common_verif["scan_source"] + "; photograph: " +
                                    "; ".join(f"{PHOTOS[k]['credit']}, {PHOTOS[k]['page']}" for k in dict.fromkeys(photo_keys)))
            verif["scan_license"] = (common_verif["scan_license"] + "; photograph: " +
                                     "; ".join(PHOTOS[k]["license"] for k in dict.fromkeys(photo_keys)))
        verif["scan_manuscript"] = site["manuscript"]
        verif["scan_mapping"] = site.get("mapping", (
            "Edict to lines: Hultzsch's line numbers. Lines to image: the edict numerals and line numbers printed "
            "in the margins of Hultzsch's plates, checked on each crop by counting the lines of the band "
            "against the transcription."))
        verif["scan_mapping_urls"] = [leaf_view(PLATES[pk][0]) for pk in plate_keys] + \
            [PHOTOS[k]["page"] for k in dict.fromkeys(photo_keys)]
        verif["scan_local_paths"] = local
        intro = intro_for(site, eds)
        desc = site["desc"]
        entry = {
            "id": tid, "slug": tid, "title": site["title"],
            "language": "Ashokan Prakrit (Hultzsch transliteration) / English (Hultzsch 1925)",
            "source": (f"{site['place']}, {obj} inscription of Ashoka; Hultzsch's collotype plates of inked impressions (1925)"
                       + ("; photograph of the stone (Wikimedia Commons)" if photo_keys else "")
                       + "; Hultzsch's transliteration and English (CII I, 1925), read from the archive.org scan"),
            "description": desc,
            "introduction": intro,
            "translator_notes": [
                "Hultzsch translates dhamma as 'morality'; other translators use 'Dharma' or 'righteousness'.",
                "Words in round brackets in the English are Hultzsch's additions for sense; words in square brackets render damaged letters.",
            ],
            "translation": sections,
            "verification": verif,
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
        captions = []
        for sec in sections:
            for p_ in sec["scan_pages"]:
                kind = "photograph" if p_.endswith("-photo.jpg") else "inked impression, Hultzsch 1925"
                captions.append({"file": p_, "caption": f"{place}, {section_ref(sec['section'], site)} ({kind})"})
        rows.append({
            "id": tid, "slug": tid, "order": order, "title": site["title"], "author_id": "ashoka",
            "language": "Ashokan Prakrit", "era": "Axial Age", "tradition": "buddhist", "category": "inscription",
            "date_approx": site["date_approx"], "century": -3,
            "source": entry["source"], "description": desc,
            "themes": ["ashoka", "edicts-of-ashoka", "mauryan", "brahmi", "prakrit", "inscription", "dharma",
                       site["slug"]] + site.get("themes", []) + ["verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": captions},
        })

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Edicts of Ashoka", "group": "India", "date_sort": -250,
            "author_name": "Ashoka (Devanampriya Priyadarsin), Maurya king (r. c. 268-232 BCE)",
            "source_url": IA_PAGE,
            "critical_edition": "E. Hultzsch, Inscriptions of Asoka (CII I, 1925), transliteration read from the scan",
            "translator_name": "E. Hultzsch (1925)",
            "original_lang_label": "Ashokan Prakrit · Hultzsch transliteration",
            "original_lang_code": "pra",
            "edition_label": "",
            "search_terms": "ashoka asoka edicts rock edicts pillar edicts maurya brahmi prakrit dhamma dharma kalinga "
                            "girnar kalsi devanampiya piyadasi buddhist inscriptions",
            "description": ("The edicts of the Maurya king Ashoka (c. 260-232 BCE), the earliest datable writing in India, "
                            "rock by rock: E. Hultzsch's 1925 transliteration and English, each edict shown on the inked "
                            "impression of the stone that carries it."),
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} entries, {sum(len(parse_proof(PROOF / s['proof'])) for s in SITES)} sections")


if __name__ == "__main__":
    build()
