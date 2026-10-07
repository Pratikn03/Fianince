# Reconstructed monthly fee-event analysis

This reconstructs the original monthly question using the restored original 2022 panel: 192 asset-days, eight assets, 24 sampled dates, two dates per month. It does not add a dataset or establish a causal fee effect.

The monthly model contains asset and sampled-date fixed effects and 11 BTC-by-month interactions, with June as the reference. Rank is 42 and residual degrees of freedom are 150. All 44 coefficients across legacy/observed Q/S match independently aggregated monthly treated-minus-control gaps. Classical, HC1, HC3, asset-cluster, date-cluster and month-cluster calculations are retained.

For observed Q, the five-restriction January–May pretrend reference has classical p=0.323499, HC3 p=0.288727, and date-cluster p=0.0000392661. These differences preclude treating a selected non-rejection as validation of parallel counterfactual trends. One treated asset, few clusters, serial dependence, concurrent changes and spillovers remain limitations.

Month clustering is degenerate because monthly treated interactions fit the treated-month cluster contrasts. Date-saturated interactions likewise make date-cluster event covariance degenerate; HC3 is unavailable at unit leverage. Joint F/p values are absent for invalid references. Individual degenerate contrast entries carry explicit status labels; their numerical zero-width intervals are not valid uncertainty intervals.

Seven focused tests cover point aggregation, QR covariance calculations, relabeling, event clocks, and saturation/high-leverage failures. The cumulative revision suite passes 41 tests. The manuscript lineage ledger checks 28 tables and 3,135 cells against named output fields; this checks rendering and numerical provenance, not scientific validity.

Rerun from the release root:

```sh
/opt/homebrew/bin/python3.11 research_extension/gap_closure_20261006/event_study/monthly_event_study.py
/opt/homebrew/bin/python3.11 -m pytest -q research_extension/gap_closure_20261006/event_study/test_event_study.py
```

The full result and covariance matrices are in `event_results.json`. The original F=.42,p=.835 statement remains untraced; the reconstructed calculations do not authenticate that historical literal.
