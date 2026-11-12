#!/usr/bin/env python3
"""
import_eridu_genesis.py -- the Sumerian Flood story ("Eridu Genesis"), Nippur tablet
CBS 10673 (+ CBS 10867), Penn Museum, CDLI P265876.

Chain of evidence
-----------------
1. SCAN      CDLI photograph https://cdli.earth/dl/photo/P265876.jpg (fat-cross: obverse,
             edges, reverse).  Cropped to the obverse (columns i-iii) and the reverse
             (columns iv-vi).  CDLI terms: non-commercial use; copyright the Penn Museum.
2. ORIGINAL  ETCSL 1.7.4 composite transliteration.  ETCSL's bibliography for 1.7.4
             (b174.htm) names one cuneiform source only: "CBS 10673: Nippur, lines 37-50,
             84-100, 135-162, 201-217, 251-261", so the composite is the text of this tablet.
             CDLI has no transliteration of P265876.
3. ENGLISH   ETCSL 1.7.4 translation (CC BY-NC-SA 3.0, Oxford Text Archive).
MAPPING      Column numbering: A. Poebel, Historical Texts (PBS 4/1, Philadelphia 1914),
             pp. 14-16, which transcribes the tablet column by column (public domain; OCR at
             archive.org/details/historicaltexts00poeb).  His columns 1, 2, 5, 6 contain
             ETCSL segments A, B, D, E; his column 3 ends with "mu-an-ki-bi-ta pa-pa-de"
             (ETCSL C 16) and column 4 begins "...dingir-ri-e-ne" (C 17), so segment C runs
             from obverse column iii (C 1-16) over the bottom edge into reverse column iv
             (C 17-28).  Checked on the photograph: three ruled columns on each face; the
             obverse text is preserved at the foot of the columns, the reverse text at the top,
             just after the bottom edge (the tablet is the lower part of a six-column tablet,
             as Poebel says); in the right-hand column of the reverse (column iv) every line
             is broken off at the right, as ETCSL C 17-28 all end in breaks.

Usage:  python3 scripts/import_eridu_genesis.py
"""
# ============================================================================
# Shared ETCSL / CDLI engine (the same block is copied into each Sumerian
# importer: import_eridu_genesis.py, import_enki_ninhursag.py, ...; keep in sync)
# ============================================================================
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"
ETCSL_CGI = "https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text={kind}.{num}&display=Crit&charenc=gcirc"
OTA = "http://ota.ox.ac.uk/desc/2518"
EPSD_LIT = "https://oracc.museum.upenn.edu/epsd2/literary/"
ETCSL_LICENSE = (f"CC BY-NC-SA 3.0 Unported: ETCSL data distributed by the Oxford Text Archive ({OTA}); "
                 f"licence stated at {EPSD_LIT}")
ETCSL_AUTHORS = ("J. A. Black, G. Cunningham, E. Flückiger-Hawker, E. Robson, J. Taylor and G. Zólyomi, "
                 "The Electronic Text Corpus of Sumerian Literature (Oxford 1998-2006)")
CDLI_IMG_LICENSE = ("CDLI terms of use (https://cdli.earth/terms-of-use): images are for the non-commercial use of "
                    "students, scholars and the public; copyright the institution that owns the object")
CDLI_TXT_LICENSE = ("CDLI terms of use: transliterations may be freely copied and re-used according to common "
                    "academic practice, with reference to CDLI (https://cdli.earth)")
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
Image.MAX_IMAGE_PIXELS = None


def fetch(src_dir, url, name, binary=False):
    src_dir.mkdir(parents=True, exist_ok=True)
    p = src_dir / name
    if not p.exists() or p.stat().st_size == 0:
        subprocess.run(["curl", "-s", "-L", "-m", "300", "-A", UA, "-o", str(p), url], check=True)
        if not p.exists() or p.stat().st_size == 0:
            raise RuntimeError(f"empty download {url}")
    return p.read_bytes() if binary else p.read_text(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------ ETCSL
def _sub(m):
    return m.group(1).translate(SUB)


def etcsl_translit_html(cell):
    """One ETCSL composite line (CGI display, charenc=gcirc) -> Unicode transliteration HTML.
    ETCSL marks partly damaged signs with / \\ (half brackets), see etcsl.orinst.ox.ac.uk/display.htm."""
    s = re.sub(r"<span onMouseover=\"doTooltip\(event, '.*?'\)\" onMouseout=\"hideTip\(\)\">", "<span>", cell, flags=re.S)
    assert "doTooltip" not in s, cell[:200]
    s = re.sub(r"\(\s*<span class=\"note\">.*?</span>\s*\)", "", s, flags=re.S)  # editorial notes (English)
    s = re.sub(r"<sub>(\d+)</sub>", _sub, s)
    s = re.sub(r"<sub>(x)</sub>", "ₓ", s)
    s = re.sub(r"<sup>([?!]+)</sup>", r"\1", s)
    s = re.sub(r"<sup>(.*?)</sup>", r"{\1}", s)
    s = re.sub(r'<span class="gap">(.*?)</span>', r"(\1)", s)
    s = re.sub(r"<(?!/?em>)[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"(?<!\d)/|/(?!\d)", "⸢", s)
    s = s.replace("\\", "⸣")
    s = re.sub(r"\s+", " ", s).strip()
    return html.escape(s, quote=False).replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>")


def etcsl_composite(src_dir, num):
    page = fetch(src_dir, ETCSL_CGI.format(kind="c", num=num), f"etcsl_c.{num}.html")
    body = page.split("<h2>", 1)[1]
    lines = []
    seg = ""
    for m in re.finditer(r"<h4>Segment ([A-Z])</h4>|<a name='c\d+\.((?:[A-Z]\.)?[0-9A-Za-z.]+)'></a></td><td>(.*?)</td></tr>",
                         body, flags=re.S):
        if m.group(1):
            seg = m.group(1)
            continue
        lid = m.group(2)
        n = lid.split(".", 1)[1] if re.match(r"[A-Z]\.", lid) else lid
        mnum = re.match(r"\d+", n)
        num = int(mnum.group(0)) if mnum else (lines[-1]["int"] if lines else 0)  # unnumbered variant lines
        lines.append({"id": lid, "seg": seg, "n": n, "int": num, "html": etcsl_translit_html(m.group(3))})
    return lines


def etcsl_clean_tr(fragment):
    s = re.sub(r'\{\s*\(<span class="note">(.*?)</span>\)\s*(.*?)\}', r"(<em>\1</em> \2)", fragment, flags=re.S)
    s = re.sub(r'<span class="note">(.*?)</span>', r"<em>\1</em>", s, flags=re.S)
    s = re.sub(r'<span class="transux">(.*?)</span>', r"<em>\1</em>", s, flags=re.S)
    s = re.sub(r'<span class="gap">(.*?)</span>', r"(\1)", s, flags=re.S)
    s = re.sub(r"<(?!/?em>)[^>]+>", "", s)
    s = html.unescape(s).replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("( <em>", "(<em>").replace("</em> )", "</em>)")


def etcsl_translation(src_dir, num):
    page = fetch(src_dir, ETCSL_CGI.format(kind="t", num=num), f"etcsl_t.{num}.html")
    body = page.split("<body class=\"translation\"", 1)[1]
    intro = re.search(r'<body id="[^"]+">\s*\(<span class="gap">(.*?)</span>\)', body, flags=re.S)
    paras = []
    for m in re.finditer(r"<p>(?:\s|&nbsp;)*<a href='[^']*lineid=c\d+\.([^']+)'>([^<]+)</a><a name='[^']+'></a>(.*?)</p>",
                         body, flags=re.S):
        lid = m.group(1)
        seg = lid.split(".")[0] if re.match(r"[A-Z]\.", lid) else ""
        label = m.group(2).strip().rstrip(".")
        a, _, b = label.partition("-")
        paras.append({"seg": seg, "label": label, "start": int(re.match(r"\d+", a).group(0)),
                      "end": int(re.match(r"\d+", b or a).group(0)), "first_id": lid,
                      "text": etcsl_clean_tr(m.group(3))})
    return (etcsl_clean_tr(intro.group(1)) if intro else ""), paras


def assign_lines(paras, comp):
    """Split the composite into ETCSL translation paragraphs.  A paragraph starts at the composite line its
    ETCSL link points to and runs to the line before the next paragraph's link.  Where ETCSL's labels overlap
    (e.g. '1-10' then '10-14') the shared line stays with the earlier paragraph.  Lines after a paragraph's
    label range but before the next paragraph (broken lines ETCSL leaves untranslated) are listed in
    p['untranslated']."""
    idx = {ln["id"]: i for i, ln in enumerate(comp)}
    starts = []
    for p in paras:
        fid = p["first_id"]
        if fid not in idx:
            raise KeyError(f"paragraph start {fid} not in composite")
        starts.append(idx[fid])
    for k, p in enumerate(paras):
        a = starts[k]
        b = starts[k + 1] if k + 1 < len(paras) else len(comp)
        p["lines"] = comp[a:b]
        p["untranslated"] = []
    for k in range(1, len(paras)):
        p, prev = paras[k], paras[k - 1]
        if p["lines"] and p["seg"] == prev["seg"] and p["lines"][0]["int"] == prev["end"] == p["start"] \
                and p["label"].split("-")[0] == prev["label"].split("-")[-1]:
            prev["lines"].append(p["lines"].pop(0))
    for p in paras:
        p["untranslated"] = [ln["id"] for ln in p["lines"] if ln["int"] > p["end"]]
    return paras


def sec_label(p):
    return f"{p['seg']} {p['label']}".strip()


# ------------------------------------------------------------------ CDLI ATF
def atf_html(s):
    """ASCII C-ATF -> Unicode transliteration (sz=š, s,=ṣ, t,=ṭ, indices subscript), HTML-escaped."""
    s = s.replace("($blank space$)", "(blank space)")
    s = re.sub(r"\(\$(.*?)\$\)", r"(\1)", s)
    s = s.replace("sz", "š").replace("SZ", "Š").replace("s,", "ṣ").replace("S,", "Ṣ")
    s = s.replace("t,", "ṭ").replace("T,", "Ṭ")
    s = re.sub(r"(?<=[A-Za-zšṣṭŠṢṬ])(\d+)", lambda m: m.group(1).translate(SUB), s)
    return html.escape(s.strip(), quote=False)


def parse_atf(text, qno=None):
    """[{surface, column, line, atf, q}] for every numbered line of a CDLI ATF; q = composite line label
    from '>>Qnnnnnn label' (only for composite qno when given)."""
    out, surf, col, cur = [], "obverse", "", None
    for raw in text.split("\n"):
        ln = raw.rstrip()
        if ln.startswith("@"):
            tag = ln[1:].split()
            if not tag:
                continue
            if tag[0] in ("obverse", "reverse", "left", "right", "top", "bottom", "edge", "seal"):
                surf, col = tag[0] if tag[0] not in ("left", "right", "top", "bottom") else f"{tag[0]} edge", ""
            elif tag[0] == "surface":
                surf, col = "surface " + " ".join(tag[1:]), ""
            elif tag[0] == "column":
                col = tag[1]
            continue
        m = re.match(r"^(\d+'*(?:\.[a-z0-9]+)?'*)\.\s(.*)$", ln)
        if m:
            cur = {"surface": surf, "column": col, "line": m.group(1), "atf": m.group(2).strip(), "q": None}
            out.append(cur)
            continue
        m = re.match(r"^>>(Q\d+) (\S+)", ln)
        if m and cur is not None and (qno is None or m.group(1) == qno):
            cur["q"] = m.group(2)
    return out


ROMAN = {str(i): r for i, r in enumerate(["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]) if i}


def place(ln):
    s = ln["surface"]
    return f"{s}, column {ROMAN.get(ln['column'], ln['column'])}" if ln["column"] else s


# ------------------------------------------------------------------ images
def save_crop(src_path, box, out_path, max_side=2600):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src_path).convert("RGB")
    c = im.crop(box) if box else im
    if max(c.size) > max_side:
        c.thumbnail((max_side, max_side), Image.LANCZOS)
    c.save(out_path, quality=86)
    return out_path


# ------------------------------------------------------------------ witnesses (CDLI tablets linked to a composite)
import difflib  # noqa: E402

_NORM = str.maketrans({"š": "sz", "Š": "sz", "ĝ": "g", "Ĝ": "g", "ḫ": "h", "Ḫ": "h", "ṣ": "s", "ṭ": "t"})


def norm_signs(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).translate(_NORM).lower()
    s = re.sub(r"[₀-₉]", "", s)
    s = re.sub(r"(?<=[a-z])\d+", "", s)
    s = re.sub(r"[\[\]⸢⸣#?!*<>«»{}()…]|\.\.\.", " ", s)
    return [t for t in re.split(r"[\s\-.:]+", s) if t and t not in ("x",)]


def similarity(a, b):
    sa, sb = norm_signs(a), norm_signs(b)
    if not sa or not sb:
        return 0.0
    return difflib.SequenceMatcher(None, sa, sb).ratio()


def qlabel_to_id(q, segmented=False):
    q = q.strip()
    m = re.match(r"^([A-Z])?0*(\d+[A-Za-z]*)$", q)
    if not m:
        return None
    seg, n = m.group(1), m.group(2)
    return f"{seg}.{n}" if seg else n


def load_witness(src_dir, p, qno):
    n = int(p[1:])
    meta = json.loads(fetch(src_dir, f"https://cdli.earth/artifacts/{n}/json", f"{p}.json"))
    meta = meta[0] if isinstance(meta, list) else meta
    page = fetch(src_dir, f"https://cdli.earth/artifacts/{n}", f"{p}.html")
    ins = re.findall(r'href="/inscriptions/(\d+)/atf"', page)
    atf = fetch(src_dir, f"https://cdli.earth/inscriptions/{ins[0]}/atf", f"{p}.atf") if ins else ""
    lines = parse_atf(atf, qno)
    prov = meta.get("provenience")
    prov = (prov or {}).get("provenience", "") if isinstance(prov, dict) else (prov or "")
    pubs = [((x.get("publication") or {}).get("designation") or "") + (" " + x["exact_reference"] if x.get("exact_reference") else "")
            for x in meta.get("publications", [])]
    period = (meta.get("period") or {}).get("period", "") if isinstance(meta.get("period"), dict) else ""
    mus = (meta.get("museum_no") or "").strip()
    if not mus or mus.endswith("—"):
        exc = (meta.get("excavation_no") or "").strip()
        uet = [x for x in pubs if x.startswith("UET ")]
        bits = []
        if uet:
            bits.append(re.sub(r"UET (\d+) 0*(\d+)", r"UET \1 \2", uet[0].split(",")[0]))
        if exc and not exc.endswith("—"):
            bits.append(re.sub(r"T0*(\d)", r"T\1", exc))
        acc = (meta.get("accession_no") or "").strip()
        if not bits and acc and not acc.endswith("—"):
            bits.append(acc)
        mus = " = ".join(bits) or f"CDLI {p}"
    return {"p": p, "museum": mus, "designation": meta.get("designation", ""),
            "provenience": ("provenance uncertain" if re.sub(r"\s*\(mod\..*?\)", "", prov).strip() in ("", "uncertain")
                            else re.sub(r"\s*\(mod\..*?\)", "", prov).strip()), "period": period,
            "publications": [x.strip() for x in pubs if x.strip()], "lines": lines,
            "page": f"https://cdli.earth/artifacts/{n}", "photo": f"https://cdli.earth/dl/photo/{p}.jpg"}


def check_links(w, comp_by_id, min_sim=0.25):
    """Attach composite ids to witness lines and score each link against the ETCSL composite."""
    bad, scores = [], []
    by_n = {}
    for cid_, cl in comp_by_id.items():
        by_n.setdefault(cl["n"], []).append(cid_)
    for ln in w["lines"]:
        q = re.sub(r"\.[a-z]\.?$", "", ln["q"]) if ln["q"] else None
        cid = qlabel_to_id(q) if q else None
        if cid and cid not in comp_by_id and len(by_n.get(cid, [])) == 1:
            cid = by_n[cid][0]
        ln["cid"] = cid if cid in comp_by_id else None
        if ln["q"] and ln["cid"] is None:
            bad.append((ln["line"], ln["q"], "no such ETCSL line"))
            continue
        if ln["cid"]:
            sc = similarity(atf_html(ln["atf"]), comp_by_id[ln["cid"]]["html"])
            # CDLI's link may be off by a line or two: re-link to a neighbouring ETCSL line whose sign
            # sequence matches much better (>= 0.5 and at least 0.25 above the linked line)
            ids = list(comp_by_id)
            k = ids.index(ln["cid"])
            best, bsc = None, sc
            for j in range(max(0, k - 3), min(len(ids), k + 4)):
                if j == k:
                    continue
                s2 = similarity(atf_html(ln["atf"]), comp_by_id[ids[j]]["html"])
                if s2 >= 0.5 and s2 >= sc + 0.25 and s2 > bsc:
                    best, bsc = ids[j], s2
            if best:
                ln["relinked_from"] = ln["cid"]
                ln["cid"], sc = best, bsc
            ln["sim"] = sc
            scores.append(sc)
            if sc < min_sim and len(norm_signs(atf_html(ln["atf"]))) >= 3:
                bad.append((ln["line"], ln["q"], f"low similarity {sc:.2f}"))
    # keep links in composite order: a later tablet line that lands on or before the previous line's
    # ETCSL line is moved to the next free ETCSL line if that matches (>= 0.5), otherwise dropped
    ids = list(comp_by_id)
    pos = {c: i for i, c in enumerate(ids)}
    last = -1
    for ln in w["lines"]:
        cid = ln.get("cid")
        if not cid:
            continue
        sub = bool(ln["q"] and re.search(r"\.[a-z]\.?$", ln["q"]))
        if pos[cid] <= last and not (sub and pos[cid] == last):
            moved = None
            for j in range(last + 1, min(len(ids), last + 3)):
                s2 = similarity(atf_html(ln["atf"]), comp_by_id[ids[j]]["html"])
                if s2 >= 0.5:
                    moved, ln["sim"] = ids[j], s2
                    break
            if moved:
                ln.setdefault("relinked_from", cid)
                ln["cid"] = moved
            else:
                ln["cid"] = None
                bad.append((ln["line"], ln["q"], "out of order, dropped"))
                continue
        last = max(last, pos[ln["cid"]])
    return bad, (sum(scores) / len(scores) if scores else 0)


def align_by_text(w, comp, min_sim=0.6, min_signs=3):
    """For a witness without CDLI composite links: match each of its lines to the ETCSL composite line with
    the most similar sign sequence (>= min_sim, at least min_signs readable signs), then keep only the
    longest run of matches that is in composite order (a manuscript follows the composition's order)."""
    order = {ln["id"]: i for i, ln in enumerate(comp)}
    comp_signs = [(ln["id"], norm_signs(ln["html"])) for ln in comp]
    cands = []
    for k, ln in enumerate(w["lines"]):
        if ln.get("cid"):
            continue
        sig = norm_signs(atf_html(ln["atf"]))
        if len(sig) < min_signs:
            continue
        best, bs, second = None, 0.0, 0.0
        for cid, cs in comp_signs:
            if not cs:
                continue
            r = difflib.SequenceMatcher(None, sig, cs).ratio()
            if r > bs:
                best, second, bs = cid, bs, r
            elif r > second:
                second = r
        if best and bs >= min_sim and bs - second >= 0.05:
            cands.append((k, best, bs))
    # longest increasing subsequence on composite order
    n = len(cands)
    dp, prv = [1] * n, [-1] * n
    for i in range(n):
        for j in range(i):
            if order[cands[j][1]] < order[cands[i][1]] and dp[j] + 1 > dp[i]:
                dp[i], prv[i] = dp[j] + 1, j
    keep, i = [], (max(range(n), key=lambda x: dp[x]) if n else -1)
    while i >= 0:
        keep.append(cands[i])
        i = prv[i]
    for k, cid, sc in keep:
        w["lines"][k]["cid"], w["lines"][k]["sim"], w["lines"][k]["how"] = cid, sc, "text"
    return len(keep)


def witness_place(ln):
    s = ln["surface"]
    return f"{s}, column {ROMAN.get(ln['column'], ln['column'])}" if ln["column"] else s


def plan_sections(paras, witnesses, max_w=4):
    """For each paragraph choose photographed witnesses (greedy by coverage) and collect their lines."""
    for p in paras:
        need = [ln["id"] for ln in p["lines"]]
        needset = set(need)
        chosen, covered = [], set()
        while len(chosen) < max_w:
            best, gain = None, 0
            for w in witnesses:
                if w in chosen:
                    continue
                carried = {ln["cid"] for ln in w["lines"] if ln.get("cid") in needset}
                g = len(carried - covered)
                if g > gain or (g == gain and g > 0 and best is not None and w["nlinks"] > best["nlinks"]):
                    best, gain = w, g
            if not best:
                break
            chosen.append(best)
            covered |= {ln["cid"] for ln in best["lines"] if ln.get("cid") in needset}
        blocks = []
        shown = set()
        for w in chosen:
            ls = [ln for ln in w["lines"] if ln.get("cid") in needset and ln["cid"] not in shown]
            shown |= {ln["cid"] for ln in ls}
            blocks.append((w, ls))
        order = {cid: i for i, cid in enumerate(need)}
        blocks.sort(key=lambda b: min(order[ln["cid"]] for ln in b[1]))
        # a paragraph is shown only if the chosen tablets carry at least half of its lines; otherwise the
        # English would mostly render manuscripts that are not shown
        if need and len(covered) / len(need) < 0.5:
            blocks = []
        p["blocks"] = blocks
        p["missing"] = [cid for cid in need if cid not in covered]
    return paras


def ranges(ids, comp_order):
    """Compress a list of composite ids into 'a-b' runs following composite order."""
    idx = sorted(comp_order[i] for i in ids)
    inv = {v: k for k, v in comp_order.items()}
    out, start, prev = [], None, None
    for i in idx:
        if start is None:
            start = prev = i
        elif i == prev + 1:
            prev = i
        else:
            out.append((start, prev))
            start = prev = i
    if start is not None:
        out.append((start, prev))
    lab = lambda i: inv[i].replace(".", " ")
    return ", ".join(lab(a) if a == b else f"{lab(a)}-{lab(b)}" for a, b in out)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def build_witness_entry(cfg):
    """Witness mode: sections = ETCSL paragraphs; Sumerian = the CDLI transliterations of the photographed
    tablets that carry the paragraph's lines (via their CDLI links to the composite); English = ETCSL."""
    src, key = cfg["src"], cfg["key"]
    comp = etcsl_composite(src, cfg["etcsl"])
    intro_note, paras = etcsl_translation(src, cfg["etcsl"])
    assign_lines(paras, comp)
    comp_by_id = {ln["id"]: ln for ln in comp}
    comp_order = {ln["id"]: i for i, ln in enumerate(comp)}
    witnesses = []
    for p in cfg["witnesses"]:
        w = load_witness(src, p, cfg["qno"])
        if "cast" in w["museum"].lower():  # the CDLI photograph may show a cast, not the tablet
            print(f"  {p} {w['museum']}: catalogued with a cast, not used")
            continue
        bad, avg = check_links(w, comp_by_id)
        w["method"] = "links"
        if cfg.get("align_text") and not any(ln.get("cid") for ln in w["lines"]):
            align_by_text(w, comp)
            w["method"] = "text"
            avg = sum(ln["sim"] for ln in w["lines"] if ln.get("cid")) / max(1, sum(1 for ln in w["lines"] if ln.get("cid")))
        w["nlinks"] = sum(1 for ln in w["lines"] if ln.get("cid"))
        rel = [(ln["line"], ln["relinked_from"], ln["cid"]) for ln in w["lines"] if ln.get("relinked_from")]
        if rel:
            print(f"  {p} re-linked {len(rel)}: {rel[:8]}")
        print(f"  {p} {w['museum']:<28} links {w['nlinks']:>3}/{len(w['lines']):<3} mean similarity {avg:.2f}"
              + (f"  CHECK {bad[:4]}" if bad else ""))
        for ln in w["lines"]:  # drop links that failed the check
            if ln.get("cid") and ln.get("sim", 1) < cfg.get("min_sim", 0.25) and len(norm_signs(atf_html(ln["atf"]))) >= 3:
                ln["cid"] = None
        if w["nlinks"]:
            witnesses.append(w)
    while True:  # plan, then drop tablets whose CDLI photograph is too small to read (long side < 1200 px)
        plan_sections(paras, witnesses, cfg.get("max_w", 4))
        used = []
        for p in paras:
            for w, _ in p["blocks"]:
                if w not in used:
                    used.append(w)
        small = []
        for w in used:
            fetch(src, w["photo"], f"{w['p']}.jpg", binary=True)
            with Image.open(src / f"{w['p']}.jpg") as im:
                if max(im.size) < 1200:
                    small.append(w)
        if not small:
            break
        for w in small:
            print(f"  {w['p']} {w['museum']}: photograph too small ({w['p']}.jpg), not used")
            witnesses.remove(w)
    scan_dir = cfg["scan_dir"]
    for w in used:
        img = src / f"{w['p']}.jpg"
        fetch(src, w["photo"], f"{w['p']}.jpg", binary=True)
        w["face_scans"] = {}
        if w["p"] in cfg.get("faces", {}):  # one crop per face, boxes checked on the image
            for surf, box in cfg["faces"][w["p"]].items():
                out = save_crop(img, box, scan_dir / f"{slug(w['museum'])}-{slug(surf)}.jpg")
                w["face_scans"][surf] = f"{key}/{out.name}"
            w["scan"] = next(iter(w["face_scans"].values()))
        else:
            out = save_crop(img, cfg.get("boxes", {}).get(w["p"]), scan_dir / f"{slug(w['museum'])}.jpg")
            w["scan"] = f"{key}/{out.name}"

    sections, skipped = [], []
    for p in paras:
        lab = sec_label(p)
        if not p["blocks"]:
            skipped.append(lab)
            continue
        parts, notes = [], []
        for w, ls in p["blocks"]:
            prev = None
            for ln in ls:
                pl = witness_place(ln)
                if pl != prev:
                    parts.append(f"<em>[{html.escape(w['museum'])}, {pl}]</em>")
                    prev = pl
                parts.append(f"<sup>{ln['cid'].replace('.', '')}</sup>{atf_html(ln['atf'])}")
            places = []
            for ln in ls:
                pl = witness_place(ln)
                if pl not in places:
                    places.append(pl)
            span = f"{witness_place(ls[0])} line {ls[0]['line']}" + (
                f" to {witness_place(ls[-1])} line {ls[-1]['line']}" if len(ls) > 1 else "")
            notes.append(f"{w['museum']} (CDLI {w['p']}), {span} = ETCSL lines {ranges([ln['cid'] for ln in ls], comp_order)}")
        methods = {w["method"] for w, _ in p["blocks"]}
        how = []
        if "links" in methods:
            relinked = [ln for w, ls in p["blocks"] for ln in ls if ln.get("relinked_from")]
            how.append(f"from the CDLI transliterations' own links to the composite ({cfg['qno']}, ETCSL numbering), "
                       "each link checked against the ETCSL composite text"
                       + (f" ({len(relinked)} line(s) where CDLI's link is off by a line are placed at the ETCSL line with the "
                          "same sign sequence)" if relinked else ""))
        if "text" in methods:
            how.append("by matching each line of the tablet's CDLI transliteration with the ETCSL composite line that has "
                       "the same sign sequence (in composite order)")
        faced = [w for w, _ in p["blocks"] if w["face_scans"]]
        note = ("; ".join(notes) + ". Line correspondence " + "; for other tablets ".join(how) + ". "
                + (cfg.get("face_note", "") + " " if faced else "")
                + ("The photograph is the whole tablet (CDLI fat-cross: obverse above, reverse below, edges beside), "
                   "checked by eye for each tablet used; the transliteration names the face and column of every block."
                   if len(faced) < len(p["blocks"]) else ""))
        if p["missing"]:
            note += (f" ETCSL line(s) {ranges(p['missing'], comp_order)} are not shown from the tablet(s) here (not preserved "
                     "on them, or the correspondence could not be confirmed): for those lines the English renders other manuscripts.")
        note += " The English is ETCSL's translation of the composite text."
        if p["untranslated"]:
            note += f" Line(s) {', '.join(x.replace('.', ' ') for x in p['untranslated'])} are left untranslated by ETCSL."
        sections.append({
            "section": lab,
            "original_ref": f"ETCSL {cfg['etcsl']} lines {lab}; " + "; ".join(
                (f"{w['museum']} {witness_place(ls[0])} {ls[0]['line']}" + (
                    f" to {witness_place(ls[-1])} {ls[-1]['line']}" if len(ls) > 1 else ""))
                for w, ls in p["blocks"]),
            "original_text": "<br>\n".join(parts),
            "text": f"<p><sup>{lab}</sup> {p['text']}</p>",
            "scan_pages": list(dict.fromkeys(
                (w["face_scans"].get(ln["surface"], w["scan"]) if w["face_scans"] else w["scan"])
                for w, ls in p["blocks"] for ln in ls)),
            "scan_note": note,
        })
    return {"sections": sections, "skipped": skipped, "used": used, "intro_note": intro_note, "paras": paras,
            "comp": comp}


def write_witness_outputs(M, r):
    """Entry JSON + collection JSON for a witness-mode work.  M = metadata dict from the importer."""
    sections, used = r["sections"], r["used"]
    wl = "".join(f"<li>{html.escape(w['museum'])} (CDLI {w['p']}; {html.escape(w['provenience'] or 'provenance not recorded')})</li>"
                 for w in used)
    total = len(r["comp"])
    missing = sum(len(p["missing"]) for p in r["paras"] if p["blocks"]) + sum(len(p["lines"]) for p in r["paras"] if not p["blocks"])
    intro = (M["intro"] +
             ("<p>No single photographed tablet preserves the whole text. " if len(used) > 1 else "<p>")
             + "Each section below is one paragraph of the ETCSL translation, shown with "
             "the photographed tablet or tablets that carry those lines and their own transliterations. The block heading names the "
             "tablet, the face and the column; the superscript numbers are ETCSL's line numbers.</p>"
             f"<p><strong>Coverage.</strong> Of the {total} lines of the ETCSL composite, {total - missing} are shown on at least one "
             "photographed tablet. The remaining lines are named in the notes of the sections concerned; the English there renders "
             "manuscripts without a usable photograph." + (" " + M["gaps"] if M.get("gaps") else "") + "</p>"
             + (f"<p><strong>Not shown.</strong> ETCSL paragraphs {', '.join(r['skipped'])} are left out: no photographed tablet "
                "carries at least half of their lines.</p>" if r["skipped"] else "")
             + f"<p>Tablets shown:</p><ul>{wl}</ul>")
    tid = M["tid"]
    entry = {
        "id": tid, "slug": tid, "title": M["title"],
        "language": "Sumerian (transliteration) / English",
        "source": M["source"], "description": M["description"], "introduction": intro,
        "translator_notes": [n for n in [r["intro_note"]] if n] + [
            "Transliteration: CDLI ATF rendered in Unicode (sz = š, s, = ṣ, t, = ṭ, sign indices as subscripts). [ ] broken signs, # damaged sign, ? uncertain reading, ! corrected sign, x unreadable sign.",
            "Where several tablets carry a paragraph, the first tablet's lines are given in full and later tablets add only lines the first does not carry.",
        ] + M.get("notes", []),
        "translation": sections,
        "verification": {
            "scan_source": "Cuneiform Digital Library Initiative photographs: " + "; ".join(f"{w['p']} {w['photo']}" for w in used),
            "scan_license": CDLI_IMG_LICENSE + " (" + M["holders"] + ")",
            "scan_manuscript": "; ".join(f"{w['museum']} ({w['p']}, {w['provenience'] or 'provenance not recorded'})" for w in used),
            "scan_mapping": (f"CDLI transliterations linked line by line to composite {M['qno']} (ETCSL {M['etcsl']} numbering), "
                             "each link checked against the ETCSL composite text" + (
                                 "; tablets without CDLI links aligned to the composite by matching sign sequences line by line, in composite order"
                                 if any(w["method"] == "text" for w in used) else "")
                             + "; tablets chosen per ETCSL paragraph by the lines they carry; each photograph checked by eye"),
            "scan_mapping_urls": [f"https://cdli.earth/artifacts/composites-score/{M['qno']}"] + [w["page"] for w in used],
            "scan_local_paths": [x for w in used for x in (list(w["face_scans"].values()) or [w["scan"]])],
            "original_text_source": "CDLI transliterations of the tablets listed (https://cdli.earth/artifacts/<id>)",
            "original_text_license": CDLI_TXT_LICENSE,
            "translation_source": f"{ETCSL_AUTHORS}, {M['etcsl']} '{M['etcsl_title']}: translation', {M['etcsl_url']}",
            "translation_license": ETCSL_LICENSE,
            "translator": "ETCSL (Black, Cunningham, Flückiger-Hawker, Robson, Taylor, Zólyomi)",
            "verified_date": TODAY,
        },
    }
    write_json(PUB / f"{tid}.json", entry)
    coll = {
        "collection": {
            "key": M["key"], "prefix": f"verified-{M['key']}-", "label": M["label"],
            "group": M.get("group", "Mesopotamia"), "date_sort": M["date_sort"],
            "author_name": M["author_name"],
            "source_url": f"https://cdli.earth/artifacts/composites-score/{M['qno']}",
            "critical_edition": f"CDLI transliterations of the tablets; ETCSL {M['etcsl']} composite",
            "translator_name": "ETCSL (Black et al., 1998-2006)",
            "original_lang_label": "Sumerian · CDLI transliteration",
            "original_lang_code": "sux", "edition_label": "",
            "search_terms": M["search_terms"], "description": M["shelf"],
        },
        "texts": [{
            "id": tid, "slug": tid, "order": 1, "title": M["title"], "author_id": M["author_id"],
            "language": "Sumerian", "era": "Ancient Near East", "tradition": "sumerian", "category": M["category"],
            "date_approx": M["date_approx"], "century": M["century"],
            "source": M["source"], "description": M["description"],
            "themes": M["themes"] + ["verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": x, "caption": f"{w['museum']} ({w['p']})" + (f", {k}" if k else "")}
                                for w in used for k, x in (list(w["face_scans"].items()) or [("", w["scan"])])]},
        }],
    }
    if M.get("authors"):
        coll["authors"] = M["authors"]
    write_json(M["coll_path"], coll)
    print(f"wrote {tid}: {len(sections)} sections, {len(used)} tablets; skipped {r['skipped']}; "
          f"{total - missing}/{total} lines on photographed tablets")
    return total, missing


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
# ============================================================================
# end of shared engine
# ============================================================================


KEY = "eridu-genesis"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TID = f"verified-{KEY}-cbs-10673"
ETCSL = "1.7.4"
CDLI_PAGE = "https://cdli.earth/artifacts/265876"
PHOTO = "https://cdli.earth/dl/photo/P265876.jpg"
POEBEL = "https://archive.org/details/historicaltexts00poeb"

# crop boxes in the 4424 x 6472 CDLI photograph (checked on the image)
FACES = {"obverse": (640, 760, 3760, 3170), "reverse": (660, 4000, 3740, 6300)}
# (segment, first line, last line) -> (face, column), after Poebel 1914 (see docstring)
COLUMNS = [("A", 1, 14, "obverse", "i"), ("B", 1, 18, "obverse", "ii"), ("C", 1, 16, "obverse", "iii"),
           ("C", 17, 28, "reverse", "iv"), ("D", 1, 17, "reverse", "v"), ("E", 1, 12, "reverse", "vi")]


def column_of(ln):
    for seg, a, b, face, col in COLUMNS:
        if ln["seg"] == seg and a <= ln["int"] <= b:
            return face, col
    raise KeyError(ln["id"])


def main():
    fetch(SRC, PHOTO, "P265876.jpg", binary=True)
    fetch(SRC, CDLI_PAGE + "/json", "P265876.json")
    fetch(SRC, "https://etcsl.orinst.ox.ac.uk/section1/b174.htm", "etcsl_b174.htm")
    comp = etcsl_composite(SRC, ETCSL)
    intro_note, paras = etcsl_translation(SRC, ETCSL)
    assert len(comp) == 89, len(comp)
    assign_lines(paras, comp)
    scans = {}
    for face, box in FACES.items():
        out = save_crop(SRC / "P265876.jpg", box, SCAN_DIR / f"cbs-10673-{face}.jpg")
        scans[face] = f"{KEY}/{out.name}"

    sections = []
    for p in paras:
        parts, faces, cols, prev = [], [], [], None
        for ln in p["lines"]:
            face, col = column_of(ln)
            if (face, col) != prev:
                parts.append(f"<em>[{face}, column {col}]</em>")
                prev = (face, col)
                cols.append(f"{face} column {col}")
                if face not in faces:
                    faces.append(face)
            parts.append(f"<sup>{ln['seg']}{ln['n']}</sup>{ln['html']}")
        lab = sec_label(p)
        note = (f"CBS 10673 {', '.join(cols)}: ETCSL segment {p['seg']} lines {p['lines'][0]['n']}-{p['lines'][-1]['n']}. "
                "Column numbering after Poebel 1914 (PBS 4/1, pp. 14-16), who transcribes the tablet column by column. "
                "Checked on the photograph: the obverse text is at the foot of its three columns (left to right i, ii, iii); "
                "the reverse text is at the top of its three columns, just after the bottom edge, read from right to left "
                "(iv, v, vi); in reverse column iv every line is broken off at the right, as in ETCSL lines C 17-28. "
                "The Sumerian is ETCSL's transliteration, whose only source is this tablet.")
        if p["lines"][0]["int"] != p["start"]:
            note += (f" ETCSL heads this paragraph {p['label']}; line {p['seg']}{p['start']} is shown with the previous "
                     "paragraph, whose English renders it.")
        if p["untranslated"]:
            note += f" Line(s) {', '.join(x.replace('.', ' ') for x in p['untranslated'])} are too broken for ETCSL to translate."
        sections.append({
            "section": lab,
            "original_ref": f"ETCSL 1.7.4 segment {p['seg']} lines {p['label']}; CBS 10673 {', '.join(cols)}",
            "original_text": "<br>\n".join(parts),
            "text": f"<p><sup>{lab}</sup> {p['text']}</p>",
            "scan_pages": [scans[f] for f in faces],
            "scan_note": note,
        })

    intro = (
        "<p>The <strong>Sumerian Flood story</strong>, often called the <em>Eridu Genesis</em>, tells how the gods An, Enlil, Enki "
        "and Ninhursaĝa made mankind and the animals, how kingship came down from heaven and the first cities (Eridu, Bad-tibira, "
        "Larak, Sippar and Shuruppak) were founded, and how the gods sent a flood to destroy mankind. Enki warns the pious king "
        "Ziusudra, who survives the flood in a great boat for seven days and seven nights, offers sacrifice to the sun god Utu, "
        "and is given 'life like a god' and settled in Dilmun. It is the Sumerian telling of the Flood story also known from the "
        "Babylonian epics of Atrahasis and Gilgamesh, and it invites comparison with Genesis 6-9.</p>"
        "<p>The text survives almost entirely on one tablet from Nippur, <strong>CBS 10673</strong> in the Penn Museum, Philadelphia, "
        "written in the Old Babylonian period (about 1800-1600 BCE). Arno Poebel found it among the museum's tablets in 1912 and published "
        "it in 1914. Only the lower third of the tablet survives: the bottom of the three columns on the obverse and the top of the three "
        "columns on the reverse. Between about 32 and 38 lines are lost in each gap, so the story is far from complete. "
        "A small joined fragment (CBS 10867) sits at the top of the obverse in the photograph.</p>"
        "<p>Each section below is one paragraph of the ETCSL translation (segments A to E are the surviving blocks of text). "
        "The photograph is the face of the tablet that carries the section, and the transliteration is marked with the column.</p>"
        "<p><strong>Gaps.</strong> The lost parts of the columns (noted in the English) cannot be shown. "
        "Two further manuscripts of the story are not included: a fragment from Ur (published in 2018, after the ETCSL edition) "
        "and a tablet in the Schøyen Collection (MS 3026) that is not yet fully published.</p>"
    )
    entry = {
        "id": TID, "slug": TID,
        "title": "The Sumerian Flood Story (Eridu Genesis): Nippur tablet CBS 10673",
        "language": "Sumerian (transliteration) / English",
        "source": "Penn Museum CBS 10673 photograph via CDLI (P265876) + ETCSL 1.7.4 transliteration and English translation (CC BY-NC-SA 3.0); columns after Poebel 1914",
        "description": "The Sumerian account of the Flood: the creation of mankind, the first cities, and Ziusudra's survival in a boat, on the Nippur tablet CBS 10673 (c. 1800-1600 BCE).",
        "introduction": intro,
        "translator_notes": [n for n in [intro_note] if n] + [
            "Transliteration: ETCSL 1.7.4 composite text in Unicode (ETCSL's c and j written š and ĝ; ⸢ ⸣ mark partly damaged signs, [ ] lost signs restored or marked …).",
            "Line labels such as A1 or C17 are ETCSL's: segment letter and line number within the segment.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Cuneiform Digital Library Initiative photograph of P265876, {PHOTO} (artifact page {CDLI_PAGE}); cropped to obverse and reverse",
            "scan_license": "Penn Museum (University of Pennsylvania Museum of Archaeology and Anthropology) object; " + CDLI_IMG_LICENSE,
            "scan_manuscript": "Penn Museum CBS 10673 + CBS 10867, clay tablet, six columns (lower third preserved), Nippur, Old Babylonian (c. 1800-1600 BCE)",
            "scan_mapping": "Columns after A. Poebel, Historical Texts (PBS 4/1, 1914) pp. 14-16 (transcription by column), matched to ETCSL segments by their opening and closing lines; faces and column order checked on the photograph (see each scan_note)",
            "scan_mapping_urls": [POEBEL, CDLI_PAGE, "https://etcsl.orinst.ox.ac.uk/section1/b174.htm"],
            "scan_local_paths": [scans["obverse"], scans["reverse"]],
            "original_text_source": f"{ETCSL_AUTHORS}, 1.7.4 'The Flood story: composite text', https://etcsl.orinst.ox.ac.uk/section1/c174.htm (source: CBS 10673 only)",
            "original_text_license": ETCSL_LICENSE,
            "translation_source": f"{ETCSL_AUTHORS}, 1.7.4 'The Flood story: translation', https://etcsl.orinst.ox.ac.uk/section1/tr174.htm",
            "translation_license": ETCSL_LICENSE,
            "translator": "ETCSL (Black, Cunningham, Flückiger-Hawker, Robson, Taylor, Zólyomi)",
            "verified_date": TODAY,
        },
    }
    write_json(PUB / f"{TID}.json", entry)
    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-", "label": "Sumerian Flood Story (Eridu Genesis)",
            "group": "Mesopotamia", "date_sort": -1700,
            "author_name": "Sumerian scribes (Nippur tablet, c. 1800-1600 BCE)",
            "source_url": CDLI_PAGE,
            "critical_edition": "ETCSL 1.7.4 (from CBS 10673)",
            "translator_name": "ETCSL (Black et al., 1998-2006)",
            "original_lang_label": "Sumerian · ETCSL transliteration",
            "original_lang_code": "sux", "edition_label": "",
            "search_terms": "eridu genesis sumerian flood story ziusudra deluge nippur poebel",
            "description": "The Sumerian Flood story (Eridu Genesis) on its Nippur tablet: creation, the first cities, the flood and Ziusudra.",
        },
        "texts": [{
            "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "sumerian-scribes",
            "language": "Sumerian", "era": "Ancient Near East", "tradition": "sumerian", "category": "sacred-text",
            "date_approx": "c. 1800-1600 BCE (Old Babylonian tablet from Nippur)", "century": -17,
            "source": entry["source"], "description": entry["description"],
            "themes": ["flood", "eridu-genesis", "ziusudra", "creation", "sumer", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": scans["obverse"], "caption": "CBS 10673, obverse (columns i-iii)"},
                                {"file": scans["reverse"], "caption": "CBS 10673, reverse (columns iv-vi)"}]},
        }],
    }
    write_json(COLL, coll)
    print(f"wrote {TID}: {len(sections)} sections")


if __name__ == "__main__":
    main()
