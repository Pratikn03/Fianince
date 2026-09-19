# Next-stage validation protocol

Status: frozen for the local confirmation run on 2026-09-18. The earlier
16-episode smoke run is exploratory and is not used as a headline result.

## Primary question

What can publicly available observations and declared adaptive policies
establish about feedback and operational loss at a stated economic cost, and
what remains unresolved under noise, dependence, and binding constraints?

## Synthetic matched-agent experiment

- Population: one independently specified single-asset synthetic market,
  three training seeds, and 128 paired held-out tapes per seed.
- Information at decision time: the seven-element public observation returned
  by `mm_next.market.SyntheticMarket`; no hidden shock or future price is
  exposed to an agent.
- Horizon: 48 steps.
- Capital and limits: initial cash 100, maximum order 0.5, maximum inventory 2.
- Frictions: spread 0.02, depth 5, impact 0.04, volatility 0.01, fees 0.001,
  partial fill range defined by `partial_fill=0.15`.
- Policies: fixed no-trade rule, adaptive non-neural linear controller, and
  frozen trained tanh MLP with 7 inputs and 8 hidden units.
- Training: deterministic cross-entropy population search, 8 iterations,
  population 24, three episodes per candidate, seeds 601, 602, and 603.
- Primary comparison: paired held-out gain difference between frozen neural and
  adaptive linear policies. A 0.5 currency-unit mean improvement is the
  predeclared minimum meaningful effect on a 100-unit account.
- Secondary outcomes: event rate, final equity, maximum drawdown, and training
  seed dispersion.

## Observation benchmark

The observation study varies exact/noisy prices, independent/dependent
episodes, missing records, and a constrained observation budget. The unit of
independence is an episode. The interval is an episode-block bootstrap, so it
is simulation-calibrated for the declared law rather than a theorem.

## Operational intervention experiment

The operational target is a nonterminal event (`halt`, `default`,
`margin_breach`, or `drawdown_halt`) in a difficult synthetic regime. The
predeclared interventions are no intervention, 50% execution throttling, and
inventory-triggered liquidation. Mean drawdown is a guardrail. No claim is
made about risk transfer because the environment has one trading account and
no external dealer ledger.

## Rejection and downgrade rules

- If the neural-minus-adaptive gain interval does not clear 0.5, the AI-specific
  hypothesis is not supported.
- If coverage is below the declared nominal level or wrong confident labels
  occur, the estimator is reported as a limitation, not upgraded to a theorem.
- If an intervention lowers the local event rate but the declared economic
  guardrail worsens, no benefit claim is made.
- Synthetic results do not become empirical market claims without an
  authorized order-book calibration and held-out validation.
