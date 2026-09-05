#!/usr/bin/env python3
"""
fix_sinaiticus_section_folios.py — Map EVERY section of every Codex Sinaiticus
entry to the specific folio(s) that actually contain its verses.

Background: the original import pointed all sections of a chapter at the folio
holding verse 1. Sinaiticus folios usually hold ~1.5 chapters, so later
sections of most chapters pointed at a folio that does not contain them.

Method: CSP's manuscript.aspx accepts &verse=N and returns the folio id plus
its verse range. We query start and end verse of each section, cache folio
ranges so subsequent lookups are free, download any folio not yet on disk
(reusing existing folio images by folio id), and rewrite scan_pages per section.

Safe to re-run; progress is cached in data/csp_folio_cache.json.
"""
import json, re, sys, time, os
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "sinaiticus-folios"
CACHE = ROOT / "data" / "csp_folio_cache.json"

spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
iv = importlib.util.module_from_spec(spec); spec.loader.exec_module(iv)

PRETTY = dict(iv.NT_BOOK_PRETTY)
for k, v in iv.CSP_BOOKS_OT.items():
    PRETTY[k] = v[4]

cache = json.loads(CACHE.read_text()) if CACHE.exists() else {"lookups": {}, "folios": {}}
# cache["lookups"][f"{book}|{ch}|{v}"] = folio_id
# cache["folios"][folio_id] = {"verse_info":..., "library_folio":..., "segments":[[bookname,a,b,c,d],...]}

def parse_segments(info):
    segs = []
    for name, a, b, c, d in re.findall(r"([A-Za-z0-9 ]+?),\s*(\d+):(\d+)\s*-\s*(\d+):(\d+)", info):
        segs.append([name.strip().lower(), int(a), int(b), int(c), int(d)])
    return segs

def folio_covers(folio_id, pretty, ch, v):
    f = cache["folios"].get(folio_id)
    if not f: return False
    for name, a, b, c, d in f["segments"]:
        if name != pretty.lower(): continue
        if (ch, v) >= (a, b) and (ch, v) <= (c, d):
            # exclusive at boundaries is ambiguous; treat boundary verses as needing a real lookup
            if (ch, v) in ((a, b), (c, d)): return False
            return True
    return False

def lookup(csp_book, pretty, ch, v):
    key = f"{csp_book}|{ch}|{v}"
    if key in cache["lookups"]:
        return cache["lookups"][key]
    for fid in cache["folios"]:
        if folio_covers(fid, pretty, ch, v):
            cache["lookups"][key] = fid
            return fid
    url = f"{iv.CSP_BASE}/en/manuscript.aspx?book={csp_book}&chapter={ch}&lid=en&side=r&verse={v}"
    for attempt in range(4):
        try:
            html = iv.http_get_text(url); break
        except Exception as e:
            time.sleep(3 * (attempt + 1)); html = None
    if html is None: return None
    m = re.search(r"zoom\.init\([^)]*'(Q\d+_\d+[rv]_[A-Z]\d+)'", html)
    if not m: return None
    fid = m.group(1)
    info_m = re.search(r'manuscriptVerseInfo">\s*([^<]+?)\s*&nbsp;', html)
    info = info_m.group(1).strip() if info_m else ""
    fol_m = re.search(r"folio</i>:\s*([A-Za-z0-9]+)", html)
    cache["folios"].setdefault(fid, {"verse_info": info, "library_folio": fol_m.group(1) if fol_m else "", "segments": parse_segments(info)})
    cache["lookups"][key] = fid
    return fid

def existing_file_for(fid):
    for f in SCAN_DIR.iterdir():
        if fid in f.name and f.stat().st_size > 10000:
            return f.name
    return None

def ensure_scan(fid, book_key, ch):
    name = existing_file_for(fid)
    if name: return name
    name = f"{book_key}-{ch}-{fid}.jpg"
    iv.csp_download_folio(fid, zoom=4, dest_path=SCAN_DIR / name)
    return name

def sups(s): return [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s)]

def save_cache(): CACHE.write_text(json.dumps(cache, indent=1))

def process(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    m = re.match(r"verified-sinaiticus-([a-z0-9]+)-(\d+)$", d["id"])
    book_key, ch = m.group(1), int(m.group(2))
    v = d["verification"]
    if v.get("section_folios_verified"): return "skip"
    pretty = PRETTY[book_key]
    csp_book = v.get("csp_book_number") or iv.CSP_BOOKS_NT[book_key][0]
    all_files = []
    infos = []
    for s in d["translation"]:
        nums = sups(s["original_text"]) or sups(s["text"])
        if not nums: continue
        fids = []
        for vv in (nums[0], nums[-1]):
            fid = lookup(csp_book, pretty, ch, vv)
            if fid and fid not in fids: fids.append(fid)
        if not fids:
            # Verses absent from the codex (e.g. Mark 16:9-20): point at the folio where the text ends.
            if all_files:
                s["scan_pages"] = [all_files[-1]]
                s["scan_note"] = "These verses are not present in Codex Sinaiticus; the folio shown is where the manuscript's text of this chapter ends."
                continue
            return f"FAIL no folio for {d['id']} {s['section']}"
        files = [ensure_scan(fid, book_key, ch) for fid in fids]
        s["scan_pages"] = [f"sinaiticus-folios/{f}" for f in files]
        for fid, f in zip(fids, files):
            if f"sinaiticus-folios/{f}" not in all_files:
                all_files.append(f"sinaiticus-folios/{f}")
                infos.append(f"{fid} (lib. folio {cache['folios'].get(fid,{}).get('library_folio','?')}): {cache['folios'].get(fid,{}).get('verse_info','')}")
    v["scan_local_paths"] = all_files
    v["scan_local_path"] = all_files[0]
    v["scan_folio_ids"] = [re.search(r"(Q\d+_\d+[rv]_[A-Z]\d+)", f).group(1) for f in all_files]
    v["scan_folio_ranges"] = infos
    v["section_folios_verified"] = True
    v["section_folios_note"] = "Each section links to the specific folio(s) containing its verses, resolved per verse via the Codex Sinaiticus Project page index."
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"ok {len(all_files)} folios"

def main():
    only = sys.argv[1:] 
    files = sorted(PUB.glob("verified-sinaiticus-*.json"))
    if only: files = [f for f in files if any(o in f.name for o in only)]
    n = 0
    for f in files:
        r = process(f)
        n += 1
        print(f"[{n}/{len(files)}] {f.stem}: {r}", flush=True)
        if n % 5 == 0: save_cache()
    save_cache()

if __name__ == "__main__":
    main()
