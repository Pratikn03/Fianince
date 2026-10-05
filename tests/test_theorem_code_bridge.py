"""Test that every mathematical theorem in the paper maps to an automated proof or test."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_every_paper_theorem_has_code_mapping():
    script = ROOT / "scripts" / "verify_theorem_code_bridge.py"
    res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert res.returncode == 0, f"Theorem-code bridge verification failed:\n{res.stdout}\n{res.stderr}"
    assert "paper theorems matched to verification code!" in res.stdout
    assert "SUCCESS: 100% of theorem mappings physically verified on disk!" in res.stdout
    assert "SUCCESS: Lean 4 theorems fully verified with 0 sorry!" in res.stdout

