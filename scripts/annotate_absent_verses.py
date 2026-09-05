#!/usr/bin/env python3
"""
annotate_absent_verses.py — For every Codex Sinaiticus NT chapter whose primary
Greek is the CSP transcription, list KJV verses that have no Greek in the
manuscript (e.g. Acts 8:37, John 5:4, 1 John 5:7) in a "Manuscript note"
paragraph, and record them in verification.absent_in_manuscript.
Re-runnable.
"""
import json, re, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sups(s): return [int(x) for x in re.findall(r"<sup>(\d+)</sup>", s)]
def ranges(ch, nums):
    out = []; start = prev = None
    for n in nums:
        if start is None: start = prev = n
        elif n == prev + 1: prev = n
        else: out.append((start, prev)); start = prev = n
    if start is not None: out.append((start, prev))
    return ", ".join(f"{ch}:{a}" if a == b else f"{ch}:{a}-{b}" for a, b in out)
n = 0
for f in sorted(glob.glob(os.path.join(ROOT, "translations", "published", "verified-sinaiticus-*.json"))):
    d = json.load(open(f, encoding="utf-8")); v = d["verification"]
    if v.get("primary_greek") != "csp_transcription": continue
    m = re.match(r"verified-sinaiticus-([a-z0-9]+)-(\d+)$", d["id"]); ch = m.group(2)
    g, e = set(), set()
    for s in d["translation"]:
        g |= set(sups(s["original_text"])); e |= set(sups(s["text"]))
    absent = sorted(e - g); extra = sorted(g - e)
    d["introduction"] = re.sub(r"<p><strong>Manuscript note:</strong>(?!.*Mark ends).*?</p>", "", d.get("introduction", ""), flags=re.S) if "Mark ends" not in d.get("introduction", "") else d["introduction"]
    if not absent and not extra:
        v.pop("absent_in_manuscript", None)
    else:
        parts = []
        if absent and "Mark ends" not in d["introduction"]:
            refs = ranges(ch, absent)
            parts.append(f"KJV verse{'s' if len(absent)>1 else ''} {refs} {'are' if len(absent)>1 else 'is'} not present in Codex Sinaiticus as transcribed by the Codex Sinaiticus Project. The English is shown for reference with no Greek beside it. Tischendorf's edition reading is available under \"Compare\" for the surrounding verses. This is a genuine difference between the 4th-century manuscript and the later text underlying the KJV, and it can be checked directly on the folio.")
        if extra:
            parts.append(f"Greek verse{'s' if len(extra)>1 else ''} {', '.join(f'{ch}:{x}' for x in extra)} {'have' if len(extra)>1 else 'has'} no KJV counterpart under that number (a verse-division difference, not missing text).")
        if parts:
            d["introduction"] += f"<p><strong>Manuscript note:</strong> {' '.join(parts)}</p>"
        v["absent_in_manuscript"] = [f"{ch}:{x}" for x in absent]
        n += 1
        print(d["id"], "absent:", absent, "extra:", extra)
    for s in d["translation"]:
        if not re.sub(r"<[^>]+>", "", s["original_text"]).strip():
            s["original_text"] = "<em>[Not present in Codex Sinaiticus as transcribed by the Codex Sinaiticus Project. The KJV text is shown for reference; see the folio and the Tischendorf reading under Compare.]</em>"
    SPECIAL = {"verified-sinaiticus-john-21": "John 21:25 was omitted by the first scribe of Codex Sinaiticus and supplied by a corrector (the Codex Sinaiticus Project labels the hand S1); the Greek shown for verse 25 is that corrector's text, visible on the folio. Verse 25 is itself the final verse of the Gospel and one of the most discussed points of the manuscript.",
               "verified-sinaiticus-acts-19": "KJV Acts 19:41 is numbered as part of 19:40 in the Greek, so it has no separate Greek verse here; no text is missing."}
    if d["id"] in SPECIAL and SPECIAL[d["id"]] not in d["introduction"]:
        d["introduction"] += f"<p><strong>Manuscript note:</strong> {SPECIAL[d['id']]}</p>"
    json.dump(d, open(f, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("annotated", n)
