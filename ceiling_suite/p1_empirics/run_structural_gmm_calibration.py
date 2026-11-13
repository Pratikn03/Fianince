#!/usr/bin/env python3
"""
Structural Econometric GMM / SMM Calibration of Paper 1 Model
=============================================================

Fits the structural parameter vector theta = (a, kappa, eta, q, sigma_w^2) on
high-frequency market data (BTC-USDT and ETH-USDT 5-minute bars) using two-step
optimal GMM with Newey-West HAC weighting.

Replaces illustrative parameter assumptions (e.g. hypothetical 4,000 years)
with empirical point estimates, asymptotic standard errors, Hansen's J-test,
and empirically fitted identification sample sizes T*(Delta_eta).
"""

import sys
import os
import csv
import json
import math
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2, norm

def load_series(csv_path):
    """Load midpoint and order flow from 5-min CSV."""
    midpoints = []
    buys = []
    sells = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                m = float(row['midpoint'])
                b = float(row['buys'])
                s = float(row['sells'])
                midpoints.append(m)
                buys.append(b)
                sells.append(s)
            except (ValueError, KeyError):
                continue
    
    midpoints = np.array(midpoints)
    buys = np.array(buys)
    sells = np.array(sells)
    
    # 5-min log return in basis points
    rets = np.diff(np.log(midpoints)) * 10000.0
    
    # Price deviation / error x_t: demeaned return or HP/EWMA error
    # Paper 1 models pricing error x_t
    alpha_ewma = 0.05
    ewma = np.zeros_like(rets)
    ewma[0] = rets[0]
    for t in range(1, len(rets)):
        ewma[t] = alpha_ewma * rets[t] + (1 - alpha_ewma) * ewma[t-1]
    x = rets - ewma
    
    # Normalized order flow u_t: net flow in normalized units
    tot_vol = buys[1:] + sells[1:] + 1e-8
    u = (buys[1:] - sells[1:]) / tot_vol
    
    return x, u

def compute_moments(theta, x, u):
    """
    Compute moment conditions for structural model:
    x_t = a * x_{t-1} + kappa * (u_t + f_t) + w_t
    f_t = eta * f_{t-1} + q * x_{t-1}
    """
    a, kappa, eta, q, sigma_w2 = theta
    T = len(x)
    
    # Compute recursive feedback f_t
    f = np.zeros(T)
    for t in range(1, T):
        f[t] = eta * f[t-1] + q * x[t-1]
    
    # Residual w_t
    # We evaluate for t >= 2
    w = np.zeros(T)
    for t in range(2, T):
        w[t] = x[t] - a * x[t-1] - kappa * (u[t] + f[t])
    
    valid = np.arange(2, T)
    N = len(valid)
    
    wv = w[valid]
    xv_l1 = x[valid - 1]
    xv_l2 = x[valid - 2]
    uv_l1 = u[valid - 1]
    uv_l2 = u[valid - 2]
    fv = f[valid]
    
    # Moment matrix G: N x 7
    g = np.zeros((N, 7))
    g[:, 0] = wv
    g[:, 1] = wv * xv_l1
    g[:, 2] = wv * xv_l2
    g[:, 3] = wv * uv_l1
    g[:, 4] = wv * uv_l2
    g[:, 5] = wv**2 - sigma_w2
    g[:, 6] = wv * fv
    
    return g

def newey_west_hac(g, max_lags=5):
    """Newey-West HAC spectral covariance estimator."""
    N, K = g.shape
    g_demean = g - np.mean(g, axis=0)
    
    Gamma0 = np.dot(g_demean.T, g_demean) / N
    S = Gamma0.copy()
    
    for lag in range(1, max_lags + 1):
        weight = 1.0 - lag / (max_lags + 1.0)
        Gamma_lag = np.dot(g_demean[lag:].T, g_demean[:-lag]) / N
        S += weight * (Gamma_lag + Gamma_lag.T)
        
    return S

def fit_gmm(x, u, asset_name="BTC"):
    """Run two-step optimal GMM estimation."""
    print(f"\n--- Estimating Structural GMM for {asset_name} (N = {len(x)} bars) ---")
    
    # Initial parameter guess: a=0.7, kappa=0.5, eta=0.85, q=0.05, sigma_w2=var(x)
    init_sigma_w2 = float(np.var(x))
    theta0 = np.array([0.70, 0.50, 0.85, 0.05, init_sigma_w2])
    
    bounds = [
        (-0.95, 0.95),     # a: stability bound
        (0.001, 10.0),     # kappa > 0: price impact
        (0.01, 0.99),      # eta in (0, 1): memory decay
        (-2.0, 2.0),       # q: feedback sensitivity
        (1e-4, 500.0)      # sigma_w2 > 0: innovation variance
    ]
    
    # Step 1: Weighting matrix W1 = diag(1 / var(g))
    g_init = compute_moments(theta0, x, u)
    var_g = np.var(g_init, axis=0)
    var_g[var_g < 1e-6] = 1.0
    W1 = np.diag(1.0 / var_g)
    
    def obj_step1(theta):
        g = compute_moments(theta, x, u)
        g_bar = np.mean(g, axis=0)
        return float(np.dot(g_bar, np.dot(W1, g_bar)))
    
    res1 = minimize(obj_step1, theta0, method='L-BFGS-B', bounds=bounds)
    theta1 = res1.x
    print(f"Step 1 estimates: {np.round(theta1, 4)}")
    
    # Step 2: Optimal HAC weighting matrix W2 = S^{-1}
    g_step1 = compute_moments(theta1, x, u)
    S = newey_west_hac(g_step1, max_lags=6)
    
    # Regularize S if near singular
    rcond = np.linalg.cond(S)
    if rcond > 1e12 or np.isnan(rcond):
        S += np.eye(S.shape[0]) * 1e-4
    W2 = np.linalg.pinv(S)
    
    def obj_step2(theta):
        g = compute_moments(theta, x, u)
        g_bar = np.mean(g, axis=0)
        return float(np.dot(g_bar, np.dot(W2, g_bar)))
    
    res2 = minimize(obj_step2, theta1, method='L-BFGS-B', bounds=bounds)
    theta_gmm = res2.x
    
    # Asymptotic Standard Errors
    # Jacobian G = d(g_bar) / d(theta)
    eps = 1e-5
    p = len(theta_gmm)
    g_hat = compute_moments(theta_gmm, x, u)
    N = len(g_hat)
    G_jac = np.zeros((g_hat.shape[1], p))
    for j in range(p):
        theta_plus = theta_gmm.copy()
        theta_plus[j] += eps
        g_plus = np.mean(compute_moments(theta_plus, x, u), axis=0)
        
        theta_minus = theta_gmm.copy()
        theta_minus[j] -= eps
        g_minus = np.mean(compute_moments(theta_minus, x, u), axis=0)
        
        G_jac[:, j] = (g_plus - g_minus) / (2 * eps)
        
    M = np.dot(G_jac.T, np.dot(W2, G_jac))
    try:
        vcov = np.linalg.pinv(M) / N
        se = np.sqrt(np.diag(vcov))
    except Exception:
        se = np.full(p, np.nan)
        
    # Hansen's J-test of overidentifying restrictions
    g_final = compute_moments(theta_gmm, x, u)
    g_bar_final = np.mean(g_final, axis=0)
    J_stat = float(N * np.dot(g_bar_final, np.dot(W2, g_bar_final)))
    df = g_final.shape[1] - p  # 7 - 5 = 2 degrees of freedom
    p_val = float(1.0 - chi2.cdf(J_stat, df))
    
    names = ["a", "kappa", "eta", "q", "sigma_w2"]
    results = {}
    print("\nGMM Estimates & Standard Errors:")
    for i, name in enumerate(names):
        val = float(theta_gmm[i])
        s = float(se[i]) if not np.isnan(se[i]) else 0.0
        t_stat = val / s if s > 1e-8 else np.nan
        results[name] = {"est": val, "se": s, "t_stat": t_stat}
        print(f"  {name:>10s}: {val:9.4f}  (SE: {s:7.4f}, t = {t_stat:6.2f})")
        
    print(f"\nHansen's J-test: J = {J_stat:.4f}, df = {df}, p-value = {p_val:.4f}")
    results["hansen_j"] = {"stat": J_stat, "df": df, "p_value": p_val}
    results["sample_size"] = N
    
    # Compute Identification Horizon T*(Delta_eta) under fitted parameters
    # Theorem 4.3 / 7.1 lower bound:
    # T*(Delta_eta) = 4 * sigma_w2 * (z_{1-alpha/2} + z_{1-beta})^2 / (kappa^2 * (Delta_eta)^{4K-2})
    # For K=2, 4K-2 = 6.
    alpha = 0.05
    power = 0.80
    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = norm.ppf(power)
    z_factor = (z_alpha + z_beta)**2  # approx (1.96 + 0.84)^2 = 7.84
    
    hat_kappa = theta_gmm[1]
    hat_sigma_w2 = theta_gmm[4]
    
    id_horizons = {}
    for delta_eta in [0.05, 0.10, 0.20]:
        denom = (hat_kappa**2) * (delta_eta**6)
        T_bars = 4.0 * hat_sigma_w2 * z_factor / denom
        T_days_crypto = T_bars / 288.0       # 288 5-min bars per day in 24/7 crypto
        T_years_crypto = T_days_crypto / 365.25
        T_days_equity = T_bars / 78.0        # 78 5-min bars per 6.5h trading day
        T_years_equity = T_days_equity / 252.0
        
        id_horizons[f"delta_eta_{delta_eta:.2f}"] = {
            "T_bars": float(T_bars),
            "T_days_crypto": float(T_days_crypto),
            "T_years_crypto": float(T_years_crypto),
            "T_days_equity": float(T_days_equity),
            "T_years_equity": float(T_years_equity)
        }
        print(f"  Identification Horizon for Delta_eta = {delta_eta:.2f} (K=2):")
        print(f"    T* = {T_bars:12.1f} bars  ({T_days_crypto:8.1f} crypto days, {T_years_crypto:6.2f} years)")
        
    results["identification_horizons"] = id_horizons
    return results

def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(root, "empirical_pipeline", "data")
    out_dir = os.path.join(root, "ceiling_suite", "p1_empirics", "results")
    os.makedirs(out_dir, exist_ok=True)
    
    btc_path = os.path.join(data_dir, "BTC_5min.csv")
    eth_path = os.path.join(data_dir, "ETH_5min.csv")
    
    all_results = {}
    
    if os.path.exists(btc_path):
        x_btc, u_btc = load_series(btc_path)
        all_results["BTC"] = fit_gmm(x_btc, u_btc, "BTC-USDT")
        
    if os.path.exists(eth_path):
        x_eth, u_eth = load_series(eth_path)
        all_results["ETH"] = fit_gmm(x_eth, u_eth, "ETH-USDT")
        
    out_file = os.path.join(out_dir, "structural_gmm_calibration_results.json")
    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[SUCCESS] Structural calibration complete. Saved to:\n  {out_file}")

if __name__ == "__main__":
    main()
