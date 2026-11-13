#!/usr/bin/env python3
"""
import_hesiod-theogony.py: Hesiod, Theogony, on Florence, Biblioteca Medicea Laurenziana,
Plut. 32.16 (late 13th century), fols. 240r-247v.

Chain of evidence
  1. SCAN     BML Teca Digitale (CONTENTdm IIIF), manifest
              https://cdm21059.contentdm.oclc.org/iiif/plutei:596036/manifest.json
              (record: "VI. Eiusdem [Hesiodi] Theogonia", rights CC BY-NC-SA).
              Plut. 32.16 is the oldest complete manuscript of the Theogony with published
              images. Older witnesses are fragmentary (papyri; Paris suppl. gr. 663, 11th c.,
              lines 72-145 and 450-504 only).
  2. MAPPING  Each page's first and last verse were read on the page image (zoomed crops
              of the top and bottom rows) and matched against the Greek; consecutive pages
              were checked for continuity. Verses run two to a row across the page (one in
              the left column, the next in the right); fol. 244v has three verses to a row.
              Results are in PAGES below; every section's scan_note repeats them.
  3. GREEK    H. G. Evelyn-White (Loeb, 1914), Perseus canonical-greekLit
              tlg0020.tlg001.perseus-grc2 (CC BY-SA 4.0). Lines the editor brackets as
              spurious (<del>) are shown in square brackets. Lines 929a-929t (quoted by Galen,
              not in any medieval manuscript) are left out.
  4. ENGLISH  H. G. Evelyn-White (1914, public domain), Perseus tlg0020.tlg001.perseus-eng2.
              Perseus divides the prose into blocks of about five lines; at each page break the
              English is cut at the end of Evelyn-White's sentence (ENGLISH_CUTS, chosen by reading
              the English against the Greek; scripts/qc4_hesiod_english.py), so a sentence that runs
              across a page break goes whole to one page and the scan_note gives the exact range.
              Spaces lost where Perseus footnotes were removed are restored (QC fix 2026-11-12).

Usage:  python3 scripts/import_hesiod-theogony.py [--force]   (--force re-downloads scans)
"""
import argparse
import io
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from qc4_hesiod_english import cut_english, english_note  # noqa: E402

KEY = "hesiod-theogony"
TOTAL = 1022
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "hesiod"
PUB = ROOT / "translations" / "published"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"

GREEK_XML = SRC / "tlg0020.tlg001.perseus-grc2.xml"
ENGLISH_XML = SRC / "tlg0020.tlg001.perseus-eng2.xml"
GITHUB = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0020/tlg001/"
MANIFEST = "https://cdm21059.contentdm.oclc.org/iiif/plutei:596036/manifest.json"
RECORD = "https://cdm21059.contentdm.oclc.org/digital/collection/plutei/id/596036"
MS = "Laur. Plut. 32.16"
MS_LONG = ("Florence, Biblioteca Medicea Laurenziana, Plut. 32.16 (paper, late 13th century; a large "
           "collection of Greek poetry that also holds letters of Maximus Planudes), Theogony on fols. 240r-247v")

# folio -> IIIF image service (from the manifest)
IIIF = {
    "240r": 595697, "240v": 595698, "241r": 595699, "241v": 595700, "242r": 595701, "242v": 595702,
    "243r": 595703, "243v": 595704, "244r": 595705, "244v": 595706, "245r": 595707, "245v": 595708,
    "246r": 595709, "246v": 595710, "247r": 595711, "247v": 595712,
}

# Verified on the images (see docstring).  first/last = edition line numbers on the page.
# Every page edge was re-read on the photograph on 2026-11-12 (QC fix: 246v ends at 933 and 247r
# begins at 934, not 939/940); read_first / read_last record the first and last row as read
# (left | right column; Greek as written, accents simplified).
PAGES = [
    {"folio": "240r", "first": 1, "last": 42,
     "read_first": "1 | 2: Μουσάων ἑλικωνιάδων ἀρχώμεθ' ... | αἵθ' ἑλικῶνος ἔχουσιν ...",
     "read_last": "41 | 42: ... θεᾶν ὀπὶ λειριοέσσῃ | ... κάρη νιφόεντος ὀλύμπου",
     "note": "The Theogony begins in the lower half of the page under the faded red title ἡσιόδου θεογονία, with a faded red initial; 21 rows of two verses."},
    {"folio": "240v", "first": 43, "last": 100,
     "read_first": "43 | 44: δώματ' ἀθανάτων αἳ δ' ... | θεῶν γένος αἰδοῖον ...",
     "read_last": "99 | 100: ... ἀκαχήμενος αὐτὰρ ἀοιδὸς | μουσάων θεράπων κλέα προτέρων ...", "note": ""},
    {"folio": "241r", "first": 101, "last": 160,
     "read_first": "101 | 102: ὑμνήσῃ μάκαράς τε θεοὺς ... | αἶψ' ὅ γε δυσφροσυνέων ...",
     "read_last": "159 | 160: ... στοναχίζετο γαῖα πελώρη | ... κακήν τ' ἐφράσσατο τέχνην", "note": ""},
    {"folio": "241v", "first": 161, "last": 222,
     "read_first": "161 | 162: αἶψα δὲ ποιήσασα γένος ... | τεῦξε μέγα δρέπανον ...",
     "read_last": "221 | 222: ... θεαὶ δεινοῖο χόλοιο | ... κακὴν ὄπιν ὅς τις ἁμάρτῃ", "note": ""},
    {"folio": "242r", "first": 223, "last": 278,
     "read_first": "223 | 224: τίκτε δὲ καὶ νέμεσιν ... | νὺξ ὀλοή μετὰ τὴν δ' ...",
     "read_last": "277 | 278: ... ἀθάνατοι καὶ ἀγήρῳ | ... παρελέξατο κυανοχαίτης", "note": ""},
    {"folio": "242v", "first": 279, "last": 340,
     "read_first": "279 | 280: ἐν μαλακῷ λειμῶνι ... | τῆς δ' ὅτε δὴ περσεὺς ...",
     "read_last": "339 | 340: στρυμόνα μαίανδρόν τε ... | ... ἀχελώϊόν τ' ἀργυροδίνην",
     "note": "A one-line note in the top margin is not part of the poem."},
    {"folio": "243r", "first": 341, "last": 409,
     "read_first": "341 (left) νέσσον τε ῥόδιόν θ' ἁλιάκμονα ...; 342 (right, half a row higher) γρήνικόν τε καὶ αἴσηπον ...",
     "read_last": "408 | 409: ... ἀγανώτατον ἐντὸς ὀλύμπου | γείνατο δ' ἀστερίην ... ἥν ποτε πέρσης",
     "note": "The right column starts half a row higher than the left, so the top rows read by height 341 (left), 342 and 343 (right), 344 (left), 345 (right) and so on; the right column has 35 rows and the left 34, and by the foot the rows pair normally (402 | 403 ... 408 | 409)."},
    {"folio": "243v", "first": 410, "last": 475,
     "read_first": "410 | 411: ἠγάγετ' ἐς μέγα δῶμα ... | ἡ δ' ὑποκυσαμένη ἑκάτην ...",
     "read_last": "474 | 475: οἳ δὲ θυγατρὶ φίλῃ ... | ... ὅσα περ πέπρωτο γενέσθαι", "note": ""},
    {"folio": "244r", "first": 476, "last": 547,
     "read_first": "476 | 477: ἀμφὶ κρόνῳ βασιλῆι ... | πέμψαν δ' ἐς λύκτον ...",
     "read_last": "546 | 547: τὸν δ' αὖτε προσέειπε προμηθεὺς ... | ... δολίης δ' οὐ λήθετο τέχνης",
     "note": "The last three rows (542-547) are written smaller, squeezed in at the foot of the page."},
    {"folio": "244v", "first": 548, "last": 668,
     "read_first": "548 | 549 | 550: ζεῦ κύδιστε μέγιστε ... | τῶν δ' ἕλε' ὁπποτέρην ... | φῆ ῥα δολοφρονέων ...",
     "read_last": "666-668 across the full width: μᾶλλον ἔτ' ἢ τὸ πάροιθε ... καὶ ὅσοι κρόνου ἐξεγένοντο",
     "note": "Dense page written in three columns, three verses to a row (548 left, 549 middle, 550 right, and so on); the last five rows run across the full width (653-655, 656-658, 659-661, 662 with 664-665, 666-668). Verse 663 (μαρνάμενοι τιτῆσιν ἀνὰ καρτερὰς ὑσμίνας) is left out of its row and written in the lower margin under a reference mark that also follows 662; the Greek shows it in its place. A short note in the top margin is not part of the text."},
    {"folio": "245r", "first": 669, "last": 736,
     "read_first": "669 | 670: οὕς τε ζεὺς ἐρέβευσφιν ... | δεινοί τε κρατεροί τε ...",
     "read_last": "735 | 736: ναίουσιν φύλακες πιστοὶ ... | ἔνθα δὲ γῆς δνοφερῆς ...",
     "note": "In the falling-anvil passage the scribe's eye slipped from ἄκμων (722) to ἄκμων (724): the column reads 721 | 722, with a mark after 722, then 725 | 726. Under the same mark in the lower margin stand 723 (οὐρανόθεν κατιὼν ...), then a verse that is not in Evelyn-White's text (read as ἶσον δ' αὖτ' ἀπὸ [γῆς] ἐς τάρταρον ἠερόεντα, the middle abbreviated, so not certain; a verse of this kind is found in part of the manuscript tradition), then 724 written over two lines. The Greek shows 723-724 in their places and does not include the extra verse."},
    {"folio": "245v", "first": 737, "last": 803,
     "read_first": "737 | 738: πόντου τ' ἀτρυγέτοιο ... | ἑξείης πάντων πηγαὶ ...",
     "read_last": "802 | 803: οὐδέ ποτ' ἐς βουλὴν ... | ἐννέα πάντα ἔτεα ... αὖτις",
     "note": "A short note in the lower margin is not part of the poem."},
    {"folio": "246r", "first": 804, "last": 867,
     "read_first": "804 | 805: εἴρας ἐς ἀθανάτων ... | τοῖον ἄρ' ὅρκον ἔθεντο ...",
     "read_last": "866 | 867: τήκεται ἐν χθονὶ δίῃ ... | ὣς ἄρα τήκετο γαῖα ...", "note": ""},
    {"folio": "246v", "first": 868, "last": 933,
     "read_first": "868 | 869: ῥῖψε δέ μιν θυμῷ ... | ἐκ δὲ τυφωέος ...",
     "read_last": "932 | 933: πυθμέν' ἔχων παρὰ μητρὶ ... | ναίει χρύσεα δῶ ... αὐτὰρ ἄρηϊ",
     "note": "Lines 929a-929t of the Loeb edition (a passage quoted by Galen) are not in this or any medieval manuscript and are left out here: the row 928 | 929 is followed directly by 930 | 931."},
    {"folio": "247r", "first": 934, "last": 991,
     "read_first": "934 | 935: ῥινοτόρῳ κυθέρεια φόβον ... | δεινούς οἵ τ' ἀνδρῶν πυκινὰς ...",
     "read_last": "990 | 991: ὦρτ' ἀναρεψαμένη ... | ... ποιήσατο δαίμονα δῖον",
     "note": "Rows 1-3 hold 934-939; 940 (Καδμείη δ' ἄρα οἱ) opens row 4. (Corrected 2026-11-12: the page map had put 934-939 on fol. 246v.)"},
    {"folio": "247v", "first": 992, "last": 1022, "ms_last": 1020,
     "read_first": "992 | 993: κούρην δ' αἰήταο ... | αἰσονίδης βουλῇσι ...",
     "read_last": "1019 | 1020: αὗται μὲν θνητοῖσι ... | ἀθάναται γείναντο θεοῖς ἐπιείκελα τέκνα",
     "note": "Line 1014 (Telegonus) is not on the page: the row 1012 | 1013 is followed by 1015 | 1016. The poem ends at 1020 with the red subscription τέλος τῆς θεογονίας ἡσιόδου; lines 1021-1022, the transition to the Catalogue of Women, are not in this manuscript and are printed from the edition."},
]

# Evelyn-White's English is cut at the end of his sentences at each page break (QC fix 2026-11-12;
# scripts/qc4_hesiod_english.py). folio: (opening words of the sentence that begins the page's English,
# occurrence, first line it renders, last line of the previous page's English). Where his sentence runs
# across the break it goes whole to the side nearer its end, or, where both are equally near or one
# part of the poem would otherwise have no English on that page, as noted.
ENGLISH_CUTS = {
    "240v": ("And they, uttering their immortal voice", 0, 43, 43),        # sentence break inside 43
    "241r": ("For although a man has sorrow", 0, 98, 97),                  # 98-103: 3 lines each side; given to 241r so that its 101-103 have English
    "241v": ("Forthwith she made the element of grey flint", 0, 161, 160),
    "242r": ("Also deadly Night bore Nemesis", 0, 223, 222),
    "242v": ("With her lay the Dark-haired One", 0, 278, 278),            # sentence break inside 278
    "243r": ("Also she brought forth a holy company", 0, 346, 345),      # rivers 337-345 kept with 242v, which holds 337-340 of this part
    "243v": ("And she conceived and bore Hecate", 0, 411, 410),           # 409-410 tie: kept with the page where it begins
    "244r": ("So they sent her to Lyctus", 0, 477, 476),
    "244v": ("“Zeus, most glorious and greatest", 0, 548, 547),
    "245r": ("A hundred arms sprang from the shoulders", 0, 671, 670),
    "245v": ("And there, all in their order, are the sources and ends of gloomy", 0, 736, 735),
    "246r": ("But in the tenth year he comes again", 0, 803, 803),        # sentence break inside 803
    "246v": ("And in the bitterness of his anger", 0, 868, 867),
    "247r": ("Also Cytherea bore to Ares", 0, 933, 933),                 # sentence break inside 933
    "247v": ("And the son of Aeson by the will of the gods", 0, 992, 991),
}
ENGLISH_SPLITS = []
FIRST_LAST_WORDS = {}  # filled from the Greek at build time

# Episodes (boundaries fall on Evelyn-White's paragraph blocks)
ENTRIES = [
    (1, 103, "proem-muses", "Proem: the Muses of Helicon",
     "Hesiod meets the Muses on Mount Helicon, receives the poet's staff and sings of their birth from Zeus and Mnemosyne."),
    (104, 206, "chaos-earth-heaven", "Chaos, Earth and Heaven; the Titans; Cronos and the castration of Heaven",
     "The invocation, the first beings (Chaos, Earth, Tartarus, Eros), the children of Earth and Heaven, Cronos' sickle and the birth of Aphrodite."),
    (207, 336, "children-of-night-and-sea", "The children of Night and of the Sea; Nereus and the Nereids; the monsters",
     "The children of Night, the offspring of Pontus, the fifty Nereids, and the monstrous line of Phorcys and Ceto."),
    (337, 452, "children-of-the-titans-hecate", "The children of the Titans; the hymn to Hecate",
     "The rivers and Oceanids, the children of Hyperion, Crius, Coeus and Phoebe, Styx's honour, and the praise of Hecate."),
    (453, 506, "birth-of-zeus", "Cronos swallows his children; the birth of Zeus",
     "Rhea's children are swallowed by Cronos until she hides the infant Zeus in Crete; Cronos disgorges them; the Cyclopes give Zeus the thunderbolt."),
    (507, 616, "prometheus-pandora", "Prometheus and Pandora",
     "The sons of Iapetus; the trick at Mecone, the theft of fire, and the making of the first woman."),
    (617, 728, "titanomachy", "The war of the gods and Titans (Titanomachy)",
     "Zeus frees the Hundred-Handers, the ten-year war with the Titans, and the Titans cast down into Tartarus."),
    (729, 819, "tartarus", "Tartarus, Night, Sleep, Death and the Styx",
     "The geography of the underworld: the prison of the Titans, the houses of Night and Day, Hades' hound and the oath of the Styx."),
    (820, 885, "typhoeus", "Typhoeus; Zeus becomes king",
     "Earth bears Typhoeus, whom Zeus defeats; the gods ask Zeus to reign."),
    (886, 962, "wives-and-children-of-zeus", "The wives and children of Zeus",
     "Zeus swallows Metis, then marries Themis, Eurynome, Demeter, Mnemosyne, Leto and Hera; the birth of Athena and the other Olympians."),
    (963, 1022, "goddesses-and-mortals", "Goddesses who lay with mortal men",
     "The children born to goddesses by mortal men, from Demeter and Iasion to Calypso and Odysseus."),
]


def fetch(url, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) > 20000:
                return data
        except Exception:
            pass
        time.sleep(3 + 4 * i)
    raise RuntimeError(f"download failed: {url}")


def scan_name(folio):
    return f"laur-32-16-f{folio}.jpg"


def get_scan(folio, force=False):
    path = SCAN_DIR / scan_name(folio)
    if path.exists() and not force:
        return path
    img = Image.open(io.BytesIO(fetch(f"https://cdm21059.contentdm.oclc.org/iiif/2/plutei:{IIIF[folio]}/full/1800,/0/default.jpg"))).convert("RGB")
    img.save(path, quality=85)
    return path


def lnum(n):
    m = re.match(r"\d+", n or "")
    return int(m.group()) if m else None


def greek_lines():
    """[(n, html)] in edition order; <del> rendered as [..]."""
    body = ET.parse(GREEK_XML).getroot().find(f".//{TEI}body")
    out = []
    for l in body.iter(f"{TEI}l"):
        def walk(e):
            s = e.text or ""
            for c in e:
                inner = walk(c)
                tag = c.tag.replace(TEI, "")
                if tag == "del":
                    s += "[" + inner.strip() + "]"
                elif tag in ("note", "milestone"):
                    pass
                else:
                    s += inner
                s += c.tail or ""
            return s
        txt = re.sub(r"\s+", " ", walk(l)).strip()
        out.append((l.get("n"), txt))
    return out


def english_blocks():
    """[(n, text)] Evelyn-White blocks in document order, notes removed. A block is split where a
    Perseus card milestone (a paragraph start) falls inside it, so the card's line starts a block;
    a card milestone standing just before a block (within 4 lines) relabels that block."""
    body = ET.parse(ENGLISH_XML).getroot().find(f".//{TEI}body")
    out = []
    pending = [None]

    def do_l(l):
        start = l.get("n")
        if pending[0] and start.isdigit() and pending[0].isdigit() and 0 < int(pending[0]) - int(start) <= 4:
            start = pending[0]
        pending[0] = None
        parts = [[start, ""]]

        def walk(e):
            parts[-1][1] += e.text or ""
            for c in e:
                tag = c.tag.replace(TEI, "")
                if tag == "milestone" and c.get("unit") == "card":
                    if parts[-1][1].strip():
                        parts.append([c.get("n"), ""])
                elif tag != "note":
                    walk(c)
                tail = c.tail or ""
                # a footnote anchored between two words leaves no space in the Perseus XML
                # ("quick-glancing<note>..</note>Aphrodite"); the printed text has one
                if tag == "note" and tail[:1].strip() and parts[-1][1][-1:].strip() and tail[0] not in ",.;:!?)]’”—":
                    tail = " " + tail
                parts[-1][1] += tail
        walk(l)
        if len(parts) > 1 and not parts[-1][1].strip():
            pending[0] = parts[-1][0]          # card milestone at the very end of the block
        out.extend((n, re.sub(r"\s+", " ", t).strip()) for n, t in parts if t.strip())

    def visit(e):
        for c in e:
            tag = c.tag.replace(TEI, "")
            if tag == "l":
                do_l(c)
            elif tag == "milestone" and c.get("unit") == "card":
                pending[0] = c.get("n")
            else:
                visit(c)
    visit(body)
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(force=False):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    grc = greek_lines()
    grc = [(n, t) for n, t in grc if re.fullmatch(r"\d+", n)]          # drop 929a-929t
    gtext = {int(n): t for n, t in grc}
    assert len(gtext) == 1022 and min(gtext) == 1 and max(gtext) == 1022, len(gtext)
    eng = [(n, t) for n, t in english_blocks() if re.fullmatch(r"\d+", n)]
    starts = [int(n) for n, _ in eng]

    page_of = {}
    for p in PAGES:
        for k in range(p["first"], p["last"] + 1):
            assert k not in page_of, k
            page_of[k] = p["folio"]
    assert sorted(page_of) == list(range(1, 1023))

    paths = {p["folio"]: get_scan(p["folio"], force) for p in PAGES}
    for f, pth in paths.items():
        print(f"  {f}: {pth.stat().st_size} bytes")

    # English: cut at Evelyn-White's sentence ends at every page break (ENGLISH_CUTS, qc4_hesiod_english)
    def entry_of(k):
        for i, (a, b, *_rest) in enumerate(ENTRIES):
            if a <= k <= b:
                return i
    pieces = cut_english([(int(n), t) for n, t in eng], PAGES, ENGLISH_CUTS, ENGLISH_SPLITS, TOTAL)
    for pc in pieces:
        pc["entry"] = entry_of(pc["start"])
        assert entry_of(pc["end"]) == pc["entry"], f"English piece {pc['start']}-{pc['end']} crosses an entry boundary"

    rows, pubs = [], []
    for ei, (a, b, slug, title, blurb) in enumerate(ENTRIES):
        tid = f"verified-{KEY}-{slug}"
        sections = []
        for p in PAGES:
            lo, hi = max(a, p["first"]), min(b, p["last"])
            if lo > hi:
                continue
            f = p["folio"]
            g = "<br>".join(f"<sup>{k}</sup>{esc(gtext[k])}" for k in range(lo, hi + 1))
            eb = [pc for pc in pieces if pc["entry"] == ei and pc["folio"] == f]
            e = "<p>" + " ".join(f"<sup>{pc['mark']}</sup>{esc(pc['text'])}" for pc in eb) + "</p>" if eb else ""
            if not eb:
                e = "<p><em>The English for these lines is given with the neighbouring section (Evelyn-White's sentence runs across the page break).</em></p>"
            ms_last = p.get("ms_last", p["last"])
            first_w = " ".join(gtext[p["first"]].split()[:4])
            last_w = " ".join(gtext[ms_last].split()[-4:])
            part = "" if (lo, hi) == (p["first"], p["last"]) else f" This section shows lines {lo}-{hi} of that page; the rest of the page belongs to the {'previous' if lo > p['first'] else 'next'} part of the poem."
            if (lo, hi) != (p["first"], p["last"]) and lo > p["first"] and hi < p["last"]:
                part = f" This section shows lines {lo}-{hi} of that page."
            eng_range = (" " + english_note(eb, PAGES, ENGLISH_CUTS, f)) if eb else ""
            note = (f"{MS}, fol. {f}: lines {p['first']}-{ms_last}, begins ‹{first_w}›, ends ‹{last_w}›. "
                    "Checked on the image: first and last rows read and matched to the Greek (re-read on the image 2026-11-12: first row ‹" + p["read_first"] + "›, last row ‹" + p["read_last"] + "›)"
                    + (f"; the page before ends at line {p['first'] - 1}" if p['first'] > 1 else "; this is the first page of the poem")
                    + (f" and the page after begins at line {ms_last + 1}." if ms_last < 1020 else " and this is its last page.") + part
                    + (" " + p["note"] if p["note"] else "") + eng_range)
            sections.append({
                "section": f"fol. {f}",
                "original_ref": f"Theogony {lo}-{hi}; {MS}, fol. {f}",
                "original_text": g,
                "text": e,
                "scan_pages": [f"{KEY}/{scan_name(f)}"],
                "scan_note": note,
            })
        n_lines = b - a + 1
        folios = [s["section"].replace("fol. ", "") for s in sections]
        intro = (
            f"<p>Hesiod's <em>Theogony</em> (c. 700 BCE) is the oldest Greek account of the origin of the world and the gods, "
            f"from Chaos and Earth through the reign of Cronos to the victory of Zeus. This part: <strong>{esc(title)}</strong> "
            f"(lines {a}-{b}, {n_lines} lines). {esc(blurb)}</p>"
            f"<p>The page photographs are from {esc(MS_LONG)}, the oldest complete manuscript of the poem with published images, "
            f"in the Biblioteca Medicea Laurenziana's Teca Digitale. This part is on fol. {', '.join(folios)}. "
            "The scribe writes two verses to a row, one in each column, so a page is read across the columns, row by row. "
            "Each section below is one page; its note gives the page's first and last verse as read on the photograph.</p>"
            "<p>The Greek is Evelyn-White's Loeb text (1914) via Perseus, not a transcription of this manuscript, whose wording differs here and there. "
            "Verses the editor brackets as later additions are shown in square brackets. "
            "The English is Evelyn-White's prose translation (1914); it is cut at the end of his sentences, so where a sentence runs across a page break it is given whole to one page; each section's note gives the exact lines its English covers.</p>"
        )
        pub = {
            "id": tid, "slug": tid,
            "title": f"Hesiod, Theogony {a}-{b}: {title}",
            "language": "Ancient Greek / English",
            "source": f"{MS} (BML Teca Digitale IIIF) + Evelyn-White Greek (Loeb 1914, Perseus) + Evelyn-White English (1914, Perseus)",
            "description": f"Hesiod's Theogony, lines {a}-{b} ({title}), on the pages of the late 13th-century Florence manuscript Laur. Plut. 32.16, with Greek and English.",
            "introduction": intro,
            "translator_notes": [
                "Greek: H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb Classical Library, 1914), via Perseus. Square brackets mark verses the editor regards as interpolated.",
                "English: H. G. Evelyn-White's translation in the same volume; his footnotes are omitted.",
                "Lines 929a-929t of the Loeb text (a passage on the birth of Athena quoted by Galen from Chrysippus) are not in the medieval manuscripts and are not included.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF): {RECORD} ; manifest {MANIFEST}",
                "scan_license": "CC BY-NC-SA, as stated in the Teca Digitale record; images © Biblioteca Medicea Laurenziana, Florence",
                "scan_manuscript": MS_LONG,
                "scan_mapping": "Each page's first and last verse read on the page image and matched to the Greek, with continuity checked between consecutive pages (details in each section's scan_note).",
                "scan_mapping_urls": [RECORD, MANIFEST],
                "scan_local_paths": [s["scan_pages"][0] for s in sections],
                "original_text_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus canonical-greekLit tlg0020.tlg001.perseus-grc2 ({GITHUB}tlg0020.tlg001.perseus-grc2.xml)",
                "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
                "translation_source": f"H. G. Evelyn-White, Hesiod, the Homeric Hymns and Homerica (Loeb, 1914), Perseus tlg0020.tlg001.perseus-eng2 ({GITHUB}tlg0020.tlg001.perseus-eng2.xml)",
                "translation_license": "public domain (published 1914); Perseus digital text CC BY-SA 4.0",
                "translator": "H. G. Evelyn-White (1914)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False), encoding="utf-8")
        pubs.append(pub)
        rows.append({
            "id": tid, "slug": tid, "order": ei + 1,
            "title": pub["title"], "author_id": "hesiod", "language": "Ancient Greek",
            "era": "Classical", "tradition": "greek", "category": "literature",
            "date_approx": "c. 700 BCE (composition); manuscript late 13th c.", "century": -7,
            "source": pub["source"], "description": pub["description"],
            "themes": ["hesiod", "theogony", "greek-myth", "creation", "titans", "greek", "manuscript", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": s["scan_pages"][0], "caption": f"{MS}, {s['section']}"} for s in sections]},
        })
        print(f"wrote {tid}: {len(sections)} sections")

    coll = {
        "collection": {
            "key": KEY, "prefix": f"verified-{KEY}-",
            "label": "Hesiod, Theogony",
            "group": "Greece", "date_sort": -700,
            "author_name": "Hesiod (c. 700 BCE; Florence manuscript, late 13th c.)",
            "source_url": RECORD,
            "critical_edition": "Evelyn-White, Loeb 1914, via Perseus",
            "translator_name": "H. G. Evelyn-White (1914)",
            "original_lang_label": "Ancient Greek · Evelyn-White",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "hesiod theogony titans cronos zeus chaos gaia uranus prometheus pandora typhoeus muses",
            "description": "Hesiod's Theogony, the Greek account of the birth of the gods and the war of the Titans, complete, on the pages of the oldest complete manuscript with published images (Florence, Laur. Plut. 32.16, late 13th century).",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    build(ap.parse_args().force)
