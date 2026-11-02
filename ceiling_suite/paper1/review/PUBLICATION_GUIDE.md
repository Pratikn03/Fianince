# Paper 1: complete guide from here to SSRN and a journal (31 October 2026)

Goal: one SSRN upload that is already the journal submission — a **journal-length main paper (about 45 pages)**
followed by an **online supplement** — so that moving from SSRN to Quantitative Finance (or a similar journal) needs
only formatting. Target quality: 9/10 or better from the five professor-role reviews on both parts.

Honest calibration: the latest AI reviews score the 112-page version 5.5–7.5 for posting and 7.5–9.2 after their
fixes. No reviewer has found a false theorem, number or regulatory fact. The weakest axis is economic depth for a
finance theorist (P2); the new targeted-intervention result addresses the main complaint. A 9/10 preprint is
realistic; journal acceptance is never guaranteed.

---

## Part A. Things only you can do (blocking)

| # | Item | What I need from you |
|---|---|---|
| A1 | **Byline** | Prashant confirms in writing that he stays on (or asks to come off). No change without his written agreement |
| A2 | **AI-use statement** | Confirm it is complete: Claude (code, checks, drafting), ChatGPT and Gemini (planning, critiques). Add any other tool you used |
| A3 | **Funding, conflicts, acknowledgments** | Tell me the facts: any funding? any competing interests? anyone to thank (ask Dr. Bhavsar first)? |
| A4 | **Companion paper** | Confirm its author list (the bibliography has 5 authors) and whether it is public (SSRN link?) |
| A5 | **CFTC re-run with CME futures** | Say "approve", then run the draft script in Colab (Part D) and send me the result file |
| A6 | **Human proof check** | Ask 1–2 people (Prashant, Sujan, or a professor) to check the packets in `proof_review_packets.md`; the priority list is in Part C |
| A7 | **Repository name** | Keep `Fianince` or rename (GitHub redirects old links); I then create the release tag `paper1-ssrn-v1` |
| A8 | **Thesis branches** | Two unmerged branches (`codex/thesis-completion-20261022`, `codex/thesis-readiness-20261026`); merge or close. One changes CI, which needs your explicit approval |
| A9 | **Journal and preprint policy** | Confirm Quantitative Finance; email its editorial office about SSRN (T&F's policy names non-commercial servers), or also post to arXiv q-fin |
| A10 | **Read and sign off** | Read the main paper end to end; be able to explain the main result in 200 words and the K-group lower bound at a whiteboard (a reviewer asked exactly this) |

## Part B. What I will do (no input needed beyond Part A)

1. **Two-part build from the single source `paper1.tex`:**
   * **Main paper (~45 pages):** Introduction with the pass/fail table (4 pp); model and the observer (4); what prices
     identify, Theorem `thm:merged` (3); costs for a known pair: quantity, capital, spectral bound, worked example (4);
     unknown groups and passive data: Theorems `thm:kcohort`, `prop:esprit`, `thm:general`, `prop:passive` (6);
     value of disclosure and the decision results: `prop:tagged`, `thm:discvalue`, `prop:choice`, `prop:target` (6);
     evidence: CFTC and Binance with the horizon-matched test and all failures (5); policy and conclusion (2);
     references (4). Proof sketches stay in the main text; full proofs move to the supplement.
   * **Online supplement (S-numbered):** all proofs; account-level capital and the explicit constants (Appendix D);
     near-colliding rates; learners and nonlinear rules; probing protocols; primitives and tied intensities;
     Cramér–Rao and Le Cam tables; the hypothetical dollar illustration; the finite-horizon note; the spectral
     blind spot and feedback measurement; the reproducibility map.
   * SSRN gets one PDF (main then supplement). The journal gets the same two parts as separate files.
2. Journal formatting (Taylor & Francis / QF template), keywords, JEL, data-availability and declarations.
3. Fix the overfull lines in the journal version and keep the clean-reproduction CI green.
4. After A5: one robustness paragraph and a table note (post hoc, alongside the registered result).
5. A final round of the five professor-role reviews on the two-part version; fix every verified point; record
   dispositions; repeat until each role scores at least 9/10 or the remaining points are author decisions.
6. The SSRN form text (title, abstract under SSRN's limit, keywords, JEL, affiliations) and the QF cover letter.

## Part C. Proofs that most need a human check (in order)

1. Theorem `thm:general` (logarithmic rate; the alternating-measure and coefficient bounds).
2. Theorem `prop:passive` (finite-T Toeplitz bound).
3. Theorems `thm:spectral` and `thm:rh` (dollar floor and its finite-horizon dual).
4. Proposition `prop:target` (new; Le Cam reduction and the window of thresholds).

Theorem `prop:esprit` (Prony upper bound) was machine-checked in Lean on 31 Oct 2026 for every K
(`Paper1PronyUpper.lean`). A human reader should still compare the formal statement's assumptions with the
paper's (sub-Gaussian noise; memory rates of modulus at most one; the estimator defined as the ordered
moment-matching representation, which `p1_prony_polynomial` shows is Prony's output).
Lean covers the model facts, not these rate theorems; the paper says so.

## Part D. CFTC re-run with CME futures prices (needs your approval)

* Script: `ceiling_suite/p11/robustness_cme_futures_DRAFT.py` (draft, not run, not registered).
* Same estimators, data end and markets as the registered test; only the price source changes for six markets:
  `BTC=F`, `ETH=F`, `ES=F`, `ZN=F`, `6E=F`, `6J=F` (crude oil and natural gas already use futures).
* Two variants written down before any result: all weeks, and excluding contract-roll weeks (calendar rule in the
  script).
* Reported as a post hoc robustness check next to the registered result (8/8, 4/8, 6/8); it does not re-score it.
* To run, after you approve: open Colab, then
  ```
  !git clone https://github.com/Pratikn03/Fianince.git
  %cd Fianince/ceiling_suite/p11
  %run robustness_cme_futures_DRAFT.py
  ```
  and send me `C4R_cot_cme_futures_robustness.json` from your Drive folder `ceiling_suite/results/`.

## Part E. From SSRN to the journal (minimum work)

1. Cite the SSRN version in the submission; note it in the cover letter.
2. Upload main and supplement as separate files; same text as SSRN.
3. Data and code: link the release tag, not the moving main branch.
4. After acceptance, update the SSRN page as T&F asks (accepted note, then DOI).

## Current state (31 October)

* SSRN build 112 pages (main text plus internet appendices), two supplements in the repository.
* Traceability audit done (`traceability_audit_20261031.md`): every table traced to code and results; two
  rounding errors fixed; a build hazard that could have reverted the paper removed.
* Remaining blockers: Part A.
