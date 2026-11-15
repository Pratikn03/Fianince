"""Simulation check of P1K design 2 (p1k_executor_v2.py). No market data.

Markets with 11 tagged classes. Each class has a memory rate common to all stocks (with a small stock-level
jitter), and each stock's class weights drift from year to year, so its kernel changes over time. Traders update
on a public price statistic, log price minus its 60-day mean (Paper 1's model allows any public statistic), which
is also what the executor observes, scaled by the stock's return volatility. Flows are
observed with noise, and that noise also moves the same day's price (the reverse causality seen in Taiwan).

Cases
  sufficient : Paper 1's model. 'inconsistent' would be a false rejection of sufficiency.
  composition: one class trades on the price five days back, so its share changes dynamics in a way its
               estimated kernel misses. 'supportive' would be a false acceptance.
  null       : no feedback at all (all weights zero). The kernel predicts nothing; 'supportive' would be false.
Usage: python3 validate_p1k_v2.py n_reps [n_stocks] [jitter] -> validate_p1k_v2_results.json
"""
import json, sys, time
import numpy as np
import pandas as pd
import p1k_executor_v2 as ex

N_CLASS = 11
DAYS = pd.bdate_range("2011-09-01", "2025-12-31")
YEAR = DAYS.year.to_numpy()


def simulate_stock(rng, case, eta_class, jitter):
    T = len(DAYS)
    eta = np.clip(eta_class * np.exp(jitter * rng.normal(size=N_CLASS)), 0.02, 0.9); r = 1 - eta
    q0 = rng.normal(0, 1, N_CLASS) / N_CLASS * 6
    q0[0] = -abs(q0[0])
    a, kappa = rng.uniform(0.85, 0.95), 0.04
    years = np.unique(YEAR)
    drift = {y: np.exp(0.6 * rng.normal(size=N_CLASS)) for y in years}       # yearly changes in class activity
    sig_e = rng.uniform(0.5, 1.5)
    x = 0.0; y = np.zeros(N_CLASS); hist = np.zeros(6)
    xs = np.empty(T); flows = np.empty((T, N_CLASS))
    fund = np.cumsum(rng.normal(0, 0.01, T)); lp = np.empty(T); cs = np.zeros(T + 1); sig = 0.012
    eps = rng.normal(0, sig_e, (T, N_CLASS)) * 1e-4
    news = rng.normal(0, 0.01, T)
    qy = {}
    for yv in years:
        q = q0 * drift[yv]
        if case == "null":
            q = q * 0.0
        c1 = 3 * np.abs(q).max() if case == "composition" else 0.0       # delayed trading of class 1
        s = kappa * (np.sum(np.abs(q)) + c1)
        f = min(1.0, (1 - a) * 0.8 / s) if s > 0 else 1.0
        qy[yv] = (q * f, c1 * f)
    for t in range(T):
        q, c1 = qy[YEAR[t]]
        u_prev = q * y * sig
        if case == "composition":
            u_prev = u_prev.copy(); u_prev[1] = c1 * hist[-1] * sig
        x = a * x + kappa * u_prev.sum() + 2.0 * eps[t].sum() + news[t]
        lp[t] = fund[t] + x; cs[t + 1] = cs[t] + lp[t]
        s_t = (lp[t] - (cs[t] - cs[t - 60]) / 60) / sig if t >= 60 else 0.0   # public statistic, as in the executor
        y = r * y + eta * s_t
        hist = np.roll(hist, 1); hist[0] = s_t
        xs[t] = x; flows[t] = q * y * sig + eps[t]
    close = 100 * np.exp(lp)
    mcap = close * 1e8
    return close, mcap, flows * mcap.mean()


def simulate_panel(seed, n_stocks, case, jitter):
    rng = np.random.default_rng(seed)
    eta_class = rng.uniform(0.03, 0.6, N_CLASS)
    frames = []
    for s in range(n_stocks):
        close, mcap, flows = simulate_stock(rng, case, eta_class, jitter)
        f = pd.DataFrame(flows, columns=[f"c{j}" for j in range(N_CLASS)])
        f.insert(0, "ticker", f"S{s:03d}"); f.insert(1, "date", DAYS); f["close"] = close; f["mcap"] = mcap
        frames.append(f)
    return pd.concat(frames, ignore_index=True), eta_class


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ns = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    jit = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
    out = {"n_stocks": ns, "jitter": jit, "cases": {}}
    t0 = time.time()
    for case, base in (("sufficient", 300), ("composition", 400), ("null", 500)):
        res = []
        for k in range(n):
            panel, eta_class = simulate_panel(base + k, ns, case, jit)
            prep = ex.prepare(panel)
            rp = ex.pooled_memories(prep)
            r_true = 1 - eta_class
            r_est = np.array([rp[f"c{j}"] for j in range(N_CLASS)])
            r = ex.evaluate(ex.stock_years(prep, rp), B=299)
            row = {key: r.get(key) for key in ("verdict", "G_A", "G_A_ci95", "G_BA", "G_BA_ci90", "E", "n_hold_stock_years")}
            row["memory_error_max"] = float(np.nanmax(np.abs(r_est - r_true)))
            res.append(row)
            print(case, k, row["verdict"], "G_A %.3g [%.3g, %.3g]" % (r["G_A"], *r["G_A_ci95"]),
                  "G_BA %.3g [%.3g, %.3g] E %.3g" % (r["G_BA"], *r["G_BA_ci90"], r["E"]),
                  "max |r_est - r| %.3f" % row["memory_error_max"], f"[{time.time() - t0:.0f}s]", flush=True)
        v = [x["verdict"] for x in res]
        out["cases"][case] = {"n": n, "verdicts": {x: v.count(x) for x in sorted(set(v))}, "runs": res}
        json.dump(out, open("validate_p1k_v2_results.json", "w"), indent=1)
