#!/usr/bin/env python3
"""
import_atlantis.py — ancient testimonia on Atlantis outside Plato's Timaeus and Critias (which are
the collections plato-timaeus and plato-critias), one entry per passage, every section linked to
the manuscript page(s) that carry it.

Uses the builder, text helpers and the Pliny passage defined in import_hyperborea.py; source texts
are cached in data/sources/hyperborea/ (shared Perseus and Gutenberg files) and
data/sources/atlantis/ (LacusCurtius Diodorus book 3, Stanley's Aelian).

Chain of evidence: as in import_hyperborea.py. Every folio/line position was read on the page images
and is quoted in the section's scan_note.

Usage:
    python3 scripts/import_atlantis.py [--force]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_hyperborea as hb  # noqa: E402

COLLECTION = {
    "key": "atlantis",
    "prefix": "verified-atlantis-",
    "label": "Atlantis: the ancient testimonia",
    "group": "Greece",
    "date_sort": -355,
    "author_name": "Greek and Latin writers after Plato, 5th c. BCE - 3rd c. AD (medieval manuscripts)",
    "source_url": "https://www.perseus.tufts.edu/",
    "critical_edition": "Perseus editions named per passage",
    "translator_name": "Public-domain translators named per passage",
    "original_lang_label": "Greek / Latin",
    "original_lang_code": "grc",
    "edition_label": "",
    "search_terms": "atlantis atlantes atlantians atlas plato solon posidonius strabo pliny diodorus meropis theopompus",
    "description": ("Ancient passages on Atlantis and the peoples of Atlas outside Plato's own dialogues, each shown on the "
                    "medieval manuscript page that carries it. Plato's Timaeus and Critias are separate collections."),
}

PASSAGE_BUILDERS = [hb.herodotus_4_184_185, hb.diodorus_3_53_61, hb.strabo_2_3_6, hb.pliny_2_205, hb.aelian_vh_3_18]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    hb.build(COLLECTION, [f() for f in PASSAGE_BUILDERS], args.force)


if __name__ == "__main__":
    main()
