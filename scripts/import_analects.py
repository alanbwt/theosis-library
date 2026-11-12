#!/usr/bin/env python3
"""
import_analects.py - The Analects of Confucius (Lunyu), all 20 books, on a Kamakura-period manuscript.

One entry per book (20 entries). Each section is the group of Legge paragraphs that begin on one page of the
manuscript; the section lists every page its text runs across.

Chain of evidence:
  1. SCAN     Kyoto University Library, Seike bunko 清家文庫, 論語 2 vols, record RB00007936 (call no. 1-66/ロ/6貴,
              Important Cultural Property 1952), attributed to Kiyohara Yoshieda 清原良枝 (1253-1331); colophon of
              Kiyohara Edakata dated Tenbun 19 (1550) naming Yoshieda as the copyist. Main text only, 7 columns of 14
              characters a page, with Japanese reading marks. IIIF manifest
              https://rmda.kulib.kyoto-u.ac.jp/iiif/metadata_manifest/RB00007936/manifest.json (96 canvases, each a
              two-page opening). Each text page is cut from its opening with an IIIF region request (crop boxes in
              data/sources/analects/page-crops.json). Terms: 画像二次利用自由（所蔵表示）, free reuse with credit.
  2. MAPPING  The opening characters of every text column on every page (1,150 columns) were read on the images
              and recorded in data/sources/analects/column-heads.tsv. Each reading is aligned to the received text
              (longest-common-subsequence match near the expected position, 14 characters a column). A page starts at
              the aligned position of its first column; a paragraph belongs to the page on which it begins.
  3. TEXT     Received text from Wikisource (zh) 論語 (one page per book, revision ids in
              data/sources/analects/wikisource-revisions.json), with the few modern emendations printed there
              replaced by the received readings that Legge translated (READINGS). CC BY-SA 4.0.
  4. DIVISION Legge's chapter and paragraph division, taken from his Chinese text in Project Gutenberg #4094
              (The Chinese Classics, vol. 1) and aligned onto the Wikisource text; missing or misnumbered markers
              in the Gutenberg file are fixed in CHAPTER_FIXES, RELABEL and PARA_STARTS.
  5. ENGLISH  James Legge, Confucian Analects (The Chinese Classics vol. 1), Project Gutenberg #3330, public domain.

Usage:
    python3 scripts/import_analects.py
"""

import difflib
import html
import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT_P = Path(__file__).resolve().parent.parent
ROOT = str(ROOT_P) + "/"
SRC = ROOT + "data/sources/analects/"
SCAN_DIR = ROOT_P / "site" / "assets" / "scans" / "analects"
PUB_DIR = ROOT_P / "translations" / "published"
COLL = ROOT_P / "data" / "collections" / "analects.json"
KEY = "analects"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
UA = "TheosisLibraryResearch/1.0 (non-commercial reference library)"

RMDA_ITEM = "https://rmda.kulib.kyoto-u.ac.jp/item/rb00007936"
RMDA_MANIFEST = "https://rmda.kulib.kyoto-u.ac.jp/iiif/metadata_manifest/RB00007936/manifest.json"
RMDA_REUSE = "https://rmda.kulib.kyoto-u.ac.jp/reuse"
WS_INDEX = "https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E"
GUT_EN = "https://www.gutenberg.org/ebooks/3330"
GUT_ZH = "https://www.gutenberg.org/ebooks/4094"


# ---------------------------------------------------------------- received text, Legge division and English

CJK = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0002ffff]")
NUMS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "廿": 20, "卅": 30}

GUT_BOOKS = ["學而第一", "為政第二", "八佾第三", "里仁第四", "公冶長第五", "雍也第六", "述而第七", "泰伯第八",
             "子罕第九", "鄉黨第十", "先進第十一", "顏淵第十二", "子路第十三", "憲問第十四", "衛靈公第十五",
             "李氏第十六", "陽貨第十七", "微子第十八", "子張第十九", "堯曰第二十"]
WS_BOOKS = ["學而第一", "爲政第二", "八佾第三", "里仁第四", "公冶長第五", "雍也第六", "述而第七", "泰伯第八",
            "子罕第九", "鄉黨第十", "先進第十一", "顏淵第十二", "子路第十三", "憲問第十四", "衞靈公第十五",
            "季氏第十六", "陽貨第十七", "微子第十八", "子張第十九", "堯曰第二十"]


def cnum(s):
    s = s.replace("第", "")
    if s in NUMS:
        return NUMS[s]
    tot = 0
    if s[0] in "廿卅":
        tot, s = NUMS[s[0]], s[1:]
    elif len(s) >= 2 and s[1] == "十":
        tot, s = NUMS[s[0]] * 10, s[2:]
    elif s[0] == "十":
        tot, s = 10, s[1:]
    elif s[0] == "四" and len(s) == 2:      # 四一 = 41 in the Gutenberg file
        tot, s = 40, s[1:]
    for ch in s:
        tot += NUMS[ch]
    return tot


# Markers missing or mislabelled in the Gutenberg transcription of Legge's Chinese text. Each fix names the
# exact string before which a marker is inserted (first occurrence after the previous chapter marker), checked
# against Legge's English chapter for chapter starts.
CHAPTER_FIXES = {
    3: [(13, "【一節】王孫賈問曰")],
    5: [(25, "【一節】顏淵季路侍")],
    7: [(29, "子曰、仁遠乎哉")],
    8: [(11, "子曰、如有周公之才之美")],
    12: [(18, "李康子患盜")],
    13: [(11, "子曰、善人為邦百年")],
}
RELABEL = {(4, 9): 9}   # book 4: the 9th marker labelled 第八章 is chapter 9 (子曰、士志於道)


def gutenberg_book_streams():
    t = open(SRC + "legge/pg4094.txt", encoding="utf-8").read()
    t = t[t.index("學而第一"):t.index("*** END OF THE PROJECT")]
    lines = [l.strip() for l in t.splitlines() if CJK.search(l)]
    stream = "".join(lines).replace(" ", "").replace("　", "")
    parts = re.split("(" + "|".join(GUT_BOOKS) + ")", stream)
    out = {}
    for i in range(1, len(parts), 2):
        out[GUT_BOOKS.index(parts[i]) + 1] = parts[i + 1]
    assert sorted(out) == list(range(1, 21))
    return out


def gutenberg_markers(b, body):
    """Return (chars, markers): chars = list of CJK characters of Legge's Chinese text (placeholders for rare
    characters collapsed to one '?'); markers = list of (char_index, chapter, paragraph or None)."""
    body = re.sub(r"[（(][^）)]*[）)]", "?", body)            # '(zao4上穴，中土，下黽)' etc. = one character
    for chap, s in CHAPTER_FIXES.get(b, []):
        i = body.index(s)
        body = body[:i] + f"【FIX{chap}章】" + body[i:]
    chars, markers, seen = [], [], 0
    pos = 0
    tok = re.compile(r"【(FIX\d+|(?:第)?[一二三四五六七八九十廿卅]+)章】|【([一二三四五六七八九十]+)節】|(.)", re.S)
    chap, para_pending = None, None
    for m in tok.finditer(body):
        if m.group(1):
            seen += 1
            if m.group(1).startswith("FIX"):
                chap = int(m.group(1)[3:])
            else:
                chap = RELABEL.get((b, seen), cnum(m.group(1)))
            markers.append([len(chars), chap, None])
        elif m.group(2):
            n = cnum(m.group(2))
            if markers and markers[-1][0] == len(chars) and markers[-1][2] is None:
                markers[-1][2] = n
            else:
                markers.append([len(chars), chap, n])
        else:
            c = m.group(3)
            if CJK.search(c) or c == "?":
                chars.append(c)
    return chars, markers


def clean_ws(x):
    x = re.sub(r"-\{zh:([^;}]*);[^}]*\}-", r"\1", x)
    x = re.sub(r"-\{(.*?)\}-", r"\1", x)
    x = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", x)
    x = re.sub(r"\[\[([^\]]*)\]\]", r"\1", x)
    x = re.sub(r"\{\{另2?\|([^|}]*)\|[^}]*\}\}", r"\1", x)
    x = re.sub(r"\{\{[^}]*\}\}", "", x)
    x = re.sub(r"'''?", "", x)
    x = re.sub(r"<[^>]+>", "", x)
    return x.strip()


def ws_book_text(b):
    t = open(SRC + "wikisource/" + WS_BOOKS[b - 1] + ".wiki", encoding="utf-8").read()
    t = t[t.index("<onlyinclude>") + len("<onlyinclude>"):]
    for a, r in READINGS.get(b, []):
        assert t.count(a) == 1, (b, a)
        t = t.replace(a, r)
    for end in ("===校勘記===", "</onlyinclude>"):
        if end in t:
            t = t[:t.index(end)]
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<ref[^>]*/>", "", t)
    chunks = re.split(r'<div id="[^"]*"[^>]*>.*?</div>', t)
    chunks = [clean_ws(c) for c in chunks]
    return "".join(c for c in chunks if c)


OPENERS = "「『《〈（"


def legge_chapters_zh(b, gut_body):
    """Wikisource text of book b cut into Legge's chapters and paragraphs. Returns {chap: [(para, text)]}."""
    gchars, markers = gutenberg_markers(b, gut_body)
    ws = ws_book_text(b)
    widx = [i for i, c in enumerate(ws) if CJK.search(c)]
    wchars = [ws[i] for i in widx]
    sm = difflib.SequenceMatcher(None, gchars, wchars, autojunk=False)
    gmap = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        for k in range(i1, i2 + 1):
            if tag == "equal" or (i2 - i1) == (j2 - j1):
                gmap.setdefault(k, j1 + (k - i1))
            else:
                gmap.setdefault(k, j1 if k == i1 else min(j2, j1 + (k - i1)))
    cuts = []
    for gi, chap, para in markers:
        wi = gmap[gi]
        pos = widx[wi] if wi < len(widx) else len(ws)
        while pos > 0 and ws[pos - 1] in OPENERS:
            pos -= 1
        cuts.append((pos, chap, para))
    out = {}
    for n, (pos, chap, para) in enumerate(cuts):
        end = cuts[n + 1][0] if n + 1 < len(cuts) else len(ws)
        seg = ws[pos:end].strip()
        out.setdefault(chap, []).append((para, seg))
    ops = [(g, w) for g, w in ((("".join(gchars[a:b_])), "".join(wchars[c:d])) for t_, a, b_, c, d in sm.get_opcodes() if t_ != "equal")]
    return out, ops


ROM = {"I": 1, "V": 5, "X": 10, "L": 50}


def rom(s):
    v = 0
    for i, c in enumerate(s):
        v += -ROM[c] if i + 1 < len(s) and ROM[s[i + 1]] > ROM[c] else ROM[c]
    return v


def legge_english():
    t = open(SRC + "legge/pg3330.txt", encoding="utf-8").read()
    t = t[t.index("BOOK I.  HSIO R."):t.index("*** END OF THE PROJECT")].replace("\r\n", "\n")
    books = re.split(r"\nBOOK [IVXL]+\.[^\n]*\n", "\n" + t)
    out, fixes = {}, []
    for bn, body in enumerate(books[1:], 1):
        parts = re.split(r"(?:^|\n)\s*(?:CHAPTER|CHAP\.?)\s+([IVXL]+)\.?\s", "\n" + body)
        chaps = {}
        for j in range(1, len(parts), 2):
            cn, exp = rom(parts[j]), len(chaps) + 1
            if cn != exp:
                fixes.append((bn, parts[j], exp))
                cn = exp
            txt = parts[j + 1]
            if re.match(r"\s*\d+\.\s", txt):
                ps = re.split(r"(?:^|\n)\s*(\d+)\.\s", "\n" + txt)
            elif re.search(r"\n\s*2\.\s", txt):          # first paragraph printed without its number
                fixes.append((bn, cn, "paragraph 1 unnumbered"))
                ps = re.split(r"(?:^|\n)\s*(\d+)\.\s", "\n1. " + txt.lstrip())
            else:
                ps = ["", None, txt]
            pl = []
            for k in range(1, len(ps), 2):
                pl.append((int(ps[k]) if ps[k] else None, re.sub(r"\s+", " ", ps[k + 1]).strip()))
            chaps[cn] = pl
        out[bn] = chaps
    return out, fixes


# Legge readings restored where the Wikisource page prints a modern emendation or a variant reading
# (each verified against Legge's English and his Chinese text in Gutenberg #4094).
READINGS = {
    1: [("{{另2|已|一無「已」字}}", "")],                       # 1.7 吾必謂之學矣 (Legge's text has no 已)
    4: [("未<ref>傳世本『未』作『求』", "求<ref>")],              # 4.14 求爲可知也 (received text)
    5: [("{{另2|車馬衣裘|一作「車馬衣輕裘」。「輕」字係後人所加。}}", "車馬衣輕裘")],  # 5.25 Legge: 'light fur dresses'
    7: [("狎<ref>傳世本『狎』作『據』", "據<ref>"),              # 7.6 據於德 (received text)
        ("{{另|藝|執}}", "執")],                                  # 7.17 執禮
    10: [("（必有寢衣，長一身有半。）", "必有寢衣，長一身有半。"),  # 10.6 editorial brackets dropped
         ("{{另|疑|色}}", "色")],                                 # 10.18 色斯舉矣
    12: [("（誠不以富，亦祇以異。）", "誠不以富，亦祇以異。")],    # 12.10 Legge keeps the line here
    13: [("{{另|德|直}}", "直")],                                 # 13.18 直躬
    14: [("{{另|德|直}}", "直")],                                 # 14.36 以直報怨
    16: [("（『誠不以富，亦祇以異。』）", "")],                    # 16.12: modern transposition, not in Legge's text
    20: [("謂之貪<ref>", "謂之有司<ref>")],                       # 20.2 謂之有司 (received text)
}

# Paragraph starts where the Gutenberg markers are missing or misnumbered, set to Legge's English numbering.
PARA_STARTS = {
    (2, 4): [(1, "子曰"), (2, "三十"), (3, "四十"), (4, "五十"), (5, "六十"), (6, "七十")],
    (2, 10): [(1, "子曰"), (2, "觀其"), (3, "察其"), (4, "人焉廋哉！人"), (5, "人焉廋哉！」")],
    (2, 18): [(1, "子張"), (2, "子曰")],
    (3, 8): [(1, "子夏"), (2, "子曰：「繪"), (3, "曰：「禮")],
    (3, 19): [(None, "定公")],
    (3, 22): [(1, "子曰"), (2, "或曰"), (3, "「然則")],
    (5, 9): [(1, "宰予"), (2, "子曰：「始")],
    (6, 2): [(None, "哀公")],
    (7, 30): [(1, "陳司敗"), (2, "孔子退"), (3, "巫馬期以")],
    (8, 4): [(1, "曾子有疾"), (2, "曾子言曰"), (3, "君子所貴")],
    (9, 10): [(1, "顏淵"), (2, "夫子循循"), (3, "欲罷")],
    (10, 15): [(1, "朋友死"), (2, "朋友之饋"), (3, "非祭肉")],
    (12, 7): [(1, "子貢問"), (2, "子貢曰：「必不得已而去，於斯三"), (3, "子貢曰：「必不得已而去，於斯二")],
    (12, 10): [(1, "子張"), (2, "愛之"), (3, "誠不以富")],
    (12, 21): [(1, "樊遲"), (2, "子曰：「善哉"), (3, "先事")],
    (14, 22): [(1, "陳成子"), (2, "孔子沐浴"), (3, "公曰：「吿夫"), (4, "孔子曰"), (5, "之三子")],
    (17, 19): [(1, "子曰"), (2, "子貢曰"), (3, "子曰：「天")],
    (18, 9): [(1, "大師"), (2, "亞飯"), (3, "鼓方叔"), (4, "播鼗"), (5, "少師")],
}


def apply_para_starts(b, chapters):
    for (bb, c), starts in PARA_STARTS.items():
        if bb != b:
            continue
        full = "".join(t for _, t in chapters[c])
        pos, cuts = 0, []
        for num, st in starts:
            i = full.index(st, pos)
            while i > 0 and full[i - 1] in OPENERS:
                i -= 1
            cuts.append((i, num))
            pos = i + 1
        assert cuts[0][0] == 0, (b, c, full[:20])
        chapters[c] = [(num, full[i:(cuts[k + 1][0] if k + 1 < len(cuts) else len(full))].strip())
                       for k, (i, num) in enumerate(cuts)]
    return chapters


# ---------------------------------------------------------------- column readings and alignment

BOOKNUM = {"學而":1,"為政":2,"爲政":2,"八佾":3,"里仁":4,"公冶長":5,"雍也":6,"述而":7,"泰伯":8,"子罕":9,"鄉黨":10,
           "先進":11,"顏淵":12,"子路":13,"憲問":14,"衛靈公":15,"衞靈公":15,"季氏":16,"陽貨":17,"微子":18,"子張":19,"堯曰":20}
EQUIV = [set(s) for s in ["為爲", "悌弟", "說悅", "衛衞", "告吿", "慎愼", "舉擧", "尚尙", "修脩", "飲飮", "即卽", "清淸",
                          "屏屛", "顛顚", "汝女", "礼禮", "乱亂", "无無", "众衆眾", "鄰隣", "游遊", "於于", "與与", "强彊強",
                          "恒恆", "兹茲", "凶兇", "鬼", "峰", "猶犹", "惡悪", "敎教", "歎嘆", "智知", "智", "嘗甞", "叩扣",
                          "皐皋", "徵", "徹", "饑飢", "疎疏", "疏", "麑", "裘", "羣群", "寢寑", "衆眾", "寧甯", "沒没", "冕",
                          "暴", "效", "竊窃", "鬭鬥", "絕絶", "黑", "冰氷", "麥", "斂", "蓋盖", "糞", "內内", "虛虚"]]
def eq(a, b):
    return a == b or any(a in s and b in s for s in EQUIV)

def book_chars(b, gut):
    zh, _ = legge_chapters_zh(b, gut)
    zh = apply_para_starts(b, zh)
    chars, chap_of = [], []
    starts = {}
    for c in sorted(zh):
        starts[c] = len(chars)
        for p, t in zh[c]:
            for ch in t:
                if CJK.search(ch):
                    chars.append(ch); chap_of.append(c)
    return chars, chap_of, starts

def load_heads(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        canvas, side, heads = line.rstrip("\n").split("\t")[:3]
        rows.append((int(canvas), side, heads.split()))
    return rows

def score(head, text, pos):
    seg = text[pos:pos + len(head) + 1]
    n, m = len(head), len(seg)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            L[i + 1][j + 1] = L[i][j] + 1 if eq(head[i], seg[j]) else max(L[i][j + 1], L[i + 1][j])
    bonus = 0.5 if seg and eq(head[0], seg[0]) else 0
    return L[n][m] + bonus

def align(path):
    gut = gutenberg_book_streams()
    books = {b: book_chars(b, gut[b]) for b in range(1, 21)}
    cols = []          # (book, offset, canvas, side, colno, head)
    book, prev = None, None
    problems = []
    for canvas, side, heads in load_heads(path):
        for i, h in enumerate(heads, 1):
            if h in ("-", "PREFACE") or h.startswith("+"):
                continue
            if h.startswith("T:"):
                m = re.match(r"T:論語(.+)第[一二三四五六七八九十]+$", h)
                name = m.group(1)
                if name.startswith("卷"):
                    continue
                book = BOOKNUM[name]; prev = None
                continue
            text = books[book][0]
            exp = 0 if prev is None else prev + 14
            lo = 0 if prev is None else prev + 5
            hi = min(len(text), (1 if prev is None else prev + 28))
            best = None
            for pos in range(lo, max(lo + 1, hi)):
                sc = score(h, text, pos)
                key = (sc - 0.15 * abs(pos - exp), 0)
                if best is None or key > best[0]:
                    best = (key, pos)
            pos = best[1]; sc = score(h, text, pos)
            if sc < len(h) - 0.5 - 1 or (len(h) <= 2 and sc < len(h)):
                problems.append((canvas, side, i, h, "".join(text[exp - 3:exp + 10]), sc))
            cols.append((book, pos, canvas, side, i, h, sc))
            prev = pos
    return books, cols, problems



# ---------------------------------------------------------------- page layout and scans

BOOK_NAMES = [("Xue er", "學而"), ("Wei zheng", "爲政"), ("Ba yi", "八佾"), ("Li ren", "里仁"),
              ("Gongye Chang", "公冶長"), ("Yong ye", "雍也"), ("Shu er", "述而"), ("Taibo", "泰伯"),
              ("Zi han", "子罕"), ("Xiang dang", "鄉黨"), ("Xian jin", "先進"), ("Yan Yuan", "顏淵"),
              ("Zilu", "子路"), ("Xian wen", "憲問"), ("Wei Ling Gong", "衞靈公"), ("Ji shi", "季氏"),
              ("Yang Huo", "陽貨"), ("Weizi", "微子"), ("Zizhang", "子張"), ("Yao yue", "堯曰")]

# Column openings whose reading on the image is not certain; they are used for alignment but not reported
# as manuscript variants.
UNCERTAIN_HEADS = {(94, "L", 3)}


def side_name(side):
    return "right-hand" if side == "R" else "left-hand"


def page_label(canvas, side):
    return f"canvas {canvas}, {side_name(side)} page"


def scan_file(canvas, side):
    return f"{KEY}/rb00007936-{canvas:03d}{side.lower()}.jpg"


def ensure_scans(pages):
    """Each page is cut from its IIIF canvas with a region request (boxes in page-crops.json)."""
    boxes = json.load(open(SRC + "page-crops.json", encoding="utf-8"))
    svc = {}
    for line in open(SRC + "iiif-canvases.tsv", encoding="utf-8"):
        n, _, url = line.rstrip("\n").split("\t")
        svc[int(n)] = url
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for canvas, side in pages:
        dst = ROOT_P / "site" / "assets" / "scans" / scan_file(canvas, side)
        if dst.exists() and dst.stat().st_size > 10_000:
            continue
        x1, y1, x2, y2 = boxes[f"{canvas}{side}"]["box"]
        url = f"{svc[canvas]}/{x1},{y1},{x2 - x1},{y2 - y1}/max/0/default.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        dst.write_bytes(urllib.request.urlopen(req, timeout=120).read())
        time.sleep(0.5)


def page_layout():
    """Ordered pages with their columns: {(canvas, side): [(col, kind, head)]}."""
    layout = {}
    for canvas, side, heads in load_heads(SRC + "column-heads.tsv"):
        cols = []
        for i, h in enumerate(heads, 1):
            if h in ("-", "PREFACE"):
                kind = "blank" if h == "-" else "preface"
            elif h.startswith("T:"):
                kind = "title"
            elif h.startswith("+"):
                kind = "extra"
            else:
                kind = "text"
            cols.append((i, kind, h[2:] if kind == "title" else h.lstrip("+")))
        layout[(canvas, side)] = cols
    return layout


# ---------------------------------------------------------------- build

def unit_label(chap, para):
    return f"{chap}" if para is None else f"{chap}.{para}"


def cjk_len(s):
    return sum(1 for ch in s if CJK.search(ch))


def build():
    gut = gutenberg_book_streams()
    english, en_fixes = legge_english()
    books, cols, problems = align(SRC + "column-heads.tsv")
    layout = page_layout()
    order = list(layout)

    # columns per (book, page), in reading order
    bcols = {}
    for b, pos, canvas, side, i, h, sc in cols:
        bcols.setdefault(b, []).append({"page": (canvas, side), "col": i, "head": h, "pos": pos})
    for b, lst in bcols.items():
        ps = [c["pos"] for c in lst]
        assert ps == sorted(ps), (b, "column positions not increasing")

    all_pages = []
    rows = []
    for b in range(1, 21):
        zh, _ = legge_chapters_zh(b, gut[b])
        zh = apply_para_starts(b, zh)
        en = english[b]
        assert sorted(zh) == sorted(en), b
        units, off = [], 0
        for c in sorted(zh):
            zps, eps = zh[c], en[c]
            assert len(zps) == len(eps), (b, c, [p for p, _ in zps], [p for p, _ in eps])
            for (p, zt), (_, et) in zip(zps, eps):
                n = cjk_len(zt)
                units.append({"chap": c, "para": p, "zh": zt, "en": et, "start": off, "end": off + n})
                off += n
        assert off == len(books[b][0]), (b, off, len(books[b][0]))

        bc = bcols[b]
        pages = []
        for c in bc:
            if not pages or pages[-1]["page"] != c["page"]:
                pages.append({"page": c["page"], "start": c["pos"], "cols": []})
            pages[-1]["cols"].append(c)
        assert pages[0]["start"] == 0, (b, pages[0])

        def page_at(offset):
            k = max(i for i, p in enumerate(pages) if p["start"] <= offset)
            return k

        def col_at(k, offset):
            return [c for c in pages[k]["cols"] if c["pos"] <= offset][-1]

        groups = {}
        for u in units:
            u["p0"], u["p1"] = page_at(u["start"]), page_at(u["end"] - 1)
            groups.setdefault(u["p0"], []).append(u)

        sections, files_all = [], []
        for k in sorted(groups):
            us = groups[k]
            pk = pages[k]
            canvas, side = pk["page"]
            span = list(range(k, max(u["p1"] for u in us) + 1))
            files = [scan_file(*pages[j]["page"]) for j in span]
            for f in files:
                if f not in files_all:
                    files_all.append(f)
            first, last = us[0], us[-1]
            ref_first = f"{b}.{unit_label(first['chap'], first['para'])}"
            ref_last = f"{b}.{unit_label(last['chap'], last['para'])}"

            lay = layout[pk["page"]]
            text_cols = [c for c in pk["cols"]]
            note = [f"Kyoto University Library RB00007936, IIIF {page_label(canvas, side)}: "
                    f"{sum(1 for c in lay if c[1] in ('text', 'title', 'extra'))} written columns of up to 14 characters, main text only, with Japanese reading marks."]
            chk = f"Checked on the image: the first column of this book's text on this page begins ‹{text_cols[0]['head']}›"
            if len(text_cols) > 1:
                chk += f", the last begins ‹{text_cols[-1]['head']}›"
            note.append(chk + ".")
            titles = [c for c in lay if c[1] == "title"]
            for i, kind, h in titles:
                note.append(f"Column {i} carries the title {h}.")
            if k == 0 and not any(BOOKNUM.get(re.sub(r"^論語|第[一二三四五六七八九十]+$", "", h)) == b for _, _, h in titles):
                tp = [pg for pg in order if any(kd == "title" and BOOKNUM.get(re.sub(r"^論語|第[一二三四五六七八九十]+$", "", h)) == b
                                                for _, kd, h in layout[pg])]
                if tp:
                    note.append(f"The book title stands in the last written column of the facing {page_label(*tp[0])}.")
            fc = col_at(k, first["start"])
            if fc["pos"] == first["start"]:
                note.append(f"{ref_first} opens column {fc['col']}.")
            else:
                note.append(f"{ref_first} begins inside column {fc['col']} (the column opens ‹{fc['head']}›), "
                            f"{first['start'] - fc['pos']} characters down in the received text.")
            prev = [u for u in units if u["end"] > pk["start"] and u["start"] < first["start"]]
            if prev:
                pr = prev[0]
                note.append(f"Above it the page finishes {b}.{unit_label(pr['chap'], pr['para'])}, shown in the previous section.")
            if len(span) == 1:
                note.append("The section ends on this page.")
            else:
                cont = [f"{page_label(*pages[j]['page'])} (first column ‹{pages[j]['cols'][0]['head']}›)" for j in span[1:]]
                note.append(f"{ref_last} runs on to " + " and ".join(cont) + ", where the section ends.")
            sec_start, sec_end = first["start"], last["end"]
            var = []
            for j in span:
                for c in pages[j]["cols"]:
                    if not (sec_start <= c["pos"] < sec_end):
                        continue
                    if (pages[j]["page"][0], pages[j]["page"][1], c["col"]) in UNCERTAIN_HEADS:
                        continue
                    seg = books[b][0][c["pos"]:c["pos"] + len(c["head"])]
                    if not all(eq(x, y) for x, y in zip(c["head"], seg)):
                        var.append(f"‹{c['head']}› where the received text has ‹{''.join(seg)}›")
            if var:
                note.append("Column openings on these pages that differ from the received text: " + "; ".join(var) + ".")
            note.append("The Chinese shown is the received text (Wikisource), not a transcription of this manuscript; "
                        "Legge's English translates the received text.")

            zh_html = "".join(f"<p><sup>{unit_label(u['chap'], u['para'])}</sup>{html.escape(u['zh'], quote=False)}</p>" for u in us)
            en_html = "".join(f"<p><sup>{unit_label(u['chap'], u['para'])}</sup>{html.escape(u['en'], quote=False)}</p>" for u in us)
            sections.append({
                "section": f"c{canvas}{side.lower()}",
                "original_ref": f"Analects {ref_first}" + (f" to {ref_last}" if ref_last != ref_first else "")
                                + f"; Kyoto RB00007936 {page_label(canvas, side)}",
                "original_text": zh_html,
                "text": en_html,
                "scan_pages": files,
                "scan_note": " ".join(note),
            })

        for p in pages:
            if p["page"] not in all_pages:
                all_pages.append(p["page"])
        py, zh_name = BOOK_NAMES[b - 1]
        nch = len(zh)
        p_first, p_last = pages[0]["page"], pages[-1]["page"]
        vol = 1 if p_first[0] <= 44 else 2
        tid = f"{PREFIX}{b:02d}"
        title = f"Analects, Book {b}: {py} {zh_name} (Kamakura-period manuscript)"
        desc = (f"Book {b} of the Analects of Confucius ({zh_name}, {nch} chapters) page by page on a Kamakura-period "
                f"manuscript in Kyoto University Library, with the received Chinese text and James Legge's English.")
        intro = (
            f"<p>Book {b} of the <em>Analects</em> (論語 <em>Lunyu</em>), titled {zh_name} ({py}) after its opening words, "
            f"{nch} chapters in Legge's division. It is shown on a manuscript of the Analects in the Kiyohara family collection "
            "(Seike bunko) of Kyoto University Library, two volumes in regular script, seven columns of fourteen characters to the page, "
            "main text only, with red and black Japanese reading marks. A colophon by Kiyohara Edakata dated 1550 names the copyist as "
            "his ancestor Kiyohara Yoshieda (1253-1331), which places the copy around 1300, in the late Kamakura period; the attribution "
            "is traditional. The Kiyohara were hereditary readers of the Confucian classics at the Japanese court, and their text descends "
            "from the edition of the Analects with the collected commentary of He Yan (3rd century CE): after each pair of books the scribe "
            "copied the character counts of the classic and of the commentary, although only the classic is written out. The manuscript is "
            "an Important Cultural Property of Japan.</p>"
            f"<p>In this copy Book {b} runs from {page_label(*p_first)} to {page_label(*p_last)} (volume {vol}). "
            "Each section gathers the paragraphs that begin on one page, numbered by chapter and paragraph as in Legge, and links to that page "
            "and to any page the last paragraph runs onto. The page boundaries were found by reading the first characters of every column on "
            "the photographs. The Chinese shown is the received text, from Wikisource. This manuscript differs from it in places, most often by "
            "an added or missing particle (也, 矣, 焉) or a variant character form; the differences seen at column openings are listed in the "
            "scan notes. The English is James Legge's translation of the received text.</p>"
        )
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Classical Chinese (received text) / English",
            "source": "Kyoto University Library RB00007936 (Analects manuscript attributed to Kiyohara Yoshieda, c. 1300) "
                      "+ Wikisource received text + James Legge's English (Project Gutenberg)",
            "description": desc,
            "introduction": intro,
            "translator_notes": [
                "English: James Legge, Confucian Analects, The Chinese Classics vol. 1. Legge's chapter and paragraph numbers are kept as superscripts (chapter.paragraph).",
                "Legge translated the received text. Where this manuscript's wording differs, his English follows the received text shown here.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": "Kyoto University Rare Materials Digital Archive, 論語 (RB00007936), " + RMDA_ITEM + "; IIIF manifest " + RMDA_MANIFEST,
                "scan_license": "画像二次利用自由（所蔵表示）: images free to reuse with the credit 『論語』（京都大学附属図書館所蔵）and a link to the archive; "
                                "here each page is cut from its two-page opening (" + RMDA_REUSE + ")",
                "scan_manuscript": "Kyoto University Library, Seike bunko, call no. 1-66/ロ/6貴, 論語 2 vols, attributed to Kiyohara Yoshieda (1253-1331), "
                                   "late Kamakura period; colophon of Kiyohara Edakata, Tenbun 19 (1550); Important Cultural Property (1952)",
                "scan_mapping": "The opening characters of every column on every page were read on the images (data/sources/analects/column-heads.tsv) and "
                                "aligned to the received text; a section starts on the page where its first paragraph begins and lists every page its text runs across.",
                "scan_mapping_urls": [RMDA_ITEM, RMDA_MANIFEST],
                "scan_local_paths": files_all,
                "original_text_source": "Wikisource (zh) 論語, book page " + WS_BOOKS[b - 1] + " (revision in data/sources/analects/wikisource-revisions.json), " + WS_INDEX
                                        + "; chapter and paragraph division from Legge's Chinese text, Project Gutenberg #4094 " + GUT_ZH,
                "original_text_license": "Ancient text public domain; Wikisource transcription CC BY-SA 4.0",
                "translation_source": "James Legge, Confucian Analects, The Chinese Classics vol. 1 (1861; 2nd ed. Oxford 1893), Project Gutenberg #3330 " + GUT_EN,
                "translation_license": "Public domain (published 1861 and 1893)",
                "translator": "James Legge (1861/1893)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": b,
            "title": title, "author_id": "confucius", "language": "Classical Chinese",
            "era": "Axial Age", "tradition": "confucian", "category": "philosophy",
            "date_approx": "5th-4th c. BCE (compilation); manuscript c. 1300 CE (Kamakura period, attributed to Kiyohara Yoshieda)",
            "century": -5,
            "source": entry["source"], "description": desc,
            "themes": ["analects", "confucius", "lunyu", "confucian", "manuscript", "chinese", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f, "caption": f"Kyoto RB00007936, canvas {int(f[-8:-5])}, {side_name(f[-5].upper())} page"} for f in files_all]},
        })
        print(f"  {tid}: {len(sections)} sections, {len(files_all)} pages, {len(units)} paragraphs")

    ensure_scans(all_pages)
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Analects of Confucius (Kamakura-period manuscript)",
            "group": "China",
            "date_sort": -450,
            "author_name": "Confucius and his disciples (manuscript attributed to Kiyohara Yoshieda, c. 1300)",
            "source_url": RMDA_ITEM,
            "critical_edition": "Received text (Wikisource) in Legge's chapter and paragraph division",
            "translator_name": "James Legge (1861/1893)",
            "original_lang_label": "Classical Chinese · received text",
            "original_lang_code": "lzh",
            "edition_label": "",
            "search_terms": "analects lunyu confucius kongzi lun yu kiyohara kamakura manuscript legge",
            "description": "The Analects of Confucius, all twenty books, page by page on a Kamakura-period manuscript in Kyoto University Library "
                           "(attributed to Kiyohara Yoshieda, c. 1300), with the received Chinese text and James Legge's English.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} entries, {len(all_pages)} page images; Legge English fixes: {en_fixes}")
    for p in problems:
        print("  low-score column reading (kept, checked by eye):", p)


if __name__ == "__main__":
    build()
