# Model diagnostics: results and scope

All alternatives are fixed retrospective diagnostics on existing data. No untouched holdout, causal identification, scholarly review or10/10 certification is claimed.

## Covariance restrictions

| Asset | Cases | Minimum p | Maximum p | Result |
|---|---:|---:|---:|---|
| BTC | 8 | 5.96077e-09 | 3.24499e-08 | All reject at5% under asymptotic reference |
| ETH | 8 | 7.75355e-06 | 4.40383e-05 | All reject at5% under asymptotic reference |
| ADA | 8 | 0.0106974 | 0.0276065 | All reject at5% under asymptotic reference |

The parameterization spans stable transitions with SPD innovation covariance, including stable matrices whose diagonals exceed one. All cases have rank11 moments and rank7 parameter Jacobian. Six starts agree numerically; this is not a global optimality proof. Centering changes the maintained mean model and has finite-segment estimation limits.

## Predictive comparisons

All513 fold/model records and96 AR-versus-VAR lag/target contrasts are saved. Six dates train the first model; seven recorder dates and five joint dates are then evaluated. No fitting/scaling uses future dates. Every price-loss interval includes zero. Some flow intervals exclude zero before multiple-testing/dependence adjustments; those are retained and not interpreted as causal learning.

| Asset | Single-recorder EMA price gain, VAR1 over AR1 | Joint CB price gain, VAR1 over AR1 |
|---|---:|---:|
| BTC | 0.328% | 1.394% |
| ETH | 0.014% | -21.583% |
| ADA | 0.067% | -45.271% |

Negative gain means the joint model worsens mean squared error. Results are equal-date averages with few ordered dates; they are not causal or universally reliable forecasts.

## Heteroskedastic source audit

The old C2 fit does not independently defend its timing, dynamic innovations, invariant slopes, regime exogeneity/conditional orthogonality, branch labels or uncertainty. The exact alternate-branch example gives identical covariance matrices in three regimes. The conditional-selection illustration starts with independent errors and induces conditional correlation. These are assumption-audit results, not estimates of actual structural market shocks.

## Active remaining work

Provider authentication for other supplied samples, full semantic/literature review, additional theory/noise/operational/calibration work, existing-policy audit and independent scrutiny remain active.
