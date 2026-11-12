#!/usr/bin/env python3
"""
import_daodejing.py - Daodejing (Laozi), all 81 chapters, on the Mawangdui silk manuscripts.

One entry per chapter (received numbering 1-81). Each entry has up to two sections, one per
manuscript witness from Mawangdui Tomb 3 (Changsha, sealed 168 BCE):
    "Mawangdui A"  Laozi A (jia ben), 169 columns, commonly dated before 195 BCE
    "Mawangdui B"  Laozi B (yi ben), 78 columns (each photographed in an upper and a lower half),
                   commonly dated 194-180 BCE
Both manuscripts put the De part (chapters 38-81) before the Dao part (chapters 1-37).

Chain of evidence:
  1. SCAN     Plates of Changsha Mawangdui Han mu jianbo jicheng, vol. 1 (Zhonghua Shuju, 2014):
              Laozi A pp. 95-102, Laozi B pp. 142-149, from the Wikimedia Commons PDF files
                File:長沙馬王堆漢墓簡帛集成 第一冊 老子甲本 圖版.pdf
                File:長沙馬王堆漢墓簡帛集成 第一冊 老子乙本及卷前古佚書襯頁 圖版.pdf
              (public domain on Commons). The embedded JPEGs (902 x 1360 px) are extracted
              unchanged with pdfimages and copied, not re-encoded or upscaled.
  2. TEXT     Diplomatic transcription with Jicheng column numbers from Wikisource (zh), Page
              namespace of the two PDFs (revisions in data/sources/daodejing/wikisource-revisions.json),
              chapter division from the transclusion pages 老子 (帛書甲本) and 老子 (帛書乙本).
              □ = one character lost on the silk. CC BY-SA 4.0.
  3. MAPPING  Chapter -> columns from the transclusion templates; column -> plate from the Page
              number, except three Laozi A edge columns whose plate was corrected after checking the
              images (PLATE_OVERRIDE_A). Every chapter of both witnesses was then checked by eye on the
              plate images; the readings are logged in data/sources/daodejing/visual-checks.tsv and
              written into each section's scan_note.
  4. RECEIVED Wang Bi recension (Huating Zhang edition), main text only, from Wikisource 道德經 (王弼本);
              shown as edition_text because it is the text Legge translated.
  5. ENGLISH  James Legge, The Tao Teh King, Sacred Books of the East 39 (1891), public domain,
              from Project Gutenberg ebook #216 (Legge's paragraph numbers kept as <sup>).

Usage:
    python3 scripts/import_daodejing.py
"""

import csv
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources" / "daodejing"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / "daodejing"
PUB_DIR = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / "daodejing.json"
KEY = "daodejing"
PREFIX = f"verified-{KEY}-"
TODAY = date.today().isoformat()

COMMONS_A = "https://commons.wikimedia.org/wiki/File:%E9%95%B7%E6%B2%99%E9%A6%AC%E7%8E%8B%E5%A0%86%E6%BC%A2%E5%A2%93%E7%B0%A1%E5%B8%9B%E9%9B%86%E6%88%90_%E7%AC%AC%E4%B8%80%E5%86%8A_%E8%80%81%E5%AD%90%E7%94%B2%E6%9C%AC_%E5%9C%96%E7%89%88.pdf"
COMMONS_B = "https://commons.wikimedia.org/wiki/File:%E9%95%B7%E6%B2%99%E9%A6%AC%E7%8E%8B%E5%A0%86%E6%BC%A2%E5%A2%93%E7%B0%A1%E5%B8%9B%E9%9B%86%E6%88%90_%E7%AC%AC%E4%B8%80%E5%86%8A_%E8%80%81%E5%AD%90%E4%B9%99%E6%9C%AC%E5%8F%8A%E5%8D%B7%E5%89%8D%E5%8F%A4%E4%BD%9A%E6%9B%B8%E8%A5%AF%E9%A0%81_%E5%9C%96%E7%89%88.pdf"
WS_A = "https://zh.wikisource.org/wiki/%E8%80%81%E5%AD%90_(%E5%B8%9B%E6%9B%B8%E7%94%B2%E6%9C%AC)"
WS_B = "https://zh.wikisource.org/wiki/%E8%80%81%E5%AD%90_(%E5%B8%9B%E6%9B%B8%E4%B9%99%E6%9C%AC)"
WS_WANGBI = "https://zh.wikisource.org/wiki/%E9%81%93%E5%BE%B7%E7%B6%93_(%E7%8E%8B%E5%BC%BC%E6%9C%AC)"
GUTENBERG = "https://www.gutenberg.org/ebooks/216"

WIT = {
    "A": {"name": "Mawangdui A", "zh": "甲本", "pdf_dir": "a", "first_book_page": 95,
          "transclusion": "ws-老子帛書甲本.wiki", "ws_url": WS_A, "commons": COMMONS_A},
    "B": {"name": "Mawangdui B", "zh": "乙本", "pdf_dir": "b", "first_book_page": 142,
          "transclusion": "ws-老子帛書乙本.wiki", "ws_url": WS_B, "commons": COMMONS_B},
}

# Laozi A columns at plate edges whose image is on a different plate from the Wikisource Page
# split (checked on the images: col 22 "取天下也恆" fragment at the right edge of plate p. 96;
# col 108 "能嬰兒乎∠脩除玄藍能毌疵乎" at the right edge of p. 100; col 130 "皆有餘我獨遺" at the
# right edge of p. 101). Values are PDF page numbers (1 = book p. 95).
PLATE_OVERRIDE_A = {"22": 2, "108": 6, "130": 7}

# Tail titles of Laozi B (character counts of each part); not chapter text.
TAIL_TITLES_B = {"43下-德尾": "《德》三千𠦜一", "78下": "《道》二千四百廿六"}

SEC_RE = re.compile(r'<section begin="([^"]+)"\s*/>(.*?)<section end="\1"\s*/>', re.S)


# ---------------------------------------------------------------- manuscript transcription

def load_pages(tag):
    segs = []
    for i in range(1, 9):
        t = (SRC / "ws-pages" / f"{tag}-{i:02d}.wiki").read_text(encoding="utf-8")
        t = re.sub(r"<noinclude>.*?</noinclude>", "", t, flags=re.S)
        for m in SEC_RE.finditer(t):
            text = re.sub(r"\s+", "", m.group(2))
            assert not re.search(r"[\[\]{}<>|A-Za-z]", text), (tag, i, m.group(1), text)
            segs.append((i, m.group(1), text))
    return segs


def chapters_from_transclusion(tag):
    segs = load_pages(tag)
    by_page = {}
    for s in segs:
        by_page.setdefault(s[0], []).append(s)
    out, order, cur = {}, [], None
    for line in (SRC / WIT[tag]["transclusion"]).read_text(encoding="utf-8").splitlines():
        h = re.match(r"===\s*(\d+)\s*-", line)
        if h:
            cur = int(h.group(1)); out[cur] = []; order.append(cur); continue
        for m in re.finditer(r"\{\{[Tt]ransclude pages\|([^}]*)\}\}", line):
            parts = m.group(1).split("|")
            named = dict(p.split("=", 1) for p in parts if "=" in p)
            pos = [p for p in parts if "=" not in p]
            p1, p2 = (int(named["start"]), int(named["end"])) if "start" in named else (int(pos[1]), int(pos[2]))
            seq = [s for p in range(p1, p2 + 1) for s in by_page[p]]
            labels = [s[1] for s in seq]
            i, j = labels.index(named["fromsection"]), labels.index(named["tosection"])
            out[cur].extend(seq[i:j + 1])
    used = [(s[0], s[1]) for v in out.values() for s in v]
    assert sorted(used) == sorted((s[0], s[1]) for s in segs), f"{tag}: transclusion does not use every column exactly once"
    assert sorted(out) == list(range(1, 82)), tag
    return out, order


def column_of(label):
    return re.match(r"\d+(?:上|下)?", label).group(0)


def plate_of(tag, page, label):
    col = column_of(label)
    if tag == "A" and col in PLATE_OVERRIDE_A:
        return PLATE_OVERRIDE_A[col]
    return page


def plate_file(tag, pdf_page):
    return f"{KEY}/mwd-laozi-{tag.lower()}-p{WIT[tag]['first_book_page'] + pdf_page - 1:03d}.jpg"


def book_page(tag, pdf_page):
    return WIT[tag]["first_book_page"] + pdf_page - 1


def lacuna_html(text):
    return re.sub(r"(□+)", r'<span class="lacuna">\1</span>', html.escape(text, quote=False))


# ---------------------------------------------------------------- received text and English

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_num(s):
    if "十" not in s:
        return CN[s]
    a, b = s.split("十")
    return (CN[a] if a else 1) * 10 + (CN[b] if b else 0)


def wang_bi():
    t = (SRC / "ws-wangbi.wiki").read_text(encoding="utf-8")
    t = t[:t.index("\n=跋")]
    parts = re.split(r"^==([一二三四五六七八九十]+)章==\s*$", t, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        lines = [l for l in parts[i + 1].splitlines()
                 if l.strip() and not l.startswith((":", "=", "{{", "[["))]
        txt = "".join(lines)
        txt = re.sub(r"-\{(.*?)\}-", r"\1", txt)
        txt = re.sub(r"[\s　]+", "", txt)
        assert not re.search(r"[\[\]{}<>|A-Za-z]", txt), (i, txt)
        out[cn_num(parts[i])] = txt
    assert sorted(out) == list(range(1, 82))
    return out


def legge():
    t = (SRC / "gutenberg-216.txt").read_text(encoding="utf-8")
    body = t[t.index("PART 1."):t.index("*** END OF THE PROJECT")]
    body = body.replace("\r\n", "\n")
    blocks = [b.strip("\n") for b in re.split(r"\n[ \t]*\n[ \t]*\n+", body)]
    chapters, expect = {}, 1
    for b in blocks:
        if not b.strip():
            continue
        m = re.match(r"\s*(?:Ch\. )?(\d+)\.\s", b)
        if not m or int(m.group(1)) != expect:
            if b.strip().startswith("PART"):
                continue
            assert expect > 1 and b.strip(), b[:80]
            chapters[expect - 1] += "\n\n" + b   # continuation block inside a chapter
            continue
        chapters[expect] = b[m.end():]
        expect += 1
    assert sorted(chapters) == list(range(1, 82)), sorted(chapters)[-3:]
    out = {}
    for n, txt in chapters.items():
        paras = [p for p in re.split(r"\n[ \t]*\n", txt) if p.strip()]
        html_paras, pending = [], None
        for p in paras:
            pm = re.match(r"\s*(\d+)\.(?:\s+|$)", p)
            num = None
            if pm:
                num, p = pm.group(1), p[pm.end():]
            if not p.strip():
                pending = num
                continue
            num = num or pending
            pending = None
            lines = [l for l in p.split("\n") if l.strip()]
            verse = sum(1 for l in lines if l.startswith("  ")) >= max(1, len(lines) // 2)
            if verse:
                body_html = "<br>".join(html.escape(l.strip(), quote=False) for l in lines)
            else:
                body_html = html.escape(re.sub(r"\s+", " ", " ".join(l.strip() for l in lines)), quote=False)
            html_paras.append(f"<p>{f'<sup>{num}</sup>' if num else ''}{body_html}</p>")
        out[n] = "".join(html_paras)
    assert out[1].startswith("<p><sup>1</sup>The Tao that can be trodden"), out[1][:80]
    assert "Sincere words are not fine" in out[81]
    return out


# ---------------------------------------------------------------- visual checks

def visual_checks():
    out = {}
    with open(SRC / "visual-checks.tsv", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if not row or row[0].startswith("#"):
                continue
            out[(row[0], int(row[1]))] = {"col": row[2], "chars": row[3], "kind": row[4]}
    for w in "AB":
        missing = [c for c in range(1, 82) if (w, c) not in out]
        assert not missing, (w, missing)
    return out


# ---------------------------------------------------------------- build

def fmt_cols(cols):
    if len(cols) == 1:
        return cols[0]
    nums = {re.match(r"\d+", c).group(0) for c in cols}
    if len(nums) == 1:
        return f"{nums.pop()} (上 and 下)"
    return f"{cols[0]} to {cols[-1]}"


def order_note(tag, ch, order):
    i = order.index(ch)
    prev = order[i - 1] if i else None
    if ch == 38:
        return "This chapter opens the manuscript: the De part (chapters 38-81) comes before the Dao part (chapters 1-37)."
    if ch == 1:
        return f"The Dao part of the manuscript begins here, after chapter {prev}, which closes the De part."
    if prev != ch - 1:
        return f"In this manuscript the chapter follows chapter {prev}, not chapter {ch - 1}."
    return ""


def build_section(tag, ch, segs, order, vc, received, english):
    w = WIT[tag]
    lines, plates, cols, tail = [], [], [], None
    for page, label, text in segs:
        if tag == "B" and label in TAIL_TITLES_B:
            assert text == TAIL_TITLES_B[label], (label, text)
            tail = (label, text)
            plates.append(plate_of(tag, page, label))
            continue
        col = column_of(label)
        if not cols or cols[-1] != col:
            cols.append(col)
        lines.append(f"<sup>{col}</sup>{lacuna_html(text)}")
        plates.append(plate_of(tag, page, label))
    plates = sorted(set(plates))
    files = [plate_file(tag, p) for p in plates]
    legible = re.sub(r"[□∠‧﹦○∟]", "", "".join(t for _, l, t in segs if l not in TAIL_TITLES_B))
    assert legible, (tag, ch)
    lost = sum(t.count("□") for _, l, t in segs if l not in TAIL_TITLES_B)

    chk = vc[(tag, ch)]
    if chk["kind"] == "open":
        check = f"Checked on the image: column {chk['col']} reads {chk['chars']} (the opening of this chapter, with the end of the preceding text where shown)."
    elif chk["kind"] == "first":
        check = (f"Checked on the image: column {chk['col']} reads {chk['chars']}. The opening characters of this chapter "
                 "are lost or not readable on this plate image, so these are the first characters that were confirmed.")
    else:
        check = "Checked on the image: " + chk["chars"].replace("(boundary) ", "") + "."
    pages_txt = " and ".join(f"p. {book_page(tag, p)}" for p in plates)
    plural = "s" if len({re.match(r"\d+", c).group(0) for c in cols}) > 1 else ""
    note = [
        f"Laozi {tag} ({w['zh']}), column{plural} {fmt_cols(cols)}, on plate{'s' if len(plates) > 1 else ''} {pages_txt} of "
        "Changsha Mawangdui Han mu jianbo jicheng, vol. 1 (column numbers are printed under each plate; the columns run from right to left"
        + ("; each column of Laozi B is photographed as an upper half (上) and a lower half (下) on facing plates" if tag == "B" else "")
        + ").",
        check,
    ]
    over = [c for c in cols if tag == "A" and c in PLATE_OVERRIDE_A]
    if over:
        note.append(f"Column {', '.join(over)} was located on the image at the edge of plate p. "
                    f"{', '.join(str(book_page(tag, PLATE_OVERRIDE_A[c])) for c in over)}; the Wikisource page split puts it on the neighbouring plate.")
    if tail:
        note.append(f"Column {column_of(tail[0])} then carries the tail title {tail[1]} (the character count of the "
                    f"{'De' if '德' in tail[1] else 'Dao'} part), which is not part of the chapter and is not shown above.")
    on = order_note(tag, ch, order)
    if on:
        note.append(on)
    if lost:
        note.append(f"□ marks a character lost on the silk ({lost} in this section).")
    note.append("Transcription and column numbers: Wikisource " + ("老子 (帛書甲本)" if tag == "A" else "老子 (帛書乙本)")
                + ", which follows the Jicheng column numbering. The English is Legge's translation of the received text, "
                "shown below the silk transcription; the silk wording differs from it in many places, so compare the two Chinese texts for the variants.")
    return {
        "section": w["name"],
        "original_ref": f"Daodejing {ch}; Mawangdui Laozi {tag} ({w['zh']}) col. {fmt_cols(cols)}; Jicheng vol. 1 plate {pages_txt}",
        "original_text": "<br>".join(lines),
        "edition_text": f"<p>{html.escape(received, quote=False)}</p>",
        "text": english,
        "scan_pages": files,
        "scan_note": " ".join(note),
    }, files


def main():
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    # 1. scans: copy the embedded plate JPEGs unchanged
    for tag in "AB":
        for p in range(1, 9):
            src = SRC / "commons" / WIT[tag]["pdf_dir"] / f"p-{p - 1:03d}.jpg"
            dst = ROOT / "site" / "assets" / "scans" / plate_file(tag, p)
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                shutil.copyfile(src, dst)

    received = wang_bi()
    english = legge()
    vc = visual_checks()
    chs = {tag: chapters_from_transclusion(tag) for tag in "AB"}

    rows, all_files = [], set()
    for ch in range(1, 82):
        tid = f"{PREFIX}{ch:02d}"
        sections, files = [], []
        for tag in "AB":
            segs, order = chs[tag][0][ch], chs[tag][1]
            sec, f = build_section(tag, ch, segs, order, vc, received[ch], english[ch])
            sections.append(sec)
            files += [x for x in f if x not in files]
        all_files.update(files)
        desc = (f"Daodejing chapter {ch} as written on the two Mawangdui silk manuscripts of the Laozi (before 168 BCE), "
                f"with Legge's English and the received Chinese text.")
        intro = (
            f"<p>Chapter {ch} of the <em>Daodejing</em> (<em>Laozi</em>), shown on the two oldest nearly complete copies of the work: "
            "the silk manuscripts Laozi A and Laozi B, found in 1973 in Tomb 3 at Mawangdui, Changsha (Hunan), a tomb sealed in 168 BCE. "
            "Laozi A is written in a script between seal and clerical forms and does not avoid the personal name of the Han founder Liu Bang (邦); "
            "it is commonly dated before 195 BCE. Laozi B is in clerical script, avoids 邦, and is commonly dated 194-180 BCE. "
            "Both put the De part (chapters 38-81) before the Dao part (chapters 1-37), and a few chapters stand in a different order from the received text.</p>"
            "<p>Each section gives the silk transcription column by column, with the Jicheng column number before each column "
            "(for Laozi B, 上 and 下 are the upper and lower halves of a column, photographed on facing plates), and links to the plate "
            "that carries those columns. □ marks a lost character; ∠, ‧ and ﹦ are marks written on the silk (﹦ repeats the character before it). "
            "Below the transcription is the received text of the Wang Bi recension, which is the text James Legge translated in 1891; "
            "the silk wording differs from it, most visibly in 恆 for received 常 (the received text avoids the name of Emperor Wen, Liu Heng), "
            "in the frequent final particle 也, and in loan characters such as 胃 for 謂.</p>"
        )
        entry = {
            "id": tid, "slug": tid,
            "title": f"Daodejing, chapter {ch} (Mawangdui silk manuscripts)",
            "language": "Classical Chinese (silk transcription; received text) / English",
            "source": "Mawangdui Laozi A and B silk manuscripts (plates of Changsha Mawangdui Han mu jianbo jicheng vol. 1, via Wikimedia Commons) "
                      "+ Wikisource column transcription + Wang Bi received text (Wikisource) + Legge 1891 English (Project Gutenberg)",
            "description": desc,
            "introduction": intro,
            "translator_notes": [
                "English: James Legge, The Tao Teh King (Sacred Books of the East 39, 1891); Legge's paragraph numbers are kept as superscripts.",
                "Legge translated the received text, not the silk manuscripts. Where the silk wording differs, his English follows the received text shown under the transcription.",
                "Silk transcription: Wikisource Page transcriptions of the Jicheng plates (revisions of 18 October 2026, marked not yet proofread on Wikisource), checked against the plates for each chapter opening.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": "Changsha Mawangdui Han mu jianbo jicheng, vol. 1 (Zhonghua Shuju, 2014), plates pp. 95-102 (Laozi A) and pp. 142-149 (Laozi B), "
                               "from the Wikimedia Commons PDF files " + COMMONS_A + " and " + COMMONS_B,
                "scan_license": "Public domain (Wikimedia Commons; photographic reproduction of a two-dimensional work over 2,000 years old)",
                "scan_manuscript": "Mawangdui Tomb 3, Changsha, Hunan (sealed 168 BCE), silk manuscripts Laozi A (before 195 BCE) and Laozi B (194-180 BCE); Hunan Museum",
                "scan_mapping": "Chapter to column: Wikisource transclusion pages 老子 (帛書甲本) and 老子 (帛書乙本). Column to plate: Jicheng column numbers printed under each plate, "
                                "as carried by the Wikisource Page transcriptions, with three Laozi A edge columns (22, 108, 130) moved to the plate where the image shows them. "
                                "Every chapter of both witnesses was checked by eye on the plates; the readings are in each section's scan_note and in data/sources/daodejing/visual-checks.tsv.",
                "scan_mapping_urls": [WS_A, WS_B, COMMONS_A, COMMONS_B],
                "scan_local_paths": files,
                "original_text_source": "Wikisource (zh) Page transcriptions of the Jicheng plate PDFs, transcluded by chapter as 老子 (帛書甲本) " + WS_A + " and 老子 (帛書乙本) " + WS_B
                                        + "; received text: Wang Bi, Laozi Daodejing zhu (Huating Zhang edition), Wikisource 道德經 (王弼本) " + WS_WANGBI,
                "original_text_license": "Ancient text public domain; Wikisource transcriptions CC BY-SA 4.0",
                "translation_source": "James Legge, The Tao Teh King, or the Tao and its Characteristics, Sacred Books of the East vol. 39 (Oxford, 1891), Project Gutenberg ebook #216 " + GUTENBERG,
                "translation_license": "Public domain (published 1891)",
                "translator": "James Legge (1891)",
                "verified_date": TODAY,
            },
        }
        (PUB_DIR / f"{tid}.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": ch,
            "title": entry["title"], "author_id": "laozi", "language": "Classical Chinese",
            "era": "Axial Age", "tradition": "taoist", "category": "philosophy",
            "date_approx": "4th c. BCE (composition); silk copies before 168 BCE (Mawangdui Tomb 3)", "century": -4,
            "source": entry["source"], "description": desc,
            "themes": ["daodejing", "laozi", "tao", "mawangdui", "silk-manuscript", "chinese", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f, "caption": ("Laozi A" if "-a-" in f else "Laozi B") + f", Jicheng plate p. {int(f[-7:-4])}"} for f in files]},
        })
        print(f"  {tid}: {len(sections)} sections, plates {', '.join(Path(f).stem for f in files)}")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "Daodejing (Mawangdui silk manuscripts)",
            "group": "China",
            "date_sort": -200,
            "author_name": "Laozi (Mawangdui Tomb 3 silk manuscripts, before 168 BCE)",
            "source_url": COMMONS_B,
            "critical_edition": "Changsha Mawangdui Han mu jianbo jicheng (2014) column numbers; Wikisource transcription; Wang Bi received text",
            "translator_name": "James Legge (1891)",
            "original_lang_label": "Classical Chinese · Mawangdui silk transcription",
            "original_lang_code": "lzh",
            "edition_label": "Received text (Wang Bi recension), the text Legge translated",
            "search_terms": "daodejing tao te ching laozi lao tzu mawangdui silk dao de",
            "description": "The Daodejing chapter by chapter on the two Mawangdui silk manuscripts (copied before 168 BCE), "
                           "the oldest nearly complete copies, with the column-by-column transcription, the received Wang Bi text and James Legge's English.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} entries, {len(all_files)} plate images")


if __name__ == "__main__":
    main()
