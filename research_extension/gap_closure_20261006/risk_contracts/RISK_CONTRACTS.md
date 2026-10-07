# Risk-contract extensions and limits

Four propositions are proved locally: signed directed coupling under downstream-only output and a fixed Euclidean state ball; common-metric changing-coefficient/nonlinear/affine loss bounds; finite Gaussian input coverage; and a nonlinear dollar-mark mapping. Finite-horizon noncontracting/unit-root and population-second-moment cases are also derived.

The general hedged-portfolio monotonicity claim is false; the explicit fixed-coordinate counterexample cancels exposure at coupling2. Individually stable matrices can produce unstable switching products. Zero pricing error cannot bound all actual marked losses when fundamentals move. These are mathematical boundaries to retain, not unfavorable results to suppress.

The amplification witnesses include the stated directed cohort family and a symmetric positive-definite impact family. Symmetry/positivity does not establish a no-manipulation equilibrium or market calibration. Physical coordinates and shock/output contracts stay fixed within each family.

All15 constructed examples have exact rational prefix/block/Frobenius-tail comparisons. Empirical floating-point matrices and unknown parameters require independent roundoff/model bounds. The14 risk tests cover signs/output geometry, structural spectra, switching, changing coefficients, bounded nonlinear and affine residuals, Gaussian and moment-tail logic, and nonlinear marked losses.

## Reproduce

Use Python3.11 with NumPy/SciPy/SymPy, from the repository root:

```sh
python3.11 research_extension/gap_closure_20261006/risk_contracts/risk_contracts.py
python3.11 research_extension/gap_closure_20261006/risk_contracts/exact_tail_certificates.py
python3.11 research_extension/gap_closure_20261006/risk_contracts/write_risk_appendix.py
python3.11 -m pytest -o addopts='' -q research_extension/gap_closure_20261006/risk_contracts/test_risk_contracts.py
```

Run the exact-certificate step after the floating-point illustrative generator; it adds exact certificates to risk_results.json. The complete manuscript builder reads the actual result fields and proofs.

## Remaining gates

Actual exposures/capital, feasible orders, price/fundamental/currency channels, cash/funding/margin rules, noise population bounds, model/parameter coverage, economic admissibility and independent specialist scrutiny are not established by these examples or tests. Empirical covariance rejections remain. The full scientific objective is active.
