#!/usr/bin/env python3
"""
Phase 6 / Priority 8: Observable-Data Microstructure Bridge & False Discovery Analysis
Investigates the mapping between structural feedback gamma and observable regression slopes.
Tests the No-Learning Economy (gamma = 0) to quantify false-positive rates induced by:
- Persistent order flow (autocorrelated TWAP/VWAP execution splitting, rho = 0.80)
- EMA trend filtering vs. raw return differencing
- Timestamp shifts without circular wraparound leakage
- Quasi-differenced structural innovation projection restoring nominal 5% size
"""
import json
import math
from pathlib import Path
import numpy as np

def run_bridge_simulation(seed, true_gamma=0.0, flow_persistence=0.80, use_quasi_diff=False, time_shift=0, T=2000):
    np.random.seed(seed)
    
    # Structural parameters
    a = 0.5           # price mean reversion
    kappa = 0.8       # price impact
    eta_adapt = 0.15  # trader adaptation memory rate
    
    # Exogenous execution order flow u_t: AR(1) persistence rho
    u = np.zeros(T)
    eta_innov = np.random.normal(0, 1.0, T)
    for t in range(1, T):
        u[t] = flow_persistence * u[t-1] + eta_innov[t]
        
    # State tracking
    x = np.zeros(T)   # price state
    y = np.zeros(T)   # adaptive memory state
    q = np.zeros(T)   # total agent order flow
    xi = np.random.normal(0, 0.2, T) # fundamental shock
    
    for t in range(T - 1):
        # Trader flow: structural feedback gamma on lagged memory/return + exogenous flow u_t
        q[t] = true_gamma * y[t] + u[t]
        
        # Price clearing with impact kappa
        x[t+1] = a * x[t] + kappa * q[t] + xi[t]
        
        # Online adaptive memory update
        dp = x[t+1] - x[t]
        y[t+1] = (1.0 - eta_adapt) * y[t] + eta_adapt * dp
        
    q[T-1] = true_gamma * y[T-1] + u[T-1]
    
    # Observed transaction prices with microstructure noise
    obs_prices = x + np.random.normal(0, 0.02, T)
    returns = np.diff(obs_prices) # length T - 1, r_t = p_{t+1} - p_t
    
    # Apply forward timestamp shift cleanly without circular wraparound
    flow_reg = q[:T-1].copy() # length T - 1
    if time_shift > 0:
        shifted = np.zeros_like(flow_reg)
        shifted[time_shift:] = flow_reg[:-time_shift]
        flow_reg = shifted
        
    # Regression specification: flow q_t on lagged return r_{t-1}
    # Y = q_t (for t = 2..T-2), X = r_{t-1} = p_t - p_{t-1}
    valid_start = max(50, time_shift + 2) # burn-in
    Y = flow_reg[valid_start:]
    X = returns[valid_start - 1 : len(flow_reg) - 1]
    
    if use_quasi_diff and flow_persistence > 0:
        # Cochrane-Orcutt / Prais-Winsten quasi-differencing:
        # q_t^perp = q_t - rho * q_{t-1}
        # r_{t-1}^perp = r_{t-1} - rho * r_{t-2}
        Y_prev = flow_reg[valid_start - 1 : len(flow_reg) - 1]
        X_prev = returns[valid_start - 2 : len(flow_reg) - 2]
        
        Y = Y - flow_persistence * Y_prev
        X = X - flow_persistence * X_prev
        
    # Standard OLS regression
    var_x = float(np.var(X))
    if var_x < 1e-12:
        return {"beta": 0.0, "t_stat": 0.0, "p_val": 1.0, "is_sig": False}
        
    beta = float(np.cov(X, Y)[0, 1] / var_x)
    residuals = Y - beta * X
    se = float(np.std(residuals) / (np.std(X) * np.sqrt(len(X))))
    t_stat = float(beta / se) if se > 1e-12 else 0.0
    p_val = float(2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0)))))
    is_sig = bool(abs(t_stat) > 1.96 and p_val < 0.05)
    
    return {
        "beta": beta,
        "se": se,
        "t_stat": t_stat,
        "p_val": p_val,
        "is_sig": is_sig
    }

def run_experiment():
    N_trials = 200
    
    # 1. No-Learning Economy (True gamma = 0.0): False Discovery Analysis
    # Condition A: Naive OLS with persistent flow (rho = 0.80) -> spurious correlation
    false_pos_persistent = []
    betas_persistent = []
    t_stats_persistent = []
    
    # Condition B: White-noise flow (rho = 0.0) -> exact nominal 5% size
    false_pos_white_noise = []
    
    # Condition C: Quasi-differenced projection on persistent flow -> purges bias
    false_pos_quasi_diff = []
    betas_quasi_diff = []
    
    # Condition D: Forward shifted flow (+1 step)
    false_pos_shifted = []
    
    for seed in range(N_trials):
        res_p = run_bridge_simulation(seed, true_gamma=0.0, flow_persistence=0.80, use_quasi_diff=False, time_shift=0)
        false_pos_persistent.append(res_p["is_sig"])
        betas_persistent.append(res_p["beta"])
        t_stats_persistent.append(res_p["t_stat"])
        
        res_w = run_bridge_simulation(seed, true_gamma=0.0, flow_persistence=0.0, use_quasi_diff=False, time_shift=0)
        false_pos_white_noise.append(res_w["is_sig"])
        
        res_q = run_bridge_simulation(seed, true_gamma=0.0, flow_persistence=0.80, use_quasi_diff=True, time_shift=0)
        false_pos_quasi_diff.append(res_q["is_sig"])
        betas_quasi_diff.append(res_q["beta"])
        
        res_s = run_bridge_simulation(seed, true_gamma=0.0, flow_persistence=0.80, use_quasi_diff=False, time_shift=1)
        false_pos_shifted.append(res_s["is_sig"])
        
    fp_rate_persistent = float(np.mean(false_pos_persistent))
    fp_rate_white = float(np.mean(false_pos_white_noise))
    fp_rate_quasi = float(np.mean(false_pos_quasi_diff))
    fp_rate_shifted = float(np.mean(false_pos_shifted))
    
    mean_beta_persistent = float(np.mean(betas_persistent))
    mean_t_persistent = float(np.mean(t_stats_persistent))
    mean_beta_quasi = float(np.mean(betas_quasi_diff))
    
    # 2. Structural and Reduced-Form Recovery with True Feedback (gamma = 0.20)
    recovery_betas_struct = []
    recovery_betas_rf = []
    T = 2000
    true_gamma = 0.20
    flow_persistence = 0.80
    eta_adapt = 0.15
    a = 0.5
    kappa = 0.8
    for seed in range(50):
        np.random.seed(seed)
        u = np.zeros(T)
        innov = np.random.normal(0, 1.0, T)
        for t in range(1, T):
            u[t] = flow_persistence * u[t-1] + innov[t]
        x = np.zeros(T)
        y = np.zeros(T)
        q = np.zeros(T)
        xi = np.random.normal(0, 0.2, T)
        for t in range(T-1):
            q[t] = true_gamma * y[t] + u[t]
            x[t+1] = a * x[t] + kappa * q[t] + xi[t]
            dp = x[t+1] - x[t]
            y[t+1] = (1.0 - eta_adapt) * y[t] + eta_adapt * dp
        q[T-1] = true_gamma * y[T-1] + u[T-1]
        
        # Observed prices with noise
        obs_p = x + np.random.normal(0, 0.02, T)
        dp_series = np.diff(obs_p)
        y_hat = np.zeros(T-1)
        for t in range(len(dp_series)-1):
            y_hat[t+1] = (1.0 - eta_adapt) * y_hat[t] + eta_adapt * dp_series[t]
            
        start = 50
        # Structural quasi-differenced regression: q on y_hat
        Y_q = q[start:T-1] - flow_persistence * q[start-1:T-2]
        X_y = y_hat[start:T-1] - flow_persistence * y_hat[start-1:T-2]
        b_struct = float(np.cov(X_y, Y_q)[0, 1] / np.var(X_y))
        recovery_betas_struct.append(b_struct)
        
        # Reduced-form quasi-differenced regression: q on raw dp
        X_dp = dp_series[start-1:T-2] - flow_persistence * dp_series[start-2:T-3]
        b_rf = float(np.cov(X_dp, Y_q)[0, 1] / np.var(X_dp))
        recovery_betas_rf.append(b_rf)
        
    mean_recovered_gamma_structural = float(np.mean(recovery_betas_struct))
    mean_recovered_gamma_rf = float(np.mean(recovery_betas_rf))
    
    summary = {
        "false_discovery_analysis_true_gamma_zero": {
            "N_trials": N_trials,
            "false_positive_rate_persistent_OLS": fp_rate_persistent,
            "mean_beta_persistent_OLS": mean_beta_persistent,
            "mean_t_stat_persistent_OLS": mean_t_persistent,
            "false_positive_rate_white_noise": fp_rate_white,
            "false_positive_rate_quasi_differenced": fp_rate_quasi,
            "mean_beta_quasi_differenced": mean_beta_quasi,
            "false_positive_rate_forward_shifted": fp_rate_shifted
        },
        "structural_recovery_true_gamma_0_20": {
            "true_gamma": true_gamma,
            "mean_recovered_gamma_structural": mean_recovered_gamma_structural,
            "structural_bias": float(mean_recovered_gamma_structural - true_gamma),
            "mean_recovered_gamma_reduced_form": mean_recovered_gamma_rf,
            "attenuation_factor": float(mean_recovered_gamma_rf / true_gamma)
        }
    }
    
    out_file = Path("breakthrough_experiments/results_exp8_observable_bridge.json")
    out_file.write_text(json.dumps(summary, indent=2))
    print(f"Observable Bridge Experiment complete. Results written to {out_file}")
    print(f"Naive OLS under persistent flow:  {fp_rate_persistent*100:.1f}% false positives (mean beta = {mean_beta_persistent:.3f}, mean t = {mean_t_persistent:.2f})")
    print(f"White-noise flow benchmark:        {fp_rate_white*100:.1f}% false positives (nominal size = 5.0%)")
    print(f"Quasi-differenced projection:      {fp_rate_quasi*100:.1f}% false positives (purged mean beta = {mean_beta_quasi:.3f})")
    print(f"Forward shifted (+1 step):         {fp_rate_shifted*100:.1f}% false positives")
    print(f"Structural gamma recovery (true=0.20): hat(gamma) = {mean_recovered_gamma_structural:.4f} (bias = {mean_recovered_gamma_structural - true_gamma:.4f})")
    print(f"Reduced-form lag beta (attenuated):    hat(beta)  = {mean_recovered_gamma_rf:.4f}")

if __name__ == "__main__":
    run_experiment()
