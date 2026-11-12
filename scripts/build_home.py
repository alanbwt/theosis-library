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
    langs = set()
    for c in colls:
        lab = c.get("language") or c.get("original_lang_label", "")
        lab = re.split(r"[·(/]", lab)[0].strip()
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
    sp.write_text(t, encoding="utf-8")
    print(f"home: {n_entries} entries, {n_sections} sections, {len(colls)} collections, languages: {sorted(langs)}")


if __name__ == "__main__":
    main()
