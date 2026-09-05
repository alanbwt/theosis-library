#!/usr/bin/env python3
"""
validate.py — Validate data integrity before publishing.

Usage:
    python scripts/validate.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCANS_DIR = PROJECT_ROOT / "site" / "assets" / "scans"

errors = []


def error(msg):
    errors.append(msg)
    print(f"  ERROR: {msg}")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("Validating Theosis Library data...\n")

    texts = load_json(DATA_DIR / "texts.json")
    authors = load_json(DATA_DIR / "authors.json")
    author_ids = {a["id"] for a in authors["authors"]}

    # Check texts
    slugs = set()
    ids = set()

    for text in texts["texts"]:
        tid = text["id"]
        print(f"  Checking: {tid}")

        # Unique ID and slug
        if tid in ids:
            error(f"{tid}: duplicate text ID")
        ids.add(tid)

        slug = text.get("slug", "")
        if slug in slugs:
            error(f"{tid}: duplicate slug '{slug}'")
        slugs.add(slug)

        # Author reference
        author_id = text.get("author_id", "")
        if author_id and author_id not in author_ids:
            error(f"{tid}: author_id '{author_id}' not found in authors.json")

        # Scans required for published texts
        if text.get("status") == "published":
            scans = text.get("scans")
            if not scans or not scans.get("pages"):
                error(f"{tid}: published text has no scans defined")
            else:
                for page in scans["pages"]:
                    scan_file = SCANS_DIR / page["file"]
                    if not scan_file.exists():
                        error(f"{tid}: scan file missing: {page['file']}")

        # Related texts reference valid IDs
        for rel_id in text.get("related_texts", []):
            if rel_id not in [t["id"] for t in texts["texts"]]:
                error(f"{tid}: related_text '{rel_id}' not found")

    # Check reviewed translations for published texts
    for text in texts["texts"]:
        if text.get("status") != "published":
            continue

        reviewed_path = PROJECT_ROOT / "translations" / "reviewed" / f"{text['id']}.json"
        if not reviewed_path.exists():
            error(f"{text['id']}: published but no reviewed translation file")
            continue

        reviewed = load_json(reviewed_path)
        content = reviewed.get("draft", reviewed)
        sections = content.get("translation", [])

        for section in sections:
            if not section.get("scan_pages"):
                error(f"{text['id']} section {section.get('section', '?')}: no scan_pages mapping")

    print(f"\n{'=' * 40}")
    if errors:
        print(f"FAILED: {len(errors)} error(s) found")
        sys.exit(1)
    else:
        print("PASSED: all checks passed")


if __name__ == "__main__":
    main()
