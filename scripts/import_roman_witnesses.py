#!/usr/bin/env python3
"""
import_roman_witnesses.py -- Roman writers on Christ and the early Christians,
each passage shown on the medieval manuscript page that carries it.

Collection key: roman-witnesses   (prefix verified-roman-witnesses-)

Entries and chain of evidence
-----------------------------
1. Tacitus, Annals 15.44 (Nero, the fire of Rome, "Christus ... Pontius Pilatus").
   SCAN     Florence, Biblioteca Medicea Laurenziana, Plut. 68.2 (the "second
            Medicean", Beneventan script, 11th c.), the only independent
            manuscript of Annals 11-16. Teca Digitale (CONTENTdm IIIF,
            tecabml.contentdm.oclc.org, item plutei:1335097), folios 38r
            (image plutei:1334785) and 38v (image plutei:1334786).
   MAPPING  Folio 38r is the folio commonly cited for the passage (Wikimedia
            Commons description of the 38r photograph, "en:Cornelius Tacitus
            Annales 15:44"). Checked line by line on the image on 2026-11-12:
            15.44 begins at fol. 38r col. b line 9 ("Et hec q(ui)de(m) huma|nis
            consiliis p(ro)uidebant(ur)") and ends at fol. 38v col. a line 4
            ("absumeren|tur", followed by 15.45 "Interea conferendis pecuniis").
            Column b of 38r has 35 lines (counted on the image and by an ink
            projection); line numbers for each part are in SECTIONS below.
   LATIN    C. D. Fisher, Cornelii Taciti Annalium ab excessu divi Augusti libri
            (Oxford 1906), Perseus canonical-latinLit phi1351.phi005.perseus-lat2
            (CC BY-SA 4.0).
   ENGLISH  A. J. Church and W. J. Brodribb, Annals of Tacitus (London: Macmillan 1876; the
            1869 in the Perseus header is the date of their History of Tacitus, not the Annals;
            the Spectator reviewed the Annals as new on 11 March 1876),
            Perseus phi1351.phi005.perseus-eng2 (public domain; CC BY-SA 4.0
            digital text).
   The chapter is split at five sentence breaks; the Latin and the English are
   cut at the same sentences (asserted below), nothing is added or reworded.

2. Suetonius, Claudius 25.4 ("Iudaeos impulsore Chresto ...") and
3. Suetonius, Nero 16.2 ("afflicti suppliciis Christiani ...").
   SCAN     Wolfenbuettel, Herzog August Bibliothek, Cod. Guelf. 268 Gud. lat.
            (Suetonius, Vitae Caesarum, parchment, 173 fols, 11th c.; HAB
            Handschriftendatenbank), Wolfenbuetteler Digitale Bibliothek
            diglib.hab.de/mss/268-gud-lat (image files /max/00222.jpg = fol.
            109v, 00223 = 110r, 00245 = 121r; folio labels from the WDB
            facsimile.xml). HAB publishes its image files as public domain.
            The oldest Suetonius manuscript, Paris BnF lat. 6115 (Memmianus,
            9th c., Gallica ark:/12148/btv1b9066860v), was the first choice, but
            Gallica refused automated requests (HTTP 403, Cloudflare) on
            2026-11-12, so the Gudianus is used instead.
   MAPPING  Found and checked by reading the Caroline minuscule on the images
            (2026-11-12): Claudius 25.4 = fol. 109v lines 24-26 + fol. 110r
            lines 1-3; Nero 16.2 = fol. 121r lines 8-16. Line counts checked by
            ink projection (26 lines per page).
   LATIN    M. Ihm, De vita Caesarum libri VIII (Teubner 1908), Perseus
            phi1348.abo015 / abo016 perseus-lat2 (CC BY-SA 4.0); Ihm's section
            numbers.
   ENGLISH  J. C. Rolfe, Suetonius (Loeb Classical Library, 1914), vol. 2, via
            Bill Thayer's LacusCurtius transcription (public domain; Rolfe's
            section numbers match Ihm's).

4. Pliny the Younger, Letters 10.96-97: not built. No manuscript of book 10
   survives; the text depends on the printed editions of 1502 (Avantius) and
   1508 (Aldus), made from a lost Paris manuscript. A printed book is not a
   photograph of the original object (spec rule 5).

Usage:
    python3 scripts/import_roman_witnesses.py           # build (uses cached scans)
    python3 scripts/import_roman_witnesses.py --force   # re-download scans
"""

import argparse
import html
import io
import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "roman-witnesses"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"
TEI = "{http://www.tei-c.org/ns/1.0}"
LONG_SIDE = 2600

PERSEUS = "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/data"
SOURCES = {
    "tacitus-annals.perseus-lat2.xml": f"{PERSEUS}/phi1351/phi005/phi1351.phi005.perseus-lat2.xml",
    "tacitus-annals.perseus-eng2.xml": f"{PERSEUS}/phi1351/phi005/phi1351.phi005.perseus-eng2.xml",
    "suetonius-abo015.perseus-lat2.xml": f"{PERSEUS}/phi1348/abo015/phi1348.abo015.perseus-lat2.xml",
    "suetonius-abo016.perseus-lat2.xml": f"{PERSEUS}/phi1348/abo016/phi1348.abo016.perseus-lat2.xml",
    "lacuscurtius-rolfe-Claudius.html": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Claudius%2A.html",
    "lacuscurtius-rolfe-Nero.html": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Nero%2A.html",
}

BML_IIIF = "https://tecabml.contentdm.oclc.org/iiif/2/plutei:{id}/full/,{h}/0/default.jpg"
BML_ITEM = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/1335097"
BML_MANIFEST = "https://tecabml.contentdm.oclc.org/iiif/2/plutei:1335097/manifest.json"
HAB_IMG = "http://diglib.hab.de/mss/268-gud-lat/max/{n}.jpg"
HAB_START = "http://diglib.hab.de/mss/268-gud-lat/start.htm"
HAB_DESC = "http://diglib.hab.de/?db=mss&list=ms&id=268-gud-lat"
HAB_TERMS = "http://diglib.hab.de/nutzungshinweise.html"
COMMONS_38R = "https://commons.wikimedia.org/wiki/File:MII.png"

SCANS = {
    "laur-plut68-2-f38r.jpg": ("bml", "1334785"),
    "laur-plut68-2-f38v.jpg": ("bml", "1334786"),
    "gud-lat-268-f109v.jpg": ("hab", "00222"),
    "gud-lat-268-f110r.jpg": ("hab", "00223"),
    "gud-lat-268-f121r.jpg": ("hab", "00245"),
}


def fetch(url):
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"could not fetch {url}: {last}")


def get_sources():
    SRC.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        p = SRC / name
        if not p.exists() or p.stat().st_size < 1000:
            p.write_bytes(fetch(url))


def get_scans(force):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    for name, (kind, ident) in SCANS.items():
        p = SCAN_DIR / name
        if p.exists() and not force:
            continue
        if kind == "bml":
            img = Image.open(io.BytesIO(fetch(BML_IIIF.format(id=ident, h=LONG_SIDE)))).convert("RGB")
        else:
            img = Image.open(io.BytesIO(fetch(HAB_IMG.format(n=ident)))).convert("RGB")
            if max(img.size) > LONG_SIDE:
                s = LONG_SIDE / max(img.size)
                img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
        img.save(p, quality=86)
        print(f"  scan {name} {img.size} {p.stat().st_size} bytes")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def tei_div(path, *steps):
    """Return the TEI div reached by following (subtype, n) steps, e.g. ("book", "15"), ("chapter", "44")."""
    root = ET.parse(path).getroot()
    node = root.find(f".//{TEI}body")
    for subtype, n in steps:
        node = next(d for d in node.iter(f"{TEI}div") if d.get("subtype") == subtype and d.get("n") == n)
    return node


def tei_text(div):
    for note in div.iter(f"{TEI}note"):
        note.clear()
    return norm("".join(div.itertext()))


def split_at(text, markers):
    """Cut text before each marker (each must occur exactly once, in order)."""
    parts, rest = [], text
    for m in markers:
        assert rest.count(m) == 1, (m, rest[:80])
        a, b = rest.split(m, 1)
        parts.append(a.strip())
        rest = m + b
    parts.append(rest.strip())
    return parts


def rolfe(name, start, end):
    t = (SRC / name).read_text(encoding="utf-8")
    i = t.index(f'NAME="{start}"')
    j = t.index(f'NAME="{end}"', i)
    seg = t[t.index("</A>", i) + 4: t.rfind("<A", i, j)]
    seg = re.sub(r'<A CLASS="ref".*?</A>', "", seg, flags=re.S)
    seg = re.sub(r"<[^>]+>", "", seg)
    seg = html.unescape(seg).replace("⁠", "").replace("­", "").replace("\xa0", " ")
    return norm(seg)


# ---------------------------------------------------------------------------
# Tacitus, Annals 15.44
# ---------------------------------------------------------------------------
TAC_LAT_CUTS = ["sed non ope humana", "auctor nominis eius", "igitur primum correpti", "hortos suos ei spectaculo"]
TAC_ENG_CUTS = ["But all human efforts", "Christus, from whom", "Accordingly, an arrest", "Nero offered his gardens"]
TAC_PARTS = [
    {
        "sid": "15.44 (1)",
        "topic": "rites to appease the gods after the fire",
        "where": "fol. 38r, column b, lines 9-16",
        "pages": ["laur-plut68-2-f38r.jpg"],
        "note": "Checked on the image: fol. 38r, right-hand column (col. b), line 9 ends "
                "'Et hec q(ui)de(m) huma-' and line 10 begins 'nis consiliis p(ro)uidebant(ur)'; "
                "this part ends on line 16 with 'mariti erant'. Marginal glosses beside it name "
                "Vulcan, Ceres, Proserpina and Juno.",
    },
    {
        "sid": "15.44 (2)",
        "topic": "Nero blames the Christians",
        "where": "fol. 38r, column b, lines 16-21",
        "pages": ["laur-plut68-2-f38r.jpg"],
        "note": "Checked on the image: fol. 38r col. b line 16 'Sed n(on) ope humana', line 18 ends "
                "'Ergo', line 19 'abolendo rumori nero subdidit reos', line 21 'gus chri stianos "
                "appellabat', written with a gap after 'chri'. Scholars who have examined the manuscript "
                "since G. Andresen (1902) report that the i here is a correction of an original e "
                "('Chrestianos'). A later hand wrote 'Christiani' in the right margin.",
    },
    {
        "sid": "15.44 (3)",
        "topic": "Christus, Tiberius and Pontius Pilate",
        "where": "fol. 38r, column b, lines 21-27",
        "pages": ["laur-plut68-2-f38r.jpg"],
        "note": "Checked on the image: fol. 38r col. b line 21 ends 'auctor nominis ei(us)', line 22 "
                "'christus · Tyberio imperitante p(er) procuratore(m) pon-', line 23 'tiu(m) pilatu(m) "
                "supplicio adfectus erat', line 27 begins 'turq;' (end of 'celebranturque'). "
                "Marginal notes beside lines 21-23 name Tiberius and Pilate.",
    },
    {
        "sid": "15.44 (4)",
        "topic": "arrests and executions",
        "where": "fol. 38r, column b, lines 27-33",
        "pages": ["laur-plut68-2-f38r.jpg"],
        "note": "Checked on the image: fol. 38r col. b line 27 'Igit(ur) p(ri)mu(m) correpti q(ui) "
                "fatebant(ur)', line 29 ends 'coniuncti sunt' (the manuscript's reading where "
                "Fisher prints 'convicti'), line 33 begins 'in usu nocturni luminis urerentur'.",
    },
    {
        "sid": "15.44 (5)",
        "topic": "Nero's gardens; pity for the victims",
        "where": "fol. 38r, column b, lines 33-35, and fol. 38v, column a, lines 1-4",
        "pages": ["laur-plut68-2-f38r.jpg", "laur-plut68-2-f38v.jpg"],
        "note": "Checked on the images: this part straddles two pages. Fol. 38r col. b line 33 "
                "'Hortos suos', line 35 (last line) 'edebat habitu aurige p(er)mixtus plebi uel "
                "circulo'; it continues at the top of fol. 38v, left-hand column (col. a), line 1 "
                "'insistens · Unde quamquam aduersus sontes', and ends on line 4 'tur' (of "
                "'absumerentur'), followed by 15.45 'Interea conferendis pecuniis'.",
    },
]


def build_tacitus():
    lat = tei_text(tei_div(SRC / "tacitus-annals.perseus-lat2.xml", ("book", "15"), ("chapter", "44")))
    eng = tei_text(tei_div(SRC / "tacitus-annals.perseus-eng2.xml", ("book", "15"), ("chapter", "44")))
    lp = split_at(lat, TAC_LAT_CUTS)
    ep = split_at(eng, TAC_ENG_CUTS)
    assert lp[0].startswith("Et haec quidem") and lp[0].endswith("quibus mariti erant."), lp[0]
    assert lp[1].endswith("Christianos appellabat."), lp[1]
    assert lp[2].endswith("celebranturque."), lp[2]
    assert lp[3].endswith("urerentur."), lp[3]
    assert lp[4].endswith("absumerentur."), lp[4]
    assert ep[0].startswith("Such indeed") and ep[0].endswith("married women."), ep[0]
    assert ep[1].endswith("called Christians by the populace."), ep[1]
    assert ep[2].endswith("become popular."), ep[2]
    assert ep[3].endswith("when daylight had expired."), ep[3]
    assert ep[4].endswith("being destroyed."), ep[4]

    sections = []
    for part, la, en in zip(TAC_PARTS, lp, ep):
        sections.append({
            "section": part["sid"],
            "original_ref": f"Tacitus, Annals 15.44, {part['topic']}; Laur. Plut. 68.2, {part['where']}",
            "original_text": html.escape(la, quote=False),
            "text": html.escape(en, quote=False),
            "scan_pages": [f"{KEY}/{p}" for p in part["pages"]],
            "scan_note": part["note"] + " Latin shown is Fisher's 1906 critical text, not a transcription of this page; "
                         "the copyist's spelling and a few words differ.",
        })

    tid = PREFIX + "tacitus-annals-15-44"
    entry = {
        "id": tid, "slug": tid,
        "title": "Tacitus, Annals 15.44: Nero, the fire of Rome and the Christians",
        "language": "Latin (Fisher 1906) / English (Church and Brodribb 1876)",
        "source": "Florence, Biblioteca Medicea Laurenziana, Plut. 68.2, fol. 38r-38v (Teca Digitale IIIF) + "
                  "Fisher's Latin and Church and Brodribb's English (Perseus)",
        "description": "Tacitus' account of Nero blaming the Christians for the fire of Rome in 64 AD, with the "
                       "earliest Roman mention of Christ's execution under Pontius Pilate, shown on the 11th-century "
                       "manuscript that alone preserves this part of the Annals.",
        "introduction": (
            "<p>Cornelius Tacitus wrote the <em>Annals</em>, a history of Rome from the death of Augustus to the death "
            "of Nero, about 115-120 AD. In book 15, chapter 44, after describing the great fire of Rome in July 64 AD, "
            "he reports that Nero, unable to stop the rumor that he had ordered the fire, fixed the blame on the "
            "Christians and had many of them put to death. In the same passage Tacitus explains the name: "
            "\"Christus\" had been executed under Tiberius by the procurator Pontius Pilate. It is the earliest "
            "surviving statement by a Roman writer about the death of Jesus.</p>\n\n"
            "<p>Books 11-16 of the <em>Annals</em> survive in a single independent manuscript, the \"second Medicean\" "
            "(Florence, Biblioteca Medicea Laurenziana, Plut. 68.2), written in Beneventan script in the 11th century, "
            "probably at Monte Cassino; the later manuscripts of these books are generally held to descend from it. The passage fills the "
            "right-hand column of folio 38r from line 9 to the end (line 35) and the first four lines of the left-hand "
            "column of folio 38v.</p>\n\n"
            "<p>The chapter is shown in five parts, cut at sentence breaks; each part names the column and lines that "
            "carry it, checked on the photographs. On folio 38r, line 21, the word for the Christians is written "
            "\"chri stianos\", with a gap after \"chri\"; scholars who have examined the manuscript report that the i is "
            "a correction of an original e, so that the copyist first wrote \"Chrestianos\".</p>"
        ),
        "translator_notes": [
            "Latin is C. D. Fisher's critical text (Oxford, 1906), which prints 'Christianos'; it is an edition, not a "
            "transcription of the manuscript page. Where the manuscript differs (for example 'coniuncti' for 'convicti', "
            "'circulo' for 'curriculo'), the scan notes say so.",
            "English is the translation of A. J. Church and W. J. Brodribb (first published 1876), as digitized by the Perseus Project.",
            "The five parts are cut at the same sentences in the Latin and the English; nothing has been added or reworded.",
        ],
        "translation": sections,
        "verification": {
            "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (CONTENTdm IIIF): {BML_ITEM} ; manifest {BML_MANIFEST} ; "
                           "fol. 38r = image plutei:1334785, fol. 38v = image plutei:1334786",
            "scan_license": "Biblioteca Medicea Laurenziana (Ministero della Cultura), Teca Digitale, access marked 'Pubblico'. "
                            "Reproduced for non-commercial scholarly use with credit (Italian Codice dei beni culturali, art. 108, "
                            "comma 3-bis); commercial reuse requires the library's permission.",
            "scan_manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 68.2 ('second Medicean'), parchment, 191 fols, "
                               "270 x 340 mm, 11th c., Beneventan script; Tacitus, Annals 11-16 and Histories 1-5, with Apuleius",
            "scan_mapping": "Folio 38r is the folio cited for Annals 15.44 in the Wikimedia Commons description of the photograph of "
                            "that page; each part was then checked line by line on the Teca Digitale images (opening and closing "
                            "words and line numbers recorded in each scan_note; column b of fol. 38r has 35 lines).",
            "scan_mapping_urls": [COMMONS_38R, BML_ITEM],
            "scan_local_paths": [f"{KEY}/laur-plut68-2-f38r.jpg", f"{KEY}/laur-plut68-2-f38v.jpg"],
            "original_text_source": "C. D. Fisher, Cornelii Taciti Annalium ab excessu divi Augusti libri (Oxford: Clarendon Press, 1906), "
                                    "Perseus canonical-latinLit phi1351.phi005.perseus-lat2 (https://github.com/PerseusDL/canonical-latinLit)",
            "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
            "translation_source": "A. J. Church and W. J. Brodribb, The Annals of Tacitus, translated into English (London: Macmillan, 1876), Perseus "
                                  "phi1351.phi005.perseus-eng2 (from the 1942 Modern Library reprint; the Perseus header gives 1869, the date of their History of Tacitus)",
            "translation_license": "public domain (published 1876); Perseus digital text CC BY-SA 4.0",
            "translator": "A. J. Church and W. J. Brodribb (1876)",
            "verified_date": TODAY,
        },
    }
    return entry


# ---------------------------------------------------------------------------
# Suetonius, Claudius 25.4 and Nero 16.2
# ---------------------------------------------------------------------------
SUET_COMMON_VERIF = {
    "scan_source": f"Herzog August Bibliothek Wolfenbuettel, Wolfenbuetteler Digitale Bibliothek: {HAB_START}",
    "scan_license": f"Public domain: the Herzog August Bibliothek publishes its image files of its own holdings as public domain "
                    f"(usage notes, {HAB_TERMS}, which also state that the copyright line printed on older image files is no "
                    f"longer valid); credit: Herzog August Bibliothek Wolfenbuettel <{HAB_START}>",
    "scan_manuscript": "Wolfenbuettel, Herzog August Bibliothek, Cod. Guelf. 268 Gud. lat. (catalogue no. 4573): Suetonius, "
                       "Vitae Caesarum; parchment, 173 fols, 20 x 15.5 cm, 11th c. (HAB Handschriftendatenbank, after "
                       "Milchsack 1913, pp. 223-224)",
    "original_text_source": "M. Ihm, C. Suetoni Tranquilli De vita Caesarum libri VIII (Leipzig: Teubner, 1908), Perseus "
                            "canonical-latinLit phi1348 (https://github.com/PerseusDL/canonical-latinLit)",
    "original_text_license": "edition public domain; Perseus digital text CC BY-SA 4.0",
    "translation_license": "public domain (published 1914); LacusCurtius marks the page public domain",
    "translator": "J. C. Rolfe (1914)",
}

SUET_INTRO_MS = (
    "<p>The photograph is of a Suetonius manuscript of the 11th century now in Wolfenbuettel (Herzog August Bibliothek, "
    "Cod. Guelf. 268 Gud. lat.), written in Caroline minuscule, 26 lines to the page. The oldest manuscript of Suetonius, "
    "Paris, BnF lat. 6115 (the Memmianus, 9th century), is digitized on Gallica but could not be retrieved for this "
    "library; it may be added later.</p>"
)


def build_claudius():
    lat = tei_text(tei_div(SRC / "suetonius-abo015.perseus-lat2.xml", ("chapter", "25"), ("section", "4")))
    eng = rolfe("lacuscurtius-rolfe-Claudius.html", "25.4", "25.5")
    assert lat.startswith("Iudaeos impulsore Chresto") and lat.endswith("praedicantes."), lat
    assert eng.startswith("Since the Jews constantly") and eng.endswith("no whit inferior."), eng
    tid = PREFIX + "suetonius-claudius-25-4"
    sec = {
        "section": "Claud. 25.4",
        "original_ref": "Suetonius, Divus Claudius 25.4; Wolfenbuettel, Cod. Guelf. 268 Gud. lat., fol. 109v lines 24-26 and fol. 110r lines 1-3",
        "original_text": html.escape(lat, quote=False),
        "text": html.escape(eng, quote=False),
        "scan_pages": [f"{KEY}/gud-lat-268-f109v.jpg", f"{KEY}/gud-lat-268-f110r.jpg"],
        "scan_note": "Checked on the images: fol. 109v line 23 ends 'immunes p(rae)stitis-' (end of 25.3), line 24 "
                     "'sent · Iudeos impulsore chresto assidue tumultuantes roma', line 25 'expulit · Germanoru(m) legatis "
                     "in orchestra sedere permisit', line 26 'simplicitate eoru(m) & fiducia commotus q(uo)d in popularia'; "
                     "the sentence continues at the top of fol. 110r, line 1 'deducti cum animaduertissent parthos & "
                     "armenios se-', and 25.4 ends on line 3 'p(rae)dicantes', before 25.5 'Druidarum religionem'. "
                     "The page spells 'chresto', as Ihm prints. A later reader drew a mark and a cross in the left "
                     "margin beside lines 24-26. Latin shown is Ihm's critical text, not a transcription of this page.",
    }
    entry = {
        "id": tid, "slug": tid,
        "title": "Suetonius, Claudius 25.4: the Jews expelled from Rome 'at the instigation of Chrestus'",
        "language": "Latin (Ihm 1908) / English (Rolfe 1914)",
        "source": "Wolfenbuettel, HAB, Cod. Guelf. 268 Gud. lat., fol. 109v-110r (Wolfenbuetteler Digitale Bibliothek) + "
                  "Ihm's Latin (Perseus) + Rolfe's English (LacusCurtius)",
        "description": "Suetonius' one-sentence notice that Claudius expelled the Jews from Rome because they were "
                       "rioting 'at the instigation of Chrestus', shown on an 11th-century manuscript page.",
        "introduction": (
            "<p>Gaius Suetonius Tranquillus published his <em>Lives of the Caesars</em> about 121 AD. In the life of "
            "Claudius (emperor 41-54 AD), among a list of the emperor's measures concerning foreigners, he writes that "
            "Claudius expelled the Jews from Rome because they were constantly rioting \"impulsore Chresto\", at the "
            "instigation of Chrestus. Many historians connect this with the expulsion mentioned in Acts 18:2, where "
            "Paul meets Aquila and Priscilla in Corinth, \"lately come from Italy ... because that Claudius had "
            "commanded all Jews to depart from Rome\", and take \"Chrestus\" as a form of the name Christus. Others "
            "read it as the name of an otherwise unknown agitator. The sentence is shown here with the rest of "
            "section 25.4.</p>\n\n"
            "<p>The section begins on the last three lines of folio 109v and ends on the first three lines of folio "
            "110r; both pages are shown.</p>\n\n" + SUET_INTRO_MS
        ),
        "translator_notes": [
            "Latin is Maximilian Ihm's critical text (Teubner, 1908), not a transcription of the manuscript page; "
            "the manuscript also reads 'chresto'.",
            "English is J. C. Rolfe's Loeb translation (1914), made from his own Latin text, which agrees with Ihm here.",
        ],
        "translation": [sec],
        "verification": dict(SUET_COMMON_VERIF, **{
            "scan_mapping": "Located and checked by reading the manuscript (Caroline minuscule) on the images: Claudius 25.4 = "
                            "fol. 109v lines 24-26 and fol. 110r lines 1-3 (26 lines per page; opening and closing words "
                            "recorded in the scan_note). Folio numbers are those written on the leaves and used in the WDB "
                            "facsimile index (image 00222 = 109v, 00223 = 110r).",
            "scan_mapping_urls": [HAB_START, HAB_DESC, "http://diglib.hab.de/mss/268-gud-lat/facsimile.xml"],
            "scan_local_paths": [f"{KEY}/gud-lat-268-f109v.jpg", f"{KEY}/gud-lat-268-f110r.jpg"],
            "translation_source": "J. C. Rolfe, Suetonius, vol. 2 (Loeb Classical Library, 1914), Life of Claudius 25.4, "
                                  "LacusCurtius transcription: " + SOURCES["lacuscurtius-rolfe-Claudius.html"],
            "verified_date": TODAY,
        }),
    }
    return entry


def build_nero():
    lat = tei_text(tei_div(SRC / "suetonius-abo016.perseus-lat2.xml", ("chapter", "16"), ("section", "2")))
    eng = rolfe("lacuscurtius-rolfe-Nero.html", "16.2", "17")
    assert lat.startswith("Multa sub eo") and lat.endswith("simul relegatae;"), lat
    assert eng.startswith("During his reign") and eng.endswith("banished from the city."), eng
    assert "Christiani" in lat and "Christians" in eng
    tid = PREFIX + "suetonius-nero-16-2"
    sec = {
        "section": "Nero 16.2",
        "original_ref": "Suetonius, Nero 16.2; Wolfenbuettel, Cod. Guelf. 268 Gud. lat., fol. 121r lines 8-16",
        "original_text": html.escape(lat, quote=False),
        "text": html.escape(eng, quote=False),
        "scan_pages": [f"{KEY}/gud-lat-268-f121r.jpg"],
        "scan_note": "Checked on the image: fol. 121r line 7 ends 16.1 'fossa mare ueteri urbi inducere'; line 8 begins "
                     "16.2 with a red initial, 'Multa sub eo & animaduersa seuere · & coercita nec'; line 12 ends "
                     "'Afflicti suppliciis', line 13 'xpiani genus hominu(m) sup(er)stitionis noue · ac malefice' "
                     "(xpiani is the usual abbreviation of Christiani); line 16 'mimorum factiones cu(m) ipsis "
                     "relegate', followed by Nero 17 'Aduersus fal-'. A later hand wrote a note beginning 'nota q(uod)' "
                     "in the right margin beside lines 12-14. Latin shown is Ihm's critical text, not a transcription "
                     "of this page.",
    }
    entry = {
        "id": tid, "slug": tid,
        "title": "Suetonius, Nero 16.2: 'punishment was inflicted on the Christians'",
        "language": "Latin (Ihm 1908) / English (Rolfe 1914)",
        "source": "Wolfenbuettel, HAB, Cod. Guelf. 268 Gud. lat., fol. 121r (Wolfenbuetteler Digitale Bibliothek) + "
                  "Ihm's Latin (Perseus) + Rolfe's English (LacusCurtius)",
        "description": "Suetonius lists the punishment of the Christians, 'a class of men given to a new and mischievous "
                       "superstition', among Nero's measures, shown on an 11th-century manuscript page.",
        "introduction": (
            "<p>In the life of Nero (emperor 54-68 AD), Suetonius lists the emperor's measures of public order: limits on "
            "spending, rules for taverns, the banishment of the pantomime actors, and \"afflicti suppliciis Christiani, "
            "genus hominum superstitionis novae ac maleficae\", punishment inflicted on the Christians, a class of men "
            "given to a new and mischievous superstition. Unlike Tacitus (Annals 15.44), Suetonius does not connect "
            "the punishment with the fire of Rome. With Tacitus, it is one of the two earliest Roman references to "
            "Nero's action against the Christians.</p>\n\n"
            "<p>Section 16.2 fills lines 8-16 of folio 121r; the copyist wrote the name with the abbreviation "
            "\"xpiani\" (line 13).</p>\n\n" + SUET_INTRO_MS
        ),
        "translator_notes": [
            "Latin is Maximilian Ihm's critical text (Teubner, 1908), not a transcription of the manuscript page.",
            "English is J. C. Rolfe's Loeb translation (1914).",
        ],
        "translation": [sec],
        "verification": dict(SUET_COMMON_VERIF, **{
            "scan_mapping": "Located and checked by reading the manuscript on the image: Nero 16.2 = fol. 121r lines 8-16 "
                            "(opening and closing words recorded in the scan_note). Folio number as written on the leaf and "
                            "in the WDB facsimile index (image 00245 = 121r).",
            "scan_mapping_urls": [HAB_START, HAB_DESC, "http://diglib.hab.de/mss/268-gud-lat/facsimile.xml"],
            "scan_local_paths": [f"{KEY}/gud-lat-268-f121r.jpg"],
            "translation_source": "J. C. Rolfe, Suetonius, vol. 2 (Loeb Classical Library, 1914), Life of Nero 16.2, "
                                  "LacusCurtius transcription: " + SOURCES["lacuscurtius-rolfe-Nero.html"],
            "verified_date": TODAY,
        }),
    }
    return entry


def row(entry, order, author_id, date_approx, century, themes, captions):
    return {
        "id": entry["id"], "slug": entry["id"], "order": order,
        "title": entry["title"], "author_id": author_id, "language": "Latin",
        "era": "Imperial", "tradition": "roman", "category": "historical-witness",
        "date_approx": date_approx, "century": century,
        "source": entry["source"], "description": entry["description"],
        "themes": themes + ["verified"],
        "is_first_translation": False, "status": "published",
        "scans": {"pages": [{"file": f, "caption": c} for f, c in captions]},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    get_sources()
    get_scans(args.force)

    tac, cla, ner = build_tacitus(), build_claudius(), build_nero()
    for e in (tac, cla, ner):
        (PUB / f"{e['id']}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {e['id']} ({len(e['translation'])} sections)")

    coll = {
        "collection": {
            "key": KEY,
            "prefix": PREFIX,
            "label": "Roman witnesses to Christ and the Christians",
            "group": "Rome",
            "date_sort": 116,
            "author_name": "Tacitus and Suetonius (early 2nd c. AD; 11th-century manuscripts)",
            "source_url": BML_ITEM,
            "critical_edition": "Fisher 1906 (Tacitus) and Ihm 1908 (Suetonius), via Perseus",
            "translator_name": "Church and Brodribb (1876); J. C. Rolfe (1914)",
            "original_lang_label": "Latin · Fisher / Ihm",
            "original_lang_code": "la",
            "edition_label": "",
            "search_terms": "tacitus annals 15.44 suetonius claudius nero chrestus christiani christians pilate nero fire roman witnesses",
            "description": "What Roman historians of the early 2nd century wrote about Christ and the first Christians: "
                           "Tacitus on Nero's punishment of the Christians and the execution of Christus under Pontius Pilate "
                           "(Annals 15.44), and Suetonius on Claudius expelling the Jews over 'Chrestus' (Claudius 25.4) and on "
                           "Nero's punishment of the Christians (Nero 16.2), each shown on the 11th-century manuscript page "
                           "that carries it.",
        },
        "texts": [
            row(tac, 1, "tacitus", "c. 115-120 AD (composition); 11th c. (Laur. Plut. 68.2)", 2,
                ["tacitus", "annals", "nero", "fire-of-rome", "christians", "pontius-pilate", "historical-jesus", "latin"],
                [(f"{KEY}/laur-plut68-2-f38r.jpg", "Laur. Plut. 68.2, fol. 38r"),
                 (f"{KEY}/laur-plut68-2-f38v.jpg", "Laur. Plut. 68.2, fol. 38v")]),
            row(cla, 2, "suetonius", "c. 121 AD (composition); 11th c. (Cod. Guelf. 268 Gud. lat.)", 2,
                ["suetonius", "claudius", "chrestus", "jews", "rome", "acts-18", "historical-jesus", "latin"],
                [(f"{KEY}/gud-lat-268-f109v.jpg", "Cod. Guelf. 268 Gud. lat., fol. 109v"),
                 (f"{KEY}/gud-lat-268-f110r.jpg", "Cod. Guelf. 268 Gud. lat., fol. 110r")]),
            row(ner, 3, "suetonius", "c. 121 AD (composition); 11th c. (Cod. Guelf. 268 Gud. lat.)", 2,
                ["suetonius", "nero", "christians", "persecution", "latin"],
                [(f"{KEY}/gud-lat-268-f121r.jpg", "Cod. Guelf. 268 Gud. lat., fol. 121r")]),
        ],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
