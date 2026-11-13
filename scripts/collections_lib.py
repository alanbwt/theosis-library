#!/usr/bin/env python3
"""
collections_lib.py — registry of self-describing collections.

Each collection lives in data/collections/<key>.json:

{
  "collection": {
    "key": "unas",                                  # lowercase, [a-z0-9-]
    "prefix": "verified-unas-",                     # every entry id starts with this
    "label": "Pyramid Texts of Unas",               # breadcrumb / reading-order label
    "group": "Egypt",                               # library shelf (see SHELVES)
    "date_sort": -2350,                             # year for chronological shelf order (BCE negative)
    "author_name": "Pyramid of Unas, Saqqara (c. 2350 BCE)",
    "source_url": "https://...",
    "critical_edition": "Thesaurus Linguae Aegyptiae ...",
    "translator_name": "Samuel A. B. Mercer (1952)",
    "original_lang_label": "Egyptian · TLA transliteration",
    "original_lang_code": "egy",                    # BCP-47-ish; drives fonts
    "edition_label": "",                            # optional label for section.edition_text blocks
    "search_terms": "pyramid texts unas saqqara",  # extra words for search / homepage pills
    "description": "One-paragraph shelf description."
  },
  "texts": [ ...rows in data/texts.json format, each with an integer "order" ... ],
  "authors": [ ...rows in data/authors.json format (optional) ... ],
  "redirects": [ ["/library/old-id", "/library/new-id"], ... ]   # optional
}
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLL_DIR = ROOT / "data" / "collections"

# Library shelves, oldest civilisations first. Collections name one of these in "group".
SHELVES = [
    "Earliest Writing",
    "Mesopotamia",
    "Egypt",
    "Levant & Israel",
    "Old Testament",
    "Persia",
    "India",
    "China",
    "Greece",
    "Dead Sea Scrolls & Second Temple",
    "Rome",
    "New Testament",
    "Early Christian",
    "Later Traditions",
]

SHELF_NOTES = {
    "Earliest Writing": "The first written records, from the cities of Sumer.",
    "Mesopotamia": "Sumerian and Babylonian literature, law and history on clay.",
    "Egypt": "Pyramid walls, papyri and stelae of the Nile valley.",
    "Levant & Israel": "Inscriptions from the lands of the Old Testament.",
    "Old Testament": "The Hebrew scriptures in their oldest complete manuscript.",
    "Persia": "The Achaemenid kings and the Avesta of Zarathustra.",
    "India": "The Vedas, the Upanishads and the Bhagavad Gita.",
    "China": "Oracle bones and the classics of the Zhou and Han.",
    "Greece": "Homer, Hesiod, Plato and the Greek historians.",
    "Dead Sea Scrolls & Second Temple": "Jewish writings from the Babylonian exile to the fall of the Temple.",
    "Rome": "Latin authors on the Roman world and the first Christians.",
    "New Testament": "The great codices of the Greek Bible, chapter by chapter.",
    "Early Christian": "Christian writings outside the New Testament canon.",
    "Later Traditions": "Later scriptures and poetry kept for comparison.",
}

# Collections built before the registry existed (rows live only in data/texts.json).
# A data/collections/<key>.json file with the same key replaces the legacy entry.
LEGACY = [
    {"key": "sinaiticus", "prefix": "verified-sinaiticus-", "label": "Codex Sinaiticus", "group": "New Testament", "date_sort": 350,
     "dates": "c. 330-360 AD", "language": "Greek",
     "critical_edition": "Codex Sinaiticus Project transcription; Tischendorf 8th ed. for comparison", "translator_name": "King James Version (1611); Brenton; Lightfoot",
     "description": "The oldest complete New Testament, with much of the Greek Old Testament, the Epistle of Barnabas and the Shepherd of Hermas. Every chapter on its own folio from the Codex Sinaiticus Project."},
    {"key": "vaticanus", "prefix": "verified-vaticanus-", "label": "Codex Vaticanus", "group": "New Testament", "date_sort": 325,
     "dates": "c. 300-350 AD", "language": "Greek",
     "critical_edition": "Codex Vaticanus transcription (NTVMR); Tischendorf 8th ed. for comparison", "translator_name": "King James Version (1611)",
     "description": "The Vatican Library's 4th-century Greek Bible, New Testament chapters mapped verse by verse to its pages."},
    {"key": "alexandrinus", "prefix": "verified-alexandrinus-", "label": "Codex Alexandrinus", "group": "New Testament", "date_sort": 420,
     "dates": "c. 400-440 AD", "language": "Greek",
     "critical_edition": "Codex Alexandrinus transcription (NTVMR); Tischendorf 8th ed. for comparison", "translator_name": "King James Version (1611)",
     "description": "The British Library's 5th-century Greek Bible, New Testament chapters on the 1909 photographic facsimile."},
    {"key": "bezae", "prefix": "verified-bezae-", "label": "Codex Bezae", "group": "New Testament", "date_sort": 400,
     "dates": "c. 400 AD", "language": "Greek",
     "critical_edition": "Codex Bezae transcription (NTVMR), Tischendorf where none is open", "translator_name": "King James Version (1611)",
     "description": "The Greek-Latin Gospels and Acts at Cambridge, with its distinctive Western text."},
    {"key": "washingtonianus", "prefix": "verified-washingtonianus-", "label": "Codex Washingtonianus", "group": "New Testament", "date_sort": 410,
     "dates": "4th-5th c. AD", "language": "Greek",
     "critical_edition": "Codex W transcription (NTVMR, IGNTP) for Mark and John; Tischendorf elsewhere", "translator_name": "King James Version (1611)",
     "description": "The Freer Gospels in the Smithsonian, including the Freer Logion in Mark 16."},
    {"key": "leningrad", "prefix": "verified-leningrad-", "label": "Leningrad Codex", "group": "Old Testament", "date_sort": 1008,
     "dates": "1008 AD", "language": "Hebrew",
     "critical_edition": "Unicode/XML Leningrad Codex (tanach.us)", "translator_name": "King James Version (1611)",
     "description": "The oldest complete manuscript of the Hebrew Old Testament, all 929 chapters on their pages."},
    {"key": "1qisaa", "prefix": "verified-1qisaa-", "label": "Great Isaiah Scroll (1QIsa-a)", "group": "Dead Sea Scrolls & Second Temple", "date_sort": -125,
     "dates": "c. 125 BCE", "language": "Hebrew",
     "critical_edition": "ETCBC Dead Sea Scrolls transcription of 1QIsa-a", "translator_name": "King James Version (1611)",
     "description": "The complete book of Isaiah from Qumran Cave 1, a thousand years older than the medieval codices, column by column."},
    {"key": "venetus", "prefix": "verified-venetus-", "label": "Homer, Iliad (Venetus A)", "group": "Greece", "date_sort": -750,
     "dates": "c. 750 BCE (composition); 10th c. manuscript", "language": "Greek",
     "critical_edition": "Venetus A diplomatic text (Homer Multitext); Monro & Allen for comparison", "translator_name": "A. T. Murray (1924); Book 1 Samuel Butler (1898)",
     "description": "All 24 books of the Iliad on the Venetus A manuscript, one section per page, with the manuscript's own text from the Homer Multitext project."},
    {"key": "gilgamesh", "prefix": "verified-gilgamesh-", "label": "Epic of Gilgamesh (Nineveh tablets)", "group": "Mesopotamia", "date_sort": -1200,
     "dates": "c. 1200 BCE (composition); 7th c. BCE tablets", "language": "Akkadian",
     "critical_edition": "Electronic Babylonian Library transliteration", "translator_name": "R. Campbell Thompson (1928)",
     "description": "The Standard Babylonian epic on the clay tablets from Ashurbanipal's library at Nineveh."},
    {"key": "parisino-petropolitanus", "prefix": "verified-parisino-petropolitanus-", "label": "Quran, Codex Parisino-petropolitanus", "group": "Later Traditions", "date_sort": 680,
     "dates": "late 7th c. AD", "language": "Arabic",
     "critical_edition": "Tanzil Uthmani text; folio mapping Corpus Coranicum", "translator_name": "Marmaduke Pickthall (1930)",
     "description": "One of the oldest Quran manuscripts, in early Hijazi script, suras mapped to folios."},
    {"key": "edda", "prefix": "verified-edda-", "label": "Poetic Edda (Codex Regius)", "group": "Later Traditions", "date_sort": 1270,
     "dates": "c. 1270 AD", "language": "Old Norse",
     "critical_edition": "Normalized Old Norse text (Gudni Jonsson); pages mapped from Wimmer and Jonsson 1891", "translator_name": "Benjamin Thorpe (1866)",
     "description": "The mythological poems of the Codex Regius, from the creation of the world to Ragnarok."},
]

REQUIRED_COLLECTION_KEYS = [
    "key", "prefix", "label", "group", "date_sort", "author_name", "source_url",
    "critical_edition", "translator_name", "original_lang_label", "original_lang_code",
]


READY = ROOT / "data" / "collections_ready.txt"


def ready_keys():
    """Keys the integrator has reviewed and released (one per line in data/collections_ready.txt)."""
    if not READY.exists():
        return set()
    return {l.split("#")[0].strip() for l in READY.read_text().splitlines() if l.split("#")[0].strip()}


def load_all(only_ready=True):
    """Return {key: collection_json} for data/collections/*.json (released ones only by default)."""
    out = {}
    if not COLL_DIR.exists():
        return out
    keys = ready_keys() if only_ready else None
    for f in sorted(COLL_DIR.glob("*.json")):
        if keys is not None and f.stem not in keys:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        c = d.get("collection", {})
        out[c.get("key", f.stem)] = d
    return out


def find_for_id(tid, registry=None):
    """Return the collection config whose prefix is the longest match for tid, or None."""
    registry = registry if registry is not None else load_all()
    best = None
    for d in registry.values():
        c = d.get("collection", {})
        p = c.get("prefix", "")
        if p and tid.startswith(p) and (best is None or len(p) > len(best["prefix"])):
            best = c
    return best


def all_collections(texts_rows):
    """Merged list of collection descriptors (registry first, legacy for the rest), each with
    its published rows in reading order. texts_rows = data/texts.json rows."""
    reg = load_all()
    out = []
    used = set()
    for key, d in reg.items():
        c = dict(d["collection"])
        rows = [r for r in texts_rows if r["id"].startswith(c["prefix"]) and r.get("status") == "published"]
        order = {r["id"]: r.get("order", 0) for r in d.get("texts", [])}
        rows.sort(key=lambda r: (order.get(r["id"], 0), r["id"]))
        c["rows"] = rows
        out.append(c)
        used.add(key)
    for c in LEGACY:
        if c["key"] in used:
            continue
        c = dict(c)
        c["rows"] = [r for r in texts_rows if r["id"].startswith(c["prefix"]) and r.get("status") == "published"]
        out.append(c)
    out = [c for c in out if c["rows"]]
    out.sort(key=lambda c: (SHELVES.index(c["group"]) if c["group"] in SHELVES else 99, c.get("date_sort", 0), c["label"]))
    return out
