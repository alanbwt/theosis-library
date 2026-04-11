#!/usr/bin/env python3
"""
build_quotes.py — Rebuild the quotes page from data/quotes.json.

Generates a data-driven quotes page with filters for tradition, topic, era,
and theosis position. Enriches existing quotes with tradition/era/topic fields
on first run if missing.

Usage:
    python scripts/build_quotes.py
"""

import json
import re
from pathlib import Path
from html import escape

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / "data" / "quotes.json"
OUT = PROJECT_ROOT / "site" / "quotes" / "index.html"

# category → tradition mapping
CATEGORY_TO_TRADITION = {
    "scripture": "christian",
    "patristic": "christian",
    "gnostic": "gnostic",
    "ancient-near-east": "mesopotamian",
    "hindu": "hindu",
    "buddhist": "buddhist",
    "sufi": "sufi",
    "islamic": "islamic",
    "neoplatonist": "greek",
    "norse": "norse",
    "taoist": "taoist",
}

TRADITION_LABELS = {
    "christian": "Christian",
    "gnostic": "Gnostic",
    "greek": "Greek/Roman",
    "hindu": "Hindu",
    "buddhist": "Buddhist",
    "sufi": "Sufi",
    "islamic": "Islamic",
    "norse": "Norse",
    "taoist": "Taoist",
    "mesopotamian": "Mesopotamian",
    "egyptian": "Egyptian",
    "celtic": "Celtic",
    "zoroastrian": "Zoroastrian",
}

TOPIC_LABELS = {
    "divinity": "Divinity",
    "soul": "Soul",
    "creation": "Creation",
    "afterlife": "Afterlife",
    "ethics": "Ethics",
    "knowledge": "Knowledge",
    "governance": "Governance",
    "suffering": "Suffering",
    "love": "Love",
    "death": "Death",
}


def parse_year(date_str):
    """Extract a signed year from a date_approx like 'c. 200 AD' or '700 BCE'."""
    if not date_str:
        return 0
    s = date_str.lower().replace("c.", "").strip()
    m = re.search(r"(\d+)\s*(bce|bc)", s)
    if m:
        return -int(m.group(1))
    m = re.search(r"(\d+)\s*(ad|ce)", s)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)(?:st|nd|rd|th)\s*c", s)
    if m:
        century = int(m.group(1))
        return century * 100 - 50 if "bce" in s or "bc" in s else century * 100 - 50
    return 0


def derive_era(year):
    if year <= -1000:
        return "Bronze Age"
    if year <= -500:
        return "Iron Age"
    if year <= 0:
        return "Classical"
    if year <= 300:
        return "Imperial"
    if year <= 600:
        return "Late Antiquity"
    if year <= 1500:
        return "Medieval"
    return "Early Modern"


def enrich(quotes):
    """Add tradition/era fields if missing. Topic must be set explicitly per quote."""
    for q in quotes:
        if "tradition" not in q:
            q["tradition"] = CATEGORY_TO_TRADITION.get(q.get("category", ""), q.get("category", ""))
        if "era" not in q:
            year = parse_year(q.get("date", ""))
            q["era"] = derive_era(year)
        if "topic" not in q:
            # Default theosis quotes to 'divinity'
            q["topic"] = "divinity"
        if "_year" not in q:
            q["_year"] = parse_year(q.get("date", ""))


def render_card(q):
    pos = q.get("position", "")
    pos_label = {
        "for": "For theosis",
        "against": "Against theosis",
        "ambiguous": "Ambiguous",
        "foundational": "Foundational",
    }.get(pos, pos.title())
    pos_class = f"tag-{pos}" if pos else ""

    original = q.get("quote_original", "")
    original_html = (
        f'<blockquote class="quote-original">{escape(original)}</blockquote>'
        if original else ""
    )
    english = escape(q.get("quote_english", ""))
    author = escape(q.get("author", ""))
    date = escape(q.get("date", ""))
    source = escape(q.get("source", ""))
    significance = escape(q.get("significance", ""))
    link = q.get("link", "")
    link_html = (
        f'<a href="{escape(link)}" class="quote-link">Read with manuscript scan →</a>'
        if link else ""
    )

    tradition = q.get("tradition", "")
    topic = q.get("topic", "")
    era = q.get("era", "")

    return f"""        <div class="quote-card" data-position="{pos}" data-tradition="{tradition}" data-topic="{topic}" data-era="{escape(era)}">
          <div class="quote-position-tag {pos_class}">{pos_label}</div>
          {original_html}
          <blockquote class="quote-english">"{english}"</blockquote>
          <div class="quote-meta">
            <span class="quote-author">{author}</span>
            <span class="quote-date">{date}</span>
            <span class="quote-source">{source}</span>
          </div>
          <p class="quote-significance">{significance}</p>
          {link_html}
        </div>"""


def build_page(quotes):
    # Sort chronologically (oldest first)
    quotes_sorted = sorted(quotes, key=lambda q: q.get("_year", 0))

    cards_html = "\n".join(render_card(q) for q in quotes_sorted)

    # Filter chip data
    traditions = sorted({q.get("tradition", "") for q in quotes if q.get("tradition")})
    topics = sorted({q.get("topic", "") for q in quotes if q.get("topic")})
    eras_present = {q.get("era", "") for q in quotes if q.get("era")}
    era_order = ["Bronze Age", "Iron Age", "Classical", "Imperial",
                 "Late Antiquity", "Medieval", "Early Modern"]
    eras = [e for e in era_order if e in eras_present]

    tradition_chips = "\n".join(
        f'        <button class="quotes-filter" data-filter-type="tradition" data-filter-value="{tr}">{TRADITION_LABELS.get(tr, tr.title())}</button>'
        for tr in traditions
    )
    topic_chips = "\n".join(
        f'        <button class="quotes-filter" data-filter-type="topic" data-filter-value="{tp}">{TOPIC_LABELS.get(tp, tp.title())}</button>'
        for tp in topics
    )
    era_chips = "\n".join(
        f'        <button class="quotes-filter" data-filter-type="era" data-filter-value="{escape(er)}">{escape(er)}</button>'
        for er in eras
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Primary Source Quotes — Theosis Library</title>
  <meta name="description" content="The best primary source quotes from every civilization on divinity, soul, creation, afterlife, ethics, knowledge, and governance. Filter by tradition, topic, era, and theosis position.">
  <meta property="og:title" content="The Evidence — Theosis Library">
  <meta property="og:description" content="Primary source quotes from every civilization, with original language and manuscript references.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://theosislibrary.com/quotes/">
  <meta name="twitter:card" content="summary">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/quotes.css">
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
    <div class="container--wide">

      <div class="quotes-header">
        <h1>The Evidence</h1>
        <p class="quotes-subtitle">Primary source quotes from every civilization on the deepest questions: divinity, soul, creation, afterlife, ethics, knowledge. Original language, English translation, manuscript source.</p>
      </div>

      <div class="quotes-filters">
        <div class="quotes-filter-row">
          <span class="quotes-filter-label">Position:</span>
          <button class="quotes-filter active" data-filter-type="position" data-filter-value="all">All</button>
          <button class="quotes-filter" data-filter-type="position" data-filter-value="for">For Theosis</button>
          <button class="quotes-filter" data-filter-type="position" data-filter-value="against">Against</button>
          <button class="quotes-filter" data-filter-type="position" data-filter-value="ambiguous">Ambiguous</button>
        </div>
        <div class="quotes-filter-row">
          <span class="quotes-filter-label">Tradition:</span>
{tradition_chips}
        </div>
        <div class="quotes-filter-row">
          <span class="quotes-filter-label">Topic:</span>
{topic_chips}
        </div>
        <div class="quotes-filter-row">
          <span class="quotes-filter-label">Era:</span>
{era_chips}
        </div>
      </div>

      <section class="quotes-section">
{cards_html}
      </section>

    </div>
  </main>

  <footer class="site-footer">
    <div class="container" style="text-align:center;">
      <img src="/assets/hyperborean-press-logo.webp" alt="Hyperborean Press" style="width:60px;height:auto;opacity:0.4;margin-bottom:0.5rem;">
      <p>&copy; Hyperborean Press 2026</p>
    </div>
  </footer>

  <script>
  var activeFilters = {{ position: 'all', tradition: '', topic: '', era: '' }};

  function applyQuoteFilters() {{
    var cards = document.querySelectorAll('.quote-card');
    cards.forEach(function(c) {{
      var show = true;
      if (activeFilters.position && activeFilters.position !== 'all') {{
        show = show && c.getAttribute('data-position') === activeFilters.position;
      }}
      if (activeFilters.tradition) {{
        show = show && c.getAttribute('data-tradition') === activeFilters.tradition;
      }}
      if (activeFilters.topic) {{
        show = show && c.getAttribute('data-topic') === activeFilters.topic;
      }}
      if (activeFilters.era) {{
        show = show && c.getAttribute('data-era') === activeFilters.era;
      }}
      c.style.display = show ? '' : 'none';
    }});
  }}

  document.querySelectorAll('.quotes-filter').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      var type = btn.getAttribute('data-filter-type');
      var value = btn.getAttribute('data-filter-value');
      // Toggle: clicking active filter clears it
      if (activeFilters[type] === value) {{
        activeFilters[type] = type === 'position' ? 'all' : '';
        btn.classList.remove('active');
        if (type === 'position') {{
          document.querySelector('.quotes-filter[data-filter-type="position"][data-filter-value="all"]').classList.add('active');
        }}
      }} else {{
        activeFilters[type] = value;
        document.querySelectorAll('.quotes-filter[data-filter-type="' + type + '"]').forEach(function(b) {{
          b.classList.remove('active');
        }});
        btn.classList.add('active');
      }}
      applyQuoteFilters();
    }});
  }});
  </script>

<script src="../js/decode.js"></script>
<script src="../js/columns.js"></script>
</body>
</html>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    quotes = data["quotes"]
    enrich(quotes)

    # Persist enriched data (strip private _year)
    persistable = []
    for q in quotes:
        clean = {k: v for k, v in q.items() if not k.startswith("_")}
        persistable.append(clean)
    DATA.write_text(json.dumps({"quotes": persistable}, indent=2, ensure_ascii=False), encoding="utf-8")

    html = build_page(quotes)
    OUT.write_text(html, encoding="utf-8")
    print(f"Quotes page rebuilt: {OUT}  ({len(quotes)} quotes)")


if __name__ == "__main__":
    main()
