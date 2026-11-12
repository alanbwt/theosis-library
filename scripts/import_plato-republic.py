#!/usr/bin/env python3
"""
import_plato-republic.py: Plato, Republic 6.506d-511e (the Sun and the Divided Line)
and 7.514a-521b (the Cave), each Stephanus subsection shown on the page of the
Florence manuscript Laur. Plut. 80.19 that carries it.

Chain of evidence
  1. MANUSCRIPT
     Florence, Biblioteca Medicea Laurenziana, Plut. 80.19, parchment, 247 leaves,
     180 x 245 mm, 12th century (BML catalogue: 1101-1200, 'datazione non espressa'):
     Republic (complete), Timaeus, speeches of Synesius. Images: BML Teca digitale
     (CONTENTdm) IIIF, https://cdm21059.contentdm.oclc.org/iiif/2/plutei:950763/manifest.json
     (cached in data/sources/plato-republic/iiif/laur8019-manifest.json); rights 'CC BY-NC-SA',
     access 'Pubblico'. Other candidates checked: Paris gr. 1807 (A, 9th c.) is on Gallica,
     which refuses automated requests; Vat. gr. 1 (DigiVatLib) holds the Laws, Epinomis and
     Letters but not the Republic (manifest ranges); Laur. Plut. 85.6 (12th c.) has only
     Republic books 1-2; Laur. Plut. 85.7 is 15th century; no online images of Marc. gr. 185
     (D) were found.
  2. MAPPING  The first and last lines of each page (fols. 72v-78v) were read on the image
     (crops of the 1800 px images) and matched to Burnet's Greek; the end of each page was
     checked against the start of the next. The words read are in PAGES and in each
     scan_note. A section is linked to every page whose first-to-last-line span contains
     part of its Greek. The marginal Stephanus page numbers written in the manuscript by a
     later hand (506, 507, 508, 509, 510, 515-521) agree with the readings.
  3. GREEK    John Burnet, Platonis Opera IV (Oxford 1902; public domain), Perseus
     canonical-greekLit tlg0059.tlg030.perseus-grc2 (CC BY-SA 4.0). Burnet places the
     Stephanus letters at the start of the printed line, often inside a sentence. Here each
     section starts with the first sentence or speech that begins at or after Burnet's
     letter (sentences split at '.', ';' and change of speaker), so a subsection in which
     no sentence begins is joined to the previous one (510d-e, 516c-d, 520a-b).
  4. ENGLISH  Paul Shorey, Plato: The Republic, vol. 2, books 6-10 (Loeb Classical Library,
     London: Heinemann; Cambridge, Mass.: Harvard University Press, 1935), Perseus
     tlg0059.tlg030.perseus-eng2 (CC BY-SA 4.0). Copyright: the US renewal lists for 1962
     and 1963 (Catalog of Copyright Entries, Project Gutenberg transcriptions, cached in
     data/sources/hyperborea/renewals/pg11825-pg11828.txt) have no entry for Shorey or for
     a Plato Republic, so the 1935 volume was not renewed and is in the US public domain
     (the Stanford renewal database could not be queried: it answers scripts with a bot check).
     Each English section starts at the words that translate the first Greek sentence of the
     section (ENG_CUTS, chosen by reading both texts sentence by sentence); where Shorey
     joins two Greek sentences into one, the cut falls inside his sentence (515d, 518d, 520d).
     Footnotes are dropped. The Perseus text was compared word by word with the OCR of the
     1935 printing (archive.org republicshorey02platuoft, cached in
     data/sources/plato-republic/shorey/); real differences are corrected in FIX_ENG.

Usage:
    python3 scripts/import_plato-republic.py [--force]
"""

import argparse
import html as htmlmod
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

KEY = "plato-republic"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0059/tlg030/tlg0059.tlg030.{ed}.xml"
MANIFEST_URL = "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:950763/manifest.json"

MS = {
    "short": "Laur. Plut. 80.19",
    "shelfmark": "Florence, Biblioteca Medicea Laurenziana, Plut. 80.19",
    "desc": ("Florence, Biblioteca Medicea Laurenziana, Plut. 80.19, parchment, 247 leaves, 180 x 245 mm, 12th century "
             "(BML catalogue: 1101-1200, no dated colophon). Contents: Plato, Republic (books 1-10) and Timaeus; "
             "speeches of Synesius of Cyrene. A later hand has written Stephanus page numbers in the margins."),
    "object": "https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/950763",
    "holder": "Biblioteca Medicea Laurenziana, Teca digitale (IIIF)",
    "license": ("Images Biblioteca Medicea Laurenziana, Florence (Teca digitale; rights statement 'CC BY-NC-SA', access 'Pubblico'). "
                "Reproduced with credit for non-commercial reference use; by concession of the Ministero della Cultura."),
    "width": 1800,
}

# ---------------------------------------------------------------------------
# Pages read on the images. 'anchor' = the words of Burnet's text at which the page's
# first line begins (located in the Greek to place the page break); 'first'/'last' =
# what was read on the first and last line of the page.
PAGES = [
    {"folio": "72v", "anchor": "ἔφη. ἀλλὰ σὺ δή, ὦ Σώκρατες",
     "first": "ἔφη· ἀλλὰ σὺ δή, ὦ Σώκρατες, πότερον ἐπιστήμην τὸ ἀγαθὸν φῂς εἶναι",
     "last": "ῥηθέντα καὶ ἄλλοτε ἤδη πολλάκις εἰρημένα. τὰ ποῖα; ἦ δ' ὅς",
     "extra": ("Fol. 72r ends with 506b '... ὁ τούτων ἐπιστήμων· ἀνάγκη'. On 72v, 506d begins in line 13 with 'μὴ πρὸς Διός, ἦ δ' ὅς, ὦ Σώκρατες', "
               "after '... παρ' ἄλλων ἀκούειν φανά τε καὶ καλά;'; the later marginal number 507 stands in the left margin in the lower half of the page.")},
    {"folio": "73r", "anchor": "πολλὰ καλά, ἦν δʼ ἐγώ, καὶ πολλὰ ἀγαθὰ",
     "first": "πολλὰ καλά, ἦν δ' ἐγώ, καὶ πολλὰ ἀγαθὰ καὶ ἕκαστα",
     "last": "δῆλον ὅτι ἐρωτᾷς. ἆρ' οὖν ὧδε πέφυκεν ὄψις πρὸς τοῦτον"},
    {"folio": "73v", "anchor": "τὸν θεόν; ¶ πῶς;",
     "first": "τὸν θεόν; πῶς; οὐκ ἔστιν ἥλιος ἡ ὄψις, οὔτε αὐτή, οὔτε ἐν ᾧ",
     "last": "τὸ γιγνώσκεσθαι φάναι ὑπὸ τοῦ ἀγαθοῦ παρεῖναι, ἀλλὰ καὶ τὸ εἶναί τε",
     "extra": ("In 509a the scribe skipped from 'ἐπιστήμην' to the next 'ἐπιστήμην'; the omitted words, 'ἐπιστήμην δὲ καὶ ἀλήθειαν, ὥσπερ ἐκεῖ φῶς τε καὶ ὄψιν' "
               "to '... τιμητέον τὴν τοῦ ἀγαθοῦ ἕξιν. ἀμήχανον κάλλος ἔφη λέγεις', are written in the left margin and across the foot of the page, "
               "beside the later marginal number 509.")},
    {"folio": "74r", "anchor": "καὶ τὴν οὐσίαν ὑπʼ ἐκείνου",
     "first": "καὶ τὴν οὐσίαν ὑπ' ἐκείνου αὐτοῖς προσεῖναι, οὐκ οὐσίας ὄντος",
     "last": "ταῦτ', ἔφη, ἃ λέγεις, οὐχ ἱκανῶς ἔμαθον. ἀλλ' αὖθις, ἦν δ' ἐγώ",
     "extra": ("Below the last line the scribe drew the divided line as a table: 'ὁρατόν' (visible) and 'νοητόν' (intelligible) over the four parts "
               "'εἰκασία', 'πίστις', 'διάνοια' and 'νόησις'. The later marginal number 510 stands beside the middle of the page.")},
    {"folio": "74v", "anchor": "ῥᾷον γὰρ τούτων προειρημένων",
     "first": "ῥᾷον γὰρ τούτων προειρημένων μαθήσῃ. οἶμαι γάρ σε εἰδέναι ὅτι",
     "last": "καὶ τελευτᾷ εἰς εἴδη. μανθάνω, ἔφη, ἱκανῶς μὲν οὔ· δοκεῖς γάρ μοι"},
    {"folio": "75r", "anchor": "συχνὸν ἔργον λέγειν",
     "first": "συχνὸν ἔργον λέγειν· ὅτι μέντοι βούλει διορίζειν σαφέστερον εἶναι",
     "last": "ὁρῶ, ἔφη. ὅρα τοίνυν παρὰ τοῦτο τὸ τειχίον φέ-",
     "extra": ("Book 6 ends in the middle of the page with 'μανθάνω, ἔφη, καὶ ξυγχωρῶ καὶ τάττω ὡς λέγεις'; below it stands the title "
               "'(Π)λάτωνος πολιτείας ἑβδόμη' and book 7 (514a) begins '(Μ)ετὰ ταῦτα δή, εἶπον, ἀπείκασον τοιούτῳ πάθει τὴν ἡμετέραν φύσιν', "
               "the initials left blank for a rubricator.")},
    {"folio": "75v", "anchor": "ἀνθρώπους σκεύη τε παντοδαπὰ",
     "first": "(φέ)ροντας ἀνθρώπους σκεύη τε παντοδαπὰ ὑπερέχοντα τοῦ τειχίου",
     "last": "καὶ νομίζειν ταῦτα τῷ ὄντι σαφέστερα τῶν δεικνυμένων; οὕτως, ἔφη· εἰ δ'",
     "extra": "The later marginal number 515 stands near the top of the page."},
    {"folio": "76r", "anchor": "ἦν δʼ ἐγώ, ἐντεῦθεν ἕλκοι",
     "first": "ἦν δ' ἐγώ, ἐντεῦθεν ἕλκοι τις αὐτὸν βίᾳ διὰ τραχείας τῆς ἀνα(βάσεως)",
     "last": "ἀνδρὶ παρ' ἀκλήρῳ, καὶ ὁτιοῦν ἂν πεπονθέναι μᾶλλον ἢ",
     "extra": "The marginal number 516 stands near the top of the page."},
    {"folio": "76v", "anchor": "κεῖνά τε δοξάζειν",
     "first": "ἐκεῖνά τε δοξάζειν καὶ ἐκείνως ζῆν. οὕτως, ἔφη, ἔγωγε οἶμαι πᾶν μᾶλλον",
     "last": "προειρημένην εἰκόνα τοῦτ' ἔχει. εἰκὸς μέντοι, ἔφη. τί δέ; τόδε",
     "extra": "The marginal number 517 stands beside the upper third of the page."},
    {"folio": "77r", "anchor": "οἴει τι θαυμαστόν, εἰ ἀπὸ θείων",
     "first": "οἴει τι θαυμαστόν, εἰ ἀπὸ θείων, ἦν δ' ἐγώ, θεωριῶν ἐπὶ τὰ ἀνθρώ(πεια)",
     "last": "ὂν καὶ τοῦ ὄντος τὸ φανότατον, δυνατὴ γένηται ἀνασχέ-",
     "extra": "The marginal number 518 stands beside the middle of the page."},
    {"folio": "77v", "anchor": "θεωμένη· τοῦτο δʼ εἶναί φαμεν",
     "first": "(ἀνασχέ)σθαι θεωμένη. τοῦτο δ' εἶναί φαμεν τἀγαθόν. ἦ γάρ; ναί. τούτου τοίνυν",
     "last": "οὐκ ἔχουσιν ἕνα, οὗ στοχαζομένους δεῖ ἅπαντα πράττειν",
     "extra": ("In 519b-c, after '... ἱκανῶς ἄν ποτε πόλιν ἐπιτροπεῦσαι', the scribe left a line and a half blank, filled with a drawn stroke, "
               "with a mark in the left margin; the text goes on 'μήτε τοὺς ἐν παιδείᾳ ἐωμένους διατρίβειν διὰ τέλους' without missing words. "
               "The marginal number 519 stands beside the upper part of the page.")},
    {"folio": "78r", "anchor": "ἃ ἂν πράττωσιν ἰδίᾳ",
     "first": "ἃ ἂν πράττωσιν ἰδίᾳ τε καὶ δημοσίᾳ, τοὺς δὲ ὅτι ἑκόντες εἶναι οὐ πρά(ξουσιν)",
     "last": "εἰς τὴν τῶν ἄλλων ξυνοίκησιν καὶ συνεθιστέον τὰ σκοτεινὰ θεά-",
     "extra": "The marginal number 520 stands beside the lower half of the page."},
    {"folio": "78v", "anchor": "συνεθιζόμενοι γὰρ μυρίῳ",
     "first": "(θεά)σασθαι· ξυνεθιζόμενοι γὰρ μυρίῳ βέλτιον ὄψεσθε τῶν ἐκεῖ",
     "last": None,
     "extra": ("The marginal number 521 stands beside the middle of the page. 521b ends in the lower half of the page at the end of a line, "
               "'... καὶ βίον ἀμείνω τοῦ πολιτικοῦ; οὐδένας ἄλλους, ἔφη', and the next line begins 521c, 'βούλει οὖν'.")},
]

# English: the words of Shorey's translation at which each section begins (in order).
ENG_CUTS = {
    "506d": "“Nay, in heaven’s name, Socrates,”",
    "506e": "“Well, speak on,” he said",
    "507a": "“I could wish,”",
    "507b": "“What?” said he.",
    "507c": "“With which of the parts of ourselves",
    "507d": "“They need nothing,” he said.",
    "507e": "“What is this thing of which you speak?”",
    "508a": "“It surely is far from being so,”",
    "508b": "“Why, no.”",
    "508c": "“How is that?” he said;",
    "508d": "“But when, I take it,",
    "508e": "“This reality, then, that gives their truth",
    "509a": "“An inconceivable beauty you speak of,”",
    "509b": "“How?”",
    "509c": "And Glaucon very ludicrously said",
    "509d-e": "“Conceive then,” said I,",
    "510a": "“I do.” “As the second section",
    "510b": "“I certainly would.”",
    "510c": "“Well, I will try again,”",
    "510d-e": "“Certainly,” he said, “I know that.”",
    "511a": "“True,” he said. ",
    "511b": "“I understand,” said he,",
    "511c": "“I understand,” he said; “not fully",
    "511d": "And I think you call the mental habit",
    "511e": "“I understand,” he said; “I concur",
    "514a": "“Next,” said I,",
    "514b-c": "“All that I see,” he said.",
    "515a": "“A strange image you speak of,”",
    "515b": "“And again, would not the same be true",
    "515c": "“Then in every way",
    "515d": "do you not think that he would be at a loss",
    "515e": "“And if he were compelled to look at the light itself,",
    "516a": "“Why, no, not immediately,”",
    "516b": "“Of course.”",
    "516c-d": "“Obviously,” he said,",
    "516e": "“Yes,” he said, “I think that he would choose",
    "517a": "And if it were possible to lay hands on",
    "517b": "But God knows whether it is true.",
    "517c": "“I concur,” he said, “so far as I am able.”",
    "517d": "“Yes, it is likely.”",
    "517e": "“It would be by no means strange,”",
    "518a": "“But a sensible man,”",
    "518b": "“That is a very fair statement,”",
    "518c": "“They do indeed,” he said.",
    "518d-e": "do we not?”",
    "519a": "Have you never observed",
    "519b": "“It is likely,” he said.",
    "519c": "“True,” he said. “It is the duty",
    "519d": "“What is that?”",
    "519e": "“You have again forgotten, my friend,”",
    "520a-b": "“True,” he said, “I did forget it.”",
    "520c": "Down you must go then,",
    "520d": "when the truth is that the city",
    "520e": "“Impossible,” he said",
    "521a": "But if, being beggars and starvelings",
    "521b": "“Can you name any other type or ideal of life",
}
ENG_END = {"511e": "I concur and arrange them as you bid.”", "521b": "“No others,” he said."}

# Differences between the Perseus English and the 1935 printing (checked on the OCR of
# archive.org republicshorey02platuoft and its page images), plus one Perseus markup slip.
FIX_ENG = [
    ("said I,” do many others", "said I, “do many others"),                 # Perseus markup slip
    ("“It would be by no men strange,”", "“It would be by no means strange,”"),
    ("image holds” “Yes, it is likely.”", "image holds.” “Yes, it is likely.”"),
    ("We predicate to be of many", "We predicate ‘to be’ of many"),
    ("that which each really is. “It is so.”", "that which each really is.” “It is so.”"),
    ("seeing and being seen? “Why, no,", "seeing and being seen?” “Why, no,"),
    ("“Yes, it does,” “This reality", "“Yes, it does.” “This reality"),
    # Perseus uses American spelling; the 1935 printing has British forms:
    ("wings my flight today", "wings my flight to-day"),
    ("though color be present", "though colour be present"),
    ("the colors will remain invisible", "the colours will remain invisible"),
    ("if light is not without honor", "if light is not without honour"),
    ("upon whose colors the light", "upon whose colours the light"),
    ("Still higher honor belongs", "Still higher honour belongs"),
    ("held in honor", "held in honour"),
    ("honors and commendations", "honours and commendations"),
    ("who were honored by these", "who were honoured by these"),
    ("in courtrooms", "in court-rooms"),
    ("periact in the theater", "periact in the theatre"),
    ("their labors and honors", "their labours and honours"),
    ("in the labors there", "in the labours there"),
    ("in the labors of state", "in the labours of state"),
]

ENTRIES = [
    {
        "slug": "sun-and-divided-line", "order": 1, "first": "506d", "last": "511e", "book": 6,
        "title": "Plato, Republic 6.506d-511e: the Sun and the Divided Line",
        "description": ("Socrates' images of the Good: the sun, offspring of the Good, gives the visible world light and growth as the Good gives "
                        "the intelligible world truth and being, itself 'beyond being'; then the line divided into four parts, from images to "
                        "intelligence. Shown on the 12th-century Florence manuscript Laur. Plut. 80.19."),
        "themes": ["plato", "republic", "idea-of-the-good", "sun", "divided-line", "forms", "knowledge", "dialectic", "theosis", "philosophy", "greek"],
        "intro": (
            "<p>In book 6 of the <em>Republic</em> Socrates has argued that the rulers of the just city must know the Good, the greatest thing to be learned. "
            "Asked what the Good is, he declines to say directly and offers instead its 'offspring' (506e). As the sun gives visible things both their visibility "
            "and their coming into being and growth, so the Good gives the objects of knowledge their truth and their very being, though the Good 'is not essence but still "
            "transcends essence in dignity and surpassing power' (509b, in Shorey's words). Glaucon's laughing reply follows. Socrates then asks him to "
            "imagine a line divided into two unequal parts, the visible and the intelligible, each divided again in the same ratio: images and shadows; "
            "the things of which they are images; the objects the mind reaches through assumptions, as in geometry; and the forms reached by dialectic, "
            "which rises to 'the starting-point of all' (509d-511c). The four parts answer to four states of the soul: picture-thinking, belief, understanding "
            "and reason (511d-e). The Cave in book 7 applies these images.</p>\n\n"
            "<p>The pages shown are from Florence, Biblioteca Medicea Laurenziana, Plut. 80.19, a parchment manuscript of the Republic and the Timaeus "
            "of the 12th century (library dating). The passage fills fols. 72v-75r. On fol. 73v the scribe left out part of 509a and added it in the margin; "
            "on fol. 74r he drew the divided line as a table with its four parts named. Each section below is a Stephanus subsection, linked to the page or pages "
            "that carry its words; the pages were identified by reading the first and last lines of each page on the image. "
            "The Greek is Burnet's critical text (1902), not a transcription of this manuscript, so spelling and some words differ in places. "
            "The English is Paul Shorey's Loeb translation (1935). A subsection in which no new sentence begins is joined to the one before it (510d-e).</p>"
        ),
    },
    {
        "slug": "allegory-of-the-cave", "order": 2, "first": "514a", "last": "521b", "book": 7,
        "title": "Plato, Republic 7.514a-521b: the Allegory of the Cave",
        "description": ("The opening of Republic book 7: prisoners chained in a cave see only shadows; one is freed, turned round and dragged up into the "
                        "sunlight, sees the sun itself, and must go back down. Education as the turning of the soul, and the duty of the philosopher "
                        "to return. Shown on the 12th-century Florence manuscript Laur. Plut. 80.19."),
        "themes": ["plato", "republic", "allegory-of-the-cave", "idea-of-the-good", "education", "ascent-of-the-soul", "conversion", "theosis", "philosophy", "greek"],
        "intro": (
            "<p>Book 7 of the <em>Republic</em> opens with the image of the Cave. Men are chained from childhood in an underground cave, facing the wall, "
            "and see only the shadows of objects carried past a fire behind them; they take the shadows for reality (514a-515c). One prisoner is released, "
            "turned round and dragged up the steep ascent into the sunlight; he sees first shadows and reflections, then the things themselves, the heavens by night, "
            "and at last the sun itself, and understands that it governs everything in the visible world (515c-516c). If he went back down, his eyes full of darkness, "
            "the prisoners would laugh at him and would kill the man who tried to free them (516e-517a). Socrates then explains the image: the cave is the visible world, "
            "the ascent is the soul's ascent to the intelligible, and the last thing seen is the idea of the Good, 'the cause for all things of all that is right and beautiful' "
            "(517b-c, Shorey). Education is not putting sight into blind eyes but turning the whole soul round from becoming to being (518b-d). The philosophers "
            "who have seen the Good must be compelled to go back down into the cave and rule (519c-521b).</p>\n\n"
            "<p>The pages shown are from Florence, Biblioteca Medicea Laurenziana, Plut. 80.19, a parchment manuscript of the Republic and the Timaeus "
            "of the 12th century (library dating). The passage fills fols. 75r-78v; book 7 begins in the middle of fol. 75r below its title. "
            "Each section below is a Stephanus subsection, linked to the page or pages that carry its words; the pages were identified by reading the first and "
            "last lines of each page on the image. The Greek is Burnet's critical text (1902), not a transcription of this manuscript. The English is Paul Shorey's "
            "Loeb translation (1935). Stephanus page 514 has only subsections a and b, because book 7 begins there; subsections in which no new sentence begins "
            "are joined to the one before (516c-d, 520a-b). Where Shorey joins two Greek sentences into one, the English section starts inside his sentence (515d, 518d, 520d).</p>"
        ),
    },
]


# ---------------------------------------------------------------------------
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def cached(name, url):
    p = SRC / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url))
    return p


def canvases():
    m = json.loads(cached("iiif/laur8019-manifest.json", MANIFEST_URL).read_text(encoding="utf-8"))
    out = {}
    for c in m["sequences"][0]["canvases"]:
        lab = c["label"].replace("Carta: ", "")
        sid = c["images"][0]["resource"]["service"]["@id"]
        out.setdefault(lab, {"service": sid, "id": sid.rsplit(":", 1)[1]})
    return out


def get_scan(folio, cv, force):
    path = SCAN_DIR / f"laur8019-f{folio}.jpg"
    if force or not path.exists():
        img = Image.open(io.BytesIO(fetch(f"{cv[folio]['service']}/full/{MS['width']},/0/default.jpg"))).convert("RGB")
        img.save(path, quality=85)
    return path


def viewer(folio, cv):
    return f"https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/{cv[folio]['id']}"


# ---------------------------------------------------------------------------
def stream(path, eng=False):
    """Body text with Stephanus markers '[506d]' and speech breaks '¶'. Notes dropped;
    in the English, <q type="spoken"> is printed with curly quotes as in the Loeb."""
    body = ET.parse(path).getroot().find(f".//{TEI}body")
    out = []

    def walk(e):
        tag = e.tag.split("}")[-1]
        if tag in ("note", "head", "bibl"):
            if e.tail:
                out.append(e.tail)
            return
        if tag == "milestone":
            if e.get("unit") == "section":
                out.append(f" [{e.get('n')}] ")
            elif e.get("unit") == "para":
                out.append(" ¶ ")
        q = eng and tag == "q" and e.get("type") == "spoken"
        if q:
            out.append("“")
        if e.text and tag != "milestone":
            out.append(e.text)
        for c in e:
            walk(c)
        if q:
            out.append("”")
        if e.tail:
            out.append(e.tail)

    walk(body)
    return re.sub(r"\s+", " ", "".join(out))


def greek_units(s, first, last):
    """[(stephanus letter at the unit's start, unit text)] from the start of `first` to the end of `last`."""
    a = s.index(f"[{first}]")
    nxt = re.search(r"\[(\d{3}[a-e])\]", s[s.index(f"[{last}]") + 6:])
    b = s.index(f"[{last}]") + 6 + nxt.start()
    toks = re.split(r"(\[\d{3}[a-e]\]|¶)", s[:b + 5000])
    units, cur, buf, bsec = [], None, "", None
    for t in toks:
        if re.fullmatch(r"\[\d{3}[a-e]\]", t):
            cur = t[1:-1]
            continue
        if t == "¶":
            if buf.strip():
                units.append((bsec, buf.strip(), True))
            buf, bsec = "", None
            continue
        parts = re.split(r"(?<=[.;;])\s+", t)
        for i, p in enumerate(parts):
            if not p.strip():
                continue
            if bsec is None:
                bsec = cur
            buf += (" " if buf else "") + p.strip()
            if i < len(parts) - 1 or re.search(r"[.;;]\s*$", p):
                units.append((bsec, buf.strip(), False))
                buf, bsec = "", None
    # keep the units that begin between `first` and `last` (inclusive)
    return [u for u in units if u[0] and first <= u[0] <= last]


def group_sections(units, milestones):
    """Group units by the letter in which they begin; letters with no unit are joined to the
    previous section, whose id becomes e.g. '510d-e' (letters as printed by Burnet)."""
    order, groups = [], {}
    for sec, text, _ in units:
        if not order or order[-1] != sec:
            order.append(sec)
        groups.setdefault(sec, []).append(text)
    out = []
    for i, sec in enumerate(order):
        j = milestones.index(sec)
        k = milestones.index(order[i + 1]) if i + 1 < len(order) else j + 1
        if i + 1 == len(order):   # last section: run to the end of the page or the passage
            k = j + 1
        last = milestones[k - 1]
        sid = sec if last == sec else (f"{sec}-{last[3]}" if last[:3] == sec[:3] else f"{sec}-{last}")
        out.append((sid, sec, groups[sec]))
    return out


def english_sections(e, sids, end_phrase):
    """Cut the English stream at ENG_CUTS[sid] (searched in order)."""
    e = e.replace("¶", " ")
    e = re.sub(r"\[\d{3}[a-e]?\]", " ", e)
    e = re.sub(r"\s+", " ", e)
    e = re.sub(r"“\s+", "“", e)
    e = re.sub(r"\s+”", "”", e)
    for a, b in FIX_ENG:
        assert a in e, a
        e = e.replace(a, b)
    pos = []
    p = e.index(ENG_CUTS[sids[0]])
    for sid in sids:
        q = e.index(ENG_CUTS[sid], p)
        pos.append(q)
        p = q + 1
    end = e.index(end_phrase, pos[-1]) + len(end_phrase)
    pos.append(end)
    return {sid: e[pos[i]:pos[i + 1]].strip() for i, sid in enumerate(sids)}


def to_html(s):
    return htmlmod.escape(s, quote=False)


def page_note(p, cv):
    s = f"{MS['short']} fol. {p['folio']} begins '{p['first']}' on its first line"
    s += f" and ends '{p['last']}' on its last line." if p.get("last") else "."
    if p.get("extra"):
        s += " " + p["extra"]
    return s + " Viewer: " + viewer(p["folio"], cv)


def build(E, grc, eng, cv, files):
    units = greek_units(grc, E["first"], E["last"])
    secs = group_sections(units, re.findall(r"\[(\d{3}[a-e])\]", grc))
    sids = [sid for sid, _, _ in secs]
    for sid in sids:
        assert sid in ENG_CUTS, sid
    en = english_sections(eng, sids, ENG_END[E["last"]])
    # Greek offsets: the stream without the Stephanus markers, with the markers' positions kept,
    # to place the page breaks (anchors) and the sections in one coordinate system.
    flat, ms_pos = "", {}
    for part in re.split(r"(\[\d{3}[a-e]\])", grc):
        if re.fullmatch(r"\[\d{3}[a-e]\]", part):
            ms_pos[part[1:-1]] = len(flat)
            continue
        part = re.sub(r"\s+", " ", part).strip()
        if part:
            flat += (" " if flat else "") + part
    origin = ms_pos["506a"]
    starts = []
    for p in PAGES:
        i = flat.find(p["anchor"], origin)
        assert i >= 0, p["anchor"]
        starts.append(i)
    assert starts == sorted(starts)
    sections = []
    for sid, sec, texts in secs:
        g = " ".join(texts)
        a = flat.find(texts[0][:40], ms_pos[sec] - 1)
        assert a >= 0, sid
        z = flat.find(texts[-1][-30:], a) + 30
        pages = []
        for k, p in enumerate(PAGES):
            ps = starts[k]
            pe = starts[k + 1] if k + 1 < len(PAGES) else len(flat)
            if a < pe and z > ps:
                pages.append(p)
        assert pages, sid
        if len(pages) == 1:
            note = f"On {MS['short']} fol. {pages[0]['folio']}. " + page_note(pages[0], cv)
        else:
            note = (f"Starts on fol. {pages[0]['folio']} and continues on fol. {pages[-1]['folio']} (page break inside this section). "
                    + " ".join(page_note(p, cv) for p in pages))
        note += " Checked on the images. The Greek shown is Burnet's edition, not a transcription of this manuscript."
        sections.append({
            "section": sid,
            "original_ref": f"Plato, Republic {E['book']}.{sid} (Burnet); {MS['short']} fol. " + ", ".join(p["folio"] for p in pages),
            "original_text": "<p>" + to_html(g) + "</p>",
            "text": "<p>" + to_html(en[sid]) + "</p>",
            "scan_pages": [f"{KEY}/{files[p['folio']].name}" for p in pages],
            "scan_note": note,
        })
    folios = []
    for s in sections:
        for sp in s["scan_pages"]:
            f = sp.split("-f")[-1].replace(".jpg", "")
            if f not in folios:
                folios.append(f)
    tid = PREFIX + E["slug"]
    entry = {
        "id": tid, "slug": tid, "title": E["title"],
        "language": "Greek (Burnet 1902) / English (Paul Shorey, 1935)",
        "source": f"{MS['shelfmark']} fol. {folios[0]}-{folios[-1]} ({MS['holder']}) + Burnet's Greek (Perseus) + Paul Shorey's English (Loeb, 1935, Perseus)",
        "description": E["description"],
        "introduction": E["intro"],
        "translator_notes": [
            "Greek: John Burnet, Platonis Opera IV (Oxford 1902), Republic, digital text Perseus tlg0059.tlg030.perseus-grc2. Apparatus not shown.",
            "English: Paul Shorey, Plato, The Republic, vol. 2 (Loeb Classical Library, 1935), digital text Perseus tlg0059.tlg030.perseus-eng2, checked against the 1935 printing. Shorey's footnotes are not shown.",
            "Each section starts at the first sentence or speech that begins at or after Burnet's Stephanus letter; the English starts at the words that translate that sentence.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"{MS['holder']}: {MS['object']} (folios {', '.join(folios)}); IIIF manifest {MANIFEST_URL}",
            "scan_license": MS["license"],
            "scan_manuscript": MS["desc"],
            "scan_mapping": "First and last lines of every page read on the image and matched to Burnet's Greek (words recorded in each scan_note); end of each page checked against the start of the next.",
            "scan_mapping_urls": [MS["object"]] + [viewer(f, cv) for f in folios],
            "scan_local_paths": [f"{KEY}/laur8019-f{f}.jpg" for f in folios],
            "original_text_source": "J. Burnet, Platonis Opera IV (Oxford 1902), Perseus canonical-greekLit tlg0059.tlg030.perseus-grc2 (https://github.com/PerseusDL/canonical-greekLit/tree/master/data/tlg0059/tlg030)",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": "Paul Shorey, Plato: The Republic, vol. 2 (Loeb Classical Library; London: Heinemann, Cambridge, Mass.: Harvard University Press, 1935), Perseus tlg0059.tlg030.perseus-eng2, checked against archive.org republicshorey02platuoft",
            "translation_license": ("public domain in the US: published 1935, copyright not renewed (no Shorey or Plato Republic entry in the 1962-1963 renewal lists of the "
                                    "Catalog of Copyright Entries, data/sources/hyperborea/renewals/pg11825-pg11828.txt); Perseus digital text CC BY-SA 4.0"),
            "translator": "Paul Shorey (1935)",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": E["order"], "title": E["title"], "author_id": "plato",
        "language": "Greek", "era": "Classical", "tradition": "greek", "category": "philosophy",
        "date_approx": "c. 375 BCE (composition); manuscript 12th century", "century": -4,
        "source": entry["source"], "description": E["description"], "themes": E["themes"] + ["verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/laur8019-f{f}.jpg", "caption": f"{MS['short']} fol. {f}"} for f in folios]},
    }
    print(f"wrote {tid} ({len(sections)} sections, folios {folios[0]}-{folios[-1]})")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cv = canvases()
    grc = stream(cached("tlg0059.tlg030.perseus-grc2.xml", PERSEUS.format(ed="perseus-grc2")))
    eng = stream(cached("tlg0059.tlg030.perseus-eng2.xml", PERSEUS.format(ed="perseus-eng2")), eng=True)
    files = {p["folio"]: get_scan(p["folio"], cv, args.force) for p in PAGES}
    rows = [build(E, grc, eng, cv, files) for E in ENTRIES]
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Plato, Republic: the Sun, the Line and the Cave",
            "group": "Greece", "date_sort": -375,
            "author_name": "Plato (c. 428-348 BCE); Florence manuscript Laur. Plut. 80.19 (12th century)",
            "source_url": MS["object"],
            "critical_edition": "Burnet, Platonis Opera IV (1902), via Perseus",
            "translator_name": "Paul Shorey (Loeb, 1935)",
            "original_lang_label": "Greek · Burnet",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "plato republic politeia sun divided line cave allegory idea of the good form beyond being dialectic education shorey laurenziana",
            "description": ("The central images of Plato's Republic, the Sun, the Divided Line and the Cave, each Stephanus subsection shown on the page of the "
                            "12th-century Florence manuscript Laur. Plut. 80.19 that carries it, with Burnet's Greek and Paul Shorey's English."),
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
