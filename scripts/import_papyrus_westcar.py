#!/usr/bin/env python3
"""
import_papyrus_westcar.py -- Papyrus Westcar (Berlin, Aegyptisches Museum P 3033):
the Tales of the Magicians at the court of King Khufu (Cheops).

Collection key: papyrus-westcar   (entry verified-papyrus-westcar-tales-of-the-magicians)

Chain of evidence
-----------------
1. OBJECT   Papyrus Westcar, Staatliche Museen zu Berlin, Aegyptisches Museum und
            Papyrussammlung P 3033, Second Intermediate Period (17th Dynasty,
            c. 1650-1550 BCE), Thebes. Twelve columns of hieratic: I-IX on the
            recto, X-XII on the verso. Mounted in four frames, each with its own
            SMB record and photograph:
              Kol. I-III, auf Recto   obj-3437568  (image 7142481)
              Kol. IV-V, auf Recto    obj-792723   (image 4868397)
              Kol. VI-IX, auf Recto   obj-792727   (image 4868400)
              Kol. X-XII, auf Verso   obj-792730   (image 4868398)
2. SCANS    SMB-digital photographs by Sandra Steiss, CC BY-SA 4.0
            ("Staatliche Museen zu Berlin, Aegyptisches Museum und
            Papyrussammlung / Sandra Steiss"), downloaded from search.smb.museum
            (extra_extra_large, 3000 px) and reduced to 2600 px. The column of
            every section comes from the TLA line numbers (column, line); the
            frame holding that column comes from the SMB record titles. Checked
            by eye: each photograph shows the stated number of columns.
3. ORIGINAL Thesaurus Linguae Aegyptiae (TLA database extract January 2018,
            urn:nbn:de:kobv:b4-opus4-29190), AED-TEI text
            J4EXGHLCL5DR7JHSPDWTVEKMDY, CC BY-SA 4.0: transliteration with
            column,line numbers, Unicode hieroglyphs from *_hiero.xml.
4. ENGLISH  W. M. Flinders Petrie, Egyptian Tales, Translated from the Papyri,
            First Series (2nd ed., London: Methuen, 1899), "Tales of the
            Magicians", Project Gutenberg #7386. Public domain. Petrie's opening
            paragraph is his own invented introduction (he says so in his
            Remarks) and is left out; the papyrus's first lines (1,1-1,17, the
            end of an earlier tale) are not translated by Petrie and are left out.
            Each section is a run of Petrie's text matched to a run of TLA
            sentences by reading Petrie against the TLA German sentence
            translations (SECTIONS below).

Usage:  python3 scripts/import_papyrus_westcar.py
"""

import argparse
import io
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "papyrus-westcar"
PREFIX = f"verified-{KEY}-"
TID = PREFIX + "tales-of-the-magicians"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()

T = "{http://www.tei-c.org/ns/1.0}"
XID = "{http://www.w3.org/XML/1998/namespace}id"
AED_RAW = "https://raw.githubusercontent.com/simondschweitzer/aed-tei/master/files/"
GUTENBERG = "https://www.gutenberg.org/cache/epub/7386/pg7386.txt"
SMB_IMG = "https://search.smb.museum/media/images/thumbs/extra_extra_large/"
UA = "TheosisLibrary/1.0 (https://theosislibrary.com; non-commercial research)"
TLA_ID = "J4EXGHLCL5DR7JHSPDWTVEKMDY"

# frame: (local file, SMB object, SMB image path, label, columns, what was checked)
FRAMES = {
    "A": ("westcar-cols-01-03-recto.jpg", "obj-3437568", "142/007/7142481", "Kol. I-III, recto", (1, 2, 3),
          "checked on the image: the frame holds three blocks of horizontal hieratic lines with large losses, read from right "
          "to left (column I at the right, partly on a detached fragment; column III at the left)"),
    "B": ("westcar-cols-04-05-recto.jpg", "obj-792723", "868/004/4868397", "Kol. IV-V, recto", (4, 5),
          "checked on the image: two columns, column IV on the right and column V on the left, both with red rubrics in their lower half; the foot of both columns is damaged"),
    "C": ("westcar-cols-06-09-recto.jpg", "obj-792727", "868/004/4868400", "Kol. VI-IX, recto", (6, 7, 8, 9),
          "checked on the image: four columns side by side, column VI at the right edge and column IX at the left"),
    "D": ("westcar-cols-10-12-verso.jpg", "obj-792730", "868/004/4868398", "Kol. X-XII, verso", (10, 11, 12),
          "checked on the image: three columns on the verso, column X on the right and column XII on the left"),
}
COL_FRAME = {c: k for k, v in FRAMES.items() for c in v[4]}
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}

# (section id, first TLA sentence, last TLA sentence, opening words of Petrie's English for that section)
SECTIONS = [
    ("1", 5, 6, "Then the royal son Khafra stood forth"),
    ("2", 7, 11, "His majesty was walking unto the temple of Ptah"),
    ("3", 12, 20, "And he came then with the servant"),
    ("4", 21, 32, "And when the even was now come the page went forth"),
    ("5", 33, 41, "Then said Uba-aner, 'Bring me my casket"),
    ("6", 42, 44, "And the wife of Uba-aner sent to the steward who had charge over the\ngarden, saying, 'Let the lodge which is in the garden be made ready, for"),
    ("7", 45, 51, "And the lodge was prepared with all good things"),
    ("8", 52, 54, "And Uba-aner abode yet seven days"),
    ("9", 55, 77, "And Uba-aner said unto his majesty"),
    ("10", 78, 80, "And his majesty the king of Upper and Lower Egypt, Nebka, the blessed,\ncommanded"),
    ("11", 81, 81, "This is a wonder that came to pass in the days of thy forefather"),
    ("12", 82, 85, "His majesty the king of Upper and Lower Egypt, Khufu, then said"),
    ("13", 86, 107, "The royal sou Bau-f-ra then stood forth"),
    ("14", 108, 126, "And they rowed down the stream"),
    ("15", 127, 153, "And his majesty said, 'Haste,\nbring me the chief reciter"),
    ("16", 154, 158, "Behold, this is a wonder that came to pass in the days of\nthy father"),
    ("17", 159, 173, "The royal son Hordedef then stood forth"),
    ("18", 174, 182, "And his majesty said, \"Thou, thyself, Hordedef"),
    ("19", 183, 187, "And the king's son Hordedef said, \"Thy state"),
    ("20", 188, 194, "And Dedi replied to him, \"Peace to thee!"),
    ("21", 195, 207, "Then the king's son, Hordedef, stretched forth"),
    ("22", 208, 233, "And his majesty went into the hall\nof columns"),
    ("23", 234, 257, "And King Khufu said, \"And is it true"),
    ("24", 258, 276, "And his majesty's heart became troubled"),
    ("25", 277, 293, "And one day it came to pass that Rud-didet"),
    ("26", 294, 307, "And they entered in\nstraightway"),
    ("27", 308, 319, "Then Isis stood before\nher, and Nebhat stood behind her, and Hakt helped her.  And Isis said,\n\"O child, by thy name of Sah-ra"),
    ("28", 320, 331, "Then Isis stood before her, and Nebhat stood behind her, and Hakt\nhelped her. And Isis said, \"O child, by thy name of Kaku"),
    ("29", 332, 350, "And the deities went out"),
    ("30", 351, 376, "And Rud-didet purified herself"),
    ("31", 377, 391, "And after these days it came to pass"),
    ("32", 392, 405, "Her uncle went therefore"),
]
TALE = {}
for sid in map(str, range(1, 13)):
    TALE[sid] = "Khafra's tale (Webaoner and the wax crocodile)"
for sid in map(str, range(13, 17)):
    TALE[sid] = "Baufra's tale (Sneferu and the rowing girls)"
for sid in map(str, range(17, 33)):
    TALE[sid] = "Hordedef's tale (Djedi; the birth of the three kings)"
HEADINGS = {"KHAFRA'S TALE", "BAUFRA'S TALE", "HORDEDEF'S TALE"}


def fetch(url, binary=False):
    out = subprocess.run(["curl", "-sL", "-m", "300", "-A", UA, url], capture_output=True, check=True).stdout
    if not out:
        raise RuntimeError(f"empty download {url}")
    return out if binary else out.decode("utf-8")


def source(name, url):
    p = SRC / name
    if not p.exists():
        SRC.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url, binary=True))
    return p


# ---------------------------- TLA TEI -------------------------------------
def render_word(el):
    """Transliteration of one <w>, with Leiden-style brackets for the TEI markup."""
    def walk(e):
        tag = e.tag.replace(T, "")
        if tag == "fs":
            return e.tail or ""
        inner = (e.text or "") + "".join(walk(c) for c in e)
        if tag == "supplied":
            inner = f"[{inner}]" if e.get("reason") == "lost" else f"〈{inner}〉"
        elif tag == "surplus":
            inner = "{" + inner + "}"
        elif tag in ("damage", "unclear"):
            inner = f"⸢{inner}⸣"
        elif tag == "add":
            inner = f"\\{inner}/"
        elif tag == "gap":
            inner = "[…]"
        return inner + (e.tail or "") if tag != "w" else inner
    return re.sub(r"\s+", "", walk(el))


def tla_sentences(tid):
    """List of sentences; each sentence = list of tokens ('lb', n) | ('w', translit, word_id) | ('gap',)."""
    base = source(f"{tid}.xml", AED_RAW + f"{tid}.xml")
    root = ET.parse(base).getroot()
    ab = root.find(f".//{T}body/{T}ab")
    sents = []

    def walk(e, cur):
        tag = e.tag.replace(T, "")
        if tag == "s":
            cur = []
            sents.append(cur)
            for c in e:
                walk(c, cur)
            return
        if cur is None:          # tokens outside a sentence: attach to a new pseudo-sentence
            cur = []
            sents.append(cur)
        if tag == "lb":
            cur.append(("lb", e.get("n")))
        elif tag == "w":
            cur.append(("w", render_word(e), e.get(XID)))
        elif tag == "gap":
            cur.append(("gap",))
        else:
            for c in e:
                walk(c, cur)

    for child in ab:
        walk(child, None)
    return [s for s in sents if s]


def tla_hiero(tid):
    p = source(f"{tid}_hiero.xml", AED_RAW + f"{tid}_hiero.xml")
    txt = p.read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in re.finditer(r'<w corresp="src:([^"]+)">([^<]*)</w>', txt)}


def norm_line(n):
    """'[5,6-7]' -> '5,6-7' ; '[2, 8]' -> '2,8' ; '[19.9]' -> '19,9'"""
    n = n.strip().strip("[]").replace("rto", "").replace(" ", "")
    return re.sub(r"^(\d+)\.(\d+)$", r"\1,\2", n)


def page_of(line):
    return int(line.split(",")[0])


def render_range(sents, a, b, hiero=None):
    """Render sentences a..b (1-based, inclusive). Returns (translit_html, hiero_html, lines)."""
    # line current at the start of sentence a
    cur = None
    for s in sents[:a - 1]:
        for t in s:
            if t[0] == "lb":
                cur = norm_line(t[1])
    out, hout, lines = [], [], []
    first_tok = True
    for s in sents[a - 1:b]:
        for t in s:
            if t[0] == "lb":
                cur = norm_line(t[1])
                lines.append(cur)
                out.append(f"<sup>{cur}</sup>")
                hout.append(f"<sup>{cur}</sup>")
                first_tok = False
                continue
            if first_tok:
                if cur:
                    out.append(f"<sup>{cur}</sup>")
                    hout.append(f"<sup>{cur}</sup>")
                    lines.append(cur)
                first_tok = False
            if t[0] == "gap":
                out.append('<span class="lacuna">[…]</span>')
                hout.append('<span class="lacuna">[…]</span>')
            else:
                out.append(t[1])
                if hiero is not None:
                    h = hiero.get(t[2], "")
                    hout.append(h if h else f"<em>{t[1]}</em>")
    txt = " ".join(out).replace("</sup> ", "</sup>")
    htxt = " ".join(hout).replace("</sup> ", "</sup>")
    return txt, (htxt if hiero is not None else None), lines




# ---------------------------- Petrie 1899 ---------------------------------
def petrie_sections(text):
    i = text.index(SECTIONS[0][3])
    j = text.index("_(The rest of the tale is lost.)_", i)
    block = text[i:j]
    starts = []
    for sid, _, _, marker in SECTIONS:
        assert block.count(marker) == 1, (sid, marker)
        starts.append(block.index(marker))
    assert starts == sorted(starts)
    # an opening quotation mark printed just before a marker belongs to the following section
    for k in range(1, len(starts)):
        if block[starts[k] - 1] == '"':
            starts[k] -= 1
    out = {}
    for k, (sid, _, _, _) in enumerate(SECTIONS):
        chunk = block[starts[k]: starts[k + 1] if k + 1 < len(starts) else len(block)]
        pars = []
        for p in re.split(r"\n\s*\n", chunk):
            p = re.sub(r"\s+", " ", p).strip()
            if p and p not in HEADINGS:
                pars.append(p)
        out[sid] = "\n\n".join(pars)
    return out


# ---------------------------- images --------------------------------------
def build_scan(frame):
    local, obj, img, label, cols, _ = FRAMES[frame]
    dest = SCAN_DIR / local
    if dest.exists():
        return dest
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        data = fetch(SMB_IMG + img + ".jpg", binary=True)
        if data[:3] == b"\xff\xd8\xff":
            break
        time.sleep(10 * (attempt + 1))
    else:
        raise RuntimeError(f"could not download {img}")
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if max(im.size) > 2600:
        im.thumbnail((2600, 2600), Image.LANCZOS)
    im.save(dest, "JPEG", quality=86, optimize=True)
    return dest


def main():
    argparse.ArgumentParser().parse_args()
    petrie = petrie_sections(source("petrie1899_pg7386.txt", GUTENBERG).read_text(encoding="utf-8"))
    sents = tla_sentences(TLA_ID)
    assert len(sents) == 405, len(sents)
    hiero = tla_hiero(TLA_ID)
    for f in FRAMES:
        build_scan(f)

    secs = []
    for sid, a, b, _ in SECTIONS:
        tr, hi, lines = render_range(sents, a, b, hiero)
        cols = sorted({page_of(l) for l in lines})
        frames = sorted({COL_FRAME[c] for c in cols})
        span = f"{lines[0]}-{lines[-1]}" if lines[0] != lines[-1] else lines[0]
        sent_desc = f"sentence {a}" if a == b else f"sentences {a}-{b}"
        col_desc = ("column " + ROMAN[cols[0]]) if len(cols) == 1 else ("columns " + " and ".join(ROMAN[c] for c in cols))
        where = " ".join(f"Frame {FRAMES[f][3]} (SMB {FRAMES[f][1]}): {FRAMES[f][5]}." for f in frames)
        note = (f"Westcar {span} (TLA column,line numbers): TLA {sent_desc}, on {col_desc}. {where}")
        if sid in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            note += (" Columns I-III are damaged and the TLA text shows many restorations in square brackets; Petrie's English renders "
                     "a continuous text that includes these restorations.")
        sec = {
            "section": sid,
            "original_ref": f"Papyrus Westcar {span}; Petrie 1899, {TALE[sid]}",
            "original_text": tr,
            "edition_text": hi,
            "text": petrie[sid],
            "scan_pages": [f"{KEY}/{FRAMES[f][0]}" for f in frames],
            "scan_note": note,
        }
        secs.append(sec)
        plain = re.sub(r"<[^>]+>", "", tr).strip()
        assert plain, sid

    scans = [f"{KEY}/{FRAMES[f][0]}" for f in FRAMES]
    entry = {
        "id": TID, "slug": TID,
        "title": "The Tales of the Magicians (Papyrus Westcar)",
        "language": "Egyptian (TLA transliteration and hieroglyphs) / English",
        "source": "Papyrus Westcar, Berlin P 3033 (SMB photographs by Sandra Steiss, CC BY-SA 4.0) + TLA transliteration and hieroglyphs "
                  "(CC BY-SA 4.0) + English of W. M. Flinders Petrie (1899, public domain)",
        "description": "The stories told to King Khufu by his sons about the magicians Webaoner, Djadjaemankh and Djedi, ending with the "
                       "birth of the first three kings of the 5th Dynasty, on the twelve columns of Papyrus Westcar (c. 1600 BCE).",
        "introduction": (
            "<p>Papyrus Westcar (Berlin, Aegyptisches Museum P 3033) was copied in the Second Intermediate Period, around 1650-1550 BCE, "
            "from a Middle Kingdom composition. It is named after Henry Westcar, who brought it from Egypt; Lepsius acquired it and it came "
            "to the Berlin museum with his estate. The story is set at the court of King Khufu (Cheops), builder of the Great Pyramid: his sons "
            "take turns telling him of wonders worked by chief lector priests in the reigns of earlier kings. Khafra tells of Webaoner, whose "
            "wax crocodile comes to life and seizes his wife's lover; Baufra tells how Djadjaemankh parted the waters of a lake to recover a "
            "rower's lost pendant for King Sneferu; Hordedef brings a living magician, Djedi, who rejoins severed heads and foretells that "
            "three sons of the sun god, born to Ruddjedet, will become kings. The birth of the three kings and the first threats against them "
            "end the surviving text; the papyrus breaks off in column XII.</p>\n\n"
            "<p>The roll has twelve columns of hieratic in horizontal lines, columns I-IX on the recto and X-XII on the verso. It is mounted "
            "in four frames, each photographed by the Staatliche Museen zu Berlin: columns I-III, IV-V, VI-IX and X-XII. Every section below "
            "is linked to the photograph of the frame that carries it; the scan note gives the column and line numbers. The beginning of the "
            "roll is lost, and the first lines of column I (1,1-1,17) hold the end of an earlier tale that Petrie did not translate; they are not "
            "included here.</p>\n\n"
            "<p>The Egyptian is the Thesaurus Linguae Aegyptiae transliteration with the column and line number before each line, followed by "
            "the TLA hieroglyphic transcription in Unicode (words without a complete hieroglyphic encoding are shown in italic transliteration). "
            "Text restored by the editors is in square brackets, signs supplied for scribal omissions in angle brackets, damaged signs in half "
            "brackets, and lost text as [...]. The English is W. M. Flinders Petrie's 1899 translation; it reads the damaged first columns "
            "as a continuous story, following the restorations of its time, and some names are spelled in his style (Dedi for Djedi, "
            "Uba-aner for Webaoner, Rud-didet for Ruddjedet).</p>"
        ),
        "translator_notes": [
            "Petrie's book opens the tale with eight lines of his own invention to introduce King Khufu and his sons (he says so in his Remarks); they are left out.",
            "Petrie's long paragraphs are cut at sentence boundaries where the papyrus moves to a new episode; the wording is unchanged.",
            "Petrie's spelling 'The royal sou Bau-f-ra' (a typesetting error for 'son') is kept as printed in the Gutenberg text.",
        ],
        "translation": secs,
        "verification": {
            "scan_source": "Staatliche Museen zu Berlin, SMB-digital (search.smb.museum): P 3033 Kol. I-III (obj-3437568), Kol. IV-V (obj-792723), "
                           "Kol. VI-IX (obj-792727), Kol. X-XII verso (obj-792730); https://id.smb.museum/object/792723 etc.",
            "scan_license": "CC BY-SA 4.0, Staatliche Museen zu Berlin, Aegyptisches Museum und Papyrussammlung / Sandra Steiss",
            "scan_manuscript": "Berlin, Aegyptisches Museum und Papyrussammlung P 3033 (Papyrus Westcar), 17th Dynasty, c. 1650-1550 BCE",
            "scan_mapping": "Column of each section from the TLA column,line numbers; frame of each column from the SMB object titles "
                            "('Kol. I - III, auf Recto' etc.); every photograph checked by eye for the number and order of its columns.",
            "scan_mapping_urls": ["https://id.smb.museum/object/3437568", "https://id.smb.museum/object/792723",
                                  "https://id.smb.museum/object/792727", "https://id.smb.museum/object/792730"],
            "scan_local_paths": scans,
            "original_text_source": f"Thesaurus Linguae Aegyptiae, TLA database extract January 2018 (urn:nbn:de:kobv:b4-opus4-29190), "
                                    f"AED-TEI text {TLA_ID}: https://github.com/simondschweitzer/aed-tei/blob/master/files/{TLA_ID}.xml",
            "original_text_license": "CC BY-SA 4.0 (BBAW / SAW Leipzig, Thesaurus Linguae Aegyptiae; AED-TEI)",
            "translation_source": "W. M. Flinders Petrie, Egyptian Tales, Translated from the Papyri, First Series, IVth to XIIth Dynasty "
                                  "(2nd ed., London: Methuen, 1899), 'Tales of the Magicians', Project Gutenberg #7386: https://www.gutenberg.org/ebooks/7386",
            "translation_license": "public domain (published 1895/1899)",
            "translator": "W. M. Flinders Petrie (1899)",
            "verified_date": TODAY,
        },
    }
    PUB.joinpath(f"{TID}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {TID}: {len(secs)} sections")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Papyrus Westcar (Tales of the Magicians)", "group": "Egypt",
            "date_sort": -1600,
            "author_name": "Papyrus Westcar (Second Intermediate Period, c. 1650-1550 BCE)",
            "source_url": "https://id.smb.museum/object/606402",
            "critical_edition": "Thesaurus Linguae Aegyptiae (2018 data, AED-TEI)",
            "translator_name": "W. M. Flinders Petrie (1899)",
            "original_lang_label": "Egyptian · TLA transliteration",
            "original_lang_code": "egy",
            "edition_label": "Hieroglyphic transcription (TLA, Unicode)",
            "search_terms": "westcar papyrus khufu cheops magicians djedi dedi webaoner wax crocodile sneferu rowing girls ruddjedet tales",
            "description": "Papyrus Westcar (Berlin P 3033): the tales of wonders told at the court of King Khufu, column by column on the "
                           "Berlin photographs, with TLA transliteration and hieroglyphs and Petrie's English.",
        },
        "texts": [{
            "id": TID, "slug": TID, "order": 1, "title": entry["title"], "author_id": "egyptian-scribes",
            "language": "Egyptian", "era": "Ancient Near East", "tradition": "egyptian", "category": "literature",
            "date_approx": "Middle Kingdom composition; manuscript c. 1650-1550 BCE", "century": -17,
            "source": entry["source"], "description": entry["description"],
            "themes": ["westcar", "khufu", "magic", "tales", "egypt", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f"{KEY}/{FRAMES[f][0]}", "caption": f"Papyrus Westcar, {FRAMES[f][3]}"} for f in FRAMES]},
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
