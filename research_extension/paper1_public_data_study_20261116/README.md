# Paper 1 public-data observational and walk-forward study — delivered 15 November 2026

This directory archives the evidence package delivered with the 141-page revision
`pdf_delivered/Paper1_Observationally_Equivalent_Algorithms_Public_Data_Revision_2026-11-16.pdf`
(Supplement S31).

## Provenance

- Produced by a parallel author-side session running on Linux (Python 3.13.18,
  numpy 2.4.6, pandas 2.2.3, seed 20261116), started 2026-11-15T22:33:53Z,
  finished 2026-11-15T22:36:30Z (`results/full/run_manifest.json`).
- The delivering session reported a clean working tree on branch
  `paper1-focused-validation-2026-11-14` at commit
  `3b8bc316c0cc15d09e1670e528b041d4ad950d85`, but that machine could not
  authenticate its HTTPS push. That commit is **not** present in this repository
  clone; this directory integrates the delivered artifacts (PDF + results zip)
  so the work is preserved and mirrored on GitHub.
- Artifact integrity (SHA-256, computed at intake on this machine):
  - `Paper1_Public_Data_Results_2026-11-16.zip`:
    `6d414fd7bf555eb5b2d26b09f019e55ce9786496cb3595b47a117eb9c4df5e57`
  - revision PDF:
    `2b02c1e6fe980d4db605bb6336cd5af4378d111d5fc0549f098881cb43cc951c`
- Run pins from the manifest: `protocol_sha256`
  `4345510fd1d1b16021483a726494f0aafb21f3b7bc7045bc522c5c1d3204b40e`,
  `source_sha256` `7ac9abab8beaeb45d9112c0bd974a37407cfe13e008ff738c33cd78da9e59db4`.

## Contents

- `Paper1_Public_Data_Results_2026-11-16.zip` — original delivered archive.
- `results/full/` — extracted contents of the archive:
  - `run_manifest.json`, `market_summary.json`, `account_summary.json` — machine-readable study summaries.
  - `market_walk_forward_daily.csv`, `market_daily_scores.csv`, `market_robustness.csv`,
    `market_robustness_summary.csv`, `market_forecast_diagnostics.csv` — Binance walk-forward outputs.
  - `binance_data_receipts.csv` — per-day SHA-256 receipts for the public Binance
    1-minute kline archives (all `archive_sha256_verified = True`).
  - `account_address_summary_all.csv`, `account_address_summary_complete.csv`,
    `account_sampling_ledger.csv`, `account_liquidation_event_windows.csv`,
    `account_native_perp_robustness.csv` — Hyperliquid address-level outputs.
  - `market_walk_forward.png/.pdf`, `account_observational_summary.png/.pdf` — figures.

## Headline readouts (from `run_manifest.json` / summaries; not re-executed here)

- **Market study (Binance BTCUSDT/ETHUSDT 1m, 84 days per symbol, 241,920 rows):**
  development-period gate coverage 1.0 with mean admission ≈ 1.3–1.4% and zero
  exceedances did **not** transfer to the final historical validation window:
  pooled coverage 0.857 (block-bootstrap 95% CI 0.732–0.964), mean admission
  ≈ 1.0%, mean positive exceedance ≈ 2.16 bp, maximum exceedance 35.1 bp.
  Forecast diagnostic: median relative MSE reduction ≈ 0.6–0.9% vs ≈ 0% placebo.
- **Account study (Hyperliquid address-level, 60 complete-history addresses):**
  liquidation-address share 26.7% (95% CI 16.7–38.3%); mean liquidation loss
  59.4 bp with CI 10.6–123.7 bp and median 0 (highly concentrated; max 1,467 bp);
  mean net realized closed PnL −$24,034 (CI −$67,931 to +$5,927). Descriptive
  Spearman associations only (gross notional ρ = 0.63); no causal claim.
  All-histories sensitivity (66 addresses) shifts pooled loss to 9.1 bp —
  sensitive to weighting and history inclusion, as the revision states.
- **Natural-experiment screen:** the Hyperliquid margin-framework change
  effective 2025-03-15 is **rejected** as a validated natural experiment
  (anticipation, treatment definition, comparison group, and spillover checks
  not established; historical account equity not available in the official
  user-fill extract).
- **Future collection lock:** a prospective public-data window
  2026-12-01 through 2026-12-31 UTC is locked under `protocol_sha256` above,
  analysis not before 2027-01-02, frozen candidate order, modifying neither H1
  nor the existing Binance prospective replication. Outcomes were not available
  at delivery time.

## Evidence status (verbatim from the manifest)

`real_public_market_data: true`, `real_public_address_data: true`;
`field_experiment`, `market_welfare`, `participant_welfare`,
`participant_intervention`, `natural_experiment_causal_effect`,
`prospective_outcome`, `h1_outcome_accessed`,
`independent_mathematical_review`, `independent_novelty_review`: all **false**.

Interpretation: the package strengthens the paper's empirical boundary analysis
and reproducibility, but does not support deployment, causal-welfare, or
participant-intervention claims. No new Lean build is claimed; the 150
formal-source hashes are unchanged from the previous verification receipts.
