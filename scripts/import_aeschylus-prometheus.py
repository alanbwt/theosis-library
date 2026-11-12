#!/usr/bin/env python3
"""
import_aeschylus-prometheus.py: Aeschylus, Prometheus Bound 436-525 (Prometheus' account of the
arts he gave to mankind), on the Medicean manuscript, Florence, Laur. Plut. 32.9 (10th century).

One entry; nine sections (one per speech or sense unit), each linked to the manuscript page(s)
that carry its lines.

Chain of evidence
  1. MANUSCRIPT  Florence, Biblioteca Medicea Laurenziana, Plut. 32.9 (Aeschylus siglum M),
     parchment, library dating 901-1000; Sophocles, Aeschylus, Apollonius Rhodius, with scholia.
     Teca digitale BML (CONTENTdm IIIF), manifest
     https://cdm21059.contentdm.oclc.org/iiif/2/plutei:711140/manifest.json. The play begins on
     fol. 147v (title, hypothesis and list of characters, read on the image); lines 436-525 stand
     on fol. 152v, 153r and 153v, one column of verse with scholia in the margins.
  2. MAPPING  The first and last verse of each of the three pages, and the verse where the
     passage begins (436, marked with a dash in the margin of fol. 152v) and ends (525), were
     read on IIIF crops and identified in the Greek text; the words read are stored in PAGES and
     quoted in each section's scan_note. No page was placed by counting or by text length.
  3. GREEK  H. W. Smyth, Aeschylus I (Loeb Classical Library, 1922), Perseus canonical-greekLit
     tlg0085.tlg003.perseus-grc2 (CC BY-SA 4.0; edition public domain).
  4. ENGLISH  H. W. Smyth, Aeschylus I (Loeb, London: Heinemann / New York: Putnam, 1922),
     pp. 255-263, public domain in the US (published 1922). The Perseus English file is a 1988
     modernised version of Smyth, so it was not used; the text below was taken from the
     archive.org OCR of the 1922 printing (item aeschyluswithan00smytgoog) and checked word by
     word against the page images of that scan (leaves n301-n309); the OCR's stray marks were
     removed. Smyth's English has no line numbers; each section starts where the speech or
     sense unit starts in both languages.

Usage:
    python3 scripts/import_aeschylus-prometheus.py           # build
    python3 scripts/import_aeschylus-prometheus.py --force   # re-download scans
"""

import argparse
import html as H
import io
import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

KEY = "aeschylus-prometheus"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"
UA = "TheosisLibrary/1.0 (non-commercial research; +https://theosislibrary.com)"
GREEK_URL = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0085/tlg003/tlg0085.tlg003.perseus-grc2.xml"
SMYTH_ITEM = "https://archive.org/details/aeschyluswithan00smytgoog"

BML_SVC = "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:"
BML_VIEW = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/"
MANIFEST = "https://cdm21059.contentdm.oclc.org/iiif/2/plutei:711140/manifest.json"
BML_LICENSE = ("Biblioteca Medicea Laurenziana, Teca digitale (access 'Pubblico'); su concessione del Ministero della Cultura; "
               "reproduced for non-commercial study with credit (Italian Code of Cultural Heritage, art. 108 c. 3-bis)")

# folio, IIIF id, first verse, last verse, words read on first and last verse lines, extra
PAGES = [
    ("152v", "710908", 408, 453, "μεγαλοσχήμονά τ᾽ ἀρχαι(οπρεπῆ)", "μύρμηκες ἄντρων ἐν μυχοῖς ἀνηλίοις",
     "436 'μή τοι χλιδῇ δοκεῖτε μηδ᾽ αὐθαδίᾳ' begins in the lower half of the page, marked with a dash in the left margin; 447 'οἳ πρῶτα μὲν βλέποντες ἔβλεπον μάτην' is eleven lines below it."),
    ("153r", "710909", 454, 501, "ἦν δ᾽ οὐδὲν αὐτοῖς οὔτε χείματος τέκμαρ", "κεκρυμμέν᾽ ἀνθρώποισιν ὠφελήματα",
     "459 'καὶ μὴν ἀριθμόν, ἔξοχον σοφισμάτων' is the sixth line of the page."),
    ("153v", "710910", 502, 561, "χαλκόν, σίδηρον, ἄργυρον, χρυσόν τε τίς", "(τίς) γῆ; τί γένος; τίνα φῶ λεύσσειν (Io's entry)",
     "525 'δεσμοὺς ἀεικεῖς καὶ δύας ἐκφυγγάνω' stands in the middle of the page, followed by the first choral ode (526ff.)."),
]

# Smyth 1922 English, pp. 255-263 (checked on the page images). Speaker labels as printed.
SECTIONS = [
    (436, 446, "Prometheus' silence; he will tell what he did for mankind", [
        ("Prometheus", "Nay, impute it not to pride nor yet to wilfulness that I am silent. Painful thoughts devour my heart as I behold myself maltreated thus. "
         "And yet who but I definitely assigned their prerogatives unto these upstart gods? But of this I speak not; for my tale would tell you naught save what ye know. "
         "But hearken to the miseries that beset mankind—how that they were witless erst and I made them to have sense and be endowed with reason. "
         "Nor will I speak to upbraid mankind, but to set forth the friendly purpose that inspired my boons.")]),
    (447, 458, "men before Prometheus: like shapes in dreams, living in caves; the stars", [
        (None, "First of all, though they had eyes to see, they saw to no avail; they had ears, but understood not; but, like to shapes in dreams, throughout their length of days, "
         "without purpose they wrought all things in confusion. Knowledge had they neither of houses built of bricks and turned to face the sun, nor yet of work in wood; "
         "but dwelt beneath the ground like swarming ants, in sunless caves. They had no sign either of winter or of flowery spring or of fruitful summer, whereon they could depend, "
         "but in everything they wrought without judgment, until such time as I taught them to discern the risings of the stars and their settings, ere this ill distinguishable.")]),
    (459, 468, "numbers, letters, the yoke, horses, ships", [
        (None, "Aye, and numbers, too, chiefest of sciences, I invented for them, and the combining of letters, creative mother of the Muses' arts, wherewith to hold all things in memory. "
         "I, too, first brought brute beasts beneath the yoke to be subject to the collar and the pack-saddle, that they might bear in men's stead their heaviest burdens; "
         "and to the chariot I harnessed horses and made them obedient to the rein, to be an adornment of wealth and luxury. "
         "'Twas I and no one else that contrived the mariner's flaxen-winged car to roam the sea.")]),
    (469, 471, "the inventor cannot free himself", [
        (None, "Wretched that I am—such are the inventions I devised for mankind, yet have myself no cunning wherewith to rid me of my present suffering.")]),
    (472, 475, "the chorus: an unskilled physician", [
        ("Chorus", "Thou hast suffered sorrow and humiliation. Thou art forsaken of thy wits and art gone astray; and, like an unskilled leech, fallen ill, "
         "thou losest heart and canst not discover what remedies to minister to thine own disease.")]),
    (476, 483, "medicine", [
        ("Prometheus", "Hear but the rest and thou shalt wonder the more at the arts and resources I devised. This first and foremost: if ever man fell ill, there was no defence—"
         "no healing food, no ointment, nor any draught—but for lack of medicine they wasted away, until I showed them how to mix soothing remedies wherewith they now ward off all their disorders.")]),
    (484, 499, "divination: dreams, omens, birds, sacrifice, fire", [
        (None, "And I marked out many ways whereby they might read the future, and among dreams I first discerned which are destined to come true; and voices baffling interpretation "
         "I explained to them, and signs from meetings by the way. The flight of crook-taloned birds I distinguished clearly—which by nature are auspicious, which sinister—"
         "their various modes of life, their mutual feuds and loves, and their consortings; and the smoothness of their entrails, and what colour the gall must have to please the gods, "
         "and the speckled symmetry of the liver-lobe; and the thigh-bones, enwrapped in fat, and the long chine I burned and initiated mankind into an occult art. "
         "Also I cleared their vision to discern signs from flames, erstwhile obscure.")]),
    (500, 506, "metals; every art from Prometheus", [
        (None, "So much then touching these arts. Now as to the benefits to men that lay concealed beneath the earth—bronze, iron, silver, and gold—who would claim to have discovered them before me? "
         "No one, I know full well, unless he were fain to babble idly. Hear the sum of the whole matter in the compass of one brief word—every art possessed by man comes from Prometheus.")]),
    (507, 525, "art is weaker than Necessity; the Fates and the Furies; the secret", [
        ("Chorus", "Do not then benefit mortals beyond due measure and yet be heedless of thine own distress; forasmuch as I am of good hope that thou shalt yet be loosed from these bonds "
         "and have power no wise inferior to Zeus."),
        ("Prometheus", "Not thus, nor yet, is fulfilling Fate destined to bring this end to pass. When I have been bent by pangs and tortures infinite, thus only am I to escape my bondage. "
         "Art is feebler far than Necessity."),
        ("Chorus", "Who then is the steersman of Necessity?"),
        ("Prometheus", "The triform Fates and mindful Furies."),
        ("Chorus", "Can it be that Zeus hath lesser power than they?"),
        ("Prometheus", "Aye, in that at least he cannot escape what is foredoomed."),
        ("Chorus", "Why, what is foredoomed for Zeus save to hold eternal sway?"),
        ("Prometheus", "This thou must not learn as yet; be not importunate."),
        ("Chorus", "'Tis some solemn secret, surely, that thou dost enshroud in mystery."),
        ("Prometheus", "Bethink ye of some other theme, for 'tis in no wise meet time to discourse of this. At every hazard this must be kept concealed; "
         "for 'tis by safeguarding it that I am to escape my ignominious bonds and outrage.")]),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def cached(name, url):
    p = SRC / name
    if not p.exists():
        SRC.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url))
    return p


def get_scan(folio, sid, force):
    from PIL import Image
    path = SCAN_DIR / f"laur32-9-f{folio}.jpg"
    if path.exists() and not force:
        return path
    Image.open(io.BytesIO(fetch(f"{BML_SVC}{sid}/full/1700,/0/default.jpg"))).convert("RGB").save(path, quality=85)
    return path


def greek_lines():
    """{line: (speaker, text)} from the Perseus TEI (speaker taken from the enclosing <sp>)."""
    root = ET.parse(cached("tlg0085.tlg003.perseus-grc2.xml", GREEK_URL)).getroot()
    out = {}
    for sp in root.iter(f"{TEI}sp"):
        who = sp.find(f"{TEI}speaker")
        who = re.sub(r"\s+", " ", "".join(who.itertext())).strip() if who is not None else ""
        for l in sp.iter(f"{TEI}l"):
            n = l.get("n")
            if n and n.isdigit():
                out[int(n)] = (who, re.sub(r"\s+", " ", "".join(l.itertext())).strip())
    return out


def esc(t):
    return H.escape(t, quote=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cached("laur32-9-manifest.json", MANIFEST)
    grc = greek_lines()
    files = {p[0]: get_scan(p[0], p[1], args.force) for p in PAGES}

    def page_note(p):
        return (f"Laur. Plut. 32.9 fol. {p[0]} runs from '{p[4]}' on its first verse line ({p[2]}) to '{p[5]}' on its last ({p[3]}). "
                f"{p[6]} Viewer: {BML_VIEW}{p[1]}")

    sections = []
    for a, b, label, speeches in SECTIONS:
        pages = [p for p in PAGES if p[2] <= b and p[3] >= a]
        assert pages, (a, b)
        out, prev = [], None
        for n in range(a, b + 1):
            who, text = grc[n]
            line = f"<sup>{n}</sup>{esc(text)}"
            if who != prev:
                line = f"<em>{esc(who)}</em><br>\n" + line
                prev = who
            out.append(line)
        greek = "<p>" + "<br>\n".join(out) + "</p>"
        eng = []
        for i, (who, text) in enumerate(speeches):
            lab = f"<em>{esc(who)}</em><br>\n" if who else ""
            num = f"<sup>{a}</sup>" if i == 0 else ""
            eng.append(f"<p>{lab}{num}{esc(text)}</p>")
        where = ", ".join(f"fol. {p[0]}" for p in pages)
        if len(pages) == 1:
            note = f"Lines {a}-{b} are on Laur. Plut. 32.9 fol. {pages[0][0]}. "
        else:
            note = f"Lines {a}-{b} start on Laur. Plut. 32.9 fol. {pages[0][0]} and continue on fol. {pages[-1][0]} (page break inside this section). "
        note += "Checked on the images: " + " ".join(page_note(p) for p in pages)
        note += " The Greek shown is Smyth's edited text; the manuscript's accents and some readings differ from it (Smyth's notes record M's readings)."
        sections.append({
            "section": f"{a}-{b}",
            "original_ref": f"Aeschylus, Prometheus Bound {a}-{b} ({label}); Laur. Plut. 32.9 {where}",
            "original_text": greek,
            "text": "\n".join(eng),
            "scan_pages": [f"{KEY}/{files[p[0]].name}" for p in pages],
            "scan_note": note,
        })

    tid = PREFIX + "436-525-the-gifts-of-prometheus"
    title = "Aeschylus, Prometheus Bound 436-525: the arts Prometheus gave to mankind"
    desc = ("Prometheus, chained to his rock, tells the chorus how mankind lived like shapes in dreams until he gave them the stars, numbers, letters, "
            "the yoke, ships, medicine, divination and metals: 'every art possessed by man comes from Prometheus'. Shown on the 10th-century Medicean manuscript, Laur. Plut. 32.9.")
    intro = (
        "<p><em>Prometheus Bound</em>, handed down under the name of Aeschylus (died 456 BCE), shows the Titan Prometheus nailed to a rock at the edge of the world "
        "as punishment for stealing fire and giving it to mortals. In this speech to the chorus of the daughters of Oceanus he describes the first state of mankind: "
        "they saw without seeing and heard without understanding, 'like to shapes in dreams', and lived in sunless caves like ants, with no way of telling the seasons. "
        "Prometheus taught them the risings and settings of the stars, numbers, 'chiefest of sciences', and the combining of letters, the yoke for animals, the chariot and the ship, "
        "medicine, every kind of divination, and the use of the metals hidden in the earth: 'every art possessed by man comes from Prometheus' (506). "
        "The section ends with a short exchange in which Prometheus says that art is weaker than Necessity, which is steered by the Fates and the Furies, "
        "and hints at the secret on which the fate of Zeus depends.</p>\n\n"
        "<p>The pages shown are from Florence, Biblioteca Medicea Laurenziana, Plut. 32.9, the Medicean manuscript, written in the 10th century, "
        "the oldest and most important manuscript of Aeschylus (siglum M). The play begins on fol. 147v; lines 436-525 stand on fol. 152v, 153r and 153v, "
        "in one column of verse with ancient commentary (scholia) in the margins. Each section below is one speech or one part of a speech; "
        "the page or pages listed for it were identified by reading the first and last verse of each page on the images. "
        "The Greek is Smyth's edition (1922), not a transcription of the manuscript. The English is Smyth's Loeb translation of the same year. "
        "The rest of the play is not included in this entry.</p>"
    )
    entry = {
        "id": tid, "slug": tid, "title": title,
        "language": "Greek (Smyth) / English (H. W. Smyth, 1922)",
        "source": "Florence, Laur. Plut. 32.9 (Medicean Aeschylus) fol. 152v-153v via Teca digitale BML + Smyth Greek (Perseus) + Smyth English (Loeb 1922, archive.org scan)",
        "description": desc,
        "introduction": intro,
        "translator_notes": [
            "Greek: Herbert Weir Smyth, Aeschylus I (Loeb Classical Library, 1922), Perseus digital text; speaker names as in Perseus.",
            "English: Herbert Weir Smyth, Aeschylus I (Loeb Classical Library, 1922), pp. 255-263, transcribed from the archive.org scan of the 1922 printing and checked against its page images. "
            "Smyth's English is prose without line numbers; each section begins where the speech or sense unit begins.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Biblioteca Medicea Laurenziana, Teca digitale (CONTENTdm), Plut. 32.9, IIIF manifest {MANIFEST} (fol. 152v, 153r, 153v)",
            "scan_license": BML_LICENSE,
            "scan_manuscript": ("Florence, Biblioteca Medicea Laurenziana, Plut. 32.9 (Aeschylus siglum M; Medicean manuscript), parchment, library dating 901-1000; "
                                "Sophocles, Aeschylus and Apollonius Rhodius with scholia; Prometheus Bound begins on fol. 147v"),
            "scan_mapping": "Own visual check: the first and last verse of fol. 152v, 153r and 153v, and the verses where the passage begins (436) and ends (525), were read on IIIF crops and identified in the Greek text (words recorded in each scan_note)",
            "scan_mapping_urls": [MANIFEST, "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/711140", BML_VIEW + "710898"]
                                 + [BML_VIEW + p[1] for p in PAGES],
            "scan_local_paths": [f"{KEY}/{files[p[0]].name}" for p in PAGES],
            "original_text_source": f"Herbert Weir Smyth, Aeschylus I (Loeb Classical Library; London: Heinemann / New York: Putnam, 1922), Perseus canonical-greekLit tlg0085.tlg003.perseus-grc2 ({GREEK_URL})",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": f"Herbert Weir Smyth, Aeschylus I: Suppliant Maidens, Persians, Prometheus, Seven against Thebes (Loeb Classical Library; London: Heinemann / New York: Putnam, 1922), pp. 255-263; scan and OCR at {SMYTH_ITEM}",
            "translation_license": "public domain in the US (published 1922)",
            "translator": "H. W. Smyth (1922)",
            "verified_date": TODAY,
        },
    }
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    row = {
        "id": tid, "slug": tid, "order": 1, "title": title, "author_id": "aeschylus",
        "language": "Greek", "era": "Classical", "tradition": "greek", "category": "literature",
        "date_approx": "5th century BCE (composition); manuscript 10th century",
        "century": -5, "source": entry["source"], "description": desc,
        "themes": ["aeschylus", "prometheus", "prometheus-bound", "gifts-of-civilisation", "origins-of-the-arts", "earliest-ages",
                   "astronomy", "writing", "medicine", "divination", "metals", "fate", "tragedy", "greek", "verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f"{KEY}/{files[p[0]].name}", "caption": f"Laur. Plut. 32.9 fol. {p[0]}"} for p in PAGES]},
    }
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Aeschylus: Prometheus Bound",
            "group": "Greece",
            "date_sort": -460,
            "author_name": "Aeschylus (c. 525-456 BCE); Medicean manuscript of the 10th century",
            "source_url": "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/711140",
            "critical_edition": "Smyth, Aeschylus I (Loeb 1922), via Perseus",
            "translator_name": "H. W. Smyth (Loeb, 1922)",
            "original_lang_label": "Greek · Smyth",
            "original_lang_code": "grc",
            "edition_label": "",
            "search_terms": "aeschylus prometheus bound arts of mankind fire numbers letters writing stars medicine divination metals necessity fates medicean laurentianus",
            "description": "Prometheus' speech on the arts he gave to mankind, from Prometheus Bound, on the 10th-century Medicean manuscript of Aeschylus.",
        },
        "texts": [row],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {tid} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
