#!/usr/bin/env python3
"""
Experiment 2A: Unknown Heterogeneous Mixture Super-Resolution
Moves beyond known 2-model pair to recover unknown K-cohort populations.
Evaluates matrix-pencil / ESPRIT estimation, condition numbers, and recovery rates.
"""
import json
from pathlib import Path
import numpy as np
from scipy import linalg, optimize

def generate_mixture_impulse(weights, lambdas, T):
    """Generate impulse response h_t = sum_k weights[k] * lambdas[k]^t for t=0..T-1."""
    t = np.arange(T)
    h = np.zeros(T)
    for w, lam in zip(weights, lambdas):
        h += w * (lam ** t)
    return h

def matrix_pencil_estimation(noisy_h, max_K, snr_thresh=0.01):
    """
    Matrix Pencil method to estimate exponential poles and weights from noisy sequence.
    Hankel matrix size L x M where L = T/2.
    """
    T = len(noisy_h)
    L = T // 2
    M = T - L + 1
    # Build Hankel matrices Y0 and Y1
    Y0 = linalg.hankel(noisy_h[:L], noisy_h[L-1:T-1])
    Y1 = linalg.hankel(noisy_h[1:L+1], noisy_h[L:T])
    
    # SVD of Y0
    U, S, Vh = linalg.svd(Y0)
    # Estimate K based on singular values
    if S[0] > 0:
        rel_s = S / S[0]
        eff_K = int(np.sum(rel_s > snr_thresh))
        eff_K = max(1, min(eff_K, max_K))
    else:
        eff_K = 1
        
    U_k = U[:, :eff_K]
    S_k = np.diag(S[:eff_K])
    V_k = Vh[:eff_K, :].T
    
    # Solve generalized eigenvalue problem or reduced matrix
    # Z = S_k^{-1} U_k^H Y1 V_k
    Z = np.linalg.pinv(S_k) @ (U_k.T @ Y1 @ V_k)
    evals = linalg.eigvals(Z)
    
    # Filter real poles in [0, 1)
    poles = []
    for ev in evals:
        if np.isreal(ev) or abs(ev.imag) < 0.05:
            r_ev = float(np.real(ev))
            if 0.0 <= r_ev < 1.0:
                poles.append(r_ev)
    if len(poles) == 0:
        poles = [0.5]
    poles = np.sort(poles)
    
    # Solve linear least squares for weights given estimated poles
    Vand = np.column_stack([p ** np.arange(T) for p in poles])
    weights, _, _, _ = np.linalg.lstsq(Vand, noisy_h, rcond=None)
    
    return eff_K, poles, weights

def run_experiment():
    np.random.seed(42)
    T = 100
    K_list = [1, 2, 3, 5]
    delta_list = [0.02, 0.05, 0.10, 0.15, 0.20]
    sigma_list = [0.0001, 0.001, 0.01]
    
    results = []
    
    for K in K_list:
        for delta in delta_list:
            for sigma in sigma_list:
                # Generate true parameters
                if K == 1:
                    true_lambdas = np.array([0.7])
                    true_weights = np.array([0.5])
                else:
                    base = 0.5
                    true_lambdas = np.linspace(base - delta * (K - 1) / 2, base + delta * (K - 1) / 2, K)
                    true_lambdas = np.clip(true_lambdas, 0.05, 0.95)
                    true_weights = np.ones(K) * (0.5 / K)
                
                # Check Vandermonde condition number of true poles
                V_true = np.column_stack([p ** np.arange(T) for p in true_lambdas])
                cond_V = float(np.linalg.cond(V_true))
                
                # Run 50 Monte Carlo trials
                K_errors = []
                weight_errors = []
                aggregate_Q_errors = []
                
                true_h = generate_mixture_impulse(true_weights, true_lambdas, T)
                true_Q = float(np.sum(true_weights))
                
                for trial in range(50):
                    noise = np.random.normal(0, sigma, T)
                    noisy_h = true_h + noise
                    
                    est_K, est_poles, est_weights = matrix_pencil_estimation(noisy_h, max_K=K+2, snr_thresh=sigma * 2)
                    
                    K_errors.append(abs(est_K - K))
                    est_Q = float(np.sum(est_weights))
                    aggregate_Q_errors.append(abs(est_Q - true_Q))
                
                res = {
                    "K": K,
                    "delta": delta,
                    "sigma": sigma,
                    "vandermonde_condition_number": cond_V,
                    "mean_K_error": float(np.mean(K_errors)),
                    "mean_aggregate_Q_error": float(np.mean(aggregate_Q_errors)),
                    "P95_aggregate_Q_error": float(np.percentile(aggregate_Q_errors, 95)),
                    "identification_success_rate": float(np.mean([e < 0.05 for e in aggregate_Q_errors]))
                }
                results.append(res)
                
    output_path = Path("breakthrough_experiments/results_exp2_unknown_mixture.json")
    output_path.write_text(json.dumps(results, indent=2))
    print(f"Experiment 2A complete: {len(results)} configurations evaluated. Results written to {output_path}")

if __name__ == "__main__":
    run_experiment()
