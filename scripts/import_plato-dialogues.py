#!/usr/bin/env python3
"""
import_plato-dialogues.py: Plato on the divine in man and "becoming like god",
key passages on the oldest manuscripts with page images.

One entry per passage; one section per Stephanus subsection (e.g. 176b), each
linked to the manuscript page(s) that carry its words.

Chain of evidence
  1. MANUSCRIPTS
     Oxford, Bodleian Library, MS. E. D. Clarke 39 (Plato 'B'), copied in 895 by
     John the Calligrapher for Arethas of Patrae. Digital Bodleian IIIF manifest
     https://iiif.bodleian.ox.ac.uk/iiif/manifest/f57d074b-cff1-4172-8236-797c7b8f0403.json
     (CC BY-NC 4.0). Folio ranges per dialogue from Pinakes (diktyon 47776):
     Phaedo 26-58, Theaetetus 83-113, Symposium 198v-224, Phaedrus 224-248v.
     Paris, BnF, grec 1807 (Plato 'A', 9th c.) for the Laws, via Gallica IIIF
     (non-commercial reuse with credit).
  2. MAPPING  For every manuscript page used, the first and last lines were read
     on the image (crops at full IIIF resolution) and matched to Burnet's text;
     the opening and closing words are stored in PAGES below and printed in each
     section's scan_note. A Stephanus subsection is assigned to every page whose
     span (first line to last line) contains part of it; a subsection cut by a
     page break lists both pages. No page was placed by counting or by text length.
  3. GREEK    John Burnet, Platonis Opera (Oxford, 1900-1907), via Perseus
     canonical-greekLit tlg0059.*.perseus-grc2 (CC BY-SA 4.0). Burnet's deletion
     brackets <del> are shown as [ ], additions <add> as < >. Perseus repeats the
     speaker label at some paragraph breaks inside one speech; a label is shown
     only when the speaker changes.
  4. ENGLISH  Perseus canonical-greekLit tlg0059.*.perseus-eng2 (CC BY-SA 4.0 digital
     text) of Loeb translations published before 1929 and so public domain in
     the US: H. N. Fowler (Phaedo, Phaedrus 1914; Theaetetus 1921),
     W. R. M. Lamb (Symposium 1925), R. G. Bury (Laws 1926). Each translation
     carries its own Stephanus milestones, which set the English section breaks.

Usage:
    python3 scripts/import_plato-dialogues.py           # build
    python3 scripts/import_plato-dialogues.py --force   # re-download scans
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

KEY = "plato-dialogues"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
PERSEUS_GH = "https://github.com/PerseusDL/canonical-greekLit/tree/master/data/tlg0059"

MSS = {
    "clarke39": {
        "manifest": SRC / "iiif" / "clarke39-manifest.json",
        "shelfmark": "Oxford, Bodleian Library, MS. E. D. Clarke 39",
        "short": "Clarke 39",
        "siglum": "B",
        "date": "895",
        "desc": "Oxford, Bodleian Library, MS. E. D. Clarke 39 (Plato 'B'), parchment, copied in Constantinople in 895 by John the Calligrapher for Arethas of Patrae; brought from the monastery of St John on Patmos by E. D. Clarke in 1801",
        "object": "https://digital.bodleian.ox.ac.uk/objects/f57d074b-cff1-4172-8236-797c7b8f0403/",
        "viewer": "https://digital.bodleian.ox.ac.uk/objects/f57d074b-cff1-4172-8236-797c7b8f0403/surfaces/{uuid}/",
        "holder": "Bodleian Libraries, University of Oxford, Digital Bodleian (IIIF)",
        "license": "Photo: (c) Bodleian Libraries, University of Oxford. Terms of use: CC BY-NC 4.0 (https://digital.bodleian.ox.ac.uk/terms/)",
        "lines": 34,
        "width": 1800,
        "mapping_ref": ("folio range of the dialogue from Pinakes diktyon 47776", "https://pinakes.irht.cnrs.fr/notices/cote/47776/"),
    },
    "grec1807": {
        "manifest": SRC / "iiif" / "grec1807-manifest.json",
        "shelfmark": "Paris, Bibliotheque nationale de France, grec 1807",
        "short": "Paris gr. 1807",
        "siglum": "A",
        "date": "9th c. (second half)",
        "desc": "Paris, Bibliotheque nationale de France, grec 1807 (Plato 'A'), parchment, second half of the 9th century, written in two columns of 44 lines by the first scribe of the so-called 'philosophical collection'; tetralogies VIII-IX (Clitophon, Republic, Timaeus, Critias, Minos, Laws, Epinomis, Letters, Definitions, spuria)",
        "object": "https://gallica.bnf.fr/ark:/12148/btv1b8419248n",
        "viewer": "https://gallica.bnf.fr/ark:/12148/btv1b8419248n/{uuid}.item",
        "holder": "Bibliotheque nationale de France, Gallica (IIIF)",
        "license": "Source gallica.bnf.fr / BnF. Non-commercial reuse is free with credit under the Gallica terms of use (https://gallica.bnf.fr/edit/und/conditions-dutilisation-des-contenus-de-gallica)",
        "lines": 44,
        "width": 1700,
        "mapping_ref": ("folio range of each book from the BnF catalogue description in the Gallica IIIF manifest (archivesetmanuscrits.bnf.fr ark:/12148/cc19975p)", "http://archivesetmanuscrits.bnf.fr/ark:/12148/cc19975p"),
    },
}

# ---------------------------------------------------------------------------
# Page data, read on the images. start/end = Stephanus subsection in which the
# page's first / last line falls; first/last = the words read on those lines.
# ---------------------------------------------------------------------------
PASSAGES = [
    {
        "slug": "theaetetus-172c-177c",
        "order": 1,
        "tlg": "tlg006",
        "work": "Theaetetus",
        "range": ("172c", "177c"),
        "ms": "clarke39",
        "title": "Plato, Theaetetus 172c-177c: the philosopher and the flight to become like god",
        "translator": "H. N. Fowler (1921)",
        "translation_source": "Harold North Fowler, Plato VII: Theaetetus, Sophist (Loeb Classical Library, Harvard University Press / Heinemann, 1921), Perseus tlg0059.tlg006.perseus-eng2",
        "date_approx": "c. 369 BCE (composition); manuscript 895 AD",
        "description": "The digression of the Theaetetus, where Socrates says that we should flee from here to there, and that the flight is becoming like god as far as possible (176a-b), shown on the pages of the Clarke Plato (895 AD) that carry it.",
        "themes": ["plato", "theaetetus", "homoiosis-theoi", "becoming-like-god", "theosis", "philosophy", "greek", "verified"],
        "intro": (
            "<p>In the middle of the <em>Theaetetus</em>, while examining Protagoras' claim that man is the measure of all things, "
            "Socrates breaks off to compare two kinds of people: the man trained in the law courts, quick and servile, and the philosopher, "
            "who does not know the way to the market place but whose mind ranges over the earth and the heavens. "
            "The digression ends with the sentence that later Platonists, Philo and the Greek Church Fathers took as a definition of the human goal: "
            "\"we ought to try to escape from earth to the dwelling of the gods as quickly as we can; and to escape is to become like God, so far as this is possible\" "
            "(<em>phyge de homoiosis theoi kata to dynaton</em>, 176a-b). Becoming like god is defined as becoming just and holy with wisdom.</p>\n\n"
            "<p>The pages shown are from the Clarke Plato (Oxford, Bodleian Library, MS. E. D. Clarke 39), copied in Constantinople in 895 for Arethas of Patrae. "
            "It is the oldest surviving manuscript of this dialogue, cited by editors as B. The passage runs from fol. 96v line 20 to fol. 99r, six pages of 34 lines. "
            "Each section below is one Stephanus subsection; the page or pages listed for it were identified by reading the first and last lines of each page on the image. "
            "The Greek shown is Burnet's critical text, so the copyist's spelling and some words differ from it in places (for example, at 173e the manuscript has "
            "<em>pheretai</em> where Burnet prints <em>petetai</em>, and at 176a it has the word <em>alethe</em> that Burnet brackets).</p>"
        ),
        "pages": [
            {"folio": "96v", "start": "171e", "end": "172e",
             "first": "βοηθοῦντες Πρωταγόρᾳ, ὡς τὰ μὲν πολλὰ ᾗ δοκεῖ ταύτῃ καὶ ἔστιν",
             "last": "ὁ ἀντίδικος ἐφέστηκεν καὶ ὑπογραφὴν παραναγιγνωσκομένην",
             "extra": "172c begins on line 20 ('λάττονος καταλαμβάνει· οὐκοῦν σχολὴν ἄγομεν, ὦ Σώκρατες'); 172d begins at the end of line 25 ('τοιᾷδε', with 'διατριβῇ τεθραμμένους' on line 26)."},
            {"folio": "97r", "start": "172e", "end": "173e",
             "first": "ὧν ἐκτὸς οὐ ῥητέον, ἣν ἀντωμοσίαν καλοῦσιν· οἱ δὲ λόγοι ἀεὶ περὶ ὁμοδούλου",
             "last": "ἀτιμάσασα πανταχῇ φέρεται κατὰ Πίνδαρον, τά τε γᾶς",
             "extra": "At 173e the manuscript reads φέρεται (Burnet πέτεται)."},
            {"folio": "97v", "start": "173e", "end": "174e",
             "first": "ὑπένερθε καὶ τὰ ἐπίπεδα γεωμετροῦσα, οὐρανοῦ τε ὕπερ ἀστρονομοῦσα",
             "last": "ἀποφῆναι, παντάπασιν ἀμβλὺ καὶ ἐπὶ σμικρὸν ὁρώντων ἡγεῖται"},
            {"folio": "98r", "start": "174e", "end": "176a",
             "first": "τὸν ἔπαινον, ὑπὸ ἀπαιδευσίας οὐ δυναμένων εἰς τὸ πᾶν ἀεὶ βλέπειν",
             "last": "θεῶν τε καὶ ἀνδρῶν εὐδαιμόνων βίον ἀληθῆ. εἰ πάντας, ὦ Σώ(κρατες)"},
            {"folio": "98v", "start": "176a", "end": "177a",
             "first": "(Σώ)κρατες, πείθοις ἃ λέγεις ὥσπερ ἐμέ, πλείων ἂν εἰρήνη καὶ κακὰ",
             "last": "τὴν αὑτοῖς ὁμοιότητα τῆς διαγωγῆς ἀεὶ ἕξουσι, κακοὶ κακοῖς",
             "extra": "176a-b ('ἐνθένδε ἐκεῖσε φεύγειν ὅτι τάχιστα· φυγὴ δὲ ὁμοίωσις θεῷ κατὰ τὸ δυνατόν') is in the upper part of this page."},
            {"folio": "99r", "start": "177a", "end": "178b",
             "first": "συνόντες, ταῦτα δὴ καὶ παντάπασιν ὡς δεινοὶ καὶ πανοῦργοι",
             "last": "ὡς φατέ, ὦ Πρωταγόρα, λευκῶν, βαρέων, κού(φων)",
             "extra": "177b begins on line 2 ('οἶδά τοι, ὦ ἑταῖρε'); 177c has 'ἐπὶ δὲ τὰ ἔμπροσθεν ἴωμεν' on line 10 and 'οὐκοῦν ἐνταῦθά που ἦμεν τοῦ λόγου' on line 13."},
        ],
    },
]


PASSAGES += [
    {
        "slug": "symposium-201d-212c",
        "order": 2,
        "tlg": "tlg011",
        "work": "Symposium",
        "range": ("201d", "212c"),
        "ms": "clarke39",
        "title": "Plato, Symposium 201d-212c: Diotima on love and the ascent to beauty itself",
        "translator": "W. R. M. Lamb (1925)",
        "translation_source": "W. R. M. Lamb, Plato III: Lysis, Symposium, Gorgias (Loeb Classical Library, Harvard University Press / Heinemann, 1925), Perseus tlg0059.tlg011.perseus-eng2",
        "date_approx": "c. 385-370 BCE (composition); manuscript 895 AD",
        "description": "Socrates' report of what the priestess Diotima taught him about love: love as a spirit between gods and mortals, the desire to possess the good for ever, and the ascent from one beautiful body to beauty itself, shown on the Clarke Plato (895 AD).",
        "themes": ["plato", "symposium", "diotima", "eros", "beauty", "ascent", "immortality", "theosis", "philosophy", "greek", "verified"],
        "intro": (
            "<p>At the banquet held by the poet Agathon each guest gives a speech in praise of Love (Eros). Socrates does not give his own: "
            "he repeats what he says he learned from Diotima, a wise woman of Mantinea. Love, she taught, is not a god but a great spirit (<em>daimon</em>) "
            "that carries messages between gods and men; it is the desire to possess the good for ever, and so it is also a desire for immortality, "
            "which mortals reach by begetting, in body or in soul. The speech ends with the 'ladder' of love: from one beautiful body to all bodies, "
            "to souls, practices, laws and sciences, until the lover sees beauty itself, pure and unmixed, and becomes, 'if any human being can, immortal' "
            "and dear to the gods (212a).</p>\n\n"
            "<p>The pages shown are from the Clarke Plato (Oxford, Bodleian Library, MS. E. D. Clarke 39), copied in Constantinople in 895, the oldest manuscript of the Symposium (siglum B). "
            "The passage runs over eleven pages, fol. 213r to fol. 218r, each of 34 lines. Each section below is one Stephanus subsection, linked to the page or pages that carry its words; "
            "the pages were identified by reading the first and last lines of each page on the image. The Greek is Burnet's critical text, not a transcription of the manuscript.</p>"
        ),
        "pages": [
            {"folio": "213r", "start": "201b", "end": "202b",
             "first": "ὁ Ἔρως κάλλος. ἀνάγκη, φάναι. τί δέ; τὸ ἐνδεὲς κάλλους καὶ μηδαμῇ",
             "last": "μὴ τοίνυν ἀνάγκαζε ὃ μὴ καλόν ἐστιν αἰσχρὸν εἶναι, μηδὲ ὃ μὴ ἀγαθὸν κακόν"},
            {"folio": "213v", "start": "202b", "end": "203b",
             "first": "οὕτω δὲ καὶ τὸν Ἔρωτα, ἐπειδὴ αὐτὸς ὁμολογεῖς μὴ εἶναι ἀγαθὸν",
             "last": "ὅτε γὰρ ἐγένετο ἡ Ἀφροδίτη, ἡστιῶντο"},
            {"folio": "214r", "start": "203b", "end": "204b",
             "first": "οἱ θεοὶ οἵ τε ἄλλοι καὶ ὁ τῆς Μήτιδος ὑὸς Πόρος",
             "last": "ὥστε ἀναγκαῖον Ἔρωτα φιλόσοφον εἶναι, φιλόσοφον δὲ ὄντα μετα(ξὺ)"},
            {"folio": "214v", "start": "204b", "end": "205b",
             "first": "(μεταξὺ) εἶναι σοφοῦ καὶ ἀμαθοῦς. αἰτία δὲ αὐτῷ καὶ τούτων ἡ γένεσις",
             "last": "ὥσπερ τί; ἦν δʼ ἐγώ. ὥσπερ τόδε"},
            {"folio": "215r", "start": "205b", "end": "206b",
             "first": "οἶσθʼ ὅτι ποίησίς ἐστί τι πολύ",
             "last": "ἀλλʼ ἐγώ σοι, ἔφη, ἐρῶ. ἔστι γὰρ τοῦτο τόκος"},
            {"folio": "215v", "start": "206b", "end": "207b",
             "first": "ἐν καλῷ καὶ κατὰ τὸ σῶμα καὶ κατὰ τὴν ψυχήν. μαντείας, ἦν δʼ ἐγώ",
             "last": "οἴοιτʼ ἄν τις ἐκ λογισμοῦ ταῦτα ποιεῖν· τὰ δὲ θηρία"},
            {"folio": "216r", "start": "207b", "end": "208c",
             "first": "τίς αἰτία οὕτως ἐρωτικῶς διατίθεσθαι",
             "last": "εἰ μὴ ἐννοεῖς ἐνθυμηθεὶς ὡς δεινῶς διά(κεινται)"},
            {"folio": "216v", "start": "208c", "end": "209c",
             "first": "(διά)κεινται ἔρωτι τοῦ ὀνομαστοὶ γενέσθαι καὶ κλέος ἐς τὸν ἀεὶ χρόνον",
             "last": "ἴσχουσι καὶ φιλίαν βεβαιοτέραν, ἅτε καλλιόνων καὶ ἀθανατωτέ(ρων)"},
            {"folio": "217r", "start": "209c", "end": "210d",
             "first": "(ἀθανατωτέ)ρων παίδων κεκοινωνηκότες",
             "last": "πολὺ ἤδη τὸ καλόν, μηκέτι τὸ παρʼ ἑνί, ὥσπερ οἰκέτης, ἀγαπῶν παι(δαρίου)"},
            {"folio": "217v", "start": "210d", "end": "211d",
             "first": "(παι)δαρίου κάλλος ἢ ἀνθρώπου τινὸς ἢ ἐπιτηδεύματος ἑνός",
             "last": "ὃ ἐάν ποτε ἴδῃς, οὐ κατὰ χρυσίον τε καὶ ἐσθῆτα καὶ"},
            {"folio": "218r", "start": "211d", "end": "212d",
             "first": "τοὺς καλοὺς παῖδάς τε καὶ νεανίσκους δόξει σοι εἶναι",
             "last": "τινὰς τῶν ἀκολούθων καὶ ἐπιστῆναι ἐπὶ τὰς θύρας"},
        ],
    },
    {
        "slug": "laws-715e-716d",
        "order": 6,
        "tlg": "tlg034",
        "work": "Laws",
        "range": ("715e", "716d"),
        "ms": "grec1807",
        "title": "Plato, Laws 4.715e-716d: god is the measure of all things",
        "translator": "R. G. Bury (1926)",
        "translation_source": "R. G. Bury, Plato X-XI: Laws (Loeb Classical Library, Harvard University Press / Heinemann, 1926), Perseus tlg0059.tlg034.perseus-eng2",
        "date_approx": "c. 350 BCE (composition); manuscript 9th c.",
        "description": "The Athenian Stranger's address to the new colonists in Laws book 4: god holds the beginning, end and middle of all things; god, not man, is the measure of all things; and the one who would be dear to god must become like him. Shown on Paris gr. 1807, fol. 189v (9th c.).",
        "themes": ["plato", "laws", "god-the-measure", "likeness-to-god", "theosis", "philosophy", "greek", "verified"],
        "intro": (
            "<p>In book 4 of the <em>Laws</em>, Plato's last work, the Athenian Stranger imagines the first settlers of a new city and composes the address they should hear. "
            "It opens with 'the ancient saying' that god holds the beginning, the end and the middle of all things, and that Justice follows him to punish those who fall away from the divine law. "
            "Then comes the reply to Protagoras' 'man is the measure of all things': for us 'god will be the measure of all things in the highest degree, much more than any man'. "
            "Whoever would be dear to such a being must, as far as he can, become like him: the temperate man is dear to god because he is like him.</p>\n\n"
            "<p>The page shown is from Paris, Bibliotheque nationale de France, grec 1807 (siglum A), copied in the second half of the 9th century, the oldest manuscript of the Laws. "
            "The whole passage stands on one page, fol. 189v, written in two columns of 44 lines: it begins on line 2 of the first column and ends in the second column, which closes with the opening words of 717a. "
            "The Greek is Burnet's critical text; the manuscript spells some words differently (for example <em>xynepetai</em> for <em>synepetai</em>).</p>"
        ),
        "pages": [
            {"folio": "189v", "start": "715d", "end": "717a",
             "custom": ("Paris gr. 1807 fol. 189v, two columns of 44 lines. Column 1, line 1 'τὰ τοιαῦτα ἀμβλύτατα αὐτὸς' ends 715d; "
                        "715e begins on line 2 'αὑτοῦ ὁρᾷ, γέρων δὲ ὀξύ(τατα)'; 'ὁ μὲν δὴ θεός, ὥσπερ καὶ ὁ παλαιὸς λόγος' is on lines 10-11 and 716a 'μέσα τῶν ὄντων ἁπάντων' on lines 12-13; "
                        "column 1 ends with 'τοῦτό γε· ὡς τῶν ξυνακολου(θησόντων)' (716b). Column 2 begins 'θησόντων ἐσόμενον τῷ θεῷ', "
                        "has 716c 'τίς οὖν δὴ πρᾶξις φίλη' on line 3, and ends 'μάτην οὖν περὶ θεοὺς ὁ πολὺς' (717a).")},
        ],
    },
]


PASSAGES += [
    {
        "slug": "phaedrus-245c-250c",
        "order": 3,
        "tlg": "tlg012",
        "work": "Phaedrus",
        "range": ("245c", "250c"),
        "ms": "clarke39",
        "title": "Plato, Phaedrus 245c-250c: the immortal soul, the winged chariot and the place beyond the heavens",
        "translator": "H. N. Fowler (1914)",
        "translation_source": "Harold North Fowler, Plato I: Euthyphro, Apology, Crito, Phaedo, Phaedrus (Loeb Classical Library, Harvard University Press / Heinemann, 1914), Perseus tlg0059.tlg012.perseus-eng2",
        "date_approx": "c. 370 BCE (composition); manuscript 895 AD",
        "description": "Socrates' proof that every soul is immortal because it moves itself, followed by the myth of the soul as a winged chariot that follows the gods to the place beyond the heavens, where it sees true being; shown on the Clarke Plato (895 AD).",
        "themes": ["plato", "phaedrus", "immortality", "soul", "chariot", "recollection", "theosis", "philosophy", "greek", "verified"],
        "intro": (
            "<p>In his second speech on love in the <em>Phaedrus</em>, Socrates argues that every soul is immortal, since what moves itself never ceases to move. "
            "He then describes the soul in an image: a charioteer with two winged horses. The souls of the gods drive easily to the outer rim of heaven and look on what lies beyond it, "
            "'the colourless, formless and intangible truly existing essence'; human souls follow as they can, lose their wings and fall into bodies. "
            "The soul of the philosopher regains its wings first, 'for it is always, so far as it is able, in communion through memory with those things the communion with which causes God to be divine' (249c).</p>\n\n"
            "<p>The pages shown are from the Clarke Plato (Oxford, Bodleian Library, MS. E. D. Clarke 39), copied in Constantinople in 895, the oldest manuscript of the Phaedrus (siglum B). "
            "The passage runs from fol. 232v line 2 to the top of fol. 235r, six pages of 34 lines. Each section is one Stephanus subsection, linked to the page or pages that carry its words, "
            "identified by reading the first and last lines of each page on the image. The Greek is Burnet's critical text, not a transcription of the manuscript.</p>"
        ),
        "pages": [
            {"folio": "232v", "start": "245b", "end": "246b",
             "first": "ἐπιπέμπεται. ἡμῖν δὲ ἀποδεικτέον αὖ τοὐναντίον, ὡς ἐπʼ εὐτυχίᾳ",
             "last": "θνητόν τε καὶ ἀθάνατον ζῷον ἐκλήθη πειρατέον εἰπεῖν. ψυχὴ πᾶσα",
             "extra": "245c begins on line 2 ('τῇ μεγίστῃ παρὰ θεῶν ἡ τοιαύτη μανία δίδοται')."},
            {"folio": "233r", "start": "246b", "end": "247c",
             "first": "παντὸς ἐπιμελεῖται τοῦ ἀψύχου, πάντα δὲ οὐρανὸν περι(πολεῖ)",
             "last": "ἔξω πορευθεῖσαι ἔστησαν ἐπὶ τῷ τοῦ οὐρανοῦ νώτῳ, στάσας"},
            {"folio": "233v", "start": "247c", "end": "248c",
             "first": "δὲ αὐτὰς περιάγει ἡ περιφορά, αἱ δὲ θεωροῦσι τὰ ἔξω τοῦ οὐρανοῦ",
             "last": "ἥ τε πτεροῦ φύσις, ᾧ ψυχὴ κουφίζεται, τούτῳ τρέφεται· θεσμός τε",
             "extra": "Line 2 has 'τὸν δὲ ὑπερουράνιον τόπον οὔτε τις ὕμνησέ πω τῶν τῇδε'."},
            {"folio": "234r", "start": "248c", "end": "249c",
             "first": "(Ἀ)δραστείας ὅδε. ἥτις ἂν ψυχὴ θεῷ συνοπαδὸς γενομένη κατίδῃ τι",
             "last": "καὶ ὑπεριδοῦσα ἃ νῦν εἶναί φαμεν, καὶ ἀνακύψασα εἰς τὸ ὂν ὄντως"},
            {"folio": "234v", "start": "249c", "end": "250c",
             "first": "διὸ δὴ δικαίως μόνη πτεροῦται ἡ τοῦ φιλοσόφου διάνοια",
             "last": "ἐν αὐγῇ καθαρᾷ, καθαροὶ ὄντες καὶ ἀσήμαντοι τούτου ὃ νῦν σῶμα",
             "extra": "Line 2 reads 'γὰρ ἐκείνοις ἀεί ἐστιν μνήμῃ κατὰ δύναμιν, πρὸς οἷσπερ θεὸς' (249c)."},
            {"folio": "235r", "start": "250c", "end": "251c",
             "first": "περιφέροντες ὀνομάζομεν, ὀστρέου τρόπον δεδεσμευμένοι",
             "last": "ἵμερος καλεῖται, δεχομένη τὸν ἵμερον ἄρδεταί τε καὶ θερ(μαίνεται)",
             "extra": "Line 2 begins 'ταῦτα μὲν οὖν μνήμῃ κεχαρίσθω', still within 250c."},
        ],
    },
]


PASSAGES += [
    {
        "slug": "phaedo-78b-84b",
        "order": 4,
        "tlg": "tlg004",
        "work": "Phaedo",
        "range": ("78b", "84b"),
        "ms": "clarke39",
        "title": "Plato, Phaedo 78b-84b: the soul's kinship with the divine",
        "translator": "H. N. Fowler (1914)",
        "translation_source": "Harold North Fowler, Plato I: Euthyphro, Apology, Crito, Phaedo, Phaedrus (Loeb Classical Library, Harvard University Press / Heinemann, 1914), Perseus tlg0059.tlg004.perseus-eng2",
        "date_approx": "c. 385-370 BCE (composition); manuscript 895 AD",
        "description": "Socrates on his last day argues that the soul is most like the divine, immortal and unchanging, and the body most like the mortal; the soul that has practised philosophy goes at death to what is like itself, the divine; shown on the Clarke Plato (895 AD).",
        "themes": ["plato", "phaedo", "soul", "immortality", "kinship-with-the-divine", "purification", "theosis", "philosophy", "greek", "verified"],
        "intro": (
            "<p>The <em>Phaedo</em> tells of Socrates' last conversation in prison before he drank the hemlock. In this passage (the 'affinity argument') he divides things into two kinds: "
            "the invisible, which is always the same, and the visible, which never stays the same. The soul is more like the first, the body like the second; "
            "and 'the soul is most like the divine and immortal and intellectual and uniform and indissoluble and ever unchanging' (80b). "
            "A soul that has lived by philosophy, keeping itself pure of the body, departs at death 'to that place which is, like itself, invisible, divine, immortal and wise' (81a), "
            "while souls bound to the body wander and are born again; philosophy is described as the release of the soul.</p>\n\n"
            "<p>The pages shown are from the Clarke Plato (Oxford, Bodleian Library, MS. E. D. Clarke 39), copied in Constantinople in 895, the oldest manuscript of the Phaedo (siglum B). "
            "The passage runs from fol. 37r to the top of fol. 40v, eight pages of 34 lines. On fol. 38v the inner part of the first lines is damaged and repaired, and some letters there have been retraced by a later hand. "
            "Each section is one Stephanus subsection, linked to the page or pages that carry its words, identified by reading the first and last lines of each page on the image. "
            "The Greek is Burnet's critical text, not a transcription of the manuscript.</p>"
        ),
        "pages": [
            {"folio": "37r", "start": "77c", "end": "78c",
             "first": "εἰς ταὐτὸν καὶ ὃν πρὸ τούτου ὡμολογήσαμεν, τὸ γίγνεσθαι πᾶν",
             "last": "δοκεῖ μοι, ἔφη, οὕτως ἔχειν, ὁ Κέβης. οὐκοῦν ἅπερ"},
            {"folio": "37v", "start": "78c", "end": "79c",
             "first": "κατὰ ταὐτὰ καὶ ὡσαύτως ἔχει, ταῦτα μάλιστα εἰκὸς εἶναι τὰ ἀσύνθετα",
             "last": "ἢ διʼ ἄλλης τινὸς αἰσθήσεως, τοῦτο γάρ ἐστιν τὸ διὰ τοῦ σώματος"},
            {"folio": "38r", "start": "79c", "end": "80c",
             "first": "τὸ διʼ αἰσθήσεως σκοπεῖν τι, τότε μὲν ἕλκεται ὑπὸ τοῦ σώματος",
             "last": "τὸ μὲν ὁρατὸν αὐτοῦ, τὸ σῶμα, καὶ ἐν ὁρατῷ κείμενον, ὃ δὴ νεκρὸν καλ(οῦμεν)"},
            {"folio": "38v", "start": "80c", "end": "81b",
             "first": "(ᾧ) προσήκει διαλύεσθαι ... οὐκ εὐθὺς τούτων",
             "last": "τὸ δὲ τοῖς ὄμμασι σκοτῶδες καὶ ἀιδές, νοητὸν δὲ καὶ φι(λοσοφίᾳ)",
             "extra": "The inner ends of lines 1-7 are damaged and repaired; line 2 reads '... συχνὸν ἐπιμένει χρόνον, ἐὰν μὲν'."},
            {"folio": "39r", "start": "81b", "end": "82b",
             "first": "(φι)λοσοφίᾳ αἱρετόν, τοῦτο δὲ εἰθισμένη μισεῖν τε καὶ τρέμειν",
             "last": "πολιτικόν τε καὶ ἥμερον γένος, ἤ που μελιττῶν ἢ σφηκῶν"},
            {"folio": "39v", "start": "82b", "end": "83b",
             "first": "ἢ μυρμήκων, ἢ καὶ εἰς ταὐτόν γε πάλιν τὸ ἀνθρώπινον γένος",
             "last": "μηδὲν ἡγεῖσθαι ἀληθές· εἶναι δὲ τὸ μὲν τοιοῦτον"},
            {"folio": "40r", "start": "83b", "end": "84b",
             "first": "(αἰσθη)τόν τε καὶ ὁρατόν, ὃ δὲ αὐτὴ ὁρᾷ, νοητόν τε καὶ ἀιδές",
             "last": "εἰς τὸ συγγενὲς καὶ εἰς τὸ τοιοῦτον ἀφικομένη ἀπηλλάχθαι τῶν"},
            {"folio": "40v", "start": "84b", "end": "85b",
             "first": "ἀνθρωπίνων κακῶν. ἐκ δὴ τῆς τοιαύτης τροφῆς οὐδὲν δεινὸν μὴ",
             "last": "ᾄδουσι καὶ τέρπονται ἐκείνην τὴν ἡμέραν διαφε(ρόντως)",
             "extra": "Line 2 reads 'ταῦτα δʼ ἐπιτηδεύσασα, ὦ Σιμμία τε καὶ Κέβης, ὅπως', still within 84b."},
        ],
    },
]


# ---------------------------------------------------------------------------
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def canvases(ms):
    m = json.loads(MSS[ms]["manifest"].read_text(encoding="utf-8"))
    out = {}
    if "items" in m:  # IIIF Presentation 3 (Gallica)
        for i, c in enumerate(m["items"], 1):
            lab = c["label"]["fr"][0]
            out[f"fol. {lab}"] = {"service": c["items"][0]["items"][0]["body"]["service"][0]["id"],
                                  "uuid": f"f{c['items'][0]['items'][0]['body']['service'][0]['id'].rsplit('/f', 1)[1]}",
                                  "w": c["width"], "h": c["height"]}
        return out
    for c in m["sequences"][0]["canvases"]:
        out[c["label"]] = {"service": c["images"][0]["resource"]["service"]["@id"],
                           "uuid": c["@id"].rsplit("/", 1)[1].replace(".json", ""),
                           "w": c["width"], "h": c["height"]}
    return out


def get_scan(ms, folio, cv, force):
    path = SCAN_DIR / f"{ms}-f{folio}.jpg"
    if path.exists() and not force:
        return path
    c = cv[f"fol. {folio}"]
    img = Image.open(io.BytesIO(fetch(f"{c['service']}/full/{MSS[ms]['width']},/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def segments(path):
    """Split a Perseus TEI text at Stephanus section milestones.
    Returns ordered list of (milestone, text). Notes are dropped; a speaker label
    is kept only when the speaker changes."""
    root = ET.parse(path).getroot()
    body = root.find(f".//{TEI}body")
    segs, cur = [], {"n": "__start__", "buf": []}
    state = {"who": None, "last_label_who": None, "in_said": 0}

    def emit(s):
        cur["buf"].append(s)

    def walk(el):
        tag = el.tag.replace(TEI, "")
        if tag == "milestone":
            if el.get("unit") == "section":
                segs.append((cur["n"], "".join(cur["buf"])))
                cur["n"], cur["buf"] = el.get("n"), []
            elif el.get("unit") == "para":
                emit(" ")
            return
        if tag in ("note", "bibl", "head"):
            return
        if tag == "label":
            if state["in_said"] and state["who"] != state["last_label_who"]:
                emit(" " + "".join(el.itertext()).strip() + " ")
                state["last_label_who"] = state["who"]
            return
        if tag == "said":
            state["who"] = el.get("who")
            state["in_said"] += 1
        if tag in ("q", "quote"):
            emit(" ")
        if tag == "del":
            emit("[")
        if tag == "add":
            emit("<")
        if el.text:
            emit(el.text)
        for ch in el:
            walk(ch)
            if ch.tail:
                emit(ch.tail)
        if tag == "said":
            state["in_said"] -= 1
        if tag == "del":
            emit("]")
        if tag == "add":
            emit(">")
        if tag in ("p", "l", "said", "q", "quote"):
            emit(" ")

    walk(body)
    segs.append((cur["n"], "".join(cur["buf"])))
    out = []
    for n, t in segs:
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"\s+([,.;·:?!])", r"\1", t)
        out.append((n, t))
    return out


def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def steph_key(ref):
    m = re.match(r"(\d+)([a-e])$", ref)
    return (int(m.group(1)), m.group(2))


def page_note(ms, p, cv):
    uuid = cv[f"fol. {p['folio']}"]["uuid"]
    if p.get("custom"):
        return p["custom"] + " Viewer: " + MSS[ms]["viewer"].format(uuid=uuid)
    s = (f"{MSS[ms]['short']} fol. {p['folio']} (34 lines) runs from '{p['first']}' on line 1 ({p['start']}) "
         f"to '{p['last']}' on line {MSS[ms]['lines']} ({p['end']}).")
    if p.get("extra"):
        s += " " + p["extra"]
    s += " Viewer: " + MSS[ms]["viewer"].format(uuid=uuid)
    return s


def build_passage(P, force):
    ms = P["ms"]
    cv = canvases(ms)
    grc = dict(segments(SRC / f"tlg0059.{P['tlg']}.perseus-grc2.xml"))
    eng = dict(segments(SRC / f"tlg0059.{P['tlg']}.perseus-eng2.xml"))
    names = [n for n, _ in segments(SRC / f"tlg0059.{P['tlg']}.perseus-grc2.xml")]
    a, b = names.index(P["range"][0]), names.index(P["range"][1])
    refs = names[a:b + 1]
    files = {}
    for p in P["pages"]:
        files[p["folio"]] = get_scan(ms, p["folio"], cv, force)
        print(f"  fol. {p['folio']}: {files[p['folio']].stat().st_size} bytes")
    sections = []
    for r in refs:
        assert r in eng, (P["slug"], r, "missing in English")
        k = steph_key(r)
        pages = [p for p in P["pages"] if steph_key(p["start"]) <= k <= steph_key(p["end"])]
        assert pages, (P["slug"], r, "no page")
        if len(pages) == 1:
            note = f"On {MSS[ms]['short']} fol. {pages[0]['folio']}. " + page_note(ms, pages[0], cv)
        else:
            note = (f"Starts on fol. {pages[0]['folio']} and continues on fol. {pages[-1]['folio']} (page break inside this subsection). "
                    + " ".join(page_note(ms, p, cv) for p in pages))
        note += " Checked on the images. The Greek shown is Burnet's critical text; the copyist's wording differs from it in small details."
        sections.append({
            "section": r,
            "original_ref": f"Plato, {P['work']} {r}; {MSS[ms]['short']} fol. " + ", ".join(p["folio"] for p in pages),
            "original_text": html_escape(grc[r]),
            "text": html_escape(eng[r]),
            "scan_pages": [f"{KEY}/{files[p['folio']].name}" for p in pages],
            "scan_note": note,
        })
    tid = PREFIX + P["slug"]
    pages_used = [p["folio"] for p in P["pages"]]
    entry = {
        "id": tid, "slug": tid, "title": P["title"],
        "language": f"Greek (Burnet) / English ({P['translator']})",
        "source": f"{MSS[ms]['shelfmark']} fol. {pages_used[0]}" + (f"-{pages_used[-1]}" if len(pages_used) > 1 else "") + f" ({MSS[ms]['holder']}) + Burnet Greek (Perseus) + {P['translator']} English (Perseus)",
        "description": P["description"],
        "introduction": P["intro"],
        "translator_notes": [
            "Greek: John Burnet, Platonis Opera (Oxford Classical Texts, 1900-1907), Perseus digital text. Square brackets mark words Burnet deletes.",
            f"English: {P['translation_source']}. The English section breaks follow the translator's own Stephanus markers, so a few words may fall on the neighbouring side of a break compared with the Greek.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"{MSS[ms]['holder']}: {MSS[ms]['object']} (folios {', '.join(pages_used)})",
            "scan_license": MSS[ms]["license"],
            "scan_manuscript": MSS[ms]["desc"],
            "scan_mapping": "First and last lines of every page (and column) read on the image and matched to Burnet's text (words recorded per page in each scan_note); " + MSS[ms]["mapping_ref"][0],
            "scan_mapping_urls": [MSS[ms]["mapping_ref"][1]] + [MSS[ms]["viewer"].format(uuid=cv[f"fol. {f}"]["uuid"]) for f in pages_used],
            "scan_local_paths": [f"{KEY}/{files[f].name}" for f in pages_used],
            "original_text_source": f"John Burnet, Platonis Opera (Oxford, 1900-1907), Perseus canonical-greekLit tlg0059.{P['tlg']}.perseus-grc2 ({PERSEUS_GH}/{P['tlg']})",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": f"{P['translation_source']} ({PERSEUS_GH}/{P['tlg']})",
            "translation_license": "public domain in the US (published before 1929); Perseus digital text CC BY-SA 4.0",
            "translator": P["translator"],
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": P["order"], "title": P["title"], "author_id": "plato",
        "language": "Greek", "era": "Classical", "tradition": "greek", "category": "philosophy",
        "date_approx": P["date_approx"], "century": -4,
        "source": entry["source"], "description": P["description"], "themes": P["themes"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[f].name}", "caption": f"{MSS[ms]['short']} fol. {f}"} for f in pages_used]},
    }
    print(f"wrote {tid} ({len(sections)} sections)")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    rows = [build_passage(P, args.force) for P in PASSAGES]
    coll = {
        "collection": {
            "key": KEY,
            "prefix": PREFIX,
            "label": "Plato: becoming like god",
            "group": "Greece",
            "date_sort": -380,
            "author_name": "Plato (c. 428-348 BCE); Clarke Plato manuscript of 895 AD",
            "source_url": MSS["clarke39"]["object"],
            "critical_edition": "Burnet, Platonis Opera (1900-1907), via Perseus",
            "translator_name": "H. N. Fowler, W. R. M. Lamb, R. G. Bury (Loeb, 1914-1926)",
            "original_lang_label": "Greek · Burnet",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "plato theaetetus homoiosis theoi becoming like god symposium diotima phaedrus phaedo clarke plato",
            "description": "Plato's passages on the divine in man and on becoming like god, each shown on the pages of the oldest manuscript that carries it.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
