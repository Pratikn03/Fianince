"""Checks for Theorems thm:eqreduced and thm:fragility (inventory equilibrium of Theorem thm:inventory).

1. Reduced-form equivalence. Solve an equilibrium, simulate it, and compare its price path with the paper's reduced
   form x_t = a* x_{t-1} + k* (xi_t + sum_i ut_{i,t}), ut_{i,t+1} = r_i ut_{i,t} + wt_i x_t, where
   a* = abar/D, k* = kappa/D, wt_i = (D - abar) w_i/(D - r_i). Also compares the two impulse responses.
2. Realizability. Take the Gauss and Gauss-Radau K = 2 reduced-form pair of Theorem thm:kcohort, with common
   (a*, k*) and total weight W, build the two equilibrium economies with identical primitives, check that each solves
   the equilibrium system, and compare their impulse responses with the reduced-form ones.
3. Fragility. For one cohort, A*(w) = max over D in (max(abar, r), 1) of
   Psi(D) = kappa(D)(D - abar) D / (sF2 D^2 + kappa(D)^2 sX2), kappa(D) = (1 - D)(D - r)/w,
   against the bisection thresholds of e4_inventory_results.json; the bounds and the large-w limit.
"""
import json
import numpy as np
from e4_inventory import equilibria, transition

BASE = dict(A=0.2, sF2=1.0, sX2=0.25, abar=0.6)


def eq_impulse(kappa, D, abar, w, r, T=60):
    """Equilibrium price response to xi_0 = 1 from the zero state, by the state recursion of Theorem thm:inventory."""
    w, r = np.array(w, float), np.array(r, float)
    beta = kappa / (D - r)
    H, u = 0.0, np.zeros(len(w))          # u holds u_{i,t}
    out = []
    for t in range(T):
        xi = 1.0 if t == 0 else 0.0
        H = abar * H - u.sum() - xi
        x = (-kappa * H + np.dot(beta * r, u)) / D       # implicit form D x_t = -kappa H_t + sum beta_i r_i u_{i,t}
        u = r * u + w * x
        out.append(x)
    return np.array(out)


def rf_impulse(a, k, w, r, T=60):
    """Reduced-form response h_t = a h_{t-1} + k (xi_t + sum_i u_{i,t}), u_{i,t+1} = r_i u_{i,t} + w_i h_t."""
    w, r = np.array(w, float), np.array(r, float)
    u = np.zeros(len(w)); h = 0.0; out = []
    for t in range(T):
        xi = 1.0 if t == 0 else 0.0
        h = a * h + k * (xi + u.sum())
        u = r * u + w * h
        out.append(h)
    return np.array(out)


def simulate_paths(kappa, D, abar, w, r, T=5000, seed=3, sX2=0.25):
    w, r = np.array(w, float), np.array(r, float)
    beta = kappa / (D - r)
    rng = np.random.default_rng(seed)
    xis = np.sqrt(sX2) * rng.standard_normal(T)
    H, u = 0.0, np.zeros(len(w)); X = []
    for xi in xis:
        H = abar * H - u.sum() - xi
        x = (-kappa * H + np.dot(beta * r, u)) / D
        u = r * u + w * x; X.append(x)
    X = np.array(X)
    a, k, wt = abar / D, kappa / D, (D - abar) * w / (D - r)
    ut = np.zeros(len(w)); Y = []; h = 0.0
    for xi in xis:
        h = a * h + k * (xi + ut.sum())
        ut = r * ut + wt * h; Y.append(h)
    return float(np.max(np.abs(X - np.array(Y)))), float(np.max(np.abs(X)))


def main():
    A, sF2, sX2, abar = BASE["A"], BASE["sF2"], BASE["sX2"], BASE["abar"]
    res = {"base": BASE, "equivalence": [], "realizability": None, "fragility": None}
    sq3 = np.sqrt(3)
    for name, w, r in [("one cohort, positive", [0.02], [0.7]), ("one cohort, negative", [-0.2], [0.7]),
                       ("two cohorts", [0.005, 0.005], [0.5, 0.85]),
                       ("Gauss pair", [0.01, 0.01], [0.6 - 0.2 / sq3, 0.6 + 0.2 / sq3])]:
        e = equilibria(A, sF2, sX2, abar, w, r, kmax=60.0, n=30001)[0]
        kappa, D = e["kappa"], e["D"]
        wt = (D - abar) * np.array(w) / (D - np.array(r))
        gap_imp = float(np.max(np.abs(eq_impulse(kappa, D, abar, w, r) - rf_impulse(abar / D, kappa / D, wt, r))))
        gap_path, scale = simulate_paths(kappa, D, abar, w, r)
        res["equivalence"].append({"case": name, "kappa": kappa, "D": D, "a_star": abar / D, "k_star": kappa / D,
                                   "w_tilde": wt.tolist(), "max_impulse_gap": gap_imp, "max_path_gap": gap_path,
                                   "path_scale": scale})
        print(res["equivalence"][-1], flush=True)

    # 2. realizability of the K = 2 Gauss / Gauss-Radau pair (rates rc + d * nodes, total weight W)
    a_s, k_s, W, rc, d = 0.5, 0.5, 0.2, 0.6, 0.1   # Theorem kcohort stability index a + kW/(1 - rc - d) = 0.833 < 1
    pairs = {"Gauss": (np.array([0.5, 0.5]), np.array([-1 / sq3, 1 / sq3])),
             "Radau": (np.array([0.25, 0.75]), np.array([-1.0, 1 / 3]))}
    stab = a_s + k_s * W / (1 - rc - d)
    D = 1 - k_s * W / (1 - a_s)
    abar_r, kappa_r = a_s * D, k_s * D
    sF2_r, sX2_r = 1.0, 0.25
    V = sF2_r + k_s ** 2 * sX2_r
    A_r = k_s * D * (1 - a_s) / V
    rr = {"a_star": a_s, "k_star": k_s, "W": W, "stability_index": stab, "D": D, "abar": abar_r, "kappa": kappa_r,
          "A": A_r, "sF2": sF2_r, "sX2": sX2_r, "economies": {}}
    for nm, (qw, nodes) in pairs.items():
        r = rc + d * nodes; wt = W * qw
        w = wt * (D - r) / (D - abar_r)
        G = float(np.sum(w / (D - r)))
        res_D = D + kappa_r * G - 1
        Vd = sF2_r + kappa_r ** 2 * sX2_r / D ** 2
        res_k = kappa_r * (D - abar_r) - A_r * Vd * D
        M, b, _, _ = transition(kappa_r, D, abar_r, w.tolist(), r.tolist())
        rho = float(max(abs(np.linalg.eigvals(M))))
        he = eq_impulse(kappa_r, D, abar_r, w, r, T=80); hr = rf_impulse(a_s, k_s, wt, r, T=80)
        rr["economies"][nm] = {"rates": r.tolist(), "w_tilde": wt.tolist(), "w": w.tolist(), "D_equation_residual": res_D,
                               "kappa_equation_residual": res_k, "spectral_radius": rho,
                               "max_gap_eq_vs_reduced_form": float(np.max(np.abs(he - hr))), "impulse": he.tolist()}
    hA, hB = np.array(rr["economies"]["Gauss"]["impulse"]), np.array(rr["economies"]["Radau"]["impulse"])
    rr["impulse_l2_gap_between_pair"] = float(np.linalg.norm(hA - hB))
    # the gap scales as d^3: repeat for smaller spacings
    sc = []
    for dd in [0.1, 0.05, 0.025]:
        g = []
        for nm, (qw, nodes) in pairs.items():
            r = rc + dd * nodes; wt = W * qw; w = wt * (D - r) / (D - abar_r)
            g.append(eq_impulse(kappa_r, D, abar_r, w, r, T=400))
        sc.append({"d": dd, "l2_gap": float(np.linalg.norm(g[0] - g[1])), "ratio_to_d3": float(np.linalg.norm(g[0] - g[1]) / dd ** 3)})
    rr["gap_scaling"] = sc
    res["realizability"] = rr
    print({k: v for k, v in rr.items() if k != "economies"}, flush=True)
    for nm in rr["economies"]:
        print(nm, {k: v for k, v in rr["economies"][nm].items() if k != "impulse"}, flush=True)

    # 3. fragility threshold for one cohort
    def Astar(w, r=0.7, n=400001):
        m = max(abar, r)
        Ds = np.linspace(m + 1e-12, 1 - 1e-12, n)
        k = (1 - Ds) * (Ds - r) / w
        psi = k * (Ds - abar) * Ds / (sF2 * Ds ** 2 + k ** 2 * sX2)
        j = int(np.argmax(psi))
        return float(psi[j]), float(Ds[j]), float(k[j])

    r = 0.7; m = max(abar, r)
    Ds = np.linspace(m + 1e-12, 1 - 1e-12, 400001)
    Phi = float(np.max((1 - Ds) * (Ds - r) * (Ds - abar) / Ds))
    bis = {b["w"]: b["A_breakdown"] for b in json.load(open("e4_inventory_results.json"))["breakdown"]}
    rows = []
    for w in [0.0005, 0.005, 0.02, 0.05, 0.1, 0.2, 1.0, 10.0]:
        a, Dst, kst = Astar(w)
        rows.append({"w": w, "G1": w / (1 - r), "A_star": a, "D_at_max": Dst, "kappa_at_max": kst,
                     "bisection": bis.get(w), "bound_benchmark": (1 - abar) / (2 * np.sqrt(sF2 * sX2)),
                     "bound_feedback": Phi / (sF2 * w), "w_times_A_star": w * a})
        print(rows[-1], flush=True)
    res["fragility"] = {"r": r, "Phi_star": Phi, "limit_w_A_star": Phi / sF2, "rows": rows}
    json.dump(res, open("e4_reduced_form_results.json", "w"), indent=1)


if __name__ == "__main__":
    main()
