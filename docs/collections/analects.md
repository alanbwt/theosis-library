# Analects of Confucius (Kamakura-period manuscript)

Key `analects`, prefix `verified-analects-`, shelf China, importer `scripts/import_analects.py`.

## Contents

20 entries, one per book (`verified-analects-01` to `-20`), 178 sections, 172 page images. Complete: every
paragraph of all 20 books (Legge's division: 499 chapters, 869 paragraph units) is in a section and linked to the
page(s) that carry it.

| Book | Title | Sections | Pages (canvas + side) |
|---|---|---|---|
| 1 | 學而 Xue er | 6 | 5L-8R |
| 2 | 爲政 Wei zheng | 7 | 8R-11R |
| 3 | 八佾 Ba yi | 7 | 11L-15R |
| 4 | 里仁 Li ren | 6 | 15R-17L |
| 5 | 公冶長 Gongye Chang | 9 | 18R-22R |
| 6 | 雍也 Yong ye | 9 | 22L-26L |
| 7 | 述而 Shu er | 9 | 27R-31L |
| 8 | 泰伯 Taibo | 7 | 31L-34L |
| 9 | 子罕 Zi han | 9 | 35R-39R |
| 10 | 鄉黨 Xiang dang | 7 | 39R-42L |
| 11 | 先進 Xian jin | 11 | 46L-52R |
| 12 | 顏淵 Yan Yuan | 11 | 52R-57R |
| 13 | 子路 Zilu | 11 | 57L-62L |
| 14 | 憲問 Xian wen | 15 | 62L-69L |
| 15 | 衞靈公 Wei Ling Gong | 10 | 70R-74L |
| 16 | 季氏 Ji shi | 10 | 74L-79R |
| 17 | 陽貨 Yang Huo | 11 | 79L-84L |
| 18 | 微子 Weizi | 8 | 84L-88R |
| 19 | 子張 Zizhang | 10 | 88R-92L |
| 20 | 堯曰 Yao yue | 5 | 92L-94L |

## The witness

Kyoto University Library, Seike bunko 清家文庫, 論語, 2 vols, call no. 1-66/ロ/6貴, record RB00007936
(https://rmda.kulib.kyoto-u.ac.jp/item/rb00007936). Important Cultural Property (1952). The colophon of Kiyohara
Edakata 清原枝賢, dated Tenbun 19 (1550), names the copyist as Kiyohara Yoshieda 清原良枝 (1253-1331), so the copy
is attributed to the late Kamakura period (c. 1300); the catalogue gives the attribution as traditional (伝).
Regular script, 7 columns of 14 characters a page, main text only, with red and black kunten. After each pair of
books the scribe copied the character counts of classic and commentary (經 / 注) from his He Yan (論語集解)
exemplar, but no commentary is written out. Canvases 3-5R hold He Yan's preface (not built); 43-45 are blank leaves
and covers between the volumes.

Why this witness: it is the oldest complete copy found with open, downloadable images. Older Tang manuscripts
(Dunhuang, Turfan; Zheng Xuan commentary) are fragmentary and sit behind Gallica/IDP, which block automated access
from here. NDL holds only Muromachi copies and a partial copy of the 1364 Shōhei print (books 5-10, 13-20).

## Sources

| Layer | Source | Licence |
|---|---|---|
| Photographs | Kyoto University Rare Materials Digital Archive, IIIF manifest RB00007936 (96 canvases, 3072 x 2048, each a two-page opening). Each page is cut from its opening (crop boxes in `data/sources/analects/page-crops.json`); about 1,210 x 1,810 px. | 画像二次利用自由（所蔵表示）: free reuse with credit 『論語』（京都大学附属図書館所蔵）and a link; the page crop is a stated modification |
| Chinese | Wikisource (zh) 論語, one page per book (revision ids in `data/sources/analects/wikisource-revisions.json`). ctext.org was not used: it serves a Cloudflare Turnstile check and its API needs a key. | CC BY-SA 4.0 |
| Division | Legge's chapter/paragraph markers from his Chinese text, Project Gutenberg #4094, aligned onto the Wikisource text | Public domain |
| English | James Legge, Confucian Analects (The Chinese Classics vol. 1), Project Gutenberg #3330 | Public domain (1861/1893) |

Where the Wikisource page prints a modern emendation from excavated texts, the received reading that Legge
translated is restored (importer `READINGS`): 1.7 (no 已), 4.14 求, 5.25 車馬衣輕裘, 7.6 據, 7.17 執, 10.6 brackets
dropped, 10.18 色, 12.10 誠不以富 line kept in place, 13.18 直, 14.36 直, 16.12 transposed line removed, 20.2 有司.

## Mapping method

1. Every page of the manuscript was viewed (two openings per image, about 1,250 px wide) and the first characters of
   every column were read and recorded: 1,150 text columns, in `data/sources/analects/column-heads.tsv` (title and
   blank columns marked).
2. Each reading is aligned to the received text by a longest-common-subsequence match near the expected position
   (14 characters a column). Irregular column spacing was reported and every case checked on the image; they are
   manuscript variants (added or missing 也/矣/焉, 小相/大相 in 11.25, 子曰 lines).
3. A page starts at the aligned position of its first column. Each Legge paragraph is assigned to the page where it
   begins; a section is the paragraphs that begin on one page, and lists every page its text runs onto.
4. Each scan_note records the page's first and last column openings, the column where the section's first
   paragraph begins, the pages it runs onto, and the column openings that differ from the received text.

## Gaps and uncertainties

- The Chinese is the received text, not a transcription of this manuscript. Variants were only seen at column
  openings (about 75; listed in the scan_notes). Typical: 悌 for 弟, 汝 for 爾, added final 也, 蝕也 for 食焉 (19.21),
  於顓臾 for 顓臾 (16.1), 如之何 for 而何 and 小相/大相 (11.25). A full collation was not made.
- One column opening is not certain (canvas 94 left, column 3: 入 or 人); it is used for alignment but not reported
  as a variant.
- Column openings were read at about 1,250 px across an opening; a few cursive forms (e.g. 爲 written 為, 禮 written
  礼) were normalised in the readings.
- Attribution to Kiyohara Yoshieda rests on the 1550 colophon (traditional attribution in the catalogue).
- Legge's English follows the received (Zhu Xi era) text; where the manuscript wording differs, the English does not
  reflect it.
- He Yan's preface (canvases 3-5) is not included.
