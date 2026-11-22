# Four referee-style reports on Observationally Equivalent Algorithms

22 November 2026. These are simulated reports by one AI system and are not independent peer review. Each report uses its own disciplinary criteria and concerns the original 33-page manuscript and 67-page Online Supplement. Main citations use the printed page, with “title” for the unnumbered first PDF page. Supplement citations use printed S-pages. The post-revision assessment appears in the issue ledger.

## Referee A — Econometric theory and statistics

### Summary

The paper contains a useful inverse problem with an explicit observation experiment. Its strongest mathematical material is the moment cancellation and the two-point comparison. Several statements around these arguments are materially stronger than the experiment or proof supports. The policy and statistical results interact precisely where these distinctions matter most.

### Major issues

- **A01 · p. 8, Proposition 4.5(i).** A factorization of the observation law through the flow map does not identify the map. A constant price law is an immediate counterexample to the asserted implication even when the safe action depends only on the map. Parts (ii) and (iii) use the correct direction.
- **A02 · pp. 9, 11, 17–18 and S-8–S-10, S-13–S-15, Theorems 5.1, 5.2 and 7.6.** Pointwise Schur stability does not supply the uniform constants used in the response and Toeplitz bounds. The short main text also loses the depth required for a nonzero reset gap, the accuracy and confidence conditions on Prony, and the local interior condition behind the tagged rate lower bound. A sufficiently short record can have exactly zero gap.
- **A03 · p. 11 and S-34–S-36, Theorem 5.2(ii)–(iii), Theorem S10.1 and Proposition S10.2.** The stated experiment has fixed depth L, but the Hardy-space result allows L to increase. At fixed L the zero-distance modulus excludes every nonpolynomial target below a positive half-width, including discounted feedback. The impossibility proof uses a TV upper bound of one half and only covers alpha below one quarter as written, whereas the main statement covers alpha below one half. In S10.1(ii), when the approximation error is zero the chosen dual witness may have zero mass and the rescaling divides by zero.
- **A04 · pp. 1, 11, 14–15 and S-36, Theorem 5.2 and Proposition 7.1(iv).** The exact Gaussian variance is for directly observed kernel taps. Extracting kernel taps from noisy impulse prices is nonlinear. Even the first reconstructed tap relies on knowing persistence or separating the zero-memory component. The first-order supplement discussion does not give a finite-sample equivalence and confuses an operator norm bound with a bound for the Euclidean norm of L noisy coordinates.
- **A05 · pp. 15, 17 and 27, Theorems 7.3 and 7.5.** Strict convexity on a closed cube does not imply a minimum is attained. A symmetric cost formed by summing a strictly convex function with an upward jump at zero is enough to break the claim. For partial tags, the value comparison must use the same cost and the correct ambiguity set for each regime.
- **A06 · pp. 18, 27–28, Lemma 7.7(ii).** The first-order condition gives E[v given the filter output] divided by the trading-cost coefficient. An arbitrary exponential filter need not supply that conditional mean, so the displayed profit-loss formula is for a plug-in strategy at fixed impact. A random-walk level does not have stationary second moment, even if the error does. An O(w) effect on equilibrium impact does not make the fixed-impact quadratic expansion exact in the deviation for positive w.
- **A07 · pp. 19 and 28 and S-44–S-45, Proposition 7.8(iii).** Strict monotonicity gives a unique positive finite cutoff only when the incremental audit cost is strictly between zero and the maximum audit gain. The statement allows zero and arbitrarily large cost gaps. The proof also leaves the zero-net-value case with multiple optimal policies.
- **A08 · pp. 20–21, 29 and S-37–S-39, Theorem 7.9 and Proposition S11.1.** The Pinsker step away from zero is valid with size control and unbiasedness at zero. The positive square-root power envelope in the Gaussian illustration requires a specified direction normal to the null. A squared KL expansion or a fitted slope for a closest null alone does not produce such a uniformly valid finite-record test. A tag does not make every detection rule independent of memory. The exact-power-law game and the venue interpretation must be distinguished.
- **A09 · S-22, Corollary S7.2(iii).** The event used to apply the inverse requires a confidence-dependent smallness condition on the rescaled noise. An absolute bound on epsilon_N cannot ensure that the displayed high-probability radius stays in a fixed inverse neighborhood at arbitrarily small beta. The observation contract must include the additional impulse tap and the pre-probe quote.
- **A10 · S-10, S-19–S-20, Theorem S4.4(ii).** The proof bounds the higher moments by a remainder in the spacing alone. It does not show that the remainder retains the extra tau factor. State the result for fixed nonzero tau, or prove a uniform remainder and the corresponding split of the testing quantifiers.
- **A11 · pp. 9–10, Theorem 5.1 and Table 2.** Fisher information controls a local shift expansion. It is not a global KL bound for arbitrary regular location laws. Also, dividing a finite-record testing threshold by an asymptotic divergence rate does not yield a finite-record lower bound without a certified finite-record KL inequality for that pair and length.
- **A12 · pp. 9, 11–12, 14–15, 17–18 and 24–29, Appendix A.** The headline passive and reset bounds, modulus, largest-class halt and disclosure claims send the reader elsewhere for the operative proofs. At minimum Appendix A needs the reductions, their hypotheses and the two-point, approximation and identification steps that drive the conclusions.

- **A15 · p. 19 and S-45–S-47, Propositions S15.2 and Theorem S15.4.** The generalized routing result needs strictly positive private marginal gains and specific cost bounds. Complete collapse requires full label reachability. With a fixed best-response tie rule, continuity of the supervisor’s objective does not follow. The comparison proof controls suprema and should be stated that way.

### Minor issues

- **A13 · pp. 14, 27, Proposition 7.1(iv).** The sample sizes are real-valued expressions for sufficient replication counts and should be rounded up. At h = 1 the threshold alternative uses zero, outside part (iii), and no permitted positive-memory group falls below it.
- **A14 · p. 17, Corollary 7.4(ii).** The proposed scaling is feasible only for a ceiling between the exogenous persistence and the original budget, and the stated ratio is undefined at zero feedback.
- **Proof checks without a separate objection.** The pathwise induction in 3.1 and S2.1, triangular equilibrium substitution in 4.1(i) and 4.4(i), Taylor and chain-rule factor in 5.4, and risk comparison in 6.1 check under their stated common-history assumptions. The 5.4 constant follows from the squared Taylor bound, the Gaussian factor one half and KL at least one half. For 7.1(iii), the left Radau endpoint is strictly below the cut, the leftmost Gauss node is strictly above it, and the normalized Radau endpoint has weight 1/K². In S4.1 the first possible response difference is h_(2K). The S9.1 Christoffel-weight argument supplies an analytic largest-weight gap for the targeting result without relying on S12.2’s numerical comparisons. In S9.3 the spectral sandwich implies the finite Toeplitz bound actually stated there. The S10.1 duality and quantile sandwich otherwise work, and S18.2 compares the mixture integral at the true truncated coefficients without conditioning a Gaussian likelihood on the whole realized design. Appendix A’s relabeling best response and 7.9 distortion comparisons were checked subject to A07 and A08. This review does not certify every auxiliary theorem in S8 or S12–S18, or a Lean build.

### Recommendation and what would change it

**Major revision.** Correct the false identification implication and the missing domains and assumptions. Make the core arguments inspectable in the main document. Supply a market-specific testing result for the stronger surveillance interpretation or keep the theorem conditional on the specified power function.

## Referee B — Market microstructure and policy

### Summary

The main economic distinction is between a known intervention on an aggregate impulse response and assigning responsibility to an economic actor. The paper’s market is too stylized to sustain the instrument claims as written. The intuition is worth preserving, but the retained scope is closer to a supervisory benchmark than an institutional model of HFT.

### Major issues

- **B01 · pp. 14–15, Proposition 7.1(iv).** A lag-decay parameter is not an executed turnover rate. A minimum resting time constrains cancellation and repricing, whereas the proposed transformation deletes a portion of executed feedback. The transaction model has no submission, cancellation, routing, queue or execution response from which either incidence follows. The sign and shape could change when liquidity supply and strategic order handling respond.
- **B02 · pp. 7–8, 14–18 and S-30, Theorems 4.1, 4.4, 7.3 and 7.5 and Proposition 7.1.** The inventory equilibrium makes market impact endogenous to the population. The cut formula holds impact and persistence fixed even though the composition intervention may change the underlying equilibrium. Minimax over labelings also holds the economic population and loss fixed. It does not select a globally optimal instrument or certify a target after agents or dealers respond.
- **A04 · pp. 11, 14–15, Proposition 7.1(iv) and Theorem 5.2.** A supervisor does not observe Gaussian kernel taps from a live exchange. Specify the signal, policy horizon, impact input and what can actually be measured. Distinguish measuring the reduction from certifying that the residual budget lies below the ceiling.
- **A08 · pp. 20–21, Theorem 7.9.** The regulator is assumed to commit to a detector, a single group moves and the penalty is constant. A convergence result inside that game says little about equilibrium instrument design. Distinguish identification, the evidence needed to assign an account or owner, and deterrence.
- **B03 · pp. 4, 19, 23, Proposition 7.8 and conclusion.** The model gives the audit trail a perfect owner link by assumption. The CAT example documents customer linkage, but that does not establish an error-free mapping to the beneficial owner, algorithm, or economic strategy targeted by the paper.
- **C04 · pp. 21–23, Section 7.4.** A daily institution-level response in Taiwan is not observation of an intraday algorithm or a causal destabilizing mechanism. The calibration should not be the bridge from the stylized equilibrium to a claim about operational interventions.

### Minor issues

- **A07 · pp. 2, 19, Proposition 7.8.** Partial policy and a hiding share independent of gamma describe the interior branch. At boundary optima the harmful label can be completely closed and the hiding share can vary with gamma.
- **D01 · pp. 3–4, Section 1.1 and Proposition 7.1(iv).** Use Budish, Cramton and Shim’s actual resting-time mechanism and confront evidence on transaction-tax-induced shifts in volume and liquidity. This would distinguish the proposed benchmark incidence from mechanisms venues can implement. [Budish, Cramton and Shim (2015), QJE](https://doi.org/10.1093/qje/qjv027) · [Colliard and Hoffmann (2017), Journal of Finance](https://doi.org/10.1111/jofi.12510).

### Recommendation and what would change it

**Reject in its current form.** I would consider a major revision if it clearly states what prudential inference the benchmark delivers. A venue mapping with credible incidence and post-policy equilibrium responses would be needed to support instrument recommendations.

## Referee C — Empirical methods and replication

### Summary

The presence of separately logged development and holdout work is valuable. The empirical contribution is a model-based calibration to estimated responses. Its strongest result is exact permutation invariance in the fitted experiment. The extreme calendar horizons and narrow aggregate range carry considerably less evidentiary weight.

### Major issues

- **C01 · pp. 2–3, 21–22 and S-55, Section 7.4/Q1–Q3.** The program computes a Whittle rate and multiplies by record length. Pinsker requires the actual finite-record KL or an upper bound on it. There is no such certificate here. Even with Gaussian stationary AR(1) laws and common innovation variance, the one-observation KL can exceed the asymptotic rate. This is an inference bug, with no demonstrated error in the archived numerical output. Preserve the output and change the interpretation.
- **C02 · pp. 2–3, 22 and S-55–S-57, Section 7.4/Q2–Q3 and P1M-A1 Part A.** Multistart SLSQP provides feasible endpoints found by search. An inner range cannot support a statement that every candidate lies inside it. This affects the uniform-cut claim as much as the targeted claim. Negative, near-canceling class weights and box constraints drive the most extreme targeted examples. Exact relabelings survive these objections where the specified class admits them.
- **C03 · pp. 2–3, 22–23 and S-16–S-17, Section 7.4/P1T.** Give the primary holdout verdict and the pre-specified reverse-causality diagnostic as different outcomes. The committed readout supports incremental prediction of foreign flow in the primary test. The residualized diagnostic does not establish causal feedback. P1M and P1M-A1 use the development period under protocols fixed before their own runs.
- **C04 · pp. 21–23 and S-54–S-57, Table 3 and P1M/P1M-A1.** The archived result files permit arithmetic checks but the original panel and bootstrap provenance are insufficient to independently reproduce the upstream fit here. The beta, reference-price construction, exclusions and retained observations enter the estimand. Causal conclusions about HFT need a different observation design.
- **C05 · pp. 21–22 and S-55, Section 7.4/Q1.** The tagged and price rate computations optimize separate single-memory alternatives, and the panel year conversion treats stocks as independent even though estimation uses a common-date block bootstrap. The quotient is a comparison of two plug-in distances to the null family. The independent-stock conversion is a scenario, not an inferred effective sample size.

### Minor issues and replication

- The archived primary estimates reproduce the individual budget contributions, total feedback and aggregate persistence arithmetic using `p1m_core.effects`. Re-evaluation of the archived price-side single-memory candidate with `p1m_core.kl_rate` gives 1.6815883267e-12. Dividing the archived tagged rate by that result gives 474931.39. The reported calendar conversions reproduce by arithmetic with the archived rate and trading-day count.
- Both archived P1M panel boxes reproduce their halt and aggregate endpoint effects and Whittle-rate constraints to numerical precision. The A1 input digest matches the committed P1M result. A1 Part B effects are archived outputs. Reconstructing the conditional tagged-flow rate, the A1 fits or the reported intervals requires the underlying development panel and bootstrap. The registered holdout was inspected through its archived readout and unlock log only.

### Recommendation and what would change it

**Major revision.** Retain the calibration if the printed inferential claim matches the Whittle proxy and the local search. Supply pinned panel provenance and an admissible replication route. Stronger claims need finite-record control and a separate causal design.

## Referee D — Editor and literature

### Summary

The subject fits JEDC’s scope on economic dynamics, control and computation. The result deserving that audience is the combination of feedback-market information limits and a narrowly specified supervisory decision. The abstract and conclusion run ahead of the manuscript’s assumptions. The statistical ingredients are too familiar for the economics to remain so lightly grounded.

### Major issues

- **D01 · title, pp. 2–4, 15 and 20, Section 1.1, Theorems 5.1–5.2 and 7.9.** The related work is extensive yet the comparison is often a list. Brock and Hommes endogenize selection among predictors by fitness, while this manuscript’s baseline fixes rules and masses. Heinrich and Kahn study local mixture estimation under strong identifiability, and Donoho treats linear-functional estimation in convex Gaussian inverse experiments. Explain what the paper adds through market feedback and who can implement which contract. For regulation, compare concrete institutional mechanisms and distinguish a fixed-test best response from strategic public-information models. [Brock and Hommes (1998), JEDC](https://doi.org/10.1016/S0165-1889(98)00011-6) · [Heinrich and Kahn (2018), Annals of Statistics](https://imstat.org/publications/aos/aos_46_6a/aos_46_6a.pdf) · [Donoho (1994), Annals of Statistics](https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/SEOR.pdf).
- **A04, B02 and C02 · title, pp. 1–3, 23, Theorems 5.1–5.2 and Section 7.4.** “Prices” currently means both an observable pricing error and a synthetic independent tap measurement. The conclusion then implies standard-rate recovery of the whole kernel and bounded precision for a live uniform intervention. State the informational grant, exact policy assumptions and scope of the calibration where the result is first presented.
- **A12 · pp. 9, 11–12, 17–18, 24–29, Appendix A.** Requiring the supplement for the main statistical headline is a structural submission problem. Keep the compact main text by removing repetition rather than leaving the inferential argument out.
- **D03 · pp. 17, 24, 29 and S-60–S-66, machine-check coverage.** “Uniqueness included” reads as existence plus uniqueness. The Lean uniqueness declaration compares supplied minimizers. The supplementary summary must match the formal hypotheses and identify which arguments are supplied on paper. The contribution statement says all authors approved the final manuscript while the declaration identifies unchecked corrections. The author-contribution wording requires author confirmation.

### Minor issues

- **D02 · title, p. 24 and submission materials, journal compliance.** The PDF includes an abstract, keywords, JEL codes, data and AI disclosures. The publisher’s general AI policy was accessible. The journal-specific Guide for Authors returned HTTP 403, so current highlights, source upload and data deposition requirements could not be verified from that page. The package should pin a durable replication version and the corresponding author should confirm the live submission requirements. [JEDC Guide for Authors](https://www.sciencedirect.com/journal/journal-of-economic-dynamics-and-control/publish/guide-for-authors) · [Elsevier generative AI policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals).
- **B03 · pp. 4, 19, Proposition 7.8.** Stable customer IDs are an institutional analogy. They are no warrant for the paper’s perfect owner link. [SEC CAT exemption, 2025](https://www.sec.gov/newsroom/press-releases/2025-38-exemption-requirement-report-certain-personally-identifiable-information-consolidated-audit-trail).

### Recommendation and what would change it

**Major revision.** I would consider a narrower JEDC paper after the headline proof and observation-contract repairs, a clearer comparison with the closest models, and author verification of the submission materials.
