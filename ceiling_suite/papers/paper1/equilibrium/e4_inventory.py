"""E4: equilibrium price impact with inventory-averse dealers and exponential-memory feedback cohorts.

Model (stationary, OLG CARA dealers):
  fundamental F_t random walk, innovation var sF2; price p_t = F_t + x_t
  cohorts: u_{i,t+1} = r_i u_{i,t} + w_i x_t   (trade at t+1 on the price error at t)
  customer flow y_t = sum_i u_{i,t} + xi_t,  xi_t ~ N(0, sX2)
  dealer inventory H_t = abar H_{t-1} - y_t   (a share 1 - abar is laid off each period)
  dealer optimality: H_t = (E_t x_{t+1} - x_t) / (A V),  V = sF2 + Var_t(x_{t+1})
Linear equilibrium x_t = -kappa H_t + sum_i beta_i u_{i,t+1} gives
  beta_i = kappa/(D - r_i),  D = 1 - kappa G(D),  G(D) = sum_i w_i/(D - r_i),
  kappa = A V D/(D - abar),   V = sF2 + kappa^2 sX2 / D^2.
"""
import json
import numpy as np

def G(D, w, r):
    return float(sum(wi / (D - ri) for wi, ri in zip(w, r)))

def dG(D, w, r):
    return float(-sum(wi / (D - ri) ** 2 for wi, ri in zip(w, r)))

def D_branch(ks, w, r, D0=1.0):
    """Regular branch D(kappa) of D + kappa G(D) = 1, continued from D = 1 at kappa = 0 by Newton steps.
    Returns nan once the branch folds (1 + kappa G'(D) = 0) or leaves (max r, inf)."""
    out = np.full(len(ks), np.nan)
    if len(w) == 0:
        out[:] = 1.0; return out
    rmax = max(r); D = D0
    for j, k in enumerate(ks):
        ok = False
        for _ in range(60):
            f = D + k * G(D, w, r) - 1; fp = 1 + k * dG(D, w, r)
            if fp <= 1e-10: break
            Dn = D - f / fp
            if Dn <= rmax: Dn = 0.5 * (D + rmax)
            if abs(Dn - D) < 1e-14: D = Dn; ok = True; break
            D = Dn
        if not ok or 1 + k * dG(D, w, r) <= 1e-10:
            break
        out[j] = D
    return out

def equilibria(A, sF2, sX2, abar, w, r, kmax=20.0, n=20001):
    """All fixed points of kappa (D - abar) = A V D on the regular D branch, kappa in (0, kmax)."""
    ks = np.linspace(1e-9, kmax, n)
    Ds = D_branch(ks, w, r)
    def resid_at(k, D):
        V = sF2 + k * k * sX2 / D ** 2
        return k * (D - abar) - A * V * D
    f = np.array([resid_at(k, D) if np.isfinite(D) and D > abar else np.nan for k, D in zip(ks, Ds)])
    out = []
    for j in range(len(ks) - 1):
        if np.isfinite(f[j]) and np.isfinite(f[j + 1]) and (f[j] > 0) != (f[j + 1] > 0):
            a, b = ks[j], ks[j + 1]; Da = Ds[j]
            for _ in range(60):
                m = 0.5 * (a + b); Dm = D_branch(np.array([m]), w, r, Da)[0] if len(w) else 1.0
                # continuation from a to m is a short step from a known branch point
                if (resid_at(m, Dm) > 0) == (resid_at(a, Da) > 0): a, Da = m, Dm
                else: b = m
            kk = 0.5 * (a + b); fD = Da if len(w) else 1.0
            # polish D at kk
            if len(w):
                for _ in range(50):
                    fD -= (fD + kk * G(fD, w, r) - 1) / (1 + kk * dG(fD, w, r))
            out.append({"kappa": kk, "D": fD, "V": sF2 + kk * kk * sX2 / fD ** 2, "impact_of_flow_shock": kk / fD,
                        "eq_residual": abs(resid_at(kk, fD)), "D_residual": abs(fD + kk * G(fD, w, r) - 1) if len(w) else 0.0})
    return out

def transition(kappa, D, abar, w, r):
    """State s_t = (H_t, u_{1,t+1},...,u_{K,t+1}). Returns M with s_t = M s_{t-1} + b xi_t, and the x-loading."""
    K = len(w); beta = np.array([kappa / (D - ri) for ri in r])
    # x_t = (-kappa H_t + sum_i beta_i r_i u_{i,t}) / D ;  H_t = abar H_{t-1} - sum u_{i,t} - xi_t ; u_{i,t+1} = r_i u_{i,t} + w_i x_t
    n = 1 + K; M = np.zeros((n, n)); b = np.zeros(n)
    # H_t
    M[0, 0] = abar; M[0, 1:] = -1.0; b[0] = -1.0
    # x_t as row
    xrow = (-kappa * M[0] + np.concatenate([[0.0], beta * np.array(r)])) / D
    xb = (-kappa * b[0]) / D
    for i in range(K):
        M[1 + i] = w[i] * xrow; M[1 + i, 1 + i] += r[i]; b[1 + i] = w[i] * xb
    return M, b, xrow, xb

def simulate_check(A, sF2, sX2, abar, w, r, eq, T=200000, seed=1):
    kappa, D, V = eq["kappa"], eq["D"], eq["V"]
    M, b, xrow, xb = transition(kappa, D, abar, w, r)
    rho = max(abs(np.linalg.eigvals(M))) if M.size else 0.0
    # recompute x_t and H_t exactly
    rng = np.random.default_rng(seed); s = np.zeros(len(b)); X = np.zeros(T); H = np.zeros(T); St = np.zeros((T, len(b)))
    beta = np.array([kappa / (D - ri) for ri in r])
    for t in range(T):
        xi = np.sqrt(sX2) * rng.standard_normal()
        Hn = abar * s[0] - (s[1:].sum() if len(r) else 0.0) - xi
        x = (-kappa * Hn + float(np.dot(beta * np.array(r), s[1:])) if len(r) else -kappa * Hn) / D if len(r) else -kappa * Hn
        un = np.array(r) * s[1:] + np.array(w) * x if len(r) else np.zeros(0)
        s = np.concatenate([[Hn], un]); X[t] = x; H[t] = Hn; St[t] = s
    # exact E_t x_{t+1}: next period with xi_{t+1} = 0
    st = St[1000:-1]; Hs = st[:, 0]; us = st[:, 1:]
    Hn = abar * Hs - (us.sum(1) if len(r) else 0.0)
    if len(r):
        Ex = (-kappa * Hn + (us * (beta * np.array(r))).sum(1)) / D
    else:
        Ex = -kappa * Hn
    foc_resid = H[1000:-1] * A * V - (Ex - X[1000:-1])
    innov_var = float(np.var(X[1001:] - Ex))
    return {"spectral_radius": float(rho), "foc_rel_error": float(np.sqrt(np.mean(foc_resid ** 2)) / np.sqrt(np.mean((H[1000:-1] * A * V) ** 2))),
            "innovation_var_sim": innov_var, "innovation_var_theory": kappa ** 2 * sX2 / D ** 2}

def main():
    base = dict(A=0.2, sF2=1.0, sX2=0.25, abar=0.6)
    res = {"base": base, "cases": []}
    sq3 = np.sqrt(3)
    for name, w, r in [("no feedback", [], []),
                       ("one cohort, positive feedback, total weight 0.2", [0.2], [0.7]),
                       ("two cohorts, total weight 0.2", [0.1, 0.1], [0.5, 0.85]),
                       ("one cohort, negative feedback", [-0.2], [0.7]),
                       ("one cohort, positive feedback", [0.02], [0.7]),
                       ("two cohorts", [0.005, 0.005], [0.5, 0.85]),
                       ("same merged measure, split", [0.0025, 0.0025, 0.005], [0.5, 0.5, 0.85]),
                       ("Gauss pair", [0.01, 0.01], [0.6 - 0.2 / sq3, 0.6 + 0.2 / sq3]),
                       ("Radau pair", [0.005, 0.015], [0.4, 0.6 + 0.2 / 3])]:
        eqs = equilibria(base["A"], base["sF2"], base["sX2"], base["abar"], w, r, kmax=60.0, n=30001)
        rows = []
        for e in eqs:
            e.update(simulate_check(base["A"], base["sF2"], base["sX2"], base["abar"], w, r, e))
            rows.append(e)
        res["cases"].append({"name": name, "w": w, "r": r, "equilibria": rows})
        print(name, json.dumps(rows, indent=None)[:600])
    # benchmark closed form
    A, sF2, sX2, abar = base["A"], base["sF2"], base["sX2"], base["abar"]
    disc = (1 - abar) ** 2 - 4 * A * A * sX2 * sF2
    res["benchmark_closed_form"] = {"disc": disc, "kappa_low": ((1 - abar) - np.sqrt(disc)) / (2 * A * sX2) if disc >= 0 else None,
                                    "kappa_high": ((1 - abar) + np.sqrt(disc)) / (2 * A * sX2) if disc >= 0 else None}
    print("benchmark", res["benchmark_closed_form"])
    # breakdown boundary in A for one positive-feedback cohort
    # breakdown boundary in A for one positive-feedback cohort at r = 0.7. For w > 0, every equilibrium with
    # positive impact and D > 0 has D in (max(abar, r), 1) and kappa = (1 - D)(D - r)/w, so a scan over D finds
    # all of them, on both branches.
    def one_cohort_all(A_, w1, r1=0.7, n=200001):
        if w1 == 0:
            disc_ = (1 - abar) ** 2 - 4 * A_ * A_ * sF2 * sX2
            return 0 if disc_ < 0 else 2
        Ds = np.linspace(max(abar, r1) + 1e-12, 1 - 1e-12, n); k = (1 - Ds) * (Ds - r1) / w1
        f = k * (Ds - abar) - A_ * (sF2 * Ds + k * k * sX2 / Ds)
        return int(np.sum(np.sign(f[:-1]) != np.sign(f[1:])))
    bd = []
    for w1 in [0.0, 0.02, 0.05, 0.1, 0.2]:
        lo, hi = 0.002, 1.0
        assert one_cohort_all(lo, w1) > 0 and one_cohort_all(hi, w1) == 0
        for _ in range(40):
            m = 0.5 * (lo + hi)
            if one_cohort_all(m, w1) > 0: lo = m
            else: hi = m
        bd.append({"w": w1, "r": 0.7, "G1": w1 / 0.3, "A_breakdown": 0.5 * (lo + hi),
                   "A_breakdown_closed_form_no_feedback": (1 - abar) / (2 * np.sqrt(sF2 * sX2)) if not w1 else None})
        print("breakdown", bd[-1])
    res["breakdown"] = bd
    # first-order formula for one small positive-feedback cohort
    k0 = res["benchmark_closed_form"]["kappa_low"]; sq = np.sqrt(disc); fo = []
    for w1 in [0.005, 0.01, 0.02]:
        e = equilibria(A, sF2, sX2, abar, [w1], [0.7])
        if e:
            G1 = w1 / (1 - 0.7)
            fo.append({"w": w1, "kappa": e[0]["kappa"], "kappa_first_order": k0 + k0 ** 2 * (abar + 2 * A * k0 * sX2) * G1 / sq,
                       "D": e[0]["D"], "D_first_order": 1 - k0 * G1})
            print("first-order", fo[-1])
    res["first_order"] = fo
    json.dump(res, open("e4_inventory_results.json", "w"), indent=1)

if __name__ == "__main__":
    main()
