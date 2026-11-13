#!/usr/bin/env python3
"""
import_dhammapada.py -- the Dhammapada, complete (26 chapters, 423 verses), on a Sinhalese palm-leaf
manuscript: Manchester, John Rylands Library, Pali MS 19 (former owner T. W. Rhys Davids).

One entry per chapter (vagga). Inside each entry, one section per manuscript page (side of a palm leaf):
the verses whose last syllable stands on that page. A verse begun on the previous page lists both pages.

Chain of evidence
-----------------
1. IMAGES        The University of Manchester Library, Pali MS 19 (Dhammapada), ola-leaf manuscript in
                 Sinhalese script, 70 x 620 mm, the second text in a bundle of eleven Khuddakanikaya texts
                 (Pali MSS 18-28). The Dhammapada runs from leaf 5a (leaf numeral 'u') to 16b.
                 Images: Manchester Digital Collections / LUNA, one image per side (16801 x 1900 px), fetched
                 through the LUNA IIIF image API (record ids in data/sources/dhammapada/ms19/luna_records.json,
                 from the LUNA search API). The LUNA HTML viewer pages show a reCAPTCHA check; that page was
                 not used or circumvented. The IIIF image service and search API answer without any check and
                 were used at a low request rate. Each side is published as two halves (left, right), 2600 px wide.
                 Terms: CC BY-NC-SA 4.0 (Access Rights field of the LUNA record).
2. MAPPING       Read on the images by me: the first words of line 1 of every side and the last words of the
                 last line of every side (IIIF regions at full resolution), located in the Pali text. Every
                 side's opening continues the words that end the previous side (checked for all 23 joins), so
                 every page boundary is a reading, not an interpolation. The readings are in READINGS below.
                 One irregularity: at the foot of 13b, after v.326, the scribe wrote v.408-412 (Brahmanavagga)
                 out of place, followed by a row of 'e'-shaped marks and the first word of v.327; v.408-412
                 stand again in their proper place on 16a. The section notes say so.
3. PALI TEXT     SuttaCentral bilara-data root text (Mahasangiti Tipitaka edition), fetched from
                 https://suttacentral.net/api/bilarasuttas/<range>/sujato ; chapter-closing lines
                 ('... vaggo ...') and the closing summary are left out. This is the edited text, not a
                 transcription of the manuscript; the scribe's spellings are not recorded.
4. ENGLISH       F. Max Muller, The Dhammapada (Sacred Books of the East, vol. X, part I, Oxford 1881),
                 public domain. Text: Wikisource 'Dhammapada (Muller)'
                 https://en.wikisource.org/wiki/Dhammapada_(Muller) . Compared word by word with two OCR texts
                 of the printed 1881 book (archive.org dhammapadacollection01ml, thedhammapada00unknuoft);
                 three places where both scans agree against Wikisource are corrected (CORRECTIONS). The
                 Wikisource text omits the diacritics of the printed book in names (Nirvana for Nirvana with
                 circumflex and dot, Brahmana, Mara); Muller's paired verses (58-59, 87-88, ...) stay paired.

Usage:
    python3 scripts/import_dhammapada.py [--force-scans]
"""

import glob
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
KEY = "dhammapada"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
MS = SRC / "ms19"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
FORCE = "--force-scans" in sys.argv
UA = "TheosisLibrary/1.0 (non-commercial research)"

LUNA_SEARCH = ("https://luna.manchester.ac.uk/luna/servlet/as/search?q=Reference_Number=%22Pali+MS+19%22"
               "&lc=Manchester~91~1&fullData=true&bs=100&os=0")
MDC = "https://www.digitalcollections.manchester.ac.uk/collections/pali/1"
WS = "https://en.wikisource.org/wiki/Dhammapada_(Muller)"
WS_RAW = "https://en.wikisource.org/w/index.php?title=Dhammapada_(Muller)&action=raw"
SC = "https://suttacentral.net/dhp"

# ---------------------------------------------------------------------------
# Readings on the images: side -> (first verse ending on it, opening words read, closing words read)
# The first number is the verse in which the side's first line begins.
# ---------------------------------------------------------------------------
SIDES = ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a", "9b", "10a", "10b", "11a", "11b", "12a", "12b",
         "13a", "13b", "14a", "14b", "15a", "15b", "16a", "16b"]
READINGS = {
    "5a": (1, True, "namo tassa bhagavato arahato sammāsambuddhassa, then manopubbaṅgamā dhammā (v.1)",
           "... bhiyyo tappati duggatiṃ gato (end of v.17)"),
    "5b": (18, True, "idha nandati pecca nandati (v.18)", "vārijova thale khitto okamokata ubbha- (v.34)"),
    "6a": (34, False, "-to pariphandatidaṃ cittaṃ māradheyyaṃ pahātave (end of v.34)",
           "na pupphagandho paṭivātameti na candanaṃ tagaramalli- (v.54)"),
    "6b": (54, False, "-kā vā, ... gandho paṭivātameti ... sappuriso pavāti (end of v.54)", "mameva kata- (v.74)"),
    "7a": (74, False, "-ññantu gihī pabbajitā ubho, mamevātivasā assu (v.74)", "uyyuñjanti satīman- (v.91)"),
    "7b": (91, False, "-to na nikete ramanti te, haṃsāva pallalaṃ hitvā (v.91)", "yaṃ kiñci yiṭṭhaṃ va hutaṃ va (v.108)"),
    "8a": (108, False, "loke saṃvaccharaṃ yajetha puññapekkho (v.108)", "na antalikkhe na (v.127)"),
    "8b": (127, False, "samuddamajjhe na pabbatānaṃ vivaraṃ pavissa (v.127)", "... pahassatha dukkhamidaṃ anappakaṃ (end of v.144)"),
    "9a": (145, True, "udakañhi nayanti nettikā (v.145; line 2 has v.147, so not the same words in v.80)",
           "micchādiṭṭhiṃ na seveyya na si- (v.167)"),
    "9b": (167, False, "-yā lokavaḍḍhano (end of v.167), then uttiṭṭhe nappamajjeyya (v.168)",
           "... pantañca sayanāsanaṃ adhicitte ca (v.185)"),
    "10a": (185, False, "āyogo etaṃ buddhāna sāsanaṃ (end of v.185)",
            "pavivekarasaṃ pitvā rasaṃ upasamassa ca niddaro hoti (v.205)"),
    "10b": (205, False, "nippāpo dhammapītirasaṃ pibaṃ (end of v.205)", "yo ve uppatitaṃ kodhaṃ rathaṃ bhantaṃ (v.222)"),
    "11a": (222, False, "-va vāraye, tamahaṃ sārathiṃ brūmi rasmiggāho itaro jano (end of v.222); line 1 goes on with v.223 akkodhena jine kodhaṃ",
            "asajjhāyamalā mantā anuṭṭhānamalā gharā malaṃ vaṇṇassa (v.241)"),
    "11b": (241, False, "kosajjaṃ pamādo rakkhato malaṃ (end of v.241)", "... sa ve dhammadharo hoti yo dhammaṃ nappamajjati (end of v.259)"),
    "12a": (260, True, "na tena thero so hoti yenassa palitaṃ siro (v.260)",
            "uṭṭhānakālamhi anuṭṭhahāno yuvā balī ālasiyaṃ upeto saṃsa- (v.280)"),
    "12b": (280, False, "-nna-saṅka-ppama-no kusīto ... paññāya maggaṃ alaso na vindati (end of v.280; the scribe leaves gaps marked with dashes in line 1)",
            "suppabuddhaṃ pabujjhanti sadā gotamasāvakā yesaṃ divā ca ra- (v.296)"),
    "13a": (296, False, "-tto ca niccaṃ buddhagatā sati (end of v.296)", "... rattiṃ khittā yathā sarā ... naga- (v.315)"),
    "13b": (315, False, "-raṃ yathā paccantaṃ guttaṃ santarabāhiraṃ (v.315)",
            "after v.326 (... hatthippabhinnaṃ viya aṅkusaggaho) the scribe wrote v.408-412 of the Brāhmaṇavagga out of "
            "place (akakkasaṃ viññāpaniṃ giraṃ ... yodha puññañca pāpañca ...), then a row of 'e'-shaped marks, then appamādaratā (first word of v.327)"),
    "14a": (327, False, "the rest of v.327 ... duggā uddharathattānaṃ paṅke sannova kuñjaro",
            "... tasmā tasiṇaṃ vinodaye bhikkhu ākaṅkhī virāgamatta- (v.343)"),
    "14b": (343, False, "-no (last syllable of v.343), then yo nibbanatho vanādhimutto (v.344)",
            "... dinnaṃ hoti mahapphalaṃ (end of v.359) and the chapter title taṇhāvaggo catuvīsatimo"),
    "15a": (360, True, "cakkhunā saṃvaro sādhu sādhu sotena saṃvaro (v.360)",
            "so attagutto satimā sukhaṃ bhikkhu vihāhisi (end of v.379)"),
    "15b": (380, True, "attā hi attano nātho attā hi attano gati (v.380)", "vāri pokkharapat- (v.401)"),
    "16a": (401, False, "-teva āraggeriva sāsapo, yo na limpati kāmesu (end of v.401)",
            "usabhaṃ pavaraṃ vīraṃ mahesiṃ vijitāvinaṃ anejaṃ (v.422)"),
    "16b": (422, False, "nhātakaṃ buddhaṃ tamahaṃ brūmi brāhmaṇaṃ (end of v.422), then pubbenivāsaṃ yo vedī (v.423)",
            "the text ends on this side with v.423; the rest of the last line is blank"),
}

CHAPTERS = [
    (1, 1, 20, "Yamakavagga"), (2, 21, 32, "Appamādavagga"), (3, 33, 43, "Cittavagga"), (4, 44, 59, "Pupphavagga"),
    (5, 60, 75, "Bālavagga"), (6, 76, 89, "Paṇḍitavagga"), (7, 90, 99, "Arahantavagga"), (8, 100, 115, "Sahassavagga"),
    (9, 116, 128, "Pāpavagga"), (10, 129, 145, "Daṇḍavagga"), (11, 146, 156, "Jarāvagga"), (12, 157, 166, "Attavagga"),
    (13, 167, 178, "Lokavagga"), (14, 179, 196, "Buddhavagga"), (15, 197, 208, "Sukhavagga"), (16, 209, 220, "Piyavagga"),
    (17, 221, 234, "Kodhavagga"), (18, 235, 255, "Malavagga"), (19, 256, 272, "Dhammaṭṭhavagga"),
    (20, 273, 289, "Maggavagga"), (21, 290, 305, "Pakiṇṇakavagga"), (22, 306, 319, "Nirayavagga"),
    (23, 320, 333, "Nāgavagga"), (24, 334, 359, "Taṇhāvagga"), (25, 360, 382, "Bhikkhuvagga"),
    (26, 383, 423, "Brāhmaṇavagga"),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI",
         "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI"]

# Wikisource -> printed 1881 text (both archive.org OCR texts agree on the printed reading)
CORRECTIONS = [
    ("70", "yet he is not worth", "yet is he not worth"),
    ("98", "(Arhanta)", "(Arahanta)"),
    ("338", "destroyed, the pain (of life)", "destroyed, this pain (of life)"),
]


def fetch(url, path):
    if path.exists() and path.stat().st_size > 1000:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sL", "-m", "300", "-A", UA, "-o", str(path), url], check=True)
    return path


# ---------------------------------------------------------------------------
def pali_verses():
    V = {}
    for f in sorted(glob.glob(str(SRC / "sc_dhp*.json"))):
        rt = json.load(open(f, encoding="utf-8"))["root_text"]
        for k, v in rt.items():
            m = re.match(r"dhp(\d+):(\d+)$", k)
            if not m or int(m.group(2)) == 0:
                continue
            V.setdefault(int(m.group(1)), []).append((int(m.group(2)), v.strip()))
    out = {}
    for n, lines in V.items():
        lines.sort()
        keep = []
        for _, t in lines:
            if re.search(r"vaggo\b", t, re.I):
                break
            keep.append(t)
        out[n] = keep
    assert sorted(out) == list(range(1, 424)), "missing Pali verses"
    return out


def muller():
    s = (SRC / "ws_muller.wiki").read_text(encoding="utf-8")
    body = s.split("==Chapter I:", 1)[1]
    body = body.split("{{translation license", 1)[0].split("[[Category", 1)[0]
    items = {}
    for m in re.finditer(r"(?:\{\{verse\|chapter=[IVXL]+\|verse=(\d+)\}\}|\n(\d+), (\d+)\.)\s*(.*?)"
                         r"(?=\{\{verse|\n\d+, \d+\.|\n==|\Z)", body, re.S):
        key = m.group(1) or f"{m.group(2)}-{m.group(3)}"
        t = re.sub(r"\s+", " ", m.group(4)).strip()
        t = t.replace("--", "—")
        items[key] = t
    for k, old, new in CORRECTIONS:
        assert items[k].count(old) == 1, (k, old)
        items[k] = items[k].replace(old, new)
    titles = re.findall(r"==Chapter ([IVXL]+)\s*[:\-]\s*([^=]+?)==", "==Chapter I:" + body)
    return items, {r: t.strip() for r, t in titles}


def side_of_verse():
    """verse -> (side where it ends, side where it begins)"""
    starts = [(READINGS[s][0], s) for s in SIDES]
    end_side, begin_side = {}, {}
    for v in range(1, 424):
        # the side whose first verse number is the largest <= v
        cand = [s for first, s in starts if first <= v]
        last = cand[-1]
        # if v is the first verse of a side and the side does not begin at the verse start, it began on the previous side
        idx = SIDES.index(last)
        first, exact = READINGS[last][0], READINGS[last][1]
        end_side[v] = last
        if first == v and not exact:
            begin_side[v] = SIDES[idx - 1]
        else:
            begin_side[v] = last
    return end_side, begin_side


# ---------------------------------------------------------------------------
def scan_names(side):
    return [f"{KEY}/ms19-f{side.zfill(3)}-1.jpg", f"{KEY}/ms19-f{side.zfill(3)}-2.jpg"]


def make_scans():
    recs = {r[1]: r for r in json.load(open(MS / "luna_records.json"))}
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for s in SIDES:
        lid = recs[s][5].split("/m/")[1].split("/")[0]
        for half, region in ((1, "0,0,8420,1900"), (2, "8380,0,8421,1900")):
            out = ROOT / "site" / "assets" / "scans" / scan_names(s)[half - 1]
            if out.exists() and not FORCE:
                continue
            tmp = MS / "halves" / f"{s}_{half}.jpg"
            fetch(f"https://luna.manchester.ac.uk/luna/servlet/iiif/{lid}/{region}/2600,/0/default.jpg", tmp)
            im = Image.open(tmp).convert("RGB")
            im.save(out, quality=86)


def section_note(side, verses, begin_side):
    first_v = verses[0]
    rd = READINGS[side]
    bits = [f"Pali MS 19, fol. {side} (both halves of the leaf side). Checked on the image: the side begins "
            f"'{rd[2]}' and its last line ends '{rd[3]}'."]
    if begin_side.get(first_v) != side:
        bits.append(f"Verse {first_v} begins on fol. {begin_side[first_v]} and ends on fol. {side}; both sides are shown.")
    if side == "13b":
        bits.append("The verses 408-412 written out of place at the foot of this side are not part of this chapter's text "
                    "here; they are shown with chapter 26 on fol. 16a, where the scribe wrote them in their place.")
    bits.append("The Pali shown is the Mahāsaṅgīti edition (SuttaCentral), not a transcription of the manuscript; "
                "the scribe's spellings differ in places.")
    return " ".join(bits)


def build():
    for f in ("ws_muller.wiki",):
        fetch(WS_RAW, SRC / f)
    fetch(LUNA_SEARCH, MS / "luna_search.json")
    make_scans()
    pali = pali_verses()
    eng, titles = muller()
    end_side, begin_side = side_of_verse()

    # English units in verse order (pairs kept together, keyed by their last verse)
    units = []
    for k, t in eng.items():
        a, b = (int(k), int(k)) if "-" not in k else tuple(map(int, k.split("-")))
        units.append((a, b, k, t))
    units.sort()
    assert sum(b - a + 1 for a, b, _, _ in units) == 423

    verif_common = {
        "scan_source": f"The University of Manchester Library, Pali MS 19, LUNA IIIF image service (records found with {LUNA_SEARCH}); "
                       f"Manchester Digital Collections, Pali manuscripts ({MDC})",
        "scan_license": "CC BY-NC-SA 4.0 (Access Rights stated on the LUNA record; rights holder: The University of Manchester Library)",
        "scan_manuscript": "Manchester, John Rylands Library, Pali MS 19: Dhammapada, ola (palm) leaf manuscript in Sinhalese "
                           "script, 70 x 620 mm, leaves 5a-16b of a bundle of eleven Khuddakanikāya texts (Pali MSS 18-28); "
                           "undated; former owner T. W. Rhys Davids (Jayawickrama 1972)",
        "scan_mapping": "Verse to page: the opening words of line 1 and the closing words of the last line of every side were read "
                        "on the images and located in the Pali text; each side's opening continues the words that close the "
                        "previous side (all 23 joins checked). A verse belongs to the side on which its last syllable stands; "
                        "a verse that begins on the previous side lists both sides.",
        "original_text_source": f"SuttaCentral bilara-data, Pali root text (Mahāsaṅgīti Tipiṭaka edition), {SC}",
        "original_text_license": "SuttaCentral bilara-data, dedicated to the public domain (CC0) by SuttaCentral (LICENSE.md, suttacentral.net/licensing)",
        "translation_source": f"F. Max Müller, The Dhammapada (Sacred Books of the East X, part I, Oxford 1881); text from Wikisource ({WS}), "
                              "compared with two OCR texts of the 1881 printing (archive.org dhammapadacollection01ml, thedhammapada00unknuoft)",
        "translation_license": "public domain (published 1881; Müller died 1900)",
        "translator": "F. Max Müller (1881)",
        "verified_date": TODAY,
    }

    PUB_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for ch, lo, hi, pname in CHAPTERS:
        etitle = titles[ROMAN[ch]]
        # group units by end side
        groups = {}
        for a, b, k, t in units:
            if lo <= a <= hi:
                groups.setdefault(end_side[b], []).append((a, b, k, t))
        sections = []
        local = []
        for side in SIDES:
            if side not in groups:
                continue
            us = groups[side]
            verses = [v for a, b, _, _ in us for v in range(a, b + 1)]
            orig = "<br>".join(
                f"<sup>{v}</sup>" + " ".join(html.escape(x) for x in pali[v]) for v in verses)
            orig = re.sub(r"(<br>)", r"\1", orig)
            text = "".join(f"<p><sup>{k}</sup>{html.escape(t, quote=False)}</p>" for a, b, k, t in us)
            pages = []
            if begin_side[verses[0]] != side:
                pages += scan_names(begin_side[verses[0]])
            pages += scan_names(side)
            for p in pages:
                if p not in local:
                    local.append(p)
            sections.append({
                "section": side,
                "original_ref": f"Dhp {verses[0]}-{verses[-1]}" if len(verses) > 1 else f"Dhp {verses[0]}",
                "original_text": orig,
                "text": text,
                "scan_pages": pages,
                "scan_note": section_note(side, verses, begin_side),
            })
        slug = f"{ch:02d}-{re.sub(r'[^a-z]+', '-', pname.lower().replace('ā','a').replace('ṇ','n').replace('ṭ','t').replace('ī','i')).strip('-')}"
        tid = PREFIX + slug
        short = re.sub(r"\s*\([^)]*\)", "", etitle).strip()
        title = f"Dhammapada {ch}: {pname}, {short} (verses {lo}-{hi})"
        sides_used = [s["section"] for s in sections]
        intro = (
            f"<p>Chapter {ch} of the Dhammapada, the <em>{pname}</em> ('{etitle}' in Max Müller's translation), verses {lo}-{hi}. "
            "The Dhammapada is a collection of 423 verses in Pali attributed to the Buddha, part of the Khuddakanikāya of the "
            "Pali canon; its compilation is usually dated to about the third century BCE.</p>"
            "<p>The images are of a Sinhalese palm-leaf manuscript in the John Rylands Library, Manchester (Pali MS 19), once owned by "
            "T. W. Rhys Davids. The text is written in Sinhalese script across the whole width of each leaf, nine lines a side, "
            "interrupted only by the string holes; each image is one half of a leaf side. "
            f"This chapter is on fol. {', '.join(sides_used)}. Each section holds the verses that end on that side.</p>"
            "<p>The Pali is the Mahāsaṅgīti edition published by SuttaCentral, and the English is Max Müller's translation in the "
            "Sacred Books of the East (1881), which sometimes renders two verses together (for example 58-59).</p>")
        if ch in (23, 26):
            intro += ("<p>At the foot of fol. 13b, after verse 326, the scribe wrote verses 408-412 out of place, then a row of "
                      "marks, and went on with verse 327. The same verses stand in their proper place on fol. 16a.</p>")
        desc = (f"Dhammapada chapter {ch}, {pname} ('{short}', verses {lo}-{hi}): Pali text and Max Müller's English, each "
                "verse on the page of a Sinhalese palm-leaf manuscript (Manchester, Pali MS 19) that carries it.")
        verif = dict(verif_common)
        verif["scan_local_paths"] = local
        verif["scan_mapping_urls"] = [LUNA_SEARCH, MDC]
        entry = {
            "id": tid, "slug": tid, "title": title,
            "language": "Pali (Mahāsaṅgīti edition) / English (Max Müller 1881)",
            "source": "Manchester, John Rylands Library, Pali MS 19 (palm leaf, Sinhalese script) + SuttaCentral Pali (Mahāsaṅgīti) + Max Müller's English (SBE X, 1881)",
            "description": desc, "introduction": intro,
            "translator_notes": [
                "Müller's English is from the Wikisource transcription, which leaves out the diacritics the printed book uses in names (for example Nirvana, Brahmana, Mara).",
                "Words in round brackets are Müller's additions for sense.",
            ],
            "translation": sections, "verification": verif,
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": ch, "title": title, "author_id": "buddha-gautama",
            "language": "Pali", "era": "Axial Age", "tradition": "buddhist", "category": "sacred-text",
            "date_approx": "c. 3rd century BCE (compilation); manuscript undated (Sinhalese palm leaf, Manchester Pali MS 19)",
            "century": -3, "source": entry["source"], "description": desc,
            "themes": ["dhammapada", "pali", "buddhist", "khuddakanikaya", f"vagga-{ch}", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": f"Pali MS 19, fol. {p.split('-f')[1].split('-')[0].lstrip('0')}, "
                                                        f"{'left' if p.endswith('-1.jpg') else 'right'} half"} for p in local]},
        })

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Dhammapada", "group": "India", "date_sort": -250,
            "author_name": "Attributed to the Buddha; Pali canon (Khuddakanikāya)",
            "source_url": MDC,
            "critical_edition": "SuttaCentral, Mahāsaṅgīti Tipiṭaka edition",
            "translator_name": "F. Max Müller (1881)",
            "original_lang_label": "Pali · Mahāsaṅgīti edition",
            "original_lang_code": "pi",
            "edition_label": "",
            "search_terms": "dhammapada pali buddha buddhist verses khuddakanikaya yamaka twin verses max muller sinhalese palm leaf",
            "description": ("The complete Dhammapada, 423 verses in 26 chapters: the Pali text and Max Müller's 1881 English, each "
                            "verse on the page of a Sinhalese palm-leaf manuscript in the John Rylands Library, Manchester "
                            "(Pali MS 19), that carries it."),
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} entries, {sum(1 for r in rows for _ in [0])} rows")


if __name__ == "__main__":
    build()
