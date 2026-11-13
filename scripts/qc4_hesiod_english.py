#!/usr/bin/env python3
"""
qc4_hesiod_english.py - cut Evelyn-White's English for the Hesiod collections (Theogony, Works and
Days, Shield) at the end of his sentences, so that each page's English starts and ends with the same
line as its Greek, or, where his sentence runs across the page break, so that the sentence is given
whole to one page and the section's scan_note states the exact English line range (QC fix
2026-11-12; at most one sentence crosses each break).

Used by scripts/import_hesiod-theogony.py, import_hesiod-works-and-days.py, import_hesiod-shield.py.

Inputs, per poem:
  eng     [(mark, text)] Evelyn-White's prose in Perseus order; mark = the line number Perseus gives
          the block (about every five lines, and at paragraph starts).
  pages   the importer's PAGES (folio, first, last).
  cuts    {folio: (phrase, occurrence, start, prev_end[, mark])}: the page's English begins with the
          sentence that opens with `phrase` (its occurrence in the poem's English, from 0). `start` is
          the first line that sentence renders, `prev_end` the last line rendered by the previous
          page's English (equal to `start` when the sentence break falls inside a line). `mark`
          (default `start`) is the superscript printed before the sentence. A cut whose phrase is
          not at the start of a block splits that block; the part before keeps the block's mark,
          or is joined to the piece before it if the cut has join_before=True (a sixth element).
  splits  [(phrase, occurrence, before_mark, after_mark)]: other places where a Perseus block holds
          the end of one part of the poem and the start of the next (not page breaks).
Every phrase was chosen by reading Evelyn-White against the Greek (see the importers).
"""


def _find(pieces, phrase, occ):
    hits = [(i, p["text"].index(phrase)) for i, p in enumerate(pieces) if phrase in p["text"]]
    if len(hits) <= occ:
        raise SystemExit(f"English phrase not found: {phrase!r} ({occ})")
    return hits[occ]


def cut_english(eng, pages, cuts, splits=(), total=None):
    """Return the list of English pieces: dict(mark, text, start, folio, cut) in reading order.
    start = first line the piece renders; folio = page whose section shows it; cut = the cut tuple
    when the piece begins a page's English."""
    pieces = [{"mark": m, "text": t, "start": m, "cut": None} for m, t in eng]
    for phrase, occ, before_mark, after_mark in splits:
        i, k = _find(pieces, phrase, occ)
        p = pieces[i]
        before, after = p["text"][:k].strip(), p["text"][k:]
        pieces[i:i + 1] = [dict(p, text=before, mark=before_mark, start=before_mark),
                           dict(p, text=after, mark=after_mark, start=after_mark)]
    order = [p["folio"] for p in pages]
    for folio in order[1:]:
        if folio not in cuts:
            raise SystemExit(f"no English cut for the page break before fol. {folio}")
        c = cuts[folio]
        phrase, occ, start, prev_end = c[:4]
        mark = c[4] if len(c) > 4 and c[4] is not None else start
        join_before = len(c) > 5 and c[5]
        i, k = _find(pieces, phrase, occ)
        p = pieces[i]
        new = dict(p, text=p["text"][k:], mark=mark, start=start, cut=(folio,) + tuple(c[:4]))
        before = p["text"][:k].strip()
        if not before:
            pieces[i] = new
        elif join_before:
            pieces[i - 1]["text"] += " " + before
            pieces[i] = new
        else:
            pieces[i:i + 1] = [dict(p, text=before), new]
    cur = order[0]
    seen = [cur]
    for p in pieces:
        if p["cut"]:
            cur = p["cut"][0]
            assert cur == order[len(seen)], f"English cuts out of page order at fol. {cur}"
            seen.append(cur)
        p["folio"] = cur
    assert seen == order, (seen, order)
    # line range rendered by each piece
    for i, p in enumerate(pieces):
        nxt = pieces[i + 1] if i + 1 < len(pieces) else None
        if nxt is None:
            p["end"] = total
        elif nxt["cut"]:
            p["end"] = nxt["cut"][4]
        else:
            p["end"] = max(p["start"], nxt["start"] - 1)
    return pieces


def _words(text, n=6, last=False):
    w = text.split()
    return " ".join(w[-n:]) if last else " ".join(w[:n])


def english_note(pieces_here, pages, cuts, folio, translator="Evelyn-White"):
    """Sentence(s) for a section's scan_note: exact English line range and how the page breaks were cut."""
    if not pieces_here:
        return ""
    a, b = pieces_here[0]["start"], pieces_here[-1]["end"]
    rng = f"{a}-{b}" if a != b else f"{a}"
    out = [f"English here: lines {rng}, cut at the end of {translator}'s sentences."]
    idx = [p["folio"] for p in pages].index(folio)
    page = pages[idx]
    first = pieces_here[0]
    if first["cut"] and first["cut"][0] == folio:          # this section opens the page's English
        _, phrase, _, start, prev_end = first["cut"]
        F = page["first"]
        if start == F and prev_end == F - 1:
            out.append(f"At the break with the page before, his sentence for line {F} (‹{phrase} ...›) begins with the Greek of this page.")
        elif start < F:
            out.append(f"His sentence ‹{phrase} ...› begins in line {start}, before the page break, and is given whole with this page"
                       + (f" (line {start} holds the end of one sentence and the start of the next)." if prev_end == start else "."))
        else:
            out.append(f"The sentence that runs across the page break (to line {prev_end}) is given whole with the page before; "
                       f"the English here begins with ‹{phrase} ...› (line {start}).")
    last = pieces_here[-1]
    if idx + 1 < len(pages):
        nf = pages[idx + 1]["folio"]
        c = cuts[nf]
        phrase, _, start, prev_end = c[:4]
        F2 = pages[idx + 1]["first"]
        if last["end"] == prev_end and last["folio"] == folio:
            if start == F2 and prev_end == F2 - 1:
                out.append(f"At the break with the next page the English ends with line {prev_end}, the same line as the Greek.")
            elif start < F2:
                out.append(f"His sentence ‹{phrase} ...› begins in line {start}, before the page break, and is given whole with the next page, "
                           f"so the English here ends with line {prev_end}"
                           + (" (the sentence break falls inside that line)." if prev_end == start else "."))
            else:
                out.append(f"His sentence that runs across the break with the next page is given whole here, so the English ends with "
                           f"line {prev_end} (‹... {_words(last['text'], 5, last=True)}›).")
    return " ".join(out)
