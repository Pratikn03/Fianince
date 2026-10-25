import numpy as np
import pandas as pd
import pytest

from margin_monitor import (add_displacement, bars_from_klines, bars_from_trades, certify, closed_loop, rolling_margin,
                            throttle, warnings)


@pytest.mark.parametrize("phi,seed", [(0.06, 1), (0.20, 2)])
def test_certify_recovers_known_margin(phi, seed):
    bars, true_m = closed_loop(days=40, phi=phi, seed=seed)
    c = certify(bars, n_boot=100)
    assert abs(c.margin - true_m) < 0.02
    assert c.ci[0] < true_m < c.ci[1]
    assert c.sign == ("safe" if true_m > 0 else "unsafe")


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
