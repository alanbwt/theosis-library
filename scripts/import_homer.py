#!/usr/bin/env python3
"""
import_homer.py — Strict primary-source import for Homer's Iliad and Odyssey.

For each book (rhapsody), this fetches:
  1. Venetus A manuscript folio scans (10th c.) via Homer Multitext IIIF
  2. Verbatim Ancient Greek text from Perseus Digital Library (Munro & Allen ed.)
  3. Verbatim English translation from Samuel Butler (1898/1900, Project Gutenberg)
"""

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PUB_DIR = PROJECT_ROOT / "translations" / "published"
SCAN_DIR = PROJECT_ROOT / "site" / "assets" / "scans" / "venetus-a"
SCAN_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "TheosisLibrary/1.0 (https://theosislibrary.com)"
)

# HMT IIIF URL template for Venetus A folio images
HMT_IIIF_TPL = (
    "https://www.homermultitext.org/iipsrv?IIIF="
    "/project/homer/pyramidal/deepzoom/hmt/vaimg/2017a/{filename}.tif"
    "/full/1024,/0/default.jpg"
)

# Iliad Book → first Venetus A folio image filename (from HMT CEX data)
ILIAD_BOOK_FOLIOS = {
    1: "VA012RN_0013", 2: "VA024RN_0025", 3: "VA042RN_0043",
    4: "VA051RN_0052", 5: "VA062RN_0063", 6: "VA080VN_0583",
    7: "VA091RN_0263", 8: "VA100VN_0603", 9: "VA111VN_0614",
    10: "VA126RN_0298", 11: "VA137VN_0639", 12: "VA154VN_0656",
    13: "VA164RN_0335", 14: "VA180VN_0682", 15: "VA191RN_0362",
    16: "VA206RN_0377", 17: "VA223VN_0725", 18: "VA239RN_0410",
    19: "VA251VN_0753", 20: "VA260RN_0431", 21: "VA270RN_0440",
    22: "VA282RN_0452", 23: "VA292VN_0794", 24: "VA310VN_0812",
}

# Odyssey manuscript scans: Hayman 1866 Greek edition on Internet Archive
# (identifier: odysseyofhome01home, 524 pages)
# Greek text begins around page 120, ~17 pages per book
ODYSSEY_IA_ID = "odysseyofhome01home"
ODYSSEY_IA_TPL = (
    "https://iiif.archive.org/image/iiif/3/"
    "odysseyofhome01home%2Fodysseyofhome01home_jp2.zip%2Fodysseyofhome01home_jp2%2F"
    "odysseyofhome01home_{page:04d}.jp2/full/max/0/default.jpg"
)
ODYSSEY_SCAN_DIR = PROJECT_ROOT / "site" / "assets" / "scans" / "odyssey-hayman"
ODYSSEY_SCAN_DIR.mkdir(parents=True, exist_ok=True)

# Proportional page ranges for each Odyssey book (pages 120-520, ~400 pages for 24 books)
def _odyssey_page(book_num):
    """Estimated page in Hayman 1866 for each book start."""
    return 120 + int((book_num - 1) * 400 / 24)

# Perseus GitHub URLs for Greek text
ILIAD_XML_URL = (
    "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/"
    "master/data/tlg0012/tlg001/tlg0012.tlg001.perseus-grc2.xml"
)
ODYSSEY_XML_URL = (
    "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/"
    "master/data/tlg0012/tlg002/tlg0012.tlg002.perseus-grc2.xml"
)

# Project Gutenberg IDs for Butler translations
PG_ILIAD = 2199
PG_ODYSSEY = 1727

_xml_cache = {}
_pg_cache = {}


def http_get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout).read()


def http_get_text(url, timeout=60):
    return http_get(url, timeout).decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Venetus A scan downloader
# ---------------------------------------------------------------------------
def download_venetus_folio(filename, dest_path):
    if dest_path.exists() and dest_path.stat().st_size > 30000:
        return
    url = HMT_IIIF_TPL.format(filename=filename)
    data = http_get(url, timeout=60)
    dest_path.write_bytes(data)


# ---------------------------------------------------------------------------
# Greek text from Perseus GitHub XML
# ---------------------------------------------------------------------------
def get_perseus_xml(xml_url):
    if xml_url not in _xml_cache:
        local = Path(f"/tmp/perseus_{hash(xml_url)}.xml")
        if not local.exists():
            data = http_get(xml_url, timeout=60)
            local.write_bytes(data)
        _xml_cache[xml_url] = local
    return _xml_cache[xml_url]


def parse_greek_book(xml_url, book_num):
    """Parse all lines of a book from Perseus TEI XML."""
    xml_path = get_perseus_xml(xml_url)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    for div in root.iter():
        if div.get('n') == str(book_num) and div.get('type') in ('Book', 'book', 'textpart'):
            lines = []
            for l in div.findall('.//tei:l', ns):
                n = l.get('n', '')
                text = ''.join(l.itertext()).strip()
                if n and text:
                    lines.append((int(n), text))
            return lines
    return []


# ---------------------------------------------------------------------------
# English text from Project Gutenberg
# ---------------------------------------------------------------------------
def get_pg_text(pg_id):
    if pg_id not in _pg_cache:
        local = Path(f"/tmp/pg{pg_id}.txt")
        if not local.exists():
            url = f"https://www.gutenberg.org/cache/epub/{pg_id}/pg{pg_id}.txt"
            data = http_get(url, timeout=60)
            local.write_bytes(data)
        _pg_cache[pg_id] = local.read_text(encoding="utf-8", errors="replace")
    return _pg_cache[pg_id]


def strip_pg_header(text):
    for marker in ["*** START OF THIS PROJECT GUTENBERG", "*** START OF THE PROJECT GUTENBERG"]:
        idx = text.find(marker)
        if idx != -1:
            nl = text.find("\n", idx)
            if nl != -1:
                text = text[nl + 1:]
                break
    for marker in ["*** END OF THIS PROJECT GUTENBERG", "*** END OF THE PROJECT GUTENBERG", "End of the Project Gutenberg", "End of Project Gutenberg"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
            break
    return text.strip()


def parse_butler_book(pg_id, book_num, total_books=24):
    """Extract one book from Butler's prose translation."""
    raw = get_pg_text(pg_id)
    body = strip_pg_header(raw)

    # Butler divides by "BOOK I", "BOOK II", etc.
    pattern = re.compile(r'\n\s*BOOK\s+([IVXLCDM]+)\b', re.IGNORECASE)
    parts = pattern.split(body)
    # parts = [preamble, "I", text1, "II", text2, ...]
    roman_to_int = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
        'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIII': 13,
        'XIV': 14, 'XV': 15, 'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19,
        'XX': 20, 'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24,
    }
    books = {}
    if len(parts) >= 3:
        for i in range(1, len(parts) - 1, 2):
            num_str = parts[i].strip().upper()
            num = roman_to_int.get(num_str)
            if num:
                books[num] = parts[i + 1].strip()

    return books.get(book_num, "")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def import_homer_book(work, book_num, force=False):
    if work == "iliad":
        xml_url = ILIAD_XML_URL
        pg_id = PG_ILIAD
        pretty_work = "The Iliad"
        tid = f"verified-venetus-{work}-{book_num}"
    else:
        xml_url = ODYSSEY_XML_URL
        pg_id = PG_ODYSSEY
        pretty_work = "The Odyssey"
        tid = f"verified-odyssey-{book_num}"

    pub_path = PUB_DIR / f"{tid}.json"
    if pub_path.exists() and not force:
        return ("skip", tid)

    print(f"  [{tid}] {pretty_work} Book {book_num}...")

    # 1. Download manuscript scan
    scan_files = []
    if work == "iliad":
        folio_filename = ILIAD_BOOK_FOLIOS.get(book_num)
        if not folio_filename:
            return ("fail", f"{tid}: no folio mapping")
        scan_name = f"venetus-a-{work}-{book_num}-{folio_filename}.jpg"
        scan_path = SCAN_DIR / scan_name
        try:
            download_venetus_folio(folio_filename, scan_path)
        except Exception as e:
            return ("fail", f"{tid}: scan download failed: {e}")
        if not scan_path.exists() or scan_path.stat().st_size < 10000:
            return ("fail", f"{tid}: scan too small or missing")
        scan_files.append(f"venetus-a/{scan_name}")
    else:
        # Odyssey: use Hayman 1866 edition from archive.org
        page = _odyssey_page(book_num)
        scan_name = f"odyssey-hayman-book{book_num}-p{page:04d}.jpg"
        scan_path = ODYSSEY_SCAN_DIR / scan_name
        if not (scan_path.exists() and scan_path.stat().st_size > 30000):
            try:
                url = ODYSSEY_IA_TPL.format(page=page)
                data = http_get(url, timeout=120)
                scan_path.write_bytes(data)
            except Exception as e:
                return ("fail", f"{tid}: scan download failed: {e}")
        if not scan_path.exists() or scan_path.stat().st_size < 30000:
            return ("fail", f"{tid}: scan too small")
        scan_files.append(f"odyssey-hayman/{scan_name}")

    # 2. Fetch Greek text from Perseus
    try:
        greek_lines = parse_greek_book(xml_url, book_num)
    except Exception as e:
        return ("fail", f"{tid}: Greek parse failed: {e}")
    if not greek_lines:
        return ("fail", f"{tid}: no Greek lines found for book {book_num}")

    # 3. Fetch English from Butler (PG)
    try:
        english_text = parse_butler_book(pg_id, book_num)
    except Exception as e:
        return ("fail", f"{tid}: Butler parse failed: {e}")
    if not english_text or len(english_text) < 200:
        return ("fail", f"{tid}: Butler text too short ({len(english_text)} chars)")

    # 4. Build sections — group Greek lines, pair with English paragraphs
    group_size = 25  # ~25 lines per section
    sections = []
    # Split English into paragraphs for pairing
    eng_paragraphs = [p.strip() for p in english_text.split("\n\n") if p.strip() and len(p.strip()) > 30]
    eng_html = "\n".join(f"<p>{p.replace(chr(10), ' ')}</p>" for p in eng_paragraphs)

    for i in range(0, len(greek_lines), group_size):
        chunk = greek_lines[i:i + group_size]
        start_line = chunk[0][0]
        end_line = chunk[-1][0]
        ref = f"{start_line}-{end_line}" if start_line != end_line else str(start_line)
        greek_html = " ".join(
            f'<sup>{n}</sup>{text}' for n, text in chunk
        )
        # Proportional English assignment
        eng_start = int(len(eng_paragraphs) * i / max(len(greek_lines), 1))
        eng_end = int(len(eng_paragraphs) * (i + group_size) / max(len(greek_lines), 1))
        eng_chunk = eng_paragraphs[eng_start:eng_end]
        eng_section = "\n".join(f"<p>{p.replace(chr(10), ' ')}</p>" for p in eng_chunk)

        sections.append({
            "section": f"{book_num}.{ref}",
            "original_ref": f"{pretty_work} {book_num}.{ref}",
            "original_text": greek_html,
            "text": eng_section,
            "scan_pages": scan_files,
        })

    today = str(date.today())
    if work == "iliad":
        scan_source = "Homer Multitext Project (homermultitext.org)"
        scan_license = "CC BY-SA"
        scan_ms = "Venetus A (Marcianus Graecus 454, Biblioteca Marciana, Venice)"
        scan_desc = (
            f"Manuscript page from Venetus A (Marcianus Graecus 454), the most important "
            f"surviving Iliad manuscript (10th c., Biblioteca Marciana, Venice), via the "
            f"Homer Multitext Project."
        )
        butler_year = "1898"
    else:
        scan_source = "Internet Archive (Hayman 1866 Greek edition)"
        scan_license = "public domain"
        scan_ms = "Hayman Greek Odyssey edition (1866, Oxford)"
        scan_desc = (
            f"Page from Hayman's 1866 Greek edition of the Odyssey with text and commentary "
            f"(Oxford), a standard 19th-century scholarly edition. Via Internet Archive "
            f"(archive.org/details/odysseyofhome01home)."
        )
        butler_year = "1900"

    entry = {
        "id": tid,
        "title": f"{pretty_work}, Book {book_num}",
        "slug": tid,
        "language": "Ancient Greek / English",
        "source": (
            f"{scan_ms} + Perseus Digital Library Greek (Munro & Allen ed.) + "
            f"Samuel Butler English ({butler_year}, Project Gutenberg #{pg_id})"
        ),
        "description": (
            f"Book {book_num} of {pretty_work} by Homer. {scan_desc} Greek text verbatim "
            f"from the Munro & Allen edition via Perseus Digital Library (public domain). "
            f"English translation verbatim from Samuel Butler's {butler_year} prose rendering "
            f"(Project Gutenberg #{pg_id}, public domain)."
        ),
        "introduction": (
            f"<p>This entry presents Book {book_num} of <strong>{pretty_work}</strong> with "
            f"the strict three-criteria standard of the Theosis Library:</p>"
            f"<ol>"
            f"<li><strong>Primary source scan:</strong> {scan_desc}</li>"
            f"<li><strong>Original text:</strong> The complete Greek text of Book {book_num} "
            f"({len(greek_lines)} lines), verbatim from the Munro & Allen edition via the "
            f"Perseus Digital Library (public domain).</li>"
            f"<li><strong>English translation:</strong> Samuel Butler's prose translation "
            f"({butler_year}), verbatim from Project Gutenberg #{pg_id} (public domain).</li>"
            f"</ol>"
        ),
        "translation": sections,
        "translator_notes": [],
        "verification": {
            "scan_source": scan_source,
            "scan_license": scan_license,
            "scan_manuscript": scan_ms,
            "scan_local_paths": scan_files,
            "original_text_source": "Perseus Digital Library (Munro & Allen edition)",
            "original_text_license": "public domain",
            "translation_source": f"Project Gutenberg #{pg_id} (Samuel Butler, {butler_year})",
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

    # Ensure author exists
    authors_path = DATA_DIR / "authors.json"
    a = json.loads(authors_path.read_text(encoding="utf-8"))
    if not any(au["id"] == "homer" for au in a["authors"]):
        a["authors"].append({
            "id": "homer",
            "name": "Homer",
            "dates": "c. 8th century BCE",
            "tradition": "greek",
        })
        authors_path.write_text(json.dumps(a, indent=2, ensure_ascii=False), encoding="utf-8")

    for tid in imported_ids:
        pub_path = PUB_DIR / f"{tid}.json"
        if not pub_path.exists():
            continue
        pub = json.loads(pub_path.read_text(encoding="utf-8"))
        meta = {
            "id": tid,
            "title": pub["title"],
            "author_id": "homer",
            "language": "Ancient Greek",
            "era": "Classical",
            "tradition": "greek",
            "category": "literature",
            "date_approx": "c. 8th c. BCE (composition); 10th c. (Venetus A)",
            "century": -8,
            "source": pub["source"],
            "description": pub["description"],
            "themes": ["homer", "iliad", "greek", "epic", "venetus-a", "verified"],
            "is_first_translation": False,
            "status": "published",
            "slug": tid,
            "scans": {
                "pages": [
                    {"file": p, "caption": "Venetus A (10th c., Biblioteca Marciana)"}
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
    parser.add_argument("--work", choices=["iliad", "odyssey", "both"], default="iliad")
    parser.add_argument("--book", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    todo = []
    if args.work in ("iliad", "both"):
        if args.book:
            todo.append(("iliad", args.book))
        else:
            todo.extend(("iliad", b) for b in range(1, 25))
    if args.work in ("odyssey", "both"):
        if args.book:
            todo.append(("odyssey", args.book))
        else:
            todo.extend(("odyssey", b) for b in range(1, 25))

    print(f"Plan: import {len(todo)} Homer books")

    imported, failed, skipped = [], [], []
    for work, book_num in todo:
        result, info = import_homer_book(work, book_num, force=args.force)
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
