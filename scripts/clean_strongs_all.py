#!/usr/bin/env python3
"""One-off: strip <S>NNNN</S> Strong's numbers from all published translation JSONs.

Bezae and Vaticanus imports skipped the clean_strongs() step that Sinaiticus NT used,
leaving inline Strong's numbers that render as visible text in the Greek column.
This script cleans every published section's original_text and rewrites the file.
"""
import json
import re
from pathlib import Path

STRONGS_RE = re.compile(r"<S>\d+</S>")
WS_COLLAPSE_RE = re.compile(r"[ \t]{2,}")

PUB = Path(__file__).resolve().parent.parent / "translations" / "published"


def clean(text):
    if not text:
        return text
    cleaned = STRONGS_RE.sub("", text)
    cleaned = WS_COLLAPSE_RE.sub(" ", cleaned)
    return cleaned.strip()


def main():
    touched = 0
    scanned = 0
    for path in sorted(PUB.glob("*.json")):
        scanned += 1
        data = json.loads(path.read_text(encoding="utf-8"))
        sections = data.get("translation") or []
        changed = False
        for s in sections:
            orig = s.get("original_text")
            if orig and "<S>" in orig:
                s["original_text"] = clean(orig)
                changed = True
        if changed:
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            touched += 1

    print(f"Scanned {scanned} files; rewrote {touched}.")


if __name__ == "__main__":
    main()
