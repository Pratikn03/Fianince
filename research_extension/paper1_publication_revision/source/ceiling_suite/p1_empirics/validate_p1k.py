"""Simulation check of the P1K executor on simulated markets that satisfy the sufficiency theorem exactly.
No market data. Each stock has 11 tagged classes with their own memory and weight; flows are observed with
noise, and that noise also moves the same day's price (the reverse causality seen in Taiwan).

Cases
  sufficient : the model of Paper 1. The verdict should rarely be 'inconsistent' (false rejection of sufficiency).
  composition: a violation. One class trades on the price with a delay of five days instead of the closed-loop
               timing, so that its share changes return dynamics in a way its estimated kernel misses.
Usage: python3 validate_p1k.py n_reps [n_stocks] -> validate_p1k_results.json
"""
import json, sys, time
import numpy as np
import pandas as pd
import p1k_executor as ex

N_CLASS = 11
DAYS = pd.bdate_range("2011-09-01", "2025-12-31")


def simulate_stock(rng, case):
    T = len(DAYS)
    eta = rng.uniform(0.03, 0.6, N_CLASS); r = 1 - eta
    q = rng.normal(0, 1, N_CLASS) * rng.uniform(0.2, 1.0) / N_CLASS * 6
    q[0] = -abs(q[0])                                   # one clearly contrarian class (like individuals)
    a, kappa = rng.uniform(0.85, 0.95), 0.04
    scale = (1 - a) * 0.8 / (kappa * np.sum(np.abs(q)))  # keep a + kappa * sum|q| < 1
    q = q * min(1.0, scale)
    sig_e = rng.uniform(0.5, 1.5)                       # noise trading per class (common within the stock)
    x = 0.0; y = np.zeros(N_CLASS); hist = np.zeros(6)
    xs = np.empty(T); flows = np.empty((T, N_CLASS))
    eps = rng.normal(0, sig_e, (T, N_CLASS)) * 1e-4
    news = rng.normal(0, 0.01, T)
    for t in range(T):
        u_prev = q * y
        if case == "composition":
            u_prev = u_prev.copy(); u_prev[1] = 3 * abs(q).max() * hist[-1]   # class 1 trades on the price five days back
        x = a * x + kappa * u_prev.sum() + 2.0 * eps[t].sum() + news[t]
        y = r * y + eta * x
        hist = np.roll(hist, 1); hist[0] = x
        xs[t] = x; flows[t] = q * y + eps[t]
    fund = np.cumsum(rng.normal(0, 0.01, T))
    close = 100 * np.exp(fund + xs)
    shares = 1e8
    mcap = close * shares
    return close, mcap, flows * mcap.mean()


def simulate_panel(seed, n_stocks, case):
    rng = np.random.default_rng(seed)
    frames = []
    for s in range(n_stocks):
        close, mcap, flows = simulate_stock(rng, case)
        f = pd.DataFrame(flows, columns=[f"c{j}" for j in range(N_CLASS)])
        f.insert(0, "ticker", f"S{s:03d}"); f.insert(1, "date", DAYS); f["close"] = close; f["mcap"] = mcap
        frames.append(f)
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    ns = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    out = {"n_stocks": ns, "cases": {}}
    t0 = time.time()
    for case, base in (("sufficient", 100), ("composition", 200)):
        res = []
        for k in range(n):
            sy = ex.stock_years(ex.prepare(simulate_panel(base + k, ns, case)))
            r = ex.evaluate(sy, B=299)
            res.append({key: r.get(key) for key in ("verdict", "G_A", "G_A_ci95", "G_BA", "G_BA_ci90", "E", "H1_kruskal_p", "n_hold_stock_years")})
            print(case, k, res[-1]["verdict"], "G_A %.3g [%.3g, %.3g]" % (r["G_A"], *r["G_A_ci95"]),
                  "G_BA %.3g [%.3g, %.3g] E %.3g" % (r["G_BA"], *r["G_BA_ci90"], r["E"]), f"[{time.time() - t0:.0f}s]", flush=True)
        v = [x["verdict"] for x in res]
        out["cases"][case] = {"n": n, "verdicts": {x: v.count(x) for x in sorted(set(v))}, "runs": res}
    json.dump(out, open("validate_p1k_results.json", "w"), indent=1)
