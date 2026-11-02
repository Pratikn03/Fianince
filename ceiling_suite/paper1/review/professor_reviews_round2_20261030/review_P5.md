# Referee Report — Professor 5 (Senior Faculty Reader: First Impression, Structure, Integrity, and Signal)

## A. Verdict
When an unsolicited 113-page (or 124-page) working paper lands in my inbox from an undergraduate first author at a regional state university and a co-author, my default prior is that it is either an unedited thesis dump or unverified AI slop. **Within five minutes of reading this paper, that negative prior was completely overturned.** The paper is unusually disciplined, mathematically ambitious, and—above all—possesses a level of scientific honesty that I rarely see even from tenured faculty: the Abstract and Table 1 (Page 5) put the *failed* empirical tests right next to the passed ones; the Reproducibility note (Page 2) openly explains the exact nature of the GitHub commits and lists which proofs most need external checking; and the AI-use disclosure (Page 68) is a model of transparency. That said, the paper's biggest weakness is that **it is three papers stitched into one 113-page monster**, and its prose occasionally suffers from "audit-defensiveness"—adding so many parenthetical caveats, file names (`P1_disclosure_oos.json`), and self-corrections (`"A first implementation of this experiment did not pass the trained parameters..."`) that the narrative momentum stalls. Trimming the stitched-on appendices and polishing the prose will turn this into an extraordinary signal for PhD admissions.

## B. Scores
- **Score for posting this version:** 7.5 / 10
- **Score after fixes:** 9.2 / 10

---

## C. Detailed Issues (FATAL / MAJOR / MINOR)

### FATAL Issues
*None. Authorship, integrity, AI disclosure, and negative-result reporting are exemplary.*

### MAJOR Issues

1. **Section 6.4 & Appendix F (Pages 62, 63, 102, 113) — Internal Project Artefacts, JSON Filenames, and Bug Logs Leaking into the Main Text.**
   - **Quote 1:** `"...we pre-registered a dedicated out-of-sample test (P1_disclosure_oos.json,) before downloading..."` (p. 62, Section 6.4; note also the stray comma inside the parenthesis `json,)`!).
   - **Quote 2:** `"After this test failed, we registered a follow-up (P1_disclosure_state_oos.json,) on untouched..."` (p. 63, Section 6.4).
   - **Quote 3:** `"...we pre-registered a second experiment (P1_trained_learners.json,) in which..."` and `"A first implementation of this experiment did not pass the trained parameters to the probing simulator; the results below come from the corrected implementation, which reloads the saved parameters."` (p. 102, Appendix F).
   - **Status:** VERIFIED.
   - **Why it matters:** While Appendix J (`Reproducibility`) and `paper1_reproducibility_map.pdf` are the right places for JSON filenames and code bug history, putting `(P1_disclosure_oos.json,)` (with a typo comma!) in the middle of Section 6.4 and narrating a fixed coding bug in Appendix F reads like an internal lab log rather than a finished working paper.
   - **Exact fix:** Remove `(P1_disclosure_oos.json,)` on p. 62, `(P1_disclosure_state_oos.json,)` on p. 63, and `(P1_trained_learners.json,)` plus the `"A first implementation..."` sentence on p. 102 (keep those details in Appendix J / `REPRODUCIBILITY_MAP.md`).

2. **Title Page & Page 2 (Page 1–2) — Typo in the Public GitHub Repository URL (`Fianince`) and Missing Acknowledgments/Funding.**
   - **Quote:** `"All code, registered test specifications and result files are public at https://github.com/Pratikn03/Fianince."` (p. 2 and p. 113).
   - **Status:** VERIFIED.
   - **Why it matters:** The repository name is spelled `Fianince` (transposing `a` and `i` in `Finance`). If that is the actual live GitHub URL, keep it (or rename the GitHub repo to `Finance` or `hidden-traders-ssrn`, since GitHub automatically redirects old repo URLs when renamed!). Also, as noted in your pre-SSRN check, Acknowledgments and a formal Funding line are missing on Page 1/68.
   - **Exact fix:** If possible, rename the GitHub repository from `Fianince` to `What-Prices-Reveal` or `Finance` and update p. 2 and p. 113. On p. 68 (above `Disclosures.`), add: `"Acknowledgments. We thank [names, with permission] for helpful comments. The authors used AI-assisted internal review during drafting."` and `"Funding. The authors received no specific funding for this work."`

3. **Whole-Paper Structure — Three Papers Stitched Together.**
   - **Quote:** Main text (pp. 1–67) + Appendices A–J (pp. 74–113).
   - **Status:** VERIFIED.
   - **Why it matters:** A 30-minute skim reveals that this PDF actually contains:
     - **Core Paper (Sections 1–8 + Appendices A–F, ~95 pages):** Closed-loop cohort identification, minimax rates $(\Delta\eta)^{-(4K-2)}$ and $1/\log N$, probing capital $\delta^{-4}$, and class-tagged disclosure (CFTC & Binance).
     - **Mini-Paper 2 (Appendix G: A spectral blind spot, pp. 105–106):** Non-normal transient growth at fixed eigenvalues and variance (which belongs to your companion paper `Niroula et al., 2026`, *"From human markets to machine markets: Transient amplification..."*!).
     - **Mini-Paper 3 (Appendix H: Empirical feedback and its measurement, pp. 106–112):** High-frequency EMA filtering bias, clock alignment, and Binance spot zero-fee events (which also belongs to the companion paper on measuring market feedback!).
   - **Exact fix:** Cut Appendices G and H (pp. 105–112, **8 pages**) from this working paper and place them in the companion paper (`Niroula et al., 2026`), where transient amplification and loop-gain measurement are the central themes.

---

## D. Tasks 1–6 Required by the Prompt

### Task 1: Five-Minute Test & 200-Word Plain-Finance Abstract Rewrite
- **Five-minute test verdict:** Reading the Title, Abstract, pp. 1–3 of the Introduction, and Table 1 (p. 5), **yes**, I immediately understand what was done, why it matters, and what passed vs. failed. The "door pushed by several people" analogy on p. 2 and the three options (Wait, Probe, Acquire labelled records) on pp. 2–3 are crystal clear. The only flaw in the current Abstract (272 words) is that it packs too many mathematical exponents and caveats into the final four sentences.
- **Rewritten Abstract (182 words, plain finance language):**
  > Can public market prices reveal the trading strategies behind market moves? We study a dynamic market model in which multiple groups of algorithmic traders react to past prices with exponentially fading memories and their combined orders move the price. Because every group affects the price only through aggregate order flow, prices identify only the combined distribution of trader memories: groups with identical memories are indistinguishable regardless of sample size, and separating $K$ unknown groups whose memory speeds differ by $\Delta\eta$ requires a sample size of order $(\Delta\eta)^{-(4K-2)}$—whether the observer waits passively or trades actively to probe the market. For a known pair of groups, halving the difference in their memories multiplies the required probing capital sixteen-fold. By contrast, regulatory audit trails or class-level reports that record each group's trading separately break the feedback loop and keep estimation well-conditioned regardless of how similar the groups are. In pre-specified tests across eight CFTC futures markets and 29 Binance perpetual markets, published trader-class positions tightly bound position persistence that prices alone leave unidentified, though they do not identify structural learning rules or improve return forecasts.

### Task 2: Thirty-Minute Skim Test (Structure & Cohesion)
- **Is the structure clear?** Sections 1–7 follow a logical arc: Model (Sec. 2) $\to$ Qualitative Identification (Sec. 3) $\to$ Two-Group Capital Cost (Sec. 4) $\to$ $K$-Group, General Memory & Passive Rates (Sec. 5) $\to$ Value of Disclosure & CFTC/Binance Tests (Sec. 6) $\to$ Policy (Sec. 7). The `"In words."` paragraphs after every theorem are a great reader aid.
- **Parts to remove:** Remove the references to Theorem G.1 and Appendix H from the Introduction ("Two supplementary results", p. 6), Table 5 (last 3 rows, p. 15), and the Conclusion (p. 66–67), along with Appendices G and H themselves (pp. 105–112). They are a distraction from the identification and disclosure story.

### Task 3: Concrete Cut Plan (and What a 40-Page Journal Version Would Keep)
- **To cut ~10 pages from `paper1_ssrn.pdf`:**
  1. Cut **Appendix H** (Empirical feedback and its measurement, pp. 106–112): **saves 6.5 pages**.
  2. Cut **Appendix G** (A spectral blind spot, pp. 105–106): **saves 1.5 pages**.
  3. Cut **Appendix C.4 & Table 19** (Probing protocols, pp. 88–89, redundant with Appendix D): **saves 1.5 pages**.
  4. Cut **Table 24** (11-day daily Roll noise table, p. 98, keeping median/range in text): **saves 0.5 pages**.
  - **Total savings: 10.0 pages.**
- **What a 40-page journal version would keep:**
  - Main text (28 pages): Sections 1, 2, 3 (Theorem 3.1), condensed Section 4 (Theorems 4.1, 4.3, Proposition 4.6, and the spectral lower bound Theorem D.2 moved up from Appendix D), Section 5 (Theorems 5.4, 5.5, 5.7, 5.9), Section 6 (Proposition 6.1, Theorem 6.2, Proposition 6.3, CFTC Table 15, and horizon-matched Binance summary), and a 2-page Conclusion.
  - Main Appendix (12 pages): Proofs of Theorems 3.1, 4.1, D.2, 5.4, 5.5, 5.7, 5.9, and Proposition 6.1. Everything else goes to an Online Supplement.

### Task 4: Integrity and Professionalism Audit Checklist

| Checklist Item | Status | Exact Findings & Audit Notes |
| :--- | :--- | :--- |
| **Author affiliations & contact emails** | **Present** | Page 1: Pratik Niroula (Minnesota State Univ., Mankato, `pratik.niroula@mnsu.edu`) and Prashant Niroula (Tribhuvan Univ., Nepal, `prashantniroula20@gmail.com`). |
| **Date** | **Present** | Page 1: `"This version: 30 October 2026"`. |
| **JEL codes & keywords** | **Present** | Page 2: 8 keywords and JEL codes `C14, C32, C58, D83, G14, G18`. |
| **Acknowledgments** | **Missing** | Missing on p. 1 and p. 68. Add before posting to SSRN. |
| **Funding statement** | **Missing** | Missing on p. 68 (only `Disclosures. The authors declare no relevant financial interests.` is present). Add `"Funding. The authors received no specific funding for this work."` |
| **Conflict-of-interest declaration** | **Present** | Page 68: `"Disclosures. The authors declare no relevant financial interests."` |
| **Data & code availability + link** | **Problematic (Typo)** | Present on p. 2, p. 68, and p. 113 (`https://github.com/Pratikn03/Fianince`), but note the spelling `Fianince` (see Major Issue 2). |
| **AI-use statement** | **Present & Exemplary** | Page 68: Explicitly names Claude, ChatGPT, and Gemini, explains their exact roles (code, derivation checks, drafting, internal critiques), and states `"These AI critiques are internal checks, not independent review."` Honest and complete. |
| **Consistent author list for companion paper** | **Present / Check** | Page 72 cites `Niroula, P., S. Alkhushayni, Y. Chen, M. Bhavsar, and P. Niroula (2026)`. However, on p. 62 you also write `"reported in full in the companion thesis"`. Clarify whether that is a thesis or the companion working paper! |
| **Self-citations** | **Present & Minimal** | Only one self-citation (`Niroula et al., 2026`, cited 4 times as the companion paper). |
| **Honest use of "registered" & "verified"** | **Present (needs label tweak)** | Page 2 defines both terms with complete honesty. However, change `"Pre-registered"` to `"Pre-specified"` in Tables 15, 16, and 17 so skimmers who skip p. 2 are not misled. |
| **Internal project language leaking into text** | **Problematic** | Leakages found on p. 62 (`P1_disclosure_oos.json,`), p. 63 (`P1_disclosure_state_oos.json,`), and p. 102 (`P1_trained_learners.json,` and the bug log) (see Major Issue 1). |

### Task 5: The Ten Worst Sentences in the Paper (Quoted and Rewritten)

1. **Page 6, Section 1:**
   - *Quote:* `"First, we show exactly what a closed-loop price process identifies: the combined memory-and-weight summary of the trader groups, and nothing finer (Theorem 3.1)."`
   - *Rewrite:* `"First, we show that a closed-loop price process identifies only the combined distribution of trader memories and weights, and nothing finer (Theorem 3.1)."`
2. **Page 20, Section 2.1:**
   - *Quote:* `"First, a reaction that all cohorts share does not separate them, and an algorithm that hides by mimicking another rate makes the hypotheses closer, so neither lowers the costs we derive: a reaction that differs across cohorts is itself a signature, but one the observer must model, which is a new identification problem rather than a free one."`
   - *Rewrite:* `"First, a uniform reaction across all groups does not help separate them, and an algorithm that mimics another group's memory rate only brings the hypotheses closer together. Conversely, a group-specific reaction creates a new signature that the observer must specify and estimate, shifting the identification problem rather than solving it for free."`
3. **Page 29, Section 4.4:**
   - *Quote:* `"At the calibrated parameters it evaluates to 4.9 \times 10^{-4} par units at \delta = 0.05 with \epsilon = 0.35, five orders of magnitude below any design we can execute, and because m/K_*^2 \propto \epsilon^7(1-S)^5 it collapses near the boundary of the family. We therefore state it as a lemma; Appendix D computes the constant that matters, within 5% of a feasible design at every separation."`
   - *Rewrite:* `"Because the time-domain constant scales as m/K_*^2 \propto \epsilon^7(1-S)^5, it is conservative by five orders of magnitude at our baseline parameters (4.9 \times 10^{-4} par units); Appendix D derives the sharp spectral lower bound (Theorem D.2), which lies within 5% of a feasible probe across all separations."`
4. **Page 36–37, Theorem 5.2(ii):**
   - *Quote:* `"The same bound holds without any labelling convention for the permutation-invariant loss d_\infty(\hat{\theta}, \theta) = \min_\pi \max_k (|\hat{w}_{\pi(k)} - w_k| + |\hat{\eta}_{\pi(k)} - \eta_k|) in place of ||\hat{w} - w(\theta)||_\infty, whenever \Delta\eta \ge 2\tau q/(q+2\tau) (\approx 0.018 at the stated values; for smaller spacings the unordered weights coincide and the relevant permutation-invariant statement is the W_1 bound of Theorem 5.4, at accuracy proportional to \Delta\eta, because then d_\infty(\theta_0, \theta_1) = \min\{2\tau(1+\Delta\eta/q), (1+2\tau/q)\Delta\eta\} \ge 2\tau)."`
   - *Rewrite:* `"For \Delta\eta \ge 2\tau q/(q+2\tau), the same bound holds without any labelling convention under the permutation-invariant loss d_\infty(\hat{\theta}, \theta) = \min_\pi \max_k (|\hat{w}_{\pi(k)} - w_k| + |\hat{\eta}_{\pi(k)} - \eta_k|), since d_\infty(\theta_0, \theta_1) = \min\{2\tau(1+\Delta\eta/q), (1+2\tau/q)\Delta\eta\} \ge 2\tau. For smaller spacings, the relevant permutation-invariant bound is the Wasserstein rate of Theorem 5.4."`
5. **Page 41, Proof of Theorem 5.5:**
   - *Quote:* `"The moment map is invariant to relabelling the atoms, so it is injective only on ordered nodes; on the class of ordered, \gamma-separated nodes it is injective, and the inverse function theorem applies there."`
   - *Rewrite:* *(Delete this sentence completely—it repeats verbatim what was already stated eight lines earlier on Page 41: `"On ordered, \gamma-separated nodes F is injective, because a measure with K distinct atoms is determined by its first 2K moments."`)*
6. **Page 54, Section 6.2:**
   - *Quote:* `"The table's 'known' rows have rates \bar{\eta}\pm\delta (spread 2\delta = \Delta\eta), while the Radau rows place rates at r_c + \Delta\eta s with s \in [-1,1], a spread of about 1.33\Delta\eta for K = 2, so the two kinds of row are not at identical spreads."`
   - *Rewrite:* `"In Table 14, the known-pair rows span a rate width of 2\delta = \Delta\eta, whereas the K=2 Gauss-Radau rows on r_c + \Delta\eta[-1,1] span \frac{4}{3}\Delta\eta \approx 1.33\Delta\eta."`
7. **Page 60, Section 6.4:**
   - *Quote:* `"The fairest comparison is the horizon-matched one, pre-specified on 30 new markets and reported at the end of this paragraph; the one-hour comparisons that come first overstate the gap."`
   - *Rewrite:* `"We begin with the baseline one-hour price kernel in Table 16 and then present the fairer horizon-matched comparison across 30 fresh markets, which reduces the width ratio to a median of 7.3."`
8. **Page 62, Section 6.4:**
   - *Quote:* `"Both results are reported in full in the companion thesis."`
   - *Rewrite:* `"Complete tables for both follow-up tests are available in the online replication repository."`
9. **Page 63, Section 6.4:**
   - *Quote:* `"Both registered primaries pass by a wide margin (Table 17), which confirms that prices cannot reconstruct class position levels; as shown below, this reflects the near-unit-root persistence of positions rather than predictive identification of strategy dynamics: for the 30-minute-ahead divergence between top-trader and all-account positions, out-of-sample R^2 is -4.8% with prices and flow and 46.0% with class data; for the top-trader state it is 4.4% and 54.8%."`
   - *Rewrite:* `"Both pre-specified primary tests pass by a wide margin (Table 17): adding class positions raises out-of-sample R^2 from -4.8% to 46.0% for 30-minute position divergence and from 4.4% to 54.8% for top-trader positions. However, as the next paragraph shows, this gain reflects the near-unit-root persistence of position levels rather than predictability of future trading."`
10. **Page 102, Appendix F:**
    - *Quote:* `"A first implementation of this experiment did not pass the trained parameters to the probing simulator; the results below come from the corrected implementation, which reloads the saved parameters."`
    - *Rewrite:* *(Delete from the paper text; keep in the GitHub commit log / reproducibility map.)*

### Task 6: What This Paper Signals for PhD Admissions — and the Three High-Impact Changes
- **What it signals right now:** To a PhD admissions committee in Finance, Economics, Statistics, or Operations Research, this paper signals **extraordinary drive, high technical ceiling, and rare scientific maturity**. An undergraduate who knows what Kung's eigensystem realization, Gauss-Radau moment matching, Bernstein's equioscillation constant, Whittle likelihoods, and split-panel jackknives are—and who knows how to use AI tools productively while maintaining a strict, reproducible verification pipeline that reports every failed test—is in the top 0.1% of applicants for research potential. However, the sheer length (113+ pages) and the defensive lab-notebook tone in Section 6.4 signal that the authors lacked a senior mentor to tell them **when to stop adding tests and how to edit ruthlessly**.
- **The Three Changes That Would Most Improve That Signal:**
  1. **Create a 35-to-40-page "Job-Market / PhD Admissions Version" alongside the full working paper:** Put the 40-page version front and center when emailing professors, with the remaining 70 pages clearly labelled as an Online Technical Appendix. No professor has time to read 113 pages, and a tight 40-page paper signals that you have professional editorial judgment.
  2. **Stop apologizing in the middle of your paragraphs and present the empirical section in logical order rather than chronological order:** In Section 6.4 (pp. 60–61), lead directly with your *best* test (the horizon-matched 96-lag comparison on 29 new markets and the jackknife unit-root diagnostic), and relegate the earlier 12-lag one-hour test and intermediate follow-ups to a brief footnote or appendix table.
  3. **Fix the CFTC return proxy (use CME futures returns instead of Binance spot / 10Y yield changes) and clean up the JSON filename leaks (`P1_disclosure_oos.json,`).**

---

## E. Cut Plan to Reach Target Page Count
See Task 3 above (cutting Appendices G, H, C.4, and Table 24 saves **10.0 pages** immediately).

---

## F. Three Questions I Would Email the Authors
1. Which parts of the mathematical proofs (specifically Theorems 5.4, 5.5, 5.7, and D.4) were conceived and derived by the human authors versus suggested by Claude/GPT, and can the first author walk me through the Chebyshev equioscillation proof of Theorem 5.7 at a whiteboard?
2. Why include Appendices G and H in this paper when they are already central to your companion paper (`Niroula et al., 2026`)?
3. If you had to condense Section 6 into a single 5-page empirical section with one CFTC table and one Binance table, which two tables would you keep?

---

## G. Would I Forward This to a Colleague?
- **Answer:** **Yes** (especially to our PhD admissions chair and to colleagues working at the intersection of market microstructure and machine learning).
- **The one change that would make my endorsement unconditional:** Strip out Appendices G and H, remove the leaked JSON filenames (`P1_disclosure_oos.json,`), and include a 2-page Executive Summary or a 40-page main body + separate Online Appendix split so busy faculty can read the main paper in one sitting.
