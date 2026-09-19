"""Compare scientific outputs of two v0.5 runs; excludes timing/environment JSON.

Usage: python scripts/compare_release.py RELEASE_ROOT FRESH_RUN_ROOT
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def strip_runtime(value):
    if isinstance(value, dict):
        return {k: strip_runtime(v) for k, v in value.items() if k != "runtime_seconds"}
    if isinstance(value, list):
        return [strip_runtime(v) for v in value]
    return value


def compare(reference: Path, fresh: Path) -> dict:
    for root in (reference, fresh):
        if not (root / "results").is_dir() or not (root / "data").is_dir():
            raise ValueError(f"Missing results/data directories: {root}")
    result = {"csv_files": 0, "csv_rows": 0, "npz_files": 0, "arrays": 0,
              "numeric_values": 0, "json_files": 0, "max_numeric_difference": 0.0,
              "mismatches": [], "outside_replication": False}
    for file in sorted((reference / "results").glob("*.csv")):
        other = fresh / "results" / file.name
        result["csv_files"] += 1
        result["csv_rows"] += max(0, len(file.read_bytes().splitlines()) - 1)
        if not other.is_file() or file.read_bytes() != other.read_bytes():
            result["mismatches"].append(str(file.relative_to(reference)))
    for sub in ("data", "replication"):
        for file in sorted((reference / sub).glob("*.npz")):
            other = fresh / sub / file.name
            result["npz_files"] += 1
            if not other.is_file():
                result["mismatches"].append(str(file.relative_to(reference))); continue
            with np.load(file, allow_pickle=False) as left, np.load(other, allow_pickle=False) as right:
                if set(left.files) != set(right.files):
                    result["mismatches"].append(str(file.relative_to(reference)) + ":keys"); continue
                for key in left.files:
                    x, y = left[key], right[key]
                    result["arrays"] += 1
                    numeric = np.issubdtype(x.dtype, np.number)
                    equal = np.array_equal(x, y, equal_nan=True) if numeric else np.array_equal(x, y)
                    if not equal:
                        result["mismatches"].append(str(file.relative_to(reference)) + ":" + key)
                    if numeric and x.shape == y.shape:
                        result["numeric_values"] += int(x.size)
                        finite = np.isfinite(x) & np.isfinite(y)
                        if finite.any():
                            error = float(np.max(np.abs(x[finite].astype(float) - y[finite].astype(float))))
                            result["max_numeric_difference"] = max(result["max_numeric_difference"], error)
    # Compare generator JSON only, not release reports that reference a particular run.
    names = ("linear_summary.json", "financial_summary.json", "followup_summary.json",
             "control_summary.json", "audit_controls.json", "measured_tail_checks.json",
             "standalone_verification.json")
    for name in names:
        left, right = reference / "results" / name, fresh / "results" / name
        result["json_files"] += 1
        if not left.is_file() or not right.is_file() or strip_runtime(json.loads(left.read_text())) != strip_runtime(json.loads(right.read_text())):
            result["mismatches"].append("results/" + name)
    if result["csv_files"] == 0 or result["npz_files"] == 0:
        result["mismatches"].append("No scientific outputs found")
    result["passed"] = not result["mismatches"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("fresh", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = compare(args.reference.resolve(), args.fresh.resolve())
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    print(text)
    if not report["passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
