#!/usr/bin/env python3
"""
import_proto_cuneiform.py -- proto-cuneiform administrative tablets (Uruk III period,
c. 3200-3000 BCE), among the earliest written documents: six tablets that have a CDLI
photograph, a CDLI transliteration and a CDLI English translation.

Chain of evidence
-----------------
1. SCAN      CDLI photograph of each tablet (https://cdli.earth/dl/photo/P......jpg), whole
             tablet (fat-cross: obverse above, reverse below, edges beside), long side <= 2600 px,
             never upscaled.  Each photo was looked at: it shows the tablet itself with the
             surfaces the transliteration names (MSVO 3, 29 has a blank reverse, as CDLI records).
             CDLI terms: non-commercial use; copyright the holding institution (Ashmolean Museum,
             Iraq Museum, ISAC Museum Chicago, Schøyen Collection).
2. ORIGINAL  CDLI transliteration (ATF, language qpc = proto-cuneiform) of each tablet: numerals
             in the N-sign system (e.g. 4(N14) = four of sign N14) and sign names; ASCII sz shown
             as š.  Nothing else is changed.
3. ENGLISH   The CDLI translation lines (#tr.en) of the same ATF, one per transliteration line.
             CDLI terms: transliterations and translations may be freely copied and re-used
             according to common academic practice, with reference to CDLI.  Explanatory comments
             in the ATF ('# calculation: ...') are kept as notes, not as translation.
MAPPING      Sections are the tablet's own surfaces and columns as given in the ATF; each section
             points at the photograph of that tablet.

Usage:  python3 scripts/import_proto_cuneiform.py
"""
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "proto-cuneiform"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"
CDLI_IMG_LICENSE = ("CDLI terms of use (https://cdli.earth/terms-of-use): images are for the non-commercial use of "
                    "students, scholars and the public; copyright the institution that owns the object")
CDLI_TXT_LICENSE = ("CDLI terms of use: transliterations and translations may be freely copied and re-used according to "
                    "common academic practice, with reference to CDLI (https://cdli.earth)")

TABLETS = [
    {"p": "P005340", "slug": "msvo-3-29-kushim", "order": 1,
     "title": "Proto-cuneiform barley account of Kushim (MSVO 3, 29)",
     "what": "an account of barley over 37 months, closed with the sign group read KU ŠIM, often taken as the name or title "
             "of the official responsible (Kushim). The CDLI translation reads: '5617 1/5 N1's, exchange barley, 37 months, "
             "Kushim's final account'. It is one of the best-known of the earliest written documents."},
    {"p": "P005068", "slug": "msvo-1-1", "order": 2,
     "title": "Proto-cuneiform field account from Jemdet Nasr (MSVO 1, 1)",
     "what": "a survey of fields in barley, fields assigned to laborers and irrigated fields belonging to officials of the "
             "settlement NI.RU (Jemdet Nasr): the chief exchange agent, the equid herder, the chief justice, the wife of the "
             "lord and the priest of NI.RU, with totals on the reverse."},
    {"p": "P005069", "slug": "msvo-1-2", "order": 3,
     "title": "Proto-cuneiform field measurements from Jemdet Nasr (MSVO 1, 2)",
     "what": "a record of the length and width of fields of the same officials and the area calculated from them."},
    {"p": "P005070", "slug": "msvo-1-3", "order": 4,
     # QC 2026-11-12: the ink number on the tablet's left edge in the CDLI photograph reads 1924.577 (an open 4,
     # unlike the looped 6 of '1926.561' on MSVO 1, 1); CDLI catalogues the tablet as Ashm 1926-0577.  The number
     # written on the object is used.
     "museum": "Ashm 1924-0577",
     "museum_note": ("The museum number is given as written in ink on the tablet's left edge in the photograph, "
                     "1924.577; CDLI's catalogue lists the tablet (MSVO 1, 3 = OECT 7, 83) as Ashm 1926-0577."),
     "title": "Proto-cuneiform field measurements from Jemdet Nasr (MSVO 1, 3)",
     "what": "a record of the length, width and area of the fields of officials (the wife of the lord, the equid herder, "
             "the chief trade agent, the priest and the chief justice), with totals on the reverse."},
    {"p": "P005071", "slug": "msvo-1-4", "order": 5,
     "title": "Proto-cuneiform field measurements from Jemdet Nasr (MSVO 1, 4)",
     "what": "a record of the length, width and area of the fields of officials (the chief exchange agent, the equid herder, "
             "the chief justice and others), with totals on the reverse, including the field of the lord."},
    {"p": "P005077", "slug": "msvo-1-10", "order": 6,
     "title": "Proto-cuneiform barley and field account from Jemdet Nasr (MSVO 1, 10)",
     "what": "a short account of 150 units of barley for a field of 10 bur, recorded by the pigsty accountant."},
]


def fetch(url, name, binary=False):
    SRC.mkdir(parents=True, exist_ok=True)
    p = SRC / name
    if not p.exists() or p.stat().st_size == 0:
        subprocess.run(["curl", "-s", "-L", "-m", "300", "-A", UA, "-o", str(p), url], check=True)
    return p.read_bytes() if binary else p.read_text(encoding="utf-8", errors="replace")


def pc_html(s):
    s = s.replace("($blank space$)", "(blank space)").replace("sz", "š").replace("SZ", "Š")
    return html.escape(s.strip(), quote=False)


def parse(atf):
    """[{place, line, atf, tr, notes}] in ATF order."""
    out, surf, col, cur = [], "obverse", "", None
    for raw in atf.split("\n"):
        ln = raw.rstrip()
        if ln.startswith("@"):
            t = ln[1:].split()
            if t and t[0] in ("obverse", "reverse"):
                surf, col = t[0], ""
            elif t and t[0] in ("left", "right", "top", "bottom", "edge"):
                surf, col = f"{t[0]} edge" if t[0] != "edge" else "edge", ""
            elif t and t[0] == "column":
                col = t[1]
            continue
        m = re.match(r"^(\d+(?:\.[a-z]\d*)?)\.\s(.*)$", ln)
        if m:
            cur = {"place": f"{surf}, column {col}" if col else surf, "line": m.group(1), "atf": m.group(2),
                   "tr": "", "notes": []}
            out.append(cur)
            continue
        if ln.startswith("#tr.en:") and cur is not None:
            cur["tr"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("# ") and cur is not None:
            cur["notes"].append(ln[2:].strip())
    return out


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for t in TABLETS:
        p, n = t["p"], int(t["p"][1:])
        meta = json.loads(fetch(f"https://cdli.earth/artifacts/{n}/json", f"{p}.json"))
        meta = meta[0] if isinstance(meta, list) else meta
        page = fetch(f"https://cdli.earth/artifacts/{n}", f"{p}.html")
        ins = re.findall(r'href="/inscriptions/(\d+)/atf"', page)
        atf = fetch(f"https://cdli.earth/inscriptions/{ins[0]}/atf", f"{p}.atf")
        fetch(f"https://cdli.earth/dl/photo/{p}.jpg", f"{p}.jpg", binary=True)
        im = Image.open(SRC / f"{p}.jpg").convert("RGB")
        if max(im.size) > 2600:
            im.thumbnail((2600, 2600), Image.LANCZOS)
        out = SCAN_DIR / f"{t['slug']}.jpg"
        im.save(out, quality=88)
        scan = f"{KEY}/{out.name}"
        lines = parse(atf)
        assert lines and all(ln["tr"] for ln in lines), p
        museum = t.get("museum") or meta.get("museum_no")
        designation = meta.get("designation")
        coll = ", ".join(c["collection"]["collection"] for c in meta.get("collections", []))
        prov = meta.get("provenience")
        prov = prov.get("provenience") if isinstance(prov, dict) else (prov or "")
        site = "Uruk" if prov.startswith("Uruk") else "Jemdet Nasr"
        prov_note = ("Uruk" if site == "Uruk" else
                     "Jemdet Nasr (CDLI catalogues the provenience as uncertain, attributed to Jemdet Nasr)")
        sections, notes = [], []
        places = []
        for ln in lines:
            if ln["place"] not in places:
                places.append(ln["place"])
        for pl in places:
            ls = [ln for ln in lines if ln["place"] == pl]
            orig = "<br>\n".join(f"<sup>{ln['line']}</sup>{pc_html(ln['atf'])}" for ln in ls)
            eng = "<br>\n".join(f"<sup>{ln['line']}</sup>{html.escape(ln['tr'], quote=False)}" for ln in ls)
            for ln in ls:
                for nt in ln["notes"]:
                    notes.append(f"{pl}, line {ln['line']}: {nt}")
            sid = pl.replace("obverse", "obv").replace("reverse", "rev").replace(", column ", " ")
            sections.append({
                "section": sid,
                "original_ref": f"{designation} ({museum}), {pl}, lines {ls[0]['line']}-{ls[-1]['line']}",
                "original_text": orig,
                "text": f"<p>{eng}</p>",
                "scan_pages": [scan],
                "scan_note": (f"{designation} ({museum}), {pl}. The photograph shows the whole tablet (obverse above, reverse below, "
                              "edges beside); face and column as given in the CDLI transliteration, checked by eye on the photograph."
                              + (" On the reverse the columns run from right to left: column 1 is the right-hand column."
                                 if pl.startswith("reverse, column") else "")
                              + (" " + t["museum_note"] if t.get("museum_note") else "")),
            })
        tid = f"verified-{KEY}-{t['slug']}"
        intro = (
            f"<p>This clay tablet ({museum}, {coll}) is a proto-cuneiform document of the Uruk III period, about 3200-3000 BCE, "
            f"from {prov_note}. It is {t['what']}</p>"
            "<p>Proto-cuneiform is the earliest stage of cuneiform writing, used for bookkeeping in southern Mesopotamia. It records "
            "numbers in several counting systems (shown in the transliteration as signs N01, N14, N34 and so on) together with "
            "signs for goods, offices and places. It does not yet write full sentences, so the English is an interpretation of the "
            "entries rather than a translation of connected language.</p>"
            "<p>The sections follow the faces and columns of the tablet. The transliteration and the English are CDLI's, line by line "
            "with the same line numbers.</p>"
            + (f"<p>{t['museum_note']}</p>" if t.get("museum_note") else "")
        )
        entry = {
            "id": tid, "slug": tid, "title": t["title"],
            "language": "Proto-cuneiform (transliteration) / English",
            "source": f"{museum} photograph, transliteration and English translation via CDLI ({p})",
            "description": f"{t['title'].split(' (')[0]}: a clay tablet from {site} of about 3200-3000 BCE, among the earliest written documents, with CDLI's transliteration and English.",
            "introduction": intro,
            "translator_notes": [
                "Transliteration: CDLI ATF (proto-cuneiform). Numerals are written as counts of numeral signs, e.g. 4(N14) = four N14 signs; ~a, ~b mark sign variants; [ ] broken, # damaged; sz is shown as š.",
                "English: CDLI's line-by-line translation (#tr.en lines of the ATF).",
            ] + ([f"CDLI notes: {'; '.join(notes)}"] if notes else []),
            "translation": sections,
            "verification": {
                "scan_source": f"CDLI photograph https://cdli.earth/dl/photo/{p}.jpg (artifact page https://cdli.earth/artifacts/{n})",
                "scan_license": f"{coll}; {CDLI_IMG_LICENSE}",
                "scan_manuscript": f"{museum} ({designation}), clay tablet, {prov_note}, Uruk III period (c. 3200-3000 BCE)",
                "scan_mapping": "Faces and columns from the CDLI transliteration; one photograph shows the whole tablet; checked by eye",
                "scan_mapping_urls": [f"https://cdli.earth/artifacts/{n}"],
                "scan_local_paths": [scan],
                "original_text_source": f"CDLI transliteration of {p} (https://cdli.earth/inscriptions/{ins[0]}/atf)",
                "original_text_license": CDLI_TXT_LICENSE,
                "translation_source": f"CDLI English translation lines of {p} (https://cdli.earth/artifacts/{n})",
                "translation_license": CDLI_TXT_LICENSE,
                "translator": "CDLI (cdli.earth)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": t["order"], "title": t["title"], "author_id": "proto-cuneiform-scribes",
            "language": "Proto-cuneiform", "era": "Ancient Near East", "tradition": "sumerian", "category": "inscription",
            "date_approx": "c. 3200-3000 BCE (Uruk III period)", "century": -31,
            "source": entry["source"], "description": entry["description"],
            "themes": ["proto-cuneiform", "earliest-writing", "accounting", site.lower().replace(" ", "-"), "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": scan, "caption": f"{designation} ({museum})"}]},
        })
        print(f"wrote {tid}: {len(sections)} sections")
    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-", "label": "Proto-cuneiform tablets",
            "group": "Earliest Writing", "date_sort": -3100,
            "author_name": "Scribes of Uruk and Jemdet Nasr (c. 3200-3000 BCE)",
            "source_url": "https://cdli.earth/artifacts/5340",
            "critical_edition": "CDLI transliterations (MSVO 1 and MSVO 3 texts)",
            "translator_name": "CDLI",
            "original_lang_label": "Proto-cuneiform · CDLI transliteration",
            "original_lang_code": "sux", "edition_label": "",
            "search_terms": "proto-cuneiform earliest writing uruk jemdet nasr kushim accounting tablet",
            "description": "Some of the earliest written documents: proto-cuneiform account tablets from Uruk and Jemdet Nasr, about 3200-3000 BCE.",
        },
        "texts": rows,
        "authors": [{
            "id": "proto-cuneiform-scribes", "name": "Proto-cuneiform scribes (anonymous)", "dates": "c. 3300-3000 BCE",
            "century": -31, "era": "Ancient Near East", "tradition": "sumerian", "language": "Proto-cuneiform",
            "bio": "The administrators of Uruk and neighbouring towns who kept the first written records, accounts of grain, fields, animals and labor, on clay tablets.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
