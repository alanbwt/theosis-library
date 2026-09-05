#!/usr/bin/env python3
"""One-off: add scan_pages mapping to Filastrius reviewed JSON."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REVIEWED = PROJECT_ROOT / "translations" / "reviewed" / "filastrius-gnostic-heresies.json"
TEXTS = PROJECT_ROOT / "data" / "texts.json"

# Section -> scan pages mapping (from the page-to-chapter table)
SECTION_SCANS = {
    "29": ["csel38-p14.jpg", "csel38-p15.jpg"],
    "30": ["csel38-p15.jpg"],
    "31": ["csel38-p16.jpg"],
    "32": ["csel38-p16.jpg", "csel38-p17.jpg"],
    "33": ["csel38-p17.jpg", "csel38-p18.jpg"],
    "34": ["csel38-p18.jpg", "csel38-p19.jpg"],
    "35": ["csel38-p19.jpg"],
    "36": ["csel38-p19.jpg", "csel38-p20.jpg"],
    "37": ["csel38-p20.jpg"],
    "38": ["csel38-p20.jpg", "csel38-p21.jpg"],
    "39": ["csel38-p21.jpg"],
    "40": ["csel38-p22.jpg"],
    "41": ["csel38-p22.jpg"],
    "42": ["csel38-p22.jpg"],
    "43": ["csel38-p23.jpg"],
}

def main():
    with open(REVIEWED, encoding="utf-8") as f:
        data = json.load(f)

    for section in data["draft"]["translation"]:
        s = section["section"]
        section["scan_pages"] = SECTION_SCANS.get(s, [])
        section["passage_id"] = f"filastrius-gnostic-heresies.{s}"
        print(f"  Section {s}: {len(section['scan_pages'])} scan(s), id={section['passage_id']}")

    with open(REVIEWED, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {REVIEWED}")

if __name__ == "__main__":
    main()
