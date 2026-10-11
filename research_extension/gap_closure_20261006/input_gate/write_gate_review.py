from pathlib import Path
HERE=Path(__file__).resolve().parent
BODY=r'''
\section{A Finite-Window Gate with Explicit Units and Existing Exposure}
Specify a scalar executed quantity $v_j$ in declared base units, a fixed-coordinate state, its input map $H$, and a monetary model-loss output $Cz$. Over $N$ steps,
\[
z_{j+1}=Jz_j+Hv_j,\qquad \ell_t=Cz_t,\qquad
\sum_{j=0}^{N-1}|v_j|\le V.
\]
No Schur-stability assumption is required for this finite-horizon calculation. For $0\le t\le N$ define $b_t=CJ^tz_0$, and for $1\le t\le N$ let
\[
g_t=\max_{0\le k<t}|CJ^kH|.
\]
An additional reserve $L_{\rm other}\ge0$ covers explicitly declared omitted risks. Bound cumulative execution costs by $c_{\rm exec}\sum_{j<t}|v_j|$, with $c_{\rm exec}\ge0$. Both $g_t$ and $c_{\rm exec}$ have monetary/quantity units; $b_t$, $L_{\rm other}$ and budget $B$ have monetary units.

\begin{proposition}[Finite-window quantity bound]
For the absolute-output criterion, the worst attainable output-plus-cost envelope at each $t\ge1$ over the stated quantity ball and cost class is
\[
|b_t|+L_{\rm other}+(g_t+c_{\rm exec})V.
\]
For a one-sided signed loss criterion, replace $|b_t|$ by $b_t$. Let $d_t$ denote the chosen background criterion. If some $d_t+L_{\rm other}>B$, no nonnegative quantity cap certifies the full window. Otherwise, if at least one $g_t+c_{\rm exec}>0$, the largest cap under this contract is
\[
V^*=\min_{\substack{1\le t\le N\\g_t+c_{\rm exec}>0}}
\frac{B-L_{\rm other}-d_t}{g_t+c_{\rm exec}}.
\]
Zero denominators impose no quantity restriction, provided their background already satisfies the budget. If all denominators vanish, this output contract places no quantity limit; other constraints may still apply. For a window lasting $\tau>0$ seconds, $V^*/\tau$ is an average quantity-per-second cap, not a count of order messages.
\end{proposition}
\begin{proof}
Superposition gives
\[
\ell_t=b_t+\sum_{j=0}^{t-1}CJ^{t-1-j}Hv_j.
\]
The triangle bound is $|b_t|+g_tV$. Its worst direction is attained by spending the whole quantity allowance in one pulse at a maximizing lag and choosing the sign to align with $b_t$; for one-sided loss choose the sign of the maximizing coefficient. A cost equal to its permitted envelope adds $c_{\rm exec}V$. Thus these are exact suprema for the specified linear output/quantity/cost class. Imposing every timewise inequality, including the initial background, yields the minimum cap. A volume exceeding that minimum violates at least one constraint under an admissible pulse.
\end{proof}

Sharpness concerns this declared linear budget criterion. It does not authenticate the financial output, unknown impact map, fills, reserve, model error or noise coverage. The absolute-output criterion can be more conservative than actual one-sided dollar loss.

\begin{proposition}[State coordinates and quantity units]
For any invertible coordinate change $T$, transforming $J,H,C,z_0$ to $TJT^{-1},TH,CT^{-1},Tz_0$ leaves every $b_t,g_t,V^*$ unchanged. Changing quantity units to $v'_j=av_j$, $a>0$, requires $H'=H/a$ and $c'_{\rm exec}=c_{\rm exec}/a$; the numerical cap becomes $aV^*$, describing the same physical quantity.
\end{proposition}
\begin{proof}
Cancel adjacent $T^{-1}T$ factors in $CT^{-1}(TJT^{-1})^tTz_0$ and $CT^{-1}(TJT^{-1})^kTH$. Quantity conversion divides the monetary-per-quantity denominator by $a$.
\end{proof}


\begin{proposition}[An identifiable financial functional despite cohort ambiguity]
Suppose two reset linear models have the same price input/output transfer for the same calibrated executed-quantity input, possibly with different state dimensions. Suppose monetary loss in this experiment is a known fixed multiple of that price output, and both models use the same budget, cost and reserve. Then their finite-window quantity gates coincide, even if cohort identities or cohort count are not identified.
\end{proposition}
\begin{proof}
Equality of the proper rational price transfers gives equality of every Laurent/Markov coefficient. Multiplying by the known monetary exposure preserves equality of the financial coefficients $CJ^kH$, so every $g_t$ agrees. Reset states give $b_t=0$ in both models. The cap formula therefore agrees. This uses no invertible correspondence between state spaces of different dimensions.
\end{proof}

An exact example compares one cohort of weight $1/5$ with two equal-rate cohorts of weights $1/10$ each, using $a=1/2$, $\eta=3/10$, $\kappa=1$. Their price input responses coincide despite different state dimensions. The monetary output $C=(2,0)$ or $(2,0,0)$ and input vector $(1,\eta)$ or $(1,\eta,\eta)$ give identical finite gates. Thus cohort ambiguity alone need not limit this financial functional. Unreset hidden states, unknown exposure/input maps, changing positions, fundamental risk and nonlinear marks can prevent this conclusion and require their own information.


\begin{proposition}[Positive-cohort price gain depends on the input protocol]
In the one-asset model with $0\le a<1$, $\kappa>0$, $q_i\ge0$, $0<\eta_i<1$ and $S=a+\kappa\sum_iq_i<1$, let all cohort states filter the same price state, with update $y_{i,t+1}=(1-\eta_i)y_{i,t}+\eta_i x_{t+1}$. A scalar executed input enters through $H=\kappa(1,\eta_1,\ldots,\eta_K)^\top$. For the known monetary price-only output $C=\lambda(1,0,\ldots,0)$,
\[
\sup_{k\ge0}|CJ^kH|=|\lambda|\kappa,
\qquad
\sum_{k\ge0}|CJ^kH|=\frac{|\lambda|\kappa}{1-S}.
\]
Thus the reset total-quantity pulse criterion and a sustained per-step input criterion use different gains. The first has no additional price-output impulse amplification beyond direct impact under these conditions; the second can grow large as $S$ approaches one. This statement does not apply without the positive, one-asset, fixed-output and stable-model assumptions, and does not include accumulated fees or fundamental/noise risks.
\end{proposition}
\begin{proof}
The price row of $J$ sums to $S$, and cohort row $i$ sums to $1-\eta_i+\eta_iS<1$. All entries are nonnegative, so $\|J\|_\infty<1$ and $\|H\|_\infty=\kappa$. Every price-response coefficient is bounded by $\kappa$, with equality at lag zero. This gives the peak statement, including $|\lambda|$.

All price coefficients have the same sign after multiplying by $\lambda$. The sum is therefore the absolute DC gain. At the stationary response to a constant unit input, each cohort has $y_i=x$, and the price equation gives $x=Sx+\kappa$, hence $x=\kappa/(1-S)$. Equivalently the sum is $|C(I-J)^{-1}H|$.
\end{proof}

The distinction also resolves a risk-ranking ambiguity. In the preceding economic supplement's positive-feedback example, increasing $\kappa$ from 0.1 to 1 lowers all-state Euclidean initial-shock magnification from a value above 1.21 to 1, while the price-based executed-input peak increases from 0.1 to 1. With budget one and zero background/cost/reserve, its quantity cap falls from 10 to 1. Matrix-state amplification and physical execution risk answer different experiments; an uncalibrated state norm cannot substitute for the financial input/output gain. These are established positive-system/control deductions applied to this model, not new general control machinery or market validation.

\section{Why a Window Cannot Be Reset without Carrying Its State}
In the scalar model $z_{t+1}=0.9z_t+v_t$, $C=H=1$, start at zero with budget one and a one-step window. The first allowance is one. Resetting the second window to zero falsely permits another pulse of one, producing actual loss output $1.9$. Carrying the actual state $z_1=1$ gives the second cap $1-0.9=0.1$ under the stated absolute-output contract. Window refreshes must use carried state, updated remaining capital, costs already paid and refreshed risk/model bounds. Repeating a single-window calculation is not an infinite-horizon solvency proof.

Displayed bid quantity does not supply a complete state embedding. For $H=(1,10)^\top$, the price component of a unit pulse is one, while its Euclidean state norm is $\sqrt{101}$; a monetary output $C=(0,1)$ responds by ten. The asserted bound of a full state norm by its price coordinate is false. A displayed top-five quantity and a price-impact coefficient also require a separate unit-consistent clearing relation before they determine $H$.

\section{Regulatory Context and the Remaining Operational Gate}
SEC Rule 15c3-5 already requires pre-trade credit/capital and erroneous-order controls; it is inaccurate to frame market-access protection as exclusively or inherently post-trade. See the SEC adopting release and staff guidance: \href{https://www.sec.gov/rules/final/2010/34-63241.pdf}{adopting release}, \href{https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions/divisionsmarketregfaq-0}{staff FAQ}. The FAQ is staff guidance rather than the rule itself. The proposed mathematical quantity bound may inform a risk-control design under its assumptions; it does not establish regulatory compliance, welfare superiority or execution feasibility.

Operational use requires authenticated positions, marks, currencies, executions, fees, funding, margins and cancellations; justified input, state, model-error and noise bounds; and carried exposure/capital accounting. Empirical model rejections and reserve calibration remain unresolved.
'''
if __name__=='__main__':
    (HERE/'gate_review_body.tex').write_text(BODY)
    pre=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsthm,hyperref}
\newtheorem{proposition}{Proposition}
\setlength{\parskip}{5pt}
\title{Machine Markets: Input and Financial-Output Gate Review}
\author{Research revision evidence}\date{October 8, 2026}
\begin{document}\maketitle
'''
    (HERE/'Machine_Markets_Input_Gate_20261008.tex').write_text(pre+BODY+'\n\\end{document}\n')
