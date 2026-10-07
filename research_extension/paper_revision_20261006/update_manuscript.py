"""Generate the revised selected manuscript from the recorded source baseline.

All new empirical tables are populated from revision outputs. Historical evidence
is labeled separately; untraceable tables are withdrawn rather than re-created.
"""
from pathlib import Path
import hashlib
import json
import re

REV=Path(__file__).resolve().parent
ROOT=REV.parents[1]
TARGET=ROOT/'paper/Machine_Markets_JF_Submission.tex'


def load(name):return json.loads((REV/'results'/f'{name}.json').read_text())
def fmt(x,n=5):return f'{x:.{n}f}'
def ci(v):return f"{v['mean']:.5f} [{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]"
def table(caption,columns,header,rows,label):
    return ('\n\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\n\\label{'+label+'}\n'
            '\\begin{adjustbox}{max width=\\textwidth}\n\\begin{tabular}{'+columns+'}\\toprule\n'+header+' \\\\\\midrule\n'
            +'\n'.join(' & '.join(str(v) for v in row)+' \\\\' for row in rows)
            +'\n\\bottomrule\\end{tabular}\n\\end{adjustbox}\n\\end{table}\n')


INTRO=r'''
\section{Introduction}
\label{sec:intro}
Electronic trading creates a feedback channel when price changes affect subsequent orders and those orders affect later prices. The existence of this channel does not identify its participant-level source: aggregate flow can reflect adaptive algorithms, order splitting, liquidity provision, or common information. Nor does decay of price disturbances establish that a dealer's loss budget will remain intact. This paper separates these identification and financial-risk questions.

Our central question is: \emph{what can observable aggregate data establish about feedback, and what additional assumptions are required to turn dynamic stability into a financially meaningful loss bound?} We combine a linear adaptive-memory model with an audit of observable-state definitions and timing, followed by controlled loss-exposure illustrations. The empirical analysis is deliberately reduced-form. It does not identify artificial-intelligence trading, individual learning rules, or a causal market-maker response from anonymous records.

\paragraph{Conditional identification results.}
Within a reset linear cohort model with known price-impact and anchor parameters, price responses identify merged rate--weight measures rather than the number or identity of cohorts sharing a rate. For a uniformly stable compact family of symmetric split alternatives, bounded-power deterministic probes with Gaussian observation noise face a separation lower bound of order $\delta^{-4}$. This is a lower bound for the stated experiment, not an attained universal rate for all passive market data. A separate scalar Gaussian price-surveillance experiment gives an explicit finite-window abstention bound near its unit-root boundary. The observation experiment matters: the scalar result is not asserted for noiselessly observed latent cohort states.

\paragraph{Measurement sensitivity.}
The primary empirical reanalysis uses recorded Coinbase BTC, ETH, and ADA book snapshots and signed executed flow from April 7--19, 2021. A 300-second EMA price deviation is estimated on 10-second bins with only end-bin observed flow. Mean reduced-form feedback is approximately $0.00194$, $0.00098$, and $0.00062$, respectively. Forward-bin flow alignment produces larger estimates, while raw-return specifications have feedback intervals spanning zero. These comparisons establish that measurement and timing materially affect the feedback diagnostic. They do not establish an algorithmic learning mechanism.

The preserved Binance panel supplies a secondary analysis of 768 saved asset-day estimates, derived from trade-price klines rather than historical full order books. Its legacy forward-flow estimator has mean $\hat Q\simeq0.00815$. The initial cache audit lacked those raw inputs. Section~\ref{sec:restored_panel} now restores all 768 original asset-days from checksum-verified official archives, reproduces the saved core estimates, and reports corrected observed-flow diagnostics separately. Original download-time hashes were not preserved. The legacy July 2022 fee contrast has a date-clustered effect interval spanning both signs and fails the inherited equivalence reference. Corrected observed-time results in Section~\ref{sec:restored_panel} have a different scale; a wide inherited margin cannot establish economic equivalence. The contradictory old joint-venue numbers and unsupported event-study inference are withdrawn. A subsequent independent reconstruction of the original April overlap supplies a joint VAR and ordering-sensitive predictive decompositions in Section~\ref{sec:restored_joint}.

\paragraph{Financially meaningful stability.}
For fixed economically specified state coordinates, loss operator $C$, and initial-shock set, the exact loss-budget radius is $B/\sup_{t\ge0}\|CJ^t\|_2$. The underlying transient-growth mechanism is established in operator theory; our financial use is the explicit mapping from a declared disturbance set to a declared budget. A fixed-spectrum numerical illustration separates transient magnification from eigenvalue decay. A distinct funded-dealer simulation shows persistent-flow accumulation and retains an exogenous benchmark matched on long-run variance. Simulation outcomes are conditional on their accounting and calibration, not measurements of actual dealer insolvency.

\subsection{Related Literature and Contribution Boundaries}
Classical microstructure studies price formation, information and order flow \citep{kyle1985,glosten1985,hasbrouck1991}. Order splitting and book imbalance can create persistent relations without identifying an adaptive trader \citep{bouchaud2004fluctuations,cont2014}. Funding constraints and inventory exposure connect market liquidity to intermediary fragility \citep{brunnermeier2009,adrian2010,greenwood2015}.

The realization and transient-growth tools used here build on existing control and numerical analysis \citep{gilbert1963,kreiss1962,spijker1991,trefethen2005spectra}. Non-normal financial-network amplification is not a first-use claim: Wang, Sornette, Wu and Lera's 2024 working paper studies evolving influence networks and subcritical financial instabilities \citep{wang2024}. Singular mixture models also have assumption-dependent identification rates \citep{manole2022}; our symmetric probing experiment is a specific dynamical testing problem rather than a universal new estimation rate. Our scope differs by specifying an output loss budget, a cohort-response observation experiment, and sensitivity of measured price--flow feedback to timing and filtering. We do not claim novelty for the general distinction between asymptotic decay and transient growth, or an independently certified priority for the full framework.

\subsection{Evidence Organization}
Section~\ref{sec:model} states the conditional model results. Section~\ref{sec:data_estimand} defines actual measurements and their timing. Section~\ref{sec:baseline_natural_exp} reports fresh observable-state diagnostics and clearly separated saved-panel evidence. Section~\ref{sec:stress_fragility} examines dimensional stress regression and model-based loss exposure. Section~\ref{sec:attribution_falsification} states attribution and replication limits. Section~\ref{sec:policy_conclusion} discusses conditional surveillance implications and concludes.

'''


ABSTENTION=r'''
\subsection{Theorem 2: A Finite-Window Price-Surveillance Bound}
The following experiment isolates a statistical boundary under passive price observations. Its parameter $s$ is the scalar transition coefficient, distinct from the algebraic index $S=a+Q$ of a general multivariate market. Applying the result to a hidden multivariate market requires a valid observation-law reduction; no such reduction is inferred solely from a common unit-root boundary.

\begin{theorem}[Finite-Window Abstention in a Scalar Gaussian Experiment]
\label{thm:m3_minimax_abstention}
Observe $\mathcal D_T=(x_1,\ldots,x_T)$ where $x_0=0$ and $x_t=sx_{t-1}+w_t$, $w_t\sim\mathcal N(0,\sigma^2)$ independently, $\sigma>0$, and $s\in(0,2)$. Let a possibly randomized rule $\Psi$ take values Stable, Unstable, or Abstain, with
\[
\sup_{s<1}P_s(\Psi=\mathrm{Unstable})\le\alpha,
\qquad \sup_{s\ge1}P_s(\Psi=\mathrm{Stable})\le\alpha,
\quad 0<\alpha<1/2.
\]
Choose $0<c_0<1$ with $c_0e^{c_0}/(2\sqrt2)<1-2\alpha$. For every integer $T\ge1$, on $\mathcal B_T=(1-c_0/T,1+c_0/T)$,
\begin{equation}
\inf_{s\in\mathcal B_T}P_s(\Psi=\mathrm{Abstain})
\ge1-2\alpha-\frac{c_0e^{c_0}}{2\sqrt2}>0.
\label{eq:abstain_bound}
\end{equation}
For every finite $T$, the minimax worst-case error of binary rules across $s\in(0,2)$ is at least $1/2$.
\end{theorem}
\begin{proof}
Pair any $s_0\in(1-c_0/T,1)$ with $s_1=s_0+c_0/T\in(1,1+c_0/T)$; reverse the pairing for a point on the other side, including $s_1=1$. Gaussian transition densities give
\[
D_{\rm KL}(P_{s_0}\|P_{s_1})
=\frac{(s_1-s_0)^2}{2\sigma^2}\sum_{t=1}^T E_{s_0}x_{t-1}^2.
\]
For either paired coefficient, $|s|\le1+c_0/T$ and
$E_sx_{t-1}^2=\sigma^2\sum_{j=0}^{t-2}s^{2j}\le\sigma^2(t-1)e^{2c_0}$.
Thus the KL divergence in either direction is at most $c_0^2e^{2c_0}/4$ and Pinsker's inequality bounds total variation by $c_0e^{c_0}/(2\sqrt2)$. Error control gives $P_{s_0}(\mathrm{Unstable})\le\alpha$ and $P_{s_0}(\mathrm{Stable})\le P_{s_1}(\mathrm{Stable})+\mathrm{TV}\le\alpha+\mathrm{TV}$, yielding the stated abstention bound. The reverse pairing is identical.

For binary rules, the Gaussian path densities are continuous in $s$ in total variation at each finite $T$. Let $s^-\uparrow1$ and $s^+\downarrow1$. Le Cam's two-point bound gives worst-case error at least $(1-\|P_{s^-}-P_{s^+}\|_{\rm TV})/2\to1/2$. This is a worst-case statement over arbitrarily close alternatives; it is not a 50\% error claim at every fixed separated parameter.
\end{proof}

The theorem forces a positive probability of withholding a classification under the specified uniform error guarantee. It does not require abstention on every sample path. Initial conditions, extra measurements, and observation noise can change the inference problem. In particular, a fully observed noiseless cohort recursion need not admit the common Lebesgue densities assumed by an informal reduction to a scalar price likelihood. Proposition~\ref{prop:exact_audited_contract} gives a constructive two-step identification result under an exact single-cohort state/demand contract, resolving that case explicitly.

'''


def empirical_text():
    cb=load('coinbase_reanalysis');null=load('mechanical_nulls');md=load('md_reanalysis')
    panel=load('saved_panel_audit');fee=load('fee_reanalysis');eq=load('equity_reanalysis');grid=load('sampling_grid')
    depth=load('depth_reanalysis');stress=load('threshold_reanalysis');dealer=load('dealer_reproduction');trans=load('transient_checks')
    text=r'''
\section{Data, Measurements, and the Observable Estimand}
\label{sec:data_estimand}
\subsection{Observed Price Proxies and Flow}
The theoretical state $x_t=p_t-p_t^*$ is not observed in these datasets. For the primary Coinbase analysis we use $p_b=10{,}000\log(P_b)$, where $P_b$ is the recorded bid--ask midpoint at the end of a 10-second bin, and an operational reference $m_b=(1-\alpha)m_{b-1}+\alpha p_b$, $\alpha=2/(300/10+1)$. The empirical state is $x_b^{\rm EMA}=p_b-m_b$. It is a deviation from a trailing filter, not a measured fundamental pricing error. A separate robustness state is the raw return $r_b=p_b-p_{b-1}$.

Signed executed flow $f_b$ is the recorded taker-buy minus taker-sell quote-currency notional aggregated in bin $b$. Repeated renders of the same book/trade record receive zero new flow following the recorded correction protocol. Price and flow both refer to information observed by the bin's end. Existing source timestamps and rolling trade counters only provide the recorder's timing resolution; they do not establish exchange-level execution latency.

\subsection{A Reduced-Form Diagnostic}
For an observable state $v_b\in\{x_b^{\rm EMA},r_b\}$ and observed flow $f_b$, fit
\begin{equation}
\begin{bmatrix}v_{b+1}\\f_{b+1}\end{bmatrix}
=d+J\begin{bmatrix}v_b\\f_b\end{bmatrix}+e_{b+1},
\qquad Q=\frac{J_{12}J_{21}}{1-J_{22}},\quad S=J_{11}+Q.
\label{eq:empirical_var_revised}
\end{equation}
Both regressors are observed at time $b$. The legacy implementation instead pairs $v_b$ with $f_{b+1}$, creating an overlapping forward-flow statistic. That alignment is retained only as a sensitivity comparison, not as a real-time observable state.

Order-flow or price-unit rescaling conjugates $J$ by a diagonal scaling matrix; the product $J_{12}J_{21}$, $Q$, $S$, and eigenvalues are unchanged. However, scale invariance does not establish causality, invariance to filtering, or equivalence to a latent economic state. Non-normal Euclidean norms additionally require fixed coordinates or a specified weighted norm.

For $J_{11},J_{22}\in[0,1)$ and $J_{12}J_{21}\ge0$, $S<1$ characterizes the positive real-root boundary and Schur stability of this two-state fit. Outside those sign restrictions, $S<1$ alone is insufficient; we always compute $\rho(J)$ directly. A multivariate fit to raw returns is not interchangeable with a fit to a filtered price level.

\subsection{Filters, Missingness, and Sessions}
For a martingale price with no price-to-flow feedback, the EMA deviation satisfies $x_{b+1}^{\rm EMA}=(1-\alpha)(x_b^{\rm EMA}+\Delta p_{b+1})$. Thus an anchor near $1-\alpha=0.93548$ can arise mechanically. Positive feedback must be interpreted against that construction and explicit no-adaptation controls.

The revision excludes transitions crossing UTC dates, timestamp gaps, or equity session boundaries. The previously reported recorder EMA continues across contiguous UTC dates and resets at data gaps; its lag products remain date-separated. Restored Binance and joint-venue constructions instead reset their filters at gaps and dates, as specified separately. It does not backward-fill missing prices or manufacture unobserved trading intervals. The primary crypto segments receive five EMA spans of initialization burn-in and require at least 500 retained observations. The equity analysis uses a separate rule: at least 600 raw session rows and a 500-event burn-in, so some retained equity fits are smaller than 500 observations. Segment estimates on the same date are combined using transition counts before date-level averaging and Student-$t$ intervals. The 13 Coinbase calendar dates include partial first and last dates. These intervals summarize variation across observed dates; they do not provide a long-horizon or independent external replication guarantee.

\subsection{Actual Dataset Scope}
Coinbase BTC, ETH, and ADA snapshots cover April 7--19, 2021. Binance's 768 saved asset-day fits cover twice-monthly dates in 2021--2024, but their generator reads 1-second trade-price klines and estimates at 10-second spacing with a 300-second EMA and forward flow. Klines do not contain bid--ask midpoints, queue identities, or full L3 books. The 66.3 million nominal seconds in the previous description are not the number of fitted transitions: the saved panel contains 6,519,552 fitted state rows, with one fewer transition per asset-day. Its original raw archives are not present in the inspected cache.

FI-2010 is an event-based book benchmark \citep{ntakaris2018}. The local representation contains 272,941 rows with supplied STOCK and DAY fields. Those fields define this reanalysis; the original identifier mapping has not been independently authenticated. The January BTC depth file covers January 9--20, 2023 rather than the entire month. It contains quote depth, and the revision uses quote-update OFI, not authenticated executed trades. Its provider attribution is not independently established here. It was already examined before this revision, so it is a secondary sample rather than an untouched prospective holdout.

\section{Observable Evidence and Fee Sensitivity}
\label{sec:baseline_natural_exp}
\subsection{Fresh Coinbase Reanalysis}
The following table is generated from fresh end-bin-aligned fits of the existing corrected recorder data. The primary filtered-state estimates are small and positive on average. Their magnitude changes substantially with alignment; raw-return intervals include zero for all three assets.
'''
    rows=[]
    for a in ['BTC','ETH','ADA']:
        for key,label in [('x_observed','EMA / observed'),('x_forward','EMA / forward'),('return_observed','Return / observed')]:
            s=cb[a]['variants'][key]
            rows.append([a,label,s['n_days'],ci(s['Q']),fmt(s['S']['mean'],4),fmt(s['max_rho'],4)])
    text+=table('Timing and state sensitivity on the recorded Coinbase sample. Feedback intervals use date-level Student-$t$ variation; maximum radius is over fitted day segments.','llrlll',r'Asset & State / flow & Dates & $\hat Q$ [95\% interval] & Mean $\hat S$ & Max $\rho$',rows,'tab:timing_revised')
    text+=r'''
\begin{figure}[htbp]\centering
\includegraphics[width=.95\textwidth]{../research_extension/paper_revision_20261006/figures/timing_comparison.pdf}
\caption{Feedback diagnostics change with observable state and timing. All plotted intervals are regenerated from the revision's daily estimates.}\label{fig:timing_revised}
\end{figure}
The comparison cautions against interpreting the larger legacy estimates as the gain of a specific learning rule. Anonymous data cannot distinguish algorithmic response from other persistent or informational channels. The primary EMA-state intervals describe aggregate observed relations; they do not supply a structural trader attribution.

\subsection{No-Adaptation Controls}
We generate 60 independent 6,000-second paths for each declared control, aggregate at 10 seconds, and apply the same 300-second EMA and burn-in. The four controls are martingale prices with independent flow; persistent exogenous flow independent of prices; persistent exogenous flow with price impact; and common price--flow news. None has a price-to-flow adaptive rule. These are bounded diagnostic experiments, not calibrated real-market null distributions or evidence that all possible confounding has been excluded.
'''
    rows=[]
    labels=['Independent martingale','Persistent exogenous flow','Order splitting with impact','Common news']
    for label,case in zip(labels,null['cases'].values()):
        rows.append([label,fmt(case['observed']['mean_Q']),fmt(case['observed']['sd_Q']),fmt(case['forward']['mean_Q']),fmt(case['forward']['sd_Q'])])
    text+=table('No-adaptation controls. Standard deviations describe Monte Carlo variation across 60 independent paths, not standard errors for the market estimates.','lrrrr',r'Control & Observed mean $Q$ & SD & Forward mean $Q$ & SD',rows,'tab:nulls_revised')
    text+=r'''
The controls show that filter construction, persistence, price impact, and information timing must be specified jointly. A diagnostic's sign is not an identification theorem. The historical estimator-validation archive also contains a no-feedback persistent-flow example with positive VAR feedback; that unfavorable result is retained in the replication materials.

\subsection{Sampling and Reference-Window Sensitivity}
We also examine the declared grid $\Delta\in\{1,10,60\}$ seconds and $W\in\{60,300,900\}$ seconds on the same recorded data and observed-flow timing. The cell $\Delta=W=60$ is excluded because the EMA span is one and its deviation is identically zero. The remaining 24 asset--specification cells use the same gap/session exclusions and date-level summaries. This is exploratory robustness, not immutable external preregistration. Changing the window changes the measured state and its mechanical persistence anchor; it does not merely change the precision of a fixed economic parameter.
'''
    rows=[]
    for g in grid['cells']:
        rows.append([g['asset'],g['delta_seconds'],g['window_seconds'],fmt(g['mechanical_anchor'],4),
                     ci(g['Q']),fmt(g['S']['mean'],4),fmt(g['max_rho'],4)])
    text+=table('Fresh sampling and filter grid. Intervals describe date-level variation; radii are maxima over fitted segments. Sign changes and intervals spanning zero are retained.','lrrrlll',r'Asset & $\Delta$ & $W$ & EMA anchor & $Q$ [95\% interval] & Mean $S$ & Max $\rho$',rows,'tab:grid_revised')
    text+=r'''
The grid should be interpreted as sensitivity of operational diagnostics, not evidence of universal positive feedback. The raw-return comparison and covariance rejections remain relevant even when a filtered-state cell has a positive estimate and a fitted radius below one.

\subsection{Covariance Specification Checks}
For each asset, fit a seven-parameter linear transition and unrestricted symmetric innovation covariance to 11 lag-0, lag-1 and lag-2 moments. Moment rows exclude all session and gap boundaries. A Bartlett HAC weighting matrix with bandwidth 10 bins is used; the $\chi^2_4$ reference is asymptotic. All three optimizations converge and their numerical moment Jacobians have rank seven, but the overidentifying restrictions are rejected at the 5\% reference level.
'''
    rows=[[a,md[a]['n_moment_rows'],fmt(md[a]['Q']),fmt(md[a]['J_stat'],2),f"{md[a]['p_chi2']:.3g}"] for a in ['BTC','ETH','ADA']]
    text+=table('Fresh covariance-matching diagnostics using observed end-bin flow. Rejection is a model limitation, not validation of structural causality.','lrrrr',r'Asset & Moment rows & $Q_{\rm MD}$ & $J$ statistic & Reference $p$',rows,'tab:md_revised')
    text+=r'''
The rejection can reflect omitted dynamics, filtering, parameter heterogeneity or nonstationarity. Section~\ref{sec:model_diagnostic_audit} independently removes unnecessary entrywise bounds, retains four HAC bandwidths and six starts per case, and confirms rejection in all twenty-four global/within-segment centering cases. Its retrospective forecast comparison retains all fixed lag alternatives and unfavorable outcomes. The revision does not select a different lag specification solely to obtain acceptance. These results constrain the linear approximation; coefficient sign agreement does not repair misspecification. The prior $J=73.00$ result belonged to pooled Coinbase data with legacy alignment, not an independent structural validation of the Binance panel.

Identification through heteroskedasticity requires invariant contemporaneous coefficients, orthogonal structural innovations, and nonproportional variance shifts. Those assumptions are not established by grouping volatile and calm observations alone. The previously reported negative contemporaneous product is not used here to identify market-maker buffering or to resolve the rejected dynamic specification.

\subsection{Saved Binance Panel: Secondary Evidence}
The saved fitted matrices satisfy their recorded $Q$, $S$ and spectral-radius identities to numerical precision. The initial calculation validated consistency of the derived archive. The subsequent independent raw reconstruction in Section~\ref{sec:restored_panel} reproduces all saved core estimates and supplies corrected observed-time fits; it does not validate the old structural interpretations. Recomputed intervals first average across assets on each of 96 dates and then use a date-level Student-$t$ reference. They remain sensitive to between-date dependence and the legacy forward-flow state definition.
'''
    rows=[]
    for k,v in panel['pooled'].items():rows.append([k,fmt(v['mean']),f"[{v['ci95_date_block'][0]:.5f}, {v['ci95_date_block'][1]:.5f}]"])
    text+=table('Saved Binance derived-panel summaries: 768 asset-days, 96 dates. These are legacy forward-flow diagnostics, not fresh raw-book estimates.','lrl',r'Index & Mean & Date-level 95\% interval',rows,'tab:panel_revised')
    text+=r'''
The archive has positive $Q$ on 86.85\% of asset-days and maximum fitted radius 0.97614. Stationarity of a filtered proxy fit does not certify fundamental price stability or dealer safety. Comparing venues without synchronized joint observations does not establish causal propagation. The previous joint four-variable matrix implied $\rho=1.00258$, contradicting its reported 0.9612, and no joint generating artifact was established after the expanded workspace and archive search. That old matrix and its associated FEVD percentages are withdrawn. Section~\ref{sec:restored_joint} now supplies a new joint fit from restored original-date archives; it does not retrospectively authenticate the withdrawn numbers or identify causal transmission.

\subsection{July 2022 Fee Intervention}
For the preserved 2022 panel, BTCUSDT is the treated pair and seven altcoin USDT pairs are comparators. There are 12 sampled dates before and 12 after July 8, giving 192 asset-day observations. We recompute $Y_{it}=\beta_0+\beta_1\mathrm{BTC}_i+\beta_2\mathrm{Post}_t+\beta_3\mathrm{BTC}_i\mathrm{Post}_t+e_{it}$ directly from saved estimates. This association is conditional on the legacy measurement construction. The exchange did not randomly assign treatment.

Binance's July announcement also excluded affected BTC volume from VIP and liquidity-provider volume calculations \citep{binance2022volume}. An August 26--September 26 ETH/BUSD fee promotion could alter cross-pair allocation even though ETHUSDT is the recorded comparator \citep{binance2022eth}. The intervention bundles trading incentives and may produce spillovers. Consequently, the treated/control contrast is not an uncontaminated shock to adaptive learning intensity.
'''
    rows=[]
    for dep in ['Q','S']:
        for key,label in [('classical','Classical OLS'),('asset_cluster','Asset clusters, $t_7$'),('date_cluster','Date clusters, $t_{23}$')]:
            v=fee[dep][key];rows.append([dep,label,fmt(v['beta'],6),fmt(v['se'],6),f"{v['p_t']:.3f}",f"[{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]"])
    text+=table('Recomputed fee-intervention association under alternative covariance/reference assumptions. One treated asset limits all inferential interpretations.','llrrrr',r'Outcome & Reference & Effect & SE & $p$ & 95\% interval',rows,'tab:fee_revised')
    text+=r'''
The date-clustered feedback interval spans both signs. The effect is not statistically distinguished from zero, but a no-effect conclusion is not established. The cross-asset placebo rank fractions are 0.750 for $Q$ and 1.000 for $S$; these are descriptive ranks over eight possible treated labels, not randomized-treatment probabilities absent an exchangeability argument. At the illustrative equivalence margin $\pm0.007$, the date-clustered two-one-sided reference gives $p=0.073$, so equivalence is not established at 5\%. The previous SE of 0.003072 was classical OLS, not asset-clustered uncertainty.

Date-specific BTC-minus-comparator gaps relative to June 24 are saved as descriptive diagnostics. The previous monthly event coefficients and joint pretrend $F$-tests were not traced to a matching fitted covariance and are withdrawn. Section~\ref{sec:monthly_event_rebuilt} reconstructs the monthly question on the restored original panel, retaining covariance-sensitive outcomes and explicit degenerate references rather than treating them as proof of parallel trends. The saved event-gap builder borrowed one global SE for all event dates, which does not identify valid date-specific uncertainty. The revision also withdraws the untraced 180\% volume headline. The rebuilt monthly reference tests vary sharply with the covariance choice, and saturated cluster choices cannot estimate valid uncertainty. No selected pretrend reference proves parallel counterfactual trends.

\section{Stress Diagnostics and Financial Exposure}
\label{sec:stress_fragility}
\subsection{Exploratory Spread-State Regression}
On the first 50,000 recorded BTC rows, repeated renders are corrected, timestamps deduplicated, and transitions crossing gaps omitted. A 100-span USD-price EMA defines a dimensional deviation. Regress its next difference on lagged deviation, observed signed base-unit flow, a wide-spread indicator at the sample 90th percentile, and their interactions. The slope-difference covariance uses a 60-second Bartlett HAC estimate. This is an exploratory conditional regression, not a full two-equation structural VAR.
'''
    rows=[['Calm flow slope',fmt(stress['flow_slope_calm'],4)],['Wide-spread flow slope',fmt(stress['flow_slope_wide'],4)],
          ['Slope difference',fmt(stress['flow_slope_difference'],4)],['HAC SE of difference',fmt(stress['HAC_se_difference'],4)],
          ['Normal-reference p',fmt(stress['p_normal_reference'],3)],['Residual SD ratio',fmt(stress['residual_sd_ratio'],2)],
          ['Calm inside-depth mean',fmt(stress['calm_depth_mean'],2)],['Wide-spread inside-depth mean',fmt(stress['wide_depth_mean'],2)]]
    text+=table('Fresh exploratory spread-state diagnostics. Flow slopes are dimensional USD per base-flow unit; they are not the dimensionless loop gain $Q$.','lr','Diagnostic & Value',rows,'tab:stress_revised')
    text+=r'''
Higher residual dispersion and lower measured depth are conditional associations, not evidence of an endogenous instability transition. A slope difference must be interpreted with its uncertainty rather than each regime's separate significance. The old 62.7-fold figure came from a separate 4,999-transition switching-regression fit, whose transition updates and convergence claims were not independently validated here. Neither its extreme p-value nor a dimensionally mixed ``stability'' index is retained as a headline result. The prior scaled sum added a persistence coefficient to a dimensional slope; this is not a valid unit-invariant boundary.

\subsection{Equity Sessions and the January Depth Sample}
The event-indexed equity analysis resets OFI and the 100-event EMA at each supplied STOCK--DAY boundary, drops 500 initialization events, and excludes sessions with fewer than 600 raw rows. All reported radii are computed directly. These supplied identifiers and price representations do not support causal comparisons of regulations across venues.
'''
    rows=[]
    for st,v in eq['per_stock'].items():rows.append([st,eq['stock_counts'][st],v['n_sessions'],fmt(v['Q_mean'],6),fmt(v['S_mean'],5),fmt(v['max_rho'],5)])
    text+=table('Fresh FI-2010 local-representation session fits. STOCK identifiers are supplied metadata; rows differ across stocks and event time is not seconds.','rrrrrr',r'STOCK & Raw rows & Sessions & Mean $Q$ & Mean $S$ & Max $\rho$',rows,'tab:equity_revised')
    ds=depth['summary']
    text+=r'''
The January depth reanalysis streams the entire existing file, carries previous quotes across read chunks, and sums OFI when one second straddles a chunk boundary. It fits a 120-second EMA state against same-second quote OFI, separately by day/gap segment. No executed-trade flow is inferred from book changes.
'''
    rows=[['Raw depth records',depth['n_raw']],['Dates retained',ds['n_days']],['Fitted transitions',ds['n_transitions']],
          [r'Mean $Q$ [date interval]',ci(ds['Q'])],[r'Mean $Q_{30}$ [date interval]',ci(ds['Q30'])],
          [r'Mean $S$ [date interval]',ci(ds['S'])],[r'Maximum segment $\rho$',fmt(ds['max_rho'],5)]]
    text+=table('Secondary January 9--20, 2023 depth-sample reanalysis. No claim of prospective holdout validation or authenticated participant attribution.','ll','Diagnostic & Value',rows,'tab:depth_revised')
    text+=r'''The 30-lag adjusted feedback changes sign in this sample. Thus a positive baseline is not robust to this adjustment, even though the fitted baseline radii remain below one. This unfavorable sensitivity is retained; quote-update OFI and executed flow are different measurements.

'''
    text+=r'''
\subsection{Fixed-Spectrum Transient Loss}
To isolate transient amplification, fix $\rho=0.85$, $C=[1,0]$, $B=1$, and the same Euclidean shock ball in declared abstract coordinates. Vary only the coupling in $J_\theta=\left[\begin{smallmatrix}.85&\theta\\0&.85\end{smallmatrix}\right]$. Compute $M_C$ over $t=0,\ldots,100$; both nonzero row components decrease beyond their peak, giving a tail certificate for this family. The spectrum is identical in every cell.
'''
    rows=[[fmt(v['theta'],1),fmt(v['rho'],2),v['peak_time'],fmt(v['M_C'],4),fmt(v['safe_radius'],5)] for v in trans['rows']]
    text+=table('Fixed-spectrum output magnification. Each exact-radius shock stays at the budget; a constructed worst-direction shock just above it breaches the budget.','rrrrr',r'Coupling $\theta$ & $\rho$ & Peak time & $M_C$ & $B/M_C$',rows,'tab:transient_revised')
    text+=r'''
\begin{figure}[htbp]\centering
\includegraphics[width=.95\textwidth]{../research_extension/paper_revision_20261006/figures/transient_loss.pdf}
\caption{Output magnification with fixed eigenvalues and a fixed loss operator. Coordinates and shock units are held fixed. This numerical family is illustrative rather than market calibrated.}\label{fig:transient_revised}
\end{figure}
The calculation verifies the norm identity and distinguishes an eigenvalue threshold from a loss-budget threshold. It does not show that arbitrary couplings are economically feasible, or that the initial-shock bound controls repeated stochastic inputs.

\subsection{Funded-Dealer Persistent-Flow Simulation}
We separately reproduce 48 cells with 400 seeds each (19,200 paths) using the preserved flow-moment calibration. The model has $a=0.5$, $\eta=0.2$, price-impact scale 0.002, price noise 0.0005, spread 0.002, initial equity 1, horizon 500, and inventory control 0.05. The simulation Jacobian uses the lagged update $J=\left[\begin{smallmatrix}a&1\\\eta Q&1-\eta\end{smallmatrix}\right]$ with $Q=S-a$; its full spectral radius is below one for the reported grid.

The dealer trades against flow at the current price, updates cash by execution proceeds and modeled spread revenue, marks inventory at the next price, and halts when equity is nonpositive or inventory market value exceeds the leverage allowance. These are modeled equity/margin failures, distinct from the historical inventory-capacity experiment, which retained positive equity. A higher allowed leverage limit changes the halt rule; it does not create additional equity.

B1 matches flow variance, B2 matches variance and lag-one autocorrelation, and B3 matches variance and long-run variance with exogenous AR flow. The flow-moment calibration is preserved rather than independently recalibrated from market data. All 48 new seeded halt counts match the recorded counts.
'''
    lookup={(r['S'],r['L'],r['mode']):r for r in dealer['cells']}
    rows=[]
    for L in [10.,20.]:
        for S in [.5,.6,.7,.8,.9,.95]:
            rho=max(abs(__import__('numpy').linalg.eigvals([[.5,1],[.2*(S-.5),.8]])))
            rates=[f"{100*lookup[S,L,m]['rate']:.1f}\\%" for m in ['feedback','B1','B2','B3']]
            rows.append([fmt(L,0),fmt(S,2),fmt(rho,4)]+rates)
    text+=table('Reproduced funded-dealer halt rates, 400 seeds per cell. Exact binomial intervals and halt counts are supplied in the revision results.','rrrrrrr',r'Limit $L$ & $S$ & $\rho$ & Feedback & B1 & B2 & B3',rows,'tab:dealer_revised')
    text+=r'''
B3 reproduces high failure rates without an endogenous price-to-flow rule. This supports the importance of low-frequency flow exposure within the model; it prevents attributing the failure uniquely to adaptive learning or non-normal transients. The fixed-spectrum experiment above addresses transient magnification separately. The simulation does not measure actual dealer failures or demonstrate welfare benefits of an exchange gate. Historical flash-crash mitigation percentages are omitted from the main evidence because they were calibrated illustrations rather than new causal event analyses.

\section{Attribution, Falsification, and Replication Limits}
\label{sec:attribution_falsification}
\subsection{Aggregate Relations Do Not Identify Algorithms}
The merged-cohort theorem concerns a stated linear, reset observation experiment. Anonymous prices and flows cannot identify identities within a merged representation. More broadly, the empirical VAR here does not distinguish a learning algorithm from a persistent exogenous flow process or discretionary response to common news. Participant identifiers improve disaggregation, but parameter recovery also requires a correct state model, sufficient regressor rank, and an orthogonality assumption; OLS alone is not an automatic causal identification guarantee.

\subsection{What the Diagnostics Establish}
Timing comparisons show that the legacy and end-bin states differ. Raw-return checks show that filtered persistence is not interchangeable with return persistence. No-adaptation controls test a finite declared family, not every confounder. Covariance rejection remains unfavorable evidence about the low-dimensional approximation. Sign-memory adjustment is a descriptive robustness exercise, not proof of causal learning. The revision makes no blanket assertion that all placebo tests have passed or that common response proves propagation.

\subsection{Traceability and Remaining Limits}
The revision archive records hashes, daily estimates, gap handling, inference calculations, numerical checks and source changes. Coinbase and equity calculations use existing local data representations; the January depth file is freshly streamed. The historical Binance results were initially recomputed from saved estimates; Section~\ref{sec:restored_panel} now also reproduces them from restored official original-date archives and supplies corrected observed-flow results. Official-source authentication is recorded for the restored Binance inputs. Provider attribution for the recorder, equity and depth representations, immutable external preregistration, independent replication and expert mathematical review remain open. Where numerical provenance could not support the previous claim, the result was withdrawn rather than replaced by a preset favorable number.

\section{Conditional Surveillance Implications and Conclusion}
\label{sec:policy_conclusion}
\subsection{Loss Budgets Require More Than Eigenvalues}
The exact radius is conditional on $J$, fixed state units, a declared shock set, a calibrated loss operator and budget $B$. If orders enter through a matrix $G$, the relevant immediate disturbance is $z_0=Gv$; a scalar price-impact bound does not automatically bound the entire state. For repeated orders or innovations,
\[
z_t=J^tz_0+\sum_{k=0}^{t-1}J^{t-1-k}Gw_{k+1},
\]
so an initial-shock radius alone is insufficient. Section~\ref{sec:risk_contract_extensions} gives sufficient common-metric bounds for changing coefficients and bounded nonlinear remainders, a finite-horizon Gaussian input contract, and a dollar mark mapping. Applying these bounds requires a defended uncertainty set, actual price-displacement states, exposure/cash rules and noise calibration.

\subsection{A Conditional One-Burst Gate}
If a separately justified model gives $\|z_0\|_2\le g_t V$ for a burst volume $V$, then $V\le B_t/(g_t M_C)$ bounds the modeled loss from that burst. The loss budget $B_t$ must come from actual available capital and declared risk limits, not an unsupported multiplication of capital by leverage. Under $C=I$, $B_t/(e n\mathcal K(J))$ is a conservative state-shock radius; an upper bound $B_t/\mathcal K(J)$ must not be used as a guaranteed safe radius. For a general $C$, the factor $\|C\|_2$ enters a norm-based conservative bound.

This mathematical implication does not establish that an exchange can observe every required input, run the estimator within its latency budget, improve price discovery, or prevent real insolvency. Comparing execution quality, delayed fills, liquidity and dealer outcomes against ordinary depth/size limits remains a separate prospective study. Circuit breakers and batching address additional market-design questions not resolved by these calculations.

\subsection{Conclusion}
Observable price--flow data support model-dependent diagnostics, while participant attribution and financial guarantees require additional information and assumptions. Within the stated linear probing experiment, merged cohorts are observationally equivalent and symmetric close-rate alternatives have a fourth-order separation lower bound. The scalar Gaussian price experiment supplies an explicit abstention layer near its unit-root boundary. The loss-budget identity shows why stable eigenvalues alone do not bound worst-case output magnification in fixed coordinates.

Empirically, end-bin observed flow produces smaller Coinbase feedback diagnostics than legacy forward-flow timing; raw-return intervals span zero, and covariance restrictions are rejected. Saved Binance fee contrasts do not establish either a causal learning response or equivalence to zero. Separate fixed-spectrum and funded-dealer simulations distinguish transient magnification from persistent-flow accumulation, with exogenous long-run-variance matching reproducing severe model losses. These limits are part of the findings. The restored studies remain descriptive; provider authentication, causal identification, independent review and real-market policy validation remain open.

'''
    return text


def main():
    source=(REV/'baseline/Machine_Markets_JF_Submission.tex').read_text()
    baseline=json.loads((REV/'baseline_manifest.json').read_text())
    expected=baseline['files']['paper/Machine_Markets_JF_Submission.tex']['sha256']
    existing=hashlib.sha256(TARGET.read_bytes()).hexdigest()
    receipt=REV/'source_update_receipt.json'
    prior=json.loads(receipt.read_text())['updated_sha256'] if receipt.exists() else None
    if existing not in [expected,prior]:raise RuntimeError('Source changed outside this revision; reconcile before writing.')
    source=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'''\begin{abstract}
\noindent Aggregate price--flow data reveal model-dependent feedback diagnostics rather than trader identities. In a reset linear cohort model, symmetric near-coincident rates require bounded-power probing budgets of order $\delta^{-4}$; a separate scalar Gaussian experiment yields a finite-window abstention layer. Reanalysis of recorded Coinbase data shows substantial sensitivity to flow timing and price filtering, while covariance restrictions are rejected. Saved Binance fee contrasts do not establish a causal response or equivalence. Finally, a declared loss operator and shock set yield an exact budget radius; fixed-spectrum and funded-dealer simulations distinguish transient magnification from persistent-flow accumulation. Independent replication and policy validation remain open.
\end{abstract}''',source,flags=re.S)
    start=source.index(r'\section{Introduction}')
    end=source.index(r'\section{Theoretical Model')
    source=source[:start]+INTRO+source[end:]
    source=source.replace('Release commit: \\texttt{488af63e9f884bf05d15320e8b262d04ba4287c8}',
                          'Revision baseline: \\texttt{451fd803c516}. This candidate has not been independently replicated')
    source=source.replace(r'\date{\today}',r'\date{October 6, 2026 --- revision candidate}')
    source=source.replace(r'\usepackage{graphicx}',r'\usepackage{graphicx,adjustbox}')
    source=source.replace(r'\onehalfspacing',r'\onehalfspacing\setlength{\emergencystretch}{2em}')
    source=source.replace(r'\maketitle',r'\hypersetup{pageanchor=false}\maketitle')
    source=source.replace(r'\setcounter{page}{1}',r'\hypersetup{pageanchor=true}\setcounter{page}{1}')
    # Explicit reset/noise experiment and correct scope of minimal realization.
    source=source.replace(r'Let price impact $\kappa > 0$ and anchor $a \in [0, 1)$ be known.',
        r'Let price impact $\kappa > 0$ and anchor $a \in [0,1)$ be known. Compare zero-initial-state responses with process innovations set to zero and adaptation rates strictly in $(0,1)$. The merged support excludes rates whose total weight cancels to zero.')
    source=source.replace('where $|\\operatorname{supp}(\\mathcal{M})|$ is the number of distinct dynamic adaptation rates $\\eta_i \\in (0, 1)$ (any instantaneous cohort with $\\eta = 1$ merges directly into the feedforward anchor $a$ without adding a dynamic pole).',
        'where the support counts distinct rates with nonzero merged weights; this statement excludes instantaneous rates. With these nonzero weights there are no cancellations at the distinct cohort poles.')
    source=source.replace('Under deterministic probing sequences satisfying power constraint',
        'Assume that the closed-loop family lies in a compact parameter set with $\\rho(J)\\le1-\\varepsilon$ uniformly for $|\\delta|\\le\\delta_0$, with $\\varepsilon>0$. Under deterministic probing sequences satisfying power constraint',1)
    source=source.replace('with rates $\\bar{\\eta} \\pm \\delta$ and identical total feedback $Q$.',
        'with rates $\\bar{\\eta}\\pm\\delta$ and identical fixed nonzero total feedback $Q$, with $\\sigma_v>0$ and $0<\\delta_0<\\min(\\bar\\eta,1-\\bar\\eta)$.')
    source=source.replace(r'C(\alpha, \sigma_v, \mathcal{P}_{\text{probe}})',r'C(\alpha,\sigma_v,\mathcal P_{\text{probe}},\mathcal S_\varepsilon)')
    source=source.replace('two transfer functions $H_A(z)$ and $H_B(z)$ are identical for all $z \\in \\mathbb{C}$ if and only if their poles and residues match identically.',
        'equality of $H_A$ and $H_B$ implies equality of $G_A$ and $G_B$ by $G=(z-a-\\kappa/H)/\\kappa$. Uniqueness of the poles and residues of $G$ therefore determines its nonzero merged weights.')
    source=re.sub(r'and its inverse \$z\$-transform.*?Summing the sequence yields',
        lambda _:r'''Choose $R\in(1-\varepsilon,1)$. Symmetry of the alternatives and compactness bound $H_\delta-H_0$ by $C_R\delta^2$ uniformly on $|z|=R$. Cauchy's coefficient formula then bounds its impulse coefficients by $C_R\delta^2R^t$, with the constant absorbing the time-index convention. Summing the sequence yields''',source,flags=re.S)
    source=source.replace(r'compact set $\mathcal{S}_\varepsilon \equiv \{J : \rho(J) \le 1 - \varepsilon\}$',
        r'compact parameter family $\mathcal S_\varepsilon$ satisfying $\rho(J)\le1-\varepsilon$')
    source=source.replace(r'analytic on $\{|z| \ge 1\}$, Choose',r'analytic on $\{|z|\ge1\}$. Choose')
    source=source.replace('lies in a uniformly Schur-stable compact parameter family',
                          'belongs to the stated compact parameter family')
    source=source.replace("By Kalman's realization theorem \\citep{kalman1960}, the minimal realization degree equals the degree of the denominator polynomial,",
        'For a rational single-input/output transfer function, the minimal realization degree is the denominator degree after cancellation \\citep{gilbert1963},')
    a=source.index(r'\begin{remark}[Economic Interpretation of Theorem 1]')
    b=source.index(r'\subsection{Theorem 2:',a)
    source=source[:a]+r'''\begin{remark}[Scope of the Separation Bound]
Merged rates identify aggregate weights, not the count or identities of participants sharing a rate in the reset linear experiment. The symmetric split construction makes the leading response difference quadratic in $\delta$, giving a fourth-order testing lower bound with fixed stability margin and noise/power assumptions. This does not identify dollar allocations, supply an upper bound, or justify a literal ratio of detection horizons between $\delta=0.05$ and a unit perturbation outside the local family.
\end{remark}

'''+source[b:]
    a=source.index(r'\subsection{Theorem 2:')
    b=source.index(r'\subsection{Theorem 3:',a)
    source=source[:a]+ABSTENTION+source[b:]
    source=source.replace('In standard economic policy models, market stability is evaluated exclusively through the spectral radius $\\rho(J) < 1$. We demonstrate that this criterion is dangerously incomplete.',
                          'Spectral radius describes asymptotic decay in the linear approximation. Loss exposure additionally depends on the shock set, output operator and finite-time magnification.')
    a=source.index(r'Let a risk-bearing market maker hold initial equity')
    b=source.index(r'Let $z_t',a)
    source=source[:a]+r'''Let $E_0$ be unencumbered equity and $0<\gamma\le1$ a chosen allocation to a modeled absolute loss/exposure budget. Define
\begin{equation}B=\gamma E_0.\label{eq:dealer_buffer}\end{equation}
This budget is not leverage-created capital. A separate margin or leverage allowance requires its own balance-sheet rule. Fix state units and a row loss operator $C$ mapping state disturbance to dollar exposure. The homogeneous initial-shock calculation below omits ongoing innovations and describes a stylized budget breach, not a complete stochastic solvency model.

'''+source[b:]
    source=source.replace(r'C \in \R^{1 \times n}',r'C\in\R^{m\times n}')
    source=source.replace('dealer\'s marked inventory loss:',
        'declared dollar exposures (one output for a scalar dealer loss):')
    source=source.replace(r'\text{Loss}_t = C z_t = C J^t z_0.',r'\text{Loss}_t = \|Cz_t\|_2=\|CJ^tz_0\|_2.')
    source=source.replace('Fix state units and a row loss operator $C$ mapping state disturbance to dollar exposure.',
        'Fix state units and an output operator $C$ mapping state disturbance to declared dollar exposures. A single row measures one loss channel; multiple commensurately scaled rows define a vector exposure budget.')
    source=source.replace('A margin breach (triggering forced liquidation and trading halts) occurs if',
                          'A modeled loss-budget breach occurs if')
    source=source.replace(r'|C J^t z_0|',r'\|C J^t z_0\|_2')
    source=source.replace('guaranteeing that no initial disturbance with', 'guaranteeing that no initial disturbance with')
    source=source.replace('triggers dealer insolvency in any direction is:', 'breaches the declared output budget in any direction is:')
    source=source.replace('where $M_C \\equiv \\sup_{t \\ge 0} \\|C J^t\\|_2$ is the peak transient magnification.',
        'where $M_C \\equiv \\sup_{t \\ge0}\\|CJ^t\\|_2$ is peak output magnification. Assume $C\\ne0$. For $C=I$, the budget constrains the Euclidean norm of the output vector rather than a scalar signed loss.')
    source=source.replace('The peak loss occurs at $t^* = \\lceil -1 / \\log \\rho \\rceil$. At $t^*$, the loss is $\\Theta(\\theta / (e (1 - \\rho)))$.\nThus, peak transient magnification satisfies $M_C \\ge \\frac{\\theta}{e (1 - \\rho)}$.\nThe exact safe radius is bounded by $r^*_{\\text{exact}} \\le \\frac{B e (1 - \\rho)}{\\theta}$.',
        'Already at $t=1$, the unit shock $z_0=[0,1]^\\top$ has loss $\\theta$, so $M_C\\ge\\theta$ and $r^*_{\\text{exact}}\\le B/\\theta$. No continuous-time approximation to the discrete peak is required.')
    a=source.index(r'\begin{remark}[The Dangerous Illusion')
    b=source.index(r'\subsection{Pseudospectral',a)
    source=source[:a]+r'''\begin{remark}[Interpretation and Coordinates]
Part 3 concerns the unrestricted class of stable linear matrices. It does not assert that every Jordan-family coupling has an admissible structural market parameterization. Non-normality alone does not imply a large financially relevant transient: the loss operator and disturbance directions must expose it. Rescaling states changes Euclidean shock balls and transient norms unless the metric is transformed consistently. Fixed physical units or a justified weighted norm are therefore necessary for financial comparisons.

Under $C=I$, $B/(en\mathcal K(J))$ is a guaranteed conservative lower bound on the allowable radius; $B/\mathcal K(J)$ is an upper bound, not a safe gating threshold. For a general output matrix, $M_C\le\|C\|_2 en\mathcal K(J)$ yields a conservative radius $B/(\|C\|_2 en\mathcal K(J))$.
\end{remark}

'''+source[b:]
    a=source.index(r'\subsection{Pseudospectral')
    b=source.index(r'\subsection{Multi-Asset',a)
    source=source[:a]+r'''\subsection{Pseudospectral Interpretation}
For $\epsilon>0$, define $\sigma_\epsilon(J)=\{z:\|(zI-J)^{-1}\|_2\ge\epsilon^{-1}\}$, including the spectrum by continuity, and $\alpha_\epsilon(J)=\sup_{z\in\sigma_\epsilon(J)}|z|$. The resolvent form of the Kreiss constant is equivalently
\[
\mathcal K(J)=\sup_{\epsilon>0}\frac{\alpha_\epsilon(J)-1}{\epsilon}.
\]
This relates transient growth to pseudospectral protrusion outside the unit disk in a specified norm \citep{trefethen2005spectra}. It is a geometric interpretation of established operator theory, not a measured market contour. We report actual matrix-power output magnification in Section~\ref{sec:stress_fragility}, with explicit matrices and loss coordinates.

'''+source[b:]
    source=source.replace(r'\frac{B}{e (2d) \mathcal{K}(J_{\text{multi}})}',r'\frac{B}{\|C\|_2 e (2d)\mathcal{K}(J_{\text{multi}})}')
    source=source.replace('compressing the safe radius by $14.5\\%$ relative to decoupled trading.',
                          'potentially reducing the radius under the stated positivity assumptions; no market-calibrated percentage is asserted.')
    source=source.replace('compressing the safe radius by roughly $14.5\\%$ in our empirical multi-asset calibrations.',
                          r'potentially reducing the radius under the stated assumptions. This is a conditional network result rather than a calibrated multi-asset estimate. Section~\ref{sec:risk_contract_extensions} proves a signed downstream-output extension, gives a hedged-portfolio counterexample to general monotonicity, and supplies a family inside the stated cohort equations.')
    source=source.replace('and portfolio loss operator $C \\ge 0$. Let',
        'nonnegative cross-impact $\\mathbf K\\ge0$, and a nonzero portfolio output operator $C\\ge0$. Assume $\\rho(J_{\\text{multi}})<1$. Let')
    source=source.replace('In empirical cross-impact calibrations examined here, asymmetric feedforward coupling injects transient terms of order $t K_{21} \\rho^{t-1}$, potentially reducing the radius under the stated positivity assumptions; no market-calibrated percentage is asserted.',
        'Coupled powers contain sums of leader-to-satellite propagation terms; their output magnitude depends on the fixed loss coordinates. No market-calibrated contraction percentage is asserted.')
    source=source.replace(r'\end{proposition}'+'\n\n'+r'Proposition~\ref{prop:cross_kreiss}',
        r'''\end{proposition}
\begin{proof}
After ordering states by asset, the coupled matrix is block triangular with the same diagonal blocks as the decoupled direct sum. The diagonal compressions of its resolvent are unchanged. Its operator norm is therefore at least the maximum norm of those diagonal blocks, which is the decoupled resolvent norm; taking the Kreiss supremum gives the first inequality. Nonnegative powers and a nonnegative output operator are entrywise nondecreasing in the directed coupling. The spectral norm is monotone for nonnegative matrices, giving $M_C(J_{\rm multi})\ge M_C(J_{\rm diag})$. The budget-radius inequalities follow with the same $B$ and $C$.
\end{proof}

Proposition~\ref{prop:cross_kreiss}''')
    source=source.replace('feedforward coupling that injects additional transient growth terms into matrix powers $J^t$',
                          'feedforward coupling that changes finite-time propagation in matrix powers $J^t$')
    # Preserve positive-feedback lag boundary, but do not extend to signed models.
    source=source.replace('This stability criterion is invariant to information timing:',
        'For positive feedback the same $+1$ boundary also holds with a lagged update; signed-feedback Jury conditions must be recomputed:')
    a=source.index(r'\section{Data and Empirical Identification Strategy}')
    b=source.index(r'\begin{thebibliography}',a)
    source=source[:a]+empirical_text()+r'\input{../research_extension/paper_revision_20261006/full_scope_appendix.tex}'+r'\newpage'+'\n'+source[b:]
    source=re.sub(r'\\enlargethispage\{[^}]+\}', '', source)
    # Correct verified FI-2010 bibliography metadata.
    source=source.replace('IEEE Transactions on Neural Networks and Learning Systems} 29, 6153--6163.',
                          'Journal of Forecasting} 37, 852--866.')
    added=r'''
\bibitem[Vetterli et~al.(2002)]{vetterli2002} Vetterli, M., P. Marziliano, and T. Blu, 2002, Sampling signals with finite rate of innovation, \emph{IEEE Transactions on Signal Processing} 50, 1417--1428. \url{https://doi.org/10.1109/TSP.2002.1003065}.
\bibitem[Boyd et~al.(1994)]{boyd1994lmi} Boyd, S., L. El Ghaoui, E. Feron, and V. Balakrishnan, 1994, \emph{Linear Matrix Inequalities in System and Control Theory}, SIAM. \url{https://web.stanford.edu/~boyd/lmibook/}.
\bibitem[Wang et~al.(2024)]{wang2024} Wang, Y., D. Sornette, K. Wu, and S. C. Lera, 2024, Dynamic influence networks self-organize towards sub-critical financial instabilities, Swiss Finance Institute Research Paper 24-77. \url{https://doi.org/10.2139/ssrn.4946318}.
\bibitem[Binance(2022a)]{binance2022volume} Binance, 2022a, Binance to exclude 13 BTC spot pairs in trading volume calculations, July 8. \url{https://www.binance.com/en/support/announcement/detail/9541012e103c4ad3bfccbc54cd5f18ba}.
\bibitem[Binance(2022b)]{binance2022eth} Binance, 2022b, Binance launches ETH/BUSD zero-fee trading, August 23. \url{https://www.binance.com/en/support/announcement/detail/5d8f9c0a68e24b82bff743a342dfa9b9}.
\bibitem[Manole and Ho(2022)]{manole2022} Manole, T., and N. Ho, 2022, Refined convergence rates for maximum likelihood estimation under finite mixture models, Proceedings of Machine Learning Research 162, 14979--15006. \url{https://proceedings.mlr.press/v162/manole22a.html}.
'''
    source=source.replace(r'\end{thebibliography}',added+r'\end{thebibliography}')
    for old,new in [('kyle1985','kyle1985continuous'),('glosten1985','glosten1985bid'),
                    ('brunnermeier2009','brunnermeier2009'),('adrian2010','adrian2010liquidity'),
                    ('greenwood2015','greenwood2015vulnerable'),('ntakaris2018','ntakaris2018benchmark')]:
        source=re.sub(r'(?<=[{,])'+old+r'(?=[},])',new,source)
    # Old macros are not evidentiary dependencies of the rewritten numerical text.
    source=re.sub(r'\\input\{generated/(?:binance_panel_macros|empirical_macros|solvency_macros)\.tex\}', '', source)
    source=source.replace('Open-science replication repository and timestamped code archive:', 'Repository address reported in the original manuscript (remote contents not verified in this revision):')
    source=source.replace('Continuous auctions and informed trader', 'Continuous auctions and insider trading')
    source=source.replace('where $\\alpha > 0$ is the learning step size.', 'where $H>0$ and $\\alpha > 0$ is the learning step size.')
    source=source.replace('two widely deployed algorithmic learning paradigms', 'two stylized signal-update paradigms')
    source=source.replace('The minimum mean-squared error (MMSE) estimator is given by the steady-state Kalman filter recursion:', 'Assume a Gaussian initial state and mutually independent, zero-mean Gaussian innovation and observation-noise sequences, independent of the initial state. In the steady-state covariance regime, the minimum mean-squared error (MMSE) estimator follows:')
    source=source.replace('Saved Binance fee contrasts do not establish a causal response or equivalence.', 'Raw reconstruction of 768 Binance asset-days confirms smaller feedback under observed-flow timing; fee contrasts and ordering-sensitive venue decompositions do not identify causal learning or transmission.')
    source=source.replace('probing budgets of order $\\delta^{-4}$', 'probing budgets of at least order $\\delta^{-4}$')

    restored=json.loads((REV.parent/'gap_closure_20261006/cross_venue/restored_panel_summary.json').read_text())
    primary=restored['summaries']['observed']['Q'];rawret=restored['summaries']['raw_return']['Q']
    updated=("\nThe restored original raw panel also permits a corrected observed-flow comparison: "
             +f"mean $Q={primary['mean']:.6f}$, with date interval $[{primary['date_t95'][0]:.6f},{primary['date_t95'][1]:.6f}]$. "
             +f"Its raw-return interval $[{rawret['date_t95'][0]:.6f},{rawret['date_t95'][1]:.6f}]$ spans zero. "
             +r"These results, all eight corrected asset means, missingness, and the re-estimated fee contrast appear in Section~\ref{sec:restored_panel}. The legacy table above is retained for comparison, not promoted to an observed-time or structural learning estimate."+"\n\n")
    source=source.replace(r'\subsection{July 2022 Fee Intervention}',updated+r'\subsection{July 2022 Fee Intervention}')
    if '\r' in source:raise ValueError('Carriage-return control character in generated manuscript')
    source=source.replace('While normal matrices have orthogonal eigenvectors that diagonalize under unitary transformations, non-normal matrices have non-orthogonal (nearly parallel) eigenvectors.', 'A normal matrix admits an orthonormal eigenbasis. A diagonalizable non-normal matrix lacks such a basis, and a defective matrix has insufficient eigenvectors; these facts alone do not determine output magnification.')
    source=source.replace('can undergo massive transient amplification before decaying asymptotically', 'can exhibit transient growth in a fixed norm before decaying asymptotically')
    TARGET.write_text(source)
    receipt.write_text(json.dumps({'baseline_sha256':expected,'updated_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
                                  'source':str(TARGET),'numeric_inputs':[str(p.relative_to(ROOT)) for p in sorted((REV/'results').glob('*.json'))]},indent=2)+'\n')
    print('Updated',TARGET)


if __name__=='__main__':main()
