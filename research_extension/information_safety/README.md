# Information-safety extension of Paper 2 (data-free)

Code for Sections 5–7 and 12 of *From Human Markets to Machine Markets* and the matching Internet Appendix material. Every
result here is a simulation, an exact computation or a certified numerical computation; nothing downloads data.

```
python3 -m pip install -r requirements_lock.txt
python3 -m pytest -q tests          # 23 unit tests, about 20 seconds
python3 run_all.py                  # all tests T01-T15, about 8 minutes; writes results/<test>.json and results/IS_results.json
python3 run_all.py T13_venue_mode   # one test
```

On Colab: upload this folder (or the replication zip), then run `!pip install -q mpmath` and `!cd information_safety && python3 run_all.py`.

## Layout (blueprint section G)

| Module | Contents | Paper |
|---|---|---|
| `model_contracts.py` | cohort economy, impulse responses, moment inversion; declared observation and risk contracts (`CONTRACTS`) | Sections 2, 5 |
| `exact_rational_witness.py` | two-market witness in rational arithmetic; two-world capacity-loss bound (T01, T02) | Ex. ex:witness, Prop. prop:twoworld |
| `price_response.py` | three-state book with depletion; mechanism controls (T08) | Section 4, Section 12 |
| `data_compatibility.py` | Markov–Krein principal representations; **certified** endpoints by weak duality and interval arithmetic (ThmB, T10) | Thm. thm:window, Lemma lem:certnum |
| `uncertainty_calibration.py` | O1 certificate, O1' t-certificate and Hotelling region; sample complexity (T03); misspecified coverage (T11) | Thm. thm:certcost, Prop. prop:hotelling |
| `risk_gain.py` | drift-plus-convolution worst case, peak vs summed gain | corrected gate, Thm. thm:guard |
| `adversarial_paths.py` | exhaustive sign enumeration (T05); joint support function vs LP (T05b) | corrected gate |
| `robust_admission.py` | closed-form guard (T06); venue mode with action-dependent dynamics and interval branch and bound (T13) | Thm. thm:robustguard, Prop. prop:venue, Thm. thm:venuebb |
| `disclosure_experiment.py` | public vs tagged vs audited information (T07); noisy-proxy intersection (T15) | Thm. thm:disclosure |
| `monte_carlo_coverage.py` | certificate coverage, width, abstention (T04); misspecification (T09) | Section 12 |
| `economic_ledger.py` | rebate from a certified S (T12); balance-sheet step (T12b) | Prop. prop:equil, Thm. thm:forward |
| `adaptive_probing.py` | anytime-valid sequential certification (T14) | IA, Prop. prop:probe |
| `interval.py` | outward-rounded interval arithmetic used by T10 and T13 | — |
| `run_all.py` | runs everything; every result file records the code hash, library versions, seeds, status and runtime | — |

Tests in `tests/` follow the blueprint names: `test_witness_exact`, `test_convolution_gain`, `test_safe_set_soundness`,
`test_adversarial_attainment`, `test_two_world_tv_bound`, `test_coverage_and_abstention`, `test_disclosure_monotonicity`,
`test_robust_optimizer`, `test_balance_sheet_accounting`, plus `test_probing`.

## What is and is not claimed

* T10 and T13 are **certified**: their safe/unsafe classifications and window endpoints hold in exact real arithmetic, not only
  in floating point, because every operation is rounded outward and the sign conditions are proved on subdivisions.
* T04, T09, T11 and T14 are Monte Carlo estimates of coverage under declared contracts; they say nothing about observational
  order-book data, for which Paper 2 reports only bootstrap diagnostics (Parts 15–16).
* The restructuring of October 20, 2026 moved code between files without changing any result: `results/IS_results.json` is
  identical, key by key, for T01–T09 and T12.
