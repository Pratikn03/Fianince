"""Regression tests for the Paper 1 -> Paper 2 bridge proposition (ceiling_suite/bridge/BRIDGE_PROPOSITION.md)."""

from __future__ import annotations

import importlib.util
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("bridge_check", ROOT / "ceiling_suite" / "bridge" / "bridge_check.py")
bc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bc)


def test_a_phi_is_invariant_to_split_but_response_is_not():
    rows = bc.part_a()
    assert len(rows) == 4
    for r in rows:
        assert r["phi_single"] == r["phi_split"] == "2/25"
        assert r["S_single"] == r["S_split"] == "25/13"
        assert r["lags_0_1_equal"]
        assert r["lag2_matches_prediction"]
        assert r["response_diff_lags_0_to_4"][2] != "0"


def test_a_summed_response_formula_matches_long_horizon_sum():
    q, eta = [F(1, 2), F(1, 2)], [F(2, 5), F(3, 5)]
    a, kappa = F(2, 5), F(1)
    h = bc.response(a, kappa, [qi * F(1, 25) for qi in q], eta, 200)
    s = bc.summed_response(a, kappa, [qi * F(1, 25) for qi in q])
    assert abs(float(sum(h)) - float(s)) < 1e-12


def test_b_identification_cost_scales_as_delta_to_the_minus_four():
    b = bc.part_b()
    assert b["loglog_slope_norm_dh"] == pytest.approx(2.0, abs=0.05)
    assert b["implied_N_exponent"] == pytest.approx(-4.0, abs=0.1)
    n = [r["N_necessary_to_separate"] for r in b["rows"]]
    assert all(x > y for x, y in zip(n, n[1:]))  # smaller delta needs more experiments


def test_c_certificate_is_delta_free_and_cohort_test_is_not():
    c = bc.part_c()
    rows = c["rows"]
    assert c["reps"] == 4000 and all(r["trials_per_row"] == 8000 for r in rows)
    for r in rows:
        lo, hi = r["certificate_coverage_ci95"]
        assert lo >= 0.93 and hi >= 0.95  # nominal 0.95; the tail term makes the certificate slightly conservative
        assert lo <= r["certificate_coverage"] <= hi
    excess = [r["certificate_mean_excess"] for r in rows]
    assert max(excess) - min(excess) < 5e-4
    assert max(excess) < 0.004
    assert rows[0]["cohort_test_accuracy_ci95"][1] < 0.60  # delta = 0.02: the Bayes two-point test is near a coin flip
    assert rows[-1]["cohort_test_accuracy_ci95"][0] > 0.99
    for r in rows:
        assert abs(r["cohort_test_accuracy_mc"] - r["cohort_test_accuracy_theory"]) < 0.03
        lo, hi = r["cohort_test_accuracy_ci95"]
        assert lo - 0.005 <= r["cohort_test_accuracy_theory"] <= hi + 0.005


def test_d_window_closed_forms_and_unbounded_family():
    d = bc.part_d()
    assert d["phi_minus_closed_form"] == "2/25"
    assert d["phi_plus_rbar_0.95_closed_form"] == "11/25"
    assert d["S_at_phi_plus_rbar_0.95"] == "25/4"
    assert d["lp_phi_max_rbar_0.95"] == pytest.approx(0.44, abs=1e-9)  # independent LP agrees
    assert d["lp_phi_min_rbar_0.95"] == pytest.approx(0.08, abs=1e-9)
    assert d["critical_delta_for_instability"] == "1/28"
    for r in d["family"]:
        assert r["phi_matches_closed_form"]
        assert r["lags_0_to_2_equal_reference"]
        assert r["stable"]
    assert d["family"][-1]["S"] == "50"  # delta = 1/27: same first three lags, S = 50 against 25/13
    # beyond the critical delta the same data are compatible with an unstable economy
    q, eta = bc.atoms_to_cohorts(bc.two_atom_family(F(1, 29)))
    assert bc.A0 + bc.KAPPA * sum(q) > 1
    assert bc.response(bc.A0, bc.KAPPA, q, eta, 3) == bc.response(bc.A0, bc.KAPPA, [bc.Q0], [bc.ETA0], 3)


def test_d_jensen_and_chord_bounds_hold_for_random_measures():
    rng = np.random.default_rng(3)
    rbar = 0.9
    for _ in range(200):
        r = rng.uniform(0, rbar, 4)
        w = rng.uniform(0, 1, 4)
        k0, k1 = w.sum(), (w * r).sum()
        phi_val = (w / (1 - r)).sum()
        assert phi_val >= k0**2 / (k0 - k1) - 1e-12
        assert phi_val <= k0 + k1 / (1 - rbar) + 1e-12


def test_e_signed_responses_break_the_sufficiency_step():
    e = bc.part_e()
    assert e["spectral_radius_signed"] < 0.98  # stable
    assert e["phi_signed"] == pytest.approx(e["phi_positive_reference"], abs=1e-12)
    assert e["sum_h_signed"] == pytest.approx(e["S_net_formula"], rel=1e-9)  # S is the same
    assert e["min_h_signed"] < 0  # the response changes sign
    assert e["loss_understatement_ratio"] > 1.3  # but the worst-case loss is more than 30% larger
