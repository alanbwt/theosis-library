#!/usr/bin/env python3
"""
publish.py — Convert a reviewed translation JSON into an HTML page.

Usage:
    python scripts/publish.py <text-id>

Reads from translations/reviewed/<text-id>.json and outputs to site/library/<slug>.html.
"""

import argparse
import json
import os
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
TEMPLATES_DIR = PROJECT_ROOT / "scripts" / "templates"

# Create templates directory if needed
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

TRANSLATION_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }} &mdash; Theosis Library</title>
  <meta name="description" content="{{ description }}">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

  <header class="site-header">
    <div class="container--wide">
      <div class="site-title"><a href="/">Theosis Library</a></div>
      <nav class="site-nav">
        <a href="/library/">Library</a>
        <a href="/sources/">Sources</a>
        <a href="/about.html">About</a>
      </nav>
    </div>
  </header>

  <main>
    <div class="container">

      <div class="translation-header">
        <h1>{{ title }}</h1>
        <div class="original-title">{{ original_title }}</div>
        <div class="author">{{ author }}, {{ author_dates }}</div>
        <div class="source">{{ source }}{% if critical_edition %} &middot; {{ critical_edition }}{% endif %}</div>
      </div>

      <section class="introduction">
        <h2>Introduction</h2>
        {{ introduction }}
      </section>

    </div>

    {% if has_parallel %}
    <div class="container--parallel">

      {% if source_url %}
      <div class="source-link-banner">
        Verify this translation: <a href="{{ source_url }}" target="_blank" rel="noopener">view the original {{ language }} text &rarr;</a>
      </div>
      {% endif %}

      <div class="parallel-controls">
        <span>{{ language }} original &amp; English translation, section-aligned. Read side by side or toggle view.</span>
        <div class="view-toggle">
          <button class="active" onclick="setView('parallel', this)">Parallel</button>
          <button onclick="setView('translation-only', this)">English only</button>
          <button onclick="setView('original-only', this)">{{ language }} only</button>
        </div>
      </div>

      <section class="translation-body" id="translation-body">
        {% for section in translation %}
        <div class="parallel-section" id="section-{{ section.section | replace('.', '-') }}">
          <span class="section-ref">&sect;{{ section.section }}{% if section.original_ref %} &middot; {{ section.original_ref }}{% endif %}</span>
          <div class="parallel-original">
            <div class="parallel-col-label">{{ language }}</div>
            {{ section.original_text }}
          </div>
          <div class="parallel-translation">
            <div class="parallel-col-label">English</div>
            {{ section.text }}
          </div>
        </div>
        {% endfor %}
      </section>

    </div>
    {% else %}
    <div class="container">
      <section class="translation-body">
        <h2>Translation</h2>
        {% for section in translation %}
        <div class="section-block" id="section-{{ section.section | replace('.', '-') }}">
          <span class="section-ref">&sect;{{ section.section }}{% if section.original_ref %} &middot; {{ section.original_ref }}{% endif %}</span>
          {{ section.text }}
        </div>
        {% endfor %}
      </section>
    </div>
    {% endif %}

    <div class="container">

      {% if translator_notes %}
      <section class="notes-section">
        <h2>Translator&rsquo;s Notes</h2>
        <ol class="notes-list">
          {% for note in translator_notes %}
          <li id="note-{{ loop.index }}">
            <strong>&sect;{{ note.ref }}:</strong> {{ note.note }}
          </li>
          {% endfor %}
        </ol>
      </section>
      {% endif %}

      <section class="source-section">
        <h2>Source &amp; Cross-References</h2>
        <ul>
          <li><strong>Source text:</strong> {{ source }}{% if source_url %} &mdash; <a href="{{ source_url }}" target="_blank" rel="noopener">view original</a>{% endif %}</li>
          {% if critical_edition %}<li><strong>Critical edition:</strong> {{ critical_edition }}</li>{% endif %}
          {% for ref in related_texts %}
          <li><a href="/library/{{ ref.slug }}.html">{{ ref.title }}</a> by {{ ref.author }}</li>
          {% endfor %}
        </ul>
      </section>

    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>Translated by Matt Mattimore. AI-assisted draft reviewed against the {{ language }} text of
        {% if 'Patrologia Graeca' in source %}Migne&rsquo;s <em>Patrologia Graeca</em>{% elif 'Patrologia Latina' in source %}Migne&rsquo;s <em>Patrologia Latina</em>{% else %}the source edition{% endif %}.</p>
      <p>Published {{ pub_date }} &middot; License: <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></p>
      <p style="margin-top: 1rem;">Theosis Library is a project of Hyperborean Press.</p>
    </div>
  </footer>

  <script>
  function setView(mode, btn) {
    var body = document.getElementById('translation-body');
    if (!body) return;
    body.className = 'translation-body';
    if (mode !== 'parallel') body.classList.add('view-' + mode);
    var btns = btn.parentElement.querySelectorAll('button');
    for (var i = 0; i < btns.length; i++) btns[i].classList.remove('active');
    btn.classList.add('active');
  }
  </script>

</body>
</html>
"""


def load_texts():
    with open(DATA_DIR / "texts.json") as f:
        return json.load(f)


def save_texts(data):
    with open(DATA_DIR / "texts.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_text(texts_data, text_id):
    for text in texts_data["texts"]:
        if text["id"] == text_id:
            return text
    return None


def get_related_texts(texts_data, text_meta):
    related = []
    for rid in text_meta.get("related_texts", []):
        rt = find_text(texts_data, rid)
        if rt and rt["status"] == "published":
            related.append(rt)
    return related


def wrap_paragraphs(text):
    """Convert plain text paragraphs to HTML <p> tags."""
    if "<p>" in text:
        return text  # Already HTML
    paragraphs = text.strip().split("\n\n")
    return "\n".join(f"        <p>{p.strip()}</p>" for p in paragraphs if p.strip())


def publish(text_id):
    reviewed_path = REVIEWED_DIR / f"{text_id}.json"
    if not reviewed_path.exists():
        print(f"Error: reviewed translation not found at {reviewed_path}")
        sys.exit(1)

    with open(reviewed_path, encoding="utf-8") as f:
        reviewed = json.load(f)

    texts_data = load_texts()
    text_meta = find_text(texts_data, text_id)
    if not text_meta:
        print(f"Error: text ID '{text_id}' not found in texts.json")
        sys.exit(1)

    # Extract translation data
    content = reviewed.get("draft", reviewed)
    introduction = wrap_paragraphs(content.get("introduction", ""))
    translation = content.get("translation", [])
    translator_notes = content.get("translator_notes", [])

    # Wrap translation section text and original text in paragraphs if needed
    has_parallel = False
    for section in translation:
        section["text"] = wrap_paragraphs(section["text"])
        if section.get("original_text"):
            has_parallel = True
            section["original_text"] = wrap_paragraphs(section["original_text"])
        else:
            section["original_text"] = ""

    related = get_related_texts(texts_data, text_meta)

    # Render template
    env = Environment(loader=FileSystemLoader("/"), autoescape=False)
    template = env.from_string(TRANSLATION_TEMPLATE)

    html = template.render(
        title=text_meta["title"],
        original_title=text_meta["original_title"],
        author=text_meta["author"],
        author_dates=text_meta["author_dates"],
        source=text_meta["source"],
        source_url=text_meta.get("source_url", ""),
        critical_edition=text_meta.get("critical_edition", ""),
        language=text_meta["language"],
        description=text_meta["description"],
        introduction=introduction,
        translation=translation,
        translator_notes=translator_notes,
        related_texts=related,
        pub_date=str(date.today()),
        has_parallel=has_parallel,
    )

    # Write HTML to site
    slug = text_meta["slug"]
    output_path = SITE_LIBRARY_DIR / f"{slug}.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Published to {output_path}")

    # Copy to published directory
    published_path = PUBLISHED_DIR / f"{text_id}.json"
    with open(published_path, "w", encoding="utf-8") as f:
        json.dump(reviewed, f, indent=2, ensure_ascii=False)

    # Update texts.json
    text_meta["status"] = "published"
    text_meta["date_published"] = str(date.today())
    save_texts(texts_data)
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
