# Paper 1: the twelve improvements of 11 November, status on 12 November 2026

Done by an AI system at the author's request. Not independent review.

| # | Item | Status | Where |
|---|---|---|---|
| 1 | Declarations | Done in both versions: contributions (CRediT), funding, competing interests, data, code, ethics. The draft "proposed review responsibilities" paragraph is gone. **Authors to confirm** the competing-interests line and "all authors approved the final manuscript". | `paper1_core/src/declarations.tex` |
| 2 | Abstract length | Note: exactly 100 words (the RFS limit). Core: 136 words. The fixed Taiwan sentence is unchanged. | `note_main.tex`, `src/front.tex` |
| 3 | Lean whole-project receipt | **Not possible here.** The Mathlib cache hosts are blocked from this sandbox (HTTP 000), and a build without the cache recompiles Mathlib. Run `python3 verify_formalization.py` on the author's Mac and commit the new receipt. | `research_extension/current_manuscript_lean_20261008` |
| 4 | Repository name | **Author's decision.** GitHub now reports the repository as `Pratikn03/Fianince`; the papers' links already use that and work. Renaming (for example to `finance`) is one click in the repository settings; old links redirect. The papers' URLs must then be updated. | |
| 5 | Title-page numbering | Done: front-matter pages carry no number in either version. | `src/front.tex`, `build_note.py` |
| 6 | Figure | Done: Figure "The passive barrier near instability" in both versions. Fitted slopes 5.86 (K = 2) and 9.95 (K = 3) against the theoretical 6 and 10. | `research_extension/fragility_reveals/make_barrier_figure.py` |
| 7 | Leaner supplement | Partly: expository paragraphs dropped, 58 to 55 pages. A larger cut (dropping S1-S7) would remove the full statements that the proofs refer to. | `build_note.py` |
| 8 | Core notation | Done: news is `\varepsilon_t` in both versions; `w_i` is only the weight. | `src/fixes.txt`, `src/sat.tex`, `src/supp_sat.tex` |
| 9 | References | All 33 checked. Three updated to their published versions: Celov, Leipus and Philippe (J. Nonparametric Statistics 22, 2010), Dreesen et al. (LVA/ICA 2017, LNCS 10169, 16-25), Vlacic and Bolcskei (Constructive Approximation 55, 2022). Leclere and Rosenbaum (arXiv 2609.03115) and Katz, Diab and Batenkov (arXiv 2302.05883) exist as preprints. | `src/fixes.txt` |
| 10 | Journal and cover letter | Review of Financial Studies first, Journal of Financial Markets second; Quantitative Economics ruled out by its 25-page supplement and self-contained-proofs rules. Double-spaced submission build (main 17 pages). Cover letter drafted. | `paper1_note/SUBMISSION_RFS.md` |
| 11 | Korea test redesign | Design 2 built and simulated: memories now recovered to within 0.024, but the sufficiency test still has little power, and composition features "predict" in markets with no feedback. **Not registerable.** Recorded in the draft spec, section 9. | `p1k_executor_v2.py`, `validate_p1k_v2.py` |
| 12 | Binance replication | Development notebook built (`CFG_REPLICATION`), hashed and logged; not run. Running it before 16 November fixes the replication's universe before any of its evaluation data exist. Evaluation only after 14 February 2027. | `P7S_A1_Replication_Development_Colab.ipynb` |
