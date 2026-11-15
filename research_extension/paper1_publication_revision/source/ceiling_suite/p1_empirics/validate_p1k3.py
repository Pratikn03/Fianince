"""Simulation check of P1K3 (spec P1K3_spec.md, section 7). No market data.

Panels of N stocks and 11 categories on the KRX calendar span (business days 2014-09-01 to 2025-12-31). Category c
has memory speed eta_c (drawn once per panel, uniform on [0.03, 0.6]); in stock s its speed is
eta_c * exp(tau_true * z_sc), clipped to [0.02, 0.9]. Weights have a category-level sign and size with stock-level
spread, and change from year to year (category activity). Prices carry a market-wide news component. Flow noise also
moves the same day's price (other trading is set so that feedback explains a share R2_c of each category's flow,
log-uniform on [1%, 20%] across categories). Stocks enter and leave the index. Traders follow the public statistic the executor
computes (log price minus its previous 60-day mean, scaled).

Cases (section 7): common, boundary, heterogeneous, null, mixture, weak.
Usage: python3 validate_p1k3.py reps [n_stocks] [cases,comma,separated] -> validate_p1k3_results.json (merged)
"""
import json, os, sys, time
import numpy as np
import pandas as pd
import p1k3_executor as ex

C = 11
DAYS = pd.bdate_range("2014-09-01", "2025-12-31")
YEAR = DAYS.year.to_numpy()
YEARS = np.arange(2015, 2026)
CASES = {"common": dict(tau=0.0), "boundary": dict(tau=0.25), "heterogeneous": dict(tau=0.5),
         "null": dict(tau=0.0, null=True), "mixture": dict(tau=0.0, mixture=True), "weak": dict(tau=0.0, scale=0.5)}
SEEDS = {"common": 1000, "boundary": 2000, "heterogeneous": 3000, "null": 4000, "mixture": 5000, "weak": 6000}


def _loop(S, eta, r, wsub, qy, a, news_rng_seed, eps_sd, lam):
    """One pass of the market. eps_sd: S x C sd of other trading (which also moves prices with impact lam)."""
    T = len(DAYS); kappa = 0.04; sig = 0.012
    nr = np.random.default_rng(news_rng_seed); er = np.random.default_rng(news_rng_seed + 7)
    x = np.zeros(S); y = np.zeros(eta.shape); fund = np.zeros(S)
    lp = np.empty((S, T)); sigflow = np.empty((S, T, C)); flows = np.empty((S, T, C))
    ring = np.zeros((S, 60)); csum = np.zeros(S)
    for t in range(T):
        q = qy[YEAR[t]]
        u_sig = q * (y * wsub).sum(2) * sig                      # feedback component, S x C
        eps = er.normal(size=(S, C)) * eps_sd                    # other trading
        news = 0.007 * nr.normal() + 0.007 * nr.normal(size=S)  # market-wide and own news
        fund = fund + nr.normal(0, 0.01, S)
        x = a * x + kappa * u_sig.sum(1) + lam * eps.sum(1) + news
        lp[:, t] = fund + x
        s_t = (lp[:, t] - csum / 60) / sig if t >= 60 else np.zeros(S)
        k = t % 60
        csum = csum - ring[:, k] + lp[:, t]; ring[:, k] = lp[:, t]
        y = r * y + eta * s_t[:, None, None]
        sigflow[:, t, :] = u_sig; flows[:, t, :] = u_sig + eps
    return lp, sigflow, flows


def simulate_panel(seed, S, tau=0.0, null=False, mixture=False, scale=1.0, r2=(0.01, 0.2)):
    """Two passes with the same news: pass 1 without other trading measures each stock-category's feedback-flow sd;
    pass 2 adds other trading so that feedback explains a share R2_c of the flow (R2_c log-uniform on r2, per
    category), calibrated on the full-strength market; the case then scales the feedback (0 null, 0.5 weak)."""
    rng = np.random.default_rng(seed)
    eta_c = rng.uniform(0.03, 0.6, C)
    if mixture:   # two sub-groups per category, speeds eta_c e^{+-0.7}, stock-specific shares
        eta = np.stack([np.clip(eta_c * np.exp(0.7), 0.02, 0.9) * np.ones((S, C)),
                        np.clip(eta_c * np.exp(-0.7), 0.02, 0.9) * np.ones((S, C))], axis=2)   # S x C x 2
        share = rng.uniform(0, 1, (S, C))
        wsub = np.stack([share, 1 - share], axis=2)
    else:
        eta = np.clip(eta_c[None, :] * np.exp(tau * rng.normal(size=(S, C))), 0.02, 0.9)[:, :, None]
        wsub = np.ones((S, C, 1))
    r = 1 - eta
    qbar = rng.normal(0, 1, C) / C * 6
    q0 = qbar[None, :] * np.exp(0.3 * rng.normal(size=(S, C)))
    drift = {y: np.exp(0.6 * rng.normal(size=(S, C))) for y in np.unique(YEAR)}
    a = rng.uniform(0.85, 0.95, S); kappa = 0.04

    def yearly(mult):
        qy = {}
        for yv in np.unique(YEAR):
            q = q0 * drift[yv]
            s_ = kappa * np.abs(q).sum(1)
            f = np.where(s_ > 0, np.minimum(1.0, (1 - a) * 0.8 / np.where(s_ > 0, s_, 1)), 1.0)
            qy[yv] = q * f[:, None] * mult
        return qy
    R2 = np.exp(rng.uniform(np.log(r2[0]), np.log(r2[1]), C))
    nseed = int(rng.integers(1 << 30))
    _, sig1, _ = _loop(S, eta, r, wsub, yearly(1.0), a, nseed, np.zeros((S, C)), 0.0)
    sd_sig = sig1[:, DAYS >= "2015-01-01", :].std(1)                                  # S x C
    eps_sd = sd_sig * np.sqrt((1 - R2) / R2)[None, :]
    lam = 0.003 / np.sqrt((eps_sd ** 2).sum(1)).mean()                               # other trading moves prices
    mult = 0.0 if null else scale
    lp, sigflow, flows = _loop(S, eta, r, wsub, yearly(mult), a, nseed, eps_sd, lam)
    close = 100 * np.exp(lp); mcap = close * 1e8
    flows = flows * mcap.mean(1)[:, None, None]
    start = np.where(rng.uniform(size=S) < 0.3, rng.integers(2015, 2020, S), 2015)
    end = np.where(rng.uniform(size=S) < 0.3, rng.integers(2021, 2026, S), 2025)
    frames = []
    for s in range(S):
        f = pd.DataFrame(flows[s], columns=[f"c{j}" for j in range(C)])
        f.insert(0, "ticker", f"S{s:03d}"); f.insert(1, "date", DAYS)
        f["close"] = close[s]; f["mcap"] = mcap[s]; f["member"] = (YEAR >= start[s]) & (YEAR <= end[s])
        frames.append(f)
    true_spread = float(np.std(np.log(eta[:, :, 0]), axis=0).mean()) if not mixture else None
    return pd.concat(frames, ignore_index=True), true_spread


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 250
    which = sys.argv[3].split(",") if len(sys.argv) > 3 else list(CASES)
    path = "validate_p1k3_results.json"
    out = json.load(open(path)) if os.path.exists(path) else {"n_stocks": S, "cases": {}}
    t0 = time.time()
    for case in which:
        runs = out["cases"].get(case, {}).get("runs", [])
        for k in range(len(runs), reps):
            panel, spread = simulate_panel(SEEDS[case] + k, S, **CASES[case])
            res = ex.run(panel, n_boot=499)
            row = {"verdict": res["verdict"], "n_identified": res["n_identified"], "n_common": res["n_common"],
                   "n_heterogeneous": res["n_heterogeneous"], "realized_true_spread": spread,
                   "tau_hat_median": float(np.median([v["tau"] for v in res["categories"].values() if v.get("tau") is not None])),
                   "U_median": float(np.median([v["U"] for v in res["categories"].values() if v.get("U") is not None]))}
            runs.append(row)
            v = [x["verdict"] for x in runs]
            out["cases"][case] = {"runs": runs, "verdicts": {x: v.count(x) for x in sorted(set(v))}}
            json.dump(out, open(path, "w"), indent=1)
            print(case, k, row, f"[{time.time() - t0:.0f}s]", flush=True)
