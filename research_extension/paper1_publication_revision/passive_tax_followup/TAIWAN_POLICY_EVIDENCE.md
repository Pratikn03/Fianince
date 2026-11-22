# Taiwan day-trading tax and feedback incidence

## Evidence available now

Taiwan lowered the tax on qualifying same-day stock round trips on 28 April 2017, from 0.3% to 0.15%. Article 2-2 specifies the same-security, same-quantity and same-account conditions. The historical text also gives a later starting date for qualifying securities-firm transactions. The precise cohort and eligibility definitions must come from archived contemporaneous rules and actual treatment records. [Ministry of Finance, Securities Transaction Tax Act](https://law-out.mof.gov.tw/EngLawContent.aspx?id=20528&lan=E&media=downloadPDF) · [TWSE timeline](https://www.twse.com.tw/en/about/company/history.html)

Wu and Wang (2020) report increased day-trading volume and share after the reduction under their matching and difference-in-differences designs. This is published evidence on turnover around the same policy. It does not measure the signed dynamic feedback response, estimate memory by trader, or validate the paper's incidence function. [Journal of Accounting Review](https://jar.acct.nccu.edu.tw/vol_file.aspx?fid=20200206020228&lang=en)

The official TWTB4U report was queried for a session after the P1T windows. The two returned tables contain market and stock aggregates. The saved schema receipt records the headings and row counts only. There is no stable desk or account identifier and no signed execution sequence. The daily eligibility and end-of-day products should not be treated as a linked account tape. [TWSE day-trading rules](https://www.twse.com.tw/en/products/system/day-trading.html) · [TWSE product fields](https://eshop.twse.com.tw/en/product/detail/0000000071aa258c01725a782bd4008f)

The published article is external evidence. The P1M and P1M-A1 numbers are unchanged. No data from 2017 or other registered Taiwan windows were downloaded or analyzed for this follow-up. No registered test was rerun.

## Minimum data for a direct incidence study

| Input | Why it matters |
|---|---|
| Persistent de-identified account or verified desk ID linked across sessions | Construct fixed cohorts, retain zero-trade observations and estimate within-desk responses. |
| Security, venue, executed side, size, price, timestamp and matching transaction identifier | Build signed flow, measure gross turnover, and align publicly observable returns before the orders. |
| Desk type and pre-policy eligibility, historical security eligibility, tax assessments or validated round-trip treatment fields | Reconstruct exposure under the rules and separate assignment from endogenous realized day trading. |
| A public price-deviation signal chosen before model fitting | Define the feedback input consistently on both sides of the event. Measure its stationarity and address return-to-flow endogeneity. |
| Archived calendar of trading-rule changes, dispositions, corporate actions and other shocks | Exclude or model concurrent changes and validate comparison groups. |

## Candidate design once an authorized panel is available

Freeze the pre-policy roster and exposure definition from administrative eligibility. Estimate each stable cohort's pre-policy memory on a distinct training block. Carry uncertainty in those estimates into the interaction analysis. Avoid defining treated desks as those that subsequently chose to trade or exited.

Estimate a comparison-group event study for daily gross turnover and for the pre-specified signed-flow response to the lagged price signal. To test the model's incidence, allow a tax-exposure interaction with that response and its pre-policy memory. Construct zero-flow rows on eligible trading dates from the fixed roster. For exit, use a separate outcome with an independently fixed observation window and recognize that desk departures can reflect activity migration. A difference in stock-level turnover alone cannot adjudicate either claim.

Before causal interpretation, check historical treatment assignment, overlap, anticipation, pre-trends in both outcomes, spillovers, concurrent rule changes, and sensitivity to the response horizon and price-signal definition. Use inference that accounts for serial dependence, common market shocks and the finite number of assignment units. The day-trading tax changes both trading incentives and market conditions, so an event study needs additional variation or restrictions to interpret the response as the fixed-impact effect. Treat a single national effective date with no credible comparison as descriptive. This document records a candidate design. It neither registers a test nor authorizes use of the frozen P1T samples.

## What the Colab notebook can run

The notebook runs the synthetic passive-only estimator and optionally checks the public TWTB4U fields. It does not request or process brokerage records. Use an authorized computing environment for any licensed account panel. Running the public cells cannot identify desk-level causal incidence.
