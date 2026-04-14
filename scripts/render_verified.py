#!/usr/bin/env python3
"""
render_verified.py — Render HTML pages for all verified entries.

Reads each translations/published/verified-*.json + the matching texts.json
metadata, and writes site/library/<slug>.html using the translation template.
"""

import json
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "texts.json"
PUB = ROOT / "translations" / "published"
LIB = ROOT / "site" / "library"
TEMPLATES = Path(__file__).resolve().parent / "templates"

TRADITION_LABELS = {
    "orthodox": "Christian", "neoplatonist": "Greco-Roman", "greek": "Greek",
    "hindu": "Hindu", "buddhist": "Buddhist", "islamic": "Islamic", "sufi": "Sufi",
    "gnostic": "Gnostic", "hermetic": "Hermetic", "norse": "Norse",
    "egyptian": "Egyptian", "mesopotamian": "Mesopotamian", "zoroastrian": "Zoroastrian",
}


def wrap_paragraphs(text):
    if not text:
        return ""
    if "<p>" in text:
        return text
    paragraphs = text.strip().split("\n\n")
    return "\n".join(f"        <p>{p.strip()}</p>" for p in paragraphs if p.strip())


def main():
    texts = json.loads(DATA.read_text(encoding="utf-8"))["texts"]
    by_id = {t["id"]: t for t in texts}

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)
    template = env.get_template("translation.html")

    today = date.today()
    rendered = 0
    skipped = 0

    for tid, meta in by_id.items():
        if not tid.startswith("verified-"):
            continue
        pub_path = PUB / f"{tid}.json"
        if not pub_path.exists():
            print(f"  skip {tid}: no published JSON")
            skipped += 1
            continue
        pub = json.loads(pub_path.read_text(encoding="utf-8"))

        introduction = wrap_paragraphs(pub.get("introduction", ""))
        translation = pub.get("translation", [])
        translator_notes = pub.get("translator_notes", [])

        has_parallel = False
        has_scans = False
        for s in translation:
            s["text"] = wrap_paragraphs(s.get("text", ""))
            if s.get("original_text"):
                has_parallel = True
                s["original_text"] = wrap_paragraphs(s["original_text"])
            else:
                s["original_text"] = ""
            if s.get("scan_pages"):
                has_scans = True
            else:
                s["scan_pages"] = []

        tradition = meta.get("tradition", "")
        slug = meta.get("slug", tid)

        # Source labeling per tradition
        if tid.startswith("verified-edda-"):
            author_name = "Anonymous (Codex Regius, 13th c.)"
            source_url = "https://handrit.is/manuscript/view/is/GKS04-2365"
            critical_edition = "Codex Regius (GKS 2365 4to)"
        elif tid.startswith("verified-leningrad-"):
            author_name = "Hebrew Bible (Codex Leningradensis, 1008 AD)"
            source_url = "https://archive.org/details/Leningrad_Codex"
            critical_edition = "Westminster Leningrad Codex (Groves Center)"
        elif tid.startswith("verified-amiatinus-"):
            author_name = "Latin Vulgate (Codex Amiatinus, c. 700 AD)"
            source_url = "https://archive.org/details/codex-amiatinua"
            critical_edition = "Latin Vulgate (Jerome, late 4th c.)"
        elif tid.startswith("verified-venetus-"):
            author_name = "Homer (Venetus A, 10th c.)"
            source_url = "https://www.homermultitext.org/"
            critical_edition = "Munro & Allen (Perseus Digital Library)"
        elif tid.startswith("verified-odyssey-"):
            author_name = "Homer (Hayman 1866 Greek edition)"
            source_url = "https://archive.org/details/odysseyofhome01home"
            critical_edition = "Munro & Allen (Perseus Digital Library)"
        elif tid.startswith("verified-gilgamesh-"):
            author_name = "Sin-leqi-unninni (attributed)"
            source_url = "https://cdli.earth/"
            critical_edition = "Stephen Langdon (1917)"
        elif tid.startswith("verified-aeneid-"):
            author_name = "Virgil (Vergilius Vaticanus, 4th-5th c.)"
            source_url = "https://digi.vatlib.it/view/MSS_Vat.lat.3225"
            critical_edition = "Greenough edition (Perseus Digital Library)"
        elif tid.startswith("verified-bookdead-"):
            author_name = "Ancient Egyptian Scribes (Papyrus of Ani, c. 1250 BCE)"
            source_url = "https://archive.org/details/papyrusofanirepr01budg"
            critical_edition = "E.A. Wallis Budge (1895/1913)"
        elif tid.startswith("verified-hammurabi"):
            author_name = "King Hammurabi of Babylon (c. 1754 BCE)"
            source_url = "https://avalon.law.yale.edu/ancient/hamframe.asp"
            critical_edition = "L.W. King (1910)"
        elif tid.startswith("verified-rigveda-"):
            author_name = "Vedic Rishis (c. 1500-1200 BCE)"
            source_url = "https://archive.org/details/rigvedasanhitasa03syaauoft"
            critical_edition = "Max Müller editio princeps (1849)"
        elif tid.startswith("verified-plato-"):
            author_name = "Plato (c. 428-348 BCE)"
            source_url = "https://www.perseus.tufts.edu/hopper/"
            critical_edition = "Perseus Digital Library"
        elif tid.startswith("verified-vaticanus-"):
            author_name = "Codex Vaticanus (4th c., Vatican Library)"
            source_url = "https://digi.vatlib.it/view/MSS_Vat.gr.1209"
            critical_edition = "Tischendorf 8th edition (NT) / KJV (OT)"
        elif tid.startswith("verified-alexandrinus-"):
            author_name = "Codex Alexandrinus (5th c., British Library)"
            source_url = "https://archive.org/details/codex-alexandrinus"
            critical_edition = "Tischendorf 8th edition (NT) / KJV (OT)"
        elif tid.startswith("verified-dss-"):
            author_name = "Dead Sea Scrolls (c. 2nd c. BCE - 1st c. CE)"
            source_url = "https://en.wikipedia.org/wiki/Great_Isaiah_Scroll"
            critical_edition = "Westminster Leningrad Codex (Hebrew)"
        else:
            author_name = "Codex Sinaiticus (4th c.) — biblical authors"
            source_url = "https://codexsinaiticus.org/"
            critical_edition = "Tischendorf 8th edition (1869) / Codex Sinaiticus transcription"

        html = template.render(
            title=pub.get("title", meta.get("title", tid)),
            original_title=pub.get("title", ""),
            author_name=author_name,
            author_dates="",
            source=pub.get("source", meta.get("source", "")),
            source_url=source_url,
            critical_edition=critical_edition,
            language=pub.get("language", meta.get("language", "")),
            description=pub.get("description", meta.get("description", "")),
            is_first_translation=False,
            introduction=introduction,
            translation=translation,
            translator_notes=translator_notes,
            related_texts=[],
            has_parallel=has_parallel,
            has_scans=has_scans,
            slug=slug,
            pub_date=str(today),
            pub_year=str(today.year),
            tradition=tradition,
            scan_thumb=translation[0].get("scan_pages", [""])[0] if translation else "",
            tradition_label=TRADITION_LABELS.get(tradition, tradition.title()),
        )

        out = LIB / f"{slug}.html"
        out.write_text(html, encoding="utf-8")
        rendered += 1

    print(f"Rendered: {rendered}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
