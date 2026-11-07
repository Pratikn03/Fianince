# Independent-review checklist (none completed)

An automated agent cannot complete any of these. Each needs a named human reviewer.

- [ ] Probability/statistics. Is the averaged Gaussian record the right experiment for S7.1, or must the paper state
  the raw-record reduction? Is "unbiased on a neighbourhood" the paper's estimator class?
- [ ] Model correspondence.
  - Do `tfTop`/`tfBottom` equal the z-transform of recursion (1)–(6) with the paper's z convention?
  - Is "all zeros of tfBottom in the open disk" the paper's stability notion?
- [ ] S3.2. The block coefficients `b₁`, `b₂` enter through `passive_three_step_price_expansion`, which is algebra on
  given definitions. Check that they match the reset recursion.
- [ ] Thm 5.5. The finite-record results are from rest, and part (iii) uses a binomial pair. Decide whether the paper
  should restate (iii), or whether Gauss/Gauss–Radau must be formalized.
- [ ] Prop 6.1. Confirm that the reported Lean coverage is limited to the determinant bound.
- [ ] Statement audit. For every row of `coverage.tsv`, read the Lean statement against the manuscript sentence.
