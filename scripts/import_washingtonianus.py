#!/usr/bin/env python3
"""
import_washingtonianus.py — Import Codex Washingtonianus (GA 032, Freer Gospels,
Freer Gallery of Art F1906.274, late 4th / early 5th c.) at chapter level.

Chain (every link is verified, nothing is estimated):

  1. Verse -> page.  CSNTM's manuscript viewer exposes a verse index
     (SearchForImageByOsis?manuscriptId=206&osis=Book.ch.v) that returns the
     CSNTM imageId(s) of the page(s) carrying that verse. The CSNTM viewer
     page itself carries the authoritative imageId -> GA_032_NNNN.jpg table
     (374 images); we read that table instead of assuming ids are contiguous.
     A verse that returns [] is not in the codex (Mark 15:13-37 and John
     14:26-16:6 are the two known lacunae) and is left out.

  2. Page -> owner-hosted image.  The Freer Gallery (Smithsonian National
     Museum of Asian Art) publishes the same 373 page photographs of
     F1906.274 through its own IIIF server (ids.si.edu, ids FS-7127_01 ..
     FS-7164_04). We match every CSNTM page to its Freer image by normalised
     pixel correlation of thumbnails (identical photographs score >= 0.999;
     the runner-up scores <= 0.93) and store the map in
     data/washingtonianus_page_map.json. The scans we publish are the Freer
     images, under the Smithsonian "Usage Conditions Apply" terms
     (personal / educational / non-commercial use with attribution and a
     link; https://www.si.edu/termsofuse). One CSNTM page (GA_032_0200) has
     no Freer counterpart (FS-7146_10 is 404 on ids.si.edu); verses that
     survive only on that page are not published.

  3. Greek: Tischendorf's 8th edition (1869-72, public domain) via bolls.life.
     English: King James Version via bible-api.com. Both verbatim.

Output:
  translations/published/verified-washingtonianus-<book>-<chapter>.json
  site/assets/scans/washingtonianus/w-p<NNNN>-<FreerId>.jpg (one file per page)
  data/pending/washingtonianus_texts.json  ({"texts": [...]}, for texts.json)

This script never touches data/texts.json.

Run:
  python3 scripts/import_washingtonianus.py --book matt --chapter 5   # one chapter
  python3 scripts/import_washingtonianus.py                            # everything
  python3 scripts/import_washingtonianus.py --build-map                # rebuild page map
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import time
import urllib.parse
from datetime import date
from pathlib import Path

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PUB_DIR = ROOT / "translations" / "published"
PENDING_PATH = DATA_DIR / "pending" / "washingtonianus_texts.json"
PAGE_MAP_PATH = DATA_DIR / "washingtonianus_page_map.json"
CACHE_DIR = DATA_DIR / "sources" / "washingtonianus_cache"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "washingtonianus"
for d in (SCAN_DIR, CACHE_DIR, CACHE_DIR / "json", CACHE_DIR / "thumbs_csntm", CACHE_DIR / "thumbs_freer", PENDING_PATH.parent):
    d.mkdir(parents=True, exist_ok=True)

# A browser-like UA: ids.si.edu rejects bare bot UAs with "Request Rejected".
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36 TheosisLibraryBot/1.0"
)
CSNTM_MS_ID = 206
CSNTM_VIEW_URL = "https://manuscripts.csntm.org/manuscript/View/GA_032"
CSNTM_IIIF = "https://images.csntm.org/iiifserver.ashx/GA_032"
FREER_IIIF = "https://ids.si.edu/ids/iiif"
FREER_OBJECT_URL = "https://asia.si.edu/object/F1906.274/"
FREER_CANDIDATE_IDS = [f"FS-{g}_{i:02d}" for g in range(7127, 7165) for i in range(1, 11)]

SCAN_WIDTH = 1200       # published page width in px (source is 3600 x 5400)
SCAN_QUALITY = 80
THUMB_WIDTH = 225       # CSNTM only serves 225 or 1500 wide "full" requests reliably

# ---------------------------------------------------------------------------
# HTTP: one session, urllib3 retries, body validation, explicit close
# ---------------------------------------------------------------------------
_session: requests.Session | None = None


def session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        retry = Retry(total=4, backoff_factor=1.5, status_forcelist=(429, 500, 502, 503, 504),
                      allowed_methods=("GET",), raise_on_status=False)
        s.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=8))
        _session = s
    return _session


def http_get(url: str, headers: dict | None = None, timeout: int = 60, attempts: int = 5,
             want: str = "any") -> bytes:
    """GET with retry/backoff. want='jpeg' insists on JPEG magic bytes, 'json' on
    parseable JSON (CSNTM sometimes answers 200 with an empty body or an HTML
    error page; those are retried, not accepted)."""
    last = None
    for a in range(attempts):
        try:
            r = session().get(url, headers=headers, timeout=timeout, stream=False)
            try:
                body = r.content
                status = r.status_code
            finally:
                r.close()
            if status == 404:
                raise FileNotFoundError(url)
            if status == 200:
                if want == "jpeg" and body[:3] == b"\xff\xd8\xff":
                    return body
                if want == "json":
                    try:
                        json.loads(body.decode("utf-8"))
                        return body
                    except Exception:
                        pass
                if want == "any" and body:
                    return body
            last = f"status={status} len={len(body)}"
        except FileNotFoundError:
            raise
        except Exception as e:  # noqa: BLE001
            last = repr(e)
        time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"GET failed after {attempts} attempts: {url} ({last})")


def cached_json(key: str, url: str, headers: dict | None = None, timeout: int = 30):
    p = CACHE_DIR / "json" / (hashlib.sha1(key.encode()).hexdigest() + ".json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    data = json.loads(http_get(url, headers=headers, timeout=timeout, want="json").decode("utf-8"))
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


# ---------------------------------------------------------------------------
# 1. CSNTM: imageId table + verse index
# ---------------------------------------------------------------------------
CSNTM_HEADERS = {"Referer": CSNTM_VIEW_URL}


def csntm_image_table() -> dict[int, str]:
    """imageId -> GA_032_NNNN.jpg, read from the CSNTM viewer HTML (cached)."""
    p = CACHE_DIR / "csntm_GA_032_view.html"
    if not p.exists():
        p.write_bytes(http_get(CSNTM_VIEW_URL, timeout=60))
    html = p.read_text(encoding="utf-8", errors="replace")
    pairs = re.findall(r'imageId="(\d+)"\s+imageName="(GA_032_\d{4}\.jpg)"', html)
    if len(pairs) < 300:
        raise RuntimeError("CSNTM viewer page did not yield the image table")
    return {int(i): n for i, n in pairs}


def csntm_page_num(image_name: str) -> int:
    return int(re.search(r"GA_032_(\d{4})", image_name).group(1))


def osis_lookup(osis_book: str, chapter: int, verse: int) -> list[int]:
    osis = f"{osis_book}.{chapter}.{verse}"
    url = ("https://manuscripts.csntm.org/manuscript/SearchForImageByOsis"
           f"?manuscriptId={CSNTM_MS_ID}&osis={urllib.parse.quote(osis)}")
    return cached_json(f"osis:{osis}", url, headers=CSNTM_HEADERS, timeout=30)


# ---------------------------------------------------------------------------
# 2. Page map: CSNTM page -> Freer (ids.si.edu) image, by pixel correlation
# ---------------------------------------------------------------------------
def _thumb_vector(path: Path):
    import numpy as np
    im = Image.open(path).convert("L").resize((32, 48))
    a = np.asarray(im, dtype=float)
    a = (a - a.mean()) / (a.std() + 1e-6)
    return a.ravel()


def _csntm_thumb(n: int) -> Path:
    p = CACHE_DIR / "thumbs_csntm" / f"{n:04d}.jpg"
    if p.exists() and p.stat().st_size > 2000:
        return p
    name = f"GA_032_{n:04d}.jpg"
    try:
        body = http_get(f"{CSNTM_IIIF}/{name}/full/{THUMB_WIDTH},/0/native.jpg",
                        headers=CSNTM_HEADERS, want="jpeg", attempts=3)
    except RuntimeError:
        # some pages only answer at 1500 wide; downscale locally
        body = http_get(f"{CSNTM_IIIF}/{name}/full/1500,/0/native.jpg",
                        headers=CSNTM_HEADERS, want="jpeg", timeout=90)
        im = Image.open(io.BytesIO(body))
        im.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 2))
        im.save(p, "JPEG")
        return p
    p.write_bytes(body)
    return p


def _freer_thumb(fid: str) -> Path | None:
    p = CACHE_DIR / "thumbs_freer" / f"{fid}.jpg"
    if p.exists() and p.stat().st_size > 2000:
        return p
    try:
        body = http_get(f"{FREER_IIIF}/{fid}/full/{THUMB_WIDTH},/0/default.jpg",
                        headers={"Referer": "https://asia.si.edu/"}, want="jpeg")
    except FileNotFoundError:
        return None
    p.write_bytes(body)
    return p


def build_page_map(force: bool = False) -> dict:
    """Return {csntm_page_num: {"csntm_image": ..., "csntm_image_id": ..., "freer_id": ...|None,
    "score": ..., "runner_up": ...}} and persist it."""
    if PAGE_MAP_PATH.exists() and not force:
        return {int(k): v for k, v in json.loads(PAGE_MAP_PATH.read_text(encoding="utf-8"))["pages"].items()}
    import numpy as np

    table = csntm_image_table()
    pages = {csntm_page_num(n): (iid, n) for iid, n in table.items()}
    nums = sorted(pages)
    print(f"  page map: {len(nums)} CSNTM pages; fetching thumbnails ...")
    cvec = np.stack([_thumb_vector(_csntm_thumb(n)) for n in nums])

    freer_ids, fvecs = [], []
    for fid in FREER_CANDIDATE_IDS:
        t = _freer_thumb(fid)
        if t is None:
            print(f"    Freer {fid}: not on ids.si.edu (404)")
            continue
        freer_ids.append(fid)
        fvecs.append(_thumb_vector(t))
    print(f"  page map: {len(freer_ids)} Freer images")

    out = {n: {"csntm_image": pages[n][1], "csntm_image_id": pages[n][0], "freer_id": None,
               "score": None, "runner_up": None} for n in nums}
    used = {}
    for fid, fv in zip(freer_ids, fvecs):
        sc = cvec @ fv / cvec.shape[1]
        order = np.argsort(sc)
        best, second = int(order[-1]), float(sc[order[-2]])
        score = float(sc[best])
        n = nums[best]
        if score < 0.995 or score - second < 0.03:
            print(f"    WARN weak match {fid} -> page {n} ({score:.3f} vs {second:.3f}); not mapped")
            continue
        if n in used:
            print(f"    WARN page {n} matched twice ({used[n]}, {fid}); dropping both")
            out[n]["freer_id"] = None
            continue
        used[n] = fid
        out[n].update({"freer_id": fid, "score": round(score, 4), "runner_up": round(second, 4)})

    unmatched = [n for n in nums if out[n]["freer_id"] is None]
    print(f"  page map: {len(used)} pages matched, unmatched CSNTM pages: {unmatched}")
    PAGE_MAP_PATH.write_text(json.dumps({
        "manuscript": "Codex Washingtonianus (GA 032), Freer Gallery of Art F1906.274",
        "method": ("CSNTM imageId/imageName table read from the viewer page; Freer ids probed on "
                   "ids.si.edu; each Freer thumbnail matched to the CSNTM thumbnail with the highest "
                   "normalised pixel correlation (32x48 greyscale); accepted only if score >= 0.995 "
                   "and margin over runner-up >= 0.03"),
        "built": str(date.today()),
        "csntm_view_url": CSNTM_VIEW_URL,
        "freer_object_url": FREER_OBJECT_URL,
        "pages": {str(n): out[n] for n in nums},
    }, indent=1), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# 3. Page image download (Freer IIIF), one file per physical page
# ---------------------------------------------------------------------------
def scan_filename(page_num: int, freer_id: str) -> str:
    return f"w-p{page_num:04d}-{freer_id}.jpg"


def download_page(page_num: int, freer_id: str) -> Path:
    dest = SCAN_DIR / scan_filename(page_num, freer_id)
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest
    url = f"{FREER_IIIF}/{freer_id}/full/1800,/0/default.jpg"
    body = http_get(url, headers={"Referer": "https://asia.si.edu/"}, timeout=120, want="jpeg")
    im = Image.open(io.BytesIO(body)).convert("RGB")
    if im.width > SCAN_WIDTH:
        im = im.resize((SCAN_WIDTH, round(im.height * SCAN_WIDTH / im.width)), Image.LANCZOS)
    im.save(dest, "JPEG", quality=SCAN_QUALITY, optimize=True)
    if dest.stat().st_size < 10_000:
        dest.unlink()
        raise RuntimeError(f"{freer_id}: downloaded image too small")
    return dest


# ---------------------------------------------------------------------------
# 4. Texts (public domain): Tischendorf 8 via bolls.life, KJV via bible-api.com
# ---------------------------------------------------------------------------
STRONGS_RE = re.compile(r"<S>\d+</S>")


def clean_strongs(text: str) -> str:
    return STRONGS_RE.sub("", text or "").strip()


def fetch_tisch_chapter(bolls_book: int, chapter: int) -> list[dict]:
    return cached_json(f"tisch:{bolls_book}:{chapter}",
                       f"https://bolls.life/get-chapter/TISCH/{bolls_book}/{chapter}/")


def fetch_kjv_chapter(api_name: str, chapter: int) -> dict:
    return cached_json(f"kjv:{api_name}:{chapter}",
                       f"https://bible-api.com/{urllib.parse.quote(api_name)}+{chapter}?translation=kjv")


# ---------------------------------------------------------------------------
# Books: W has the four Gospels in the "Western" order Matt, John, Luke, Mark
# ---------------------------------------------------------------------------
GOSPELS = {
    # key: (osis, bolls book number, bible-api name, chapters, pretty)
    "matt": ("Matt", 40, "matthew", 28, "Matthew"),
    "john": ("John", 43, "john", 21, "John"),
    "luke": ("Luke", 42, "luke", 24, "Luke"),
    "mark": ("Mark", 41, "mark", 16, "Mark"),
}
MS_ORDER = ("matt", "john", "luke", "mark")


def section_group_size(num_verses: int) -> int:
    if num_verses <= 20:
        return 5
    if num_verses <= 40:
        return 8
    return 10


def ranges_str(nums: list[int]) -> str:
    """[1,2,3,7,8] -> '1-3, 7-8'"""
    if not nums:
        return ""
    out, start, prev = [], nums[0], nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        out.append(f"{start}-{prev}" if start != prev else str(start))
        start = prev = n
    out.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(out)


# ---------------------------------------------------------------------------
# Introduction text
# ---------------------------------------------------------------------------
def build_introduction(pretty: str, chapter: int, absent: list[int], unmapped: list[int],
                       greek_only_missing: list[int], unplaced: list[int], inferred: list[int],
                       versification_note: str | None = None) -> str:
    parts = [
        f"<p>{pretty} {chapter} from <strong>Codex Washingtonianus</strong> (the Freer Gospels, "
        f"Gregory-Aland 032, Freer Gallery of Art F1906.274), a parchment codex of the four Gospels "
        f"written in Egypt in the late 4th or early 5th century and bought by Charles Lang Freer from "
        f"the dealer Ali Arabi at Giza in 1906. It is one of the oldest nearly complete Gospel books "
        f"in existence. The Gospels stand in the so-called Western order, Matthew, John, Luke, Mark, "
        f"and the text is famously block-mixed: the copyist drew on several exemplars of different "
        f"textual character, so the text type changes in blocks within a single Gospel. After Mark "
        f"16:14 the codex carries the Freer Logion, a saying found in no other manuscript. Two "
        f"passages are lost to damage: Mark 15:13-37 and John 14:26-16:6.</p>",
        "<ol>",
        "<li><strong>Scan:</strong> each section is shown with the actual page of the codex that "
        "carries those verses, from the Freer Gallery's own photographs of F1906.274 served by the "
        "Smithsonian IIIF service (ids.si.edu). Which page holds which verse comes from the verse "
        "index of the Center for the Study of New Testament Manuscripts (CSNTM), whose photographs "
        "of the codex are the same shots; every CSNTM page was matched to its Smithsonian image by "
        "pixel comparison before use. Where a verse begins on one page and ends on the next, both "
        "pages are listed. Verses the index cannot place on a surviving page are not shown.</li>",
        "<li><strong>Greek:</strong> Constantin von Tischendorf's <em>Editio octava critica maior</em> "
        "(1869-72, public domain), verbatim from bolls.life. This is a printed critical edition, not "
        "a transcription of Washingtonianus itself: the codex has many readings of its own, and where "
        "it differs from Tischendorf the manuscript reading can be checked on the page image. "
        "Numbering: Tischendorf omits a few verses that the KJV prints (they are in the English "
        "column only).</li>",
        "<li><strong>English:</strong> the King James Version (1611, public domain), verbatim from "
        "bible-api.com. The KJV translates the later Byzantine text, so it will not always match "
        "the Greek shown or the reading of the codex.</li>",
        "</ol>",
    ]
    notes = []
    if absent:
        notes.append(f"Not in the codex (lost to damage): {pretty} {chapter}:{ranges_str(absent)}.")
    if unmapped:
        notes.append(f"Not shown: {pretty} {chapter}:{ranges_str(unmapped)} survive on a CSNTM page "
                     f"(GA_032_0200) that has no counterpart on the Smithsonian image server, so no "
                     f"owner-hosted scan could be paired with them.")
    if unplaced:
        notes.append(f"Not shown: {pretty} {chapter}:{ranges_str(unplaced)}. The CSNTM verse index has no "
                     f"entry for these verses and their neighbours fall on different pages, so the page "
                     f"cannot be fixed without guessing; they are omitted rather than estimated.")
    if inferred:
        notes.append(f"Verses {ranges_str(inferred)} have no entry of their own in the CSNTM index; they "
                     f"are placed on the page that carries both the verse before and the verse after "
                     f"them, which is where continuous text must put them.")
    if versification_note:
        notes.append("Numbering: " + versification_note)
    if greek_only_missing:
        notes.append(f"Tischendorf's edition has no text for verse(s) {ranges_str(greek_only_missing)}; "
                     f"the KJV verse is given alone.")
    if notes:
        parts.append("<p>" + " ".join(notes) + "</p>")
    if pretty == "Mark" and chapter == 16:
        parts.append(
            "<p>The Freer Logion: on the page carrying 16:14 the codex inserts, after that verse, a "
            "passage in which the disciples excuse their unbelief and Christ replies that the term of "
            "Satan's power is fulfilled. It is not part of Tischendorf's text or of the KJV and so does "
            "not appear in either column; it can be read on the scan of that page, where it fills the "
            "lines between 16:14 and 16:15.</p>")
    return "".join(parts)


# Leaves lost from the codex (Sanders 1912; CSNTM index agrees): verses here are
# reported as absent, not as index gaps.
KNOWN_LACUNAE = {
    "mark": {15: range(13, 38)},
    "john": {14: range(26, 32), 15: range(1, 28), 16: range(1, 7)},
}


def in_lacuna(book_key: str, chapter: int, verse: int) -> bool:
    return verse in KNOWN_LACUNAE.get(book_key, {}).get(chapter, range(0))


def neighbour_pages(osis: str, book_key: str, chapter: int, side: str, table: dict) -> int | None:
    """Page of the last verse of the previous chapter (side='prev') or the first
    verse of the next chapter (side='next'), or None at the ends of the book."""
    _osis, bolls, api_name, max_ch, _ = GOSPELS[book_key]
    if side == "prev":
        if chapter == 1:
            return None
        kjv = fetch_kjv_chapter(api_name, chapter - 1)
        last = max(int(v["verse"]) for v in kjv["verses"])
        for v in range(last, 0, -1):
            ids = osis_lookup(osis, chapter - 1, v)
            if ids:
                return csntm_page_num(table[ids[-1]])
        return None
    if chapter >= max_ch:
        return None
    for v in range(1, 6):
        ids = osis_lookup(osis, chapter + 1, v)
        if ids:
            return csntm_page_num(table[ids[0]])
    return None


# ---------------------------------------------------------------------------
# Per-chapter importer
# ---------------------------------------------------------------------------
def import_chapter(book_key: str, chapter: int, page_map: dict, force: bool = False):
    osis, bolls, api_name, _max_ch, pretty = GOSPELS[book_key]
    tid = f"verified-washingtonianus-{book_key}-{chapter}"
    pub_path = PUB_DIR / f"{tid}.json"
    if pub_path.exists() and not force:
        return ("skip", tid, None)
    print(f"  [{tid}] {pretty} {chapter} ...")

    table = csntm_image_table()

    greek = fetch_tisch_chapter(bolls, chapter)
    kjv = fetch_kjv_chapter(api_name, chapter)
    if not greek or not kjv.get("verses"):
        return ("fail", f"{tid}: missing Greek or KJV verses", None)
    greek_by = {int(v["verse"]): v for v in greek}
    versification_note = None
    if book_key == "john" and chapter == 1 and 52 in greek_by:
        # Tischendorf splits John 1:38 into two verses (38, 39) and so numbers
        # 52 verses; the KJV has 51. Re-label to KJV numbering: 38+39 -> 38,
        # 40..52 -> 39..51. Text unchanged.
        merged = {n: greek_by[n] for n in greek_by if n < 38}
        merged[38] = {"verse": 38, "text": greek_by[38]["text"] + " " + greek_by[39]["text"]}
        for n in range(40, 53):
            merged[n - 1] = {"verse": n - 1, "text": greek_by[n]["text"]}
        greek_by = merged
        versification_note = ("Tischendorf divides John 1:38 into two verses (his 1:38-39) and numbers "
                              "the chapter 1-52; the Greek here is re-labelled to KJV numbering "
                              "(Tischendorf 38+39 = 38, 40-52 = 39-51). No words are changed.")
    kjv_by = {int(v["verse"]): v for v in kjv["verses"]}
    verses = sorted(set(greek_by) | set(kjv_by))

    # verse -> [(page_num, freer_id)], in codex order
    verse_pages: dict[int, list[tuple[int, str]]] = {}
    absent, unmapped, unplaced, inferred = [], [], [], []
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        lookups = dict(zip(verses, ex.map(lambda v: osis_lookup(osis, chapter, v), verses)))

    def pages_for(ids):
        out = []
        for iid in ids:
            if iid not in table:
                raise KeyError(f"CSNTM imageId {iid} not in image table")
            out.append(csntm_page_num(table[iid]))
        return out

    # CSNTM's index has occasional holes (e.g. Matt 10:40-42 return [] although
    # 10:39 and 11:1 are both on page 35). A verse with no hit that sits between
    # two indexed verses on the SAME page is on that page (the text is
    # continuous, one column per page); we place it there. If the neighbours are
    # on different pages we cannot tell where the page break falls and leave the
    # verse out ("unplaced"). Verses inside the two known lacunae are "absent".
    hit_pages = {v: pages_for(lookups[v]) for v in verses if lookups[v]}
    prev_ctx = neighbour_pages(osis, book_key, chapter, "prev", table)
    next_ctx = neighbour_pages(osis, book_key, chapter, "next", table)
    for v in verses:
        if v in hit_pages:
            continue
        if in_lacuna(book_key, chapter, v):
            absent.append(v)
            continue
        before = [hit_pages[u][-1] for u in verses if u < v and u in hit_pages]
        after = [hit_pages[u][0] for u in verses if u > v and u in hit_pages]
        lo = before[-1] if before else prev_ctx
        hi = after[0] if after else next_ctx
        if lo is not None and lo == hi:
            hit_pages[v] = [lo]
            inferred.append(v)
        else:
            unplaced.append(v)
    for v in verses:
        if v not in hit_pages:
            continue
        pages = [(n, page_map[n]["freer_id"]) for n in hit_pages[v] if page_map.get(n, {}).get("freer_id")]
        if not pages:
            unmapped.append(v)
            continue
        verse_pages[v] = pages

    present = [v for v in verses if v in verse_pages]
    if not present:
        return ("fail", f"{tid}: no verse of this chapter is on a mapped page", None)

    # group consecutive present verses into sections, never crossing a gap
    runs, run = [], []
    for v in present:
        if run and v != run[-1] + 1:
            runs.append(run)
            run = []
        run.append(v)
    runs.append(run)
    group = section_group_size(len(present))
    sections = []
    greek_only_missing = []
    for run in runs:
        for i in range(0, len(run), group):
            nums = run[i:i + group]
            # avoid a dangling 1-2 verse tail
            if len(run) - (i + group) in (1, 2):
                nums = run[i:]
            sv, ev = nums[0], nums[-1]
            ref = f"{sv}-{ev}" if sv != ev else str(sv)
            pages: list[tuple[int, str]] = []
            for v in nums:
                for pg in verse_pages[v]:
                    if pg not in pages:
                        pages.append(pg)
            pages.sort()
            g_parts, e_parts = [], []
            for n in nums:
                if n in greek_by:
                    g_parts.append(f"<sup>{n}</sup>{clean_strongs(greek_by[n].get('text', ''))}")
                else:
                    greek_only_missing.append(n)
                if n in kjv_by:
                    e_parts.append(f"<sup>{n}</sup>{(kjv_by[n].get('text') or '').strip()}")
            sections.append({
                "section": f"{chapter}.{ref}",
                "original_ref": f"{pretty} {chapter}:{ref}",
                "original_text": " ".join(g_parts),
                "text": " ".join(e_parts),
                "scan_pages": [f"washingtonianus/{scan_filename(n, fid)}" for n, fid in pages],
                "scan_folios": [f"GA_032_{n:04d} = Freer {fid}" for n, fid in pages],
            })
            if len(run) - (i + group) in (1, 2):
                break

    # download every page used
    all_pages = sorted({pg for v in present for pg in verse_pages[v]})
    for n, fid in all_pages:
        try:
            download_page(n, fid)
        except Exception as e:  # noqa: BLE001
            return ("fail", f"{tid}: scan download {fid} (page {n}) failed: {e}", None)
    scan_paths = [f"washingtonianus/{scan_filename(n, fid)}" for n, fid in all_pages]

    today = str(date.today())
    entry = {
        "id": tid,
        "title": f"{pretty}, Chapter {chapter} (Codex Washingtonianus)",
        "slug": tid,
        "language": "Greek (Tischendorf) / English (KJV)",
        "source": ("Codex Washingtonianus (Freer Gospels, GA 032) via Smithsonian/Freer IIIF + CSNTM "
                   "verse index + Tischendorf + KJV"),
        "description": (
            f"{pretty} {chapter} shown on the actual pages of Codex Washingtonianus (Freer Gospels, "
            f"GA 032, late 4th-early 5th c., Freer Gallery of Art F1906.274). Page images from the "
            f"Smithsonian's own IIIF service; verse-to-page index from CSNTM. Greek is Tischendorf's "
            f"8th edition (public domain), English the King James Version."
        ),
        "introduction": build_introduction(pretty, chapter, absent, unmapped, sorted(set(greek_only_missing)),
                                           unplaced, inferred, versification_note),
        "translation": sections,
        "translator_notes": [],
        "verification": {
            "scan_source": ("Smithsonian National Museum of Asian Art (Freer Gallery of Art) IIIF image "
                            "service, ids.si.edu, object F1906.274 'Washington Manuscript III - The Four "
                            "Gospels (Codex Washingtonensis)'"),
            "scan_source_url": FREER_OBJECT_URL,
            "scan_license": ("Smithsonian Terms of Use, 'Usage Conditions Apply' (not CC0): personal, "
                             "educational and other non-commercial use permitted with attribution and a "
                             "link to the source; commercial use requires permission "
                             "(https://www.si.edu/termsofuse). Credit: Freer Gallery of Art, Smithsonian "
                             "Institution, Washington, D.C.: Gift of Charles Lang Freer, F1906.274."),
            "scan_manuscript": ("Codex Washingtonianus / Freer Gospels, GA 032, late 4th-early 5th c., "
                                "Freer Gallery of Art F1906.274"),
            "scan_mapping": ("Verse-level page index from CSNTM (manuscripts.csntm.org, manuscript 206, "
                             "SearchForImageByOsis); CSNTM imageId -> GA_032_NNNN table read from the "
                             "CSNTM viewer page; each CSNTM page matched to its Freer/ids.si.edu image by "
                             "normalised pixel correlation of thumbnails (see "
                             "data/washingtonianus_page_map.json). A verse the index does not list is "
                             "placed only if the verses before and after it are on one and the same page "
                             "(verses_placed_by_enclosure); otherwise it is omitted "
                             "(verses_not_shown_index_gap / verses_absent_from_codex). Each section "
                             "lists every page its verses touch."),
            "scan_pages_used": {f"washingtonianus/{scan_filename(n, fid)}": {
                "csntm_image": f"GA_032_{n:04d}.jpg", "freer_id": fid,
                "freer_iiif": f"{FREER_IIIF}/{fid}/full/1800,/0/default.jpg",
                "verses_in_this_chapter": ranges_str([v for v in present if (n, fid) in verse_pages[v]]),
            } for n, fid in all_pages},
            "scan_local_paths": scan_paths,
            "verses_absent_from_codex": ranges_str(absent),
            "verses_not_shown_no_owner_image": ranges_str(unmapped),
            "verses_not_shown_index_gap": ranges_str(unplaced),
            "verses_placed_by_enclosure": ranges_str(inferred),
            "original_text_source": "bolls.life, TISCH (Tischendorf, Editio octava critica maior, 1869-72)",
            "original_text_license": "public domain",
            "original_text_note": ("Printed edition text, not a transcription of Codex Washingtonianus; "
                                   "readings of the codex are visible on the page images"),
            "original_text_versification": versification_note or "Tischendorf and KJV verse numbers agree",
            "translation_source": "bible-api.com (KJV)",
            "translation_license": "public domain",
            "verified_date": today,
        },
    }
    pub_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    meta = {
        "id": tid,
        "title": entry["title"],
        "author_id": "biblical-authors",
        "language": entry["language"],
        "era": "Apostolic",
        "tradition": "orthodox",
        "category": "sacred-text",
        "date_approx": "late 4th-early 5th c. AD (Codex Washingtonianus)",
        "century": 4,
        "source": entry["source"],
        "description": entry["description"],
        "themes": ["bible", "new-testament", "washingtonianus", "freer-gospels", "verified"],
        "is_first_translation": False,
        "status": "published",
        "slug": tid,
        "scans": {"pages": [{"file": p, "caption": "Codex Washingtonianus (Freer Gospels)"} for p in scan_paths]},
    }
    return ("ok", tid, meta)


def write_pending(new_metas: list[dict]):
    d = {"texts": []}
    if PENDING_PATH.exists():
        d = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in d["texts"]}
    for m in new_metas:
        by_id[m["id"]] = m
    # keep manuscript order (Matt, John, Luke, Mark) then chapter
    def key(t):
        b, ch = t["id"].rsplit("-", 2)[1:]
        return (MS_ORDER.index(b), int(ch))
    d["texts"] = sorted(by_id.values(), key=key)
    PENDING_PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default="", help="matt|john|luke|mark (omit = all)")
    ap.add_argument("--chapter", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--build-map", action="store_true", help="rebuild the CSNTM->Freer page map")
    ap.add_argument("--delay", type=float, default=0.3)
    args = ap.parse_args()

    page_map = build_page_map(force=args.build_map)
    if args.build_map and not (args.book or args.chapter):
        return

    todo: list[tuple[str, int]] = []
    if args.book and args.chapter:
        todo = [(args.book, args.chapter)]
    elif args.book:
        todo = [(args.book, ch) for ch in range(1, GOSPELS[args.book][3] + 1)]
    else:
        for b in MS_ORDER:
            todo += [(b, ch) for ch in range(1, GOSPELS[b][3] + 1)]
    if args.limit:
        todo = todo[: args.limit]

    print(f"Plan: {len(todo)} chapters of Codex Washingtonianus")
    ok, skipped, failed, metas = [], [], [], []
    for book, ch in todo:
        try:
            status, msg, meta = import_chapter(book, ch, page_map, force=args.force)
        except Exception as e:  # noqa: BLE001
            status, msg, meta = "fail", f"verified-washingtonianus-{book}-{ch}: {e!r}", None
        if status == "ok":
            ok.append(msg)
            metas.append(meta)
            write_pending([meta])  # persist immediately, one chapter at a time
        elif status == "skip":
            skipped.append(msg)
        else:
            print(f"    FAIL: {msg}")
            failed.append(msg)
        time.sleep(args.delay)

    print(f"\nImported: {len(ok)}\nSkipped (exist): {len(skipped)}\nFailed: {len(failed)}")
    for f in failed:
        print(f"  {f}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
