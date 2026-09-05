#!/usr/bin/env python3
"""
import_washingtonianus.py — Import Codex Washingtonianus (GA 032, Freer Gospels).

Pipeline per chapter:
  1. Ask CSNTM which image IDs cover each verse range of the chapter (OSIS query).
  2. Download each unique image via tile-stitched IIIF (Stanford IIIF 1.1 syntax).
  3. Pair the verse block with Tischendorf Greek (bolls.life) + KJV English
     (bible-api.com).
  4. Write a verified-washingtonianus-*.json matching the shape used for Vaticanus
     and Bezae; sync data/texts.json.

Criteria enforced (the strict rule set):
  - EVERY section links to the specific Freer folio image that contains the verses
    of that section (not a reused representative page).
  - original_text is verbatim Tischendorf public-domain Greek.
  - text is verbatim KJV public-domain English.
  - scan_pages is non-empty and points to files >10KB on disk.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PUB_DIR = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "washingtonianus"
SCAN_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "TheosisLibraryBot/1.0 (+https://theosislibrary.com)"
CSNTM_MS_ID = 206  # internal numeric ID for GA_032 on manuscripts.csntm.org
CSNTM_REFERER = "https://manuscripts.csntm.org/manuscript/View/GA_032"
IIIF_BASE = "https://images.csntm.org/iiifserver.ashx/GA_032"

# imageId → "GA_032_NNNN.jpg" — imageIds are contiguous starting at 140566
IMAGE_ID_BASE = 140565


def image_name_for(image_id: int) -> str:
    n = image_id - IMAGE_ID_BASE
    return f"GA_032_{n:04d}.jpg"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def _req(url: str, headers: dict | None = None, timeout: int = 30) -> urllib.request.Request:
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    return urllib.request.Request(url, headers=h)


def http_text(url: str, headers=None, timeout=30) -> str:
    return urllib.request.urlopen(_req(url, headers), timeout=timeout).read().decode(
        "utf-8", errors="replace"
    )


def http_json(url: str, headers=None, timeout=30):
    return json.loads(http_text(url, headers, timeout))


def http_bytes(url: str, headers=None, timeout=30) -> bytes:
    return urllib.request.urlopen(_req(url, headers), timeout=timeout).read()


# ---------------------------------------------------------------------------
# CSNTM OSIS → image-id lookup
# ---------------------------------------------------------------------------
def osis_lookup(book_osis: str, chapter: int, verse: int) -> list[int]:
    """Return the CSNTM image IDs for the leaf containing the given verse."""
    osis = f"{book_osis}.{chapter}.{verse}"
    url = (
        "https://manuscripts.csntm.org/manuscript/SearchForImageByOsis"
        f"?manuscriptId={CSNTM_MS_ID}&osis={urllib.parse.quote(osis)}"
    )
    try:
        return http_json(url, headers={"Referer": CSNTM_REFERER}, timeout=15)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# IIIF tile stitcher
# ---------------------------------------------------------------------------
def iiif_info(image_name: str) -> tuple[int, int, int]:
    """Return (width, height, tile_size) for an image."""
    url = f"{IIIF_BASE}/{image_name}/info.json"
    info = http_json(url, headers={"Referer": CSNTM_REFERER}, timeout=20)
    return int(info["width"]), int(info["height"]), int(info["tile_width"])


def _tile(image_name: str, x: int, y: int, w: int, h: int, target: int):
    url = f"{IIIF_BASE}/{image_name}/{x},{y},{w},{h}/{target},/0/native.jpg"
    return (x, y, http_bytes(url, headers={"Referer": CSNTM_REFERER}, timeout=30))


def download_image(image_name: str, dest: Path, scale: int = 2, workers: int = 6) -> Path:
    """Tile-stitch a CSNTM page into a single JPEG at 1/scale resolution."""
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest

    full_w, full_h, tile = iiif_info(image_name)
    out_w = full_w // scale
    out_h = full_h // scale
    tile_target = tile // scale
    # Region size in source coordinates, scale-aligned
    region = tile  # tiles cover `tile` × `tile` of source space

    canvas = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    coords = []
    y = 0
    py = 0
    while y < full_h:
        rh = min(region, full_h - y)
        target_h = rh // scale
        x = 0
        px = 0
        while x < full_w:
            rw = min(region, full_w - x)
            target_w = rw // scale
            coords.append((x, y, rw, rh, px, py, target_w, target_h))
            x += region
            px += tile_target
        y += region
        py += tile_target

    def fetch(args):
        sx, sy, sw, sh, px, py, tw, th = args
        url = f"{IIIF_BASE}/{image_name}/{sx},{sy},{sw},{sh}/{tw},/0/native.jpg"
        return (px, py, http_bytes(url, headers={"Referer": CSNTM_REFERER}, timeout=45))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(fetch, c) for c in coords]
        for fut in as_completed(futures):
            px, py, data = fut.result()
            im = Image.open(io.BytesIO(data))
            canvas.paste(im, (px, py))

    canvas.save(dest, "JPEG", quality=88, optimize=True)
    return dest


# ---------------------------------------------------------------------------
# Text fetchers (re-uses the same public-domain sources as import_verified.py)
# ---------------------------------------------------------------------------
STRONGS_RE = re.compile(r"<S>\d+</S>")


def clean_strongs(text: str) -> str:
    return STRONGS_RE.sub("", text or "").strip()


def fetch_tisch_chapter(bolls_book_num: int, chapter: int) -> list[dict]:
    url = f"https://bolls.life/get-chapter/TISCH/{bolls_book_num}/{chapter}/"
    return http_json(url, timeout=20)


def fetch_kjv_chapter(book_name: str, chapter: int) -> dict:
    url = f"https://bible-api.com/{urllib.parse.quote(book_name)}+{chapter}?translation=kjv"
    return http_json(url, timeout=20)


# ---------------------------------------------------------------------------
# Book definitions — W contains the four Gospels, Western order
# ---------------------------------------------------------------------------
GOSPELS = {
    # book_key → (osis, tisch bolls_book, bible-api name, chapter count, pretty)
    "matt": ("Matt", 40, "matthew", 28, "Matthew"),
    "john": ("John", 43, "john", 21, "John"),
    "luke": ("Luke", 42, "luke", 24, "Luke"),
    "mark": ("Mark", 41, "mark", 16, "Mark"),
}


# ---------------------------------------------------------------------------
# Per-chapter importer
# ---------------------------------------------------------------------------
def section_group_size(num_verses: int) -> int:
    if num_verses <= 20:
        return 5
    if num_verses <= 40:
        return 8
    return 10


def import_chapter(book_key: str, chapter: int, force: bool = False, delay: float = 0.5):
    osis, bolls, api_name, max_ch, pretty = GOSPELS[book_key]
    tid = f"verified-washingtonianus-{book_key}-{chapter}"
    pub_path = PUB_DIR / f"{tid}.json"
    if pub_path.exists() and not force:
        return ("skip", tid)

    print(f"  [{tid}] {pretty} {chapter}...")

    # 1. Fetch Greek + English chapters
    try:
        greek = fetch_tisch_chapter(bolls, chapter)
    except Exception as e:
        return ("fail", f"{tid}: Greek fetch failed: {e}")
    try:
        kjv = fetch_kjv_chapter(api_name, chapter)
    except Exception as e:
        return ("fail", f"{tid}: KJV fetch failed: {e}")
    if not greek or not kjv.get("verses"):
        return ("fail", f"{tid}: missing Greek or KJV verses")

    greek_by = {v["verse"]: v for v in greek}
    kjv_by = {v["verse"]: v for v in kjv["verses"]}
    verses = sorted(set(greek_by) | set(kjv_by))
    group = section_group_size(len(verses))

    # 2. Build sections (verse-range buckets); for each bucket, ask CSNTM for
    #    the imageIds covering the starting verse. CSNTM returns [id] or
    #    [id1, id2] when a verse straddles a folio.
    sections = []
    image_ids_seen: list[int] = []
    for i in range(0, len(verses), group):
        nums = verses[i : i + group]
        sv, ev = nums[0], nums[-1]
        ref = f"{sv}-{ev}" if sv != ev else str(sv)

        # For each verse in this group, collect covering imageIds. Deduplicate
        # while preserving order.
        section_image_ids: list[int] = []
        for v in nums:
            for iid in osis_lookup(osis, chapter, v):
                if iid not in section_image_ids:
                    section_image_ids.append(iid)
            time.sleep(0.05)
        if not section_image_ids:
            return ("fail", f"{tid}: no Freer image for {osis} {chapter}:{sv}")
        for iid in section_image_ids:
            if iid not in image_ids_seen:
                image_ids_seen.append(iid)

        greek_text = " ".join(
            f'<sup>{n}</sup>{clean_strongs(greek_by[n].get("text", ""))}'
            for n in nums
            if n in greek_by
        )
        english_text = " ".join(
            f'<sup>{n}</sup>{(kjv_by[n].get("text") or "").strip()}'
            for n in nums
            if n in kjv_by
        )

        scan_paths = [
            f"washingtonianus/{pretty.lower()}-{chapter}-{image_name_for(iid).replace('.jpg','')}.jpg"
            for iid in section_image_ids
        ]
        sections.append(
            {
                "section": f"{chapter}.{ref}",
                "original_ref": f"{pretty} {chapter}:{ref}",
                "original_text": greek_text,
                "text": english_text,
                "scan_pages": scan_paths,
            }
        )
        time.sleep(delay)

    # 3. Download each unique image via tile-stitching
    image_name_for_id = {iid: image_name_for(iid) for iid in image_ids_seen}
    for iid in image_ids_seen:
        image_name = image_name_for_id[iid]
        local_name = f"{pretty.lower()}-{chapter}-{image_name.replace('.jpg','')}.jpg"
        dest = SCAN_DIR / local_name
        try:
            download_image(image_name, dest, scale=2, workers=6)
        except Exception as e:
            return ("fail", f"{tid}: scan download {image_name} failed: {e}")
        if not dest.exists() or dest.stat().st_size < 10_000:
            return ("fail", f"{tid}: scan {image_name} empty or too small")

    # 4. Assemble the published JSON
    today = str(date.today())
    entry = {
        "id": tid,
        "title": f"{pretty}, Chapter {chapter} (Codex Washingtonianus)",
        "slug": tid,
        "language": "Greek (Tischendorf) / English (KJV)",
        "source": "Codex Washingtonianus (Freer Gospels, 4th-5th c.) via CSNTM IIIF + Tischendorf + KJV",
        "description": (
            f"{pretty} chapter {chapter} from Codex Washingtonianus (Freer Gallery of Art, F1906.274; "
            f"GA 032, 4th-5th c.). Manuscript scans via the Center for the Study of New Testament "
            f"Manuscripts (CSNTM). Greek text verbatim from Tischendorf's 8th critical edition "
            f"(1869) via bolls.life. English translation verbatim from the King James Version (1611) "
            f"via bible-api.com."
        ),
        "introduction": (
            f"<p><strong>Codex Washingtonianus</strong> (Freer Gospels, GA 032) is the third-oldest "
            f"near-complete Greek manuscript of the four Gospels, dated to the late 4th or early "
            f"5th century. It contains the Gospels in the Western order (Matthew, John, Luke, Mark) "
            f"and is famous for the Freer Logion, a unique expansion at the end of Mark 16. Purchased "
            f"by Charles Lang Freer in Egypt in 1906 and now held at the Smithsonian's Freer Gallery "
            f"of Art in Washington, D.C.</p>"
            f"<p>This entry pairs the actual Freer folio scan with verbatim Tischendorf Greek and "
            f"the King James Version English — no paraphrase, no AI generation.</p>"
        ),
        "translation": sections,
        "translator_notes": [],
        "verification": {
            "scan_source": "Center for the Study of New Testament Manuscripts (CSNTM) IIIF",
            "scan_license": "CSNTM non-commercial scholarly use",
            "scan_manuscript": "Codex Washingtonianus (F1906.274, Smithsonian Freer Gallery)",
            "scan_mapping": "CSNTM verse-to-image lookup (SearchForImageByOsis API)",
            "scan_local_paths": [s for sec in sections for s in sec["scan_pages"]],
            "original_text_source": "bolls.life (TISCH = Tischendorf 8)",
            "original_text_license": "public domain (1869)",
            "translation_source": "bible-api.com (KJV)",
            "translation_license": "public domain (1611)",
            "verified_date": today,
        },
    }
    pub_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return ("ok", tid)


# ---------------------------------------------------------------------------
# data/texts.json sync
# ---------------------------------------------------------------------------
def sync_texts_json(imported_ids: list[str]):
    data_path = DATA_DIR / "texts.json"
    d = json.loads(data_path.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in d["texts"]}
    for tid in imported_ids:
        pub_path = PUB_DIR / f"{tid}.json"
        if not pub_path.exists():
            continue
        pub = json.loads(pub_path.read_text(encoding="utf-8"))
        first_scan = pub["verification"]["scan_local_paths"][0]
        meta = {
            "id": tid,
            "title": pub["title"],
            "author_id": "biblical-authors",
            "language": pub["language"],
            "era": "Apostolic",
            "tradition": "orthodox",
            "category": "sacred-text",
            "date_approx": "c. 50-100 AD (composition); 4th-5th c. (Codex Washingtonianus)",
            "century": 1,
            "source": pub["source"],
            "description": pub["description"],
            "themes": [
                "bible",
                "new-testament",
                "washingtonianus",
                "freer-gospels",
                "verified",
            ],
            "is_first_translation": False,
            "status": "published",
            "slug": tid,
            "scans": {"pages": [{"file": first_scan, "caption": "Codex Washingtonianus (Freer Gospels)"}]},
        }
        by_id[tid] = meta
    d["texts"] = list(by_id.values())
    data_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  texts.json now has {len(d['texts'])} entries")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=str, default="", help="matt|mark|luke|john (omit = all)")
    parser.add_argument("--chapter", type=int, default=0, help="single chapter (requires --book)")
    parser.add_argument("--limit", type=int, default=0, help="cap number of chapters")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--delay", type=float, default=0.5)
    args = parser.parse_args()

    todo: list[tuple[str, int]] = []
    if args.book and args.chapter:
        todo = [(args.book, args.chapter)]
    elif args.book:
        _, _, _, max_ch, _ = GOSPELS[args.book]
        todo = [(args.book, ch) for ch in range(1, max_ch + 1)]
    else:
        # Western order on the manuscript, but matters only for UX grouping.
        for b in ("matt", "john", "luke", "mark"):
            _, _, _, max_ch, _ = GOSPELS[b]
            for ch in range(1, max_ch + 1):
                todo.append((b, ch))
    if args.limit:
        todo = todo[: args.limit]

    print(f"Plan: import {len(todo)} chapters from Codex Washingtonianus")
    imported, skipped, failed = [], [], []
    for (book, ch) in todo:
        status, msg = import_chapter(book, ch, force=args.force, delay=args.delay)
        if status == "ok":
            imported.append(msg)
        elif status == "skip":
            skipped.append(msg)
        else:
            print(f"    FAIL: {msg}")
            failed.append(msg)
        time.sleep(args.delay)

    print()
    print(f"Imported: {len(imported)}")
    print(f"Skipped (already exist): {len(skipped)}")
    print(f"Failed: {len(failed)}")
    for f in failed:
        print(f"  {f}")

    if imported:
        sync_texts_json(imported)


if __name__ == "__main__":
    main()
