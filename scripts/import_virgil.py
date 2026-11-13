#!/usr/bin/env python3
"""
import_virgil.py: Virgil, Eclogue 4 (the golden age returns) on the Vergilius Romanus, and
Aeneid 6.724-751 (the world-soul, the purification and the return of souls) on the
Vergilius Vaticanus. Two entries; every section linked to the manuscript page(s) that carry it.

Chain of evidence
  1. MANUSCRIPTS  Vatican City, Biblioteca Apostolica Vaticana (DigiVatLib IIIF):
     - Vat. lat. 3867, the Vergilius Romanus, 5th century, rustic capitals, 18 lines a page,
       with miniatures; manifest https://digi.vatlib.it/iiif/MSS_Vat.lat.3867/manifest.json.
       Eclogue 4 runs from fol. 9v (red title SAECULI NOVI INTERPRETATIO) to fol. 11r, where it
       ends above a miniature.
     - Vat. lat. 3225, the Vergilius Vaticanus, BAV dating 4th century, rustic capitals, 21 lines a
       page, fragments of the Georgics and Aeneid; manifest
       https://digi.vatlib.it/iiif/MSS_Vat.lat.3225/manifest.json. The BAV catalogue lists for
       Aeneid 6 the lines 589-755 among the surviving fragments; 6.719-739 are on fol. 55r and
       6.740-755 on fol. 55v.
  2. MAPPING  The first and last verse of every page used (and the position of 6.724 on fol. 55r)
     were read on the images (IIIF crops); capitals, so every word is legible. The words read
     are stored in PAGES and quoted in each scan_note. No page was placed by counting.
  3. LATIN  J. B. Greenough, The Bucolics, Aeneid, and Georgics of Virgil (Boston: Ginn, 1881 / 1900),
     Perseus canonical-latinLit phi0690.phi001.perseus-lat2 and phi0690.phi003.perseus-lat2
     (CC BY-SA 4.0; edition public domain).
  4. ENGLISH  Public domain in the US, Perseus digital texts (CC BY-SA 4.0):
     Eclogue 4: James Rhoades, The Poems of Vergil (Oxford University Press, 1921), phi0690.phi001.perseus-eng2.
     Aeneid: Theodore C. Williams, The Aeneid of Virgil (Boston: Houghton Mifflin, 1910), phi0690.phi003.perseus-eng2.
     Both are verse translations with more lines than the Latin and their own line numbers;
     each English section starts at the translator's line that begins the rendering of the
     first Latin line of the section (correspondences in SECTIONS, read by comparing the texts).

Usage:
    python3 scripts/import_virgil.py           # build
    python3 scripts/import_virgil.py --force   # re-download scans
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

KEY = "virgil"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"
PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/data/phi0690/{w}/phi0690.{w}.perseus-{ed}.xml"
BAV_LICENSE = ("(c) Biblioteca Apostolica Vaticana (copyright line printed on each image); DigiVatLib: free use for personal use or study; "
               "reproduced here for non-commercial scholarly use with credit")

MSS = {
    "romanus": {
        "shelf": "Vat. lat. 3867", "name": "Vergilius Romanus",
        "svc": "https://digi.vatlib.it/iiifimage/MSS_Vat.lat.3867/Vat.lat.3867_{id}.jp2",
        "view": "https://digi.vatlib.it/view/MSS_Vat.lat.3867/{seq}",
        "manifest": "https://digi.vatlib.it/iiif/MSS_Vat.lat.3867/manifest.json",
        "file": "vat-lat-3867-f{f}.jpg", "width": 1800,
        "desc": "Vatican City, Biblioteca Apostolica Vaticana, Vat. lat. 3867 (Vergilius Romanus), parchment, 5th century, rustic capitals, 18 lines a page, with miniatures; Eclogues, Georgics and Aeneid with losses",
    },
    "vaticanus": {
        "shelf": "Vat. lat. 3225", "name": "Vergilius Vaticanus",
        "svc": "https://digi.vatlib.it/iiifimage/MSS_Vat.lat.3225/Vat.lat.3225_{id}.jp2",
        "view": "https://digi.vatlib.it/view/MSS_Vat.lat.3225/{seq}",
        "manifest": "https://digi.vatlib.it/iiif/MSS_Vat.lat.3225/manifest.json",
        "file": "vat-lat-3225-f{f}.jpg", "width": 1780,
        "desc": "Vatican City, Biblioteca Apostolica Vaticana, Vat. lat. 3225 (Vergilius Vaticanus), parchment, BAV dating 4th century (commonly dated around 400), rustic capitals, 21 lines a page, with miniatures; 76 leaves of fragments of the Georgics and Aeneid",
    },
}

# (ms, folio, image id, first line, last line, first words, last words, extra)
PAGES = [
    ("romanus", "9v", "0020_fa_0009v", 1, 17, "Sicelides Musae, paulo maiora canamus (under the red title SAECULI NOVI INTERPRETATIO)",
     "pacatumque reget patriis virtutibus orbem", "The speaker mark POE stands in red in the left margin of the first line."),
    ("romanus", "10r", "0021_fa_0010r", 18, 35, "At tibi prima, puer, nullo munuscula cultu",
     "delectos heroas; erunt etiam altera bella", ""),
    ("romanus", "10v", "0022_fa_0010v", 36, 53, "atque iterum ad Troiam magnus mittetur Achilles",
     "o mihi tum longae maneat pars ultima vitae", "The last line reads TUM where Greenough prints 'tam' (4.53)."),
    ("romanus", "11r", "0023_fa_0011r", 54, 63, "spiritus et quantum sat erit tua dicere facta",
     "nec deus hunc mensa, dea nec dignata cubili est",
     "The ten lines of text fill the upper part of the page; a framed miniature follows below them."),
    ("vaticanus", "55r", "0113_fr_0055r", 719, 739, "O pater, anne aliquas ad caelum hinc ire putandum (est)",
     "ergo exercentur poenis, veterumque malorum",
     "6.724 'Principio caelum ac terras camposque liquentis' is the sixth line of the page."),
    ("vaticanus", "55v", "0114_fr_0055v", 740, 755, "supplicia expendunt: aliae panduntur inanes",
     "adversos legere et venientum discere vultus",
     "6.751 'rursus et incipiant in corpora velle reverti' is the twelfth line; the page ends with 6.755, followed by a gap in the manuscript."),
]

ENTRIES = [
    {
        "slug": "eclogue-4", "order": 1, "work": "phi001", "unit": "4", "ms": "romanus", "ref": "Eclogue 4",
        "title": "Virgil, Eclogue 4: the return of the golden age",
        "translator": "James Rhoades (1921)",
        "translation_source": "James Rhoades, The Poems of Vergil (London: Oxford University Press, 1921), Perseus canonical-latinLit phi0690.phi001.perseus-eng2",
        "era": "Late Republic", "century": -1, "date_approx": "c. 40 BCE (composition); manuscript 5th century",
        "description": ("Virgil's fourth Eclogue, written around 40 BCE: the last age foretold by the Sibyl has come, the Virgin returns and a new race "
                        "is sent down from heaven, and a child is born under whom the iron age will end and the golden age return. Shown on the Vergilius Romanus (5th century)."),
        "themes": ["virgil", "eclogues", "fourth-eclogue", "golden-age", "ages-of-man", "sibyl", "messianic-eclogue", "earliest-ages", "latin", "verified"],
        "intro": (
            "<p>The fourth of Virgil's ten Eclogues (pastoral poems) is addressed to Asinius Pollio, consul in 40 BCE. It announces that "
            "'the last age of the Cumaean song' has come: the great order of the centuries is born anew, the Virgin (Justice) returns, Saturn's reign returns, "
            "and 'a new race is sent down from high heaven'. A boy is about to be born under whom 'the iron race shall cease and a golden race arise throughout the world'; "
            "he will receive the life of the gods and see heroes mingled with gods. As he grows, the earth will give its fruits untilled, "
            "though some traces of the old wrong will remain for a time (a second Argo, a second Trojan war), until all lands bear all things. "
            "From late antiquity Christian readers, among them Constantine and Augustine, read the poem as a prophecy of Christ.</p>\n\n"
            "<p>The pages shown are from Vatican City, Biblioteca Apostolica Vaticana, Vat. lat. 3867, the Vergilius Romanus, one of the oldest surviving books of Virgil, "
            "written in rustic capitals in the 5th century. Here the poem carries the red title SAECULI NOVI INTERPRETATIO ('interpretation of the new age') "
            "and fills four pages: fol. 9v (lines 1-17), 10r (18-35), 10v (36-53) and 11r (54-63), where a miniature follows. "
            "Each section below is a group of lines; the pages were identified by reading the first and last line of each page on the images. "
            "The Latin is Greenough's edition (Perseus), not a transcription of the manuscript; at line 53 the manuscript has <em>tum</em> where Greenough prints <em>tam</em>. "
            "The English is James Rhoades' verse translation. The poem is complete.</p>"
        ),
        "sections": [  # (latin a, b, english a, b, label)
            (1, 3, 1, 4, "the Sicilian Muses sing a greater theme"),
            (4, 10, 5, 12, "the last age of the Sibyl's song; the Virgin returns; a new race from heaven"),
            (11, 17, 13, 21, "Pollio's consulship; the child will share the life of the gods"),
            (18, 25, 22, 32, "the earth's first gifts to the child"),
            (26, 30, 33, 38, "as the child grows, the fields turn golden"),
            (31, 36, 39, 46, "traces of the old wrong: a second Argo, a second Achilles"),
            (37, 45, 47, 57, "when he is a man, every land will bear all things"),
            (46, 47, 58, 60, "the Fates' song"),
            (48, 52, 61, 65, "the whole world rejoices at the coming age"),
            (53, 59, 66, 74, "the poet's wish to sing the child's deeds"),
            (60, 63, 75, 79, "begin, little boy, to know your mother with a smile"),
        ],
    },
    {
        "slug": "aeneid-6-724-751", "order": 2, "work": "phi003", "unit": "6", "ms": "vaticanus", "ref": "Aeneid 6",
        "title": "Virgil, Aeneid 6.724-751: Anchises on the world-soul and the return of souls",
        "translator": "Theodore C. Williams (1910)",
        "translation_source": "Theodore C. Williams, The Aeneid of Virgil (Boston: Houghton Mifflin, 1910), Perseus canonical-latinLit phi0690.phi003.perseus-eng2",
        "era": "Imperial", "century": -1, "date_approx": "29-19 BCE (composition); manuscript c. 400 (BAV: 4th century)",
        "description": ("In the underworld Anchises explains to Aeneas that one spirit and mind move the whole universe, that souls have a fiery heavenly origin dulled by the body, "
                        "and that after purification they drink of Lethe and return to bodies. Shown on the Vergilius Vaticanus (about 400)."),
        "themes": ["virgil", "aeneid", "underworld", "anchises", "world-soul", "spiritus-intus-alit", "purification", "reincarnation", "lethe", "elysium", "theosis", "latin", "verified"],
        "intro": (
            "<p>In book 6 of the <em>Aeneid</em> Aeneas goes down to the underworld with the Sibyl of Cumae and finds his father Anchises in Elysium, beside the river Lethe, "
            "where crowds of souls wait. Asked why souls would ever wish to return to bodies, Anchises explains: 'a spirit within nourishes' heaven, earth, sea, moon and stars, "
            "and 'mind, poured through the limbs, moves the whole mass and mingles with the great body' (<em>spiritus intus alit ... mens agitat molem</em>, 726-727). "
            "Men and animals have in their seeds 'a fiery force and a heavenly origin', dulled by the earthly body; hence fear and desire, grief and joy. "
            "Even after death the stains of the body remain, so souls are purified by wind, water or fire; a few remain in Elysium until the long cycle of time "
            "has removed every stain and left 'the pure ethereal sense and the fire of simple air'. The rest, after a thousand years, are called to Lethe, "
            "forget, and begin to wish to return to bodies.</p>\n\n"
            "<p>The pages shown are from Vatican City, Biblioteca Apostolica Vaticana, Vat. lat. 3225, the Vergilius Vaticanus, the oldest illustrated manuscript of Virgil, "
            "written in rustic capitals around 400 (the library dates it to the 4th century). Only 76 leaves survive; this passage is among them. "
            "Lines 724-739 stand on fol. 55r (line 724 is its sixth line) and 740-751 on fol. 55v. "
            "The Latin is Greenough's edition (Perseus), not a transcription of the manuscript. The English is Theodore C. Williams' verse translation (1910).</p>"
        ),
        # English cut at the end of Williams' sentences (QC fix 2026-11-12). His sentence "Thence man and beast ...
        # the radiant world." renders 728-734 and runs across the 732/733 break; it is given whole with 724-732.
        # His line 966 holds the end of 742 and the start of 743 ("Or burned away in fire. Each man receives"):
        # it is divided at the full stop (ENG_LINE_SPLITS).
        "sections": [
            (724, 732, 942, 956, "one spirit and mind move the universe; the fiery seed of souls"),
            (733, 742, 957, 966, "the body's darkness; purification after death"),
            (743, 751, 966, 977, "Elysium; after a thousand years the souls drink of Lethe and return"),
        ],
        "english_notes": {
            "724-732": ("English: Williams' lines 942-956, which render Latin 724-734. His sentence for 728-734 (Thence man and beast ... "
                        "on the radiant world.) runs across the break after 732 and is given whole here, so the English of 733-734 "
                        "(whence also spring / Terrors and passions ... the radiant world.) stands in this section and the next "
                        "section's English begins with 735."),
            "733-742": ("English: Williams' lines 957-966 (to the full stop in 966), which render Latin 735-742; the English of 733-734 "
                        "ends the sentence given with the previous section (see there). His line 966 ends this section at "
                        "Or burned away in fire. (aut exuritur igni, 742)."),
            "743-751": ("English: Williams' lines 966 (from Each man receives) to 977, which render Latin 743-751, the same lines as the "
                        "Latin."),
        },
        "english_from": {"724-732": 724, "733-742": 735, "743-751": 743},
    },
]


# A translator's verse line that holds the end of one Latin sentence and the start of the next is divided
# at the full stop: the text before goes with the section that ends with that line, the rest with the next.
ENG_LINE_SPLITS = {
    (("phi003", "6"), 966): "Or burned away in fire.",
}


# The Perseus file of Rhoades lowercases three line-initial words that are capitalised in print
# (a proper noun twice and the vocative O); they are restored here and the restoration is noted.
CAPS_FIXES = {
    (("phi001", "4"), 1): ("muses", "Muses"),
    (("phi001", "4"), 13): ("apollo", "Apollo"),
    (("phi001", "4"), 76): ("o baby-boy", "O baby-boy"),
}


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
    m = MSS[p[0]]
    path = SCAN_DIR / m["file"].format(f=p[1])
    if path.exists() and not force:
        return path
    url = m["svc"].format(id=p[2]) + f"/full/{m['width']},/0/default.jpg"
    Image.open(io.BytesIO(fetch(url))).convert("RGB").save(path, quality=85)
    return path


def lines(work, ed, unit):
    root = ET.parse(cached(f"phi0690.{work}.perseus-{ed}.xml", PERSEUS.format(w=work, ed=ed))).getroot()
    div = [d for d in root.iter(f"{TEI}div") if d.get("n") == unit and d.get("subtype") in ("poem", "book")][0]
    out = {}
    for l in div.iter(f"{TEI}l"):
        n = l.get("n")
        if n and n.isdigit():
            out[int(n)] = re.sub(r"\s+", " ", "".join(l.itertext())).strip()
    return out


def esc(t):
    return H.escape(t, quote=False)


def viewer(p):
    return MSS[p[0]]["view"].format(seq=p[2][:4])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for m in MSS.values():
        cached(m["manifest"].rsplit("/", 2)[1] + "-manifest.json", m["manifest"])
    files = {(p[0], p[1]): get_scan(p, args.force) for p in PAGES}
    rows = []
    for E in ENTRIES:
        ms = MSS[E["ms"]]
        lat = lines(E["work"], "lat2", E["unit"])
        eng = lines(E["work"], "eng2", E["unit"])
        for (unit, n), (old, new) in CAPS_FIXES.items():
            if unit == (E["work"], E["unit"]):
                assert eng[n].startswith(old), (n, eng[n])
                eng[n] = new + eng[n][len(old):]
        mpages = [p for p in PAGES if p[0] == E["ms"]]
        secs, used = [], []
        unit = (E["work"], E["unit"])
        for (a, b, c, d, label), nxt in zip(E["sections"], E["sections"][1:] + [None]):
            if nxt:
                assert nxt[2] == d + 1 or (nxt[2] == d and (unit, d) in ENG_LINE_SPLITS), (E["slug"], d, nxt[2])

            def eline(n, first, last):
                t = eng[n]
                cutw = ENG_LINE_SPLITS.get((unit, n))
                if cutw:
                    assert t.startswith(cutw), (n, t)
                    if n == last and nxt and nxt[2] == n:              # this section ends inside line n
                        return t[:len(cutw)]
                    if n == first and any(x[3] == n for x in E["sections"] if x[0] < a):   # starts inside it
                        return t[len(cutw):].strip()
                return t
            pages = [p for p in mpages if p[3] <= b and p[4] >= a]
            assert pages, (E["slug"], a, b)
            for p in pages:
                if p[1] not in used:
                    used.append(p[1])

            def pn(p):
                s = f"{ms['shelf']} fol. {p[1]} runs from '{p[5]}' on its first line ({p[3]}) to '{p[6]}' on its last ({p[4]})."
                return s + (" " + p[7] if p[7] else "") + " Viewer: " + viewer(p)
            pre = f"{E['ref']}.{a}-{b}"
            if len(pages) == 1:
                note = f"Lines {a}-{b} are on {ms['name']} ({ms['shelf']}) fol. {pages[0][1]}. "
            else:
                note = f"Lines {a}-{b} start on {ms['shelf']} fol. {pages[0][1]} and continue on fol. {pages[-1][1]} (page break inside this section). "
            note += "Checked on the images: " + " ".join(pn(p) for p in pages)
            note += " The Latin shown is Greenough's edited text; the manuscript's spelling differs from it in places."
            sec_id = f"{a}-{b}"
            if E.get("english_notes", {}).get(sec_id):
                note += " " + E["english_notes"][sec_id]
            e_from = E.get("english_from", {}).get(sec_id, a)
            secs.append({
                "section": f"{a}-{b}",
                "original_ref": f"Virgil, {pre} ({label}); {ms['shelf']} fol. " + ", ".join(p[1] for p in pages),
                "original_text": "<p>" + "<br>\n".join(f"<sup>{n}</sup>{esc(lat[n])}" for n in range(a, b + 1)) + "</p>",
                "text": f"<p><sup>{e_from}</sup>" + "<br>\n".join(esc(eline(n, c, d)) for n in range(c, d + 1)) + "</p>",
                "scan_pages": [f"{KEY}/{files[(E['ms'], p[1])].name}" for p in pages],
                "scan_note": note,
            })
        tid = PREFIX + E["slug"]
        src = f"{ms['shelf']} ({ms['name']}) fol. {used[0]}-{used[-1]} (DigiVatLib) + Greenough Latin (Perseus) + {E['translator']} English (Perseus)"
        entry = {
            "id": tid, "slug": tid, "title": E["title"],
            "language": f"Latin (Greenough) / English ({E['translator']})",
            "source": src, "description": E["description"], "introduction": E["intro"],
            "translator_notes": [
                "Latin: J. B. Greenough, The Bucolics, Aeneid, and Georgics of Virgil (Boston: Ginn), Perseus digital text.",
                f"English: {E['translation_source']}. The translation is in verse with more lines than the Latin; "
                + ("each English section is cut at the end of one of Williams' sentences; where his sentence runs across a section break it is given whole to one side, "
                   "and each section's note says which Latin lines its English renders."
                   if E.get("english_notes") else
                   "each English section begins at the translator's line that starts the rendering of the section's first Latin line, so a few words can fall on the neighbouring side of a break."),
            ] + (["In Rhoades' Eclogue 4 the Perseus file lowercases three line-initial words; 'Muses' (line 1), 'Apollo' (13) and the vocative 'O' (76) are printed with capitals here."]
                 if E["work"] == "phi001" else []),
            "translation": secs,
            "verification": {
                "scan_source": f"Biblioteca Apostolica Vaticana, DigiVatLib, {ms['shelf']}, IIIF manifest {ms['manifest']} (fol. {', '.join(used)})",
                "scan_license": BAV_LICENSE,
                "scan_manuscript": ms["desc"],
                "scan_mapping": "Own visual check: the first and last line of every page used were read on IIIF crops of the capital script and identified in Greenough's text (words recorded in each scan_note)",
                "scan_mapping_urls": [ms["manifest"], f"https://digi.vatlib.it/mss/detail/{ms['shelf'].replace(' ', '').replace('lat.', 'lat.')}"] + [viewer(p) for p in mpages],
                "scan_local_paths": [f"{KEY}/{files[(E['ms'], f)].name}" for f in used],
                "original_text_source": f"J. B. Greenough, The Bucolics, Aeneid, and Georgics of Virgil (Boston: Ginn and Company), Perseus canonical-latinLit phi0690.{E['work']}.perseus-lat2 ({PERSEUS.format(w=E['work'], ed='lat2')})",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"{E['translation_source']} ({PERSEUS.format(w=E['work'], ed='eng2')})",
                "translation_license": "public domain in the US (published before 1929); Perseus digital text CC BY-SA 4.0",
                "translator": E["translator"],
                "verified_date": TODAY,
            },
        }
        PUB_DIR.mkdir(parents=True, exist_ok=True)
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": E["order"], "title": E["title"], "author_id": "virgil",
            "language": "Latin", "era": E["era"], "tradition": "roman", "category": "literature",
            "date_approx": E["date_approx"], "century": E["century"], "source": src,
            "description": E["description"], "themes": E["themes"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{files[(E['ms'], f)].name}", "caption": f"{ms['name']}, {ms['shelf']} fol. {f}"} for f in used]},
        })
        print(f"wrote {tid} ({len(secs)} sections)")
    for f in PUB_DIR.glob(f"{PREFIX}*.json"):
        if f.stem not in {r["id"] for r in rows}:
            f.unlink()
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Virgil: the golden age and the return of souls",
            "group": "Rome",
            "date_sort": -40,
            "author_name": "Virgil (70-19 BCE); Vergilius Romanus and Vergilius Vaticanus (4th-5th century)",
            "source_url": "https://digi.vatlib.it/view/MSS_Vat.lat.3867",
            "critical_edition": "Greenough, Virgil (Ginn), via Perseus",
            "translator_name": "James Rhoades (Eclogues), Theodore C. Williams (Aeneid, 1910)",
            "original_lang_label": "Latin · Greenough",
            "original_lang_code": "la",
            "edition_label": "",
            "search_terms": "virgil vergil fourth eclogue golden age sibyl new race messianic aeneid book 6 anchises world soul spiritus intus alit lethe elysium vergilius romanus vaticanus",
            "description": "Virgil's fourth Eclogue, on the return of the golden age, and Anchises' account of the world-soul and the return of souls in Aeneid 6, on the two oldest illustrated manuscripts of Virgil.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
