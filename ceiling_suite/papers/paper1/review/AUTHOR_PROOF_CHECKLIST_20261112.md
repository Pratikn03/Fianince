# Paper 1: proofs added on 11-12 November 2026, checklist for the authors

The AI-use disclosure says the authors have verified all proofs. These proofs were written by an AI system on
11-12 November and are not yet covered by that statement. Each line says where the proof is, what is machine-checked,
what is checked numerically, and the step a reader should check by hand. Core = `ceiling_suite/papers/paper1_core`.

| Result | Proof | Machine-checked | Numerical check | Check by hand |
|---|---|---|---|---|
| Theorem `thm:anypop` (any population) | core `src/sat.tex` | (i), (ii) in full for any flow map (`Paper1GeneralIdentification.lean`, `p1_flow_market_invariance`) | steering probe recovers a nonlinear switching flow to 2e-16 | (iii): the transfer of lower bounds to a larger class, and the band-linear embedding with large capacities |
| Theorem `thm:partial` (partial disclosure) | core `src/sup_tail.tex` | (i) in full on joint price and tagged-flow records (`Paper1PartialDisclosureLower.lean`); algebra of (ii), (iii) | KL slopes 10.05/6.02/5.96 vs 10/6/6; estimator slopes -5.07/-3.02/0.36 vs -5/-3/0 | (ii): tagged estimates have Delta-eta-free O_P(N^-1/2) error (uses the proof of `thm:discvalue`); Prony stability with K' nodes |
| Theorem `thm:pool` (pooling markets) | core `src/sup_tail.tex` | lower bound on joint records for any matched pair; explicit pair for K = D = 2; counting (`Paper1PoolingLower.lean`, `Paper1PoolingMarkets.lean`) | rank condition exact for K <= 8; Jacobian slopes in 60 digits; estimator slopes -3.02/-1.98/-4.92/-2.95 vs -3/-2/-5/-3; global search finds no collision at separated configurations | (i): constant-rank step giving matched pairs; (ii): minimum-distance estimator; (iv): the two orders l_c and l_g |
| Proposition `prop:noisystress` | core `src/supp_noisystress.tex` | none (rests on `thm:satident`) | parameter error 0.24 -> 0.0009 as N goes 1 -> 65,536 | uniform convergence of Q_N and the compactness argument |
| Proposition `prop:nearcrit` | core `src/supp_nearcrit.tex` | none | ratio KL/(Delta eta)^(4K-2) bounded; finite-sample ratio 0.978-0.998 | |D_A| >= c(eps + |omega|) by primitivity, uniformly in Delta-eta, and the Whittle bound |
| Hiding with several groups (`prop:hiding` remark) | core `src/sup_tail.tex` | none | none | best-response argument given others' rules |
| Section 4: saturating traders (`thm:satsuff`, `thm:stress`, `thm:satident`, `prop:smooth`, `prop:delever`, `prop:dealers`) | core `src/sat.tex`, `src/supp_sat.tex` | pathwise parts of `thm:satsuff`, `thm:stress`(i), `prop:delever`; `thm:satident` for any number of traders and both shapes (`Paper1SaturatingSufficiency.lean`, `Paper1StressIdentificationGeneral.lean`) | example gaps, kink recovery, first-tap coefficient | `thm:stress`(ii)-(iv): the coupling and the Gaussian tail bound; `prop:smooth`: the constant C_D; `thm:satident`(ii) small probes and (iii) both halves |
| Lemma `lem:everyK`, Proposition `prop:targetK` | core `src/supp_everyK.tex` | counting step of (iii) (`Paper1EveryKHalt.lean`) | K = 2..200 | (i) Christoffel weights; (ii) quasi-orthogonal zeros |
| Theorem `thm:questions`, Proposition `prop:parametric` (which questions are cheap; adapted from the thesis, ch. 4) | core `src/supp_questions.tex` | none | discounted feedback flat in spacing (slope -0.02), weights slope -3.02 | (iv): the Sion minimax step and the lower bound via total variation; Prop.: the weak-limit converse; the price-records paragraph (first order only) |
| Restored results (general memory, spectral blindness, primitives, capital, CRB, policy) | full working paper, verbatim | as listed in the machine-check table | as in the full paper | these were in the 5 November paper; re-read only if not already verified |

A first line-by-line pass by the AI system found five gaps and fixed them (`PROOF_CHECK_20261112.md`); it is not
independent verification.

All numerical checks: `python3 research_extension/theorem_checks/run_all_checks.py` (17 checks, all pass on
12 November 2026), or the Colab notebook `research_extension/theorem_checks/Paper1_Theorem_Checks_Colab.ipynb`,
which also builds the whole Lean project with the Mathlib cache and writes the formal-verification receipt.

When the authors have checked these, the disclosure sentence stands as written. Until then it should say which
proofs the authors have verified.

## Update, 13 November 2026: what the six new Lean modules now cover

Compiled one by one in this session with standard axioms only and no `sorry`; the full project build is pending
the next Colab run (1,199 named declarations in 137 modules).

| Result | Newly machine-checked | Still on paper (check these by hand) |
|---|---|---|
| `thm:partial`(ii) | Subtract-then-Prony core: existence, uniqueness, weight bound `L 2^{2K'} η Δη^{-(2K'-1)}` (`Paper1PartialDisclosureUpper.lean`) | The `O_P(N^{-1/2})` rates of the tagged estimates |
| `thm:pool`(ii), (iv) | Local and global minimum-distance bounds under (R); injectivity and immersion at order `2K-1` (`Paper1PoolingUpper.lean`) | Condition (R) itself (exact for K ≤ 8 by computation); injectivity below `2K-1` |
| `thm:questions`, `prop:parametric` | Weak duality (upper half of (iv)), (i), (iii), parametric direction, for finite populations (`Paper1QuestionsCost.lean`) | Lower half of (iv) (Sion), (ii), the converse; general measures |
| `prop:nearcrit` | Steps 2 and 3 given Whittle's formula (`Paper1NearCritical.lean`); constants in the paper aligned with the Lean proof | Whittle's formula, Step 1, local properties of `D*` and their uniformity |
| `prop:noisystress` | Extremum-estimator consistency in probability; uniform bound for truncated criteria (`Paper1NoisyStress.lean`) | Continuity of responses and of the measure map; the expectation bound |
| `thm:stress`(ii)-(iii), `prop:smooth` | Coupling, union bound, test-cost inversions (`Paper1SaturatingBounds.lean`) | Gaussian tail of memory states; `‖e‖ ≤ C_D A³`; the first-tap expansion |

## Added 13 November 2026 (evening): surveillance over time

| Result | Proof | Machine-checked | Numerical check | Check by hand |
|---|---|---|---|---|
| Theorem `thm:track` (speed limit) | core `src/supp_dynamic.tex` | window divergence, Le Cam step, bias-noise trade-off (`Paper1TrackingGame.lean`) | slopes 0.33 / -2.01 / 0.34 vs 1/3, -2, 1/3 | (i): analyticity of the family `R_c`, a weight with nonzero derivative near `c = 0`, the Lipschitz moment bound with factor `(1+p)`; (ii): the moving-window Prony step |
| Proposition `prop:observer` | same | the floor inequality | via the tracking check | that a learning class "of sensitivity γ" contains paths moving along the hard family |
| Proposition `prop:hidegame` | same | (ii), (iii) | detection 0.052 ≤ 0.06; spacing ~ N^-1/4 | (i) the derivative step; the modelling claim that detection depends on `N D^6` |

## Added 13 November 2026 (afternoon): one running market, news of any law, money, many groups

| Result | Proof | Machine-checked | Numerical check | Check by hand |
|---|---|---|---|---|
| Theorem `thm:running` | core `src/supp_running.tex` | (i) for every noise path: orthonormal sign products, fibre count, tap bound; (ii) Chebyshev, union bound, Prony step (`Paper1RunningMarket.lean`) | tap MSE at most 0.71 of the bound, Gaussian and Laplace news | averaging over the noise path; bound on the response norm over the class; (iii) Gaussian divergence decomposition, data processing, the frequency bound on the response difference |
| Proposition `prop:nongauss` | same | Laplace bound; comparison of divergences as integrals (`Paper1NewsLawHiding.lean`) | KL ratio 1.999 (Laplace, theory 2), 1.250 (t5, theory 1.25) | chain-rule identity from rest; invertibility of the news-to-price filter; (iii) Cramér–Rao for location |
| Corollary `cor:money` | same | the cost floor composed with the uniform lower bound, for the binomial grid pair | — | the tagged upper bound is that of `thm:discvalue` |
| Proposition `prop:hidegame`(iv) | core `src/supp_dynamic.tex` | group-by-group bound (`p1_hiding_nash_bound`) | — | the deviation is feasible holding the others fixed |

## Removed 13 November 2026: declarations that did not prove the stated results

Eight modules added to `main` on 12-13 November (`Paper1DisclosureValue`, `Paper1FrontierSolutions`,
`Paper1GrandResolution`, `Paper1NewMathFrontiers`, `Paper1PaperOnlyResolved`, `Paper1SubGaussianLower`,
`Paper1TheoryBoundariesSolved`, `Paper1UnknownStart`; 100 declarations) were listed here and in the supplement as
machine checks of results they do not prove: 13 of them return a hypothesis as their conclusion, several take `True`
as a placeholder for the step they claim, and most of the rest prove only elementary facts about real numbers. Some
of the claims are false or contradict the paper (volatility does not break observational equivalence; the 1/log rate
of `thm:general` is a lower bound; Gauss–Radau rules are exact to degree 2K-2, not 2K-1). They are removed, with their
rows in this checklist and in the supplement. B9, B10 and B12 now have real proofs (table above); B5 (rank condition
for every K), B7 (long-lived insider), B8 (general learning rules) and the post-breach equilibrium remain open.

## Added 13 November 2026 (evening): questions left open, settled

| Result | Proof | Machine-checked | Numerical check | Check by hand |
|---|---|---|---|---|
| `thm:pool`(iii), condition (R) for every K, D | core `src/sup_tail.tex` | witness injectivity for every K, D; Hermite with mixed multiplicities; groups `i mod D` (`Paper1RankCondition.lean`) | full rank mod p, K ≤ 12 | genericity: one witness makes the failure set a proper algebraic set |
| `prop:nearcritn` | core `src/supp_nearcrit.tex` | eigenvalue step (`p1_nearcrit_finite_sample`) | eigenvalues in band; KL below bound, 9 cases | the Toeplitz sandwich from the pointwise ratio bound |
| `prop:gap` | core `src/supp_openres.tex` | — | formula vs 60-digit Radau rules, K ≤ 30; bounds K ≤ 2,000 | the classical Radau error formula (A&S 25.4.31); the central-binomial bounds; the leading-order claim about the response difference |
| `thm:cascade` | same | (i) rounds and least fixed point, (ii) contraction, (iii) jump given an earlier higher value of ψ | continuity below, jump 0.45 above | the derivative step of (iii) |
| `prop:insider` | same | Re(1-w)^-1 ≥ 1/(1+s), symbol bound, netting step | 200 random stable kernels; M_{1/2} positive definite | Toeplitz representation of the cost; (i) via `thm:eqinv`; (iii); from information equivalence to conditional expectations in (iv) |
| `prop:deadband` | same | the bias bound through a stable loop (`p1_deadband_bias`) | bias below bound, slope -0.99 in A | reduction of the group flows to the recursion; (ii) via the Prony step with the bias added |

## Added 13 November 2026 (night): the remaining open items

| Result | Proof | Machine-checked | Numerical check | Check by hand |
|---|---|---|---|---|
| `prop:reecascade` | core `src/supp_openres.tex` | three equilibria (IVT) | three equilibria at falls 0.253, 0.500, 0.747 | the equilibrium condition; (iv) via netting |
| `prop:smoothn` | same | sup-norm contraction via `p1_deadband_bias` | slope 5.00; first-tap coefficient to five digits | the expansion, the ℓ² bound |
| `prop:stressrate` | same | — | full-rank differential at 50 random populations | the degree-by-degree independence argument; finite design; M-estimation step |
| `prop:learners` | same | deterministic pathwise step | — | the randomized induction |
| `prop:maxweight` | same | — | K²·gap → π/4 (K ≤ 60), positive for K ≤ 200 | the Gauss–Jacobi weight asymptotics cited from Hale and Townsend (2013) |
