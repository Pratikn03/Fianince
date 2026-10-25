"""A closed-loop market with a known margin, for tests and examples."""
import numpy as np
import pandas as pd


def closed_loop(days=30, bars_per_day=288, reversion=0.08, kappa=0.5, phi=0.06, memory=0.6, lags=12, span=12,
                flow_sd=1.0, price_sd=1.0, seed=0, start="2026-01-01"):
    """Five-minute bars of a market whose traders respond to the displacement x = p - EMA_span(p) with a geometric
    kernel of total weight `phi` over `lags` bars:
        f_k = sum_m k_m x_{k-m} + w_k,     r_k = kappa f_k - reversion * x_{k-1} + e_k.
    The true margin is reversion - kappa * phi. Returns (bars with columns p and f, true margin)."""
    rng = np.random.default_rng(seed)
    n = days * bars_per_day
    k = (1 - memory) * memory ** np.arange(lags); k = phi * k / k.sum()
    p = np.zeros(n); f = np.zeros(n); x = np.zeros(n); ema = 0.0; alpha = 2 / (span + 1)
    for t in range(1, n):
        past = x[max(0, t - lags):t][::-1]
        f[t] = k[:len(past)] @ past + flow_sd * rng.normal()
        p[t] = p[t - 1] + kappa * f[t] - reversion * x[t - 1] + price_sd * rng.normal()
        ema = ema + alpha * (p[t] - ema)
        x[t] = p[t] - ema
    idx = pd.date_range(start, periods=n, freq="5min", tz="UTC")
    return pd.DataFrame({"p": p + 4.6e4, "f": f}, index=idx), reversion - kappa * phi
