# Economic review and experiment runner - 29 October 2026

This is a separate **exploratory** development package. It does not replace the
registered tests or their results. A completed run is not an empirical pass, a
proof certificate, or a production risk-control guarantee.

Start with [RESEARCH_PLAN.md](RESEARCH_PLAN.md), [ECONOMIC_CONTRACT.md](ECONOMIC_CONTRACT.md),
and [CLAIM_LEDGER.csv](CLAIM_LEDGER.csv). The ledger covers 93 current theorem-like
environments from the reviewed snapshot, including remarks/examples/conjectures;
it is not a count of original or independently verified theorems.

## Run in Colab

Open [Economic_Review_Experiments.ipynb](Economic_Review_Experiments.ipynb).
Run all cells first in `smoke` mode. Change `MODE` to `full` and run the experiment
cell again for the larger study. Every run uses a new directory, saves the source
commit and source-file hashes, dependencies, input hash, seed and configuration,
and leaves old runs intact. Download the result ZIP at the end.

Local equivalent, from repository root:

```bash
python -m pip install -r studies/economic_review_20261029/requirements.txt
python -m pytest tests/economic_review_20261029 -q
python -m studies.economic_review_20261029.run --mode smoke --out /tmp/mm-review-smoke
python -m studies.economic_review_20261029.run --mode full --out /tmp/mm-review-full
```

`full` means the configured larger exploratory study, not full repository
replication. Runs E1/E2/E3/E4/E6 use CPU, no account or market downloads.

| ID | Target | Output | Interpretation |
|---|---|---|---|
| E1 | Corrected cumulative drift, pointwise peak and invariant box | `E1_drift.csv` | Resolvent cross-check plus random-model stress; induction, not Monte Carlo, supplies the box proof |
| E2 | Filter-induced persistence and timing | `E2_filter_controls.csv` | Martingale nulls with independent persistent flow, plus a structural synthetic model observed directly/through an EMA |
| E3 | Identity versus aggregate-risk target | `E3_information_targets.csv` | Exact known-pair Gaussian classification error; honest sum-of-taps interval with a conservative class tail |
| E4 | Risk-control comparison | `E4_matched_capacity.csv` | Baselines match the guard's training capacity; independent test episodes report capacity drift and paired loss uncertainty |
| E5 | Real-data forecasting diagnostic | `E5_real_data.csv`, predictions | Optional CSV, chronological purged train/validation/test, training-only transforms, paired block-bootstrap comparison |
| E6 | Coverage and misspecification | `E6_coverage.csv` | Independent Gaussian case versus correlated tap errors, heavy tails, biased readings and a violated memory floor |
| E7 | Existing economic/AI validation | Existing notebooks below | Separate data/GPU/prospective work; not auto-run or counted as completed |

E3 compares two **known alternatives with the same total feedback**. Its risk
target is identical by construction. It does not prove a uniform rate advantage
over unknown mixtures. Observation cost is `N*horizon`, not just the number of
experiments. Its simple confidence interval is not an optimal estimator.

E2's fitted VAR loop proxy is a diagnostic, not generally the structural total
`Phi`. An EMA changes the observation law; a model's true displacement is only
available in the synthetic comparison. E4 controls the position of a price-taking
dealer, not venue-wide admission. It has bounded shocks and fixed inventory,
without execution P&L, fills, funding, fees, cross-margin or economic welfare.
The oracle is a separate information benchmark; it is not capacity-retuned.

## Optional real-data CSV

Required columns:

```text
timestamp,market,price,signed_flow
2024-01-01T00:00:00Z,EXAMPLE,100.0,2.5
```

Use regularly spaced bars within each market, chronological rows, positive
prices, signed executed flow, no duplicate timestamps or missing required values.
Record the source, units, bar width, availability time, exclusions and whether the
sample has already been examined. Do not mix positions with executed flow.
The illustrative single row above is a schema, not data for inference.

```bash
python -m studies.economic_review_20261029.run --mode full \
  --csv /path/to/market.csv --window 120 --forecast-horizon 12 \
  --out /tmp/mm-review-market
```

Features at t use data through t; the target uses t+1 through t+H. The last H rows
of training and validation are purged at the next split. Ridge penalties are
chosen on validation, never test. The baseline is trailing volatility; the
augmentation adds finite-response and margin **proxies** from a rolling VAR.
All markets are reported. This is an exploratory predictive exercise, not a
replication of a registered primary and not a causal or structural identification
test. A stronger economic design and richer volatility baselines remain needed.

No CSV is bundled into the result ZIP. Prediction outputs still contain market
identifiers/timestamps: review data permissions before sharing them.

## Work that still needs your resources or expert input

* [K1 ETF design](../../thesis/evidence/K1_LETF_Test.ipynb): inspect its original
  registration and data requirements; use its specified primary unchanged.
* [B3 model diversity](../../thesis/evidence/B3_Diversity_Test.ipynb): model access
  and potentially GPU/API resources. Record exact model revision and prompt hashes.
* [B2 archived LLM test](../../thesis/evidence/B2_LLM_Test.ipynb): inspect existing
  results first. A new seed, prompt or model is a labeled replication, not another
  opening of the original primary.
* [H1 participant data](../../thesis/evidence/H1_Hyperliquid.ipynb),
  [H2 cascade design](../../thesis/evidence/H2_Cascades.ipynb), and
  [E2 prospective analysis](../../thesis/evidence/E2_Prospective_Analysis.ipynb):
  respect original accumulation/opening conditions. Notebook availability does
  not imply the data window has matured. No scheduled collectors were activated.

Independent statistics, time-series and microstructure review is still required.
See the open questions in the plan. Do not interpret passing Python tests or a
Lean name mapping as proof that all manuscript claims are valid.
