"""Test that every mathematical theorem in the paper maps to an automated proof or test."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

_ELAN_BIN = Path.home() / ".elan" / "bin"
if _ELAN_BIN.is_dir() and str(_ELAN_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ELAN_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]


def test_every_paper_theorem_has_code_mapping():
    if shutil.which("lake") is None:
        pytest.skip("Lean 4 (lake) not installed in this environment; verified in lean-formal-audit CI job")
    script = ROOT / "scripts" / "verify_theorem_code_bridge.py"
    res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert res.returncode == 0, f"Theorem-code bridge verification failed:\n{res.stdout}\n{res.stderr}"
    assert "paper theorems matched to verification code!" in res.stdout
    assert "SUCCESS: 100% of theorem mappings physically verified on disk!" in res.stdout
    # Wording changed Oct 11 2026: the check (Lean build + strict axiom audit, else exit 1) is unchanged;
    # the old message "fully verified" overstated coverage (only 1/17 statements are fully formalized).
    assert "SUCCESS: named Lean 4 declarations build with 0 sorry and 0 unapproved axioms." in res.stdout

