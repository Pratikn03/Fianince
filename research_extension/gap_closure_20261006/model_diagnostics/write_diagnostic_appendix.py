"""Render all fixed diagnostic cases and honest identifying-assumption limits."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def longtable(caption,columns,header,rows,label):
    return '\n{\\small\n\\begin{longtable}{'+columns+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n'+r'\toprule '+header+r'\\\midrule\endfirsthead'+'\n'+r'\toprule '+header+r'\\\midrule\endhead'+'\n'+r'\bottomrule\endfoot'+'\n'+'\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\end{longtable}'+'\n}\n'

def build():
    md=json.loads((HERE/'covariance_complete.json').read_text());prediction=json.loads((HERE/'predictive_results.json').read_text())
    s=r'''
\section{Diagnosing the Maintained Linear Approximation}
\label{sec:model_diagnostic_audit}
The original covariance rejection is examined rather than repaired by choosing a passing specification. We retain four fixed HAC bandwidths (5, 10, 20 and 40 bins) and six optimizer starts for each asset/bandwidth. An independent parameterization covers the stable two-state transition with an unrestricted positive-definite innovation covariance. Let $\Gamma_0\succ0$ be arbitrary and let $K=M(I+M^\top M)^{-1/2}$ for unrestricted $M\in\mathbb R^{2\times2}$. Set
\[
J=\Gamma_0^{1/2}K\Gamma_0^{-1/2},\qquad
\Sigma=\Gamma_0^{1/2}(I-KK^\top)\Gamma_0^{1/2}.
\]
This ensures $\Sigma\succ0$, $\rho(J)<1$ and $\Gamma_0=J\Gamma_0J^\top+\Sigma$. Conversely, the stationary covariance of any stable $J$ with $\Sigma\succ0$ supplies such a strict contraction, so the parameterization removes unnecessary entrywise bounds. Its eleven moment restrictions and seven local parameter directions retain four overidentifying degrees of freedom. The weighting rank is eleven and the parameter Jacobian rank seven in all reported cases. The six starts agree numerically, without constituting a certified global optimization proof. All twenty-four global/within-segment centering cases reject under their asymptotic reference. Within-segment demeaning changes the maintained mean model and can introduce finite-segment estimation effects; it is retained as a sensitivity, not a selected replacement. Changing these computational bounds does not rescue the maintained covariance model.
'''
    rows=[]
    for asset,r in md['assets'].items():
        for key,v in r['cases'].items():rows.append([asset,'Global' if v['centering']=='global' else 'Segment',v['bandwidth_bins'],v['n_rows'],f"{v['J_stat']:.4f}",f"{v['p_chi2']:.4g}"])
    s+=longtable('Independent full-class covariance audit. All fixed bandwidth cases are retained; the chi-square reference is asymptotic.','llrrrr',r'Asset & Centering & HAC bins & Moment rows & $J$ & Reference $p$',rows,'tab:covariance_audit_complete')
    s+=r'''
\subsection{Retrospective Whole-Date Forecast Comparisons}
We next compare a mechanical EMA-anchor forecast (or zero-return forecast), separately fitted autoregressions, and joint VARs at fixed lags $p\in\{1,2,3,6\}$. The mechanical forecast has a training-only intercept and a training mean for flow. The alternatives and scoring protocol were fixed before this run, after prior exploration of these data; this is not an untouched holdout or external preregistration. Six initial dates train the first expanding-window fit. Subsequent entire dates supply one-step evaluations; all models use the same rows after six within-segment history bins. Training-only means, scales and coefficients prevent future-fit normalization. Lags do not bridge gaps or dates.

The previously reported recorder EMA continues across contiguous UTC dates while its lag products are split by date; it resets at data gaps. The restored joint and original-panel studies reset both filters at gaps and UTC dates. These constructions are explicitly distinguished rather than retroactively changing the old estimates. A price--flow VAR can improve prediction through order splitting, common news or measurement structure; improvement is not identified adaptation.

The complete table reports price and flow comparisons for every fixed lag and construction. Improvement is $100(\overline L_{\rm AR}-\overline L_{\rm VAR})/\overline L_{\rm AR}$ using training-scale squared loss, averaged equally across held dates. The displayed interval concerns the paired normalized-loss difference, not percentage improvement. Only seven recorder dates and five joint dates are evaluated. Date-$t$ intervals are exploratory and do not address multiple comparisons or establish serial independence. Negative improvements and unfavorable dates remain visible. Companion radii, residual correlations, physical-unit RMSE and every fold are saved digitally.
'''
    rows=[];labels={'coinbase_ema_observed':'Recorder EMA','coinbase_return_observed':'Recorder return','joint_ema_observed':'Joint EMA'}
    target_labels={'price':'Price','flow':'Flow','coinbase_price':'CB price','coinbase_flow':'CB flow','binance_price':'BN price','binance_flow':'BN flow'}
    for asset,data in prediction['assets'].items():
        for construction,r in data.items():
            for p,v in r['summary']['paired'].items():
                for target,entry in v['variables'].items():
                    lo,hi=entry['date_t95'];rows.append([asset,labels[construction],target_labels[target],p,v['n_dates'],f"{entry['relative_mean_improvement_percent']:.3f}",f"[{lo:.6f}, {hi:.6f}]"])
    s+=longtable('Every fixed AR-versus-VAR forecast comparison. Positive values favor VAR, negative values favor separate AR; intervals are paired normalized-loss differences.','lllrrrl',r'Asset & State & Target & Lag & Dates & Gain (\%) & $\Delta L$ date interval',rows,'tab:forecast_audit_complete')
    s+=r'''
For recorder EMA price forecasts, VAR(1) improves mean squared loss only modestly relative to AR(1). Price-loss intervals include zero across all fixed price comparisons. Joint price forecasts can deteriorate substantially for ETH and ADA. Additional lags do not turn the rejected two-state covariance restrictions into a structural learning model. These results identify limitations of this approximation; they do not prove that markets lack all adaptive trading.

\subsection{Heteroskedastic Identification Requires More Than Covariance Fitting}
The inspected C2 generator applies an unweighted covariance fit to price differences and legacy forward-aligned flow, rather than innovations from a defended dynamic reduced form. Its rolling price volatility includes the contemporaneous state and backward-fills initialization; regimes use pooled state-dependent quantiles. Conditional shock orthogonality, constant slopes and distinct structural variance profiles are assumptions, not consequences of those operations \citep{rigobon2003identification}. A bounded optimizer with one starting point supplies neither a causal interpretation nor uncertainty.

An exact algebraic example shows why shock labels matter. Let
\[
A=\begin{bmatrix}1&-\lambda\\-\alpha&1\end{bmatrix},\qquad
\Omega_r=A^{-1}\mathrm{diag}(v_{p,r},v_{f,r})A^{-\top}.
\]
Swapping and rescaling the structural equations yields another normalized matrix with $\lambda'=1/\alpha$ and $\alpha'=1/\lambda$, and transformed diagonal variances. It produces exactly the same regime covariances. The retained witness has $\lambda=1/20$, $\alpha=-3/20$, product $-3/400$, and an alternative product $-400/3$ under three nonproportional variance regimes. Bounds on the two slopes implicitly exclude this alternative; they are not independently authenticated shock labels. External sign or exclusion information could distinguish branches, but that information must be defended.

A separate bounded Gaussian illustration starts with independent structural errors and partitions observations using the contemporaneous reduced-form price. Conditional errors become correlated within the selected regimes. This demonstrates that endogenous selection can violate the needed restriction even when unconditional errors are orthogonal. It does not estimate actual market shock correlations. Reopening causal identification requires a stated innovation equation, valid timing, defended conditional orthogonality/invariance and shock labels, plus uncertainty and adequacy checks. The current archive does not establish market-maker buffering from its negative fitted product.
'''
    return s
if __name__=='__main__':(HERE/'diagnostic_appendix.tex').write_text(build());print('Generated all-case diagnostic appendix')
