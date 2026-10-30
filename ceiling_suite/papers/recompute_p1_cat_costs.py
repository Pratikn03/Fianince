"""Paper 1, Section 8.2: disclosure in dollars.

Compares the yearly price-only round-trip probing trading loss (Theorem 5.1 spectral bound,
repeated R times per year as certificates are renewed) with the published annual running costs
of the U.S. Consolidated Audit Trail (CAT).

For K >= 2 unknown cohorts, the two-point constant is derived directly from the K-point Gauss
and Gauss-Radau quadrature rules of Theorem thm:kcohort and Table tab:radau (moment gaps
Delta_2 = 2/9 = 0.2222, Delta_3 = 8/150 = 0.0533, Delta_4 = 32/2450 = 0.0131 at order 2K-1),
evaluating the exact spectral round-trip trading loss bound
    L_rt^*(K, Delta_eta) = 4 * sigma^2 * z_{0.95}^2 * inf_omega g_0^{(K)}(omega) / |Delta H_K(e^{i omega})|^2
across a single separation variable Delta_eta.

External benchmarks (cited with primary source page numbers):
  - CAT LLC 2025 Financial and Operating Budget: $248.8M ($248,846,076, Nov. 2024 filing;
    SEC Release No. 34-101901, p. 4), revised to $228.3M in the May 2025 mid-year update.
  - SEC Rule 613 proposing release, Release No. 34-62174 (May 26, 2010, 75 FR 32556 at
    32598, 32600, pp. 147, 153): $4.0B initial industry build and $2.1B ongoing annual cost
    (adopted with modifications in Release No. 34-67457, July 18, 2012, 77 FR 45722 at
    45790-45795, pp. 220-238).
  - SEC Order Approving the CAT NMS Plan, Release No. 34-79318 (Nov. 15, 2016, 81 FR 84696
    at 84801, p. 363): $2.4B initial industry build and $1.7B ongoing annual cost.

Output: ceiling_suite/papers/recomputed/R_P1_cat_disclosure_dollars.json
"""
from __future__ import annotations

import json
import os
import numpy as np
from scipy.stats import norm
from numpy.polynomial.legendre import leggauss
from numpy.polynomial import legendre as L

HERE = os.path.dirname(os.path.abspath(__file__))

A_PAR, KAPPA_PAR, Q_PAR, ETA_BAR, SIGMA_PAR = 0.5, 0.8, 0.2, 0.4, 0.01
W_MERGED = Q_PAR * ETA_BAR          # 0.08 total merged weight
R_CENTER = 1.0 - ETA_BAR            # 0.60 center memory rate
Z_95 = float(norm.ppf(0.95))

SIGMA_ROLL = 0.4019011506831126     # USDT, median Roll estimate (Table tab:capital)
SIGMA_1S = 1.9762563262273953       # USDT, median one-second price-change s.d. (Table tab:capital)
C_REF_K2_KNOWN = 61.41              # certified round-trip loss at sigma=0.01, delta=0.05 (Delta_eta=0.10)

CAT_BUDGET_2025_NOV2024 = 248.8e6   # CAT LLC Nov 2024 2025 operating budget ($248,846,076)
CAT_BUDGET_2025_MAY2025 = 228.3e6   # CAT LLC May 2025 revised 2025 operating budget ($228.3M), superseded
CAT_BUDGET_2026_MAR2026 = 147.044869e6  # CAT LLC 2026 Financial and Operating Budget, 31 Mar 2026: total expenses $147,044,869
CAT_ANNUAL_INDUSTRY_2016 = 1.7e9    # SEC Release No. 34-79318 (2016), 81 FR 84801, p. 363
CAT_BUILD_INDUSTRY_2016 = 2.4e9     # SEC Release No. 34-79318 (2016), 81 FR 84801, p. 363
CAT_ANNUAL_INDUSTRY_2010 = 2.1e9    # SEC Release No. 34-62174 (2010), 75 FR 32600, p. 153
CAT_BUILD_INDUSTRY_2010 = 4.0e9     # SEC Release No. 34-62174 (2010), 75 FR 32598, p. 147


def imp_from_merged(w_merged: np.ndarray, r_mem: np.ndarray, T: int = 400) -> np.ndarray:
    u = np.zeros(len(w_merged))
    h = np.zeros(T)
    xp = 0.0
    for t in range(T):
        u = r_mem * u + w_merged * xp
        xt = A_PAR * xp + KAPPA_PAR * float(np.sum(u)) + (KAPPA_PAR if t == 0 else 0.0)
        h[t] = xt
        xp = xt
    return h


def Hhat(h: np.ndarray, om: np.ndarray) -> np.ndarray:
    return np.exp(-1j * np.outer(om, np.arange(len(h)))) @ h


def gauss_radau_rules(K: int):
    xg, wg = leggauss(K)
    wg = wg / 2.0
    c = np.zeros(K + 1)
    c[K - 1] = 1.0
    c[K] = 1.0
    xr = np.sort(np.real(L.legroots(c)))
    V = np.vander(xr, K, increasing=True).T
    mom = np.array([(1.0 - (-1.0) ** (j + 1)) / (2.0 * (j + 1)) for j in range(K)])
    wr = np.linalg.solve(V, mom)
    gap = float((wg * xg ** (2 * K - 1)).sum() - (wr * xr ** (2 * K - 1)).sum())
    return xg, wg, xr, wr, gap


def spectral_loss_gauss_radau(K: int, deta: float) -> dict:
    xg, wg, xr, wr, gap = gauss_radau_rules(K)
    hG = imp_from_merged(W_MERGED * wg, R_CENTER + deta * xg)
    hR = imp_from_merged(W_MERGED * wr, R_CENTER + deta * xr)
    om = np.linspace(1e-4, np.pi, 10001)
    HG = Hhat(hG, om)
    HR = Hhat(hR, om)
    g0 = HG.real - KAPPA_PAR / 2.0
    ratios = g0 / np.abs(HR - HG) ** 2
    idx = int(np.argmin(ratios))
    L_par = float(4.0 * SIGMA_PAR ** 2 * Z_95 ** 2 * ratios[idx])
    return {
        "K": K,
        "deta": deta,
        "moment_gap_order": 2 * K - 1,
        "moment_gap_constant": round(gap, 6),
        "omega_star": round(float(om[idx]), 4),
        "norm_dh": float(np.linalg.norm(hR - hG)),
        "L_rt_par": round(L_par, 2),
        "L_rt_roll_usd": round(L_par * (SIGMA_ROLL / SIGMA_PAR) ** 2, 0),
        "L_rt_1s_usd": round(L_par * (SIGMA_1S / SIGMA_PAR) ** 2, 0),
    }


def loss_k2_known_pair(deta: float) -> dict:
    # Known pair with rates eta_bar +/- delta, so full rate separation is Delta_eta = 2 * delta
    delta = deta / 2.0
    L_par = C_REF_K2_KNOWN * (0.05 / delta) ** 4
    L_roll = L_par * (SIGMA_ROLL / SIGMA_PAR) ** 2
    L_1s = L_par * (SIGMA_1S / SIGMA_PAR) ** 2
    return {
        "K": 2,
        "deta": deta,
        "delta_half_spacing": delta,
        "L_rt_par": round(L_par, 2),
        "L_rt_roll_usd": round(L_roll, 0),
        "L_rt_1s_usd": round(L_1s, 0),
    }


def main():
    rows = []
    # 1. Known two-cohort pair (Section 5, Table tab:capital), indexed by full spacing Delta_eta = 2 * delta
    for deta in (0.20, 0.10, 0.04):
        info = loss_k2_known_pair(deta)
        l_roll_1 = info["L_rt_roll_usd"]
        l_roll_52 = 52.0 * l_roll_1
        l_1s_52 = 52.0 * info["L_rt_1s_usd"]
        rows.append({
            "case": "K=2, known pair",
            "K": 2,
            "deta": deta,
            "moment_gap_constant": None,
            "loss_per_probe_roll_usd": int(round(l_roll_1)),
            "loss_per_probe_1s_usd": int(round(info["L_rt_1s_usd"])),
            "annual_loss_weekly_roll_usd": int(round(l_roll_52)),
            "annual_loss_weekly_1s_usd": int(round(l_1s_52)),
            "markets_cat_llc_228m_weekly_roll": round(CAT_BUDGET_2025_MAY2025 / l_roll_52, 1),
            "markets_cat_llc_228m_weekly_1s": round(CAT_BUDGET_2025_MAY2025 / l_1s_52, 2),
            "markets_cat_llc_2026_147m_weekly_roll": round(CAT_BUDGET_2026_MAR2026 / l_roll_52, 1),
            "markets_cat_llc_2026_147m_weekly_1s": round(CAT_BUDGET_2026_MAR2026 / l_1s_52, 2),
            "markets_sec_1700m_weekly_roll": round(CAT_ANNUAL_INDUSTRY_2016 / l_roll_52, 1),
            "markets_sec_1700m_weekly_1s": round(CAT_ANNUAL_INDUSTRY_2016 / l_1s_52, 2),
        })

    # 2. Unknown K-cohort Gauss vs Gauss-Radau two-point bound (Theorem thm:kcohort, Table tab:radau)
    for K, deta in ((2, 0.20), (2, 0.10), (3, 0.20), (3, 0.10), (4, 0.20)):
        info = spectral_loss_gauss_radau(K, deta)
        l_roll_1 = info["L_rt_roll_usd"]
        l_roll_52 = 52.0 * l_roll_1
        l_1s_52 = 52.0 * info["L_rt_1s_usd"]
        rows.append({
            "case": f"K={K}, Gauss-Radau pair",
            "K": K,
            "deta": deta,
            "moment_gap_constant": info["moment_gap_constant"],
            "loss_per_probe_roll_usd": int(round(l_roll_1)),
            "loss_per_probe_1s_usd": int(round(info["L_rt_1s_usd"])),
            "annual_loss_weekly_roll_usd": int(round(l_roll_52)),
            "annual_loss_weekly_1s_usd": int(round(l_1s_52)),
            "markets_cat_llc_228m_weekly_roll": round(CAT_BUDGET_2025_MAY2025 / l_roll_52, 1),
            "markets_cat_llc_228m_weekly_1s": round(CAT_BUDGET_2025_MAY2025 / l_1s_52, 2),
            "markets_cat_llc_2026_147m_weekly_roll": round(CAT_BUDGET_2026_MAR2026 / l_roll_52, 1),
            "markets_cat_llc_2026_147m_weekly_1s": round(CAT_BUDGET_2026_MAR2026 / l_1s_52, 2),
            "markets_sec_1700m_weekly_roll": round(CAT_ANNUAL_INDUSTRY_2016 / l_roll_52, 1),
            "markets_sec_1700m_weekly_1s": round(CAT_ANNUAL_INDUSTRY_2016 / l_1s_52, 2),
        })

    for r in rows:
        print(r)

    out = {
        "benchmarks": {
            "cat_llc_2025_nov2024_usd": CAT_BUDGET_2025_NOV2024,
            "cat_llc_2025_may2025_usd": CAT_BUDGET_2025_MAY2025,
            "cat_llc_2026_mar2026_usd": CAT_BUDGET_2026_MAR2026,
            "sec_2016_annual_industry_usd": CAT_ANNUAL_INDUSTRY_2016,
            "sec_2016_build_industry_usd": CAT_BUILD_INDUSTRY_2016,
            "sec_2010_annual_industry_usd": CAT_ANNUAL_INDUSTRY_2010,
            "sec_2010_build_industry_usd": CAT_BUILD_INDUSTRY_2010,
            "sources": [
                "CAT LLC 2025 Financial and Operating Budget ($248.8M in Nov. 2024, SEC Release No. 34-101901, p. 4; revised to $228.3M in May 2025)",
                "SEC Release No. 34-62174 (May 26, 2010, 75 FR 32556 at 32598, 32600, pp. 147, 153) and Release No. 34-67457 (July 18, 2012, 77 FR 45722 at 45790-45795, pp. 220-238)",
                "SEC Release No. 34-79318 (Nov. 15, 2016, 81 FR 84696 at 84801, p. 363)",
            ],
        },
        "caveat": "Probing cost is a lower bound on the cost of learning from prices, not a social cost.",
        "sigma_roll": SIGMA_ROLL,
        "sigma_1s": SIGMA_1S,
        "renewal_per_year": 52,
        "rows": rows,
    }
    fp = os.path.join(HERE, "recomputed", "R_P1_cat_disclosure_dollars.json")
    json.dump(out, open(fp, "w"), indent=2)
    print("Wrote", fp)


if __name__ == "__main__":
    main()
