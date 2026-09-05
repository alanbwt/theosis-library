#!/usr/bin/env python3
"""
fix_lxx_psalm_numbering.py — Pair each Codex Sinaiticus (Septuagint) psalm with
the CORRECT King James psalm.

The Septuagint numbers the Psalter differently from the Hebrew/KJV:
  LXX 1-8      = KJV 1-8
  LXX 9        = KJV 9 + 10
  LXX 10-112   = KJV 11-113
  LXX 113      = KJV 114 + 115
  LXX 114      = KJV 116:1-9
  LXX 115      = KJV 116:10-19
  LXX 116-145  = KJV 117-146
  LXX 146      = KJV 147:1-11
  LXX 147      = KJV 147:12-20
  LXX 148-150  = KJV 148-150

The original import paired LXX psalm N with KJV psalm N, so for psalms 10-147
the English shown was a different psalm from the Greek on the folio.

Also aligns verses: the LXX counts superscriptions as numbered verses, so
Greek verse numbers run ahead of the KJV by the length of the title. We pair
Greek verse n with KJV verse n - offset, where offset = (LXX verse count) -
(KJV verse count). Section labels keep LXX (manuscript) numbering; English
superscripts keep KJV numbering, so both remain citable.

Run AFTER fix_sinaiticus_section_folios.py (preserves per-section scans).
"""
import json, re, sys, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "translations" / "published"
DATA = ROOT / "data" / "texts.json"

def kjv_target(lxx):
    if lxx <= 8 or lxx >= 148: return (str(lxx), f"psalms {lxx}", f"Psalm {lxx}")
    if lxx == 9: return ("9-10", "psalms 9:1-10:18", "Psalms 9 and 10")
    if 10 <= lxx <= 112: return (str(lxx + 1), f"psalms {lxx+1}", f"Psalm {lxx+1}")
    if lxx == 113: return ("114-115", "psalms 114:1-115:18", "Psalms 114 and 115")
    if lxx == 114: return ("116:1-9", "psalms 116:1-9", "Psalm 116:1-9")
    if lxx == 115: return ("116:10-19", "psalms 116:10-19", "Psalm 116:10-19")
    if 116 <= lxx <= 145: return (str(lxx + 1), f"psalms {lxx+1}", f"Psalm {lxx+1}")
    if lxx == 146: return ("147:1-11", "psalms 147:1-11", "Psalm 147:1-11")
    if lxx == 147: return ("147:12-20", "psalms 147:12-20", "Psalm 147:12-20")

def fetch_kjv(ref):
    url = f"https://bible-api.com/{urllib.parse.quote(ref)}?translation=kjv"
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TheosisLibrary/1.0"})
            return json.loads(urllib.request.urlopen(req, timeout=20).read())
        except Exception as e:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"KJV fetch failed for {ref}")

def sups_pairs(html):
    """Return list of (verse_num, text) from '<sup>n</sup>text' runs."""
    parts = re.split(r"<sup>(\d+)</sup>", html)
    out = []
    for i in range(1, len(parts), 2):
        out.append((int(parts[i]), parts[i + 1].strip()))
    return out

def process(lxx):
    tgt = kjv_target(lxx)
    if not tgt: return "not affected"
    label, ref, pretty_kjv = tgt
    path = PUB / f"verified-sinaiticus-ps-{lxx}.json"
    if not path.exists(): return "absent"
    d = json.loads(path.read_text(encoding="utf-8"))
    v = d["verification"]
    if v.get("lxx_psalm_numbering_fixed"): return "already fixed"

    greek = []
    for s in d["translation"]:
        greek += sups_pairs(s["original_text"])
    greek_by_num = dict(greek)
    if not greek_by_num: return "FAIL no greek"

    kjv = fetch_kjv(ref)
    verses = kjv.get("verses", [])
    if not verses: return "FAIL no kjv"
    # KJV verse numbering: for split psalms keep book-verse numbers as-is
    kjv_list = [(vv["verse"], (vv["text"] or "").strip()) for vv in verses]
    if label in ("9-10", "114-115"):
        # two KJV psalms: number continuously 1..n for pairing, label with chapter
        kjv_list = [(f"{vv['chapter']}:{vv['verse']}", (vv["text"] or "").strip()) for vv in verses]
        kjv_index = list(range(len(kjv_list)))
    else:
        kjv_index = None

    gnums = sorted(greek_by_num)
    same = (pretty_kjv == f"Psalm {lxx}")
    n_g, n_k = len(gnums), len(kjv_list)
    offset = n_g - n_k  # LXX title verses
    if offset < 0: offset = 0

    # map greek verse index -> kjv entry
    group_size = 5 if n_g <= 20 else 8 if n_g <= 40 else 10
    old_sections = d["translation"]
    def scans_for(nums):
        hits = []
        for os_ in old_sections:
            on = [n for n, _ in sups_pairs(os_["original_text"])]
            if set(on) & set(nums):
                for p in os_.get("scan_pages", []):
                    if p not in hits: hits.append(p)
        return hits or (old_sections[0].get("scan_pages") or [])

    sections = []
    for i in range(0, n_g, group_size):
        nums = gnums[i:i + group_size]
        sv, ev = nums[0], nums[-1]
        ref_lbl = f"{sv}-{ev}" if sv != ev else str(sv)
        greek_text = " ".join(f"<sup>{n}</sup>{greek_by_num[n]}" for n in nums)
        eng_parts = []
        for n in nums:
            j = n - 1 - offset  # 0-based index into kjv_list
            if 0 <= j < n_k:
                kn, kt = kjv_list[j]
                eng_parts.append(f"<sup>{kn}</sup>{kt}")
        english_text = " ".join(eng_parts)
        if not english_text.strip():
            # title-only section (e.g. long superscription): attach the note
            english_text = f"<em>[Superscription: the Septuagint numbers the psalm title as verse{'s' if len(nums)>1 else ''} {ref_lbl}; the KJV prints it unnumbered above verse 1.]</em>"
        sections.append({
            "section": f"{lxx}.{ref_lbl}",
            "original_ref": (f"Psalm {lxx}:{ref_lbl}" if same else f"Psalm {lxx} (LXX) : {ref_lbl}  =  {pretty_kjv} (KJV)"),
            "original_text": greek_text,
            "text": english_text,
            "scan_pages": scans_for(nums),
        })
    d["translation"] = sections
    d["title"] = f"Psalm {lxx}" if same else f"Psalm {lxx} (Septuagint) = {pretty_kjv} (KJV)"
    if offset:
        vnote = (f"Greek verse numbers follow the Septuagint, which counts the superscription as "
                 f"verse{'s 1 and 2' if offset >= 2 else ' 1'}; English verse numbers follow the KJV, "
                 f"so they run {offset} behind the Greek. ")
    else:
        vnote = "Verse numbers align between the Greek and the KJV in this psalm. "
    note = (f"<p><strong>Numbering:</strong> Codex Sinaiticus follows the Septuagint Psalter, in which this is "
            f"Psalm {lxx}. " + ("" if same else f"In the Hebrew and King James numbering the same psalm is {pretty_kjv}. ")
            + vnote +
            "The Greek and English in each section are the same words of the same psalm.</p>")
    d["introduction"] = re.sub(r"<p><strong>Numbering:</strong>.*?</p>", "", d.get("introduction", "")) + note
    d["description"] = re.sub(r"^Psalms chapter \d+\.", f"Psalm {lxx} in the Septuagint numbering ({pretty_kjv} in the KJV).", d.get("description", ""))
    v["lxx_psalm_numbering_fixed"] = True
    v["kjv_psalm"] = label
    v["lxx_title_verse_offset"] = offset
    v["translation_source"] = f"bible-api.com (KJV, {pretty_kjv})"
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

    td = json.loads(DATA.read_text(encoding="utf-8"))
    for t in td["texts"]:
        if t["id"] == d["id"]:
            t["title"] = d["title"]; t["description"] = d["description"]
    DATA.write_text(json.dumps(td, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"ok -> {pretty_kjv}, offset {offset}, {len(sections)} sections"

if __name__ == "__main__":
    targets = [int(a) for a in sys.argv[1:]] or sorted(int(re.search(r"ps-(\d+)", p.name).group(1)) for p in PUB.glob("verified-sinaiticus-ps-*.json"))
    for n in targets:
        print(f"Psalm {n}: {process(n)}", flush=True)
        time.sleep(1.5)
