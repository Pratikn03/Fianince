# Initialization and smooth-choice robustness, v1

Locked before new outcome evaluation, 2026-09-27. This is an internally
predeclared robustness audit of a **post-hoc selected** example, not external
preregistration, trained-population confirmation, or a new market calibration.
User approved the bounded design. Main paper and earlier sealed packages stay
unchanged. No large training run is part of this study.

## Model held fixed

Use the v0.12 two-dealer, two-period economy: asks (2,4,6); equiprobable
V in (0,4); independent Z in (-2,2,6) with masses (1/4,1/2,1/4); C=V+Z.
Customers buy one unit iff C >= minimum ask; ties split the unit. Quotes precede
the current economic draw. Dealer gross rewards are fill*(ask-V), customer
surplus is C-ask on a trade, and welfare sums both profits and customer surplus.
No inventory, funding, default, shock, or systemic-loss process is introduced.

Early deployment copies shadow to active before period 0; waiting preserves
active. Both dealers refresh from shadow before period 1, including frozen
learners. A learning dealer updates only its chosen shadow entry with its own
gross reward, step size 1/2. Deployment costs never enter learning rewards.
Dealer 0 has A=(0,1,0), S=(0,0,1), as in selected state 140.

## Complete deterministic grid

Rival table q = c + permutation(-d,0,d), with all six permutations, c in
{-1/100,0,1/100}, and d in {1/1000,1/100,1/10}. This gives 54 distinct
non-tied tables in each of two families:

1. shadow_only: A1=(0,0,0), S1=q (initial action law unchanged when rival waits).
2. active_shadow: A1=S1=q (non-tied initial active and shadow values).

Keep the original all-zero rival as a separate baseline, not in either
54-case denominator: 109 initial states total.

Apply the same action rule to both dealers:

- Original epsilon-greedy, epsilon=1/10, uniform greedy ties.
- Smooth choice p(a)=epsilon/3+(1-epsilon)*softmax(Q/tau)(a), at tau in
  {1/10,1/4,1/2,1,2}, epsilon=1/10.

The uniform-exploration floor is matched; entropy, effective exploration, and
initial action distributions are not. The selected-action learning equation
is unchanged: this isolates smooth action selection, not a second learning
algorithm. All four early/wait profiles and four learning masks are evaluated
for every state/rule: 109*6*16 = 10,464 payoff cells.

## Contrasts, games, denominators

Primary: dealer 0 early minus wait, rival waits, own learning frozen, rival
learning enabled. Save all five expected outcomes (two dealer profits,
customer surplus, welfare, and units), period decomposition, and probability
of minimum ask 2. Report the same contrast with rival frozen and subtract it
from the primary contrast as an intervention-defined learning interaction.
It is not an identified unique mediation decomposition. Retain secondary
contrasts for both own-learning settings and both rival-release choices.

A strict gross conflict means focal profit > 0 and welfare < 0. Report both
the total contrast and the learning interaction; the former alone cannot
establish that learning is necessary. Evaluate the full 2x2 deployment game
at cost 1/20 per early dealer (fixed before results), with own learning off,
rival learning on. Compare pure best responses and the same-information,
same-profile-menu welfare maximizer. Unresolved comparisons remain unresolved;
no pure equilibrium does not mean no mixed equilibrium. Do not claim to solve
mixed equilibria here.

Counts refer to stipulated grid points, not independent populations or
estimated real-world prevalence. No significance tests, confidence intervals,
or power calculation on this fully enumerated finite grid.

## Arithmetic and failure rules

Greedy calculations use exact Fraction arithmetic. Smooth calculations use
outward-rounded Decimal intervals at 40 significant digits, repeated at 60.
Rational inputs/updates and settlements remain exact until conversion.
Interval operations enclose their operands; exp endpoints use correctly rounded
Decimal exp widened by one adjacent representable number on each side.
Trap overflow, underflow and subnormal operations. Never use floats for a
decision. An interval strictly above/below zero has that sign; an interval
containing zero is unresolved, unless it is exactly [0,0]. A separate
1e-12 economic-near-zero flag is descriptive, not a significance threshold.
These are numerical enclosures conditional on Python Decimal semantics and
our implementation, **not Lean certificates**. Precision agreement alone is
not a proof. Any incompatible enclosures, reference mismatch or accounting
failure blocks acceptance. Preserve failed outputs and exception records.

## Verification and deliverables

Tests first: arithmetic enclosure, known baseline fractions, ties, abstention,
accounting, action-rule invariances, selected-entry update, frozen refresh,
candidate-equals-incumbent placebo, invalid inputs, and create-only outputs.
Cross-check every greedy cell against the sealed independent evaluator.
Independently enumerate complete two-period histories for baseline, first and
last perturbed states at each smooth temperature, across the four profiles
with the primary mask. Reproduce the complete grid from a clean source copy.

Produce all-cell JSON, all-contrast CSV, complete family/rule tables, static
paper figures, a bounded mathematical note, and an assumption/code/test/result
ledger. Retain zero, opposite-sign, and unresolved cases. No main-paper edit,
new novelty claim, inherited formal-verification claim, or external-review
completion. Review-triggered corrections must be logged and versioned.

## Sources and reading scope

- Approved local v0.12 specification and sealed mechanism dossier.
- Arslantas, Yuceel and Sayin, *Strategizing against Q-learners*, v3:
  https://arxiv.org/html/2403.08906v3, Section II equations (1)-(2) motivate
  smooth choice with selected-action updates; our exploration mixture differs.
  This review does not claim a fresh full-paper or full-appendix reading.
- Python 3.11 Decimal documentation, exp and Context arithmetic:
  https://docs.python.org/3.11/library/decimal.html#decimal.Decimal.exp .
