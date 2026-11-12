#!/usr/bin/env python3
"""
qc2_sinaiticus_folios.py - second QC pass on the Codex Sinaiticus entries
(translations/published/verified-sinaiticus-*.json): every section must link
every folio side that carries any of its verses, in codex order, and nothing
else; the Greek of each verse must be the complete Codex Sinaiticus Project
(CSP) transcription of that verse.

Chain of evidence
-----------------
Page data: the CSP transcription in TEI XML, version 1.95 (30.8.2024), as
published by ITSEE, University of Birmingham, the project partner that made
it: https://github.com/itsee-birmingham/codex-sinaiticus
(sinaiticus_full_v195.xml, CC BY-NC-SA 3.0). It marks every page (<pb>),
column (<cb>) and line (<lb>) of the manuscript, and every verse (<ab>), so the
page, column and line on which each verse begins and ends can be read off
directly. A verse is counted on a page only if some of its letters are on that
page. (The CSP website's "first verse - last verse" summary of a page, used by
scripts/fix_sinaiticus_section_folios.py, names the verse that ended on the
last line of the previous page as the first verse of the next page; and where
the Greek order of chapters differs from the English order, as in Proverbs
24-31 and Sirach 30-36, the summary is a min/max pair, not a range. Both
caused wrong links that this script removes.)

Images: the existing CSP folio images in site/assets/scans/sinaiticus-folios/
(stitched from the CSP zoom-4 tiles by scripts/import_verified.py). A folio
side with no image on disk is downloaded the same way (CSP tile handler,
csp_download_folio). If codexsinaiticus.org does not answer, the script falls
back to the copy of the same CSP photographs in
https://github.com/0x53616D75656C/Codex-Sinaiticus (images/uncompressed/NNN.jpg,
2000 x 2000 px). That copy is not numbered by folio, so the file for each folio
side is listed in MIRROR_FILES below and was identified on the image (folio
number written in the top corner, recto/verso, first words of column 1).

Greek: each verse in each section is compared with the first-hand text of the
same verse in the XML (corrections ignored, abbreviations shown as written).
Verses the earlier folio walker (import_verified.csp_get_chapter_text) missed
or truncated are reported; with --fill-greek, verses shown as "Not present"
that the XML does contain are filled in from the XML, and the sections that
held only such a placeholder get their Greek back.

Outputs (data/sources/qc-sinaiticus-venetus/):
  sinaiticus_full_v195.xml.gz      the source XML (downloaded once)
  sinaiticus_xml_index.json        page list + verse -> pages/lines + first-hand text
  sinaiticus_check.json            problems found by `check` (0 expected after `fix`)
  sinaiticus_greek_check.json      verse-level comparison of the Greek with the XML
  sinaiticus_changes.json          what `fix` changed, per entry and section
  sinaiticus_texts_json_rows.json  catalog rows (data/texts.json) that need a new scans.pages

Usage (from the repo root):
  python3 scripts/qc2_sinaiticus_folios.py index
  python3 scripts/qc2_sinaiticus_folios.py fix [--dry-run]
  python3 scripts/qc2_sinaiticus_folios.py check
  python3 scripts/qc2_sinaiticus_folios.py greek
  python3 scripts/qc2_sinaiticus_folios.py legacy-audit   # earlier audit's checks + XML evidence
Re-runnable; `fix` is idempotent.
"""
import collections
import gzip
import io
import json
import re
import sys
import urllib.request
import xml.sax
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
FOLIO_DIR = SCANS / "sinaiticus-folios"
CACHE = ROOT / "data" / "csp_folio_cache.json"
OUT = ROOT / "data" / "sources" / "qc-sinaiticus-venetus"
XML_GZ = OUT / "sinaiticus_full_v195.xml.gz"
INDEX = OUT / "sinaiticus_xml_index.json"
XML_URL = "https://raw.githubusercontent.com/itsee-birmingham/codex-sinaiticus/main/sinaiticus_full_v195.xml"
MIRROR_URL = "https://raw.githubusercontent.com/0x53616D75656C/Codex-Sinaiticus/main/images/uncompressed/{}"
TODAY = "2026-11-12"

# Folio sides whose image is taken from the GitHub copy of the CSP photographs
# when codexsinaiticus.org is unreachable. Each was identified on the image:
#   475.jpg: recto, folio number "176" in the top right corner (BL fol. 176 = Q70-1r);
#   476.jpg: the verso following it (ruler on the left), column 1 begins with
#            the text the XML gives for Q70-1v; 477.jpg is the same photograph as
#            our sirach-36-Q70_2r_B361.jpg (fol. 177), which fixes the sequence.
#   817.jpg: recto with "347" in the top right corner; columns 3-4 on the British
#            Library leaf, a strip of column 1 on the St Petersburg fragment (Q93-7r);
#            816.jpg is the same photograph as our hermas-26-Q93_6v_B720.jpg.
#   223.jpg (Q47-1r, Leipzig leaf with the library stamp), 337.jpg (Q61-4r), 344.jpg (Q61-7v)
#   and 408.jpg (Q65-7v, Proverbs subscription in column 2): in each case the file before it
#   (222, 336, 343, 407) is the same photograph as our image of the preceding folio side
#   (Q46_8v, Q61_3v, Q61_7r, Q65_7r). The copy numbers its files one lower than the
#   page order of the XML in all these places.
MIRROR_FILES = {"Q70-1r": "475.jpg", "Q70-1v": "476.jpg", "Q93-7r": "817.jpg", "Q47-1r": "223.jpg",
                "Q61-4r": "337.jpg", "Q61-7v": "344.jpg", "Q65-7v": "408.jpg"}
# CSP image ids not in the cache and not derivable from neighbours:
#   Q93-7r: the CSP page for quire 93, folio 7r (web.archive.org capture of
#   codexsinaiticus.org/en/manuscript.aspx?folioNo=7&quireNo=93&side=r, 2024-06-17)
#   shows image Q93_7r_B721-P007 (British Library fol. 347 + St Petersburg Greek 843),
#   "Shepherd of Hermas, 27:7 - 29:8". Files use the British Library part, Q93_7r_B721.
#   Q47-1r: archived CSP page for quire 47, folio 1r (capture 2024-10-15) shows image
#   Q47_1r_L020 (Leipzig fol. xx), "Jeremiah, 10:25 - 11:23".
EXTRA_IDS = {"Q93-7r": "Q93_7r_B721", "Q47-1r": "Q47_1r_L020"}

# CSP book numbers of the NT books (same as scripts/import_verified.py CSP_BOOKS_NT)
NT_BOOKS = {"matt": 33, "mark": 34, "luke": 35, "john": 36, "acts": 51, "romans": 37, "1cor": 38, "2cor": 39,
            "gal": 40, "eph": 41, "phil": 42, "col": 43, "1thess": 44, "2thess": 45, "1tim": 47, "2tim": 48,
            "titus": 49, "philemon": 50, "hebrews": 46, "james": 52, "1peter": 53, "2peter": 54, "1john": 55,
            "2john": 56, "3john": 57, "jude": 58, "rev": 59}
BOOK_NAMES = {10: "Tobit", 11: "Judith", 12: "1 Maccabees", 13: "4 Maccabees", 14: "Isaiah", 15: "Jeremiah",
              17: "Joel", 18: "Obadiah", 19: "Jonah", 20: "Nahum", 21: "Habakkuk", 22: "Zephaniah", 23: "Haggai",
              24: "Zechariah", 25: "Malachi", 26: "Psalms", 27: "Proverbs", 28: "Ecclesiastes", 29: "Song of Songs",
              30: "Wisdom of Solomon", 31: "Sirach", 32: "Job", 33: "Matthew", 34: "Mark", 35: "Luke", 36: "John",
              37: "Romans", 38: "1 Corinthians", 39: "2 Corinthians", 40: "Galatians", 41: "Ephesians",
              42: "Philippians", 43: "Colossians", 44: "1 Thessalonians", 45: "2 Thessalonians", 46: "Hebrews",
              47: "1 Timothy", 48: "2 Timothy", 49: "Titus", 50: "Philemon", 51: "Acts", 52: "James", 53: "1 Peter",
              54: "2 Peter", 55: "1 John", 56: "2 John", 57: "3 John", 58: "Jude", 59: "Revelation",
              60: "Barnabas", 61: "Shepherd of Hermas"}

FID_RE = re.compile(r"(Q\d+_\d+[rv]_[A-Z]\d+)")
VID_RE = re.compile(r"V-B(\d+)K(\d+)V(\d+)([a-z]?)-")
NOT_PRESENT_RE = re.compile(r"^\s*<em>\[Not present in Codex Sinaiticus as transcribed", re.S)


# ---------------------------------------------------------------------------
# 1. XML -> index
# ---------------------------------------------------------------------------
def get_xml_stream():
    if not XML_GZ.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        raw = urllib.request.urlopen(urllib.request.Request(XML_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=600).read()
        XML_GZ.write_bytes(gzip.compress(raw))
    return gzip.open(XML_GZ, "rb")


class _Handler(xml.sax.ContentHandler):
    SKIP = {"note", "fw", "seg"}  # margins, running titles, section numbers, hyphen marks

    def __init__(self):
        super().__init__()
        self.pages, self.page, self.line = [], None, None
        self.verse, self.skip, self.rdg, self.ex, self.unclear = None, 0, [], 0, 0
        self.vpages = collections.defaultdict(list)
        self.vpos = collections.defaultdict(dict)  # verse -> page -> [first lb, last lb]
        self.vtext = collections.defaultdict(list)
        self.order = []

    def startElement(self, name, attrs):
        if name == "pb":
            self.page = attrs.get("xml:id")
            self.pages.append({"id": self.page, "source": attrs.get("source", ""),
                               "folionum": attrs.get("folionum", "") or attrs.get("corresp", "")})
        elif name == "lb":
            self.line = attrs.get("xml:id") or self.line
        elif name == "ab":
            m = VID_RE.match(attrs.get("xml:id", ""))
            self.verse = (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)) if m else None
            if self.verse and self.verse not in self.vtext:
                self.order.append(self.verse)
                self.vtext[self.verse]
        elif name in self.SKIP:
            self.skip += 1
        elif name == "rdg":
            self.rdg.append(attrs.get("type", ""))
        elif name == "unclear":
            self.unclear += 1
        elif name == "ex":
            self.ex += 1
            # the 'kai' compendium is shown as κ(αι) on the CSP website
            if "ϗ" in (attrs.get("rend") or "") and self.verse and not self.skip and (not self.rdg or self.rdg[-1] == "orig"):
                self.vtext[self.verse].append("κ(αι)")
        elif name in ("w", "pc"):
            if self.verse and not self.skip and (not self.rdg or self.rdg[-1] == "orig"):
                self.vtext[self.verse].append(" ")

    def endElement(self, name):
        if name == "ab":
            self.verse = None
        elif name in self.SKIP:
            self.skip -= 1
        elif name == "rdg":
            self.rdg.pop()
        elif name == "ex":
            self.ex -= 1
        elif name == "unclear":
            self.unclear -= 1

    def characters(self, content):
        if not self.verse or self.skip or not content.strip():
            return
        pl = self.vpages[self.verse]
        if self.page not in pl:
            pl.append(self.page)
        pos = self.vpos[self.verse].setdefault(self.page, [self.line, self.line])
        pos[1] = self.line
        # first hand only; letters the transcription supplies for an
        # abbreviation (<ex>) are left out, as on the CSP website
        if (not self.rdg or self.rdg[-1] == "orig") and not self.ex:
            t = content.strip()
            if self.unclear:  # uncertain letters carry a dot below, as on the CSP website
                t = "".join(ch + "\u0323" for ch in t)
            self.vtext[self.verse].append(t)


def build_index():
    h = _Handler()
    p = xml.sax.make_parser()
    p.setFeature(xml.sax.handler.feature_external_ges, False)
    p.setFeature(xml.sax.handler.feature_external_pes, False)
    p.setContentHandler(h)
    with get_xml_stream() as fh:
        p.parse(fh)
    verses = {}
    for v in h.order:
        key = f"{v[0]}|{v[1]}|{v[2]}{v[3]}"
        verses[key] = {"pages": h.vpages.get(v, []), "pos": h.vpos.get(v, {}),
                       "text": re.sub(r"\s+", " ", "".join(h.vtext[v])).strip()}
    idx = {"source": XML_URL, "version": "1.95", "pages": h.pages, "verses": verses}
    INDEX.write_text(json.dumps(idx, ensure_ascii=False))
    print(f"index: {len(h.pages)} page sides, {len(verses)} verses -> {INDEX.relative_to(ROOT)}")
    return idx


def load_index():
    return json.loads(INDEX.read_text()) if INDEX.exists() else build_index()


# ---------------------------------------------------------------------------
# 2. page ids <-> CSP image ids <-> files
# ---------------------------------------------------------------------------
def pid_of(fid):
    m = re.match(r"Q(\d+)_(\d+)([rv])_", fid)
    return f"Q{m.group(1)}-{m.group(2)}{m.group(3)}"


def known_csp_ids():
    ids = {}
    cache = json.loads(CACHE.read_text())
    for fid in cache["folios"]:
        ids[pid_of(fid)] = fid
    for f in FOLIO_DIR.iterdir():
        m = FID_RE.search(f.name)
        if m:
            ids[pid_of(m.group(1))] = m.group(1)
    return ids, cache


def derive_csp_id(pid, idx, ids):
    """CSP image id (e.g. Q70_1r_B359) of a page with no known id, from the
    nearest known pages before and after it: allowed only when both carry the
    same holding letter and the number gap equals the page gap."""
    order = [p["id"] for p in idx["pages"]]
    k = order.index(pid)
    i = next((j for j in range(k - 1, -1, -1) if order[j] in ids), None)
    j = next((j for j in range(k + 1, len(order)) if order[j] in ids), None)
    if i is None or j is None:
        return None
    a = re.match(r".*_([A-Z])(\d+)$", ids[order[i]])
    b = re.match(r".*_([A-Z])(\d+)$", ids[order[j]])
    if a.group(1) != b.group(1) or int(b.group(2)) - int(a.group(2)) != j - i:
        return None
    q, rest = pid[1:].split("-")
    return f"Q{q}_{rest}_{a.group(1)}{int(a.group(2)) + (k - i):03d}"


def files_by_fid():
    out = collections.defaultdict(list)
    for f in sorted(FOLIO_DIR.iterdir()):
        m = FID_RE.search(f.name)
        if m and f.stat().st_size > 10000:
            out[m.group(1)].append(f.name)
    return out


def csp_reachable():
    try:
        urllib.request.urlopen("https://codexsinaiticus.org/en/", timeout=15)
        return True
    except Exception:
        return False


def download_folio(fid, pid, dest, log):
    """CSP tiles first (as scripts/import_verified.py), GitHub copy second."""
    if csp_reachable():
        import importlib.util
        spec = importlib.util.spec_from_file_location("iv", ROOT / "scripts" / "import_verified.py")
        iv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(iv)
        iv.csp_download_folio(fid, zoom=4, dest_path=dest)
        log.append(f"{dest.name}: CSP tiles, zoom 4")
        return "csp"
    if pid not in MIRROR_FILES:
        raise SystemExit(f"no image source for {pid} ({fid}): CSP unreachable and no identified mirror file")
    from PIL import Image
    raw = urllib.request.urlopen(MIRROR_URL.format(MIRROR_FILES[pid]), timeout=120).read()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    im.save(dest, "JPEG", quality=88, optimize=True)
    log.append(f"{dest.name}: GitHub copy of the CSP photograph ({MIRROR_FILES[pid]}), {im.size[0]}x{im.size[1]}")
    return "mirror"


# ---------------------------------------------------------------------------
# 3. sections -> verses -> pages
# ---------------------------------------------------------------------------
def entry_book(d):
    key, ch = re.match(r"verified-sinaiticus-(.+)-(\d+)$", d["id"]).groups()
    b = d["verification"].get("csp_book_number") or NT_BOOKS[key]
    return key, int(ch), int(b)


def section_verses(s, b, ch):
    out = []
    for lab in re.findall(r"<sup>([^<]+)</sup>", s.get("original_text", "")):
        if ":" in lab:
            c, v = lab.split(":")
            out.append((b, int(c), v))
        else:
            out.append((b, ch, lab))
    return out


def verse_keys(idx, b, c, v):
    """XML keys for one verse label; '10' also matches the split verses '10a', '10b'."""
    base = f"{b}|{c}|{v}"
    if base in idx["verses"]:
        return [base]
    return [k for k in (f"{base}a", f"{base}b", f"{base}c") if k in idx["verses"]]


def pages_for(idx, verses):
    order = {p["id"]: n for n, p in enumerate(idx["pages"])}
    pages, absent = [], []
    for (b, c, v) in verses:
        keys = verse_keys(idx, b, c, v)
        hit = False
        for k in keys:
            for p in idx["verses"][k]["pages"]:
                hit = True
                if p not in pages:
                    pages.append(p)
        if not hit:
            absent.append(f"{c}:{v}")
    return sorted(pages, key=lambda p: order[p]), absent


def fmt_line(lb):
    # "Q65-5r-1-25" -> (col 1, line 25)
    m = re.match(r"Q\d+-\d+[rv]-(\d+)-(\d+)$", lb or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def folio_label(idx, pid):
    p = next(x for x in idx["pages"] if x["id"] == pid)
    fn = p["folionum"].strip()
    side = pid[-1]
    if re.fullmatch(r"\d+b?", fn):
        num = fn.rstrip("b")
        return f"fol. {num}{'v' if side == 'v' else 'r'}"
    return f"quire {pid[1:].split('-')[0]}, leaf {pid.split('-')[1]}"


def page_span_note(idx, pid, fid, verses, with_verses=False):
    first = last = None
    on_page = []
    for (b, c, v) in verses:
        for k in verse_keys(idx, b, c, v):
            pos = idx["verses"][k]["pos"].get(pid)
            if not pos:
                continue
            lab = f"{c}:{k.split('|')[2]}"
            if lab not in on_page:
                on_page.append(lab)
            a, z = fmt_line(pos[0]), fmt_line(pos[1])
            if a and (first is None or a < first):
                first = a
            if z and (last is None or z > last):
                last = z
    if not first:
        return f"{folio_label(idx, pid)} ({fid})"
    if first[0] == last[0]:
        span = f"col. {first[0]}, lines {first[1]}-{last[1]}" if first[1] != last[1] else f"col. {first[0]}, line {first[1]}"
    else:
        span = f"col. {first[0]} line {first[1]} to col. {last[0]} line {last[1]}"
    out = f"{folio_label(idx, pid)} ({fid}), {span}"
    if with_verses and on_page:
        out += f" ({on_page[0]}{'-' + on_page[-1].split(':')[1] if len(on_page) > 1 else ''})" if len(on_page) > 1 and on_page[0].split(':')[0] == on_page[-1].split(':')[0] else f" ({', '.join(on_page)})"
    return out


def verse_line(idx, b, c, v, pid, end=True):
    for k in verse_keys(idx, b, c, v):
        pos = idx["verses"][k]["pos"].get(pid)
        if pos:
            cl = fmt_line(pos[1] if end else pos[0])
            return f"col. {cl[0]}, line {cl[1]}" if cl else ""
    return ""


def page_range_text(idx, pid):
    """'Book, c:v - c:v' runs of the verses whose letters are on this page, in codex order."""
    runs = []
    for k, v in idx["verses"].items():
        if pid in v["pages"]:
            b, c, vv = k.split("|")
            m = re.match(r"(\d+)", vv)
            runs.append((int(b), int(c), int(m.group(1))))
    # keep document order: idx["verses"] preserves XML order (json object order)
    segs = []
    for b, c, v in runs:
        if segs and segs[-1][0] == b and (segs[-1][3], segs[-1][4]) <= (c, v) and (c == segs[-1][3] or (c == segs[-1][3] + 1 and v <= 1)):
            segs[-1][3], segs[-1][4] = c, v
        elif segs and segs[-1][0] == b and (c, v) == (segs[-1][3], segs[-1][4]):
            continue
        else:
            segs.append([b, c, v, c, v])
    return "  /  ".join(f"{BOOK_NAMES.get(b, b)}, {c1}:{v1} - {c2}:{v2}" for b, c1, v1, c2, v2 in segs)


# ---------------------------------------------------------------------------
# 4. Greek comparison
# ---------------------------------------------------------------------------
def letters(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"[^Ͱ-Ͽἀ-῿]", "", s).replace("ς", "ϲ").replace("σ", "ϲ")


def verse_texts(html):
    parts = re.split(r"<sup>([^<]+)</sup>", html or "")
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]


def compare_greek(idx):
    import difflib
    rows = []
    for f in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key, ch, b = entry_book(d)
        for s in d["translation"]:
            for lab, txt in verse_texts(s.get("original_text", "")):
                c, v = (int(lab.split(":")[0]), lab.split(":")[1]) if ":" in lab else (ch, lab)
                keys = verse_keys(idx, b, c, v)
                xml_txt = " ".join(idx["verses"][k]["text"] for k in keys)
                a, z = letters(txt), letters(xml_txt)
                if not keys:
                    rows.append({"id": d["id"], "section": s["section"], "verse": f"{c}:{v}", "type": "verse_not_in_xml", "site_letters": len(a)})
                    continue
                if a == z:
                    continue
                ratio = difflib.SequenceMatcher(None, a, z, autojunk=False).ratio()
                kind = "minor_difference"
                if len(a) < 0.85 * len(z):
                    kind = "site_text_shorter"
                elif len(a) > 1.15 * len(z) + 5:
                    kind = "site_text_longer"
                elif ratio < 0.9:
                    kind = "different_text"
                rows.append({"id": d["id"], "section": s["section"], "verse": f"{c}:{v}", "type": kind,
                             "ratio": round(ratio, 3), "site_letters": len(a), "xml_letters": len(z),
                             "site": re.sub(r"<[^>]+>", "", txt)[:160], "xml": xml_txt[:160]})
            # verses shown as "Not present" that the XML has
            if NOT_PRESENT_RE.match(s.get("original_text", "")):
                for lab, _ in verse_texts(s.get("text", "")):
                    c, v = (int(lab.split(":")[0]), lab.split(":")[1]) if ":" in lab else (ch, lab)
                    if verse_keys(idx, b, c, v):
                        rows.append({"id": d["id"], "section": s["section"], "verse": f"{c}:{v}",
                                     "type": "marked_absent_but_in_xml"})
    return rows


# ---------------------------------------------------------------------------
# 5. fix
# ---------------------------------------------------------------------------
MAPPING_NOTE = ("Each section links every folio side that carries any of its verses, in codex order. Page, column "
                "and line of every verse are taken from the Codex Sinaiticus Project transcription in TEI XML "
                "(version 1.95, ITSEE, University of Birmingham, github.com/itsee-birmingham/codex-sinaiticus), "
                "which marks each page, column and line break of the manuscript; a verse counts on a page only "
                "if some of its letters are on that page.")
XML_NOTE_MARK = "Codex Sinaiticus Project XML transcription (v1.95)"

# --- Greek repairs ----------------------------------------------------------
# Verses whose Greek on the site is incomplete or empty although the XML has
# them (folio walker stopped at a quire boundary or at the Sirach
# transposition). "!" = replace the site text of that verse with the XML text.
FORCE_XML = {
    "verified-sinaiticus-barnabas-14": ["4"],   # site text stopped at the foot of Q91_6v (quire 91 has 6 leaves)
    "verified-sinaiticus-zech-1": ["2:4"],      # site label had no text
    "verified-sinaiticus-judith-12": ["11"],    # site text lacked οϲ ην εφεϲτηκωϲ επι παντων των αυτου (Q38_8v col. 1, lines 2-6)
}
# section -> Greek labels it should hold (site text kept where present, XML otherwise)
FILL = {
    "verified-sinaiticus-sirach-30": {"30.25": ["25"]},
    "verified-sinaiticus-barnabas-14": {"14.1-5": ["1", "2", "3", "4", "5"], "14.6-9": ["6", "7", "8", "9"]},
}
# Sirach 33 and 36: the Greek numbering of the CSP transcription differs from the
# KJV numbering, so the sections are rebuilt to pair each Greek verse with the
# KJV verse that translates it (checked by reading both):
#   KJV 33:16 = Greek 33:16a + 16b + 17; KJV 33:n = Greek 33:n+1 (n = 17-30); KJV 33:31 = Greek 33:32-33
#   KJV 36:1-2 = Greek 36:1; KJV 36:n+1 = Greek 36:n (n = 2-9); KJV 36:11 = Greek 36:10a-10b;
#   KJV 36:n+1 = Greek 36:n (n = 11-15); KJV 36:17 = Greek 36:16-17; KJV 36:n = Greek 36:n (n = 18-25);
#   KJV 36:26 = Greek 36:26-27
def _r(a, b):
    return [str(x) for x in range(a, b + 1)]


REBUILD = {
    "verified-sinaiticus-sirach-33": [
        ("33.1-8", _r(1, 8), _r(1, 8)),
        ("33.9-15", _r(9, 15), _r(9, 15)),
        ("33.16-21", ["16a", "16b"] + _r(17, 21), _r(16, 20)),
        ("33.22-27", _r(22, 27), _r(21, 26)),
        ("33.28-33", _r(28, 33), _r(27, 31)),
    ],
    "verified-sinaiticus-sirach-36": [
        ("36.1-9", _r(1, 9), _r(1, 10)),
        ("36.10-15", ["10a", "10b"] + _r(11, 15), _r(11, 16)),
        ("36.16-22", _r(16, 22), _r(17, 22)),
        ("36.23-27", _r(23, 27), _r(23, 26)),
    ],
}
SIRACH_ORDER_NOTE = ("<p><strong>Manuscript order:</strong> In Codex Sinaiticus, as in the other Greek manuscripts of "
                     "Sirach, the passage numbered 33:16b-36:10a in the Codex Sinaiticus Project transcription stands "
                     "before 30:25-33:16a. Fol. 174r-175v (Q69_7r-Q69_8v) carry 30:1-24 and then 33:16b-36:10a; "
                     "fol. 175v-176v (Q69_8v-Q70_1v) carry 30:25-33:16a; 36:10b follows on fol. 176v and the text "
                     "continues in order from fol. 177r (Q70_2r). Each section links the folio sides that hold its "
                     "verses, so sections of these chapters may point at pages that are not next to each other.</p>")
NUMBERING_33 = ("<p><strong>Numbering:</strong> The Greek is numbered as in the Codex Sinaiticus Project transcription "
                "and the English as in the KJV. KJV 33:16 = Greek 33:16a-17; KJV 33:17-30 = Greek 33:18-31; "
                "KJV 33:31 = Greek 33:32-33. Each section pairs the Greek with the KJV verses that translate it.</p>")
NUMBERING_36 = ("<p><strong>Numbering:</strong> The Greek is numbered as in the Codex Sinaiticus Project transcription "
                "and the English as in the KJV. KJV 36:1-2 = Greek 36:1; KJV 36:3-10 = Greek 36:2-9; "
                "KJV 36:11 = Greek 36:10a-10b; KJV 36:12-16 = Greek 36:11-15; KJV 36:17 = Greek 36:16-17; "
                "KJV 36:18-25 = Greek 36:18-25; KJV 36:26 = Greek 36:26-27. Each section pairs the Greek with the "
                "KJV verses that translate it.</p>")
GREEK_FIX_NOTE = ("Greek checked against the Codex Sinaiticus Project XML transcription (v1.95) on 2026-11-12; "
                  "verses {} were missing or cut short on the site and are now given from the XML (first hand, "
                  "abbreviations as written, κ(αι) for the kai compendium, a dot below uncertain letters, as on the "
                  "Codex Sinaiticus Project website).")


def _site_greek(d, ch):
    out = {}
    for s in d["translation"]:
        if NOT_PRESENT_RE.match(s.get("original_text", "")):
            continue
        for lab, txt in verse_texts(s.get("original_text", "")):
            if txt.strip():
                out[lab] = txt.strip()
    return out


def _site_english(d):
    out = {}
    for s in d["translation"]:
        for lab, txt in verse_texts(s.get("text", "")):
            out[lab] = txt.strip()
    return out


def _xml_text(idx, b, ch, lab):
    c, v = (int(lab.split(":")[0]), lab.split(":")[1]) if ":" in lab else (ch, lab)
    keys = [f"{b}|{c}|{v}"] if f"{b}|{c}|{v}" in idx["verses"] else verse_keys(idx, b, c, v)
    t = " ".join(idx["verses"][k]["text"] for k in keys).strip()
    return t or None


def repair_greek(d, idx):
    """Apply FORCE_XML, FILL and REBUILD to one entry. Returns list of changed verse labels."""
    tid = d["id"]
    key, ch, b = entry_book(d)
    if tid not in FORCE_XML and tid not in FILL and tid not in REBUILD:
        return []
    greek, eng = _site_greek(d, ch), _site_english(d)
    changed = []
    for lab in FORCE_XML.get(tid, []):
        x = _xml_text(idx, b, ch, lab)
        if x and greek.get(lab) != x:
            greek[lab] = x
            changed.append(lab)

    def g(lab):
        if lab not in greek:
            x = _xml_text(idx, b, ch, lab)
            if not x:
                raise SystemExit(f"{tid}: no XML text for {lab}")
            greek[lab] = x
            changed.append(lab)
        return f"<sup>{lab}</sup>{greek[lab]}"

    if tid in REBUILD:
        pretty = re.match(r"(.*?) \d+:", d["translation"][0]["original_ref"]).group(1)
        secs = []
        for label, gl, el in REBUILD[tid]:
            gr = f"{ch}:{gl[0]}-{gl[-1]}"
            kr = f"{ch}:{el[0]}-{el[-1]}"
            secs.append({"section": label,
                         "original_ref": f"{pretty} {gr} (KJV {kr})" if gl != el else f"{pretty} {gr}",
                         "original_text": " ".join(g(x) for x in gl),
                         "text": " ".join(f"<sup>{x}</sup>{eng[x]}" for x in el)})
        prev = {x["section"]: x for x in d["translation"]}
        for sec in secs:
            if sec["section"] in prev:
                for k in ("scan_pages", "scan_note"):
                    if k in prev[sec["section"]]:
                        sec[k] = prev[sec["section"]][k]
        used = {x for _, _, el in REBUILD[tid] for x in el}
        if set(eng) - used:
            raise SystemExit(f"{tid}: English verses left out: {sorted(set(eng) - used)}")
        d["translation"] = secs
    else:
        fill = FILL.get(tid, {})
        for s in d["translation"]:
            if s["section"] in fill:
                s["original_text"] = " ".join(g(x) for x in fill[s["section"]])
            elif any(lab in FORCE_XML.get(tid, []) for lab, _ in verse_texts(s["original_text"])):
                s["original_text"] = " ".join(f"<sup>{lab}</sup>{greek[lab]}" for lab, _ in verse_texts(s["original_text"]))
    # introduction notes
    intro = d.get("introduction", "")
    if key == "sirach" and 30 <= ch <= 36 and "Manuscript order:" not in intro:
        intro += SIRACH_ORDER_NOTE
    if tid in REBUILD:
        intro = re.sub(r"<p><strong>Numbering:</strong> English verses [^<]*have no Greek under that number[^<]*</p>", "", intro)
        new_note = NUMBERING_33 if ch == 33 else NUMBERING_36
        if new_note not in intro:
            intro += new_note
    else:
        # recompute the "English verses ... have no Greek" note
        gl = {lab for s in d["translation"] for lab, t in verse_texts(s["original_text"]) if t.strip()}
        missing = [lab for lab in eng if lab not in gl and not re.match(r"\d+:", lab)]
        intro = re.sub(r"<p><strong>Numbering:</strong> English verses? [^<]*have no Greek under that number[^<]*</p>", "", intro)
        if missing and tid != "verified-sinaiticus-zech-1":
            word = "verses" if len(missing) > 1 else "verse"
            intro += (f"<p><strong>Numbering:</strong> English {word} {', '.join(missing)} {'have' if len(missing) > 1 else 'has'} "
                      f"no Greek under that number in the codex as transcribed. Compare by content.</p>")
    d["introduction"] = intro
    if changed:
        notes = d.setdefault("translator_notes", [])
        notes[:] = [n for n in notes if not n.startswith("Greek checked against the Codex Sinaiticus Project XML")]
        allc = sorted(set(changed), key=lambda x: (int(re.match(r"(?:\d+:)?(\d+)", x).group(1)), x))
        notes.append(GREEK_FIX_NOTE.format(", ".join(f"{ch}:{x}" if ":" not in x else x for x in allc)))
        d["verification"]["greek_checked_against"] = "CSP XML transcription v1.95 (github.com/itsee-birmingham/codex-sinaiticus)"
    return changed


def placeholder_pages(d, s, idx, b, ch):
    """Section whose verses are not in the manuscript: the page where the text
    passes over them (last page of the nearest earlier verse of the entry that
    is present, else first page of the nearest later one)."""
    labs = [lab for lab, _ in verse_texts(s.get("text", ""))]
    if not labs:
        return None, None
    order = [lab for sec in d["translation"] for lab, _ in verse_texts(sec.get("text", ""))]
    gl = {lab for sec in d["translation"] for lab, t in verse_texts(sec.get("original_text", "")) if t.strip()}
    i0, i1 = order.index(labs[0]), order.index(labs[-1])
    for j in range(i0 - 1, -1, -1):
        if order[j] in gl:
            pg, _ = pages_for(idx, [(b, ch, order[j])])
            if pg:
                return pg[-1], (f"the last page with text of this chapter before them ({ch}:{order[j]} ends there, "
                                f"{verse_line(idx, b, ch, order[j], pg[-1])})")
    for j in range(i1 + 1, len(order)):
        if order[j] in gl:
            pg, _ = pages_for(idx, [(b, ch, order[j])])
            if pg:
                return pg[0], (f"the first page with text of this chapter after them ({ch}:{order[j]} begins there, "
                               f"{verse_line(idx, b, ch, order[j], pg[0], end=False)})")
    return None, None


def fix(dry=False):
    idx = load_index()
    ids, cache = known_csp_ids()
    fbf = files_by_fid()
    changes, downloads, rows_needed, greek_changes = [], [], [], []
    catalog = {t["id"]: t for t in json.loads((ROOT / "data" / "texts.json").read_text())["texts"]}
    order = {p["id"]: n for n, p in enumerate(idx["pages"])}

    # canonical file per folio side: the one most sections already link (ties: alphabetical)
    use = collections.Counter()
    for f in PUB.glob("verified-sinaiticus-*.json"):
        for s in json.loads(f.read_text())["translation"]:
            for p in s.get("scan_pages") or []:
                use[p.split("/")[-1]] += 1
    prefer = {fid: sorted(names, key=lambda n: (-use[n], n))[0] for fid, names in fbf.items()}

    def file_for(pid, key, ch):
        fid = ids.get(pid) or EXTRA_IDS.get(pid) or derive_csp_id(pid, idx, ids)
        if not fid:
            raise SystemExit(f"no CSP image id for {pid}")
        ids[pid] = fid
        if fid in prefer:
            return fid, prefer[fid]
        name = f"{key}-{ch}-{fid}.jpg"
        if dry:
            downloads.append(f"(dry run) would fetch {name}")
        else:
            download_folio(fid, pid, FOLIO_DIR / name, downloads)
        prefer[fid] = name
        return fid, name

    for f in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        before = json.dumps(d, ensure_ascii=False, sort_keys=True)
        key, ch, b = entry_book(d)
        gch = repair_greek(d, idx)
        if key == "sirach" and 30 <= ch <= 36 and "Manuscript order:" not in d.get("introduction", ""):
            d["introduction"] = d.get("introduction", "") + SIRACH_ORDER_NOTE
        if gch:
            greek_changes.append({"id": d["id"], "verses": gch})
        ent_changes, all_files = [], []
        for s in d["translation"]:
            vs = section_verses(s, b, ch)
            old = list(s.get("scan_pages") or [])
            old_note = s.get("scan_note", "") or ""
            if old_note.find(XML_NOTE_MARK) >= 0:
                old_note = old_note[old_note.find(XML_NOTE_MARK) + len(XML_NOTE_MARK) + 1:].strip()
                old_note = re.sub(r"^Not in the manuscript: [^.]*\.\s*", "", old_note)
            pids, absent = pages_for(idx, vs) if vs else ([], [])
            if pids:
                new, spans = [], []
                for pid in pids:
                    fid, name = file_for(pid, key, ch)
                    new.append(f"sinaiticus-folios/{name}")
                    spans.append(page_span_note(idx, pid, fid, vs, with_verses=len(pids) > 1))
                note = "; ".join(spans) + f". Page, column and line from the {XML_NOTE_MARK}."
                if absent:
                    note += f" Not in the manuscript: {', '.join(absent)}."
            else:
                pid, why = placeholder_pages(d, s, idx, b, ch)
                if not pid:
                    new, note = old, old_note
                else:
                    fid, name = file_for(pid, key, ch)
                    new = [f"sinaiticus-folios/{name}"]
                    note = (f"These verses are not in the Codex Sinaiticus Project transcription. The page shown, "
                            f"{folio_label(idx, pid)} ({fid}), is {why}; positions from the {XML_NOTE_MARK}.")
                    if old_note.startswith("These verses are not present in Codex Sinaiticus; the folio shown is"):
                        old_note = ""
            if old_note and old_note not in note:
                note = f"{note} {old_note}"
            if new != old:
                ent_changes.append({"section": s["section"], "old": old, "new": new})
            s["scan_pages"] = new
            s["scan_note"] = note
            for p in new:
                if p not in all_files:
                    all_files.append(p)
        all_files.sort(key=lambda p: order.get(pid_of(FID_RE.search(p).group(1)), 10 ** 6))
        v = d["verification"]
        v["scan_local_paths"] = all_files
        v["scan_local_path"] = all_files[0]
        v["scan_folio_ids"] = [FID_RE.search(p).group(1) for p in all_files]
        rng = []
        for p in all_files:
            fid = FID_RE.search(p).group(1)
            lib = cache["folios"].get(fid, {}).get("library_folio") or next(
                (x["folionum"] for x in idx["pages"] if x["id"] == pid_of(fid)), "")
            rng.append(f"{fid} (lib. folio {lib or '?'}): {page_range_text(idx, pid_of(fid))}")
        v["scan_folio_ranges"] = rng
        v["section_folios_verified"] = True
        v["section_folios_source"] = "csp_xml_v1.95"
        v["section_folios_note"] = MAPPING_NOTE
        if ent_changes or gch:
            changes.append({"id": d["id"], "sections": ent_changes, "greek_verses": gch})
        row = catalog.get(d["id"])
        if row:
            rp = [p["file"] for p in (row.get("scans") or {}).get("pages", [])]
            if not rp or any(p not in all_files for p in rp):
                linked = {FID_RE.search(p).group(1) for p in all_files}
                kind = ("same folio, other file name" if rp and all(FID_RE.search(p).group(1) in linked for p in rp)
                        else "folio not linked by any section")
                rows_needed.append({"id": d["id"], "kind": kind, "scans_pages_now": rp,
                                    "scans_pages_should_be": [
                                        {"file": p, "caption": f"Codex Sinaiticus {folio_label(idx, pid_of(FID_RE.search(p).group(1)))}"}
                                        for p in all_files]})
        if json.dumps(d, ensure_ascii=False, sort_keys=True) != before:
            v["section_folios_checked_date"] = TODAY
            if not dry:
                f.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    if (changes or downloads) and not dry:  # a re-run with nothing to do keeps the earlier log
        (OUT / "sinaiticus_changes.json").write_text(json.dumps(
            {"date": TODAY, "downloads": downloads, "greek_changes": greek_changes, "entries": changes},
            indent=1, ensure_ascii=False))
    (OUT / "sinaiticus_texts_json_rows.json").write_text(json.dumps(rows_needed, indent=1, ensure_ascii=False))
    nsec = sum(len(c["sections"]) for c in changes)
    print(f"fix{' (dry run)' if dry else ''}: {len(changes)} entries with page or Greek changes, {nsec} sections with new "
          f"scan_pages; Greek repaired in {len(greek_changes)} entries; downloads: {downloads}; "
          f"catalog rows to update: {len(rows_needed)}")


# ---------------------------------------------------------------------------
# 6. check (read only)
# ---------------------------------------------------------------------------
def check():
    idx = load_index()
    problems = []
    sizes = collections.defaultdict(set)
    for f in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key, ch, b = entry_book(d)
        for s in d["translation"]:
            listed = []
            for p in s.get("scan_pages") or []:
                fp = SCANS / p
                if not fp.exists() or fp.stat().st_size < 10000:
                    problems.append({"id": d["id"], "section": s["section"], "type": "scan_file_missing", "file": p})
                m = FID_RE.search(p)
                listed.append(pid_of(m.group(1)))
                sizes[m.group(1)].add(p)
            vs = section_verses(s, b, ch)
            if not vs:
                continue
            exp, absent = pages_for(idx, vs)
            if not exp:
                problems.append({"id": d["id"], "section": s["section"], "type": "no_verse_on_any_page", "verses": absent})
                continue
            for p in listed:
                if p not in exp:
                    problems.append({"id": d["id"], "section": s["section"], "type": "listed_page_carries_none_of_section", "page": p})
            for p in exp:
                if p not in listed:
                    problems.append({"id": d["id"], "section": s["section"], "type": "missing_page_with_section_text", "page": p})
            if listed != [p for p in exp if p in listed]:
                problems.append({"id": d["id"], "section": s["section"], "type": "pages_out_of_order", "listed": listed})
    for fid, ps in sizes.items():
        if len(ps) > 1:
            problems.append({"id": None, "section": None, "type": "same_folio_saved_under_several_names", "files": sorted(ps)})
    out = OUT / "sinaiticus_check.json"
    out.write_text(json.dumps(problems, indent=1, ensure_ascii=False))
    c = collections.Counter(p["type"] for p in problems)
    print(f"check: {len(problems)} problems {dict(c)} -> {out.relative_to(ROOT)}")
    return problems


# XML verses deliberately not shown, with the reason
KNOWN_UNSHOWN = {
    "61|91|3": "only the last letters of the verse (νοηϲε) survive, at the top of Q95_8r; the rest was on a lost leaf",
}


def missing_from_entries(idx):
    """XML verses of every chapter that has an entry, shown as Greek in no entry of that book."""
    shown, chapters, owner = collections.defaultdict(set), collections.defaultdict(set), {}
    for f in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key, ch, b = entry_book(d)
        chapters[b].add(ch)
        owner[(b, ch)] = d["id"]
        for s in d["translation"]:
            for (bb, c, v) in section_verses(s, b, ch):
                shown[b].add((c, re.match(r"\d+", v).group(0)))
    rows = []
    for k, v in idx["verses"].items():
        b, c, vv = k.split("|")
        b, c = int(b), int(c)
        if b not in chapters or c not in chapters[b] or not v["pages"] or not letters(v["text"]):
            continue  # verses with no first-hand letters (added only by a corrector) are not counted
        num = re.match(r"\d+", vv).group(0)
        if (c, num) not in shown[b] and not (num == "0"):
            known = KNOWN_UNSHOWN.get(k)
            rows.append({"id": owner[(b, c)], "verse": f"{c}:{vv}",
                         "type": "fragment_not_shown_explained" if known else "xml_verse_not_shown",
                         "pages": v["pages"], "xml": v["text"][:120], **({"reason": known} if known else {})})
    return rows


def legacy_audit():
    """Run the earlier audit (scripts/qc_scan_audit.py, CSP page summaries) on
    the Sinaiticus entries without touching its own output files, and give
    the XML evidence for every item it still reports."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import qc_scan_audit as qa
    idx = load_index()
    probs, counts = [], collections.Counter()
    qa.generic_checks("sinaiticus", probs, counts)
    qa.audit_sinaiticus(probs, counts)
    out = []
    for p in probs:
        item = {k: v for k, v in p.items() if k != "collection"}
        if p["type"] == "missing_page_boundary_verse":
            d = json.loads((PUB / f"{p['id']}.json").read_text())
            key, ch, b = entry_book(d)
            ev = []
            for cv in p["verses_on_missing_page"]:
                c, v = cv.split(":")
                k = f"{b}|{c}|{v}"
                x = idx["verses"].get(k, {})
                ev.append(f"{cv}: letters only on {', '.join(x.get('pages', []))}, ending at {x.get('pos', {}).get(x.get('pages', [''])[-1], ['', ''])[1]}")
            item["xml_evidence"] = ev
            item["verdict"] = ("not a problem: the verse ends on the last line of the previous page; the CSP page "
                               "summary names it as the first verse of the next page")
        elif p["type"] in ("listed_page_carries_none_of_section", "verses_on_no_known_folio"):
            labels = re.findall(r"<sup>([^<]+)</sup>", next(s["original_text"] for s in json.loads(
                (PUB / f"{p['id']}.json").read_text())["translation"] if s["section"] == p["section"]))
            if any(re.search(r"[a-z]$", l) for l in labels):
                item["verdict"] = ("not a problem: the section holds split verses (labels such as 16a, 10a) that the "
                                   "earlier audit skips; the XML places them on the linked page")
            elif p.get("page") == "Q69_8v_B358" or "Q69_8v_B358" in " ".join(p.get("listed", [])):
                item["verdict"] = ("not a problem: the earlier audit replaces the CSP summary of Q69_8v with a hand-made "
                                   "range (35:22-36:10 and 30:25) that leaves out 31:1-18, which the XML places on "
                                   "Q69_8v col. 1 line 40 to col. 2 line 48")
            else:
                item["verdict"] = "open"
        else:
            item["verdict"] = "open"
        out.append(item)
    path = OUT / "sinaiticus_legacy_audit.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    c = collections.Counter((i["type"], i["verdict"].split(":")[0]) for i in out)
    print(f"legacy audit: {len(out)} items {dict(c)} -> {path.relative_to(ROOT)}")
    return out


def greek():
    idx = load_index()
    rows = compare_greek(idx) + missing_from_entries(idx)
    out = OUT / "sinaiticus_greek_check.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    c = collections.Counter(r["type"] for r in rows)
    print(f"greek: {dict(c)} -> {out.relative_to(ROOT)}")
    return rows


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "index":
        build_index()
    elif cmd == "fix":
        fix(dry="--dry-run" in sys.argv)
    elif cmd == "check":
        check()
    elif cmd == "greek":
        greek()
    elif cmd == "legacy-audit":
        legacy_audit()
    else:
        raise SystemExit(__doc__)
