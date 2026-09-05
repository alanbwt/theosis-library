#!/usr/bin/env python3
"""
swap_sinaiticus_nt_to_transcription.py — Make the Codex Sinaiticus Project's
verbatim manuscript transcription the primary Greek for Sinaiticus NT chapters
(as the OT chapters already do), keeping Tischendorf's 8th edition as a
secondary "critical edition reading" per section.

Why: the folio in the scan is Sinaiticus. Tischendorf's edition often differs
from it (e.g. John 1:18 Sinaiticus μονογενης θεος vs Tischendorf ο μονογενης
υιος). The library's promise is that the Greek can be checked against the scan.

Run AFTER fix_sinaiticus_section_folios.py (scan_pages are preserved by verse
overlap). Safe to re-run; skips entries already swapped.
"""
import json, re, sys, time
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
DATA = ROOT / "data" / "texts.json"
spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
iv = importlib.util.module_from_spec(spec); spec.loader.exec_module(iv)

def sups_pairs(html):
    parts = re.split(r"<sup>(\d+)</sup>", html)
    return [(int(parts[i]), parts[i + 1].strip()) for i in range(1, len(parts), 2)]

def process(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    v = d["verification"]
    if v.get("primary_greek") == "csp_transcription" and not FORCE: return "already"
    m = re.match(r"verified-sinaiticus-([a-z0-9]+)-(\d+)$", d["id"])
    book, ch = m.group(1), int(m.group(2))
    if book not in iv.CSP_BOOKS_NT: return "not NT"
    csp_book = iv.CSP_BOOKS_NT[book][0]
    pretty = iv.NT_BOOK_PRETTY[book]
    start = (v.get("scan_folio_ids") or [v["scan_folio_id"]])[0]
    greek = {}
    for attempt in range(3):
        try:
            greek = iv.csp_get_chapter_text(csp_book, ch, start); break
        except Exception:
            time.sleep(3)
    if not greek: return "FAIL no CSP transcription"
    old = d["translation"]
    tisch, kjv = {}, {}
    for s in old:
        for n, t in sups_pairs(s.get("edition_text") or s["original_text"]): tisch[n] = t
        for n, t in sups_pairs(s["text"]): kjv[n] = t
    known_short = {("mark", 16): "Codex Sinaiticus ends the Gospel of Mark at 16:8. Verses 9-20 (the so-called longer ending) are not in the manuscript; the KJV text of those verses is shown for reference, with no Greek beside it, and Tischendorf's edition reading beneath. This is one of the most important textual facts a reader can verify directly on the folio."}
    if len(greek) < 0.6 * len(kjv) and (book, ch) not in known_short: return f"FAIL transcription too short ({len(greek)} vs {len(kjv)} KJV verses)"
    all_nums = sorted(set(greek) | set(kjv))
    n = len(all_nums)
    gs = 5 if n <= 20 else 8 if n <= 40 else 10
    def scans_for(nums):
        hits = []
        for os_ in old:
            on = {x for x, _ in sups_pairs(os_["original_text"])} | {x for x, _ in sups_pairs(os_["text"])}
            if on & set(nums):
                for p in os_.get("scan_pages", []):
                    if p not in hits: hits.append(p)
        return hits or (old[0].get("scan_pages") or [])
    secs = []
    for i in range(0, n, gs):
        nums = all_nums[i:i + gs]
        sv, ev = nums[0], nums[-1]
        lbl = f"{sv}-{ev}" if sv != ev else str(sv)
        secs.append({
            "section": f"{ch}.{lbl}",
            "original_ref": f"{pretty} {ch}:{lbl}",
            "original_text": " ".join(f"<sup>{x}</sup>{greek[x]}" for x in nums if x in greek),
            "edition_text": " ".join(f"<sup>{x}</sup>{tisch[x]}" for x in nums if x in tisch),
            "text": " ".join(f"<sup>{x}</sup>{kjv[x]}" for x in nums if x in kjv),
            "scan_pages": scans_for(nums),
        })
    d["translation"] = secs
    d["language"] = "Greek (Codex Sinaiticus transcription) / English (KJV)"
    d["source"] = "Codex Sinaiticus folio + transcription (codexsinaiticus.org) + Tischendorf 8th edition (bolls.life) + KJV (bible-api.com)"
    d["description"] = re.sub(r"Greek text verbatim from Tischendorf's 8th critical edition \(1869, public domain\) via bolls\.life\.",
        "Greek text is the verbatim Codex Sinaiticus Project transcription of this very folio (uncial letters, lunate sigma, and nomina sacra abbreviations preserved), with Tischendorf's 8th critical edition (1869) shown beneath it as a comparison reading.", d.get("description", ""))
    d["introduction"] = re.sub(r"<li><strong>Original text:</strong>.*?</li>",
        "<li><strong>Original text:</strong> The Codex Sinaiticus Project's verbatim transcription of the folio shown, letter for letter as the scribe wrote it (no accents, lunate sigma ϲ, nomina sacra such as θϲ for θεός and κϲ for κύριος). Beneath it, for comparison, the reading of Tischendorf's 8th critical edition (1869). Where the two differ, the transcription is what the manuscript actually says.</li>",
        d.get("introduction", ""), flags=re.S)
    if (book, ch) in known_short:
        d["introduction"] = re.sub(r"<p><strong>Manuscript note:</strong>.*?</p>", "", d["introduction"]) + f"<p><strong>Manuscript note:</strong> {known_short[(book, ch)]}</p>"
        for sec in secs:
            if not sec["original_text"].strip():
                sec["original_text"] = "<em>[Not present in Codex Sinaiticus. The manuscript's text of Mark ends at 16:8.]</em>"
                sec["scan_note"] = "These verses are not present in Codex Sinaiticus; the folio shown is where the manuscript's text of Mark ends."
    v["primary_greek"] = "csp_transcription"
    v["original_text_source"] = "Codex Sinaiticus Project transcription (codexsinaiticus.org)"
    v["original_text_license"] = "CC BY-NC-SA 3.0"
    v["edition_text_source"] = "bolls.life API (TISCH = Tischendorf 8)"
    v["edition_text_license"] = "public domain (1869)"
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    td = json.loads(DATA.read_text(encoding="utf-8"))
    for t in td["texts"]:
        if t["id"] == d["id"]:
            t["language"] = d["language"]; t["source"] = d["source"]; t["description"] = d["description"]
            if "tischendorf" in t.get("themes", []):
                t["themes"] = [x for x in t["themes"] if x != "tischendorf"] + ["sinaiticus-transcription"]
    DATA.write_text(json.dumps(td, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"ok {len(greek)} csp verses / {len(kjv)} kjv, {len(secs)} sections"

FORCE = False
if __name__ == "__main__":
    FORCE = "--force" in sys.argv
    only = [a for a in sys.argv[1:] if a != "--force"]
    files = sorted(PUB.glob("verified-sinaiticus-*.json"))
    if only: files = [f for f in files if any(o in f.name for o in only)]
    for i, f in enumerate(files, 1):
        r = process(f)
        if r != "not NT": print(f"[{i}/{len(files)}] {f.stem}: {r}", flush=True)
