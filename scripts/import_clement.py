#!/usr/bin/env python3
"""
import_clement.py -- 1 Clement and 2 Clement on the pages of Codex Alexandrinus
(London, British Library, Royal MS 1 D. VIII, 5th c.), with the passages lost
from Alexandrinus shown on Codex Hierosolymitanus 54 (Jerusalem, 1056).

Chain of evidence
-----------------
1. SCAN (A)   The Codex Alexandrinus (Royal MS. 1 D. V-VIII) in reduced
              photographic facsimile: New Testament and Clementine Epistles
              (British Museum, 1909, ed. F. G. Kenyon), Internet Archive item
              codexalexandrinu01unse (digitised by the Getty Research
              Institute; public domain). The Clementine Epistles are on scan
              leaves 281-302, after Revelation (leaf 280).
2. MAPPING (A) The caption the facsimile prints under every plate
              ("1 Clem. i. 1-iii. 4" ...). All 22 captions were read on the
              scans (2026-11-12) and are listed in A_PAGES. Folio numbers follow
              the NTVMR page list for GA 02 (docID 20002: fol. 158v ends
              Revelation; pages 1410-1511 follow as fol. 159r-169v) and agree
              with the numbers written on the plates (159, 161, 162, 163, 165,
              168 read on leaves 281, 285, 287, 289, 293, 299). Spot checks on
              the images: 159r opens with the salutation ("...τοῦ θεοῦ ἡ
              παροικοῦσα"), 167v ends at 57.6 in a damaged second column, 168r opens with 64.1 ("[λοι]πὸν ὁ παντεπόπτης θεός"),
              168v opens with 2 Clem 2.3 ("ἔρημος δοκεῖ εἶναι").
3. SCAN (H)   For 1 Clem 57.7-63.4 and 2 Clem 12.5b-20.5 (lost from A):
              Library of Congress microfilm of Jerusalem, Greek Patriarchate,
              Panagios Taphos 54 (Microfilm 5017; https://www.loc.gov/item/00279389694-jo/ ;
              "These collections are in the public domain"). Frame n shows
              fol. (n-3)v and fol. (n-2)r; folio numbers 68-76 read on the rectos.
4. MAPPING (H) Read on the images: the opening words of each page were
              located in the Greek text (H_PAGES).
5. GREEK      Kirsopp Lake, The Apostolic Fathers I (Loeb, 1912), First1KGreek
              tlg1271.tlg001 / tlg002 .1st1K-grc1 (CC BY-SA 4.0). Footnotes and
              scripture references left out; tokens the digital text corrupted
              (non-Greek characters) corrected from the printed page; elision
              encodings normalised to an apostrophe.
6. ENGLISH    J. B. Lightfoot, The Apostolic Fathers (1891), transcription at
              earlychristianwritings.com (public domain); Lightfoot's italics kept.

Usage:
    python3 scripts/import_clement.py [--force]
Cache: $THEOSIS_CACHE/theosis-clement or ~/.cache/theosis-clement
"""

import argparse
import html
import io
import json
import os
import re
import time
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "clement"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
CACHE = Path(os.environ.get("THEOSIS_CACHE", Path.home() / ".cache")) / f"theosis-{KEY}"
TODAY = date.today().isoformat()
UA = "Mozilla/5.0 (TheosisLibrary research; non-commercial)"
TEI = "{http://www.tei-c.org/ns/1.0}"

IA_ITEM = "codexalexandrinu01unse"
IA_URL = f"https://archive.org/details/{IA_ITEM}"
IA_LEAF = "https://archive.org/download/{i}/{i}_jp2.zip/{i}_jp2%2F{i}_{leaf:04d}.jp2&ext=jpg"
NTVMR_URL = "https://ntvmr.uni-muenster.de/manuscript-workspace?docID=20002"
LOC_ITEM = "https://www.loc.gov/item/00279389694-jo/"
LOC_IIIF = "https://tile.loc.gov/image-services/iiif/service:amed:amedmonastery:00279389694-jo:{frame:04d}/full/pct:100/0/default.jpg"
GREEK_URL = "https://github.com/OpenGreekAndLatin/First1KGreek/tree/master/data/tlg1271"
ENGLISH_URLS = {1: "http://www.earlychristianwritings.com/text/1clement-lightfoot.html",
                2: "http://www.earlychristianwritings.com/text/2clement-lightfoot.html"}
LAKE_PRINT = "https://archive.org/details/theapostolicfath00unknuoft"

# Alexandrinus: facsimile leaf -> (folio, caption as printed, spans [(work, c1, v1, c2, v2)])
A_PAGES = {
    281: ("159r", "1 Clem. i. 1-iii. 4", [(1, 0, 1, 3, 4)]),   # chapter 0 = salutation
    282: ("159v", "1 Clem. iii. 4-vii. 2", [(1, 3, 4, 7, 2)]),
    283: ("160r", "1 Clem. vii. 2-x. 4", [(1, 7, 2, 10, 4)]),
    284: ("160v", "1 Clem. x. 4-xiii. 2", [(1, 10, 4, 13, 2)]),
    285: ("161r", "1 Clem. xiii. 2-xvi. 8", [(1, 13, 2, 16, 8)]),
    286: ("161v", "1 Clem. xvi. 8-xviii. 11", [(1, 16, 8, 18, 11)]),
    287: ("162r", "1 Clem. xviii. 11-xxi. 2", [(1, 18, 11, 21, 2)]),
    288: ("162v", "1 Clem. xxi. 2-xxiv. 3", [(1, 21, 2, 24, 3)]),
    289: ("163r", "1 Clem. xxiv. 4-xxix. 1", [(1, 24, 4, 29, 1)]),
    290: ("163v", "1 Clem. xxix. 1-xxxiii. 3", [(1, 29, 1, 33, 3)]),
    291: ("164r", "1 Clem. xxxiii. 3-xxxv. 6", [(1, 33, 3, 35, 6)]),
    292: ("164v", "1 Clem. xxxv. 6-xxxviii. 2", [(1, 35, 6, 38, 2)]),
    293: ("165r", "1 Clem. xxxviii. 2-xlii. 2", [(1, 38, 2, 42, 2)]),
    294: ("165v", "1 Clem. xlii. 2-xlv. 1", [(1, 42, 2, 45, 1)]),
    295: ("166r", "1 Clem. xlv. 2-xlviii. 1", [(1, 45, 2, 48, 1)]),
    296: ("166v", "1 Clem. xlviii. 1-li. 4", [(1, 48, 1, 51, 4)]),
    297: ("167r", "1 Clem. li. 4-lv. 6", [(1, 51, 4, 55, 6)]),
    298: ("167v", "1 Clem. lv. 6-lvii. 6", [(1, 55, 6, 57, 6)]),
    299: ("168r", "1 Clem. lxiv. 1-2 Clem. ii. 2", [(1, 64, 1, 65, 2), (2, 1, 1, 2, 2)]),
    300: ("168v", "2 Clem. ii. 3-vi. 1", [(2, 2, 3, 6, 1)]),
    301: ("169r", "2 Clem. vi. 1-ix. 4", [(2, 6, 1, 9, 4)]),
    302: ("169v", "2 Clem. ix. 4-xii. 5", [(2, 9, 4, 12, 5)]),
}
# Hierosolymitanus 54 pages used for the gaps in A: folio -> (frame, side, opening words read on the image, where they stand)
H_PAGES = {
    "68r": (70, "R", "[ζητήσου]σί με κακοὶ καὶ οὐχ εὑρήσουσιν· ἐμίσησαν γὰρ σοφίαν", "1 Clem 57.5"),
    "68v": (71, "L", "ἀπὸ ἀγνωσίας εἰς ἐπίγνωσιν δόξης ὀνόματος αὐτοῦ", "1 Clem 59.2"),
    "69r": (71, "R", "ἀλλὰ καθάρισον ἡμᾶς τὸν καθαρισμὸν τῆς σῆς ἀληθείας", "1 Clem 60.2"),
    "69v": (72, "L", "[θέλουσιν] εὐσεβῶς καὶ δικαίως διευθύνειν, ἱκανῶς ἐπεστείλαμεν ὑμῖν, ἄνδρες ἀδελφοί", "1 Clem 62.1"),
    "73v": (76, "L", "καὶ τὸ ἄρσεν μετὰ τῆς θηλείας, οὔτε ἄρσεν οὔτε θῆλυ. τὰ δύο δὲ ἕν", "2 Clem 12.2-3"),
    "74r": (76, "R", "[ἴ]δωσιν ὅτι οὐ μόνον τοὺς μισοῦντας οὐκ ἀγαπῶμεν", "2 Clem 13.4; the scribe's marginal ιδ' marks 14.1"),
    "74v": (77, "L", "πλανωμένην ψυχὴν καὶ ἀπολλυμένην ἀποστρέψαι εἰς τὸ σωθῆναι", "2 Clem 15.1"),
    "75r": (77, "R", "συλλάβωμεν ἑαυτοῖς ... περὶ τὸ ἀγαθόν, ὅπως σωθῶμεν ἅπαντες", "2 Clem 17.2"),
    "75v": (78, "L", "φοβούμενος τὴν κρίσιν τὴν μέλλουσαν. ὥστε, ἀδελφοὶ καὶ ἀδελφαί", "2 Clem 18.2-19.1"),
    "76r": (78, "R", "οὐ τὸ εὐσεβὲς ἀλλὰ τὸ κερδαλέον διώκοντες", "2 Clem 20.4"),
}
H_NEXT = {"69v": ("70r", "ἐπικεκλημένῃ τὸ μεγαλοπρεπὲς καὶ ἅγιον ὄνομα αὐτοῦ", "1 Clem 64.1")}
# chapters lost in A, with the H pages that carry them (derived from the page openings above)
H_CHAPTERS = {
    (1, 57): ["68r"], (1, 58): ["68r"], (1, 59): ["68r", "68v"], (1, 60): ["68v", "69r"],
    (1, 61): ["69r"], (1, 62): ["69r", "69v"], (1, 63): ["69v"],
    (2, 12): ["73v"], (2, 13): ["73v", "74r"], (2, 14): ["74r"], (2, 15): ["74r", "74v"], (2, 16): ["74v"],
    (2, 17): ["74v", "75r"], (2, 18): ["75r", "75v"], (2, 19): ["75v"], (2, 20): ["75v", "76r"],
}
# (work, section, wrong, right): corrupted tokens of the digital text, checked on Lake's printed page
GREEK_FIXES = [
    (1, "4.11", "ʼΛαρὼν", "Ἀαρὼν"),
    (1, "32.4", "ʽ??ʼ", "ὁ"),
]
WORKS = {
    1: {"slug": "1-clement", "tei": "tlg1271.tlg001.1st1K-grc1.xml", "html": "1clement-lightfoot.html", "label": "1Clem",
        "chapters": 65},
    2: {"slug": "2-clement", "tei": "tlg1271.tlg002.1st1K-grc1.xml", "html": "2clement-lightfoot.html", "label": "2Clem",
        "chapters": 20},
}


def fetch(url, timeout=180, tries=5):
    last = None
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (a + 1))
    raise RuntimeError(f"GET failed: {url}: {last}")


def cached_image(name, url):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if not (p.exists() and p.stat().st_size > 50_000):
        data = fetch(url)
        Image.open(io.BytesIO(data)).verify()
        p.write_bytes(data)
    return Image.open(p).convert("RGB")


def split_page(im, side):
    import numpy as np
    a = np.asarray(im.convert("L"), dtype=np.float32)
    h, w = a.shape
    cm = a[int(h * .2):int(h * .8)].mean(axis=0)
    lo, hi = int(w * .4), int(w * .6)
    g = lo + int(np.argmin(cm[lo:hi]))
    page = im.crop((0, 0, g, h)) if side == "L" else im.crop((g, 0, w, h))
    b = np.asarray(page.convert("L"), dtype=np.float32) > 140
    xs = np.where(b.mean(axis=0) > 0.5)[0]
    ys = np.where(b.mean(axis=1) > 0.5)[0]
    m = 40
    return page.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(page.width, xs.max() + m), min(page.height, ys.max() + m)))


def save(img, dest):
    if max(img.size) > 2400:
        img.thumbnail((2400, 2400))
    img.save(dest, "JPEG", quality=85, optimize=True)


def a_scan(leaf, force=False):
    folio = A_PAGES[leaf][0]
    dest = SCAN_DIR / f"alex-f{folio}.jpg"
    if force or not (dest.exists() and dest.stat().st_size > 10_000):
        save(cached_image(f"alex_leaf_{leaf:04d}.jpg", IA_LEAF.format(i=IA_ITEM, leaf=leaf)), dest)
    return f"{KEY}/{dest.name}"


def h_scan(folio, force=False):
    frame, side = H_PAGES[folio][0], H_PAGES[folio][1]
    dest = SCAN_DIR / f"h54-f{folio}.jpg"
    if force or not (dest.exists() and dest.stat().st_size > 10_000):
        save(split_page(cached_image(f"frame_{frame:04d}.jpg", LOC_IIIF.format(frame=frame)), side), dest)
    return f"{KEY}/{dest.name}"


# ---------------------------------------------------------------------------
def _text(el):
    out = []

    def walk(e):
        if e.tag in (TEI + "note", TEI + "bibl"):
            if e.tail:
                out.append(e.tail)
            return
        if e.text:
            out.append(e.text)
        for c in e:
            walk(c)
        if e.tail:
            out.append(e.tail)

    if el.text:
        out.append(el.text)
    for c in el:
        walk(c)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def normalize_elision(t):
    """The digital text encodes Lake's elision apostrophe in three ways
    (consonant + combining U+0313, 'παῤ', 'δἰ'); write them as Lake prints them."""
    t = re.sub(r"([βγδζθκλμνξπρστφχψ])̓(?=[\s,.;·:]|$)", "\\1’", t)
    t = re.sub(r"(?<!\w)παῤ(?=\s)", "παρ’", t)
    t = re.sub(r"(?<!\w)([Δδ])ἰ(?=\s)", "\\1ι’", t)
    return t


def greek(work):
    root = ET.parse(SRC / WORKS[work]["tei"]).getroot()
    body = root.find(f".//{TEI}body")
    secs = {}
    for ch in body.iter(TEI + "div"):
        if ch.get("subtype") != "chapter":
            continue
        cn = 0 if ch.get("n") == "preface" else int(ch.get("n"))
        for s in ch:
            if s.tag == TEI + "div" and s.get("subtype") == "section":
                secs[(cn, int(s.get("n")))] = _text(s)
    for w, ref, wrong, right in GREEK_FIXES:
        if w == work:
            k = tuple(int(x) for x in ref.split("."))
            assert wrong in secs[k], (ref, wrong)
            secs[k] = secs[k].replace(wrong, right)
    out = {}
    for (c, s), t in sorted(secs.items()):
        t = normalize_elision(t).replace(":", "·")
        assert not re.search(r"[A-Za-z?ʽʼ]", t), (work, c, s, t)
        out.setdefault(c, []).append((s, t))
    return out


def english(work):
    t = (SRC / WORKS[work]["html"]).read_text(encoding="latin-1")
    lab = WORKS[work]["label"]
    out, notes = {}, []
    for m in re.finditer(rf"<p>\s*{lab} (prologue|\d+):(\d+)\s*<br>(.*?)</p>", t, re.S | re.I):
        c = 0 if m.group(1) == "prologue" else int(m.group(1))
        body = m.group(3)
        body = re.sub(r"<I>(.*?)</I>", r"<em>\1</em>", body, flags=re.S | re.I)
        body = re.sub(r"<br\s*/?>", " ", body, flags=re.I)
        body = re.sub(r"<(?!/?em>)[^>]+>", " ", body)
        body = html.unescape(re.sub(r"\s+", " ", body)).strip()
        for n in re.findall(r"\{([^}]*)\}", body):
            notes.append(f"{lab.replace('Clem', ' Clem')} {m.group(1)}:{m.group(2)}: " + re.sub(r"<[^>]+>", "", n).strip())
        body = re.sub(r"\s*\{[^}]*\}\s*", " ", body).strip()
        body = re.sub(r"\s+([,;:.?!])", r"\1", body)
        body = re.sub(r"(<em>)\s+", r"\1", body)
        body = re.sub(r"\s+(</em>)", r"\1", body)
        out.setdefault(c, []).append((int(m.group(2)), body))
    return out, notes


def a_pages_for(work, chapter):
    res = []
    for leaf, (folio, cap, spans) in A_PAGES.items():
        for (w, c1, v1, c2, v2) in spans:
            if w == work and c1 <= chapter <= c2:
                res.append(leaf)
    return res


# ---------------------------------------------------------------------------
def build_work(work, force):
    grc = greek(work)
    eng, eng_notes = english(work)
    n = WORKS[work]["chapters"]
    chapters = ([0] if work == 1 else []) + list(range(1, n + 1))
    assert sorted(grc) == chapters and sorted(eng) == chapters, (sorted(grc), sorted(eng))
    sections, scan_paths = [], []
    for c in chapters:
        leaves = a_pages_for(work, c)
        hfol = H_CHAPTERS.get((work, c), [])
        pages, notes = [], []
        for leaf in leaves:
            folio, cap, spans = A_PAGES[leaf]
            pages.append(a_scan(leaf, force))
            notes.append(f"Codex Alexandrinus fol. {folio} (1909 facsimile, scan leaf {leaf}; caption printed under the plate: '{cap}')")
        for f in hfol:
            frame, side, words, where = H_PAGES[f]
            pages.append(h_scan(f, force))
            notes.append(f"Codex Hierosolymitanus 54 fol. {f} (LoC microfilm frame {frame}, {'left' if side == 'L' else 'right'} page), "
                         f"checked on the image: the page opens '{words}' ({where})")
            if f in H_NEXT:
                nf, nw, nwhere = H_NEXT[f]
                notes.append(f"the next page, fol. {nf}, opens '{nw}' ({nwhere})")
        gap = ""
        if work == 1 and c == 57:
            gap = " Alexandrinus carries 57.1-6 (fol. 167v, where the foot of the second column is damaged); 57.7 is lost there and is on Hierosolymitanus 54 fol. 68r."
        elif work == 1 and 58 <= c <= 63:
            gap = " This chapter is lost from Codex Alexandrinus (a missing leaf between fol. 167v and 168r) and is shown on Hierosolymitanus 54."
        elif work == 2 and c == 12:
            gap = " Alexandrinus breaks off in 12.5 at the foot of fol. 169v, its last surviving page; the rest of the chapter is on Hierosolymitanus 54 fol. 73v."
        elif work == 2 and c > 12:
            gap = " This chapter is lost from Codex Alexandrinus, whose last surviving page ends in 12.5, and is shown on Hierosolymitanus 54."
        label = "salutation" if c == 0 else str(c)
        g = " ".join(f"<sup>{s}</sup>{t}" if c else t for s, t in grc[c])
        e = " ".join(f"<sup>{v}</sup>{t}" if c else t for v, t in eng[c])
        wit = []
        if leaves:
            wit.append("Alexandrinus fol. " + ", ".join(A_PAGES[l][0] for l in leaves))
        if hfol:
            wit.append("Hierosolymitanus 54 fol. " + ", ".join(hfol))
        sections.append({
            "section": label,
            "original_ref": f"{work} Clement {'salutation' if c == 0 else c}; " + "; ".join(wit),
            "original_text": g,
            "text": e,
            "scan_pages": pages,
            "scan_note": "; ".join(notes) + "." + gap + " The Greek shown is Lake's edited text (1912), not a transcription of the manuscript page.",
        })
        scan_paths += [p for p in pages if p not in scan_paths]
    return sections, scan_paths, eng_notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    PUB.mkdir(parents=True, exist_ok=True)

    common_verif = {
        "scan_license": "Alexandrinus: public domain (1909 British Museum photographic facsimile, digitised by the Getty Research Institute for the Internet Archive). "
                        "Hierosolymitanus 54: public domain ('These collections are in the public domain', Library of Congress; credit: Library of Congress Collection of Manuscripts in the Greek Orthodox Patriarchate of Jerusalem)",
        "original_text_license": "edition public domain; digital text CC BY-SA 4.0 (Open Greek and Latin, First1KGreek)",
        "translation_license": "public domain (published 1891)",
        "translator": "J. B. Lightfoot (1891)",
        "verified_date": TODAY,
    }
    meta = {
        1: {
            "title": "1 Clement (Letter of the Church of Rome to the Corinthians), on Codex Alexandrinus",
            "description": "The letter of the church at Rome to the church at Corinth, traditionally ascribed to Clement of Rome (c. 96 AD), shown chapter by chapter on the pages of Codex Alexandrinus (5th c.), with the lost chapters 57-63 on Codex Hierosolymitanus 54 (1056).",
            "date_approx": "c. 96 AD (composition); 5th c. (Codex Alexandrinus); 1056 (Hierosolymitanus 54)",
            "themes": ["clement-of-rome", "1-clement", "apostolic-fathers", "early-church", "corinth", "codex-alexandrinus", "greek", "verified"],
            "intro": (
                "<p><em>1 Clement</em> is a letter from the church at Rome to the church at Corinth, written because the Corinthians had removed their presbyters. "
                "It does not name its author, but from the second century it was attributed to Clement, a leader of the Roman church, and it is usually dated "
                "to the 90s AD. It is one of the oldest Christian writings outside the New Testament; it mentions the deaths of Peter and Paul (chapter 5).</p>\n\n"
                "<p>The oldest manuscript is Codex Alexandrinus (London, British Library, Royal MS 1 D. VIII, 5th century), where 1 and 2 Clement follow the Book of Revelation "
                "on fol. 159r-169v. The pages are shown from the photographic facsimile published by the British Museum in 1909. "
                "Each section is linked to the facsimile plate or plates that carry the chapter, using the caption the facsimile prints beneath each plate.</p>\n\n"
                "<p>One leaf of Alexandrinus is lost between fol. 167v and fol. 168r, taking 57.7 to the end of chapter 63, and the foot of the second column of fol. 167v is damaged. "
                "Those chapters are shown on the only other complete Greek manuscript, Codex Hierosolymitanus 54 (Jerusalem, dated 1056), from the Library of Congress microfilm. "
                "The Greek is Kirsopp Lake's edition (1912); the English is J. B. Lightfoot's translation (1891).</p>"),
        },
        2: {
            "title": "2 Clement (an early Christian sermon), on Codex Alexandrinus",
            "description": "The oldest surviving Christian sermon outside the New Testament, transmitted as Clement's second letter to the Corinthians, shown chapter by chapter on Codex Alexandrinus (5th c.) and, after 12.5 where Alexandrinus breaks off, on Codex Hierosolymitanus 54 (1056).",
            "date_approx": "mid 2nd c. AD (composition); 5th c. (Codex Alexandrinus); 1056 (Hierosolymitanus 54)",
            "themes": ["2-clement", "apostolic-fathers", "early-church", "sermon", "codex-alexandrinus", "greek", "verified"],
            "intro": (
                "<p><em>2 Clement</em> is a sermon calling its hearers to repentance and self-control, read aloud in an assembly (\"I read you an exhortation\", 19.1). "
                "Manuscripts transmit it after 1 Clement as Clement's second letter to the Corinthians, but it is not a letter and is usually thought to be by another, "
                "unknown author of the second century. It is often called the oldest complete Christian sermon after the New Testament.</p>\n\n"
                "<p>In Codex Alexandrinus (British Library, Royal MS 1 D. VIII, 5th century) it begins on fol. 168r after the end of 1 Clement and breaks off in 12.5 "
                "at the foot of fol. 169v, the last surviving page of the codex. Those pages are shown from the British Museum's 1909 photographic facsimile, "
                "each linked by the caption printed beneath the plate. The rest of the sermon (12.5-20.5) is shown on Codex Hierosolymitanus 54 (Jerusalem, 1056), "
                "from the Library of Congress microfilm, where the page boundaries were read on the images. "
                "The Greek is Kirsopp Lake's edition (1912); the English is J. B. Lightfoot's translation (1891).</p>"),
        },
    }
    rows = []
    for work in (1, 2):
        sections, scan_paths, eng_notes = build_work(work, args.force)
        slug = WORKS[work]["slug"]
        tid = f"{PREFIX}{slug}"
        m = meta[work]
        notes = [
            f"Greek: Kirsopp Lake, The Apostolic Fathers I (Loeb Classical Library, 1912), digital text by First1KGreek (tlg1271.tlg00{work}, CC BY-SA 4.0). "
            "Lake's footnotes and scripture references are not shown. Elided words, which the digital text encodes with stray accent characters (e.g. 'δἰ', 'παῤ', 'καθ̓'), "
            "are written with an apostrophe as Lake prints them, and the digital text's colon is shown as the Greek raised dot.",
            "English: J. B. Lightfoot, The Apostolic Fathers (1891), as transcribed at earlychristianwritings.com; Lightfoot's italics (scripture quotations) are kept. "
            "Lightfoot translated his own Greek text, which differs from Lake's in places, and his verse numbers differ from Lake's in a few chapters.",
        ]
        fixes = [f for f in GREEK_FIXES if f[0] == work]
        if fixes:
            notes.append("Tokens of the digital Greek text with corrupted characters were corrected from Lake's printed page: "
                         + "; ".join(f"{r} '{w}' to '{c}'" for _, r, w, c in fixes) + ". The rest of the digital text was not proofread against the print.")
        else:
            notes.append("The digital Greek text was not proofread against Lake's printed page.")
        if eng_notes:
            notes.append("Alternative renderings that the English transcription gives in braces are left out of the text: " + " | ".join(eng_notes))
        if work == 1:
            notes.append("Codex Alexandrinus lacks 57.7-63.4 (a lost leaf); those chapters are shown on Codex Hierosolymitanus 54.")
        else:
            notes.append("Codex Alexandrinus ends in 12.5; 12.5-20.5 are shown on Codex Hierosolymitanus 54.")
        entry = {
            "id": tid, "slug": tid, "title": m["title"],
            "language": "Greek (Lake 1912) / English (Lightfoot 1891)",
            "source": "Codex Alexandrinus (1909 BM facsimile, archive.org) + Codex Hierosolymitanus 54 (LoC microfilm) + Lake 1912 Greek (First1KGreek, CC BY-SA 4.0) + Lightfoot 1891 English (public domain)",
            "description": m["description"],
            "introduction": m["intro"],
            "translator_notes": notes,
            "translation": sections,
            "verification": {
                "scan_source": f"Internet Archive {IA_ITEM} ('The Codex Alexandrinus in reduced photographic facsimile', British Museum 1909), scan leaves "
                               f"{min(l for l in A_PAGES if any(s[0] == work for s in A_PAGES[l][2]))}-{max(l for l in A_PAGES if any(s[0] == work for s in A_PAGES[l][2]))} ({IA_URL}); "
                               f"Library of Congress Microfilm 5017, Panagios Taphos 54 ({LOC_ITEM})",
                "scan_manuscript": "London, British Library, Royal MS 1 D. VIII (Codex Alexandrinus, GA 02, 5th c.), fol. 159r-169v; "
                                   "Jerusalem, Greek Orthodox Patriarchate, Panagios Taphos (Hierosolymitanus) 54 (dated 1056)",
                "scan_mapping": "Alexandrinus: the chapter range printed beneath every plate of the 1909 facsimile (all captions read on the scans), with spot checks of page openings on the images; "
                                "folio numbers from the NTVMR page list, agreeing with the numbers written on the plates. Hierosolymitanus 54: opening words of each page read on the images and located in the Greek text.",
                "scan_mapping_urls": [IA_URL, NTVMR_URL, LOC_ITEM],
                "scan_local_paths": scan_paths,
                "original_text_source": f"Kirsopp Lake, The Apostolic Fathers I (1912), First1KGreek tlg1271.tlg00{work}.1st1K-grc1 ({GREEK_URL}); corrections checked on {LAKE_PRINT}",
                "translation_source": f"J. B. Lightfoot, The Apostolic Fathers (1891), transcription at {ENGLISH_URLS[work]}",
                **common_verif,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": work,
            "title": m["title"], "author_id": "clement-of-rome" if work == 1 else "second-clement-anonymous", "language": "Greek",
            "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": m["date_approx"], "century": 1 if work == 1 else 2,
            "source": entry["source"], "description": m["description"],
            "themes": m["themes"], "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": ("Codex Alexandrinus fol. " + p.split("alex-f")[1][:-4]) if "alex-f" in p
                                 else ("Hierosolymitanus 54 fol. " + p.split("h54-f")[1][:-4])} for p in scan_paths]},
        })
        print(f"wrote {tid} ({len(sections)} sections, {len(scan_paths)} images)")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "1 and 2 Clement (Codex Alexandrinus)",
            "group": "Early Christian",
            "date_sort": 96,
            "author_name": "Clement of Rome (c. 96 AD) and an anonymous 2nd-century preacher; Codex Alexandrinus (5th c.)",
            "source_url": IA_URL,
            "critical_edition": "Kirsopp Lake, The Apostolic Fathers I (1912), via First1KGreek",
            "translator_name": "J. B. Lightfoot (1891)",
            "original_lang_label": "Greek · Lake 1912",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "clement of rome 1 clement 2 clement corinthians apostolic fathers codex alexandrinus",
            "description": "1 Clement, the letter of the Roman church to Corinth, and 2 Clement, an early sermon, on the last pages of Codex Alexandrinus, with the lost passages on Codex Hierosolymitanus 54.",
        },
        "texts": rows,
        "authors": [
            {"id": "clement-of-rome", "name": "Clement of Rome", "dates": "fl. c. 96 AD", "century": 1, "era": "Apostolic",
             "tradition": "christian", "language": "Greek",
             "bio": "Leader of the church at Rome at the end of the first century, to whom early tradition ascribes the letter known as 1 Clement."},
            {"id": "second-clement-anonymous", "name": "2 Clement (anonymous preacher)", "dates": "2nd c. AD", "century": 2, "era": "Apostolic",
             "tradition": "christian", "language": "Greek",
             "bio": "Unknown author of the second-century sermon transmitted as Clement's second letter to the Corinthians."},
        ],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
