# Build log (GitHub Actions job "Lean 4 Formal Mechanization Audit")

The job runs `lake exe cache get`, `lake build`, `lake env lean AxiomAudit.lean` and
`python3 verify_formalization.py`. The last step fails on any `sorry`, `admit`, `native_decide` or added axiom, and on
any named theorem whose axioms go beyond {propext, Classical.choice, Quot.sound}.

| Commit | Run | Lean job | Notes |
|---|---|---|---|
| f2f64a4 | 42285123772 | success | KalmanTied (S5.1, S5.2) |
| afd9d6c | 42320205700 | failure | PassiveVariance: noncomputable abbrev. GaussianHCR: instance at `n = 0`. CapitalConverse: rewrite pattern and ambiguous names. |
| 50f1fb5 | 42321490051 | failure | GaussianCR: implicit arguments of `nhdsWithin_le_nhds`. SpectralID: one `ring` missing. PassiveVariance, GaussianHCR and CapitalConverse built. |
