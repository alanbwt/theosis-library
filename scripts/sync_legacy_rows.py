#!/usr/bin/env python3
"""sync_legacy_rows.py — keep data/texts.json rows of the older collections (those without a
data/collections/<key>.json) in step with their published JSONs: scans.pages lists every page the
entry's sections link, in order; title/description/source/language follow the published JSON."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collections_lib import LEGACY, ROOT, load_all  # noqa: E402

PUB = ROOT / "translations" / "published"
DATA = ROOT / "data" / "texts.json"


def main():
    reg = load_all()
    prefixes = [c["prefix"] for c in LEGACY if c["key"] not in reg]
    d = json.loads(DATA.read_text(encoding="utf-8"))
    changed = 0
    for r in d["texts"]:
        if not any(r["id"].startswith(p) for p in prefixes):
            continue
        pf = PUB / f"{r['id']}.json"
        if not pf.exists():
            continue
        pub = json.loads(pf.read_text(encoding="utf-8"))
        pages = []
        for s in pub.get("translation", []):
            for p in s.get("scan_pages") or []:
                if p not in pages:
                    pages.append(p)
        new_scans = {"pages": [{"file": p, "caption": Path(p).stem} for p in pages]}
        before = json.dumps(r, sort_keys=True)
        r["scans"] = new_scans
        for k in ("title", "description", "source", "language"):
            if pub.get(k):
                r[k] = pub[k]
        if json.dumps(r, sort_keys=True) != before:
            changed += 1
    DATA.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"legacy rows synced: {changed} changed")


if __name__ == "__main__":
    main()
