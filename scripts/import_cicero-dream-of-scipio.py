#!/usr/bin/env python3
"""
import_cicero-dream-of-scipio.py: Cicero, The Dream of Scipio (De re publica 6.9-29),
complete, on the late 10th-century manuscript Bamberg, Staatsbibliothek, Msc.Class.38.

One entry; one section per section of the Somnium (6.9 to 6.29, 21 sections), each linked
to the manuscript page(s) that carry its words.

Chain of evidence
  1. MANUSCRIPT  Bamberg, Staatsbibliothek, Msc.Class.38: Cicero, Somnium Scipionis, followed
     by Macrobius' commentary on it; parchment, 36 leaves, 32 x 19.5 cm, end of the 10th
     century, Italy (catalogue data in the IIIF manifest). Digitised by the Bayerische
     Staatsbibliothek: IIIF manifest
     https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00140750/manifest
     (license in the manifest: Public Domain Mark 1.0; the Deutsche Digitale Bibliothek record
     lists CC BY-NC-SA 4.0). The Somnium is copied as a separate text at the head of the codex,
     under the red title "Somnium Scip(ionis) M. T. C. excerptum ex libro sexto de re publica",
     in two columns per page, from fol. 1r column a to fol. 3r column b, where it ends
     "ille discessit, ego somno solutus" with the red EXPLICIT SOMNIUM; the title of
     Macrobius' commentary follows on the same column.
  2. MAPPING  The first and last lines of every column (fol. 1r-3r, ten columns) were read
     on full-resolution IIIF crops and matched to the Latin text; the words read are stored in
     COLUMNS below and quoted in each section's scan_note. A section is assigned to every page
     whose columns contain part of it; a section cut by a page break lists both pages. No page
     was placed by counting or by text length.
  3. LATIN  C. F. W. Mueller, M. Tulli Ciceronis librorum de re publica sex quae manserunt
     (Leipzig: Teubner, 1889), via Perseus canonical-latinLit phi0474.phi043.perseus-lat2
     (CC BY-SA 4.0; edition public domain).
  4. ENGLISH  Clinton Walker Keyes, Cicero XVI: De re publica, De legibus (Loeb Classical
     Library, London: Heinemann / New York: Putnam, 1928), pp. 261-283. Public domain in the
     US (published 1928). Text taken from the archive.org OCR of the volume
     (item cicero-in-28-volumes.-vol.-16-loeb-213, Public Domain Mark), corrected against the
     page images of the same scan (leaves n144-n155); every correction is listed in OCR_FIXES.
     Keyes's English carries Roman chapter numbers only; the section breaks follow the Arabic
     section numbers printed beside his facing Latin text (the same breaks as Mueller's), placed
     at the English sentence that renders the first Latin words of each section.

Usage:
    python3 scripts/import_cicero-dream-of-scipio.py           # build
    python3 scripts/import_cicero-dream-of-scipio.py --force   # re-download scans
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

KEY = "cicero-dream-of-scipio"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"

MANIFEST_URL = "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00140750/manifest"
VIEWER = "https://www.digitale-sammlungen.de/en/view/bsb00140750?page={n}"
IMG_SVC = "https://api.digitale-sammlungen.de/iiif/image/v2/bsb00140750_{n:05d}"
LATIN_URL = "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/data/phi0474/phi043/phi0474.phi043.perseus-lat2.xml"
KEYES_OCR_URL = ("https://archive.org/download/cicero-in-28-volumes.-vol.-16-loeb-213/"
                 "Cicero%20in%2028%20volumes.%20vol.16%20%5BLoeb%20213%5D_djvu.txt")
KEYES_ITEM = "https://archive.org/details/cicero-in-28-volumes.-vol.-16-loeb-213"

# folio -> IIIF canvas number (manifest labels '1r (0005)' etc.)
CANVAS = {"1r": 5, "1v": 6, "2r": 7, "2v": 8, "3r": 9}

# ---------------------------------------------------------------------------
# Columns read on the images. start/end = section of the Somnium in which the
# column's first / last line falls; first/last = the words read on those lines
# (abbreviations expanded, spelling of the manuscript kept).
# ---------------------------------------------------------------------------
COLUMNS = [
    ("1r", "a", 9, 10, "Cum in Africam venissem ... Manlio (below the red title)", "notior. Quem ubi agnovi, et quidem"),
    ("1r", "b", 10, 12, "cohorrui. Sed ille: Ades, inquit, animo", "(ingemui)ssentque vehementius ceteri, leniter"),
    ("1v", "a", 12, 15, "arridens Scipio et quaeso, inquit, ne", "(sem)piternis ignibus, quae sidera et stellas"),
    ("1v", "b", 15, 17, "vocatis, quae globosae et rotundae di(vinis)", "complectitur, summus ipse deus, arcens"),
    ("2r", "a", 17, 18, "et continens ceteros, in quo sunt infixi", "acute et excitatio movetur sono"),
    ("2r", "b", 18, 20, "gravissimo autem hic lunaris atque infi(mus)", "possint, sed partim obliquos, partim"),
    ("2v", "a", 20, 23, "etiam adversos stare vobis, a quibus expec(tare)", "... aeternam, sed ne diuturnam"),
    ("2v", "b", 23, 25, "quidem gloriam assequi possumus. Quid", "omnis ille et angustiis cingitur his"),
    ("3r", "a", 25, 27, "regionum quas vides, nec umquam", "principium extinctum nec ipsum"),
    ("3r", "b", 27, 29, "ab alia renascetur, nec ex se aliud", "discessit, ego somno solutus, then the red EXPLICIT SOMNIUM"),
]
EXTRA = {
    "6.26": "6.26 begins on fol. 3r column a line 4 ('Quae cum dixisset'); 'Deum te igitur scito esse' ('Know, then, that you are a god') begins line 17 of the same column.",
    "6.12": "The manuscript reads 'et quaeso' where Mueller prints 'St! quaeso'.",
    "6.18": "The manuscript reads 'acute et excitatio movetur sono' (Mueller 'acuto et excitato movetur sono').",
    "6.9": "The red title above column a reads 'Somnium Scip(ionis) M. T. C. excerptum ex libro sexto de re publica'; the manuscript writes the consul's name 'Manlio' (Mueller 'Manilio').",
    "6.29": "Column b of fol. 3r ends the Somnium with the red EXPLICIT SOMNIUM, followed by the red title of Macrobius' commentary.",
}

# ---------------------------------------------------------------------------
# Keyes 1928, English pages in the archive.org OCR (line ranges of the djvu.txt,
# English pages 261-283 only; Latin pages and footnotes excluded).
# ---------------------------------------------------------------------------
KEYES_RANGES = [(12424, 12441), (12503, 12542), (12599, 12637), (12700, 12740), (12804, 12842),
                (12901, 12939), (12991, 13029), (13086, 13120), (13179, 13213), (13273, 13312),
                (13364, 13401), (13440, 13462)]
# OCR -> print, each checked on the page images (archive.org leaves n144-n155).
# Footnote reference marks are dropped; Keyes's Roman chapter numbers are dropped.
OCR_FIXES = [
    ("IX. Scipio. l was", "Scipio. I was"),
    ("Manilius! as", "Manilius, as"),
    ("reasons? was", "reasons was"),
    ("words: “I thank thee", "words: “I thank thee"),
    ("hero? faded", "hero faded"),
    ("X. Later,", "Later,"),
    ("hour was late, The", "hour was late. The"),
    ("Homer,! about", "Homer, about"),
    ("said : * Courage", "said: “Courage"),
    ("XI. *Do you see", "“Do you see"),
    ("at rest” (and", "at rest” (and"),
    ("Carthage), *that city", "Carthage), “that city"),
    ("by pu own efforts the surname? which till now you ave as", "by your own efforts the surname which till now you have as"),
    ("Numantia.! But", "Numantia. But"),
    ("grandson.? XII. * Then", "grandson. “Then"),
    ("tbe light", "the light"),
    ("cónsidered perfect,? in", "considered perfect, in"),
    ("kinsmen.” 4 Laelius", "kinsmen.” Laelius"),
    ("XIII. “ But", "“But"),
    ("so that ou may", "so that you may"),
    ("they return.\" XIV. Though", "they return.” Though"),
    ("still alive, * Surely all those are alive,\" he said, “ who", "still alive. “Surely all those are alive,” he said, “who"),
    ("approaching you?\"", "approaching you?”"),
    ("XV. Assoon", "As soon"),
    ("cried out: ** O best", "cried out: “O best"),
    ("thither to you?” * Not so,”", "thither to you?” “Not so,”"),
    ("replied, “for", "replied, “for"),
    ("temple? is", "temple is"),
    ("XVI. But", "But"),
    ("grandfather? here", "grandfather here"),
    ("now see\" (it", "now see” (it"),
    ("fires), * and which", "fires), “and which"),
    ("Milky Circle.”", "Milky Circle.”"),
    ("light.3 The", "light. The"),
    ("XVII. As I", "As I"),
    ("said: * How long", "said: “How long"),
    ("assign to Mars, Below", "assign to Mars. Below"),
    ("distance! is", "distance is"),
    ("downward.” XVIII. reve recovering", "downward.” After recovering"),
    ("I said : ** What", "I said: “What"),
    ("my ears?\" ? * That is produced,\" he replied, * by", "my ears?” “That is produced,” he replied, “by"),
    ("radiance.” While", "radiance.” While"),
    ("back toearth. XIX. Then", "back to earth. Then"),
    ("resumed : * [ see", "resumed: “I see"),
    ("Catadupa;! the", "Catadupa; the"),
    ("own;! from", "own; from"),
    ("XX. * Besides", "“Besides"),
    ("yours)? has", "yours) has"),
    ("XXI. “But", "“But"),
    ("conflagrations! which", "conflagrations which"),
    ("youtobetalkedof bythose", "you to be talked of by those"),
    ("[XXII] who", "who"),
    ("revolving year? I hardly", "revolving year. I hardly"),
    ("XXIII. “Consequently", "“Consequently"),
    ("posterity.\" XXIV. When", "posterity.” When"),
    ("XXV. *For that", "“For that"),
    ("XXVI. ** Therefore", "“Therefore"),
    ("immortal! Use it", "immortal. Use it"),
    ("my sleep.”", "my sleep."),
]
# First words of each English section (Keyes), matching the first Latin words of
# Mueller's sections 10-29.
EN_STARTS = {
    10: "Later, after I had been entertained", 11: "“Do you see yonder city",
    12: "“Then, Africanus, it will be your duty", 13: "“But, Africanus, be assured",
    14: "Though I was then thoroughly terrified", 15: "As soon as I had restrained",
    16: "But, Scipio, imitate your grandfather", 17: "As I gazed still more fixedly",
    18: "After recovering from the astonishment", 19: "Men's ears, ever filled",
    20: "Then Africanus resumed", 21: "“Besides, you will notice",
    22: "Do you suppose that your fame", 23: "“But even if future generations",
    24: "who were no less numerous", 25: "“Consequently, if you despair",
    26: "When he had spoken thus", 27: "“For that which is always in motion",
    28: "“Therefore, now that it is clear", 29: "Use it, therefore, in the best pursuits",
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


def get_scan(folio, force):
    from PIL import Image
    path = SCAN_DIR / f"bamberg-class38-f{folio}.jpg"
    if path.exists() and not force:
        return path
    url = IMG_SVC.format(n=CANVAS[folio]) + "/full/1700,/0/default.jpg"
    Image.open(io.BytesIO(fetch(url))).convert("RGB").save(path, quality=85)
    return path


def latin_sections():
    root = ET.parse(cached("phi0474.phi043.perseus-lat2.xml", LATIN_URL)).getroot()
    out = {}
    for b in root.iter(f"{TEI}div"):
        if b.get("subtype") == "book" and b.get("n") == "6":
            for d in b:
                if d.tag != f"{TEI}div" or not (9 <= int(d.get("n")) <= 29):
                    continue
                buf = []

                def walk(e):
                    tag = e.tag.replace(TEI, "")
                    if tag in ("label", "note", "head", "bibl"):
                        if e.tail:
                            buf.append(e.tail)
                        return
                    if e.text:
                        buf.append(e.text)
                    for c in e:
                        walk(c)
                    if e.tail:
                        buf.append(e.tail)
                for c in d:
                    walk(c)
                out[int(d.get("n"))] = re.sub(r"\s+", " ", "".join(buf)).strip()
    assert sorted(out) == list(range(9, 30)), sorted(out)
    return out


def keyes_sections():
    lines = cached("keyes1928-loeb213_djvu.txt", KEYES_OCR_URL).read_text(encoding="utf-8").split("\n")
    keep = []
    for a, b in KEYES_RANGES:
        for i in range(a, b + 1):
            l = lines[i - 1]
            if l.startswith("THE REPUBLIC") or not l.strip():
                continue
            keep.append(l.rstrip())
    s = "\n".join(keep)
    s = re.sub(r"-\n", "", s)
    s = re.sub(r"\s+", " ", s.replace("\n", " "))
    s = s.replace(" ;", ";").replace(" :", ":")
    for old, new in OCR_FIXES:
        old = old.replace(" ;", ";").replace(" :", ":")
        if old not in s:
            raise SystemExit(f"OCR fix not found: {old!r}")
        s = s.replace(old, new, 1)
    s = s.replace("’", "'")
    # remaining straight double quotes -> curly by position
    s = re.sub(r'"(?=\w)', "“", s)
    s = s.replace('"', "”")
    s = re.sub(r"\s+([,;:!?.])", r"\1", s)
    assert not re.search(r"[*!?][a-z]|\s[*]\s|\d", s.replace("Scipio. I", "")), re.findall(r".{20}[*\d].{20}", s)
    out, pos = {}, 0
    starts = [(n, s.index(t)) for n, t in sorted(EN_STARTS.items())]
    prev_n, prev_i = 9, 0
    for n, i in starts:
        assert i > prev_i, (n, i)
        out[prev_n] = s[prev_i:i].strip()
        prev_n, prev_i = n, i
    out[29] = s[prev_i:].strip()
    return out


def esc(t):
    return H.escape(t, quote=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cached("bamberg-class38-manifest.json", MANIFEST_URL)
    lat = latin_sections()
    eng = keyes_sections()
    files = {f: get_scan(f, args.force) for f in CANVAS}

    def col_note(c):
        folio, col, a, b, first, last = c
        return (f"fol. {folio} column {col} runs from '{first}' on its first line (6.{a}) "
                f"to '{last}' on its last line (6.{b})")

    sections = []
    for n in range(9, 30):
        cols = [c for c in COLUMNS if c[2] <= n <= c[3]]
        assert cols, n
        folios = []
        for c in cols:
            if c[0] not in folios:
                folios.append(c[0])
        where = "; ".join(f"fol. {c[0]} col. {c[1]}" for c in cols)
        note = (f"On Bamberg Msc.Class.38 {where}. " if len(folios) == 1 else
                f"Starts on fol. {folios[0]} and continues on fol. {folios[-1]} (page break inside this section): {where}. ")
        note += "Checked on the images: " + "; ".join(col_note(c) for c in cols) + "."
        if f"6.{n}" in EXTRA:
            note += " " + EXTRA[f"6.{n}"]
        note += (" The Latin shown is Mueller's critical text; the copyist's spelling and some words differ from it. Viewer: "
                 + ", ".join(VIEWER.format(n=CANVAS[f]) for f in folios))
        sections.append({
            "section": f"6.{n}",
            "original_ref": f"Cicero, De re publica 6.{n}; Bamberg Msc.Class.38 {where}",
            "original_text": f"<p><sup>{n}</sup>{esc(lat[n])}</p>",
            "text": f"<p><sup>{n}</sup>{esc(eng[n])}</p>",
            "scan_pages": [f"{KEY}/{files[f].name}" for f in folios],
            "scan_note": note,
        })

    tid = PREFIX + "somnium-scipionis"
    title = "Cicero, The Dream of Scipio (De re publica 6.9-29)"
    desc = ("Cicero's Dream of Scipio, the closing myth of the Republic: Scipio Aemilianus sees the heavens, the music of the spheres "
            "and the smallness of the earth, and is told 'know, then, that you are a god'. Complete, on the manuscript Bamberg Msc.Class.38 (late 10th century).")
    intro = (
        "<p>Cicero wrote the six books of <em>On the Republic</em> in 54-51 BCE. Most of the work was lost in the Middle Ages, "
        "but its ending, the Dream of Scipio (<em>Somnium Scipionis</em>), survived complete because the Latin writer Macrobius "
        "(early 5th century) wrote a long commentary on it, and copyists placed Cicero's text before the commentary. "
        "In the dream, Scipio Aemilianus is taken up by his grandfather Scipio Africanus to a high place among the stars. "
        "He is told that those who serve their country have a place prepared in heaven, that the bodies of men are a prison, "
        "and that souls come from the eternal fires of the stars. He sees the nine spheres of the universe, hears the music they make, "
        "and looks back at an earth so small that Rome's empire seems a point. Africanus tells him that fame among men is brief, "
        "and that the true self is the spirit: 'Know, then, that you are a god, if a god is that which lives, feels, remembers, and foresees, "
        "and which rules, governs, and moves the body over which it is set, just as the supreme God above us rules this universe' "
        "(<em>deum te igitur scito esse</em>, 6.26). The closing argument for the immortality of the self-moving soul (6.27-28) is taken from Plato's <em>Phaedrus</em>.</p>\n\n"
        "<p>The pages shown are from Bamberg, Staatsbibliothek, Msc.Class.38, written in Italy at the end of the 10th century. "
        "The Somnium stands at the head of the book as a text of its own, under the red title 'Somnium Scipionis M. T. C., excerpt from the sixth book on the Republic', "
        "and fills five pages in two columns, from fol. 1r to fol. 3r; it ends with a red 'Explicit somnium', and Macrobius' commentary begins in the same column. "
        "Each section below is one numbered section of the text (6.9 to 6.29). The page or pages listed for it were identified by reading the first and last lines of every column on the images. "
        "The Latin is Mueller's critical edition (1889), not a transcription of this manuscript, so its spelling and a few words differ from what the copyist wrote "
        "(for example, the manuscript has 'et quaeso' for Mueller's 'St! quaeso' at 6.12). The English is C. W. Keyes's Loeb translation of 1928. The text is complete.</p>"
    )
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Latin (Mueller) / English (C. W. Keyes, 1928)",
        "source": "Bamberg, Staatsbibliothek, Msc.Class.38 fol. 1r-3r (Bayerische Staatsbibliothek IIIF) + Mueller Latin (Perseus) + C. W. Keyes English (Loeb 1928, archive.org)",
        "description": desc,
        "introduction": intro,
        "translator_notes": [
            "Latin: C. F. W. Mueller, M. Tulli Ciceronis librorum de re publica sex quae manserunt (Teubner, 1889), Perseus digital text.",
            "English: Clinton Walker Keyes, Cicero, De re publica, De legibus (Loeb Classical Library, 1928), pp. 261-283, transcribed from the archive.org scan and checked against its page images. "
            "Keyes's Roman chapter numbers and footnote marks are left out; section breaks follow the section numbers beside his Latin text.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Bayerische Staatsbibliothek / MDZ digital collections, Bamberg Msc.Class.38: IIIF manifest {MANIFEST_URL} (canvases 5-9 = fol. 1r-3r)",
            "scan_license": "Credit: Staatsbibliothek Bamberg, Msc.Class.38, digitised by the Bayerische Staatsbibliothek. License stated in the IIIF manifest: Public Domain Mark 1.0; the Deutsche Digitale Bibliothek record lists CC BY-NC-SA 4.0",
            "scan_manuscript": "Bamberg, Staatsbibliothek, Msc.Class.38: Cicero, Somnium Scipionis (fol. 1r-3r) and Macrobius, Commentarii in Somnium Scipionis; parchment, 36 leaves, 32 x 19.5 cm, end of the 10th century, Italy; two columns",
            "scan_mapping": "Own visual check: the first and last lines of each of the ten columns on fol. 1r-3r were read on full-resolution IIIF crops and matched to the Latin (words recorded in each scan_note)",
            "scan_mapping_urls": [MANIFEST_URL, "https://mdz-nbn-resolving.de/urn:nbn:de:bvb:12-bsb00140750-1"] + [VIEWER.format(n=CANVAS[f]) for f in CANVAS],
            "scan_local_paths": [f"{KEY}/{files[f].name}" for f in CANVAS],
            "original_text_source": f"C. F. W. Mueller, M. Tulli Ciceronis librorum de re publica sex quae manserunt (Leipzig: Teubner, 1889), Perseus canonical-latinLit phi0474.phi043.perseus-lat2 ({LATIN_URL})",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": f"Clinton Walker Keyes, Cicero XVI: De re publica, De legibus (Loeb Classical Library 213; London: Heinemann / New York: Putnam, 1928), pp. 261-283; scan and OCR at {KEYES_ITEM}",
            "translation_license": "public domain in the US (published 1928, before 1929)",
            "translator": "C. W. Keyes (1928)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": 1, "title": title, "author_id": "cicero",
        "language": "Latin", "era": "Late Republic", "tradition": "roman", "category": "philosophy",
        "date_approx": "54-51 BCE (composition); manuscript end of the 10th century",
        "century": -1, "source": entry["source"], "description": desc,
        "themes": ["cicero", "somnium-scipionis", "dream-of-scipio", "know-that-you-are-a-god", "music-of-the-spheres",
                   "immortality", "soul", "cosmos", "theosis", "philosophy", "latin", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[f].name}", "caption": f"Bamberg Msc.Class.38 fol. {f}"} for f in CANVAS]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Cicero: The Dream of Scipio",
            "group": "Rome",
            "date_sort": -51,
            "author_name": "Marcus Tullius Cicero (106-43 BCE); Bamberg manuscript of the late 10th century",
            "source_url": "https://www.digitale-sammlungen.de/en/view/bsb00140750",
            "critical_edition": "Mueller, De re publica (Teubner 1889), via Perseus",
            "translator_name": "C. W. Keyes (Loeb, 1928)",
            "original_lang_label": "Latin · Mueller",
            "original_lang_code": "la",
            "edition_label": "",
            "search_terms": "cicero somnium scipionis dream of scipio de re publica republic know that you are a god music of the spheres macrobius bamberg",
            "description": "The Dream of Scipio, the end of Cicero's Republic, in which the soul is shown its home among the stars and told that it is a god; complete on a manuscript of the late 10th century.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
