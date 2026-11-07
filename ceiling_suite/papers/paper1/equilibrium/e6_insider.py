"""E6: a strategic insider with short-lived information inside the inventory equilibrium (Theorem thm:insider).

Model (adds to e4_inventory.py): F_{t+1} = F_t + theta_t + eps_{t+1}; at t an insider privately observes
theta_t ~ N(0, sT2) (i.i.d.) and submits d_t, valued at F_{t+1} (Kyle convention). Unexpected flow nu_t = xi_t + d_t.
Cohorts trade on the observed deviation s_t = p_t - F_t: u_{i,t+1} = r_i u_{i,t} + w_i s_t. OLG CARA dealers as in E4,
Bayesian about theta_t from the flow.

Linear equilibrium: d_t = b theta_t; p_t = F_t + lam nu_t + x_t, x_t = -kappa H_t + sum_i beta_i u_{i,t+1}, with
  beta_i = kappa/(D - r_i),   D = 1 - kappa G(D),   kappa (D - abar) = A V D,
  sN2 = sX2 + b^2 sT2,   lam = b sT2 / sN2,   b = D / (2 (kappa + lam)),
  V = sE2 + sT2 sX2 / sN2 + ((kappa + lam)/D)^2 sN2.
Checks: (1) dealers' FOC residual and lam = Cov(theta, nu)/Var(nu) in simulation; (2) the insider's best response:
expected profit over a grid of b' with everything else fixed peaks at b; (3) observer's deviation s_t follows
s_t = a* s_{t-1} + kappa* sum ut_{i,t} + c0 nu_t - c1 nu_{t-1}, c0 = (kappa+lam)/D, c1 = abar lam / D (pathwise);
(4) the A -> 0 limit is Kyle's one-period lam = sT/(2 sX), b = sX/sT."""
import json
import numpy as np
from scipy.optimize import brentq

def G(D, w, r):
    return float(sum(wi / (D - ri) for wi, ri in zip(w, r)))

def kyle_given(kappa, D, sT2, sX2):
    """Solve lam, b given (kappa, D): b = D/(2(kappa+lam)), lam = b sT2/(sX2 + b^2 sT2)."""
    def f(lam):
        b = D / (2 * (kappa + lam)); return lam - b * sT2 / (sX2 + b * b * sT2)
    lam = brentq(f, 1e-12, 10 * np.sqrt(sT2 / sX2) + 10)
    return lam, D / (2 * (kappa + lam))

from e4_inventory import D_branch

def resid_D(kappa, D, A, sE2, sT2, sX2, abar, w, r):
    if not np.isfinite(D) or D <= 0 or (len(r) and D <= max(r)) or D <= abar:
        return np.nan, np.nan, np.nan, np.nan
    lam, b = kyle_given(kappa, D, sT2, sX2)
    sN2 = sX2 + b * b * sT2
    V = sE2 + sT2 * sX2 / sN2 + ((kappa + lam) / D) ** 2 * sN2
    return kappa * (D - abar) - A * V * D, lam, b, V

def solve(A, sE2, sT2, sX2, abar, w, r, kmax=5.0, n=4000):
    """Equilibria on the branch of D(kappa) continuous with D = 1 (as in e4_inventory)."""
    ks = np.linspace(1e-6, kmax, n); Ds = D_branch(ks, w, r)
    fs = np.array([resid_D(k, D, A, sE2, sT2, sX2, abar, w, r)[0] for k, D in zip(ks, Ds)])
    out = []
    for j in range(n - 1):
        if np.isfinite(fs[j]) and np.isfinite(fs[j + 1]) and np.sign(fs[j]) != np.sign(fs[j + 1]):
            a_, b_, Da, fa = ks[j], ks[j + 1], Ds[j], fs[j]
            for _ in range(100):
                m = 0.5 * (a_ + b_)
                Dm = D_branch(np.array([m]), w, r, Da)[0] if len(w) else 1.0
                fm = resid_D(m, Dm, A, sE2, sT2, sX2, abar, w, r)[0]
                if np.isfinite(fm) and np.sign(fm) == np.sign(fa): a_, Da, fa = m, Dm, fm
                else: b_ = m
            kk = 0.5 * (a_ + b_)
            D2 = D_branch(np.array([kk]), w, r, Da)[0] if len(w) else 1.0
            _, lam, b, V = resid_D(kk, D2, A, sE2, sT2, sX2, abar, w, r)
            out.append({"kappa": kk, "D": D2, "lam": lam, "b": b, "V": V, "total_impact": (kk + lam) / D2,
                        "insider_profit": b * sT2 / 2, "D_eq_residual": abs(D2 + kk * G(D2, w, r) - 1) if len(w) else 0.0})
    return out

def simulate(eq, A, sE2, sT2, sX2, abar, w, r, T=200000, seed=5, b_dev=None):
    kappa, D, lam, b = eq["kappa"], eq["D"], eq["lam"], eq["b"]
    w, r = np.array(w, float), np.array(r, float); beta = kappa / (D - r)
    bd = b if b_dev is None else b_dev
    rng = np.random.default_rng(seed)
    H, u = 0.0, np.zeros(len(w)); s_prev, x_prev, nu_prev = 0.0, 0.0, 0.0
    S, X, NU, TH, Hs, Us, FOC, PROF, RF = [], [], [], [], [], [], [], [], []
    for t in range(T):
        th = np.sqrt(sT2) * rng.standard_normal(); xi = np.sqrt(sX2) * rng.standard_normal()
        d = bd * th; nu = xi + d
        H = abar * H - u.sum() - nu
        x = (-kappa * H + np.dot(beta * r, u) + (1 - D) * lam * nu) / D     # implicit form, cohorts trade on s
        s = x + lam * nu
        un = r * u + w * s
        # dealers' FOC: E_t x_{t+1} with nu_{t+1} = 0
        Hn = abar * H - un.sum(); Ex = (-kappa * Hn + np.dot(beta * r, un)) / D
        FOC.append(Ex - x - A * eq["V"] * H)
        # insider profit (F_{t+1} - p_t) d with F_{t+1} - F_t = theta + eps; p_t - F_t = s
        PROF.append((th - s) * d)
        # observer reduced form residual
        if t > 0:
            ut = (D - abar) / (D - r) * u
            RF.append(s - (abar / D * s_prev + kappa / D * ut.sum() + (kappa + lam) / D * nu - abar * lam / D * nu_prev))
        S.append(s); NU.append(nu); TH.append(th)
        u = un; s_prev, nu_prev = s, nu
    NU, TH = np.array(NU), np.array(TH)
    return {"foc_rmse": float(np.sqrt(np.mean(np.square(FOC)))), "lam_regression": float(np.cov(TH, NU)[0, 1] / np.var(NU)),
            "mean_profit": float(np.mean(PROF)), "reduced_form_max_abs_resid": float(np.max(np.abs(RF))),
            "s_sd": float(np.std(S))}

def main():
    base = dict(A=0.05, sE2=1.0, sT2=0.25, sX2=0.25, abar=0.6)
    res = {"base": base, "cases": []}
    for name, w, r in [("no feedback", [], []), ("one cohort +0.02 at 0.7", [0.02], [0.7]),
                       ("one cohort -0.2 at 0.7", [-0.2], [0.7]), ("two cohorts", [0.005, 0.005], [0.5, 0.85]),
                       ("same merged measure, split", [0.0025, 0.0025, 0.005], [0.5, 0.5, 0.85])]:
        eqs = solve(base["A"], base["sE2"], base["sT2"], base["sX2"], base["abar"], w, r)
        rows = []
        for e in eqs[:1]:   # the low-impact equilibrium
            chk = simulate(e, **base, w=w, r=r)
            # insider deviation grid: expected profit at b' (dealers keep their rule)
            prof = {}
            for f in [0.6, 0.8, 1.0, 1.2, 1.4]:
                prof[f] = simulate(e, **base, w=w, r=r, T=60000, seed=9, b_dev=f * e["b"])["mean_profit"]
            # analytic expected profit at b' = (b' sT2) - (kappa+lam)/D b'^2 sT2
            c = (e["kappa"] + e["lam"]) / e["D"]
            prof_an = {f: f * e["b"] * base["sT2"] - c * (f * e["b"]) ** 2 * base["sT2"] for f in prof}
            e.update(chk); e["profit_by_b_factor_sim"] = prof; e["profit_by_b_factor_analytic"] = prof_an
            rows.append(e)
        res["cases"].append({"name": name, "w": w, "r": r, "equilibria": rows, "n_equilibria_found": len(eqs)})
        print(name, json.dumps(rows, default=float)[:700], flush=True)
    # Kyle limit A -> 0
    lim = []
    for A in [0.05, 0.01, 0.001]:
        e = solve(A, 1.0, 0.25, 0.25, 0.6, [0.02], [0.7])
        if e: lim.append({"A": A, "kappa": e[0]["kappa"], "lam": e[0]["lam"], "b": e[0]["b"], "D": e[0]["D"]})
    res["kyle_limit"] = {"rows": lim, "kyle_lam": 0.5 * np.sqrt(0.25 / 0.25), "kyle_b": np.sqrt(0.25 / 0.25)}
    print("kyle limit", lim)
    json.dump(res, open("e6_insider_results.json", "w"), indent=1, default=float)

if __name__ == "__main__":
    main()
