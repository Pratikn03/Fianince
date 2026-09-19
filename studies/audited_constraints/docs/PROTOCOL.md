# Audited-tail and binding-constraint study: v0.5 protocol

Status: authored before primary execution in this session; NOT externally preregistered.
No live orders, real financial records, trained neural agents or human external reviewers.
Original v0.4 artifacts remain unmodified.

## Three different estimands
1. Hidden-memory kernel tail, conditional on a complete, resettable implementation contract.
2. Local fixed-linear-system gain A = a + sum(q), conditional on audited public rates and exact observed midprices. Ordinary terminal-row regression with one independent final innovation per episode; NO claim of a new regression algorithm.
3. Finite-horizon adverse-event probability under a fully specified constrained market simulation. Exact binomial intervals; NOT asymptotic stability.

## Audit contract
Public executable update rates, zero-memory reset, memory-only adaptive-demand input, declared code digest, no other state-dependent controller channel. Static inspection and mutation tests of the released implementation. A digest is version identity, not a security attestation or proof of full-system coverage. Cash, inventory and leverage persist and are explicitly outside this tail certificate. When they affect execution, switch from the linear claim to finite-horizon risk.

## Tail statement
For a positive mixture k_j = sum(q_i eta_i (1-eta_i)^j), q_i>=0, sum(q_i)<=Qmax, eta_i>=eta0, sum_{j=H}^infinity k_j <= Qmax (1-eta0)^H. Unknown-rate tails cannot be certified from short response observations alone. An optional general norm certificate ||A||<=r<1, ||B||<=b, ||C||<=c implies tail <=bc r^H/(1-r). No end-to-end certificate follows if a relevant inventory state has unit persistence.

## Primary linear experiment
12 previous model combinations (a=.4, impact=.02, normalized gain .7/.95/1.05/1.3, slow rate .002/.02/.1; fast rate .5; weights 60/40). Zero initial memory and exact quoted midprice are NEW audited assumptions, not the v0.4 information contract.
Episode counts 32,128,512. Observation lengths 16,64. Two designs: four-share initial impulse; eight signed half-share orders in four round trips, gross shares 4, terminal net position 0. Last step has no probe. 20 independent panels per cell. 2,880 panels; per-panel two-sided 95% Student-t interval for a+sum(q). No selection on labels. Count singular fits as inconclusive.
Endpoint inference reconstructs public linear memory filters from earlier prices but never reads simulator memory. Condition on all pre-terminal prices: last price innovation independent Gaussian. No pooling of multiple terminal rows from the same episode as iid.
Measure coverage, definite decisions, wrong confident decisions, interval width, gross volume, peak probe inventory, squared-order energy. Equal gross volume does NOT mean equal Fisher information or energy.

## Constraint experiment
Stylized dealer market with two memory traders, fundamentalist, background trader, probe trader, and dealer. Explicit cash, inventory, leverage, credit, spread fees, forced liquidation, rejected/unfilled orders, dealer limits, and default/market-halt events. Each exogenous shock and transaction is logged. No debt silently forgiven. Cash and shares conserved at settlement; negative equity marked as default, not reset.
Predeclare 24 settings: normalized gains .7,1.3; slow rates .02,.1; three funding regimes (unlimited counterfactual, ample, tight); external price jump 0 or -2 dollars at t=16; 64 transitions. Probe is a 4-share round trip, baseline flow sd=.10, quote midprice exact.
Generate 20,480 fresh iid episodes per setting, in 40 nonoverlapping panels of 512. Evaluate nested sample budgets 32,128,512 with Bonferroni alpha=.05/3 across the three planned looks. Primary adverse event: any account default, market halt, OR any adaptive trader's peak equity drawdown >20% of initial capital. Report dislocation separately, not used to tune endpoint.
Use exact two-sided Clopper-Pearson intervals for probability, compare to policy-design threshold 5%. This threshold is hypothetical, not a legal standard or investment recommendation. Compare funding regimes using common external shock tapes, descriptive paired effect.

## Negative controls / remaining boundary
Omitted slow memory; incorrect reset; noisy observations (errors in variables); extra inventory channel; audit tampering; forged manifest; generic nonlinear/capped demand. Never claim certificate validity simply because a fit passed.
Try budget designs; retain negative findings. All protocol changes logged separately as exploratory.

## Reproduction
Tests before code. Save source, seeds, sufficient data and selected full observable trajectories. A separately coded verifier uses no project inference imports. Rerun from a clean extracted archive. This is internal computational reproduction, NOT outside replication. Supply external challenge inputs, held-out answers, checksums, and reviewer checklist. External status remains pending until an outside group returns results.
