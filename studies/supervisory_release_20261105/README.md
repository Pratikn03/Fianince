# Paper 1 supervisory proof and accounting release

The release builds on main `5c93dab1ed2e690c65506fbece92aa315b255c47` and the subsequent supervisory review branch. See [RELEASE_REVIEW.md](RELEASE_REVIEW.md) for the completed work and remaining review obligations.

## Proofs

- `Paper1GaussRadau.lean`: eight theorems construct the exact K=2 witness used by the numerical example and prove its actual Gaussian-record lower bound. The dominant-intensity result assumes `0 ≤ d ≤ u/3`, which includes the accounting example `d=0.1`, `u=0.4`.
- `Paper1SupervisoryDecision.lean`: eight theorems cover robustness, an actual product-Gaussian unsafe-halt event, its error budget, the no-data two-action optimum and after-cost acquisition algebra.
- `tools/verify_release.py`: builds the full project, checks every named theorem and all CurrentMM constants against standard axiom dependencies, records exact new theorem types, and binds the receipt to active manuscript and figure hashes. It explicitly does not claim full manuscript equivalence or independent review.

The new files live under `research_extension/current_manuscript_lean_20261008/CurrentProofs/` and are imported by the main proof project. The older `Robustness.lean` is retained as an earlier scalar-only check, not the probability theorem.

## Experiment

```sh
python studies/supervisory_release_20261105/run_study.py
```

Requires NumPy and SciPy. Six archived response/decision rows independently reproduce within 2.1e-17 in response discrepancy. The accounting layer assumes a declared scalar Gaussian disclosure contract, common hypothetical sample fees, a response allowance and fixed-menu utility. It does not directly observe tagged flow or class positions.

`results/study.csv` retains all 4,608 configurations: 2,304 normal-quantile cases plus 2,304 conservative Chebyshev-gate cases. These are deterministic sensitivity cases, not independent markets. Negative outcomes are retained. `results/study.json` records representative outcomes and explicit failures.

For the normal-quantile rule, positive/negative/tied paid-information values number 1,207/1,079/18. For the conservative rule covered by the new actual-event theorem, they number 781/1,499/24. At N=128 the conservative representative has information bill 0.114, loss 1.349034, and conditional net advantage 0.100185 surplus units. These are not real-market profits or estimated social welfare.

## Interpretation and release

`EVIDENCE_INVENTORY.md` records inspected historical results and what they cannot establish. `CLAIM_SCOPE.json` inventories the current manuscript's numbered environments without treating inherited mappings as newly reviewed proofs. General-K supervisory dominance remains an explicit additional condition. No market calibration, complete novelty certificate, coauthor approval or journal acceptance follows from the build.

Both PDF variants are rebuilt from synchronized LaTeX. The SSRN variant is the working-paper candidate; the full development variant retains the dated work register. No SSRN submission is performed by this release.
