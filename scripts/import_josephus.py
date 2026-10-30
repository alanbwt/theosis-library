#!/usr/bin/env python3
"""
import_josephus.py — Josephus, Jewish Antiquities 18.63-64 (Testimonium Flavianum).

One entry, three Greek manuscript witnesses, one section per witness, each linked
to the exact Vatican Library folio that carries the passage.

Chain of evidence:
  1. MAPPING  Folio and line numbers from T. C. Schmidt, Josephus and Jesus: New
              Evidence for the One Called Christ (Oxford University Press, 2025),
              manuscript image list at https://josephusandjesus.com/manuscript-images/
                Vat. gr. 148  fol. 214v lines 3-13   (10th/11th c., excerpt)
                Vat. gr. 342  fol. 282v lines 11-24  (1087/1088, excerpt)
                Vat. gr. 984  fol. 152v lines 27-31  (1354, full Antiquities)
              Each folio was then checked by eye on the downloaded image (the
              passage opens "Γίνεται δὲ κατὰ τοῦτον τὸν χρόνον Ἰησοῦς σοφὸς ἀνήρ").
  2. SCAN     DigiVatLib IIIF (digi.vatlib.it). BAV terms: non-commercial reuse
              with credit "© Biblioteca Apostolica Vaticana".
  3. GREEK    Benedikt Niese, Flavii Iosephi opera (Weidmann 1885-1890), via
              Perseus canonical-greekLit tlg0526.tlg001.perseus-grc2 (CC BY-SA 4.0).
              Niese brackets the whole passage as suspect; the brackets are noted.
  4. ENGLISH  William Whiston, The Works of Flavius Josephus (1737; Perseus
              tlg0526.tlg001.perseus-eng2 from the 1856 printing), public domain.

Usage:
    python3 scripts/import_josephus.py           # build
    python3 scripts/import_josephus.py --force   # re-download scans
"""

import argparse
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "josephus"
PUB_DIR = ROOT / "translations" / "published"
DATA = ROOT / "data" / "texts.json"
AUTHORS = ROOT / "data" / "authors.json"
SRC = ROOT / "data" / "sources" / "josephus"
TODAY = date.today().isoformat()
TID = "verified-josephus-antiquities-18-63"

TEI = "{http://www.tei-c.org/ns/1.0}"
SCHMIDT_URL = "https://josephusandjesus.com/manuscript-images/"
SCHMIDT_BOOK = "https://academic.oup.com/book/60034"

# region = IIIF region "x,y,w,h" of the single page (None = full image)
WITNESSES = [
    {
        "key": "vatgr148-f214v",
        "shelfmark": "Vat. gr. 148",
        "folio": "214v",
        "lines": "3-13",
        "date": "10th/11th c.",
        "kind": "excerpt headed 'From the 18th book of the Jewish Antiquities: testimony concerning Christ'",
        "iiif": "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.148/Vat.gr.148_0226.jp2",
        "region": "0,0,1110,1059",
        "viewer": "https://digi.vatlib.it/view/MSS_Vat.gr.148/0226",
        "note": "DigiVatLib image 226. Black-and-white microfilm scan, the only image the Vatican Library has published of this page. "
                "The heading reads ἐκ τοῦ ὀκτωκαιδεκάτου λόγου τῆς Ἰουδαϊκῆς ἀρχαιολογίας περὶ τοῦ Χριστοῦ μαρτυρία. "
                "This is the manuscript page shown in the October 2026 news coverage of Schmidt's study.",
    },
    {
        "key": "vatgr342-f282v",
        "shelfmark": "Vat. gr. 342",
        "folio": "282v",
        "lines": "11-24",
        "date": "1087/1088",
        "kind": "excerpt copied after the Psalter, introduced 'Ἰουδαῖος Ἰώσηππος'",
        "iiif": "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.342/Vat.gr.342_0580_fa_0282v.jp2",
        "region": None,
        "viewer": "https://digi.vatlib.it/view/MSS_Vat.gr.342/0580",
        "note": "DigiVatLib image 580 (Polonsky Foundation digitization).",
    },
    {
        "key": "vatgr984-f152v",
        "shelfmark": "Vat. gr. 984",
        "folio": "152v",
        "lines": "27-31",
        "date": "1354",
        "kind": "complete text of the Antiquities (fol. 1r-173r), the passage in its place in book 18",
        "iiif": "https://digi.vatlib.it/iiifimage/MSS_Vat.gr.984/Vat.gr.984_0311_fa_0152v-153r.jp2",
        "region": "0,0,4700,6772",
        "viewer": "https://digi.vatlib.it/view/MSS_Vat.gr.984/0311",
        "note": "DigiVatLib image 311 (opening 152v-153r, left page cropped). The passage begins at the red initial Γ; "
                "a marginal note beside it reads περὶ τοῦ Χ(ριστο)ῦ.",
    },
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def get_scan(w, force):
    path = SCAN_DIR / f"{w['key']}.jpg"
    if path.exists() and not force:
        return path
    region = w["region"] or "full"
    img = Image.open(io.BytesIO(fetch(f"{w['iiif']}/{region}/1600,/0/default.jpg"))).convert("RGB")
    img.save(path, quality=88)
    return path


def section_text(xml_path, lang, sections):
    root = ET.parse(xml_path).getroot()
    out = {}
    for div in root.iter(f"{TEI}div"):
        base = div.get("{http://www.w3.org/XML/1998/namespace}base", "")
        if div.get("subtype") == "section" and base.endswith(":18") and div.get("n") in sections:
            out[div.get("n")] = re.sub(r"\s+", " ", "".join(div.itertext())).strip()
    assert set(out) == set(sections), (lang, out.keys())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)

    grc = section_text(SRC / "tlg0526.tlg001.perseus-grc2.xml", "grc", {"63", "64"})
    eng = section_text(SRC / "tlg0526.tlg001.perseus-eng2.xml", "eng", {"63"})
    # Whiston prints 18.63-64 as one paragraph; split at the start of 18.64.
    w63, w64 = eng["63"].split(" And when Pilate,", 1)
    w64 = "And when Pilate," + w64
    assert w63.startswith("Now there was about this time Jesus") and w63.endswith("He was [the] Christ."), w63
    assert grc["63"].startswith("Γίνεται δὲ κατὰ τοῦτον τὸν χρόνον Ἰησοῦς") and grc["64"].endswith("οὐκ ἐπέλιπε τὸ φῦλον."), grc

    greek = f"<sup>63</sup>{grc['63']} <sup>64</sup>{grc['64']}"
    english = f"<sup>63</sup>{w63} <sup>64</sup>{w64}"

    sections = []
    for w in WITNESSES:
        p = get_scan(w, args.force)
        print(f"  {w['shelfmark']} fol. {w['folio']}: {p.stat().st_size} bytes")
        sections.append({
            "section": f"18.63-64 ({w['shelfmark']}, fol. {w['folio']})",
            "original_ref": f"Josephus, Ant. 18.63-64; {w['shelfmark']} fol. {w['folio']} lines {w['lines']} ({w['date']}), {w['kind']}",
            "original_text": greek,
            "text": english,
            "scan_pages": [f"josephus/{p.name}"],
            "scan_note": f"{w['note']} Viewer: {w['viewer']} ; folio and lines per Schmidt, {SCHMIDT_URL} . "
                         "Greek shown is Niese's critical text; the copyist's wording on this page differs in small details.",
        })

    entry = {
        "id": TID, "title": "Josephus, Jewish Antiquities 18.63-64 (Testimonium Flavianum)", "slug": TID,
        "language": "Greek (Niese 1890) / English (Whiston 1737)",
        "source": "Vatican Library manuscripts Vat. gr. 148, 342, 984 via DigiVatLib IIIF + folio identifications from T. C. Schmidt (OUP 2025) + Niese Greek (Perseus) + Whiston English (Perseus)",
        "description": "The Testimonium Flavianum, Josephus' paragraph on Jesus (Antiquities 18.63-64, written c. 93/94 AD), "
                       "shown on three Greek manuscript pages in the Vatican Library, each linked to the exact folio.",
        "introduction": (
            "<p>Around 93/94 AD the Jewish historian Flavius Josephus mentioned Jesus in book 18 of his <em>Jewish Antiquities</em>. "
            "The paragraph, known as the <strong>Testimonium Flavianum</strong>, is the oldest description of Jesus by a non-Christian writer. "
            "Its authenticity has been argued over for centuries: Niese's 1890 edition prints the whole passage in brackets as a suspected Christian insertion.</p>\n\n"
            "<p>In <em>Josephus and Jesus: New Evidence for the One Called Christ</em> (Oxford University Press, 2025), T. C. Schmidt argues the passage is substantially authentic, "
            "and that Josephus may have drawn on people close to the trial of Jesus, most likely the high priest Ananus II, son of the Annas who questioned Jesus (John 18:13). "
            "That argument was reported widely in October 2026.</p>\n\n"
            "<p>Below, the same passage appears three times, once for each Greek manuscript: two medieval excerpts (Vat. gr. 148 and Vat. gr. 342) "
            "and a complete copy of the <em>Antiquities</em> made in 1354 (Vat. gr. 984). The folio and line numbers come from Schmidt's published manuscript list "
            "and were checked against each page image.</p>"
        ),
        "translator_notes": [
            "Greek is Benedikt Niese's critical text (Flavii Iosephi opera, 1885-1890), which brackets 18.63-64 as suspect. The brackets are editorial and are not shown in the text.",
            "English is William Whiston's 1737 translation; his '[the] Christ' brackets are his own.",
            "The oldest Greek manuscript of book 18 (Milan, Ambrosiana F 128 sup., 11th c., fol. 274r-v) is not included here.",
            "Source of the folio identifications and of the Ananus II argument: T. C. Schmidt, Josephus and Jesus (OUP 2025), chapter 'Ananus II and the Trial of Jesus', https://academic.oup.com/book/60034/chapter/513641763",
        ],
        "translation": sections,
        "verification": {
            "scan_source": "Biblioteca Apostolica Vaticana, DigiVatLib IIIF (digi.vatlib.it): Vat. gr. 148 image 226, Vat. gr. 342 image 580, Vat. gr. 984 image 311",
            "scan_license": "© Biblioteca Apostolica Vaticana; reproduced for non-commercial scholarly use with credit",
            "scan_manuscript": "Vat. gr. 148 (10th/11th c.), Vat. gr. 342 (1087/1088), Vat. gr. 984 (1354)",
            "scan_mapping": "Folio and line numbers from T. C. Schmidt's manuscript list (josephusandjesus.com, companion to OUP 2025); each page checked by eye for the opening words of 18.63",
            "scan_mapping_urls": [SCHMIDT_URL, SCHMIDT_BOOK] + [w["viewer"] for w in WITNESSES],
            "scan_local_paths": [s["scan_pages"][0] for s in sections],
            "original_text_source": "Benedikt Niese, Flavii Iosephi opera (Weidmann, 1885-1890), Perseus canonical-greekLit tlg0526.tlg001.perseus-grc2",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": "William Whiston, The Works of Flavius Josephus (1737), Perseus tlg0526.tlg001.perseus-eng2 (Alden and Beardsley 1856 printing)",
            "translation_license": "public domain; Perseus digital text CC BY-SA 4.0",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

    meta = {
        "id": TID, "title": entry["title"], "author_id": "josephus", "language": "Greek",
        "era": "Apostolic", "tradition": "jewish", "category": "historical-witness",
        "date_approx": "c. 93/94 AD (composition); 10th-14th c. (Vatican manuscripts)", "century": 1,
        "source": entry["source"], "description": entry["description"],
        "themes": ["josephus", "jesus", "testimonium-flavianum", "historical-jesus", "greek", "verified"],
        "is_first_translation": False, "status": "published", "slug": TID,
        "scans": {"pages": [{"file": s["scan_pages"][0], "caption": f"{w['shelfmark']} fol. {w['folio']}"} for s, w in zip(sections, WITNESSES)]},
    }
    d = json.loads(DATA.read_text(encoding="utf-8"))
    d["texts"] = [t for t in d["texts"] if t["id"] != TID] + [meta]
    DATA.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

    a = json.loads(AUTHORS.read_text(encoding="utf-8"))
    if not any(x["id"] == "josephus" for x in a["authors"]):
        a["authors"].append({
            "id": "josephus", "name": "Flavius Josephus", "dates": "37-c. 100 AD", "century": 1,
            "era": "Apostolic", "tradition": "jewish", "language": "Greek",
            "bio": "Jewish priest, commander in the revolt of 66 AD and later historian under the Flavian emperors; author of the Jewish War and the Jewish Antiquities.",
            "name_latin": "Flavius Iosephus",
        })
        AUTHORS.write_text(json.dumps(a, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
