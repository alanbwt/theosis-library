# Theosis Library — Verified Primary Source Plan

## Criteria (Non-Negotiable)

Every single text in the library must have all three of:

1. **Primary source scan** — real photograph of the manuscript/tablet/inscription, from a verifiable public-domain or CC-licensed source
2. **Original language text** — verbatim, from a verified public-domain source
3. **English translation** — verbatim, from a verified public-domain source

Plus ideally:
4. **Doré illustration** (bonus visual for Bible texts)

Nothing gets added that doesn't meet criteria 1-3.

## Verified Sources

### Text sources (verbatim, public domain)
| Source | Provides | License | URL |
|--------|----------|---------|-----|
| bible-api.com | KJV Bible (English) | Public Domain | https://bible-api.com |
| bolls.life | KJV, ASV, WEB, YLT, Vulgate, TR, Tischendorf | Public Domain | https://bolls.life |
| ETCSL (Oxford) | Sumerian transliteration + English | CC-BY | https://etcsl.orinst.ox.ac.uk |
| Project Gutenberg | Public domain classical translations | Public Domain (US) | https://gutenberg.org |

### Scan sources (verified public domain / CC)
| Source | Provides | License | Status |
|--------|----------|---------|--------|
| Wikimedia Commons | Codex Sinaiticus (81 images), many others | CC0 / Public Domain | ✅ Verified |
| Internet Archive | Lake facsimile of Codex Sinaiticus (1911) | Public Domain | ✅ Available as PDF |
| British Library | Many biblical manuscripts via IIIF | CC-BY | Research needed |
| e-codices (Swiss) | Medieval manuscripts via IIIF | Various CC | Research needed |
| Bodleian | Medieval manuscripts via IIIF | Various CC | Research needed |
| CDLI | Cuneiform tablet photographs | Research needed | Research needed |

### Doré illustrations (bonus hero images)
| Source | Provides | License |
|--------|----------|---------|
| Wikimedia Commons Category:Doré's Bible Illustrations | 241 engravings | Public Domain (pre-1928) |

## Phase 1: Rigorous NT with Codex Sinaiticus

**Scope:** All 260 New Testament chapters, each with:
- Codex Sinaiticus page scan (from Wikimedia Commons where available)
- Greek Tischendorf text (from bolls.life)
- KJV English (from bible-api.com)
- Doré illustration for NT scenes (from Wikimedia Commons)

**Outputs:** 260 verified entries. Each triple-verified.

## Phase 2: Hebrew Bible with Aleppo/Leningrad Codex

**Scope:** 929 Old Testament chapters, each with:
- Leningrad Codex page scan (from archive.org public domain facsimile)
- Hebrew text (WLC from bolls.life)
- KJV English
- Doré illustration for OT scenes

**Outputs:** 929 verified entries.

## Phase 3: Sumerian Literature with CDLI Tablets

**Scope:** ~70 core Sumerian compositions, each with:
- Real tablet photograph from CDLI (license verification needed)
- Sumerian transliteration from ETCSL
- English translation from ETCSL

**Outputs:** ~70 verified entries.

## Phase 4: Classical Greek/Latin

**Scope:** Each major work, with:
- Manuscript scan from a verified open library (via IIIF)
- Original Greek/Latin text
- Public domain English translation (Gutenberg)

**Outputs:** Variable, research per text.

## Storage & Sovereignty

- **Primary**: GitHub + Cloudflare Pages (current)
- **Sovereign**: Start9 self-hosted Gitea + IPFS
- **Permanent archive**: Arweave for scan images (pay once)
- **Cold backup**: Encrypted external SSD (quarterly)

## Rules

1. **Never generate text.** Every character must come from a verified source.
2. **Never add an entry without a scan.** The scan is required.
3. **Always attribute the source.** Each entry must have a "source" field naming the origin.
4. **Audit regularly.** Every month, spot-check random entries to verify criteria are met.
5. **Delete unverified entries.** Better to have 500 rigorous texts than 10,000 unverifiable ones.
