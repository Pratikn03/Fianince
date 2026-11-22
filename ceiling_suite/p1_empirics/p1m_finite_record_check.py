"""Finite-record check of the Taiwan calibration (P1M): exact Gaussian divergence of a T-day record against the
leading-order approximation T x (Whittle rate) used for the ranges and record lengths in the paper.

At the primary estimates, two nearby compositions (foreign memory +0.03 and +0.10, foreign weight x1.15 and x1.5) are
compared at T = 250, 900 (the median record per stock) and 1,500 days. Reads results/p1m_results.json only; no raw data.
Run: python p1m_finite_record_check.py   (writes results/p1m_finite_record_check.json)
"""
import json
from pathlib import Path

import numpy as np

import p1m_core as pm
from test_p1m_core import exact_kl_per_obs

HERE = Path(__file__).parent


def main():
    P = json.load(open(HERE / "results/p1m_results.json"))["runs"]["primary"]
    th = {k: (np.array(v) if isinstance(v, list) else v) for k, v in P["theta"].items()}
    th["delay"] = P["delay"]
    rows = []
    for scale in (0.3, 1.0):
        r2, w2 = th["r"].copy(), th["w"].copy()
        r2[0] += 0.1 * scale
        w2[0] *= 1 + 0.5 * scale
        wr = pm.kl_rate(th, r2, w2)
        for T in (250, 900, 1500):
            ex = exact_kl_per_obs(th, r2, w2, T=T)
            rows.append({"perturbation": scale, "T": T, "whittle_rate": wr, "exact_per_obs": ex, "ratio": ex / wr})
            print(f"perturbation {scale}: T={T}: exact / (T x Whittle) = {ex / wr:.4f}")
    out = {"median_stock_days": P["records"]["median_stock_days"], "rows": rows}
    (HERE / "results/p1m_finite_record_check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
