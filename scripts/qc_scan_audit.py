#!/usr/bin/env python3
"""
qc_scan_audit.py - read-only audit of section-level scan_pages for the legacy
collections (Sinaiticus, Leningrad, 1QIsa-a, Parisino-Petropolitanus Quran,
Venetus A Iliad, Gilgamesh, Josephus).

For every section it works out which verses / lines / ayas the section holds
and which images the importer's own mapping data says carry them, then compares
that with the section's scan_pages. It never edits a published JSON.

Mapping data used per collection:
  sinaiticus  verification.scan_folio_ranges of every entry + data/csp_folio_cache.json
              (Codex Sinaiticus Project page index, verse range per folio side)
  leningrad   tanach.us LCIndex.xml (page per verse), cached under
              data/sources/qc-legacy/audit/
  1qisaa      COLUMNS table in scripts/import_1qisaa.py plus ETCBC dss data if cached
  parisino    Corpus Coranicum folio data used by scripts/import_quran.py
  venetus     Homer Multitext line-to-folio data used by scripts/import_homer.py
  gilgamesh   eBL fragment/line data used by scripts/import_gilgamesh.py
  josephus    folio list in scripts/import_josephus.py

Output: data/sources/qc-legacy/audit/problems.json (every problem found) and
data/sources/qc-legacy/audit/summary.json (counts per collection).

Usage: python3 scripts/qc_scan_audit.py [collection ...]
"""
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
OUT = ROOT / "data" / "sources" / "qc-legacy" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

ESTIMATE_RE = re.compile(r"\b(estimat\w*|approximat\w*|proportional\w*|roughly|assum\w*|guess\w*|interpolat\w*)\b", re.I)


def load(prefix):
    for f in sorted(PUB.glob(f"verified-{prefix}-*.json")):
        yield json.loads(f.read_text(encoding="utf-8"))


def sup_labels(html):
    return re.findall(r"<sup>([^<]+)</sup>", html or "")


def generic_checks(prefix, problems, counts):
    """Checks that do not need mapping data: missing files, estimation words,
    duplicate image content under different names."""
    hashes = defaultdict(set)
    for d in load(prefix):
        tid = d["id"]
        v = d.get("verification", {})
        for key in ("scan_mapping", "scan_note", "note", "scan_page_range", "section_folios_note"):
            val = str(v.get(key, ""))
            if ESTIMATE_RE.search(val):
                problems.append({"collection": prefix, "id": tid, "section": None, "type": "estimation_language",
                                 "field": f"verification.{key}", "text": val[:300]})
        for s in d["translation"]:
            counts[prefix] += 1
            note = s.get("scan_note", "") or ""
            if ESTIMATE_RE.search(note):
                problems.append({"collection": prefix, "id": tid, "section": s["section"], "type": "estimation_language",
                                 "field": "scan_note", "text": note[:300]})
            for p in s.get("scan_pages") or []:
                fp = SCANS / p
                if not fp.exists():
                    problems.append({"collection": prefix, "id": tid, "section": s["section"], "type": "scan_file_missing", "file": p})
                elif fp.stat().st_size < 10000:
                    problems.append({"collection": prefix, "id": tid, "section": s["section"], "type": "scan_file_tiny", "file": p})
                else:
                    hashes[p]  # register
            if not s.get("scan_pages"):
                problems.append({"collection": prefix, "id": tid, "section": s["section"], "type": "no_scan_pages"})
    # duplicate content under different file names
    by_md5 = defaultdict(list)
    for p in hashes:
        h = hashlib.md5((SCANS / p).read_bytes()).hexdigest()
        by_md5[h].append(p)
    for h, ps in by_md5.items():
        if len(ps) > 1:
            problems.append({"collection": prefix, "id": None, "section": None, "type": "identical_image_different_names",
                             "files": sorted(ps)})
    return by_md5


# ---------------------------------------------------------------------------
# Codex Sinaiticus
# ---------------------------------------------------------------------------
FID_RE = re.compile(r"(Q\d+_\d+[rv]_[A-Z]\d+)")


def parse_csp_info(info):
    segs = []
    for seg in info.split("/"):
        m = re.match(r"\s*(.+?),\s*(\d+):(\d+)[a-z]?\s*-\s*(\d+):(\d+)[a-z]?\s*$", seg)
        if m:
            segs.append((m.group(1).strip(), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))))
    return segs


def audit_sinaiticus(problems, counts):
    folios = {}
    cache = json.loads((ROOT / "data" / "csp_folio_cache.json").read_text())
    for fid, f in cache["folios"].items():
        folios[fid] = parse_csp_info(f.get("verse_info", ""))
    entries = list(load("sinaiticus"))
    for d in entries:
        for s in d["verification"].get("scan_folio_ranges") or []:
            m = re.match(r"(Q\d+_\d+[rv]_[A-Z]\d+)\s*\(lib\. folio [^)]*\):\s*(.*)", s)
            if m and m.group(1) not in folios:
                folios[m.group(1)] = parse_csp_info(m.group(2))
    # book key -> CSP book name (most frequent name in that book's folio ranges)
    names = defaultdict(Counter)
    for d in entries:
        key = re.match(r"verified-sinaiticus-(.+)-\d+$", d["id"]).group(1)
        for s in d["verification"].get("scan_folio_ranges") or []:
            m = FID_RE.search(s)
            for seg in folios.get(m.group(1), []):
                names[key][seg[0]] += 1
    bookname = {k: c.most_common(1)[0][0] for k, c in names.items()}
    bookname["3john"] = "3 John"
    # CSP gives each folio side as "first verse - last verse". Where the Greek
    # order departs from the chapter order (LXX Proverbs 24-31, the Sirach
    # 30-36 transposition) that min/max pair is not a linear range, so it is
    # replaced here by the content checked on the image (Q65_4r, Q69_7r) or
    # derived from the CSP endpoints plus the Greek order (Q65_4v, Q69_8v).
    folios["Q65_4r_B285"] = [("Proverbs", 24, 14, 24, 24), ("Proverbs", 30, 1, 30, 14)]
    folios["Q65_4v_B286"] = [("Proverbs", 24, 24, 24, 34), ("Proverbs", 30, 14, 30, 33), ("Proverbs", 31, 1, 31, 1)]
    folios["Q69_7r_B355"] = [("Sirach", 30, 1, 30, 24), ("Sirach", 33, 16, 33, 22)]
    folios["Q69_8v_B358"] = [("Sirach", 35, 22, 36, 10), ("Sirach", 30, 25, 30, 25)]
    files_per_fid = defaultdict(set)
    stats = Counter()
    for d in entries:
        tid = d["id"]
        key, ch = re.match(r"verified-sinaiticus-(.+)-(\d+)$", tid).groups()
        ch = int(ch)
        book = bookname[key]
        for s in d["translation"]:
            listed = []
            for p in s.get("scan_pages") or []:
                m = FID_RE.search(p)
                if m:
                    listed.append(m.group(1))
                    files_per_fid[m.group(1)].add(p)
            labels = sup_labels(s["original_text"]) or []
            if not labels:
                stats["sections_without_greek_verses"] += 1
                continue
            verses = []
            for lab in labels:
                if ":" in lab:
                    c, v = lab.split(":")
                    verses.append((int(c), int(v)))
                elif lab.isdigit():
                    verses.append((ch, int(lab)))
            carriers = defaultdict(list)  # fid -> verses it carries
            boundary = defaultdict(list)
            uncovered = []
            for cv in verses:
                hit = False
                for fid, segs in folios.items():
                    for (nm, a, b, c, e) in segs:
                        if nm == book and (a, b) <= cv <= (c, e):
                            carriers[fid].append(cv)
                            if cv in ((a, b), (c, e)):
                                boundary[fid].append(cv)
                            hit = True
                if not hit:
                    uncovered.append(cv)
            stats["sections_checked"] += 1
            for fid in listed:
                if fid not in carriers:
                    problems.append({"collection": "sinaiticus", "id": tid, "section": s["section"],
                                     "type": "listed_page_carries_none_of_section",
                                     "listed": s["scan_pages"], "page": fid, "page_range": folios.get(fid),
                                     "section_verses": f"{verses[0]}-{verses[-1]}"})
            for fid, cvs in carriers.items():
                if fid in listed:
                    continue
                only_boundary = set(cvs) <= set(boundary[fid])
                problems.append({"collection": "sinaiticus", "id": tid, "section": s["section"],
                                 "type": "missing_page_boundary_verse" if only_boundary else "missing_page_with_section_text",
                                 "listed": s["scan_pages"], "missing_page": fid, "page_range": folios.get(fid),
                                 "verses_on_missing_page": [f"{c}:{v}" for c, v in cvs]})
            if uncovered:
                problems.append({"collection": "sinaiticus", "id": tid, "section": s["section"],
                                 "type": "verses_on_no_known_folio", "verses": [f"{c}:{v}" for c, v in uncovered],
                                 "listed": s["scan_pages"]})
    # folio sides inside a book that no section links to (text never shown)
    seq = sorted({(int(re.search(r"_[A-Z](\d+)$", f).group(1)), f[-4:-3], f) for f in files_per_fid}, key=lambda x: (x[2][-4], x[0]))
    by_letter = defaultdict(list)
    for num, _, fid in seq:
        by_letter[fid[-4]].append((num, fid))
    for letter, items in by_letter.items():
        items.sort()
        for (n1, f1), (n2, f2) in zip(items, items[1:]):
            if n2 - n1 > 1:
                b1 = {x[0] for x in folios.get(f1, [])}
                b2 = {x[0] for x in folios.get(f2, [])}
                if b1 & b2 and b1 & b2 != {"Psalms"}:  # only selected Psalms are published
                    problems.append({"collection": "sinaiticus", "id": None, "section": None,
                                     "type": "folio_sides_inside_book_linked_by_no_section",
                                     "between": [f1, f2], "book": sorted(b1 & b2), "missing_count": n2 - n1 - 1})
    for fid, fs in files_per_fid.items():
        if len(fs) > 1:
            problems.append({"collection": "sinaiticus", "id": None, "section": None,
                             "type": "same_folio_saved_under_several_names", "folio": fid, "files": sorted(fs)})
    return dict(stats, csp_book_names=bookname)


# ---------------------------------------------------------------------------
# Leningrad Codex
# ---------------------------------------------------------------------------
LC_NAMES = {}


def _lc_books():
    src = (ROOT / "scripts" / "import_leningrad.py").read_text(encoding="utf-8")
    for m in re.finditer(r'\("([a-z0-9]+)", "([^"]+)", "[^"]+", "([^"]+)", "[^"]+", \d+\)', src):
        LC_NAMES[m.group(1)] = m.group(3)


def load_lcindex():
    p = OUT / "LCIndex.xml"
    if not p.exists():
        import urllib.request
        req = urllib.request.Request("https://tanach.us/XSL/LCIndex.xml", headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"})
        p.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    text = p.read_text(encoding="utf-8", errors="replace")
    out = defaultdict(list)
    for row in re.findall(r"<tr>(.*?)</tr>", text, flags=re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)]
        if len(cells) < 3 or not re.match(r"^\d{3}[AB]$", cells[0]):
            continue
        m = re.match(r"^(\d+):(\d+)([ab]?)-(\d+):(\d+)([ab]?)$", cells[2])
        if not m:
            continue
        out[cells[1]].append((cells[0], (int(m.group(1)), int(m.group(2))), m.group(3),
                              (int(m.group(4)), int(m.group(5))), m.group(6)))
    return out


def audit_leningrad(problems, counts):
    _lc_books()
    idx = load_lcindex()
    stats = Counter()
    for d in load("leningrad"):
        tid = d["id"]
        key, ch = re.match(r"verified-leningrad-(.+)-(\d+)$", tid).groups()
        ch = int(ch)
        rows = idx[LC_NAMES[key]]
        for s in d["translation"]:
            labels = [x for x in sup_labels(s["original_text"]) if x.isdigit()]
            if not labels:
                stats["sections_without_verse_numbers"] += 1
                continue
            stats["sections_checked"] += 1
            expected = []
            for v in map(int, labels):
                for fid, a, ha, b, hb in rows:
                    if a <= (ch, v) <= b:
                        # "26a" at the end of a page means the verse continues
                        # on the next page; "26b" at the start means it began
                        # on the previous one. A bare boundary verse is whole.
                        if fid not in expected:
                            expected.append(fid)
            listed = [re.search(r"-f(\d{3}[ab])\.jpg$", p).group(1).upper() for p in s["scan_pages"]]
            for fid in listed:
                if fid not in expected:
                    problems.append({"collection": "leningrad", "id": tid, "section": s["section"],
                                     "type": "listed_page_carries_none_of_section", "listed": s["scan_pages"],
                                     "page": fid, "expected": expected})
            for fid in expected:
                if fid not in listed:
                    problems.append({"collection": "leningrad", "id": tid, "section": s["section"],
                                     "type": "missing_page_with_section_text", "listed": s["scan_pages"],
                                     "missing_page": fid, "expected": expected})
            if not expected:
                problems.append({"collection": "leningrad", "id": tid, "section": s["section"],
                                 "type": "verses_on_no_known_folio", "listed": s["scan_pages"]})
    return dict(stats)


# ---------------------------------------------------------------------------
# Codex Parisino-petropolitanus (Quran, BnF Arabe 328)
# ---------------------------------------------------------------------------
def _signature(path):
    from PIL import Image, ImageOps
    im = ImageOps.grayscale(Image.open(path)).resize((48, 64))
    px = list(im.tobytes())
    n = len(px)
    mean = sum(px) / n
    sd = (sum((p - mean) ** 2 for p in px) / n) ** 0.5 or 1e-9
    return [(p - mean) / sd for p in px]


def audit_parisino(problems, counts):
    qdir = ROOT / "data" / "sources" / "quran"
    meta_src = json.loads((qdir / "cc_init_quran.json").read_text()) if (qdir / "cc_init_quran.json").exists() else None
    pages = {}
    for p in qdir.glob("cc_page_*_*.json"):
        d = json.loads(p.read_text())["data"]
        pages[f"{d['folio']}{d['side']}"] = d["passages"]
    stats = Counter()
    for d in load("parisino"):
        tid = d["id"]
        sura = int(re.search(r"quran-(\d+)$", tid).group(1))
        for s in d["translation"]:
            stats["sections_checked"] += 1
            lab = re.search(r"\(fol\. (\d+[rv])\)", s["section"]).group(1)
            if s["scan_pages"] != [f"parisino-petropolitanus/pp-f{lab}.jpg"]:
                problems.append({"collection": "parisino", "id": tid, "section": s["section"],
                                 "type": "scan_file_not_the_named_folio", "listed": s["scan_pages"]})
            ps = pages.get(lab)
            if not ps or len(ps) != 1:
                problems.append({"collection": "parisino", "id": tid, "section": s["section"],
                                 "type": "no_single_corpus_coranicum_passage", "folio": lab})
                continue
            st, en = ps[0]["start"], ps[0]["end"]
            vs = [int(x) for x in sup_labels(s["original_text"])]
            lo = (st["sura"], max(1, st["verse"]))
            hi = (en["sura"], en["verse"]) if en["verse"] else (en["sura"] - 1, 10 ** 6)
            bad = [v for v in vs if not (lo <= (sura, v) <= hi)]
            if bad:
                problems.append({"collection": "parisino", "id": tid, "section": s["section"],
                                 "type": "verses_outside_page_range", "verses": bad,
                                 "cc_range": f"{st['sura']}:{st['verse']}.{st['word']}-{en['sura']}:{en['verse']}.{en['word']}"})
            # verses of this sura inside the page range that the section leaves out
            exp_first = lo[1] if lo[0] == sura else 1
            exp_last = hi[1] if hi[0] == sura else None
            if exp_last is not None and vs and (vs[0] != exp_first or vs[-1] != exp_last):
                problems.append({"collection": "parisino", "id": tid, "section": s["section"],
                                 "type": "section_verses_differ_from_page_range", "section_verses": [vs[0], vs[-1]],
                                 "cc_range": f"{st['sura']}:{st['verse']}-{en['sura']}:{en['verse']}"})
    # Is each Gallica image closer to the Corpus Coranicum image of its own folio
    # than to any other folio's image? (checks the folio identity of every file)
    sdir = SCANS / "parisino-petropolitanus"
    labels = sorted(p.stem[4:] for p in sdir.glob("pp-f*.jpg"))
    cc_sig = {l: _signature(qdir / f"cc_image_{l}.jpg") for l in labels if (qdir / f"cc_image_{l}.jpg").exists()}
    for l in labels:
        g = _signature(sdir / f"pp-f{l}.jpg")
        scores = sorted(((sum(x * y for x, y in zip(g, c)) / len(g)), k) for k, c in cc_sig.items())
        best = scores[-1]
        own = next((sc for sc, k in scores if k == l), None)
        stats["images_identity_checked"] += 1
        if best[1] != l:
            problems.append({"collection": "parisino", "id": None, "section": None,
                             "type": "image_closer_to_other_folio", "file": f"pp-f{l}.jpg",
                             "own_corr": round(own or 0, 3), "best": best[1], "best_corr": round(best[0], 3)})
        else:
            stats["images_best_match_own_folio"] += 1
    return dict(stats)


# ---------------------------------------------------------------------------
# Venetus A (Iliad)
# ---------------------------------------------------------------------------
def load_hmt_dse():
    """Iliad line -> Venetus A image id, from the HMT 2024c release CEX
    (citerelationset urn:cite2:hmt:hmtdse.v1:all)."""
    p = OUT / "hmt-2024c.cex"
    if not p.exists():
        import urllib.request
        url = "https://raw.githubusercontent.com/homermultitext/hmt-archive/master/releases-cex/hmt-2024c.cex"
        p.write_bytes(urllib.request.urlopen(url, timeout=300).read())
    line2img = defaultdict(set)
    rx = re.compile(r"^urn:cts:greekLit:tlg0012\.tlg001\.msA:(\d+)\.(\d+)\|urn:cite2:hmt:vaimg\.2017a:(VA\w+?)@[^|]*\|urn:cite2:hmt:msA\.v1:(\w+)$")
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            m = rx.match(line.strip())
            if m:
                line2img[(int(m.group(1)), int(m.group(2)))].add(m.group(3))
    return line2img


def audit_venetus(problems, counts):
    l2i = load_hmt_dse()
    stats = Counter()
    for d in load("venetus"):
        tid = d["id"]
        book = int(re.search(r"iliad-(\d+)$", tid).group(1))
        for s in d["translation"]:
            lines = [int(x) for x in sup_labels(s["original_text"]) if x.isdigit()]
            listed = [re.search(r"(VA\d+[RV]N_\d+)", p).group(1) for p in s["scan_pages"]]
            stats["sections_checked"] += 1
            expected, unindexed = [], []
            for ln in lines:
                imgs = l2i.get((book, ln))
                if not imgs:
                    unindexed.append(ln)
                    continue
                for im in sorted(imgs):
                    if im not in expected:
                        expected.append(im)
            missing = [im for im in expected if im not in listed]
            extra = [im for im in listed if im not in expected]
            if missing:
                lines_on = {im: [ln for ln in lines if im in l2i.get((book, ln), ())] for im in missing}
                problems.append({"collection": "venetus", "id": tid, "section": s["section"],
                                 "type": "missing_page_with_section_text", "listed": s["scan_pages"],
                                 "missing_pages": {im: f"{v[0]}-{v[-1]} ({len(v)} lines)" for im, v in lines_on.items()}})
            if extra:
                problems.append({"collection": "venetus", "id": tid, "section": s["section"],
                                 "type": "listed_page_carries_none_of_section", "listed": s["scan_pages"],
                                 "pages": extra, "expected": expected})
            if unindexed:
                stats["lines_not_in_hmt_index"] += len(unindexed)
                problems.append({"collection": "venetus", "id": tid, "section": s["section"],
                                 "type": "lines_not_in_hmt_dse_index", "lines": unindexed})
    return dict(stats)


ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def _roman(s):
    total, prev = 0, 0
    for ch in reversed(s):
        v = ROMAN[ch]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total


def audit_1qisaa(problems, counts):
    """The column of every word comes from the ETCBC transcription; here the
    column list in each section's original_ref must equal its scan_pages."""
    stats = Counter()
    for d in load("1qisaa"):
        for s in d["translation"]:
            stats["sections_checked"] += 1
            cols = [_roman(c) for c in re.findall(r"col\. ([IVXL]+)", s["original_ref"])]
            files = [int(re.search(r"col-(\d+)\.jpg$", p).group(1)) for p in s["scan_pages"]]
            if cols != files:
                problems.append({"collection": "1qisaa", "id": d["id"], "section": s["section"],
                                 "type": "columns_in_ref_differ_from_scan_pages", "ref_columns": cols, "files": files})
    return dict(stats)


def audit_single_object(prefix):
    """Gilgamesh (one tablet photo per entry) and Josephus (one page per
    witness): every section must point at exactly one image of its object."""
    def run(problems, counts):
        stats = Counter()
        for d in load(prefix):
            imgs = {p for s in d["translation"] for p in s["scan_pages"]}
            for s in d["translation"]:
                stats["sections_checked"] += 1
                if len(s["scan_pages"]) != 1:
                    problems.append({"collection": prefix, "id": d["id"], "section": s["section"],
                                     "type": "unexpected_page_count", "listed": s["scan_pages"]})
            if prefix == "gilgamesh" and len(imgs) != 1:
                problems.append({"collection": prefix, "id": d["id"], "section": None,
                                 "type": "tablet_entry_with_several_images", "files": sorted(imgs)})
        return dict(stats)
    return run


AUDITS = {"sinaiticus": audit_sinaiticus, "leningrad": audit_leningrad, "parisino": audit_parisino,
          "venetus": audit_venetus, "1qisaa": audit_1qisaa, "gilgamesh": audit_single_object("gilgamesh"),
          "josephus": audit_single_object("josephus")}


def main():
    which = sys.argv[1:] or list(AUDITS)
    out_path = OUT / "problems.json"
    sum_path = OUT / "summary.json"
    all_problems = json.loads(out_path.read_text()) if out_path.exists() else {}
    summary = json.loads(sum_path.read_text()) if sum_path.exists() else {}
    for coll in which:
        problems, counts = [], Counter()
        generic_checks(coll, problems, counts)
        extra = AUDITS[coll](problems, counts)
        all_problems[coll] = problems
        summary[coll] = {"sections": counts[coll], "problems_by_type": dict(Counter(p["type"] for p in problems)),
                         "entries_with_problems": len({p["id"] for p in problems if p.get("id")}), "notes": extra}
        print(coll, json.dumps(summary[coll], ensure_ascii=False)[:1500])
    out_path.write_text(json.dumps(all_problems, indent=1, ensure_ascii=False))
    sum_path.write_text(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
