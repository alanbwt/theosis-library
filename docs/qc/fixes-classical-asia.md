# Fixes: classical and Asian collections (2026-11-12)

Input: docs/qc/review-classical-asia.md. data/texts.json not touched (integrator re-syncs).

1. **Hesiod page maps.** All 38 pages of Laur. Plut. 32.16 re-read on the images; first and last rows recorded (`read_first`/`read_last` in PAGES, quoted in every scan_note). Corrected: Theogony 246v 868-933, 247r 934-991; Shield 248v 65-130, 249r 131-194. Other 36 edges confirmed. Page notes added: marginal 663, 723-724 (plus an extra verse); W&D 93 and 370-372 at page feet, 169 absent, 758 twice; Shield 378 in margin, struck repeat of 253.
2. **English vs original.** Cut at sentence ends, at most one sentence crossing, exact English range in scan_note: Hesiod at all 29 page breaks (`scripts/qc4_hesiod_english.py`) plus W&D 502-503 moved to ploughing; Odyssey 8 breaks (3.9, 13.207, 13.232, 13.439, 21.424, 22.338, 22.361, 24.2); Iliad 13 fol. 172r (English 404-426; 13.422 now "alone at the foot"); Aeneid 6 (728-734 whole in 724-732, line 966 split); Critias 110a/b; Timaeus 17a/b, 18a/b.
3. **Timaeus/Critias labels.** Repeated labels hidden; Greek and English label counts now match in all 440 sections. Continued quotations no longer reopened; inner quotes single.
4. **Metadata.** Monro (24 Venetus entries, script, doc); Perseus ids (14 W&D/Shield entries); Besant "her" (18 entries, doc); Petelia intro; 32 lost spaces restored plus one Perseus typo; Aelian 113r lines 30/37, Rigveda 1.1 line 7, Gita 1.1 line 6 (each rechecked on the image); Rigveda 7.87 quotes the leaf.
5. **Doubts.** Tacitus Annals dated 1876 (Spectator review, 11 March 1876; 1869 is their History); Hymns intro says M ends at 18.4 and 19-33 are absent; Herodotus "some seventy years"; plato-dialogues and plato-republic docs corrected.

**Checks.** check_collection: 0 hard failures for all 16 keys. qc2_venetus check: 0 problems. validate_strict: 3821/3821 pass. audit_sections: all pass.

**Not fixed.**
- Elsewhere, the English still follows the translator's five-line marks: Odyssey (397/481 sections), Venetus (537/638), Homeric Hymns.
- Bury milestone offsets remain elsewhere (e.g. Timaeus 36a/b, 50b/c).
- "Munro" remains in render_verified.py and collections_lib.py, which are not mine to edit.
- venetus_visual_checks.json is overridden in the script, not edited.
- The Upanishads 404 is a build issue.
