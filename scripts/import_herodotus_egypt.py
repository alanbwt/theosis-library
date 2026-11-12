#!/usr/bin/env python3
"""
import_herodotus_egypt.py - Herodotus, Histories 2.99-2.146: the kings of Egypt from Min to Sethos
as the priests of Memphis told them, and the priests' chronology of 341 generations (11,340 years)
in which the sun twice rose where it now sets. Each chapter is linked to the page(s) of the oldest
manuscript of Herodotus that carry it.

Eleven entries (groups of chapters by king or theme), 54 sections (one per chapter; Godley's
subdivisions 121a-f of the Rhampsinitus story are kept as separate sections).

Chain of evidence:
  1. SCAN     Florence, Biblioteca Medicea Laurenziana, Plut. 70.3 (codex A of Herodotus, 10th c.,
              374 fols.), fols. 78v-92v. Teca Digitale IIIF (manifest
              https://tecabml.contentdm.oclc.org/iiif/info/plutei/1358114/manifest.json, cached in
              data/sources/herodotus-egypt/), access "Pubblico". Chosen as the oldest witness, in colour.
  2. MAPPING  By eye on the downloaded images: the first and last words of every page from fol. 78v
              to 92v were read and located in the Greek (PAGE_STARTS / PAGE_NOTES below); the start of
              2.99 (fol. 78v line 24), 2.146 (fol. 92v line 11) and 2.147 (fol. 92v line 27) were also
              read. Each chapter's page(s) are computed from those page breaks, never from text length;
              a chapter that runs across a page break lists every page it touches.
  3. GREEK    Perseus canonical-greekLit tlg0016.tlg001.perseus-grc2: the Greek text printed in
              A. D. Godley's Loeb edition (vol. 1, 1920), CC BY-SA 4.0.
              Spot-checked against the printed page (archive.org historiesvolumei00hero_249, leaf n411,
              2.99.2-4). Editorial deletions (<del>) are shown in square brackets; Perseus note
              markers and Homer citation tags are omitted.
  4. ENGLISH  A. D. Godley, Herodotus vol. 1 (Loeb, 1920), public domain. The Perseus English
              (perseus-eng2) is a modernized revision, so the verbatim 1920 wording is taken from the
              Wikisource transcription "Herodotus The Persian Wars (Godley)/Book II", checked word by
              word against the OCR of the 1920 printing (archive.org historiesvolumei00hero_249). Every
              disagreement was an OCR fault except two Wikisource typos fixed in EN_FIXES.

Usage:
    python3 scripts/import_herodotus_egypt.py           # build
    python3 scripts/import_herodotus_egypt.py --force   # re-download scans
"""

import argparse
import io
import json
import re
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "herodotus-egypt"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
TEI = "{http://www.tei-c.org/ns/1.0}"

RECORD = "https://tecabml.contentdm.oclc.org/digital/collection/plutei/id/1358114"
PERSEUS_GRC = "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0016/tlg001/tlg0016.tlg001.perseus-grc2.xml"
WIKISOURCE = "https://en.wikisource.org/wiki/Herodotus_The_Persian_Wars_(Godley)/Book_II"
GODLEY_SCAN = "https://archive.org/details/historiesvolumei00hero_249"

FOLIOS = ["78v", "79r", "79v", "80r", "80v", "81r", "81v", "82r", "82v", "83r", "83v", "84r", "84v",
          "85r", "85v", "86r", "86v", "87r", "87v", "88r", "88v", "89r", "89v", "90r", "90v", "91r",
          "91v", "92r", "92v"]

# first words of each page, as read on the image (accent-free, for locating in the Greek)
# (section where the page starts, words). 78v starts before 2.99 (in 2.96).
PAGE_STARTS = {
    "78v": None,
    "79r": ("99.2", "τον προσ μεσαμβριησ αγκωνα"), "79v": ("101.1", "βασιλεων ου γαρ ελεγον"),
    "80r": ("103.2", "και επειτε εγινετο επι φασι"), "80v": ("106.1", "αι δε στηλαι"),
    "81r": ("108.1", "εσ την αιγυπτον και τισαμενοσ"), "81v": ("110.1", "τουσ δε παιδασ"),
    "82r": ("111.4", "ανεθηκε και του γε"), "82v": ("113.3", "κατηγορεον δε ταυτα"),
    "83r": ("115.5", "και ουδε ταυτα τοι μουνα"), "83v": ("116.6", "οι δε φοινικεσ"),
    "84r": ("119.2", "τυχων μεντοι τουτων"), "84v": ("120.4", "και τοισι αλλοισι πασι τρωσι"),
    "85r": ("121A.2", "δουναι τα μετρα αυτου"), "85v": ("121C.1", "η κατοικτισαμενον"),
    "86r": ("121D.6", "φυλακων επι λυμη"), "86v": ("121F.2", "επισταμενω ανθρωπων"),
    "87r": ("124.1", "κοτητα ελασαι"), "87v": ("125.4", "μηχαναι ησαν"),
    "88r": ("127.2", "εσ την ετερην ρεουσα"), "88v": ("130.1", "παντοια καταγιζουσι"),
    "89r": ("133.2", "αντιμεμφομενον"), "89v": ("134.4", "ποινην τησ αισωπου"),
    "90r": ("136.1", "οψιν οικοδομηματων"), "90v": ("137.4", "στριοσ βασιλεοσ"),
    "91r": ("139.2", "κακον τι προσ θεων"), "91v": ("141.3", "ωσ ουδεν πεισεται αχαρι"),
    "92r": ("142.4", "ουτε τα αμφι νουσουσ"), "92v": ("145.2", "δη οσα αυτοι αιγυπτιοι"),
}
PAGE_NOTES = {
    "78v": "fol. 78v: 2.99 begins in line 24 'μέχρι μὲν τούτου ὄψις τε ἐμή' (after '...Αἰγύπτιον τὸ οὔνομα'); the page ends '...ὅσον τε ἑκατὸν σταδίους ἀπὸ Μέμφιος' (2.99.2)",
    "79r": "fol. 79r begins 'τὸν πρὸς μεσαμβρίης ἀγκῶνα προσχώσαντα' (2.99.2) and ends 'τῶν δὲ ἄλλων' (2.101.1)",
    "79v": "fol. 79v begins 'βασιλέων· οὐ γὰρ ἔλεγον οὐδεμίαν ἔργων ἀπόδεξιν' (2.101.1), margin 'περὶ Μοίριδος', and ends '...ἐνθεῦτεν δὲ ἐπιστρέψας ὀπίσω ἤιε' (2.103.2)",
    "80r": "fol. 80r begins '...ἐγένετο ἐπὶ Φάσι ποταμῷ' (2.103.2) and ends with the last words of 2.105 'καλέεται Αἰγύπτιον' (a reader's note stands in the lower margin)",
    "80v": "fol. 80v begins with 2.106 'αἱ δὲ στῆλαι τὰς ἵστη κατὰ τὰς χώρας' and ends '...ἀποσωθῆναι ἅμα τῷ πατρί. νοστήσας δὲ ὁ Σέσωστρις' (2.107.2-2.108.1)",
    "81r": "fol. 81r begins 'ἐς τὴν Αἴγυπτον καὶ τισάμενος τὸν ἀδελφεόν' (2.108.1) and ends '...ἑωυτόν τε καὶ τὴν γυναῖκα' (2.110.1)",
    "81v": "fol. 81v begins 'τοὺς δὲ παῖδας ἐόντας τέσσερας' (2.110.1) and ends '...ἄλλα τε ἀνὰ τὰ ἱρὰ πάντα τὰ λόγιμα' (2.111.4)",
    "82r": "fol. 82r begins 'ἀνέθηκε καὶ τοῦ γε λόγον μάλιστα ἄξιόν ἐστι ἔχειν' (2.111.4) and ends '...τὴν Ἑλένην τε καὶ τὴν ἐς Μενέλεων ἀδικίην' (2.113.2)",
    "82v": "fol. 82v begins 'κατηγόρεον δὲ ταῦτα πρός τε τοὺς ἱρέας' (2.113.3) and ends '...ἀλλ’ ἀναπτερώσας αὐτὴν οἴχεαι ἔχων ἐκκλέψας' (2.115.4)",
    "83r": "fol. 83r begins 'καὶ οὐδὲ ταῦτά τοι μοῦνα' (2.115.5) and ends '...ὁμουρέει γὰρ ἡ Συρίη Αἰγύπτῳ' (2.116.6)",
    "83v": "fol. 83v begins 'οἱ δὲ Φοίνικες, τῶν ἡ Σιδών, ἐν τῇ Συρίῃ οἰκέουσι' (2.116.6) and ends '...πρὸς δὲ καὶ τὰ ἑωυτοῦ χρήματα πάντα' (2.119.1)",
    "84r": "fol. 84r begins 'τυχὼν μέντοι τούτων ἐγένετο Μενέλεως ἀνὴρ ἄδικος' (2.119.2) and ends '...συμβαινόντων ἰδίῃ τε αὐτῷ' (2.120.4)",
    "84v": "fol. 84v begins 'καὶ τοῖσι ἄλλοισι πᾶσι Τρωσί' (2.120.4) and ends '...τὰ περὶ τὴν ἐξαίρεσιν τοῦ λίθου' (2.121a.2)",
    "85r": "fol. 85r begins 'δοῦναι τὰ μέτρα αὐτοῦ' (2.121a.2) and ends '...τὸν ἂν ἴδωνται ἀποκλαύ-' (2.121c.1)",
    "85v": "fol. 85v begins '-σαντα ἢ κατοικτισάμενον, συλλαβόντας ἄγειν' (2.121c.1) and ends '...τό τε σῶμα τοῦ ἀδελφεοῦ καταλῦσαι καὶ τῶν' (2.121d.6)",
    "86r": "fol. 86r begins 'φυλάκων ἐπὶ λύμῃ πάντων ξυρῆσαι τὰς δεξιὰς παρηίδας' (2.121d.6) and ends '...συνοικίσαι ὡς πλεῖστα' (2.121f.2)",
    "86v": "fol. 86v begins 'ἐπισταμένῳ ἀνθρώπων' (2.121f.2) and ends '...βασιλεύσαντά σφεων Χέοπα ἐς πᾶσαν κα-' (2.124.1; a reader's note on Cheops stands in the lower margin)",
    "87r": "fol. 87r begins '-κότητα ἐλάσαι· κατακληίσαντα γάρ μιν πάντα τὰ ἱρά' (2.124.1) and ends '...τοσαῦται καί' (2.125.4)",
    "87v": "fol. 87v begins 'μηχαναὶ ἦσαν' (2.125.4), margin 'περὶ Χεφρῆνος', and ends '...οὔτε ἐκ τοῦ Νείλου διῶρυξ ἥκει ἐς αὐτὴν ὥσπερ' (2.127.2)",
    "88r": "fol. 88r begins 'ἐς τὴν ἑτέρην ῥέουσα' (2.127.2) and ends '...θυμιήματα δὲ παρ’ αὐτῇ' (2.130.1)",
    "88v": "fol. 88v begins 'παντοῖα καταγίζουσι ἀνὰ πᾶσαν ἡμέρην' (2.130.1) and ends '...πέμψαι ἐς τὸ μαντήιον τῷ θεῷ ὀνείδισμα' (2.133.2; a reader's note on the oracle stands in the lower margin)",
    "89r": "fol. 89r begins 'ἀντιμεμφόμενον, ὅτι ὁ μὲν αὐτοῦ πατὴρ' (2.133.2) and ends '...κηρυσσόντων Δελφῶν ἐκ θεοπροπίου ὃς βούλοιτο' (2.134.4)",
    "89v": "fol. 89v begins 'ποινὴν τῆς Αἰσώπου ψυχῆς ἀνελέσθαι' (2.134.4) and ends '...τύπους τε ἐγγεγλυμμένους καὶ ἄλλην' (2.136.1; a note on Asychis stands in the lower margin)",
    "90r": "fol. 90r begins 'ὄψιν οἰκοδομημάτων μυρίην' (2.136.1) and ends '...ὑπὸ τῶν τὰς διώρυχας ὀρυξάντων ἐπὶ Σεσώ-' (2.137.4; a note on Anysis stands in the lower margin)",
    "90v": "fol. 90v begins '-στριος βασιλέος, δεύτερα δὲ ἐπὶ τοῦ Αἰθίοπος' (2.137.4) and ends '...ἵνα ἀσεβήσας περὶ τὰ ἱρά' (2.139.2)",
    "91r": "fol. 91r begins 'κακόν τι πρὸς θεῶν ἢ πρὸς ἀνθρώπων λάβοι' (2.139.2) and ends '...ἐπιστάντα τὸν θεὸν θαρσύνειν' (2.141.3)",
    "91v": "fol. 91v begins 'ὡς οὐδὲν πείσεται ἄχαρι' (2.141.3) and ends '...οὔτε τὰ ἐκ τοῦ ποταμοῦ σφι γινόμενα' (2.142.4); the margin notes the sun rising twice where it now sets",
    "92r": "fol. 92r begins 'οὔτε τὰ ἀμφὶ νούσους οὔτε τὰ κατὰ τοὺς θανάτους' (2.142.4) and ends 'Ἡρακλέι μέν' (2.145.2; a note on Heracles, Pan and Dionysus stands in the lower margin)",
    "92v": "fol. 92v begins 'δὴ ὅσα αὐτοὶ Αἰγύπτιοί φασι εἶναι ἔτεα' (2.145.2); 2.146 begins in line 11 'τούτων ὦν ἀμφοτέρων' and ends in line 27 '...γενεηλογέουσι αὐτῶν τὴν γένεσιν', where 2.147 'ταῦτα μέν νυν αὐτοὶ Αἰγύπτιοι λέγουσι' begins",
}

# English: start of Godley's subdivisions of chapter 121
EN_121 = [("121A", "This king (they told me) had great wealth"), ("121B", "When the king opened the building"),
          ("121C", "When it was morning the king came"), ("121D", "So when she bitterly reproached him"),
          ("121E", "When the king was told of the stealing"), ("121F", "When this also came to the king")]
EN_FIXES = [("Sal ting-places", "Salting-places"), ("called Any sis,", "called Anysis,")]  # 1920 printing

ENTRIES = [
    ("min-and-the-330-kings", "99", "101", "Min, Nitocris and the 330 kings",
     "Herodotus begins the Egyptian priests' history of their kings: Min, the first king, who dammed the Nile and founded Memphis; the 330 kings after him read out from a papyrus roll, among them the queen Nitocris; and Moeris, who built the lake."),
    ("sesostris", "102", "110", "Sesostris, the conqueror king",
     "The campaigns of Sesostris by sea and land through Asia and into Europe, the pillars he set up, the Colchians as Egyptian settlers, the plot of his brother at Daphnae, the canals dug by his captives, and his statues at the temple of Hephaestus."),
    ("pheros", "111", "111", "Pheros, the blind king",
     "Pheros, son of Sesostris, who threw a spear into the flooding Nile, was struck blind for ten years, and recovered his sight as the oracle of Buto foretold."),
    ("proteus-and-helen", "112", "120", "Proteus, and Helen in Egypt",
     "The priests' account of Proteus of Memphis, who detained Helen and the stolen treasure when Paris was driven to Egypt, of Menelaus' visit, and Herodotus' argument that Homer knew this version and that Helen was never at Troy."),
    ("rhampsinitus", "121", "123", "Rhampsinitus, the treasure-thief, and the descent to the underworld",
     "Rhampsinitus and the tale of the builder's sons who robbed his treasury, his journey alive to the underworld where he played dice with Demeter, and the Egyptian teaching on the immortality and migration of the soul."),
    ("cheops-and-chephren", "124", "128", "Cheops and Chephren, the builders of the pyramids",
     "Cheops, who closed the temples and set all Egyptians to building the Great Pyramid, its construction by stages and its cost in radishes, onions and garlic, and his brother Chephren's pyramid; 106 years of oppression."),
    ("mycerinus", "129", "135", "Mycerinus, the oracle of six years, and Rhodopis",
     "Mycerinus, who reopened the temples and judged justly, his daughter buried in a golden cow at Sais, the oracle that gave him six more years, his pyramid, and the story of the courtesan Rhodopis."),
    ("asychis", "136", "136", "Asychis and the brick pyramid",
     "Asychis, who built the eastern gateway of the temple of Hephaestus, made a law of loans on the security of a father's mummy, and built a pyramid of brick."),
    ("anysis-and-sabacos", "137", "140", "Anysis the blind and Sabacos the Ethiopian",
     "The blind king Anysis, the fifty-year rule of the Ethiopian Sabacos who raised the cities on mounds, his dream and withdrawal, and Anysis' return from the marshes."),
    ("sethos", "141", "141", "Sethos and the army of Sennacherib",
     "Sethos, priest of Hephaestus, whose army of shopkeepers and craftsmen faced Sennacherib at Pelusium, where mice gnawed the enemy's quivers, bowstrings and shield-straps in the night."),
    ("the-priests-chronology", "142", "146", "The priests' chronology: 341 generations and 11,340 years",
     "The priests' reckoning from the first king to Sethos: 341 generations of kings and high priests, 11,340 years without a god in human form, in which the sun four times rose out of its usual place; the 345 wooden statues shown to Hecataeus at Thebes; and the ages of Heracles, Dionysus and Pan."),
]


def strip(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^α-ω ]", "", s.lower().replace("ς", "σ").replace("ϊ", "ι"))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0 (non-commercial research)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def canvases():
    m = json.loads((SRC / "laur-plut70.3-manifest.json").read_text(encoding="utf-8"))
    return {c["label"].replace("Carta: ", ""): c["images"][0]["resource"]["service"]["@id"]
            for c in m["sequences"][0]["canvases"]}


def scan(folio, force, svc):
    path = SCAN_DIR / f"laur-plut-70-3-f{folio.zfill(4)}.jpg"
    if path.exists() and not force:
        return path
    Image.open(io.BytesIO(fetch(f"{svc[folio]}/full/1800,/0/default.jpg"))).convert("RGB").save(path, quality=85)
    return path


def chapter_key(n):
    return (int(re.match(r"\d+", n).group()), n)


def tei_text(el):
    """Text of el without <note>, <bibl>; <del> in square brackets; verse lines on new lines."""
    out = []

    def walk(e):
        tag = e.tag.replace(TEI, "")
        if tag in ("note", "bibl"):
            out.append(e.tail or "")
            return
        if tag == "del":
            out.append("[")
        if tag == "l":
            out.append("¶")
        out.append(e.text or "")
        for c in e:
            walk(c)
        if tag == "del":
            out.append("]")
        if tag == "quote":
            out.append("¶")
        if e is not el:
            out.append(e.tail or "")

    walk(el)
    return "".join(out)


def greek():
    root = ET.parse(SRC / "tlg0016.tlg001.perseus-grc2.xml").getroot()
    chapters = {}
    for b in root.iter(f"{TEI}div"):
        if b.get("subtype") == "book" and b.get("n") == "2":
            for c in b.iter(f"{TEI}div"):
                if c.get("subtype") == "chapter" and 99 <= chapter_key(c.get("n"))[0] <= 146:
                    secs = []
                    for s in c.iter(f"{TEI}div"):
                        if s.get("subtype") == "section":
                            t = re.sub(r"\s+", " ", tei_text(s))
                            t = re.sub(r" ,(?=\S)", ", ", t)  # note marker left a stray space before a comma (2.143.4)
                            t = "\n".join(x.strip() for x in t.split("¶") if x.strip())
                            secs.append((s.get("n"), t))
                    chapters[c.get("n")] = secs
    assert len(chapters) == 54, len(chapters)
    for k, secs in chapters.items():
        for n, t in secs:
            assert not re.search(r"[A-Za-z0-9]", t), (k, n, t[:80])
    return chapters


def english():
    w = json.loads((SRC / "wikisource_godley_book2.json").read_text(encoding="utf-8"))["parse"]["wikitext"]
    seg = w[w.index("\n99. "):w.index("\n147. ")]
    for a, b in EN_FIXES:
        assert seg.count(a) == 1, a
        seg = seg.replace(a, b)
    parts = re.split(r"\n(\d{2,3})\. ", seg)
    e = {}
    for n, t in zip(parts[1::2], parts[2::2]):
        paras = [re.sub(r"\s+", " ", p).strip() for p in t.strip().split("\n\n") if p.strip()]
        e[n] = "<br>".join(paras)
    assert list(e) == [str(n) for n in range(99, 147)], list(e)
    t = e.pop("121")
    marks = [t.index(m) for _, m in EN_121]
    assert marks == sorted(marks)
    cuts = [0] + marks + [len(t)]
    labels = ["121"] + [k for k, _ in EN_121]
    for lab, a, b in zip(labels, cuts, cuts[1:]):
        e[lab] = t[a:b].strip().removeprefix("<br>").removesuffix("<br>").strip()
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    g, e = greek(), english()
    order = sorted(g, key=chapter_key)
    assert set(order) == set(e), set(order) ^ set(e)

    # linear positions over the accent-free Greek, to place the page breaks
    pos, cur, sec_start = {}, 0, {}
    for ch in order:
        pos[ch] = cur
        for n, t in g[ch]:
            sec_start[f"{ch}.{n}"] = cur
            cur += len(strip(t)) + 1
    end_all = cur
    stripped = {f"{ch}.{n}": strip(t) for ch in order for n, t in g[ch]}
    page_pos = {}
    for f in FOLIOS:
        ps = PAGE_STARTS[f]
        if ps is None:
            page_pos[f] = -1
            continue
        sec, words = ps
        off = stripped[sec].find(words)
        assert off >= 0, (f, sec, words)
        page_pos[f] = sec_start[sec] + off
    assert [page_pos[f] for f in FOLIOS] == sorted(page_pos[f] for f in FOLIOS)
    bounds = [(f, page_pos[f], page_pos[FOLIOS[i + 1]] if i + 1 < len(FOLIOS) else end_all) for i, f in enumerate(FOLIOS)]
    ch_end = {ch: (pos[order[i + 1]] if i + 1 < len(order) else end_all) for i, ch in enumerate(order)}
    pages = {ch: [f for f, a, b in bounds if a < ch_end[ch] and b > pos[ch]] for ch in order}

    svc = canvases()
    paths = {f: scan(f, args.force, svc) for f in FOLIOS}
    rel = {f: f"{KEY}/{p.name}" for f, p in paths.items()}

    def label(ch):
        return f"2.{ch[:-1]}{ch[-1].lower()}" if ch[-1].isalpha() else f"2.{ch}"

    intro_common = (
        "<p>In the second book of his <em>Histories</em> (written c. 430 BCE) Herodotus reports what the priests of Hephaestus at Memphis told him of the kings of Egypt, "
        "from Min (Menes), who first ruled and founded Memphis, through 330 kings named from a papyrus roll, to Sesostris, Proteus, Rhampsinitus, the pyramid builders Cheops, Chephren and Mycerinus, "
        "and Sethos, priest-king in the time of Sennacherib. He ends with their chronology: 341 generations, 11,340 years, during which no god had reigned in human form and the sun had four times risen out of its usual place.</p>\n\n"
        "<p>The manuscript is Florence, Biblioteca Medicea Laurenziana, Plut. 70.3, written in the 10th century, the oldest surviving manuscript of Herodotus (codex A of the editors). "
        "Chapters 2.99-146 run from fol. 78v to fol. 92v. Each section is one chapter (Godley's subdivisions of the Rhampsinitus story, 121a-f, are kept apart) and points at the page(s) that carry it; the page breaks were read on the images and are recorded in each note.</p>"
    )
    notes = [
        "Greek: the text printed in A. D. Godley's Loeb edition (1920), from Perseus. Square brackets mark words the editor considers later additions. The manuscript's wording differs from the edition in places; the Greek is the edition, not a transcription of the page.",
        "English: A. D. Godley's translation as printed in 1920 (Loeb Classical Library, Herodotus vol. 1), not the modernized version on Perseus. Godley's footnotes are omitted.",
        "Chapter 121 is divided into 121 and 121a-121f as in Godley's edition; the English is divided at the corresponding sentences.",
    ]
    rows = []
    for order_n, (slug, a, b, title, desc) in enumerate(ENTRIES, 1):
        chs = order[order.index(a):order.index(b) + 1]
        fols = [f for f in FOLIOS if any(f in pages[c] for c in chs)]
        secs = []
        for ch in chs:
            fp = pages[ch]
            lead = (f"{label(ch)} is on fol. {fp[0]}." if len(fp) == 1
                    else f"{label(ch)} runs from fol. {fp[0]} to fol. {fp[-1]}.")
            secs.append({
                "section": label(ch),
                "original_ref": f"Herodotus, Histories {label(ch)}; Laur. Plut. 70.3 fol. {', '.join(fp)}",
                "original_text": f"<sup>{label(ch)}</sup>" + "<br>".join(t.replace("\n", "<br>") for _, t in g[ch]),
                "text": f"<sup>{label(ch)}</sup>{e[ch]}",
                "scan_pages": [rel[f] for f in fp],
                "scan_note": lead + " Page breaks read on the images: " + "; ".join(PAGE_NOTES[f] for f in fp)
                             + ". Checked on the image. Viewer: " + RECORD,
            })
        tid = PREFIX + slug
        full_title = f"Herodotus, Histories {label(a)}" + (f"-{b}" if b != a else "") + f": {title}"
        entry = {
            "id": tid, "slug": tid, "title": full_title,
            "language": "Greek (Godley 1920) / English (Godley 1920)",
            "source": "Florence, Laur. Plut. 70.3 (10th c.) via BML Teca Digitale + Greek of Godley's Loeb (Perseus) + English of A. D. Godley (1920, Wikisource, checked against the printing)",
            "description": desc,
            "introduction": intro_common + f"\n\n<p>This entry covers {label(a)}" + (f" to 2.{b}" if b != a else "") + f", on fol. {fols[0]}" + (f" to {fols[-1]}" if len(fols) > 1 else "") + ".</p>",
            "translator_notes": notes,
            "translation": secs,
            "verification": {
                "scan_source": f"Biblioteca Medicea Laurenziana, Teca Digitale (IIIF cdm21059.contentdm.oclc.org), Plut. 70.3, fols. {fols[0]}-{fols[-1]}; record {RECORD}",
                "scan_license": "Teca Digitale access 'Pubblico'; reproduced for non-commercial study with credit 'Biblioteca Medicea Laurenziana, Plut. 70.3, su concessione del MiC'",
                "scan_manuscript": "Florence, Biblioteca Medicea Laurenziana, Plut. 70.3 (10th c., parchment, 374 fols.), Herodotus, Histories (codex A)",
                "scan_mapping": "Checked on the images: the first and last words of every page from fol. 78v to 92v were read and located in the Greek; each chapter's page(s) follow from those page breaks (see scan_note)",
                "scan_mapping_urls": [RECORD] + [f"{svc[f]}/full/1800,/0/default.jpg" for f in fols],
                "scan_local_paths": [rel[f] for f in fols],
                "original_text_source": f"Herodotus, ed. and tr. A. D. Godley, vol. 1 (Loeb, 1920), Greek text via Perseus canonical-greekLit tlg0016.tlg001.perseus-grc2 ({PERSEUS_GRC})",
                "original_text_license": "edition public domain (1920); Perseus digital text CC BY-SA 4.0",
                "translation_source": f"A. D. Godley, Herodotus vol. 1 (London: Heinemann; New York: Putnam, 1920), Book II; transcription {WIKISOURCE} checked against {GODLEY_SCAN}",
                "translation_license": "public domain (published 1920)",
                "translator": "A. D. Godley (1920)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": order_n, "title": full_title, "author_id": "herodotus",
            "language": "Greek", "era": "Classical", "tradition": "greek", "category": "history",
            "date_approx": "c. 430 BCE (Herodotus); 10th c. (Laur. Plut. 70.3)", "century": -5,
            "source": entry["source"], "description": desc,
            "themes": ["herodotus", "egypt", "pharaohs", "egyptian-chronology", "pyramids", "greek", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": rel[f], "caption": f"Laur. Plut. 70.3, fol. {f}"} for f in fols]},
        })
        print(f"  {tid}: {len(secs)} sections, fols {fols[0]}-{fols[-1]}")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Herodotus on the kings of Egypt",
            "group": "Egypt", "date_sort": -430,
            "author_name": "Herodotus (c. 430 BCE), Histories book 2",
            "source_url": RECORD,
            "critical_edition": "Greek of A. D. Godley's Loeb edition (1920), via Perseus",
            "translator_name": "A. D. Godley (1920)",
            "original_lang_label": "Greek · Godley (Loeb 1920)",
            "original_lang_code": "grc", "edition_label": "",
            "search_terms": "herodotus histories book 2 egypt kings min menes sesostris proteus helen rhampsinitus cheops chephren mycerinus pyramids sethos 341 generations 11340 years sun rose west",
            "description": "Herodotus' account of the kings of Egypt from Min to Sethos, as the priests of Memphis told it, and their chronology of 341 generations and 11,340 years, on the pages of the oldest manuscript of the Histories (Florence, Laur. Plut. 70.3, 10th c.).",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
