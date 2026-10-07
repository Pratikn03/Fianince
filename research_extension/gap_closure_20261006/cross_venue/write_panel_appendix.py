"""Generate restored full-panel evidence from actual verified outputs."""
from pathlib import Path
import json
from write_joint_appendix import table
HERE=Path(__file__).resolve().parent

def interval(v):return f"{v['mean']:.6f} [{v['date_t95'][0]:.6f}, {v['date_t95'][1]:.6f}]"
def build():
 d=json.loads((HERE/'restored_panel_summary.json').read_text())
 assert d['n_asset_days']==768
 s='\n\\section{Raw Reproduction of the Original Binance Panel}\n\\label{sec:restored_panel}\n'
 s+=f"All 768 original asset-day inputs are now restored from current official exchange archives, with their checksums and ZIP CRC verified. They contain {d['n_raw_rows']:,} CSV rows and {d['n_unique_seconds']:,} unique seconds; the legacy filled fits contain {d['n_legacy_states']:,} states. The corrected observed-time analysis retains {d['n_primary_transitions']:,} transitions in {d['n_primary_segments']} contiguous segments. Every saved baseline coefficient, invariant, mean price, state count, and flow-controlled coefficient is reproduced within the stated numerical tolerance. The legacy loop ratio is independently recomputed from its defining identity. The old covariance-matching and heteroskedastic structural interpretations are not certified by these numerical matches. Original download-time hashes were not preserved; the receipt anchors the current official input snapshot.\n\n"
 s+='Across the original dates, 38,859 seconds are missing and 363 timestamp records are exact duplicates, concentrated on December 24, 2021 and March 24, 2023. No conflicting duplicate values were found. The legacy forward-fill and zero-flow substitution are retained only to reconstruct the saved calculations. Corrected bins require ten recorded seconds, reset at gaps and dates, and exclude five EMA spans after each reset. Segment estimates are combined within dates using transition counts. The resulting estimand differs from the legacy forward-flow alignment.\n\n'
 rows=[]
 for key,label in [('legacy','Legacy EMA / forward'),('observed','EMA / observed'),('raw_return','Return / observed')]:
  v=d['summaries'][key];rows.append([label,interval(v['Q']),interval(v['Q30']) if key!='raw_return' else '--',f"{v['S']['mean']:.6f}",f"{100*v['share_Q_positive']:.2f}",f"{v['max_rho']:.6f}"])
 s+=table('Full original panel, three measurement constructions. Intervals describe variation across 96 date means; positive-share percentages count asset-days.','llllrr',r'Construction & $Q$ [date interval] & $Q_{30}$ [date interval] & Mean $S$ & Positive $Q$ (\%) & Max $\rho$',rows,'tab:restored_panel_comparison')
 s+='Corrected observed-flow feedback is much smaller than its reproduced legacy counterpart. Raw-return intervals span zero. Circular date-block bootstrap sensitivities with block lengths two, four and eight sampled dates are retained in the digital results; they do not establish stationarity, serial independence or causal learning. The sign share is not a participant-attribution statistic.\n\n'
 rows=[]
 for a,v in d['summaries']['observed']['by_asset'].items():
  rv=d['summaries']['raw_return']['by_asset'][a];rows.append([a,f"{v['Q']:.7f}",f"{v['Q30']:.7f}",f"{rv['Q']:.7f}",f"{v['S']:.6f}"])
 s+=table('All eight assets under corrected observed-flow timing, with raw-return comparison. These are reduced-form diagnostic means, not identified learning gains.','lrrrr',r'Asset & Observed $Q$ & Observed $Q_{30}$ & Return $Q$ & Observed $S$',rows,'tab:restored_panel_assets')
 fee=d['fee_observed'];rows=[]
 for dep in ['Q','S']:
  for key,label in [('classical','Classical'),('asset_cluster','Asset clusters, $t_7$'),('date_cluster','Date clusters, $t_{23}$')]:
   v=fee[dep][key];rows.append([dep,label,f"{v['beta']:.7f}",f"{v['se']:.7f}",f"{v['p_t']:.4f}",f"[{v['ci95'][0]:.7f}, {v['ci95'][1]:.7f}]"])
 s+=table('Fee-period association recalculated on the raw-reproduced, corrected observed-flow panel. Reference covariance assumptions remain fragile with one treated asset.','llrrrr',r'Outcome & Covariance & Effect & SE & $p$ & 95\% interval',rows,'tab:restored_panel_fee')
 volume=fee['measured_btc_quote_volume'];s+=f"The original sampled-day BTCUSDT quote-volume mean rises from {volume['pre_sampled_day_mean']:,.2f} before the fee change to {volume['post_sampled_day_mean']:,.2f} after it, a measured {volume['percentage_change']:.2f}\\% change in the recovered representation, rather than the old uncomputed 180\\% literal. This is a descriptive comparison of the original sampled dates; price levels, market trends, bundled incentives and spillovers prevent a fee-induced volume interpretation.\n\n"
 s+=f"At the inherited illustrative equivalence margin $\\pm0.007$, the corrected diagnostic's date-cluster TOST gives $p={fee['Q']['equivalence_date_cluster']['p_tost']:.3g}$. This margin is over eighteen times the corrected mean $Q$, so passing that reference test is not evidence of economically small effects or no causal response. The date-cluster effect interval remains compatible with changes large relative to the corrected baseline. The legacy estimator's failed equivalence test concerns a different measurement construction and remains visible.\n"
 return s
if __name__=='__main__':(HERE/'panel_appendix.tex').write_text(build());print('Generated raw-panel appendix')
