#!/usr/bin/env python3
"""
import_papyrus_prisse.py -- Papyrus Prisse (BnF, Egyptien 183-194): the end of the
Instruction for Kagemni and the complete Instruction of Ptahhotep.

Collection key: papyrus-prisse   (entries verified-papyrus-prisse-*)

Chain of evidence
-----------------
1. OBJECT   Papyrus Prisse, Bibliotheque nationale de France, Departement des
            Manuscrits, Egyptien 183-194 (12th Dynasty, c. 1850 BCE; bought at
            Thebes by E. Prisse d'Avennes in 1843). The roll is mounted in twelve
            frames. BnF catalogue (archivesetmanuscrits.bnf.fr/ark:/12148/cc12921q):
              Egyptien 183  Kagemni, two columns of 12 and 9 lines
              Egyptien 184-185  erased text (no edition)
              Egyptien 186  end of the erased part and two columns (Ptahhotep verses 1-73)
              Egyptien 187  one column of eleven lines (verses 75-123)
              Egyptien 188  one column of 12 lines (verses 124-216)
              Egyptien 189-194  two columns each (verses 217-end)
            With the TLA page numbering (Kagemni pages 1-2, Ptahhotep pages 4-19)
            this gives: 183 = pages 1-2; 186 = pages 4-5; 187 = page 6;
            188 = page 7; 189 = 8-9; 190 = 10-11; 191 = 12-13; 192 = 14-15;
            193 = 16-17; 194 = 18-19. The line count of every page in the TLA
            text agrees with this (page 6: 11 lines, page 7: 12 lines, ...).
2. SCANS    Photographs of each frame taken by the Wikimedia Commons user Zunkir
            at the BnF exhibition "L'aventure Champollion" (2022), published as
            own work under CC BY-SA 4.0 (Category:Prisse Papyrus). For frames
            186 and 189-194 there is one photograph per column ("right part" =
            first column, since the hieratic runs right to left). The frame 183
            photograph shows both Kagemni columns and is cropped into page 1
            (right) and page 2 (left). Checked by eye: line counts per page and
            the red rubrics at the maxim openings (see PAGE_CHECKS).
3. ORIGINAL Thesaurus Linguae Aegyptiae, edition by Peter Dils (after Jequier
            1911), from the TLA database extract of January 2018
            (urn:nbn:de:kobv:b4-opus4-29190) as converted to TEI by S. D.
            Schweitzer, AED-TEI (github.com/simondschweitzer/aed-tei), texts
            DKAFDVSXYFADJDS3Z3AOISAP4U (Ptahhotep) and KI7QRD7K55C6PJRUN5AFW6OFLI
            (Kagemni), CC BY-SA 4.0. Transliteration with the TLA's Prisse
            page,line numbers; Unicode hieroglyphs from the *_hiero.xml file
            (none exist for Kagemni).
4. ENGLISH  Battiscombe G. Gunn, The Instruction of Ptah-hotep and the
            Instruction of Ke'gemni: the Oldest Books in the World (Wisdom of
            the East, London: John Murray, 1906), Project Gutenberg #30508.
            Public domain (published 1906). Gunn's numbered sections (A, B, 1-37,
            C, 38-43, D) are the section units here. Each section was matched to
            the TLA sentences by reading Gunn against the TLA German sentence
            translations (SECTIONS below lists the first and last TLA sentence
            of every Gunn section).

Usage:  python3 scripts/import_papyrus_prisse.py           (build)
        python3 scripts/import_papyrus_prisse.py --force   (re-download images)
"""

import argparse
import io
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "papyrus-prisse"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()

T = "{http://www.tei-c.org/ns/1.0}"
XID = "{http://www.w3.org/XML/1998/namespace}id"
AED_RAW = "https://raw.githubusercontent.com/simondschweitzer/aed-tei/master/files/"
GUTENBERG = "https://www.gutenberg.org/cache/epub/30508/pg30508.txt"
COMMONS = "https://commons.wikimedia.org/wiki/File:"
UA = "TheosisLibrary/1.0 (https://theosislibrary.com; non-commercial research)"

TLA_PTAH = "DKAFDVSXYFADJDS3Z3AOISAP4U"
TLA_KAG = "KI7QRD7K55C6PJRUN5AFW6OFLI"

# --------------------------------------------------------------------------
# Images: page -> (local file, Commons file, BnF frame, crop box or None)
# --------------------------------------------------------------------------
PAGES = {
    1: ("kagemni-p01.jpg", "Papyrus_Prisse_183.jpg", "Egyptien 183", "right"),
    2: ("kagemni-p02.jpg", "Papyrus_Prisse_183.jpg", "Egyptien 183", "left"),
    4: ("ptahhotep-p04.jpg", "Papyrus_Prisse_186_1.jpg", "Egyptien 186", None),
    5: ("ptahhotep-p05.jpg", "Papyrus_Prisse_186_2.jpg", "Egyptien 186", None),
    6: ("ptahhotep-p06.jpg", "Papyrus_Prisse_187.jpg", "Egyptien 187", None),
    7: ("ptahhotep-p07.jpg", "Papyrus_Prisse_188.jpg", "Egyptien 188", None),
    8: ("ptahhotep-p08.jpg", "Papyrus_Prisse_189_1.jpg", "Egyptien 189", None),
    9: ("ptahhotep-p09.jpg", "Papyrus_Prisse_189_2.jpg", "Egyptien 189", None),
    10: ("ptahhotep-p10.jpg", "Papyrus_Prisse_190_1.jpg", "Egyptien 190", None),
    11: ("ptahhotep-p11.jpg", "Papyrus_Prisse_190_2.jpg", "Egyptien 190", None),
    12: ("ptahhotep-p12.jpg", "Papyrus_Prisse_191_1.jpg", "Egyptien 191", None),
    13: ("ptahhotep-p13.jpg", "Papyrus_Prisse_191_2.jpg", "Egyptien 191", None),
    14: ("ptahhotep-p14.jpg", "Papyrus_Prisse_192_1.jpg", "Egyptien 192", None),
    15: ("ptahhotep-p15.jpg", "Papyrus_Prisse_192_2.jpg", "Egyptien 192", None),
    16: ("ptahhotep-p16.jpg", "Papyrus_Prisse_193_1.jpg", "Egyptien 193", None),
    17: ("ptahhotep-p17.jpg", "Papyrus_Prisse_193_2.jpg", "Egyptien 193", None),
    18: ("ptahhotep-p18.jpg", "Papyrus_Prisse_194_1.jpg", "Egyptien 194", None),
    19: ("ptahhotep-p19.jpg", "Papyrus_Prisse_194_2.jpg", "Egyptien 194", None),
}
# Kagemni crop: the gap between the two columns on Papyrus_Prisse_183.jpg (3285 px wide)
KAGEMNI_SPLIT = {"right": (1690, None), "left": (0, 1760)}

# What was checked by eye on each photograph (line counts against the TLA page,
# red rubrics against the TLA sentence that opens a maxim).
PAGE_CHECKS = {
    1: "right-hand column of frame 183; checked on the image: 12 lines (BnF: 'deux colonnes de texte, 12 et 9 lignes'; TLA 1,1-1,12), no rubrics",
    2: "left-hand column of frame 183; checked on the image: 9 lines (TLA 2,1-2,9), the rest of the frame blank",
    4: "checked on the image: four lines at the foot of the column below the erased area, line 1 opening with the red title (TLA 4,1)",
    5: "checked on the image: 14 lines; red rubric in the middle of line 6 (title, TLA 5,6) and at the end of line 10, where maxim 2 opens (TLA 5,10)",
    6: "checked on the image: one column of 11 lines (BnF: 'une colonne de onze lignes'); rubrics at the start of line 1, the end of line 3, the start of line 8 and line 11 (maxims 4-7, TLA 6,1, 6,3, 6,8, 6,11)",
    7: "checked on the image: one wide column of 12 lines (BnF: 'une colonne de 12 lignes'); rubrics on lines 3, 5, 7, 9 and 10 (TLA 7,3, 7,5, 7,7, 7,9, 7,10)",
    8: "right-hand column of frame 189; checked on the image: 14 lines, rubrics on lines 2, 6, 11 and 14 (TLA 8,2, 8,6, 8,11, 8,14)",
    9: "left-hand column of frame 189; checked on the image: rubrics on lines 3 and 7 and near the foot of the column at line 13 (TLA 9,3, 9,7, 9,13)",
    10: "right-hand column of frame 190; checked on the image: rubrics on lines 5 and 8 (TLA 10,5, 10,8)",
    11: "left-hand column of frame 190; checked on the image: 13 lines, rubrics on lines 1 and 5, at the end of line 8 and on line 12 (TLA 11,1, 11,5, 11,8, 11,12)",
    12: "right-hand column of frame 191; checked on the image: rubrics on lines 6 and 9 (TLA 12,6, 12,9)",
    13: "left-hand column of frame 191; checked on the image: rubrics at the start of line 1 and on lines 4, 6 and 9 (TLA 13,1, 13,4, 13,6, 13,9)",
    14: "right-hand column of frame 192; checked on the image: 13 lines, rubrics in the middle of line 4 and at the end of lines 6 and 12 (TLA 14,4, 14,6, 14,12)",
    15: "left-hand column of frame 192; checked on the image: 13 lines, rubrics at the end of line 2 and on lines 5, 6 and 8 (TLA 15,2, 15,5, 15,6, 15,8)",
    16: "right-hand column of frame 193; checked on the image: rubrics on lines 3 and 13 (TLA 16,3, 16,13)",
    17: "left-hand column of frame 193; checked on the image: rubrics on lines 4 and 10 (TLA 17,4, 17,10)",
    18: "right-hand column of frame 194; checked on the image: 14 lines, rubric at the end of line 12 (TLA 18,12)",
    19: "left-hand column of frame 194; checked on the image: 8 black lines and the red colophon as line 9 (TLA 19,1-19,9), rubric on line 3 (TLA 19,3), the rest of the sheet blank",
}

# --------------------------------------------------------------------------
# Sections: (section id, first TLA sentence, last TLA sentence), 1-based
# indexes into the sentence list of the TLA text. Established by reading
# Gunn against the TLA German sentence translations.
# --------------------------------------------------------------------------
PTAH_SECTIONS = [
    ("A", 1, 30), ("B", 31, 32), ("1", 33, 38), ("2", 39, 44), ("3", 45, 47),
    ("4", 48, 54), ("5", 55, 66), ("6", 67, 77), ("7", 78, 92), ("8", 93, 100),
    ("9", 101, 109), ("10", 110, 118), ("11", 119, 125), ("12", 126, 136),
    ("13", 137, 143), ("14", 144, 155), ("15", 156, 161), ("16", 162, 165),
    ("17", 166, 170), ("18", 171, 178), ("19", 179, 188), ("20", 189, 194),
    ("21", 195, 209), ("22", 210, 217), ("23", 218, 230), ("24", 231, 236),
    ("25", 237, 250), ("26", 251, 259), ("27", 260, 269), ("28", 270, 274),
    ("29", 275, 277), ("30", 278, 281), ("31", 282, 292), ("32", 293, 296),
    ("33", 297, 308), ("34", 309, 315), ("35", 316, 322), ("36", 323, 326),
    ("37", 327, 330), ("C", 331, 347), ("38", 348, 366), ("39", 367, 372),
    ("40", 373, 378), ("41", 379, 396), ("42", 397, 404), ("43", 405, 409),
    ("D", 410, 412), ("colophon", 413, 413),
]
KAG_SECTIONS = [
    ("1", 1, 7), ("2", 8, 18), ("3", 19, 25), ("4", 26, 31), ("5", 32, 34),
    ("6", 35, 45), ("colophon", 46, 46),
]
# Sanity anchors: the TLA transliteration must start with these words
PTAH_ANCHORS = {"A": "sbꜣy,t", "1": "m ꜥꜣi̯ jb", "2": "jr gmi̯ =k ḏꜣjs,w", "7": "jr wnn =k m z n ḥmsi̯",
                "13": "jr wnn =k m rwy,t", "21": "jr jqr =k grg =k pr", "32": "jmi̯ =k nk",
                "C": "jr sḏm =k nn", "38": "ꜣḫ sḏm", "D": "mj pḥ =k wj", "colophon": "jwi̯ =f pw"}
KAG_ANCHORS = {"1": "wḏꜣ snḏ,w", "2": "jr ḥmsi̯ =k ḥnꜥ ꜥšꜣ,t", "6": "rḏi̯.jn ṯꜣ,t〈j〉", "colophon": "jwi̯ =f pw"}


# --------------------------------------------------------------------------
def fetch(url, binary=False):
    out = subprocess.run(["curl", "-sL", "-m", "300", "-A", UA, url], capture_output=True, check=True).stdout
    if not out:
        raise RuntimeError(f"empty download {url}")
    return out if binary else out.decode("utf-8")


def source(name, url):
    p = SRC / name
    if not p.exists():
        SRC.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url, binary=True))
    return p


# ---------------------------- TLA TEI -------------------------------------
def render_word(el):
    """Transliteration of one <w>, with Leiden-style brackets for the TEI markup."""
    def walk(e):
        tag = e.tag.replace(T, "")
        if tag == "fs":
            return e.tail or ""
        inner = (e.text or "") + "".join(walk(c) for c in e)
        if tag == "supplied":
            inner = f"[{inner}]" if e.get("reason") == "lost" else f"〈{inner}〉"
        elif tag == "surplus":
            inner = "{" + inner + "}"
        elif tag in ("damage", "unclear"):
            inner = f"⸢{inner}⸣"
        elif tag == "add":
            inner = f"\\{inner}/"
        elif tag == "gap":
            inner = "[…]"
        return inner + (e.tail or "") if tag != "w" else inner
    return re.sub(r"\s+", "", walk(el))


def tla_sentences(tid):
    """List of sentences; each sentence = list of tokens ('lb', n) | ('w', translit, word_id) | ('gap',)."""
    base = source(f"{tid}.xml", AED_RAW + f"{tid}.xml")
    root = ET.parse(base).getroot()
    ab = root.find(f".//{T}body/{T}ab")
    sents = []

    def walk(e, cur):
        tag = e.tag.replace(T, "")
        if tag == "s":
            cur = []
            sents.append(cur)
            for c in e:
                walk(c, cur)
            return
        if cur is None:          # tokens outside a sentence: attach to a new pseudo-sentence
            cur = []
            sents.append(cur)
        if tag == "lb":
            cur.append(("lb", e.get("n")))
        elif tag == "w":
            cur.append(("w", render_word(e), e.get(XID)))
        elif tag == "gap":
            cur.append(("gap",))
        else:
            for c in e:
                walk(c, cur)

    for child in ab:
        walk(child, None)
    return [s for s in sents if s]


def tla_hiero(tid):
    p = source(f"{tid}_hiero.xml", AED_RAW + f"{tid}_hiero.xml")
    txt = p.read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in re.finditer(r'<w corresp="src:([^"]+)">([^<]*)</w>', txt)}


def norm_line(n):
    """'[5,6-7]' -> '5,6-7' ; '[2, 8]' -> '2,8' ; '[19.9]' -> '19,9'"""
    n = n.strip().strip("[]").replace(" ", "")
    return re.sub(r"^(\d+)\.(\d+)$", r"\1,\2", n)


def page_of(line):
    return int(line.split(",")[0])


def render_range(sents, a, b, hiero=None):
    """Render sentences a..b (1-based, inclusive). Returns (translit_html, hiero_html, lines)."""
    # line current at the start of sentence a
    cur = None
    for s in sents[:a - 1]:
        for t in s:
            if t[0] == "lb":
                cur = norm_line(t[1])
    out, hout, lines = [], [], []
    first_tok = True
    for s in sents[a - 1:b]:
        for t in s:
            if t[0] == "lb":
                cur = norm_line(t[1])
                lines.append(cur)
                out.append(f"<sup>{cur}</sup>")
                hout.append(f"<sup>{cur}</sup>")
                first_tok = False
                continue
            if first_tok:
                if cur:
                    out.append(f"<sup>{cur}</sup>")
                    hout.append(f"<sup>{cur}</sup>")
                    lines.append(cur)
                first_tok = False
            if t[0] == "gap":
                out.append('<span class="lacuna">[…]</span>')
                hout.append('<span class="lacuna">[…]</span>')
            else:
                out.append(t[1])
                if hiero is not None:
                    h = hiero.get(t[2], "")
                    hout.append(h if h else f"<em>{t[1]}</em>")
    txt = " ".join(out).replace("</sup> ", "</sup>")
    htxt = " ".join(hout).replace("</sup> ", "</sup>")
    return txt, (htxt if hiero is not None else None), lines


# ---------------------------- Gunn 1906 -----------------------------------
def clean_par(p):
    p = re.sub(r"\{\d+\}", "", p)
    p = re.sub(r"\[\d+\]", "", p)
    p = re.sub(r"\s+", " ", p).strip()
    return p


def gunn_paragraphs(text, start_marker, end_marker):
    i = text.index("\n" + start_marker + "\n") if ("\n" + start_marker + "\n") in text else text.index(start_marker)
    j = text.index(end_marker, i)
    block = text[i:j]
    pars = [clean_par(x) for x in re.split(r"\n\s*\n", block)]
    return [p for p in pars if p]


def gunn_ptahhotep(text):
    pars = gunn_paragraphs(text, "The Instruction of the Governor of his City", "[1] The King.")
    secs, order, cur = {}, [], None
    title = pars[0]
    assert title.startswith("The Instruction of the Governor of his City"), title
    colophon = []
    for p in pars[1:]:
        m = re.match(r"^([A-D]|\d+)\.\s+(.*)$", p)
        if m:
            cur = m.group(1)
            order.append(cur)
            secs[cur] = [m.group(2)]
        elif p.isupper() or p.startswith("IT IS FINISHED"):
            colophon.append(p)
        else:
            secs[cur].append(p)
    secs["A"].insert(0, title)
    secs["colophon"] = [" ".join(colophon)]
    order.append("colophon")
    return {k: "\n\n".join(v) for k, v in secs.items()}, order


def gunn_kagemni(text):
    pars = gunn_paragraphs(text, "THE INSTRUCTION OF KE'GEMNI", "\n[1] ")
    pars = [p for p in pars if p not in ("THE INSTRUCTION OF KE'GEMNI", "On Avoiding Offence")]
    secs, cur = {}, None
    for p in pars:
        m = re.match(r"^(\d+)\.\s*(.*)$", p)
        if p.startswith("The Vizier caused his sons"):
            cur = "6"
            secs[cur] = [p]
        elif p.startswith("IT IS FINISHED"):
            secs["colophon"] = [p]
        elif m and cur != "6":
            cur = m.group(1)
            secs[cur] = [m.group(2)]
        else:
            secs[cur].append(p)
    return {k: "\n\n".join(v) for k, v in secs.items()}


# ---------------------------- images --------------------------------------
def build_scan(page, force):
    local, commons, frame, side = PAGES[page]
    dest = SCAN_DIR / local
    if dest.exists() and not force:
        return dest
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for attempt in range(8):   # Commons rate-limits bursts; back off and retry
        data = fetch(f"https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/{commons}", binary=True)
        if data[:3] == b"\xff\xd8\xff":
            break
        time.sleep(10 * (attempt + 1))
    else:
        raise RuntimeError(f"could not download {commons}")
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if side:
        x0, x1 = KAGEMNI_SPLIT[side]
        im = im.crop((x0, 0, x1 or im.size[0], im.size[1]))
    if max(im.size) > 2600:
        im.thumbnail((2600, 2600), Image.LANCZOS)
    im.save(dest, "JPEG", quality=86, optimize=True)
    return dest


# ---------------------------- entries -------------------------------------
def make_sections(sents, hiero, secdefs, gunn, anchors, label):
    out = []
    for sid, a, b in secdefs:
        tr, hi, lines = render_range(sents, a, b, hiero)
        plain = re.sub(r"<[^>]+>", "", tr).strip()
        if sid in anchors:
            assert plain.startswith(anchors[sid]) or anchors[sid] in plain[:80], (label, sid, plain[:80])
        pages = sorted({page_of(l) for l in lines})
        scans = [f"{KEY}/{PAGES[p][0]}" for p in pages]
        span = f"{lines[0]}-{lines[-1]}" if lines and lines[0] != lines[-1] else (lines[0] if lines else "?")
        where = " ".join(f"Page {p} is {PAGES[p][2]} (Commons photograph {PAGES[p][1]}), {PAGE_CHECKS[p]}." for p in pages)
        sent_desc = f"sentence {a}" if a == b else f"sentences {a}-{b}"
        on = f"page {pages[0]}" if len(pages) == 1 else "pages " + " and ".join(map(str, pages))
        note = (f"Prisse {span} (TLA page,line numbers): TLA {sent_desc} of this text, on {on}. {where}")
        if label == "ptahhotep" and sid == "32":
            note += (" Gunn (1906) did not translate this maxim and printed only the heading '[Concerning continence]'; "
                     "the English below is that heading, not a translation.")
        if label == "ptahhotep" and sid == "A":
            note += " The English includes Gunn's rendering of the red title line (4,1) before his paragraph A."
        sec = {
            "section": sid,
            "original_ref": f"Papyrus Prisse {span}; Gunn 1906, {('§' + sid) if sid not in ('colophon',) else 'colophon'}",
            "original_text": tr,
            "text": gunn[sid],
            "scan_pages": scans,
            "scan_note": note,
        }
        if hi:
            sec["edition_text"] = hi
        out.append(sec)
    return out


def verification(scans, tla_id, extra_mapping=""):
    return {
        "scan_source": "Wikimedia Commons, Category:Prisse Papyrus: photographs of BnF Egyptien 183-194 by the user Zunkir "
                       "(own work, BnF exhibition 'L'aventure Champollion', 2022), e.g. " + COMMONS + "Papyrus_Prisse_187.jpg",
        "scan_license": "CC BY-SA 4.0 (Zunkir, Wikimedia Commons); object: Bibliotheque nationale de France, Departement des Manuscrits",
        "scan_manuscript": "Paris, BnF, Egyptien 183-194 (Papyrus Prisse), 12th Dynasty, c. 1850 BCE, from Thebes (Dra Abu el-Naga)",
        "scan_mapping": "Frame-to-column structure from the BnF catalogue (Egyptien 183: two columns of 12 and 9 lines; 187: one column of "
                        "11 lines; 188: one column of 12 lines; 186 and 189-194: two columns) combined with the TLA page,line numbering, "
                        "and checked by eye on every photograph (line counts per column, rubrics at maxim openings). " + extra_mapping,
        "scan_mapping_urls": ["https://archivesetmanuscrits.bnf.fr/ark:/12148/cc12921q",
                              "https://commons.wikimedia.org/wiki/Category:Prisse_Papyrus"],
        "scan_local_paths": scans,
        "original_text_source": f"Thesaurus Linguae Aegyptiae (ed. Peter Dils), TLA database extract January 2018 "
                                f"(urn:nbn:de:kobv:b4-opus4-29190), TEI by S. D. Schweitzer, AED-TEI text {tla_id}: "
                                f"https://github.com/simondschweitzer/aed-tei/blob/master/files/{tla_id}.xml",
        "original_text_license": "CC BY-SA 4.0 (BBAW / SAW Leipzig, Thesaurus Linguae Aegyptiae; AED-TEI)",
        "translation_source": "Battiscombe G. Gunn, The Instruction of Ptah-hotep and the Instruction of Ke'gemni: the Oldest Books "
                              "in the World (Wisdom of the East; London: John Murray, 1906), Project Gutenberg #30508: "
                              "https://www.gutenberg.org/ebooks/30508",
        "translation_license": "public domain (published 1906)",
        "translator": "Battiscombe G. Gunn (1906)",
        "verified_date": TODAY,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    gunn_txt = source("gunn1906_pg30508.txt", GUTENBERG).read_text(encoding="utf-8")
    gp, order = gunn_ptahhotep(gunn_txt)
    gk = gunn_kagemni(gunn_txt)
    assert [s for s, _, _ in PTAH_SECTIONS] == order, (order,)
    assert set(gk) == {s for s, _, _ in KAG_SECTIONS}, gk.keys()

    ps = tla_sentences(TLA_PTAH)
    ks = tla_sentences(TLA_KAG)
    assert len(ps) == 413 and len(ks) == 46, (len(ps), len(ks))
    ph = tla_hiero(TLA_PTAH)

    for p in PAGES:
        build_scan(p, args.force)

    kag_secs = make_sections(ks, None, KAG_SECTIONS, gk, KAG_ANCHORS, "kagemni")
    ptah_secs = make_sections(ps, ph, PTAH_SECTIONS, gp, PTAH_ANCHORS, "ptahhotep")

    kag_scans = [f"{KEY}/{PAGES[p][0]}" for p in (1, 2)]
    ptah_scans = [f"{KEY}/{PAGES[p][0]}" for p in range(4, 20)]

    entries = []
    kag = {
        "id": PREFIX + "kagemni", "slug": PREFIX + "kagemni",
        "title": "The Instruction for Kagemni (Papyrus Prisse, pages 1-2)",
        "language": "Egyptian (TLA transliteration) / English",
        "source": "Papyrus Prisse, BnF Egyptien 183 (photographs by Zunkir, Wikimedia Commons, CC BY-SA 4.0) + TLA transliteration "
                  "(ed. P. Dils, CC BY-SA 4.0) + English of Battiscombe Gunn (1906, public domain)",
        "description": "The closing part of the Instruction for Kagemni, an Old Kingdom style wisdom text, on the first two "
                       "columns of the Papyrus Prisse (c. 1850 BCE), with Gunn's 1906 English.",
        "introduction": (
            "<p>The Papyrus Prisse, bought at Thebes in 1843 by Emile Prisse d'Avennes and now in the Bibliotheque nationale de France "
            "(Egyptien 183-194), is one of the oldest surviving literary papyri. It was written in the 12th Dynasty, around 1850 BCE, in a "
            "large hieratic book hand. The roll begins with the end of a wisdom text addressed to Kagemni; the beginning of that text is lost.</p>\n\n"
            "<p>The instruction is set in the Old Kingdom: a vizier gives rules of modest conduct (silence, restraint at table, no boasting) to his "
            "children, who read them aloud; then King Huni dies, Sneferu becomes king, and Kagemni is made vizier. The two columns of Kagemni "
            "(12 and 9 lines) are on frame Egyptien 183; the papyrus then has a stretch of erased writing (frames 184-185) before the Instruction of "
            "Ptahhotep begins.</p>\n\n"
            "<p>Each section below gives the Thesaurus Linguae Aegyptiae transliteration with the papyrus page and line numbers (1,1 to 2,9), "
            "the English of Battiscombe Gunn (1906), and the photograph of the column that carries it. Signs supplied by the editor are in angle "
            "brackets, superfluous signs in braces, damaged signs in half brackets, and the lost end of the colophon is shown as [...].</p>"
        ),
        "translator_notes": [
            "Gunn's footnote markers and page numbers have been removed; his own square brackets and question marks are kept.",
            "Gunn numbers the precepts 1-5; the closing narrative and the colophon are given here as sections 6 and 'colophon'.",
            "The TLA has no hieroglyphic encoding for this text, so only the transliteration is shown.",
        ],
        "translation": kag_secs,
        "verification": verification(kag_scans, TLA_KAG, "Kagemni: the frame 183 photograph is cropped at the gap between its two columns."),
    }
    ptah = {
        "id": PREFIX + "ptahhotep", "slug": PREFIX + "ptahhotep",
        "title": "The Instruction of Ptahhotep (Papyrus Prisse, complete)",
        "language": "Egyptian (TLA transliteration and hieroglyphs) / English",
        "source": "Papyrus Prisse, BnF Egyptien 186-194 (photographs by Zunkir, Wikimedia Commons, CC BY-SA 4.0) + TLA transliteration and "
                  "hieroglyphs (ed. P. Dils, CC BY-SA 4.0) + English of Battiscombe Gunn (1906, public domain)",
        "description": "The complete Instruction of Ptahhotep, the best known Egyptian wisdom text, on the 16 columns of the Papyrus Prisse "
                       "(c. 1850 BCE), section by section with Gunn's 1906 English.",
        "introduction": (
            "<p>The Instruction of Ptahhotep presents itself as the teaching of Ptahhotep, vizier of King Isesi of the 5th Dynasty (24th century BCE), "
            "handed on to his son when the vizier asks to retire. It is a series of 37 maxims on conduct (modesty, self-control, justice, speech "
            "at the right moment, care of household and dependants), framed by a prologue and a long epilogue on 'hearing', which in Egyptian "
            "means both listening and obeying. The oldest complete copy is the Papyrus Prisse, written in the 12th Dynasty around 1850 BCE and now "
            "in the Bibliotheque nationale de France (Egyptien 183-194).</p>\n\n"
            "<p>In the papyrus the text runs over 16 columns of horizontal hieratic lines, numbered pages 4 to 19 (pages 1-2 hold the end of the "
            "Instruction for Kagemni, page 3 was erased). The opening of most maxims is written in red. The papyrus is mounted in frames: page 4-5 on "
            "Egyptien 186, page 6 on 187, page 7 on 188, and two pages on each of 189 to 194. Every section below is linked to the photograph of the "
            "column or columns that carry it, and its scan note gives the page and line numbers.</p>\n\n"
            "<p>The sections follow Battiscombe Gunn's 1906 translation (A, B, maxims 1-37, C, 38-43, D and the colophon). For each Gunn section the "
            "Egyptian is the corresponding run of sentences in the Thesaurus Linguae Aegyptiae edition by Peter Dils, with the papyrus page and line "
            "number before each line. A second block gives the TLA hieroglyphic transcription in Unicode (a transcription of the hieratic); the few "
            "words for which the TLA has no complete hieroglyphic encoding are shown there in transliteration, in italics. Signs supplied by the "
            "editor are in angle brackets, superfluous signs in braces, damaged or unclear signs in half brackets, and lost text as [...].</p>\n\n"
            "<p>Gunn translated from the Prisse text but did not translate maxim 32, for which he printed only a heading; that section therefore "
            "has the Egyptian but no real English. Gunn's renderings are early and some passages are now understood differently.</p>"
        ),
        "translator_notes": [
            "Gunn's footnote markers and page numbers have been removed; his own square brackets, question marks and the dots marking passages he left untranslated are kept.",
            "Maxim 32 (on forbidden sexual intercourse) was not translated by Gunn; the English shown is only his heading '[Concerning continence]'.",
            "The hieroglyphs are the TLA editor's transcription of the hieratic, not a facsimile of the papyrus.",
            "Line numbers such as 6,11 are papyrus page and line. A number at the start of a section that does not begin a new line marks the line on which the section starts.",
            "The TLA edition opens with two lacuna marks before line 4,1; they are kept as given.",
        ],
        "translation": ptah_secs,
        "verification": verification(ptah_scans, TLA_PTAH),
    }
    for e in (kag, ptah):
        (PUB / f"{e['id']}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")
        entries.append(e)
        print(f"wrote {e['id']}: {len(e['translation'])} sections")

    rows = []
    for order_n, (e, author, date_approx, themes, pages) in enumerate([
        (kag, "egyptian-wisdom", "Middle Kingdom composition; manuscript c. 1850 BCE (12th Dynasty)",
         ["kagemni", "wisdom-literature", "papyrus-prisse", "egypt", "verified"], (1, 2)),
        (ptah, "ptahhotep", "composition attributed to the 5th Dynasty (c. 2400 BCE); manuscript c. 1850 BCE (12th Dynasty)",
         ["ptahhotep", "wisdom-literature", "maxims", "papyrus-prisse", "egypt", "verified"], range(4, 20)),
    ], start=1):
        rows.append({
            "id": e["id"], "slug": e["id"], "order": order_n, "title": e["title"], "author_id": author,
            "language": "Egyptian", "era": "Ancient Near East", "tradition": "egyptian", "category": "philosophy",
            "date_approx": date_approx, "century": -19, "source": e["source"], "description": e["description"],
            "themes": themes, "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{PAGES[p][0]}", "caption": f"Papyrus Prisse page {p} ({PAGES[p][2]})"} for p in pages]},
        })
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Papyrus Prisse (Kagemni and Ptahhotep)", "group": "Egypt",
            "date_sort": -1850,
            "author_name": "Papyrus Prisse, Thebes (12th Dynasty, c. 1850 BCE)",
            "source_url": "https://archivesetmanuscrits.bnf.fr/ark:/12148/cc12921q",
            "critical_edition": "Thesaurus Linguae Aegyptiae, ed. Peter Dils (2018 data, AED-TEI)",
            "translator_name": "Battiscombe G. Gunn (1906)",
            "original_lang_label": "Egyptian · TLA transliteration",
            "original_lang_code": "egy",
            "edition_label": "Hieroglyphic transcription (TLA, Unicode)",
            "search_terms": "ptahhotep ptah-hotep kagemni ke'gemni prisse papyrus wisdom maxims instruction sebayt vizier isesi",
            "description": "The Papyrus Prisse (BnF, c. 1850 BCE), the oldest complete copy of the Instruction of Ptahhotep, with the end of "
                           "the Instruction for Kagemni: every column photographed, TLA transliteration and hieroglyphs, Gunn's 1906 English.",
        },
        "texts": rows,
        "authors": [{
            "id": "ptahhotep", "name": "Ptahhotep (attributed)", "dates": "5th Dynasty, c. 2400 BCE (attributed)", "century": -24,
            "era": "Ancient Near East", "tradition": "egyptian", "language": "Egyptian",
            "bio": "Vizier of King Isesi of the 5th Dynasty, named as the author of the Instruction of Ptahhotep; the text itself survives in Middle Kingdom copies.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
