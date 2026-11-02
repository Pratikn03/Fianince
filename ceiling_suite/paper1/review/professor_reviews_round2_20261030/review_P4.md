# Referee Report — Professor 4 (Regulation & Market-Structure Policy / Former SEC DERA Senior Economist)

## A. Verdict
As a former SEC DERA economist who has worked on Consolidated Audit Trail (CAT) economic baselines and CFTC large-trader reporting, I checked every regulatory citation, release number, Federal Register page, and budget figure in this paper expecting to find the usual academic errors. Instead, I found that your regulatory facts—including the March 2026 CAT budget ($147.0M), the 2025 budget revisions ($248.8M and $228.3M), the 2016 CAT Approval Order industry build/ongoing cost estimates ($2.4B / $1.7B), the February 2025 PII exemptive relief (Release No. 34-102386), MiFID II RTS 24 Article 2(1)(b)-(c), and CFTC TFF/Disaggregated categories—are **100% verified and cited with pinpoint accuracy**. Moreover, Section 7 ("When audit trails already exist", p. 65) rightly notes that CAT exists for enforcement, market reconstruction, and cross-market surveillance, that account IDs do not equal single algorithms, and that crypto perpetuals lie outside CAT. However, **Section 6.2 and Table 14 (pp. 52–54)** still set up a headline comparison that will make an SEC or CFTC staff economist wince: dividing the SEC's $147M CAT budget and $1.7B industry compliance estimate by the hypothetical trading losses ($52 \times L_{rt}^*$) of an imaginary trader executing 52 weekly "reset probes" calibrated to 11 days of 2023 Binance BTCUSDT noise. Even with your disclaimers, computing "break-even market counts" (`Mkts ($147.0M / $1.7B)`) conflates private price-impact dissipation in a crypto perpetual with the public-good infrastructure cost of an equity/options audit trail.

## B. Scores
- **Score for posting this version:** 7.0 / 10
- **Score after fixes:** 9.0 / 10

---

## C. Detailed Issues (FATAL / MAJOR / MINOR)

### FATAL Issues
*None. There are zero factual errors in the regulatory citations or institutional descriptions.*

### MAJOR Issues

1. **Section 6.2 & Table 14 (Page 52–54) — Dividing CAT Budgets by Annualised Probing Losses (`Mkts ($147.0M / $1.7B)`) is Conceptually Incommensurable.**
   - **Quote:** `"The final columns divide the CAT LLC 2026 Financial and Operating Budget of 31 March 2026 (total expenses $147.0M...) and the SEC 2016 annual industry estimate ($1.7B, Release No. 34-79318, p. 363) by the annual probing loss per market."` (p. 53, Table 14 caption; discussed on pp. 52–54).
   - **Status:** VERIFIED.
   - **Why it matters:** A DERA economist reading Table 14 will object on three grounds:
     1. **Transfer vs. Resource Cost:** In a zero-sum trading ledger, the prober's execution loss $\frac{1}{2}v^\top T_h v$ is paid to the liquidity providers and cohorts on the other side of the book; it is a *private transfer/dissipation cost* to an active experimenter, whereas CAT's $147M budget and the $1.7B industry compliance figure are *real resource costs* (cloud compute, storage, broker-dealer reporting engineering). (You acknowledge `"not a social cost"` in the caption, but you still divide $147M by it in the final columns!)
     2. **Asset-Class Mismatch:** The dollar numbers in Table 14 (`$14,741,376` and `$356,439,824`) come from multiplying arbitrary par-unit parameters ($a=0.5, \kappa=0.8, W=0.08, r_c=0.60$) by the Roll noise (`0.40 USDT`) and 1-second volatility (`1.98 USDT`) of **Binance BTCUSDT perpetuals in January 2023**. CAT covers **US NMS equities and listed options**, where tick sizes, notional values, and Roll noise per share are completely different from a $20,000 Bitcoin contract! Saying `"matching the $147.0 million 2026 CAT LLC budget requires 456.1 or 18.86 markets"` when each "market" is priced in Bitcoin USDT noise units makes no institutional sense.
     3. **Regulators Do Not Probe:** Since SEC Enforcement and Market Surveillance never submit market orders to probe trader memories (and doing so would be illegal market manipulation!), the SEC's actual alternative to CAT is **passive surveillance** on public SIP / OPRA feeds (or subpoenaing broker-dealer blue sheets after an event), which is governed by Theorem 5.9 and Proposition 6.3, *not* Theorem D.2.
   - **Exact fix:** Remove the last two columns (`Mkts ($147.0M / $1.7B)`) from Table 14 (p. 53) and remove the "break-even number of markets" sentences on p. 54 (`"so matching the $147.0 million 2026 CAT LLC budget requires 456.1 or 18.86 markets..."`). Keep the CAT budget figures in the text simply as a **reference order of magnitude** for what a national audit trail costs to operate, and let **Proposition 6.3** (which compares CAT's fixed operating cost $F$ and per-market compliance cost $c$ against *passive attribution delay* $l G(\Delta\eta)$) carry the multi-market economies-of-scale argument!

2. **Section 1 & Section 7 (Page 1, Page 65, Page 70) — Clarify MiFID II RTS 24 (Record Keeping) vs. RTS 6 (Algo Governance/Testing).**
   - **Quote:** `"Under MiFID II, EU trading venues must keep order records that identify the person or algorithm responsible for each investment and execution decision (European Commission, 2017; ESMA, 2016)."` (p. 1, Section 1; p. 65, Section 7; p. 70, References citing Commission Delegated Regulation (EU) 2017/580, RTS 24, Article 2(1)(b)-(c)).
   - **Status:** VERIFIED.
   - **Why it matters:** Your citation to **RTS 24** (`Commission Delegated Regulation (EU) 2017/580`, Article 2(1)(b)-(c) and Annex Fields 4 & 5) is *completely accurate* for trading venue order record keeping of algorithm IDs! However, European market-structure specialists also think of **MiFID II Article 17 and RTS 6 (`Commission Delegated Regulation (EU) 2017/589`)**, which governs investment firms' algorithmic trading systems, pre-trade controls, and requirement to flag/test each distinct algorithm, and **RTS 22 (`(EU) 2017/590`)** for transaction reporting to national competent authorities (NCAs). Also, note that under RTS 24, each investment firm assigns its own internal short code mapped to a national/venue identifier, so an algorithm ID in RTS 24 is *firm-specific*.
   - **Exact fix:** On p. 65 (Section 7), expand the sentence on MiFID II to: `"MiFID II's order-record and algorithmic-governance framework (RTS 24, Regulation (EU) 2017/580 for venue order records; RTS 6, Regulation (EU) 2017/589 for algorithmic system controls) is the closer analogue, although firm-assigned algorithm identifiers track distinct software strategies within a firm rather than continuous parameter updates \eta_i."`

---

## D. Tasks 1–5 Required by the Prompt

### Task 1: Fact-Check of Every Regulatory Claim in the Paper

| Regulatory Claim in Paper | Location | Verdict | Verification & Primary Source Details |
| :--- | :--- | :--- | :--- |
| **CAT scope:** Captures order & reportable-event info for NMS stocks and listed options across exchanges and broker-dealers from origination to execution/cancellation, linked to customer & broker-dealer IDs. | p. 1, p. 65 | **VERIFIED** | SEC Rule 613 (17 CFR § 242.613), Release No. 34-67457 (July 18, 2012, 77 FR 45722) and CAT NMS Plan Approval Order, Release No. 34-79318 (Nov. 15, 2016, 81 FR 84696). |
| **CAT 2025 PII relief:** Since Feb 2025, under SEC exemptive relief, CAT no longer requires names, addresses, and years of birth of natural-person customers, who remain linked via transformed tax identifier (CCID). | p. 65, p. 73 | **VERIFIED** | SEC Release No. 34-102386 (Feb. 10, 2025), *Order Granting Exemptive Relief from Certain Requirements of the CAT NMS Plan* (exempting reporting of natural person name, address, YOB to CAIS while preserving CCID linkage via transformed SSN/ITIN). |
| **CAT LLC 2026 Budget:** Revised 2026 Financial and Operating Budget published 31 March 2026 has total expenses of $147,044,869 ($147.0M). | p. 1, p. 52–53, p. 73 | **VERIFIED** | CAT LLC 2026 Financial and Operating Budget (published March 31, 2026 on `catnmsplan.com`, total operating expenses $147.04M). |
| **CAT LLC 2025 Budget vintages:** $248.8M for 2025 in Nov 2024 filing (SEC Release No. 34-101901, Dec. 12, 2024, p. 4), revised to $228.3M in May 2025. | p. 52–53, p. 73 | **VERIFIED** | SEC Release No. 34-101901 (Dec. 12, 2024, 89 FR 102975, p. 4 citing $248.8M 2025 budget) and May 2025 CAT LLC budget update ($228.3M). |
| **SEC ex ante industry compliance cost estimates:** 2016 CAT NMS Plan Approval Order estimated $2.4B initial build and $1.7B/year ongoing (Release No. 34-79318, Nov. 15, 2016, 81 FR 84696 at 84801, p. 363); Rule 613 proposing/adopting releases estimated $4.0B initial and $2.1B/year ongoing (Release No. 34-62174 & 34-67457). | p. 52–53, p. 73 | **VERIFIED** | Exact page and Federal Register pinpoints (`81 FR 84801`, `75 FR 32598/32600`, `77 FR 45790-45795`) are 100% accurate and properly distinguished from CAT LLC's own operating budget. |
| **MiFID II algorithm identification:** Commission Delegated Regulation (EU) 2017/580 (RTS 24), Art. 2(1)(b)-(c) and ESMA/2016/1452 require venues to keep order records identifying person or algorithm responsible for investment and execution decisions. | p. 1, p. 65, p. 70 | **VERIFIED** | OJ L 87, 31.3.2017 (RTS 24) and ESMA Guidelines ESMA/2016/1452. (See Major Issue 2 on also mentioning RTS 6). |
| **CFTC Commitments of Traders reporting categories:** TFF (Financial Futures: leveraged funds, asset managers/institutional, dealers/intermediaries) and Disaggregated (Commodities: managed money, producers/merchants/processors/users, swap dealers); Tuesday positions published Friday. | p. 57 | **VERIFIED** | CFTC Form 40 / Large Trader Reporting Program (17 CFR Parts 15–21); Traders in Financial Futures (TFF) and Disaggregated Commitments of Traders reports. |
| **SEC Market Access Rule:** Pre-trade risk controls for broker-dealers with market access governed by SEC Rule 15c3-5 (Release No. 34-63241, 2010). | p. 14, p. 73 | **VERIFIED** | 17 CFR § 240.15c3-5, Release No. 34-63241 (Nov. 3, 2010). |

### Task 2: Judgment of the Comparison of Probing Loss with CAT Budgets (Section 6.2 & 6.4)
- Even with the extensive caveats on pp. 52–54, **dividing the CAT budget by the BTCUSDT probing loss in the final two columns of Table 14 is misleading** (see Major Issue 1).
- However, a regulator reading Section 7 ("When audit trails already exist", p. 65) will **not** feel the authors misunderstand why audit trails exist, because p. 65 explicitly states: `"This is a measurement value, not a cost-benefit assessment: CAT's budget pays for enforcement, market reconstruction and surveillance, none of which the model measures, and Section 6.2 sets the hypothetical probing loss beside it only as a scale illustration."` Dropping the division columns in Table 14 makes Section 6.2 consistent with the sophistication of Section 7.

### Task 3: Audit of Policy Paragraph "When Audit Trails Already Exist" (p. 65) and Conclusion (p. 66–67)
- The three conditional points in "When audit trails already exist" (p. 65)—(1) persistent pseudonymous labels suffice for class response estimation without speaking to enforcement's need for PII; (2) account IDs $\neq$ decision rules because one account can run multiple algos or one algo can split across accounts; and (3) CAT does not cover crypto perpetuals or CFTC futures and is non-public—are **spot on** and do not overclaim beyond the model.
- The Conclusion (pp. 66–67) is similarly restrained and properly flags the missing decision problem.

### Task 4: What a Regulator Would Actually Find Useful (and How to State It in One Paragraph)
A regulator at the SEC, CFTC, or ESMA will find three genuinely valuable insights in this paper: (1) an information-theoretic explanation for why post-crash reconstructions of algorithmic feedback from public price and anonymous order-book tapes alone are fundamentally ill-conditioned when multiple algorithms react over similar horizons; (2) proof that coarse, privacy-preserving *class-tagged* or *persistent pseudonymous* flow records break the closed-loop identification bottleneck ($\Theta(T^{-1/2})$ vs. $\Theta((\Delta\eta)^{-(4K-2)})$) without requiring natural-person PII; and (3) a distinction between *aggregate market stability monitoring* (which only requires the summed impulse response and can be done from public data without participant tags) and *selective participant attribution* (which requires tagged records).

**Suggested One-Paragraph Policy Summary (to place at the start of Section 7, p. 64):**
> *"For market regulators, our results draw a sharp boundary between two supervisory tasks that are often conflated: monitoring aggregate market fragility and attributing feedback to specific trader groups. If a supervisor's goal is to bound overall price amplification or set market-wide circuit breakers, public price and order-flow data suffice because the aggregate closed-loop impulse response is identified at the standard parametric rate regardless of how many hidden algorithmic groups are active (Remark 5.3). By contrast, if supervision requires attribution—determining which class of algorithms or accounts drove a feedback loop in order to apply targeted margin, position limits, or enforcement—public prices face a severe mathematical conditioning barrier ($\Theta((\Delta\eta)^{-(4K-2)})$) whenever groups operate at nearby horizons. Account- or class-tagged records eliminate this barrier by decoupling the feedback loop group by group (Proposition 6.1), and for statistical surveillance of algorithmic feedback, persistent pseudonymous or class-level identifiers deliver this full statistical gain without requiring natural-person personal identifiable information."*

### Task 5: Any Sentence That Could Embarrass the Authors Before an SEC, CFTC, or ESMA Economist
1. **Page 54, Section 6.2:** `"At \Delta\eta = 0.10 (\delta = 0.05) the unknown K = 2 Gauss-Radau pair costs $14.74 million (Roll) or $356.44 million (one-second) per market per year, matching the CAT LLC budget in 10.0 or 0.41 markets and the SEC's $1.7 billion industry figure in 115.3 or 4.77 markets."`
   - *Why it embarrasses:* An SEC economist will immediately ask: "Why are you dividing the CAT NMS equity/options budget by a number calibrated to Binance Bitcoin perpetual volatility?" Delete the market-ratio division (Major Issue 1).
2. **Page 58, Table 15 caption:** `"Weekly returns from Binance spot (Bitcoin, Ether) and Yahoo Finance (others; the Treasury return is minus the change in the 10-year yield), not from the CME futures contracts themselves; the basis between them is ignored."`
   - *Why it embarrasses:* A CFTC economist who works with CoT data every day knows that CME futures settlement prices are publicly downloadable in 30 seconds and that in Treasury futures, the leveraged-fund position *is* the cash-futures basis trade. Using spot returns while arguing about basis trades looks like a shortcut.

---

## E. Cut Plan to Reach Target Page Count
1. **Cut Appendix H (pp. 106–112, 6.5 pages):** Unrelated to regulatory disclosure or trader-cohort identification.
2. **Trim Section 6.2 (pp. 52–54) by 1 page:** Cut the market-count ratios and multi-paragraph walkthrough of Table 14.
3. **Cut Appendix C.4 / Table 19 (pp. 88–89, 1.5 pages).**

---

## F. Three Questions I Would Email the Authors
1. Why divide the US equity/options CAT budget ($147M) by a probing loss calibrated to Binance BTCUSDT perpetual noise in Table 14, rather than calibrating Roll noise to a representative S&P 500 stock or simply keeping the comparison in dimensionless sample ratios (Theorem 6.2) and delay units (Proposition 6.3)?
2. Since CFTC Form 40 classifies traders by predominant business purpose (e.g., "Leveraged Funds") rather than strategy, and one hedge fund category simultaneously runs fast statistical arbitrage and slow macro/basis trades, how does within-class heterogeneity of $\eta_i$ affect the consistency of the class-level IV estimator in Proposition 6.1?
3. Under the SEC's 2015 Regulation Automated Trading (Reg AT) proposal (later withdrawn) and MiFID II RTS 6, regulators considered requiring firms to register algorithm source code or parameters directly (your contract $I_5$ in Table 13). Based on Table 13 and Proposition 6.1, why is tagged order flow ($I_1$ with class tags) preferable to an algorithm parameter registry ($I_5$) when algorithms adapt online?

---

## G. Would I Forward This to a Colleague?
- **Answer:** **Yes** (to colleagues at DERA, the CFTC Office of the Chief Economist, and ESMA working on audit-trail data minimization and algorithmic tagging).
- **The one change that would make me forward it without reservation:** Remove the `Mkts ($147.0M / $1.7B)` division columns from Table 14 (Major Issue 1) so that the regulatory section focuses on the rock-solid statistical contrast between public prices and pseudonymous class-tagged records.
