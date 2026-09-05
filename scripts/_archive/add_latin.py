#!/usr/bin/env python3
"""One-off script to add original Latin text to the Filastrius reviewed JSON."""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "filastrius_chapters_29_60.txt"
REVIEWED_FILE = PROJECT_ROOT / "translations" / "reviewed" / "filastrius-gnostic-heresies.json"


def parse_latin_chapters(text):
    """Parse the source file into {chapter_number: latin_text} dict."""
    chapters = {}
    # Split on chapter headers
    parts = re.split(r'={5,}\nCAPUT (\d+)\n={5,}', text)
    # parts[0] is the preamble, then alternating: chapter_num, chapter_text
    for i in range(1, len(parts), 2):
        chap_num = parts[i].strip()
        chap_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        # Clean up the Latin text: join broken lines, normalize whitespace
        # The CSEL text has line breaks mid-word and extra spaces
        lines = chap_text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
        # Join all lines into one block, then split into paragraphs on double-period or clear breaks
        joined = ' '.join(cleaned_lines)
        # Normalize multiple spaces
        joined = re.sub(r'\s+', ' ', joined)
        # Fix broken words (hyphenation artifacts from the CSEL scan)
        # Remove artifacts like "I " or "II " that are footnote markers
        joined = re.sub(r'\s+I\s+', ' ', joined)
        joined = re.sub(r'\s+II\s+', ' ', joined)
        joined = re.sub(r'\s+III\s+', ' ', joined)
        # Clean up HTML entities that got in
        joined = joined.replace('&lt;', '<').replace('&gt;', '>')
        chapters[chap_num] = joined.strip()
    return chapters


def main():
    source_text = SOURCE_FILE.read_text(encoding="utf-8")
    chapters = parse_latin_chapters(source_text)

    with open(REVIEWED_FILE, encoding="utf-8") as f:
        reviewed = json.load(f)

    for section in reviewed["draft"]["translation"]:
        chap_num = section["section"]
        if chap_num in chapters:
            section["original_text"] = chapters[chap_num]
            print(f"  Chapter {chap_num}: {len(chapters[chap_num])} chars of Latin added")
        else:
            print(f"  Chapter {chap_num}: NO LATIN FOUND")

    with open(REVIEWED_FILE, "w", encoding="utf-8") as f:
        json.dump(reviewed, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {REVIEWED_FILE}")


if __name__ == "__main__":
    main()
