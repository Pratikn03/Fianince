"""Unit tests for publication-grade empirical visualizations."""
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
FIG_PDF = ROOT / "paper" / "figures" / "fig_binance_panel_and_identification.pdf"
FIG_PNG = ROOT / "paper" / "figures" / "fig_binance_panel_and_identification.png"
SCRIPT = ROOT / "scripts" / "generate_empirical_figures.py"


def test_empirical_figure_generator_runs():
    """Verify that generate_empirical_figures.py runs with exit code 0."""
    res = subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT), capture_output=True, text=True)
    assert res.returncode == 0, f"Script failed with output:\n{res.stdout}\n{res.stderr}"


def test_empirical_figure_artifacts_exist():
    """Verify that empirical figure PDF and PNG exist and are substantial in size."""
    assert FIG_PDF.exists(), f"Figure PDF missing: {FIG_PDF}"
    assert FIG_PNG.exists(), f"Figure PNG missing: {FIG_PNG}"
    assert FIG_PDF.stat().st_size > 5000, f"Figure PDF too small: {FIG_PDF.stat().st_size} bytes"
    assert FIG_PNG.stat().st_size > 50000, f"Figure PNG too small: {FIG_PNG.stat().st_size} bytes"
