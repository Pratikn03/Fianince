"""Checks p1ks_dev on simulated stocks with known foreign feedback (no KRX data)."""
import numpy as np
import pandas as pd

import p1ks_dev as P


def fake_stock(seed, r=0.4, w=0.002, kappa=0.3, n=1400, start='2014-09-01'):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=n)
    dates = dates[dates < P.CUTOFF]
    n = len(dates)
    x = np.zeros(n); u = np.zeros(n)
    for t in range(1, n):
        u[t] = r * u[t - 1] + w * x[t - 1] + 0.004 * rng.standard_normal()
        x[t] = 0.95 * x[t - 1] + kappa * u[t - 1] + 0.05 * rng.standard_normal()
    mcap = np.full(n, 1e12)
    close = np.exp(np.cumsum(0.01 * rng.standard_normal(n)) + 0 * x)
    df = pd.DataFrame({'close': close, 'mcap': mcap, 'fnet': u * mcap}, index=dates)
    return df, x


def test_cutoff_enforced():
    df, _ = fake_stock(1)
    bad = df.copy()
    bad.loc[pd.Timestamp('2020-01-02')] = bad.iloc[-1]
    try:
        P.prepare(bad)
    except AssertionError:
        return
    raise AssertionError('cutoff not enforced')


def test_rule_recovery_on_known_x():
    # Feed the estimator a stock whose x is the simulated x, by building close from it.
    rng = np.random.default_rng(3)
    dates = pd.bdate_range('2014-09-01', '2019-12-30')
    n = len(dates)
    x = np.zeros(n); u = np.zeros(n)
    r, w = 0.4, 0.002
    for t in range(1, n):
        u[t] = r * u[t - 1] + w * x[t - 1] + 0.004 * rng.standard_normal()
        x[t] = 0.9 * x[t - 1] + rng.standard_normal()
    d = pd.DataFrame({'x': x, 'u': u}, index=dates)
    st = P.window_stats(d[d.index >= P.START])
    assert abs(st['r'] - r) < 0.08, st
    assert abs(st['w'] - w) < 0.0006, st
    assert 0.8 < st['S'] < 1.0, st


def test_summary_shapes():
    res = {}; groups = {}
    for i in range(12):
        df, _ = fake_stock(100 + i)
        res[f't{i}'] = P.stock_stats(df)
        groups[f't{i}'] = 'index' if i % 2 else 'other'
    s = P.summarize(res, groups)
    for g in ('index', 'other', 'all'):
        assert s[g]['n_full'] == 6 if g != 'all' else s[g]['n_full'] == 12
    assert 'corr_dS_dc' in s['all']


if __name__ == '__main__':
    test_cutoff_enforced(); test_rule_recovery_on_known_x(); test_summary_shapes()
    print('p1ks_dev tests passed')
