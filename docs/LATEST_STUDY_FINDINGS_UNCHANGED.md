# v0.5 findings and open requirements

## The result in one sentence
Publicly verified memory dynamics can support a conditional tail and gain estimate, but those estimates do not certify a financially constrained system; operational risk requires a separate target and observation protocol.

## What was actually completed
The integrated paper now has 47 pages. Sections 14–16 add auditable-tail logic, observed-price inference, fixed-budget input/endpoint experiments, binding financial constraints, finite-horizon probability inference and controls. All previous findings remain labeled in the manuscript. This is synthetic, uncalibrated, CPU-only research, not a real-market validation or deployment.

### Hidden-tail assumptions
For complete positive geometric memory with total gain at most Q and every update rate at least eta0, the omitted kernel mass after H steps is at most Q(1-eta0)^H. Public exact rates additionally make the tail a linear regression contrast. This is a standard conditional bound, not a new general theorem. The assumptions are justified only within the released controlled source/configuration. A digest and manifest cannot prove that a proprietary deployment has no omitted memory, inventory or execution feedback. Omission of a slow state produced 80/80 false-stable calls in its failure control. Authentic outside source/configuration review remains required.

### Observation-budget result
The fresh-seed paired endpoint study used the same price paths and estimator in both branches. Each cell below has 240 panels. Wrong confident calls are included in the definite counts.

| Independent episodes | Fixed 64-step endpoint: definite | Wrong | Preassigned diverse endpoints: definite | Wrong |
|---|---:|---:|---:|---:|
| 32 | 26 (10.83%) | 0 | 75 (31.25%) | 2 |
| 128 | 86 (35.83%) | 0 | 112 (46.67%) | 1 |
| 512 | 159 (66.25%) | 1 | 144 (60.00%) | 0 |

Diverse endpoints help at small budgets but not the largest. Earlier repeated small round trips do not outperform an impulse at equal gross volume. Energy and inventory costs differ. The strongest disclosure branch knows rates, exact resets and exact midquotes; it must not be presented as an equal-information win over the older black-box study.

### Binding financial constraints
The simulator enforces inventory, leverage including spread fees, credit and dealer limits; margin breaches can force liquidation and dealer breaches can halt trading. The primary 24-setting study has 491,520 setting-trajectories but only 163,840 unique exogenous tapes because funding counterfactuals are paired. Limits alter 12,388,550 order requests and generate 2,240,614 account-step margin calls. These are repeated operational counts, not unique crises.

A separate preloaded-dealer experiment has 65,536 episodes. For a stable isolated signal model with a+sum(q)=0.82, one scenario halts in 45.42% of 8,192 episodes. This is a constructed model-specific illustration of the difference between signal stability and operational safety, not a real-market probability or uniquely AI-caused effect.

Operational probability intervals concern default, halt or an adaptive-account drawdown exceeding 20% in 64 steps. They do not require linearity but do require independent repetitions of the specified scenario. The primary probability settings are near-zero/near-one easy cases; high decisiveness there does not establish general low-budget performance near a risk threshold.

## Verification completed
- 98 tests: 24 new plus 74 inherited.
- The standalone verifier imports no project modules: 4,320 regression rows, 2,880 tail intervals, 2,880 binomial intervals, 500 fill-projection LP checks, 24 public-price reconstruction checks and 64 example ledgers.
- A complete fresh-directory rerun matched 19 scientific CSV files byte for byte and all 566 arrays in 82 archives exactly in this environment. Runtime metadata is not a scientific equality criterion.
- The original 875 algebra checks were rerun.
- All 47 PDF pages were rendered; key tables and updated sections were visually inspected. No unresolved references or overflowing text boxes remained.

## Not completed
1. **Independent external replication/proof review:** no outside person or institution has performed it. Separate assistant-written code and a fresh directory are internal checks only.
2. **Authenticated runtime audit:** the released manifest does not secure configuration truth or channel completeness.
3. **Calibrated exchange/agent transfer:** no real order book, trained neural agent population, proprietary data or live intervention is used.
4. **Practical observation costs and errors:** exact midquotes, verified resets, known rates and independent episodes may be unavailable. Develop and test noisy-regressor and dependent-record inference rather than silently reusing this theorem.
5. **Novelty and publication assessment:** the proof tools are established regression, positive-system bounds and binomial inference. Literature priority and economic significance need independent evaluation; no paradigm-level result is claimed.

## The next decisive experiment
Have an independent team implement the inference from the paper alone and test it in a second, calibrated market environment with genuinely binding limits. Require that team to verify the disclosed state inventory and report both unresolved cases and incorrect labels. The released challenge files and reviewer form support that task, but do not substitute for it.
