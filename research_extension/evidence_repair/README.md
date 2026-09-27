# Machine Markets: corrective revision, 26 September 2026

This file records the first corrective pass. The subsequent statistical and
mathematical repair is documented in `STATISTICAL_REPAIR_README.md`; its new
receipt supersedes current-build status from the earlier seal, not earlier data.

## Outcome and scope

This revision aligns the selected main manuscript, affected implementations and
regenerated results. It is a post-review correction, not a new confirmatory
experiment, a novelty certificate, or independent human review. It does not
establish a 10/10 paper or publication readiness.

The main document remains `paper/Machine_Markets_Final_Integrated_Paper.pdf`,
with the same title. The coordinated mathematical supplement remains beside it.
The starting files, including pre-existing uncommitted edits, are preserved in
the archive identified in `PROTOCOL.md`. Historical numerical outputs have not
been replaced. Main's commit remains
`1ec937cc512a12f8a36e887c20ce721bf675d87e`; this work is on
`codex/paper-evidence-repair-20260926`. No commit, push or submission is implied.

## What changed

| Area | Correction | Evidence boundary |
|---|---|---|
| Audited inference | Correct episode-level terminal regression, intercept, design rank, residual degrees of freedom and disclosed rates; invalid inputs abstain | Input validation does not authenticate a runtime or verify Gaussian independent episodes |
| Mathematical statements | Explicit rate/rank/reference-noise assumptions, unknown-rate counterexample, and equal aggregate disturbance law for stochastic equivalence | Restricted-model statements, not general nonlinear-agent theorems or a novelty claim |
| Finite-window witness | Figure recomputed from exact rational parameters | Agreement through lag 3 and subsequent divergence; not an indefinite equivalence claim |
| Learned-agent economics | All counterpart ledgers, consistent capacity allocation, absorbing halts with full-horizon valuation, isolated validation RNG and paired checkpoint clones | Inventory-only experiment; negative cash remains allowed and funding/liquidation are not modeled |
| Learned-policy audit | Recorded action visits required; unsupported response coefficients suppressed | All ten policies abstain; neither certification nor model-class falsification is established |
| Coinbase statistics | Both frozen row and cached samples regenerated and separately reported | In-sample associations, not out-of-sample forecasting |
| Binance dynamic fits | Ordered training prefix, carried state, chronological validation and retained failed fits | Eight failures; no survivor-only regression or validated structural identification |
| Public-data proxy simulation | Correct price/flow units, full implemented Jacobian, counterparty accounting, uncertainty, cost and data provenance | Not historical event-book or exchange-execution calibration |
| Manuscript integration | Generated tables, population-level figure, corrected abstract/conclusion and method/claim links | Correction-specific traceability, not an exhaustive proof/code equivalence certificate |

## Findings after correction

- Ten tabular policies were retrained for 100,000 transitions each under the
  recorded specification. Each was evaluated on ten fixed common tapes in
  frozen, active and validation-frequency-calibrated arms, plus twenty baseline
  runs: 320 nested runs, **not 320 independent populations**.
- Active-minus-frozen mean absolute displacement is -0.00022736, with a
  population-level 95% t interval [-0.00065870, 0.00020398], conditional on those
  fixed tapes. This does not establish a zero effect or equivalence.
- Frozen-minus-no-trade displacement is +0.00070488, with interval
  [0.00013305, 0.00127670]. Lower displacement is not itself a welfare measure;
  there is no demonstrated learned-policy advantage over no-trade here.
- All ten structural response screens abstain for insufficient recorded action
  support. A constant or unvisited local response is not evidence that a policy
  violates the positive-memory model.
- The previous Coinbase combination (t=2.47, p=.039, R²=.4330) is not reproduced
  jointly by either saved bivariate sample. The paper reports both samples and
  controlled specifications without selecting the favorable one.
- Binance accepts 42 of 50 requested seed fits and retains eight failures.
  All seven fully completed asset panels have negative mean conditional
  validation R². A complete-panel association regression is unavailable.
- The proxy study consumes 18,445,389 bytes from nine historical kline archives
  and three separate REST depth snapshots. Only one consumed file has a matching
  cached official checksum. Snapshot capture timestamps are not established.
- Synthetic halt scenarios have correct full-horizon ledgers and exact binomial
  intervals. Capacity, cash and noise co-vary in the scale diagnostic: it does
  not isolate a capacity intervention or establish welfare improvement.

## Authoritative artifacts

All paths below are relative to
`research_extension/outputs/evidence_repair_20260926/`:

- `learned_agents_v2/`: authoritative corrected training/results/checkpoints.
  `learned_agents/` is the first corrective run, before reporting-label cleanup;
  it is not another independent study. Smoke and development runs are retained.
- `empirical/final/`: authoritative Coinbase and Binance numerical audits.
- `gate24/gate24_summary.json`: compact, correctly scoped public-data summary.
  Its metadata distinguishes the frozen numerical-run source from the later
  labeling correction. `gate24/final/` preserves that numerical run.
- `paper_artifacts.json`: generated tables/figure coordinates and exact witness.
- `verification/final/`: final command receipts, clean-copy comparisons and the
  correction-specific integrity manifest, once generated by the recorder.

`claims.json` links corrected assertions to assumptions, tests, outputs and
permitted wording. This ledger does not cover every historical appendix claim.
Earlier worker handoffs contain intermediate test counts and failures; the
final verification receipt supersedes those status snapshots, not their data.

## Reproduction

Run from the repository root with Python 3.11. No network or paid compute is
required. Result runners refuse existing destinations. Use a fresh destination
for every reproduction; do not replace the authoritative results.

```sh
python3.11 -m pytest -q tests research_extension/tests reference_directory/test_mathematical_supplement.py
python3.11 tools/run_all_tests.py --log-dir /tmp/machine-markets-native-new
python3.11 reference_directory/run_checks.py
python3.11 -m research_extension.evidence_repair.check_evidence

python3.11 -m research_extension.evidence_repair.run_learned_agents --output research_extension/outputs/evidence_repair_20260926/learned-new
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.11 -m research_extension.evidence_repair.empirical_report --output-dir research_extension/outputs/evidence_repair_20260926/empirical/new
python3.11 -m research_extension.gate24_public_data.gate24_analysis --offline --output-dir research_extension/outputs/evidence_repair_20260926/gate24/new

python3.11 tools/build_paper.py --output /tmp/Machine_Markets_Corrected_New.pdf
python3.11 -m research_extension.evidence_repair.check_evidence --seal research_extension/outputs/evidence_repair_20260926/verification/final/correction_manifest.json
```

The final clean-copy check uses a local clone of the starting commit with the
corrective sources, required cached inputs and artifacts explicitly overlaid.
It is **not** reproduction from a published correction commit. The receipt
records the path and source hashes. Corrected training and empirical numerical
JSONs match byte-for-byte; Gate24 comparisons separate numerical equality from
changed labels, code hashes and the absolute checksum-sidecar location.

The historical `SHA256SUMS.txt` remains unchanged. Consequently
`python3.11 tools/verify_master.py --strict` still fails for the revised checkout;
the old seal must not be presented as certifying this revision. The separate
correction manifest checks its explicitly listed files and does not silently
rebaseline the frozen release or claim completeness of unlisted files.

## Highest-value next work

1. Obtain an independent mathematical/economics review of the restricted
   identification claims and the finite-window construction. Internal checking
   does not close that gate.
2. Select one economic contribution for the main argument and compare it
   explicitly with its nearest predecessors. More experiments do not establish
   novelty, and this correction did not perform a new comprehensive literature
   review.
3. If testing learning spillovers next, use an explicit dealer objective,
   customer surplus, resource costs and a common pre-deployment state. Lock a
   separate protocol and unused evaluation seeds before training. The current
   inventory-only experiment is not that multi-dealer deployment game.
4. Acquire event-level data only for a specified calibration question, with
   lawful use, timestamp alignment and measured-versus-modeled execution kept
   separate. Cached snapshots cannot complete this requirement.
5. Human authors confirm contributions, rights, disclosure and venue choice.
   Submission and publication acceptance remain separate external decisions.

The revision improves defensibility by removing unsupported conclusions. It
does not convert negative findings into favorable results or complete the
entire research and publication program.
