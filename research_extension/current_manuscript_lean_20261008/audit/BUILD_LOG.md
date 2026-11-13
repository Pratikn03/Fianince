# Build log (GitHub Actions job "Lean 4 Formal Mechanization Audit")

The job runs `lake exe cache get`, `lake build`, `lake env lean AxiomAudit.lean` and
`python3 verify_formalization.py`. The last step fails on any `sorry`, `admit`, `native_decide` or added axiom, and on
any named theorem whose axioms go beyond {propext, Classical.choice, Quot.sound}.

| Commit | Run | Lean job | Notes |
|---|---|---|---|
| f2f64a4 | 42285123772 | success | KalmanTied (S5.1, S5.2) |
| afd9d6c | 42320205700 | failure | PassiveVariance: noncomputable abbrev. GaussianHCR: instance at `n = 0`. CapitalConverse: rewrite pattern and ambiguous names. |
| 50f1fb5 | 42321490051 | failure | GaussianCR: implicit arguments of `nhdsWithin_le_nhds`. SpectralID: one `ring` missing. PassiveVariance, GaussianHCR and CapitalConverse built. |
| 1bff88f | 42322651256 | failure | CRActual: explicit argument of `comp_hasDerivAt_of_eq`. GaussianCR, SpectralID and SpectralH built. |
| 727ac9c | 42323561223 | failure | IVBoundary: missing `Real` import. CRRaw: `inv_smul` rewrite. CRActual built. |
| 65847c2 | 42324342693 | failure | CRRaw: `inv_smul` argument order. |
| cebb5c5 | 42325228369 | **success** | 931 named declarations; `NAMED_PROOFS_BUILD_AND_STRICT_AXIOM_AUDIT_PASS`; only standard axioms. |
| 4d6adfc | 42339802397 | **success** | PassiveMatched (any moment-matched pair; K = 2 Gauss/Gauss–Radau) |
| 51e0896 | 42340738038 | **success** | ModelLink (eigenvalues = poles; impulse transfer function), GaussRadau3 |
| 21ff920 | — | failure | CRScaling: `HasDerivAt.div`/`.pow` resolved to `HasFDerivAtFilter` (Deriv.Add not imported). |
| c0b2d45 | 42342953769 | failure | CRScaling: `field_simp` could not clear squared denominators; replaced by `p1_K2_alg`. |
| 1687175 | 42344595527 | failure | FisherBounds: missing `Real` import. CRScaling, CRScalingH built. |
| 26f8995 | 42345445176 | failure | CRS71iii: higher-order unification in range reduction; `ring` on powers. FisherBounds, CRTaps built. |
| c18188b | 42346346197 | failure | CRS71iiiEta: stray parenthesis. CRS71iii built. |
| 7059b69 | 42347257874 | **success** | 1026 named declarations, 109 modules; `NAMED_DECLARATIONS_KERNEL_CHECKED_STANDARD_FOUNDATIONS_ONLY`. S7.1(iii) end to end. |
| 708beda | — | **success** | EquilibriumInvariance (Theorem 4.5, E1) |
| 8a741c0 | — | failure | InventoryEquilibrium: rewrite looked inside a `let`; fixed with a helper lemma |
| a06a62e | 42412283005 | **success** | InventoryEquilibrium (Theorem 4.1 core) |
| 5fa3427 | 42413617975 | failure | EquilibriumReducedForm: missing `Real` import |
| 36f5042 | 42414734205 | failure | EquilibriumReducedForm: `sum_div` not imported |
| 9351733 | 42415594000 | failure | EquilibriumReducedForm: `ring` could not split a product denominator |
| 8735e0b | 42416658027 | **success** | EquilibriumReducedForm (Theorem 4.2, fragility bounds) |
| 29dd037 | 42425469307 | not run | GitHub Actions refused to start any job (account billing). `Paper1EquilibriumExtras.lean` built locally from source with Lean v4.34.1 and the pinned Mathlib: 1,056 jobs, success, no `sorry`, standard axioms only (`#print axioms` on all seven theorems). |
| (local) | — | **success (local)** | `Paper1EquilibriumInsider.lean` (Theorem 4.6) built locally from source with Lean v4.34.1 and the pinned Mathlib: 1,051 jobs, success, no `sorry`, standard axioms only. |
| (local) | — | **success (local)** | `Paper1HaltKernelBound.lean` (S28.2(i) kernel bound) built locally: 1,102 jobs, no `sorry`, standard axioms only. |
| (local) | — | failure (local) | InventoryIFT: `HasStrictFDerivAt.pow` not imported (replaced by products); rewrite through a `set` local inverse; derivative extraction. CRUniform: `dsimp` made no progress; `add_le_add_right` argument order; `ring` on a product denominator. |
| (local) | — | **success (local)** | `Paper1InventoryIFT.lean` (Theorem 4.1(iv), inverse function theorem), `Paper1CRUniform.lean` and `Paper1CRUniformW2.lean` (S7.1(iii) with a `T`-free lower constant under a small-gain margin): 3,254 jobs, no `sorry`, standard axioms only (`#print axioms` on the four main theorems). 1078 named declarations, 118 modules. |
| (local) | — | failure (local), then **success (local)** | `Paper1KCohortUniform.lean` (Theorem `thm:kcohort` with a horizon-free constant). First build: a local name shadowed the measurable-set hypothesis, and one `ring` had no goal left. After the fix: 3,268 jobs, no `sorry`, standard axioms only. 1081 named declarations, 119 modules. |
| (local) | — | **success (local)** | `Paper1KCohortEstimators.lean` (Theorem `thm:kcohort`, estimator statements for weights and the Wasserstein loss, uniform in the horizon). Built first time: 3,269 jobs, no `sorry`, standard axioms only. 1085 named declarations, 120 modules. |
| (local) | — | **success (local)** | `Paper1SaturatingSufficiency.lean` (core version Section 7: sufficiency of the capacity-weighted measure for saturating traders; no information without stress, pathwise; the market follows the linear market until the first band exceedance). Standard axioms only. 1093 named declarations across 121 modules. 8 November 2026. |
| (local) | — | **success (local)** | `Paper1CoreExtensions.lean` (core version: Proposition 3.2 for arbitrary linear kernels; Proposition 7.5, traders that deleverage or follow any causal rule outside their bands). Standard axioms only. 1098 named declarations across 122 modules. 8 November 2026. |
| (local) | — | **success (local)** | `Paper1StressIdentificationGeneral.lean` and `Paper1StressIdentificationTanh.lean`: Theorem 7.4 of the core version in general form (any odd shape with independent dilations, any number of traders); the hard limit and tanh have the property; a cubic shape does not. `Paper1StressIdentification.lean`: seven trivial declarations removed after the 10 November audit, one renamed (`p1_proportional_trade_recursion`). The three modules were built here with their imports (1,955 jobs) and `#print axioms` was run on all 37 theorems in them: standard axioms only. 1135 named declarations across 125 modules (a count of the sources). 10 November 2026. **The whole-project receipt was not regenerated.** `formal_verification_receipt.json` is still the 9 November full run (1,121 declarations, made on the author's machine). This environment has no Mathlib cache, and four modules import all of Mathlib, so `verify_formalization.py` stops at its 240-second build limit. `AxiomAudit.lean` and `named_declarations.json` already list the 1,135 names; run `python3 verify_formalization.py` on a machine with the Mathlib cache to refresh the receipt. |
| (local) | — | **success (local)** | `Paper1EveryKHalt.lean` (2 theorems: the counting step of the every-K halt lemma, core version Lemma S5.3(iii)). 11 November 2026. Built here with its imports (871 jobs); `#print axioms` on both theorems: standard axioms only. 1137 named declarations across 126 modules (a count of the sources). The whole-project receipt is still the 9 November run; see the previous row. |
