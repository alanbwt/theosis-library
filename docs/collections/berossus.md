# berossus

**Entries:** 6 entries, 45 sections (`verified-berossus-*`), shelf Mesopotamia.

## Contents
| order | entry | text | witness, pages | sections |
|---|---|---|---|---|
| 1 | `oannes` | Polyhistor's summary of Babyloniaka book 1: Berossus, Babylonia, Oannes, the creation (Müller fr. 1) | Paris gr. 1711 pp. 18-19 | 6 (Müller §§1-6) |
| 2 | `flood` | Book 2: the ten kings (120 sars) and the flood of Xisouthros (Müller fr. 4 second part + fr. 7) | Paris gr. 1711 pp. 19-20 | 7 |
| 3 | `tower` | The tower of Babel: Polyhistor quoting the Sibyl (Müller fr. 10) and Abydenus fr. 5 | Paris gr. 1711 p. 29 | 2 |
| 4 | `apollodorus` | Apollodorus' list of the ten kings and the Annedotoi (Müller fr. 6) | Paris gr. 1711 pp. 25-26 | 2 (one per page) |
| 5 | `abydenus` | Abydenus' kings and flood (Müller, Abydenus fr. 1) | Paris gr. 1711 p. 25 | 2 |
| 6 | `josephus-apion` | Josephus, Against Apion 1.128-153 (book 3: Nabopolassar to Nabonidus) | Laur. Plut. 69.22 fols. 10r-11v | 26 (Niese sections) |

## Sources
- Scans: Paris, BnF, grec 1711 (11th c., Syncellus, Ecloga chronographica, paginated), Gallica
  ark:/12148/btv1b10723005g, microfilm openings split into single pages (page p = image f(14 + p//2),
  even pages on the left). Terms: Gallica non-commercial reuse with credit.
  Florence, BML, Plut. 69.22 (10th c. per BML, 11th per Niese; Contra Apionem book 1), Teca Digitale
  IIIF, record plutei 1350351, access "Pubblico" (spec rule 9).
- Greek (Syncellus fragments): C. Müller, FHG II pp. 496-502 and IV p. 280, via the DFHG API
  (CC BY-NC-SA 4.0), proofread line by line against Müller's printed pages on archive.org. The DFHG
  OCR had 30+ errors, including one dropped line in fr. 7 §2 ("καὶ πόματα, ἐμβαλεῖν δὲ καὶ ζῶα πτηνὰ
  καὶ τετράποδα"); each correction is listed and asserted in `scripts/import_berossus.py`. Müller's
  parenthesized apparatus notes are removed; his square brackets are kept.
- Greek (Josephus): Niese 1889 via Perseus tlg0526.tlg003.perseus-grc2 (CC BY-SA 4.0).
- English (Syncellus fragments): I. P. Cory, Ancient Fragments, 2nd ed. 1832 (PD). Text from the
  sacred-texts.com transcription (Wayback captures, since the live site blocks automated access),
  diffed word by word against the archive.org OCR of the 1832 printing; the two real disagreements
  were settled on the page images ("gongæ" not "gongre"; "reduced the universe"). Footnote markers
  and Cory's source citations removed.
- English (Josephus): Whiston 1737 via Project Gutenberg #2849 (PD); three transcription faults
  ("oilier", a stray footnote fragment in 1.142, "mouths") corrected against the 1860 printing.

## Mapping
All by eye on the downloaded images; no published folio list was used. For every page the first and
last lines were read and located in the edition, and section openings were found by their opening
words and counted line numbers (recorded in each `scan_note`). Paris gr. 1711: p. 18 l. 11 heading
"Ἐκ τῶν Ἀλεξάνδρου τοῦ Πολυΐστορος"; l. 26 Oannes (margin "ὠάννης"); p. 19 begins "καὶ εἰδιφυεῖς";
flood quotation from p. 19 l. 28 to p. 20 l. 19; p. 25 l. 9 heading "Ἐκ τῶν Ἀβυδηνοῦ", Abydenus to l. 29,
Apollodorus from l. 33 to p. 26 l. 8; p. 29 l. 11 heading of Polyhistor on the tower, Sibyl quotation ll. 12-15, Abydenus ll. 18-23. Laur. Plut. 69.22: 1.128 at fol. 10r l. 6; page breaks inside
1.135 ("Συ|ρίαν") and 1.141 ("ἀνοικοδομήσας | καὶ τὴν ὄψιν"), 11r ends with 1.148, 1.153 ends on 11v l. 20.
Sections that cross a page break list both pages.

## Gaps
- Fragments preserved only in the Armenian Eusebius (Müller fr. 5, 9, 11, 12; Abydenus fr. 2-4, 6-8)
  have no Greek: not published.
- Syncellus' own remarks on Berossus (Müller fr. 1 appendix, fr. 4 first part, fr. 11a) and the short
  testimonia (Athenaeus, Agathias, Josephus Ant. 1.93, 1.158, 10.20, Clement, Theophilus, Vitruvius,
  Pliny, Seneca) are not included: Cory 1832 does not translate most of them, and no other PD English
  was located.
- Paris gr. 1764 (a second Syncellus witness, Gallica btv1b10722002s) was not used.
- Josephus, Antiquities 1.93 (Berossus on the remains of the ark) and 1.158 (on Abraham) are not
  included. In Vat. gr. 984 (fol. 3v-4r, checked on the image) the text of 1.93-95 is abridged: the
  amulet clause of 1.93 and Nicolaus' quotation in 1.95 are missing, so Niese's text and Whiston's
  English would not match the page. Another manuscript of the Antiquities would be needed.

## Open questions
- Line counts on the microfilm pages were made by eye; the opening words in each `scan_note` are
  the primary locator.
- In the tower entry Cory's English goes beyond the Greek on the page in two places (the Armenian
  Eusebius for Polyhistor's last clause, Praeparatio 9.14 for Abydenus' last sentence); both are
  stated in the section notes.
- Cory sometimes translates readings of the Armenian Eusebius or older editors (e.g. "fertile" for
  Goar's εὔφορα where Müller prints ἄφορα); these are noted in the entries.
- The manuscript reads Κορκυραίων (p. 20 l. 15) where Müller prints Κορδυαίων; the Greek shown is the
  edition, not a transcription of the page.
