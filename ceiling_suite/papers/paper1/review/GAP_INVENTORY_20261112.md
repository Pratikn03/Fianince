# Paper 1 (JEDC theory version): every remaining gap, what drags, what can go, what was misjudged

12 November 2026. Written by an AI system for the authors; judgement, not independent review. Version checked:
`pdf_delivered/Paper1_theory_main.pdf` (17 pages) and `Paper1_theory_supplement.pdf` (90 pages), commit f2e8d33.

Counts: 4 must-fix items, 12 open theory limits (all disclosed), 6 evidence gaps, about 20 supplement pages that
can be cut, 9 items labelled "failed" or "inconclusive" re-examined (8 correctly labelled, 1 misframed), and
4 errors of my own found and corrected earlier today.

## A. Must fix before submission (4)

| # | Gap | Why it matters | Fix |
|---|---|---|---|
| A1 | **The Taiwan result is missing from the theory version's abstract and main text.** It appears only in Supplement S7. | Breaks the binding readout rule in `P1T_HOLDOUT_READOUT.md` (rule 3: the primary verdict appears in the abstract, the empirical section and "What we do not claim", whatever it is; an unfavourable result is not moved to the supplement). The core and note versions comply; the theory version, built on 12 November, does not. This was my error. | Put the reading-B abstract sentence in the abstract and the reading-B "what we do not claim" sentence in the main text's Evidence paragraph, word for word. Costs about 40 words of abstract. |
| A2 | Main text calls both tests "pre-registered". | P7S's primary sample is retrospective (specified after the sample period, before data were read). A referee who reads S7 can call "pre-registered" a misstatement. | Say "registered" in the main text, as S7 already does. |
| A3 | AI-use disclosure says the authors verified all proofs. | Not yet true for the results new since 5 November. | The authors' check (`AUTHOR_PROOF_CHECKLIST_20261112.md`), or reword the sentence to say which proofs were verified. |
| A4 | Lean whole-project receipt is from 9 November. | The 11 modules added since were compiled one by one here; the full build has not run with them. | Run the Colab notebook; commit the receipt. |

## B. Open theory limits (12, all stated in the paper)

| # | Limit | Where stated | Weight with a JEDC referee |
|---|---|---|---|
| B1 | Nonlinear rules: lower bounds hold, no upper bound; for some families composition is not identified at all | Main 7, S6.3 | Medium |
| B2 | Near instability: per-observation bound only; a finite-sample version uniform in the margin is not proved (numbers within 98-99.8%) | Main 4 | Low |
| B3 | Noisy stress identification: consistency, no rate; needs probes of all sizes | S12.3 | Low |
| B4 | Pooling globally: order between the local exponent and one market's; equality only numerical | S5.3 | Low-medium |
| B5 | Pooling: rank condition (R) exact only for K up to 8 | S5.3 | Low |
| B6 | Probabilistic steps of the partial-disclosure and pooling upper bounds are on paper, not in Lean | S28 | Low |
| B7 | Strategic hiding: one group; several groups only as a remark; long-lived strategic insider open | S5.4, S7 | Medium |
| B8 | Traders who learn while trading are outside the theorems (simulations show where it fails) | S7, S26 | Medium |
| B9 | Gaussian innovations assumed for passive results | S7 | Low |
| B10 | Upper bounds need reset experiments or a known initial state | S7 | Medium (realism) |
| B11 | Constants grow fast in K; double-precision Prony fails at K = 4 | S4.1 | Low |
| B12 | No supervisory loss estimated, so no value of disclosure in money | S7 | Medium |

None is a hole in a proof. Each is a stated boundary. B1, B7, B8, B10 and B12 are what a referee will push on.

## C. Evidence gaps (6)

| # | Gap | Status |
|---|---|---|
| C1 | No test is a direct test of a theorem of this paper (ledger finding 1) | Structural: no public data with class-tagged executed flow at the needed resolution |
| C2 | Taiwan (P1T): supportive by the registered criterion; its pre-specified check attributes the gain to prices revealing past flow (reading B) | Fixed by the readout rule; cannot be reread |
| C3 | Binance stress test (P7S): inconclusive | Replication result after 14 February 2027 |
| C4 | Class-report tests of the full working paper: 11 of 23 outcomes pass, all proxies | Cited in S7 |
| C5 | Cross-market (P1X) and probe (P1K) test designs failed their simulation checks | Not in the paper; no feasible public-data design found |
| C6 | Calibration (4,000 years) uses illustrative parameters, not fitted ones | Stated |

## D. What drags the paper, and what can be cut

The supplement is 90 pages against a 17-page main text. Two things make it heavy.

1. **S1-S7 (25 pages) restate the main text in full** before the proofs (S8). Much of this is needed, because the new
   results (S5.2 partial disclosure, S5.3 pooling, S6 saturating traders) carry their proofs inline. The rest repeats
   the main text with more detail.
2. **Sections the main text never cites** (pages are approximate):

| Section | Pages | Keep? |
|---|---|---|
| S24 Account-level capital | 8 | **Cut**; in Niroula et al. (2026a). Crypto-calibrated capital, far from the JEDC question |
| S25 Hypothetical illustration in Bitcoin dollars | 1 | **Cut**; same reason |
| S11 Two unknown groups: pole fitting and global | 2 | Cut or fold into S4.1 |
| S20 Natural excitation and the cost of ambiguity | 1 | Cut |
| S21 Worked example: two Kalman desks | <1 | Keep (short, concrete) or cut |
| S16 Cramér-Rao benchmark | 2 | Keep (ties to the literature, machine-checked) |
| S17 Finite-sample surveillance bounds | 1 | Keep (short) |

Cutting S24, S25, S11 and S20 saves about 12 pages; tightening S1-S7 to statements plus inline proofs could save
about 8 more, for a supplement near 70 pages. These were restored earlier today at the authors' request; they are not
wrong, they are unused by this version and stay in the full working paper.

## E. Things labelled "failed" or "inconclusive", re-examined (9)

| Item | Label | Correct? | Note |
|---|---|---|---|
| P7S primary | Inconclusive | Yes | Its calm half passed precisely (interval ±0.007 against a ±0.10 margin); its stress half did not (p = 0.553). The registered verdict needs both. A calm null is also what a world without limits predicts, so the passed half is not evidence alone. |
| P1T primary | Supportive, reading B | Yes, under the registered rule | The check's interval [-0.032, 0.017] is wide, and amendment A2 found the check also removes some genuine feedback. The readout rule forbids adding that nuance to the paper; it can only state numbers. |
| Class-report tests, 11 of 23 | 11 fail, 1 not supported | Labels yes; **framing in Paper 1 misleads** | All are proxy tests of the full working paper's persistence claims; none tests a theorem here (ledger). S7 gives the count without saying so. Add: "None is a direct test of a result in this paper." Keep the count. |
| E23 root-T shrinkage | Pass | Yes, but uninformative | Any regular estimator passes it; correctly kept as secondary. |
| P1K designs 1 and 2 | Failed simulation | Yes | Design stage; no data read. |
| P1X designs 1 and 2 | Failed simulation | Yes | Criteria fixed before running; design 2 had near-zero power, design 1 inflated size. |
| Prony at K = 4 | "Fails" | Yes, as an implementation note | Double precision only; the 60-digit checks work. Could say so in one clause. |
| Prediction (c) for independent learners | Fails | Yes | A boundary of the linear theory, reported. |
| Saturation, adaptive gains, neural nets | Linear theory fails | Yes | Reported in S26 as where the theory stops. |

## F. My own errors found and corrected today (4)

1. Rank condition claimed exact for K up to 5 for all D; the exact check had timed out. Now certified for K up to 8.
2. Global pooling stated as an exact order; only the upper bound was proved. Restated.
3. "Collisions" for three algorithms in three markets were ill-conditioning at nearly coincident nodes. Corrected.
4. The P7S data statement claimed checksum verification and spot data. Corrected.

## What moves the score

- Fixing A1-A4: required. A1 puts an unfavourable sentence in the abstract, which costs a little with referees but is
  required by the authors' own rule; leaving it out would be worse if noticed.
- Cutting about 20 supplement pages (D): helps more than any new result now.
- Clarifying C4 framing (E): small help.
- Theory limits B: acceptable as disclosed; no further theorem is needed for submission.
- Evidence C: nothing feasible before the February 2027 replication.

Estimate after A, D and the C4 clarification: about 86-87, roughly 55% at JEDC. Judgement, not data.

## Status after the fixes of 12 November 2026 (afternoon)

- A1 done: the Taiwan reading-B abstract sentence and "what we do not claim" sentences are in the JEDC abstract and
  main text, word for word; the Binance result is in the abstract too.
- A2 done: "pre-registered" now only for the Taiwan holdout; the Binance test is "registered", and the main text
  says it was specified after its sample period, before its data were read. Same change in the note, the core and
  the RFS cover letter.
- C4 framing done: "None is a direct test of a result in this paper" added after the 11-of-23 count.
- D partly done: account-level capital and the dollar illustration cut (they remain in the full working paper);
  the capital order the main text cites is in Section "Execution cost and capital". Supplement 90 -> 81 pages.
  The two-group section (S11) is kept: Theorem prop:passive(ii) uses it. Natural excitation is kept (one page, part
  of the economic-primitives block). Tightening S1-S7 is not done: it would need a restructuring of the build.
- A3 and A4 remain with the authors: the proof check and the Colab Lean receipt.

## Later on 12 November: the Taiwan test removed from the JEDC version

By the authors' decision (`p1_empirics/P1T_readout_amendment_R1.md`), the JEDC theory version no longer mentions the
Taiwan test: not in the abstract, the main text, Supplement S7 or the data statement. The other versions keep it.
This replaces item A1 above for this version. Abstract 142 words; supplement 80 pages. Risk recorded in the
amendment: the test is public in the cited repository.

Revised the same afternoon: the Taiwan test is back in Supplement S7 (reading-B text), not in the abstract or the
main-text results; the main text points to S7 for both registered tests. Supplement 81 pages.

## Evening of 12 November: both levers pulled

- Thesis chapter 4 imported (authors' decision): Theorem `thm:questions` (exact cost of any linear question, by a
  modulus with a polynomial-approximation dual) and Proposition `prop:parametric` (cheap exactly for square-summable
  coefficients), with proofs, re-checked step by step on import; new main-text Theorem "Which questions prices answer
  cheaply"; abstract sentence; Monte Carlo (slopes -0.02 and -3.02). The safety boundary case is cited to Paper 2,
  not proved here. Costs recorded: uses up the planned Paper 3's lead result; the thesis chapter is the first author's
  own work and now appears under three authors; the cover letter's "shares no results" with Paper 2 still holds (the
  boundary case is cited).
- Hostile-referee pass (`HOSTILE_REFEREE_PASS_20261112.md`); "What is new" rewritten as six results with no
  counterpart in the cited literatures; robustness sentence in the opening.
- Supplement: four duplicated expository paragraphs dropped. Net 83 pages (the new section adds three).
- run_all_checks.py: 19 of 19 checks pass (two new dichotomy checks).
