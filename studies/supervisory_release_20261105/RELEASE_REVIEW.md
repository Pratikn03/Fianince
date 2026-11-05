# Paper 1 preprint review release — 5 November 2026

This is a conditional theory working paper with existing empirical diagnostics. It has not been submitted to SSRN, accepted by a journal, or independently refereed. No score or journal-acceptance prediction is supplied.

## Completed in this release

1. Installed the pinned Lean 4.34.1 toolchain and built the entire current proof project locally, rather than relying solely on a historical receipt or CI queue.
2. Added eight exact-witness theorems: Gauss/Radau node bounds, positive and normalized weights, three matched moments, the third-moment gap, a constructed dominant-intensity gap, aggregate-budget closeness, and a Gaussian price-record testing bound. The intensity bound holds for spacing at most u/3, covering the new accounting example with u=0.4 and spacing 0.1.
3. Added eight decision theorems: robust thresholds, an unsafe-halt bound under the actual product Gaussian law, its risk-budget consequence, two no-data lottery optima, information break-even, optional purchase, and robust fallback feasibility.
4. Extended the experiment with the conservative Chebyshev gate that the probability proof actually covers. The earlier normal-quantile rule remains clearly distinct. Both sets of 2,304 configurations are retained, including negative paid-information values.
5. Rebuilt both manuscript versions, updated verification scope and narrowed remaining interpretation claims. Corrected the description of the Rayleigh–Hölder result from an exact cheapest probe to a lower bound.
6. Added a fresh strict axiom audit with active manuscript, figure and proof-source hashes. Supporting declaration counts are not percentages of manuscript completion.

## What the new proofs do not claim

- No unconditional all-K supervisory construction: that extension retains an explicit gap hypothesis. The exact new construction is for K=2.
- No claim that reported class positions directly measure the post-halt feedback budget. The scalar disclosure law is an explicit, hypothetical contract.
- No formalized normal-quantile identity; the actual-event probability theorem covers the conservative gate.
- No general strategic equilibrium, empirical welfare estimate or universal market-safety guarantee.
- No independent proof review, exhaustive novelty certificate or full-manuscript Lean equivalence. Referenced classical results and inherited supplementary arguments remain separately identified.

## Human review record

| Reviewer | Required check | Recorded outcome |
|---|---|---|
| Pratik | Economic institution, executable target label, actions, costs and holding horizon | Not supplied in this session |
| Prashant | Exact witness, observation laws, testing reduction and finite-horizon scope | Not supplied in this session |
| Sujan | Robustness allowance, gate event, source-to-result reproduction and independent calculations | Not supplied in this session |

These assignments are proposed checks, not a claim that anyone has performed them. Each author should review the complete manuscript; the division above identifies additional focal checks.

## Before submission

Confirm all coauthors' approval, author names/affiliations, funding and conflicts, data/code sharing permissions and any institution-specific requirements. A journal-specific submission package additionally needs a chosen journal and its current formatting/declaration requirements. AI cannot attest to these facts or substitute for independent review. The paper may be circulated for those reviews without representing them as completed.

## Reproduce

From the repository root, with the pinned Lean toolchain and NumPy/SciPy:

```sh
python studies/supervisory_release_20261105/run_study.py
cd research_extension/current_manuscript_lean_20261008
lake exe cache get
cd ../..
python studies/supervisory_release_20261105/tools/verify_release.py --project research_extension/current_manuscript_lean_20261008 --repo .
cd ceiling_suite/papers/paper1
latexmk -pdf -interaction=nonstopmode -halt-on-error paper1_ssrn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error paper1.tex
```

The release verifier checks every named project theorem and every CurrentMM constant for nonstandard axiom dependencies. It deliberately records `full_manuscript_formalization_complete: false`.
