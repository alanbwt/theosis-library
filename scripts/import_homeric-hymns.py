#!/usr/bin/env python3
"""
import_homeric-hymns.py: the Homeric Hymns on Leiden, Universiteitsbibliotheek, BPG 33 H
(the "Moscow" manuscript, siglum M; first half of the 15th century), fols. 31r-50r.

M is the only manuscript of the Hymn to Demeter and the only one that preserves the end of the
Hymn to Dionysus (Hymn 1). It was found in Moscow in 1777 by C. F. Matthaei.

Chain of evidence
  1. SCAN     Leiden University Libraries, Digital Collections (IIIF v3), manifest
              https://digitalcollections.universiteitleiden.nl/iiif_manifest/item:1615207/manifest
              (cached in data/sources/homeric-hymns/leiden-bpg-33h-manifest.json); Public Domain Mark.
  2. MAPPING  The text is in two columns per page (a = left, b = right), 25-30 verses each.
              For every column the first and last verse were read on the page image (crops of the
              top and bottom rows, and full-column views where the text is irregular) and matched
              to the Greek; consecutive columns were checked for continuity. The library's
              catalogue gives the hymn-level folio ranges (31r-36r Demeter, 36r-40v Apollo,
              40v-46r Hermes, 46v-48v Aphrodite, 48v-50r minor hymns). A later hand has written
              verse numbers in the margins every five lines; they follow an older numbering and
              were used only as a cross-check. Results are in COLUMNS below.
  3. GREEK    H. G. Evelyn-White (Loeb, 1914), Perseus canonical-greekLit tlg0013.tlg001-018
              perseus-grc2 (CC BY-SA 4.0). Text the edition marks as lost in M (<supplied>) is
              shown in square brackets. Lines numbered with letters (137a, 236a ...) are editorial
              supplements or variants and are left out.
  4. ENGLISH  H. G. Evelyn-White (1914, public domain), Perseus tlg0013.*.perseus-eng2, in blocks of
              about five lines; each block goes to the column holding the block's middle line (or,
              if that line is not in M, the first of its lines that is).

Usage:  python3 scripts/import_homeric-hymns.py [--force]   (--force re-downloads scans)
"""
import argparse
import io
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image

KEY = "homeric-hymns"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
GITHUB = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0013/"
MANIFEST = "https://digitalcollections.universiteitleiden.nl/iiif_manifest/item:1615207/manifest"
VIEWER = "https://digitalcollections.universiteitleiden.nl/view/item/1615207"
MS = "Leiden BPG 33 H"
MS_LONG = ("Leiden, Universiteitsbibliotheek, BPG 33 H (the 'Moscow' manuscript, M; paper, Greece?, first half of the "
           "15th century; found in Moscow in 1777 by C. F. Matthaei), Homeric Hymns on fols. 31r-50r")

HYMN_NAMES = {1: "To Dionysus", 2: "To Demeter", 3: "To Apollo", 4: "To Hermes", 5: "To Aphrodite",
              6: "To Aphrodite", 7: "To Dionysus", 8: "To Ares", 9: "To Artemis", 10: "To Aphrodite",
              11: "To Athena", 12: "To Hera", 13: "To Demeter", 14: "To the Mother of the Gods",
              15: "To Heracles the Lion-hearted", 16: "To Asclepius", 17: "To the Dioscuri", 18: "To Hermes"}

# Verified on the images. (folio, column, [(hymn, first, last), ...], note)
COLUMNS = [
    ("31r", "a", [(1, 10, 21), (2, 1, 12)], "Hymn 1 ends with verse 21; the red title of the Hymn to Demeter (faded) follows, then Demeter 1-12."),
    ("31r", "b", [(2, 13, 37)], ""),
    ("31v", "a", [(2, 38, 62)], ""),
    ("31v", "b", [(2, 63, 87)], ""),
    ("32r", "a", [(2, 88, 112)], ""),
    ("32r", "b", [(2, 113, 137)], ""),
    ("32v", "a", [(2, 138, 161)], "Line 137a of the Loeb text is not in the manuscript: 32r b ends with 137 and this column begins with 138."),
    ("32v", "b", [(2, 162, 186)], ""),
    ("33r", "a", [(2, 187, 211)], ""),
    ("33r", "b", [(2, 212, 236)], "The last verse (236) runs on to the word Δημήτηρ; editors take this as a sign that text is lost here, and the Loeb's 236a is a supplement that is not in the manuscript."),
    ("33v", "a", [(2, 237, 261)], ""),
    ("33v", "b", [(2, 262, 286)], ""),
    ("34r", "a", [(2, 287, 311)], ""),
    ("34r", "b", [(2, 312, 336)], ""),
    ("34v", "a", [(2, 337, 361)], ""),
    ("34v", "b", [(2, 362, 386)], ""),
    ("35r", "a", [(2, 387, 411)], "Folio 35 is badly damaged and repaired; most of this column is lost and survives only in fragments along the left margin. The words in square brackets are the editor's restorations, not on the page."),
    ("35r", "b", [(2, 412, 436)], ""),
    ("35v", "a", [(2, 437, 461)], ""),
    ("35v", "b", [(2, 462, 481)], "The upper part of this column is torn away and repaired; the ends of the first verses survive at the right. Text in square brackets is restored by the editor. Fragments of folio 35 are also mounted on a separate sheet (photographed by the library as 'pag. t.o. f035r')."),
    ("36r", "a", [(2, 482, 495), (3, 1, 10)], "The Hymn to Demeter ends with verse 495; a red title (faded) introduces the Hymn to Apollo."),
    ("36r", "b", [(3, 11, 22), (3, 74, 86)], "The manuscript passes from Apollo 22 straight to 74: verses 23-73 are not in M (a note in the right margin marks the place)."),
    ("36v", "a", [(3, 87, 112)], ""),
    ("36v", "b", [(3, 113, 140)], "Verses 136-138, bracketed by the editor as an alternative version of 139, are not in this manuscript; the column runs from 135 to 139."),
    ("37r", "a", [(3, 141, 165)], ""),
    ("37r", "b", [(3, 166, 190)], ""),
    ("37v", "a", [(3, 191, 216)], ""),
    ("37v", "b", [(3, 217, 243)], ""),
    ("38r", "a", [(3, 244, 269)], ""),
    ("38r", "b", [(3, 270, 295)], ""),
    ("38v", "a", [(3, 296, 321)], "Line 317a of the Loeb text (a supplement) is not in the manuscript."),
    ("38v", "b", [(3, 322, 347)], ""),
    ("39r", "a", [(3, 348, 372)], ""),
    ("39r", "b", [(3, 373, 394)], "The scribe wrote verses 376-378 twice (after 382 they are repeated before 383); the repetition is marked with χ in the margin. The column has 26 written lines for 22 verses."),
    ("39v", "a", [(3, 395, 420)], ""),
    ("39v", "b", [(3, 421, 446)], ""),
    ("40r", "a", [(3, 447, 472)], ""),
    ("40r", "b", [(3, 473, 498)], ""),
    ("40v", "a", [(3, 499, 524)], ""),
    ("40v", "b", [(3, 525, 546), (4, 1, 4)], "The Hymn to Apollo ends with verse 546; a red title (faded) introduces the Hymn to Hermes."),
    ("41r", "a", [(4, 5, 30)], ""),
    ("41r", "b", [(4, 31, 56)], ""),
    ("41v", "a", [(4, 57, 82)], ""),
    ("41v", "b", [(4, 83, 108)], ""),
    ("42r", "a", [(4, 109, 133)], ""),
    ("42r", "b", [(4, 134, 159)], ""),
    ("42v", "a", [(4, 160, 185)], ""),
    ("42v", "b", [(4, 186, 211)], ""),
    ("43r", "a", [(4, 212, 239)], ""),
    ("43r", "b", [(4, 240, 265)], ""),
    ("43v", "a", [(4, 266, 291)], ""),
    ("43v", "b", [(4, 292, 317)], ""),
    ("44r", "a", [(4, 318, 343)], ""),
    ("44r", "b", [(4, 344, 369)], ""),
    ("44v", "a", [(4, 370, 395)], ""),
    ("44v", "b", [(4, 396, 421)], ""),
    ("45r", "a", [(4, 422, 447)], ""),
    ("45r", "b", [(4, 448, 473)], ""),
    ("45v", "a", [(4, 474, 500)], "Verse 499 is not in the manuscript: the column passes from 498 to 500 (a χ stands above the last line)."),
    ("45v", "b", [(4, 501, 527)], "Line 526a of the Loeb text (a supplement) is not in the manuscript."),
    ("46r", "a", [(4, 528, 553)], ""),
    ("46r", "b", [(4, 554, 580)], "The Hymn to Hermes ends at the foot of the column."),
    ("46v", "a", [(5, 1, 25)], "The Hymn to Aphrodite begins at the head of the column with a large initial."),
    ("46v", "b", [(5, 26, 51)], ""),
    ("47r", "a", [(5, 52, 67), (5, 113, 122)], "The manuscript passes from Aphrodite 67 straight to 113: verses 68-112 are not in M (a later hand notes the verse numbers in the margin)."),
    ("47r", "b", [(5, 123, 147)], ""),
    ("47v", "a", [(5, 148, 173)], ""),
    ("47v", "b", [(5, 174, 199)], ""),
    ("48r", "a", [(5, 200, 225)], ""),
    ("48r", "b", [(5, 226, 251)], ""),
    ("48v", "a", [(5, 252, 277)], ""),
    ("48v", "b", [(5, 278, 293), (6, 1, 8)], "The Hymn to Aphrodite ends with verse 293; a red title (faded) introduces the short Hymn 6."),
    ("49r", "a", [(6, 9, 21), (7, 1, 12)], "Hymn 6 ends with verse 21; a red title (faded) introduces Hymn 7, To Dionysus."),
    ("49r", "b", [(7, 13, 38)], ""),
    ("49v", "a", [(7, 39, 59), (8, 1, 4)], "Hymn 7 ends with verse 59; red title, then Hymn 8, To Ares."),
    ("49v", "b", [(8, 5, 17), (9, 1, 9), (11, 1, 2)], "Hymn 8 ends; red titles introduce Hymn 9, To Artemis, and then the hymn to Athena (Hymn 11 in the modern numbering; in M it stands before Hymn 10)."),
    ("50r", "a", [(11, 3, 5), (10, 1, 6), (12, 1, 5), (13, 1, 3), (14, 1, 5)], "Four short hymns, each under its own red title: the end of Hymn 11, then 10, 12, 13 and the beginning of 14."),
    ("50r", "b", [(14, 6, 6), (15, 1, 9), (16, 1, 5), (17, 1, 5), (18, 1, 4)], "The last page: the end of Hymn 14, then Hymns 15, 16 and 17, and the first four verses of Hymn 18, To Hermes, where the manuscript breaks off (fol. 50v is blank)."),
]
# Edition lines that M passes over inside a mapped range (not shown in that column's Greek).
NOT_IN_M = {3: set(range(136, 139)), 4: {499}}

ENTRIES = [
    ("hymn-1-dionysus", [1], "Homeric Hymn 1, To Dionysus (the end)",
     "The opening hymn of the collection, to Dionysus, survives only in fragments. M preserves its last twelve verses (10-21): Zeus promises the god's honours and the singer takes his leave. Verses 1-9 of the Loeb text come from quotations in Diodorus and are not in this manuscript."),
    ("hymn-2-demeter", [2], "Homeric Hymn 2, To Demeter",
     "Hades carries off Persephone; Demeter searches for her, nurses the child Demophon at Eleusis, withholds the harvest, and wins her daughter back for two thirds of each year. The hymn ends with the founding of the Eleusinian Mysteries. This manuscript is its only witness."),
    ("hymn-3-apollo", [3], "Homeric Hymn 3, To Apollo",
     "The birth of Apollo on Delos and the founding of his oracle at Delphi, with the slaying of the serpent and the Cretan sailors who become his priests."),
    ("hymn-4-hermes", [4], "Homeric Hymn 4, To Hermes",
     "Hermes is born at dawn, invents the lyre by noon and steals Apollo's cattle by night; the brothers are reconciled when he gives Apollo the lyre."),
    ("hymn-5-aphrodite", [5], "Homeric Hymn 5, To Aphrodite",
     "Zeus makes Aphrodite fall in love with the mortal Anchises; she comes to him on Mount Ida disguised as a girl and foretells the birth of Aeneas."),
    ("hymns-6-18", [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], "Homeric Hymns 6-18 (the shorter hymns)",
     "Thirteen short hymns, to Aphrodite, Dionysus (the pirates turned into dolphins), Ares, Artemis, Athena, Hera, Demeter, the Mother of the Gods, Heracles, Asclepius, the Dioscuri and Hermes, in the order in which M copies them."),
]


def fetch(url, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) > 20000:
                return data
        except Exception:
            pass
        time.sleep(3 + 4 * i)
    raise RuntimeError(f"download failed: {url}")


def scan_name(folio):
    return f"leiden-bpg-33h-f{folio}.jpg"


def iiif_services():
    d = json.loads((SRC / "leiden-bpg-33h-manifest.json").read_text(encoding="utf-8"))
    out = {}
    for c in d["items"]:
        lab = list(c["label"].values())[0][0]
        m = re.fullmatch(r"\d+ - f0*(\d+[rv])", lab)
        if m:
            svc = c["items"][0]["items"][0]["body"]["service"][0]
            out[m.group(1)] = svc.get("@id") or svc.get("id")
    return out


def get_scan(folio, services, force=False):
    path = SCAN_DIR / scan_name(folio)
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"{services[folio]}/full/1600,/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_greek(e):
    """Text of a TEI <l>: notes dropped, <supplied>/<surplus>/<del> in brackets, <choice> -> <corr>, <gap> -> …"""
    s = esc(e.text or "")
    for c in e:
        tag = c.tag.replace(TEI, "")
        inner = render_greek(c)
        if tag == "supplied":
            s += f'<span class="lacuna">[{inner}]</span>'
        elif tag in ("del", "surplus"):
            s += f"[{inner}]"
        elif tag == "gap":
            s += "…"
        elif tag == "choice":
            corr = c.find(f"{TEI}corr")
            s += render_greek(corr) if corr is not None else inner
        elif tag in ("note", "milestone"):
            pass
        else:
            s += inner
        s += esc(c.tail or "")
    return s


def greek(h):
    body = ET.parse(SRC / f"tlg0013.tlg{h:03d}.perseus-grc2.xml").getroot().find(f".//{TEI}body")
    out = {}
    for l in body.iter(f"{TEI}l"):
        n = l.get("n")
        if n and n.isdigit():
            out[int(n)] = re.sub(r"\s+", " ", render_greek(l)).strip()
    return out


def english_blocks(h):
    """[(start, text)] Evelyn-White blocks; card milestones inside a block split it; notes dropped;
    letter-numbered blocks (137a ...) left out."""
    body = ET.parse(SRC / f"tlg0013.tlg{h:03d}.perseus-eng2.xml").getroot().find(f".//{TEI}body")
    out = []
    pending = [None]

    def do_l(l):
        start = l.get("n")
        if pending[0] and start.isdigit() and pending[0].isdigit() and 0 < int(pending[0]) - int(start) <= 4:
            start = pending[0]
        pending[0] = None
        parts = [[start, ""]]

        def walk(e):
            parts[-1][1] += e.text or ""
            for c in e:
                tag = c.tag.replace(TEI, "")
                if tag == "milestone" and c.get("unit") == "card":
                    if parts[-1][1].strip():
                        parts.append([c.get("n"), ""])
                elif tag not in ("note", "head"):
                    walk(c)
                parts[-1][1] += c.tail or ""
        walk(l)
        if len(parts) > 1 and not parts[-1][1].strip():
            pending[0] = parts[-1][0]
        out.extend((int(n), re.sub(r"\s+", " ", t).strip()) for n, t in parts if t.strip() and n.isdigit())

    def visit(e):
        for c in e:
            tag = c.tag.replace(TEI, "")
            if tag == "l":
                do_l(c)
            elif tag == "milestone" and c.get("unit") == "card":
                pending[0] = c.get("n")
            elif tag != "head":
                visit(c)
    visit(body)
    return out


def build(force=False):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    services = iiif_services()
    G = {h: greek(h) for h in range(1, 19)}
    E = {h: english_blocks(h) for h in range(1, 19)}
    folios = sorted({c[0] for c in COLUMNS}, key=lambda f: (int(f[:-1]), f[-1]))
    for f in folios:
        get_scan(f, services, force)

    # line -> column index, per hymn
    where = {}
    for ci, (f, col, segs, note) in enumerate(COLUMNS):
        for h, a, b in segs:
            for k in range(a, b + 1):
                if k in NOT_IN_M.get(h, set()):
                    continue
                assert (h, k) not in where, (h, k)
                assert k in G[h], (h, k)
                where[(h, k)] = ci

    # English block -> column
    eng_at = {}
    dropped = {}
    for h, blocks in E.items():
        last = max(G[h])
        for i, (a, t) in enumerate(blocks):
            b = max(a, blocks[i + 1][0] - 1) if i + 1 < len(blocks) else last
            mid = (a + b) // 2
            ci = where.get((h, mid))
            if ci is None:
                inm = [k for k in range(a, b + 1) if (h, k) in where]
                ci = where[(h, inm[0])] if inm else None
            if ci is None:
                dropped.setdefault(h, []).append(f"{a}-{b}")
                continue
            eng_at.setdefault((ci, h), []).append((a, b, t))

    rows = []
    for order, (slug, hymns, title, blurb) in enumerate(ENTRIES, 1):
        tid = f"verified-{KEY}-{slug}"
        sections, multi = [], len(hymns) > 1
        for ci, (f, col, segs, note) in enumerate(COLUMNS):
            mysegs = [s for s in segs if s[0] in hymns]
            if not mysegs:
                continue
            g_parts, e_parts, refs = [], [], []
            for h in sorted({s[0] for s in mysegs}, key=lambda x: [s[0] for s in mysegs].index(x)):
                ks = sorted(k for (hh, k), c in where.items() if hh == h and c == ci)
                head = f"<em>Hymn {h}, {HYMN_NAMES[h]}</em><br>" if multi else ""
                ghead = f"<em>Hymn {h}</em><br>" if multi else ""
                g_parts.append(ghead + "<br>".join(f"<sup>{k}</sup>{G[h][k]}" for k in ks))
                eb = eng_at.get((ci, h), [])
                body = " ".join(f"<sup>{a}</sup>{esc(t)}" for a, b, t in eb)
                e_parts.append(f"<p>{head}{body}</p>" if body else (f"<p>{head}<em>(The English for these verses is given with the neighbouring column.)</em></p>"))
                spans = [f"{a}-{b}" if a != b else f"{a}" for (hh, a, b) in mysegs if hh == h]
                refs.append(f"Hymn {h} {', '.join(spans)}")
            side = "left" if col == "a" else "right"
            first_h, first_a, _ = segs[0]
            last_h, _, last_b = segs[-1]
            fw = " ".join(re.sub(r"<[^>]+>", "", G[first_h][first_a]).split()[:4])
            lw = " ".join(re.sub(r"<[^>]+>", "", G[last_h][last_b]).split()[-4:])
            allsegs = "; ".join(f"Hymn {h} {a}-{b}" for h, a, b in segs)
            prev_ci, next_ci = ci - 1, ci + 1
            cont = ""
            if prev_ci >= 0:
                ph, _, pb = COLUMNS[prev_ci][2][-1]
                cont += f" The column before ends with Hymn {ph} {pb}."
            if next_ci < len(COLUMNS):
                nh, na, _ = COLUMNS[next_ci][2][0]
                cont += f" The next column begins with Hymn {nh} {na}."
            eb_all = [x for h in hymns for x in eng_at.get((ci, h), [])]
            eng_note = ""
            if eb_all:
                eng_note = f" English blocks here: {', '.join(f'{a}-{b}' for a, b, t in eb_all)}."
                over = [f"{a}-{b}" for h in hymns for a, b, t in eng_at.get((ci, h), [])
                        if any((h, k) not in where for k in range(a, b + 1))]
                if over:
                    eng_note += f" The English block(s) {', '.join(over)} also cover verses that are not in the manuscript."
            sn = (f"{MS}, fol. {f}, column {col} ({side}): {allsegs}; begins ‹{fw}›, ends ‹{lw}›. "
                  f"Checked on the image: the first and last verses of the column were read and matched to the Greek.{cont}"
                  + (f" {note}" if note else "") + eng_note)
            sections.append({
                "section": f"fol. {f} {col}",
                "original_ref": f"{'; '.join(refs)}; {MS}, fol. {f}, column {col}",
                "original_text": "<br><br>".join(g_parts),
                "text": "".join(e_parts),
                "scan_pages": [f"{KEY}/{scan_name(f)}"],
                "scan_note": sn,
            })
        fol_list = []
        for s in sections:
            fo = s["section"].split()[1]
            if fo not in fol_list:
                fol_list.append(fo)
        gaps = []
        for h in hymns:
            mx = max(G[h])
            missing = [k for k in range(1, mx + 1) if (h, k) not in where]
            if missing:
                rngs, start = [], missing[0]
                for i, k in enumerate(missing):
                    if i + 1 == len(missing) or missing[i + 1] != k + 1:
                        rngs.append(f"{start}-{k}" if start != k else f"{start}")
                        if i + 1 < len(missing):
                            start = missing[i + 1]
                gaps.append(f"Hymn {h}: {', '.join(rngs)}")
        gap_txt = ("<p>Verses of the Loeb text that are not in this manuscript, and so are not shown: "
                   + "; ".join(gaps) + ".</p>") if gaps else ""
        intro = (
            f"<p>The <em>Homeric Hymns</em> are 33 hexameter poems to the Greek gods, composed by anonymous poets between about the 7th and the 5th century BCE "
            f"and handed down under Homer's name. This entry: <strong>{esc(title)}</strong>. {esc(blurb)}</p>"
            f"<p>The page photographs are from {esc(MS_LONG)}. M is the only manuscript of the Hymn to Demeter. "
            f"Each section below is one column of a page (a = left, b = right); its note gives the first and last verse as read on the photograph. "
            f"This entry is on fol. {', '.join(fol_list)}.</p>"
            + gap_txt +
            "<p>The Greek is Evelyn-White's Loeb text (1914) via Perseus, not a transcription of the manuscript; where M is damaged the edition's restorations are shown in square brackets. "
            "The English is Evelyn-White's prose translation (1914), in blocks of about five lines, so a block can begin a line or two before or after a column break.</p>"
        )
        pub = {
            "id": tid, "slug": tid, "title": title,
            "language": "Ancient Greek / English",
            "source": f"{MS} (Leiden University Libraries IIIF) + Evelyn-White Greek (Loeb 1914, Perseus) + Evelyn-White English (1914, Perseus)",
            "description": f"{title}, column by column on the 15th-century Leiden manuscript BPG 33 H, the only witness of the Hymn to Demeter, with Greek and English.",
            "introduction": intro,
            "translator_notes": [
                "Greek: H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb Classical Library, 1914), via Perseus. Square brackets mark the editor's restorations of text lost or doubtful in the manuscript.",
                "Lines the Loeb numbers with letters (137a, 236a, 317a, 526a and others) are editorial supplements or variants and are left out.",
                "English: Evelyn-White's translation in the same volume; his footnotes are omitted."
                + (f" English blocks that fall wholly in verses missing from M are left out ({'; '.join(f'Hymn {h}: ' + ', '.join(v) for h, v in dropped.items() if h in hymns)})." if any(h in dropped for h in hymns) else ""),
            ],
            "translation": sections,
            "verification": {
                "scan_source": f"Leiden University Libraries, Digital Collections (IIIF): {VIEWER} ; manifest {MANIFEST}",
                "scan_license": "Public Domain Mark 1.0 (as stated in the Leiden IIIF manifest); images Leiden University Libraries",
                "scan_manuscript": MS_LONG,
                "scan_mapping": "First and last verse of every column read on the page image and matched to the Greek, with continuity checked between consecutive columns; hymn-level folio ranges from the library catalogue (details in each section's scan_note).",
                "scan_mapping_urls": [VIEWER, MANIFEST],
                "scan_local_paths": list(dict.fromkeys(s["scan_pages"][0] for s in sections)),
                "original_text_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus canonical-greekLit tlg0013 perseus-grc2 ({GITHUB})",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus tlg0013 perseus-eng2 ({GITHUB})",
                "translation_license": "public domain (published 1914); Perseus digital text CC BY-SA 4.0",
                "translator": "H. G. Evelyn-White (1914)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order, "title": title, "author_id": "homer",
            "language": "Ancient Greek", "era": "Classical", "tradition": "greek", "category": "sacred-text",
            "date_approx": "c. 700-500 BCE (composition); manuscript 15th c.", "century": -7,
            "source": pub["source"], "description": pub["description"],
            "themes": ["homeric-hymns", "greek-religion", "greek-myth", "hymn", "greek", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": f"{MS}, fol. {p.split('-f')[-1][:-4]}"} for p in pub["verification"]["scan_local_paths"]]},
        })
        print(f"wrote {tid}: {len(sections)} sections")

    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-", "label": "Homeric Hymns (Leiden manuscript)",
            "group": "Greece", "date_sort": -650,
            "author_name": "Homeric Hymns (anonymous, c. 7th-5th c. BCE; Leiden BPG 33 H, 15th c.)",
            "source_url": VIEWER,
            "critical_edition": "Evelyn-White, Loeb 1914, via Perseus",
            "translator_name": "H. G. Evelyn-White (1914)",
            "original_lang_label": "Ancient Greek · Evelyn-White",
            "original_lang_code": "grc", "edition_label": "",
            "search_terms": "homeric hymns demeter persephone eleusis apollo delos delphi hermes lyre aphrodite anchises dionysus",
            "description": "The Homeric Hymns to Demeter, Apollo, Hermes and Aphrodite and the shorter hymns, column by column on the Leiden 'Moscow' manuscript (BPG 33 H), the only witness of the Hymn to Demeter.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries); English dropped: {dropped}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    build(ap.parse_args().force)
