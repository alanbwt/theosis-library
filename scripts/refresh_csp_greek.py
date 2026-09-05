#!/usr/bin/env python3
"""
refresh_csp_greek.py — Re-walk the Codex Sinaiticus Project transcription for
every Sinaiticus chapter whose primary Greek is the CSP transcription (all OT
chapters, and NT chapters after swap_sinaiticus_nt_to_transcription.py) and
replace each verse's Greek in place. Sections, labels, English and scan pages
are untouched. Needed after the page-break fix in csp_get_chapter_text (verses
straddling a folio boundary used to keep only their second half).
Re-runnable; pass entry-name fragments to limit.
"""
import json, re, sys, time
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
iv = importlib.util.module_from_spec(spec); spec.loader.exec_module(iv)

def process(path):
    d = json.loads(path.read_text(encoding="utf-8")); v = d["verification"]
    m = re.match(r"verified-sinaiticus-([a-z0-9]+)-(\d+)$", d["id"]); book, ch = m.group(1), int(m.group(2))
    is_ot = book in iv.CSP_BOOKS_OT
    if not is_ot and v.get("primary_greek") != "csp_transcription": return "skip (Tischendorf primary)"
    csp_book = v.get("csp_book_number") or iv.CSP_BOOKS_NT[book][0]
    start = (v.get("scan_folio_ids") or [v["scan_folio_id"]])[0]
    greek = {}
    for attempt in range(3):
        try: greek = iv.csp_get_chapter_text(csp_book, ch, start); break
        except Exception: time.sleep(3)
    if not greek: return "FAIL no transcription"
    changed = 0
    for s in d["translation"]:
        parts = re.split(r"(<sup>[\d:]+</sup>)", s["original_text"])
        out = []; i = 0
        while i < len(parts):
            piece = parts[i]
            mm = re.match(r"<sup>(\d+)</sup>", piece)
            if mm and i + 1 < len(parts):
                n = int(mm.group(1)); new = greek.get(n)
                if new is not None and new.strip() and new.strip() != parts[i + 1].strip():
                    parts[i + 1] = new; changed += 1
                out.append(piece); out.append(parts[i + 1]); i += 2
            else:
                out.append(piece); i += 1
        s["original_text"] = "".join(out)
    v["csp_greek_refreshed"] = True
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"ok ({changed} verses updated)"

if __name__ == "__main__":
    only = sys.argv[1:]
    files = sorted(PUB.glob("verified-sinaiticus-*.json"))
    if only: files = [f for f in files if any(o in f.name for o in only)]
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f.stem}: {process(f)}", flush=True)
