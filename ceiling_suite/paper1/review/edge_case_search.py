"""Counterexample search at the edges of Paper 1's statements (internal adversarial review, 30 Oct).
Random positive and signed economies, a in [0, 0.95], eta in (0, 1], K up to 5. Writes edge_case_search.json."""
import json
import numpy as np

rng = np.random.default_rng(7)
w_grid = np.exp(1j * np.linspace(-np.pi, np.pi, 2049))

def H(a, k, q, eta, z):
    G = sum(qi * ei * z / (z - (1 - ei)) for qi, ei in zip(q, eta))
    return k * z / (z - a - k * G)

def resp(a, k, q, eta, T=400):
    x = np.zeros(T); y = np.zeros(len(q))
    for t in range(T):
        x[t] = a * (x[t - 1] if t else 0) + k * np.dot(q, y) + (k if t == 0 else 0)
        y = (1 - eta) * y + eta * x[t]
    return x

res = {"positive": {"n": 0, "neg_response": 0, "nonmonotone": 0, "ReH_below_k2": 0, "max_h_ne_kappa": 0},
       "signed": {"n": 0, "zero_outside_disk": 0}, "a_zero": {"n": 0, "ReH_below_k2": 0},
       "kcohort_order": {}}
for trial in range(3000):
    K = int(rng.integers(1, 6)); a = rng.uniform(0, 0.95); k = rng.uniform(0.1, 2)
    eta = rng.uniform(0.01, 1.0, K); q = rng.uniform(0, 1, K)
    S = a + k * q.sum()
    if S >= 0.98:
        q *= (0.97 - a) / (k * q.sum()) if 0.97 > a else 0
    if q.sum() == 0:
        continue
    h = resp(a, k, q, eta)
    r = res["positive"]; r["n"] += 1
    r["neg_response"] += int(h.min() < -1e-12)
    r["nonmonotone"] += int(np.any(np.diff(h) > 1e-12))
    r["max_h_ne_kappa"] += int(abs(h.max() - k) > 1e-9)
    r["ReH_below_k2"] += int(np.min(H(a, k, q, eta, w_grid).real) < k / 2 - 1e-9)
    # a = 0 version
    h0 = H(0.0, k, q * min(1, 0.97 / max(k * q.sum(), 1e-9)), eta, w_grid)
    res["a_zero"]["n"] += 1; res["a_zero"]["ReH_below_k2"] += int(np.min(h0.real) < k / 2 - 1e-9)
    # signed weights, stable: zeros of H are the memory rates (inside the disk)
    qs = rng.uniform(-0.5, 0.5, K)
    rows = np.zeros((K + 1, K + 1))
    rows[0, 0] = a; rows[0, 1:] = k * qs
    for i in range(K):
        rows[i + 1, 0] = eta[i] * a; rows[i + 1, 1:] = eta[i] * k * qs; rows[i + 1, i + 1] += 1 - eta[i]
    if np.max(np.abs(np.linalg.eigvals(rows))) < 0.99:
        res["signed"]["n"] += 1
        res["signed"]["zero_outside_disk"] += int(np.any(np.abs(1 - eta) >= 1))
# K-cohort order: Gauss vs Gauss-Radau responses, slope of ||dh|| in spacing
from numpy.polynomial.legendre import leggauss
def radau(K):
    # Gauss-Radau nodes on [-1,1] with fixed node -1 (uniform weight), weights by moment fitting
    from numpy.polynomial import legendre as L
    c = np.zeros(K + 1); c[K - 1] = 1; c[K] = 1
    pts = np.sort(np.real(L.legroots(L.legder(L.Legendre(c).coef) * 0 + L.legsub(L.Legendre.basis(K - 1).coef, -L.Legendre.basis(K).coef)))) if False else None
    nodes = np.r_[-1.0, np.sort(np.real(np.roots(np.polyder(np.polynomial.legendre.leg2poly(np.r_[np.zeros(K - 1), 1, 1])[::-1]))))[:K - 1]] if False else None
    return None
for K in (2, 3, 4, 5):
    xs, ws = leggauss(K); ws = ws / ws.sum()
    # Gauss-Radau: roots of (P_{K-1}+P_K)/(1+x)
    c = np.zeros(K + 1); c[K - 1] = 1; c[K] = 1
    roots = np.sort(np.real(np.polynomial.legendre.legroots(c)))
    V = np.vander(roots, K, increasing=True).T
    mom = np.array([((1 - (-1) ** (m + 1)) / (m + 1)) / 2 for m in range(K)])
    wr = np.linalg.solve(V, mom)
    sl = []
    ds = np.array([0.02, 0.03, 0.05, 0.08])
    for d in ds:
        rA = 0.7 + d * xs; rB = 0.7 + d * roots
        hA = resp(0.5, 1.0, 0.1 * ws / (1 - rA), 1 - rA, 600); hB = resp(0.5, 1.0, 0.1 * wr / (1 - rB), 1 - rB, 600)
        sl.append(np.linalg.norm(hA - hB))
    res["kcohort_order"][K] = {"slope": float(np.polyfit(np.log(ds), np.log(sl), 1)[0]), "theory": 2 * K - 1,
                               "radau_weights_positive": bool(np.all(wr > 0)), "radau_has_minus1": bool(abs(roots[0] + 1) < 1e-9)}
json.dump(res, open(__file__.replace(".py", ".json"), "w"), indent=1)
print(json.dumps(res, indent=1))
