# Response to the two simulated referee reports (written 22 November 2026)

The reports are in `REFEREE_REPORTS_SIMULATED_20261121.md`. They were written by AI agents and are not independent
human review. This file says, for every point, what was changed and where. It was drafted by an AI system for the
authors.

**Version answered:**
- the JEDC main text `pdf_delivered/Paper1_JEDC_main.pdf` (31 pages);
- its Online Supplement `pdf_delivered/Paper1_JEDC_online_supplement.pdf` (66 pages);
- built by `ceiling_suite/papers/paper1_jedc_short/build_short.py`.

The long journal version `pdf_delivered/Paper1_JEDC_submission.pdf` (100 pages) carries the same corrections and is
kept for SSRN. Section numbers below are those of the 31-page main text. In the reports, Theorem 7.8 is now
Theorem 7.9, Proposition 7.7 is now Proposition 7.8, and Table 1 is now Table 2.

**Status:**
- **Fixed**: the point is answered in the text.
- **Partly**: it is disclosed or narrowed but not fully answered.
- **Open**: answering it needs new work. The authors' approval is needed where that work is a new analysis.

## Errors in the mathematics (both referees)

| Point | Status | What changed |
|---|---|---|
| Theorem 7.8 used exponent 6 and the rate N^(-1/2) (A 3.1, B 5) | Fixed | Theorem 7.9 now states the null: the group trades like its neighbour, one group in place of the two, memory and weight unknown, so the null is composite. Against the closest such economy the exponent is 4 and the rate is N^(-1). `paradox/exponent_check.py` fits slopes of 4.1 (composite null), 2.1 (simple null) and 8.0 (a shrinking cluster of three). `paradox_check.py` fits -1.000 for n = 4 and -0.327 for n = 8. The text says that a simple null gives n = 2 and complete hiding. |
| The theorem was called an equilibrium (A 3.1, B 4) | Fixed | It is called a best response to a fixed test, in the theorem's lead-in, after the theorem and in the conclusion. |
| The loss L conflicts with Theorem 7.3 (A 3.1) | Fixed | L is the cost of the inquiry that detection triggers, for example a request to brokers for account records. The text says that without the inquiry, detection would have no consequence. |
| Crowding as deterrence, and relation to Bond et al. and Frankel–Kartik (B 5) | Fixed | A paragraph after the theorem: what fails is learning, not necessarily welfare. Bond et al. (2010), Bond and Goldstein (2015) and Frankel and Kartik (2019) are cited. |
| Part (iv): with tags the information comes from the tagged flow (A minor 8) | Fixed | Part (iv) now cites Theorem 7.6. |
| Proposition S4.5 used a pair with different persistences (A 3.2) | Fixed | The pair now has a common persistence. One economy's weights are rescaled by 1 + O((∆η)^(2K-1)) to give a common budget, and the proof is redone. `nearcrit_admissible.py` recomputes Figure 1, Table 2 and the checks. Figure 1(b) shows both pairs. The caption says the information levels off; it does not "grow without bound". |
| The Taiwan targeted range equals the cap by construction (A 3.6a) | Fixed | With the authors' approval, the range was recomputed under protocol P1M-A1, fixed and pushed before the run. The recomputation uses the theory's class: memories in [0, 0.99]; weights all nonnegative (P) or with the tagged signs (T); memory spacings of 0 to 0.10; the two boxes; and a box scan. That is 28 configurations, run once. **P:** the foreign-halt range is [0, 0.0018] at every spacing up to 0.10 and in both boxes, so prices leave foreign feedback anywhere between none and nearly all of the total. The uniform cut stays in [0.0016, 0.0018]. The contrast between the two is therefore not an artefact of the cap. **T:** the cap sets the range (its maximum equals the cap in the box scan), because dealers' negative weight can offset a large foreign weight. The text gives both, and the supplement tabulates all 28. |

## Referee A, other major points

| Point | Status | What changed |
|---|---|---|
| 2: the statistics are borrowed; most results are elementary | Partly | A paragraph in the introduction, "What is new, and what is not", says which statistics are borrowed. It says that Theorem 6.1 is the Gaussian chain rule. It names Theorems 7.3 and 7.5 as the finite-group case of Hunt–Stein, and cites Frankel and Kartik (2022) and Perez-Richet and Skreta (2022). The paper has not been rebuilt around one new result. |
| 3.3: the reset contract, passive upper bound, price records, memory bound | Partly | Theorem 4.4(iv) and the sentence after it state the reset contract. The abstract, Section 7.1 and the conclusion now say that a uniform cut needs the persistence and a memory bound. Section 7.1 gives the log-rate argument for the budget. Open: an upper bound for passive running-market data. |
| 3.4: hidden assumptions | Partly | Table 2's note and Section 5 give the factor σ²I_f for non-Gaussian news. The conclusion lists fixed rules, the public fundamental and investor classes. Not added: idiosyncratic group shocks, and the dealers' lay-off counterparty. |
| 3.5: the Lean checks cover less than the text says | Fixed | Section 7.2 names exactly what is checked in full and what is proved on paper. Theorem 7.9 now says that its Lean file checks the two bounds on (δ*)^(n-2), with Pinsker's inequality, unbiasedness and the power envelope as hypotheses. The main text points to the Supplement's table instead of naming files. The 14,400-economy and 1,200-economy Monte Carlo checks are removed. |
| 3.6(b): the tagged interval rests on a restriction the counterfactual drops | Fixed | With the authors' approval, the decoupled specification was estimated under protocol P1M-A1, fixed and pushed before the run. Each class's flow is a free 10-day distributed lag of x, with AR(2) non-feedback flow, fitted by iterated Cochrane–Orcutt with P1M's price equation and date bootstrap. It was run once in the first author's Colab. Foreign feedback contributes 0.0013 (95% [0.0011, 0.0015]), which contains Table 3's 0.0014. The sensitivity runs are J = 5: 0.0013; J = 20: 0.0012; AR(1): 0.0014. The second Taiwan qualification and a supplement table report them. |
| 3.6(c): the price deviation is not defined | Fixed | Section 7.4 defines it. So do the flow units and the stock universe. |
| 3.6(d): the barrier reflects a weak signal | Partly | Disclosed: feedback contributes 0.0017 to a budget of 0.97, and the calibration illustrates the relative gap. |
| 3.6(e): independence and the grant | Fixed (disclosed) | The third and fourth qualifications in Section 7.4. |
| 3.7: self-containment | Partly | The main text is 31 pages, and Appendix A proves its economic results. Every citation of a supplementary result is to the submitted supplement. Two side remarks still cite other working papers: the rational market maker (companion note, Proposition C2.1(iv)) and the log lower bound for total feedback weight (Niroula et al., 2026b). |
| 3.7: overclaims (the uniform cut from Theorem 6.1; "however long the record"; Taiwan in the abstract) | Fixed | Section 6 no longer derives the uniform cut from Theorem 6.1. The "however long" sentence now rests on the corrected Theorem 7.9. The abstract says the calibration illustrates the barrier, and the introduction reports that the registered test did not establish feedback. |

## Referee A, minor points

| # | Status | What changed |
|---|---|---|
| 1 | Fixed | The minimax sentence appears once. "Negative equilibrium identification rate" is gone. |
| 2 | Fixed | Theorem 4.1(iv) uses the sup of \|G\| + \|G'\| near D = 1. |
| 3 | Partly | Theorem 5.5 says that the estimator is an exact minimizer over a non-convex set, and that no algorithm is given. The constants' dependence on γ and ω_min is stated in the Supplement, not in the main text. |
| 4 | Fixed | The Supplement cites Gautschi (2004) for quasi-orthogonal quadrature. |
| 5 | Fixed | The argument applies record by record, so it covers record-dependent policies. |
| 6 | Fixed | The Figure 1 caption is corrected. |
| 7 | Fixed in the main text | Labelings are π, the paradox distance is δ, the discriminant is Λ0, and harm is α_H. |
| 8 | Fixed | See Theorem 7.9(iv) above. |
| 9 | Fixed | Uncited references are dropped and the lists are alphabetized. |
| 10 | Partly | Added: Grazzini and Richiardi (2015), Platt (2020), Foucault et al. (2007). Not added: Kukacka and Barunik (2017), Comerton-Forde and Tang (2009). |
| 11 | Fixed | Revision history is removed. A build check fails if it returns. |
| Confidential: overlap with 2026a | Fixed (disclosed) | A "Related manuscripts" paragraph cites the 5 November working paper as Niroula et al. (2026a), and the cover letter mentions it. The main text and supplement now use the same letters for the authors' working papers. |

## Referee B, major points

| Point | Status | What changed |
|---|---|---|
| 1: a uniform cut needs a, and knowing a is a composition question | Partly | A new paragraph in Section 7.1, "What setting a uniform cut from prices requires". Knowing a amounts to memories bounded away from zero, and the budget needs a memory bound r̄ < 1. Under both, the budget is learned at rate σ²ε⁻²log(1/ε). Instruments whose incidence varies with horizon act through ∫θ(r)(1-r)⁻¹dM, and Theorem 5.2 sorts them. A theorem classifying real instruments, the paper B proposes, is not written. |
| 2: the barrier binds for no modelled policy | Fixed | New Proposition 7.1(iii) covers a restriction by horizon, which halts feedback from every group with memory below a cutoff r̂ and needs no tags. The hard pair of Theorem 5.1 is placed so that r̂ separates the lowest memories of its two economies, which gives the following: (a) the restriction removes at least κW/K² of the budget in one economy and nothing in the other; (b) the budgets differ only by O((∆η)^(2K-1)); (c) over an interval of ceilings, the restriction meets the ceiling in one economy and breaches it in the other; (d) deciding which takes N ≥ cσ²(∆η)^(-(4K-2)) records. The proof is in Appendix A and holds for every K, using the Gauss–Radau endpoint weight 2/K². `horizon/horizon_check.py` checks it numerically for K = 2 to 6. The introduction mentions it. |
| 3: model assumptions | Partly | The conclusion now lists fixed rules, the public fundamental and investor classes rather than algorithms. Persistence is now said to be derived given the dealers' carry share ā, not derived outright. |
| 4: overclaims | Fixed | The chain rule is named as such. Minimax is "over labelings". The equilibrium wording is gone. The audit trail "keeps its value, because we assume that it cannot be gamed". Taiwan says "given the grant". |
| 6: Proposition 7.7's ranking is built in | Partly | The text says the ranking is built in. It names what an audit trail needs, a stable pseudonymous link, and cites the SEC's 2025 exemption. It notes that self-assigned algorithm labels are the gameable kind. Lemma 7.7(i) ties the social values to equilibrium impact, with λ_ext a parameter. The game itself is unchanged. |
| 7(a): missing definitions | Fixed | See A 3.6(c). |
| 7(b): the uniform cut is granted | Fixed (disclosed) | The third qualification, and item 3 now says "given the grant". |
| 7(c): feedback not established | Fixed (disclosed) | Stated in the introduction, Section 7.4 and the conclusion. |
| 7(d): negligible signal | Partly | See A 3.6(d). |
| 7(e): the tagged-flow information does not reconcile | Partly | The text now says both record lengths hold each class's non-feedback flow at its estimated law. No reconciliation computation was added. |
| 7(f): independence | Fixed (disclosed) | The fourth qualification. |
| 7(g): prior literature | Fixed | Froot et al. (2001), Griffin et al. (2004) and Richards (2005) are cited. |
| 7(h): pending and self-registered tests | Partly | The main text mentions only the completed test. The Supplement still describes the registered tests, now more exactly. Its reverse-causality diagnostic "cannot separate the gain from prices revealing past flow"; it no longer "attributes the gain to reverse causality". The replication's protocol is "recorded with hashes in the authors' public repository", no longer "externally locked". |
| 8: positioning | Mostly fixed | Added: Ho and Stoll; Grossman and Miller; Hendershott and Menkveld; De Long et al.; Cutler et al.; Sentana and Wadhwani; Grazzini and Richiardi; Platt; Rothenberg; Manski; Hunt–Stein (Lehmann and Romano); Chaboud et al.; Khandani and Lo; Stein. Not added: Chiarella, He and Hommes (2006); Chiarella, He and Zwinkels (2014). |
| 9: length, cross-references, repetition, bibliography, apparatus | Fixed | 31-page main text. Cross-references are repaired, the repetition and uncited references are removed, and Lean file and script names are moved out of the main text. |

## Referee B, minor points

| # | Status | What changed |
|---|---|---|
| 1 | Fixed | The abstract says "in the worst case" and is grammatical. |
| 2 | Fixed | "Minimax over labelings, Bayes under an exchangeable prior". The quasi-convex extension of the worst-case comparison is stated. |
| 3 | Fixed | The Monte Carlo checks are removed. |
| 4 | Fixed | Remark 4.2 says the positive results assume that the pricing error is observed. |
| 5 | Fixed in the main text | See A minor 7. |
| 6 | Fixed (disclosed) | The calibrated economy lies outside the positive class, and the calibration's computations do not need positivity. |
| 7 | Fixed | Table 3's note gives the within-stock R² of the price equation (0.95) and of the three rules (0.14, 0.18, 0.10). |
| 8 | Not changed | Proposition 4.5 and Corollary 7.2 remain results. |
| 9 | Partly | Theorem 5.2 now cites the Supplement, not a thesis. The log lower bound for Φ still cites Niroula et al. (2026b). |

## Added beyond the reports

- **Proposition 7.1(iii), restriction by horizon.** See B 2 above. In the long version it is a remark after
  Proposition n:target, with the same argument.
  - `horizon/horizon_check.py` checks, for K = 2 to 6 and four spacings:
    - the matched moments;
    - that all memories lie in [r̂ − ∆η, r̂ + 2∆η];
    - the weights below the cutoff (W/K² and 0);
    - the removal and the ceiling gap.
  - The fitted slopes of the budget gap are 3.2, 5.5, 7.7, 9.9 and 12.1, against 2K − 1. They come out slightly
    above it because the centre moves with ∆η.
  - The budget gap is computed in 60-digit arithmetic.
- **Theorem 7.3(ii), uniqueness of the minimax policy under a strictly convex cost.**
  - The received 27-page version added it.
  - It is now checked in Lean: `PublicationRevision12.lean`, `minimax_unique`.
- **Theorem 7.3(i) and Theorem 7.5 for a cost convex only on [0,1]^K**, as the theorems state.
  - Before, the checks needed convexity on all of ℝ^K.
  - New declarations: `minimax_uniform_on` in `PublicationRevision12.lean` and `tag_minimax_on` in `PublicationRevision11.lean`.
  - The audits show only Lean's three standard axioms.
- **Lemma 7.7, from the received version.** The value λ_ext is now stated as a parameter of the supervisor's welfare criterion.
- **Rothenberg's information matrix.** The introduction now says that it is singular where memories collide, and that the rates measure how fast identification weakens near a collision.

## What still limits the paper

1. **No new economic result is proved entirely within the model's equilibrium.** Both referees asked for one: the relabeling game inside Section 4 (A), or a classification of instruments by incidence (B).
2. **No passive running-market upper bound.**
3. **The horizon restriction of Proposition 7.1(iii) is stylized.** It halts feedback below a cutoff. Real instruments have smoother incidence, and their cost is given by Theorem 5.2, not computed for named instruments.
4. **Taiwan still does not establish feedback.** Both analyses the referees asked for are now done and support the text: the sign-restricted range and the decoupled specification. The registered test still does not establish feedback, and the signal is small: 0.0017 of a budget of 0.97.
5. **The authors have not yet read the corrected results.** These are Proposition 7.1(iii), Theorem 7.3(ii), Lemma 7.7, Theorem 7.9, and Supplement Propositions S4.5 and S11.1. The declaration says so until the first author confirms.
