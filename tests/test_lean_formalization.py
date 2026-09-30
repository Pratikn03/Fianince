"""Test Lean 4 formalization of market feedback control theorems."""
import subprocess
from pathlib import Path

def test_lean_proofs_build_and_axiom_audit():
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
