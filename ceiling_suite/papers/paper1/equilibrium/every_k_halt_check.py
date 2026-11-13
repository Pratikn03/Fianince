"""Numerical check of the every-K targeted-halt lemma (Supplement, 'The targeted halt for every K').

Claims checked for K = 2..14, uniform probability measure on [-1, 1], orthonormal Legendre p_j:
  L1  A K-node rule exact to degree 2K-2 has weights lambda_K(node), lambda_K(s) = 1 / sum_{j<K} p_j(s)^2.
      Checked for the rules with node polynomial p_K - c p_{K-1}, c on a grid of [c_-, c_+] (c = 0 is Gauss,
      c = c_- and c_+ are the two Gauss-Radau rules).
  L2  These rules have K real nodes in [-1, 1], positive weights, and integrate s^m exactly for m <= 2K-2.
  L3  Two different rules of the family differ at degree 2K-1.
  L4  The largest weight M(c) = max_i lambda_K(node_i(c)) is not constant in c.
This is a numerical check, not a proof. Writes every_k_halt_check_results.json.
"""
import json
import numpy as np
from numpy.polynomial import legendre as L
from numpy.polynomial import polynomial as Pm


def p_coef(j):
    """Monomial coefficients of the orthonormal Legendre polynomial of degree j (uniform probability on [-1,1])."""
    c = np.zeros(j + 1); c[j] = 1.0
    return L.leg2poly(c) * np.sqrt(2 * j + 1.0)


def lam(K, s):
    return 1.0 / sum(Pm.polyval(s, p_coef(j)) ** 2 for j in range(K))


def rule(K, c):
    q = Pm.polysub(p_coef(K), c * p_coef(K - 1))
    nodes = np.sort(np.roots(q[::-1]))
    assert np.max(np.abs(nodes.imag)) < 1e-9, "complex node"
    nodes = nodes.real
    V = np.vander(nodes, K, increasing=True).T                     # interpolatory weights from moments 0..K-1
    mom = np.array([0.0 if m % 2 else 1.0 / (m + 1) for m in range(K)])
    return nodes, np.linalg.solve(V, mom)


def moment(m):
    return 0.0 if m % 2 else 1.0 / (m + 1)


rows = []
for K in range(2, 15):
    c_plus = np.sqrt((2 * K + 1.0) / (2 * K - 1.0))                # p_K(1) / p_{K-1}(1)
    grid = np.linspace(-c_plus, c_plus, 41)
    M, worst_l1, worst_exact, min_w, max_abs_node = [], 0.0, 0.0, 1.0, 0.0
    top = {}
    for c in grid:
        x, w = rule(K, c)
        worst_l1 = max(worst_l1, float(np.max(np.abs(w - lam(K, x)))))
        worst_exact = max(worst_exact, max(abs(float(w @ x ** m) - moment(m)) for m in range(2 * K - 1)))
        min_w = min(min_w, float(w.min())); max_abs_node = max(max_abs_node, float(np.max(np.abs(x))))
        M.append(float(w.max())); top[float(c)] = float(w @ x ** (2 * K - 1))
    xg, wg = rule(K, 0.0); xr, wr = rule(K, -c_plus)
    rows.append({"K": K, "c_plus": float(c_plus), "max_weight_gauss": float(wg.max()), "max_weight_radau": float(wr.max()),
                 "M_min_over_family": min(M), "M_max_over_family": max(M), "M_range": max(M) - min(M),
                 "L1_max_abs_weight_minus_lambda": worst_l1, "L2_max_exactness_error": worst_exact,
                 "L2_min_weight": min_w, "L2_max_abs_node": max_abs_node,
                 "L3_degree_2K-1_gap_gauss_vs_radau": float(wg @ xg ** (2 * K - 1) - wr @ xr ** (2 * K - 1)),
                 "radau_left_node": float(xr.min())})
ok = {"L1": all(r["L1_max_abs_weight_minus_lambda"] < 1e-7 for r in rows),
      "L2": all(r["L2_max_exactness_error"] < 1e-7 and r["L2_min_weight"] > 0 and r["L2_max_abs_node"] < 1 + 1e-7 for r in rows),
      "L3": all(abs(r["L3_degree_2K-1_gap_gauss_vs_radau"]) > 1e-9 for r in rows),
      "L4": all(r["M_range"] > 1e-6 for r in rows)}
json.dump({"checks": ok, "rows": rows}, open("every_k_halt_check_results.json", "w"), indent=1)
print(ok)
for r in rows:
    print(r["K"], "Gauss max %.6f  Radau max %.6f  family range of max weight [%.6f, %.6f]  |w-lambda| %.1e  exact %.1e" % (
        r["max_weight_gauss"], r["max_weight_radau"], r["M_min_over_family"], r["M_max_over_family"],
        r["L1_max_abs_weight_minus_lambda"], r["L2_max_exactness_error"]))
