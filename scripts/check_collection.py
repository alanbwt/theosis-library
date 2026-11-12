#!/usr/bin/env python3
"""
check_collection.py — strict, section-level validation of one collection
(or all collections) defined in data/collections/<key>.json.

Usage:
    python3 scripts/check_collection.py <key> [<key> ...]
    python3 scripts/check_collection.py --all

Hard failures (exit 1):
  - collection block missing required keys / unknown shelf / prefix mismatch
  - catalog row missing fields, slug != id, missing "order", missing "verified" theme
  - published JSON missing for a row, or a published JSON under the prefix with no row
  - verification block missing a required provenance field
  - any section: empty/short original, empty English, original == English,
    original that reads as English, no scan_pages, scan file missing/too small/unreadable
  - estimation language ("estimated", "approximate", "proportional", "roughly",
    "assumed", "guess") in scan mapping fields or scan notes
  - <script> in any text field
Warnings (exit 0): short originals, small images, entries whose many sections all
point at one image (fine for a single tablet or stele; check it is intended).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collections_lib import COLL_DIR, REQUIRED_COLLECTION_KEYS, ROOT, SHELVES, load_all  # noqa: E402

PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"

ROW_KEYS = ["id", "title", "author_id", "language", "era", "tradition", "category", "date_approx",
            "century", "source", "description", "themes", "status", "slug", "scans", "order"]
VERIF_KEYS = ["scan_source", "scan_license", "scan_manuscript", "scan_mapping", "scan_local_paths",
              "original_text_source", "original_text_license", "translation_source",
              "translation_license", "verified_date"]
ESTIMATE_RE = re.compile(r"\b(estimat\w*|approximat\w*|proportional\w*|roughly|assum\w*|guess\w*)\b", re.I)
EN_STOP = {"the", "and", "of", "that", "which", "with", "was", "were", "they", "their", "them",
           "his", "from", "have", "this", "unto", "shall", "thou", "thy"}


def vis(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def looks_english(text):
    toks = re.findall(r"[A-Za-z]+", text.lower())
    if len(toks) < 12:
        return False
    return sum(t in EN_STOP for t in toks) / len(toks) > 0.12


def image_info(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def check(key, d, hard, warn):
    c = d.get("collection", {})
    for k in REQUIRED_COLLECTION_KEYS:
        if c.get(k) in (None, ""):
            hard.append(f"[{key}] collection.{k} missing")
    if c.get("group") not in SHELVES:
        hard.append(f"[{key}] collection.group '{c.get('group')}' not in SHELVES {SHELVES}")
    prefix = c.get("prefix", "")
    if not prefix.startswith("verified-") or not prefix.endswith("-"):
        hard.append(f"[{key}] prefix '{prefix}' must look like 'verified-<key>-'")
    rows = d.get("texts", [])
    if not rows:
        hard.append(f"[{key}] no texts")
    ids = [r.get("id") for r in rows]
    for tid, n in Counter(ids).items():
        if n > 1:
            hard.append(f"[{key}] duplicate row id {tid}")
    orders = [r.get("order") for r in rows]
    if len(set(orders)) != len(orders):
        warn.append(f"[{key}] duplicate 'order' values (reading order ambiguous)")

    for r in rows:
        tid = r.get("id", "?")
        for k in ROW_KEYS:
            if k not in r or r[k] in (None, "", []):
                hard.append(f"[{tid}] row.{k} missing")
        if not tid.startswith(prefix):
            hard.append(f"[{tid}] id does not start with prefix {prefix}")
        if r.get("slug") != tid:
            hard.append(f"[{tid}] slug != id")
        if "verified" not in (r.get("themes") or []):
            hard.append(f"[{tid}] themes must include 'verified'")
        if r.get("status") != "published":
            hard.append(f"[{tid}] status must be 'published'")
        if not isinstance(r.get("order"), int):
            hard.append(f"[{tid}] order must be an int")
        for p in (r.get("scans") or {}).get("pages", []):
            if not (SCANS / p.get("file", "")).exists():
                hard.append(f"[{tid}] row.scans file missing {p.get('file')}")

        pf = PUB / f"{tid}.json"
        if not pf.exists():
            hard.append(f"[{tid}] no published JSON at {pf.relative_to(ROOT)}")
            continue
        pub = json.loads(pf.read_text(encoding="utf-8"))
        if pub.get("id") != tid or pub.get("slug", tid) != tid:
            hard.append(f"[{tid}] published id/slug mismatch")
        for k in ("title", "introduction", "description", "source"):
            if not pub.get(k):
                hard.append(f"[{tid}] published.{k} missing")
        v = pub.get("verification") or {}
        for k in VERIF_KEYS:
            if v.get(k) in (None, "", []):
                hard.append(f"[{tid}] verification.{k} missing")
        for k, val in v.items():
            if k.startswith("scan_") and isinstance(val, str) and ESTIMATE_RE.search(val):
                hard.append(f"[{tid}] verification.{k} uses estimation language: '{ESTIMATE_RE.search(val).group(0)}'")
        for p in v.get("scan_local_paths") or []:
            if not (SCANS / p).exists():
                hard.append(f"[{tid}] verification.scan_local_paths missing file {p}")

        secs = pub.get("translation") or []
        if not secs:
            hard.append(f"[{tid}] no sections")
        sec_ids = Counter(str(s.get("section", "")) for s in secs)
        for sid, n in sec_ids.items():
            if not sid:
                hard.append(f"[{tid}] a section has no 'section' id")
            elif n > 1:
                hard.append(f"[{tid}] section id '{sid}' repeated {n}x")
        imgs = Counter()
        for s in secs:
            sid = s.get("section", "?")
            o, e = vis(s.get("original_text")), vis(s.get("text"))
            if len(o) < 3:
                hard.append(f"[{tid} §{sid}] original_text empty")
            elif len(o) < 10:
                warn.append(f"[{tid} §{sid}] original_text very short ({len(o)} chars)")
            if len(e) < 3:
                hard.append(f"[{tid} §{sid}] English empty")
            if o and e and o[:120] == e[:120]:
                hard.append(f"[{tid} §{sid}] original == English")
            if looks_english(o):
                hard.append(f"[{tid} §{sid}] original_text reads as English")
            for fld in ("original_text", "text", "edition_text", "scan_note"):
                if "<script" in (s.get(fld) or "").lower():
                    hard.append(f"[{tid} §{sid}] <script> in {fld}")
            if s.get("scan_note") and ESTIMATE_RE.search(s["scan_note"]):
                hard.append(f"[{tid} §{sid}] scan_note uses estimation language: '{ESTIMATE_RE.search(s['scan_note']).group(0)}'")
            sp = s.get("scan_pages") or []
            if not sp:
                hard.append(f"[{tid} §{sid}] no scan_pages")
            for p in sp:
                imgs[p] += 1
                fp = SCANS / p
                if not fp.exists():
                    hard.append(f"[{tid} §{sid}] scan missing {p}")
                    continue
                size = fp.stat().st_size
                if size < 10_000:
                    hard.append(f"[{tid} §{sid}] scan too small {p} ({size} b)")
                if size > 8_000_000:
                    hard.append(f"[{tid} §{sid}] scan too large {p} ({size} b; keep under 8 MB)")
                dims = image_info(fp)
                if dims is None:
                    hard.append(f"[{tid} §{sid}] scan unreadable {p}")
                elif min(dims) < 500:
                    warn.append(f"[{tid} §{sid}] scan small {p} {dims}")
        if len(secs) >= 4 and len(imgs) == 1:
            warn.append(f"[{tid}] all {len(secs)} sections point at one image {next(iter(imgs))} "
                        "(fine for one tablet/stele/page; wrong for a multi-page text)")

    # orphans: published files under this prefix with no catalog row
    if prefix:
        listed = set(ids)
        for f in PUB.glob(f"{prefix}*.json"):
            if f.stem not in listed:
                hard.append(f"[{key}] orphan published file {f.name} (no row in data/collections/{key}.json)")


def main():
    args = sys.argv[1:]
    reg = load_all()
    keys = sorted(reg) if args == ["--all"] else args
    if not keys:
        print(__doc__)
        sys.exit(2)
    hard, warn = [], []
    total_entries = total_sections = 0
    for k in keys:
        if k not in reg:
            hard.append(f"no collection file data/collections/{k}.json")
            continue
        check(k, reg[k], hard, warn)
        for r in reg[k].get("texts", []):
            total_entries += 1
            pf = PUB / f"{r.get('id')}.json"
            if pf.exists():
                total_sections += len(json.loads(pf.read_text(encoding="utf-8")).get("translation", []))
    for w in warn[:200]:
        print("WARN", w)
    if len(warn) > 200:
        print(f"WARN ... {len(warn) - 200} more")
    for h in hard[:300]:
        print("FAIL", h)
    if len(hard) > 300:
        print(f"FAIL ... {len(hard) - 300} more")
    print(f"\n{', '.join(keys)}: {total_entries} entries, {total_sections} sections, "
          f"{len(hard)} hard failures, {len(warn)} warnings")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
