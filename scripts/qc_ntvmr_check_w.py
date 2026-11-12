#!/usr/bin/env python3
"""
qc_ntvmr_check_w.py: cross-check the page mapping of the Codex Washingtonianus
Matthew and Luke entries (built from CSNTM's verse index by
import_washingtonianus.py; Greek still Tischendorf because the NTVMR
transcription files for these books state "All rights reserved by the INTF")
against the page on which the NTVMR transcription places each verse.

Read-only: prints every verse whose NTVMR page is not among the scan_pages of
the section that shows it. NTVMR page -> CSNTM page comes from
data/sources/qc-legacy/ntvmr/w_page_to_csntm.json (written by
qc_swap_ntvmr_transcriptions.py). Run from the repo root with python3 -I.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import qc_ntvmr_parse as P  # noqa: E402

wmap = json.loads((P.CACHE / "w_page_to_csntm.json").read_text(encoding="utf-8"))
pages, verses = P.parse_ntvmr_doc(20032)
BOOK = {"matt": 1, "luke": 3}
bad, checked, extra = [], 0, []
for f in sorted((ROOT / "translations" / "published").glob("verified-washingtonianus-*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    m = re.match(r"verified-washingtonianus-(matt|luke)-(\d+)$", d["id"])
    if not m:
        continue
    b, ch = BOOK[m.group(1)], int(m.group(2))
    for s in d["translation"]:
        have = {int(re.search(r"w-p(\d{4})", p).group(1)) for p in s["scan_pages"]}
        union = set()
        for v in [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s["text"])]:
            for p, _c, t in verses.get((b, ch, v), []):
                if t and str(p) in wmap:
                    union.add(wmap[str(p)]["csntm_page"])
        if union and have - union:
            extra.append((d["id"], s["section"], sorted(have - union)))
        for v in [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s["text"])]:
            parts = [x for x in verses.get((b, ch, v), []) if x[2]]
            if not parts:
                continue
            checked += 1
            pg = {wmap[str(p)]["csntm_page"] for p, _c, _t in parts if str(p) in wmap}
            if not pg & have:
                bad.append((d["id"], s["section"], v, sorted(have), sorted(pg)))
print(f"verses checked: {checked}; NTVMR page not among the section's pages: {len(bad)}")
for x in bad:
    print("  ", x)
print(f"sections listing a page that carries none of their verses: {len(extra)}")
for x in extra:
    print("  ", x)
