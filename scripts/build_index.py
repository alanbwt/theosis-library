#!/usr/bin/env python3
"""
build_index.py — Rebuild the library index page and search index.

Usage:
    python scripts/build_index.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SITE_DIR = PROJECT_ROOT / "site"
LIBRARY_DIR = SITE_DIR / "library"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_authors(texts_data, authors_data):
    """Join author info into each text record."""
    author_map = {a["id"]: a for a in authors_data["authors"]}
    for text in texts_data["texts"]:
        author = author_map.get(text.get("author_id", ""), {})
        text["author_name"] = author.get("name", "Unknown")
        text["author_dates"] = author.get("dates", "")
        text["author_tradition"] = author.get("tradition", "")


def group_by_era(texts):
    era_order = ["Apostolic", "Ante-Nicene", "Nicene", "Post-Nicene", "Byzantine"]
    groups = {}
    for text in texts:
        era = text.get("era", "Unknown")
        if era not in groups:
            groups[era] = []
        groups[era].append(text)

    for era in groups:
        groups[era].sort(key=lambda t: (t.get("century", 0), t.get("author_name", "")))

    ordered = []
    for era in era_order:
        if era in groups:
            ordered.append((era, groups[era]))
    for era in groups:
        if era not in era_order:
            ordered.append((era, groups[era]))

    return ordered


def render_text_item(text):
    status_class = f"status-badge--{text['status']}"
    themes_html = "".join(f"<span>{t}</span>" for t in text.get("themes", []))

    first_badge = ""
    if text.get("is_first_translation") and text["status"] == "published":
        first_badge = ' <span class="status-badge status-badge--first">first translation</span>'

    link_start = ""
    link_end = ""
    if text["status"] == "published":
        link_start = f'<a href="/library/{text["slug"]}.html">'
        link_end = "</a>"

    tradition = text.get("tradition", "")
    category = text.get("category", "")

    return f"""          <li class="text-item" data-themes="{' '.join(text.get('themes', []))}" data-author="{text['author_name']}" data-title="{text['title']}" data-tradition="{tradition}" data-category="{category}">
            <h3>{link_start}{text['title']}{link_end} <span class="status-badge {status_class}">{text['status']}</span>{first_badge}</h3>
            <div class="text-meta">{text['author_name']} &middot; {text['author_dates']} &middot; {text['language']}</div>
            <div class="text-description">{text['description']}</div>
            <div class="text-themes">{themes_html}</div>
          </li>"""


def build_library_page(era_groups):
    items_html = ""
    for era, texts in era_groups:
        era_range = {
            "Apostolic": "1st-2nd century",
            "Ante-Nicene": "before 325 AD",
            "Nicene": "325-451 AD",
            "Post-Nicene": "451-800 AD",
            "Byzantine": "800-1453 AD",
        }.get(era, "")

        items = "\n".join(render_text_item(t) for t in texts)
        items_html += f"""
      <div class="era-group">
        <div class="era-label">{era} ({era_range})</div>
        <ul class="text-list">
{items}
        </ul>
      </div>
"""

    published_count = sum(
        1 for _, texts in era_groups for t in texts if t["status"] == "published"
    )
    total_count = sum(len(texts) for _, texts in era_groups)

    if published_count > 0:
        status_line = f'<p style="color: #999; font-size: 0.9rem;">{published_count} published translation{"s" if published_count != 1 else ""} &middot; {total_count} texts in catalog</p>'
    else:
        status_line = '<p style="color: #999; font-style: italic;">Published translations will appear here as they are completed.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Library — Theosis Library</title>
  <meta name="description" content="Browse all translations of early Christian texts in the Theosis Library.">
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

      <h1>Library</h1>

      <div class="search-container">
        <input type="text" class="search-input" id="search-input" placeholder="Search translations by author, title, or theme...">
        <div class="search-results-info" id="search-results-info"></div>
      </div>

      {status_line}
{items_html}
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>Theosis Library is a project of Hyperborean Press.</p>
    </div>
  </footer>

  <script src="../js/search.js"></script>

</body>
</html>"""


def build_search_index(texts):
    """Build a JSON search index for published texts with passage-level content."""
    index = []
    for text in texts:
        entry = {
            "id": text["id"],
            "title": text["title"],
            "author": text.get("author_name", ""),
            "author_dates": text.get("author_dates", ""),
            "description": text["description"],
            "themes": text.get("themes", []),
            "slug": text["slug"],
            "status": text["status"],
            "era": text.get("era", ""),
            "tradition": text.get("tradition", ""),
            "category": text.get("category", ""),
            "is_first_translation": text.get("is_first_translation", False),
        }

        if text["status"] == "published":
            published_path = (
                PROJECT_ROOT / "translations" / "published" / f"{text['id']}.json"
            )
            if published_path.exists():
                pub_data = load_json(published_path)
                content = pub_data.get("draft", pub_data)
                sections = content.get("translation", [])
                entry["content"] = " ".join(s.get("text", "") for s in sections)

        index.append(entry)

    return index


def main():
    texts_data = load_json(DATA_DIR / "texts.json")
    authors_data = load_json(DATA_DIR / "authors.json")
    resolve_authors(texts_data, authors_data)

    all_texts = texts_data["texts"]
    era_groups = group_by_era(all_texts)

    # Rebuild library index page
    html = build_library_page(era_groups)
    output_path = LIBRARY_DIR / "index.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Library index rebuilt: {output_path}")

    # Rebuild search index
    search_index = build_search_index(all_texts)
    search_path = SITE_DIR / "search-index.json"
    with open(search_path, "w", encoding="utf-8") as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)
    print(f"Search index rebuilt: {search_path}")

    published = [t for t in all_texts if t["status"] == "published"]
    print(f"Total texts: {len(all_texts)} | Published: {len(published)}")


if __name__ == "__main__":
    main()
