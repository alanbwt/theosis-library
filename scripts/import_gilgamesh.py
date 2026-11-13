#!/usr/bin/env python3
"""
import_gilgamesh.py -- Epic of Gilgamesh from the electronic Babylonian Library
(eBL, LMU Munich), complete Standard Babylonian version (Tablets I-XII), one
entry per tablet of the series.  This file is also the shared engine used by
the other eBL importers (import_enuma-elish.py etc.), which only supply a
WORK configuration and call build_work().

Chain of evidence for every published section
---------------------------------------------
1. ORIGINAL  eBL corpus edition (https://www.ebl.lmu.de/corpus/...).  For every
             line of the poem eBL lists each manuscript that carries it, with
             that manuscript's own column label, its own line number and the
             ATF transliteration of the signs on that manuscript.  We publish
             ONLY that manuscript-level ATF (never eBL's normalised composite
             text), verbatim, minus the separate '#note:' and '$' state lines.
             Licence: CC BY-NC-SA 4.0 (ebl.lmu.de, about/library).
2. ENGLISH   The eBL translation of each line (the '#tr.en:' line of the
             corpus edition; for Gilgamesh by A. R. George, for most other
             works by B. R. Foster).  Same licence as the edition.  The English
             renders eBL's composite text, so it can include words restored
             from other manuscripts; every section says so.
3. SCAN      The photograph of that same manuscript served by eBL's fragment
             photo API (https://www.ebl.lmu.de/api/fragments/<no>/photo).
             British Museum photographs: "(c) The Trustees of the British
             Museum, CC BY-NC-SA 4.0" as stated by eBL.  Photographs of other
             holders that eBL serves (Iraq Museum, Penn Museum, Berlin, Yale,
             Hatay) carry restrictive terms (eBL: "cannot be reproduced without
             the explicit consent ..."); under COLLECTION_SPEC rule 9 (owner's
             instruction 2026-11-12) they are used with credit, but only for
             lines that no British Museum photograph carries.  Open photographs
             from a holder's own site (Yale Peabody CC0 IIIF) are configured per
             work in external_photos.
4. MAPPING   Text-to-image mapping is eBL's own attribution of each line to a
             manuscript (museum number + column + line).  Every manuscript
             used was additionally checked by eye on its photograph
             (PHOTO_CHECKS below): the object is the right one (ink number,
             joined pieces), it has inscribed faces where eBL puts columns, and
             the visible line count is consistent with eBL's line count.
             Manuscripts that failed (wrong photograph, photograph showing only
             one piece of a later join) are listed in EXCLUDED with the reason.
             Where eBL joins pieces that the British Museum photographed
             separately, piece_line_map() places lines on pieces from eBL's own
             documentation (the piece's own transliteration and its parallel-line
             references, notes naming the piece); a section links only the
             photographs of the pieces that carry its lines.  Where eBL documents
             nothing, every photograph of the join is linked and the section says so.

Selecting the witness for each line
-----------------------------------
For each line of a chapter the candidates are the checked, photographed
copies of the work that carry it.  eBL's manuscript types decide what counts
(QC 2026-11-12): commentaries, quotations in other texts (letters, rituals,
god lists, treatises) and parallel texts are never witnesses, and neither is
any line written with commentary/quotation markup (!bs !cm !qt !zz); a
catch-line on a library copy of the previous tablet is the line itself and is
used.  School, excerpt, amulet and 'Varia' tablets are a fallback: used for a
line only when no photographed library copy preserves it as well, and the
section says so.  A dynamic programme then picks, line by line, the candidate
with the most preserved signs (signs outside [ ], not 'x'), with a penalty for
switching manuscript, column or photograph, so that sections are long runs of
consecutive lines on one column of one tablet.  Runs longer than MAX_RUN lines
are split.  Lines with no usable witness are not published and are listed as
gaps in the entry introduction with the reason for each manuscript.

Rendering: eBL's ATF control codes are written out (render_atf); each entry's
notes carry a key to the sign conventions used on that page.  Each section's
scan_note lists the lines that are entirely or partly broken on its tablet,
because the English always translates eBL's composite line.

Face of a column: eBL gives column numbers (i-vi) or o/r.  The face is named
only where it is certain: explicit o/r labels, or a six-column manuscript
(the manuscript has text in column v or vi somewhere in the work, so columns
i-iii are the obverse and iv-vi the reverse).  Otherwise the section names the
column only.

Usage
  python3 scripts/import_gilgamesh.py                    # build all
  python3 scripts/import_gilgamesh.py --chapters SB:XI   # subset
  python3 scripts/import_gilgamesh.py --raw-dir DIR      # where raw eBL photos are cached
  python3 scripts/import_gilgamesh.py --report           # coverage report only, no writes

Writes (key = gilgamesh): translations/published/verified-gilgamesh-*.json,
site/assets/scans/gilgamesh/*.jpg, data/collections/gilgamesh.json.
Downloads are cached in data/sources/gilgamesh/ (chapter and fragment JSON).
"""

import argparse
import html
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
COLL = ROOT / "data" / "collections"
EBL_API = "https://www.ebl.lmu.de/api"
EBL_WEB = "https://www.ebl.lmu.de"
UA = "Mozilla/5.0 TheosisLibrary/1.0 (+https://theosislibrary.com)"
TODAY = date.today().isoformat()

STAGES = {"SB": "Standard Babylonian", "OB": "Old Babylonian", "MB": "Middle Babylonian",
          "NA": "Neo-Assyrian", "MA": "Middle Assyrian", "NB": "Neo-Babylonian"}
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8}
BM_LICENCE = "(c) The Trustees of the British Museum, CC BY-NC-SA 4.0 (terms as stated by eBL for British Museum photographs)"
EBL_LICENCE = "CC BY-NC-SA 4.0 (eBL editions, https://www.ebl.lmu.de/about/library)"

MAX_RUN = 30          # longest section, in poem lines
MAX_GAP = 12          # a run may continue across this many lines that no checked witness carries
SWITCH_PENALTY = 8.0  # in preserved signs
SPLIT_FACTOR = 0.5    # score multiplier for joins photographed in several pieces
MAX_SIDE = 2600       # px, long side of published scans

# eBL manuscript types (chapter JSON, manuscripts[].type).  Only copies of the poem itself are
# witnesses.  Commentaries quote words of a line and add explanations; quotations embed a line in
# another text (a letter, a ritual, a god list); neither carries the poem line as such, so they are
# never used (QC 2026-11-12).  Excerpt-type tablets (school exercises, excerpt tablets, amulets,
# 'Varia') copy a passage of the poem; they are a fallback only: used for a line only when no
# photographed library copy preserves it as well, only when eBL's transliteration of the line has no
# commentary or quotation markup (i.e. the tablet carries the line verbatim), and the section says so.
POEM_TYPES = {"Library", "None", ""}
EXCERPT_TYPES = {
    "School": "a school tablet (a scribal exercise that copies an excerpt of the text)",
    "Excerpt": "an excerpt tablet (a tablet that copies an excerpt of the text)",
    "Amulet": "an amulet tablet inscribed with an excerpt of the text",
    "Varia": "a tablet that eBL classes as 'Varia' (not a library copy of the series)",
}
NON_POEM_TYPES = {
    "Commentary": "commentary",
    "Quotation": "quotation in another text",
    "Parallel": "parallel text",
    "Lexical": "lexical list",
}
COMMENTARY_MARK_RE = re.compile(r"(?<!\S)!(?:bs|cm|qt|zz)(?!\S)")

# Photograph holders other than the British Museum whose eBL photographs may be used under the
# library's photo rule (COLLECTION_SPEC rule 9, owner's instruction 2026-11-12: museum photographs of
# the object may be used with credit even when the terms are restrictive or unstated).  Terms as
# stated on eBL's About page (https://www.ebl.lmu.de/about/library, section III. Photographs).
EBL_PHOTO_TERMS = ("eBL: 'The images cannot be reproduced without the explicit consent of the funding projects "
                   "and institutions, as well as the institutions in which the cuneiform tablets are kept.'")
HOLDERS = {
    "THE_BRITISH_MUSEUM": ("British Museum", BM_LICENCE),
    "THE_IRAQ_MUSEUM": ("Iraq Museum", "Photograph by A. A. Fadhil and N. Jabbar (Iraq Museum - eBL Project), "
                        "displayed by eBL by permission of the State Board of Antiquities and Heritage and The Iraq "
                        "Museum; " + EBL_PHOTO_TERMS + " Used with credit under the library's photo rule (non-commercial)."),
    "PENN_MUSEUM": ("Penn Museum", "Photograph of the Penn Museum (University of Pennsylvania Museum of Archaeology and "
                    "Anthropology) as served by eBL; terms not stated beyond " + EBL_PHOTO_TERMS +
                    " Used with credit under the library's photo rule (non-commercial)."),
    "YALE_PEABODY_COLLECTION": ("Yale Peabody Museum", "Photograph by K. Wagensonner (Yale Babylonian Collection), "
                                "used by eBL with the permission of the Yale Peabody Museum; " + EBL_PHOTO_TERMS +
                                " Used with credit under the library's photo rule (non-commercial)."),
    "HATAY_ARCHAEOLOGY_MUSEUM": ("Hatay Archaeology Museum", "Photograph of the Hatay Archaeology Museum, Antakya, "
                                 "as served by eBL; " + EBL_PHOTO_TERMS +
                                 " Used with credit under the library's photo rule (non-commercial)."),
    "VORDERASIATISCHES_MUSEUM": ("Vorderasiatisches Museum, Berlin", "Photograph of the Vorderasiatisches Museum, "
                                 "Staatliche Museen zu Berlin, as served by eBL; " + EBL_PHOTO_TERMS +
                                 " Used with credit under the library's photo rule (non-commercial)."),
}
HOLDER_NAMES = {
    "THE_BRITISH_MUSEUM": "British Museum", "THE_IRAQ_MUSEUM": "Iraq Museum", "PENN_MUSEUM": "Penn Museum",
    "YALE_PEABODY_COLLECTION": "Yale Peabody Museum", "VORDERASIATISCHES_MUSEUM": "Vorderasiatisches Museum, Berlin",
    "MUSEUM_OF_ANATOLIAN_CIVILIZATIONS": "Museum of Anatolian Civilizations, Ankara",
    "ISTANBUL_ARKEOLOJI_MUSEUM": "Istanbul Archaeological Museum", "ASHMOLEAN_MUSEUM": "Ashmolean Museum",
    "LOUVRE": "Louvre", "SANLIURFA_MUSEUM": "Şanlıurfa Museum", "PIERPONT_MORGAN": "Morgan Library",
    "ANCIENT_CULTURES_CHICAGO": "Institute for the Study of Ancient Cultures, Chicago",
    "NATIONAL_MUSEUM_OF_WORLD_WRITING_SYSTEMS": "National Museum of World Writing Systems, Korea",
    "HATAY_ARCHAEOLOGY_MUSEUM": "Hatay Archaeology Museum", "MUSEUM_OF_MONTSERRAT": "Museum of Montserrat",
    "DE_LIAGRE_BOEHL_COLLECTION": "de Liagre Böhl Collection, Leiden", "KUNSTHISTORISCHES_MUSEUM": "Kunsthistorisches Museum, Vienna",
}


# ---------------------------------------------------------------------------
# Downloads (curl -4: urllib hangs on IPv6 to ebl.lmu.de on this host)
# ---------------------------------------------------------------------------
_DROP = {"atfTokens", "reconstructionTokens", "signs", "alignment"}


def _slim(o):
    if isinstance(o, dict):
        return {k: _slim(v) for k, v in o.items() if k not in _DROP}
    if isinstance(o, list):
        return [_slim(x) for x in o]
    return o


def _curl(url, timeout=300):
    r = subprocess.run(["curl", "-4", "-sL", "--compressed", "-m", str(timeout), "-A", UA, url],
                       capture_output=True)
    return r.stdout


def ebl_chapter(src, genre, cat, idx, stage, name):
    p = src / "ebl" / f"chapter_{stage}_{name}.json"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = f"{EBL_API}/texts/{genre}/{cat}/{idx}/chapters/{urllib.parse.quote(stage)}/{urllib.parse.quote(name)}"
        d = json.loads(_curl(url))
        p.write_text(json.dumps(_slim(d), ensure_ascii=False), encoding="utf-8")
        time.sleep(1.5)
    return json.loads(p.read_text(encoding="utf-8"))


_FRAG_KEEP = {"museumNumber", "publication", "description", "collection", "museum", "width", "length",
              "thickness", "joins", "folios", "notes", "references", "genres", "script",
              "externalNumbers", "archaeology", "atf", "hasPhoto", "traditionalReferences", "cdliImages"}


def ebl_fragment(src, museum):
    p = src / "frag" / f"frag_{museum}.json"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        d = json.loads(_curl(f"{EBL_API}/fragments/{urllib.parse.quote(museum)}", 120) or b"{}")
        if "museumNumber" in d:
            d = {k: v for k, v in d.items() if k in _FRAG_KEEP}
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.8)
    return json.loads(p.read_text(encoding="utf-8"))


def mus_str(mn):
    return mn["prefix"] + "." + mn["number"] + ("." + mn["suffix"] if mn.get("suffix") else "")


def scan_name(key, museum):
    return f"{key}-{museum.replace(',', '-').replace(' ', '')}.jpg"


def ensure_scan(key, museum, raw_dir, dry=False):
    """Download the eBL photograph (once) and store a JPEG, long side <= MAX_SIDE."""
    rel = f"{key}/{scan_name(key, museum)}"
    dest = SCANS / rel
    if dest.exists() and dest.stat().st_size > 10_000:
        return rel
    if dry:
        return rel
    raw = Path(raw_dir) / f"photo_{museum}.jpg"
    if not raw.exists() or raw.stat().st_size < 10_000:
        raw.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-4", "-sL", "-m", "900", "-A", UA, "-o", str(raw),
                        f"{EBL_API}/fragments/{urllib.parse.quote(museum)}/photo"], check=True)
        time.sleep(1.5)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(raw)
    im.draft("RGB", (MAX_SIDE, MAX_SIDE))
    im = im.convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=85, optimize=True, progressive=True)
    return rel


def ensure_crop(key, museum, face, box, raw_dir, dry=False):
    """One face of an eBL photograph, cropped (box = fractions x0, y0, x1, y1 of the photograph)."""
    rel = f"{key}/{scan_name(key, museum)[:-4]}-{face.replace(' ', '-')}.jpg"
    dest = SCANS / rel
    if dest.exists() and dest.stat().st_size > 10_000 or dry:
        return rel
    ensure_scan(key, museum, raw_dir)  # makes sure the raw photograph is downloaded
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(Path(raw_dir) / f"photo_{museum}.jpg").convert("RGB")
    W, H = im.size
    im = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    im.save(dest, "JPEG", quality=85, optimize=True, progressive=True)
    return rel


def ensure_external(key, spec, dry=False):
    """Photograph from another open source (e.g. Yale IIIF), stored once."""
    rel = f"{key}/{spec['file']}"
    dest = SCANS / rel
    if dest.exists() and dest.stat().st_size > 10_000 or dry:
        return rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".download")
    subprocess.run(["curl", "-4", "-sL", "-m", "600", "-A", UA, "-o", str(tmp), spec["url"]], check=True)
    time.sleep(1.0)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(tmp).convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    im.save(dest, "JPEG", quality=85, optimize=True, progressive=True)
    tmp.unlink()
    return rel


# ---------------------------------------------------------------------------
# ATF and translation helpers
# ---------------------------------------------------------------------------
def clean_atf(atf):
    """The manuscript's line as eBL prints it: first ATF line(s) without the
    separate '#note:' and '$' (state/ruling) lines.  Signs are untouched."""
    keep = [ln.strip() for ln in atf.split("\n")
            if ln.strip() and not ln.lstrip().startswith(("#", "$"))]
    return " ".join(keep).strip()


def preserved_signs(atf):
    out, depth = [], 0
    for ch in atf:
        if ch == "[":
            depth += 1
            out.append(" ")
        elif ch == "]":
            depth = max(0, depth - 1)
            out.append(" ")
        else:
            out.append(ch if depth == 0 else " ")
    toks = [t.strip("#?!*<>()°\\") for t in re.split(r"[\s\-.:{}+]+", "".join(out))]
    return sum(1 for t in toks if t and t not in ("x", "X", "...", "…", "&", "|", "/", "ø") and not t.startswith(("%", "!", "$", "&")))


# ---------------------------------------------------------------------------
# Plain rendering of eBL ATF (QC 2026-11-12: no raw control codes on the page)
# ---------------------------------------------------------------------------
# eBL-ATF reference: https://github.com/ElectronicBabylonianLiterature/ebl-api/blob/master/docs/ebl-atf.md
#   !bs !cm !qt !zz  commentary protocols (base text / commentary / quotation / uncertain): dropped
#                    (they only occur in commentaries and quotations, which are no longer used)
#   ($___$)          tabulation: shown as "(blank space)"
#   |  (alone)       line break on the manuscript: shown as "(line break)"
#   &  &n            column separator (&n: the next column spans n columns): shown as " | "
#   {( ... )}        document-oriented gloss: shown as "(gloss: ...)"
#   °a\b°            erasure (a erased, b written over it): described in words
#   %n %sb ...       language/register shifts: dropped
#   ø                word omitted: "(word omitted)"
ATF_KEY = [  # (id, text) in display order; the first five are always listed
    ("[]", "[ ] broken away"), ("x", "x illegible sign"), ("#", "# damaged sign"), ("?", "? uncertain reading"),
    ("!", "! sign corrected by the editor"), ("*", "* collated sign"), ("...", "... broken signs of unknown number"),
    ("()", "( ) signs perhaps broken away"), ("{}", "{ } determinative"), ("{+}", "{+ } phonetic gloss"),
    ("<>", "< > sign omitted by the scribe, supplied by the editor"), ("<()>", "<( )> sign left out on purpose by the scribe"),
    ("<<>>", "<< >> sign written in error by the scribe"), ("/", "/ alternative readings"),
    (":", ": divider sign written on the tablet"), ("@", "@v and similar: variant or modified form of a sign"),
    ("|", "| division between the parts of a line written in separate columns on the tablet"),
    ("lb", "(line break) the line runs on to the next line of the tablet"),
    ("tab", "(blank space) a space left by the scribe"),
    ("gloss", "(gloss: ...) a note written by the scribe in small signs or in the margin"),
]
ATF_KEY_BASE = {"[]", "x", "#", "?", "!"}
_ATF_SPECIAL = re.compile(
    r"(?P<prot>(?<!\S)!(?:bs|cm|qt|zz)(?!\S))"
    r"|(?P<tab>\(\$___\$\))"
    r"|(?P<lb>(?<!\S)\|(?!\S))"
    r"|(?P<col>(?<!\S)&(?P<span>\d*)(?!\S))"
    r"|(?P<gloss>\{\((?P<gbody>.*?)\)\})"
    r"|(?P<eras>°(?P<erased>[^°\\]*)\\(?P<over>[^°]*)°)"
    r"|(?P<shift>(?:(?<=\s)|(?<=\[)|^)%[a-z][a-z0-9]*(?=\s|$))"
    r"|(?P<omit>(?<!\S)ø(?!\S))"
)


def _atf_symbols(plain):
    s = set()
    if "[" in plain or "]" in plain:
        s.add("[]")
    if re.search(r"(?<![\w])[xX](?![\w])", plain):
        s.add("x")
    for ch, k in (("#", "#"), ("?", "?"), ("*", "*"), ("/", "/"), ("@", "@")):
        if ch in plain:
            s.add(k)
    if re.search(r"[\w\])]!", plain):
        s.add("!")
    if "..." in plain or "…" in plain:
        s.add("...")
    if "{+" in plain:
        s.add("{+}")
    if re.search(r"\{(?![+(])", plain):
        s.add("{}")
    if "<<" in plain:
        s.add("<<>>")
    if "<(" in plain:
        s.add("<()>")
    if re.search(r"(?<![<])<(?![<(])", plain):
        s.add("<>")
    if re.search(r"(?<![{<])\((?!\$)", plain):
        s.add("()")
    if re.search(r"(?<!\S):(?:[.'\"?:])?(?!\S)", plain):
        s.add(":")
    return s


def render_atf(atf):
    """eBL manuscript ATF -> (HTML for the page, set of ATF_KEY ids that the reader needs).
    Signs are untouched; only eBL's control codes are replaced by plain wording."""
    out, syms, pos = [], set(), 0
    note = lambda t: f'<span class="lacuna">({t})</span>'
    for m in _ATF_SPECIAL.finditer(atf):
        plain = atf[pos:m.start()]
        out.append(html.escape(plain, quote=False))
        syms |= _atf_symbols(plain)
        pos = m.end()
        if m.group("prot") or m.group("shift"):
            continue
        if m.group("tab"):
            out.append(note("blank space"))
            syms.add("tab")
        elif m.group("lb"):
            out.append(note("line break"))
            syms.add("lb")
        elif m.group("col"):
            out.append("|")
            syms.add("|")
        elif m.group("gloss"):
            body = m.group("gbody").strip()
            out.append("(gloss: " + html.escape(body, quote=False) + ")")
            syms |= _atf_symbols(body)
            syms.add("gloss")
        elif m.group("eras"):
            er, ov = m.group("erased").strip(), m.group("over").strip()
            syms |= _atf_symbols(er + " " + ov)
            if ov and er:
                out.append(html.escape(ov, quote=False) + " " + note("written over erased " + html.escape(er, quote=False)))
            elif ov:
                out.append(html.escape(ov, quote=False) + " " + note("written over an erasure"))
            elif er:
                out.append(note("erased: " + html.escape(er, quote=False)))
            else:
                out.append(note("erasure"))
        elif m.group("omit"):
            out.append(note("word omitted"))
    plain = atf[pos:]
    out.append(html.escape(plain, quote=False))
    syms |= _atf_symbols(plain)
    s = re.sub(r"\s{2,}", " ", "".join(out)).strip()
    return s, syms


def atf_key_line(syms):
    used = ATF_KEY_BASE | set(syms)
    return "Signs in the Akkadian: " + "; ".join(t for k, t in ATF_KEY if k in used) + "."


_TR_RE = re.compile(r"^#tr\.en(?:\.\(([^)]*)\))?:\s?(.*)$")


def english_of(line):
    """(text, extent) from the eBL line translation; extent = last line number covered, if given."""
    for ln in (line.get("translation") or "").split("\n"):
        m = _TR_RE.match(ln.strip())
        if m:
            return m.group(2).strip(), m.group(1)
    return None, None


def tr_html(t):
    s = html.escape(t, quote=False)
    s = re.sub(r"@i\{([^{}]*)\}", r"<em>\1</em>", s)
    s = re.sub(r"@(?:akk|sux|es)\{([^{}]*)\}", r"<em>\1</em>", s)
    s = re.sub(r"@bib\{[^{}]*\}", "", s)
    s = re.sub(r"@[a-z]+\{([^{}]*)\}", r"\1", s)
    return s.strip()


def col_label(labels):
    return " ".join(labels).strip()


# ---------------------------------------------------------------------------
# Manuscript table
# ---------------------------------------------------------------------------
def siglum_of(ms, rx=None):
    if rx:
        m = re.search(rx, ms.get("notes") or "")
        return m.group(1).strip() if m else ""
    for o in ms.get("oldSigla") or []:
        if o.get("siglum"):
            return o["siglum"]
    m = re.search(r"George 2003 ms\.? ([^;,\s]+)", ms.get("notes") or "")
    return m.group(1) if m else ""


def six_column(work_chapters, museum):
    """True if this manuscript has text in column v or vi anywhere in the work."""
    for ch in work_chapters:
        ids = {m["id"] for m in ch["manuscripts"] if m["museumNumber"] == museum}
        for l in ch["lines"]:
            for v in l["variants"]:
                for m in v["manuscripts"]:
                    if m["manuscriptId"] in ids and any(x.rstrip("?") in ("v", "vi") for x in m["labels"]):
                        return True
    return False


def face_and_col(labels, sixcol):
    lab = [x for x in labels if x]
    if not lab:
        return "", ""
    face, col = "", ""
    for x in lab:
        xx = x.rstrip("?").rstrip(".")
        if xx in ROMAN and face and face.endswith("edge"):
            col = x
            continue
        if xx in ("o", "obv"):
            face = "obverse"
        elif xx in ("r", "rev"):
            face = "reverse"
        elif xx in ("e", "le", "ue", "be", "l.e", "u.e", "lo.e", "b.e"):
            face = {"e": "edge", "le": "left edge", "ue": "upper edge", "be": "lower edge", "l.e": "left edge",
                    "u.e": "upper edge", "lo.e": "lower edge", "b.e": "lower edge"}[xx]
        elif xx in ROMAN:
            col = x
            if sixcol and not face:
                face = "obverse" if ROMAN[xx] <= 3 else "reverse"
    return face, col


def where_text(face, col):
    if face and col:
        return f"{face}, column {col}"
    if col:
        return f"column {col}"
    if face:
        return face
    return "the inscribed face"


# ---------------------------------------------------------------------------
# Core: one chapter -> sections
# ---------------------------------------------------------------------------
def ms_type(ms):
    return (ms.get("type") or "").strip()


def catchline_of(ms, chapter, all_chapters):
    """eBL types a catch-line (the first line of the next tablet of a series, written at the end of a
    library copy of the previous tablet) as a 'Quotation'.  It is the poem's own line on a copy of the
    poem, so it is a witness.  Recognised when eBL's notes say 'catchline', or when the same tablet is
    a library or school copy of another chapter of this work; never for commentaries or texts that
    cite the line ('cites', 'CCP', 'Commentary', 'Letter', 'treatise', 'God List', 'Ritual').
    Returns the chapter name of which the tablet is a copy, or '' if not a catch-line."""
    if ms_type(ms) != "Quotation" or not ms.get("museumNumber"):
        return ""
    notes = ms.get("notes") or ""
    if re.search(r"cites|CCP|[Cc]ommentary|Letter|treatise|God List|Ritual|incipit", notes):
        return ""
    for ch in all_chapters:
        if ch is chapter:
            continue
        for m in ch["manuscripts"]:
            if m["museumNumber"] == ms["museumNumber"] and ms_type(m) in POEM_TYPES | set(EXCERPT_TYPES):
                return f"{ch.get('_stage_abbr', '')} {ch['name']}".replace(" -", "")
    if re.search(r"catch-?line", notes, re.I):
        return "?"
    return ""


def chapter_tag(chapter):
    return f"{chapter.get('_stage_abbr', '')}:{chapter['name']}"


def idx_ranges(idxs, lines):
    """Chapter line indices -> 'a-b, c' in eBL line numbers (runs of consecutive lines merged)."""
    out = []
    for i in sorted(set(idxs)):
        if out and out[-1][1] == i - 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    parts = []
    for a, b in out:
        na, nb = lines[a]["number"], lines[b]["number"]
        if a == b:
            parts.append(na)
        else:
            parts.append(f"{na}{' to ' if ('-' in na or '-' in nb) else '-'}{nb}")
    return ", ".join(parts)


_TOK_SPLIT = re.compile(r"[\s\-.:{}+]+")


def sign_tokens(atf, preserved_only):
    """Sign readings of an ATF line, lower-cased and without flags; preserved_only drops what is in [ ]."""
    if preserved_only:
        out, depth = [], 0
        for ch in atf:
            if ch == "[":
                depth += 1
                out.append(" ")
            elif ch == "]":
                depth = max(0, depth - 1)
                out.append(" ")
            else:
                out.append(ch if depth == 0 else " ")
        atf = "".join(out)
    atf = atf.replace("[", "").replace("]", "")
    toks = [t.strip("#?!*<>()°\\").lower() for t in _TOK_SPLIT.split(atf)]
    return [t for t in toks if t and t not in ("x", "...", "…", "&", "|", "/", "ø")
            and not t.startswith(("%", "!", "$", "&", "@"))]


_SUBSCRIPT = str.maketrans("", "", "₀₁₂₃₄₅₆₇₈₉ₓ")


def _same_sign(x, y):
    """x (a piece's reading, possibly a sign cut by a break) matches y (eBL's reading for the join)."""
    x, y = x.translate(_SUBSCRIPT), y.translate(_SUBSCRIPT)
    return x == y or (len(x) < len(y) and (y.startswith(x) or y.endswith(x)))


def _lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if _same_sign(x, y) else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def _roman(n):
    out = ""
    for v, r in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def piece_line_map(work, src, chapters):
    """Joins that the British Museum photographed in separate pieces: which lines each separately
    photographed piece carries, from eBL's own documentation only:
      (a) the piece's own eBL transliteration (fragment ATF): its parallel-line references
          ('// L I.4 SB "X" 308'), or a sign-by-sign match against eBL's corpus lines for the join
          (a piece line with at least 2 preserved signs, at least 3/4 of which occur in order in
          exactly one corpus line);
      (b) notes in eBL's corpus edition that name the piece (e.g. 'preserved in K.19050');
      (c) 'piece_lines' in the work configuration (visual checks).
    Returns {main: {piece: {"mapped": bool, "lines": {chapter_tag: {line number: only_on_piece}}}}}.
    'mapped' means the piece's extent is documented: every line of its own transliteration with 3 or
    more preserved signs was located (lines with 1-2 legible signs are traces that eBL does not place).
    only_on_piece is True when every preserved sign of eBL's line for the join is accounted for by the
    piece's own transliteration (the line is then not on the main piece)."""
    out = {}
    cfg = work.get("piece_lines") or {}
    g, c, i = work["ebl_text"]
    text_ref = f"{g} {_roman(int(c))}.{i}"
    for main, pieces in (work.get("split_photos") or {}).items():
        res = {}
        for p in pieces:
            frag = ebl_fragment(src, p)
            plines = []   # [tokens, [(stage, chapter, line) parallels]]
            for ln in (frag.get("atf") or "").split("\n"):
                pm_ = re.match(r'^\s*//\s*(\S+ \S+) (\S+) "([^"]*)" (\S+)', ln)
                if pm_ and plines:
                    if pm_.group(1) == text_ref:
                        plines[-1][1].append((pm_.group(2), pm_.group(3), pm_.group(4)))
                    continue
                mm = re.match(r"^\s*([^\s.@$#&/]*\d[^\s.]*)\.\s+(.*)$", ln)
                if mm:
                    plines.append([sign_tokens(mm.group(2), True), []])
            has_atf = bool(plines)
            located_all = True
            info = {"lines": {}}
            per_tag = {}
            for ch in chapters:
                tag = chapter_tag(ch)
                ids = {m["id"] for m in ch["manuscripts"] if m["museumNumber"] == main}
                if not ids:
                    continue
                rows = []
                for l in ch["lines"]:
                    for v in l["variants"]:
                        for m in v["manuscripts"]:
                            if m["manuscriptId"] in ids and (m.get("atf") or "").strip():
                                rows.append((l["number"], m["atf"]))
                per_tag[tag] = (ch, rows)
            for toks, pars in plines:
                where = None
                for st, chn, num in pars:
                    t2 = f"{st}:{chn}"
                    if t2 in per_tag and any(n == num for n, _ in per_tag[t2][1]):
                        where = (t2, num)
                        break
                if where is None and len(toks) >= 2:
                    scored = []
                    for t2, (_ch, rows) in per_tag.items():
                        for num, atf in rows:
                            k = _lcs(toks, sign_tokens(clean_atf(atf), False))
                            if k >= 2 and k >= 0.75 * len(toks):
                                scored.append((k, t2, num))
                    if scored:
                        best = max(x[0] for x in scored)
                        top = [x for x in scored if x[0] == best]
                        if len(top) == 1:
                            where = (top[0][1], top[0][2])
                if where is None:
                    if len(toks) >= 3:
                        located_all = False
                    continue
                t2, num = where
                atf = dict(per_tag[t2][1])[num]
                rest = sign_tokens(clean_atf(atf), True)
                for t in toks:
                    if t in rest:
                        rest.remove(t)
                got = info["lines"].setdefault(t2, {})
                got[num] = got.get(num, True) and not rest
            for t2, (_ch, rows) in per_tag.items():
                for num, atf in rows:
                    if re.search(r"#note:.*\b" + re.escape(p) + r"\b", atf):
                        info["lines"].setdefault(t2, {}).setdefault(num, False)
            pc = cfg.get(main, {}).get(p) or {}
            for t2, nums in pc.items():
                if t2 == "note":
                    continue
                if t2 == "labels":
                    # configured by visual check: the piece carries the lines of these columns/faces
                    for t3, (ch, _rows) in per_tag.items():
                        ids = {m["id"] for m in ch["manuscripts"] if m["museumNumber"] == main}
                        for l in ch["lines"]:
                            for v in l["variants"]:
                                for m in v["manuscripts"]:
                                    if m["manuscriptId"] in ids and (m["labels"] or [""])[0] in nums:
                                        info["lines"].setdefault(t3, {}).setdefault(l["number"], False)
                    continue
                for num in nums:
                    info["lines"].setdefault(t2, {}).setdefault(num, False)
            # a piece covers a continuous stretch of the tablet: lines of the join between the first and the
            # last line located on it run across it as well (e.g. the first half of a tablet line 6'a whose
            # second half 6'b is on the piece)
            for t2, got in info["lines"].items():
                order = [n for n, _ in per_tag[t2][1]]
                pos = [order.index(n) for n in got if n in order]
                if pos:
                    for n in order[min(pos):max(pos) + 1]:
                        got.setdefault(n, False)
            info["mapped"] = (has_atf and located_all) or p in cfg.get(main, {})
            info["note"] = (cfg.get(main, {}).get(p) or {}).get("note", "")
            res[p] = info
        out[main] = res
    return out


def photos_for_line(main, u, pmap, tag, num):
    """Photographs (museum numbers) that show line `num` of manuscript `main`, and whether the
    attribution to pieces is documented."""
    pieces = u["photos"][1:]
    if not pieces:
        return (main,), True
    info = pmap.get(main, {})
    shown, documented = [], True
    only_piece = False
    for p in pieces:
        pi = info.get(p)
        if not pi or not pi["mapped"]:
            shown.append(p)
            documented = False
            continue
        if num in pi["lines"].get(tag, {}):
            shown.append(p)
            only_piece = only_piece or pi["lines"][tag][num]
    if only_piece and documented and shown:
        return tuple(shown), True
    return (main,) + tuple(shown), documented


GAP_CATS = [  # (category, heading used in the list of lines not shown), in display order
    ("nophoto", "no photograph in eBL"),
    ("notfrag", "not in the eBL Fragmentarium (no photograph there)"),
    ("excluded", "photograph does not show these lines (visual check)"),
    ("wrongphoto", "eBL's photograph shows a different object"),
    ("unchecked", "photograph not checked"),
    ("extskip", "its photographs do not show which lines these are"),
    ("partface", "its photograph shows only part of this face, and the lines cannot be located on it"),
    ("Commentary", "commentary"),
    ("Quotation", "quotation in another text"),
    ("Parallel", "parallel text"),
    ("Lexical", "lexical list"),
    ("markup", "line written with commentary or quotation markup"),
    ("unnumbered", "unnumbered manuscript"),
]


def gap_reason(work, src, ms, atf, usable):
    """(category, label) for a manuscript that carries a line that is not shown."""
    museum = ms["museumNumber"]
    t = ms_type(ms)
    if t in NON_POEM_TYPES and not ms.get("_catch"):
        return t, museum
    if COMMENTARY_MARK_RE.search(atf):
        return "markup", museum
    if not museum:
        return "unnumbered", "unnumbered"
    if museum in work["excluded"]:
        return "excluded", museum
    if museum in (work.get("excluded_faces") or {}):
        return "partface", museum
    if museum in (work.get("external_photos") or {}):
        return "extskip", museum
    f = ebl_fragment(src, museum)
    if not f.get("museumNumber"):
        return "notfrag", museum
    holder = HOLDER_NAMES.get(f.get("museum") or "", "")
    lab = museum + (f" ({holder})" if holder and holder != "British Museum" else "")
    if not f.get("hasPhoto"):
        return "nophoto", lab
    if "photo shows" in ((f.get("notes") or {}).get("text") or ""):
        return "wrongphoto", lab
    return "unchecked", lab


def chapter_sections(work, chapter, all_chapters, usable, raw_dir, dry=False, log=print):
    """Return (sections, coverage dict)."""
    key = work["key"]
    src = work["_src"]
    tag = chapter_tag(chapter)
    pmap = work.get("_pmap") or {}
    msinfo = {}
    for m in chapter["manuscripts"]:
        msinfo[m["id"]] = m
    lines = chapter["lines"]
    num_idx = {l["number"]: i for i, l in enumerate(lines)}
    cands_by_line = []
    for i, l in enumerate(lines):
        cands = []
        for v in l["variants"]:
            for m in v["manuscripts"]:
                raw_atf = m.get("atf") or ""
                if not raw_atf.strip() or raw_atf.lstrip().startswith("$"):
                    continue
                atf = clean_atf(raw_atf)
                if not atf:
                    continue
                ms = msinfo.get(m["manuscriptId"])
                if not ms:
                    continue
                catch = catchline_of(ms, chapter, all_chapters)
                if (ms_type(ms) in NON_POEM_TYPES and not catch) or COMMENTARY_MARK_RE.search(atf):
                    continue   # commentary / quotation: not the poem line as such
                museum = ms["museumNumber"]
                if museum not in usable:
                    continue
                if (m["labels"] or [""])[0] in (work.get("excluded_faces") or {}).get(museum, {}):
                    continue   # this face cannot be located on the photograph (see the importer)
                u = usable[museum]
                fkey = None
                if u.get("external") and u["external"].get("face_rule"):
                    # several separately photographed fragments of one manuscript (configured per line)
                    fkey = u["external"]["face_rule"](m["labels"], m["number"])
                    if not fkey:
                        continue
                    photos, documented = (f"{museum}|{fkey}",), True
                else:
                    photos, documented = photos_for_line(museum, u, pmap, tag, l["number"])
                kept = preserved_signs(atf)
                sc = (kept + 1.0) * (SPLIT_FACTOR if len(photos) > 1 else 1.0)
                fix = (work.get("ms_line_fix") or {}).get((tag, l["number"], museum))
                cands.append({"state": (m["manuscriptId"], col_label(m["labels"]), photos), "score": sc, "atf": atf,
                              "kept": kept, "ms_line": fix[0] if fix else m["number"], "ms_line_note": fix[1] if fix else "", "labels": m["labels"], "museum": museum,
                              "ms": ms, "excerpt": ms_type(ms) in EXCERPT_TYPES, "photos": photos,
                              "documented": documented, "restricted": bool(u.get("restricted")), "catch": catch,
                              "face_key": fkey})
        if any(not c["restricted"] for c in cands):
            # photographs under restrictive terms (rule 9) only where no openly licensed photograph carries the line
            cands = [c for c in cands if not c["restricted"]]
        best_poem = max((c["kept"] for c in cands if not c["excerpt"]), default=None)
        if best_poem is not None:
            # excerpt-type tablets only where no photographed library copy preserves the line as well
            cands = [c for c in cands if not c["excerpt"] or c["kept"] > best_poem]
        cands_by_line.append(cands)

    # dynamic programme
    NEG = -1e18
    V = []      # per line: {state: (value, came_from_same_state)}
    T = []      # best total up to line i
    for i, cands in enumerate(cands_by_line):
        prevV = V[i - 1] if i else {}
        prevT = T[i - 1] if i else 0.0
        if not cands:
            # a line no checked witness carries: transparent, so a run on one tablet can
            # continue across it (the tablet does not carry the line either)
            V.append({st: (v[0], True, None) for st, v in prevV.items()})
            T.append(prevT)
            continue
        cur = {}
        for c in cands:
            st = c["state"]
            cont = prevV[st][0] + c["score"] if st in prevV else NEG
            new = prevT - SWITCH_PENALTY + c["score"]
            val, same = (cont, True) if cont >= new else (new, False)
            if st not in cur or val > cur[st][0]:
                cur[st] = (val, same, c)
        V.append(cur)
        T.append(max((v[0] for v in cur.values()), default=prevT))
    chosen = [None] * len(lines)
    i = len(lines) - 1
    forced = None
    while i >= 0:
        cur = V[i]
        if not cands_by_line[i]:
            i -= 1
            continue
        if not cur:
            forced = None
            i -= 1
            continue
        st = forced if forced in cur else max(cur, key=lambda s: cur[s][0])
        val, same, c = cur[st]
        chosen[i] = c
        forced = st if same else None
        i -= 1

    # runs
    runs, run = [], []
    for i, c in enumerate(chosen):
        if c is None:
            if cands_by_line[i]:
                if run:
                    runs.append(run)
                run = []
            continue
        if (run and run[-1][1]["state"] == c["state"] and i - run[-1][0] <= MAX_GAP + 1
                and all(not cands_by_line[j] for j in range(run[-1][0] + 1, i))):
            run.append((i, c))
        else:
            if run:
                runs.append(run)
            run = [(i, c)]
    if run:
        runs.append(run)
    pieces = []
    for r in runs:
        n = math.ceil(len(r) / MAX_RUN)
        size = math.ceil(len(r) / n)
        for k in range(n):
            part = r[k * size:(k + 1) * size]
            if part:
                pieces.append(part)

    # English spanning several lines (configured: eBL translates some lines together)
    spans = (work.get("translation_spans") or {}).get(tag, {})
    span_of = {}
    for first, spec in spans.items():
        a, b = num_idx[first], num_idx[spec["through"]]
        for j in range(a, b + 1):
            span_of[j] = (a, b, spec)

    chap_label = f"{work['chapter_prefix'](chapter)}"
    chap_url = work["chapter_url"](chapter)
    sections = []
    seen_ids = set()
    for part in pieces:
        c0 = part[0][1]
        ms = c0["ms"]
        museum = c0["museum"]
        u = usable[museum]
        sixcol = u["sixcol"]
        face, col = face_and_col(c0["labels"], sixcol)
        first, last = lines[part[0][0]]["number"], lines[part[-1][0]]["number"]
        joiner = " to " if ("-" in first or "-" in last) else "-"
        sid = first if first == last else f"{first}{joiner}{last}"
        base = sid
        k = 2
        while sid in seen_ids:
            sid = f"{base} ({k})"
            k += 1
        seen_ids.add(sid)
        ms_first, ms_last = part[0][1]["ms_line"], part[-1][1]["ms_line"]
        ms_range = ms_first if ms_first == ms_last else f"{ms_first} to {ms_last}"
        # eBL's tablet line numbers that jump inside a run of consecutive poem lines are listed as given
        groups = []
        for _i, c in part:
            nums_ = [int(x) for x in re.findall(r"\d+", c["ms_line"])]
            if groups and nums_ and groups[-1][2] and (nums_[0] - groups[-1][2][-1]) > 2:
                groups.append([c["ms_line"], c["ms_line"], nums_])
            elif groups:
                groups[-1][1] = c["ms_line"]
                groups[-1][2] = nums_ or groups[-1][2]
            else:
                groups.append([c["ms_line"], c["ms_line"], nums_])
        ms_jump = ""
        if len(groups) > 1:
            ms_range = " and ".join(a if a == b else f"{a} to {b}" for a, b, _ in groups)
            ms_jump = (f" eBL numbers these lines on the tablet {ms_range}: its line numbers jump although the poem "
                       "lines are consecutive.")
        orig, eng = [], []
        no_tr, syms, span_notes = [], set(), []
        lost, traces, scant, partial = [], [], [], []
        in_part = {i for i, _ in part}
        for i, c in part:
            num = html.escape(lines[i]["number"], quote=False)
            rendered, s = render_atf(c["atf"])
            syms |= s
            orig.append(f"<sup>{num}</sup>{rendered}")
            if c["kept"] == 0 and re.search(r"(?<![\w])x(?![\w])", re.sub(r"\[[^\]]*\]", " ", c["atf"])):
                traces.append(i)
            elif c["kept"] == 0:
                lost.append(i)
            elif c["kept"] <= 3 and re.search(r"[\[\]]|\.\.\.|…", c["atf"]):
                scant.append(i)
            elif re.search(r"[\[\]]|(?<![\w])x(?![\w])|\.\.\.|…", c["atf"]):
                partial.append(i)
            if i in span_of:
                a, b, spec = span_of[i]
                if i != a:
                    if a in in_part:
                        continue   # the English was given with the first line of the span
                    eng.append(f"<sup>{num}</sup><span class=\"lacuna\">(translated together with line "
                               f"{html.escape(lines[a]['number'], quote=False)}, in the section that shows it)</span>")
                    continue
                parts_t = []
                for j in range(a, b + 1):
                    t, _ext = english_of(lines[j])
                    if t:
                        parts_t.append(t)
                t = " ".join(parts_t)
                for old, new in spec.get("replace", []):
                    t = t.replace(old, "\x00" + new + "\x00")
                t = t.replace("\x00", "")
                last_in = max(j for j in range(a, b + 1) if j in in_part or j == a)
                lab = lines[a]["number"] if last_in == a else f"{lines[a]['number']}-{lines[last_in]['number']}"
                eng.append(f"<sup>{html.escape(lab, quote=False)}</sup>{tr_html(t)}")
                span_notes.append(spec["note"])
                continue
            t, _ext = english_of(lines[i])
            if t is None:
                eng.append(f"<sup>{num}</sup><span class=\"lacuna\">(no English for this line in the eBL edition)</span>")
                no_tr.append(lines[i]["number"])
            else:
                eng.append(f"<sup>{num}</sup>{tr_html(t)}")
        sig = siglum_of(ms, work.get("siglum_re"))
        photo_ids = c0["photos"]
        if u.get("external"):
            ext = u["external"]
            fkey = c0.get("face_key") or face or ext["label_face"].get(col.rstrip("?"), "")
            if fkey not in ext["faces"]:
                raise SystemExit(f"{museum}: no photograph configured for face '{fkey}' (labels {c0['labels']})")
            if not face or c0.get("face_key"):
                face = fkey
            photos = [ensure_external(key, ext["faces"][fkey], dry)]
        elif face in (work.get("crops") or {}).get(museum, {}):
            photos = [ensure_crop(key, museum, face, work["crops"][museum][face], raw_dir, dry)]
        else:
            photos = [ensure_scan(key, p, raw_dir, dry) for p in photo_ids]
        where = where_text(face, col)
        holder = u.get("holder_short", "British Museum")
        ref = (f"{museum}{' (' + work['siglum_label'] + ' ' + sig + ')' if sig else ''}, {where}, "
               f"line{'s' if ms_first != ms_last else ''} {ms_range} of the tablet = {chap_label} {sid}")
        note = (f"{holder} {museum}: {where}, the tablet's own line{'s' if ms_first != ms_last else ''} "
                f"{ms_range}. eBL's corpus edition ({chap_url}) attributes {chap_label} {sid} to this manuscript "
                f"at these column and line numbers. {u['check']}")
        note += ms_jump
        for _i, c in part:
            if c.get("ms_line_note"):
                note += " " + c["ms_line_note"]
        if (tag, museum) in (work.get("extra_notes") or {}):
            note += " " + work["extra_notes"][(tag, museum)]
        if ms_type(ms) in EXCERPT_TYPES:
            note += (f" eBL classes {museum} as {EXCERPT_TYPES[ms_type(ms)]}, not a library copy of the whole work. "
                     "It carries these lines as text (eBL's transliteration has no commentary or quotation markup), and "
                     "it is used because no photographed library copy preserves these lines as well.")
        if c0.get("catch"):
            of = (f", a copy of {c0['catch']}" if c0["catch"] != "?" else "")
            note += (f" {museum}{of}, carries {'these lines' if len(part) > 1 else 'this line'} as its catch-line: the "
                     "opening of the next tablet of the series, copied at the end of the previous one (eBL lists catch-lines "
                     "among its quotations; unlike commentaries and quotations in other texts, a catch-line is the line itself "
                     "on a copy of the work).")
        all_split = u["photos"]
        if len(all_split) > 1:
            if c0["documented"]:
                on_piece = [p for p in photo_ids if p != museum]
                cfg_notes = [pmap[museum][p]["note"] for p in all_split[1:]
                             if pmap.get(museum, {}).get(p, {}).get("note")]
                if cfg_notes:
                    # piece placed by a visual check recorded in the importer
                    note += " " + " ".join(cfg_notes)
                    if on_piece:
                        note += (" " + " and ".join(on_piece) + (" is" if len(on_piece) == 1 else " are")
                                 + " therefore linked for these lines.")
                    else:
                        note += f" Only the photograph of {museum} is linked for these lines."
                elif on_piece and museum in photo_ids:
                    note += (f" {museum} is joined to " + ", ".join(x for x in all_split if x != museum) +
                             ", which the British Museum photographed separately. eBL's own transliteration of "
                             + " and ".join(on_piece) + " and the notes of its edition place parts of these lines on "
                             + " and ".join(on_piece) + ", so " + ("its photograph is" if len(on_piece) == 1 else "their photographs are")
                             + f" linked as well as that of {museum}.")
                elif on_piece:
                    note += (f" These lines are on the joined piece {' and '.join(on_piece)}, photographed separately from "
                             f"{museum}: eBL's own transliteration of {' and '.join(on_piece)} carries every preserved "
                             "sign of them, so only that photograph is linked.")
                else:
                    note += (f" {museum} is joined to " + ", ".join(x for x in all_split if x != museum) +
                             ", photographed separately; eBL's own transliteration of the joined piece(s) does not "
                             "include these lines, so only the photograph of " + museum + " is linked.")
            else:
                note += (" eBL treats " + " + ".join(all_split) + " as one manuscript and holds a separate "
                         "photograph of each of these pieces; it does not say which piece carries which line, so the "
                         "photographs of " + " + ".join(photo_ids) + " are linked, and the lines are on one or more of them.")
        # what the English renders that this tablet does not show (spec rule 7)
        if lost or traces or scant or partial:
            bits = []
            if lost:
                bits.append(f"line{'s' if len(lost) > 1 else ''} {idx_ranges(lost, lines)} "
                            f"{'are' if len(lost) > 1 else 'is'} entirely broken")
            if traces:
                bits.append(f"of line{'s' if len(traces) > 1 else ''} {idx_ranges(traces, lines)} only illegible "
                            "traces (x) survive")
            if scant:
                bits.append(f"of line{'s' if len(scant) > 1 else ''} {idx_ranges(scant, lines)} only one to three "
                            "signs survive")
            if partial:
                bits.append(f"line{'s' if len(partial) > 1 else ''} {idx_ranges(partial, lines)} "
                            f"{'are' if len(partial) > 1 else 'is'} partly broken (square brackets and x in the Akkadian)")
            note += (" On this tablet " + ", ".join(bits[:-1]) + (" and " if len(bits) > 1 else "") + bits[-1]
                     + ". The English of " + ("these lines" if len(lost) + len(traces) + len(scant) + len(partial) > 1 else "this line")
                     + " translates eBL's composite text, so it includes words that are not preserved on this tablet "
                       "but are restored from other manuscripts or by the editors. Square brackets in the English mark "
                       "eBL's restorations in its composite text; words that survive on other tablets carry no brackets "
                       "even where this tablet is broken.")
            others = [i for i in in_part if i not in lost and i not in traces and i not in scant and i not in partial]
            if others:
                note += f" Line{'s' if len(others) > 1 else ''} {idx_ranges(others, lines)} {'are' if len(others) > 1 else 'is'} complete on this tablet."
        else:
            note += (" Every line of this section is complete on this tablet; the English translates eBL's composite "
                     "text, which may follow other manuscripts where they differ in wording.")
        for sn in span_notes:
            note += " " + sn
        if no_tr:
            note += f" eBL gives no English for line(s) {', '.join(no_tr)}."
        skipped = [lines[j]["number"] for j in range(part[0][0], part[-1][0] + 1) if j not in in_part]
        if skipped:
            note += (f" eBL line(s) {', '.join(skipped)} fall within this run but are not on this tablet "
                     "(they are listed among the lines not shown).")
        sections.append({
            "section": sid,
            "original_ref": ref,
            "original_text": "<br>\n".join(orig),
            "text": "<br>\n".join(eng),
            "scan_pages": photos,
            "scan_note": note,
            "_museum": museum,
            "_n": len(part),
            "_syms": syms,
            "_excerpt": ms_type(ms) in EXCERPT_TYPES,
        })

    # coverage
    covered = {i for part in pieces for i, _ in part}
    gaps = []
    for i, l in enumerate(lines):
        if i in covered:
            continue
        reasons = []
        for v in l["variants"]:
            for m in v["manuscripts"]:
                if m.get("atf", "").strip() and not m["atf"].lstrip().startswith("$"):
                    ms = msinfo.get(m["manuscriptId"])
                    if ms:
                        ms = dict(ms, _catch=catchline_of(ms, chapter, all_chapters))
                        r = gap_reason(work, src, ms, clean_atf(m["atf"]), usable)
                        if r not in reasons:
                            reasons.append(r)
        gaps.append((l["number"], tuple(reasons), i))
    cov = {"lines": len(lines), "covered": len(covered), "gaps": gaps,
           "with_ms": sum(1 for l in lines if any(m.get("atf", "").strip() and not m["atf"].lstrip().startswith("$")
                                                   for v in l["variants"] for m in v["manuscripts"]))}
    return sections, cov


def gap_ranges(gaps):
    """[(num, reasons, idx)] -> list of ('a-b', reason) merging neighbours with the same reason."""
    out = []
    for num, reasons, idx in gaps:
        if not reasons:
            reason = "no manuscript preserves it"
        else:
            parts = []
            for cat, head in GAP_CATS:
                labs = [lab for c, lab in reasons if c == cat]
                if labs:
                    parts.append(f"{head}: {', '.join(labs)}")
            reason = "; ".join(parts)
        if out and out[-1][2] == reason and out[-1][3] == idx - 1:
            out[-1][1] = num
            out[-1][3] = idx
            out[-1][4] += 1
        else:
            out.append([num, num, reason, idx, 1])

    def lab(a, b, n):
        if a == b:
            return a
        if "-" in a or "-" in b:   # eBL labels that are themselves ranges ("109-110")
            return f"{a}, {b}" if n == 2 else f"{a} to {b}"
        return f"{a}-{b}"
    return [(lab(a, b, n), r) for a, b, r, _, n in out]


# ---------------------------------------------------------------------------
# Work driver
# ---------------------------------------------------------------------------
def load_usable(work, src):
    """museum -> {photos, check, sixcol, holder_short, licence}.  Only manuscripts with a PHOTO_CHECKS
    entry (visual check) and an eBL photograph of a holder listed in HOLDERS are usable."""
    out = {}
    for museum, check in work["photo_checks"].items():
        if museum in work["excluded"]:
            continue
        f = ebl_fragment(src, museum)
        if f.get("museum") not in HOLDERS or not f.get("hasPhoto"):
            continue
        photos = [museum] + list(work.get("split_photos", {}).get(museum, []))
        hs, lic = HOLDERS[f["museum"]]
        out[museum] = {"photos": photos, "check": check, "frag": f, "holder_short": hs, "licence": lic,
                       "restricted": f["museum"] != "THE_BRITISH_MUSEUM"}
    for museum, ext in (work.get("external_photos") or {}).items():
        f = ebl_fragment(src, museum)
        out[museum] = {"photos": [museum], "check": ext["check"], "frag": f, "external": ext,
                       "holder_short": ext["holder_short"], "licence": ext["licence"]}
    return out


def auto_candidates(work, src, chapters):
    """All manuscripts with an eBL photograph of a holder listed in HOLDERS (not excluded), with the
    pieces of their physical join group that have their own photograph (split joins)."""
    out = {}
    listed = {m["museumNumber"] for ch in chapters for m in ch["manuscripts"] if m["museumNumber"]}
    for ch in chapters:
        for m in ch["manuscripts"]:
            museum = m["museumNumber"]
            if not museum or museum in out or museum in work["excluded"]:
                continue
            f = ebl_fragment(src, museum)
            if f.get("museum") not in HOLDERS or not f.get("hasPhoto"):
                continue
            if "photo shows" in ((f.get("notes") or {}).get("text") or ""):
                continue
            split, missing = [], []
            for grp in f.get("joins") or []:
                names = [mus_str(j["museumNumber"]) for j in grp]
                own_group = museum in names
                if not own_group and any(n in listed for n in names):
                    continue  # an indirect join that eBL lists as a manuscript of its own
                photographed = []
                for n in names:
                    if n == museum:
                        continue
                    jf = ebl_fragment(src, n)
                    if jf.get("hasPhoto") and jf.get("museum") in HOLDERS:
                        photographed.append(n)
                split += photographed
                if not own_group and not photographed:
                    missing += names   # an indirectly joined group with no open photograph at all
            if missing:
                print(f"      (skipping {museum}: indirectly joined piece(s) {', '.join(missing)} have no usable photograph)")
                continue
            hs, lic = HOLDERS[f["museum"]]
            out[museum] = {"photos": [museum] + split, "check": "(unchecked)", "frag": f,
                           "holder_short": hs, "licence": lic, "restricted": f["museum"] != "THE_BRITISH_MUSEUM"}
    return out


def build_work(work, argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", nargs="*", help="subset, e.g. SB:XI")
    ap.add_argument("--raw-dir", default=os.environ.get("EBL_RAW_DIR", str(Path(tempfile.gettempdir()) / "theosis-ebl-raw")))
    ap.add_argument("--report", action="store_true", help="coverage report only; write nothing")
    ap.add_argument("--candidates", action="store_true",
                    help="treat every eBL photograph of a listed holder as usable (unchecked) and list the tablets the "
                         "selection would use, for visual checking; writes nothing")
    args = ap.parse_args(argv)
    key = work["key"]
    src = ROOT / "data" / "sources" / key
    g, c, i = work["ebl_text"]
    chapters = []
    for ent in work["entries"]:
        st, name = ent["chapter"]
        ch = ebl_chapter(src, g, c, i, st, name)
        ch["_stage_abbr"] = st
        chapters.append(ch)
    work["_src"] = src
    work["_pmap"] = piece_line_map(work, src, chapters)
    usable = load_usable(work, src)
    if args.candidates:
        cand = auto_candidates(work, src, chapters)
        for k, v in cand.items():
            usable.setdefault(k, v)
        args.report = True
    for museum, u in usable.items():
        u["sixcol"] = six_column(chapters, museum) or museum in work.get("six_column_extra", set())

    rows, report = [], []
    wanted = set(args.chapters or [])
    for order, (ent, ch) in enumerate(zip(work["entries"], chapters), start=1):
        tag = f"{ent['chapter'][0]}:{ent['chapter'][1]}"
        if wanted and tag not in wanted:
            continue
        secs, cov = chapter_sections(work, ch, chapters, usable, args.raw_dir, dry=args.report)
        n_sec_lines = sum(s["_n"] for s in secs)
        used = []
        for s in secs:
            if s["_museum"] not in used:
                used.append(s["_museum"])
        report.append((tag, cov["lines"], cov["with_ms"], cov["covered"], len(secs), len(used)))
        print(f"{tag:12} eBL lines {cov['lines']:4}  with any ms {cov['with_ms']:4}  published {cov['covered']:4}  "
              f"sections {len(secs):3}  tablets {len(used):2}")
        if args.report:
            for r, why in gap_ranges(cov["gaps"]):
                print(f"      gap {r}: {why}")
            if args.candidates:
                for m in used:
                    n = sum(s["_n"] for s in secs if s["_museum"] == m)
                    flag = "" if m in work["photo_checks"] else "  UNCHECKED"
                    groups = [[mus_str(j["museumNumber"]) for j in g] for g in (usable[m]["frag"].get("joins") or [])]
                    jtxt = " (+) ".join("+".join(g) for g in groups) if groups else "-"
                    print(f"      uses {m:16} {n:4} lines  photos={usable[m]['photos']}{flag}  joins: {jtxt}")
            continue
        entry, row = work["make_entry"](work, ent, ch, secs, cov, used, usable, order)
        for s in entry["translation"]:
            for k_ in ("_museum", "_n", "_syms", "_excerpt"):
                s.pop(k_, None)
        (PUB / f"{entry['id']}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
        rows.append(row)
    if args.report or wanted:
        return report
    coll = {"collection": work["collection"], "texts": rows}
    if work.get("authors"):
        coll["authors"] = work["authors"]
    if work.get("redirects"):
        coll["redirects"] = work["redirects"]
    COLL.mkdir(parents=True, exist_ok=True)
    (COLL / f"{key}.json").write_text(json.dumps(coll, ensure_ascii=False, indent=2), encoding="utf-8")
    # remove stale entry files / scans of this collection
    keep_ids = {r["id"] for r in rows}
    for f in PUB.glob(f"{work['collection']['prefix']}*.json"):
        if f.stem not in keep_ids:
            print(f"  removing stale entry {f.name}")
            f.unlink()
    used_scans = set()
    for r in rows:
        for p in r["scans"]["pages"]:
            used_scans.add(p["file"])
    for f in (SCANS / key).glob("*.jpg"):
        if f"{key}/{f.name}" not in used_scans:
            print(f"  removing unused scan {f.name}")
            f.unlink()
    print(f"wrote {len(rows)} entries, data/collections/{key}.json")
    return report


def caption_for(p, key, used, usable):
    for m in used:
        ext = usable[m].get("external")
        if ext:
            for face, spec in ext["faces"].items():
                if p == f"{key}/{spec['file']}":
                    return f"{ext['holder_short']} {m}, {face}"
        for ph in usable[m]["photos"]:
            stem = scan_name(key, ph)[:-4]
            name = p.split("/", 1)[1][:-4]
            if name == stem or name.startswith(stem + "-"):
                return f"{usable[m].get('holder_short', 'British Museum')} {name[len(key) + 1:]}"
    return "British Museum " + p.split("/", 1)[1][len(key) + 1:-4]


def standard_entry(work, ent, ch, secs, cov, used, usable, order):
    """Entry JSON + catalog row for one chapter (shared by all eBL works)."""
    key = work["key"]
    tid = f"{work['collection']['prefix']}{ent['slug']}"
    photos = []
    for s in secs:
        for p in s["scan_pages"]:
            if p not in photos:
                photos.append(p)
    gaps = gap_ranges(cov["gaps"])
    chap_url = work["chapter_url"](ch)
    used_desc = []
    holders = []
    for m in used:
        f = usable[m]["frag"]
        prov = (f.get("archaeology") or {}).get("site") or ""
        used_desc.append(m + (f" ({prov})" if prov else ""))
        h = usable[m].get("holder_short", "British Museum")
        if h not in holders:
            holders.append(h)
    holder_txt = " and ".join(holders)
    ext_used = [usable[m]["external"] for m in used if usable[m].get("external")]
    pct = round(100 * cov["covered"] / cov["lines"]) if cov["lines"] else 0
    gap_html = ""
    if gaps:
        items = "; ".join(f"{r} ({html.escape(why, quote=False)})" for r, why in gaps)
        gap_html = (f"<p><strong>Lines not shown.</strong> {cov['lines'] - cov['covered']} of the {cov['lines']} lines of "
                    f"the eBL edition are not shown, because no photographed copy of the work used here carries them: "
                    f"{items}. A line is shown only on a photographed tablet that carries it as text. Commentaries "
                    "and other texts that quote a line (letters, rituals, god lists) are not used as witnesses, because "
                    "they carry it with explanations or inside another text; tablets without a photograph in eBL are "
                    "not used, because the line could not be shown on its tablet.</p>")
    excerpt_used = sorted({s["_museum"] for s in secs if s.get("_excerpt")})
    syms = set()
    for s in secs:
        syms |= s.get("_syms", set())
    excerpt_txt = (" School and excerpt tablets are used only for lines that no photographed library copy preserves "
                   "as well, and only where they carry the line as text; their sections say so"
                   + (f" ({', '.join(excerpt_used)})" if excerpt_used else "") + ".")
    intro = (
        ent["intro"]
        + f"<p><strong>How this page is built.</strong> Each section is a run of consecutive lines as written on one "
        f"photographed clay tablet. For every line the eBL edition ({html.escape(chap_url, quote=False)}) lists the manuscripts "
        "that carry it, with each tablet's own column and line numbers; the tablet chosen for each run is the "
        "photographed copy of the work with the most signs preserved there. Commentaries and texts that only quote a "
        "line are never chosen." + html.escape(excerpt_txt, quote=False) + " The original text is eBL's transliteration of "
        "that tablet's signs (not a modern composite text): square brackets mark broken signs, x an illegible sign, "
        "# a damaged sign, ? an uncertain reading, and words in {braces} are determinatives; the notes give a key to "
        "every sign used on this page, and eBL's layout codes are written out in words (for example '(line break)' or "
        "'(blank space)'). Superscript numbers are the line numbers of the eBL edition, used in both the Akkadian and the "
        f"English. {html.escape(work['translator_line'], quote=False)} Where the tablet is broken, the English still "
        "translates the whole line of eBL's composite text; each section's note names the lines that are broken on its "
        "tablet.</p><p><strong>Finding a line on the photograph.</strong> Each section names the tablet, the face and column, "
        "and the tablet's own line numbers (a prime, as in 5', counts from the first preserved line of a broken "
        "column). On a tablet with six columns the obverse carries columns i-iii from left to right; the reverse, "
        "turned over from bottom to top, carries columns iv-vi from right to left. The photographs often show the "
        "obverse above the reverse with the edges around them; a fragment preserves only part of this layout.</p>"
        f"<p>This page shows {cov['covered']} of the {cov['lines']} lines of the eBL edition ({pct}%), from "
        f"{len(used)} tablet{'s' if len(used) != 1 else ''} in the {html.escape(holder_txt, quote=False)}: {', '.join(html.escape(x, quote=False) for x in used_desc)}.</p>"
        + gap_html
    )
    notes = list(work.get("translator_notes", [])) + [atf_key_line(syms)]
    licences = []
    for m in used:
        lic = usable[m].get("licence") or BM_LICENCE
        if lic not in licences:
            licences.append(lic)
    ebl_used = [m for m in used if not usable[m].get("external")]
    entry = {
        "id": tid,
        "slug": tid,
        "title": ent["title"],
        "language": "Akkadian (transliteration) / English",
        "source": (f"{holder_txt} tablet photographs + eBL manuscript transliterations "
                   f"({work['ebl_name']}, {ent['chapter'][0]} {ent['chapter'][1]}) + English of the eBL edition "
                   f"({work['translator_short']})"),
        "description": ent["description"].format(covered=cov["covered"], lines=cov["lines"], tablets=len(used)),
        "introduction": intro,
        "translator_notes": notes,
        "translation": secs,
        "verification": {
            "scan_source": "; ".join(
                ([("electronic Babylonian Library fragment photo API, https://www.ebl.lmu.de/api/fragments/<museum number>/photo "
                   "(photographs of the " + " and ".join(dict.fromkeys(usable[m]["holder_short"] for m in ebl_used))
                   + "); tablets used: " + ", ".join(
                       f"{m} ({EBL_WEB}/library/{urllib.parse.quote(m)})" for m in ebl_used))] if ebl_used else [])
                + [e["source"] for e in ext_used]),
            "scan_license": "; ".join(licences),
            "scan_manuscript": "; ".join(
                (usable[m]["external"]["holder"] if usable[m].get("external") else f"{usable[m]['holder_short']} {m}")
                + (f" ({usable[m]['frag'].get('description', '')[:120].strip()})"
                   if usable[m]['frag'].get('description') else "") for m in used),
            "scan_mapping": ("eBL corpus edition: every line of the poem lists the manuscripts that carry it with the "
                             "manuscript's own column and line number; each section uses one manuscript's lines only. "
                             "Each tablet photograph was also checked by eye (object identity, inscribed faces, visible "
                             "line count); see each section's scan_note."),
            "scan_mapping_urls": [chap_url] + [f"{EBL_WEB}/library/{urllib.parse.quote(m)}" for m in used],
            "scan_local_paths": photos,
            "original_text_source": f"{work['ebl_name']}, {chap_url} (API {EBL_API}/texts/{'/'.join(map(str, work['ebl_text']))}/chapters/{ent['chapter'][0]}/{ent['chapter'][1]}); manuscript-level ATF only",
            "original_text_license": EBL_LICENCE,
            "translation_source": work["translation_source"] + f"; {chap_url}",
            "translation_license": EBL_LICENCE,
            "translator": work["translator_short"],
            "line_coverage": {"ebl_lines": cov["lines"], "lines_with_any_manuscript": cov["with_ms"],
                              "lines_published": cov["covered"]},
            "lines_not_published": [f"{r}: {why}" for r, why in gaps],
            "verified_date": TODAY,
        },
    }
    row = {
        "id": tid, "slug": tid, "order": order, "title": ent["title"],
        "author_id": ent.get("author_id", work["author_id"]), "language": "Akkadian",
        "era": "Ancient Near East", "tradition": "mesopotamian", "category": work.get("category", "literature"),
        "date_approx": ent.get("date_approx", work["date_approx"]), "century": ent.get("century", work["century"]),
        "source": entry["source"], "description": entry["description"],
        "themes": work["themes"] + ent.get("themes", []) + ["verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": p, "caption": caption_for(p, key, used, usable)} for p in photos]},
    }
    return entry, row


def simple_work(key, ebl_text, ebl_name, label, entries, translator, translator_short, translation_source,
                author_id, date_approx, century, date_sort, themes, search_terms, shelf_description,
                author_name, checks, excluded=None, split=None, external=None, siglum_label="ms.",
                siglum_re=None, authors=None, category="literature"):
    """Configuration for an eBL work published one entry per chapter (used by the other importers)."""
    g, c, i = ebl_text
    return {
        "key": key, "ebl_text": ebl_text, "ebl_name": ebl_name,
        "chapter_prefix": lambda ch: f"{ch['_stage_abbr']} {ch['name']}".replace(" -", ""),
        "chapter_url": lambda ch: f"{EBL_WEB}/corpus/{g}/{c}/{i}/{ch['_stage_abbr']}/{urllib.parse.quote(ch['name'])}",
        "siglum_label": siglum_label, "siglum_re": siglum_re,
        "photo_checks": checks, "excluded": excluded or {}, "split_photos": split or {},
        "external_photos": external or {},
        "entries": entries, "make_entry": standard_entry, "author_id": author_id,
        "date_approx": date_approx, "century": century, "themes": themes, "category": category,
        "translator_short": translator_short,
        "translator_line": (f"The English is {translator}'s translation in the eBL edition (CC BY-NC-SA 4.0), one line "
                            "of English per line of the text; italics mark uncertain renderings, as in the source."),
        "translation_source": translation_source,
        "translator_notes": [
            "Akkadian: eBL transliteration of the signs on the photographed tablet (manuscript-level ATF), not a composite text.",
            f"English: {translator}'s translation in the eBL edition; it renders eBL's composite text, including restorations from other tablets.",
            "Line numbers: eBL edition. Each section also gives the tablet's own column and line numbers.",
        ],
        "collection": {
            "key": key, "prefix": f"verified-{key}-", "label": label, "group": "Mesopotamia",
            "date_sort": date_sort, "author_name": author_name,
            "source_url": f"{EBL_WEB}/corpus/{g}/{c}/{i}",
            "critical_edition": f"electronic Babylonian Library, {ebl_name.split(', ', 1)[-1]}, manuscript transliterations",
            "translator_name": translator_short,
            "original_lang_label": "Akkadian · eBL transliteration of each tablet",
            "original_lang_code": "akk", "edition_label": "",
            "search_terms": search_terms, "description": shelf_description,
        },
        **({"authors": authors} if authors else {}),
    }


# ===========================================================================
# GILGAMESH configuration
# ===========================================================================
# Visual checks of every eBL photograph used (done on the downloaded photographs,
# contact sheets and full views, 2026-11-12).  "Lines" = lines eBL attributes to
# the manuscript in the chapters used.
GILG_CHECKS = {
    'IM.67564': "Photograph checked (eBL photograph of the Iraq Museum): two views of a fragment from Kalhu (Nimrud), each face with two columns divided by a vertical ruling and about 30 to 40 lines per column. The ink on the right part of the face shown first reads 'N.D. 4381', the Nimrud excavation number (not the Iraq Museum number). Consistent with eBL's columns i (tablet lines 1'b to 40') and ii (1' to 36') of Tablet X on the face shown first, and column vi of Tablet XI on the other.",
    "K.2756.C": "Photograph checked: one face shown, about 16 lines in a single column, consistent with eBL's 16 lines in column i.",
    "K.8584": "Photograph checked: two views; the inscribed face (lower view) shows two columns, consistent with eBL's columns i and ii (12 lines each); the other view is the uninscribed back with the ink number K.8584.",
    "K.15145": "Photograph checked: one face, ink number K.15145, about 6 lines, consistent with eBL's 6 lines of column i.",
    "K.4465": "Photograph checked: obverse, reverse and edges of the joined tablet (K.4465 + K.9245 + K.22153 + Sm.2133; Sm.2133 ink number on the lower edge); two columns preserved on each face, consistent with eBL's columns ii-iii and iv-v.",
    "BM.37163": "Photograph checked: obverse, reverse and edges, ink number 37163 (80-6-17,913) on the edge; a few lines on each face, consistent with eBL's columns iii (6 lines) and iv (7 lines).",
    "K.7017": "Photograph checked: both faces and edges, ink number K.7017; a few lines on each face, consistent with eBL's columns iii and iv (8 and 9 lines).",
    "K.2756.D": "Photograph checked: the inscribed face shows two joined pieces (ink number K.20778 on the lower piece) with a column divider, consistent with eBL's columns iv and v on the reverse; the other view is the eroded obverse.",
    "K.12000.Q": "Photograph checked: one small face with two or three lines of large signs and the ink number K.12000.",
    "Rm.785": "Photograph checked: obverse, reverse and edges of the joined fragments (ink numbers of Rm.956 and BM.34357 visible on the edges, modern plaster fill); text on the obverse in two columns, consistent with eBL's columns i and ii.",
    "BM.38538": "Photograph checked: obverse, reverse and edges, ink number 38538 on the edge; one face carries about 15 lines running to the left edge, consistent with eBL's column vi (15 lines); the other face is worn.",
    "Rm.289": "Photograph checked: obverse, reverse and edges of two joined pieces; text on both faces, consistent with eBL's columns i-iii and iv-v.",
    "K.8574": "Photograph checked: both faces and edges, ink number K.8574; a few lines on each face, consistent with eBL's columns ii and v.",
    "BM.38833": "Photograph checked: two views, the inscribed face with about 20 lines of small script and the back with the ink number 38833, consistent with eBL's 23 lines of column iv.",
    "BM.40849": "Photograph checked: two views, the inscribed face with about 8 lines, consistent with eBL's column vi.",
    "BM.98990": "Photograph checked: obverse, reverse and edges (ink number 98990, registration 1904-10-9,13); a full column on the obverse and a few lines on the reverse, consistent with eBL's columns i (27 lines) and vi (11 lines).",
    "K.8558": "Photograph checked: one face with two columns separated by a ruling, consistent with eBL's columns i and ii.",
    "K.4474": "Photograph checked: one face, two columns with a divider, consistent with eBL's columns i and ii.",
    "K.3423": "Photograph checked: obverse, reverse and edges of the join K.3423 + Sm.2097 + Rm.579 (ink numbers on the edges); two columns on each face, consistent with eBL's columns ii-iii and iv-v.",
    "K.9885": "Photograph checked: both faces of the joined tablet (two pieces, ink number K.9885); text on both faces, consistent with eBL's columns ii-iii and iv-v.",
    "BM.35079": "Photograph checked: obverse, reverse and edges of the join (ink numbers 35079 and 35103 visible); inscribed obverse, consistent with eBL's columns ii and iii.",
    "BM.32960": "Photograph checked: obverse, reverse and edges, ink number 32960; about 10 lines on one face, consistent with eBL's 10 lines of column iii.",
    "BM.36093": "Photograph checked: obverse, reverse and edges, ink number 36093; about 10 lines on one face, consistent with eBL's 10 lines of column iii.",
    "K.8586": "Photograph checked: obverse, reverse and edges, ink number K.8586 on the edge; about 20 lines on one face, consistent with eBL's 20 lines of column i.",
    "Rm.853": "Photograph checked: obverse, reverse and edges, ink number Rm.853; a few lines on each face, consistent with eBL's attribution.",
    "K.10777": "Photograph checked: both faces and edges, ink number K.10777; a few lines on each face, consistent with eBL's columns iii (13 lines) and iv (6 lines).",
    "Sm.1040": "Photograph checked: obverse, reverse and edges, ink number S.1040; one column of about 23 lines on the inscribed face, consistent with eBL's column iii.",
    "BM.45883": "Photograph checked: obverse, reverse and edges, ink number 45883 (81-7-6,314); a few lines on each face, consistent with eBL's columns iii and iv.",
    "1879,0708.342": "Photograph checked: one face with the ink number 79-7-8,342 and about 7 lines, consistent with eBL's column v.",
    "K.7224": "Photograph checked: one face with the ink number K.7224 and about 10 lines, consistent with eBL's column vi.",
    "K.3252": "Photograph checked: obverse, reverse and edges of the join K.3252 + K.8561 (both ink numbers on the edge); text on both faces, consistent with eBL's columns i-ii and v-vi.",
    "K.8591": "Photograph checked: obverse, reverse and edges; text on the obverse in two columns, consistent with eBL's columns i and ii.",
    "K.13525": "Photograph checked: one face with about 9 lines; eBL gives no column for this fragment.",
    "Sm.866": "Photograph checked: obverse, reverse and edges, ink number S.866; about 7 lines on one face, consistent with eBL's column iii.",
    "Sm.209": "Photograph checked: obverse, reverse and edges, ink number S.209; about 8 lines on one face; eBL gives no column for this fragment.",
    "K.231": "Photograph checked: obverse and reverse of a large tablet, three columns on each face, consistent with eBL's columns i-vi.",
    "K.3990": "Photograph checked: obverse, reverse and edges of the join K.3990 + K.4579 + DT.2 + Rm.578 + Rm-II.197 (modern plaster fill, ink numbers on the pieces); text on both faces, consistent with eBL's columns i and iv-vi.",
    "K.4579.A": "Photograph checked: obverse, reverse and edges of the join K.4579.A + K.8018 (both ink numbers on the edge); text on both faces, consistent with eBL's columns i-ii and v-vi.",
    "Sm.2112": "Photograph checked: obverse, reverse and edges, ink number S.2112; text on both faces, consistent with eBL's columns ii-iii and iv.",
    "K.15193": "Photograph checked: obverse and reverse of the joined pieces K.15193, Sm.2194 and Sm.401 (ink numbers visible); text in two columns on each face.",
    "K.5335": "Photograph checked: obverse, reverse and edges; a few lines on each face, consistent with eBL's columns iii and iv.",
    "K.14945": "Photograph checked: one face of a fragment from the lower edge with about 8 lines (British Museum description: 8 lines), consistent with eBL's 9 lines of column iv.",
    "K.3588": "Photograph checked: obverse, reverse and edges, ink number K.3588 on both side edges; one column on each face, consistent with eBL's columns i and vi.",
    "BM.43021": "Photograph checked: obverse, reverse and edges of a small fragment (ink number 81-7-1,785); a few lines on each face, consistent with eBL's columns i and vi (4 lines each).",
    'Sm.2132': "Photograph checked: obverse, reverse and edges, ink number S.2132 on the left edge. The face shown above carries about 13 lines whose right ends are cut off by a diagonal break, consistent with eBL's column iv? (13 lines, VII 249-261); the face shown below keeps only the first two to four signs of about 11 lines along its left edge, consistent with eBL's column i (11 lines, VII 56-68). The photograph therefore shows the face with column iv? above the face with column i.",
    "Rm-II.399": "Photograph checked: obverse, reverse and edges; about 13 lines on one face, consistent with eBL's column ii.",
    "BM.46002": "Photograph checked: two views, ink number 46002 (81-7-6,446) on the back; the inscribed face shows two columns, consistent with eBL's columns ii and iii.",
    "K.8590": "Photograph checked: obverse, reverse and edges, ink number K.8590; one column on each face, consistent with eBL's columns iii and iv.",
    "K.2589": "Photograph checked: obverse, reverse and edges, ink number K.2589; one column on each face, consistent with eBL's columns iii and iv.",
    "K.19325": "Photograph checked: one face with parts of about 6 lines; eBL gives no column for this fragment.",
    "BM.34423": "Photograph checked: obverse, reverse and edges, ink number 34423 (Sp.543).",
    "K.11659": "Photograph checked: one face with about 15 lines, consistent with eBL's column iii.",
    "K.3389": "Photograph checked: obverse, reverse and edges, ink number K.3389; one column on each face, consistent with eBL's columns iii and iv.",
    "1879,0708.320": "Photograph checked: obverse, reverse and edges, ink number 79-7-8,320; the inscribed face shows two columns, consistent with eBL's columns iv and v.",
    "BM.35245": "Photograph checked: two views, the inscribed face with about 9 lines, consistent with eBL's column iv.",
    "K.9196": "Photograph checked: one face with ink number K.9196 and two columns, consistent with eBL's columns iv and v.",
    "1879,0708.335": "Photograph checked: obverse, reverse and edges, ink number 79-7-8,335; about 14 lines on one face, consistent with eBL's column iv.",
    "K.8587": "Photograph checked: obverse, reverse and edges, ink number K.8587; about 10 lines on one face, consistent with eBL's column i.",
    "K.6899": "Photograph checked: obverse, reverse and edges of the join K.6899 + K.8564 + K.9716 + Rm-II.262 (ink numbers on the pieces); text on both faces, consistent with eBL's columns i-iii and iv-v.",
    "K.8565": "Photograph checked: one face showing the join K.8565 + K.9997 with two columns, consistent with eBL's columns i and ii.",
    "BM.37189": "Photograph checked: obverse, reverse and edges, ink number 37189; about 8 lines on one face, consistent with eBL's column i.",
    "K.19549": "Photograph checked: obverse, reverse and edges, ink number K.19549; a few lines on each face.",
    "BM.36999": "Photograph checked: obverse, reverse and edges, ink number 36999; about 11 lines on one face, consistent with eBL's column ii.",
    "BM.36909": "Photograph checked: obverse, reverse and edges of the join BM.36909 + BM.37023 + F.235.A; text on both faces, consistent with eBL's columns ii-iii and iv-v.",
    "K.8281": "Photograph checked: obverse, reverse and edges, ink number K.8281; one column on each face, consistent with eBL's columns iii and iv.",
    "K.19751": "Photograph checked: one face with about 8 lines of large signs, consistent with eBL's column iii.",
    "K.2360": "Photograph checked: obverse, reverse and edges of the join K.2360 + K.3060 (both ink numbers on the edge); three columns on each face, consistent with eBL's columns i-vi.",
    "1880,0719.305": "Photograph checked: obverse, reverse and edges, ink number 80-7-19,305; about 12 lines on one face, consistent with eBL's column i.",
    "K.18183": "Photograph checked: one face with about 5 lines, consistent with eBL's column iv.",
    "K.8589": "Photograph checked: obverse, reverse and edges of the join K.8589 + Sm.1681 (ink numbers on the edge); text on both faces, consistent with eBL's columns i and v-vi.",
    "BM.34160": "Photograph checked: obverse, reverse and edges of the large joined tablet (several pieces with plaster joins, ink numbers on the edges); two columns on each face, consistent with eBL's columns i-ii and v-vi.",
    "K.3382": "Photograph checked: obverse, reverse and edges of the join K.3382 + Rm.621 (two large pieces, ink number K.3382 on the edge); text on both faces, consistent with eBL's columns i-iii and iv-v.",
    "K.2252": "Photograph checked: obverse, reverse and edges of the join K.2252 + K.2602 + K.3321 + K.4486 + Sm.1881 (ink numbers K.3321 and S.1881 on the lower edge, plaster fill); three columns on each face, consistent with eBL's columns i-vi.",
    "Rm.616": "Photograph checked: obverse, reverse and edges, ink number Rm.616; one column on the obverse, consistent with eBL's column i.",
    "K.8517": "Photograph checked: obverse, reverse and edges of the join K.8517 + K.8518 + K.8569 + K.8593 + K.8595 (many pieces, plaster fill); text on both faces, consistent with eBL's columns i-ii and v-vi.",
    "BM.35380": "Photograph checked: obverse, reverse and edges of BM.35380 alone (ink number 35380); two columns on each face.",
    "Sm.2131": "Photograph checked: obverse, reverse and edges of the join Sm.2131 + Sm.2196 + Rm-II.383 + Rm-II.390 + 1882,0522.316 (several pieces with plaster); text on both faces, consistent with eBL's columns i-iii.",
    "K.3375": "Photograph checked: obverse, reverse and edges, ink number K.3375 and 'W.A.I. IV 50 & 51' on the edge; two columns on each face, consistent with eBL's columns ii-iii (obverse) and iv-v (reverse).",
    "K.7752": "Photograph checked: obverse, reverse and edges of the join K.7752 + 1881,0204.245 + .296 + .460 (ink numbers on the pieces); text on both faces, consistent with eBL's columns ii-iii and iv-vi.",
    "K.8594": "Photograph checked: one face showing two joined pieces (K.8594 + K.21502) with about 14 lines, consistent with eBL's column iii.",
    "K.17343": "Photograph checked: one face of K.17343 alone, ink number on the right edge; eBL notes this piece as Gilgamesh XI 163-169.",
    "K.3475": "Photograph checked: obverse, reverse and edges of the join K.3475 + DT.13 + 1881,0204.327 (ink numbers D.T.13 and 81-2-4,327 visible); text on both faces, consistent with eBL's columns i and vi.",
    "Rm.964": "Photograph checked: obverse, reverse and edges, ink number Rm.964; about 9 lines on one face, consistent with eBL's column i.",
    "BM.30559": "Photograph checked: obverse, reverse and edges of the join BM.30559 + BM.32418 (both ink numbers visible); about 10 lines on the obverse, consistent with eBL's column i.",
    "K.2774": "Photograph checked: obverse, reverse and edges of a wide tablet, ink number K.2774; three columns on each face, consistent with eBL's columns i-vi.",
    "BM.41862": "Photograph checked: obverse, reverse and edges, ink number 41862; two columns on the obverse and text on the reverse, consistent with eBL's columns i-ii and iv.",
    "K.8225": "Photograph checked: one face with the ink number K.8225 and two columns, consistent with eBL's columns ii and iii.",
    "K.8226": "Photograph checked: one face with about 13 lines; eBL gives no column for this fragment.",
    "BM.135909": "Photograph checked: obverse, reverse and edges of a small complete tablet (ink number 1973-6-18,1 / 135909); one column on each face, consistent with eBL's columns iii and iv.",
    "Rm.933": "Photograph checked: obverse, reverse and edges, ink number Rm.933; about 7 lines on one face, consistent with eBL's column iv.",
    "BM.34449": "Photograph checked: obverse, reverse and edges of BM.34449 alone (ink numbers 34449 and Sp.573); about 10 lines in two columns on one face.",
}
GILG_EXCLUDED = {
    "K.913": "eBL notes that its photograph shows K.11913, not K.913.",
    "BM.34916": "the photograph shows a small flake with about 8 lines, while eBL attributes 139 lines in four columns to the join BM.34916 + BM.35419; BM.35419 has no photograph.",
    "BM.34964": "the photograph shows a small piece with about 7 lines on one face, while eBL attributes 31 lines in three columns to the join BM.34964 + BM.35567; BM.35567 has no photograph.",
}
# Joins whose pieces the British Museum photographed separately (eBL joins made after the photography).
GILG_SPLIT = {
    "BM.34160": ["BM.34306", "BM.34499", "Sp.667"],
    "BM.35380": ["BM.36114", "BM.36225"],
    "BM.34423": ["BM.34873", "Sp-III.895"],
    "K.15193": ["Sm.423"],
    "K.3382": ["K.23050"],
    "BM.34449": ["BM.34153"],
    "K.17343": ["K.21790", "Sm.1541"],
}

GILG_INTROS = {
    "I": ("Tablet I: Gilgamesh and the creation of Enkidu",
          "The prologue praises Gilgamesh, king of Uruk, and the walls of his city. Because he oppresses his people, "
          "the gods create Enkidu, a wild man who lives with the animals. A trapper sends the prostitute Shamhat to him; "
          "she civilizes him and tells him of Gilgamesh, who meanwhile dreams of his coming."),
    "II": ("Tablet II: Enkidu comes to Uruk",
           "Shamhat leads Enkidu to the shepherds, where he learns to eat bread and drink ale. He goes to Uruk, "
           "blocks Gilgamesh's way, and the two wrestle and become friends. Gilgamesh proposes an expedition to the "
           "Forest of Cedar to kill its guardian Humbaba; Enkidu and the elders of Uruk warn him against it."),
    "III": ("Tablet III: preparations for the journey",
            "The elders advise Gilgamesh. His mother, the goddess Ninsun, prays to Shamash for his protection and "
            "adopts Enkidu. The two heroes leave Uruk for the Forest of Cedar."),
    "IV": ("Tablet IV: the journey to the Forest of Cedar",
           "On the way, at each stage, the heroes perform a ritual for dreams, and Gilgamesh has a series of "
           "frightening dreams that Enkidu interprets favourably. They reach the edge of the forest."),
    "V": ("Tablet V: the killing of Humbaba",
          "The heroes enter the Forest of Cedar, confront Humbaba, and with the help of Shamash's winds overpower "
          "him. Humbaba pleads for his life and curses them; they kill him, fell the cedars, and float a great "
          "cedar door down the Euphrates to Nippur."),
    "VI": ("Tablet VI: Ishtar and the Bull of Heaven",
           "The goddess Ishtar proposes marriage to Gilgamesh. He rejects her and lists the fates of her former "
           "lovers. She asks her father Anu for the Bull of Heaven, which ravages Uruk until Gilgamesh and Enkidu kill it."),
    "VII": ("Tablet VII: the death of Enkidu",
            "Enkidu dreams that the gods have decided he must die. He curses the door he made from the cedar and the "
            "trapper and Shamhat, then relents at Shamash's word. He describes a dream of the Netherworld and dies after "
            "a long illness."),
    "VIII": ("Tablet VIII: the funeral of Enkidu",
             "Gilgamesh laments Enkidu, has a statue made of him, and lays out treasures and offerings for the gods of "
             "the Netherworld at his funeral."),
    "IX": ("Tablet IX: Gilgamesh's wandering",
           "Afraid of death, Gilgamesh roams the wild in search of Uta-napishti, the survivor of the Flood. He passes "
           "the scorpion-people guarding the mountains of sunrise and walks the dark path of the sun to a garden of "
           "jewelled trees."),
    "X": ("Tablet X: Shiduri, Ur-shanabi and Uta-napishti",
          "Gilgamesh meets the ale-wife Shiduri by the sea, then the boatman Ur-shanabi, who takes him across the "
          "Waters of Death. Uta-napishti speaks to him about the fate of mortals."),
    "XI": ("Tablet XI: the Flood",
           "Uta-napishti tells how the god Ea warned him of the Flood, how he built a boat, survived the deluge, "
           "sent out birds, and was granted eternal life. Gilgamesh fails a test of sleep, obtains a plant of "
           "rejuvenation, loses it to a snake, and returns to Uruk."),
    "XII": ("Tablet XII: Enkidu and the Netherworld",
            "An Akkadian translation of the second half of the Sumerian poem 'Bilgames and the Netherworld', appended "
            "to the series: Enkidu goes down to the Netherworld to fetch Gilgamesh's lost ball and mallet and is held "
            "there; his ghost tells Gilgamesh about the fate of the dead."),
}


def gilg_entries():
    out = []
    for t in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]:
        title, summary = GILG_INTROS[t]
        out.append({
            "chapter": ("SB", t),
            "slug": f"tablet-{t.lower()}",
            "title": f"Epic of Gilgamesh, {title}",
            "description": ("Standard Babylonian Epic of Gilgamesh, Tablet " + t + ": {covered} of {lines} lines, each "
                            "shown on a photographed cuneiform tablet ({tablets} tablets), with the eBL "
                            "transliteration of that tablet and A. R. George's English translation."),
            "intro": (f"<p>{summary}</p>"
                      f"<p>The Standard Babylonian version of the epic, traditionally ascribed to the scholar "
                      f"Sin-leqi-unninni, was written on twelve tablets. Most surviving copies come from the libraries "
                      f"of Ashurbanipal at Nineveh (7th century BCE) and from Babylon and other Babylonian cities "
                      f"(7th-2nd century BCE). This page gives Tablet {t} in the line numbering of the electronic "
                      f"Babylonian Library edition by A. R. George (2022 and later revisions).</p>"),
            "themes": [f"tablet-{t.lower()}"],
        })
    return out


YALE_IIIF = "https://images.collections.yale.edu/iiif/2/ypm:{}/full/!2600,2600/0/default.jpg"
GILG_EXTERNAL = {
    "YBC.2178": {
        "holder": "Yale Peabody Museum, Yale Babylonian Collection, YPM BC 016806 (formerly YBC 2178), the 'Yale tablet' of the Old Babylonian Gilgamesh",
        "holder_short": "Yale Peabody Museum",
        "source": ("Yale Peabody Museum IIIF images (photographs by A. Urcia, 2014), manifest "
                   "https://manifests.collections.yale.edu/ypm/nat/1833370 ; record https://collections.peabody.yale.edu/search/Record/YPM-BC-016806"),
        "licence": "CC0 1.0 (IIIF manifest 'rights'; Yale Peabody Museum open access, http://hdl.handle.net/10079/8931zqj)",
        "faces": {
            "obverse": {"url": YALE_IIIF.format("0cfeab8e-2c7b-4549-a14a-d24d2f39ffbb"), "file": "ybc2178-obverse.jpg"},
            "reverse": {"url": YALE_IIIF.format("37b6ab3b-74ce-47dc-819f-c5a32b7dbf1a"), "file": "ybc2178-reverse.jpg"},
            "left edge": {"url": YALE_IIIF.format("99148bf4-5fb3-4dd0-b974-f45a746fbd78"), "file": "ybc2178-left-edge.jpg"},
        },
        "label_face": {"i": "obverse", "ii": "obverse", "iii": "obverse", "iv": "reverse", "v": "reverse", "vi": "reverse"},
        "check": ("Photograph checked: the Yale images carry the captions 'YBC2178 - Obverse', 'YBC2178 - Reverse' and "
                  "'YBC2178 - Left side'; the obverse and reverse each show three columns, and the left side carries "
                  "two short columns of text, matching eBL's columns i-iii, iv-vi and left edge i-ii."),
    },
}

GILGAMESH = {
    "key": "gilgamesh",
    "ebl_text": ("L", 1, 4),
    "ebl_name": "eBL corpus edition L I.4, Poem of Gilgamesh (ed. A. R. George, rev. G. Rozzi and E. Jiménez)",
    "chapter_prefix": lambda ch: f"{ch['_stage_abbr']} {ch['name']}",
    "chapter_url": lambda ch: f"{EBL_WEB}/corpus/L/1/4/{ch['_stage_abbr']}/{urllib.parse.quote(ch['name'])}",
    "siglum_label": "George 2003 ms.",
    "photo_checks": GILG_CHECKS,
    "excluded": GILG_EXCLUDED,
    "split_photos": GILG_SPLIT,
    "external_photos": GILG_EXTERNAL,
    "entries": gilg_entries() + [{
        "chapter": ("OB", "III"),
        "slug": "old-babylonian-yale-tablet",
        "title": "Epic of Gilgamesh, Old Babylonian version: the Yale tablet (Gilgamesh and Enkidu plan the journey to the Forest of Cedar)",
        "description": ("The Old Babylonian 'Yale tablet' of the Epic of Gilgamesh (YBC 2178, c. 18th century BCE): "
                        "{covered} of {lines} lines, each shown on the Yale Peabody Museum photographs, with the eBL "
                        "transliteration and A. R. George's English translation."),
        "date_approx": "c. 1800-1700 BCE (Old Babylonian tablet)",
        "author_id": "anonymous-babylonian-poet",
        "century": -18,
        "intro": ("<p>The 'Yale tablet' (Yale Babylonian Collection YBC 2178, now YPM BC 016806) is one of the two "
                  "large Old Babylonian tablets of the epic, written about a thousand years before the Nineveh copies. "
                  "It is the third tablet of the Old Babylonian series that began 'Surpassing all other kings'. It "
                  "tells how Gilgamesh and Enkidu, now friends, decide to go to the Forest of Cedar to kill Humbaba, "
                  "how Enkidu and the elders of Uruk try to dissuade Gilgamesh, how weapons are cast for the "
                  "journey, and how the heroes set out. It was first published by M. Jastrow and A. T. Clay in 1920. Its six columns (three on each face) and two short columns on the "
                  "left edge are badly worn in places.</p>"
                  "<p>This page follows the line numbering of the eBL edition of the Old Babylonian Gilgamesh (ed. A. R. "
                  "George). The photographs are the Yale Peabody Museum's, released as CC0.</p>"),
        "themes": ["old-babylonian", "yale-tablet"],
    }],
    "make_entry": standard_entry,
    "author_id": "sin-leqi-unninni",
    "date_approx": "composed c. 1200-1000 BCE; tablets 7th-2nd c. BCE",
    "century": -12,
    "themes": ["gilgamesh", "mesopotamian", "akkadian", "cuneiform", "epic"],
    "translator_short": "A. R. George (eBL edition)",
    "translator_line": ("The English is A. R. George's translation in the eBL edition (CC BY-NC-SA 4.0), one line of "
                        "English per line of the poem; italics mark uncertain renderings, as in the source."),
    "translation_source": "A. R. George, English translation of the Epic of Gilgamesh in the eBL corpus edition (electronic Babylonian Library, LMU Munich, 2022 and later)",
    "translator_notes": [
        "Akkadian: eBL transliteration of the signs on the photographed tablet (manuscript-level ATF), not a composite text.",
        "English: A. R. George's translation in the eBL edition; it renders eBL's composite text, including restorations from other tablets.",
        "Line numbers: eBL edition (based on A. R. George, The Babylonian Gilgamesh Epic, Oxford 2003). Each section also gives the tablet's own column and line numbers.",
    ],
    "collection": {
        "key": "gilgamesh",
        "prefix": "verified-gilgamesh-",
        "label": "Epic of Gilgamesh",
        "group": "Mesopotamia",
        "date_sort": -1200,
        "author_name": "Sin-leqi-unninni (Standard Babylonian version, c. 1200-1000 BCE)",
        "source_url": "https://www.ebl.lmu.de/corpus/L/1/4",
        "critical_edition": "electronic Babylonian Library, Poem of Gilgamesh (ed. A. R. George), manuscript transliterations",
        "translator_name": "A. R. George (eBL edition)",
        "original_lang_label": "Akkadian · eBL transliteration of each tablet",
        "original_lang_code": "akk",
        "edition_label": "",
        "search_terms": "gilgamesh gilgamesh epic enkidu uta-napishti flood utnapishtim nineveh ashurbanipal cuneiform akkadian",
        "description": ("The Standard Babylonian Epic of Gilgamesh, Tablets I-XII, read line by line on photographed "
                        "clay tablets, mostly in the British Museum: each section shows one tablet's own transliteration "
                        "with A. R. George's English translation from the electronic Babylonian Library."),
    },
    "authors": [{
        "id": "sin-leqi-unninni", "name": "Sin-leqi-unninni", "dates": "c. 1200-1000 BCE", "century": -12,
        "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian",
        "bio": "Babylonian scholar to whom later tradition ascribed the Standard Babylonian version of the Epic of Gilgamesh.",
    }, {
        "id": "anonymous-babylonian-poet", "name": "Anonymous (Babylonian poets)", "dates": "2nd-1st millennium BCE",
        "century": -12, "era": "Ancient Near East", "tradition": "mesopotamian", "language": "Akkadian",
        "bio": "Unnamed Babylonian and Assyrian poets and scribes who composed and copied the Akkadian myths and epics preserved on cuneiform tablets.",
    }],
}


def gilg_redirects():
    old = sorted(p.name[:-5] for p in (ROOT / "data" / "sources" / "gilgamesh" / "legacy").glob("verified-gilgamesh-*.json"))
    out = []
    for o in old:
        m = re.match(r"verified-gilgamesh-tablet-([IVX]+)-", o)
        if not m:
            continue
        new = f"verified-gilgamesh-tablet-{m.group(1).lower()}"
        out.append([f"/library/{o}", f"/library/{new}"])
        out.append([f"/library/{o}.html", f"/library/{new}"])
    return out


if __name__ == "__main__":
    GILGAMESH["redirects"] = gilg_redirects()
    build_work(GILGAMESH)
