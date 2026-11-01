# Paper 1: SSRN submission text and Quantitative Finance cover letter (draft, 1 November 2026)

The authors must read, edit and approve these before anything is submitted. Nothing here has been sent.

## SSRN form

- **Title:** What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure
- **Authors:** Pratik Niroula (Minnesota State University, Mankato); Prashant Niroula (Tribhuvan University); Sujan Khatiwada (Minnesota State University, Mankato)
- **Abstract (under SSRN's limit):**
  > Market supervisors increasingly ask which group of traders, often which algorithm, drove a price move, and whether they need costly trader-level records to find out. We answer this in a linear market in which groups of traders follow prices with exponentially fading memory and their combined orders move the price. Prices reveal one combined summary of the groups and nothing finer. This gives a separation result for supervision: a market-wide measure, such as a limit applied to everyone, can be sized from prices alone, while deciding whether halting one group is enough needs that group's own trading intensity. Learning it from prices costs a number of experiments or observations that grows as (Δη)^-(4K-2) when the memories of K groups are Δη apart, with matching bounds, and accuracy improves only with the logarithm of the data when memory is a general mixture; records that tag each class's flow remove this cost. The main theorems are machine-checked in the Lean proof assistant. In pre-specified tests, the CFTC's trader-class reports pin down the persistence of speculative positions in all 20 futures markets tested, 9 to 71 times more precisely than prices; matching that precision from prices alone would take, at the median, about 1,350 times as much data. Binance class data show the same in 29 of 29 new markets. We do not show that this persistence is learning memory, and ten of the twenty-two predictions we tested failed, among them tests of price feedback on class positions and of what aggregate order flow reveals.
- **Keywords:** algorithmic trading; market supervision; identification; trader heterogeneity; audit trails; Commitments of Traders; minimax sample complexity; formal verification
- **JEL:** C14, C32, C58, D83, G14, G18
- **Files:** `Paper1_SSRN_full_main_plus_supplement.pdf` (one PDF: main paper, then online supplement)
- **Data and code:** https://github.com/Pratikn03/Fianince

## Cover letter (Quantitative Finance)

Dear Editors,

We submit "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure" for consideration in *Quantitative Finance*.

**The question.** Supervisors and exchanges must decide what trading records to require. MiFID II algorithm identifiers and the US Consolidated Audit Trail are recent examples, and their cost is debated. We ask which questions about who drives prices public data can answer, which they can answer only at a prohibitive cost, and what class-level disclosure is worth.

**Results.**
1. *What prices identify.* In a linear closed-loop market with fading-memory trader groups, prices identify one combined memory distribution and nothing finer.
2. *Supervisory separation.* A market-wide measure can be sized from prices, but deciding whether halting one group restores stability cannot. We give matching bounds on the cost of finding out:
   - experiments growing as (Δη)^-(4K-2) for K groups whose memories are Δη apart;
   - a logarithmic minimax rate for general memory;
   - the same order for passive observation.
3. *Value of class records.* Records that tag each class's flow remove this cost.

**Evidence.**
- In pre-specified tests, the CFTC's weekly trader-class reports pin down the persistence of speculative positions in all 20 futures markets tested. This includes a replication on twelve markets registered after the first eight.
- Matching that precision from prices alone would take, at the median, about 1,350 times as much data (a post hoc lower bound).
- All 22 pre-specified predictions are reported, ten of them failures.

**Verification.** The identification theorem, the matching lower and upper bounds for K groups, the logarithmic rate for general memory and the supervisory separation for two groups are machine-checked in Lean 4 using only its standard axioms. The paper and its supplement state exactly what is and is not formally verified.

**Disclosures.** AI tools (Anthropic's Claude) were used extensively for drafting, computation and formal proofs, as described in the paper's declarations. The proofs not covered by Lean have been checked by the authors and numerically, but not yet independently reviewed. The manuscript is posted on SSRN [link to add] and is not under review elsewhere. All code, specifications and result files are public.

**Suggested reviewer expertise:** market microstructure and surveillance; statistical identification and super-resolution; system identification.

Sincerely,
Pratik Niroula, on behalf of the authors

## Before submitting (authors)

1. Read the whole paper and approve the title change.
2. Confirm Quantitative Finance's preprint policy for SSRN (Taylor & Francis); post to arXiv q-fin as well if preferred.
3. Ask one outside economist or microstructure researcher to read pages 1–3 (the question, the answer and Figure 1).
4. Fill in the SSRN link and check the affiliations.
