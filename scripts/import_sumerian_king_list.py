#!/usr/bin/env python3
"""
import_sumerian_king_list.py -- the Sumerian King List on the Weld-Blundell Prism
(Ashmolean Museum AN1923.444 = W-B 444, CDLI P384786), all four faces / eight columns.

Chain of evidence
-----------------
1. SCAN      CDLI photograph of the prism, https://cdli.earth/dl/photo/P384786.jpg
             ("Image courtesy of the Ashmolean Museum").  The photograph shows the four
             inscribed faces side by side plus the uninscribed top and bottom.  Each face is
             cropped to its own file (wb444-face-a.jpg ... -d.jpg).  Face order a, b, c, d
             (left to right in the CDLI photo) was checked on the image against the damage
             recorded in the CDLI transliteration: face a column ii opens with 4 restored
             (bracketed) lines, face b column ii with 11, face c column i with 13 and column ii
             with 5, and face d column ii ends with a double ruling and a one-line colophon.
             CDLI terms: images are for non-commercial use; copyright the holding institution.
2. ORIGINAL  CDLI transliteration of P384786 (ATF, https://cdli.earth/artifacts/384786),
             i.e. the signs on this prism, with its own face/column/line numbers.  CDLI links
             every prism line to a line of the composite Q000371 (">>Q000371 nnn"), whose
             numbering is that of ETCSL 2.1.1 (checked line by line: e.g. 39 a-ma-ru ba-ur3,
             40 egir a-ma-ru ba-ur3-ra-ta, 95 e2-an-na-ka, 284 a-ba-am3 lugal).  ASCII ATF is
             rendered in the usual Unicode form (sz = š, s, = ṣ, t, = ṭ, sign indices as
             subscripts); nothing else is changed.
3. ENGLISH   ETCSL 2.1.1 "The Sumerian king list: translation" (J. A. Black et al., The
             Electronic Text Corpus of Sumerian Literature, Oxford 1998-2006), distributed by
             the Oxford Text Archive under CC BY-NC-SA 3.0.  ETCSL translates the composite
             text in paragraphs headed by composite line ranges; its numbers follow ms. WB
             (this prism) unless a note names another manuscript.

Sections = ETCSL translation paragraphs.  Each section's Sumerian is every prism line whose
CDLI composite link falls in the paragraph's line range, grouped by face and column; its
scan_pages are the face crops that carry those columns.  ETCSL paragraph 378-431 (the grand
totals) is not on this prism and is not published.

Usage:  python3 scripts/import_sumerian_king_list.py
"""
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "sumerian-king-list"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TID = f"verified-{KEY}-wb444"

CDLI_PAGE = "https://cdli.earth/artifacts/384786"
PHOTO_URL = "https://cdli.earth/dl/photo/P384786.jpg"
ATF_URL = "https://cdli.earth/inscriptions/2376229/atf"
ETCSL_TR = "https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.2.1.1&display=Crit&charenc=gcirc"
ETCSL_TR_STATIC = "https://etcsl.orinst.ox.ac.uk/section2/tr211.htm"
ETCSL_C_STATIC = "https://etcsl.orinst.ox.ac.uk/section2/c211.htm"
OTA = "http://ota.ox.ac.uk/desc/2518"
EPSD_LIT = "https://oracc.museum.upenn.edu/epsd2/literary/"

# Face boxes (x0, y0, x1, y1) in the 5702 x 5809 CDLI photograph, found from the black
# background and checked on the image.
FACES = {
    "a": (18, 1489, 1377, 4362),
    "b": (1442, 1475, 2774, 4358),
    "c": (2830, 1497, 4175, 4328),
    "d": (4213, 1398, 5685, 4415),
}
ROMAN = {"1": "i", "2": "ii"}


def fetch(url, name, binary=False):
    p = SRC / name
    if not p.exists() or p.stat().st_size == 0:
        subprocess.run(["curl", "-s", "-L", "-m", "300", "-A", "TheosisLibrary/1.0 (non-commercial research)",
                        "-o", str(p), url], check=True)
    return p.read_bytes() if binary else p.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- ATF
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def atf_html(s):
    """ASCII C-ATF -> Unicode transliteration, HTML-escaped."""
    s = s.replace("($blank space$)", "(blank space)")
    s = re.sub(r"\(\$(.*?)\$\)", r"(\1)", s)
    s = s.replace("sz", "š").replace("SZ", "Š").replace("s,", "ṣ").replace("S,", "Ṣ")
    s = s.replace("t,", "ṭ").replace("T,", "Ṭ")
    s = re.sub(r"(?<=[A-Za-zšṣṭŠṢṬ])(\d+)", lambda m: m.group(1).translate(SUB), s)
    return html.escape(s.strip(), quote=False)


def parse_atf(text):
    """[{surface, column, line, atf, q}] with q = composite line label (e.g. '040', '288A', 'colophon')."""
    out, surf, col, cur = [], None, None, None
    alias = {}  # CDLI may also link through an alias defined in the header: '#link: def A = Q000371', '>>A 040'
    for raw in text.split("\n"):
        ln = raw.rstrip()
        m = re.match(r"^#link:\s*def\s+(\S+)\s*=\s*(Q\d+)", ln)
        if m:
            alias[m.group(1)] = m.group(2)
            continue
        if ln.startswith("@surface"):
            surf = ln.split()[1]
        elif ln.startswith("@column"):
            col = ln.split()[1]
        m = re.match(r"^(\d+(?:\.[a-z])?)\.\s(.*)$", ln)
        if m:
            cur = {"surface": surf, "column": col, "line": m.group(1), "atf": m.group(2).strip(), "q": None}
            out.append(cur)
            continue
        m = re.match(r"^>>(\S+)\s+(\S+)", ln)
        if m and cur is not None and (m.group(1) == "Q000371" or alias.get(m.group(1)) == "Q000371"):
            cur["q"] = m.group(2)
    return out


def qnum(q):
    m = re.match(r"(\d+)", q or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- ETCSL translation
def clean_tr(fragment):
    # ETCSL's CGI display marks a variant reading as {(note) reading}; its static pages print the
    # same variant as (note reading).  Use the static form.
    s = re.sub(r'\{\s*\(<span class="note">(.*?)</span>\)\s*(.*?)\}', r"(<em>\1</em> \2)", fragment, flags=re.S)
    s = re.sub(r'<span class="note">(.*?)</span>', r"<em>\1</em>", s, flags=re.S)
    s = re.sub(r"<(?!/?em>)[^>]+>", "", s)
    s = html.unescape(s).replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("( <em>", "(<em>").replace("</em> )", "</em>)")
    return s


def etcsl_paragraphs(page):
    body = page.split("<body class=\"translation\"", 1)[1]
    intro = re.search(r'\(<span class="gap">(.*?)</span>\)', body, flags=re.S)
    paras = []
    for m in re.finditer(r"<p><a href='[^']*lineid=c\d+\.([^']+)'>([^<]+)</a><a name='[^']+'></a>(.*?)</p>",
                         body, flags=re.S):
        rng = m.group(2).strip().rstrip(".")
        a, _, b = rng.partition("-")
        paras.append({"range": rng, "start": int(a), "end": int(b or a), "text": clean_tr(m.group(3))})
    return (clean_tr(intro.group(1)) if intro else ""), paras


# ---------------------------------------------------------------- scans
def make_scans():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    Image.MAX_IMAGE_PIXELS = None
    src = SRC / "P384786.jpg"
    fetch(PHOTO_URL, "P384786.jpg", binary=True)
    im = Image.open(src).convert("RGB")
    paths = {}
    for face, box in FACES.items():
        out = SCAN_DIR / f"wb444-face-{face}.jpg"
        c = im.crop(box)
        if max(c.size) > 2600:
            c.thumbnail((2600, 2600), Image.LANCZOS)
        c.save(out, quality=86)
        paths[face] = f"{KEY}/{out.name}"
    return paths


# ---------------------------------------------------------------- build
def main():
    SRC.mkdir(parents=True, exist_ok=True)
    atf = fetch(ATF_URL, "P384786.atf")
    fetch(CDLI_PAGE + "/json", "P384786.json")
    tr_page = fetch(ETCSL_TR, "etcsl_t.2.1.1.html")
    fetch(ETCSL_C_STATIC, "etcsl_c211.htm")
    lines = parse_atf(atf)
    assert len(lines) == 380, len(lines)
    intro_note, paras = etcsl_paragraphs(tr_page)
    assert len(paras) == 22 and paras[0]["range"] == "1-39" and paras[-1]["range"] == "378-431", [p["range"] for p in paras]
    scans = make_scans()

    # the scribe's colophon (after the double ruling) belongs with the last paragraph on the prism
    for ln in lines:
        if ln["q"] == "colophon":
            ln["qn"] = 377
            ln["colophon"] = True
        else:
            ln["qn"] = qnum(ln["q"])
            assert ln["qn"] is not None, ln

    sections = []
    for p in paras:
        sel = [ln for ln in lines if p["start"] <= ln["qn"] <= p["end"]]
        if not sel:
            print(f"  ETCSL {p['range']}: not on WB 444, skipped")
            continue
        parts, faces, prev = [], [], None
        for ln in sel:
            fc = (ln["surface"], ln["column"])
            if fc != prev:
                parts.append(f"<em>[face {fc[0]}, column {ROMAN[fc[1]]}]</em>")
                prev = fc
                if fc[0] not in faces:
                    faces.append(fc[0])
            lab = "colophon" if ln.get("colophon") else str(ln["q"]).lstrip("0")
            parts.append(f"<sup>{lab}</sup>{atf_html(ln['atf'])}")
        first, last = sel[0], sel[-1]
        span = (f"face {first['surface']} col. {ROMAN[first['column']]} {first['line']}"
                f" to face {last['surface']} col. {ROMAN[last['column']]} {last['line']}")
        cols = []
        for ln in sel:
            c = f"face {ln['surface']} column {ROMAN[ln['column']]}"
            if c not in cols:
                cols.append(c)
        note = (f"WB 444 {span} ({len(sel)} prism lines; {', '.join(cols)}). "
                f"The prism lines were matched to ETCSL lines {p['range']} through the CDLI transliteration's own links "
                "to the composite (Q000371, ETCSL numbering). Faces checked on the photograph: the face crops follow the "
                "CDLI photo order a-d, confirmed by the broken areas the transliteration records. "
                "The English is ETCSL's translation of the composite text: numbers follow this prism unless a note in "
                "italics names another manuscript, and those notes report readings that are not on this prism.")
        if any(ln.get("colophon") for ln in sel):
            note += (" The last line, after the double ruling at the foot of face d column ii, is the scribe's colophon "
                     "(su nu-ur2-{d}nin-szubur in CDLI's ATF); ETCSL does not translate it.").replace(
                "su nu-ur2-{d}nin-szubur", "šu nu-ur₂-{d}nin-šubur")
        if p["range"] == "1-39":
            note += " Face a column i lines 1-39: the kings before the Flood, ending 'a-ma-ru ba-ur3' (then the flood swept over)."
            note = note.replace("ba-ur3", "ba-ur₃")
        sections.append({
            "section": p["range"],
            "original_ref": f"ETCSL 2.1.1 lines {p['range']}; WB 444 {span}",
            "original_text": "<br>\n".join(parts),
            "text": f"<p><sup>{p['range']}</sup> {p['text']}</p>",
            "scan_pages": [scans[f] for f in faces],
            "scan_note": note,
        })

    intro = (
        "<p>The <strong>Sumerian King List</strong> names the cities that held kingship in Sumer and the kings who ruled in each, "
        "from the time when 'the kingship descended from heaven' to the dynasty of Isin. It begins with eight kings in five cities "
        "who ruled for 241,200 years before 'the flood swept over', then lists the dynasties after the Flood, starting with Kish. "
        "The list was compiled from older sources and survives on many Old Babylonian manuscripts.</p>"
        "<p>The <strong>Weld-Blundell Prism</strong> (Ashmolean Museum AN1923.444, W-B 444) is the most complete copy. "
        "It is a four-sided clay prism with two columns of text on each face, eight columns in all, written in the Old Babylonian period. "
        "The last king it names is Sin-magir of Isin, so it was written in his reign or soon after (about 1800 BCE). "
        "A hole runs through the prism from top to bottom, probably for a spindle so that it could be turned. "
        "S. Langdon published it in 1923 (OECT 2).</p>"
        "<p>Each section below is one paragraph of the ETCSL translation, headed by its composite line range. "
        "The Sumerian is the transliteration of the signs on this prism (CDLI), with each prism line numbered by the composite line it matches "
        "and grouped under the face and column where it stands. The photograph for each section is the face of the prism that carries it. "
        "The English is the ETCSL translation of the composite text: its numbers follow this prism unless a note names another manuscript.</p>"
        "<p><strong>Gaps.</strong> The prism has broken areas at the top of several columns (bracketed in the transliteration). "
        "The closing summary of the list (ETCSL lines 378-431, totals of kings and years for each city) is not on this prism and is not shown.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "Sumerian King List: the Weld-Blundell Prism (WB 444)",
        "language": "Sumerian (transliteration) / English",
        "source": "Ashmolean Museum AN1923.444 photograph via CDLI (P384786) + CDLI transliteration of the prism + ETCSL 2.1.1 English translation (CC BY-NC-SA 3.0)",
        "description": "The Sumerian King List on the Weld-Blundell Prism (Ashmolean Museum, c. 1800 BCE), all four faces: the kings before the Flood, the Flood, and the dynasties after it down to Isin.",
        "introduction": intro,
        "translator_notes": [
            "ETCSL's note on the translation: (" + intro_note + ")",
            "Numbers: the prism writes years in the sexagesimal system (e.g. 8(šar₂) = 8 x 3600 = 28,800); ETCSL gives them as decimal numbers.",
            "Transliteration: CDLI ATF rendered in Unicode (sz = š, s, = ṣ, t, = ṭ, sign indices as subscripts). Square brackets enclose broken signs restored by the editor; # marks a damaged sign, ? an uncertain reading, ! a corrected sign, &lt;...&gt; an omitted sign supplied by the editor and &lt;&lt;...&gt;&gt; a sign written in error.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Cuneiform Digital Library Initiative photograph of P384786, {PHOTO_URL} (artifact page {CDLI_PAGE}); cropped to one file per face",
            "scan_license": "Image courtesy of the Ashmolean Museum, University of Oxford (credit printed on the CDLI image). CDLI terms of use (https://cdli.earth/terms-of-use): images are for the non-commercial use of students, scholars and the public; copyright the institution that owns the object",
            "scan_manuscript": "Ashmolean Museum AN1923.444 (W-B 444, 'Weld-Blundell Prism'), clay prism, four faces of two columns each, Old Babylonian (c. 1800 BCE)",
            "scan_mapping": "Face, column and line of every prism line from the CDLI transliteration of P384786; each prism line carries CDLI's link to the composite line (Q000371, ETCSL numbering); sections follow ETCSL translation paragraphs and point at the face(s) that carry those lines. Face order a-d in the photograph checked by eye against the broken areas recorded in the transliteration.",
            "scan_mapping_urls": [CDLI_PAGE, ATF_URL, "https://cdli.earth/artifacts/composites-score/Q000371", ETCSL_C_STATIC],
            "scan_local_paths": [scans[f] for f in "abcd"],
            "original_text_source": f"CDLI transliteration of P384786 (CDLI Literary 000371 ex. 06), {ATF_URL}",
            "original_text_license": "CDLI terms of use: transliterations and translations may be freely copied and re-used according to common academic practice, with reference to CDLI (https://cdli.earth)",
            "translation_source": f"J. A. Black, G. Cunningham, E. Flückiger-Hawker, E. Robson, J. Taylor and G. Zólyomi, The Electronic Text Corpus of Sumerian Literature (Oxford 1998-2006), 2.1.1 'The Sumerian king list: translation', {ETCSL_TR_STATIC} (Unicode display {ETCSL_TR})",
            "translation_license": f"CC BY-NC-SA 3.0 Unported: ETCSL data distributed by the Oxford Text Archive ({OTA}), licence stated at {EPSD_LIT}",
            "translator": "ETCSL (Black, Cunningham, Flückiger-Hawker, Robson, Taylor, Zólyomi)",
            "verified_date": TODAY,
        },
    }
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

    coll = {
        "collection": {
            "key": KEY,
            "prefix": f"verified-{KEY}-",
            "label": "Sumerian King List",
            "group": "Mesopotamia",
            "date_sort": -1800,
            "author_name": "Sumerian scribes (Weld-Blundell Prism, c. 1800 BCE)",
            "source_url": CDLI_PAGE,
            "critical_edition": "CDLI transliteration of the prism (P384786); ETCSL 2.1.1 composite",
            "translator_name": "ETCSL (Black et al., 1998-2006)",
            "original_lang_label": "Sumerian · CDLI transliteration",
            "original_lang_code": "sux",
            "edition_label": "",
            "search_terms": "sumerian king list weld-blundell prism wb 444 antediluvian kings flood kish uruk ur isin",
            "description": "The Sumerian King List on the Weld-Blundell Prism in the Ashmolean Museum: the kings before the Flood, the Flood, and the dynasties after it, shown face by face.",
        },
        "texts": [{
            "id": TID, "slug": TID, "order": 1,
            "title": entry["title"], "author_id": "sumerian-scribes", "language": "Sumerian",
            "era": "Ancient Near East", "tradition": "sumerian", "category": "history",
            "date_approx": "c. 1800 BCE (prism, reign of Sin-magir of Isin or soon after)", "century": -19,
            "source": entry["source"], "description": entry["description"],
            "themes": ["sumerian-king-list", "antediluvian-kings", "flood", "sumer", "kingship", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": scans[f], "caption": f"WB 444, face {f}"} for f in "abcd"]},
        }],
        "authors": [{
            "id": "sumerian-scribes", "name": "Sumerian scribes (anonymous)", "dates": "c. 2600-1700 BCE", "century": -20,
            "era": "Ancient Near East", "tradition": "sumerian", "language": "Sumerian",
            "bio": "The anonymous scribes of Sumer and Babylonia who composed and copied Sumerian literature, from the earliest literary tablets of the mid-third millennium BCE to the Old Babylonian school copies.",
        }],
    }
    COLL.parent.mkdir(parents=True, exist_ok=True)
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID}: {len(sections)} sections; scans {list(scans.values())}")


if __name__ == "__main__":
    main()
