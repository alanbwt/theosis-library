#!/usr/bin/env python3
"""
import_vendidad.py - Vendidad (Videvdad) Fargards 1 and 2 on a dated Vendidad Sade manuscript.

Chain of evidence
  1. SCANS    Columbia University, Rare Book & Manuscript Library, MS Or 320 - FOLIO,
              "Vendidad Sade", 322 leaves, 17 lines to the page, Avestan with Persian verses
              before each fargard; copied at Surat, colophon dated day Asman, month Adar,
              1131 AY (1762 CE) by Herbed Darab Framroz Minochehr (f. 320r-320v). Images on
              OPenn (https://openn.library.upenn.edu/Data/0032/html/ms_or_320.html) under the
              Creative Commons Public Domain Mark (stated in the TEI, data/sources/vendidad/).
  2. MAPPING  Chapter level only, from the Persian verse headings, which were read on the
              images: fol. 60r (heading naming the Vendidad and "the first fargard",
              vargard-e avval), fol. 63v (heading for "the second fargard", which "tells the
              story of Jamshid"), fol. 71v (heading that speaks of reading the third fargard).
              Fargard 1 therefore runs from fol. 60r (below the heading) to fol. 63v (above
              the second heading); Fargard 2 from fol. 63v (below that heading) to fol. 71v
              (above the third heading). Page-by-page positions of paragraphs inside each
              fargard could not be confirmed on the images (the Avestan hand could not be
              read with enough certainty), so each fargard is ONE section listing all its
              pages, as the mapping rule for this collection prescribes. Nothing is placed on
              a single page by calculation.
  3. AVESTAN  Geldner's text (Avesta, Stuttgart 1886-1896) in the transliteration of
              avesta.org (Joseph H. Peterson, "AVESTA: Vendidad (Avestan)",
              https://www.avesta.org/vendidad/vd.htm). No license is stated on the page; the
              text is a transcription of a public-domain edition. Abbreviations ("...") are
              kept as given. Fargard 1 paragraphs are renumbered to Geldner's numbering used
              by Darmesteter's 2nd edition (avesta.org 2-20 = Geldner 3-21); Fargard 2 keeps
              the avesta.org numbers, which already agree with Geldner.
  4. ENGLISH  James Darmesteter, The Zend-Avesta, Part I: The Vendidad, Sacred Books of the
              East vol. 4, 2nd ed. (Oxford 1895), public domain; transcription validated on
              English Wikisource ("Sacred Books of the East/Volume 4/Fargard I" and
              "Fargard II", pages 99-119 of the djvu), CC BY-SA 4.0. Footnotes are omitted.

Usage:  python3 scripts/import_vendidad.py
"""

import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "vendidad"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "vendidad"
PUB_DIR = ROOT / "translations" / "published"
COLL_FILE = ROOT / "data" / "collections" / "vendidad.json"
TODAY = date.today().isoformat()
KEY = "vendidad"
PREFIX = "verified-vendidad-"
OPENN = "https://openn.library.upenn.edu/Data/0032/ms_or_320"
OPENN_HTML = "https://openn.library.upenn.edu/Data/0032/html/ms_or_320.html"
UA = {"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"}
SHELF = "Columbia University, Rare Book & Manuscript Library, MS Or 320"

# fol. -> OPenn image index (from the TEI facsimile list)
FARGARDS = [
    {
        "n": 1, "slug": "fargard-1", "folios": ["60r", "60v", "61r", "61v", "62r", "62v", "63r", "63v"],
        "title": "Vendidad, Fargard 1: the sixteen lands, beginning with Airyana Vaejah",
        "start_note": ("fol. 60r: two red lines in Avestan script, then four lines of Persian verse in nasta'liq which name the book "
                       "(که وندیداد نامش, 'whose name is Vendidad') and ask to be taught 'the first fargard' (ورگرد اول), then a red line "
                       "with rosettes; the Avestan text of Fargard 1 begins in the first black line below it"),
        "end_note": ("fol. 63v: the Avestan text of Fargard 1 ends in line 4 with a closing formula partly in red and a rosette, "
                     "followed by a row of red rosettes and three lines of Persian verse in red introducing 'the second fargard' "
                     "(به ورگرد دویم), 'which tells the story of Jamshid' (احوال جمشید)"),
        "geldner_map": "fargard1",
    },
    {
        "n": 2, "slug": "fargard-2", "folios": ["63v", "64r", "64v", "65r", "65v", "66r", "66v", "67r", "67v", "68r", "68v",
                                                "69r", "69v", "70r", "70v", "71r", "71v"],
        "title": "Vendidad, Fargard 2: Yima, the spreading of the earth, and the vara",
        "start_note": ("fol. 63v: below the red Persian verses introducing the second fargard (ورگرد دویم ... احوال جمشید) and a red "
                       "line with rosettes, the Avestan text of Fargard 2 fills the last eight lines of the page"),
        "end_note": ("fol. 71v: the Avestan text of Fargard 2 ends above a row of red rosettes, which is followed by three lines of "
                     "Persian verse whose first line speaks of reading the third fargard (سیوم, 'third')"),
        "geldner_map": "same",
    },
]


# Transcription slips in the Wikisource text, each checked against the printed page of the
# 1895 edition (Wikisource/Commons djvu page image, page number given).
ERRATA = {
    1: [("Bâkhtri", "Bâkhdhi", "djvu p. 103 = printed p. 5, para. 8")],
    2: [("O Zarathusra, replied", "O Zarathustra, replied", "djvu p. 109 = printed p. 11, para. 3"),
        ("son of Vivanghat", "son of Vîvanghat", "djvu pp. 110-111 = printed pp. 12-13, paras. 9 and 13"),
        ("Airyrana", "Airyana", "djvu p. 113 = printed p. 15, para. 21"),
        ("the seals of sheep", "the seeds of sheep", "djvu p. 116 = printed p. 18, para. 33")],
}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def tei_index():
    s = (SRC / "ms_or_320_TEI.xml").read_text(encoding="utf-8")
    out = {}
    for n, body in re.findall(r'<surface[^>]*n="([^"]*)"[^>]*>(.*?)</surface>', s, re.S):
        web = re.findall(r'url="(web/[^"]+)"', body)
        if web:
            out[n.strip()] = (web[0], int(re.findall(r"_(\d{4})_web", web[0])[0]))
    return out


def scan(folio, idx):
    web, img = idx[folio]
    name = f"ms-or-320-f{int(folio[:-1]):03d}{folio[-1]}.jpg"
    out = SCAN_DIR / name
    if not out.exists():
        cache = SRC / "web" / Path(web).name
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(fetch(f"{OPENN}/data/{web}"))
        SCAN_DIR.mkdir(parents=True, exist_ok=True)
        Image.open(cache).convert("RGB").save(out, quality=85)
    return f"{KEY}/{name}", img


# ----------------------------------------------------------------------------- Avestan (avesta.org)

def avestan(fargard):
    s = (SRC / "avesta_org" / "vd.htm").read_bytes().decode("utf-8", "replace")
    t = html.unescape(re.sub(r"<[^>]+>", "", s))
    a = t.find(f"Fargard {fargard}.")
    b = t.find(f"Fargard {fargard + 1}.")
    block = t[a:b]
    paras, cur = [], None
    for line in block.split("\n"):
        l = line.strip()
        m = re.match(r"^(\d+(?:-\d+)?)$", l)
        if m:
            cur = [m.group(1), []]
            paras.append(cur)
            continue
        if cur is not None and l:
            cur[1].append(l)
    return [(n, " ".join(ls)) for n, ls in paras]


# ----------------------------------------------------------------------------- English (Wikisource)

def ws_clean(t):
    t = re.sub(r"<noinclude>.*?</noinclude>", "", t, flags=re.S)
    t = re.sub(r"<ref[^>/]*/>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<section[^>]*/>", "", t)
    for _ in range(4):
        t = re.sub(r"\{\{hwe\|[^|}]*\|([^}]*)\}\}", "", t)
        t = re.sub(r"\{\{hws\|[^|}]*\|([^}]*)\}\}", r"\1", t)
        t = re.sub(r"\{\{(?:sp|smaller|larger|sc|asc|polytonic|nowrap|uc)\|([^{}]*)\}\}", r"\1", t)
        t = re.sub(r"\{\{(?:gap|rule|nop|clear)[^{}]*\}\}", " ", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    return t.replace("''", "")


def english(fargard):
    pages = json.loads((SRC / "sbe4" / "sbe4_pages_95_129.json").read_text(encoding="utf-8"))
    sec = f"fargard {fargard}"
    rng = range(99, 109) if fargard == 1 else range(108, 120)
    parts = []
    for n in rng:
        raw = pages[str(n)]
        segs = re.findall(r'<section begin="%s"\s*/>(.*?)(?:<section end="%s"\s*/>|$)' % (sec, sec), raw, re.S)
        parts.append(" ".join(segs))
    # join the pages; a sentence that runs over a page break (the page ends with a {{hws}} hyphenation or without
    # closing punctuation, and the next begins with {{hwe}} or a lower-case word) is joined without a line break
    # (QC 2026-11-12: these joins had printed a stray <br> inside 2.14 and 2.40)
    joined = parts[0] if parts else ""
    for nxt in parts[1:]:
        a, b = joined.rstrip(), nxt.lstrip()
        if re.search(r"\{\{hws\|[^{}]*\}\}$", a) and b.startswith("{{hwe|"):
            joined = a + b
        elif re.search(r"[A-Za-z,;]$", a) and re.match(r"(?:<ref[^>]*>.*?</ref>)?\s*[a-z]", b, re.S):  # may open with a footnote
            joined = a + " " + b
        else:
            joined = joined + "\n" + nxt
    text = ws_clean(joined)
    start = text.find("1. Ahura Mazda spake") if fargard == 1 else text.find("1. Zarathustra asked")
    assert start > 0, fargard
    text = text[start:]
    # split into numbered paragraphs: "3 (5)." or "9." or "[32. ...]" at line start
    out = []
    for block in re.split(r"\n\s*\n", text):
        b = re.sub(r"\s+", " ", block).strip()
        if not b or b in ("II.", "{{c|II.}}") or re.fullmatch(r"\{\{c\|[IVX]+\.\}\}", b):
            continue
        m = re.match(r"^\[?(\d+)(?:\s*\(([\d\-, ]+)\)[.,]?|[.,])\s*(.*)$", b)
        if m:
            out.append([m.group(1), m.group(3).rstrip("]") if b.startswith("[") else m.group(3), b.startswith("[")])
        else:
            assert out, b[:80]
            out[-1][1] += "<br>" + b
    for para in out:
        for wrong, right, where in ERRATA.get(fargard, []):
            if wrong in para[1]:
                para[1] = para[1].replace(wrong, right)
    for wrong, right, where in ERRATA.get(fargard, []):
        assert not any(wrong in p[1] for p in out), wrong
    return out


def build():
    idx = tei_index()
    entries, rows = [], []
    for fg in FARGARDS:
        av = avestan(fg["n"])
        en = english(fg["n"])
        if fg["geldner_map"] == "fargard1":
            def gnum(n):
                k = int(n)
                return str(k if k == 1 else k + 1)
            av = [(gnum(n), t) for n, t in av]
        orig = "<br>".join(f"<sup>{n}</sup>{t}" for n, t in av)
        eng = "<br>".join(f"<sup>{n}</sup>{'[' if br else ''}{t}{']' if br else ''}" for n, t, br in en)
        scans = [scan(f, idx) for f in fg["folios"]]
        scan_pages = [p for p, _ in scans]
        first, last = fg["folios"][0], fg["folios"][-1]
        note = (f"{SHELF}, fol. {first}-{last} (OPenn images {scans[0][1]}-{scans[-1][1]}). Checked on the images: "
                f"{fg['start_note']}; {fg['end_note']}. The fargard therefore occupies exactly these {len(scan_pages)} pages, "
                "in this order. The opening words of the pages inside the fargard could not be confirmed on the images, so the "
                "paragraphs are not assigned to single pages: all of them are on these pages together. As a Vendidad Sade, the "
                "manuscript adds liturgical formulas in red at the end of the fargard.")
        if fg["n"] == 2:  # QC 2026-11-12
            note += (" Short forms: the Avestan text used (avesta.org's transliteration of Geldner) gives paragraphs 12-14 as one "
                     "abbreviated line, 'âat ýimâi xshathrâi xshvash-satô-zima hañjaseñti, âat hê îm zå bvat perene ... mashyânãmca', "
                     "because they repeat the wording of paragraphs 8-10 with 'six hundred winters' in place of 'three hundred'; "
                     "the English gives paragraphs 12, 13 and 14 in full. Paragraph 43 is likewise abbreviated in the Avestan "
                     "('dâtare ... ashâum') and given in full in the English. The Avestan is shown as the source gives it and is "
                     "not expanded here; the manuscript pages carry the passage, but where it stands on them could not be "
                     "confirmed (see above).")
        if fg["n"] == 1:
            note += (" Darmesteter notes that clause 2 of this fargard in Vendidad Sade manuscripts consists of Avestan quotations "
                     "from the Pahlavi commentary; that clause is not in the Avestan text shown and is not translated.")
        tid = f"{PREFIX}{fg['slug']}"
        sec_id = f"{av[0][0]}-{av[-1][0].split('-')[-1]}"
        section = {
            "section": sec_id,
            "original_ref": f"Vd {fg['n']}.{sec_id} (Geldner); {SHELF} fol. {first}-{last}",
            "original_text": orig,
            "text": eng,
            "scan_pages": scan_pages,
            "scan_note": note,
        }
        if fg["n"] == 1:
            intro = (
                "<p>The Vendidad (Avestan Vīdaēvadāta, 'law against the demons') is the Zoroastrian book of purity law, "
                "written in Young Avestan and set as a dialogue between Ahura Mazda and Zarathustra. Its first chapter "
                "(fargard) lists sixteen lands that Ahura Mazda created as good places to live. The first of them is Airyana "
                "Vaejah (Airyanem Vaējō) by the river Vanguhi Daitya, a land of ten winter months and two summer months. "
                "For each land Angra Mainyu creates a counter-plague. Several of the later lands can be identified with "
                "regions of eastern Iran and its neighbours, such as Sughdha (Sogdiana), Mouru (Merv), Bakhdhi (Balkh), "
                "Haroyu (Herat), Harahvaiti (Arachosia) and Hapta Hindu (the Punjab).</p>"
            )
        else:
            intro = (
                "<p>The second fargard of the Vendidad tells of Yima (Jamshid in Persian tradition), the first king. Ahura "
                "Mazda asks him to receive and carry the religion; Yima declines but agrees to rule, nourish and watch over "
                "the world. Three times the world becomes full, and three times Yima enlarges the earth. Ahura Mazda then "
                "warns him of a coming winter of deadly frost and snow, and orders him to build a vara, an enclosure "
                "'long as a riding-ground on every side', into which he is to bring the seeds of the best men and women, of "
                "animals, plants and fires. The chapter describes the vara and its self-created and created lights.</p>"
            )
        intro += (
            f"<p>The manuscript shown is {SHELF}, a Vendidad Sade (the Vendidad in pure Avestan, arranged for recitation "
            "with the Yasna and Visperad), 322 leaves, copied at Surat by Herbed Darab Framroz Minochehr and dated 1131 of "
            "the Yazdegird era (1762 CE) in its colophon. Each fargard is preceded by Persian verses that name it; these "
            f"headings fix the fargard to fol. {first}-{last}. The pages between the headings were not divided further, so "
            "the whole fargard forms one section that lists all its pages.</p>"
            "<p>The Avestan text is Geldner's edition in the avesta.org transliteration; the English is James Darmesteter's "
            "translation (2nd edition, 1895), without his footnotes.</p>"
        )
        entry = {
            "id": tid, "slug": tid, "title": fg["title"],
            "language": "Avestan (transliteration) / English",
            "source": f"{SHELF} (Surat, 1762; OPenn, Public Domain Mark) + Geldner's Avestan text (avesta.org) + Darmesteter's English (SBE 4, 1895; Wikisource)",
            "description": (f"Fargard {fg['n']} of the Vendidad in Avestan and English, shown on the pages of a Vendidad Sade "
                            "manuscript copied at Surat in 1762 (Columbia University MS Or 320)."),
            "introduction": intro,
            "translator_notes": [
                "Avestan: Geldner's text in the transliteration of avesta.org, which writes some repeated passages in short form with '...'.",
                ("Paragraph numbers follow Geldner, as in Darmesteter's 2nd edition. For Fargard 1 the avesta.org numbers 2-20 have been "
                 "changed to Geldner's 3-21; Geldner's 1.2 is not in the avesta.org text.") if fg["n"] == 1 else
                ("Darmesteter numbers paragraphs 6-7 together as 7 and 20-21 together as 21, and gives 32 in brackets; the Avestan keeps "
                 "Geldner's separate numbers."),
                "English: James Darmesteter, The Zend-Avesta, Part I: The Vendidad, Sacred Books of the East 4, 2nd ed. (1895); footnotes omitted.",
            ] + [f"Corrected against the printed page ({w}): '{a}' to '{b}'." for a, b, w in ERRATA[fg["n"]]],
            "translation": [section],
            "verification": {
                "scan_source": f"Columbia University Rare Book & Manuscript Library via OPenn: {OPENN_HTML}",
                "scan_license": "Creative Commons Public Domain Mark 1.0 (as stated by Columbia University on OPenn)",
                "scan_manuscript": f"{SHELF} - FOLIO, Vendidad Sade, Surat, 1131 AY (1762 CE), scribe Herbed Darab Framroz Minochehr",
                "scan_mapping": ("Fargard boundaries read on the images from the Persian verse headings that name each fargard (fol. 60r, "
                                 "63v, 71v). Page positions of individual paragraphs not confirmed, so each fargard is one section "
                                 "listing all its pages."),
                "scan_mapping_urls": [OPENN_HTML, f"{OPENN}/data/ms_or_320_TEI.xml"],
                "scan_local_paths": scan_pages,
                "original_text_source": "K. F. Geldner, Avesta: the sacred books of the Parsis (Stuttgart 1886-1896), Vendidad; transliteration by Joseph H. Peterson, avesta.org: https://www.avesta.org/vendidad/vd.htm",
                "original_text_license": "edition public domain; avesta.org digital transliteration, no license stated",
                "translation_source": "James Darmesteter, The Zend-Avesta Part I: The Vendidad, SBE 4, 2nd ed. (Oxford 1895), English Wikisource: https://en.wikisource.org/wiki/Sacred_Books_of_the_East/Volume_4/Fargard_I and /Fargard_II",
                "translation_license": "public domain (1895); Wikisource transcription CC BY-SA 4.0",
                "translator": "James Darmesteter (1895)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": fg["n"], "title": fg["title"], "author_id": "zarathustra",
            "language": "Avestan", "era": "Axial Age", "tradition": "zoroastrian", "category": "sacred-text",
            "date_approx": "Young Avestan text, first millennium BCE (date disputed); manuscript 1762 CE (Surat)",
            "century": -5,
            "source": entry["source"], "description": entry["description"],
            "themes": ["avesta", "vendidad", "zoroastrian", "airyana-vaejah" if fg["n"] == 1 else "yima", "persia", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": f"MS Or 320, fol. {f}"} for p, f in zip(scan_pages, fg["folios"])]},
        })
        entries.append(entry)
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Vendidad (Fargards 1-2)",
            "group": "Persia", "date_sort": -500,
            "author_name": "Avesta, Vendidad (Young Avestan); manuscript Surat 1762",
            "source_url": OPENN_HTML,
            "critical_edition": "Geldner, Avesta (1886-1896), avesta.org transliteration",
            "translator_name": "James Darmesteter (1895)",
            "original_lang_label": "Avestan · Geldner (transliteration)",
            "original_lang_code": "ae",
            "edition_label": "",
            "search_terms": "vendidad videvdad avesta zoroastrian airyana vaejah yima vara jamshid sixteen lands",
            "description": ("The first two chapters of the Vendidad, the Zoroastrian law book: the sixteen lands created by Ahura "
                            "Mazda, beginning with Airyana Vaejah, and the story of Yima and his vara, shown on a Vendidad Sade "
                            "manuscript copied at Surat in 1762."),
        },
        "texts": rows,
    }
    COLL_FILE.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(entries)} entries")


if __name__ == "__main__":
    build()
