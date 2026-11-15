# P1R: TPEx replication of P1T (DRAFT, not registered)

- **Status.** DRAFT for the author's approval. Nothing is registered and no TPEx data in the sample periods have
  been requested.
- **Registration needs three things:**
  1. the author's explicit approval of this text;
  2. probe 4 (`P1_Schema_Probe4_TPEx_Colab.ipynb`, burned days only), which must name an index source and an
     ex-rights source;
  3. the resolution of the open choices in §8.
- **Purpose.** To ask the same single question as P1T on a second, independent market: the TPEx (OTC) common stocks.
  A replication is informative only if it is frozen before its data are seen, so this draft copies P1T and its
  amendment A1 wherever possible and flags every difference.

## 1. Question (as P1T §1)

Does the Foreign class's own tagged daily flow respond to the price deviation, measured as the out-of-sample
next-day forecast gain from the market-reference basis beyond two own lags?

## 2. Data and periods (as P1T §2)

| Period | Dates | Use |
|---|---|---|
| Development | 2013-01-02 to 2016-12-30 | Universe filter, scale constants, β̂; free exploration |
| Validation | 2017-01-03 to 2018-12-28 | One pass end to end; may fix bugs, not change the hypothesis or criteria |
| Holdout | 2019-01-02 to 2023-12-29 | Opened once |
| Reserved | 2024-01-01 onward | Not used; contains the burned TPEx days 2024-01-02, 2024-01-03 and 2026-11-06 |

Holdout fit window: as in P1T, the trailing 1,000 trading days before 2019-01-02.

## 3. Sources

- **Institutional flows.** `www/zh-tw/insti/dailyTrade?type=Daily&sect=EW&date=YYYY/MM/DD&response=json`. It
  honours the date (probe 3), and its 24-column layout and group identities are confirmed (probe 1).
- **Quotes.** `www/zh-tw/afterTrading/otc?date=YYYY/MM/DD&type=EW&response=json`. It honours the date (probe 3).
- **Market reference.** The TPEx index (櫃買指數). **Source open:** probe 4 must find a daily series that honours
  the date.
- **Corporate events.** **Source open:** probe 4 must find an ex-rights/ex-dividend table. If none is found, events
  are taken as days with |return| > 9.5% where the next-day reference price differs from the close. That is a
  weaker rule, and it would be stated as a deviation from P1T.
- **Request integrity.** As P1T §10.8: every response is checked against the requested date, a mismatch stops the
  run, and raw responses are stored with SHA-256.
- **Schema eras.** As amendment A1, before any parsing:
  - a census of field names over all stored responses;
  - every class is mapped by its economic definition;
  - a series that an era does not report is NaN, never zero;
  - an unknown schema stops the run.

## 4. Variables (as P1T §3 and §10, with these differences)

- **Classes from the flow columns.**
  - Foreign = foreign total including foreign dealers (columns 8–10 in the current layout).
  - Investment trusts.
  - Dealers' own account.
  - Hedging control.
  - Residual = minus the three-institution total.
- **Flow scaling.** Development-period average daily volume.
- **x_t.** As P1T, with the TPEx index in place of TAIEX.
- **Limit days.** |close change| ≥ 9.5% of the previous close, as P1T. The TPEx limit is also ±10%.
- **Universe.** Four-digit common stocks, with the event, listing and suspension exclusions as P1T, trading on ≥ 95%
  of development days. TPEx is less liquid than TWSE. See §8 for the cutoff.

## 5. Estimator, statistic, uncertainty and criteria

These are identical to P1T §4–§6:
- the forecasting models M0 and M1;
- d_s and D;
- the stationary date-block bootstrap, with mean block 20, B = 9,999 and seed 20261107;
- D* = 0.0035;
- the same three-way verdict.

The executor is the P1T executor with a TPEx parse layer. It is validated on simulated TPEx-format responses
before the validation download, and frozen with its SHA-256 recorded in `P1R_unlocks.json`.

## 6. Diagnostics and secondary outcomes

As P1T §7–§8: the reverse-causality check, the per-stock share, stability by year, sensitivity, and S1–S3 with Holm
adjustment.

## 7. How the result is read together with P1T

- The two venues are reported side by side. There is no pooled test, and neither result is reinterpreted in the
  light of the other.
- If P1T is supportive and P1R is not, the paper says the feedback channel replicated on one of two venues.

## 8. Open choices for the author (before registration)

1. **Universe size.** Top 300 by development turnover (as P1T) if at least 300 stocks are eligible, otherwise all
   eligible. Alternative: top 200, to keep the sample liquid. Recommendation: top 200. The power analysis used
   N_eff, and the effective sample is set by cross-sectional dependence, not by the count, so 200 loses little.
2. **Event rule if probe 4 finds no ex-rights table.** Recommendation: the fallback rule in §3, labelled as a
   deviation.
3. **Timing.** Recommendation: register P1R only after the P1T validation pass is checked, so that any bug fix
   found there is inherited by P1R before its data are requested.
