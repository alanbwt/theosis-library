#!/usr/bin/env python3
"""
import_rosetta_stone.py -- the Rosetta Stone (British Museum EA 24): the Greek text of the
decree of the priests at Memphis for Ptolemy V (196 BCE), all 54 lines, in nine groups of
six lines, each placed on the photograph of the stone.

Collection key: rosetta-stone   (entry verified-rosetta-stone-greek-decree)

Chain of evidence
-----------------
1. OBJECT   British Museum EA 24, granodiorite stela, found at Rashid (Rosetta) in 1799;
            decree of 27 March 196 BCE (4 Xandikos = 18 Mecheir, year 9 of Ptolemy V).
            Hieroglyphic (14 lines, top broken), Demotic (32 lines) and Greek (54 lines).
2. SCANS    (a) The British Museum's own photograph published in E. A. W. Budge, The
            Rosetta Stone (British Museum, 1922), photograph by Donald Macbeth, on
            Wikimedia Commons as File:The_Rosetta_Stone.jpg (4911 x 6000 px), public
            domain. The Greek lines are sharp enough on it to be read letter by letter.
            The importer turns it by -0.4 degrees so that the Greek lines run level, cuts
            the Greek register, and makes one image per group of six lines. On this photograph
            the lines bow (they drop by up to 45 px towards the lower left), so each group
            image is straightened: every pixel column is shifted up or down by the mean
            offset of the group's lines at that column (at most 61 px; no other change), and
            the line is shown in two halves, the left half above the right half (the halves
            overlap by 300 px). The vertical position of every line was read by eye at the
            left edge (x 550), the middle (x 1700) and the right edge (x 3900; x 3075 for
            lines 46-54, whose right ends are broken away) on calibrated strips of the turned
            photograph (LINE_Y below). Every group image was then opened and checked:
            first and last letters of its first and last line (GROUP_CHECKS).
            (b) Overview: Hans Hillewaert, File:Rosetta_Stone.JPG, CC BY-SA 4.0.
3. ORIGINAL Greek text of E. A. Wallis Budge, The Decrees of Memphis and Canopus, vol. 2
            (London: Kegan Paul, 1904), pp. 101-123 ("Transcript"), which prints the Greek
            line by line with the stone's line numbers (Boeckh's CIG 4697 text with additions
            by Porson, Letronne and others). Typed from the page images of the Internet
            Archive copy (decreesofmemphis02budg, pages saved in data/sources/rosetta-stone/
            budge1904/) and proofread word by word against the printed page; then compared
            letter by letter with the FHG text of the open-greek-corpus (OCR, CC BY-SA 4.0),
            and every difference looked up again on Budge's page. Budge's misprints are kept
            (e.g. line 10 ὑπὰ, 16 ἐτάσσοντα, 18 ἀποκατέστηοεν, 19 καταπορευομένος, 29 ἀγδόου).
            Data file: data/sources/rosetta-stone/transcribed/budge1904_greek.txt.
4. ENGLISH  Budge's own "English Rendering" of the Greek in the same volume, pp. 100-122,
            numbered by the same stone lines; public domain (1904). Typed from the page
            images and checked word by word against the Internet Archive OCR of the same pages.
            Data file: data/sources/rosetta-stone/transcribed/budge1904_english.txt.

Usage:  python3 scripts/import_rosetta_stone.py           (build)
        python3 scripts/import_rosetta_stone.py --force   (rebuild images)
"""

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "rosetta-stone"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (https://theosislibrary.com; non-commercial research)"
COMMONS = "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/"
BM_PHOTO = "The_Rosetta_Stone.jpg"          # British Museum 1922, photo Donald Macbeth, PD
HILL_PHOTO = "Rosetta_Stone.JPG"             # Hans Hillewaert, CC BY-SA 4.0
ARCHIVE = "https://archive.org/details/decreesofmemphis02budg"

ROT = -0.4                                   # degrees, centre (2450, 4500), white fill
REGISTER = (100, 3480, 4850, 5660)           # Greek register on the turned photograph
HALVES = ((150, 2600), (2300, 4850))         # left half, right half (x ranges)

# Vertical position (y, on the turned photograph) of the middle of every Greek line, read by
# eye on calibrated strips at four x positions.
LINE_Y = {
    550: [3565, 3615, 3655, 3700, 3735, 3775, 3810, 3845, 3885, 3920, 3955, 3985, 4025, 4060, 4095, 4125, 4160, 4195,
          4230, 4270, 4315, 4350, 4395, 4435, 4485, 4520, 4560, 4600, 4645, 4672, 4702, 4740, 4780, 4815, 4850, 4900,
          4940, 4975, 5010, 5050, 5085, 5130, 5170, 5205, 5250, 5290, 5320, 5360, 5400, 5440, 5480, 5505, 5545, 5595],
    1700: [3575, 3618, 3658, 3698, 3738, 3775, 3812, 3848, 3880, 3915, 3950, 3985, 4022, 4058, 4095, 4130, 4165, 4202,
           4238, 4275, 4310, 4345, 4383, 4418, 4455, 4490, 4537, 4585, 4620, 4657, 4693, 4728, 4765, 4800, 4835, 4872,
           4908, 4945, 4980, 5015, 5052, 5088, 5125, 5160, 5195, 5232, 5268, 5303, 5340, 5378, 5415, 5450, 5490, 5528],
    3075: {46: 5240, 47: 5275, 48: 5305, 49: 5345, 50: 5380, 51: 5415, 52: 5460, 53: 5500, 54: 5550},
    3900: [3575, 3620, 3660, 3695, 3735, 3770, 3815, 3855, 3885, 3925, 3960, 3995, 4025, 4065, 4100, 4130, 4165, 4200,
           4230, 4265, 4300, 4330, 4370, 4415, 4460, 4500, 4535, 4570, 4605, 4640, 4675, 4710, 4755, 4790, 4830, 4870,
           4900, 4935, 4975, 5005, 5040, 5075, 5115, 5145, 5180, 5215, 5255, 5285, 5330, 5370],
}
GROUPS = [(1, 6), (7, 12), (13, 18), (19, 24), (25, 30), (31, 36), (37, 42), (43, 48), (49, 54)]

# What was read on each group image (left half: start of the line; right half: end of the line).
GROUP_CHECKS = {
    (1, 6): "line 1 begins ΒΑΣΙΛΕΥΟΝΤΟΣΤΟΥΝΕΟΥΚΑΙ and ends ΚΑΙΤΑΠΡΟΣΤΟΥΣ; line 6 begins ΤΗΣΠΤΟΛΕΜΑΙΟΥΜΗΝΟΣΞΑΝΔΙΚΟΥ and "
            "ends ΠΡΟΣΤΟΝΣΤΟΛΙΣΜΟΝΤΩΝ",
    (7, 12): "line 7 begins (Θ)ΕΩΝΚΑΙΠΤΕΡΟΦΟΡΑΙΚΑΙΙΕΡΟΓΡΑΜΜΑΤΕΙΣ and ends ΠΑΡΑΛΗΨΕΩΣΤΗΣ; line 12 begins "
             "ΤΑΙΣΤΕΕΑΥΤΟΥΔΥΝΑΜΕΣΙΝ and ends ΟΙΑΛΛΟΙΠΑΝΤΕΣΕΝ",
    (13, 18): "line 13 begins (ΕΥ)ΘΗΝΙΑΙΩΣΙΝΕΠΙΤΗΣΕΑΥΤΟΥ and ends ΤΟΥΣΕΝΤΑΙΣΦΥΛΑΚΑΙΣ; line 18 begins ΟΘΟΝΙΩΝΑΠΕΛΥΣΕΝ "
              "and ends ΤΟΙΣΘΕΟΙΣΚΑΤΑΤΟ",
    (19, 24): "line 19 begins ΠΡΟΣΗΚΟΝΟΜΟΙΩΣΔΕΚΑΙΤΟΔΙΚΑΙΟΝ and ends ΤΩΝΑΛΛΟΤΡΙΑ; line 24 begins ΤΙΚΑΘΙΣΑΣΧΩΜΑΣΙΝ and "
              "ends ΚΑΤΑΚΛΥΖΕΙΝΤΑ",
    (25, 30): "line 25 begins ΠΕΔΙΑΚΑΤΕΣΧΕΝΕΚΠΟΛΛΩΝΤΟΠΩΝ and ends ΠΡΟΣΤΗΙΦΥΛΑΚΗΙ; line 30 begins "
              "ΩΝΚΑΙΤΩΝΣΥΝΤΕΤΕΛΕΣΜΕΝΩΝ and ends ΤΗΣΑΜΠΕΛΙΤΙΔΟΣΟΜΟΙ",
    (31, 36): "line 31 begins ΤΟΚΕΡΑΜΙΟΝΤΗΙΑΡΟΥΡΑΙ and ends ΥΠΕΡΤΩΝΑΝΗΚΟ; line 36 begins ΤΗΣΒΑΣΙΛΕΙΑΣΔΙΑΜΕΝΟΥΣΗΣ and "
              "ends ΤΑΥΠΑΡΧΟΝΤΑ, with ΑΓΑΘΗΙΤΥΧΗΙΕΔΟΞΕΝ in the middle",
    (37, 42): "line 37 begins ΤΩΙΑΙΩΝΟΒΙΩΙΒΑΣΙΛΕΙ and ends ΘΕΩΝΕΥΕΡΓ; line 42 begins ΙΕΡΩΝΚΑΙΚΑΘΙΔΡΥΣΑΙ and ends "
              "ΤΟΥΘΕΟΥΕΠΙΦΑΝΟΥΣΕ at the break",
    (43, 48): "line 43 begins ΞΟΔΕΥΕΙΝ and ends ΑΣΠΙ at the break; line 48 begins ΓΥΠΤΟΝΙΕΡΟΙΣΚΑΤΑΜΗΝΑ and ends "
              "ΤΑΣΤΕΓΙΝΟΜΕΝΑΣΠΡΟΘ at the break",
    (49, 54): "line 49 begins ΡΕΧΟΜΕΝΟΙΣΕΝΤΟΙΣΙΕΡΟΙΣ and ends ΚΑΤΕΝΙ at the break; line 54 begins ΤΕΡΕΟΥΛΙΘΟΥΤΟΙΣΤΕΙΕΡΟΙΣ "
              "and ends ΤΕΠΡΩΤΩΝΚΑΙΔΕΥΤΕΡΩ at the break",
}
TITLES = {
    (1, 6): "Date and protocol: titles of Ptolemy V, the eponymous priests, the date",
    (7, 12): "The synod at Memphis; the king's benefactions begin",
    (13, 18): "Remission of debts, prisoners released, temple revenues kept",
    (19, 24): "Justice, return of rebels, defence of Egypt, the siege of Lykopolis",
    (25, 30): "Capture of Lykopolis, punishment of the rebels, remission of temple dues",
    (31, 36): "Gifts to Apis and Mnevis, temples restored; the resolution begins",
    (37, 42): "Statues and golden shrines of the king in every temple",
    (43, 48): "The crowns on the shrine; the king's festival days",
    (49, 54): "The yearly festival, the priests' new title, the stelae in three scripts",
}


# --------------------------------------------------------------------------
def fetch(url, dest):
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = subprocess.run(["curl", "-sL", "-m", "300", "-A", UA, url], capture_output=True, check=True).stdout
    assert data[:3] == b"\xff\xd8\xff", url
    dest.write_bytes(data)
    return dest


def read_lines(name):
    out = {}
    for line in (SRC / "transcribed" / name).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        n, text = line.split("|", 1)
        out[int(n)] = text.strip()
    assert sorted(out) == list(range(1, 55)), name
    return out


def line_y(n, xs):
    pts = []
    for x, v in sorted(LINE_Y.items()):
        if isinstance(v, dict):
            if n in v:
                pts.append((x, v[n]))
        elif n <= len(v):
            pts.append((x, v[n - 1]))
    return np.interp(xs, [p[0] for p in pts], [p[1] for p in pts])


def build_images(force):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    bm = fetch(COMMONS + BM_PHOTO, SRC / "photos" / "The_Rosetta_Stone_PD.jpg")
    hill = fetch(COMMONS + HILL_PHOTO, SRC / "photos" / "Rosetta_Stone_Hillewaert.jpg")
    files = {"overview": SCAN_DIR / "rosetta-stone-hillewaert.jpg", "register": SCAN_DIR / "greek-register.jpg"}
    files.update({g: SCAN_DIR / f"greek-lines-{g[0]:02d}-{g[1]:02d}.jpg" for g in GROUPS})
    if all(p.exists() for p in files.values()) and not force:
        return files
    im = Image.open(hill).convert("RGB")
    im.thumbnail((2600, 2600), Image.LANCZOS)
    im.save(files["overview"], "JPEG", quality=86, optimize=True)

    rot = Image.open(bm).convert("RGB").rotate(ROT, resample=Image.BICUBIC, center=(2450, 4500), fillcolor=(255, 255, 255))
    reg = rot.crop(REGISTER)
    reg.thumbnail((2600, 2600), Image.LANCZOS)
    reg.save(files["register"], "JPEG", quality=88, optimize=True)

    img = np.asarray(rot)
    H, W, _ = img.shape
    X = np.arange(W)
    for a, b in GROUPS:
        off = np.mean(np.stack([line_y(n, X) - line_y(n, 1700) for n in range(a, b + 1)]), axis=0)
        ya, yb = line_y(a, 1700), line_y(b, 1700)
        top, h = int(ya - 28), int(yb - ya + 62)
        strip = np.full((h, W, 3), 255, np.uint8)
        for x in range(W):
            s = int(round(top + off[x]))
            lo, hi = max(0, s), min(H, s + h)
            if hi > lo:
                strip[lo - s:hi - s, x] = img[lo:hi, x]
        st = Image.fromarray(strip)
        (l0, l1), (r0, r1) = HALVES
        left, right = st.crop((l0, 0, l1, h)), st.crop((r0, 0, r1, h))
        comp = Image.new("RGB", (max(left.width, right.width), 2 * h + 12), (255, 255, 255))
        comp.paste(left, (0, 0))
        comp.paste(right, (0, h + 12))
        comp.save(files[(a, b)], "JPEG", quality=88, optimize=True)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    greek = read_lines("budge1904_greek.txt")
    english = read_lines("budge1904_english.txt")
    files = build_images(args.force)
    rel = {k: f"{KEY}/{p.name}" for k, p in files.items()}

    secs = []
    for a, b in GROUPS:
        g = "<br>".join(f"<sup>{n}</sup>{greek[n]}" for n in range(a, b + 1))
        e = "<br>".join(f"<sup>{n}</sup>{english[n]}" for n in range(a, b + 1))
        secs.append({
            "section": f"{a}-{b}",
            "original_ref": f"Rosetta Stone, Greek text, lines {a}-{b} (OGIS 90; Budge 1904, vol. 2)",
            "original_text": g,
            "text": e,
            "scan_pages": [rel[(a, b)], rel["register"]],
            "scan_note": (f"Greek lines {a}-{b} of 54. The first image shows these six lines on the British Museum photograph of "
                          f"1922: the left half of each line above, the right half below (the halves overlap); the strip has been "
                          f"straightened by shifting pixel columns up or down, nothing else is changed. The second image is the "
                          f"whole Greek register on the same photograph, turned 0.4 degrees and not straightened. Line positions "
                          f"were read by eye at the left, middle and right of the register. Checked on the image: "
                          f"{GROUP_CHECKS[(a, b)]}. Square brackets in the Greek mark letters restored where the stone is broken "
                          f"(Budge's text); Budge's English also translates these restorations."),
        })

    eid = PREFIX + "greek-decree"
    intro = (
        "<p>The Rosetta Stone (British Museum EA 24) is a granodiorite stela found in 1799 at Rashid (Rosetta) in the western Nile "
        "Delta. It carries one decree in three scripts: Egyptian hieroglyphs at the top (14 surviving lines), Egyptian Demotic in "
        "the middle (32 lines) and Greek at the bottom (54 lines). The decree was passed by a synod of Egyptian priests at Memphis "
        "on 27 March 196 BCE (4 Xandikos, 18 Mecheir, year 9) to honour the young king Ptolemy V Epiphanes after his coronation. "
        "Because the Greek could be read, the stone gave the key to the decipherment of hieroglyphs (Thomas Young, Jean-Francois "
        "Champollion, 1814-1822).</p>\n\n"
        "<p>The Greek text lists the king's benefactions to the temples (tax remissions, release of prisoners, gifts to the sacred "
        "bulls Apis and Mnevis, the siege of rebel Lykopolis) and then the priests' resolutions: statues and golden shrines of the "
        "king in every temple, monthly and yearly festivals, a new priestly title, and the order to set up the decree on stelae "
        "of hard stone 'in holy, native and Greek letters', which is the stone itself.</p>\n\n"
        "<p>This entry gives the complete Greek text, all 54 lines, in nine sections of six lines. The Greek is the line-by-line "
        "transcript printed by E. A. Wallis Budge in The Decrees of Memphis and Canopus (1904), with the stone's line numbers; "
        "letters in square brackets are restorations where the right-hand and lower edges of the stone are broken. The English "
        "is Budge's own rendering of the Greek in the same book, numbered by the same lines; words in square brackets there are "
        "Budge's additions for sense. Each section is shown on the British Museum's 1922 photograph of the stone, cut and "
        "straightened to the six lines of that section, together with the whole Greek register. The hieroglyphic and Demotic "
        "versions are not given here because no openly licensed digital text of them was found.</p>"
    )
    entry = {
        "id": eid, "slug": eid,
        "title": "The Rosetta Stone: Greek text of the Memphis decree (complete, lines 1-54)",
        "language": "Greek / English",
        "source": "Rosetta Stone, British Museum EA 24 (British Museum photograph of 1922, public domain, via Wikimedia Commons) + "
                  "Greek transcript and English rendering of E. A. Wallis Budge, The Decrees of Memphis and Canopus, vol. 2 "
                  "(1904, public domain)",
        "description": "The complete Greek text of the Rosetta Stone (196 BCE), the priests' decree for Ptolemy V, line by line on "
                       "the photograph of the stone, with Budge's 1904 English.",
        "introduction": intro,
        "translator_notes": [
            "Budge's Greek is printed as in his book, including his misprints (line 10 ὑπὰ for ὑπὸ, 16 ἐτάσσοντα, 18 "
            "ἀποκατέστηοεν, 19 καταπορευομένος, 29 ἀγδόου, 52 ἀλλοῖς) and missing accents (8 παρελαβεν, 17 προσεταξεν).",
            "Budge prints each Greek line and its English with the same line number; a line of English can end in the middle "
            "of a phrase because the Greek line does.",
            "Budge's footnote markers and the quotation marks that open each of his printed lines are left out.",
            "Dotted lines (line 49) and gaps marked ....... (lines 48 and 51) are Budge's, where he gives no restoration.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": "Wikimedia Commons, File:The_Rosetta_Stone.jpg (British Museum photograph by Donald Macbeth, published in "
                           "E. A. W. Budge, The Rosetta Stone, British Museum 1922; https://archive.org/details/rosettastone00budgrich); "
                           "overview: File:Rosetta_Stone.JPG by Hans Hillewaert",
            "scan_license": "Public domain (photograph published 1922; marked public domain on Wikimedia Commons); overview "
                            "photograph CC BY-SA 4.0 (Hans Hillewaert)",
            "scan_manuscript": "London, British Museum EA 24, granodiorite stela from Rashid (Rosetta), decree of 196 BCE; Greek "
                               "register, 54 lines",
            "scan_mapping": "Line numbers of the Greek follow the stone (Budge prints them). The vertical position of every one of "
                            "the 54 lines was read by eye on calibrated strips of the photograph at the left edge, the middle and the "
                            "right edge of the register (lines 46-54 also near their broken right ends), and each six-line group "
                            "image was cut along those lines; every group image was opened and its first and last line checked "
                            "letter by letter (see scan notes).",
            "scan_mapping_urls": ["https://commons.wikimedia.org/wiki/File:The_Rosetta_Stone.jpg",
                                  "https://commons.wikimedia.org/wiki/File:Rosetta_Stone.JPG", ARCHIVE],
            "scan_local_paths": [rel["overview"], rel["register"]] + [rel[g] for g in GROUPS],
            "original_text_source": "E. A. Wallis Budge, The Decrees of Memphis and Canopus, vol. 2 (London: Kegan Paul, Trench, "
                                    "Trubner, 1904), pp. 101-123, 'The Greek Text of the Rosetta Stone: Transcript', typed from the "
                                    f"page images of {ARCHIVE} and proofread line by line against the printed pages",
            "original_text_license": "public domain (published 1904)",
            "translation_source": "E. A. Wallis Budge, The Decrees of Memphis and Canopus, vol. 2 (1904), pp. 100-122, 'English "
                                  f"Rendering', typed from the page images of {ARCHIVE}",
            "translation_license": "public domain (published 1904; Budge died 1934)",
            "translator": "E. A. Wallis Budge (1904)",
            "verified_date": TODAY,
        },
    }
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / f"{eid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {eid}: {len(secs)} sections")

    pages = [{"file": rel["overview"], "caption": "The Rosetta Stone, front (Hans Hillewaert, CC BY-SA 4.0)"},
             {"file": rel["register"], "caption": "Greek register, lines 1-54 (British Museum photograph, 1922)"}]
    pages += [{"file": rel[g], "caption": f"Greek lines {g[0]}-{g[1]}"} for g in GROUPS]
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Rosetta Stone (Greek text)", "group": "Egypt", "date_sort": -196,
            "author_name": "Synod of priests at Memphis (196 BCE)",
            "source_url": "https://www.britishmuseum.org/collection/object/Y_EA24",
            "critical_edition": "E. A. Wallis Budge, The Decrees of Memphis and Canopus (1904)",
            "translator_name": "E. A. Wallis Budge (1904)",
            "original_lang_label": "Greek · Budge 1904 transcript",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "rosetta stone memphis decree ptolemy v epiphanes eucharistos 196 bce greek demotic hieroglyphs "
                            "champollion decipherment ogis 90 apis lykopolis",
            "description": "The Rosetta Stone (British Museum EA 24, 196 BCE): the complete Greek text of the priests' decree for "
                           "Ptolemy V, 54 lines in groups of six, each cut from the British Museum's photograph of the stone, "
                           "with Budge's 1904 English.",
        },
        "texts": [{
            "id": eid, "slug": eid, "order": 1, "title": entry["title"], "author_id": "memphis-synod",
            "language": "Greek", "era": "Ancient Near East", "tradition": "egyptian", "category": "inscription",
            "date_approx": "27 March 196 BCE (year 9 of Ptolemy V)", "century": -2,
            "source": entry["source"], "description": entry["description"],
            "themes": ["rosetta-stone", "ptolemaic-egypt", "decree", "decipherment", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": pages},
        }],
        "authors": [{
            "id": "memphis-synod", "name": "Synod of Egyptian priests at Memphis", "dates": "196 BCE", "century": -2,
            "era": "Ancient Near East", "tradition": "egyptian", "language": "Egyptian / Greek",
            "bio": "The assembly of high priests, prophets and scribes from the temples of Egypt that met at Memphis for the "
                   "coronation of Ptolemy V and passed the decree copied on the Rosetta Stone.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
