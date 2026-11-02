"""Step-by-step numerical checks of the proof of Proposition prop:tagged (Paper 1, Appendix).

Each function checks one numbered step of review/proof_checks/prop_tagged_steps.md against random parameters or a
long simulation. A check passing is evidence, not proof. Run: python check_prop_tagged.py  (about 1 minute).
"""
import json, os
import numpy as np

rng = np.random.default_rng(1)
out = {}


def random_economy(K=2):
    a = rng.uniform(0.1, 0.6)
    kappa = rng.uniform(0.5, 1.0)
    eta = rng.uniform(0.1, 0.9, K)
    q = rng.uniform(0.05, 0.4, K)
    if a + kappa * q.sum() >= 0.95:                       # keep the economy stable (S < 1)
        q = q * (0.9 - a) / (kappa * q.sum())
    return a, kappa, eta, q


def simulate(a, kappa, eta, q, T, sig_xi=1.0, sig_f=0.3):
    K = len(eta); x = np.zeros(T); y = np.zeros((K, T)); xi = sig_xi * rng.standard_normal(T)
    for t in range(1, T):
        x[t] = a * x[t - 1] + kappa * np.dot(q, y[:, t - 1]) + xi[t]
        y[:, t] = (1 - eta) * y[:, t - 1] + eta * x[t]
    u = q[:, None] * y
    eps = sig_f * rng.standard_normal((K, T))
    return x, u, u + eps, eps


# Step 1: u_{i,t} = r_i u_{i,t-1} + w_i x_t exactly (w_i = q_i eta_i, r_i = 1 - eta_i)
a, kappa, eta, q = random_economy()
x, u, ut, eps = simulate(a, kappa, eta, q, 20000)
r, w = 1 - eta, q * eta
res1 = np.max(np.abs(u[:, 1:] - (r[:, None] * u[:, :-1] + w[:, None] * x[None, 1:])))
out["S1_recursion_max_residual"] = float(res1)

# Step 2: noisy flow satisfies ut_t = r ut_{t-1} + w x_t + e_t with e_t = eps_t - r eps_{t-1}
e = eps[:, 1:] - r[:, None] * eps[:, :-1]
res2 = np.max(np.abs(ut[:, 1:] - (r[:, None] * ut[:, :-1] + w[:, None] * x[None, 1:] + e)))
out["S2_noisy_recursion_max_residual"] = float(res2)

# Steps 5-8: Sigma_i from simulation vs the closed forms A_0, A_1 and the determinant formula
a, kappa, eta, q = random_economy()
T = 400000
x, u, ut, eps = simulate(a, kappa, eta, q, T)
burn = 2000
x, ut = x[burn:], ut[:, burn:]
r, w = 1 - eta, q * eta
lags = 400
gam = np.array([np.mean(x[s:] * x[:len(x) - s]) for s in range(lags + 2)])
rows = []
for i in range(len(eta)):
    Sig_emp = np.array([[np.mean(x[:-1] * ut[i, :-1]), np.mean(x[:-1] * x[1:])],
                        [np.mean(x[1:] * ut[i, :-1]), np.mean(x[1:] * x[1:])]])
    A0 = sum(r[i] ** s * gam[s] for s in range(lags))
    A1 = sum(r[i] ** s * gam[s + 1] for s in range(lags))
    Sig_form = np.array([[w[i] * A0, gam[1]], [w[i] * A1, gam[0]]])
    rows.append({"Sigma_empirical": Sig_emp.tolist(), "Sigma_formula": Sig_form.tolist(),
                 "max_rel_error": float(np.max(np.abs(Sig_emp - Sig_form)) / np.max(np.abs(Sig_form))),
                 "det_empirical": float(np.linalg.det(Sig_emp)), "det_formula": float(np.linalg.det(Sig_form)),
                 "det_step7": float(w[i] * (gam[0] * A0 - gam[1] * A1))})
out["S5_S7_Sigma_check"] = rows

# Step 8: gamma0*A0 - gamma1*A1 = sum_{l,m} c_l c_m (1 - lam_l lam_m)/(1 - r lam_m) for nonnegative mixtures
worst8 = 0.0
for _ in range(20000):
    L = rng.integers(1, 5)
    c = rng.uniform(0, 1, L); lam = rng.uniform(0, 0.99, L); rr = rng.uniform(0, 0.99)
    g0, g1 = c.sum(), (c * lam).sum()
    A0 = (c / (1 - rr * lam)).sum(); A1 = (c * lam / (1 - rr * lam)).sum()
    lhs = g0 * A0 - g1 * A1
    rhs = sum(c[l] * c[m] * (1 - lam[l] * lam[m]) / (1 - rr * lam[m]) for l in range(L) for m in range(L))
    worst8 = max(worst8, abs(lhs - rhs) / max(1e-12, abs(rhs)))
out["S8_identity_worst_rel_error_20000_draws"] = worst8

# Step 12: lower bound det/w >= (1 - lam_bar^2) gamma0^2 for lam_l <= lam_bar, r in [0,1)
viol12 = 0
for _ in range(20000):
    L = rng.integers(1, 5)
    c = rng.uniform(0, 1, L); lam_bar = rng.uniform(0.1, 0.99); lam = rng.uniform(0, lam_bar, L)
    rr = rng.uniform(0, 0.99)
    val = sum(c[l] * c[m] * (1 - lam[l] * lam[m]) / (1 - rr * lam[m]) for l in range(L) for m in range(L))
    viol12 += val < (1 - lam_bar ** 2) * c.sum() ** 2 - 1e-12
out["S12_lower_bound_violations_20000_draws"] = int(viol12)

# Step 10: E[m m^T] = sigma_f^2 [(1+r^2) Gamma0 - r (Gamma1 + Gamma1^T)], m_t = (Z_t - r Z_{t+1}) eps_t
a, kappa, eta, q = random_economy()
sig_f = 0.3
x, u, ut, eps = simulate(a, kappa, eta, q, 300000, sig_f=sig_f)
x, eps = x[burn:], eps[:, burn:]
i = 0; ri = 1 - eta[i]
Z = np.vstack([x[:-2], x[1:-1]])            # Z_t = (x_{t-1}, x_t) for t = 1..T-2
Znext = np.vstack([x[1:-1], x[2:]])         # Z_{t+1}
m = (Z - ri * Znext) * eps[i, 1:-1][None, :]
emp = (m @ m.T) / m.shape[1]
G0 = (Z @ Z.T) / Z.shape[1]
G1 = (Z[:, 1:] @ Z[:, :-1].T) / (Z.shape[1] - 1)    # E[Z_t Z_{t-1}^T]
form = sig_f ** 2 * ((1 + ri ** 2) * G0 - ri * (G1 + G1.T))
out["S10_Omega_max_rel_error"] = float(np.max(np.abs(emp - form)) / np.max(np.abs(form)))

# Hidden assumption found in step 7: det Sigma_i = 0 when w_i = 0 (a cohort with zero weight)
out["finding_det_zero_when_w_zero"] = "det Sigma_i = w_i * (positive number): it is 0, not > 0, when w_i = 0"

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "check_prop_tagged_results.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "S5_S7_Sigma_check"}, indent=1))
for row in out["S5_S7_Sigma_check"]:
    print("Sigma rel. error", round(row["max_rel_error"], 4), "| det emp", round(row["det_empirical"], 5),
          "formula", round(row["det_formula"], 5), "step7", round(row["det_step7"], 5))
