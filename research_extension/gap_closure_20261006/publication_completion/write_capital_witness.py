"""Constructed numerical illustration of exact known-pair resource/capital contracts."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from capital_frontier import positive_cohort_model,robust_quantity_cap,account
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PARAMS=dict(anchor=.5,impact=.8,total_weight=.2,rate=.4,observation_sd=.003,
            reference_price=100.,margin=.25,cost=.02,execution_fraction=.5,alpha=.1,horizon=200)
def response(split):
 p=PARAMS;weights=[p['total_weight']] if split==0 else [p['total_weight']/2]*2
 rates=[p['rate']] if split==0 else [p['rate']-split,p['rate']+split]
 J,H,C=positive_cohort_model(p['anchor'],p['impact'],weights,rates);h=[];z=H.copy()
 for _ in range(p['horizon']):h.append(float(C@z));z=J@z
 return np.array(h)
def run():
 p=PARAMS;original=response(0);curve=[];z=stats.norm.ppf(1-p['alpha'])
 for d in np.geomspace(.005,.15,50):
  diff=response(d)-original;gain=float(np.linalg.norm(diff));V=2*p['observation_sd']*z/gain
  B=(1+p['margin']-p['execution_fraction'])*p['impact']*V*V+(p['cost']+p['margin']*p['reference_price'])*V
  # Verify actual account at the optimal pulse, not just the algebraic budget.
  J,H,C=positive_cohort_model(p['anchor'],p['impact'],[p['total_weight']/2]*2,[p['rate']-d,p['rate']+d])
  path=account(J,H,C,np.r_[V,np.zeros(p['horizon']-1)],B,p['reference_price'],p['cost'])
  assert min(r['equity']-p['margin']*abs(r['inventory'])*r['price'] for r in path)>-1e-6*max(1,B)
  assert np.isclose(robust_quantity_cap(B,p['impact'],p['margin'],p['reference_price'],p['cost']),V)
  curve.append(dict(delta=float(d),impulse_difference_norm= gain,quantity_for_alpha=V,capital_inside_robust_quantity_contract=B))
 time=[];d=.05;norms=np.sqrt(np.cumsum((response(d)-original)**2))
 for B in [100.,1000.]:
  cap=robust_quantity_cap(B,p['impact'],p['margin'],p['reference_price'],p['cost'])
  errors=stats.norm.cdf(-cap*norms/(2*p['observation_sd']))
  time.append(dict(capital=B,quantity_cap=cap,worst_error=errors.tolist()))
 capital=np.geomspace(.1,1e6,100);caps=[robust_quantity_cap(B,p['impact'],p['margin'],p['reference_price'],p['cost']) for B in capital]
 fig,axes=plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
 for t in time:axes[0].plot(np.arange(1,p['horizon']+1),t['worst_error'],label=f"Capital {t['capital']:g}")
 axes[0].set(title='(a) Waiting at fixed capital',xlabel='Model observations',ylabel='Exact known-pair error',ylim=(0,.51));axes[0].legend(fontsize=8)
 axes[1].loglog(capital,caps);axes[1].set(title='(b) Counterparty margin cap',xlabel='Counterparty initial capital',ylabel='Robust probe quantity')
 axes[2].loglog([v['delta'] for v in curve],[v['capital_inside_robust_quantity_contract'] for v in curve]);axes[2].set(title='(c) Resolving closer memories',xlabel='Rate separation delta',ylabel='Counterparty capital for error 0.1')
 plot=ROOT/'paper/figures/fig_capital_information_20261008.pdf';fig.savefig(plot);plt.close(fig)
 data=dict(scope='Constructed maintained linear model and imposed fill/margin convention; not empirical market calibration. Exact finite-horizon known-pair likelihood, no process noise. Capital requirement refers to robust quantity-ball contract, not every safe strategy.',params=p,
           capital_error_time=time,separation_curve=curve,capital_grid=capital.tolist(),quantity_caps=caps,plot_sha256=hashlib.sha256(plot.read_bytes()).hexdigest())
 (HERE/'capital_witness.json').write_text(json.dumps(data,indent=2)+'\n')
 print('Constructed exact capital/information witness generated')
if __name__=='__main__':run()
