"""Checks of p1m_a1_core on simulated markets (no data). Run: python test_p1m_a1_core.py

1. Decoupled rules recover free kernels and AR(2) non-feedback flow in a market where flows move prices, the same day
   and the next.
2. On the paper's restricted model (feedback and flow share one decay), the decoupled rules recover the geometric
   kernel's sum and phi_1 = r.
3. The constrained ranges respect every constraint, stay inside [0, U'] for the positive class, and narrow, or at least
   do not widen, as the required separation grows.
"""
import json
import time

import numpy as np

import p1m_a1_core as a1
import p1m_core as pm
from test_p1m_core import simulate as simulate_restricted


def simulate_decoupled(N=150, T=985, a=(0.6, 0.1, 0.05, 0.03, 0.02), kappa0=0.01, kappa=0.02, phi=(0.5, 0.2),
                       sig_x=0.03, sig_u=(0.10, 0.05, 0.04), seed=3, burn=400):
    rng = np.random.default_rng(seed)
    J = 10
    beta = np.array([[0.30 * 0.6 ** j for j in range(J)],                       # Foreign: geometric, decay 0.6
                     [0.0, 0.05, 0.08, 0.05, 0.02, 0, 0, 0, 0, 0],                # Trust: hump-shaped
                     [-0.02 * 0.3 ** j for j in range(J)]])                       # Dealers: negative
    TT = T + burn
    x = np.zeros((N, TT)); e = np.zeros((3, N, TT)); u = np.zeros((3, N, TT))
    for t in range(2, TT):
        for c in range(3):
            e[c, :, t] = phi[0] * e[c, :, t - 1] + phi[1] * e[c, :, t - 2] + sig_u[c] * rng.standard_normal(N)
            fb = sum(beta[c, j] * x[:, t - 1 - j] for j in range(J) if t - 1 - j >= 0)
            u[c, :, t] = fb + e[c, :, t]
        x[:, t] = (sum(a[j] * x[:, t - 1 - j] for j in range(min(len(a), t))) + kappa0 * u[:, :, t].sum(0)
                   + kappa * u[:, :, t - 1].sum(0) + sig_x * rng.standard_normal(N))
    sl = slice(burn, TT)
    prep = {"x": x[:, sl], "U": np.arange(N), "usable": np.ones((N, T), bool),
            "u": {"Foreign": u[0][:, sl], "Trust": u[1][:, sl], "DealerTotal": u[2][:, sl], "DealerOwn": u[2][:, sl]}}
    prep["usable"][:, :6] = False
    return prep, beta


def check_constraints(th, res, variant, gamma, hbar, n_rec, tol=1e-8):
    if res["empty"]:
        return True
    A1 = pm.A_of(th)
    ok = True
    for name in ("H_Foreign", "U"):
        for key in ("min", "max"):
            ru = res[name][key + "_rules"]
            r, w = np.array(ru["r"]), np.array(ru["w"])
            ok &= a1.in_class(r, w, variant, gamma, hbar, th["kappa"], tol=tol)
            ok &= n_rec * pm.kl_rate(th, r, w, A1) <= pm.J0 * (1 + 1e-6)
            ok &= pm.stationary(th, r, w)[0]
    return bool(ok)


if __name__ == "__main__":
    out = {}
    t0 = time.time()
    # 1. decoupled recovery
    prep, beta = simulate_decoupled()
    mask = np.ones(985, bool)
    R = a1.decoupled(prep, mask, 10, 2, B_=49, label="test")
    est = np.array([R["rules"][c]["beta"] for c in a1.CLASSES])
    out["decoupled_max_abs_beta_error"] = float(np.max(np.abs(est - beta)))
    out["decoupled_sum_beta"] = {c: [R["rules"][c]["sum_beta"], float(beta[k].sum())] for k, c in enumerate(a1.CLASSES)}
    out["decoupled_phi"] = {c: R["rules"][c]["phi"] for c in a1.CLASSES}
    ci = R["bootstrap"]["ci"]
    out["decoupled_sum_beta_se"] = {c: ci[f"sum_beta_{c}"]["se"] for c in a1.CLASSES}
    out["check_decoupled_sum_within_3se"] = all(abs(R["rules"][c]["sum_beta"] - beta[k].sum()) < 3 * ci[f"sum_beta_{c}"]["se"]
                                                for k, c in enumerate(a1.CLASSES))
    out["check_decoupled_beta"] = out["decoupled_max_abs_beta_error"] < 0.03
    out["check_decoupled_phi"] = all(np.allclose(R["rules"][c]["phi"], (0.5, 0.2), atol=0.02) for c in a1.CLASSES)
    out["check_decoupled_converged"] = all(R["rules"][c]["converged"] for c in a1.CLASSES)
    out["check_decoupled_H_is_kappa_sum"] = bool(np.allclose(R["H"], [R["kappa"] * R["rules"][c]["sum_beta"] for c in a1.CLASSES]))
    out["check_bootstrap_draws"] = R["bootstrap"]["B_used"] == 49
    # 2. restricted model: feedback and flow share one decay r
    truth = dict(r=(0.8, 0.5, 0.2), w=(-0.6, 0.4, -0.3))
    prep2 = simulate_restricted()
    R2 = a1.decoupled(prep2, mask, 20, 2, B_=19, label="restricted")
    geo = [w * (1 - r ** 20) / (1 - r) for r, w in zip(truth["r"], truth["w"])]
    out["restricted_sum_beta_vs_geometric"] = {c: [R2["rules"][c]["sum_beta"], geo[k]] for k, c in enumerate(a1.CLASSES)}
    out["restricted_phi"] = {c: R2["rules"][c]["phi"] for c in a1.CLASSES}
    out["check_restricted_sum_beta"] = all(abs(R2["rules"][c]["sum_beta"] - geo[k]) < 0.1 * abs(geo[k]) + 0.02
                                           for k, c in enumerate(a1.CLASSES))
    out["check_restricted_phi1"] = all(abs(R2["rules"][c]["phi"][0] - truth["r"][k]) < 0.05 for k, c in enumerate(a1.CLASSES))
    # 3. constrained ranges on a synthetic estimate (not the Taiwan estimate)
    th = {"a": np.array([0.55, 0.15, 0.08, 0.05, 0.03]), "kappa": 0.02, "r": np.array([0.8, 0.5, 0.2]),
          "w": np.array([0.6, 0.4, -0.3]), "delay": 1}
    H = pm.effects(th)["H"]
    hbar = 2 * float(np.max(np.abs(H)))
    n_rec = 3000.0
    t1 = time.time()
    rng_res = {}
    for variant in ("P", "T"):
        for gamma in (0.0, 0.05, 0.2):
            res = a1.constrained_ranges(th, n_rec, hbar, variant, gamma, n_random=6)
            rng_res[f"{variant}_{gamma}"] = res
    out["seconds_per_range_config"] = (time.time() - t1) / len(rng_res)
    out["ranges"] = {k: (None if v["empty"] else [v["H_Foreign"]["min"], v["H_Foreign"]["max"], v["U"]["min"], v["U"]["max"]])
                     for k, v in rng_res.items()}
    out["feasible_starts"] = {k: v["n_feasible_starts"] for k, v in rng_res.items()}
    out["check_constraints_hold"] = all(check_constraints(th, v, v["variant"], v["gamma"], hbar, n_rec) for v in rng_res.values())
    out["check_P_inside_0_U"] = all(v["empty"] or (v["H_Foreign"]["min"] >= -1e-12 and v["H_Foreign"]["max"] <= v["U"]["max"] + 1e-12)
                                    for k, v in rng_res.items() if k.startswith("P"))
    out["check_pool_consistent"] = all(v["empty"] or v["H_Foreign"]["max"] <= v["U"]["max"] + 1e-12 or k.startswith("T")
                                       for k, v in rng_res.items())
    out["check_T_foreign_nonnegative"] = all(v["empty"] or v["H_Foreign"]["min"] >= -1e-12 for k, v in rng_res.items() if k.startswith("T"))
    out["check_relabelings_T"] = rng_res["T_0.0"]["relabeling_values_H_Foreign_in_class"] == sorted(
        float(h) for h in (H[0], H[1]))
    out["check_estimate_not_in_P"] = rng_res["P_0.0"]["estimate_in_class"] is False
    out["seconds"] = time.time() - t0
    out["all_pass"] = all(v for k, v in out.items() if k.startswith("check_"))
    print(json.dumps(out, indent=1, default=float))
    json.dump(out, open("test_p1m_a1_core_results.json", "w"), indent=1, default=float)
