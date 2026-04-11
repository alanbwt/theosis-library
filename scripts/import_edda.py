#!/usr/bin/env python3
"""
import_edda.py — Strict primary-source import for the Poetic Edda.

For each poem of the Codex Regius (GKS 2365 4to), this fetches:
  1. Codex Regius folio scans from handrit.is (Árni Magnússon Institute)
  2. Verbatim Old Norse text from heimskringla.no (public-domain Bugge edition)
  3. Verbatim English translation from Thorpe (1866) via Project Gutenberg

Refuses to publish unless all three are available. Records full provenance.
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PUB_DIR = PROJECT_ROOT / "translations" / "published"
SCAN_DIR = PROJECT_ROOT / "site" / "assets" / "scans" / "codex-regius"
SCAN_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "TheosisLibrary/1.0 (https://theosislibrary.com)"
)

# Codex Regius (GKS 2365 4to) page-index ↔ folio mapping at handrit.is:
# folio Nr → page index 8 + 2*N (1r=10, 2r=12, 3r=14, …, 45r=98)
# folio Nv → page index 9 + 2*N (1v=11, 2v=13, …, 45v=99)
# Reference: https://handrit.is/manuscript/view/is/GKS04-2365


def folio_to_page(folio_label):
    """Convert a folio label like '3v' to the handrit.is page index."""
    m = re.match(r"^(\d+)([rv])$", folio_label)
    if not m:
        raise ValueError(f"Bad folio label: {folio_label}")
    n = int(m.group(1))
    side = m.group(2)
    return 8 + 2 * n + (0 if side == "r" else 1)


# Registry: poem_key → (
#   pretty title,
#   handrit folio range (start_label, end_label),
#   heimskringla.no URL fragment,
#   thorpe section header (line search marker),
# )
# Folio ranges from standard Codex Regius scholarship.
EDDA_POEMS = [
    ("voluspa", "Völuspá",
     ("1r", "3r"), "V%C3%B6lusp%C3%A1",
     "VÖLUSPÂ. THE VALA'S PROPHECY."),
    ("havamal", "Hávamál",
     ("3r", "7v"), "H%C3%A1vam%C3%A1l",
     "THE HIGH ONE'S"),
    ("vafthrudnismal", "Vafþrúðnismál",
     ("7v", "10r"), "Vaf%C3%BEr%C3%BA%C3%B0nism%C3%A1l",
     "THE LAY OF VAFTHRUDNIR."),
    ("grimnismal", "Grímnismál",
     ("10r", "12r"), "Gr%C3%ADmnism%C3%A1l",
     "THE LAY OF GRIMNIR."),
    ("skirnismal", "Skírnismál (För Skírnis)",
     ("12r", "13v"), "Sk%C3%ADrnism%C3%A1l",
     "THE JOURNEY OR LAY OF SKIRNIR."),
    ("harbardsljod", "Hárbarðsljóð",
     ("13v", "15v"), "H%C3%A1rbar%C3%B0slj%C3%B3%C3%B0",
     "THE LAY OF HARBARD."),
    ("hymiskvida", "Hymiskviða",
     ("15v", "17r"), "Hymiskvi%C3%B0a",
     "THE LAY OF HYMIR."),
    ("lokasenna", "Lokasenna",
     ("17r", "19v"), "Lokasenna",
     "OEGIR'S COMPOTATION, OR LOKI'S ALTERCATION."),
    ("thrymskvida", "Þrymskviða",
     ("19v", "20v"), "%C3%9Erymskvi%C3%B0a",
     "THE LAY OF THRYM, OR THE HAMMER RECOVERED."),
    ("volundarkvida", "Vǫlundarkviða",
     ("20v", "23r"), "V%C3%B6lundarkvi%C3%B0a",
     "THE LAY OF VOLUND."),
    ("alvissmal", "Alvíssmál",
     ("23r", "24r"), "Alv%C3%ADssm%C3%A1l",
     "THE LAY OF THE DWARF ALVIS."),
]


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout).read()


def http_get_text(url, timeout=30):
    return http_get(url, timeout).decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Codex Regius scan downloader (handrit.is)
# ---------------------------------------------------------------------------
HANDRIT_URL_TPL = (
    "https://myndir.handrit.is/file/Handrit.is/GKS%202365%204to/"
    "{page}/SECONDARY_DISPLAY"
)


def download_codex_regius_folio(folio_label, dest_path):
    if dest_path.exists() and dest_path.stat().st_size > 50000:
        return
    page = folio_to_page(folio_label)
    url = HANDRIT_URL_TPL.format(page=page)
    data = http_get(url, timeout=60)
    dest_path.write_bytes(data)


# ---------------------------------------------------------------------------
# Old Norse text (heimskringla.no)
# ---------------------------------------------------------------------------
def fetch_heimskringla_text(url_fragment):
    """Fetch a Heimskringla.no Edda poem page and return list of stanzas.
    Each stanza is a dict {'num': int, 'lines': [str, str, ...]}
    """
    url = f"https://heimskringla.no/wiki/{url_fragment}"
    html = http_get_text(url, timeout=30)
    # Heimskringla pages put each line of verse in a <dd> tag.
    # Stanzas are separated by lines containing only a number "1." "2." etc.
    dd_lines = re.findall(r"<dd>([^<]*)</dd>", html)
    if not dd_lines:
        return []

    stanzas = []
    cur = None
    for line in dd_lines:
        line = unescape(line).strip()
        if not line or line == "\xa0":
            continue
        m = re.match(r"^(\d+)\.\s*$", line)
        if m:
            if cur is not None and cur["lines"]:
                stanzas.append(cur)
            cur = {"num": int(m.group(1)), "lines": []}
            continue
        if cur is None:
            cur = {"num": 1, "lines": []}
        cur["lines"].append(line)
    if cur is not None and cur["lines"]:
        stanzas.append(cur)

    return stanzas


# ---------------------------------------------------------------------------
# English translation (Thorpe, Project Gutenberg #14726)
# ---------------------------------------------------------------------------
PG_URL = "https://www.gutenberg.org/cache/epub/14726/pg14726.txt"
_pg_cache = None


def get_thorpe_text():
    global _pg_cache
    if _pg_cache is None:
        local = Path("/tmp/pg14726.txt")
        if not local.exists():
            data = http_get(PG_URL, timeout=60)
            local.write_bytes(data)
        _pg_cache = local.read_text(encoding="utf-8", errors="replace")
    return _pg_cache


def fetch_thorpe_poem(header_marker):
    """Find the section starting with `header_marker` in the Thorpe text and
    return list of stanzas as dicts {'num': int, 'text': str}."""
    text = get_thorpe_text()
    idx = text.find(header_marker)
    if idx == -1:
        return []
    # Find the next major heading (uppercase ALL CAPS line longer than 8 chars)
    section = text[idx + len(header_marker):]
    end_match = re.search(
        r"\n\n(THE LAY OF [A-Z][A-Z, ]+|VÖLUSPÂ|VÖLUSPA|HÁVAMÁL|"
        r"THE SAYINGS OF [A-Z][A-Z ]+|HYNDLA|GRIMNIR|GROUGALDR|GROA's GALDR|"
        r"FIOLSVITH|EGIL|VEGTAM|RIG|SKIRNIR|VOLUND|HELGI|"
        r"GRIPIR|REGIN|FAFNIR|SIGURDRIFA|SIGURD|GUDRUN|SIGRDRIFA|"
        r"BRYNHILD|ATLI|ODDRUN|HAMDIR)",
        section,
    )
    if end_match:
        section = section[: end_match.start()]
    # Parse stanzas: paragraphs starting with "N." where N is a number
    stanzas = []
    # A stanza paragraph: "1. blah blah\nblah\n\n2. ..."
    for m in re.finditer(
        r"(?:^|\n)(\d+)\.\s+(.*?)(?=\n\n\d+\.|\n\n[A-Z]|\Z)",
        section,
        flags=re.DOTALL,
    ):
        num = int(m.group(1))
        body = m.group(2).strip()
        # Collapse internal whitespace
        body = re.sub(r"\s+", " ", body)
        stanzas.append({"num": num, "text": body})
    return stanzas


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def import_edda_poem(poem_key, force=False):
    spec = next((p for p in EDDA_POEMS if p[0] == poem_key), None)
    if not spec:
        return ("fail", f"unknown poem: {poem_key}")
    _, pretty, (start_folio, end_folio), heimskringla_frag, thorpe_marker = spec

    tid = f"verified-edda-{poem_key}"
    pub_path = PUB_DIR / f"{tid}.json"
    if pub_path.exists() and not force:
        return ("skip", tid)

    print(f"  [{tid}] {pretty} ({start_folio}-{end_folio})...")

    # 1. Download Codex Regius folios for the range
    scan_files = []
    n_start = int(re.match(r"^(\d+)", start_folio).group(1))
    n_end = int(re.match(r"^(\d+)", end_folio).group(1))
    folios_in_range = []
    for n in range(n_start, n_end + 1):
        for side in ["r", "v"]:
            label = f"{n}{side}"
            # Filter to actual range
            if n == n_start and start_folio == f"{n}v" and side == "r":
                continue
            if n == n_end and end_folio == f"{n}r" and side == "v":
                continue
            folios_in_range.append(label)

    for folio in folios_in_range:
        scan_filename = f"codex-regius-{folio}.jpg"
        scan_path = SCAN_DIR / scan_filename
        try:
            download_codex_regius_folio(folio, scan_path)
        except Exception as e:
            return ("fail", f"{tid}: scan download failed for {folio}: {e}")
        if not scan_path.exists() or scan_path.stat().st_size < 50000:
            return ("fail", f"{tid}: scan {folio} too small")
        scan_files.append(f"codex-regius/{scan_filename}")

    # 2. Fetch Old Norse stanzas
    try:
        norse_stanzas = fetch_heimskringla_text(heimskringla_frag)
    except Exception as e:
        return ("fail", f"{tid}: heimskringla fetch failed: {e}")
    if not norse_stanzas:
        return ("fail", f"{tid}: no Old Norse stanzas parsed")

    # 3. Fetch English (Thorpe) stanzas
    try:
        eng_stanzas = fetch_thorpe_poem(thorpe_marker)
    except Exception as e:
        return ("fail", f"{tid}: thorpe fetch failed: {e}")
    if not eng_stanzas:
        return ("fail", f"{tid}: no English stanzas parsed")

    # 4. Build sections — pair by stanza number
    norse_by_num = {s["num"]: s for s in norse_stanzas}
    eng_by_num = {s["num"]: s["text"] for s in eng_stanzas}
    all_nums = sorted(set(norse_by_num) | set(eng_by_num))

    sections = []
    group_size = 5
    for i in range(0, len(all_nums), group_size):
        nums = all_nums[i:i + group_size]
        sv, ev = nums[0], nums[-1]
        ref = f"{sv}-{ev}" if sv != ev else str(sv)

        norse_text = " ".join(
            f'<sup>{n}</sup>{" / ".join(norse_by_num[n]["lines"])}'
            for n in nums if n in norse_by_num
        )
        eng_text = " ".join(
            f'<sup>{n}</sup>{eng_by_num[n]}'
            for n in nums if n in eng_by_num
        )
        sections.append({
            "section": ref,
            "original_ref": f"{pretty} st. {ref}",
            "original_text": norse_text,
            "text": eng_text,
            "scan_pages": scan_files,
        })

    today = str(date.today())
    entry = {
        "id": tid,
        "title": pretty,
        "slug": tid,
        "language": "Old Norse / English",
        "source": "Codex Regius (GKS 2365 4to) via handrit.is + Heimskringla.no Old Norse + Thorpe (1866) English",
        "description": (
            f"{pretty}, from the Poetic Edda preserved in Codex Regius (GKS 2365 4to, "
            f"c. 1270 AD), housed at the Árni Magnússon Institute, Reykjavík. Manuscript "
            f"folio scans (folios {start_folio}–{end_folio}) from handrit.is. Old Norse text "
            f"verbatim from heimskringla.no. English translation verbatim from Benjamin "
            f"Thorpe's 1866 edition (Project Gutenberg #14726, public domain)."
        ),
        "introduction": (
            f"<p>This entry meets the strict three-criteria standard of the Theosis Library:</p>"
            f"<ol>"
            f"<li><strong>Manuscript scan:</strong> Folios {start_folio}–{end_folio} of "
            f"Codex Regius (GKS 2365 4to), the unique 13th-century Icelandic manuscript "
            f"containing the Poetic Edda, hosted by the Árni Magnússon Institute via "
            f"handrit.is.</li>"
            f"<li><strong>Original text:</strong> The Old Norse text of {pretty}, "
            f"verbatim from heimskringla.no.</li>"
            f"<li><strong>English translation:</strong> Benjamin Thorpe's 1866 translation "
            f"of the Elder Edda, retrieved verbatim from Project Gutenberg eBook #14726 "
            f"(public domain).</li>"
            f"</ol>"
        ),
        "translation": sections,
        "translator_notes": [],
        "verification": {
            "scan_source": "handrit.is (Árni Magnússon Institute, Reykjavík)",
            "scan_license": "public domain (manuscript photographs)",
            "scan_manuscript": "GKS 2365 4to (Codex Regius)",
            "scan_folios": f"{start_folio}-{end_folio}",
            "scan_local_paths": scan_files,
            "original_text_source": "heimskringla.no",
            "original_text_license": "public domain",
            "translation_source": "Project Gutenberg #14726 (Thorpe 1866 Elder Edda)",
            "translation_license": "public domain",
            "verified_date": today,
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
            "author_id": "anonymous-norse",
            "language": "Old Norse",
            "era": "Viking Age",
            "tradition": "norse",
            "category": "sacred-text",
            "date_approx": "c. 9th-13th c. AD; manuscript c. 1270",
            "century": 13,
            "source": pub["source"],
            "description": pub["description"],
            "themes": ["norse", "edda", "codex-regius", "verified"],
            "is_first_translation": False,
            "status": "published",
            "slug": tid,
            "scans": {
                "pages": [
                    {"file": p, "caption": f"Codex Regius (GKS 2365 4to)"}
                    for p in pub["verification"]["scan_local_paths"]
                ]
            },
        }
        by_id[tid] = meta

    # Ensure author exists
    authors_path = DATA_DIR / "authors.json"
    a = json.loads(authors_path.read_text(encoding="utf-8"))
    if not any(au["id"] == "anonymous-norse" for au in a["authors"]):
        a["authors"].append({
            "id": "anonymous-norse",
            "name": "Anonymous (Codex Regius)",
            "dates": "c. 9th-13th c. AD",
            "tradition": "norse",
        })
        authors_path.write_text(json.dumps(a, indent=2, ensure_ascii=False), encoding="utf-8")

    d["texts"] = list(by_id.values())
    data_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  texts.json now has {len(d['texts'])} entries")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--poem", type=str, default="", help="Only import this poem key")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0)
    args = parser.parse_args()

    todo = [args.poem] if args.poem else [p[0] for p in EDDA_POEMS]
    print(f"Plan: import {len(todo)} Edda poems")

    imported, failed, skipped = [], [], []
    for poem_key in todo:
        result, info = import_edda_poem(poem_key, force=args.force)
        if result == "ok":
            imported.append(info)
        elif result == "skip":
            skipped.append(info)
        else:
            failed.append(info)
            print(f"    FAIL: {info}")
        time.sleep(args.delay)

    print(f"\nImported: {len(imported)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Failed: {len(failed)}")
    for f in failed:
        print(f"  {f}")

    if imported or args.force:
        sync_texts_json(imported + skipped)


if __name__ == "__main__":
    main()
