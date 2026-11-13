#!/usr/bin/env python3
"""
qc2_venetus.py - rebuild Homer's Iliad on Venetus A (translations/published/
verified-venetus-iliad-*.json) so that every section is the text of one page
of the manuscript and links exactly that page.

Chain of evidence
-----------------
Page of every line: Homer Multitext Project (HMT), data release 2024c
(github.com/homermultitext/hmt-archive, releases-cex/hmt-2024c.cex). Its DSE
relation set urn:cite2:hmt:hmtdse.v1:all gives, for each Iliad line of Venetus
A (urn:cts:greekLit:tlg0012.tlg001.msA:BOOK.LINE), the folio side
(urn:cite2:hmt:msA.v1:12r) and the photograph (urn:cite2:hmt:vaimg.2017a:...).
A section is the run of lines on one folio side (one book per entry, so a page
that holds the end of one book and the start of the next gives a section in
each entry). Lines that the edition has but the index leaves out are placed
(a) when the lines before and after them in the manuscript are on the same
page, on that page, or (b) by reading the photograph (PLACED_BY_IMAGE below,
each checked on the image on 2026-11-12).

Greek (original_text): the HMT diplomatic edition of the Venetus A text
(urn:cts:greekLit:tlg0012.tlg001.msA.diplomatic, same release), line by line in
the manuscript's order, with its punctuation and signs as given. The release
states the licence CC BY-NC 4.0 (images: CC BY-SA, per the vaimg collection).
edition_text: Monro & Allen, Homeri Opera (Oxford 1908-1920), Perseus
canonical-greekLit tlg0012.tlg001.perseus-grc2 (CC BY-SA 4.0 encoding), for the
same lines; lines of the standard text that Venetus A lacks are given there
with the page before which they would stand.

English (text): A. T. Murray, Homer: The Iliad, Loeb Classical Library, 2 vols.,
London: Heinemann / New York: Putnam, 1924-1925 (public domain in the US),
Perseus canonical-greekLit tlg0012.tlg001.perseus-eng3 (CC BY-SA 4.0 encoding).
Murray marks every fifth line and the first line of every paragraph ("card").
The English is cut only at those marks: each block (from one mark to the next)
goes with the page that holds most of its lines (ties to the earlier page), so
the English of a section can start or end a few lines away from the Greek. The
exact English range is stated in each section's original_ref and scan_note.
Pages listed in ENGLISH_CUTS are instead cut at Murray's sentence ends: the
sentence that runs across the page break goes whole to one page, and the
scan_note says which (QC fix 2026-11-12).
Murray's footnotes are left out; speeches, which Perseus marks as quotations,
are shown in quotation marks.

Images: site/assets/scans/venetus-a/venetus-a-<image id>.jpg, the HMT IIIF
images at 1024 px width (as made by scripts/import_homer.py); missing pages
are fetched the same way.

Outputs: data/sources/qc-sinaiticus-venetus/venetus_check.json (problems found
by `check`), venetus_texts_json_rows.json (catalog rows to update),
venetus_pages.json (page -> lines table).

Usage (repo root):
  python3 scripts/qc2_venetus.py build        # rewrite the 24 entries
  python3 scripts/qc2_venetus.py check        # section/page/English checks
  python3 scripts/qc2_venetus.py crops OUTDIR FOLIO [FOLIO ...]   # first/last-line crops for checking
Re-runnable.
"""
import collections
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
IMG_DIR = SCANS / "venetus-a"
OUT = ROOT / "data" / "sources" / "qc-sinaiticus-venetus"
SRC = OUT / "venetus"
CEX_PATHS = [ROOT / "data" / "sources" / "qc-legacy" / "audit" / "hmt-2024c.cex", SRC / "hmt-2024c.cex"]
CEX_URL = "https://raw.githubusercontent.com/homermultitext/hmt-archive/master/releases-cex/hmt-2024c.cex"
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0012/tlg001/{}"
GRC = SRC / "tlg0012.tlg001.perseus-grc2.xml"
ENG = SRC / "tlg0012.tlg001.perseus-eng3.xml"
IIIF = ("https://www.homermultitext.org/iipsrv?IIIF=/project/homer/pyramidal/deepzoom/hmt/vaimg/2017a/"
        "{}.tif/full/1024,/0/default.jpg")
TEI = "{http://www.tei-c.org/ns/1.0}"
TODAY = "2026-11-12"

# Lines in the HMT diplomatic edition that its page index leaves out and whose
# neighbours are on different pages: placed by reading the photographs.
PLACED_BY_IMAGE = {
    "11.275": ("142v", "last line of fol. 142v, below 11.274 (ἤϋσεν δὲ διαπρύσιον Δαναοῖσι γεγωνώς); fol. 143r begins with 11.276"),
    "16.276-300": ("211v", "fol. 211v, which the HMT index omits, holds 25 lines from ἒν δ' ἔπεσον Τρώεσσιν ἀολλέες (16.276) to καὶ νάπαι οὐρανόθεν δ' ἄρ ὑπερράγη ἄσπετος αἰθήρ (16.300)"),
    "16.401": ("213v", "26th and last line of fol. 213v (δούπησεν δὲ πεσών· ὁ δὲ Θέστορα Ἤνοπος υἱὸν); fol. 214r begins with 16.402"),
    "16.627-628": ("218r", "last two lines of fol. 218r (Μηριόνη τί σὺ ταῦτα ... / ὦ πέπον οὔ τοι Τρῶες ...); fol. 218v begins with 16.629"),
    "16.704-705": ("219v", "last two lines of fol. 219v (χείρεσσ' ἀθανάτῃσι ... / ἀλλ' ὅτε δὴ τὸ τέταρτον ...); fol. 220r begins with 16.706"),
    "18.604_605": ("250v", "last line of fol. 250v (τερπόμενοι· δοιὼ δὲ κυβιστητῆρε κατ' αὐτοὺς); fol. 251r begins with 18.606"),
    "18.617": ("251r", "last line of book 18 on fol. 251r (τεύχεα μαρμαίροντα παρ' Ἡφαίστοιο φέρουσα), above the end ornament"),
}

# English cut at Murray's sentence ends instead of his five-line marks (QC 2026-11-12): the English of
# the page (book, folio) begins with the sentence that starts with the phrase (its occurrence in the
# book's English, counted from 0), which renders the given line. The note goes into the scan_note of
# that page and of the page before it.
ENGLISH_CUTS = {
    (13, "172r"): ("Howbeit Idomeneus, looking steadily", 0, 404,
                   "Murray's sentence for 13.404-410 (Howbeit Idomeneus ... grazed thereon.) runs across the break between "
                   "fol. 171v (Greek to 13.406) and fol. 172r (Greek from 13.407); it is given whole with fol. 172r, so the "
                   "English of fol. 171v ends with 13.403 and that of fol. 172r begins with 13.404."),
    (13, "172v"): ("Then the dear son of Aesyetes", 0, 427,
                   "Murray's next sentence, for 13.427-441 (Then the dear son of Aesyetes ... cloven about the spear.), runs "
                   "across the break between fol. 172r (Greek to 13.432) and fol. 172v (Greek from 13.433); it is given whole "
                   "with fol. 172v, so the English of fol. 172r ends with 13.426 and that of fol. 172v begins with 13.427."),
}

# Corrections to venetus_visual_checks.json entries (they replace the stored text).
VISUAL_CHECK_FIXES = {
    "13:172r": ("first line 13.407 (‹δινωτὴν φορέεσκε›) and last line of the column 13.432 (‹ἰδὲ φρεσί· τοὔνεκα καί μιν›) "
                "read on the photograph; the column has 25 lines, because 13.422 (‹μηκιστεὺς ἐχίοιο πάϊς καὶ δῖος ἀλάστωρ›) "
                "is not written in it: the scribe left it out between 13.421 and 13.423 and wrote it alone at the foot of the "
                "page, below the last line of the column (rechecked 2026-11-12)."),
}
# Corrections to the "placed on this page by ..." wording for single lines.
PLACED_NOTE_FIXES = {
    "13.422": ("Line 13.422 is not in that index; it is on this page, written alone at the foot of the page below the "
               "column (the scribe left it out between 13.421 and 13.423); the Greek above gives it in its place in the "
               "line order, as the Homer Multitext edition does."),
}

# Pages whose first and last lines were read on the photograph (2026-11-12),
# one or more per book; text as read.
CHECKED_ON_IMAGE = {}  # filled from data/sources/qc-sinaiticus-venetus/venetus_visual_checks.json


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------
def fetch(url, dest):
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TheosisLibrary QC)"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    return dest


def cex_path():
    for p in CEX_PATHS:
        if p.exists():
            return p
    return fetch(CEX_URL, CEX_PATHS[1])


def load_hmt():
    dip = collections.OrderedDict()   # "1.1" -> text, manuscript order
    dse = {}                          # "1.1" -> (image, folio, roi)
    codex = {}                        # "12r" -> (sequence, default image)
    rx = re.compile(r"^urn:cts:greekLit:tlg0012\.tlg001\.msA:([^|]+)\|urn:cite2:hmt:vaimg\.2017a:([^@|]+)@([^|]*)\|urn:cite2:hmt:msA\.v1:(\w+)$")
    cx = re.compile(r"^(-?\d+)\|urn:cite2:hmt:msA\.v1:(\w+)\|(?:recto|verso)\|[^|]*\|urn:cite2:hmt:vaimg\.2017a:(\w+)")
    with cex_path().open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("urn:cts:greekLit:tlg0012.tlg001.msA.diplomatic:"):
                k, t = line.split("|", 1)
                dip[k.rsplit(":", 1)[1]] = t.strip()
                continue
            m = rx.match(line)
            if m:
                dse.setdefault(m.group(1), (m.group(2), m.group(4), m.group(3)))
                continue
            m = cx.match(line)
            if m:
                codex[m.group(2)] = (int(m.group(1)), m.group(3))
    return dip, dse, codex


def load_ma():
    fetch(PERSEUS.format(GRC.name), GRC)
    root = ET.parse(GRC).getroot()
    out = {}
    for div in root.iter(TEI + "div"):
        if div.get("subtype") == "Book":
            lines = {}
            for l in div.iter(TEI + "l"):
                txt = re.sub(r"\s+", " ", "".join(l.itertext())).strip()
                lines[int(l.get("n"))] = txt
            out[int(div.get("n"))] = lines
    return out


def load_murray():
    """book -> list of atoms: ("m", n) line mark, ("p",) paragraph break, ("t", text)."""
    fetch(PERSEUS.format(ENG.name), ENG)
    root = ET.parse(ENG).getroot()
    books = {}

    def walk(el, atoms, depth):
        tag = el.tag.replace(TEI, "")
        if tag == "note":
            if el.tail:
                atoms.append(("t", el.tail))
            return
        if tag == "div" and el.get("subtype") == "card":
            atoms.append(("p",))
            atoms.append(("m", int(el.get("n"))))
        if tag == "p":
            atoms.append(("p",))
        if tag == "milestone" and el.get("unit") == "line":
            atoms.append(("m", int(el.get("n"))))
        if tag == "quote":
            atoms.append(("t", "“" if depth % 2 == 0 else "‘"))
        if el.text and tag not in ("milestone",):
            atoms.append(("t", el.text))
        for ch in el:
            walk(ch, atoms, depth + (1 if tag == "quote" else 0))
        if tag == "quote":
            atoms.append(("t", "”" if depth % 2 == 0 else "’"))
        if el.tail and tag != "div":
            atoms.append(("t", el.tail))

    for div in root.iter(TEI + "div"):
        if div.get("subtype") == "book":
            atoms = []
            for ch in div:
                walk(ch, atoms, 0)
            # keep only increasing line marks (Perseus has two out-of-order marks:
            # book 13 "825" after 830, book 22 card "224" after mark 225)
            clean, last, dropped = [], 0, []
            for a in atoms:
                if a[0] == "m":
                    if a[1] <= last:
                        if a[1] != last:
                            dropped.append(a[1])
                        continue
                    last = a[1]
                clean.append(a)
            books[int(div.get("n"))] = (clean, dropped)
    return books


# ---------------------------------------------------------------------------
# Book 1 English: the Perseus "Murray" Book 1 is not the 1924 text. It is a
# later modernised revision ("The wrath sing, goddess, of Peleus' son ...",
# "you" throughout), whereas the 1924 Loeb reads "The wrath do thou sing, O
# goddess, of Peleus' son, Achilles, that baneful wrath ..." (archive.org
# iliadmurray01homeuoft, printed p. 3). Books 2-24 in Perseus match the 1924
# printing. Until the 1924 Book 1 is transcribed, Book 1 keeps Samuel Butler's
# prose (1898, Project Gutenberg #2199, public domain), now cut at each page
# break of Venetus A where Butler's English for the page's first line begins,
# found by reading Butler against the Greek. Butler gives no line numbers, so
# only the first line of each section is marked.
# (start line of the page, words where Butler's English for it begins, occurrence, English start line)
BUTLER_BOOK1_CUTS = [
    (26, "“Old man,” said he, “let me not find you", 0, 26),
    (51, "but presently he aimed his shafts", 0, 51),
    (76, "I will therefore do so;", 0, 76),
    (101, "With these words he sat down, and Agamemnon rose", 0, 101),
    (126, "we cannot disallow the awards", 0, 126),
    (151, "either on foray or in open fighting?", 0, 151),
    (176, "There is no king here so hateful to me", 0, 176),
    (201, "“Why are you here,” said he,", 0, 201),
    (226, "you never dare to go out with the host", 0, 226),
    (251, "Two generations of men born and bred in Pylos", 0, 250),
    (277, "and you, Achilles, strive not further", 0, 277),
    (302, "Try, that others may see;", 0, 302),
    (327, "whereon they went their way sorrowfully", 0, 327),
    (352, "“Mother,” he cried, “you bore me", 0, 352),
    (377, "were for respecting the priest", 1, 377),
    (402, "by calling to Olympus the hundred-handed", 0, 402),
    (427, "and will beseech him; nor do I doubt", 0, 427),
    (452, "and holy Cilla, and rulest Tenedos with thy might. Even", 0, 452),
    (477, "and when the child of morning, rosy-fingered Dawn,", 0, 477),
    (502, "and besought him, saying:—", 0, 502),
    (527, "or fail to do what I say", 0, 527),
    (552, "“Dread son of Saturn,” answered Juno", 0, 551),
    (577, "Let me then advise my mother", 0, 577),
    (602, "Thus through the livelong day to the going down of the sun", 0, 601),
]
BUTLER_NOTES = {
    250: "Butler renders lines 250-252 in one sentence (“Two generations of men born and bred in Pylos had passed away under his rule”), so the English here begins with line 250",
    551: "Butler joins line 551 (“answered Juno”) to the first words of 552, so the English here begins with line 551",
    601: "Butler's sentence for lines 601-602 (“Thus through the livelong day to the going down of the sun they feasted”) begins with line 601",
}
PG_BUTLER = SRC / "pg2199.txt"


def butler_book1():
    """paragraphs of Butler's Book I (without his argument line) as one string with \n\n between paragraphs."""
    fetch("https://www.gutenberg.org/cache/epub/2199/pg2199.txt", PG_BUTLER)
    t = PG_BUTLER.read_text(encoding="utf-8")
    a = t.index("BOOK I.\n\n\n")
    b = t.index("BOOK II.", a)
    paras = [re.sub(r"\s+", " ", x).strip() for x in t[a:b].split("\n\n") if x.strip()]
    paras = paras[2:]  # drop the heading and Butler's summary of the book
    return "\n\n".join(paras)


def butler_segments():
    text = butler_book1()
    cuts = [0]
    for line, words, occ, eline in BUTLER_BOOK1_CUTS:
        pos = -1
        for _ in range(occ + 1):
            pos = text.find(words, pos + 1)
        if pos < 0:
            raise SystemExit(f"Butler anchor not found: {words}")
        cuts.append(pos)
    if cuts != sorted(cuts):
        raise SystemExit("Butler anchors out of order")
    cuts.append(len(text))
    segs = []
    starts = [1] + [c[3] for c in BUTLER_BOOK1_CUTS]
    for i in range(len(cuts) - 1):
        chunk = text[cuts[i]:cuts[i + 1]].strip()
        paras = [x.strip() for x in chunk.split("\n\n") if x.strip()]
        html = "".join(f"<p>{'<sup>%d</sup>' % starts[i] if k == 0 else ''}{x}</p>" for k, x in enumerate(paras))
        segs.append((starts[i], (starts[i + 1] - 1) if i + 1 < len(starts) else 611, html))
    return segs, text


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------
def line_numbers(lid):
    """'1.12' -> [12]; '18.604_605' -> [604, 605]; '14.147a' -> [147]; '6.386del' -> [] (a deleted repeat)."""
    rest = lid.split(".", 1)[1]
    if rest.endswith("del") or rest == "title":
        return []
    return [int(x) for x in re.findall(r"\d+", rest)]


def expand_placed():
    out = {}
    for key, (folio, why) in PLACED_BY_IMAGE.items():
        b, rng = key.split(".", 1)
        if re.fullmatch(r"\d+-\d+", rng):
            a, z = map(int, rng.split("-"))
            for n in range(a, z + 1):
                out[f"{b}.{n}"] = (folio, why)
        else:
            out[key] = (folio, why)
    return out


def assign_pages(dip, dse):
    placed = expand_placed()
    order = list(dip)
    page, how = {}, {}
    for i, lid in enumerate(order):
        if lid in dse:
            page[lid], how[lid] = dse[lid][1], "index"
        elif lid in placed:
            page[lid], how[lid] = placed[lid][0], "image: " + placed[lid][1]
    for i, lid in enumerate(order):
        if lid in page:
            continue
        prev = next((order[j] for j in range(i - 1, -1, -1) if order[j] in dse), None)
        nxt = next((order[j] for j in range(i + 1, len(order)) if order[j] in dse), None)
        if prev and nxt and dse[prev][1] == dse[nxt][1]:
            page[lid] = dse[prev][1]
            how[lid] = f"order: between {prev} and {nxt}, both on this page"
        else:
            raise SystemExit(f"cannot place {lid}: neighbours {prev} ({dse.get(prev, [None, None])[1]}) and {nxt}")
    return page, how


def image_for(folio, dse, codex, lines):
    """the photograph the HMT index uses for this page (most of its lines), else the codex default."""
    c = collections.Counter(dse[l][0] for l in lines if l in dse)
    ids = [i for i, _ in c.most_common()] + [codex[folio][1]]
    for i in ids:
        if (IMG_DIR / f"venetus-a-{i}.jpg").exists():
            return i
    i = ids[0]
    dest = IMG_DIR / f"venetus-a-{i}.jpg"
    fetch(IIIF.format(i), dest)
    return i


def folio_label(f):
    return f"fol. {f}"


def build_book(book, dip, dse, codex, page, how, ma, murray):
    lids = [l for l in dip if l.split(".")[0] == str(book) and not l.endswith(".title")]
    idx_only = [l for l in dse if l.split(".")[0] == str(book) and l not in dip and not l.endswith(".title")]
    groups = collections.OrderedDict()
    for l in lids:
        groups.setdefault(page[l], []).append(l)
    for l in idx_only:
        groups.setdefault(dse[l][1], [])
    folios = sorted(groups, key=lambda f: codex[f][0])
    # edition lines -> page: the page of the manuscript line with the largest number <= n
    ms_num = {}
    for f in folios:
        for l in groups[f]:
            for n in line_numbers(l):
                ms_num.setdefault(n, f)
    for l in idx_only:
        for n in line_numbers(l):
            ms_num.setdefault(n, dse[l][1])
    ed_lines = sorted(ma[book])
    ed_page = {}
    for n in ed_lines:
        cands = [m for m in ms_num if m <= n]
        ed_page[n] = ms_num[max(cands)] if cands else folios[0]
    absent = [n for n in ed_lines if n not in ms_num]
    # Murray blocks
    atoms, dropped = murray[book]
    marks = [a[1] for a in atoms if a[0] == "m"]
    last_line = ed_lines[-1]
    blocks = [(m, (marks[i + 1] - 1) if i + 1 < len(marks) else last_line) for i, m in enumerate(marks)]
    owner = {}
    for (a, z) in blocks:
        cnt = collections.Counter(ed_page[n] for n in range(a, z + 1) if n in ed_page)
        best = max(cnt.values())
        owner[a] = min((f for f, c in cnt.items() if c == best), key=lambda f: codex[f][0])
    # every page gets at least one block
    for f in folios:
        if f not in owner.values():
            cands = []
            for (a, z) in blocks:
                ov = sum(1 for n in range(a, z + 1) if ed_page.get(n) == f)
                if ov and list(owner.values()).count(owner[a]) > 1:
                    cands.append((ov, -a, a))
            if not cands:
                raise SystemExit(f"book {book}: page {f} gets no English block")
            owner[max(cands)[2]] = f
    # blocks of a page must be contiguous
    seq = [owner[a] for a, _ in blocks]
    for f in folios:
        idx = [i for i, x in enumerate(seq) if x == f]
        if idx and idx != list(range(idx[0], idx[-1] + 1)):
            raise SystemExit(f"book {book}: English blocks of {f} not contiguous")
    # render English per page
    flat = []
    cur = None
    for a in atoms:
        if a[0] == "m":
            cur = owner[a[1]]
        if cur is None:
            continue
        flat.append([cur, a])
    # sentence cuts (ENGLISH_CUTS): the page's English starts at the sentence that begins with the phrase
    cut_start = {}
    for (bk, fol), (phrase, occ, start, _note) in ENGLISH_CUTS.items():
        if bk != book:
            continue
        hits = [i for i, (_, a) in enumerate(flat) if a[0] == "t" and phrase in a[1]]
        i = hits[occ]
        a = flat[i][1]
        k = a[1].index(phrase)
        new = ([[flat[i][0], ("t", a[1][:k])]] if a[1][:k] else []) + [[fol, ("m", start)], [fol, ("t", a[1][k:])]]
        flat[i:i + 1] = new
        j = i + (1 if a[1][:k] else 0)            # first atom of the page's English
        fi = folios.index(fol)
        prev, nxt = folios[fi - 1], (folios[fi + 1] if fi + 1 < len(folios) else None)
        for x in range(len(flat)):
            if x < j and flat[x][0] == fol:
                flat[x][0] = prev
            elif x >= j and flat[x][0] == prev:
                flat[x][0] = fol
            if nxt and x > j and flat[x][0] == nxt:
                break
        cut_start[fol] = start
    eng = collections.defaultdict(list)
    for fol, a in flat:
        eng[fol].append(a)
    # drop a block mark left at the very end of a page by a cut
    for fol in eng:
        while eng[fol] and eng[fol][-1][0] in ("m", "p"):
            eng[fol].pop()
    sections = []
    for fi, f in enumerate(folios):
        ms = groups[f]
        ed = sorted(n for n in ed_lines if ed_page[n] == f)
        img = image_for(f, dse, codex, ms)
        my_blocks = [(a, z) for (a, z) in blocks if owner[a] == f]
        e_from, e_to = my_blocks[0][0], my_blocks[-1][1]
        if f in cut_start:
            e_from = cut_start[f]
        if fi + 1 < len(folios) and folios[fi + 1] in cut_start:
            e_to = cut_start[folios[fi + 1]] - 1
        cut_notes = []
        if f in cut_start:
            cut_notes.append(ENGLISH_CUTS[(book, f)][3])
        if fi + 1 < len(folios) and folios[fi + 1] in cut_start:
            cut_notes.append(ENGLISH_CUTS[(book, folios[fi + 1])][3])
        sections.append({"folio": f, "image": img, "ms": ms, "ed": ed, "blocks": my_blocks, "cut_notes": cut_notes,
                         "eng_atoms": eng[f], "absent": [n for n in absent if ed_page[n] == f],
                         "idx_only": [l for l in idx_only if dse[l][1] == f],
                         "e_range": (e_from, e_to)})
    return sections, absent, dropped


def render_english(atoms):
    paras, cur = [], ""
    for a in atoms:
        if a[0] == "p":
            # a paragraph starts; line marks already collected stay with it
            if re.sub(r"<sup>\d+</sup>", "", cur).strip():
                paras.append(cur)
                cur = ""
        elif a[0] == "m":
            cur += f" <sup>{a[1]}</sup>"
        else:
            cur += a[1]
    if cur.strip():
        paras.append(cur)
    out = []
    for p in paras:
        p = re.sub(r"\s+", " ", p).strip()
        p = re.sub(r"\s+([,.;:!?”’])", r"\1", p)
        p = re.sub(r"</sup>\s+", "</sup>", p)
        p = re.sub(r"([“‘])\s+", r"\1", p)
        if re.sub(r"<sup>\d+</sup>", "", p).strip():
            out.append(f"<p>{p}</p>")
    return "".join(out)


def first_words(t, n=5):
    w = t.split()
    return " ".join(w[:n])


def last_words(t, n=5):
    w = t.split()
    return " ".join(w[-n:])


def ranges(nums):
    out, s, p = [], None, None
    for n in nums:
        if s is None:
            s = p = n
        elif n == p + 1:
            p = n
        else:
            out.append((s, p))
            s = p = n
    if s is not None:
        out.append((s, p))
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def load_visual_checks():
    p = OUT / "venetus_visual_checks.json"
    return json.loads(p.read_text()) if p.exists() else {}


def build(dry=False):
    dip, dse, codex = load_hmt()
    page, how = assign_pages(dip, dse)
    ma = load_ma()
    murray = load_murray()
    checks = load_visual_checks()
    rows, table = [], {}
    for book in range(1, 25):
        path = PUB / f"verified-venetus-iliad-{book}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        secs, absent, dropped = build_book(book, dip, dse, codex, page, how, ma, murray)
        butler = None
        if book == 1:
            butler, _ = butler_segments()
            if len(butler) != len(secs):
                raise SystemExit("Book 1: Butler segments do not match pages")
        out = []
        for si, s in enumerate(secs):
            f, ms, ed = s["folio"], s["ms"], s["ed"]
            texted = [l for l in ms if dip[l]]
            lab = lambda l: l.split(".", 1)[1].replace("_", "-")
            greek = "<br>".join(f"<sup>{lab(l)}</sup>{dip[l]}" for l in texted)
            edition = "<br>".join(f"<sup>{n}</sup>{ma[book][n]}" for n in ed)
            a, z = ed[0], ed[-1]
            ea, ez = s["e_range"]
            if butler:
                ea, ez, eng_html = butler[si]
            else:
                eng_html = render_english(s["eng_atoms"])
            nums = [n for l in ms for n in line_numbers(l)]
            notes = [f"Venetus A {folio_label(f)} (photograph {s['image']}): Iliad {book}.{a}-{z}"
                     f"{'' if not texted else f', {len(texted)} lines of the manuscript'}, begins ‹{first_words(dip[texted[0]])}›, "
                     f"ends ‹{last_words(dip[texted[-1]])}›. Page of each line from the Homer Multitext 2024c index of lines to pages."]
            placed = [l for l in ms if how.get(l, "index") != "index"]
            for l in placed:
                notes.append(PLACED_NOTE_FIXES.get(l, f"Line {l} is not in that index; placed on this page by {how[l]}."))
            if s["idx_only"]:
                notes.append(f"Line{'s' if len(s['idx_only']) > 1 else ''} {', '.join(s['idx_only'])} "
                             f"{'are' if len(s['idx_only']) > 1 else 'is'} indexed on this page but "
                             f"{'have' if len(s['idx_only']) > 1 else 'has'} no text in the HMT diplomatic edition; "
                             f"Monro & Allen's text is in the edition text.")
            dele = [l for l in ms if l.endswith("del")]
            for l in dele:
                notes.append(f"{l}: the HMT edition cites this line as deleted in the manuscript; its words repeat line {l.split('.')[0]}.{''.join(re.findall(r'\d+', l.split('.')[1]))}.")
            plus = [l for l in ms if re.search(r"\d[a-z]$", l)]
            for l in plus:
                notes.append(f"{l} is a line of Venetus A that Monro & Allen do not number.")
            if nums != sorted(nums):
                notes.append("The manuscript has these lines in the order " + ", ".join(lab(l) for l in ms) + ".")
            if s["absent"]:
                notes.append(f"Line{'s' if len(s['absent']) > 1 else ''} {book}.{ranges(s['absent'])} of the standard text "
                             f"{'are' if len(s['absent']) > 1 else 'is'} not in Venetus A; "
                             f"{'they are' if len(s['absent']) > 1 else 'it is'} in the edition text (Monro & Allen) and the English.")
            blocks = ", ".join(f"{x}-{y}" if x != y else f"{x}" for x, y in s["blocks"])
            off = []
            if ea != a:
                off.append(f"begins at line {ea}")
            if ez != z:
                off.append(f"ends at line {ez}")
            if butler:
                notes.append(f"English (Butler): lines {book}.{ea}-{ez}; cut where Butler's English for the first line of "
                             f"the page begins, found by reading his English against the Greek"
                             + (f" ({BUTLER_NOTES[ea]})." if ea in BUTLER_NOTES else "."))
            elif s["cut_notes"]:
                notes.append(f"English (Murray): lines {book}.{ea}-{ez}. " + " ".join(s["cut_notes"])
                             + (" At the page's other break the English follows Murray's five-line marks (a block that "
                                "crosses the break goes with the page holding most of its lines)."
                                if len(s["cut_notes"]) == 1 else ""))
            else:
                notes.append(f"English (Murray): lines {book}.{ea}-{ez}, in his blocks {blocks}. Murray marks every fifth line and "
                             f"each paragraph; a block that crosses the page break goes with the page holding most of its lines"
                             + (f", so the English here {' and '.join(off)}." if off else "."))
            ck = VISUAL_CHECK_FIXES.get(f"{book}:{f}", checks.get(f"{book}:{f}"))
            if ck:
                notes.append(f"Checked on the image: {ck}")
            out.append({
                "section": f"{book}.{a}-{z}",
                "original_ref": f"Iliad {book}.{a}-{z}; Venetus A {folio_label(f)}; English ({'Butler' if butler else 'Murray'}) {book}.{ea}-{ez}",
                "original_text": greek,
                "edition_text": edition,
                "text": eng_html,
                "scan_pages": [f"venetus-a/venetus-a-{s['image']}.jpg"],
                "scan_note": " ".join(notes),
            })
            table[f"{book}:{f}"] = {"lines": [l for l in ms], "edition": [ed[0], ed[-1]], "english": [ea, ez],
                                    "image": s["image"]}
        first_f, last_f = secs[0]["folio"], secs[-1]["folio"]
        n_ma = len(ma[book])
        placed_book = sorted({how[l] for l in dip if l.split(".")[0] == str(book) and how.get(l, "index").startswith("image")})
        intro = (f"<p>Book {book} of the <em>Iliad</em> ({n_ma} lines in Monro and Allen's edition) as written in Venetus A "
                 f"(Venice, Biblioteca Nazionale Marciana, Marc. gr. Z. 454 = 822), the oldest complete manuscript of the "
                 f"Iliad, copied in the 10th century with the text in the centre of each page and the scholia around it. "
                 f"This book is on fol. {first_f}-{last_f}; each section below is one page of the manuscript and links "
                 f"that page.</p>"
                 f"<p>The page of every line comes from the Homer Multitext Project's index of the manuscript (release 2024c), "
                 f"which records where each line stands on the page photographs."
                 f"{' Lines missing from that index were placed by reading the photographs; each case is described in its section.' if placed_book else ''}</p>"
                 f"<p><strong>Greek:</strong> the manuscript's own text, from the Homer Multitext diplomatic edition of "
                 f"Venetus A, with its accents, punctuation and signs as given there. The Oxford text of Monro and Allen "
                 f"(1920) is given for comparison.</p>"
                 f"<p><strong>English:</strong> A. T. Murray's translation (Loeb Classical Library, 1924). Murray numbers "
                 f"every fifth line and starts a new paragraph at many other lines; the English is divided only at those "
                 f"points, and a passage that runs across a page break goes with the page that holds most of its lines. "
                 f"The English of a section can therefore begin or end a few lines away from the Greek; each section gives "
                 f"its exact English line range.</p>")
        if butler:
            intro = intro.replace(intro[intro.index("<p><strong>English:</strong>"):], "")
            intro += ("<p><strong>English:</strong> Samuel Butler's prose translation (1898). The Perseus text labelled "
                      "as A. T. Murray's 1924 Loeb translation, used for Books 2-24, has a later revised translation in "
                      "Book 1 instead of the 1924 text, so it is not used here. Butler's English is cut at each page "
                      "break where his rendering of the page's first line begins; each section gives its English line "
                      "range. Butler gives no line numbers, so only the first line of each section is numbered.</p>")
        if absent:
            one = len(absent) == 1
            intro += (f"<p><strong>Not in Venetus A:</strong> {'line' if one else 'lines'} {book}.{ranges(absent)} of the "
                      f"standard text {'is' if one else 'are'} not "
                      f"in this manuscript. {'It is' if one else 'They are'} shown in the Monro and Allen text and in the English of the page "
                      f"where {'it' if one else 'they'} would stand.</p>")
        d["translation"] = out
        d["language"] = "Ancient Greek (Venetus A) / English (A. T. Murray)"
        d["source"] = ("Venetus A (Marc. gr. Z. 454) page photographs and diplomatic text, Homer Multitext Project "
                       "(release 2024c) + Monro & Allen (Oxford 1920, Perseus) + A. T. Murray, Loeb (1924, Perseus)")
        d["description"] = (f"Book {book} of Homer's Iliad page by page in Venetus A (10th century, Venice): "
                            f"{len(out)} pages, fol. {first_f}-{last_f}, each with the manuscript's own Greek text "
                            f"(Homer Multitext edition), Monro and Allen's text for comparison, and A. T. Murray's 1924 English.")
        d["introduction"] = intro
        tn = ["Greek: Homer Multitext Project, diplomatic edition of the Venetus A text (release 2024c); "
              "edition text: D. B. Monro and T. W. Allen, Homeri Opera (Oxford, 1908-1920), via Perseus.",
              "English: A. T. Murray, Homer: The Iliad (Loeb Classical Library, 1924-1925), via Perseus; his footnotes "
              "are omitted, and speeches, marked as quotations in the Perseus text, are shown in quotation marks."]
        if butler:
            tn[1] = ("English: Samuel Butler, The Iliad of Homer rendered into English prose (London: Longmans, Green, "
                     "1898), Project Gutenberg #2199; his summary line at the head of the book is omitted. A. T. Murray's "
                     "1924 Loeb translation is used for Books 2-24; for Book 1 the Perseus text has a later revision of "
                     "Murray, not the 1924 text (which begins “The wrath do thou sing, O goddess”).")
        if dropped and not butler:
            tn.append(f"The Perseus text of Murray has an out-of-order line mark in this book ({', '.join(map(str, dropped))}); "
                      f"it is not used to divide the English.")
        d["translator_notes"] = tn
        v = d["verification"]
        for k in ("scan_mapping", "translation_source", "translation_license"):
            v.pop(k, None)
        imgs = []
        for s in out:
            for p in s["scan_pages"]:
                if p not in imgs:
                    imgs.append(p)
        v.update({
            "scan_source": "Homer Multitext Project (homermultitext.org), photographs of Venetus A, collection urn:cite2:hmt:vaimg.2017a: (IIIF https://www.homermultitext.org/iipsrv)",
            "scan_license": "CC BY-SA (licence of the HMT Venetus A image collection, hmt-2024c release)",
            "scan_manuscript": "Venetus A, Venice, Biblioteca Nazionale Marciana, Marc. gr. Z. 454 (= 822), 10th century",
            "scan_mapping": ("Homer Multitext 2024c DSE index (urn:cite2:hmt:hmtdse.v1:all): each Iliad line of Venetus A to "
                             "its folio side and photograph; each section is the lines on one folio side. Lines missing "
                             "from the index: placed by the order of the text when the lines before and after are on the "
                             "same page, otherwise read on the photograph (noted in the section). First and last lines of "
                             "sample pages checked on the images (noted in the sections)."),
            "scan_mapping_urls": ["https://github.com/homermultitext/hmt-archive/blob/master/releases-cex/hmt-2024c.cex"],
            "scan_local_paths": imgs,
            "original_text_source": ("Homer Multitext Project, diplomatic edition of the Iliad in Venetus A "
                                     "(urn:cts:greekLit:tlg0012.tlg001.msA.diplomatic), release 2024c, "
                                     "https://github.com/homermultitext/hmt-archive/blob/master/releases-cex/hmt-2024c.cex"),
            "original_text_license": "CC BY-NC 4.0 (licence stated for the HMT 2024c release)",
            "primary_greek": "hmt_diplomatic",
            "edition_text_source": ("D. B. Monro and T. W. Allen, Homeri Opera, Oxford 1908-1920 (vols. 1-2, 3rd ed. 1920), "
                                    "Perseus canonical-greekLit tlg0012.tlg001.perseus-grc2, "
                                    "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0012/tlg001/tlg0012.tlg001.perseus-grc2.xml"),
            "edition_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": ("A. T. Murray, Homer: The Iliad, with an English Translation, Loeb Classical Library, "
                                   "2 vols., London: William Heinemann; New York: G. P. Putnam's Sons, 1924-1925; Perseus "
                                   "canonical-greekLit tlg0012.tlg001.perseus-eng3, "
                                   "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0012/tlg001/tlg0012.tlg001.perseus-eng3.xml"),
            "translation_license": ("public domain in the US (published 1924-1925, more than 95 years ago); Perseus digital "
                                    "text CC BY-SA 4.0"),
            "translator": "A. T. Murray (1924)",
            "english_division": ("At Murray's line marks (every fifth line and paragraph starts); a block crossing a page "
                                 "break goes with the page holding most of its lines; exact range per section."),
            "verified_date": TODAY,
        })
        if butler:
            v.update({
                "translation_source": "Samuel Butler, The Iliad of Homer rendered into English prose, London: Longmans, Green, 1898; Project Gutenberg #2199, https://www.gutenberg.org/ebooks/2199",
                "translation_license": "public domain (published 1898)",
                "translator": "Samuel Butler (1898)",
                "english_division": ("Cut at each page break where Butler's English for the page's first line begins, "
                                     "found by reading Butler against the Greek; exact range per section."),
            })
            d["language"] = "Ancient Greek (Venetus A) / English (Samuel Butler)"
            d["source"] = d["source"].replace("A. T. Murray, Loeb (1924, Perseus)", "Samuel Butler (1898, Project Gutenberg #2199)")
            d["description"] = d["description"].replace("A. T. Murray's 1924 English", "Samuel Butler's 1898 English")
        rows.append({"id": d["id"], "language": "Ancient Greek", "source": d["source"], "description": d["description"],
                     "scans_pages": [{"file": p, "caption": f"Venetus A, fol. {s['original_ref'].split('fol. ')[1].split(';')[0]}"}
                                     for s in out for p in s["scan_pages"]]})
        if not dry:
            path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"book {book}: {len(out)} sections, fol. {first_f}-{last_f}, not in Venetus A: {len(absent)} lines")
    (OUT / "venetus_texts_json_rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    (OUT / "venetus_pages.json").write_text(json.dumps(table, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------
def check():
    dip, dse, codex = load_hmt()
    page, how = assign_pages(dip, dse)
    ma = load_ma()
    murray = load_murray()
    probs = []
    for book in range(1, 25):
        d = json.loads((PUB / f"verified-venetus-iliad-{book}.json").read_text(encoding="utf-8"))
        seen_ed, seen_eng = [], []
        prev_end = 0
        for s in d["translation"]:
            labs = re.findall(r"<sup>([^<]+)</sup>", s["original_text"])
            lids = [f"{book}.{x.replace('-', '_')}" for x in labs]
            pages_needed = {page[l] for l in lids if l in page}
            listed = {re.search(r"(VA\w+?)\.jpg", p).group(1) for p in s["scan_pages"]}
            listed_f = {f for f, (sq, im) in codex.items() if im in listed} | {dse[l][1] for l in lids if l in dse and dse[l][0] in listed}
            for l in lids:
                if l not in page:
                    probs.append({"id": d["id"], "section": s["section"], "type": "line_without_page", "line": l})
            if len(pages_needed) != 1:
                probs.append({"id": d["id"], "section": s["section"], "type": "section_spans_pages", "pages": sorted(pages_needed)})
            if len(s["scan_pages"]) != 1:
                probs.append({"id": d["id"], "section": s["section"], "type": "not_one_image", "scan_pages": s["scan_pages"]})
            for f in pages_needed:
                if f not in listed_f:
                    probs.append({"id": d["id"], "section": s["section"], "type": "missing_page_with_section_text", "page": f})
            for p in s["scan_pages"]:
                if not (SCANS / p).exists() or (SCANS / p).stat().st_size < 10000:
                    probs.append({"id": d["id"], "section": s["section"], "type": "scan_file_missing", "file": p})
            for l, x in zip(lids, labs):
                if l in dip and dip[l] and f"<sup>{x}</sup>{dip[l]}" not in s["original_text"]:
                    probs.append({"id": d["id"], "section": s["section"], "type": "greek_not_verbatim", "line": l})
            ed = [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s.get("edition_text", ""))]
            seen_ed += ed
            eng = [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s["text"])]
            if not eng:
                probs.append({"id": d["id"], "section": s["section"], "type": "no_english"})
            else:
                if eng[0] < prev_end:
                    probs.append({"id": d["id"], "section": s["section"], "type": "english_overlap"})
                prev_end = eng[-1]
                m = re.search(r"English \((?:Murray|Butler)\) \d+\.(\d+)-(\d+)", s["original_ref"])
                if not m or int(m.group(1)) != eng[0]:
                    probs.append({"id": d["id"], "section": s["section"], "type": "english_range_label_wrong"})
                seen_eng += eng
        if seen_ed != sorted(ma[book]):
            probs.append({"id": d["id"], "section": None, "type": "edition_lines_not_complete_once",
                          "missing": sorted(set(ma[book]) - set(seen_ed))[:20]})
        marks = sorted({a[1] for a in murray[book][0] if a[0] == "m"}
                       | {v[2] for (bk, _f), v in ENGLISH_CUTS.items() if bk == book})   # + sentence-cut marks
        if book == 1:
            _, full = butler_segments()
            joined = " ".join(re.sub(r"<[^>]+>", " ", re.sub(r"<sup>\d+</sup>", "", s["text"])) for s in d["translation"])
            if re.sub(r"\s+", " ", joined).strip() != re.sub(r"\s+", " ", full).strip():
                probs.append({"id": d["id"], "section": None, "type": "butler_text_not_complete_once"})
        elif seen_eng != marks:
            probs.append({"id": d["id"], "section": None, "type": "murray_marks_not_complete_once"})
        ms_lines = [l for l in dip if l.split(".")[0] == str(book) and not l.endswith(".title") and dip[l]]
        shown = [f"{book}.{x.replace('-', '_')}" for s in d["translation"] for x in re.findall(r"<sup>([^<]+)</sup>", s["original_text"])]
        if sorted(shown) != sorted(ms_lines):
            probs.append({"id": d["id"], "section": None, "type": "manuscript_lines_not_complete_once",
                          "missing": sorted(set(ms_lines) - set(shown))[:20]})
    # the earlier audit's own test (qc_scan_audit.audit_venetus), run read-only
    sys.path.insert(0, str(ROOT / "scripts"))
    import qc_scan_audit as qa
    legacy, counts = [], collections.Counter()
    qa.generic_checks("venetus", legacy, counts)
    qa.audit_venetus(legacy, counts)
    for p in legacy:
        if p["type"] == "lines_not_in_hmt_dse_index":
            p["verdict"] = ("not a page error: lines the HMT index leaves out, placed by the order of the text or "
                            "read on the photograph (see the section's scan_note)")
        elif p["type"] == "missing_page_with_section_text" and set(p["missing_pages"]) == {"VA172RN_0343"}:
            p["verdict"] = ("not a page error: the HMT index gives line 13.281 the image of fol. 172r while placing it on "
                            "fol. 169v; the photograph of fol. 169v shows 13.281 as its first line")
        elif p["type"] == "listed_page_carries_none_of_section" and p.get("pages") == ["VA211VN_0713"]:
            p["verdict"] = ("not a page error: fol. 211v is missing from the HMT index; its 25 lines (16.276-300) "
                            "were read on the photograph")
        else:
            p["verdict"] = "open"
    out = {"problems": probs, "legacy_audit": legacy}
    (OUT / "venetus_check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"check: {len(probs)} problems {dict(collections.Counter(p['type'] for p in probs))}; "
          f"earlier audit: {dict(collections.Counter((p['type'], p['verdict'].split(':')[0]) for p in legacy))}")
    return probs


def crops(outdir, folios):
    from PIL import Image
    dip, dse, codex = load_hmt()
    page, how = assign_pages(dip, dse)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for f in folios:
        lines = [l for l in dip if page.get(l) == f and dip[l]]
        img = image_for(f, dse, codex, lines)
        im = Image.open(IMG_DIR / f"venetus-a-{img}.jpg")
        W, H = im.size
        parts = []
        for l, up in ((lines[0], True), (lines[-1], False)):
            if l not in dse:
                continue
            x, y, w, h = [float(v) for v in dse[l][2].split(",")]
            box = (max(0, x - 0.06) * W, max(0, y - h * (2.5 if up else 0.4)) * H, min(1, x + w + 0.1) * W,
                   min(1, y + h * (1.4 if up else 3.0)) * H)
            c = im.crop(tuple(int(v) for v in box))
            parts.append(c.resize((900, max(1, int(900 * c.size[1] / c.size[0])))))
        tot = sum(p.size[1] + 8 for p in parts)
        canvas = Image.new("RGB", (900, tot), "white")
        yy = 0
        for p in parts:
            canvas.paste(p, (0, yy))
            yy += p.size[1] + 8
        canvas.save(outdir / f"{f}.jpg", quality=85)
        print(f, img, "first:", lines[0], dip[lines[0]], "| last:", lines[-1], dip[lines[-1]])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "build":
        build(dry="--dry-run" in sys.argv)
    elif cmd == "check":
        check()
    elif cmd == "crops":
        crops(sys.argv[2], sys.argv[3:])
    else:
        raise SystemExit(__doc__)
