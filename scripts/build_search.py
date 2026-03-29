#!/usr/bin/env python3
"""
build_search.py — Generate passage-level search index and metadata for MiniSearch.

Outputs:
  site/data/texts-meta.json   — compact metadata for faceted filtering (loads immediately)
  site/data/search-index.json — passage-level entries for full-text search (loads on demand)
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PUBLISHED_DIR = PROJECT_ROOT / "translations" / "published"
OUTPUT_DIR = PROJECT_ROOT / "site" / "data"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def strip_html(text):
    """Remove HTML tags from text for indexing."""
    return re.sub(r"<[^>]+>", "", text or "")


def build():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    texts = load_json(DATA_DIR / "texts.json")
    authors = load_json(DATA_DIR / "authors.json")
    author_map = {a["id"]: a for a in authors["authors"]}

    # --- texts-meta.json (compact, loads immediately) ---
    meta = []
    for t in texts["texts"]:
        author = author_map.get(t.get("author_id", ""), {})
        meta.append({
            "id": t["id"],
            "title": t["title"],
            "author": author.get("name", "Unknown"),
            "dates": author.get("dates", ""),
            "century": t.get("century", 0),
            "era": t.get("era", ""),
            "language": t.get("language", ""),
            "tradition": t.get("tradition", ""),
            "category": t.get("category", ""),
            "is_first": t.get("is_first_translation", False),
            "themes": t.get("themes", []),
            "slug": t.get("slug", ""),
            "status": t["status"],
            "description": t.get("description", ""),
        })

    with open(OUTPUT_DIR / "texts-meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    print(f"texts-meta.json: {len(meta)} texts")

    # --- search-index.json (passage-level, loads on demand) ---
    passages = []
    for t in texts["texts"]:
        if t["status"] != "published":
            continue

        pub_path = PUBLISHED_DIR / f"{t['id']}.json"
        if not pub_path.exists():
            continue

        reviewed = load_json(pub_path)
        content = reviewed.get("draft", reviewed)
        author = author_map.get(t.get("author_id", ""), {})

        for section in content.get("translation", []):
            passages.append({
                "pid": section.get("passage_id", f"{t['id']}.{section['section']}"),
                "tid": t["id"],
                "s": section["section"],
                "en": strip_html(section.get("text", "")),
                "orig": strip_html(section.get("original_text", "")),
                "title": t["title"],
                "author": author.get("name", "Unknown"),
                "slug": t.get("slug", ""),
            })

    with open(OUTPUT_DIR / "search-index.json", "w", encoding="utf-8") as f:
        json.dump(passages, f, ensure_ascii=False)
    print(f"search-index.json: {len(passages)} passages across published texts")


if __name__ == "__main__":
    build()
