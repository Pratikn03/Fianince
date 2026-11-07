# Paper 1 empirical ledger (Phase 1 of the empirical plan, 7 November 2026)

This ledger lists all 23 recorded outcomes in `tab:scorecard` of `papers/paper1/paper1.tex`. The table, not earlier
summaries, is the count of record: 11 passed or held, 11 failed, 1 not supported. Among the 19 primary outcomes,
9 passed and 10 failed. An earlier chat summary said "22 tests, 11 passed, 10 failed"; that was stale.

## Theorem-connection codes

- **D** (direct): the observed variable is the variable in a theorem.
- **B** (bridge): the test is direct only if a stated observation bridge holds, for example weekly position changes
  standing in for executed class flow.
- **P** (proxy): the test checks an implication or analogue of the model on a different observable.
- **S** (semi-synthetic): synthetic groups with real noise. It tests the implementation and the rate, not real
  traders.

## Reproduction status

Column R records reproduction status.
- **not reproduced**: only the saved results file is in the repository, so the number has not been rebuilt from raw
  inputs in this session.
- **raw in repo**: the raw inputs are also present.

No outcome below has been rebuilt from raw inputs yet. Raw market data are not stored in the repository, and this
workspace cannot reach the exchanges. Reproduction therefore requires a Colab run by the author.

| ID | Observation | Conn. | Prediction tested | Recorded result | Specification / unlock | Selection history | R |
|---|---|---|---|---|---|---|---|
| E1 | CFTC COT positions, 8 markets | P | class positions pin down persistence prices leave open | Pass 8/8 | `p11res/prereg/P11_cot.json` | registered before data | not reproduced |
| E2 | same | P | designated class trend-follows | Fail 4/8 | same | registered | not reproduced |
| E3 | same | P | that class has less persistent positions | Pass 6/8 | same | registered | not reproduced |
| E4 | CFTC weekly position changes | B | class flows pin down their persistence | Fail 3/8 (6 req.) | `p11res/prereg/P11F_unlocks.json`, `p11/prereg_flow/P11F_cot_tagged_flow.json` | registered after E1–E3 results | not reproduced |
| E5 | CFTC positions, two-root model | P | second, faster memory root | Fail 2/8 (6 req.) | `p11/prereg_memory/P11M_two_root.json` | registered after E1–E4 | not reproduced |
| E6 | real BTC noise, synthetic K=2 groups | S | price-only requirement ∝ (Δη)^−6; tagged bounded | Pass, slope −6.01 | `p1_injection/prereg/P1_injection.json` | registered | not reproduced |
| E7 | same, K=3 (secondary) | S | slope −10 | Holds, −9.81 | same | registered | not reproduced |
| E8 | Binance top-trader positions, 30 markets | P | class data restrict persistence; price-only wide | Pass 30/30 | thesis `C2`/`C3` family (to verify which file) | to verify | not reproduced |
| E9 | same | P | prices pin down combined response | Fail 5/30 | same | to verify | not reproduced |
| E10 | Binance, 30 new markets, horizon-matched | P | class interval narrower | Pass 29/29 | `thesis/checks/prereg/C2_margin_vs_identify.json` | registered | not reproduced |
| E11 | same, secondary | P | class persistence is a stable memory | Not supported | same | registered | not reproduced |
| E12 | Binance, 105-day follow-up | P | combined response cheaper than separate rates | Fail 10/30 (23 req.) | `thesis/checks/prereg/E1v2_certify_vs_identify.json` | registered follow-up | not reproduced |
| E13 | Binance, 58-day follow-up, P2 | P | tagging advantage grows with sample | Pass 22/29 (22 req.) | `thesis/checks/prereg/D1_tagging_scaling.json` | registered | not reproduced |
| E14 | same, P1 | P | tagged interval shrinks at parametric rate | Fail 20/29 (22 req.) | same | registered | not reproduced |
| E15 | Binance, return forecasts | P | class memory states improve 30-min return forecasts | Fail (inconclusive) | to verify | to verify | not reproduced |
| E16 | Binance, state tracking | P | class data track class positions better | Pass, explained by target persistence | to verify | to verify | not reproduced |
| E17 | CFTC, 12 new markets (replication of E1) | P | as E1 | Pass 12/12 | `p11/prereg_replication/P11R_cot_replication.json` | registered | result JSON in Drive only |
| E18 | same, as E2 | P | trend-follows | Pass 11/12 | same | registered | same |
| E19 | same, as E3 | P | less persistent | Fail 3/12 | same | registered | same |
| E20 | Binance Oct 2026, N2 | P | prices forecast top-trader position beyond its persistence | Fail 1/30 | `p1_oct/prereg/P1O_october2026.json` (SHA 72cbc8ba…) | registered | results zip in repo |
| E21 | same, N3 | P | aggregate taker flow pins down combined response | Fail 5/30 | same | registered | same |
| E22 | same, N3 secondary | P | sign stable within month | Fail 21/30 | same | registered | same |
| E23 | same, N3 secondary | P | interval shrinks at root-T | Pass 30/30, median ratio 1.69 vs 1.73 | same | registered | same |

## Findings of the audit

1. **No outcome is a direct (D) test of a Paper 1 theorem.**
   - Every CFTC test uses positions.
   - Every Binance test uses top-trader account ratios or aggregate taker flow. These are not executed flow tagged by
     trader class.
   - E6–E7 are semi-synthetic.

   This is the main empirical gap.
2. **E23 should not be promoted.**
   - The 1.69 vs 1.73 agreement checks root-T shrinkage: an interval from three times the data should be √3 ≈ 1.73
     times narrower. Any regular estimator does this, so it is not evidence for the feedback model.
   - Its 30 markets are on one venue in one month, so they share shocks and are not 30 independent replications.
   - It stays in the table as a secondary outcome only.
3. **Independence.** E8–E16 and E20–E23 use the same Binance perpetuals universe and overlapping periods. Counts out
   of 30 should be read as one venue, not as 30 replications.
4. **Housekeeping.** Several rows are marked "to verify" for their specification file. Each must be matched to its
   specification and unlock file before the next manuscript revision.
5. **Outstanding copy.** The byte-exact `C6R_cot_replication.json` (E17–E19) still has to be committed from Drive.

## What this means for new data

- A direct test needs instrument-level signed flow by investor class: TWSE/TPEx three-institution daily flows, or
  KRX investor-type flows.
- Those sources still need an observation bridge before any test counts as direct:
  - daily net flow to the model's per-period flow;
  - a reference price to the pricing error x_t.
- No new test may be run until its specification is frozen and the author approves it.

The schema probe in `SCHEMA_PROBE.md` looks only at field layouts on two declared days. It is not a test, and those
days are excluded from every future confirmatory sample.

## Empirical runs still missing (7 November 2026)

1. **P1T validation, then holdout.** The validation run is in progress in the author's Colab. The holdout is opened
   once, after validation is checked and any bug fixes are logged. This is the first direct test on tagged flow.
2. **P1T replication on TPEx.** A separate registered specification with the same frozen procedure on the OTC
   market. It must be registered before the TPEx test data are requested.
3. **Calibrated cost illustration for Taiwan.**
   - Fit (a, κ, r_i, w_i) on development data.
   - Report the sample, quantity and capital requirements for price-only versus tagged observation.
   - Carry the fitted parameters' uncertainty through.
   - Label it a model-based illustration, with lower bounds labelled as lower bounds.
4. **Independent reproduction of the Binance results E10 and E23.** This is a labelled check, and the recorded
   outcomes do not change. It needs the author's ruling on reruns.
5. **S3 of P1T.** The formula-based standard error of r̂_F against the holdout bootstrap standard error. This is the
   paper's quantitative holdout prediction and comes with the holdout run.
