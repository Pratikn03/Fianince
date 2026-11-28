# Paper 1 revision of 28 November 2026: plan and status

Written by an AI system (Claude Opus 5.5) for the authors, at the first author's request ("fix all gaps and things all 3
referees mention; I want the full revision"). Inputs: three AI referee reports and an AI editor's decision letter
(review packet in the session scratchpad; summarized in `REVISION_1128_RESPONSE.md`). These are AI reviews, not independent
human review.

Implementation: `ceiling_suite/papers/paper1_jedc_short/revision_1128.py`, hooked after `final_cut_1127` in
`make_short.py` (main) and `build_short.py` (supplement). Every replacement asserts a single match.

Status codes: DONE, PARTIAL (what is missing is stated), NOT DONE (reason stated), USER (needs an action only the
authors can take).

## Editor's required items

| # | Item | Approach | Status |
|---|---|---|---|
| 1 | Policy results in the Section 4 equilibrium | New Theorem (uniform cut in equilibrium): exact post-cut budget S*_θ = 1 − (1 − ā/D_θ)S_M(1)/S_M(D_θ); direction by branch; O((Δη)^{2K−1}) post-cut gap for prices-indistinguishable pairs; plug-in estimator from one passive record with D̂ = 1 + ā − φ̂_0, rate (log T)T^{−γ/2}, spacing-free, not parametric; principal-branch selection; pilot repaired with the dealer-root correction; prudential object remark. Checks: `p1_theory/equilibrium_uniform_cut_check.py` || DONE |
| 2 | Separation within one experiment | Theorem 7.1 restated: passive record (5.2(i), 5.1(i)/passive KL bound, 5.2(ii)); reset contract (new summed-impulse-response rate for S; 7.2(ii)-(iii); tags 7.6). Corollary 5.4 restated inside the tap model; steering probe made self-contained || DONE |
| 3 | Novelty paragraph | Position against long AR (Berk), single-trajectory identification (Oymak–Ozay; Simchowitz et al.; Sarkar et al.), disaggregation (Leipus et al.; Celov et al.), near-unit-root asymptotics; 7.3 as corollary || DONE |
| 4 | Inaccurate statements | Intro example (Δ²/Δ⁻⁴; Δ³/Δ⁻⁶ for two two-group economies); "the opposite holds"; best response not equilibrium, upper bound, two-sided GLRT rate; abstract probes; "pricing-error record"; known (a, κ) and observed x; m-dependence; "Exact modulus cost"; horizon in 3.1; Table 2 note (share 0.30–0.33, KL direction) || DONE |
| 5 | Self-contained and focused | Prove or relabel S6.1, S10.2 etc.; remove material not used by the main text; duplicates; residue; label collisions; cross-reference errors; dependence on 2026a–d made explicit or removed; shrink the supplement || PARTIAL (supplement not shrunk; authors to decide cuts) |
| 6 | Holdout reporting | Committed reading-B text restored verbatim (main and supplement); "placebo" removed; registration appendix (timestamps, commits, amendments, download times from the run manifest, access control); every registered outcome tabulated from the run's full output (`results/p1t_holdout_results_full_A4.json`); post hoc rows labelled, COVID confound stated; all pre-specified tests listed; p-value method || DONE |
| 7 | Taiwan headline claims | Removed from abstract and introduction; Section 7.5 as illustration: mechanical persistence, ŵ_c and u_c across specifications (from Table S5), class-specific-impact arithmetic, absolute information and implied power, harmonized conversions, contributions not memories, negative-memory range, like-for-like and stock-level ranges, local-search wording. New data runs (equal-impact test, information gap under alternative specifications) not done || PARTIAL (no new data runs) |
| 8 | Machine-checking claims | Title page and declaration aligned with S20; Table S2 rows corrected; claims register (Lean from Mathlib / Lean conditional / paper only); verbatim statements in the archive at a fixed commit || PARTIAL (verbatim statements in archive only) |
| 9 | Reproducibility | Data appendix from the spec and executor; archive at a fixed commit. DOI: USER (Zenodo release) || PARTIAL; DOI is USER |
| 10 | Declarations | Elsevier-style AI declaration with model names (Claude Opus 5.5 and Claude Fable 5.2 from commit history; ChatGPT/Codex and Gemini versions not recorded); Methods paragraph; CRediT; related manuscripts with status (author: none under review); data statement extended || DONE |
| 11 | Economic framing | Instruments defined; persistence from carry share; dealers' information; Theorem 7.9 assumptions in statement; Lemma 7.7 renamed; mixed signs and the ceiling; executable labels; Tick Size Pilot softened || DONE |
| 12 | Minor corrections | A m5, m7; B m3, m4, m10; C 11–19 || DONE except block-60 Table 3 |

## Log

- 28 Nov: holdout results zip retrieved from the author's Drive (approved) and stored; nothing recomputed.
- 28 Nov: equilibrium uniform-cut checks run (`equilibrium_uniform_cut_check_results.json`).
- 28 Nov: revision built (main 35 pp, supplement 96 pp), audit 63/63; response in `REVISION_1128_RESPONSE.md`.
