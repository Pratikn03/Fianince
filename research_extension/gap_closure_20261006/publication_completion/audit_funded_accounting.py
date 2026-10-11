"""Independent replay/accounting audit of the existing 22-cell funded experiment.

Also fixes inventory projection in a separately labelled sensitivity; never
changes historical outputs or calls a capacity event bankruptcy.
"""
from pathlib import Path
import json
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def path(shocks,S,cap,repricing,projection):
    Q=S-.4;limit=25*cap;I=.2*limit;cash=10000-I*100;E=10000.;price=100.;x=0.;yf=ys=.05
    hit=False;default=False;minE=E;dd=False;resid=0.;margin=False;negative_price=False
    for t,shock in enumerate(shocks):
        oldI=I;oldE=E;oldP=price
        if t==16:x+=repricing
        desired=(.6*Q*yf+.4*Q*ys)/.02-10*x+shock
        wanted=I-desired
        if abs(wanted)>limit:
            hit=True
            if projection:actual=I-np.clip(wanted,-limit,limit)
            else:actual=max(0,limit-abs(I))*np.sign(desired)
        else:actual=desired
        xnext=x+.02*actual;price=100+xnext
        I-=actual;cash+=actual*price;E=cash+I*price
        expected=oldE+oldI*(price-oldP)
        resid=max(resid,abs(E-expected));negative_price|=price<=0
        default|=E<=0;minE=min(minE,E);dd|=E<.8*10000
        margin|=abs(I*price)>.0 and E/(abs(I*price))<.25
        yf=.5*yf+.5*xnext;ys=.98*ys+.02*xnext;x=xnext
    return dict(halt=hit,default=default,drawdown=dd,margin=margin,min_equity=minE,
                max_accounting_residual=resid,nonpositive_price=negative_price)

def run():
    saved=json.loads((HERE/'high_power_table16_results.json').read_text());out={}
    for projection in [False,True]:
        rng=np.random.default_rng(20260924);rows=[]
        for r in saved['cells']:
            runs=[path(rng.normal(0,.05,64),r['S'],r['capital_multiplier'],r['mean_shock'],projection) for _ in range(1000)]
            d=dict(S=r['S'],capacity=r['capital_multiplier'],shock=r['mean_shock'],
                halt_count=int(sum(x['halt'] for x in runs)),default_count=int(sum(x['default'] for x in runs)),
                   margin_path_count=int(sum(x['margin'] for x in runs)),drawdown_count=int(sum(x['drawdown'] for x in runs)),
                   mean_min_equity=float(np.mean([x['min_equity'] for x in runs])),
                   max_accounting_residual=max(x['max_accounting_residual'] for x in runs),
                   nonpositive_price_count=int(sum(x['nonpositive_price'] for x in runs)))
            if not projection:
                assert d['halt_count']==r['halt_count']
                assert d['default_count']==r['default_count']
                assert np.isclose(d['mean_min_equity'],r['mean_min_equity'],atol=1e-8,rtol=0)
            rows.append(d)
        out['projected_inventory' if projection else 'independent_legacy_replay']=rows
    out['scope']='Existing fixed-parameter constructed scenario, fills at post-impact price, no spreads/fees/funding. Independent cash identity checked; corrected projection sensitivity separately labelled. Not actual exposure/fill calibration.'
    (HERE/'funded_accounting_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Independent22-cell accounting replay and projection sensitivity passed')
    print('Max residual',max(r['max_accounting_residual'] for r in out['independent_legacy_replay']))
    print('Changed hit counts',sum(x['halt_count']!=y['halt_count'] for x,y in zip(out['independent_legacy_replay'],out['projected_inventory'])))

if __name__=='__main__':run()
