#!/usr/bin/env python3
"""
import_sinaiticus_extra.py — The rest of Codex Sinaiticus: the Septuagint
deuterocanon (Tobit, Judith, 1 & 4 Maccabees, Wisdom, Sirach), Song of Songs
(the surviving end), and the two Apostolic-Fathers texts bound in the codex
(Epistle of Barnabas, Shepherd of Hermas).

Per chapter:
  scan     — CSP folio(s), resolved PER SECTION by verse (fix_sinaiticus_section_folios)
  original — Codex Sinaiticus Project verbatim transcription (CC BY-NC-SA 3.0)
  English  — KJV Apocrypha 1611/1769 (ebible.org, PD) for Tobit, Judith, Wisdom,
             Sirach, 1 Maccabees; Brenton 1851 (ebible.org, PD) for 4 Maccabees;
             KJV via bible-api.com for Song of Songs; J. B. Lightfoot 1891 (PD)
             for Barnabas and Hermas.
Re-runnable; skips existing entries unless --force.
"""
import json, re, sys, time, html
from datetime import date
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SRC = ROOT / "data" / "sources"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "sinaiticus-folios"
spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
iv = importlib.util.module_from_spec(spec); spec.loader.exec_module(iv)
spec2 = importlib.util.spec_from_file_location("ff", ROOT / "scripts" / "fix_sinaiticus_section_folios.py")
ff = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(ff)

# key: (csp_book, pretty (as CSP names it), english source, era, max chapters)
BOOKS = {
    "tobit":    (10, "Tobit",              ("usfm", "ebible-eng-kjv/41-TOBeng-kjv.usfm"),        "deutero", 14),
    "judith":   (11, "Judith",             ("usfm", "ebible-eng-kjv/42-JDTeng-kjv.usfm"),        "deutero", 16),
    "1macc":    (12, "1 Maccabees",        ("usfm", "ebible-eng-kjv/52-1MAeng-kjv.usfm"),        "deutero", 16),
    "4macc":    (13, "4 Maccabees",        ("usfm", "ebible-eng-Brenton/59-4MAeng-Brenton.usfm"), "deutero", 18),
    "song":     (29, "Song of Songs",      ("bibleapi", "song of solomon"),                     "ot", 8),
    "wisdom":   (30, "Wisdom of Solomon",  ("usfm", "ebible-eng-kjv/45-WISeng-kjv.usfm"),        "deutero", 19),
    "sirach":   (31, "Sirach",             ("usfm", "ebible-eng-kjv/46-SIReng-kjv.usfm"),        "deutero", 51),
    "barnabas": (60, "Barnabas",           ("lightfoot", "lightfoot-barnabas.html"),            "apostolic", 21),
    "hermas":   (61, "Shepherd of Hermas", ("lightfoot", "lightfoot-hermas.html"),              "apostolic", 114),
}
TITLE = {"tobit": "Tobit", "judith": "Judith", "1macc": "1 Maccabees", "4macc": "4 Maccabees", "song": "Song of Songs",
         "wisdom": "Wisdom of Solomon", "sirach": "Sirach (Ecclesiasticus)", "barnabas": "Epistle of Barnabas", "hermas": "Shepherd of Hermas"}
ENG_LABEL = {"usfm-kjv": "King James Version Apocrypha (1611; 1769 text)", "usfm-brenton": "Brenton's Septuagint (1851)",
             "bibleapi": "King James Version (1611)", "lightfoot": "J. B. Lightfoot, The Apostolic Fathers (1891)"}

# Hermas: Whittaker continuous chapter numbers → (division, book, chapter) for Lightfoot
def hermas_map():
    m = {}; n = 1
    for vis, chs in ((1, 4), (2, 4), (3, 13), (4, 3), (5, 1)):
        for c in range(1, chs + 1): m[n] = ("Vision", vis, c); n += 1
    for man, chs in ((1, 1), (2, 1), (3, 1), (4, 4), (5, 2), (6, 2), (7, 1), (8, 1), (9, 1), (10, 3), (11, 1), (12, 6)):
        for c in range(1, chs + 1): m[n] = ("Mandate", man, c); n += 1
    for sim, chs in ((1, 1), (2, 1), (3, 1), (4, 1), (5, 7), (6, 5), (7, 1), (8, 11), (9, 33), (10, 4)):
        for c in range(1, chs + 1): m[n] = ("Similitude", sim, c); n += 1
    return m
HERMAS = hermas_map()

_usfm_cache = {}
def load_usfm(rel):
    if rel in _usfm_cache: return _usfm_cache[rel]
    txt = (SRC / rel).read_text(encoding="utf-8")
    out = {}; ch = 0
    for line in txt.splitlines():
        m = re.match(r"\\c (\d+)", line)
        if m: ch = int(m.group(1)); out.setdefault(ch, {}); continue
        parts = re.split(r"\\v (\d+)\s*", line)
        for i in range(1, len(parts), 2):
            v = int(parts[i]); t = parts[i + 1]
            t = re.sub(r"\\f\s.*?\\f\*", "", t); t = re.sub(r"\\x\s.*?\\x\*", "", t)  # footnotes / xrefs
            t = re.sub(r"\\[a-z]+\d?\*?\s?", " ", t).strip()
            t = re.sub(r"\s+", " ", t)
            if t: out.setdefault(ch, {})[v] = (out.get(ch, {}).get(v, "") + " " + t).strip()
    _usfm_cache[rel] = out; return out

_lf_cache = {}
def load_lightfoot(rel, book):
    if rel in _lf_cache: return _lf_cache[rel]
    t = (SRC / rel).read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S); t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(re.sub(r"\s+", " ", t))
    out = {}
    if book == "barnabas":
        for m in re.finditer(r"Barnabas (\d+):(\d+)\s+(.*?)(?=Barnabas \d+:\d+|$)", t):
            out.setdefault(int(m.group(1)), {})[int(m.group(2))] = m.group(3).replace("*", "").strip()
    else:
        # "Vision 2 1[5]:1 text 1[5]:2 text ... Mandate 1 1[26]:1 ..."  ([n] = continuous chapter number)
        div = None; divnum = None; last_w = None; last_v = 0
        pat = re.compile(r"(Vision|Mandate|Parable|Similitude) (\d+)\s|(\d+)(?:\[(\d+)\])?:(\d+)\s+(.*?)(?=(?:Vision|Mandate|Parable|Similitude) \d+\s|\d+(?:\[\d+\])?:\d+\s|$)")
        for m in pat.finditer(t):
            if m.group(1):
                div = "Similitude" if m.group(1) == "Parable" else m.group(1); divnum = int(m.group(2)); continue
            if div is None: continue
            c, v, body = int(m.group(3)), int(m.group(5)), m.group(6).strip()
            w = int(m.group(4)) if m.group(4) else c   # continuous (Whittaker) chapter; Vision 1 has no bracket
            if w == last_w and v <= last_v: w = last_w + 1   # source repeats a label for the next chapter
            elif last_w is not None and w < last_w: w = last_w + (1 if v <= last_v else 0)
            last_w, last_v = w, v
            out.setdefault(w, {})[v] = body.replace("*", "")
    _lf_cache[rel] = out; return out

def english_for(book, ch):
    kind, arg = BOOKS[book][2]
    if kind == "usfm":
        return load_usfm(arg).get(ch, {})
    if kind == "bibleapi":
        for attempt in range(5):
            try:
                d = iv.fetch_kjv_chapter(arg, ch); return {v["verse"]: (v["text"] or "").strip() for v in d.get("verses", [])}
            except Exception: time.sleep(5 * (attempt + 1))
        return {}
    if kind == "lightfoot":
        data = load_lightfoot(arg, book)
        if book == "barnabas": return data.get(ch, {})
        return data.get(ch, {})

def find_first_folio(csp_book, ch):
    for v in (1, 2, 3, 5, 8):
        for side in ("r", "v"):
            try:
                f = iv.csp_get_folio(csp_book, ch, side=side)
            except Exception:
                f = None
            if f: return f
            # csp_get_folio hardcodes verse=1; try direct verse url
            url = f"{iv.CSP_BASE}/en/manuscript.aspx?book={csp_book}&chapter={ch}&lid=en&side={side}&verse={v}"
            try: h = iv.http_get_text(url)
            except Exception: continue
            m = re.search(r"zoom\.init\([^)]*'(Q\d+_\d+[rv]_[A-Z]\d+)'", h)
            if m:
                info = re.search(r'manuscriptVerseInfo">\s*([^<]+?)\s*&nbsp;', h)
                fol = re.search(r"folio</i>:\s*([A-Za-z0-9]+)", h)
                return {"folio_id": m.group(1), "verse_info": info.group(1).strip() if info else "", "library_folio": fol.group(1) if fol else ""}
    return None

def build(book, ch, force=False):
    csp_book, pretty, (kind, arg), era, _ = BOOKS[book]
    tid = f"verified-sinaiticus-{book}-{ch}"
    path = PUB / f"{tid}.json"
    if path.exists() and not force: return "skip"
    folio = find_first_folio(csp_book, ch)
    if not folio: return "no folio (chapter not in codex)"
    greek = iv.csp_get_chapter_text(csp_book, ch, folio["folio_id"], max_walk=10)
    greek = {k: v for k, v in greek.items() if v.strip()}
    if not greek: return "no transcription"
    eng = english_for(book, ch)
    if not eng: return f"no English for {book} {ch}"
    nums = sorted(set(greek) | set(eng))
    n = len(nums); gs = 5 if n <= 20 else 8 if n <= 40 else 10
    secs = []
    for i in range(0, n, gs):
        chunk = nums[i:i + gs]
        sv, ev = chunk[0], chunk[-1]; lbl = f"{sv}-{ev}" if sv != ev else str(sv)
        secs.append({"section": f"{ch}.{lbl}", "original_ref": f"{TITLE[book]} {ch}:{lbl}",
                     "original_text": " ".join(f"<sup>{x}</sup>{greek[x]}" for x in chunk if x in greek),
                     "text": " ".join(f"<sup>{x}</sup>{eng[x]}" for x in chunk if x in eng),
                     "scan_pages": []})
    # per-section folios
    all_files, infos = [], []
    for s in secs:
        gn = [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s["original_text"])] or [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s["text"])]
        fids = []
        for vv in (gn[0], gn[-1]):
            fid = ff.lookup(csp_book, pretty, ch, vv)
            if fid and fid not in fids: fids.append(fid)
        if not fids:
            if all_files: s["scan_pages"] = [all_files[-1]]; s["scan_note"] = "These verses are not present in Codex Sinaiticus; the folio shown is where the manuscript's text ends."; continue
            return f"no folio for section {s['section']}"
        files = [ff.ensure_scan(fid, book, ch) for fid in fids]
        s["scan_pages"] = [f"sinaiticus-folios/{f}" for f in files]
        for fid, f in zip(fids, files):
            rel = f"sinaiticus-folios/{f}"
            if rel not in all_files:
                all_files.append(rel); fo = ff.cache["folios"].get(fid, {})
                infos.append(f"{fid} (lib. folio {fo.get('library_folio', '?')}): {fo.get('verse_info', '')}")
    ff.save_cache()
    for s in secs:
        if not re.sub(r"<[^>]+>", "", s["text"]).strip():
            s["text"] = "<em>[The KJV numbers this chapter differently and has no verse under these numbers; compare by content with the preceding section.]</em>"
    # any English-only sections (verses absent from the codex) get a placeholder
    for s in secs:
        if not re.sub(r"<[^>]+>", "", s["original_text"]).strip():
            s["original_text"] = "<em>[Not present in Codex Sinaiticus as transcribed by the Codex Sinaiticus Project. The English is shown for reference.]</em>"
    eng_key = "usfm-brenton" if book == "4macc" else "usfm-kjv" if kind == "usfm" else kind
    eng_label = ENG_LABEL[eng_key]
    eng_src = {"usfm-kjv": "ebible.org eng-kjv USFM (KJV with Apocrypha)", "usfm-brenton": "ebible.org eng-Brenton USFM",
               "bibleapi": "bible-api.com (KJV)", "lightfoot": "Lightfoot 1891 via earlychristianwritings.com transcription"}[eng_key]
    notes = []
    if book == "tobit":
        notes.append("<p><strong>Recension:</strong> Codex Sinaiticus preserves the <em>longer</em> Greek recension of Tobit (GII). The King James Version translates the <em>shorter</em> recension (GI, as in Vaticanus and Alexandrinus). Wording therefore differs substantially between the two columns even where verse numbers coincide; that difference is itself one of the most important facts about the text of Tobit, and it can be read directly off the folio.</p>")
    if book == "sirach":
        notes.append("<p><strong>Numbering:</strong> Verse numbering of Sirach differs between the Greek manuscripts, Rahlfs, and the KJV in many chapters. Compare by content rather than by number.</p>")
    if book == "hermas":
        d = HERMAS.get(ch); 
        if d: notes.append(f"<p><strong>Numbering:</strong> Chapter {ch} in the continuous (Whittaker) numbering used by the Codex Sinaiticus Project is {d[0]} {d[1]}, chapter {d[2]} in Lightfoot's traditional division, which the English column follows.</p>")
    if book == "song":
        notes.append("<p><strong>Survival:</strong> Only the end of Song of Songs survives in Codex Sinaiticus (the folio that also begins Wisdom of Solomon). Chapters not on a surviving folio are not in the library.</p>")
    if book in ("barnabas", "hermas"):
        notes.append("<p><strong>Why this is here:</strong> Codex Sinaiticus binds this text after Revelation, alongside the canonical books. Reading it on the same parchment as the Gospels is primary evidence for how a 4th-century Christian community treated it.</p>")
    g_sup = sorted(set(greek)); e_sup = sorted(set(eng))
    og = [x for x in e_sup if x not in g_sup]; oe = [x for x in g_sup if x not in e_sup]
    if og or oe:
        parts = []
        if og: parts.append(f"English verse{'s' if len(og)>1 else ''} {', '.join(map(str, og))} {'have' if len(og)>1 else 'has'} no Greek under that number in the codex as transcribed")
        if oe: parts.append(f"Greek verse{'s' if len(oe)>1 else ''} {', '.join(map(str, oe))} {'have' if len(oe)>1 else 'has'} no English counterpart under that number")
        notes.append(f"<p><strong>Numbering:</strong> {'; '.join(parts)}. Compare by content.</p>")
    today = str(date.today())
    entry = {
        "id": tid, "title": f"{TITLE[book]}, Chapter {ch}", "slug": tid,
        "language": f"Greek (Codex Sinaiticus) / English ({eng_label.split(' (')[0]})",
        "source": f"Codex Sinaiticus folio + transcription (codexsinaiticus.org) + {eng_label}",
        "description": f"{TITLE[book]} chapter {ch}. Manuscript page scan(s) from Codex Sinaiticus hosted by the Codex Sinaiticus Project, with the Project's verbatim transcription of the Greek and the English of {eng_label}.",
        "introduction": ("<p>This entry meets the strict three-criteria standard of the Theosis Library:</p><ol>"
            "<li><strong>Manuscript scan:</strong> The actual folio(s) of Codex Sinaiticus containing this chapter, from the Codex Sinaiticus Project (codexsinaiticus.org). Each section links to the specific folio holding its verses.</li>"
            "<li><strong>Original text:</strong> The Codex Sinaiticus Project's verbatim transcription of the folio shown (uncial letters, lunate sigma, nomina sacra preserved).</li>"
            f"<li><strong>English translation:</strong> {eng_label}, public domain, retrieved verbatim from {eng_src}.</li></ol>" + "".join(notes)),
        "translator_notes": [], "translation": secs,
        "verification": {
            "scan_source": "Codex Sinaiticus Project (codexsinaiticus.org)", "scan_license": "CC BY-NC-SA 3.0 (academic/scholarly use)",
            "scan_folio_id": re.search(r"(Q\d+_\d+[rv]_[A-Z]\d+)", all_files[0]).group(1), "scan_folio_ids": [re.search(r"(Q\d+_\d+[rv]_[A-Z]\d+)", f).group(1) for f in all_files],
            "scan_local_path": all_files[0], "scan_local_paths": all_files, "scan_folio_ranges": infos, "scan_verse_info": infos[0].split(": ", 1)[-1] if infos else "",
            "section_folios_verified": True, "csp_book_number": csp_book,
            "original_text_source": "Codex Sinaiticus Project transcription (codexsinaiticus.org)", "original_text_license": "CC BY-NC-SA 3.0",
            "primary_greek": "csp_transcription", "csp_greek_refreshed": True,
            "translation_source": eng_src, "translation_license": "public domain", "translator": eng_label,
            "verified_date": today},
    }
    path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"ok {len(secs)} sections, {len(all_files)} folios, {len(greek)} greek / {len(eng)} eng verses"

def sync_texts(ids):
    p = ROOT / "data" / "texts.json"; d = json.loads(p.read_text(encoding="utf-8")); by = {t["id"]: t for t in d["texts"]}
    for tid in ids:
        pp = PUB / f"{tid}.json"
        if not pp.exists(): continue
        pub = json.loads(pp.read_text(encoding="utf-8")); book = re.match(r"verified-sinaiticus-([a-z0-9]+)-", tid).group(1)
        era = BOOKS[book][3]
        by[tid] = {"id": tid, "title": pub["title"], "author_id": "biblical-authors" if era != "apostolic" else "apostolic-fathers",
            "language": pub["language"], "era": {"deutero": "Old Testament", "ot": "Old Testament", "apostolic": "Apostolic"}[era],
            "tradition": "orthodox", "category": "sacred-text",
            "date_approx": {"deutero": "c. 3rd-1st c. BCE (composition); 4th c. (Codex Sinaiticus)", "ot": "c. 1500-400 BCE (composition); 3rd c. BCE (LXX); 4th c. (Codex Sinaiticus)", "apostolic": "c. 70-150 AD (composition); 4th c. (Codex Sinaiticus)"}[era],
            "century": -2 if era == "deutero" else -5 if era == "ot" else 2,
            "source": pub["source"], "description": pub["description"],
            "themes": ["bible" if era != "apostolic" else "apostolic-fathers", {"deutero": "deuterocanon", "ot": "old-testament", "apostolic": "early-church"}[era], "septuagint" if era != "apostolic" else "sinaiticus-transcription", "codex-sinaiticus", "verified"],
            "is_first_translation": False, "status": "published", "slug": tid,
            "scans": {"pages": [{"file": pub["verification"]["scan_local_path"], "caption": f"Codex Sinaiticus folio {pub['verification'].get('scan_folio_id')}"}]}}
    d["texts"] = list(by.values()); p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; force = "--force" in sys.argv
    books = args or list(BOOKS)
    done = []
    for b in books:
        for ch in range(1, BOOKS[b][4] + 1):
            try: r = build(b, ch, force)
            except Exception as e: r = f"ERROR {e}"
            print(f"{b}-{ch}: {r}", flush=True)
            if r.startswith("ok") or r == "skip": done.append(f"verified-sinaiticus-{b}-{ch}")
            time.sleep(0.5)
    sync_texts(done)
