#!/usr/bin/env python3
"""
export_epub.py — Generate EPUB files for published translations.

Usage:
    python scripts/export_epub.py [text-id]
    python scripts/export_epub.py --all
"""

import argparse
import json
import re
import zipfile
from datetime import date
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PUBLISHED_DIR = PROJECT_ROOT / "translations" / "published"
EPUB_DIR = PROJECT_ROOT / "site" / "downloads"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def strip_tags(html):
    return re.sub(r"<[^>]+>", "", html or "")


def wrap_p(text):
    if not text:
        return ""
    if "<p>" in text:
        return text
    return "\n".join(f"<p>{p.strip()}</p>" for p in text.strip().split("\n\n") if p.strip())


def generate_epub(text_id):
    texts = load_json(DATA_DIR / "texts.json")
    authors = load_json(DATA_DIR / "authors.json")
    author_map = {a["id"]: a for a in authors["authors"]}

    text_meta = None
    for t in texts["texts"]:
        if t["id"] == text_id:
            text_meta = t
            break

    if not text_meta or text_meta["status"] != "published":
        print(f"Skipping {text_id}: not published")
        return

    pub_path = PUBLISHED_DIR / f"{text_id}.json"
    if not pub_path.exists():
        return

    reviewed = load_json(pub_path)
    content = reviewed.get("draft", reviewed)
    author = author_map.get(text_meta.get("author_id", ""), {})
    author_name = author.get("name", "Unknown")

    title = text_meta["title"]
    lang = text_meta["language"]
    uid = str(uuid4())
    today = str(date.today())
    slug = text_meta["slug"]

    # Build XHTML content
    sections_html = ""
    for section in content.get("translation", []):
        orig = wrap_p(section.get("original_text", ""))
        trans = wrap_p(section.get("text", ""))
        ref = section.get("original_ref", "")

        sections_html += f"""
    <div class="section">
      <h3>§{section["section"]}{f" · {ref}" if ref else ""}</h3>
      <div class="parallel">
        <div class="col-orig">
          <div class="label">{lang}</div>
          {orig}
        </div>
        <div class="col-en">
          <div class="label">English</div>
          {trans}
        </div>
      </div>
    </div>"""

    notes_html = ""
    for note in content.get("translator_notes", []):
        notes_html += f'<p><strong>§{note["ref"]}:</strong> {note["note"]}</p>\n'

    content_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <title>{title}</title>
  <style>
    body {{ font-family: Georgia, serif; line-height: 1.6; margin: 1em; color: #222; }}
    h1 {{ font-size: 1.4em; margin-bottom: 0.25em; }}
    h2 {{ font-size: 1.1em; margin-top: 1.5em; color: #555; }}
    h3 {{ font-size: 0.9em; color: #888; margin-top: 1.5em; margin-bottom: 0.5em; }}
    .subtitle {{ font-style: italic; color: #666; }}
    .meta {{ font-size: 0.8em; color: #888; margin-bottom: 1em; }}
    .section {{ margin-bottom: 1.5em; }}
    .parallel {{ display: flex; gap: 1em; }}
    .col-orig {{ flex: 1; font-size: 0.9em; color: #444; }}
    .col-en {{ flex: 1; }}
    .label {{ font-size: 0.7em; text-transform: uppercase; letter-spacing: 0.08em; color: #8b7355; margin-bottom: 0.3em; }}
    .notes {{ margin-top: 2em; border-top: 1px solid #ddd; padding-top: 1em; font-size: 0.9em; }}
    .notes p {{ margin-bottom: 0.5em; color: #555; }}
    .footer {{ margin-top: 2em; font-size: 0.8em; color: #999; border-top: 1px solid #ddd; padding-top: 1em; }}
    em {{ font-style: italic; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="subtitle">{text_meta["original_title"]}</div>
  <div class="meta">{author_name} · {text_meta.get("date_approx", "")} · Translated by Alan B.</div>

  {wrap_p(content.get("introduction", ""))}

  {sections_html}

  {"<div class='notes'><h2>Translator's Notes</h2>" + notes_html + "</div>" if notes_html else ""}

  <div class="footer">
    <p>Theosis Library · theosislibrary.com · {today}</p>
    <p>License: Creative Commons BY-SA 4.0</p>
  </div>
</body>
</html>"""

    # Build EPUB (which is a zip file with specific structure)
    EPUB_DIR.mkdir(parents=True, exist_ok=True)
    epub_path = EPUB_DIR / f"{slug}.epub"

    with zipfile.ZipFile(str(epub_path), "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be first and uncompressed
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # Container
        zf.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""")

        # OPF
        zf.writestr("content.opf", f"""<?xml version="1.0" encoding="UTF-8"?>
<package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:{uid}</dc:identifier>
    <dc:title>{title}</dc:title>
    <dc:creator>Alan B.</dc:creator>
    <dc:language>en</dc:language>
    <dc:publisher>Theosis Library / Hyperborean Press</dc:publisher>
    <dc:date>{today}</dc:date>
    <dc:rights>Creative Commons BY-SA 4.0</dc:rights>
    <meta property="dcterms:modified">{today}T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>""")

        # Navigation
        zf.writestr("nav.xhtml", f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Navigation</title></head>
<body>
  <nav epub:type="toc">
    <h1>Contents</h1>
    <ol><li><a href="content.xhtml">{title}</a></li></ol>
  </nav>
</body>
</html>""")

        # Content
        zf.writestr("content.xhtml", content_xhtml)

    print(f"  {slug}.epub ({epub_path.stat().st_size // 1024}KB)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text_id", nargs="?")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        texts = load_json(DATA_DIR / "texts.json")
        for t in texts["texts"]:
            if t["status"] == "published":
                generate_epub(t["id"])
    elif args.text_id:
        generate_epub(args.text_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
