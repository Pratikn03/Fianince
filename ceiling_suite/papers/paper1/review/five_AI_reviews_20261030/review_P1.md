# P1 — AI-assisted internal review: probability, estimation and proofs
**Manuscript:** *What Prices Reveal About Hidden Trader Populations, and What Identifying Them Costs*; PDF dated November 2026, 124 PDF pages. **Basis:** attached PDF, selected independent algebraic checks, and public prior-literature records. **Not** an independent professor, independent model, formal proof certification, or line-by-line verification of all arguments. Pages below are the paper's **printed pages**; add 3 for PDF-page number after the front matter.

## A. Verdict
**Do not post unchanged.** There is a credible mathematical programme here, but a professor should not be asked to absorb a strong uniform, sharp, and novel-sounding set of conclusions when several statements do not specify the loss, class and observation contract tightly enough. The K-component exponent is already a mixture/super-resolution exponent, which the paper does acknowledge; its distinctive claim is the feedback-to-cost transfer, not the exponent. Some derivations can be checked, but the highly consequential spectral capital constants, K-uniform inversion and general-memory bounds require a separate human proof audit. The strongest practical hazard is the blanket language about rates and tagging in the abstract, not a presently demonstrated false theorem.

## B. SSRN readiness
**5.5/10 as posted; potentially 7.5/10 after the corrections below and a genuine independent proof check.** This evaluates whether to send to professors, not journal acceptance. I have **not** established a fatal mathematical contradiction and therefore do not assert one.

## C. Issues

### FATAL
**None VERIFIED in this audit.** That does **not** mean the proofs are certified. If the authors cannot verify the Appendix D optimized trading-loss results, those dollar headlines become FATAL to this version and must be removed.

### MAJOR

1. **Scope of sharp K-rate is too easy to misread — printed pp. 35–37, §5.4; abstract pp. i–ii. SUSPECT (scope and communication, not demonstrated false mathematics).** Quote: “the minimax sample requirement is `N* ≍ σ²(∆η)^−(4K−2)`.” Theorem 5.5 actually conditions on a compact class of **ordered, γ-separated rescaled nodes**, weights bounded below, and a **rich class containing the Gauss/Gauss–Radau pair**. Fix: state that full contract with every headline use: “On specified rich, separated rescaled-rate classes, for fixed weight-estimation accuracy, the minimax number of independent unit-impulse reset experiments is of this order.” Do not use “for every K” as shorthand for every parameter class.

2. **Mismatch between K-loss definitions in headline and proofs — printed pp. 34–37, §5.4. SUSPECT.** Quote: “The same requirement holds for the permutation-invariant loss `W1(M, M̂)` … at accuracy `c_K W∆η`.” That is a **shrinking** Wasserstein target, whereas Theorem 5.5's advertised upper bound is **fixed-accuracy weight recovery**. Their equivalence on the selected lower-bound pair appears plausible but needs an explicit reduction; a reader cannot silently substitute losses. Fix: add a one-paragraph lemma connecting the fixed-weight risk of both quadrature configurations to the lower bound, and display the distinct minimax targets side by side.

3. **Tagging is robust to collisions, not literally invariant to spacing — printed pp. 44–46, §6/§6.1; abstract p. ii. VERIFIED (logical precision).** Quote: “each group an ordinary estimation problem whose precision does not depend on the spacing.” Yet Proposition 6.1's displayed asymptotic variance `V_i = Σ_i^−1 Ω_i Σ_i^−⊤` depends on price autocovariances, which can change when rates move. The proof supports no **singular blow-up as spacing tends to zero under uniform bounds**, not constant variance at every spacing. Fix: “Tagging yields root-T inference with conditioning uniformly bounded as rates collide, under the stated nondegeneracy assumptions.”

4. **Tagged rate loss needs a target constant — printed p. 46, Theorem 6.2(ii). SUSPECT.** Quote: “to recover the rates to accuracy proportional to `∆η`.” A sufficiently large proportionality constant makes a constant-center estimate trivially accurate even with zero observations, so a lower bound cannot hold for **every** such meaning. Fix: define the threshold as `c_0 ∆η` for a specified sufficiently small `c_0>0`, the class and permutation matching, and state the result as a minimax claim at that threshold.

5. **Meaning of experiment and economic sample size — printed pp. 34–37, §5.4. VERIFIED (contract stated, headline broader).** Quote: “an experiment is a unit impulse from the reset state whose response is observed with noise of variance σ² per tap.” This is not weekly prices, continuous observations, or an unrestricted trading strategy. Fix: retain “independent reset” in abstract, conclusion, Tables 1–3 and all economic comparisons; avoid treating a `reset` as a calendar day without validation.

6. **Potential proof gap in Prony's global inversion description — printed pp. 36–37, Theorem 5.5 proof. SUSPECT.** Quote: “there are `ρ0 > 0` and `L < ∞`, uniform over the class, such that `F^-1` exists and is `L`-Lipschitz on the ball … around every point of `F(class)`.” A quantitative *local* inverse-function theorem alone does not automatically give one globally consistent inverse on all those balls, especially across disjoint compact components or overlapping neighborhoods. Global injectivity for positive ordered K-atomic moments is classical and likely repairs this, but the proof should invoke it explicitly and define the admissible inverse/Prony root selection for noisy moment vectors off the moment manifold. Fix: add a global uniqueness lemma, a compactness-and-local-charts argument and an estimator projection/truncation rule on inadmissible noisy inputs.

7. **K-lower-bound source and novelty — printed pp. 7, 10–11, 34–37, §§1.1/5.4. VERIFIED (prior-art existence; exact reduction not independently certified).** Quote: “we do not claim the exponent as new.” This is the correct caveat; however the paper still repeatedly sells the exponent as a central result. Heinrich–Kahn give local finite-mixture minimax rates; Katz–Diab–Batenkov analyze Prony sharpness in near-colliding regimes. Fix: put the source of the statistical exponent in the *abstract or contribution summary*, and present the new claim as the closed-loop reduction plus economic unit/cost contract. Sources: https://arxiv.org/abs/1507.04313 ; https://doi.org/10.1016/j.acha.2024.101687 . Different statistical models: do not say either paper alone proves your precise theorem without deriving the reduction.

8. **The Θ(1/log N) claim has a model-specific constant and asymptotic contract — printed pp. 39–41, §5.5. SUSPECT (full proof unverified).** Quote: “Hence the minimax accuracy is of exact order `1/log(N/σ²)`.” The displayed proof uses fixed `ρ<1`, fixed stability margin, known `(a,κ)`, reset impulses, Gaussian tap noise, *unrestricted* positive mixing measure and Wasserstein-1. It is not a universal rate for arbitrary 'general memory.' Fix: add all these qualifiers to the short-form claim and a paragraph explaining that `ρ→1` is not uniform and finite-K changes the problem. Request independent check of the alternating-measure argument and the polynomial coefficient bound in Appendix A.

9. **Passive KL bound must not be extrapolated to noisy observed returns — printed pp. 42–43, Theorem 5.9. VERIFIED (contract), proof audit still SUSPECT.** Quote: “without observation noise” and “`D = Θ((∆η)^(4K−2))`.” This is for stationary Gaussian price output with one known innovation law; observed prices with microstructure noise, endogenous supply/demand innovations or extra cohort shocks are separate experiments. Fix: repeat 'stationary single-innovation Gaussian model with exact price observations' in conclusions and retain the finite-T Toeplitz proof on printed pp. 77–78. Verify uniform spectral lower bounds under the full signed-weight class.

10. **Capital and losses are contract-dependent — printed pp. 21–26, §4; pp. 87–93, App. D. SUSPECT for sharp optimization; scope VERIFIED.** Quote: “Necessary and sufficient capital orders are `δ^-4`.” This holds only with the stated positive, stable impact/execution law, Gaussian price reading, solvent end mark, and pulse/solvent account protocols. Exact “61.41–64.48 par units” and “within 5%” are computed/optimized constants, not separately proved universal market capital requirements. Fix: mark each constant as **numerically evaluated at a declared parameter set** and ask a separate checker to reproduce the Rayleigh–Hölder dual, frequency-domain bound and feasible finite-horizon ledger before retaining any dollar headline.

11. **Kalman-to-trader identification overreach — printed pp. 14–16, §2. VERIFIED as an interpretive gap.** Quote: “The memory rate encodes the desk’s signal-to-noise ratio or regularization, which is the private information a supervisor would like to recover.” The mapping holds in the stylized filter/gradient model, not for real trading algorithms; a fitted position autoregression is not identification of private signal quality. Fix: “In these two illustrative algorithm families, η is a known function of their tuning parameters.”

12. **Two-cohort result needs no-hidden-label qualifier everywhere — printed pp. 32–33, Theorem 5.2. VERIFIED.** Quote: “as unordered sets the two weight vectors coincide.” The paper commendably supplies a permutation-invariant bound only for a restricted spacing domain and a W1 alternative at smaller spacings. Fix: when describing the `∆^-6` test, explicitly name ordered weight error vs invariant Wasserstein loss; do not imply the exact same risk uniformly for both.

13. **Proof-audit status should be first-page visible — printed front p. iii. VERIFIED.** Quote: “The proofs have been checked by the authors and against numerical computations; they have not yet been independently reviewed or formally verified.” This is candid but a major warning to faculty about a 124-page paper built on new proof variants. Fix: attach a 1-page 'critical lemmas / independent check pending' inventory and avoid 'proof verified' phrasing for numerical recomputation.

### MINOR
14. **Precision of Monte Carlo terminology — printed p. 22, §4.1. VERIFIED.** Quote: “simulated errors match the formula to Monte Carlo precision.” Correct interpretation: illustrative stochastic check, not a proof; label Monte Carlo standard errors and random seeds in the table note. Fix: one sentence.
15. **Notational overloading — printed p. 32, Theorem 5.2. VERIFIED.** Quote: “`w_k` denotes cohort k's trading intensity `q_k`, not the merged weight `q_kη_k` of Section 2.” A proof referee may mistake which moments match. Fix: choose distinct symbols for raw intensity and merged weight globally.
16. **Nonnegative-mode numerical check is not a theorem check — printed p. 15, Lemma 2.3. VERIFIED.** Quote: “held in all 892 stable random positive economies tested.” Retain as illustration after proof, not as supporting a general mathematical quantifier.

## Theorem/lemma/proposition audit inventory — **all 21 numbered results in main text**
`P`=proof is given in manuscript / contract looks aligned on inspection; `?`=needs separate proof check; **none** means independently certified. Printed page first, PDF page in brackets.

| Result | Printed page [PDF] | Exact target and key conditions | Audit |
|---|---:|---|---|
| Lem. 2.1 |14 [17]| Kalman/regularized OGD yield exponential updates; steady-state scalar filtering | P; scalar gain algebra plausible; indexing/timing clarify |
| Lem. 2.3 |15 [18]| Positive stable economy: completely monotone impulse response and price-row gain | ? full spectral mixture proof |
| Thm. 3.1 |19 [22]| Known a,κ; zero state; all common probes; merged measure iff same price response; average-power known pair bound | P/? boundary rates and minimal realization check |
| Thm. 4.1 |21 [24]| Known single vs symmetric split; deterministic probes, Gaussian reading; quantity Θ(δ^-2), power horizon Θ(δ^-4)| P; third-tap identity verified independently |
| Lem. 4.2 |23 [26]| Average linear-book execution; positive stable response yields Toeplitz cost form | ? cash ledger and positive definiteness |
| Thm. 4.3 |24 [27]| Counterparty cash/margin, sharp quantity cap | ? worst-case necessity and units |
| Prop. 4.4 |25 [28]| Exact third equity mark distinguishes known pair | P conditional on noiseless mark |
| Lem. 4.5 |25 [28]| Solvent signed probes yield δ^-4 funded-capital lower order | ? indefinite signed economy excluded |
| Prop. 4.6 |27 [30]| Identified economic primitives for Kalman desks under known mapping | ? mapping, invertibility and nuisance normalization |
| Prop. 4.7 |29 [32]| Intensity/information-quality restriction and resulting identification | ? class-specific sign/monotonicity |
| Prop. 5.1 |31 [34]| Gaussian Cramér–Rao local benchmark | P for regular unbiased estimators only |
| Thm. 5.2 |32 [35]| Two-cluster moment matching, ordered/invariant loss, ∆^-6 bound | P/? loss regimes and reduction explicit |
| Thm. 5.4 |34 [37]| Gauss/Radau positive K-atom pairs, W1 and weight recovery ∆^-(4K-2) lower | P/? lower target uniformity |
| Thm. 5.5 |35 [38]| Rich separated compact rescaled class, Prony upper fixed-weight accuracy | ? global inverse/noisy roots |
| Lem. 5.6 |39 [42]| Alternating extremizers give n-atom moment-matched W1 pairs | ? duality and atom count |
| Thm. 5.7 |39 [42]| Compact ρ<1, known a,κ, Gaussian resets, W1 Θ(1/log N)| ? both constants and finite-sample logarithm |
| Thm. 5.8 |42 [45]| One-innovation stationary spectrum, minimum-phase identification | P/? degeneracies, scale |
| Thm. 5.9 |42 [45]| Passive Whittle divergence and finite-T sample lower | P/? spectral uniformity and exact sampling |
| Prop. 6.1 |44 [47]| Class tagged noisy flow + noiseless observed price, IV root-T | P; det algebra matches structure; constants depend on spectrum |
| Thm. 6.2 |45 [48]| Tagged reset experiments: weights Θ(1), rate accuracy c∆: Θ(∆^-2)| ? loss target constant and class definition |
| Prop. 6.3 |51 [54]| Stylized fixed-cost vs delay choice; middle-band disclosure | P algebraic under assumed loss model |

**Numerical checks independently reproduced in this audit (not the whole program):** Theorem 4.1's third impulse tap changes by `−κ² qδ²` between a symmetric split and its center (from direct two-step recursion). At `(κ,q,δ)=(0.8,0.2,0.05)`, this is `−0.00032`, agreeing with printed p. 22. Gauss vs Radau with K=2 and normalized Legendre weights has moment-3 gap `2/9 = 0.222222…`, consistent with Table 7 on p. 35. These checks are not a validation of the reported fitting slopes or optimized capital constants.

**Literature priority.** Relevant accessible sources are Heinrich–Kahn, *Optimal rates for finite mixture estimation* (https://arxiv.org/abs/1507.04313); Katz–Diab–Batenkov (2024), *On the accuracy of Prony's method…* (https://doi.org/10.1016/j.acha.2024.101687); Andrews–Cheng (2012), *Econometrica* weak identification (https://doi.org/10.3982/ECTA9456). They support the existence of related rate phenomena, not a first-in-literature claim for this precise closed-loop problem. Moitra/Batenkov/Wu–Yang/reverse Laplace results already in the bibliography need comparison of observation contracts, not only exponent matching. The passive spectral result may be a modest but useful closed-loop corollary: claim that size honestly.

## D. Cut plan to ~115 PDF pages
Move **Appendix J, PDF pp. 120–124 (5 PDF pages)** to a separately linked replication index; move **Appendix B notation, PDF p. 83 (1)** to the same supplement; move **selected full numerical calibration ledger from Appendix D, ~3 PDF-page equivalents** while keeping the theorem statement and proof. **Total ~9 pages**, subject to actual retypesetting and cross-reference repair. Do not cut the core Appendix A proofs before checking them.

## E. Three questions for authors
1. Precisely which fixed-accuracy loss, rescaled-node class and per-reset noise/input design is claimed to have the matching K exponent? Can you state this on one page without changing mathematical meaning?
2. Has anyone other than the analysis-code authors verified the Rayleigh–Hölder and adaptive-probing lower constants, with a separately written script or handwritten proof?
3. Does the positive-decision example in Appendix I actually require cohort identification, or does it establish that *aggregate estimation* suffices, weakening the policy rationale for tagging?

## F. Forward to a colleague?
**No, not this build.** The one change that could change this: publish a one-page theorem-contract matrix plus an independently checked proof audit for the three financially essential results (Theorems 5.5, 5.9 and D.2–D.4), with all numerical constants explicitly distinguished from proofs.
