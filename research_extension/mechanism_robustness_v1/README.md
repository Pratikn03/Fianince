# Machine Markets: initialization and smooth-choice robustness

This separately versioned study tests the selected v0.12 economic example
without changing the main paper or earlier sealed evidence.

## Result in one paragraph

The learning-related profit–welfare conflict is **not solely a tied-value or
epsilon-greedy artifact**. It survives all 54 non-tied rival tables in each
of two initialization families at each of five tested softmax temperatures.
However, that does not make early deployment universally privately desirable:
with both active and shadow values perturbed, the **total** gross conflict
holds in 45/54 cases at temperature 0.10 and 51/54 at each other temperature.
Ordinary immediate competition offsets the later learning benefit in the
remaining cases. At a real deployment cost of 0.05, temperatures 0.50, 1 and 2
yield mutual waiting as the unique pure equilibrium and planner choice at
every tested state. A robust learning effect is not a universal inefficient
deployment equilibrium.

These are deterministic comparisons of **stipulated initial states**, not
trained populations, a random sample, real-market evidence, or an estimate of
how often the mechanism occurs in practice.

## Deliverables

- [Complete result tables](artifacts/v2/RESULTS.md), including null and
  opposite-sign cases, numerical unresolved cases, and all pure-game counts.
- [Robustness figure](artifacts/v2/robustness_counts.png): full 54-case
  denominators, total contrast versus learning interaction.
- [Profit–welfare figure](artifacts/v2/profit_welfare.png): all 108 non-tied
  points per rule, common axes, no fabricated confidence intervals.
- [All contrasts](artifacts/v2/all_contrasts.csv): 39,240 outcome rows,
  exact rationals or outward bounds, period decomposition and near-zero flags.
- [Theory and proof](THEORY.md): a restricted smooth-choice welfare-sign
  proposition, the immediate-profit expression, continuity argument, and limits.
- [Protocol](PROTOCOL.md) and [timestamped lock](protocol.lock.json).
- [Verification](verification/reviewed/report.json) and
  [post-hoc formula diagnostic](verification/reviewed_theory_check.json).
- [Claim ledger](claims.json) and [execution notes](EXECUTION_NOTES.md).

## What was evaluated

109 states (108 perturbations plus the original tied baseline), six action
rules, four deployment profiles and four learning masks: **10,464 payoff
cells**. Shadow-only changes preserve the initial rival action law when it
waits; active-plus-shadow changes deliberately do not. The softmax mixture
retains the baseline 10% uniform-exploration floor, not its entropy or action
distribution. The selected-action reward update remains unchanged.

Each period contains independent asset/customer draws. All finite histories
are integrated; there is no Monte Carlo seed, burn-in, training sample, held-out
population, or uncertainty interval from sampling. Numerical bounds quantify
rounding enclosure only. Greedy calculations use exact rational arithmetic.
Smooth calculations use outward Decimal intervals at 40 and 60 digits.

The primary contrast is focal early deployment minus wait, with rival waiting,
focal learning frozen and rival learning on. Its learning interaction subtracts
the otherwise identical contrast with rival learning frozen. All other
own-learning/rival-release strata are saved, not pooled into the headline.

## Proof boundaries

The new mathematical note proves a negative **gross welfare** contrast for
any finite rival active/shadow values within its stated smooth H2 model. It
does not prove an always-positive private gain. The proof uses explicit
participation accounting and monotonicity of the rival's softmax low-ask
probability. It was developed after inspecting the grid and is labeled
accordingly. The two derived formulas match 1,090 numerical comparisons over
545 state/temperature cases; those checks are not a substitute for proof.

This is an elementary model-specific result, not a novelty certificate.
Strategic teaching is established literature. The model's welfare variation
depends on participation at a statically dominated low ask. Longer horizons,
endogenously generated candidate policies, alternative learning update rules,
and a less restricted economic environment remain open. No new Lean claim,
external human-review completion, real-market claim, or systemic-risk claim
is made.

## Reproduce

Use Python 3.11 from the repository root. Fraction/Decimal calculations need
only the standard library; testing uses pytest and figures use matplotlib.
All destinations must be new. The protocol is already locked: **do not rerun
`--lock` or delete the existing outputs to reuse their names**.

```bash
python3.11 -m pytest -q -p no:cacheprovider research_extension/mechanism_robustness_v1
python3.11 -m research_extension.mechanism_robustness_v1.run --precision 40 --output /new/path/p40
python3.11 -m research_extension.mechanism_robustness_v1.run --precision 60 --output /new/path/p60
python3.11 -m research_extension.mechanism_robustness_v1.verify --p40 /new/path/p40 --p60 /new/path/p60 --output /new/path/verification
python3.11 -m research_extension.mechanism_robustness_v1.artifacts --results /new/path/p60 --verification /new/path/verification/report.json --output /new/path/figures
python3.11 -m research_extension.mechanism_robustness_v1.theory_check --output /new/path/theory_check.json
```

`theory_check` uses this package's preserved `results/reviewed_p60`. The verifier checks
all 1,744 greedy cells against the earlier sealed evaluator, 60 selected smooth
cells against a separately written 100-digit full-history calculation, every
numeric value across the two precisions, and the whole grid in a clean source
copy. The copied executable sources are hashed before and after execution.

The accepted runs are `results/reviewed_p40` and `results/reviewed_p60`.
Earlier runs and `verification/first` remain as superseded execution records.
Review found three failure-handling weaknesses; regression tests reproduced
and fixed them. The corrected runs' entire numerical result blocks are
byte-identical to the originals. See [correction comparison](verification/review_correction_comparison.json).

Both earlier manifests (23 and 60 files) and five manuscript/source files are
checked against locked hashes. The old reference worktree was not changed.
The current branch remains unchanged, with this study added only as untracked
files. Nothing was committed, pushed, sent, or submitted.

## Numerical interpretation

Softmax zero effects often return an interval containing zero; those remain
`unresolved` in the numerical inventory, even when a separate argument proves
a null. Do not relabel all small numbers as exact zero. Strict signs require
an entire interval on one side of zero. All effect sizes are in model units.
Costly games compare the same four feasible profiles for owners and planner;
multiple pure equilibria are retained and mixed equilibria are not computed.

## Literature and disclosure

The smooth-choice benchmark is motivated by the softmax/selected-action setup
in [Arslantas, Yuceel and Sayin, Section II](https://arxiv.org/html/2403.08906v3).
Our exploration mixture and restricted deployment game differ. This does not
establish priority over strategic teaching or earlier learning-market models.
The code, proof note and internal review are AI-assisted; they do not substitute
for independent human economics, mathematics or reproducibility review.
