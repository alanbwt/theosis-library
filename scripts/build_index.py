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


def sort_chronologically(texts):
    """Sort texts by date, oldest first. Returns flat list."""
    def sort_key(t):
        # Parse century or date_approx for sorting
        century = t.get("century", 0)
        date_str = t.get("date_approx", "")
        # Try to extract a year from date_approx
        import re
        match = re.search(r'(\d+)\s*(BCE|BC)', date_str)
        if match:
            return -int(match.group(1))
        match = re.search(r'(\d+)\s*(AD|CE)', date_str)
        if match:
            return int(match.group(1))
        # Fall back to century
        if century < 0:
            return century * 100
        return century * 100
    return sorted(texts, key=sort_key)


def group_by_era(texts):
    era_order = [
        "Ancient Near East", "Vedic", "Upanishadic", "Hebrew Bible",
        "Axial Age", "Pre-Socratic", "Classical", "Hellenistic",
        "Second Temple", "Late Republic", "Ancient",
        "Apostolic", "Imperial", "Late Antiquity",
        "Ante-Nicene", "Nicene", "Post-Nicene",
        "Byzantine", "Tang Dynasty", "Song Dynasty",
        "Abbasid", "Early Islamic",
        "Medieval", "Viking Age",
        "Reformation", "Modern"
    ]
    groups = {}
    for text in texts:
        era = text.get("era", "Unknown")
        if era not in groups:
            groups[era] = []
        groups[era].append(text)

    for era in groups:
        groups[era] = sort_chronologically(groups[era])

    ordered = []
    for era in era_order:
        if era in groups:
            ordered.append((era, groups[era]))
    for era in groups:
        if era not in era_order:
            ordered.append((era, groups[era]))

    return ordered


def get_scan_thumb(text):
    """Get the first scan image path for a text."""
    scans = text.get("scans", {})
    if scans and scans.get("pages"):
        return scans["pages"][0].get("file", "")
    return ""


def render_text_card(text):
    """Render a visual card with scan thumbnail."""
    scan = get_scan_thumb(text)
    scan_html = ""
    if scan and text["status"] == "published":
        scan_html = f'<div class="lib-card-scan"><img src="/assets/scans/{scan}" alt="" loading="lazy"></div>'

    first_badge = ""
    if text.get("is_first_translation") and text["status"] == "published":
        first_badge = '<span class="lib-card-badge">First Translation</span>'

    tradition = text.get("tradition", "")
    category = text.get("category", "")
    themes = " ".join(text.get("themes", []))

    if text["status"] == "published":
        href = f'/library/{text["slug"]}.html'
        return f"""<a href="{href}" class="lib-card" data-themes="{themes}" data-author="{text['author_name']}" data-title="{text['title']}" data-tradition="{tradition}" data-category="{category}">
            {scan_html}
            <div class="lib-card-body">
              {first_badge}
              <div class="lib-card-title">{text['title']}</div>
              <div class="lib-card-meta">{text['author_name']} &middot; {text.get('date_approx', '')} &middot; {text['language']}</div>
            </div>
          </a>"""
    else:
        return f"""<div class="lib-card lib-card--queued" data-themes="{themes}" data-author="{text['author_name']}" data-title="{text['title']}" data-tradition="{tradition}" data-category="{category}">
            <div class="lib-card-body">
              <div class="lib-card-title">{text['title']}</div>
              <div class="lib-card-meta">{text['author_name']} &middot; {text.get('date_approx', '')} &middot; Forthcoming</div>
            </div>
          </div>"""


def render_text_item(text):
    """Legacy list item (kept for compatibility)."""
    return render_text_card(text)


def build_filtered_html(era_groups, filter_fn):
    """Build card grid HTML for texts matching a filter function."""
    html = ""
    for era, texts in era_groups:
        filtered = [t for t in texts if filter_fn(t)]
        if not filtered:
            continue
        era_range = {
            "Ancient Near East": "3000-500 BCE",
            "Vedic": "1500-800 BCE",
            "Upanishadic": "800-200 BCE",
            "Hebrew Bible": "1200-200 BCE",
            "Axial Age": "800-200 BCE",
            "Pre-Socratic": "600-400 BCE",
            "Classical": "500-300 BCE",
            "Hellenistic": "300-30 BCE",
            "Second Temple": "200 BCE-70 AD",
            "Late Republic": "100-27 BCE",
            "Ancient": "before 500 BCE",
            "Epic": "400 BCE-200 AD",
            "Apostolic": "30-150 AD",
            "Imperial": "27 BCE-284 AD",
            "Late Antiquity": "200-600 AD",
            "Ante-Nicene": "100-325 AD",
            "Nicene": "325-451 AD",
            "Post-Nicene": "451-800 AD",
            "Byzantine": "330-1453 AD",
            "Abbasid": "750-1258 AD",
            "Early Islamic": "610-750 AD",
            "Tang Dynasty": "618-907 AD",
            "Song Dynasty": "960-1279 AD",
            "Viking Age": "793-1066 AD",
            "Medieval": "500-1500 AD",
            "Reformation": "1500-1650 AD",
            "Modern": "1650-present",
        }.get(era, "")
        items = "\n".join(render_text_card(t) for t in filtered)
        html += f"""
      <div class="era-group">
        <div class="era-label">{era} ({era_range})</div>
        <div class="lib-card-grid">
{items}
        </div>
      </div>
"""
    return html if html.strip() else '<p style="color:#8a7e6f;font-style:italic;padding:2rem 0;">No texts in this category yet.</p>'


def build_library_page(era_groups):
    # Single unified chronological view with data attributes for filtering
    items_html = build_filtered_html(era_groups, lambda t: True)

    published_count = sum(
        1 for _, texts in era_groups for t in texts if t["status"] == "published"
    )
    first_count = sum(
        1 for _, texts in era_groups for t in texts if t.get("is_first_translation") and t["status"] == "published"
    )
    total_count = sum(len(texts) for _, texts in era_groups)

    # Collect unique traditions for filter chips
    # Exclude 'jewish' — Hebrew Bible / Second Temple texts are part of the Christian tradition on this site
    traditions = set()
    for _, texts in era_groups:
        for t in texts:
            if t.get("tradition") and t["status"] == "published" and t["tradition"] != "jewish":
                traditions.add(t["tradition"])
    tradition_labels = {
        "orthodox": "Christian",
        "neoplatonist": "Greek / Roman",
        "greek": "Greek",
        "hindu": "Hindu",
        "buddhist": "Buddhist",
        "islamic": "Islamic",
        "sufi": "Sufi",
        "gnostic": "Gnostic",
        "hermetic": "Hermetic",
        "norse": "Norse",
        "egyptian": "Egyptian",
        "mesopotamian": "Mesopotamian",
        "zoroastrian": "Zoroastrian",
        "taoist": "Taoist",
        "confucian": "Confucian",
    }
    tradition_chips = "\n".join(
        f'        <button class="filter-chip" onclick="toggleFilter(\'tradition\', \'{tr}\', this)">{tradition_labels.get(tr, tr.title())}</button>'
        for tr in sorted(traditions)
    )

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
        <a href="/">Home</a>
        <a href="/library/">Library</a>
        <a href="/quotes/">Quotes</a>
      </nav>
    </div>
  </header>

  <main>
    <div class="container">

      <h1>Library</h1>

      <div class="search-container">
        <input type="text" class="search-input" id="search-input" placeholder="Search by author, title, theme, or keyword in English, Greek, or Latin...">
        <div class="search-results-info" id="search-results-info"></div>
      </div>

      <div class="filter-chips-wrap">
        <button class="filter-chip active" onclick="clearFilters(this)">All ({published_count})</button>
        <button class="filter-chip" onclick="toggleFilter('first', 'true', this)">First Translations ({first_count})</button>
        <button class="filter-chip" onclick="toggleFilter('canon', 'true', this)">Core Canon</button>
{tradition_chips}
      </div>

      <p style="color: #8a7e6f; font-size: 0.8rem; margin-bottom: 1.5rem;">{published_count} texts &middot; Oldest first</p>

      <div id="search-results"></div>

{items_html}

    </div>
  </main>

  <footer class="site-footer">
    <div class="container" style="text-align:center;">
      <img src="../assets/hyperborean-press-logo.webp" alt="Hyperborean Press" style="width:60px;height:auto;opacity:0.4;margin-bottom:0.5rem;">
      <p>&copy; Hyperborean Press 2026</p>
    </div>
  </footer>

  <script type="module" src="../js/search.js"></script>
  <script>
  var activeFilters = {{}};
  var canonIds = new Set(['septuagint-genesis-1','septuagint-exodus-3','septuagint-psalm-82','sinaiticus-mark-1','sinaiticus-matt-5','sinaiticus-luke-1','sinaiticus-john-1','sinaiticus-john-10','sinaiticus-john-17','sinaiticus-2peter-1','sinaiticus-phil-2-5','sinaiticus-col-1-15','nicene-creed']);

  function toggleFilter(type, value, btn) {{
    document.querySelectorAll('.filter-chip').forEach(function(c) {{ c.classList.remove('active'); }});
    btn.classList.add('active');
    activeFilters = {{}};
    activeFilters[type] = value;
    applyFilters();
  }}

  function clearFilters(btn) {{
    activeFilters = {{}};
    document.querySelectorAll('.filter-chip').forEach(function(c) {{ c.classList.remove('active'); }});
    btn.classList.add('active');
    applyFilters();
  }}

  function applyFilters() {{
    var cards = document.querySelectorAll('.lib-card, .lib-card--queued');
    var groups = document.querySelectorAll('.era-group');

    cards.forEach(function(card) {{
      var show = true;
      if (activeFilters.tradition) {{
        show = show && card.getAttribute('data-tradition') === activeFilters.tradition;
      }}
      if (activeFilters.first) {{
        show = show && card.querySelector('.lib-card-badge') !== null;
      }}
      if (activeFilters.canon) {{
        var href = card.getAttribute('href') || '';
        var slug = href.replace('/library/', '').replace('.html', '').split('#')[0];
        show = show && canonIds.has(slug);
      }}
      card.style.display = show ? '' : 'none';
    }});

    groups.forEach(function(g) {{
      var anyVisible = false;
      g.querySelectorAll('.lib-card, .lib-card--queued').forEach(function(c) {{
        if (c.style.display !== 'none') anyVisible = true;
      }});
      g.style.display = anyVisible ? '' : 'none';
    }});
  }}

  // Auto-search from URL ?q= param
  (function() {{
    var q = new URLSearchParams(window.location.search).get('q');
    if (q) {{
      var input = document.getElementById('search-input');
      if (input) {{
        input.value = q;
        input.dispatchEvent(new Event('input'));
      }}
    }}
  }})();
  </script>

<script src="../js/decode.js"></script>
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
