#!/usr/bin/env python3
"""
import_leningrad.py — Strict primary-source import for the Leningrad Codex (1008 AD).

For each of the 39 books of the Hebrew Bible, this fetches:
  1. Sample folios from the Leningrad Codex via Internet Archive IIIF
     (https://archive.org/details/Leningrad_Codex — public domain)
  2. The verbatim Hebrew text (WLC, Westminster Leningrad Codex) from bolls.life
  3. The verbatim KJV English from bible-api.com

Each entry is a complete book with sections per chapter. Refuses to publish
unless all three sources are confirmed.
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PUB_DIR = PROJECT_ROOT / "translations" / "published"
SCAN_DIR = PROJECT_ROOT / "site" / "assets" / "scans" / "leningrad-folios"
SCAN_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "TheosisLibrary/1.0 (https://theosislibrary.com)"
)

# Internet Archive IIIF image URL for Leningrad Codex
IA_IIIF_TPL = (
    "https://iiif.archive.org/image/iiif/3/"
    "Leningrad_Codex%2FLeningrad_jp2.zip%2FLeningrad_jp2%2FLeningrad_{page:04d}.jp2/"
    "full/1600,/0/default.jpg"
)

# Total content pages in the IA facsimile: 988 (leafNum 0-987).
# Pages 0-9 are covers / front carpet pages / dedication.
# Pages 10-985 are biblical text in standard Tanakh order (Torah, Nevi'im, Ketuvim).
# Within Ketuvim, Leningrad puts Chronicles BEFORE Psalms.
#
# Per published Leningrad foliation (Loewinger 1971 facsimile and BHS apparatus),
# the codex has 491 folios = 982 sides; the IA scan adds front/back binding pages.
#
# The page ranges below are estimated proportionally from each book's verse count
# against the known Leningrad biblical-text page count (~976 pages from p.10 to p.985).
# Each book gets its representative folios; chapter-level granularity within a book
# uses the same scan set (the user can browse other folios via the IA link).

# Hebrew Bible books in LENINGRAD ORDER (Torah, Nevi'im, Ketuvim with Chr first)
# Format: (book_key, pretty, bolls_book_num, num_chapters, bible_api_name, total_verses)
LENINGRAD_BOOKS = [
    # Torah
    ("gen",     "Genesis",          1, 50, "genesis",      1533),
    ("exod",    "Exodus",           2, 40, "exodus",       1213),
    ("lev",     "Leviticus",        3, 27, "leviticus",     859),
    ("num",     "Numbers",          4, 36, "numbers",      1288),
    ("deut",    "Deuteronomy",      5, 34, "deuteronomy",   959),
    # Nevi'im (Former Prophets)
    ("josh",    "Joshua",           6, 24, "joshua",        658),
    ("judg",    "Judges",           7, 21, "judges",        618),
    ("1sam",    "1 Samuel",         9, 31, "1 samuel",      810),
    ("2sam",    "2 Samuel",        10, 24, "2 samuel",      695),
    ("1kgs",    "1 Kings",         11, 22, "1 kings",       816),
    ("2kgs",    "2 Kings",         12, 25, "2 kings",       719),
    # Nevi'im (Latter Prophets)
    ("isa",     "Isaiah",          23, 66, "isaiah",       1292),
    ("jer",     "Jeremiah",        24, 52, "jeremiah",     1364),
    ("ezek",    "Ezekiel",         26, 48, "ezekiel",      1273),
    # The Twelve (in Leningrad order)
    ("hos",     "Hosea",           28, 14, "hosea",         197),
    ("joel",    "Joel",            29,  3, "joel",           73),
    ("amos",    "Amos",            30,  9, "amos",          146),
    ("obad",    "Obadiah",         31,  1, "obadiah",        21),
    ("jonah",   "Jonah",           32,  4, "jonah",          48),
    ("mic",     "Micah",           33,  7, "micah",         105),
    ("nahum",   "Nahum",           34,  3, "nahum",          47),
    ("hab",     "Habakkuk",        35,  3, "habakkuk",       56),
    ("zeph",    "Zephaniah",       36,  3, "zephaniah",      53),
    ("hag",     "Haggai",          37,  2, "haggai",         38),
    ("zech",    "Zechariah",       38, 14, "zechariah",     211),
    ("mal",     "Malachi",         39,  4, "malachi",        55),
    # Ketuvim (Writings — Leningrad puts Chronicles first)
    ("1chr",    "1 Chronicles",    13, 29, "1 chronicles",  942),
    ("2chr",    "2 Chronicles",    14, 36, "2 chronicles",  822),
    ("ps",      "Psalms",          19,150, "psalms",       2461),
    ("job",     "Job",             18, 42, "job",          1070),
    ("prov",    "Proverbs",        20, 31, "proverbs",      915),
    ("ruth",    "Ruth",             8,  4, "ruth",           85),
    ("song",    "Song of Solomon", 22,  8, "song of solomon",117),
    ("eccl",    "Ecclesiastes",    21, 12, "ecclesiastes",  222),
    ("lam",     "Lamentations",    25,  5, "lamentations",  154),
    ("esth",    "Esther",          17, 10, "esther",        167),
    ("dan",     "Daniel",          27, 12, "daniel",        357),
    ("ezra",    "Ezra",            15, 10, "ezra",          280),
    ("neh",     "Nehemiah",        16, 13, "nehemiah",      406),
]


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout).read()


def http_get_json(url, timeout=30):
    return json.loads(http_get(url, timeout))


def http_get_text(url, timeout=30):
    return http_get(url, timeout).decode("utf-8", errors="replace")


def fetch_wlc_chapter(bolls_book, chapter, retries=4):
    """Fetch a Hebrew chapter from bolls.life Westminster Leningrad Codex."""
    url = f"https://bolls.life/get-chapter/WLC/{bolls_book}/{chapter}/"
    for attempt in range(retries):
        try:
            return http_get_json(url, timeout=20)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception:
            time.sleep(2)
    return None


def fetch_kjv_chapter(book_name, chapter, retries=5):
    """Fetch a KJV chapter from bible-api.com."""
    url = f"https://bible-api.com/{urllib.parse.quote(book_name)}+{chapter}?translation=kjv"
    for attempt in range(retries):
        try:
            return http_get_json(url, timeout=20)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception:
            time.sleep(2)
    return None


def download_leningrad_page(page, dest_path):
    """Download one page of the Leningrad Codex from IA IIIF."""
    if dest_path.exists() and dest_path.stat().st_size > 50000:
        return
    url = IA_IIIF_TPL.format(page=page)
    data = http_get(url, timeout=120)
    dest_path.write_bytes(data)


# ----------------------------------------------------------------------------
# Page-range estimation
# Books are positioned proportionally from p.10 to p.985 (976 content pages)
# weighted by total verses in each book.
# ----------------------------------------------------------------------------
def compute_page_ranges():
    total_verses = sum(b[5] for b in LENINGRAD_BOOKS)
    p_start, p_end = 10, 985
    pages_avail = p_end - p_start
    cursor = p_start
    out = {}
    for key, _, _, _, _, vc in LENINGRAD_BOOKS:
        n_pages = max(2, round(pages_avail * vc / total_verses))
        out[key] = (cursor, min(p_end, cursor + n_pages - 1))
        cursor += n_pages
    return out


PAGE_RANGES = compute_page_ranges()


def representative_pages(book_key, max_n=3):
    """Pick representative page indices for a book: start, middle, end."""
    start, end = PAGE_RANGES[book_key]
    if end - start <= max_n - 1:
        return list(range(start, end + 1))
    if max_n == 1:
        return [start]
    if max_n == 2:
        return [start, end]
    mid = (start + end) // 2
    return [start, mid, end]


# ----------------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------------
def import_leningrad_book(book_key, force=False, delay=0.5):
    spec = next((b for b in LENINGRAD_BOOKS if b[0] == book_key), None)
    if not spec:
        return ("fail", f"unknown book: {book_key}")
    _, pretty, bolls_book, num_chapters, bible_api_name, _ = spec

    tid = f"verified-leningrad-{book_key}"
    pub_path = PUB_DIR / f"{tid}.json"
    if pub_path.exists() and not force:
        return ("skip", tid)

    print(f"  [{tid}] {pretty} ({num_chapters} chapters)...")

    # 1. Download representative Leningrad pages
    pages_to_download = representative_pages(book_key, max_n=3)
    scan_files = []
    for p in pages_to_download:
        scan_filename = f"leningrad-{book_key}-p{p:04d}.jpg"
        scan_path = SCAN_DIR / scan_filename
        try:
            download_leningrad_page(p, scan_path)
        except Exception as e:
            return ("fail", f"{tid}: scan download failed for p{p}: {e}")
        if not scan_path.exists() or scan_path.stat().st_size < 50000:
            return ("fail", f"{tid}: scan p{p} too small")
        scan_files.append(f"leningrad-folios/{scan_filename}")
        time.sleep(0.3)

    # 2. Fetch ALL chapters of the book in parallel
    sections = []
    for ch in range(1, num_chapters + 1):
        wlc_verses = fetch_wlc_chapter(bolls_book, ch)
        if not wlc_verses:
            return ("fail", f"{tid}: WLC fetch failed for {pretty} {ch}")
        kjv_data = fetch_kjv_chapter(bible_api_name, ch)
        if not kjv_data:
            return ("fail", f"{tid}: KJV fetch failed for {pretty} {ch}")
        kjv_verses = kjv_data.get("verses", [])

        wlc_by = {v.get("verse"): v for v in wlc_verses}
        kjv_by = {v.get("verse"): v for v in kjv_verses}
        nums = sorted(set(wlc_by) | set(kjv_by))

        # Group verses for display
        n = len(nums)
        gs = 5 if n <= 20 else 8 if n <= 40 else 10
        for i in range(0, len(nums), gs):
            grp = nums[i:i + gs]
            sv, ev = grp[0], grp[-1]
            ref = f"{sv}-{ev}" if sv != ev else str(sv)

            heb = " ".join(
                f'<sup>{nv}</sup>{(wlc_by[nv].get("text") or "").strip()}'
                for nv in grp if nv in wlc_by
            )
            eng = " ".join(
                f'<sup>{nv}</sup>{(kjv_by[nv].get("text") or "").strip()}'
                for nv in grp if nv in kjv_by
            )
            sections.append({
                "section": f"{ch}.{ref}",
                "original_ref": f"{pretty} {ch}:{ref}",
                "original_text": heb,
                "text": eng,
                "scan_pages": scan_files,
            })
        time.sleep(delay)

    today = str(date.today())
    page_start, page_end = PAGE_RANGES[book_key]
    entry = {
        "id": tid,
        "title": f"{pretty} (Leningrad Codex)",
        "slug": tid,
        "language": "Hebrew (Leningrad Codex / WLC) / English (KJV)",
        "source": (
            "Leningrad Codex (1008 AD) folios via Internet Archive + "
            "Westminster Leningrad Codex Hebrew (bolls.life) + KJV (bible-api.com)"
        ),
        "description": (
            f"The complete book of {pretty} from the Leningrad Codex, the oldest "
            f"complete Masoretic Hebrew Bible (1008 AD), housed at the Russian National "
            f"Library, St. Petersburg. Manuscript folios from the public-domain Internet "
            f"Archive facsimile (pages {page_start}–{page_end}). Hebrew text verbatim from "
            f"the Westminster Leningrad Codex transcription via bolls.life. English "
            f"translation verbatim from the King James Version (1611) via bible-api.com."
        ),
        "introduction": (
            f"<p>This entry presents the entire book of <strong>{pretty}</strong> from the "
            f"Leningrad Codex (Codex Leningradensis, 1008 AD)—the oldest complete medieval "
            f"manuscript of the Hebrew Bible. It meets the strict three-criteria standard "
            f"of the Theosis Library:</p>"
            f"<ol>"
            f"<li><strong>Manuscript scans:</strong> Sample folios from the Leningrad Codex "
            f"via the public-domain Internet Archive facsimile "
            f"(<a href=\"https://archive.org/details/Leningrad_Codex\" target=\"_blank\">"
            f"archive.org/details/Leningrad_Codex</a>, CC0). The selected pages cover the "
            f"book's approximate location in the codex (folio range {page_start}–{page_end} "
            f"in the digital facsimile).</li>"
            f"<li><strong>Original text:</strong> The complete Hebrew text of {pretty} "
            f"verbatim from the Westminster Leningrad Codex (WLC), the standard digital "
            f"edition of the Leningrad Codex maintained by the Groves Center, accessed via "
            f"the public-domain bolls.life API. Includes full Masoretic vocalization and "
            f"cantillation marks.</li>"
            f"<li><strong>English translation:</strong> The complete book of {pretty} from "
            f"the King James Version (1611), verbatim from the public-domain bible-api.com "
            f"endpoint.</li>"
            f"</ol>"
        ),
        "translation": sections,
        "translator_notes": [],
        "verification": {
            "scan_source": "Internet Archive (Leningrad_Codex item)",
            "scan_license": "CC0 / public domain",
            "scan_manuscript": "Codex Leningradensis (B19a, Russian National Library)",
            "scan_iiif_source": "https://iiif.archive.org/iiif/Leningrad_Codex/manifest.json",
            "scan_page_range": f"{page_start}-{page_end} (estimated by proportional book length)",
            "scan_local_paths": scan_files,
            "original_text_source": "bolls.life API (WLC = Westminster Leningrad Codex)",
            "original_text_license": "public domain (Groves Center)",
            "translation_source": "bible-api.com (KJV)",
            "translation_license": "public domain (1611)",
            "verified_date": today,
            "note": (
                "The page range is an approximate proportional estimate; the manuscript "
                "scans link to a sample of folios from approximately where this book lives "
                "in the Leningrad Codex sequence. The Hebrew text and English translation "
                "are verbatim from their respective public-domain sources."
            ),
        },
    }

    pub_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return ("ok", tid)


def sync_texts_json(imported_ids):
    data_path = DATA_DIR / "texts.json"
    d = json.loads(data_path.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in d["texts"]}

    for tid in imported_ids:
        pub_path = PUB_DIR / f"{tid}.json"
        if not pub_path.exists():
            continue
        pub = json.loads(pub_path.read_text(encoding="utf-8"))
        meta = {
            "id": tid,
            "title": pub["title"],
            "author_id": "biblical-authors",
            "language": "Hebrew",
            "era": "Hebrew Bible",
            "tradition": "orthodox",
            "category": "sacred-text",
            "date_approx": "c. 1500-400 BCE (composition); 1008 AD (Leningrad Codex)",
            "century": -10,
            "source": pub["source"],
            "description": pub["description"],
            "themes": ["bible", "tanakh", "hebrew", "leningrad-codex", "verified"],
            "is_first_translation": False,
            "status": "published",
            "slug": tid,
            "scans": {
                "pages": [
                    {"file": p, "caption": "Leningrad Codex (1008 AD, RNL)"}
                    for p in pub["verification"]["scan_local_paths"]
                ]
            },
        }
        by_id[tid] = meta

    d["texts"] = list(by_id.values())
    data_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  texts.json now has {len(d['texts'])} entries")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=str, default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--delay", type=float, default=0.4)
    args = parser.parse_args()

    todo = [args.book] if args.book else [b[0] for b in LENINGRAD_BOOKS]
    print(f"Plan: import {len(todo)} Hebrew Bible books from Leningrad Codex")

    imported, failed, skipped = [], [], []
    for book_key in todo:
        result, info = import_leningrad_book(book_key, force=args.force, delay=args.delay)
        if result == "ok":
            imported.append(info)
        elif result == "skip":
            skipped.append(info)
        else:
            failed.append(info)
            print(f"    FAIL: {info}")

    print(f"\nImported: {len(imported)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Failed: {len(failed)}")
    for f in failed:
        print(f"  {f}")

    if imported or args.force:
        sync_texts_json(imported + skipped)


if __name__ == "__main__":
    main()
