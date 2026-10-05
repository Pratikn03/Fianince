# Review 4 — AI comparison, causality, and operational risk

## Scope

This pass inspected policy definitions, training/evaluation separation,
paired tapes, interventions, outcome definitions, and claims about AI or
safety.

## Findings

1. **High — the current result is a null against one adaptive non-AI
   controller, not evidence of no AI effect.** The three neural-minus-adaptive
   means are -0.090, -0.023, and +0.048, with intervals crossing zero and no
   seed clearing the 0.5-unit threshold.
2. **Medium — policy-family coverage is narrow.** There is no trained
   reinforcement-learning population, architecture sweep, or empirical-log
   causal design in this branch.
3. **High — intervention efficacy is not external validity.** The throttle
   reduces the local synthetic event rate from 0.090 to 0.000, but there is no
   second account, dealer, or market-capacity ledger to detect transferred loss.
4. **Medium — empirical exchange data are not connected to the agent study.**
   The L2 data currently calibrate observable descriptive targets only.

## Implemented remediation

- Kept the primary claim as “no AI-specific advantage is supported by this
  predeclared pilot threshold,” not “AI has no effect.”
- Preserved fixed, adaptive non-neural, and frozen-neural controls with common
  tapes and declared information.
- Added explicit loss-shifting and empirical-transfer limitations to the paper,
  task board, and publication packet.
- Kept external operational validation and matched empirical AI experiments
  pending.

## Residual status

The result is suitable as a scoped synthetic null and design demonstration,
not as a causal AI or safety conclusion.
