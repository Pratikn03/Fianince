# Paper 1, core version (8 November 2026)

A shortened version of Paper 1, built around one result: the feedback kernel is a sufficient statistic for every
outcome that price-based trading determines, and it is all that prices identify. The full working paper
(`../paper1/paper1_ssrn.tex`) is unchanged.

- **Build.** `python3 build_core.py && pdflatex paper1_core.tex` (three times).
- **How it is made.** `build_core.py` copies theorem statements and proofs by line range from
  `../paper1/paper1_ssrn.tex`. Each block's first line is checked, so a change to the source stops the build. New text
  lives in `src/`. Cross-references to material that is left out are rewritten from `src/fixes.txt`, and each rewrite
  must match.
- **New in this version.**
  - Framing: introduction, Section 3 header, Proposition `prop:anylinear` (any linear population; proved on paper
    only), the analogy paragraph, the scope section and the conclusion.
  - Literature check on the aggregation framing, with new references: Granger (1980), Zaffaroni (2004), Celov, Leipus
    and Philippe (2008), and Auclert, Rognlie and Straub (2024).
- **New, later the same day.** Section 7, "Beyond the kernel: saturating traders and stress".
  - Theorem 7.1: sufficiency of the capacity-weighted measure ν.
  - Theorem 7.2: no information without stress.
  - Proposition 7.3: smooth saturation, where information grows like A⁶.
  - Machine-checked: 7.1, and the pathwise part (i) of 7.2, in `Paper1SaturatingSufficiency.lean`. The rest is proved
    on paper.
- **Not in this version.** Account-level capital, general memory, spectral blindness, robustness to nonlinear rules
  and every empirical test. They are in the full working paper.

## Literature finding (8 November 2026)

- **Already known.**
  - Aggregate series reveal only the distribution of individual autoregressive coefficients (Granger 1980; the
    disaggregation literature).
  - Sufficient statistics for aggregate dynamics under heterogeneity exist in macroeconomics (intertemporal MPCs,
    Auclert et al. 2024).
  - The (Δη)^-(4K-2) rate is the known mixture rate (Heinrich and Kahn 2018; Wu and Yang 2020).
- **What the paper claims as new.**
  - Sufficiency inside a strategic market, holding pathwise for any insider and any causal dealer rule.
  - Memories enter as transmission zeros of the closed loop, so passive observation is no cheaper than probing.
  - Both results hold in equilibrium.
  - The supervisory split (market-wide versus targeted actions), with a price for disclosure.
