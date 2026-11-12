#!/usr/bin/env python3
"""
import_upanishads.py — Principal Upanishads on one Sanskrit manuscript (Penn Ms. Coll. 390 Item 869).

Entries (14): Isa (1), Katha (6, one per valli), Prasna (6, one per question), Mandukya (1).
Every section is one folio side (or the two sides a verse straddles) of the manuscript.

Chain of evidence:
  1. SCAN     University of Pennsylvania, Kislak Center, Ms. Coll. 390 Item 869, "Six early upanisads",
              16 paper leaves, 13 x 27 cm, 11-13 lines per side, 18th or 19th century (catalogue genre terms),
              undated. OPenn master TIFFs (Public Domain Mark):
              https://openn.library.upenn.edu/Data/0002/html/mscoll390_item869.html
              Each OPenn photograph shows an opening (verso above, following recto below); the importer
              crops each leaf into its own JPEG (penn869-fNNv.jpg / fNNr.jpg).
  2. MAPPING  Read by eye on every page used (Nov. 2026). The manuscript does not number verses; each
              verse was located by its words, and chapter ends by the scribe's colophons and section
              numbers. Line-by-line readings: data/sources/upanishads/mapping_notes_869.txt (also written
              to data/sources/upanishads/mapping_log.json). The catalogue's folio ranges for Katha, Prasna,
              Mundaka and Mandukya are off; the marginal titles (kaTha, prazno, muNDaka) and the scribe's
              colophons confirm the ranges used here.
  3. SANSKRIT GRETIL (CC BY-NC-SA 4.0): Isa, Kanva recension (Sansknet input, checked against
              Limaye & Vadekar 1958); Katha (Vienna student team, after Olivelle 1998); Prasna (Sansknet
              input, mula text of the file with Samkara's commentary); Mandukya (input by Jeff Samuels).
  4. ENGLISH  F. Max Müller, The Upanishads, SBE vol. 1 (1879: Vajasaneyi-samhita-upanishad = Isa) and
              vol. 15 (1884: Katha, Prasna), English Wikisource proofread transcription (public domain).
              Mandukya: R. E. Hume, The Thirteen Principal Upanishads (1921), transcribed from the
              archive.org page images (public domain in the US).

Not published (reported in docs/collections/upanishads.md): Kena and Mundaka (fol. 2r-3v, 12v-15v of the
same manuscript, mapped in the notes) because no openly licensed, reliable Sanskrit e-text was found
(GRETIL has none; the Sanskrit Wikisource texts carry many misprints and a non-standard verse division).

Usage:
    python3 scripts/import_upanishads.py                 # build (downloads TIFFs only for missing scans)
    python3 scripts/import_upanishads.py --tif-dir DIR   # use already downloaded OPenn TIFFs (6128_00NN.tif)
    python3 scripts/import_upanishads.py --force         # re-make scans
"""

import argparse
import html as htmlmod
import json
import re
import tempfile
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = "upanishads"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"

OPENN_ITEM = "https://openn.library.upenn.edu/Data/0002/html/mscoll390_item869.html"
OPENN_MASTER = "https://openn.library.upenn.edu/Data/0002/mscoll390_item869/data/master/6128_{:04d}.tif"
MS_NAME = "Penn Ms. Coll. 390 Item 869"
MS_DESC = ("University of Pennsylvania, Kislak Center for Special Collections, Ms. Coll. 390 Item 869 "
           "('Six early upanisads'), 16 paper leaves, 13 x 27 cm, 11-13 lines per side, Devanagari, "
           "18th or 19th century, undated; contains Isa, Kena, Katha, Prasna, Mundaka and Mandukya")
SCAN_LICENSE = ("Public Domain Mark 1.0: 'These images and the content of Ms. Coll. 390 Item 869 are free of "
                "known copyright restrictions and in the public domain' (University of Pennsylvania, OPenn)")
GRETIL = "https://gretil.sub.uni-goettingen.de/gretil/corpustei/"
WS = "https://en.wikisource.org/wiki/"

# --------------------------------------------------------------------------------------------
# Scans: spread index -> (top leaf = verso, bottom leaf = following recto)
# --------------------------------------------------------------------------------------------
ITEMS = {
    "869": {"name": "Penn Ms. Coll. 390 Item 869", "tif": "6128_{:04d}.tif", "single": {16}, "narrow": {2, 4, 6},
            "url": "https://openn.library.upenn.edu/Data/0002/html/mscoll390_item869.html",
            "master": "https://openn.library.upenn.edu/Data/0002/mscoll390_item869/data/master/6128_{:04d}.tif",
            "notes": "data/sources/upanishads/mapping_notes_869.txt"},
    "1213": {"name": "Penn Ms. Coll. 390 Item 1213", "tif": "5439_{:04d}.tif", "single": {7}, "narrow": set(),
             "url": "https://openn.library.upenn.edu/Data/0002/html/mscoll390_item1213.html",
             "master": "https://openn.library.upenn.edu/Data/0002/mscoll390_item1213/data/master/5439_{:04d}.tif",
             "notes": "data/sources/upanishads/mapping_notes_1213.txt"},
}
ITEMS["945"] = {"name": "Penn Ms. Coll. 390 Item 945", "tif": "6239_{:04d}.tif", "single": {0, 74}, "narrow": set(),
                "url": "https://openn.library.upenn.edu/Data/0002/html/mscoll390_item945.html",
                "master": "https://openn.library.upenn.edu/Data/0002/mscoll390_item945/data/master/6239_{:04d}.tif",
                "notes": "data/sources/upanishads/mapping_945.json", "width": 2000}
ITEMS["1216"] = {"name": "Penn Ms. Coll. 390 Item 1216", "tif": "5409_{:04d}.tif", "single": {0, 7}, "narrow": {1, 4, 6},
                 "band": (0.45, 0.55),
                 "url": "https://openn.library.upenn.edu/Data/0002/html/mscoll390_item1216.html",
                 "master": "https://openn.library.upenn.edu/Data/0002/mscoll390_item1216/data/master/5409_{:04d}.tif",
                 "notes": "data/sources/upanishads/mapping_notes_1216.txt", "width": 2000}
NEEDED_1216 = ["f01v", "f02r", "f02v", "f03r", "f03v", "f04r", "f04v", "f05r", "f05v", "f06r", "f06v", "f07r"]
MS_DESC_1216 = ("University of Pennsylvania, Kislak Center for Special Collections, Ms. Coll. 390 Item 1216 "
                "(Aitareyopanisad, followed by the opening of a Narayanopanisad), 7 paper leaves, 10 x 24 cm, 7 lines per "
                "side, Devanagari with red accent marks, undated (catalogued 18th/19th c.)")
MS_DESC_945 = ("University of Pennsylvania, Kislak Center for Special Collections, Ms. Coll. 390 Item 945 "
               "(Chandogyopanisad, prapathakas 1-8), 74 paper leaves, 11 x 17 cm, 10-11 lines per side, Devanagari, "
               "blue machine-made paper with watermarks, undated (catalogued 18th/19th c.)")


def needed_945():
    m = json.loads((SRC / "mapping_945.json").read_text(encoding="utf-8"))
    return sorted({pg["page"] for pages in m.values() for pg in pages})


NEEDED_1213 = ["f01v", "f02r", "f02v", "f03r", "f03v", "f04r", "f04v", "f05r", "f05v", "f06r", "f06v", "f07r", "f07v"]
MS_DESC_1213 = ("University of Pennsylvania, Kislak Center for Special Collections, Ms. Coll. 390 Item 1213 "
                "(Chandogyopanisad, sixth prapathaka), 7 paper leaves, 11 x 24 cm, 9-10 lines per side, Devanagari, "
                "with red accent marks; dated saka 1758 (1836 CE) in the colophon on fol. 7v")
NEEDED = ["f01v", "f02r", "f03v", "f04r", "f04v", "f05r", "f05v", "f06r", "f06v", "f07r", "f07v",
          "f08r", "f08v", "f09r", "f09v", "f10r", "f10v", "f11r", "f11v", "f12r", "f12v", "f16r", "f16v"]
# spreads where the two leaves touch: search the cut in a narrow band
NARROW = {2, 4, 6}


def folio_source(fol):
    n, side = int(fol[1:3]), fol[3]
    if side == "v":
        return n, 0          # spread n, top
    return n - 1, 1          # spread n-1, bottom


def fetch(url, binary=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def split_spread(tif_path, n_leaves, narrow, width=2400, band=(0.47, 0.53)):
    """Return leaf images (top first) cropped from an OPenn spread photograph."""
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(tif_path).convert("RGB")
    W, H = im.size
    f = 8
    a = np.asarray(im.resize((W // f, H // f))).astype(float).mean(axis=2)
    br = a > 110
    rows = br.mean(axis=1)
    h = len(rows)
    if n_leaves == 2:
        lo, hi = (int(h * band[0]), int(h * band[1])) if narrow else (int(h * 0.35), int(h * 0.65))
        cut = lo + int(np.argmin(rows[lo:hi]))
        halves = [(0, cut), (cut, h)]
    else:
        halves = [(0, h)]
    out = []
    for r0, r1 in halves:
        ys = np.where(br[r0:r1].mean(axis=1) > 0.30)[0]
        y0, y1 = r0 + ys.min(), r0 + ys.max()
        xs = np.where(br[y0:y1].mean(axis=0) > 0.30)[0]
        x0, x1 = xs.min(), xs.max()
        pad = 10
        box = (max(0, (x0 - pad) * f), max(0, (y0 - pad) * f), min(W, (x1 + pad) * f), min(H, (y1 + pad) * f))
        leaf = im.crop(box)
        lw, lh = leaf.size
        if lw > width:
            leaf = leaf.resize((width, round(lh * width / lw)), Image.LANCZOS)
        out.append(leaf)
    return out


def make_scans(tif_dirs, force):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for item, needed in (("869", NEEDED), ("1213", NEEDED_1213), ("945", needed_945()), ("1216", NEEDED_1216)):
        cfg = ITEMS[item]
        spreads = {}
        for fol in needed:
            sp, pos = folio_source(fol)
            spreads.setdefault(sp, []).append((pos, fol))
        for sp, items in sorted(spreads.items()):
            if not force and all((SCAN_DIR / f"penn{item}-{fol}.jpg").exists() for _, fol in items):
                continue
            local = None
            for d in tif_dirs or []:
                if (Path(d) / cfg["tif"].format(sp)).exists():
                    local = Path(d) / cfg["tif"].format(sp)
            tmp = None
            if local is None:
                tmp = tempfile.TemporaryDirectory()
                local = Path(tmp.name) / cfg["tif"].format(sp)
                print(f"  downloading {cfg['master'].format(sp)}")
                local.write_bytes(fetch(cfg["master"].format(sp)))
            leaves = split_spread(local, 1 if sp in cfg["single"] else 2, sp in cfg["narrow"], cfg.get("width", 2400),
                                  cfg.get("band", (0.47, 0.53)))
            for pos, fol in items:
                out = SCAN_DIR / f"penn{item}-{fol}.jpg"
                leaves[pos].save(out, quality=85)
                print(f"  {out.relative_to(ROOT)} {leaves[pos].size}")
            if tmp:
                tmp.cleanup()


def scan(fol, item="869"):
    return f"{KEY}/penn{item}-{fol}.jpg"


def viewer(fol):
    return OPENN_ITEM


# --------------------------------------------------------------------------------------------
# Sanskrit (GRETIL TEI)
# --------------------------------------------------------------------------------------------
def gretil(name):
    p = SRC / "gretil" / f"{name}.xml"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(GRETIL + f"{name}.xml"))
    return p.read_text(encoding="utf-8")


def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(t)).strip()


def lines_html(lines):
    return "<br>".join(x.strip() for x in lines if x.strip())


def load_isa():
    s = gretil("sa_IzopaniSad-or-IzAvAsyopaniSadkANva-recension-comm")
    out = {}
    for m in re.finditer(r'<hi rend="bold">(.*?)</hi>', s, re.S):
        body = m.group(1)
        r = re.search(r"\|\|\s*IsUp_(\d+)\s*\|\|", body)
        if not r:
            continue
        txt = body[:r.start()] + "||"
        out[int(r.group(1))] = lines_html(clean(txt).split("\n"))
    assert sorted(out) == list(range(1, 19)), sorted(out)
    return out


def load_katha():
    s = gretil("sa_kathopaniSad")
    s = s[s.find("<body"):]
    out, buf = {}, []
    # verse lines are <l> elements; a refrain ('etad vai tat // KaU_4.3 //') can stand in its own <l> after the <lg>
    for x in re.findall(r"<l>(.*?)</l>", s, re.S):
        ln = clean(x)
        r = re.search(r"//\s*KaU_(\d+)\.(\d+)\s*//", ln)
        if r:
            buf.append(re.sub(r"\s*//\s*KaU_\d+\.\d+\s*//", " //", ln))
            out[(int(r.group(1)), int(r.group(2)))] = lines_html(buf)
            buf = []
        else:
            buf.append(ln)
    counts = {v: max(k[1] for k in out if k[0] == v) for v in range(1, 7)}
    assert counts == {1: 29, 2: 25, 3: 17, 4: 15, 5: 15, 6: 18}, counts
    assert len(out) == 119
    return out


def load_prasna():
    s = gretil("sa_praznopaniSad-comm")
    s = s[s.find("<body"):]
    out = {}
    for m in re.finditer(r"START PrUp (\d+)\.(\d+)", s):
        q, v = int(m.group(1)), int(m.group(2))
        rest = s[m.end():]
        r = re.search(r"(\|\||//)\s*PrUp_%d\.%d\s*(\|\||//)" % (q, v), rest)
        assert r, (q, v)
        seg = rest[:r.end() + 40]   # include the closing tag(s) after the reference
        # keep only the mula (bold) part; the commentary sometimes puts a sentence before it
        bold = re.findall(r'<(hi|lg|l) rend="bold">(.*?)</\1>', seg, re.S)
        assert bold, (q, v)
        seg = "\n".join(b for _, b in bold)
        seg = re.sub(r"(\|\||//)\s*PrUp_\d+\.\d+\s*(\|\||//)", "", seg)
        seg = re.sub(r"</?(p|hi|lg|l)[^>]*>", "\n", seg)
        ls = [clean(x) for x in seg.split("\n")]
        ls = [x for x in ls if x]
        ls[-1] = ls[-1] + " " + r.group(1)
        out[(q, v)] = lines_html(ls)
    # GRETIL's 2.9 (in both the TEI and the legacy mula file) gives Samkara's paraphrase of the verse
    # ('rudro 'si saṃharañ jagat | sthitau ca pari samantād rakṣitā pālayitā ...') instead of the verse itself.
    # It is not shown; the section marks the gap.
    assert "pālayitā" in out[(2, 9)]
    out[(2, 9)] = '<span class="lacuna">[…]</span>'

    counts = {q: max(k[1] for k in out if k[0] == q) for q in range(1, 7)}
    assert counts == {1: 16, 2: 13, 3: 12, 4: 11, 5: 7, 6: 8}, counts
    assert len(out) == 67, len(out)
    return out


def load_chandogya(pr):
    """Chandogya Upanisad prapathaka pr: the mula (bold) text of GRETIL's file with Samkara's commentary.
    Paragraphs close at a reference 'ChUp_pr,k.v' or, where GRETIL entered a paragraph in another style, at '//v//'
    (its khanda is then taken from the preceding reference and khanda colophons). Khanda and chapter colophons
    ('iti cchāndogyopaniṣadi ... khaṇḍaḥ') are skipped."""
    s = gretil("sa_chAndogyopaniSad-comm")
    a = s.find(f"START ChUp {pr},1.1")
    b = s.find(f"START ChUp {pr + 1},1.1") if pr < 8 else len(s)
    s = s[a:b]
    out, buf, cur_k, after_colophon, alt = {}, [], 1, False, set()
    for tag, body in re.findall(r'<(hi|lg|l) rend="bold">(.*?)</\1>', s, re.S):
        txt = re.sub(r"</?(p|hi|lg|l)[^>]*>", "\n", body)
        ls = [clean(x) for x in txt.split("\n")]
        ls = [x for x in ls if x]
        if not ls:
            continue
        joined = " ".join(ls)
        if joined.strip(" |/") in ("oṃ", "hariḥ oṃ", "oṃ hariḥ"):
            continue                     # invocation syllable between chapters
        if re.match(r"(iti|atha) ", ls[0]) and re.search(r"khaṇḍaḥ|prapāṭhakaḥ|dhyāyaḥ", joined) \
                and (len(joined) < 80 or "vivaraṇe" in joined):
            after_colophon = True        # khanda / chapter colophons (and the commentary's chapter colophon)
            continue
        r = re.search(r"(\|\||//)\s*ChUp_%d,(\d+)\.(\d+)\s*(\|\||//)" % pr, joined)
        r2 = re.search(r"//\s*(\d+)\s*//\s*$", joined)
        if r:
            k, v = int(r.group(2)), int(r.group(3))
            ls[-1] = re.sub(r"\s*(\|\||//)\s*ChUp_\d+,\d+\.\d+\s*(\|\||//)", " " + r.group(1), ls[-1])
        elif r2:
            k, v = (cur_k + 1 if after_colophon else cur_k), int(r2.group(1))
            ls[-1] = re.sub(r"//\s*\d+\s*//\s*$", "//", ls[-1])
        else:
            buf.extend(ls)
            continue
        buf.extend(ls)
        if (k, v) in out:
            # GRETIL sometimes enters a paragraph twice (an unreferenced '//v//' copy next to the referenced one):
            # the referenced copy is kept
            assert (k, v) in alt or r is None, (pr, k, v)
            if r is None:
                buf, cur_k, after_colophon = [], k, False
                continue
        out[(k, v)] = lines_html(buf)
        if r is None:
            alt.add((k, v))
        else:
            alt.discard((k, v))
        buf, cur_k, after_colophon = [], k, False
    assert not buf, (pr, buf)
    # legacy-encoding artifacts in the GRETIL file, normalized (listed in the entry notes)
    for (p2, k, v), (a, b2) in CHU_GRETIL_FIXES.items():
        if p2 == pr:
            assert out[(k, v)].count(a) == 1, (p2, k, v, a)
            out[(k, v)] = out[(k, v)].replace(a, b2)
    return out


CHU_GRETIL_FIXES = {
    (2, 8, 1): ("saptavidh.am", "saptavidham"),
    (2, 12, 2): ("brahmavarcasy: annādo", "brahmavarcasy annādo"),
    (2, 14, 2): ("tejasvy: annādo", "tejasvy annādo"),
}


def load_chandogya6():
    out = load_chandogya(6)
    counts = {k: max(x[1] for x in out if x[0] == k) for k in range(1, 17)}
    assert counts == {1: 7, 2: 4, 3: 4, 4: 7, 5: 4, 6: 5, 7: 6, 8: 7, 9: 4, 10: 3, 11: 3, 12: 3, 13: 3, 14: 3,
                      15: 3, 16: 3}, counts
    assert len(out) == 69, len(out)
    # legacy-encoding artifact in GRETIL 6.13.2: 'an;gāsyāntād' (n; = ṅ); shown as aṅgāsyāntād
    assert out[(13, 2)].count("an;gā") == 1
    out[(13, 2)] = out[(13, 2)].replace("an;gā", "aṅgā")
    return out


def load_aitareya():
    """Aitareya Upanisad (Samkara's division 1.1.1-3.4): the mula (bold) text of GRETIL's file with his commentary."""
    s = gretil("sa_aitareyopaniSad-comm")
    s = s[s.find("<body"):]
    out = {}
    for tag, body in re.findall(r'<(hi|lg|l) rend="bold">(.*?)</\1>', s, re.S):
        txt = re.sub(r"</?(p|hi|lg|l)[^>]*>", "\n", body)
        ls = [clean(x) for x in txt.split("\n") if clean(x)]
        joined = " ".join(ls)
        r = re.search(r"(\|\||//)\s*AitUp_(\d+(?:,\d+)?\.\d+)\s*(\|\||//)", joined)
        if not r:
            continue
        ls[-1] = re.sub(r"\s*(\|\||//)\s*AitUp_[\d,.]+\s*(\|\||//)", " " + r.group(1), ls[-1])
        out[r.group(2).replace(",", ".")] = lines_html(ls)
    assert len(out) == 33, len(out)
    return out


def load_mandukya():
    s = gretil("sa_mANDUkyopaniSad-alt")
    b = s[s.find("<body"):]
    # mark verse lines, keep TEI <l> lines as line breaks
    b = re.sub(r"</l>\s*<l>", "\n", b)
    t = re.sub(r"<[^>]+>", "\n", b)
    parts = re.split(r"(Māṇḍūkya Upaniṣad|Māṇḍūkya Kārikā|Verse \d+)", t)
    mode, cur, out = None, None, {}
    for p in parts:
        if p in ("Māṇḍūkya Upaniṣad", "Māṇḍūkya Kārikā"):
            mode = p
            continue
        m = re.match(r"Verse (\d+)$", p)
        if m:
            cur = int(m.group(1))
            continue
        if mode == "Māṇḍūkya Upaniṣad" and cur and p.strip():
            ls = [clean(x) for x in p.split("\n") if clean(x)]
            out.setdefault(cur, []).extend(ls)
    out = {k: lines_html(v) for k, v in out.items()}
    assert sorted(out) == list(range(1, 13)), sorted(out)
    return out


# --------------------------------------------------------------------------------------------
# English: Müller (English Wikisource, proofread pages) and Hume 1921 (transcribed)
# --------------------------------------------------------------------------------------------
WS_PAGES = {
    "isa": "Sacred Books of the East/Volume 1/Vâgasaneyi-samhitâ-upanishad",
    "katha": "Sacred Books of the East/Volume 15/Katha-upanishad",
    "prasna": "Sacred Books of the East/Volume 15/Prasña-upanishad",
    "chandogya6": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Sixth Prapâthaka",
    "chandogya1": "Sacred Books of the East/Volume 1/Khândogya-upanishad/First Prapâthaka",
    "chandogya2": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Second Prapâthaka",
    "chandogya3": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Third Prapâthaka",
    "chandogya4": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Fourth Prapâthaka",
    "chandogya5": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Fifth Prapâthaka",
    "chandogya7": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Seventh Prapâthaka",
    "chandogya8": "Sacred Books of the East/Volume 1/Khândogya-upanishad/Eighth Prapâthaka",
}
ORD = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8,
       "NINTH": 9, "TENTH": 10, "ELEVENTH": 11, "TWELFTH": 12, "THIRTEENTH": 13, "FOURTEENTH": 14,
       "FIFTEENTH": 15, "SIXTEENTH": 16, "SEVENTEENTH": 17, "EIGHTEENTH": 18, "NINETEENTH": 19, "TWENTIETH": 20,
       "TWENTY-FIRST": 21, "TWENTY-SECOND": 22, "TWENTY-THIRD": 23, "TWENTY-FOURTH": 24, "TWENTY-FIFTH": 25,
       "TWENTY-SIXTH": 26}


def ws_html(key):
    p = SRC / "english" / f"ws_{key}.json"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://en.wikisource.org/w/api.php?action=parse&prop=text&format=json&formatversion=2&page="
               + urllib.parse.quote(WS_PAGES[key]))
        p.write_bytes(fetch(url))
    return json.loads(p.read_text(encoding="utf-8"))["parse"]["text"]


WS_LABELS = {}


def ws_units(key):
    """Return list of (heading_stack, number, html) for numbered paragraphs on a Wikisource page."""
    h = ws_html(key)
    h = re.sub(r"<style.*?</style>", "", h, flags=re.S)
    h = re.sub(r'<sup[^>]*class="reference".*?</sup>', "", h, flags=re.S)
    h = re.sub(r'<ol class="references">.*?</ol>', "", h, flags=re.S)
    h = re.sub(r"<i>(.*?)</i>", r"[[EM]]\1[[/EM]]", h, flags=re.S)
    h = re.sub(r"<br\s*/?>|</p>|<p[^>]*>|</div>|<div[^>]*>", "\n", h)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", "", h)).replace("​", "")
    lines = [re.sub(r"[ \t]+", " ", x).strip() for x in t.split("\n")]
    units, heads, cur = [], [], None
    for ln in lines:
        if not ln:
            continue
        plain = ln.replace("[[EM]]", "").replace("[[/EM]]", "")
        if plain == "Footnotes":
            break
        if plain.startswith("↑"):
            continue
        m = re.match(r"^(\d+)(?:,\s*\d+)*\.\s+(.*)$", ln)
        hm = re.match(r"^(" + "|".join(ORD) + r")\s+(\S+)", plain, re.I)
        if m:
            cur = [list(heads), int(m.group(1)), m.group(2)]
            WS_LABELS[(key, len(units))] = re.match(r"^([\d,\s]+)\.", ln).group(1).replace(" ", "")
            units.append(cur)
        elif hm and len(plain) < 40:
            heads.append((hm.group(1).upper(), hm.group(2).rstrip(".").upper()))
            cur = None
        elif cur is not None and not plain.isupper():
            cur[2] = cur[2] + " " + ln     # verse continued across a printed page
    out = []
    for hs, n, txt in units:
        txt = re.sub(r"\s+", " ", txt).strip()
        txt = txt.replace("[[EM]]", "<em>").replace("[[/EM]]", "</em>")
        out.append((hs, n, txt))
    return out


# Wikisource transcription slips, corrected to the printed pages (checked on the page images of the
# djvu scan behind the transcription: SBE 15 djvu pp. 64, 71, 73, 83).
WS_FIXES = {
    ("katha", (1, 13)): [("fire-sacrificef which", "fire-sacrifice which")],
    ("katha", (2, 23)): [("the Self can be can gained", "the Self can be gained")],
    ("katha", (3, 13)): [("the Self whichs is the Great", "the Self which is the Great")],
    ("katha", (6, 15)): [("Whean all the ties", "When all the ties")],
    # SBE 1 p. 100 (archive.org OCR of the printed page agrees: 'a second')
    ("chandogya6", (11, 2)): [("if it leaves at second", "if it leaves a second")],
}


def apply_fixes(work, d):
    for (w, k), pairs in WS_FIXES.items():
        if w != work:
            continue
        for a, b in pairs:
            assert d[k].count(a) == 1, (w, k, a)
            d[k] = d[k].replace(a, b)
    return d


def eng_isa():
    u = ws_units("isa")
    out = {n: t for _, n, t in u if 1 <= n <= 18}
    assert sorted(out) == list(range(1, 19))
    # Müller's essay on the Upanishad follows verse 18 on the page; keep the verse only
    end = "(Rv. I, 189, 1.)"
    assert end in out[18]
    out[18] = out[18][:out[18].index(end) + len(end)]
    return out


def eng_katha():
    # Paired by order within each valli: the Wikisource transcription misnumbers I.3.15-17 as 18-20 (the
    # printed page, SBE 15 p. 14, has 15-17). The extra 19th paragraph of valli VI is the closing invocation
    # 'May He protect us both!' (saha nāv avatu), which the manuscript writes as the opening of the Prasna.
    seq = {}
    for hs, n, t in ws_units("katha"):
        vallis = [h for h in hs if h[1].startswith("VALL")]
        if not vallis:
            continue
        seq.setdefault(ORD[vallis[-1][0]], []).append(t)
    assert seq[6][18].startswith("May He protect us both"), seq[6][18][:40]
    seq[6] = seq[6][:18]
    out = {(v, i + 1): t for v, ts in seq.items() for i, t in enumerate(ts)}
    counts = {v: max(k[1] for k in out if k[0] == v) for v in range(1, 7)}
    assert counts == {1: 29, 2: 25, 3: 17, 4: 15, 5: 15, 6: 18}, counts
    assert len(out) == 119, len(out)
    return apply_fixes("katha", out)


def eng_prasna():
    out = {}
    for hs, n, t in ws_units("prasna"):
        qs = [h for h in hs if h[1].startswith("QUESTION") or h[1].startswith("PRAS")]
        if not qs:
            continue
        out[(ORD[qs[-1][0]], n)] = t
    counts = {q: max(k[1] for k in out if k[0] == q) for q in range(1, 7)}
    assert counts == {1: 16, 2: 13, 3: 12, 4: 11, 5: 7, 6: 8}, counts
    assert len(out) == 67, len(out)
    return out


def eng_chandogya6():
    """Müller's numbering: khandas 15 and 16 have two paragraphs each (his 2 = the edition's 2 and 3)."""
    out = {}
    for hs, n, t in ws_units("chandogya6"):
        ks = [h for h in hs if h[1].startswith("KHANDA")]
        if ks:
            out[(ORD[ks[-1][0]], n)] = t
    counts = {k: max(x[1] for x in out if x[0] == k) for k in range(1, 17)}
    assert counts == {1: 7, 2: 4, 3: 4, 4: 7, 5: 4, 6: 5, 7: 6, 8: 7, 9: 4, 10: 3, 11: 3, 12: 3, 13: 3, 14: 3,
                      15: 2, 16: 2}, counts
    return apply_fixes("chandogya6", out)


# Wikisource transcription slips in SBE 1, corrected to the printed page. 1.9.2 checked on the page image (SBE 1
# p. 17); the others against the archive.org OCR of the same 1879 printing (copy upanishads01mluoft), which reads the
# printed words. The heading 'Elventh Khanda.' is merged into 2.10.6 by the transcription and is removed.
CHU_EN_FIXES = {
    (1, 9, "2"): [("the udîttha (Om", "the udgîtha (Om")],
    (2, 10, "6"): [(" Elventh Kha<em>nd</em>a.", "")],
    (3, 16, "2"): [("that I, the sacrifices may not perish", "that I, the sacrificer, may not perish")],
    (4, 6, "1"): [("drove the cows (toward the house", "drove the cows (towards the house")],
    (7, 25, "1"): [("it is indeed alt this", "it is indeed all this")],
}


def eng_chandogya_labeled(pr):
    """{khanda: [(label, text), ...]} with Müller's printed paragraph labels (e.g. '1', '1,2')."""
    out, kh, last_head, prev_n = {}, 0, None, 0
    for idx, (hs, n, t) in enumerate(ws_units(f"chandogya{pr}")):
        ks = [h for h in hs if h[1].startswith("KHANDA")]
        if not ks:
            continue
        head = ORD[ks[-1][0]]
        if head != last_head:
            kh, last_head = head, head
        elif n <= prev_n:
            kh += 1
        prev_n = n
        label = WS_LABELS[(f"chandogya{pr}", idx)]
        for a, b in CHU_EN_FIXES.get((pr, kh, label), []):
            assert t.count(a) == 1, (pr, kh, label, a)
            t = t.replace(a, b)
        out.setdefault(kh, []).append((label, t))
    return out


def eng_chandogya_raw(pr):
    """Müller's paragraphs keyed (khanda, n). A khanda heading missing from the transcription is detected by the
    paragraph number starting again at 1 (the khanda number is then advanced by one)."""
    out, kh, last_head, prev_n = {}, 0, None, 0
    for hs, n, t in ws_units(f"chandogya{pr}"):
        ks = [h for h in hs if h[1].startswith("KHANDA")]
        if not ks:
            continue
        head = ORD[ks[-1][0]]
        if head != last_head:
            kh, last_head = head, head
        elif n <= prev_n:
            kh += 1
        prev_n = n
        assert (kh, n) not in out, (pr, kh, n)
        out[(kh, n)] = t
    return out


def eng_mandukya():
    d = json.loads((SRC / "english" / "hume1921_mandukya.json").read_text(encoding="utf-8"))
    return {int(k): v for k, v in d["verses"].items()}


# --------------------------------------------------------------------------------------------
# Mapping (all readings checked on the images; see mapping_notes_869.txt)
# --------------------------------------------------------------------------------------------
# (chapter, first verse, last verse, pages, note)
ISA_MAP = [
    (None, 1, 9, ["f01v"],
     "fol. 1v (11 lines): after 'śrīgaṇeśāya namaḥ' and the invocation 'oṃ pūrṇam adaḥ ... oṃ śāntiḥ 3' (lines 1-2), "
     "verse 1 begins in line 2 ‹oṃ īśāvāsyam idaṃ sarvaṃ›; verse 9 ends in line 11 ‹ya u vidyāyāṃ ratāḥ›. "
     "The manuscript does not number the verses; each was found by reading its words on the image."),
    (None, 10, 18, ["f01v", "f02r"],
     "Verse 10 begins at the end of fol. 1v line 11 ‹anyad evāhu-› and goes on at fol. 2r line 1 ‹-r vidyayā›; "
     "verses 11-18 fill fol. 2r lines 1-10 (verse 18 ends ‹bhūyiṣṭhāṃ te nama uktiṃ vidhema›), followed in line 10 by "
     "a colophon beginning ‹iti yajurvedasaṃhitāyāṃ› and ending ‹'dhyāyaḥ›. The order of verses 9-14 on the page is "
     "the Kāṇva order printed here. Checked on the image."),
]

KATHA_MAP = {
    1: [(1, 2, ["f03v"], "fol. 3v line 11: after the Kena colophon and the invocation 'oṃ saha nāv avatu ... śāntiḥ 3', "
                         "verse 1 begins ‹uśan ha vai vājaśravasaḥ›; verse 2 ‹taṃ ha kumāraṃ santaṃ› in line 12. The manuscript "
                         "omits the closing words of verse 2, 'so 'manyata'."),
        (3, 13, ["f03v", "f04r"], "Verse 3 begins at the end of fol. 3v line 12 ‹pītodakā jagdhatṛṇā› and ends at fol. 4r line 1 "
                                  "‹nirindriyāḥ ... tā dadat›; verses 4-13 follow on fol. 4r to line 12 ‹etad dvitīyena vṛṇe vareṇa›."),
        (14, 24, ["f04r", "f04v"], "Verse 14 begins at the end of fol. 4r line 12 ‹pra te bravīmi› and ends at fol. 4v line 1 "
                                   "‹nihitaṃ guhāyām›; verses 15-24 follow on fol. 4v to line 13 ‹kāmabhājaṃ karomi›."),
        (25, 29, ["f04v", "f05r"], "Verse 25 begins at the end of fol. 4v line 13 ‹ye ye kāmā durlabhā› and ends at fol. 5r line 2 "
                                   "‹maraṇaṃ mānuprākṣīḥ›; verses 26-29 follow, and the red colophon ‹iti prathamādhyāye prathamavallī› "
                                   "stands in fol. 5r lines 6-7."),
        ],
    2: [(1, 5, ["f05r"], "fol. 5r line 7: after the colophon of the first vallī, verse 1 begins ‹anyac chreyo 'nyad utaiva preyaḥ›; "
                         "verse 5 ends in line 12 ‹andhenaiva nīyamānā yathāndhāḥ›."),
        (6, 16, ["f05r", "f05v"], "Verse 6 begins at the end of fol. 5r line 12 ‹na sāṃparāyaḥ› and ends at fol. 5v line 1 ‹-dyate me›; "
                                  "verses 7-16 follow on fol. 5v to line 12 ‹yo yad icchati tasya tat›."),
        (17, 25, ["f05v", "f06r"], "Verse 17 begins at the end of fol. 5v line 12 ‹etad ālambanam› and ends at fol. 6r line 1 "
                                   "‹brahmaloke mahīyate›; verses 18-25 follow, and the red colophon ‹iti prathamādhyāye dvitīyavallī› "
                                   "stands in fol. 6r lines 8-9."),
        ],
    3: [(1, 4, ["f06r"], "fol. 6r line 9: verse 1 begins ‹ṛtaṃ pibantau›; verse 4 ends in line 12 ‹bhoktety āhur manīṣiṇaḥ›."),
        (5, 17, ["f06r", "f06v"], "Verse 5 begins at the end of fol. 6r line 12 ‹yas tv avijñānavān bhavaty ayuktena› and ends at fol. 6v "
                                  "line 1 ‹sāratheḥ›; verses 6-17 follow on fol. 6v to line 12 ‹tad ānantyāya kalpata iti›, then the "
                                  "colophon ‹iti prathamādhyāye tṛtīyavallī›."),
        ],
    4: [(1, 12, ["f06v", "f07r"], "Verse 1 begins at the end of fol. 6v line 12 ‹parāñci› and ends at fol. 7r line 2 ‹amṛtatvam icchan›; "
                                  "verses 2-12 follow on fol. 7r to line 12 ‹etad vai tat›."),
        (13, 15, ["f07r", "f07v"], "Verse 13 begins at the end of fol. 7r line 12 ‹aṅguṣṭhamātraḥ puruṣo jyotir ivādhūmakaḥ› and ends at "
                                   "fol. 7v line 1 ‹sa evādya sa u śvaḥ etad vai tat›; verses 14-15 follow, and the colophon "
                                   "‹iti dvitīyādhyāye prathamavallī› stands in fol. 7v lines 2-3."),
        ],
    5: [(1, 10, ["f07v"], "fol. 7v line 3: verse 1 begins ‹puram ekādaśadvāram›; verse 10 ends in line 13 ‹pratirūpo bahiś ca›. "
                          "In verse 6 the word 'gautama' is added in the right margin."),
        (11, 15, ["f07v", "f08r"], "Verse 11 begins at the end of fol. 7v line 13 ‹sūryo yathā sarvalokasya cakṣuḥ› and ends at fol. 8r "
                                   "line 1 ‹bāhyadoṣaiḥ›; verses 12-15 follow, and the red colophon ‹dvitīyavallī› stands in fol. 8r line 6."),
        ],
    6: [(1, 8, ["f08r"], "fol. 8r line 6: verse 1 begins ‹ūrdhvamūlo 'vākśākhaḥ›; verse 8 ends in line 13 ‹amṛtatvaṃ ca gacchati›."),
        (9, 18, ["f08r", "f08v"], "Verse 9 begins at the end of fol. 8r line 13 ‹na saṃdṛśe tiṣṭhati rūpam› and ends at fol. 8v line 1 "
                                  "‹na cakṣuṣā paśyati›; verses 10-18 follow to line 10 ‹yo vid adhyātmam eva›, then a red colophon "
                                  "closing the Katha (‹iti dvitīya[...] samāptaḥ paramānanda›)."),
        ],
}

PRASNA_MAP = {
    1: [(1, 8, ["f08v", "f09r"], "Question 1, paragraph 1 begins at fol. 8v line 12 ‹oṃ sukeśā ca bhāradvājaḥ› (after the invocation "
                                 "'oṃ saha nāv avatu ... śāntiḥ' in line 11) and ends at fol. 9r line 1 ‹pippalādam upasannāḥ›; "
                                 "paragraphs 2-8 follow on fol. 9r to line 10 ‹udayaty eṣa sūryaḥ›."),
        (9, 16, ["f09r", "f09v"], "Paragraph 9 begins at fol. 9r line 10 ‹saṃvatsaro vai prajāpatiḥ› and ends at fol. 9v line 1 "
                                  "‹eṣa ha vai rayir yaḥ pitṛyāṇaḥ›; paragraphs 10-16 follow to line 9 ‹na māyā ceti›, marked ‹||1||›."),
        ],
    2: [(1, 2, ["f09v"], "fol. 9v lines 9-12: paragraph 1 begins ‹atha hainaṃ bhārgavo vaidarbhiḥ›; paragraph 2 ends in line 12 "
                         "‹vidhārayāmaḥ›."),
        (3, 13, ["f09v", "f10r"], "Paragraph 3 begins at fol. 9v line 12 ‹tān variṣṭhaḥ prāṇa uvāca› and ends at fol. 10r line 1 "
                                  "‹te 'śraddadhānā babhūvuḥ›; paragraphs 4-13 follow to line 12 ‹vidhehi na iti›. Verse 9 stands on fol. 10r "
                                  "lines 7-8 ‹indras tvaṃ prāṇa tejasā rudro 'si parirakṣitā› ... ‹jyotiṣāṃ patiḥ›; its Sanskrit is not "
                                  "shown here because the GRETIL e-text gives the commentary's paraphrase in place of the verse. The scribe then adds a "
                                  "short sentence ending ‹prāṇāyanam arhati› that is not in the edition, the number ‹||2||› and a red "
                                  "colophon ending ‹praśnopaniṣadi prathamo 'dhyāyaḥ› (lines 12-13)."),
        ],
    3: [(1, 12, ["f10r", "f10v"], "Paragraph 1 begins at fol. 10r line 13 ‹atha hainaṃ kausalyaś cāśvalāyanaḥ› and ends at fol. 10v "
                                  "line 2 ‹katham adhyātmam iti›; paragraphs 2-12 follow on fol. 10v to line 13 "
                                  "‹vijñāyāmṛtam aśnuta iti›, marked ‹||3||›."),
        ],
    4: [(1, 7, ["f10v", "f11r"], "Paragraph 1 begins at the end of fol. 10v line 13 ‹atha ha› and goes on at fol. 11r line 1 "
                                 "‹hainaṃ sauryāyaṇī gārgyaḥ›, ending in line 2; paragraphs 2-7 follow on fol. 11r to line 12 "
                                 "‹para ātmani saṃpratiṣṭhate›."),
        (8, 11, ["f11r", "f11v"], "Paragraph 8 begins at the end of fol. 11r line 12 ‹pṛthivī ca› and ends at fol. 11v line 5 "
                                  "‹prāṇaś ca vidhārayitavyaṃ ca›; paragraphs 9-11 follow to line 8 ‹sarvam evāviveśeti›, marked ‹||4||›, "
                                  "and the colophon ‹dvitīyo 'dhyāyaḥ›."),
        ],
    5: [(1, 3, ["f11v"], "fol. 11v line 8: paragraph 1 begins ‹atha hainaṃ śaibyaḥ satyakāmaḥ›; paragraph 3 ends in line 12 "
                         "‹mahimānam anubhavati›."),
        (4, 7, ["f11v", "f12r"], "Paragraph 4 begins at the end of fol. 11v line 12 ‹atha yadi dvimātreṇa› and ends at fol. 12r line 1 "
                                 "‹punar āvartate›; paragraphs 5-7 follow to line 6 ‹abhayaṃ paraṃ ceti›, marked ‹||5||›."),
        ],
    6: [(1, 4, ["f12r"], "fol. 12r line 6: paragraph 1 begins ‹atha hainaṃ sukeśā bhāradvājaḥ›; paragraph 4 ends in line 13 "
                         "‹lokeṣu ca nāma ca›."),
        (5, 8, ["f12r", "f12v"], "Paragraph 5 begins at fol. 12r line 13 ‹sa yathemā nadyaḥ syandamānāḥ› and ends at fol. 12v line 3 "
                                 "‹tad eṣa ślokaḥ›; paragraphs 6-8 follow to line 6 ‹namaḥ paramaṛṣibhyaḥ›, then the colophon "
                                 "‹iti śrī pippalādātharvaṇaśākhāyāṃ praśnopaniṣat samāptā ||6||› (lines 6-7)."),
        ],
}

AITAREYA_MAP = [  # (first verse, last verse, pages, note) -- item 1216
    ("1.1.1", "1.1.3", ["f01v"], "fol. 1v (7 lines): after 'śrīgaṇeśāya namaḥ' 1.1.1 begins in line 1 ‹oṃ ātmā vā idam eka "
                                 "evāgra āsīt›; 1.1.3 ends in line 5 ‹samuddhṛtyāmūrchayat›."),
    ("1.1.4", "1.2.2", ["f01v", "f02r"], "1.1.4 begins at fol. 1v line 5 ‹tam abhyatapat› and ends at fol. 2r line 4 ‹retasa "
                                         "āpaḥ ||1||›; 1.2.1 follows to line 7 ‹annam adāmeti›; 1.2.2 begins in line 7 "
                                         "‹tābhyo gām ānayat› and is completed in two lines added in the lower margin "
                                         "‹... na vai no 'yam alam iti›."),
    ("1.2.3", "1.2.4", ["f02v"], "fol. 2v line 1 ‹[tā]bhyaḥ puruṣam ānayat› (1.2.3) to line 6 ‹śiśnaṃ prāviśan› (end of 1.2.4)."),
    ("1.2.5", "1.3.3", ["f02v", "f03r"], "1.2.5 begins at fol. 2v line 6 ‹tam aśanāpipāse› and ends at fol. 3r line 2 "
                                         "‹bhavataḥ ||2||›; 1.3.1-1.3.3 follow to line 6 ‹haivānnam atrapsyat›."),
    ("1.3.4", "1.3.9", ["f03r", "f03v"], "1.3.4 begins at fol. 3r line 6 ‹tat prāṇenājighṛkṣat› and ends at fol. 3v line 1 "
                                         "‹atrapsyat›; 1.3.5-1.3.9 follow to line 7."),
    ("1.3.10", "1.3.11", ["f03v", "f04r"], "1.3.10 begins at the end of fol. 3v line 7 ‹tad apāne-› and ends at fol. 4r "
                                           "line 1 ‹yad vāyuḥ›; 1.3.11 follows to line 5 ‹atha ko 'ham iti›."),
    ("1.3.12", "1.3.14", ["f04r", "f04v"], "1.3.12 begins at fol. 4r line 5 ‹sa etam eva sīmānaṃ› and ends at fol. 4v "
                                           "line 1 ‹iti›; 1.3.13-1.3.14 follow to line 4 ‹parokṣapriyā iva hi devāḥ ||3||›. "
                                           "Some words in fol. 4v line 1 are covered in yellow (a scribal correction)."),
    ("2.1", "2.1", ["f04v"], "fol. 4v line 4: ‹apakrāmantu garbhiṇyaḥ› (Müller: 'Let the women who are with child move "
                             "away!'; not in the GRETIL text), then 2.1 ‹puruṣe ha vā ayam ādito garbho bhavati› to line 7 "
                             "‹tad asya prathamaṃ janma›."),
    ("2.2", "2.4", ["f04v", "f05r"], "2.2 begins at fol. 4v line 7 ‹tat striyā ātmabhūyaṃ gacchati› and ends at fol. 5r "
                                     "line 1 ‹bhāvayati›; 2.3-2.4 follow to line 6 ‹tad asya tṛtīyaṃ janma›."),
    ("2.5", "3.1", ["f05r", "f05v"], "2.5 begins at fol. 5r line 6 ‹tad uktam ṛṣiṇā› and ends at fol. 5v line 2 ‹vāmadeva "
                                     "evam uvāca›; 2.6 follows to line 4 ‹samabhavat samabhavat ||4||›; then ‹yathāsthānaṃ "
                                     "garbhiṇyaḥ› (Müller: 'Let the women go back to their place.'; not in the GRETIL text) "
                                     "and 3.1 ‹ko 'yam ātmeti› to line 6 ‹vijānāti›."),
    ("3.2", "3.2", ["f05v", "f06r"], "3.2 begins at fol. 5v line 6 ‹yad etad dhṛdayaṃ› and ends at fol. 6r line 2 "
                                     "‹nāmadheyāni bhavanti›."),
    ("3.3", "3.4", ["f06r", "f06v", "f07r"], "3.3 begins at fol. 6r line 2 ‹eṣa brahmaiṣa indra› and runs to line 7 ‹prajñā "
                                             "pratiṣṭhā›; fol. 6v lines 1-6 hold the opening of a Narayanopanisad copied by "
                                             "mistake and covered in yellow; 3.3 ends at fol. 6v line 6 ‹prajñānaṃ brahma›; "
                                             "3.4 runs from line 6 ‹sa etena prajñenātmanā› to fol. 7r line 1 ‹samabhavat "
                                             "samabhavat ||5||›, followed by the closing prayer and the colophon."),
]

CHANDOGYA6_MAP = [  # (khanda, first, last, pages, note) -- item 1213
    (1, 1, 4, ["f01v"], "fol. 1v (9 lines): after 'śrīgaṇeśāya namaḥ' and the invocation 'oṃ āpyāyantu mamāṅgāni ...' (lines 1-4), "
                        "paragraph 1 begins in line 4 ‹hariḥ oṃ śvetaketur hāruṇeya āsa›; paragraph 4 ends in line 9 ‹mṛttikety eva satyaṃ›."),
    (1, 5, 7, ["f01v", "f02r"], "Paragraph 5 begins at the end of fol. 1v line 9 ‹yathā somyaikena lohamaṇinā› and ends at fol. 2r line 1 "
                                "‹loham ity eva satyaṃ›; paragraphs 6-7 follow to line 4 ‹tathā somyeti hovāca›, marked ‹||1||›."),
    (2, 1, 3, ["f02r"], "fol. 2r lines 4-9: paragraph 1 begins ‹sad eva somyedam agra āsīt›; paragraph 3 ends ‹tad adhy āpo jāyante›. "
                        "Some words in line 7 are covered in yellow (a scribal deletion)."),
    (2, 4, 4, ["f02r", "f02v"], "Paragraph 4 begins at the end of fol. 2r line 9 ‹tā āpa aikṣanta› and ends at fol. 2v line 1 "
                                "‹annādyaṃ jāyate›, marked ‹||2||›."),
    (3, 1, 4, ["f02v"], "fol. 2v lines 1-6: paragraph 1 begins ‹teṣāṃ khalv eṣāṃ bhūtānāṃ›; paragraph 4 ends ‹tan me vijānīhīti›, "
                        "marked ‹||3||›."),
    (4, 1, 2, ["f02v"], "fol. 2v lines 6-9: paragraph 1 begins ‹yad agne rohitaṃ rūpaṃ›; paragraph 2 ends ‹trīṇi rūpāṇīty eva satyaṃ›."),
    (4, 3, 7, ["f02v", "f03r"], "Paragraph 3 begins at fol. 2v line 9 ‹yac candramaso rohitaṃ rūpaṃ› and ends at fol. 3r line 1 "
                                "‹trīṇi rūpāṇīty eva satyaṃ›; paragraphs 4-7 follow to line 8 ‹tan me vijānīhīti›, marked ‹||4||›."),
    (5, 1, 1, ["f03r"], "fol. 3r lines 8-9: ‹annam aśitaṃ tredhā vidhīyate› ... ‹yo 'ṇiṣṭhas tan manaḥ›."),
    (5, 2, 4, ["f03r", "f03v"], "Paragraph 2 begins at the end of fol. 3r line 9 ‹āpaḥ pītās tredhā vidhīyante› and ends at fol. 3v line 1 "
                                "‹sa prāṇaḥ›; paragraphs 3-4 follow to line 4 ‹tathā somyeti hovāca›, marked ‹||5||›."),
    (6, 1, 5, ["f03v"], "fol. 3v lines 4-8: paragraph 1 begins ‹dadhnaḥ somya mathyamānasya›; paragraph 5 ends ‹tathā somyeti hovāca›, "
                        "marked ‹||6||›."),
    (7, 1, 1, ["f03v"], "fol. 3v lines 8-10: ‹ṣoḍaśakalaḥ somya puruṣaḥ› ... ‹na pibato vicchetsyata iti›."),
    (7, 2, 6, ["f03v", "f04r"], "Paragraph 2 begins at the end of fol. 3v line 10 ‹sa ha pañcadaśāhāni nāśa› and ends at fol. 4r line 1 "
                                "‹na vai mā pratibhānti bho iti› (the words 'sa hovāca' are added in the top margin of fol. 4r); "
                                "paragraphs 3-6 follow to line 7 ‹vijajñāv iti vijajñāv iti›, marked ‹||7||›."),
    (8, 1, 5, ["f04r", "f04v"], "Paragraph 1 begins at fol. 4r line 8 ‹uddālako hāruṇiḥ śvetaketuṃ putram uvāca› and ends at fol. 4v "
                                "line 1 ‹apīto bhavati›; paragraphs 2-5 follow to line 10 ‹nedam amūlaṃ bhaviṣyatīti›."),
    (8, 6, 7, ["f04v", "f05r"], "Paragraph 6 begins at the end of fol. 4v line 10 ‹tasya kva mūlaṃ syād anyatrādbhyaḥ› and ends at fol. 5r "
                                "line 3 ‹parasyāṃ devatāyāṃ› (words left out in fol. 5r line 1 are supplied in the top margin); "
                                "paragraph 7 follows to line 4, marked ‹||8||›."),
    (9, 1, 3, ["f05r"], "fol. 5r lines 4-8: paragraph 1 begins ‹yathā somya madhu madhukṛtaḥ›; paragraph 3 ends "
                        "‹yad yad bhavanti tad ābhavanti›."),
    (9, 4, 4, ["f05r", "f05v"], "Paragraph 4 begins at fol. 5r line 8 ‹sa ya eṣo 'ṇimaitadātmyam› and ends at fol. 5v line 1 "
                                "‹tathā somyeti hovāca›, marked ‹||9||›."),
    (10, 1, 3, ["f05v"], "fol. 5v lines 1-6: paragraph 1 begins ‹imāḥ somya nadyaḥ›; paragraph 3 ends ‹tathā somyeti hovāca›, "
                         "marked ‹||10||›."),
    (11, 1, 2, ["f05v"], "fol. 5v lines 6-9: paragraph 1 begins ‹asya somya mahato vṛkṣasya›; paragraph 2 ends ‹sarvaḥ śuṣyati›. "
                         "Müller ends his paragraph 2 with 'In exactly the same manner, my son, know this. Thus he spoke', which "
                         "renders the opening words of Sanskrit paragraph 3 (‹evam eva khalu somya viddhīti hovāca›, line 9)."),
    (11, 3, 3, ["f05v", "f06r"], "Paragraph 3 begins at the end of fol. 5v line 9 ‹evam eva khalu somya viddhīti› and ends at fol. 6r "
                                 "line 3 ‹tathā somyeti hovāca›, marked ‹||11||›."),
    (12, 1, 3, ["f06r"], "fol. 6r lines 3-8: paragraph 1 begins ‹nyagrodhaphalam ata āhareti›; paragraph 3 ends ‹tathā somyeti hovāca›, "
                         "marked ‹||12||›."),
    (13, 1, 3, ["f06r", "f06v"], "Paragraph 1 begins at fol. 6r line 8 ‹lavaṇam etad udake 'vadhāya› and ends at fol. 6v line 1 "
                                 "‹na viveda›; paragraphs 2-3 follow to line 6 ‹tathā somyeti hovāca›, marked ‹||13||›."),
    (14, 1, 1, ["f06v"], "fol. 6v lines 6-8: ‹yathā somya puruṣaṃ gandhārebhyaḥ› ... ‹abhinaddhākṣo visṛṣṭaḥ›."),
    (14, 2, 3, ["f06v", "f07r"], "Paragraph 2 begins at fol. 6v line 8 ‹tasya yathābhinahanaṃ› (the word 'pramucya' is added below the "
                                 "text) and ends at fol. 7r line 1 ‹saṃpatsya iti›; paragraph 3 follows to line 2, marked ‹||14||›."),
    (15, 1, 3, ["f07r"], "fol. 7r lines 3-7: paragraph 1 begins ‹puruṣaṃ somyotopatāpinaṃ›; paragraph 3 ends ‹tathā somyeti hovāca›, "
                         "marked ‹||15||›. Müller numbers this khanda in two paragraphs; his 2 covers Sanskrit 2 and 3."),
    (16, 1, 1, ["f07r"], "fol. 7r lines 7-9: ‹puruṣaṃ somyota hastagṛhītam ānayanti› ... ‹atha hanyate›."),
    (16, 2, 3, ["f07r", "f07v"], "Paragraph 2 begins at the end of fol. 7r line 9 ‹atha yadi tasyākartā bhavati› and ends at fol. 7v "
                                 "line 2 ‹atha mucyate›; paragraph 3 follows to line 3 ‹vijajñāv iti vijajñāv iti›, marked ‹||16||›, "
                                 "then the colophon ‹iti chāndogye ṣaṣṭhaḥ prapāṭhakaḥ› and a dated colophon (śaka 1758). "
                                 "Müller's paragraph 2 covers Sanskrit 2 and 3."),
]

MANDUKYA_MAP = [
    (None, 1, 8, ["f16r"], "fol. 16r (11 lines): after the invocations 'oṃ bhadraṃ karṇebhiḥ ...' and 'svasti na indro ...' "
                           "(abbreviated) and 'oṃ śāntiḥ', paragraph 1 begins in line 1 ‹om ity etad akṣaram›; paragraph 8 ends in "
                           "line 11 ‹akāra ukāro makāra iti›."),
    (None, 9, 12, ["f16r", "f16v"], "Paragraph 9 begins at fol. 16r line 11 ‹jāgaritasthāno vaiśvānaro 'kāraḥ› and ends at fol. 16v "
                                    "line 1 ‹ādiś ca bhavati ya evaṃ veda›; paragraphs 10-12 follow to line 5 "
                                    "‹ātmanātmānaṃ ya evaṃ veda›, then the colophon ‹iti māṇḍūkyopaniṣat samāptā paramānanda›."),
]


# --------------------------------------------------------------------------------------------
def sup_join(pairs):
    return "<br>".join(f"<sup>{n}</sup>{t}" for n, t in pairs)


def build_section(sid, ref, sa, en, pages, note, extra="", item="869"):
    pages_txt = ", ".join("fol. " + p[1:3].lstrip("0") + p[3] for p in pages)
    return {
        "section": sid,
        "original_ref": ref,
        "original_text": sa,
        "text": en,
        "scan_pages": [scan(p, item) for p in pages],
        "scan_note": f"{ITEMS[item]['name']}, {pages_txt}. {note}{extra} Checked on the image; readings logged in "
                     f"{ITEMS[item]['notes']}.",
    }


def entry_json(tid, title, description, intro, notes, sections, sa_src, sa_lic, en_src, en_lic, translator, mapping_urls,
               item="869"):
    cfg = ITEMS[item]
    pages = []
    for s in sections:
        for p in s["scan_pages"]:
            if p not in pages:
                pages.append(p)
    return {
        "id": tid, "slug": tid, "title": title,
        "language": "Sanskrit (IAST) / English",
        "source": f"{cfg['name']} (OPenn, public domain) + GRETIL Sanskrit + {translator} English",
        "description": description,
        "introduction": intro,
        "translator_notes": notes,
        "translation": sections,
        "verification": {
            "scan_source": f"University of Pennsylvania Libraries, OPenn: {cfg['url']}",
            "scan_license": SCAN_LICENSE.replace("Item 869", f"Item {item}"),
            "scan_manuscript": {"869": MS_DESC, "1213": MS_DESC_1213, "945": MS_DESC_945, "1216": MS_DESC_1216}[item],
            "scan_mapping": "Each section was located by reading the manuscript page images (the manuscript has no verse "
                            "numbers; verses were identified by their words, chapter ends by the scribe's colophons and "
                            "numbers). Line-level readings are recorded in each scan_note and in "
                            f"{cfg['notes']}.",
            "scan_mapping_urls": mapping_urls,
            "scan_local_paths": pages,
            "original_text_source": sa_src,
            "original_text_license": sa_lic,
            "translation_source": en_src,
            "translation_license": en_lic,
            "translator": translator,
            "verified_date": TODAY,
        },
    }


# --------------------------------------------------------------------------------------------
# Chandogya 1-5, 7, 8 on Item 945
# --------------------------------------------------------------------------------------------
CHU_TITLES = {
    1: "the udgitha and the syllable Om",
    2: "the Saman, fivefold and sevenfold",
    3: "the honey of the gods; Sandilya; Ghora Angirasa",
    4: "Raikva; Satyakama Jabala; Upakosala",
    5: "the breath; the five fires; Asvapati and the universal self",
    7: "Narada and Sanatkumara: the infinite (bhuman)",
    8: "the space in the heart; Indra and Virocana",
}
CHU_SUMMARY = {
    1: "It opens the Upanishad with meditations on the udgitha, the chanted portion of a Saman, identified with the "
       "syllable Om. It tells how the gods used the udgitha against the demons, how the priests Silaka, Caikitayana "
       "and the king Pravahana Jaivali debated the support of the Saman, how the impoverished Usasti Cakrayana "
       "challenged the priests at a royal sacrifice, and closes with the 'udgitha of the dogs' and the stobha syllables.",
    2: "It treats the Saman as a whole: the fivefold and sevenfold Saman meditated on in the worlds, the rain, the "
       "waters, the seasons, the animals and the breaths, the Samans woven into the world (2.11-21), the 'three "
       "branches of law' (2.23) and the rites that win the worlds of the three daily soma pressings (2.24).",
    3: "It contains the meditation on the sun as the honey of the gods (3.1-11), the Gayatri (3.12), the doors of the "
       "heart (3.13), Sandilya's teaching that 'all this is Brahman' and the self within the heart is smaller than a "
       "grain and greater than the worlds (3.14), the universe as a chest (3.15), man as a sacrifice (3.16), Ghora "
       "Angirasa's teaching to Krishna son of Devaki (3.17), mind and space as Brahman (3.18) and the world egg (3.19).",
    4: "It tells of King Janasruti and Raikva 'with the cart' who teaches that wind and breath are the gatherers "
       "(4.1-3), of Satyakama Jabala, accepted as a student for his truthfulness and taught by a bull, the fire, a "
       "swan and a diver bird (4.4-9), of Upakosala taught by his teacher's sacred fires (4.10-15), and of the "
       "Brahman priest who mends the sacrifice (4.16-17).",
    5: "It tells of the dispute of the senses and the breath (5.1-2), of Svetaketu and King Pravahana Jaivali on the "
       "five fires and the paths of the dead (5.3-10), and of King Asvapati Kaikeya teaching six learned householders "
       "the universal self, Vaisvanara, and the offering to the breaths (5.11-24).",
    7: "Narada, learned in all the Vedas and sciences, comes to Sanatkumara for help against sorrow. Sanatkumara leads "
       "him step by step from name, speech and mind up to breath and to the infinite (bhuman), which is happiness: "
       "'where one sees nothing else, hears nothing else, knows nothing else, that is the infinite'.",
    8: "It teaches the small space within the heart, the 'city of Brahman' that holds heaven and earth (8.1-6), and "
       "tells how the god Indra and the demon Virocana lived as students with Prajapati to learn the self that is free "
       "from evil, age and death; Virocana leaves with the teaching that the body is the self, Indra returns three times "
       "(8.7-12). It closes with verses on the way to Brahman (8.13-15).",
}


def chu_order(pr):
    return 15 + pr


def chandogya_sections(pr, sa, en_lab, pages):
    """Build sections for one prapathaka from the page table (mapping_945.json).
    A paragraph belongs to every page whose span covers it; a section holds the paragraphs that end on one page
    (with all pages they occupy). Khandas whose paragraph division in Müller differs from the Sanskrit are kept whole
    in one section."""
    paras = sorted(sa)
    pos = {k: i for i, k in enumerate(paras)}
    omitted = set()
    for pg in pages:
        if pg.get("omits"):
            a, b = [tuple(x) for x in pg["omits"]]
            omitted |= {k for k in paras if pos[a] <= pos[k] <= pos[b]}
    on_pages = {k: [] for k in paras}
    for i, pg in enumerate(pages):
        a, b = pos[tuple(pg["start"])], pos[tuple(pg["end"])]
        for k in paras[a:b + 1]:
            if k not in omitted:
                on_pages[k].append(i)
    missing = [k for k in paras if not on_pages[k] and k not in omitted]
    assert not missing, (pr, missing)
    mism = set()
    for k in sorted({x[0] for x in paras}):
        n = max(v for kk, v in paras if kk == k)
        if [l for l, _ in en_lab.get(k, [])] != [str(v) for v in range(1, n + 1)]:
            mism.add(k)
    groups = {}
    for k in paras:
        if k in omitted:
            continue
        groups.setdefault(on_pages[k][-1], []).append(k)
    seq = [groups[i] for i in sorted(groups)]
    # merge groups so that a mismatched khanda stays in one section
    merged = []
    for g in seq:
        g_mism = {k[0] for k in g if k[0] in mism}
        if merged and g_mism & {k[0] for k in merged[-1]}:
            merged[-1] = merged[-1] + g
        else:
            merged.append(g)
    out = []
    for g in merged:
        pg_idx = sorted({i for k in g for i in on_pages[k]})
        (k1, v1), (k2, v2) = g[0], g[-1]
        sid = f"{pr}.{k1}.{v1}" if (k1, v1) == (k2, v2) else (
            f"{pr}.{k1}.{v1}-{v2}" if k1 == k2 else f"{pr}.{k1}.{v1}-{k2}.{v2}")
        sa_html = "<br>".join(f"<sup>{k}.{v}</sup>{sa[(k, v)]}" for k, v in g)
        en_parts, done = [], set()
        for k, v in g:
            if k in mism:
                if k in done:
                    continue
                done.add(k)
                en_parts += [f"<sup>{k}.{l}</sup>{t}" for l, t in en_lab[k]]
            else:
                en_parts.append(f"<sup>{k}.{v}</sup>{en_lab[k][v - 1][1]}")
        notes = []
        for i in pg_idx:
            pg = pages[i]
            fol = pg["page"]
            notes.append(f"fol. {fol[1:3].lstrip('0')}{fol[3]} begins ‹{pg['first_words']}› and ends ‹{pg['last_words']}›")
        extra = [pages[i]["note"] for i in pg_idx if pages[i].get("note")]
        sec_om = sorted(k for k in omitted if pos[g[0]] <= pos[k] <= pos[g[-1]])
        if sec_om:
            extra.append(f"Paragraphs {pr}.{sec_om[0][0]}.{sec_om[0][1]}-{sec_om[-1][1]} are not in this manuscript and are "
                         "not shown")
        mk = sorted({k for k, _ in g if k in mism})
        if mk:
            extra.append("Müller divides khanda " + ", ".join(f"{pr}.{k}" for k in mk) + " into paragraphs differently "
                         "from the Sanskrit edition; the whole khanda is given here with his own numbers")
        note = "; ".join(notes) + " (first and last words read on the image, transliterated). " + \
               ("Notes: " + ". ".join(extra) + ". " if extra else "")
        out.append({
            "section": sid,
            "original_ref": f"Chāndogya Upaniṣad {sid}",
            "original_text": sa_html,
            "text": "<br>".join(en_parts),
            "scan_pages": [scan(pages[i]["page"], "945") for i in pg_idx],
            "scan_note": f"{ITEMS['945']['name']}. {note}The words were located in the GRETIL text by string matching "
                         "and the page boundaries follow from them; readings and results are stored in "
                         "data/sources/upanishads/mapping_945.json.",
        })
    return out, sorted(omitted)


MS_INTRO = (
    "<p>The page images come from a single paper manuscript in the University of Pennsylvania Libraries, "
    "Ms. Coll. 390 Item 869, catalogued as 'Six early upanisads'. It has 16 leaves (13 x 27 cm) written in Devanagari, "
    "11 to 13 lines to a side, and is undated (the library assigns it to the 18th or 19th century). It contains the "
    "Isa, Kena, Katha, Prasna, Mundaka and Mandukya Upanisads in that order; its title page names a set of ten. "
    "Leaves are numbered in the right margin of each verso and carry abbreviated titles in the upper left margin.</p>"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tif-dir", action="append", default=[], help="directory with OPenn TIFFs (repeatable)")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    make_scans(args.tif_dir, args.force)
    PUB_DIR.mkdir(parents=True, exist_ok=True)

    gretil_lic = "CC BY-NC-SA 4.0 (GRETIL, SUB Göttingen)"
    mapping_urls = [OPENN_ITEM, "https://openn.library.upenn.edu/Data/0002/mscoll390_item869/data/mscoll390_item869_TEI.xml"]
    rows, entries = [], []

    # ---------------- Isa ----------------
    sa, en = load_isa(), eng_isa()
    secs = []
    for _, a, b, pages, note in ISA_MAP:
        vs = range(a, b + 1)
        secs.append(build_section(f"{a}-{b}", f"Īśā Upaniṣad {a}-{b} (Kāṇva recension)",
                                  sup_join((v, sa[v]) for v in vs), sup_join((v, en[v]) for v in vs), pages, note))
    tid = PREFIX + "isa"
    entries.append((tid, entry_json(
        tid, "Isa Upanishad (Isavasya)",
        "The Isa (Isavasya) Upanishad, the closing chapter of the White Yajurveda Samhita, in Sanskrit and Max Müller's "
        "English, on two pages of a Sanskrit manuscript in the University of Pennsylvania.",
        "<p>The Isa or Isavasya Upanishad is the fortieth and last chapter of the Vajasaneyi Samhita of the White "
        "Yajurveda. Its eighteen verses open with the line that gives the text its name, 'All this is to be hidden in the "
        "Lord'. The Sanskrit here is the Kanva recension, the version commented on by Samkara, which matches the order of "
        "verses in the manuscript; the Madhyandina recension orders verses 9-14 differently.</p>"
        + MS_INTRO +
        "<p>The Isa occupies fol. 1v and 2r. The manuscript ends it with a colophon that names it as a chapter of the "
        "Yajurveda Samhita. Verses 1-9 stand on fol. 1v and verses 10-18 on fol. 2r.</p>",
        ["Sanskrit: GRETIL, Isopanisad (Kanva recension) with the commentary ascribed to Samkara, mula text only; input by the "
         "Sansknet project, checked by GRETIL against Limaye and Vadekar, Eighteen Principal Upanisads (1958).",
         "English: F. Max Müller, 'Vagasaneyi-samhita-upanishad', The Upanishads part I, Sacred Books of the East 1 (1879), "
         "from the proofread English Wikisource transcription; Müller's footnotes are not reproduced. Italic letters in "
         "Müller's spellings of Sanskrit names follow the printed book.",
         "The invocation 'oṃ pūrṇam adaḥ ...' written before verse 1 on fol. 1v is not translated by Müller and is not shown."],
        secs,
        GRETIL + "sa_IzopaniSad-or-IzAvAsyopaniSadkANva-recension-comm.xml", gretil_lic,
        f"F. Max Müller, The Upanishads I, SBE 1 (Oxford, 1879), {WS}{WS_PAGES['isa'].replace(' ', '_')}",
        "public domain (1879); Wikisource transcription CC BY-SA 4.0", "F. Max Müller (1879)", mapping_urls)))
    rows.append((tid, "Isa Upanishad (Isavasya)", 1, "isa", "Isa Upanishad, 18 verses (Kanva recension)"))

    # ---------------- Katha ----------------
    sa, en = load_katha(), eng_katha()
    vnames = {1: ("I", 1), 2: ("I", 2), 3: ("I", 3), 4: ("II", 1), 5: ("II", 2), 6: ("II", 3)}
    for v in range(1, 7):
        adh, val = vnames[v]
        secs = []
        for a, b, pages, note in KATHA_MAP[v]:
            vs = range(a, b + 1)
            ad_n = 1 if adh == "I" else 2
            secs.append(build_section(f"{ad_n}.{val}.{a}-{b}", f"Kaṭha Upaniṣad {ad_n}.{val}.{a}-{b} (vallī {v})",
                                      sup_join((x, sa[(v, x)]) for x in vs), sup_join((x, en[(v, x)]) for x in vs), pages, note))
        tid = PREFIX + f"katha-{v}"
        title = f"Katha Upanishad, Adhyaya {adh}, Valli {val}"
        intro = (
            f"<p>The Katha Upanishad belongs to the Black Yajurveda. It tells how the boy Naciketas, given to Death by his "
            f"father, waits three nights at Death's house and is granted three wishes; the third, to know what happens to a "
            f"man after death, leads to Death's teaching on the Self. The text has two adhyayas of three vallis each. This "
            f"entry gives valli {v} of 6 (adhyaya {adh}, valli {val}).</p>" + MS_INTRO +
            "<p>The Katha runs from fol. 3v to fol. 8v of the manuscript. The scribe closes each valli with a colophon "
            "(for example 'iti prathamādhyāye prathamavallī'), which makes the valli boundaries visible on the pages. "
            "Each section below holds the verses that end on one page; a verse that begins at the foot of the previous "
            "page is shown with both pages.</p>")
        entries.append((tid, entry_json(
            tid, title,
            f"Katha Upanishad {adh}.{val} (valli {v} of 6) in Sanskrit and Max Müller's English, mapped verse by verse to the "
            f"pages of an 18th or 19th century Sanskrit manuscript at the University of Pennsylvania.",
            intro,
            ["Sanskrit: GRETIL, Kathopanisad, input by the Vienna University student team after P. Olivelle, The Early "
             "Upanisads (1998). Verse numbers follow the edition; the manuscript has none.",
             "English: F. Max Müller, 'Katha-upanishad', The Upanishads part II, Sacred Books of the East 15 (1884), from the "
             "proofread English Wikisource transcription. Müller numbers the vallis of the second adhyaya IV-VI; his verse "
             "numbers agree with the Sanskrit. Footnotes are not reproduced.",
             "Four slips in the Wikisource transcription are corrected to the printed page (SBE 15 pp. 4, 11, 13, 23): "
             "I.1.13 'fire-sacrificef', I.2.23 'can be can gained', I.3.13 'whichs', II.3.15 'Whean'. The transcription "
             "also numbers I.3.15-17 as 18-20; the book has 15-17.",
             "Müller ends the sixth valli with a 19th paragraph, the closing prayer 'May He protect us both!' "
             "(saha nāv avatu). It is not part of the edited Sanskrit text and is not shown; in the manuscript this prayer "
             "stands on fol. 8v line 11 as the opening invocation of the Prasna."],
            secs,
            GRETIL + "sa_kathopaniSad.xml", gretil_lic,
            f"F. Max Müller, The Upanishads II, SBE 15 (Oxford, 1884), {WS}{WS_PAGES['katha'].replace(' ', '_')}",
            "public domain (1884); Wikisource transcription CC BY-SA 4.0", "F. Max Müller (1884)", mapping_urls)))
        rows.append((tid, title, 1 + v, "katha", f"Katha Upanishad {adh}.{val}"))

    # ---------------- Prasna ----------------
    sa, en = load_prasna(), eng_prasna()
    asker = {1: "Kabandhin Katyayana", 2: "Bhargava Vaidarbhi", 3: "Kausalya Asvalayana",
             4: "Sauryayanin Gargya", 5: "Saibya Satyakama", 6: "Sukesas Bharadvaja"}
    for q in range(1, 7):
        secs = []
        for a, b, pages, note in PRASNA_MAP[q]:
            vs = range(a, b + 1)
            secs.append(build_section(f"{q}.{a}-{b}", f"Praśna Upaniṣad {q}.{a}-{b}",
                                      sup_join((x, sa[(q, x)]) for x in vs), sup_join((x, en[(q, x)]) for x in vs), pages, note))
        tid = PREFIX + f"prasna-{q}"
        title = f"Prasna Upanishad, Question {q}"
        intro = (
            "<p>The Prasna ('Question') Upanishad belongs to the Atharvaveda (Paippalada school). Six students come to the "
            "sage Pippalada, and after a year of discipline each asks one question: on the origin of creatures, the powers "
            "that sustain the body, the breath, sleep and dreaming, meditation on the syllable Om, and the person of "
            f"sixteen parts. This entry gives question {q}, asked by {asker[q]}.</p>" + MS_INTRO +
            "<p>The Prasna runs from fol. 8v to fol. 12v. The scribe numbers the end of each question (||1|| to ||6||) and "
            "groups the questions in pairs as three adhyayas. Each section below holds the paragraphs that end on one page; "
            "a paragraph that begins on the previous page is shown with both pages.</p>")
        entries.append((tid, entry_json(
            tid, title,
            f"Prasna Upanishad, question {q} of 6, in Sanskrit and Max Müller's English, mapped to the pages of an 18th or "
            f"19th century Sanskrit manuscript at the University of Pennsylvania.",
            intro,
            ["Sanskrit: GRETIL, Prasnopanisad with the commentary ascribed to Samkara, mula text only; input by the Sansknet "
             "project. Paragraph numbers follow the edition; the manuscript has none.",
             "Prasna 2.9: the GRETIL file (TEI and legacy mula file alike) prints Samkara's paraphrase in place of this verse, "
             "so its Sanskrit is left out and marked [...]; the verse itself can be read on fol. 10r lines 7-8 of the manuscript.",
             "English: F. Max Müller, 'Prasña-upanishad', The Upanishads part II, Sacred Books of the East 15 (1884), from the "
             "proofread English Wikisource transcription. Footnotes are not reproduced."],
            secs,
            GRETIL + "sa_praznopaniSad-comm.xml", gretil_lic,
            f"F. Max Müller, The Upanishads II, SBE 15 (Oxford, 1884), {WS}{WS_PAGES['prasna'].replace(' ', '_')}",
            "public domain (1884); Wikisource transcription CC BY-SA 4.0", "F. Max Müller (1884)", mapping_urls)))
        rows.append((tid, title, 7 + q, "prasna", f"Prasna Upanishad, question {q}"))

    # ---------------- Chandogya 6 (item 1213) ----------------
    sa, en = load_chandogya6(), eng_chandogya6()
    secs = []
    for k, a, b, pages, note in CHANDOGYA6_MAP:
        vs = list(range(a, b + 1))
        sa_html = sup_join((v, sa[(k, v)]) for v in vs)
        en_pairs = []
        for v in vs:
            if k in (15, 16) and v == 3:
                continue                        # Müller's paragraph 2 covers the edition's 2 and 3
            label = "2-3" if (k in (15, 16) and v == 2) else v
            en_pairs.append((label, en[(k, v)]))
        sid = f"6.{k}.{a}" if a == b else f"6.{k}.{a}-{b}"
        secs.append(build_section(sid, f"Chāndogya Upaniṣad {sid}", sa_html, sup_join(en_pairs), pages, note, item="1213"))
    tid = PREFIX + "chandogya-6"
    m1213 = ["https://openn.library.upenn.edu/Data/0002/html/mscoll390_item1213.html",
             "https://openn.library.upenn.edu/Data/0002/mscoll390_item1213/data/mscoll390_item1213_TEI.xml"]
    entries.append((tid, entry_json(
        tid, "Chandogya Upanishad, Prapathaka 6 (Tat tvam asi)",
        "The sixth chapter of the Chandogya Upanishad, Uddalaka's teaching to his son Svetaketu ending 'thou art that' "
        "(tat tvam asi), in Sanskrit and Max Müller's English, mapped to a Sanskrit manuscript copied in 1836.",
        "<p>The Chandogya Upanishad belongs to the Samaveda. Its sixth chapter (prapathaka) is a dialogue between the "
        "teacher Uddalaka Aruni and his son Svetaketu, who returns home proud of his learning after twelve years of study. "
        "Through a series of examples (clay and its products, honey gathered from many trees, rivers merging in the sea, "
        "the seed of the banyan, salt dissolved in water) the father teaches that all things come from Being (sat), and "
        "closes each lesson with the words 'that is the Self; thou art that, Svetaketu' (tat tvam asi). The chapter has "
        "sixteen khandas.</p>"
        "<p>The page images come from University of Pennsylvania Libraries, Ms. Coll. 390 Item 1213, a paper manuscript of "
        "seven leaves (11 x 24 cm) that holds the sixth prapathaka alone, in Devanagari with red accent marks, 9 to 10 "
        "lines to a side. Its colophon on fol. 7v is dated saka 1758 (1836 CE). The scribe marks the end of each khanda "
        "with its number (||1|| to ||16||) but does not number paragraphs; paragraphs were located by their words. Each "
        "section below holds the paragraphs of one khanda that end on one page; a paragraph that begins on the previous "
        "page is shown with both pages.</p>",
        ["Sanskrit: GRETIL, Chandogyopanisad with the commentary ascribed to Samkara, mula text only; input by the Sansknet "
         "project. In 6.13.2 a legacy encoding artifact ('an;gāsyāntād') is shown as aṅgāsyāntād. Paragraph 6.2.4 is "
         "entered in GRETIL without word division; it is shown as given.",
         "English: F. Max Müller, 'Khandogya-upanishad, Sixth Prapathaka', The Upanishads part I, Sacred Books of the East 1 "
         "(1879), from the proofread English Wikisource transcription; footnotes are not reproduced. One transcription slip "
         "is corrected to the printed page (6.11.2 'leaves at second' for 'leaves a second').",
         "Müller divides khandas 15 and 16 into two paragraphs each; his second paragraph covers Sanskrit paragraphs 2 and 3 "
         "and is numbered 2-3 here. Elsewhere his paragraph breaks fall in a few places a clause earlier or later than the "
         "Sanskrit numbering (6.7.3-5, 6.11.2-3, 6.12.2-3, 6.13.1-2); each such case lies inside one section except 6.11, "
         "explained in its scan note."],
        secs,
        GRETIL + "sa_chAndogyopaniSad-comm.xml", gretil_lic,
        f"F. Max Müller, The Upanishads I, SBE 1 (Oxford, 1879), {WS}{WS_PAGES['chandogya6'].replace(' ', '_')}",
        "public domain (1879); Wikisource transcription CC BY-SA 4.0", "F. Max Müller (1879)", m1213, item="1213")))
    rows.append((tid, "Chandogya Upanishad, Prapathaka 6 (Tat tvam asi)", chu_order(6), "chandogya", "Chandogya Upanishad 6"))

    # ---------------- Aitareya (item 1216) ----------------
    sa = load_aitareya()
    mu = json.loads((SRC / "english" / "muller1879_aitareya.json").read_text(encoding="utf-8"))
    en = dict(mu["verses"])
    en["1.1.1"] = mu["preface_1.1.1"] + "<br>" + en["1.1.1"]
    en["2.1"] = mu["pre_2.1"] + "<br>" + en["2.1"]
    en["3.1"] = mu["pre_3.1"] + "<br>" + en["3.1"]
    order_ait = list(sa)
    secs = []
    for a, b, pages, note in AITAREYA_MAP:
        vs = order_ait[order_ait.index(a):order_ait.index(b) + 1]
        sid = a if a == b else f"{a}-{b}"
        secs.append(build_section(sid, f"Aitareya Upaniṣad {sid}", sup_join((v, sa[v]) for v in vs),
                                  sup_join((v, en[v]) for v in vs), pages, note, item="1216"))
    tid = PREFIX + "aitareya"
    m1216 = ["https://openn.library.upenn.edu/Data/0002/html/mscoll390_item1216.html",
             "https://openn.library.upenn.edu/Data/0002/mscoll390_item1216/data/mscoll390_item1216_TEI.xml"]
    entries.append((tid, entry_json(
        tid, "Aitareya Upanishad",
        "The Aitareya Upanishad of the Rigveda, on the Self that created the worlds and entered the body, ending 'knowledge "
        "is Brahman', in Sanskrit and Max Müller's English, mapped to the pages of a Sanskrit manuscript at the University "
        "of Pennsylvania.",
        "<p>The Aitareya Upanishad belongs to the Rigveda and forms chapters 4-6 of the second book of the Aitareya "
        "Aranyaka. It tells how the Self, alone in the beginning, sent forth the worlds and a cosmic person, from whose "
        "body the senses and their gods came forth; how the gods were given a place in man; how the Self entered the body "
        "through the suture of the skull; and, in its last chapter, identifies the Self with knowledge (prajnana): "
        "'knowledge is Brahman'. Its second chapter speaks of the three births of a man.</p>"
        "<p>The page images come from University of Pennsylvania Libraries, Ms. Coll. 390 Item 1216, a paper manuscript of "
        "seven leaves (10 x 24 cm) written in Devanagari with red accent marks, 7 lines to a side, undated (catalogued 18th "
        "or 19th century). The scribe numbers the khandas continuously from 1 to 5 and closes with a colophon naming the "
        "text as the Aitareyopanisad of the Asvalayana school of the Rigveda. On fol. 6v he began to copy the next text, "
        "a Narayanopanisad, by mistake, then covered those six lines in yellow and finished the Aitareya.</p>"
        "<p>The verse division is Samkara's (1.1.1-3.4), which Müller marks with numbers in parentheses. Each section "
        "below holds the verses that end on one page, with the pages they occupy.</p>",
        ["Sanskrit: GRETIL, Aitareyopanisad with the commentary ascribed to Samkara, mula text only (input by the Sansknet "
         "project).",
         "English: F. Max Müller, The Upanishads part I, Sacred Books of the East 1 (1879), Aitareya-aranyaka II.4-6, "
         "pp. 237-246, transcribed for this edition from the page images of the 1879 printing (Wikimedia Commons scan of "
         "SBE vol. 1) with the archive.org OCR as a draft. Müller's paragraph numbers (after Sayana) and footnotes are left "
         "out; his parenthesized numbers for Samkara's divisions give the verse division used here. Müller places the "
         "words 'And this has been declared by a Rishi' at the end of 2.4; the Sanskrit edition begins 2.5 with them.",
         "Müller's opening 'Adoration to the Highest Self. Hari, Om!' and his sentences 'Let the women who are with child "
         "move away!' (before 2.1) and 'Let the women go back to their place.' (before 3.1) translate words that stand in "
         "this manuscript ('apakrāmantu garbhiṇyaḥ', fol. 4v line 4; 'yathāsthānaṃ garbhiṇyaḥ', fol. 5v line 4) but not "
         "in the GRETIL text, so the English has them while the Sanskrit shown does not.",
         "Müller's seventh adhyaya, the closing prayer 'My speech rests in the mind' (vāṅ me manasi), is written in the "
         "manuscript on fol. 7r but is not part of the GRETIL text and is not shown."],
        secs,
        GRETIL + "sa_aitareyopaniSad-comm.xml", gretil_lic,
        "F. Max Müller, The Upanishads I, SBE 1 (Oxford, 1879), pp. 237-246, transcribed from the page images: "
        "https://commons.wikimedia.org/wiki/File:Sacred_Books_of_the_East_-_Volume_1.djvu (pages 351-360)",
        "public domain (1879)", "F. Max Müller (1879)", m1216, item="1216")))
    rows.append((tid, "Aitareya Upanishad", 15, "aitareya", "Aitareya Upanishad"))

    # ---------------- Chandogya 1-5, 7, 8 (item 945) ----------------
    m945 = json.loads((SRC / "mapping_945.json").read_text(encoding="utf-8"))
    urls945 = ["https://openn.library.upenn.edu/Data/0002/html/mscoll390_item945.html",
               "https://openn.library.upenn.edu/Data/0002/mscoll390_item945/data/mscoll390_item945_TEI.xml"]
    for pr in (1, 2, 3, 4, 5, 7, 8):
        sa_pr, en_pr = load_chandogya(pr), eng_chandogya_labeled(pr)
        pages_pr = m945[str(pr)]
        secs, omitted = chandogya_sections(pr, sa_pr, en_pr, pages_pr)
        f_first, f_last = pages_pr[0]["page"], pages_pr[-1]["page"]
        fol = lambda f: f"{f[1:3].lstrip('0')}{f[3]}"
        tid = PREFIX + f"chandogya-{pr}"
        title = f"Chandogya Upanishad, Prapathaka {pr} ({CHU_TITLES[pr]})"
        gap_txt = ""
        if omitted:
            gap_txt = (f" The copyist left out paragraphs {pr}.{omitted[0][0]}.{omitted[0][1]}-{omitted[-1][1]} (his eye "
                       "passed between repeated words); they are not shown, because no page of this manuscript carries them.")
        notes_pr = [pg["note"] for pg in pages_pr if pg.get("note")]
        intro = (
            "<p>The Chandogya Upanishad belongs to the Samaveda and is one of the two longest and oldest Upanishads. "
            f"It has eight chapters (prapathakas). This entry gives chapter {pr}. {CHU_SUMMARY[pr]}</p>"
            "<p>The page images come from University of Pennsylvania Libraries, Ms. Coll. 390 Item 945, a paper manuscript of "
            "74 leaves (11 x 17 cm) holding the whole Chandogya Upanishad, written in Devanagari, 10 to 11 lines to a side, on "
            "blue machine-made paper with watermarks; it is undated (catalogued 18th or 19th century). The scribe numbers the "
            "khandas and closes each chapter with a colophon, but does not number paragraphs. "
            f"Chapter {pr} runs from fol. {fol(f_first)} to fol. {fol(f_last)}.</p>"
            "<p>For every page, the first and last words were read on the image and found in the edited text; the page "
            "boundaries follow from them. Each section below holds the paragraphs that end on one page, with every page "
            f"they occupy.{gap_txt}</p>")
        tnotes = [
            "Sanskrit: GRETIL, Chandogyopanisad with the commentary ascribed to Samkara, mula text only (input by the Sansknet "
            "project). Paragraph numbers (khanda.paragraph) follow the edition. Three legacy encoding artifacts in GRETIL "
            "chapter 2 ('saptavidh.am', 'brahmavarcasy:', 'tejasvy:') are normalized.",
            "English: F. Max Müller, 'Khandogya-upanishad', The Upanishads part I, Sacred Books of the East 1 (1879), from the "
            "proofread English Wikisource transcription; footnotes are not reproduced. Where Müller divides a khanda into a "
            "different number of paragraphs than the Sanskrit edition, the whole khanda stands in one section and keeps his "
            "numbers. In other khandas his paragraph breaks sometimes fall a clause earlier or later than the Sanskrit ones.",
            "Transcription slips corrected to the printed page: 1.9.2 'udîttha' (printed udgîtha), 3.16.2 'sacrifices' "
            "(sacrificer,), 4.6.1 'toward' (towards), 7.25.1 'alt' (all); the stray heading 'Elventh Khanda' inside 2.10.6 "
            "is removed. 1.2.1 'Whent he' is a misprint in the book itself and is kept as printed.",
            "The manuscript readings differ from the edition in places; the Sanskrit shown is the edition text."] + notes_pr
        entries.append((tid, entry_json(
            tid, title,
            f"Chapter {pr} of the Chandogya Upanishad in Sanskrit and Max Müller's English, each passage linked to the page "
            "of a Sanskrit manuscript of the whole Upanishad at the University of Pennsylvania (Ms. Coll. 390 Item 945).",
            intro, tnotes, secs,
            GRETIL + "sa_chAndogyopaniSad-comm.xml", gretil_lic,
            f"F. Max Müller, The Upanishads I, SBE 1 (Oxford, 1879), {WS}{WS_PAGES[f'chandogya{pr}'].replace(' ', '_')}",
            "public domain (1879); Wikisource transcription CC BY-SA 4.0", "F. Max Müller (1879)", urls945, item="945")))
        rows.append((tid, title, chu_order(pr), "chandogya", f"Chandogya Upanishad {pr}"))

    # ---------------- Mandukya ----------------
    sa, en = load_mandukya(), eng_mandukya()
    secs = []
    for _, a, b, pages, note in MANDUKYA_MAP:
        vs = range(a, b + 1)
        secs.append(build_section(f"{a}-{b}", f"Māṇḍūkya Upaniṣad {a}-{b}",
                                  sup_join((v, sa[v]) for v in vs), sup_join((v, en[v]) for v in vs), pages, note))
    tid = PREFIX + "mandukya"
    entries.append((tid, entry_json(
        tid, "Mandukya Upanishad",
        "The Mandukya Upanishad, twelve short paragraphs on the syllable Om and the four states of the self, in Sanskrit "
        "and R. E. Hume's English, on the last leaf of a Sanskrit manuscript at the University of Pennsylvania.",
        "<p>The Mandukya, the shortest of the principal Upanishads, belongs to the Atharvaveda. In twelve paragraphs it "
        "identifies the syllable Om with all that is, past, present and future, and with the self, whose four 'quarters' "
        "are waking, dreaming, deep sleep and a fourth state beyond them; the sounds a, u and m stand for the first three. "
        "Gaudapada's verse commentary on it (the Mandukya Karika) is a founding text of Advaita Vedanta.</p>"
        + MS_INTRO +
        "<p>The Mandukya is the last text in the manuscript, on fol. 16r and 16v (the catalogue gives 15v-16v; fol. 15v "
        "carries the end of the Mundaka). Max Müller did not translate it, so the English is R. E. Hume's (1921).</p>",
        ["Sanskrit: GRETIL, Mandukyopanisad (alternative version), input by Jeff Samuels; line breaks are those of the "
         "GRETIL file. In paragraph 7 GRETIL reads adṛśyam where the manuscript reads adṛṣṭam.",
         "English: R. E. Hume, The Thirteen Principal Upanishads (Oxford University Press, 1921), pp. 391-393, transcribed "
         "from the page images of archive.org copy thirteenprincipa00hume. Hume's footnote numbers and his two editorial "
         "sub-headings are left out."],
        secs,
        GRETIL + "sa_mANDUkyopaniSad-alt.xml", gretil_lic,
        "R. E. Hume, The Thirteen Principal Upanishads (London: Oxford University Press, 1921), pp. 391-393, "
        "https://archive.org/details/thirteenprincipa00hume/page/391",
        "public domain in the US (published 1921)", "R. E. Hume (1921)", mapping_urls)))
    rows.append((tid, "Mandukya Upanishad", 14, "mandukya", "Mandukya Upanishad, 12 paragraphs"))

    # ---------------- write ----------------
    for tid, e in entries:
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")
    by_id = dict(entries)
    texts = []
    for tid, title, order, work, short in sorted(rows, key=lambda r: r[2]):
        e = by_id[tid]
        texts.append({
            "id": tid, "slug": tid, "order": order, "title": title, "author_id": "upanishads",
            "language": "Sanskrit", "era": "Axial Age", "tradition": "hindu", "category": "sacred-text",
            "date_approx": ("c. 700-200 BCE (composition); manuscript copied 1836" if tid.endswith("chandogya-6")
                            else "c. 700-200 BCE (composition); 18th or 19th c. (Penn manuscript)"), "century": -5,
            "source": e["source"], "description": e["description"],
            "themes": ["upanishads", work, "vedanta", "sanskrit", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": f"Penn Ms. Coll. 390 Item {Path(p).stem.split('-')[0][4:]}, "
                                                        f"fol. {Path(p).stem.split('-f')[1].lstrip('0')}"}
                                for p in e["verification"]["scan_local_paths"]]},
        })
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Principal Upanishads",
            "group": "India", "date_sort": -600,
            "author_name": "Principal Upanishads (c. 700-200 BCE; Penn manuscripts, 18th-19th c.)",
            "source_url": OPENN_ITEM,
            "critical_edition": "GRETIL Sanskrit e-texts (Isa, Katha, Prasna, Mandukya, Aitareya, Chandogya)",
            "translator_name": "F. Max Müller (1879, 1884); R. E. Hume (1921) for the Mandukya",
            "original_lang_label": "Sanskrit · GRETIL (IAST)",
            "original_lang_code": "sa",
            "edition_label": "",
            "search_terms": "upanishad upanisad isa isavasya katha kathopanishad naciketas prasna pippalada mandukya aitareya prajnanam brahma chandogya uddalaka svetaketu tat tvam asi om atman brahman vedanta",
            "description": "Principal Upanishads in Sanskrit and English, each passage mapped to its page in Sanskrit "
                           "manuscripts at the University of Pennsylvania: the Isa, the Katha (six vallis), the Prasna "
                           "(six questions) and the Mandukya from Ms. Coll. 390 Item 869, the Aitareya from Item 1216, "
                           "and the complete Chandogya in eight chapters from Item 945 (chapter 6, 'thou art that', from "
                           "Item 1213, copied in 1836).",
        },
        "texts": texts,
        "authors": [{
            "id": "upanishads", "name": "Upanishads (Vedic tradition)", "dates": "c. 700-200 BCE", "century": -5,
            "era": "Axial Age", "tradition": "hindu", "language": "Sanskrit",
            "bio": "Anonymous philosophical texts attached to the Vedas, transmitted orally in Vedic schools and later in manuscripts.",
        }],
    }
    COLL.parent.mkdir(parents=True, exist_ok=True)
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")

    # mapping log
    log = {"manuscripts": {"869": MS_DESC, "1213": MS_DESC_1213, "945": MS_DESC_945, "1216": MS_DESC_1216},
           "images": [ITEMS[k]["url"] for k in ("869", "1213", "945", "1216")],
           "notes_869": (SRC / "mapping_notes_869.txt").read_text(encoding="utf-8").splitlines(),
           "notes_1213": (SRC / "mapping_notes_1213.txt").read_text(encoding="utf-8").splitlines(),
           "notes_1216": (SRC / "mapping_notes_1216.txt").read_text(encoding="utf-8").splitlines(),
           "pages_945": "see data/sources/upanishads/mapping_945.json (first and last words of every page, read on "
                        "the images, and the resulting page spans)",
           "sections": {tid: [{"section": s["section"], "scan_pages": s["scan_pages"], "scan_note": s["scan_note"]}
                              for s in e["translation"]] for tid, e in entries}}
    (SRC / "mapping_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(entries)} entries, {sum(len(e['translation']) for _, e in entries)} sections")


if __name__ == "__main__":
    main()
