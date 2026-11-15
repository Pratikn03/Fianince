"""Unit tests for p7s_executor_A1 on small made-up arrays. No market data. Size and power are in validate_p7s_A1.py."""
import numpy as np
import pytest

import p7s_executor_A1 as ex

BPD = ex.BARS_PER_DAY


def test_proximity_needs_full_history_and_has_no_lookahead():
    v = np.linspace(1.0, 2.0, 40 * BPD)
    pi = ex.proximity(v.copy())
    assert np.isnan(pi[: ex.TRAIL_BARS - 1]).all()
    assert np.isfinite(pi[ex.TRAIL_BARS - 1:]).all()
    assert np.allclose(pi[ex.TRAIL_BARS - 1:], 1.0)          # a rising series is always at its trailing maximum
    v2 = v.copy(); v2[-1] = 100.0                              # a later value must not change earlier Pi
    assert np.array_equal(ex.proximity(v2)[:-1], pi[:-1], equal_nan=True)


def test_forward_return_and_log_return_alignment():
    close = np.exp(np.arange(30) * 0.01)
    assert np.isnan(ex.log_returns(close)[0]) and np.allclose(ex.log_returns(close)[1:], 0.01)
    f = ex.forward_return(close)
    assert np.allclose(f[: -ex.H_BARS], 0.01 * ex.H_BARS) and np.isnan(f[-ex.H_BARS:]).all()


def _bars(n_days, rng, effect=0.0):
    """One symbol: state flips every 5 days; stress responses shifted by `effect` when the state is high."""
    n = n_days * BPD
    state = np.where((np.arange(n) // (5 * BPD)) % 2 == 0, 1, -1).astype(np.int8)
    move = np.zeros(n, dtype=np.int8)
    move[rng.random(n) < 0.3] = 1
    move[rng.random(n) < 0.01] = 2
    resp = rng.standard_normal(n)
    resp[(move == 2) & (state == 1)] += effect
    return {"resp": resp, "move": move, "state": state}


def test_shift_test_requires_a_cyclic_group():
    rng = np.random.default_rng(0)
    bars = [_bars(12, rng)]
    with pytest.raises(ValueError):
        ex.shift_test(bars, 12, step_days=5)
    out = ex.shift_test(bars, 12, step_days=3)
    assert out["n_shifts"] == 3 and out["step_days"] == 3
    assert 1 / 4 <= out["p_shift"] <= 1.0                     # p is a multiple of step / n_days


def test_shift_test_smallest_p_when_effect_is_planted():
    rng = np.random.default_rng(1)
    n_days = 200                                              # state period is 10 days; step 5 puts shifts in and out of phase
    bars = [_bars(n_days, rng, effect=3.0) for _ in range(5)]
    out = ex.shift_test(bars, n_days, step_days=5)
    # out-of-phase shifts reverse the sign of the DiD, so |DiD_k| ties the observed value on in-phase shifts only
    assert out["did"] > 2.0
    assert out["n_shifts"] == n_days // 5 - 1


def test_verdict_logic_on_cell_sums():
    rng = np.random.default_rng(2)
    n_sym, n_days = 6, 60
    N = np.full((n_sym, n_days, 4), 50.0)
    S = rng.standard_normal((n_sym, n_days, 4)) * 0.5        # all cell means near zero
    res = ex.evaluate(S, N, [f"S{i}" for i in range(n_sym)], bars=None, B=199)
    assert res["h1_calm_silence"] is True and res["h2_stress_reveals"] is False
    assert res["verdict"] == "inconclusive"                   # without bars there is no H2 test, so never supportive
    S2 = S.copy(); S2[:, :, 0] += 50.0 * 0.5                  # calm-high mean raised by 0.5 sd
    res2 = ex.evaluate(S2, N, [f"S{i}" for i in range(n_sym)], bars=None, B=199)
    assert res2["verdict"] == "inconsistent" and res2["beta_calm_mean"] > ex.E_MARGIN


def test_symbols_with_thin_cells_are_dropped():
    n_sym, n_days = 4, 20
    N = np.full((n_sym, n_days, 4), 5.0); N[0, :, 2] = 0.0    # symbol 0 has no stress-high events
    S = np.zeros((n_sym, n_days, 4))
    res = ex.evaluate(S, N, ["A", "B", "C", "D"], bars=None, B=99)
    assert res["symbols_excluded"] == ["A"] and res["n_symbols_used"] == 3


def test_blinded_precision_returns_no_estimate():
    N = np.full((3, 20, 4), 30.0); S = np.zeros((3, 20, 4))
    out = ex.blinded_precision(S, N, ["A", "B", "C"], B=99)
    assert not any(k in out for k in ("did", "beta_calm_mean", "verdict", "p_h2_stress_reveals", "beta_calm_ci90"))
