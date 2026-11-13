# Machine Markets: what a top-level version of Paper 1 and Paper 2 would have to contain (13 November 2026)

Written by an AI system for the authors; judgement, not independent review.

This is a blueprint, not a paper. A paper at the level the authors want needs results that do not exist yet.
Writing the paper first and hoping the results follow would mean claiming things that are not established, so
each part below is marked **have**, **partial** or **missing**, with the work that would produce it and the
outcome that would kill it. Even if every missing part succeeds, a rating above 90 is possible, not likely.

## Why the current papers stop near 80

| Limit | Paper 1 | Paper 2 |
|---|---|---|
| Mathematics | Applies known mixture and moment theory | Applies known theory of estimating functionals and of induced gains |
| Evidence | No direct test: class positions, not tagged flow | 10 of 25 tests fail; the guard did not reduce realized tail losses |
| Stakes | Shows a cost, not that anyone pays it | Shows a certificate, not that it prevents a loss |

A top-level version has to remove one limit in each column, not polish the text.

## Paper 1 redesigned: "Who trades cannot be learned from prices: a law and its measurement"

**One sentence.** The data needed to tell trader groups apart from prices grows as a fixed power of how similar
they are, and real markets obey that law.

| Pillar | Content | Status | Work | What would kill it |
|---|---|---|---|---|
| 1. The law | Sufficiency of the kernel; cost of order (spacing)^-(4K-2), matched above and below; tags remove it | **Have**, machine-checked | Proof check by the authors | An error in the lower bound or the Prony step |
| 2. The law in data | In account-level data, the precision with which prices recover accounts' memories falls with their spacing at the predicted exponent, across many markets, while the accounts' own records recover them at the usual rate | **Missing**. H1 (registered, opens 10 December) tests whether records separate memories where prices do not. It does not test the exponent | After H1: a new registered test of the scaling law on Hyperliquid days that H1 did not use. Specification simulated, approved and pushed before any of those days is read | H1 fails; or the fitted exponent is far from the prediction; or accounts' memories are not stable enough to measure |
| 3. The law has a price | The cost of learning composition, in money, set against what real regimes spend (the audit-trail budgets), with the account-level estimates as inputs instead of illustrative parameters | **Partial**: the calibration and the dollar comparison exist with illustrative inputs | Redo the calibration with the H1 estimates | The measured spacing is so wide that composition is cheap in the markets that matter |
| 4. Beyond the model | One theorem that holds for any population, not only linear rules with exponential memory, and is not a restatement of sufficiency | **Missing**. The current general statements (any flow map; lower bounds over any class containing the linear rules) are short | Open research. Candidate: a lower bound stated through a geometric quantity of the class of flow maps, with the mixture rate as a special case. Novelty must be checked against the statistics literature before any claim | The candidate turns out to be known, or false |

**If pillars 1–3 hold:** a strong paper with a measured law, roughly mid 80s. Pillar 4 is what would separate it
from an application of known rates.

## Paper 2 redesigned: "Machine Markets: certifying safety without knowing the traders"

**One sentence.** A market's safety can be certified from prices at a cost that does not depend on who trades,
and acting on the certificate prevents losses.

| Pillar | Content | Status | Work | What would kill it |
|---|---|---|---|---|
| 1. The certificate | Risk depends on traders through the summed response; certified at the parametric rate with one logarithm; the guard is the largest safe rule; it cannot be gamed except by making the market safer | **Have** (Paper 2 and thesis chapter 4) | Proof check; one headline instead of three | An error in the certification rate or the maximality proof |
| 2. Decided but not identified | The safety decision is reached in markets where memories cannot be identified | **Have**, registered: 22 against 1, 22 against 0, 23 against 0 | Move from the thesis into the paper, with the caveat that these markets were far from the boundary | Nothing; it is run. Its weight is limited by that caveat |
| 3. The certificate warns | A low certified margin precedes stress, prospectively | **Partial**. It forecast next-day variance (passed) but not extreme moves or stress-day damage (failed). E2 is registered and cannot run before 2 February 2027 | Run E2 once when it opens. Consider one further prospective test near the boundary, registered first | E2 fails |
| 4. The guard prevents losses | Acting on the certificate lowers realized losses | **Missing, and the one registered attempt failed** (G1: tail loss 4.5% higher) | The hardest part. Options: (a) natural experiments, where a venue changed leverage or position limits, with the certificate predicting which markets benefit, registered before the data; (b) a deployed guard in a small on-chain market or a testnet with real participants. Both need new design and, for (b), partners and money | No venue change predicts as the theory says; or the deployed guard does nothing |
| 5. Agents that matter | The certificate works when the traders are learning systems, not fixed rules | **Partial**: simulations with simple learners and one open language model | Larger agent experiments, registered, with stronger models | The certificate fails against capable learning agents |

**If pillars 1–3 hold and E2 passes:** low to mid 80s. Pillar 4 is what a top general-interest journal would ask
for, and it is the pillar with a failed test behind it.

## Order of work

1. Authors check the proofs of pillar 1 in both papers.
2. Submit the current Paper 1 to JEDC and post both papers. The redesign does not need to delay this; a paper
   under review can gain pillars 2 and 3 at revision, or they can form a new paper.
3. 10 December: run H1 once.
4. If H1 passes: write, simulate, approve and push the scaling-law specification; then run it once.
5. 2 February 2027: run E2 once.
6. Design the guard test (pillar 4 of Paper 2) with the co-authors; register it before any data.
7. Only then rewrite either paper around what the tests showed, pass or fail.

## What is not in this blueprint

- No result is assumed. A failed test is reported and the paper is written around what held.
- No new theorem is promised. Pillar 4 of Paper 1 is a research question.
- No rating is promised. The estimates above are one reader's view.
