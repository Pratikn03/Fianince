#!/usr/bin/env python3
"""
Generates publication-quality canonical figures for the breakthrough research program:
- Figure 1: The Tri-Region Financial Identification Phase Diagram
- Figure 2: Probing Method Capital Cost Scaling (Theta(delta^{-4}) verification)
- Figure 3: Causal Multi-Agent Microstructure Intervention (Active vs Frozen vs Persistent)
- Figure 4: The Quantitative Value of Financial Disclosure Frontier (I0 to I5)
- Figure 5: Non-Normal Balance Sheet Decoupling & Multi-Asset Kreiss Inflation
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'lines.linewidth': 1.8
})

OUT_DIR = Path("breakthrough_experiments/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# Figure 1: The Tri-Region Financial Identification Phase Diagram
# -------------------------------------------------------------
def plot_fig1():
    with open("breakthrough_experiments/results_exp4_phase_diagram.json") as f:
        data = json.load(f)
        
    delta_min_t3 = data["parameters"]["delta_min_3rd_tap_approx"] # 0.2028
    delta_min_t20 = data["parameters"]["delta_min_T20"] # 0.0914
    
    curve_t20 = data["phase_diagram_T20_optimal"]["delta_curve"]
    curve_t3 = data["phase_diagram_T3_restricted"]["delta_curve"]
    
    deltas = np.array([d["delta"] for d in curve_t20])
    B_pulse_t20 = np.array([d["B_req_pulse"] for d in curve_t20])
    B_seq_t20 = np.array([d["B_req_sequential"] for d in curve_t20])
    B_seq_t3 = np.array([d["B_req_sequential"] for d in curve_t3])
    
    # Proved exact spectral lower bounds from Theorem IA.D.1 and IA.D.2
    # At delta=0.05: C*_det = 61.44 USDT, E[C*_adapt] = 30.09 USDT
    # Invariant constant: delta^4 * C*_det = 3.84e-4
    C_star_det = 3.84e-4 / (deltas ** 4)
    C_star_adapt = 0.4897 * C_star_det # 1.88e-4 / delta^4
    
    fig, ax = plt.subplots(figsize=(8.5, 6))
    
    # Plot boundaries
    ax.plot(deltas, B_pulse_t20, label=r'Single-Pulse Upper Bound ($T=20$)', color='darkblue', lw=2.0)
    ax.plot(deltas, B_seq_t20, label=r'Isolated-Pulse Upper Bound ($T=20$, $|v|\leq 6.25$)', color='darkorange', lw=2.0)
    ax.plot(deltas, B_seq_t3, label=r'Isolated-Pulse Baseline ($T=3$)', color='gray', lw=1.6, ls=':')
    ax.plot(deltas, C_star_det, label=r'Certified Deterministic Lower Bound $\underline{C}_{\mathrm{det}}(\delta)$ ($61.44$ at $\delta=0.05$)', color='crimson', lw=2.2)
    ax.plot(deltas, C_star_adapt, label=r'Adaptive Expected-Loss Lower Bound $\underline{C}_{\mathrm{adapt}}(\delta)$ ($30.09$ at $\delta=0.05$)', color='purple', lw=1.8, ls='-.')
    
    # Feasible non-pulse candidate point from Theorem IA.D.1 / Exp 14
    ax.scatter([0.05], [64.59], color='black', marker='*', s=160, zorder=6,
               label='Constructed Feasible Candidate (64.59 USDT at L=160; 65.05 at L=120)')
    
    # Vertical lines for physical depth limits
    ax.axvline(delta_min_t20, color='darkgreen', lw=1.6, ls='--', label=rf'Single-Pulse Floor $\delta_{{\min}}(20) = {delta_min_t20:.4f}$')
    ax.axvline(delta_min_t3, color='crimson', lw=1.6, ls='--', label=rf'Single-Pulse Floor $\delta_{{\min}}(3) = {delta_min_t3:.4f}$')
    
    # Fill Regions
    ax.fill_between(deltas, B_pulse_t20, 1e6, where=[d >= delta_min_t20 for d in deltas], color='green', alpha=0.10, label='Regime 1: Feasible Single-Pulse ($T=20$)')
    ax.fill_between(deltas, B_seq_t20, 1e6, where=[d < delta_min_t20 for d in deltas], color='orange', alpha=0.10, label='Regime 2: Feasible Sequential Isolated-Pulse')
    ax.fill_between(deltas, C_star_det, B_seq_t20, color='gold', alpha=0.10, label=r'Regime 3: Not Feasible with Tested Isolated Pulses ($T\leq 20$)')
    ax.fill_between(deltas, 1.0, C_star_det, color='red', alpha=0.12, label=r'Regime 4: Below Certified Deterministic Lower Bound $\underline{C}_{\mathrm{det}}(\delta)$')
    
    ax.set_yscale('log')
    ax.set_xlim(0.01, 0.25)
    ax.set_ylim(10.0, 1e6)
    ax.set_xlabel(r'Memory Separation Parameter $\delta$')
    ax.set_ylabel(r'Required Trader Capital $B$ (USDT, log scale)')
    ax.set_title('The Financial Identification Frontier: Multi-Observation Phase Diagram')
    ax.grid(True, which='both', ls='-', alpha=0.2)
    ax.legend(loc='upper right', frameon=True, fontsize=7.5)
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig1_phase_diagram.pdf")
    plt.savefig(OUT_DIR / "fig1_phase_diagram.png", dpi=300)
    plt.close()
    print("Figure 1 generated.")

# -------------------------------------------------------------
# Figure 2: Probing Method Capital Cost Scaling
# -------------------------------------------------------------
def plot_fig2():
    with open("breakthrough_experiments/results_exp3_adaptive_probing.json") as f:
        data = json.load(f)
        
    protocols = list(set([r["protocol"] for r in data]))
    
    fig, ax = plt.subplots(figsize=(7.5, 5))
    colors = {'Method_A_Single_Pulse': 'navy', 'Method_B_Multi_Pulse': 'crimson', 
              'Method_C_Sequential_Feedback': 'forestgreen', 'Method_D_Minimax_LQG': 'darkorange'}
    labels = {
        'Method_A_Single_Pulse': 'Method A: Unconstrained Single Pulse',
        'Method_B_Multi_Pulse': 'Method B: Repeated Capacity Pulses (|v_t| <= 6.25 BTC)',
        'Method_C_Sequential_Feedback': 'Method C: Sequential SPRT Stopping',
        'Method_D_Minimax_LQG': 'Method D: Predetermined Gen.-Eigenvector Trajectory'
    }
    
    for prot in protocols:
        sub = [r for r in data if r["protocol"] == prot]
        sub = sorted(sub, key=lambda x: x["delta"])
        deltas = [r["delta"] for r in sub]
        costs = [r["mean_capital_cost"] for r in sub]
        ax.plot(deltas, costs, marker='o', label=labels.get(prot, prot), color=colors.get(prot, 'black'))
        
    # Theoretical delta^{-4} slope reference
    ref_deltas = np.array([0.03, 0.12])
    ref_costs = 5000.0 * (0.03 / ref_deltas)**4
    ax.plot(ref_deltas, ref_costs, 'k--', alpha=0.5, label=r'Theoretical $\Theta(\delta^{-4})$ Reference')
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'Separation $\delta$ (log scale)')
    ax.set_ylabel(r'Probing Capital Cost $\mathcal{C}$ (USDT, log scale)')
    ax.set_title(r'Observed Capital Scaling Across Evaluated Probing Protocols ($\delta \in [0.03, 0.12]$)')
    ax.grid(True, which='both', ls='-', alpha=0.2)
    ax.legend(frameon=True, fontsize=8)
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig2_probing_cost_scaling.pdf")
    plt.savefig(OUT_DIR / "fig2_probing_cost_scaling.png", dpi=300)
    plt.close()
    print("Figure 2 generated.")

# -------------------------------------------------------------
# Figure 3: Causal Multi-Agent Policy-Freeze Intervention
# -------------------------------------------------------------
def plot_fig3():
    with open("breakthrough_experiments/results_exp10_multi_agent.json") as f:
        full = json.load(f)
        data = full["conditions_summary"]
        causal = full["causal_intervention"]
        
    conds = ["P0_Baseline", "P2_Frozen_Policy", "P2_Active_Learning", "P1_Persistent_Flow"]
    labels = ["P0 Baseline\n(Noise Traders)", "P2 Frozen\n(Static Policy)", "P2 Active\n(Online Learning)", "P1 Persistent\n(TWAP Splitting)"]
    drawdowns = [data[c]["mean_dealer_drawdown"] for c in conds]
    errs = [data[c]["std_dealer_drawdown"] for c in conds]
    liq_rates = [data[c]["liquidation_rate"] * 100.0 for c in conds]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    
    # Left: Dealer Drawdown
    colors = ['gray', 'royalblue', 'darkblue', 'crimson']
    bars1 = ax1.bar(labels, drawdowns, yerr=errs, capsize=5, color=colors, alpha=0.85, edgecolor='black')
    ax1.set_ylabel('Mean Dealer Drawdown (USDT)')
    ax1.set_title('Intervention Impact on Dealer Drawdown')
    ax1.grid(True, axis='y', ls='--', alpha=0.3)
    ax1.set_ylim(0, max(drawdowns) * 1.35)
    
    # Dynamic annotation
    af_diff = causal["active_minus_frozen_drawdown_mean"]
    af_t = causal["active_minus_frozen_t_stat"]
    ax1.text(0.5, 0.88, f"Active vs Frozen Policy:\n+{af_diff:.2f} USDT (t = {af_t:.2f})",
             transform=ax1.transAxes, ha='center', fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1.0))
             
    # Right: Liquidation Rate
    bars2 = ax2.bar(labels, liq_rates, color=colors, alpha=0.85, edgecolor='black')
    ax2.set_ylabel('Dealer Liquidation Rate (%)')
    ax2.set_title('Forced Liquidation Frequency (Binance MMR)')
    ax2.set_ylim(0, 100)
    ax2.grid(True, axis='y', ls='--', alpha=0.3)
    
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig3_causal_multi_agent.pdf")
    plt.savefig(OUT_DIR / "fig3_causal_multi_agent.png", dpi=300)
    plt.close()
    print("Figure 3 generated.")

# -------------------------------------------------------------
# Figure 4: The Quantitative Value of Financial Disclosure Frontier
# -------------------------------------------------------------
def plot_fig4():
    with open("breakthrough_experiments/results_exp7_disclosure_value.json") as f:
        data = json.load(f)
        
    d5 = data["delta_0.05"]
    c_names = ["I0 (T=3)", "I0* (T=20)", "I1 Flow", "I2 (vs T=3)", "I2* (vs T=20)", "I3 CME Std", "I3 Micro", "I3* Binance", "I3 0.01 tick", "I4 (no model)", "I5 Audit"]
    keys = ["I0_Prices_Only_Restricted_T3", "I0_Prices_Only_Optimal_T20", "I1_Prices_and_Flow", "I2_Noisy_Equity_T3", "I2_Noisy_Equity_T20", 
            "I3_Exact_Equity_CME_Std_5BTC", "I3_Exact_Equity_CME_Micro_0_1BTC", "I3_Exact_Equity_Binance_minNotional", "I3_Exact_Equity_Cent_Rounded", "I4_Timestamps_Event_Study", "I5_Supervisory_Audit"]
    
    caps = [max(0.01, d5[k]["required_capital_B"]) for k in keys]
    vols = [d5[k]["required_volume_V"] for k in keys]
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    x = np.arange(len(c_names))
    width = 0.38
    
    color1 = 'navy'
    bars1 = ax1.bar(x - width/2, caps, width, label='Benchmark Capital B (USDT)', color=color1, alpha=0.85, edgecolor='black')
    ax1.set_ylabel('Required Capital B (USDT, log scale)', color=color1)
    ax1.set_yscale('log')
    ax1.set_ylim(0.005, 1e5)
    ax1.tick_params(axis='y', labelcolor=color1)
    
    ax2 = ax1.twinx()
    color2 = 'darkorange'
    bars2 = ax2.bar(x + width/2, vols, width, label='Required Executed Volume V', color=color2, alpha=0.85, edgecolor='black')
    ax2.set_ylabel('Required Executed Volume V', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(c_names, rotation=15, ha='right')
    ax1.set_title(r'Disclosure contracts at $\delta = 0.05$ (I2: independent reports; I3: noiseless unless rounded)')
    ax1.grid(True, axis='y', ls='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig4_disclosure_frontier.pdf")
    plt.savefig(OUT_DIR / "fig4_disclosure_frontier.png", dpi=300)
    plt.close()
    print("Figure 4 generated.")

# -------------------------------------------------------------
# Figure 5: Non-Normal Decoupling & Multi-Asset Kreiss Inflation
# -------------------------------------------------------------
def plot_fig5():
    with open("breakthrough_experiments/results_exp12_nonnormal_balance_sheet.json") as f:
        data = json.load(f)
        
    net_data = data["multi_asset_network"]
    M_vals = [r["assets_M"] for r in net_data]
    kreiss = [r["kreiss_constant"] for r in net_data]
    rho_vals = [r["spectral_radius"] for r in net_data]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # Left: Decoupling Bar Chart
    labels = ['Price Output\nC = [1, 0]', 'Weighted (price, memory)\nC = [1, 160] (not a margin)']
    gains = [1.0, 160.003]
    colors = ['steelblue', 'crimson']
    
    bars = ax1.bar(labels, gains, color=colors, alpha=0.85, edgecolor='black', width=0.5)
    ax1.set_ylabel('Peak Transient Amplification Gain $M_C$')
    ax1.set_title('Coordinate-weighted operator gain (no holdings in state)')
    ax1.grid(True, axis='y', ls='--', alpha=0.3)
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 3, f"{yval:.1f}x", ha='center', va='bottom', fontsize=10, fontweight='bold')
        
    # Right: Multi-Asset Cross-Impact Coupling
    ax2.plot(M_vals, kreiss, marker='s', color='darkred', lw=2.2, label=r'Kreiss Constant $\mathcal{K}(J) = 1.00$ (Lower Bound)')
    ax2.plot(M_vals, rho_vals, marker='o', color='navy', lw=2.0, ls='--', label=r'Network Spectral Radius $\rho(J_{\mathrm{network}}) \to 1.0$')
    ax2.set_xlabel('Number of Cross-Impacted Assets $M$')
    ax2.set_ylabel('Stability & Resolvent Metrics')
    ax2.set_title(r'Cross-Impact Network Spectral Inflation ($\mathcal{K}(J) \equiv 1.00$)')
    ax2.grid(True, ls='--', alpha=0.3)
    ax2.legend(frameon=True)
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig5_nonnormal_decoupling.pdf")
    plt.savefig(OUT_DIR / "fig5_nonnormal_decoupling.png", dpi=300)
    plt.close()
    print("Figure 5 generated.")

if __name__ == "__main__":
    plot_fig1()
    plot_fig2()
    plot_fig3()
    plot_fig4()
    plot_fig5()
    print("All 5 breakthrough figures generated successfully.")
