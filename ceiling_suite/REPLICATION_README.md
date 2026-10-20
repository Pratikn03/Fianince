# Replication package: Niroula & Niroula (Paper 1) and Niroula, Alkhushayni, Chen, Bhavsar & Niroula (Paper 2)

Every number in both papers is written to a result file by one of the notebooks or scripts below. Each paper's
Appendix "Reproducibility: source of every number" maps every table, figure and quoted number to the result file
(`results/<ID>.json`) or script output (`recomputed/*.json`) that produced it. "Part N" in the papers refers to
the notebook numbered N here.

## 1. Notebooks (Google Colab; data downloaded from public archives at run time)

All notebooks mount the same Google Drive folder `MyDrive/ceiling_suite/` and cache raw downloads and
intermediate files there (`data_xsec/`, `data_bybit/`, `data_bybit_ob/`, `data_cot/`, `data_spot/`).
**Run them in the order listed**: later parts reuse files written by earlier ones (noted in the last column).

| Part | Notebook | Paper(s) | What it produces (result IDs) | Pre-registration (SHA-256 prefix) | Needs from earlier parts |
|---|---|---|---|---|---|
| 1 | `Ceiling_Test_Suite.ipynb` | 1, 2 | Numerical theorem checks (`T*`, `P1.*`, `P2.*`, `R2-*`); spot tests | `P2.5` spot test (`b1fd7f8e`) | — |
| 2 | `Depth_Liquidation_Tests.ipynb` | 2 | BTCUSDT futures depth: validation, structural estimates, mediation, pre-registered test, events (`D1`–`D9`) | `P2_depth` (`d9521218`) | — |
| 4 | `Part4_CrossSection_Disclosure.ipynb` | 1, 2 | 30-symbol cross-section, tick events, 30-second depletion, thin-book test, disclosure metrics (`X1`–`X9`) | `P4_xsec` (`5910b6b4`) | — |
| 5 | `Part5_Replication_NewSymbols.ipynb` | 2 | Replication on 10 new thin symbols; post-hoc impact controls (`Y1`–`Y8`) | `P5_replication` (`6aa8e2c0`) | Part 4 cache |
| 6 | `Part6_FreshDays_Confirmatory.ipynb` | 1, 2 | Fresh-day replication, six-hour sizing backtest, Binance disclosure test (`Z1`–`Z8`) | `P6_fresh_days` (`65acda36`) | Parts 4–5 (`X3`, `Y3` results; minute cache) |
| 7 | `Part7_Bybit_SecondVenue.ipynb` | 2 | Bybit, trades only (`W1`–`W6`) | `P7_bybit` (`c457f40d`) | Parts 4–5 (`X3`, `Y3`) |
| 8 | `Part8_Paper1_SpotPanel_FeeEvents.ipynb` | 1 | Spot feedback panel and two fee events re-run from 1-second klines (`V2`, `V3`) | — | — |
| 9 | `Part9_VolatilityBenchmark.ipynb` | 2 | Thin-book test beyond a volatility-forecasting baseline (`U1`–`U6`); saves `blocks_p9_30sym.parquet` | `P9_volbench` (`71983f1a`) | Parts 4–5 |
| 10 | `Part10_Bybit_OrderBook.ipynb` | 2 | Bybit with order-book depth (`V3A`, `V4`–`V6`) | `P10_bybit_ob` (`ec2145fa`) | Part 7 (Bybit trade cache, optional) |
| 11 | `Part11_CFTC_Disclosure.ipynb` | 1 | CFTC Commitments of Traders disclosure test (`C3`, `C4`) | `P11_cot` (`6f1d6f35`) | — |
| 12 | `Part12_CertifiedGuard.ipynb` | 2 | Certified-guard backtest, economic size, Oct 10 2025 event (`E1`, `Q4`–`Q7`) | `P12_certified_guard` (`b9a56af4`) | Parts 4, 9 (`X3`, `Y3`, `blocks_p9_30sym.parquet`) |
| 13 | `Part13_PostHoc_Robustness.ipynb` | 1, 2 | Post-hoc checks: throttle guard, terciles, Bybit bars, IV estimate, fixed-grid depletion, CFTC basis signature, VPIN, Cochrane–Orcutt (`R1`–`R8`) | none (post hoc) | Parts 4, 7, 9, 11, 12 |
| 14 | `Part14_US_Equities.ipynb` | 2 | Thin US stocks, consolidated trades via Alpaca (`A1`–`A5`) | `P14_us_equities` (`f5800a69`) | — (needs a free Alpaca key) |

There is no notebook numbered 3.

### Pre-registration protocol
Each pre-registered notebook writes its specification to `prereg/<name>.json` and prints its SHA-256 hash **before**
any test-period file is downloaded, then counts every execution of the test cell in `prereg/test_set_unlocks_<n>.json`.
The specification files were e-mailed to the first author when written; those e-mails are the evidence of timing.
Hashes and unlock counts are reported in each paper's table notes.

## 2. Stand-alone scripts (Python 3, numpy/scipy/pandas; no data download)

| Script | Paper | Output |
|---|---|---|
| `theory/general_minimax.py`, `theory/lemma_checks.py` | 1 | Lemma (moment-matched pairs), Theorem (general memory), Table `tab:general` → `R_P1_general_minimax.json` |
| `theory/kcohort_upper.py` | 1 | Theorem (Prony upper bound), Table `tab:kupper` |
| `theory/disclosure_value.py` | 1 | Theorem (value of disclosure) |
| `theory/equilibrium.py`, `theory/t6m_search*.py`, `theory/thmA_check.py` | 2 | Equilibrium numbers, counterexamples, Theorem nomom check |
| `papers/recompute_theory.py`, `recompute_extra.py`, `recompute_crb.py`, `recompute_p1_capital.py`, `recompute_p1_protocols.py`, `recompute_p1_sprt.py` | 1 | Capital constants, protocols, CRB table, SPRT |
| `papers/recompute_p1_estimators.py` | 1 | ML at the critical noise level (Table `tab:crb`); four-estimator check (Table `tab:lecam`) |
| `papers/recompute_oct20.py` | 1, 2 | Cohort-split invariance; symmetric multi-asset network; re-optimization check (Prop. `prop:lucas`) |
| `papers/recompute_audit.py` | 1, 2 | Proof audit (Oct 2026): symbolic and numerical checks of Prop. shape (peak bracket), Remark counterexamples, Props. sum and equil (Paper 2); Thm. quantity K* bound, Thm. twocohort moments, Thm. blind example (Paper 1) → `R_audit_oct2026.json` |
| `papers/recompute_dollar.py` | 2 | Liquidation probabilities and dollar losses from `E1_economic_size` (Part 12) → `R_P2_dollar_translation.json` |
| `papers/calib_guard.py`, `papers/kreiss_table.py`, `papers/make_figs*.py`, `scripts_p45/make_fig_forest.py` | 2 | Calibrated guard illustration, Kreiss table, figures |

## 3. Data sources and terms
- Binance public archive, https://data.binance.vision (USD-M futures klines, bookDepth, metrics; spot 1-second klines). Files are verified against Binance's published SHA-256 checksums.
- Bybit public trade archive, https://public.bybit.com, and Bybit historical order-book files (https://www.bybit.com/derivatives/en/history-data).
- CFTC public reporting API (Traders in Financial Futures and Disaggregated reports), https://publicreporting.cftc.gov.
- Yahoo Finance daily closes via `yfinance` (Part 11 prices other than BTC and ETH).
- Alpaca market-data API (consolidated SIP trades for US stocks; free account), Part 14.

Raw data are not redistributed; the notebooks download them. Download manifests with SHA-256 hashes of every file
are written to `results/*_manifest_sha256.csv`.

## 4. Determinism
Every notebook fixes its random seed (`SEED` in cell 0). Bootstrap draws, symbol draws and simulations are therefore
reproducible given the same downloaded files.
