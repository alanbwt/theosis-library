#!/usr/bin/env python3
"""
qc3_fix_entries.py: fixes for the defects and the actionable doubts of the
QC review docs/qc/review-bible-christian.md (2026-11-12). Re-runnable: every
edit checks the current state first and does nothing when it is already done.

Evidence for each fix (images read during this QC, crops in the session
scratchpad, not in the repo):
  - Vaticanus p. 1303: col. 2 ends εφοβουντο γαρ, then the subscription
    ΚΑΤΑ ΜΑΡΚΟΝ; col. 3 has no writing (the faint mirror-image letters and the
    green band there show through from the start of Luke on the other side).
  - Vaticanus p. 1518: last line of col. 3 reads ΑΜΩΜΟΝ ΤΩ ΘΩ ΚΑΘΑ.
  - Sinaiticus fol. 278v: col. 2 line 1 ΟΙ ΑΓΙΟΙ ΠΑΝΤΕϹ, lines 2-6 Η ΧΑΡΙϹ ΤΟΥ
    ΚΥ ... ΜΕΤΑ ΠΑΝΤΩΝ ΥΜΩΝ (KJV 13:14 is present).
  - Washingtonianus p0211 (30 lines): line 26 ends ΕΝΟΜΕΙΖΕΤΟ ΙΩϹΗΦ (3:23),
    line 27 begins ΙϹ ΔΕ ΠΛΗΡΗϹ ΠΝϹ ΑΓΙΟΥ (4:1), lines 29-30 ΗΜΕΡΑϹ Μ
    ΠΕΙΡΑΖΟΜΕΝΟϹ ΥΠΟ ΤΟΥ ΔΙΑΒΟΛΟΥ (4:2a). Luke 3:23b-38 is not in the codex.
  - Washingtonianus p0302: last three lines ΚΑΙ ΑΝΑϹΤΑΝ ΑΠΑΝ ΤΟ ΠΛΗΘΟϹ
    ΑΥΤΩΝ ΗΓΑΓΟΝ ΑΥΤΟΝ ΕΠΙ ΤΟΝ ΠΕΙΛΑΤΟΝ (Luke 23:1); p0303 begins ΗΡΞΑΝΤΟ.
  - Leningrad fol. 133v, right-hand column: line 10 ends מגרשה ערים ארבע
    (21:35), line 11 begins וממטה גד את עיר (21:38). UXLC marks 21:36-37
    with note X, "This verse does NOT occur in the Leningrad Codex".
  - 1QIsa-a col. II: וישח אדם וישפל איש runs straight into ועיני גבהות אדם
    (2:9a, then 2:11).
  - Bezae fol. 3v: line 1 ΠΑΡΑΛΑΒΕΙΝ ΜΑΡΙΑΜ ΤΗΝ ΓΥΝΑΙΚΑ ϹΟΥ (inside 1:20).
  - BnF Arabe 328 fol. 70v line 1 begins واستغشوا (word 10 of 71:7), so 70r
    ends at word 9; fol. 2r last line ends واخرى (word 13 of 3:13), the right
    end of the first line of 2v is damaged.
English for added or flagged verses is the KJV already used by these
entries (bible-api.com, cached in other entries or in
data/sources/washingtonianus_cache); Greek for added verses is Tischendorf
8 from the same bolls.life caches.

Run from the repo root:  python3 -I scripts/qc3_fix_entries.py
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
WCACHE = ROOT / "data" / "sources" / "washingtonianus_cache" / "json"
TODAY = str(date.today())
LOG = []


def path(eid):
    return PUB / f"{eid}.json"


def load(eid):
    return json.loads(path(eid).read_text(encoding="utf-8"))


def save(d):
    path(d["id"]).write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def sec(d, name):
    for s in d["translation"]:
        if s["section"] == name:
            return s
    return None


def log(eid, what):
    LOG.append(f"{eid}: {what}")


def sub_once(text, old, new):
    """Replace old by new once; return (text, changed). Fails loudly if
    neither the old nor the new form is there."""
    if old in text:
        return text.replace(old, new, 1), True
    if new in text:
        return text, False
    raise SystemExit(f"text not found: {old[:80]!r}")


def verse_seg(html, v):
    m = re.search(rf"<sup>{v}</sup>", html)
    if not m:
        return None
    n = re.search(r"<sup>", html[m.end():])
    return m.end(), (m.end() + n.start() if n else len(html))


def set_verse(html, v, new_body):
    sp = verse_seg(html, v)
    return html[:sp[0]] + new_body + html[sp[1]:]


def get_verse(html, v):
    sp = verse_seg(html, v)
    return html[sp[0]:sp[1]] if sp else None


def drop_tail_space(s):
    return s.rstrip()


def para(intro, label, body, after=None):
    """Add or replace <p><strong>label:</strong> body</p> in an intro."""
    new = f"<p><strong>{label}:</strong> {body}</p>"
    pat = re.compile(rf"<p><strong>{re.escape(label)}:</strong>.*?</p>", re.S)
    if pat.search(intro):
        return pat.sub(lambda m: new, intro, count=1)
    return intro + new


def strongs(t):
    return re.sub(r"<S>\d+</S>", "", t or "").strip()


def wcache(key):
    p = WCACHE / (hashlib.sha1(key.encode()).hexdigest() + ".json")
    return json.loads(p.read_text(encoding="utf-8"))


def tisch(bolls_book, ch, v):
    return next(strongs(x["text"]) for x in wcache(f"tisch:{bolls_book}:{ch}") if int(x["verse"]) == v)


def kjv(api, ch, v):
    return next(x["text"].strip() for x in wcache(f"kjv:{api}:{ch}")["verses"] if int(x["verse"]) == v)


def partial(d, v, greek_mark, eng_keep, eng_lost, where, reason):
    """Mark a verse of which only part is in the manuscript. where='start'
    (the beginning is missing) or 'end'."""
    for s in d["translation"]:
        g = get_verse(s.get("original_text", ""), v)
        e = get_verse(s.get("text", ""), v)
        if g is None or e is None:
            continue
        if "<em>[" in g and "<em>[" in e:
            return False
        trail_g = " " if g.endswith(" ") else ""
        trail_e = " " if e.endswith(" ") else ""
        gb = g.strip()
        if where == "start":
            g_new = f"<em>[{greek_mark}]</em> {gb}"
            e_new = f"<em>[The beginning of this verse, \"{eng_lost}\", {reason}.]</em> {eng_keep}"
        else:
            g_new = f"{gb} <em>[{greek_mark}]</em>"
            e_new = f"{eng_keep} <em>[the rest of this verse, \"{eng_lost}\", {reason}]</em>"
        norm_e = re.sub(r"\s+", " ", e).strip()
        assert re.sub(r"\s+", " ", eng_keep) in norm_e and re.sub(r"\s+", " ", eng_lost) in norm_e, (d["id"], v, norm_e)
        s["original_text"] = set_verse(s["original_text"], v, g_new + trail_g)
        s["text"] = set_verse(s["text"], v, e_new + trail_e)
        log(d["id"], f"verse {v} marked as partly preserved ({where} missing)")
        return True
    raise SystemExit(f"{d['id']}: verse {v} not found")


# ---------------------------------------------------------------------------
# Codex Sinaiticus
# ---------------------------------------------------------------------------
def fix_barnabas_21():
    d = load("verified-sinaiticus-barnabas-21")
    s = sec(d, "21.6-9")
    end = "The Lord of glory and of every grace be with your spirit."
    i = s["text"].find(end)
    if i < 0:
        raise SystemExit("barnabas-21 ending not found")
    if len(s["text"]) > i + len(end):
        s["text"] = s["text"][:i + len(end)]
        save(d)
        log(d["id"], "21:9 English cut after Lightfoot's last sentence; earlychristianwritings.com page text removed")


def fix_sinaiticus_2cor_13():
    d = load("verified-sinaiticus-2cor-13")
    s = sec(d, "13.11-14")
    if "<sup>14</sup>η χαριϲ" in s["original_text"]:
        return
    s["original_text"], _ = sub_once(
        s["original_text"], "<sup>13</sup>η χαριϲ",
        "<sup>13</sup><em>[these words are part of verse 12 in the Greek numbering]</em> <sup>14</sup>η χαριϲ")
    s["scan_note"] = (s["scan_note"].rstrip(".") + ". Checked on the image: col. 2 line 1 ends verse 12 (ΟΙ ΑΓΙΟΙ ΠΑΝΤΕϹ, "
                      "KJV 13:13) and lines 2-6 carry the grace (Η ΧΑΡΙϹ ΤΟΥ ΚΥ ΙΥ ΧΥ ... ΜΕΤΑ ΠΑΝΤΩΝ ΥΜΩΝ, KJV 13:14).")
    intro = re.sub(r"<p><strong>Manuscript note:</strong> KJV verse 13:14 is not present.*?</p>", "", d["introduction"], flags=re.S)
    d["introduction"] = para(intro, "Numbering",
        "The Codex Sinaiticus Project transcription, like Tischendorf's comparison text, follows the standard Greek "
        "numbering (13:12-13); the KJV divides the same words as 13:12-14. Greek verse 13 (the grace) is shown as KJV "
        "verse 14, and KJV verse 13 (\"All the saints salute you\") is part of Greek verse 12. Nothing is missing: the "
        "grace stands on fol. 278v, col. 2, lines 2-6.")
    v = d["verification"]
    if isinstance(v.get("absent_in_manuscript"), list):
        v["absent_in_manuscript"] = [x for x in v["absent_in_manuscript"] if x != "13:14"]
    save(d)
    log(d["id"], "13:14 is present (fol. 278v col. 2 ll. 2-6): Greek 13 shown as KJV 14, KJV 13 marked part of Greek 12, false note replaced")


NS_OLD = ("nomina sacra (e.g. ⟨θϲ⟩ = θεός), and scribal marks. Nomina sacra are shown in angle brackets to indicate "
          "the manuscript's sacred-name abbreviations.")
NS_NEW = ("nomina sacra as the scribe contracted them (e.g. θϲ = θεός, κϲ = κύριος; the overline is not reproduced), "
          "and scribal marks.")
FILLER = ("<p><strong>Line fillers:</strong> the sign &gt; in the Greek is a mark the Codex Sinaiticus Project transcribes "
          "as a diple: a small wedge the scribe wrote at the end of a line, usually to fill out a short line. It is not "
          "part of the text. Line breaks are not shown here, so where a word runs over a line end the mark can stand "
          "inside the word (for example ζητει&gt;τε, where the line ends after ζητει).</p>")
SUPERSCRIPTION_OLD = "The Greek and English in each section are the same words of the same psalm."
SUPERSCRIPTION_NEW = ("The KJV prints the superscription as an unnumbered heading, which is not part of the English "
                      "here, so the Greek superscription has no English beside it; otherwise the Greek and English in "
                      "each section are the same words of the same psalm.")


def fix_sinaiticus_intros():
    n_ns = n_fill = n_ps = 0
    for p in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        intro = d.get("introduction", "")
        changed = False
        if NS_OLD in intro:
            intro = intro.replace(NS_OLD, NS_NEW)
            n_ns += 1
            changed = True
        has_filler = any(">" in re.sub(r"<[^>]*>", "", s.get("original_text", "")) for s in d["translation"])
        if has_filler and "<strong>Line fillers:</strong>" not in intro:
            intro += FILLER
            n_fill += 1
            changed = True
        if "counts the superscription as verse" in intro and SUPERSCRIPTION_OLD in intro:
            intro = intro.replace(SUPERSCRIPTION_OLD, SUPERSCRIPTION_NEW)
            n_ps += 1
            changed = True
        if changed:
            d["introduction"] = intro
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    if n_ns or n_fill or n_ps:
        LOG.append(f"Sinaiticus intros: nomina sacra sentence corrected in {n_ns}; line-filler note added to {n_fill}; "
                   f"psalm superscription sentence corrected in {n_ps}")


def fix_sinaiticus_john_5():
    d = load("verified-sinaiticus-john-5")
    if partial(d, 3, "the rest of this verse in the KJV (5:3b) is not in Codex Sinaiticus",
               "In these lay a great multitude of impotent folk, of blind, halt, withered,",
               "waiting for the moving of the water.", "end", "is not in Codex Sinaiticus"):
        d["introduction"], _ = sub_once(
            d["introduction"], "KJV verse 5:4 is not present in Codex Sinaiticus",
            "KJV verse 5:4, and the end of 5:3 (\"waiting for the moving of the water\"), are not present in Codex Sinaiticus")
        save(d)


def fix_matt_16_2():
    """Matthew 16:2b-3 is not in Sinaiticus or Vaticanus; 16:3 is flagged by
    qc3_absent_verses.py, the end of 16:2 is marked here."""
    for eid, name in (("verified-sinaiticus-matt-16", "Codex Sinaiticus"), ("verified-vaticanus-matt-16", "Codex Vaticanus")):
        d = load(eid)
        if partial(d, 2, f"the rest of this verse in the KJV (16:2b) is not in {name}",
                   "He answered and said unto them,",
                   "When it is evening, ye say, It will be fair weather: for the sky is red.", "end",
                   f"is not in {name}"):
            notes = re.findall(r"<p><strong>Manuscript note:</strong>.*?</p>", d["introduction"], flags=re.S)
            add = (f" The end of 16:2 (\"When it is evening, ye say, It will be fair weather: for the sky is red.\") is "
                   f"not in {name} either, and is marked in both columns.")
            if notes:
                d["introduction"] = d["introduction"].replace(notes[0], notes[0][:-4] + add + "</p>", 1)
            d["verification"]["verses_partly_preserved"] = "2"
            save(d)


def fix_sinaiticus_numbering_notes():
    """Two verse-division differences explained under 'Manuscript note' are
    moved to a 'Numbering' paragraph with the words concerned."""
    items = {
        "verified-sinaiticus-3john-1": ("Greek verse 1:15 has no KJV counterpart under that number",
            "The Codex Sinaiticus Project transcription follows the standard Greek numbering, which divides the KJV's "
            "verse 14 into verses 14 and 15: Greek verse 15 (\"Peace be to thee. Our friends salute thee. Greet the "
            "friends by name.\") is the end of KJV verse 14. Nothing is missing."),
        "verified-sinaiticus-rev-12": ("Greek verse 12:18 has no KJV counterpart under that number",
            "The Codex Sinaiticus Project transcription follows the standard Greek numbering, which has a verse 12:18 "
            "(και εϲταθη επι την αμμον τηϲ θαλαϲϲηϲ, \"and he stood upon the sand of the sea\"); the KJV prints these "
            "words at the start of 13:1, so Greek verse 18 has no English here. Nothing is missing."),
    }
    for eid, (old, body) in items.items():
        d = load(eid)
        if "<strong>Numbering:</strong>" in d["introduction"]:
            continue
        d["introduction"] = re.sub(rf"<p><strong>Manuscript note:</strong> {re.escape(old)}.*?</p>", "",
                                   d["introduction"], flags=re.S)
        d["introduction"] = para(d["introduction"], "Numbering", body)
        save(d)
        log(eid, "verse-division difference explained in a Numbering paragraph")


GITHUB_IMAGES = ["sirach-31-Q70_1r_B359.jpg", "sirach-32-Q70_1v_B360.jpg", "hermas-27-Q93_7r_B721.jpg",
                 "jer-10-Q47_1r_L020.jpg", "prov-29-Q65_7v_B292.jpg", "ps-71-Q61_4r_B221.jpg", "ps-80-Q61_7v_B228.jpg"]


def fix_small_notes():
    # Sinaiticus: say where the 7 images taken from a GitHub copy of the CSP photographs come from
    n = 0
    for p in sorted(PUB.glob("verified-sinaiticus-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        used = sorted({f.split("/")[-1] for s in d["translation"] for f in s["scan_pages"]} & set(GITHUB_IMAGES))
        v = d["verification"]
        if not used or v.get("scan_source_note"):
            continue
        v["scan_source_note"] = (f"{', '.join(used)}: the Codex Sinaiticus Project's photograph, taken from a copy on "
                                 f"GitHub (github.com/0x53616D75656C/Codex-Sinaiticus, images/uncompressed) because "
                                 f"codexsinaiticus.org did not answer on 2026-11-12; each file was identified on the image "
                                 f"(folio number, first words, neighbouring pages). See "
                                 f"docs/collections/qc-sinaiticus-venetus.md.")
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        n += 1
    if n:
        LOG.append(f"Sinaiticus: scan_source_note on the GitHub-copied CSP images added to {n} entries")
    # 1QIsa-a: explain "line 0"
    d = load("verified-1qisaa-isa-51")
    s = sec(d, "51.9-16")
    if not s.get("scan_note"):
        s["scan_note"] = ("The transcription numbers as line 0 the text written above the first full line of col. XLIII. "
                          "Checked on the image: the column begins with two short lines at the upper right, כאשר כונן "
                          "להשחית ואיה חמת המציק (end of 51:13) and מהר צרה להפתח ... ולוא יחסר לחמו (51:14), above the "
                          "full-width lines that begin with 51:15 (אנוכי יהוה אלוהיכה).")
        save(d)
        log(d["id"], "'line 0' of col. XLIII explained in a scan_note (checked on the image)")
    # Alexandrinus Hebrews 7: the NTVMR index range recorded for leaf 141v
    d = load("verified-alexandrinus-hebrews-7")
    v = d["verification"]
    if not v.get("page_captions_note"):
        v["page_captions_note"] = ("The NTVMR index range recorded in page_captions for fol. 141v (Heb 7:17-28) starts one "
                                   "verse late: col. 1 of 141v begins with the end of 7:16 (ΑΛΛΑ ΚΑΤΑ ΔΥΝΑΜΙΝ ΖΩΗϹ "
                                   "ΑΚΑΤΑΛΥΤΟΥ), which is why section 7.10-16 links that page.")
        save(d)
        log(d["id"], "note on the NTVMR index range of fol. 141v")


def fix_magdala():
    for eid in ("verified-sinaiticus-matt-15", "verified-vaticanus-matt-15", "verified-bezae-matt-15",
                "verified-washingtonianus-matt-15"):
        d = load(eid)
        hit = False
        for s in d["translation"]:
            if "coasts of Magdala," in s["text"] and s["text"].rstrip().endswith("Magdala,"):
                s["text"] = s["text"].rstrip()[:-1] + "."
                hit = True
        if hit:
            save(d)
            log(eid, "KJV 15:39 ends 'Magdala.' (full stop restored)")


# ---------------------------------------------------------------------------
# Codex Vaticanus
# ---------------------------------------------------------------------------
def fix_vaticanus_2cor_13():
    d = load("verified-vaticanus-2cor-13")
    s = sec(d, "13.9-13")
    if s is None:
        return
    alex = load("verified-alexandrinus-2cor-13")
    k14 = get_verse(sec(alex, "13.10-14")["text"], 14).strip()
    s["original_text"], _ = sub_once(
        s["original_text"], "<sup>13</sup>η χαρις",
        "<sup>13</sup><em>[these words are part of verse 12 in the Greek numbering]</em> <sup>14</sup>η χαρις")
    s["text"] = s["text"].rstrip() + f" <sup>14</sup>{k14}"
    s["section"], s["original_ref"] = "13.9-14", "2 Corinthians 13:9-14"
    s["scan_note"] = s["scan_note"].replace("verses 9-13 on p. 1487", "Greek verses 9-13 (KJV 9-14) on p. 1487").rstrip(".") + \
        ". KJV verse 13 is part of the Greek verse before it."
    d["introduction"] = para(d["introduction"], "Numbering",
        "The transcription, like Tischendorf's comparison text, follows the standard Greek numbering (13:12-13); the "
        "KJV divides the same words as 13:12-14. Greek verse 13 (the grace) is shown as KJV verse 14, and KJV verse 13 "
        "(\"All the saints salute you\") is part of Greek verse 12.")
    save(d)
    log(d["id"], "Greek 13 paired with KJV 14 (added); KJV 13 marked part of Greek 12; Numbering note")


def fix_vaticanus_mark_16():
    d = load("verified-vaticanus-mark-16")
    if sec(d, "16.9-20"):
        return
    sin = load("verified-sinaiticus-mark-16")
    eng, tis = {}, {}
    for s in sin["translation"]:
        for n, t in re.findall(r"<sup>(\d+)</sup>((?:(?!<sup>).)*)", s["text"], re.S):
            eng.setdefault(int(n), t.strip())
        for n, t in re.findall(r"<sup>(\d+)</sup>((?:(?!<sup>).)*)", s.get("edition_text", ""), re.S):
            tis.setdefault(int(n), t.strip())
    vs = range(9, 21)
    note = ("Checked on the image: p. 1303, col. 2 ends with 16:8 (ΕΦΟΒΟΥΝΤΟ ΓΑΡ) and the subscription ΚΑΤΑ ΜΑΡΚΟΝ; "
            "the third column has no writing of its own (the faint mirror-image letters and the green band seen there "
            "show through from the beginning of Luke on the other side of the leaf). Verses 16:9-20 are not in Codex "
            "Vaticanus; the page shown is where the text of Mark ends.")
    d["translation"].append({
        "section": "16.9-20", "original_ref": "Mark 16:9-20",
        "original_text": " ".join(f"<sup>{v}</sup><em>[not in Codex Vaticanus]</em>" for v in vs),
        "text": " ".join(f"<sup>{v}</sup>{eng[v]}" for v in vs),
        "scan_pages": ["vaticanus/vat-b-mark-16-f1303.jpg"],
        "scan_note": note,
        "edition_text": " ".join(f"<sup>{v}</sup>{tis[v]}" for v in vs),
    })
    s8 = sec(d, "16.4-8")
    if "subscription" not in s8["scan_note"]:
        s8["scan_note"] = s8["scan_note"].rstrip(".") + (". Checked on the image: col. 2 ends ΕΦΟΒΟΥΝΤΟ ΓΑΡ, followed by the "
                                                         "subscription ΚΑΤΑ ΜΑΡΚΟΝ; col. 3 is left blank.")
    d["introduction"] = para(d["introduction"], "Manuscript note",
        "Codex Vaticanus ends Mark at 16:8 (\"for they were afraid\"), followed by the subscription ΚΑΤΑ ΜΑΡΚΟΝ; the "
        "rest of the column and the whole of the next column are left blank. Not written in Codex Vaticanus: verses "
        "16:9-20. The English is shown with the note [not in Codex Vaticanus] in the Greek column, and Tischendorf's "
        "text of these verses is under Compare.")
    d["verification"]["verses_not_in_manuscript"] = "9-20"
    save(d)
    log(d["id"], "16:9-20 added as a flagged section on p. 1303 (codex ends at 16:8, blank column checked on the image)")


def fix_vaticanus_hebrews_9():
    d = load("verified-vaticanus-hebrews-9")
    s = sec(d, "9.8-14")
    g = get_verse(s["original_text"], 14)
    if "breaks off" in g:
        return
    s["original_text"] = set_verse(s["original_text"], 14, g.rstrip() + " <em>[the original codex breaks off here, in the "
                                   "middle of the word καθα(ριει), \"shall purge\"]</em>")
    e = get_verse(s["text"], 14)
    keep = "How much more shall the blood of Christ, who through the eternal Spirit offered himself without spot to God, purge"
    lost = "your conscience from dead works to serve the living God?"
    assert e.startswith(keep) and e.rstrip().endswith(lost), e
    s["text"] = set_verse(s["text"], 14, f"{keep} <em>[the original codex breaks off in this word; the rest of the "
                                         f"verse, \"{lost}\", is not in it]</em>")
    s["scan_note"] = s["scan_note"].rstrip(".") + (". Checked on the image: the last line of col. 3 reads ΑΜΩΜΟΝ ΤΩ ΘΩ "
                                                   "ΚΑΘΑ, the last words of the original codex.")
    d["introduction"] = para(d["introduction"], "Manuscript note",
        "The original Codex Vaticanus breaks off at the foot of p. 1518, in Hebrews 9:14, in the middle of the word "
        "καθα(ριει), \"shall purge\". Everything after this point in the original codex is lost. The pages that now "
        "complete Hebrews in Vat. gr. 1209 were written in minuscule script in the 15th century and are counted as a "
        "separate manuscript (Gregory-Aland 1957); they are not shown here. Hebrews 9:15-28 is therefore not shown, "
        "and the English of 9:14 stops where the Greek stops.")
    v = d["verification"]
    v["verses_lost_in_manuscript"] = "15-28"
    v["verses_partly_preserved"] = "14"
    save(d)
    log(d["id"], "9:14 English cut at the end of the original hand (καθα); end of the codex stated; 9:15-28 listed as lost")


# ---------------------------------------------------------------------------
# Codex Alexandrinus
# ---------------------------------------------------------------------------
STALE_NUM = re.compile(r"<p><strong>Numbering:</strong> Tischendorf's verse numbering in this chapter differs from the "
                       r"KJV's \((\d+) Greek verses against (\d+) English\)\. This affects only the Tischendorf "
                       r"comparison text\.</p>")


def fix_double_numbering():
    """Entries with the stale Tischendorf-only Numbering paragraph and the
    new transcription Numbering paragraph: keep one, true paragraph."""
    for ms in ("alexandrinus", "vaticanus", "bezae", "washingtonianus"):
        for p in sorted(PUB.glob(f"verified-{ms}-*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            intro = d["introduction"]
            m = STALE_NUM.search(intro)
            if not m or "<strong>Numbering:</strong> The transcription follows" not in intro:
                continue
            intro = STALE_NUM.sub("", intro)
            intro = intro.replace("<strong>Numbering:</strong> The transcription follows",
                                  f"<strong>Numbering:</strong> The transcription and Tischendorf's comparison text "
                                  f"({m.group(1)} verses; the KJV has {m.group(2)}) both follow", 1)
            d["introduction"] = intro
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
            log(d["id"], "two contradictory Numbering paragraphs merged into one")


def fix_alexandrinus():
    d = load("verified-alexandrinus-matt-25")
    if partial(d, 6, "the beginning of this verse is lost with the missing leaves; fol. 26r begins here",
               "go ye out to meet him.", "And at midnight there was a cry made, Behold, the bridegroom cometh;",
               "start", "is lost with the missing leaves at the start of the codex"):
        d["introduction"] = para(d["introduction"], "Manuscript note",
            "The first surviving page of the codex, fol. 26r, begins inside Matthew 25:6 (εξερχεσθε εις απαντησιν "
            "αυτου); the first part of the verse is lost with the leaves before it, and is marked in both columns.")
        d["verification"]["verses_partly_preserved"] = "6"
        save(d)
    d = load("verified-alexandrinus-john-6")
    if partial(d, 50, "the rest of this verse is lost with the missing leaves (John 6:50-8:52)",
               "This is the bread which cometh down from heaven,", "that a man may eat thereof, and not die.",
               "end", "is lost with the missing leaves"):
        d["introduction"] = para(d["introduction"], "Manuscript note",
            "Fol. 70v ends inside John 6:50 (ο εκ του ουνου καταβαινων); the rest of 6:50 and 6:51-71 are lost with the "
            "missing leaves (the codex resumes at 8:52). The partly preserved verse is marked in both columns.")
        d["verification"]["verses_partly_preserved"] = "50"
        save(d)
    d = load("verified-alexandrinus-2cor-4")
    if partial(d, 13, "the rest of this verse is lost with the missing leaves (2 Corinthians 4:13-12:6)",
               "We having the same spirit of faith, according as it is written,",
               "I believed, and therefore have I spoken; we also believe, and therefore speak;",
               "end", "is lost with the missing leaves"):
        d["introduction"] = para(d["introduction"], "Manuscript note",
            "Fol. 126v ends inside 2 Corinthians 4:13 (κατα το γεγραμμε[νον]); the rest of the chapter is lost with the "
            "missing leaves (the codex resumes in 12:6). The partly preserved verse is marked in both columns.")
        d["verification"]["verses_partly_preserved"] = "13"
        save(d)
    d = load("verified-alexandrinus-1john-5")
    if "Johannine Comma" not in d["introduction"]:
        d["introduction"] = para(d["introduction"], "Reading differences",
            "Two places where the KJV has words that this codex does not. In verse 3 the codex has only \"and his "
            "commandments are not grievous\" (και αι εντολαι αυτου βαριαι ουκ εισιν): the scribe's eye passed from "
            "τηρωμεν at the end of verse 2 to the same word in verse 3, so \"For this is the love of God, that we keep "
            "his commandments\" is not written. In verses 7-8 the codex reads \"for there are three that bear witness, "
            "the spirit and the water and the blood, and the three agree in one\" (οτι τρεις εισιν οι μαρτυρουντες · "
            "το πνα και το υδωρ και το αιμα ...); the KJV words \"in heaven, the Father, the Word, and the Holy Ghost: "
            "and these three are one. And there are three that bear witness in earth\" (the Johannine Comma) are not in "
            "this manuscript. The English column gives the KJV unchanged.")
        save(d)
        log(d["id"], "note on 5:3 (homoeoteleuton) and the Johannine Comma (5:7-8), neither in the codex")


# ---------------------------------------------------------------------------
# Codex Bezae
# ---------------------------------------------------------------------------
BEZAE_GAPS = ("<p><strong>What survives and what is shown:</strong> Codex Bezae has lost leaves. In the Greek pages "
              "Matthew 1:1-20 (to μη φοβηθης), 6:20-9:2, 27:2-12 and John 1:16-3:26 are missing in whole or in part: "
              "Matthew 1:20, 6:20, 9:2, 27:12, John 1:16 and 3:26 survive only in part, and Matthew 27:2 only as a torn "
              "fragment. The surviving part of each edge verse is marked in both columns, and the verses in between are "
              "not shown. A few leaves were replaced by a later scribe; pages from these supplementary leaves are marked "
              "\"supplement\". This library so far shows only Matthew and John from the codex; its Mark, Luke and Acts "
              "are not included.</p>")


def fix_bezae():
    n = 0
    for p in sorted(PUB.glob("verified-bezae-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if "What survives and what is shown" in d["introduction"]:
            continue
        d["introduction"] += BEZAE_GAPS
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        n += 1
    if n:
        LOG.append(f"Bezae: lacunae and coverage paragraph added to {n} introductions")
    edges = [
        ("verified-bezae-matt-6", 20, "end", "But lay up for yourselves treasures in heaven,",
         "where neither moth nor rust doth corrupt, and where thieves do not break through nor steal:",
         "the rest of this verse is lost with the missing leaves (Matthew 6:20-9:2)"),
        ("verified-bezae-matt-9", 2, "start",
         "and Jesus seeing their faith said unto the sick of the palsy; Son, be of good cheer; thy sins be forgiven thee.",
         "And, behold, they brought to him a man sick of the palsy, lying on a bed:",
         "the beginning of this verse is lost with the missing leaves (Matthew 6:20-9:2)"),
        ("verified-bezae-matt-27", 12, "start", "he answered nothing.",
         "And when he was accused of the chief priests and elders,",
         "the beginning of this verse is lost with the missing leaves (Matthew 27:2-12)"),
        ("verified-bezae-john-1", 16, "end", "And of his fulness have all we", "received, and grace for grace.",
         "the rest of this verse is lost with the missing leaves (John 1:16-3:26)"),
        ("verified-bezae-john-3", 26, "start",
         "Rabbi, he that was with thee beyond Jordan, to whom thou barest witness, behold, the same baptizeth, and all men come to him.",
         "And they came unto John, and said unto him,",
         "the beginning of this verse is lost with the missing leaves (John 1:16-3:26)"),
    ]
    for eid, v, where, keep, lost, gmark in edges:
        d = load(eid)
        reason = "is lost with the missing leaves"
        if partial(d, v, gmark, keep, lost, where, reason):
            vv = d["verification"]
            vv["verses_partly_preserved"] = str(v)
            save(d)
    # Matthew 1:20: Tischendorf fallback entry; fol. 3v begins inside the verse
    d = load("verified-bezae-matt-1")
    s = sec(d, "1.20-25")
    g = get_verse(s["original_text"], 20)
    if "<em>[" not in g:
        start = "παραλαβεῖν Μαρίαμ"
        i = g.find(start)
        assert i > 0, g
        s["original_text"] = set_verse(s["original_text"], 20,
            "<em>[the first part of this verse, to μὴ φοβηθῇς, is lost with the missing leaves; fol. 3v begins with "
            "παραλαβειν]</em> " + g[i:])
        e = get_verse(s["text"], 20)
        lost = "But while he thought on these things, behold, the angel of the Lord appeared unto him in a dream, saying, Joseph, thou son of David, fear not"
        keep = e[e.find("to take unto thee"):]
        assert e.startswith(lost), e
        s["text"] = set_verse(s["text"], 20, f"<em>[The beginning of this verse, \"{lost}\", is lost with the missing "
                                             f"leaves.]</em> {keep}")
        s["scan_note"] = (s.get("scan_note", "").rstrip(".") + ". Checked on the image: fol. 3v line 1 reads ΠΑΡΑΛΑΒΕΙΝ "
                          "ΜΑΡΙΑΜ ΤΗΝ ΓΥΝΑΙΚΑ ϹΟΥ, inside 1:20; the start of the verse was on a lost leaf.").lstrip(". ")
        d["verification"]["verses_partly_preserved"] = "20"
        save(d)
        log(d["id"], "1:20 starts mid-verse on fol. 3v: lost part marked in Greek (Tischendorf) and English")


# ---------------------------------------------------------------------------
# Codex Washingtonianus
# ---------------------------------------------------------------------------
P0211 = "washingtonianus/w-p0211-FS-7148_01.jpg"
P0212 = "washingtonianus/w-p0212-FS-7148_02.jpg"
P0302 = "washingtonianus/w-p0302-FS-7157_02.jpg"


def page_used(fname, fid, verses):
    n = int(re.search(r"w-p(\d{4})", fname).group(1))
    return {"csntm_image": f"GA_032_{n:04d}.jpg", "freer_id": fid,
            "freer_iiif": f"https://ids.si.edu/ids/iiif/{fid}/full/1800,/0/default.jpg",
            "verses_in_this_chapter": verses}


def fix_w_luke_3():
    d = load("verified-washingtonianus-luke-3")
    if sec(d, "3.24-38"):
        return
    old = [sec(d, x) for x in ("3.17-24", "3.25-32", "3.33-38")]
    g, e = {}, {}
    for s in old:
        for n, t in re.findall(r"<sup>(\d+)</sup>((?:(?!<sup>).)*)", s["original_text"], re.S):
            g[int(n)] = t.strip()
        for n, t in re.findall(r"<sup>(\d+)</sup>((?:(?!<sup>).)*)", s["text"], re.S):
            e[int(n)] = t.strip()
    assert g[23].endswith("Ἰωσὴφ τοῦ Ἡλεὶ"), g[23]
    g23 = g[23][:-len(" τοῦ Ἡλεὶ")] + (" <em>[Tischendorf continues τοῦ Ἡλεὶ; the codex stops after ιωσηφ and goes "
                                       "straight on to 4:1]</em>")
    keep23 = "And Jesus himself began to be about thirty years of age, being (as was supposed) the son of Joseph,"
    assert re.sub(r"\s+", " ", e[23]).startswith(keep23), e[23]
    e23 = keep23 + " <em>[the rest of this verse, \"which was the son of Heli,\", and verses 24-38 are not in Codex Washingtonianus]</em>"
    first = {"section": "3.17-23", "original_ref": "Luke 3:17-23",
             "original_text": " ".join(f"<sup>{v}</sup>{g23 if v == 23 else g[v]}" for v in range(17, 24)),
             "text": " ".join(f"<sup>{v}</sup>{e23 if v == 23 else e[v]}" for v in range(17, 24)),
             "scan_pages": [P0211], "scan_folios": ["GA_032_0211 = Freer FS-7148_01"],
             "scan_note": ("Page from the CSNTM verse index: verses 17-23 on GA_032_0211 (Freer FS-7148_01). Checked on the "
                           "image: the page has 30 lines; line 26 ends ως ενομειζετο ιωσηφ (3:23) and line 27 begins "
                           "ις δε πληρης πνς αγιου (4:1).")}
    gen = {"section": "3.24-38", "original_ref": "Luke 3:24-38",
           "original_text": " ".join(f"<sup>{v}</sup><em>[not in Codex Washingtonianus]</em>" for v in range(24, 39)),
           "text": " ".join(f"<sup>{v}</sup>{e[v]}" for v in range(24, 39)),
           "edition_text": " ".join(f"<sup>{v}</sup>{g[v]}" for v in range(24, 39)),
           "scan_pages": [P0211], "scan_folios": ["GA_032_0211 = Freer FS-7148_01"],
           "scan_note": ("Not in the codex. Checked on the image: on GA_032_0211 (Freer FS-7148_01) 3:23 ends at line 26 "
                         "with ιωσηφ and line 27 begins 4:1 (ις δε πληρης πνς αγιου); the genealogy of 3:23b-38 is not "
                         "written. The CSNTM index lists 3:16-38 for this page, which is not what the page shows. "
                         "Tischendorf's text of these verses is under Compare.")}
    keep = [s for s in d["translation"] if s["section"] not in ("3.17-24", "3.25-32", "3.33-38")]
    d["translation"] = keep + [first, gen]
    v = d["verification"]
    v["scan_pages_used"][P0211]["verses_in_this_chapter"] = "16-23"
    v["verses_absent_from_codex"] = "24-38"
    v["verses_not_in_manuscript"] = "24-38"
    v["verses_partly_preserved"] = "23"
    d["introduction"] = para(d["introduction"], "Manuscript note",
        "Codex Washingtonianus does not have the genealogy of Jesus. On its page GA_032_0211, Luke 3:23 stops after "
        "\"being (as was supposed) the son of Joseph\" (ως ενομειζετο ιωσηφ) and the next line begins 4:1. Not written in "
        "Codex Washingtonianus: the end of 3:23 and verses 3:24-38. The English is shown with the note [not in Codex "
        "Washingtonianus] in the Greek column, and Tischendorf's text of these verses is under Compare. (The CSNTM verse "
        "index, from which the pages of this chapter were taken, lists 3:16-38 for that page; the photograph shows "
        "otherwise.)")
    save(d)
    log(d["id"], "3:23b-38 flagged as not in the codex (checked on p0211); sections 3.17-23 + 3.24-38")


def fix_w_luke_4():
    d = load("verified-washingtonianus-luke-4")
    if sec(d, "4.1-11"):
        return
    s = sec(d, "4.2-11")
    g1, e1 = tisch(42, 4, 1), kjv("luke", 4, 1)
    s["section"], s["original_ref"] = "4.1-11", "Luke 4:1-11"
    s["original_text"] = f"<sup>1</sup>{g1} " + s["original_text"]
    s["text"] = f"<sup>1</sup>{e1} " + s["text"]
    s["scan_pages"] = [P0211, P0212]
    s["scan_folios"] = ["GA_032_0211 = Freer FS-7148_01", "GA_032_0212 = Freer FS-7148_02"]
    s["scan_note"] = ("Verse 1 and the start of verse 2 on GA_032_0211 (Freer FS-7148_01), checked on the image: lines 27-28 "
                      "ις δε πληρης πνς αγιου υπεστρεψεν απο του ιορδανου ..., lines 29-30 ημερας μ πειραζομενος υπο του "
                      "διαβολου (4:2a). Verses 2-11 on GA_032_0212 (Freer FS-7148_02), from the CSNTM verse index. "
                      "Luke 4:1 is not in that index; it was placed by reading the page.")
    v = d["verification"]
    v["scan_pages_used"] = {P0211: page_used(P0211, "FS-7148_01", "1-2"), **v["scan_pages_used"]}
    v["verses_not_shown_index_gap"] = ""
    v["verses_placed_by_reading_image"] = "1"
    v["scan_local_paths"] = [P0211] + [x for x in v.get("scan_local_paths", []) if x != P0211]
    d["introduction"] = re.sub(r"<p>Not shown: Luke 4:1\..*?</p>", "", d["introduction"], flags=re.S)
    d["introduction"] = para(d["introduction"], "Page check",
        "Luke 4:1, which the CSNTM verse index does not list, was read on the photograph of GA_032_0211 (lines 27-28), "
        "and 4:2 begins on the last two lines of the same page; both pages are shown with the first section.")
    save(d)
    log(d["id"], "4:1 added (read on p0211) and p0211 added to the section with 4:2")


def fix_w_luke_23():
    d = load("verified-washingtonianus-luke-23")
    if sec(d, "23.1"):
        return
    new = {"section": "23.1", "original_ref": "Luke 23:1",
           "original_text": f"<sup>1</sup>{tisch(42, 23, 1)}", "text": f"<sup>1</sup>{kjv('luke', 23, 1)}",
           "scan_pages": [P0302], "scan_folios": ["GA_032_0302 = Freer FS-7157_02"],
           "scan_note": ("Checked on the image: the last three lines of GA_032_0302 (Freer FS-7157_02) read και αναστα(ν) απαν "
                         "το πληθος αυτων ηγαγον αυτον επι τον πειλατον (23:1); GA_032_0303 begins with 23:2 (ηρξαντο δε "
                         "κατηγορειν). Luke 23:1 is not in the CSNTM verse index; it was placed by reading the page.")}
    d["translation"].insert(0, new)
    v = d["verification"]
    v["scan_pages_used"] = {P0302: page_used(P0302, "FS-7157_02", "1"), **v["scan_pages_used"]}
    v["verses_not_shown_index_gap"] = ""
    v["verses_placed_by_reading_image"] = "1"
    v["scan_local_paths"] = [P0302] + [x for x in v.get("scan_local_paths", []) if x != P0302]
    d["introduction"] = re.sub(r"<p>Not shown: Luke 23:1\..*?</p>", "", d["introduction"], flags=re.S)
    d["introduction"] = para(d["introduction"], "Page check",
        "Luke 23:1, which the CSNTM verse index does not list, was read on the photograph: it fills the last three lines "
        "of GA_032_0302, and the next page begins with 23:2.")
    save(d)
    log(d["id"], "23:1 added (read at the foot of p0302)")


GOODSPEED = ("\"And they made excuse, saying, This age of lawlessness and unbelief is under Satan, who, by the unclean "
             "spirits, does not allow (sc. \"us\") power to comprehend the truth of God,\" etc.")


def fix_w_mark_16():
    d = load("verified-washingtonianus-mark-16")
    s = sec(d, "16.13-17")
    if "[Freer Logion:]" in s["original_text"]:
        return
    s["original_text"], _ = sub_once(s["original_text"], "ουκ επιστευσαν κακεινοι απελογουντε",
                                     "ουκ επιστευσαν <em>[Freer Logion:]</em> κακεινοι απελογουντε")
    s["original_text"], _ = sub_once(s["original_text"], "δοξαν κληρονομησωσιν <sup>15</sup>",
                                     "δοξαν κληρονομησωσιν <em>[end of the Freer Logion]</em> <sup>15</sup>")
    s["text"], _ = sub_once(s["text"], "after he was risen. <sup>15</sup>",
                            "after he was risen. <em>[Here the codex adds the Freer Logion, which has no counterpart in "
                            "the KJV; no complete public-domain English translation of it was found (see the "
                            "introduction).]</em> <sup>15</sup>")
    intro = re.sub(r"<p>The Freer Logion: on the page carrying 16:14.*?</p>", "", d["introduction"], flags=re.S)
    intro = re.sub(r"<p><strong>Manuscript note:</strong> After verse 14 the codex carries the Freer Logion.*?</p>", "",
                   intro, flags=re.S)
    d["introduction"] = para(intro, "The Freer Logion",
        "after 16:14 the codex adds a passage found in no other manuscript, in which the disciples excuse their unbelief "
        "and Christ replies that the term of Satan's power is fulfilled. The Greek column gives it inside verse 14, "
        "between the markers [Freer Logion:] and [end of the Freer Logion]; it is on page GA_032_0373. The KJV has no "
        "English for it, and no complete public-domain English translation was found: H. A. Sanders' study of the "
        "codex (The Washington Manuscript of the Four Gospels, 1912) gives the Greek only. The one public-domain rendering located covers only the first sentence, "
        "made by E. J. Goodspeed from his own corrected Greek (\"The Detroit Manuscripts of the Septuagint and New "
        f"Testament\", The Biblical World 31, 1908, p. 226): {GOODSPEED}")
    save(d)
    log(d["id"], "Freer Logion marked in the Greek, English column note, stale intro paragraph replaced")


OVERLINE_NOTE = (" A stroke ¯ after a letter (for example μενω¯, το¯) is the scribe's abbreviation for a final ν, "
                 "kept as the transcription gives it.")


def fix_w_overline():
    n = 0
    for p in sorted(PUB.glob("verified-washingtonianus-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if not any("¯" in s.get("original_text", "") for s in d["translation"]):
            continue
        if "abbreviation for a final ν" in d["introduction"] or \
                "the overline is not reproduced)." not in d["introduction"]:
            continue
        intro, ch = sub_once(d["introduction"], "the overline is not reproduced).",
                             "the overline is not reproduced)." + OVERLINE_NOTE)
        if ch:
            d["introduction"] = intro
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
            n += 1
    if n:
        LOG.append(f"Washingtonianus: the ¯ (final-nu stroke) explained in {n} introductions")


def fix_w_scan_notes():
    """W Matthew and Luke sections without a scan_note: state the page(s) of
    the section's verses as the CSNTM verse index gives them."""
    n = 0
    for p in sorted(PUB.glob("verified-washingtonianus-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        used = d["verification"].get("scan_pages_used") or {}
        enclosed = set()
        for part in (d["verification"].get("verses_placed_by_enclosure") or "").split(","):
            if part.strip():
                a, _, b = part.strip().partition("-")
                enclosed |= set(range(int(a), int(b or a) + 1))
        changed = False
        for s in d["translation"]:
            if s.get("scan_note"):
                continue
            vs = [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s["text"])]
            bits = []
            for f in s["scan_pages"]:
                u = used.get(f, {})
                rng = set()
                for part in (u.get("verses_in_this_chapter") or "").split(","):
                    if part.strip():
                        a, _, b = part.strip().partition("-")
                        rng |= set(range(int(a), int(b or a) + 1))
                on = [v for v in vs if v in rng]
                pg = re.search(r"w-p(\d{4})", f).group(1)
                lab = f"GA_032_{pg} (Freer {u.get('freer_id', '')})"
                if on:
                    r = f"{on[0]}-{on[-1]}" if len(on) > 1 else str(on[0])
                    bits.append(f"verse{'s' if len(on) > 1 else ''} {r} on {lab}")
                else:
                    bits.append(f"page {lab}")
            note = "Page from the CSNTM verse index for GA 032 (the page or pages that index gives for each verse): " + "; ".join(bits) + "."
            enc = [v for v in vs if v in enclosed]
            if enc:
                note += (f" Verse{'s' if len(enc) > 1 else ''} {', '.join(map(str, enc))} {'are' if len(enc) > 1 else 'is'} "
                         f"not in the index and {'stand' if len(enc) > 1 else 'stands'} between verses on the same page.")
            s["scan_note"] = note
            changed = True
            n += 1
        if changed:
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    if n:
        LOG.append(f"Washingtonianus: scan_note written for {n} sections (CSNTM index pages per verse)")


# ---------------------------------------------------------------------------
# Leningrad Codex, 1QIsa-a
# ---------------------------------------------------------------------------
def fix_leningrad():
    d = load("verified-leningrad-josh-21")
    s = sec(d, "21.33-40")
    if "[not in the Leningrad Codex]" not in s["original_text"]:
        for v in (36, 37):
            s["original_text"] = set_verse(s["original_text"], v, "<em>[not in the Leningrad Codex]</em> ")
        s["scan_note"] = ("Checked on the image: fol. 133v, right-hand column (column 1), line 10 ends מגרשה ערים ארבע "
                          "(21:35) and line 11 begins וממטה גד את עיר (21:38); verses 21:36-37 are not written. Folio from "
                          "the tanach.us LC folio index.")
        d["introduction"] = para(d["introduction"], "Manuscript note",
            "Joshua 21:36-37 (the Levite cities in Reuben: Bezer, Jahazah, Kedemoth and Mephaath) are not in the "
            "Leningrad Codex: on fol. 133v the scribe passes from 21:35 directly to 21:38. UXLC prints the two verses "
            "for continuity of numbering, with its note \"This verse does NOT occur in the Leningrad Codex\"; they are not "
            "shown here. The English is shown with the note [not in the Leningrad Codex] in the Hebrew column.")
        d["verification"]["verses_not_in_manuscript"] = "21:36-37"
        save(d)
        log(d["id"], "21:36-37 flagged as not in the codex (UXLC note X; checked on fol. 133v)")
    old = ("English verse markers give the KJV numbers and each section's KJV range is listed as english_ref.")
    new = ("English verse markers give the KJV numbers, and each section's KJV range is shown at the head of its "
           "English column.")
    n = 0
    for p in sorted(PUB.glob("verified-leningrad-*.json")):
        t = p.read_text(encoding="utf-8")
        if old in t:
            p.write_text(t.replace(old, new), encoding="utf-8")
            n += 1
    if n:
        LOG.append(f"Leningrad: 'listed as english_ref' sentence rewritten in {n} entries (template now renders english_ref)")


def fix_1qisaa():
    d = load("verified-1qisaa-isa-2")
    s = sec(d, "2.9-15")
    if "<sup>10</sup>" in s["original_text"]:
        return
    e = get_verse(s["text"], 9)
    keep, lost = "And the mean man boweth down, and the great man humbleth himself:", "therefore forgive them not."
    assert e.startswith(keep) and lost in e, e
    s["text"] = set_verse(s["text"], 9, f"{keep} <em>[the rest of this verse, \"{lost}\", is not in 1QIsa-a]</em> ")
    s["original_text"], _ = sub_once(s["original_text"], "וישח אדם וישפל איש <sup>11</sup>",
                                     "וישח אדם וישפל איש <em>[the rest of verse 9 is not in the scroll]</em> "
                                     "<sup>10</sup><em>[not in 1QIsa-a]</em> <sup>11</sup>")
    s["scan_note"] = ("Checked on the image: col. II, line 18 reads ... וישח אדם וישפל איש ועיני גבהות אדם: the scroll goes "
                      "from 2:9a straight to 2:11, without 2:9b (ואל תשא להם) and 2:10. Column and lines from the "
                      "transcription.")
    d["introduction"], _ = sub_once(
        d["introduction"],
        "<p><strong>Manuscript note:</strong> KJV verse 2:10 is not present in 1QIsa<sup>a</sup> as transcribed. The English "
        "is shown for reference with no Hebrew beside it; the omission can be checked on the column image.</p>",
        "<p><strong>Manuscript note:</strong> The end of 2:9 (\"therefore forgive them not\") and the whole of 2:10 are not "
        "in 1QIsa<sup>a</sup>: in column II the scribe wrote וישח אדם וישפל איש and went straight on to 2:11. The English "
        "is shown with the missing words marked, and 2:10 has the note [not in 1QIsa-a] in the Hebrew column.</p>")
    v = d["verification"]
    if isinstance(v.get("absent_in_manuscript"), list) and "2:9b" not in v["absent_in_manuscript"]:
        v["absent_in_manuscript"] = ["2:9b"] + v["absent_in_manuscript"]
    save(d)
    log(d["id"], "2:9b and 2:10 flagged (checked on col. II line 18)")


# ---------------------------------------------------------------------------
# Quran, 1 Clement, Josephus
# ---------------------------------------------------------------------------
def fix_quran():
    d = load("verified-parisino-petropolitanus-quran-71")
    s = sec(d, "71.1-7 (fol. 70r)")
    if "word 8 of 71:7" in s["original_ref"]:
        s["original_ref"] = s["original_ref"].replace("page ends at word 8 of 71:7", "page ends at word 9 of 71:7")
        s["scan_note"] = s["scan_note"] + (" Page break checked on the images: fol. 70v line 1 begins واستغشوا, word 10 of "
                                           "71:7, so this page ends with word 9 (اذانهم); the Corpus Coranicum record gives word 8.")
        save(d)
        log(d["id"], "fol. 70r ends at word 9 of 71:7 (heading said 8)")
    d = load("verified-parisino-petropolitanus-quran-3")
    s = sec(d, "3.13-24 (fol. 2v)")
    if "begins at word 15 of 3:13" in s["original_ref"]:
        s["original_ref"] = s["original_ref"].replace("page begins at word 15 of 3:13",
                                                      "page begins at word 14 of 3:13, at the damaged start of line 1")
        s["scan_note"] = s["scan_note"] + (" Page break checked on the images: the last line of fol. 2r ends واخرى, word 13 of "
                                           "3:13, and the right-hand end of line 1 here is damaged; the Corpus Coranicum "
                                           "record gives word 15.")
        save(d)
        log(d["id"], "fol. 2v begins at word 14 of 3:13 (heading said 15)")
    old = "differs orthographically from what is on the folio while conveying the same reading;"
    new = ("differs orthographically from what is on the folio. It usually conveys the same reading, but the codex has some "
           "readings and verse divisions of its own, which can be checked on the folio;")
    n = 0
    for p in sorted(PUB.glob("verified-parisino-petropolitanus-*.json")):
        t = p.read_text(encoding="utf-8")
        if old in t:
            p.write_text(t.replace(old, new), encoding="utf-8")
            n += 1
    if n:
        LOG.append(f"Quran: 'same reading' sentence qualified in {n} introductions")


CLEMENT_NUM = {
    "5": ("Lake's verses 5-6 are Lightfoot's 5, Lake's 7 is Lightfoot's 6"),
    "8": ("Lake's verse 2 is Lightfoot's 2-3 and the start of his 4 (\"and He added also a merciful judgment\"), "
          "Lake's 3 is the rest of Lightfoot's 4, Lake's 4-5 are Lightfoot's 5-6"),
    "15": ("Lake's verses 6-7 are Lightfoot's 6"),
    "18": ("Lake's 3-4 are Lightfoot's 3, Lake's 5-6 his 4, Lake's 7-9 his 5-7, Lake's 10-11 his 8, Lake's 12-13 his "
           "9-10, Lake's 14 and the first sentence of 15 his 11, the rest of Lake's 15 his 12, Lake's 16-17 his 13-14"),
    "44": ("Lake's verses 2-3 are Lightfoot's 2, Lake's 4-6 are Lightfoot's 3-5"),
    "50": ("Lake's verses 2-3 are Lightfoot's 2, Lake's 4-7 are Lightfoot's 3-6"),
}


def fix_clement():
    d = load("verified-clement-1-clement")
    changed = False
    for name, marker, n in (("52", "1Clem 52:4", 4), ("53", "1Clem 53:3", 3)):
        s = sec(d, name)
        if marker in s["text"]:
            s["text"] = re.sub(rf"\s*{re.escape(marker)}\s*", f" <sup>{n}</sup>", s["text"])
            changed = True
            log(d["id"], f"ch. {name}: raw '{marker}' replaced by verse number {n}")
    for name, note in CLEMENT_NUM.items():
        s = sec(d, name)
        tag = " (verse numbers differ: "
        if tag not in s["original_ref"]:
            s["original_ref"] += f"{tag}{note})"
            changed = True
    body = ("Greek verse numbers are Lake's; the English carries the verse numbers of the Lightfoot transcription. "
            "They differ in six chapters, and each of those sections says how in its heading: " +
            "; ".join(f"ch. {k}: {v}" for k, v in CLEMENT_NUM.items()) + ".")
    if "<strong>Numbering:</strong>" not in d["introduction"]:
        d["introduction"] = para(d["introduction"], "Numbering", body)
        changed = True
    if changed:
        save(d)
        log(d["id"], "per-section verse-number correspondences for ch. 5, 8, 15, 18, 44, 50 (heading + Numbering note)")


def fix_josephus():
    d = load("verified-josephus-antiquities-18-63")
    ch = False
    if " That argument was reported widely in October 2026." in d["introduction"]:
        d["introduction"] = d["introduction"].replace(" That argument was reported widely in October 2026.", "")
        ch = True
    s = d["translation"][0]
    bad = " This is the manuscript page shown in the October 2026 news coverage of Schmidt's study."
    if bad in s["scan_note"]:
        s["scan_note"] = s["scan_note"].replace(bad, "")
        ch = True
    if ch:
        save(d)
        log(d["id"], "unsourced 'October 2026 news coverage' statements removed")


def main():
    fix_barnabas_21()
    fix_sinaiticus_2cor_13()
    fix_sinaiticus_intros()
    fix_sinaiticus_john_5()
    fix_magdala()
    fix_sinaiticus_numbering_notes()
    fix_matt_16_2()
    fix_vaticanus_2cor_13()
    fix_vaticanus_mark_16()
    fix_vaticanus_hebrews_9()
    fix_double_numbering()
    fix_alexandrinus()
    fix_bezae()
    fix_w_luke_3()
    fix_w_luke_4()
    fix_w_luke_23()
    fix_w_mark_16()
    fix_w_overline()
    fix_w_scan_notes()
    fix_leningrad()
    fix_1qisaa()
    fix_quran()
    fix_clement()
    fix_josephus()
    fix_small_notes()
    for line in LOG:
        print(" ", line)
    print(f"{len(LOG)} changes")


if __name__ == "__main__":
    main()
