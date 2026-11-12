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
    e, r = build_josephus(args.force)
    built.append((50, e, r))

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
