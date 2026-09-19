# Machine Markets research extension

This directory implements the locally actionable portion of the complete verification
plan while preserving the frozen master release. It does not claim that human external
replication, crypto calibration, trained-agent experiments, authorship review, or
publication review has occurred.

Run the extension from the master-release root:

```bash
PYTHONPATH=. python research_extension/run_extension.py
PYTHONPATH=. pytest -q research_extension/tests
```

The command writes generated artifacts to `research_extension/outputs/`:

- `evidence_manifest.json`: hashes and sizes for the current working release.
- `gate_status.json`: implemented, pilot, and pending gates.
- `runtime_manifest.json` and `runtime_audit.json`: source/configuration boundary record.
- `noisy_dependent_pilot.npz`: schema-complete pilot observations with costs, noise,
  missingness, partial fills, and within-episode dependence.
- `observation_summary.json`: dataset counts and cost/missingness summary.

The original `SHA256SUMS.txt` is intentionally not changed. The new manifest is a
working-release inventory, not an external authenticity attestation.

## What remains external

`specs/crypto_dataset_schema.json`, `specs/agent_run_schema.json`, and
`specs/operational_validation_schema.json` define the required interfaces for the
crypto replay, matched AI/non-AI study, and operational validation. Their status remains
pending until licensed data, independent reviewers, and experiment results exist.

