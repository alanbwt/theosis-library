# QC review: classical and Asian collections (2026-11-12)

Independent reviewer pass over 25 collections plus the Venetus A Iliad (`verified-venetus-`). Read-only: no data, script or site file was changed.

## Method

- Per collection 3 sections (first section of the first entry, middle section of the middle entry, one random), 6 for `rigveda` and `odyssey`: **84 sections**. Picks are listed at the end.
- a. scan: the scan image(s) opened and cropped; first and last lines/words read on the manuscript and compared with the `scan_note` and the section text.
- b. alignment: original vs English range (Stephanus/Bekker/line/verse), boundaries checked against neighbouring sections.
- c. render: `http://localhost:8765/library/<id>.html` fetched; section count, anchor, both text columns non-empty, no escaped HTML, every `<img>` returns 200.
- d. intro/notes/verification and `docs/collections/<key>.md` read for wrong or contradictory claims.
- Extra: a length-ratio scan (English/original characters) over every section of all 26 collections, to find shifted sections outside the sample. Rows marked "(extra)".

## Checker and render results

- `python3 scripts/check_collection.py <key>`: **0 hard failures** for all 25 collections (warnings only: plato-timaeus 12, plato-critias 2, plato-dialogues 1, all "all sections point at one image" for single-page Stephanus entries, which is correct). Venetus (no collection file): equivalent checks run by script, 24 entries / 638 sections, no missing scan, empty text or estimation wording.
- Render: 81 of 84 picked sections render correctly (section counts match JSON, anchors present, both columns filled, all images 200, no raw escapes). **upanishads: DEFECT, no page built** (`/library/verified-upanishads-*.html` 404; 0 of 23 entries in `site/library`, collection absent from `site/collections`). Exception in content: Timaeus 23e renders a stray empty paragraph "Crit. ““" (see table).

## Verdict count

304 rows: DEFECT 31, DOUBT 12, OK 261. DEFECT rows marked "Minor" are wording errors in notes that do not change which page is shown.

## Findings

| collection | entry id | section | check | verdict | evidence |
|---|---|---|---|---|---|
| plato-timaeus | `verified-plato-timaeus-17` | 17a | a-scan | OK | 114r col. b read: title 'Πλάτωνος Τίμαιος ἢ περὶ φύσεως', then 'εἷς δύο τρεῖς· ὁ δὲ δὴ τέταρτος ἡμῖν ὦ φίλε τίμαιε ... ἀσθένειά τις αὐτῷ συνέπεσεν'; col. a ends Republic ('πολιτείας ἢ περὶ δικαίου'). Matches scan_note. |
| plato-timaeus | `verified-plato-timaeus-17` | 17a | b-alignment | OK | Greek 17a ends 'ἀναπληροῦν μέρος;' but English also carries 'Tim. Undoubtedly, and we shall do our best not to come short;' (= Greek 17b 'πάνυ μὲν οὖν ... ἐλλείψομεν'). Few-word Bury/Burnet boundary offset, disclosed in translator_notes. |
| plato-timaeus | `verified-plato-timaeus-17` | 17a | c-render | OK | Page 200, 4/4 sections, anchor s17a, both columns filled, img f114r 200. |
| plato-timaeus | `verified-plato-timaeus-17` | - | d-intro/notes | OK | BnF gr. 1807 (Plato A), c. 850-875, Timaeus 114r-144v, Burnet 1902, Bury 1929 (US PD since 1 Jan 2025) all consistent with data and images. |
| plato-timaeus | `verified-plato-timaeus-55` | 55c | a-scan | OK | 128v col. b opens 'νιῶν δώδεκα ὑπὸ πέντε ἐπιπέδων τριγώνων ἰσοπλεύρων' (as noted); ~line 14 of col. b reads 'ἓξ δὲ τοιαῦτα συμπαγέντα γωνίας ὀκτὼ στερεὰς ἀπετέλεσεν ... γέγονεν κυβικόν' = start of 55c. Section is on this column. |
| plato-timaeus | `verified-plato-timaeus-55` | 55c | b-alignment | OK | Greek 'συμπαγέντα γωνίας ὀκτὼ ... πέρας ἔχοντας, τὸ μὲν' / English 'when joined together, formed eight solid angles ... that of a man unversed'. English runs a few words into 55d (disclosed Bury offset). |
| plato-timaeus | `verified-plato-timaeus-55` | 55c | c-render | OK | Renders, 5/5 sections, img 200. |
| plato-timaeus | `verified-plato-timaeus-23` | 23e | a-scan | OK | 116v col. b opens 'ἐξ ὧν σύ τε καὶ πᾶσα ἡ νῦν πόλις' (23b); foot of col. b reads '... καὶ τῶν ἔργων αὐτοῖς ὃ κάλλιστον ἐπράχθη· τὸ δ' ἀκριβὲς περὶ πάντων ἐφεξῆς εἰς αὖθις κατὰ σχολὴν αὐτὰ τὰ γράμματα λαβόντες'. 23e is on 116v col. b. |
| plato-timaeus | `verified-plato-timaeus-23` | 23e | b-alignment | **DEFECT** | Greek ends with a separate paragraph 'ΚΡ. τὸ δʼ ἀκριβὲς περὶ' and English with an empty paragraph 'Crit. ““'. The words continue the Egyptian priest's sentence (no change of speaker in Burnet or on the MS); the 'ΚΡ.'/'Crit.' label and doubled quotes '””'/'““' are importer artifacts. Same artifact in 22e and 24e English ('Crit. ““Hence...', 'Crit. ““ For the ocean...') and 25d ('settled down.””'). |
| plato-timaeus | `verified-plato-timaeus-23` | 23e | c-render | **DEFECT** | Rendered page shows the stray last paragraph 'Crit. ““' with no text (from JSON). |
| plato-timaeus | (collection) | many | d-intro/notes | **DEFECT** | Systemic: speaker labels injected at every Perseus paragraph split inside Timaeus' monologue, often mid-sentence and in one language only: Greek 'ΤΙ. διὸ' (55e), 'ΤΙ. γῆν' (60e), 'ΤΙ. μεμειγμένη γὰρ' (47e); English 'Tim. and next, that it might be One,' (32d), 'Tim. Wherefore' (74e), empty 'Tim.' (47e). 18 sections have different label counts Greek vs English. plato-dialogues' importer already suppresses repeated labels; Timaeus/Critias do not. |
| plato-critias | `verified-plato-critias-106` | 106a | a-scan | OK | 145r col. a: title 'Πλάτωνος Κριτίας ἢ Ἀτλαντικός μα', then 'ὡς ἅσμενος ὦ σώκρατες οἷον ἐκ μακρᾶς'. Matches. |
| plato-critias | `verified-plato-critias-106` | 106a | b-alignment | OK | Greek 'ὡς ἅσμενος ... σωτηρίαν ἡμῖν αὐτὸν αὐτῶν' = English 'How gladly do I now welcome my release ... that have been rightly said,'. |
| plato-critias | `verified-plato-critias-106` | 106a | c-render | OK | Renders, 3/3 sections, img 200. |
| plato-critias | `verified-plato-critias-114` | 114c | a-scan | OK | 148r (folio number '148' visible) col. b opens 'σιππον μὲν τὸν πρότερον· μήστορα δὲ τὸν ὕστερον· ἐπὶ δὲ τοῖς πέμπτοις τῷ μὲν'. Section listed as 148r col. a-b; correct. |
| plato-critias | `verified-plato-critias-114` | 114c | b-alignment | OK | Same Autochthon...Etruria passage; English adds 'Now a large family of distinguished sons sprang from Atlas;' which is Greek 114d (disclosed Bury offset). |
| plato-critias | `verified-plato-critias-114` | 114c | c-render | OK | Renders, 5/5, img 200. |
| plato-critias | `verified-plato-critias-108` | 108c | a-scan | OK | 145v col. b opens 'γαθοὺς ὄντας ἀναφαίνειν τε καὶ ὑμνεῖν· ὦ φίλε ἑρμόκρατες'. 108c straddles col. a/b of 145v as listed. |
| plato-critias | `verified-plato-critias-108` | 108c | b-alignment | OK | Greek 'τῷδε. ἀλλὰ γὰρ ἀθυμοῦντες ... παραμυθουμένῳ δʼ οὖν καὶ' / English 'But men of faint heart ... trust to your consolation' align. |
| plato-critias | `verified-plato-critias-108` | 108c | c-render | OK | Renders, 5/5, img 200. |
| plato-critias | (collection) | 116e, 119e | d-intro/notes | **DEFECT** | Same mid-monologue label artifact as Timaeus: Greek 'ΚΡΙ. βωμός' (116e), 'ΚΡΙ. ὅτʼ οὖν κατὰ τοὺς' (119e); English 'Crit. And this island,' (115e), 'Crit. And the altar,' (116e) inside Critias' continuous narrative. |
| plato-critias | `verified-plato-critias-110` | 110a/110b | b-alignment (extra, length-ratio scan) | **DOUBT** | English 110a carries 'I point to the statement of Solon, that the Egyptian priests ... mentioned most of those names' which is Greek 110b; English 110b is 191 chars against 436 Greek (Perseus milestone placement, verbatim from Perseus eng2). Larger than the 'few words' offset the notes promise. |
| plato-dialogues | `verified-plato-dialogues-theaetetus-172c-177c` | 172c | a-scan | OK | Clarke 39 f.96v: line 1 '...βοηθοῦντες πρωταγόρᾳ ὡς τὰ μὲν πολλὰ ᾗ δοκεῖ ταύτῃ καὶ ἔστι'; counted line 20 'λάττονος καταλαμβάνει· οὐκοῦν σχολὴν ἄγομεν ὦ σώκρατες'; last line 'ὁ ἀντίδικος ἐφέστηκεν καὶ ὑπογραφὴν παραναγιγνωσκομένην'. All as noted. |
| plato-dialogues | `verified-plato-dialogues-theaetetus-172c-177c` | 172c | b-alignment | OK | Greek 'καταλαμβάνει. ΘΕΟ. οὐκοῦν σχολὴν ...' / English 'a greater one after a lesser, is overtaking us. THEO. ...' same passage (English carries 2 extra words of 172b). |
| plato-dialogues | `verified-plato-dialogues-theaetetus-172c-177c` | 172c | c-render | OK | Renders, 26/26, img 200. |
| plato-dialogues | `verified-plato-dialogues-phaedrus-245c-250c` | 248a | a-scan | OK | f.233v line 1 'δὲ αὐτὰς περιάγει ἡ περιφορά· αἱ δὲ θεωροῦσι τὰ ἔξω τοῦ οὐρανοῦ', line 2 'τὸν δὲ ὑπερουράνιον τόπον', mid-page 'καὶ οὗτος μὲν θεῶν βίος· αἱ δὲ ἄλλαι ψυχαί', last line '...πτεροῦ φύσις ᾧ ψυχὴ κουφίζεται τούτῳ τρέφεται· θεσμός τε'. |
| plato-dialogues | `verified-plato-dialogues-phaedrus-245c-250c` | 248a | b-alignment | OK | English begins 'that which best follows after God' because 'Such is the life of the gods; but of the other souls,' sits at the end of 247e English; disclosed translator-milestone offset. |
| plato-dialogues | `verified-plato-dialogues-phaedrus-245c-250c` | 248a | c-render | OK | Renders, img 200. |
| plato-dialogues | `verified-plato-dialogues-symposium-201d-212c` | 207e | a-scan | OK | f.216r line 1 'τίς αἰτία οὕτως ἐρωτικῶς διατίθεσθαι'; mid-page '...καὶ σάρκα καὶ ὀστᾶ καὶ αἷμα καὶ ξύμπαν τὸ σῶμα· καὶ μὴ ὅτι κατὰ τὸ σῶμα'. 207e on this page. |
| plato-dialogues | `verified-plato-dialogues-symposium-201d-212c` | 207e | b-alignment | OK | Greek 'αἷμα καὶ σύμπαν τὸ σῶμα ... αἱ ἐπιστῆμαι' / English 'his blood and body altogether ... a yet stranger fact:' align (Lamb). |
| plato-dialogues | `verified-plato-dialogues-symposium-201d-212c` | 207e | c-render | OK | Renders, 55/55, img 200. |
| plato-dialogues | (collection) | - | d-intro/notes | **DOUBT** | docs/collections/plato-dialogues.md still says the Republic and Cave were 'Not built' because Shorey 1935 'could not be confirmed as unrenewed'; the plato-republic collection now publishes exactly that with Shorey (renewal check done). Stale doc, not a data error. Translators/years (Fowler 1914/1921, Lamb 1925, Bury 1926) correct. |
| plato-republic | `verified-plato-republic-sun-and-divided-line` | 506d | a-scan | OK | Laur. 80.19 f.72v line 1 'ἔφη· ἀλλὰ σὺ δή ὦ σώκρατες πότερον ἐπιστήμην τὸ ἀγαθὸν φῂς εἶναι'; counted line 13 '... φανά τε καὶ καλά· μὴ πρὸς διός ἦ δ' ὅς ὦ σώ-'. As noted. |
| plato-republic | `verified-plato-republic-sun-and-divided-line` | 506d | b-alignment | OK | Greek 'μὴ πρὸς Διός ... εἰ δὲ μή, ἐᾶν.' = English 'Nay, in heaven's name ... let the matter drop.' |
| plato-republic | `verified-plato-republic-sun-and-divided-line` | 506d | c-render | OK | Renders, 25/25, img 200. |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 517e | a-scan | OK | f.77r line 1 'οἴει τι θαυμαστόν εἰ ἀπὸ θείων ... ἐπὶ τὰ ἀνθρώ-'; 517e (one short reply) follows within the next lines; page carries 517d-518. |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 517e | b-alignment | OK | 'οὐδʼ ὁπωστιοῦν θαυμαστόν, ἔφη.' = 'It would be by no means strange, he said.' (very short section by design). |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 517e | c-render | OK | Renders, 31/31, img 200. |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 519b | a-scan | OK | f.77v foot: '...ἱκανῶς ἄν ποτε πόλιν ἐπιτροπεῦσαι' then the drawn stroke over 1.5 blank lines, then 'μήτε τοὺς ἐν παιδείᾳ ἐωμένους / διατρίβειν διὰ τέλους ... / οὐκ ἔχουσιν ἕνα, οὗ στοχαζομένους δεῖ ἅπαντα πράττειν'; f.78r line 1 'ἃ ἂν πράττωσιν ἰδίᾳ τε καὶ δημοσίᾳ'. Both pages listed; exact. |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 519b | b-alignment | OK | Greek and Shorey English both end with the Islands of the Blest. |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 519b | c-render | OK | Renders, both imgs 200. |
| plato-republic | (collection) | - | d-intro/notes | **DOUBT** | Shorey 1935 PD claim rests on no renewal in CCE 1962-63 lists (grep of the cached lists finds no Shorey; OK as far as checked; Stanford DB not queried). Doc's reason for not using Paris gr. 1807 ('Gallica refuses scripts') contradicts the Timaeus/Critias/Laws collections, which use Paris gr. 1807 images from Gallica. |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 676a | a-scan | OK | f.174r: title 'Πλάτωνος νόμοι ἢ νομοθεσίαι με', col. a 'ταῦτα μὲν οὖν δὴ ταύτῃ· πολιτείας'; col. a ends '...κλυσμοῖς τε καὶ νόσοις καὶ ἄλ-'; col. b 'λοις πολλοῖς ἐν οἷς βραχύ τι'. Matches. |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 676a | b-alignment | OK | Greek and Bury both 676a, same speeches. |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 676a | c-render | OK | Renders, 18/18, img 200. |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 677a | a-scan | OK | Same reading: 677a crosses the col. a/b break at 'ἄλ-/λοις', listed as col. a-b. |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 677a | b-alignment | OK | Greek 'ἆρʼ οὖν ὑμῖν οἱ παλαιοὶ λόγοι ... διανοηθέντες;' = English 'Do you consider ... imagine about it?' |
| plato-laws-3 | `verified-plato-laws-3-rebirth-of-cities` | 681d | a-scan | OK | f.175v col. b ends '...ἀνάγουσι τοῖς ἡγεμόσιν οἷον / βασιλεῦσι φανερὰ δείξαντες'; f.176r col. a opens 'ἑλέσθαι τε δόντες, αὐτοὶ μὲν / νομοθέται κληθήσονται'. Both pages listed; exact. |
| plato-laws-3 | `verified-plato-laws-3-rebirth-of-cities` | 681d | b-alignment | OK | Same passage; English stops before 'What is that?' (in 681e), disclosed Bury-letter offset. |
| plato-laws-3 | `verified-plato-laws-3-rebirth-of-cities` | 681d | c-render | OK | Renders, both imgs 200. |
| plato-laws-3 | (collection) | - | d-intro/notes | OK | Paris gr. 1807 c. 850-875, Burnet vol. 5 1907, Bury Loeb 1926 consistent. |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.6-1176a | a-scan | OK | Paris gr. 1854 f.175r line 1 'καὶ ἡδοναὶ εἶεν ἂν αἱ τούτῳ φαινόμεναι'; mid-page 'εἰρημένων δὲ τῶν περί τε τὰς ἀρετὰς καὶ φιλίας'; last line '...εἴπομεν δὴ ὅτι οὐκ ἔστιν ἕξις· καὶ γὰρ τῷ καθεύδοντι διὰ βίου ὑπάρχοι'; f.175v 'ἄν, φυτῶν ζῶντι βίον'. Exact. |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.6-1176a | b-alignment | OK | Bywater 1176a30-35 = Rackham 'Having now discussed ... deepest misfortune.' |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.6-1176a | c-render | OK | Renders, 9/9, imgs 200. |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.6-1177a | a-scan | OK | f.176v ends '...ἡ δὲ τοῦ βελτίονος κρείττων καὶ εὐδαι-'; f.177r 'μονικωτέρα ἤδη. ἀπολαύσει-/ε τ' ἂν τῶν σωματικῶν ἡδονῶν'. Exact. |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.6-1177a | b-alignment | OK | 1177a1-11 Greek = English '(iii)...(v)... as has been said already.' |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.7-1177b | a-scan | OK | Kb f.121v top '...μένων ὁ μὲν δίκαιος δεῖται πρὸς οὓς', foot '...αὗται δ' ἄσχολοι καὶ τέλους τινὸς ἐφίενται καὶ'; f.122r 'οὐ δι' αὑτὰς αἱρεταί εἰσιν' ... 'ἀλλ' ἐφ' ὅσον ἐνδέχεται ἀθανατίζειν' ... last line 'καὶ τῷ ἀνθρώπῳ δὴ ὁ κατὰ τὸν νοῦν βίος εἴπερ τοῦτο'. Exact. |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 10.7-1177b | b-alignment | OK | 1177b1-34 both ends match ('δόξαι τ' ἂν αὐτὴ μόνη' / 'loved for its own sake'; 'τῷ ὄγκῳ μικρόν ἐστι' / 'small in bulk'). |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | - | d-intro/notes | OK | Kb Laur. 81.11 10th c., Lb Paris gr. 1854 12th c., Bywater 1894, Rackham 1926; Kb lacuna claim agrees with f.121v opening. |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.6 | a-scan | OK | Paris gr. 1853 f.293r line 1 'ἄνθρωπος μὲν γὰρ ἀνθρώπου καθόλου ... πηλεὺς ἀχιλλέως'; c. line 17 'ἐπεὶ δ' ἦσαν τρεῖς οὐσίαι'; last line '...λεύκιππος καὶ πλάτων· ἀεὶ γὰρ εἶναί φασι κίνησιν'.  |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.6 | b-alignment | OK | Ross Greek 1071b3-1072a18 and Ross English both end 'τί οὖν ἄλλας δεῖ ζητεῖν ἀρχάς;' / 'What need then is there to seek for other principles?' |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.6 | c-render | OK | Renders, 5/5, imgs 200. |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.8 | a-scan | OK | f.294r foot: 'ταῦτα μὲν οὖν δῆλα διότι τοῦτον ἔχει τὸν τρόπον· πότερον δὲ μίαν θετέον ...', last line 'ἡ μὲν γὰρ ἀρχὴ καὶ τὸ πρῶτον τῶν ὄντων ἀκί-'. Matches; section spans 294r-295v as listed. |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.8 | b-alignment | OK | Ends agree (1074b14 'φανερὰ μόνον' / 'clear to us'); English opens with 1073a13 sentence 'It is clear, then, why...' which the Greek puts in 12.7 (disclosed). |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.9 | a-scan | OK | f.295v line 1 'ὅτι θεοί τέ εἰσιν οὗτοι καὶ περιέχει τὸ θεῖον τὴν ὅλην φύσιν'; c. line 11 'τὰ δὲ περὶ τὸν νοῦν ἔχει τινὰς ἀπορίας'; last line '...ποτέρως ἔχει ἡ τοῦ ὅλου φύσις τὸ ἀγαθὸν καὶ τὸ ἄριστον'. Exact. |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 12.9 | b-alignment | OK | 1074b15-1075a10 Greek and English both end with 'τὸν ἅπαντα αἰῶνα' / 'throughout eternity...'. |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | - | d-intro/notes | OK | Paris gr. 1853 (E) 10th c., Ross Greek 1924, Ross English 1928 (US PD) consistent. Sections are whole chapters (up to 6,000 Greek characters over 4 pages), coarse but disclosed. |
| hyperborea | `verified-hyperborea-homeric-hymn-7-dionysus` | 0 (1-31) | a-scan | OK | Leiden BPG 33 H f49r: col.1 has red title then 'amphi Dionyson Semeles erikydeos huion' (v.1), margin 5/10 at vv.5/10, col.1 ends 'einai kai desmois ethelon dein argaleoisi' (v.12); col.2 opens 'ton d' ouk ischane desma' (v.13), margin 15/30/35 tally, 'e es hyperboreous' at col.2 line 17, col.2 ends 'autika d' akrotaton para histion' (v.38). vv.1-31 all on 49r. |
| hyperborea | `verified-hyperborea-homeric-hymn-7-dionysus` | 0 (1-31) | b-alignment | OK | Greek 1-31 ends 'epei hemin emballe daimon'; English ends 'now that providence has thrown him in our way' (v.31); next section starts 'When he had said this' = v.32. No gap or overlap. |
| hyperborea | `verified-hyperborea-homeric-hymn-7-dionysus` | all | d-intro/notes | OK | Shelfmark, date (1st half 15th c.), Moscow 1777, sole witness of Demeter, PD Mark all consistent. Minor: intro says Hymn 7 'fills fol. 49r' but 49r col.1 lines 1-13 are the end of Hymn 6 (scan_note itself is correct). |
| hyperborea | `verified-hyperborea-strabo-1-3-22` | 0 (1.3.22) | a-scan | OK | Paris gr. 1397 f34v: page opens 'madyos te tou skythikou'; counted lines: line 16 'oikeian historian. epanimen d' epi ta hexes aph' hon pare-', line 17 '-bemen. tou gar herodotou medenas hyperboreious', line 34 'anemon d' ho autos horos' followed by 1.3.23. Lines 16-34 intact. |
| hyperborea | `verified-hyperborea-strabo-1-3-22` | 0 (1.3.22) | b-alignment | OK | Greek 'Epanimen ... ho autos horos' = whole 1.3.22; English 'We must now return ... these winds have no other limit' = same chapter. |
| hyperborea | `verified-hyperborea-strabo-1-3-22` | all | d-intro/notes | OK | 'Palimpsest' is supported by the BnF manifest ('Parchemin. - 232 fol. - Palimpseste'); dating, NoC-NC, Meineke/Hamilton-Falconer PD claims fine. |
| hyperborea | `verified-hyperborea-strabo-11-6-2` | 0 (11.6.2) | a-scan | OK | Paris gr. 1393 f132v: counting text lines from the first ('...arche haute apo tes kaspias thalattes'), line 12 ends 'kai malista peri ton diastematon. eisple-', line 19 'kai tou adriou katoikountas, hyperboreous elegon kai sauromat(as)', line 25 'grapheon haploteta kai ten philomythian. horontes gar...'. Numbers right; the note's 'margin of one line (a flourish)' sentence is confusing but the numbers count text lines only. |
| hyperborea | `verified-hyperborea-strabo-11-6-2` | 0 (11.6.2) | b-alignment | OK | Greek and English both = all of 11.6.2 ('eispleonti ... philomythian' / 'Upon sailing into the Caspian ... love of fable'). 'Normades' is verbatim from Perseus eng4. |
| hyperborea | `verified-hyperborea-strabo-11-6-2` | all | d-intro/notes | OK | Par. gr. 1393 = Strabo C, 13th-14th c., complete; 1397 ends in book 9: correct. |
| hyperborea | (collection) | - | checker | OK | check_collection.py hyperborea: 16 entries, 43 sections, 0 hard failures, 0 warnings. |
| atlantis | `verified-atlantis-herodotus-4-184-185` | 0 (4.184) | a-scan | OK | Laur. 70.3 f193r line 1 'apo de garamanton di' alleon deka hemereon'; lines 3-4 'esti atlan\|tes' (and 'atlantes' again line 5); counted to line 22 'enypnia horan. mechri men de ton atlanton' where 4.185 begins. Page has 31 lines. |
| atlantis | `verified-atlantis-herodotus-4-184-185` | 0 (4.184) | b-alignment | OK | Greek 184.1-4 and Macaulay 4.184 ('From the Garmantians ... nor have any dreams') same span; 'Garmantians' is verbatim PG 2707. |
| atlantis | `verified-atlantis-herodotus-4-184-185` | all | d-intro/notes | **DOUBT** | Intro: 'a century before Plato's Atlantis' - Herodotus c.430 BCE vs Timaeus/Critias c.360 BCE is about 70 years. Rest (Atlantes reading, BML dating, 31 lines) checks out. |
| atlantis | `verified-atlantis-strabo-2-3-6` | 0 (2.3.6) | a-scan | OK | Paris gr. 1397 f58r, lines counted: 11 'au synchore. tauta men oun ouk eu. to de exairesthai ten', 12 'gen pote', 15-17 'to tou platonos eu paratithesin ... neson tes atlantidos', 29 'eis indous. epicheiresas de aitiasthai' (2.3.7 same line). |
| atlantis | `verified-atlantis-strabo-2-3-6` | 0 (2.3.6) | b-alignment | OK | Greek and English both whole 2.3.6 ('to de exairesthai ... eis Indous' / 'However, he is right ... so many thousand stadia'). Cimbri sentence contradiction is H&F/Kramer and is disclosed in docs/collections/atlantis.md. |
| atlantis | `verified-atlantis-strabo-2-3-6` | all | d-intro/notes | OK | Claims consistent with data; 'earliest surviving discussion' defensible (Crantor survives only via Proclus). |
| atlantis | `verified-atlantis-aelian-varia-historia-3-18` | 0 (3.18) | a-scan | **DEFECT** | Start/end words right but f113r line numbers are off by one: numbering every text line on a ruler crop, the page has 37 lines (first 'autois ... thanat...', last '...georgein de kai speirein oud' autois ergon einai'); the title '+ Peri synousias midou kai silenou +' is line 30, not 31, and the last line is 37, not 38. f113v checked: subtitle line 2, subtitle line 8, Meropes line 9, chapter ends line 18 'emoi de deinos ... kai en allois de' then title of 3.19: correct. |
| atlantis | `verified-atlantis-aelian-varia-historia-3-18` | 0 (3.18) | b-alignment | OK | Greek (Hercher) and Stanley both cover all of 3.18, 'Periegeitai tina Theopompos' / 'Theopompus relates' to 'kai en allois de' / 'as other things'. Cosmetic: Greek carries a U+FEFF before 'lithois' (inherited from Perseus). |
| atlantis | `verified-atlantis-aelian-varia-historia-3-18` | all | d-intro/notes | OK | 10 million (myriasi chiliais), Supp. gr. 352 13th c. bombycin, Stanley 1665 PD consistent. Collection doc says Proclus was excluded by a '200 AD limit' while Aelian (wrote after 200 AD) is included: minor inconsistency. |
| atlantis | (collection) | - | checker | OK | check_collection.py atlantis: 5 entries, 14 sections, 0 hard failures. |
| hesiod-theogony | `verified-hesiod-theogony-proem-muses` | 0 (fol. 240r) | a-scan | OK | f240r lower half under red title: row 1 'Mousaon helikoniadon archometh' aeidein \| haith' helikonos echousin oros mega te zatheon te'; last row 'zenos erigdoupoio thean opi leirioesse \| skidnamene; echei de kare niphoentos olympou' (vv.41-42). |
| hesiod-theogony | `verified-hesiod-theogony-proem-muses` | 0 (fol. 240r) | b-alignment | **DOUBT** | Greek 1-42, English 1-44: English carries vv.43-44 ('and the homes of the immortals. And they ... revered race of the gods'), which are on 240v. Disclosed ('English blocks here: 1-44'); next section's English starts at 45, no duplication. Also 'quick-glancingAphrodite' (missing space: Perseus <note> stripped without a space). |
| hesiod-theogony | `verified-hesiod-theogony-proem-muses` | all | d-intro/notes | OK | Plut. 32.16 paper late 13th c., Planudes, fols. 240r-247v, CC BY-NC-SA, Perseus tlg0020.tlg001 ids correct for the Theogony. |
| hesiod-theogony | `verified-hesiod-theogony-prometheus-pandora` | 1 (fol. 244v) | a-scan | OK | f244v, three verses per row: row 1 'zeu kydiste megiste theon aieigenetaon \| ton d' hele' oppoteren se eni phresi thymos anogei \| phe rha dolophroneon; zeus d' aphthita medea eidos' (548-550); last full-width row ends '...kai hosoi kronou exegenonto' (668). 548-616 lie inside this page. |
| hesiod-theogony | `verified-hesiod-theogony-prometheus-pandora` | 1 (fol. 244v) | b-alignment | **DOUBT** | Greek 548-616, English 550-616: Greek 548-549 have no English here (it is with fol. 244r, whose English runs 507-549). Disclosed in note. English also has 'Melianrace' (missing space from <note> removal). |
| hesiod-theogony | `verified-hesiod-theogony-prometheus-pandora` | all | d-intro/notes | OK | Same intro as other Theogony entries; no data contradictions found for this entry. |
| hesiod-theogony | `verified-hesiod-theogony-wives-and-children-of-zeus` | 1 (fol. 247r) | a-scan | **DEFECT** | Note says f247r begins 'Kadmeie d' ara hoi' (940) and 246v ends at 939. On the image f247r rows 1-3 are 934-939: 'rhinotoro kythereia phobon kai deimon etikte \| deinous hoit' andron pykinas kloneousi phalangas', 'en polemo kryoenti syn arei ptoliportho \| harmonien th' hen kadmos hyperthymos thet' akoitin', 'zeni d' ar' atlantis maie teke kydimon hermen \| keryk' athanaton hieron lechos eisanabasa'; 'Kadmeie' opens row 4. f246v's last row is 'pythmen' echon para metri phile kai patri anakti \| naiei chrysea do deinos theos. autar arei' (932-933). So section 0 (886-939, fol. 246v only) wrongly includes 934-939 and should also list f247r. This section's own 940-962 and page end 991 ('...nychion poiesato daimona dion') are correct. |
| hesiod-theogony | `verified-hesiod-theogony-wives-and-children-of-zeus` | 1 (fol. 247r) | b-alignment | OK | Greek 940-962 and English 940-962 ('And Semele, daughter of Cadmus ... neat-ankled Medea') match. |
| hesiod-theogony | `verified-hesiod-theogony-wives-and-children-of-zeus` | all | d-intro/notes | **DEFECT** | docs/collections/hesiod-theogony.md page map '246v 868-939, 247r 940-991' and the claim that every page boundary was checked from both sides are contradicted by the image (246v = 868-933, 247r = 934-991). |
| hesiod-theogony | (collection) | - | checker | OK | check_collection.py hesiod-theogony: 11 entries, 26 sections, 0 hard failures. |
| hesiod-theogony | (collection) | - | b-alignment | **DEFECT** | Systemic: stripping Perseus <note> tags removed a space in 23 places in Theogony English and 4 in Shield, e.g. 'quick-glancingAphrodite', 'Melianrace', 'allthe', 'Aetherand', 'Cymatolegeand', 'Nemerteswho', 'Iapetusstands', 'backflowingOcean', 'channelledcrucibles', 'capof', 'lionson', 'spoil.She'. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-proem-two-strifes` | 0 (fol. 233r) | a-scan | OK | f233r: row 1 'Mousai pieriethen aoidesi kleiousai \| deute di' ennepete spheteron pater' hymneiousai'; last row 'tois d' ego anti pyros doso kakon ... \| terpontai kata thymon heon kakon amphagapontes' (57-58). 1-41 inside the page. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-proem-two-strifes` | 0 (fol. 233r) | b-alignment | OK | Greek 1-41, English 1-41 ('Muses of Pieria ... mallow and asphodel'). Same span. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-proem-two-strifes` | all | d-intro/notes | **DEFECT** | verification.original_text_source/translation_source cite 'tlg0020.tlg001.perseus-grc2/eng2' (the Theogony) with URL .../tlg0020/tlg002/tlg0020.tlg001...xml (a URL that does not exist). Works and Days is tlg0020.tlg002 (the importer's cache is correct). Same error in all 10 W&D entries. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | 1 (fol. 236v) | a-scan | OK | f236v row 1 'kaumatos idalimou metoporinon ombresantos \| zenos eristheneos meta de trepetai broteos chros' (415-416); last row 'hode ken hadrosyne stachyes neuoien eraze \| ei telos autos opisthen olympios esthlon opazoi' (473-474). |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | 1 (fol. 236v) | b-alignment | OK | Greek 415-474; English begins 'and almighty Zeus sends the autumn rains' (415-416) and ends 'if the Olympian himself gives a good result at the last' (474). 'sultry heat' of 415 sits in section 0, a half-line overlap. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | 2 (fol. 237r) | a-scan | OK | f237r row 1 'ek d' angeon elaseias arachnia; kai se eolpa \| gethesein biotou haireumenon endon eontos' (475-476); last row 'to ikeloi phoitosin aleuomenoi nipha leuken \| kai tote hessasthai eryma chroos hos se keleuo' (535-536). 475-503 inside the page. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | 2 (fol. 237r) | b-alignment | **DEFECT** | Greek ends at 503 'ouk aiei theros esseitai, poieisthe kalias', but the English stops at 501 ('...while he has no sure livelihood'). The English of 502-503 ('While it is yet midsummer command your slaves: It will not always be summer, build barns') is in verified-hesiod-works-and-days-winter-spring-summer section 0 (Greek 504-536), because Perseus card 504 starts with it. The note's 'English blocks here: 475-503' is wrong. |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | all | d-intro/notes | **DEFECT** | Same wrong Perseus ids (tlg001 in tlg002 path) as the proem entry; page map 236v 415-474, 237r 475-536 confirmed on the images. |
| hesiod-works-and-days | (collection) | - | checker | OK | check_collection.py hesiod-works-and-days: 10 entries, 23 sections, 0 hard failures. |
| hesiod-shield | `verified-hesiod-shield-alcmene-and-the-birth-of-heracles` | 0 (fol. 248r) | a-scan | OK | f248r row 1 'e hoie prolipousa domous kai patrida gaian \| elythen es thebas met' areion amphitryona'; last row 'koptomene plektoisin hyph' harmasi kai posin hippon \| harmata d' eupoieta kai antyges ampharabizon' (63-64). |
| hesiod-shield | `verified-hesiod-shield-alcmene-and-the-birth-of-heracles` | 0 (fol. 248r) | b-alignment | OK | Greek 1-64, English 1-64 ('Or like her who left home ... rattled around them'). Same span. |
| hesiod-shield | `verified-hesiod-shield-alcmene-and-the-birth-of-heracles` | all | d-intro/notes | **DEFECT** | verification cites 'tlg0020.tlg001.perseus-grc2/eng2' inside .../tlg0020/tlg003/ (nonexistent URL); the Shield is tlg0020.tlg003. Same in all 4 Shield entries. |
| hesiod-shield | `verified-hesiod-shield-the-shield` | 1 (fol. 249v) | a-scan | OK | f249v row 1 'diphrou epembebaos; para de deimos te phobos te \| hestasan hiemenoi polemon katadymenai andron' (195-196); last row 'pasai d' amph' heni photi machen drimeian ethento \| deina d' es allelas drakon ommasi thymenasai' (261-262). |
| hesiod-shield | `verified-hesiod-shield-the-shield` | 1 (fol. 249v) | b-alignment | **DOUBT** | Greek 195-262, English 195-264 (+2: 'fighting equally with claws and hands. By them stood Darkness of Death, mournful and fearful' = 263-264, which are on 250r). Disclosed; next section English starts 265. English also has 'capof Hades' and 'spoil.She' (missing spaces). |
| hesiod-shield | `verified-hesiod-shield-the-arming-of-heracles` | 0 (fol. 248v) | a-scan | **DEFECT** | Section's own 78-128 are on f248v, but the note's page end is wrong: f248v row 1 'hippon hiemenon; kechareto de kyknos amymon' (65) is right, but the last row is 'deinos aner; koilen de peri stethessi pharetren \| kabbalet' exopithen; polloi d' entosthen oistoi' (129-130), with 'to proton stonoentas ... \| thekato d' amph' omoisin ... sideron' (127-128) the row above. f249r begins 'rhigeloi thanatoio lathiphthongoio doteres \| prosthen men thanaton t' eichon' (131-132). So 129-130 belong on 248v; section 1 (129-153 on f249r) is mis-mapped for those two verses, and docs/collections/hesiod-shield.md page map (248v 65-128, 249r 129-194) is wrong. |
| hesiod-shield | `verified-hesiod-shield-the-arming-of-heracles` | 0 (fol. 248v) | b-alignment | **DOUBT** | Greek 78-128, English 78-129 (+1, 'and across his breast'). Disclosed. Given the image, 129-130 Greek should also be in this section. |
| hesiod-shield | `verified-hesiod-shield-the-arming-of-heracles` | all | d-intro/notes | **DEFECT** | Wrong Perseus ids (tlg001 for tlg003) as above; page map error 248v/249r as above. |
| hesiod-shield | (collection) | - | checker | OK | check_collection.py hesiod-shield: 4 entries, 11 sections, 0 hard failures. |
| homeric-hymns | `verified-homeric-hymns-hymn-1-dionysus` | 0 (fol. 31r a) | a-scan | OK | Leiden f31r col. a line 1 'kai hoi anastesousin agalmata poll' eni neois' (1.10); Hymn 1 ends with 'syn metri semele...' then faded red title; Demeter 1-5 'auten ede thygatra ... paizousan kouresi syn okeanou bathykolpois'; col. a ends 'thaumaston ganoonta ... / athanatois te theois ede thnetois anthropois / tou kai apo rhizes hekaton kara exepephykei' (Dem. 10-12). |
| homeric-hymns | `verified-homeric-hymns-hymn-1-dionysus` | 0 (fol. 31r a) | b-alignment | OK | Greek 10-21 and English 10-21 ('and men will lay up ... whom men call Thyone'). |
| homeric-hymns | `verified-homeric-hymns-hymn-1-dionysus` | all | d-intro/notes | **DOUBT** | Intro calls the Hymns '33 poems' but the collection has Hymns 1-18 only (M ends at 18.4); the 18.5-12 gap is listed, but the absence of Hymns 19-33 is not stated in the entries or docs/collections/homeric-hymns.md (spec rule 10). |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | 11 (fol. 43v a) | a-scan | OK | f43v col. a line 1 'ouk emon ergon touto, paros de moi alla memelen' (266), line 2 'hypnos emoi ge memele...'; last three lines 'all' age me pymaton te kai hystaton hypnon iauses / ek liknou katabaine melaines nyktos hetaire / touto gar oun kai epeita met' athanatois geras hexeis' (289-291). |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | 11 (fol. 43v a) | b-alignment | **DOUBT** | Greek 266-291, English 265-289: starts with v.265 ('Am I like a cattle-lifter') and lacks 290-291 ('get out of your cradle ... prince of robbers'), which are in the next section. Disclosed via block list; no text lost or duplicated overall. |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | 21 (fol. 46r a) | a-scan | OK | f46r col. a line 1 'piston emo thymo kai timion; autar epeita' (528), line 2 'olbou kai ploutou doso perikallea rhabdon'; last lines 'kai dios aigiochoio theon eriounie daimon / semnai gar tines eisi kasignetai gegauiai / parthenoi okeiesin agallomenai pterygessi' (551-553). |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | 21 (fol. 46r a) | b-alignment | **DOUBT** | Greek 528-553, English 530-554: 528-529 English (trusted friend, staff of riches) sits in the previous section; English adds 554 ('heads besprinkled with white meal'). Disclosed offset. |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | all | d-intro/notes | OK | Folio list 40v-46r and missing v.499 consistent with the section list; PD Mark, Evelyn-White 1914 PD. |
| homeric-hymns | (collection) | - | checker | OK | check_collection.py homeric-hymns: 6 entries, 82 sections, 0 hard failures. |
| odyssey | `verified-odyssey-book-13` | fol. 134r | b-alignment (extra, length-ratio scan) | **DEFECT** | Greek holds 13.438-440 but English is only '440 went to goodly Lacedaemon to fetch the son of Odysseus.'; the English of 438-439 ('slung by a twisted cord. So when the two had thus taken counsel together, they parted; and thereupon the goddess') sits at the end of the fol. 133v section, whose Greek stops at 437. |
| odyssey | `verified-odyssey-book-24` | fol. 231v | b-alignment (extra, length-ratio scan) | **DEFECT** | Greek is 24.1-2 only; English runs on through 24.3-4 ('a fair wand of gold, wherewith he lulls to sleep ... wakens even out of slumber;'), which the fol. 232r section's Greek carries; 232r English starts at 24.5. English is cut at Murray's 5-line markers, not at the page's lines. |
| odyssey | `verified-odyssey-book-1` | 0 (fol. 2r) | a-scan | OK | 2r: title '...ὁμήρου' then 19 lines, first 'ἄνδρα μοι ἔννεπε μοῦσα πολύτροπον ὃς μάλα', last 'καὶ μετὰ οἷσι φίλοισι θεοὶ δ' ἐλέαιρον ἅπαντ(ες)'; 1v (later hand, heading 'Odyssea homeri') has the same 19 lines, Ἄνδρα ... ἐλέαιρον ἅπαντες, counted. |
| odyssey | `verified-odyssey-book-1` | 0 (fol. 2r) | b-alignment | OK | Greek 1.1-19 and English blocks 1-19 match exactly: English ends 'And all the gods pitied him' (19); 'save Poseidon' (20) goes to 2v with the Greek. |
| odyssey | `verified-odyssey-book-1` | 0 (fol. 2r) | c-render | OK | render_all: 18/18 sections, both images 200. |
| odyssey | `verified-odyssey-book-1` | entry | d-intro/notes | OK | Translator A. T. Murray (1919) stated identically in all 24 Odyssey entries (verification.translator, translation_source = Perseus perseus-eng3, notes, source line); local eng3 header confirms translator A. T. Murray, Loeb 1919 (eng4 is Butler, not used). Published 1919 = PD in US; claim correct. Book 1 = 2r-10v = 18 pages, 18 sections. |
| odyssey | `verified-odyssey-book-13` | 9 (fol. 129v) | a-scan | OK | 129v: first line 'νῦν δ' οὔτ' ἄρ πῃ θέσθαι ἐπίσταμαι οὐδὲ μὲν αὐτοῦ' (207), last 'εὔχομαι ὥς τε θεῷ καί σευ φίλα γούναθ' ἱκάνω' (231); counted 25 lines = 207-231. |
| odyssey | `verified-odyssey-book-13` | 9 (fol. 129v) | b-alignment | **DEFECT** | English does not stop where the Greek does: Greek 13.207-231, English blocks 205-229 (opens with 205-206 'and had then come to some other of the mighty kings...', which are on 129r; Murray's 230-231 'Nay, save this treasure...' are on 130r). Disclosed 5-line-block method, but 2-line offset at both ends. |
| odyssey | `verified-odyssey-book-13` | 9 (fol. 129v) | c-render | OK | render_all: 19/19 sections, image 200. |
| odyssey | `verified-odyssey-book-13` | entry | d-intro/notes | OK | Same Murray 1919 attribution; Book 13 = 125r-134r, 19 pages = 19 sections, matches doc table. |
| odyssey | `verified-odyssey-book-3` | 0 (fol. 19r) | a-scan | OK | 19r: 2.422-434, ornament/'τέλος τῆς β', heading ὀδυσσείας γ ὁμήρου, then 8 lines: 'Ἠέλιος δ' ἀνόρουσε λιπὼν περικαλλέα λίμνην' ... 'ἥατο καὶ προύχοντο ἑκάστοθι ἐννέα ταύρους' (3.8); counted 8. |
| odyssey | `verified-odyssey-book-3` | 0 (fol. 19r) | b-alignment | **DEFECT** | Greek 3.1-8 but English block 5-9 runs on to 3.9 'Now when they had tasted the inner parts and were burning the thigh-pieces to the god,' whose Greek is on 19v; 19v English starts at 10, so 3.9 English sits under the wrong page. Disclosed block method, 1-line offset. |
| odyssey | `verified-odyssey-book-3` | 0 (fol. 19r) | c-render | OK | render_all: 21/21 sections, image 200. |
| odyssey | `verified-odyssey-book-3` | entry | d-intro/notes | OK | Book 3 = 19r-29r, 21 pages = 21 sections; Murray 1919 consistent. |
| odyssey | `verified-odyssey-book-21` | 17 (fol. 214r) | a-scan | OK | 214r: 11 lines 'τηλέμαχ' οὔ σ' ὁ ξεῖνος ἐνὶ μεγάροισιν ἐλέγχει' (424) ... 'πὰρ θρόνον ἑστήκει κεκορυθμένος αἴθοπι χαλκῷ' (434), ornament row, heading ΟΔΥΣΣΕΙΑΣ Χ, then 22.1-7. Counted 11. |
| odyssey | `verified-odyssey-book-21` | 17 (fol. 214r) | b-alignment | **DEFECT** | Greek 21.424-434, English starts at 425 mid-sentence 'that sits in thy halls brings no shame upon thee'; Murray's 424 'Telemachus, the stranger' is on 213v's section. 1-line offset (disclosed block method). |
| odyssey | `verified-odyssey-book-21` | 17 (fol. 214r) | c-render | OK | render_all: 18/18; IMG MISMATCH is only the footer logo (known artifact). |
| odyssey | `verified-odyssey-book-21` | entry | d-intro/notes | OK | Book 21 = 205v-214r, 18 pages = 18 sections; Murray 1919 consistent. |
| odyssey | `verified-odyssey-book-22` | 14 (fol. 221r) | a-scan | OK | 221r: first 'ἢ γούνων λίσσοιτο προσαΐξας ὀδυσῆα' (337), last 'ὣς φάτο τοῦ δ' ἤκουσε μέδων πεπνυμένα εἰδώς' (361); counted 25 lines. |
| odyssey | `verified-odyssey-book-22` | 14 (fol. 221r) | b-alignment | **DEFECT** | Greek 22.337-361, English blocks 335-359: opens with 335-336 ('and sit down by the well-built altar of great Zeus...', on 220v) and lacks 360-361 ('or he met thee as thou didst rage...So he spoke, and Medon...', given with 221v). 2-line offset each end (disclosed method). |
| odyssey | `verified-odyssey-book-22` | 14 (fol. 221r) | c-render | OK | render_all: 21/21, image 200. |
| odyssey | `verified-odyssey-book-22` | 10 (fol. 219r) | a-scan | OK | 219r: first 'μέντωρ ἀλκιμίδης εὐεργεσίας ἀποτίνειν' (235), last 'ἄλλου δ' ἐν τοίχῳ μελίη πέσε χαλκοβάρεια' (259); counted 25 lines = 235-259. |
| odyssey | `verified-odyssey-book-22` | 10 (fol. 219r) | b-alignment | OK | Greek 22.235-259 and English blocks 235-259 coincide; English ends 'another's ashen spear, heavy with bronze, struck upon the wall.' Neighbours 210-234 / 260-284 abut without gap. |
| odyssey | `verified-odyssey-book-22` | 10 (fol. 219r) | c-render | OK | render_all: 21/21, image 200. |
| odyssey | `verified-odyssey-book-22` | entry | d-intro/notes | OK | Book 22 = 214r-224r, 21 pages = 21 sections; Murray 1919 consistent. odyssey.md mapping/omission notes not contradicted on the pages seen. |
| odyssey | (collection) | - | checker | OK | check_collection.py odyssey: 24 entries, 482 sections, 0 hard failures, 0 warnings. |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 0 (1-3) | a-scan | OK | Photo shows the crumpled tablet with two curved cut-outs at the bottom and '3155' painted at right; in the upper rows 'EDONEM' and 'PELA..' can be made out (line 3 sigma-chedon empelaseias), blurry. One object carries the whole text (by design). |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 0 (1-3) | b-alignment | OK | Greek 1-3 and Murray 1-3 match line for line. |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 1 (4-9) | a-scan | OK | Same single photograph; individual lines 4-9 cannot be read on it (stated in note). |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 1 (4-9) | b-alignment | OK | Greek 4-9 and English 4-9 match line for line. |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 2 (10-14) | a-scan | OK | Same photograph; line 14 along the right edge not verifiable at this resolution (claim is from Harrison). |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 2 (10-14) | b-alignment | OK | Greek 10-14 (12-14 fragments), English 10-11 only; disclosed ('Murray's translation stops after line 11'). |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | all | d-intro/notes | **DEFECT** | Intro: 'The photograph shows the tablet with its chain and case as displayed in the British Museum' - the published image is cropped to the tablet alone on its perspex mount; no chain or case is visible. Licences (CC BY-SA 3.0 photo; Harrison/Murray 1903 PD) fine. |
| orphic-gold-tablets | (collection) | - | checker | OK | check_collection.py orphic-gold-tablets: 1 entry, 3 sections, 0 hard failures. |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | 0 (I.1) | a-scan | OK | Laur. 71.33 f123r: red title 'hermou trismegistou poimandres', red initial, 'Ennoias moi pote genomenes peri ton onton kai meteoristheises moi tes dianoias sphodra'; I.1 ends on line 5; last line '...ex dynamesin anarithmetois on kai kosmon aperioriston gegenemenon' (I.7). |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | 0 (I.1) | b-alignment | OK | Parthey I.1 and Mead I.1 ('It chanced once on a time ... learn and know?') same span. |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | 7 (I.8) | a-scan | OK | f123v line 1 'kai periischesthai to pyr dynamei megiste kai stasin eschekenai kratoumenon' (I.7); line 2 '...dia ton tou poimandrou logon. hos de ... en ekple-' (I.8 starts); line 7 '...kai gennematon psychon. ho de nous ho theos arrenothelys on zoe kai phos' (I.8 ends, I.9 starts). Whole of I.8 on 123v. |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | 7 (I.8) | b-alignment | OK | Parthey I.8 'Hos de en en ekplexei ... gennematon psychon' = Mead 'But as I was in great astonishment ... births of souls'. |
| corpus-hermeticum | `verified-corpus-hermeticum-on-rebirth` | 11 (XIII.12) | a-scan | OK | f143r first line 'syneteth- ... kai ten dodekaten exelaunei; kai etheorethemen'; XIII.12 starts mid-line '...o trismegiste. to skenos touto ... ho diexeleluthamen' and ends '...he de dekas ten henada. pater to pan horo kai emauton en to noi'. On this page. |
| corpus-hermeticum | `verified-corpus-hermeticum-on-rebirth` | 11 (XIII.12) | b-alignment | OK | Parthey XIII.12 'To skenos touto ... ten henada' = Mead 'This dwelling-place ... the Ten the One'. Neighbours 11 and 13 adjoin cleanly. |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | all | d-intro/notes | OK | Laur. 71.33 = A, 14th c., paper, Ficino's exemplar, Ficino 1463, Parthey 1854, Mead 1906 PD (d.1933): consistent. Minor: intro says 'oldest copy ... with page images online' while verification says 'oldest dated witness' (A carries no date). |
| corpus-hermeticum | `verified-corpus-hermeticum-on-rebirth` | all | d-intro/notes | OK | fols. 141v-144r, 'hymnodia' heading 143v, Parthey cap. 13 pp.114-128 and Mead pp.219-233: consistent with sections. |
| corpus-hermeticum | (collection) | - | checker | OK | check_collection.py corpus-hermeticum: 2 entries, 54 sections, 0 hard failures. |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 0 (436-446) | a-scan | OK | 152v lower half: '— μή τοι χλιδῇ δοκεῖτε μηδ' αὐθαδίᾳ' (dash in left margin) through 'ἀλλ' ὧν δέδωκ' εὔνοιαν ἐξηγούμενος' (446); 'οἳ πρῶτα μὲν βλέποντες ἔβλεπον μάτην' 11 lines below 436; page ends 'μύρμηκες ἄντρων ἐν μυχοῖς ἀνηλίοις' (453). |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 0 (436-446) | b-alignment | OK | Smyth Greek 436-446 vs Smyth English 'Nay, impute it not to pride...the friendly purpose that inspired my boons.' = same speech end; matches the archive.org OCR (p. 255). |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 0 (436-446) | c-render | OK | render_all: 9/9, image 200. |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 4 (472-475) | a-scan | OK | 153r: speaker mark 'χ —' at 'πέπονθας αἰκὲς πῆμ' ἀποσφαλεὶς φρενῶν' (472), four lines to 'εὑρεῖν ὁποίοις φαρμάκοις ἰάσιμος' (475), next line marked 'π —' 'τὰ λοιπά μου κλύουσα'. Page top 'ἦν δ' οὐδὲν αὐτοῖς οὔτε χείματος τέκμαρ' (454), 459 is line 6. |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 4 (472-475) | b-alignment | OK | Chorus 472-475 = English 'Thou hast suffered sorrow and humiliation...thine own disease.' exactly (OCR p. 258). |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 4 (472-475) | c-render | OK | render_all: image 200. |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 6 (484-499) | a-scan | OK | 153r: 'τρόπους τε πολλοὺς μαντικῆς ἐστοίχισα' (484) ... 'ἐξωμμάτωσα πρόσθεν ὄντ' ἐπάργεμα' (499); then 500 and last line 'κεκρυμμέν' ἀνθρώποισιν ὠφελήματα' (501). Line 494 reads 'ἔχοντ' ἂν εἴη' (Smyth ἔχουσ', his apparatus 'ἔχοντ': Wieseler'). |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 6 (484-499) | b-alignment | OK | Greek 484-499 vs English 'And I marked out many ways...signs from flames, erstwhile obscure.' Next section begins 'So much then touching these arts' (500). Matches OCR. |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 6 (484-499) | c-render | OK | render_all: image 200. |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | entry | d-intro/notes | OK | Smyth Loeb vol. I 1922 PD; Perseus eng2 header confirms 1988 modernisation, so avoiding it is right; M = Laur. 32.9, 10th c. correct. Partial coverage (436-525) stated. |
| aeschylus-prometheus | (collection) | - | checker | OK | check_collection.py: 1 entry, 9 sections, 0 hard failures. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 0 (6.9) | a-scan | OK | 1r col. a: red title 'SOMNIUM SCIP. M.T.C. EXCERPTUM EX LIBRO SEXTO DE RE PUBLICA', 'Cum in africa venissem M'. manlio consule ad quartam legionem tribun(us)', 6.9 ends 'ille nobis consumptus est dies.' mid-column, then 'Post apparatu regio accep-'. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 0 (6.9) | b-alignment | OK | Mueller 6.9 'Cum in Africam...consumptus est dies' = Keyes 'Scipio. I was military tribune...extended discussion of both.' |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 0 (6.9) | c-render | OK | render_all: 21/21, image 200. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 10 (6.19) | a-scan | OK | 2r col. b (first 'gravissimo autem hic lunaris atque infi-', last 'possint, sed partim obliquos, partim'): 'Hoc sonitu oppletae aures hominum obsurduerunt' ... 'Haec ego admirans referebam tamen oculos ad terram identidem' both inside col. b. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 10 (6.19) | b-alignment | OK | 6.19 Latin and English ('Men's ears, ever filled with this sound...turning my eyes back to earth.') cover the same span; English verified in Keyes OCR. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 10 (6.19) | c-render | OK | render_all: image 200. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 18 (6.27) | a-scan | OK | 3r col. a lower part 'Nam quod semper movetur aeternum est' ... col. a last line 'principium extinctum nec ipsum'; col. b 'ab alia renascetur nec ex se aliud creabit' ... 'qua a primo impulsa moveatur' before 'Cum igitur pateat'. Both columns on the one listed image. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 18 (6.27) | b-alignment | OK | Latin 'Nam quod semper movetur...a primo inpulsa moveatur' = English 'For that which is always in motion...first impulse to motion.' |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 18 (6.27) | c-render | OK | render_all: image 200. |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | entry | d-intro/notes | OK | Keyes Loeb 213 (1928) PD; intro quote 'Know, then, that you are a god' matches 6.26 English and the OCR; five pages fol. 1r-3r, ten columns, red EXPLICIT SOMNIUM and Macrobius title seen on 3r col. b. |
| cicero-dream-of-scipio | (collection) | - | checker | OK | check_collection.py: 1 entry, 21 sections, 0 hard failures. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 0 (1.1-4) | a-scan | OK | Laur. 36.12 1r (abraded): faded title, then 'In nova fert animus mutatas dicere formas / Corpora di coeptis... / Adspirate meis primaque ab origine mundi / Ad mea perpetuum deducite tempora carmen'. Urb. lat. 341 1v (Beneventan, confirmed by letter forms): same 4 lines under large I; last line 'Iussit et ambitae circumdare litora terrae' (1.37). |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 0 (1.1-4) | b-alignment | OK | Magnus 1.1-4 vs More 'My soul is wrought to sing of forms transformed...to this completed time!' - same proem. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 0 (1.1-4) | c-render | OK | render_all: 27/27, both images 200. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 12 (1.168-181) | a-scan | OK | 2r foot: 'Est via sublimis caelo manifesta sereno' (initial E) ... last line 'Celsior ipse loco sceptroque innixus eburno' (178); 2v top 'Terrificam capitis concussit terque quaterque / Caesariem... / Talibus inde modis ora indignantia solvit' (181). Both pages listed. 1.173 reads 'Plebs diversa locis habitat, a fronte potentes' (word order also differs from Magnus; note mentions only 'a fronte'). |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 12 (1.168-181) | b-alignment | OK | Latin 168-181 vs More 'When skies are clear a path...and thus indignantly began to speak;' - ends with 181. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 12 (1.168-181) | c-render | OK | render_all: both images 200. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 13 (1.182-208) | a-scan | OK | 2v: 'Non ego pro mundi regno magis anxius illa' (182, 4th line, large N) ... 'murmura compressit tenuere silentia cuncti', 'Substitit ut clamor...', 'Iuppiter hoc iterum sermone silentia rupit' (208); page runs to 1.238. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 13 (1.182-208) | b-alignment | OK | Latin 182-208 vs More '...Jove once again broke the deep silence with imperial words;' - same end; next section opens with 209. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 13 (1.182-208) | c-render | OK | render_all: image 200. |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | entry | d-intro/notes | OK | Perseus eng3 header = Brookes More 1922 (PD); page spans 55-63 lines consistent; Urb. lat. 341 is visibly Beneventan. Minor: '140 x 275 mm' and 'small manuscript' sit oddly together (unverified). |
| ovid-metamorphoses-1 | (collection) | - | checker | OK | check_collection.py: 1 entry, 27 sections, 0 hard failures. |
| virgil | `verified-virgil-eclogue-4` | 0 (1-3) | a-scan | OK | Vat. lat. 3867 9v: red SAECULI NOVI INTERPRETATIO, red POE in margin, 'SICELIDES MUSAE PAULO MAIORA CANAMUS / NON OMNES ARBUSTA IUVANT HUMILESQUE MYRICAE / SI CANIMUS SILVAS SILVAE SINT CONSULE DIGNAE'; page ends 'PACATUMQUE REGET PATRIIS VIRTUTIBUS ORBEM' (17). |
| virgil | `verified-virgil-eclogue-4` | 0 (1-3) | b-alignment | OK | Lines 1-3 = Rhoades 'Muses of Sicily...woods worthy of a Consul let them be.' |
| virgil | `verified-virgil-eclogue-4` | 0 (1-3) | c-render | OK | render_all: 11/11, image 200. |
| virgil | `verified-virgil-eclogue-4` | entry | d-intro/notes | OK | Rhoades, Poems of Vergil (OUP 1921) confirmed by Perseus header; PD. Romanus 5th c., 18 lines/page consistent with 9v (title + 17). |
| virgil | `verified-virgil-aeneid-6-724-751` | 0 (724-732) | a-scan | OK | Vat. lat. 3225 55r: 21 lines, 'O PATER ANNE ALIQUAS AD CAELUM HINC IRE PUTANDUM' (719) ... 'ERGO EXERCENTUR POENIS VETERUMQUE MALORUM' (739); 'PRINCIPIO CAELUM AC TERRAS CAMPOSQUE LIQUENTIS' is line 6; 'TERRENIQUE HEBETANT ARTUS MORIBUNDAQUE MEMBRA' (732) line 14. |
| virgil | `verified-virgil-aeneid-6-724-751` | 0 (724-732) | b-alignment | **DEFECT** | English stops mid-sentence: Williams '...but bodies vile, With limbs of clay and members born to die,' - the verb 'Encumber and o'ercloud' (= tardant/hebetant, 731-732) opens the next section. Disclosed in notes, but English does not end with 732. |
| virgil | `verified-virgil-aeneid-6-724-751` | 0 (724-732) | c-render | OK | render_all: 3/3, image 200. |
| virgil | `verified-virgil-aeneid-6-724-751` | 1 (733-742) | a-scan | OK | 55r lines 15-21 'HINC METUUNT CUPIUNTQUE...' to 739; 55v 'SUPPLICIA EXPENDUNT ALIAE PANDUNTUR INANES' (740) ... 'INFECTUM ELUITUR SCELUS AUT EXURITUR IGNI' (742); both pages listed. 55v: 751 is line 12, page ends 'ADVERSOS LEGERE ET VENIENTUM DISCERE VULTUS' (755), 16 lines. |
| virgil | `verified-virgil-aeneid-6-724-751` | 1 (733-742) | b-alignment | **DEFECT** | Latin ends 742 'aut exuritur igni' but English ends '...In vast ablution of deep-rolling seas,'; 'Or burned away in fire' is in section 743-751; and it begins with the 731-732 verb 'Encumber and o'ercloud'. Half-line shift at both ends (disclosed). |
| virgil | `verified-virgil-aeneid-6-724-751` | 1 (733-742) | c-render | OK | render_all: both images 200. |
| virgil | `verified-virgil-aeneid-6-724-751` | entry | d-intro/notes | OK | Williams (Houghton Mifflin) per Perseus header; dated 1910 here (first ed. was 1908) - PD either way. 76 leaves, 4th c./c. 400, 21 lines/page consistent with images. |
| virgil | (collection) | - | checker | OK | check_collection.py virgil: 2 entries, 14 sections, 0 hard failures. |
| roman-witnesses | `verified-roman-witnesses-tacitus-annals-15-44` | 0 (15.44 (1)) | a-scan | OK | Plut. 68.2 38r col. b line 9 ends 'Et hec q(ui)de(m) huma-', line 10 'nis consiliis p(ro)uidebant(ur) mox petita dis piacula', line 16 'mariti erant. Sed non ope humana...'; glosses Vulcan/Ceres/Proserpina/Juno in right margin. Line count matches. |
| roman-witnesses | `verified-roman-witnesses-tacitus-annals-15-44` | 0 (15.44 (1)) | b-alignment | OK | Latin 'Et haec quidem...quibus mariti erant' = English 'Such indeed were the precautions...celebrated by married women.' Next part starts 'sed non ope humana'. |
| roman-witnesses | `verified-roman-witnesses-tacitus-annals-15-44` | 0 (15.44 (1)) | c-render | OK | render_all: 5/5, image 200. |
| roman-witnesses | `verified-roman-witnesses-tacitus-annals-15-44` | entry | d-intro/notes | **DOUBT** | Translation dated 'Church and Brodribb (1869)' / 'Annals of Tacitus (London: Macmillan, 1869)'. The 1869 comes from the Perseus header, which cites 'The History of Tacitus' (Macmillan 1869); the Spectator reviewed the Annals translation as new on 11 March 1876 (archive.spectator.co.uk), though Online Books lists an 1869 Annals. First-edition year unconfirmed, likely 1876. PD either way. |
| roman-witnesses | `verified-roman-witnesses-suetonius-claudius-25-4` | 0 (Claud. 25.4) | a-scan | OK | Gud. lat. 268 109v (26 lines counted): l.23 '...ab omni onere immunes praestitis-', l.24 'sent Iudeos impulsore chresto assidue tumultuantes roma', l.26 'simplicitate eorum et fiducia commotus quod in popularia'; 110r l.1 'deducti cum animaduertissent parthos et armenios se-', l.3 '...suam predicantes', l.4 'Druidarum religionem'. Both pages listed. |
| roman-witnesses | `verified-roman-witnesses-suetonius-claudius-25-4` | 0 (Claud. 25.4) | b-alignment | OK | Ihm 25.4 'Iudaeos impulsore Chresto...praedicantes' = Rolfe 'Since the Jews constantly made disturbances...no whit inferior.' |
| roman-witnesses | `verified-roman-witnesses-suetonius-claudius-25-4` | 0 (Claud. 25.4) | c-render | OK | render_all: images 200; IMG MISMATCH = footer logo only. |
| roman-witnesses | `verified-roman-witnesses-suetonius-claudius-25-4` | entry | d-intro/notes | OK | Rolfe Loeb vol. 2 (1914) PD; HAB images PD; Memmianus gap stated. |
| roman-witnesses | `verified-roman-witnesses-suetonius-nero-16-2` | 0 (Nero 16.2) | a-scan | OK | 121r: l.7 'fossa mare veteri urbi inducere', l.8 red M 'Multa sub eo et animadversa severe et coercita nec', l.12 ends 'Afflicti suppliciis', l.13 'xpiani genus hominum superstitionis noue ac malefice', l.16 'mimorum factiones cum ipsis relegate. Aduersus fal-'; 'nota q(uod)' in right margin. |
| roman-witnesses | `verified-roman-witnesses-suetonius-nero-16-2` | 0 (Nero 16.2) | b-alignment | OK | Ihm 16.2 'Multa sub eo...relegatae' = Rolfe 'During his reign many abuses...banished from the city.' |
| roman-witnesses | `verified-roman-witnesses-suetonius-nero-16-2` | 0 (Nero 16.2) | c-render | OK | render_all: image 200; IMG MISMATCH = footer logo only. |
| roman-witnesses | `verified-roman-witnesses-suetonius-nero-16-2` | entry | d-intro/notes | OK | Rolfe 1914 PD; intro claims (line 13 'xpiani', lines 8-16) match the page. |
| roman-witnesses | (collection) | - | checker | OK | check_collection.py roman-witnesses: 3 entries, 7 sections, 0 hard failures. |
| rigveda | `verified-rigveda-1-1` | 0 (1-9) | a-scan | **DEFECT** | Minor, scan_note wording only. fol. 1v has 9 lines. Line 1 श्रीगणेशायनमः हरिः ॐ अग्निं ईळे पुरःऽहितं; 1.1.9 ends ...सचस्व नः स्वस्तये in LINE 7 (the line opening दमे), followed by a red-smudged varga mark and वायो इति आ या. The note says 'ends in line 8'. Line 9 ends ...सोमऽपीतये (1.2.3), which fits fol. 2r starting at 1.2.4. The page assignment is correct. |
| rigveda | `verified-rigveda-1-1` | 0 (1-9) | b-alignment | OK | Aufrecht 1.1.1-9 (agnim īḷe ... svastaye) = Griffith 1-9 (I Laud Agni ... be with us for our weal); <sup> 1-9 in both; padapāṭha edition text same verses; single-section hymn. |
| rigveda | `verified-rigveda-1-1` | 0 | c-render | OK | render_all: 1 section, the f001v image served 200 (logo mismatch is the known footer artifact). |
| rigveda | `verified-rigveda-1-1` | all | d-intro/notes | OK | Item 41 padapāṭha, undated, 7-9 lines/page (this page 9), PD Mark; Griffith 1889-92 / 2nd ed. 1896-97 PD; saṃhitā-plus-padapāṭha display explained; margin reads प॰ऋ॰१ as the note says. |
| rigveda | `verified-rigveda-6-74` | 0 (1-4) | a-scan | OK | fol. 489v last line ...॥१७॥ सोमारुद्रा धारयेथां असुर्यं प्र वां इष्टयः अरं अश्नुवंतु दमेऽदमे (6.74.1 begins). fol. 490r line 1 सप्त रत्ना दधाना शं नः भूतं द्विऽपदे; line 6 ...गोपायतं नः सुऽमनस्यमाना ॥१८॥ जीमूतस्यऽइव (6.74.4 end + 6.75.1); last line ...प्रऽदिशः जयेम (6.75.2). Both pages are listed. |
| rigveda | `verified-rigveda-6-74` | 0 (1-4) | b-alignment | OK | Aufrecht 6.74.1-4 (somārudrā dhārayethām ... sumanasyamānā) = Griffith 1-4 (HOLD fast your Godlike sway ... tender loving-kindness); varga 18 matches the ms ॥१८॥. |
| rigveda | `verified-rigveda-6-74` | 0 | c-render | OK | render_all: both images 200; logo mismatch is the known artifact. |
| rigveda | `verified-rigveda-6-74` | all | d-intro/notes | OK | Intro says fol. 489v-490r, which matches; the margin प॰पं॰१ fits aṣṭaka 5, adhyāya 1 in the ref. |
| rigveda | `verified-rigveda-7-88` | 0 (1-3) | a-scan | OK | fol. 547v line 1 तं दिवि प्रऽइंखं हिरण्ययं (7.87.5 cont.); line 4 ...कृण्वंतः ॥९॥ प्र शुंध्युवं वरुणाय प्रेष्ठां (7.88.1); 7.88.3 ends ईंखयावहै शु\|भे कं over lines 8-9; line 9 वसिष्ठं ह वरुणः नावि आ अधात् (7.88.4, 1st half). Section 4-7 lists 547v+548r, which is correct. |
| rigveda | `verified-rigveda-7-88` | 0 (1-3) | b-alignment | OK | Aufrecht 1-3 (pra śundhyuvaṃ ... śubhe kam) = Griffith 1-3 (PRESENT to Varuṇa ... there be happy); no overlap with section 4-7. |
| rigveda | `verified-rigveda-7-88` | 0 | c-render | OK | render_all OK. |
| rigveda | `verified-rigveda-7-88` | all | d-intro/notes | OK | Intro says fol. 547v-548r, which matches; margin प॰पं॰६ fits adhyāya 6. |
| rigveda | `verified-rigveda-7-87` | 0 (1-4) | a-scan | OK | fol. 547r line 1 उपऽश्रितः चित् अस्तु शं नः क्षेमे ... अस्तु ॥८॥ रदत् पथः वरुणः (7.86.8 end, 7.87.1); line 8 ...युगाय विप्रः उपराय शिक्षन् (7.87.4 end), then तिस्रः द्यावः निऽहिताः ... चक्रे ए- (7.87.5, continued on 547v as तं दिवि). Small slip: the note quotes 'upa-sṛitaḥ' (copied from the typo in the Sansknet padapāṭha); the page reads upa-śritaḥ. |
| rigveda | `verified-rigveda-7-87` | 0 (1-4) | b-alignment | OK | Aufrecht 1-4 (radat patho ... śikṣan) = Griffith 1-4 (Varuṇa cut a pathway ... the race that cometh); section 5-7 lists 547r+547v, which is correct. |
| rigveda | `verified-rigveda-7-87` | 0 | c-render | OK | render_all OK. |
| rigveda | `verified-rigveda-7-87` | all | d-intro/notes | OK | Intro says fol. 547r-547v, which matches. |
| rigveda | `verified-rigveda-10-54` | 1 (4-6) | a-scan | OK | Item 48 fol. 11r line 6 ...चत्वारि ते असुर्याणि नामादाभ्यानि महि- (10.54.4 begins); fol. 11v line 1 -षस्य संति त्वमंग तानि विश्वानि; line 4 ...बृहदुक्थादवाचि, line 5 ॥१५॥ दूरे तन्नाम गुह्यं (10.55.1); line 6 ends ...गुह्यं पुरुस्पृ- (continued on 12r). Both pages are listed; the page has 6 lines, as the intro says. |
| rigveda | `verified-rigveda-10-54` | 1 (4-6) | b-alignment | OK | Aufrecht 4-6 (catvāri te ... avāci) = Griffith 4-6 (Thou, Mighty Steer ... Bṛihaduktha); no padapāṭha text, consistent with a saṃhitā ms. |
| rigveda | `verified-rigveda-10-54` | 1 | c-render | OK | render_all OK (logo artifact). |
| rigveda | `verified-rigveda-10-54` | all | d-intro/notes | OK | Item 48: saṃhitā aṣṭaka 8, 158 leaves, Saṃvat 1768 = 1711 CE, fol. 11r-11v; all consistent with the doc. |
| rigveda | `verified-rigveda-7-97` | 0 (1-3) | a-scan | OK | fol. 552r line 1 -तु भद्रा कृणवत् सरस्वती (7.96.3); line 4 ...प्रऽजां इषं ॥२०॥ यज्ञे दि- (7.97.1); line 8 ...देवऽकृतस्य राजा (7.97.3 end) then आ नः योनिं सद- (7.97.4, continued on 552v as -तु प्रेष्ठः). |
| rigveda | `verified-rigveda-7-97` | 0 (1-3) | b-alignment | OK | Aufrecht 1-3 (yajñe divo ... rājā) = Griffith 1-3 (WHERE Heaven and Earth ... the Gods' creation); section 4-8 lists 552r+552v. |
| rigveda | `verified-rigveda-7-97` | 0 | c-render | OK | render_all OK. |
| rigveda | `verified-rigveda-7-97` | all | d-intro/notes | OK | Intro says fol. 552r-553r, which matches the 3 sections. |
| rigveda | (collection) | - | d-intro/notes | OK | docs/collections/rigveda.md: Items 41/48/35, Griffith gaps (1.179.3-4, 10.61.5-8, 10.86.16-17) and the method agree with the entries checked. |
| rigveda | (collection) | - | checker | OK | check_collection.py rigveda: 1028 entries, 2623 sections, 0 hard failures, 0 warnings. |
| bhagavad-gita | `verified-bhagavad-gita-01` | 0 (1-2) | a-scan | **DEFECT** | Minor, scan_note wording only. fol. 4r (7 lines): l.4 मः ॥९॥ इति न्यासः ॥ धृतराष्ट्र उवाच ॥ धर्मक्षेत्रे कुरुक्षेत्रे; l.5 ...किमकुर्वत संज-; l.6 य ॥१॥ संजय उवाच ॥ दृष्ट्वा तु; l.7 ...वचनमब्रवीत् ॥२॥ पश्यैतां. 1.1's ॥१॥ stands at the START OF LINE 6; the note says 'ends line 5'. The page assignment is correct. |
| bhagavad-gita | `verified-bhagavad-gita-01` | 0 (1-2) | b-alignment | OK | Besant 1.1-2 in Sanskrit and English (Dhritarâshtra said ... spake these words:); section 3-6 lists 4r+4v, with 1.3 beginning at the end of 4r line 7. |
| bhagavad-gita | `verified-bhagavad-gita-01` | 0 | c-render | OK | render_all OK. |
| bhagavad-gita | `verified-bhagavad-gita-01` | all | d-intro/notes | **DEFECT** | Minor. translator_notes say 'Besant prints most Sanskrit colophons ... while HIS English gives the full formula'. Annie Besant was a woman, and the same note appears in every Gita entry. The rest is consistent: Item 559, 90 leaves, 7 lines, Saṃvat 1851 Caitra śu. 3 = 1794; Besant 4th ed. 1922 is PD (pre-1929). '700 verses' in the intro vs '701' in the notes is explained. |
| bhagavad-gita | `verified-bhagavad-gita-10` | 5 (23-27) | a-scan | OK | fol. 50v l.6 ...चेतना ॥२२॥ रुद्राणां शंकरश्चा-, l.7 ...मेरुः शि-; fol. 51r l.1 खरिणामहं ॥२३॥ पुरोधसां; ॥२४॥ l.2, ॥२५॥ l.4, ॥२६॥ l.6, l.7 ...नराधिपं ॥२७॥ आयु- (10.28). Both pages are listed; TEI '50r (=51r)' fits the doc's foliation note. |
| bhagavad-gita | `verified-bhagavad-gita-10` | 5 (23-27) | b-alignment | OK | Besant 23-27 in both layers; 'Asvattha of all tree' is in the cached Wikisource source (verbatim); neighbours 19-22 (50r+50v) and 28-31 (51r+51v) abut. |
| bhagavad-gita | `verified-bhagavad-gita-10` | 5 | c-render | OK | render_all OK. |
| bhagavad-gita | `verified-bhagavad-gita-10` | all | d-intro/notes | OK | fol. 48r-53r; the 10.31 label note is consistent with the doc. Same 'his' pronoun slip as Gita-01. |
| bhagavad-gita | `verified-bhagavad-gita-12` | 6 (colophon) | a-scan | OK | fol. 63v l.1 मत्परमा भक्तास्तेतीव मे प्रियाः ॥२०॥ इति श्रीभगवद्गी- (red); l.3 ...भक्तियोगो नाम द्वादशोध्यायः ॥१२॥ अर्जुन उवा-; l.5 ...केशव ॥१॥; l.7 ...तद्विदः ॥२॥ क्षेत्रज्ञं चापि. Every claim in the note matches. |
| bhagavad-gita | `verified-bhagavad-gita-12` | 6 (colophon) | b-alignment | OK | Besant's abbreviated Sanskrit colophon (इति श्रीमद्भगवद्गीता॰ भक्तियोगो नाम द्वादशोऽध्यायः) and his English 'twelfth discourse, THE YOGA OF DEVOTION' match; the full-form difference on the ms is disclosed. |
| bhagavad-gita | `verified-bhagavad-gita-12` | 6 | c-render | OK | render_all OK (logo artifact). |
| bhagavad-gita | `verified-bhagavad-gita-12` | all | d-intro/notes | OK | fol. 61r-63v, 20 verses; same 'his' pronoun slip in the notes. |
| bhagavad-gita | (collection) | - | d-intro/notes | **DEFECT** | Minor. docs/collections/bhagavad-gita.md says 'his Sanskrit is mostly abbreviated' of Annie Besant. The rest (foliation 41r=42r..51v=52v, 701 verses, Telang rejected) agrees with the data. |
| bhagavad-gita | (collection) | - | checker | OK | 18 entries, 201 sections, 0 hard failures, 0 warnings. |
| upanishads | `verified-upanishads-isa` | 0 (1-9) | a-scan | OK | fol. 1v (11 lines): l.1 श्रीगणेशाय नमः ॐ पूर्णमदः...; l.2 ...ॐ शांतिः ३ ॥ ॐ ईशावास्यमिदं सर्वं यत्किंच जगत्यां जगत्; l.11 ...ततो भूय इव ते तमो य उ विद्यायां रताः ॥ अन्यदेवाहु-. Verse 9 ends in l.11; verse 10 starts there, and section 10-18 lists 1v+2r. |
| upanishads | `verified-upanishads-isa` | 0 (1-9) | b-alignment | OK | GRETIL Kāṇva 1-9 = Müller 1-9 (All this ... greater darkness). The GRETIL typos v.8 'yāthātathyator 'thān' and v.9 'ya uvidyāyāṃ' are copied verbatim from the cached source file, not introduced. |
| upanishads | `verified-upanishads-isa` | 0 | c-render | **DEFECT** | Upanishads pages are not built: /library/verified-upanishads-*.html returns 404 for isa, prasna-5 and katha-6 (logged once for the collection). |
| upanishads | `verified-upanishads-isa` | all | d-intro/notes | OK | Minor imprecision: the intro says 'Verses 1-9 stand on fol. 1v and verses 10-18 on fol. 2r', but verse 10 begins on 1v l.11 (the section's scan_pages are right). Müller SBE 1 (1879) is PD; Item 869 has 16 leaves and 11-13 lines. |
| upanishads | `verified-upanishads-prasna-5` | 1 (5.4-7) | a-scan | OK | fol. 11v has 13 lines: l.12 ends ...महिमानमनुभवति ॥ अथ य-, l.13 दि द्विमात्रेण मनसि संपद्यते ... विभूतिमनु-. fol. 12r l.1 भूय पुनरावर्तते ॥ यः पुनरेतं त्रिमात्रेणो-; l.6 ...अभयं परं चेति ॥५॥ अथ हैनं सुकेशा. Both pages are listed. |
| upanishads | `verified-upanishads-prasna-5` | 1 (5.4-7) | b-alignment | OK | GRETIL 5.4-7 = Müller 4-7 (If he meditate with two Mâtrâs ... the Highest."); 5.1-3 is on 11v alone; no gap. |
| upanishads | `verified-upanishads-prasna-5` | all | d-intro/notes | OK | Müller SBE 15 (1884) is PD; fol. 8v-12v matches the mapping notes (the catalogue range differs, as explained in the doc). |
| upanishads | `verified-upanishads-katha-6` | 0 (2.3.1-8) | a-scan | OK | fol. 8r (13 lines): l.6 सर्वमिदं विभाति ॥ द्वितीयवल्ली ॥ ऊर्ध्वमूलोवाक्शाख एषोश्वत्थः सनातनः; l.13 व्यक्तात्तु परः पुरुषो व्यापको लिंग एव च ॥ यं ज्ञात्वा मुच्यते जंतुरमृतत्वं च गच्छति ॥ न संदृशे तिष्ठति रूपम. Section 9-18 lists 8r+8v. |
| upanishads | `verified-upanishads-katha-6` | 0 (2.3.1-8) | b-alignment | OK | GRETIL (after Olivelle 1998) 2.3.1-8 = Müller VI.1-8 (There is that ancient tree ... obtains immortality). |
| upanishads | `verified-upanishads-katha-6` | all | d-intro/notes | OK | The Müller IV-VI valli numbering, the 4 corrected transcription slips and the saha nāv avatu placement (8v l.11) agree with the mapping notes. |
| upanishads | (collection) | - | checker | OK | 23 entries, 184 sections, 0 hard failures, 0 warnings. |
| daodejing | `verified-daodejing-01` | 0 (Mawangdui A) | a-scan | OK | Plate p.99, odd column labels 89-107. The column over label 93 reads 道可道也 非恆道也 名可名也 非恆名也 无名萬物之始也 有名萬物之母也. Col. 92, to its right, is short and ends ch.79 夫天道无親 恆與善人. Col. 94 reads 恆无欲也以觀其眇 恆有欲也以觀其所噭 兩者同出異名同胃 玄之有玄眾眇之. |
| daodejing | `verified-daodejing-01` | 0 (Mawangdui A) | b-alignment | OK | The silk A text (恆/也/胃 variants, 2 □) is not Wang Bi; Wang Bi is in edition_text. Legge 1-4 covers the whole chapter. The entry says the English follows the received text. |
| daodejing | `verified-daodejing-01` | 0 | c-render | OK | render_all OK. |
| daodejing | `verified-daodejing-01` | all | d-intro/notes | OK | Tomb 3 sealed 168 BCE; A before 195 BCE (邦 not avoided), B 194-180 BCE; 恆/常 avoidance of Liu Heng; Legge SBE 39 (1891) PD; Jicheng 2014 plates on Commons. |
| daodejing | `verified-daodejing-41` | 1 (Mawangdui B) | a-scan | OK | p.142 col. 4上 (between labels 3上/5上): ch.39 是故不欲祿﹦若玉 ... 若石. The 上 at its foot is too small to read at 902 px but sits where expected. Col. 5上: ...大白如辱 廣德如不足 建德如. p.143 col. 4下: ...道堇能行之 中士聞道若存若亡 下士聞道大笑之 弗笑; col. 5下: 大器免成 大音希聲 天象无刑 道褒无名 夫唯道善始且善. Both plates are listed. |
| daodejing | `verified-daodejing-41` | 1 (Mawangdui B) | b-alignment | OK | The silk B text (8 □, as the note counts) ends 善始且善\|成; Legge 41 ¶1-3 and Wang Bi cover the same chapter. The 39-41-40 order is noted. |
| daodejing | `verified-daodejing-41` | 1 | c-render | OK | render_all OK (logo artifact). |
| daodejing | `verified-daodejing-41` | all | d-intro/notes | OK | Same intro as ch.1; visual-checks.tsv B 41 4上 '若石 上' matches the note. |
| daodejing | `verified-daodejing-63` | 0 (Mawangdui A) | a-scan | OK | Plate p.97. The column over label 53 reads ...故為天下貴 為无為 事无事 味无未 大小多少 報怨以德 圖難乎. Col. 54: ...天下之難作於易 天下之大作於細 是以聖人冬不為大故能. Col. 55, lower part: ...是□□人猷難之 故終於无難 (partly worn). |
| daodejing | `verified-daodejing-63` | 0 (Mawangdui A) | b-alignment | OK | 23 □ as stated; Legge 63 ¶1-3 = Wang Bi 63 (edition_text). The silk text is A, not Wang Bi. |
| daodejing | `verified-daodejing-63` | 0 | c-render | OK | render_all OK. |
| daodejing | `verified-daodejing-63` | all | d-intro/notes | OK | Same intro as ch.1; consistent. |
| daodejing | (collection) | - | d-intro/notes | OK | docs/collections/daodejing.md: 902x1360 plates (below the 1600 px target, disclosed); Wikisource transcription not proofread (disclosed); plate-edge overrides noted. |
| daodejing | (collection) | - | checker | OK | 81 entries, 162 sections, 0 hard failures, 0 warnings. |
| verified-venetus | `verified-venetus-iliad-1` | 0 (1.1-25, fol. 12r) | a-scan | OK | VA012RN_0013 = fol. 12r (tab '12r'): heading ΙΛΙΑΔΟΣ ΑΛΦΑ, first line 'μῆνιν ἄειδε θεὰ πηληϊάδεω ἀχιλῆος', last 'ἀλλὰ κακῶς ἀφίει κρατερὸν δ' ἐπὶ μῦθον ἔτελλε'; 25 lines in the central column. Image only 1024 px wide (legible but small). |
| verified-venetus | `verified-venetus-iliad-1` | 0 (1.1-25, fol. 12r) | b-alignment | OK | HMT Greek 1.1-25, Butler English cut before 'Old man' (1.26): ends 'who spoke fiercely to him and sent him roughly away' = 1.25. Next section starts 1.26. |
| verified-venetus | `verified-venetus-iliad-1` | 0 (1.1-25, fol. 12r) | c-render | OK | render_all: 25/25, image 200. |
| verified-venetus | `verified-venetus-iliad-1` | entry | d-intro/notes | **DEFECT** | Intro/source of all 24 Venetus entries (and 48 times in texts.json) spell the editor 'Munro and Allen'; it is D. B. Monro (the translator note itself says 'D. B. Monro'). Also 'lines 1.265 of the standard text are not...' (one line). Licences check out: HMT cex lists vaimg.2017a as CC-attribution-share-alike, release CC BY-NC 4.0. texts.json scans.pages still the 3 old 'representative' pages (qc doc lists the fix as not made). |
| verified-venetus | `verified-venetus-iliad-13` | 16 (13.407-432, fol. 172r) | a-scan | **DEFECT** | Page is right (column 'δινωτὴν φορέεσκε δύω κανόνεσσ' ἀραρυῖαν' to 'κάλλεϊ καὶ ἔργοισιν ἰδὲ φρεσί τοὔνεκα καί μιν'), but the column has 25 lines: 13.422 'μηκιστεὺς ἐχίοιο πάϊς καὶ δῖος ἀλάστωρ' is written at the FOOT of the page (reference mark at 423). scan_note says 422 was 'placed between 13.421 and 13.423' and 'no Iliad line ... below the last' (same in venetus_visual_checks.json): both wrong. |
| verified-venetus | `verified-venetus-iliad-13` | 16 (13.407-432, fol. 172r) | b-alignment | **DEFECT** | Greek 13.407-432 but Murray English 405-434: opens with 405-406 (on 171v) and closes 433-434 'wherefore the best man in wide Troy had taken her to wife - this Alcathous did Poseidon subdue' (on 172v). Disclosed in intro and ref ('English (Murray) 13.405-434'). |
| verified-venetus | `verified-venetus-iliad-13` | 16 (13.407-432, fol. 172r) | c-render | OK | render_all: 33/33, image 200. |
| verified-venetus | `verified-venetus-iliad-13` | entry | d-intro/notes | OK | Book 13, 837 lines, fol. 164r-180r = 33 pages = 33 sections; Murray 1924-25 PD; Munro misspelling as above. |
| verified-venetus | `verified-venetus-iliad-21` | 24 (21.605-611, fol. 282r) | a-scan | OK | VA282RN_0452 = 282r: 7 lines 'ὡς αἰεὶ ἔλποιτο κιχήσεσθαι ποσὶν οἷσι' (605) ... 'ἐς πόλιν ὅν τινα τῶν γε πόδες καὶ γοῦνα σαώσαι' (611), then boxed hypothesis, ΙΛΙΑΔΟΣ Χ and 22.1-7. |
| verified-venetus | `verified-venetus-iliad-21` | 24 (21.605-611, fol. 282r) | b-alignment | OK | Greek 605-611, Murray English 605-611: 'that he ever hoped to overtake him...whomsoever of them his feet and knees might save.' |
| verified-venetus | `verified-venetus-iliad-21` | 24 (21.605-611, fol. 282r) | c-render | OK | render_all: 25/25; IMG MISMATCH = footer logo only. |
| verified-venetus | `verified-venetus-iliad-21` | entry | d-intro/notes | OK | Book 21, 611 lines, fol. 270r-282r = 25 pages = 25 sections; Murray (1924) English is the archaic 1924 style ('Thou fool!'), not the modern revision. Munro misspelling as above. |
| verified-venetus | (no collection file) | - | checker | OK | No check_collection run for Venetus (rows in data/texts.json); qc-sinaiticus-venetus.md records qc2_venetus check: 0 problems. |

## Systemic issues

1. **English cut at the translator's own markers, not at the page.** Odyssey (Murray), Venetus Iliad books 2-24 (Murray), Hesiod (Evelyn-White), Homeric Hymns, Virgil (Williams) and Plato/Bury cut the English where the translator marks a line or Stephanus letter, so a section's English often starts or ends 1-4 lines (or, in Virgil 6.731-732, half a sentence) away from its Greek/Latin. This is disclosed in notes, but it breaks the promise that the English is the same passage: in Odyssey 13 fol. 134r the English has 1 of 3 lines; in Odyssey 24 fol. 231v it has 4 lines against 2 Greek.
2. **Hesiod page maps (Laur. Plut. 32.16) are counted, not read.** Two of nine page joins checked were wrong (Theogony 246v/247r: 247r starts at 934, not 940; Shield 248v/249r: 248v ends at 130, not 128), although the docs say every join was read from both sides. All Theogony and Shield page ends need re-reading on the images.
3. **Speaker labels injected inside monologues (Timaeus, Critias).** The importer prints "ΤΙ./Tim.", "ΚΡ(Ι)./Crit." at every Perseus paragraph split, often mid-sentence and in one language only (18 Timaeus sections differ in label count between Greek and English; e.g. "ΤΙ. διὸ" 55e, empty "Tim." 47e, "Crit. ““" 23e), plus doubled quotation marks "““/””" in 22e-25d. The plato-dialogues importer already suppresses repeated labels; the same rule is missing here.
4. **Lost spaces in Hesiod English** where Perseus `<note>` tags were stripped (27 places: "quick-glancingAphrodite", "Melianrace", "capof Hades", "spoil.She").
5. **Scan notes are not always readings of the image.** Line numbers off by one (Rigveda 1.1, Gita 1.1, Aelian f113r), a quote that copies an edition typo rather than the page (Rigveda 7.87 "upa-sṛitaḥ" vs उपऽश्रितः on the leaf), and the Venetus 13.422 note describing a line position the page contradicts. Page assignments in Rigveda/Gita/Upanishads/Daodejing samples were all correct.
6. **Name and identifier slips repeated across entries:** "Munro" for D. B. Monro (24 Venetus entries, 48 times in texts.json); Works and Days and Shield verification fields cite the Theogony's Perseus id (tlg001) inside tlg002/tlg003 paths; Annie Besant called "his" in every Gita entry and the Gita doc.
7. **Stale or inconsistent docs:** plato-dialogues.md still lists the Republic/Cave as not built; plato-republic.md says Gallica "refuses scripts" for Paris gr. 1807 while three other collections use those Gallica images; homeric-hymns intro speaks of 33 hymns but only 1-18 are present and 19-33 are not listed as a gap.

## Sections picked

| collection | entry id | section index (0-based) |
|---|---|---|
| plato-timaeus | `verified-plato-timaeus-17` | 0 |
| plato-timaeus | `verified-plato-timaeus-55` | 2 |
| plato-timaeus | `verified-plato-timaeus-23` | 4 |
| plato-critias | `verified-plato-critias-106` | 0 |
| plato-critias | `verified-plato-critias-114` | 2 |
| plato-critias | `verified-plato-critias-108` | 2 |
| plato-dialogues | `verified-plato-dialogues-theaetetus-172c-177c` | 0 |
| plato-dialogues | `verified-plato-dialogues-phaedrus-245c-250c` | 13 |
| plato-dialogues | `verified-plato-dialogues-symposium-201d-212c` | 31 |
| plato-republic | `verified-plato-republic-sun-and-divided-line` | 0 |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 15 |
| plato-republic | `verified-plato-republic-allegory-of-the-cave` | 21 |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 0 |
| plato-laws-3 | `verified-plato-laws-3-rebirth-of-cities` | 8 |
| plato-laws-3 | `verified-plato-laws-3-floods-and-survivors` | 3 |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 0 |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 4 |
| aristotle-ethics | `verified-aristotle-ethics-nicomachean-10-6-8` | 2 |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 0 |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 2 |
| aristotle-metaphysics | `verified-aristotle-metaphysics-lambda-6-10` | 3 |
| hyperborea | `verified-hyperborea-homeric-hymn-7-dionysus` | 0 |
| hyperborea | `verified-hyperborea-strabo-1-3-22` | 0 |
| hyperborea | `verified-hyperborea-strabo-11-6-2` | 0 |
| atlantis | `verified-atlantis-herodotus-4-184-185` | 0 |
| atlantis | `verified-atlantis-strabo-2-3-6` | 0 |
| atlantis | `verified-atlantis-aelian-varia-historia-3-18` | 0 |
| hesiod-theogony | `verified-hesiod-theogony-proem-muses` | 0 |
| hesiod-theogony | `verified-hesiod-theogony-prometheus-pandora` | 1 |
| hesiod-theogony | `verified-hesiod-theogony-wives-and-children-of-zeus` | 1 |
| hesiod-works-and-days | `verified-hesiod-works-and-days-proem-two-strifes` | 0 |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | 1 |
| hesiod-works-and-days | `verified-hesiod-works-and-days-ploughing` | 2 |
| hesiod-shield | `verified-hesiod-shield-alcmene-and-the-birth-of-heracles` | 0 |
| hesiod-shield | `verified-hesiod-shield-the-shield` | 1 |
| hesiod-shield | `verified-hesiod-shield-the-arming-of-heracles` | 0 |
| homeric-hymns | `verified-homeric-hymns-hymn-1-dionysus` | 0 |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | 11 |
| homeric-hymns | `verified-homeric-hymns-hymn-4-hermes` | 21 |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 0 |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 1 |
| orphic-gold-tablets | `verified-orphic-gold-tablets-petelia` | 2 |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | 0 |
| corpus-hermeticum | `verified-corpus-hermeticum-on-rebirth` | 11 |
| corpus-hermeticum | `verified-corpus-hermeticum-poimandres` | 7 |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 0 |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 4 |
| aeschylus-prometheus | `verified-aeschylus-prometheus-436-525-the-gifts-of-prometheus` | 6 |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 0 |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 10 |
| cicero-dream-of-scipio | `verified-cicero-dream-of-scipio-somnium-scipionis` | 18 |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 0 |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 13 |
| ovid-metamorphoses-1 | `verified-ovid-metamorphoses-1-creation-to-flood` | 12 |
| virgil | `verified-virgil-eclogue-4` | 0 |
| virgil | `verified-virgil-aeneid-6-724-751` | 1 |
| virgil | `verified-virgil-aeneid-6-724-751` | 0 |
| roman-witnesses | `verified-roman-witnesses-tacitus-annals-15-44` | 0 |
| roman-witnesses | `verified-roman-witnesses-suetonius-claudius-25-4` | 0 |
| roman-witnesses | `verified-roman-witnesses-suetonius-nero-16-2` | 0 |
| bhagavad-gita | `verified-bhagavad-gita-01` | 0 |
| bhagavad-gita | `verified-bhagavad-gita-10` | 5 |
| bhagavad-gita | `verified-bhagavad-gita-12` | 6 |
| upanishads | `verified-upanishads-isa` | 0 |
| upanishads | `verified-upanishads-prasna-5` | 1 |
| upanishads | `verified-upanishads-katha-6` | 0 |
| daodejing | `verified-daodejing-01` | 0 |
| daodejing | `verified-daodejing-41` | 1 |
| daodejing | `verified-daodejing-63` | 0 |
| verified-venetus | `verified-venetus-iliad-1` | 0 |
| verified-venetus | `verified-venetus-iliad-13` | 16 |
| verified-venetus | `verified-venetus-iliad-21` | 24 |
| rigveda | `verified-rigveda-1-1` | 0 |
| rigveda | `verified-rigveda-6-74` | 0 |
| rigveda | `verified-rigveda-7-88` | 0 |
| rigveda | `verified-rigveda-7-87` | 0 |
| rigveda | `verified-rigveda-10-54` | 1 |
| rigveda | `verified-rigveda-7-97` | 0 |
| odyssey | `verified-odyssey-book-1` | 0 |
| odyssey | `verified-odyssey-book-13` | 9 |
| odyssey | `verified-odyssey-book-3` | 0 |
| odyssey | `verified-odyssey-book-21` | 17 |
| odyssey | `verified-odyssey-book-22` | 14 |
| odyssey | `verified-odyssey-book-22` | 10 |
| odyssey (extra) | `verified-odyssey-book-13` | fol. 134r |
| odyssey (extra) | `verified-odyssey-book-24` | fol. 231v |
| plato-critias (extra) | `verified-plato-critias-110` | 110a/110b |
