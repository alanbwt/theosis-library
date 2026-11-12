#!/usr/bin/env python3
"""
import_philo.py: Philo of Alexandria, On the Creation of the World (De opificio
mundi, complete, 172 sections) and two Logos passages (On the Confusion of
Tongues 146-147; Who is the Heir of Divine Things 205-206), each section shown
on the manuscript page that carries it.

Chain of evidence
  1. MANUSCRIPT
     Vatican City, Biblioteca Apostolica Vaticana, Pal. gr. 248 (14th-15th c.),
     a Philo corpus. Contents and folio ranges from Pinakes (diktyon 65980):
     De vita Mosis 1-40v, De opificio mundi 40v-56v, De confusione linguarum
     196v-208, Quis rerum divinarum heres sit 280v-300v. Colour images from
     DigiVatLib IIIF, https://digi.vatlib.it/iiif/MSS_Pal.gr.248/manifest.json
     (manifest cached in data/sources/philo/iiif/palgr248-manifest.json).
     Other candidates were checked and set aside: Vat. gr. 381 holds the
     Allegorical Commentary but not De opificio (Pinakes 67012) and is a
     black-and-white microfilm; Paris gr. 435 is on Gallica, which refuses
     automated requests (HTTP 403); the BML server for Laur. Plut. 10.20 did not
     answer; Munich Cod. graec. 459 (13th c.) is online only as a microfilm.
  2. MAPPING  The first and last lines of every page used were read on the
     image (crops at 2000 px) and matched to the Greek; the words read are
     stored in PAGES below and quoted in each scan_note. Reading the end of one
     page and the start of the next confirmed that no line was skipped. A
     section is assigned to every page whose first-to-last-line span contains
     part of it, so a section cut by a page break lists both pages. Nothing was
     placed by counting lines or by text length.
  3. GREEK    Leopold Cohn (De opificio) and Paul Wendland (De confusione, Quis
     heres) in Cohn-Wendland, Philonis Alexandrini opera quae supersunt I-III
     (Berlin 1896-1898; public domain), digital text OpenGreekAndLatin
     First1KGreek tlg0018.tlg001/013/015.1st1K-grc1 (CC BY-SA 4.0), apparatus
     notes dropped, editorial additions <add> shown as angle brackets.
     Proofreading: the whole of De opificio was compared word by word (accents
     included) with an independent digital Cohn-Wendland text (R. Khazarzar,
     khazarzar.skeptik.net, cached in data/sources/philo/*.htm). The texts agree
     except for two OCR faults in First1KGreek, both checked against the printed
     page (Cohn 1896 pp. 7 and 36, archive.org philonisalexand05wendgoog) and
     corrected below (CORRECTIONS_GRC). First1KGreek places Cohn's section
     numbers at the start of the printed line; the sections here start at the
     sentence where the section begins (the placement of the Khazarzar/TLG text
     and of the English), found by aligning the two Greek texts.
  4. ENGLISH  C. D. Yonge, The Works of Philo Judaeus (Bohn, London 1854-1855;
     public domain), digital text First1KGreek tlg0018.*.1st1K-eng1 (CC BY-SA
     4.0), divided into the sections of the Scholer edition. The digital text of
     On the Creation was compared word by word with the archive.org OCR of the
     1854 printing (worksphilojudaeu01philuoft); the only real differences are
     corrected below (CORRECTIONS_ENG). Conf. 146-147 and Heres 205-206 were
     checked against the OCR of volume 2 (worksphilojudaeu02philuoft) and agree.

Usage:
    python3 scripts/import_philo.py           # build
    python3 scripts/import_philo.py --force   # re-download scans
"""

import argparse
import difflib
import html as htmlmod
import io
import json
import re
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

KEY = "philo"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
F1K = "https://github.com/OpenGreekAndLatin/First1KGreek/tree/master/data/tlg0018"

MS = {
    "manifest": SRC / "iiif" / "palgr248-manifest.json",
    "shelfmark": "Vatican City, Biblioteca Apostolica Vaticana, Pal. gr. 248",
    "short": "Pal. gr. 248",
    "desc": ("Vatican City, Biblioteca Apostolica Vaticana, Pal. gr. 248, paper, 14th-15th century, a collection of Philo's works "
             "(Life of Moses, On the Creation, On the Decalogue, the Special Laws, the Allegorical Commentary and others); "
             "formerly in the Palatine Library at Heidelberg. Folio ranges from Pinakes (diktyon 65980)."),
    "object": "https://digi.vatlib.it/view/MSS_Pal.gr.248",
    "holder": "Biblioteca Apostolica Vaticana, DigiVatLib (IIIF)",
    "license": ("Images (c) Biblioteca Apostolica Vaticana (copyright notice on each image; DigiVatLib, https://digi.vatlib.it). "
                "Reproduced here with credit for non-commercial reference use."),
    "pinakes": "https://pinakes.irht.cnrs.fr/notices/cote/65980/",
    "width": 2000,
}

# Greek OCR faults in First1KGreek, checked on the printed page of Cohn 1896.
CORRECTIONS_GRC = {
    ("tlg001", "24"): [(re.compile(r"ἤδη \[νοητὴν\]ν \[\[?νοητὴν\]ητὴν\]\.? πόλιν"), "ἤδη τὴν [νοητὴν] πόλιν")],
    ("tlg001", "104"): [(re.compile(r"ἔχους’"), "ἔχουσ’")],
}
# English: differences from the 1854 printing (checked on the archive.org scan).
CORRECTIONS_ENG = {
    "tlg001": [("oysters an fish", "oysters and fish"), ("fullness", "fulness"),
               ("preeminent", "pre-eminent"), ("in his before mentioned account", "in his beforementioned account")],
    "tlg015": [("preeminent", "pre-eminent")],
}

# ---------------------------------------------------------------------------
# Page data, read on the images. start/end = the sections in which the page's
# first / last line falls; first/last = words read on those lines.
# ---------------------------------------------------------------------------
OPIF_PAGES = [
    {"folio": "40v", "start": 1, "end": 8,
     "custom": ("Pal. gr. 248 fol. 40v: the first four lines end the Life of Moses ('... διὰ τῶν ἱερῶν γραμμάτων μνημονεύεται'); "
                "below a red headpiece and the red title 'Φίλωνος περὶ τῆς τοῦ Μωσέως κοσμοποιίας λόγος', On the Creation begins with a red initial: "
                "'Τῶν ἄλλων νομοθετῶν οἱ μὲν ἀκαλλώπιστα καὶ γυμνὰ τὰ νομισθέντα'. The last line reads "
                "'..., ἢ αὐτὸ τἀγαθὸν, ἢ αὐτὸ τὸ καλόν' (end of section 8).")},
    {"folio": "41r", "start": 9, "end": 16, "first": "τὸ δὲ παθητὸν ἄψυχον ... καὶ ἀκίνητον ἐξ ἑαυτοῦ, κινηθὲν δὲ",
     "last": "πρεσβυτέρου νεώτερον ἀπεικόνισμα, τοσαῦτα περιέξοντα αἰσθητὰ γένη, ὅσα περ"},
    {"folio": "41v", "start": 16, "end": 24, "first": "ἐν ἐκείνῳ νοητά. τὸν δὲ ἐκ τῶν ἰδεῶν συνεστῶτα κόσμον ἐν τόπῳ",
     "last": "οὐδὲν ἂν ἕτερον εἴποι τὸν νοητὸν κόσμον εἶναι ἢ θεοῦ λόγον ἤδη κοσμοποιοῦντος· οὐδὲ"},
    {"folio": "42r", "start": 24, "end": 31, "first": "ἡ νοητὴ πόλις ἕτερόν τι ἐστὶν ἢ ὁ τοῦ ἀρχιτέκτονος λογισμὸς",
     "last": "τρέπεσθαι κατὰ τὴν ἐκ νοητοῦ πρὸς αἰσθητὸν μεταβολήν· εἱλικρινὲς γὰρ οὐδὲν",
     "extra": "Line 2 has the start of section 25, 'τὸ δὲ δόγμα τοῦτο Μωσέως ἐστὶν οὐκ ἐμόν'."},
    {"folio": "42v", "start": 31, "end": 38, "first": "τῶν ἐν αἰσθήσει. εὖ μέντοι καὶ τὸ φάναι ὅτι σκότος ἐπάνω τῆς ἀβύσσου",
     "last": "ξηρὰν ἀναφανῆναι, τῆς τοῦ γλυκέος νοτίδος ἐναπολειφθείσης εἰς διαμονήν· κόλλα"},
    {"folio": "43r", "start": 38, "end": 45, "first": "γάρ τίς ἐστιν ἡ μεμετρημένη γλυκεῖα νοτὶς τῶν διεστηκότων",
     "last": "τέλους ἀρχή. τῇ δὲ τετάρτῃ ἡμέρᾳ μετὰ τὴν γῆν, τὸν οὐρανὸν ἐποίκιλλε διακοσμῶν· οὐκ"},
    {"folio": "43v", "start": 45, "end": 49, "first": "ἐπειδὴ τοῦτον ἐν ὑστέρῳ γῆς ἔταττε, τῇ μὲν ἐλάττονι φύσει προνομίαν διδούς",
     "last": "καὶ μέγα χρῆμα συμβέβηκεν εἶναι τὸν ἀριθμὸν τοῦτον, ὃς ἐκ τῆς ἀσωμάτου καὶ νοητ(ῆς)"},
    {"folio": "44r", "start": 49, "end": 54, "first": "(νοητ)ῆς οὐσίας ἤγαγεν εἰς ἔννοιαν ἡμᾶς τριχῆ διαστατοῦ σώματος",
     "last": "ζητήσεως, τὸ φιλοσοφίας συνέστη γένος, οὗ τελειότερον ἀγαθὸν οὐκ ἦλθεν εἰς τὸν ἀνθρώπινον βίον"},
    {"folio": "44v", "start": 55, "end": 61, "first": "πρὸς δὴ τὴν τοῦ νοητοῦ φωτὸς ἰδέαν ἐκείνην ἀπιδών, ἣ λέλεκται κατὰ τὸν ἀσώματον",
     "last": "κινήσεις ἀστέρων· εἰς πόσα δὲ ἄλλα φαίην ἂν ἔγωγε τῶν ἡμῖν μὲν ἀδηλουμένων"},
    {"folio": "45r", "start": 61, "end": 66, "first": "τῷ θνητῷ γένει γνώριμα, πρὸς δὲ τὴν τοῦ ὅλου συνεργούντων διαμονήν",
     "last": "αὐτοῖς τοῦ ψυχοειδοῦς, καθάπερ φασὶ τοὺς ἅλας τοῖς κρέασιν, ἵνα μὴ ῥᾳδίως φθείροιντο"},
    {"folio": "45v", "start": 66, "end": 71, "first": "μετὰ δὲ τοὺς ἰχθύας τὰ πτηνὰ καὶ χερσαῖα· ἤδη γὰρ ταῦτα αἰσθητικώτερα",
     "last": "κάλλη, μέθῃ νηφαλίῳ κατασχεθεὶς ὥσπερ οἱ κορυβαντιῶντες ἐνθουσιᾷ· ἑτέρου"},
    {"folio": "46r", "start": 71, "end": 76, "first": "γεμισθεὶς ἱμέρου καὶ πόθου βελτίονος, ὑφ’ οὗ πρὸς τὴν ἄκραν ἁψῖδα παραπεμφθεὶς",
     "last": "μήπω τῶν ἐν μέρει μορφὴν λαβόντων, ἐπειδὴ τὰ ... τῶν εἰδῶν ἐνυπάρχει τῷ γένει καὶ"},
    {"folio": "46v", "start": 76, "end": 80, "first": "ὥσπερ ἐν κατόπτρῳ διαφαίνεται τοῖς ὀξὺ καθορᾶν δυναμένοις. ἐπιζητήσειε δ’ ἄν τις τὴν",
     "last": "(παρευημερη)σάντων καὶ τῶν ἀνθρώπων ἀνέδην ἐκκεχυμένων εἴς τε τὰ πάθη"},
    {"folio": "47r", "start": 80, "end": 84, "first": "ἃς οὐδ’ εἰπεῖν θέμις ὀρέξεις, ἀπαντᾶται δίκη προσήκουσα τιμωρὸς ἀσεβῶν",
     "last": "ἅτε θειοτέρας μοίρας ἐπιλαχόντα. πίστις δὲ τῆς ἀρχῆς ἐναργεστάτη, τὰ φαινόμενα"},
    {"folio": "47v", "start": 84, "end": 90, "first": "θρεμμάτων ἔστιν ὅτε πλήθη μυρία πρὸς ἀνδρὸς ἑνὸς ἄγεται τοῦ τυχόντος",
     "last": "φύσιν οὐκ οἶδ’ εἴ τις ... ὑμνῆσαι δύναιτο"},
    {"folio": "48r", "start": 90, "end": 96, "first": "θαυμασιωτέρα τῶν περὶ αὐτῆς λεγομένων ἐστί, διὰ τοῦθ’ ἡσυχαστέον",
     "last": "λόγον· τὰ δὲ πέντε πρὸς δύο πλείστην ἐν ἁρμονίᾳ δύναμιν ἐπιδείκνυται σχεδὸν ἐνάμιλ(λον)"},
    {"folio": "48v", "start": 96, "end": 100, "first": "τῇ διὰ πασῶν, ὅπερ ἐν τῇ κανονικῇ θεωρίᾳ σαφέστατα παρίσταται",
     "last": "γάρ, φησίν, ὁ ἡγεμὼν καὶ ἄρχων ἁπάντων θεὸς εἷς ἀεὶ ὤν, μόνιμος, ἀκίνητος, αὐτὸς"},
    {"folio": "49r", "start": 100, "end": 104, "first": "αὑτῷ ὅμοιος, ἕτερος τῶν ἄλλων. ἐν μὲν οὖν τοῖς νοητοῖς τὸ ἀκίνητον",
     "last": "ἐλεγεῖα ποιήσας τάδε· Παῖς μὲν ἄνηβος ἐὼν ἔτι νήπιος, ἕρκος ὀδόντων",
     "extra": "Solon's elegy is written continuously, not set out as verse."},
    {"folio": "49v", "start": 104, "end": 107, "first": "φύσας ἐκβάλλει πρῶτον ἐν ἕπτ’ ἔτεσιν· τοὺς δ’ ἑτέρους ὅτε δὴ τελέσῃ",
     "last": "γίας, τὴν ἀριθμητικήν, τὴν γεωμετρικήν, ἔτι δὲ τὴν ἁρμονικὴν περιέχει. τὸ δὲ πλινθίον"},
    {"folio": "50r", "start": 107, "end": 113, "first": "συνέστηκεν ἐκ τῶνδε τῶν ἀριθμῶν, ἓξ ὀκτὼ ἐννέα δώδεκα",
     "last": "αἰθρίαις, νεφώσεσι, βίαις ἐξαισίοις πνευμάτων· πάλιν τε ποταμοὺς"},
    {"folio": "50v", "start": 113, "end": 118, "first": "πλημμυροῦσι καὶ μειοῦσι καὶ πεδία λιμνάζουσι",
     "last": "κινεῖται τὰς ἁρμοττούσας σχέσεις καὶ κινήσεις ἕκαστον. ὁμοίως δὲ καὶ τοῦ"},
    {"folio": "51r", "start": 118, "end": 126, "first": "σώματος εἴ τις ἐξετάζειν ἐπιχειρήσειε τά τ’ ἐκτὸς καὶ ἐντὸς μέρη",
     "last": "χορείᾳ τὰς ἐλλογίμους ἁρμονίας ἀποτελεῖ, σχεδόν τι τῆς κατὰ μουσικὴν ὀργανο(ποιίας)"},
    {"folio": "51v", "start": 126, "end": 130, "first": "(ὀργανο)ποιίας ἁπάσης ἡγεμονὶς οὖσα· στοιχείων τε τῶν ἐν γραμματικῇ",
     "last": "ἀθρόα πάντα διεξελήλυθε φροντίζων εἴ καί τις ἄλλος βραχυλογίας, οὐδὲν ἧττον τὰ"},
    {"folio": "52r", "start": 130, "end": 134, "first": "ῥηθέντα ὀλίγα δείγματα τῆς τῶν συμπάντων ἐστὶ φύσεως",
     "last": "πάντα τὰ ζῷα. μετὰ δὲ ταῦτά φησιν ὅτι ἔπλασεν ὁ θεὸς τὸν ἄνθρωπον χοῦν λαβὼν ἀπὸ τῆς γῆς"},
    {"folio": "52v", "start": 134, "end": 138, "first": "καὶ ἐνεφύσησεν εἰς τὸ πρόσωπον αὐτοῦ πνοὴν ζωῆς. ἐναργέστατα καὶ διὰ τούτου",
     "last": "καὶ εὔχροιαν ἠνθογράφει βουλόμενος ὡς ἔνι μάλιστα κάλλιστον ὀφθῆναι τὸν πρῶτον"},
    {"folio": "53r", "start": 138, "end": 142, "first": "ἄνθρωπον. ὅτι δὲ καὶ τὴν ψυχὴν ἄριστος ἦν, φανερόν· οὐδενὶ γὰρ ἑτέρῳ παραδείγματι",
     "last": "φόβου μὲν ἐκτὸς ὤν, ἅτε τῆς τῶν περιγείων ἡγεμονίας ἀξιωθεὶς καὶ πάντων ὅσα"},
    {"folio": "53v", "start": 142, "end": 147, "first": "θνητὰ κατεπτηχότων ... δεδιδαγμένων ἢ βιασθέντων",
     "last": "τὸ σῶμα, λέγοιτ’ ἂν ἐνδίκως ἀεροπόρον εἶναι, πρὸς δὲ καὶ οὐράνιον, διὰ τῆς ἡγεμονικ(ωτάτης)"},
    {"folio": "54r", "start": 147, "end": 152, "first": "τῶν αἰσθήσεων ὄψεως ἡλίῳ καὶ σελήνῃ καὶ ἑκάστῳ τῶν ἄλλων ἀστέρων",
     "last": "ἡδονὴν ἐγέννησεν, ἥτις ἐστὶν ἀδικημάτων καὶ παρανομημάτων ἀρχή, δι’ ἣν ὑπαλλάττονται"},
    {"folio": "54v", "start": 152, "end": 156, "first": "τὸν θνητὸν καὶ κακοδαίμονα βίον ἀντ’ ἀθανάτου καὶ εὐδαίμονος",
     "last": "παντέλειαν, ὑφ’ ἧς μακραίωνα καὶ εὐδαίμονα βίον ἐδύναντο καρποῦσθαι, τὸν ἐφ(ήμερον)"},
    {"folio": "55r", "start": 156, "end": 161, "first": "καὶ θνητὸν οὐ βίον ἀλλὰ χρόνον κακοδαιμονίας μεστὸν εἵλοντο",
     "last": "δυσχεραίνοντα· παρὸ καὶ ἀνακλαίεται τὸ βρέφος ἀποκυηθέν, ἀλγῆσαν ὡς εἰκὸς τῇ περιψύξει"},
    {"folio": "55v", "start": 161, "end": 166, "first": "ἐκ γὰρ θερμοτάτου καὶ πυρωδεστάτου χωρίου τοῦ κατὰ τὴν μήτραν",
     "last": "ἡδονὴ γλίχεται τυχεῖν ἐραστοῦ καὶ μαστροποὺς ἀναζητεῖ, δι’ ὧν τοῦτον ἀγκισ(τρεύσεται)"},
    {"folio": "56r", "start": 166, "end": 171, "first": "μαστροπεύουσι δ’ αὐτῇ καὶ προξενοῦσι τὸν ἐρῶντα αἰσθήσεις",
     "last": "φαυλοτάτην τῶν κακοπολιτειῶν ὀχλοκρατίαν ἀπὸ γῆς εἰς οὐρανὸν μετοικίζοντες"},
    {"folio": "56v", "start": 171, "end": 172,
     "custom": ("Pal. gr. 248 fol. 56v: line 1 'τρίτον δ’ ὡς ἤδη λέλεκται ὅτι γενητὸς ὁ κόσμος' (section 171); "
                "section 172 begins 'ὁ δὴ ταῦτα μὴ ἀκοῇ μᾶλλον ἢ διανοίᾳ προμαθὼν' on line 10, and the treatise ends on line 14 "
                "'... δόγμασιν εὐσεβείας καὶ ὁσιότητος χαραχθείς'. Below a red headpiece follows the title of On the Decalogue "
                "('Φίλωνος περὶ τῶν δέκα λογίων ...') and its first words 'Τοὺς βίους τῶν κατὰ Μωυσέα σοφῶν ἀνδρῶν'.")},
]

PASSAGES = [
    {
        "slug": "on-the-creation", "order": 1, "tlg": "tlg001", "khaz": "opificig.htm",
        "work": "On the Creation", "ref": "Opif.", "range": (1, 172), "pages": OPIF_PAGES,
        "title": "Philo of Alexandria, On the Creation of the World (De opificio mundi)",
        "edition": "Leopold Cohn, Philonis Alexandrini opera quae supersunt I (Berlin: Reimer, 1896), pp. 1-60",
        "yonge": "C. D. Yonge, The Works of Philo Judaeus, vol. 1 (London: H. G. Bohn, 1854), pp. 1-52, 'A Treatise on the Account of the Creation of the World, as Given by Moses'",
        "yonge_url": "https://archive.org/details/worksphilojudaeu01philuoft",
        "date_approx": "c. 20-50 AD (composition); manuscript 14th-15th century",
        "description": "Philo's account of the six days of creation read as philosophy: God first conceives the intelligible world in his Logos, then makes the visible world after it; man is made in the image of God as to his mind. Complete, shown on the pages of the Vatican manuscript Pal. gr. 248.",
        "themes": ["philo", "creation", "logos", "image-of-god", "genesis", "platonism", "number-symbolism", "theosis", "philosophy", "greek", "verified"],
        "intro": (
            "<p><em>On the Creation of the World</em> opens Philo's exposition of the Law of Moses. Philo, a Jewish scholar of Alexandria writing in Greek in the first half of the first century AD, "
            "argues that Moses began his laws with the making of the world because the law agrees with the world and the man who keeps it is a citizen of the world. "
            "He reads the six days of Genesis 1-3 with the tools of Greek philosophy. God first formed in his own Logos (reason, word) an incorporeal, intelligible world, "
            "as an architect plans a city in his mind before building it (sections 16-25), and then made the visible world as a copy of it. "
            "Long passages on the numbers four and seven follow (sections 47-52, 89-128). "
            "Man 'after the image' is the mind, which rises through the heavens toward God (69-71); the moulded earthly man is 'the borderland between mortal and immortal nature' (135). "
            "The first man was a citizen of the world who tried 'to become like' the God who begot him (144). The work closes with five lessons: God exists, God is one, the world was made, the world is one, and God cares for it (170-172).</p>\n\n"
            "<p>The pages shown are from Vatican City, Biblioteca Apostolica Vaticana, Pal. gr. 248, a paper manuscript of the 14th or 15th century that collects Philo's works. "
            "On the Creation fills fols. 40v-56v, 33 pages of about 31-34 lines. Each section below is one section of Cohn's edition, linked to the page or pages that carry its words; "
            "the pages were identified by reading the first and last lines of each page on the image. "
            "The Greek is Cohn's critical text (1896), not a transcription of this manuscript, so its spelling and some words differ in places. "
            "The English is C. D. Yonge's translation of 1854, made from an earlier printed text. Yonge's sections do not always break at the same word as the Greek, "
            "and Yonge leaves out a few phrases; for example, the sentence on Hippocrates in section 124 is not in his translation.</p>"
        ),
    },
    {
        "slug": "confusion-of-tongues-146-147", "order": 2, "tlg": "tlg013", "khaz": "conf_lig.htm",
        "work": "On the Confusion of Tongues", "ref": "Conf.", "range": (146, 147),
        "title": "Philo of Alexandria, On the Confusion of Tongues 146-147: the Logos, God's firstborn and image",
        "edition": "Paul Wendland, Philonis Alexandrini opera quae supersunt II (Berlin: Reimer, 1897), pp. 229-267",
        "yonge": "C. D. Yonge, The Works of Philo Judaeus, vol. 2 (London: H. G. Bohn, 1854), 'A Treatise on the Confusion of Languages'",
        "yonge_url": "https://archive.org/details/worksphilojudaeu02philuoft",
        "date_approx": "c. 20-50 AD (composition); manuscript 14th-15th century",
        "description": "Philo on the Logos as God's 'firstborn', the eldest of the angels, an archangel of many names, called 'the Beginning', 'the Name of God', 'the Man after his image' and 'he that sees, Israel'; whoever is not yet fit to be called a son of God may be a son of his image, the Logos. Shown on Pal. gr. 248 fol. 205r.",
        "themes": ["philo", "logos", "firstborn", "image-of-god", "sons-of-god", "archangel", "theosis", "philosophy", "greek", "verified"],
        "pages": [{"folio": "205r", "start": 145, "end": 148,
                   "custom": ("Pal. gr. 248 fol. 205r (a different hand from On the Creation). Line 1 ends section 145 ('τῆς ἡδονῆς πρὸς ἐμπειροπολέμων ἀνδρῶν ἀντιτειχίζεται πρὸς'); "
                              "section 146 begins on line 2 with 'κἂν μηδέπω μέντοι τυγχάνῃ τις ἀξιόχρεως' and runs to 'Ἰσραὴλ προσαγορεύεται' on line 6; "
                              "section 147 runs from 'διὸ προήχθην' on line 6 to 'θεοῦ γὰρ εἰκὼν λόγος ὁ πρεσβύτατος' on line 10, followed by 'καὶ πολλαχοῦ μέντοι τῆς νομοθεσίας' (section 148).")}],
        "intro": (
            "<p><em>On the Confusion of Tongues</em> is one of Philo's allegorical commentaries on Genesis; it treats the tower of Babel (Genesis 11:1-9). "
            "Commenting on the brothers' words 'We are all sons of one man' (Genesis 42:11), Philo says that those who know the one God are rightly called sons of God (145). "
            "The two sections shown here add that one who is not yet worthy of that name should strive to be adorned after God's 'firstborn Logos, the eldest of the angels, an archangel as it were, who has many names': "
            "he is called the Beginning, the Name of God, the Logos, the Man after the image, and he that sees, Israel. "
            "If we are not yet fit to be called children of God, we may be children of his invisible image, the most holy Logos, 'for the most ancient Logos is the image of God' (146-147).</p>\n\n"
            "<p>The page shown is fol. 205r of Vatican City, Biblioteca Apostolica Vaticana, Pal. gr. 248 (14th-15th century), where this treatise occupies fols. 196v-208 in a hand different from that of On the Creation. "
            "Both sections stand on lines 2-10 of the page. The Greek is Wendland's critical text (1897); the English is C. D. Yonge's translation (1854).</p>"
        ),
    },
    {
        "slug": "who-is-the-heir-205-206", "order": 3, "tlg": "tlg015", "khaz": "heressig.htm",
        "work": "Who is the Heir of Divine Things", "ref": "Her.", "range": (205, 206),
        "title": "Philo of Alexandria, Who is the Heir of Divine Things 205-206: the Logos stands between Creator and creation",
        "edition": "Paul Wendland, Philonis Alexandrini opera quae supersunt III (Berlin: Reimer, 1898), pp. 1-71",
        "yonge": "C. D. Yonge, The Works of Philo Judaeus, vol. 2 (London: H. G. Bohn, 1854), 'Who is the Heir of Divine Things'",
        "yonge_url": "https://archive.org/details/worksphilojudaeu02philuoft",
        "date_approx": "c. 20-50 AD (composition); manuscript 14th-15th century",
        "description": "Philo on the archangel and eldest Logos, who stands on the border between the Creator and what he made, a suppliant for mortals and an ambassador of the ruler: 'neither uncreated as God, nor created as you, but midway between the extremes'. Shown on Pal. gr. 248 fol. 293r.",
        "themes": ["philo", "logos", "mediator", "archangel", "high-priest", "theosis", "philosophy", "greek", "verified"],
        "pages": [{"folio": "293r", "start": 201, "end": 208,
                   "custom": ("Pal. gr. 248 fol. 293r. The page runs from 'τῶν τεθνηκότων καὶ τῶν ζώντων· εὐθὺς γάρ φησι Μωυσῆς' (section 201) to "
                              "'μετόπωρον· τῷ μὲν γὰρ ἀνθεῖ, τῷ δὲ φθίνει τὰ ἔγγεια· πάλιν ὕδατος' (section 208). "
                              "Section 205 begins on line 18 with 'τῷ δὲ ἀρχαγγέλῳ καὶ πρεσβυτάτῳ λόγῳ', after '... φθορὰν οἰκτίστην ἐπιφέρουσα' (end of 204); "
                              "section 206 begins 'ἀγάλλεται δὲ ἐπὶ τῇ δωρεᾷ' in the middle of line 22 and ends with '... εἰρηνοφύλακος ἀεὶ θεοῦ', "
                              "after which 'διδάξας οὖν ἡμᾶς περὶ τῆς εἰς ἴσα τομῆς' (section 207) begins a new line.")}],
        "intro": (
            "<p><em>Who is the Heir of Divine Things</em> comments on Genesis 15, God's covenant with Abraham, and especially on the animals Abraham divided in two (Genesis 15:10). "
            "Philo reads the dividing as the work of the divine Logos, which cuts all things into their opposites. "
            "In the two sections shown, the Father who begot all things has given the archangel and eldest Logos a special gift: to stand on the border and separate the creature from the Creator. "
            "The same Logos pleads for mortal man before the immortal and carries the ruler's message to the subject, and says with Moses, 'I stood between the Lord and you' (Deuteronomy 5:5): "
            "'neither uncreated as God is, nor created as you are, but midway between the two extremes, a hostage to both'.</p>\n\n"
            "<p>The page shown is fol. 293r of Vatican City, Biblioteca Apostolica Vaticana, Pal. gr. 248 (14th-15th century), where this treatise occupies fols. 280v-300v in a third, more upright hand. "
            "Both sections stand in the lower middle of the page. The Greek is Wendland's critical text (1898); the English is C. D. Yonge's translation (1854).</p>"
        ),
    },
]


# ---------------------------------------------------------------------------
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def canvases():
    m = json.loads(MS["manifest"].read_text(encoding="utf-8"))
    out = {}
    for c in m["sequences"][0]["canvases"][6:]:   # skip binding and the two flyleaves (their labels 1r-2v repeat)
        out.setdefault(c["label"], {"service": c["images"][0]["resource"]["service"]["@id"],
                                    "file": c["images"][0]["resource"]["service"]["@id"].rsplit("/", 1)[1]})
    return out


def get_scan(folio, cv, force):
    path = SCAN_DIR / f"palgr248-f{folio}.jpg"
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"{cv[folio]['service']}/full/{MS['width']},/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def viewer(folio, cv):
    n = re.search(r"_(\d{4})_", cv[folio]["file"])
    return f"https://digi.vatlib.it/view/MSS_Pal.gr.248/{n.group(1)}" if n else MS["object"]


# ---------------------------------------------------------------------------
def tei_sections(path, eng=False):
    """Ordered (n, text) from a First1KGreek TEI file. Notes and heads dropped;
    <add> shown as angle brackets; <q> and <quote> in curly quotes; verse lines end with ' |'."""
    root = ET.parse(path).getroot()

    def txt(el):
        tag = el.tag.replace(TEI, "")
        if tag in ("note", "head"):
            return ""
        s = ""
        if tag == "add":
            s += "⟨"
        if tag == "q" or (tag == "quote" and el.get("rend") != "blockquote"):
            s += "“"
        if tag == "lg" or (tag == "quote" and el.get("rend") == "blockquote"):
            s += " | "
        if el.text:
            s += el.text
        for ch in el:
            s += txt(ch)
            if ch.tail:
                s += ch.tail
        if tag == "add":
            s += "⟩"
        if tag == "q" or (tag == "quote" and el.get("rend") != "blockquote"):
            s += "”"
        if tag == "l":
            s = s.rstrip() + " | "
        return s

    out = []
    for d in root.iter(TEI + "div"):
        if d.get("subtype") == "section":
            t = re.sub(r"\s+", " ", txt(d)).strip()
            t = re.sub(r"\s+([,.;·:])", r"\1", t).replace("“ ", "“").replace(" ”", "”")
            if not eng:   # Greek uses „ ... “ ; the digital text sometimes runs the closing mark into the next word
                t = re.sub(r"“(?=[^\s,.;·:)\]|])", "“ ", t)
            out.append((d.get("n"), t))
    return out


def khaz_sections(path):
    t = path.read_text(encoding="utf-8-sig")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t)
    parts = re.split(r"(?:^| )(\d+) \. ", t)
    return [(parts[i], parts[i + 1].replace("¦", " ")) for i in range(1, len(parts), 2)]


def norm(w):
    w = unicodedata.normalize("NFC", w).replace("’", "'").replace("᾿", "'")
    return re.sub(r"[,.;·:!?“”„\"«»()\[\]⟨⟩<>|—–\-]", "", w).lower()


def resegment(f1k, khz):
    """Re-split the First1KGreek word stream at the sentence-level section starts of
    the second digital text (words aligned with difflib)."""
    fw, fsec = [], []
    for n, t in f1k:
        for w in t.split():
            fw.append(w)
            fsec.append(n)
    kw, kstart = [], {}
    for n, t in khz:
        kstart[n] = len(kw)
        kw.extend(t.split())
    fn = [norm(w) for w in fw]
    kn = [norm(w) for w in kw]
    sm = difflib.SequenceMatcher(None, fn, kn, autojunk=False)
    k2f = {}
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal" or (a2 - a1 == b2 - b1):
            for i in range(b2 - b1):
                k2f[b1 + i] = a1 + i
    starts = {}
    for n, p in kstart.items():
        q = p
        while q not in k2f and q < len(kw):   # skip words absent from First1K (chapter numerals)
            q += 1
        starts[n] = k2f[q]
    names = [n for n, _ in f1k]
    for n in names:   # a section number the second text does not mark: keep First1K's own start
        starts.setdefault(n, fsec.index(n))
    out = []
    for i, n in enumerate(names):
        a = starts[n]
        b = starts[names[i + 1]] if i + 1 < len(names) else len(fw)
        out.append((n, " ".join(fw[a:b])))
    return out


def to_html(s):
    s = htmlmod.escape(s, quote=False)
    s = s.replace("⟨", "&lt;").replace("⟩", "&gt;")
    s = re.sub(r"\s*\|\s*", "<br>", s.strip())
    s = re.sub(r"(<br>)+$", "", s)
    return s


def page_note(p, cv):
    if p.get("custom"):
        return p["custom"] + " Viewer: " + viewer(p["folio"], cv)
    s = (f"{MS['short']} fol. {p['folio']} runs from '{p['first']}' on its first line (section {p['start']}) "
         f"to '{p['last']}' on its last line (section {p['end']}).")
    if p.get("extra"):
        s += " " + p["extra"]
    return s + " Viewer: " + viewer(p["folio"], cv)


def build(P, cv, force):
    grc_raw = tei_sections(SRC / f"tlg0018.{P['tlg']}.1st1K-grc1.xml")
    khz = khaz_sections(SRC / P["khaz"])
    grc = dict(resegment(grc_raw, khz))
    for (tlg, n), fixes in CORRECTIONS_GRC.items():
        if tlg == P["tlg"]:
            for rx, rep in fixes:
                new = rx.sub(rep, grc[n])
                assert new != grc[n], (tlg, n, "correction did not apply")
                grc[n] = new
    eng = dict(tei_sections(SRC / f"tlg0018.{P['tlg']}.1st1K-eng1.xml", eng=True))
    for a, b in CORRECTIONS_ENG.get(P["tlg"], []):
        for n in eng:
            eng[n] = eng[n].replace(a, b)
    files = {p["folio"]: get_scan(p["folio"], cv, force) for p in P["pages"]}
    sections = []
    for i in range(P["range"][0], P["range"][1] + 1):
        n = str(i)
        pages = [p for p in P["pages"] if p["start"] <= i <= p["end"]]
        assert pages, (P["slug"], n)
        if len(pages) == 1:
            note = f"On {MS['short']} fol. {pages[0]['folio']}. " + page_note(pages[0], cv)
        else:
            note = (f"Starts on fol. {pages[0]['folio']} and continues on fol. {pages[-1]['folio']} (page break inside this section). "
                    + " ".join(page_note(p, cv) for p in pages))
        note += " Checked on the images. The Greek shown is the critical edition, not a transcription of this manuscript."
        sections.append({
            "section": n,
            "original_ref": f"Philo, {P['ref']} {n} (Cohn-Wendland); {MS['short']} fol. " + ", ".join(p["folio"] for p in pages),
            "original_text": to_html(grc[n]),
            "text": to_html(eng[n]),
            "scan_pages": [f"{KEY}/{files[p['folio']].name}" for p in pages],
            "scan_note": note,
        })
    tid = PREFIX + P["slug"]
    folios = [p["folio"] for p in P["pages"]]
    fol_str = folios[0] + (f"-{folios[-1]}" if len(folios) > 1 else "")
    entry = {
        "id": tid, "slug": tid, "title": P["title"],
        "language": "Greek (Cohn-Wendland) / English (C. D. Yonge, 1854)",
        "source": f"{MS['shelfmark']} fol. {fol_str} ({MS['holder']}) + Cohn-Wendland Greek (First1KGreek) + C. D. Yonge English (1854, First1KGreek)",
        "description": P["description"],
        "introduction": P["intro"],
        "translator_notes": [
            f"Greek: {P['edition']}, digital text First1KGreek tlg0018.{P['tlg']}.1st1K-grc1. Square brackets mark words the editor deletes, angle brackets words he adds. Apparatus notes are not shown.",
            f"English: {P['yonge']}. Yonge translated from Mangey's edition of 1742, so his wording follows a slightly different Greek text; his section breaks follow the Scholer edition and a clause can fall on the neighbouring side of a break.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"{MS['holder']}: {MS['object']} (folios {', '.join(folios)}); IIIF manifest https://digi.vatlib.it/iiif/MSS_Pal.gr.248/manifest.json",
            "scan_license": MS["license"],
            "scan_manuscript": MS["desc"],
            "scan_mapping": "First and last lines of every page read on the image and matched to the Greek (words recorded in each scan_note); end of each page checked against the start of the next; folio range of the treatise from Pinakes diktyon 65980.",
            "scan_mapping_urls": [MS["pinakes"]] + [viewer(f, cv) for f in folios],
            "scan_local_paths": [f"{KEY}/{files[f].name}" for f in folios],
            "original_text_source": f"{P['edition']}; First1KGreek tlg0018.{P['tlg']}.1st1K-grc1 ({F1K}/{P['tlg']}); proofread against the Khazarzar digital text and the printed page where they differ",
            "original_text_license": "edition public domain; First1KGreek digital text CC BY-SA 4.0",
            "translation_source": f"{P['yonge']} ({P['yonge_url']}); digital text First1KGreek tlg0018.{P['tlg']}.1st1K-eng1 ({F1K}/{P['tlg']}), checked against the 1854 printing",
            "translation_license": "public domain (published 1854); First1KGreek digital text CC BY-SA 4.0",
            "translator": "C. D. Yonge (1854)",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": P["order"], "title": P["title"], "author_id": "philo",
        "language": "Greek", "era": "Second Temple", "tradition": "jewish", "category": "philosophy",
        "date_approx": P["date_approx"], "century": 1,
        "source": entry["source"], "description": P["description"], "themes": P["themes"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[f].name}", "caption": f"{MS['short']} fol. {f}"} for f in folios]},
    }
    print(f"wrote {tid} ({len(sections)} sections)")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cv = canvases()
    rows = [build(P, cv, args.force) for P in PASSAGES]
    coll = {
        "collection": {
            "key": KEY,
            "prefix": PREFIX,
            "label": "Philo of Alexandria: Creation and the Logos",
            "group": "Dead Sea Scrolls & Second Temple",
            "date_sort": 30,
            "author_name": "Philo of Alexandria (c. 20 BCE-c. 50 AD); Vatican manuscript Pal. gr. 248",
            "source_url": MS["object"],
            "critical_edition": "Cohn-Wendland, Philonis Alexandrini opera (1896-1898), via First1KGreek",
            "translator_name": "C. D. Yonge (1854)",
            "original_lang_label": "Greek · Cohn-Wendland",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "philo alexandria de opificio mundi creation logos image of god heir confusion of tongues firstborn archangel yonge",
            "description": "Philo of Alexandria's On the Creation of the World, complete, with his two best-known passages on the Logos, each section shown on the page of the Vatican Philo manuscript Pal. gr. 248 that carries it, with Cohn-Wendland's Greek and C. D. Yonge's English.",
        },
        "texts": rows,
        "authors": [
            {"id": "philo", "name": "Philo of Alexandria", "dates": "c. 20 BCE-c. 50 AD", "century": 1, "era": "Second Temple",
             "tradition": "jewish", "language": "Greek", "name_latin": "Philo Iudaeus",
             "bio": "Jewish philosopher of Alexandria who interpreted the Law of Moses with the concepts of Greek philosophy, above all through the idea of the divine Logos."},
        ],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
