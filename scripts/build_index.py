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
            "Apostolic": "1st-2nd century",
            "Ante-Nicene": "before 325 AD",
            "Nicene": "325-451 AD",
            "Post-Nicene": "451-800 AD",
            "Byzantine": "800-1453 AD",
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
    # Full list
    items_html = build_filtered_html(era_groups, lambda t: True)

    # First translations only
    first_html = build_filtered_html(era_groups, lambda t: t.get("is_first_translation", False) and t["status"] == "published")

    # Core canon: the irreducible essential texts
    canon_ids = {
        "septuagint-genesis-1", "septuagint-exodus-3", "septuagint-psalm-82",
        "sinaiticus-mark-1", "sinaiticus-matt-5", "sinaiticus-luke-1",
        "sinaiticus-john-1", "sinaiticus-john-10", "sinaiticus-john-17",
        "sinaiticus-2peter-1", "sinaiticus-phil-2-5", "sinaiticus-col-1-15",
        "nicene-creed",
    }
    canon_html = build_filtered_html(era_groups, lambda t: t["id"] in canon_ids and t["status"] == "published")

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

      <div class="library-tabs">
        <button class="library-tab active" onclick="switchView('full', this)">All Texts</button>
        <button class="library-tab" onclick="switchView('first', this)">First Translations</button>
        <button class="library-tab" onclick="switchView('canon', this)">Core Canon</button>
        <button class="library-tab" onclick="switchView('ancient', this)">Most Ancient</button>
      </div>

      {status_line}

      <!-- Full Library view -->
      <div id="view-full" class="library-view">
{items_html}
      </div>

      <!-- Most Ancient timeline view -->
      <div id="view-ancient" class="timeline-view" style="display:none;">
        <div class="timeline">

          <div class="timeline-entry">
            <div class="timeline-entry-img"><img src="/assets/timeline/sumerian-tablet.jpg" alt="Sumerian clay tablet" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 2600 BCE</div>
              <h3>Instructions of Shuruppak</h3>
              <div class="text-meta">Sumerian &middot; Earliest known wisdom literature</div>
              <div class="text-description">One of the oldest surviving literary texts. A father's advice to his son, preserved on clay tablets from ancient Sumer. Predates the Hebrew Bible by over a millennium.</div>
              <div class="timeline-status">Forthcoming</div>
            </div>
          </div>

          <div class="timeline-entry">
            <div class="timeline-entry-img"><img src="/assets/timeline/gilgamesh-tablet.jpg" alt="Gilgamesh flood tablet" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 2100 BCE</div>
              <h3>Epic of Gilgamesh (Standard Version)</h3>
              <div class="text-meta">Akkadian &middot; Mesopotamia</div>
              <div class="text-description">The oldest great work of literature. A king's search for immortality and the meaning of human mortality. Contains the earliest flood narrative, predating Genesis by centuries.</div>
              <div class="timeline-status">Forthcoming</div>
            </div>
          </div>

          <div class="timeline-entry">
            <div class="timeline-entry-img"><img src="/assets/timeline/book-of-dead.jpg" alt="Papyrus of Ani" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 1550 BCE</div>
              <h3>Egyptian Book of the Dead (Papyrus of Ani)</h3>
              <div class="text-meta">Egyptian &middot; Thebes</div>
              <div class="text-description">Spells and instructions for navigating the afterlife. The most complete surviving copy of the funerary texts that shaped Egyptian religion for two millennia.</div>
              <div class="timeline-status">Forthcoming</div>
            </div>
          </div>

          <div class="timeline-entry">
            <div class="timeline-entry-img"><img src="/assets/timeline/septuagint.jpg" alt="Codex Vaticanus" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 250 BCE</div>
              <h3>Septuagint (LXX)</h3>
              <div class="text-meta">Greek &middot; Alexandria</div>
              <div class="text-description">The Greek translation of the Hebrew scriptures, produced in Ptolemaic Alexandria. The Bible of the early Church and the textual basis for most New Testament quotations of the Old.</div>
              <div class="timeline-status">Forthcoming</div>
            </div>
          </div>

          <div class="timeline-entry">
            <div class="timeline-entry-img"><img src="/assets/timeline/codex-sinaiticus.jpg" alt="Codex Sinaiticus" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 50&ndash;120 AD</div>
              <h3>Earliest Gospel Manuscripts</h3>
              <div class="text-meta">Greek &middot; From Codex Sinaiticus (4th c. copy)</div>
              <div class="text-description">The words of Jesus as preserved in the earliest surviving manuscripts. John 1 (the Logos), John 10 ("ye are gods"), 2 Peter 1:4 ("partakers of the divine nature").</div>
              <div class="timeline-status">Forthcoming</div>
            </div>
          </div>

          <div class="timeline-entry">
            <div class="timeline-entry-img"><img src="/assets/timeline/irenaeus.jpg" alt="Irenaeus of Lyon" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 130&ndash;200 AD</div>
              <h3>Irenaeus, Against Heresies</h3>
              <div class="text-meta">Greek/Latin &middot; Lyon</div>
              <div class="text-description">The earliest systematic account of Gnostic theology and its refutation. "God became man so that man might become God."</div>
              <div class="timeline-status">Forthcoming</div>
            </div>
          </div>

          <div class="timeline-entry timeline-entry--published">
            <div class="timeline-entry-img"><img src="/assets/scans/csel38-p20.jpg" alt="CSEL 38" loading="lazy"></div>
            <div class="timeline-content">
              <div class="timeline-date">c. 385 AD</div>
              <h3><a href="/library/filastrius-gnostic-heresies.html">Filastrius, The Gnostic Schools</a></h3>
              <div class="text-meta">Latin &middot; Brescia &middot; <strong>First English translation</strong></div>
              <div class="text-description">Fifteen chapters covering every major Gnostic school: Simonians, Basilideans, Valentinians, Marcosians, Carpocratians, Barbelo-Gnostics. With manuscript scans.</div>
              <div class="timeline-status timeline-status--live">Published &middot; Read now &rarr;</div>
            </div>
          </div>

        </div>
      </div>

      <!-- First Translations view -->
      <div id="view-first" class="library-view" style="display:none;">
        <p class="view-description">Texts appearing in English for the first time. No previous English translation exists for any text in this collection.</p>
{first_html}
      </div>

      <!-- Core Canon view -->
      <div id="view-canon" class="library-view" style="display:none;">
        <p class="view-description">The essential texts of the theosis debate: Church Fathers, Gnostic teachers, and the councils that attempted to settle the question. Includes both new and existing translations.</p>
{canon_html}
      </div>

    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>Theosis Library is a project of <a href="#">Hyperborean Press</a>.</p>
    </div>
  </footer>

  <script type="module" src="../js/search.js"></script>
  <script>
  function switchView(view, btn) {{
    var views = ['full', 'ancient', 'first', 'canon'];
    views.forEach(function(v) {{
      var el = document.getElementById('view-' + v);
      if (el) el.style.display = (v === view) ? '' : 'none';
    }});
    var tabs = document.querySelectorAll('.library-tab');
    for (var i = 0; i < tabs.length; i++) tabs[i].classList.remove('active');
    if (btn) btn.classList.add('active');
    // Update URL without reload
    var url = new URL(window.location);
    if (view === 'full') url.searchParams.delete('view');
    else url.searchParams.set('view', view);
    history.replaceState(null, '', url);
  }}
  // Init from URL
  (function() {{
    var view = new URLSearchParams(window.location.search).get('view') || 'full';
    var tabs = document.querySelectorAll('.library-tab');
    for (var i = 0; i < tabs.length; i++) {{
      if (tabs[i].textContent.toLowerCase().indexOf(view === 'full' ? 'all' : view === 'first' ? 'first' : view === 'canon' ? 'core' : 'ancient') !== -1) {{
        switchView(view, tabs[i]);
      }}
    }}
  }})();
  </script>

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
