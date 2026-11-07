"""Numerical illustration of Theorem thm:eqinv (E1).

Two cohort configurations with equal kernels k_0, k_1, k_2 (Gauss vs Radau two-point rules on rates c + d s):
  Gauss: weights (1/2, 1/2), nodes s = -/+ 1/sqrt(3)
  Radau: weights (1/4, 3/4), nodes s = -1, 1/3
The market: insider x_t = beta (v - p_{t-1}); noise z_t; a dealer with inventory aversion,
p_t = p_{t-1} + lam * y_t - gam * (I_t - I_{t-1}) with I_t = -sum y (a causal linear rule; any rule would do);
public signal s_t = p_t - p_{t-1}; total flow y_t = x_t + z_t + W * sum_i w_i m_{i,t}.
Same (v, z) draws in both economies. Output: max |price gap| by date, and the largest group's position in each.
"""
import json
import numpy as np

def run(weights, nodes, c, d, T, v, z, beta=0.3, lam=0.3, gam=0.05, W=0.5):
    r = c + d * np.asarray(nodes); w = W * np.asarray(weights)
    m = np.zeros(len(w)); p = [0.0]; I = 0.0; groups = []
    for t in range(T):
        f = float(w @ m)
        x = beta * (v - p[-1])
        y = x + z[t] + f
        I_new = I - y
        p_new = p[-1] + lam * y - gam * (I_new - I)
        s = p_new - p[-1]
        groups.append((w * m).tolist())
        m = r * m + s              # memory update on the new price change
        p.append(p_new); I = I_new
    return np.array(p[1:]), np.array(groups)

def main():
    rng = np.random.default_rng(20261107)
    T, c, d = 40, 0.6, 0.2
    out = {"T": T, "c": c, "d": d, "paths": []}
    for rep in range(200):
        v = rng.standard_normal(); z = 0.5 * rng.standard_normal(T)
        pG, gG = run([0.5, 0.5], [-1/np.sqrt(3), 1/np.sqrt(3)], c, d, T, v, z)
        pR, gR = run([0.25, 0.75], [-1.0, 1/3], c, d, T, v, z)
        out["paths"].append({"gap": np.abs(pG - pR).tolist(),
                             "largest_share_G": float(np.max(np.abs(gG[-1])) / max(np.sum(np.abs(gG[-1])), 1e-12)),
                             "largest_share_R": float(np.max(np.abs(gR[-1])) / max(np.sum(np.abs(gR[-1])), 1e-12))})
    gaps = np.array([q["gap"] for q in out["paths"]])
    out["max_gap_by_date"] = gaps.max(0).tolist()
    out["kernel"] = {"k3_gap_predicted": 2 * d ** 3 / 9 * 0.5}
    json.dump(out, open("e1_demo_results.json", "w"), indent=1)
    for t, g in enumerate(out["max_gap_by_date"], 1):
        print(f"date {t:2d}: max |p_G - p_R| = {g:.3e}")
    print("median largest-group share G, R:",
          np.median([q["largest_share_G"] for q in out["paths"]]), np.median([q["largest_share_R"] for q in out["paths"]]))

if __name__ == "__main__":
    main()
