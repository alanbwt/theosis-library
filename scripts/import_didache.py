#!/usr/bin/env python3
"""
import_didache.py -- The Didache (Teaching of the Twelve Apostles) on the pages
of the only complete Greek manuscript, Codex Hierosolymitanus 54 (Jerusalem,
Greek Orthodox Patriarchate, Panagios Taphos 54, dated 1056).

Chain of evidence
-----------------
1. SCAN     Library of Congress microfilm of the manuscript, "Panagios Taphos 54.
            John Chrysostom: Synopsis of the Testaments; Apostolic Fathers.
            1056 A.D. 120 f." (Microfilm 5017, collection "Manuscripts in the
            Libraries of the Greek and Armenian Patriarchates in Jerusalem"),
            https://www.loc.gov/item/00279389694-jo/ , served by IIIF.
            Rights statement on the item: "These collections are in the public
            domain." Each microfilm frame shows one opening (verso left, recto
            right); frame n shows fol. (n-3)v and fol. (n-2)r. The folio
            numbers written on the rectos (76, 77, 78, 79, 80) were read on
            frames 78-82. Each opening is split at the gutter and cropped to
            the single page.
2. MAPPING  Read on the images (2026-11-12). The Didache begins on fol. 76r
            below the end of 2 Clement and a list of Old Testament books, under
            the heading "Διδαχὴ τῶν δώδεκα ἀποστόλων", and ends on fol. 80v
            ("...ἐπάνω τῶν νεφελῶν τοῦ οὐρανοῦ"), the rest of the page blank.
            The first and last words of every page were read and located in
            the Greek text (see PAGES below); the scribe also numbers some
            chapters in the margin (δ', ε', η', ι', ιϛ' seen on 77v, 78v, 80r).
3. GREEK    Kirsopp Lake, The Apostolic Fathers I (Loeb, 1912), digital text of
            the Open Greek and Latin / First1KGreek project,
            tlg1311.tlg001.1st1K-grc1 (CC BY-SA 4.0). Editorial footnotes and
            scripture references are left out. Words the digital text gets
            wrong were corrected against the printed page of Lake 1912
            (archive.org item theapostolicfath00unknuoft); every correction is
            listed in GREEK_FIXES and in the entry's translator notes.
4. ENGLISH  J. B. Lightfoot, The Apostolic Fathers (1891), transcription at
            earlychristianwritings.com (public domain). Phrases the
            transcription marks with braces (scriptural quotations and
            allusions) are shown in italics; its own verse numbers do not
            follow the standard Greek section numbers and are not shown.

Usage:
    python3 scripts/import_didache.py            # build
    python3 scripts/import_didache.py --force    # re-download and re-crop scans
Cache for raw microfilm frames: $THEOSIS_CACHE/didache or ~/.cache/theosis-didache
"""

import argparse
import html
import io
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "didache"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
CACHE = Path(os.environ.get("THEOSIS_CACHE", Path.home() / ".cache")) / f"theosis-{KEY}"
TODAY = date.today().isoformat()
UA = "Mozilla/5.0 (TheosisLibrary research; non-commercial)"
TEI = "{http://www.tei-c.org/ns/1.0}"

LOC_ITEM = "https://www.loc.gov/item/00279389694-jo/"
LOC_IIIF = "https://tile.loc.gov/image-services/iiif/service:amed:amedmonastery:00279389694-jo:{frame:04d}/full/pct:100/0/default.jpg"
GREEK_FILE = SRC / "tlg1311.tlg001.1st1K-grc1.xml"
GREEK_URL = "https://github.com/OpenGreekAndLatin/First1KGreek/blob/master/data/tlg1311/tlg001/tlg1311.tlg001.1st1K-grc1.xml"
ENGLISH_FILE = SRC / "didache-lightfoot.html"
ENGLISH_URL = "http://www.earlychristianwritings.com/text/didache-lightfoot.html"
LAKE_PRINT = "https://archive.org/details/theapostolicfath00unknuoft"

# folio -> (microfilm frame, side, first words read on the page, last words read on the page, Didache span)
PAGES = {
    "76r": (78, "R", "Διδαχὴ τῶν δώδεκα ἀποστόλων (heading, below the end of 2 Clement and the list of Old Testament books)",
            "πρῶτον ἀγα[πήσεις]", "title, 1.1-1.2"),
    "76v": (79, "L", "[ἀγαπή]σ(εις) τὸν θ(εὸ)ν τὸν ποιήσαντά σε· δεύτερον τὸν πλησίον σου", "οὐ κακολογήσεις· οὐ μνησικακήσ[εις]", "1.2-2.3"),
    "77r": (79, "R", "οὐκ ἔσῃ διγνώμων οὐδὲ δίγλωσσος", "εἰδὼς ὅτι ἄτερ θ(εο)ῦ", "2.4-3.10"),
    "77v": (80, "L", "οὐδὲν γίνεται· τέκνον μου, τοῦ λαλοῦντός σοι", "πρῶτον πάντων πονηρά ἐστι καὶ κατάρας", "3.10-5.1"),
    "78r": (80, "R", "μεστή· φόνοι, μοιχεῖαι, ἐπιθυμίαι", "κελεύεις δὲ νηστεῦσαι τὸν βαπτιζόμενον πρὸ μι[ᾶς]", "5.1-7.4"),
    "78v": (81, "L", "ἢ δύο. αἱ δὲ νηστεῖαι ὑμῶν μὴ ἔστωσαν", "καὶ ὑπὲρ τῆς γνώσεως καὶ πίστεως καὶ ἀθανασί[ας]", "7.4-10.2"),
    "79r": (81, "R", "ἧς ἐγνώρισας ἡμῖν διὰ Ἰ(ησο)ῦ τοῦ παιδός σου", "αὕτη δὲ ἡ ἁμαρ[τία]", "10.2-11.7"),
    "79v": (82, "L", "οὐκ ἀφεθήσεται. οὐ πᾶς δὲ ὁ λαλῶν ἐν πνεύματι", "δὸς κατὰ τὴν ἐντολήν. ὡ[σαύτως]", "11.7-13.6"),
    "80r": (82, "R", "σαύτως κεράμιον οἴνου ἢ ἐλαίου ἀνοίξας", "ζητοῦντες τὰ ἀνήκοντα ταῖς ψυχαῖς ὑμῶν", "13.6-16.2"),
    "80v": (83, "L", "οὐ γὰρ ὠφελήσει ὑμᾶς ὁ πᾶς χρόνος", "ἐπάνω τῶν νεφελῶν τοῦ οὐρανοῦ (end; rest of the page blank)", "16.2-16.8"),
}
# chapter -> folios carrying it, derived from the page spans above
CHAPTER_PAGES = {
    1: ["76r", "76v"], 2: ["76v", "77r"], 3: ["77r", "77v"], 4: ["77v"], 5: ["77v", "78r"],
    6: ["78r"], 7: ["78r", "78v"], 8: ["78v"], 9: ["78v"], 10: ["78v", "79r"],
    11: ["79r", "79v"], 12: ["79v"], 13: ["79v", "80r"], 14: ["80r"], 15: ["80r"], 16: ["80r", "80v"],
}
# (section, wrong, right): digital-text errors checked against the printed page of Lake 1912
GREEK_FIXES = [
    ("1.3", "τοῦς καταρωμένους", "τοὺς καταρωμένους"),
    ("1.5", "λαμβάνονται", "λαμβάνοντι"),
    ("5.1", "ʽΠ δὲ", "Ἡ δὲ"),
    ("11.1", "ἂν οὑν", "ἂν οὖν"),
    ("11.6", "ἕως οὖ", "ἕως οὗ"),
    ("11.10", "οὐ ποιεῖ. ψευδοπροφήτης", "οὐ ποιεῖ, ψευδοπροφήτης"),
    ("12.2", "δύο ἡ τρεῖς", "δύο ἢ τρεῖς"),
    ("12.2", "ἑὰν ᾖ", "ἐὰν ᾖ"),
    ("13.6", "οἴνου ἡ ἐλαίου", "οἴνου ἢ ἐλαίου"),
    ("14.2", "ὁ??ʼ", "οὗ"),
    ("14.3", "ὑπὸ κυρίον", "ὑπὸ κυρίου"),
]


def normalize_elision(t):
    """The digital text encodes Lake's elision apostrophe in three ways
    (consonant + combining U+0313, 'παῤ', 'δἰ'); print them as Lake does."""
    t = re.sub(r"([βγδζθκλμνξπρστφχψ])\u0313(?=[\s,.;·:]|$)", "\\1’", t)
    t = re.sub(r"(?<!\w)παῤ(?=\s)", "παρ’", t)
    t = re.sub(r"(?<!\w)([Δδ])ἰ(?=\s)", "\\1ι’", t)
    return t


def fetch(url, timeout=180, tries=5):
    last = None
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (a + 1))
    raise RuntimeError(f"GET failed: {url}: {last}")


# ---------------------------------------------------------------------------
# Scans
# ---------------------------------------------------------------------------
def frame_image(frame):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"frame_{frame:04d}.jpg"
    if not (p.exists() and p.stat().st_size > 100_000):
        data = fetch(LOC_IIIF.format(frame=frame))
        Image.open(io.BytesIO(data)).verify()
        p.write_bytes(data)
    return Image.open(p).convert("RGB")


def split_page(im, side):
    """Split a microfilm opening at the gutter (darkest column band near the
    middle) and crop the chosen page to its bright parchment area."""
    import numpy as np
    a = np.asarray(im.convert("L"), dtype=np.float32)
    h, w = a.shape
    cm = a[int(h * .2):int(h * .8)].mean(axis=0)
    lo, hi = int(w * .4), int(w * .6)
    g = lo + int(np.argmin(cm[lo:hi]))
    page = im.crop((0, 0, g, h)) if side == "L" else im.crop((g, 0, w, h))
    b = np.asarray(page.convert("L"), dtype=np.float32) > 140
    xs = np.where(b.mean(axis=0) > 0.5)[0]
    ys = np.where(b.mean(axis=1) > 0.5)[0]
    m = 40
    box = (max(0, xs.min() - m), max(0, ys.min() - m), min(page.width, xs.max() + m), min(page.height, ys.max() + m))
    return page.crop(box)


def make_scan(folio, force=False):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    dest = SCAN_DIR / f"h54-f{folio}.jpg"
    if dest.exists() and dest.stat().st_size > 10_000 and not force:
        return dest
    frame, side = PAGES[folio][0], PAGES[folio][1]
    page = split_page(frame_image(frame), side)
    if max(page.size) > 2400:
        page.thumbnail((2400, 2400))
    page.save(dest, "JPEG", quality=85, optimize=True)
    return dest


# ---------------------------------------------------------------------------
# Texts
# ---------------------------------------------------------------------------
def _text(el):
    out = []

    def walk(e):
        if e.tag in (TEI + "note", TEI + "bibl"):
            if e.tail:
                out.append(e.tail)
            return
        if e.text:
            out.append(e.text)
        for c in e:
            walk(c)
        if e.tail:
            out.append(e.tail)

    if el.text:
        out.append(el.text)
    for c in el:
        walk(c)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def greek():
    root = ET.parse(GREEK_FILE).getroot()
    body = root.find(f".//{TEI}body")
    head = _text(body.find(f".//{TEI}head"))
    secs = {}
    for ch in body.iter(TEI + "div"):
        if ch.get("subtype") != "chapter":
            continue
        for s in ch:
            if s.tag == TEI + "div" and s.get("subtype") == "section":
                secs[f"{ch.get('n')}.{s.get('n')}"] = _text(s)
    for ref, wrong, right in GREEK_FIXES:
        assert wrong in secs[ref], (ref, wrong)
        secs[ref] = secs[ref].replace(wrong, right)
    # the digital text uses ':' for the Greek raised dot (ano teleia); Lake prints '·'
    secs = {k: normalize_elision(v).replace(":", "·") for k, v in secs.items()}
    out = {}
    for k, v in secs.items():
        c, s = (int(x) for x in k.split("."))
        out.setdefault(c, []).append((s, v))
    return head, out


def english():
    t = ENGLISH_FILE.read_text(encoding="latin-1")
    t = t[t.find("1:1 There are two ways"):]
    t = t[:t.find("</STRONG></P>\n<P>\n")] if "</STRONG></P>\n<P>\n" in t else t[:t.find("</div>")]
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    assert t.count("{") == t.count("}")
    parts = re.split(r"(?:^|\s)(\d+):(\d+)\s", " " + t)
    chap = {}
    for i in range(1, len(parts) - 1, 3):
        c, body = int(parts[i]), parts[i + 2].strip()
        chap.setdefault(c, []).append(body)
    out, carry = {}, False
    for c in sorted(chap):
        s = ("{" if carry else "") + " ".join(chap[c])
        carry = s.count("{") > s.count("}")
        if carry:
            s += "}"
        s = re.sub(r"\{([^}]*)\}", r"<em>\1</em>", s)
        s = re.sub(r"\s+([,;:.?!])", r"\1", s)
        out[c] = s.strip()
    assert sorted(out) == list(range(1, 17)), sorted(out)
    assert "{" not in "".join(out.values()) and "}" not in "".join(out.values())
    return out


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    head, grc = greek()
    eng = english()
    assert sorted(grc) == list(range(1, 17))

    for f in PAGES:
        p = make_scan(f, args.force)
        print(f"  fol. {f}: {p.name} {Image.open(p).size} {p.stat().st_size} bytes")

    sections = []
    for c in range(1, 17):
        g = " ".join(f"<sup>{s}</sup>{t}" for s, t in grc[c])
        if c == 1:
            g = f"{head}<br>" + g
        folios = CHAPTER_PAGES[c]
        notes = []
        for f in folios:
            frame, side, first, last, span = PAGES[f]
            notes.append(f"fol. {f} (LoC microfilm frame {frame}, {'left' if side == 'L' else 'right'} page) carries {span}; "
                         f"checked on the image: the page begins '{first}' and ends '{last}'")
        sections.append({
            "section": str(c),
            "original_ref": f"Didache {c}; Hierosolymitanus 54 fol. {', '.join(folios)}",
            "original_text": g,
            "text": eng[c],
            "scan_pages": [f"{KEY}/h54-f{f}.jpg" for f in folios],
            "scan_note": "; ".join(notes) + ". The Greek shown is Lake's printed text (1912), which follows this manuscript closely; "
                         "the scribe's abbreviations and spellings on the page differ in small details.",
        })

    tid = f"{PREFIX}teaching-of-the-twelve-apostles"
    intro = (
        "<p>The <em>Didache</em> (\"Teaching\") is a short early Christian manual in sixteen chapters: the Two Ways of life and death (1-6), "
        "instructions on baptism, fasting, prayer and the eucharist (7-10), on travelling apostles and prophets (11-13), on the Lord's day "
        "and on bishops and deacons (14-15), and a closing warning about the last days (16). It is usually dated to the late first or early "
        "second century. Ancient writers name it, but its text was lost until Philotheos Bryennios found it in this manuscript and published it in 1883.</p>\n\n"
        "<p>The only complete Greek copy is Codex Hierosolymitanus 54 (Jerusalem, Library of the Greek Orthodox Patriarchate, "
        "Panagios Taphos 54), a parchment volume of 120 folios dated 1056. The same volume holds the Epistle of Barnabas and 1 and 2 Clement. "
        "The Didache fills fol. 76r-80v: it begins on fol. 76r after the end of 2 Clement and a list of Old Testament books, and ends on fol. 80v, "
        "where the rest of the page is left blank.</p>\n\n"
        "<p>The photographs are the Library of Congress microfilm of the Jerusalem patriarchate manuscripts (public domain). "
        "Each section is linked to the page or pages that carry that chapter; the page boundaries were read on the images, "
        "and every page's first and last words are recorded in the notes. The Greek is Kirsopp Lake's edition (1912); "
        "the English is J. B. Lightfoot's translation (1891).</p>"
    )
    entry = {
        "id": tid, "slug": tid,
        "title": "Didache (Teaching of the Twelve Apostles), on Codex Hierosolymitanus 54",
        "language": "Greek (Lake 1912) / English (Lightfoot 1891)",
        "source": "Codex Hierosolymitanus 54 (1056), fol. 76r-80v, Library of Congress microfilm + Lake 1912 Greek (First1KGreek, CC BY-SA 4.0) + Lightfoot 1891 English (public domain)",
        "description": "The Didache, an early Christian manual of the late first or early second century, shown chapter by chapter on the ten pages of the only complete Greek manuscript (Jerusalem, 1056).",
        "introduction": intro,
        "translator_notes": [
            "Greek: Kirsopp Lake, The Apostolic Fathers I (Loeb Classical Library, 1912), digital text by the First1KGreek project (CC BY-SA 4.0). "
            "Lake's footnotes and scripture references are not shown. The digital text writes the Greek raised dot as a colon; it is shown as '·'.",
            "The digital text was read against the printed pages of Lake 1912 (pp. 308-332) and these errors of the digital text were corrected: "
            + "; ".join(f"{r} '{w}' to '{c}'" for r, w, c in GREEK_FIXES) + ". Lake's own misprints ('μια' in 1.1, 'τούτωι' in 5.2) are kept as printed. "
            "Elided words, which the digital text encodes with stray accent characters (e.g. 'καθ̓', 'παῤ'), are written with an apostrophe as Lake prints them. "
            "Accents and breathings were not checked mark by mark against the print.",
            "English: J. B. Lightfoot, The Apostolic Fathers (1891), as transcribed at earlychristianwritings.com. Phrases the transcription marks "
            "with braces (scriptural quotations and allusions) are shown in italics. The transcription divides the chapters into its own numbered lines, which do not match the Greek "
            "section numbers, so the English is given by chapter without those numbers.",
            "Lightfoot translated his own Greek text, which differs from Lake's in a few places.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Library of Congress, Manuscripts in the Libraries of the Greek and Armenian Patriarchates in Jerusalem, Microfilm 5017, "
                           f"Panagios Taphos 54, frames 78-83 via IIIF ({LOC_ITEM})",
            "scan_license": "Public domain: 'These collections are in the public domain' (Library of Congress rights statement); credit: Library of Congress Collection of Manuscripts in the Greek Orthodox Patriarchate of Jerusalem",
            "scan_manuscript": "Jerusalem, Greek Orthodox Patriarchate Library, Panagios Taphos (Hierosolymitanus) 54, parchment, 120 fol., dated 1056; Didache fol. 76r-80v",
            "scan_mapping": "Read on the images: first and last words of each of the ten pages located in the Greek text; folio numbers 76-80 read on the rectos; marginal chapter numerals of the scribe agree",
            "scan_mapping_urls": [LOC_ITEM],
            "scan_local_paths": [f"{KEY}/h54-f{f}.jpg" for f in PAGES],
            "original_text_source": f"Kirsopp Lake, The Apostolic Fathers I (1912), First1KGreek tlg1311.tlg001.1st1K-grc1 ({GREEK_URL}); corrections checked on {LAKE_PRINT}",
            "original_text_license": "edition public domain; digital text CC BY-SA 4.0 (Open Greek and Latin)",
            "translation_source": f"J. B. Lightfoot, The Apostolic Fathers (1891), transcription at {ENGLISH_URL}",
            "translation_license": "public domain (published 1891)",
            "translator": "J. B. Lightfoot (1891)",
            "verified_date": TODAY,
        },
    }
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Didache (Codex Hierosolymitanus 54)",
            "group": "Early Christian",
            "date_sort": 100,
            "author_name": "Didache (late 1st or early 2nd c.; manuscript of 1056)",
            "source_url": LOC_ITEM,
            "critical_edition": "Kirsopp Lake, The Apostolic Fathers I (1912), via First1KGreek",
            "translator_name": "J. B. Lightfoot (1891)",
            "original_lang_label": "Greek · Lake 1912",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "didache teaching of the twelve apostles two ways baptism eucharist bryennios hierosolymitanus",
            "description": "The Didache, an early Christian church manual, on the ten pages of the only complete Greek manuscript, Codex Hierosolymitanus 54 (1056).",
        },
        "texts": [{
            "id": tid, "slug": tid, "order": 1,
            "title": entry["title"], "author_id": "didache-anonymous", "language": "Greek",
            "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
            "date_approx": "late 1st or early 2nd c. AD (composition); 1056 (manuscript)", "century": 1,
            "source": entry["source"], "description": entry["description"],
            "themes": ["didache", "apostolic-fathers", "early-church", "baptism", "eucharist", "lords-prayer", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/h54-f{f}.jpg", "caption": f"Hierosolymitanus 54 fol. {f}"} for f in PAGES]},
        }],
        "authors": [{
            "id": "didache-anonymous", "name": "Didache (anonymous)", "dates": "late 1st or early 2nd c. AD", "century": 1,
            "era": "Apostolic", "tradition": "christian", "language": "Greek",
            "bio": "Anonymous early Christian church manual, transmitted under the title Teaching of the Twelve Apostles.",
        }],
    }
    COLL.parent.mkdir(parents=True, exist_ok=True)
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
