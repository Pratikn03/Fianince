# Gate24 corrected evidence handoff — 2026-09-26

Canonical compact artifact: [gate24_summary.json](gate24_summary.json). It contains no raw replications.
Status: **PENDING_CALIBRATION** for Gates 2, 3 and 4. Implementation/accounting checks passed; real execution and structural calibration are not established.

This handoff is an annotation-only summary of the frozen numerical run in
[final/gate24_analysis_results.json](final/gate24_analysis_results.json).
The numerical values below were not rerun or changed for the joint-scale labeling correction.
The root-level first corrective result and the later full result are preserved as prior corrective attempts.
The compact artifact records current final code/test hashes separately from the hashes of the code that generated the frozen numerical run.

## Paper-ready numbers and interpretation

OLS with intercept regresses close-to-close absolute price change on signed base volume,
`2*taker_buy_base_volume - total_base_volume`. Prices are USDT/base and flows are base units,
so the slope is **USDT/base²** (price change per signed base unit), not a dimensionless
return/imbalance coefficient, and not a causal execution-impact estimate. Signs are retained;
zero-variance flow or nonpositive slopes do not receive a positive calibration substitute.

Each asset has 129,600 one-minute bars, 90,719 training price-change observations, and
38,880 held-out observations. Bars begin 2025-01-01 00:00 UTC. Training outcomes run
2025-01-01 00:01 through 2025-03-04 23:59 UTC; holdout is 2025-03-05 00:00 through
2025-03-31 23:59 UTC. Arrival-rate anchors also use only training observations.

| Asset | Training slope (USDT/base²) | Holdout diagnostic slope | Holdout R² | Actual Jacobian eigenvalues |
|---|---:|---:|---:|---|
| BTC | 2.620070045 | 2.556021780 | 0.255626 | -0.8998198563, 0.9607848340 |
| ETH | 0.006654932375 | 0.003915126403 | 0.128126 | 0.3825172784, 0.9851552554 |
| SOL | 0.00006398253303 | 0.00003658809071 | 0.092325 | 0.3856195151, 0.9853484937 |

The implemented unconstrained Jacobian is
`J = [[a - kappa*phi, q], [eta*(a - kappa*phi), 1 - eta + eta*q]]`.
Its second row uses **x_next** memory and its first row includes fundamental demand
`-phi*x`. All three fitted-proxy scenarios have spectral radius below one.
The legacy `|a|+|q|=0.82` is only a parameter summary, not the stability certificate.
The maintained a=.4, q=.42, eta=.05 and phi=.5 are synthetic assumptions.

| Asset | Halts at 0/−1/−3/−5% shocks | Final dealer equity at 0/−1/−3/−5% (USDT) |
|---|---|---|
| BTC | 0% / 100% / 100% / 100% | 257345.52 / 256830.23 / 255799.32 / 254768.41 |
| ETH | 16% / 100% / 100% / 100% | 28214.75 / 28161.78 / 28055.58 / 27949.39 |
| SOL | 16% / 100% / 100% / 100% | 251323.90 / 251391.76 / 251751.93 / 252224.11 |

These are 50 replications per shock cell, 64 steps per run, repricing at step 16.
All cells have zero observed defaults; do not call the halt pattern a solvency frontier.
Exact 95% halt-rate intervals: 0/50 = [0, .0711217365], 8/50 = [.0717007672, .2911263066],
50/50 = [.9288782635, 1]. These intervals describe the maintained synthetic seeds.

Capacity is a synthetic symmetric bound anchored to the snapshot top-five BID quantity:
1.52876 BTC, 5.2722 ETH and 1077.93 SOL. The old hidden 2-base-unit minimum is removed.
Initial dealer cash is 2*reference_price*capacity. Price marks and equity continue through
the full horizon after an absorbing halt; no subsequent transactions or terminal liquidation occur.
At negative x, fundamentalists **buy** and the dealer sells; the old selling/long-dealer explanation is incorrect.

## Joint scale diagnostic, not isolated capacity sensitivity

The 0.5x/1x/2x grid is explicitly **JOINT_SCALE_DIAGNOSTIC**.
Capacity, initial cash and exogenous-noise standard deviation all co-vary:
`capacity=m*anchor`, `cash=2*p_star*capacity`, `noise_std=.05*capacity`.
The summary lists all three values at every scale. Normalized noise seeds are matched,
but the physical disturbances and capital are not held fixed. Baseline price displacement
therefore scales with the multiplier. Across these joint scales, the halt-rate sequences
remain BTC [0,1,1,1], ETH [0.16,1,1,1], SOL [0.16,1,1,1].
**No isolated causal capacity effect, intervention welfare or empirical policy benefit is identified.**

## Cash, inventory and fees

Every adaptive, fundamentalist and exogenous fill has a counterpart cash/inventory transfer.
Dealer half-spread is income, counterpart spread is a debit, and fees have an explicit
recipient. The checks cover aggregate cash, base inventory, aggregate marked equity and
each party's revaluation-plus-trading identity. External repricing of pre-existing inventory
is included. Counterpart credit is unconstrained, which is a maintained simulation assumption.

Largest absolute cash/equity/accounting residual across the 1,800 joint-grid runs:
BTC 1.2805685401e-9 USDT, ETH 8.0035533756e-11 USDT, SOL 9.8953023553e-10 USDT.
Largest normalized residual across assets: 8.4541748602e-15.
The checks use absolute-plus-relative tolerances (quote atol=1e-10, base atol=1e-12, rtol=1e-12).
**Do not retain the universal absolute residual <1e-10 claim.**

## Cost and time scope

Each hypothetical round trip assumes one entry plus an equal-size unwind at the same
reference mid. Each leg crosses half the spread and integrates assumed linear marginal
impact to 0.5*kappa*units². Execution impact, decay and symmetric unwind assumptions remain unvalidated.
Fees are unknown by default, so complete budgets are null. Fee sensitivities are declared
assumptions, not measured fee schedules. All amounts are USDT; USD equivalence is not assumed.

For 1,000 round trips of 1,000-USDT entry notional:

| Asset | Friction excluding fees (USDT) | With assumed 1 bp/leg | With assumed 10 bp/leg | 50,000 passive arrivals (hours) |
|---|---:|---:|---:|---:|
| BTC | 0.488678 | 200.488678 | 2000.488678 | 0.393639 |
| ETH | 4.666683 | 204.666683 | 2004.666683 | 0.487900 |
| SOL | 90.498006 | 290.498006 | 2090.498006 | 0.608273 |

Arrival counts are **50 trades × 1,000 hypothetical episodes = 50,000**, not 1,000 events.
These durations do not establish exogenous randomized episodes or complete protocol duration.
Queue/fill dynamics, adverse selection, opportunity cost and information leakage remain pending.

## Input provenance

Only 9 historical one-minute ZIPs and 3 cached REST depth snapshots are consumed:
18,445,389 bytes, not the full 3.41-GB acquisition. aggTrades and DOGE/ADA are unused.
Only BTC January 2025 has a matching cached official .CHECKSUM (1/9 ZIPs, 1/12 total inputs).
The other eight archive sidecars are missing. All twelve local SHA-256 hashes are recorded,
but local hashes and old manifest flags do not establish official verification.

The three depth inputs are live REST `/api/v3/depth` snapshots, not historical
`/data/spot/daily/bookDepth/`. Their actual capture timestamps are unverified/null.
The old manifest says downloaded_on=2026-09-24; that is not an exchange capture timestamp
and does not establish alignment with January–March 2025.

## Manuscript pointers (no paper edits performed here)

Use label/text anchors because the shared manuscript is being edited concurrently:

- `paper/Machine_Markets_Final_Integrated_Paper.tex`, abstract and contribution statements:
  replace Gate24 execution-calibration/3.41-GB validation language with observational proxy and synthetic diagnostic scope.
- `sec:gate24_empirical`: replace coefficient formula/units and report chronological holdout and pending status.
- `tab:gate24_empirical`: revise fees, entry/unwind, USDT amounts, 50,000-arrival timing and snapshot limitations.
- `tab:gate4_shock_ci`: replace rates/equities and identify the actual Jacobian, 64-step horizon and assumptions.
- Paragraph `Dealer inventory orientation and equity trajectory under shocks`:
  correct fundamentalist demand sign and absorbing-halt/full-horizon mark semantics.
- The 0.5x/1x/2x depth paragraph: call this JOINT_SCALE_DIAGNOSTIC and list all co-varying dimensions;
  remove isolated capacity robustness, causal capacity effect and welfare interpretations.
- Data-availability paragraph beginning `The Gate~2--4 empirical calibration study`:
  correct consumed data size, checksum coverage, REST snapshot source and missing timestamps.
  The simulator is in `gate24_analysis.py`, not a separate `calibrated_simulator.py`.
- Traceability table's Clean-Room Calibration row and Empirical Microstructure conclusion row:
  point to the new compact artifact and mark calibration pending; local implementation does not certify independent authorship.

## Verification and preservation

21 new repair tests were first observed failing (18 original defects, 2 reporting cases,
1 joint-scale disclosure case). The current integrated command passes **187 tests**.
The isolated native suite runner additionally passes **98 scientific tests and 6 release-tool tests**.
See tests_before*.txt, tests_after_joint_scale.txt and native_suite_logs/test_report.json.
Finite-difference Jacobian, known eigenvalues, party cash/inventory conservation, reversal,
absorbing halt/default, holdout isolation, fee/unwind, provenance and output-lock tests are included.

The historical Gate24 JSONs remain byte-identical:
- analysis results: 0483fdd5c9488b90b4061292d4abea79badb10f1895421f04359eb0bde7ec96e
- acquisition manifest: b9f72868b2c7d8c7d89930d72ba0bf562b6af335974655ed775dce75b42c1144

Only Gate24 code, tests/test_gate24_repairs.py, and new files below this output directory
were changed by this task. No paper edits, commits, subagents, deletions or network acquisition.
The CLI refuses existing/legacy result destinations and creates files exclusively.
