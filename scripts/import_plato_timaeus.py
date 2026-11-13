#!/usr/bin/env python3
"""
import_plato_timaeus.py — Plato, Timaeus (complete), one entry per Stephanus page
(17-92), one section per Stephanus section (17a, 17b, ...), each section linked to the
folio side(s) of the oldest manuscript that carry it.

Also provides the shared builder used by import_plato_critias.py.

Chain of evidence:
  1. SCAN     Paris, Bibliotheque nationale de France, grec 1807 ("Plato A"), copied in
              Constantinople c. 850-875 (BnF catalogue). Timaeus fol. 114r-144v, Critias
              fol. 145r-151r (BnF description in the IIIF manifest). Two columns of 44 lines.
              Images: BnF IIIF Image API (openapi.bnf.fr), Gallica ark:/12148/btv1b8419248n.
              Rights: rightsstatements.org NoC-NC (no copyright, non-commercial use),
              credit "Source gallica.bnf.fr / BnF".
  2. MAPPING  Own visual check, no interpolation. The opening words of every column
              (fol. 114r col. b to 144v col. b; 145r col. a to 151r col. b) were read on the
              BnF images (top-of-column crops at full resolution) and located in Burnet's
              text. COLUMNS below records, for each column, its opening words as they stand
              in Burnet (the scribe's spelling differs in places). A Stephanus section is
              linked to every folio side whose columns contain part of it. The Timaeus
              starts in 114r col. b under the title; its last words (eis ouranos hode
              monogenes on) and the end title stand in 144v col. b. The Critias starts at
              the top of 145r col. a and breaks off in 151r col. b ("kai synageiras eipen"),
              the rest of the column being left blank.
  3. GREEK    John Burnet, Platonis Opera IV (Oxford 1902), Perseus canonical-greekLit
              tlg0059.tlg031 / tlg032 perseus-grc2 (CC BY-SA 4.0).
  4. ENGLISH  R. G. Bury, Plato IX: Timaeus, Critias, Cleitophon, Menexenus, Epistles
              (Loeb Classical Library, 1929), Perseus perseus-eng2. Published 1929, so in the
              US public domain since 1 Jan 2025; Perseus digital text CC BY-SA 4.0.
              Bury's footnotes are not reproduced.

Usage:
    python3 scripts/import_plato_timaeus.py           # build
    python3 scripts/import_plato_timaeus.py --force   # re-download scans
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

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "plato"
PUB_DIR = ROOT / "translations" / "published"
COLL_DIR = ROOT / "data" / "collections"
SCANS = ROOT / "site" / "assets" / "scans"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0059/{w}/tlg0059.{w}.{ed}.xml"
MANIFEST_URL = "https://openapi.bnf.fr/iiif/presentation/v3/ark:/12148/btv1b8419248n/manifest.json"
GALLICA = "https://gallica.bnf.fr/ark:/12148/btv1b8419248n"
BNF_CATALOGUE = "http://archivesetmanuscrits.bnf.fr/ark:/12148/cc19975p"
SCAN_WIDTH = 1650

MS_PARAGRAPH = (
    "<p>The manuscript is Paris, Bibliothèque nationale de France, <strong>grec 1807</strong>, known to editors as "
    "<strong>Plato A</strong>. It was copied in Constantinople around 850-875 by the scribe of the so-called philosophical "
    "collection, and is the oldest surviving medieval manuscript of the <em>Timaeus</em> and <em>Critias</em> (tetralogies VIII-IX: "
    "Clitophon, Republic, Timaeus, Critias, Minos, Laws, Epinomis, Letters). Each page has two columns of 44 lines. "
    "The <em>Timaeus</em> fills fol. 114r-144v and the <em>Critias</em> fol. 145r-151r.</p>"
)

# (folio, column, opening words of the column as they stand in Burnet's text; a leading
#  "-" marks a column that opens with the end of a word divided at the column break)
COLUMNS = [
    ("114r", "b", "εἷς, δύο, τρεῖς· ὁ δὲ δὴ"),
    ("114v", "a", "πόλεως, εἴτε τις ἔξωθεν ἢ καὶ"),
    ("114v", "b", "ἢ τοῦτο μὲν διὰ τὴν ἀήθειαν"),
    ("115r", "a", "ἦν τὰ λεχθέντα, ὦ Σώκρατες"),
    ("115r", "b", "τὸ δὲ τῶν σοφιστῶν γένος αὖ"),
    ("115v", "a", "σκεψάμενοι πρὸς ὑμᾶς αὐτοὺς εἰς νῦν"),
    ("115v", "b", "ἀληθοῦς, ὡς ὁ τῶν ἑπτὰ σοφώτατος"),
    ("116r", "a", "ποιητὴς εὐδοκιμώτερος ἐγένετο ἄν ποτε αὐτοῦ"),
    ("116r", "b", "πειρᾶσθαι διαμνημονεύων τοὺς χρόνους ἀριθμεῖν· καί"),
    ("116v", "a", "ὑπὸ τῶν ποταμῶν φέρονται· κατὰ δὲ"),
    ("116v", "b", "ἐξ ὧν σύ τε καὶ πᾶσα"),
    ("117r", "a", "σκόπει πρὸς τοὺς τῇδε· πολλὰ γὰρ"),
    ("117r", "b", "-εξαμένη πρῶτον κατῴκισεν. ᾠκεῖτε δὴ οὖν"),
    ("117v", "a", "τῆς δὲ Εὐρώπης μέχρι Τυρρηνίας. αὕτη"),
    ("117v", "b", "εἰπεῖν, ἀκήκοας· λέγοντος δὲ δὴ χθὲς"),
    ("118r", "a", "-φῆς ἔμμονά μοι γέγονεν· καὶ δὴ"),
    ("118r", "b", "τοῦ παντὸς εἰδέναι μάλιστα ἔργον πεποιημένον"),
    ("118v", "a", "μάλιστʼ ἂν περὶ τῶν προκειμένων ἐνδειξαίμην"),
    ("118v", "b", "-τέρα τοῦδε τοῦ παντὸς εὑρεῖν τε"),
    ("119r", "a", "πάντῃ πάντως αὐτοὺς ἑαυτοῖς ὁμολογουμένους λόγους"),
    ("119r", "b", "νοῦν δʼ αὖ χωρὶς ψυχῆς ἀδύνατον"),
    ("119v", "a", "ἐκείνῳ τῷ περιέχοντι τόδʼ ἂν ἀφωμοιωμένον"),
    ("119v", "b", "νῦν δὲ στερεοειδῆ γὰρ αὐτὸν προσῆκεν"),
    ("120r", "a", "ἐξ ἁπάντων τέλεον καὶ ἀγήρων καὶ"),
    ("120r", "b", "περὶ νοῦν καὶ φρόνησιν μάλιστα οὖσαν"),
    ("120v", "a", "-χούσης οὐσίας καὶ τῆς αὖ περὶ"),
    ("120v", "b", "τούτων τῶν δεσμῶν ἐν ταῖς πρόσθεν"),
    ("121r", "a", "ἐπεὶ δὲ κατὰ νοῦν τῷ συνιστάντι"),
    ("121r", "b", "ψυχὴν διαγγείλῃ, δόξαι καὶ πίστεις γίγνονται"),
    ("121v", "a", "τὸ ἔστιν μόνον κατὰ τὸν ἀληθῆ"),
    ("121v", "b", "ἀριθμῶν χρόνου γέγονεν· σώματα δὲ αὐτῶν"),
    ("122r", "a", "τὸ βραδύτατα ἀπιὸν ἀφʼ αὑτῆς οὔσης"),
    ("122r", "b", "-μοιότατον ᾖ τῷ τελέῳ καὶ νοητῷ"),
    ("122v", "a", "τῆς αἰτίας γέγονεν ὅσʼ ἀπλανῆ τῶν"),
    ("122v", "b", "παισὶν ἀπιστεῖν, καίπερ ἄνευ τε εἰκότων"),
    ("123r", "a", "-τα γενόμενα καὶ βίου μετασχόντα θεοῖς"),
    ("123r", "b", "-σοιτο ἀνήρ. ΤΙ. ὁπότε δὴ σώμασιν"),
    ("123v", "a", "-ρέδωκεν θεοῖς σώματα πλάττειν θνητά, τό"),
    ("123v", "b", "ἓξ τόπους πλανώμενα προῄειν. πολλοῦ γὰρ"),
    ("124r", "a", "τοτὲ δὲ ὑπτίας· οἷον ὅταν τις"),
    ("124r", "b", "ἀποτελοῦσιν. ἂν μὲν οὖν δὴ καὶ"),
    ("124v", "a", "-ρειδόμενον διὰ πάντων τόπων πορεύεσθαι δυνατὸν"),
    ("124v", "b", "-δῃ τὸ προσπῖπτον ἔνδοθεν πρὸς ὃ"),
    ("125r", "a", "ἐξ ἀνάγκης ἐμφαίνεται, τοῦ περὶ τὸ"),
    ("125r", "b", "-νων, ἕτερα δὲ κατὰ ἀνάγκης κινούντων"),
    ("125v", "a", "ἐπὶ τὰς περιφορὰς τὰς τῆς παρʼ"),
    ("125v", "b", "συστάσεως ἐγεννήθη· νοῦ δὲ ἀνάγκης ἄρχοντος"),
    ("126r", "a", "διαφυλάττων, τὴν τῶν εἰκότων λόγων δύναμιν"),
    ("126r", "b", "τινὶ πιστῷ καὶ βεβαίῳ χρήσασθαι λόγῳ"),
    ("126v", "a", "-δείκνυται φάσις. ἀλλὰ ταῦτα μὲν ἕκαστα"),
    ("126v", "b", "-σχηματιζόμενον ὑπὸ τῶν εἰσιόντων, φαίνεται δὲ"),
    ("127r", "a", "τῶν πάντων ἀεί τε ὄντων κατὰ"),
    ("127r", "b", "μέγας διὰ βραχέων φανείη, τοῦτο μάλιστα"),
    ("127v", "a", "νόθῳ, μόγις πιστόν, πρὸς ὃ δὴ"),
    ("127v", "b", "ταλαντουμένην σείεσθαι μὲν ὑπʼ ἐκείνων αὐτήν"),
    ("128r", "a", "διʼ ὧν ἐνδείκνυσθαι τὰ λεγόμενα ἀνάγκη"),
    ("128r", "b", "μίαν εἴληχεν φύσιν, τὸ δὲ πρόμηκες"),
    ("128v", "a", "-σήκοντα ἑαυτοῖς σχήματα, καὶ σμικρὰ ὅταν"),
    ("128v", "b", "-νιῶν δώδεκα, ὑπὸ πέντε ἐπιπέδων τριγώνων"),
    ("129r", "a", "τῶν τεττάρων γενῶν γῆ καὶ τῶν"),
    ("129r", "b", "-τα οὐδὲν ὁρώμενον ὑφʼ ἡμῶν, συναθροισθέντων"),
    ("129v", "a", "πάλιν, ὡς ὅταν ἐν πυρὶ λαμβανόμενον"),
    ("129v", "b", "ἕτερα ἐμπεφυκέναι γένη τὴν ἑκατέρου τῶν"),
    ("130r", "a", "-νὴν χώραν οὐδεμίαν ἐᾷ λείπεσθαι. διὸ"),
    ("130r", "b", "τε καθʼ αὑτὸ καὶ ὑπʼ ἄλλου"),
    ("130v", "a", "πυκνότητα σκληρότατον ὂν καὶ μελανθέν, ἀδάμας"),
    ("130v", "b", "ὑπὲρ γῆς μάλιστα παθὸν ταῦτα χάλαζα"),
    ("131r", "a", "οὖν πλησίον ἔωσεν ἀέρα. ὁ δὲ"),
    ("131r", "b", "μόνον λύει, συνεστηκυῖαν δὲ πλὴν πυρὸς"),
    ("131v", "a", "τυγχάνει δὲ οὔτε ταῦτα χωρὶς τῶν"),
    ("131v", "b", "-γαζόμενα πήγνυσιν· τὸ δὲ παρὰ φύσιν"),
    ("132r", "a", "πέριξ οὔτε δὴ μέσος οὔτʼ ἔχων"),
    ("132r", "b", "φερόμενον κληθῆναι, τὸ δὲ σμικρὸν ἐλαφρὸν"),
    ("132v", "a", "-μαλότητι μειχθεῖσα, τὸ δʼ ὁμαλότης πυκνότητι"),
    ("132v", "b", "τὸ δὴ τῆς ἡδονῆς καὶ λύπης"),
    ("133r", "a", "κατὰ σμικρὰ δὲ μόγις τε εἰς"),
    ("133r", "b", "-μασται, τὰ δὲ ὑποδεέστερα τῆς λιτρώδους"),
    ("133v", "a", "εἰρημένοις πάθος ἐναντίον ἀπʼ ἐναντίας ἐστὶ"),
    ("133v", "b", "ἀναπνοὴν ἄγῃ τις βίᾳ τὸ πνεῦμα"),
    ("134r", "a", "-γα τῶν σωμάτων ἑκάστων ἀπορρέουσαν, ὄψει"),
    ("134r", "b", "-νυμένου, παντοδαπῶν ἐν τῇ κυκήσει ταύτῃ"),
    ("134v", "a", "ἂν εἴη διάφορον, ὅτι θεὸς μὲν"),
    ("134v", "b", "ἑκάστῳ τε αὐτῷ πρὸς αὑτὸ καὶ"),
    ("135r", "a", "καὶ τοῦ στήθους, αὐχένα μεταξὺ τιθέντες"),
    ("135r", "b", "-τες ὅτι διὰ πυρὸς ἡ τοιαύτη"),
    ("135v", "a", "-ταῦθʼ ἔδοσαν αὐτῷ τὴν τάξιν. εἰδότες"),
    ("135v", "b", "-μένη καὶ πάντα ὀρθὰ καὶ λεῖα"),
    ("136r", "a", "γένος ἐπὶ ταῖς ἐνθέοις μαντείαις κριτὰς"),
    ("136r", "b", "-ριζοίμεθα· τό γε μὴν εἰκὸς ἡμῖν"),
    ("136v", "a", "γένος· αὐτὸς δὲ ὁ μυελὸς γέγονεν"),
    ("136v", "b", "-αν ἐφύρασε καὶ ἔδευσεν μυελῷ, καὶ"),
    ("137r", "a", "σώμασιν μαλακῶς καὶ πρᾴως ὑπείκουσαν, θερμὴν"),
    ("137r", "b", "ἐμπεπιλημέναι, διὰ στερεότητα ἀναισθησίαν ἐμποιοῦσαι, δυσμνη"),
    ("137v", "a", "ὀστῷ, σαρξὶν δὲ καὶ νεύροις κεφαλήν"),
    ("137v", "b", "δὲ διὰ τὴν περὶ τὸν ἐγκέφαλον"),
    ("138r", "a", "-φαλον ἕνεκα ἀσφαλείας κοῦφον καὶ θέρους"),
    ("138r", "b", "-σχεν, πρὶν δὲ ἦν μόνα τὰ"),
    ("138v", "a", "κάταντες ἡ ἐπίχυσις γιγνομένη παρέχοι τὴν"),
    ("138v", "b", "κατὰ τὴν εἴσοδον ἐγκύρτια ἔχον, ὧν"),
    ("139r", "a", "τῷ σώματι γέγονεν ἀρδομένῳ καὶ ἀναψυχομένῳ"),
    ("139r", "b", "τὴν τοῦ στόματος καὶ τὴν τῶν"),
    ("139v", "a", "-χεῖς τε καὶ βραδεῖς ὀξεῖς τε"),
    ("139v", "b", "-ναπνοῆς, ὅθεν ὁ λόγος ὥρμησεν, κατὰ"),
    ("140r", "a", "-τὸς ἀναγκάζεται μιμεῖσθαι φοράν· πρὸς τὸ"),
    ("140r", "b", "παρὰ φύσιν ἀλγεινόν, τὸ δʼ ᾗ"),
    ("140v", "a", "-σις νοσημάτων τῷ βουλομένῳ γίγνεται συννοῆσαι"),
    ("140v", "b", "-ρετα γὰρ πάντα γεγονότα καὶ διεφθαρμένα"),
    ("141r", "a", "ὁ δὲ μελαίνης χολῆς ὀξείας τε"),
    ("141r", "b", "τότε ταῦτα πάσχον πᾶν τὸ τοιοῦτον"),
    ("141v", "a", "-θα μὲν οὐκ ἰόν, ἔνθα δὲ"),
    ("141v", "b", "-ταράττον αὐτάς, καθʼ ὕπνον μὲν ἰὸν"),
    ("142r", "a", "καὶ ὑγρὰ κατʼ ὀλίγον τὸ πρῶτον"),
    ("142r", "b", "δύο δʼ ἀνοίας γένη, τὸ μὲν"),
    ("142v", "a", "τροφὴν ὁ κακὸς γίγνεται κακός, παντὶ"),
    ("142v", "b", "δὲ τούτων ἀντίστροφον αὖ, τὸ περὶ"),
    ("143r", "a", "διασείουσα πᾶν αὐτὸ ἔνδοθεν νόσων ἐμπίμπλησι"),
    ("143r", "b", "-μενον εἶδος. τοῦ γὰρ σώματος ὑπὸ"),
    ("143v", "a", "γίγνωνται· τρίτον δὲ εἶδος κινήσεως σφόδρα"),
    ("143v", "b", "παιδαγωγῆσον αὐτὸ μᾶλλόν που καὶ πρότερον"),
    ("144r", "a", "θνητὰ ἐγγεγονέναι, καὶ παντάπασιν καθʼ ὅσον"),
    ("144r", "b", "ἄλλα ζῷα ᾗ γέγονεν αὖ, διὰ"),
    ("144v", "a", "ἄκαρπον παρὰ τὴν ὥραν χρόνον πολὺν"),
    ("144v", "b", "-ας ἔσχον τὰς κορυφάς, ὅπῃ συνεθλίφθησαν"),
]

TOPICS = {
    17: "Socrates counts the guests and recalls yesterday's discussion of the best city",
    18: "the recapitulation continued: guardians, women, marriages and children",
    19: "Socrates wishes to see the city he described in action",
    20: "the speakers' qualifications; Critias introduces the story Solon brought from Egypt",
    21: "Critias heard the story as a boy at the Apaturia; Solon at Sais",
    22: "the Egyptian priest: 'you Greeks are always children'; floods and conflagrations",
    23: "Egypt keeps the old records; the ancient Athens destroyed by flood",
    24: "the laws of ancient Athens compared with Egypt's; the power from the Atlantic Ocean",
    25: "Atlantis, its empire and its defeat by Athens; the island sinks into the sea",
    26: "Critias recalled the story overnight; it will be fitted to Socrates' city",
    27: "the order of the speeches; Timaeus' invocation; Being and Becoming",
    28: "whatever becomes has a cause; the maker and father of the universe",
    29: "the world is a copy of an eternal model; a likely account; the maker was good",
    30: "order out of disorder; the world a living creature with soul and reason",
    31: "one world, not many; the body of the world made of fire and earth",
    32: "proportion: air and water placed between fire and earth",
    33: "the world uses all four elements; its spherical shape",
    34: "the rotation of the world; the world soul",
    35: "the soul compounded of Same, Different and Being; the first divisions",
    36: "the harmonic intervals; the circles of the Same and the Different",
    37: "the knowledge of the world soul; time, the moving image of eternity",
    38: "was, is and will be; sun, moon and planets made to mark time",
    39: "the motions of the planets; day, month and year; the perfect year",
    40: "the fixed stars, the earth and the traditional gods",
    41: "the maker's speech to the gods; the mixing of souls",
    42: "souls sown in the stars; the young gods shape mortal bodies",
    43: "the soul enters the body; the six motions disturb its circles",
    44: "how the soul regains its reason; the head and the body",
    45: "limbs, face and eyes; how vision works",
    46: "dreams and mirrors; auxiliary causes",
    47: "the purpose of sight, hearing and voice",
    48: "Reason and Necessity; a new beginning",
    49: "the receptacle, nurse of all becoming; the elements pass into one another",
    50: "the receptacle compared to gold that takes every shape",
    51: "is there a Form of fire? reason and true opinion",
    52: "Form, copy and space; the shaking of the receptacle",
    53: "the god gives the elements shapes; the two kinds of triangle",
    54: "the most beautiful triangles; the construction of the solids",
    55: "pyramid, octahedron, icosahedron and cube",
    56: "earth the cube, water the icosahedron, air the octahedron, fire the pyramid",
    57: "the transformation of the elements; motion and rest",
    58: "why motion never stops; the kinds of fire and air",
    59: "the kinds of water: gold, bronze, ice, snow",
    60: "juices, oil and honey; the kinds of earth",
    61: "solution of earth; the sensible qualities begin with heat",
    62: "hot and cold, hard and soft, heavy and light",
    63: "up and down; heavy and light defined",
    64: "rough and smooth; pleasure and pain",
    65: "pleasure and pain continued; tastes",
    66: "tastes continued; smells",
    67: "smells and sounds; colour as a flame",
    68: "the colours and their mixtures",
    69: "the two kinds of cause; the mortal soul placed in the chest",
    70: "the heart and lungs; the appetite below the midriff",
    71: "the liver and its images",
    72: "divination and its interpreters; the spleen",
    73: "the intestines; the marrow",
    74: "vertebrae, bone, sinew and flesh",
    75: "flesh and intelligence; the head and the mouth",
    76: "skin, hair and nails",
    77: "plants; the channels of the body",
    78: "the fish-trap: the mechanism of breathing",
    79: "breathing continued",
    80: "projectiles, sounds and other motions; digestion and the blood",
    81: "nourishment, growth and decline; death",
    82: "diseases arising from the four elements",
    83: "diseases of flesh and blood; bile",
    84: "diseases of bone and marrow; of breath",
    85: "phlegm; the sacred disease; fevers",
    86: "diseases of the soul: madness and ignorance",
    87: "bad constitution and education; proportion between body and soul",
    88: "exercise of body and soul",
    89: "gymnastics and medicine; regimen",
    90: "the care of the divine part in us",
    91: "the origin of women and of the animals",
    92: "fishes and shellfish; the world a visible god",
}
ATLANTIS_PAGES = {20, 21, 22, 23, 24, 25}

WORK = {
    "key": "plato-timaeus", "name": "Timaeus", "abbr": "Tim.", "tlg": "tlg031",
    "columns": COLUMNS, "topics": TOPICS, "atlantis_pages": ATLANTIS_PAGES,
    "first_folio": "114r", "last_folio": "144v",
    # Bury's 17b and 18b milestones fall inside a reply of Timaeus that Burnet's Greek has wholly in
    # 17b / 18b; the English reply is moved whole to the section that holds the Greek.
    "english_moves": [
        ("17a", "17b", "Undoubtedly, and we shall do our best",
         "English: Timaeus' reply πάνυ μὲν οὖν ... ἀνταφεστιᾶν stands wholly in 17b in the Greek; Bury's 17b milestone falls inside "
         "it, so his English of the reply (Undoubtedly ... cordially in return.) is given whole with 17b."),
        ("18a", "18b", "Certainly.",
         "English: Timaeus' reply πάνυ μὲν οὖν stands in 18b in the Greek; Bury's 18b milestone falls after it, so his English "
         "of the reply (Certainly.) is given with 18b."),
    ],
}


# ---------------------------------------------------------------- downloads
def fetch(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def source_xml(tlg, ed):
    path = SRC / f"tlg0059.{tlg}.{ed}.xml"
    if not path.exists():
        SRC.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fetch(PERSEUS.format(w=tlg, ed=ed)))
    return path


def manifest():
    path = SRC / "iiif" / "grec1807-manifest.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fetch(MANIFEST_URL))
    man = json.loads(path.read_text(encoding="utf-8"))
    return {c["label"]["fr"][0]: (i + 1, c["items"][0]["items"][0]["body"]["id"].split("/full/")[0])
            for i, c in enumerate(man["items"])}


def get_scan(key, folio, canvases, force=False):
    from PIL import Image
    out_dir = SCANS / key
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"grec1807-f{folio}.jpg"
    if path.exists() and path.stat().st_size > 50_000 and not force:
        return path
    _, svc = canvases[folio]
    img = Image.open(io.BytesIO(fetch(f"{svc}/full/{SCAN_WIDTH},/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


# ---------------------------------------------------------------- text
# Perseus splits a long speech into several <said rend="merge"> (and quoted speech into several
# <q rend="merge">) at its card boundaries, repeating the speaker label each time. A merged <q>
# continues the quotation, so it gets no new opening mark, and the <q> it continues gets no
# closing mark. Repeated labels are marked "label_dup" in sections(): kept for locating column
# openings (plain()), not shown (to_html()).
_Q_CONTINUED = set()


def _mark_continued_quotes(body):
    """ids of <q> elements whose quotation is continued by a later <q rend="merge"> at the same depth."""
    events, counter = [], [0]

    def walk(el, depth):
        tag = el.tag.replace(TEI, "")
        is_q = tag in ("q", "quote") and el.get("type") not in ("emph", "foreign", "mentioned")
        start = counter[0]
        counter[0] += 1
        for ch in el:
            walk(ch, depth + (1 if is_q else 0))
        if is_q:
            events.append((start, counter[0], depth, el))
        counter[0] += 1
    walk(body, 0)
    events.sort(key=lambda e: e[0])
    for i, (s, e, d, el) in enumerate(events):
        later = [x for x in events[i + 1:] if x[0] > e]
        nxt = next((x for x in later if x[2] == d), None)
        if not nxt or nxt[3].get("rend") != "merge":
            continue
        # every enclosing quotation opened in between must itself be a continuation
        if all(x[3].get("rend") == "merge" for x in later if x[0] < nxt[0] and x[2] < d):
            _Q_CONTINUED.add(id(el))


def _tokens(el, out, lang, qdepth=0):
    tag = el.tag.replace(TEI, "")
    if tag in ("note", "teiHeader", "head", "bibl"):
        if el.tail:
            out.append(("t", el.tail))
        return
    if tag == "milestone":
        if el.get("unit") == "section":
            out.append(("ms", el.get("n")))
    elif tag == "label":
        out.append(("label", "".join(el.itertext()).strip()))
    else:
        if tag == "p":
            out.append(("para", None))
        wrap = None
        if lang == "eng" and tag in ("q", "quote"):
            if el.get("type") in ("emph", "foreign", "mentioned"):
                wrap = ("em", "em")
            else:
                # outer quotation “ ”, a quotation inside it ‘ ’
                o, c = ("“", "”") if qdepth % 2 == 0 else ("‘", "’")
                wrap = ("" if el.get("rend") == "merge" else o, "" if id(el) in _Q_CONTINUED else c)
        elif tag == "emph":
            wrap = ("em", "em")
        if wrap == ("em", "em"):
            out.append(("open", "em"))
        elif wrap and wrap[0]:
            out.append(("t", wrap[0]))
        if el.text:
            out.append(("t", el.text))
        for ch in el:
            _tokens(ch, out, lang, qdepth + (1 if wrap and wrap != ("em", "em") else 0))
        if wrap == ("em", "em"):
            out.append(("close", "em"))
        elif wrap and wrap[1]:
            out.append(("t", wrap[1]))
    if el.tail:
        out.append(("t", el.tail))


def sections(path, lang):
    """Return (ordered section ids, {id: [tokens]}) split at Stephanus section milestones.
    A speaker label that repeats the previous label (same speaker, speech continued after a
    Perseus card break) becomes "label_dup" and is not shown."""
    body = ET.parse(path).getroot().find(f".//{TEI}body")
    _mark_continued_quotes(body)
    toks = []
    _tokens(body, toks, lang)
    last = None
    for i, (kind, v) in enumerate(toks):
        if kind == "label":
            who = v.rstrip(".").strip().lower()
            if who == last:
                toks[i] = ("label_dup", v)
            last = who
    order, secs, cur = [], {}, None
    for kind, v in toks:
        if kind == "ms":
            cur = v
            order.append(v)
            secs[v] = []
        elif cur is not None:
            secs[cur].append((kind, v))
    return order, secs


def plain(items):
    """Plain text of a section (speaker labels included), used to locate column openings."""
    paras = [[]]
    for kind, v in items:
        if kind == "para":
            if paras[-1]:
                paras.append([])
        elif kind in ("label", "label_dup"):
            paras[-1].append(v + " ")
        elif kind == "t":
            paras[-1].append(v)
    return " ".join(re.sub(r"\s+", " ", "".join(p)).strip() for p in paras if "".join(p).strip())


def to_html(items):
    """Section HTML: one <p> per speech/paragraph, speaker label at its head, <em> kept."""
    paras, cur, only_label = [], [], False
    open_em = 0

    def flush():
        txt = re.sub(r"\s+", " ", "".join(cur)).strip()
        if txt:
            txt = txt + "</em>" * open_em
            paras.append(txt)

    for kind, v in items:
        if kind == "label":
            flush()
            cur = ["<em>" * open_em, html.escape(v, quote=False) + " "]
            only_label = True
        elif kind == "para":
            if not only_label:
                flush()
                cur = ["<em>" * open_em]
        elif kind == "open":
            cur.append("<em>")
            open_em += 1
        elif kind == "close":
            if open_em:
                cur.append("</em>")
                open_em -= 1
        elif kind == "label_dup":
            continue
        else:
            if v.strip():
                only_label = False
            cur.append(html.escape(v, quote=False))
    flush()
    out = []
    for p in paras:
        p = re.sub(r"<em>\s*</em>", "", p).strip()
        if re.sub(r"<[^>]+>", "", p).strip():
            out.append(f"<p>{p}</p>")
    return "\n".join(out)


def norm_letters(s):
    out = []
    for ch in s:
        base = "".join(c for c in unicodedata.normalize("NFD", ch) if not unicodedata.combining(c)).lower()
        base = base.replace("ς", "σ")
        if base and "α" <= base <= "ω":
            out.append(base)
    return "".join(out)


def locate_columns(order, plain_by_sec, columns):
    """Normalised letter offsets: section starts, and each column's start (found in reading order)."""
    sec_start, text = {}, []
    pos = 0
    for s in order:
        sec_start[s] = pos
        n = norm_letters(plain_by_sec[s])
        text.append(n)
        pos += len(n)
    full = "".join(text)
    starts, prev = [], 0
    for i, (fol, col, opening) in enumerate(columns):
        q = norm_letters(opening.lstrip("-"))
        at = full.find(q, prev)
        assert at >= 0, f"column opening not found: {fol} {col} {opening}"
        assert i == 0 or at - prev < 1600, f"column {fol}{col} too far from previous ({at - prev})"
        starts.append(at)
        prev = at
    return sec_start, len(full), starts, full


def section_of(pos, order, sec_start):
    cur = order[0]
    for s in order:
        if sec_start[s] <= pos:
            cur = s
        else:
            break
    return cur


def span_text(cols):
    first, last = cols[0], cols[-1]
    if first == last:
        return f"fol. {first[0]} col. {first[1]}"
    return f"fol. {first[0]} col. {first[1]} to fol. {last[0]} col. {last[1]}"


def folio_range(folios):
    return folios[0] if len(folios) == 1 else f"{folios[0]}-{folios[-1]}"


# ---------------------------------------------------------------- build
def build(work, force=False):
    key, name, abbr = work["key"], work["name"], work["abbr"]
    g_order, g_secs = sections(source_xml(work["tlg"], "perseus-grc2"), "grc")
    e_order, e_secs = sections(source_xml(work["tlg"], "perseus-eng2"), "eng")
    assert g_order == e_order, "Greek and English Stephanus sections differ"
    # Where Bury's word order puts a whole English sentence on the other side of a Stephanus
    # milestone from the Greek it renders, the sentence is moved whole to the section that holds
    # most of the Greek (work["english_moves"]: (from, to, opening words of the moved English)).
    move_notes = {}
    for frm, to, phrase, note in work.get("english_moves", []):
        toks = e_secs[frm]
        k = next(i for i, (kind, v) in enumerate(toks) if kind == "t" and phrase in v)
        kind, v = toks[k]
        cut = v.index(phrase)
        head = k
        if not v[:cut].strip():          # a whole speech: take its paragraph start and label too
            def blank(t):
                return t[0] in ("para", "label", "label_dup") or (t[0] == "t" and not t[1].strip())
            while head > 0 and blank(toks[head - 1]):
                head -= 1
        moved = toks[head:k] + ([("t", v[cut:])] if v[cut:] else []) + toks[k + 1:]
        e_secs[frm] = toks[:head] + ([("t", v[:cut])] if v[:cut].strip() else [])
        assert to == e_order[e_order.index(frm) + 1], (frm, to)
        e_secs[to] = moved + e_secs[to]
        move_notes[frm] = move_notes.get(frm, "") + " " + note
        move_notes[to] = move_notes.get(to, "") + " " + note
    plain_by_sec = {s: plain(g_secs[s]) for s in g_order}
    sec_start, total, col_starts, _ = locate_columns(g_order, plain_by_sec, work["columns"])
    columns = work["columns"]
    col_ranges = [(col_starts[i], col_starts[i + 1] if i + 1 < len(columns) else total) for i in range(len(columns))]

    canvases = manifest()
    folios = []
    for fol, _, _ in columns:
        if fol not in folios:
            folios.append(fol)
    for fol in folios:
        get_scan(key, fol, canvases, force)

    # Section -> columns that carry part of it
    sec_cols = {}
    for i, s in enumerate(g_order):
        a = sec_start[s]
        b = sec_start[g_order[i + 1]] if i + 1 < len(g_order) else total
        sec_cols[s] = [j for j, (c, d) in enumerate(col_ranges) if a < d and c < b]
        assert sec_cols[s], s

    # Boundary check: column openings that fall close to a section boundary
    for j, st in enumerate(col_starts):
        s = section_of(st, g_order, sec_start)
        if 0 < st - sec_start[s] < 20:
            print(f"  note: {columns[j][0]}{columns[j][1]} opens {st - sec_start[s]} letters after the start of {s}")

    pages = {}
    for s in g_order:
        pages.setdefault(int(re.match(r"\d+", s).group()), []).append(s)

    rows, n_sec = [], 0
    for order_n, (page, secs) in enumerate(sorted(pages.items()), 1):
        tid = f"verified-{key}-{page}"
        rng = f"{secs[0]}-{secs[-1]}" if len(secs) > 1 else secs[0]
        page_cols = sorted({j for s in secs for j in sec_cols[s]})
        page_folios = []
        for j in page_cols:
            if columns[j][0] not in page_folios:
                page_folios.append(columns[j][0])
        topic = work["topics"][page]
        is_atl = page in work["atlantis_pages"]

        translation = []
        for s in secs:
            cols = [columns[j] for j in sec_cols[s]]
            sfol = []
            for c in cols:
                if c[0] not in sfol:
                    sfol.append(c[0])
            evidence = "; ".join(
                f"fol. {columns[j][0]} col. {columns[j][1]} begins ‹{columns[j][2]}› ({abbr} {section_of(col_starts[j], g_order, sec_start)})"
                for j in sec_cols[s])
            translation.append({
                "section": s,
                "original_ref": f"Plato, {name} {s}; Paris gr. 1807, {span_text(cols)}",
                "original_text": to_html(g_secs[s]),
                "text": to_html(e_secs[s]),
                "scan_pages": [f"{key}/grec1807-f{f}.jpg" for f in sfol],
                "scan_note": (f"{abbr} {s} stands in Paris gr. 1807, {span_text(cols)}. Checked on the image (column openings "
                              f"read on the BnF photographs and found in Burnet's text, quoted in Burnet's spelling): {evidence}."
                              + move_notes.get(s, "")),
            })
        n_sec += len(translation)

        col_list = "; ".join(
            f"fol. {columns[j][0]} col. {columns[j][1]} begins ‹{html.escape(columns[j][2], quote=False)}› ({abbr} {section_of(col_starts[j], g_order, sec_start)})"
            for j in page_cols)
        intro = [f"<p>Stephanus page {page} of Plato's <em>{name}</em> ({rng}): {html.escape(topic, quote=False)}.</p>"]
        if is_atl:
            intro.append(work["atlantis_note"] if "atlantis_note" in work else ATLANTIS_NOTE)
        intro.append(MS_PARAGRAPH)
        intro.append(f"<p>On the manuscript this page of text runs over {span_text([columns[page_cols[0]], columns[page_cols[-1]]])}. "
                     f"Each section below is linked to the folio side(s) that carry it. The mapping comes from reading the first words "
                     f"of every column on the images and finding them in Burnet's text: {col_list}.</p>")
        intro.append("<p>The Greek is John Burnet's critical text (Oxford, 1902), not a transcription of this manuscript; the scribe's "
                     "spelling, accents and occasional readings differ from it. The English is R. G. Bury's Loeb translation (1929).</p>")
        f_rng = folio_range(page_folios)
        entry = {
            "id": tid, "slug": tid,
            "title": f"Plato, {name} {rng}: {topic}",
            "language": "Greek (Burnet 1902) / English (R. G. Bury 1929)",
            "source": (f"Paris, BnF grec 1807 (Plato A, c. 850-875) fol. {f_rng} via BnF IIIF + Burnet's Greek (Perseus) + "
                       f"R. G. Bury's English (Loeb 1929, Perseus)"),
            "description": (f"Plato, {name} {rng} ({topic}), shown on the 9th-century manuscript Paris gr. 1807 fol. {f_rng}, "
                            f"with Burnet's Greek and R. G. Bury's English."),
            "introduction": "\n\n".join(intro),
            "translator_notes": [
                "Greek: John Burnet, Platonis Opera IV (Oxford, 1902), via Perseus canonical-greekLit; Burnet's text is a critical edition, so its wording can differ from the manuscript shown.",
                "English: R. G. Bury, Plato IX (Loeb Classical Library, 1929), via Perseus. Bury's footnotes are not reproduced. Quotation marks stand where Perseus marks quoted speech.",
                "Stephanus sections (a-e) are those of the 1578 Stephanus edition as given by Burnet and Bury; Bury's section breaks can fall a few words away from Burnet's because English word order differs.",
            ],
            "translation": translation,
            "verification": {
                "scan_source": f"Bibliothèque nationale de France, Gallica {GALLICA} (IIIF images via openapi.bnf.fr), fol. {f_rng}",
                "scan_license": "rightsstatements.org NoC-NC (no copyright, non-commercial use); credit: Source gallica.bnf.fr / BnF",
                "scan_manuscript": "Paris, BnF grec 1807 (Plato A), parchment, Constantinople, c. 850-875; Timaeus fol. 114r-144v, Critias fol. 145r-151r",
                "scan_mapping": ("Own visual check on the images: the opening words of every column of the dialogue were read on the BnF "
                                 "photographs and located in Burnet's text; each Stephanus section is linked to the folio side(s) whose "
                                 "columns contain it. Column openings are listed in each section's scan_note."),
                "scan_mapping_urls": [GALLICA, MANIFEST_URL, BNF_CATALOGUE],
                "scan_local_paths": [f"{key}/grec1807-f{f}.jpg" for f in page_folios],
                "original_text_source": f"John Burnet, Platonis Opera IV (Oxford, 1902), Perseus canonical-greekLit tlg0059.{work['tlg']}.perseus-grc2, https://github.com/PerseusDL/canonical-greekLit",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"R. G. Bury, Plato IX: Timaeus, Critias, Cleitophon, Menexenus, Epistles (Loeb Classical Library, 1929), Perseus tlg0059.{work['tlg']}.perseus-eng2",
                "translation_license": "public domain in the US (published 1929; term expired 1 January 2025); Perseus digital text CC BY-SA 4.0",
                "translator": "R. G. Bury (1929)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        themes = ["plato", name.lower(), "greek", "philosophy", "paris-a", "verified"]
        if is_atl:
            themes.insert(2, "atlantis")
        rows.append({
            "id": tid, "slug": tid, "order": order_n, "title": entry["title"], "author_id": "plato",
            "language": "Greek", "era": "Classical", "tradition": "greek", "category": "philosophy",
            "date_approx": "c. 360 BCE (composition); c. 850-875 AD (Paris gr. 1807)", "century": -4,
            "source": entry["source"], "description": entry["description"], "themes": themes,
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{key}/grec1807-f{f}.jpg", "caption": f"Paris gr. 1807 fol. {f}"} for f in page_folios]},
        })
    for f in PUB_DIR.glob(f"verified-{key}-*.json"):
        if f.stem not in {r["id"] for r in rows}:
            f.unlink()
    coll = {"collection": work["collection"], "texts": rows}
    (COLL_DIR / f"{key}.json").write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{key}: {len(rows)} entries, {n_sec} sections, {len(folios)} folio images")


ATLANTIS_NOTE = (
    "<p>Timaeus 20d-25d is Critias' first account of Atlantis: the story Solon was told by a priest at Sais in Egypt about an "
    "Athens of 9,000 years before, which defeated an invading power from the island of Atlantis beyond the Pillars of Heracles, "
    "after which the island sank into the sea. Plato returns to it at length in the <em>Critias</em>.</p>"
)

WORK["collection"] = {
    "key": "plato-timaeus",
    "prefix": "verified-plato-timaeus-",
    "label": "Plato, Timaeus (Paris gr. 1807)",
    "group": "Greece",
    "date_sort": -360,
    "author_name": "Plato (c. 360 BCE); Paris, BnF grec 1807, c. 850-875",
    "source_url": GALLICA,
    "critical_edition": "Burnet, Platonis Opera IV (1902), via Perseus",
    "translator_name": "R. G. Bury (Loeb, 1929)",
    "original_lang_label": "Greek · Burnet",
    "original_lang_code": "grc",
    "edition_label": "",
    "search_terms": "plato timaeus atlantis solon sais cosmology demiurge world soul receptacle paris a grec 1807",
    "description": ("The complete Timaeus, Plato's account of the making of the world, which opens with Critias' story of Atlantis "
                    "(20d-25d). Every Stephanus section is shown on the page of the oldest medieval manuscript that carries it, Paris gr. 1807 "
                    "(9th century), with Burnet's Greek and R. G. Bury's English."),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    build(WORK, args.force)


if __name__ == "__main__":
    main()
