#!/usr/bin/env python3
"""
import_berossus.py - Berossus of Babylon, Babyloniaka (c. 290-278 BCE): the Greek fragments
on Oannes, the creation, the ten kings before the flood, Xisouthros and the flood, and the
Neo-Babylonian kings, each section linked to the manuscript page that carries it.

Five entries:
  1. oannes       Polyhistor's summary of book 1 (Oannes, the creation)      Syncellus, Paris gr. 1711 pp. 18-19
  2. flood        Polyhistor on book 2 (the ten kings, Xisouthros' flood)     Paris gr. 1711 pp. 19-20
  3. apollodorus  Apollodorus' list of the ten kings and the Annedotoi        Paris gr. 1711 pp. 25-26
  4. abydenus     Abydenus' version of the kings and the flood                Paris gr. 1711 p. 25
  5. josephus     Josephus, Against Apion 1.128-153 (book 3: Nebuchadnezzar)  Laur. Plut. 69.22 fols. 10r-11v

Chain of evidence:
  1. SCANS    (a) Paris, BnF, grec 1711 (11th c.), George Syncellus' Ecloga chronographica,
              paginated 1-230; Gallica ark:/12148/btv1b10723005g (black-and-white microfilm,
              double-page openings; page p sits on image f(14 + p//2), left page even).
              IIIF: openapi.bnf.fr. Terms: Gallica non-commercial reuse with credit
              "Source gallica.bnf.fr / BnF".
              (b) Florence, Biblioteca Medicea Laurenziana, Plut. 69.22 (10th c., 37 fols.),
              Josephus, Contra Apionem book 1; Teca Digitale IIIF (cdm21059.contentdm.oclc.org,
              record plutei 1350351), access "Pubblico".
  2. MAPPING  By eye on the downloaded images (no published folio list was used). For each
              page the first and last lines were read and found in the edition; section
              positions are given as line numbers counted on the page, with opening words.
                Paris gr. 1711 p. 18 l. 11: heading "Ἐκ τῶν Ἀλεξάνδρου τοῦ Πολυΐστορος" after a
                  dotted rule; l. 14 "Βήρωσσος δὲ ἐν τῇ πρώτῃ"; l. 26 "ἐν δὲ τῷ πρώτῳ ἐνιαυτῷ"
                  (margin: ὠάννης); page ends "...ζῶα τερατώδη" (§4).
                p. 19 begins "καὶ εἰδιφυεῖς τὰς ἰδέας"; l. 24 "...φάσκειν· ἐν τῇ δευτέρᾳ";
                  l. 28 "Ἀρδάτου δὲ τελευτήσαντος"; page ends "...ἀφιέναι τὰ ὄρνεα".
                p. 20 begins "ταῦτα δὲ πάλιν"; flood text ends l. 19 "ἐπικτίσαι τὴν Βαβυλῶνα".
                p. 25 l. 9 heading "Ἐκ τῶν Ἀβυδηνοῦ. Περὶ τῆς τῶν Χαλδαίων βασιλείας"; Abydenus
                  ends l. 29 "παρείχετο"; l. 33 "πρὸς τούτοις καὶ Ἀπολλόδωρος"; page ends
                  "...πρὸς ἀνθρώπους μίξιν".
                p. 26 begins "εἶτα ἄρξαι Εὐεδώραχον"; Apollodorus ends l. 8 "σάρους δὲ ρκʹ".
                Laur. Plut. 69.22 fol. 10r l. 6 "Λέξω δὲ νῦν ἤδη" (1.128), page ends "...περὶ τὴν
                  Συ|ρίαν" (1.135); 10v begins "τὴν κοίλην", ends "...ὑψηλὰ ἀνοικοδομήσας"
                  (1.141); 11r begins "καὶ τὴν ὄψιν ἀποδοὺς", ends "...ἀπετυμπανίσθη" (end of
                  1.148); 11v begins "ἀπολομένου δὲ τούτου" (1.149), 1.153 ends l. 20 "κατέ|στρεψε
                  τὸν βίον".
  3. GREEK    Syncellus fragments: C. Müller, Fragmenta Historicorum Graecorum II (Paris 1848)
              pp. 496-502 (Berosus fr. 1, 4, 6, 7) and IV (1851) p. 280 (Abydenus fr. 1), via the
              Digital Fragmenta Historicorum Graecorum (DFHG, Leipzig; dfhg-project.org,
              CC BY-NC-SA 4.0) API, cached in data/sources/berossus/dfhg-*.json. The DFHG OCR was
              proofread against Müller's printed pages (archive.org fragmentahistori02mueluoft,
              fragmentahistori04mueluoft); every correction is listed in FIXES below and asserted.
              Müller's Latin and Greek apparatus notes in parentheses are removed (they are not
              part of the text); his square brackets are kept.
              Josephus: B. Niese, Flavii Iosephi opera V (1889), Perseus canonical-greekLit
              tlg0526.tlg003.perseus-grc2 (CC BY-SA 4.0).
  4. ENGLISH  Syncellus fragments: I. P. Cory, Ancient Fragments, 2nd ed. (London 1832), public
              domain; transcription by C. M. Weimer (sacred-texts.com/cla/af, 2002, Wayback
              captures cached in data/sources/berossus/cory1832/), checked word by word against
              the OCR of the 1832 printing (archive.org ancientfragments00coryrich); the two
              disagreements were settled on the page images (FIXES_EN). Cory's footnote markers
              and source citations are removed.
              Josephus: William Whiston (1737), Project Gutenberg eBook #2849 (public domain),
              three transcription faults corrected against the 1860 printing
              (archive.org worksofflaviusjo00jose_0).

Usage:
    python3 scripts/import_berossus.py           # build
    python3 scripts/import_berossus.py --force   # re-download scans
"""

import argparse
import html
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "berossus"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
NUM = "ʹ"  # Greek numeral sign

GALLICA_ARK = "btv1b10723005g"
GALLICA_URL = f"https://gallica.bnf.fr/ark:/12148/{GALLICA_ARK}"
LAUR_RECORD = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/1350351"
LAUR_IIIF = {
    "10r": "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:1350287",
    "10v": "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:1350288",
    "11r": "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:1350289",
    "11v": "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:1350290",
}
DFHG_API = "http://www.dfhg-project.org/DFHG/api.php"
MUELLER_II = "https://archive.org/details/fragmentahistori02mueluoft"
MUELLER_IV = "https://archive.org/details/fragmentahistori04mueluoft"
CORY_SCAN = "https://archive.org/details/ancientfragments00coryrich"
CORY_ST = "https://sacred-texts.com/cla/af/"
WHISTON_PG = "https://www.gutenberg.org/ebooks/2849"
WHISTON_1860 = "https://archive.org/details/worksofflaviusjo00jose_0"
PERSEUS_GRC = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0526/tlg003/tlg0526.tlg003.perseus-grc2.xml"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return r.read()


def save_jpeg(img, path, long_side=2400):
    img = img.convert("RGB")
    w, h = img.size
    s = long_side / max(w, h)
    if s < 1:
        img = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
    img.save(path, quality=85)


# ---------------------------------------------------------------- scans

def gallica_page(page, force):
    """Paris gr. 1711 page `page`: image f(14 + page//2), left half if even."""
    path = SCAN_DIR / f"paris-gr-1711-p{page:03d}.jpg"
    if path.exists() and not force:
        return path
    f = 14 + page // 2
    img = Image.open(io.BytesIO(fetch(
        f"https://openapi.bnf.fr/iiif/image/v3/ark:/12148/{GALLICA_ARK}/f{f}/full/6000,/0/default.jpg")))
    w, h = img.size
    small = img.convert("L").resize((w // 10, h // 10))
    px = small.load()
    sw, sh = small.size
    cols = range(int(sw * 0.4), int(sw * 0.6))
    gutter = min(cols, key=lambda x: sum(px[x, y] for y in range(sh))) * 10  # darkest column
    box = (0, 0, gutter, h) if page % 2 == 0 else (gutter, 0, w, h)
    save_jpeg(img.crop(box), path)
    return path


def laur_page(folio, force):
    path = SCAN_DIR / f"laur-plut-69-22-f{folio.zfill(4)}.jpg"
    if path.exists() and not force:
        return path
    save_jpeg(Image.open(io.BytesIO(fetch(f"{LAUR_IIIF[folio]}/full/full/0/default.jpg"))), path)
    return path


def gallica_view(page):
    return f"{GALLICA_URL}/f{14 + page // 2}.item"


# ---------------------------------------------------------------- Greek (Müller via DFHG)

def apply(text, fixes, label):
    for old, new in fixes:
        assert text.count(old) >= 1, (label, old)
        text = text.replace(old, new)
    return text


def norm_greek(t):
    t = re.sub(r" ?̓ ?", "’ ", t)          # DFHG elision mark "κατ ̓ αὐτοὺς" -> "κατ’ αὐτοὺς"
    t = t.replace("’ ,", "’,")
    t = re.sub(r"(?<=[α-ω])'", NUM, t)               # numerals "ιε'" -> "ιεʹ"
    t = t.replace("ʹ", NUM)
    return re.sub(r"\s+", " ", t).strip()


def dfhg(author_file, witness_start):
    rows = json.loads((SRC / author_file).read_text(encoding="utf-8"))
    hits = [r for r in rows if r["witness"].strip().startswith(witness_start)]
    assert len(hits) == 1, (author_file, witness_start, len(hits))
    return hits[0]["text"]


# corrections checked against Müller's printed page images (FHG II pp. 496-502, IV p. 280)
FIX_F1 = [
    ("Πολυίστορος", "Πολυΐστορος"), ("Πολυίστωρ", "Πολυΐστωρ"),           # printed with diaeresis
    ("κατακλυσοῦ", "κατακλυσμοῦ"), ("ῥόζας", "ῥίζας"), ("ἄρνεα", "ὄρνεα"),
    ("χερσαῖά τε ̓ καὶ", "χερσαῖά τε καὶ"),
    ("ἄφορα εὔφορα Goar.). Ἐν", "ἄφορα. Ἐν"),                             # apparatus note
    ("ἄφρενον (ἄρρεν ὂν J. Voss.)", "ἄφρενον"),
    ("τὴν κεφαλὴ παραπεφυκυῖαν", "τὴν κεφαλὴν παραπεφυκυῖαν"),
    ("τῆς τοῦ τοῦ ἰχθύος", "τῆς τοῦ ἰχθύος"), ("ἀνθρωπου", "ἀνθρώπου"),
    ("τουτονὶ (τοῦτο s. τουτί?)", "τουτονὶ"), ("ἕτερα ζῶν ὅμοια", "ἕτερα ζῶα ὅμοια"),
    ("εἰδφυεῖς (ἰδιοφυεῖς recte Richter.; αὐτοφυεῖς Mai.; διφυεῖς Scalig.)", "εἰδιφυεῖς"),
    ("ἐνίου δὲ", "ἐνίους δὲ"), ("ἕτερα ζῶν κεφαλὰς", "ἕτερα ζῶα κεφαλὰς"),
    ("τοῦ Βάλου ναῷ", "τοῦ Βήλου ναῷ"), ("Ὁμόρωκα (Ὀμόρκα Scalig.)", "Ὁμόρωκα"),
    ("σελήνη, quod Syncelli, ut videtur, addidamentum]", "σελήνη]"),
    ("τὸν βῆλον", "τὸν Βῆλον"),
    (" Ἐν δὲ τῇ δευτέρᾳ κτλ. (v. fr. 4).", ""),
]
FIX_F4 = [("Πολυίστωρ", "Πολυΐστωρ"), ("φάσκειν (fr. 1). ἐν δὲ", "φάσκειν. Ἐν δὲ"),
          ("κατακλυσμοῦ· λέγει γὰρ κτλ. (Vide fragm. 7).", "κατακλυσμοῦ·")]
FIX_F7 = [
    ("Λέγει γὰρ ὁ αὐτὸς", "λέγει γὰρ ὁ αὐτὸς"),                            # continues F4 in Syncellus
    ("Ἀρδάτου (deb. Ὀτιάρτου)", "Ἀρδάτου"),
    ("Σισπάροις (Σιππάροις Scaliger)", "Σισπάροις"),
    ("ἐνθέσθαι δὲ βρώματα καὶ πάντα εὐτρεπισάμενον",                      # line dropped by the OCR
     "ἐνθέσθαι δὲ βρώματα καὶ πόματα, ἐμβαλεῖν δὲ καὶ ζῶα πτηνὰ καὶ τετράποδα, καὶ πάντα εὐτρεπισάμενον"),
    ("εὐξάμενον (εὐξόμενον Scal.)", "εὐξάμενον"), ("πέντε (quindecim, Eus.)", "πέντε"),
    ("Ξίσουθρον (aliter Euseb.)", "Ξίσουθρον"), ("καὶ γὰρ (vgo παρ ̓) αὐτὸν", "καὶ γὰρ αὐτὸν"),
    ("Σισπάρων (l. Σιππάρων)", "Σισπάρων"), ("πέριξ (scr. πεζῇ; pedestri itinere Eus.)", "πέριξ"),
    ("πάλεις", "πόλεις"),
]
FIX_F6 = [
    ("Πρὸ τούτοις", "Πρὸς τούτοις"), ("Παντιβίβλων (Πανταβ. Cod. A Dindorfii)", "Παντιβίβλων"),
    ("μυσαρὸν (δεύτερον?) Ὠάννην", "μυσαρὸν Ὠάννην"), ("τεσσαράκοντα(?)·", "τεσσαράκοντα·"),
    ("Ἀβυδηνὸς (fr. 1) τὸν", "Ἀβυδηνὸς τὸν"), ("τέταρτον (Ct. Euseb.)", "τέταρτον"),
    ("Εὐεδώραχον (sic cod. A. Εὐερώδεσχον Goar.)", "Εὐεδώραχον"), ("Ὠδάκων (Ὀδάκων G.)", "Ὠδάκων"),
    ("Ἀβυδηνὸς (fr. 1) οὐδὲν", "Ἀβυδηνὸς οὐδὲν"),
]
FIX_AB = [
    ("ἀποδείξαι", "ἀποδεῖξαι"), ("Παντιβίβλιος (Παυτιβίβλιος cod. A.)", "Παντιβίβλιος"),
    ("Ὠάννῃ τὴν τὴν ἰδέαν", "Ὠάννῃ τὴν ἰδέαν"), ("Ἡλιουπόλει τῆ ἐν", "Ἡλιουπόλει τῇ ἐν"),
    ("Σισπόροισιν (l. Σιππάροισιν ex Euseb.)", "Σισπόροισιν"), ("ἔτεραι", "ἕτεραι"),
]


def cut(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) + len(end) if end else len(text)
    return text[i:j].strip()


def greek_sections():
    f1 = norm_greek(apply(dfhg("dfhg-berosus.json", "Syncell. p. 28, B"), FIX_F1, "F1"))
    f4 = norm_greek(apply(dfhg("dfhg-berosus.json", "Syncell. p. 30, A:"), FIX_F4, "F4"))
    f7 = norm_greek(apply(dfhg("dfhg-berosus.json", "Syncell. p. 30, A (cf. fr. 4)"), FIX_F7, "F7"))
    f6 = norm_greek(apply(dfhg("dfhg-berosus.json", "Syncell. P. 39, B"), FIX_F6, "F6"))
    ab = norm_greek(apply(dfhg("dfhg-abydenus.json", "Syncellus p. 38, B"), FIX_AB, "Ab1"))
    for t in (f1, f4, f7, f6, ab):
        assert not re.search(r"[A-Za-z]{3}", t.replace("Goar", "")), t[:200]   # no Latin left
    g = {}
    # Müller's paragraph numbers "1." .. "6." in F1 and "(2)" .. "(7)" in F7 become <sup>
    p = re.split(r" ?(?<![\w])([1-6])\. (?=[Α-ΩἈ-Ὧ])", f1)
    head, paras = p[0], dict(zip(p[1::2], p[2::2]))
    assert head.startswith("(Ἐκ τοῦ Ἀλεξάνδρου") and set(paras) == set("123456"), (head[:40], paras.keys())
    g["oannes"] = {
        "1": f"{head} <sup>1</sup>{paras['1']}",
        **{n: f"<sup>{n}</sup>{paras[n]}" for n in "23456"},
    }
    assert g["oannes"]["6"].endswith("ἐν τῇ πρώτῃ φάσκειν."), g["oannes"]["6"][-60:]
    second = cut(f4, "Ἐν δὲ τῇ δευτέρᾳ")
    q = re.split(r" \(([2-7])\) | (4)\. ", f7)
    q = [x for x in q if x is not None]
    first, fl = q[0], dict(zip(q[1::2], q[2::2]))
    assert set(fl) == set("234567"), fl.keys()
    fl["7"] = cut(fl["7"], "Τοῦ δὲ πλοίου", "πάλιν ἐπικτίσαι τὴν Βαβυλῶνα.")   # drop Syncellus' "Τούτων δὴ ..."
    g["flood"] = {"1": f"{second} {first}", **{n: f"<sup>{n}</sup>{fl[n]}" for n in "234567"}}
    k = f6.index("Εἶτα ἄρξαι Εὐεδώραχον")
    g["apollodorus"] = {"1": f6[:k].strip(), "2": f6[k:].strip()}
    k = ab.index("Καὶ περὶ τοῦ κατακλυσμοῦ")
    g["abydenus"] = {"1": ab[:k].strip(), "2": ab[k:].strip()}
    return g


# ---------------------------------------------------------------- English (Cory 1832)

FIXES_EN = [("gongre", "gongæ"),                                   # printed "gongæ" (1832, p. 21)
            ("and reduced universe to order", "and reduced the universe to order")]  # 1832, p. 24


def cory_paragraphs(name, start):
    raw = (SRC / "cory1832" / name).read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", raw, flags=re.S)
    blocks = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", b))).strip()
              for b in re.split(r"<p[^>]*>|<h[23][^>]*>", raw)]
    k = next(i for i, b in enumerate(blocks) if b.startswith(start))
    paras = []
    for b in blocks[k:]:
        if b == "Next" or b.startswith("Next "):
            break
        if b:
            paras.append(b)
    out = []
    for t in paras:
        t = re.sub(r"(?<=[A-Za-zæ\.,;:])\d+(?=[\s,;:\.\)]|$)", "", t)          # footnote markers
        t = re.sub(r"\s*—Syncel\..*$", "", t)                                    # Cory's citations
        for old, new in FIXES_EN:
            t = t.replace(old, new)
        out.append(t.strip())
    return out


def split_at(text, marker):
    i = text.index(marker)
    return text[:i].strip(), text[i:].strip()


def english_sections():
    e = {}
    a = cory_paragraphs("af02.htm", "BEROSSUS, in the first")
    a = [x for x in a if not x.startswith("Next")]
    assert a[0].startswith("BEROSSUS, in the first") and a[-1].startswith("The vessel being thus"), (a[0][:30], a[-1][:30])
    babylon, oannes = split_at(a[2], "In the first year there appeared")
    omoroca, rest = split_at(a[5], "All things being in this situation")
    belus5, belus6 = split_at(rest, "This Belus, by whom")
    head = "BEROSSUS: FROM ALEXANDER POLYHISTOR. OF THE COSMOGONY AND DELUGE."
    e["oannes"] = {
        "1": f"{head} <sup>1</sup>{a[0]}",
        "2": f"<sup>2</sup>{a[1]} {babylon}",
        "3": f"<sup>3</sup>{oannes} {a[3]}",
        "4": f"<sup>4</sup>{a[4]} {omoroca}",
        "5": f"<sup>5</sup>{belus5}",
        "6": f"<sup>6</sup>{belus6}",
    }
    xis, cronus = split_at(a[7], "The Deity, Cronus")
    cronus, ship = split_at(cronus, "He then obeyed the divine admonition")
    remained, added = split_at(a[9], "To this he added")
    e["flood"] = {
        "1": f"{a[6]} {xis}", "2": f"<sup>2</sup>{cronus}", "3": f"<sup>3</sup>{ship}",
        "4": f"<sup>4</sup>{a[8]}", "5": f"<sup>5</sup>{remained}", "6": f"<sup>6</sup>{added}",
        "7": f"<sup>7</sup>{a[10]}",
    }
    b = [x for x in cory_paragraphs("af03.htm", "THIS is the history") if not x.startswith("Next")]
    assert len(b) == 1, b
    p1, p2 = split_at(b[0], "Then reigned Euedorachus")
    e["apollodorus"] = {"1": f"BEROSSUS: FROM APOLLODORUS. OF THE CHALDÆAN KINGS. {p1}", "2": p2}
    c = cory_paragraphs("af04.htm", "So much concerning")
    c = c[:c.index(next(x for x in c if x.startswith("THE TOWER OF BABEL")))]
    assert len(c) == 3, c
    k1, k2 = split_at(c[2], "(And among other things")
    e["abydenus"] = {"1": f"BEROSSUS: FROM ABYDENUS. OF THE CHALDÆAN KINGS AND THE DELUGE. {c[0]} {c[1]} {k1}", "2": k2}
    return e


# ---------------------------------------------------------------- Josephus

WHISTON_FIXES = [
    ("in oilier things also", "in other things also"),
    ("by Semiramis, [14] queen of Assyria, and for her false pretense to those wonderful edifices thereto buildings at Babylon, do no way contradict those ancient and relating,",
     "by Semiramis, queen of Assyria, and for her false pretense to those wonderful edifices thereto relating,"),
    ("kept it nine mouths", "kept it nine months"),
]
# Whiston's chapters 19-20 split at Niese's section openings (marker = first words of each section)
WHISTON_MARKS = [
    ("128", "I will now relate"), ("129", "Berosus shall be witness"), ("130", "This Berosus, therefore,"),
    ("131", "after which he gives us a catalogue"), ("132", "he describes to us how"),
    ("133", "He then says,"), ("134", "A little after which"), ("135", '"When Nabolassar,'),
    ("136", "Nabuchodonosor joined battle"), ("137", "But as he understood"), ("138", "whither, when he was come"),
    ("139", "but for himself, he adorned"), ("140", "So when he had thus fortified"),
    ("141", "Now in this palace"), ("142", "This is what Berosus relates"),
    ("143", "as indeed in these affairs"), ("144", "in which case Philostratus"),
    ("145", "Now as to what I have said before"), ("146", "for thus he says in his third book"),
    ("147", "He governed public affairs"), ("148", "his son Laborosoarchod"),
    ("149", "After his death, the conspirators"), ("150", "but when he was come to the seventeenth"),
    ("151", "When Nabonnedus perceived"), ("152", "Hereupon Cyrus took Babylon"),
    ("153", "but as Nabonnedus did not sustain"),
]
JOS_PAGES = {  # Niese section -> folios of Laur. Plut. 69.22 that carry it (from the page breaks read on the images)
    **{str(n): ["10r"] for n in range(128, 135)}, "135": ["10r", "10v"],
    **{str(n): ["10v"] for n in range(136, 141)}, "141": ["10v", "11r"],
    **{str(n): ["11r"] for n in range(142, 149)}, **{str(n): ["11v"] for n in range(149, 154)},
}
JOS_PAGE_NOTE = {
    "10r": "Fol. 10r (Teca Digitale image 10r): 1.128 begins on line 6 'Λέξω δὲ νῦν ἤδη τὰ παρὰ Χαλδαίοις' (marked in the margin) after the last words of 1.127 'διὰ τῆς ἀρχαιολογίας'; the page ends in 1.135 with '...καὶ τοῖς περὶ τὴν Συ-|ρίαν'.",
    "10v": "Fol. 10v: begins 'τὴν κοίλην καὶ τὴν Φοινίκην τόποις ἀποστάτης γέγονεν' (1.135) and ends '...βασιλείοις τούτοις ἀναλήμματα λίθινα ὑψηλὰ ἀνοικοδομήσας' (1.141).",
    "11r": "Fol. 11r: begins 'καὶ τὴν ὄψιν ἀποδοὺς ὁμοιοτάτην τοῖς ὄρεσι' (1.141) and ends with the last words of 1.148 'ὑπὸ τῶν φίλων ἀπετυμπανίσθη'.",
    "11v": "Fol. 11v: begins 'ἀπολομένου δὲ τούτου συνελθόντες' (1.149, line 1); 1.153 ends on line 20 'κατέ|στρεψε τὸν βίον', followed by Josephus' comment 'ταῦτα σύμφωνα ἔχει ταῖς ἡμετέραις βίβλοις'.",
}


def josephus_sections():
    root = ET.parse(SRC / "perseus" / "tlg0526.tlg003.perseus-grc2.xml").getroot()
    grc = {}
    for b in root.iter(f"{TEI}div"):
        if b.get("subtype") == "book" and b.get("n") == "1":
            for s in b.iter(f"{TEI}div"):
                if s.get("subtype") == "section" and 128 <= int(s.get("n")) <= 153:
                    assert not list(s.iter(f"{TEI}note"))
                    grc[s.get("n")] = re.sub(r"\s+", " ", "".join(s.itertext())).strip()
    assert len(grc) == 26
    pg = (SRC / "gutenberg" / "pg2849.txt").read_text(encoding="utf-8").replace("\r", "")
    i = pg.index("19. I will now relate what hath been written")
    j = pg.index("Accordingly Nabonnedus spent the rest of his time in that country, and there\ndied.\"") + len(
        "Accordingly Nabonnedus spent the rest of his time in that country, and there\ndied.\"")
    t = re.sub(r"\s+", " ", pg[i:j])
    t = t.replace("19. I will now", "I will now").replace(' 20. This is what', ' This is what')
    for old, new in WHISTON_FIXES:
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    eng, pos = {}, [t.index(m) for _, m in WHISTON_MARKS]
    assert pos == sorted(pos), pos
    for (n, _), a, b in zip(WHISTON_MARKS, pos, pos[1:] + [len(t)]):
        eng[n] = t[a:b].strip()
    return grc, eng


# ---------------------------------------------------------------- entries

def gal_note(page, text):
    return (f"Paris gr. 1711, p. {page} (Gallica image f{14 + page // 2}, {'left' if page % 2 == 0 else 'right'} page of the "
            f"opening; microfilm). {text} Checked on the image. Viewer: {gallica_view(page)}")


SYNC_NOTE = ("The Greek shown is Müller's edited text; the copyist's wording on the page differs in places "
             "(for example the manuscript reads Κορκυραίων where Müller prints Κορδυαίων).")

ENTRIES = [
    {
        "slug": "oannes", "order": 1,
        "title": "Berossus, Babyloniaka book 1: Oannes and the creation (Alexander Polyhistor in George Syncellus)",
        "description": "Berossus' account, as summarized by Alexander Polyhistor and copied by George Syncellus, of the records kept at Babylon, the fish-man Oannes who taught writing, cities, laws and agriculture, and the creation of the world by Bel from the body of Omoroka, shown on the two pages of Paris gr. 1711 that carry it.",
        "pages": [18, 19],
        "sections": [
            ("1", "Berossus F 1 (Müller fr. 1 §1); Syncellus p. 28 Goar; Paris gr. 1711 p. 18 ll. 11-18", [18],
             "Below a dotted rule that closes the previous extract, line 11 opens Syncellus' heading 'Ἐκ τῶν Ἀλεξάνδρου τοῦ Πολυΐστορος περὶ τῶν πρὸ τοῦ κατακλυσμοῦ βασιλευσάντων ι´ βασιλέων' (lines 11-14). After 'γεγραμμένα:' on line 14 the text begins 'Βήρωσσος δὲ ἐν τῇ πρώτῃ τῶν Βαβυλωνιακῶν' and §1 runs to '...καὶ τῶν κατ’ αὐτοὺς πράξεων' on line 18."),
            ("2", "Müller fr. 1 §2; Paris gr. 1711 p. 18 ll. 18-25", [18],
             "§2 begins on line 18 'καὶ πρῶτον μὲν τὴν Βαβυλωνίων γῆν' and ends on line 25 '...ζῆν δὲ αὐτοὺς ἀτάκτως ὥσπερ τὰ θηρία'."),
            ("3", "Müller fr. 1 §3 (Oannes); Paris gr. 1711 p. 18 ll. 26-40", [18],
             "§3 begins at the start of line 26 'ἐν δὲ τῷ πρώτῳ ἐνιαυτῷ φανῆναι ἐκ τῆς ἐρυθρᾶς θαλάσσης', with the marginal note 'ὠάννης' beside it, and ends on line 40 '...τόνδε τὸν λόγον τοῖς ἀνθρώποις'."),
            ("4", "Müller fr. 1 §4; Paris gr. 1711 p. 18 ll. 40-41 and p. 19 ll. 1-12", [18, 19],
             "§4 begins at the end of line 40 of p. 18 'γε-|νέσθαι φησὶ χρόνον ἐν ᾧ τὸ πᾶν σκότος'; p. 18 ends '...ζῶα τερατώδη', and p. 19 begins 'καὶ εἰδιφυεῖς τὰς ἰδέας ἔχοντα ζωογονεῖσθαι'. The section ends on p. 19 line 12 '...κατὰ δὲ ἰσόψηφον σελήνη', which the manuscript has in the running text."),
            ("5", "Müller fr. 1 §5; Paris gr. 1711 p. 19 ll. 13-18", [19],
             "§5 begins on line 13 'οὕτως δὲ τῶν ὅλων συνεστηκότων ἐπανελθόντα' and ends on line 18 '...φρονήσεως θείας μετέχειν'."),
            ("6", "Müller fr. 1 §6; Paris gr. 1711 p. 19 ll. 18-24", [19],
             "§6 begins on line 18 'τὸν δὲ Βῆλον ὃν Δία μεθερμηνεύουσι' and ends on line 24 'ταῦ-|τά φησιν ὁ Πολυΐστωρ Ἀλέξανδρος τὸν Βήρωσσον ἐν τῇ πρώτῃ φάσκειν'."),
        ],
    },
    {
        "slug": "flood", "order": 2,
        "title": "Berossus, Babyloniaka book 2: the ten kings and the flood of Xisouthros (Alexander Polyhistor in George Syncellus)",
        "description": "Berossus on the ten kings who reigned 120 sars (432,000 years) before the flood and on Xisouthros, warned by Kronos in a dream, who buried the writings at Sippar, built a ship, sent out birds and was taken to live with the gods, shown on the two pages of Paris gr. 1711 that carry it.",
        "pages": [19, 20],
        "sections": [
            ("1", "Müller fr. 4 (Syncellus p. 30 Goar) and fr. 7 §1; Paris gr. 1711 p. 19 ll. 24-30", [19],
             "The summary of book 2 begins at the end of line 24 'ἐν τῇ | δευτέρᾳ τοὺς ι´ βασιλέας τῶν Χαλδαίων'; line 26 'λέγει γὰρ ὁ αὐτὸς Ἀλέ-|ξανδρος'; the quotation 'Ἀρδάτου δὲ τελευτήσαντος' begins at the end of line 28, and the section ends on line 30 'ἀναγεγράφθαι δὲ τὸν λόγον οὕτως'."),
            ("2", "Müller fr. 7 §2; Paris gr. 1711 p. 19 ll. 30-36", [19],
             "§2 begins on line 30 'τὸν Κρόνον αὐτῷ κατὰ τὸν ὕπνον' and ends on line 36 '...ἀνθρώποις ἀγαθὰ γενέσθαι'."),
            ("3", "Müller fr. 7 §3; Paris gr. 1711 p. 19 ll. 36-38", [19],
             "§3 begins on line 36 'τὸν δὲ οὐ παρακούσαντα ναυ-|πηγῆσαι σκάφος' and ends on line 38 '...τοὺς ἀναγκαίους φίλους ἐμβιβάσαι'."),
            ("4", "Müller fr. 7 §4; Paris gr. 1711 p. 19 ll. 39-41 and p. 20 ll. 1-6", [19, 20],
             "§4 begins on p. 19 line 39 'γενομένου δὲ τοῦ κατακλυσμοῦ καὶ εὐθέως λήξαντος' (corrections in the left margin); p. 19 ends '...μετά τινας ἡμέρας ἀφιέναι τὰ ὄρνεα', p. 20 begins 'ταῦτα δὲ πάλιν εἰς τὴν ναῦν ἐλθεῖν', and the section ends on p. 20 line 6 '...γενέσθαι μετὰ τῶν ἐκβάν-|των τοῦ πλοίου ἀφανῆ'."),
            ("5", "Müller fr. 7 §5; Paris gr. 1711 p. 20 ll. 6-11", [20],
             "§5 begins on line 6 'τοὺς δὲ ὑπομείναντας ἐν τῷ πλοίῳ' and ends on line 11 '...τὸν κυβερνήτην μετεσχηκέναι'."),
            ("6", "Müller fr. 7 §6; Paris gr. 1711 p. 20 ll. 11-14", [20],
             "§6 begins on line 11 'εἰπεῖν τε αὐτοῖς ὅτι ἐλεύσονται πάλιν εἰς Βαβυλῶνα' and ends on line 14 '...πορευθῆναι εἰς Βαβυλῶνα'."),
            ("7", "Müller fr. 7 §7; Paris gr. 1711 p. 20 ll. 14-19", [20],
             "§7 begins on line 14 'τοῦ δὲ πλοίου τούτου κατακλιθέντος ἐν τῇ Ἀρμενίᾳ'; line 15 reads 'ἐν τοῖς Κορκυραίων ὄρεσι' (Cory's 'Corcyræan mountains'); the extract ends on line 19 '...ἐπικτίσαι τὴν Βα-|βυλῶνα', where Syncellus' comment 'Τούτων δὴ ἀπὸ Ἀλεξάνδρου τοῦ Πολυΐστορος' begins."),
        ],
    },
    {
        "slug": "apollodorus", "order": 3,
        "title": "Berossus in Apollodorus: the ten kings before the flood and the fish-men Annedotoi (George Syncellus)",
        "description": "Apollodorus' list, from Berossus, of the ten Chaldean kings from Aloros to Xisouthros with their reigns in sars, and of the fish-men (Oannes, the Annedotoi, Odakon) who came up from the Red Sea, shown on the two pages of Paris gr. 1711 that carry it.",
        "pages": [25, 26],
        "sections": [
            ("1", "Müller fr. 6 (Syncellus p. 39 Goar); Paris gr. 1711 p. 25 ll. 33-41", [25],
             "Syncellus introduces the extract on line 33 'πρὸς τούτοις καὶ Ἀπολλόδωρος ὁμοίως τούτοις τερατευό-|μενος οὕτω λέγει'; line 34 'ταῦτα μὲν ὁ Βήρωσσος ἱστόρησε· πρῶτον γενέσθαι βασιλέα Ἄλωρον'; the page ends on line 41 '...καὶ τὴν ἰχθύος πρὸς ἀνθρώπους μίξιν'. A marginal note beside line 38 names Abydenus."),
            ("2", "Müller fr. 6, continued; Paris gr. 1711 p. 26 ll. 1-8", [26],
             "p. 26 begins 'εἶτα ἄρξαι Εὐεδώραχον ἐκ Παντιβίβλων'; line 4 'περὶ τούτου Ἀβυδηνὸς οὐδὲν εἶπεν'; the extract ends on line 8 'πάντας βασιλεῖς ι´ σάρους δὲ ρκ´'."),
        ],
    },
    {
        "slug": "abydenus", "order": 4,
        "title": "Berossus in Abydenus: the kings of the Chaldeans and the flood of Sisithros (George Syncellus)",
        "description": "Abydenus' retelling of Berossus in Ionic Greek: Aloros the shepherd of the people, the sar of 3,600 years, the Annedotoi who came up from the sea, and Sisithros, who hid the writings at Sippar and sailed to Armenia, shown on the page of Paris gr. 1711 that carries it.",
        "pages": [25],
        "sections": [
            ("1", "Abydenus fr. 1 (Müller FHG IV 280; Syncellus p. 38 Goar); Paris gr. 1711 p. 25 ll. 9-20", [25],
             "Line 9 is the heading 'Ἐκ τῶν Ἀβυδηνοῦ. Περὶ τῆς τῶν Χαλδαίων βασιλείας', followed on line 10 by 'Χαλδαίων μὲν τῆς σοφίης πέρι τοσαῦτα' (the margin beside it notes 'Ἄλωρος πρῶτος βασιλεὺς Χαλδαίων'); the list of kings ends on line 20 'συνῆξε σάρους ρκ´'."),
            ("2", "Abydenus fr. 1, the flood; Paris gr. 1711 p. 25 ll. 20-29", [25],
             "The flood begins on line 20 'καὶ περὶ τοῦ κατακλυσμοῦ παρόμοια μέν, οὐκ ἀπαράλλα-|κτα' and ends on line 29 '...τοῖσιν ἐπιχωρίοισι παρείχετο'."),
        ],
    },
]


def build_sync_entry(spec, gk, en, force):
    paths = {p: gallica_page(p, force) for p in spec["pages"]}
    sections = []
    for sid, ref, pages, note in spec["sections"]:
        sections.append({
            "section": sid,
            "original_ref": ref,
            "original_text": gk[spec["slug"]][sid],
            "text": en[spec["slug"]][sid],
            "scan_pages": [f"{KEY}/{paths[p].name}" for p in pages],
            "scan_note": " ".join(gal_note(p, note if i == 0 else "") for i, p in enumerate(pages)).replace("  ", " ")
                         + " " + SYNC_NOTE,
        })
    return sections, [f"{KEY}/{paths[p].name}" for p in spec["pages"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    gk, en = greek_sections(), english_sections()
    rows, authors = [], [{
        "id": "berossus", "name": "Berossus", "name_latin": "Berosus", "dates": "fl. c. 290-270 BCE", "century": -3,
        "era": "Hellenistic", "tradition": "mesopotamian", "language": "Greek",
        "bio": "Priest of Bel at Babylon who wrote a history of Babylonia in Greek (the Babyloniaka) for Antiochus I; it survives only in quotations by later writers.",
    }]

    common_intro_sync = (
        "<p>Berossus was a priest of Bel at Babylon who, around 290-278 BCE, wrote a history of his country in Greek for the Seleucid king Antiochus I. "
        "His three books ran from the creation of the world through the ten kings who reigned before the flood to the Neo-Babylonian kings. "
        "The work is lost. Its fullest remains reached the Byzantine chronicler George Syncellus (c. 800 AD) through a chain of excerpts: "
        "Alexander Polyhistor (1st c. BCE) summarized Berossus, Eusebius of Caesarea quoted Polyhistor, and Syncellus copied Eusebius into his <em>Ecloga chronographica</em>.</p>\n\n"
        "<p>The manuscript shown is Paris, Bibliothèque nationale de France, grec 1711, an 11th-century copy of Syncellus' chronicle, the oldest and principal witness to the text. "
        "The images are the library's black-and-white microfilm, published on Gallica. "
        "Each section points at the page that carries it; the line numbers in the notes were counted on the images.</p>"
    )
    sync_notes = [
        "Greek: C. Müller, Fragmenta Historicorum Graecorum (1848-1851), text taken from the Digital Fragmenta Historicorum Graecorum and proofread against Müller's printed pages. Müller's notes on variant readings, printed in parentheses inside the text, are left out; his square brackets mark words he took to be additions by the excerptors.",
        "English: I. P. Cory, Ancient Fragments (2nd ed., 1832). Cory sometimes follows readings of the Armenian translation of Eusebius or older editors rather than the Greek printed here, so a few phrases differ from the Greek. His footnotes and source references are omitted. The capitalized heading at the start of the English is Cory's own heading; Syncellus' Greek heading is not translated by Cory.",
        "The manuscript's wording differs from Müller's edited text in small details. The Greek is the edition, not a transcription of the page.",
    ]
    extra = {
        "oannes": ["In §2 Müller prints ἄφορα ('barren'); Cory translates the older reading εὔφορα ('fertile'). In §4 Müller brackets 'κατὰ δὲ ἰσόψηφον σελήνη' as an addition by Syncellus; the manuscript has it in the running text."],
        "flood": ["The first section joins Syncellus' summary of book 2 (Müller fr. 4) to the start of the quotation (fr. 7), which follow each other without a break in the manuscript.",
                  "Berossus names the ninth king Ardates here; Apollodorus' list calls him Otiartes."],
        "apollodorus": ["Cory's English does not translate Syncellus' introductory clause 'Πρὸς τούτοις καὶ Ἀπολλόδωρος ὁμοίως τούτοις τερατευόμενος οὕτω λέγει'. The words in square brackets are Syncellus' (or Eusebius') comments inside the quotation; Cory prints them in parentheses."],
        "abydenus": ["Abydenus (2nd c. AD?) wrote in the Ionic dialect of Herodotus and drew on Berossus through Polyhistor; his king list differs in several names and reign lengths from Apollodorus' version."],
    }
    intros = {
        "oannes": "<p>This entry is Polyhistor's summary of Berossus' first book: who Berossus was, the land of Babylonia, the creature Oannes, half fish and half man, who came out of the Red Sea and taught mankind letters, crafts, the founding of cities and temples, laws, geometry and agriculture, and the account of creation in which Bel cuts the woman Omoroka in two to make heaven and earth.</p>",
        "flood": "<p>This entry continues the same extract into Berossus' second book: the ten kings before the flood, who reigned 120 sars (one sar = 3,600 years, 432,000 years in all), and the flood under the tenth king Xisouthros. Kronos warns him in a dream, he buries the writings in the city of the sun at Sippar, builds a ship five stadia long, sends out birds three times, lands in Armenia and is taken to live with the gods. The story corresponds to the Babylonian flood stories of Atrahasis and Utnapishtim.</p>",
        "apollodorus": "<p>Syncellus also quotes Apollodorus of Athens (2nd c. BCE), who gave Berossus' list of the ten kings before the flood with the length of each reign in sars, and the creatures, part fish and part man, who came up from the Red Sea under some of them: Oannes, the four Annedotoi and Odakon. The list corresponds to the antediluvian section of the cuneiform Sumerian King List.</p>",
        "abydenus": "<p>The third version in Syncellus is that of Abydenus, who retold Berossus' account of the ten kings and the flood in Ionic Greek. His Sisithros is Berossus' Xisouthros.</p>",
    }
    gaps = ("<p>Not included: the summaries of Berossus that survive only in the Armenian translation of Eusebius' Chronicle (no Greek), Syncellus' "
            "own remarks on Berossus' chronology (no public-domain English translation), and the short testimonia in other authors.</p>")

    for spec in ENTRIES:
        sections, local = build_sync_entry(spec, gk, en, args.force)
        tid = PREFIX + spec["slug"]
        entry = {
            "id": tid, "slug": tid, "title": spec["title"],
            "language": "Greek (Müller, FHG) / English (Cory 1832)",
            "source": "Paris gr. 1711 (George Syncellus, 11th c.) via Gallica + Greek of C. Müller, FHG (DFHG, proofread) + English of I. P. Cory, Ancient Fragments (1832)",
            "description": spec["description"],
            "introduction": common_intro_sync + "\n\n" + intros[spec["slug"]] + "\n\n" + gaps,
            "translator_notes": sync_notes + extra[spec["slug"]],
            "translation": sections,
            "verification": {
                "scan_source": f"Bibliothèque nationale de France, Gallica: Grec 1711, {GALLICA_URL} (IIIF openapi.bnf.fr), pages " + ", ".join(str(p) for p in spec["pages"]),
                "scan_license": "Gallica terms: free non-commercial reuse with the credit 'Source gallica.bnf.fr / BnF'",
                "scan_manuscript": "Paris, BnF, grec 1711 (11th c.), George Syncellus, Ecloga chronographica (pp. 1-230), microfilm images",
                "scan_mapping": "Checked on the images: first and last lines of each page read and found in the Greek; section openings located by line count and opening words (see each scan_note)",
                "scan_mapping_urls": [gallica_view(p) for p in spec["pages"]],
                "scan_local_paths": local,
                "original_text_source": f"C. Müller, Fragmenta Historicorum Graecorum II pp. 496-502 and IV p. 280, via DFHG ({DFHG_API}), proofread against {MUELLER_II} and {MUELLER_IV}",
                "original_text_license": "edition public domain (1848-1851); DFHG data CC BY-NC-SA 4.0",
                "translation_source": f"I. P. Cory, Ancient Fragments, 2nd ed. (London: Pickering, 1832); transcription {CORY_ST} checked against the 1832 printing {CORY_SCAN}",
                "translation_license": "public domain (published 1832)",
                "translator": "I. P. Cory (1832)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(row(tid, spec, entry, [(f"{KEY}/{gallica_page(p, False).name}", f"Paris gr. 1711, p. {p}") for p in spec["pages"]]))
        print(f"  {tid}: {len(sections)} sections")

    # ---- Josephus, Against Apion 1.128-153
    grc, eng = josephus_sections()
    lp = {f: laur_page(f, args.force) for f in ("10r", "10v", "11r", "11v")}
    sections = []
    for n in sorted(grc, key=int):
        pages = JOS_PAGES[n]
        note = " ".join(JOS_PAGE_NOTE[p] for p in pages)
        if len(pages) == 2:
            note = f"1.{n} runs across the page break. " + note
        sections.append({
            "section": f"1.{n}",
            "original_ref": f"Josephus, Against Apion 1.{n}; Laur. Plut. 69.22 fol. {' and '.join(pages)}",
            "original_text": f"<sup>{n}</sup>{grc[n]}",
            "text": f"<sup>{n}</sup>{eng[n]}",
            "scan_pages": [f"{KEY}/{lp[p].name}" for p in pages],
            "scan_note": note + " Checked on the image. Viewer: " + LAUR_RECORD + " . The Greek shown is Niese's critical text.",
        })
    tid = PREFIX + "josephus-apion"
    spec = {"slug": "josephus-apion", "order": 5,
            "title": "Berossus in Josephus, Against Apion 1.128-153: Nabopolassar, Nebuchadnezzar and the last kings of Babylon",
            "description": "Josephus quotes Berossus' third book on Nebuchadnezzar's campaign, his building of Babylon and the hanging garden, and the kings after him down to Nabonidus and the capture of Babylon by Cyrus, shown on the four pages of the 10th-century Florence manuscript Laur. Plut. 69.22 that carry it."}
    entry = {
        "id": tid, "slug": tid, "title": spec["title"],
        "language": "Greek (Niese 1889) / English (Whiston 1737)",
        "source": "Florence, Laur. Plut. 69.22 (10th c.) via BML Teca Digitale IIIF + Niese Greek (Perseus) + Whiston English (Project Gutenberg)",
        "description": spec["description"],
        "introduction": (
            "<p>In his reply to Apion (c. 95 AD) Josephus set out to prove the antiquity of the Jews from non-Greek historians. After the Egyptian Manetho and the Phoenician archives he turned to Berossus, "
            "summarized what Berossus said about the flood, the ark that landed in the mountains of Armenia and the generations after Noah, and then quoted his third book word for word: "
            "Nabopolassar sends his son Nebuchadnezzar against a rebel governor in Egypt and Syria; Nebuchadnezzar hurries back across the desert on his father's death, rebuilds and walls Babylon, "
            "builds a new palace in fifteen days and a hanging garden for his Median queen; after him come Evil-Merodach, Neriglissar, Labashi-Marduk and Nabonidus, until Cyrus takes Babylon.</p>\n\n"
            "<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 69.22, a 10th-century copy of the first book of <em>Against Apion</em>, the oldest Greek witness to the passage. "
            "The excerpt runs from fol. 10r to fol. 11v. Each section is one of Niese's numbered sections and points at the page(s) that carry it; the page breaks were read on the images.</p>"
        ),
        "translator_notes": [
            "Greek: B. Niese, Flavii Iosephi opera vol. 5 (1889), from Perseus. Square brackets are Niese's marks for words he took to be later additions.",
            "English: William Whiston's translation (1737), from Project Gutenberg. Three faults in that transcription were corrected against the 1860 printing: 'oilier' for 'other' (1.128), a stray fragment of a footnote inside 1.142, and 'mouths' for 'months' (1.148). Whiston's footnote marker in 1.142 is omitted.",
            "Whiston's paragraphs were divided at the points that correspond to the openings of Niese's sections; where one English sentence spans two Greek sections it is split at a clause boundary.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF cdm21059.contentdm.oclc.org), Plut. 69.22 fols. 10r, 10v, 11r, 11v; record {LAUR_RECORD}",
            "scan_license": "Teca Digitale access 'Pubblico'; reproduced for non-commercial study with credit 'Biblioteca Medicea Laurenziana, Plut. 69.22, su concessione del MiC'",
            "scan_manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 69.22 (10th c., 37 fols.), Josephus, Contra Apionem",
            "scan_mapping": "Checked on the images: the first and last words of fols. 10r, 10v, 11r and 11v were read and found in Niese's text; each section's folio follows from those page breaks (see scan_note)",
            "scan_mapping_urls": [LAUR_RECORD] + [LAUR_IIIF[f] + "/full/full/0/default.jpg" for f in ("10r", "10v", "11r", "11v")],
            "scan_local_paths": [f"{KEY}/{lp[f].name}" for f in ("10r", "10v", "11r", "11v")],
            "original_text_source": f"B. Niese, Flavii Iosephi opera V (Berlin: Weidmann, 1889), Perseus canonical-greekLit tlg0526.tlg003.perseus-grc2 ({PERSEUS_GRC})",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": f"William Whiston, The Works of Flavius Josephus (1737), Against Apion, Project Gutenberg eBook #2849 ({WHISTON_PG}), corrected against {WHISTON_1860}",
            "translation_license": "public domain",
            "translator": "William Whiston (1737)",
            "verified_date": TODAY,
        },
    }
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    rows.append(row(tid, spec, entry, [(f"{KEY}/{lp[f].name}", f"Laur. Plut. 69.22, fol. {f}") for f in ("10r", "10v", "11r", "11v")],
                    date_approx="c. 290-278 BCE (Berossus); c. 95 AD (Josephus); 10th c. (manuscript)", tradition="mesopotamian"))
    print(f"  {tid}: {len(sections)} sections")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Berossus, History of Babylonia",
            "group": "Mesopotamia", "date_sort": -290,
            "author_name": "Berossus of Babylon (c. 290 BCE), in George Syncellus and Josephus",
            "source_url": GALLICA_URL,
            "critical_edition": "C. Müller, FHG II and IV (via DFHG, proofread); B. Niese 1889 (Perseus)",
            "translator_name": "I. P. Cory (1832); William Whiston (1737)",
            "original_lang_label": "Greek · Müller / Niese",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "berossus berosus babyloniaca oannes annedotus xisouthros xisuthrus flood deluge antediluvian kings sar chaldean babylon syncellus nebuchadnezzar",
            "description": "The Babylonian priest Berossus' Greek history of his land (c. 290 BCE): Oannes the fish-man who taught civilization, the creation, the ten kings before the flood and the flood of Xisouthros, and the last kings of Babylon, on the pages of a Paris manuscript of George Syncellus and a Florence manuscript of Josephus.",
        },
        "texts": rows,
        "authors": authors,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


def row(tid, spec, entry, pages, date_approx="c. 290-278 BCE (Berossus); 11th c. (Paris gr. 1711)", tradition="mesopotamian"):
    return {
        "id": tid, "slug": tid, "order": spec["order"], "title": entry["title"], "author_id": "berossus",
        "language": "Greek", "era": "Hellenistic", "tradition": tradition, "category": "history",
        "date_approx": date_approx, "century": -3, "source": entry["source"], "description": entry["description"],
        "themes": ["berossus", "babylon", "chaldeans", "antediluvian", "flood", "oannes", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f, "caption": c} for f, c in pages]},
    }


if __name__ == "__main__":
    main()
