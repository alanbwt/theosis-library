#!/usr/bin/env python3
"""
import_code_of_hammurabi.py -- the Code of Hammurabi on the Louvre stele (Sb 8),
complete as preserved: prologue, laws 1-65 and 100-282, epilogue.

One section per law (and per column for the prologue and epilogue). Every
section carries the CDLI transliteration of exactly the stele lines that hold
it, Harper's 1904 English for the same law, and the photograph(s) of the
stele column(s) on which those lines stand.

Chain of evidence
-----------------
1. ORIGINAL TEXT  CDLI P249253 (Louvre Sb 8), ATF transliteration
                  https://cdli.earth/artifacts/249253 , ATF export
                  https://cdli.earth/inscriptions/2346002/atf
                  The ATF gives the stele layout itself: obverse columns 1-16
                  (+ the erased column 17), reverse columns 1-28, line numbers
                  per column, and an @law marker where each law begins.
                  Terms (cdli.earth/terms-of-use): text "may be freely copied,
                  aggregated and re-used according to common and fair academic
                  practice", with mention of CDLI.
                  Presentation only: ATF letters are written in the usual
                  Unicode form (sz>š, s,>ṣ, t,>ṭ, h>ḫ, sign indices as
                  subscripts, Sumerograms between underscores in capitals).
                  No sign, break or damage mark is added or removed.
2. ENGLISH        Robert Francis Harper, The Code of Hammurabi King of Babylon
                  about 2250 B.C. (Chicago, 1904), public domain.
                  Base text: the Wikisource transcription
                  https://en.wikisource.org/wiki/The_Code_of_Hammurabi_(Harper_translation)
                  checked word by word against the printed book: three archive.org
                  OCR texts (codeofhammurabik00harpuoft, cu31924074445523,
                  codeofhammurabi00harp) plus our own Tesseract OCR of the
                  Toronto scan's page images (data/sources/code-of-hammurabi/
                  harper_pages/). Wherever two or more of these four readings of
                  the printed page agree against the Wikisource text, the printed
                  page image was consulted and the reading of the book restored;
                  every such correction is listed in CORRECTIONS below.
                  Harper's own column markers "(Col. II)" ... "(Col. 44.)" in the
                  prologue and epilogue are kept: they split those parts by column.
                  Harper numbers the reverse columns continuously (rev. xxv =
                  his col. 41).
3. PHOTOGRAPHS    a) Obverse, colour: two Wikimedia Commons photographs,
                     cropped band by band (each "column" of the stele is a
                     horizontal band read right to left; column i lies directly
                     under the relief):
                     - Francesco Bini (Sailko), "Regno di babilonia ... SB 8, 03"
                       (CC BY-SA 4.0), columns i-x;
                     - Rama, "Code of Hammurabi-Sb 8-IMG 7764" (CC BY-SA 3.0 fr),
                       columns xi-xvi.
                     Bands counted by eye on the photographs from the relief
                     downwards (16 bands, then the polished erasure). The count
                     was checked against two fixed points: the horizontal crack
                     that runs at the boundary of columns x and xi (CDLI marks
                     damage in col. x 24-58 and col. xi 12-66), and L. Zhiltsova,
                     "Plan de repérage des paragraphes sur la stèle du Code de
                     Hammu-rabi (SB 8, Louvre)", NABU 2023/3 no. 62, pp. 122-123,
                     whose plan shows the same crack and the same 16 bands.
                  b) Both faces, column by column: the photographic montage of
                     the whole inscription distributed by CDLI with P249253
                     (https://cdli.earth/dl/photo/P249253_d.jpg, credited
                     "image: Richardson, M., A Comprehensive Grammar to
                     Hammurabi's Stele"; CDLI lists it as "Photo (detail)
                     © Louvre Museum"). In the montage each stele column is a
                     vertical strip and is labelled i-xvi (front) and i-xxviii
                     (rear) at the top. Each crop is centred on one label and
                     keeps the label row. The labels were checked against the
                     damage recorded in the CDLI ATF: the front crack between
                     x and xi; the large flake in rear columns xxii-xxiii (CDLI
                     damage rev. 22 29-54, rev. 23 22-46) and the long crack in
                     xx-xxi (rev. 20 59-67, rev. 21 52-96); the flake near the
                     start of rear v-vi (rev. 5 5-10, rev. 6 11-19).
                     CDLI terms: images are for the non-commercial use of
                     students, scholars and the public.
4. MAPPING        Law -> stele column/line: CDLI ATF (@column / @law markers).
                  Column -> photograph: the visual band count and montage
                  labels described above. No mapping is interpolated.

Gaps: laws 66-99 stood on the seven obverse columns erased in antiquity
(only the restored last word of law 65 in CDLI); the opening of law 100 is lost
with them. They are not on the stele and are not published here.

Usage:
    python3 scripts/import_code_of_hammurabi.py
"""

import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
KEY = "code-of-hammurabi"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
PHOTOS = SRC / "photos"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()

CDLI_PAGE = "https://cdli.earth/artifacts/249253"
CDLI_ATF = "https://cdli.earth/inscriptions/2346002/atf"
CDLI_MONTAGE = "https://cdli.earth/dl/photo/P249253_d.jpg"
WS_URL = "https://en.wikisource.org/w/index.php?title=The_Code_of_Hammurabi_(Harper_translation)&action=raw"
WS_PAGE = "https://en.wikisource.org/wiki/The_Code_of_Hammurabi_(Harper_translation)"
HARPER_SCAN = "https://archive.org/details/codeofhammurabik00harpuoft"
LOUVRE = "https://collections.louvre.fr/ark:/53355/cl010174436"
NABU = "https://sepoa.fr/wp/wp-content/uploads/2023/10/NABU-2023-3.pdf"
COMMONS_SAILKO = ("https://commons.wikimedia.org/wiki/File:Regno_di_babiblonia,_I_dinastia,_codice_di_hammurabi,"
                  "_in_basalto,_1792-1750_ac_ca,_da_susa,_SB_8,_03.jpg")
COMMONS_RAMA = "https://commons.wikimedia.org/wiki/File:Code_of_Hammurabi-Sb_8-IMG_7764.JPG"

PHOTO_FILES = {
    "sailko": (PHOTOS / "Regno_di_babiblonia_SB_8_03_Sailko.jpg",
               "https://upload.wikimedia.org/wikipedia/commons/1/18/Regno_di_babiblonia%2C_I_dinastia%2C_codice_di_hammurabi%2C_in_basalto%2C_1792-1750_ac_ca%2C_da_susa%2C_SB_8%2C_03.jpg"),
    "rama": (PHOTOS / "Code_of_Hammurabi-Sb_8-IMG_7764.JPG",
             "https://upload.wikimedia.org/wikipedia/commons/f/f7/Code_of_Hammurabi-Sb_8-IMG_7764.JPG"),
    "montage": (PHOTOS / "cdli_P249253_d.jpg", CDLI_MONTAGE),
}

ROMAN = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv",
         "xv", "xvi", "xvii", "xviii", "xix", "xx", "xxi", "xxii", "xxiii", "xxiv", "xxv", "xxvi",
         "xxvii", "xxviii"]

# ---------------------------------------------------------------------------
# Obverse colour crops: (photo, x0, y0, x1, y1) in original pixels.
# Ruling lines (centre of the face) found by eye on the photographs:
#   Sailko 03: relief base 290; I/II 660; II/III 1045; III/IV 1420; IV/V 1810;
#              V/VI 2180; VI/VII 2540; VII/VIII 2900; VIII/IX 3245; IX/X 3600;
#              X/XI 3950 (crack 3840-3930 in the lower part of band X).
#              The rulings sit up to ~120 px lower at the left edge, so each
#              crop keeps a margin above and below the band.
#   Rama 7764: X/XI ~200 (crack above it at the centre, inside XI at the left);
#              XI/XII 740; XII/XIII 1290; XIII/XIV 1830; XIV/XV 2350;
#              XV/XVI 2900; end of text ~3420, then the erased surface.
# ---------------------------------------------------------------------------
OBV_CROPS = {
    1: ("sailko", 200, 200, 3620, 870),
    2: ("sailko", 200, 570, 3620, 1250),
    3: ("sailko", 200, 955, 3620, 1620),
    4: ("sailko", 200, 1330, 3620, 2000),
    5: ("sailko", 200, 1670, 3620, 2330),
    6: ("sailko", 200, 2030, 3620, 2690),
    7: ("sailko", 200, 2390, 3620, 3050),
    8: ("sailko", 200, 2730, 3620, 3395),
    9: ("sailko", 200, 3070, 3620, 3730),
    10: ("sailko", 200, 3420, 3620, 4080),
    11: ("rama", 600, 60, 5150, 960),
    12: ("rama", 600, 600, 5150, 1500),
    13: ("rama", 600, 1150, 5150, 2050),
    14: ("rama", 600, 1680, 5150, 2580),
    15: ("rama", 600, 2210, 5150, 3100),
    16: ("rama", 600, 2740, 5150, 3640),
}
OBV_BAND_NOTE = {
    1: "the first band directly beneath the relief (the relief base is at the top of the image)",
    10: "the band crossed near its lower edge by the horizontal crack",
    11: "the band just below the horizontal crack (the crack dips into it at the left)",
    16: "the last inscribed band; the smooth erased surface begins below it",
}

# Montage label centres (x, full-resolution pixels), found from the label row.
MONTAGE_REAR_X = [194, 821, 1155, 1642, 1943, 2370, 2701, 3258, 3616, 3926, 4249, 4591, 4958, 5292,
                  5692, 5996, 6425, 6858, 7168, 7450, 7854, 8258, 8572, 8928, 9309, 9664, 10029, 10367]
MONTAGE_FRONT_X = [5223, 5579, 5884, 6227, 6539, 6872, 7200, 7538, 7924, 8228, 8570, 8910, 9285, 9607,
                   9981, 10309]
MONTAGE_REAR_Y = (4380, 10400)
MONTAGE_FRONT_Y = (260, 4130)

# ---------------------------------------------------------------------------
# Corrections to the Wikisource transcription, restoring Harper's printed text
# (segment, wikisource text, printed text). Each was flagged by at least two of
# the four OCR readings of the printed book and checked on the page image.
# ---------------------------------------------------------------------------
CORRECTIONS = [
    ("prologue", "who seized the enemy", "who seizes the enemy"),
    ("prologue", "the appointments of E-ud-gal-gal", "the appointments in E-ud-gal-gal"),
    ("prologue", "the benefactor of the temple E-mah; the presented life",
     "the benefactor of the temple E-mah; the lordly city king; the soldier who has no equal; who presented life"),
    ("prologue", "When Mardul sent", "When Marduk sent"),
    ("7", "or a man's servant without", "or from a man's servant without"),
    ("13", "he shall bear the penalty", "he shall himself bear the penalty"),
    ("16", "commandment", "commandant"),
    ("25", "casts his eye", "cast his eye"),
    ("26", "dispatch him", "despatch him"),
    ("35", "the cattle of sheep", "the cattle or sheep"),
    ("40", "property-owner", "property-holder"),
    ("47", "to the charge of another", "into the charge of another"),
    ("48", "grain to his creditor", "grain to the creditor"),
    ("49", "Cultivate the field, and take", "Cultivate the field, and harvest and take"),
    ("54", "the farmer whose grain", "the farmers whose grain"),
    ("57", "come to agreement", "come to an agreement"),
    ("107", "the amount which he has obtained", "the amount which he obtained"),
    ("109", "arrest those outlaws", "arrest these outlaws"),
    ("111", "at the time of the harvest", "at the time of harvest"),
    ("115", "in the house of the one who seized him", "in the house of him who seized him"),
    ("117", "purchaser of master", "purchaser or master"),
    ("121", "rate of 5 KA", "rate of five KA"),
    ("123", "at the place of the deposit", "at the place of deposit"),
    ("124", "whatever he disputed", "whatever he has disputed"),
    ("133A", "call that woman into account", "call that woman to account"),
    ("134", "there no be maintenance", "there be no maintenance"),
    ("135", "there no be maintenance", "there be no maintenance"),
    ("135", "his wife enter openly into", "his wife openly enter into"),
    ("137", "give to he the income", "give to her the income"),
    ("142", "and been without reproach and her husband has been going",
     "and be without reproach and her husband have been going"),
    ("142", "her dowry and go to", "her dowry and shall go to"),
    ("151", "before she entered the house of that man", "before she entered into the house of the man"),
    ("155", "throw him in the water", "throw him into the water"),
    ("166", "when the brothers divide, he shall take the present which the father gave him, and over and above they shall divide the goods of the father's house equally.",
     "when the brothers divide, they shall give from the goods of the father's house to their youngest brother, who has not taken a wife, money for a marriage settlement in addition to his portion and they shall enable him to take a wife."),
    ("167", "(the estate).They shall receive the dowries of the respective mothers and divide equally",
     "(the estate). They shall receive the dowries of their respective mothers and they shall divide equally"),
    ("169", "If he commit a crime a second time", "If he commit a grave crime a second time"),
    ("171", "But if a father during", "But if the father during"),
    ("172", "she shall receive the goods of her husband's house", "she shall receive from the goods of her husband's house"),
    ("172", "gave her; and she shall receive", "gave her; she shall receive"),
    ("175", "or a slave of the freeman take", "or a slave of a freeman take"),
    ("176", "or a slave of the freeman take", "or a slave of a freeman take"),
    ("176", "from the time they joined hands;", "from the time they had joined hands;"),
    ("176A", "If the daughter of a man had no dowry", "If the daughter of the man had no dowry"),
    ("177", "inquire into the state of her former husband", "inquire into the estate of her former husband"),
    ("177", "intrust the estate of the former husband", "intrust the estate of her former husband"),
    ("177", "shall revert to the owner.", "shall revert to their owner."),
    ("178", "a dowry or written a deed of gift", "a dowry and written a deed of gift"),
    ("179", "a dowry or written a deed of gift", "a dowry and written a deed of gift"),
    ("182", "If a man do not give a dowry", "If a father do not give a dowry"),
    ("186", "his father and his mother", "his father and mother"),
    ("190", "whom he has taken and reared", "whom he has taken for a son and reared"),
    ("193", "hate the father that has reared", "hate the father who has reared"),
    ("194", "If man give", "If a man give"),
    ("194", "cut off his breast", "cut off her breast"),
    ("203", "another man on his own rank", "another man of his own rank"),
    ("207", "die as a result", "die as the result"),
    ("218", "cause that man's death", "cause the man's death"),
    ("223", "to the builder", "to the physician"),
    ("231", "he shall give the owner of the house a slave", "he shall give to the owner of the house a slave"),
    ("234", "he shall give him 2 shekels", "he shall give to him two shekels"),
    ("235", "reconstruct the boat", "reconstruct that boat"),
    ("237", "that boatman is careless", "that boatman be careless"),
    ("239", "6 GUR", "six GUR"),
    ("248", "he shall pay silver to the owner of the ox to the extent of one-quarter its value",
     "he shall pay silver to the extent of one-fourth of its value"),
    ("253", "and to furnish him", "and furnish him"),
    ("265", "oxen or sheep tenfold", "oxen and sheep tenfold"),
    ("267", "give them to the owner", "give them to their owner"),
    ("273", "from the sixth month until the end", "from the sixth month till the end"),
    ("277", "sixty GUR", "60 GUR"),
    ("epilogue", "efface my statutes", "efface my statues"),
    ("epilogue", "my deeds are unrivaled ''[…]'' and the bringing to honor",
     "my deeds are unrivaled . . . . . . . . . . . . . . . . . . . (Col. 42) and the bringing to honor"),
    ("epilogue", "upon the fields in heaps", "upon the field in heaps"),
    ("epilogue", "with a powerful and may it come", "with a powerful curse and may it come"),
]

# Harper's column markers in the prologue: (column, text before marker, text after marker).
PRO_MARKERS = [
    (2, "who purified ", "the sanctuary of E-apsu"),
    (3, "whose help brings victory", "; who extended the limits of Cutha"),
    (4, "the soldier who has no equal; ", "who presented life"),
    (5, "the powerful son of Sinmu-ballit", ", the ancient seed of royalty"),
]
# ... and in the epilogue (reverse columns; Harper's col. 41 = rev. xxv).
EPI_MARKERS = [
    (25, "remembered with favor in Esagila forever. ", "Let any oppressed man", "(Col. 41.) "),
    (26, ". . . . . . . . . . . . . . . . . . . ", "(Col. 42) and the bringing to honor", ""),
    (27, "who knows everything, who prolongs ", "the days of my life", "(Col. 43) "),
    (28, "and turn good into evil for him! ", "May she shatter his weapons", "(Col. 44.) "),
]
MARKER_ROMAN = {2: "II", 3: "III", 4: "IV", 5: "V"}

# Entries: (slug, title, laws range or part)
ENTRIES = [
    ("prologue", "Code of Hammurabi: Prologue (obverse, columns i-v)", "prologue"),
    ("laws-1-65", "Code of Hammurabi: Laws 1-65 (obverse, columns v-xvi)", (1, 65)),
    ("laws-100-149", "Code of Hammurabi: Laws 100-149 (reverse, columns i-ix)", (100, 149)),
    ("laws-150-199", "Code of Hammurabi: Laws 150-199 (reverse, columns ix-xvii)", (150, 199)),
    ("laws-200-249", "Code of Hammurabi: Laws 200-249 (reverse, columns xvii-xxi)", (200, 249)),
    ("laws-250-282", "Code of Hammurabi: Laws 250-282 (reverse, columns xxi-xxiii)", (250, 282)),
    ("epilogue", "Code of Hammurabi: Epilogue (reverse, columns xxiv-xxviii)", "epilogue"),
]

TOPICS = {
    "laws-1-65": "false accusation and witnesses, judges, theft and receiving, kidnapping, runaway slaves, burglary and robbery, "
                 "the fiefs of soldiers and tax-gatherers, fields, gardens, irrigation, and the leasing of orchards",
    "laws-100-149": "merchants and their agents, wine-sellers, debt, pledges and deposits, slander, adultery, marriage, "
                    "the wives of captives, divorce and the sick wife",
    "laws-150-199": "gifts to wives, debts of husband and wife, incest, betrothal and the marriage settlement, dowries, "
                    "inheritance, children of slave women, priestesses' shares, adoption, and bodily injury",
    "laws-200-249": "bodily injury and its payments, physicians, veterinary surgeons, branders, builders, boatmen, "
                    "and hired oxen",
    "laws-250-282": "the goring ox, the hire of oxen, farm hands and herdsmen, theft of farm implements, wages of labourers "
                    "and craftsmen, hire of boats, and the sale of slaves",
}


# ---------------------------------------------------------------------------
def fetch(url, path):
    if path.exists() and path.stat().st_size > 1000:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sL", "-m", "600", "-A", "TheosisLibrary/1.0 (non-commercial research)",
                    "-o", str(path), url], check=True)
    return path


def atf_to_unicode(s):
    """CDLI ATF -> conventional Unicode transliteration (letters only; no sign changes)."""
    def conv(t, upper=False):
        t = t.replace("sz", "š").replace("SZ", "Š").replace("s,", "ṣ").replace("S,", "Ṣ")
        t = t.replace("t,", "ṭ").replace("T,", "Ṭ")
        t = t.replace("h", "ḫ").replace("H", "Ḫ")
        t = re.sub(r"(?<=[A-Za-zšṣṭḫŠṢṬḪ])(\d+)", lambda m: "".join("₀₁₂₃₄₅₆₇₈₉"[int(c)] for c in m.group(1)), t)
        if upper:
            # capitals outside determinative braces
            t = re.sub(r"\{[^}]*\}|[^{}]+", lambda m: m.group(0) if m.group(0).startswith("{") else m.group(0).upper(), t)
        return t
    out = []
    for i, part in enumerate(s.split("_")):
        out.append(conv(part, upper=(i % 2 == 1)))
    return "".join(out)


def parse_atf():
    text = (SRC / "cdli_P249253.atf").read_text(encoding="utf-8").replace("\r", "")
    face, col, unit = "obv", None, "prologue"
    rows = []
    for ln in text.split("\n"):
        if ln.startswith("@reverse"):
            face = "rev"
            continue
        m = re.match(r"@column (\d+)", ln)
        if m:
            col = int(m.group(1))
            continue
        m = re.match(r"@law (.+)", ln)
        if m:
            unit = m.group(1).strip()
            continue
        if ln.startswith("@epilogue"):
            unit = "epilogue"
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", ln)
        if m:
            u = unit
            # Reverse column 1, lines 1-7: the end of law 100 (its opening stood in the erased columns).
            if face == "rev" and col == 1 and int(m.group(1)) <= 7:
                u = "100"
            rows.append({"face": face, "col": col, "line": int(m.group(1)), "atf": m.group(2), "unit": u})
    return rows


def parse_ws():
    ws = (SRC / "ws_harper.wiki").read_text(encoding="utf-8")
    body = ws.split(";Prologue", 1)[1]
    pro, rest = body.split(";The Code of Hammurabi", 1)
    laws_txt, epi = rest.split(";Epilogue", 1)
    epi = epi.split("{{translation license", 1)[0]
    laws = {}
    for line in laws_txt.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+A?)\.\s+(?:(\d+)\.\s+)?(.*)$", line)
        assert m, line
        key = m.group(1) if not m.group(2) else f"{m.group(1)}-{m.group(2)}"
        laws[key] = m.group(3).strip()
    return pro.strip(), laws, epi.strip()


def clean(t):
    t = re.sub(r"''([^']+)''", r"<em>\1</em>", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


def harper_text():
    pro, laws, epi = parse_ws()
    segs = {"prologue": pro, "epilogue": epi}
    segs.update(laws)
    for seg, old, new in CORRECTIONS:
        s = re.sub(r"[ \t]+", " ", segs[seg])
        n = s.count(old)
        assert n == 1, (seg, old, n)
        segs[seg] = s.replace(old, new)
    for k in segs:
        segs[k] = clean(segs[k]) if k not in ("epilogue",) else segs[k]
    return segs


def split_prologue(pro):
    parts = {}
    rest = pro
    cur = 1
    for col, before, after in PRO_MARKERS:
        key = before + after
        i = rest.find(key)
        assert i >= 0 and rest.count(key) == 1, (col, key)
        cut = i + len(before)
        parts[cur] = rest[:cut].strip()
        rest = f"(Col. {MARKER_ROMAN[col]}) " + rest[cut:].lstrip() if not after.startswith(",") and not after.startswith(";") \
            else f"(Col. {MARKER_ROMAN[col]})" + rest[cut:]
        cur = col
    parts[cur] = rest.strip()
    return parts


def split_epilogue(epi):
    epi = re.sub(r"[ \t]+", " ", epi)
    paras_text = epi
    parts = {}
    cur = 24
    rest = paras_text
    for col, before, after, marker in EPI_MARKERS:
        key = before + after
        i = rest.find(key)
        assert i >= 0 and rest.count(key) == 1, (col, key)
        cut = i + len(before)
        parts[cur] = rest[:cut].rstrip()
        rest = marker + rest[cut:]
        cur = col
    parts[cur] = rest.strip()
    out = {}
    for c, t in parts.items():
        paras = [clean(p) for p in t.split("\n\n") if p.strip()]
        out[c] = "".join(f"<p>{p}</p>" for p in paras)
    return out


# ---------------------------------------------------------------------------
def scan_name(face, col, kind):
    if face == "obv" and kind == "colour":
        return f"{KEY}/obv-col{col:02d}.jpg"
    return f"{KEY}/{face}-col{col:02d}-montage.jpg"


def save_crop(img, box, out):
    c = img.crop(box)
    s = min(1.0, 2600 / max(c.size))
    if s < 1:
        c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    c.save(out, quality=86)


def make_scans():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    imgs = {}
    for k, (p, url) in PHOTO_FILES.items():
        fetch(url, p)
    for col, (src, x0, y0, x1, y1) in OBV_CROPS.items():
        out = ROOT / "site" / "assets" / "scans" / scan_name("obv", col, "colour")
        if not out.exists():
            if src not in imgs:
                imgs[src] = Image.open(PHOTO_FILES[src][0]).convert("RGB")
            save_crop(imgs[src], (x0, y0, x1, y1), out)
    mont = None
    W = None
    for face, xs, (y0, y1), half in (("rev", MONTAGE_REAR_X, MONTAGE_REAR_Y, 600), ("obv", MONTAGE_FRONT_X, MONTAGE_FRONT_Y, 520)):
        for i, x in enumerate(xs, 1):
            out = ROOT / "site" / "assets" / "scans" / scan_name(face, i, "montage")
            if out.exists():
                continue
            if mont is None:
                mont = Image.open(PHOTO_FILES["montage"][0]).convert("RGB")
                W = mont.width
            a, b = x - half, x + half
            if face == "rev" and i == 1:
                a, b = 0, 1300
            if b > W:
                a, b = W - 2 * half, W
            save_crop(mont, (max(0, a), y0, b, y1), out)


# ---------------------------------------------------------------------------
def lines_html(rows, show_col=True):
    out = []
    for r in rows:
        lab = f"{ROMAN[r['col']]} {r['line']}" if show_col else str(r["line"])
        out.append(f"<sup>{lab}</sup>{html.escape(atf_to_unicode(r['atf']), quote=False)}")
    return "<br>".join(out)


def colrange(rows):
    a, b = rows[0], rows[-1]
    fa = "obv." if a["face"] == "obv" else "rev."
    if a["col"] == b["col"]:
        return f"{fa} col. {ROMAN[a['col']]} {a['line']}-{b['line']}"
    return f"{fa} col. {ROMAN[a['col']]} {a['line']} to col. {ROMAN[b['col']]} {b['line']}"


def scans_for(rows):
    cols = []
    for r in rows:
        if (r["face"], r["col"]) not in cols:
            cols.append((r["face"], r["col"]))
    pages = []
    for face, col in cols:
        if face == "obv" and col == 17:
            continue  # erased column: no surface to photograph
        if face == "obv":
            pages.append(scan_name("obv", col, "colour"))
        pages.append(scan_name(face, col, "montage"))
    return cols, pages


def scan_note_for(cols):
    bits = []
    for face, col in cols:
        if face == "obv" and col == 17:
            bits.append("The restored last word in obv. col. xvii stood on the erased part of the stele and is not on any photograph.")
            continue
        if face == "obv":
            where = OBV_BAND_NOTE.get(col, f"band {col} counted from the relief down")
            src = "Sailko photograph" if col <= 10 else "Rama photograph IMG 7764"
            bits.append(f"Obverse column {ROMAN[col]}: in the colour crop of the {src} it is the band in the middle of the image, "
                        f"{where} (the stele's columns are horizontal bands read right to left); in the CDLI montage it is the strip "
                        f"under the label '{ROMAN[col]}' (front surface).")
        else:
            pos = "the left-hand strip" if col == 1 else ("the right-hand strip" if col == 28 else "the middle strip")
            bits.append(f"Reverse column {ROMAN[col]}: CDLI montage, {pos} of the image, under the label '{ROMAN[col]}' (rear surface). "
                        f"In the montage each stele column is turned upright, read top to bottom.")
    return " ".join(bits)


def build():
    for name, url in (("cdli_P249253.atf", CDLI_ATF), ("ws_harper.wiki", WS_URL)):
        fetch(url, SRC / name)
    make_scans()
    rows = parse_atf()
    eng = harper_text()
    pro_eng = split_prologue(eng["prologue"])
    epi_eng = split_epilogue(eng["epilogue"])

    units = {}
    for r in rows:
        units.setdefault(r["unit"], []).append(r)
    law_units = [u for u in units if u not in ("prologue", "epilogue")]
    # sanity: every law unit has Harper English
    for u in law_units:
        base = u
        assert base in eng, base

    common_verif = {
        "scan_source": f"Obverse colour photographs: Wikimedia Commons, {COMMONS_SAILKO} (Francesco Bini/Sailko, 2024) and "
                       f"{COMMONS_RAMA} (Rama, 2018); column montage of both faces: CDLI P249253, {CDLI_MONTAGE}",
        "scan_license": "Sailko photograph CC BY-SA 4.0; Rama photograph CC BY-SA 3.0 FR; CDLI montage credited 'image: Richardson, M., "
                        "A Comprehensive Grammar to Hammurabi's Stele', listed by CDLI as Photo (detail) © Louvre Museum, "
                        "provided by CDLI for the non-commercial use of students, scholars and the public (cdli.earth/terms-of-use)",
        "scan_manuscript": "Paris, Musée du Louvre Sb 8 (stele of Hammurabi, basalt, 225 cm; found at Susa 1901-1902; "
                           "reign of Hammurabi of Babylon, c. 1792-1750 BCE)",
        "scan_mapping": "Law to stele column and line: CDLI ATF of P249253 (@column and @law markers). Column to image: obverse bands "
                        "counted by eye on the colour photographs from the relief down (16 bands, then the erasure), checked against "
                        "the crack at the boundary of columns x and xi and against Zhiltsova's plan of the stele (NABU 2023/3 no. 62); "
                        "montage strips identified by the column labels printed on the CDLI montage, checked against the damage "
                        "the ATF records in obv. x-xi and rev. v-vi, xx-xxiii.",
        "scan_mapping_urls": [CDLI_PAGE, CDLI_ATF, CDLI_MONTAGE, NABU, COMMONS_SAILKO, COMMONS_RAMA, LOUVRE],
        "original_text_source": f"CDLI P249253 ATF transliteration (CDLI staff, R. K. Englund et al.), {CDLI_ATF}; "
                                "ATF letters written in Unicode form (š, ṣ, ṭ, ḫ, subscript sign numbers, Sumerograms in capitals)",
        "original_text_license": "CDLI terms of use: text may be freely copied and re-used according to fair academic practice, with credit to CDLI (https://cdli.earth/terms-of-use)",
        "translation_source": f"Robert Francis Harper, The Code of Hammurabi King of Babylon about 2250 B.C. (University of Chicago Press, 1904); "
                              f"text from Wikisource ({WS_PAGE}) corrected against the printed book ({HARPER_SCAN})",
        "translation_license": "public domain (published 1904; Harper died 1914)",
        "translator": "Robert Francis Harper (1904)",
        "verified_date": TODAY,
    }

    entries = []
    for order, (slug, title, part) in enumerate(ENTRIES, 1):
        sections = []
        if part == "prologue":
            for col in range(1, 6):
                rs = [r for r in units["prologue"] if r["col"] == col]
                cols, pages = scans_for(rs)
                sections.append({
                    "section": ROMAN[col],
                    "original_ref": f"Prologue, {colrange(rs)} (Harper col. {ROMAN[col].upper()})",
                    "original_text": lines_html(rs, show_col=False),
                    "text": f"<p>{pro_eng[col]}</p>",
                    "scan_pages": pages,
                    "scan_note": scan_note_for(cols) + (" The English is cut at Harper's own column markers '(Col. II)' etc., which he placed "
                                                        "where the column begins in his rendering; English word order does not follow the "
                                                        "Akkadian line by line." ),
                })
        elif part == "epilogue":
            for col in range(24, 29):
                rs = [r for r in units["epilogue"] if r["col"] == col]
                cols, pages = scans_for(rs)
                sections.append({
                    "section": ROMAN[col],
                    "original_ref": f"Epilogue, {colrange(rs)} (Harper col. {col + 16})",
                    "original_text": lines_html(rs, show_col=False),
                    "text": epi_eng[col],
                    "scan_pages": pages,
                    "scan_note": scan_note_for(cols) + (" The English is cut at Harper's own column markers '(Col. 41.)' to '(Col. 44.)' "
                                                        "(his continuous numbering: rev. xxv = col. 41). Column xxiv has no marker in "
                                                        "Harper because the epilogue begins at its first line."),
                })
        else:
            lo, hi = part
            keys = [u for u in law_units if lo <= int(u.split("-")[0]) <= hi]
            keys.sort(key=lambda u: int(u.split("-")[0]))
            for u in keys:
                rs = units[u]
                cols, pages = scans_for(rs)
                english = f"<p>{eng[u]}</p>"
                if u in ("133", "176"):
                    english += f"<p><em>§ {u}A.</em> {eng[u + 'A']}</p>"
                note = scan_note_for(cols)
                if u == "100":
                    note += " Only the end of law 100 survives (rev. col. i 1-7); its beginning stood in the erased columns."
                if u == "65":
                    note += " CDLI restores the last word, [i-ma-ad-da-ad], in the erased column xvii."
                ref = f"§ {u}; {colrange(rs)}"
                if u in ("133", "176"):
                    ref = f"§ {u} (Harper § {u} and § {u}A); {colrange(rs)}"
                sections.append({
                    "section": u,
                    "original_ref": ref,
                    "original_text": lines_html(rs, show_col=True),
                    "text": english,
                    "scan_pages": pages,
                    "scan_note": note,
                })
        # the column range in the title must match the CDLI layout
        allrows = [r for u in ([part] if isinstance(part, str) else [x for x in law_units if part[0] <= int(x.split("-")[0]) <= part[1]]) for r in units[u]]
        allrows = [r for r in allrows if not (r["face"] == "obv" and r["col"] == 17)]
        c0, c1 = min(r["col"] for r in allrows), max(r["col"] for r in allrows)
        assert f"columns {ROMAN[c0]}-{ROMAN[c1]})" in title, (title, ROMAN[c0], ROMAN[c1])
        entries.append((order, slug, title, part, sections))

    # ------------------------------------------------------------------ write
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    rows_out = []
    for order, slug, title, part, sections in entries:
        tid = PREFIX + slug
        local = []
        for s in sections:
            for p in s["scan_pages"]:
                if p not in local:
                    local.append(p)
        intro = introduction(slug, part, sections)
        if part == "prologue":
            desc = ("The prologue of the Code of Hammurabi (c. 1754 BCE), in which Hammurabi names the gods who called him to rule "
                    "and the cities he cared for, shown column by column on the Louvre stele.")
        elif part == "epilogue":
            desc = ("The epilogue of the Code of Hammurabi: the king's charge to later rulers and the curses on anyone who alters "
                    "the stele, shown column by column on the Louvre stele.")
        else:
            desc = (f"Laws {part[0]}-{part[1]} of the Code of Hammurabi (c. 1754 BCE): {TOPICS[slug]}. "
                    f"Each law is shown with its Akkadian lines, Harper's English and the stele column that carries it.")
        verif = dict(common_verif)
        verif["scan_local_paths"] = local
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Akkadian (Old Babylonian, CDLI transliteration) / English (Harper 1904)",
            "source": "Louvre Sb 8 photographs (Wikimedia Commons; CDLI montage) + CDLI P249253 transliteration + R. F. Harper's 1904 English",
            "description": desc,
            "introduction": intro,
            "translator_notes": translator_notes(),
            "translation": sections,
            "verification": verif,
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        captions = []
        for p in local:
            m = re.search(r"(obv|rev)-col(\d+)(-montage)?", p)
            face = "obverse" if m.group(1) == "obv" else "reverse"
            captions.append({"file": p, "caption": f"Sb 8, {face} column {ROMAN[int(m.group(2))]}" + (" (CDLI montage)" if m.group(3) else "")})
        rows_out.append({
            "id": tid, "slug": tid, "order": order, "title": title, "author_id": "hammurabi",
            "language": "Akkadian", "era": "Ancient Near East", "tradition": "mesopotamian",
            "category": "law", "date_approx": "c. 1754 BCE (stele set up late in Hammurabi's reign)", "century": -18,
            "source": entry["source"], "description": desc,
            "themes": ["code-of-hammurabi", "hammurabi", "law", "babylon", "akkadian", "stele", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": captions},
        })

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Code of Hammurabi",
            "group": "Mesopotamia", "date_sort": -1754,
            "author_name": "Hammurabi of Babylon (stele, c. 1754 BCE)",
            "source_url": LOUVRE,
            "critical_edition": "CDLI P249253 transliteration of the Louvre stele",
            "translator_name": "Robert Francis Harper (1904)",
            "original_lang_label": "Akkadian · CDLI transliteration",
            "original_lang_code": "akk",
            "edition_label": "",
            "search_terms": "code of hammurabi hammurapi laws louvre sb 8 stele babylon akkadian eye for an eye prologue epilogue",
            "description": "The Code of Hammurabi on the basalt stele in the Louvre (Sb 8): the prologue, laws 1-65 and 100-282, and the "
                           "epilogue, each law shown with its Akkadian lines, Harper's 1904 English and the stele column that carries it.",
        },
        "texts": rows_out,
    }
    COLL.parent.mkdir(parents=True, exist_ok=True)
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    n = sum(len(e[4]) for e in entries)
    print(f"wrote {len(entries)} entries, {n} sections")


def translator_notes():
    return [
        "Akkadian: CDLI transliteration of the Louvre stele. Square brackets mark signs lost on the stone; # marks a damaged sign and ! a sign the editors correct, as in the source.",
        "Line labels such as 'v 26' give the stele column and line. The obverse has 16 legible columns and the reverse 28; seven further obverse columns were erased in antiquity.",
        "English: R. F. Harper (1904), from the Wikisource transcription corrected against the printed book where the two differ. Harper's words in parentheses are his own additions for sense.",
        "Harper numbers the reverse columns continuously after the 16 obverse columns, so his col. 41 is reverse column xxv.",
        "Harper divides laws 133 and 176 into 133 and 133A, 176 and 176A; CDLI keeps one law number for each, so both parts appear in one section. Laws 242 and 243 form one law in both.",
    ]


def introduction(slug, part, sections):
    stele = ("<p>The <strong>Code of Hammurabi</strong> is the longest and best preserved law collection of ancient Mesopotamia. "
             "Hammurabi, king of Babylon (c. 1792-1750 BCE), had it carved on basalt stelae late in his reign. The stele in the Louvre "
             "(Sb 8) is 2.25 m high. At the top Hammurabi stands before the seated sun god Shamash, god of justice; below, the text "
             "runs in horizontal bands, called columns, read from right to left with the signs set upright in the old monumental "
             "manner. The stele was carried off to Susa in Elam as war booty in the 12th century BCE and found there by the French "
             "mission of Jacques de Morgan in 1901-1902. Many of its laws touch matters also treated in the law of Moses in the Old "
             "Testament, such as false witness, theft, kidnapping, slaves, deposits, goring oxen and the rule of like for like "
             "(Exodus 21-23, Leviticus 24, Deuteronomy 19-25).</p>")
    layout = ("<p>Each section below gives the Akkadian lines of the stele as transliterated by CDLI, with column and line "
              "numbers, R. F. Harper's English of 1904, and the photograph of the column that carries those lines. On the obverse "
              "each column is shown twice: a colour crop of the band on the stone (the column is the band in the middle of the image) "
              "and the same column in the photographic montage of the whole inscription distributed by CDLI, where every column "
              "is turned upright and labelled at the top. Reverse columns are shown in the montage. A law that runs over from one "
              "column into the next lists both.</p>")
    if part == "prologue":
        body = ("<p>The <strong>prologue</strong> fills obverse columns i to v line 25. It tells how the gods Anu and Enlil (Bel) "
                "gave Marduk rule over mankind and called Hammurabi 'to cause justice to prevail in the land, to destroy the wicked "
                "and the evil, to prevent the strong from oppressing the weak', and then lists the cities and temples of his "
                "kingdom that he restored and provided for, from Nippur and Eridu to Ashur and Nineveh.</p>")
    elif part == "epilogue":
        body = ("<p>The <strong>epilogue</strong> fills reverse columns xxiv to xxviii. Hammurabi says he set up the stele in "
                "Esagila, the temple of Marduk in Babylon, so that the wronged man could come before his image and have the "
                "inscription read to him; he charges later kings to keep his judgments and calls down the curses of the great gods "
                "on any ruler who alters them or effaces his name.</p>")
    else:
        lo, hi = part
        gap = ""
        if lo == 1:
            gap = (" Laws 66-99 are missing: they stood on the seven columns at the foot of the obverse that were polished away, "
                   "probably to make room for an Elamite inscription that was never cut. They are known in part from clay-tablet "
                   "copies, which are not on this stele and are not shown here.")
        if lo == 100:
            gap = (" The reverse opens with the end of law 100, whose beginning stood in the erased obverse columns.")
        body = (f"<p>This part holds <strong>laws {lo}-{hi}</strong>: {TOPICS[slug]}. Most laws begin with "
                f"<em>šum-ma</em>, 'if'.{gap}</p>")
    return stele + body + layout


if __name__ == "__main__":
    build()
