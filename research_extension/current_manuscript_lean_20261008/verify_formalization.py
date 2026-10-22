"""Build current proofs and audit dependencies; this does not certify semantic coverage."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    entries = []
    for path in sorted((HERE / "CurrentProofs").glob("*.lean")):
        source = path.read_text()
        for match in re.finditer(r"^theorem\s+([A-Za-z0-9_]+)", source, re.M):
            entries.append(dict(name="CurrentMM." + match[1], source=str(path.relative_to(HERE)),
                                line=source[:match.start()].count("\n") + 1))
        assert not re.search(r"^\s*(axiom|constant)\s", source, re.M), path
        assert not re.search(r"\b(sorry|admit|native_decide)\b", source), path
    (HERE / "named_declarations.json").write_text(json.dumps(entries, indent=2) + "\n")
    audit = (HERE / "AxiomAudit.lean").read_text()
    start = audit.index("  let names : Array Name := #[")
    end = audit.index("  let mut allConstantCount", start)
    audit = audit[:start] + "  let names : Array Name := #[\n  " + ",\n  ".join(
        "`" + row["name"] for row in entries) + "]\n" + audit[end:]
    (HERE / "AxiomAudit.lean").write_text(audit)
    receipt_path = HERE / "formal_verification_receipt.json"
    receipt = dict(status="RUNNING", timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    elan_bin = str(Path.home() / ".elan" / "bin")
    env = dict(os.environ, COPYFILE_DISABLE="1", PATH=elan_bin + os.pathsep + os.environ.get("PATH", ""))
    for args, stem in [(["lake", "build"], "build"),
                       (["lake", "env", "lean", "AxiomAudit.lean"], "axiom_audit")]:
        run = subprocess.run(args, cwd=HERE, env=env, text=True, capture_output=True, timeout=240)
        (HERE / (stem + ".log")).write_text(run.stdout + run.stderr)
        if run.returncode:
            receipt.update(status="FAILED", command=args, returncode=run.returncode)
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
            raise RuntimeError(f"{args} failed; inspect {stem}.log")
    rows = [json.loads(line) for line in (HERE / "axiom_audit.log").read_text().splitlines()
            if line.startswith('{"')]
    named = [row for row in rows if row["kind"] == "named_theorem"]
    summaries = [row for row in rows if row["kind"] == "audit_summary"]
    assert len(summaries) == 1 and len(named) == len(entries)
    assert {row["name"] for row in named} == {row["name"] for row in entries}
    assert all(set(row["axioms"]) <= ALLOWED for row in named)
    (HERE / "axiom_audit.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    (HERE / "checked_theorem_types.json").write_text(json.dumps(named, indent=2) + "\n")
    body_dir = ROOT / "research_extension/gap_closure_20261006/publication_completion"
    manuscript_paths = [ROOT / "paper/Machine_Markets_JF_Submission.tex"] + [body_dir / (s + ".tex")
        for s in ["resource_frontier", "capital_frontier", "trader_capital_frontier", "natural_excitation_boundary"]]
    manuscript_paths.append(ROOT / "thesis/ch4_paper3.tex")
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in manuscript_paths}
    lean_hashes = {str(p.relative_to(HERE)): sha(p) for p in sorted((HERE / "CurrentProofs").glob("*.lean"))}
    for name in ["CurrentProofs.lean", "AxiomAudit.lean", "lakefile.toml", "lake-manifest.json", "lean-toolchain"]:
        lean_hashes[name] = sha(HERE / name)
    actual_mathlib = subprocess.check_output(["git", "-C", str(HERE / ".lake/packages/mathlib"),
                                              "rev-parse", "HEAD"], text=True).strip()
    assert actual_mathlib == "d13f23b723b8a846827a245b89c10fc7d3f11612"
    receipt.update(status="NAMED_PROOFS_BUILD_AND_STRICT_AXIOM_AUDIT_PASS",
                   lean_version=subprocess.check_output(["lake", "env", "lean", "--version"],
                                                         cwd=HERE, env=env, text=True).strip(),
                   mathlib_commit=actual_mathlib, named_theorems=len(named),
                   project_constants_scanned=summaries[0]["project_constants_scanned"],
                   observed_axioms=sorted(set().union(*(set(row["axioms"]) for row in named))),
                   manuscript_source_sha256=source_hashes, formal_source_sha256=lean_hashes,
                   axiom_log_sha256=sha(HERE / "axiom_audit.log"),
                   manuscript_coverage_sha256=sha(HERE / "MANUSCRIPT_COVERAGE.json"),
                   verification_script_sha256=sha(Path(__file__)),
                   full_manuscript_formalization_complete=False,
                   coverage_boundary="S13/S20 external dependencies; S21 uniform blind-estimator obligation open",
                   limits=["Named declarations are kernel-checked; manuscript equivalence needs the explicit coverage review.",
                           "No market calibration, novelty, causal identification or independent human review follows."])
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["named_theorems"], "named mathematical declarations")


if __name__ == "__main__":
    main()
