#!/usr/bin/env python3
"""
import_bhagavad_gita.py: the Bhagavad Gita, complete (18 chapters, 701 verses as numbered in the
manuscript and in Besant's edition), shown page by page on one dated Sanskrit manuscript.

Chain of evidence:
  1. SCAN     University of Pennsylvania, Kislak Center, Ms. Coll. 390 Item 559
              ("Athabhagavadgītāprārambhaḥ"), 90 paper leaves, 7 lines per leaf, Devanagari,
              final colophon dated Saṃvat 1851, Caitra śukla 3 (1794 CE) on fol. 90r.
              Images: OPenn (openn.library.upenn.edu/Data/0002/mscoll390_item559), Creative
              Commons Public Domain Mark. Each OPenn web JPEG shows an opening with the verso of
              leaf k above the recto of leaf k+1; this script cuts every opening into its two pages
              at the dark shadow line between the leaves (searched in rows 850-1000).
  2. MAPPING  Every page from fol. 1r to fol. 90v was read by eye on the images. The readings
              (verse numbers and the line on which each verse ends, chapter colophons, speaker
              headings) are recorded in data/sources/bhagavad-gita/mapping_log.json and copied
              into each section's scan_note. A section is the run of verses whose text ends on one
              page; when its first verse began on the previous page, both pages are listed.
              Foliation: the scribe wrote the folio number 41 twice; the cataloguer's labels
              ("41r =42r" etc.) are quoted in the notes, and file names use the physical leaf count.
  3. TEXT     Sanskrit (Devanagari) and English, verse by verse, from Annie Besant, The
              Bhagavad-Gita, 4th edition (Madras: G. A. Natesan, 1922), as transcribed and
              validated on English Wikisource ("Bhagavad-Gita (Besant 4th)", Discourse 1-18,
              revision ids saved in data/sources/bhagavad-gita/besant/revids.json). The book is in
              the public domain (published 1922; Besant died 1933); the Wikisource transcription is
              CC BY-SA 4.0. Besant prints each verse in Sanskrit with its English and a verse number,
              so the two languages align exactly. Footnote markers are dropped.
              K. T. Telang's SBE 8 (1882) prose was evaluated first but carries no verse division,
              so it cannot be split per page without guessing; GRETIL's
              sa_bhagavadgItA-4comm.xml was evaluated for the Sanskrit and set aside (irregular
              markup that interleaves commentary, and 46 verses in chapter 1).

Usage:
    python3 scripts/import_bhagavad_gita.py            # build (uses cached downloads)
    python3 scripts/import_bhagavad_gita.py --download # re-fetch OPenn images and Wikisource pages
"""

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = "bhagavad-gita"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
OPENN_DIR = SRC / "openn"
BESANT_DIR = SRC / "besant"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL_FILE = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibraryResearch/1.0 (non-commercial reference library)"

OPENN_BASE = "https://openn.library.upenn.edu/Data/0002/mscoll390_item559"
OPENN_HTML = "https://openn.library.upenn.edu/Data/0002/html/mscoll390_item559.html"
WS_BASE = "https://en.wikisource.org/wiki/Bhagavad-Gita_(Besant_4th)"
WS_INDEX = "https://en.wikisource.org/wiki/Index:Bhagavad_Gita_-_Annie_Besant_4th_edition.djvu"
SHELFMARK = "University of Pennsylvania, Kislak Center, Ms. Coll. 390 Item 559"
SHORT_MS = "Penn Ms. Coll. 390 Item 559"

VERSE_COUNT = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78]
DEV = str.maketrans("०१२३४५६७८९", "0123456789")
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
       "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth"]


def fetch(url, tries=6):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:  # rate limits on Wikisource
            if k == tries - 1:
                raise
            print("  retry", url, e)
            time.sleep(15)


def download():
    OPENN_DIR.mkdir(parents=True, exist_ok=True)
    BESANT_DIR.mkdir(parents=True, exist_ok=True)
    (OPENN_DIR / "mscoll390_item559_TEI.xml").write_bytes(fetch(f"{OPENN_BASE}/data/mscoll390_item559_TEI.xml"))
    for k in range(91):
        f = OPENN_DIR / f"6555_{k:04d}_web.jpg"
        if not f.exists():
            f.write_bytes(fetch(f"{OPENN_BASE}/data/web/{f.name}"))
    revs = {}
    for n in range(1, 19):
        u = "https://en.wikisource.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "parse", "page": f"Bhagavad-Gita (Besant 4th)/Discourse {n}", "prop": "text|revid", "format": "json"})
        p = json.loads(fetch(u))["parse"]
        (BESANT_DIR / f"d{n:02d}.html").write_text(p["text"]["*"], encoding="utf-8")
        revs[n] = p.get("revid")
        time.sleep(2)
    (BESANT_DIR / "revids.json").write_text(json.dumps(revs), encoding="utf-8")


# --------------------------------------------------------------------------------------------
# Besant 1922: Sanskrit + English per verse, plus the chapter colophon
# --------------------------------------------------------------------------------------------
VOID = ("br", "link", "img", "meta", "hr", "wbr", "input", "col", "source")


class BesantParser(HTMLParser):
    """Token stream: ('sa', text) for each Devanagari block, ('en', text) for English, ('V', label) for verse numbers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.toks, self.buf, self.sabuf, self.frbuf = [], [], [], [], []
        self.skip = self.sa = self.fr = 0

    def flush(self):
        t = "".join(self.buf)
        if t.strip():
            self.toks.append(("en", t))
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if tag in VOID:
            if tag == "br" and not self.skip:
                (self.sabuf if self.sa else self.buf).append("\n")
            return
        skip = (tag in ("style", "script") or "reference" in cls.split() or "pagenum" in cls
                or "mw-references" in cls or "wst-header" in cls or "references" in cls.split())
        sa = a.get("lang") == "sa"
        fr = "wst-floatright" in cls
        self.stack.append((tag, skip, sa, fr))
        if skip:
            self.skip += 1
        if sa and not self.skip:
            self.flush()
            self.sa += 1
        if fr and not self.skip:
            self.flush()
            self.fr += 1
        if tag in ("p", "div") and not self.skip:
            (self.sabuf if self.sa else self.buf).append("\n")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, skip, sa, fr = self.stack.pop()
            if skip:
                self.skip -= 1
            if sa and not self.skip:
                self.sa -= 1
                if self.sa == 0:
                    self.toks.append(("sa", "".join(self.sabuf)))
                    self.sabuf = []
            if fr and not self.skip:
                self.fr -= 1
                self.toks.append(("V", "".join(self.frbuf)))
                self.frbuf = []
            if t == tag:
                break

    def handle_data(self, d):
        if self.skip:
            return
        if self.fr:
            self.frbuf.append(d)
        elif self.sa:
            self.sabuf.append(d)
        else:
            self.buf.append(d)


HEAD = re.compile(r"^(Layout 2|Aum\.?|THE BHAGAVAD-GITA|THE LORD'S SONG\.?|[A-Z\-]+ DISCOURSE\.?|ॐ)$")


def lines(t):
    return [re.sub(r"\s+", " ", x).strip() for x in t.split("\n") if x.strip()]


def besant_chapter(n):
    p = BesantParser()
    p.feed((BESANT_DIR / f"d{n:02d}.html").read_text(encoding="utf-8"))
    p.flush()
    verses, sa, en = [], [], []
    for kind, t in p.toks:
        if kind == "sa":
            sa.append(t)
        elif kind == "en":
            en.append(t)
        else:
            verses.append({"label": re.sub(r"[^0-9]", "", t), "sa": sa, "en": en})
            sa, en = [], []
    out = []
    for i, v in enumerate(verses, start=1):
        sa_lines = [l for blk in v["sa"] for l in lines(blk) if not HEAD.match(l)]
        en_lines = [l for blk in v["en"] for l in lines(blk) if not HEAD.match(l)]
        m = re.search(r"॥\s*([०-९]+)\s*॥\s*$", sa_lines[-1])
        assert m and int(m.group(1).translate(DEV)) == i, (n, i, sa_lines[-1])
        assert en_lines, (n, i)
        out.append({"n": i, "label": v["label"], "sa": sa_lines, "en": en_lines})
    assert len(out) == VERSE_COUNT[n - 1], (n, len(out))
    # colophon: first Devanagari block after the last verse + English up to the chapter title
    col_sa = lines(sa[0])
    assert col_sa[0].startswith("इति श्रीमद्भगवद्गीता"), col_sa
    en_tail = " ".join(l for blk in en for l in lines(blk))
    m = re.search(r"(Thus in the glorious Upanishads.*?entitled:?\s*[A-Z][A-Z\-' ,]+\.)", en_tail)
    assert m, (n, en_tail[:200])
    col_en = m.group(1)
    return out, col_sa, col_en


def label_anomalies():
    """Verse-number labels in the Wikisource transcription that differ from the running count."""
    notes = []
    for n in range(1, 19):
        vs, _, _ = besant_chapter(n)
        for v in vs:
            if v["label"] != str(v["n"]):
                notes.append(f"{n}.{v['n']} (printed or transcribed as '({v['label']})')" if v["label"] else f"{n}.{v['n']} (number missing in the transcription)")
    return notes


# --------------------------------------------------------------------------------------------
# Page images
# --------------------------------------------------------------------------------------------
def page_file(pid):
    return f"upenn559-f{pid}.jpg"


def make_scans(pids):
    import numpy as np
    from PIL import Image
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    log = {p["page"]: p for p in json.loads((SRC / "mapping_log.json").read_text(encoding="utf-8"))["pages"]}
    splits = {}
    for pid in pids:
        out = SCAN_DIR / page_file(pid)
        rec = log[pid]
        im = Image.open(OPENN_DIR / rec["openn_image"]).convert("RGB")
        if rec["half"] == "single":
            crop = im
        else:
            k = rec["openn_image"]
            if k not in splits:
                a = np.asarray(im.convert("L")).astype(int)
                h, w = a.shape
                dark = (a[:, int(w * 0.06):int(w * 0.94)] < 105).mean(axis=1)
                splits[k] = 850 + int(np.argmax(dark[850:1000]))
            y = splits[k]
            crop = im.crop((0, 0, im.size[0], y)) if rec["half"] == "top" else im.crop((0, y, im.size[0], im.size[1]))
        crop.save(out, quality=85)
    return splits


# --------------------------------------------------------------------------------------------
# Mapping
# --------------------------------------------------------------------------------------------
def parse_tokens(tok):
    """'1.3-1.6' -> ('v', 1, [3..6]); '2.1' -> ('v', 2, [1]); 'C4' -> ('c', 4, None); 'C5a' -> ('c', 5, 'a');
    '10.1a' -> ('begin', 10, [1])."""
    m = re.fullmatch(r"C(\d+)([ab]?)", tok)
    if m:
        return ("c", int(m.group(1)), m.group(2) or None)
    m = re.fullmatch(r"(\d+)\.(\d+)a", tok)
    if m:
        return ("begin", int(m.group(1)), [int(m.group(2))])
    m = re.fullmatch(r"(\d+)\.(\d+)(?:-(\d+)\.(\d+))?", tok)
    assert m, tok
    c, a = int(m.group(1)), int(m.group(2))
    b = int(m.group(4)) if m.group(4) else a
    if m.group(3):
        assert int(m.group(3)) == c, tok
    return ("v", c, list(range(a, b + 1)))


def build_mapping():
    log = json.loads((SRC / "mapping_log.json").read_text(encoding="utf-8"))["pages"]
    order = [p["page"] for p in log]
    by = {p["page"]: p for p in log}
    chapters = {c: [] for c in range(1, 19)}   # list of dicts: kind, verses/None, pages, page
    colophon_pages = {c: [] for c in range(1, 19)}
    for i, p in enumerate(log):
        if not p["ends"]:
            continue
        toks = [parse_tokens(t) for t in p["ends"]]
        for j, (kind, c, val) in enumerate(toks):
            if kind == "begin":
                continue
            if kind == "c":
                colophon_pages[c].append(p["page"])
                continue
            pages = [p["page"]]
            if j == 0 and p["starts"] == "mid":
                pages = [order[i - 1], p["page"]]
            chapters[c].append({"page": p["page"], "verses": val, "pages": pages})
    # coverage check
    for c in range(1, 19):
        seen = [v for s in chapters[c] for v in s["verses"]]
        assert seen == list(range(1, VERSE_COUNT[c - 1] + 1)), (c, seen)
        assert colophon_pages[c], c
    return chapters, colophon_pages, by


def folio_label(rec):
    """Physical page id '042r' -> 'fol. 42r' plus the catalogue label when it differs."""
    pid = rec["page"]
    phys = f"{int(pid[:-1])}{pid[-1]}"
    lab = rec["tei_label"]
    if lab.replace(" ", "") != phys:
        return f"fol. {phys} (catalogue label {lab}; the scribe repeated folio number 41)"
    return f"fol. {phys}"


def short_fol(pid):
    return f"{int(pid[:-1])}{pid[-1]}"


# Chapter names as the manuscript's own colophons give them (read on the images; see mapping_log.json)
MS_CHAPTER_NAMES = {
    1: "arjunaviṣāda", 2: "sāṃkhyayoga", 3: "karmayoga", 4: "karmasaṃnyāsayoga", 5: "saṃnyāsayoga",
    6: "ātmasaṃyamayoga", 7: "jñānavijñānayoga", 8: "mahāpuruṣayoga", 9: "rājavidyārājaguhyayoga",
    10: "vibhūtiyoga", 11: "viśvarūpadarśana", 12: "bhaktiyoga", 13: "kṣetrakṣetrajñavibhāgayoga",
    14: "guṇatrayavibhāgayoga", 15: "puruṣottamayoga", 16: "daivāsurasaṃpadvibhāgayoga",
    17: "guṇavibhāgadarśana", 18: "mokṣasaṃnyāsayoga",
}


def title_case(s):
    small = {"of", "the", "and", "by", "from", "between", "to", "a", "in"}
    words = s.lower().split()
    return " ".join(w if (i and w in small) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def verse_html_sa(v):
    return f"<p><sup>{v['n']}</sup>" + "<br>".join(esc(l) for l in v["sa"]) + "</p>"


def verse_html_en(v):
    return f"<p><sup>{v['n']}</sup>" + "<br>".join(esc(l) for l in v["en"]) + "</p>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    args = ap.parse_args()
    if args.download:
        download()

    chapters, colophon_pages, log = build_mapping()
    used_pages = sorted({pg for c in chapters.values() for s in c for pg in s["pages"]}
                        | {pg for v in colophon_pages.values() for pg in v},
                        key=lambda p: (int(p[:-1]), p[-1] == "v"))
    splits = make_scans(used_pages)
    print(f"  {len(used_pages)} page images written to {SCAN_DIR.relative_to(ROOT)}")

    revids = json.loads((BESANT_DIR / "revids.json").read_text(encoding="utf-8"))
    anomalies = label_anomalies()
    rows = []
    for c in range(1, 19):
        verses, col_sa, col_en = besant_chapter(c)
        vmap = {v["n"]: v for v in verses}
        name_en = re.search(r"entitled:?\s*(.+?)\.$", col_en).group(1)
        name_en = title_case(name_en).replace("Indesctructible", "Indestructible")
        tid = f"{PREFIX}{c:02d}"
        sections = []
        for s in chapters[c]:
            vs = s["verses"]
            rec = log[s["page"]]
            rng = f"{vs[0]}" if len(vs) == 1 else f"{vs[0]}-{vs[-1]}"
            note = f"{folio_label(rec)}, OPenn image {rec['openn_image'][:9]} ({'upper' if rec['half'] == 'top' else 'lower' if rec['half'] == 'bottom' else 'single'} leaf). Checked on the image: {rec['reading']}."
            if len(s["pages"]) == 2:
                note += f" Verse {c}.{vs[0]} begins on the previous page, fol. {short_fol(s['pages'][0])}, so both pages are shown."
            sections.append({
                "section": rng,
                "original_ref": f"Bhagavad Gita {c}.{rng}; {SHORT_MS}, " + " and ".join(f"fol. {short_fol(p)}" for p in s["pages"]),
                "original_text": "".join(verse_html_sa(vmap[v]) for v in vs),
                "text": "".join(verse_html_en(vmap[v]) for v in vs),
                "scan_pages": [f"{KEY}/{page_file(p)}" for p in s["pages"]],
                "scan_note": note,
            })
        cp = colophon_pages[c]
        crec = [log[p] for p in cp]
        sections.append({
            "section": "colophon",
            "original_ref": f"Colophon of chapter {c}; {SHORT_MS}, " + " and ".join(f"fol. {short_fol(p)}" for p in cp),
            "original_text": "<p>" + "<br>".join(esc(l) for l in col_sa) + "</p>",
            "text": "<p>" + esc(col_en) + "</p>",
            "scan_pages": [f"{KEY}/{page_file(p)}" for p in cp],
            "scan_note": " ".join(f"{folio_label(r)}: {r['reading']}." for r in crec)
                         + f" The manuscript names the chapter {MS_CHAPTER_NAMES[c]}; the Sanskrit and English shown are the colophon printed in Besant's edition, whose wording differs in places from the manuscript's.",
        })
        first_fol = short_fol(chapters[c][0]["pages"][0])
        last_fol = short_fol(cp[-1])
        n = VERSE_COUNT[c - 1]
        intro = (
            f"<p>The <em>Bhagavad Gita</em> (\"Song of the Lord\") is a dialogue of 700 verses between the prince Arjuna and Krishna, "
            f"set on the battlefield of Kurukshetra in book 6 (Bhishmaparvan) of the Mahabharata. Its date of composition is debated; "
            f"many scholars place it in the last centuries BCE. This is chapter {c}, <strong>{name_en}</strong> "
            f"({n} verses as numbered in the manuscript and in Besant's edition).</p>\n\n"
            f"<p>The pages shown are from a complete Sanskrit manuscript of the Gita at the University of Pennsylvania ({SHORT_MS}), "
            f"90 paper leaves of 7 lines in Devanagari, with speaker headings, colophons and verse-end marks in red. "
            f"Its final colophon (fol. 90r) dates the copy to Saṃvat 1851, the third day of the bright half of Caitra (1794 CE). "
            f"Chapter {c} runs from fol. {first_fol} to the chapter colophon on fol. {last_fol}.</p>\n\n"
            f"<p>Each section below is one manuscript page: the verses whose text ends on that page, located by reading the scribe's "
            f"verse numbers and the first and last words on the image. When a verse begins at the foot of one page and ends on the next, "
            f"both pages are shown. The Sanskrit and English are from Annie Besant's edition and translation (4th edition, 1922), "
            f"which prints each verse in Devanagari with its English; the manuscript's spelling differs from the printed text in small details.</p>"
        )
        notes = [
            "Sanskrit and English: Annie Besant, The Bhagavad-Gita, 4th edition (Madras: G. A. Natesan, 1922), transcription validated on English Wikisource. Besant's footnotes are not reproduced.",
            "Verse numbers follow Besant and the manuscript, which agree throughout: chapter 13 counts Arjuna's opening question ('prakṛtiṃ puruṣaṃ caiva...') as verse 1, so it has 35 verses and the whole text 701.",
            "K. T. Telang's translation (Sacred Books of the East 8, 1882) was the first choice for the English, but it is continuous prose without verse divisions, so it cannot be matched to manuscript pages verse by verse; Besant's verse-numbered translation is used instead.",
            "The last section of each chapter is the chapter colophon. Besant prints most Sanskrit colophons in shortened form (marked with ॰) while her English gives the full formula; the manuscript writes the colophon out in full, and its chapter names differ in places from Besant's (see the scan note).",
        ]
        if c == 1:
            notes.append("Before chapter 1 the manuscript has a ritual preface (Gītā-nyāsa) and nine meditation verses (dhyāna), fol. 1v-4r; they are not part of the 700-verse text and are not reproduced here.")
            notes.append("In chapter 1 the scribe wrote no number after verse 28 (fol. 7r line 7); the verse is placed by its words ('kṛpayā parayāviṣṭo ... samupasthitam').")
        ch_anom = [a for a in anomalies if a.startswith(f"{c}.")]
        if ch_anom:
            notes.append("In the Wikisource transcription of Besant's edition, the verse-number label is irregular at " + "; ".join(ch_anom)
                         + ". The verses are counted in sequence and checked against the Sanskrit numbers, which are regular.")
        if c == 8:
            notes.append("Besant's English colophon for this chapter reads 'INDESCTRUCTIBLE', reproduced as transcribed.")
        entry = {
            "id": tid, "slug": tid,
            "title": f"Bhagavad Gita, Chapter {c}: {name_en}",
            "language": "Sanskrit / English",
            "source": f"{SHORT_MS} (dated 1794) via OPenn + Sanskrit and English of Annie Besant, The Bhagavad-Gita (4th ed. 1922), Wikisource",
            "description": f"Bhagavad Gita chapter {c} ({name_en}), shown page by page on a Sanskrit manuscript copied in 1794 "
                           f"({SHORT_MS}), with the Sanskrit text and Annie Besant's English.",
            "introduction": intro,
            "translator_notes": notes,
            "translation": sections,
            "verification": {
                "scan_source": f"University of Pennsylvania Libraries, OPenn: {OPENN_HTML} (web JPEGs {OPENN_BASE}/data/web/); each opening cut into its two pages",
                "scan_license": "Creative Commons Public Domain Mark 1.0 ('free of known copyright restrictions and in the public domain', OPenn TEI licence statement)",
                "scan_manuscript": f"{SHELFMARK}, Bhagavadgītā, 90 paper leaves, 7 lines per leaf, Devanagari; colophon fol. 90r dated Saṃvat 1851, Caitra śukla 3 (1794 CE)",
                "scan_mapping": "Every page read by eye on the OPenn images: scribe's verse numbers with their line, first and last words, speaker headings and chapter colophons; "
                                "readings recorded in data/sources/bhagavad-gita/mapping_log.json and in each section's scan_note",
                "scan_mapping_urls": [OPENN_HTML, f"{OPENN_BASE}/data/mscoll390_item559_TEI.xml"],
                "scan_local_paths": sorted({p for s in sections for p in s["scan_pages"]}),
                "original_text_source": f"Annie Besant, The Bhagavad-Gita, 4th ed. (Madras: G. A. Natesan, 1922), Sanskrit text, English Wikisource {WS_BASE}/Discourse_{c} (revision {revids.get(str(c))}); scan index {WS_INDEX}",
                "original_text_license": "edition public domain (1922); Wikisource transcription CC BY-SA 4.0",
                "translation_source": f"Annie Besant, The Bhagavad-Gita, 4th ed. (Madras: G. A. Natesan, 1922), English Wikisource {WS_BASE}/Discourse_{c}",
                "translation_license": "public domain (published 1922; Besant died 1933); Wikisource transcription CC BY-SA 4.0",
                "translator": "Annie Besant (1922)",
                "verified_date": TODAY,
            },
        }
        PUB_DIR.mkdir(parents=True, exist_ok=True)
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": c,
            "title": entry["title"], "author_id": "vyasa", "language": "Sanskrit",
            "era": "Classical", "tradition": "hindu", "category": "sacred-text",
            "date_approx": "c. 2nd c. BCE (composition, date debated); manuscript dated Saṃvat 1851 (1794 CE)",
            "century": -2,
            "source": entry["source"], "description": entry["description"],
            "themes": ["bhagavad-gita", "gita", "krishna", "arjuna", "mahabharata", "sanskrit", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": f"{SHORT_MS}, fol. {short_fol(Path(p).stem.split('-f')[1])}"}
                                for p in entry["verification"]["scan_local_paths"]]},
        })
        print(f"  wrote {tid}: {len(sections)} sections")

    coll = {
        "collection": {
            "key": KEY,
            "prefix": PREFIX,
            "label": "Bhagavad Gita (Penn manuscript of 1794)",
            "group": "India",
            "date_sort": -200,
            "author_name": "Bhagavad Gita (Mahabharata book 6; manuscript dated 1794)",
            "source_url": OPENN_HTML,
            "critical_edition": "Annie Besant, The Bhagavad-Gita, 4th ed. (1922), Sanskrit text, via Wikisource",
            "translator_name": "Annie Besant (1922)",
            "original_lang_label": "Sanskrit · Devanagari (Besant 1922)",
            "original_lang_code": "sa",
            "edition_label": "",
            "search_terms": "bhagavad gita bhagavadgita krishna arjuna mahabharata kurukshetra yoga sanskrit manuscript",
            "description": "The complete Bhagavad Gita, chapter by chapter and page by page, on a Sanskrit manuscript copied in 1794 "
                           "(University of Pennsylvania Ms. Coll. 390 Item 559), with the Sanskrit text and Annie Besant's verse-by-verse English.",
        },
        "texts": rows,
    }
    COLL_FILE.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL_FILE.relative_to(ROOT)} ({len(rows)} entries); splits used: {len(splits)} openings")


if __name__ == "__main__":
    main()
