#!/usr/bin/env python3
"""build_quotes.py — Rebuild `/quotes/` as a curated "Key Passages" landing page.

Previous incarnation was a heavy filter UI over 20 hand-picked verses, framed as
"quotes from every civilization" — which misrepresented the actual library
(~6 manuscripts, 3 traditions). This rebuild drops the filter chrome and
organizes the same 20 passages by position on the theosis question, so the page
matches what the library actually delivers: a compact evidence compass.

Each passage links to the full library entry (with manuscript scan).
"""

import json
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / "data" / "quotes.json"
OUT = PROJECT_ROOT / "site" / "quotes" / "index.html"

POSITION_SECTIONS = [
    (
        "foundational",
        "Foundational",
        "The texts every subsequent argument refers to.",
    ),
    (
        "for",
        "For theosis",
        "Passages read as affirming some form of human participation in the divine nature.",
    ),
    (
        "against",
        "Against theosis",
        "Passages read as ruling out any real human participation in the divine nature.",
    ),
    (
        "ambiguous",
        "Ambiguous",
        "Passages that can be read either way. Included so the reader can decide.",
    ),
]


def canonical_library_href(link: str | None) -> str:
    if not link:
        return ""
    # Previous build used `.html` suffixes; strip so it lands on the clean URL.
    return link.replace(".html", "") if link.startswith("/library/") else link


def render_quote(q: dict) -> str:
    original = q.get("quote_original") or ""
    english = q.get("quote_english") or ""
    source = q.get("source") or ""
    author = q.get("author") or ""
    date = q.get("date") or ""
    manuscript = q.get("manuscript") or ""
    significance = q.get("significance") or ""
    href = canonical_library_href(q.get("link"))

    original_block = (
        f'<blockquote class="passage-original" lang="{escape(q.get("language","").lower()[:3] or "grc")}">{escape(original)}</blockquote>'
        if original else ""
    )
    english_block = (
        f'<blockquote class="passage-english">“{escape(english)}”</blockquote>'
    )
    significance_block = (
        f'<p class="passage-note">{escape(significance)}</p>' if significance else ""
    )
    link_block = (
        f'<a class="passage-link" href="{escape(href)}">Read with manuscript scan →</a>'
        if href else ""
    )
    meta_parts = []
    if source:
        meta_parts.append(f'<span class="passage-source">{escape(source)}</span>')
    if manuscript:
        meta_parts.append(f'<span class="passage-manuscript">{escape(manuscript)}</span>')
    if date:
        meta_parts.append(f'<span class="passage-date">{escape(date)}</span>')
    meta_block = (
        f'<div class="passage-meta">{" · ".join(meta_parts)}</div>' if meta_parts else ""
    )

    return f"""        <article class="passage-card" data-position="{escape(q.get("position",""))}">
          {original_block}
          {english_block}
          {meta_block}
          {significance_block}
          {link_block}
        </article>"""


def build():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    quotes = data.get("quotes", [])

    section_html = []
    for key, title, blurb in POSITION_SECTIONS:
        items = [q for q in quotes if q.get("position") == key]
        if not items:
            continue
        cards = "\n".join(render_quote(q) for q in items)
        section_html.append(
            f"""      <section class="passages-section">
        <header class="passages-section-header">
          <h2>{escape(title)}</h2>
          <p class="passages-section-blurb">{escape(blurb)}</p>
        </header>
        <div class="passages-grid">
{cards}
        </div>
      </section>"""
        )
    sections_html = "\n\n".join(section_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Key Passages — Theosis Library</title>
  <meta name="description" content="A compass through the verified library: the passages most often cited for, against, or ambiguous on the question of human participation in the divine nature. Each links to the full manuscript page.">
  <link rel="canonical" href="https://theosislibrary.com/quotes/">
  <meta property="og:title" content="Key Passages — Theosis Library">
  <meta property="og:description" content="The passages most often cited on the theosis question — arranged by position, each linked to the full verified chapter with manuscript scan.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://theosislibrary.com/quotes/">
  <meta property="og:image" content="https://theosislibrary.com/assets/scans/sinaiticus-folios/john-1-Q80_1r_B521.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Key Passages — Theosis Library">
  <meta name="twitter:description" content="The passages most often cited on the theosis question, linked to the full manuscript page.">
  <meta name="twitter:image" content="https://theosislibrary.com/assets/scans/sinaiticus-folios/john-1-Q80_1r_B521.jpg">
  <link rel="stylesheet" href="../css/style.css">
<meta name="generator" content="Noble Growth (https://noblegrowth.co)">
<link rel="author" href="https://noblegrowth.co/">
<link rel="author" type="text/plain" href="/humans.txt">
</head>
<body>

  <header class="site-header">
    <div class="container--wide">
      <div class="site-title"><a href="/">Theosis Library</a></div>
      <nav class="site-nav">
        <a href="/">Home</a>
        <a href="/library/">Library</a>
        <a href="/paths/">Paths</a>
        <a href="/quotes/">Passages</a>
        <a href="/sources/">Sources</a>
        <a href="/about">About</a>
      </nav>
    </div>
  </header>

  <main>
    <div class="container--wide">

      <div class="passages-header">
        <h1>Key Passages</h1>
        <p class="passages-subtitle">A compass through the verified library. These are the passages most often invoked in the debate over whether human beings can participate in the divine nature. Arranged by the position each tends to anchor. Every line links to the full chapter with the manuscript scan.</p>
      </div>

{sections_html}

      <div class="passages-footer">
        <p>Want a guided tour? Read a <a href="/paths/">reading path</a>. Want to judge for yourself? Browse the <a href="/library/">full library</a> of {len(quotes)} curated passages drawn from {len(set(q.get("manuscript","") for q in quotes if q.get("manuscript")))} manuscripts.</p>
      </div>

    </div>
  </main>

  <footer class="site-footer">
    <div class="container" style="text-align:center;">
      <img src="/assets/hyperborean-press-logo.webp" alt="Hyperborean Press" style="width:60px;height:auto;opacity:0.4;margin-bottom:0.5rem;">
      <p>&copy; Hyperborean Press 2026</p>
      <p class="ng-credit" style="font-size:11px;opacity:.55;margin:.5rem 0 0"><a href="https://noblegrowth.co" rel="author" style="color:inherit;text-decoration:none">Built by Noble Growth</a></p>
    </div>
  </footer>

</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Key Passages page rebuilt: {OUT}  ({len(quotes)} passages)")


if __name__ == "__main__":
    build()
