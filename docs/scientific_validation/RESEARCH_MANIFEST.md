# Machine Markets (107p) — Research Provenance & Artifact Manifest

## 1. Baseline 107-Page Manuscript Provenance
- **Supplied 107p PDF:** `.codex-research/Machine_Markets_JF_Submission(20261014-043429).pdf`
  - **SHA-256:** `fafb4c9e5dab117cfb111e07f5367831e57f366949750adc3881ec7916ed1ce9e`
  - **Exact Git Commit Match:** `4017dc3722edd1a154d871866dd7567be1c7558f:paper/Machine_Markets_JF_Submission.pdf` (byte-for-byte identical).
- **GitHub Actions Run `38512199252` Root-Cause Diagnosis:**
  - Inspected via `gh run view 38512199252`: all 4 jobs (`verify (3.11)`, `verify (3.12)`, `lean4-formal-verification`, `latex-manuscript-build`) failed in `0s` prior to container provisioning with runner error:
    > `"The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings."`
  - This is a GitHub account billing/runner quota block, not a code, Lean, or LaTeX build failure.

## 2. Authenticated Empirical Datasets & Checksums
1. **January 9–20, 2023 Binance BTCUSDT L2 Order-Book & Trade Archive:**
   - File: `empirical_pipeline/data/1-09-1-20.csv` (10 bid/ask price and volume levels `bid_p0..9`, `bid_v0..9`, `ask_p0..9`, `ask_v0..9`).
2. **Historical Crisis 1-Second Spot BTCUSDT Archives (`data.binance.vision`, Official `.CHECKSUM` Verified):**
   - `BTCUSDT-1s-2021-05-19.zip`: SHA-256 `463ffba71b8fc0edab9dc21cd36ffbe1d9cc22ac3f8de931cc54965b357900ba` (`86,400` 1s bars, `-31.17%` intraday drop).
   - `BTCUSDT-1s-2022-05-09.zip`: SHA-256 `c4b1ff6ca639923d4ac24833e1fa992978fc6422ddac367761314ed2c33a8da7` (`86,400` 1s bars, `-12.29%` intraday drop).
   - `BTCUSDT-1s-2022-11-08.zip`: SHA-256 `2afac51bd35e5aa8bd45bc0c2da4c3a326fa0ab9a3da8558cf12203aecc5c61b` (`86,400` 1s bars, `-17.07%` intraday drop).
   - `BTCUSDT-1s-2023-03-11.zip`: SHA-256 `53392e95edde0b0cf4e3336e8238fe935e81f70a99fd92b1aa4cf4fa9d52eb35` (`86,400` 1s bars, `-4.45%` intraday drop).
3. **Synchronized 8-Asset 1-Second Crisis Panel (`2022-11-08`, `data.binance.vision`, Official `.CHECKSUM` Verified):**
   - `BTCUSDT`: `2afac51bd35e5aa8bd45bc0c2da4c3a326fa0ab9a3da8558cf12203aecc5c61b`
   - `ETHUSDT`: `285051f1030be33fbce8042c72e4bbcb336381b25caae7c29f950f19403ca58f`
   - `SOLUSDT`: `bb6ba8c8e27319b0b880cf3ebdc94270cd3c8c028379595e5554a24f4d21dc3d`
   - `ADAUSDT`: `595d6280d7e4234389897beae75405f97e29a7606dc628981fa148e7b1fd90a0`
   - `DOGEUSDT`: `2bf7f72bb69f9045aa197fbeb1f542516ec308a4fffe5b806eb065023df8a7e0`
   - `BNBUSDT`: `c33102967f5ff26e81d7dd27370c70cb0c92c17025f6d1bb12d543fb3e2cb8bf`
   - `XRPUSDT`: `bb4d06d4bd422a2a87ff9e32c9bb5b092b4628d5249cb83c02fa849d4601b6fd`
   - `LTCUSDT`: `68b07b80982297e3f16d474db71bf1607e191dcfe7676214176898d4ef353bd6`

## 3. Remediated Code, JSON Results, and LaTeX Tables
- `scripts/independent_checks/independent_model_and_counterexamples.py` -> `scripts/independent_checks/independent_oracle_receipt.json`
- `breakthrough_experiments/exp13_account_capital.py` -> `breakthrough_experiments/results_exp13_account_capital.json`, `breakthrough_experiments/tables/table_account_capital.tex`
- `breakthrough_experiments/exp16_nonconvex_duality_closing.py` -> `breakthrough_experiments/results_exp16_nonconvex_duality.json`, `breakthrough_experiments/tables/table_nonconvex_duality.tex`
- `breakthrough_experiments/exp17_minimax_lecam_bound.py` -> `breakthrough_experiments/results_exp17_minimax_lecam.json`, `breakthrough_experiments/tables/table_minimax_lecam.tex`
- `breakthrough_experiments/exp18_crash_free_ai_guard.py` -> `breakthrough_experiments/results_exp18_crash_free_ai_guard.json`, `breakthrough_experiments/tables/table_crash_free_ai_guard.tex`
- `breakthrough_experiments/exp19_historical_crash_replay.py` -> `breakthrough_experiments/results_exp19_historical_crash_replay.json`, `breakthrough_experiments/tables/table_historical_crash_replay.tex`
- `breakthrough_experiments/exp21_empirical_multi_asset_kreiss_network.py` -> `breakthrough_experiments/results_exp21_empirical_multi_asset_kreiss.json`, `breakthrough_experiments/tables/table_empirical_multi_asset_kreiss.tex`
- `breakthrough_experiments/generate_all_breakthrough_figures.py` -> `paper/figures/fig1..fig7.pdf`
