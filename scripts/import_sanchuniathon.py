#!/usr/bin/env python3
"""
import_sanchuniathon.py - Philo of Byblos, Phoenician History (the "Sanchuniathon"), as quoted by
Eusebius, Praeparatio evangelica 1.9.20-1.10.55, on the pages of the Arethas codex, Paris gr. 451
(written in 914 AD).

Six entries (chapter groups), 66 sections (one per Dindorf section, 1.9.20 ... 1.10.55).

Chain of evidence:
  1. SCAN     Paris, BnF, grec 451, fols. 204v-213v (Eusebius, PE books 1-5 on fols. 188-322; copied
              in 914 by the scribe Baanes for Arethas of Caesarea). Gallica ark:/12148/btv1b84701396,
              IIIF via openapi.bnf.fr; colour digitization from the original. Gallica terms:
              non-commercial reuse with credit "Source gallica.bnf.fr / BnF".
  2. MAPPING  By eye on the downloaded images: the first and last words of each page from fol. 204v
              to 213v were read and found in Dindorf's text (FOLIO_NOTES below). Each section points
              at the page(s) that carry it, derived from those page breaks; a section that runs
              across a page break lists both pages.
  3. GREEK    W. Dindorf, Eusebii Caesariensis opera vol. 1 (Leipzig: Teubner, 1867) pp. 37-53, digital
              text from First1KGreek (OpenGreekAndLatin) tlg2018.tlg001.1st1K-grc1 (CC BY-SA 4.0).
              The digital text was proofread word by word against the printed pages (archive.org
              bub_gb_5yRMTBxhA74C); 133 corrections (OCR errors, dropped words, page-margin letters)
              are listed in data/sources/sanchuniathon/dindorf-proofread-fixes.txt and asserted here.
  4. ENGLISH  E. H. Gifford, Eusebii Pamphili Evangelicae Praeparationis libri XV, vol. 3 part 1
              (Oxford, 1903), public domain. Transcription by P. Kirby and R. Pearse (tertullian.org,
              2003, public domain), checked word by word against the OCR of the 1903 printing
              (archive.org eusebius-preparation-for-the-gospel-full-work-gifford-1903-trans); the
              disagreements were settled on the page images (EN_FIXES). Gifford's marginal labels
              (PORPHYRY, PHILO) and footnote numbers are omitted.

Usage:
    python3 scripts/import_sanchuniathon.py           # build
    python3 scripts/import_sanchuniathon.py --force   # re-download scans
"""

import argparse
import html
import io
import json
import re
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "sanchuniathon"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
N = lambda s: unicodedata.normalize("NFC", s)

ARK = "btv1b84701396"
GALLICA = f"https://gallica.bnf.fr/ark:/12148/{ARK}"
F1K_URL = "https://github.com/OpenGreekAndLatin/First1KGreek/blob/master/data/tlg2018/tlg001/tlg2018.tlg001.1st1K-grc1.xml"
DINDORF_SCAN = "https://archive.org/details/bub_gb_5yRMTBxhA74C"
GIFFORD_WEB = "https://www.tertullian.org/fathers/eusebius_pe_01_book1.htm"
GIFFORD_SCAN = "https://archive.org/details/eusebius-preparation-for-the-gospel-full-work-gifford-1903-trans"

FOLIOS = ["204v", "205r", "205v", "206r", "206v", "207r", "207v", "208r", "208v", "209r",
          "209v", "210r", "210v", "211r", "211v", "212r", "212v", "213r", "213v"]

# What was read on each page (first words / last words, with the sections they belong to).
FOLIO_NOTES = {
    "204v": "Fol. 204v: in the lower half, after a heading in majuscule 'ὅτι νεώτερα τῷ βίῳ παρεισῆκται τὰ παρὰ τῶν θεῶν παρὰ τοῖς λοιποῖς τεθρυλημένα', 1.9.20 opens with a large initial 'Ἱστορεῖ δὲ ταῦτα Σαγχουνιάθων, ἀνὴρ παλαιότατος'; 1.9.21 begins near the foot, marked ÷ in the margin, 'ἱστορεῖ δὲ τὰ περὶ Ἰουδαίων ἀληθέστατα'; the page ends 'τὰ συμ-'.",
    "205r": "Fol. 205r: begins '-φωνότατα, Σαγχουνιάθων ὁ Βηρύτιος, εἰληφὼς τὰ ὑπομνήματα παρὰ Ἱερομβάλου' (1.9.21) and ends with the last words of 1.9.22 'δέχου δὲ καὶ τούτων ἐκ τῶν ἐγγράφων τὰς ἀποδείξεις'.",
    "205v": "Fol. 205v: begins with a large initial at 1.9.23 'Ὁ δὴ Φίλων εἰς ἐννέα βίβλους τὴν πᾶσαν τοῦ Σαγχουνιάθωνος πραγματείαν' and ends in 1.9.26 '...καὶ τέλος ἐπιθεὶς τῇ πραγματείᾳ τὸν κατ’ ἀρχὰς μῦθον'.",
    "206r": "Fol. 206r: begins 'καὶ τὰς ἀλληγορίας ἐκποδὼν ποιησάμενος, ἐξηνύσατο τὴν πρόθεσιν' (1.9.26) and ends in 1.9.29 '...τοῖς κοσμικοῖς στοιχείοις καί τισι τῶν νομιζομένων θεῶν τὰς'.",
    "206v": "Fol. 206v: begins 'ὀνομασίας ἐπέθεσαν· φυσικοὺς δὲ ἥλιον καὶ σελήνην' (1.9.29); the last line, with a large initial, starts 1.10.4 'Καὶ τοῦ ἀέρος διαυγάσαντος διὰ πύρωσιν καὶ τῆς'.",
    "207r": "Fol. 207r: begins 'θαλάσσης καὶ τῆς γῆς ἐγένετο πνεύματα καὶ νέφη' (1.10.4) and ends in 1.10.7 '...εὑρεῖν δὲ τὸν Αἰῶνα τὴν ἀπὸ δένδρων τροφήν. ἐκ τούτων τοὺς'.",
    "207v": "Fol. 207v: begins 'γενομένους' with 'Γένος καὶ Γενεὰν καὶ οἰκῆσαι τὴν Φοινίκην' (1.10.7) and ends in 1.10.10 '...ῥαγδαίων δὲ γενομένων ὄμβρων καὶ πνευμάτων παρατριβέντα τὰ ἐν τῇ'.",
    "208r": "Fol. 208r: begins 'Τύρῳ δένδρα πῦρ ἀνάψαι καὶ τὴν αὐτόθι ὕλην καταφλέξαι' (1.10.10) and ends in 1.10.12 '...ναὸν ζυγοφορούμενον ἐν Φοινίκῃ· παρὰ δὲ Βυβλίοις'.",
    "208v": "Fol. 208v: begins 'ἐξαιρέτως θεῶν ὁ μέγιστος ὀνομάζεται' (end of 1.10.12) and ends in 1.10.16 '...ποιεῖται ἐξ αὐτῆς παῖδας τέσσαρας, Ἦλον τὸν καὶ Κρόνον'.",
    "209r": "Fol. 209r: begins 'καὶ Βαίτυλον καὶ Δαγὼν, ὅς ἐστι Σίτων, καὶ Ἄτλαντα' (1.10.16) and ends at the start of 1.10.20 'μετὰ ταῦτα τὸν ἀδελφὸν τὸν ἴδιον'.",
    "209v": "Fol. 209v: begins 'Ἄτλαντα ὑπονοήσας ὁ Κρόνος μετὰ γνώμης τοῦ Ἑρμοῦ' (1.10.20) and ends at the start of 1.10.25 'ὁ δὲ Δαγὼν, ἐπειδὴ εὗρε σῖτον'.",
    "210r": "Fol. 210r: begins 'καὶ ἄροτρον, ἐκλήθη Ζεὺς Ἀρότριος' (1.10.25) and ends at the start of 1.10.31 'Ἀστάρτη δὲ ἡ μεγίστη καὶ Ζεὺς'.",
    "210v": "Fol. 210v: begins 'Δημαροῦς καὶ Ἄδωδος βασιλεὺς θεῶν ἐβασίλευον τῆς χώρας' (1.10.31) and ends at the start of 1.10.37 'τὸ δὲ' after '...δύο δὲ ὡς ὑφειμένα'.",
    "211r": "Fol. 211r: begins 'σύμβολον ἦν, ἐπειδὴ Κρόνος κοιμώμενος ἔβλεπε' (1.10.37); the main text ends in 1.10.40 '...ἔνθεν Ἡσίοδος οἵ τε κυκλικοὶ περιηχημένοι θεογονίας καὶ γιγαντο-'. A marginal scholion stands in the lower right corner.",
    "211v": "Fol. 211v: begins '-μαχίας καὶ Τιτανομαχίας ἔπλασαν ἰδίας καὶ ἐκτομάς' (1.10.40) and ends in 1.10.44 '...κατεσφάττοντο δὲ οἱ διδόμενοι μυστικῶς. Κρόνος τοίνυν, ὃν οἱ Φοίνικες'.",
    "212r": "Fol. 212r: begins 'Ἦλον προσαγορεύουσι, βασιλεύων τῆς χώρας' (1.10.44) and ends in 1.10.47 '...ἀλλὰ καὶ αὔξησιν ἐπιδέχεσθαι μείζονα πέφυκε· καὶ'.",
    "212v": "Fol. 212v: begins 'ἐπειδὰν τὸ ὡρισμένον μέτρον πληρώσῃ, εἰς ἑαυτὸν ἀναλίσκεται' (1.10.47) and ends in 1.10.51 '...καὶ ἔστι τὸ πᾶν σχῆμα ὡς τὸ παρ’ ἡμῖν θῆτα'.",
    "213r": "Fol. 213r: begins 'τὸν μὲν κύκλον κόσμον μηνύοντες' (1.10.51); 1.10.52 'καὶ Ζωροάστρης δὲ ὁ μάγος' (line 2, marked ÷); 1.10.53 'πάντες δὲ τὰς ἀφορμὰς παρὰ Ταυθοῦ λαβόντες' (line 12, marked ÷ at line 13); 1.10.54 'ἀλλὰ γὰρ τὰ μὲν τῆς Φοινίκων θεολογίας' (line 18); 1.10.55 'ὅτι δὲ μὴ' at the end of line 21, with a large marginal sign at 'μῦθοι ταῦτα'; the page ends '...τό τε πιστὸν τῶν λόγων'.",
    "213v": "Fol. 213v: begins 'ἐπαγόμεναι ἀπὸ τῆς εἰσέτι δεῦρο ἐν ταῖς κατὰ Φοινίκην πόλεσι' (1.10.55); book 1 ends on line 8 'ἐπιθεωρῆσαι' and is followed by the subscription and the list of chapters of book 2.",
}

# Dindorf section -> folios (from the page breaks above)
PAGES = {
    "9.20": ["204v"], "9.21": ["204v", "205r"], "9.22": ["205r"],
    "9.23": ["205v"], "9.24": ["205v"], "9.25": ["205v"], "9.26": ["205v", "206r"],
    "9.27": ["206r"], "9.28": ["206r"], "9.29": ["206r", "206v"],
    "9.30": ["206v"], "10.1": ["206v"], "10.2": ["206v"], "10.3": ["206v"], "10.4": ["206v", "207r"],
    "10.5": ["207r"], "10.6": ["207r"], "10.7": ["207r", "207v"],
    "10.8": ["207v"], "10.9": ["207v"], "10.10": ["207v", "208r"],
    "10.11": ["208r"], "10.12": ["208r", "208v"],
    "10.13": ["208v"], "10.14": ["208v"], "10.15": ["208v"], "10.16": ["208v", "209r"],
    "10.17": ["209r"], "10.18": ["209r"], "10.19": ["209r"], "10.20": ["209r", "209v"],
    "10.21": ["209v"], "10.22": ["209v"], "10.23": ["209v"], "10.24": ["209v"], "10.25": ["209v", "210r"],
    "10.26": ["210r"], "10.27": ["210r"], "10.28": ["210r"], "10.29": ["210r"], "10.30": ["210r"], "10.31": ["210r", "210v"],
    "10.32": ["210v"], "10.33": ["210v"], "10.34": ["210v"], "10.35": ["210v"], "10.36": ["210v"], "10.37": ["210v", "211r"],
    "10.38": ["211r"], "10.39": ["211r"], "10.40": ["211r", "211v"],
    "10.41": ["211v"], "10.42": ["211v"], "10.43": ["211v"], "10.44": ["211v", "212r"],
    "10.45": ["212r"], "10.46": ["212r"], "10.47": ["212r", "212v"],
    "10.48": ["212v"], "10.49": ["212v"], "10.50": ["212v"], "10.51": ["212v", "213r"],
    "10.52": ["213r"], "10.53": ["213r"], "10.54": ["213r"], "10.55": ["213r", "213v"],
}
SECTIONS = [f"9.{n}" for n in range(20, 31)] + [f"10.{n}" for n in range(1, 56)]
assert set(PAGES) == set(SECTIONS)

# English: first words of each Dindorf section in Gifford's translation
EN_MARKS = {
    "9.20": "Now the historian of this subject", "9.21": "'Of the affairs of the Jews",
    "9.22": "So wrote the author before mentioned", "9.23": "Philo then, having divided",
    "9.24": "'These things being so", "9.25": "After these statements he finds fault",
    "9.26": "'But the most recent of the writers", "9.27": "Next to this he says:",
    "9.28": "And after other statements:", "9.29": "And again after other statements he adds:",
    "9.30": "Philo having explained these points", "10.1": "'The first principle of the universe",
    "10.2": "which some say is mud", "10.3": "Such was their cosmogony",
    "10.4": "'And when the air burst into light", "10.5": "Such is their theory of the generation",
    "10.6": "Next to this, after mentioning the names", "10.7": "He adds also:",
    "10.8": "And after this he charges the Greeks", "10.9": "Afterwards he says:",
    "10.10": "Then he says: 'Hypsuranius", "10.11": "'But when Hypsuranius and Ous",
    "10.12": "And he was also called Zeus Meilichios", "10.13": "'These two devised the addition",
    "10.14": "'From Misor was born Taautus", "10.15": "'And from them is born Epigeius",
    "10.16": "'And Uranus, having succeeded", "10.17": "'But Uranus, after he had left her",
    "10.18": "'To Kronos are born children", "10.19": "And in his house she gave birth",
    "10.20": "'Soon after this he became suspicious", "10.21": "'And Kronos, having a son Sadidus",
    "10.22": "'But as time went on Uranus", "10.23": "And when Uranus knew it",
    "10.24": "and again to the same there were born of Rhea", "10.25": "And Dagon, after he discovered corn",
    "10.26": "'In Peraea also", "10.27": "'And from Pontus is born Sidon",
    "10.28": "'Then again Uranus makes war", "10.29": "'And in the thirty-second year",
    "10.30": "This, then, is the story of Kronos", "10.31": "'But Astarte, the greatest goddess",
    "10.32": "And the Phoenicians say that Astarte is Aphrodite", "10.33": "But on the occurrence of a pestilence",
    "10.34": "And not long after another of his sons", "10.35": "And after this Kronos gives the city Byblos",
    "10.36": "'But before this the god Tauthus", "10.37": "'And the symbol meant",
    "10.38": "'And when Kronos came into the South", "10.39": "'All these stories Thabion",
    "10.40": "Then again afterwards he adds:", "10.41": "'But our ears having grown up",
    "10.42": "Let these suffice as quotations", "10.43": "'Tauthus, whom the Egyptians call",
    "10.44": "And soon after he says:", "10.45": "Again see what the same author",
    "10.46": "'The nature then of the dragon", "10.47": "It is also most long-lived",
    "10.48": "'We have spoken more fully", "10.49": "'Epeïs also (who is called",
    "10.50": "'Epeïs here intimates", "10.51": "'Moreover the Egyptians, describing",
    "10.52": "'Zoroaster also the Magian", "10.53": "From Tauthus, as is said above",
    "10.54": "Such then is the character of the theology", "10.55": "It must be manifest that these are not fables",
}
# transcription vs 1903 printing (checked on the page images of the printed book)
EN_FIXES = [
    ("Thoyth", "Thöyth"), ("connexion Mot was produced", "connexion Môt was produced"),
    ("Ousous", "Ousöus"), ("on the sea; and be consecrated", "on the sea; and he consecrated"),
    ("race of llypsuranius", "race of Hypsuranius"), ("were bom two brethren", "were born two brethren"),
    ("Agrueros", "Agruëros"), ("called Ge", "called Gé"), ("sister Ge,", "sister Gé,"),
    ("account Ge was", "account Gé was"), ("but Ge repelled", "but Gé repelled"), ("behalf of Ge.", "behalf of Gé."),
    ("named Demarus.", "named Demarûs."), ("sisters, Ehea and Dione", "sisters, Rhea and Dione"),
    ("called ledud", "called Iedud"), ("eternal, uncreated,", "eternal, uncreate,"),
]

ENTRIES = [
    ("testimony", 1, "9.20", "9.30",
     "Sanchuniathon and Philo of Byblos: Porphyry's testimony and Philo's preface (Eusebius, Praeparatio evangelica 1.9.20-30)",
     "Eusebius introduces Sanchuniathon of Berytus, older than the Trojan War, whose Phoenician History Philo of Byblos translated into Greek; Porphyry's testimony that he drew on the records of the priest Hierombalus; and Philo's preface on Taautus, inventor of writing, and on the later priests who turned history into allegory."),
    ("cosmogony", 2, "10.1", "10.8",
     "Sanchuniathon: the Phoenician cosmogony and the first worship (Eusebius, Praeparatio evangelica 1.10.1-8)",
     "The beginning of all things in Philo's translation of Sanchuniathon: dark air and chaos, the wind's desire, Mot and the egg-shaped Zophasemin, the 'observers of heaven', thunder waking the first living things, and the first men who worshipped the plants of the earth and the sun as Beelsamen, lord of heaven."),
    ("first-inventors", 3, "10.9", "10.14",
     "Sanchuniathon: the first generations and the inventors of the arts (Eusebius, Praeparatio evangelica 1.10.9-14)",
     "The generations after Aeon and Protogonus: Light, Fire and Flame who discovered fire, the giants who gave their names to Lebanon and Mount Cassius, Hypsuranius who built huts at Tyre and Ousoos who first went to sea, Chrysor who invented iron-working and sailing, the builders of brick, the shepherds, Misor and Sydyk who found salt, and Taautus who invented writing."),
    ("kronos", 4, "10.15", "10.30",
     "Sanchuniathon: Uranus, Ge and the reign of Kronos (Eusebius, Praeparatio evangelica 1.10.15-30)",
     "Uranus and Ge, the war of their son Elus or Kronos against his father, the founding of Byblos as the first city, the baetyls or living stones, the children of Kronos and Astarte, Dagon who found grain and the plough, and the mutilation of Uranus near springs and rivers."),
    ("astarte-and-taautus", 5, "10.31", "10.41",
     "Sanchuniathon: Astarte, the deeds of Kronos and the symbols of Taautus (Eusebius, Praeparatio evangelica 1.10.31-41)",
     "Astarte with the head of a bull and the star she found and dedicated at Tyre, Kronos' sacrifice of his only son and his gifts of cities, the four eyes and six wings Taautus devised as the insignia of Kronos, the gift of Egypt to Taautus, the records kept by the Cabeiri, and Philo's complaint that the Greeks turned these stories into myth."),
    ("taautus-and-the-serpent", 6, "10.42", "10.55",
     "Philo of Byblos on Taautus, royal sacrifice and the serpent, with Eusebius' conclusion (Eusebius, Praeparatio evangelica 1.10.42-55)",
     "Further passages of Philo: Taautus who first set religion in order, the ancient custom of sacrificing a ruler's beloved son in times of danger, and the serpent, which Taautus held divine, the good daemon of the Phoenicians and the Egyptian Kneph, followed by Eusebius' closing words on the Phoenician theology."),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def scan(folio, force, idx):
    path = SCAN_DIR / f"paris-gr-451-f{folio.zfill(4)}.jpg"
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"https://openapi.bnf.fr/iiif/image/v3/ark:/12148/{ARK}/f{idx[folio]}/full/,2400/0/default.jpg")))
    img.convert("RGB").save(path, quality=85)
    return path


def canvas_index():
    m = json.loads((SRC / "grec451-manifest.json").read_text(encoding="utf-8"))
    out = {}
    for i, c in enumerate(m["items"]):
        lab = c["label"].get("fr", c["label"].get("none", [""]))[0]
        out[lab] = i + 1
    return out


def greek():
    root = ET.parse(SRC / "tlg2018.tlg001.1st1K-grc1.xml").getroot()
    g = {}
    for b in root.iter(f"{TEI}div"):
        if b.get("subtype") == "book" and b.get("n") == "1":
            for c in b.iter(f"{TEI}div"):
                if c.get("subtype") == "chapter" and c.get("n") in ("9", "10"):
                    for s in c.iter(f"{TEI}div"):
                        k = f"{c.get('n')}.{s.get('n')}"
                        if s.get("subtype") == "section" and k in PAGES:
                            g[k] = N(re.sub(r"\s+", " ", "".join(s.itertext())).strip())
    assert set(g) == set(SECTIONS), set(SECTIONS) - set(g)
    n = 0
    for line in (SRC / "dindorf-proofread-fixes.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        k, a, b = N(line).split("|")
        assert g[k].count(a) == 1, (k, a)
        g[k] = g[k].replace(a, b)
        n += 1
    for k in g:
        g[k] = re.sub(r"\s+", " ", g[k].replace("᾿", "’").replace("᾿", "’").replace("‟", "“")).strip()
        assert not re.search(r"[A-Za-z0-9]", g[k]), (k, g[k])
        g[k] = g[k].replace("* * *", '<span class="lacuna">* * *</span>')
    return g, n


def english():
    raw = (SRC / "gifford" / "eusebius_pe_01_book1.htm").read_text(encoding="utf-8", errors="replace")
    i = raw.index("Now the historian of this subject is Sanchuniathon")
    j = raw.index("[Selected footnotes", i)
    paras = []
    for p in re.split(r"<P[^>]*>|<p[^>]*>", raw[i:j]):
        p = re.sub(r'<A HREF="#\d+"><SUP>\d+</SUP></A>', "", p)
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", p))).strip()
        if t and t != "CHAPTER X":
            paras.append(t.replace("[PORPHYRY] ", "").replace("[PHILO] ", ""))
    text = " ".join(paras)
    for a, b in EN_FIXES:
        assert a in text, a
        text = text.replace(a, b)
    assert not re.search(r"\d", text.replace("thirty-second", "")), re.findall(r".{20}\d.{5}", text)
    pos = []
    for k in SECTIONS:
        assert text.count(EN_MARKS[k]) == 1, (k, text.count(EN_MARKS[k]))
        pos.append(text.index(EN_MARKS[k]))
    assert pos == sorted(pos) and pos[0] == 0
    e = {}
    for k, a, b in zip(SECTIONS, pos, pos[1:] + [len(text)]):
        e[k] = text[a:b].strip()
    assert e["10.55"].endswith("examine carefully the case of the Egyptians.")
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    g, nfix = greek()
    e = english()
    idx = canvas_index()
    paths = {f: scan(f, args.force, idx) for f in FOLIOS}
    rel = {f: f"{KEY}/{p.name}" for f, p in paths.items()}

    intro_common = (
        "<p>Philo of Byblos, a Phoenician grammarian writing in Greek around 100 AD, claimed to have translated the <em>Phoenician History</em> of Sanchuniathon of Berytus, "
        "a priestly writer said to have lived before the Trojan War, who drew on the city records and the temple inscriptions of Phoenicia and on the writings of Taautus (Thoth). "
        "Philo's work survives only in the long quotations that Eusebius of Caesarea copied into book 1 of his <em>Preparation for the Gospel</em> (c. 313 AD), taken partly through the philosopher Porphyry. "
        "It is the fullest account of Phoenician myth in Greek, and since the discovery of the Ugaritic tablets (14th-13th c. BCE) several of its gods and stories, such as El, Dagon, the succession of divine kings and the castration of the sky god, are known to go back to Bronze Age Canaan.</p>\n\n"
        "<p>The manuscript shown is Paris, Bibliothèque nationale de France, grec 451, written in 914 AD by the scribe Baanes for Arethas, archbishop of Caesarea in Cappadocia; it is the oldest manuscript of books 1-5 of the <em>Preparation</em>. "
        "The passage runs from fol. 204v to fol. 213v. Each section is one of Dindorf's numbered sections and points at the page(s) that carry it; the page breaks were read on the images and are recorded in each note.</p>"
    )
    notes = [
        "Greek: W. Dindorf's Teubner edition (1867), from the First1KGreek digital text, proofread against the printed pages. The manuscript's wording differs from the edition in small details; the Greek shown is the edition, not a transcription of the page.",
        "English: E. H. Gifford's translation (Oxford, 1903). Where a Greek section begins in the middle of an English sentence, the English is divided at the corresponding clause.",
        "Asterisks mark a gap that Dindorf indicates in the Greek of 1.10.36; Gifford marks it with dots.",
    ]
    rows = []
    for slug, order, a, b, title, desc in ENTRIES:
        keys = SECTIONS[SECTIONS.index(a):SECTIONS.index(b) + 1]
        fols = [f for f in FOLIOS if any(f in PAGES[k] for k in keys)]
        secs = []
        for k in keys:
            fp = PAGES[k]
            note = " ".join(FOLIO_NOTES[f] for f in fp)
            lead = f"1.{k} runs from fol. {fp[0]} to fol. {fp[1]}. " if len(fp) == 2 else f"1.{k} is on fol. {fp[0]}. "
            secs.append({
                "section": f"1.{k}",
                "original_ref": f"Eusebius, PE 1.{k} (Dindorf); Paris gr. 451 fol. {' and '.join(fp)}",
                "original_text": f"<sup>{k}</sup>{g[k]}",
                "text": f"<sup>{k}</sup>{e[k]}",
                "scan_pages": [rel[f] for f in fp],
                "scan_note": lead + note + " Checked on the image. Viewer: " + GALLICA + f"/f{idx[fp[0]]}.item",
            })
        tid = PREFIX + slug
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Greek (Dindorf 1867) / English (Gifford 1903)",
            "source": "Paris gr. 451 (Arethas codex, 914 AD) via Gallica + Dindorf Greek (First1KGreek, proofread) + Gifford English (1903)",
            "description": desc,
            "introduction": intro_common + f"\n\n<p>This entry covers sections 1.{a} to 1.{b}, on fols. {fols[0]} to {fols[-1]}.</p>",
            "translator_notes": notes,
            "translation": secs,
            "verification": {
                "scan_source": f"Bibliothèque nationale de France, Gallica: Grec 451, {GALLICA} (IIIF openapi.bnf.fr), fols. {fols[0]}-{fols[-1]}",
                "scan_license": "Gallica terms: free non-commercial reuse with the credit 'Source gallica.bnf.fr / BnF'",
                "scan_manuscript": "Paris, BnF, grec 451 (written 914 AD by Baanes for Arethas of Caesarea), Eusebius, Praeparatio evangelica books 1-5 on fols. 188-322",
                "scan_mapping": "Checked on the images: the first and last words of every page from fol. 204v to 213v were read and found in Dindorf's text; each section's folio(s) follow from those page breaks (see scan_note)",
                "scan_mapping_urls": [f"{GALLICA}/f{idx[f]}.item" for f in fols],
                "scan_local_paths": [rel[f] for f in fols],
                "original_text_source": f"W. Dindorf, Eusebii Caesariensis opera vol. 1 (Leipzig: Teubner, 1867) pp. 37-53, First1KGreek tlg2018.tlg001.1st1K-grc1 ({F1K_URL}), proofread against {DINDORF_SCAN} ({nfix} corrections)",
                "original_text_license": "edition public domain; First1KGreek digital text CC BY-SA 4.0",
                "translation_source": f"E. H. Gifford, Eusebii Pamphili Evangelicae Praeparationis libri XV, vol. 3 part 1 (Oxford: Clarendon Press, 1903), book 1 chapters 9-10; transcription {GIFFORD_WEB} checked against {GIFFORD_SCAN}",
                "translation_license": "public domain (published 1903)",
                "translator": "E. H. Gifford (1903)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order, "title": title, "author_id": "philo-of-byblos",
            "language": "Greek", "era": "Imperial", "tradition": "canaanite", "category": "sacred-text",
            "date_approx": "c. 100 AD (Philo of Byblos); c. 313 AD (Eusebius); 914 AD (Paris gr. 451)", "century": 2,
            "source": entry["source"], "description": desc,
            "themes": ["sanchuniathon", "philo-of-byblos", "phoenician", "canaanite", "cosmogony", "kronos", "eusebius", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": rel[f], "caption": f"Paris gr. 451, fol. {f}"} for f in fols]},
        })
        print(f"  {tid}: {len(secs)} sections, fols {fols[0]}-{fols[-1]}")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Sanchuniathon, Phoenician History",
            "group": "Levant & Israel", "date_sort": 100,
            "author_name": "Philo of Byblos (c. 100 AD), translating Sanchuniathon, in Eusebius",
            "source_url": GALLICA,
            "critical_edition": "W. Dindorf, Eusebii Caesariensis opera I (Teubner 1867), First1KGreek, proofread",
            "translator_name": "E. H. Gifford (1903)",
            "original_lang_label": "Greek · Dindorf",
            "original_lang_code": "grc", "edition_label": "",
            "search_terms": "sanchuniathon sanchoniathon philo byblos phoenician history eusebius praeparatio evangelica kronos elus uranus taautus thoth astarte dagon byblos tyre",
            "description": "The Phoenician account of the beginning of the world, the first inventors, and the reigns of Uranus, Kronos (El) and Astarte, from Philo of Byblos' Greek translation of Sanchuniathon, on the pages of the Arethas codex of Eusebius written in 914 AD.",
        },
        "texts": rows,
        "authors": [{
            "id": "philo-of-byblos", "name": "Philo of Byblos", "name_latin": "Herennius Philo Byblius",
            "dates": "c. 64-141 AD", "century": 2, "era": "Imperial", "tradition": "canaanite", "language": "Greek",
            "bio": "Phoenician grammarian and historian from Byblos who wrote in Greek; his Phoenician History, presented as a translation of the ancient writer Sanchuniathon, survives in quotations by Eusebius.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
