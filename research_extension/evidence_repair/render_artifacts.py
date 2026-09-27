"""Generate corrected table/figure source from exact algebra and saved results."""
from fractions import Fraction as F
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research_extension/outputs/evidence_repair_20260926'


def exact_witness():
    rates = [F(1), F(1,2), F(1,20)]
    paths = []
    for weights in ([F(0), F(12,65), F(0)], [F(54,1235), F(0), F(240,247)]):
        k = [sum(q*e*(1-e)**j for q,e in zip(weights,rates)) for j in range(8)]
        h = [F(1), F(2,5)]
        for t in range(1,8):
            h.append(F(2,5)*h[t] + sum(k[j]*h[t-1-j] for j in range(t)))
        paths.append(h)
    return paths


def main():
    d = json.loads((OUT/'learned_agents_v2/results.json').read_text())
    rows = []
    for p in d['policies']:
        f,a = p['q_frozen'],p['q_active']
        rows.append(f"{p['policy_id']:02d} & {f['total_turnover']:.1f} & {f['mean_dislocation']:.6f} & {a['mean_dislocation']:.6f} & {p['active_minus_frozen']:+.6f} \\\\")
    table = r'''\begin{table}[htbp]
\centering\small
\caption{Corrective inventory-only experiment: ten independently trained policies, each averaged over the same ten shock tapes. All response audits abstain for insufficient recorded support; none certifies or falsifies a global model class. Displacement is mean absolute price deviation over 128 steps.}
\label{tab:q_learning_transfer}
\begin{tabular}{lrrrr}\toprule
Policy & Turnover & Frozen displacement & Active displacement & Active $-$ frozen\\\midrule
''' + '\n'.join(rows) + r'''
\bottomrule\end{tabular}
\end{table}
'''
    coordinates = ' '.join(f"({p['policy_id']},{p['active_minus_frozen']:.9f})" for p in d['policies'])
    figure = r'''\begin{figure}[htbp]\centering
\begin{tikzpicture}\begin{axis}[width=.86\textwidth,height=5cm,
xlabel={Independent training population},ylabel={Active minus frozen displacement},
xtick={1,2,3,4,5,6,7,8,9,10},grid=major]
\addplot[only marks,mark=*,blue] coordinates {''' + coordinates + r'''};
\addplot[black,dashed] coordinates {(1,0) (10,0)};
\end{axis}\end{tikzpicture}
\caption{Population-level corrective contrasts. Each point averages ten paired shock tapes; trades are not treated as independent replications. A negative value means less displacement with continued learning, not demonstrated welfare improvement.}
\label{fig:corrected_learning_effects}\end{figure}
'''
    artifact = {'table_tex': table, 'figure_tex': figure,
        'witness': [[{'exact':str(v),'decimal':float(v)} for v in h] for h in exact_witness()],
        'means': {arm: {key: float(np.mean([p[arm][key] for p in d['policies']]))
            for key in ('mean_dislocation','total_turnover','dealer_halted')} for arm in ('q_frozen','q_active','frequency_calibrated')},
        'max_cash_residual': max(r['max_cash_residual'] for r in d['raw_runs'])}
    empirical = json.loads((OUT/'empirical/final/coinbase_audit.json').read_text())
    erows = []
    for name, key in [('Saved rows','serialized_rows'), ('Frozen cache','frozen_cache')]:
        for spec,label in [('bivariate_F','bivariate'), ('full_model_F','controlled')]:
            r = empirical[key]['specifications'][spec]
            erows.append(f"{name}, {label} & {r['df']} & {r['beta'][1]:.6f} & {r['t_stats'][1]:.6f} & {r['p_values'][1]:.6f} & {r['r2']:.6f} \\\\")
    artifact['empirical_table_tex'] = r'''\begin{table}[htbp]\centering\small
\caption{Two distinct frozen samples, ten assets each. Conventional OLS statistics describe associations fitted using those same assets' Period-B outcomes; they are not out-of-sample forecast scores. Controlled specifications include spread and volatility.}
\label{tab:empirical_reg}
\begin{tabular}{lrrrrr}\toprule
Sample and specification & df & $F$ coefficient & $t$ & $p$ & $R^2$\\\midrule
''' + '\n'.join(erows) + r'''
\bottomrule\end{tabular}\end{table}
'''
    gate = json.loads((OUT/'gate24/final/gate24_analysis_results.json').read_text())
    grows, hrows = [], []
    for sym,g in gate['gate2_authenticated_boundary'].items():
        fit, hold = g['impact_proxy'], g['impact_proxy']['holdout']
        market = gate['gate4_calibrated_implementation'][sym]
        grows.append(f"{sym} & {fit['slope']:.7g} & {hold['r_squared']:.4f} & {g['lob_depth_authentication']['top5_bid_depth_units']:.5g} & {market['spectral_radius']:.6f} \\\\")
        for scenario in market['scenarios'].values():
            lo,hi = scenario['halt_rate_exact_95pct_ci']
            hrows.append(f"{sym} & ${100*scenario['shock_fraction']:.0f}\\%$ & {scenario['halts']}/{scenario['n_reps']} & $[{100*lo:.1f}\\%,{100*hi:.1f}\\%]$ & {scenario['mean_final_equity_quote']:.2f} \\\\")
    artifact['gate_table_tex'] = r'''\begin{table}[htbp]\centering\small
\caption{Corrected public-data proxies and synthetic local Jacobians. Impact units are USDT per squared base-asset unit. Depth is a separate REST snapshot, not historical dealer capacity. The $R^2$ is a held-out contemporaneous-flow fit, not a trading forecast.}
\label{tab:gate24_empirical}
\begin{tabular}{lrrrr}\toprule
Asset & Impact proxy & Holdout $R^2$ & Top-5 bid depth & Synthetic $\rho(J)$\\\midrule
''' + '\n'.join(grows) + r'''
\bottomrule\end{tabular}\end{table}
'''
    artifact['halt_table_tex'] = r'''\begin{table}[htbp]\centering\small
\caption{Corrected synthetic inventory-halt scenarios: 50 seeds per asset--shock cell, 64 steps, base snapshot-depth mapping. Exact 95\% binomial intervals refer to the specified simulator law, not exchange event probabilities. Equity is in USDT.}
\label{tab:gate4_shock_ci}
\begin{tabular}{lrrrr}\toprule
Asset & Shock & Halts/seeds & 95\% interval & Final dealer equity\\\midrule
''' + '\n'.join(hrows) + r'''
\bottomrule\end{tabular}\end{table}
'''
    (OUT/'paper_artifacts.json').write_text(json.dumps(artifact, indent=2, allow_nan=False))
    print(json.dumps({k:v for k,v in artifact.items() if not k.endswith('_tex')},indent=2))


if __name__ == '__main__':
    main()
