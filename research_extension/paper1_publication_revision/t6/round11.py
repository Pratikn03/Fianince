"""Supplementary derivations and reproducible diagnostics for the instrument theorem."""

import json
from pathlib import Path


SECTION = r"""
\section{Derived incidence of price and quantity instruments}\label{app:instruments}

\paragraph{Perceived profits and the constant-signal response.}
A desk chooses a scale $q\ge0$ for exposure $q y_t$ at revision dates, with
$y_t=(1-r)\sum_{j\ge0}r^j x_{t-1-j}$. Conditional on this signal it forecasts return
$\beta\rho^j y_t$ in period $j$ of its planned $h$-period exposure. This is a
belief about the desk's returns. The actual stationary price law supplies second
moments, and trading can lose money under that law. Common $\beta>0$, $b>0$ and
$\rho\in[0,1]$ are known inputs. Per date the perceived gain is $\beta A_h V q$ and
the quadratic risk charge is $bVq^2/2$, where $A_h=h^{-1}\sum_{j=0}^{h-1}\rho^j$ and
$V=\operatorname{Var}(y_t)$. A zero-mean Gaussian revision of the unscaled signal has
variance $D_h=\operatorname{Var}(y_t-y_{t-h})$. Dividing expected volume and squared
changes by $h$ gives $qT_h$, $T_h=\sqrt{2D_h/\pi}/h$, and $q^2D_h/h$. With a linear
charge $\tau$, quadratic charge $\nu$, and per-desk cap $c$, the scalar optimum is
\[
 q^*(r;h,\tau,\nu,c)=\min\left\{\frac{c}{T_h},\,
          \frac{(\beta A_h V-\tau T_h)_+}{bV+\nu D_h/h}\right\}.
\]
Strict positivity of the spectrum gives $V,D_h>0$ at every $r<1$. With feasible
interior activity the first-order condition and strict concavity give the optimum.
A negative marginal gain at zero selects zero. If the unrestricted optimum exceeds
$c/T_h$, concavity selects that endpoint. A mass $m_i$ of desks gives pre-policy
merged weight $w_i=(1-r_i)m_iq^0(r_i)$. At a constant signal, each scheduled revision
takes the same target, and the mean response across a cycle scales by $q^*$. The
cyclic response to a varying signal can differ substantially. A literal exchange
resting-time rule acts on outstanding orders, and order-to-trade limits act on order
messages and executions. These mechanisms require additional state variables. A cap
applied to the entire class instead of each desk also introduces the class mass into
the incidence. The per-desk turnover cap here uses expected volume.

\paragraph{Reference moments and inference.}
Write $\gamma_j=\mathbb E[x_t x_{t-j}]$, $B(z)=\sum_k\gamma_k z^{|k|}$, and
$B_h(z)=\sum_k\gamma_{k+h}z^{|k|}$, summing over all integers. For pairs of filter
indices $i,j\ge0$ with $i-j=k$, the common factor sums to $r^{|k|}/(1-r^2)$. Thus
$\operatorname{Cov}(y_t,y_{t-h})=(1-r)B_h(r)/(1+r)$. The ratio $D_h/V$ equals
$(1-r)C_h/B$, where $C_h=2(B-B_h)/(1-z)$ and the value at $z=1$ is by continuation.
When $h$ is fixed, the geometric covariance assumption gives a common analytic
neighbourhood of the disk and uniformly bounded derivatives. On the unit circle
$\operatorname{Re}B$ is the spectrum under the covariance-series normalization.
The uniform positive lower bound and the maximum principle bound $B$ away from zero
throughout the disk. For small enough $\nu$ the denominators in the quadratic-cost
and scheduled-revision expressions remain separated from zero, uniformly over the
reference laws. Parseval's identity then bounds the Taylor coefficient norm by a
common constant. The loss of perceived gain from holding for $h$ periods contributes
$(1-A_h)/(1-r)$ to $g$. It reduces to a multiple of the initial aggregate budget,
and fails the coefficient criterion when $A_h<1$. For white noise and $\rho=1$,
$D_h/h=2V(1-r)h^{-1}\sum_{j<h}r^j\le D_1$. With a positive quadratic charge,
lengthening the schedule can therefore raise the feedback scale by lowering
adjustment costs.

For lag $j\le n/2$, Wick's formula bounds the variance of the sample mean of
$x_t x_{t-j}$ by a constant times $n^{-1}\sum_k(\gamma_k^2+
|\gamma_{k-j}\gamma_{k+j}|)$, hence by $C/n$ uniformly in $j$. The estimator uses a
centered reference signal. The expected uniform error of its covariance series on
$[0,\bar r]$ is bounded by this root mean square bound summed with geometric weights,
plus a geometric tail. Dividing by $1-r$ for $C_h$ is safe on the memory interval.
The bounded-denominator ratios inherit the same error after flooring estimated real
denominators. Projecting onto polynomials with a bounded Euclidean coefficient norm
guards the tap variance even though the covariance estimator was controlled on the
real interval alone. Independence of the reference record and the tap observations
justifies conditioning on the chosen coefficients. The result describes that
measurement contract, including its known preference inputs. Neither the desk's
beliefs nor the direct Gaussian taps are automatically observed on an exchange.

In the white-noise example, $V=\gamma_0(1-r)/(1+r)$ and
$D_h=2V(1-r^h)$. A positive linear tax with no cap gives
$\theta=\min\{1,d\sqrt{1+r}\}$ with $d=2\tau/(\beta\sqrt{\pi\gamma_0})$.
The active formula differs from $d\sqrt{2}/(1-r)$ in $g$ by
$-d/(\sqrt{1+r}+\sqrt{2})$, which is bounded on the unit disk. For this example
an independently known initial budget supplies the pole term. With that budget and the same tap and reference contract, the active effect in this example is parametric. If $r_e=d^{-2}-1$ is interior,
the right branch saturates continuously at exit and its derivative differs from
the left derivative. With daily revisions, zero charges, and white-noise reference
prices, $q^0 T_1$ is proportional to $(1-r)/\sqrt{1+r}$. This is strictly decreasing.
A cap strictly between its values at the ends of a positive-width memory interval
therefore has a transversal binding threshold. If the threshold is outside the
memory support, the same kink lower bound does not follow.

\paragraph{Local equilibrium feedback.}
Consider daily revisions and the stable low-impact branch of
Theorem~\ref{n:thm_inventory}(iv). Scale the desk masses by $s$ and write
$w_i(s)=s\bar w_i+o(s)$ with the reference moments evaluated at zero feedback.
Let $Q=\sum_i\bar w_i/(1-r_i)$. Holding the dealer primitives fixed,
\[
 D=1-s\kappa_-Q+o(s),\qquad
 \kappa=\kappa_-+
 s\,\frac{\kappa_-^2(\bar a+2A\kappa_-\sigma_\xi^2)}{\sqrt{\Lambda_0}}Q+o(s).
\]
The effective persistence changes through $a^*=\bar a/D$. These first-order changes
depend on $Q$. If the actual pre-policy spectrum is used by the desks, the spectral
map is differentiable locally on a uniformly stable daily-revision branch. For example,
on a finite set of memories it follows by differentiating the rational stable
transfer function for the stationary covariances. If the desk policy is on a smooth
branch and locally differentiable in those moments, the equilibrium equation for the
vector of aggregate scales has the form $q=s\,\mathcal Q(\gamma(q),\lambda)$ for
instrument parameter $\lambda$. Its derivative with respect to $q$ after moving
everything to the left is the identity at $s=0$. The implicit function theorem gives
a local fixed point with $q=s\,\mathcal Q(\gamma(0),\lambda)+o(s)$. The spectrum's
reaction enters at higher order on this branch. These arguments do not validate a
first-order calculation at a threshold or near loss of stability.

Even at zero feedback the first-order effective \emph{budget}, rather than
$(D,\kappa,a^*)$ alone, involves another quantity: since
$\tilde w_i=w_i(D-\bar a)/(D-r_i)$, its derivative is
\[
 \left.\frac{d S^*}{ds}\right|_{s=0}
   =\bar a\kappa_- Q + \kappa_-(1-\bar a)
                  \sum_i \frac{\bar w_i}{(1-r_i)^2}.
\]
At a nonzero-feedback equilibrium, differentiating $D=1-\kappa G(D)$ involves
$G'(D)$ and the policy perturbation of $G(D)$, so a composition-free correction
depending only on $G(1)$ does not hold in general.

\paragraph{Adjustable memory at an interior optimum.}
Suppose a smooth desk-specific tracking penalty or payoff selects an interior
optimum in $(q,r)$, and the Hessian $H$ there is strictly negative definite. A smooth
instrument $\lambda$ gives local derivatives $(\dot q,\dot r)=-H^{-1}
\nabla_{q,r}\partial_\lambda \Pi$ by the first-order conditions. The direct
fixed-impact budget derivative is $\kappa\sum_i m_i\dot q_i$. In merged coordinates
the identity
\[
 \frac{d}{d\lambda}\frac{w_i}{1-r_i}
   =\frac{\dot w_i}{1-r_i}+\frac{w_i\dot r_i}{(1-r_i)^2}=m_i\dot q_i
\]
uses fixed desk masses. If the optimized sensitivity satisfies
$-\dot q(r)/(q^0(r)(1-r))\in H^2$ with a controlled coefficient norm, and the
necessary preference inputs are known or estimated at the required rate, the
linearized reduction from $M$ admits the same certificate. A uniform analytic
extension with bounded denominators and bounded sensitivity on the disk is a
sufficient condition. Local real analyticity, an unidentified preference parameter,
an indefinite Hessian or an optimizer moving to a constraint cannot supply it.

\paragraph{Formal coverage.}
\path{CurrentProofs/Paper1InstrumentIncidence.lean} checks five rational identities:
the payoff difference after substitution of the interior first-order relation,
cross-multiplied quadratic attenuation, the finite geometric sum, the truncated quadratic-cost Taylor identity, and
cancellation of a common affine contribution in the kink budget calculation.
The real optimizer, infinite-series and analytic arguments, endpoint construction,
equilibrium claims, and statistical conclusions are proved on paper.

"""


def diagnostics():
    data = json.loads(Path(__file__).with_name("instrument_incidence_diagnostics.json").read_text())
    smooth = data["smooth"]
    kink = data["kink"]
    taiwan = data["taiwan_scenario"]
    foreign, trust = taiwan["rows"]
    return (
        r"\paragraph{Numerical checks.} The script \nolinkurl{instrument_incidence.py} compares the formula with numerical "
        rf"optimization. The maximum absolute scale discrepancy is $ {data['optimizer_max_abs_difference']:.2g}$. "
        r"An independent AR(1) reference record supplies an estimated persistence, and independent Gaussian tap means "
        rf"supply the kernel. Across $ {smooth['repetitions']}$ repetitions per sample size, the fitted log-RMSE "
        rf"slope is $ {smooth['rmse_slope']:.3f}$. Near proportional-tax exit, the fitted log budget-gap slopes "
        rf"for the two quadrature designs are $ {kink['2']['budget_slope']:.3f}$ and $ {kink['3']['budget_slope']:.3f}$. "
        r"The implied repetition counts for the exact Gaussian tap likelihood test at equal error "
        rf"$1/4$ have fitted log slopes $ {kink['2']['testing_slope']:.3f}$ and $ {kink['3']['testing_slope']:.3f}$. "
        r"The results are finite-design diagnostics."
        "\n\n"
        r"\paragraph{Taiwan coefficient illustration.} Using the archived P1M memories and positive contributions "
        r"for foreign investors and investment trusts, impose a hypothetical white-noise reference and "
        rf"tax multiplier $d={taiwan['normalized_tax']:g}$. The assumed benchmark reduces the two scales "
        rf"by $ {100*foreign['attenuation']:.1f}\%$ and $ {100*trust['attenuation']:.1f}\%$. "
        rf"The resulting reduction for those two contributions is $ {taiwan['feedback_reduction']:.6f}$. "
        r"The signed dealer contribution is held fixed. This exercise uses archived coefficients and imposed beliefs. "
        r"It estimates neither Taiwan tax elasticities nor causal effects."
        "\n\n"
    )


def apply(text):
    marker = r"\section{Notation}\label{app:notation}"
    assert text.count(marker) == 1
    text = text.replace(marker, SECTION + diagnostics() + marker)
    declaration = r"\begin{thebibliography}"
    assert text.count(declaration) == 1
    return text.replace(
        declaration,
        r"The derived-instrument result and its supplemental derivations were added with AI assistance "
        r"and have not yet been checked by the authors." "\n\n" + declaration,
    )
