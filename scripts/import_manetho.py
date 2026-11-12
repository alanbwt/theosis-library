#!/usr/bin/env python3
"""
import_manetho.py: Manetho of Sebennytus, Aegyptiaca (c. 280 BCE), as preserved by
Josephus and by George Syncellus. Builds the collection key `manetho`.

Chain of evidence
=================

A. Josephus, Against Apion 1.73-105 (Manetho on the Hyksos)
   SCAN     Florence, Biblioteca Medicea Laurenziana, Plut. 69.22 (10th c., parchment,
            37 fols., Contra Apionem only; the oldest Greek manuscript of the work),
            Teca Digitale IIIF manifest
            https://tecabml.contentdm.oclc.org/iiif/info/plutei/1350351/manifest.json
            (saved as data/sources/manetho/laur69.22-manifest.json).
   MAPPING  Read on the page images (fols. 6v-8v), line by line: 1.73 begins fol. 6v
            line 2 'ἄρξομαι δὴ πρῶτον ἀπὸ τῶν'; 1.105 ends fol. 8v line 17
            '...αὐτοῦ ψευδολογίαν.'; every Niese section start was located on the page
            (see SECTIONS_JOS below; line numbers count the written lines of the page).
   GREEK    B. Niese, Flavii Iosephi opera vol. 5 (1889), Perseus canonical-greekLit
            tlg0526.tlg003.perseus-grc2 (CC BY-SA 4.0).
   ENGLISH  W. Whiston (1737), Perseus tlg0526.tlg003.perseus-eng2 (from the 1856 Alden
            and Beardsley printing; CC BY-SA 4.0 digital text of a public-domain
            translation). Whiston's footnotes (<note>) are removed. Whiston prints the
            passage in three long paragraphs; it is divided here at the sentence that
            renders each Niese section. Five obvious digitization slips were corrected
            against a printed Whiston page (archive.org worksofflaviusjo00jose_0, 1860,
            pp. 635-636): see WHISTON_FIXES.

B. Syncellus (added below the Josephus block when built).

Usage:
    python3 scripts/import_manetho.py            # build (downloads missing scans)
    python3 scripts/import_manetho.py --force    # re-download scans
"""

import argparse
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "manetho"
PREFIX = f"verified-{KEY}-"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
SRC = ROOT / "data" / "sources" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
XMLB = "{http://www.w3.org/XML/1998/namespace}base"
UA = {"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        return r.read()


def save_jpeg(img, path, long_side=2200):
    img = img.convert("RGB")
    w, h = img.size
    s = long_side / max(w, h)
    if s < 1:
        img = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
    img.save(path, quality=85)
    return path


# ---------------------------------------------------------------------------
# A. Josephus, Against Apion 1.73-105 in Laur. Plut. 69.22
# ---------------------------------------------------------------------------

LAUR_MANIFEST = SRC / "laur69.22-manifest.json"
LAUR_VIEWER = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/1350351"


def laur_canvas(folio):
    d = json.loads(LAUR_MANIFEST.read_text(encoding="utf-8"))
    for c in d["sequences"][0]["canvases"]:
        if c["label"] == f"Carta: {folio}":
            return c["images"][0]["resource"]["service"]["@id"]
    raise KeyError(folio)


def laur_scan(folio, force=False):
    name = f"laur-plut69-22-f{int(folio[:-1]):02d}{folio[-1]}.jpg"
    path = SCAN_DIR / name
    if path.exists() and not force:
        return f"{KEY}/{name}"
    sid = laur_canvas(folio)
    img = Image.open(io.BytesIO(fetch(f"{sid}/full/full/0/default.jpg")))
    save_jpeg(img, path, long_side=2400)
    return f"{KEY}/{name}"


def text_without_notes(el):
    """itertext() that skips <note> elements but keeps the text that follows them."""
    if el.tag != f"{TEI}note":
        if el.text:
            yield el.text
        for ch in el:
            yield from text_without_notes(ch)
    if el.tail:
        yield el.tail


def perseus_sections(xml_path, book="1"):
    root = ET.parse(xml_path).getroot()
    out = {}
    for div in root.iter(f"{TEI}div"):
        if div.get("subtype") == "section" and div.get(XMLB, "").endswith(":" + book):
            t = "".join(text_without_notes(div))
            out[int(div.get("n"))] = re.sub(r"\s+", " ", t).strip()
    return out


# Digitization slips in the Perseus/Gutenberg Whiston e-text, corrected against the
# printed page (Whiston, Works, 1860 printing, archive.org worksofflaviusjo00jose_0,
# pp. 635-636). Each pair is (e-text, printed).
WHISTON_FIXES = [
    ("Tethtoosis the king of Egypt", "Tethmosis the king of Egypt"),
    ("four hundred and eighty thousand men to lie rotund about them",
     "four hundred and eighty thousand men to lie round about them"),
    ("as their most ancient king Manetho, therefore, hears this testimony",
     "as their most ancient king. Manetho, therefore, bears this testimony"),
    ("those things which Manetbo adds", "those things which Manetho adds"),
    ("in the most ancient ages and as they led", "in the most ancient ages; and as they led"),
]

# Whiston's English, cut at the sentence that renders each Niese section (73-105).
# Each value is the opening words of that section in Whiston.
WHISTON_STARTS = {
    73: "I shall begin with the writings of the Egyptians;",
    74: "Now this Manetho, in the second book of his Egyptian History,",
    75: "There was a king of ours whose name was Timaus.",
    76: "So when they had gotten those that governed us under their power,",
    77: "At length they made one of themselves king, whose name was Salatis;",
    78: "and as he found in the Saite Nomos,",
    79: "Thither Salatis came in summer time,",
    80: "after him reigned another, whose name was Beon,",
    81: "after all these reigned Assis forty-nine years and two months.",
    82: "This whole nation was styled HYCSOS,",
    83: "but some say that these people were Arabians.",
    84: "[But Manetho goes on]:",
    85: "After these, he says, That the kings of Thebais",
    86: "He says further, That under a king, whose name was Alisphragmuthosis,",
    87: "Manetho says, That the shepherds built a wall round all this place,",
    88: "but that Thummosis the son of Alisphragmuthosis",
    89: "and that, after this composition was made,",
    90: "but that as they were in fear of the Assyrians,",
    91: "Now Manetho, in another book of his, says,",
    92: "Nor was it without reason that they were called Captives",
    93: "But now I shall produce the Egyptians as witnesses",
    94: "and thus he speaks: When this people or shepherds",
    95: "after whom came Amenophis, for twenty years and seven months;",
    96: "after him was Thmosis, for nine years and eight months;",
    97: "then was Acencheres, for twelve years and five months;",
    98: "after him Amenophis, for nineteen years and six months;",
    99: "while he made an expedition against Cyprus,",
    100: "But after some considerable time, Armais,",
    101: "But then he who was set over the priests of Egypt",
    102: "The country also was called from his name Egypt;",
    103: "This is Manetho's account.",
    104: "Manetho, therefore, bears this testimony",
    105: "but then, as to those things which Manetho adds,",
}


def whiston_split():
    eng = perseus_sections(SRC / "tlg0526.tlg003.perseus-eng2.xml")
    text = " ".join(eng[n] for n in (73, 93, 103))
    text = re.sub(r"\s+", " ", text)
    for old, new in WHISTON_FIXES:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    # Whiston's ':' after 'thus he speaks' etc. are kept; cut points must each occur once.
    pos = {}
    for n, start in WHISTON_STARTS.items():
        assert text.count(start) == 1, (n, start, text.count(start))
        pos[n] = text.index(start)
    keys = sorted(pos)
    assert [pos[k] for k in keys] == sorted(pos.values()), "Whiston cut points out of order"
    out = {}
    for i, n in enumerate(keys):
        end = pos[keys[i + 1]] if i + 1 < len(keys) else len(text)
        out[n] = text[pos[n]:end].strip()
    assert out[73].startswith("I shall begin") and out[105].endswith("incredible fables.")
    return out


# Sections: (id, Niese sections, folios, scan_note)
SECTIONS_JOS = [
    ("1.73-78", range(73, 79), ["6v"],
     "Fol. 6v, lines 2-32 (31 full lines and a short closing line). Line 1 ends Against Apion 1.72. "
     "1.73 begins at line 2 'ἄρξομαι δὴ πρῶτον ἀπὸ τῶν'; 1.74 begins at the end of line 8 (the manuscript spells the name Μανεθών); "
     "the quotation from Manetho (1.75) begins at the end of line 11 'τοῦ Τίμαιος' / line 12 'ὄνομα'; from line 12 onward the quoted "
     "words are marked by strokes in the left margin. 1.76 begins line 15 'καὶ τοὺς', 1.77 line 20 'πέρας δὲ', 1.78 line 26 'εὑρὼν δὲ'. "
     "The page ends with 1.78 'ἀνδρῶν προφυλακήν' (line 32). In line 27 the manuscript reads 'ἐν νομῷ τῷ Σαΐτῃ' (the Saite nome), "
     "which Whiston translates; Niese prints the emendation Σεθροΐτῃ."),
    ("1.79-86", range(79, 87), ["7r"],
     "Fol. 7r, lines 1-31 (31 lines), all marked as quotation in the left margin. 1.79 begins line 1 'ἔνθα δὲ κατὰ θέρειαν'; "
     "1.80 line 4 'μετὰ τοῦτον δὲ ἕτερος'; 1.81 line 8 'ἐπὶ πᾶσι δὲ καὶ Ἄσσις'; 1.82 line 11 'ἐκαλεῖτο δὲ τὸ σύμπαν ἔθνος'; "
     "1.83 line 15 'τινὲς δὲ λέγουσιν'; 1.84 line 21 'τούτους τοὺς προκατωνομασμένους'; 1.85 line 24 'μετὰ ταῦτα δὲ'; "
     "1.86 line 27 'ἐπὶ δὲ βασιλέως'. Line 31 ends with the first words of 1.87 'τοῦτον φη-', which continues on fol. 7v."),
    ("1.87", [87], ["7r", "7v"],
     "1.87 straddles the page break: it begins at the end of fol. 7r line 31 'τοῦτον φη-' and continues on fol. 7v lines 1-3 "
     "'-σιν ὁ Μανεθὼν ἅπαντα τείχει τε μεγάλῳ ... καὶ τὴν λείαν τὴν ἑαυτῶν'."),
    ("1.88-93", range(88, 94), ["7v"],
     "Fol. 7v (31 lines of text). 1.88 begins at the end of line 3 'τὸν δὲ Μισφραγμουθώσεως'; 1.89 line 8 'τοὺς δὲ ἐπὶ ταῖς'; "
     "1.90 line 11 'φοβουμένους δὲ'; 1.91 line 15 'ἐν ἄλλῃ δέ τινι βίβλῳ'; 1.92 line 20 'αἰχμάλωτοί τε πάλιν'; "
     "1.93 line 26 'νυνὶ δὲ τῆς ἀρχαιότητος'. Josephus' own comments (lines 18-28) carry no quotation strokes in the margin. "
     "Three lines written below the text block, introduced 'ἐν ἑτέρῳ ἀντιγράφῳ' ('in another copy'), give a variant wording "
     "of 1.92 about Joseph sold by his brothers; they are not part of the printed text."),
    ("1.94", [94], ["7v", "8r"],
     "1.94 straddles the page break: it begins on fol. 7v line 29 'φησὶ δὲ οὕτως· μετὰ τὸ ἐξελθεῖν ἐξ Αἰγύπτου' and runs to the end of "
     "the page ('ἐβασίλευσε μετὰ ταῦτα ἔτη', line 31), then continues on fol. 8r lines 1-2 'εἴκοσι πέντε καὶ μῆνας τέσσαρας ... "
     "Χέβρων ἔτη δεκατρία'."),
    ("1.95-100", range(95, 101), ["8r"],
     "Fol. 8r (32 lines). 1.95 begins at the end of line 2 'μεθ’ ὃν' / line 3 'Ἀμένωφις'; 1.96 line 6 'τοῦ δὲ Θμῶσις'; "
     "1.97 line 10 'τοῦ δὲ Ἀκεγχήρης'; 1.98 line 14 'δὲ Ἀμένωφις'; 1.99 line 20 'αὐτὸς δὲ ἐπὶ Κύπρον'; 1.100 line 25 'χρόνου τε ἱκανοῦ'. "
     "The variant that Whiston gives in square brackets in 1.98 ('In another copy it stood thus...') is written in the right margin "
     "beside lines 5-17, beginning 'ἐν ἑτέρῳ ἀντιγράφῳ οὕτως· μεθ’ ὃν Σέθως καὶ Ῥαμέσσης δύο ἀδελφοί'."),
    ("1.101", [101], ["8r", "8v"],
     "1.101 straddles the page break: it begins at the end of fol. 8r line 30 'ὁ δὲ τε-' and fills lines 31-32 to "
     "'ὁ ἀδελφὸς αὐτοῦ Ἅρμαϊς'; the rest ('παραχρῆμα οὖν ὑπέστρεψεν εἰς Πηλούσιον ... τῆς ἰδίας βασιλείας') is fol. 8v lines 1-2."),
    ("1.102-105", range(102, 106), ["8v"],
     "Fol. 8v lines 2-17. 1.102 begins line 2 'ἡ δὲ χώρα ἐκλήθη'; Manetho's quotation ends line 4 'Δαναός' (margin strokes stop there); "
     "1.103 begins line 4 'ταῦτα μὲν ὁ Μανεθῶν'; 1.104 line 10 'δύο τοίνυν'; 1.105 line 14 'ὑπὲρ ὧν δ’ ὁ Μανεθών'; it ends line 17 "
     "'τὴν ἀπίθανον αὐτοῦ ψευδολογίαν'. Line 18 begins 1.106 'Βούλομαι τοίνυν' with an enlarged initial."),
]


def build_josephus(force):
    grc = perseus_sections(SRC / "tlg0526.tlg003.perseus-grc2.xml")
    eng = whiston_split()
    secs = []
    for sid, rng, folios, note in SECTIONS_JOS:
        rng = list(rng)
        pages = [laur_scan(f, force) for f in folios]
        secs.append({
            "section": sid,
            "original_ref": f"Josephus, Against Apion {sid}; Laur. Plut. 69.22, fol. {', '.join(folios)}",
            "original_text": " ".join(f"<sup>{n}</sup>{grc[n]}" for n in rng),
            "text": " ".join(f"<sup>{n}</sup>{eng[n]}" for n in rng),
            "scan_pages": pages,
            "scan_note": note + f" Viewer: {LAUR_VIEWER} . Greek shown is Niese's critical text; the copyist's spelling differs in small details.",
        })
    tid = PREFIX + "hyksos-josephus-apion-1-73-105"
    entry = {
        "id": tid, "slug": tid,
        "title": "Manetho on the Hyksos (Josephus, Against Apion 1.73-105)",
        "language": "Greek (Niese 1889) / English (Whiston 1737)",
        "source": "Laur. Plut. 69.22 (10th c.), fols. 6v-8v, via BML Teca Digitale IIIF + Niese Greek (Perseus) + Whiston English (Perseus)",
        "description": "Manetho's account of the Hyksos, the 'shepherd kings' who seized Egypt, and of the kings after their expulsion, "
                       "quoted word for word by Josephus in Against Apion 1.73-105 and shown on the five pages of the oldest manuscript.",
        "introduction": (
            "<p>Manetho, an Egyptian priest of Sebennytus, wrote a history of Egypt in Greek (the <em>Aegyptiaca</em>, in three books) "
            "under Ptolemy II, around 280 BCE. The work is lost. Its longest surviving passages of continuous narrative are the quotations "
            "made by the Jewish historian Flavius Josephus in his treatise <em>Against Apion</em> (written in the 90s AD).</p>\n\n"
            "<p>In 1.73-105 Josephus quotes Manetho's second book on an invasion of Egypt 'from the regions of the east' by people of "
            "obscure race, the Hyksos, a name Manetho explains as 'shepherd kings'. He names six of their rulers (Salitis, Bnon, Apachnan, "
            "Apophis, Iannas, Assis), their fortress of Avaris in the eastern Delta, their expulsion after 511 years, and their march through "
            "the desert to Syria, where, Manetho says, they built Jerusalem. Josephus then quotes Manetho's list of the kings who followed, "
            "down to Sethos (Sethosis), whom Manetho identifies with the Aegyptus of Greek legend, and his brother Harmais (Danaus). "
            "Josephus identifies the shepherds with the ancestors of the Jews; modern historians see in the passage a memory of the Hyksos "
            "rulers of the Fifteenth Dynasty (c. 1650-1550 BCE) and of the New Kingdom kings of the Eighteenth and Nineteenth Dynasties.</p>\n\n"
            "<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 69.22, a small parchment book of the 10th century (37 folios) "
            "that contains only <em>Against Apion</em>. It is the oldest Greek copy of the work. The passage runs from fol. 6v to fol. 8v. "
            "Each section below covers the Niese sections written on one page; three sections that run across a page break show both pages. "
            "Every section start was read on the page image and is recorded with its line number. The copyist marks Manetho's quoted words "
            "with strokes in the left margin, and two variant readings from 'another copy' are written in the margins of fols. 7v and 8r.</p>\n\n"
            "<p>The Greek is Niese's critical text, which follows this manuscript closely but not letter for letter. The English is William "
            "Whiston's translation (1737), which in a few places follows a different Greek text (for example 'thirteen years' for Salitis, "
            "where Niese prints nineteen).</p>"
        ),
        "translator_notes": [
            "Greek: Benedikt Niese, Flavii Iosephi opera vol. 5 (Berlin 1889), Perseus canonical-greekLit tlg0526.tlg003.perseus-grc2. "
            "At 1.75 the manuscript and Niese's text read 'τοῦ Τίμαιος ὄνομα', a corruption of the king's name (Tutimaeus), which Whiston renders 'Timaus'.",
            "English: William Whiston (1737), Perseus tlg0526.tlg003.perseus-eng2. Whiston's paragraphs were divided at the sentences that render each Niese "
            "section; his footnotes are omitted. Five digitization slips were corrected against the printed 1860 Whiston (archive.org "
            "worksofflaviusjo00jose_0, pp. 635-636): 'Tethtoosis' to 'Tethmosis', 'rotund' to 'round', 'king Manetho, therefore, hears' to "
            "'king. Manetho, therefore, bears', 'Manetbo' to 'Manetho', and a semicolon lost after 'ancient ages' (1.91).",
            "Whiston's square brackets ('[Sethroite,]', '[But Manetho goes on]', '[In another copy it stood thus ...]') are his own.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF manifest https://tecabml.contentdm.oclc.org/iiif/info/plutei/1350351/manifest.json), Plut. 69.22 fols. 6v, 7r, 7v, 8r, 8v; viewer {LAUR_VIEWER}",
            "scan_license": "Biblioteca Medicea Laurenziana, Florence, on concession of the Italian Ministry of Culture; access listed as 'Pubblico'; reproduced for non-commercial scholarly use with credit (any other use requires the library's permission)",
            "scan_manuscript": "Florence, BML, Plut. 69.22, parchment, 155 x 210 mm, 37 fols., 10th century, Josephus, Contra Apionem (ex San Marco, Niccolò Niccoli)",
            "scan_mapping": "Read on the page images: for each page the first and last lines and the start of every Niese section were located and recorded with line numbers in the section notes (1.73 begins fol. 6v line 2; 1.105 ends fol. 8v line 17)",
            "scan_mapping_urls": [LAUR_VIEWER, "https://pinakes.irht.cnrs.fr/notices/cote/16549/"],
            "scan_local_paths": sorted({p for s in secs for p in s["scan_pages"]}),
            "original_text_source": "Benedikt Niese, Flavii Iosephi opera vol. 5 (1889), Perseus canonical-greekLit tlg0526.tlg003.perseus-grc2, https://github.com/PerseusDL/canonical-greekLit/tree/master/data/tlg0526/tlg003",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": "William Whiston, The Works of Flavius Josephus (1737), Perseus tlg0526.tlg003.perseus-eng2 (Alden and Beardsley 1856 printing), checked against the 1860 printing at https://archive.org/details/worksofflaviusjo00jose_0",
            "translation_license": "public domain (published 1737); Perseus digital text CC BY-SA 4.0",
            "translator": "William Whiston (1737)",
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "title": entry["title"], "author_id": "manetho", "language": "Greek",
        "era": "Hellenistic", "tradition": "egyptian", "category": "history",
        "date_approx": "c. 280 BCE (Manetho); quoted by Josephus c. 95 AD; manuscript 10th c.", "century": -3,
        "source": entry["source"], "description": entry["description"],
        "themes": ["manetho", "hyksos", "egypt", "avaris", "josephus", "exodus", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p, "caption": "Laur. Plut. 69.22 fol. " + p.split("-f")[-1].replace(".jpg", "").lstrip("0")}
                            for p in entry["verification"]["scan_local_paths"]]},
    }
    return entry, row


# ---------------------------------------------------------------------------
# B. Manetho's king lists in George Syncellus (Paris gr. 1711 and Paris gr. 1764)
# ---------------------------------------------------------------------------

GALLICA_A = "btv1b10723005g"   # Paris gr. 1711 (A), 11th c., Syncellus on pp. 1-230
GALLICA_B = "btv1b10722002s"   # Paris gr. 1764 (B), 11th c., Syncellus, ed. reg. pp. 51-341, acephalous
GALLICA_IIIF = "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/{ark}/f{n}"
DFHG_FILE = SRC / "dfhg-manetho.json"
WADDELL_DIR = SRC / "lacuscurtius"
FHG_ARCHIVE = "https://archive.org/details/fragmentahistori02mueluoft"
WADDELL_URL = "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Manetho/home.html"
WADDELL_SCAN = "https://archive.org/details/manethowithengli00maneuoft"


def gutter(ark, n):
    """x position (fraction of width) of the binding gutter on a microfilm double-page image."""
    import numpy as np
    im = Image.open(io.BytesIO(fetch(GALLICA_IIIF.format(ark=ark, n=n) + "/full/1000,/0/default.jpg"))).convert("L")
    a = np.asarray(im).astype(float)
    h, w = a.shape
    band = a[int(h * 0.25):int(h * 0.75), int(w * 0.42):int(w * 0.58)]
    return (int(np.argmin(band.mean(axis=0))) + int(w * 0.42)) / w


def gallica_page(ark, n, side, name, force=False):
    """Crop one page (side 'L' or 'R') out of Gallica image f{n} and save it."""
    path = SCAN_DIR / name
    if path.exists() and not force:
        return f"{KEY}/{name}"
    g = gutter(ark, n)
    x0, x1 = (0.0, min(1.0, g + 0.01)) if side == "L" else (max(0.0, g - 0.01), 1.0)
    reg = f"pct:{x0 * 100:.2f},0,{(x1 - x0) * 100:.2f},100"
    img = Image.open(io.BytesIO(fetch(GALLICA_IIIF.format(ark=ark, n=n) + f"/{reg}/1700,/0/default.jpg")))
    save_jpeg(img, path, long_side=2400)
    return f"{KEY}/{name}"


def scan_B(folio, force=False):
    """Paris gr. 1764: fol. Nr is the right page of image N+4, fol. Nv the left page of image N+5."""
    num, side = int(folio[:-1]), folio[-1]
    n = num + 4 if side == "r" else num + 5
    return gallica_page(GALLICA_B, n, "R" if side == "r" else "L", f"paris-gr1764-f{num:02d}{side}.jpg", force)


def scan_A(page, force=False):
    """Paris gr. 1711 (paginated): page p is on image 14 + p//2 (even pages left, odd pages right)."""
    return gallica_page(GALLICA_A, 14 + page // 2, "L" if page % 2 == 0 else "R", f"paris-gr1711-p{page:03d}.jpg", force)


# Corrections to the DFHG digital text, each checked against the printed page of
# C. Müller, FHG II (1848), archive.org fragmentahistori02mueluoft (OCR slips, lost
# numeral signs such as stigma, koppa, sampi and the thousands mark). Keyed by the
# index of the record in data/sources/manetho/dfhg-manetho.json.
DFHG_FIXES = {
    1: [("παρὰ τούτοις, νεκύων", "παρὰ τούτοις νεκύων"), ("συνεκστῶτας", "συνεστῶτας"),
        ("κοσμικοῦ ασπβ'", "κοσμικοῦ ͵ασπβ'"), ("κασμικοῦ", "κοσμικοῦ"),
        ("σελήνια αʹ ͵απεʹ", "σελήνια αʹ ͵αϡπεʹ"), ("ἡλιακὰ πξθʹ", "ἡλιακὰ ϡξθʹ"),
        ("ἡλιακοῖς, ͵ανηʹ", "ἡλιακοῖς ͵ανηʹ"), ("ἐτῶν βκζʹ", "ἐτῶν ͵βκζʹ"),
        ("σὺν πξθʹ. ͵αρνγʹ", "σὺν ϡξθʹ. ͵αρνγʹ"), ("βασιλείας ανηʹ", "βασιλείας ͵ανηʹ"),
        ("συνάγειν ἔτη, ͵βσμβʹ", "συνάγειν ἔτη ͵βσμβʹ")],
    2: [("ἔτη αʹ ͵αππεʹ", "ἔτη αʹ ͵αϡπεʹ"), ("Ἥφαιστος ἔτη, ͵θ ἐβασίλευσε", "Ἥφαιστος ἔτη ͵θ ἐβασίλευσε"),
        ("Ταῦτα τὰ θ ἔτη", "Ταῦτα τὰ ͵θ ἔτη"), ("τῶν αὐτῶν, θ σεληνίων", "τῶν αὐτῶν ͵θ σεληνίων"),
        ("ἔτη ψκζʹ δʹ,", "ἔτη ψκζʹ ‿δʹ,"), ("ἡμέθεος", "ἡμίθεος"), ("ἕτη κʹ", "ἔτη κʹ")],
    9: [("ἀναγκαῖον ἡγησάμην δύο· τῶν", "ἀναγκαῖον ἡγησάμην δύο τῶν"), ("ἀντὶ, βσμβ' βσξβ'", "ἀντὶ ͵βσμβ' ͵βσξβ'"),
        ("Εὐσέβιος δὲ βσμβ'", "Εὐσέβιος δὲ ͵βσμβ'"), ("Καῖνᾶν", "Καϊνᾶν"), ("ἔτους γσβ'", "ἔτους ͵γσβ'"),
        ("ὑφελὼν, γρπδʹ", "ὑφελὼν, ͵γρπδʹ")],
    11: [("Θιωίτης", "Θινίτης"), ("ἐβασιλευσεν ἔτεσιν", "ἐβασίλευσεν ἔτεσιν"), ("παλλὰ παράσημα", "πολλὰ παράσημα")],
    14: [("Καίρης", "Χαίρης")],
    15: [("Χώος", "Χῶος"), ("γυναῖκας, βασιλείας", "γυναῖκας βασιλείας"), ("Οἲ καὶ", "Οἳ καὶ")],
    17: [("παρά λόγον", "παρὰ λόγον"), ("καὶ τὴν ξεστῶν", "καὶ τὴν διὰ ξεστῶν"),
         ("Σήφουρις (Σίφουρις Goar.).", "Σήφουρις (Σίφουρις Goar.) λʹ."), ("τῶν τρῶν", "τῶν τριῶν")],
    18: [("ἀπέστησααν", "ἀπέστησαν"), ("ἑαυτο`θς", "ἑαυτοὺς"), ("Σέσοράος", "Σέσορθος"), ("εὕρκτο", "εὕρατο"),
         ("ἀξιομνημόνευετον", "ἀξιομνημόνευτον"), ("ρ?ηʹ", "ρϟηʹ")],
    21: [("ἔγειρε πυραμίδα", "ἤγειρε πυραμίδα"),
         ("Ὁμοῦ τῶν δ' δυναστειῶν μετὰ τὸν κατακλυσμὸν ἔτη, αμςʹ", "Ὁμοῦ τῶν δ' δυναστειῶν τῶν μετὰ τὸν κατακλυσμὸν ἔτη ͵αμςʹ")],
    22: [("ἐγεί ρας", "ἐγείρας"), ("κατακλυσμὸν αρϟεʹ", "κατακλυσμὸν ͵αρϟεʹ")],
    25: [("Ῥαθούρης ἔτη θʹ", "Ῥαθούρης ἔτη μδʹ"), ("ἐτη λγʹ", "ἔτη λγʹ"), ("προτεταγμένοις, αμςʹ", "προτεταγμένοις ͵αμςʹ")],
    26: [("αρ(??)εʹ", "͵αρϟεʹ")],
    28: [("Όθόης", "Ὀθόης"), ("ασ?δʹ", "͵ασϟδʹ"), ("͵αυϟʹ", "͵αυϟζʹ")],
    29: [("Ἕχτη", "Ἕκτη"), ("ῆ καὶ λέγεται", "ἣ καὶ λέγεται"), ("ῷκοδομηκέναι", "ᾠκοδομηκέναι"),
         ("ασ?εʹ", "͵ασϟεʹ"), ("αυ?ηʹ", "͵αυϟηʹ")],
    33: [("πἐντε", "πέντε")],
    35: [("χζʹ", "κζʹ"), ("οἴ ἐβασίλευσαω", "οἳ ἐβασίλευσαν"), ("ἔτη, αχλθʹ", "ἔτη ͵αχλθʹ")],
    36: [("ἀφϟηʹ", "͵αφϟηʹ")],
    38: [("οἲ", "οἳ"), ("ὧν δ πρῶτος", "ὧν ὁ πρῶτος"), ("δειωότατος", "δεινότατος"), ("μαωίᾳ", "μανίᾳ")],
    39: [("αὺτοῦ", "αὐτοῦ"), ("ὔστερον", "ὕστερον")],
    41: [("οἲ", "οἳ"), ("ρκεʹ", "ρπεʹ")],
    42: [("οἲ", "οἳ")],
    44: [("οἲ", "οἳ"), ("Μἐχρι", "Μέχρι"), ("ἔτη, βτʹ", "ἔτη, ͵βτʹ")],
    48: [("Αωδεχάτη", "Δωδεκάτη"), ("ἔτη μζʹ", "ἔτη μςʹ"), ("δς ὑτὸ", "ὃς ὑπὸ"), ("ἔτη μή, δς ἅπασαν", "ἔτη μηʹ, ὃς ἅπασαν"),
         ("ὑτὸ Αἰγυπτίων", "ὑπὸ Αἰγυπτίων"), ("ἔτη ηʹ, δς τὸν", "ἔτη ηʹ, ὃς τὸν"), ("Σχεμίοφρις", "Σκεμίοφρις"),
         ("Θρᾷκης", "Θρᾴκης")],
    49: [("Διοσπολιτῶν λιτῶν", "Διοσπολιτῶν"), ("Ὧν πρῶτος", "Ὧν ὁ πρῶτος"), ("ληʹ, δς ὑπὸ", "ληʹ, ὃς ὑπὸ"),
         ("μηʹ, δς λέγεται", "μηʹ, ὃς λέγεται"), ("δακτύλων βʹ, Ὃς", "δακτύλων βʹ. Ὃς"), ("Θρᾲκης", "Θρᾴκης"),
         ("τῆς τῶν ἐπὶ δὲ τοῖς ἀγεννέσι", "τῆς τῶν ἐθνῶν κατασχέσεως, ἐπὶ μὲν τοῖς γενναίοις ἀνδρῶν, ἐπὶ δὲ τοῖς ἀγεννέσι"),
         ("Ἀρσενοἵτῃ", "Ἀρσενοΐτῃ"), ("οἵ πάντες", "οἳ πάντες"), ("σμέ.", "σμεʹ.")],
    52: [("οἲ", "οἳ"), ("ἔτη υνγʹ", "ἔτη υνγʹ.")],
    55: [("οἲ", "οἳ")],
    56: [("σςʹ, οἲ", "οςʹ, οἳ"), ("υ π δʹ", "υπδʹ")],
    59: [("οἲ καὶ Μέμφιν", "οἳ καὶ Μέμφιν"), ("οἲ καὶ ἐν", "οἳ καὶ ἐν"), ("ὰφ ̓ ἧς", "ἀφʼ ἧς"), ("ἀφ ̓ οὗ ὁ Σαΐτης", "ἀφʼ οὗ καὶ ὁ Σαΐτης")],
    60: [("οἲ", "οἳ")],
    63: [("δυναστείαν", "δυναστεία"), ("Βασιλεῖς", "βασιλεῖς"), ("οἲ καὶ εβασίλευσαν ἔτη ρ ϟʹ", "οἳ καὶ ἐβασίλευσαν ἔτη ρϟʹ")],
    66: [("δυναστείαν", "δυναστεία"), ("ᾖσαν", "ἦσαν"), ("Θοίνικες", "Φοίνικες"), ("οἲ καὶ Μέμφιν", "οἳ καὶ Μέμφιν"),
         ("ἀφʹ οὗ καὶ δ Σαΐτης", "ἀφʼ οὗ καὶ ὁ Σαΐτης"), ("οἲ καὶ ἐν", "οἳ καὶ ἐν"), ("Βʹ βνῶν", "βʹ Βνῶν"),
         ("Μεφ ̓ ὃν Ἄρχλησἔτη", "Μεθʼ ὃν Ἄρχλης ἔτη")],
    75: [("ὉμήρΠω", "Ὁμήρῳ"), ("δʹ Ῥαμεσσῆς ἔτη ξʹ. ςʹ Θούωρις", "δʹ Ῥαμεσσῆς ἔτη ξʹ. εʹ Ἀμμενεμνῆς ἔτη εʹ. ςʹ Θούωρις")],
    76: [("γʹ Ἀμμενεφοὴς ἔτη μʹ. δʹ Ἀμμενέμης ἔτη κςʹ. εʹ Θούωρις, ὁπαρ ̓ Ὁμήρῳ",
          "γʹ Ἀμμενεφθὴς ἔτη μʹ. δʹ Ἀμμενέμης ἔτη κςʹ. εʹ Θούωρις, ὁ παρʼ Ὁμήρῳ καλούμενος Πόλυβος, Ἀλκάνδρας ἀνὴρ, "
          "ἐφʼ οὗ τὸ Ἴλιον ἑάλω, ἔτη ζʹ. Ὁμοῦ ἔτη ρϟδʹ. Ἐπὶ τὸ αὐτὸ (τοῦ αὐτοῦ correx. m.) βʹ τόμου Μανεθῶ βασιλέων ϟβʹ "
          "ἔτη ͵αρκαʹ (scr. ͵βρκαʹ).")],
    78: [("ΚΑΤΑ ΛΦΡΙΚΑΝΟΝ", "ΚΑΤΑ ΑΦΡΙΚΑΝΟΝ"), ("οἲ", "οἳ"), ("ΚΑΤ ̓ ΕΥΣΒΙΟΝ", "ΚΑΤʼ ΕΥΣΕΒΙΟΝ"), ("ἔτη ροή.", "ἔτη ροηʹ.")],
    80: [("Ἀμενωρθίς", "Ἀμενωφθὶς"), ("έ Ὀσοκὼρ", "εʹ Ὀσοχὼρ"), ("Ψινακῆς", "Ψιναχῆς")],
    81: [("ἐπτὰ", "ἑπτά")],
    83: [("ἔτξ καʹ", "ἔτη καʹ"), ("γʹ δ ̓ εʹ", "γʹ δʹ εʹ"), ("ἔτη. μβʹ", "ἔτη μβʹ")],
    84: [("πριῶν", "τριῶν"), ("Σεώγχωσις", "Σεσώγχωσις")],
    86: [("ὂν Ἡρακλέα", "ὃν Ἡρακλέα"), ("Ψαμμοοῦς", "Ψαμμοῦς")],
    89: [("[ἔτη πϟʹ]", "[ἔτη ϡϟʹ]")],
    90: [("ἀρωίον", "ἀρνίον")],
    92: [("ὂς", "ὃς"), ("ἐλὼν", "ἑλὼν")],
    93: [("τέμπτη", "πέμπτη"), ("ὂς", "ὃς"), ("υἰὸς", "υἱὸς")],
    95: [("Σαῖτῶν", "Σαϊτῶν"), ("ἐννἐα", "ἐννέα"), ("Νεχαὼδεύτερος ἔτη δʹ Οὗτος", "Νεχαὼ δεύτερος ἔτη ςʹ. Οὗτος"),
         ("βασιλεα", "βασιλέα"), ("ἔτη ἔξ", "ἔτη ἕξ")],
    96: [("γʹ Νεχεψὼς ἔτη δʹ", "γʹ Νεχεψὼς ἔτη ςʹ"), ("δ ̓ Νεχαὼ", "δʹ Νεχαὼ"), ("Οὗτος εἷτος εἷλε", "Οὗτος εἷλε"),
         ("Ψάμμουθισ ἔτεροσ, ὁ καὶ ψαμμήτιχος", "Ψάμμουθις ἕτερος, ὁ καὶ Ψαμμήτιχος"), ("Οὔαφρισ", "Οὔαφρις")],
    98: [("βζσιλείας Περοῶν", "βασιλείας Περσῶν"), ("Αἰγύπτου ἔτη λς'", "Αἰγύπτου ἔτη ςʹ"), ("ὁ μέγασ", "ὁ μέγας"),
         ("Σογδιανὸς μῆνας ξʹ", "Σογδιανὸς μῆνας ζʹ")],
    99: [("Δαρεῖος ἔτη λ(??).", "Δαρεῖος ἔτη λςʹ."), ("ἔτει πέμπτῳ ἑαυτοῦ", "ἔτει πέμπτῳ τῆς ἑαυτοῦ")],
    101: [("Εἰκοστὴ ἀτὴ ὀγδόη", "Εἰκοστὴ ὀγδόη")],
    104: [("Ἔνάτη", "Ἐνάτη"), ("Ψάμμουθισ", "Ψάμμουθις"), ("Μεφερίτης", "Νεφερίτης")],
    105: [("δυν: στε α", "δυναστεία"), ("Μενσήσιοι", "Μενδήσιοι"), ("Ἄχωρισ", "Ἄχωρις"),
          ("γʹ Νεφερίτης (Ἀναφερίτης G.) μῆνας δʹ. εʹ Μοῦθις καʹ καὶ μῆνας δʹ.",
           "γʹ Ψάμμουθις ἔτος αʹ. δʹ Νεφερίτης (Ἀναφερίτης G.) μῆνας δʹ. εʹ Μοῦθις ἔτος αʹ. Ὁμοῦ ἔτη καʹ καὶ μῆνας δʹ.")],
    107: [("δυναστείαν", "δυναστεία")],
    108: [("Σιβεννυτῶν", "Σεβεννυτῶν"), ("αʹ Νεκτανέβης ἔτη ιηʹ", "αʹ Νεκτανέβης ἔτη ιʹ"), ("Νεκταωςεβὸς", "Νεκτανεβὸς")],
    110: [("τόμου ,ανʹ", "τόμου ͵ανʹ")],
    111: [("αρατεῖ τῆς Αἰγύπτου ἔτη ζʹ", "κρατεῖ τῆς Αἰγύπτου ἔτη ςʹ"), ("Μεθ ̓ δν Ἀρσῆς", "Μεθʼ ὃν Ἀρσῆς"),
          ("Μεθ ̓ δν Δαρεῖος", "Μεθʼ ὃν Δαρεῖος"), ("ἕξ· δν Ἀλέξανδρος", "ἕξ· ὃν Ἀλέξανδρος"), ("Mέχρι", "Μέχρι")],
    45: [("Ἀμμεμἐνης", "Ἀμμεμένης"), ("καταγήοχεν δ Μανεθῶ", "καταγήοχεν ὁ Μανεθῶ"), ("βασιλεἰς", "βασιλεῖς"),
         ("ἔτη, βτʹ", "ἔτη, ͵βτʹ")],
}

LATIN_OR_DIGIT = re.compile(r"[A-Za-z0-9]")


def strip_apparatus(t):
    """Remove Müller's inline apparatus: parentheses or square brackets whose content contains
    Latin letters or Arabic digits (variant readings with sigla, references, sums, notes).
    Greek-only parentheses and brackets (part of the text, or Müller's deletions) are kept."""
    for opener, closer in (("(", ")"), ("[", "]")):
        inner_pat = r"[^()\[\]]*" if opener == "(" else r"[^\[\]]*"
        pat = re.compile(re.escape(opener) + inner_pat + re.escape(closer))
        while True:
            changed = False
            for m in list(pat.finditer(t))[::-1]:
                inner = m.group(0)[1:-1]
                if LATIN_OR_DIGIT.search(inner) or re.search(r"(^|\s)[ΑΒ]\.?$", inner.strip()):
                    t = t[:m.start()] + t[m.end():]
                    changed = True
            if not changed:
                break
    t = t.replace(" ̓", "ʼ").replace("̓ ", "ʼ ")
    t = re.sub(r"\s+([,.·;\]])", r"\1", t)
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\.\.+", ".", t)
    return t.strip()


_DFHG = None


def dfhg(idx):
    global _DFHG
    if _DFHG is None:
        _DFHG = json.loads(DFHG_FILE.read_text(encoding="utf-8"))
    t = _DFHG[idx]["text"]
    for old, new in DFHG_FIXES.get(idx, []):
        assert old in t, (idx, old)
        t = t.replace(old, new)
    return strip_apparatus(t)


# Waddell's English (LacusCurtius transcription of the 1940 Loeb). Transcription slips
# corrected against the printed Loeb (archive.org manethowithengli00maneuoft OCR).
WADDELL_FIXES = [
    ("dynasties of Egypt pamphlet the Flood]", "dynasties of Egypt [after the Flood]"),
    ("Achthô ês", "Achthôês"),
]


def _w_clean(s):
    s = re.sub(r'<A CLASS="ref"[^>]*>.*?</A>', "", s, flags=re.S | re.I)
    s = re.sub(r'<A CLASS="(?:comment|correction)".*?</A>', "", s, flags=re.S | re.I)   # LacusCurtius hover markers
    s = re.sub(r'<SPAN CLASS="pagenum">.*?</SPAN>', "", s, flags=re.S | re.I)
    s = re.sub(r'<SPAN CLASS="fraction"><SPAN CLASS="top">(\d+)</SPAN>&frasl;<SPAN CLASS="bottom">(\d+)</SPAN></SPAN>',
               r" \1/\2", s, flags=re.I)
    s = re.sub(r"<(I|EM)>", "<em>", s, flags=re.I)
    s = re.sub(r"</(I|EM)>", "</em>", s, flags=re.I)
    s = re.sub(r"<(?!/?em>)[^>]+>", "", s)
    import html as _html
    s = s.replace("&#60;", "\x00LT").replace("&#62;", "\x00GT")  # keep Waddell's angle brackets escaped
    s = _html.unescape(s).replace("\u2060", "").replace("\x00LT", "&lt;").replace("\x00GT", "&gt;")
    s = re.sub(r"\s+", " ", s).strip()
    for old, new in WADDELL_FIXES:
        s = s.replace(old, new)
    return s


def waddell(fname, fid, drop_from=None):
    """Paragraphs of one Waddell fragment (by its LacusCurtius anchor id)."""
    t = (WADDELL_DIR / fname).read_text(encoding="utf-8", errors="replace")
    m = re.search(r'<H3[^>]*ID="' + re.escape(fid) + r'"[^>]*>', t)
    assert m, fid
    rest = t[m.end():]
    e = re.search(r'<H3[^>]*ID="Fragment_|CLASS="endnotes"|<HR', rest)
    seg = rest[:e.start()] if e else rest
    seg = seg[seg.find("</H3>") + 5:]
    paras = [_w_clean(b) for b in re.split(r"(?i)<P[^>]*>|<H[34][^>]*>|</H[34]>", seg)]
    paras = [p for p in paras if p]
    if drop_from:
        i = next(k for k, p in enumerate(paras) if p.startswith(drop_from))
        paras = paras[:i]
    return paras


def w_html(paras):
    return "<br>".join(paras)


# Book I: Paris gr. 1764 fols. 2r-4v. (section id, DFHG index, Waddell anchor, folios, note)
SYN_BOOK1 = [
    ("Preface", 9, "Fragment_6", ["2r"],
     "Fol. 2r. Syncellus' preface to the two king lists begins below the short chapter on Noah, at the enlarged initial "
     "'Ἐπειδὴ δὲ τῶν ἀπὸ Μεστραὶμ αἰγυπτιακῶν', and runs to 'ἕως πρώτου ἔτους Ἀβραὰμ ἐξέδωκε' in the third line from the foot of the page."),
    ("I (Africanus)", 10, "Fragment_6.Africanus", ["2r", "2v"],
     "The heading 'Περὶ τῶν μετὰ τὸν κατακλυσμὸν Αἰγύπτου δυναστειῶν ὡς ὁ Ἀφρικανός' fills the last two lines of fol. 2r. "
     "The list begins at the top of fol. 2v 'Μετὰ νέκυας τοὺς ἡμιθέους πρώτη βασιλεία' with Menes of This, kings numbered α'-η' in the "
     "left margin, and ends 'Τὰ τῆς πρώτης δυναστείας οὕτω πως καὶ Εὐσέβιος ὡς ὁ Ἀφρικανὸς ἐξέθετο' (marginal notes beside it)."),
    ("II (Africanus)", 14, "Fragment_8", ["2v", "3r"],
     "Kings 1-7 are on fol. 2v, from 'Δευτέρα δυναστεία Θινιτῶν βασιλέων θ'' (marginal note 'οἱ βόες θεοί') to "
     "'μέλιτι κεκραμένον ἡμέρας ια' ῥυῆναι'. Kings 8-9 (Sesochris, Cheneres) and the totals are on fol. 3r, lines 6-9, where the copyist "
     "joined them to the end of Eusebius' second dynasty: 'σέσωχρις ἔτη μη' ὃς ὕψος εἶχε πηχῶν ε'' ... 'κατὰ τὴν β' ἔκδοσιν Ἀφρικανοῦ'."),
    ("I (Eusebius)", 11, "Fragment_7a", ["2v", "3r"],
     "Fol. 2v, lower half: heading 'Περὶ τῶν μετὰ τὸν κατακλυσμὸν Αἰγυπτίων δυναστειῶν ὡς Εὐσέβιος' (marginal 'Εὐσεβίου'), then "
     "'Μετὰ νέκυας καὶ τοὺς ἡμιθέους πρώτην δυναστείαν καταριθμοῦσι' to king η' 'Οὐβιένθης ἔτη κς'' at the foot of the page; "
     "the total 'οἱ πάντες ἐβασίλευσαν ἔτη σνβ'' opens fol. 3r."),
    ("II (Eusebius)", 15, "Fragment_9", ["3r"],
     "Fol. 3r. Kings 1-7 follow the total of the first dynasty on line 1: 'Δευτέρα βασιλεία βασιλέων θ'' / 'Πρῶτος Βῶχος ἐφ' οὗ χάσμα' "
     "(marginal α'), to 'μέλιτι κεκραμένον ἡμέραις ια' ῥυῆναι' on line 6. Kings 8-9 and the total stand transposed after Africanus' "
     "fourth dynasty, in the last four lines of the page: 'μεθ' ὃν Σέσωχρις ἔτη μη'' ... 'κατὰ τὴν ἔκδοσιν Εὐσεβίου' (marginal 'Εὐσεβίου')."),
    ("III (Africanus)", 17, "Fragment_11", ["3r"],
     "Fol. 3r, from the line marked with a cross 'τρίτη δυναστεία Μεμφιτῶν βασιλέων θ'' to 'Ὁμοῦ τῶν τριῶν δυναστειῶν κατὰ Ἀφρικανὸν "
     "ἔτη ψξθ''. Beside it in the right margin a note on Tosorthros (building in hewn stone and writing)."),
    ("IV (Africanus)", 21, "Fragment_14", ["3r"],
     "Fol. 3r, from the line marked with a cross 'τετάρτη δυναστεία Μεμφιτῶν συγγενείας ἑτέρας βασιλεῖς η'' to "
     "'τῶν μετὰ τὸν κατακλυσμὸν ἔτη ,αμς'' (marginal 'κατὰ Ἀφρικανόν'). The copy writes the total of the dynasty as σοζ' (277)."),
    ("III (Eusebius)", 18, "Fragment_12a", ["3v"],
     "Fol. 3v, top: 'τρίτη δυναστεία Μεμφιτῶν βασιλέων η'' (with a cross) to 'Ὁμοῦ τῶν γ' δυναστειῶν κατὰ τὸν Εὐσέβιον ἔτη ψμζ''."),
    ("IV (Eusebius)", 22, "Fragment_15", ["3v"],
     "Fol. 3v: 'τετάρτη δυναστεία βασιλέων ιζ' Μεμφιτῶν συγγενείας ἑτέρας βασιλείας', then 'Ὧν τρίτος Σοῦφις' (enlarged initial) "
     "to 'Ὁμοῦ τῶν δ' δυναστειῶν μετὰ τὸν κατακλυσμὸν ,αρϟε' κατ' Εὐσέβιον'."),
    ("V (Africanus)", 25, "Fragment_18", ["3v"],
     "Fol. 3v, middle: 'κατὰ Ἀφρικανὸν ε' δυναστεία βασιλέων η' ἐξ Ἐλεφαντίνης', the nine kings written three to a line, to "
     "'ἔτη ,ασϟδ''. The copy has Ὄβνος for Onnos."),
    ("VI (Africanus)", 28, "Fragment_20", ["3v"],
     "Fol. 3v: 'ἕκτη δυναστεία βασιλέων ἓξ Μεμφιτῶν' (same line as the end of the fifth) to 'τῶν ε' δυναστειῶν ἔτη ,αυϟζ'', "
     "with Nitocris at numeral ς' in the left margin."),
    ("VII (Africanus)", 32, "Fragment_23", ["3v"],
     "Fol. 3v, second and third lines from the foot: 'ἑβδόμη δυναστεία Μεμφιτῶν βασιλέων ο' οἳ ἐβασίλευσαν ἡμέρας ο''."),
    ("VIII (Africanus)", 35, "Fragment_25", ["3v", "4r"],
     "The heading 'ὀγδόη δυναστεία Μεμφιτῶν βασιλέων κζ'' (with a cross) is the last line of fol. 3v; the reign and running total "
     "'οἳ ἐβασίλευσαν ἔτη ρμς' γίνονται σὺν τοῖς προτεταγμένοις ἔτη ,αχλθ' τῶν η' δυναστειῶν' are the first two lines of fol. 4r."),
    ("V (Eusebius)", 26, "Fragment_19", ["4r"],
     "Fol. 4r, lines 3-7: 'κατὰ Εὐσέβιον ε' δυναστεία βασιλέων τριάκοντα ἑνὸς ἐξ Ἐλεφαντίνης' (in capitals, with a cross), "
     "'ὧν πρῶτος Ὀθόης' to ',ασϟε''."),
    ("VI (Eusebius)", 29, "Fragment_21", ["4r"],
     "Fol. 4r: heading 'ἕκτη δυναστεία' in capitals, then 'Γυνὴ Νίτωκρις ἐβασίλευσε' to 'τῶν πέντε δυναστειῶν ἔτη ,αυϟη''. "
     "Syncellus' remark that follows on the page ('σημειωτέον ὁπόσον Εὐσέβιος Ἀφρικανοῦ λείπεται ἀκριβείας', three lines) is not given here."),
    ("VII (Eusebius)", 33, "Fragment_24a", ["4r"],
     "Fol. 4r: 'ἑβδόμη δυναστεία Μεμφιτῶν βασιλέων ε' οἳ ἐβασίλευσαν ἡμέρας οε'' (two lines, with a cross)."),
    ("VIII (Eusebius)", 36, "Fragment_25a", ["4r"],
     "Fol. 4r: 'ὀγδόη δυναστεία Μεμφιτῶν βασιλέων ε' οἳ ἐβασίλευσαν ἔτη ρ'' (with a large cross) and the line "
     "'γίνονται σὺν τοῖς προτεταγμένοις ἔτη ,αφϟη' τῶν ὀκτὼ δυναστειῶν', to which the copyist joined 'κατὰ Ἀφρικανόν', "
     "the heading of what follows."),
    ("IX (Africanus)", 38, "Fragment_27", ["4r"],
     "Fol. 4r: 'ἐννάτη δυναστεία Ἡρακλεοπολιτῶν βασιλέων ιθ' οἳ ἐβασίλευσαν ἔτη υθ'', then 'ὧν πρῶτος Ἀχθόης' to "
     "'ὑπὸ κροκοδείλου διεφθάρη'."),
    ("X (Africanus)", 41, "Fragment_29", ["4r"],
     "Fol. 4r: 'δεκάτη δυναστεία Ἡρακλεοπολιτῶν βασιλέων ιθ' οἳ ἐβασίλευσαν ἔτη ρπε'' (two lines, with a cross)."),
    ("XI (Africanus)", 44, "Fragment_31", ["4r", "4v"],
     "The last four lines of fol. 4r: 'ἑνδεκάτη δυναστεία Διοσπολιτῶν βασιλέων ις'' ... 'μέχρι τοῦδε τὸν πρῶτον τόμον κατάγει ὁ Μανεθῶ'; "
     "the total 'ὁμοῦ βασιλεῖς ρϟβ' ἔτη ,βτ' ἡμέραι ο'' is the first line of fol. 4v."),
    ("IX (Eusebius)", 39, "Fragment_28", ["4v"],
     "Fol. 4v, after the heading 'κατ' Εὐσέβιον': 'ἐννάτη δυναστεία Ἡρακλεοπολιτῶν βασιλέων τεσσάρων οἳ ἐβασίλευσαν ἔτη ρ''"
     " (enlarged initial), 'ὧν πρῶτος Ἀχθώης' to 'ὑπὸ κροκοδείλου διεφθάρη'."),
    ("X (Eusebius)", 42, "Fragment_30", ["4v"],
     "Fol. 4v: 'δεκάτη δυναστεία Ἡρακλεοπολιτῶν βασιλέων ιθ' οἳ ἐβασίλευσαν ἔτη ρπε''."),
    ("XI (Eusebius)", 45, "Fragment_32", ["4v"],
     "Fol. 4v: 'ἑνδεκάτη δυναστεία Διοσπολιτῶν βασιλέων ις' οἳ ἐβασίλευσαν ἔτη μγ'' ... 'μέχρι τοῦ α' τόμου κατάγει ὁ Μανεθῶ' and "
     "'ὁμοῦ βασιλεῖς ρϟβ' ἔτη ,βτ' ἡμέραι οθ''. Below it begins 'δευτέρου τόμου Μανεθῶ' (Book II)."),
]

B_VIEWER = "https://gallica.bnf.fr/ark:/12148/" + GALLICA_B
A_VIEWER = "https://gallica.bnf.fr/ark:/12148/" + GALLICA_A
GALLICA_LICENSE = ("Bibliothèque nationale de France, Gallica: non-commercial reuse permitted with the credit "
                   "'Source gallica.bnf.fr / BnF' (Gallica terms of use); images made from the BnF microfilm")
SYN_TR_NOTES = [
    "Greek: C. Müller, Fragmenta Historicorum Graecorum II (Paris 1848), Manetho fragments, from the Digital FHG (DFHG, "
    "University of Leipzig) and corrected against the printed pages (archive.org fragmentahistori02mueluoft); the corrections "
    "are listed in scripts/import_manetho.py. Müller's text is a critical text based on Goar's and Dindorf's editions of Syncellus, "
    "so its spelling of names and some numbers differ from this manuscript. Müller's inline apparatus (variant readings and "
    "references in parentheses) is omitted; his square brackets (words he added or doubted) are kept.",
    "English: W. G. Waddell, Manetho (Loeb Classical Library, 1940), as transcribed on LacusCurtius, checked against the printed "
    "Loeb (archive.org manethowithengli00maneuoft). Waddell translates his own Greek text, which follows Müller closely but not in "
    "every name and number.",
]


def build_syncellus_book1(force):
    secs = []
    for sid, idx, wid, folios, note in SYN_BOOK1:
        drop = "(Syncellus adds:)" if wid == "Fragment_21" else None
        paras = waddell("book1.html", wid, drop_from=drop)
        pages = [scan_B(f, force) for f in folios]
        secs.append({
            "section": sid,
            "original_ref": f"Waddell fr. {wid.split('_')[1].replace('.Africanus', '')}; Müller FHG II; Paris gr. 1764 fol. {', '.join(folios)}",
            "original_text": dfhg(idx),
            "text": w_html(paras),
            "scan_pages": pages,
            "scan_note": note + f" Checked on the image (Gallica {B_VIEWER}).",
        })
    tid = PREFIX + "dynasties-1-11-syncellus"
    local = []
    for s in secs:
        for p in s["scan_pages"]:
            if p not in local:
                local.append(p)
    entry = {
        "id": tid, "slug": tid,
        "title": "Manetho's Dynasties I-XI (Book I), in Africanus and Eusebius (George Syncellus)",
        "language": "Greek (Müller 1848) / English (Waddell 1940)",
        "source": "Paris gr. 1764 (11th c.), fols. 2r-4v, via Gallica IIIF + Müller FHG II Greek (DFHG, checked against the print) + Waddell English (Loeb 1940, public domain)",
        "description": "The first book of Manetho's king list, from Menes to the Eleventh Dynasty, in the two versions of Julius Africanus "
                       "and Eusebius as copied by George Syncellus, shown on the manuscript pages of Paris gr. 1764.",
        "introduction": (
            "<p>Manetho's <em>Aegyptiaca</em> divided the kings of Egypt after the reigns of gods, demigods and spirits of the dead into "
            "thirty dynasties, a scheme still used by Egyptologists. Its lists survive only in epitomes: the <em>Chronographiae</em> of "
            "Julius Africanus (early 3rd century AD) and the <em>Chronicle</em> of Eusebius of Caesarea (early 4th century), both lost "
            "in Greek but quoted side by side around 810 AD by the Byzantine chronicler George Syncellus in his <em>Ecloga chronographica</em>.</p>\n\n"
            "<p>This entry gives Book I: Menes of This and the First Dynasty, the pyramid builders of the Third and Fourth Dynasties "
            "(Tosorthros, credited with building in hewn stone; Suphis, credited with the Great Pyramid), the queen Nitocris, the seventy "
            "kings of seventy days, and the Heracleopolitan and Theban houses down to Ammenemes, where Manetho's first book ended "
            "('192 kings, 2300 years'). Each version is a separate section, in the order the manuscript gives them.</p>\n\n"
            "<p>The manuscript is Paris, Bibliothèque nationale de France, grec 1764, an 11th-century copy of Syncellus that has lost its "
            "beginning and end; the lists of Book I occupy fols. 2r-4v. The images are from the BnF microfilm. Every section names the "
            "folio(s) carrying it and the words seen there. The copy has the same order and the same displacements as Goar's and Dindorf's "
            "text: the end of Africanus' second dynasty is joined to Eusebius' second, and the end of Eusebius' second dynasty stands after "
            "Africanus' fourth.</p>"
        ),
        "translator_notes": SYN_TR_NOTES + [
            "Syncellus' own comment after Eusebius' sixth dynasty (on fol. 4r) is not part of Manetho and is omitted in both languages.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": f"Bibliothèque nationale de France, Gallica, Grec 1764 ({B_VIEWER}), IIIF images 6-9 (fols. 2r-4v), single pages cropped from the microfilm openings",
            "scan_license": GALLICA_LICENSE,
            "scan_manuscript": "Paris, BnF, grec 1764, parchment, 143 fols., 11th century, George Syncellus, Ecloga chronographica (acephalous; from Istanbul, bought 1687)",
            "scan_mapping": "Read on the page images: each dynasty list located on its folio by its heading and opening words, recorded in the section notes",
            "scan_mapping_urls": [B_VIEWER, "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc21908z"],
            "scan_local_paths": local,
            "original_text_source": f"C. Müller, FHG II (1848) pp. 539-557, via DFHG (http://www.dfhg-project.org/DFHG/api.php?author=MANETHO%20SEBENNYTA), corrected against the print ({FHG_ARCHIVE})",
            "original_text_license": "edition public domain (1848); DFHG digital text CC BY-NC-SA 4.0 (as stated on dfhg-project.org)",
            "translation_source": f"W. G. Waddell, Manetho (Loeb Classical Library 350, 1940), LacusCurtius transcription {WADDELL_URL}, checked against {WADDELL_SCAN}",
            "translation_license": "public domain in the US: 1940 copyright not renewed (no renewal for Waddell or Manetho in the Copyright Office renewal records for 1966-1969, NYPL CCE renewals data; LacusCurtius states the same); translator died 1945",
            "translator": "W. G. Waddell (1940)",
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "title": entry["title"], "author_id": "manetho", "language": "Greek",
        "era": "Hellenistic", "tradition": "egyptian", "category": "history",
        "date_approx": "c. 280 BCE (Manetho); epitomes 3rd-4th c. AD; Syncellus c. 810 AD; manuscript 11th c.", "century": -3,
        "source": entry["source"], "description": entry["description"],
        "themes": ["manetho", "egypt", "dynasties", "pharaohs", "menes", "pyramids", "syncellus", "africanus", "eusebius", "king-list", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p, "caption": "Paris gr. 1764 fol. " + p.split("-f")[-1].replace(".jpg", "").lstrip("0")} for p in local]},
    }
    return entry, row


# Book III: Paris gr. 1764 fols. 10v-11v. DFHG index 78 holds both versions of Dynasty XX.
def dfhg_d20(which):
    t = dfhg(78)
    afr, eus = t.split(" ΚΑΤʼ ΕΥΣΕΒΙΟΝ. ", 1)
    return afr if which == "afr" else "ΚΑΤʼ ΕΥΣΕΒΙΟΝ. " + eus


SYN_BOOK3 = [
    ("XX (Africanus)", "afr20", "Fragment_57", ["10v"],
     "Fol. 10v, lines 8-9, marked κ' in the margin: 'κατὰ δὲ Ἀφρικανὸν τρίτου τόμου Μανεθῶ εἰκοστὴ δυναστεία / βασιλέων Διοσπολιτῶν ιβ' "
     "οἳ ἐβασίλευσαν ἔτη ρλε''."),
    ("XXI (Africanus)", 80, "Fragment_58", ["10v"],
     "Fol. 10v: 'πρώτη καὶ εἰκοστὴ δυναστεία βασιλέων Τανιτῶν ζ'', then three lines of kings (α' Σμένδης ... ζ' Ψουσέννης ἔτη ιδ') "
     "and 'ὁμοῦ ἔτη ρλ''."),
    ("XXII (Africanus)", 83, "Fragment_60", ["10v"],
     "Fol. 10v: 'εἰκοστὴ δευτέρα δυναστεία Βουβαστιτῶν βασιλέων θ'', two lines of kings (Σέσωγχις, Ὀσορθών, 'ἄλλοι τρεῖς', "
     "Τακέλωθις, 'ἄλλοι τρεῖς') ending 'ὁμοῦ ἔτη ρκ''."),
    ("XXIII (Africanus)", 86, "Fragment_62", ["10v"],
     "Fol. 10v: 'τρίτη καὶ εἰκοστὴ δυναστεία Τανιτῶν βασιλέων δ'', 'α' Πετουβάτης ἔτη μ' ἐφ' οὗ Ὀλυμπιὰς ἤχθη α'' to 'ὁμοῦ ἔτη πθ''."),
    ("XXIV (Africanus)", 89, "Fragment_64", ["10v"],
     "Fol. 10v: 'τετάρτη καὶ εἰκοστὴ δυναστεία· Βόχχωρις Σαΐτης ἔτη ς' ἐφ' οὗ / ἀρνίον ἐφθέγξατο ἔτη ϡϟ''; a marginal note at left "
     "reads 'ἐπὶ τούτου ἀρνίον'."),
    ("XXV (Africanus)", 92, "Fragment_66", ["10v"],
     "Fol. 10v: 'πέμπτη καὶ εἰκοστὴ δυναστεία Αἰθιόπων βασιλέων γ'', 'α' Σαβάκων ὃς αἰχμάλωτον Βόχχωριν ἑλὼν ἔκαυσε ζῶντα' to "
     "'γ' Τάρκος ἔτη ιη'' and the total."),
    ("XX (Eusebius)", "eus20", "Fragment_57b", ["10v"],
     "Fol. 10v, lines 26-27, marked κ': 'κατ' Εὐσέβιον τρίτου τόμου Μανεθῶ κ' δυναστεία βα/σιλέων Διοσπολιτῶν ιβ' οἳ ἐβασίλευσαν ἔτη ροη''."),
    ("XXI (Eusebius)", 81, "Fragment_59a", ["10v", "11r"],
     "The heading 'εἰκοστὴ πρώτη δυναστεία βασιλέων Τανιτῶν ζ'' (marked κα') is the last line of fol. 10v; the seven kings "
     "(α' Σμένδης ἔτη κς' ... ζ' Ψουσέννης) and 'ὁμοῦ ἔτη ρλ'' are the first three lines of fol. 11r."),
    ("XXII (Eusebius)", 84, "Fragment_61a", ["11r"],
     "Fol. 11r, lines 4-5, marked κβ': 'εἰκοστὴ δευτέρα δυναστεία Βουβαστιτῶν βασιλέων γ'', 'α' Σεσώγχωσις ἔτη κα'' to 'ἔτη μθ''."),
    ("XXIII (Eusebius)", 87, "Fragment_63a", ["11r"],
     "Fol. 11r, lines 6-8, marked κγ': 'εἰκοστὴ τρίτη δυναστεία Τανιτῶν βασιλέων γ'' to 'ὁμοῦ ἔτη μδ''."),
    ("XXIV (Eusebius)", 90, "Fragment_65a", ["11r"],
     "Fol. 11r, lines 9-10, marked κδ': 'εἰκοστὴ τετάρτη δυναστεία', 'Βόχχωρις Σαΐτης ἔτη μδ' ἐφ' οὗ ἀρνίον ἐφθέγξατο'; in the right "
     "margin 'ἐπὶ τούτου ἀρνίον'."),
    ("XXV (Eusebius)", 93, "Fragment_67a", ["11r"],
     "Fol. 11r, lines 11-13, marked κε': 'εἰκοστὴ πέμπτη δυναστεία Αἰθιόπων βασιλέων γ'' to 'γ' Ταρακὸς ἔτη κ'' and the total."),
    ("XXVI (Africanus)", 95, "Fragment_68", ["11r"],
     "Fol. 11r, marked κς': 'κατὰ Ἀφρικανὸν ἕκτη καὶ εἰκοστὴ δυναστεία Σαϊτῶν βασιλέων θ'', six lines from 'α' Στεφινάτης' "
     "to 'θ' Ψαμμεχερίτης μῆνας ς'' and the total."),
    ("XXVII (Africanus)", 98, "Fragment_70", ["11r"],
     "Fol. 11r, marked κζ': 'ἑβδόμη καὶ εἰκοστὴ δυναστεία Περσῶν βασιλέων η'', five lines from 'α' Καμβύσης' to "
     "'ὁμοῦ ἔτη ρκδ' μῆνας δ''."),
    ("XXVIII (Africanus)", 101, "Fragment_72a", ["11r"],
     "Fol. 11r, one line marked κη': 'εἰκοστὴ ὀγδόη δυναστεία Ἀμυρτέος Σαΐτης ἔτη ς''."),
    ("XXIX (Africanus)", 104, "Fragment_73a", ["11r"],
     "Fol. 11r, last three lines, marked κθ': 'ἐννάτη καὶ εἰκοστὴ δυναστεία Μενδήσιοι βασιλεῖς δ'' to 'ὁμοῦ ἔτη κ' μῆνας δ''."),
    ("XXVI (Eusebius)", 96, "Fragment_69a", ["11v"],
     "Fol. 11v, top, marked κς' and 'Εὐσεβίου' in the margin: 'κατὰ Εὐσέβιον κς' δυναστεία Σαϊτῶν βασιλεῖς θ'', six lines from "
     "'α' Ἀμμέρις Αἰθίοψ ἔτη ιβ'' to 'ὁμοῦ ἔτη ρξγ''. The manuscript writes out the notes on Nechao II and Uaphris, which Müller "
     "shortens with κτλ."),
    ("XXVII (Eusebius)", 99, "Fragment_71a", ["11v"],
     "Fol. 11v, marked κζ': 'εἰκοστὴ ἑβδόμη δυναστεία Περσῶν βασιλέων η'', five lines from 'α' Καμβύσης' to 'ὁμοῦ ἔτη ρκ' καὶ μῆνας δ''."),
    ("XXVIII (Eusebius)", 102, "Fragment_72b", ["11v"],
     "Fol. 11v, one line marked κη': 'εἰκοστὴ ὀγδόη δυναστεία Ἀμυρταῖος Σαΐτης ἔτη ς''."),
    ("XXIX (Eusebius)", 105, "Fragment_73b", ["11v"],
     "Fol. 11v, marked κθ': 'εἰκοστὴ θ' δυναστεία Μενδήσιοι βασιλεῖς δ'' and two lines of kings, the fifth 'ε' Μοῦθις ἔτος α'', "
     "and the total."),
    ("XXX (Africanus)", 107, "Fragment_74a", ["11v"],
     "Fol. 11v, marked λ' and 'Ἀφρικανοῦ' in the margin: 'κατὰ Ἀφρικανὸν λ' δυναστεία Σεβεννυτῶν βασιλέων γ'' and one line of kings "
     "(Νεκτανέβης ἔτη ιη', Τεὼς ἔτη β', Νεκτανεβὸς ἔτη ιη')."),
    ("XXXI (Africanus)", 110, "Fragment_75a", ["11v"],
     "Fol. 11v, marked λα': 'πρώτη καὶ τριακοστὴ δυναστεία Περσῶν βασιλέων γ'', two lines of kings and the total of the third book, "
     "then the centred line 'μέχρι τῶνδε Μανεθῶς'. The next line, 'τὰ δὲ μετὰ ταῦτα ἐξ Ἑλληνικῶν συγγραφέων' (the Macedonian kings), "
     "is Syncellus and is not given here."),
    ("XXX (Eusebius)", 108, "Fragment_74b", ["11v"],
     "Fol. 11v, marked λ' and 'Εὐσεβίου': 'κατὰ Εὐσέβιον τριακοστὴ δυναστεία Σεβεννυτῶν βασιλέων γ'' and one line of kings "
     "(Νεκτανέβης ἔτη ι', Τεὼς ἔτη β', Νεκτανεβὸς ἔτη η')."),
    ("XXXI (Eusebius)", 111, "Fragment_75b", ["11v"],
     "Fol. 11v, last four lines, marked λα': 'τριακοστὴ πρώτη δυναστεία Περσῶν βασιλέων γ'' to 'ὃν Ἀλέξανδρος ὁ Μακεδὼν καθεῖλε· "
     "ταῦτα τοῦ τρίτου Μανεθῶ'. A later hand has written 'p. 78 ed. Paris.' in the left margin."),
]


def build_syncellus_book3(force):
    secs = []
    for sid, idx, wid, folios, note in SYN_BOOK3:
        greek = dfhg_d20(idx[:3]) if isinstance(idx, str) else dfhg(idx)
        paras = waddell("book3.html", wid)
        pages = [scan_B(f, force) for f in folios]
        secs.append({
            "section": sid,
            "original_ref": f"Waddell fr. {wid.split('_')[1]}; Müller FHG II; Paris gr. 1764 fol. {', '.join(folios)}",
            "original_text": greek,
            "text": w_html(paras),
            "scan_pages": pages,
            "scan_note": note + f" Checked on the image (Gallica {B_VIEWER}).",
        })
    tid = PREFIX + "dynasties-20-31-syncellus"
    local = []
    for s in secs:
        for p in s["scan_pages"]:
            if p not in local:
                local.append(p)
    entry = {
        "id": tid, "slug": tid,
        "title": "Manetho's Dynasties XX-XXXI (Book III), in Africanus and Eusebius (George Syncellus)",
        "language": "Greek (Müller 1848) / English (Waddell 1940)",
        "source": "Paris gr. 1764 (11th c.), fols. 10v-11v, via Gallica IIIF + Müller FHG II Greek (DFHG, checked against the print) + Waddell English (Loeb 1940, public domain)",
        "description": "The third book of Manetho's king list, from the Twentieth Dynasty to the Persian kings conquered by Alexander, "
                       "in the versions of Africanus and Eusebius as copied by George Syncellus, on the manuscript pages of Paris gr. 1764.",
        "introduction": (
            "<p>Manetho's third book carried the kings of Egypt from the Twentieth Dynasty to the second Persian conquest. It includes "
            "the Tanite and Bubastite houses (Smendes, Psusennes, Sesonchis, Osorthon), Bocchoris of Sais, under whom 'a lamb spoke', the "
            "Ethiopian conquerors Sabacon, Sebichos and Taracus, the Saite kings Psammetichus, Nechao II and Amosis, the Persian kings from "
            "Cambyses to Darius II, the last native houses of Mendes and Sebennytus (Nectanebes and Teos), and the brief Persian dynasty "
            "of Ochus, Arses and Darius III, 'whom Alexander of Macedon overthrew'.</p>\n\n"
            "<p>As with the earlier books, the lists survive in the two epitomes of Julius Africanus and Eusebius, which George Syncellus "
            "copied side by side about 810 AD. The manuscript is Paris, Bibliothèque nationale de France, grec 1764 (11th century), "
            "fols. 10v-11v, where the dynasties are numbered κ'-λα' in the margin; the images are from the BnF microfilm. Each section is "
            "one dynasty in one version, in the order of the manuscript, with the folio and the words read on it.</p>"
        ),
        "translator_notes": SYN_TR_NOTES + [
            "In Eusebius' twenty-sixth dynasty Müller abbreviates the notes on Nechao II and Uaphris with κτλ. ('and so on', as in "
            "Africanus); Waddell translates them in full.",
            "At Eusebius' twenty-ninth dynasty the printed FHG page has damaged type in the word δυναστεία and the DFHG text lost two kings; "
            "the list was restored from the printed page.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": f"Bibliothèque nationale de France, Gallica, Grec 1764 ({B_VIEWER}), IIIF images 15-16 (fols. 10v-11v), single pages cropped from the microfilm openings",
            "scan_license": GALLICA_LICENSE,
            "scan_manuscript": "Paris, BnF, grec 1764, parchment, 143 fols., 11th century, George Syncellus, Ecloga chronographica (acephalous; from Istanbul, bought 1687)",
            "scan_mapping": "Read on the page images: each dynasty located by its heading and its marginal dynasty numeral, recorded in the section notes",
            "scan_mapping_urls": [B_VIEWER, "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc21908z"],
            "scan_local_paths": local,
            "original_text_source": f"C. Müller, FHG II (1848) pp. 589-598, via DFHG (http://www.dfhg-project.org/DFHG/api.php?author=MANETHO%20SEBENNYTA), corrected against the print ({FHG_ARCHIVE})",
            "original_text_license": "edition public domain (1848); DFHG digital text CC BY-NC-SA 4.0 (as stated on dfhg-project.org)",
            "translation_source": f"W. G. Waddell, Manetho (Loeb Classical Library 350, 1940), LacusCurtius transcription {WADDELL_URL}, checked against {WADDELL_SCAN}",
            "translation_license": "public domain in the US: 1940 copyright not renewed (no renewal for Waddell or Manetho in the Copyright Office renewal records for 1966-1969, NYPL CCE renewals data; LacusCurtius states the same); translator died 1945",
            "translator": "W. G. Waddell (1940)",
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "title": entry["title"], "author_id": "manetho", "language": "Greek",
        "era": "Hellenistic", "tradition": "egyptian", "category": "history",
        "date_approx": "c. 280 BCE (Manetho); epitomes 3rd-4th c. AD; Syncellus c. 810 AD; manuscript 11th c.", "century": -3,
        "source": entry["source"], "description": entry["description"],
        "themes": ["manetho", "egypt", "dynasties", "pharaohs", "saite", "persian-kings", "syncellus", "africanus", "eusebius", "king-list", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p, "caption": "Paris gr. 1764 fol. " + p.split("-f")[-1].replace(".jpg", "").lstrip("0")} for p in local]},
    }
    return entry, row


# Book II, dynasties XII-XVII: Paris gr. 1764 fols. 4v-5r.
SYN_BOOK2A = [
    ("XII (Africanus)", 48, "Fragment_34", ["4v"],
     "Fol. 4v, lines 2-10, directly after the total of Africanus' first book: '+ Δευτέρου τόμου Μανεθῶ· Δωδεκάτη δυ/ναστεία Διοσπολιτῶν "
     "βασι(λέων) ζ'', then 'Σεσόγχοσις Ἀμμανέμου υἱὸς ἔτη μς'' (marginal α'), Sesostris' conquests, Lachares and the labyrinth, to "
     "'ζ' Σκεμίοφρις ἀδελφὴ ἔτη δ' ὁμοῦ ἔτη ρξ''. Goar and Müller print this list later in Syncellus (Goar p. 69); in this manuscript "
     "it stands here, before the heading 'κατ' Εὐσέβιον'."),
    ("XII (Eusebius)", 49, "Fragment_35", ["4v", "5r"],
     "Begins on fol. 4v below the total of Eusebius' first book: 'Δευτέρου τόμου Μανεθῶ' in capitals, 'Δωδεκάτη δυναστεία Διοσπολιτῶν "
     "βασιλέων ζ'', 'ὧν ὁ πρῶτος Σεσόγχωσις Ἀμμενέμου υἱὸς ἔτη μς'' to the foot of the page; continues on fol. 5r lines 1-4 'ὑπὸ τῶν "
     "Αἰγυπτίων μετὰ Ὄσιριν νομισθῆναι· μεθ' ὃν Λάμαρις ...' to 'οἱ πάντες ἐβασίλευσαν ἔτεσι σμε''. The heading 'Δευτέρου τόμου "
     "Μανεθῶ' is on the page and in Waddell's English but not in Müller's text of this fragment."),
    ("XIII (Africanus)", 52, "Fragment_38", ["5r"],
     "Fol. 5r, line 5, under the heading 'κατὰ Ἀφρικανόν' at the end of line 4: 'Τρισκαιδεκάτη δυναστεία Διοσπολιτῶν βασιλέων ξ' οἳ "
     "ἐβασίλευσαν ἔτη υνγ''."),
    ("XIV (Africanus)", 55, "Fragment_41a", ["5r"],
     "Fol. 5r, line 6: 'Τεσσαρεσκαιδεκάτη δυναστεία Ξοϊτῶν βασιλέων ος' οἳ ἐβασίλευσαν ἔτη ρπδ''. Müller notes that this line is found "
     "only in this manuscript (B); Paris gr. 1711 has a gap here."),
    ("XV (Africanus)", 59, "Fragment_43", ["5r"],
     "Fol. 5r, lines 7-11: 'Πεντεκαιδεκάτη δυναστεία ποιμένων· ἦσαν δὲ Φοίνικες ξένοι βασιλεῖς ς' οἳ καὶ Μέμφιν εἷλον' to 'ς' Ἄφοβις "
     "ἔτη ξα'' and 'ὁμοῦ ἔτη σπδ''. In the manuscript the sentence on Saites ('ὧν πρῶτος Σαΐτης ...') comes before the founding of the "
     "town in the Sethroite nome; Müller and Waddell print it after."),
    ("XVI (Africanus)", 62, "Fragment_45", ["5r"],
     "Fol. 5r, lines 12-13, in capitals: 'Ἑξκαιδεκάτη δυναστεία ποιμένες ἄλλοι βασιλεῖς λβ' ἐβα/σίλευσαν ἔτη φιη''."),
    ("XVII (Africanus)", 65, "Fragment_47", ["5r"],
     "Fol. 5r, lines 14-15: 'Ἑπτακαιδεκάτη δυναστεία ποιμένες ἄλλοι βασιλεῖς μγ' καὶ Θη/βαῖοι Διοσπολῖται μγ'· ὁμοῦ οἱ ποιμένες καὶ "
     "οἱ Θηβαῖοι ἐβασίλευσαν ἔτη ρνα''. The word ἢ ('or') in square brackets is Müller's addition and is not on the page."),
    ("XIII (Eusebius)", 52, "Fragment_39a", ["5r"],
     "Fol. 5r, line 17, under the heading 'κατ' Εὐσέβιον' (line 16): 'Τρισκαιδεκάτη δυναστεία Διοσπολιτῶν βασιλέων ξ' οἳ ἐβασίλευσαν ἔτη "
     "υνγ''. Müller does not print this line separately, stating that Syncellus' Eusebius has it word for word as Africanus (FHG II p. 565); "
     "the Greek shown is his text of Africanus' line, which agrees with what is written here."),
    ("XIV (Eusebius)", 56, "Fragment_41b", ["5r"],
     "Fol. 5r, lines 18-19: 'Τεσσαρεσκαιδεκάτη δυναστεία Ξοϊτῶν βασιλέων ος' οἳ ἐβασίλευσαν ἔτη ρπδ' / ἐν ἄλλῳ υπδ''."),
    ("XV (Eusebius)", 60, "Fragment_44a", ["5r"],
     "Fol. 5r, lines 19-20: 'Πεντεκαιδεκάτη δυναστεία Διοσπολιτῶν βασιλέων / οἳ ἐβασίλευσαν ἔτη σν''."),
    ("XVI (Eusebius)", 63, "Fragment_46a", ["5r"],
     "Fol. 5r, lines 20-21: 'Ἑξκαιδεκάτη δυναστεία Θηβαῖοι βασιλεῖς / ε' οἳ καὶ ἐβασίλευσαν ἔτη ρϟ''."),
    ("XVII (Eusebius)", 66, "Fragment_48a", ["5r"],
     "Fol. 5r, lines 21-27: 'Ἑπτακαιδεκάτη δυναστεία ποιμένες ἦσαν ἀδελφοὶ Φοίνικες ξένοι βασιλεῖς οἳ καὶ Μέμφιν εἷλον· ὧν πρῶτος "
     "Σαΐτης' to 'τρίτος Ἄφωφις ἔτη ιδ' μεθ' ὃν Ἄρχλης ἔτη λ' ὁμοῦ ἔτη ργ'' and 'κατὰ τούτους Αἰγυπτίων βασιλεὺς Ἰωσὴφ δείκνυται'. "
     "The page writes 'τρίτος' in full where Müller prints [γ']. Syncellus' comment that follows ('Σημειωτέον πῶς ὁ Εὐσέβιος ...') is "
     "not given here."),
    ("XIX (Africanus)", 75, "Fragment_55", ["10r"],
     "Fol. 10r, lower half, beginning on the line that ends Africanus' eighteenth dynasty ('ὁμοῦ ἔτη σξγ''): 'Ἐννεακαιδεκάτη δυναστεία "
     "βασιλέων ζ' / Διοσπολιτῶν· α' Σέθως ἔτη να'· β' Ῥαψάκης ...', with ε' Ἀμμενεμνῆς and 'ς' Θούωρις ὁ παρ' Ὁμήρῳ καλούμενος Πόλυβος, "
     "ζ' Ἀλκάνδρας ἀνήρ', to 'ὁμοῦ ἔτη σθ'' and the line 'ἐπὶ τοῦ αὐτοῦ δευτέρου τόμου Μανεθῶ βασιλεῖς ϟς' ἔτη ,βρκα''. The closing "
     "words 'ἔτη ,βρκα'' (2121 years), which Waddell translates, are on the page but stand in Müller's note, not in his text."),
    ("XIX (Eusebius)", 76, "Fragment_56a", ["10v"],
     "Fol. 10v, lines 4-8, after the end of Eusebius' eighteenth dynasty: '+ Ἐννεακαιδεκάτη δυναστεία βασιλέων ε' Διοσπολιτῶν', "
     "'α' Σέθως ἔτη νε'' (marginal α', δ', ς') to 'ε' Θούωρις ὁ παρ' Ὁμήρῳ καλούμενος Πόλυβος Ἀλκάνδρας ἀνήρ ...', 'ὁμοῦ ἔτη ρϟδ'' and "
     "'ἐπὶ τὸ αὐτὸ δευτέρου τόμου Μανεθῶ βασιλέων ϟβ' ἔτη ,βρκα''. Müller prints ,αρκα' with the note 'scr. ,βρκα''; the page has ,βρκα'."),
]


def build_syncellus_book2a(force):
    secs = []
    for sid, idx, wid, folios, note in SYN_BOOK2A:
        paras = waddell("book2.html", wid)
        pages = [scan_B(f, force) for f in folios]
        secs.append({
            "section": sid,
            "original_ref": f"Waddell fr. {wid.split('_')[1]}; Müller FHG II; Paris gr. 1764 fol. {', '.join(folios)}",
            "original_text": dfhg(idx),
            "text": w_html(paras),
            "scan_pages": pages,
            "scan_note": note + f" Checked on the image (Gallica {B_VIEWER}).",
        })
    tid = PREFIX + "dynasties-12-19-syncellus"
    local = []
    for s in secs:
        for p in s["scan_pages"]:
            if p not in local:
                local.append(p)
    entry = {
        "id": tid, "slug": tid,
        "title": "Manetho's Dynasties XII-XVII and XIX (Book II): Sesostris, the Shepherd Kings and the Fall of Troy, in Africanus and Eusebius (George Syncellus)",
        "language": "Greek (Müller 1848) / English (Waddell 1940)",
        "source": "Paris gr. 1764 (11th c.), fols. 4v-5r and 10r-10v, via Gallica IIIF + Müller FHG II Greek (DFHG, checked against the print) + Waddell English (Loeb 1940, public domain)",
        "description": "The start of Manetho's second book: the Twelfth Dynasty with Sesostris, conqueror of Asia, and the builder of the Labyrinth, "
                       "the Thirteenth to Seventeenth Dynasties with the Shepherd Kings (Hyksos), and the Nineteenth Dynasty, ending with Thuoris, "
                       "in whose reign Troy was taken, in the versions of Africanus and Eusebius, on the manuscript pages of Paris gr. 1764.",
        "introduction": (
            "<p>Manetho's second book began with the Twelfth Dynasty of Diospolis (Thebes). Its third king, Sesostris, is credited with "
            "conquering Asia and Europe as far as Thrace in nine years and setting up pillars in every land; his successor Lachares (or "
            "Lamaris) built the Labyrinth in the Arsinoite nome as his tomb. Then come the long dynasties of the Middle Kingdom and the "
            "Second Intermediate Period, and the Shepherd Kings (the Hyksos), foreigners from Phoenicia who took Memphis. Africanus puts "
            "them in the Fifteenth Dynasty, Eusebius in the Seventeenth, adding that Joseph ruled Egypt in their time. Josephus' longer "
            "quotation of Manetho on the same people is a separate entry in this collection.</p>\n\n"
            "<p>The lists come from the epitomes of Julius Africanus and Eusebius as copied by George Syncellus about 810 AD. The manuscript "
            "is Paris, Bibliothèque nationale de France, grec 1764 (11th century), fols. 4v-5r and 10r-10v, from the BnF microfilm. In this "
            "copy Africanus' Twelfth Dynasty stands directly after his first book, before the Eusebian list; the printed editions place it later. "
            "The book closes with the Nineteenth Dynasty, whose last king Thuoris Manetho equates with Polybus, husband of Alcandra in the "
            "Odyssey, 'in whose reign Troy was taken'.</p>\n\n"
            "<p>Gap: the Eighteenth Dynasty is not included. Syncellus breaks both versions of it into pieces and spreads them, with his own "
            "arguments about Joseph and Moses, over fols. 5v, 9r and 10r-10v of this manuscript; those pieces have not yet been mapped line by line.</p>"
        ),
        "translator_notes": SYN_TR_NOTES,
        "translation": secs,
        "verification": {
            "scan_source": f"Bibliothèque nationale de France, Gallica, Grec 1764 ({B_VIEWER}), IIIF images 9 (fols. 4v, 5r), 14 (fol. 10r) and 15 (fol. 10v), single pages cropped from the microfilm openings",
            "scan_license": GALLICA_LICENSE,
            "scan_manuscript": "Paris, BnF, grec 1764, parchment, 143 fols., 11th century, George Syncellus, Ecloga chronographica (acephalous; from Istanbul, bought 1687)",
            "scan_mapping": "Read on the page images: each dynasty located by its heading and opening words and recorded with line numbers in the section notes",
            "scan_mapping_urls": [B_VIEWER, "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc21908z"],
            "scan_local_paths": local,
            "original_text_source": f"C. Müller, FHG II (1848) pp. 560-570 and 581, via DFHG (http://www.dfhg-project.org/DFHG/api.php?author=MANETHO%20SEBENNYTA), corrected against the print ({FHG_ARCHIVE})",
            "original_text_license": "edition public domain (1848); DFHG digital text CC BY-NC-SA 4.0 (as stated on dfhg-project.org)",
            "translation_source": f"W. G. Waddell, Manetho (Loeb Classical Library 350, 1940), LacusCurtius transcription {WADDELL_URL}, checked against {WADDELL_SCAN}",
            "translation_license": "public domain in the US: 1940 copyright not renewed (no renewal for Waddell or Manetho in the Copyright Office renewal records for 1966-1969, NYPL CCE renewals data; LacusCurtius states the same); translator died 1945",
            "translator": "W. G. Waddell (1940)",
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "title": entry["title"], "author_id": "manetho", "language": "Greek",
        "era": "Hellenistic", "tradition": "egyptian", "category": "history",
        "date_approx": "c. 280 BCE (Manetho); epitomes 3rd-4th c. AD; Syncellus c. 810 AD; manuscript 11th c.", "century": -3,
        "source": entry["source"], "description": entry["description"],
        "themes": ["manetho", "egypt", "dynasties", "pharaohs", "sesostris", "labyrinth", "hyksos", "shepherd-kings", "troy", "syncellus", "king-list", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p, "caption": "Paris gr. 1764 fol. " + p.split("-f")[-1].replace(".jpg", "").lstrip("0")} for p in local]},
    }
    return entry, row


def build_gods(force):
    p11, p12 = scan_A(11, force), scan_A(12, force)
    g = dfhg(2)
    head, rest = g.split(" Μανεθῶ ὁ Σεβεννύτης", 1)
    rest = "Μανεθῶ ὁ Σεβεννύτης" + rest
    narr, table = rest.split(" Αἰγυπτίων αʹ ἐβασίλευσεν", 1)
    table = "Αἰγυπτίων αʹ ἐβασίλευσεν" + table
    gods, demi = table.split(" ζʹ Ὦρος", 1)
    demi = "ζʹ Ὦρος" + demi
    assert head == "Περὶ τῆς τῶν Αἰγυπτίων ἀρχαιολογίας.", head
    w = waddell("book1.html", "Fragment_3")
    assert w[0] == "On the Antiquity of Egypt" and w[2] == "The First Dynasty of Egypt" and w[9] == "Demigods:", w
    secs = [
        {"section": "Fr. 3.1", "original_ref": "Waddell fr. 3 (Müller fr. 3); Paris gr. 1711 pp. 11-12",
         "original_text": head + "<br>" + narr, "text": w[0] + "<br>" + w[1], "scan_pages": [p11, p12],
         "scan_note": "The heading 'περὶ τῆς τῶν αἰγυπτίων ἀρχαιολογίας' is the last line of p. 11, below the table of the ten Chaldean "
                      "kings before the Flood. The text fills the first eight lines of p. 12: 'Μανεθῶ ὁ Σεβεννύτης ἀρχιερεὺς τῶν ἐν "
                      "Αἰγύπτῳ μιαρῶν ἱερῶν' to 'τῇ ἀληθείᾳ συμβιβάζοντες'. Checked on the image (Gallica " + A_VIEWER + ", images 19 and 20)."},
        {"section": "Fr. 3.2", "original_ref": "Waddell fr. 3 (Müller fr. 3); Paris gr. 1711 p. 12",
         "original_text": gods, "text": "<br>".join(w[2:9]), "scan_pages": [p12],
         "scan_note": "P. 12, the table below the text: each row begins 'Αἰγυπτίων' in the left column, then the numeral and "
                      "'ἐβασίλευσεν' with the god's name, and the years at the right. The gods are rows α' Ἥφαιστος ('πρώτη δυναστεία') "
                      "to the row of Typhon. The manuscript numbers the rows α'-ις' and leaves row ς' without a name, so Typhon stands at ζ'; "
                      "Müller renumbers (his note: 'pro η', θ' scripsimus ζ', θ''). Checked on the image."},
        {"section": "Fr. 3.3", "original_ref": "Waddell fr. 3 (Müller fr. 3); Paris gr. 1711 p. 12",
         "original_text": demi, "text": "<br>".join(w[9:]), "scan_pages": [p12],
         "scan_note": "P. 12, lower rows of the same table: 'Ὦρος ἡμίθεος' to 'Ζεὺς ἡμίθεος', each name followed by 'ἡμίθεος'. "
                      "Below the table Syncellus' own text resumes with a starred line 'γενέσεως κόσμου ἔτη ... ἐγρηγόρων παράβασις'. "
                      "Checked on the image."},
    ]
    tid = PREFIX + "gods-and-demigods-syncellus"
    entry = {
        "id": tid, "slug": tid,
        "title": "Manetho on the Reigns of the Gods and Demigods (George Syncellus)",
        "language": "Greek (Müller 1848) / English (Waddell 1940)",
        "source": "Paris gr. 1711 (11th c.), pp. 11-12, via Gallica IIIF + Müller FHG II Greek (DFHG, checked against the print) + Waddell English (Loeb 1940, public domain)",
        "description": "Manetho's list of the gods who ruled Egypt before men, from Hephaestus (Ptah) for 9000 years to Typhon, and of the demigods "
                       "Horus to Zeus, as quoted by George Syncellus, on the page of Paris gr. 1711 that carries it.",
        "introduction": (
            "<p>Before the thirty dynasties of human kings, Manetho set reigns of gods, demigods and spirits of the dead, totalling many "
            "thousands of years. The Byzantine chronicler George Syncellus (c. 810 AD), who rejected these figures as invented, quotes "
            "the list near the start of his chronicle: six gods ruling for 11,985 years, the first of them Hephaestus (the Greek name for "
            "Ptah) for 9000 years, followed by Helios, Agathodaemon, Cronos, Osiris and Isis, and Typhon (Seth), then nine demigods from "
            "Horus to Zeus. Syncellus also reports how later Christian chronographers reduced Hephaestus' 9000 years to 727¾ by treating "
            "them as lunar months.</p>\n\n"
            "<p>The page is p. 12 of Paris, Bibliothèque nationale de France, grec 1711, an 11th-century manuscript whose first part "
            "(pp. 1-230) contains Syncellus. The list is laid out as a table; the page before it (p. 11) ends with the matching table of "
            "the ten Chaldean kings before the Flood from Berossus, and its last line is the heading of this passage. The images are from "
            "the BnF microfilm.</p>\n\n"
            "<p>Syncellus also preserves, from the Byzantine monk Panodorus, an attempt to convert these reigns into solar years "
            "(Waddell fr. 2); that passage is not included here.</p>"
        ),
        "translator_notes": SYN_TR_NOTES + [
            "The figures 727¾, 80⅙ and so on are the reduced reigns given in the table; the 9000 years of Hephaestus are Manetho's.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": f"Bibliothèque nationale de France, Gallica, Grec 1711 ({A_VIEWER}), IIIF images 19 (right page, p. 11) and 20 (left page, p. 12)",
            "scan_license": GALLICA_LICENSE,
            "scan_manuscript": "Paris, BnF, grec 1711, parchment, 11th century; pp. 1-230 George Syncellus, Ecloga chronographica; then Theophanes, Leo Grammaticus and others",
            "scan_mapping": "Read on the page images: heading on p. 11 last line, text and table on p. 12, recorded in the section notes",
            "scan_mapping_urls": [A_VIEWER, "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc21847c"],
            "scan_local_paths": [p11, p12],
            "original_text_source": f"C. Müller, FHG II (1848) pp. 530-531 (fr. 3), via DFHG, corrected against the print ({FHG_ARCHIVE})",
            "original_text_license": "edition public domain (1848); DFHG digital text CC BY-NC-SA 4.0 (as stated on dfhg-project.org)",
            "translation_source": f"W. G. Waddell, Manetho (Loeb Classical Library 350, 1940), fr. 3, LacusCurtius transcription {WADDELL_URL}",
            "translation_license": "public domain in the US: 1940 copyright not renewed (no renewal for Waddell or Manetho in the Copyright Office renewal records for 1966-1969, NYPL CCE renewals data; LacusCurtius states the same); translator died 1945",
            "translator": "W. G. Waddell (1940)",
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "title": entry["title"], "author_id": "manetho", "language": "Greek",
        "era": "Hellenistic", "tradition": "egyptian", "category": "history",
        "date_approx": "c. 280 BCE (Manetho); Syncellus c. 810 AD; manuscript 11th c.", "century": -3,
        "source": entry["source"], "description": entry["description"],
        "themes": ["manetho", "egypt", "gods", "demigods", "antediluvian", "hephaestus", "osiris", "syncellus", "king-list", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p11, "caption": "Paris gr. 1711 p. 11"}, {"file": p12, "caption": "Paris gr. 1711 p. 12"}]},
    }
    return entry, row


# ---------------------------------------------------------------------------

AUTHORS = [{
    "id": "manetho", "name": "Manetho of Sebennytus", "dates": "fl. c. 285-246 BCE", "century": -3,
    "era": "Hellenistic", "tradition": "egyptian", "language": "Greek",
    "bio": "Egyptian priest of Sebennytus who wrote a history of Egypt in Greek (Aegyptiaca) under the first Ptolemies; "
           "his division of Egypt's kings into thirty dynasties is still used.",
}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)

    built = []  # (order, entry, row)
    built.append((10, *build_gods(args.force)))
    built.append((20, *build_syncellus_book1(args.force)))
    built.append((30, *build_syncellus_book2a(args.force)))
    built.append((50, *build_josephus(args.force)))
    built.append((60, *build_syncellus_book3(args.force)))

    rows = []
    for i, (_, e, r) in enumerate(sorted(built, key=lambda x: x[0]), 1):
        r["order"] = i
        (PUB_DIR / f"{e['id']}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(r)
        print(f"  wrote {e['id']} ({len(e['translation'])} sections)")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Manetho, History of Egypt",
            "group": "Egypt",
            "date_sort": -280,
            "author_name": "Manetho of Sebennytus (c. 280 BCE), quoted by Josephus and Syncellus",
            "source_url": LAUR_VIEWER,
            "critical_edition": "Niese 1889 (Josephus, via Perseus)",
            "translator_name": "William Whiston (1737)",
            "original_lang_label": "Greek",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "manetho aegyptiaca history of egypt hyksos shepherd kings avaris dynasties pharaohs josephus syncellus",
            "description": "Manetho's history of Egypt, written in Greek about 280 BCE, survives only in quotations. "
                           "This shelf shows them on the manuscript pages that carry them.",
        },
        "texts": rows,
        "authors": AUTHORS,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
