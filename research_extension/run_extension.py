#!/usr/bin/env python3
"""Generate local evidence-freeze and observation-study extension artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_extension.observation_study import ObservationConfig, generate_dataset, summarize_dataset
from research_extension.release_extension import build_evidence_manifest, gate_status
from research_extension.runtime_audit import AuditTrace, build_manifest, validate_trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    source = root / "studies/audited_constraints/src/audit.py"
    runtime_manifest = build_manifest(source, {"reset": "zero", "execution": "linear"})
    trace = AuditTrace(runtime_manifest)
    for channel in ("memory", "inventory", "funding", "execution", "reset"):
        trace.record(0, channel, "observed")
    runtime_result = validate_trace(trace)

    config = ObservationConfig(episodes=128, horizon=64, seed=20260918, dependent=True,
                               noise_sd=0.05, missing_rate=0.02)
    dataset_path = output / "noisy_dependent_pilot.npz"
    data = generate_dataset(config, dataset_path)
    study_summary = summarize_dataset(data)

    (output / "evidence_manifest.json").write_text(
        json.dumps(build_evidence_manifest(root), indent=2) + "\n", encoding="utf-8"
    )
    (output / "gate_status.json").write_text(
        json.dumps(gate_status(), indent=2) + "\n", encoding="utf-8"
    )
    (output / "runtime_manifest.json").write_text(
        json.dumps(runtime_manifest, indent=2) + "\n", encoding="utf-8"
    )
    (output / "runtime_audit.json").write_text(
        json.dumps(runtime_result, indent=2) + "\n", encoding="utf-8"
    )
    (output / "observation_summary.json").write_text(
        json.dumps(study_summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(output),
        "runtime_audit_eligible": runtime_result["eligible"],
        "observation_rows": study_summary["rows"],
        "gate_status": str(output / "gate_status.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

