# Existing-paper revision, 29 October 2026

This revision corrects the earlier delivery of a separate blank manuscript.
It edits the existing work and retains its historical statements and evidence.
Preserving a statement is not a new correctness or novelty certification.

## Where the work appears

| Document | Source | New material |
| --- | --- | --- |
| Paper 1 | `ceiling_suite/papers/paper1/` | Introduction paragraph; economic decision appendix; returned information results and assumption failures |
| Paper 2 | `ceiling_suite/papers/paper2/` | Introduction paragraph; account, horizon, cost and decision definitions; all ten policies in the displayed comparison |
| Thesis | `thesis/thesis.tex` | Existing chapters retained; one common information-decision appendix |
| Synthesis | `ceiling_suite/papers/flagship/identify_certify.tex` | Existing synthesis retained; economic and returned-run extension |
| Journal layouts | `ceiling_suite/papers/versions/` | Regenerated from the same revised paper sources |

Mirrors in `ceiling_suite/paper1/` and `ceiling_suite/paper2/` are refreshed too.

## What the returned run supports

The original uploaded ZIP has SHA-256
`f51794914d7ac20059aaa458e2720bed4496564338468c470e487fda502c58ca`.
Its 35 manifest entries and eight core source files match the experiment.
The full profile completed, 12 targeted checks passed, and eight conditional
decision-logic lemmas compiled with Lean 4.19.0 without axioms reported.
This is an author-returned seeded reproduction, not independent replication.

There are 20 repetitions per regime. Policies, observation counts and budgets
share underlying tapes. The 16,800 policy rows are not 16,800 independent trials.
The displayed slice (32 reset readings, $1 loss budget, $1,000 initial wealth)
is illustrative, selected after execution; all outputs remain available.

In moderate feedback and near-boundary simulations, aggregate information
reaches the oracle's grid capacity although candidate cohorts remain mostly
unresolved. This does not establish a continuous-class identification rate.
Unpaid disclosure does not enlarge capacity in this slice; a hypothetical
one-cent disclosure fee lowers net expected log wealth. Disclosure does not
have a demonstrated positive net value here.

The manuscripts also show all seven regimes' tap-band and empty-set diagnostics.
Hidden slow memory, biased readings, correlated errors and changed behaviour
invalidate assumptions. No observed breach cannot repair an invalid contract.

The new account is an unlevered price-taking investor. It buys once, holds for
60 one-minute model periods, and closes with round-trip charges. It is separate
from a venue's admission policy or an equilibrium dealer model. Reading noise,
plant parameters, reset conditions and a finite candidate class are assumed
known. Training and validation add 768 and 384 reset episodes per repetition;
512 further paths evaluate the decisions. These are not ordinary public tapes.

## What remains pending

Numerical cells are deliberately empty for an untouched real-market test,
changing inventory with execution/funding, endogenous dealer or venue policy,
empirically calibrated disclosure costs, and independent replication.
The general separation theorem, continuous-class result, independent proof
review and exact novelty comparison remain open. The Lean check does not prove
these claims, Gaussian coverage, portfolio optimality, welfare or the full papers.

## Rebuild

The notebook and experiment are unchanged. To reproduce this editorial
integration from the returned ZIP, run from the repository root:

```bash
python studies/information_decision_20261029/integrate_existing_papers.py /absolute/path/to/returned.zip
python studies/economic_review_20261029/refresh_sources.py
python studies/economic_review_20261029/build_updated_pdfs.py --out /absolute/path/to/pdf-output
```

The first script verifies archive hashes and reads declared data files. It does
not execute uploaded source code. A LaTeX installation is required for the build.
The six compiled outputs were checked for unresolved references and overflow.
Original theorem/proof/table blocks were compared with the pre-revision sources.
The added pages and pending tables were rendered and inspected visually.
