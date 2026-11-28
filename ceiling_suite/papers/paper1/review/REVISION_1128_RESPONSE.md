# Paper 1: response to the AI referee reports and editor's letter (revision of 28 November 2026)

Written by an AI system (Claude Opus 5.5) for the authors. The three referee reports and the editor's decision letter
were written by AI agents that read only the submitted PDFs; they are not independent human review. Decision: major
revision (all three referees and the editor: pass). The authors have not yet checked this revision; the AI declaration
says so until `AUTHORS_CHECKED_1128` is set to True in `ceiling_suite/papers/paper1_jedc_short/revision_1128.py`.

Build: main text 35 pages (was 29), supplement 96 pages (was 89); no undefined references or overfull boxes; audit
63/63 (checks 58–63 are new and guard this revision's fixes). Implementation: `revision_1128.py` (main text) and
`revision_1128_supp.py` (supplement), applied after `final_cut_1127`.

## Numbering after the revision (Section 7)

7.1 separation; 7.2 market-wide versus targeted (proposition); **7.3 uniform cut in equilibrium (new)**; 7.4 pilot;
7.5 decision loss (corollary); 7.6 minimax; 7.7 tags; 7.8 payoff foundations (lemma); 7.9 relabeling (proposition);
7.10 surveillance paradox; 7.11 value of records. Supplement: new Sections "The uniform cut and the pilot in
equilibrium" and "The registered Taiwan test", Tables "Every registered outcome", "Every pre-specified test" and
"Claims register".

## Editor's required items

| # | Item | What was done | Status |
|---|---|---|---|
| 1 | Policy results in the dealer equilibrium (decisive) | New Theorem 7.3. (i) Exact post-cut budget S*_θ = 1 − (1 − ā/D_θ)S_M(1)/S_M(D_θ): the cut acts only through the dealer root. (ii) On the principal equilibrium (largest root, ∂F/∂D > 0) a cut lowers the budget; on a root with ∂F/∂D < 0 it raises it. (iii) Populations prices cannot tell apart end within C(Δη)^{2K−1} after the cut. (iv) One passive record estimates the post-cut budget at rate (log T)T^{−γ/2}, free of the spacing but not parametric; the identity φ₀ = 1 + ā − D reads the dealer root off the first autoregressive coefficient. Theorem 7.4(iv): the pilot record gives the post-restriction budget directly; the removed groups' moments need a correction fixed by the two dealer roots. "Which ceiling" remark (distance to the fold). Selection: principal equilibrium = largest root; Figure S2 relabelled by the sign of ∂F/∂D. "Safe default" withdrawn; conclusion conditions on the principal branch. Proofs: Appendix A ((i)–(ii)) and Supplement ((iii)–(iv), pilot rate). Checks: `p1_theory/equilibrium_uniform_cut_check.py` (formula and identity to 1e-16; sign reversal 0.755 → 0.913 on the lower root, 0.650 → 0.487 on the principal root against 0.557 fixed-impact; 16% example; gap slopes 2.94 and 4.98; estimator error slope ≈ −0.33 in log T at every spacing; barrier on the principal root, impulse-response gaps ≈ 7d³) | DONE (no Lean for the new theorem; listed as paper-only) |
| 2 | Separation within one experiment | Theorem 7.1 restated: (i)–(ii) within one passive pricing-error record (Theorem 5.2(i); passive finite-record KL bound for the Proposition 7.2 pairs; Theorem 5.2(ii)); (iii)–(iv) within reset records, with a new self-contained rate for S from the summed impulse response (Appendix A). Corollary 5.4 restated inside the tap experiment. Steering probe made self-contained and stated to observe aggregate flow | DONE |
| 3 | Novelty | Paragraph rewritten: long autoregression (Berk), single-trajectory identification (Simchowitz et al. 2018; Oymak–Ozay 2019; Sarkar et al. 2021), disaggregation (Leipus et al. 2006; Celov et al. 2010), near-unit-root asymptotics (Chan–Wei 1988; Sims–Stock–Watson 1990); pilot as a corollary. References verified online | DONE |
| 4 | Inaccurate statements | Opening example (Δ²/Δ⁻⁴; Δ³/Δ⁻⁶ only for two two-group economies); "the opposite holds" → bounded gain (Table 2 factors 1.35–2.3); best response not equilibrium, upper bound, two-sided bound N^{−1/6} (Theorem 7.11, proof added); abstract no longer says "even near instability or under active probes"; "pricing-error record"; m^{−4} constant; "Modulus cost"; horizon in Theorem 3.1; Table 2 note (share 0.30–0.33, KL direction, ln 5/D) | DONE. B's "kδ0 typo" is a text-extraction artifact (the PDF reads kδ0²) |
| 5 | Self-contained and focused | Batch-auction theorem → conjecture (no proof); bispectrum claim labelled unproved; margin-buffer and volatility-interruption subsections marked as discussion; duplicate proofs removed; map of proof locations fixed; label collisions with 2026d fixed; 2026b and 2026c citations made non-load-bearing | PARTIAL: the supplement did not shrink (96 pp). Halving it requires removing results the main text uses — an authors' decision (proposal below). One stability step still cites 2026d (S-35) |
| 6 | Holdout reporting | Committed reading-B text restored verbatim (main and supplement); "placebo" removed; new supplement section with registration time, commits, all four amendments, R1, download times from the run manifest, access control and data construction; every registered outcome tabulated from the run's full output (retrieved from the author's Drive with approval; nothing recomputed); post hoc rows labelled, masked check reported, COVID confound stated; table of every pre-specified test (E1–E26, P1F, H1–H2, P1KS); p-value method | DONE |
| 7 | Taiwan headline claims | Removed from abstract and introduction; Section 7.5 states mechanical persistence, sign flip under differencing, class-specific-impact contributions (0.0013 / 0.0013), absolute information (0.22 nats, power − size ≤ 0.33), harmonized conversions (Pinsker, 245.5 days; Table 2 uses ln 5/D), tags identify contributions not memories, negative-memory range, like-for-like and stock-level ranges, local-search wording; trust response has no out-of-sample support | PARTIAL: no new data runs (equal-impact test with intervals; information gap under alternative specifications) |
| 8 | Machine-checking claims | Title page and declaration aligned with the supplement (deterministic steps and several finite-sample probability bounds); Table S2 rows corrected (minimax declarations exist as `p1_minimax_*`); claims register for every main-text result | PARTIAL: verbatim Lean statements at a fixed commit are in the archive files, not printed |
| 9 | Reproducibility | Data appendix (sources, access dates, construction, β̂ from development days only, eligibility, bootstrap, forecasting scheme) | PARTIAL: DOI needs a Zenodo release by the authors |
| 10 | Declarations | AI declaration with model names (Claude Opus 5.5 and Fable 5.2 from commit history; ChatGPT/Codex and Gemini versions not recorded); research-use paragraph in the supplement; CRediT software credit; related manuscripts with status (author: none under review); data statement extended to Binance and CFTC | DONE (authors may add the missing versions) |
| 11 | Economic framing | Instruments and information paragraph; persistence from the carry share and dealers' information; Theorem 7.10 assumptions in the statement (power through J, Pinsker envelope); Lemma 7.8 renamed; mixed signs and the ceiling; executable labels; Tick Size Pilot softened; CAT update (2025 PII exemption, linkage without identity) | DONE |
| 12 | Minor corrections | A m5 (proof slip), A m7, A m9; B m3, m4 (Twu–Wang 2018), m10; C 11 (map, S-84, collisions), 12 (duplicates), 13 (G → S_M, Δ → Λ₀), 14, 15, 16 (lag sum), 17, 18 (fit range), 19 (terminology, full ASA v. SEC citation) | DONE except Table 3 at block 60 (needs a data run) |

## For the authors

1. Read and check the revision; then set `AUTHORS_CHECKED_1128 = True` and rebuild.
2. Mint a DOI for the archive (Zenodo release of the repository) and add it to the data statement.
3. Add versions for ChatGPT/Codex and Gemini if known.
4. Decide the deeper cut the editor wants. A proposal that brings the main text back to about 30 pages: move
   Theorem 4.4 (fragility), Theorem 6.1 (forecast mismatch), Corollary 7.5, Lemma 7.8, Figure 2 and the
   instruments paragraph to the supplement; and drop from the supplement the sections no main-text result uses
   (noise injection, latency and batch auctions, margin buffers, rational inattention, pre-averaging).
5. Optional data runs (Colab, development data 2013–2016, no registration issue): equal-impact test with intervals,
   class-specific-impact Table 3, information gap and ranges under the first-differenced and limit-excluded
   specifications, Table 3 at block length 60.
