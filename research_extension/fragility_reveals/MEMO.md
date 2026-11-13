# Scoping memo: does fragility reveal the traders? (11 November 2026)

Numerical scoping by an AI system; not a proof and not independent review.

**Question.** In Paper 1's model, does information about trader composition grow as the market approaches
instability (feedback budget S -> 1)? If yes, "markets reveal their traders only when about to break" would be
a new and surprising result.

**Method.** Gauss and Gauss-Radau K-group pairs (K = 2, 3), persistence a raised so that 1 - S falls from 0.2 to
0.003. Active information: squared norm of the impulse-response difference. Passive information: Gaussian KL rate
between the stationary price processes. `fragility_scan.py`, `fragility_scan_matched.py`, results in JSON.

**Results.**

| Pair | Active information | Passive information |
|---|---|---|
| Same a (budgets differ by order (spacing)^(2K-1)) | grows like (1 - S)^-3 | grows like (1 - S)^-1 |
| Same S (a adjusted) | grows like (1 - S)^-1 | bounded: exponent about 0 |

**Reading.** The growth with a common a comes from the small difference in the budgets, which near instability
becomes visible. Holding the budget fixed, passive data about composition do not improve at all as the market
nears instability. Active probing improves by a factor (1 - S)^-1, but probing a market on the edge of
instability is not a policy.

**Verdict.** The surprising version fails. What survives is a robustness statement for Paper 1: the barrier to
identifying traders from passive prices does not lift near a crash; only the distance to instability becomes
visible. It is a useful proposition, not an 85+ result. Related work: Costa et al. (2026) show the distance to
criticality itself is hard to estimate in Ornstein-Uhlenbeck systems near threshold.
