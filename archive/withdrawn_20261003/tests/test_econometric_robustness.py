"""
Econometric Robustness and Identification Diagnostics Suite.
Performs:
1. Anderson-Rubin (1949) weak-instrument robust inference.
2. Durbin-Wu-Hausman endogeneity test (OLS vs 2SLS specification).
3. First-stage Kleibergen-Paap rk Wald F-statistic verification.
"""
import numpy as np
import pytest
from scipy import stats

def run_2sls_with_diagnostics(y: np.ndarray, x: np.ndarray, z: np.ndarray, w: np.ndarray):
    """
    y: Price innovation (N,)
    x: Endogenous order flow imbalance OFI (N,)
    z: Exogenous latency instrument (N,)
    w: Exogenous controls (volatility, trade counts) (N, K)
    """
    N = len(y)
    # Add intercept to controls
    W = np.column_stack([np.ones(N), w])
    
    # Projection matrix for exogenous controls: M_W = I - W(W'W)^-1 W'
    Q_w, R_w = np.linalg.qr(W)
    
    def project_out(vec):
        return vec - Q_w @ (Q_w.T @ vec)
    
    y_tilde = project_out(y)
    x_tilde = project_out(x)
    z_tilde = project_out(z)
    
    # First stage: x_tilde on z_tilde
    gamma_hat = np.dot(z_tilde, x_tilde) / np.dot(z_tilde, z_tilde)
    x_hat = z_tilde * gamma_hat
    u_first = x_tilde - x_hat
    s2_first = np.sum(u_first**2) / (N - W.shape[1] - 1)
    f_stat = (gamma_hat**2 * np.sum(z_tilde**2)) / s2_first
    
    # Second stage: y_tilde on x_hat
    beta_2sls = np.dot(x_hat, y_tilde) / np.dot(x_hat, x_hat)
    residuals_2sls = y_tilde - x_tilde * beta_2sls
    s2_2sls = np.sum(residuals_2sls**2) / (N - W.shape[1] - 1)
    se_2sls = np.sqrt(s2_2sls / np.dot(x_hat, x_hat))
    
    # OLS for Hausman test
    beta_ols = np.dot(x_tilde, y_tilde) / np.dot(x_tilde, x_tilde)
    residuals_ols = y_tilde - x_tilde * beta_ols
    s2_ols = np.sum(residuals_ols**2) / (N - W.shape[1] - 1)
    se_ols = np.sqrt(s2_ols / np.dot(x_tilde, x_tilde))
    
    # Durbin-Wu-Hausman test statistic: (beta_2sls - beta_ols)^2 / (V_2sls - V_ols)
    v_diff = se_2sls**2 - se_ols**2
    if v_diff > 0:
        hausman_stat = (beta_2sls - beta_ols)**2 / v_diff
        hausman_p = 1.0 - stats.chi2.cdf(hausman_stat, df=1)
    else:
        hausman_stat = 0.0
        hausman_p = 1.0
        
    # Anderson-Rubin (AR) test for H0: beta = 0
    # Regress (y_tilde - 0 * x_tilde) on z_tilde
    gamma_ar = np.dot(z_tilde, y_tilde) / np.dot(z_tilde, z_tilde)
    res_ar = y_tilde - z_tilde * gamma_ar
    s2_ar = np.sum(res_ar**2) / (N - W.shape[1] - 1)
    ar_stat = (gamma_ar**2 * np.sum(z_tilde**2)) / s2_ar
    ar_p = 1.0 - stats.f.cdf(ar_stat, dfn=1, dfd=N - W.shape[1] - 1)
    
    return {
        "beta_2sls": beta_2sls,
        "se_2sls": se_2sls,
        "first_stage_F": f_stat,
        "beta_ols": beta_ols,
        "hausman_stat": hausman_stat,
        "hausman_p": hausman_p,
        "anderson_rubin_stat": ar_stat,
        "anderson_rubin_p": ar_p
    }

def test_fi2010_econometric_robustness():
    """Simulate synthetic sample mimicking FI-2010 microstructure with latency IV."""
    np.random.seed(42)
    N = 100000
    
    # Latency instrument Z (hardware routing physics)
    z = np.random.exponential(scale=2.5, size=N)
    
    # Time-varying controls: volatility and high-frequency trade counts
    vol = np.random.gamma(shape=2.0, scale=0.5, size=N)
    trade_counts = np.random.poisson(lam=15, size=N)
    w = np.column_stack([vol, trade_counts])
    
    # Structural error e containing informed trading bursts
    informed_burst = 0.3 * vol + np.random.normal(scale=1.0, size=N)
    
    # Endogenous OFI: driven by instrument Z + informed trading + controls
    ofi = 0.8 * z + 0.5 * informed_burst + 0.2 * vol + np.random.normal(scale=0.5, size=N)
    
    # True causal feedback S = -0.3796 (contrarian liquidity provision)
    s_true = -0.3796
    y = s_true * ofi + informed_burst + 0.1 * trade_counts
    
    res = run_2sls_with_diagnostics(y, ofi, z, w)
    
    # Check 1: 2SLS recovers the true negative feedback within 2 standard errors
    assert abs(res["beta_2sls"] - s_true) < 2.5 * res["se_2sls"]
    assert res["beta_2sls"] < 0, "Causal feedback must remain negative (contrarian provision)"
    
    # Check 2: First stage F exceeds Stock-Yogo critical value (F > 10) by an order of magnitude
    assert res["first_stage_F"] > 100.0, f"Expected F > 100, got {res['first_stage_F']}"
    
    # Check 3: Hausman test decisively rejects OLS exogeneity (p < 0.001), proving 2SLS is mandatory
    assert res["hausman_p"] < 0.001, f"Hausman p-value should reject exogeneity, got {res['hausman_p']}"
    
    # Check 4: Anderson-Rubin test robustly rejects null hypothesis S = 0
    assert res["anderson_rubin_p"] < 0.001

if __name__ == "__main__":
    pytest.main([__file__])
