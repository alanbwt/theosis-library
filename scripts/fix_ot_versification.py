#!/usr/bin/env python3
"""
fix_ot_versification.py — Align Septuagint (Codex Sinaiticus) verse numbering
with KJV verse numbering where the two traditions divide chapters differently,
and add an explicit numbering note to every Old Testament entry where the
verse sets still differ (genuine Septuagint omissions/reorderings).

Known boundary differences handled (LXX/MT = KJV):
  Ecclesiastes 4:17 = KJV 5:1; 5:n = KJV 5:n+1
  Isaiah 8:23 = KJV 9:1; 9:n = KJV 9:n+1
  Jeremiah 8:23 = KJV 9:1; 9:n = KJV 9:n+1
  Nahum 2:1 = KJV 1:15; 2:n = KJV 2:n-1
  Malachi 3:19-24 = KJV 4:1-6
  Joel 3:1-5 = KJV 2:28-32 (Greek fetched from CSP)
  Zechariah 2:1-4 = KJV 1:18-21 (Greek fetched from CSP)
  Jonah 2:1 = KJV 1:17 (Greek fetched from CSP)

Run AFTER fix_sinaiticus_section_folios.py.
"""
import json, re, sys, time
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
iv = importlib.util.module_from_spec(spec); spec.loader.exec_module(iv)

def sups_pairs(html):
    parts = re.split(r"<sup>([\d:]+)</sup>", html)
    return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]

def load(book, ch):
    p = PUB / f"verified-sinaiticus-{book}-{ch}.json"
    return p, json.loads(p.read_text(encoding="utf-8"))

def save(p, d): p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

def kjv_verses(api_name, ch, vrange=None):
    ref = f"{api_name} {ch}" + (f":{vrange}" if vrange else "")
    for attempt in range(6):
        try:
            data = iv.http_get_json(f"https://bible-api.com/{iv.urllib.parse.quote(ref)}?translation=kjv", timeout=20)
            return {v["verse"]: (v["text"] or "").strip() for v in data.get("verses", [])}
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(ref)

def csp_greek(d, book, ch):
    v = d["verification"]
    cands = iv.CSP_BOOKS_OT[book][0]
    for cb in [v.get("csp_book_number")] + cands:
        if not cb: continue
        out = iv.csp_get_chapter_text(cb, ch, v["scan_folio_ids"][-1] if v.get("scan_folio_ids") else v["scan_folio_id"])
        if out: return out
    return {}

def rebuild(d, greek_items, eng_map, chapter, pretty, note):
    """greek_items: list of (label, text) in order. eng_map: label -> (eng_label, text) or None."""
    old = d["translation"]
    def scans_for(labels):
        hits = []
        for os_ in old:
            on = {l for l, _ in sups_pairs(os_["original_text"])}
            if on & set(labels):
                for p in os_.get("scan_pages", []):
                    if p not in hits: hits.append(p)
        return hits or (old[-1].get("scan_pages") or [])
    n = len(greek_items)
    gs = 5 if n <= 20 else 8 if n <= 40 else 10
    secs = []
    for i in range(0, n, gs):
        chunk = greek_items[i:i + gs]
        labels = [l for l, _ in chunk]
        lbl = f"{labels[0]}-{labels[-1]}" if len(labels) > 1 else labels[0]
        g = " ".join(f"<sup>{l}</sup>{t}" for l, t in chunk)
        e = " ".join(f"<sup>{eng_map[l][0]}</sup>{eng_map[l][1]}" for l in labels if eng_map.get(l))
        secs.append({"section": f"{chapter}.{lbl}", "original_ref": f"{pretty} {chapter}:{lbl}",
                     "original_text": g, "text": e, "scan_pages": scans_for(labels)})
    d["translation"] = secs
    d["introduction"] = re.sub(r"<p><strong>Numbering:</strong>.*?</p>", "", d.get("introduction", "")) + f"<p><strong>Numbering:</strong> {note}</p>"
    d["verification"]["versification_fixed"] = True

def shift_chapter(book, ch, api, pretty, delta, extra_first=None, extra_last=None):
    """Greek ch:n pairs with KJV ch:(n+delta). extra_first: (greek_label, kjv_ch, kjv_v) for greek verse pairing outside chapter."""
    p, d = load(book, ch)
    if d["verification"].get("versification_fixed"): return "already"
    greek = []
    for s in d["translation"]: greek += sups_pairs(s["original_text"])
    kj = kjv_verses(api, ch)
    eng = {}
    for l, _ in greek:
        n = int(l); kn = n + delta
        if kn in kj: eng[l] = (str(kn), kj[kn])
    if extra_first:
        gl, kc, kv = extra_first
        eng[gl] = (f"{kc}:{kv}", kjv_verses(api, kc, f"{kv}")[kv])
    note = (f"The Septuagint (and Hebrew) divide this chapter differently from the KJV: Greek verse n here corresponds to KJV "
            f"{ch}:{'n+%d' % delta if delta > 0 else 'n%d' % delta}. English superscripts show the KJV verse number, so the two columns line up by content, not by number.")
    rebuild(d, greek, eng, ch, pretty, note)
    save(p, d); return "ok"

def append_english(book, ch, api, pretty, pairs, note):
    """pairs: list of (greek_label, kjv_ch, kjv_v)"""
    p, d = load(book, ch)
    if d["verification"].get("versification_fixed"): return "already"
    greek = []
    for s in d["translation"]: greek += sups_pairs(s["original_text"])
    kj = kjv_verses(api, ch)
    eng = {l: (l, kj[int(l)]) for l, _ in greek if int(l) in kj}
    cache = {}
    for gl, kc, kv in pairs:
        if kc not in cache: cache[kc] = kjv_verses(api, kc)
        if kv in cache[kc]: eng[gl] = (f"{kc}:{kv}", cache[kc][kv])
    rebuild(d, greek, eng, ch, pretty, note)
    save(p, d); return "ok"

def append_greek(book, ch, api, pretty, greek_ch, greek_vs, kjv_vs, note):
    """Fetch LXX greek_ch:greek_vs from CSP and pair with KJV ch:kjv_vs at the end of this entry."""
    p, d = load(book, ch)
    if d["verification"].get("versification_fixed"): return "already"
    greek = []
    for s in d["translation"]: greek += sups_pairs(s["original_text"])
    kj = kjv_verses(api, ch)
    eng = {l: (l, kj[int(l)]) for l, _ in greek if int(l) in kj}
    gk = csp_greek(d, book, greek_ch)
    missing = [v for v in greek_vs if v not in gk]
    if missing: return f"FAIL CSP lacks {book} {greek_ch}:{missing}"
    for gv, kv in zip(greek_vs, kjv_vs):
        lbl = f"{greek_ch}:{gv}"
        greek.append((lbl, gk[gv]))
        eng[lbl] = (str(kv), kj[kv])
    rebuild(d, greek, eng, ch, pretty, note)
    save(p, d); return "ok"

def annotate_remaining():
    """Add a numbering note to any OT entry whose Greek/English verse sets still differ."""
    n = 0
    for p in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        m = re.match(r"verified-sinaiticus-([a-z0-9]+)-(\d+)$", d["id"])
        if m.group(1) not in iv.CSP_BOOKS_OT or m.group(1) == "ps": continue
        if d["verification"].get("versification_fixed"): continue
        g, e = [], []
        for s in d["translation"]:
            g += [l for l, _ in sups_pairs(s["original_text"])]; e += [l for l, _ in sups_pairs(s["text"])]
        og = sorted(set(g) - set(e), key=lambda x: int(x.split(':')[-1])); oe = sorted(set(e) - set(g), key=lambda x: int(x.split(':')[-1]))
        if not og and not oe: continue
        parts = []
        if oe: parts.append(f"KJV verse{'s' if len(oe)>1 else ''} {', '.join(oe)} of this chapter {'have' if len(oe)>1 else 'has'} no counterpart in the Septuagint text as it stands in Codex Sinaiticus (the Greek either omits, relocates, or numbers {'them' if len(oe)>1 else 'it'} differently).")
        if og: parts.append(f"Greek verse{'s' if len(og)>1 else ''} {', '.join(og)} {'have' if len(og)>1 else 'has'} no KJV counterpart under the same number.")
        note = " ".join(parts) + " Compare by content rather than by verse number. Where the Septuagint lacks a verse found in the Hebrew, that is itself a documented textual difference between the two traditions."
        d["introduction"] = re.sub(r"<p><strong>Numbering:</strong>.*?</p>", "", d.get("introduction", "")) + f"<p><strong>Numbering:</strong> {note}</p>"
        d["verification"]["versification_note"] = note
        save(p, d); n += 1
    return n

if __name__ == "__main__":
    print("eccl-5", shift_chapter("eccl", 5, "ecclesiastes", "Ecclesiastes", +1))
    print("eccl-4", append_english("eccl", 4, "ecclesiastes", "Ecclesiastes", [("17", 5, 1)], "Septuagint Ecclesiastes 4:17 is KJV 5:1; the English for that verse is shown with its KJV reference."))
    print("isa-9", shift_chapter("isa", 9, "isaiah", "Isaiah", +1))
    print("isa-8", append_english("isa", 8, "isaiah", "Isaiah", [("23", 9, 1)], "Septuagint Isaiah 8:23 is KJV 9:1; the English for that verse is shown with its KJV reference."))
    print("jer-9", shift_chapter("jer", 9, "jeremiah", "Jeremiah", +1))
    print("jer-8", append_english("jer", 8, "jeremiah", "Jeremiah", [("23", 9, 1)], "Septuagint Jeremiah 8:23 is KJV 9:1; the English for that verse is shown with its KJV reference. KJV 8:11-12 are absent from the Septuagint text of Codex Sinaiticus."))
    print("nahum-2", shift_chapter("nahum", 2, "nahum", "Nahum", -1, extra_first=("1", 1, 15)))
    print("mal-3", append_english("mal", 3, "malachi", "Malachi", [(str(19+i), 4, 1+i) for i in range(6)], "The Septuagint has no Malachi chapter 4: Greek 3:19-24 are KJV 4:1-6, shown here with their KJV references."))
    print("joel-2", append_greek("joel", 2, "joel", "Joel", 3, [1,2,3,4,5], [28,29,30,31,32], "KJV Joel 2:28-32 are Septuagint Joel 3:1-5; the Greek for those verses is included here from the same Codex Sinaiticus folio, labelled with its Septuagint reference."))
    print("zech-1", append_greek("zech", 1, "zechariah", "Zechariah", 2, [1,2,3,4], [18,19,20,21], "KJV Zechariah 1:18-21 are Septuagint Zechariah 2:1-4; the Greek for those verses is included here, labelled with its Septuagint reference."))
    print("jonah-1", append_greek("jonah", 1, "jonah", "Jonah", 2, [1], [17], "KJV Jonah 1:17 is Septuagint Jonah 2:1; the Greek for that verse is included here, labelled with its Septuagint reference."))
    print("annotated remaining:", annotate_remaining())
