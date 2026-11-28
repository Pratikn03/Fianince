"""Supplement part of the revision of 28 November 2026 (see revision_1128.py)."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
H = json.loads((ROOT / 'ceiling_suite/p1_empirics/results/p1t_holdout_results_full_A4.json').read_text())
EQ = json.loads((ROOT / 'ceiling_suite/p1_theory/equilibrium_uniform_cut_check_results.json').read_text())


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, ('revision_1128_supp', old[:160], n, count)
    return t.replace(old, new)


def sci(x):
    m, e = f'{x:.1e}'.split('e')
    return f'${m} \\times 10^{{{int(e)}}}$'


def f4(x):
    return f'{x:.4f}'


def ci(c):
    return f'$[{f4(c[0])}, {f4(c[1])}]$'


# ------------------------------------------------------------------------ the registered test (P1T) ------------

def p1t_table():
    g = H['diagnostics']
    p = H['primary_file']['primary']
    rb = H['robustness_blocks']
    rows = []

    def row(name, d, extra=''):
        rows.append(f"{name} & ${f4(d['D'])}$ & {ci(d['ci95'])} & {d['verdict']} & {d.get('n_stocks', '')} & {extra}\\\\")
    row('Primary: Foreign, block 20 ($B = 9{,}999$)', p, f"$p = 0.000$; {100 * p['share_stocks_positive']:.1f}\\% of stocks $> 0$")
    row('Foreign, block 10', rb['10'], f"$p = {rb['10']['p_one_sided']:.3f}$")
    row('Foreign, block 60', rb['60'], f"$p = {rb['60']['p_one_sided']:.4f}$")
    rc = g['reverse_causality']
    row('Reverse-causality check (\\S7.1)', rc, f"median stock $d = {rc['median_d_descriptive']:.4f}$; {100 * rc['share_stocks_positive']:.1f}\\% $> 0$")
    ps = g['per_stock']
    rows.append(f"Per-stock gains (\\S7.2) & median ${ps['median_d']:.4f}$ & quartiles $[{ps['quartiles_d'][0]:.4f}, {ps['quartiles_d'][1]:.4f}]$ & --- & 284 & {100 * ps['share_positive']:.1f}\\% $> 0$\\\\")
    for y in ('2019', '2020', '2021', '2022', '2023', '2020-02_to_2020-06'):
        s = g['stability'][y]
        row('Stability: ' + (y if y[0] == '2' and len(y) == 4 else 'Feb--Jun 2020'), s, f"$p = {s['p_one_sided']:.3f}$")
    sens = g['sensitivity']
    row('Sensitivity: dealer class with hedging', sens['hedging_in_dealer_class'], 'tests the dealer class')
    rows.append("Sensitivity: market-cap scaling & \\multicolumn{3}{l}{not computable (shares outstanding not in the registered sources)} & & \\\\")
    row('Sensitivity: limit days dropped', sens['limit_days_dropped'], '')
    row('Sensitivity: two-day periods', sens['2_day_periods'], f"block {sens['2_day_periods']['mean_block']}")
    row('Sensitivity: five-day periods', sens['5_day_periods'], f"block {sens['5_day_periods']['mean_block']}")
    s1 = g['S1']
    for c in ('Trust', 'DealerOwn'):
        row(f"S1: {'Investment trusts' if c == 'Trust' else 'Dealers, own account'}", s1['by_class'][c], f"Holm $p = {s1['holm_adjusted_p'][c]:.1f}$")
    s3 = g['S3']
    rows.append(f"S3: formula / bootstrap s.e.\\ of $\\hat r_F$ & median ${s3['median_ratio_formula_to_bootstrap']:.4f}$ & IQR $[{s3['iqr_ratio'][0]:.4f}, {s3['iqr_ratio'][1]:.4f}]$ & {'agreement' if s3['agreement'] else 'no agreement'} & {s3['n_stocks']} & {s3['n_excluded_abs_r_ge_1']} stocks with $|\\hat r_F| \\ge 1$ excluded\\\\")
    s2rows = []
    for c, nm in (('Foreign', 'Foreign'), ('Trust', 'Investment trusts'), ('DealerOwn', 'Dealers, own')):
        for per in ('fit', 'eval'):
            q = g['S2'][c][per]
            s2rows.append(f"{nm} & {'fit' if per == 'fit' else 'holdout'} & {q['n_stocks']} & ${q['r_median']:.2f}$ $[{q['r_iqr'][0]:.2f}, {q['r_iqr'][1]:.2f}]$ & ${q['w_median']:.4f}$ $[{q['w_iqr'][0]:.3f}, {q['w_iqr'][1]:.3f}]$ & {100 * q['share_w_positive_significant']:.1f}\\% / {100 * q['share_w_negative_significant']:.1f}\\%\\\\")
    share_in = 100 * g['S2']['Foreign']['share_eval_rF_in_fit_interval']
    return (r"""\begin{table}[!htbp]\centering\footnotesize
\caption{Every registered outcome of the Taiwan holdout (spec P1T, 2019--2023), from the single run's output file \nolinkurl{results/p1t_holdout_results_full_A4.json}. $D$ is the mean across stocks of the proportional out-of-sample MSE reduction; intervals are $95\%$ stationary date-bootstrap percentile intervals; $p$ is one-sided. Verdicts follow the registered rule: supportive if $p < 0.05$, $D > 0$ and the lower bound $> 0$; inconsistent if the upper bound is below $D^* = 0.0035$; inconclusive otherwise. Diagnostics use $B = 1{,}999$ resamples.}\label{tab:p1t_all}
\resizebox{\textwidth}{!}{\begin{tabular}{@{}lccccl@{}}\toprule
Outcome & $D$ & 95\% interval & Verdict & Stocks & Note\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}

\vspace{6pt}
\resizebox{\textwidth}{!}{\begin{tabular}{@{}llcccc@{}}\toprule
S2 (tagged IV, per stock) & Period & Stocks & $\hat r$: median [IQR] & $\hat w$: median [IQR] & $\hat w$ significant $>0$ / $<0$\\\midrule
""" + '\n'.join(s2rows) + r"""
\bottomrule\end{tabular}}
\parbox{\linewidth}{\footnotesize\emph{Notes:} S2 is descriptive (no test, as registered). The share of stocks whose holdout $\hat r_F$ lies in its fit-period interval is """ + f"{share_in:.1f}" + r"""\%. ``$p = 0.000$'' means that no centred resample out of $9{,}999$ reached $D$ ($p < 10^{-4}$). The Holm family is the two S1 classes.}
\end{table}""")


PRESPEC_TABLE = r"""\begin{table}[!htbp]\centering\footnotesize
\caption{Every pre-specified test tied to this model or its companions, from the project's empirical ledger (\nolinkurl{ceiling_suite/p1_empirics/EMPIRICAL_LEDGER.md}). None is a direct test of a theorem in this paper; ``registered'' means a specification committed to the public repository before the test data were read.}\label{tab:prespec}
\resizebox{\textwidth}{!}{\begin{tabular}{@{}p{0.2\textwidth}p{0.24\textwidth}p{0.17\textwidth}p{0.39\textwidth}@{}}\toprule
Test & Data & Registered & Outcome\\\midrule
E1--E5, E17--E19 & CFTC Commitments of Traders, 8 and 12 markets & before data (E1--E3, E17--E19); after earlier results (E4, E5) & class positions pin down persistence prices leave open: pass 8/8 and 12/12; trend-following class: fail 4/8, pass 11/12; less persistent class: pass 6/8, fail 3/12; flows pin persistence: fail 3/8; second memory root: fail 2/8\\
E6--E7 & real BTC noise, synthetic groups & before data & price-only requirement slope $-6.01$ for $K = 2$ (pass), $-9.81$ for $K = 3$ (holds)\\
E8--E16, E20--E23 & Binance class ratios, 30 markets & before data (from 24 October 2026) & 7 pass or hold, 8 fail, 1 not supported (Niroula et al., 2026a, scorecard: 11 of 23 recorded outcomes pass)\\
E24, P1T & TWSE tagged flows, holdout 2019--2023 & 7 November 2026 (four amendments, Section~\ref{sec:p1t}) & primary supportive; pre-specified reverse-causality check not supportive; reading B (Table~\ref{tab:p1t_all})\\
E25, P7S & Binance perpetuals, 5-minute & 11 November 2026 (retrospective sample, disclosed) & inconclusive; prospective replication after 14 February 2027\\
P1F & Binance futures metrics & 14 November 2026 & retrospective window void (0 of 30 symbols met the coverage rule); prospective window 16 November 2026 to 14 January 2027, open\\
H1, H2 & Hyperliquid trades with wallet addresses & 25 October 2026, prospective & collecting; analysis opens no earlier than 10 December 2026\\
P1KS & Korea short-sale ban, Naver data & not registered & design failed its power check on 2015--2019 data (27 November 2026); no 2020--2025 data read\\
E26, P1M & TWSE tagged flows, 2013--2016 & protocol fixed before the run & a measurement, not a test (Main Section~\ref{M-sec:taiwan})\\
\bottomrule\end{tabular}}
\end{table}"""


def sec_p1t():
    return (r"""\section{The registered Taiwan test: protocol, timeline and every outcome}\label{sec:p1t}

This section documents the out-of-sample test of Main Section~\ref{M-sec:taiwan}. Every file named here is in the public replication archive, with SHA-256 values in \nolinkurl{ceiling_suite/p1_empirics/P1T_SHA256SUMS}.

\paragraph{Registration.} The specification \nolinkurl{P1T_taiwan_spec.md} was approved by the first author on 7 November 2026 at 16:29 UTC and committed at 16:30 UTC (commit \texttt{a52ceea}), before any development, validation or holdout data were requested. The registration is a commit to the authors' own public repository, not a deposit with a third-party registry; the protocol was written after the 2019--2023 holdout period had ended, but before any of its data were requested. The single question is whether a class's own tagged daily flow responds to the price deviation, as the flow equation $u_{i,t} = r_i u_{i,t-1} + w_i x_t$ requires. The primary class is Foreign. The statistic $D$ is the mean across stocks of $d_s = (\mathrm{MSE}_0 - \mathrm{MSE}_1)/\mathrm{Var}_{\mathrm{fit}}(\tilde u_F)$ over holdout days, where model~0 forecasts next-day flow from its own two lags with an intercept and a limit-day indicator and model~1 adds $x_t$ and $x_{t-1}$. Coefficients are fitted per stock on the 1,000 trading days before 2 January 2019 and held fixed. Uncertainty comes from a stationary bootstrap over dates (the same dates for every stock), mean block 20, $9{,}999$ resamples, seed $20261107$; the one-sided $p$ is the share of centred resamples at least as large as $D$, and the interval is the $95\%$ percentile interval. The smallest effect of interest is $D^* = 0.0035$, from the sizing study. The verdict is supportive if $p < 0.05$, $D > 0$ and the lower bound exceeds zero; inconsistent with the model's feedback at the effect of interest if the upper bound is below $D^*$; inconclusive otherwise. The diagnostics (reverse-causality check, per-stock share, calendar stability, four sensitivity variants) and the secondary outcomes (S1: the same test for investment trusts and dealers' own account, with Holm adjustment; S2: tagged instrumental-variable estimates per class, descriptive; S3: formula against bootstrap standard errors) are reported whatever the outcome.

\paragraph{Amendments and access control.} Each period is opened once, and its unlock counter is kept in \nolinkurl{P1T_unlocks.json}.
\begin{itemize}[itemsep=1pt,topsep=2pt]
\item A1 (7 November): an era-aware parser for the exchange's report layouts, after the first validation attempt stopped at parsing before any statistic was computed.
\item A2 (7 November): the pre-specified diagnostics implemented and validated on simulated data.
\item The holdout readout, fixing the paper's wording for each possible outcome, was committed on 8 November at 03:55 UTC (commit \texttt{807a63b}), before the holdout was opened.
\item A3 (8 November, 05:30 UTC, commit \texttt{2691584}): the reverse-causality check drops a redundant regressor and classes that are zero on most fit days, and S3 is restricted to $|\hat r_F| < 1$, after two investigations on the validation period only.
\item A4 (8 November, 15:58 UTC, commit \texttt{67fedbe}): one index-row label on 2019-04-29 is read under its registered name. The holdout download had failed the integrity check on that label before any statistic was computed.
\item Readout amendment R1 (12 November) moves the test from the abstract to this supplement and Main Section~\ref{M-sec:taiwan}; it keeps the registered reading and its wording.
\end{itemize}
The run's download manifest records the time of every request. Development data (2013--2016) were first requested on 7 November at 16:35 UTC and validation data (2017--2018) at 16:38 UTC. Holdout data (2019--2023) were first requested on 8 November at 06:16 UTC, after the readout, A1, A2 and A3, and last at 15:33 UTC. The primary statistic was computed once, at 17:07 UTC. The only exchange days read before registration were those of a schema probe on 7 November (06:37 UTC), all outside the holdout and excluded from every confirmatory sample (2024-01-02 and 2024-01-03 on both exchanges, and 2026-11-06 on TPEx).

\paragraph{Data and construction.} TWSE daily reports T86 (institutional net buying by class), MI\_INDEX (closing quotes and the TAIEX), FMTQIK (market summary) and TWT49U (ex-rights and ex-dividend events), requested from \url{https://www.twse.com.tw} on the dates above and stored with their SHA-256. The universe is the 300 four-digit common stocks with the highest development-period traded value, after event, listing and suspension exclusions. A stock enters a period only if at least $95\%$ of that period's trading days are usable (traded on $t$, $t - 1$ and $t + 1$, none excluded); 284 stocks qualify in the holdout (281 for investment trusts). S2 and S3 use every stock with an estimate in the period (293 in the holdout). Classes: Foreign is foreign investors plus foreign dealers; investment trusts; dealers' own account; hedging enters only the reverse-causality regression and one sensitivity. Flows are net shares divided by development-period average daily volume. The price level is the cumulative sum of close-to-close log returns, with an event day's return replaced by $\hat\beta$ times the index return; event days and the day after are excluded. $\hat\beta$ is the OLS slope of daily stock on TAIEX log returns over development days (excluding event, post-event and limit days), fixed per stock afterwards, so the holdout uses no holdout information. $x_t$ is the log price level minus $\hat\beta$ times log TAIEX, minus its mean over the 60 preceding valid days.

""" + p1t_table() + r"""

\paragraph{Post hoc analyses, not registered.} Two analyses were run on 26 November 2026, after the holdout had been opened, and are not registered: the same statistic with price-limit and post-halt days masked, $D = 0.0410$ $[0.0197, 0.0623]$ (block 60: $p = 0.0019$), whose reverse-causality check is $-0.0083$ $[-0.0332, 0.0150]$; and the statistic split at the 23 March 2020 switch from periodic call auctions to continuous matching, $0.0319$ $[0.0219, 0.0415]$ before (291 days) and $0.0421$ $[0.0145, 0.0701]$ after (925 days). The switch coincided with the COVID-19 sell-off, so the split does not isolate the change in matching, and the two intervals overlap; we do not test their difference. The same re-extraction has $269{,}967$ valid stock-days in 2013--2016, $93$ fewer than the $270{,}060$ of the calibration in Main Table~\ref{M-tab:taiwan}, because it splices suspensions differently; Table~\ref{tab:p1m_sensitivity} uses it.

\subsection{Every pre-specified test tied to the model}

""" + PRESPEC_TABLE + "\n")


# ------------------------------------------------------------------------ the equilibrium proofs -----------------

def sec_eqcut():
    pr = EQ['principal_root_barrier']
    ex = EQ['same_precut_example']
    gaps2 = EQ['moment_matched_post_cut_gaps']['K2']
    gaps3 = EQ['moment_matched_post_cut_gaps']['K3']
    slopes = EQ['error_slope_in_logT']
    return (r"""\section{The uniform cut and the pilot in equilibrium}\label{sec:eqcut}

This section proves Main Theorem~\ref{M-n:eqcut}(iii)--(iv) and the rate in Main Theorem~\ref{M-n:pilot}(iv), and records the numerical checks (\nolinkurl{ceiling_suite/p1_theory/equilibrium_uniform_cut_check.py}, results in \nolinkurl{equilibrium_uniform_cut_check_results.json}). Constants $C$ depend only on the quantities listed in the statements.

\paragraph{The reduced form as an autoregression.} At a root $D$ of Main equation~\eqref{M-eq:Fcut}, Theorem~\ref{thm:eqreduced}(i) makes the pricing error the closed loop of Main equation~\eqref{M-eq:baseline} with $a^* = \bar a/D$, $\kappa^* = \kappa/D$ and effective measure $\tilde M = \theta h_D M$, $h_D(r) = (D - \bar a)/(D - r)$. With $v \equiv 0$ it is the autoregression $x_t = \sum_{j \ge 0} \phi_j x_{t-1-j} + e_t$ with $\phi_0 = a^* + \kappa^* \tilde k_0$, $\phi_j = \kappa^* \tilde k_j$ for $j \ge 1$, $\tilde k_j = \int r^j\, d\tilde M$ and i.i.d.\ Gaussian $e_t$. The coefficients are nonnegative and sum to $S^*$. Two identities follow.
\begin{itemize}[itemsep=1pt,topsep=2pt]
\item Since $\kappa\theta S_M(D) = 1 - D$, $\phi_0 = \bar a/D + (\kappa\theta/D)(D - \bar a)S_M(D) = \bar a/D + (1 - \bar a/D)(1 - D) = 1 + \bar a - D$.
\item For $z > \bar r$ let $\Psi(z) = \sum_{j \ge 0} \phi_j z^{-(j+1)}$, so that $\int (z - r)^{-1}\, d\tilde M = \{\Psi(z) - a^*/z\}/\kappa^*$. With $\theta = 1$, $M = \tilde M\,(D - r)/(D - \bar a)$, and $(D - r)/(z - r) = 1 + (D - z)/(z - r)$ gives
\begin{equation}\label{eq:SMfromphi}
  S_M(z) = \frac{\tilde k_0 + (D - z)\int (z - r)^{-1}\, d\tilde M}{D - \bar a} = \frac{\phi_0 - a^* + (D - z)\{\Psi(z) - a^*/z\}}{\kappa^*(D - \bar a)},
\end{equation}
the reconstruction used in Main Theorem~\ref{M-n:eqcut}(iv).
\end{itemize}

\paragraph{Proof of Main Theorem~\ref{M-n:eqcut}(iii).} Let $J = [D_\theta - \delta_1, 1]$ and $I = r_c + \Delta\eta[-1, 1]$. For $z \in J$, $z - r \ge \mu$ on $I$, so $f_z(r) = g(r)/(z - r)$ is analytic near $I$ with $\sup_I |f_z^{(n)}| \le C_n$ uniformly in $z \in J$. Expanding $f_z$ at $r_c$ to degree $2K - 2$, the polynomial part integrates to zero against $Q_A - Q_B$, so
\[
  |S_{M_A}(z) - S_{M_B}(z)| = \Bigl|\int R_z\, d(Q_A - Q_B)\Bigr| \le \frac{2\bar W C_{2K-1}}{(2K-1)!}(\Delta\eta)^{2K-1}.
\]
On $J$, $D - \bar a \ge D_{\min} - \bar a + \mu$, so $\kappa_-$ is smooth and bounded there; hence $e = \sup_J |F_A - F_B| \le C(\Delta\eta)^{2K-1}$. Let $D_A$ be the largest root of $F_A$. Since $\partial_D F_A \ge \nu$ on $J$, $F_A(D) \ge \nu(D - D_A)$ for $D \ge D_A$ and $F_A(D) \le -\nu(D_A - D)$ on $[D_A - \delta_1, D_A]$. For $e < \nu\delta_1/2$, $F_B > 0$ on $(D_A + 2e/\nu, 1]$ and $F_B(D_A - 2e/\nu) < 0$, so the largest root $D_B$ of $F_B$ satisfies $|D_A - D_B| \le 2e/\nu$. Finally $S^* = \Phi_M(D) = 1 - (1 - \bar a/D)S_M(1)/S_M(D)$ is Lipschitz in $D$ on $J$ uniformly over the class, because $S_M(D) \ge S_M(1) \ge W_{\min}\min_I g > 0$, and $|\Phi_{M_A} - \Phi_{M_B}| \le C(\Delta\eta)^{2K-1}$ on $J$ by the bound above at $z = D$ and $z = 1$. The two bounds give the claim.

\paragraph{Proof of Main Theorem~\ref{M-n:eqcut}(iv).} \emph{Step 1.} The proof of Main Theorem~\ref{M-n:passiveupper} uses only that the autoregressive coefficients are nonnegative with sum at most $1 - m$; it applies verbatim to the regression of $x_t$ on $L$ own lags with the theorem's $a$ set to zero and $\theta_j = \phi_j$. Hence, with probability at least $1 - 3\beta$ and for $T \ge 128L^2/(m^4\beta)$, $E_\phi = \|\hat\phi - \phi_{0:L-1}\|_2 \le 8\sqrt L\{(m\sqrt{T\beta})^{-1} + \rho_L/(m^2\beta)\}$ with $\rho_L = \sum_{j \ge L}\phi_j \le \kappa^*\tilde W\bar r^L/(1 - \bar r)$ and $\tilde W = \int d\tilde M \le \bar W(1 - \bar a)/\mu$. With $L = \lceil \log T/(2\log(1/\bar r))\rceil$, $\bar r^L \le T^{-1/2}$ and $E_\phi \le C\sqrt L\, T^{-1/2}$; also $|\hat D - D| = |\hat\phi_0 - \phi_0| \le E_\phi$.

\emph{Step 2.} Let $z_0 = \bar r + \mu$, so $z \ge z_0$ on $J$. Then
\[
  |\hat\Psi(z) - \Psi(z)| \le \sum_{j < L} |\hat\phi_j - \phi_j| z^{-(j+1)} + \sum_{j \ge L} \phi_j z^{-(j+1)} \le E_\phi\sqrt L\, z_0^{-L-1} + \frac{\kappa^*\tilde W (\bar r/z_0)^L}{z_0 - \bar r}.
\]
Since $z_0^{-L} \le z_0^{-1}T^{(1-\gamma)/2}$ with $1 - \gamma = \log(1/z_0)/\log(1/\bar r)$, both terms are at most $C L\, T^{-\gamma/2}$.

\emph{Step 3.} The map $(\phi_0, D, \Psi(z)) \mapsto S_M(z)$ in~\eqref{eq:SMfromphi} is Lipschitz on the relevant compact set, because $D - \bar a \ge D_{\min} - \bar a > 0$ and $\kappa^* = \kappa_-(D)/D$ is bounded below there. Hence $e = \sup_J |\hat F - F| \le C L\, T^{-\gamma/2}$ for the estimated~\eqref{M-eq:Fcut}. The root argument of part~(iii) gives $|\hat D_\theta - D_\theta| \le 2e/\nu$, and Lipschitz continuity of $\Phi$ gives $|\hat S^*_\theta - S^*_\theta| \le C L\, T^{-\gamma/2} = C(\log T)T^{-\gamma/2}$. No constant involves $K$ or the spacing. The rate is not parametric in general: by Main Theorem~\ref{M-n:questions}(ii) a functional with tap coefficients $z^{-(t+1)}$, $z < 1$, which are not square-summable, is not certified at rate $\sigma^2\epsilon^{-2}$ even from direct tap measurements.

\paragraph{The rate in Main Theorem~\ref{M-n:pilot}(iv).} In each regime the root is read off the first coefficient ($D = 1 + \bar a - \phi_0$, $D' = 1 + \bar a - \phi'_0$), and the effective taps are $\tilde k_j = \phi_j/\kappa^*$ for $j \ge 1$ and $\tilde k_0 = (\phi_0 - a^*)/\kappa^*$, with the dealer primitives giving $\kappa^*$. The pre-restriction taps are estimated at the rate of Step~1. The correction $\sum_{n \ge 0}\tilde k'_{m+n}D^{-(n+1)}$ is the pilot's analogue of $\Psi$ at $z = D \ge \bar r + \mu$, so Step~2 gives error $C(\log T')T'^{-\gamma/2}$ for a pilot record of length $T'$. The removed groups' effective measure $h_D M_R$ has the removed groups' memories as atoms, so Main Theorem~\ref{M-n:cost}(iii) applies to it with $K_R$ in place of $K$.

\paragraph{Both equilibrium roots of the realization.} With the primitives of Theorem~\ref{thm:eqreduced}(iv) ($\bar a = 0.4$, $A = 0.188$, $\sigma_F^2 = 1$, $\sigma_\xi^2 = 0.25$, $K = 2$, $r_c = 0.6$), each economy has two equilibria in $(\max(D_{\min}, \max_i r_i), 1]$: the constructed root $D = 0.800$, with $\partial_D F = -0.41$ (Gauss) and $-0.38$ (Gauss--Radau), and the principal root""" +
            f" $D = {pr[0]['D_G']:.4f}$ and ${pr[0]['D_R']:.4f}$" + r""", with $\partial_D F = 0.29$ and $0.28$. On the principal root the effective measures $h_{D_G}M_G$ and $h_{D_R}M_R$ differ from moment-matched measures only through the smooth factors $h_{D}/h_{0.8}$, so the barrier of Theorem~\ref{thm:eqreduced}(iv) holds there too: at $\Delta\eta = 0.1$, $0.05$ and $0.025$ the two roots differ by """ +
            ', '.join(sci(p['D_gap']) for p in pr) + r""" and the equilibrium impulse responses by """ +
            ', '.join(f"${p['ir_gap_over_d3']:.1f}\\,d^3$" for p in pr) + r""" in $\ell^2$. The lower root is the one at which a uniform cut raises the budget (Main Theorem~\ref{M-n:eqcut}(ii)); Figure~\ref{fig:supp_fragility} now labels its two branches by the sign of $\partial_D F$ rather than by a stability property, since we make no dynamic stability claim for the lower branch.

\paragraph{Numerical checks.} (a) The formula of Main Theorem~\ref{M-n:eqcut}(i) equals the reduced-form budget, and $\phi_0 = 1 + \bar a - D$, to $2 \times 10^{-16}$ at all four roots above. (b) A $50\%$ cut moves the principal Gauss root to $0.954$ and its budget from $0.650$ to $0.487$ (fixed-impact formula: $0.557$), and moves the lower root to $0.702$ and its budget from $0.755$ to $0.913$. (c) The example after Main Theorem~\ref{M-n:eqcut}: one group at $0.7$ with weight $0.02$ and groups at $0$ and $0.93$ with weights """ + f"${ex['w2'][0]:.4f}$ and ${ex['w2'][1]:.6f}$" + r""" share $D = """ + f"{ex['D']:.4f}" + r"""$ and $S^* = """ + f"{ex['one group at 0.7']['S_pre']:.4f}" + r"""$; after a $50\%$ cut their budgets are """ + f"${ex['one group at 0.7']['S_post']:.4f}$ and ${ex['groups at 0.0 and 0.93']['S_post']:.4f}$" + r""". (d) Post-cut gaps between the moment-matched pairs on the principal root fall with fitted slope """ + f"${gaps2['slope']:.2f}$ for $K = 2$ and ${gaps3['slope']:.2f}$ for $K = 3$" + r""" in $\log\Delta\eta$ ($\Delta\eta$ from $0.1$ to $0.0125$). (e) The estimator of part~(iv), applied to simulated records of the principal equilibrium (40 replications per cell, $L = \lceil\log T/(2\log(1/\bar r))\rceil$), has median absolute error falling with fitted slope """ + ', '.join(f"${v:.2f}$" for v in slopes.values()) + r""" in $\log T$ at $\Delta\eta = 0.1$, $0.05$ and $0.025$ over $T \in [2{,}000, 32{,}000]$; the errors do not grow as the spacing shrinks.
""")


# ------------------------------------------------------------------------ claims register -----------------------

CLAIMS = r"""\begin{longtable}{>{\raggedright\arraybackslash}p{0.14\textwidth}>{\raggedright\arraybackslash}p{0.29\textwidth}>{\raggedright\arraybackslash}p{0.21\textwidth}>{\raggedright\arraybackslash}p{0.22\textwidth}}
\caption{Claims register: for every main-text result, what Lean~4 proves from Mathlib with only the standard axioms, what the Lean statements take as hypotheses, and what is proved on paper only. Declaration names refer to the archive's Lean project (1,316 named declarations; axiom audit in \nolinkurl{formal_verification_receipt.json}); a machine check confirms the formal statement, not that it matches the prose.}\label{tab:claims}\\
\toprule
Result & Proved in Lean & Lean hypotheses & On paper only\\
\midrule
\endfirsthead
\toprule
Result & Proved in Lean & Lean hypotheses & On paper only\\
\midrule
\endhead
Thm.~\ref{M-n:suff} & kernel form of aggregate flow and its converse (\texttt{p1\_eqAggFlow\_kernel}, \texttt{p1\_anylinear\_iff}) & finite horizon & the step from pathwise equality to equal equilibria\\
Thm.~\ref{M-n:ident} & the price response obeys the closed loop with the merged kernel; deconvolution & --- & minimality of the realization (classical)\\
Thm.~\ref{M-n:thm_inventory} & first-order conditions, innovation, benchmark, small-feedback root (\texttt{p1\_inventory\_foc}, \texttt{p1\_inventory\_small\_feedback}) & --- & part (iii); the version of (iv) uniform over small measures\\
Thm.~\ref{M-thm:fragility} & discriminant positivity, ordered roots, $V < 2\sigma_F^2$, $S^*(\lambda_{\mathrm{crit}}) < 1$ & --- & the fold asymptotics under $F_{DD} > 0$ (assumed)\\
Thm.~\ref{M-n:thm_eqreduced} & reduced form and the realization (\texttt{p1\_eq\_realize\_D}, \texttt{p1\_eq\_scaled\_cohort}) & --- & parts (ii)--(iii); (iv) beyond the realization\\
Prop.~\ref{M-n:interv} & (ii)--(iii) (\texttt{interv\_same}, \texttt{interv\_tv}) & --- & the definition of total variation\\
Thm.~\ref{M-n:cost} & lower bound for every $K$ and horizon on a binomial moment-matched pair (\texttt{p1\_thm\_kcohort\_lower\_bound\_uniform}); Prony upper bound with sub-Gaussian noise (\texttt{p1\_thm\_prony\_upper\_bound}) & stability index below one; sub-Gaussian, independent noise & the Gauss and Gauss--Radau pair for general $K$; the matching lower order; the passive divergence rates\\
Thm.~\ref{M-n:passiveupper} & --- & --- & all of it\\
Thm.~\ref{M-n:questions} & tap identity, weak duality, half-width as half the modulus (\texttt{halfwidth\_modulus}) & finite populations & the minimax exchange; Gaussian coverage; the converse in (ii)\\
Cor.~\ref{M-n:sep} & the ratio bound (\texttt{sep\_ratio}, \texttt{sep\_unbounded}) & the two input bounds & the input bounds\\
Thm.~\ref{M-n:dual} & mismatch identity, $\Lambda > 1$ (\texttt{forecast\_mismatch\_identity}, \texttt{errors\_need\_unit\_loss}) & one-step Gaussian divergence, chain rule, Pinsker & those inputs\\
Thm.~\ref{M-n:separation} & through its parts & --- & part (iii) (summed impulse response)\\
Prop.~\ref{M-n:target} & (i) \texttt{target\_uniform\_iff}; (ii) \texttt{no\_common\_zero}, \texttt{node\_no\_recur}, \texttt{weight\_from\_lagrange}; (iii) \texttt{p1\_every\_k\_halt} & --- & exactness of the quasi-orthogonal rule; the sample bounds\\
Thm.~\ref{M-n:eqcut} & --- & --- & all of it (numerical checks in Section~\ref{sec:eqcut})\\
Thm.~\ref{M-n:pilot} & before-minus-pilot taps; one-group recovery (\texttt{pilot\_difference}, \texttt{one\_atom\_recovery}) & finite populations & Gaussian tap noise, truncation; part (iv)\\
Cor.~\ref{M-n:decisionloss} & two-point loss bound and its divergence form (\texttt{decision\_loss\_tv}) & Pinsker; Gaussian tail & those inputs\\
Thm.~\ref{M-n:minimax} & label averaging, Jensen, worst case, strict dominance and uniqueness (\texttt{minimax\_uniform\_strict}, \texttt{minimax\_unique}, \texttt{p1\_minimax\_compact\_existence}, \texttt{p1\_minimax\_strict\_loss\_dominance}) & --- & none beyond the model\\
Thm.~\ref{M-n:disc} & tagged coordinates determine weight and memory (\texttt{tagged\_inversion}) & --- & sampling rates; the two-point lower bound\\
Lemma~\ref{M-lem:micro} & small-feedback impact derivative; Kalman gain and Riccati identities & $n_{\mathcal H} < 0 < n_{\mathcal B}$ & third-order Taylor remainder\\
Prop.~\ref{M-n:relabel} & best response, welfare under tags, label gap (\texttt{hide\_best\_response}, \texttt{tag\_welfare\_identity}) & --- & none beyond the model\\
Thm.~\ref{M-n:paradox} & distortion comparisons and the bounds on the optimal spacing (\texttt{compare\_zero}, \texttt{compare\_double}) & Pinsker; the power envelope & those inputs\\
Thm.~\ref{M-n:recordvalue} & value of information on finite records; crowding divergence; record choice (\texttt{voi\_le\_tv\_mul\_gain}, \texttt{crowding\_divergence\_bound}, \texttt{trail\_beats\_prices}) & finite records & the integral form of (i); the two-sided case\\
Sec.~\ref{M-sec:taiwan} & halt effect of a geometric rule, relabeling, uniform cut, Whittle integrand, Pinsker record length & Whittle's formula; Pinsker & the estimates themselves\\
\bottomrule
\end{longtable}"""


# ------------------------------------------------------------------------ targeted fixes ---------------------------

EVIDENCE_START = r"A pre-registered out-of-sample test of the feedback premise on Taiwan's tagged exchange flows"
EVIDENCE_END = r"its pre-specified diagnostic cannot separate the gain from prices revealing past flow."


def evidence_new():
    p = H['primary_file']['primary']
    rc = H['diagnostics']['reverse_causality']
    return (r"A registered out-of-sample test of the feedback premise on Taiwan's tagged exchange flows (spec P1T, holdout 2019--2023; Section~\ref{sec:p1t} documents the protocol, its timeline and every outcome) reads, in the words fixed before the holdout was opened: ``$D = " + f4(p['D']) + "$ $[" + f4(p['ci95'][0]) + ", " + f4(p['ci95'][1]) + r"]$, $p = 0.000$, meets the registered supportive criterion. The pre-specified reverse-causality check gives $D = " + f4(rc['D']) + "$ $[" + f4(rc['ci95'][0]) + ", " + f4(rc['ci95'][1]) + r"]$, which does not meet it. The registered verdict is `supportive'. Read with its pre-specified diagnostic, the test does not provide evidence of feedback beyond prices revealing past flow.'' By the registered rule the check's verdict is `inconclusive': its interval contains zero and $D^* = 0.0035$, and $" + f"{100 * rc['share_stocks_positive']:.0f}" + r"\%$ of stocks have a positive adjusted gain (median $" + f"{rc['median_d_descriptive']:.3f}" + r"$). By calendar year the primary gain meets the criterion in 2019--2021 and not in 2022--2023. ``We do not claim that tagged flow in Taiwan responds to price deviations. The registered test is supportive, but its pre-specified diagnostic attributes the gain to reverse causality.'' Table~\ref{tab:prespec} lists every pre-specified test tied to the model.")


HOLDOUT_PARA_START = r"\paragraph{Out-of-sample 2019--2023 holdout and specification sensitivity.}"


def holdout_para_new():
    return (r"\paragraph{Out-of-sample 2019--2023 holdout and specification sensitivity.} Section~\ref{sec:p1t} documents the registered holdout and Table~\ref{tab:p1t_all} reports every registered outcome; the post hoc analyses run after it was opened are described there and labelled ``post hoc'' in Main Figure~\ref{M-fig:twse_sensitivity}. Table~\ref{tab:p1m_sensitivity} reports the 2013--2016 calibration under the baseline, limit-excluded and first-differenced specifications. Under first differencing the responses change sign for foreign investors and dealers, so the sign of the foreign contribution depends on the specification, while the class flow persistences barely move.")


def supplement(doc, main_tex):
    t = doc
    # registered test, wording fixed before the holdout was opened
    a = t.index(EVIDENCE_START); b = t.index(EVIDENCE_END, a) + len(EVIDENCE_END)
    t = t[:a] + evidence_new() + t[b:]
    a = t.index(HOLDOUT_PARA_START); b = t.index(r'\end{table}', a) + len(r'\end{table}')
    t = t[:a] + holdout_para_new() + t[b:]
    t = t.replace('pre-registered', 'registered')
    # map of where things are proved
    t = rep(t, r"(and Proposition~\ref{prop:endogenous_supervisor}, moved from the main text, is proved in Section~\ref{app:paradox}); Theorem~\ref{M-thm:fragility} is proved in Main Appendix~\ref{M-app:proofs} and",
            r"(and Proposition~\ref{prop:endogenous_supervisor} is proved in Section~\ref{app:paradox}); Theorem~\ref{M-thm:fragility} is proved in Section~\ref{app:proofs} and")
    t = rep(t, r"Proposition~\ref{thm:instruments} is proved in Main Appendix~\ref{M-app:proofs} and Sections~\ref{app:instruments}--\ref{app:passiveincidence}.",
            r"Proposition~\ref{thm:instruments} is proved in Sections~\ref{app:proofs}, \ref{app:instruments} and~\ref{app:passiveincidence}; Main Theorem~\ref{M-n:eqcut} is proved in Main Appendix~\ref{M-app:proofs} and Section~\ref{sec:eqcut}; Section~\ref{sec:p1t} documents the registered Taiwan test; and Table~\ref{tab:claims} records what is proved where.")
    # Theorem 4.4 proof slip
    t = rep(t, r"and $F_-(D; \lambda) \to +\infty$ as $D \downarrow D_* \equiv \max(D_{\min}, \max_i r_i)$. Thus",
            r"and $D_* \equiv \max(D_{\min}, \max_i r_i)$. If $D_* = \max_i r_i$, the ratio $(1 - D)/[\kappa_-(D)S_M(D)]$ tends to zero as $D \downarrow D_*$ because $S_M(D) \to +\infty$; if $D_* = D_{\min} > \max_i r_i$, the ratio stays finite but its derivative tends to $+\infty$ because $d\kappa_-/dD \to -\infty$. The ratio also vanishes at $D = 1$. Thus")
    # notation: the Stieltjes transform is S_M, the no-feedback discriminant is Lambda_0
    t = t.replace("G'(D)", "S_M'(D)").replace('G(D)', 'S_M(D)').replace('G(1)', 'S_M(1)')
    a = t.index(r'\label{thm:inventory}'); b = t.index(r'\end{theorem}', a)
    seg = re.sub(r'\\sqrt\\Delta', r'\\sqrt{\\Lambda_0}', t[a:b])
    seg = re.sub(r'\\Delta(?![a-zA-Z\\_])', r'\\Lambda_0', seg)
    t = t[:a] + seg + t[b:]
    t = t.replace(r'(\bar a+2A\kappa_-\sigma_\xi^2)/\sqrt\Delta$, and so the stated formula', r'(\bar a+2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0}$, and so the stated formula')
    # an unproved theorem becomes a conjecture; an unproved claim is labelled as such
    t = rep(t, r'\newtheorem{remark}', r'\newtheorem{conjecture}[theorem]{Conjecture}' + '\n' + r'\newtheorem{remark}')
    a = t.index(r'\begin{theorem}[Frequent batch auctions restore kernel sufficiency]\label{thm:batch_restoration}')
    b = t.index(r'\end{theorem}', a)
    t = t[:a] + t[a:b].replace(r'\begin{theorem}[Frequent batch auctions restore kernel sufficiency]', r'\begin{conjecture}[Frequent batch auctions restore kernel sufficiency; stated without proof]', 1) + r'\end{conjecture}' + t[b + len(r'\end{theorem}'):]
    t = t.replace(r'Theorem~\ref{thm:batch_restoration}', r'Conjecture~\ref{thm:batch_restoration}')
    t = rep(t, r'the local $(\Delta\eta)^{-(4K-2)}$ sample-complexity barrier continues to hold.',
            r'we expect the local $(\Delta\eta)^{-(4K-2)}$ sample-complexity barrier to continue to hold; we have not proved it.')
    # duplicate proof of the surveillance paradox (paragraph form)
    a = t.index(r'\paragraph{Proof of Theorem~\ref{M-n:paradox}.}'); b = t.index('\n\n', a)
    t = t[:a] + r'The proof of Main Theorem~\ref{M-n:paradox} is in Section~\ref{app:proofs}.' + t[b:]
    # duplicate proof of the relabeling proposition: keep the first
    first = t.index(r'\begin{proof}[Proof of Proposition~\ref{M-n:relabel}]')
    second = t.find(r'\begin{proof}[Proof of Proposition~\ref{M-n:relabel}]', first + 10)
    if second > 0:
        e = t.index(r'\end{proof}', second) + len(r'\end{proof}')
        t = t[:second] + r'The proof of Main Proposition~\ref{M-n:relabel} is in Section~\ref{app:proofs}.' + t[e:]
    # label collisions with the full working paper
    t = re.sub(r'\\(citealp|citet)\[(Theorem|Proposition|Section|Lemma|Corollary)~S', r'\\\1[their \2~S', t)
    # cross-reference and residue fixes
    t = rep(t, r"whereas tiny daily shares ($\Delta S \approx 2\times 10^{-4}$ in Table~\ref{M-tab:taiwan})",
            r"whereas tiny daily feedback contributions ($0.0017$ in total in Main Table~\ref{M-tab:taiwan})")
    t = rep(t, r'The inherited project has 1,316 named declarations', r'The Lean project has 1,316 named declarations')
    t = t.replace(r'Table~\ref{tab:newlean} covers the results added in this revision', r'Table~\ref{tab:newlean} covers the remaining results, and Table~\ref{tab:claims} gives the status of every main-text result')
    t = rep(t, r'During 2013--2016 TWSE stepped periodic call-auction intervals down ($20\text{s}\to 15\text{s}\to 10\text{s}\to 5\text{s}$),',
            r'TWSE had reduced its periodic call-auction interval in four steps from 25 to 5 seconds between 2010 and 2014 (Twu and Wang, 2018, in the main text),')
    t = t.replace(r"SEC CAT funding also remains subject to the Eleventh Circuit's July~2025 vacatur in \emph{ASA v.\ SEC}",
                  r"the SEC's 2023 CAT funding order was vacated in \emph{American Securities Association v.\ SEC}, No.~23-13396 (11th Cir.\ July 25, 2025)")
    t = rep(t, r'Both economies are equilibria with $D=0.8$, $\bar a=0.4$, $\kappa=0.4$ and $A=0.188$, and both equilibrium equations hold to machine precision.',
            r'Both economies are equilibria with $D=0.8$, $\bar a=0.4$, $\kappa=0.4$ and $A=0.188$, and both equilibrium equations hold to machine precision. The same primitives also have a principal equilibrium, with $D = 0.862$ (Gauss) and $0.861$ (Gauss--Radau), on which the barrier holds as well (Section~\ref{sec:eqcut}).')
    # Table S2: Lean names listed as paper-only; the corollary's inputs
    t = rep(t, r'compact existence (\nolinkurl{minimax_compact_existence}) and strict-loss dominance (\nolinkurl{minimax_strict_loss_dominance})',
            r'none (compact existence and strict-loss dominance are machine-checked: \nolinkurl{p1_minimax_compact_existence}, \nolinkurl{p1_minimax_strict_loss_dominance})')
    t = t.replace(r'group-uniform strict-cost uniqueness (\nolinkurl{minimax_partial_tags_strict_unique}, \nolinkurl{PublicationRevision18.lean})',
                  r'none (group-uniform strict-cost uniqueness is machine-checked: \nolinkurl{p1_minimax_partial_tags_strict_unique})')
    t = rep(t, r'the two input bounds (Theorems~\ref{M-n:cost}(i) and~\ref{M-n:questions}(ii))',
            r'the two input bounds, both in the tap-measurement experiment (the tap gap in the proof of Theorem~\ref{M-n:cost} and Theorem~\ref{M-n:questions}(ii))')
    t = rep(t, r'(cumulative sum $+0.341$;', r'(the ten-lag cumulative sum is $+0.341$, the five shown sum to $+0.374$;')
    # discussion-only subsections
    for title in (r'\subsection{Randomized hazard volatility interruptions and cross-venue coordination}\label{sec:jittered_auctions}',
                  r'\subsection{Pre-funded countercyclical margin buffers and maker-exempt fee incidence}\label{sec:margin_scaling}'):
        t = rep(t, title, title + '\n' + r'\noindent\emph{This subsection is a discussion; no result in the paper uses it.}' + '\n')
    # new sections before the machine checks; claims register in the verification section
    anchor = r'\section{Machine checks in detail}\label{app:mc}'
    t = rep(t, anchor, sec_eqcut() + '\n' + sec_p1t() + '\n' + anchor)
    vanchor = r'\section{Machine-checked declarations}\label{app:verification}'
    a = t.index(vanchor); b = t.index(r'\section', a + 10)
    claims = '{\\footnotesize\n' + re.sub(r'(\\texttt\{[^}]*\})', lambda m: m.group(1).replace('\\_', '\\_\\allowbreak{}'), CLAIMS) + '\n}'
    t = t[:b] + '\n' + r"\paragraph{Research use of AI tools.} Claude (Anthropic; Claude Opus 5.5 and Claude Fable 5.2), ChatGPT/Codex (OpenAI) and Gemini (Google) wrote, at the authors' direction, the numerical verification scripts, the empirical executors and notebooks, and the Lean~4 files, including the formal statements. The correspondence between formal and prose statements was audited with AI assistance (\nolinkurl{ceiling_suite/papers/paper1/review/LEAN_AUDIT_20261127.md}); the authors validated the proofs, the Lean formalizations and the empirical calculations (Main Declarations). Table~\ref{tab:claims} gives the status of every main-text result." + '\n\n' + claims + '\n\n' + t[b:]
    return t
