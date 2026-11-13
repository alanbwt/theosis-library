# QC fixes: Bible and early Christian collections (2026-11-12)

Input: `docs/qc/review-bible-christian.md`. Re-runnable scripts: `scripts/qc3_page_joins.py`, `scripts/qc3_fix_entries.py`, `scripts/qc3_absent_verses.py`. Template renders `english_ref`. No git, build or deploy.

## Defects

- Barnabas 21: web-page text removed; English ends with Lightfoot's "be with your spirit."
- Sinaiticus 2 Cor 13: 13:14 is on 278v (checked); Greek 13 = KJV 14, Numbering note. 240 OT intros: nomina sacra sentence corrected.
- Vaticanus: 2 Cor 13 re-paired; Mark 16:9-20 flagged, blank column described (p. 1303 checked); Heb 9:14 English cut at καθα, end of codex stated.
- Page joins: 153 fixed (Vaticanus 101, Bezae 27, W John 22, Alexandrinus 3): 122 fused words split, 31 split words joined.
- Alexandrinus Rev 12, 2 Cor 13, 3 John: one Numbering paragraph each. Bezae: lacunae and coverage in 45 intros.
- W (images checked): Luke 3:23b-38 flagged; 4:1 and 23:1 added; p0211 linked to 4:2; Freer Logion marked. No complete PD English found (Goodspeed 1908 first sentence quoted).
- Leningrad Josh 21:36-37 flagged (fol. 133v, UXLC note X; no other X verses). 57 english_ref intros reworded.
- 1QIsa-a 2:9b-10 flagged (checked). 1 Clement 52-53 verse numbers. `docs/collections/josephus.md` written; unsourced claims removed.

## Doubts fixed

Partial verses marked: Sinaiticus John 5:3b, Matt 16:2b; Vaticanus Matt 16:2b; Alexandrinus Matt 25:6, John 6:50, 2 Cor 4:13; Bezae Matt 1:20 (fol. 3v checked), 6:20, 9:2, 27:12, John 1:16, 3:26. Line-filler note (103), psalm superscriptions (21), Magdala (4), Clement numbering, Quran 70r/2v breaks (checked), 252 W scan_notes, ¯ note (20), 1 John 5 Comma, image provenance, 1QIsa-a line 0.

## Absent verses (`qc3_absent_verses.py`)

781 entries, 3,433 sections checked: 36 verses flagged in 34 Sinaiticus sections (19 KJV-only; 17 left out by the first scribe, supplied by a corrector); 34 notes updated. 60 Tischendorf-text entries not testable.

## Checks

`validate_strict.py`: all 3,821 pass. `audit_sections.py`: all pass, 0 warnings (was 20).

## Not fixed

`data/texts.json` rows (integrator); images (out of scope); Edda label (`render_verified.py`); 9 further Quran page-break word counts unchecked; Leningrad/1QIsa-a scan_notes (rule 4); Vaticanus John 7:53 needs nothing (bolls TISCH itself is unaccented).
