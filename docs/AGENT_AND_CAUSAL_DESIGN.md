# Matched agent and causal design

The controlled comparison holds the public observation vector, market tape,
horizon, capital, risk limits, fees, and execution rules constant. The agents
are:

- `fixed_rule`: no-trade non-adaptive baseline;
- `adaptive_linear`: hand-specified non-neural controller using current return
  and inventory;
- `frozen_neural`: a seven-input, eight-hidden-unit tanh policy trained by a
  deterministic population search on development tapes and frozen before
  held-out evaluation.

The design supports a narrow statement about this trained policy family in the
declared synthetic environment. It cannot identify a universal AI effect,
architecture effect, or real-market causal effect. The matched baseline is
especially important because the current result does not clear the preregistered
0.5-unit improvement threshold.
