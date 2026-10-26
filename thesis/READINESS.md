# Thesis readiness — 26 October 2026

Canonical draft: [thesis.pdf](thesis.pdf). Main source: [thesis.tex](thesis.tex).
This is a research draft for review, not an assertion of university acceptance, peer review, complete formalization or production safety.

## Completed in this revision

- Corrected the B2 macro input order, which caused compilation to fail before the completed result could enter the PDF.
- Rebuilt the thesis with B2's actual results, failed lead-time primary, and an explicitly post hoc seed-level sensitivity check.
- Documented the missing original model revision. The saved result contains `model_snapshot: null`; the default local Hugging Face cache has no matching Qwen2.5-14B run. No current revision was substituted for the unknown original.
- Reconciled 520 named declarations across the registry and public count documentation, and the 54 coverage rows (23 full, 18 conditional, 13 arithmetic). Fresh local Lean build and strict axiom audit passed. These counts are not full-manuscript proof coverage.
- Narrowed claims about uniform inference, shared-model behavior, fixed-window anti-gaming, and static admission to their stated assumptions. The standard estimator is now distinguished from the disclosed estimator that false-alarmed in controls.
- Listed B2 and the pending B3, H2 and K1 studies in the status appendix. B3 model diversity is distinct from completed B3v2 certificate-lifetime simulation.
- Added hash protection for 214 pre-existing experiment specifications, counters, frozen pipelines, notebooks, result artifacts and diagnostics. Verification never opens experiments.
- Added thesis verification, package regressions and current-PDF checks to the CI workflow. Removed the job that rebased generated audit receipts onto a newer main and pushed with skip-ci. Changed CI remains locally validated until a run on its own commit completes.
- Changed margin-monitor 0.2.0 to report `positive`/`negative` margin signs, with `stability_conditions_verified=false`. Added the static positive-feedback fixed-point solver and counterexample regressions. This is an API change from 0.1.0's `safe`/`unsafe` labels.
- Corrected invalid-number handling, state thresholds, signed position capacity and audit-field hashing in the older guard prototype.
- Withdrew the FPGA script's fixed timing, resource and power figures as measurements. Hardware reports now say `NOT_MEASURED`; neither physical timing nor compliance is established.

## What the completed evidence establishes

The central empirical pattern is a gap between deciding a reduced-form margin and identifying individual memories. C3 decides 23/25 margins and identifies 1/25 memories; F1 decides 24/26 and identifies 1/26. Most decisions persist without the feedback term, so these results do not validate dangerous endogenous feedback near the boundary. The ten completed empirical follow-ups retain all failures: 11 of 23 evaluated primaries pass, and another gated primary was not tested. Those counts exclude separately reported AI simulations.

B1 is a learning-rule simulation (all four primaries passed). B2 is a one-model language-model simulation: 0/15 control alarms, warnings before 30/30 crises but median lead 3.5 days below the five-day criterion, paired crisis delay median three days, and no crises in the shared-model arm because it abandoned momentum immediately. B2 does not establish behavior of AI traders in deployed markets. Its supplementary seed aggregation is post hoc; no registered evaluation was replaced.

## Still required for an academically complete submission

1. **Advisor decision on scope.** Decide whether the completed theory and mixed evidence form the submission thesis, with prospective studies as future work, or whether a specified study is essential. A percentage is not a substitute for an agreed thesis scope.
2. **Independent mathematical review.** Review the analytic arguments and cited probabilistic limit theory identified in [PROOF_REVIEW.md](PROOF_REVIEW.md). Kernel checks cover named statements under their encoded hypotheses; they do not establish novelty, every semantic bridge, or complete statistical theory.
3. **Co-author contributions and permissions.** Complete the existing co-authorship statement with the authors. No signature or permission has been inferred.
4. **Institutional format and approval.** Apply the university's required title page, committee/approval pages, deposit requirements and advisor edits once supplied. The current document is not represented as an approved university template.
5. **Model provenance recovery if possible.** Original Colab/Hugging Face cache or checkpoint metadata may identify the original B2 revision and dependencies. Local saved summaries cannot establish them. The limitation must remain if recovery fails.
6. **Observational inference.** EMA displacement, contemporaneous flow/noise independence, dependence across markets, nonstationarity and finite-sample bootstrap coverage remain modeling/statistical limits. A positive estimated margin is not general solvency certification.
7. **Hardware validation if claimed.** Obtain actual fresh tool reports, parse them, and independently verify the implemented design before making physical performance claims.

## Pending studies — not results

| Study | Current state | Earliest action |
|---|---|---|
| B3 model diversity | Registered, counter 0 | Run only through its frozen protocol with suitable GPU/model resources |
| K1 disclosed ETF feedback | Registered, counter 0; synthetic calibration only | Resolve authorized market-data access, then use frozen collection/analysis protocol |
| H1 participant records | Prospective, counter 0 | Confirm the external collector and coverage; analysis from 10 December 2026 subject to the gate |
| H2 crash-hour feedback | Prospective, counter 0 | Opens with H1; synthetic null calibration is not a market result |
| E2 deleveraging mechanism | Prospective, counter 0 | Analysis on/after 2 February 2027; open-interest proxy is not direct liquidation data |

No collector was launched, paid resource provisioned, registered counter changed, or future analysis opened by these changes.

## Reproduction

From repository root, with Python dependencies in `requirements-runtime.txt` and `requirements-artifacts.txt`, plus pypdf:

```sh
python thesis/verify_thesis_numbers.py
python thesis/checks/check_b2_supplement.py --check
python scripts/verify_thesis_release.py
PYTHONPATH=margin_monitor pytest margin_monitor/tests -q
sh thesis/build_thesis.sh
python scripts/verify_thesis_release.py --pdf
```

Lean requires the pinned Lean 4.34.1 and Mathlib revision; see the formalization directory. Build commands change generated outputs. The PDF build compiles in a temporary directory and replaces the canonical PDF only after successful compilation and reference checks. `THESIS_PYTHON` selects the interpreter for chapter generation.
