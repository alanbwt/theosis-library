# Edicts of Ashoka (`ashoka-edicts`)

The inscriptions of the Maurya king Ashoka (Devanampriya Priyadarsin, r. c. 268-232 BCE), one entry per inscribed rock
or pillar: `verified-ashoka-edicts-<site>`. Inside each entry, one section per edict (or per face where an edict runs over
two faces). Every section shows Hultzsch's transliteration of exactly the lines of that edict at that site, Hultzsch's
English for that site's version, and the image of the inked impression (estampage) that carries those lines; the
Rummindei (Lumbini) section also shows a photograph of the stone.

## Contents

| Order | Entry | Sections | Lines |
|---|---|---|---|
| 1 | Girnar: Major Rock Edicts I-XIV | 14 (I ... XIV) | complete as preserved; V ends broken, XIII fragmentary (much of the rock blasted in the 19th c.) |
| 2 | Kalsi: Major Rock Edicts I-XIV + elephant label | 16 (I-XII, XIII east face, XIII south face, XIV, elephant) | complete; XIII is the fullest Brahmi text of the Kalinga edict |
| 3 | Dhauli: the two Separate Edicts (to the officers of Tosali) | 2 (Sep-I, Sep-II) | complete as preserved (weathered rock, many bracketed letters) |
| 4 | Delhi-Topra pillar: Pillar Edicts I-VII | 8 (I-VI, VII east face, VII round the pillar) | complete; VII only exists here |
| 5 | Rummindei (Lumbini) pillar | 1 | complete (5 lines) |
| 6 | Nigali Sagar pillar | 1 | 4 lines, beginnings of lines 3-4 lost |
| 7 | Calcutta-Bairat (Bhabru) inscription | 1 | complete (8 lines) |

Total: 7 entries, 43 sections.

## Sources

| Layer | Source | License |
|---|---|---|
| Transliteration | E. Hultzsch, Inscriptions of Asoka, new ed. (Corpus Inscriptionum Indicarum I, Oxford 1925), archive.org `InscriptionsOfAsoka.NewEditionByE.Hultzsch` (300 ppi scan, digitized by Artur Karp) | public domain (1925; Hultzsch d. 1927); archive.org item Public Domain Mark |
| English | Hultzsch's translation in the same volume | public domain |
| Images | Hultzsch's collotype plates of inked impressions (estampages) made for the Archaeological Survey of India, leaves of the same scan fetched at full resolution (BookReader image service) | public domain |
| Photograph (Rummindei only) | Wikimedia Commons, "Lumbini inscription (complete)", Photo Dharma (Anandajoti Bhikkhu) and Charlie Phillips | CC BY 2.0 |

The plates are photographs of impressions pressed on the stone, not drawings; every scan_note says so. Commons has
photographs of the Girnar and Kalsi rocks and of Hultzsch's plates, but no stone photograph on which the edicts of these
sites could be located line by line, so the impressions are used. For Lumbini the stone photograph is clear and was read.

## Transcription method

The archive.org OCR (`HultzschCorpusAsokaSearchable_djvu.txt`) drops most diacritics and garbles brackets. Every line of
transliteration and English was read on the printed page image (bands of each page at about 225 ppi; doubtful letters
at 300 ppi) and typed with Hultzsch's diacritics (ā ī ū ṁ ṭ ḍ ṇ ñ ś ṣ ḷ). The result was then aligned word by word with the
OCR (scratch tool, normalising diacritics) to catch skipped words or lines; every disagreement that was not OCR noise was
looked up on the image again. Transcriptions: `data/sources/ashoka-edicts/proofread/<site>.txt`, one block per edict with
Hultzsch's pages and the archive.org leaf numbers. Kept as printed: square brackets (damaged or uncertain letters), dots for
lost letters, section letters (A), (B) ..., Kalsi's punctuation strokes (|), Hultzsch's spellings. Left out: footnote
numbers and footnotes (other scholars' readings, "read ..." corrections), and Hultzsch's Devanagari transcript.

The scan used for the Delhi-Topra pages has a former reader's pencil notes over some lacunae of Pillar Edict VII; they are
not part of the print and were ignored.

## Mapping method

Edict to lines: Hultzsch's line numbers. Lines to image: the edict numerals and line numbers printed in the margins of each
plate. Each crop was checked by eye: the band was located by its numeral, and its lines counted against the transcription
(recorded per section in scan_note). Lumbini photograph: the five lines were counted and their first and last signs read
in Brahmi against the transcription.

## Gaps and open questions

- Not yet built: the Shahbazgarhi and Mansehra versions (Kharoshthi), Dhauli's Major Rock Edicts I-X and XIV, Jaugada
  (rock edicts and its two Separate Edicts),
  the Bombay-Sopara fragment, the other pillars (Delhi-Mirath, Lauriya-Araraj, Lauriya-Nandangarh, Rampurva,
  Allahabad-Kosam with the Queen's and Kausambi edicts), the Sanchi and Sarnath schism edicts, the Minor Rock Edicts
  (Rupnath, Sahasram, Bairat, Maski, Brahmagiri, Siddapura, Jatinga-Ramesvara) and the Barabar caves. All are in
  Hultzsch 1925 and can be added the same way.
- Not in Hultzsch (found later): the Kandahar Greek-Aramaic bilingual and other Afghan and Indian finds after 1925. No
  public-domain or openly licensed English was found for the Kandahar bilingual, so it is not published.
- Girnar: the short line below edict XIII ('the entirely white elephant') and two fragments under XIII are not on
  Hultzsch's plates and are not shown.
- Kalsi XIII south face: the impression begins at line 4; lines 1-3 (only "[ney]u (O) ichha" survives) are not on the plate,
  as the scan_note says.
- Kalsi Edict X-XIV: the writer uses s, sh and ś for one sound; Hultzsch prints them as written and so does this text.
- Hultzsch's English renders dhamma as "morality"; his translation is kept as printed.

## Check

`python3 scripts/check_collection.py ashoka-edicts` -> `ashoka-edicts: 7 entries, 43 sections, 0 hard failures, 0 warnings`
