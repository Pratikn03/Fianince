"""Passive-price identification and the scope of Taiwan's turnover evidence."""

import json
from pathlib import Path


SECTION = r"""
\section{Estimating smooth instrument incidence from passive prices}\label{app:passiveincidence}

\paragraph{Observation contract.}
Observe one centered stationary Gaussian realization of the pricing signal in
the base model. The process has positive exponential feedback with memories in
$[0,\bar r]$ for $\bar r<1$, known anchor $a$, stability budget at most $\bar S<1$,
and innovation variance between fixed positive bounds. The desk uses pre-policy
second moments from this same process. Its preference and policy inputs are
known. All comparisons concern the change at fixed impact and anchor. Neither the
realized innovations nor the impact coefficient are required by this estimator.

\paragraph{Normalized factor.}
Let $J(z)=\kappa\sum_{m\ge0}k_m z^m$ and $Q(z)=1-z(a+J(z))$. Positivity and the
budget bound give $\sup_{|z|\le1}|z(a+J(z))|\le\bar S$. By the memory bound, the
derivatives of $z(a+J(z))$ are uniformly bounded on some larger disk, since
$\kappa M([0,\bar r])\le\bar S$. Shrinking the larger radius if needed gives
$\sup|z(a+J(z))|<1$ there. Thus $Q^{-1}$ is uniformly bounded and analytic there.
Its impulse coefficients decay geometrically and the innovation variance
bounds give uniform geometric decay for the covariance sequence $\gamma_j$.
The stationary spectrum $f(\omega)$ in the convention
$f(\omega)=\sum_{j\in\mathbb Z}\gamma_j e^{-ij\omega}$ is bounded above and away
from zero.

Put $\ell_j=(2\pi)^{-1}\int_{-\pi}^\pi e^{ij\omega}\log f(\omega)\,d\omega$.
The analytic logarithm of $Q$ has zero constant and its negative has Taylor
coefficients $\ell_j$ for $j\ge1$. This follows by writing
$\log f=\log\sigma^2-\log Q(e^{-i\omega})-\overline{\log Q(e^{-i\omega})}$.
Hence $J=(1-\exp(-\sum_{j\ge1}\ell_j z^j))/z-a$. The apparent singularity at
zero is removable. The constant log-spectral coefficient is unnecessary for
$J$. This explains why the observer can estimate the impact-weighted functional
without estimating $\kappa$ or supplying direct kernel taps.

\paragraph{Statistical bound for the factor.}
Let $\tilde f$ be the covariance series truncated at $L_n=\lceil C\log n\rceil$,
using sample covariances with denominators $n-k$ for lag $k$. Take $C$ large
enough that the uniform geometric covariance tail is $o(n^{-1/2})$.
The expectation of the sum of absolute estimation errors is $O(L_n/\sqrt n)$
by the Gaussian fourth-moment identity, so the uniform spectral error has this
order in probability. Floor $\tilde f$ at half the known spectral lower bound.
With probability tending uniformly to one the floor is inactive. The log
expansion is $\log(\hat f)-\log f=(\tilde f-f)/f+O_P(L_n^2/n)$ uniformly.
For the linear term in coefficient $j$, the weights of the random covariance
errors are the Fourier integrals of $e^{ij\omega}/f(\omega)$ against the
covariance-series basis. Parseval bounds their squared sum independently of
$j$ by a constant times $\|f^{-1}\|_{L^2}^2$. The corresponding Gaussian
quadratic form has one diagonal per lag, with entries divided by $n-k$.
Its matrix $H$ has $\|H\|_{\mathrm F}^2\le C\sum_k|v_k|^2/n$ for weights
$v_k$. Since the sample covariance matrix has operator norm at most
$\sup f$, Gaussian quadratic-form variance is at most
$2(\sup f)^2\|H\|_{\mathrm F}^2$ for a real form. Apply this separately to
real and imaginary parts for complex weights. On $|z|=s<1$, sum the expected
absolute linear errors with geometrically decaying weights $s^j$.
Truncation bias and the log remainder are $o_P(n^{-1/2})$. Exponentiation on
the interior disk and division on the circle of radius $s>0$ give
$\|\hat J-J\|_s=O_P(n^{-1/2})$. A growing equally spaced frequency grid can
approximate the integrals: with order $n$ grid points the quadrature error
for each fixed coefficient is of order $O_P((L_n^2+j)/n)$ on the
high-probability event, using the derivative of the covariance polynomial
and the floor. Geometric summation controls these errors on the same circle.

\paragraph{A weight estimated from the same record.}
For the analytic quadratic-cost and scheduled-holding terms of the instrument
theorem, fix $R>1$ inside a uniform disk of analyticity of $g$. By Cauchy's
coefficient bound, $\sum_mR^m|c_m|$ is bounded by a common constant $B$.
Smooth dependence on the covariance series gives a pilot $\tilde g$ with
$\|\tilde g-g\|_{[0,\bar r]}=O_P(n^{-1/2})$. Fit a polynomial $\hat g$ at
logarithmic depth on a mesh of spacing at most a constant times $n^{-1/2}$.
Minimize maximum mesh error under $\sum_mR^m|\hat c_m|\le B$. The truncated
true coefficients are feasible and have exponentially small truncation error.
Both $g$ and the fitted polynomials have bounded first derivatives on the
memory interval, so the root-$n$ mesh bound holds on the interval. For
$R^{-1}<s<1$,
\[
 |\widehat{\Delta S}-\Delta S|
 \le B\|\hat J-J\|_s+\kappa M([0,\bar r])\|\hat g-g\|_{[0,\bar r]} .
\]
Indeed the coefficient error of order $m$ in $J$ is at most
$s^{-m}\|\hat J-J\|_s$ by Cauchy's inequality. The inequality is pathwise,
so fitting both objects on the same record is valid. The bound also yields
uniform fixed-confidence error of order $n^{-1/2}$ on the stated class.
In a fixed-memory submodel, with a strictly positive quadratic charge, the
target has nonzero derivative in the atom's weight near zero: at zero its
derivative is $\kappa g(r)>0$. For nearby small positive weights the derivative
remains nonzero, while stationary Gaussian finite-record KL is $O(n\delta^2)$
for a weight difference $\delta$, by the uniform spectral covariance
sandwich. The two-point testing argument gives the matching order on classes
containing this submodel.

\paragraph{Which price must be observed.}
An observable price deviation can serve as the pricing signal if the stated
stationary model is specified for that series. A tape with an unrestricted
independent latent component is insufficient in general. Take two different
stable feedback spectra and a constant spectrum larger than both. For each
candidate add an independent Gaussian process with spectrum equal to the
difference. The observed Gaussian price laws then coincide while the
quadratic-cost effect can differ. The observer needs a signal definition or
additional restrictions on the latent component. A zero-memory group is also
confounded with an unknown anchor. The passive theorem addresses smooth terms;
it supplies no parametric guarantee for the total-budget pole, tapering at exit,
or a venue whose pricing signal is unspecified.

\paragraph{What the Taiwan tax change measures.}
The exchange documents a cut from $0.3\%$ to $0.15\%$ for qualifying stock day
trades in April 2017. \citet{wuwang2020} report increased day-trading volume and
share under their comparison designs. This supports a volume response to the
policy. Their aggregate outcomes do not identify the change in signed
feedback by desk or its dependence on independently estimated pre-policy
memory. The public exchange table reports day-trade volume and values by stock,
without account IDs, execution sequences, or a trader-specific pricing signal.
Accordingly, this historical evidence is distinct from the P1M calibration and
the hypothetical coefficient exercise. Identifying the derived response would
require verified exposure to the tax change and linked signed executions for
stable trader cohorts. No historical outcome was re-estimated here.

"""


def diagnostics():
    p = Path(__file__).resolve().parent.parent / "passive_tax_followup" / "passive_diagnostics.json"
    data = json.loads(p.read_text())
    first, last = data["rows"][0], data["rows"][-1]
    return (
        r"\paragraph{Synthetic verification.} The script \nolinkurl{passive_incidence.py} "
        r"simulates the stationary feedback model and uses a single record per estimate. "
        f"Across {data['repetitions_per_size']} draws at each size, the RMSE of the "
        f"quadratic-cost budget estimate falls from {first['rmse']:.4f} at {first['prices']:,} prices "
        f"to {last['rmse']:.4f} at {last['prices']:,} prices. "
        r"This finite-design calculation shows the size of the errors. The rate in the theorem follows "
        r"from the proof rather than the simulation." "\n\n"
    )


def apply(text):
    marker = r"\section{Notation}\label{app:notation}"
    bibliography = r"\end{thebibliography}"
    declaration = r"\begin{thebibliography}"
    assert text.count(marker) == text.count(bibliography) == text.count(declaration) == 1
    text = text.replace(marker, SECTION + diagnostics() + marker)
    text = text.replace(
        declaration,
        r"The passive-price extension and its proof were verified and checked by the authors, who take full responsibility for the content. Its deterministic steps are checked in Lean~4 (\nolinkurl{PublicationRevision14.lean})."
        "\n\n" + declaration,
    )
    return text.replace(
        bibliography,
        r"\bibitem[Wu and Wang(2020)]{wuwang2020} Wu, C.-H., and T.-Y. Wang (2020). "
        r"The effects of reducing the securities transaction tax on day trading: Evidence from the Taiwan stock market. "
        r"\emph{Journal of Accounting Review} 70, 135--169." "\n" + bibliography,
    )
