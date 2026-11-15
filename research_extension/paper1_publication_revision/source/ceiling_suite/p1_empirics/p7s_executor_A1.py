"""P7S executor, amendment A1 (P7S_amendment_A1.md). Supersedes p7s_executor.py, which did not implement the
registered inference or the registered proximity variable.

Pipeline, per symbol, on a complete 5-minute grid:
  r_t      = ln(P_t / P_{t-1})                          5-minute log return
  Pi_t     = V_t / max_{t-30d < s <= t} V_s             V = open-interest value; needs 30 full days of history
  response = sign(r_t) * ln(P_{t+12} / P_t) / sigma60   60-minute continuation, in units of the symbol's
                                                        development-period sd of 60-minute returns
  calm     : q50 <= |r_t|/sigma <= q80, and no stress   thresholds from the development period, per symbol
             bar in the previous 60 minutes
  stress   : |r_t|/sigma >= q99
  high/low : Pi_t >= pi_hi / Pi_t <= pi_lo              development terciles of Pi, per symbol
For each symbol: beta_calm = mean(response | calm, high) - mean(response | calm, low); beta_stress likewise.
Statistics: mean over symbols of beta_calm, of beta_stress, and DiD = their difference.
Inference:
  intervals : stationary block bootstrap over dates (mean block 5 days), the same resampled dates for every symbol;
  H1        : two one-sided tests at 5% (the 90% bootstrap interval of mean beta_calm inside (-E, E));
  H2        : a time-shift randomization test. The high/low state series of every symbol is shifted circularly by
              the same k days against the returns, for k = step, 2*step, ..., n_days - step, and the DiD is
              recomputed. n_days must be a multiple of step, so the shifts and the unshifted series form a cyclic
              group and the test is exact when the state series is independent of the return series and both are
              stationary. p = (1 + #{|DiD_k| >= |DiD|}) / (n_days / step). The smallest possible p is step / n_days.
              The percentile bootstrap for the DiD rejected a true linear null in 8 to 9% of simulated data sets
              (validate_p7s_A1); the shift test replaces it for H2. The bootstrap p-value is kept as a descriptive
              output.
Decision (spec section 4): verdict supportive / inconsistent / inconclusive.

Nothing in this file downloads data. Thresholds are fitted on development data only and passed in.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261108
B_DEFAULT = 9999
MEAN_BLOCK_DAYS = 5.0
E_MARGIN = 0.10            # sd units of the 60-minute return; fixed a priori (amendment A1, section 3)
H_BARS = 12                # 60 minutes
BARS_PER_DAY = 288
TRAIL_BARS = 30 * BARS_PER_DAY
CALM_GAP_BARS = 12         # a calm bar has no stress bar in the previous 60 minutes
SHIFT_STEP_DAYS = 5        # spacing of the circular shifts in the randomization test; must divide n_days
MIN_EVENTS = 20            # a symbol enters only with >= 20 events in each of the four cells
CELLS = ("calm_high", "calm_low", "stress_high", "stress_low")


def log_returns(close: np.ndarray) -> np.ndarray:
    r = np.full(len(close), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        r[1:] = np.log(close[1:] / close[:-1])
    return r


def forward_return(close: np.ndarray, h: int = H_BARS) -> np.ndarray:
    f = np.full(len(close), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        f[:-h] = np.log(close[h:] / close[:-h])
    return f


def proximity(oi_value: np.ndarray, trail: int = TRAIL_BARS) -> np.ndarray:
    """Pi_t = V_t / max over the trailing `trail` bars (including t). NaN until `trail` bars of history exist, and
    NaN if fewer than 95% of the bars in the window are observed."""
    s = pd.Series(oi_value, dtype="float64")
    mx = s.rolling(trail, min_periods=int(0.95 * trail)).max().to_numpy()
    pi = oi_value / mx
    pi[: trail - 1] = np.nan
    return pi


def trailing_rv(r: np.ndarray, window: int = BARS_PER_DAY) -> np.ndarray:
    """Realized volatility of 5-minute returns over the previous `window` bars (excluding t)."""
    s = pd.Series(r ** 2, dtype="float64").rolling(window, min_periods=int(0.9 * window)).mean().shift(1)
    return np.sqrt(s.to_numpy())


def fit_thresholds(close: np.ndarray, state_var: np.ndarray, dev_mask: np.ndarray, rv_normalize: bool = False) -> dict:
    """Thresholds for one symbol from development bars only. `state_var` is Pi (or the variant's state variable)."""
    r = log_returns(close); f = forward_return(close)
    sigma = float(np.nanstd(r[dev_mask]))
    sigma60 = float(np.nanstd(f[dev_mask]))
    z = np.abs(r) / (trailing_rv(r) if rv_normalize else sigma)
    zd = z[dev_mask & np.isfinite(z)]
    sd = state_var[dev_mask & np.isfinite(state_var)]
    q50, q80, q99 = (float(x) for x in np.percentile(zd, [50, 80, 99]))
    lo, hi = (float(x) for x in np.percentile(sd, [100 / 3, 200 / 3]))
    return {"sigma": sigma, "sigma60": sigma60, "q50": q50, "q80": q80, "q99": q99, "state_lo": lo, "state_hi": hi,
            "n_dev_bars": int(len(zd)), "rv_normalize": bool(rv_normalize)}


def symbol_cells(close: np.ndarray, state_var: np.ndarray, day_id: np.ndarray, eval_mask: np.ndarray, thr: dict,
                 n_days: int) -> tuple[np.ndarray, np.ndarray]:
    """Per-day sums and counts of the response in the four cells, for one symbol. Returns (S, N), each (n_days, 4).
    `day_id` maps each bar to 0..n_days-1 on evaluation bars; an event belongs to the day of its initiating bar."""
    r = log_returns(close); f = forward_return(close)
    z = np.abs(r) / (trailing_rv(r) if thr["rv_normalize"] else thr["sigma"])
    resp = np.sign(r) * f / thr["sigma60"]
    ok = eval_mask & np.isfinite(z) & np.isfinite(resp) & np.isfinite(state_var) & (r != 0)
    is_stress = np.where(np.isfinite(z), z >= thr["q99"], False)
    recent = pd.Series(is_stress.astype(float)).rolling(CALM_GAP_BARS, min_periods=1).max().shift(1).fillna(0.0).to_numpy() > 0
    calm = ok & (z >= thr["q50"]) & (z <= thr["q80"]) & ~recent
    stress = ok & is_stress
    high = state_var >= thr["state_hi"]
    low = state_var <= thr["state_lo"]
    S = np.zeros((n_days, 4)); N = np.zeros((n_days, 4))
    for k, m in enumerate((calm & high, calm & low, stress & high, stress & low)):
        np.add.at(S[:, k], day_id[m], resp[m]); np.add.at(N[:, k], day_id[m], 1.0)
    return S, N


def symbol_bars(close: np.ndarray, state_var: np.ndarray, eval_mask: np.ndarray, thr: dict) -> dict:
    """Bar-level arrays on evaluation bars, in time order, for the time-shift test: response, move type
    (1 calm, 2 stress, 0 neither) and state (+1 high, -1 low, 0 neither or missing)."""
    r = log_returns(close); f = forward_return(close)
    z = np.abs(r) / (trailing_rv(r) if thr["rv_normalize"] else thr["sigma"])
    resp = np.sign(r) * f / thr["sigma60"]
    ok = np.isfinite(z) & np.isfinite(resp) & (r != 0)
    is_stress = np.where(np.isfinite(z), z >= thr["q99"], False)
    recent = pd.Series(is_stress.astype(float)).rolling(CALM_GAP_BARS, min_periods=1).max().shift(1).fillna(0.0).to_numpy() > 0
    move = np.zeros(len(close), dtype=np.int8)
    move[ok & (z >= thr["q50"]) & (z <= thr["q80"]) & ~recent] = 1
    move[ok & is_stress] = 2
    state = np.zeros(len(close), dtype=np.int8)
    state[np.isfinite(state_var) & (state_var >= thr["state_hi"])] = 1
    state[np.isfinite(state_var) & (state_var <= thr["state_lo"])] = -1
    return {"resp": np.where(ok, resp, 0.0)[eval_mask], "move": move[eval_mask], "state": state[eval_mask]}


def _did_bars(bars: list[dict], shift_bars: int) -> tuple[float, float]:
    """Mean over symbols of beta_calm and the DiD, with every state series rolled forward by `shift_bars` bars."""
    bc, bs = [], []
    for b in bars:
        st = np.roll(b["state"], shift_bars) if shift_bars else b["state"]
        m = []
        for mv in (1, 2):
            for sg in (1, -1):
                sel = (b["move"] == mv) & (st == sg)
                m.append(b["resp"][sel].mean() if sel.any() else np.nan)
        bc.append(m[0] - m[1]); bs.append(m[2] - m[3])
    bc, bs = np.array(bc), np.array(bs)
    return float(np.nanmean(bc)), float(np.nanmean(bs) - np.nanmean(bc))


def shift_test(bars: list[dict], n_days: int, step_days: int = SHIFT_STEP_DAYS) -> dict:
    """Time-shift randomization p-value for the DiD. `bars` holds only the symbols used by `evaluate`.
    The shifts step, 2*step, ..., n_days - step and the unshifted series form a cyclic group."""
    if n_days % step_days != 0:
        raise ValueError(f"n_days={n_days} must be a multiple of step_days={step_days}")
    _, did = _did_bars(bars, 0)
    shifts = list(range(step_days, n_days, step_days))
    null_all = np.array([_did_bars(bars, k * BARS_PER_DAY)[1] for k in shifts])
    null = null_all[np.isfinite(null_all)]
    p = float((1 + np.sum(np.abs(null) >= abs(did))) / (1 + len(null)))
    return {"did": did, "p_shift": p, "n_shifts": int(len(null)), "step_days": int(step_days), "null_sd": float(np.std(null)),
            "null_quantiles_2.5_50_97.5": [float(x) for x in np.percentile(null, [2.5, 50, 97.5])],
            "shift_days": [int(k) for k in shifts],
            "did_by_shift": [float(x) if np.isfinite(x) else None for x in null_all]}


def stationary_weights(n_days: int, B: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    """B x n_days matrix of day multiplicities from the stationary block bootstrap (circular)."""
    p = 1.0 / mean_block
    W = np.zeros((B, n_days))
    for b in range(B):
        new = rng.random(n_days) < p; new[0] = True
        starts = rng.integers(n_days, size=n_days)
        idx = np.empty(n_days, dtype=np.int64); cur = 0
        for i in range(n_days):
            cur = starts[i] if new[i] else (cur + 1) % n_days
            idx[i] = cur
        W[b] = np.bincount(idx, minlength=n_days)
    return W


def _betas(S: np.ndarray, N: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """S, N: (..., n_symbols, 4) aggregated over days. Returns beta_calm, beta_stress per symbol (NaN if a cell is empty)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        m = np.where(N > 0, S / N, np.nan)
    return m[..., 0] - m[..., 1], m[..., 2] - m[..., 3]


def evaluate(S: np.ndarray, N: np.ndarray, symbols: list[str], bars: list[dict] | None = None, B: int = B_DEFAULT,
             seed: int = SEED, mean_block: float = MEAN_BLOCK_DAYS, e_margin: float = E_MARGIN,
             min_events: int = MIN_EVENTS, shift_step_days: int = SHIFT_STEP_DAYS) -> dict:
    """S, N: (n_symbols, n_days, 4); bars: per-symbol output of `symbol_bars` (needed for H2 and the verdict)."""
    n_sym, n_days, _ = S.shape
    tot = N.sum(1)
    keep = (tot >= min_events).all(1)
    Sk, Nk = S[keep], N[keep]
    bc, bs = _betas(Sk.sum(1), Nk.sum(1))
    mean_calm, mean_stress = float(np.mean(bc)), float(np.mean(bs)); did = mean_stress - mean_calm
    rng = np.random.default_rng(seed)
    boot_calm = np.empty(B); boot_did = np.empty(B)
    chunk = 500
    for a in range(0, B, chunk):
        W = stationary_weights(n_days, min(chunk, B - a), mean_block, rng)
        Sb = np.einsum("bd,sdc->bsc", W, Sk); Nb = np.einsum("bd,sdc->bsc", W, Nk)
        c, s = _betas(Sb, Nb)
        boot_calm[a:a + len(W)] = np.nanmean(c, axis=1)
        boot_did[a:a + len(W)] = np.nanmean(s, axis=1) - np.nanmean(c, axis=1)
    finite = np.isfinite(boot_calm) & np.isfinite(boot_did)     # a draw with an empty cell for every symbol is dropped
    n_dropped = int((~finite).sum())
    boot_calm, boot_did = boot_calm[finite], boot_did[finite]
    ci90_calm = [float(x) for x in np.percentile(boot_calm, [5, 95])]
    ci95_calm = [float(x) for x in np.percentile(boot_calm, [2.5, 97.5])]
    ci95_did = [float(x) for x in np.percentile(boot_did, [2.5, 97.5])]
    h1 = (ci90_calm[0] > -e_margin) and (ci90_calm[1] < e_margin)
    p_boot = float(min(1.0, 2.0 * min(np.mean(boot_did <= 0), np.mean(boot_did >= 0))))
    st = shift_test([b for b, k in zip(bars, keep) if k], n_days, step_days=shift_step_days) if bars is not None else None
    p_h2 = st["p_shift"] if st is not None else float("nan")
    h2 = bool(st is not None and p_h2 < 0.05)
    if h1 and h2:
        verdict = "supportive"
    elif abs(mean_calm) >= e_margin:
        verdict = "inconsistent"
    else:
        verdict = "inconclusive"
    return {"spec": "P7S", "amendment": "A1", "n_symbols_total": int(n_sym), "n_symbols_used": int(keep.sum()),
            "symbols_excluded": [s for s, k in zip(symbols, keep) if not k], "n_days": int(n_days),
            "events_per_cell_total": {c: int(v) for c, v in zip(CELLS, Nk.sum((0, 1)))},
            "beta_calm_mean": mean_calm, "beta_calm_ci90": ci90_calm, "beta_calm_ci95": ci95_calm,
            "beta_stress_mean": mean_stress, "did": did, "did_ci95": ci95_did,
            "se_beta_calm": float(np.std(boot_calm)), "se_did": float(np.std(boot_did)),
            "share_symbols_beta_stress_positive": float(np.mean(bs > 0)),
            "h1_calm_silence": bool(h1), "p_h2_stress_reveals": p_h2, "h2_stress_reveals": bool(h2),
            "shift_test": st, "p_did_percentile_bootstrap_descriptive": p_boot,
            "verdict": verdict, "E_margin": e_margin, "B": int(B), "bootstrap_draws_dropped": n_dropped,
            "mean_block_days": mean_block, "seed": int(seed),
            "min_events": int(min_events),
            "per_symbol": {s: {"beta_calm": float(a), "beta_stress": float(b)} for s, a, b in
                           zip([s for s, k in zip(symbols, keep) if k], bc, bs)}}


def blinded_precision(S: np.ndarray, N: np.ndarray, symbols: list[str], **kw) -> dict:
    """Design-stage output on development data: standard errors and event counts only. No point estimate, interval
    or verdict is returned."""
    r = evaluate(S, N, symbols, bars=None, **kw)
    return {k: r[k] for k in ("n_symbols_used", "symbols_excluded", "n_days", "events_per_cell_total", "se_beta_calm",
                              "se_did", "E_margin", "B", "mean_block_days")}
