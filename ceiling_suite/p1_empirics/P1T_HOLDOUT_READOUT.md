# P1T holdout: readout fixed before the holdout is opened

- **Written:** 8 November 2026 (UTC). The holdout unlock counter is 0 (`P1T_unlocks.json`), and no holdout file has been
  requested.
- **Purpose:** to fix, before any holdout number exists, what the paper will say for each possible outcome. Once the
  holdout is open, this file is not edited. The SHA-256 of this file is recorded in `P1T_unlocks.json` when it is
  committed.
- **Basis:** spec `P1T_taiwan_spec.md` (§6 criteria, §7 diagnostics, §8 secondary outcomes), amendment A1 (parser),
  amendment A2 (diagnostics and their known limits).
- **Not changed by this file:** the hypothesis, the statistic, the criteria and the executor. This file only commits
  the wording.

## 1. Binding rules

1. **The verdict.**
   - The verdict is spec §6 applied to the holdout primary: Foreign, D, B = 9,999, mean block 20, seed 20261107.
   - Nothing else changes the verdict: not the diagnostics, not the secondary outcomes, and not the validation pass.
2. **The validation pass.**
   - The validation pass (D = 0.0405, 95% interval [0.0226, 0.0542]) is described only as "the validation pass of the
     pipeline".
   - It is never cited as evidence for the hypothesis, and never pooled with the holdout.
3. **Where the result appears.**
   - The primary verdict appears in the abstract, in the empirical section and in "What we do not claim", whatever it
     is.
   - An unfavourable result is not moved to the supplement.
4. **Diagnostics and secondary outcomes.**
   - Every diagnostic in spec §7 and every secondary outcome in spec §8 is reported in one table, whatever the
     primary.
   - The table includes: reverse causality; per-stock share; each calendar year and COVID; each sensitivity; S1 with
     Holm; S2; S3.
   - "Market-cap scaling: not computable from the registered sources" is reported as such (A2, item 3).
5. **Failures.**
   - *Before any statistic is computed* (download, parsing, a date mismatch): this is a bug. The fix is a written
     amendment with simulation validation, as for A1, and the counter is unchanged.
   - *After the primary D is computed:* that D is the result. It is not recomputed with changed code, data or
     settings.
   - A later error found in the executor is reported next to the original number. The original number is not
     replaced.
6. **Robustness block lengths 10 and 60.** These are reported. If they disagree with block length 20, both are
   shown. The verdict stays the one at 20.
7. **Burned days.** The holdout (2019-01-02 to 2023-12-29) contains no burned day. The notebook asserts that no date
   at or after 2024-01-01 is requested.

## 2. How the reverse-causality check is read (spec §7.1, amendment A2)

| Check outcome | What it means | What it does not mean |
|---|---|---|
| Gain survives (residualized D supportive by the §6 rule) | The gain is not explained by the price level standing in for flow lags that the forecasting model omits (A2 case d). | It does not rule out prices revealing true flow better than noisy *reported* flow (A2 case c). That channel needs misattributed foreign flow of roughly the size of the flow itself. |
| Gain disappears (residualized D not supportive) | The primary gain is consistent with prices revealing past flow. It is not evidence of feedback beyond that channel. | It does not show that w_F = 0. The check removes some genuine feedback signal as well (A2 case a: D fell from 0.010–0.013 to 0.005–0.008 in simulation). |

## 3. The four readings, and the exact text for each

Placeholders: `{D}`, `{lo}`, `{hi}`, `{p}` (primary, Foreign); `{Dr}`, `{lor}`, `{hir}` (reverse-causality check);
`{n}` (stocks); `{share}` (share of stocks with d_s > 0). Numbers are rounded to 4 decimals, p-values to 3.

### A. Primary supportive, check survives

- **Abstract:** "In a pre-registered out-of-sample test on Taiwan's tagged exchange flows (2019–2023), foreign
  investors' daily flow responds to the price deviation as the model's flow equation requires, and the response is
  not explained by prices standing in for past reported flow."
- **Empirical section:** "The registered primary statistic is D = {D} (95% interval [{lo}, {hi}], one-sided p = {p},
  {n} stocks, {share} with a positive gain). It meets the registered supportive criterion. With the price deviation
  replaced by its residual on lagged reported flows, D = {Dr} [{lor}, {hir}]. One alternative remains: prices may
  reveal true flow better than the reported flow does. That would require foreign flow to be misattributed between
  account types by roughly the size of the flow itself. Exchange accounting identities cannot detect this, so we do
  not rule it out."
- **What we do not claim:** "The Taiwan test supports the feedback premise (w_F ≠ 0) on tagged flow. It does not test
  the identification theorem, which is a mathematical result, and it does not estimate the structural parameters."

### B. Primary supportive, check does not survive

- **Abstract:** "In a pre-registered out-of-sample test on Taiwan's tagged exchange flows (2019–2023), prices improve
  forecasts of foreign investors' flow as the registered criterion requires, but a pre-specified check attributes the
  gain to prices revealing past flow rather than to feedback."
- **Empirical section:** "D = {D} [{lo}, {hi}], p = {p}, meets the registered supportive criterion. The pre-specified
  reverse-causality check gives D = {Dr} [{lor}, {hir}], which does not meet it. The registered verdict is
  'supportive'. Read with its pre-specified diagnostic, the test does not provide evidence of feedback beyond prices
  revealing past flow."
- **What we do not claim:** "We do not claim that tagged flow in Taiwan responds to price deviations. The registered
  test is supportive, but its pre-specified diagnostic attributes the gain to reverse causality."

### C. Primary inconclusive

- **Abstract:** "A pre-registered out-of-sample test on Taiwan's tagged exchange flows (2019–2023) is inconclusive about
  whether foreign investors' flow responds to price deviations."
- **Empirical section:** "D = {D} [{lo}, {hi}], p = {p}. This meets neither the supportive nor the inconsistent
  criterion. The validation pass of the pipeline (2017–2018) gave a larger value. It is not evidence, and the holdout
  is the registered result."
- **What we do not claim:** "We have no real-data evidence for or against the feedback premise at the registered effect
  size."

### D. Primary inconsistent (upper bound below D* = 0.0035)

- **Abstract:** "A pre-registered out-of-sample test on Taiwan's tagged exchange flows (2019–2023) finds no response of
  foreign investors' flow to price deviations at the registered effect size."
- **Empirical section:** "D = {D} [{lo}, {hi}]. The upper bound is below the minimum effect of interest D* = 0.0035, so
  the result is inconsistent with the model's feedback at that size for foreign flow in this market and period. The
  identification results are mathematical and are unaffected. The capital and disclosure figures assume feedback of
  the calibrated size. For this market they describe a counterfactual, not the observed flow."
- **What we do not claim:** "Our pre-registered tagged-flow test does not find the feedback the model assumes, for
  foreign flow in Taiwan, 2019–2023."
- **Also:** the introduction's motivation for feedback in real markets must cite this result next to the crypto
  evidence. It must not omit it.

## 4. Secondary outcomes: fixed readings

- **S1 (Investment trusts, Dealers' own).**
  - Report the §6 verdict for each class, with the Holm-adjusted one-sided p-value.
  - A class that is supportive is described as "supportive after Holm" only if the adjusted p < 0.05.
  - Validation was inconclusive for Investment trusts and inconsistent for Dealers' own. These are not cited.
- **S2 (tagged IV).**
  - Report medians, IQRs and the shares of ŵ significantly positive and significantly negative.
  - Report the share of stocks whose holdout r̂_F lies in its fit-period interval.
  - No p-value (A2, item 5). This is a description, not a test.
- **S3 (formula SE against bootstrap SE).**
  - Agreement if the median ratio is in [0.67, 1.5].
  - A ratio outside this range is read as stated in A2, before data: eq. `eq:ivvar` assumes pure measurement error,
    and structural flow shocks violate it. A failure is reported as a failure of that error assumption for the
    standard-error formula. It is not read as a failure of the identification results.
- **Stability.**
  - Every calendar year and the COVID window is reported.
  - A year with a negative D is shown, not dropped.
  - If the sign of the yearly D changes, the empirical section says so in one sentence.
- **Sensitivity.** The four §7.4 variants are reported in one table. None changes the verdict.

## 5. After the run

1. The zip and its SHA-256 are stored in `results/`. `P1T_unlocks.json` records holdout = 1, the run time and the
   executor SHA.
2. The reading (A–D) and the placeholders are filled into the paper exactly as above. Any further sentence about the
   Taiwan result is limited to stating numbers from the results file.
3. `EMPIRICAL_LEDGER.md` gets a row with the verdict, whatever it is.
