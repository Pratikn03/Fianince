# Observation design for a direct Taiwan test (draft, 7 November 2026; needs author approval)

This document resolves the five open items in `DATA_DICTIONARY.md`.
- Items 1 and 4 are factual questions about the data. The design rules are fixed below, and the second schema probe
  (`P1_Schema_Probe2_Colab.ipynb`, same burned days only) checks the facts they rest on.
- Items 2, 3 and 5 are design choices. They are fixed here so they cannot be tuned after seeing outcomes.

Nothing here has been run on test data.

## 1. Missing versus zero

The security-day universe comes from the daily price file, not from the institutional-flow file.

| Price file | Flow file | Treatment |
|---|---|---|
| Traded, volume > 0 | Present | Use the reported flows |
| Traded, volume > 0 | Absent | All institutional flows are zero |
| Not traded or suspended | Any | Missing; the day is excluded for that security |

- The "absent means zero" rule is an assumption. Probe 2 checks it on the burned days by testing whether securities
  absent from T86 but traded have low volume and no reported institutional activity in other TWSE tables. If the
  check fails, those days are treated as missing instead.
- A security is dropped from a window if more than 5% of its trading days are missing.

## 2. Hedging trades

Classes (i = 1, …, 4):

1. Foreign: foreign and mainland investors plus foreign dealers. Foreign-dealer flow is almost always zero, and the
   split depends on registration rather than behaviour.
2. Investment trusts: domestic funds.
3. Dealers' own-account trading.
4. Residual: domestic individuals and other domestic institutions, implied by market clearing as
   minus the sum of all reported institutional net flow, hedging included.

- Dealer hedging flow is not a class. It enters only as an exogenous control series and in the market-clearing
  identity. It is mechanical (it offsets warrant and derivative books), so it is not a price-responsive learning
  rule.
- Robustness check, declared now: put hedging into the dealer class.

## 3. Universe

- Four-digit common-stock codes only. This excludes ETFs (codes starting `00`), leveraged and inverse ETFs (`L`, `R`),
  foreign-currency ETFs (`K`, `M`, `S`, `C`), warrants, TDRs and preferred shares.
- Exclude the first 60 trading days after listing.
- Exclude ex-dividend and ex-rights days and the following day, from the TWSE/TPEx ex-rights calculation tables.
- Exclude full-day suspensions and the five days after any suspension of at least five days.
- Liquidity filter: trading on at least 95% of days and in the top 300 by average daily turnover. This is computed on
  the development period only and then frozen.
- TWSE (main board) is the primary universe. TPEx (OTC) is the replication universe.

## 4. Prices and the ±10% limit

- Prices are daily closes from the TWSE all-securities quote table, which probe 2 inspects. Returns are close-to-close
  log returns, with event days removed under item 3.
- A limit day is one with |close change| ≥ 9.5% of the previous close.
  - Primary analysis: limit days stay in, with an indicator in every regression.
  - Declared robustness check: drop limit days and the following day.
  - The share of limit days is reported.
- The TAIEX daily close, from the same quote table or the index table, is the market reference.

## 5. Model link

### Period

One trading day.
- Justification: flows are published only daily, and each day is one complete auction-plus-continuous session.
- The memory rates are therefore daily rates.
- Declared robustness check: aggregate to two-day and five-day periods. The theory predicts the rates compound
  (r ↦ r^k). That is a checkable implication, not an assumption.

### Flow variable

u_{i,t} = net shares of class i on day t divided by the security's average daily volume over the development period.
- The scale is fixed per security before testing, so the price-impact coefficient κ is comparable across securities.
- This scaling is chosen because Proposition 6.1 is linear in flow, so a fixed per-security scale changes κ only.
- Declared robustness check: net value divided by market capitalization.

### Pricing error

x_t = log P_t − β̂ log I_t − m_t.
- I_t is TAIEX.
- β̂ is estimated on development data only.
- m_t is the trailing 60-day mean of the first two terms, so no future observation enters x_t.

This is a market-reference basis, not the model's fundamental pricing error. The paper must use that label. Its
measurement error relative to the model's x_t is not known, and it is the main threat to a direct interpretation.

## What this design does not settle

- Whether real investor classes follow one homogeneous exponential-memory rule. Taiwan's classes are legal
  categories, so each is a mixture of strategies. The class-aggregation results of the paper apply, and the test can
  only check the merged class response.
- Whether the market-reference basis behaves like the model's x_t. Diagnostics will check autocorrelation and
  stability, and the paper will report them.

## Next step

1. The author runs probe 2.
2. I update items 1 and 4 with the facts.
3. I write the frozen primary-test specification: question, target, estimators, intervals, dependence handling,
   pass/fail/inconclusive criteria, and period split from a simulation power analysis.
4. The author approves it before any test-period data are downloaded.
