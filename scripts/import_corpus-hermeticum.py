#!/usr/bin/env python3
"""
import_corpus-hermeticum.py: Corpus Hermeticum I (Poimandres), complete, each
section shown on the page of the oldest manuscript with page images.

Chain of evidence
  1. MANUSCRIPT
     Florence, Biblioteca Medicea Laurenziana, Plut. 71.33 (siglum A of the
     editions), paper, 14th century; the Hermetic treatises fill fols. 123-145v
     (Pinakes diktyon 16627). Images: BML Teca digitale (CONTENTdm) IIIF,
     https://cdm21059.contentdm.oclc.org/iiif/plutei:1210396/manifest.json
     (cached in data/sources/corpus-hermeticum/iiif/laur7133-manifest.json);
     access 'Pubblico'. Paris gr. 1220 is on Gallica, which refuses automated
     requests; Vat. gr. 951 is not online; Vat. gr. 237 is a microfilm.
  2. MAPPING  The first and last lines of each of the six pages (123r-125v)
     were read on the image and matched to the Greek; the words read are in
     PAGES and in each scan_note. The end of each page was checked against the
     start of the next. A section is linked to every page that carries part of it.
  3. GREEK    Gustav Parthey, Hermetis Trismegisti Poemander (Berlin 1854;
     public domain), pp. 1-18, from the proofread transcription on Greek
     Wikisource (pages 'Hermetis Trismegisti Poemander (1854).djvu/25-42', all
     at proofread level 3; revision ids cached with the text in
     wikisource-parthey-pp24-43.json; CC BY-SA 4.0). Parthey's section
     numbers (1-32) are the standard ones. Notes and apparatus are dropped.
  4. ENGLISH  G. R. S. Mead, Thrice-Greatest Hermes, vol. 2 (London and
     Benares: Theosophical Publishing Society, 1906; public domain), pp. 3-20,
     'Poemandres, the Shepherd of Men'. Text from the archive.org OCR of the
     Toronto copy (thricegreatesthe02hermuoft): page headings and footnotes
     removed, footnote numbers removed. It was compared word by word with the
     OCR of a second scan of the same printing (thricegreatesth02meadgoog);
     where they differ, the reading confirmed by the gnosis.org transcription
     was taken, and the remaining fixes are listed in FIX_ENG.

  CH XIII (the secret discourse on rebirth), added 2026-11-12, entry 'on-rebirth':
  5. MANUSCRIPT  same Laur. Plut. 71.33, fol. 141v (middle, red title) to 144r (middle, red title of
     CH XIV). First and last lines of the six pages read on the image (PAGES13).
  6. GREEK    Parthey 1854, cap. 13, pp. 114-128. Greek Wikisource has not transcribed these pages, and
     the archive.org OCR of the Greek is unusable, so the text was transcribed from the page images of
     archive.org poemander00trisgoog (leaves 140-154) and proofread line by line against them:
     data/sources/corpus-hermeticum/parthey/parthey1854-ch13.txt (one printed line per line, with
     Parthey's page and section numbers). Parthey's sections 1-22.
  7. ENGLISH  Mead 1906, vol. 2 pp. 219-233, from the same Toronto OCR; compared word by word with the
     OCRs of two other scans (thricegreatesth02meadgoog, afx0734.0002.001.umich.edu); OCR faults and the
     lacuna dots (checked on the page images pp. 222, 224, 225) are fixed in FIX13_ENG. The English is cut
     at the words translating the start of each of Parthey's sections (ENG13_CUTS); Mead's own numerals,
     which fall elsewhere at 8, 9 and 19, are removed.

Usage:
    python3 scripts/import_corpus-hermeticum.py
"""

import html as htmlmod
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image

KEY = "corpus-hermeticum"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()

MS = {
    "manifest": SRC / "iiif" / "laur7133-manifest.json",
    "short": "Laur. Plut. 71.33",
    "shelfmark": "Florence, Biblioteca Medicea Laurenziana, Plut. 71.33",
    "desc": ("Florence, Biblioteca Medicea Laurenziana, Plut. 71.33, paper, 14th century, 211 leaves; a philosophical miscellany "
             "(Petrus Hispanus, Proclus and others) with the Hermetic treatises on fols. 123-145v. It is manuscript A of the editions "
             "and the oldest dated witness of the Corpus Hermeticum. Owned by Marsilio Ficino and Angelo Poliziano (Pinakes diktyon 16627)."),
    "object": "https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/1210396",
    "holder": "Biblioteca Medicea Laurenziana, Teca digitale (IIIF)",
    "license": ("Images Biblioteca Medicea Laurenziana, Florence (Teca digitale; access 'Pubblico', no licence stated). "
                "Reproduced with credit for non-commercial reference use; by concession of the Ministero della Cultura."),
    "pinakes": "https://pinakes.irht.cnrs.fr/notices/cote/16627/",
    "width": 1800,
}

PAGES = [
    {"folio": "123r", "start": 1, "end": 7,
     "custom": ("Laur. Plut. 71.33 fol. 123r: below the red title 'Ἑρμοῦ τρισμεγίστου ποιμάνδρης' the text begins with a red initial: "
                "'Ἐννοίας μοί ποτε γενομένης περὶ τῶν ὄντων καὶ μετεωρισθείσης μοι τῆς διανοίας'. In the middle of the page (sections 4-5) the scribe left "
                "blank spaces in several lines where his exemplar was defective. The last line reads '... ἀναριθμήτοις ὂν καὶ κόσμον ἀπεριόριστον "
                "γεγενημένον' (section 7).")},
    {"folio": "123v", "start": 7, "end": 14,
     "first": "καὶ περιίσχεσθαι τὸ πῦρ δυνάμει μεγίστῃ καὶ στάσιν ἐσχηκέναι κρατούμενον",
     "last": "ἀλόγων ζῴων ἔχων πᾶσαν ἐξουσίαν, διὰ τῆς ἁρμονίας παρέκυψεν, ἀναρρήξας",
     "extra": "Section 8 begins on line 2 ('ὡς δέ μου ἐν ἐκπλήξει ὄντος')."},
    {"folio": "124r", "start": 14, "end": 18,
     "first": "τὸ κράτος, καὶ ἔδειξε τῇ κατωφερεῖ φύσει τὴν καλὴν τοῦ θεοῦ μορφήν",
     "last": "πάντα τὰ κτίσματα καὶ δημιουργήματα, καὶ ἀναγνωρισάτω ὁ ἔννους"},
    {"folio": "124v", "start": 18, "end": 23,
     "first": "ἑαυτὸν ὄντα ἀθάνατον, καὶ τὸν αἴτιον τοῦ θανάτου ἔρωτα, καὶ πάντα τὰ ὄντα",
     "last": "σκοτομαχῶν· καὶ τοῦτον βασανίζει, καὶ ἐπ’ αὐτὸν πῦρ ἐπὶ τὸ πλεῖον αὐξάνει",
     "extra": "Section 19 begins on line 2 ('τοῦτο εἰπόντος, ἡ πρόνοια διὰ τῆς εἱμαρμένης'); the page ends with the end of section 23."},
    {"folio": "125r", "start": 24, "end": 29,
     "first": "εὖ μοι πάντα ὡς ἐβουλόμην ἐδίδαξας, ὦ νοῦς· ἔτι δέ μοι εἰπὲ περὶ τῆς ἀνόδου",
     "last": "κάλουν διδαχθῆναι, ἑαυτοὺς πρὸ ποδῶν μου ῥίψαντες· ἐγὼ δὲ ἀναστήσας"},
    {"folio": "125v", "start": 29, "end": 32,
     "custom": ("Laur. Plut. 71.33 fol. 125v: line 1 'αὐτούς, καθοδηγὸς ἐγενόμην τοῦ γένους, τοὺς λόγους διδάσκων' (section 29); "
                "section 30 begins in line 5 ('ἐγὼ δὲ τὴν εὐεργεσίαν τοῦ Ποιμάνδρου'), section 31 in line 11 ('ἅγιος ὁ θεὸς ὁ πατὴρ τῶν ὅλων') "
                "and section 32 at the start of line 18 ('αἰτουμένῳ τὸ μὴ σφαλῆναι'). The treatise ends in line 22 with "
                "'... καθὼς παρέδωκας αὐτῷ τὴν πᾶσαν ἐξουσίαν', followed on the same line by the red title of the next treatise.")},
]

INTRO = (
    "<p>The <em>Poimandres</em> is the first treatise of the Corpus Hermeticum, a collection of Greek dialogues and sermons ascribed to Hermes Trismegistus, "
    "written in Roman Egypt probably in the 2nd or 3rd century AD. The narrator falls into a trance and meets Poimandres (in Mead's translation 'Man-Shepherd, Mind of all-masterhood'), "
    "who shows him in a vision how the world came to be: light and a holy Word (Logos) come out of the divine Mind, a second creator-Mind makes the seven planetary governors, "
    "and the archetypal Man, made in the image of the Father, descends through the spheres, falls in love with Nature and becomes mortal in body but immortal in essence (sections 12-15). "
    "Poimandres then teaches the way back: at death the soul gives up its passions to each of the seven zones, enters the eighth nature, hymns the Father with the Powers, "
    "which is 'the good end for those who have gained Gnosis' (26); the Greek word for the end is <em>theothenai</em>, 'to be made god' (Mead: 'to be made one with God'). The narrator begins to preach to mankind and closes with a hymn, 'Holy art Thou, O God, the universals' Father' (31-32).</p>\n\n"
    "<p>The pages shown are from Florence, Biblioteca Medicea Laurenziana, Plut. 71.33, a paper manuscript of the 14th century (manuscript A of the editions), "
    "the oldest copy of the Corpus Hermeticum with page images online; it later belonged to Marsilio Ficino, whose Latin translation of 1463 made the Hermetica famous in the Renaissance. "
    "The Poimandres fills fols. 123r-125v. Each section below is one of the 32 standard sections, linked to the page or pages that carry its words, "
    "identified by reading the first and last lines of each page on the image. "
    "The Greek is Gustav Parthey's edition of 1854, which differs from this manuscript and from later editions in places (in section 5 the manuscript has blank spaces where its exemplar was damaged). "
    "The English is G. R. S. Mead's translation of 1906, made from Reitzenstein's text of 1904, so a few phrases do not match Parthey's Greek word for word.</p>"
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def canvases():
    m = json.loads(MS["manifest"].read_text(encoding="utf-8"))
    out = {}
    for c in m["sequences"][0]["canvases"]:
        lab = c["label"].replace("Carta: ", "")
        sid = c["images"][0]["resource"]["service"]["@id"]
        out[lab] = {"service": sid, "id": sid.rsplit(":", 1)[1]}
    return out


def get_scan(folio, cv):
    path = SCAN_DIR / f"laur7133-f{folio}.jpg"
    if not path.exists():
        img = Image.open(io.BytesIO(fetch(f"{cv[folio]['service']}/full/{MS['width']},/0/default.jpg"))).convert("RGB")
        img.save(path, quality=85)
    return path


def viewer(folio, cv):
    return f"https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/{cv[folio]['id']}"


# ---------------------------------------------------------------------------
# Greek: Parthey on Wikisource
def parthey_sections():
    d = json.loads((SRC / "wikisource-parthey-pp24-43.json").read_text(encoding="utf-8"))
    chunks = []
    for n in sorted(d, key=int):
        m = re.search(r'<section begin="text"\s*/>(.*?)<section end="text"\s*/>', d[n]["content"], re.S)
        if m:
            chunks.append(m.group(1))
    s = " ".join(chunks)
    for _ in range(10):
        s2 = re.sub(r"\{\{Σημείωση\|αρ=[^|{}]*\|([^{}]*)\}\}", r"\1", s)
        s2 = re.sub(r"\{\{αρίθμηση Burnet\|p(\d+)\|\d+\}\}", r" §§\1§§ ", s2)
        s2 = re.sub(r"\{\{σλβα\|[^|{}]*\|([^{}]*)\}\}", r"\1", s2)      # word split over a page: first half -> whole word
        s2 = re.sub(r"\{\{σλβτ\|[^{}]*\}\}", "", s2)                      # second half on the next page: dropped
        s2 = re.sub(r"\{\{(?:κσγ|larger|smaller|c)\|([^{}]*)\}\}", r"\1", s2)
        s2 = re.sub(r"\{\{(?:gap|nop)(?:\|[^{}]*)?\}\}", " ", s2)
        if s2 == s:
            break
        s = s2
    assert "{{" not in s, re.findall(r"\{\{[^}]*", s)[:5]
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;·:])", r"\1", s)
    parts = re.split(r" ?§§(\d+)§§ ?", s)
    secs = [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]
    return dict(secs[:32])   # CH I = the first 32 sections; CH II follows


# ---------------------------------------------------------------------------
# English: Mead 1906, archive.org OCR
HDR = re.compile(r"(THRICE.?G.?.?.?TEST|Hosted by Google|SHEPHERD\s+OF\s+MEN|Thrice-Greatest|Shepherd of Men)", re.I)
FIX_ENG = [
    ("IT chanced", "It chanced"), ("Keason", "Reason"),
    ('¶, energy, and realization. ¶ That is " a-sexual " but having the potentiality of both sexes. ¶ For the various suggestions for filling up this lacuna, see R. in loc.; and for that of Keil, see R. 367. ¶ Sc. as well as Nature.', ""),
    ("the J generation", "the generation"), ("Miher.", "Æther."), ("Eight was thy", "Right was thy"),
    ("that them [only] happen st", "that thou [only] happen'st"), ("Above.as", "Above as"), ("Kashness", "Rashness"),
    ("gavesfc", "gavest"), ("Man -Shepherd", "Man-Shepherd"), ("[Nature *]", "[Nature]"), ("well* am", "well am"),
    ("drink.*", "drink."),
]


def mead_sections():
    lines = (SRC / "mead" / "mead1906-v2_djvu.txt").read_text(encoding="utf-8", errors="replace").split("\n")
    i = next(k for k, l in enumerate(lines) if re.search(r"^1\.\s+IT\s+chanced", l))
    j = next(k for k, l in enumerate(lines) if k > i and re.search(r"^COMMENTA", l))
    pages = [[]]
    for l in lines[i:j]:
        s = l.strip()
        if HDR.search(s) and len(s) < 70 and (re.search(r"\d", s) or s.upper() == s):
            pages.append([])
            continue
        pages[-1].append(s)
    kept = []
    for p in pages:   # footnotes: from the first line after a blank line that starts with a footnote number
        cut = len(p)
        for k, s in enumerate(p):
            if k > 0 and p[k - 1] == "" and re.match(r"^([1lI]|\^|\*)\s{1,4}\S", s) and not re.match(r"^1\.\s", s):
                cut = k
                break
        q = p[:cut]
        while q and q[0] == "":
            q.pop(0)
        while q and q[-1] == "":
            q.pop()
        kept.extend(q)
    t = "\n".join(kept)
    g = (SRC / "mead" / "hermes1.html").read_text(encoding="latin-1")
    keep = set(w.lower() for w in re.findall(r"\b\w+-\w+(?:-\w+)*\b", htmlmod.unescape(re.sub(r"<[^>]+>", " ", g))))
    t = re.sub(r"(\w+)-[ \t]*\n[ \t]*(\w+)",
               lambda m: m.group(1) + "-" + m.group(2) if m.group(2)[:1].isupper() or (m.group(1) + "-" + m.group(2)).lower() in keep else m.group(1) + m.group(2), t)
    t = re.sub(r"\n\s*\n+", " ¶ ", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(?<=\w)- (?=[A-Z])", "-", t)
    t = re.sub(r"(?<=[A-Za-z\.,;:\)\]'’\"—?!])\d{1,2}(?=[\s,;:.]|$)", "", t)   # footnote numbers on words
    t = re.sub(r"(?<=\s)([1-9]|l|\*)(?=\s)", " ", t)                           # free-standing footnote marks
    t = re.sub(r"(?<=\s)0(?=\s)", "O", t).replace("^", " ").replace(" ,", ",")
    t = re.sub(r"\s+([:;?!.,])", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    for a, b in FIX_ENG:
        assert a in t, a
        t = t.replace(a, b)
    t = re.sub(r"\s+", " ", t).replace(" ¶ ¶ ", " ¶ ")
    parts = re.split(r"(?:^| )(\d{1,2})\. (?=[A-Z\[“\"‘'(])", t)
    secs = {parts[k]: parts[k + 1].strip() for k in range(1, len(parts), 2)}
    assert list(secs) == [str(n) for n in range(1, 33)], list(secs)
    return secs


def to_html(s):
    s = htmlmod.escape(s, quote=False)
    s = re.sub(r"\s*¶\s*", "<br>", s).strip()
    return re.sub(r"^(<br>)+|(<br>)+$", "", s)


def page_note(p, cv):
    if p.get("custom"):
        return p["custom"] + " Viewer: " + viewer(p["folio"], cv)
    s = (f"{MS['short']} fol. {p['folio']} runs from '{p['first']}' on its first line (section {p['start']}) "
         f"to '{p['last']}' on its last line (section {p['end']}).")
    if p.get("extra"):
        s += " " + p["extra"]
    return s + " Viewer: " + viewer(p["folio"], cv)


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cv = canvases()
    grc = parthey_sections()
    eng = mead_sections()
    files = {p["folio"]: get_scan(p["folio"], cv) for p in PAGES}
    sections = []
    for i in range(1, 33):
        n = str(i)
        pages = [p for p in PAGES if p["start"] <= i <= p["end"]]
        if len(pages) == 1:
            note = f"On {MS['short']} fol. {pages[0]['folio']}. " + page_note(pages[0], cv)
        else:
            note = (f"Starts on fol. {pages[0]['folio']} and continues on fol. {pages[-1]['folio']} (page break inside this section). "
                    + " ".join(page_note(p, cv) for p in pages))
        note += " Checked on the images. The Greek shown is Parthey's edition, not a transcription of this manuscript."
        sections.append({
            "section": n,
            "original_ref": f"Corpus Hermeticum I.{n}; {MS['short']} fol. " + ", ".join(p["folio"] for p in pages),
            "original_text": to_html(grc[n]),
            "text": to_html(eng[n]),
            "scan_pages": [f"{KEY}/{files[p['folio']].name}" for p in pages],
            "scan_note": note,
        })
    tid = PREFIX + "poimandres"
    folios = [p["folio"] for p in PAGES]
    title = "Corpus Hermeticum I: Poimandres"
    desc = ("The first Hermetic treatise: the vision of Poimandres, the divine Mind, on the making of the world, the fall of the archetypal Man "
            "and the soul's ascent through the seven spheres to God, shown complete on the 14th-century Florence manuscript Laur. Plut. 71.33.")
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Greek (Parthey 1854) / English (G. R. S. Mead, 1906)",
        "source": f"{MS['shelfmark']} fol. 123r-125v ({MS['holder']}) + Parthey's Greek (1854, Wikisource) + G. R. S. Mead's English (1906)",
        "description": desc,
        "introduction": INTRO,
        "translator_notes": [
            "Greek: Gustav Parthey, Hermetis Trismegisti Poemander (Berlin: Nicolai, 1854), pp. 1-18, transcription proofread on Greek Wikisource. Parthey's apparatus is not shown.",
            "English: G. R. S. Mead, Thrice-Greatest Hermes, vol. 2 (1906), pp. 3-20. Mead's footnotes are not shown; his square brackets mark words he supplied, and '...' marks a gap in the Greek. Paragraph breaks inside a section follow the printed page, except where a paragraph starts at the top of a page.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"{MS['holder']}: {MS['object']} (folios {', '.join(folios)}); IIIF manifest https://cdm21059.contentdm.oclc.org/iiif/plutei:1210396/manifest.json",
            "scan_license": MS["license"],
            "scan_manuscript": MS["desc"],
            "scan_mapping": "First and last lines of every page read on the image and matched to the Greek (words recorded in each scan_note); end of each page checked against the start of the next; folio range of the Hermetica from Pinakes diktyon 16627.",
            "scan_mapping_urls": [MS["pinakes"]] + [viewer(f, cv) for f in folios],
            "scan_local_paths": [f"{KEY}/{files[f].name}" for f in folios],
            "original_text_source": "G. Parthey, Hermetis Trismegisti Poemander (Berlin 1854), via Greek Wikisource https://el.wikisource.org/wiki/Ποιμάνδρης (page transcriptions at proofread level 3; revision ids stored in data/sources/corpus-hermeticum/wikisource-parthey-pp24-43.json)",
            "original_text_license": "edition public domain (1854); Wikisource transcription CC BY-SA 4.0",
            "translation_source": "G. R. S. Mead, Thrice-Greatest Hermes, vol. 2 (London: Theosophical Publishing Society, 1906), pp. 3-20, archive.org thricegreatesthe02hermuoft (OCR checked against thricegreatesth02meadgoog)",
            "translation_license": "public domain (published 1906; Mead died 1933)",
            "translator": "G. R. S. Mead (1906)",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": 1, "title": title, "author_id": "hermes-trismegistus",
        "language": "Greek", "era": "Imperial", "tradition": "hermetic", "category": "sacred-text",
        "date_approx": "c. 2nd-3rd century AD (composition); manuscript 14th century", "century": 2,
        "source": entry["source"], "description": desc,
        "themes": ["hermetica", "corpus-hermeticum", "poimandres", "nous", "logos", "ascent-of-the-soul", "deification", "theosis", "gnosis", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[f].name}", "caption": f"{MS['short']} fol. {f}"} for f in folios]},
    }
    row13 = build_ch13(cv)
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Corpus Hermeticum",
            "group": "Greece", "date_sort": 200,
            "author_name": "Hermes Trismegistus (attributed), 2nd-3rd century AD; Florence manuscript Laur. Plut. 71.33",
            "source_url": MS["object"],
            "critical_edition": "Parthey, Hermetis Trismegisti Poemander (1854): CH I via Greek Wikisource, CH XIII transcribed from the 1854 page images",
            "translator_name": "G. R. S. Mead (1906)",
            "original_lang_label": "Greek · Parthey",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "corpus hermeticum hermes trismegistus poimandres poemandres pimander nous logos ascent become god rebirth regeneration palingenesia tat secret hymn ficino laurenziana mead",
            "description": "The Hermetic Poimandres (CH I), the vision of the divine Mind and of the soul's ascent to become God, and the secret discourse on rebirth (CH XIII), shown section by section on the oldest manuscript of the Corpus Hermeticum, with Parthey's Greek and G. R. S. Mead's English.",
        },
        "texts": [row, row13],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections)")


# ---------------------------------------------------------------------------
# CH XIII (the secret discourse on rebirth), added 2026-11-12
# ---------------------------------------------------------------------------
P13_FILE = SRC / "parthey" / "parthey1854-ch13.txt"
# Laur. Plut. 71.33: CH XIII runs from the middle of fol. 141v to the middle of fol. 144r. 'anchor' = the words of
# Parthey's text with which the page's first line begins (to place the page break); first/last = read on the image.
PAGES13 = [
    {"folio": "141v", "anchor": None,
     "custom": ("Laur. Plut. 71.33 fol. 141v: in the middle of the page CH XII ends ('... θρησκεία δὲ τοῦ θεοῦ μία ἐστί, μὴ εἶναι κακόν'); "
                "below it stands the red title 'Ἑρμοῦ τρισμεγίστου πρὸς τὸν υἱὸν Τὰτ περὶ παλιγγενεσίας καὶ σιγῆς ἐπαγγελίας' (without the words "
                "'ἐν ὄρει λόγος ἀπόκρυφος' of Parthey's title), and CH XIII begins with a red initial: 'Ἐν τοῖς γενικοῖς, ὦ πάτερ, αἰνιγματωδῶς καὶ οὐ τηλαυγῶς ἔφρασας'; "
                "a later hand has written '13.' in the margin. The last line reads 'ἐξ οἵας μήτρας ἄνθρωπος ἐγεννήθη· σπορᾶς δὲ ποίας. ὦ τέκνον' "
                "(end of section 1 and the first words of section 2; the manuscript has no 'ὕλης καὶ').")},
    {"folio": "142r", "anchor": "σοφία νοερὰ ἐν σιγῇ",
     "first": "σοφία νοερὰ ἐν σιγῇ· καὶ ἡ σπορὰ τὸ ἀληθινὸν ἀγαθόν. τίνος σπείραντος, ὦ πάτερ;",
     "last": "φερὲς ὡς γῆ· καὶ ὑγρὸν ὡς ὕδωρ· καὶ σύμπνοον ὡς ἀήρ· πῶς αἰσθητῶς"},
    {"folio": "142v", "anchor": "αὐτὸ νοήσεις, τὸ μὴ",
     "first": "αὐτὸ νοήσεις, τὸ μὴ σκληρόν, τὸ μὴ ὑγρόν, τὸ ἀσφίγκτον, τὸ μὴ διαλυόμενον",
     "last": "τῆς παλιγγενεσίας τὸν τρόπον. τῆς δεκάδος παραγινομένης, ὦ τέκνον"},
    {"folio": "143r", "anchor": "συνετέθη νοερὰ γένεσις",
     "first": "συνετέθη νοερὰ γένεσις· καὶ τὴν δωδεκάτην ἐξελαύνει· καὶ ἐθεωρήθημεν",
     "last": "ὁ ποιμάνδρης ἐθέσπισε, τέκνον· καλῶς σπεύδεις λῦσαι τὸ σκῆνος"},
    {"folio": "143v", "anchor": "κεκαθαρμένος γάρ. ὁ Ποιμάνδρης",
     "first": "κεκαθαρμένος γάρ· ὁ ποιμάνδρης ὁ τῆς αὐθεντίας νοῦς, πλέον μοι τῶν ἐγ(γεγραμμένων)",
     "last": "λογικὴν θυσίαν· τὸ πᾶν τὸ ἐν ἡμῖν σῶζε ζωή· φώτιζε φῶς· πνεῦμα θε(έ)",
     "extra": ("In the upper half of the page, after 'ἡσύχασον, ὦ τέκνον', the scribe wrote the heading 'ὑμνῳδία' in red at the end of the line; "
               "the hymn (section 17) begins on the next line with a red initial: 'Πᾶσα φύσις κόσμου προσδεχέσθω τοῦ ὕμνου τὴν ἀκοήν'.")},
    {"folio": "144r", "anchor": "λόγον γὰρ τὸν σὸν",
     "first": "λόγον γὰρ τὸν σὸν ποιμαίνει ὁ νοῦς· πνευματοφόρε δημιουργέ· σὺ ὁ θεός· ὁ σὸς",
     "last": None,
     "extra": ("CH XIII ends in the middle of the page: 'νοερῶς ἔγνως σεαυτὸν καὶ τὸν πατέρα τὸν ἡμέτερον', followed on the same line by the red title "
               "of CH XIV, 'Ἑρμοῦ πρὸς Ἀσκληπιόν' (a later hand has written '14' in the margin).")},
]

# English: G. R. S. Mead's text cut at the words that translate the first words of each of Parthey's sections.
# Mead (following Reitzenstein) numbers 8, 9 and 19 at other places; his numerals are removed.
ENG13_CUTS = {
    1: "Tat. [Now] in the General Sermons", 2: "Hermes. Wisdom that understands", 3: "Tat. Thou sayest things impossible",
    4: "Tat. Into fierce frenzy", 5: "Tat. Now hast thou brought me", 6: "Tat. What then is true",
    7: "Tat. I am incapable of this", 8: "But they depart (although not all at once)", 9: "The Power that follows Joy do I invoke",
    10: "Thou knowest [now], my son, the manner of Rebirth", 11: "Tat. By God made steadfast", 12: "Her. This dwelling-place",
    13: "Tat. Father, I see the All", 14: "Tat. Tell me, O father", 15: "Tat. I would, O father, hear the Praise-giving",
    16: "Tat. Father, I wish to hear", 17: "Let every nature of the World", 18: "Ye Powers that are within me",
    19: "Thus cry the Powers in me", 20: "[For] Thou art God", 21: "Her. But not unheedfully", 22: "Her. Happy am I, my son",
}
# OCR faults in the Toronto scan (mead1906-v2_djvu.txt), settled by the two other OCRs of the same printing
# (thricegreatesth02meadgoog, afx0734.0002.001.umich.edu) and, for the lacunae, by the page images (pp. 222, 224, 225).
FIX13_ENG = [
    ("Eebirth", "Rebirth"), ("Kebirth", "Rebirth"), ("This Kace,", "This Race,"), ("no longer do ¶ vl see", "no longer do I see"),
    ("Birth in God *?", "Birth in God?"), ("eleventh, Eashness", "eleventh, Rashness"), ("my Eighteousness", "my Righteousness"),
    ("Truth's praises f", "Truth's praises!"), ("oblation l!", "oblation!"), ("Keceive from me", "Receive from me"),
    ("from Thy Mon I have", "from Thy Æon I have"), ("being sung,4' O father", "being sung, O father"),
    ("Light and Life 2]", "Light and Life]"), ("my Self - control", "my Self-control"), ("Bat further I myself", "But further I myself"),
    ("receive my word (logos) \\", "receive my word (logos)!"), ("I had before,....;", "I had before, . . . .;"),
    ("Rebirth. And.... the Reason", "Rebirth. And . . . . the Reason"), ("against Desire. ¶.... This step", "against Desire. ¶ . . . . This step"),
    ("extended),... though", "extended), . . . though"), ("Sharing- with-all", "Sharing-with-all"),
]


def parthey13():
    """Parthey's CH XIII from the transcription: (title, {section: [paragraphs]}, hymn heading).
    Words divided at a line end ('-') are joined; a speaker label starts a new paragraph."""
    title, heading, secs, cur = "", "", {}, None
    for line in P13_FILE.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("@p"):
            continue
        if line.startswith("@title "):
            title = line[7:]
            continue
        if line.startswith("@heading "):
            heading = line[9:]
            continue
        for k, piece in enumerate(re.split(r"\s*§(\d+) ", line)):
            if k % 2 == 1:
                cur = int(piece)
                secs[cur] = [""]
                continue
            if not piece:
                continue
            if re.match(r"(Τάτ|Ἑρμῆς)\. ", piece) and secs[cur][-1]:
                secs[cur].append("")
            para = secs[cur][-1]
            if para.endswith("-"):
                para = para[:-1] + piece
            else:
                para = (para + " " + piece).strip()
            secs[cur][-1] = para
    for n in secs:
        for p in secs[n]:
            assert not p.endswith("-"), (n, p)
    assert sorted(secs) == list(range(1, 23)), sorted(secs)
    return title, secs, heading


def mead13(raw=False):
    """Mead's CH XIII from the Toronto OCR: page heads, footnotes and footnote numbers removed."""
    lines = (SRC / "mead" / "mead1906-v2_djvu.txt").read_text(encoding="utf-8", errors="replace").split("\n")
    i = next(k for k, l in enumerate(lines) if re.search(r"^1\.\s+Tat\.\s+\[Now\]", l))
    j = next(k for k, l in enumerate(lines) if k > i and re.search(r"^COMMENTA", l))
    hdr = re.compile(r"(THRICE.?G.?.?.?TEST|SECRET\s+S\w+\s+ON)", re.I)
    pages = [[]]
    for l in lines[i:j]:
        st = l.strip()
        if hdr.search(st) and len(st) < 70 and (st.upper() == st or re.match(r"^\d{3}\s", st) or re.search(r"\s\d{3}$", st)):
            pages.append([])
            continue
        if re.fullmatch(r"\d{3}", st):
            pages.append([])
            continue
        pages[-1].append(st)
    kept = []
    for p in pages:   # footnotes: from the first line after a blank line that starts with a footnote number
        cut = len(p)
        for k, st in enumerate(p):
            if k > 0 and p[k - 1] == "" and re.match(r"^([1-9]|\^|\*)\s{1,4}\S", st) and not re.match(r"^\d{1,2}\.\s", st):
                cut = k
                break
        q = p[:cut]
        while q and q[0] == "":
            q.pop(0)
        while q and q[-1] == "":
            q.pop()
        kept.extend(q)
    t = "\n".join(kept)
    # a footnote that runs over from p. 229 onto the top of p. 230 (Porphyry) and Mead's heading of the hymn
    a = re.search(r"struck\s+thy\s+tent\s+and\s+left\s+the\s+tomb", t).start()
    b = re.search(r"THE\s+SECRET\s+HYMNODY", t)
    t = t[:a] + "\n\n" + t[b.end():]
    g = (SRC / "mead" / "hermes13.html").read_text(encoding="latin-1")
    keep = set(w.lower() for w in re.findall(r"\b\w+-\w+(?:-\w+)*\b", htmlmod.unescape(re.sub(r"<[^>]+>", " ", g))))
    t = re.sub(r"(\w+)-[ \t]*\n[ \t]*(\w+)",
               lambda m: m.group(1) + "-" + m.group(2) if m.group(2)[:1].isupper() or (m.group(1) + "-" + m.group(2)).lower() in keep else m.group(1) + m.group(2), t)
    t = re.sub(r"\n\s*\n+", " ¶ ", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(?<=[A-Za-z\.,;:\)\]'’\"—?!])\d{1,2}(?=[\s,;:.]|$)", "", t)
    t = re.sub(r"(?<=\s)([1-9]|\*)(?=\s)", " ", t)
    t = re.sub(r"(?<=\s)0(?=\s)", "O", t).replace(" ,", ",")
    t = re.sub(r"\s+([:;?!.,])", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    if raw:
        return t
    for x, y in FIX13_ENG:
        assert x in t, x
        t = t.replace(x, y)
    t = re.sub(r"(?:(?<=\s)|^)\d{1,2}\. (?=[A-Z\[])", "", t)        # Mead's section numerals
    t = re.sub(r"\s+", " ", t).replace(" ¶ ¶ ", " ¶ ")
    pos = []
    p = 0
    for n in range(1, 23):
        q = t.index(ENG13_CUTS[n], p)
        pos.append(q)
        p = q + 1
    pos.append(len(t))
    return {n: t[pos[n - 1]:pos[n]].strip(" ¶") for n in range(1, 23)}


def build_ch13(cv):
    title, grc, heading = parthey13()
    eng = mead13()
    files = {p["folio"]: get_scan(p["folio"], cv) for p in PAGES13}
    flat = " ".join(" ".join(grc[n]) for n in range(1, 23))
    starts = [0] + [flat.index(p["anchor"]) for p in PAGES13[1:]]
    assert starts == sorted(starts)
    sec_span, pos = {}, 0
    for n in range(1, 23):
        s_ = " ".join(grc[n])
        a = flat.index(s_, pos)
        sec_span[n] = (a, a + len(s_))
        pos = a + len(s_)
    sections = []
    for n in range(1, 23):
        a, z = sec_span[n]
        pages = [p for k, p in enumerate(PAGES13) if a < (starts[k + 1] if k + 1 < len(PAGES13) else len(flat) + 1) and z > starts[k]]
        assert pages, n
        if len(pages) == 1:
            note = f"On {MS['short']} fol. {pages[0]['folio']}. " + page_note13(pages[0], cv)
        else:
            note = (f"Starts on fol. {pages[0]['folio']} and continues on fol. {pages[-1]['folio']} (page break inside this section). "
                    + " ".join(page_note13(p, cv) for p in pages))
        note += " Checked on the images. The Greek shown is Parthey's edition, not a transcription of this manuscript."
        g_html = "<br>".join(htmlmod.escape(p, quote=False) for p in grc[n])
        e_html = to_html(eng[n])
        if n == 1:
            g_html = f"<em>{htmlmod.escape(title, quote=False)}</em><br>" + g_html
            e_html = "<em>The Secret Sermon on the Mountain, concerning Rebirth and the Promise of Silence, of Thrice-greatest Hermes unto Tat his Son</em><br>" + e_html
        if n == 17:
            g_html = f"<em>{htmlmod.escape(heading, quote=False)}</em><br>" + g_html
            e_html = "<em>The Secret Hymnody</em><br>" + e_html
        sections.append({
            "section": str(n),
            "original_ref": f"Corpus Hermeticum XIII.{n} (Parthey 1854, cap. 13); {MS['short']} fol. " + ", ".join(p["folio"] for p in pages),
            "original_text": g_html,
            "text": e_html,
            "scan_pages": [f"{KEY}/{files[p['folio']].name}" for p in pages],
            "scan_note": note,
        })
    tid = PREFIX + "on-rebirth"
    folios = [p["folio"] for p in PAGES13]
    title_en = "Corpus Hermeticum XIII: the Secret Discourse on the Mountain, on Rebirth"
    desc = ("Hermes teaches his son Tat the way of rebirth: the twelve torments of matter are driven out by ten powers of God, Tat is born again "
            "in Mind and sings the secret hymn of rebirth. Complete, shown on the 14th-century Florence manuscript Laur. Plut. 71.33.")
    intro = (
        "<p>The thirteenth treatise of the Corpus Hermeticum is a dialogue between Hermes Trismegistus and his son Tat on 'rebirth' (<em>palingenesia</em>), "
        "written in Roman Egypt probably in the 2nd or 3rd century AD. Tat reminds his father that he had said no one can be saved before rebirth, and asks "
        "how it happens. Hermes answers that the womb is wisdom in silence and the seed the true Good, and that the one born is 'a god, child of God' (section 2, in Parthey's Greek). "
        "He describes his own experience: he has passed out of himself into an immortal body and is 'born in Mind' (3). The twelve 'torments' of matter, from ignorance "
        "and grief to rashness and malice, are driven out one by one by ten powers of God, from knowledge of God and joy to life and light (7-10); "
        "in Mead's words, 'by this Birth we are made into Gods' (10). Tat, reborn, sees himself everywhere, 'in heaven, in earth, in water, air' (11). "
        "Hermes then teaches him the secret hymn, to be sung facing the south wind at sunset and the east at sunrise (16-20), Tat adds his own praise, "
        "and Hermes binds him to silence (21-22).</p>\n\n"
        "<p>The pages shown are from Florence, Biblioteca Medicea Laurenziana, Plut. 71.33, a paper manuscript of the 14th century (manuscript A of the editions), "
        "the same manuscript as the Poimandres in this collection. CH XIII runs from the middle of fol. 141v to the middle of fol. 144r; the title stands in red ink, "
        "and the hymn has the red heading 'ὑμνῳδία' on fol. 143v. Each section below is one of the 22 sections of Parthey's edition, linked to the page or pages "
        "that carry its words, identified by reading the first and last lines of each page on the image. "
        "The Greek is Gustav Parthey's edition of 1854 (chapter 13, pp. 114-128), transcribed for this library from the printed pages and checked line by line against them; "
        "Parthey's apparatus is not shown, and his text differs from the manuscript in places. The English is G. R. S. Mead's translation of 1906, made from Reitzenstein's text of 1904, "
        "so some phrases do not match Parthey's Greek word for word, and Mead places the numbers 8, 9 and 19 at other sentences (here the English is divided at Parthey's sections).</p>"
    )
    entry = {
        "id": tid, "slug": tid, "title": title_en,
        "language": "Greek (Parthey 1854) / English (G. R. S. Mead, 1906)",
        "source": f"{MS['shelfmark']} fol. 141v-144r ({MS['holder']}) + Parthey's Greek (1854, transcribed from the page images) + G. R. S. Mead's English (1906)",
        "description": desc,
        "introduction": intro,
        "translator_notes": [
            "Greek: Gustav Parthey, Hermetis Trismegisti Poemander (Berlin: Nicolai, 1854), cap. 13, pp. 114-128, transcribed from the page images of archive.org poemander00trisgoog and proofread line by line against them (transcription in data/sources/corpus-hermeticum/parthey/parthey1854-ch13.txt). Speaker names (Τάτ., Ἑρμῆς.) are Parthey's. Parthey's apparatus is not shown.",
            "English: G. R. S. Mead, Thrice-Greatest Hermes, vol. 2 (1906), pp. 219-233, 'The Secret Sermon on the Mountain'. Mead's footnotes are not shown; his square brackets mark words he supplied and '. . . .' marks gaps in the Greek. Mead numbers sections 8, 9 and 19 at other sentences than Parthey; the English is divided here at the words that translate the start of Parthey's sections, and Mead's numerals are left out.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"{MS['holder']}: {MS['object']} (folios {', '.join(folios)}); IIIF manifest https://cdm21059.contentdm.oclc.org/iiif/plutei:1210396/manifest.json",
            "scan_license": MS["license"],
            "scan_manuscript": MS["desc"],
            "scan_mapping": "First and last lines of every page read on the image and matched to Parthey's Greek (words recorded in each scan_note); end of each page checked against the start of the next; start and end of the treatise read at the red titles on fols. 141v and 144r.",
            "scan_mapping_urls": [MS["pinakes"]] + [viewer(f, cv) for f in folios],
            "scan_local_paths": [f"{KEY}/{files[f].name}" for f in folios],
            "original_text_source": "G. Parthey, Hermetis Trismegisti Poemander (Berlin 1854), pp. 114-128, transcribed from the page images of https://archive.org/details/poemander00trisgoog (leaves 140-154) and proofread line by line",
            "original_text_license": "public domain (published 1854)",
            "translation_source": "G. R. S. Mead, Thrice-Greatest Hermes, vol. 2 (London: Theosophical Publishing Society, 1906), pp. 219-233, archive.org thricegreatesthe02hermuoft (OCR checked against thricegreatesth02meadgoog and afx0734.0002.001.umich.edu, and against the page images at the lacunae)",
            "translation_license": "public domain (published 1906; Mead died 1933)",
            "translator": "G. R. S. Mead (1906)",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections)")
    return {
        "id": tid, "slug": tid, "order": 2, "title": title_en, "author_id": "hermes-trismegistus",
        "language": "Greek", "era": "Imperial", "tradition": "hermetic", "category": "sacred-text",
        "date_approx": "c. 2nd-3rd century AD (composition); manuscript 14th century", "century": 2,
        "source": entry["source"], "description": desc,
        "themes": ["hermetica", "corpus-hermeticum", "rebirth", "palingenesia", "tat", "hymn", "nous", "deification", "theosis", "gnosis", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[f].name}", "caption": f"{MS['short']} fol. {f}"} for f in folios]},
    }


def page_note13(p, cv):
    if p.get("custom"):
        return p["custom"] + " Viewer: " + viewer(p["folio"], cv)
    s = f"{MS['short']} fol. {p['folio']} begins '{p['first']}' on its first line"
    s += f" and ends '{p['last']}' on its last line." if p.get("last") else "."
    if p.get("extra"):
        s += " " + p["extra"]
    return s + " Viewer: " + viewer(p["folio"], cv)


if __name__ == "__main__":
    main()
