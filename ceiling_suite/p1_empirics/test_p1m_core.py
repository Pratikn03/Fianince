"""Checks of p1m_core on simulated markets (no data). Run: python test_p1m_core.py"""
import json
import time

import numpy as np
from scipy.linalg import toeplitz

import p1m_core as pm


def simulate(N=120, T=985, a=(0.55, 0.15, 0.08, 0.05, 0.03), kappa=0.02, r=(0.8, 0.5, 0.2), w=(-0.6, 0.4, -0.3),
             sig_x=0.01, sig_u=(0.10, 0.04, 0.03), seed=1, burn=400):
    """The paper's model with the empirical timing: F_c,t = r_c F_c,t-1 + w_c x_{t-1}; class flow u_c = F_c + N_c with
    non-feedback flow N_c,t = r_c N_c,t-1 + eta; x_t = sum_j a_j x_{t-j} + kappa sum_c u_c,t-1 + e_t."""
    rng = np.random.default_rng(seed)
    TT = T + burn
    p = len(a)
    x = np.zeros((N, TT)); F = np.zeros((3, N, TT)); Nn = np.zeros((3, N, TT))
    for t in range(1, TT):
        for c in range(3):
            F[c, :, t] = r[c] * F[c, :, t - 1] + w[c] * x[:, t - 1]
            Nn[c, :, t] = r[c] * Nn[c, :, t - 1] + sig_u[c] * rng.standard_normal(N)
        U = (F[:, :, t - 1] + Nn[:, :, t - 1]).sum(0)
        x[:, t] = sum(a[j] * x[:, t - 1 - j] for j in range(min(p, t))) + kappa * U + sig_x * rng.standard_normal(N)
    u = F + Nn
    sl = slice(burn, TT)
    prep = {"x": x[:, sl], "U": np.arange(N), "usable": np.ones((N, T), bool),
            "u": {"Foreign": u[0][:, sl], "Trust": u[1][:, sl], "DealerTotal": u[2][:, sl], "DealerOwn": u[2][:, sl]}}
    prep["usable"][:, :6] = False
    return prep


def exact_kl_per_obs(th, r2, w2, T=1500):
    """Exact Gaussian KL / T for two stationary processes with spectra 1/|A|^2 (autocovariances by inverse FFT)."""
    M = 1 << 16
    om = 2 * np.pi * np.arange(M) / M
    z = np.exp(-1j * om)
    def acov(r, w):
        f = 1 / np.abs(pm.A_of(th, r, w, z)) ** 2
        return np.real(np.fft.ifft(f))[:T]
    S1, S2 = toeplitz(acov(th["r"], th["w"])), toeplitz(acov(r2, w2))
    L2 = np.linalg.cholesky(S2)
    X = np.linalg.solve(L2, np.linalg.cholesky(S1))
    tr = np.sum(X ** 2)
    ld1 = 2 * np.sum(np.log(np.diag(np.linalg.cholesky(S1))))
    ld2 = 2 * np.sum(np.log(np.diag(L2)))
    return 0.5 * (tr - T + ld2 - ld1) / T


if __name__ == "__main__":
    out = {}
    t0 = time.time()
    truth = dict(a=(0.55, 0.15, 0.08, 0.05, 0.03), kappa=0.02, r=(0.8, 0.5, 0.2), w=(-0.6, 0.4, -0.3))
    prep = simulate()
    mask = np.ones(985, bool)
    eqs = pm.build_equations(prep, mask)
    th, stats, ci, nb = pm.estimate(eqs, B_=199)
    out["estimates"] = {"r": th["r"].tolist(), "w": th["w"].tolist(), "kappa": th["kappa"], "a": th["a"].tolist()}
    out["truth"] = truth
    ok_r = np.allclose(th["r"], truth["r"], atol=0.03)
    ok_w = np.allclose(th["w"], truth["w"], atol=0.08)
    ok_k = abs(th["kappa"] - truth["kappa"]) < 0.004
    out["check_recovery"] = bool(ok_r and ok_w and ok_k)
    # truth inside bootstrap intervals
    Htrue = truth["kappa"] * np.array(truth["w"]) / (1 - np.array(truth["r"]))
    out["H_true"] = Htrue.tolist()
    out["H_ci"] = {c: ci[f"H_{c}"]["ci95"] for c in pm.CLASSES}
    out["check_H_in_ci"] = bool(all(ci[f"H_{c}"]["ci95"][0] - 0.002 <= Htrue[k] <= ci[f"H_{c}"]["ci95"][1] + 0.002
                                    for k, c in enumerate(pm.CLASSES)))
    # relabelings are exactly indistinguishable
    rates_perm = [pm.kl_rate(th, th["r"][list(p)], th["w"][list(p)]) for p in [(1, 0, 2), (2, 1, 0), (1, 2, 0)]]
    out["check_relabel_rate_zero"] = bool(max(abs(x) for x in rates_perm) < 1e-15)
    # Whittle rate against exact finite-record KL, for a nearby composition
    thW = {"a": np.array([0.5, 0.1]), "kappa": 0.3, "r": np.array([0.8, 0.5, 0.2]), "w": np.array([-0.6, 0.4, -0.3]),
           "delay": 1}
    r2, w2 = np.array([0.7, 0.5, 0.2]), np.array([-0.5, 0.4, -0.3])
    wr = pm.kl_rate(thW, r2, w2)
    ex = exact_kl_per_obs(thW, r2, w2)
    out["whittle_vs_exact"] = {"whittle": wr, "exact_T1500": ex}
    out["check_whittle"] = bool(abs(wr - ex) / wr < 0.02)
    # stationarity polynomial: roots agree with zeros of A
    st, mr = pm.stationary(th)
    roots = np.roots(pm.char_poly(th)[::-1])
    zr = roots[np.argmin(np.abs(roots))]
    Az = pm.A_of(th, z=np.array([zr]))[0]
    out["check_char_poly"] = bool(st and abs(Az) * np.prod([abs(1 - rc * zr) for rc in th["r"]]) < 1e-8)
    # Q1: tags carry more information than prices about a single-memory alternative (data processing inequality)
    q1p = pm.q1_price(th)
    S, ok = pm.tag_filters(prep, mask, th)
    res = []
    common = ok.copy()
    for c in pm.CLASSES:
        common &= eqs[c]["ok"]
    for c in pm.CLASSES:
        e = eqs[c]["yd"] - eqs[c]["Xd"] @ np.array(stats[c]["coef"])
        res.append(e[common])
    Om = np.cov(np.vstack(res))
    q1t = pm.q1_tags(th, S, ok, Om)
    out["Q1"] = {"price_rate": q1p["rate"], "tag_rate": q1t["rate"], "R_price": q1p["R"], "R_tags": q1t["R"]}
    # the same alternative evaluated on both records
    Wsum = float(np.sum(q1t["W"]))
    out["Q1"]["price_rate_at_tag_alternative"] = pm.kl_rate(th, [q1t["R"], 0, 0], [Wsum, 0, 0])
    out["check_data_processing"] = bool(q1t["rate"] >= out["Q1"]["price_rate_at_tag_alternative"])
    # Q1 tag rate against a direct Monte Carlo of the flow-prediction difference under the alternative
    out["check_q1_min_le_grid"] = bool(q1p["rate"] <= min(pm.kl_rate(th, [R, 0, 0], [W, 0, 0])
                                                      for R in np.linspace(-0.9, 0.9, 19) for W in np.linspace(-1, 1, 41)) + 1e-18)
    # Q2/Q3 on the pooled record
    n_rec = float(eqs["price"]["n"].sum())
    hbar, _ = pm.hbar_of(th)
    rg = pm.ranges(th, n_rec, hbar, n_random=12)
    out["Q2Q3"] = {k: (rg[k] if not isinstance(rg[k], dict) else {kk: rg[k][kk] for kk in ("min", "max")}) for k in rg}
    eff = pm.effects(th)
    out["check_range_contains_estimate"] = bool(rg["H_Foreign"]["min"] <= eff["H"][0] <= rg["H_Foreign"]["max"]
                                                and rg["U"]["min"] <= eff["U"] <= rg["U"]["max"])
    out["check_range_contains_relabelings"] = bool(rg["H_Foreign"]["min"] <= min(eff["H"]) + 1e-12 and
                                                   rg["H_Foreign"]["max"] >= max(eff["H"]) - 1e-12)
    for k in ("min", "max"):
        rr = rg["H_Foreign"][k + "_rules"]
        out.setdefault("check_extremes_feasible", True)
        out["check_extremes_feasible"] &= bool(n_rec * rr["rate"] <= pm.J0 * (1 + 1e-9))
    out["width_H"] = rg["H_Foreign"]["max"] - rg["H_Foreign"]["min"]
    out["width_U"] = rg["U"]["max"] - rg["U"]["min"]
    out["check_uniform_narrower"] = bool(out["width_U"] < out["width_H"])
    out["seconds"] = time.time() - t0
    checks = {k: v for k, v in out.items() if k.startswith("check_")}
    out["all_pass"] = all(checks.values())
    print(json.dumps(out, indent=1, default=float))
    json.dump(out, open("test_p1m_core_results.json", "w"), indent=1, default=float)
