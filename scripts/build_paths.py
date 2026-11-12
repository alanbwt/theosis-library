#!/usr/bin/env python3
"""
build_paths.py — reading paths from data/paths.json.

Each path is a short guided sequence of library sections. Every step links to a real
entry and section anchor; the build fails if an entry or section does not exist.

data/paths.json:
{"paths": [{"slug": "flood", "card_label": "8 steps · Mesopotamia to Genesis",
            "title": "...", "description": "...",
            "steps": [{"id": "verified-...", "section": "XI 1-20", "meta": "c. 1200 BCE · Akkadian",
                       "heading": "...", "note": "..."}]}]}

Writes site/paths/<slug>.html and the cards between PATHS:CARDS markers in site/paths/index.html.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SITE = ROOT / "site"
e = html.escape


def anchor(section):
    return "s" + str(section).replace(".", "-").replace(" ", "-")


def page(p, steps_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(p['title'])} | Theosis Library</title>
  <meta name="description" content="{e(p['description'])}">
  <meta property="og:title" content="{e(p['title'])} | Reading Path">
  <meta property="og:description" content="{e(p['description'])}">
  <meta property="og:type" content="article">
  <link rel="canonical" href="https://theosislibrary.com/paths/{p['slug']}">
  <link rel="stylesheet" href="/css/style.css">
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
    <div class="container">

      <div class="path-header">
        <div class="path-label">Reading Path</div>
        <h1>{e(p['title'])}</h1>
        <p class="path-description">{e(p['description'])}</p>
      </div>

      <ol class="path-list">
{steps_html}
      </ol>

      <div style="text-align: center; margin-top: 2.5rem;">
        <a href="/paths/" class="browse-link">More reading paths</a>
        <span style="margin: 0 0.5rem; color: #b0a28c;">·</span>
        <a href="/library/" class="browse-link">The library</a>
      </div>

    </div>
  </main>

  <footer class="site-footer">
    <div class="container" style="text-align:center;">
      <img src="/assets/hyperborean-press-logo.webp" alt="Hyperborean Press" style="width:60px;height:auto;opacity:0.4;margin-bottom:0.5rem;">
      <p>&copy; Hyperborean Press 2026</p>
      <p class="ng-credit">Built by <a href="https://noblegrowth.co" rel="author">Noble Growth</a></p>
    </div>
  </footer>
</body>
</html>
"""


def main():
    cfg = json.loads((ROOT / "data" / "paths.json").read_text(encoding="utf-8"))
    errors, cards = [], []
    for p in cfg["paths"]:
        steps = []
        for i, st in enumerate(p["steps"], 1):
            pf = PUB / f"{st['id']}.json"
            if not pf.exists():
                errors.append(f"{p['slug']} step {i}: no entry {st['id']}")
                continue
            secs = {str(s["section"]) for s in json.loads(pf.read_text(encoding="utf-8"))["translation"]}
            href = f"/library/{st['id']}"
            if st.get("section") is not None:
                if str(st["section"]) not in secs:
                    errors.append(f"{p['slug']} step {i}: {st['id']} has no section {st['section']!r}")
                href += "#" + anchor(st["section"])
            steps.append(f"""        <li class="path-step">
          <div class="path-number">{i}</div>
          <div class="path-content">
            <div class="path-meta">{e(st['meta'])}</div>
            <h3><a href="{href}">{e(st['heading'])}</a></h3>
            <p>{e(st['note'])}</p>
          </div>
        </li>""")
        (SITE / "paths" / f"{p['slug']}.html").write_text(page(p, "\n\n".join(steps)), encoding="utf-8")
        cards.append(f"""        <a href="/paths/{p['slug']}" class="paths-card">
          <div class="paths-card-label">{e(p['card_label'])}</div>
          <h3>{e(p['title'])}</h3>
          <p>{e(p['description'])}</p>
        </a>""")
    idx = SITE / "paths" / "index.html"
    s = idx.read_text(encoding="utf-8")
    block = "<!-- PATHS:CARDS START -->\n" + "\n\n".join(cards) + "\n<!-- PATHS:CARDS END -->"
    if "<!-- PATHS:CARDS START -->" in s:
        s = re.sub(r"<!-- PATHS:CARDS START -->.*?<!-- PATHS:CARDS END -->", lambda m: block, s, flags=re.S)
    else:
        s = s.replace('<div class="paths-grid">', '<div class="paths-grid">\n' + block, 1)
    idx.write_text(s, encoding="utf-8")
    for x in errors:
        print("FAIL", x)
    print(f"paths: {len(cfg['paths'])} built, {len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
