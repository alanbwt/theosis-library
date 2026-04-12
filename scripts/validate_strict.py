#!/usr/bin/env python3
"""
validate_strict.py — Strict validation for Theosis Library entries.

This MUST pass before any entry is published. Run after every import.

Rules (NON-NEGOTIABLE):
1. original_text MUST NOT equal text (no duplicate English)
2. original_text MUST be non-empty and contain real original-language content
3. text (English) MUST be non-empty
4. scan_pages MUST exist on disk and be >10KB each
5. verification field MUST be present with documented sources
6. HTML page MUST exist
7. No "estimated" or "approximate" scan page ranges — scans must be specific
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "texts.json"
PUB = ROOT / "translations" / "published"
LIB = ROOT / "site" / "library"
SCANS = ROOT / "site" / "assets" / "scans"


def validate_entry(tid, pub_data):
    """Validate one entry. Returns list of failure reasons (empty = pass)."""
    failures = []
    v = pub_data.get("verification", {})
    sections = pub_data.get("translation", [])

    # Rule 5: verification must exist
    if not v:
        failures.append("NO_VERIFICATION_FIELD")
        return failures

    # Rule 7: no estimated/approximate scans
    for field in ["scan_page_range", "note"]:
        val = str(v.get(field, "")).lower()
        if "estimated" in val or "approximate" in val or "proportional" in val:
            failures.append(f"ESTIMATED_SCANS: verification.{field} contains estimation language")

    if not sections:
        failures.append("NO_SECTIONS")
        return failures

    # Check first 3 sections for content quality
    for i, s in enumerate(sections[:3]):
        orig = s.get("original_text", "").strip()
        eng = s.get("text", "").strip()

        # Rule 3: English must be non-empty
        if not eng:
            failures.append(f"EMPTY_ENGLISH (section {i})")
            break

        # Rule 2: original must be non-empty
        if not orig:
            failures.append(f"EMPTY_ORIGINAL (section {i})")
            break

        # Rule 2: original must have real content (not just sup tags/numbers)
        orig_clean = re.sub(r"<[^>]+>", "", orig).strip()
        if len(orig_clean) < 10:
            failures.append(f"STUB_ORIGINAL (section {i}): only {len(orig_clean)} chars")
            break

        # Rule 1: original MUST NOT equal English
        eng_clean = re.sub(r"<[^>]+>", "", eng).strip()
        if orig_clean[:200] == eng_clean[:200]:
            failures.append(f"ORIGINAL_EQUALS_ENGLISH (section {i})")
            break

    # Rule 4: scan files must exist on disk
    scans = v.get("scan_local_paths", [])
    if not scans and v.get("scan_local_path"):
        scans = [v["scan_local_path"]]
    if not scans:
        # Check sections for scan_pages
        for s in sections[:1]:
            scans = s.get("scan_pages", [])
            if scans:
                break
    if not scans:
        failures.append("NO_SCAN_PATHS")
    else:
        for scan in scans:
            if not scan:
                failures.append("EMPTY_SCAN_PATH")
                break
            full = SCANS / scan
            if not full.exists():
                failures.append(f"SCAN_MISSING: {scan}")
                break
            if full.stat().st_size < 10000:
                failures.append(f"SCAN_TOO_SMALL: {scan} ({full.stat().st_size}b)")
                break

    # Rule 6: HTML page must exist
    html_path = LIB / f"{tid}.html"
    if not html_path.exists():
        failures.append("NO_HTML_PAGE")

    return failures


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    total = len(d["texts"])
    passed = 0
    failed_entries = []

    for t in d["texts"]:
        tid = t["id"]
        pub_path = PUB / f"{tid}.json"
        if not pub_path.exists():
            failed_entries.append((tid, ["MISSING_PUB_FILE"]))
            continue
        pub = json.loads(pub_path.read_text(encoding="utf-8"))
        failures = validate_entry(tid, pub)
        if failures:
            failed_entries.append((tid, failures))
        else:
            passed += 1

    print(f"{'=' * 60}")
    print(f"STRICT VALIDATION — THEOSIS LIBRARY")
    print(f"{'=' * 60}")
    print(f"Total entries: {total}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {len(failed_entries)}")

    if failed_entries:
        print(f"\nFailures:")
        from collections import Counter
        reasons = Counter()
        for tid, fails in failed_entries:
            for f in fails:
                reason = f.split(":")[0].split("(")[0].strip()
                reasons[reason] += 1
            print(f"  {tid}: {'; '.join(fails)}")

        print(f"\nFailure summary:")
        for reason, count in reasons.most_common():
            print(f"  {reason}: {count}")

        sys.exit(1)
    else:
        print(f"\nALL ENTRIES PASS STRICT VALIDATION")
        sys.exit(0)


if __name__ == "__main__":
    main()
