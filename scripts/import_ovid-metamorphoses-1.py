#!/usr/bin/env python3
"""
import_ovid-metamorphoses-1.py: Ovid, Metamorphoses 1.1-415 (proem, creation, the four ages,
the giants, Lycaon, the flood, Deucalion and Pyrrha), on the 11th-century manuscript
Florence, Biblioteca Medicea Laurenziana, Plut. 36.12.

One entry; 27 sections, each a sense unit of the Latin (line ranges), linked to the
manuscript page(s) that carry its lines.

Chain of evidence
  1. MANUSCRIPT  Florence, Biblioteca Medicea Laurenziana, Plut. 36.12 ("Ovidii Metamorph"),
     parchment, 72 leaves, 140 x 275 mm, library dating 1001-1100. Teca digitale BML
     (CONTENTdm IIIF), manifest https://cdm21059.contentdm.oclc.org/iiif/2/plutei:671758/manifest.json.
     One column of verse, 55-63 lines a page; Met. 1.1-415 runs from fol. 1r to the top of fol. 4v.
     Fol. 1r (1.1-55) is abraded in its lower half, so for the sections on that page a second,
     legible witness is added: Vatican City, BAV, Urb. lat. 341 (Metamorphoses with commentary,
     Beneventan script, 11th-12th century), fol. 1v (1.1-37) and 2r (1.38-75),
     DigiVatLib IIIF https://digi.vatlib.it/iiif/MSS_Urb.lat.341/manifest.json.
  2. MAPPING  The first and last verse of every page used was read on the images (IIIF crops)
     and identified in Magnus' text; the words read are stored in PAGES below and quoted in
     each section's scan_note. A section is linked to every page whose span (first to last
     verse) contains one of its lines. No page was placed by counting or by text length.
  3. LATIN  Hugo Magnus, P. Ovidi Nasonis Metamorphoseon libri XV (Gotha: Perthes, 1892),
     Perseus canonical-latinLit phi0959.phi006.perseus-lat2 (CC BY-SA 4.0; edition public domain).
  4. ENGLISH  Brookes More, Ovid's Metamorphoses (Boston: Cornhill, 1922), blank verse,
     Perseus canonical-latinLit phi0959.phi006.perseus-eng3 (CC BY-SA 4.0 digital text;
     public domain in the US, published 1922). More's lines do not correspond one to one with
     Ovid's; each English section starts at the More line that begins the rendering of the
     first Latin line of the section (correspondences in SECTIONS, read by comparing the texts).

Usage:
    python3 scripts/import_ovid-metamorphoses-1.py           # build
    python3 scripts/import_ovid-metamorphoses-1.py --force   # re-download scans
"""

import argparse
import html as H
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

KEY = "ovid-metamorphoses-1"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/data/phi0959/phi006/phi0959.phi006.perseus-{ed}.xml"

BML_SVC = "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:"
BML_VIEW = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/"
BML_MANIFEST = "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:671758/manifest.json"
BML_LICENSE = ("Biblioteca Medicea Laurenziana, Teca digitale (access 'Pubblico'); su concessione del Ministero della Cultura; "
               "reproduced for non-commercial study with credit (Italian Code of Cultural Heritage, art. 108 c. 3-bis)")
BAV_SVC = "https://digi.vatlib.it/iiifimage/MSS_Urb.lat.341/"
BAV_MANIFEST = "https://digi.vatlib.it/iiif/MSS_Urb.lat.341/manifest.json"
BAV_LICENSE = ("(c) Biblioteca Apostolica Vaticana (copyright line printed on each image); DigiVatLib: free use for personal use or study; "
               "reproduced here for non-commercial scholarly use with credit")

# ---------------------------------------------------------------------------
# Pages read on the images: (ms, folio, IIIF id, first verse, last verse, first words, last words, extra)
# ---------------------------------------------------------------------------
PAGES = [
    ("L", "1r", "671608", 1, 55, "In nova fert animus mutatas dicere formas (under a faded red title)",
     "(iussit et humanas motura) tonitrua mentes",
     "The last line is abraded and only its end is legible; the line above it ends 'consistere nubes' (1.54). The lower half of this page is abraded and many verses are only partly legible."),
    ("L", "1v", "671609", 56, 118, "Et cum fulminibus facientes frigora ventos",
     "et breve ver spatiis exegit quattuor annum",
     "Line 1 reads 'frigora ventos' where Magnus prints 'fulgura ventos' (1.56)."),
    ("L", "2r", "671610", 119, 178, "Tum primum siccis aer fervoribus ustus",
     "celsior ipse loco sceptroque innixus eburno",
     "At 1.173 the manuscript reads 'a fronte potentes' where Magnus prints 'hac parte potentes'."),
    ("L", "2v", "671611", 179, 238, "Terrificam capitis concussit terque quaterque",
     "canities eadem est, eadem violentia vultus", ""),
    ("L", "3r", "671612", 239, 296, "(I)dem oculi lucent, eadem feritatis imago est",
     "navigat, hic piscem deprendit summa in ulmo",
     "The last line has the word order 'piscem deprendit summa in ulmo' (Magnus 'summa piscem deprendit in ulmo')."),
    ("L", "3v", "671613", 297, 354, "Figitur in viridi, si fors tulit, ancora prato",
     "terrarum, quascumque vident occasus et ortus", ""),
    ("L", "4r", "671614", 355, 412, "(N)os duo turba sumus, possidet cetera pontus",
     "missa viri manibus faciem traxere virorum", ""),
    ("L", "4v", "671615", 413, 415, "Et de femineo reparata est femina iactu",
     "et documenta damus qua simus origine nati (line 3)",
     "Lines 1-3 of the page are 1.413-415; line 4 begins the Python episode (1.416, 'Cetera diversis tellus animalia formis') with a large initial."),
    ("U", "1v", "Urb.lat.341_0010_fa_0001v.jp2", 1, 37, "In nova fert animus mutatas dicere formas (large initial I)",
     "Iussit et ambitae circumdare litora terrae", ""),
    ("U", "2r", "Urb.lat.341_0011_fa_0002r.jp2", 38, 75, "Addidit et fontes et stagna inmensa lacusque",
     "Terra feras cepit, volucres agitabilis aer", ""),
]
MS = {
    "L": {"short": "Laur. Plut. 36.12", "file": "laur36-12-f{f}.jpg", "svc": BML_SVC,
          "view": lambda p: BML_VIEW + p[2]},
    "U": {"short": "Vat. Urb. lat. 341", "file": "urb-lat-341-f{f}.jpg", "svc": BAV_SVC,
          "view": lambda p: f"https://digi.vatlib.it/view/MSS_Urb.lat.341/{p[2][12:16]}"},
}

# ---------------------------------------------------------------------------
# Sections: Latin lines (a-b), More's English lines (c-d), short label.
# ---------------------------------------------------------------------------
SECTIONS = [
    (1, 4, 1, 6, "proem"),
    (5, 20, 7, 27, "chaos"),
    (21, 31, 28, 40, "a god separates the elements"),
    (32, 51, 41, 68, "the earth shaped, the waters, the five zones"),
    (52, 68, 69, 92, "air, clouds, the four winds, the ether"),
    (69, 75, 93, 101, "the stars; living creatures fill each region"),
    (76, 88, 102, 119, "the making of man"),
    (89, 112, 120, 152, "the golden age"),
    (113, 124, 153, 165, "the silver age"),
    (125, 150, 166, 197, "the bronze and iron ages; Astraea leaves the earth"),
    (151, 162, 198, 215, "the giants"),
    (163, 167, 216, 223, "Jupiter remembers Lycaon's feast"),
    (168, 181, 224, 241, "the Milky Way and the council of the gods"),
    (182, 208, 242, 275, "Jupiter's speech; the gods' anger"),
    (209, 215, 276, 284, "Jupiter visits the earth"),
    (216, 239, 285, 315, "Lycaon's crime; he becomes a wolf"),
    (240, 243, 316, 321, "the whole race must perish"),
    (244, 252, 322, 332, "the gods ask who will worship them"),
    (253, 273, 333, 361, "fire set aside; the south wind brings the rain"),
    (274, 292, 362, 387, "Neptune and the rivers; land and sea become one"),
    (293, 312, 388, 412, "the world under the flood"),
    (313, 323, 413, 426, "Parnassus; Deucalion and Pyrrha"),
    (324, 347, 427, 458, "the waters withdraw"),
    (348, 366, 459, 479, "Deucalion's lament"),
    (367, 380, 480, 495, "prayer at the shrine of Themis"),
    (381, 394, 496, 512, "the oracle: the bones of the great mother"),
    (395, 415, 513, 533, "the stones become men and women"),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def cached(name, url):
    p = SRC / name
    if not p.exists():
        SRC.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url))
    return p


def get_scan(p, force):
    from PIL import Image
    ms, folio, sid = p[0], p[1], p[2]
    path = SCAN_DIR / MS[ms]["file"].format(f=folio)
    if path.exists() and not force:
        return path
    url = f"{MS[ms]['svc']}{sid}/full/1480,/0/default.jpg"
    Image.open(io.BytesIO(fetch(url))).convert("RGB").save(path, quality=85)
    return path


def book1_lines(ed):
    root = ET.parse(cached(f"phi0959.phi006.perseus-{ed}.xml", PERSEUS.format(ed=ed))).getroot()
    b = [d for d in root.iter(f"{TEI}div") if d.get("subtype") == "book" and d.get("n") == "1"][0]
    out = {}
    for l in b.iter(f"{TEI}l"):
        n = l.get("n")
        if n and n.isdigit():
            out[int(n)] = re.sub(r"\s+", " ", "".join(l.itertext())).strip()
    return out


def esc(t):
    return H.escape(t, quote=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cached("laur36-12-manifest.json", BML_MANIFEST)
    lat = book1_lines("lat2")
    eng = book1_lines("eng3")
    assert all(n in lat for n in range(1, 416))
    files = {(p[0], p[1]): get_scan(p, args.force) for p in PAGES}

    def page_note(p):
        s = (f"{MS[p[0]]['short']} fol. {p[1]} runs from '{p[5]}' on its first verse line (1.{p[3]}) "
             f"to '{p[6]}' on its last (1.{p[4]}).")
        if p[7]:
            s += " " + p[7]
        return s + " Viewer: " + MS[p[0]]["view"](p)

    sections, used = [], []
    for a, b, c, d, label in SECTIONS:
        pl = [p for p in PAGES if p[0] == "L" and p[3] <= b and p[4] >= a]
        pu = [p for p in PAGES if p[0] == "U" and a <= 55 and p[3] <= b and p[4] >= a]
        assert pl, (a, b)
        where = ", ".join(f"fol. {p[1]}" for p in pl)
        if len(pl) == 1:
            note = f"Lines 1.{a}-{b} are on {MS['L']['short']} fol. {pl[0][1]}. "
        else:
            note = (f"Lines 1.{a}-{b} start on {MS['L']['short']} fol. {pl[0][1]} and continue on fol. {pl[-1][1]} "
                    f"(page break inside this section). ")
        note += "Checked on the images: " + " ".join(page_note(p) for p in pl)
        if pu:
            note += (" Because fol. 1r of Laur. Plut. 36.12 is abraded, the same lines are also shown on "
                     + " and ".join(f"{MS['U']['short']} fol. {p[1]}" for p in pu) + ": " + " ".join(page_note(p) for p in pu))
        note += " The Latin shown is Magnus' critical text; the copyists' spelling and some words differ from it."
        pages = pl + pu
        for p in pages:
            if (p[0], p[1]) not in used:
                used.append((p[0], p[1]))
        sections.append({
            "section": f"1.{a}-{b}",
            "original_ref": f"Ovid, Metamorphoses 1.{a}-{b} ({label}); Laur. Plut. 36.12 {where}"
                            + (("; Urb. lat. 341 " + ", ".join(f"fol. {p[1]}" for p in pu)) if pu else ""),
            "original_text": "<p>" + "<br>\n".join(f"<sup>{n}</sup>{esc(lat[n])}" for n in range(a, b + 1)) + "</p>",
            "text": f"<p><sup>{a}</sup>" + "<br>\n".join(esc(eng[n]) for n in range(c, d + 1)) + "</p>",
            "scan_pages": [f"{KEY}/{files[(p[0], p[1])].name}" for p in pages],
            "scan_note": note,
        })
    # English coverage must be continuous
    for (_, _, c1, d1, _), (_, _, c2, _, _) in zip(SECTIONS, SECTIONS[1:]):
        assert c2 == d1 + 1, (d1, c2)

    tid = PREFIX + "creation-to-flood"
    title = "Ovid, Metamorphoses 1.1-415: creation, the four ages, Lycaon and the flood"
    desc = ("The opening of Ovid's Metamorphoses: the world made out of chaos, the making of man, the golden, silver, bronze and iron ages, "
            "the giants, Lycaon turned into a wolf, the great flood, and Deucalion and Pyrrha, who repeople the earth from stones. "
            "Shown on the 11th-century manuscript Laur. Plut. 36.12.")
    intro = (
        "<p>Ovid (43 BCE-17 CE) finished the fifteen books of the <em>Metamorphoses</em> around 8 CE, a poem of transformations that runs "
        "'from the first origin of the world to my own times'. Book 1 begins with creation: a mass called chaos, in which hot fought with cold and wet with dry, "
        "is set in order by 'a god, or a kinder nature'; the elements take their places, the earth is shaped, and finally man is made, 'a creature more holy, "
        "more able to take in high thoughts', perhaps from divine seed, perhaps by Prometheus from earth and rain water, and given an upright face to look at the stars. "
        "There follow the four ages of mankind, from the golden age without laws or labour to the iron age of greed and war, when Justice (Astraea) leaves the earth; "
        "the war of the giants; and the crime of Lycaon, king of Arcadia, who tests Jupiter by serving him human flesh and is turned into a wolf. "
        "Jupiter resolves to destroy the human race by water. The flood covers everything except the two peaks of Parnassus, where a small boat brings Deucalion and Pyrrha, "
        "the most just man and the most god-fearing woman. When the waters withdraw, the oracle of Themis tells them to throw behind them 'the bones of the great mother'; "
        "they understand the stones of the earth, and the stones become men and women.</p>\n\n"
        "<p>The pages shown are from Florence, Biblioteca Medicea Laurenziana, Plut. 36.12, a small manuscript of the poem dated by the library to the 11th century, "
        "one of the oldest surviving copies of book 1. It is written in one column of 55 to 63 verses a page, and 1.1-415 runs from fol. 1r to the top of fol. 4v. "
        "The first page (fol. 1r, lines 1-55) is badly abraded in its lower half, so the sections on it also show the same lines on a second early manuscript, "
        "Vatican City, Biblioteca Apostolica Vaticana, Urb. lat. 341 (fol. 1v-2r), written in Beneventan script in southern Italy in the 11th or 12th century. "
        "Each section below is a group of lines; the page or pages listed for it were identified by reading the first and last verse of every page on the images. "
        "The Latin is Hugo Magnus' edition (1892), not a transcription of the manuscript; where the copyist's reading was noticed to differ, the scan note says so. "
        "The English is Brookes More's blank-verse translation (1922). The passage is complete.</p>"
    )
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Latin (Magnus) / English (Brookes More, 1922)",
        "source": "Florence, Laur. Plut. 36.12 fol. 1r-4v (Teca digitale BML) with Vat. Urb. lat. 341 fol. 1v-2r (DigiVatLib) + Magnus Latin (Perseus) + Brookes More English (Perseus)",
        "description": desc,
        "introduction": intro,
        "translator_notes": [
            "Latin: Hugo Magnus, P. Ovidi Nasonis Metamorphoseon libri XV (Gotha, 1892), Perseus digital text; line numbers are Magnus'.",
            "English: Brookes More, Ovid's Metamorphoses (Boston: Cornhill, 1922), Perseus digital text. More's blank verse has more lines than the Latin; "
            "each English section begins where More begins the first Latin line of the section, so a phrase can fall on the neighbouring side of a break "
            "(for example, More's 'and they wept', for 'Dixerat, et flebant' at 1.367, ends the section 1.348-366).",
        ],
        "translation": sections,
        "verification": {
            "scan_source": (f"Biblioteca Medicea Laurenziana, Teca digitale (CONTENTdm), Plut. 36.12, IIIF manifest {BML_MANIFEST} "
                            f"(fol. 1r-4v = canvases 9-16); Biblioteca Apostolica Vaticana, DigiVatLib, Urb. lat. 341, IIIF manifest {BAV_MANIFEST} (fol. 1v-2r)"),
            "scan_license": f"Laur. Plut. 36.12: {BML_LICENSE}. Urb. lat. 341: {BAV_LICENSE}",
            "scan_manuscript": ("Florence, Biblioteca Medicea Laurenziana, Plut. 36.12: Ovid, Metamorphoses; parchment, 72 leaves, 140 x 275 mm, "
                                "library dating 1001-1100; one column. Second witness for 1.1-75: Vatican City, BAV, Urb. lat. 341, Ovid, Metamorphoses "
                                "with commentary (fol. 1v-182r), Beneventan script of southern Italy, 11th-12th century"),
            "scan_mapping": "Own visual check: the first and last verse of every page used (Laur. Plut. 36.12 fol. 1r-4v; Urb. lat. 341 fol. 1v-2r) were read on IIIF crops and identified in Magnus' text (words recorded in each scan_note)",
            "scan_mapping_urls": [BML_MANIFEST, BAV_MANIFEST, "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/671758"]
                                 + [MS[p[0]]["view"](p) for p in PAGES],
            "scan_local_paths": [f"{KEY}/{files[k].name}" for k in used],
            "original_text_source": f"Hugo Magnus, P. Ovidi Nasonis Metamorphoseon libri XV (Gotha: F. A. Perthes, 1892), Perseus canonical-latinLit phi0959.phi006.perseus-lat2 ({PERSEUS.format(ed='lat2')})",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": f"Brookes More, Ovid's Metamorphoses (Boston: Cornhill Publishing Co., 1922), Perseus canonical-latinLit phi0959.phi006.perseus-eng3 ({PERSEUS.format(ed='eng3')})",
            "translation_license": "public domain in the US (published 1922); Perseus digital text CC BY-SA 4.0",
            "translator": "Brookes More (1922)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": 1, "title": title, "author_id": "ovid",
        "language": "Latin", "era": "Imperial", "tradition": "roman", "category": "literature",
        "date_approx": "c. 8 CE (composition); manuscript 11th century",
        "century": 1, "source": entry["source"], "description": desc,
        "themes": ["ovid", "metamorphoses", "creation", "chaos", "making-of-man", "four-ages", "golden-age", "giants",
                   "lycaon", "flood", "deluge", "deucalion", "pyrrha", "prometheus", "earliest-ages", "latin", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[k].name}", "caption": f"{MS[k[0]]['short']} fol. {k[1]}"} for k in used]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Ovid: Metamorphoses, book 1",
            "group": "Rome",
            "date_sort": 8,
            "author_name": "Ovid (43 BCE-17 CE); Laurenziana manuscript of the 11th century",
            "source_url": "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/671758",
            "critical_edition": "Magnus, Metamorphoses (1892), via Perseus",
            "translator_name": "Brookes More (1922)",
            "original_lang_label": "Latin · Magnus",
            "original_lang_code": "la",
            "edition_label": "",
            "search_terms": "ovid metamorphoses creation chaos four ages golden age iron age giants lycaon wolf flood deluge deucalion pyrrha parnassus themis stones prometheus",
            "description": "The first book of Ovid's Metamorphoses, from chaos and the making of man through the four ages to the flood and Deucalion and Pyrrha, on an 11th-century manuscript.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections, {len(used)} images)")


if __name__ == "__main__":
    main()
