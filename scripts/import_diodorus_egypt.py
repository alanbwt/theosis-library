#!/usr/bin/env python3
"""
import_diodorus_egypt.py - Diodorus Siculus, Library of History 1.10-1.29 and 1.44 (the Egyptian
account of the first men, the gods who ruled as kings, Isis and Osiris, the colonies sent out from
Egypt, and the years of gods and kings), each chapter linked to the pages of Vat. gr. 130 that carry it.

Six entries, 21 sections (one per chapter).

Chain of evidence:
  1. SCAN     Biblioteca Apostolica Vaticana, Vat. gr. 130 (parchment, mid-10th c., 28 lines a page;
              books 1-5 without the summary of book 1; siglum C in Vogel's edition), the oldest
              manuscript of books 1-5. DigiVatLib IIIF (digi.vatlib.it), black-and-white microfilm
              images, one opening per image. Each opening is split at the gutter into its two pages and
              the library's caption bar is cropped off. No folio numbers are legible on the images, so
              pages are cited as "DigiVatLib image NNNN, left/right page". Image 0004 shows book 1
              beginning on the right-hand page, after the 14th-century paper leaf with the note from
              Photius. Chosen over Laur. Plut. 70.1 (14th c., abbreviated text) and Paris gr. 1665
              (books 16-20 only).
  2. MAPPING  By eye on the downloaded images: for every page from image 0012 (right) to 0026 (right)
              and both pages of image 0040, the first and last two lines were read and found in Vogel's
              text (PAGE_BREAKS below, quoted in the edition's spelling where the copy agrees). Each
              chapter lists the pages that carry it; the sections on each page follow from those
              page breaks, never from text length.
  3. GREEK    F. Vogel, Diodori Bibliotheca historica vol. 1 (Leipzig: Teubner, 1888), Perseus
              canonical-greekLit tlg0060.tlg001.perseus-grc5 (CC BY-SA 4.0). Collated by machine with
              the OCR of the printed volume (archive.org diodoribibliothe01diod_0) and every flagged
              place checked on the page images; five corrections (GREEK_FIXES) restore Vogel's square
              brackets and fix transcription slips.
  4. ENGLISH  C. H. Oldfather, Diodorus of Sicily vol. 1 (Loeb Classical Library 279; London: Heinemann,
              Cambridge MA: Harvard University Press, 1933). Public domain in the US: no renewal of the
              1933 copyright appears in the Copyright Office renewal registrations for 1959-1962 (NYPL
              cce-renewals data, files 1959-1.tsv to 1962-1.tsv, cached in data/sources/diodorus-egypt/
              cce-renewals/: 0 entries for "Oldfather" or "Diodorus"), while other 1933 Harvard books were
              renewed in that window (e.g. Harris, Twenty years of Federal Reserve policy, R272802,
              20 Mar 1961). LacusCurtius states the same. Text from B. Thayer's LacusCurtius transcription
              (penelope.uchicago.edu), collated by machine with the OCR of the 1933 printing
              (archive.org in.gov.ignca.2849) and every disagreement checked on the page images; where
              the transcription follows a later printing, the 1933 wording is restored (EN_FIXES).
              Oldfather's footnotes and Thayer's page numbers and notes are omitted.

Usage:
    python3 scripts/import_diodorus_egypt.py           # build
    python3 scripts/import_diodorus_egypt.py --force   # re-download scans
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
KEY = "diodorus-egypt"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
N = lambda s: unicodedata.normalize("NFC", s)

IIIF = "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.130/Vat.gr.130_{:04d}.jp2"
VIEW = "https://digi.vatlib.it/view/MSS_Vat.gr.130/{:04d}"
PERSEUS = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0060/tlg001/tlg0060.tlg001.perseus-grc5.xml"
VOGEL_SCAN = "https://archive.org/details/diodoribibliothe01diod_0"
THAYER = "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Diodorus_Siculus/1A*.html"
LOEB_SCAN = "https://archive.org/details/in.gov.ignca.2849"
CCE = "https://github.com/NYPL/cce-renewals"
BANNER_Y = 1640  # rows below this are the library's caption bar

# page id -> (DigiVatLib image, side, what was read on the image)
PAGE_BREAKS = {
    "0012R": "the last lines begin 1.10.1; the page ends 'Αἰγύπτιοι κατὰ τὴν ἐξ ἀρχῆς τῶν ὅλων γένεσιν πρώ-|τους ἀνθρώπους γενέσθαι κατὰ τὴν Αἴγυπτον διά' (1.10.1)",
    "0013L": "begins 'τὴν εὐκρασίαν τῆς χώρας καὶ διὰ τὴν φύσιν τοῦ Νείλου' (1.10.1); ends 'ἡ γῆ πάλιν ἐξ ἀρχῆς καινὰς ἤνεγκε τῶν ζῴων φύσεις, ὅμως καὶ κατὰ' (1.10.4)",
    "0013R": "begins 'τοῦτον τὸν λόγον πρέπειν τὴν ἀρχηγὸν τῶν ἐμψύχων γένεσιν' (1.10.4); ends 'ἀστροφαῆ Διόνυσον ἐν ἀκτίνεσσι πυρωπόν, Ὀρφεὺς δὲ' (1.11.3)",
    "0014L": "begins 'τοὔνεκά μιν καλέουσι Φάνητά τε καὶ Διόνυσον. φασὶ δέ τινες' (1.11.3-4); ends 'τοὺς πρώτους διαλέκτῳ χρησαμένους διηρθρωμένῃ τῶν κατ’ Αἴγυπτον ἀν-' (1.12.1)",
    "0014R": "begins '-θρώπων. τὸ μὲν οὖν πνεῦμα Δία προσαγορεῦσαι' (1.12.1-2); ends 'καὶ παρθένον ὑποστήσασθαι διά τε τὸ ἄφθορον εἶναι τὸν' (1.12.7)",
    "0015L": "begins 'ἀέρα καὶ τὸν ἀκρότατον ἐπέχειν τόπον τοῦ σύμπαντος κόσμου' (1.12.7); ends 'κατὰ τὴν Αἴγυπτον. μεθερμηνευομένων δ’ αὐτῶν τινὰς μὲν ὁμωνύμους ὑπάρχειν τοῖς οὐρανίοις' (1.13.1-2)",
    "0015R": "begins 'τινὰς δ’ ἰδίαν ἐσχηκέναι προσηγορίαν ... καὶ Κρόνον καὶ Ῥέαν' (1.13.2); the last line but one begins 1.14 'πρῶτον μὲν γὰρ παῦσαι τῆς ἀλληλοφαγίας'",
    "0016L": "begins 'γένος, εὑρούσης μὲν Ἴσιδος τόν τε τοῦ πυροῦ καὶ τῆς κριθῆς καρπόν' (1.14.1); ends 'ἐνίους δὲ Θήβας. ἀμφισβητεῖται δ’ ἡ' (1.15.1-2)",
    "0016R": "begins 'κτίσις τῆς πόλεως ταύτης οὐ μόνον παρὰ τοῖς συγγραφεῦσιν' (1.15.2); ends 'σχεδὸν Αἰγύπτοιο ῥοάων. εὑρετὴν δ’ αὐτὸν φασὶ γενέσθαι' (1.15.7-8)",
    "0017L": "begins 'τῆς ἀμπέλου περὶ τὴν Νῦσαν, καὶ τὴν κατεργασίαν τοῦ ταύτης καρποῦ' (1.15.8); ends 'στρατόπεδον μέγα συστήσασθαι, διανοούμενον ἐπελθεῖν ἅπασαν τὴν οἰκου-' (1.17.1)",
    "0017R": "begins '-μένην καὶ διδάξαι τὸ γένος τῶν ἀνθρώπων τήν τε τῆς ἀμπέλου φυτείαν' (1.17.1); ends 'τοῦ δὲ κιττοῦ τὴν εὕρεσιν ἀνατιθέασιν Ὀσίριδι, καὶ καθιεροῦσιν αὐτὸν τούτῳ τῷ θεῷ' (1.17.4)",
    "0018L": "begins 'καθάπερ καὶ οἱ Ἕλληνες Διονύσῳ. καὶ κατὰ τὴν Αἰγυπτίων μὲν διάλεκτον' (1.17.4-5); ends 'τὸ περὶ τῆς κόμης νόμιμον παρ’ Αἰγυπτίοις, καὶ τοὺς ποιουμένους' (1.18.3)",
    "0018R": "begins 'τὰς ἀποδημίας μέχρι τῆς εἰς οἶκον ἀνακομιδῆς κομοτροφεῖν' (1.18.3); ends 'τὸν δ’ Ἡρακλέα, μεγαλεπίβολον ὄντα ... τό τε γενόμενον ἔκρηγμα ταχέως' (1.19.2)",
    "0019L": "begins 'ἐμφράξαι καὶ τὸν ποταμὸν ἐπὶ τὴν προϋπάρξασαν ῥύσιν ἀποστρέψαι' (1.19.2); ends 'πολλὰ δὲ καὶ ἄλλα σημεῖα τῆς ἑαυτοῦ παρουσίας ἀπολελοιπέναι κατ’ ἐκείνην τὴν χώραν, δι’ ὧν' (1.19.8)",
    "0019R": "begins 'προαχθέντας τοὺς μεταγενεστέρους τῶν Ἰνδῶν ἀμφισβητῆσαι' (1.19.8); 1.20 begins at the end of the second line 'γενέσθαι δὲ'; ends 'μεγαλύνοντας τοῦ θεοῦ τὴν δύναμιν. τῶν' (1.20.6, with the first word of 1.21)",
    "0020L": "begins 'δ’ ἱερέων περὶ τῆς Ὀσίριδος τελευτῆς ἐξ ἀρχαίων ἐν ἀπορρήτοις' (1.21.1); ends 'καὶ τῶν εὐεργεσιῶν ὑπομνήσασαν παρακαλέσαι θάψαντας ἐν τοῖς ἰδίοις' (1.21.6)",
    "0020R": "begins 'τόποις τὸ σῶμα τιμᾶν ὡς θεὸν τὸν Ὄσιριν' (1.21.6); ends 'τυχεῖν ἀθανάτων τιμῶν καὶ ταφῆναι κατὰ τὴν Μέμφιν, ὅπου δείκνυται' (1.22.2)",
    "0021L": "begins 'μέχρι τοῦ νῦν ὁ σηκός, ὑπάρχων ἐν τῷ τεμένει τοῦ Ἡφαίστου' (1.22.2); ends 'παρειληφότας τὰ περὶ τοὺς ὀργιασμοὺς καὶ τὰς Διονυσιακὰς ἑορτάς' (1.22.7)",
    "0021R": "begins 'τιμᾶν τοῦτο τὸ μόριον ἔν τε τοῖς μυστηρίοις' (1.22.7); 1.23 begins on line 3 'εἶναι δὲ ἔτη φασὶν'; ends 'Ὀσίριδος γεγενημένης. ἀνάψαι δὲ καὶ τὴν γένεσιν εἰς Δία' (1.23.5-6)",
    "0022L": "begins 'σεμνύνοντα τὸν Ὄσιριν καὶ τῆς φθαρείσης τὴν διαβολὴν ἀφαιρούμενον' (1.23.6); ends 'Ἡρακλῆς συνηγωνίσατο τὸν πρὸς τοὺς γίγαντας πόλεμον, φασὶ' (1.24.2)",
    "0022R": "begins 'τῇ γῇ μηδαμῶς ἁρμόττειν γεγεννηκέναι τοὺς γίγαντας' (1.24.2); ends 'καὶ μάλιστα κατὰ τὴν Αἴγυπτον καὶ τὴν ὑπερκειμένην' (1.24.6)",
    "0023L": "begins 'χώραν μέχρι τοῦ νῦν ἔρημον οὖσαν καὶ θηριώδη' (1.24.6); ends 'διδόναι τοῖς κάμνουσι βοηθήματα πρὸς τὰς νόσους, καὶ τοὺς' (1.25.5)",
    "0023R": "begins 'ὑπακούσαντας αὐτῇ παραδόξως ὑγιάζεσθαι' (1.25.5); ends 'συνέβαινε κατὰ τὴν τῆς σελήνης περίοδον ἄγεσθαι τὸν ἐνιαυτόν. διόπερ τῶν ἐτῶν τρια-' (1.26.3-4)",
    "0024L": "begins '-κονθημέρων ὄντων οὐκ ἀδύνατον εἶναι βεβιωκέναι τινὰς ἔτη χίλια καὶ διακόσια' (1.26.4); ends 'μετελθεῖν τόν τε φόνον τἀνδρὸς καὶ διατελέσαι βασιλεύουσαν νομιμώτατα' (1.27.1)",
    "0024R": "begins 'καὶ τὸ σύνολον πλείστων καὶ μεγίστων ἀγαθῶν αἰτίαν γενέσθαι πᾶσιν ἀνθρώποις' (1.27.1); ends 'καὶ οὐκ ἔστι τόπος τῆς οἰκουμένης εἰς ὃν οὐκ ἀφῖγμαι, διαδοὺς' (1.27.5)",
    "0025L": "begins 'πᾶσιν ὧν ἐγὼ εὑρετὴς ἐγενόμην. τοσαῦτα τῶν γεγραμμένων ἐν ταῖς στήλαις' (1.27.5-6); ends 'καὶ τοὺς Ἀθηναίους δέ φασιν ἀποίκους εἶναι Σαϊτῶν τῶν ἐξ Αἰγύπτου, καὶ πειρῶνται' (1.28.4)",
    "0025R": "begins 'τῆς οἰκειότητος ταύτης φέρειν ἀποδείξεις· παρὰ μόνοις γὰρ τῶν Ἑλλήνων' (1.28.4); ends 'Ἑλληνικῆς καὶ βαρβάρου, διφυὴς ἐνομίσθη, τὸ μὲν ἔχων' (1.28.7)",
    "0026L": "begins 'μέρος θηρίου, τὸ δὲ ἀνθρώπου' (end of 1.28.7), followed on the same line by 1.29 'ὁμοίως δὲ τούτῳ καὶ τὸν Ἐρεχθέα'; ends 'τοὺς δὲ Κήρυκας ἀπὸ τῶν παστοφόρων. τήν τε Ἶσιν μόνους τῶν' (1.29.4)",
    "0026R": "begins 'Ἑλλήνων ὀμνύειν, καὶ ταῖς ἰδέαις καὶ τοῖς ἤθεσιν' (1.29.4); 1.29 ends in the middle of the page 'ἐν κεφαλαίοις ἕκαστα διεξιέναι πειρασόμεθα', followed by 1.30 'ἡ γὰρ Αἴγυπτος κεῖται μὲν μάλιστά πως κατὰ μεσημβρίαν'",
    "0040L": "the last line begins 1.44.1 'μυθολογοῦσι δ’ αὐτῶν τινες τὸ μὲν πρῶτον ἄρξαι τῆς', after the end of 1.43 'ἐν ταῖς ἱεραῖς ἀναγραφαῖς οὕτω παρειληφότων'",
    "0040R": "begins 'Αἰγύπτου θεοὺς καὶ ἥρωας ἔτη βραχὺ λείποντα τῶν μυρίων καὶ ὀκτακισχιλίων' (1.44.1); ends with the last words of 1.44.5 'τὰ κυριώτατα συντόμως διεξιέναι πειρασόμεθα'",
}
# chapter -> pages carrying it (from the page breaks above)
CHAPTER_PAGES = {
    10: ["0012R", "0013L", "0013R"], 11: ["0013R", "0014L"], 12: ["0014L", "0014R", "0015L"],
    13: ["0015L", "0015R"], 14: ["0015R", "0016L"], 15: ["0016L", "0016R", "0017L"], 16: ["0017L"],
    17: ["0017L", "0017R", "0018L"], 18: ["0018L", "0018R"], 19: ["0018R", "0019L", "0019R"],
    20: ["0019R"], 21: ["0019R", "0020L", "0020R"], 22: ["0020R", "0021L", "0021R"],
    23: ["0021R", "0022L"], 24: ["0022L", "0022R", "0023L"], 25: ["0023L", "0023R"],
    26: ["0023R", "0024L"], 27: ["0024L", "0024R", "0025L"], 28: ["0025L", "0025R", "0026L"],
    29: ["0026L", "0026R"], 44: ["0040L", "0040R"],
}

GREEK_FIXES = [  # checked against Vogel's printed pages (archive.org diodoribibliothe01diod_0)
    ("26.7", "καὶ πολλὰς ἐπιτελεσαμένους", "καὶ πολλὰς πράξεις ἐπιτελεσαμένους"),   # p. 42 l. 10-11
    ("26.8", "ἀνῃρέ- θησαν", "ἀνῃρέθησαν"),
    ("28.5", "οἵτινες ἱεροποιοὶ ὑπῆρχον", "οἵτινες [ἱεροποιοὶ] ὑπῆρχον"),       # p. 46, bracketed by Vogel
    ("44.1", "φασιν ἀπὸ Μοίριδος ἔτη", "φασιν [ἀπὸ Μοίριδος] ἔτη"),             # p. 77 l. 21-22
    ("44.2", "Αἰθίοκας μὲν οὖν", "Αἰθίοπας μὲν οὖν"),                          # p. 78 l. 1
]
EN_FIXES = [  # Thayer's transcription -> 1933 printing (checked on the page images, Loeb pp. 35-95, 157-159)
    ("10.1", "corsaeon, as it is called", "corsaeum, as it is called"),
    ("10.4", "In general, he says that", "In general, they say that"),
    ("10.7", "living animals, he says,", "living animals, they say,"),
    ("11.1", "the men of Egypt, he says,", "the men of Egypt, they say,"),
    ("12.4", "Gê Meter", "Ge Meter"),
    ("13.4", "Aphroditê", "Aphrodite"),
    ("15.7", "Aegyptus' streams", "Aegyptus' stream"),
    ("16.2", "not Athena's, as the Greeks say", "not Athena's, as Greeks say"),
    ("17.2", "who received his gift", "who received this gift"),
    ("17.5", "Aphroditê", "Aphrodite"),
    ("18.5", "taken along in the campaign", "taken along on the campaign"),
    ("19.5", "by dykes", "by dikes"),
    ("20.2", "opposed his undertaking,", "opposed his undertakings,"),
    ("25.1", "Selenê", "Selene"),
    ("28.2", "the oldest city in Greece", "the oldest city of Greece"),
    ("28.4", "Saïs", "Sais"),
    ("29.3", "were instituted at Eleusis", "were instituted in Eleusis"),
]

ENTRIES = [
    ("origins", 1, [10, 11, 12, 13],
     "Diodorus Siculus 1.10-13: the first men, the eternal gods and the god-kings of Egypt",
     "The Egyptian account in Diodorus of how the first men came into being in Egypt from the mud of the Nile, of the sun and moon as the eternal gods Osiris and Isis, of the elements as gods, and of the earthly gods who ruled Egypt as kings, from Helius or Hephaestus to Cronus and Osiris."),
    ("isis-osiris-hermes", 2, [14, 15, 16],
     "Diodorus Siculus 1.14-16: Isis and Osiris as givers of grain, wine and law; Hermes the inventor",
     "Isis discovers wheat and barley and gives laws, Osiris founds Thebes and teaches the vine, and Hermes invents letters, music, astronomy and the olive, in Diodorus' account of the Egyptian gods who ruled as kings."),
    ("osiris-campaign", 3, [17, 18, 19, 20],
     "Diodorus Siculus 1.17-20: the campaign of Osiris through the inhabited world",
     "Osiris leaves Isis to rule Egypt and travels with Anubis, Macedon, Pan, the Muses and the Satyrs through Ethiopia, Arabia and India to Thrace, teaching agriculture and the vine, while Heracles stops the flood of the Nile."),
    ("death-of-osiris", 4, [21, 22],
     "Diodorus Siculus 1.21-22: the death of Osiris, the vengeance of Isis and the tombs of the gods",
     "Typhon murders Osiris and divides his body into twenty-six pieces; Isis and Horus avenge him, Isis gives each order of priests a share of the burial, and the tombs of Isis and Osiris are shown at Memphis and at Philae."),
    ("colonies-and-claims", 5, [23, 24, 25, 26, 27, 28, 29],
     "Diodorus Siculus 1.23-29: the age of the gods, the Egyptian Heracles, Isis the healer, the stelae of Isis and Osiris, and the colonies from Egypt",
     "The Egyptian claims in Diodorus: more than ten thousand years from Osiris to Alexander, the gods' reigns of 1,200 and 300 years explained as lunar years, the giants, the inscriptions on the stelae of Isis and Osiris, and the colonies said to have gone out from Egypt to Babylon, Argos, Colchis, Judea and Athens."),
    ("reign-lengths", 6, [44],
     "Diodorus Siculus 1.44: gods and heroes for almost 18,000 years, then mortal kings",
     "Diodorus' summary of the Egyptian priests' chronology: gods and heroes ruled Egypt for a little less than 18,000 years, the last of them Horus son of Isis, and mortal kings for almost 5,000 years, 470 men and 5 women of native birth besides the Ethiopian, Persian and Macedonian rulers."),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def page_label(pid):
    return f"DigiVatLib image {pid[:4]}, {'left' if pid[4] == 'L' else 'right'} page"


def scan(pid, force, cache={}):
    path = SCAN_DIR / f"vat-gr-130-img{pid[:4]}-{'left' if pid[4] == 'L' else 'right'}.jpg"
    if path.exists() and not force:
        return path
    n = int(pid[:4])
    if n not in cache:
        cache[n] = Image.open(io.BytesIO(fetch(IIIF.format(n) + "/full/full/0/default.jpg"))).convert("L")
    img = cache[n]
    w, h = img.size
    small = img.resize((w // 8, h // 8))
    px = small.load()
    sw, sh = small.size
    cols = range(int(sw * 0.4), int(sw * 0.6))
    gutter = min(cols, key=lambda x: sum(px[x, y] for y in range(int(sh * 0.1), int(sh * 0.85)))) * 8
    box = (0, 0, gutter, BANNER_Y) if pid[4] == "L" else (gutter, 0, w, BANNER_Y)
    page = img.crop(box)
    long_side = max(page.size)
    if long_side > 2600:
        page = page.resize((round(page.size[0] * 2600 / long_side), round(page.size[1] * 2600 / long_side)))
    page.convert("RGB").save(path, quality=88)
    print(f"  {path.name}: gutter x={gutter}, {page.size}")
    return path


def greek():
    root = ET.parse(SRC / "tlg0060.tlg001.perseus-grc5.xml").getroot()
    g = {}
    for b in root.iter(f"{TEI}div"):
        if b.get("subtype") == "book" and b.get("n") == "1":
            for c in b.iter(f"{TEI}div"):
                if c.get("subtype") == "chapter" and c.get("n").isdigit() and int(c.get("n")) in CHAPTER_PAGES:
                    for s in c.iter(f"{TEI}div"):
                        if s.get("subtype") == "section":
                            g[f"{c.get('n')}.{s.get('n')}"] = N(re.sub(r"\s+", " ", "".join(s.itertext())).strip())
    for k, a, b in GREEK_FIXES:
        assert g[k].count(N(a)) == 1, (k, a)
        g[k] = g[k].replace(N(a), N(b))
    for k, t in g.items():
        assert not re.search(r"[A-Za-z0-9]|\w- ", t), (k, t)
    return g


def english():
    secs = {}
    for name in ("1A.html", "1C.html"):
        t = (SRC / "oldfather" / name).read_text(encoding="utf-8", errors="replace")
        t = t[:t.index('<HR CLASS="endnotes"')]
        t = re.sub(r'<SPAN CLASS="emend">of</SPAN><A CLASS="correction".*?º</A>', "", t, flags=re.S)  # 'of' added by Thayer, not in the Loeb
        t = re.sub(r'<A CLASS="ref"[^>]*>.*?</A>', "", t, flags=re.S | re.I)
        t = re.sub(r'<SPAN CLASS="pagenum">.*?</SPAN>', "", t, flags=re.S | re.I)
        t = re.sub(r'<A CLASS="chapter" NAME="(\d+)">\d+</A>', r"@@\1.1@@", t)
        t = re.sub(r'<A CLASS="sec" NAME="(\d+)\.(\d+)">\d+</A>', r"@@\1.\2@@", t)
        t = re.sub(r"</?(I|B|EM|SMALL|SPAN|FONT)(\s[^>]*)?>", "", t, flags=re.I)  # inline markup
        t = html.unescape(re.sub(r"<[^>]+>", " ", t))
        cur = None
        for tok in re.split(r"(@@\d+\.\d+@@)", t):
            m = re.fullmatch(r"@@(\d+\.\d+)@@", tok)
            if m:
                cur = m.group(1)
                secs.setdefault(cur, "")
            elif cur:
                secs[cur] += tok
    for k in secs:
        s = secs[k].replace("⁠", "")
        s = re.sub(r"\s*\xad\s*", "", s)
        secs[k] = re.sub(r"\s+", " ", s).strip()
    for k, a, b in EN_FIXES:
        assert secs[k].count(a) == 1, (k, a)
        secs[k] = secs[k].replace(a, b)
    return secs


def chapter_text(d, ch):
    keys = sorted((k for k in d if int(k.split(".")[0]) == ch), key=lambda k: int(k.split(".")[1]))
    assert keys and keys[0] == f"{ch}.1", (ch, keys[:3])
    return keys, " ".join(f"<sup>{k.split('.')[1]}</sup>{d[k]}" for k in keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    g, e = greek(), english()
    pages = {pid: scan(pid, args.force) for pid in PAGE_BREAKS}
    rel = {pid: f"{KEY}/{p.name}" for pid, p in pages.items()}

    intro_common = (
        "<p>Diodorus of Sicily wrote his <em>Library of History</em>, a history of the world in forty books, between about 60 and 30 BCE; he visited Egypt in the 180th Olympiad (60-56 BCE). "
        "Book 1 is devoted to Egypt, and its first part gives what the Egyptian priests and the Greek writers who used them (chiefly Hecataeus of Abdera) told of the beginning of the world and of the gods who ruled Egypt as kings before the first mortal king, Menas. "
        "Diodorus reports these accounts without vouching for them.</p>\n\n"
        "<p>The manuscript shown is Vat. gr. 130 in the Vatican Library, a parchment copy of books 1-5 made in the middle of the 10th century, the oldest manuscript of this part of the work. "
        "The images are the library's black-and-white microfilm; each opening has been split into its two pages. No folio numbers are legible on the images, so pages are cited by DigiVatLib image number and side. "
        "Each section is one chapter and lists the page or pages that carry it; the page breaks were read on the images and are recorded in each note.</p>"
    )
    notes = [
        "Greek: F. Vogel's Teubner edition (1888), from the Perseus Digital Library, checked against the printed volume. Square brackets are Vogel's marks for words he took to be later additions. The manuscript's wording differs from the edition in places; the Greek shown is the edition, not a transcription of the page.",
        "English: C. H. Oldfather's Loeb translation (1933), as printed in that year; his footnotes are omitted. Oldfather's section numbers follow Vogel's, with occasional small differences in where a section begins.",
    ]
    rows = []
    for slug, order, chapters, title, desc in ENTRIES:
        secs, fols = [], []
        for ch in chapters:
            gk, gtxt = chapter_text(g, ch)
            ek, etxt = chapter_text(e, ch)
            if len(gk) != len(ek):
                print(f"  note: 1.{ch} has {len(gk)} Greek and {len(ek)} English sections")
            pids = CHAPTER_PAGES[ch]
            fols += [p for p in pids if p not in fols]
            lead = (f"1.{ch} is on {page_label(pids[0])}. " if len(pids) == 1 else
                    f"1.{ch} runs over {len(pids)} pages: " + "; ".join(page_label(p) for p in pids) + ". ")
            note = lead + " ".join(f"{page_label(p)}: {PAGE_BREAKS[p]}." for p in pids)
            secs.append({
                "section": f"1.{ch}",
                "original_ref": f"Diodorus 1.{ch} (Vogel); Vat. gr. 130, " + ", ".join(page_label(p) for p in pids),
                "original_text": gtxt,
                "text": etxt,
                "scan_pages": [rel[p] for p in pids],
                "scan_note": note + " Checked on the images. Viewer: " + VIEW.format(int(pids[0][:4])),
            })
        tid = PREFIX + slug
        rng = f"1.{chapters[0]}" + (f"-{chapters[-1]}" if len(chapters) > 1 else "")
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Greek (Vogel 1888) / English (Oldfather 1933)",
            "source": "Vat. gr. 130 (10th c.) via DigiVatLib IIIF + Vogel Greek (Perseus, checked against the 1888 printing) + Oldfather English (Loeb 1933, public domain)",
            "description": desc,
            "introduction": intro_common + f"\n\n<p>This entry covers chapters {rng}.</p>",
            "translator_notes": notes,
            "translation": secs,
            "verification": {
                "scan_source": "Biblioteca Apostolica Vaticana, DigiVatLib IIIF (digi.vatlib.it), Vat. gr. 130, images " + ", ".join(sorted({p[:4] for p in fols})),
                "scan_license": "© Biblioteca Apostolica Vaticana (all rights reserved, as stated on the images); reproduced for non-commercial scholarly use with credit",
                "scan_manuscript": "Vatican City, Biblioteca Apostolica Vaticana, Vat. gr. 130 (parchment, mid-10th c.), Diodorus books 1-5; microfilm images",
                "scan_mapping": "Checked on the images: the first and last lines of every page were read and found in Vogel's text; each chapter's pages follow from those page breaks (quoted in each scan_note in the edition's spelling where the copy agrees)",
                "scan_mapping_urls": [VIEW.format(int(n)) for n in sorted({p[:4] for p in fols})],
                "scan_local_paths": [rel[p] for p in fols],
                "original_text_source": f"F. Vogel, Diodori Bibliotheca historica vol. 1 (Leipzig: Teubner, 1888), Perseus canonical-greekLit tlg0060.tlg001.perseus-grc5 ({PERSEUS}), checked against {VOGEL_SCAN}",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"C. H. Oldfather, Diodorus of Sicily vol. 1 (Loeb Classical Library 279, 1933); transcription by B. Thayer ({THAYER}) checked against the 1933 printing ({LOEB_SCAN})",
                "translation_license": f"public domain in the US: published 1933, copyright not renewed (no entry in the 1959-1962 renewal registrations, {CCE}); LacusCurtius states the same",
                "translator": "C. H. Oldfather (1933)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order, "title": title, "author_id": "diodorus",
            "language": "Greek", "era": "Late Republic", "tradition": "greek", "category": "history",
            "date_approx": "c. 60-30 BCE (Diodorus); mid-10th c. (Vat. gr. 130)", "century": -1,
            "source": entry["source"], "description": desc,
            "themes": ["diodorus", "egypt", "osiris", "isis", "gods-as-kings", "earliest-civilization", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": rel[p], "caption": f"Vat. gr. 130, {page_label(p)}"} for p in fols]},
        })
        print(f"  {tid}: {len(secs)} sections, {len(fols)} pages")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Diodorus Siculus on the gods of Egypt",
            "group": "Egypt", "date_sort": -60,
            "author_name": "Diodorus Siculus (c. 60-30 BCE), Library of History book 1",
            "source_url": "https://digi.vatlib.it/view/MSS_Vat.gr.130",
            "critical_edition": "F. Vogel, Teubner 1888 (Perseus, checked against the printing)",
            "translator_name": "C. H. Oldfather (1933)",
            "original_lang_label": "Greek · Vogel",
            "original_lang_code": "grc", "edition_label": "",
            "search_terms": "diodorus siculus bibliotheca library of history egypt osiris isis hermes thoth gods kings first men nile colonies hecataeus",
            "description": "Diodorus of Sicily's account of the Egyptian traditions on the first men, the gods who ruled Egypt as kings, the deeds and death of Osiris, the colonies said to have gone out from Egypt, and the 18,000 years of gods and heroes, on the pages of the 10th-century Vatican manuscript.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
