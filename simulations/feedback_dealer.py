"""Funded-dealer simulation with genuine price<->flow feedback.

Replaces tests/test_solvency_phase_diagram.py::simulate_dealer_solvency, whose
price was an exogenous AR(1) (S never entered the price) and whose
"non-AI" benchmark was random noise rather than inventory control.

Market (single-cohort specialization of eq. heterogeneous, S = a + Q):
    x_{t+1} = a x_t + y_t + lam * n_t + sig * e_t          (price deviation)
    y_{t+1} = (1 - eta) y_t + eta * Q * x_t                (adaptive pressure)
    D_t     = y_t / lam                                     (adaptive demand)
Dealer takes the other side of all market flow f_t = D_t + n_t (+ phi*I_t
induced by its own quote skew when inventory control is on):
    I_{t+1}   = I_t - f_t
    cash_{t+1}= cash_t + f_t * p_t + (s/2)|f_t|,   p_t = 1 + x_t
    E_t       = E0 + cash_t + I_t p_t
Halt if |I_t| p_t > L * E_t or E_t <= 0.

Benchmarks with NO price->flow loop (flow exogenous, price impact retained):
    B1  iid flow, variance matched to the feedback flow f
    B2  AR(1) flow, variance and lag-1 autocorrelation matched
    B3  AR(1) flow, variance and long-run variance (sum of autocovariances) matched
Outputs: results/provenance/solvency_feedback.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "provenance" / "solvency_feedback.json"

BASE = dict(a=0.5, eta=0.2, lam=0.002, sig=0.0005, s=0.002, E0=1.0, T=500)


def flow_moments(S: float, p=BASE, n=400_000, seed=0) -> dict:
    """Stationary variance, lag-1 autocorrelation and long-run variance of
    the feedback flow f = y/lam + n (estimated from one long path)."""
    rng = np.random.default_rng(seed)
    a, eta, lam, sig = p["a"], p["eta"], p["lam"], p["sig"]
    Q = S - a
    x = y = 0.0
    f = np.empty(n)
    nn = rng.standard_normal(n)
    ee = rng.standard_normal(n)
    for t in range(n):
        f[t] = y / lam + nn[t]
        x, y = a * x + y + lam * nn[t] + sig * ee[t], (1 - eta) * y + eta * Q * x
    f = f[10_000:]
    f = f - f.mean()
    v = f.var()
    ac1 = float(np.dot(f[1:], f[:-1]) / (len(f) - 1) / v)
    # long-run variance via Bartlett window
    Lw = 400
    lrv = v
    for k in range(1, Lw + 1):
        lrv += 2 * (1 - k / (Lw + 1)) * np.dot(f[k:], f[:-k]) / len(f)
    a_, Q_ = p["a"], S - p["a"]
    lrv_exact = ((1 - a_) ** 2 + (Q_ * sig / lam) ** 2) / (1 - S) ** 2  # zero-frequency gain, Prop. flow_gain
    return {"var": float(v), "ac1": ac1, "lrv_bartlett": float(lrv), "lrv": float(lrv_exact)}


def _ar1_for_lrv(var: float, lrv: float) -> float:
    # AR(1) with variance v and coefficient r has lrv = v (1+r)/(1-r)
    ratio = lrv / var
    return float((ratio - 1) / (ratio + 1))


def simulate(S: float, L: float, phi: float, mode: str, n_seeds: int, mom: dict | None = None,
             p=BASE, seed0=0) -> dict:
    a, eta, lam, sig, s, E0, T = (p[k] for k in ("a", "eta", "lam", "sig", "s", "E0", "T"))
    Q = S - a
    halts = 0
    halt_times = []
    for sd in range(n_seeds):
        rng = np.random.default_rng(seed0 + sd)
        nn = rng.standard_normal(T)
        ee = rng.standard_normal(T)
        x = y = 0.0
        I = cash = 0.0
        g = 0.0  # exogenous AR(1) flow state for B2/B3
        if mode == "B1":
            sd_f = np.sqrt(mom["var"])
        elif mode in ("B2", "B3"):
            r = mom["ac1"] if mode == "B2" else _ar1_for_lrv(mom["var"], mom["lrv"])
            r = min(max(r, -0.999), 0.999)
            innov_sd = np.sqrt(mom["var"] * (1 - r * r))
            g = np.sqrt(mom["var"]) * rng.standard_normal()
        halted = False
        for t in range(T):
            pt = 1.0 + x
            if mode == "feedback":
                f_exog = y / lam + nn[t]
            elif mode == "B1":
                f_exog = sd_f * nn[t]
            else:
                f_exog = g
                g = r * g + innov_sd * nn[t]
            f = f_exog + phi * I
            cash += f * pt + 0.5 * s * abs(f)
            I -= f
            if mode == "feedback":
                x, y = a * x + y + lam * nn[t] + sig * ee[t], (1 - eta) * y + eta * Q * x
            else:
                x = a * x + lam * f_exog + sig * ee[t]
            E = E0 + cash + I * (1.0 + x)
            if E <= 0 or abs(I) * (1.0 + x) > L * E:
                halted = True
                halt_times.append(t)
                break
        halts += halted
    from scipy.stats import beta as _beta

    k, n = halts, n_seeds
    lo = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))
    return {"S": S, "L": L, "phi": phi, "mode": mode, "halts": k, "n": n, "rate": k / n,
            "ci95_exact": [lo, hi],
            "median_halt_time": float(np.median(halt_times)) if halt_times else None}


def run(S_grid=(0.5, 0.6, 0.7, 0.8, 0.9, 0.95), L_grid=(10.0, 20.0), phi_grid=(0.05, 0.10),
        n_seeds=400) -> dict:
    out = {"params": BASE, "S_grid": list(S_grid), "moments": {}, "cells": []}
    for S in S_grid:
        mom = flow_moments(S)
        out["moments"][str(S)] = mom
        for L in L_grid:
            for phi in phi_grid:
                for mode in ("feedback", "B1", "B2", "B3"):
                    out["cells"].append(simulate(S, L, phi, mode, n_seeds, mom))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    r = run()
    for S, m in r["moments"].items():
        print("S", S, {k: round(v, 3) for k, v in m.items()})
    for c in r["cells"]:
        print(c["S"], c["L"], c["phi"], c["mode"], f"{c['rate']:.3f}", [round(v, 3) for v in c["ci95_exact"]])
