#!/usr/bin/env python3
"""
Phase 4 / Priority 7: Quantitative Value of Financial Disclosure
Quantifies how financial disclosures (I0 to I5) substitute for costly active probing.
Derives exact measurement channel Fisher information and optimizes required volume V and capital B
to achieve statistical identification error alpha <= 0.05 under each contract.

Clarifies:
- Benchmark Public Prices: Reports savings against both the restricted T=3 baseline and the optimal T=20 transient design.
- Concrete exchange filter rules: CME 5 BTC standard and 0.1 BTC micro contracts vs Binance USD(S)-M linear minNotional (0.05 BTC / 5 USDT).
- Exact joint likelihoods for prices, signed order flow, marked equity, and event study windows.
"""
import json
import math
from pathlib import Path
import numpy as np
from scipy.stats import norm

def get_mean_trajectories(delta, T=20, kappa=0.8, q=0.2, a=0.5, eta=0.4):
    """Computes price and order flow trajectories under H0 and H1 for unit pulse."""
    rates_0 = np.array([eta]); weights_0 = np.array([q])
    rates_1 = np.array([eta - delta, eta + delta]); weights_1 = np.array([q / 2.0, q / 2.0])
    
    x0 = np.zeros(T + 1); y0 = np.zeros((1, T + 1))
    x1 = np.zeros(T + 1); y1 = np.zeros((2, T + 1))
    u0 = np.zeros(T); u1 = np.zeros(T)
    
    for t in range(T):
        u0[t] = np.sum(weights_0 * y0[:, t])
        u1[t] = np.sum(weights_1 * y1[:, t])
        v = 1.0 if t == 0 else 0.0
        x0[t + 1] = a * x0[t] + kappa * u0[t] + kappa * v
        x1[t + 1] = a * x1[t] + kappa * u1[t] + kappa * v
        y0[:, t + 1] = (1.0 - rates_0) * y0[:, t] + rates_0 * x0[t + 1]
        y1[:, t + 1] = (1.0 - rates_1) * y1[:, t] + rates_1 * x1[t + 1]
        
    diff_x = x1[1:] - x0[1:]
    diff_u = u1 - u0
    return diff_x, diff_u

def solve_contract_requirements(delta, alpha=0.05):
    z_alpha = norm.ppf(1.0 - alpha) # ~1.64485
    target_kl = 2.0 * (z_alpha ** 2) # ~5.4114
    kappa = 0.8                     # price impact
    q = 0.2                         # feedback intensity
    a = 0.5                         # dealer decay
    eta = 0.4                       # base adaptation rate
    mu = 0.005                      # Binance MMR (0.50%)
    c_fee = 0.0004                  # Binance taker fee (4 bps)
    P_star = 100.0                  # index price
    V_eff = 6.25                    # effective displacement cap
    
    # Noise parameters
    sigma_p = 0.01                  # price observation noise
    sigma_q = 0.05                  # order flow observation noise
    sigma_E_noisy = 0.50            # periodic accounting statement noise
    
    # Trajectories over full transient horizon T=20
    diff_x_20, diff_u_20 = get_mean_trajectories(delta, T=20, kappa=kappa, q=q, a=a, eta=eta)
    energy_p_20 = float(np.sum(diff_x_20 ** 2))
    energy_u_20 = float(np.sum(diff_u_20 ** 2))
    
    # 3rd-tap trajectory alone (T=3)
    diff_x_3rd = float(diff_x_20[2])
    energy_p_3rd = diff_x_3rd ** 2
    
    # ---------------------------------------------------------
    # Contract I0: Public Prices Only
    # ---------------------------------------------------------
    # (A) Restricted Baseline (T=3):
    kl_pulse_I0_T3 = (V_eff**2 * energy_p_3rd) / (2.0 * sigma_p**2)
    N_I0_T3 = int(math.ceil(target_kl / kl_pulse_I0_T3))
    B_I0_T3 = float(N_I0_T3 * (0.5 * kappa * (V_eff**2) + c_fee * P_star * V_eff) + mu * P_star * V_eff)
    V_I0_T3 = float(N_I0_T3 * V_eff)
    
    # (B) Optimal Full Transient Baseline (T=20):
    kl_pulse_I0_T20 = (V_eff**2 * energy_p_20) / (2.0 * sigma_p**2)
    N_I0_T20 = int(math.ceil(target_kl / kl_pulse_I0_T20))
    B_I0_T20 = float(N_I0_T20 * (0.5 * kappa * (V_eff**2) + c_fee * P_star * V_eff) + mu * P_star * V_eff)
    V_I0_T20 = float(N_I0_T20 * V_eff)
    
    # ---------------------------------------------------------
    # Contract I1: Prices + Signed Order Flow
    # Joint Fisher info: I_total = I_price + I_flow
    # ---------------------------------------------------------
    info_per_pulse_I1 = (V_eff**2) * (energy_p_20 / (sigma_p**2) + energy_u_20 / (sigma_q**2))
    kl_pulse_I1 = info_per_pulse_I1 / 2.0
    N_I1 = int(math.ceil(target_kl / kl_pulse_I1))
    B_I1 = float(N_I1 * (0.5 * kappa * (V_eff**2) + c_fee * P_star * V_eff) + mu * P_star * V_eff)
    V_I1 = float(N_I1 * V_eff)
    
    # ---------------------------------------------------------
    # Contract I2: Prices + Noisy Marked Equity Disclosure (Proposition 2.8)
    # Observation model (stated explicitly): after EACH reset j = 1..N the observer
    # receives one report E_j = E_j^0 + dE + e_j, e_j ~ N(0, sigma_E^2) iid, independent of
    # price noise, where dE = kappa^2 q delta^2 V^2 is the mark difference of the
    # probe position at the third observation. Independent Gaussian reports add KL linearly:
    #     D_equity(N) = N dE^2 / (2 sigma_E^2).
    # The earlier code used (N dE)^2 / (2 sigma_E^2), i.e. a single report whose
    # signal grows with N. That corresponds to an unmodelled cumulative statement and
    # is NOT implied by the reset experiment; it is retained only as a diagnostic.
    # ---------------------------------------------------------
    dE = kappa**2 * q * (delta**2) * (V_eff**2)
    kl_E_per_report = dE**2 / (2.0 * sigma_E_noisy**2)

    def n_required(kl_price_per_pulse, kl_equity_per_report):
        return int(math.ceil(target_kl / (kl_price_per_pulse + kl_equity_per_report)))

    def err_from_kl(kl_total):
        return float(norm.cdf(-math.sqrt(kl_total / 2.0)))

    N_I2_T3 = n_required(kl_pulse_I0_T3, kl_E_per_report)
    B_I2_T3 = float(N_I2_T3 * (0.5 * kappa * (V_eff**2) + c_fee * P_star * V_eff) + mu * P_star * V_eff)
    V_I2_T3 = float(N_I2_T3 * V_eff)

    N_I2_T20 = n_required(kl_pulse_I0_T20, kl_E_per_report)
    B_I2_T20 = float(N_I2_T20 * (0.5 * kappa * (V_eff**2) + c_fee * P_star * V_eff) + mu * P_star * V_eff)
    V_I2_T20 = float(N_I2_T20 * V_eff)

    # Diagnostic: the withdrawn quadratic-accumulation design and its true error
    N_I2_T3_withdrawn = next(n for n in range(1, 5000)
                             if n * kl_pulse_I0_T3 + (n * dE)**2 / (2.0 * sigma_E_noisy**2) >= target_kl)
    err_withdrawn_true = err_from_kl(N_I2_T3_withdrawn * (kl_pulse_I0_T3 + kl_E_per_report))

    # ---------------------------------------------------------
    # Contract I3: Exact Account Equity Disclosure (Proposition 2.8)
    # Theoretical infimum is inf C = 0 (as V -> 0) ONLY under noiseless,
    # infinite-precision reporting. If reports are rounded to a tick of 0.01 USDT,
    # a difference is guaranteed to change the report only if |dE| >= tick:
    #     V >= sqrt(tick / (kappa^2 q delta^2)).
    # ---------------------------------------------------------
    report_tick = 0.01
    V_I3_tick_guarantee = float(math.sqrt(report_tick / (kappa**2 * q * delta**2)))
    B_I3_tick_guarantee = float(0.5 * kappa * V_I3_tick_guarantee**2 + (c_fee + mu) * P_star * V_I3_tick_guarantee)
    # Specification A: CME Standard Bitcoin Futures (5.0 BTC contract size)
    V_I3_CME_Std = 5.0
    B_I3_CME_Std = float(0.5 * kappa * (V_I3_CME_Std**2) + (c_fee + mu) * P_star * V_I3_CME_Std) # 12.70 USDT
    
    # Specification B: CME Micro Bitcoin Futures (0.1 BTC contract size)
    V_I3_CME_Micro = 0.1
    B_I3_CME_Micro = float(0.5 * kappa * (V_I3_CME_Micro**2) + (c_fee + mu) * P_star * V_I3_CME_Micro) # 0.058 USDT
    
    # Specification C: Binance USD(S)-M linear minNotional (5.0 USDT threshold -> 0.05 BTC at P*=100)
    V_I3_Binance = 0.05
    B_I3_Binance = float(0.5 * kappa * (V_I3_Binance**2) + (c_fee + mu) * P_star * V_I3_Binance) # 0.028 USDT
    
    # ---------------------------------------------------------
    # Contract I4: Algorithmic Update Timestamps
    # The previous version multiplied price information by (z_search / z_alpha)^2 ~ 7.32,
    # a multiple-testing correction. That correction is not information: the price-only
    # benchmark already knows the timing of its own controlled probes and never paid a
    # search penalty. No timestamp observation with a hypothesis-dependent likelihood is
    # defined in this model, so the timestamp contract carries zero additional KL here.
    # A positive value of timestamps requires a separately specified timestamp likelihood
    # (e.g. update times whose law differs between H0 and H1); not modelled -> no saving claimed.
    # ---------------------------------------------------------
    N_I4 = N_I0_T20
    B_I4 = B_I0_T20
    V_I4 = V_I0_T20
    N_I4_withdrawn = 2
    err_I4_withdrawn_true = err_from_kl(N_I4_withdrawn * kl_pulse_I0_T20)
    
    # ---------------------------------------------------------
    # Contract I5: Supervisory Algorithmic Tagging / Full Audit Trail
    # Regulator directly inspects code/weights; zero probing needed
    # ---------------------------------------------------------
    N_I5 = 0
    V_I5 = 0.0
    B_I5 = 0.0
    
    return {
        "I0_Prices_Only_Restricted_T3": {
            "required_volume_V": V_I0_T3,
            "required_capital_B": B_I0_T3,
            "sequential_n_pulses": N_I0_T3,
            "disclosure_type": "Public Prices Only (Restricted T=3 Baseline)"
        },
        "I0_Prices_Only_Optimal_T20": {
            "required_volume_V": V_I0_T20,
            "required_capital_B": B_I0_T20,
            "sequential_n_pulses": N_I0_T20,
            "disclosure_type": "Public Prices Only (Optimal T=20 Transient)"
        },
        "I1_Prices_and_Flow": {
            "required_volume_V": V_I1,
            "required_capital_B": B_I1,
            "sequential_n_pulses": N_I1,
            "disclosure_type": "Public Flow Records"
        },
        "I2_Noisy_Equity_T3": {
            "required_volume_V": V_I2_T3,
            "required_capital_B": B_I2_T3,
            "sequential_n_pulses": N_I2_T3,
            "observation_model": "one independent N(0, sigma_E^2) equity report per reset; KL adds linearly",
            "withdrawn_quadratic_design_n_pulses": N_I2_T3_withdrawn,
            "withdrawn_quadratic_design_true_error": err_withdrawn_true,
            "disclosure_type": "Periodic Statements, independent per-reset reports (vs. T=3 single-tap)"
        },
        "I2_Noisy_Equity_T20": {
            "required_volume_V": V_I2_T20,
            "required_capital_B": B_I2_T20,
            "sequential_n_pulses": N_I2_T20,
            "observation_model": "one independent N(0, sigma_E^2) equity report per reset; KL adds linearly",
            "disclosure_type": "Periodic Statements, independent per-reset reports (vs. T=20 transient)"
        },
        "I3_Exact_Equity_CME_Std_5BTC": {
            "required_volume_V": V_I3_CME_Std,
            "required_capital_B": B_I3_CME_Std,
            "sequential_n_pulses": 1,
            "assumption": "noiseless, infinite-precision equity report",
            "disclosure_type": "Exact Account Reporting (CME 5 BTC Standard Lot)"
        },
        "I3_Exact_Equity_CME_Micro_0_1BTC": {
            "required_volume_V": V_I3_CME_Micro,
            "required_capital_B": B_I3_CME_Micro,
            "sequential_n_pulses": 1,
            "assumption": "noiseless, infinite-precision equity report",
            "disclosure_type": "Exact Account Reporting (CME 0.1 BTC Micro Lot)"
        },
        "I3_Exact_Equity_Binance_minNotional": {
            "required_volume_V": V_I3_Binance,
            "required_capital_B": B_I3_Binance,
            "sequential_n_pulses": 1,
            "theoretical_infimum_capital": 0.0,
            "assumption": "noiseless, infinite-precision equity report",
            "disclosure_type": "Exact Account Reporting (Binance 5 USDT minNotional)"
        },
        "I3_Exact_Equity_Cent_Rounded": {
            "report_tick_usdt": report_tick,
            "required_volume_V": V_I3_tick_guarantee,
            "required_capital_B": B_I3_tick_guarantee,
            "sequential_n_pulses": 1,
            "assumption": "noiseless report rounded to 0.01 USDT; |dE| >= tick guarantees a changed report",
            "disclosure_type": "Exact Account Reporting with 0.01 USDT reporting precision"
        },
        "I4_Timestamps_Event_Study": {
            "required_volume_V": V_I4,
            "required_capital_B": B_I4,
            "sequential_n_pulses": N_I4,
            "observation_model": "no hypothesis-dependent timestamp likelihood defined; zero added information",
            "withdrawn_multiplier_design_n_pulses": N_I4_withdrawn,
            "withdrawn_multiplier_design_true_error": err_I4_withdrawn_true,
            "disclosure_type": "Known Update Timestamps (no saving established)"
        },
        "I5_Supervisory_Audit": {
            "required_volume_V": V_I5,
            "required_capital_B": B_I5,
            "sequential_n_pulses": N_I5,
            "disclosure_type": "Direct Supervisory Audit Trail"
        }
    }

def run_experiment():
    deltas = [0.03, 0.05, 0.08, 0.12]
    all_results = {}
    for delta in deltas:
        res = solve_contract_requirements(delta)
        all_results[f"delta_{delta:.2f}"] = res
        
    out_file = Path("breakthrough_experiments/results_exp7_disclosure_value.json")
    out_file.write_text(json.dumps(all_results, indent=2))
    print(f"Disclosure value experiment complete. Results written to {out_file}")
    
    # Print comparison at delta = 0.05
    d05 = all_results["delta_0.05"]
    print("\n--- Value of Disclosure at delta = 0.05 ---")
    print(f"I0 (Prices Only, T=3 baseline):   Capital = {d05['I0_Prices_Only_Restricted_T3']['required_capital_B']:8.2f} USDT (N={d05['I0_Prices_Only_Restricted_T3']['sequential_n_pulses']})")
    print(f"I0 (Prices Only, T=20 optimal):   Capital = {d05['I0_Prices_Only_Optimal_T20']['required_capital_B']:8.2f} USDT (N={d05['I0_Prices_Only_Optimal_T20']['sequential_n_pulses']})")
    print(f"I1 (Prices + Order Flow):         Capital = {d05['I1_Prices_and_Flow']['required_capital_B']:8.2f} USDT (N={d05['I1_Prices_and_Flow']['sequential_n_pulses']})")
    print(f"I2 (Noisy Equity vs T=3 baseline):Capital = {d05['I2_Noisy_Equity_T3']['required_capital_B']:8.2f} USDT (N={d05['I2_Noisy_Equity_T3']['sequential_n_pulses']})")
    print(f"I2 (Noisy Equity vs T=20 baseline):Capital = {d05['I2_Noisy_Equity_T20']['required_capital_B']:8.2f} USDT (N={d05['I2_Noisy_Equity_T20']['sequential_n_pulses']})")
    print(f"I3 (Exact Equity, CME 5 BTC Std): Capital = {d05['I3_Exact_Equity_CME_Std_5BTC']['required_capital_B']:8.2f} USDT")
    print(f"I3 (Exact Equity, CME 0.1 BTC Mic):Capital = {d05['I3_Exact_Equity_CME_Micro_0_1BTC']['required_capital_B']:8.4f} USDT")
    print(f"I3 (Exact Equity, Binance 5USDT): Capital = {d05['I3_Exact_Equity_Binance_minNotional']['required_capital_B']:8.4f} USDT")
    print(f"I4 (Known Timestamps Event Study):Capital = {d05['I4_Timestamps_Event_Study']['required_capital_B']:8.2f} USDT (N={d05['I4_Timestamps_Event_Study']['sequential_n_pulses']})")
    print(f"I5 (Supervisory Audit Trail):     Capital = {d05['I5_Supervisory_Audit']['required_capital_B']:8.2f} USDT (N=0)")

if __name__ == "__main__":
    run_experiment()
