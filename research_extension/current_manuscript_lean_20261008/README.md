# Current manuscript Lean proofs

The 5 November 2026 Paper 1 release adds 16 supervisory-witness and decision theorems and includes them in the main project import. `paper1_release_receipt.json` records the fresh full-project build, strict axiom audit, exact new theorem types and active Paper 1 source hashes. The audited project has 803 named declarations across the research programme; this is not a count or percentage of fully formalized Paper 1 statements. Only `propext`, `Classical.choice` and `Quot.sound` are permitted.

The new K=2 Gauss/Radau construction matches the numerical witness. The Gaussian event theorem covers a conservative scalar-measurement gate; it does not identify the scalar reading with observed class stocks or tagged order flow. The market response allowance and economic costs remain assumptions. The all-K supervisory extension remains conditional.

Run the release verifier from repository root:

```sh
python studies/supervisory_release_20261105/tools/verify_release.py --project research_extension/current_manuscript_lean_20261008 --repo .
```

See `studies/supervisory_release_20261105/RELEASE_REVIEW.md` and `CLAIM_SCOPE.json` for current scope. The historical coverage files and implementation notes below concern earlier stages; neither a name mapping nor a build replaces semantic review. Independent review, empirical market assumptions and novelty are not certified.

## Historical implementation notes

## What is checked

- Actual real-valued cash, inventory and marked-equity identities; two-account conservation; robust quadratic root; first-pulse margin inequality.
- Actual price-first cohort recursion through three observations; exact equity differences and a correct Boolean disclosure decision for arbitrarily small positive pulses.
- Positive-cohort trajectory bounds and direct-impact pulse peak for every finite cohort count, including a=0; funded trader margin at every subsequent mark under the declared constant-fundamental account.
- Real and complex symmetric transfer identities; unit-circle rate denominator and single-transfer bounds.
- General finite input-column quantity inequality and pulse attainment; explicitly Euclidean third-tap signal norm.
- Riccati root, its positive uniqueness, gain interval and explicit gain formula; actual scalar quadratic-loss derivative/OGD update; EMA algebra.
- Gaussian/CARA exponential integral and quote inequality from a HasLaw Gaussian hypothesis; bounded robust quote and baseline comparison.
- Actual willingness-to-pay integral, baseline-dependent allocation loss and constrained static capacity maximum/monotonicity.

Full merged-measure/minimal-realization, Gaussian minimax/Pinsker and all-horizon model-to-experiment bridge, actual positive-cohort spectral-mixture construction, passive fourth moments, Kalman MMSE, abstention, Kreiss/network and finite-window-gate formalizations remain Codex work. Conditional intermediate lemmas remain labeled conditional. See coverage for the precise remaining steps.

## Reproduce

The pinned mathlib commit is d13f23b723b8a846827a245b89c10fc7d3f11612. From this directory, with Lean/Lake available:

```sh
MATHLIB_NO_CACHE_ON_UPDATE=1 lake update
lake exe cache get Mathlib.Basic.Real.Basic Mathlib.Analysis.Real.Sqrt Mathlib.Tactic.Ring Mathlib.Tactic.Linarith Mathlib.Tactic.FieldSimp Mathlib.Tactic.Positivity Mathlib.Tactic.NormNum Mathlib.Algebra.BigOperators.Fin Mathlib.Data.Fin.VecNotation Mathlib.Data.Nat.Dist Mathlib.Probability.Distributions.Gaussian.Real Mathlib.Analysis.InnerProductSpace.PiL2 Mathlib.Analysis.Calculus.Deriv.Pow Mathlib.Analysis.SpecialFunctions.Integrals.Basic Mathlib.Analysis.Complex.Basic Mathlib.InformationTheory.KullbackLeibler.Basic Mathlib.Probability.Distributions.Gaussian.HasGaussianLaw.Basic Mathlib.MeasureTheory.Measure.WithDensity Mathlib.MeasureTheory.Integral.Prod Mathlib.Algebra.Order.BigOperators.Group.Finset
python3.11 verify_formalization.py
```

On this Mac, .lake and the shared mathlib cache reside on the mounted T9 drive. They are omitted from the package. Other machines can resolve the pinned dependencies normally. A first dependency/cache installation requires free disk space; the source bundle itself is small. The verifier needs its surrounding manuscript paths to bind the receipt to the current source; the review ZIP preserves that directory structure.

formal_verification_receipt.json and checked_theorem_types.json are the acceptance evidence for these declarations. A receipt does not prove real-market assumptions, novelty, causal identification or independent human review.

## Additional completed formal subresults

ARKernels.lean proves the exact backward factorization of every finite AR kernel, a uniform coercivity bound for positive mixtures, strict nonzero execution cost and the energy bound for the actual solvent trader account. CausalConvolution.lean derives all causal columns, their Euclidean first-column bound and the greatest lifetime-quantity signal norm. GaussianInformation/ProductInformation/GaussianRecords derive actual scalar/product/finite-record Radon-Nikodym likelihoods, equal-variance KL, the lifetime-quantity information bound and pulse attainment for arbitrary baseline means. PriceOutputGain.lean proves the exact price-only peak gain over all signed initial states and time. ComplexTransfers.lean derives the explicit uniform unit-circle difference bound.

The remaining induced L2/Parseval, full Gaussian minimax/Pinsker, actual cohort spectral-mixture, realization, Kalman, passive, Kreiss/network and gate obligations are still explicitly tracked. Named intermediate proof counts are not a percentage of full-paper completion.

