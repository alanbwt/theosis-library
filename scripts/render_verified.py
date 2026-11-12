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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collections_lib import find_for_id, load_all  # noqa: E402

REGISTRY = {}

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "texts.json"
PUB = ROOT / "translations" / "published"
LIB = ROOT / "site" / "library"
READING_ORDER = ROOT / "site" / "data" / "reading-order.json"
TEMPLATES = Path(__file__).resolve().parent / "templates"

TRADITION_LABELS = {
    "orthodox": "Christian", "neoplatonist": "Greco-Roman", "greek": "Greek",
    "hindu": "Hindu", "buddhist": "Buddhist", "islamic": "Islamic", "sufi": "Sufi",
    "gnostic": "Gnostic", "hermetic": "Hermetic", "norse": "Norse",
    "egyptian": "Egyptian", "mesopotamian": "Mesopotamian", "zoroastrian": "Zoroastrian",
    "jewish": "Jewish", "canaanite": "Levantine", "persian": "Persian", "taoist": "Taoist",
    "confucian": "Confucian", "chinese": "Chinese", "roman": "Roman", "sumerian": "Sumerian",
    "vedic": "Vedic", "ethiopian": "Ethiopian", "christian": "Christian",
}


# Google Fonts per original-language code (Gentium Plus covers transliterations,
# polytonic Greek and Old Norse; script fonts for everything else).
FONT_FAMILIES = {
    "grc": ["Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "non": ["Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "la": ["Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "akk": ["Gentium+Plus:ital,wght@0,400;0,700;1,400", "Noto+Sans+Cuneiform"],
    "sux": ["Gentium+Plus:ital,wght@0,400;0,700;1,400", "Noto+Sans+Cuneiform"],
    "egy": ["Gentium+Plus:ital,wght@0,400;0,700;1,400", "Noto+Sans+Egyptian+Hieroglyphs"],
    "peo": ["Gentium+Plus:ital,wght@0,400;0,700;1,400", "Noto+Sans+Old+Persian"],
    "ae": ["Gentium+Plus:ital,wght@0,400;0,700;1,400", "Noto+Sans+Avestan"],
    "sa": ["Gentium+Plus:ital,wght@0,400;0,700;1,400", "Noto+Serif+Devanagari:wght@400;700"],
    "lzh": ["Noto+Serif+TC:wght@400;700"],
    "och": ["Noto+Serif+TC:wght@400;700"],
    "gez": ["Noto+Serif+Ethiopic:wght@400;700", "Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "cop": ["Noto+Sans+Coptic", "Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "hbo": ["Noto+Serif+Hebrew:wght@400;700", "Noto+Sans+Phoenician"],
    "he": ["Noto+Serif+Hebrew:wght@400;700"],
    "arc": ["Noto+Serif+Hebrew:wght@400;700", "Noto+Sans+Imperial+Aramaic"],
    "obm": ["Noto+Sans+Phoenician", "Noto+Serif+Hebrew:wght@400;700", "Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "phn": ["Noto+Sans+Phoenician", "Noto+Serif+Hebrew:wght@400;700", "Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "uga": ["Noto+Sans+Ugaritic", "Gentium+Plus:ital,wght@0,400;0,700;1,400"],
    "ar": ["Amiri:ital,wght@0,400;0,700;1,400"],
}
# Tradition banners: new traditions borrow the closest existing banner art.
HERO_ALIAS = {"sumerian": "mesopotamian", "vedic": "hindu", "christian": "orthodox", "roman": "greek"}


def font_link_for(code):
    fams = FONT_FAMILIES.get(code)
    if not fams:
        return ""
    return "https://fonts.googleapis.com/css2?" + "&".join(f"family={f}" for f in fams) + "&display=swap"


def host_label(url):
    from urllib.parse import urlparse
    try:
        h = urlparse(url).netloc
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return url


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

    reading_order = {}
    if READING_ORDER.exists():
        reading_order = json.loads(READING_ORDER.read_text(encoding="utf-8"))

    global REGISTRY
    REGISTRY = load_all()
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
            if s.get("edition_text"):
                s["edition_text"] = wrap_paragraphs(s["edition_text"])
            if s.get("scan_pages"):
                has_scans = True
            else:
                s["scan_pages"] = []

        tradition = meta.get("tradition", "")
        slug = meta.get("slug", tid)

        # Source labeling per manuscript prefix. Each branch sets:
        #   author_name       — manuscript + its date
        #   source_url        — canonical external home for the manuscript
        #   critical_edition  — which scholarly edition produced the original text
        #   translator_name   — who produced the English (public-domain)
        #   original_lang_label / original_lang_code — label + BCP-47 for the
        #     left reading column (drives typography and column header).
        coll = find_for_id(tid, REGISTRY)
        edition_label = "Tischendorf 8th edition (1869)"
        if coll:
            author_name = coll["author_name"]
            source_url = coll["source_url"]
            critical_edition = coll["critical_edition"]
            translator_name = coll["translator_name"]
            original_lang_label = coll["original_lang_label"]
            original_lang_code = coll["original_lang_code"]
            edition_label = coll.get("edition_label") or "Edition text"
        elif tid.startswith("verified-edda-"):
            author_name = "Anonymous (Codex Regius, c. 1270)"
            source_url = "https://handrit.is/manuscript/view/is/GKS04-2365"
            critical_edition = "Codex Regius (GKS 2365 4to)"
            translator_name = "Benjamin Thorpe (1866)"
            original_lang_label = "Old Norse · heimskringla.no"
            original_lang_code = "non"
        elif tid.startswith("verified-venetus-"):
            author_name = "Homer (Venetus A, 10th c.)"
            source_url = "https://www.homermultitext.org/"
            critical_edition = "Munro & Allen (Perseus Digital Library)"
            translator_name = "Samuel Butler (1898)"
            original_lang_label = "Greek · Munro & Allen"
            original_lang_code = "grc"
        elif tid.startswith("verified-vaticanus-"):
            author_name = "Codex Vaticanus (4th c., Vatican Library)"
            source_url = "https://digi.vatlib.it/view/MSS_Vat.gr.1209"
            critical_edition = "Tischendorf 8th edition (1869)"
            translator_name = "King James Version (1611)"
            original_lang_label = "Greek · Tischendorf 8"
            original_lang_code = "grc"
        elif tid.startswith("verified-bezae-"):
            author_name = "Codex Bezae (5th c., Cambridge UL)"
            source_url = "https://cudl.lib.cam.ac.uk/view/MS-NN-00002-00041/"
            critical_edition = "Tischendorf 8th edition (1869)"
            translator_name = "King James Version (1611)"
            original_lang_label = "Greek · Tischendorf 8"
            original_lang_code = "grc"
        elif tid.startswith("verified-1qisaa-"):
            author_name = "Great Isaiah Scroll, 1QIsa-a (c. 125 BCE, Israel Museum)"
            source_url = "https://www.imj.org.il/en/collections/199976"
            critical_edition = "ETCBC Dead Sea Scrolls transcription (Abegg data, CC BY-NC 4.0)"
            translator_name = "King James Version (1611)"
            original_lang_label = "Hebrew · 1QIsa-a transcription"
            original_lang_code = "hbo"
        elif tid.startswith("verified-leningrad-"):
            author_name = "Leningrad Codex, Firkovich B19a (1008 AD, National Library of Russia)"
            source_url = "https://archive.org/details/Leningrad_Codex_Color_Images"
            critical_edition = "Unicode/XML Leningrad Codex (tanach.us), transcription of this manuscript"
            translator_name = "King James Version (1611)"
            original_lang_label = "Hebrew · Leningrad Codex (UXLC)"
            original_lang_code = "hbo"
        elif tid.startswith("verified-parisino-petropolitanus-"):
            author_name = "Codex Parisino-petropolitanus, BnF Arabe 328 (7th-8th c.)"
            source_url = "https://gallica.bnf.fr/ark:/12148/btv1b8415207g"
            critical_edition = "Tanzil Uthmani text (CC BY 3.0); folio mapping Corpus Coranicum"
            translator_name = "Marmaduke Pickthall (1930)"
            original_lang_label = "Arabic · Tanzil Uthmani"
            original_lang_code = "ar"
        elif tid.startswith("verified-gilgamesh-"):
            author_name = "Epic of Gilgamesh, Nineveh tablets (7th c. BCE, British Museum)"
            source_url = "https://www.ebl.lmu.de/"
            critical_edition = "Electronic Babylonian Library manuscript transliteration (CC BY-NC-SA 4.0)"
            translator_name = "R. Campbell Thompson (1928)"
            original_lang_label = "Akkadian · eBL transliteration"
            original_lang_code = "akk"
        elif tid.startswith("verified-alexandrinus-"):
            author_name = "Codex Alexandrinus (5th c., British Library)"
            source_url = "https://www.bl.uk/manuscripts/FullDisplay.aspx?ref=Royal_MS_1_D_VIII"
            critical_edition = "Tischendorf 8th edition (1869)"
            translator_name = "King James Version (1611)"
            original_lang_label = "Greek · Tischendorf 8"
            original_lang_code = "grc"
        elif tid.startswith("verified-dss-"):
            author_name = "Dead Sea Scrolls (Great Isaiah Scroll, c. 125 BCE)"
            source_url = "https://www.imj.org.il/en/collections/199976"
            critical_edition = "Westminster Leningrad Codex (Groves Center)"
            translator_name = "King James Version (1611)"
            original_lang_label = "Hebrew · WLC"
            original_lang_code = "hbo"
        elif tid.startswith("verified-josephus-"):
            author_name = "Flavius Josephus (c. 93/94 AD; Vatican manuscripts 10th-14th c.)"
            source_url = "https://digi.vatlib.it/view/MSS_Vat.gr.984"
            critical_edition = "Niese, Flavii Iosephi opera (1885-1890), via Perseus"
            translator_name = "William Whiston (1737)"
            original_lang_label = "Greek · Niese"
            original_lang_code = "grc"
        elif tid.startswith("verified-washingtonianus-"):
            author_name = "Codex Washingtonianus (4th-5th c., Freer Gallery)"
            source_url = "https://www.si.edu/object/fsg_F1906.274"
            critical_edition = "Tischendorf 8th edition (1869)"
            translator_name = "King James Version (1611)"
            original_lang_label = "Greek · Tischendorf 8"
            original_lang_code = "grc"
        else:
            # Default: Codex Sinaiticus (both NT and LXX chapters)
            author_name = "Codex Sinaiticus (4th c.) — biblical authors"
            source_url = "https://codexsinaiticus.org/"
            critical_edition = "Tischendorf 8th edition (1869) / Codex Sinaiticus transcription"
            translator_name = "King James Version (1611)"
            # OT side uses the CSP verbatim transcription, NT side uses Tischendorf.
            is_ot = meta.get("era") == "Old Testament"
            uses_csp = is_ot or pub.get("verification", {}).get("primary_greek") == "csp_transcription"
            original_lang_label = "Greek · Codex Sinaiticus transcription" if uses_csp else "Greek · Tischendorf 8"
            original_lang_code = "grc"

        translator_name = pub.get("verification", {}).get("translator") or translator_name
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
            translator_name=translator_name,
            original_lang_label=original_lang_label,
            edition_label=edition_label,
            original_lang_code=original_lang_code,
            reading=reading_order.get(tid, {}),
            verification=pub.get("verification", {}),
            font_link=font_link_for(original_lang_code),
            hero_tradition=HERO_ALIAS.get(tradition, tradition),
            collection_url=f"/collections/{reading_order.get(tid, {}).get('manuscript', '')}" if reading_order.get(tid) else "/library/",
            source_url_label=host_label(source_url),
            edition_lang=(coll.get("edition_lang") if coll else None) or ("grc" if original_lang_code in ("grc",) or not coll else original_lang_code),
        )

        out = LIB / f"{slug}.html"
        out.write_text(html, encoding="utf-8")
        rendered += 1

    print(f"Rendered: {rendered}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
