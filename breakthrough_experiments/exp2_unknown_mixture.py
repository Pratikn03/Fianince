#!/usr/bin/env python3
"""
Experiment 2A: Unknown Heterogeneous Mixture Super-Resolution in Closed-Loop Markets
Recovers unknown K-cohort populations from the physical closed-loop market impulse response.
Features:
- Closed-loop state-space impulse response (price-first market dynamics)
- Inverts closed-loop transfer function H(z) = kappa / (z - a - kappa * G(z))
- Theorem 2.3: Cohort memory poles r_i = 1 - eta_i are the transmission zeros of H(z)
- Blind model order selection via singular value ratio / MDL without truth leakage
- Direct pole/rate recovery error metric (matched Hausdorff/Wasserstein distance)
"""
import json
from pathlib import Path
import numpy as np
from scipy import linalg, signal

def simulate_closed_loop_impulse(weights, etas, T=120, kappa=0.8, a=0.5):
    """
    Computes exact closed-loop impulse response to unit trade v_0 = 1.0:
    t = 0: x_0 = kappa * v_0 = kappa, y_{k,0} = eta_k * x_0
    t >= 1: x_t = a x_{t-1} + kappa sum_k w_k y_{k,t-1}
            y_{k,t} = (1 - eta_k) y_{k,t-1} + eta_k x_t
    Returns full impulse response h_0, h_1, ..., h_T
    """
    K = len(etas)
    h = np.zeros(T + 1)
    
    # t = 0
    x_0 = kappa * 1.0
    y_0 = etas * x_0
    h[0] = x_0
    
    x_prev = x_0
    y_prev = y_0.copy()
    
    for t in range(1, T + 1):
        u_t = np.sum(weights * y_prev)
        x_t = a * x_prev + kappa * u_t
        y_t = (1.0 - etas) * y_prev + etas * x_t
        h[t] = x_t
        x_prev = x_t
        y_prev = y_t.copy()
        
    return h

from scipy.optimize import nnls

def blind_transfer_function_inversion(noisy_h, max_K=6, kappa=0.8, a=0.5):
    """
    Inverts the closed-loop transfer function H(z) to extract hidden cohort poles and feedback weights.
    Theorem 2.3: H(z) = kappa / (z - a - kappa G(z))
    Transmission zeros of H(z) are identically the poles of G(z): r_i = 1 - eta_i.
    Feedback weights w_i are recovered by inverting u_t = (x_t - a x_{t-1}) / kappa = sum_i w_i y_{i, t-1}.
    """
    D_est = float(noisy_h[0]) if abs(noisy_h[0]) > 1e-4 else kappa
    g = noisy_h[1:]
    T_g = len(g)
    L = min(45, T_g // 2)
    
    # Hankel matrices of strictly proper impulse response
    H0 = linalg.hankel(g[:L], g[L-1:2*L-1])
    H1 = linalg.hankel(g[1:L+1], g[L:2*L])
    
    # SVD
    U, S, Vh = linalg.svd(H0)
    
    # Blind order selection using Gavish-Donoho optimal singular value thresholding
    # State dimension n = K + 1 (1 price state + K memory states)
    if S[0] > 1e-12:
        med_s = float(np.median(S))
        thresh = max(S[0] * 0.0005, 2.80 * med_s)
        n_est = int(np.sum(S > thresh))
        n_est = max(1, min(n_est, max_K + 1))
    else:
        n_est = 1
        
    if n_est <= 1:
        # Pure dealer market: K = 0 (zero algorithmic learning)
        return 0, np.array([]), np.array([])
        
    U_k = U[:, :n_est]
    S_k = np.diag(S[:n_est])
    V_k = Vh[:n_est, :].T
    
    sqrt_S = np.diag(np.sqrt(S[:n_est]))
    inv_sqrt_S = np.diag(1.0 / np.sqrt(S[:n_est]))
    
    # Kung's ERA realization of H(z)
    C_est = (U_k @ sqrt_S)[0:1, :]
    B_est = (sqrt_S @ V_k.T)[:, 0:1]
    A_est = inv_sqrt_S @ U_k.T @ H1 @ V_k @ inv_sqrt_S
    
    # Convert realization to transfer function H(z) = num(z) / den(z)
    num, den = signal.ss2tf(A_est, B_est, C_est, [[D_est]])
    num = num[0]
    
    # Roots of numerator are the transmission zeros of H(z)
    # By Theorem 2.3, these zeros are the cohort poles r_i = 1 - eta_i
    zeros = np.roots(num)
    
    # Filter valid real roots in (0.05, 0.98) representing algorithmic memory
    poles = []
    for z in zeros:
        if abs(z.imag) < 0.15 and 0.05 < np.real(z) < 0.98:
            poles.append(float(np.real(z)))
            
    if len(poles) == 0:
        # No detectable algorithmic poles (order collapsed to pure price mode)
        return 0, np.array([]), np.array([])
        
    poles = np.sort(poles)
    est_K = len(poles)
    est_etas = 1.0 - poles
    
    # Exact Physical Inversion for Feedback Weights w_i:
    # 1. Reconstruct latent memory states y_{k, t} from observed price history x_t:
    #    y_{k, 0} = eta_k * x_0
    #    y_{k, t} = (1 - eta_k) * y_{k, t-1} + eta_k * x_t
    # 2. Invert feedback: u_t = (x_t - a * x_{t-1}) / kappa = sum_k w_k y_{k, t-1}
    T_obs = len(noisy_h)
    y_rec = np.zeros((est_K, T_obs))
    for k in range(est_K):
        y_rec[k, 0] = est_etas[k] * noisy_h[0]
        for t in range(1, T_obs):
            y_rec[k, t] = (1.0 - est_etas[k]) * y_rec[k, t-1] + est_etas[k] * noisy_h[t]
            
    lhs = (noisy_h[1:] - a * noisy_h[:-1]) / kappa
    rhs = y_rec[:, :-1].T # shape (T_obs - 1, est_K)
    
    est_weights, _ = nnls(rhs, lhs)
    
    return est_K, np.array(poles), np.array(est_weights)

def matched_pole_error(true_poles, est_poles):
    """Computes directed Hausdorff matching distance between true and estimated poles."""
    if len(true_poles) == 0 and len(est_poles) == 0:
        return 0.0
    if len(est_poles) == 0 or len(true_poles) == 0:
        return 1.0
    errs = []
    for tp in true_poles:
        min_dist = np.min(np.abs(est_poles - tp))
        errs.append(min_dist)
    return float(np.max(errs))

def run_experiment():
    np.random.seed(42)
    T = 120
    K_list = [0, 1, 2, 3, 5]
    delta_list = [0.03, 0.08, 0.15]
    sigma_list = [0.0001, 0.001, 0.005]
    
    results = []
    
    for K in K_list:
        for delta in delta_list:
            for sigma in sigma_list:
                if K == 0:
                    true_etas = np.array([])
                    true_weights = np.array([])
                elif K == 1:
                    true_etas = np.array([0.30])
                    true_weights = np.array([0.20])
                else:
                    base_eta = 0.35
                    true_etas = np.linspace(base_eta - delta * (K - 1) / 2, base_eta + delta * (K - 1) / 2, K)
                    true_etas = np.clip(true_etas, 0.05, 0.85)
                    true_weights = np.ones(K) * (0.20 / K)
                    
                true_poles = 1.0 - true_etas
                true_h = simulate_closed_loop_impulse(true_weights, true_etas, T=T)
                
                trials = 30
                K_recovered = []
                pole_errors = []
                weight_errors = []
                per_cohort_errors = []
                per_cohort_success = []
                
                for _ in range(trials):
                    noisy_h = true_h + np.random.normal(0, sigma, len(true_h))
                    est_K, est_poles, est_weights = blind_transfer_function_inversion(noisy_h, max_K=6)
                    
                    K_recovered.append(int(est_K == K))
                    p_err = matched_pole_error(true_poles, est_poles)
                    pole_errors.append(p_err)
                    w_err = float(abs(np.sum(est_weights) - np.sum(true_weights)))
                    weight_errors.append(w_err)
                    # Per-cohort scoring (audit): weights matched by sorted pole order; only defined when K is right
                    if est_K == K and K > 0:
                        order = np.argsort(true_poles)
                        e = float(np.max(np.abs(np.asarray(est_weights) - true_weights[order])))
                        per_cohort_errors.append(e)
                        per_cohort_success.append(int(e < 0.01))
                    elif est_K == K == 0:
                        per_cohort_success.append(1)
                    else:
                        per_cohort_success.append(0)
                    
                recovery_rate = float(np.mean(K_recovered))
                mean_p_err = float(np.mean(pole_errors))
                mean_w_err = float(np.mean(weight_errors))
                
                results.append({
                    "true_K": K,
                    "delta": delta,
                    "sigma": sigma,
                    "blind_K_recovery_rate": recovery_rate,
                    "mean_pole_matching_error": mean_p_err,
                    "mean_weight_error": mean_w_err,
                    "mean_weight_error_definition": "absolute error of the SUM of weights only",
                    "median_per_cohort_weight_error_given_correct_K": (float(np.median(per_cohort_errors)) if per_cohort_errors else None),
                    "per_cohort_weight_recovery_rate_tol_0_01": float(np.mean(per_cohort_success))
                })
                
    out_file = Path("breakthrough_experiments/results_exp2_unknown_mixture.json")
    out_file.write_text(json.dumps(results, indent=2))
    print(f"Unknown mixture super-resolution experiment complete. Results written to {out_file}")

if __name__ == "__main__":
    run_experiment()
