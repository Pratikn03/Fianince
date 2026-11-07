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
