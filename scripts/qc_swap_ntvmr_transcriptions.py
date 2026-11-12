#!/usr/bin/env python3
"""
qc_swap_ntvmr_transcriptions.py: make the manuscript's own diplomatic
transcription the primary Greek for the legacy Codex Vaticanus, Bezae,
Alexandrinus and Washingtonianus chapters, keep Tischendorf's 8th edition as
the per-section comparison text (`edition_text`), and re-derive every
section's scan_pages from the page on which the transcription places each
verse.

Chain of evidence
  1. Transcriptions.
     - NTVMR (INTF Muenster) page transcriptions, one TEI file per page:
         https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID=<doc>&pageID=<pageID>&format=txt
       docIDs 20003 (Vaticanus, GA 03), 20005 (Bezae, GA 05), 20002
       (Alexandrinus, GA 02), 20032 (Washingtonianus, GA 032). Cached by
       scripts/qc_ntvmr_fetch.py in data/sources/qc-legacy/ntvmr/<doc>/.
       Most pages carry a generated header "Creative Commons Attribution 4.0".
       Some pages return an older INTF file whose header says "All rights
       reserved by the INTF" (Bezae Matt 1:20-5:18 and John 18:14-25 [supplement],
       Alexandrinus Luke 15:7-16:1, Washingtonianus Matthew and Luke). Text
       from those pages is NOT published: a chapter that needs one of them
       stays on Tischendorf (its page mapping is still checked; page/verse
       facts come from the CC BY 4.0 NTVMR index as well). Pass
       --allow-all-rights-reserved to override once permission is confirmed.
     - Washingtonianus John has no NTVMR page transcription. It comes from the
       IGNTP transcription of John in GA 032 (04_032.xml, supplement quire
       04_032S.xml; version 2.1, 2013, header: CC BY 4.0), as redistributed in
       https://github.com/vanja-ivancevic/gospel-of-john-tc
       (data/raw/IGNTP_greek_john_transcriptions/), a copy of the IGNTP
       download for John (iohannes.com; that site's TLS certificate had
       expired on 2026-11-12). Cached in data/sources/qc-legacy/ntvmr/igntp-john/.
     Rendering policy: scripts/qc_ntvmr_parse.py (first hand only, nomina
     sacra as written without overline, [supplied], dotted unclear letters,
     [...] for gaps).
  2. Verse to page: the page (and column) whose transcription contains the
     verse, or each part of a verse that crosses a page. This replaces the
     NTVMR range index the entries were built from; the two agree for
     Vaticanus on every page and differ at a few verse boundaries elsewhere
     (scratch comparison run on 2026-11-12; the transcription is what is used).
  3. Page to local image (unchanged files, nothing downloaded):
     - Vaticanus: Vatican page number (NTVMR "folio" field, = Vat.gr.1209
       page) -> vaticanus/vat-b-<book>-<ch>-f<page>.jpg
     - Bezae: folio (Greek is always on the verso) -> bezae/bezae-<book>-<ch>-<fol>.jpg
     - Alexandrinus: NTVMR page -> 1909 British Museum facsimile leaf
       (leaf = 17 + ordinal of the page from pageID 90 = fol. 26r, as in
       import_alexandrinus.py, which read every leaf's printed verse caption)
       -> alexandrinus/alex-f<fol>-leaf<leaf>.jpg. Keyed by leaf because
       NTVMR labels two consecutive leaves "141r/141v".
     - Washingtonianus: NTVMR/IGNTP page -> CSNTM page GA_032_NNNN, decided
       by CSNTM's own verse index (cached in data/sources/washingtonianus_cache)
       for the verses that lie wholly on the page; every page used had a
       unanimous vote. CSNTM page -> Freer image via data/washingtonianus_page_map.json.
     A verse whose page has no local image is not shown and is listed in
     verification.verses_not_shown_no_image.
  4. English: the KJV already in each entry (bible-api.com). A verse the
     manuscript has but the entry lacked is fetched from bible-api.com and
     cached in data/sources/qc-legacy/ntvmr/kjv/.

Sections are rebuilt: a new section starts where a new page or column
starts (capped at 12 verses), so each section's scan_pages are exactly the
pages its verses are written on. A verse crossing a page appears once, in the
section of the page where it begins, and that section lists both pages.

Washingtonianus Matthew and Luke stay as built by import_washingtonianus.py
(CSNTM verse index); scripts/qc_ntvmr_check_w.py compares their pages with the
page on which the NTVMR transcription places each verse (read-only).

Never touches data/texts.json; prints the catalogue row changes instead.

Run from the repo root:
  python3 -I scripts/qc_ntvmr_fetch.py            # fetch / refresh the cache
  python3 -I scripts/qc_swap_ntvmr_transcriptions.py [--ms vaticanus ...] [--force] [--dry-run]
"""
import argparse
import collections
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import qc_ntvmr_parse as P  # noqa: E402

PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
CACHE = P.CACHE
WCACHE = ROOT / "data" / "sources" / "washingtonianus_cache"
TODAY = str(date.today())
MAXV = 12
UA = "TheosisLibrary-QC/1.0 (static reference library)"
TRANSCRIPT_URL = "https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID={doc}&pageID={pid}&format=txt"
IGNTP_URL = ("https://github.com/vanja-ivancevic/gospel-of-john-tc/tree/main/data/raw/"
             "IGNTP_greek_john_transcriptions (04_032.xml, 04_032S.xml)")

BOOKS = {"matt": 1, "mark": 2, "luke": 3, "john": 4, "acts": 5, "romans": 6, "1cor": 7, "2cor": 8,
         "gal": 9, "eph": 10, "phil": 11, "col": 12, "1thess": 13, "2thess": 14, "1tim": 15,
         "2tim": 16, "titus": 17, "philemon": 18, "hebrews": 19, "james": 20, "1peter": 21,
         "2peter": 22, "1john": 23, "2john": 24, "3john": 25, "jude": 26, "rev": 27}
KJV_API = {"matt": "matthew", "mark": "mark", "luke": "luke", "john": "john", "acts": "acts",
           "romans": "romans", "1cor": "1 corinthians", "2cor": "2 corinthians", "gal": "galatians",
           "eph": "ephesians", "phil": "philippians", "col": "colossians", "1thess": "1 thessalonians",
           "2thess": "2 thessalonians", "1tim": "1 timothy", "2tim": "2 timothy", "titus": "titus",
           "philemon": "philemon", "hebrews": "hebrews", "james": "james", "1peter": "1 peter",
           "2peter": "2 peter", "1john": "1 john", "2john": "2 john", "3john": "3 john",
           "jude": "jude", "rev": "revelation"}

MSS = {
    "vaticanus": {"doc": 20003, "name": "Codex Vaticanus", "ga": "GA 03"},
    "bezae": {"doc": 20005, "name": "Codex Bezae", "ga": "GA 05"},
    "alexandrinus": {"doc": 20002, "name": "Codex Alexandrinus", "ga": "GA 02"},
    "washingtonianus": {"doc": 20032, "name": "Codex Washingtonianus", "ga": "GA 032"},
}

# Leaves lost from each codex (verses there are "lost", not "omitted"):
LACUNAE = {
    "alexandrinus": [(1, 1, 1, 25, 5), (4, 6, 50, 8, 52), (8, 4, 13, 12, 6)],
    "bezae": [(1, 1, 1, 1, 20), (1, 6, 20, 9, 2), (1, 27, 2, 27, 12), (4, 1, 16, 3, 26)],
    "washingtonianus": [(2, 15, 13, 15, 37), (4, 14, 26, 16, 6)],
    "vaticanus": [(19, 9, 14, 13, 25)],
}

# Standard Greek (NA) verse numbering vs KJV numbering, applied only when the
# transcription follows the Greek numbering at that point.
REMAP = {
    (25, 1): {"merge": {15: 14}},                  # 3 John: NA 1:14-15 = KJV 1:14
    (8, 13): {"renumber": {13: 14}, "partof": {13: 12}},  # 2 Cor 13: NA 12 = KJV 12-13, NA 13 = KJV 14
    (5, 19): {"partof": {41: 40}},                 # Acts 19: NA 40 = KJV 40-41
    (27, 12): {"extra": {18: "12:18 in the standard Greek numbering; the KJV prints these words at the start of 13:1"}},
}
NUMBERING_NOTES = {
    (25, 1): "The transcription follows the standard Greek numbering, which divides the KJV's verse 14 into verses 14 and 15; both are shown under verse 14.",
    (8, 13): "The transcription follows the standard Greek numbering (13:12-13); the KJV divides the same words as 13:12-14. Greek verse 13 is shown as KJV verse 14, and KJV verse 13 is part of Greek verse 12.",
    (5, 19): "The transcription follows the standard Greek numbering, in which the KJV's verse 41 is the end of verse 40.",
    (27, 12): "The transcription follows the standard Greek numbering, which has a verse 12:18 (\"and he stood upon the sand of the sea\"); the KJV prints these words at the start of 13:1, so verse 18 has Greek but no English here.",
}


SPECIAL_NOTES = {
    ("washingtonianus", "mark", 16): "After verse 14 the codex carries the Freer Logion (κακεινοι απελογουντε "
        "λεγοντες ... κληρονομησωσιν), a passage found in no other manuscript; the transcription includes it "
        "in verse 14, and the KJV has no English for it.",
}
for _c in range(1, 6):
    SPECIAL_NOTES[("washingtonianus", "john", _c)] = (
        "John 1:1-5:11 in this codex is on a replacement quire (fols. 57-64) written by a later hand; its "
        "transcription is the IGNTP file for that supplement (04_032S).")


DESC_TAIL = {
    "vaticanus": "(4th c., Vatican Library, Vat. gr. 1209)",
    "bezae": "(5th c., Cambridge University Library, MS Nn.2.41)",
    "alexandrinus": "(5th c., British Library, Royal MS 1 D. VIII), shown on the 1909 British Museum photographic facsimile",
    "washingtonianus": "(the Freer Gospels, late 4th-early 5th c., Freer Gallery of Art F1906.274), shown on the Freer Gallery's photographs",
}


def parse_ranges(s):
    out = set()
    for part in (s or "").split(","):
        part = part.strip()
        if not part:
            continue
        a, _, b = part.partition("-")
        out |= set(range(int(a), int(b or a) + 1))
    return out


# ---------------------------------------------------------------------------
def sups_pairs(html):
    parts = re.split(r"<sup>(\d+)</sup>", html or "")
    return [(int(parts[i]), parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def ranges(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


def in_lacuna(ms, b, k, v):
    for (bb, c1, v1, c2, v2) in LACUNAE.get(ms, []):
        if bb == b and (c1, v1) <= (k, v) <= (c2, v2):
            return True
    return False


def norm_folio(s):
    m = re.match(r"0*(\d+[rv])", (s or "").strip())
    return m.group(1) if m else ""


def kjv_verse(book_key, ch, v):
    """One KJV verse from bible-api.com (the source of every English verse in
    these entries), cached."""
    d = CACHE / "kjv"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{book_key}-{ch}-{v}.json"
    if not f.exists():
        url = f"https://bible-api.com/{urllib.parse.quote(KJV_API[book_key])}+{ch}:{v}?translation=kjv"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    f.write_bytes(r.read())
                break
            except Exception:
                time.sleep(4 * (attempt + 1))
    if not f.exists():
        return None
    data = json.loads(f.read_text(encoding="utf-8"))
    vs = [x for x in data.get("verses", []) if int(x["chapter"]) == ch and int(x["verse"]) == v]
    return vs[0]["text"].strip() if vs else None


# ---------------------------------------------------------------------------
# Washingtonianus: page -> CSNTM page by CSNTM's verse index
# ---------------------------------------------------------------------------
def csntm_table():
    html = (WCACHE / "csntm_GA_032_view.html").read_text(encoding="utf-8", errors="replace")
    return {int(a): int(re.search(r"(\d{4})", b).group(1))
            for a, b in re.findall(r'imageId="(\d+)"\s+imageName="(GA_032_\d{4}\.jpg)"', html)}


def csntm_lookup(table, osis):
    p = WCACHE / "json" / (hashlib.sha1(f"osis:{osis}".encode()).hexdigest() + ".json")
    if not p.exists():
        return None
    return [table[i] for i in json.loads(p.read_text(encoding="utf-8")) if i in table]


def w_page_map(pages, verses):
    table = csntm_table()
    osis_b = {1: "Matt", 2: "Mark", 3: "Luke", 4: "John"}
    out = {}
    for pg in pages:
        votes = collections.Counter()
        for (b, k, v) in dict.fromkeys(pg["verses"]):
            parts = verses[(b, k, v)]
            if len(parts) != 1 or not parts[0][2]:
                continue
            r = csntm_lookup(table, f"{osis_b[b]}.{k}.{v}")
            if r and len(r) == 1:
                votes[r[0]] += 1
        if votes:
            top, n = votes.most_common(1)[0]
            out[str(pg["pid"])] = {"csntm_page": top, "votes": n, "dissent": sum(votes.values()) - n}
    return out


# ---------------------------------------------------------------------------
class Context:
    """Transcription, page and image data for one manuscript."""

    def __init__(self, ms):
        self.ms = ms
        cfg = MSS[ms]
        self.doc = cfg["doc"]
        self.name = cfg["name"]
        self.pages, self.verses = P.parse_ntvmr_doc(self.doc)
        self.page_by_pid = {p["pid"]: p for p in self.pages}
        self.source_of = {}  # (b,k,v) -> "ntvmr" | "igntp"
        for key in self.verses:
            self.source_of[key] = "ntvmr"
        if ms == "washingtonianus":
            d = CACHE / "igntp-john"
            ipages, iverses = P.parse_igntp_book([d / "04_032S.xml", d / "04_032.xml"])
            for p in ipages:
                self.page_by_pid[p["pid"]] = p
            self.pages += ipages
            for key, val in iverses.items():
                self.verses[key] = val
                self.source_of[key] = "igntp"
        self.images = self._image_index()
        if ms == "washingtonianus":
            self.wmap = w_page_map(self.pages, self.verses)
            (CACHE / "w_page_to_csntm.json").write_text(json.dumps(self.wmap, indent=1), encoding="utf-8")
            self.freer = json.loads((ROOT / "data" / "washingtonianus_page_map.json").read_text(encoding="utf-8"))["pages"]
        if ms == "alexandrinus":
            # facsimile leaf = 17 + ordinal of the NTVMR page from pageID 90 (fol. 26r)
            # onward, as in import_alexandrinus.py (each leaf's printed caption was
            # read there). Keyed by leaf, not folio: NTVMR labels two leaves "141r/141v".
            self.leaf_of, ordinal = {}, 0
            for pm in P.load_meta(self.doc):
                if int(pm["pageID"]) < 90:
                    continue
                self.leaf_of[pm["pageID"]] = 17 + ordinal
                ordinal += 1
            # printed captions per leaf, saved from the entries as import_alexandrinus.py built them
            cp = CACHE / "alexandrinus_page_captions.json"
            self.captions = {int(k): c for k, c in
                             json.loads(cp.read_text(encoding="utf-8"))["captions"].items()}

    def _image_index(self):
        idx = collections.defaultdict(list)
        for f in sorted((SCANS / self.ms).glob("*.jpg")):
            n = f.name
            if self.ms == "vaticanus":
                m = re.search(r"-f(\d+)\.jpg$", n)
                key = m and m.group(1)
            elif self.ms == "bezae":
                m = re.search(r"-(\d{3}[rv])(?:Suppl)?\.jpg$", n)
                key = m and norm_folio(m.group(1))
            elif self.ms == "alexandrinus":
                m = re.match(r"alex-f\w+-leaf(\d+)\.jpg$", n)
                key = m and int(m.group(1))
            else:
                m = re.match(r"w-p(\d{4})-", n)
                key = m and int(m.group(1))
            if key:
                idx[key].append(f"{self.ms}/{n}")
        return idx

    def page_key(self, pid):
        pg = self.page_by_pid[pid]
        if self.ms == "vaticanus":
            return pg["folio"]
        if self.ms == "alexandrinus":
            return self.leaf_of.get(pid)
        if self.ms == "bezae":
            return norm_folio(pg["folio"] or pg["label"])
        w = self.wmap.get(str(pid))
        return w["csntm_page"] if w else None

    def image_for(self, pid, prefer=""):
        files = self.images.get(self.page_key(pid), [])
        for f in files:
            if prefer and prefer in f:
                return f
        return files[0] if files else None

    def page_label(self, pid):
        pg = self.page_by_pid[pid]
        if self.ms == "vaticanus":
            return f"p. {pg['folio']}"
        if self.ms == "bezae":
            return f"fol. {norm_folio(pg['folio'] or pg['label'])}" + (" (supplement)" if "Suppl" in (pg["label"] + pg["content"]) else "")
        if self.ms == "alexandrinus":
            leaf = self.leaf_of.get(pid)
            cap = self.captions.get(leaf, {})
            return f"fol. {cap.get('folio') or norm_folio(pg['folio'])} (facsimile leaf {leaf})"
        cp = self.page_key(pid)
        fol = f"fol. {pg['folio']}, " if re.match(r"^\d+[rv]$", str(pg.get("folio", ""))) else ""
        return f"{fol}CSNTM GA_032_{cp:04d}" if cp else str(pid)

    def place(self, pid, col):
        lab = self.page_label(pid)
        if self.ms in ("vaticanus", "alexandrinus") and col:
            lab += f", col. {col}"
        return lab

    def license_ok(self, key, allow_arr):
        lic = {self.page_by_pid[pid]["license"] for pid, _c, _t in self.verses.get(key, [])}
        return allow_arr or lic <= {"CC BY 4.0"}


# ---------------------------------------------------------------------------
def build_chapter(ctx, d, bk, ch, allow_arr, notes_out):
    """Return a dict with the rebuilt sections and facts, or None to leave
    the entry untouched."""
    b = BOOKS[bk]
    v_old = d["verification"]
    old = d["translation"]
    pretty = re.sub(r"\s+\d+:.*$", "", old[0]["original_ref"]).strip()
    was_tr = v_old.get("primary_greek") in ("ntvmr_transcription", "igntp_transcription")
    tisch, kjv = {}, {}
    for s in old:
        src = s.get("edition_text") if was_tr else s["original_text"]
        for n, t in sups_pairs(src):
            tisch.setdefault(n, t)
        for n, t in sups_pairs(s["text"]):
            kjv.setdefault(n, t)

    na = {v: list(parts) for (bb, k, v), parts in ctx.verses.items() if bb == b and k == ch}
    if not any(t for parts in na.values() for _p, _c, t in parts):
        return {"status": "no_transcription"}

    # versification
    rm = REMAP.get((b, ch), {})
    partof, extra_note, numbering, merged = {}, {}, None, set()
    for src, dst in rm.get("merge", {}).items():
        if src in na and src not in kjv and dst in na:
            na[dst] = na[dst] + na.pop(src)
            merged.add(dst)
            numbering = NUMBERING_NOTES[(b, ch)]
    for src, dst in rm.get("renumber", {}).items():
        if src in na and dst in kjv and dst not in na:
            na[dst] = na.pop(src)
            numbering = NUMBERING_NOTES[(b, ch)]
    for kv, nav in rm.get("partof", {}).items():
        if kv in kjv and kv not in na and nav in na:
            partof[kv] = nav
            numbering = NUMBERING_NOTES[(b, ch)]
    for nav, note in rm.get("extra", {}).items():
        if nav in na and nav not in kjv:
            extra_note[nav] = note
            numbering = NUMBERING_NOTES[(b, ch)]

    has_text = {v for v, parts in na.items() if any(t for _p, _c, t in parts)}
    use_tr = all(ctx.license_ok((b, ch, v), allow_arr) for v in has_text)

    # verses the manuscript has that the entry lacks: add the KJV
    for v in sorted(has_text - set(kjv)):
        if v in extra_note:
            continue
        t = kjv_verse(bk, ch, v)
        if t:
            kjv[v] = t
            notes_out.append(f"added KJV {ch}:{v}")

    verses = sorted(set(kjv) | set(extra_note))
    info = {}
    lost, omitted, no_image = [], [], []
    # verses found lost on an earlier run are no longer in the entry; keep them listed
    for v in sorted(parse_ranges(v_old.get("verses_lost_in_manuscript"))):
        if v not in kjv:
            lost.append(v)
    for v in verses:
        parts = na.get(v)
        if in_lacuna(ctx.ms, b, ch, v) and v not in has_text:
            lost.append(v)
            continue
        if v in has_text:
            parts = [x for x in parts if x[2]]
            info[v] = {"kind": "text", "parts": parts}
        elif parts:
            info[v] = {"kind": "omitted", "parts": parts}
            omitted.append(v)
        elif v in partof:
            info[v] = {"kind": "partof", "parts": [], "of": partof[v]}
        else:
            info[v] = {"kind": "absent", "parts": []}
            omitted.append(v)
    # place verses with no part of their own at the point where they would stand
    shown = [v for v in verses if v in info]
    for i, v in enumerate(shown):
        if info[v]["parts"]:
            continue
        prev = next((info[u]["parts"][-1] for u in reversed(shown[:i]) if info[u]["parts"]), None)
        nxt = next((info[u]["parts"][0] for u in shown[i + 1:] if info[u]["parts"]), None)
        ref = prev or nxt
        if ref is None:
            return {"status": "unplaceable"}
        info[v]["parts"] = [(ref[0], ref[1], "")]
    # verses whose page has no local image: drop the verse if none of its
    # pages has an image; if only a continuation page is missing, keep the
    # part(s) that are shown and say where the rest is
    for v in list(shown):
        parts = info[v]["parts"]
        have = [x for x in parts if ctx.image_for(x[0]) is not None]
        if not have:
            no_image.append(v)
            shown.remove(v)
        elif len(have) < len(parts):
            info[v]["missing"] = [ctx.place(x[0], x[1]) for x in parts if x not in have]
            info[v]["missing_first"] = parts[0] not in have
            info[v]["parts"] = have
    if not shown:
        return {"status": "nothing_shown"}

    # group by the page/column where each verse starts
    groups, cur, cur_key = [], [], None
    for v in shown:
        p0 = info[v]["parts"][0]
        key = (p0[0], p0[1])
        if cur and key != cur_key:
            groups.append(cur)
            cur = []
        cur.append(v)
        cur_key = key
    if cur:
        groups.append(cur)
    chunks = []
    for g in groups:
        # cap a page/column run at MAXV written verses (verses the scribe did
        # not write do not count), split into near-equal chunks
        ntext = sum(1 for v in g if info[v]["kind"] == "text")
        n = max(1, -(-ntext // MAXV))
        size = -(-ntext // n) if ntext else len(g)
        cur, cnt = [], 0
        for v in g:
            if cnt >= size and info[v]["kind"] == "text":
                chunks.append(cur)
                cur, cnt = [], 0
            cur.append(v)
            cnt += info[v]["kind"] == "text"
        if cur:
            chunks.append(cur)

    name = ctx.name
    secs = []
    prefer = f"-{bk}-{ch}-"
    for g in chunks:
        sv, ev = g[0], g[-1]
        lbl = f"{sv}-{ev}" if sv != ev else str(sv)
        pids = []
        for v in g:
            for p, _c, _t in info[v]["parts"]:
                if p not in pids:
                    pids.append(p)
        files = []
        for p in pids:
            f = ctx.image_for(p, prefer)
            if f not in files:
                files.append(f)
        greek, eng = [], []
        for v in g:
            it = info[v]
            if it["kind"] == "text":
                g_txt = P.join_parts([t for _p, _c, t in it["parts"]])
                if it.get("missing"):
                    gap = f"<em>[{'begins' if it['missing_first'] else 'continues'} on {', '.join(it['missing'])}; image not in this library]</em>"
                    g_txt = f"{gap} {g_txt}" if it["missing_first"] else f"{g_txt} {gap}"
            elif it["kind"] == "partof":
                g_txt = f"<em>[these words are part of verse {it['of']} in the Greek numbering]</em>"
            else:
                g_txt = f"<em>[not in {name}]</em>"
            if not use_tr:
                # the Greek column stays Tischendorf's edition for every verse he prints
                g_txt = tisch.get(v) or g_txt
            if g_txt:
                greek.append(f"<sup>{v}</sup>{g_txt}")
            if v in kjv:
                eng.append(f"<sup>{v}</sup>{kjv[v]}")
        # scan note: where each verse starts, and which verses cross a page
        by_place = collections.OrderedDict()
        crossing = []
        for v in g:
            parts = info[v]["parts"]
            p0 = parts[0]
            if info[v]["kind"] != "text":
                continue
            by_place.setdefault(ctx.place(p0[0], p0[1]), []).append(v)
            later = [x for x in parts[1:] if x[0] != p0[0]]
            if later and info[v]["kind"] == "text":
                x = later[0]
                words = " ".join(P.strip_joins(x[2]).split()[:3])
                crossing.append(f"verse {v} continues on {ctx.place(x[0], x[1])} (which begins '{words}')")
        src = "IGNTP transcription" if ctx.source_of.get((b, ch, g[0])) == "igntp" else f"NTVMR transcription (docID {ctx.doc})"
        bits = []
        if by_place:
            bits.append(f"Page from the {src}: " + "; ".join(
                f"verse{'s' if len(vs) > 1 else ''} {ranges(vs)} on {pl}" for pl, vs in by_place.items())
                + ("; " + "; ".join(crossing) if crossing else ""))
        om = [v for v in g if info[v]["kind"] in ("omitted", "absent")]
        if om:
            p0 = info[om[0]]["parts"][0]
            bits.append(f"Verse{'s' if len(om) > 1 else ''} {ranges(om)} {'are' if len(om) > 1 else 'is'} not in "
                        f"{name}; the {src} shows the text passing over {'them' if len(om) > 1 else 'it'} on "
                        f"{ctx.place(p0[0], p0[1])}")
        po = [v for v in g if info[v]["kind"] == "partof"]
        if po:
            bits.append(f"KJV verse {ranges(po)} is part of the Greek verse before it")
        for v in g:
            if info[v].get("missing"):
                bits.append(f"Part of verse {v} is on {', '.join(info[v]['missing'])}, whose image is not in this "
                            f"library; only the part on the page shown is given in the Greek")
        note = ". ".join(bits) + "."
        sec = {"section": f"{ch}.{lbl}", "original_ref": f"{pretty} {ch}:{lbl}",
               "original_text": " ".join(greek), "text": " ".join(eng),
               "scan_pages": files, "scan_note": note}
        sec["_pids"] = pids
        sec["_range"] = (sv, ev)
        secs.append(sec)

    if use_tr:
        lost_set = set(lost) | set(no_image)
        buckets = [[] for _ in secs]
        for t in sorted(tisch):
            if t in lost_set:
                continue
            idx = 0
            for i, s in enumerate(secs):
                if s["_range"][0] <= t:
                    idx = i
            buckets[idx].append(t)
        for s, bucket in zip(secs, buckets):
            s["edition_text"] = " ".join(f"<sup>{t}</sup>{tisch[t]}" for t in bucket)
    repeats = [v for v in shown if info[v]["kind"] == "text" and v not in merged
               and len(info[v]["parts"]) != len({(p, c) for p, c, _t in info[v]["parts"]})]
    partial = [v for v in shown if info[v].get("missing")]
    lost = sorted(set(lost))
    return {"status": "ok", "use_tr": use_tr, "secs": secs, "lost": lost, "omitted": omitted, "partial": partial,
            "ch": ch,
            "no_image": no_image, "numbering": numbering, "pretty": pretty, "repeats": repeats,
            "kjv_added": [v for v in kjv if v not in {n for s in old for n, _ in sups_pairs(s["text"])}],
            "srcs": {ctx.source_of.get((b, ch, v)) for v in has_text}}


# ---------------------------------------------------------------------------
GREEK_POLICY = ("Letters as the first scribe wrote them (corrections by later hands are not shown); "
                "no accents or breathings; the scribe's spelling kept; nomina sacra in their contracted "
                "form without the overline (e.g. θς, ις, κς); letters the transcribers restored where the "
                "page is damaged in square brackets; uncertain letters with a dot below; [...] for text lost "
                "to damage.")


def intro_greek_paragraph(ctx, igntp):
    who = ("the International Greek New Testament Project (IGNTP), transcription of John in GA 032, "
           "version 2.1 (2013)" if igntp else
           "the Institut für Neutestamentliche Textforschung (INTF), Münster, for the New Testament "
           "Virtual Manuscript Room (NTVMR)")
    return (f"<p><strong>Greek text:</strong> a diplomatic transcription of {ctx.name} made by {who}, "
            f"published under a Creative Commons Attribution 4.0 licence. It gives the letters as the first "
            f"scribe wrote them: no accents or breathings, the scribe's own spelling, and the sacred names in "
            f"their contracted form (θς for θεος, ις for ιησους, κς for κυριος; the overline is not reproduced). "
            f"Corrections by later hands are not shown. Letters in square brackets are not legible on the page "
            f"and were restored by the transcribers, a dot under a letter marks an uncertain reading, and [...] "
            f"marks text lost to damage. Beneath each section, for comparison, is Tischendorf's 8th critical "
            f"edition (1869). Where the two differ, the transcription is what the manuscript says. Each section "
            f"is shown with the page on which the transcription places its verses.</p>")


BEZAE_NOTE = ("Codex Bezae is bilingual: at each opening the Greek is on the left-hand (verso) page and the "
              "Latin on the facing right-hand (recto) page. Only the Greek pages are shown here; the Latin "
              "column is not included.")


def update_entry(ctx, path, r, dry):
    d = json.loads(path.read_text(encoding="utf-8"))
    v = d["verification"]
    ms, name = ctx.ms, ctx.name
    secs = r["secs"]
    pids_all = []
    for s in secs:
        for p in s.pop("_pids"):
            if p not in pids_all:
                pids_all.append(p)
        s.pop("_range")
    old_tisch_src = v.get("edition_text_source") or v.get("original_text_source")
    igntp = "igntp" in r["srcs"]
    d["translation"] = secs
    scan_paths = []
    for s in secs:
        for f in s["scan_pages"]:
            if f not in scan_paths:
                scan_paths.append(f)
    v["scan_local_paths"] = scan_paths

    # per-manuscript scan bookkeeping
    if ms == "alexandrinus":
        leaves = []
        for s in secs:
            out = []
            for f in s["scan_pages"]:
                m = re.match(r"alexandrinus/alex-f0*(\w+)-leaf(\d+)\.jpg", f)
                fol, leaf = m.group(1), int(m.group(2))
                if leaf not in leaves:
                    leaves.append(leaf)
                c = ctx.captions.get(leaf, {})
                txt = f"fol. {c.get('folio') or fol} (facsimile leaf {leaf}"
                if c:
                    txt += f"; NTVMR index: {c.get('ntvmr_index', '')}; printed caption: {c.get('printed_caption', '')}"
                out.append(txt + ")")
            s["scan_folios"] = out
        v["scan_facsimile_leaves"] = leaves
        v["scan_folios"] = [ctx.captions.get(l, {}).get("folio") or "" for l in leaves]
        v["page_captions"] = [ctx.captions[l] for l in leaves if l in ctx.captions]
    if ms == "washingtonianus":
        used = {}
        for s in secs:
            out = []
            for f in s["scan_pages"]:
                m = re.match(r"washingtonianus/w-p(\d{4})-(FS-[\d_]+)\.jpg", f)
                n, fid = int(m.group(1)), m.group(2)
                out.append(f"GA_032_{n:04d} = Freer {fid}")
                vs = [x for x, _ in sups_pairs(s["text"])]
                u = used.setdefault(f, {"csntm_image": f"GA_032_{n:04d}.jpg", "freer_id": fid,
                                        "freer_iiif": f"https://ids.si.edu/ids/iiif/{fid}/full/1800,/0/default.jpg",
                                        "verses": []})
                u["verses"] += vs
            s["scan_folios"] = out
        for f, u in used.items():
            u["verses_in_this_chapter"] = ranges(u.pop("verses"))
        v["scan_pages_used"] = used

    if ms == "washingtonianus":
        page_to_image = ("NTVMR/IGNTP page -> CSNTM page GA_032_NNNN by CSNTM's verse index for the verses wholly "
                         "on that page (unanimous for every page used; table in data/sources/qc-legacy/ntvmr/"
                         "w_page_to_csntm.json) -> Freer image via data/washingtonianus_page_map.json")
    elif ms == "alexandrinus":
        page_to_image = ("NTVMR page -> 1909 British Museum facsimile leaf (leaf = 17 + page ordinal from fol. 26r, "
                         "as in import_alexandrinus.py), each leaf's printed verse caption read and recorded in "
                         "page_captions")
    elif ms == "vaticanus":
        page_to_image = "Vat.gr.1209 page number (NTVMR folio field) -> Vatican Library image of that page"
    else:
        page_to_image = "folio (Greek verso pages only) -> Cambridge University Library image of that folio"
    src = "IGNTP transcription of John in GA 032 (verse placement read from its <pb/> page breaks)" if igntp \
        else f"NTVMR page transcriptions for docID {ctx.doc} (one TEI file per page)"
    v["scan_mapping"] = (f"Verse-level, from the {src}: every verse, or each part of a verse that crosses a page, "
                         f"is assigned to the page whose transcription contains it; {page_to_image}. Each "
                         f"section lists every page its verses are written on. Checked {TODAY} by "
                         f"scripts/qc_swap_ntvmr_transcriptions.py.")
    v["section_pages_verified"] = True
    v["verses_not_in_manuscript"] = ranges(r["omitted"])
    v["verses_lost_in_manuscript"] = ranges(r["lost"])
    v["verses_not_shown_no_image"] = ranges(r["no_image"])
    if ms == "alexandrinus":
        v["verses_absent_from_manuscript"] = ranges(sorted(set(r["lost"]) | set(r["omitted"])))
    if ms == "washingtonianus":
        v["verses_absent_from_codex"] = ranges(sorted(set(r["lost"]) | set(r["omitted"])))
        # CSNTM-index bookkeeping from import_washingtonianus.py no longer applies
        for k in ("verses_not_shown_index_gap", "verses_placed_by_enclosure", "verses_not_shown_no_owner_image"):
            v.pop(k, None)

    intro = d.get("introduction", "")
    intro = re.sub(r"<p><strong>Manuscript note:</strong>.*?</p>", "", intro, flags=re.S)
    intro = re.sub(r"<p><strong>Greek text:</strong>.*?</p>", "", intro, flags=re.S)
    intro = re.sub(r"<p><strong>Page check:</strong>.*?</p>", "", intro, flags=re.S)
    intro = re.sub(r"<p><strong>Numbering:</strong> The transcription follows.*?</p>", "", intro, flags=re.S)
    if r["use_tr"]:
        v["primary_greek"] = "igntp_transcription" if igntp else "ntvmr_transcription"
        if igntp:
            v["original_text_source"] = ("IGNTP (International Greek New Testament Project) transcription of John "
                                         "in GA 032, version 2.1 (2013), files 04_032.xml and 04_032S.xml, via "
                                         + IGNTP_URL)
            v["original_text_attribution"] = ("International Greek New Testament Project; XML by the Institute for "
                                              "Textual Scholarship and Electronic Editing, University of Birmingham")
        else:
            v["original_text_source"] = (f"NTVMR transcription of {MSS[ms]['ga']} "
                                         f"(docID {ctx.doc}), INTF Münster, per page: "
                                         + TRANSCRIPT_URL.format(doc=ctx.doc, pid="<pageID>"))
            v["original_text_attribution"] = ("Institut für Neutestamentliche Textforschung (INTF), Münster, "
                                              "New Testament Virtual Manuscript Room")
            v["original_text_pages"] = [p for p in pids_all if isinstance(p, int)]
        v["original_text_license"] = "CC BY 4.0 (stated in the TEI header of each transcription file used)"
        v["original_text_note"] = "Diplomatic transcription of this manuscript. " + GREEK_POLICY
        v["edition_text_source"] = old_tisch_src if "TISCH" in (old_tisch_src or "") or "Tischendorf" in (old_tisch_src or "") \
            else "bolls.life (TISCH = Tischendorf 8th edition)"
        v["edition_text_license"] = "public domain (1869)"
        d["language"] = f"Greek ({name} transcription) / English (KJV)"
        d["source"] = (f"{name} page images + " + ("IGNTP" if igntp else "NTVMR") +
                       " transcription (CC BY 4.0) + Tischendorf 8th edition + KJV")
        d["description"] = (f"{r['pretty']} {r['ch']} from {name} {DESC_TAIL[ms]}. The Greek is a letter-by-letter "
                            f"transcription of the manuscript ({'IGNTP' if igntp else 'NTVMR'}, CC BY 4.0), with "
                            f"Tischendorf's edition for comparison and the King James Version in English; each "
                            f"section is shown on the page that carries it.")
        # replace the old Greek/Original-text list items
        intro = re.sub(r"<li><strong>Original text:</strong>.*?</li>",
                       "<li><strong>Original text:</strong> the manuscript's own text, from a diplomatic transcription "
                       "(see Greek text below), with Tischendorf's 8th critical edition (1869) for comparison.</li>",
                       intro, flags=re.S)
        intro = re.sub(r"<li><strong>Greek:</strong>.*?</li>",
                       "<li><strong>Greek:</strong> the manuscript's own text, from a diplomatic transcription (see "
                       "Greek text below), with Tischendorf's 8th critical edition (1869) for comparison.</li>",
                       intro, flags=re.S)
        for old_txt in ("; the Greek verse numbers are Tischendorf's own and are not re-aligned",
                        "; this numbering applies only to the Tischendorf comparison text; the transcription "
                        "and the English use the standard numbering",
                        ". This affects only the Tischendorf comparison text; the transcription and the "
                        "English use the standard numbering"):
            intro = intro.replace(old_txt, ". This affects only the Tischendorf comparison text")
        intro = intro.replace(", which supplies the page for each section.",
                              ". The page for each section now comes from the NTVMR transcription itself, which "
                              "records the page and column on which every verse is written.")
        intro = intro.replace("Verses the index cannot place on a surviving page are not shown.",
                              "For this chapter the page of each verse is taken from the transcription itself, "
                              "which records where every page begins; CSNTM's index confirms which photograph "
                              "shows that page.")
        intro += intro_greek_paragraph(ctx, igntp)
    else:
        v["primary_greek"] = "tischendorf"
        why = r.get("why", "")
        v["original_text_note"] = ("Critical edition text (Tischendorf 8th edition), not a transcription of this "
                                   "manuscript. " + why)
        intro += (f"<p><strong>Page check:</strong> {why} The sections were re-checked against the page on which "
                  f"the transcription places each verse, so every section shows the page(s) that carry it.</p>")
    if ms == "bezae":
        if BEZAE_NOTE not in intro:
            intro += f"<p>{BEZAE_NOTE}</p>"
        tn = d.setdefault("translator_notes", [])
        if BEZAE_NOTE not in tn:
            tn.append(BEZAE_NOTE)
    mn = []
    if r["omitted"]:
        mn.append(f"Not written in {name}: verse{'s' if len(r['omitted']) > 1 else ''} {ranges(r['omitted'])}. "
                  f"The English is shown with a bracketed note in the Greek column.")
    if r["lost"]:
        mn.append(f"Lost from {name} (missing or damaged leaves): verse{'s' if len(r['lost']) > 1 else ''} "
                  f"{ranges(r['lost'])}; not shown.")
    if r["no_image"]:
        mn.append(f"Verse{'s' if len(r['no_image']) > 1 else ''} {ranges(r['no_image'])} "
                  f"{'are' if len(r['no_image']) > 1 else 'is'} on a page whose image is not in this library yet; not shown.")
    if r.get("partial"):
        mn.append(f"Verse{'s' if len(r['partial']) > 1 else ''} {ranges(r['partial'])} continue{'' if len(r['partial']) > 1 else 's'} "
                  f"on a page whose image is not in this library; the Greek gives only the part on the page shown.")
    if r["repeats"]:
        mn.append(f"The scribe wrote verse{'s' if len(r['repeats']) > 1 else ''} {ranges(r['repeats'])} twice; "
                  f"both copies are given in the Greek.")
    m_id = re.match(rf"verified-{ms}-([a-z0-9]+)-(\d+)$", d["id"])
    special = SPECIAL_NOTES.get((ms, m_id.group(1), int(m_id.group(2))))
    if special and r["use_tr"]:
        mn.append(special)
    if mn:
        intro += "<p><strong>Manuscript note:</strong> " + " ".join(mn) + "</p>"
    if r["numbering"] and r["use_tr"]:
        intro += f"<p><strong>Numbering:</strong> {r['numbering']}</p>"
    d["introduction"] = intro
    v["verified_date"] = TODAY
    if not dry:
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    return d


ROW_RULES = []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", nargs="*", default=list(MSS))
    ap.add_argument("--only", default="", help="substring of entry ids to process")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-all-rights-reserved", action="store_true")
    args = ap.parse_args()
    summary = {}
    for ms in args.ms:
        ctx = Context(ms)
        ctx.ga = MSS[ms]["ga"]
        stats = collections.Counter()
        rows = []
        for path in sorted(PUB.glob(f"verified-{ms}-*.json")):
            if args.only and args.only not in path.stem:
                continue
            d = json.loads(path.read_text(encoding="utf-8"))
            vv = d["verification"]
            if vv.get("section_pages_verified") and vv.get("verified_date") and not args.force \
                    and vv.get("primary_greek") in ("ntvmr_transcription", "igntp_transcription", "tischendorf"):
                stats["already"] += 1
                continue
            m = re.match(rf"verified-{ms}-([a-z0-9]+)-(\d+)$", d["id"])
            bk, ch = m.group(1), int(m.group(2))
            if ms == "washingtonianus" and bk in ("matt", "luke") and not args.allow_all_rights_reserved:
                stats["kept: W Matt/Luke, transcription all rights reserved, CSNTM mapping kept"] += 1
                continue
            notes = []
            r = build_chapter(ctx, d, bk, ch, args.allow_all_rights_reserved, notes)
            if r["status"] != "ok":
                stats[f"untouched: {r['status']}"] += 1
                print(f"  {d['id']}: {r['status']}")
                continue
            if not r["use_tr"]:
                r["why"] = ("The NTVMR transcription of this chapter comes partly from pages whose files state "
                            "\"All rights reserved by the INTF\", so the Greek shown is Tischendorf's edition.")
                stats["kept on Tischendorf (all-rights-reserved transcription pages), pages re-checked"] += 1
            else:
                stats["swapped to transcription"] += 1
            update_entry(ctx, path, r, args.dry_run)
            extra = []
            if r["omitted"]:
                extra.append(f"not in ms {ranges(r['omitted'])}")
            if r["lost"]:
                extra.append(f"lost {ranges(r['lost'])}")
            if r["no_image"]:
                extra.append(f"no image {ranges(r['no_image'])}")
            if r["kjv_added"]:
                extra.append(f"KJV added {ranges(r['kjv_added'])}")
            print(f"  {d['id']}: {'transcription' if r['use_tr'] else 'Tischendorf'}, "
                  f"{len(r['secs'])} sections" + (f" ({'; '.join(extra)})" if extra else ""))
            dd = json.loads(path.read_text(encoding="utf-8")) if not args.dry_run else d
            rows.append({"id": dd["id"], "language": dd["language"], "source": dd["source"],
                         "description": dd["description"], "primary_greek": dd["verification"]["primary_greek"]})
        if rows and not args.dry_run:
            rp = CACHE / "texts_json_row_changes.json"
            allrows = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
            for row in rows:
                allrows[row["id"]] = row
            rp.write_text(json.dumps(allrows, indent=1, ensure_ascii=False), encoding="utf-8")
        summary[ms] = dict(stats)
        print(ms, dict(stats))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
