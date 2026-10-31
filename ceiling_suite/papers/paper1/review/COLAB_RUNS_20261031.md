# Paper 1: Colab runs approved on 30 October 2026

All three are committed to GitHub **before** any of them is run. Run each **once**, in its own Colab session, and send
back the result file from your Google Drive folder `ceiling_suite/results/`. Every run writes an unlock counter; if a
run crashes before it finishes, tell me before running it again (a crash before results is recorded, not hidden).

| Run | What it answers | Kind | Time (CPU runtime) | Send back |
|---|---|---|---|---|
| A. `p11/robustness_cot.py` | Does the CFTC result change with CME futures prices, without contract-roll weeks, or with 26/52-week bootstrap blocks? | Post hoc robustness (reported next to the registered result, never re-scoring it) | about 30-60 min | `C4R_cot_robustness.json` |
| B. `p1_injection/injection_test.py` | Do the theory's rates survive real market noise? Price-only requirement should scale as (Delta eta)^-6 (K = 2) and (Delta eta)^-10 (K = 3); the tagged requirement should stay bounded | Pre-specified test (spec SHA-256 `596a700d...`) | about 10-20 min | `I1_injection_test.json` |
| C. `p11/tagged_flow_test.py` | Read as flows (weekly changes in class positions), do the CFTC reports identify each class's response with root-T precision, as Proposition 6.1 predicts? | Pre-specified test (spec SHA-256 `052a63f2...`) | about 10-20 min | `C5F_cot_tagged_flow.json` |

## How to run each (same steps)

1. Open https://colab.research.google.com, **New notebook**. CPU runtime is enough.
2. In the first cell:
   ```
   !git clone https://github.com/Pratikn03/Fianince.git
   ```
3. Second cell, one of:
   ```
   %cd Fianince/ceiling_suite/p11
   %run robustness_cot.py
   ```
   ```
   %cd Fianince/ceiling_suite/p1_injection
   %run injection_test.py
   ```
   ```
   %cd Fianince/ceiling_suite/p11
   %run tagged_flow_test.py
   ```
4. Allow Google Drive access when asked (results are saved there).
5. When it prints its summary, download the result file from `My Drive/ceiling_suite/results/` and send it to me,
   together with the unlock file from `My Drive/ceiling_suite/prereg/` (`P1_injection_unlocks.json`,
   `P11F_unlocks.json`; run A has none because it is not a test).

## What I will do with the results

* A: one robustness paragraph and a table note in Section 6.3; the registered 8/8, 4/8, 6/8 stay the headline.
* B: a short subsection in the main paper ("Do the rates survive real noise?") and a supplement table, pass or fail.
* C: a row in the pass/fail table and a paragraph in Section 6.3, pass or fail.
* Then one more professor-review round on the final build.

## Notes

* B uses real Binance one-minute price changes on the 6th of each month (Jan 2025 - Sep 2026), dates not used
  anywhere else in the project; the cohorts are synthetic with known spacing, so only the noise is real.
* B's noise level and spacing grid were calibrated on synthetic Gaussian noise only, before any real data; its code
  was dry-run on synthetic Student-t noise. A and C were dry-run on fake data with the network switched off.
* If Colab cannot reach Yahoo Finance, the CFTC API or the Binance archive, the scripts stop with a message;
  send me the message.

## Results (returned 31 October 2026, each run opened once)

Console output: `colab_console_20261031.txt` (verbatim). The five result and unlock files are in the author's Google Drive (`My Drive/ceiling_suite/results/` and `.../prereg/`); I1 and C5F were read through the Drive connector on 2026-10-31 and match the console output; both unlock files read n = 1. Byte-exact copies still to be committed.

| Run | Outcome | In the paper |
|---|---|---|
| A. Robustness | Futures prices: H1 8/8, H2 4/8, H3 6/8, every sign of w_fast unchanged (the basis does not make the negative signs). 26/52-week blocks: counts unchanged; Bitcoin's w interval includes zero. Roll weeks removed: H1 8, H2 4, **H3 4 of 8**, Treasury w turns negative. | Section 6.3 paragraph "Post hoc robustness"; tab:cot note |
| B. Real-noise injection | **PASS.** K=2 price slope -6.01 (band [-7.5,-4.5]); tagged N* 256-724, max/min 2.83 (<= 8); K=3 slope -9.81 (band [-12.5,-7.5]). Real/Gaussian within one grid step everywhere. Limit: N* > 4096 uses the CLT draw (tails not kept); all tagged points and the first three K=2 price points are exact. The JSON shows the real windows are almost uncorrelated (lag-1 autocorrelation -0.007 to 0.009), so above 4096 the real arm is close to Gaussian by construction; the paper now says the direct heavy-tail evidence is the exact-range points only. | New main subsection sec:injection, tab:injection; Supplement tab:injectionfull; scorecard rows; abstract; introduction |
| C. CFTC tagged flow | **FAIL** (H1 3 of 8; 6 required). H2 first-stage F >= 10 in 7 of 8 (pass); H3 w excludes zero in 6 of 8 (pass), same signs as positions. | Section 6.3 paragraph "Class flows: a pre-specified test that failed"; scorecard row; abstract; introduction |
