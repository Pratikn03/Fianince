"""
Rebuild Minimum-Distance (MD) Lyapunov Estimator.
==================================================
Implements HAC-weighted minimum distance for the 2x2 linear state-space system:
  z_{t+1} = J z_t + e_{t+1},   Sigma_e unrestricted symmetric positive-definite.

Parameters (k = 7):
  J_11, J_12, J_21, J_22, sigma_11, sigma_12, sigma_22

Moments (m = 11):
  vech(Gamma_0): 3 moments
  vec(Gamma_1):  4 moments
  vec(Gamma_2):  4 moments

Degrees of Freedom:
  df = m - k = 11 - 7 = 4.
"""
from __future__ import annotations
import json
import pickle
from pathlib import Path
import numpy as np
import scipy.linalg as la
from scipy.optimize import minimize
from scipy.stats import chi2

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from empirical_pipeline.feedback_var import build_series

CACHE_DIR = ROOT / "empirical_pipeline" / "cache"
OUT_DIR = ROOT / "results" / "provenance"

def run_md_rebuild():
    assets = ["BTC", "ETH", "ADA"]
    all_Z = []
    asset_results = {}

    for ast in assets:
        pkl_path = CACHE_DIR / f"{ast}_1sec_core_v2dedup.pkl"
        if not pkl_path.exists():
            continue
        with open(pkl_path, "rb") as f:
            df = pickle.load(f)
        s = build_series(df, delta=10, window=300)
        x = s["x"].to_numpy()
        f_arr = s["f"].to_numpy()
        x = (x - np.mean(x)) / np.std(x)
        f_arr = (f_arr - np.mean(f_arr)) / np.std(f_arr)
        Z_ast = np.column_stack([x, f_arr])
        all_Z.append(Z_ast)

        # Single-asset MD
        res_ast = estimate_md_for_data(Z_ast)
        asset_results[ast] = res_ast

    # Pooled MD across all cached high-frequency series
    Z_pooled = np.vstack(all_Z)
    pooled_res = estimate_md_for_data(Z_pooled)

    output = {
        "description": "Rebuilt 11-moment, 7-parameter HAC-weighted Minimum-Distance Lyapunov Estimator",
        "m_moments": 11,
        "k_parameters": 7,
        "df": 4,
        "parameters": ["J11", "J12", "J21", "J22", "sigma11", "sigma12", "sigma22"],
        "pooled": pooled_res,
        "by_asset": asset_results,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "minimum_distance_rebuild.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved MD rebuild results to {out_file}")
    return output


def estimate_md_for_data(Z: np.ndarray, bandwidth_L: int = 10) -> dict:
    T = len(Z)
    G0 = (Z.T @ Z) / T
    G1 = (Z[1:].T @ Z[:-1]) / (T - 1)
    G2 = (Z[2:].T @ Z[:-2]) / (T - 2)

    m_hat = np.concatenate([
        [G0[0, 0], G0[0, 1], G0[1, 1]],
        G1.flatten(),
        G2.flatten()
    ])

    u = np.zeros((T - 2, 11))
    for t in range(T - 2):
        z_t = Z[t]
        z_t1 = Z[t + 1]
        z_t2 = Z[t + 2]
        g0_t = np.array([z_t[0]**2, z_t[0] * z_t[1], z_t[1]**2])
        g1_t = np.outer(z_t1, z_t).flatten()
        g2_t = np.outer(z_t2, z_t).flatten()
        u[t] = np.concatenate([g0_t, g1_t, g2_t]) - m_hat

    N_u = len(u)
    Omega0 = (u.T @ u) / N_u
    V_hac = Omega0.copy()
    for l in range(1, bandwidth_L + 1):
        w_l = 1.0 - l / (bandwidth_L + 1)
        Gamma_l = (u[l:].T @ u[:-l]) / N_u
        V_hac += w_l * (Gamma_l + Gamma_l.T)

    W = la.pinv(V_hac)

    def get_theo_moments(p):
        J11, J12, J21, J22, s11, s12, s22 = p
        J = np.array([[J11, J12], [J21, J22]])
        if np.max(np.abs(la.eigvals(J))) >= 0.999:
            return None
        Sigma = np.array([[s11, s12], [s12, s22]])
        if s11 <= 0 or s22 <= 0 or (s11 * s22 - s12**2) <= 0:
            return None
        denom = np.eye(4) - np.kron(J, J)
        if abs(la.det(denom)) < 1e-8:
            return None
        vec_g0 = la.solve(denom, Sigma.flatten())
        G0_m = vec_g0.reshape(2, 2)
        G1_m = J @ G0_m
        G2_m = J @ G1_m
        return np.concatenate([
            [G0_m[0, 0], G0_m[0, 1], G0_m[1, 1]],
            G1_m.flatten(),
            G2_m.flatten()
        ])

    def objective(p):
        m_th = get_theo_moments(p)
        if m_th is None:
            return 1e8
        diff = m_hat - m_th
        return float(diff.T @ W @ diff)

    v_ols = la.lstsq(Z[:-1], Z[1:])[0].T
    res = Z[1:] - Z[:-1] @ v_ols.T
    Sig_ols = (res.T @ res) / len(res)

    init_p = [v_ols[0, 0], v_ols[0, 1], v_ols[1, 0], v_ols[1, 1], Sig_ols[0, 0], Sig_ols[0, 1], Sig_ols[1, 1]]
    bounds = [
        (0.5, 0.99), (-0.5, 0.5), (-0.5, 0.5), (0.01, 0.99),
        (0.01, 5.0), (-2.0, 2.0), (0.01, 5.0)
    ]

    res_opt = minimize(objective, init_p, method="L-BFGS-B", bounds=bounds)
    p_hat = res_opt.x
    Q_md = float(p_hat[1] * p_hat[2] / (1.0 - p_hat[3]) if abs(1.0 - p_hat[3]) > 1e-4 else p_hat[1] * p_hat[2])
    S_md = float(p_hat[0] + Q_md)
    rho_md = float(np.max(np.abs(la.eigvals(np.array([[p_hat[0], p_hat[1]], [p_hat[2], p_hat[3]]])))))

    eps = 1e-5
    G_jac = np.zeros((11, 7))
    m_0 = get_theo_moments(p_hat)
    for i in range(7):
        p_step = p_hat.copy()
        p_step[i] += eps
        m_step = get_theo_moments(p_step)
        G_jac[:, i] = (m_step - m_0) / eps

    rank_G = int(np.linalg.matrix_rank(G_jac))
    diff = m_hat - m_0
    J_stat = float(N_u * diff.T @ W @ diff)
    p_val = float(1.0 - chi2.cdf(J_stat, df=4))

    cov_p = (1.0 / N_u) * la.pinv(G_jac.T @ W @ G_jac)
    grad_Q = np.array([0, p_hat[2] / (1.0 - p_hat[3]), p_hat[1] / (1.0 - p_hat[3]), p_hat[1] * p_hat[2] / ((1.0 - p_hat[3])**2), 0, 0, 0])
    se_Q = float(np.sqrt(max(0, float(grad_Q.T @ cov_p @ grad_Q))))

    return {
        "n_obs": T,
        "success": bool(res_opt.success),
        "theta": [float(x) for x in p_hat],
        "Q_MD": Q_md,
        "se_Q": se_Q,
        "ci95_Q": [Q_md - 1.96 * se_Q, Q_md + 1.96 * se_Q],
        "S_MD": S_md,
        "rho_MD": rho_md,
        "jacobian_rank": rank_G,
        "Hansen_J_stat": J_stat,
        "df": 4,
        "p_val": p_val,
    }


if __name__ == "__main__":
    run_md_rebuild()
