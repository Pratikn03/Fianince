"""Value of disclosure for safe capacity (Theorem thm:disclosure; test T07, blueprint D9, E06): public price-response
certificate versus class-tagged flows (measured with noise, 2SLS) versus audited exposure (oracle)."""
import numpy as np
from scipy.stats import norm
from model_contracts import impulse, summed_response
from uncertainty_calibration import certificate, T_for
from robust_admission import alpha_star, Phi_from_S


def run_disclosure():
    rng = np.random.default_rng(7); t7 = []
    for rho_true in [0.6, 0.9, 0.97, 0.995]:
        aa, kk = 0.4, 1.0; eta = np.array([1 - rho_true, 0.5]); q = np.array([0.06, 0.12])     # one long-memory class
        Phi_ = q.sum(); S = summed_response(aa, kk, Phi_); I, ub, Bb = 1.0, 0.48, 1.0
        a_oracle = alpha_star(aa, kk, Phi_, I, ub, Bb)
        sbar = aa + kk * Phi_ + 0.02; N, sig_ = 500, 0.05
        res = {"rho": rho_true, "S": S, "alpha_oracle_audited": a_oracle}
        # public: price-response certificate with memory bound rho_true
        aps = []
        h = impulse(aa, kk, q, eta, 20000); T = min(T_for(0.02 * S, kk, rho_true, sbar), 20000)
        for rep in range(300):
            hb = h[:T] + rng.normal(0, sig_ / np.sqrt(N), T)
            Sup = certificate(np.r_[hb], sig_, N, kk, rho_true, sbar, T, 0.05)
            aps.append(alpha_star(aa, kk, Phi_from_S(aa, kk, Sup), I, ub, Bb) or 0.0)
        res["alpha_public_mean"] = float(np.mean(aps)); res["T_public"] = int(T)
        # class-tagged: each class's flow u_c,t = r_c u_c,t-1 + w_c x_t + noise; passive data, T_f periods
        Tf, sf = 2000, 0.02; atg = []
        for rep in range(300):
            x = np.zeros(Tf); y = np.zeros(2)
            for t in range(1, Tf):
                x[t] = aa * x[t - 1] + kk * np.dot(q, y) + rng.normal(0, 1); y = (1 - eta) * y + eta * x[t]
            Phi_up = 0.0; var_sum = 0.0
            for c in range(2):
                u = q[c] * np.zeros(Tf); yy = 0.0
                yc = np.zeros(Tf)
                for t in range(1, Tf):
                    yc[t] = (1 - eta[c]) * yc[t - 1] + eta[c] * x[t]
                sig_c = q[c] * yc; u = sig_c + rng.normal(0, 0.1 * np.std(sig_c), Tf)   # tagged flows measured with 10% noise
                # 2SLS: u_t on (u_{t-1}, x_t), instrumenting the noisy u_{t-1} by u_{t-2} (Paper 1, Proposition tagged)
                yv = u[2:]; X = np.c_[u[1:-1], x[2:]]; Z = np.c_[u[:-2], x[2:]]
                Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
                beta = np.linalg.solve(Pz.T @ X, Pz.T @ yv); res_ = yv - X @ beta
                s2 = res_ @ res_ / (len(yv) - 2); V = s2 * np.linalg.inv(Pz.T @ Pz)
                r_h, w_h = beta; g = np.array([w_h / (1 - r_h) ** 2, 1 / (1 - r_h)])
                Phi_up += w_h / (1 - r_h); var_sum += g @ V @ g
            Phi_up += norm.ppf(0.95) * np.sqrt(var_sum)
            atg.append(alpha_star(aa, kk, max(Phi_up, 1e-9), I, ub, Bb) or 0.0)
        res["alpha_tagged_mean"] = float(np.mean(atg))
        res["value_tagged_vs_public"] = res["alpha_tagged_mean"] - res["alpha_public_mean"]
        res["value_audited_vs_public"] = a_oracle - res["alpha_public_mean"]
        t7.append(res)
    return {"rows": t7, "note": "capacity alpha* in [0,1]; value = extra admitted fraction of algorithmic flow; "
                           "net value = w * value - disclosure cost, which can be negative"}




def _tagged_estimate(rng, aa, kk, q, eta, Tf):
    """One replication of the class-tagged contract (as in run_disclosure): 2SLS per class and the delta method.
    Returns the estimated total exposure, its delta-method standard deviation and the slow class's standard error."""
    x = np.zeros(Tf); y = np.zeros(2)
    for t in range(1, Tf):
        x[t] = aa * x[t - 1] + kk * np.dot(q, y) + rng.normal(0, 1); y = (1 - eta) * y + eta * x[t]
    Phi_hat = 0.0; var_sum = 0.0; se_slow = None
    for c in range(2):
        yc = np.zeros(Tf)
        for t in range(1, Tf):
            yc[t] = (1 - eta[c]) * yc[t - 1] + eta[c] * x[t]
        sig_c = q[c] * yc; u = sig_c + rng.normal(0, 0.1 * np.std(sig_c), Tf)
        yv = u[2:]; X = np.c_[u[1:-1], x[2:]]; Z = np.c_[u[:-2], x[2:]]
        Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
        beta = np.linalg.solve(Pz.T @ X, Pz.T @ yv); res_ = yv - X @ beta
        s2 = res_ @ res_ / (len(yv) - 2); V = s2 * np.linalg.inv(Pz.T @ Pz)
        r_h, w_h = beta; g = np.array([w_h / (1 - r_h) ** 2, 1 / (1 - r_h)])
        Phi_hat += w_h / (1 - r_h); var_sum += g @ V @ g
        if c == 0:
            se_slow = float(np.sqrt(g @ V @ g))
    return Phi_hat, float(np.sqrt(var_sum)), se_slow


def run_disclosure_intersection():
    """Theorem thm:disclosure (v): a noisy class-tagged certificate can admit less than the public one when the slow
    class's memory is long; intersecting the two certificates, each at level 1 - gamma/2, is valid at level 1 - gamma and
    admits at least as much as the better of the two at level 1 - gamma/2 (test T15, seed 15, design of T07)."""
    rng = np.random.default_rng(15); rows = []; g = 0.05
    for rho_true in [0.6, 0.9, 0.97, 0.995]:
        aa, kk = 0.4, 1.0; eta = np.array([1 - rho_true, 0.5]); q = np.array([0.06, 0.12])
        Phi_ = q.sum(); S = summed_response(aa, kk, Phi_); I, ub, Bb = 1.0, 0.48, 1.0
        sbar = aa + kk * Phi_ + 0.02; N, sig_ = 500, 0.05
        h = impulse(aa, kk, q, eta, 20000); T = min(T_for(0.02 * S, kk, rho_true, sbar), 20000)
        A = {"public": [], "tagged": [], "intersection": []}; cov = []; se_slow = []
        for rep in range(300):
            hb = h[:T] + rng.normal(0, sig_ / np.sqrt(N), T)
            P1 = Phi_from_S(aa, kk, certificate(hb, sig_, N, kk, rho_true, sbar, T, g))
            P2 = Phi_from_S(aa, kk, certificate(hb, sig_, N, kk, rho_true, sbar, T, g / 2))
            ph, sd, se = _tagged_estimate(rng, aa, kk, q, eta, 2000); se_slow.append(se)
            T1, T2 = ph + norm.ppf(1 - g) * sd, ph + norm.ppf(1 - g / 2) * sd
            Pint = min(P2, T2); cov.append(Phi_ <= Pint)
            A["public"].append(alpha_star(aa, kk, P1, I, ub, Bb) or 0.0)
            A["tagged"].append(alpha_star(aa, kk, max(T1, 1e-9), I, ub, Bb) or 0.0)
            A["intersection"].append(alpha_star(aa, kk, max(Pint, 1e-9), I, ub, Bb) or 0.0)
        rows.append({"rho": rho_true, "alpha_oracle": alpha_star(aa, kk, Phi_, I, ub, Bb),
                     **{f"alpha_{k}_mean": float(np.mean(v)) for k, v in A.items()},
                     "coverage_intersection": float(np.mean(cov)), "se_slow_class_mean": float(np.mean(se_slow)),
                     "se_slow_times_(1-r)^2": float(np.mean(se_slow) * (1 - rho_true) ** 2)})
    ok = all(r["alpha_intersection_mean"] >= max(r["alpha_public_mean"], r["alpha_tagged_mean"]) - 0.02 and
             r["coverage_intersection"] >= 0.93 for r in rows)
    return {"rows": rows, "pass": bool(ok),
            "note": "intersection admits about as much as the better single certificate at every memory rate and covers"}
