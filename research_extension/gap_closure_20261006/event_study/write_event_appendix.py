from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def longtable(caption,columns,header,rows,label,size="small"):
    return '\n{\\'+size+'\n\\begin{longtable}{'+columns+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n'+r'\toprule '+header+r'\\\midrule\endfirsthead'+'\n'+r'\toprule '+header+r'\\\midrule\endhead'+'\n'+r'\bottomrule\endfoot'+'\n'+'\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\end{longtable}'+'\n}\n'

def build():
    d=json.loads((HERE/'event_results.json').read_text());s=r'''
\section{Reconstructed Monthly Fee-Event Analysis}
\label{sec:monthly_event_rebuilt}
The original date-gap builder's pooled standard error multiplied by $\sqrt2$ does not supply a monthly event-specific covariance. We reconstruct the monthly question from the raw-reproduced original 2022 panel, separating the legacy forward-flow and corrected observed-flow diagnostics. The sample has eight assets on twenty-four dates, two per calendar month. Treatment begins July 8, between the last June and first July observations. June is the calendar-month reference: January through December have event months $-6,\ldots,-1,0,\ldots,5$. This differs from subtracting the June 24 date alone.

The fitted design has an intercept, seven asset effects, twenty-three sampled-date effects and eleven BTC-by-month interactions: rank forty-two and 150 residual degrees of freedom in 192 observations. Point coefficients independently equal the monthly BTC-minus-seven-control gap minus the June gap. The January--May joint reference tests five restrictions. We retain classical, HC1, HC3, asset-cluster and date-cluster covariance calculations; cluster small-sample corrections and reference degrees of freedom are explicit. These are declared approximations with one treated asset, not defended causal assignment or guaranteed sampling coverage.

Clustering at the calendar-month level exposes saturation. Let $g_m$ be the BTC-minus-control monthly mean gap. The coefficient is $g_m-g_{\rm June}$. Normal equations make each treated month's residual sum zero, and date effects make aggregate control residual means zero. The cluster influence of each gap contrast is therefore zero in a month-clustered sandwich. The resulting degenerate covariance does not mean the effect has no uncertainty. A date-saturated design similarly perfectly fits the sole treated observation per date and degenerates under date clustering; HC3 also fails at its unit-leverage observations. These failures are explicitly flagged rather than used to print precise intervals or extreme $F$ statistics.

The following joint-test table retains every covariance choice, including unavailable references. Corrected $Q$ rejects under the date-cluster approximation, while classical and HC3 references do not. Legacy $S$ also changes conclusion sharply across references. Thus the earlier untraced $F=0.42,p=0.835$ does not establish parallel counterfactual trends; neither a newly computed nonsignificant result nor one selected significant reference can resolve this identification problem. Concurrent fee/volume rules, spillovers and outcome construction remain material.
'''
    rows=[];labels={'classical':'Classical','HC1':'HC1','HC3':'HC3','asset_cluster':'Asset','date_cluster':'Date','month_cluster':'Month'}
    for variant,r in d['variants'].items():
        for outcome,study in r['monthly'].items():
            for kind,fit in study['fits'].items():
                v=fit['pretrend_joint_test'];rows.append([variant.capitalize(),outcome,labels[kind],str(v['df_denominator']) if v['df_denominator'] is not None else '--',f"{v['F']:.4f}" if v['F'] is not None else '--',f"{v['p_F']:.4g}" if v['p_F'] is not None else '--','Degenerate' if v['F'] is None else 'Reference'])
    s+=longtable('January--May joint tests relative to June. Month-cluster event covariance is degenerate; the other references retain their stated assumptions.','lllrrrl',r'State & Outcome & Covariance & df & $F$ & $p$ & Status',rows,'tab:event_pretrend_rebuilt')
    s+=r'''
The complete monthly coefficient table uses date-cluster uncertainty for its displayed intervals and supplies classical, HC3 and asset-cluster standard errors for comparison. HC1 results and all covariance matrices are saved digitally. Intervals are covariance/reference-specific diagnostics; the few-cluster and serial-dependence limitations remain even when matrix arithmetic is correct. A different comparison clock or reference period changes the coefficient, not just its label.
'''
    rows=[]
    for variant,r in d['variants'].items():
        for outcome,study in r['monthly'].items():
            for v in study['contrasts']:
                ref=v['references'];date=ref['date_cluster'];lo,hi=date['ci95']
                rows.append([variant.capitalize(),outcome,v['event_month'],f"{date['beta']:.7f}",f"{ref['classical']['se']:.7f}",f"{ref['HC3']['se']:.7f}",f"{ref['asset_cluster']['se']:.7f}",f"[{lo:.7f}, {hi:.7f}]"])
    s+=longtable('All monthly coefficients and covariance contrasts. June is omitted by construction; displayed intervals use date-cluster $t_{23}$ references.','llrrrrrl',r'State & $Y$ & Month & Effect & Classical SE & HC3 SE & Asset SE & Date interval',rows,'tab:event_monthly_rebuilt',size='footnotesize')
    s+='This reconstruction closes the numerical monthly-design/covariance gap. The inference cannot by itself establish that fees caused a learning response, that the effect is zero, or that counterfactual trends are parallel. The original descriptive date-gap ledger remains as a different reference construction; it is not assigned these monthly errors.\n'
    return s
if __name__=='__main__':(HERE/'event_appendix.tex').write_text(build());print('Generated reconstructed monthly appendix')
