#!/usr/bin/env python3
"""Build a reading-order index so every library page can show prev/next chapter
links like an e-book. One ordered list per manuscript; render_verified.py reads
it to pick prev/next for each entry.

Order within each manuscript:
  - Sinaiticus: OT (LXX order) → NT (canonical order)
  - Vaticanus: NT (canonical order)
  - Bezae: Gospels + Acts (canonical order; Bezae's physical order is Gospels
    in Western order Mt/Jn/Lk/Mk + Acts, but we keep canonical order for the
    reader's mental model — a preference can be added later).
  - Venetus A: Iliad books 1–24
  - Codex Regius: Eddic poems in manuscript order
  - DSS: single entry
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "texts.json"
OUT = ROOT / "site" / "data" / "reading-order.json"

# Canonical biblical order used wherever a book has chapters.
NT_ORDER = [
    "matt", "mark", "luke", "john", "acts",
    "romans", "1cor", "2cor", "gal", "eph", "phil", "col",
    "1thess", "2thess", "1tim", "2tim", "titus", "philemon",
    "hebrews", "james", "1peter", "2peter",
    "1john", "2john", "3john", "jude", "rev",
]

# Sinaiticus OT order (as it appears in the LXX/Sinaiticus arrangement).
OT_ORDER = [
    "job", "ps", "prov", "eccl",
    "isa", "jer",
    "joel", "obad", "jonah", "nahum", "hab",
    "zeph", "hag", "zech", "mal",
]

# Eddic poems in Codex Regius manuscript order.
EDDA_ORDER = [
    "voluspa", "havamal", "vafthrudnismal", "grimnismal",
    "skirnismal", "harbardsljod", "hymiskvida",
    "lokasenna", "thrymskvida", "volundarkvida", "alvissmal",
]


def book_and_chapter(slug: str):
    """Extract (book_key, chapter_int_or_none) from a verified slug."""
    m = re.match(r"verified-[a-z]+-([a-z0-9]+)(?:-(\d+))?$", slug)
    if not m:
        return (None, None)
    return (m.group(1), int(m.group(2)) if m.group(2) else None)


def sort_chapters(entries, book_order):
    """Given entries of the same book, sort by chapter."""
    keyed = {}
    for e in entries:
        book, ch = book_and_chapter(e["id"])
        keyed[(book, ch or 0)] = e
    out = []
    for book in book_order:
        chapters = sorted([(k, v) for k, v in keyed.items() if k[0] == book])
        for _, v in chapters:
            out.append(v)
    # Any unclassified entries (shouldn't happen) go at the end in slug order.
    known = {v["id"] for _, v in keyed.items() if _[0] in book_order}
    for e in entries:
        if e["id"] not in known:
            out.append(e)
    return out


def build():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    texts = [t for t in data["texts"] if t.get("status") == "published"]

    buckets = {
        "sinaiticus": [],
        "vaticanus": [],
        "bezae": [],
        "venetus": [],
        "edda": [],
        "dss": [],
    }
    for t in texts:
        for key in buckets:
            if t["id"].startswith(f"verified-{key}-"):
                buckets[key].append(t)
                break

    order = {}

    # Sinaiticus: OT first, then NT
    sin_ordered = (
        sort_chapters([e for e in buckets["sinaiticus"] if book_and_chapter(e["id"])[0] in OT_ORDER], OT_ORDER)
        + sort_chapters([e for e in buckets["sinaiticus"] if book_and_chapter(e["id"])[0] in NT_ORDER], NT_ORDER)
    )
    order["sinaiticus"] = [e["id"] for e in sin_ordered]

    order["vaticanus"] = [e["id"] for e in sort_chapters(buckets["vaticanus"], NT_ORDER)]
    order["bezae"] = [e["id"] for e in sort_chapters(buckets["bezae"], NT_ORDER)]

    # Venetus A: Iliad books numerically
    venetus_sorted = sorted(
        buckets["venetus"],
        key=lambda e: int(re.search(r"iliad-(\d+)", e["id"]).group(1)),
    )
    order["venetus"] = [e["id"] for e in venetus_sorted]

    # Codex Regius (Edda) in manuscript order
    edda_by_name = {re.search(r"edda-([a-z]+)", e["id"]).group(1): e for e in buckets["edda"]}
    order["edda"] = [edda_by_name[name]["id"] for name in EDDA_ORDER if name in edda_by_name]
    # any edda entries we missed
    for e in buckets["edda"]:
        if e["id"] not in order["edda"]:
            order["edda"].append(e["id"])

    order["dss"] = [e["id"] for e in buckets["dss"]]

    # Build prev/next lookup per entry, plus pretty labels.
    by_id = {t["id"]: t for t in texts}
    reading = {}  # id -> {prev, next, manuscript, manuscript_label, position, total}
    MANUSCRIPT_LABEL = {
        "sinaiticus": "Codex Sinaiticus",
        "vaticanus": "Codex Vaticanus",
        "bezae": "Codex Bezae",
        "venetus": "Venetus A (Iliad)",
        "edda": "Codex Regius (Poetic Edda)",
        "dss": "Dead Sea Scrolls",
    }
    for manuscript, ids in order.items():
        total = len(ids)
        for i, tid in enumerate(ids):
            prev_id = ids[i - 1] if i > 0 else None
            next_id = ids[i + 1] if i < total - 1 else None
            reading[tid] = {
                "manuscript": manuscript,
                "manuscript_label": MANUSCRIPT_LABEL[manuscript],
                "position": i + 1,
                "total": total,
                "prev": {
                    "id": prev_id,
                    "title": by_id[prev_id]["title"] if prev_id else None,
                }
                if prev_id
                else None,
                "next": {
                    "id": next_id,
                    "title": by_id[next_id]["title"] if next_id else None,
                }
                if next_id
                else None,
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(reading, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"reading-order.json: {len(reading)} entries across {len(order)} manuscripts")


if __name__ == "__main__":
    build()
