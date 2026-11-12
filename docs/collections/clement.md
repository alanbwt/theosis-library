# 1 and 2 Clement (key `clement`)

Built 2026-11-12 by `scripts/import_clement.py`.

## Contents

| Entry | Sections | Witnesses |
|---|---|---|
| `verified-clement-1-clement` | 66 (salutation + chapters 1-65) | Codex Alexandrinus fol. 159r-168r; chapters 57 (from 57.7) to 63 on Hierosolymitanus 54 fol. 68r-69v |
| `verified-clement-2-clement` | 20 (chapters 1-20) | Codex Alexandrinus fol. 168r-169v (to 12.5); 12.5-20.5 on Hierosolymitanus 54 fol. 73v-76r |

Both works are complete. 33 images (22 Alexandrinus plates, 10 Hierosolymitanus pages, 23 MB).

## Sources

| Layer | Source | License |
|---|---|---|
| Photograph (A) | The Codex Alexandrinus in reduced photographic facsimile: New Testament and Clementine Epistles (British Museum 1909, ed. Kenyon), archive.org `codexalexandrinu01unse`, scan leaves 281-302 | public domain |
| Photograph (H) | Library of Congress Microfilm 5017, Panagios Taphos 54 (dated 1056), https://www.loc.gov/item/00279389694-jo/ , frames 70-72, 76-78 | LoC: public domain |
| Greek | Kirsopp Lake, The Apostolic Fathers I (1912), First1KGreek `tlg1271.tlg001` / `tlg002` `.1st1K-grc1` | edition PD; digital text CC BY-SA 4.0 |
| English | J. B. Lightfoot, The Apostolic Fathers (1891), earlychristianwritings.com transcription | public domain |

## Mapping method

- Alexandrinus: the 1909 facsimile prints the chapter range beneath every plate. All 22 captions
  were read on the scans (leaf 281 "1 Clem. i. 1-iii. 4" ... leaf 299 "1 Clem. lxiv. 1-2 Clem. ii. 2",
  leaf 302 "2 Clem. ix. 4-xii. 5"; full table `A_PAGES`). A chapter links to every plate whose range
  includes it. Folios follow NTVMR (GA 02: Revelation ends fol. 158v, then 22 pages = fol. 159r-169v);
  the numbers 159, 161, 162, 163, 165, 168 written on the plates agree. Spot checks on the images:
  159r opens with the salutation, 167v ends at 57.6, 168r opens with 64.1 ([λοι]πὸν ὁ παντεπόπτης
  θεός), 168v opens in 2 Clem 2.3 (ἔρημος δοκεῖ εἶναι).
- Hierosolymitanus 54: opening words of each page read on the images (table `H_PAGES`): 68r 57.5,
  68v 59.2, 69r 60.2, 69v 62.1, 70r 64.1; 73v 12.2, 74r 13.4 (marginal ιδ' at 14.1), 74v 15.1,
  75r 17.2, 75v 18.2, 76r 20.4. Chapters lost in A link to the H pages that carry them; 1 Clem 57
  and 2 Clem 12 link to both witnesses, and the scan note says which verses are on which.

## Text notes

- Greek digital text: corrupted tokens with non-Greek characters corrected from Lake's print
  (1 Clem 4.11 ʼΛαρὼν -> Ἀαρὼν, 32.4 ʽ??ʼ -> ὁ); elision encodings (δἰ, παῤ, καθ̓) written with an
  apostrophe; colon shown as ·. The rest of the Greek was NOT proofread against the print; the
  Didache check found about one letter or accent error per printed page in the same First1KGreek
  series, so similar errors are likely here.
- English: Lightfoot's italics kept as <em>. One alternative rendering the transcription gives in
  braces (1 Clem 4:5) is moved to the translator notes. Lightfoot's verse numbers differ from Lake's
  in 1 Clem 5, 8, 15, 18, 44, 50.
- The Greek is Lake's edited text, not a transcription of either manuscript.

## Gaps and open questions

- Codex Alexandrinus lacks 1 Clem 57.7-63.4 (a lost leaf between fol. 167v and 168r) and everything
  after 2 Clem 12.5; both gaps are filled from Hierosolymitanus 54, so no text is unillustrated.
- The Syriac witness and the Latin/Coptic versions are not included.
