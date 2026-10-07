"""Generate manuscript content from the new joint fit, never preset results."""
from pathlib import Path
import json,numpy as np
HERE=Path(__file__).resolve().parent

def table(cap,columns,header,rows,label):
 return '\n\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+cap+'}\\label{'+label+'}\n\\begin{adjustbox}{max width=\\textwidth}\n\\begin{tabular}{'+columns+'}\\toprule\n'+header+r'\\\midrule'+'\n'+'\n'.join(' & '.join(map(str,r))+r'\\' for r in rows)+'\n\\bottomrule\\end{tabular}\n\\end{adjustbox}\n\\end{table}\n'

def build():
 d=json.loads((HERE/'joint_results.json').read_text());m=json.loads((HERE/'restoration_manifest.json').read_text());legacy=json.loads((HERE/'legacy_overlap_reproduction.json').read_text())
 assert len(m['rows'])==33 and all(r['status']=='VERIFIED_ORIGINAL_SAMPLE_RESTORED' for r in m['rows'])
 assert len(legacy['results'])==3 and all(r['all_baseline_metrics_match'] for r in legacy['results'])
 s=r'''
\section{Restored Joint-Venue Study}
\label{sec:restored_joint}
The original separate-venue generator did not establish its reported joint matrix or FEVD. That contradiction remains in the audit. A subsequent recovery retrieved the exact original study's Binance BTCUSDT, ETHUSDT and ADAUSDT daily one-second kline objects for April 8--18, 2021: thirty-three exchange archives, each verified against a newly retrieved official checksum and its ZIP CRC. These are current public archives for the original sample dates, not byte-authenticated copies of the original downloads. Three recovered April 10 asset-days reproduce every saved baseline coefficient, invariant, observation count and mean price exactly. Full original-panel recovery and reproduction are recorded separately; this three-row overlap comparison alone does not close that full-panel gate.

The new independent joint study joins the three recorder caches to restored exchange observations. Binance supplies transaction closes and signed quote flow $2V^{\rm buy}-V^{\rm total}$, rather than order-book midpoints. Coinbase supplies recorded midpoint and deduplicated flow, with provider authentication still open. Quote currencies differ (USD and USDT); basis movements and common information can affect the relation. The two timestamp conventions do not establish subsecond simultaneity. We retain integer-second offset sensitivities of minus and plus one second for the recorder.

Ten-second bins require all ten integer-second records from both venues. Incomplete bins are excluded; neither series is filled from future observations. Gaps and UTC date changes reset both filters together, followed by a 150-bin burn-in. Segments require at least 500 retained bins. A four-variable VAR with separate segment intercepts is fit to the within-segment centered observations. The ordered state is recorder price deviation, recorder flow, Binance price deviation, Binance flow. Each variable is divided by its retained-sample standard deviation for estimation; the saved fit also supplies the raw-unit matrix and covariance. The filtered state uses a 300-second EMA; a raw-return variant measures a different estimand.
'''
 rows=[]
 for a,r in d['assets'].items():
  for k,label in [('primary','EMA, offset 0'),('raw_return','Return, offset 0'),('cb_offset_minus1','EMA, offset -1s'),('cb_offset_plus1','EMA, offset +1s')]:
   v=r['variants'][k]['fit'];rows.append([a,label,v['n_transitions'],v['n_segments'],f"{v['rho']:.6f}"])
 s+=table('Joint fits from restored original overlap. Radii describe fitted reduced-form dynamics, not fundamental stability.','llrrr',r'Asset & State / clock & Transitions & Segments & $\rho$',rows,'tab:joint_fit_recovered')
 s+=r'''
For horizon $H$, with $\Psi_k=J^k$ and residual covariance $\Sigma$, the generalized decomposition \citep{pesaran1998} is
\[
\theta_{ij}(H)=\frac{\Sigma_{jj}^{-1}\sum_{k=0}^{H-1}(e_i^\top\Psi_k\Sigma e_j)^2}{\sum_{k=0}^{H-1} e_i^\top\Psi_k\Sigma\Psi_k^\top e_i}.
\]
With correlated innovations, these raw generalized shares need not sum to one. We report $\widetilde\theta_{ij}=\theta_{ij}/\sum_j\theta_{ij}$ as an explicitly chosen row normalization, retain raw shares in the output, and do not interpret their directional difference as identified net causality. We also calculate orthogonal decompositions under all twenty-four variable orderings. Six fitted steps are sixty seconds. The matrix, full residual covariance, responses, and every horizon use the same saved joint fit.
'''
 rows=[]
 for a,r in d['assets'].items():
  v=r['variants']['primary']['decomposition']['horizons']['6'];p=np.array(v['generalized_row_normalized']);lo=np.array(v['orthogonal_order_min']);hi=np.array(v['orthogonal_order_max'])
  rows.append([a,f'{100*p[0,2]:.2f}',f'[{100*lo[0,2]:.2f}, {100*hi[0,2]:.2f}]',f'{100*p[2,0]:.2f}',f'[{100*lo[2,0]:.2f}, {100*hi[2,0]:.2f}]'])
 s+=table('Sixty-second cross-price predictive decomposition, percentages. Ordering ranges are sensitivity ranges, not confidence intervals.','lrrrr',r'Asset & BN to CB & Order range & CB to BN & Order range',rows,'tab:joint_fevd_recovered')
 s+=r'''
The ordering ranges are broad. Contemporaneously correlated innovations can produce cross-price shares even without a directed lag channel. These calculations establish a reproducible joint descriptive study; they do not identify a structural information shock, eliminate common news, or validate the old untraced percentages. Date-resampling with 200 draws is supplied as exploratory variation under an exchangeable-date assumption, not as a small-sample causal guarantee. Residual lag correlations are retained; fitting a stable matrix does not establish model adequacy. The raw-return and clock-offset fits remain visible rather than selecting a preferred result.
'''
 rows=[]
 for a,r in d['assets'].items():
  fit=r['variants']['primary']['fit']
  for key,label in [('J_normalized','$J$'),('covariance_normalized','$\\Sigma$')]:
   for i,row in enumerate(fit[key]):rows.append([a,label,i+1]+[f'{x:.6f}' for x in row])
 s+=table('Full-precision fits are saved digitally; displayed normalized matrices round to six decimals. Row/column order is CB price, CB flow, BN price, BN flow.','llrrrrr',r'Asset & Matrix & Row & CB price & CB flow & BN price & BN flow',rows,'tab:joint_matrices_recovered')
 return s
if __name__=='__main__':
 (HERE/'joint_appendix.tex').write_text(build());print('Generated joint appendix')
