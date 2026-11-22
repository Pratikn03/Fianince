# Two simulated referee reports on the JEDC submission version (21 November 2026)

**What these are.** Two separate AI agents (Claude), each told to act as a demanding JEDC referee, read
`Paper1_JEDC_submission.pdf` (commit 5278582) independently and wrote the reports below. They are **AI-simulated
reports, not independent human review**, and they must not be described as peer review anywhere.

| | Referee A | Referee B |
|---|---|---|
| Recommendation | Reject | Reject |
| Stated chance of eventual acceptance at JEDC | about 5% | about 5% |
| Errors found in the mathematics | Theorem 7.8 uses the wrong exponent; Proposition S4.5 uses a pair the paper's observer can tell apart; Taiwan targeted range equals the box by construction | Theorem 7.8 uses the wrong exponent (computed slopes 2.2 / 4.4 / 5.9) |
| Single change that would most raise the chance | one new economic result proved entirely in the submission | a ~35-page paper on which supervisory instruments can be calibrated from prices |

The response, item by item, is in `REFEREE_RESPONSE_20261121.md`.

---

## Referee A

**Referee report: "Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What Supervisors Need" (submitted to JEDC)**

**1. Summary**

The paper studies a linear market in which K groups of feedback traders trade on exponentially weighted averages of a public pricing error. Price impact is κ and persistence is a. The main results are as follows.

- **Sufficiency (Thm 3.1).** The population enters every public outcome only through the aggregate kernel k_m = Σ w_i r_i^m.
- **Identification (Thm 3.2).** Noiseless probe responses identify the merged rate–weight measure.
- **Equilibrium (Thms 4.1, 4.3).** An overlapping-generations CARA dealer equilibrium reproduces the same closed loop, with effective parameters ā/D and κ/D and unchanged memory rates.
- **Cost of composition (Section 5).** This section imports the near-colliding-mixture rate. Gauss and Gauss–Radau populations need N ≍ σ²(∆η)^(−(4K−2)) reset experiments to be told apart. The section adds a passive analogue, a smooth-family lower bound (Thm 5.4), a local upper bound (Thm 5.5) and a modulus characterization of cheap linear questions (Thm 5.2).
- **Detection and forecasting (Section 6).** The Gaussian KL divergence between two candidate records equals cumulative excess forecast loss.
- **Supervision (Section 7).**
  - A uniform cut depends only on the feedback budget, while a targeted halt needs composition (Prop 7.1, Cor 7.2).
  - When labels carry no information, uniform policies are minimax (Thms 7.3, 7.5).
  - A costly-relabeling disclosure game is solved in closed form (Prop 7.7).
  - A hiding game yields a "surveillance paradox" (Thm 7.8).
- **Taiwan calibration.** Using Taiwanese institutional flows, the paper concludes that prices fix a uniform cut but cannot attribute feedback to trading classes.

**2. Assessment of the contribution**

The authors say the rate is borrowed, and it is.

- The moment-matching construction and the exponent come from Heinrich and Kahn (2018) and Wu and Yang (2020).
- The weight error σN^(−1/2)(∆η)^(−(2K−1)) is the cluster-amplitude rate SRF^(2ℓ−1)ε of Batenkov, Goldman and Yomdin (2021).
- The closed-loop wrapper is routine: the map from response taps to kernel taps is triangular and polynomial, with Lipschitz constants that do not depend on ∆η.
- The 1/log N rate for completely monotone memory is the classical severe ill-posedness of Laplace inversion (Bertero, Boccacci and Pike, 1982). The ill-conditioning of exponential fitting is Lanczos's (1956) textbook example. Neither is cited.

Most of the results presented as new are elementary:

- Theorem 3.1 is an induction showing that a fixed causal linear map is determined by its kernel.
- Theorem 3.2 is partial-fraction realization theory.
- Theorem 6.1 is the chain rule for equal-variance Gaussian conditionals.
- Theorems 7.3 and 7.5 are the finite-group invariance argument, the easy case of Hunt–Stein.
- Proposition 4.4 and Corollary 7.4 restate earlier results.
- Proposition 7.7 is a standard linear-quadratic costly-falsification problem. Its qualitative conclusion, that the principal should under-use a manipulable signal, is close to Frankel and Kartik (2022) and Perez-Richet and Skreta (2022), which are not cited.

What remains is the Section 4 equilibrium mapping, the near-instability bound and the hiding game. This is modest, and the last two have the problems described below. The policy message is that aggregate remedies can be calibrated from aggregates while targeted remedies need identity data tied to owners. That message is intuitive and is already the design principle of the Consolidated Audit Trail.

The residual contribution does not meet the JEDC bar.

**3. Major concerns**

**3.1 Theorem 7.8 rests on a divergence that the paper's own results contradict.**

The theorem defines J as the divergence between records "with the group at distance D and with the group trading like its neighbour". It sets n = 6 for two groups, citing Theorem 5.1. But the D⁶ in Theorem 5.1 is the divergence between two different moment-matched two-group compositions. That measures how hard it is to estimate weights, not how hard it is to tell a two-group economy from the merged one.

- **The stated comparison.** If one group moves to distance D from a fixed neighbour, the first moment of the merged measure changes at order D, so the divergence is of order ND².
- **Against the closest single-group economy,** the divergence is of order ND⁴. This matches the paper's own Theorem S2.3(ii).

I computed Whittle divergence rates for this comparison (a = 0.3, κ = 0.5, neighbour at 0.5, weights 0.05 each, D from 0.1 down to 0.0125). The log-log slopes are 2.14 against the merged neighbour and 4.18 against the best single group, not 6.

- With n = 2, part (i) fails, because complete hiding becomes optimal for large N.
- With n = 4, the rates in part (iii) change.

The authors need to specify the detection problem: the null and alternative hypotheses, whether they are simple or composite, and the test. They then need to derive a power function that depends on D only through ND^n.

There is also a conflict with Theorem 7.3. That theorem says that without tags, labels carry no information and targeting is pointless. So the action that imposes the loss L on an untagged group once it is "detected" must be modelled.

Finally, the test is held fixed and the neighbour does not respond. "Equilibrium identification rate" therefore describes one group's best response, not an equilibrium.

**3.2 The near-instability claim (Prop S4.5, p. 11, Fig. 1) uses a pair outside the paper's own observer model.**

The pair holds the budget at 1 − S = ε by giving the two economies different persistences a. But the paper's observer knows a and κ (p. 5), so this pair is not admissible for that observer. Figure 1(b) itself shows the information rising sharply when a is held common.

Steps 1–3 of the proof are correct, and the result can be repaired. Rescaling the mass of one economy by 1 + O((∆η)^(2K−1)) gives a pair with common a and common budget, whose largest weights still differ at order one. I checked this for K = 2, ∆η = 0.1, r_c = 0.5, total weight 0.15 and κ = 0.5:

| Pair | Divergence rate per observation as 1 − S goes from 10⁻¹ to 10⁻⁵ |
|---|---|
| Rescaled pair (common a, common budget) | stays between 6.2×10⁻⁸ and 8.4×10⁻⁸; spacing slope 5.84 |
| Gauss/Gauss–Radau pair with common a | rises from 1.0×10⁻⁷ to 5.0×10⁻⁵ |

Please restate the proposition with an admissible pair and prove it.

**3.3 The bounds match only under an artificial observation contract, and the "cheap" side is assumed rather than shown.**

- **Reset contract.** Theorems 5.1(ii), 5.5 and 4.3(iv) ("N* ≍ σ²(∆η)^(−(4K−2)) in equilibrium") assume independent reset experiments with i.i.d. Gaussian noise added to the impulse response. That contract is unavailable in a running market. It is also absent from the Section 4 equilibrium, where the only noise ξ drives prices, so the noise is coloured and depends on the hypothesis.
- **Passive data.** Only the lower bound is proved. The running-market upper bound is deferred to an unrefereed working paper (2026d, Thm S16.1).
- **Price records.** Theorem 5.2 concerns kernel taps. For price records it holds only "to first order" (Section S10), and the log rate for the budget is in another paper (2026b).
- **Memory bound.** Theorem 5.2(iii) with g(r) = 1/(1−r) implies something stronger. Without a known memory bound r̄ < 1, a group with memory near one and negligible weight can move S across [a, 1) at bounded divergence. "A uniform cut can be set from prices" (abstract) therefore requires an a priori memory bound, and the abstract and Proposition 7.1 should say so.

**3.4 Hidden or under-emphasized assumptions.**

- The rates require exponential memory, linearity and a known K. With unknown K the local rate changes.
- The reported years assume Gaussian news. Those are the largest possible lower bounds; they shrink by the factor σ²I_f. That factor is large for returns with kurtosis near 19 (Section S13). Table 1 and the abstract should say this.
- The model requires a public fundamental, so that traders and the supervisor both observe x.
- Groups carry no idiosyncratic shocks. Such shocks add a second aggregate object (Section S8).
- In Section 4, the share 1 − ā of dealer inventory is laid off to an unmodelled counterparty, and probes are priced as noise.

**3.5 The Lean checks cover less than the text implies.**

- **Theorem 6.1.** The declaration `dual_end_to_end` takes the one-step Gaussian divergence, the chain rule, Pinsker's inequality and the testing inequality as hypotheses. It verifies only scalar algebra, so "machine-checked end to end" (p. 16) is inaccurate.
- **Theorem 7.8.** Four scalar inequalities are checked. The game, its optimum and its probabilistic inputs are not.
- **Taiwan calibration.** The checked lemmas (`halt_geometric`, `relabel_kernel`, `whittle_integrand_nonneg`, `pinsker_record_length`) are elementary identities. No part of the calibration's actual computation is verified.
- **Theorem S4.1.** The checked pair is a binomial pair; the Gauss/Gauss–Radau pair is checked only at K = 3.
- **Theorem S4.4.** The divergence rates and the stationary limit are unchecked.

By contrast, the formalization of Theorem S4.2 (the Prony upper bound with sub-Gaussian noise) appears substantive and deserves credit.

The main text should state exactly what each formal statement covers, and drop "end to end" and "in full" wherever the content is unformalized probability. The 14,400-economy numerical check of Theorem 7.3, which is a two-line Jensen argument, should be removed.

**3.6 The Taiwan calibration does not measure the paper's mechanism, and its key range is an artefact.**

**(a) The targeted range equals the box by construction.** The set of compositions treated as indistinguishable allows signed class weights and free rates, subject only to |H′_c| ≤ h̄. If two classes share one memory rate with large opposite weights, the aggregate kernel is exactly unchanged, so H′_Foreign can be placed anywhere in the box.
- Using the Table 2 estimates with an AR(1) stand-in (the paper's own p = 1 run reports the same ranges), I let Foreign and Trust share rate 0.41 with H′_Foreign = ±0.028, and let Dealers absorb the 0.35 and 0.33 atoms.
- This costs 2.7×10⁻¹⁵ nats per stock-day, about 4×10⁻⁸ of the J₀/n budget.
- The reported ranges (±0.028 and ±0.0027) are therefore ±h̄ by construction, and "127 times narrower" is set by h̄.
- The phenomenon is signed-measure non-identifiability, not the positive-weight near-collision of Theorem 5.1. Please recompute on a class the theory covers (bounded weights, minimum separation between class memories) and report how the range scales with h̄.

**(b) The tagged interval rests on a restriction the counterfactual drops.**
- Table 2's H_c = κw_c/(1−r_c) ties each feedback kernel's decay to the class's own flow persistence, so r_c is identified mainly by flow autocorrelation.
- The counterfactuals instead hold non-feedback flow fixed and let feedback memory vary freely (pp. 23–24).
- Under that model, the paper's own Q1 calculation (at least 5,738 years per stock) says that tagged flows carry little information about feedback memory.
- "Tags give 0.0014 [0.0012, 0.0016]" therefore compares a restricted tagged estimate with an unrestricted price-only set. Please show that the interval survives a decoupled specification, for example distributed lags of x plus ARMA non-feedback flow.

**(c) The "price deviation" is not the model's pricing error.** The paper does not define it. Per the cited protocol, it is the market-adjusted log price minus its trailing 60-day mean. Its persistence (Σa_j = 0.97) is largely mechanical, and the registered test could not distinguish w_c from prices revealing past flow.

**(d) The barrier reflects a weak signal, not near-collision.** κ = 0.0038 and the three classes contribute 0.0017 to a budget of 0.97. The barrier comes from this low signal-to-noise ratio, not from near-collision of memories (0.33, 0.35, 0.41). At this magnitude no ceiling decision depends on composition.

**(e) Assumptions are inconsistent.** The panel record length treats the 300 stocks as independent, although the date-block bootstrap is used precisely because they are not. The "price-only" supervisor is also handed κ and the law of non-feedback flow, both estimated from tagged data. None of this calibrates Theorems 5.1 or 6.1.

**3.7 Self-containment and overclaiming.**

The main text relies on at least a dozen results from unrefereed companion papers (2026a–d) and a thesis described as "in preparation", including S6.7, S16.1, S16.2, S18.2, S29.1 and C2.1. Anything the main text uses must be proved in the submission.

The text also overclaims:
- "Which is why a uniform cut can be set from prices" (p. 2) does not follow from Theorem 6.1.
- "Supervision does not converge to knowledge of composition however long the record" (p. 22) inherits the problem in 3.1.
- The abstract's Taiwan sentence omits the reverse-causality finding.

At 95 pages with roughly 30 formal results, the paper reads as a research programme, not an article.

**4. Minor comments**

1. The sentence "Without tags, a uniform policy is minimax…" appears twice on p. 2. "The equilibrium identification rate is negative" is not meaningful.
2. Theorem 4.1(iv) is stated in terms of G(1) alone. The supplement correctly requires sup over |D−1| ≤ δ of |G| + |G′| to be small.
3. Theorem 5.5 needs an exact global minimizer over a nonconvex set. Put this computability caveat, and the dependence of the constants on γ and ω_min, into the statement.
4. Lemma S9.1(i)–(ii) is classical quasi-orthogonal quadrature with Christoffel numbers (e.g., Gautschi, 2004). Please cite it.
5. Theorem 7.3 is formalized for deterministic policies only. State the extension to record-dependent rules, which follows because the law of the record does not depend on the labelling.
6. Fig. 1(b): with a common a, the divergence saturates once 1 − S falls below the O((∆η)^(2K−1)) budget gap. It does not "grow without bound".
7. Notation clashes:
   - x_t is the pricing error, but the insider's order in Section S2.
   - S is the budget, a class label and a node set.
   - a is both persistence and −n_H.
   - σ is both a noise standard deviation and a labelling permutation.
   - ∆ is both a spacing and a discriminant.
8. Theorem 7.8(iv): with tags, the relevant information comes from the tagged flow, not from cND₀ⁿ.
9. At least fourteen listed references are never cited (Modigliani–Miller, Brunnermeier–Pedersen, Barroso et al., Fan, Kong–Valiant, Rivlin, Guo–Ljung, Hua–Sarkar, Roy–Kailath, Ing–Wei 2003, …), and the list is not alphabetized.
10. Please engage the JEDC literature on estimating heterogeneous-agent models (Grazzini and Richiardi, 2015; Kukacka and Barunik, 2017) and the literature on trader anonymity (Foucault, Moinas and Theissen, 2007; Comerton-Forde and Tang, 2009).
11. Remove revision history from the supplement ("earlier versions of this table", "the incoming optimizer simulation", "this revision").

**5. Results checked in detail**

- **Theorem 5.1(i) / S4.1: correct.** Using C(m,j) ≤ C(m,n)·C(m−n, j−n), I get ‖∆k‖₁ ≤ 2W(∆η)^(2K−1)/(1−r_c−∆η)^(2K) and ‖∆h‖₁ ≤ κ²‖∆k‖₁/(1−ς)². The first differing tap is ∆h_{2K} = κ²W g_K (∆η)^(2K−1). The constant g_K = 4^K/(K·C(2K,K)²) reproduces 0.222, 0.0533 and 0.0131.
- **Theorems 4.1(i), 4.1(iv) and 4.3(i): correct.**
  - Matching coefficients gives β_i = κ/(D−r_i), D = 1 − κG(D), κ(D−ā) = AVD, and an innovation of κξ/D.
  - The implicit-function derivatives ∂_DΦ₂ = κ₋(ā + 2Aκ₋σ_ξ²) and ∂_κΦ₂ = √∆ reproduce the stated slope.
  - The pathwise reduced form with w̃_i = w_i(D−ā)/(D−r_i) checks.
- **Proposition 7.7: correct.** Welfare under tags is mx + χ(ad − d²/(2g)). All four cases follow, and the hiding share a/(2a+b_H) lies strictly between 0 and 1.
- **Theorems 6.1, 7.3 and 7.5: correct but elementary** (see Section 2).
- **Theorem 7.8:** the algebra is correct, but its premise is wrong for the stated comparison (3.1).
- **Proposition S4.5:** the steps are correct, but the pair is not admissible for the paper's observer (3.2).

**6. Recommendation: Reject**

- The statistical core is borrowed.
- The new results are either elementary or rest on flawed premises (Theorem 7.8, Proposition S4.5).
- The calibration's headline range is an artefact of the box constraint.
- The paper is not self-contained.

A short paper built on one genuinely new economic result, proved in full, would deserve a fresh look.

**Confidential comments to the editor**

The authors are careful in places, and the formalization of Theorem S4.2 is real work. Even so, the manuscript is a compilation. At least four overlapping working papers (2026a–d) and a thesis share its material, and 2026a ("What prices cannot tell a market supervisor: the cost of identifying trader groups and the value of class disclosure") appears to cover the same core. Please check the overlap before any resubmission. The AI-use declaration says that Proposition 7.7, Theorems 7.3, 7.5 and 7.8 and Corollary 7.4 were developed on 21 November 2026, the manuscript's own date, with proofs checked by the first author. I found a foundational error in one of them (Theorem 7.8), so the paper has not stabilized. I put the probability that this paper is eventually accepted at JEDC at about 5%. The single change that would most raise it is to rebuild the paper around one new economic result proved entirely within the submission. For example, the relabeling game could be embedded in the Section 4 equilibrium, so that the supervisor's information and the traders' hiding are determined together. The mixture rate should then be reduced to a cited lemma and the Lean rhetoric removed from the main text.

---

## Referee B

# Referee report

**"Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What Supervisors Need"**

## 1. Summary

The model has K groups of feedback traders. Each group trades in proportion to an exponentially weighted average of a pricing error. Price impact is κ and arbitrage persistence is a. The population enters prices only through the merged measure M = Σ wᵢ δ_{rᵢ}, whose moments form the "feedback kernel".

The main results are:
- **Sufficiency (Theorem 3.1).** Equal kernels give identical price, flow, insider-profit and inventory paths, for arbitrary causal insider and dealer rules.
- **Identification (Theorem 3.2).** Probe responses identify M.
- **Equilibrium (Theorems 4.1, 4.3).** Both results survive in an equilibrium with CARA dealers who dislike holding inventory.
- **Cost of composition (Theorems 5.1–5.5).** Separating K groups whose memories lie within Δη takes order (Δη)^{-(4K-2)} observations, which is the known mixture rate. Linear functionals with square-summable power-series representations cost only σ²ε⁻².
- **Policy (Section 7).** Four claims:
  - A uniform scaling of feedback depends only on the aggregate, but halting the largest group does not.
  - Uniform policies are minimax when labels are uninformative.
  - Class tags remove the barrier but lose value when relabeling is cheap.
  - Untagged groups "crowd" together, so the supervisor's information falls as the record grows.

A calibration on Taiwan's daily institutional flows illustrates the barrier.

## 2. Assessment of the contribution

The question is a good one: what can a supervisor learn from prices about who trades, and which interventions need that knowledge? The authors are commendably candid about limitations.

Two pieces are, to my knowledge, new and economic:
- **Theorem 4.3.** Dealers' anticipation leaves memory rates as transmission zeros but reweights groups by (D−ā)/(D−rᵢ). Persistent feedback is therefore over-represented in equilibrium prices.
- **Theorem 5.2.** It characterises which linear supervisory questions are cheap: exactly the H² functions of memory. Corollary 5.3 then separates market-wide questions from questions about composition.

Most of the other results are known or elementary:
- Theorem 3.1 is an induction showing that an aggregate is sufficient when only the aggregate enters.
- Theorems 3.2 and S4.3 recover a rational transfer function from its impulse response or minimum-phase spectral factor. This is classical systems identification (Hannan and Deistler, 1988; Komunjer and Ng, 2011), though the point that memories are zeros, not poles, of the price response is useful.
- The rate is borrowed (Heinrich and Kahn, 2018; Wu and Yang, 2020), as the authors acknowledge.
- Theorem 6.1 is the Kullback–Leibler chain rule for Gaussian conditionals.
- Theorem 7.3 is symmetrisation plus Jensen's inequality.
- Theorem 7.6 says that observing the components removes a deconvolution problem.

The organising message is that market-wide policies need a reduced-form aggregate while targeted ones need structure. That is Marschak's (1953) maxim and the sufficient-statistics logic (Chetty, 2009), applied to a linear heterogeneous-agent model. This is legitimate. As delivered, however, the distinction has no bite for any policy the paper models (concerns 1–2), and the empirics do not support the mechanism (concern 7). The insight does not yet justify publication in JEDC.

## 3. Major concerns

**1. The uniform cut is neither market-wide nor generally identified from prices.**
- **It needs a.** Proposition 7.1(i)'s effect θ(S−a) requires a, and every result assumes (a, κ) known (p. 5).
- **Knowing a is itself a composition question.** Corollary S7.2(i) shows that a acts exactly like a zero-memory feedback group. The uniform cut is therefore the functional g(r) = 1{r>0}/(1−r) of (a/κ)δ₀ + M, which is discontinuous at zero.
- **A concrete pair.** Take one population with weight w on memory ε, and another with that weight absorbed into a. Their kernel taps differ by O(wε), but their uniform-cut effects differ by κw.
- **So it is not cheap where it matters.** By the logic of Theorem 5.2, the question cannot be answered uniformly once short-memory traders are present. That is exactly the case of algorithmic traders sampled daily, and it is why Corollary S7.2 assumes all memories are at least ε > 0.
- **The instrument is itself targeting.** It must scale feedback traders while sparing arbitrageurs and dealers.
- **Real instruments look different.** Transaction taxes, minimum resting times, order-to-trade limits and circuit breakers have horizon-dependent incidence, so their effects are ∫θ(r) dM/(1−r). Classifying such instruments with Theorem 5.2 would be a real contribution.

**2. The composition barrier never binds for a modelled policy.**
- **Without tags.** A halt of "the largest group" cannot be executed; the supplement itself says "a largest latent atom alone supplies no such identity" (p. S-12).
- **With tags.** Theorem 7.6 removes the barrier.
- **The only case where it matters is unmodelled.** The (Δη)^{-(4K-2)} cost that fills Sections 5–6 matters only when the supervisor can enforce against labels yet has no records linking labels to flows. That is Theorem 7.3's setting. It needs explicit motivation (for example, rules aimed at categories of traders in fragmented markets that lack a consolidated audit trail) and a model, because whoever enforces against a label usually sees at least part of its trading.
- **Where the barrier does bite.** It bites for behaviour-based rules, such as restrictions by horizon with incidence 1{r<r̄}. This is close to Corollary S15.3 and should be the paper's centre.

**3. Model assumptions.**
- **Fixed rules.** Rules are fixed and non-strategic. Theorem 3.1's "same equilibria" therefore concern games in which the traders of interest are not players.
- **The trading signal.** Traders respond to deviations from a public fundamental (Section 4). That is an unusual signal for "algorithms", which in practice condition on returns and order-book state.
- **Not Brock–Hommes in substance.** There is no strategy switching, so the defining nonlinearity of the Brock–Hommes framework is absent. Estimated heterogeneous-agent models also find types that are far apart, not near-colliding.
- **Price impact.** Section 2 concedes that a Kyle-type dealer nets predictable flow out, leaving prices uninformative. The inventory equilibrium restores impact, but the dealers' lay-off rate 1−ā is exogenous, so persistence is not "derived" (pp. 1, 7).
- **Investor classes, not algorithms.** The empirical classes are types of investor. The title and abstract should match what is modelled.

**4. Overclaiming.**
- Page 2 presents "what a record reveals… equals the forecast loss from confusing them" as a new economic result. Page 16 calls it the Gaussian chain rule. It is also not the reason a uniform cut can be set from prices; Proposition 7.1(i) is.
- "The minimax supervisory policy" (abstract) holds only over labellings, for losses that depend on the budget alone and costs that ignore labels.
- The "equilibrium identification rate [that] is negative" (p. 2) is not an equilibrium. Section S11.2 admits that the test is fixed and the neighbour does not respond.
- "Only audit trails that link accounts to owners escape the problem" is assumed, not derived (concern 6).
- "Prices pin down a uniform cut" in Taiwan does not hold (concern 7).

**5. Theorem 7.8 uses the wrong exponent.** The theorem takes the divergence between "the group at distance D" and "the group trading like its neighbour" to be cND^n with n = 6 (or 4K−2), citing Theorem 5.1. But Theorem 5.1 concerns two moment-matched K-group populations, which is a different test.

I computed stationary Gaussian divergence rates in model (1): a = κ = 0.5, neighbour memory 0.6, weights 0.05, D from 0.1 to 0.0125. The fitted exponents are:
- **2.2** for the comparison as stated (simple null);
- **4.4** against the closest one-memory population (composite null), consistent with the paper's own Theorems S2.3(ii) and S4.4(i);
- **5.9** only for the Gauss/Gauss–Radau pair.

I then solved the group's problem at the authors' parameters (k = D₀ = c = 1, L = 50, α = 0.05, Gaussian Neyman–Pearson power):
- **n = 2:** D* = 0 for every N from 10² to 10¹², so part (i), "hiding is never complete", fails.
- **n = 4:** J* ∝ N^{-1.00}.
- **n = 6:** J* ∝ N^{-0.50}, the stated rate.

The headline N^{-1/2} therefore rests on an exponent that is not derived for this game.

The welfare reading is also doubtful. If D₀ is the conduct the supervisor fears, driving D* to zero is successful deterrence, not a paradox, and "tags reverse it" means tags let the group keep D₀. The authors should:
- specify the supervisor's objective;
- relate the result to Bond, Goldstein and Prescott (2010) and Bond and Goldstein (2015), where intervention based on prices degrades their informativeness;
- relate it also to Frankel and Kartik (2019).

**6. Proposition 7.7 is correct, but its conclusions are built in.** I verified the closed forms. However:
- **The ranking is assumed.** Tags can be gamed at cost γ while the audit trail is assumed ungameable, so V_C < V_A for all γ follows immediately.
- **The game is narrow.** Only the restricted class relabels, and there is one cycle.
- **It is detached from the market model.** The social values n_H and n_S have no connection to the kernel, the memories or the budget.
- **The live policy debate is missing.** The SEC's February 2025 order exempted reporting of natural persons' names, addresses and years of birth to CAT, while CAT keeps generating consistent anonymised customer identifiers. By Proposition 7.7's own logic, what matters is a stable pseudonymous link to the owner, not personal data.
- **MiFID II algorithm identifiers** are self-assigned labels, exactly the gameable kind that Corollary S15.3 describes.

**7. Taiwan calibration and registered tests.**
- **(a) Missing definitions.** The pricing error x_t is defined neither in the text nor in S19. Nor are the units of flow (and hence of κ = 0.0038), or how the 300 stocks were selected.
- **(b) The uniform cut is granted, not learned.** The supervisor is "granted the market's impact function and the law of non-feedback flow" (p. 23). That includes the AR(5) coefficients a_j, which were estimated using the tagged flows. Separating 0.0017 of feedback from 0.97 of own persistence is exactly concern 1. With memories near 0.35, nearly all of the feedback kernel sits on the first five lags, where it is confounded with the a_j. "Prices pin down a uniform cut" is an artefact of this grant.
- **(c) Feedback is not established.** The authors' registered diagnostic (S6) attributes the estimated response to prices revealing past flow. Table 2 therefore does not estimate feedback rules.
- **(d) The signal is negligible.** Even at face value, the classes contribute 0.0017 to a budget of 0.97. The astronomical record lengths reflect a near-zero signal, not near-colliding memories, and the policy question is moot in this market.
- **(e) The tagged-flow information figure does not reconcile with model (1).** The paper reports 8×10⁻⁷ nats per stock-day.
  - In model (1), each class's flow is an AR(1) with coefficient r_c. Any common decay lies at least 0.04 from one of the estimates. With Gaussian innovations, that carries about 0.04²/[2(1−0.41²)] ≈ 10⁻³ nats per stock-day, a thousand times more than reported.
  - Conversely, 270,060 × 8×10⁻⁷ ≈ 0.22 nats would, by Pinsker's inequality, cap the power of any 5% test near 0.38. Yet Table 2's persistence intervals for foreign investors [0.31, 0.38] and investment trusts [0.39, 0.43] do not overlap.
  - Please state which components are held fixed. If non-feedback persistence is held at r_c, then r_c is not the feedback memory of model (1).
- **(f) Independence.** Treating the 300 stocks as independent conflicts with the date-block bootstrap used for Table 2.
- **(g) Prior literature.** Positive feedback in daily foreign flows, and the reverse-causality problem, are documented, including for Taiwan (Richards, 2005; see also Froot, O'Connell and Seasholes, 2001; Griffin, Nardari and Stulz, 2004). None of this is cited.
- **(h) Registration.**
  - Pending tests (P1F, which cannot be analysed before January 2027, and H1) do not belong in a submission.
  - A protocol written after its sample period (P7S) is not a pre-registration.
  - Protocols kept in the authors' own repository are not independent registration.

**8. Positioning.** Beyond the works above, the paper should engage with:
- inventory-based impact: Ho and Stoll (1981); Grossman and Miller (1988); Hendershott and Menkveld (2014);
- feedback trading: De Long et al. (1990); Cutler, Poterba and Summers (1990); Sentana and Wadhwani (1992); Chiarella, He and Hommes (2006);
- estimation of heterogeneous-agent models: Chiarella, He and Zwinkels (2014); Grazzini and Richiardi (2015); Platt (2020);
- identification: Rothenberg (1971);
- decisions under ambiguity and invariance: Manski (2000); the Hunt–Stein theorem;
- crowding: Chaboud et al. (2014); Khandani and Lo (2011); Stein (2009).

**9. Length and organisation.**
- **Size and dependencies.** The paper runs to 95 pages with 19 numbered main-text results, and it leans on four companion manuscripts and a thesis in preparation. Several main-text claims rest on results not submitted (e.g., Niroula et al. 2026d, Theorems S6.1 and S16.1, Proposition S16.2).
- **Broken cross-references.** S6 says S12 "settles several earlier open questions", but S12 is the moment-gap section. Numerical checks are attributed to "Section S21, reproduce.py", which is the Lean table.
- **Repetition.** The introduction states the minimax result twice in one paragraph.
- **Bibliography.** Over a dozen entries are never cited (e.g., Modigliani–Miller, Brunnermeier–Pedersen, Barroso et al., Kong–Valiant, Cesa-Bianchi–Lugosi), and the list is not alphabetised.
- **Apparatus.** Lean declaration names, script names and protocol file names belong in a replication appendix.
- **Hedging.** Pervasive hedging obscures what is actually claimed.

A 30–35 page paper with one model and three or four results would serve readers better.

## 4. Minor comments

1. Abstract: "needs of order" is ungrammatical, and the abstract should say the bound is a worst case over pairs.
2. Theorem 7.3:
   - "Weakly dominated" (p. 18) is the wrong term. The uniform policy is minimax, and Bayes under an exchangeable prior, but it is not dominant state by state.
   - Labels never enter prices, so no theorem is needed to show that records cannot distinguish them.
   - The minimax half extends to quasi-convex ℓ and C, which covers the paper's own ceiling loss (Proposition 7.1, Corollary 7.4); the Bayes half does not.
3. Monte Carlo "checks" of results proved by Jensen's inequality (14,400 and 1,200 economies) add nothing.
4. The "a fortiori" in Remark 4.2 covers only the lower bounds. The positive claims require the pricing error to be observed.
5. Notation is overloaded:
   - Δ is both a discriminant and a spread;
   - D is both the dealer root and a distance;
   - a is both persistence and −n_H;
   - σ is both a labelling and a noise level;
   - x_t is the insider's order in S2.
6. Taiwan's dealers have w_c < 0. Results proved for the positive economy (Lemma S7.1, Proposition S5.2, the S < 1 criterion) therefore do not apply to the calibration.
7. Report the price-equation estimates and fit alongside Table 2.
8. Proposition 4.4 and Corollary 7.2 are two-point bounds and could be remarks.
9. Readers cannot verify Theorem 5.2's attribution to a thesis "in preparation", or Φ's log lower bound attributed to another working paper.

## 5. Detailed checks

**Theorem 3.1 / S2.1 (sufficiency).**
- The strong induction is correct: signals, flows, insider orders, total flow and price agree in turn.
- Feedback states are functions of the public history from a zero state, so continuation games coincide and refinements also agree.
- The result is correct but definitional. Its equilibria exclude the feedback traders, and the extension to "any population, linear or not" (p. 6) cites a manuscript that was not submitted.

**Theorem 7.3 (uniform policies are minimax).**
- The proof is correct. Each class carries each label in (K−1)! of the K! labellings, so the average budget is a + θ̄U. Jensen's inequality, symmetry and convexity then give both inequalities.
- The statement is accurate; the gloss around it is not (minor 2; concern 2).

**Theorem 7.8.**
- Given J = cND^n with n > 2, parts (i)–(iv) are correct; I re-derived both bounds.
- The flaw is the choice of n (concern 5). The Lean formalisation checks the algebra, not this modelling step, which is exactly where the error lies.

**Also verified:**
- the equilibrium conditions (2) of Theorem 4.1, by coefficient matching and computing the price innovation;
- the closed forms and comparative statics of Proposition 7.7;
- six rows of Table 1, recomputed from the closed-form spectra (20,100; 104; 6,020; 120; 6,960; 1.5×10⁸ years), all matching.

## 6. Recommendation: Reject

The mathematics I checked is largely correct, and two results are interesting. But the central policy claims do not follow from the model:
- the uniform cut requires knowing what counts as feedback;
- the composition barrier binds for no modelled policy;
- the "surveillance paradox" applies the wrong exponent;
- the empirics neither identify feedback nor find it economically relevant.

Fixing this requires a different, much shorter paper.

## 7. Confidential comments to the editor

The manuscript is technically capable but over-extended. It reads as an accumulation of results from a large project, and key claims rest on companion manuscripts that referees cannot evaluate.

The authors' declaration says the main Section 7 results (Proposition 7.7; Theorems 7.3, 7.5 and 7.8) were developed with AI assistance on 21 November 2026, the date on the supplement. That fits their weak integration with the rest of the paper and the exponent error in Theorem 7.8.

The "registered" tests are self-registered, partly retrospective and partly pending, and none supports the mechanism. The authors say so honestly.

My probability that this paper is eventually accepted at JEDC is about 5%.

The single change that would most raise it is a ~35-page paper built around one question: which supervisory instruments can be calibrated from prices? It would combine the equilibrium of Section 4 with Theorem 5.2 to classify real instruments by their incidence across trading horizons, including how to separate feedback from non-feedback persistence. It would drop the borrowed statistics, the Lean and registration apparatus, and the stylised games.

---

**Sources checked for this report**
- [Bond and Goldstein (2015), *Journal of Finance* 70(6)](https://ideas.repec.org/a/bla/jfinan/v70y2015i6p2777-2812.html)
- [Richards (2005), *JFQA* 40(1)](https://econpapers.repec.org/RePEc:cup:jfinqa:v:40:y:2005:i:01:p:1-27_00); [RBA working-paper version](https://www.rba.gov.au/publications/rdp/2004/2004-05/how-are-the-net-purchases-of-foreign-investors-related-to-prior-returns.html)
- [Griffin, Nardari and Stulz (2004), *Review of Economics and Statistics* 86(3)](https://econpapers.repec.org/RePEc:tpr:restat:v:86:y:2004:i:3:p:641-657); [NBER WP 9000](https://nber.org/papers/w9000)
- [Chaboud, Chiquoine, Hjalmarsson and Vega (2014), *Journal of Finance* 69(5)](https://econpapers.repec.org/RePEc:bla:jfinan:v:69:y:2014:i:5:p:2045-2084)
- [Heinrich and Kahn (2018), *Annals of Statistics* 46(6A)](https://projecteuclid.org/euclid.aos/1536307235)
- [SEC press release 2025-38](https://www.sec.gov/newsroom/press-releases/2025-38); [FINRA, "Eliminating All PII from CAT"](https://finra.org/media-center/blog/eliminating-all-pii-from-cat)
