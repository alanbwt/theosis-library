#!/usr/bin/env python3
"""One-off: re-fetch KJV English for the single-chapter NT books whose English
columns ended up truncated (Obadiah, Philemon, 2 John, 3 John, Jude).

bible-api.com treats `obadiah 1` as "chapter 1 verse 1" for one-chapter books,
so the original import call only got verse 1. Requery with `<book> 1:1-N` and
rebuild each section's English text verbatim from bible-api.com.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"

# book_key → (bible-api name, verse count in KJV)
TARGETS = {
    "obad":     ("obadiah",  21),
    "philemon": ("philemon", 25),
    "2john":    ("2 john",   13),
    "3john":    ("3 john",   14),
    "jude":     ("jude",     25),
}


def fetch_kjv_chapter(name: str, verses: int) -> dict[int, str]:
    ref = f"{name} 1:1-{verses}"
    url = "https://bible-api.com/" + urllib.parse.quote(ref) + "?translation=kjv"
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibraryBot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    return {v["verse"]: (v.get("text") or "").strip() for v in data.get("verses", [])}


def build_section_english(greek_html: str, kjv_by_verse: dict[int, str]) -> str:
    """Re-build the English paragraph using the same <sup>N</sup>…<sup>N+1</sup>
    boundaries that the Greek column already uses, so verses align."""
    verse_nums = [int(n) for n in re.findall(r"<sup>(\d+)</sup>", greek_html)]
    parts = []
    for n in verse_nums:
        text = kjv_by_verse.get(n, "")
        if text:
            parts.append(f"<sup>{n}</sup>{text}")
    return " ".join(parts)


def patch(path: Path, manuscript_prefix: str) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    sections = data.get("translation") or []
    if not sections:
        return False

    # Derive book_key from slug pattern: verified-<ms>-<book>-<chapter>
    m = re.match(r"verified-[a-z]+-([a-z0-9]+)-\d+$", data["id"])
    if not m:
        return False
    book_key = m.group(1)
    if book_key not in TARGETS:
        return False

    bible_name, total_verses = TARGETS[book_key]
    try:
        kjv = fetch_kjv_chapter(bible_name, total_verses)
    except Exception as e:
        print(f"  {path.name}: KJV fetch failed: {e}")
        return False
    if len(kjv) < total_verses // 2:
        print(f"  {path.name}: unexpectedly few KJV verses ({len(kjv)})")
        return False

    changed = False
    for s in sections:
        new_eng = build_section_english(s.get("original_text", ""), kjv)
        if new_eng and new_eng != (s.get("text") or "").strip():
            s["text"] = new_eng
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return changed


def main():
    touched = 0
    for path in sorted(PUB.glob("verified-*.json")):
        if patch(path, ""):
            print(f"  patched {path.name}")
            touched += 1
    print(f"Done. Patched {touched} entries.")


if __name__ == "__main__":
    main()
