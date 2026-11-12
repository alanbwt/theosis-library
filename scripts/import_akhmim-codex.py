#!/usr/bin/env python3
"""
import_akhmim-codex.py -- The Gospel of Peter on the pages of the Akhmim codex
(Cairo, Egyptian Museum, P. Cair. 10759; parchment, 6th-9th c.), one section per
chapter of J. A. Robinson's division (1-14), each linked to the codex page(s) carrying it.

Chain of evidence
-----------------
1. SCAN     A. Lods, "L'Evangile et l'Apocalypse de Pierre ... avec le texte grec du
            livre d'Henoch", Memoires publies par les membres de la Mission archeologique
            francaise au Caire IX.3 (Paris: Leroux 1893): heliogravure plates made from
            photographs of the manuscript taken at the Gizeh Museum.  Internet Archive item
            MMAF9.3 (scan of the Bibliotheque de l'Universite Bordeaux Montaigne copy),
            public domain (1893).  Each plate shows two codex pages, printed sideways, with
            Lods's page number under each page: pl. II = pp. 1-2, III = 3-4, IV = 5-6,
            V = 7-8, VI = 9-10 (IA images 0027-0031).  Each page is cut out of its plate
            and turned upright; the first line of every page was compared with Lods's
            transcription on the image.
2. GREEK    Lods's diplomatic transcription of the same pages (pp. 219-224 of the 1893
            volume), with his page and line numbers, transcribed line by line from the
            printed pages for this library (data/sources/akhmim-codex/
            lods1893_gospel_of_peter.txt; checked against an OCR of the same pages).
            Lods prints the manuscript text without accents or word division other than his
            own spacing; [ ] = letters taken from Bouriant's first copy and not verifiable on
            the photographs; dots = lost letters; bars over nomina sacra and over a final
            letter standing for nu are given as combining overlines.
3. MAPPING  Page and line numbers are Lods's.  The chapter openings of Robinson's division
            are located in Lods's lines by their Greek words (CHAPTERS below), so each
            section shows exactly the lines (or part-lines) of its chapter and points at the
            page(s) that carry them.
4. ENGLISH  J. Armitage Robinson, "The Gospel according to Peter", in Ante-Nicene Fathers
            vol. IX (ed. A. Menzies, 1896), revised by Robinson "in accordance with the
            photographic facsimile"; Wikisource transcription, public domain.

Usage:  python3 scripts/import_akhmim-codex.py [--force]
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

from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
KEY = "akhmim-codex"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
CACHE = Path(os.environ.get("THEOSIS_CACHE", Path.home() / ".cache" / "theosis-akhmim"))
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"

IA_ITEM = "MMAF9.3"
IA_DETAILS = "https://archive.org/details/MMAF9.3"
IA_IMG = ("https://archive.org/download/MMAF9.3/MMAF%209.3%20Lods%20%281893%29%20LR_jp2.zip/"
          "MMAF%209.3%20Lods%20%281893%29%20LR_jp2%2FMMAF%209.3%20Lods%20%281893%29%20LR_{n:04d}.jp2&ext=jpg")
ANF_URL = ("https://en.wikisource.org/w/index.php?title=Ante-Nicene_Fathers/Volume_IX/"
           "The_Gospel_of_Peter/The_Gospel_According_to_Peter&action=raw")
ANF_PAGE = "https://en.wikisource.org/wiki/Ante-Nicene_Fathers/Volume_IX/The_Gospel_of_Peter/The_Gospel_According_to_Peter"

# IA image number, rotation that makes the plate upright, plate number, codex pages (left, right)
PLATES = [(27, 90, "II", (1, 2)), (28, 270, "III", (3, 4)), (29, 90, "IV", (5, 6)),
          (30, 270, "V", (7, 8)), (31, 90, "VI", (9, 10))]

# Robinson's chapter openings in Lods's lines: (chapter, page, line, first words on that line)
CHAPTERS = [
    (1, 2, 1, "τ . . δε"),
    (2, 2, 5, "ιστηκει δε"),
    (3, 2, 13, "και παρεδωκεν"),
    (4, 3, 4, "και η[νεγκον]"),
    (5, 3, 15, "ην δε μεσημβρια"),
    (6, 4, 9, "και τοτε απεσπασαν"),
    (7, 4, 17, "τοτε οι ιουδαιοι"),
    (8, 5, 9, "συναχθεντες δε"),
    (9, 6, 14, "τη δε νυκτι"),
    (10, 7, 5, "ιδ[οντες]"),
    (11, 7, 16, "συνε"),
    (12, 8, 15, "ορθου δε"),
    (13, 9, 14, "και απελθουσαι"),
    (14, 10, 6, "ην δε τελευταια"),
]

# first words of each codex page as read on the plates (checked against Lods's lines)
PAGE_CHECK = {
    2: "small cross above the text; line 1 ...δε ιουδαιων ουδεις ενιψατο τας χειρας",
    3: "lines 1-2 badly rubbed, as Lods's brackets show; the last line reads ηλιον μη δυναι επι πεφωνευμενω και τις αυτων",
    4: "ειπεν ποτισατε αυτον χολην μετα οξους και κερα",
    5: "[κακον εα]υτοις εποιησαν ηρξαντο κοπτεσθαι",
    6: "οι μαθηται αυτου κλεψωσιν αυτον και υπολαβη",
    7: "κατελθοντας εκειθε πολυ φεγγος εχοντας",
    8: "και ενφανισαι ταυτα τω πειλατω και ετι διανοουμε",
    9: "υπο της οργης ουκ εποιησεν επι τω μνηματι",
    10: "στολην λαμπροτατην οστις εφη αυται οτι ηλθα; the page ends with a braided band",
}


def fetch(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except Exception as e:  # noqa
            if k == tries - 1:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(3 * (k + 1))


def plate(n):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"lods1893_{n:04d}.jpg"
    if not p.exists():
        p.write_bytes(fetch(IA_IMG.format(n=n)))
    return Image.open(p).convert("RGB")


def split_plate(im, rot):
    """Turn the plate upright and return the two page boxes (left, right)."""
    im = im.rotate(rot, expand=True, fillcolor=(255, 255, 255))
    a = np.asarray(im.convert("L")).astype(float)
    H, W = a.shape
    nonpaper = a < 215
    colp = nonpaper[int(H * 0.2):int(H * 0.8)].mean(axis=0)
    sm = np.convolve(colp, np.ones(61) / 61, mode="same")
    lo = int(W * 0.35)
    gap = int(np.argmin(sm[lo:int(W * 0.65)])) + lo

    def bbox(x0, x1):
        sub = nonpaper[:, x0:x1]
        cp = np.convolve(sub[int(H * 0.2):int(H * 0.8)].mean(axis=0), np.ones(31) / 31, mode="same")
        xs = np.where(cp > 0.3)[0]
        rp = np.convolve(sub[:, xs.min():xs.max()].mean(axis=1), np.ones(31) / 31, mode="same")
        y_lo, y_hi = int(H * 0.06), int(H * 0.94)
        ys = np.where(rp[y_lo:y_hi] > 0.5)[0] + y_lo
        return (int(x0 + xs.min() - 60), int(max(0, ys.min() - 60)),
                int(x0 + xs.max() + 60), int(min(H, ys.max() + 60)))
    boxes = [bbox(0, gap), bbox(gap, W)]
    y0 = min(b[1] for b in boxes)
    y1 = max(b[3] for b in boxes)
    return im, [(b[0], y0, b[2], y1) for b in boxes]


def scan_name(p):
    return f"akhmim-p{p:02d}.jpg"


def make_scans(force=False):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for n, rot, _pl, pages in PLATES:
        if not force and all((SCAN_DIR / scan_name(p)).exists() for p in pages):
            continue
        im, boxes = split_plate(plate(n), rot)
        for p, b in zip(pages, boxes):
            c = im.crop(b)
            s = 2400 / max(c.size)
            if s < 1:
                c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
            c.save(SCAN_DIR / scan_name(p), quality=85)
            print(f"  {scan_name(p)} {c.size}")


def lods_lines():
    pages, cur = {}, None
    for line in (SRC / "lods1893_gospel_of_peter.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("PAGE "):
            cur = int(line.split()[1])
            pages[cur] = []
            continue
        n, text = line.split("\t", 1)
        assert int(n) == len(pages[cur]) + 1, (cur, n)
        pages[cur].append(text)
    return pages


def anf_sections():
    p = SRC / "anf9_gospel_of_peter.wiki"
    if not p.exists():
        p.write_bytes(fetch(ANF_URL))
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"<ref>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"\{\{header.*?\}\}", "", t, flags=re.S)
    t = re.sub(r"==Footnotes==.*", "", t, flags=re.S)
    t = html.unescape(t).replace("\xa0", " ")
    parts = re.split(r"\n\s*(\d{1,2})\s{1,3}(?=[A-Z\[])", t)
    out = {}
    for i in range(1, len(parts), 2):
        body = re.sub(r"\s+", " ", parts[i + 1]).strip()
        body = re.sub(r"''(.+?)''", r"<em>\1</em>", body)
        out[int(parts[i])] = body
    assert sorted(out) == list(range(1, 15)), sorted(out)
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chapter_greek(pages):
    """Return {chapter: (html, [pages], first(page,line), last(page,line))}."""
    flat = [(p, i + 1, t) for p in sorted(pages) for i, t in enumerate(pages[p])]
    starts = []
    for ch, p, ln, words in CHAPTERS:
        text = pages[p][ln - 1]
        k = text.find(words)
        assert k >= 0 and (k == 0 or text[k - 1] == " "), (ch, p, ln, words, text)
        starts.append((ch, p, ln, k))
    res = {}
    for j, (ch, p, ln, k) in enumerate(starts):
        nxt = starts[j + 1] if j + 1 < len(starts) else None
        rows, used = [], []
        for (pp, ll, t) in flat:
            if (pp, ll) < (p, ln):
                continue
            if nxt and (pp, ll) > (nxt[1], nxt[2]):
                break
            seg = t
            if (pp, ll) == (p, ln):
                seg = seg[k:]
            if nxt and (pp, ll) == (nxt[1], nxt[2]):
                seg = t[:nxt[3]].rstrip() if (pp, ll) != (p, ln) else t[k:nxt[3]].rstrip()
                if not seg:
                    break
            rows.append(f"<sup>{pp}.{ll}</sup> {esc(seg)}")
            if pp not in used:
                used.append(pp)
            last = (pp, ll)
        res[ch] = ("<p>" + "<br>".join(rows) + "</p>", used, (p, ln), last)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    make_scans(args.force)
    pages = lods_lines()
    assert sorted(pages) == list(range(2, 11))
    greek = chapter_greek(pages)
    eng = anf_sections()

    sections, used_all = [], []
    for ch in range(1, 15):
        g, used, first, last = greek[ch]
        files = [f"{KEY}/{scan_name(p)}" for p in used]
        for f in files:
            if f not in used_all:
                used_all.append(f)
        span = f"p. {first[0]}, line {first[1]} to p. {last[0]}, line {last[1]}"
        checks = "; ".join(f"p. {p} begins ‹{PAGE_CHECK[p]}›" for p in used)
        sections.append({
            "section": str(ch),
            "original_ref": f"Gospel of Peter {ch} (Robinson); Akhmim codex {span} (Lods 1893)",
            "original_text": g,
            "text": f"<p><sup>{ch}</sup> {eng[ch]}</p>",
            "scan_pages": files,
            "scan_note": (f"Akhmim codex {span}, page and line numbers as printed by Lods (1893), whose heliogravure "
                          f"plates are shown. Checked on the plates: {checks}. The chapter opening was located in "
                          f"Lods's lines by its Greek words (‹{CHAPTERS[ch - 1][3]}›)."),
        })

    tid = PREFIX + "gospel-of-peter"
    entry = {
        "id": tid, "slug": tid,
        "title": "Gospel of Peter (Akhmim codex, pages 2-10)",
        "language": "Greek (Lods 1893 transcription) / English (J. A. Robinson)",
        "source": "Akhmim codex (P. Cair. 10759) pages 2-10 in A. Lods's heliogravure plates (1893, Internet Archive) + Lods's diplomatic transcription + English of J. Armitage Robinson (Ante-Nicene Fathers IX, public domain)",
        "description": "The surviving fragment of the Gospel of Peter (trial, crucifixion, burial and resurrection of Jesus), "
                       "in the Greek of the only manuscript, the Akhmim codex, each chapter linked to the photographed page that carries it.",
        "introduction": (
            "<p>The <strong>Gospel of Peter</strong> was known only by name, from Eusebius and from Serapion of Antioch (c. 200 AD), "
            "until a long fragment of it was found in the winter of 1886-87 in a monk's grave at Akhmim (ancient Panopolis) in Upper Egypt. "
            "The fragment tells the story of the passion from Pilate's hand-washing to the resurrection, in the first person of Simon Peter, "
            "and breaks off as Peter, Andrew and Levi go to the sea. It is now generally dated to the 2nd century.</p>"
            "<p><strong>The manuscript.</strong> The Akhmim codex (Cairo, Egyptian Museum, P. Cair. 10759) is a small parchment book of 33 leaves; proposed dates for its hands range from the 6th to the 9th century. "
            "Page 1 carries a cross; the Gospel of Peter fills pages 2-10 and ends with a braided band; the Apocalypse of Peter and the Greek text of 1 Enoch 1-32 follow. "
            "The pages shown are A. Lods's heliogravure plates of 1893, made from photographs taken in the Gizeh Museum: each plate reproduced two pages, "
            "and each page has been cut out of its plate and turned upright here.</p>"
            "<p><strong>Texts and mapping.</strong> The Greek is Lods's line-by-line diplomatic transcription of the same pages, "
            "with his page and line numbers (shown as page.line), so every line can be found on the photograph. "
            "Each section is one chapter of J. Armitage Robinson's division, which is also the division of his English translation; "
            "the chapter openings were located in Lods's lines by their Greek words. Robinson revised his translation against the photographic facsimile.</p>"
        ),
        "translator_notes": [
            "Lods's signs: [ ] letters not legible on the photographs and given from Bouriant's first copy; dots mark lost letters; the manuscript has no accents and almost no punctuation.",
            "A bar over a group of letters (nomina sacra such as κ̅υ̅ for κυριου, θ̅υ̅ for θεου, α̅ν̅ω̅ν̅ for ανθρωπων) or over a final letter standing for a dropped nu is shown with a combining overline.",
            "Lods prints ηι with iota adscript and η̈ with two dots at 6.14, and an apostrophe after ϊωσηφ (2.6) and μαριαμ (8.16), as in the manuscript.",
            "Chapter numbers (1-14) are J. Armitage Robinson's, used in his English translation.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"A. Lods, Memoires publies par les membres de la Mission archeologique francaise au Caire IX.3 (Paris 1893), plates II-VI; Internet Archive {IA_DETAILS} (images 0027-0031)",
            "scan_license": "Public domain (published 1893); scan by the Internet Archive from the Bibliotheque de l'Universite Bordeaux Montaigne copy",
            "scan_manuscript": "Cairo, Egyptian Museum, P. Cair. 10759 (Akhmim codex, Codex Panopolitanus), parchment, dated by scholars between the 6th and 9th centuries, found at Akhmim 1886-87; Gospel of Peter on pages 2-10. Images: heliogravure plates from photographs of the manuscript (Lods 1893).",
            "scan_mapping": "Page and line numbers from Lods's transcription (1893), which prints them for every line; plate and page numbers as printed under each plate page; first line of every page checked on the plate; chapter openings located in the transcription by their Greek words.",
            "scan_mapping_urls": [IA_DETAILS],
            "scan_local_paths": used_all,
            "original_text_source": "A. Lods, transcription of the Gospel of Peter in Memoires ... Mission archeologique francaise au Caire IX.3 (1893) pp. 219-224, transcribed from the printed pages (Internet Archive MMAF9.3)",
            "original_text_license": "public domain (published 1893)",
            "translation_source": f"J. Armitage Robinson, The Gospel according to Peter, in Ante-Nicene Fathers vol. IX (ed. A. Menzies, 1896); Wikisource: {ANF_PAGE}",
            "translation_license": "public domain (published 1896)",
            "translator": "J. Armitage Robinson (1896)",
            "verified_date": TODAY,
        },
    }
    (PUB / f"{tid}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": 1, "title": entry["title"],
        "author_id": "gospel-of-peter", "language": "Greek",
        "era": "Apostolic", "tradition": "christian", "category": "sacred-text",
        "date_approx": "2nd century AD (composition); Akhmim codex 6th-9th century",
        "century": 2, "source": entry["source"], "description": entry["description"],
        "themes": ["gospel-of-peter", "akhmim", "passion-narrative", "resurrection", "apocrypha", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{scan_name(1)}", "caption": "Akhmim codex, page 1 (cross)"}]
                  + [{"file": f, "caption": f"Akhmim codex, page {int(f[-6:-4])} (Lods 1893)"} for f in used_all]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Akhmim Codex (Gospel of Peter)",
            "group": "Early Christian",
            "date_sort": 150,
            "author_name": "Gospel of Peter (2nd c. AD; Akhmim codex, 6th-9th c.)",
            "source_url": IA_DETAILS,
            "critical_edition": "A. Lods, diplomatic transcription and heliogravure facsimile (1893)",
            "translator_name": "J. Armitage Robinson (1896)",
            "original_lang_label": "Greek · Lods 1893 (diplomatic)",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "gospel of peter akhmim panopolis codex panopolitanus apocrypha passion resurrection pilate herod",
            "description": "The Gospel of Peter from the Akhmim codex, the only manuscript of the work, page by page in Lods's 1893 photographic plates with his line-by-line transcription and Robinson's English.",
        },
        "texts": [row],
        "authors": [{
            "id": "gospel-of-peter", "name": "Gospel of Peter", "dates": "2nd c. AD (composition)", "century": 2,
            "era": "Apostolic", "tradition": "christian", "language": "Greek",
            "bio": "Anonymous gospel written in the name of Simon Peter, known from early church writers and from one fragment found at Akhmim in Egypt in 1886-87.",
        }],
    }
    COLL.write_text(json.dumps(coll, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {tid}: {len(sections)} sections, {len(used_all)} pages")


if __name__ == "__main__":
    main()
