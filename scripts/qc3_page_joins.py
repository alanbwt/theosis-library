#!/usr/bin/env python3
"""
qc3_page_joins.py: repair word breaks where a verse crosses a page in the
NTVMR / IGNTP diplomatic transcriptions used by the Codex Vaticanus, Bezae,
Alexandrinus and Washingtonianus entries (QC review 2026-11-12, defect
"page-join word fusion").

What went wrong in scripts/qc_swap_ntvmr_transcriptions.py
  1. NTVMR splits its transcription into one TEI file per page. When a verse
     runs over a page, the last word of the page is written <w part="I"> and
     the first word of the next page <w part="F">, whether or not one word is
     really divided between the pages. qc_ntvmr_parse.join_parts() treated
     every I/F pair as one divided word and removed the space, so two words
     ran together ("ιουδαςεις", "υψωθηναιτον"). Bezae, written in sense
     lines, almost never divides a word at a page end; Vaticanus does so
     about half the time.
  2. A few NTVMR pages mark only the second half of a divided word (part="F")
     and the two halves were left apart ("ζη τουσιν").
  3. The IGNTP John file for Washingtonianus writes a divided word as one
     <w> with <pb/><cb/> inside. The parser's <w> renderer only marked a
     break when text stood on both sides of a single marker, so a page break
     followed by a column break left the halves apart ("ερ χαιται").

The fix (re-runnable; it only changes text that still has the old form)
  - Every verse that crosses a page is re-read from the cached transcription
    (data/sources/qc-legacy/ntvmr/). For each page join, the last word of the
    first page (w1) and the first word of the next (w2) are tested:
      a. the verse in Tischendorf's 8th edition (the entry's edition_text):
         if it has w1+w2 as one word and not w1 and w2, the halves are one
         word; if it has w1 and w2 and not w1+w2, they are two words;
      b. otherwise a word list built from every Tischendorf verse in these
         entries, the Sinaiticus transcription and every NTVMR/IGNTP word that
         does not touch a page join: w1+w2 attested and a half not attested
         = one word; both halves attested and w1+w2 not = two words; both
         attested = one word only if w1+w2 occurs at least 3 times and more
         often than the rarer half.
    Accents, breathings, case, brackets and dots are ignored for the test.
  - IGNTP: the <w> renderer is patched (in memory only) to mark a divided
    word across any run of page/column markers; the IGNTP markup itself says
    which words are divided, so no word test is needed there.
  - The JSON is changed only inside the verse concerned, and only where the
    old form occurs exactly once in that verse.

Run from the repo root:  python3 -I scripts/qc3_page_joins.py [--dry-run]
"""
import argparse
import collections
import difflib
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import qc_ntvmr_parse as P  # noqa: E402

PUB = ROOT / "translations" / "published"
MSS = {"vaticanus": 20003, "bezae": 20005, "alexandrinus": 20002, "washingtonianus": 20032}
BOOKS = {"matt": 1, "mark": 2, "luke": 3, "john": 4, "acts": 5, "romans": 6, "1cor": 7, "2cor": 8,
         "gal": 9, "eph": 10, "phil": 11, "col": 12, "1thess": 13, "2thess": 14, "1tim": 15,
         "2tim": 16, "titus": 17, "philemon": 18, "hebrews": 19, "james": 20, "1peter": 21,
         "2peter": 22, "1john": 23, "2john": 24, "3john": 25, "jude": 26, "rev": 27}
SUP_RE = re.compile(r"<sup>(\d+)</sup>")


def norm(w):
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    w = w.lower().replace("ς", "σ").replace("ϲ", "σ")
    return re.sub(r"[^α-ω]", "", w)


def merge(w1, w2):
    """The two halves written as one word, brackets merged as the parser does."""
    return (w1 + w2).replace("][", "")


# ---------------------------------------------------------------------------
def load_entries():
    """(ms, book, chapter) -> path, for entries whose Greek is a transcription."""
    out = {}
    for ms in MSS:
        for f in sorted(PUB.glob(f"verified-{ms}-*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            if d["verification"].get("primary_greek") not in ("ntvmr_transcription", "igntp_transcription"):
                continue
            m = re.match(rf"verified-{ms}-([a-z0-9]+)-(\d+)$", d["id"])
            out[(ms, BOOKS[m.group(1)], int(m.group(2)))] = f
    return out


def tisch_by_verse(d):
    """verse -> Tischendorf's words for that verse, in order (normalised)."""
    out = {}
    for s in d["translation"]:
        parts = SUP_RE.split(s.get("edition_text") or "")
        for i in range(1, len(parts), 2):
            out.setdefault(int(parts[i]), []).extend(
                norm(w) for w in re.sub(r"<[^>]+>", " ", parts[i + 1]).split() if norm(w))
    return out


def build_lexicon(parsed):
    lex = collections.Counter()
    for f in glob.glob(str(PUB / "verified-*.json")):
        m = re.search(r"verified-(vaticanus|bezae|alexandrinus|washingtonianus|sinaiticus)-", f)
        if not m:
            continue
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        tisch_primary = d["verification"].get("primary_greek") == "tischendorf"
        for s in d["translation"]:
            flds = ["edition_text"]
            if m.group(1) == "sinaiticus" or tisch_primary:
                flds.append("original_text")
            for fld in flds:
                for w in re.sub(r"<[^>]+>", " ", s.get(fld) or "").replace(">", " ").split():
                    if norm(w):
                        lex[norm(w)] += 1
    for verses in parsed:
        for parts in verses.values():
            for _p, _c, t in parts:
                for w in t.split():
                    if P.JI in w or P.JF in w:
                        continue
                    if norm(w):
                        lex[norm(w)] += 1
    return lex


def decide(w1, w2, tseq, lex):
    """'join' or 'split' (or None when the test cannot tell). tseq: the
    verse's words in Tischendorf, in order."""
    j, n1, n2 = norm(w1 + w2), norm(w1), norm(w2)
    if not (n1 and n2):
        return None
    if tseq:
        tset = set(tseq)
        adjacent = any(a == n1 and b == n2 for a, b in zip(tseq, tseq[1:]))
        if j in tset and not adjacent:
            return "join"
        if adjacent and j not in tset:
            return "split"
        if n1 in tset and n2 in tset:
            return "split"
        # the scribe's spelling often differs from Tischendorf's (ει for ι,
        # ε for αι ...): a close match of the whole word, where a half is not
        # a word of the verse, counts as one word
        # (and matches it better than either half does)
        if len(j) >= 4:
            t = max(tset, key=lambda x: difflib.SequenceMatcher(None, j, x).ratio())
            rj = difflib.SequenceMatcher(None, j, t).ratio()
            if rj >= 0.8 and all(rj > difflib.SequenceMatcher(None, n, t).ratio() for n in (n1, n2)):
                return "join"
    jo, p1, p2 = lex[j], lex[n1], lex[n2]
    if jo and (not p1 or not p2):
        return "join"
    if not jo and p1 and p2:
        return "split"
    if not jo:
        return None
    return "join" if jo >= 3 and jo > min(p1, p2) else "split"


def verse_span(html, v):
    """(start, end) of verse v's text inside an original_text string."""
    m = re.search(rf"<sup>{v}</sup>", html)
    if not m:
        return None
    n = SUP_RE.search(html, m.end())
    return m.end(), (n.start() if n else len(html))


# ---------------------------------------------------------------------------
# IGNTP: patched <w> renderer (in memory)
_orig_render = P.render


def _render_fixed(el, out):
    if P._local(el.tag) != "w":
        return _orig_render(el, out)
    sub = [el.text or ""]
    for c in el:
        P.render(c, sub)
        if c.tail:
            sub.append(c.tail)
    pieces = "".join(sub).split(P.PB)
    for i in range(0, len(pieces), 2):
        pieces[i] = re.sub(r"\s+", "", pieces[i])
    texts = [i for i in range(0, len(pieces), 2) if pieces[i]]
    for a, b in zip(texts, texts[1:]):
        if b > a + 1:  # at least one page/column marker between the two pieces
            pieces[a] += P.JI
            pieces[b] = P.JF + pieces[b]
    word = P.PB.join(pieces)
    if el.get("part") == "I":
        word += P.JI
    elif el.get("part") == "F":
        word = P.JF + word
    out.append(" " + word + " ")


def igntp_changes():
    """[(book, ch, v, old_local, new_local)] for divided words left apart."""
    d = P.CACHE / "igntp-john"
    files = [d / "04_032S.xml", d / "04_032.xml"]
    _p0, old = P.parse_igntp_book(files)
    P.render = _render_fixed
    try:
        _p1, new = P.parse_igntp_book(files)
    finally:
        P.render = _orig_render
    out = []
    for key, parts in new.items():
        tp = [t for _p, _c, t in parts if t]
        for a, b in zip(tp, tp[1:]):
            if a.endswith(P.JI) and b.startswith(P.JF):
                w1, w2 = P.strip_joins(a).split()[-1], P.strip_joins(b).split()[0]
                old_tp = [t for _p, _c, t in old.get(key, []) if t]
                if P.join_parts(old_tp) != P.join_parts(tp):
                    out.append((*key, f"{w1} {w2}", merge(w1, w2)))
    return out


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    entries = load_entries()
    parsed = {ms: P.parse_ntvmr_doc(doc)[1] for ms, doc in MSS.items()}
    lex = build_lexicon(parsed.values())

    planned = collections.defaultdict(list)   # path -> [(v, old, new, why)]
    stats = collections.Counter()
    undecided = []
    for ms, verses in parsed.items():
        for (b, k, v), parts in verses.items():
            path = entries.get((ms, b, k))
            if not path:
                continue
            if ms == "washingtonianus" and b == 4:
                continue  # W John comes from IGNTP (below)
            tp = [t for _p, _c, t in parts if t]
            if len(tp) < 2:
                continue
            for a, bb in zip(tp, tp[1:]):
                mi, mf = a.endswith(P.JI), bb.startswith(P.JF)
                if not (mi or mf):
                    continue
                w1, w2 = P.strip_joins(a).split()[-1], P.strip_joins(bb).split()[0]
                if not norm(w1) or not norm(w2) or "[...]" in (w1 + w2):
                    continue
                current = "join" if (mi and mf) else "split"
                tset = None
                want = decide(w1, w2, tset, lex)
                planned[path].append((v, w1, w2, current, want))
    # attach the verse-level Tischendorf test now that entries are known
    changes = collections.defaultdict(list)
    for path, items in planned.items():
        d = json.loads(path.read_text(encoding="utf-8"))
        tv = tisch_by_verse(d)
        for v, w1, w2, current, _w in items:
            want = decide(w1, w2, tv.get(v), lex)
            if want is None:
                undecided.append((path.stem, v, w1, w2, current))
                continue
            if want == current:
                stats[f"ok ({current})"] += 1
                continue
            old = merge(w1, w2) if current == "join" else f"{w1} {w2}"
            new = f"{w1} {w2}" if want == "split" else merge(w1, w2)
            changes[path].append((v, old, new, f"{current}->{want}"))
    for (b, k, v, old, new) in igntp_changes():
        path = entries.get(("washingtonianus", b, k))
        if path:
            changes[path].append((v, old, new, "igntp split->join"))

    log = []
    for path, items in sorted(changes.items()):
        d = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for v, old, new, why in items:
            done = False
            for s in d["translation"]:
                html = s.get("original_text") or ""
                sp = verse_span(html, v)
                if not sp:
                    continue
                seg = html[sp[0]:sp[1]]
                if seg.count(new) and not seg.count(old):
                    stats["already fixed"] += 1
                    done = True
                    break
                if seg.count(old) == 1:
                    s["original_text"] = html[:sp[0]] + seg.replace(old, new) + html[sp[1]:]
                    stats[why] += 1
                    log.append(f"{path.stem} {v}: '{old}' -> '{new}'")
                    changed = done = True
                    break
            if not done:
                stats["not found in entry"] += 1
                log.append(f"NOT FOUND {path.stem} {v}: '{old}'")
        if changed and not args.dry_run:
            path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    for line in log:
        print(" ", line)
    for u in undecided:
        print("  undecided (left as is):", u)
    by_ms = collections.Counter(l.split()[0].split("-")[1] for l in log if not l.startswith("NOT"))
    print("changes by manuscript:", dict(by_ms))
    print(dict(stats))


if __name__ == "__main__":
    main()
