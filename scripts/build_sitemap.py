#!/usr/bin/env python3
"""Generate sitemap.xml for search engines."""

import json
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SITE_DIR = PROJECT_ROOT / "site"

BASE_URL = "https://theosislibrary.com"


def build():
    texts = json.load(open(DATA_DIR / "texts.json"))
    today = str(date.today())

    urls = [
        (f"{BASE_URL}/", today, "1.0"),
        (f"{BASE_URL}/library/", today, "0.9"),
        (f"{BASE_URL}/quotes/", today, "0.8"),
        (f"{BASE_URL}/about.html", today, "0.5"),
    ]

    for t in texts["texts"]:
        if t["status"] == "published":
            urls.append((
                f"{BASE_URL}/library/{t['slug']}.html",
                t.get("date_published", today),
                "0.8",
            ))
            # Also add the print/download version
            urls.append((
                f"{BASE_URL}/downloads/{t['slug']}.html",
                t.get("date_published", today),
                "0.3",
            ))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url, lastmod, priority in urls:
        xml += f"  <url>\n"
        xml += f"    <loc>{url}</loc>\n"
        xml += f"    <lastmod>{lastmod}</lastmod>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += f"  </url>\n"
    xml += "</urlset>\n"

    out = SITE_DIR / "sitemap.xml"
    out.write_text(xml, encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} URLs")


if __name__ == "__main__":
    build()
