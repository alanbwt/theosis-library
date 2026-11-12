# QC review: Bible and early Christian collections (2026-11-12)

Independent check of the library's promise for each section: (1) a photograph of the manuscript page
that carries exactly that section's text, (2) the verbatim original-language text, (3) a verbatim English
translation of the same passage. Read-only review: no repo file other than this one was written; no build,
deploy or commit.

## Scope and method

- Newer collections (data/collections/*.json), 3 sections each: enoch-ethiopic, akhmim-codex,
  gospel-of-thomas, qumran-1qphab (columns I-V only), didache, clement, josephus, philo (24 sections).
- Legacy collections (data/texts.json only): Sinaiticus 12 (+3 entries checked from data), Leningrad 13,
  Vaticanus 8, Alexandrinus 8, Bezae 8, Washingtonianus 13, 1QIsa-a 8, Quran (BnF Arabe 328) 10 folio-side
  sections, Poetic Edda 9 (89 sections).
- Total: 113 sections checked on the photographs. For each: (a) first and last words read on the linked
  image(s) with crops/zooms; (b) original and English cover the same verses, absent verses flagged;
  (c) rendered page at http://localhost:8765/library/<id>.html fetched: section present, images HTTP 200,
  no escaped tags, column labels right; (d) introduction, notes, verification and catalog rows against the data.
- Scripts: `check_collection.py` on the 8 newer keys = 0 hard failures each (warnings only for Thomas page-45
  and page-51, both correctly single-page). `audit_sections.py` = ALL SECTIONS PASS with 20
  `verse_numbering_differs_without_note` warnings, all Sinaiticus; 17 are false alarms (those intros say
  "Manuscript note:", the script looks for "Numbering:"), 3john-1 and rev-12 are explained numbering
  differences, 2cor-13 carries a wrong note (see below).
- Crops are in the session scratchpad (qc-c/), not in the repo.

## Defects (fix needed)

| Collection | Entry | Section | Problem |
|---|---|---|---|
| Sinaiticus | verified-sinaiticus-barnabas-21 | 21.6-9 | English ends with ~3,200 characters scraped from earlychristianwritings.com ("Please buy the CD", "copyright Peter Kirby", site menu); visible on the live page. |
| Sinaiticus | verified-sinaiticus-2cor-13 | 13.11-14 | Intro says KJV 13:14 is not in Sinaiticus; fol. 278v col. 2 ll. 2-6 read Η ΧΑΡΙϹ ΤΟΥ ΚΥ ΙΥ ΧΥ: a numbering difference (Greek 13 = KJV 14) described as a missing verse. |
| Sinaiticus | verified-sinaiticus-ps-50 (+240 OT intros) | intro | "Nomina sacra are shown in angle brackets": the Greek has no brackets. |
| Vaticanus | verified-vaticanus-2cor-13 | 13.9-13 | Greek 13 "η χαρις του κυ ιυ..." stands beside English 13 "All the saints salute you"; KJV 14 dropped; no note. |
| Vaticanus | verified-vaticanus-mark-16 | 16.4-8 | 16:9-20 absent with no note anywhere; blank column is visible on p. 1303. |
| Vaticanus | verified-vaticanus-hebrews-9 | 9.8-14 | Greek stops mid-word "καθα" (end of the original hand); English gives all of 9:14; end of the codex not stated. |
| Vaticanus, Bezae | verified-vaticanus-luke-22 (systemic) | 22.37-47 | Words run together at page joins ("ιουδαςεις"); >=85 Vaticanus and 24 of 101 Bezae joins (e.g. bezae-john-12 "υψωθηναιτον"). |
| Vaticanus | 7 catalog rows | - | data/texts.json scans.pages omits a page the sections use: acts-7, john-21, luke-12, luke-8, mark-14, mark-6, matt-26. |
| Alexandrinus | verified-alexandrinus-rev-12 (+2cor-13, 3john-1) | intro | Two contradictory Numbering paragraphs (stale "affects only the Tischendorf comparison text" + new one). |
| Bezae | all 45 entries | intro | Lacunae Matt 1:1-20a, 6:21-9:1, 27:3-11, John 1:17-3:25 not stated (rule 10). |
| Washingtonianus | verified-washingtonianus-luke-3 | 3.17-24, 3.25-32, 3.33-38 | p0211 goes from 3:23 "ενομιζετο ιωσηφ" straight to 4:1 "ις δε πληρης πνς αγιου" (confirmed by the lead reviewer on the image): W lacks 3:24-38, yet 15 verses of Tischendorf Greek + KJV are shown against p0211 with no flag. |
| Washingtonianus | verified-washingtonianus-luke-4 | 4.2-11 | 4:2 begins on the last line of p0211; section links only p0212. |
| Washingtonianus | verified-washingtonianus-mark-16 | intro | Says the Freer Logion "does not appear in either column"; the NTVMR Greek now prints it inside v. 14. |
| Washingtonianus | verified-washingtonianus-john-4 | catalog row | texts.json scans.pages includes w-p0211 (a Luke page). |
| Leningrad | verified-leningrad-josh-21 | 21.33-40 | Josh 21:36-37 are not in the codex (fol. 133v col. 1: 21:35 runs into 21:38) but are printed as Leningrad Hebrew beside KJV, unflagged (UXLC fills them from elsewhere; importer drops UXLC notes). |
| Leningrad | verified-leningrad-1chr-12 (+56 entries) | intro | Says each section's KJV range is shown as english_ref; the template never renders it. |
| 1QIsa-a | verified-1qisaa-isa-2 | 2.9-15 | Scroll lacks 2:9b as well as 2:10 ("וישפל איש" runs into "ועיני"); English 9 still has "therefore forgive them not"; note names only 2:10. |
| 1 Clement | verified-clement-1-clement | 52, 53 | English contains raw source markers "1Clem 52:4" and "1Clem 53:3" in place of verse numbers, rendered on the page. |
| Josephus | collection | - | docs/collections/josephus.md missing (spec requires it). |

## Doubts (check or document)

- Sinaiticus: john-5 5:3b ("waiting for the moving of the water") absent in Greek but not flagged (5:4 is);
  ps-50 English omits the KJV heading so Greek 1-2 have no English while the intro says "the same words";
  scribe's line-filler marks render as ">" mid-word in 223 sections (mark-16 "ζητει>τε") with no explanation;
  matt-15 15:39 English ends with a comma; texts.json rows list only the first page (11 of 12 sampled) and
  some duplicate files (isa-53-/isa-54- same folio); new Ps 71 / Jer 10 images credited to codexsinaiticus.org
  though taken from a GitHub copy.
- Alexandrinus: matt-25 25:6 and john-6 6:50 partial in Greek, full in English, unmarked; 1john-5 English has
  the 5:3a clause the codex skips and the Comma Johanneum, unnoted; hebrews-7 page_captions say 141v = 7:17-28
  but the image has the end of 7:16.
- Vaticanus: 199 duplicate image files; all 495 images 1024-1119 px (spec 1600-2600); john-7 7:53 edition text
  unaccented (other source?).
- Bezae: matt-1 1.20-25 starts mid-verse on fol. 3v, full 1:20 shown unflagged; only Matthew and John present
  though intros describe Gospels and Acts; 33 of 45 texts.json rows omit pages sections use.
- Washingtonianus: Luke 4:1 and 23:1 omitted as "index gaps" but visible on p0211 / p0302; IGNTP John leaves
  ~20 split words ("ερ χαιται") and stray overbars; Freer Logion unmarked and untranslated; 256 Matthew/Luke
  sections without scan_note.
- 1 Clement: chapters 5, 8, 15, 18, 44, 50 use the same superscripts for different verses (Lake vs Lightfoot,
  e.g. ch. 5 Greek 7 = English 6); only a general note.
- 1QpHab: cols-1-3 image is 760 px wide; col. I and the col. III line beginnings are barely legible; rule 9 now
  permits Israel Museum images.
- Quran: quran-71 (and 3:13) headings skip one word at the folio break (word 9 visible at the foot of 70r);
  intro asserts Tanzil "conveys the same reading" as the folio, unchecked; quran-4 row page order string-sorted.
- Edda: label "Old Norse · heimskringla.no" names a website, licence of Guðni Jónsson's text unverified;
  qc-legacy.md "catalog changes not made" now stale (rows already fixed).
- Leningrad / 1QIsa-a: no section has a scan_note (mapping rests on LCIndex / column-line refs; all sampled
  page breaks matched the images); isa-51 shows an unexplained "line 0".
- Josephus: "reported widely in October 2026" and "page shown in the news coverage" are unsourced; images keep
  the DigiVatLib copyright bar and a strip of the facing page.

## Systemic

1. Verses absent from a manuscript are flagged inconsistently: Sinaiticus/Alexandrinus/Vaticanus mostly flag
   them, but W Luke 3:24-38, Leningrad Josh 21:36-37, 1QIsa-a 2:9b, Vaticanus Mark 16:9-20 / Heb 9:14b-end,
   and partial verses at lacunae are shown or dropped silently. Base texts that fill gaps from other witnesses
   (UXLC, Tischendorf fallback, CSNTM index ranges) are the cause.
2. Page joins: words lost their space (Vaticanus, Bezae) or stay split (W John) where a word crosses a page.
3. data/texts.json catalog rows lag the section data for Sinaiticus, Vaticanus and Bezae (pending integrator
   changes listed in qc docs but not applied).
4. Page mapping itself held up: in all 113 sections every linked page carries the section's text and no page
   was missing, except W Luke 3/4 above.

## Findings table

| Collection | Entry id | Section | Check | Verdict | Evidence |
|---|---|---|---|---|---|
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-watchers | 10 | a | OK | fol. 2v col. b line 8 reads ‹...በእንተ፡ ዝንቱ፡ ክፍል፡ ወአሜሃ፡ ልዑል፡ ዐቢይ...› (ch. 10 opens mid-column after rubric ክፍል); fol. 3r col. a line 1 ‹ውልድ፡ ትውልድ፡ ወእስከ፡ ለዓለም፡ ወበእማንቱ፡ መዋዕል...› = last words of ch. 10 then ch. 11. Both linked pages carry the chapter; none missing. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-watchers | 10 | b | OK | Ge'ez (Dillmann, unnumbered, stated in notes) runs ወአሜሃ ... ወእስከ ፡ ለዓለም = whole ch. 10; Charles English 10:1-22 complete. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-watchers | 10 | c | OK | Renders; 2 images 200; labels Ge'ez · Dillmann 1851 / English · R. H. Charles (1917); no escapes. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-parables | 69 | a | OK | fol. 8v col. b foot carries the angel-name list with red numerals (69:2-3), last line ‹...ለመኰንነ፡ ፻ ዚአሆሙ›; col. c line 1 ‹ወመኰንን፡ ፶ ዚአሆሙ፡ ወመኰንን፡ ፲ ዚአሆሙ፡ ስሙ፡ ለቀዳማዊ፡ ይቁን› (69:3-4); fol. 9r col. b lines 1-2 ‹እቱ፡ ወልደ፡ ብእሲ፡ ተርእየ፡ ወነበረ፡ ዲበ፡ መንበረ፡ ስብሐቲሁ› (69:29). 8v + 9r both needed and linked. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-parables | 69 | b | OK | Ge'ez ends ‹ዝውእቱ ፡ ምሳሌ ፡ ሣልስ ፡ ዘሄኖክ›, English 69:1-29 ends "This is the third Parable of Enoch." Minor: Dillmann digital text numbers two angels ፲ወ፯ (17) and none ፲ወ፮ (16), shown as in source. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-parables | 69 | c | OK | Renders, both images 200, labels right. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-epistle | 107 | a | OK | fol. 16v col. a: rubric ‹ክ፡ ፻፯› then ‹ወርኢኩ፡ ጽሑፈ፡ በላዕሌሆሙ፡ እስመ፡ ትውልድ...›; same column ‹...ለምድር፡ እምኵሉ፡ ኀጕል፡ ክ፡ ፻፰›. Whole chapter in col. a; col. c ends after 4 lines + decorated band as the 108 note says. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-epistle | 107 | b,c | OK | Ge'ez = 107:1-3, English 107:1-3; renders, image 200. |
| 1 Enoch (Ethiopic) | verified-enoch-ethiopic-* | intro | d | OK | "3 columns of 40 lines", "fol. 2r-16v" agree with images and data; check_collection 0 failures. |
| Akhmim codex | verified-akhmim-codex-gospel-of-peter | 3 | a | OK | Plate p. 2: 19 lines; line 5 ends ιστηκει δε, line 13 ‹και παρεδωκεν αυτον τω λαω προ μιας των αζυμων›, line 19 ‹ακανθινον εθηκεν επι της κεφαλης του κυριου›; p. 3 line 4 ‹ταυτη τη τιμη τιμησωμεν τον υιον του θυ και η...›. Both pages carry ch. 3. |
| Akhmim codex | verified-akhmim-codex-gospel-of-peter | 3 | b | OK | Greek 2.13-3.4 (page.line) = Robinson ch. 3 English complete; numbering differs by design (page.line vs chapter), explained in intro. |
| Akhmim codex | verified-akhmim-codex-gospel-of-peter | 8 | a | OK | p. 5 line 9 ‹...συναχθεντες δε οι γραμματεις›, line 17 ‹αυτου επι τρεις ημ[ερας] μηποτε ελθοντες›; p. 6 line 13 ‹χωρου ινα ιδωσι το μνημειον εσφραγισμενον›. |
| Akhmim codex | verified-akhmim-codex-gospel-of-peter | 13 | a | OK | p. 9 line 14 ends ‹και απελθουσαι ευρον›, line 17 (last) ‹μενον μεσω του ταφου ωραιον και περιβεβλημενον›; p. 10 line 6 ‹τοτε αι γυναικες φοβηθεισαι εφυγον›, braided band below. |
| Akhmim codex | verified-akhmim-codex-gospel-of-peter | 3, 8, 13 | c | OK | All render; images 200; labels Greek · Lods 1893 (diplomatic) / English · J. Armitage Robinson (1896). |
| Akhmim codex | verified-akhmim-codex-gospel-of-peter | intro / notes | d | OK | Scan notes for ch. 4-5 say "p. 3 begins ‹lines 1-2 badly rubbed ...; the last line reads ηλιον μη δυναι ...›" (awkward but true: 3.18). Catalog row lists akhmim-p01.jpg, used by no section (cover image only). Plates are heliogravures from photographs: allowed by rule 5. |
| Gospel of Thomas | verified-gospel-of-thomas-page-32 | 3 | a | OK | p. 32: Thomas opens below the Apocryphon of John colophon/title; line with ‹...ⲡⲉϫⲉⲓ︤ⲥ︥ ϫⲉⲉⲩϣⲁ› present, last line ‹ⲥⲟⲩⲱⲛⲧⲏⲩⲧⲛ̄ ⲧⲟⲧⲉ ⲥⲉⲛⲁⲥⲟⲩⲱ›; p. 33 line 1 ‹ⲧⲏⲛⲉ ⲁⲩⲱ ⲧⲉⲧⲛⲁⲉⲓⲙⲉ›, line 5 ‹ⲡⲉ ⲧⲙⲛ̄ⲧϩⲏⲕⲉ ⲡⲉϫⲉⲓ︤ⲥ︥...›. |
| Gospel of Thomas | verified-gospel-of-thomas-page-41 | 50 | a | OK | p. 41 last line ‹ϩⲓⲧⲟⲟⲧϥ ⲟⲩⲁⲁⲧϥ ⲁϥⲱϩ[ⲉ]›; p. 42 line 1 ‹ⲁⲩⲱ ⲁϥⲟⲩⲱⲛϩ ⲉⲃⲟⲗ ϩⲛ̄ⲧⲟⲩϩⲓⲕⲱⲛ›, line 7 ‹ⲟⲩⲁⲛⲁⲡⲁⲩⲥⲓⲥ› then saying 51. |
| Gospel of Thomas | verified-gospel-of-thomas-page-51 | 114 | a | OK | p. 51 ‹...ⲡⲉϫⲉⲥⲓ̈ⲙⲱⲛ ⲡⲉⲧⲣⲟⲥ / ⲛⲁⲩ ϫⲉⲙⲁⲣⲉⲙⲁⲣⲓϩⲁⲙ...› to ‹ⲛⲙ̄ⲡⲏⲩⲉ›, then decorative line and title ⲡⲉⲩⲁⲅⲅⲉⲗⲓⲟⲛ ⲡⲕⲁⲧⲁ ⲑⲱⲙⲁⲥ. |
| Gospel of Thomas | verified-gospel-of-thomas-page-32/41/51 | 3, 50, 114 | b | OK | Coptic lines (page.line) cover the whole saying; Mattison English whole saying; English has no line numbers (chapter-level pairing, stated). |
| Gospel of Thomas | verified-gospel-of-thomas-page-32/41/51 | 3, 50, 114 | c | OK | Render; images 200; labels Coptic · Coptic SCRIPTORIUM (Dilley) / English · Mark M. Mattison. check_collection warnings for page-45/51 (all sections on one image) are correct: one page each. |
| 1QpHab (cols I-V) | verified-qumran-1qphab-columns-1-5 | I | a | OK | 1qphab-cols-1-3.jpg, right edge of right piece: ‹...שועתי ולוא›, ‹אל בעשק ומעל›, ‹על כן תפוג תורה›, ‹אשר מאשו בתורת אל›, ‹הוא מורה הצדק›, ‹ל כן יצא המשפט› all visible as the note says. |
| 1QpHab (cols I-V) | verified-qumran-1qphab-columns-1-5 | III | a | OK | Line beginnings at left edge of left piece of cols-1-3 (ובמישור, כיא הוא, ונורא הוא, פשרו על ה, יעופו כנשר, ואין שבעה, אפים ידב...); line ends on 1qphab-col-03-left.jpg: ‹את ערי הארץ› (1), ‹משכנות לוא לו איום› (2), ‹הוא אשר› (13), ‹שבי› (14). Both images needed and linked. |
| 1QpHab (cols I-V) | verified-qumran-1qphab-columns-1-5 | IV | a | OK | col-04: line 1 ‹יקלס ורזנים משחק לו פשרו אשר›, line 2 ‹ילעיגו על רבים ובזו על נכבדים במלכים›, line 10 ‹לאלוהו פשרו על מושלי הכתיאים›, line 13 ‹לשחית את›, line 14 ‹פשרו› at torn edge. |
| 1QpHab (cols I-V) | verified-qumran-1qphab-columns-1-5 | I, III, IV | b | OK | Hebrew lines 1-17 vs Brownlee margin line numbers; English stops at 15 in col. I where Hebrew 16-17 are wholly editorial restoration; col. IV English lacks a "12" marker (Brownlee prints none), explained in intro. |
| 1QpHab (cols I-V) | verified-qumran-1qphab-columns-1-5 | I, III | a | DOUBT | 1qphab-cols-1-3.jpg is 760x633 px (spec: long side 1600-2600); col. I and the line beginnings of col. III are strips ~150 px wide, barely legible. Rule 9 (2026-11-12) now allows Israel Museum DSS photographs with credit, so a sharper image is usable. |
| 1QpHab (cols I-V) | verified-qumran-1qphab-columns-1-5 | I, III, IV | c | OK | Render; images 200; labels Hebrew · Qumran transcription (Abegg, ETCBC) / English · W. H. Brownlee (1948). |
| Didache | verified-didache-teaching-of-the-twelve-apostles | 7 | a | OK | fol. 78r: marginal ζ' at ‹περὶ δὲ τοῦ βαπτίσματος›, last line ‹...κελεύεις δὲ νηστεῦσαι τὸν βαπτιζόμενον πρὸ μι›; fol. 78v line 1 ‹ἢ δύο· αἱ δὲ νηστεῖαι ὑμῶν μὴ ἔστωσαν μετὰ τῶν ὑποκριτῶν›. |
| Didache | verified-didache-teaching-of-the-twelve-apostles | 10 | a | OK | fol. 78v marginal ι' at ‹μετὰ δὲ τὸ ἐμπλησθῆναι›, last line ‹...γνώσεως καὶ πίστεως καὶ ἀθανασί›; fol. 79r line 1 ‹ἧς ἐγνώρισας ἡμῖν διὰ Ἰυ τοῦ παιδός σου›, ‹...μαρὰν ἀθά› lower on 79r. |
| Didache | verified-didache-teaching-of-the-twelve-apostles | 16 | a | OK | fol. 80r marginal ιϛ' at ‹Γρηγορεῖτε›, last line ‹πυκνῶς δὲ συναχθήσεσθε ζητοῦντες τὰ ἀνήκοντα ταῖς ψυχαῖς ὑμῶν›; fol. 80v line 1 ‹οὐ γὰρ ὠφελήσει ὑμᾶς ὁ πᾶς χρόνος›, ends ‹ἐπάνω τῶν νεφελῶν τοῦ οὐρανοῦ›, page blank below. |
| Didache | verified-didache-teaching-of-the-twelve-apostles | 7, 10, 16 | b | OK | Lake Greek with verse numbers, Lightfoot English unnumbered by chapter (stated in notes); same chapter content. Greek is Lake's edition, labelled "Greek · Lake 1912", not presented as a transcription. |
| Didache | verified-didache-teaching-of-the-twelve-apostles | 7, 10, 16 | c | OK | Render; images 200; labels right. |
| 1-2 Clement | verified-clement-1-clement | 38 | a | OK | 164v caption ‹1 Clem. xxxv. 6-xxxviii. 2›; last lines of col. 2 read ‹...ο ταπεινοφρονων μη εαυτω μαρτυρειτω ... ο αγνος εν τη σαρκι και μη αλαζονευεσθω› (38:2); 165r caption ‹xxxviii. 2-xlii. 2›. |
| 1-2 Clement | verified-clement-1-clement | 57 | a | OK | 167v caption ‹1 Clem. lv. 6-lvii. 6›; H54 fol. 68r line 1 ‹σί με κακοὶ καὶ οὐχ εὑρήσουσιν· ἐμίσησαν γὰρ σοφίαν› (57.5), line 4 ‹ἀνθ' ὧν γὰρ ἠδίκουν νηπίους φονευθήσονται› (57.7). |
| 1-2 Clement | verified-clement-2-clement | 9 | a | OK | Captions read on plates: 169r ‹2 Clem. vi. 1-ix. 4›, 169v ‹2 Clem. ix. 4-xii. 5›. Plates are the 1909 reduced facsimile: col. 2 of 164v and much of 167v are near-illegible, so mapping rests on the printed captions (documented source). |
| 1-2 Clement | verified-clement-1-clement | 38, 57; 2 Clem 9 | b | OK | Verse numbers 1-4 / 1-7 / 1-11 match between Lake Greek and Lightfoot English. |
| 1-2 Clement | verified-clement-1-clement | 52, 53 | b/c | DEFECT | English carries raw source markers instead of verse numbers: ch. 52 ‹...I will deliver thee, and thou shalt glorify Me. 1Clem 52:4 For a sacrifice unto God...›, ch. 53 ‹...molten images. 1Clem 53:3 And the Lord said...›. Rendered on the live page. |
| 1-2 Clement | verified-clement-1-clement | 5, 8, 15, 18, 44, 50 | b | DOUBT | Same superscripts label different verses: ch. 5 Greek ‹7 δικαιοσύνην διδάξας› = English ‹6 having taught righteousness›; ch. 18 Greek 1-17 vs English 1-14; ch. 44 Greek 6 = English 5. Notes say only "his verse numbers differ from Lake's in a few chapters"; no per-section flag. |
| 1-2 Clement | verified-clement-1-clement / 2-clement | 38, 57, 9 | c | OK | Render; images 200; labels Greek · Lake 1912 / English · J. B. Lightfoot (1891). |
| Josephus | verified-josephus-antiquities-18-63 | Vat. gr. 148 fol. 214v | a | OK | Heading ‹ἐκ τοῦ ὀκτωκαιδεκάτου λόγου τῆς ἰουδαϊκῆς ἀρχαιολογίας περὶ τοῦ Χυ μαρτυρία› at top, passage below it to about line 13; B/W microfilm as stated. |
| Josephus | verified-josephus-antiquities-18-63 | Vat. gr. 342 fol. 282v | a | OK | ‹ἰουδαῖος ἰώσηππος ...› after the Psalter matter at about line 11, passage ends ‹...οὐκ ἐπέλιπε τὸ φῦλον› about line 24. |
| Josephus | verified-josephus-antiquities-18-63 | Vat. gr. 984 fol. 152v | a | OK | Red initial Γ with marginal ‹περὶ τοῦ Χυ›; ‹γίνεται δὲ κατὰ / τοῦτον τὸν χρόνον ἰησοῦς σοφὸς ἀνήρ› to ‹οὐκ ἐπέλιπε τὸ φῦλον› within 5 lines on 152v; no run-over to 153r seen. |
| Josephus | verified-josephus-antiquities-18-63 | all 3 | b,c | OK | Niese 18.63-64 vs Whiston 63-64 (same text in each section, by design); render, images 200, label Greek · Niese / English · William Whiston (1737). |
| Josephus | verified-josephus-antiquities-18-63 | collection | d | DEFECT | docs/collections/josephus.md does not exist (spec requires a report per collection). Intro and 148 scan_note assert "reported widely in October 2026" / "the page shown in the October 2026 news coverage" with no source cited. Images keep the DigiVatLib copyright bar and a strip of the facing page (984, 342). |
| Philo | verified-philo-on-the-creation | 107 | a | OK | fol. 49v: ‹ἔστι δὲ οὐ τελεσφόρος μόνον› 3 lines from foot, last line ‹...ἔτι δὲ τὴν ἁρμονικὴν περιέχει· τὸ δὲ πλινθίον›; fol. 50r line 1 ‹συνέστηκεν ἐκ τῶνδε τῶν ἀριθμῶν· ἓξ ὀκτὼ ἐννέα δώδεκα›, section ends line 4 ‹διὰ πασῶν›. |
| Philo | verified-philo-confusion-of-tongues-146-147 | 147 | a | OK | fol. 205r line 1 ‹τῆς ἡδονῆς πρὸς ἐμπειροπολέμων ἀνδρῶν ἀντιτειχίζεται πρὸς›; line 6 ‹...προσαγορεύεται· διὸ προήχθην›; line 10 ‹...εἰκὼν λόγος ὁ πρεσβύτατος· καὶ πολλαχοῦ μέντοι›. |
| Philo | verified-philo-who-is-the-heir-205-206 | 206 | a | OK | fol. 293r: ‹ἀγάλλεται δὲ ἐπὶ τῇ δωρεᾷ› mid-line, ends ‹εἰρηνοφύλακος ἀεὶ θεοῦ›; next line ‹διδάξας οὖν ἡμᾶς περὶ τῆς εἰς ἴσα τομῆς›; last line ‹...φθίνει τὰ ἔγγεια· πάλιν ὕδατος›. |
| Philo | verified-philo-* | 107, 147, 206 | b | OK | Cohn-Wendland section = Yonge section; Greek is the critical text, stated in each scan_note and label. |
| Philo | verified-philo-* | 107, 147, 206 | c | OK | Render; images 200; labels Greek · Cohn-Wendland / English · C. D. Yonge (1854). 11 "&lt;" on the Opif page are Cohn's editorial angle brackets, correctly escaped. |
| (newer, all) | data/collections/*.json | catalog rows | d | OK | Row scans.pages = union of section scan_pages for all 35 newer entries, except akhmim row also lists akhmim-p01.jpg (cover). check_collection: 0 hard failures in all 8; 2 warnings (Thomas page-45, page-51) are correct single-page entries. |
| Codex Sinaiticus | verified-sinaiticus-ps-50 | 50.1-8 | a | OK | fol. 101r (corner "101"): red title ΕΙϹ ΤΟ ΤΕΛΟϹ ΨΑΛΜΟϹ ΤΩ ΔΑΥΕΙΔ in col. 1 lower half; col. 1 last line ΤΑ ΑΔΗΛΑ ΚΑΙ ΤΑ ΚΡΥΦΙΑ ΤΗϹ ϹΟΦΙΑϹ, col. 2 line 1 ϹΟΥ ΕΔΗΛΩϹΑϹ ΜΟΙ = end of 50:8, as the scan_note says |
| Codex Sinaiticus | verified-sinaiticus-ps-50 | 50.1-8 | b | DOUBT | Greek 1-8 (LXX, superscription = vv. 1-2) beside KJV 51:1-6; offset explained in the "Numbering" note, but the KJV superscription is not given, so Greek 1-2 have no English although the note says "the Greek and English in each section are the same words" |
| Codex Sinaiticus | verified-sinaiticus-ps-50 | 50.1-8 | c | OK | renders; 1 image (200); label "Greek · Codex Sinaiticus transcription" matches the uncial CSP text; no escapes |
| Codex Sinaiticus | verified-sinaiticus-ps-50 | intro | d | DEFECT | intro says "Nomina sacra are shown in angle brackets"; the Greek has none (ο θϲ, κε without brackets). Same false sentence in 240 Sinaiticus OT intros, none of which has a bracket in its Greek |
| Codex Sinaiticus | verified-sinaiticus-ps-71 | 71.16-20 | a | OK | fol. 106v col. 2 lower: 71:16 ΕϹΤΑΙ ϹΤΗΡΙΓΜΑ ... last line (red) ΕΞΕΛΙΠΟΝ ΟΙ ΥΜΝΟΙ ΔΑΥΕΙΔ ΤΟΥ; new image Q61_4r col. 1 line 1 ΥΙΟΥ ΙΕϹϹΑΙ then ΨΑΛΜΟϹ ΤΩ ΑϹΑΦ (Ps 72 LXX begins): continuity proves it is fol. 107r (corner digit hard to read, "10?"; neighbours 104/106/111 consistent) |
| Codex Sinaiticus | verified-sinaiticus-ps-71 | 71.16-20 | b | OK | Greek 16-20 = KJV 72:16-20, same numbers, same content |
| Codex Sinaiticus | verified-sinaiticus-ps-71 | 71.16-20 | c | OK | 2 images 200; CSP label right |
| Codex Sinaiticus | verified-sinaiticus-ps-71 | entry | d | DOUBT | data/texts.json row scans.pages lists only ps-71-Q61_3v; section also uses Q61_4r (catalog change listed as pending in qc-sinaiticus-venetus.md, not applied). verification.scan_source says codexsinaiticus.org, but Q61_4r is one of the 7 images taken from a GitHub copy (provenance only in docs) |
| Codex Sinaiticus | verified-sinaiticus-prov-25 | 25.17-24 | a | OK | fol. 140r col. 2: ϹΠΑΝΙΟΝ ΕΙϹΑΓΑΓΕ ϹΟΝ ΠΟΔΑ in mid-column (~l. 31), last line ΕΑΝ ΠΙΝΑ Ο ΕΧΘΡΟϹ ϹΟΥ ΤΡΕΦΕ ΑΥΤΟ; fol. 140v col. 1 l. 1 ΕΑΝ ΔΙΨΑ ΠΟΤΙΖΕ ΑΥΤΟΝ ... l. 11 ΚΙΑ ΚΟΙΝΗ, then ΩϹΠΕΡ ΔΡΟϹΟϹ (25:25). Both pages needed, both linked |
| Codex Sinaiticus | verified-sinaiticus-prov-25 | 25.17-24 | b | OK | Greek 17-24 / KJV 17-24; LXX plus (20b moth/worm) present in Greek only, normal LXX difference |
| Codex Sinaiticus | verified-sinaiticus-prov-25 | 25.17-24 | c | OK | 2 images 200; label right |
| Codex Sinaiticus | verified-sinaiticus-sirach-33 | 33.16-21 | a | OK | fol. 174r col. 2: ΩϹ ΚΑΛΑΜΕΝΟϹ ΟΠΙϹΩ ΤΡΥΓΗΤΩΝ (16b) ... ΜΗ ΑΛΛΑΞΗϹ ϹΕΑΥΤΟΝ ΠΑϹΗ ϹΑΡΚΙ (21); fol. 176v col. 2 line 28 (counted) ΚΑΓΩ ΕϹΧΑΤΟϹ ΗΓΡΥΠΝΗϹΑ (16a), followed by 36:10b ΚΑΙ ΚΑΤΕΚΛΗΡΟΝΟΜΗϹΑ: matches note and the transposition explained in the intro |
| Codex Sinaiticus | verified-sinaiticus-sirach-33 | 33.16-21 | b | OK | Greek 16a-21 = KJV 16-20 per the intro mapping (KJV 16 = Gk 16a-17); content checked |
| Codex Sinaiticus | verified-sinaiticus-sirach-33 | 33.16-21 | c | OK | 2 images 200; label CSP transcription; translator "KJV Apocrypha (1611; 1769 text)" |
| Codex Sinaiticus | verified-sinaiticus-isa-53 | 53.1-5 | a | OK | fol. 63r: col. 2 (marg. section no.) ΚΕ ΤΙϹ ΕΠΙϹΤΕΥϹΕΝ ΤΗ ΑΚΟΗ ΗΜΩΝ; col. 3 ΤΩ ΜΩΛΩΠΙ ΑΥΤΟΥ / ΗΜΕΙϹ ΙΑΘΗΜΕΝ then ΠΑΝΤΕϹ ΩϹ ΠΡΟΒΑΤΑ (53:6) |
| Codex Sinaiticus | verified-sinaiticus-isa-53 | 53.1-5 | b/c | OK | Greek 1-5 / KJV 1-5; renders, label right |
| Codex Sinaiticus | verified-sinaiticus-isa-53 | entry | d | DOUBT | texts.json row points at isa-53-Q45_6r_B133.jpg, sections at isa-54-Q45_6r_B133.jpg (duplicate copy of same folio, file named for the wrong chapter); known pending catalog change |
| Codex Sinaiticus | verified-sinaiticus-jer-10 | 10.25 | a | OK | fol. 73v col. 4 last lines ΕΚΧΕΟΝ ΤΟΝ ΘΥΜΟΝ / ϹΟΥ ΕΠΙ ΕΘΝΗ / ... ΜΗ ΕΙΔΟΤΑ ϹΕ ΚΑΙ; Leipzig leaf (stamp BIBL. UNIVERS. LIPS., "20") col. 1 ll. 1-8 ΕΠΙ ΓΕΝΕΑϹ Ε(corr.) ΤΟ ΟΝΟΜΑ ... ΤΟΝ ΝΟΜΟΝ ΑΥΤΟΥ ΗΡΗΜΩϹΑΝ; transcription's "ε" for αι matches the first hand |
| Codex Sinaiticus | verified-sinaiticus-jer-10 | 10.25 | b/c | OK | one verse both sides; 2 images 200; label right |
| Codex Sinaiticus | verified-sinaiticus-john-5 | 5.1-10 | a | OK | fol. 249r col. 4 ~l. 23 ΜΕΤΑ ΤΑΥΤΑ ΗΝ Η ΕΟΡΤΗ ... col. 4 end ΛΕΓΕΙ ΑΥΤΩ Ο ΙϹ; fol. 249v col. 1 l. 1 ΥΓΙΗϹ ΓΕΝΕϹΘΑΙ, l. 27 (counted) ΒΑΚΤΟΝ ϹΟΥ Ο ΔΕ, l. 28 ΑΠΕΚΡΙΝΑΤΟ (5:11) |
| Codex Sinaiticus | verified-sinaiticus-john-5 | 5.1-10 | b | DOUBT | KJV 5:4 shown without Greek and flagged in the intro "Manuscript note" (OK), but KJV 5:3b "waiting for the moving of the water" (also absent: Greek 5:3 ends ξηρων) is not flagged |
| Codex Sinaiticus | verified-sinaiticus-john-5 | 5.1-10 | c | OK | 2 images 200; label CSP transcription matches text; Compare: Tischendorf 8 present |
| Codex Sinaiticus | verified-sinaiticus-mark-16 | 16.6-10 | a | OK | fol. 228r col. 1 (marg. ϲλε) Ο ΔΕ ΛΕΓΕΙ ΑΥΤΑΙϹ / ΜΗ ΕΚΘΑΜΒΕΙϹΘΕ / ΙΗϹΟΥΝ ΖΗΤΕΙ> / ΤΕ ΤΟΝ ΕϹΤΑΥ> ...; col. 2 l. 4 ΤΟ ΓΑΡ then coronis and ΕΥΑΓΓΕΛΙΟΝ ΚΑΤΑ ΜΑΡΚΟΝ |
| Codex Sinaiticus | verified-sinaiticus-mark-16 | 16.6-10 | b | OK | Greek 6-8, KJV 6-10; 16:9-20 absence flagged in intro note; 16.11-15 and 16.16-20 show "[Not present ...]" with the page where Mark ends |
| Codex Sinaiticus | verified-sinaiticus-mark-16 | 16.6-10 | c | DOUBT | Greek shows the scribe's line-filler signs as ">" inside words ("ζητει>τε", "εϲταυ>ρωμενον", "απο > > του"); they are real (seen at line ends on fol. 228r) but nothing on the page explains them. 223 sections in 103 Sinaiticus entries carry ">" |
| Codex Sinaiticus | verified-sinaiticus-acts-8 | 8.33-40 | a | OK | fol. 304r col. 2 l. 13 ΑΥΤΟΥ ΕΝ ΤΗ ΤΑΠΙ/ΝΩϹΕΙ; col. 3 ll. 1-13 ΗΡΠΑϹΕΝ ΤΟΝ ΦΙ/ΛΙΠΠΟΝ ... l. 13 ϹΑΡΙΑΝ |
| Codex Sinaiticus | verified-sinaiticus-acts-8 | 8.33-40 | b/c | OK | KJV 8:37 English without Greek, flagged in intro; audit_sections warning is a false positive (audit looks for "Numbering:", the note is headed "Manuscript note:"); 1 image 200, label right |
| Codex Sinaiticus | verified-sinaiticus-matt-18 | 18.9-16 | a | OK | fol. 209v col. 4 ΚΑΙ ΕΙ Ο Ο> / ΦΘΑΛΜΟϹ ϹΟΥ ϹΚΑ/... ΒΑΛΕ ΑΠΟ > / ϹΟΥ; fol. 210r col. 1 ΕΑΝ ΔΕ ΑΜΑΡΤΗϹΗ (marg. ρπγ), 18:16 ends ϹΤΑΘΗ ΠΑΝ / ΡΗΜΑ before ΕΑΝ ΔΕ ΠΑΡΑΚΟΥϹΗ |
| Codex Sinaiticus | verified-sinaiticus-matt-18 | 18.9-16 | b/c | OK | KJV 18:11 flagged in intro; 2 images 200; label right. Minor: Greek 18:15 has an accented "ὁ" in an unaccented transcription (184 Sinaiticus sections contain such accented letters) |
| Codex Sinaiticus | verified-sinaiticus-john-7 | 7.51-53 | a | OK | fol. 251v col. 4 last line ΜΗ Ο ΝΟΜΟϹ ΗΜΩ; fol. 252r col. 1 l. 1 ΚΡΙΝΙ ΤΟΝ ΑΝΘΡΩ/ΠΟΝ, l. 11 ΚΕΓΕΙΡΕΤΑΙ · ΠΑΛΙ (8:12 follows; no pericope adulterae) |
| Codex Sinaiticus | verified-sinaiticus-john-7 | 7.51-53 | b/c | OK | KJV 7:53 flagged in intro; John 8:1-11 shown as "[Not present ...]" linked to 252r; 2 images 200; label right |
| Codex Sinaiticus | verified-sinaiticus-romans-8 | 8.33-39 | a | OK | fol. 264r col. 4 l. 14 (counted) ΤΙϹ ΕΓΚΑΛΕϹΕΙ ΚΑΤΑ, last line ΟΥΤΕ ΑΡΧΑΙ; fol. 264v col. 1 ll. 1-10 ΟΥΤΕ ΕΝΕϹΤΩΤΑ ... ΧΩ ΙΥ ΤΩ ΚΩ ΗΜΩΝ, l. 11 ΑΛΗΘΕΙΑΝ ΛΕΓΩ (9:1) |
| Codex Sinaiticus | verified-sinaiticus-romans-8 | 8.33-39 | b/c/d | OK | Greek/KJV 33-39; 2 images 200; label right. texts.json row uses romans-8-Q82_3v_B554.jpg vs section romans-7-Q82_3v_B554.jpg (duplicate copy; known pending) |
| Codex Sinaiticus | verified-sinaiticus-2cor-13 | 13.11-14 | b/d | DEFECT | intro "Manuscript note: KJV verse 13:14 is not present in Codex Sinaiticus" is false: fol. 278v col. 2 ll. 2-6 read Η ΧΑΡΙϹ ΤΟΥ ΚΥ ΙΥ ΧΥ ... ΜΕΤΑ ΠΑΝΤΩΝ ΥΜΩΝ (= KJV 13:14, Greek 13:13). Greek 13 (grace) stands beside KJV 13 "All the saints salute you"; numbering difference (Gk 12 = KJV 12-13) mislabelled as an omission (one of the 20 audit warnings) |
| Codex Sinaiticus | verified-sinaiticus-barnabas-21 | 21.6-9 | b/c | DEFECT | English ends with about 3,200 characters of earlychristianwritings.com page text after 21:9: "Go to the Chronological List of all Early Christian Writings Please buy the CD ... copyright © Peter Kirby ... MLA Style ..." and the site's whole author menu ("... Muratorian Canon Kerygmata Petrou Inscription of Abercius"); it renders on /library/verified-sinaiticus-barnabas-21.html. Only entry affected (searched all published JSON) |
| Codex Sinaiticus | verified-sinaiticus-matt-15 | 15.33-39 | b | DOUBT | KJV 15:39 ends "came into the coasts of Magdala," (comma, sentence cut off); the KJV ends the verse with a full stop |
| Codex Sinaiticus | all Sinaiticus | all | d | DOUBT | data/texts.json scans.pages lists only the first page for entries whose sections use 2-3 pages (11 of 12 sampled), and some rows name duplicate files (isa-53-, romans-8-); the fix is listed in qc-sinaiticus-venetus.md as a pending catalog change, not yet applied |
| Leningrad Codex | verified-leningrad-gen-1 | 1.25-31 | a | OK | fol. 1v col. 3: 1:25 ויעש אלהים את חית הארץ למינה mid-column; page ends כדמותנו וירדו בדגת הי[ם] (1:26a). fol. 2r col. 1 opens ובעוף השמים ובבהמה (1:26b); 1:31 וירא אלהים את כל אשר עשה ... יום הששי near foot of col. 1, then ויכלו (2:1). Both pages needed, both linked |
| Leningrad Codex | verified-leningrad-gen-1 | 1.25-31 | b | OK | Hebrew 25-31 and KJV 25-31, same numbering, verse 31 ends "sixth day" in both |
| Leningrad Codex | verified-leningrad-gen-1 | 1.25-31 | c/d | OK | renders; f001b + f002a HTTP 200; label "Hebrew · Leningrad Codex (UXLC)"; no escapes. texts.json scans.pages = section pages (f001b, f002a) |
| Leningrad Codex | verified-leningrad-exod-15 | 15.9-16 | a | OK | fol. 40r (Song of the Sea, brick layout): 15:9 אמר אויב ארדף אשיג; page ends שמעו עמים ירגזון חיל (15:14a). fol. 40v opens אחז ישבי פלשת (15:14b); 15:16 תפל עליהם אימתה ... עם זו קנית in the song block. Both pages linked |
| Leningrad Codex | verified-leningrad-exod-15 | 15.9-16 | b | OK | Hebrew 9-16 = KJV 9-16 |
| Leningrad Codex | verified-leningrad-exod-15 | 15.9-16 | c/d | OK | renders, both images 200, label right; texts.json pages f040a, f040b match |
| Leningrad Codex | verified-leningrad-deut-32 | 32.17-24 | a | OK | fol. 118v (Song of Moses, two-column stichic layout), left column: יזבחו לשדים לא אלה (32:17) and last line ... מוסדי הרים: אספה עלימו (32:22-23a). fol. 119r col. 1 opens רעות חצי אכלה בם מזי רעב (32:23b-24). Both linked |
| Leningrad Codex | verified-leningrad-deut-32 | 32.17-24 | b | OK | Hebrew 17-24 = KJV 17-24 |
| Leningrad Codex | verified-leningrad-deut-32 | 32.17-24 | c/d | OK | renders, f118b + f119a 200, label right; texts.json pages f118b, f119a, f119b = section union |
| Leningrad Codex | verified-leningrad-2kgs-25 | 25.25-30 | a | OK | fol. 220r col. 3: ויהי בחדש השביעי בא ישמעאל בן נתניה (25:25) mid-column; foot ... כסאו (25:28a). fol. 220v col. 1 opens מעל כסא המלכים אשר אתו בבבל (25:28b), ends כל ימי חיו (25:30), then Masoretic book summary and Isaiah 1 (חזון ישעיהו). Both linked |
| Leningrad Codex | verified-leningrad-2kgs-25 | 25.25-30 | b | OK | Hebrew 25-30 = KJV 25-30 |
| Leningrad Codex | verified-leningrad-2kgs-25 | 25.25-30 | c/d | OK | renders, 2 images 200, label right; texts.json f219b, f220a, f220b match |
| Leningrad Codex | verified-leningrad-isa-53 | 53.9-12 | a | OK | fol. 241r middle column: ויתן את רשעים קברו (53:9) ... ואת פשעים נמנה והוא חטא רבים נשא ולפשעים יפגיע (53:12), all on this page; one page linked, correct |
| Leningrad Codex | verified-leningrad-isa-53 | 53.9-12 | b | OK | Hebrew 9-12 = KJV 9-12 |
| Leningrad Codex | verified-leningrad-isa-53 | 53.9-12 | c/d | OK | renders, f241a 200, label right; texts.json f241a matches |
| Leningrad Codex | verified-leningrad-mal-3 | 3.17-24 | a | OK | fol. 325v col. 3 ends והיו לי אמר יהוה צבאות ליום אשר אני עשה סגלה וחמלתי (3:17a). fol. 326r col. 1 opens עליהם כאשר יחמל איש על בנו (3:17b), 3:19 כי הנה היום בא בער כתנור; 3:24 ...והכיתי את הארץ חרם at top of col. 2, then Masoretic lists. Both linked |
| Leningrad Codex | verified-leningrad-mal-3 | 3.17-24 | b | OK | Hebrew 3:19-24 paired with KJV 4:1-6, English markers "4:1".."4:6"; numbering note present; pairing correct (Heb 3:23-24 = KJV 4:5-6 Elijah) |
| Leningrad Codex | verified-leningrad-mal-3 | 3.17-24 | c/d | OK | renders, 2 images 200, label right; texts.json f325b, f326a match. Section header shows only "Malachi 3:17-24" (no KJV 4:1-6 range visible; see 1chr-12 d) |
| Leningrad Codex | verified-leningrad-ps-51 | 51.1-8 | a | OK | fol. 375v (Psalms in 2 columns): right col. Ps 50 מזמור לאסף; left col. למנצח מזמור לדוד בבוא אליו נתן (51:1-2) ... down to ירושלם אז תחפץ זבחי צדק (51:21a) at foot; 51:1-8 entirely on 375v |
| Leningrad Codex | verified-leningrad-ps-51 | 51.1-8 | b | OK | Hebrew 1-8 (superscription = vv.1-2) vs KJV 1-6 (heading printed in v.1); intro: "Hebrew verse n = KJV verse n-2. The KJV heading is shown with verse 1"; English ends KJV 6 "hidden part ... wisdom" = Heb 8 |
| Leningrad Codex | verified-leningrad-ps-51 | 51.1-8 | c/d | OK | renders, f375b 200, label right; texts.json f375b, f376a match |
| Leningrad Codex | verified-leningrad-ps-119 | 119.89-96 | a | OK | fol. 391v left col.: Lamed stanza לעולם יהוה דברך נצב בשמים (89) ... last line לעולם לא אשכח פקודיך כי בם חייתני (93). fol. 392r opens לך אני הושיעני (94), 95, לכל תכלה ראיתי קץ (96). Both linked |
| Leningrad Codex | verified-leningrad-ps-119 | 119.89-96 | b | OK | Hebrew 89-96 = KJV 89-96. English carries the KJV stanza heading "LAMED." which has no Hebrew word (KJV editorial heading; acrostic letter is visible on the page) |
| Leningrad Codex | verified-leningrad-ps-119 | 119.89-96 | c/d | OK | renders, f391b + f392a 200, label right; texts.json 4 pages f391a-f392b match |
| Leningrad Codex | verified-leningrad-job-3 | 3.9-16 | a | OK | fol. 397v left col.: יחשכו כוכבי נשפו (3:9) ... last line ואשקוט ישנתי אז ינוח לי עם מלכים (3:13-14a). fol. 398r opens ויעצי ארץ הבנים חרבות למו (3:14b) ... כעללים לא ראו אור (3:16). Both linked |
| Leningrad Codex | verified-leningrad-job-3 | 3.9-16 | b | OK | Hebrew 9-16 = KJV 9-16 |
| Leningrad Codex | verified-leningrad-job-3 | 3.9-16 | c/d | OK | renders, 2 images 200, label right; texts.json f397b, f398a match |
| Leningrad Codex | verified-leningrad-1chr-12 | 12.1-8 | a | OK | fol. 334v left col.: ואלה הבאים אל דויד לציקלג (12:1); foot וירמיה ויחזיאל ויוחנן ויוזבד הגדרתי אלעוזי (12:5-6a). fol. 335r col. 1 opens וירימות ובעליה ושמריהו (12:6b); 12:8 ויועאלה וזבדיה בני ירחם מן הגדור in line 5. Both linked |
| Leningrad Codex | verified-leningrad-1chr-12 | 12.1-8 | b | OK | Hebrew 1-8 vs KJV 1-7: KJV 12:4 (Ismaiah ... Josabad the Gederathite) correctly covers Heb 12:4+12:5; then Heb n = KJV n-1 |
| Leningrad Codex | verified-leningrad-1chr-12 | 12.1-8 | d | DEFECT | Intro and translator note say "each section's KJV range is listed as english_ref", but english_ref is never rendered (template has no such field; "12:1-7" appears nowhere on the page; header says only "1 Chronicles 12:1-8"). Reader sees an internal field name pointing at nothing, and is not told how the Hebrew/KJV verses differ. Same sentence on 57 Leningrad pages (import_leningrad.py line 582) |
| Leningrad Codex | verified-leningrad-1chr-12 | 12.1-8 | c | OK | renders, f334b + f335a 200, label right, no escapes; texts.json f334b, f335a, f335b match |
| Leningrad Codex | verified-leningrad-2chr-36 | 36.17-23 | a | OK | fol. 365v middle col.: ויעל עליהם את מלך כשדיים ויהרג בחוריהם (36:17); left col. ends יהוה אלהיו עמו ויעל (36:23), then Masoretic summary of Chronicles. One page, correct. (in this codex Chronicles opens the Writings, fol. 327v-365v per the index; the codex ends with Nehemiah on fol. 463r) |
| Leningrad Codex | verified-leningrad-2chr-36 | 36.17-23 | b | OK | Hebrew 17-23 = KJV 17-23; English ends "let him go up" = ויעל |
| Leningrad Codex | verified-leningrad-2chr-36 | 36.17-23 | c/d | OK | renders, f365b 200, label right; texts.json f365a, f365b match |
| Leningrad Codex | verified-leningrad-neh-13 | 13.25-31 | a | OK | fol. 463r (last text page of the codex) right col. foot: ואריב עמם ואקללם ... מבנתיהם לבניכם ולכם (13:25); middle col. הלוא על אלה חטא שלמה (13:26) ... ולבכורים זכרה לי אלהי לטובה (13:31); left col. Masoretic verse/sedarim lists. One page, correct |
| Leningrad Codex | verified-leningrad-neh-13 | 13.25-31 | b | OK | Hebrew 25-31 = KJV 25-31 |
| Leningrad Codex | verified-leningrad-neh-13 | 13.25-31 | c/d | OK | renders, f463a 200, label right; texts.json f462b, f463a match |
| Leningrad Codex | verified-leningrad-josh-21 | 21.33-40 | a | DEFECT | Josh 21:36-37 are not in the Leningrad Codex. fol. 133v col. 1 reads ...ואת נהלל ואת מגרשה ערים ארבע (21:35) and the next line is וממטה גד את עיר מקלט הרצח את רמת (21:38). The section's original_text nevertheless prints vv.36-37 (וממטה ראובן את בצר ... ערים ארבע ס), fully pointed, under "Hebrew · Leningrad Codex (UXLC)" |
| Leningrad Codex | verified-leningrad-josh-21 | 21.33-40 | b | DEFECT | KJV 21:36-37 silently paired with Hebrew taken from outside this manuscript; no note in intro, translator_notes or page (grep "not in/omit/absent" = 0). Cause: import_leningrad.py drops UXLC <x> editorial notes and KJV_ABSENT lists only Neh 7:68 |
| Leningrad Codex | verified-leningrad-josh-21 | 21.33-40 | c | OK | renders, f133b 200, label right; texts.json f132b, f133a, f133b match |
| Leningrad Codex | (all 929 entries) | - | d | OK | data/texts.json scans.pages equals the ordered union of section scan_pages for all 929 Leningrad entries (scripted check, 0 mismatches) |
| Leningrad Codex | (all 929 entries) | - | d | DOUBT | No section has a scan_note; mapping rests on the tanach.us LCIndex only (documented source, allowed by rule 4). 12 of 12 sampled page breaks matched the index exactly on the images |
| Codex Vaticanus | verified-vaticanus-jude-1 | 1.1-7 | a | OK | p. 1443 col. 3 begins ΙΟΥΔΑϹ ΙΥ ΧΥ ΔΟΥΛΟϹ, ends ΤΟΝ ΟΜΟΙΟΝ ΤΡΟΠΟΝ ΤΟΥΤ(οις) at the foot; p. 1444 (rest of v7, vv8-25) not in repo (only page missing from the Vaticanus series, 1443 -> 1445) |
| Codex Vaticanus | verified-vaticanus-jude-1 | 1.1-7 | b/c/d | OK | partial v7 marked "[continues on p. 1444 ...; image not in this library]"; vv8-25 absence stated in intro and verses_not_shown_no_image; labels "Greek · Codex Vaticanus transcription (NTVMR)" + "Compare: Tischendorf 8th edition (1869)"; image 200 |
| Codex Vaticanus | verified-vaticanus-mark-16 | 16.4-8 | a | OK | p. 1303 col. 2 opens ΗΜΙΝ ΤΟΝ ΛΙΘΟΝ ΕΚ ΤΗϹ ΘΥΡΑϹ (end v3) ΚΑΙ ΑΝΑΒΛΕΨΑϹΑΙ, ends ΕΦΟΒΟΥΝΤΟ ΓΑΡ + subscription ΚΑΤΑ ΜΑΡΚΟΝ; col. 3 blank |
| Codex Vaticanus | verified-vaticanus-mark-16 | 16.4-8 | b/d | DEFECT | Mark 16:9-20 silently absent: no section, no "Manuscript note", verses_not_in_manuscript = ""; intro never says Vaticanus ends at 16:8 (blank column visible on the linked page) |
| Codex Vaticanus | verified-vaticanus-luke-22 | 22.37-47 | a | OK | p. 1344 col. 3 line 4 ΛΕΓΩ ΓΑΡ ΥΜΙΝ ΟΤΙ ΤΟΥΤΟ ΤΟ ΓΕΓΡΑΜΜΕΝΟΝ, ends ΚΑΙ Ο ΛΕΓΟΜΕΝΟϹ ΙΟΥΔΑϹ; p. 1345 col. 1 opens ΕΙϹ ΤΩΝ ΔΩΔΕΚΑ ΠΡΟΗΡΧΕΤΟ |
| Codex Vaticanus | verified-vaticanus-luke-22 | 22.37-47 | b | DEFECT | 22:43-44 correctly "[not in Codex Vaticanus]", but the page join is rendered "ιουδαςεις των δωδεκα" (space lost). Systemic: >=85 Vaticanus and >=17 Bezae page joins run two words together (e.g. 2 Pet 1:8 "ακαρπουςκαθιστησιν", Acts 8:26 "φιλιππονλεγων", Luke 4:36 "εξουσιακαι"); Alexandrinus joins are clean |
| Codex Vaticanus | verified-vaticanus-john-8 | 8.1-19 | a/b | OK | p. 1361 col. 3: ΕΡΑΥΝΗϹΟΝ ΚΑΙ ΙΔΕ ... ΟΥΚ ΕΓΕΙΡΕΤΑΙ (7:52) then ΠΑΛΙΝ ΟΥΝ ΑΥΤΟΙϹ ΕΛΑΛΗϹΕΝ (8:12), ends ΚΑΙ ΤΟΝ ΠΑΤΕΡΑ ΜΟΥ ΑΝ ΗΔΕΙΤΕ (8:19); 7:53-8:11 flagged "[not in Codex Vaticanus]" |
| Codex Vaticanus | verified-vaticanus-john-7 | 7.53 | d | DOUBT | Tischendorf comparison for 7:53 is unaccented ("και επορευθησαν εκαστος...") unlike every other edition_text verse: probably not from the stated bolls.life TISCH source. Same page stored twice (vat-b-john-7-f1361.jpg = vat-b-john-8-f1361.jpg, identical md5) |
| Codex Vaticanus | verified-vaticanus-acts-8 | 8.34-40 | a/b/c | OK | p. 1394 col. 2 line 3 ΑΠΟΚΡΙΘΕΙϹ ΔΕ Ο ΕΥΝΟΥΧΟϹ, ends ΕΙϹ ΚΑΙϹΑΡΕΙΑΝ before Ο ΔΕ ϹΑΥΛΟϹ (9:1); 8:37 flagged; renders with both labels |
| Codex Vaticanus | verified-vaticanus-james-1 | 1.20-27 | a/b/c | OK | page-crossing verse: p. 1426 col. 3 ΟΡΓΗ ΓΑΡ ΑΝΔΡΟϹ ... ends ΑϹΠΙΛΟΝ ΕΑΥ; p. 1427 col. 1 opens ΤΟΝ ΤΗΡΕΙΝ ΑΠΟ ΤΟΥ ΚΟϹΜΟΥ; both pages linked |
| Codex Vaticanus | verified-vaticanus-romans-16 | 16.18-24 | a/b | OK | p. 1461 col. 1 opens ΔΕΛΦΟΙ ϹΚΟΠΕΙΝ (16:17), line 7 ΟΙ ΓΑΡ ΤΟΙΟΥΤΟΙ, ends ΚΑΙ ΚΟΥΑΡΤΟϹ Ο ΑΔΕΛΦΟϹ; 16:24 flagged |
| Codex Vaticanus | verified-vaticanus-hebrews-9 | 9.8-14 | a | OK | p. 1518 col. 3 opens ΤΟΥΤΟ ΔΗΛΟΥΝΤΟϹ ΤΟΥ ΠΝΕΥΜΑΤΟϹ, ends ΑΜΩΜΟΝ ΤΩ ΘΩ ΚΑΘΑ (last original page) |
| Codex Vaticanus | verified-vaticanus-hebrews-9 | 9.8-14 | b/d | DEFECT | Greek stops mid-word "καθα" where the original hand breaks off, but English gives all of 9:14; 9:15-28 have no section and neither section nor intro says the manuscript ends here |
| Codex Vaticanus | verified-vaticanus-2cor-13 | 13.9-13 | b | DEFECT | found by cross-check: Greek v12 = KJV 12+13, Greek v13 "η χαρις του κυ ιυ..." stands beside English v13 "All the saints salute you"; KJV v14 dropped; no Numbering note (Alexandrinus 2cor-13 handles the same split correctly) |
| Codex Vaticanus | (all) | - | d | DEFECT | data/texts.json scans.pages lacks a page the sections use in 7 rows: acts-7 (f1390), john-21 (vat-b-acts-1-f1382), luke-12 (f1328), luke-8 (f1319), mark-14 (f1298), mark-6 (f1286), matt-26 (f1271) |
| Codex Vaticanus | (all) | - | images | DOUBT | 199 duplicate page files (same md5 under two chapter names) against the spec's one-file-per-image rule; all 495 images 1024-1119 px long side (spec 1600-2600); legible but small |
| Codex Alexandrinus | verified-alexandrinus-matt-25 | 25.6-13 | a/c | OK | fol. 26r col. 1 opens [Ε]ΞΕΡΧΕϹΘΕ ΕΙϹ ΑΠΑΝΤΗϹΙΝ ΑΥΤΟΥ · ΤΟΤΕ ΗΓΕΡΘΗϹΑΝ; facsimile caption Matt. xxv. 6-35; labels NTVMR + Tischendorf compare |
| Codex Alexandrinus | verified-alexandrinus-matt-25 | 25.6-13 | b | DOUBT | Greek v6 is only its last words (εξερχεσθε εις απαντησιν αυτου) but English gives all of 25:6 with no marker; intro mentions only vv1-5 lost |
| Codex Alexandrinus | verified-alexandrinus-luke-16 | 16.14-24 | a | OK | fol. 58v col. 2 line 6 ΗΚΟΥΟΝ ΔΕ ΤΑΥΤΑ ΠΑΝΤΑ ΚΑΙ ΟΙ ΦΑΡΙϹΑΙΟΙ; fol. 59r col. 1 opens ΤΟ ΑΚΡΟΝ ΤΟΥ ΔΑΚΤΥΛΟΥ ΑΥΤΟΥ; captions Luke xvi. 1-24 / xvi. 24-xvii. 16 |
| Codex Alexandrinus | verified-alexandrinus-luke-16 | 16.14-24 | c/d | OK | Tischendorf fallback correctly labelled "Greek · Tischendorf 8", no Compare box; intro, primary_greek=tischendorf and texts.json row all say Tischendorf |
| Codex Alexandrinus | verified-alexandrinus-john-6 | 6.44-50 | a | OK | fol. 70v col. 2 ends ΤΟΥ ΟΥΝΟΥ ΚΑΤΑΒΑΙΝΩΝ followed by a later "Desunt hic..." note; caption John vi. 22-50 |
| Codex Alexandrinus | verified-alexandrinus-john-6 | 6.44-50 | b | DOUBT | Greek v50 stops at καταβαινων; English gives all of 6:50 ("that a man may eat thereof, and not die") with no marker; intro mentions only vv51-71 |
| Codex Alexandrinus | verified-alexandrinus-acts-8 | 8.33-39 | a/b | OK | fol. 87r col. 2 ... ΟΤΕ ΔΕ ΑΝΕΒΗϹΑΝ ΕΚ ΤΟΥ ΥΔΑΤΟϹ / ΑΓΓΕΛΟϹ ... ΗΡΠΑϹΕΝ ΤΟΝ ΦΙΛΙΠΠΟ(Ν); fol. 87v col. 1 opens ΚΑΙ ΟΥΚ ΕΙΔΕΝ ΑΥΤΟΝ ΟΥΚΕΤΙ; 8:37 flagged. The page also shows ΠΝΑ ΑΓΙΟΝ ΕΠΕΠΕϹΕΝ ΕΠΙ ΤΟΝ ΕΥΝΟΥΧΟ(Ν) (corrector line), left out per the stated first-hand policy |
| Codex Alexandrinus | verified-alexandrinus-1cor-6 | 6.1-11 | a/b | OK | fol. 120r col. 2: ΑΝΑΞΙΟΙ ΕϹΤΕ ΚΡΗΤΗΡΙΩΝ ΕΛΑΧΙϹΤΩΝ · then directly ΗΔΗ ΜΕΝ ΟΥΝ ΗΤΤΗΜΑ (6:7): 6:3-6 omission (homoeoteleuton) confirmed on the image and flagged |
| Codex Alexandrinus | verified-alexandrinus-hebrews-7 | 7.10-16 | a | OK | fol. 141v col. 1 opens ΑΛΛΑ ΚΑΤΑ ΔΥΝΑΜΙΝ ΖΩΗϹ ΑΚΑΤΑΛΥΤΟΥ, so the 141v fix is right; 141r is heavily faded in the facsimile (start of 7:10 not readable by eye; caption Heb. vi. 10-vii. 16 agrees) |
| Codex Alexandrinus | verified-alexandrinus-hebrews-7 | 7.10-16 | d | DOUBT | verification.page_captions gives 141v ntvmr_index "Heb 7:17-28" while the section note and image put the end of 7:16 on 141v col. 1 |
| Codex Alexandrinus | verified-alexandrinus-rev-12 | 12.12-18 | a/b | OK | fol. 154r col. 2 opens (ΑΙ)ΜΑ ΤΟΥ ΑΡΝΙΟΥ (12:11), line 4 ΔΙΑ ΤΟΥΤΟ ΕΥΦΡΑΙΝΕϹΘΑΙ; 12:18 Greek without English, explained |
| Codex Alexandrinus | verified-alexandrinus-rev-12 | 12.12-18 | d | DEFECT | intro has two contradictory Numbering paragraphs: a stale one ("This affects only the Tischendorf comparison text") and the new one (the transcription has 12:18 without English). Same stale paragraph in alexandrinus-2cor-13 and 3john-1 |
| Codex Alexandrinus | verified-alexandrinus-1john-5 | 5.1-9 | a | OK | fol. 109r col. 2 ...ΤΑϹ ΕΝΤΟΛΑϹ ΑΥΤΟΥ ΤΗΡΩΜΕΝ ΚΑΙ ΑΙ ΕΝΤΟΛΑΙ ΑΥΤΟΥ ΒΑΡΙΑΙ ΟΥΚ ΕΙϹΙΝ: transcription's short 5:3 matches the page; v9 runs to 109v (both linked) |
| Codex Alexandrinus | verified-alexandrinus-1john-5 | 5.1-9 | b | DOUBT | English v3 includes the clause A omits ("this is the love of God, that we keep his commandments") and v7-8 carry the Comma Johanneum ("in heaven, the Father, the Word...") absent from A; neither noted |
| Codex Bezae | verified-bezae-matt-1 | 1.20-25 | a | DOUBT | fol. 3v's first line is "παραλαβειν μαριαμ την γυναικα σου το γαρ εν αυτη γεννηθεν", which starts partway through 1:20. 1:20a ("ταυτα δε αυτου ενθυμηθεντος ... μη φοβηθης") is not on the page (the earlier leaves are lost), yet the Tischendorf Greek and KJV show all of 1:20 without a flag. 1:21-25 and 2:1-4a are on the page. |
| Codex Bezae | verified-bezae-matt-1 | 1.20-25 | b | OK | Verse numbers 20-25 match in the Greek and the English. |
| Codex Bezae | verified-bezae-matt-1 | 1.20-25 | c | OK | Renders. 3v.jpg returns 200. The label "Greek · Tischendorf 8" is correct, because this entry falls back to Tischendorf (INTF rights). |
| Codex Bezae | verified-bezae-matt-1 | (all Bezae entries) | d | DEFECT | No Bezae introduction states the lacunae the data skip, against spec rule 10: Matt 1:1-20a (matt-1 starts at 1.20), Matt 6:21-9:1 (matt-6, then matt-9 starting at 9.2), Matt 27:3-11 (27.2, then 27.12), John 1:17-3:25 (john-1, then john-3 starting at 3.26). Only John 20 has a note, about missing images. |
| Codex Bezae | (collection) | - | d | DOUBT | The library has only Matthew (26 entries) and John (19) from Bezae. There is no Mark, Luke or Acts, although each introduction describes the codex as "containing the Gospels and Acts". Nothing tells the reader that coverage is partial. |
| Codex Bezae | verified-bezae-matt-3 | 3.1-7 | a | OK | Fol. 6v carries 2:21b-23, then 3:1 "εν ταις ημεραις εκειναις παραγεινεται ιωαννης ο βαπτιστης", and ends in 3:7 "...τις υπεδειξεν υμιν φυγειν". The rest of 3:7 is on fol. 7v (supplement), which is linked. |
| Codex Bezae | verified-bezae-matt-3 | 3.1-7 | b/c | OK | Verses 1-7 appear on both sides. The label "Greek · Tischendorf 8" is correct for the fallback. Both images return 200. |
| Codex Bezae | verified-bezae-matt-18 | 18.11-19 | a | OK | 59v line 1 is "του εν τοις ουρανοις" (the end of 18:10). Line 2 is "ηλθεν γαρ ο υιος του ανθρωπου σωσαι το απολωλος" (18:11, restored). The page ends with 18:19 "...του πατρος μου του εν ουρανοις". 18:18 is shortened by homoioteleuton in the first hand, with a corrector's supplement in the bottom margin, and the transcription follows the first hand. |
| Codex Bezae | verified-bezae-matt-18 | 18.11-19 | b/c | OK | Verses 11-19 match. The edition text starts at 12 because Tischendorf omits 18:11, which is acceptable. The label reads "Greek · Codex Bezae transcription (NTVMR)", and the edition block reads "Compare: Tischendorf 8th edition (1869)". |
| Codex Bezae | verified-bezae-matt-18 | 18.11-19 | d | DOUBT | The texts.json row's scans.pages (060v, 057v, 058v) leaves out 059v, which is the page carrying 18:11-19. In 33 of 45 Bezae rows, scans.pages leaves out pages that the sections use (a catalog lag). |
| Codex Bezae | verified-bezae-matt-27 | 27.2 | a | OK | Fol. 96v is a torn fragment, and only "...ηγεμονι" is legible on it. The transcription brackets every other word ("[και] [δησαντες] ... η̣γεμονι"), which is honest. |
| Codex Bezae | verified-bezae-john-8 | 8.1-4 | a | OK | Fol. 133v carries 7:44-53, then "ις δε επορευθη εις το ορος των ελαιων" (8:1), and ends 8:4 "...κατειληπται επ αυτοφωρω μοιχευομενη". |
| Codex Bezae | verified-bezae-john-8 | 8.1-4 | b | OK | Verses 1-4 match. KJV 8:2 includes "he sat down, and taught them", which Bezae lacks. This is a reading difference inside a verse, not a whole missing verse. |
| Codex Bezae | verified-bezae-john-12 | 12.24-34 | a | OK | Fol. 152v opens "αμην αμην λεγω υμειν εαν μη ο κοκκος του σιτου" (12:24) and ends "και πως συ λεγεις οτι δει υψωθηναι" (12:34a). 153v is linked for the rest. |
| Codex Bezae | verified-bezae-john-12 | 12.24-34 | b | DEFECT | original_text runs two words together at the page join: "υψωθηναιτον". This is systemic: 24 of 101 Bezae page joins do it. Examples are john-10 "ιεροσολυμοιςχειμων", john-8 "αποκτειναιανθρωπον" and "υμετερωγεγραπται", john-14 "διδυμοςουκ", john-6 "ιηςκαι" and "εστινεκει". The rejoin step treats each Bezae page end (a sense-line end) as a word split across pages. |
| Codex Bezae | verified-bezae-john-12 | 12.24-34 | c | OK | Both images return 200. The NTVMR label is correct. There are no escaped tags. |
| Codex Bezae | verified-bezae-john-18 | 18.3-13 | a | OK | Fol. 168v opens "ιουδας ο παραδιδους αυτον τον τοπον" (18:2) and ends 18:13 "...ος ην αρχιερευς του ενιαυτου εκεινου". 169v (supplement) opens with 18:14 "ην δε καιαφας ο συμβουλευσας". |
| Codex Bezae | verified-bezae-john-18 | 18.3-13 | b/c | OK | Verses 3-13 match. The label "Greek · Tischendorf 8" is correct for this fallback chapter. |
| Codex Bezae | verified-bezae-john-20 | 20.2-13 | a | OK | Fol. 175v (supplement) opens "ετι ουσης εις το μνημιον και βλεπει τον λιθον ηρμενον" (the end of 20:1) and ends "και λεγουσιν αυτη εκεινοι γυναι τι κλαιεις" (20:13a). |
| Codex Bezae | verified-bezae-john-20 | 20.2-13 | b/d | OK | The Greek stops partway through 20:13 while the KJV gives the whole verse. The scan_note and the introduction both say so. The introduction also says that 20:14-31 is not shown because there is no image. |
| Codex Washingtonianus | verified-washingtonianus-matt-5 | 5.11-20 | a | OK | p0012 opens "ενεκεν εμου χαιρετε και αγαλλιασθε" (the end of 5:11) and ends "λεγω γαρ υμιν οτι εαν μη περισσευση" (5:20a). p0013 opens "υμων η δικαιοσυνη πλειον των γραμματεων". All three linked pages are needed. |
| Codex Washingtonianus | verified-washingtonianus-matt-5 | 5.11-20 | b/c | OK | Verses 11-20 match. The label "Greek · Tischendorf 8" is correct, because Matthew is still on Tischendorf. The section has no scan_note, and neither do 256 of the 435 W sections (all of Matthew and Luke). |
| Codex Washingtonianus | verified-washingtonianus-luke-3 | 3.17-24, 3.25-32, 3.33-38 | a | DEFECT | p0211 carries 3:16b-23, ending "ωσει ετων λ ων υιος ως ενομιζετο ιωσηφ", and continues directly with 4:1 "ις δε πληρης πνς αγιου υπεστρεψεν απο του ιορδανου". The genealogy, 3:24-38, is not in the codex. Even so, 15 verses of Tischendorf Greek and KJV are shown linked to p0211 without a flag, because the CSNTM index entry "16-38" for p0211 was taken at face value. |
| Codex Washingtonianus | verified-washingtonianus-luke-3 | 3.17-24 | b/d | DEFECT | Verse numbers match (17-24), but 3:24-38 should be marked "[not in Codex Washingtonianus]" the way Mark 10:48 is. The introduction does not mention the omission. |
| Codex Washingtonianus | verified-washingtonianus-luke-4 | 4.2-11 | a | DEFECT | 4:2 begins on the last line of p0211 ("ημερας μ πειραζομενος υπο του διαβολου") and continues on p0212 ("και ουκ εφαγεν ουδεν εν ταις ημεραις εκειναις"). The section links only p0212. |
| Codex Washingtonianus | verified-washingtonianus-luke-4 | 4.1 (not shown) | a/d | DOUBT | Luke 4:1 is omitted as a CSNTM "index gap" (the introduction says so), but it is plainly visible on p0211. Luke 23:1 is the same: it is omitted, yet visible at the foot of p0302 ("και ανασταν απαν το πληθος αυτων ηγαγον αυτον επι τον πειλατον"). Both could be placed by a visual check, which rule 4 allows. |
| Codex Washingtonianus | verified-washingtonianus-luke-7 | 7.21-30 | a | OK | p0229 opens "εν εκεινη τη ωρα εθεραπευσεν πολλους απο νοσων" (7:21) and ends at 7:28a "...ιωαννου ουδεις εστιν". p0230 opens "ο δε μικροτερος εν τη βασιλεια" and carries 29-30. |
| Codex Washingtonianus | verified-washingtonianus-luke-11 | 11.11-20 | a | OK | p0253 opens "τινα δε εξ υμων τον πατερα αιτησει ο υιος αρτον" (11:11) and ends "ει δε εν δακτυλω θυ εκ[βαλλω] τα δαιμονια" (11:20a). p0254 is linked for the rest. In Luke 7 and 11, the page index agrees with the photographs. The misalignment shows only around Luke 3-4. |
| Codex Washingtonianus | verified-washingtonianus-luke-11 | 11.11-20 | b/c | OK | Verses 11-20 match. The label is Tischendorf 8, which is correct. Both images return 200. |
| Codex Washingtonianus | verified-washingtonianus-john-4 | 4.1-7 | a | OK | p0123 carries 3:31-36, then "ως ουν εγνω ο κς οτι ηκουσαν οι φαρισεοι" with a section number in the margin, and ends "ωρα δε ην ως εκτη και ερ-". p0124 opens "χαιται γυνη". |
| Codex Washingtonianus | verified-washingtonianus-john-4 | 4.1-7 | b | DOUBT | In the IGNTP John text, words split across a page are left split: "και ερ χαιται". This is systemic in W John, about 20 joins, for example "πολ λοι", "γαλι λαιας", "πε πληρωμενην", "σταυ ρωσαι", "κε κλισμενων", "ακο λουθει". That contradicts the stated policy that split words are rejoined. The text also keeps stray "¯" suspension marks ("το¯ κν", "λαμβανω¯", "πε¯τηκοντα"), although the introduction says the overline is not reproduced. |
| Codex Washingtonianus | verified-washingtonianus-john-4 | 4.1-7 | c | OK | The label is "Greek · Codex Washingtonianus transcription (IGNTP)". The edition block is Tischendorf. |
| Codex Washingtonianus | verified-washingtonianus-john-4 | (row) | d | DEFECT | The texts.json row's scans.pages includes w-p0211-FS-7148_01.jpg, which is the Luke 3:16-4:2 page, not John 4. The section data no longer uses it. |
| Codex Washingtonianus | verified-washingtonianus-john-20 | 20.12-19 | a | OK | p0189 opens "[προς] τω μνημειω εξω κλαιουσα" (20:11), carries 20:12 "και θεωρει δυο αγγελους", and ends "και των θυρων κε-". p0190 opens "κλισμενων οπου ησαν οι μαθηται". |
| Codex Washingtonianus | verified-washingtonianus-john-20 | 20.12-19 | b/c | OK | Verses 12-19 match. The IGNTP label is correct. The split "κε κλισμενων" is the issue already noted above. |
| Codex Washingtonianus | verified-washingtonianus-mark-10 | 10.1-12 | a | OK | p0348 carries 9:47b-50, then 10:1 "και εκειθεν αναστας ερχεται εις τα ορια της ιουδαιας", and ends 10:12 "...μοιχαται". 10:13 is on p0349. |
| Codex Washingtonianus | verified-washingtonianus-mark-10 | 10.43-52 | a/b | OK | The omission of 10:48 is confirmed on p0352: "ηρξατο κραζειν και λεγειν υιε δαδ ιυ ελεησον με" is followed directly by "και στας ο ις ειπεν αυτον φωνηθηναι". It is flagged "[not in Codex Washingtonianus]" and has a Manuscript note. p0352 opens partway through 10:42. |
| Codex Washingtonianus | verified-washingtonianus-mark-12 | 12.1-3 | a | OK | p0355 carries the end of 11:25 and then 11:27-33 (11:26 is absent from the codex and flagged). 12:1 "και ηρξατο αυτοις εν παραβολαις λαλειν" follows, and the page ends 12:3 "...και απεστιλαν κενον". |
| Codex Washingtonianus | verified-washingtonianus-mark-16 | 16.13-17 | a | OK | p0373 opens in 16:12 ("...εν ετερα μορφη πορευομενοις") and carries 16:13 "κακεινοι απελθοντες", 16:14, the Freer Logion, and 16:15-17 as far as "εν τω ονοματι μου". p0374 opens "[δαι]μονια εκβαλουσιν". |
| Codex Washingtonianus | verified-washingtonianus-mark-16 | 16.13-17 | b | DOUBT | The Freer Logion (about 450 characters) sits inside verse 14 of the Greek column with no marker, and the English has no counterpart. |
| Codex Washingtonianus | verified-washingtonianus-mark-16 | (intro) | d | DEFECT | The introduction says the logion "is not part of Tischendorf's text or of the KJV and so does not appear in either column; it can be read on the scan". That is stale since the NTVMR swap: the Greek column now prints the logion. |
| Codex Washingtonianus | verified-washingtonianus-mark-16 | 16.13-17 | c | OK | The label is "Greek · Codex Washingtonianus transcription (NTVMR)". The edition block reads "Compare: Tischendorf 8th edition (1869)". Images return 200. |
| 1QIsa-a | verified-1qisaa-isa-1 | 1.1-8 | a | OK | col. I image: line 1 "חזון ישעיהו בן אמוץ אשר חזה על יהודה" at top; line 10 "ונותרה בת ציון כסוכה בכרם ... כעיר נצורה" read on the image |
| 1QIsa-a | verified-1qisaa-isa-1 | 1.1-8 | b,c | OK | verses 1-8 in both columns; label "Hebrew · 1QIsa-a transcription", image 200, no escapes |
| 1QIsa-a | verified-1qisaa-isa-2 | 2.9-15 | a | OK | col. II lines 18-23 read on image: "וישח אדם וישפל איש ועיני גבהות אדם" ... "ועל כול [חומה] בצורה" |
| 1QIsa-a | verified-1qisaa-isa-2 | 2.9-15 | b | DEFECT | scroll lacks 2:9b as well as 2:10 (image: "וישפל איש" runs straight into "ועיני גבהות"); English v.9 still shows "therefore forgive them not" beside Hebrew without it. The "Manuscript note" in the introduction names only 2:10, and the section itself has no flag for either (English v.10 sits beside no Hebrew with no in-section note) |
| 1QIsa-a | verified-1qisaa-isa-2 | 2.9-15 | c | OK | renders, col-02 image 200, labels right, no escapes |
| 1QIsa-a | verified-1qisaa-isa-14 | 14.1-7 | a | OK | col. XI last line "כי ירחם יהוה את יעקוב"; col. XII line 1 "ובחר עוד בישראל", line 9 "כול הארץ פצחו רונה" read on image; both columns linked |
| 1QIsa-a | verified-1qisaa-isa-33 | 33.17-24 | a | OK | col. XXVII: "מלך ביופיו תחזינה עיניך" mid-column; last written line "ובל יואמר שוכן חליתי העם היושב בה נשא עוון", then the blank lower third of the column (scroll's known gap) |
| 1QIsa-a | verified-1qisaa-isa-40 | 40.1-8 | a | OK | last line of col. XXXII "נחמו נחמו עמי יואמר אלוהיכמה דברו על לב ירושלים"; col. XXXIII line 1 "כיא מלא צבאה", line 7 with the supralinear addition and "יקום לעולם" |
| 1QIsa-a | verified-1qisaa-isa-53 | 53.7-12 | a | OK | col. XLIV: "נגש והואה נענה ולוא יפתח פיהו" and "ואת עצומים יחלק שלל" read in lines 12-22 |
| 1QIsa-a | verified-1qisaa-isa-61 | 61.1-6 | a | OK | col. XLIX foot "רוח יהוה עלי יען משח יהוה אותי לבשר ענוים"; col. L line 3 "חיל גואים תואכלו ובכבודם תתיאמרו" |
| 1QIsa-a | verified-1qisaa-isa-66 | 66.17-24 | a | OK | col. LIV line 4 "...המתקדשים והמטהרים אל הגנות"; text ends "...והיו דראון לכול הבשר" around line 18, rest blank; right margin intact in crop (line starts not clipped) |
| 1QIsa-a | (all 8 above) | - | c | OK | all 8 render; images 200; label "Hebrew · 1QIsa-a transcription"; no raw escapes |
| 1QIsa-a | (collection) | - | d | DOUBT | 1QIsa-a sections carry no scan_note ("Where on the image" absent); placement relies on col./line in original_ref only. Ref "col. XLIII lines 0-4" (isa-51 51.9-16) shows an unexplained "line 0" (it is the text the scribe added in the top margin, visible on col-43; label could say so) |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-2 | 2.275-282 (fol. 1r) | a | OK | fol. 1r top "وامره الى الله ومن عاد فاولئك اصحب النار" (2:275 mid); foot "ولا يأب الشهداء اذا ما دعوا" (2:282 mid), matching heading word positions |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-3 | 3.13-24 (fol. 2v) | a | OK | fol. 2v top "...لعبرة لاولى الابصر / زين للناس حب الشهوت"; last line ends "ثم يتولى فريق منهم وهم معرضون ذلك" = 3:24 word 1 as headed; 3:13 shown in full under 2r and 2v as the intro says |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-6 / -7 | 6.162-165 + 7.1-10 (fol. 30r) | a | OK | fol. 30r line 1 "ومحياى ومماتى لله رب العلمين" (6:162 from word 5); blank line, basmala, "المص كتب انزل اليك"; last line "ولقد مكنكم فى الارض وجعلنا" = 7:10 words 1-5 |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-7 | 7.1-10 (fol. 30r) | b | OK | Tanzil verse 1 includes the basmala, Pickthall's verse 1 does not; disclosed in the introduction ("Numbering") |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-9 / -10 | 9.121-129 + 10.1-2 (fol. 44v) | a | OK | fol. 44v: end of sura 9 "حسبى الله لا اله الا هو عليه توكلت وهو رب العرش العظيم" (last lines retraced in darker ink), gap, basmala, "الر تلك ايت الكتب الحكيم"; page ends "...قدم صدق عند" (10:2) |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-15 | 15.19-52 (fol. 54r) | a | OK | 34 verses on one side looked suspicious, but the page is dense (~29 lines): line 1 "مددنها والقينا فيها رواسى" (15:19 from word 2); last line "...ابرهيم اذ دخلوا عليه فقالوا سلما" (15:52) |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-43 | 43.1-23 (fol. 60r) | a | OK | fol. 60r opens with basmala "حم والكتب المبين انا جعلنه قرءنا عربيا"; last line "...وانا على اثرهم مهتدون وكذلك ما ارسلنا" = 43:23 words 1-3 |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-71 / -72 | 71.7-28 + 72.1-2 (fol. 70v) | a | OK | fol. 70v line 1 "واستغشوا ثيابهم واصروا واستكبروا"; foot: basmala, "قل اوحى الى انه استمع نفر من الجن ... يهدى الى" = 72:2 word 2 |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-71 | 71.1-7 (fol. 70r) / 71.7-28 (fol. 70v) | a | DOUBT | headings say 70r "ends at word 8 of 71:7" and 70v "begins at word 10": image of 70r's last line ends "اصبعهم فى اذانهم" (word 9 on 70r). Same one-word gap in 3:13 (2r "ends at word 13", 2v "begins at word 15"). Heading-only off-by-one from Corpus Coranicum word counts; full verse shown under both pages |
| Quran BnF Arabe 328 | (all sampled) | - | c | OK | all render; images 200; label "Arabic · Tanzil Uthmani" (standard text, not called a transcription), English "Marmaduke Pickthall (1930)"; no escapes |
| Quran BnF Arabe 328 | (collection intro) | - | d | DOUBT | introduction says the modern text "differs orthographically from what is on the folio while conveying the same reading"; not checked by the builder and Arabe 328 has non-standard readings and verse divisions in places; should be "usually the same reading" or cite a source |
| Quran BnF Arabe 328 | verified-parisino-petropolitanus-quran-4 | (texts.json row) | d | DOUBT | data/texts.json scans.pages lists pp-f9v.jpg last (string sort) while sections run f9v, f10r ... f20v; catalog thumbnails out of codex order (cosmetic) |
| Poetic Edda | verified-edda-voluspa | 47-64 | a | OK | p13 (fol. 2v, page no. 4 area) line 1 "...hatt bles heimdallr horn e alopti" (st. 46 end), line 2 "ymr iþ aldna tre ... scelfr ygdrasils ask" (st. 47), refrain "Geyr nu g.", foot "Sal ser hon standa solo fegra gulli þaektan a gimle. þar"; p14 line 1 "sculo dyggvar drottir byggia" (st. 64 end) |
| Poetic Edda | verified-edda-voluspa | 47-64 | b | OK | Old Norse has 49, 54, 58 (refrains) without English; introduction and scan_note state Thorpe has no English for them, that 54 is not in R and that R's order differs (48 after 51); Thorpe's 47 = his 48 incl. the refrain, declared |
| Poetic Edda | verified-edda-havamal | 1-15 | a | OK | p14 line 2 "Þar kemr inn dimmi dreki" (Völuspá 66, no st. 65 = consistent with note), large initial G "Gattir allar" (Hávamál 1) at line 4, foot "þagalt oc hugalt sculi þioðans barn" (st. 15) |
| Poetic Edda | verified-edda-havamal | 124-142 | a | OK | p21 (page no. 12) line 1 "goþs laun of geta" (end 123), then "Sifiom er þa blandat" (124); p22 (page no. 13) line 1 "stinna stafi er fáði fimbulþulr" (end 142) |
| Poetic Edda | verified-edda-havamal | 124-142 | b | OK | ON 124 "Sifjum er þá blandat" = Eng "There is a mingling of affection"; ON 132+133 = Eng "132-133" block; 142 "Rúnar munt þú finna" = "Runes thou wilt find"; offsets declared in intro |
| Poetic Edda | verified-edda-volundarkvida | 8-26 | a | OK | p45 (page no. 36) line 1 "gengo inn þaðan endlangan sal"; p46 (page no. 37) line 1 "at it mik fyndit. Snemma kallaði" |
| Poetic Edda | verified-edda-volundarkvida | 8-26 | b | OK | English blocks "15-16" and "19-26" (Thorpe's breaks fall mid-stanza), declared in intro and scan_note |
| Poetic Edda | verified-edda-volundarkvida | 38-41 | a | OK | p47 (page no. 38) line 1 "Hlæjandi volundr hofz at lopti" (st. 38) |
| Poetic Edda | verified-edda-alvissmal | 1-18 | a | OK | p47 holds Völundarkviða 38-41 then Alvíssmál; p48 (page no. 39) line 1 "hialm hulið" (end 18), Alvíssmál ends mid-page, then the Helgakviða initial "Ár var alda" |
| Poetic Edda | verified-edda-grimnismal | 23-24 | a | OK | p27 foot "Fimm hundruð golfa oc um fiorom togom sva hyg[g]" (st. 24 first), p28 line 1 "ec bilscirni m[eð] bugom", then "Fimm hundruð dura" (st. 23): manuscript order 24, 23 as the scan_note says |
| Poetic Edda | verified-edda-thrymskvida | 13-31 | a | OK | p43 (page no. 34) line 1 "Reið varð þá Freyja"; p44 (page no. 35) line 1 "fyrstan þ[ursa] d[rótti]n" (end 31), "Svá kom Óðins sonr endr at hamri" (32) below |
| Poetic Edda | verified-edda-lokasenna | 63-65 | a | OK | p42 (page no. 33) line 1 "Þegi þú rög vættr" (st. 63) |
| Poetic Edda | (all 9 above) | - | c | OK | render; images 200; "Where on the image" notes present; label "Old Norse · heimskringla.no"; translator "Benjamin Thorpe (1866)"; no escapes |
| Poetic Edda | (collection) | - | c,d | DOUBT | column label "Old Norse · heimskringla.no" names a website, not the text (Guðni Jónsson's normalized edition, not the manuscript's spelling); the Old Norse licence is unverified (editor d. 1974), as the verification block itself says |
| Poetic Edda | (texts.json rows) | - | d | DOUBT | qc-legacy.md "Catalog changes needed in data/texts.json (not made)" is now stale: all 11 Edda rows already match the section pages and descriptions. Row captions are bare file names ("codex-regius-p47") not folios; codex-regius-p49..p56 still on disk and unused |
