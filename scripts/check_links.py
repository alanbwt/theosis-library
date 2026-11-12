#!/usr/bin/env python3
"""check_links.py — verify every internal link in site/ resolves (file exists; #anchor exists
in the target page; /assets/ files exist). Respects site/_redirects. Exit 1 on any broken link."""
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

redirects = set()
rf = SITE / "_redirects"
if rf.exists():
    for line in rf.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            redirects.add(line.split()[0])

ids_cache = {}


def page_for(path):
    path = unquote(path)
    p = SITE / path.lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    elif p.is_dir():
        p = p / "index.html"
    elif not p.suffix:
        p = p.with_suffix(".html")
    return p


def ids_of(p):
    if p not in ids_cache:
        ids_cache[p] = set(re.findall(r'\sid="([^"]+)"', p.read_text(encoding="utf-8", errors="ignore")))
    return ids_cache[p]


def main():
    broken = defaultdict(list)
    n = 0
    for f in SITE.rglob("*.html"):
        s = f.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'(?:href|src)="(/[^"#?]*)(?:\?[^"#]*)?(#[^"]*)?"', s):
            path, frag = m.group(1), m.group(2)
            if path.startswith("//") or "'" in path or "+" in path:
                continue  # protocol-relative URL or a JavaScript string, not a static link
            n += 1
            if path in redirects or path.rstrip("/") in redirects:
                continue
            target = page_for(path) if not path.startswith(("/assets/", "/css/", "/js/", "/data/")) else SITE / unquote(path).lstrip("/")
            if not target.exists():
                broken[f"missing {path}"].append(str(f.relative_to(SITE)))
                continue
            if frag and len(frag) > 1 and target.suffix == ".html":
                anchor = unquote(frag[1:])
                if anchor not in ids_of(target):
                    broken[f"no anchor {path}{frag}"].append(str(f.relative_to(SITE)))
    for k, v in sorted(broken.items()):
        print(f"BROKEN {k}  (in {len(v)} pages, e.g. {v[0]})")
    print(f"checked {n} internal links; {len(broken)} broken targets")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
