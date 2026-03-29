#!/usr/bin/env python3
"""
export_pdf.py — Generate downloadable PDFs for published translations.

Usage:
    python scripts/export_pdf.py [text-id]     # specific text
    python scripts/export_pdf.py --all          # all published texts
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
PUBLISHED_DIR = PROJECT_ROOT / "translations" / "published"
PDF_OUTPUT_DIR = PROJECT_ROOT / "site" / "downloads"

PDF_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@page { size: A4; margin: 2.5cm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.6; color: #222; }
h1 { font-size: 18pt; margin-bottom: 4pt; }
h2 { font-size: 13pt; margin-top: 24pt; margin-bottom: 8pt; color: #555; }
.subtitle { font-style: italic; color: #666; font-size: 12pt; margin-bottom: 4pt; }
.meta { font-family: Helvetica, Arial, sans-serif; font-size: 8.5pt; color: #888; margin-bottom: 16pt; }
.intro { margin-bottom: 24pt; }
.section { margin-bottom: 20pt; page-break-inside: avoid; }
.section-ref { font-family: Helvetica, Arial, sans-serif; font-size: 8pt; color: #999; margin-bottom: 4pt; }
.parallel { display: table; width: 100%; border-collapse: collapse; margin-bottom: 12pt; }
.col { display: table-cell; width: 50%; padding: 8pt; vertical-align: top; }
.col-label { font-family: Helvetica, Arial, sans-serif; font-size: 7.5pt; text-transform: uppercase; letter-spacing: 0.08em; color: #8b7355; margin-bottom: 4pt; }
.col-original { font-size: 10pt; color: #444; }
.col-english { font-size: 10.5pt; }
.notes { margin-top: 24pt; border-top: 1px solid #ddd; padding-top: 16pt; }
.note { font-size: 9.5pt; margin-bottom: 8pt; color: #555; }
.note strong { color: #333; }
.footer { margin-top: 32pt; border-top: 1px solid #ddd; padding-top: 12pt; font-family: Helvetica, Arial, sans-serif; font-size: 8pt; color: #999; }
.citation { font-size: 8.5pt; color: #666; background: #f8f6f2; padding: 8pt; border-radius: 3px; margin-top: 8pt; }
em { font-style: italic; }
</style>
</head>
<body>

<h1>{{ title }}</h1>
<div class="subtitle">{{ original_title }}</div>
<div class="meta">{{ author_name }}, {{ author_dates }} · {{ source }} · Translated by Alan B.</div>

<div class="intro">
{{ introduction }}
</div>

{% for section in translation %}
<div class="section">
  <div class="section-ref">§{{ section.section }}{% if section.original_ref %} · {{ section.original_ref }}{% endif %}</div>
  <div class="parallel">
    <div class="col">
      <div class="col-label">{{ language }}</div>
      <div class="col-original">{{ section.original_text }}</div>
    </div>
    <div class="col">
      <div class="col-label">English</div>
      <div class="col-english">{{ section.text }}</div>
    </div>
  </div>
</div>
{% endfor %}

{% if translator_notes %}
<div class="notes">
<h2>Translator's Notes</h2>
{% for note in translator_notes %}
<div class="note"><strong>§{{ note.ref }}:</strong> {{ note.note }}</div>
{% endfor %}
</div>
{% endif %}

<div class="footer">
  <p>Theosis Library · theosislibrary.com · {{ pub_date }}</p>
  <p>License: Creative Commons BY-SA 4.0</p>
  <div class="citation">
    <strong>Cite as:</strong> {{ author_name }}, <em>{{ original_title }}</em>, trans. Alan B., Theosis Library ({{ pub_year }}), https://theosislibrary.com/library/{{ slug }}.html
  </div>
</div>

</body>
</html>
"""


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def wrap_paragraphs(text):
    if not text:
        return ""
    if "<p>" in text:
        return text
    paragraphs = text.strip().split("\n\n")
    return "\n".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())


def generate_pdf(text_id):
    try:
        from weasyprint import HTML
    except ImportError:
        print("weasyprint not installed. Generating HTML-only PDF source.")
        HTML = None

    texts = load_json(DATA_DIR / "texts.json")
    authors = load_json(DATA_DIR / "authors.json")
    author_map = {a["id"]: a for a in authors["authors"]}

    text_meta = None
    for t in texts["texts"]:
        if t["id"] == text_id:
            text_meta = t
            break

    if not text_meta:
        print(f"Text '{text_id}' not found")
        return

    if text_meta["status"] != "published":
        print(f"Text '{text_id}' not published yet")
        return

    reviewed_path = PUBLISHED_DIR / f"{text_id}.json"
    if not reviewed_path.exists():
        print(f"Published file not found for '{text_id}'")
        return

    reviewed = load_json(reviewed_path)
    content = reviewed.get("draft", reviewed)
    author = author_map.get(text_meta.get("author_id", ""), {})

    translation = content.get("translation", [])
    for section in translation:
        section["text"] = wrap_paragraphs(section.get("text", ""))
        section["original_text"] = wrap_paragraphs(section.get("original_text", ""))

    env = Environment(loader=FileSystemLoader("/"), autoescape=False)
    template = env.from_string(PDF_TEMPLATE)

    today = date.today()
    html_content = template.render(
        title=text_meta["title"],
        original_title=text_meta["original_title"],
        author_name=author.get("name", "Unknown"),
        author_dates=author.get("dates", ""),
        source=text_meta["source"],
        language=text_meta["language"],
        introduction=wrap_paragraphs(content.get("introduction", "")),
        translation=translation,
        translator_notes=content.get("translator_notes", []),
        slug=text_meta["slug"],
        pub_date=str(today),
        pub_year=str(today.year),
    )

    PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = text_meta["slug"]

    if HTML:
        pdf_path = PDF_OUTPUT_DIR / f"{slug}.pdf"
        HTML(string=html_content).write_pdf(str(pdf_path))
        print(f"PDF: {pdf_path}")
    else:
        html_path = PDF_OUTPUT_DIR / f"{slug}-print.html"
        html_path.write_text(html_content, encoding="utf-8")
        print(f"HTML (for manual PDF): {html_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text_id", nargs="?", help="Text ID to export")
    parser.add_argument("--all", action="store_true", help="Export all published texts")
    args = parser.parse_args()

    if args.all:
        texts = load_json(DATA_DIR / "texts.json")
        for t in texts["texts"]:
            if t["status"] == "published":
                generate_pdf(t["id"])
    elif args.text_id:
        generate_pdf(args.text_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
