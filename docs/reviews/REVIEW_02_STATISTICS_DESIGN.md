# Review 2 — statistical design and denominators

## Scope

This pass checked estimands, counting units, splits, uncertainty summaries,
paired comparisons, and the observation and intervention experiments.

## Findings

1. **High — the observation result is simulation-calibrated, not theorem-level
   coverage.** The noisy/dependent benchmark reports 0.790 coverage and 0.075
   wrong-confident calls in 200 declared replicates, but those are properties
   of the implemented law and bootstrap procedure.
2. **Medium — the AI comparison has limited policy and seed support.** Three
   training seeds and 128 paired held-out episodes per seed support a scoped
   pilot null, not a general AI/non-AI causal conclusion.
3. **Medium — the intervention event is local to one synthetic account.** The
   throttle result changes event rate and drawdown in the same account; it does
   not identify externality or loss shifting.
4. **Low — the empirical L2 summary averages daily metrics.** It must not be
   read as a snapshot-level confidence interval or as a test of a calibrated
   stochastic simulator.

## Implemented remediation

- Kept episode, training-seed, paired-tape, and calendar-day units explicit in
  the claim ledger and paper.
- Preserved per-seed bootstrap intervals and the predeclared 0.5-unit effect
  threshold rather than aggregating away the seed-level result.
- Added a separate L2 report that labels all depth/trade summaries as
  descriptive held-out targets and states the absence of fill/spread inference.
- Reframed the paper's intervention text as a conditional single-account
  result.

## Residual status

No externally collected noisy/dependent observation benchmark or operational
intervention study has been run. These remain synthetic evidence only.
