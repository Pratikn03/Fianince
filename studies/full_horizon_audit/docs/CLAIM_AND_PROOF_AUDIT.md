# Claim and proof audit

Research date: 18 September 2026. This is an internal mathematical/code audit plus a focused primary-source literature review. No outside researcher reviewed these proofs or independently replicated the study. The original archive was preserved.

## Decision on the research target

**The strongest supported interpretation is a restricted measurement requirement, supported by illustrative constructions and a reproducible comparison—not superiority of the original diagnostic.** Full-horizon positive-mixture confidence bounds make more decisions on this benchmark than the original summary bound. They are not universally better: some earlier decisions become model conflicts, and four higher-noise confident decisions are wrong. Point fitting is accurate at long horizons but is not certification.

## Claim ledger

| Claim | Evidence and verdict |
|---|---|
| Adaptive decision feedback changes the price process. | Already studied in adaptive-agent finance and performative prediction. Not new. |
| Stability is equivalent to a + sum(q) < 1 in the specified positive model. | Valid specialization of positive-system/M-matrix theory. Not a new general stability law. |
| A finite exact window can be shared by opposite-stability models. | Existing rational construction rechecked: 112 pairs and a readable example. Classical moment/interpolation ingredients. Global novelty not established. |
| Equal numbers of agents make the old construction a fixed-order theorem. | Incorrect. Repeated-rate copies equalize active counts; minimal order can grow with the requested exact horizon. |
| The original summary diagnostic outperforms adequately informed conventional identification. | Not supported. The previous 32-tap comparator was too weak to justify that claim. |
| Full-horizon NNLS is a certified stability test. | Incorrect. It estimates one plausible positive mixture and makes 24/306 errors at H=256 in lower/higher noise. It has no stated confidence guarantee. |
| Full-moment outer bounds have a finite-family error guarantee under the stated model. | Mathematical guarantee in exact arithmetic on a simultaneous Gaussian event; implementation uses guarded floating point. All 82,364 on-event rows contain the true gain. Four erroneous confident labels occur off-event. |
| Raw LP strictly dominates the old method on every dataset. | Incorrect. Error allocation differs, and infeasible confidence sets cause loss of some decisions. Net coverage improves, not pointwise universal dominance. |
| The intersection diagnostic dominates its summary component. | Only when the joint confidence set is feasible. Empty joint sets are reported as conflicts, not converted to safe labels. Its labels equal the raw LP labels on this primary dataset. |
| Hidden slow modes imply a fixed-order noisy identification limit. | Derived explicitly for two common-rate-component models, by classical Gaussian two-point testing. Valid restricted statement; not a new general minimax technique. |
| More elapsed observation time always solves the problem. | False under the assumed independent per-tap noise experiment: information can saturate. Repeated probes/other measurements can change this conclusion. |
| This establishes a new finance paradigm or a deployable crisis predictor. | Unsupported. No real financial data, trained neural agents, endogenous policy learning, economic welfare, or external replication. |

## Proof audit A: stability

For J = [[a, 1^T], [diag(eta) q, diag(1-eta)]], with 0 <= a < 1, q >= 0 and eta in (0,1], the lower diagonal block of I-J is positive. Its scalar Schur complement is 1-a-sum(q). Standard nonsingular M-matrix reasoning gives Schur stability iff that scalar is positive. At equality 1 is an eigenvalue; above the boundary, the Perron eigenvalue exceeds 1. Zero-weight states can be removed and their stable diagonal modes retained. This does not extend automatically to signed feedback, switching matrices, nonlinear systems, or arbitrary financial networks.

## Proof audit B: finite-window ambiguity

The prior barycentric construction matches finitely many geometric-mixture moments using positive and negative parts of a signed measure. The differing total gains are placed around the same stability threshold. Exact Fraction arithmetic verifies all saved witnesses. Matching early kernels gives matching early closed-loop response coefficients through the finite causal recursion; it does not imply indistinguishability at all later dates. No claim that a fixed finite-order noiseless system stays unidentified under arbitrarily many exact measurements is made.

## Proof audit C: outer confidence bounds

For any continuous rate bin B, total positive mass w_B satisfies min_B(f) w_B <= integral_B f dmu <= max_B(f) w_B. Intersect the resulting necessary inequalities for every measured coordinate, available prefix sum and terminal tap. Every truly compatible mixture is feasible in this finite LP; a point-grid omission cannot exclude a true off-grid mode. The relaxation may be loose because extrema of different features need not occur at the same rate. Tightening bin resolution reduces this source of looseness, but does not make the implementation a formally verified real-arithmetic solver.

Half the total 0.05 error budget is assigned to sum/terminal features across four horizons; half to all 256 individual coordinates. Gaussian tail probabilities plus a union bound give at least 0.95 simultaneous coverage. Feature dependence does not invalidate that union bound. The guarantee is for a fixed declared horizon family, not optional stopping or error conditional on deciding. Wrong rate floors, unknown/non-Gaussian/correlated errors, and incorrect model structure invalidate the stated contract unless separately modeled.

## Proof audit D: fixed-order Gaussian limit

Use normalized common fast weight 0.7 at rate 0.5 and slow weights 0.2 versus 0.4 at a shared rate eta. Thus gain is 0.9 versus 1.1, with the same number of states and a fixed separation from the boundary. For Delta=0.2 and independent tap noise standard error v, the difference of mean taps is Delta eta (1-eta)^j. Its squared Mahalanobis norm is

    d_H^2 = Delta^2 eta [1-(1-eta)^(2H)] / [v^2 (2-eta)].

The balanced likelihood-ratio classifier between the two *known* Gaussian means has exact error Phi(-d_H/2). Since this oracle knows more than a generic estimator, it supplies a lower bound for the latter's forced error on the same pair.

For stable/unstable decision regions S,U, balanced decision coverage c and unconditional wrong-label probability e,

    c - 2e = 0.5[(P0(S)-P1(S)) + (P1(U)-P0(U))] <= TV(P0,P1).

Hence c <= 2e + 2Phi(d_H/2)-1. This remains a necessary bound for randomized rules. It is not a claim that the bound is always attainable. As eta decreases with H and v fixed, d_H tends to zero even with fixed two-state order and fixed gain margin. A uniformly accurate AND decisive classifier therefore needs a restriction excluding such pairs, better precision, or a more informative experiment. A rate floor is one such restriction, not the only possible solution and not sufficient at every noise level.

## Remaining external review questions

1. Does an existing paper contain this exact positive-mixture stability specialization and observation-budget expression? Search positive realization, truncated Hausdorff moments, functional estimation, and partial identification, not finance alone.
2. Can a reviewer construct a counterexample to a stated theorem under its actual assumptions? Signed weights or a false floor are outside the theorem, but are essential transfer tests.
3. Is the proposed financial observation protocol experimentally feasible without directly observing hidden decision states? The current kernel access is stronger than passive prices.
4. Does a complete continuous-moment or semidefinite implementation change the conclusion relative to the tested LP outer relaxation? No optimality among conventional methods is established here.
5. Can a separately authored implementation, different solver and independently generated benchmark replicate the results? The present second algorithm uses the same HiGHS library.
