# Paper 1 supervisory release — 5 November 2026

This development revision starts from main commit 5c93dab1ed2e690c65506fbece92aa315b255c47. It is a working draft, not an independently reviewed or SSRN-published release.

## Audit and manuscript changes

- `Paper1SupervisorySeparation.lean` imports `Paper1LowerBound` and `Paper1MatchedPair`. Its two-cohort theorem concerns actual Gaussian records and a different explicit pair from the numerical Gauss–Radau example. Source inspection is not a new Lean build.
- `p1_prop_target_every_K` assumes an index, positive intensity gap and dominance inequality. It does not construct those hypotheses. Symmetric binomial odd/even weights have equal maxima. The unconditional decision claim is restricted to two groups; general K requires a separate gap construction.
- The unsupported smooth-response assertion is removed. A constant smooth response map can erase separation. The replacement requires a declared absolute response allowance and checks the threshold margin explicitly.
- The prudential target is a row feedback budget, not the state matrix's spectral radius. Already stable economies can fail the tighter prudential ceiling.
- The action model includes horizon, surplus convention, implementation cost, information fee, per-world error probability, an optional acquisition decision and the same-action no-data benchmark. Surplus is assumed rather than empirically estimated.
- Literature positioning acknowledges clustered Prony/super-resolution rates (Batenkov et al.; Katz et al.) and control without full identification (van Waarde et al.). The candidate delta is model-specific; exhaustive novelty review remains open.

## Evidence reuse and new check

Run from repository root:

```sh
python studies/supervisory_release_20261105/run_study.py
```

Requires NumPy and SciPy. Six archived synthetic rows are independently recomputed from their declared state recursion, with maximum response discrepancy error below 2.1e-17. Existing archived rows contain no measured intervention utility, disclosure prices, or response allowances. GPU runs are not rerun or claimed to validate these absent quantities. Historical and real-noise experiments remain existing evidence with their original limitations; this release does not independently reproduce all of them.

The remaining gap is evaluated with exact Gaussian integrals in a scalar disclosure contract. It is not the tagged-flow theorem, an observed post-intervention market trial, or a preregistered experiment. `results/study.json` records assumptions, representative results and failures; `results/study.csv` retains all 2,304 deterministic sensitivity configurations, including adverse outcomes. No random seed selection or independent-market interpretation applies. Common per-record prices are assumptions, not cost estimates. Public data in this experiment are paid reset response records, not freely observed passive prices.

Representative conditional net disclosure value: 0.144087 surplus units after a 0.066 information bill. Positive configurations: 1,207; negative: 1,079; ties: 18. Bias and understated future response invalidate error guarantees. Under drift misspecification the fallback throttle can also fail, so such cases are safety failures rather than fair payoff comparisons.

## Formal verification status

`Robustness.lean` contains only scalar deterministic threshold lemmas. No Lean executable was available locally. The targeted GitHub workflow must pass before describing these new lemmas as machine checked. It also compiles `CurrentProofs/Paper1SupervisorySeparation.lean` with the existing dependency project. Historical declaration counts are not a proof-to-manuscript semantic audit.

## Required human proof review

Pratik, Prashant and Sujan should each independently record a verdict on: Gaussian record/horizon scope; the two-group weight-gap construction; hypothetical all-K hypotheses; observability and executability of the chosen class; the robustness allowance; and the acquisition/payoff assumptions. Resolve discrepancies in a written claim ledger before a preprint-ready verdict. No review verdict or SSRN submission is fabricated by this revision.

The supplementary empirical precision-to-years arithmetic is hypothetical and does not establish an equivalent sample requirement for different estimands. Negative empirical tests do not prove the necessity of granular reporting.
