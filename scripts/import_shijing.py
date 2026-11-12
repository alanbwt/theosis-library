#!/usr/bin/env python3
"""
import_shijing.py - Book of Odes (Shijing): the Major Odes (Daya) on the founding of Zhou, on a Keicho-era print.

Eight odes of the Daya that tell the rise of the Zhou house (Mao 235 文王, 236 大明, 237 緜, 240 思齊, 241 皇矣,
243 下武, 244 文王有聲, 245 生民). One entry per ode; each section is the stanzas that begin on one page of the
print, and lists every page its text runs across.

Chain of evidence:
  1. SCAN     National Diet Library, 詩經 2卷, [慶長年間] 活字印 (movable-type print of the Keicho era, 1596-1615),
              call no. WA7-183, vol. [2] (info:ndljp/pid/2544552), main text only, 8 columns of 17 characters a page,
              with Japanese reading marks. IIIF https://dl.ndl.go.jp/api/iiif/2544552/manifest.json. Each page is cut
              from its two-page opening with an IIIF region request (boxes in data/sources/shijing/page-crops.json).
              Access restriction: PDM (public domain mark).
  2. MAPPING  The opening characters of every column on the pages used were read on the images and recorded in
              data/sources/shijing/column-heads.tsv (ode tails "N章章N句" and headings marked). Each reading is aligned
              to the ode text; a stanza belongs to the page where it begins.
  3. TEXT     Wikisource (zh) 詩經/<ode> pages (Mao text), stanza by stanza. CC BY-SA 4.0.
  4. ENGLISH  James Legge, The Shih King, Sacred Books of the East vol. 3 (Oxford, 1879), from the validated
              Wikisource transcription (Page:Sacred Books of the East - Volume 3.djvu/411-433); footnotes and the
              editors' reconstructions (text supplied from another edition) are left out. Public domain.

Usage:
    python3 scripts/import_shijing.py
"""

import html
import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT_P = Path(__file__).resolve().parent.parent
SRC = str(ROOT_P) + "/data/sources/shijing/"
SCAN_DIR = ROOT_P / "site" / "assets" / "scans" / "shijing"
PUB_DIR = ROOT_P / "translations" / "published"
COLL = ROOT_P / "data" / "collections" / "shijing.json"
KEY = "shijing"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
UA = "TheosisLibraryResearch/1.0 (non-commercial reference library)"
NDL_ITEM = "https://dl.ndl.go.jp/pid/2544552"
NDL_MANIFEST = "https://dl.ndl.go.jp/api/iiif/2544552/manifest.json"
WS_ZH = "https://zh.wikisource.org/wiki/%E8%A9%A9%E7%B6%93"
WS_EN = "https://en.wikisource.org/wiki/Sacred_Books_of_the_East/Volume_3/The_Shih/The_Major_Odes_of_the_Kingdom"
CJK = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0002ffff]")

# (key, Mao number, pinyin, Legge's SBE title, decade/ode in Legge, summary)
ODES = [
    ("文王", 235, "Wen wang", "The Wan Wang", "Decade i, Ode 1", "King Wen in heaven and the transfer of Heaven's appointment from Shang to Zhou"),
    ("大明", 236, "Da ming", "The Ta Ming", "Decade i, Ode 2", "the mothers of King Wen and King Wu and the victory over Shang at Muye"),
    ("緜", 237, "Mian", "The Mien", "Decade i, Ode 3", "the ancient duke Danfu (Tai Wang) leading the Zhou people to the plain below Mount Qi and building there"),
    ("思齊", 240, "Si qi", "The Sze Kai", "Decade i, Ode 6", "Tai Ren, mother of King Wen, and the virtue of King Wen"),
    ("皇矣", 241, "Huang yi", "The Hwang I", "Decade i, Ode 7", "God choosing the Zhou house: Tai Wang, Wang Ji and King Wen's campaigns against Mi and Chong"),
    ("下武", 243, "Xia wu", "The Hsia Wu", "Decade i, Ode 9", "King Wu as heir of the virtue of his predecessors"),
    ("文王有聲", 244, "Wen wang you sheng", "The Wan Wang Yu Shang", "Decade i, Ode 10", "King Wen's city at Feng and King Wu's capital at Hao"),
    ("生民", 245, "Sheng min", "The Shang Min", "Decade ii, Ode 1", "the miraculous birth of Hou Ji, ancestor of the Zhou, and the origin of agriculture and sacrifice"),
]
# Wikisource gives 遐 with the variant 瑕 in 思齊 stanza 4; Legge translates 瑕 ("without stain"), so 瑕 is used.
READINGS = {"思齊": [("{{另|遐|瑕}}", "瑕")]}
EQUIV = [set(s) for s in ["于於", "為爲", "緜綿", "廱雝", "淢洫", "隕殞", "暨及", "迺廼", "兌兑", "恆恒"]]


# ---------------------------------------------------------------- English (Legge, SBE 3, Wikisource Page namespace)


EN_SRC = SRC + "wikisource-en/"

# ode key -> (first page, first section, last page, last section or None = whole page)
ODE_PAGES = {
    "文王": (411, "ode1", 414, "ode1"),
    "大明": (414, "ode2", 416, "ode2"),
    "緜": (416, "ode3", 419, None),
    "思齊": (421, "ode6", 422, None),
    "皇矣": (423, None, 427, "ode7"),
    "下武": (427, "ode9", 428, "ode9"),
    "文王有聲": (428, "ode10", 430, "ode10"),
    "生民": (430, "ode1", 433, "ode1"),
}
PAGE_OTHER = "\u0001"   # marks a line end that is a real verse-line end


def page_body(n, section):
    t = open(f"{EN_SRC}page-{n}.wiki", encoding="utf-8").read()
    t = re.sub(r"<noinclude>.*?</noinclude>", "", t, flags=re.S)
    if section is None:
        return re.sub(r'<section (?:begin|end)="[^"]*"\s*/>', "", t)
    m = re.search(rf'<section begin="{section}"\s*/>(.*?)<section end="{section}"\s*/>', t, re.S)
    assert m, (n, section)
    return m.group(1)


def strip_templates(x):
    x = x.replace("{{nop}}", "\u0002")
    x = re.sub(r"<ref[^>/]*/>", "", x)
    x = re.sub(r"<ref[^>]*>.*?</ref>", "", x, flags=re.S)
    x = x.replace("{{page other|{{wsp|0.5em}}|{{br}}}}", PAGE_OTHER)
    # remove editorial reconstructions (text supplied from another edition, not printed in SBE 3)
    for _ in range(3):
        x = re.sub(r"\{\{reconstruct\|(?:[^{}]|\{\{[^{}]*\}\})*\}\}", "", x)
    x = re.sub(r"\{\{smaller block/s\}\}.*?\{\{smaller block/e\}\}", "", x, flags=re.S)
    x = x.replace("{{lb}}", PAGE_OTHER + "\n")
    x = re.sub(r"\{\{(?:anchor\+?)\|[^{}]*\}\}", "", x)
    x = re.sub(r"\{\{main other\|[^{}]*(?:\{\{[^{}]*\}\}[^{}]*)*\}\}", "", x)
    x = re.sub(r"\{\{SIC\|([^{}|]*)\|[^{}]*\}\}", r"\1", x)
    x = re.sub(r"\{\{bl/il\|([^{}|]*)\}\}", r"\1", x)
    x = re.sub(r"\{\{(?:gap|BC)\}\}", "", x)
    for _ in range(4):
        x = re.sub(r"\{\{(?:tooltip|nowrap|sc|asc|lang\|[^|{}]*|bl|c|center|smaller|larger)\|([^{}|]*)(?:\|[^{}]*)?\}\}", r"\1", x)
        x = re.sub(r"\{\{sp\|([^{}|]*)\|([^{}|]*)\}\}", r"\1\2", x)
    x = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", x)
    x = re.sub(r"\[\[([^\]]*)\]\]", r"\1", x)
    x = re.sub(r"\{\{(?:dhr|rule|center block/s|center block/e|hanging indent/s|hanging indent/e|nop)[^{}]*\}\}", "", x)
    x = x.replace("''", "")
    return x


def ode_english(key):
    p1, s1, p2, s2 = ODE_PAGES[key]
    chunks = []
    for n in range(p1, p2 + 1):
        sec = s1 if n == p1 else (s2 if n == p2 else None)
        chunks.append(strip_templates(page_body(n, sec)))
    # drop heading text before the poem on the first page: everything up to the end of the ode title line
    text = ""
    for ch in chunks:
        ch = ch.strip("\n ")
        if not text:
            text = ch
        elif text.endswith("\u0002") or ch.startswith("\u0002"):
            text = text.rstrip("\u0002 \n") + "\n\n" + ch.lstrip("\u0002 \n")
        elif text.endswith(PAGE_OTHER):
            text = text + "\n" + ch
        else:
            text = text.rstrip() + " " + ch.lstrip()
    text = text.replace("\u0002", "\n\n")
    leftover = re.findall(r"\{\{[^{}]*\}\}", text)
    assert not leftover, (key, leftover[:5])
    stanzas = []
    for para in re.split(r"\n[ \t]*\n", text):
        para = para.strip()
        if not para:
            continue
        flat = re.sub(r"\s*\n\s*", " ", para)
        lines = [l.strip() for l in flat.split(PAGE_OTHER) if l.strip()]
        stanzas.append(lines)
    # drop heading stanzas (decade/ode titles) that precede the poem
    while stanzas and re.match(r"^(The (First|Second|Third) Decade|Ode \d+)", stanzas[0][0]):
        stanzas = stanzas[1:]
    return stanzas




# ---------------------------------------------------------------- Chinese (Wikisource)

def ode_chinese(key, expect):
    """Stanzas of the ode from Wikisource. Some pages put one stanza per line, others separate stanzas by blank
    lines; whichever layout gives the stanza count of Legge's translation is used (asserted)."""
    t = open(SRC + f"wikisource-zh/{key}.wiki", encoding="utf-8").read()
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"-\{(.*?)\}-", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    for a, r in READINGS.get(key, []):
        assert t.count(a) == 1, (key, a)
        t = t.replace(a, r)
    t = re.sub(r"\{\{另\|([^|{}]*)\|[^{}]*\}\}", r"\1", t)     # {{另|main|variant}}: the main reading
    body = t[t.index("===" + key + "==="):].split("===註解===")[0]
    assert "{{" not in body, (key, body[:200])
    groups, cur, lines = [], [], []
    for line in body.splitlines():
        if line.startswith(":"):
            s = line[1:].strip()
            if re.match(r"^《.*》，.*章", s):
                continue
            cur.append(s)
            lines.append([s])
        elif not line.strip() and cur:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    if len(groups) == expect:
        return groups
    assert len(lines) == expect, (key, len(groups), len(lines), expect)
    return lines


def cjk(s):
    return [c for c in s if CJK.search(c)]


# ---------------------------------------------------------------- column readings and alignment

def eq(a, b):
    return a == b or any(a in s and b in s for s in EQUIV)


def lcs_score(head, seg):
    n, m = len(head), len(seg)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            L[i + 1][j + 1] = L[i][j] + 1 if eq(head[i], seg[j]) else max(L[i][j + 1], L[i + 1][j])
    return L[n][m] + (0.5 if seg and eq(head[0], seg[0]) else 0)


def load_layout():
    pages = []
    for line in open(SRC + "column-heads.tsv", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        canvas, side, heads = line.rstrip("\n").split("\t")[:3]
        cols = []
        for i, h in enumerate(heads.split(), 1):
            kind = {"T:": "title", "E:": "tail", "X:": "other"}.get(h[:2], "blank" if h == "-" else "text")
            cols.append((i, kind, h[2:] if kind in ("title", "tail", "other") else h))
        pages.append(((int(canvas), side), cols))
    return pages


def align(texts):
    """texts: {ode: list of CJK chars}. Returns columns [(ode, pos, page, col, head, score)]."""
    order = [o[0] for o in ODES]
    k, prev, out, started = 0, None, [], False
    for page, cols in load_layout():
        for i, kind, h in cols:
            if kind == "tail":
                if started:
                    k, prev, started = k + 1, None, False
                continue
            if kind != "text":
                continue
            ode = order[k]
            text = texts[ode]
            lo = 0 if prev is None else prev + 1
            hi = 1 if prev is None else min(len(text), prev + 19)
            best = max(range(lo, max(lo + 1, hi)), key=lambda p: (lcs_score(h, text[p:p + len(h) + 1]) - 0.01 * abs(p - (lo + 16)), -p))
            sc = lcs_score(h, text[best:best + len(h) + 1])
            out.append((ode, best, page, i, h, sc))
            prev, started = best, True
    assert k == len(order), (k, "odes found")
    return out


# ---------------------------------------------------------------- scans

def side_name(side):
    return "right-hand" if side == "R" else "left-hand"


def page_label(page):
    return f"canvas {page[0]}, {side_name(page[1])} page"


def scan_file(page):
    return f"{KEY}/ndl-wa7-183-2-{page[0]:03d}{page[1].lower()}.jpg"


def ensure_scans(pages):
    boxes = json.load(open(SRC + "page-crops.json", encoding="utf-8"))
    svc = {}
    for line in open(SRC + "iiif-canvases.tsv", encoding="utf-8"):
        n, _, url = line.rstrip("\n").split("\t")
        svc[int(n)] = url
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for page in pages:
        dst = ROOT_P / "site" / "assets" / "scans" / scan_file(page)
        if dst.exists() and dst.stat().st_size > 10_000:
            continue
        x1, y1, x2, y2 = boxes[f"{page[0]}{page[1]}"]["box"]
        url = f"{svc[page[0]]}/{x1},{y1},{x2 - x1},{y2 - y1}/,2400/0/default.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        dst.write_bytes(urllib.request.urlopen(req, timeout=180).read())
        time.sleep(1)


# ---------------------------------------------------------------- build

def build():
    en = {o[0]: ode_english(o[0]) for o in ODES}
    zh = {o[0]: ode_chinese(o[0], len(en[o[0]])) for o in ODES}
    texts = {}
    for key, *_ in ODES:
        assert len(zh[key]) == len(en[key]), (key, len(zh[key]), len(en[key]))
        texts[key] = [c for st in zh[key] for line in st for c in cjk(line)]
    cols = align(texts)
    low = [c for c in cols if c[5] < len(c[4]) - 1]
    layout = dict(load_layout())

    rows, all_pages = [], []
    for order, (key, mao, py, sbe_title, sbe_ref, summary) in enumerate(ODES, 1):
        oc = [c for c in cols if c[0] == key]
        pages = []
        for c in oc:
            if not pages or pages[-1]["page"] != c[2]:
                pages.append({"page": c[2], "start": c[1], "cols": []})
            pages[-1]["cols"].append(c)
        assert pages[0]["start"] == 0, (key, pages[0])
        units, off = [], 0
        for n, (zst, est) in enumerate(zip(zh[key], en[key]), 1):
            ln = len([c for line in zst for c in cjk(line)])
            units.append({"n": n, "zh": zst, "en": est, "start": off, "end": off + ln})
            off += ln

        def page_at(o):
            return max(i for i, p in enumerate(pages) if p["start"] <= o)

        groups = {}
        for u in units:
            u["p0"], u["p1"] = page_at(u["start"]), page_at(u["end"] - 1)
            groups.setdefault(u["p0"], []).append(u)
        sections, files_all = [], []
        for k in sorted(groups):
            us = groups[k]
            pg = pages[k]
            span = list(range(k, max(u["p1"] for u in us) + 1))
            files = [scan_file(pages[j]["page"]) for j in span]
            for f in files:
                if f not in files_all:
                    files_all.append(f)
            first, last = us[0], us[-1]
            lay = layout[pg["page"]]
            note = [f"National Diet Library WA7-183, vol. [2], IIIF {page_label(pg['page'])}: "
                    f"{sum(1 for c in lay if c[1] != 'blank')} columns of up to 17 characters, main text only, with Japanese reading marks."]
            chk = f"Checked on the image: the first column of this ode on this page begins ‹{pg['cols'][0][4]}›"
            if len(pg["cols"]) > 1:
                chk += f", the last begins ‹{pg['cols'][-1][4]}›"
            note.append(chk + ".")
            fc = [c for c in pg["cols"] if c[1] <= first["start"]][-1]
            if fc[1] == first["start"]:
                note.append(f"Stanza {first['n']} opens column {fc[3]}.")
            else:
                note.append(f"Stanza {first['n']} begins inside column {fc[3]} (the column opens ‹{fc[4]}›), "
                            f"{first['start'] - fc[1]} characters down.")
            heads = [c for c in lay if c[1] in ("title", "tail")]
            for i, kind, h in heads:
                note.append(f"Column {i} reads {h}" + (" (the ode's stanza and line count)." if kind == "tail" else " (heading)."))
            prev_units = [u for u in units if u["end"] > pg["start"] and u["start"] < first["start"]]
            if prev_units:
                note.append(f"Above it the page finishes stanza {prev_units[0]['n']}, shown in the previous section.")
            if len(span) == 1:
                note.append("The section ends on this page.")
            else:
                cont = [f"{page_label(pages[j]['page'])} (first column ‹{pages[j]['cols'][0][4]}›)" for j in span[1:]]
                note.append(f"Stanza {last['n']} runs on to " + " and ".join(cont) + ", where the section ends.")
            note.append("The Chinese shown is the Wikisource Mao text, not a transcription of this print; Legge's English translates the same text.")
            zh_html = "".join(f"<p><sup>{u['n']}</sup>" + "<br>".join(html.escape(l, quote=False) for l in u["zh"]) + "</p>" for u in us)
            en_html = "".join(f"<p><sup>{u['n']}</sup>" + "<br>".join(html.escape(l, quote=False) for l in u["en"]) + "</p>" for u in us)
            sections.append({
                "section": f"c{pg['page'][0]}{pg['page'][1].lower()}",
                "original_ref": f"Shijing, Mao {mao} {key}, stanza {first['n']}" + (f"-{last['n']}" if last is not first else "")
                                + f"; NDL WA7-183 vol. [2] {page_label(pg['page'])}",
                "original_text": zh_html,
                "text": en_html,
                "scan_pages": files,
                "scan_note": " ".join(note),
            })
        for p in pages:
            if p["page"] not in all_pages:
                all_pages.append(p["page"])
        slug = re.sub(r"[^a-z]+", "-", py.lower()).strip("-")
        tid = f"{PREFIX}{mao}-{slug}"
        title = f"Book of Odes, Mao {mao}: {py} {key} (Keicho-era print)"
        desc = (f"The ode {key} ({py}), on {summary}, from the Major Odes of the Book of Odes, page by page on a Keicho-era "
                "Japanese movable-type print, with the Chinese text and James Legge's English.")
        intro = (
            f"<p>{key} ({py}, Mao {mao}) is one of the Major Odes of the Kingdom (大雅 <em>Daya</em>) in the Book of Odes "
            f"(詩經 <em>Shijing</em>); its subject is {summary}. With the other odes in this group it forms the Zhou court's account of "
            "how the house of Zhou rose to rule, and it was sung at the Zhou court; it is usually dated to the early Western Zhou "
            "(11th-10th century BCE).</p>"
            "<p>The photographs are of a copy of the Book of Odes in the National Diet Library, Tokyo (call no. WA7-183), printed "
            "with movable type in Japan in the Keicho era (1596-1615): main text only, eight columns of seventeen characters to the page, "
            "with Japanese reading marks added by hand, and the count of stanzas and lines after each ode. "
            f"In this copy the ode runs from {page_label(pages[0]['page'])} to {page_label(pages[-1]['page'])} of the second volume. "
            "Each section gathers the stanzas that begin on one page and links to that page and to any page the last stanza runs onto; "
            "the page boundaries were found by reading the first characters of every column on the photographs. "
            "The Chinese is the Mao text from Wikisource. The English is James Legge's translation in Sacred Books of the East, "
            f"volume 3 (1879), where this ode is The Major Odes of the Kingdom, {sbe_ref}; his footnotes are not reproduced.</p>"
        )
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Classical Chinese / English",
            "source": "National Diet Library WA7-183 (Keicho-era movable-type print of the Shijing, vol. 2) + Wikisource Mao text + "
                      "James Legge, Sacred Books of the East 3 (1879), via Wikisource",
            "description": desc,
            "introduction": intro,
            "translator_notes": [
                f"English: James Legge, The Shih King, Sacred Books of the East vol. 3 (1879), The Major Odes of the Kingdom, {sbe_ref} ({sbe_title}). Stanzas are numbered as in the Chinese.",
                "Text is taken from the validated Wikisource transcription; footnotes and lines the Wikisource editors supplied from Legge's 1871 edition are left out.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": "National Diet Library Digital Collections, 詩經 2卷 [慶長年間] 活字印, vol. [2], " + NDL_ITEM + "; IIIF manifest " + NDL_MANIFEST,
                "scan_license": "Public domain (NDL access restriction PDM, public domain mark); each page is cut from its two-page opening",
                "scan_manuscript": "National Diet Library, call no. WA7-183, 詩經 2 vols, movable-type print, Keicho era (1596-1615), main text only",
                "scan_mapping": "The opening characters of every column on the pages used were read on the images (data/sources/shijing/column-heads.tsv) "
                                "and aligned to the ode text; a section starts on the page where its first stanza begins and lists every page its text runs across.",
                "scan_mapping_urls": [NDL_ITEM, NDL_MANIFEST],
                "scan_local_paths": files_all,
                "original_text_source": f"Wikisource (zh) 詩經/{key} " + WS_ZH + "/" + urllib.request.quote(key),
                "original_text_license": "Ancient text public domain; Wikisource transcription CC BY-SA 4.0",
                "translation_source": "James Legge, The Shih King, Sacred Books of the East vol. 3 (Oxford, 1879), validated Wikisource transcription " + WS_EN,
                "translation_license": "Public domain (published 1879); Wikisource transcription CC BY-SA 4.0",
                "translator": "James Legge (1879)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order,
            "title": title, "author_id": "shijing-poets", "language": "Classical Chinese",
            "era": "Axial Age", "tradition": "confucian", "category": "sacred-text",
            "date_approx": "c. 11th-10th c. BCE (Western Zhou court odes); print Keicho era (1596-1615)",
            "century": -10,
            "source": entry["source"], "description": desc,
            "themes": ["shijing", "book-of-odes", "daya", "zhou", "confucian", "chinese", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f, "caption": f"NDL WA7-183 vol. 2, canvas {int(f[-8:-5])}, {side_name(f[-5].upper())} page"} for f in files_all]},
        })
        print(f"  {tid}: {len(sections)} sections, {len(files_all)} pages, {len(units)} stanzas")

    ensure_scans(all_pages)
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Book of Odes: hymns on the founding of Zhou (Keicho-era print)",
            "group": "China",
            "date_sort": -1000,
            "author_name": "Zhou court poets (Major Odes of the Shijing)",
            "source_url": NDL_ITEM,
            "critical_edition": "Mao text (Wikisource)",
            "translator_name": "James Legge (1879)",
            "original_lang_label": "Classical Chinese · Mao text",
            "original_lang_code": "lzh",
            "edition_label": "",
            "search_terms": "shijing shi jing book of odes book of songs classic of poetry daya major odes zhou king wen hou ji legge",
            "description": "Eight Major Odes of the Book of Odes that tell the rise of the Zhou house, from Hou Ji to King Wu, page by page "
                           "on a Japanese movable-type print of the Keicho era, with the Mao text and James Legge's English.",
        },
        "texts": rows,
        "authors": [{"id": "shijing-poets", "name": "Poets of the Book of Odes", "dates": "c. 11th-6th c. BCE", "century": -10,
                     "era": "Axial Age", "tradition": "confucian", "language": "Chinese",
                     "bio": "The anonymous court and local poets whose songs were gathered in the Book of Odes (Shijing)."}],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} entries, {len(all_pages)} page images")
    for c in low:
        print("  low-score column reading:", c)


if __name__ == "__main__":
    build()
