# P1T amendment A1: T86 schema eras (7 November 2026, before any statistic)

**Status.** This is a parse-layer bug fix inside the validation pass. Spec §2 allows the validation pass to "fix bugs,
not change the hypothesis or criteria". The hypothesis, statistic, criteria, periods, universe rule, seed, bootstrap
and D* are unchanged. `P1T_taiwan_spec.md` itself is not edited; this file is the amendment, with its own checksum
in `P1T_SHA256SUMS`.

## What happened

- **First attempt.** The validation notebook downloaded all 1,475 trading days of 2013-01-02 to 2018-12-28 (TWSE T86
  and MI_INDEX, stored on the author's Drive with SHA-256). It then stopped at the first parsing call.
  `parse_t86` raised `ValueError: '外陸資買賣超股數(不含外資自營商)' is not in list` on 2013-01-02.
- **Nothing was computed.** The crash came before the panel was built. No forecast, statistic, bootstrap or verdict
  exists from that attempt, so the validation counter in `P1T_unlocks.json` stays at 0. The attempt is logged there.
- **Cause.** The spec's class definitions (§10.4) were written from the schema probes, which looked at recent days
  only. A census of the column names of every stored response found three T86 schemas. It read field names only, no
  values (`schema_census.json` on Drive; printout kept with the session). MI_INDEX has one schema throughout.

| Era | Dates | Trading days | Foreign columns | Dealer columns |
|---|---|---|---|---|
| E1 | 2013-01-02 – 2014-11-28 | 470 | `外資買賣超股數` | `自營商買賣超股數` only |
| E2 | 2014-12-01 – 2017-12-15 | 748 | `外資買賣超股數` | total, `(自行買賣)`, `(避險)` |
| E3 | 2017-12-18 – 2018-12-28 | 257 | `外陸資買賣超股數(不含外資自營商)` + `外資自營商買賣超股數` | total, `(自行買賣)`, `(避險)` |

All eras also report `投信買賣超股數` and `三大法人買賣超股數`.

## Mapping (replaces the field list of spec §10.4; the class definitions in §3 are unchanged)

- **Foreign (including foreign dealers).**
  - E1–E2: `外資買賣超股數`, the reported foreign total. Its E3 successor is split into the two parts below.
  - E3: `外陸資買賣超股數(不含外資自營商)` + `外資自營商買賣超股數`, as in the spec.
  - That the E1–E2 total contains the foreign dealers is an assumption about TWSE's reporting, stated here and
    checked indirectly by the accounting diagnostics below.
- **Investment trusts.** `投信買賣超股數` in all eras.
- **Dealers' own account.** `自營商買賣超股數(自行買賣)` in E2–E3. **NaN in E1** for every stock (not zero): the
  series does not exist.
- **Hedging control.** `自營商買賣超股數(避險)` in E2–E3. NaN in E1.
- **Residual.** Minus (Foreign + Investment trusts + `自營商買賣超股數`). The dealer total equals own + hedging
  wherever both are reported; the diagnostics check this, and the total exists in every era. So this is the spec's
  "minus the sum of all reported net series".
- **Missing versus zero.** A stock that traded but is absent from a day's T86 table has zero institutional flow, as
  before. A series that the day's schema lacks is NaN.
- **Unknown schemas.** A schema lacking the foreign, trust or dealer total stops the run.

## Consequences, stated before any result

- **Primary test (Foreign): no change in definition.** Foreign exists in every era. In the validation pass its
  forecasts are fitted on all 982 development days.
- **Holdout.** The holdout fit window is the trailing 1,000 days before 2019-01-02, which starts 2014-12-08 (day 476).
  It lies entirely in E2–E3, so the holdout never uses E1 flows. The holdout download (2019–2023) will repeat the
  schema census before parsing. An unknown schema stops the run.
- **S1 (Dealers' own account) in the validation pass.** It is fitted on the 512 development days from 2014-12-01,
  because E1 does not report the class. The holdout S1 is unaffected.
- **Reverse-causality diagnostic and the hedging sensitivity.** In the validation pass they use E2–E3 days only.
- **Executor guard.** `stock_losses` now also requires finite flows at t−1, t and t+1 for an origin to be used. For
  Foreign this is a no-op, as the simulation validation shows (below).

## Diagnostics recorded with the validation run (flow-only; no prices, no forecasts)

`t86_diagnostics` reports four quantities per era:
- the share of stock-days on which `三大法人買賣超股數` equals the sum of the parts, with and without the foreign
  dealers;
- the share on which the dealer total equals own + hedging;
- in E3, the foreign dealers' share of absolute foreign net flow.

These are reported whatever they show. If E3's total excludes the foreign dealers while E1–E2's includes everything
in `外資買賣超股數`, that is evidence about the E1–E2 definition, and it is reported as such.

## Validation of the amended executor (before the rerun)

- `validate_executor.py`, rewritten to simulate the three eras with the census column lists verbatim. Schema checks
  pass. The verdicts are unchanged and identical to the original validation to every digit (D = −0.00078, −0.00098
  and −0.00151 under w = 0, all "inconsistent"; D = 0.0107, 0.0113 and 0.0099 under w = 0.1, all "supportive"). So
  Foreign is unaffected by the amendment.
- `validate_executor_A1_extra.py`. A class absent in E1 (dealers' own account) is NaN on every E1 day and on no later
  day. It runs end to end with fitting on reported days only, and its verdict on a no-feedback flow is not
  supportive. Foreign is supportive in the same simulation. Passed.

## Executor

- Previous: commit d4a6579, sha256 `4de3baa9145ced50713a2c1eedc2890275aad6d05c37f7e6c8f89cfd4eb06c09`.
- Amended: sha256 `da44075ed9da3a240a792f74777b50404b96401e90e1075e5433e6613e7d7fa0`. The commit is recorded in
  `P1T_unlocks.json`.
- Notebook: `P1T_Validation_A1_Colab.ipynb`. It is the same download code, which resumes from Drive and fetches
  nothing new, plus the amended executor, its checksum assertion and the diagnostics.
