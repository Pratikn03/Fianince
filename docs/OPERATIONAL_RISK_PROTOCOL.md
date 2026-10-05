# Operational-risk protocol

The declared operational event is any nonterminal environment outcome:
`halt`, `default`, `margin_breach`, or `drawdown_halt`. A normal terminal
settlement is not counted as an event. The confirmation regime uses initial cash
50, maximum order 1, maximum inventory 1, volatility 0.02, impact 0.30,
fee rate 0.002, margin rate 0.40, maintenance margin 0.10, and a 0.05 drawdown
limit. There are 256 paired held-out tapes.

Interventions are fixed before the run:

1. no intervention;
2. halve every requested order;
3. liquidate when normalized inventory exceeds 0.10.

The primary target is event-rate reduction. Mean drawdown and mean gain are
guardrails. Because this environment has one account and no external dealer
ledger, it cannot test whether losses are shifted to another party. That
limitation remains explicit.
