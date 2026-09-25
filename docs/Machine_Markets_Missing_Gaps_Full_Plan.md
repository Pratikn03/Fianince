# Machine Markets — Complete Missing-Gaps and Execution Plan

## Current manuscript reviewed
- `Machine_Markets_Final_Integrated_Paper.pdf`
- 59 pages, dated September 24, 2026.

## Goal
Produce a submission-ready first paper whose strongest claims are:
1. exact identification limits for adaptive market feedback;
2. valid observable-data inference under explicit information contracts;
3. a controlled funded-market mechanism showing that signal stability does not imply solvency;
4. an explicitly exploratory public-market study unless a truly locked forecasting design is completed.

---

# A. MUST-FIX BEFORE SUBMISSION

## A1. Repair remaining claim-scope inconsistencies
1. Abstract Evidence Status currently says empirical validation is demonstrated; change to "exploratory empirical analysis is reported".
2. Related-work section currently says the paper demonstrates empirical predictive power of the closed-loop operator J* on live order books. This is not established by Coinbase F or the Binance fitted state-space model. Replace with "evaluates empirical associations and model fits".
3. Section 3 says the paper supplies "empirical limit-order-book validation"; replace with "exploratory public-market analysis".
4. Final Appendix D sentence says structural algorithmic feedback significantly drives liquidity strain even in liquid spot markets. Remove. The causal liquidity-strain result is from a synthetic funded simulator, not live spot-market identification.
5. Wherever cross-venue differences are discussed, use: "differences conflate estimator, sampling-frequency, symbol/quote-currency, and venue effects; they are not identified as venue effects."

## A2. Covariance-aware output-error benchmark: make inference internally correct
Current model:
    min_theta (beta_hat-beta(theta))'W(beta_hat-beta(theta)) + lambda(a^2+Q^2)
with theta=(a,eta,Q), kappa fixed to beta_hat_0, and sandwich SE.

Problems to address:
- penalization changes the estimator and its asymptotic bread matrix;
- active box constraints make naive normal SE unreliable near boundaries;
- fixing kappa=beta_hat_0 ignores uncertainty in beta_hat_0;
- W is estimated and regularized;
- 1.96 sandwich intervals are asymptotic, not finite-sample certificates.

Preferred fix:
1. Fit theta=(a,eta,Q,kappa), not kappa fixed at beta_hat_0.
2. Use lambda=0 for the primary inferential benchmark unless identification is numerically impossible.
3. If regularization is retained, include the penalty Hessian in the bread and label the interval approximate.
4. Add profile-likelihood / profile-objective intervals for S=a+Q as the main robustness interval.
5. Add parametric bootstrap intervals generated from the fitted response covariance.
6. Report bound-hit rates and treat boundary solutions separately.
7. Keep the method labeled "asymptotic benchmark", not "certificate".

Required outputs per panel:
panel_id, true_S, S_hat, ci_low, ci_high, covered, decision,
wrong, optimizer_success, bound_hit, cond_W, residual_acf,
objective, lambda, seed, runtime.

## A3. Implement the rigorous covariance-aware conic certificate
This is different from A2.

Use the exact finite-sample F-calibrated ellipsoid for beta under the controlled Gaussian episode contract:
    E_alpha = {b : (b-beta_hat)' V^{-1}(b-beta_hat) <= k_alpha^2}
Then optimize S=a+Q over the positive-memory recurrence using a conic outer relaxation with:
- continuous rate bins;
- McCormick envelopes for a*b_t and w_l*b_s;
- data-derived finite cap on Q when L0>0;
- numerical outward certification / dual residual repair.

This becomes the rigorous covariance-aware I0 certificate.

Compare:
- rectangle recurrence LP;
- covariance-aware conic certificate;
- covariance-aware output-error benchmark;
- point fit.

Required metrics:
coverage, decisiveness, unconditional error, conditional error,
median width, 90th-percentile width, conflicts, failures, runtime.

Run on the full primary grid, not only eta=0.002.

## A4. Broaden comparator evaluation
Current covariance comparator is reported on 600 panels at H=64, eta=0.002.
Run a fresh, frozen benchmark across:
- S or G: stable far, stable near, boundary, unstable near, unstable far;
- slow rates: 0.002, 0.02, 0.10;
- episode budgets: 128, 1024;
- pulse sizes: 1 and 4;
- H: 24 and 64;
- >=100 replicate panels per cell.

Pre-register the grid before reading results.
Do not tune on the final comparison grid.

## A5. Fix information-contract language
Maintain:
- I0: public randomized probes + prices + valid rate floor.
- I1: exact prices + audited rates + verified reset + complete channel inventory.
- I2: observational public market data.

Do not call I2 a structural certificate.
Do not compare I1 decisiveness to I0 as if it were pure estimator efficiency.

---

# B. THEORETICAL COMPLETION

## B1. Add continuous-time theorem
Add to supplement, not necessarily main text.

Model:
    xdot = -Gamma x + g B m
    mdot = E(Cx-m)
with Gamma>0 diagonal, E>0 diagonal, B,C>=0.

Theorem:
    A_c Hurwitz iff rho(Gamma^{-1} g B C) < 1.
For Gamma=gamma I:
    g rho(BC) < gamma.

Then show Euler-consistent scaling:
    a_h = 1-h gamma
    g_h = h g
    eta_h = h eta
which recovers:
    g_h rho(BC) < 1-a_h.

Add a numerical ODE figure:
- one stable case;
- one boundary-near case;
- one unstable case;
same initial perturbation and same B,C.

Do not claim arbitrary discretization invariance.

## B2. Finalize group-identification theorem
Current five-case structure is much improved.

Add:
1. an exact identified-set formulation for unknown eta:
       U q = s b,  s=1/eta,
       q>=0, 1/eta_max <= s <= 1/eta_min.
2. a noisy-data version:
       b in confidence set B_alpha
   and define the projected identified set for q.
3. conditioning diagnostics when eta_i are close in heterogeneous-rate Vandermonde separation.
4. one numerical example per case.

## B3. Literature-priority audit
For every theorem/result, classify:
- standard result;
- specialization;
- new construction;
- new application;
- empirical observation.

Priority-audit at least:
- positive-feedback boundary;
- finite-window construction;
- group non-identifiability;
- channel measurement-rank theorem;
- covariance-aware conic certificate;
- operational-risk separation.

Do not market established positive-systems or regression facts as novel.

---

# C. FUNDED-MARKET MECHANISM WORK

## C1. Repair saturation in paired counterfactual controls
Current N=100 table has:
- Active: 100% halt / 100% failure
- Frozen: 100% halt / 100% failure
- Q=0: 100% halt / 100% failure

This cannot identify whether learning changes halt/failure probability because the endpoint is saturated.

Build a near-threshold factorial design varying:
- dealer capital: 0.75x, 1x, 1.5x, 2x;
- starting inventory utilization: 0%, 50%, 80%, 95%;
- mean shock: 0, -1, -2, -4;
- S: 0.70, 0.82, 0.97, 1.03, 1.18;
- slow eta: 0.02, 0.10.

Use identical exogenous tapes across:
1. active learning;
2. frozen memory;
3. Q=0;
4. unlimited funding diagnostic.

Primary endpoint:
    composite failure probability.
Secondary:
    halt, default, drawdown, price dislocation, min equity,
    leverage, unfilled volume, liquidation volume, recovery time.

Use paired differences and exact/binomial or bootstrap CIs by independent tape.

## C2. Clarify frozen versus Q=0
At zero initial memory, frozen memory can equal Q=0 in some designs.
Create cases with nonzero pre-shock memory so the interventions differ:
- freeze means retain pre-shock memory;
- Q=0 removes the feedback channel.
Report when they coincide and why.

## C3. Produce a funded-risk surface
Main figure:
x = S
y = dealer capital buffer
fill = failure probability
facet = shock size or initial utilization

Do not call it a phase transition.
Call it a scenario-risk surface.

---

# D. EMPIRICAL PUBLIC-MARKET WORK

## D1. Decide whether empirical evidence is exploratory or confirmatory
Two valid routes:

Route 1 — theoretical/mechanism paper:
- retain N=10 Coinbase study as exploratory;
- remove all words implying real-market validation;
- do not require new months of data.

Route 2 — stronger empirical paper:
- collect a multi-date panel;
- use truly locked train/validation/test periods;
- evaluate future forecasts.

Do not mix the two standards.

## D2. If choosing Route 2, build the locked forecasting panel
Target example:
- 10–20 assets;
- 60–120 dates;
- Coinbase + Binance only if data are time-synchronized and comparable.

For each date:
Period A:
- construct F and/or fitted state-space features;
- historical volatility;
- historical spread/depth if actually archived;
- volume;
- order-flow persistence;
- return autocorrelation baseline.

Gap:
- enforce no overlap.

Period B:
- future return persistence;
- secondary outcomes: spread widening, depth loss, recovery time.

Outer split:
- train dates;
- validation dates;
- locked test dates.

Fit coefficients only on train/validation.
Do not use locked outcomes until final scoring.

Primary comparison:
baseline conventional model vs baseline + F or S_model.
Report:
paired forecast-loss improvement, MAE, RMSE, out-of-sample R2,
date-block bootstrap CI, availability.

## D3. Fix Binance state-space robustness
Current assumptions include y0=0 and fitted total flow v_t.

Add sensitivity to:
- y0 estimated;
- y0 profiled;
- warm-up burn-in;
- lambda in {0, 0.001, 0.01, 0.1};
- wider/narrower parameter bounds;
- residual autocorrelation;
- flow scaling;
- alternative price anchors.

Report:
parameter profiles, validation loss, bound-hit frequency,
condition numbers, residual diagnostics, seed dispersion.

Do not call theta structurally identifiable unless an observation-identification argument is supplied.

## D4. Same-estimator cross-venue comparison (optional but valuable)
If you want any venue-comparison claim:
- same estimator;
- same clock;
- same horizon;
- same symbol economics where possible;
- same feature construction.

Then report:
Pearson, Spearman, MAE, RMSE, equality-line scatter,
and uncertainty.

Otherwise keep Coinbase and Binance as separate exploratory analyses.

---

# E. FIGURES THAT ARE STILL MISSING

Main paper should add:

F1. Information-contract diagram
    I0 vs I1 vs I2 and what each can identify.

F2. Exact finite-window ambiguity
    stable and unstable models overlap through cutoff, then diverge.

F3. Comparator frontier
    x=decisiveness, y=conditional error or coverage;
    one point per method, with information contract encoded.

F4. Interval-width distributions
    rectangle LP vs covariance conic vs output-error.

F5. Group-identification schematic
    aggregate probes identify Q; channel probes identify q under rank conditions.

F6. Funded risk surface
    S x capital buffer -> failure probability.

F7. Paired mechanism-effect plot
    active-frozen and active-Q0 paired differences with CI.

F8. Empirical coefficient/forecast plot
    only if doing Route 2 locked forecasting.

Optional:
F9. Continuous-time stable vs unstable trajectories.
F10. Binance profile-likelihood / parameter-sensitivity plots.

---

# F. TABLES TO ADD OR REVISE

T1. Claim / evidence / information-contract matrix.
T2. Theorem assumptions and exclusions.
T3. Full comparator table over all benchmark cells.
T4. Comparator by slow-rate and budget.
T5. Group-identification five-case table.
T6. Funded-risk scenario table.
T7. Paired mechanism controls with CIs.
T8. Empirical data-quality and timing table.
T9. Locked forecast results (if Route 2).
T10. Reproduction and external-review status.

---

# G. MANUSCRIPT REWRITE

## G1. Reduce over-fragmentation
Current 24-section structure is too sprawling.

Recommended main structure:
1. Introduction and contributions
2. Model and information contracts
3. Identification limits
4. Observable inference
5. Controlled benchmark results
6. Funded-system mechanism
7. Exploratory public-market analysis
8. Limitations and conclusion

Move:
- prospective MARL program;
- detailed legal discussion;
- full algebra verification;
- long replication commands;
to supplement.

## G2. Correct remaining overclaims
Search for:
- "validation";
- "predictive power";
- "structural";
- "causal";
- "significantly drives";
- "verified".

Each occurrence must point to a specific method and evidence level.

Specific current phrases to revise:
- Evidence Status: "empirical validation is demonstrated" -> "exploratory empirical analysis is reported".
- Related work: "demonstrating empirical predictive power of that operator" -> remove.
- Section 3: "empirical limit-order-book validation" -> "exploratory public-market analysis".
- Final Appendix D: "structural algorithmic feedback significantly drives liquidity strain even in liquid spot markets" -> remove/rewrite as a synthetic mechanism statement.

## G3. Keep the conclusion narrower
The conclusion should say:
- what is mathematically identifiable;
- what the controlled simulator demonstrates;
- what public-market analysis only suggests;
- what remains untested.

---

# H. REPRODUCIBILITY AND EXTERNAL VALIDATION

## H1. Create one claim ledger
CSV columns:
claim_id
paper_location
claim_text
claim_type
information_contract
source_result_file
source_data_hash
code_commit
verification_test
status
limitations

No number enters the paper without a result-file pointer.

## H2. Independent verifier
Must not import production estimator code.

Recompute:
- stability boundaries;
- finite-window witness;
- group-identification fixtures;
- decision metrics;
- selected recurrence bounds;
- funded accounting;
- selected comparator rows.

## H3. External review
Before submission obtain:
1. one systems/control reviewer;
2. one finance/microstructure reviewer;
3. one independent reproduction attempt if possible.

The reviewer must be allowed to reject a claim.

---

# I. EXECUTION ORDER

## Stage 1 — 2–4 days
- freeze current release;
- build claim ledger;
- repair prose overclaims;
- freeze new protocols.

## Stage 2 — 4–7 days
- implement rigorous covariance ellipsoid + conic certificate;
- unit-test group identified-set cases;
- add continuous-time theorem to supplement.

## Stage 3 — 5–10 days compute/analysis
- run full matched comparator grid;
- generate comparator figures/tables;
- audit coverage and error metrics.

## Stage 4 — 5–10 days
- run funded near-threshold scenario surface;
- run paired active/frozen/Q0/unlimited controls;
- generate risk figures.

## Stage 5A — 3–5 days if keeping empirical section exploratory
- clean wording;
- run robustness checks on current Binance fit;
- finalize exploratory empirical appendix.

OR

## Stage 5B — data-dependent if doing locked forecasting
- collect/build multi-date synchronized data;
- freeze train/validation/test;
- run final locked test once.

## Stage 6 — 5–7 days
- restructure manuscript;
- generate all figures/tables from artifacts;
- run offline reproduction;
- external review package.

---

# J. DEFINITION OF DONE

Submission-ready first paper:
- no known mathematical inconsistency;
- every headline number traceable;
- comparator results documented under matched information;
- funded mechanism not based only on saturated endpoints;
- empirical section explicitly exploratory OR genuinely locked;
- no causal live-market claim unsupported by design;
- outside proof/reproduction review attempted;
- all figures generated from frozen artifacts;
- main text streamlined and supplement contains technical detail.

Optional future program, NOT required for first submission:
- ABIDES transfer;
- trained MARL populations;
- LLM trading agents;
- real institutional provenance;
- prospective market intervention;
- cross-domain banking/insurance transfer;
- multi-clearinghouse contagion.
