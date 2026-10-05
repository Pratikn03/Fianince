"""
Phase 0 Pre-Registration (committed with timestamp 2026-10-02)
===============================================================
Title: From Human Markets to Machine Markets — Feedback Stability,
       Auditable Memory, and Financial Constraints

Authors: Pratik Niroula, Prashant Niroula

Theorems to attempt, experiments, pass/fail criteria, analysis specs.
This file must not be modified after the timestamp date.

NOVELTY TABLE SUMMARY (from Phase 0 literature search)
-------------------------------------------------------
All five foundational areas confirmed as not directly applicable to LOB:
  1. Mixture deconvolution rates (Chen 1995, Heinrich & Kahn 2018, Wu & Yang 2020)
     Gap: assumes open-loop i.i.d.; LOB is closed-loop dynamical system.
     Novel contribution: Contract I0/I1 hierarchy replaces passive deconvolution.

  2. Selective classification / abstention (Chow 1970, Herbei & Wegkamp 2006)
     Gap: abstention is passive in ML; in LOBs it withdraws liquidity -> feedback spiral.
     Novel contribution: Endogenous-abstention model + action-support audit.

  3. Set-membership identification (Milanese & Vicino 1991, Tempo et al.)
     Gap: assumes UBB noise and exogenous regressors; LOBs have endogenous regressors.
     Novel contribution: Exact-arithmetic recurrence LP with conic candidate bounds.

  4. Ho-Kalman realization (Ho & Kalman 1966, Hautus 1969)
     Gap: arbitrary similarity transforms; LOBs need economic non-negativity.
     Novel contribution: PBH defect theorem + active probe matrix rank condition.

  5. Kreiss constant / pseudospectra (Trefethen & Embree 2005, Kreiss 1962)
     Gap: Euclidean norms, single operator; LOBs need coordinate scaling + hard limits.
     Novel contribution: Coordinate scaling + hard margin boundary + switched instability.

PRE-REGISTERED THEOREMS
------------------------
M1: Equivalence-class / observational equivalence theorem (Ho-Kalman)
    Claim: Two economies give identical IRFs iff merged (eta_i, sum_q_i) pairs agree.
    Minimal order = 1 + number of distinct eta.
    Pass: Python verification matches analytical formula for all test cases.

M2: Quantitative non-identifiability (Le Cam minimax lower bound)
    Claim: R_min = Omega(sigma^2 / (A^2 * delta^2)) episodes to distinguish rates
    differing by delta. Matching upper bound from explicit MLE estimator.
    Pass: R_min scales as predicted (doubling sigma -> 4x R_min; halving delta -> 4x R_min).
    Known gap: Wu & Yang (2020) prove rate is actually O(delta^{-(4k-2)}) for k components
    (worse than delta^{-2}). Our delta^{-2} is a special case k=1 (single rate).

M3: Minimax abstention theorem (indifference-zone testing)
    Claim: Any test with conditional error <= alpha must abstain when
    |S-1| <= C * sigma / sqrt(R*H). Our rule attains this rate.
    Pass: epsilon* correctly predicts where empirical abstention rate peaks.

M4 (Phase 2): Exact model-class test (Hausdorff / Hankel PSD)
    Claim: positive-memory class = completely monotone kernels. Finite-sample test with size control.
    Status: To be derived in Phase 2.

M5 (Phase 2): Transient solvency bound (Kreiss constant)
    Claim: sup_t ||J^t|| bounded by Kreiss constant. Shock threshold derived analytically.
    Status: To be derived in Phase 2.

PRE-REGISTERED EXPERIMENTS
--------------------------
E1: Cross-simulator validation (price-time LOB, pro-rata LOB, Kyle CDA)
    Pass criterion: coverage >= 70% in all three independent simulators.
    Specification: 30 seeds per condition, 300 episodes, 25 steps.

E2: Contract-violation robustness curves
    Pass criterion: coverage >= 65% at eps=0 for all violation types.
    Specification: 3 violation types × 6 epsilon levels × 20 seeds.

E3: Equal-information baselines (OLS, penalized single-rate, SPSA)
    Pass criterion: Our method dominates OLS on coverage at equal information budget.
    Specification: episode grid [20,40,...,300], 30 seeds per cell.

E4: Decisiveness trade-off
    Pass criterion: Can separately attribute abstentions to info-limit vs. bounds.
    Specification: 40 seeds at ep=100, alpha comparison at [0.01, 0.05, 0.10, 0.20].

E5: Crypto panel regression (two-way FE, clustered SE, asset+day FE)
    Pass criterion: beta significant (p<0.05) after FE; placebos insignificant (p>0.10).
    Specification: Use Binance 1-min klines; panel over asset×day; Bonferroni correction.

E6: Solvency phase diagram
    Pass criterion: halt rate increases monotonically with S; phase transition at S=1.
    Specification: Sweep S×leverage×margin_tightness, 10 seeds each cell.

E7: Broadened RL study (Tabular Q, DQN, rule-based adaptive)
    Pass criterion: DQN coverage > tabular; all CIs finite; 30 seeds.
    Specification: 300 steps, reward sensitivity sweep over lambda_I × lambda_T.

FAILED EXPERIMENTS (pre-registered as failures)
------------------------------------------------
F1: Original 10-asset crypto OLS cross-section
    Result: p=0.264 with controls. Effect disappears. Moved to panel (E5).
    Lesson: 10 assets + 8 degrees of freedom cannot carry a causal claim.

F2: ABIDES simulator integration
    Result: Java runtime dependency; approximated by 3-simulator cross-validation.
    Lesson: Always use pure-Python simulators for integration tests.
"""

PREREGISTRATION = {
    "title": "From Human Markets to Machine Markets",
    "timestamp": "2026-10-02T21:30:00-05:00",
    "theorems": {
        "M1": {"status": "pre-registered", "pass_criterion": "IRF identity holds for all merged pairs"},
        "M2": {"status": "pre-registered", "pass_criterion": "R_min ~ sigma^2/delta^2 scaling verified"},
        "M3": {"status": "pre-registered", "pass_criterion": "epsilon* predicts empirical abstention peak"},
        "M4": {"status": "phase-2", "pass_criterion": "TBD"},
        "M5": {"status": "phase-2", "pass_criterion": "TBD"},
    },
    "experiments": {
        "E1": {"status": "pre-registered", "pass_criterion": "coverage >= 70% all simulators"},
        "E2": {"status": "pre-registered", "pass_criterion": "coverage >= 65% at eps=0"},
        "E3": {"status": "pre-registered", "pass_criterion": "our method >= OLS on coverage"},
        "E4": {"status": "pre-registered", "pass_criterion": "abstention decomposed"},
        "E5": {"status": "pre-registered", "pass_criterion": "panel beta significant; placebos not"},
        "E6": {"status": "pre-registered", "pass_criterion": "halt rate monotone in S"},
        "E7": {"status": "pre-registered", "pass_criterion": "DQN > tabular; 30 seeds; CIs finite"},
    },
    "failures": {
        "F1": {"experiment": "10-asset OLS crypto", "result": "p=0.264", "action": "replaced by E5"},
        "F2": {"experiment": "ABIDES integration", "result": "Java dep", "action": "replaced by E1"},
    },
}
