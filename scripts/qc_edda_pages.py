#!/usr/bin/env python3
"""
qc_edda_pages.py - QC rebuild of the Poetic Edda entries (verified-edda-*).

Why: the original import (scripts/import_edda.py) pointed the poems at the
wrong leaves (e.g. Alvissmal at fol. 23r-24r, which carry heroic poems) and
spread the stanzas evenly over the pages. It also paired Thorpe's English with
the Old Norse by stanza number, but Thorpe printed several poems in a different
stanza order (Voluspa, Volundarkvida) or split stanzas differently (Havamal,
Hymiskvida, Thrymskvida, Alvissmal), so many English stanzas sat beside the
wrong Old Norse stanza, and Gutenberg typos (Vafthrudnismal "33" twice,
Harbardsljod "36"/"39") dropped stanzas.

Chain of evidence
-----------------
1. Page of every stanza: Ludv. F. A. Wimmer and Finnur Jonsson, "Haandskriftet
   Nr 2365 4to gl. kgl. samling ... (Codex regius af den aeldre Edda) i
   fototypisk og diplomatisk gengivelse", Kobenhavn 1891 (archive.org item
   handskriftetnr2300kben). Each diplomatic page reproduces one manuscript page
   (pages numbered 1-90, page P = fol. ceil(P/2) recto/verso) and ends with a
   caption naming the stanzas on it in Bugge's numbering. Bugge's numbers do
   not always equal the numbers of the text used here, so every page break was
   matched by the words of the text (OCR of the diplomatic page, cached in
   data/sources/qc-legacy/edda/wj1891_dipl_pages.json), not by number.
2. Images: handrit.is page images of GKS 2365 4to, cached in
   site/assets/scans/codex-regius/codex-regius-pN.jpg where N = handrit image
   index = manuscript page + 9. Checked on every image used (pages 1-39): the
   page number written in the top corner and the first line agree with the
   Wimmer and Jonsson page (QC 2026-11-12).
3. Old Norse: Gudni Jonsson's normalized edition as transcribed on
   heimskringla.no (cached HTML in data/sources/qc-legacy/edda/heimskringla/).
   Verse lines are taken verbatim from the <dd> elements.
4. English: Benjamin Thorpe, The Edda of Saemund the Learned (1866), Project
   Gutenberg #14726 (cached in data/sources/qc-legacy/edda/pg14726.txt).
   Footnote markers [n] are removed; speaker labels (e.g. "_Harbard_.") are
   attached to the stanza they introduce; Gutenberg _italics_ become <em>.
5. Stanza concordance Old Norse <-> Thorpe: built by reading both texts side by
   side (CONC below). Thorpe stanzas are placed beside the Old Norse stanza
   they translate and carry the Old Norse stanza number; Thorpe's own number is
   listed in the entry's translator_notes where it differs.

Sections: one per manuscript page, holding the stanzas that begin on that page.
A stanza that runs onto the next page lists both pages. Where one Thorpe
paragraph covers parts of stanzas on two pages, the section is widened so the
English and Old Norse stay together, and both pages are listed.

Run from the repo root:  python3 scripts/qc_edda_pages.py [--dry-run] [poem ...]
Re-runnable: rebuilds the entries from the cached sources every time.
"""
import html as htmlmod
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "qc-legacy" / "edda"
PUB = ROOT / "translations" / "published"
SCANS = ROOT / "site" / "assets" / "scans"
TODAY = str(date.today())

WJ_URL = "https://archive.org/details/handskriftetnr2300kben"
HANDRIT_URL = "https://handrit.is/manuscript/view/is/GKS04-2365"
PG_URL = "https://www.gutenberg.org/ebooks/14726"

# Wimmer and Jonsson 1891: caption printed under each diplomatic page (stanza
# numbers are Bugge's; "pr." = prose).
WJ_CAPTION = {
    1: "Vǫluspá v. 1-15", 2: "Vǫluspá v. 15-31", 3: "Vǫluspá v. 31-45", 4: "Vǫluspá v. 45-61",
    5: "Vǫluspá v. 61 - Hávamál v. 15", 6: "Hávamál v. 15-31", 7: "Hávamál v. 31-50",
    8: "Hávamál v. 50-69", 9: "Hávamál v. 69-88", 10: "Hávamál v. 88-104",
    11: "Hávamál v. 104-123", 12: "Hávamál v. 123-142", 13: "Hávamál v. 142-161",
    14: "Hávamál v. 161 - Vafþrúðnismál v. 14", 15: "Vafþrúðnismál v. 15-37",
    16: "Vafþrúðnismál v. 38 - Grímnismál pr.", 17: "Grímnismál pr. - v. 4",
    18: "Grímnismál v. 4-24", 19: "Grímnismál v. 24-37", 20: "Grímnismál v. 37-53",
    21: "Grímnismál v. 53 - Skírnismál pr. efter v. 10", 22: "Skírnismál pr. efter v. 10 - v. 28",
    23: "Skírnismál v. 28 - Hárbarðsljóð v. 1", 24: "Hárbarðsljóð v. 1-18",
    25: "Hárbarðsljóð v. 18-40", 26: "Hárbarðsljóð v. 40 - Hymiskviða v. 3",
    27: "Hymiskviða v. 3-21", 28: "Hymiskviða v. 22-38", 29: "Hymiskviða v. 38 - Lokasenna v. 10",
    30: "Lokasenna v. 10-27", 31: "Lokasenna v. 27-45", 32: "Lokasenna v. 45-62",
    33: "Lokasenna v. 63 - Þrymskviða v. 12", 34: "Þrymskviða v. 13-31",
    35: "Þrymskviða v. 31 - Vǫlundarkviða v. 7", 36: "Vǫlundarkviða v. 7-22",
    37: "Vǫlundarkviða v. 22-37", 38: "Vǫlundarkviða v. 38 - Alvíssmál v. 18",
    39: "Alvíssmál v. 18 - Helgakviða Hundingsbana I v. 7",
}


def folio(p):
    return f"{(p + 1) // 2}{'r' if p % 2 else 'v'}"


def image(p):
    return f"codex-regius/codex-regius-p{p + 9}.jpg"


# Words in the first line of each manuscript page (normalized spelling of the
# edition where the line is verse), read on the handrit.is image and matched to
# the Wimmer and Jonsson page, QC 2026-11-12.
PAGE_FIRST = {
    1: ("Hljóðs bið ek allar", "Völuspá 1"), 2: ("meðan öld lifir", "end of Völuspá 16"),
    3: ("Nú eru talðar", "end of Völuspá 30"), 4: ("hátt blæss Heimdallr", "end of Völuspá 46"),
    5: ("dróttir byggja", "end of Völuspá 64"), 6: ("glaðr ok reifr", "end of Hávamál 15"),
    7: ("glissir", "end of Hávamál 31"), 8: ("er stendr þorpi á", "end of Hávamál 50"),
    9: ("sumr er af sonum sæll", "end of Hávamál 69"), 10: ("trúi engi maðr", "end of Hávamál 88"),
    11: ("nú em ek aftr of kominn", "end of Hávamál 104"), 12: ("góðs laun of geta", "end of Hávamál 123"),
    13: ("stinna stafi", "end of Hávamál 142"), 14: ("gaman", "end of Hávamál 161"),
    15: ("Seg þú þat, Gagnráðr", "Vafþrúðnismál 15"), 16: ("Seg þú þat it tíunda", "Vafþrúðnismál 38"),
    17: ("báti með dorgar sínar", "the prose before Grímnismál"), 18: ("ásum ok alfum nær", "end of Grímnismál 4"),
    19: ("með bugum", "end of Grímnismál 24"), 20: ("svangir sól draga", "end of Grímnismál 37"),
    21: ("nú knáttu Óðin sjá", "end of Grímnismál 53"), 22: ("hliði þess er um sal Gerðar var", "the prose after Skírnismál 10"),
    23: ("víðkunnari þú verðir", "end of Skírnismál 28"), 24: ("sveinn sveina", "end of Hárbarðsljóð 1"),
    25: ("hjá þeim systrum sjau", "end of Hárbarðsljóð 18"), 26: ("gnæfa gunnfana", "end of Hárbarðsljóð 40"),
    27: ("yðr of heita", "end of Hymiskviða 3"), 28: ("Egndi á öngul", "Hymiskviða 22"),
    29: ("er hann bæði galt", "end of Hymiskviða 38"), 30: ("sitja sumbli at", "end of Lokasenna 10"),
    31: ("at þér vreiðum vegit", "end of Lokasenna 27"), 32: ("hér hróðugr", "end of Lokasenna 45"),
    33: ("Þegi þú, rög vættr", "Lokasenna 63"), 34: ("Reið varð þá Freyja", "Þrymskviða 13"),
    35: ("fyrstan", "end of Þrymskviða 31"), 36: ("gengu inn þaðan", "end of Vǫlundarkviða 7"),
    37: ("at it mik fyndið", "end of Vǫlundarkviða 22"), 38: ("Hlæjandi Völundr", "Vǫlundarkviða 38"),
    39: ("hjalm huliðs", "end of Alvíssmál 18"),
}


# Per poem: heimskringla file, Thorpe heading, pages as (page, first stanza
# beginning there, last stanza beginning there), stanzas that run onto the next
# page with the Old Norse words that open that next page (checked on the image
# and in Wimmer and Jonsson), page overrides, stanzas not in the manuscript.
POEMS = {
    "voluspa": dict(
        title="Völuspá", hk="V%C3%B6lusp%C3%A1", thorpe="VÖLUSPÂ. THE VALA'S PROPHECY.",
        pages=[(1, 1, 16), (2, 17, 30), (3, 31, 46), (4, 47, 64), (5, 65, 66)],
        cont={16: "meðan öld lifir", 30: "Nú eru talðar", 46: "hátt blæss Heimdallr", 64: "dróttir byggja"},
        text_note={15: "In stanza 15 the edition's names Dóri, Óri, Dúfr, Andvari are not in Codex Regius; on fol. 1r the list runs Draupnir, Dolgþrasir, Hár, Haugspori, Hlévangr, Glói, Skirvir, Virvir, Skafiðr, Ái (Wimmer and Jónsson 1891 page 1)."},
        not_in_r={65: "Stanza 65 (Þá kemr inn ríki) is not in Codex Regius: on fol. 3r stanza 64 is followed directly by stanza 66. Guðni Jónsson's text takes it from Hauksbók (AM 544 4to); fol. 3r is linked because that is where the stanza would stand.",
                  54: "Stanza 54 (the Garmr refrain) is not written at this point in Codex Regius: on fol. 2v stanza 53 is followed directly by stanza 55. Guðni Jónsson repeats the refrain here after Hauksbók."},
        order_note={tuple(range(47, 65)): "On fol. 2v the manuscript order is 47, refrain (abbreviated 'Geyr nú g.'), 50, 51, 48, 52, 53, 55, 56, 57, refrain ('Geyr n.'), 59-64; the edition moves stanza 48 and writes the refrain out in full as stanzas 49 and 58."},
    ),
    "havamal": dict(
        title="Hávamál", hk="H%C3%A1vam%C3%A1l", thorpe="THE HIGH ONE'S[14] LAY.",
        pages=[(5, 1, 15), (6, 16, 31), (7, 32, 50), (8, 51, 69), (9, 70, 88), (10, 89, 104),
               (11, 105, 123), (12, 124, 142), (13, 143, 161), (14, 162, 164)],
        cont={15: "glaðr ok reifr", 31: "glissir", 50: "er stendr þorpi á", 69: "sumr er af sonum sæll",
              88: "trúi engi maðr", 104: "nú em ek aftr of kominn", 123: "góðs laun of geta",
              142: "stinna stafi", 161: "gaman"},
    ),
    "vafthrudnismal": dict(
        title="Vafþrúðnismál", hk="Vaf%C3%BEr%C3%BA%C3%B0nism%C3%A1l", thorpe="THE LAY OF VAFTHRUDNIR.",
        pages=[(14, 1, 14), (15, 15, 37), (16, 38, 55)], cont={},
    ),
    "grimnismal": dict(
        title="Grímnismál", hk="Gr%C3%ADmnism%C3%A1l", thorpe="THE LAY OF GRIMNIR.",
        pages=[(17, 1, 4), (18, 5, 24), (19, 25, 37), (20, 38, 53), (21, 54, 54)],
        cont={4: "ásum ok alfum nær", 24: "með bugum", 37: "svangir sól draga", 53: "nú knáttu Óðin sjá"},
        override={23: [19]},
        order_note={(23, 24): "In the manuscript stanza 24 (Fimm hundruð golfa) comes before stanza 23 (Fimm hundruð dura): 24 begins at the foot of fol. 9v and ends at the top of fol. 10r, and 23 follows it on 10r. The edition reverses the two."},
    ),
    "skirnismal": dict(
        title="Skírnismál", hk="Sk%C3%ADrnism%C3%A1l", thorpe="THE JOURNEY OR LAY OF SKIRNIR.",
        pages=[(21, 1, 10), (22, 11, 28), (23, 29, 42)],
        cont={28: "víðkunnari þú verðir"},
    ),
    "harbardsljod": dict(
        title="Hárbarðsljóð", hk="H%C3%A1rbar%C3%B0slj%C3%B3%C3%B0", thorpe="THE LAY OF HARBARD.",
        pages=[(23, 1, 1), (24, 2, 18), (25, 19, 40), (26, 41, 60)],
        cont={1: "sveinn sveina", 18: "hjá þeim systrum sjau", 40: "gnæfa gunnfana"},
    ),
    "hymiskvida": dict(
        title="Hymiskviða", hk="Hymiskvi%C3%B0a", thorpe="THE LAY OF HYMIR.",
        pages=[(26, 1, 3), (27, 4, 21), (28, 22, 38), (29, 39, 39)],
        cont={3: "yðr of heita", 38: "er hann bæði galt"},
    ),
    "lokasenna": dict(
        title="Lokasenna", hk="Lokasenna", thorpe="OEGIR'S COMPOTATION, OR LOKI'S ALTERCATION.",
        pages=[(29, 1, 10), (30, 11, 27), (31, 28, 45), (32, 46, 62), (33, 63, 65)],
        cont={10: "sitja sumbli at", 27: "at þér vreiðum vegit", 45: "hér hróðugr"},
    ),
    "thrymskvida": dict(
        title="Þrymskviða", hk="%C3%9Erymskvi%C3%B0a", thorpe="THE LAY OF THRYM, OR THE HAMMER RECOVERED.",
        pages=[(33, 1, 12), (34, 13, 31), (35, 32, 32)],
        cont={31: "fyrstan, þursa dróttin"},
    ),
    "volundarkvida": dict(
        title="Vǫlundarkviða", hk="V%C3%B6lundarkvi%C3%B0a", thorpe="THE LAY OF VOLUND.",
        pages=[(35, 1, 7), (36, 8, 22), (37, 23, 37), (38, 38, 41)],
        cont={7: "gengu inn þaðan", 22: "at it mik fyndið"},
    ),
    "alvissmal": dict(
        title="Alvíssmál", hk="Alv%C3%ADssm%C3%A1l", thorpe="THE LAY OF THE DWARF ALVIS.",
        pages=[(38, 1, 18), (39, 19, 35)],
        cont={18: "hjalm huliðs"},
    ),
}

# Old Norse stanza(s) -> Thorpe stanza(s), by Thorpe's printed number (T) or,
# where the Gutenberg numbering has typos, by position in his list (P).
def _ident(n):
    return [([i], [i]) for i in range(1, n + 1)]


def _conc():
    c = {}
    v = [([i], [i]) for i in range(1, 21)]
    v += [([21], [25]), ([22], [26]), ([23], [27]), ([24], [28]), ([25], [29]), ([26], [30]), ([27], [31]),
          ([28], [21, 22]), ([29], [23]), ([30], [24]), ([31], [36]), ([32, 33], [37]), ([34], [39]),
          ([35], [38]), ([36], [40]), ([37], [41]), ([38], [42]), ([39], [43]), ([40], [32]), ([41], [33]),
          ([42], [34]), ([43], [35]), ([44], [44]), ([45], [45, 46]), ([46], [47]), ([47], [48]),
          ([48], [52]), ([49], []), ([50], [49]), ([51], [50]), ([52], [51]), ([53], [53]), ([54], []),
          ([55], [54]), ([56], [55]), ([57], [56]), ([58], []), ([59], [57]), ([60], [58]), ([61], [59]),
          ([62], [60]), ([63], [61]), ([64], [62]), ([65], [64]), ([66], [65])]
    c["voluspa"] = ("T", v)
    h = [([i], [i]) for i in range(1, 11)] + [([11, 12], [11, 12])]
    h += [([i], [i]) for i in range(13, 62)] + [([62], [63]), ([63], [62])]
    h += [([i], [i]) for i in range(64, 103)] + [([103], [103, 104])]
    h += [([i], [i + 1]) for i in range(104, 111)] + [([111], [112, 113])]
    h += [([i], [i + 2]) for i in range(112, 132)] + [([132, 133], [134, 135])]
    h += [([i], [i + 2]) for i in range(134, 165)]
    c["havamal"] = ("T", h)
    c["vafthrudnismal"] = ("P", _ident(55))
    c["grimnismal"] = ("T", _ident(54))
    c["skirnismal"] = ("T", _ident(42))
    c["harbardsljod"] = ("P", _ident(60))
    hy = [([i], [i]) for i in range(1, 6)] + [([6, 7, 8], [6, 7, 8])] + [([i], [i]) for i in range(9, 40)]
    c["hymiskvida"] = ("T", hy)
    c["lokasenna"] = ("T", _ident(65))
    th = [([i], [i]) for i in range(1, 7)] + [([7], [7, 8])] + [([i], [i + 1]) for i in range(8, 33)]
    c["thrymskvida"] = ("T", th)
    vo = [([i], [i]) for i in range(1, 15)] + [([15, 16], [15]), ([17], [16]), ([18], [17]),
                                               (list(range(19, 27)), list(range(18, 25)))]
    vo += [([i], [i - 2]) for i in range(27, 42)]
    c["volundarkvida"] = ("T", vo)
    al = [([i], [i]) for i in range(1, 9)] + [([i], [i + 1]) for i in range(9, 36)]
    c["alvissmal"] = ("T", al)
    return c


CONC = _conc()
THORPE_DROPPED = {"alvissmal": {9: "Thorpe's stanza 9 (Alvis: 'Vingthor! thou canst try ... All the nine worlds I have travelled over') has no counterpart in Codex Regius, where stanza 8 (Meyjar ástum) is followed directly by Thor's first question (fol. 19v), so it is not shown."}}
CONC_NOTES = {
    "voluspa": "Thorpe printed the middle of the poem in a different order from the manuscript, and the old version of this entry set his stanzas beside the wrong Old Norse stanzas from stanza 21 on. Each Thorpe stanza now stands beside the Old Norse stanza it translates. His numbers differ as follows (Old Norse = Thorpe): 21=25, 22=26, 23=27, 24=28, 25=29, 26=30, 27=31, 28=21+22, 29=23, 30=24, 31=36, 32-33=37, 34=39, 35=38, 36=40, 37=41, 38=42, 39=43, 40=32, 41=33, 42=34, 43=35, 45=45+46, 46=47, 47=48 (which also renders the Garmr refrain), 48=52, 50=49, 51=50, 52=51, 55=54, 56=55, 57=56, 59=57, 60=58, 61=59, 62=60, 63=61, 64=62, 65=64, 66=65. Thorpe has no separate English for the repeated refrain (49, 54, 58), and his translation lacks parts of stanzas 32-33 (Baldrs bróðir ... Baldrs andskota).",
    "havamal": "Thorpe divides some stanzas differently. Old Norse = Thorpe: 11-12 = 11-12 (his stanza breaks fall mid-stanza), 62=63, 63=62, 103=103+104, 104-110 = 105-111, 111=112+113, 112-131 = 114-133, 132-133 = 134-135, 134-164 = 136-166.",
    "vafthrudnismal": "The Gutenberg text of Thorpe prints stanza 32 with the number 33 (so 33 appears twice); here his stanzas are matched in order, and the old version of this entry, which dropped one of them, is corrected.",
    "harbardsljod": "The Gutenberg text of Thorpe misprints stanza 26 as '36' and stanza 29 as '39'; here his stanzas are matched in order, which restores two stanzas the old version of this entry had dropped or misplaced.",
    "hymiskvida": "Thorpe divides stanzas 6-8 differently (his 6 is the first half of 6; his 7 covers the second half of 7 and the first half of 8); they are shown together. The Old Norse stanza 9, which the heimskringla.no page prints inside stanza 8, is shown as its own stanza.",
    "thrymskvida": "Thorpe prints stanza 7 as two stanzas (7 and 8), so from stanza 8 on his number is one higher than the Old Norse (Old Norse 8 = Thorpe 9, ... 32 = 33).",
    "volundarkvida": "Thorpe's stanza breaks differ from stanza 15 to 26 (his 15 = Old Norse 15-16; 16 = 17; 17 = 18; his 18-24 run across Old Norse 19-26, each starting mid-stanza, so they are shown as one block), and from stanza 27 on his number is two lower (Old Norse 27 = Thorpe 25, ... 41 = 39).",
    "alvissmal": "From stanza 9 on Thorpe's number is one higher than the Old Norse (Old Norse 9 = Thorpe 10, ... 35 = 36).",
}


# ---------------------------------------------------------------- sources
def heimskringla(frag):
    h = (SRC / "heimskringla" / f"{frag}.html").read_text(encoding="utf-8")
    st, cur = [], None
    for line in re.findall(r"<dd>([^<]*)</dd>", h):
        line = htmlmod.unescape(line).strip()
        if not line or line == "\xa0":
            continue
        m = re.match(r"^(\d+)\.\s*(.*)$", line)
        if m:
            if cur and cur["lines"]:
                st.append(cur)
            cur = {"num": int(m.group(1)), "lines": [m.group(2)] if m.group(2) else []}
            continue
        if cur is None:
            cur = {"num": 1, "lines": []}
        cur["lines"].append(line)
    if cur and cur["lines"]:
        st.append(cur)
    return {s["num"]: " / ".join(s["lines"]) for s in st}


_TH = None
# Unnumbered Thorpe paragraphs that are verse translation, not prose narrative:
# Hymiskvida, Ty's reply and the journey (Old Norse 6 second half, 7 first half).
VERSE_CONTINUATIONS = ['"Yes, friend! if we stratagem']


def thorpe(head):
    global _TH
    if _TH is None:
        _TH = (SRC / "pg14726.txt").read_text(encoding="utf-8").replace("\r", "").split("\n")
    lines = _TH
    start = [i for i, l in enumerate(lines) if l.strip() == head][0]
    end = len(lines)
    for j in range(start + 1, len(lines)):
        l = lines[j].strip()
        if l == l.upper() and re.match(r"^(THE LAY OF|THE JOURNEY|OEGIR'S|THE SONG OF|THE HIGH ONE|VÖLUSP|GROA|FRAGMENT|THE FIRST|THE SECOND|THE THIRD|THE LAMENT|THE TALE|SIGURD|ODDRUN|THE GREENLAND|THE INCITE|THE SPEECH|THE NORNS|PREFACE|INDEX|NOTES)", l):
            end = j
            break
    paras = [p.strip() for p in re.split(r"\n\s*\n", "\n".join(lines[start + 1:end])) if p.strip()]
    out, label = [], None
    for p in paras:
        if p.startswith("[Footnote") or p.startswith("FOOTNOTES"):
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", p, re.S)
        if m:
            t = re.sub(r"\s+", " ", m.group(2)).strip()
            t = re.sub(r"\[\d+\]", "", t)
            # a speaker label printed at the end of a paragraph belongs to the next stanza
            glued = re.search(r"\s+_([^_]{1,25})_\.?$", t)
            if glued:
                t = t[:glued.start()]
            t = re.sub(r"_([^_]+)_", r"<em>\1</em>", t)
            if label:
                t = f"<em>{label}</em>{'' if label.endswith('.') else '.'} {t}"
            out.append({"num": int(m.group(1)), "text": t})
            label = glued.group(1) if glued else None
            continue
        lm = re.match(r"^_([^_]+)_\.?$", p)
        if lm:
            label = lm.group(1)
            continue
        if out and any(p.startswith(c) for c in VERSE_CONTINUATIONS):
            t = re.sub(r"\s+", " ", p).strip()
            if label:
                t = f"<em>{label}</em>{'' if label.endswith('.') else '.'} {t}"
            out[-1]["text"] += " " + t
        label = None
    return out


# ---------------------------------------------------------------- build
def build(key):
    cfg = POEMS[key]
    title = cfg["title"]
    norse = heimskringla(cfg["hk"])
    th = thorpe(cfg["thorpe"])
    by_num = {}
    for i, s in enumerate(th):
        by_num.setdefault(s["num"], s)
    mode, blocks = CONC[key]

    def eng(ref):
        return (th[ref - 1] if mode == "P" else by_num[ref])

    # coverage checks: every Old Norse stanza in exactly one block; every Thorpe stanza used once
    used_n = [n for b in blocks for n in b[0]]
    assert sorted(used_n) == sorted(norse), (key, set(norse) ^ set(used_n))
    used_t = [r for b in blocks for r in b[1]]
    assert len(used_t) == len(set(used_t)), key
    all_t = set(range(1, len(th) + 1)) if mode == "P" else set(by_num)
    dropped = set(THORPE_DROPPED.get(key, {}))
    assert all_t - set(used_t) == dropped, (key, all_t - set(used_t))

    # stanza -> pages
    start = {}
    for p, a, b in cfg["pages"]:
        for n in range(a, b + 1):
            start[n] = p
    for n, ps in cfg.get("override", {}).items():
        start[n] = ps[0]
    pages_of = {}
    for n in norse:
        ps = [start[n]]
        if n in cfg["cont"]:
            ps.append(start[n] + 1)
            assert cfg["cont"][n] in norse[n].replace(" / ", " "), (key, n, cfg["cont"][n])
        if key == "grimnismal" and n == 24:
            ps = [18, 19]
        pages_of[n] = ps

    # the first-line phrase of each page must occur in the stanza it is said to belong to
    for p, _, _ in cfg["pages"]:
        ph, what = PAGE_FIRST[p]
        m = re.match(r"^(?:end of )?(.+) (\d+)$", what)
        if m and m.group(1) == title:
            assert ph in norse[int(m.group(2))].replace(" / ", " "), (key, p, ph)

    # group into sections by start page, then widen for concordance blocks
    order = sorted(norse)
    groups = []
    for n in order:
        if groups and start[groups[-1][-1]] == start[n]:
            groups[-1].append(n)
        else:
            groups.append([n])
    # Grimnismal: 23 sits on 10r with 24's end; keep 23-24 as its own section
    if key == "grimnismal":
        g2 = []
        for g in groups:
            if 23 in g or 24 in g:
                rest = [x for x in g if x not in (23, 24)]
                if rest:
                    g2.append(rest)
                if not any(23 in x for x in g2):
                    g2.append([23, 24])
            else:
                g2.append(g)
        groups = g2
    # a concordance block that crosses a page section is kept whole in the
    # section where it begins (that section then lists both pages)
    widened = {}
    for b in blocks:
        gi = {n: i for i, g in enumerate(groups) for n in g}
        first = gi[b[0][0]]
        moved = False
        for n in b[0][1:]:
            if gi[n] != first:
                groups[gi[n]].remove(n)
                groups[first].append(n)
                moved = True
        groups[first].sort()
        if moved:
            widened[tuple(b[0])] = True
        groups = [g for g in groups if g]

    sections, all_pages = [], []
    for g in groups:
        sv, ev = g[0], g[-1]
        ref = f"{sv}-{ev}" if sv != ev else str(sv)
        ps = []
        for n in g:
            for p in pages_of[n]:
                if p not in ps:
                    ps.append(p)
        ps.sort()
        orig = " ".join(f"<sup>{n}</sup>{norse[n]}" for n in g)
        etxt = []
        for gl, tl in blocks:
            if gl[0] in g and tl:
                lab = f"{gl[0]}-{gl[-1]}" if len(gl) > 1 else str(gl[0])
                etxt.append(f"<sup>{lab}</sup>" + " ".join(eng(r)["text"] for r in tl))
        note = scan_note(key, cfg, g, ps, pages_of, norse)
        for bl in widened:
            if bl[0] in g:
                note += (f" Stanzas {bl[0]}-{bl[-1]} are kept together in this section because Thorpe's English for them "
                         f"runs across the stanza breaks, so this section lists both pages.")
        fol = f"fol. {folio(ps[0])}" + (f"-{folio(ps[-1])}" if len(ps) > 1 else "")
        sections.append({
            "section": ref,
            "original_ref": f"{title} st. {ref} (GKS 2365 4to, {fol})",
            "original_text": orig,
            "text": " ".join(etxt),
            "scan_pages": [image(p) for p in ps],
            "scan_note": note,
        })
        for p in ps:
            if p not in all_pages:
                all_pages.append(p)
    all_pages.sort()
    return sections, all_pages, norse, th


def scan_note(key, cfg, g, ps, pages_of, norse):
    parts = []
    for p in ps:
        here = [n for n in g if p in pages_of[n]]
        if not here:
            continue
        starts = [n for n in here if pages_of[n][0] == p and n not in cfg.get("not_in_r", {})]
        ends = [n for n in here if pages_of[n][0] != p]
        d = f"Fol. {folio(p)} (manuscript page {p}; handrit.is image {p + 9}; Wimmer and Jónsson 1891 page {p}, caption '{WJ_CAPTION[p]}')"
        bits = []
        if ends:
            bits.append(f"the top of the page finishes stanza {ends[0]} ('{cfg['cont'][ends[0]]} ...')")
        if starts:
            rng = f"{starts[0]}-{starts[-1]}" if len(starts) > 1 else f"{starts[0]}"
            word = "stanzas" if len(starts) > 1 else "stanza"
            bits.append(f"{word} {rng} {'begin' if len(starts) > 1 else 'begins'} here")
            last = starts[-1]
            if last in cfg["cont"] and pages_of[last][-1] != p:
                bits.append(f"stanza {last} runs on to fol. {folio(p + 1)}")
        if p == cfg["pages"][0][0] and cfg["title"] not in PAGE_FIRST[p][1]:
            bits.insert(0, f"stanza 1 is lower on the page (the first line belongs to {PAGE_FIRST[p][1].replace('end of ', 'the end of ')})")
        parts.append(d + ": " + "; ".join(bits) + ".")
    checks = []
    for p in ps:
        ph, what = PAGE_FIRST[p]
        checks.append(f"the first line of fol. {folio(p)} has '{ph}' ({what})")
    s = " ".join(parts) + " Checked on the image: " + "; ".join(checks) + "."
    for n in g:
        if n in cfg.get("text_note", {}):
            s += " " + cfg["text_note"][n]
    for n in g:
        if n in cfg.get("not_in_r", {}):
            s += " " + cfg["not_in_r"][n]
    for stz, txt in cfg.get("order_note", {}).items():
        if set(stz) & set(g):
            s += " " + txt
    return s


def write(key, dry):
    cfg = POEMS[key]
    path = PUB / f"verified-edda-{key}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    sections, pages, norse, th = build(key)
    for p in pages:
        f = SCANS / image(p)
        assert f.exists() and f.stat().st_size > 50000, f
    title = cfg["title"]
    f0, f1 = folio(pages[0]), folio(pages[-1])
    fol = f"fol. {f0}-{f1}" if f0 != f1 else f"fol. {f0}"
    v = d.get("verification", {})
    v.pop("scan_folios", None)
    v.update({
        "scan_source": f"handrit.is (Árni Magnússon Institute for Icelandic Studies), page images of GKS 2365 4to, {HANDRIT_URL}",
        "scan_manuscript": "GKS 2365 4to (Codex Regius of the Poetic Edda, Iceland, c. 1270), Árni Magnússon Institute, Reykjavík",
        "scan_mapping": ("Page of every stanza from Ludv. F. A. Wimmer and Finnur Jónsson, Håndskriftet Nr. 2365 4to gl. kgl. samling "
                         "(Codex regius af den ældre Edda) i fototypisk og diplomatisk gengivelse (København 1891), which prints the text of "
                         "each manuscript page with a caption of the stanzas on it. Captions use Bugge's stanza numbers, so each page break was "
                         "matched by the words of the text. Every page used was checked on the handrit.is image (first line, and the page "
                         "number written in the top corner where it is visible). handrit.is image N = manuscript page N-9. Rebuilt by scripts/qc_edda_pages.py on " + TODAY + "."),
        "scan_mapping_urls": [WJ_URL, HANDRIT_URL],
        "scan_local_paths": [image(p) for p in pages],
        "scan_folios": [folio(p) for p in pages],
        "original_text_source": f"Guðni Jónsson (ed.), Eddukvæði (Sæmundar-Edda), normalized text as transcribed on heimskringla.no, https://heimskringla.no/wiki/{cfg['hk']}",
        "original_text_license": "heimskringla.no gives no licence on the page. Earlier versions of this entry called it public domain; that is not verified (the editor, Guðni Jónsson, died in 1974).",
        "translation_source": f"Benjamin Thorpe, Edda Sæmundar hinns Fróða: The Edda of Sæmund the Learned (London, 1866), Project Gutenberg eBook #14726, {PG_URL}",
        "translation_license": "public domain (published 1866)",
        "translator": "Benjamin Thorpe (1866)",
        "thorpe_alignment": "Thorpe's stanzas matched to the Old Norse by content, stanza by stanza (scripts/qc_edda_pages.py)",
        "footnote_markers_removed": True,
        "verified_date": TODAY,
    })
    v.pop("scan_folios_note", None)
    d["verification"] = v
    d["translation"] = sections
    d["source"] = "Codex Regius (GKS 2365 4to) page images via handrit.is + Guðni Jónsson's Old Norse via heimskringla.no + Thorpe (1866) English"
    d["description"] = (f"{title}, from the Poetic Edda in Codex Regius (GKS 2365 4to, c. 1270), {fol}. Each section links the "
                        f"manuscript page that carries its stanzas. Old Norse from Guðni Jónsson's edition (heimskringla.no); "
                        f"English by Benjamin Thorpe (1866, public domain).")
    notes = []
    if key in CONC_NOTES:
        notes.append(CONC_NOTES[key])
    for t, why in THORPE_DROPPED.get(key, {}).items():
        notes.append(why)
    for n, why in cfg.get("not_in_r", {}).items():
        notes.append(why)
    d["translator_notes"] = notes
    extra = ""
    if cfg.get("not_in_r"):
        extra += "<p><strong>Not in the manuscript:</strong> " + " ".join(cfg["not_in_r"][n] for n in sorted(cfg["not_in_r"])) + "</p>"
    if cfg.get("order_note"):
        extra += "<p><strong>Stanza order:</strong> " + " ".join(cfg["order_note"].values()) + "</p>"
    if key in CONC_NOTES:
        extra += "<p><strong>English alignment:</strong> " + CONC_NOTES[key] + "</p>"
    d["introduction"] = (
        f"<p><strong>{title}</strong> is preserved in the Codex Regius of the Poetic Edda (GKS 2365 4to, Árni Magnússon Institute, "
        f"Reykjavík), an Icelandic parchment book written about 1270. The poem fills {fol} (manuscript pages {pages[0]}-{pages[-1]}).</p>"
        f"<p><strong>Pages:</strong> each section holds the stanzas that begin on one manuscript page and links that page's photograph "
        f"(handrit.is); a stanza that runs onto the next page links both pages. The page of every stanza comes from Wimmer and Finnur "
        f"Jónsson's 1891 diplomatic edition, which prints the text of each manuscript page, and the first line of every page was checked "
        f"on the photograph. 'Where on the image' under each section gives the details.</p>"
        f"<p><strong>Texts:</strong> the Old Norse is Guðni Jónsson's normalized edition (via heimskringla.no), a reading text in modern "
        f"spelling, not a letter-by-letter transcription of the manuscript; in places it adds words or lines from other manuscripts and "
        f"follows modern editions where they rearrange stanzas. The English is Benjamin Thorpe's 1866 translation (public domain). The "
        f"prose passages of the manuscript are not included.</p>" + extra
    )
    if dry:
        print(key, len(sections), "sections, pages", [folio(p) for p in pages])
        return
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{key}: {len(sections)} sections, {len(norse)} Old Norse stanzas, {len(th)} Thorpe stanzas, {fol}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    for key in (args or list(POEMS)):
        write(key, dry)


if __name__ == "__main__":
    main()
