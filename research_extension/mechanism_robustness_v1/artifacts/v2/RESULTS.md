# Robustness results: finite stipulated states, not trained populations

Generated from the verified 60-digit run. Positive private profit and negative
gross welfare define a strict conflict. Each family/rule has 54 non-tied
states; the original tied baseline is separate. The primary contrast has
own learning off and rival learning on, with the rival waiting.

| Rule | Initialization | Total conflict | Learning-interaction conflict | Other total sign pairs |
|---|---|---:|---:|---|
| Epsilon-greedy | Shadow only | 18/54 | 18/54 | positive/zero: 18, zero/zero: 18 |
| Epsilon-greedy | Active + shadow | 18/54 | 18/54 | negative/zero: 18, positive/zero: 16, zero/zero: 2 |
| Softmax 0.10 | Shadow only | 54/54 | 54/54 | None |
| Softmax 0.10 | Active + shadow | 45/54 | 54/54 | negative/negative: 9 |
| Softmax 0.25 | Shadow only | 54/54 | 54/54 | None |
| Softmax 0.25 | Active + shadow | 51/54 | 54/54 | negative/negative: 3 |
| Softmax 0.50 | Shadow only | 54/54 | 54/54 | None |
| Softmax 0.50 | Active + shadow | 51/54 | 54/54 | negative/negative: 3 |
| Softmax 1.00 | Shadow only | 54/54 | 54/54 | None |
| Softmax 1.00 | Active + shadow | 51/54 | 54/54 | negative/negative: 3 |
| Softmax 2.00 | Shadow only | 54/54 | 54/54 | None |
| Softmax 2.00 | Active + shadow | 51/54 | 54/54 | negative/negative: 3 |

Signs in the final column are profit/welfare. The learning interaction
subtracts the frozen-rival deployment contrast. It is not a unique causal
mediation estimate. No Monte Carlo sampling or confidence interval is involved.

## Original tied baseline (not in the 54-case denominators)

| Rule | Gross profit change | Gross welfare change | Pure equilibrium at cost 0.05 | Planner |
|---|---:|---:|---|---|
| Epsilon-greedy | +0.06393750 | -0.01087500 | [[True, False]] | [[False, False]] |
| Softmax 0.10 | +0.06296710 | -0.01071078 | [[True, False]] | [[False, False]] |
| Softmax 0.25 | +0.04432786 | -0.00781474 | [[False, False]] | [[False, False]] |
| Softmax 0.50 | +0.01670505 | -0.00370519 | [[False, False]] | [[False, False]] |
| Softmax 1.00 | +0.00367214 | -0.00110217 | [[False, False]] | [[False, False]] |
| Softmax 2.00 | +0.00075041 | -0.00025820 | [[False, False]] | [[False, False]] |

Profiles use [dealer 0 early, dealer 1 early]; false means wait.
Decimal displays are rounded; all numerical bounds are in the source JSON/CSV.

## Costly deployment games over non-tied states

| Rule | Family | Unique pure NE outside planner set | Unique pure NE within planner set | Multiple pure NE | No certified pure NE | Unresolved comparisons |
|---|---|---:|---:|---:|---:|---:|
| Epsilon-greedy | Shadow only | 51 | 0 | 3 | 0 | 0 |
| Epsilon-greedy | Active + shadow | 18 | 36 | 0 | 0 | 0 |
| Softmax 0.10 | Shadow only | 48 | 0 | 6 | 0 | 0 |
| Softmax 0.10 | Active + shadow | 42 | 12 | 0 | 0 | 0 |
| Softmax 0.25 | Shadow only | 3 | 48 | 3 | 0 | 0 |
| Softmax 0.25 | Active + shadow | 12 | 42 | 0 | 0 | 0 |
| Softmax 0.50 | Shadow only | 0 | 54 | 0 | 0 | 0 |
| Softmax 0.50 | Active + shadow | 0 | 54 | 0 | 0 | 0 |
| Softmax 1.00 | Shadow only | 0 | 54 | 0 | 0 | 0 |
| Softmax 1.00 | Active + shadow | 0 | 54 | 0 | 0 | 0 |
| Softmax 2.00 | Shadow only | 0 | 54 | 0 | 0 | 0 |
| Softmax 2.00 | Active + shadow | 0 | 54 | 0 | 0 | 0 |

Cost is a real resource cost of 1/20 per early dealer. Profits and welfare
are net of that cost; learner rewards are not. All four feasible profiles
are compared. Multiple pure equilibria are not resolved by selecting a
favorable one; no mixed-equilibrium calculation is claimed.

## Complete sign inventory

| Rule | Family | Contrast | Denominator | Profit/welfare signs and counts |
|---|---|---|---:|---|
| Epsilon-greedy | baseline | frozen | 1 | zero/zero: 1 |
| Epsilon-greedy | baseline | learning | 1 | positive/negative: 1 |
| Epsilon-greedy | baseline | interaction | 1 | positive/negative: 1 |
| Epsilon-greedy | shadow_only | frozen | 54 | zero/zero: 54 |
| Epsilon-greedy | shadow_only | learning | 54 | positive/negative: 18, positive/zero: 18, zero/zero: 18 |
| Epsilon-greedy | shadow_only | interaction | 54 | positive/negative: 18, positive/zero: 18, zero/zero: 18 |
| Epsilon-greedy | active_shadow | frozen | 54 | negative/zero: 18, positive/zero: 18, zero/zero: 18 |
| Epsilon-greedy | active_shadow | learning | 54 | negative/zero: 18, positive/negative: 18, positive/zero: 16, zero/zero: 2 |
| Epsilon-greedy | active_shadow | interaction | 54 | positive/negative: 18, positive/zero: 18, zero/zero: 18 |
| Softmax 0.10 | baseline | frozen | 1 | unresolved/unresolved: 1 |
| Softmax 0.10 | baseline | learning | 1 | positive/negative: 1 |
| Softmax 0.10 | baseline | interaction | 1 | positive/negative: 1 |
| Softmax 0.10 | shadow_only | frozen | 54 | unresolved/unresolved: 54 |
| Softmax 0.10 | shadow_only | learning | 54 | positive/negative: 54 |
| Softmax 0.10 | shadow_only | interaction | 54 | positive/negative: 54 |
| Softmax 0.10 | active_shadow | frozen | 54 | negative/unresolved: 27, positive/unresolved: 27 |
| Softmax 0.10 | active_shadow | learning | 54 | negative/negative: 9, positive/negative: 45 |
| Softmax 0.10 | active_shadow | interaction | 54 | positive/negative: 54 |
| Softmax 0.25 | baseline | frozen | 1 | unresolved/unresolved: 1 |
| Softmax 0.25 | baseline | learning | 1 | positive/negative: 1 |
| Softmax 0.25 | baseline | interaction | 1 | positive/negative: 1 |
| Softmax 0.25 | shadow_only | frozen | 54 | unresolved/unresolved: 54 |
| Softmax 0.25 | shadow_only | learning | 54 | positive/negative: 54 |
| Softmax 0.25 | shadow_only | interaction | 54 | positive/negative: 54 |
| Softmax 0.25 | active_shadow | frozen | 54 | negative/unresolved: 27, positive/unresolved: 27 |
| Softmax 0.25 | active_shadow | learning | 54 | negative/negative: 3, positive/negative: 51 |
| Softmax 0.25 | active_shadow | interaction | 54 | positive/negative: 54 |
| Softmax 0.50 | baseline | frozen | 1 | unresolved/unresolved: 1 |
| Softmax 0.50 | baseline | learning | 1 | positive/negative: 1 |
| Softmax 0.50 | baseline | interaction | 1 | positive/negative: 1 |
| Softmax 0.50 | shadow_only | frozen | 54 | unresolved/unresolved: 54 |
| Softmax 0.50 | shadow_only | learning | 54 | positive/negative: 54 |
| Softmax 0.50 | shadow_only | interaction | 54 | positive/negative: 54 |
| Softmax 0.50 | active_shadow | frozen | 54 | negative/unresolved: 27, positive/unresolved: 27 |
| Softmax 0.50 | active_shadow | learning | 54 | negative/negative: 3, positive/negative: 51 |
| Softmax 0.50 | active_shadow | interaction | 54 | positive/negative: 54 |
| Softmax 1.00 | baseline | frozen | 1 | unresolved/unresolved: 1 |
| Softmax 1.00 | baseline | learning | 1 | positive/negative: 1 |
| Softmax 1.00 | baseline | interaction | 1 | positive/negative: 1 |
| Softmax 1.00 | shadow_only | frozen | 54 | unresolved/unresolved: 54 |
| Softmax 1.00 | shadow_only | learning | 54 | positive/negative: 54 |
| Softmax 1.00 | shadow_only | interaction | 54 | positive/negative: 54 |
| Softmax 1.00 | active_shadow | frozen | 54 | negative/unresolved: 27, positive/unresolved: 27 |
| Softmax 1.00 | active_shadow | learning | 54 | negative/negative: 3, positive/negative: 51 |
| Softmax 1.00 | active_shadow | interaction | 54 | positive/negative: 54 |
| Softmax 2.00 | baseline | frozen | 1 | unresolved/unresolved: 1 |
| Softmax 2.00 | baseline | learning | 1 | positive/negative: 1 |
| Softmax 2.00 | baseline | interaction | 1 | positive/negative: 1 |
| Softmax 2.00 | shadow_only | frozen | 54 | unresolved/unresolved: 54 |
| Softmax 2.00 | shadow_only | learning | 54 | positive/negative: 54 |
| Softmax 2.00 | shadow_only | interaction | 54 | positive/negative: 54 |
| Softmax 2.00 | active_shadow | frozen | 54 | negative/unresolved: 27, positive/unresolved: 27 |
| Softmax 2.00 | active_shadow | learning | 54 | negative/negative: 3, positive/negative: 51 |
| Softmax 2.00 | active_shadow | interaction | 54 | positive/negative: 54 |
