"""Phase 4-7 internal checks for Paper 1 (exact equivalence, near equivalence, resolvent identity, d2 identity,
experiment-energy bound). Writes phase7_checks.json. Deterministic; no data."""
import json
import numpy as np


def response(a, kappa, cohorts, T=200):
    """Impulse response of x_t = a x_{t-1} + kappa*sum q_i y_{i,t-1} + kappa v_t, y_i,t = (1-eta_i) y + eta_i x_t."""
    x = np.zeros(T); y = np.zeros(len(cohorts))
    for t in range(T):
        v = 1.0 if t == 0 else 0.0
        xp = x[t - 1] if t else 0.0
        x[t] = a * xp + kappa * sum(q * yi for (q, _), yi in zip(cohorts, y)) + kappa * v
        y = np.array([(1 - eta) * yi + eta * x[t] for (_, eta), yi in zip(cohorts, y)])
    return x


a, k = 0.5, 0.8
out = {}
A = [(0.2, 0.4)]
B = [(0.05, 0.4), (0.07, 0.4), (0.08, 0.4)]            # same rate, same merged weight
C = [(0.3, 0.4), (-0.1, 0.4)]                          # signed weights, same merged weight
D = [(0.1, 0.35), (0.1, 0.45)]                         # different merged measure (rates 0.6+-0.05)
hA, hB, hC, hD = (response(a, k, e) for e in (A, B, C, D))
out["exact_equivalence_max_abs_diff_AB"] = float(np.max(np.abs(hA - hB)))
out["exact_equivalence_max_abs_diff_AC"] = float(np.max(np.abs(hA - hC)))
out["different_M_l2_diff_AD"] = float(np.linalg.norm(hA - hD))
out["d2_identity"] = {"computed": float(hD[2] - hA[2]), "formula_-kappa^2 q delta^2": -k**2 * 0.2 * 0.05**2}
# near equivalence: response difference scales as delta^2
ds = [0.01, 0.02, 0.04, 0.08]
diffs = [np.linalg.norm(response(a, k, [(0.1, 0.4 - d), (0.1, 0.4 + d)]) - hA) for d in ds]
out["near_equivalence_slope_in_delta"] = float(np.polyfit(np.log(ds), np.log(diffs), 1)[0])
# resolvent identity with the z^{-1} factor
z = np.exp(1j * 0.7)
def H(coh):
    G = sum(q * eta * z / (z - (1 - eta)) for q, eta in coh)
    return k * z / (z - a - k * G), G
(H1, G1), (H0, G0) = H(D), H(A)
out["resolvent_identity_error_with_zinv"] = float(abs((H1 - H0) - H1 * H0 * (G1 - G0) / z))
out["resolvent_identity_error_without_zinv"] = float(abs((H1 - H0) - H1 * H0 * (G1 - G0)))
# experiment energy: ||Dh * v|| <= sup|dH| ||v|| for random probes
rng = np.random.default_rng(0)
w = np.linspace(-np.pi, np.pi, 4001); zz = np.exp(1j * w)
def Hw(coh):
    G = sum(q * eta * zz / (zz - (1 - eta)) for q, eta in coh)
    return k * zz / (zz - a - k * G)
sup = float(np.max(np.abs(Hw(D) - Hw(A))))
worst = 0.0
for _ in range(200):
    v = rng.normal(size=30)
    dm = np.convolve(hD - hA, v)[:230]
    worst = max(worst, np.linalg.norm(dm) / (sup * np.linalg.norm(v)))
out["energy_bound_max_ratio_(<=1)"] = worst
json.dump(out, open(__file__.replace(".py", ".json"), "w"), indent=1)
print(json.dumps(out, indent=1))
