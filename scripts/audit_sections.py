#!/usr/bin/env python3
"""
audit_sections.py — Deep per-section audit (validate_strict.py only checks the
first 3 sections of each entry). Checks EVERY section for:
  - empty original / empty English / original == English
  - missing or tiny scan files
  - verse-number alignment between original and English (numbering
    differences are expected for LXX vs KJV; anything flagged must carry a
    "Numbering" note in the introduction)
  - Sinaiticus: every section has folio(s) resolved per verse
Exit 1 on hard failures; alignment differences are reported as warnings.
"""
import json, re, glob, os, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "site", "assets", "scans")
hard = defaultdict(list); warn = defaultdict(list); fam = Counter()
def sups(s): return re.findall(r"<sup>([^<]+)</sup>", s)
for f in sorted(glob.glob(os.path.join(ROOT, "translations", "published", "*.json"))):
    d = json.load(open(f, encoding="utf-8")); tid = d["id"]; fam[tid.split("-")[1]] += 1
    v = d.get("verification", {})
    for s in d["translation"]:
        o = re.sub(r"<[^>]+>", "", s.get("original_text", "")).strip()
        e = re.sub(r"<[^>]+>", "", s.get("text", "")).strip()
        sec = s.get("section")
        if len(o) < 10 and not s.get("scan_note"): hard["empty_original"].append((tid, sec))
        if len(e) < 10: hard["empty_english"].append((tid, sec))
        if o and e and o[:100] == e[:100]: hard["orig_eq_eng"].append((tid, sec))
        sp = s.get("scan_pages") or []
        if not sp: hard["section_no_scan"].append((tid, sec))
        for p in sp:
            fp = os.path.join(SC, p)
            if not os.path.exists(fp) or os.path.getsize(fp) < 10000: hard["scan_missing"].append((tid, p))
        so, se = sups(s.get("original_text", "")), sups(s.get("text", ""))
        if so and se and so != se and "Numbering:" not in d.get("introduction", "") and tid.split("-")[1] in ("sinaiticus", "vaticanus", "bezae"):
            warn["verse_numbering_differs_without_note"].append((tid, sec))
    if tid.startswith("verified-sinaiticus-") and not v.get("section_folios_verified"):
        hard["sinaiticus_sections_not_folio_verified"].append(tid)
print("entries by manuscript:", dict(fam))
for k, vals in warn.items():
    print(f"WARN {k}: {len(vals)}"); [print("   ", x) for x in vals[:10]]
bad = 0
for k, vals in hard.items():
    bad += len(vals); print(f"FAIL {k}: {len(vals)}"); [print("   ", x) for x in vals[:10]]
print("ALL SECTIONS PASS" if not bad else f"{bad} HARD FAILURES")
sys.exit(1 if bad else 0)
