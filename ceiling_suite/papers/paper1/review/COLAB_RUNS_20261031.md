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
