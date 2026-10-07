"""Build evidence/method appendices without dropping original study questions."""
from pathlib import Path
import json,csv
REV=Path(__file__).resolve().parent
load=lambda n:json.loads((REV/'results'/f'{n}.json').read_text())
def esc(s):
 for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:s=s.replace(a,b)
 return s
def longtable(cap,cols,header,rows):
 return r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+cap+r'}\\'+'\n'+r'\toprule '+header+r'\\\midrule\endfirsthead'+'\n'+r'\toprule '+header+r'\\\midrule\endhead'+'\n'+r'\bottomrule\endfoot'+'\n'+'\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\end{longtable}'+'\n'
s=r'''
\clearpage
\appendix
\section{Full Study Coverage and the Evidence Boundary}
This review revision retains all ten study questions and the information-contract and financial-risk program of the original 48-page manuscript. The original submission PDFs are preserved separately. Correcting an invalid result is different from abandoning its scientific question: the evidence below records successful reanalyses, model rejections, and specific missing dependencies. This version is a review candidate with open scientific gates, not a declaration of publication readiness. The page-disposition appendix connects every original page to its revision obligation.

\subsection{The Ten-Study Program}
\paragraph{Study 1: baseline aggregate diagnostics.}
The 768 asset-day archive answers a descriptive question about the fitted dynamics of a filtered price/flow proxy. Its matrices and derived invariants are internally consistent, but rechecking a stored matrix is not reproducing the transformation from exchange observations. The historical generator used close-price klines and forward-aligned flow. Accordingly, the archived means remain a separately labeled historical diagnostic. The primary observed-timing reanalysis on the traceable Coinbase sample shows how strongly the same scientific quantity changes under a corrected information convention.

\paragraph{Study 2: cross-asset heterogeneity.}
Differences in the archived $Q$ means across eight symbols can be reproduced from their saved fits. They do not identify institutional participation or a monotone effect of capitalization, because no participant identities or independently aligned capitalization data enter these estimates. A study of heterogeneity remains useful when sampling, filtering and uncertainty are held fixed. The appendix reports the actual saved means rather than interpreting the rank ordering as a causal mechanism.

\paragraph{Study 3: fee responsiveness.}
The saved 2022 panel permits reproduction of a treated-minus-control contrast around the fee change. Classical, asset-cluster and date-cluster uncertainty differ substantially. A one-treated-asset comparison needs a defensible counterfactual and assumptions about spillovers. A broad confidence interval containing zero does not establish that fees leave feedback unchanged; the stated equivalence margin also fails under the reported date-cluster test. These are results of the intervention study, not reasons to exclude it.

\paragraph{Study 4: dynamics around the intervention.}
The twice-monthly dates identify descriptive contrasts relative to the last pre-treatment date. Recovering a date-specific point contrast does not recover its standard error. The inspected event-study generator assigns pooled DiD uncertainty scaled by $\sqrt2$, without estimating the covariance of the individual contrast, and its clock differs from the old monthly display. The original joint pretrend statistic is therefore not retained as verified evidence. The dated contrasts remain available as a different reference construction. Section~\ref{sec:monthly_event_rebuilt} now fits a monthly asset/date fixed-effects design with declared covariance alternatives, reconstructs the pretrend references, and identifies saturation-induced covariance failures; causal assumptions remain unresolved.

\paragraph{Study 5: venue transmission.}
A saved separate-venue comparison is evidence of differences or similarities in marginal fitted dynamics. Transmission requires synchronized joint observations. The old displayed joint matrix contradicts its own spectral-radius claim, and its generating fit was not established in the expanded artifact search. Section~\ref{sec:restored_joint} now restores the original overlap from checksum-verified exchange archives and supplies an independently fitted joint process, while retaining clock/missingness sensitivities and the distinction between predictive relations and identified information shocks.

\paragraph{Study 6: forecast-error variance.}
FEVD additionally requires the residual covariance and a declared innovation identification or generalized decomposition. Percentages cannot be reconstructed from separate marginal summaries. Horizon labels must count the actual bin width: ten fitted steps at ten seconds per step do not represent ten seconds. Ordering sensitivity and the relation between quote midpoints and transaction-close proxies matter. No untraced percentage is offered as an observed systemic contribution. The subsequently restored joint study supplies a complete residual covariance, explicit generalized normalization, and all twenty-four orthogonal orderings; their sensitivity prevents a causal systemic-contribution interpretation.

\paragraph{Study 7: liquidity-state dependence.}
The first-50,000-record controlled regression is a bounded diagnostic on a recorded sample, not a comprehensive nonlinear identification design. Its slope difference is not detected with HAC uncertainty, while residual scales differ modestly. The historical switching code fits a scalar differenced-EMA regression, uses ad hoc transition updates, and creates a dimensionally chosen index by multiplying a slope by ten. That index is not the structural $S$ in the cohort theorem. A justified regime likelihood, initialization audit and uncertainty are required before a structural bifurcation conclusion.

\paragraph{Study 8: historical stress scenarios.}
The inspected historical script simulates an E-mini path with imposed depth dynamics and assigns the reported feedback parameters directly. The Treasury routine returns fixed values. These outputs can motivate an illustrative stress scenario, but they are not estimates from ingested historical TAQ. Moreover, the protected E-mini scenario changes depth and external liquidation flow as well as the proposed interception rule. Its improvement cannot isolate the rule's causal effect. Authenticated historical observation, where recoverable, would be a separate empirical test.

\paragraph{Study 9: the supplied equity sample.}
Session-reset fits reproduce aggregate diagnostics for supplied STOCK/DAY identifiers. Their counts differ across stocks, and their index is an event clock. The original benchmark/provider map has not been independently authenticated. The estimates therefore support replication of the local calculation, conditional on the supplied representation, rather than a fully authenticated cross-market mechanism. The session audit preserves actual stock counts and excludes cross-session transitions.

\paragraph{Study 10: funded dealers.}
The 48-cell replay reproduces archived halt counts exactly under preserved flow-moment calibration. Matched independent and persistent-flow comparators are important because inventory accumulation can arise without adaptive learning. Simulation seeds quantify path variability under that calibration; they are not independent market observations. The fixed-coordinate transient examples address a different deterministic experiment. Keeping the two studies separate prevents a simulated halt percentage from being presented as a theorem or historical intervention outcome.

\subsection{Information Contracts and Their Distinct Scientific Roles}
Public observation, controlled aggregate probing and audited internal state provide different information. A public tape lacks participant identity and policy-state disclosures. An aggregate probe can excite a transfer function under its reset, observation-noise and admissible-input assumptions, but does not automatically separate equal-rate cohorts. Audited cohort-specific state/action histories can remove an aggregation ambiguity in the specified linear model. They cannot on their own establish a correct fundamental-value proxy, a stationary policy, or a calibrated balance-sheet loss mapping.

A regression on disclosed state must specify whether the same-time price innovation enters the state update, which disturbances remain unobserved, and whether measurement error corrupts the disclosed variable. Ordinary least squares consistency cannot be inferred solely from observing a variable called ``internal state.'' Its moment restrictions need independent justification. Similarly, a Kalman recursion is an MMSE statement only under the stated distributional/independence model, and its steady-state gain concerns filtering error rather than financial solvency.

An operational information contract would need an authenticated schema, timestamps, units, missingness policy and verification of access to the declared variables. The present analysis defines conceptual information requirements. It does not claim that a deployed schema implements them or that firms' supplied signals satisfy the model. Uncertainty sets for parameters and output exposures must precede a regulatory action based on a calculated radius. Aggregate model rejection is itself a reason to withhold a structural certification.

\section{Repeated Innovations: A Conditional Loss Bound}
The initial-shock theorem does not control a stream of innovations. This gap has a direct conditional linear-system solution, stated here separately from empirical calibration.
\begin{proposition}[Exact induced gain for bounded innovations]
Let $z_0=0$, $z_t=Jz_{t-1}+Dw_t$, $y_t=Cz_t$, and $\rho(J)<1$. Use fixed Euclidean coordinates and suppose $\|w_t\|_2\le r$ separately at each time. Define
\[
G=\sup_{t\ge1}\max_{\|v\|_2=1}
\sum_{k=0}^{t-1}\|D^\top(J^k)^\top C^\top v\|_2.
\]
Then $G<\infty$ and
\[
\sup_{\|w_t\|_2\le r}\sup_{t\ge1}\|y_t\|_2=rG.
\]
For $G>0$ and loss budget $B>0$, the exact radius for this repeated-input experiment is $B/G$. For a scalar output, $G=\sum_{k=0}^\infty\|CJ^kD\|_2$. With an additional initial ball $\|z_0\|_2\le r_0$, the conservative sufficient condition $r_0 M_C+rG\le B$ controls all times.
\end{proposition}
\begin{proof}
For fixed $t$, write $y_t=\sum_{k=0}^{t-1}CJ^kDw_{t-k}$. Euclidean duality gives $\|y_t\|_2=\max_{\|v\|_2=1}v^\top y_t$. The compact finite product of input balls and the unit sphere permits interchanging their maxima. Each input independently maximizes its linear functional to $r\|D^\top(J^k)^\top C^\top v\|_2$, proving the finite-horizon equality. Taking the supremum over $t$ proves the formula. Schur stability implies summability of $\|J^k\|_2$, so $G\le\sum_k\|CJ^kD\|_2<\infty$. For a scalar output, the dual sphere is $\{-1,1\}$ and the sum is independent of its sign. The initial-condition inequality follows from the triangle inequality and the definition of $M_C$.
\end{proof}

This result requires neither nonnegative coupling nor independence of the innovations. It controls bounded adversarial inputs in a fixed linear system; Gaussian innovations are unbounded and do not satisfy its almost-sure premise. A stochastic high-probability result needs a declared horizon and tail law. Applying the proposition to orders requires the actual input operator $D$, the economically calibrated loss operator $C$, fixed units and a justified parameter set. It does not establish market execution safety from a descriptive proxy VAR.

For computation, let $G_N$ be the scalar-output partial sum through $k=N-1$. Choose an integer $h$ with $q=\|J^h\|_2<1$, which exists for a Schur-stable matrix. Commutativity of powers and submultiplicativity give the tail certificate
\[
0\le G-G_N\le
\frac{\|D\|_2}{1-q}\sum_{j=0}^{h-1}\|CJ^{N+j}\|_2.
\]
Thus a truncated calculation can provide an interval for $G$ rather than assuming that a finite horizon captured its maximum. Near instability the required horizon and uncertainty can be large. For a vector output, the partial dual optimization gives a lower bound and the summed operator norms give a conservative upper bound.

\section{Measurement and Inference Methods}
\subsection{The observable transformation}
The primary transformation forms past-observed bins, uses the last recorded midpoint in each bin and sums deduplicated executed signed flow. A missing bin splits the sequence; it is not filled from future values. The price state is log midpoint minus its exponential reference with $\alpha=2/(W/\Delta+1)$. Five reference horizons are excluded after a segment reset. This changes both the estimand and its sample count. For raw-return diagnostics, differences are formed within the same contiguous segment. Daily aggregation treats multiple segments on one date as parts of one date, rather than independent observations.

The observable proxy is not latent fundamental mispricing. Even a martingale filtered through an EMA produces memory. If a statement concerns fundamental stability, an observation-law relation is needed. Our reduced-form fit includes an intercept, and the off-diagonal ratio defining $Q$ is a diagnostic of that fit. Dividing by $1-J_{22}$ can amplify uncertainty when flow persistence is close to one; the invariants must be read alongside the full fitted radius, sampling clock and denominator.

\subsection{Timing recovery}
The recovered Gemini scratch script independently compares one-minute reported buys against sums of one-second records under three interval closures. The deduplicated past interval reproduces every one of the tested 1,995 windows for each asset. The future interval does not. The corresponding duplicate-render counts are 79,581 (BTC), 73,762 (ETH), and 65,973 (ADA). These arithmetic checks support how to read the local flow timestamps; they do not authenticate the original provider or identify a trader's policy. The revision also reconstructs each full local cache from its raw CSV with exact agreement.

\subsection{Dependence and small samples}
Means and confidence intervals based on a daily panel describe variation across observed dates. They are not probabilities that an individual latent learning parameter falls in the displayed interval. For the saved Binance panel, all assets on a date are kept together in the date-block summary. The DiD covariance calculations state whether they use classical residual variance, eight asset clusters or twenty-four date clusters, with corresponding reference degrees of freedom. Asset clustering with one treated asset remains fragile, even when the mechanical covariance calculation is correct.

Eight assignment contrasts permit only a coarse descriptive rank fraction unless an exchangeable assignment design is defended. The equivalence margin is a sensitivity choice, not a pre-registered economically optimal tolerance. Failing a TOST or failing to reject a zero effect cannot be combined into evidence that the effect is exactly zero. An event-specific covariance must be calculated for its own contrast, including uncertainty in the reference date.

\subsection{Minimum distance and rejection}
The reanalysis matches eleven covariance/lag moments to seven parameters and checks local rank seven. Segments contribute their own lagged products; products do not bridge discontinuities. The fitted system is restricted to be stable and innovation covariance positive definite. The diagnostic uses HAC weighting with ten bins and a four-degree-of-freedom asymptotic reference. A successful optimizer supplies a candidate moment fit; rejection assesses the maintained moment model. It cannot establish structural validity through a nearby reduced-form point estimate.

\subsection{Null families and specification sensitivity}
The nulls are declared no-adaptation data-generating families, not fitted replicas of every feature of the real sample. They isolate independence, persistent exogenous flow, order splitting with impact, and common news. Sixty repetitions per family under the same transformation show that a small positive diagnostic is compatible with mechanisms other than adaptive learning. This is a bounded falsification exercise; a stronger mechanistic comparison needs calibrated information and uncertainty. The sampling/window grid is exploratory, and all admissible declared cells are retained. The $W=\Delta=60$ cell is excluded because the chosen EMA becomes degenerate, not because its empirical result is unfavorable.

\section{Expanded Numerical Ledgers}
\subsection{Saved cross-asset means}
The following legacy means are displayed from the preserved outputs for comparison. Section~\ref{sec:restored_panel} independently reproduces them from current official archives and reports corrected observed-time estimates separately. The legacy table retains its original forward-flow construction.
'''
p=load('saved_panel_audit')
s+=longtable('Saved legacy panel: all eight asset means.','lrrr','Symbol & $Q$ & $S$ & $Q_{30}$',[[esc(a),f"{v['Q']:.7f}",f"{v['S']:.7f}",f"{v['Q30']:.7f}"] for a,v in p['by_asset'].items()])
s+=r'\subsection{Fee covariance and reference distributions}'+'\n'
fee=load('fee_reanalysis');rows=[]
for dep in ['Q','S']:
 for name in ['classical','asset_cluster','date_cluster']:
  v=fee[dep][name];rows.append([dep,esc(name),f"{v['beta']:.7f}",f"{v['se']:.7f}",v['df'],f"{v['p_t']:.5f}"])
s+=longtable('The same DiD coefficient with explicitly different uncertainty.','llrrrr','Outcome & Covariance & Coefficient & SE & df & $p$',rows)
s+=r'\subsection{Dated event contrasts, without unestimated error bars}'+'\n'
pth=REV/'results/event_gaps_descriptive.csv'
with pth.open() as f:rows=list(csv.DictReader(f))
print('Event columns',list(rows[0]))
# Preserve the exact file schema as numeric columns rather than assigning a new event clock.
keys=list(rows[0]);headers={'date':'Date','Q_gap':'$Q$ gap','S_gap':'$S$ gap','Q_relative':'$Q$ relative','S_relative':'$S$ relative'}
body=[]
for r in rows:
 vals=[]
 for k in keys:
  try:vals.append(f'{float(r[k]):.6f}')
  except ValueError:vals.append(esc(r[k]))
 body.append(vals)
s+=longtable('Descriptive dated contrasts from the same saved 2022 panel; no causal error bars are asserted.','l'+'r'*(len(keys)-1),' & '.join(headers.get(k,esc(k)) for k in keys),body)
s+=r'\subsection{All forty-eight funded-dealer cells}'+'\n'
s+=r'''All cells use 400 seeded paths under the archived calibration. Exact binomial intervals concern these conditional path probabilities. They do not quantify calibration error. $B_1,B_2,B_3$ are the preserved comparator labels; matching halt counts does not imply identical underlying economic mechanisms.
'''
dealer=load('dealer_reproduction');body=[]
for v in dealer['cells']:
 lo,hi=v['ci95_exact'];body.append([f"{v['S']:.2f}",f"{v['L']:.0f}",esc(v['mode']),v['halts'],f"{v['rate']:.4f}",f"[{lo:.4f}, {hi:.4f}]"])
s+=longtable('Complete conditional dealer replay, including zero and adverse cells.','rrlrrl','$S$ & $L$ & Mode & Halts/400 & Rate & Exact 95\% CI',body)
s+=r'\subsection{Every retained equity session}'+'\n'
with (REV/'results/equity_session_estimates.csv').open() as f:equity_rows=list(csv.DictReader(f))
s+=longtable('Session-reset equity estimates, including negative session diagnostics. Supplied identifiers are not independently authenticated.', 'rrrrrrr', 'Stock & Day & Raw rows & Transitions & $Q$ & $S$ & $\\rho$', [[r['stock'],r['day'],r['raw_rows'],r['n'],f"{float(r['Q']):.7f}",f"{float(r['S']):.6f}",f"{float(r['rho']):.6f}"] for r in equity_rows])
# Integrate the independently reconstructed joint study and exact-contract result.
import importlib.util
joint_path=REV.parent/'gap_closure_20261006/cross_venue/write_joint_appendix.py'
joint_spec=importlib.util.spec_from_file_location('joint_appendix_builder',joint_path)
joint_module=importlib.util.module_from_spec(joint_spec)
joint_spec.loader.exec_module(joint_module)
s+=joint_module.build()
panel_path=REV.parent/'gap_closure_20261006/cross_venue/write_panel_appendix.py'
import sys
sys.path.insert(0,str(panel_path.parent))
panel_spec=importlib.util.spec_from_file_location('panel_appendix_builder',panel_path)
panel_module=importlib.util.module_from_spec(panel_spec)
panel_spec.loader.exec_module(panel_module)
s+=panel_module.build()

s+=(REV.parent/'gap_closure_20261006/theory/full_observation_result.tex').read_text()
diag_path=REV.parent/'gap_closure_20261006/model_diagnostics/write_diagnostic_appendix.py'
diag_spec=importlib.util.spec_from_file_location('diagnostic_appendix_builder',diag_path)
diag_module=importlib.util.module_from_spec(diag_spec)
diag_spec.loader.exec_module(diag_module)
s+=diag_module.build()
risk_path=REV.parent/'gap_closure_20261006/risk_contracts/write_risk_appendix.py'
risk_spec=importlib.util.spec_from_file_location('risk_appendix_builder',risk_path)
risk_module=importlib.util.module_from_spec(risk_spec)
risk_spec.loader.exec_module(risk_module)
s+=risk_module.build()
event_path=REV.parent/'gap_closure_20261006/event_study/write_event_appendix.py'
event_spec=importlib.util.spec_from_file_location('event_appendix_builder',event_path)
event_module=importlib.util.module_from_spec(event_spec)
event_spec.loader.exec_module(event_module)
s+=event_module.build()




s+=r'\section{Recovering Evidence Across Workspaces}'+'\n'
s+=r'''The search receipt indexes 14,804 text files and archive members, with 10,570 distinct content hashes. It includes related local release/repair folders, historical tar releases, a Zoom ZIP and Gemini/Antigravity scratch material. Texts larger than two megabytes, environments, credentials and Git objects were excluded from content matching. This is a bounded discovery search rather than a declaration that all possible backups have been read. Candidate text matches are reviewed semantically before they support a result.

The recovered numeric-provenance matcher accepts a number if some token anywhere in a JSON/CSV rounds to it, including sign changes and factors of one hundred. Such a rule can accept an unrelated observation or simulated input and does not establish a generating chain. A source-to-data-to-estimator-to-field link is required instead. A subsequent current-source ledger checks 3,135 cells across all twenty-eight main and appendix tables against their specifically named result fields, with no rendering mismatch. It separately records nine input hashes and inventories theorem, figure and numerical-prose review obligations. These checks do not certify the scientific assumptions, provider identity, causal interpretation, or novelty. Agent completion reports and test counts are useful retrieval leads, but do not independently authenticate a historical sample or a theorem.

Additional named data and release directories were listed on the external T9 volume, including January 2025 archives. After a temporary loss of access, the volume became readable and 458 research files were inventoried, including 192 data archives with matching checksum-file names. Small research JSON outputs were read and hashed. A subsequent recovery audit streamed all 192 already located compressed data archives (6,510,779,702 bytes) and matched each SHA-256 digest to its supplied local checksum. Archive member names and initial CSV records were inspected without extracting new datasets. This establishes payload integrity relative to those checksum records, not independent provider authentication or complete CSV validation. The named binance-one-second directory contains no data files. The located archive dates and types do not establish the older one-second panel. An older January report repeats a withdrawn Coinbase value of $-0.3796$ and has conclusion prose inconsistent with its own positive estimates; recovery does not resolve those scientific conflicts. The subsequent recovery restores only original study units, as detailed above. No additional sample expansion or complex learner training was launched to substitute for evidence repair.

\section{Disposition of Every Original Page}
The table below refers to the original 48-page submission PDF, not the pagination of this review revision. It retains every original topic. Items marked open require the precise dependencies specified in the accompanying gap register, rather than silent removal from scope. Completed local calculations and unresolved scientific identification are deliberately distinguished.
'''
with (REV/'original_page_disposition.csv').open() as f:page_rows=list(csv.DictReader(f))
s+=longtable('Full original-page disposition.',r'rp{0.24\textwidth}p{0.61\textwidth}','Page & Original topic & Revision obligation',[[r['original_page'],esc(r['topic']).replace('/',r'/\allowbreak '),esc(r['action'])] for r in page_rows])
s+=r'''\section{Remaining Gates and the User-Requested Deferrals}
Raw reconstruction of all 768 original panel units and an independent synchronized joint study are now complete at their declared descriptive level. The active work remains full claim-ledger closure, residual/model diagnostics, existing policy/manifest verification, provider authentication and independent review. Neither the reconstructed panel nor its predictive decomposition identifies adaptive learning or a causal venue shock. Provider authentication, observational causal identification and independent mathematical/econometric review cannot be replaced by a compilation or test pass.

New large datasets, new complex learning-agent experiments and extra market modules are deferred until existing evidence is reliable. The currently located datasets and existing experiment outputs remain in the recovery/audit scope. T9 metadata and small-result checks were reopened when the volume became readable; original panel inputs have now been restored from current official archives and their saved core estimates reproduced; original download-time bytes and broader structural interpretations are not certified. Historical TAQ estimation reopens when an authenticated existing source is recovered; illustrative simulation parameters do not fill that gap. External replication and journal submission follow a concrete reproducible package, not an agent declaration of completion.

A rejection, null effect or invalid interpretation is already a result and must be reported now. These unfavorable findings are not deferred. The full revision retains their scientific questions while correcting their evidentiary status.
'''
(REV/'full_scope_appendix.tex').write_text(s)
print('Wrote full-scope appendices',len(s.split()),'words')
