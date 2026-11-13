#!/usr/bin/env python3
"""build_home.py — regenerate the homepage shelf pills and holdings line from the catalog
(between the HOME:PILLS-STATS markers in site/index.html)."""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collections_lib import ROOT, SHELVES, all_collections  # noqa: E402

PUB = ROOT / "translations" / "published"


def main():
    rows = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))["texts"]
    colls = all_collections(rows)
    n_entries = sum(len(c["rows"]) for c in colls)
    n_sections = 0
    for c in colls:
        for r in c["rows"]:
            p = PUB / f"{r['id']}.json"
            if p.exists():
                n_sections += len(json.loads(p.read_text(encoding="utf-8")).get("translation", []))
    LANG = {"grc": "Greek", "la": "Latin", "hbo": "Hebrew", "he": "Hebrew", "arc": "Aramaic", "akk": "Akkadian",
            "sux": "Sumerian", "egy": "Egyptian", "lzh": "Classical Chinese", "och": "Old Chinese", "gez": "Ge'ez",
            "cop": "Coptic", "sa": "Sanskrit", "ae": "Avestan", "peo": "Old Persian", "obm": "Moabite",
            "phn": "Phoenician", "uga": "Ugaritic", "non": "Old Norse", "ar": "Arabic", "elx": "Elamite", "hit": "Hittite", "pi": "Pali", "pra": "Prakrit", "inc": "Prakrit"}
    langs = set()
    for c in colls:
        code = c.get("original_lang_code")
        lab = LANG.get(code) if code else None
        if not lab:
            lab = re.split(r"[·(/]", c.get("language") or c.get("original_lang_label", ""))[0].strip()
            lab = {"Ancient Greek": "Greek", "Vedic Sanskrit": "Sanskrit"}.get(lab, lab)
        if lab:
            langs.add(lab)
    pills = ['<a href="/library/" class="evidence-pill">All Texts</a>']
    for s in SHELVES:
        if any(c["group"] == s for c in colls):
            anchor = s.lower().replace(" & ", "-").replace(" ", "-")
            pills.append(f'<a href="/library/#{anchor}" class="evidence-pill">{html.escape(s)}</a>')
    block = ("<!-- HOME:PILLS-STATS START -->\n        <div class=\"evidence-pills\">\n          "
             + "\n          ".join(pills)
             + "\n        </div>\n\n        <div class=\"evidence-stats\">\n          "
             + f"<strong>{n_entries:,} entries</strong> · {n_sections:,} sections · {len(colls)} collections · {len(langs)} ancient languages "
             + f"({html.escape(', '.join(sorted(langs)))}) · every section with its original document, original text and English"
             + "\n        </div>\n<!-- HOME:PILLS-STATS END -->")
    p = ROOT / "site" / "index.html"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!-- HOME:PILLS-STATS START -->.*?<!-- HOME:PILLS-STATS END -->", lambda m: block, s, flags=re.S)
    # Featured passages (data/featured.json): quote must appear verbatim in the section's English.
    import build_library
    feats = json.loads((ROOT / "data" / "featured.json").read_text(encoding="utf-8"))["featured"]
    cards = []
    for f in feats:
        pub = json.loads((PUB / f"{f['id']}.json").read_text(encoding="utf-8"))
        secs = [x for x in pub["translation"] if f.get("section") in (None, x["section"])]
        sec = secs[0]
        eng = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sec.get("text", "") + " " + sec.get("original_text", "")))
        if f["quote"] not in eng:
            raise SystemExit(f"featured quote not verbatim in {f['id']} {f.get('section')}: {f['quote']}")
        thumb = build_library.thumb(sec["scan_pages"][0], width=640)
        anchor = "#s" + str(sec["section"]).replace(".", "-").replace(" ", "-") if f.get("section") else ""
        cards.append(f'''          <a href="/library/{f['id']}{anchor}" class="passage-card">
            <div class="card-scan"><img src="{thumb}" alt="" loading="lazy"></div>
            <div class="card-body">
              <div class="card-quote">"{html.escape(f['quote'])}"</div>
              <div class="card-meta">{html.escape(f['meta'])}</div>
              <div class="card-context">{html.escape(f['context'])}</div>
            </div>
          </a>''')
    s = re.sub(r"<!-- HOME:FEATURED START -->.*?<!-- HOME:FEATURED END -->",
               lambda m: "<!-- HOME:FEATURED START -->\n" + "\n".join(cards) + "\n<!-- HOME:FEATURED END -->", s, flags=re.S)
    # Reading paths (data/paths.json), first four plus the compass and the index
    paths = json.loads((ROOT / "data" / "paths.json").read_text(encoding="utf-8"))["paths"]
    pc = [f'''          <a href="/paths/{x['slug']}" class="paths-card">
            <div class="paths-card-label">{html.escape(x['card_label'])}</div>
            <h3>{html.escape(x['title'])}</h3>
            <p>{html.escape(x['description'])}</p>
          </a>''' for x in paths[:5]]
    pc.append('''          <a href="/paths/" class="paths-card">
            <div class="paths-card-label">Browse all</div>
            <h3>All reading paths →</h3>
            <p>Short guided sequences through the library, each step a real section with its photograph, original and English.</p>
          </a>''')
    s = re.sub(r"<!-- HOME:PATHS START -->.*?<!-- HOME:PATHS END -->",
               lambda m: "<!-- HOME:PATHS START -->\n" + "\n".join(pc) + "\n<!-- HOME:PATHS END -->", s, flags=re.S)
    desc = (f"{n_entries:,} ancient primary sources in {len(colls)} collections, from the first Sumerian writing to the New Testament. "
            "Every section pairs a photograph of the original document with the verbatim original-language text and an English translation.")
    short = f"{n_entries:,} ancient primary sources, each with a photograph of the original document, the original language and English."
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(desc) + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(desc) + m.group(2), s, count=1)
    s = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(short) + m.group(2), s, count=1)
    p.write_text(s, encoding="utf-8")

    # About page: holdings, shelf by shelf, generated from the catalog.
    parts = [f"<!-- ABOUT:HOLDINGS START -->\n        <p>{n_entries:,} entries ({n_sections:,} sections) in {len(colls)} collections. "
             "Every section passes the three-criteria rule.</p>"]
    for shelf in SHELVES:
        cs = [c for c in colls if c["group"] == shelf]
        if not cs:
            continue
        parts.append(f"        <h3>{html.escape(shelf)}</h3>\n        <ul>")
        for c in cs:
            n = len(c["rows"])
            src = "; ".join(x for x in (c.get("critical_edition"), c.get("translator_name") and f"English: {c['translator_name']}") if x)
            parts.append(f'          <li><a href="/collections/{c["key"]}"><strong>{html.escape(c["label"])}</strong></a> '
                         f'({n:,} {"entry" if n == 1 else "entries"}). {html.escape(c.get("description", ""))}'
                         + (f' <span class="holdings-src">{html.escape(src)}.</span>' if src else "") + "</li>")
        parts.append("        </ul>")
    parts.append("<!-- ABOUT:HOLDINGS END -->")
    a = ROOT / "site" / "about.html"
    t = a.read_text(encoding="utf-8")
    t = re.sub(r"<!-- ABOUT:HOLDINGS START -->.*?<!-- ABOUT:HOLDINGS END -->", lambda m: "\n".join(parts), t, flags=re.S)
    a.write_text(t, encoding="utf-8")

    # Sources page: one block per registry collection, from its first entry's verification record.
    from collections_lib import load_all
    reg = load_all()
    blocks = ["<!-- SOURCES:COLLECTIONS START -->", "      <section>", "        <h2>Collections added from 2026-11</h2>"]
    for c in colls:
        if c["key"] not in reg or not c["rows"]:
            continue
        pub = PUB / f"{c['rows'][0]['id']}.json"
        v = json.loads(pub.read_text(encoding="utf-8")).get("verification", {}) if pub.exists() else {}
        def li(label, src, lic):
            if not src:
                return ""
            return f"<li><strong>{label}:</strong> {html.escape(src)}" + (f" <em>({html.escape(lic)})</em>" if lic else "") + "</li>"
        blocks.append(f'        <h3><a href="/collections/{c["key"]}">{html.escape(c["label"])}</a></h3>')
        blocks.append(f"        <p>{html.escape(c.get('description', ''))}</p>")
        blocks.append("        <ul>" + li("Images", v.get("scan_source"), v.get("scan_license"))
                      + li("Mapping", v.get("scan_mapping"), "")
                      + li("Original text", v.get("original_text_source"), v.get("original_text_license"))
                      + li("English", v.get("translation_source"), v.get("translation_license")) + "</ul>")
    blocks += ["      </section>", "<!-- SOURCES:COLLECTIONS END -->"]
    sp = ROOT / "site" / "sources" / "index.html"
    t = sp.read_text(encoding="utf-8")
    t = re.sub(r"<!-- SOURCES:COLLECTIONS START -->.*?<!-- SOURCES:COLLECTIONS END -->", lambda m: "\n".join(blocks), t, flags=re.S)
    # "What's Not Here (Yet)": generated from docs/GAPS.md
    gaps = (ROOT / "docs" / "GAPS.md").read_text(encoding="utf-8")
    parts = []
    for block in re.split(r"\n## ", gaps)[1:]:
        title, *lines = block.strip().split("\n")
        items = [l[2:] for l in lines if l.startswith("- ")]
        parts.append(f"        <h3>{html.escape(title)}</h3>\n        <ul>\n" + "\n".join(f"          <li>{html.escape(i)}</li>" for i in items) + "\n        </ul>")
    gap_html = ("      <section>\n        <h2>What's Not Here (Yet)</h2>\n"
                "        <p>A text enters the library only when every section has a photograph of the original document that carries it, "
                "the verbatim original-language text, and a public-domain or openly licensed English translation of the same passage. "
                "These important texts do not yet meet that bar, and why:</p>\n" + "\n".join(parts) + "\n      </section>")
    a = t.index("<h2>What's Not Here (Yet)</h2>")
    start = t.rfind("<section>", 0, a); start = t.rfind("\n", 0, start) + 1
    end = t.index("</section>", a) + len("</section>")
    t = t[:start] + gap_html + t[end:]
    sp.write_text(t, encoding="utf-8")
    print(f"home: {n_entries} entries, {n_sections} sections, {len(colls)} collections, languages: {sorted(langs)}")


if __name__ == "__main__":
    main()
