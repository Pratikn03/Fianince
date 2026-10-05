"""Falsifiable checks for the Section-7 estimator and the rebuilt dealer simulation."""
import json
from pathlib import Path

import numpy as np
import pytest

from empirical_pipeline.feedback_var import q_long_memory_robust, var1
from simulations.estimator_validation import q_true, simulate
from simulations import feedback_dealer as fd

ROOT = Path(__file__).resolve().parents[1]


def test_S_identity_and_scale_invariance():
    rng = np.random.default_rng(0)
    x, f = simulate("G1", 6000, rng)
    e1 = var1(x, f)
    e2 = var1(x, 37.0 * f)
    for k in ("Q", "S", "L", "rho"):
        assert e1[k] == pytest.approx(e2[k], rel=1e-8)
    J = np.array([[e1["J11"], e1["J12"]], [e1["J21"], e1["J22"]]])
    assert 1 - e1["S"] == pytest.approx(np.linalg.det(np.eye(2) - J) / (1 - e1["J22"]), rel=1e-10)
    assert e1["S"] - 1 == pytest.approx((1 - e1["J11"]) * (e1["L"] - 1), rel=1e-10)


def test_var1_recovers_single_cohort_feedback_within_30pct():
    rng = np.random.default_rng(1)
    q = [var1(*simulate("G1", 8640, rng))["Q"] for _ in range(12)]
    assert abs(np.mean(q) - q_true("G1")) / q_true("G1") < 0.30


def test_robust_estimator_removes_spurious_feedback_under_order_splitting():
    rng = np.random.default_rng(2)
    q1, q30 = [], []
    for _ in range(12):
        x, f = simulate("G0", 8640, rng)
        q1.append(var1(x, f)["Q"])
        q30.append(q_long_memory_robust(x, f, 30)["Q_L"])
    assert np.mean(q1) > 0.02                     # naive estimator is fooled
    assert abs(np.mean(q30)) < 3 * np.std(q30) / np.sqrt(len(q30)) + 0.004


def test_q_robust_with_L1_equals_var1():
    rng = np.random.default_rng(3)
    x, f = simulate("G1", 5000, rng)
    assert q_long_memory_robust(x, f, 1)["Q_L"] == pytest.approx(var1(x, f)["Q"], rel=1e-8)


@pytest.mark.parametrize("S", [0.6, 0.8])
def test_flow_gain_proposition_matches_simulation(S):
    m = fd.flow_moments(S, n=300_000, seed=4)
    assert m["lrv_bartlett"] == pytest.approx(m["lrv"], rel=0.12)


def test_dealer_halts_increase_with_S_and_lrv_matched_benchmark_tracks_feedback():
    rates_fb, rates_b1, rates_b3 = [], [], []
    for S in (0.5, 0.7, 0.8):
        mom = fd.flow_moments(S, n=100_000)
        rates_fb.append(fd.simulate(S, 10.0, 0.05, "feedback", 150, mom)["rate"])
        rates_b1.append(fd.simulate(S, 10.0, 0.05, "B1", 150, mom)["rate"])
        rates_b3.append(fd.simulate(S, 10.0, 0.05, "B3", 150, mom)["rate"])
    assert rates_fb[0] < rates_fb[1] < rates_fb[2]
    assert rates_b1[2] < rates_fb[2] - 0.3          # variance matching understates
    assert abs(rates_b3[2] - rates_fb[2]) < 0.15    # long-run variance matching does not


def test_generated_tables_match_json():
    gen = ROOT / "paper" / "generated"
    r = json.loads((ROOT / "results" / "provenance" / "empirical_feedback.json").read_text())
    macros = (gen / "empirical_macros.tex").read_text()
    qmax = max(v["summary"]["Q"]["mean"] for v in r["baseline"].values())
    assert f"\\newcommand{{\\EmpQmax}}{{{qmax:.4f}}}" in macros
    for name in ("empirical_feedback_baseline", "empirical_feedback_grid", "empirical_kernel_cm",
                 "estimator_validation", "solvency_feedback"):
        assert (gen / f"{name}.tex").read_text().startswith("% AUTO-GENERATED")


def test_prop_flow_gain_zero_frequency():
    """Proposition 8.1: Zero-frequency gain of feedback flow."""
    test_flow_gain_proposition_matches_simulation(0.6)

