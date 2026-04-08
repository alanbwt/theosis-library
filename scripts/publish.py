#!/usr/bin/env python3
"""
publish.py — Convert a reviewed translation JSON into an HTML page.

Usage:
    python scripts/publish.py <text-id>
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REVIEWED_DIR = PROJECT_ROOT / "translations" / "reviewed"
PUBLISHED_DIR = PROJECT_ROOT / "translations" / "published"
SITE_LIBRARY_DIR = PROJECT_ROOT / "site" / "library"
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_text(texts_data, text_id):
    for text in texts_data["texts"]:
        if text["id"] == text_id:
            return text
    return None


def find_author(authors_data, author_id):
    for author in authors_data["authors"]:
        if author["id"] == author_id:
            return author
    return None


def get_related_texts(texts_data, authors_data, text_meta):
    related = []
    for rid in text_meta.get("related_texts", []):
        rt = find_text(texts_data, rid)
        if rt and rt["status"] == "published":
            author = find_author(authors_data, rt.get("author_id", ""))
            rt_copy = dict(rt)
            rt_copy["author_name"] = author["name"] if author else rt.get("author", "Unknown")
            related.append(rt_copy)
    return related


def wrap_paragraphs(text):
    """Convert plain text paragraphs to HTML <p> tags."""
    if not text:
        return ""
    if "<p>" in text:
        return text
    paragraphs = text.strip().split("\n\n")
    return "\n".join(f"        <p>{p.strip()}</p>" for p in paragraphs if p.strip())


def publish(text_id):
    reviewed_path = REVIEWED_DIR / f"{text_id}.json"
    if not reviewed_path.exists():
        print(f"Error: reviewed translation not found at {reviewed_path}")
        sys.exit(1)

    reviewed = load_json(reviewed_path)
    texts_data = load_json(DATA_DIR / "texts.json")
    authors_data = load_json(DATA_DIR / "authors.json")

    text_meta = find_text(texts_data, text_id)
    if not text_meta:
        print(f"Error: text ID '{text_id}' not found in texts.json")
        sys.exit(1)

    author = find_author(authors_data, text_meta.get("author_id", ""))
    author_name = author["name"] if author else "Unknown"
    author_dates = author["dates"] if author else ""

    # Extract translation data
    content = reviewed.get("draft", reviewed)
    introduction = wrap_paragraphs(content.get("introduction", ""))
    translation = content.get("translation", [])
    translator_notes = content.get("translator_notes", [])

    # Process sections
    has_parallel = False
    has_scans = False
    for section in translation:
        section["text"] = wrap_paragraphs(section.get("text", ""))
        if section.get("original_text"):
            has_parallel = True
            section["original_text"] = wrap_paragraphs(section["original_text"])
        else:
            section["original_text"] = ""
        if section.get("scan_pages"):
            has_scans = True
        else:
            section["scan_pages"] = []

    related = get_related_texts(texts_data, authors_data, text_meta)

    # Render template
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    template = env.get_template("translation.html")

    tradition_labels = {
        "orthodox": "Christian", "neoplatonist": "Greco-Roman", "greek": "Greek",
        "hindu": "Hindu", "buddhist": "Buddhist", "islamic": "Islamic", "sufi": "Sufi",
        "gnostic": "Gnostic", "hermetic": "Hermetic", "norse": "Norse",
        "egyptian": "Egyptian", "mesopotamian": "Mesopotamian", "zoroastrian": "Zoroastrian",
        "taoist": "Taoist", "confucian": "Confucian", "celtic": "Celtic",
        "japanese": "Japanese", "tibetan": "Tibetan", "mesoamerican": "Mesoamerican",
        "ethiopian": "Ethiopian", "african": "African", "slavic": "Slavic",
        "persian": "Persian", "jain": "Jain", "canaanite": "Canaanite",
        "korean": "Korean", "southeast-asian": "Southeast Asian", "finnish": "Finnish",
        "chinese": "Chinese", "jewish": "Jewish",
    }
    tradition = text_meta.get("tradition", "")

    today = date.today()
    html = template.render(
        title=text_meta["title"],
        original_title=text_meta["original_title"],
        author_name=author_name,
        author_dates=author_dates,
        source=text_meta["source"],
        source_url=text_meta.get("source_url", ""),
        critical_edition=text_meta.get("critical_edition", ""),
        language=text_meta["language"],
        description=text_meta["description"],
        is_first_translation=text_meta.get("is_first_translation", False),
        introduction=introduction,
        translation=translation,
        translator_notes=translator_notes,
        related_texts=related,
        has_parallel=has_parallel,
        has_scans=has_scans,
        slug=text_meta["slug"],
        pub_date=str(today),
        pub_year=str(today.year),
        tradition=tradition,
        tradition_label=tradition_labels.get(tradition, tradition.title()),
    )

    # Write HTML
    slug = text_meta["slug"]
    output_path = SITE_LIBRARY_DIR / f"{slug}.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Published to {output_path}")

    # Copy to published directory
    published_path = PUBLISHED_DIR / f"{text_id}.json"
    save_json(published_path, reviewed)

    # Update texts.json
    text_meta["status"] = "published"
    text_meta["date_published"] = str(today)
    save_json(DATA_DIR / "texts.json", texts_data)
    print(f"Status updated to 'published' in texts.json")

    # Rebuild index
    print("Rebuilding library index...")
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "build_index.py")],
        check=True,
    )

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish a reviewed translation as HTML")
    parser.add_argument("text_id", help="Text ID from texts.json")
    args = parser.parse_args()
    publish(args.text_id)
