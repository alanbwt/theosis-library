# Final QC queue (items to fix before release)

- clement: Greek (Lake 1912) not proofread against print; expect ~1 error per page. Proofread all 86 sections.
- didache: Greek accents not checked mark by mark.
- qumran-1qphab: Brownlee 1948 English hand-transcribed; line numbers 1-2 off from the Hebrew in columns I-II.
- akhmim-codex: Lods Greek hand-transcribed from print; spot-proofread.
- authors.json: tacitus and suetonius carry placeholder bios.
- gilgamesh: old 19 entries deleted in commit 4b0586df pending the eBL rebuild; restore from bb3d99ad if the rebuild fails.
- venetus: Iliad Book 1 English is still Butler (1898); transcribe A. T. Murray 1924 Book 1 from the archive.org Loeb scan (Perseus Book 1 is a later revision).
- sinaiticus: Shepherd of Hermas 28-31 have Greek in the CSP XML but no entries; add them.
- odyssey: Book 24.104-548 missing (Laur. Plut. 32.24 ends at 24.103); add from a second manuscript (e.g. Marc. gr. 613, BL Harley 5674, Vat. gr. 915).
- quran: 9 more folio page breaks with unassigned words to check on the images (see docs/qc/fixes-bible-christian.md).
- edda: Old Norse is Gudni Jonsson's normalized text; upgrade to the Wimmer & Jonsson 1891 diplomatic text of Codex Regius (PD) so the original matches the manuscript.
- NOTE: re-running scripts/qc_swap_ntvmr_transcriptions.py --force undoes the qc3 fixes; re-run scripts/qc3_*.py after it.
