# Book of Odes: hymns on the founding of Zhou (Keicho-era print)

Key `shijing`, prefix `verified-shijing-`, shelf China, importer `scripts/import_shijing.py`.

## Contents

8 entries, 24 sections, 21 page images. Each entry is one complete ode of the Major Odes (大雅 Daya) that tell the
rise of the Zhou house; every stanza is in a section and linked to the page(s) that carry it.

| Entry | Ode | Stanzas | Sections | Pages (vol. 2 canvas + side) |
|---|---|---|---|---|
| `verified-shijing-235-wen-wang` | 文王 Wen wang | 7 | 3 | 59L-60L |
| `verified-shijing-236-da-ming` | 大明 Da ming | 8 | 3 | 60L-61L |
| `verified-shijing-237-mian` | 緜 Mian | 9 | 4 | 61L-63R |
| `verified-shijing-240-si-qi` | 思齊 Si qi | 5 | 2 | 64R-64L |
| `verified-shijing-241-huang-yi` | 皇矣 Huang yi | 8 | 4 | 64L-66L |
| `verified-shijing-243-xia-wu` | 下武 Xia wu | 6 | 2 | 67R-67L |
| `verified-shijing-244-wen-wang-you-sheng` | 文王有聲 Wen wang you sheng | 8 | 3 | 67L-68L |
| `verified-shijing-245-sheng-min` | 生民 Sheng min | 8 | 3 | 69R-70R |

## Sources

| Layer | Source | Licence |
|---|---|---|
| Photographs | National Diet Library, 詩經 2卷, [慶長年間] 活字印 (Japanese movable-type print, Keicho era 1596-1615), call no. WA7-183, vol. [2], IIIF https://dl.ndl.go.jp/api/iiif/2544552/manifest.json. Main text only, 8 columns of 17 characters, hand-added reading marks. Pages cut from the openings by IIIF region (boxes in `data/sources/shijing/page-crops.json`), 2400 px high. | PDM (public domain mark) |
| Chinese | Wikisource (zh) 詩經/<ode> (Mao text) | CC BY-SA 4.0 |
| English | James Legge, The Shih King, Sacred Books of the East 3 (1879), The Major Odes of the Kingdom, from the validated Wikisource Page transcription (Page:Sacred Books of the East - Volume 3.djvu/411-433) | Public domain; transcription CC BY-SA |

Footnotes are omitted. One Wikisource editorial reconstruction (a line supplied from Legge's 1871 edition in 文王
stanza 2) is left out, so the English is as printed in SBE 3. In 思齊 stanza 4 Wikisource gives 遐 with the variant
瑕; 瑕 is used because Legge translates it ("without stain").

## Mapping method

The first characters of every column on pages 59L-70L were read on the images (`data/sources/shijing/column-heads.tsv`;
ode tails such as 文王七章章八句, headings, and columns of odes not built are marked). The readings are aligned to the
ode text (all 122 text-column openings match the Wikisource text, allowing 迺/廼, 于/於). A stanza belongs to the page
where it begins; each section lists the pages its stanzas run across. Scan notes record first/last column openings,
the column where the first stanza starts, headings and tail lines.

## Gaps and uncertainties

- **Guofeng (Airs of the States) not built.** No clean public-domain English for all 160 pieces was reachable: Legge's
  full 1871 translation (Chinese Classics IV) exists here only as raw archive.org OCR mixed with notes; ctext.org
  (which carries it) is behind a Cloudflare Turnstile check; SBE 3 has only a dozen Guofeng pieces, mostly single
  stanzas; Legge's 1876 verse version (Gutenberg #10056) is a selection. Candidate witnesses are ready: the same NDL
  print vol. [1] (pid 2544551) for all Guofeng, and a 1942 collotype facsimile of an old manuscript of 周南/召南 with
  Mao-Zheng commentary (NDL pid 1139393, PDM). Building them needs a usable English.
- 公劉 (Mao 250), part of the founding cycle, is not in SBE 3 and was not built.
- The print is c. 1600, not the oldest witness. Older complete witnesses (Tang stone classics, Dunhuang manuscripts,
  Song prints) were not available as open photographs of the object from here; the Kyoto 1597 manuscript (RB00008077)
  carries the Zheng commentary and is cursive.
- The Chinese is the Wikisource Mao text, not a transcription of the print; no variants were found at column openings.
