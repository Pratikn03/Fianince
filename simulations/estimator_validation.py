"""Monte Carlo validation of the Section-7 estimator (empirical_pipeline.feedback_var).

The estimator is applied to synthetic (price, flow) paths whose true
feedback is known, using exactly the same EMA construction as on real data.

  G0  no feedback, long-memory exogenous flow (order splitting): Q_true = 0
  G1  single-cohort feedback, iid flow noise:          Q_true = (1-alpha) lam c
  G2  two-cohort feedback (fast + slow), iid noise:    Q_true = (1-alpha) lam (c1 + c2)
  G3  G1 + long-memory exogenous flow

Derivation (G1): p_{t+1} = p_t + lam f_t + sig e;  m_{t+1}=(1-alpha)m_t+alpha p_{t+1};
x = p - m  =>  x_{t+1} = (1-alpha)(x_t + lam f_t + sig e).  With
f_{t+1} = (1-eta) f_t + eta c x_t + u, J = [[1-alpha, (1-alpha)lam],[eta c, 1-eta]],
so Q = (1-alpha) lam c and S = (1-alpha) + Q.
Outputs: results/provenance/estimator_validation.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from empirical_pipeline.feedback_var import c_flow_controlled, q_long_memory_robust, var1

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "provenance" / "estimator_validation.json"

ALPHA = 2.0 / 31.0  # Delta = 10 s, W = 300 s
LAM, SIG = 1.0, 3.0
LM_RATES = (0.5, 0.9, 0.98, 0.995)


def _long_memory(n, rng, scale=1.0):
    out = np.zeros(n)
    for r in LM_RATES:
        g = 0.0
        sd = np.sqrt(1 - r * r) * scale / np.sqrt(len(LM_RATES))
        e = rng.standard_normal(n)
        comp = np.empty(n)
        for t in range(n):
            comp[t] = g
            g = r * g + sd * e[t]
        out += comp
    return out


def simulate(dgp: str, n: int, rng, c=0.012, eta=0.2, c_slow=0.006, eta_slow=0.02):
    lm = _long_memory(n, rng) if dgp in ("G0", "G3") else np.zeros(n)
    u = rng.standard_normal(n)
    e = rng.standard_normal(n)
    x = 0.0
    f1 = f2 = 0.0
    xs = np.empty(n)
    fs = np.empty(n)
    for t in range(n):
        if dgp == "G0":
            f = lm[t] + u[t]
        elif dgp in ("G1", "G3"):
            f = f1 + u[t] + lm[t]
        else:
            f = f1 + f2 + u[t]
        xs[t], fs[t] = x, f
        x_new = (1 - ALPHA) * (x + LAM * f + SIG * e[t])
        if dgp in ("G1", "G3"):
            f1 = (1 - eta) * f1 + eta * c * x
        elif dgp == "G2":
            f1 = (1 - eta) * f1 + eta * c * x
            f2 = (1 - eta_slow) * f2 + eta_slow * c_slow * x
        x = x_new
    return xs, fs


def q_true(dgp, c=0.012, c_slow=0.006):
    if dgp == "G0":
        return 0.0
    if dgp in ("G1", "G3"):
        return (1 - ALPHA) * LAM * c
    return (1 - ALPHA) * LAM * (c + c_slow)


def run(n_rep=60, n=8640, seed=20261003) -> dict:
    out = {"alpha": ALPHA, "n_per_rep": n, "n_rep": n_rep, "dgps": {}}
    for k, dgp in enumerate(("G0", "G1", "G2", "G3")):
        rng = np.random.default_rng(seed + k)
        Q, S, c1, c90, q30, q90 = [], [], [], [], [], []
        for _ in range(n_rep):
            x, f = simulate(dgp, n, rng)
            est = var1(x, f)
            Q.append(est["Q"]); S.append(est["S"])
            c1.append(c_flow_controlled(x, f, 1)); c90.append(c_flow_controlled(x, f, 90))
            q30.append(q_long_memory_robust(x, f, 30)["Q_L"]); q90.append(q_long_memory_robust(x, f, 90)["Q_L"])
        Q, S, c1, c90, q30, q90 = map(np.asarray, (Q, S, c1, c90, q30, q90))
        qt = q_true(dgp)
        out["dgps"][dgp] = {
            "Q_true": qt, "S_true": (1 - ALPHA) + qt,
            "Q_mean": float(Q.mean()), "Q_sd": float(Q.std(ddof=1)),
            "Q_bias_rel": float((Q.mean() - qt) / qt) if qt else None,
            "S_mean": float(S.mean()),
            "Q_L30_mean": float(q30.mean()), "Q_L30_sd": float(q30.std(ddof=1)),
            "Q_L90_mean": float(q90.mean()), "Q_L90_sd": float(q90.std(ddof=1)),
            "share_Q_pos": float(np.mean(Q > 0)),
            "c_L1_mean": float(c1.mean()), "c_L90_mean": float(c90.mean()),
            "c_ratio_90_1": float(c90.mean() / c1.mean()) if c1.mean() != 0 else None,
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    r = run()
    for k, v in r["dgps"].items():
        print(k, {kk: (round(vv, 5) if isinstance(vv, float) else vv) for kk, vv in v.items()})
