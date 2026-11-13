import numpy as np
import pandas as pd
import pytest

from margin_monitor import (add_displacement, bars_from_klines, bars_from_trades, certify, closed_loop, equilibrium_throttle, rolling_margin,
                            throttle, warnings)


@pytest.mark.parametrize("phi,seed", [(0.06, 1), (0.20, 2)])
def test_certify_recovers_known_margin(phi, seed):
    bars, true_m = closed_loop(days=40, phi=phi, seed=seed)
    c = certify(bars, n_boot=100)
    assert abs(c.margin - true_m) < 0.02
    assert c.ci[0] < true_m < c.ci[1]
    assert c.sign == ("positive" if true_m > 0 else "negative")
    assert c.stability_conditions_verified is False


def test_noise_in_flow_does_not_bias():
    bars, true_m = closed_loop(days=40, flow_sd=4.0, seed=3)
    assert abs(certify(bars, n_boot=50).margin - true_m) < 0.03


def test_rolling_and_warnings_shapes():
    bars, true_m = closed_loop(days=6, seed=4)
    roll = rolling_margin(bars, window="24h", step="1h", n_boot=30)
    assert len(roll) > 100 and {"margin", "lo", "hi", "reversion", "feedback"} <= set(roll.columns)
    assert abs(roll["margin"].median() - true_m) < 0.05
    w = warnings(roll)
    assert {"lost", "buffer", "t2z"} <= set(w.columns) and w["t2z"].dtype == bool


def test_rolling_skips_gappy_windows():
    bars, _ = closed_loop(days=4, seed=5)
    gappy = bars.drop(bars.index[300:700])
    full = rolling_margin(bars, n_boot=0); part = rolling_margin(gappy, n_boot=0)
    assert len(part) < len(full)


def test_throttle_values():
    assert throttle(0.0) == 0.0 and throttle(0.02) == 0.0 and throttle(0.5) == 1.0
    assert throttle(0.06) == pytest.approx(0.5)


def test_bars_from_trades_and_klines():
    t0 = pd.Timestamp("2026-01-01", tz="UTC")
    trades = pd.DataFrame({"time": [t0 + pd.Timedelta(seconds=s) for s in (10, 70, 400, 1300)],
                           "price": [100.0, 101.0, 100.5, 102.0], "size": [1.0, 2.0, 1.0, 1.0], "side": ["B", "S", "B", "A"]})
    b = bars_from_trades(trades)
    assert list(b.columns) == ["p", "f", "n"]
    assert b["f"].iloc[0] == pytest.approx(100.0 - 202.0) and b["n"].iloc[0] == 2
    assert b["n"].sum() == 4 and np.isfinite(b["p"]).all()
    k = pd.DataFrame({"open_time": [1767225600000 + 300000 * i for i in range(3)], "close": [1.0, 1.1, 1.2],
                      "quote_volume": [10.0, 10.0, 10.0], "taker_buy_quote_volume": [6.0, 4.0, 5.0]})
    kb = bars_from_klines(k)
    assert kb["f"].tolist() == [2.0, -2.0, 0.0]


def test_displacement_restarts_after_gap():
    bars, _ = closed_loop(days=2, seed=6)
    b = add_displacement(bars.drop(bars.index[100:200]))
    assert b["seg"].nunique() == 2 and b["x"].iloc[100:112].isna().all()


def test_positive_margin_does_not_claim_stability_of_explosive_negative_root():
    rng = np.random.default_rng(73)
    n = 700
    flow = rng.normal(size=n)
    noise = rng.normal(scale=0.3, size=n)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = -1.01 * x[t - 1] + 0.1 * flow[t] + noise[t]
    bars = pd.DataFrame({"f": flow, "x": x, "r": np.r_[np.nan, np.diff(x)], "seg": 0},
                        index=pd.date_range("2026-01-01", periods=n, freq="5min", tz="UTC"))
    c = certify(bars, lags=1, block="1h", n_boot=100)
    assert c.margin > 2 and c.ci[0] > 0
    assert c.sign == "positive" and not c.stability_conditions_verified


@pytest.mark.parametrize("reversion", [0.0, 0.01, 0.1, 0.5])
@pytest.mark.parametrize("feedback", [0.0, 0.09, 1.0, 100.0])
def test_equilibrium_throttle_solves_admitted_loop_and_preserves_buffer(reversion, feedback):
    alpha = equilibrium_throttle(reversion, feedback)
    margin = reversion - alpha * feedback
    assert alpha == pytest.approx(throttle(margin), abs=1e-12)
    assert margin >= min(0.02, reversion) - 1e-12


def test_previous_margin_response_can_breach_buffer_but_fixed_point_does_not():
    assert 0.1 - 0.09 * throttle(0.1) < 0.02
    alpha = equilibrium_throttle(0.1, 0.09)
    assert alpha == pytest.approx(0.47058823529411764)
    assert 0.1 - 0.09 * alpha > 0.02


def test_throttle_rejects_invalid_bounds_and_abstains_on_missing_margin():
    assert throttle(float("nan")) == 0.0
    assert throttle(float("inf")) == 0.0
    with pytest.raises(ValueError):
        throttle(0.1, m_min=0.1, m_max=0.1)
    with pytest.raises(ValueError):
        equilibrium_throttle(0.1, float("nan"))
    with pytest.raises(ValueError):
        equilibrium_throttle(0.1, -0.1)
