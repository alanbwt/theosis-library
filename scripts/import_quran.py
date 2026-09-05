#!/usr/bin/env python3
"""
import_quran.py — Folio-level Quran import for Theosis Library.

Manuscript: Codex Parisino-petropolitanus, the Paris portion, i.e. BnF Arabe 328
fragments (a) fol. 1-56 and (b) fol. 57-70 (hijazi script, c. 650-750 AD).

Chain of evidence for every section (one section = one folio side):
  1. MAPPING  Corpus Coranicum "Manuscripta Coranica" (Berlin-Brandenburgische
              Akademie der Wissenschaften). Its public JSON API returns, for each
              folio side, the sura:verse:word where the page's text starts and
              ends (standard Kufan / Cairo-edition verse numbering).
                https://api.corpuscoranicum.de/api/data/manuscripts/<id>
                https://api.corpuscoranicum.de/api/data/language/en/manuscripts/<id>/pages/<folio><side>
              Site content is licensed CC BY 3.0 (imprint, corpuscoranicum.de).
  2. SCAN     Gallica IIIF, BnF ark:/12148/btv1b8415207g (Arabe 328). Canvas
              labels are BnF folio numbers ("30v"), the same foliation Corpus
              Coranicum uses. Every downloaded Gallica image is additionally
              compared pixel-wise against the image Corpus Coranicum serves for
              the same folio; a page is rejected if they do not match.
              Terms: "La reutilisation non commerciale de ces contenus est libre
              et gratuite" with the credit "Source gallica.bnf.fr / BnF".
  3. ARABIC   Tanzil Uthmani text v1.1 (tanzil.net), CC BY 3.0, verbatim copy
              required (their terms forbid altering the text; we do not).
  4. ENGLISH  Marmaduke Pickthall, The Meaning of the Glorious Koran (1930),
              verse-indexed file from tanzil.net/trans/en.pickthall. Public
              domain: published 1930 (US term expired 1 Jan 2026); author died
              1936 (life+70 expired 2007).

Usage:
    python3 scripts/import_quran.py --prove 30v      # one folio, print evidence
    python3 scripts/import_quran.py                  # build everything
    python3 scripts/import_quran.py --force          # re-download scans
Writes:
    site/assets/scans/parisino-petropolitanus/pp-f<NN><r|v>.jpg
    translations/published/verified-parisino-petropolitanus-quran-<sura>.json
    data/pending/parisino-petropolitanus_texts.json
    data/sources/quran/  (HTTP cache + folio mapping report)
"""

import argparse
import io
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
MS_NAME = "parisino-petropolitanus"
SCAN_DIR = ROOT / "site" / "assets" / "scans" / MS_NAME
PUB_DIR = ROOT / "translations" / "published"
PENDING = ROOT / "data" / "pending" / f"{MS_NAME}_texts.json"
CACHE = ROOT / "data" / "sources" / "quran"
for d in (SCAN_DIR, PUB_DIR, PENDING.parent, CACHE):
    d.mkdir(parents=True, exist_ok=True)

UA = "TheosisLibrary/1.0 (https://theosislibrary.com; scholarly, non-commercial)"
CC_API = "https://api.corpuscoranicum.de"
CC_MANUSCRIPTS = [13, 157]          # Arabe 328 (a) fol. 1-56, Arabe 328 (b) fol. 57-70
GALLICA_ARK = "ark:/12148/btv1b8415207g"
GALLICA_MANIFEST = f"https://gallica.bnf.fr/iiif/{GALLICA_ARK}/manifest.json"
GALLICA_WIDTH = 1600
TANZIL_UTHMANI = "https://tanzil.net/pub/download/index.php?quranType=uthmani&outType=txt-2&agree=true"
TANZIL_PICKTHALL = "https://tanzil.net/trans/en.pickthall"
POLITE_DELAY = 0.6
MATCH_THRESHOLD = 0.35   # normalised cross-correlation Gallica vs Corpus Coranicum image
TODAY = date.today().isoformat()


# ----------------------------------------------------------------------------
# HTTP with on-disk cache
# ----------------------------------------------------------------------------
def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    try:
        return resp.read()
    finally:
        resp.close()


def cached(url, name, binary=False, force=False):
    p = CACHE / name
    if p.exists() and not force:
        return p.read_bytes() if binary else p.read_text(encoding="utf-8")
    for attempt in range(3):
        try:
            data = http_get(url)
            break
        except Exception as e:  # noqa
            if attempt == 2:
                raise
            print(f"    retry {attempt + 1} for {url}: {e}")
            time.sleep(3)
    time.sleep(POLITE_DELAY)
    p.write_bytes(data)
    return data if binary else data.decode("utf-8")


def cached_json(url, name, force=False):
    return json.loads(cached(url, name, force=force))


# ----------------------------------------------------------------------------
# Text sources
# ----------------------------------------------------------------------------
def load_tanzil(url, name):
    """Parse a Tanzil 'sura|verse|text' file into {(sura, verse): text}."""
    txt = cached(url, name)
    out = {}
    for line in txt.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        out[(int(parts[0]), int(parts[1]))] = parts[2].strip()
    return out


def load_sura_meta():
    d = cached_json(f"{CC_API}/api/init/quran", "cc_init_quran.json")["data"]
    return {s["key"]: {"verses": s["verses"], "name": s["nameTranslit"]} for s in d}


# ----------------------------------------------------------------------------
# Corpus Coranicum mapping
# ----------------------------------------------------------------------------
def cc_manuscript(ms_id):
    return cached_json(f"{CC_API}/api/data/manuscripts/{ms_id}", f"cc_manuscript_{ms_id}.json")["data"]


def cc_page(ms_id, folio, side):
    url = f"{CC_API}/api/data/language/en/manuscripts/{ms_id}/pages/{folio}{side}"
    return cached_json(url, f"cc_page_{ms_id}_{folio}{side}.json")["data"], url


def expand_range(start, end, meta):
    """List (sura, verse) from start to end inclusive across sura boundaries.
    Verse 0 = sura heading / basmala; Tanzil carries the basmala inside verse 1."""
    s_sura, s_verse = start["sura"], max(1, start["verse"])
    e_sura, e_verse = end["sura"], end["verse"]
    if e_verse == 0:                       # page ends on next sura's heading only
        e_sura -= 1
        e_verse = meta[e_sura]["verses"]
    out = []
    sura = s_sura
    while sura <= e_sura:
        first = s_verse if sura == s_sura else 1
        last = e_verse if sura == e_sura else meta[sura]["verses"]
        for v in range(first, last + 1):
            out.append((sura, v))
        sura += 1
    return out


# ----------------------------------------------------------------------------
# Gallica scans + cross-check against Corpus Coranicum image
# ----------------------------------------------------------------------------
def gallica_folio_map():
    man = cached_json(GALLICA_MANIFEST, "gallica_arabe328_manifest.json")
    label_to_service = {}
    for c in man["sequences"][0]["canvases"]:
        lab = c["label"].strip()
        if re.fullmatch(r"\d+[rv]", lab):
            label_to_service[lab] = c["images"][0]["resource"]["service"]["@id"]
    return man, label_to_service


def image_signature(data):
    im = ImageOps.grayscale(Image.open(io.BytesIO(data))).resize((48, 64))
    px = list(im.tobytes())
    n = len(px)
    mean = sum(px) / n
    var = sum((p - mean) ** 2 for p in px) / n
    sd = var ** 0.5 or 1e-9
    return [(p - mean) / sd for p in px]


def correlation(a, b):
    return sum(x * y for x, y in zip(a, b)) / len(a)


def fetch_scan(label, service, cc_image_url, force=False):
    """Download the Gallica image for a folio label; verify against CC image.
    Returns (relative_path, gallica_url, corr)."""
    fname = f"pp-f{label}.jpg"
    dest = SCAN_DIR / fname
    gallica_url = f"{service}/full/{GALLICA_WIDTH},/0/native.jpg"
    if not dest.exists() or dest.stat().st_size < 10000 or force:
        data = None
        for attempt in range(3):
            try:
                data = http_get(gallica_url, timeout=120)
                Image.open(io.BytesIO(data)).verify()
                break
            except Exception as e:  # noqa
                print(f"    gallica retry {attempt + 1} ({label}): {e}")
                time.sleep(4)
        if data is None:
            raise RuntimeError(f"Gallica download failed for {label}")
        dest.write_bytes(data)
        time.sleep(POLITE_DELAY)
    cc_data = cached(cc_image_url, f"cc_image_{label}.jpg", binary=True)
    corr = correlation(image_signature(dest.read_bytes()), image_signature(cc_data))
    return f"{MS_NAME}/{fname}", gallica_url, corr


# ----------------------------------------------------------------------------
# Build the folio table
# ----------------------------------------------------------------------------
def build_folio_table(meta, only=None, force=False):
    _, gmap = gallica_folio_map()
    rows = []
    for ms_id in CC_MANUSCRIPTS:
        ms = cc_manuscript(ms_id)
        for pg in ms["pages"]:
            label = f"{pg['folio']}{pg['side']}"
            if only and label != only:
                continue
            if len(pg["passages"]) != 1:
                print(f"  ! {label}: {len(pg['passages'])} passages, skipping")
                continue
            page, page_url = cc_page(ms_id, pg["folio"], pg["side"])
            imgs = [i for i in page["images"] if "nationale" in (i.get("image_source") or "")] or page["images"]
            if label not in gmap:
                print(f"  ! {label}: no Gallica canvas with that label, skipping")
                continue
            rel, gallica_url, corr = fetch_scan(label, gmap[label], imgs[0]["image_url"], force=force)
            ok = corr >= MATCH_THRESHOLD
            ps = pg["passages"][0]
            rows.append({
                "label": label, "ms_id": ms_id, "call_number": ms["call_number"],
                "page_id": pg["page_id"], "start": ps["start"], "end": ps["end"],
                "verses": expand_range(ps["start"], ps["end"], meta),
                "scan": rel, "gallica_url": gallica_url, "cc_page_url": page_url,
                "cc_image_url": imgs[0]["image_url"], "match_corr": round(corr, 3), "match_ok": ok,
            })
            flag = "" if ok else "  <-- IMAGE MISMATCH, excluded"
            print(f"  {label}: {ps['start']['sura']}:{ps['start']['verse']}.{ps['start']['word']} -> "
                  f"{ps['end']['sura']}:{ps['end']['verse']}.{ps['end']['word']}  corr={corr:.2f}{flag}")
    (CACHE / "folio_mapping_report.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    return rows


# ----------------------------------------------------------------------------
# Entry assembly
# ----------------------------------------------------------------------------
def ref(p):
    return f"{p['sura']}:{p['verse']}"


def intro_html(sura, name, nfolios, lacunae):
    lac = ""
    if lacunae:
        lac = ("<p><strong>Lacunae:</strong> the surviving Paris leaves do not carry every verse of this sura. "
               f"Only the verses listed in the sections below are on the folios shown; the rest of the sura is lost "
               "or preserved in other fragments of the same codex (St Petersburg Marcel 18, Vatican Ar. 1605/1, London KFQ 60) "
               "that are not included here.</p>")
    return (
        f"<p>Sura {sura} (<em>{name}</em>) as preserved on {nfolios} folio side{'s' if nfolios != 1 else ''} of the "
        "<strong>Codex Parisino-petropolitanus</strong> (Paris, BnF Arabe 328 (a) and (b)), one of the oldest surviving "
        "Quran manuscripts, written in hijazi script on parchment, c. 650-750 AD. Each section below is one folio side, "
        "and the image shown is that exact page.</p>"
        "<ol>"
        "<li><strong>Manuscript scan:</strong> the specific folio side from Gallica (Bibliotheque nationale de France IIIF). "
        "The folio's sura:verse range was taken from the Corpus Coranicum \"Manuscripta Coranica\" record for that page, "
        "which states the first and last word on the page; the folio numbers of both services were cross-checked by "
        "comparing the two images pixel by pixel.</li>"
        "<li><strong>Original text:</strong> the Arabic of the Tanzil Project Uthmani text (CC BY 3.0), reproduced unchanged, "
        "verse by verse.</li>"
        "<li><strong>English:</strong> Marmaduke Pickthall, <em>The Meaning of the Glorious Koran</em> (1930), public domain, "
        "verse by verse.</li>"
        "</ol>"
        "<p><strong>Orthography:</strong> the codex is written in <em>scriptio defectiva</em>: no vowel signs, almost no "
        "consonantal dots, long vowels often unwritten, and letter shapes that differ from the printed Uthmani text. The modern "
        "text given here therefore differs orthographically from what is on the folio while conveying the same reading; "
        "readers should expect, for example, the basmala and words such as <em>qala</em> to be spelled with fewer letters "
        "on the page.</p>"
        "<p><strong>Numbering:</strong> verse numbers follow the standard Kufan (Cairo 1924) division used by Corpus Coranicum, "
        "Tanzil and Pickthall. Early codices mark verse ends with ink dots that in places divide the text differently, so a "
        "verse count made on the page may not match these numbers exactly. In Tanzil's text the basmala opening each sura "
        "(except sura 9) is printed as part of verse 1. Where a page begins or ends in the middle of a verse the whole verse "
        "is given and the word position is stated in the section heading.</p>"
        + lac
    )


def build_entries(rows, meta, uth, pick):
    rows = [r for r in rows if r["match_ok"]]
    by_sura = {}
    for r in rows:
        for sura in sorted({s for s, _ in r["verses"]}):
            by_sura.setdefault(sura, []).append(r)

    entries, pending = [], []
    for sura in sorted(by_sura):
        name = meta[sura]["name"]
        sections, covered = [], set()
        for r in by_sura[sura]:
            vs = [v for s, v in r["verses"] if s == sura]
            covered.update(vs)
            orig = " ".join(f"<sup>{v}</sup>{uth[(sura, v)]}" for v in vs)
            eng = " ".join(f"<sup>{v}</sup>{pick[(sura, v)]}" for v in vs)
            st, en = r["start"], r["end"]
            note_bits = []
            if st["sura"] == sura and st["verse"] >= 1 and st["word"] and st["word"] > 1:
                note_bits.append(f"page begins at word {st['word']} of {ref(st)}")
            if en["sura"] == sura and en["verse"] >= 1:
                note_bits.append(f"page ends at word {en['word']} of {ref(en)}")
            if st["sura"] < sura:
                note_bits.append(f"page begins in sura {st['sura']} ({ref(st)})")
            if en["sura"] > sura:
                note_bits.append(f"page continues into sura {en['sura']} ({ref(en)})")
            sections.append({
                "section": f"{sura}.{vs[0]}-{vs[-1]} (fol. {r['label']})",
                "original_ref": f"Quran {sura}:{vs[0]}-{vs[-1]}, BnF Arabe 328 fol. {r['label']}"
                                + (f" ({'; '.join(note_bits)})" if note_bits else ""),
                "original_text": orig,
                "text": eng,
                "scan_pages": [r["scan"]],
                "scan_note": f"Corpus Coranicum page record: {r['cc_page_url']} ; image: {r['gallica_url']}",
            })
        total = meta[sura]["verses"]
        lacunae = len(covered) < total
        tid = f"verified-{MS_NAME}-quran-{sura}"
        title = f"Quran, Sura {sura} ({name}) (Codex Parisino-petropolitanus)"
        scan_paths = sorted({s["scan_pages"][0] for s in sections})
        notes = [
            f"{len(covered)} of {total} verses of this sura survive on the Paris leaves of the codex "
            f"({len(sections)} folio side{'s' if len(sections) != 1 else ''})." if lacunae else
            f"All {total} verses of this sura are present on the Paris leaves ({len(sections)} folio sides).",
            "Corpus Coranicum records the first and last word of each page; a verse split across two pages is shown in full "
            "under both pages with the word position noted.",
        ]
        entry = {
            "id": tid, "title": title, "slug": tid,
            "language": "Arabic (Tanzil Uthmani) / English (Pickthall 1930)",
            "source": "Codex Parisino-petropolitanus (BnF Arabe 328) via Gallica IIIF + Corpus Coranicum folio mapping + Tanzil + Pickthall",
            "description": f"Sura {sura} ({name}) from the Codex Parisino-petropolitanus (c. 650-750 AD), one section per folio side, "
                           f"each linked to the exact Gallica image of that page ({len(sections)} pages).",
            "introduction": intro_html(sura, name, len(sections), lacunae),
            "translator_notes": notes,
            "translation": sections,
            "verification": {
                "scan_source": f"Gallica (BnF) IIIF, {GALLICA_ARK} (Arabe 328), full-page images at {GALLICA_WIDTH}px width",
                "scan_license": "BnF/Gallica conditions d'utilisation: non-commercial reuse free with credit 'Source gallica.bnf.fr / Bibliotheque nationale de France'; commercial reuse requires a BnF licence",
                "scan_manuscript": "Codex Parisino-petropolitanus, Paris portion: BnF Arabe 328 (a) fol. 1-56 and (b) fol. 57-70, hijazi I, c. 650-750 AD",
                "scan_mapping": "Corpus Coranicum / Manuscripta Coranica (BBAW, CC BY 3.0) per-page start and end sura:verse:word; Gallica canvas labels use the same BnF foliation; each Gallica image cross-checked against the Corpus Coranicum image of the same folio (normalised correlation >= 0.35)",
                "scan_mapping_urls": sorted({s["scan_note"].split(" ; ")[0].replace("Corpus Coranicum page record: ", "") for s in sections}),
                "scan_local_paths": scan_paths,
                "original_text_source": "Tanzil Project, Quran Uthmani text v1.1 (tanzil.net)",
                "original_text_license": "CC BY 3.0; Tanzil terms require the text to be reproduced unchanged with attribution and a link to tanzil.net (complied with)",
                "translation_source": "Marmaduke Pickthall, The Meaning of the Glorious Koran (1930), verse-indexed file from tanzil.net/trans/en.pickthall",
                "translation_license": "public domain (published 1930, US term expired 1 Jan 2026; author d. 1936)",
                "verse_numbering": "Kufan / Cairo 1924 standard",
                "verified_date": TODAY,
            },
        }
        entries.append(entry)
        pending.append({
            "id": tid, "title": title, "author_id": "quran-author", "language": "Arabic",
            "era": "Early Islamic", "tradition": "islamic", "category": "sacred-text",
            "date_approx": "c. 610-632 AD; c. 650-750 AD (Codex Parisino-petropolitanus)", "century": 7,
            "source": entry["source"], "description": entry["description"],
            "themes": ["quran", "islam", "arabic", "parisino-petropolitanus", "hijazi", "verified"],
            "is_first_translation": False, "status": "published", "slug": tid,
            "scans": {"pages": [{"file": p, "caption": f"Codex Parisino-petropolitanus, BnF Arabe 328 fol. {Path(p).stem[4:]}"} for p in scan_paths]},
        })
    return entries, pending


# ----------------------------------------------------------------------------
def prove(label, meta, uth, pick, force):
    rows = build_folio_table(meta, only=label, force=force)
    if not rows:
        print("no such folio"); sys.exit(1)
    r = rows[0]
    print("\n=== PROOF OF CHAIN, folio", label, "===")
    print("Corpus Coranicum page record :", r["cc_page_url"])
    print("Corpus Coranicum image       :", r["cc_image_url"])
    print("Gallica image (downloaded)   :", r["gallica_url"])
    print("Local scan                   :", r["scan"], (SCAN_DIR / Path(r["scan"]).name).stat().st_size, "bytes")
    print("Image match Gallica vs CC    :", r["match_corr"], "OK" if r["match_ok"] else "MISMATCH")
    print(f"Stated range on page         : {ref(r['start'])} word {r['start']['word']}  ->  {ref(r['end'])} word {r['end']['word']}")
    print("Verses                       :", f"{r['verses'][0]} .. {r['verses'][-1]} ({len(r['verses'])} verses)")
    for s, v in r["verses"][:3]:
        print(f"  {s}:{v} AR: {uth[(s, v)]}")
        print(f"  {s}:{v} EN: {pick[(s, v)]}")
    print("  ...")
    s, v = r["verses"][-1]
    print(f"  {s}:{v} AR: {uth[(s, v)]}")
    print(f"  {s}:{v} EN: {pick[(s, v)]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove", metavar="FOLIO", help="e.g. 30v: run one folio and print the evidence")
    ap.add_argument("--force", action="store_true", help="re-download scans")
    args = ap.parse_args()

    print("Loading Tanzil Uthmani + Pickthall + sura metadata ...")
    uth = load_tanzil(TANZIL_UTHMANI, "tanzil_quran-uthmani.txt")
    pick = load_tanzil(TANZIL_PICKTHALL, "tanzil_en.pickthall.txt")
    meta = load_sura_meta()
    assert len(uth) == 6236 and len(pick) == 6236, (len(uth), len(pick))

    if args.prove:
        prove(args.prove, meta, uth, pick, args.force)
        return

    print("Building folio table (Corpus Coranicum mapping + Gallica scans) ...")
    rows = build_folio_table(meta, force=args.force)
    good = [r for r in rows if r["match_ok"]]
    print(f"\nfolio sides mapped: {len(rows)}, image-verified: {len(good)}, rejected: {len(rows) - len(good)}")

    entries, pending = build_entries(rows, meta, uth, pick)
    for e in entries:
        (PUB_DIR / f"{e['id']}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")
    PENDING.write_text(json.dumps({"texts": pending}, indent=2, ensure_ascii=False), encoding="utf-8")
    nsec = sum(len(e["translation"]) for e in entries)
    print(f"published {len(entries)} sura entries, {nsec} sections, {len({s['scan_pages'][0] for e in entries for s in e['translation']})} distinct scans")
    print(f"pending metadata -> {PENDING}")


if __name__ == "__main__":
    main()
