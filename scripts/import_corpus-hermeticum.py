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
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Corpus Hermeticum",
            "group": "Greece", "date_sort": 200,
            "author_name": "Hermes Trismegistus (attributed), 2nd-3rd century AD; Florence manuscript Laur. Plut. 71.33",
            "source_url": MS["object"],
            "critical_edition": "Parthey, Hermetis Trismegisti Poemander (1854), via Greek Wikisource",
            "translator_name": "G. R. S. Mead (1906)",
            "original_lang_label": "Greek · Parthey",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "corpus hermeticum hermes trismegistus poimandres poemandres pimander nous logos ascent become god ficino laurenziana mead",
            "description": "The Hermetic Poimandres, the vision of the divine Mind and of the soul's ascent to become God, shown section by section on the oldest manuscript of the Corpus Hermeticum, with Parthey's Greek and G. R. S. Mead's English.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
