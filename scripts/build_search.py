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
    """Remove HTML tags for indexing; verse/line numbers become separate tokens."""
    text = re.sub(r"<sup>(.*?)</sup>", r" \1 ", text or "")
    text = re.sub(r"<br\s*/?>|</p>", " ", text)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


def build():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    texts = load_json(DATA_DIR / "texts.json")
    authors = load_json(DATA_DIR / "authors.json")
    author_map = {a["id"]: a for a in authors["authors"]}
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from collections_lib import all_collections
    coll_label = {}
    for c in all_collections(texts["texts"]):
        for r in c["rows"]:
            coll_label[r["id"]] = c["label"]

    # --- texts-meta.json (compact, loads immediately) ---
    meta = []
    for t in texts["texts"]:
        author = author_map.get(t.get("author_id", ""), {})
        meta.append({
            "id": t["id"],
            "title": t["title"],
            "author": author.get("name") or coll_label.get(t["id"], ""),
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
                "author": author.get("name") or coll_label.get(t["id"], ""),
                "slug": t.get("slug", ""),
            })

    # Shard into files of at most ~18 MB (Cloudflare Pages limit is 25 MiB per file).
    # English+metadata shards and original-language shards; search.js merges them by pid.
    orig = {p["pid"]: p.pop("orig") for p in passages}
    for p in passages:
        p.pop("slug", None)  # identical to tid
    sdir = OUTPUT_DIR / "search"
    sdir.mkdir(parents=True, exist_ok=True)
    for old in sdir.glob("*.json"):
        old.unlink()
    LIMIT = 18_000_000

    def shard(items, name, as_dict):
        files, cur, size = [], ([] if not as_dict else {}), 0
        def flush():
            nonlocal cur, size
            if cur:
                fn = f"{name}-{len(files)}.json"
                (sdir / fn).write_text(json.dumps(cur, ensure_ascii=False), encoding="utf-8")
                files.append(f"/data/search/{fn}")
            cur, size = ([] if not as_dict else {}), 0
        for it in items:
            n = len(json.dumps(it, ensure_ascii=False).encode())
            if size + n > LIMIT:
                flush()
            if as_dict:
                cur[it[0]] = it[1]
            else:
                cur.append(it)
            size += n
        flush()
        return files

    manifest = {"en": shard(passages, "en", False), "orig": shard(list(orig.items()), "orig", True),
                "passages": len(passages)}
    (sdir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    for legacy in ("search-index.json", "search-index-orig.json"):
        if (OUTPUT_DIR / legacy).exists():
            (OUTPUT_DIR / legacy).unlink()
    print(f"search: {len(passages)} passages in {len(manifest['en'])}+{len(manifest['orig'])} shards")


if __name__ == "__main__":
    build()
