#!/usr/bin/env python3
"""
qc3_absent_verses.py: make every KJV verse that a New Testament manuscript
does not contain visibly flagged, in one consistent form (QC review
2026-11-12, systemic item 1).

Scope: New Testament entries of Codex Sinaiticus, Vaticanus, Bezae,
Alexandrinus and Washingtonianus whose original_text is the manuscript's own
transcription (verification.primary_greek = csp_transcription,
ntvmr_transcription or igntp_transcription). Entries whose Greek is
Tischendorf's printed edition are outside the test (their Greek is not the
manuscript's text) and are listed in the summary.

For every section the verse numbers in the original (<sup>n</sup>) are
compared with the KJV verse numbers in the English. A KJV verse with no Greek
beside it is a verse the manuscript does not have, unless:
  - the section already says so for the whole section (no verse numbers in
    the original and a "[Not present ...]" / "[not in ...]" note), or
  - the entry's "Numbering:" paragraph explains the difference (verse
    division, not absence); such cases are reported, not changed.
A verse number followed by no letters at all (the transcription has the
number but the scribe wrote nothing; in Codex Sinaiticus this is how the
CSP marks a verse the first scribe left out and a corrector later added) is
also an absent verse. For Sinaiticus the CSP XML (data/sources/
qc-sinaiticus-venetus/sinaiticus_full_v195.xml.gz) is checked for the
corrector's reading, and the flag then says so.
Each absent verse gets "<sup>n</sup><em>[not in Codex X]</em>" in the
original column, in verse order, and the introduction's Manuscript note lists
it (the note is created or extended when it does not already name the verse).
verification.verses_not_in_manuscript records the verses. Sections that
already flag every verse are not touched; the script is re-runnable.

Run from the repo root:  python3 -I scripts/qc3_absent_verses.py [--dry-run]
"""
import argparse
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
NT = ("matt mark luke john acts romans 1cor 2cor gal eph phil col 1thess 2thess 1tim 2tim titus philemon hebrews "
      "james 1peter 2peter 1john 2john 3john jude rev").split()
NAMES = {"sinaiticus": "Codex Sinaiticus", "vaticanus": "Codex Vaticanus", "bezae": "Codex Bezae",
         "alexandrinus": "Codex Alexandrinus", "washingtonianus": "Codex Washingtonianus"}
TRANSCRIPTION = ("csp_transcription", "ntvmr_transcription", "igntp_transcription")
SUP = re.compile(r"<sup>(\d+)</sup>")


def ranges(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


def mentioned(note, ch):
    """Verse numbers of chapter ch named in a Manuscript note ("5:4",
    "16:9-20", "verses 9-20", "verse 37")."""
    out = set()
    for a, b, c in re.findall(r"\b(\d+):(\d+)(?:-(\d+))?", note):
        if int(a) == ch:
            out |= set(range(int(b), int(c or b) + 1))
    for m in re.finditer(r"verses? (\d+(?:-\d+)?(?:(?:, | and )\d+(?:-\d+)?)*)(?![\d:])", note):
        for a, b in re.findall(r"(\d+)(?:-(\d+))?", m.group(1)):
            out |= set(range(int(a), int(b or a) + 1))
    return out


CSP_BOOK = {"matt": "MATT", "mark": "MARK", "luke": "LUKE", "john": "JOHN", "acts": "ACTS", "romans": "ROM",
            "1cor": "1COR", "2cor": "2COR", "gal": "GAL", "eph": "EPH", "phil": "PHIL", "col": "COL",
            "1thess": "1THESS", "2thess": "2THESS", "1tim": "1TIM", "2tim": "2TIM", "titus": "TITUS",
            "philemon": "PHLM", "hebrews": "HEB", "james": "JAS", "1peter": "1PET", "2peter": "2PET",
            "1john": "1JOHN", "2john": "2JOHN", "3john": "3JOHN", "jude": "JUDE", "rev": "REV"}
_CSP = None


def csp_corrected(bk, ch, v):
    """True if the CSP XML has the verse empty in the first hand and supplied
    by a corrector."""
    global _CSP
    if _CSP is None:
        import gzip
        f = ROOT / "data" / "sources" / "qc-sinaiticus-venetus" / "sinaiticus_full_v195.xml.gz"
        _CSP = gzip.open(f, "rt", encoding="utf-8").read() if f.exists() else ""
    m = re.search(rf'<ab xml:id="V-B\d+K{ch}V{v}-\d+-{CSP_BOOK[bk]}" n="{v}">(.*?)</ab>', _CSP, re.S)
    if not m:
        return False
    body = m.group(1)
    orig = re.findall(r'<rdg type="orig" hand="firsthand">(.*?)</rdg>', body, re.S)
    outside = re.sub(r"<app>.*?</app>|<seg[^>]*>.*?</seg>|<note[^>]*>.*?</note>|<pc[^>]*>.*?</pc>", "", body, flags=re.S)
    first_hand_empty = all(not re.sub(r"<[^>]+>|\s", "", o) for o in orig) and not re.sub(r"<[^>]+>|\s|[·˙.:]", "", outside)
    return bool(orig) and first_hand_empty and 'type="corr"' in body


def empty_verses(html):
    out = []
    for m in re.finditer(r"<sup>(\d+)</sup>((?:(?!<sup>).)*)", html, re.S):
        if not re.sub(r"<[^>]+>|\s|[·˙.:,;]", "", m.group(2)):
            out.append(int(m.group(1)))
    return out


def fill_empty(html, v, flag):
    return re.sub(rf"<sup>{v}</sup>\s*(?=<sup>|$)", f"<sup>{v}</sup><em>[{flag}]</em> ", html, count=1).rstrip() \
        if re.search(rf"<sup>{v}</sup>\s*(?:<sup>|$)", html) else html


def insert_flags(html, verses, flag):
    """Insert <sup>v</sup><em>[flag]</em> for each v, before the first verse
    number greater than v (or at the end)."""
    for v in sorted(verses):
        piece = f"<sup>{v}</sup><em>[{flag}]</em> "
        pos = None
        for m in SUP.finditer(html):
            if int(m.group(1)) > v:
                pos = m.start()
                break
        if pos is None:
            html = html.rstrip() + " " + piece.rstrip()
        else:
            html = html[:pos] + piece + html[pos:]
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    stats = collections.Counter()
    skipped_edition = collections.Counter()
    report = []
    for p in sorted(PUB.glob("verified-*.json")):
        m = re.match(r"verified-(sinaiticus|vaticanus|bezae|alexandrinus|washingtonianus)-([a-z0-9]+)-(\d+)$", p.stem)
        if not m or m.group(2) not in NT:
            continue
        ms, bk, ch = m.group(1), m.group(2), int(m.group(3))
        d = json.loads(p.read_text(encoding="utf-8"))
        pg = d["verification"].get("primary_greek")
        if pg not in TRANSCRIPTION:
            skipped_edition[ms] += 1
            continue
        stats["entries checked"] += 1
        name = NAMES[ms]
        flag = f"not in {name}"
        intro = d.get("introduction", "")
        num_para = " ".join(re.findall(r"<p><strong>Numbering:</strong>.*?</p>", intro, flags=re.S))
        added, corrected = [], []
        for s in d["translation"]:
            stats["sections checked"] += 1
            orig = s.get("original_text", "")
            for v in empty_verses(orig):
                fl = flag
                if ms == "sinaiticus" and csp_corrected(bk, ch, v):
                    fl = f"{flag} as first written; a later corrector added it"
                new_orig = fill_empty(orig, v, fl)
                if new_orig != orig:
                    orig = s["original_text"] = new_orig
                    added.append(v)
                    if fl != flag:
                        corrected.append(v)
                    stats["empty verses flagged"] += 1
                    report.append(f"{p.stem} {s['section']}: empty verse {v} flagged ({fl})")
            so = {int(x) for x in SUP.findall(orig)}
            se = [int(x) for x in SUP.findall(s.get("text", ""))]
            missing = [v for v in se if v not in so]
            if not missing:
                continue
            if not so and re.search(r"\[(?:Not present|not in) ", orig, re.I):
                stats["sections already flagged as a whole"] += 1
                continue
            numbered = [v for v in missing if re.search(rf"\b(?:verse |{ch}:){v}\b", num_para)]
            if numbered:
                report.append(f"{p.stem} {s['section']}: KJV {ranges(numbered)} explained by the Numbering note, not changed")
                missing = [v for v in missing if v not in numbered]
            if not missing:
                continue
            s["original_text"] = insert_flags(orig, missing, flag)
            added += missing
            stats["sections given flags"] += 1
            stats["verses flagged"] += len(missing)
            report.append(f"{p.stem} {s['section']}: flagged {ranges(missing)}")
        if not added:
            continue
        vv = d["verification"]
        prev = set()
        for part in (vv.get("verses_not_in_manuscript") or "").split(","):
            part = part.strip()
            if re.fullmatch(r"\d+(-\d+)?", part):
                a, _, b = part.partition("-")
                prev |= set(range(int(a), int(b or a) + 1))
        vv["verses_not_in_manuscript"] = ranges(prev | set(added))
        notes = re.findall(r"<p><strong>Manuscript note:</strong>.*?</p>", intro, flags=re.S)
        named = set()
        for n in notes:
            named |= mentioned(n, ch)
        new = [v for v in added if v not in named]
        sentence = (f"The Greek column marks {'these verses' if len(added) > 1 else 'this verse'} "
                    f"[{flag}] and the English is shown for reference.")
        if new:
            plain = [v for v in new if v not in corrected]
            corr = [v for v in new if v in corrected]
            refs = lambda vs: ", ".join(f"{ch}:{r}" for r in ranges(vs).split(", "))
            parts = []
            if plain:
                parts.append(f"Not written in {name}: {'verses' if len(plain) > 1 else 'verse'} {refs(plain)}. "
                             f"The Greek column marks {'them' if len(plain) > 1 else 'it'} [{flag}] and the English is "
                             f"shown for reference.")
            if corr:
                parts.append(f"Not written by the first scribe of {name}: {'verses' if len(corr) > 1 else 'verse'} "
                             f"{refs(corr)}, which a later corrector supplied; corrections are not shown here. The Greek "
                             f"column marks {'them' if len(corr) > 1 else 'it'} and the English is shown for reference.")
            extra = " ".join(parts)
            if notes:
                intro = intro.replace(notes[0], notes[0][:-4].rstrip() + " " + extra + "</p>", 1)
            else:
                intro += f"<p><strong>Manuscript note:</strong> {extra}</p>"
            stats["Manuscript notes created or extended"] += 1
        else:
            old = "The English is shown for reference with no Greek beside it."
            for n in notes:
                if old in n:
                    intro = intro.replace(n, n.replace(old, sentence), 1)
                    stats["Manuscript notes reworded"] += 1
                    break
        d["introduction"] = intro
        if not args.dry_run:
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in report:
        print(" ", r)
    print("not checked (Greek is Tischendorf's edition, not a transcription):", dict(skipped_edition))
    print(dict(stats))


if __name__ == "__main__":
    main()
