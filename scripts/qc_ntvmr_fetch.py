#!/usr/bin/env python3
"""
qc_ntvmr_fetch.py: cache NTVMR (INTF Muenster) page metadata and per-page TEI
transcriptions for the four legacy NT manuscripts.

  docID 20002  Codex Alexandrinus (GA 02)
  docID 20003  Codex Vaticanus    (GA 03)
  docID 20005  Codex Bezae        (GA 05)
  docID 20032  Codex Washingtonianus (GA 032)

Metadata:  https://ntvmr.uni-muenster.de/community/vmr/api/metadata/manuscript/get/?docID=N&format=json
Transcript: https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID=N&pageID=P&format=txt

Cache: data/sources/qc-legacy/ntvmr/meta-<docID>.json and <docID>/<pageID>.xml.
Only pages whose NTVMR index lists biblical content are fetched. Cache-first,
safe to re-run. Run from the repo root:  python3 -I scripts/qc_ntvmr_fetch.py [docID ...]
"""
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "sources" / "qc-legacy" / "ntvmr"
API = "https://ntvmr.uni-muenster.de/community/vmr/api"
UA = "TheosisLibrary-QC/1.0 (static reference library)"
DOCS = [20002, 20003, 20005, 20032]


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def meta(doc):
    p = CACHE / f"meta-{doc}.json"
    if not p.exists() or p.stat().st_size < 10000:
        p.write_bytes(get(f"{API}/metadata/manuscript/get/?docID={doc}&format=json"))
    return json.loads(p.read_text(encoding="utf-8"))["data"]["manuscript"]


def fetch_page(doc, pid):
    out = CACHE / str(doc) / f"{pid}.xml"
    if out.exists() and out.stat().st_size > 500:
        return "cached"
    for attempt in range(4):
        try:
            data = get(f"{API}/transcript/get/?docID={doc}&pageID={pid}&format=txt")
            out.write_bytes(data)
            return "ok"
        except Exception as e:  # network hiccup: back off and retry
            time.sleep(3 * (attempt + 1))
            err = e
    return f"fail {err}"


def main():
    docs = [int(a) for a in sys.argv[1:]] or DOCS
    for doc in docs:
        m = meta(doc)
        (CACHE / str(doc)).mkdir(parents=True, exist_ok=True)
        pids = [p["pageID"] for p in m["pages"]["page"] if (p.get("biblicalContent") or "").strip()]
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda pid: fetch_page(doc, pid), pids))
        fails = [(pid, r) for pid, r in zip(pids, res) if r.startswith("fail")]
        print(f"{doc}: {len(pids)} pages, {res.count('ok')} fetched, {res.count('cached')} cached, {len(fails)} failed")
        for f in fails[:10]:
            print("   ", f)


if __name__ == "__main__":
    main()
