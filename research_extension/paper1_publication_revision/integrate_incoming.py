"""Reconcile the incoming 15-November source with the audited revision.

The incoming file is preserved verbatim. Only the explicitly scoped results
below enter the manuscript; the earlier inference and initialization repairs
remain in force.
"""
from pathlib import Path

HERE=Path(__file__).resolve().parent

def between(text,start,end):
    return text[text.index(start):text.index(end,text.index(start))]

def integrate(t):
    incoming=(HERE/'incoming_20261115/ceiling_suite/papers/paper1_note/ssrn_parts.tex').read_text()
    shape=r'''
\begin{theorem}[Recovery within a shrinking cluster of linear memory rules]\label{n:shape}
Fix known $K\ge2$, $a$, $\kappa>0$, $\theta_c$, $L\ge2K$, and a nonempty compact parameter class
\[
\mathcal Z=\{(s,w):-1\le s_1<\cdots<s_K\le1,\ s_{i+1}-s_i\ge\gamma,
\ \omega_{\min}\le w_i\le\omega_{\max}\},
\]
where $\gamma>0$ and $0<\omega_{\min}\le\omega_{\max}<\infty$ are fixed. Let $g=(g_0,\ldots,g_{L-1})$ be $C^{2K}$ near $\theta_c$, with its derivative vectors of orders $0,\ldots,2K-1$ linearly independent there. The population has kernel $k_m=\sum_iw_i g_m(\theta_c+\Delta s_i)$, with known $\Delta>0$. Observe $N\ge1$ independent copies of its deterministic zero-state unit-impulse response $(h_0,\ldots,h_L)$ plus independent $N(0,\sigma^2 I_{L+1})$ measurement noise, $\sigma>0$.

There are $\Delta_0>0$ and $C<\infty$, depending on this fixed class and response design, such that for $0<\Delta\le\Delta_0$ every exact minimum-distance estimator over $\mathcal Z$ satisfies, with probability at least $1-\delta$, $0<\delta<1$,
\[
\|\hat z-z\|\le C\sigma\big(\sqrt{L+1}+\sqrt{2\log(1/\delta)}\big)
N^{-1/2}\Delta^{-(2K-1)}.
\]
The rank condition holds for $g_m(\theta)=(1-\theta)\theta^m$ at $\theta_c\in(0,1)$ and for $g_m(\theta)=(m+1)^{-\theta}$; taking $\theta_c>1$ in the latter gives summable infinite-memory rules on a sufficiently small neighborhood.
If the class contains the two Gauss--Radau/Gauss configurations with a common positive mass, distinguishing them requires $N\ge c\sigma^2\Delta^{-(4K-2)}$ at errors below $1/4$. Thus, for fixed confidence and sufficiently small fixed accuracy in the weights and rescaled types, the upper and lower orders agree on such a class.
\end{theorem}

The inverse estimate is global over the fixed separated class $\mathcal Z$, within a sufficiently small physical cluster. It does not establish global identification over an unrestricted type interval or over unknown numbers of types. Its constants can deteriorate as $\gamma$ or $\omega_{\min}$ tends to zero. The observation law is explicitly a noisy deterministic-response experiment; identifying it with passive process-noise data would require a separate argument. Proposition~\ref{n:univup} remains useful for other response families, including nonlinear ones for which this rank argument supplies no upper bound. Supplement Section~\ref{app:incoming} gives the inverse proof. The incoming optimizer simulation starts at the true parameter and is interpreted only as a local conditioning diagnostic, not as a deployable global recovery algorithm.
'''
    anchor=r'\section{Forecasting the public signal without recovering composition}'
    assert anchor in t
    t=t.replace(anchor,shape+'\n'+anchor,1)
    dual=r'''
\begin{theorem}[Pairwise detection and forecast mismatch]\label{n:dual}
Consider two specified causal aggregate maps $F,F'$ with the same known $a,\kappa$, common observed initial information, independent $N(0,\sigma^2)$ innovations, and a common predictable probe policy including the same independent randomization. Assume the required squared mean gaps are integrable. For a record of $T$ subsequent innovations, let
\[
V_t=\kappa^2\mathbb E_P[(F(h_t)-F'(h_t))^2],\qquad
\Lambda_T=\sigma^{-2}\sum_{t<T}V_t.
\]
Then $V_t$ is the excess mean squared forecast error of using the alternative conditional mean on the true record, and
\[
\mathrm{KL}(P_T\Vert P'_T)=\Lambda_T/2.
\]
Both testing errors can be below $1/4$ only if $\Lambda_T>1$.
For a countable set of candidate record densities with prior mass $\pi_*>0$ on the truth, the Bayesian mixture also satisfies the one-sided pathwise bound
\[
\log p_*(X_{1:T})-\log q(X_{1:T})\le\log(1/\pi_*).
\]
\end{theorem}

This is the Gaussian chain rule and the standard mixture likelihood bound, applied to the market experiment \citep{dawid1984,vovk2001}. It identifies a pairwise forecast mismatch with a directional information divergence. It does not identify total information about an unrestricted population, prove that every kernel is cheaply estimated, or make a failed detection test evidence of a small KL divergence. The test condition is necessary, not sufficient. The mixture bound is an upper bound on regret, not an absolute difference of log scores; it requires positive prior mass on the true candidate.

The error curve $\Phi(-\sqrt{\Lambda}/2)$ is exact for a deterministic Gaussian mean difference with common covariance, not for every predictable random mean gap. For example, in the two-step experiment $X_1\sim N(0,1)$ and $X_2=\pm\alpha X_1+\varepsilon_2$, the directional divergence is $2\alpha^2$ while the equal-prior testing error is $\arctan(1/\alpha)/\pi$, $\alpha>0$. It differs from $\Phi(-\alpha)$. This distinction limits what a numerical collapse onto a Gaussian reference curve can establish.

'''
    anchor=r'\begin{theorem}[A forecast benchmark]'
    assert anchor in t
    t=t.replace(anchor,dual+anchor,1)
    uniform=r'''
\begin{theorem}[Uniform cumulative predictive log-loss]\label{n:uniformlog}
Let $x_t=0$ and all feedback states be zero for $t\le0$. There are no probes. Innovations are iid $N(0,\sigma^2)$ with known $\sigma>0$. Consider all positive exponential-feedback populations with any finite $K$, $0\le r_i\le\bar r<1$, $0\le a$, and $S=a+\kappa\sum_iq_i\le\bar s<1$. For integers $T,L\ge1$, use the Bayesian AR($L$) predictive density with coefficient prior $N(0,I_L)$, known innovation variance, and zero padding before date one. Its expected cumulative log-loss relative to the known-population conditional density obeys
\[
0\le\mathbb E_P\log\frac{p(X_{1:T})}{q_L(X_{1:T})}
\le\frac{\bar s^2}{2}+\frac L2\log\Big(1+\frac{T}{(1-\bar s)^2}\Big)
+\frac{T\bar s^2\bar r^{2L}}{2(1-\bar s)^2}.
\]
For $0<\bar r<1$, choosing $L=\max\{1,\lceil\log T/(2\log(1/\bar r))\rceil\}$ gives average excess log-loss $O(\log^2(T+1)/T)$ uniformly over this class. If $\bar r=0$, take $L=1$.
\end{theorem}

The loss is measured in nats. This is an implementable density forecast with a uniform expected cumulative bound, rather than a pointwise statement about the last date's squared-error forecast. Its predictive variance incorporates parameter uncertainty. Unknown innovation variance, arbitrary initial states, a stationary unobserved prehistory, and a uniform MSE theorem need separate treatment. The stability and memory margins are fixed; the bound need not remain small as $\bar s$ or $\bar r$ approaches one. The Gaussian integral calculation in Supplement Section~\ref{app:incoming} proves the bound directly.

'''
    anchor=r'\begin{remark}[Drift remains a separate problem]'
    assert anchor in t
    t=t.replace(anchor,uniform+anchor,1)
    shapeproof=between(incoming,r'\begin{proof}[Proof of Theorem~\ref{n:shape}]',r'\begin{proof}[Proof of Theorem~\ref{n:irr}]')
    shapeproof=shapeproof.replace('which includes degree below $2K$.','with $q$ allowed to range over all polynomials of degree below $2K$.')
    shapeproof=shapeproof.replace('(i) As in',r'\emph{Lower bound.} As in').replace(r'(ii) \emph{Moments.}',r'\emph{Inverse bound: moments.}').replace('(iii) A linear',r'\emph{Rank examples.} A linear')
    shapeproof=shapeproof.replace(r'Theorem~\ref{n:dual}(ii)',r'Theorem~\ref{n:dual}')
    shapeproof=shapeproof.replace('This is the claim with $C=4C_b/(\\sigma_Ac_\\mu)$.',r'This is the claim with $C=4C_b/(\sigma_Ac_\mu)$. Compactness of $\mathcal Z$ and continuity give existence of an exact minimizer. A criterion tolerance $\zeta$ replaces $2\|\bar\xi\|$ by $2\|\bar\xi\|+\zeta$, which must be controlled at the desired statistical scale. The fixed-accuracy lower bound applies below half the separation of the two normalized configurations; positivity and weight bounds must be chosen so both belong to $\mathcal Z$.')
    proofs=r'''
\section{Detection, local-cluster recovery, and uniform log-loss}\label{app:incoming}

This section incorporates the incoming SSRN additions with explicit observation and initialization conditions. The statements are proved on paper. The revision formal file checks selected supporting algebra, rather than the full statistical or inverse-map results.

\begin{proof}[Proof of Theorem~\ref{n:dual}]
Condition on the observed history and the next probe. The two next-price laws have common variance $\sigma^2$ and means differing by $d_t=\kappa(F-F')(h_t)$. Their conditional divergence is $d_t^2/(2\sigma^2)$. The initial laws and conditional probe laws agree, so the chain rule sums these terms and gives $\mathrm{KL}(P_T\Vert P'_T)=\sum_t\mathbb E_Pd_t^2/(2\sigma^2)$. The alternative mean has error $\varepsilon_{t+1}+d_t$, with expected square $\sigma^2+\mathbb E_Pd_t^2$ by conditional mean zero. If both errors are below $1/4$, their sum and the total-variation testing inequality give $\mathrm{TV}(P_T,P'_T)>1/2$. Pinsker then gives KL greater than $1/2$ and $\Lambda_T>1$. Finally, $q=\sum_j\pi_jp_j\ge\pi_*p_*$ on every path, proving the mixture inequality. In the two-step counterexample, conditional testing error is $\Phi(-\alpha|X_1|)$; its expectation is the angle probability $\arctan(1/\alpha)/\pi$ for two independent standard normals. This supplies the stated counterexample to a universal error curve.
\end{proof}

'''+shapeproof+r'''
\begin{proof}[Proof of Theorem~\ref{n:uniformlog}]
Eliminating the group states gives $x_t=\sum_{j\ge1}\phi_jx_{t-j}+\varepsilon_t$ with $\phi_1=a+\kappa k_0$ and $\phi_j=\kappa k_{j-1}$ for $j\ge2$, with zero terms before date one. Positivity gives $\sum_j\phi_j=S$ and, for $L\ge1$,
\[
\sum_{j>L}\phi_j=\kappa\sum_iq_ir_i^L\le S\bar r^L.
\]
The causal inverse filter has nonnegative coefficients with sum at most $(1-S)^{-1}$. Zero initialization therefore gives $\sup_t\mathbb E x_t^2\le\sigma^2/(1-S)^2$, by Minkowski or the innovation representation.

Let $p_L$ be the Gaussian AR($L$) density with the true truncated coefficients $\phi_{1:L}$, and let $Z$ have rows $z_t=(x_{t-1},\ldots,x_{t-L})$. These regressors are predictable, although random. The truncation mean gap is $\tau_t=\sum_{j>L}\phi_jx_{t-j}$. The same conditional-density argument gives
\[
\mathbb E\log(p/p_L)=\frac1{2\sigma^2}\sum_t\mathbb E\tau_t^2
\le\frac{TS^2\bar r^{2L}}{2(1-S)^2}.
\]
Completing the square in $q_L(X)=\int\prod_t N(x_t;\varphi^\top z_t,\sigma^2)N(d\varphi;0,I_L)$ yields
\[
\log q_L=-\tfrac T2\log(2\pi\sigma^2)-\tfrac12\log\det(I_L+Z^\top Z/\sigma^2)
-\frac1{2\sigma^2}\min_\varphi\{\|X-Z\varphi\|^2+\sigma^2\|\varphi\|^2\}.
\]
This integral is a proper sequential density even for coefficients outside the stable region: each finite-horizon conditional Gaussian integrates to one. Comparing the minimum with $\varphi=\phi_{1:L}$ gives the pathwise inequality
\[
\log(p_L/q_L)\le\tfrac12\|\phi_{1:L}\|^2+\tfrac12\log\det(I_L+Z^\top Z/\sigma^2).
\]
Now $\|\phi_{1:L}\|^2\le S^2$. Concavity, the arithmetic--geometric mean eigenvalue bound, and $\mathbb E\|z_t\|^2\le L\sigma^2/(1-S)^2$ give
\[
\mathbb E\log\det(I_L+Z^\top Z/\sigma^2)
\le L\log\left(1+\frac{\mathbb E\operatorname{tr}(Z^\top Z)}{L\sigma^2}\right)
\le L\log\left(1+\frac{T}{(1-S)^2}\right).
\]
Add the bounds on $\log(p/p_L)$ and $\log(p_L/q_L)$ and use $S\le\bar s$. Nonnegativity is KL nonnegativity. The stated $L$ makes $T\bar r^{2L}\le1$; the $\bar r=0$ case has no omitted coefficients. This proves the uniform cumulative log-loss bound and its average rate.
\end{proof}

The incoming simulation evaluates 64 pair-and-probe combinations, local fits initialized at the truth, and two Bayesian AR examples. Its first experiment truncates memory at 120 taps; it is a check of that finite simulation model. Its Gaussian error curve is only a reference, and its local optimizer is not a proof of global computation. Additional regression tests in the revision package check sequential Gaussian scores against the batch integral at non-unit noise variances, the random-gap counterexample, the need for zero initialization, and the effect of dropping the rank condition. The frozen market-forecast calibration failures remain separate from these theoretical examples.

'''
    anchor=r'\section{Machine checks in detail}'
    assert anchor in t
    t=t.replace(anchor,proofs+'\n'+anchor,1)
    bib=between(incoming,r'\bibitem[Cesa-Bianchi', '%%END bib')
    assert r'\bibitem[Dawid' not in t
    t=t.replace(r'\end{thebibliography}',bib+'\n'+r'\end{thebibliography}',1)
    t=t.replace('Matching recovery requires additional identifiability and observation assumptions.', 'For separated linear-memory classes, a full-rank derivative condition yields matching recovery from noisy deterministic responses.')
    t=t.replace('In a stationary exponential-memory benchmark, a price-signal predictor approaches the composition oracle\'s forecast risk pointwise.', 'A Gaussian identity relates pairwise detection to forecast mismatch. A Bayesian predictor has a uniform cumulative log-loss bound under fixed stability and memory margins.')
    t=t.replace('It does not establish a uniform bound as types collide, a monotone decline in the value of positions, or irrelevance for traded returns when fundamentals are hidden.',r'Theorem~\ref{n:uniformlog} adds a uniform cumulative log-loss bound under zero initialization and known Gaussian innovation variance. Neither result establishes a monotone decline in the value of positions or irrelevance for traded returns with hidden fundamentals. Theorem~\ref{n:dual} relates pairwise detection to forecast mismatch, while Theorem~\ref{n:shape} proves a recovery bound within separated shrinking clusters in a specified response experiment.')
    t=t.replace('For exponential kernels the moment structure supports the relevant inverse analysis;',r'Theorem~\ref{n:shape} below proves such an inverse estimate on a restricted shrinking cluster for linear rules with full-rank derivative vectors;')
    start=t.index(r'\paragraph{What this means.}',t.index(r'\label{thm:pool}'))
    t=t[:start]+(HERE/'pooling_certificate.tex').read_text()+'\n\n'+t[start:]
    a=t.index('Whether $l_c=l^*$ in all configurations is a global question')
    b=t.index('Monte Carlo runs of the local estimator',a)
    t=t[:a]+r'''Proposition~\ref{prop:poolcertificate} supplies a block-Hankel rank certificate for global recovery at $l^*$ and proves that it holds generically. A compact class entirely satisfying that certificate has $l_c=l_g=l^*$. Numerical multistart searches are supplementary diagnostics: approximate roots near colliding nodes do not certify distinct exact populations, and absence of a found alternative is not a proof. The fresh extended-search output and its residual checks are included in the revision audit. For $D=K$ the certificate can be written out: the participation matrix cancels from the shift matrix $T_0^{-1}T_1$ of the pooled moments, whose eigenvalues are the memory rates (Supplement Section~\ref{app:jacobian}). This is the rotational-invariance identity behind ESPRIT and the matrix-pencil method \citep{roy1989,huasarkar1990}. '''+t[b:]
    t=t.replace('the closed-form exponent for $D$ deterministic snapshots and its use in markets are, to our knowledge, new.', 'the contribution here is the explicit market observation contract, its local and rank-certified global cost, and its intervention interpretation. We do not claim the underlying multi-channel Prony method as new.')
    a=t.index(r'\label{n:pool}')
    b=t.index(r'\end{theorem}',a)+len(r'\end{theorem}')
    t=t[:b]+r'''\par Supplement Proposition~\ref{prop:poolcertificate} adds a block-Hankel rank certificate: it gives global identification at this moment order, holds generically, and yields the same global rate on compact classes satisfying the certificate throughout. Rank-deficient exceptions and noisy rank decisions remain distinct issues.'''+t[b:]
    t=t.replace(r'\end{thebibliography}',r'''\bibitem[Hua and Sarkar(1990)]{huasarkar1990} Hua, Y., and T.~K. Sarkar (1990). Matrix pencil method for estimating parameters of exponentially damped/undamped sinusoids in noise. \emph{IEEE Transactions on Acoustics, Speech, and Signal Processing} 38(5), 814--824.
\bibitem[Roy and Kailath(1989)]{roy1989} Roy, R., and T. Kailath (1989). ESPRIT---Estimation of signal parameters via rotational invariance techniques. \emph{IEEE Transactions on Acoustics, Speech, and Signal Processing} 37(7), 984--995.
\end{thebibliography}''',1)
    t=t.replace(r'\paragraph{Contribution relative to existing methods.}',r'''\paragraph{Contribution relative to existing methods.}''',1)
    t=t.replace(r'\usepackage{etoolbox}',r'\usepackage{etoolbox,needspace}')
    t=t.replace(r'\begin{theorem}[Recovery within a shrinking',r'\Needspace{6\baselineskip}'+'\n'+r'\begin{theorem}[Recovery within a shrinking')
    t=t.replace('Take $q_i\\ge0$, $0<r_i<1$, $\\kappa>0$, $S<1$ and no probes. The following parts use different initialization and decision regimes.',r'The forecast benchmarks take $q_i\ge0$, $0<r_i<1$, $\kappa>0$, $S<1$ and no probes, with boundary cases stated explicitly. The pairwise detection comparison separately allows predictable probes. The results use different initialization and decision regimes.')
    return t
