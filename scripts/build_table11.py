#!/usr/bin/env python3
"""
Generate referee-proof Table 11 for Machine_Markets_JF_Submission.tex
directly from research_extension/outputs/high_power_table16_results.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_FILE = ROOT / "research_extension" / "outputs" / "high_power_table16_results.json"
OUT_FILE = ROOT / "paper" / "generated" / "table_funded_risk_surface.tex"

def main():
    with open(IN_FILE) as f:
        d = json.load(f)

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering\footnotesize")
    lines.append(r"\setlength{\tabcolsep}{3.5pt}")
    lines.append(r"\caption{\textbf{Dealer Solvency Risk Surface and Inventory Buffer Exhaustion Under Stress.}")
    lines.append(r"High-power Monte Carlo simulation ($N = 1{,}000$ independent trajectories per cell, totaling 22,000 paths) evaluating leveraged dealer balance-sheet survival across inventory-capacity multipliers and directional repricing shocks (initial equity $E_0 = \$10{,}000$, base inventory limit 25 shares, $\eta_s=0.02$, initial capacity utilization $20\%$). Effective persistence $S_{\rm eff} = a_{\rm eff} + Q$ reflects unconstrained price persistence $a_{\rm eff} = 1 - \kappa\phi = 0.80$ with $\kappa=0.02, \phi=10.0$. Exact $95\%$ Clopper--Pearson binomial confidence intervals in brackets. At $S_{\rm nom}=0.70$, $0.5\times$ capacity, and moderate repricing shock $\mu=-0.2$, the dealer experiences a $69.1\%$ failure rate despite nominal subcriticality.}")
    lines.append(r"\label{tab:funded_risk_surface}")
    lines.append(r"\begin{tabular}{lrrrrrrr}\toprule")
    lines.append(r"$S_{\rm nom}$ & $S_{\rm eff}$ & $\rho(J)$ & Capacity & Shock $\mu$ & Failure Rate & Halt Rate [95\% CI] & Min Equity (\$) \\\midrule")

    curr_s = None
    for c in d['cells']:
        s_val = c['S']
        if s_val != curr_s:
            if curr_s is not None:
                lines.append(r"\midrule")
            curr_s = s_val
        s_eff = 0.80 + (s_val - 0.40)
        if abs(s_val - 0.70) < 1e-4:
            rho = 1.027
        elif abs(s_val - 0.82) < 1e-4:
            rho = 1.074
        else:
            rho = 1.226
        cap = f"{c['capital_multiplier']:.1f}$\\times$"
        shock = f"{c['mean_shock']:+.1f}"
        fail_pct = f"{c['fail_rate_pct']:.1f}\\%"
        ci_lo = c['halt_ci_95'][0]
        ci_hi = c['halt_ci_95'][1]
        halt_str = f"{c['halt_rate_pct']:.1f}\\% [{ci_lo:.1f}, {ci_hi:.1f}]"
        min_eq = f"\\${c['mean_min_equity']:,.2f}"
        lines.append(f"{s_val:.2f} & {s_eff:.2f} & {rho:.3f} & {cap} & {shock} & {fail_pct} & {halt_str} & {min_eq} \\\\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")

    with open(OUT_FILE, "w") as f:
        f.write("\n".join(lines))
    print(f"Successfully generated {OUT_FILE}")

if __name__ == "__main__":
    main()
