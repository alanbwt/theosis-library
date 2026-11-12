#!/bin/zsh
# Full site build chain. Run from the repo root after any data change.
set -e
cd "$(dirname "$0")/.."
python3 scripts/integrate_collections.py
python3 scripts/build_reading_order.py
python3 scripts/render_verified.py
python3 scripts/build_index.py        # library shelves + collection pages
python3 scripts/build_home.py
[ -f data/paths.json ] && python3 scripts/build_paths.py
python3 scripts/build_search.py
python3 scripts/build_quotes.py
python3 scripts/build_sitemap.py
python3 scripts/check_collection.py --all
python3 scripts/validate_strict.py
python3 scripts/audit_sections.py
echo "build ok: $(find site -type f | wc -l) files, $(du -sh site | cut -f1)"
