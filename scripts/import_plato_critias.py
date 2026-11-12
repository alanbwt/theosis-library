#!/usr/bin/env python3
"""
import_plato_critias.py — Plato, Critias (complete, as far as Plato wrote it), one entry per
Stephanus page (106-121), one section per Stephanus section, each section linked to the folio
side(s) of Paris, BnF grec 1807 (Plato A, c. 850-875) that carry it.

Chain of evidence (details in import_plato_timaeus.py, whose builder this script reuses):
  1. SCAN     Paris gr. 1807 fol. 145r-151r, BnF IIIF (Gallica ark:/12148/btv1b8419248n), NoC-NC.
              The Critias begins at the top of 145r col. a under the title
              "platonos kritias e atlantikos" and breaks off in 151r col. b with "kai synageiras
              eipen"; the rest of that column is blank and there is no end title.
  2. MAPPING  Own visual check: the opening words of all 26 columns (145r a - 151r b) were read
              on the images and located in Burnet's text (COLUMNS below, Burnet's wording).
  3. GREEK    Burnet, Platonis Opera IV (1902), Perseus tlg0059.tlg032.perseus-grc2 (CC BY-SA).
  4. ENGLISH  R. G. Bury, Loeb Plato IX (1929), Perseus tlg0059.tlg032.perseus-eng2 (US public
              domain since 2025; Perseus text CC BY-SA).

Usage:
    python3 scripts/import_plato_critias.py [--force]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_plato_timaeus as base  # noqa: E402

COLUMNS = [
    ("145r", "a", "ὡς ἅσμενος, ὦ Σώκρατες, οἷον ἐκ"),
    ("145r", "b", "θνητῶν πρὸς ἡμᾶς. ἡ γὰρ ἀπειρία"),
    ("145v", "a", "-τὰ καὶ ἀνθρώπινα ἀκριβῶς ἐξετάζομεν. ἐκ"),
    ("145v", "b", "-γαθοὺς ὄντας ἀναφαίνειν τε καὶ ὑμνεῖν"),
    ("146r", "a", "-τε, καθʼ ἕκαστα ἡ τοῦ λόγου"),
    ("146r", "b", "φρονήσει πεφυκυῖαν, ἄνδρας δὲ ἀγαθοὺς ἐμποιήσαντες"),
    ("146v", "a", "ἑκάστων ἀπομνημονεύεται, τούτων ἐκείνους τὰ πολλὰ"),
    ("146v", "b", "-ρωπίαν ἔχοντας, ἐν ἀριστερᾷ δὲ πρὸς"),
    ("147r", "a", "ἐκέκτητο, καὶ πολλὴν ἐν τοῖς ὄρεσιν"),
    ("147r", "b", "πλὴν ὀλίγον ἐπίπεδος ἄνωθεν. ᾠκεῖτο δὲ"),
    ("147v", "a", "ταὐτὸν αὑτῶν εἶναι πρὸς τὸν ἀεὶ"),
    ("147v", "b", "-ματα, μηδὲν ὑμῖν ἔστω θαῦμα· τὸ"),
    ("148r", "a", "τήν τε ἐν μέσῳ νῆσον οἷα"),
    ("148r", "b", "-σιππον μὲν τὸν πρότερον, Μήστορα δὲ"),
    ("148v", "a", "-νήματα παρέχεται, πάντα φέρουσα ἄφθονα, τά"),
    ("148v", "b", "τὴν ἀρχαίαν ἦσαν μητρόπολιν, πρῶτον μὲν"),
    ("149r", "a", "πέντε σταδίων τὴν διάμετρον εἶχεν. ταύτην"),
    ("149r", "b", "δʼ ἐπὶ τούτοις σύμμετρον ἰδεῖν, εἶδος"),
    ("149v", "a", "-στήσαντες οἰκοδομήσεις καὶ δένδρων φυτεύσεις πρεπούσας"),
    ("149v", "b", "τριήρεσιν προσήκει, πάντα δὲ ἐξηρτυμένα ἱκανῶς"),
    ("150r", "a", "ὄρη τότε ὑμνεῖτο πλῆθος καὶ μέγεθος"),
    ("150r", "b", "τήν τε ἐκ τῶν ὀρῶν ὕλην"),
    ("150v", "a", "τῆς βασιλικῆς πόλεως, τῶν δὲ ἐννέα"),
    ("150v", "b", "-γίζοιεν πάντα τοῦ ταύρου τὰ μέλη"),
    ("151r", "a", "τὸ βασιλικὸν καταλύειν ἐπιχειρῇ γένος, κοινῇ"),
    ("151r", "b", "ἐξίτηλος ἐγίγνετο ἐν αὐτοῖς πολλῷ τῷ"),
]

TOPICS = {
    106: "Timaeus ends his discourse with a prayer and hands over to Critias",
    107: "Critias asks for indulgence: talk about mortals is judged more strictly than talk about gods",
    108: "Hermocrates encourages Critias; the invocation of Memory",
    109: "the war 9,000 years ago; the gods divide the earth; Hephaestus and Athena receive Attica",
    110: "names remembered, deeds forgotten; the classes of ancient Athens; the borders of Attica",
    111: "the fertility of ancient Attica and the soil carried off by floods",
    112: "the ancient Acropolis, the guardians' dwellings and the number of the warriors",
    113: "why the Atlantid names are Greek; Poseidon, Cleito and the rings of land and sea",
    114: "Atlas and the ten kings; the wealth of the island",
    115: "the produce of Atlantis; bridges and canals through the rings",
    116: "the walls, the royal citadel and the temple of Poseidon",
    117: "springs, baths, gardens, docks and the outer wall",
    118: "the great plain and its ditch and canals",
    119: "the allotments and the army; the laws of Poseidon and the bull sacrifice",
    120: "the kings' oath and judgment; the laws binding the ten kings",
    121: "the kings' decline; Zeus calls the gods together (the dialogue breaks off)",
}

ATLANTIS_NOTE = (
    "<p>The <em>Critias</em> is Plato's full account of Atlantis and of the Athens that fought it: the land and city of "
    "ancient Athens (109b-112e), then the island of Atlantis, Poseidon's kingdom beyond the Pillars of Heracles, its "
    "royal city, plain, army and laws (113b-120d), and the moral decline of its kings (120e-121c). Plato left the "
    "dialogue unfinished; it stops in mid-sentence as Zeus begins to speak, and the manuscript shown here stops at the "
    "same words.</p>"
)

WORK = {
    "key": "plato-critias", "name": "Critias", "abbr": "Crit.", "tlg": "tlg032",
    "columns": COLUMNS, "topics": TOPICS, "atlantis_pages": set(TOPICS), "atlantis_note": ATLANTIS_NOTE,
    "collection": {
        "key": "plato-critias",
        "prefix": "verified-plato-critias-",
        "label": "Plato, Critias (Paris gr. 1807)",
        "group": "Greece",
        "date_sort": -359,
        "author_name": "Plato (c. 360 BCE); Paris, BnF grec 1807, c. 850-875",
        "source_url": base.GALLICA,
        "critical_edition": "Burnet, Platonis Opera IV (1902), via Perseus",
        "translator_name": "R. G. Bury (Loeb, 1929)",
        "original_lang_label": "Greek · Burnet",
        "original_lang_code": "grc",
        "edition_label": "",
        "search_terms": "plato critias atlantis atlantikos poseidon cleito atlas ancient athens paris a grec 1807",
        "description": ("The Critias, Plato's unfinished account of ancient Athens and the island of Atlantis, complete as far as "
                        "Plato wrote it. Every Stephanus section is shown on the page of the oldest manuscript that carries it, "
                        "Paris gr. 1807 (9th century), with Burnet's Greek and R. G. Bury's English."),
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    base.build(WORK, args.force)


if __name__ == "__main__":
    main()
