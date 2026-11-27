# P1KS: a causal test of the supervisory separation (scoping, 27 November 2026)

Written by an AI system for the authors. **Nothing is registered and no data have been read.** This memo chooses the
event and design. Registration needs the author's explicit approval, and so does reading the development window used
for calibration.

## What the test must show

Theorem 7.1 says that a uniform cut needs only the aggregate, while a targeted restriction needs composition. The
testable consequence is Supplement Proposition S19.1(i): when one class's feedback is removed, the change in
each stock's aggregate feedback is predicted by that class's pre-event tagged contribution. It is not predicted by
anything prices alone identify. This needs a restriction that hits one class, plus daily class-tagged flows by stock.

## Candidates

| Event | Class hit | Class-tagged data | Verdict |
|---|---|---|---|
| **Korea short-sale ban and partial lift.** The ban started in March 2020. On 3 May 2021 short selling resumed **only for KOSPI 200 and KOSDAQ 150 stocks**. A full re-ban followed in November 2023, and a full lift on 31 March 2025 | Foreigners did about 85% of short selling after the lift (FSC) | KRX: daily net purchases by 11 investor categories for every stock, via pykrx and your free KRX account. **Never read for any test** | **Recommended** |
| India, SEBI index-derivative measures (20 November 2024 onward) | Mostly retail option traders; not class-specific by rule | NSE participant-wise open interest (client, DII, FII, pro), index level only | One market and no cross-section, so no control group. Weak |
| China programme-trading rules (2024–2025) | High-frequency and quant accounts | No public class-tagged flows | Not feasible |
| CFTC federal position limits (compliance 2023) | Speculators above the limits | Weekly COT class positions | Weekly data, and few positions bind. Weak |
| Taiwan, March 2020 short-sale limits | Mostly foreign borrowers | TWSE class flows, but the 2019–2023 window was already opened for P1T | Contaminated. Not usable for a fresh test |

## Design for the recommended event (draft, to be fixed in a spec before any data)

- **Switches.** Three dated switches of one class's ability to short:
  - 3 May 2021: on for index stocks, still off for others. This is the cleanest, because it has a same-date control
    group.
  - November 2023: off for all.
  - 31 March 2025: on for all.
- **Pre-event tagged contribution.** For stock s, u_F,s is the foreign category's feedback contribution, estimated from
  tagged flow in a pre-switch window. This uses the paper's tagged rule u_t = r u_{t-1} + w x_t, as in Table 3.
- **Outcome.** ΔA_s is the change in stock s's aggregate price-feedback response across the switch, estimated from
  prices alone. The budget is the cheap question, by Theorem 7.1(i) and Theorem 5.2(i).
- **Primary prediction (sign and slope registered beforehand).** In the 2021 difference-in-differences (index stocks
  against non-index stocks), ΔA_s rises with the pre-switch u_F,s in treated stocks and not in control stocks.
- **Secondary prediction.** A price-only two-exponential fit, run on the same pre-switch window, adds nothing once
  u_F,s is controlled for.
- **Reversals.** The November 2023 and March 2025 switches must reverse the sign.

## The main risk: power

Earlier designs that used daily class flows failed their power checks before any data were read:
- P1K3 on these same KRX data;
- P1A, the liquidity test;
- the P1X cross-market designs.

The reason is the same each time. In daily data, feedback explains only 1–20% of a class's flow, and in Taiwan it adds
about 0.0014 to a budget of 0.97. A stock-level change of that size is far below the noise of a stock-level
persistence estimate from a year of data. The cross-section of about 350 index stocks against about 1,800 others helps,
but my prior that the power check passes is about one in four.

## Protocol (as for P1A and P1K3)

1. **Development window, 2015–2019.** This is before every switch. It is used only to measure the size and spread of
   u_F,s and the noise of a stock-level ΔA, and nothing from 2020 onward is read. **Needs your approval.**
2. **Power simulation.** Calibrate it to step 1, with pass criteria fixed and committed before it runs. If it fails,
   stop and record the failure, as with P1A.
3. **If it passes:** write the spec, executor and Colab notebook, hash and push them, and then **you approve
   registration.**
4. **One run** on 2020–2025, with the result reported whatever it is.

## What it is worth

- **Supportive:** about +4 to +5. This is the first evidence that tags predict a targeted policy's effect where prices
  cannot.
- **Fails:** reported. About 0 to −1.
- **Power check fails:** nothing is registered and the score is unchanged.

Sources: [FSC, partial resumption 3 May 2021](https://fsc.go.kr/eng/pr010101/75835) ·
[FSC, analysis after partial resumption](https://fsc.go.kr/eng/pr010101/76031?curPage=89) ·
[FSC, full reinstatement 31 March 2025](https://fsc.go.kr/eng/pr010101/84220?curPage=2) ·
[SEBI measures (Zerodha)](https://zerodha.com/z-connect/business-updates/sebis-new-rules-for-index-derivatives-heres-whats-changing)
