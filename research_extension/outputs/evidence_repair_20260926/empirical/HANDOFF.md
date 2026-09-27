# Empirical repair handoff

Use `final/report.md`, `final/coinbase_audit.json`, and
`final/binance_chronological_results.json` for integration. The initial artifacts
at this directory's root are preserved as the **preliminary snapshot**. Their
manifest still verifies, and `preliminary_generator.py` exactly matches its
recorded generator hash. The final generator source is
`research_extension/evidence_repair/empirical_report.py`.

The four numerical/sample artifacts are byte-for-byte identical between the
preliminary and final snapshots. The final report only changes reproduction and
overwrite instructions. No study design or numerical results changed after the
preliminary report was delivered.

Final manifest SHA-256:
`7be52134dd93faa18fa452bb0d6ca3799963f153baeb447922cf22301478618c`

Final Binance results SHA-256:
`5ace48e69772965325995027b968147115383b94a602c0d99ddf8f1b656e4446`

Final Coinbase audit SHA-256:
`fdfdd9f375554ff59de502617b1c74c79b85fe23f822436ef20e76fc819c1a55`

Input, source, output and test-receipt hashes in the final manifest were all
verified against disk after generation. The two cached inputs and both historical
result JSON files retain their original SHA-256 values.

## Findings for manuscript integration

| Sample / specification | F coefficient | SE | t | p | R² |
|---|---:|---:|---:|---:|---:|
| Legacy bivariate claim, unreproduced | .6866 | .2778 | 2.47 | .039 | .4330 |
| Serialized rows, bivariate | .518781819485 | .272815008616 | 1.901588267145 | .093738292833 | .311297015137 |
| Serialized rows, controlled | .370952992405 | .300894316568 | 1.232834825982 | .263746920310 | .518494330750 |
| Frozen cache, bivariate | .686638812316 | .283025244787 | 2.426069140341 | .041455688572 | .423872345153 |
| Frozen cache, controlled | .958333680272 | .387885377993 | 2.470662042560 | .048414233378 | .549207850403 |

Both samples contain ten assets; bivariate df=8 and controlled df=6. The historical
full-model values reproduce from the serialized rows. Neither sample reproduces
the joint legacy bivariate claim. Both are reported without favorable selection.
These regressions use outcome B to estimate slopes on the same assets and are
**in-sample explanatory associations**, not forecast evaluations.

The corrected Binance run retains all 50 requested seeds. It accepts 42 and
rejects 8 optimizer failures: AVAXUSDT 3, LTCUSDT 1, LINKUSDT 4. The seven complete
asset panels all have negative mean conditional validation R². DOGEUSDT is
-3784.32201858841 and ADAUSDT is -5.998576256841421; neither is clipped. Four
accepted LTCUSDT seeds have positive validation R², but its fifth seed fails;
no survivor mean or complete-panel cross-sectional regression is reported.
The complete-panel regression is explicitly **unavailable**. Failed fits are
scientific outcomes of the fixed run, not a reason to select favorable seeds or
change optimizer settings after inspecting validation.

The final report includes detailed safe manuscript wording, exact splits,
remaining timestamp/alignment limitations, and seed-level diagnostic references.

## Verification

- Initial regression run: **16 failed, 4 passed**, before implementation.
- Added overwrite-guard tests: **3 failed**, before the guard.
- Final targeted empirical tests: **23 passed**.
- Native scientific suites: **98 passed**; release tools: **6 passed**.
- Earlier shared integration run: **165 passed**.
- Final shared integration run: **168 passed, 1 failed**. Failure:
  `tests/test_q_learning_repairs.py::test_untrained_audit_abstains_and_does_not_consume_randomness`;
  newly present assertion expects `jac['dq_dx'] is None`, receives `0.0`.
  This is outside the authorized empirical write scope; no Q-learning files
  were modified for this repair. Full failure output is preserved in
  `tests_integration_final.txt` and bound by the final manifest.

The generator now refuses an existing output directory before computation and
uses exclusive artifact creation to prevent differing overwrites. Rerun only to
a fresh directory within the authorized empirical output subtree:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.11 -m research_extension.evidence_repair.empirical_report --output-dir research_extension/outputs/evidence_repair_20260926/empirical/fresh-run
```

No new data fetched, existing empirical results overwritten, paper edits,
commits, or agents used. Other ongoing shared-checkout edits were preserved.
