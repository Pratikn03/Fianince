"""P1M: the identification barrier measured in a real market (protocol P1M_measurement_protocol.md).

Taiwan development period 2013-01-02 to 2016-12-30 only. Input: the `prep` dictionary of p1t_executor.prepare (universe,
market-reference basis x, class flows u scaled by development-period average volume, usable-origin mask).

Layers
------
1. Estimation: per-class feedback rules u_{c,t} = r_c u_{c,t-1} + w_c x_{t-d} (stock fixed effects, pooled OLS) and the
   price equation x_t = sum_j a_j x_{t-j} + kappa U_{t-1} (U = sum of the class flows), with a stationary date-block
   bootstrap that resamples the same dates for every equation.
2. The price-only experiment: A(z) = 1 - sum_j a_j z^j - kappa z^(1+d) sum_c w_c / (1 - r_c z). With the market's
   impact function and the non-feedback order flow held at their estimates, the spectral density of x is g / |A|^2 for
   a fixed g, so the Whittle divergence rate between two compositions depends on A alone.
3. The three outcomes: Q1 years to separate the classes; Q2 range of the foreign-halt effect, and Q3 range of the
   uniform-cut effect, over compositions the whole development record cannot tell apart.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

SEED = 20261121
B = 999
MEAN_BLOCK = 20
P_LAGS = 5
DELAY = 1
J0 = 0.02            # no test of any size has power above size + sqrt(J0/2) = size + 0.10 (Pinsker)
POWER, SIZE = 0.80, 0.05
M_GRID = 8192
R_MAX = 0.99
N_RANDOM_STARTS = 40
CLASSES = ("Foreign", "Trust", "Dealers")


# ----------------------------------------------------------------------------------------------------------------
# 1. Estimation
# ----------------------------------------------------------------------------------------------------------------

def lag(a, k):
    out = np.full(a.shape, np.nan)
    if k == 0:
        return a.copy()
    out[:, k:] = a[:, :-k]
    return out


def fe_moments(y, Xs, ok, min_rows=50):
    """Within-stock demeaned pooled regression of y on the columns Xs over rows ok. Returns per-date moment sums so
    that a date bootstrap only re-sums them."""
    X = np.stack(Xs, -1)
    ok = ok & np.isfinite(y) & np.isfinite(X).all(-1)
    cnt = ok.sum(1)
    ok &= (cnt >= min_rows)[:, None]
    cnt = ok.sum(1)
    c = np.maximum(cnt, 1)
    ym = np.where(ok, y, 0).sum(1) / c
    Xm = np.where(ok[..., None], X, 0).sum(1) / c[:, None]
    yd = np.where(ok, y - ym[:, None], 0.0)
    Xd = np.where(ok[..., None], X - Xm[:, None, :], 0.0)
    return {"M": np.einsum("itk,itl->tkl", Xd, Xd), "m": np.einsum("itk,it->tk", Xd, yd), "yy": (yd ** 2).sum(0),
            "n": ok.sum(0), "n_stocks": int((cnt > 0).sum()), "ok": ok, "yd": yd, "Xd": Xd}


def ols_from(mom, idx=None):
    M = mom["M"].sum(0) if idx is None else mom["M"][idx].sum(0)
    m = mom["m"].sum(0) if idx is None else mom["m"][idx].sum(0)
    yy = mom["yy"].sum() if idx is None else mom["yy"][idx].sum()
    n = mom["n"].sum() if idx is None else mom["n"][idx].sum()
    b = np.linalg.solve(M, m)
    ssr = yy - 2 * b @ m + b @ M @ b
    dof = max(n - len(b) - mom["n_stocks"], 1)
    return b, float(ssr / dof), float(1 - ssr / yy) if yy > 0 else float("nan")


def stationary_indices(n, mean_block, rng):
    restart = rng.random(n) < 1.0 / mean_block
    restart[0] = True
    starts = rng.integers(n, size=n)
    pos = np.arange(n)
    last = np.maximum.accumulate(np.where(restart, pos, 0))
    return (starts[last] + (pos - last)) % n


def class_flows(prep, dealer="DealerTotal"):
    u = prep["u"]
    return {"Foreign": u["Foreign"], "Trust": u["Trust"], "Dealers": u[dealer]}


def universe_mask(prep, T):
    m = np.zeros((prep["x"].shape[0], T), bool)
    m[prep["U"]] = True
    return m


def build_equations(prep, mask, delay=DELAY, p=P_LAGS, dealer="DealerTotal"):
    """mask: dates (bool, length T) to use. Returns the moment objects for the three rule equations, the price
    equation, and the class-specific-impact diagnostic."""
    x = prep["x"]
    N, T = x.shape
    base = prep["usable"] & universe_mask(prep, T) & mask[None, :]
    u = class_flows(prep, dealer)
    eqs = {}
    sig = lag(x, delay)
    for c in CLASSES:
        eqs[c] = fe_moments(u[c], [lag(u[c], 1), sig], base)
    Usum = u["Foreign"] + u["Trust"] + u["Dealers"]
    xl = [lag(x, j) for j in range(1, p + 1)]
    eqs["price"] = fe_moments(x, xl + [lag(Usum, 1)], base)
    eqs["price_by_class"] = fe_moments(x, xl + [lag(u[c], 1) for c in CLASSES], base)
    return eqs


def theta_from(betas, p=P_LAGS, delay=DELAY):
    bp = betas["price"]
    return {"a": np.array(bp[:p]), "kappa": float(bp[p]), "r": np.array([betas[c][0] for c in CLASSES]),
            "w": np.array([betas[c][1] for c in CLASSES]), "delay": delay}


def estimate(eqs, p=P_LAGS, delay=DELAY, B_=B, mean_block=MEAN_BLOCK, seed=SEED):
    """Point estimates and the joint stationary date bootstrap of (theta, H_c, U, S)."""
    point = {}
    stats = {}
    for k in list(CLASSES) + ["price", "price_by_class"]:
        b, s2, r2 = ols_from(eqs[k])
        point[k] = b
        stats[k] = {"coef": b.tolist(), "sigma2": s2, "R2": r2, "rows": int(eqs[k]["n"].sum()),
                    "stocks": eqs[k]["n_stocks"]}
    th = theta_from(point, p, delay)
    T = len(eqs["price"]["n"])
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(B_):
        idx = stationary_indices(T, mean_block, rng)
        try:
            bb = {k: ols_from(eqs[k], idx)[0] for k in list(CLASSES) + ["price"]}
        except np.linalg.LinAlgError:
            continue
        t = theta_from(bb, p, delay)
        H = effects(t)
        draws.append(np.r_[t["r"], t["w"], t["kappa"], t["a"].sum(), H["H"], H["U"], H["S"]])
    draws = np.array(draws)
    names = [f"r_{c}" for c in CLASSES] + [f"w_{c}" for c in CLASSES] + ["kappa", "sum_a"] + \
            [f"H_{c}" for c in CLASSES] + ["U", "S"]
    pt = effects(th)
    ptv = np.r_[th["r"], th["w"], th["kappa"], th["a"].sum(), pt["H"], pt["U"], pt["S"]]
    ci = {n: {"est": float(v), "ci95": [float(np.percentile(draws[:, j], 2.5)), float(np.percentile(draws[:, j], 97.5))],
              "se": float(np.std(draws[:, j]))} for j, (n, v) in enumerate(zip(names, ptv))}
    return th, stats, ci, len(draws)


def effects(th):
    """H_c = kappa w_c / (1 - r_c): class c's contribution to the feedback budget, i.e. the fall in S when class c's
    feedback is halted. U = sum_c H_c: the fall in S when all feedback is cut (a uniform cut by a fraction l lowers S by
    l U). S = sum_j a_j + U."""
    H = th["kappa"] * th["w"] / (1 - th["r"])
    return {"H": H, "U": float(H.sum()), "S": float(th["a"].sum() + H.sum())}


# ----------------------------------------------------------------------------------------------------------------
# 2. The price-only experiment
# ----------------------------------------------------------------------------------------------------------------

_OMEGA = 2 * np.pi * (np.arange(M_GRID) + 0.5) / M_GRID - np.pi
_Z = np.exp(-1j * _OMEGA)


def A_of(th, r=None, w=None, z=_Z):
    r = th["r"] if r is None else np.asarray(r)
    w = th["w"] if w is None else np.asarray(w)
    poly = 1 - sum(a * z ** (j + 1) for j, a in enumerate(th["a"]))
    K = sum(wc / (1 - rc * z) for rc, wc in zip(r, w))
    return poly - th["kappa"] * z ** (1 + th["delay"]) * K


def kl_rate(th, r2, w2, A1=None):
    """Whittle divergence rate per observation, KL(P_theta || P_theta'), theta' = theta with rules (r2, w2):
    (1/4 pi) int [f/f' - 1 - log(f/f')] d omega, with f/f' = |A'|^2 / |A|^2."""
    A1 = A_of(th) if A1 is None else A1
    R = np.abs(A_of(th, r2, w2)) ** 2 / np.abs(A1) ** 2
    return float(0.5 * np.mean(R - 1 - np.log(R)))


def char_poly(th, r=None, w=None):
    """Coefficients (increasing powers) of the polynomial whose roots are the poles of the price process:
    (1 - sum a_j z^j) prod (1 - r_c z) - kappa z^(1+d) sum_c w_c prod_{e != c} (1 - r_e z)."""
    from numpy.polynomial import polynomial as Pl
    r = th["r"] if r is None else np.asarray(r)
    w = th["w"] if w is None else np.asarray(w)
    left = np.r_[1.0, -np.asarray(th["a"])]
    prod = np.array([1.0])
    for rc in r:
        prod = Pl.polymul(prod, [1.0, -rc])
    left = Pl.polymul(left, prod)
    right = np.array([0.0])
    for c, wc in enumerate(w):
        pc = np.array([1.0])
        for e, re_ in enumerate(r):
            if e != c:
                pc = Pl.polymul(pc, [1.0, -re_])
        right = Pl.polyadd(right, wc * pc)
    shift = np.zeros(2 + th["delay"]); shift[-1] = th["kappa"]
    right = Pl.polymul(shift, right)
    return Pl.polysub(left, right)


def stationary(th, r=None, w=None, margin=1e-6):
    roots = np.roots(char_poly(th, r, w)[::-1])
    return bool(len(roots) == 0 or np.min(np.abs(roots)) > 1 + margin), float(np.min(np.abs(roots))) if len(roots) else float("inf")


def _min_over_W(fun, lo=-50.0, hi=50.0):
    from scipy.optimize import minimize_scalar
    r = minimize_scalar(fun, bounds=(lo, hi), method="bounded", options={"xatol": 1e-12})
    return r.x, r.fun


def q1_price(th):
    """Smallest Whittle rate from the estimated population to any single-memory population (aggregate kernel
    W R^m), over R in [-R_MAX, R_MAX] and W."""
    from scipy.optimize import minimize
    A1 = A_of(th)
    Uhat = effects(th)["U"]
    scale = max(abs(th["kappa"]), 1e-12)
    best = (np.inf, None, None)
    for R in np.linspace(-R_MAX, R_MAX, 199):
        Wk, f = _min_over_W(lambda W: kl_rate(th, [R, 0, 0], [W / scale, 0, 0], A1),
                            lo=-10 * (abs(Uhat) + 1e-3), hi=10 * (abs(Uhat) + 1e-3))
        if f < best[0]:
            best = (f, R, Wk / scale)
    f0, R0, W0 = best
    g = lambda v: kl_rate(th, [np.clip(v[0], -R_MAX, R_MAX), 0, 0], [v[1], 0, 0], A1)
    res = minimize(g, [R0, W0], method="Nelder-Mead", options={"xatol": 1e-12, "fatol": 1e-20, "maxiter": 4000})
    if res.fun < f0:
        f0, R0, W0 = res.fun, float(np.clip(res.x[0], -R_MAX, R_MAX)), float(res.x[1])
    return {"rate": float(f0), "R": float(R0), "W": float(W0)}


def pinsker_days(rate, power=POWER, size=SIZE):
    """Observations below which no test of size `size` has power `power`: KL >= 2 (power - size)^2 is necessary."""
    return 2 * (power - size) ** 2 / rate if rate > 0 else float("inf")


def tag_filters(prep, mask, th, dealer="DealerTotal", burn=100):
    """Pooled, within-stock demeaned series used by the tagged-record divergence: s_t = x_{t-d}, and the rows where
    all three rule equations are usable. Returns (S, ok) as stocks x dates arrays."""
    x = prep["x"]
    N, T = x.shape
    s = lag(x, th["delay"])
    u = class_flows(prep, dealer)
    ok = prep["usable"] & universe_mask(prep, T) & mask[None, :] & np.isfinite(s)
    for c in CLASSES:
        ok &= np.isfinite(u[c]) & np.isfinite(lag(u[c], 1))
    sd = np.where(np.isfinite(s), s, np.nan)
    mu = np.nanmean(np.where(ok, sd, np.nan), axis=1)
    sd = sd - mu[:, None]
    # rows need `burn` finite days of s before them, so the filters below have converged
    fin = np.isfinite(sd)
    run = np.zeros((N, T), int)
    for t in range(T):
        run[:, t] = np.where(fin[:, t], (run[:, t - 1] + 1) if t else 1, 0)
    ok &= run > burn
    return np.where(fin, sd, 0.0), ok


def ar_filter(s, R):
    G = np.zeros_like(s)
    for t in range(1, s.shape[1]):
        G[:, t] = R * G[:, t - 1] + s[:, t]
    return G


def q1_tags(th, S, ok, resid_cov):
    """Divergence rate per stock-day of the tagged record (prices and the three class flows) between the estimated
    population and the closest single-memory population (decay R common to all classes, weights W_c free). With the
    price equation the same under both, the rate is (1/2) E[d' Omega^{-1} d], d_c = w_c s_t - W_c q_c(R)_t,
    q_c = (1 - r_c L)/(1 - R L) s."""
    Oi = np.linalg.inv(resid_cov)
    w, r = th["w"], th["r"]
    n = ok.sum()
    s = S[ok]
    S0 = float(np.mean(s * s))

    def at(R):
        G = ar_filter(S, R)
        Gl = lag(G, 1)
        q = [np.where(ok, G - rc * np.nan_to_num(Gl), 0)[ok] for rc in r]
        Q = np.array([[np.mean(q[c] * q[e]) for e in range(3)] for c in range(3)])
        Cq = np.array([np.mean(q[c] * s) for c in range(3)])
        # E[d' Oi d] = sum_ce Oi_ce (w_c w_e S0 - W_c w_e Cq_c - w_c W_e Cq_e + W_c W_e Q_ce)
        Mq = Oi * Q
        bq = (Oi * Cq[:, None]) @ w
        W = np.linalg.solve(Mq, bq)
        val = float(w @ (Oi * S0) @ w - 2 * W @ bq + W @ Mq @ W)
        return 0.5 * val, W

    grid = np.linspace(-R_MAX, R_MAX, 67)
    vals = [at(R)[0] for R in grid]
    k = int(np.argmin(vals))
    lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, len(grid) - 1)]
    from scipy.optimize import minimize_scalar
    res = minimize_scalar(lambda R: at(R)[0], bounds=(lo, hi), method="bounded", options={"xatol": 1e-6})
    R = float(res.x) if res.fun <= vals[k] else float(grid[k])
    rate, W = at(R)
    return {"rate": float(rate), "R": R, "W": W.tolist(), "rows": int(n)}


# ----------------------------------------------------------------------------------------------------------------
# 3. Q2 and Q3: ranges over the compositions the record cannot tell apart
# ----------------------------------------------------------------------------------------------------------------

def _unpack(v):
    return R_MAX * np.tanh(v[:3]), v[3:]


def _pack(r, w):
    return np.r_[np.arctanh(np.clip(np.asarray(r) / R_MAX, -0.999999, 0.999999)), w]


def feasible_set(th, n_rec, hbar):
    A1 = A_of(th)

    def cons(v):
        r, w = _unpack(v)
        H = th["kappa"] * w / (1 - r)
        return np.r_[J0 - n_rec * kl_rate(th, r, w, A1), hbar - H, hbar + H]
    return cons


def ranges(th, n_rec, hbar, seed=SEED, n_random=N_RANDOM_STARTS):
    """Min and max, over rules theta' with n_rec * rate(theta, theta') <= J0 and |H'_c| <= hbar, of the foreign-halt
    effect H'_Foreign and of the uniform-cut effect U' = sum_c H'_c. Starts: the estimate, its five relabelings, and
    `n_random` random rules pulled into the set. Returns the extremes found and the relabeling values (which lie in the
    set for every record length, because the rate is exactly 0 there)."""
    from scipy.optimize import minimize
    cons = feasible_set(th, n_rec, hbar)
    A1 = A_of(th)
    rng = np.random.default_rng(seed)
    v0 = _pack(th["r"], th["w"])
    starts = []
    for perm in itertools.permutations(range(3)):
        starts.append(_pack(th["r"][list(perm)], th["w"][list(perm)]))
    wscale = np.maximum(np.abs(th["w"]), 1e-6)
    for _ in range(n_random):
        r = np.clip(th["r"] + rng.normal(0, 0.3, 3), -0.95, 0.95)
        w = th["w"] + rng.normal(0, 1, 3) * wscale.max()
        v = _pack(r, w)
        base = starts[rng.integers(len(starts[:6]))]
        for _ in range(60):                      # pull toward a relabeling until feasible
            if np.all(cons(v) >= 0):
                break
            v = base + 0.5 * (v - base)
        starts.append(v)
    kap = th["kappa"]

    def HF(v):
        r, w = _unpack(v)
        return kap * w[0] / (1 - r[0])

    def UU(v):
        r, w = _unpack(v)
        return float(np.sum(kap * w / (1 - r)))

    out = {}
    for name, f in (("H_Foreign", HF), ("U", UU)):
        best = {"min": (np.inf, None), "max": (-np.inf, None)}
        for v in starts:
            for sgn, key in ((1, "min"), (-1, "max")):
                try:
                    res = minimize(lambda q: sgn * f(q), v, method="SLSQP",
                                   constraints=[{"type": "ineq", "fun": cons}], options={"maxiter": 500, "ftol": 1e-14})
                    cand = res.x
                except Exception:
                    continue
                c = cons(cand)
                if np.all(c >= -1e-12 * max(1.0, J0)):
                    r, w = _unpack(cand)
                    if stationary(th, r, w)[0]:
                        val = f(cand)
                        if (key == "min" and val < best["min"][0]) or (key == "max" and val > best["max"][0]):
                            best[key] = (val, cand)
        rec = {}
        for key in ("min", "max"):
            val, v = best[key]
            r, w = _unpack(v) if v is not None else (None, None)
            rec[key] = float(val)
            rec[key + "_rules"] = {"r": None if r is None else r.tolist(), "w": None if w is None else w.tolist(),
                                   "rate": None if r is None else kl_rate(th, r, w, A1)}
        out[name] = rec
    H = effects(th)["H"]
    out["relabeling_values_H_Foreign"] = sorted(float(h) for h in H)
    out["n_rec"] = float(n_rec); out["hbar"] = float(hbar); out["J0"] = J0; out["n_starts"] = len(starts)
    return out


def hbar_of(th):
    m = 1 - float(np.sum(th["a"]))
    return (m, False) if m >= 0.01 else (0.01, True)


def measure(prep, mask, dealer="DealerTotal", delay=DELAY, p=P_LAGS, B_=B, n_random=N_RANDOM_STARTS, days_per_year=None,
            label="primary"):
    eqs = build_equations(prep, mask, delay, p, dealer)
    th, stats, ci, nb = estimate(eqs, p, delay, B_)
    st, minroot = stationary(th)
    eff = effects(th)
    dpy = days_per_year if days_per_year else float(mask.sum()) / 4.0
    n_pooled = float(eqs["price"]["n"].sum())
    per_stock = eqs["price"]["ok"].sum(1)
    n_stock = float(np.median(per_stock[per_stock > 0]))
    N_st = eqs["price"]["n_stocks"]
    # Q1
    q1p = q1_price(th)
    S, ok = tag_filters(prep, mask, th, dealer)
    # residual covariance of the three rule equations on common rows
    res = []
    common = ok.copy()
    for c in CLASSES:
        common &= eqs[c]["ok"]
    for c in CLASSES:
        b = np.array(stats[c]["coef"])
        e = eqs[c]["yd"] - eqs[c]["Xd"] @ b
        res.append(e[common])
    Om = np.cov(np.vstack(res))
    q1t = q1_tags(th, S, ok, Om)
    q1 = {"price_rate_per_stock_day": q1p["rate"], "closest_single_memory_price": q1p,
          "tag_rate_per_stock_day": q1t["rate"], "closest_single_memory_tags": q1t,
          "information_ratio_tags_to_prices": (q1t["rate"] / q1p["rate"]) if q1p["rate"] > 0 else float("inf"),
          "pinsker_stock_days_prices": pinsker_days(q1p["rate"]), "pinsker_stock_days_tags": pinsker_days(q1t["rate"]),
          "years_prices_one_stock_at_least": pinsker_days(q1p["rate"]) / dpy,
          "years_prices_whole_panel_at_least": pinsker_days(q1p["rate"]) / (dpy * N_st),
          "years_tags_one_stock_at_least": pinsker_days(q1t["rate"]) / dpy,
          "residual_cov": Om.tolist()}
    hbar, flagged = hbar_of(th)
    q23_pooled = ranges(th, n_pooled, hbar, n_random=n_random)
    q23_stock = ranges(th, n_stock, hbar, n_random=n_random)
    hbar_tight = 2 * float(np.max(np.abs(eff["H"])))
    q23_tight = ranges(th, n_pooled, hbar_tight, n_random=n_random)
    return {"label": label, "dealer_series": dealer, "delay": delay, "p_lags": p, "theta": {
                "a": th["a"].tolist(), "kappa": th["kappa"], "r": th["r"].tolist(), "w": th["w"].tolist()},
            "stationary": st, "min_root_modulus": minroot, "effects": {"H": eff["H"].tolist(), "U": eff["U"], "S": eff["S"]},
            "equations": stats, "bootstrap": {"B_used": nb, "mean_block": MEAN_BLOCK, "seed": SEED, "ci": ci},
            "records": {"pooled_stock_days": n_pooled, "median_stock_days": n_stock, "n_stocks": N_st,
                        "days_per_year": dpy},
            "hbar": hbar, "hbar_floor_used": flagged, "Q1": q1, "Q2Q3_whole_panel": q23_pooled,
            "Q2Q3_one_stock": q23_stock, "hbar_tight": hbar_tight, "Q2Q3_whole_panel_tight_box": q23_tight}
