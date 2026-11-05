import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

_ELAN_BIN = Path.home() / ".elan" / "bin"
if _ELAN_BIN.is_dir() and str(_ELAN_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ELAN_BIN}:{os.environ.get('PATH', '')}"

def test_lean_proofs_build_and_axiom_audit():
    if shutil.which("lake") is None:
        pytest.skip("Lean 4 (lake) not installed in this environment; audited in lean-formal-audit CI job")
    lean_dir = Path(__file__).resolve().parent.parent / "lean_proofs"
    assert lean_dir.exists(), "lean_proofs directory must exist"

    # 1. Run lake build
    build_res = subprocess.run(
        ["lake", "build"],
        cwd=str(lean_dir),
        capture_output=True,
        text=True
    )
    assert build_res.returncode == 0, f"lake build failed:\n{build_res.stderr}"

    # 2. Run AxiomAudit.lean
    audit_res = subprocess.run(
        ["lake", "env", "lean", "AxiomAudit.lean"],
        cwd=str(lean_dir),
        capture_output=True,
        text=True
    )
    assert audit_res.returncode == 0, f"Axiom audit failed:\n{audit_res.stderr}"
    assert "SUCCESS: ALL THEOREMS FULLY VERIFIED WITHOUT SORRY!" in audit_res.stdout


def test_ceiling_suite_manifest_audit():
    root = Path(__file__).resolve().parent.parent
    audit_script = root / "ceiling_suite" / "verify_ceiling_suite_lean_proofs.py"
    res = subprocess.run(
        [sys.executable, str(audit_script)],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"Manifest audit failed:\n{res.stdout}\n{res.stderr}"
    manifest = json.loads((root / "ceiling_suite" / "CEILING_SUITE_LEAN_PROOF_MANIFEST.json").read_text())
    records = manifest["paper1"] + manifest["paper2"]
    assert manifest["total_ceiling_suite_environments"] == len(records)
    assert manifest["total_existing_name_mappings"] == len(records)
    assert manifest["unmapped_labels"] == []
    assert all(r["mathlib_theorem"] != "UNMAPPED" and r["mathlib_file"] for r in records)
    by_label = {r["label"]: r for r in manifest["paper1"]}
    assert "p1_supervisory_gaussian_unsafe_halt" in by_label["prop:robust_gate"]["mathlib_theorem"]
    assert "p1_information_purchase_break_even" in by_label["prop:priced_decision"]["mathlib_theorem"]
    assert by_label["prop:robust_gate"]["core_lean_theorem"] == "NOT_SEPARATELY_FORMALIZED"
    # Name completeness must not silently become a semantic-coverage claim.
    assert manifest["fresh_lean_build_performed"] is False
    assert manifest["revised_labels_requiring_semantic_review"]
    strict = subprocess.run([sys.executable, str(audit_script), "--require-complete"],
                            cwd=root, capture_output=True, text=True)
    assert strict.returncode != 0

