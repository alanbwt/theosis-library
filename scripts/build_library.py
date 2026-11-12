#!/usr/bin/env python3
"""
build_library.py — the library as shelves of collections.

Writes:
  site/library/index.html          shelves (oldest civilisations first), each collection a card
  site/collections/<key>.html      one page per collection, entries in reading order
  site/assets/thumbs/<hash>.jpg    small thumbnails for collection and entry cards

Run after integrate_collections.py and build_reading_order.py.
"""
import hashlib
import html
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collections_lib import ROOT, SHELF_NOTES, SHELVES, all_collections, load_all  # noqa: E402

SITE = ROOT / "site"
SCANS = SITE / "assets" / "scans"
THUMBS = SITE / "assets" / "thumbs"
PUB = ROOT / "translations" / "published"
READING = SITE / "data" / "reading-order.json"
CARD_THUMB_LIMIT = 80  # collections with more entries get a compact list instead of thumbnail cards

e = html.escape


def thumb(scan_rel, width=420):
    """Make (once) a small JPEG thumbnail of a scan; return its site path or ''."""
    if not scan_rel:
        return ""
    src = SCANS / scan_rel
    if not src.exists():
        return ""
    h = hashlib.sha1(f"{scan_rel}:{width}".encode()).hexdigest()[:16]
    out = THUMBS / f"{h}.jpg"
    if not out.exists():
        THUMBS.mkdir(parents=True, exist_ok=True)
        try:
            with Image.open(src) as im:
                im = im.convert("RGB")
                im.thumbnail((width, int(width * 1.5)))
                im.save(out, quality=80, optimize=True)
        except Exception:
            return ""
    return f"/assets/thumbs/{out.name}"


def head(title, desc, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="https://theosislibrary.com{canonical}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="https://theosislibrary.com{canonical}">
  <meta property="og:site_name" content="Theosis Library">
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
"""


FOOT = """
  <footer class="site-footer">
    <div class="container" style="text-align:center;">
      <img src="/assets/hyperborean-press-logo.webp" alt="Hyperborean Press" style="width:60px;height:auto;opacity:0.4;margin-bottom:0.5rem;">
      <p>&copy; Hyperborean Press 2026</p>
      <p class="ng-credit">Built by <a href="https://noblegrowth.co" rel="author">Noble Growth</a></p>
    </div>
  </footer>
"""


def fmt_year(y):
    if y is None:
        return ""
    return f"{-y} BCE" if y < 0 else f"{y} AD"


def section_count(tid):
    p = PUB / f"{tid}.json"
    if not p.exists():
        return 0
    try:
        return len(json.loads(p.read_text(encoding="utf-8")).get("translation", []))
    except Exception:
        return 0


def first_scan(row):
    pages = (row.get("scans") or {}).get("pages") or []
    return pages[0]["file"] if pages else ""


def build():
    texts = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))["texts"]
    reading = json.loads(READING.read_text(encoding="utf-8")) if READING.exists() else {}
    colls = all_collections(texts)
    reg = load_all()

    # legacy collections: order rows by reading-order position
    for c in colls:
        if c["key"] not in reg:
            c["rows"].sort(key=lambda r: (reading.get(r["id"], {}).get("position", 10**6), r["id"]))

    total_entries = sum(len(c["rows"]) for c in colls)
    langs = sorted({(c.get("language") or c.get("original_lang_label", "").split("·")[0]).strip() for c in colls} - {""})

    # ---------------- collection pages ----------------
    out_dir = SITE / "collections"
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in colls:
        rows = c["rows"]
        n_sec = sum(section_count(r["id"]) for r in rows)
        dates = c.get("dates") or (rows[0].get("date_approx", "") if rows else "")
        if len(rows) <= CARD_THUMB_LIMIT:
            items = []
            for r in rows:
                t = thumb(first_scan(r))
                img = f'<div class="lib-card-scan"><img src="{t}" alt="" loading="lazy"></div>' if t else ""
                items.append(f'''<a href="/library/{r['slug']}" class="lib-card">{img}
            <div class="lib-card-body"><div class="lib-card-title">{e(r['title'])}</div>
            <div class="lib-card-meta">{e(r.get('date_approx', ''))} &middot; {section_count(r['id'])} sections</div></div></a>''')
            body = f'<div class="lib-card-grid">\n' + "\n".join(items) + "\n</div>"
        else:
            lis = "\n".join(f'<li><a href="/library/{r["slug"]}">{e(r["title"])}</a></li>' for r in rows)
            body = f'<ol class="coll-list">\n{lis}\n</ol>'
        src_bits = []
        for label, k in (("Images", "author_name"), ("Original text", "critical_edition"), ("English", "translator_name")):
            if c.get(k):
                src_bits.append(f"<li><strong>{label}:</strong> {e(c[k])}</li>")
        page = head(f"{c['label']} | Theosis Library", c.get("description", c["label"]), f"/collections/{c['key']}") + f"""
  <main>
    <div class="container container--library">
      <nav class="reading-breadcrumb" aria-label="Breadcrumb"><a href="/library/">Library</a><span class="reading-breadcrumb-sep">›</span><a href="/library/#{e(c['group'].lower().replace(' & ', '-').replace(' ', '-'))}">{e(c['group'])}</a></nav>
      <div class="coll-header">
        <h1>{e(c['label'])}</h1>
        <p class="coll-dates">{e(dates)}</p>
        <p class="coll-desc">{e(c.get('description', ''))}</p>
        <p class="coll-stats">{len(rows):,} entries &middot; {n_sec:,} sections, each with its manuscript image, original text and English</p>
        {'<ul class="coll-sources">' + ''.join(src_bits) + '</ul>' if src_bits else ''}
        {f'<p class="coll-start"><a class="coll-start-btn" href="/library/{rows[0]["slug"]}">Start reading →</a></p>' if rows else ''}
      </div>
      {body}
    </div>
  </main>
""" + FOOT + "</body>\n</html>\n"
        (out_dir / f"{c['key']}.html").write_text(page, encoding="utf-8")

    # ---------------- library index ----------------
    shelves_html = []
    for shelf in SHELVES + sorted({c["group"] for c in colls} - set(SHELVES)):
        cs = [c for c in colls if c["group"] == shelf]
        if not cs:
            continue
        cards = []
        for c in cs:
            t = thumb(first_scan(c["rows"][0])) if c["rows"] else ""
            img = f'<div class="lib-card-scan"><img src="{t}" alt="" loading="lazy"></div>' if t else ""
            dates = c.get("dates") or c["rows"][0].get("date_approx", "")
            cards.append(f'''<a href="/collections/{c['key']}" class="lib-card coll-card" data-search="{e((c['label'] + ' ' + c.get('search_terms', '') + ' ' + c.get('description', '')).lower())}">{img}
            <div class="lib-card-body"><div class="lib-card-title">{e(c['label'])}</div>
            <div class="lib-card-meta">{e(dates)} &middot; {len(c['rows']):,} {'entry' if len(c['rows']) == 1 else 'entries'}</div>
            <div class="coll-card-desc">{e(c.get('description', ''))}</div></div></a>''')
        anchor = shelf.lower().replace(" & ", "-").replace(" ", "-")
        shelves_html.append(f'''
      <section class="shelf" id="{anchor}">
        <div class="era-label">{e(shelf)}</div>
        <p class="shelf-note">{e(SHELF_NOTES.get(shelf, ''))}</p>
        <div class="lib-card-grid">
{chr(10).join(cards)}
        </div>
      </section>''')

    jump = " &middot; ".join(
        f'<a href="#{s.lower().replace(" & ", "-").replace(" ", "-")}">{e(s)}</a>'
        for s in SHELVES if any(c["group"] == s for c in colls))
    page = head("Library | Theosis Library",
                "Every collection in the Theosis Library, oldest civilisations first. Each entry pairs a photograph of the original "
                "document with the verbatim original-language text and an English translation.", "/library/") + f"""
  <main>
    <div class="container container--library">
      <h1>Library</h1>
      <p class="lib-intro">{total_entries:,} entries in {len(colls)} collections, oldest civilisations first. Every section shows the original document, the original language and an English translation.</p>

      <div class="search-container">
        <input type="text" class="search-input" id="search-input" placeholder="Search every text: words in English or the original, books, chapters, names...">
        <div class="search-results-info" id="search-results-info"></div>
      </div>
      <div id="search-results"></div>

      <p class="shelf-jump">{jump}</p>
{''.join(shelves_html)}
    </div>
  </main>
""" + FOOT + """
  <script type="module" src="/js/search.js"></script>
  <script>
  (function() {
    var q = new URLSearchParams(window.location.search).get('q');
    if (q) {
      var input = document.getElementById('search-input');
      if (input) { input.value = q; input.dispatchEvent(new Event('input')); }
    }
  })();
  </script>
</body>
</html>
"""
    (SITE / "library" / "index.html").write_text(page, encoding="utf-8")
    print(f"library: {len(colls)} collections, {total_entries} entries; {len(list(out_dir.glob('*.html')))} collection pages")
    return colls


if __name__ == "__main__":
    build()
