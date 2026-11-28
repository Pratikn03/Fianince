"""Revision of 28 November 2026: responds to three AI referee reports and an AI editor's decision letter.

Applied after final_cut_1127 (main text: make_short.build; supplement: build_short.main). Every replacement asserts a
single match. Plan and status: ceiling_suite/papers/paper1/review/REVISION_1128_PLAN.md.

AUTHORS_CHECKED_1128 stays False until the first author says the authors have read and checked the revision; the AI
declaration says so until then.
"""
import json
from pathlib import Path

AUTHORS_CHECKED_1128 = False

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HOLDOUT = json.loads((ROOT / 'ceiling_suite/p1_empirics/results/p1t_holdout_results_full_A4.json').read_text())


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, ('revision_1128', old[:160], n, count)
    return t.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------
# Main text
# ---------------------------------------------------------------------------------------------------------------

ABSTRACT_OLD = r"""We study financial markets in which heterogeneous trading algorithms feed a common public pricing signal back into order flow. In a linear market and in a stationary inventory-dealer equilibrium, every public outcome---prices, volume, dealer inventories and optimal forecasts---depends on the trader population only through its aggregate feedback kernel. This yields a supervisory separation. Once persistence and impact are known, whether a uniform feedback cut meets a stability ceiling can be learned from the aggregate response at a cost that does not depend on how close the traders' memories are, and without class tags the uniform cut is minimax over labelings. Whether a targeted restriction meets the same ceiling can require of order $\Delta^{-(4K-2)}$ observations when $K$ classes have memory rates within $\Delta$, even near instability or under active probes; verified class tags, or a pilot of the restriction itself, remove that penalty. Cheap relabeling across accounts erodes tags, and untagged surveillance invites traders to crowd their memories. Class-tagged flows from the Taiwan Stock Exchange calibrate the gap."""

ABSTRACT_NEW = r"""We study markets in which heterogeneous trading algorithms feed a common public pricing signal back into order flow. In a linear market and in a stationary inventory-dealer equilibrium, every public outcome depends on the trader population only through its aggregate feedback kernel. Within one passive record of pricing errors this yields a supervisory separation. With impact and persistence held fixed, whether a uniform feedback cut meets a stability ceiling depends only on the aggregate budget, which the record estimates at a near-parametric rate however close the traders' memories are. In the dealer equilibrium the cut moves impact and persistence; on the principal equilibrium branch it still lowers the budget, and its size is learned at a slower rate that again does not depend on the spacing of memories. Whether a targeted restriction meets the ceiling can require of order $\Delta^{-(4K-2)}$ observations when $K$ classes have memory rates within $\Delta$; verified class tags, or a pilot of the restriction, remove that penalty. Cheap relabeling erodes tags, and against a fixed untagged test traders gain by crowding their memories. Class-tagged flows from the Taiwan Stock Exchange illustrate the magnitudes."""

FRONT_OLD = r"""Technical lemmas, extended proofs, numerical robustness checks, and Lean~4 machine-checked formalizations of deterministic algebraic steps (with probabilistic and asymptotic steps proved on paper) are provided in the Online Supplement and public replication archive (\url{https://github.com/Pratikn03/Fianince})."""

FRONT_NEW = r"""Technical lemmas, extended proofs and numerical checks are in the Online Supplement. Lean~4 formalizations check the deterministic steps and several finite-sample probability bounds; asymptotic steps are proved on paper. Supplement Table~\ref{S-tab:claims} records, for every main-text result, whether it is proved in Lean from Mathlib, proved in Lean under stated hypotheses, or proved on paper only. The replication archive is \url{https://github.com/Pratikn03/Fianince} (version of 28 November 2026)."""

EXAMPLE_OLD = r"""Prices clear only aggregate order flow, so the two blend: together they produce nearly the same flow as a single group at $0.50$. The first- and second-order differences cancel, the remaining difference in lag curvature is of order $\Delta^3$ with $\Delta = 0.01$, and detecting it takes of order $\Delta^{-6}$ noisy observations; with $K$ nearby groups it takes $\Delta^{-(4K-2)}$. A uniform cut does not care about this blending. A targeted halt does."""

EXAMPLE_NEW = r"""Prices clear only aggregate order flow, so the two blend: together they produce nearly the same flow as a single group at $0.50$. The first-order difference cancels, the second lag tap differs by order $\Delta^2$ with $\Delta = 0.01$, and detecting the difference takes of order $\Delta^{-4}$ noisy observations. Populations of two groups each can be matched more closely: pairs that agree through the second moment differ at order $\Delta^3$ and need of order $\Delta^{-6}$ observations, and with $K$ nearby groups on each side the requirement is $\Delta^{-(4K-2)}$. A uniform cut does not care about this blending. A targeted halt does."""

MODEL_OLD = r"""In Section~\ref{sec:equilibrium}, price impact and the persistence of pricing errors come from competitive, risk-averse dealers who carry inventory, and equilibrium prices follow the same closed-loop recursion with unchanged memory rates (Theorems~\ref{n:thm_inventory} and~\ref{n:thm_eqreduced}). The barriers below are therefore equilibrium properties, not artifacts of mechanical price impact."""

MODEL_NEW = r"""In Section~\ref{sec:equilibrium}, price impact comes from competitive, risk-averse dealers who carry inventory, and the persistence of pricing errors from the share of inventory they carry overnight, which we take as given. Dealers observe the pricing error, and the equilibrium depends on the population only through the merged measure, the one population object they need. Equilibrium prices follow the same closed-loop recursion with unchanged memory rates (Theorems~\ref{n:thm_inventory} and~\ref{n:thm_eqreduced}), so the identification barriers below are equilibrium properties, not artifacts of mechanical price impact; Theorem~\ref{n:eqcut} takes the uniform cut into the same equilibrium."""

MAIN_RESULT_OLD = r"""\textbf{The main result.} Theorem~\ref{n:separation} is a supervisory separation. Given persistence, impact and a memory bound, whether a uniform feedback cut meets a stability ceiling depends on the population only through the aggregate budget. Kernel-tap records, or one passive price record, estimate that budget at a near-parametric rate however close the traders' memories are (Theorem~\ref{n:passiveupper}), and without tags the uniform cut is minimax over labelings (Theorem~\ref{n:minimax}). Whether a targeted restriction meets the same ceiling can require $c\sigma^2(\Delta\eta)^{-(4K-2)}$ records (Proposition~\ref{n:target}). There are two ways around this. Verified class tags remove the spacing penalty for class weights (Theorem~\ref{n:disc}). A pilot of the restriction does the same after the fact: once a restriction is in force, the change in the price response is the removed groups' own kernel, so prices alone learn the restriction's effect at a near-parametric rate (Theorem~\ref{n:pilot})."""

MAIN_RESULT_NEW = r"""\textbf{The main result.} Theorem~\ref{n:separation} is a supervisory separation stated inside one experiment. In one passive record of pricing errors, given persistence, impact and a memory bound, whether a uniform feedback cut meets a stability ceiling depends on the population only through the aggregate budget, which the record estimates at a near-parametric rate however close the traders' memories are (Theorem~\ref{n:passiveupper}); whether a targeted restriction meets the same ceiling can require of order $(\Delta\eta)^{-(4K-2)}$ observations of the same record (Proposition~\ref{n:target}). The same separation holds for reset probes, where verified class tags also remove the spacing penalty for class weights (Theorem~\ref{n:disc}), and without tags the uniform cut is minimax over labelings (Theorem~\ref{n:minimax}). Theorem~\ref{n:eqcut} takes the uniform cut into the dealer equilibrium, where the cut moves impact and persistence. The post-cut budget then depends on the population through the Stieltjes transform of the merged measure at the new dealer root, so the fixed-impact formula is wrong in size and, on a lower equilibrium branch, in sign. On the principal branch a cut lowers the budget, populations that prices cannot tell apart end within $(\Delta\eta)^{2K-1}$ of each other, and one passive record estimates the post-cut budget at a polynomial rate that does not depend on the spacing. A pilot of a targeted restriction removes the penalty after the fact: the pilot record identifies the post-restriction budget directly, and the change in the price response identifies the removed groups' kernel, exactly when impact is fixed and after a correction fixed by the two dealer roots in equilibrium (Theorem~\ref{n:pilot})."""

LIMITS_OLD = r"""Divergence scales as $N\delta^4$ in the memory distance $\delta$, so the supervisor's information falls at rate $N^{-1}$ and detection collapses toward the false-alarm rate (Theorem~\ref{n:paradox}). A longer price record therefore never substitutes for an owner-linked one: in equilibrium its value falls like $N^{-1/2}$ (Theorem~\ref{n:recordvalue})."""

LIMITS_NEW = r"""Divergence scales as $N\delta^4$ in the memory distance $\delta$, so the supervisor's information falls at rate $N^{-1}$ and detection collapses toward the false-alarm rate (Theorem~\ref{n:paradox}). This is the group's best response to a fixed test, not an equilibrium with an optimizing supervisor; a two-sided test, whose power rises with the divergence rather than its square root, slows the crowding. A longer price record therefore does not substitute for an owner-linked one: against a group that best-responds to a one-sided test, the price record's value is at most of order $N^{-1/2}$, and at most of order $N^{-1/6}$ against a two-sided test (Theorem~\ref{n:recordvalue})."""

NOVELTY_OLD = r"""We do not claim those results as new. Three statistical results here have no counterpart in that literature, because they use features a mixture lacks: a single closed-loop price record attains the rate (Theorem~\ref{n:passiveupper}), the barrier survives the approach to instability (Supplement Proposition~\ref{S-prop:nearcrit}), and a restriction deletes part of the population, so a pilot collapses the exponent (Theorem~\ref{n:pilot}). That market-wide policies need only a reduced-form aggregate while targeted ones need structure is Marschak's maxim and the logic of sufficient statistics for policy (Marschak, 1953; Chetty, 2009). What we add is the informational price of that structure in a feedback market: kernel sufficiency survives inventory-equilibrium pricing, in which dealer anticipation over-weights slow memories; uniform rules are minimax over labelings and separate cleanly from targeted ones; and tags have strategic limits, both from relabeling and from crowding."""

NOVELTY_NEW = r"""We do not claim those results. Three statistical results adapt known tools to the closed loop. Theorem~\ref{n:passiveupper} feeds a long autoregression (Berk, 1974) into Prony's method. Its closest relatives are single-path estimation of the distribution of autoregressive coefficients from autocovariances (Leipus et al., 2006; Celov et al., 2010) and non-asymptotic identification of linear systems from one trajectory (Simchowitz et al., 2018; Oymak and Ozay, 2019; Sarkar et al., 2021); what the feedback market adds is that the autoregressive coefficients are the kernel taps and that positivity bounds the spectrum uniformly in the population, so the tap error does not depend on the spacing. Supplement Proposition~\ref{S-prop:nearcrit} is a near-unit-root statement: matched budgets make the composition difference vanish at zero frequency, so, as in the near-unit-root asymptotics of Chan and Wei (1988) and Sims et al.\ (1990), information about directions other than the long-run one stays bounded. Theorem~\ref{n:pilot} is a corollary of Theorem~\ref{n:cost}(iii) once a restriction deletes part of the population. That market-wide policies need only a reduced-form aggregate while targeted ones need structure is Marschak's maxim and the logic of sufficient statistics for policy (Marschak, 1953; Chetty, 2009). What we add is the informational price of that structure in a feedback market and its equilibrium form: kernel sufficiency survives inventory-equilibrium pricing, in which dealer anticipation over-weights slow memories; in that equilibrium the reduced form a market-wide cut needs is more than the aggregate budget, yet it is still learned without the spacing penalty (Theorem~\ref{n:eqcut}); uniform rules are minimax over labelings; and tags have strategic limits, both from relabeling and from crowding."""

ILLUSTRATION_OLD = r"""\textbf{Empirical illustration.} Using daily class-tagged institutional order flows from the Taiwan Stock Exchange (300 stocks, 2013--2016, 270,060 stock-days), we calibrate the bounds to observed institutional rules (foreign investors, investment trusts and dealers). Granting a price-only supervisor the market's persistence, impact and non-feedback flow law, tagged flows carry, at leading order, $4.7 \times 10^5$ times more information per stock-day about composition than prices. On the same grant, a spectral-rate search pins market-wide cut effects to $[0.0014, 0.0019]$, whereas the price-consistent effect of halting foreign feedback spans $[0, 0.0018]$ under nonnegative weights---from zero to nearly the entire aggregate effect (Section~\ref{sec:taiwan})."""

ILLUSTRATION_NEW = r"""\textbf{Empirical illustration.} Daily class-tagged institutional order flows from the Taiwan Stock Exchange (300 stocks, 2013--2016) illustrate the model's magnitudes (Section~\ref{sec:taiwan}). At daily frequency the feedback share is small. With impact and non-feedback flow granted, the price-consistent effect of halting foreign feedback ranges from zero to the whole uniform effect. The exercise is an illustration, not a test: the persistence it displays is largely produced by the detrending filter, the tags identify class contributions only under the restriction that feedback memory equals flow persistence, and a registered out-of-sample test of the feedback premise does not separate feedback from prices revealing past flow."""

ROADMAP_OLD = r"""Section~\ref{sec:supervision} analyzes minimax policy, disclosure, relabeling, the surveillance paradox, and the Taiwan calibration. Section~\ref{sec:conclusion} discusses scope and concludes. Appendix~\ref{app:proofs} proves the headline results (Theorems~\ref{n:suff}, \ref{thm:what-id}, \ref{n:passiveupper}, \ref{n:separation} and~\ref{n:pilot}); the other proofs are in Supplement Section~\ref{S-app:proofs}."""

ROADMAP_NEW = r"""Section~\ref{sec:supervision} analyzes the separation, the uniform cut in equilibrium, minimax policy, disclosure, relabeling, the surveillance paradox, and the Taiwan illustration. Section~\ref{sec:conclusion} discusses scope and concludes. Appendix~\ref{app:proofs} proves the headline results (Theorems~\ref{n:suff}, \ref{thm:what-id}, \ref{n:passiveupper}, \ref{n:separation}, \ref{n:eqcut} and~\ref{n:pilot}); the other proofs are in Supplement Section~\ref{S-app:proofs}."""

MARKET_MAKER_OLD = r"""by contrast, a risk-neutral rational market maker who knows the aggregate flow rule nets out predictable feedback flow entirely, so prices reveal \emph{less}, not more, about the population (Niroula et al., 2026c, Proposition~C2.1(iv))."""

MARKET_MAKER_NEW = r"""by contrast, a risk-neutral market maker who knows the aggregate flow rule would net out predictable feedback flow, so prices would reveal \emph{less}, not more, about the population (no result here uses this; Niroula et al., 2026c, Proposition~C2.1(iv), states it formally)."""

HORIZON_OLD = r"""The two games share identical strategy sets and payoff functions, and hence identical equilibria under any solution concept defined from public histories and payoffs."""

HORIZON_NEW = r"""For games that end by date $T$, the two games share identical strategy sets and payoff functions, and hence identical equilibria under any solution concept defined from public histories and payoffs; with equal kernels at every lag the statement holds for every horizon."""

FOLD_OLD = r"""Under the standard non-degenerate quadratic fold condition $F_{DD}(D_{\mathrm{crit}}; \lambda_{\mathrm{crit}}) > 0$ on $F_-(D; \lambda) \equiv D - 1 + \lambda \kappa_-(D) S_M(D)$ (automatic for $K=1$, generic for $K \ge 2$), as"""

FOLD_NEW = r"""Under the non-degenerate quadratic fold condition $F_{DD}(D_{\mathrm{crit}}; \lambda_{\mathrm{crit}}) > 0$ on $F_-(D; \lambda) \equiv D - 1 + \lambda \kappa_-(D) S_M(D)$, which we assume, as"""

BRANCH_OLD = r"""For $K \ge 2$ with $\max_i r_i > D_{\min}$, secondary inter-pole branches may exist on $(D_{\min}, \max_i r_i)$, while long-run dealer entry unfolds the fixed-$A$ cliff into a smooth schedule (Supplement Section~\ref{S-sec:mixed_sign} and Figure~\ref{S-fig:supp_fragility})."""

BRANCH_NEW = r"""The interval $(\max(D_{\min}, \max_i r_i), 1]$ can hold more than one root: with the primitives of Supplement Theorem~\ref{S-thm:eqreduced}(iv) both $D = 0.80$ and $D = 0.862$ are equilibria. We call the largest root the principal equilibrium; it is the one reached continuously from the no-feedback equilibrium as feedback is scaled up, and Theorem~\ref{n:eqcut} shows that comparative statics reverse on a root below it. For $K \ge 2$ with $\max_i r_i > D_{\min}$, further inter-pole branches may exist on $(D_{\min}, \max_i r_i)$, while long-run dealer entry unfolds the fixed-$A$ cliff into a smooth schedule (Supplement Section~\ref{S-sec:mixed_sign} and Figure~\ref{S-fig:supp_fragility})."""

PART_IV_OLD = r"""Part~(iv) uses the reset contract of Section~\ref{sec:cost}, a benchmark for what data can reveal rather than a description of a running market."""

PART_IV_NEW = r"""Part~(iv) uses the reset contract of Section~\ref{sec:cost}, a benchmark for what data can reveal rather than a description of a running market; the finite-record bound in the proof of Theorem~\ref{n:cost} gives the same order for one passive record. With the primitives of its realization both equilibrium roots satisfy part~(iv) (Supplement Section~\ref{S-sec:eqcut})."""

PASSIVE_TITLE_OLD = r"""\textbf{One passive price record attains the rates.} The upper bound in Theorem~\ref{n:cost}(iii) uses reset experiments. A single stationary record suffices too,"""

PASSIVE_TITLE_NEW = r"""\textbf{One passive pricing-error record attains the rates.} The upper bound in Theorem~\ref{n:cost}(iii) uses reset experiments. A single stationary record of pricing errors suffices too,"""

PASSIVE_THM_OLD = r"""\begin{theorem}[One passive price record attains the rates]\label{n:passiveupper}"""

PASSIVE_THM_NEW = r"""\begin{theorem}[One passive pricing-error record attains the rates]\label{n:passiveupper}"""

PASSIVE_CONST_OLD = r"""The constants $C$ and $\epsilon_0$ depend only on $(\kappa, m, \bar r, \bar W)$ and, in~(ii), on $K$, $r_c$, $\Delta\eta_0$ and the class."""

PASSIVE_CONST_NEW = r"""The constants $C$ and $\epsilon_0$ depend only on $(\kappa, m, \bar r, \bar W)$ and, in~(ii), on $K$, $r_c$, $\Delta\eta_0$ and the class; through the threshold $T \ge 128 L^2/(m^4\beta)$, $C$ is of order $m^{-4}$ in the stability margin."""

SIM_OLD = r"""and weight errors have fitted slopes $-2.5$ in $\log\Delta\eta$ over $\Delta\eta \in [0.36, 0.70]$ (the asymptotic exponent $-3$ is approached as the spacing shrinks) and $-0.45$ in $\log T$."""

SIM_NEW = r"""and weight errors have fitted slopes $-2.5$ in $\log\Delta\eta$ over $\Delta\eta \in [0.36, 0.70]$ and $-0.45$ in $\log T$. These spacings are far from the collision regime, so the simulation illustrates the estimator; it does not test the asymptotic exponent $-3$."""

OPPOSITE_OLD = r"""One might conjecture that as a market approaches instability ($S \uparrow 1$), feedback amplification magnifies compositional differences and makes traders easier to distinguish. The opposite holds. Give the hard pair"""

OPPOSITE_NEW = r"""One might conjecture that as a market approaches instability ($S \uparrow 1$), feedback amplification magnifies compositional differences and makes traders easier to distinguish. It does so only boundedly. Give the hard pair"""

OPPOSITE2_OLD = r"""The passive KL divergence per observation then remains bounded by $C(\Delta\eta)^{4K-2}$ uniformly in $\epsilon > 0$ (Supplement Proposition~\ref{S-prop:nearcrit}). As Figure~\ref{fig:near-instability} illustrates,"""

OPPOSITE2_NEW = r"""The passive KL divergence per observation then remains bounded by $C(\Delta\eta)^{4K-2}$ uniformly in $\epsilon > 0$ (Supplement Proposition~\ref{S-prop:nearcrit}): the gain from approaching instability is bounded and the exponent is unchanged. In Table~\ref{tab:years} the required years fall by factors of $1.35$ to $2.3$ as $1 - S$ falls from $0.1$ to $10^{-6}$. As Figure~\ref{fig:near-instability} illustrates,"""

TABLE2_NOTE_OLD = r"""\emph{Notes:} Rate-based proxy $\ln(5)/D$, where $D$ is the stationary Gaussian KL rate computed from the closed-form Gaussian spectra at a common persistence and a common feedback budget $S$ (the Gauss--Radau weights rescaled to match the budget), $\kappa = 0.5$, and feedback share $\kappa \sum_i q_i = 0.3$ (total weight $0.6(1 - r_c)$ of the Gauss economy), assuming $252$ trading days per year."""

TABLE2_NOTE_NEW = r"""\emph{Notes:} Rate-based proxy $\ln(5)/D$ (the Bretagnolle--Huber bound for $5\%$ per error), where $D$ is the stationary Gaussian KL rate of the Gauss--Radau economy's law from the Gauss economy's, computed from the closed-form spectra at a common persistence and a common feedback budget $S$ (the Gauss--Radau weights rescaled to match the budget), $\kappa = 0.5$, and feedback share $\kappa \sum_i q_i$ of about $0.3$ (from $0.30$ to $0.33$ across rows; total weight $0.6(1 - r_c)$ of the Gauss economy), assuming $252$ trading days per year. The rows are worst-case (minimax) benchmarks."""

QUESTIONS_PRE_OLD = r"""When independent measurements of kernel lags are available, composition is only one functional of the merged measure $M$."""

QUESTIONS_PRE_NEW = r"""Suppose the supervisor can measure kernel taps directly. A steering probe that trades against aggregate feedback flow so as to hold the pricing error at a unit impulse ($x_0 = 1$, $x_t = 0$ afterwards, from zero group states) meets, at date $t + 1$, the aggregate feedback flow $\sum_i w_i r_i^t = k_t$, so each such experiment records the taps. This benchmark observes aggregate (untagged) feedback flow and is therefore more informative than a price-only record. Composition is then only one functional of the merged measure $M$."""

MODULUS_OLD = r"""  \item[(i)] \emph{Exact modulus cost.} The minimum number of experiments $N_{\mathrm{cert}}(\epsilon; F_g)$ required to certify $F_g(M)$ to half-width $\epsilon$ at confidence level $1-\alpha$ is bounded by the necessary condition $\omega_L(2z_{1-\alpha}\sigma/\sqrt N)\le2\epsilon$ and the sufficient condition $\omega_L(2z_{1-\alpha/2}\sigma/\sqrt N)\le2\epsilon$, where the modulus is"""

MODULUS_NEW = r"""  \item[(i)] \emph{Modulus cost.} The minimum number of experiments $N_{\mathrm{cert}}(\epsilon; F_g)$ required to certify $F_g(M)$ to half-width $\epsilon$ at confidence level $1-\alpha$ lies between the necessary condition $\omega_L(2z_{1-\alpha}\sigma/\sqrt N)\le2\epsilon$ and the sufficient condition $\omega_L(2z_{1-\alpha/2}\sigma/\sqrt N)\le2\epsilon$, which differ only in the normal quantile; the modulus is"""

MODULUS2_OLD = r"""\Bigr\}
  \]
  governed by this common modulus.
  \item[(ii)]"""

MODULUS2_NEW = r"""\Bigr\}.
  \]
  \item[(ii)]"""

BOUNDARY_OLD = r"""total feedback weight $\Phi = \sum_m k_m$ sits on the boundary at $O(\sigma^2 \epsilon^{-2} \log(1/\epsilon))$ (Niroula et al., 2026b); and individual group weights are nonlinear functionals costing $(\Delta\eta)^{-(4K-2)}$."""

BOUNDARY_NEW = r"""total feedback weight $\Phi = \sum_m k_m$ is not parametric, because its tap coefficients are all one, yet summing taps at logarithmic depth estimates it with $O(\sigma^2 \epsilon^{-2} \log(1/\epsilon))$ experiments (the argument for Theorem~\ref{n:separation}(iii); Niroula et al., 2026b, show that the logarithm cannot be removed, which no result here uses); and individual group weights are nonlinear functionals costing $(\Delta\eta)^{-(4K-2)}$."""

SEP_COR_OLD = r"""Fix $K \ge 2$, accuracy $\epsilon > 0$, and any cheap functional $F_g$ satisfying Theorem~\ref{n:questions}(ii). Over $K$-group populations with memory spacing $\Delta\eta$, the ratio of experiments needed to recover group weights within a fixed fraction of total weight to the experiments needed to certify $F_g$ within $\epsilon$ is at least $c \epsilon^2 (\Delta\eta)^{-(4K-2)}$, diverging as $\Delta\eta \to 0$."""

SEP_COR_NEW = r"""Fix $K \ge 2$, accuracy $\epsilon > 0$, and any cheap functional $F_g$ satisfying Theorem~\ref{n:questions}(ii). In the tap-measurement experiment of Theorem~\ref{n:questions}, over $K$-group populations with memory spacing $\Delta\eta$, the ratio of experiments needed to recover group weights within a fixed fraction of total weight to the experiments needed to certify $F_g$ within $\epsilon$ is at least $c \epsilon^2 (\Delta\eta)^{-(4K-2)}$, diverging as $\Delta\eta \to 0$. Both counts are for the same experiment: the hard pair's taps differ by $O((\Delta\eta)^{2K-1})$ in $\ell^2$ (proof of Theorem~\ref{n:cost}), and Theorem~\ref{n:questions}(ii) gives $O(\sigma^2\epsilon^{-2})$ for $F_g$."""

INSTRUMENTS_OLD = r"""We now derive regulatory implications, moving from static ceilings and countercyclical pre-funded margin buffers to minimax policy design, class-tagged disclosure, and empirical calibration."""

INSTRUMENTS_NEW = r"""We now derive regulatory implications, moving from static ceilings to minimax policy design, class-tagged disclosure, and an empirical illustration. \textbf{Instruments and information.} A uniform cut scales every group's feedback weight by the same factor $\theta$; it idealizes market-wide measures whose incidence does not depend on who trades, and Supplement Proposition~\ref{S-thm:instruments} shows which real charges keep that property (smooth incidence across memories) and which lose it. A class halt is different: a supervisor who halts a class must be able to identify its accounts when it acts, and a supervisor who can do that can also record their flows. The price-only benchmark answers what such records are worth before the halt; Theorem~\ref{n:disc} and Proposition~\ref{n:relabel} value them."""

SEP_SETUP_OLD = r"""The results of this section combine into one statement. Fix $K \ge 2$, known $(a, \kappa)$, a memory bound $\bar r < 1$ on total merged weight at most $\bar W$, and a ceiling $\bar s \in (a, 1)$ in a positive, stable market. Records are $N$ independent experiments with Gaussian noise of variance $\sigma^2$: direct kernel-tap measurements as in Theorem~\ref{n:questions} for part~(i), and the reset contract of Theorem~\ref{n:cost} for parts~(ii) and~(iii)."""

SEP_SETUP_NEW = r"""The results of this section combine into one statement, made inside a single experiment. Fix $K \ge 2$, known $(a, \kappa)$, a memory bound $\bar r < 1$, total merged weight at most $\bar W$, and a ceiling $\bar s \in (a, 1)$ in a positive, stable market. A \emph{passive record} is one stationary record of the pricing error with i.i.d.\ Gaussian news; a \emph{reset record} is one of $N$ independent reset experiments of Theorem~\ref{n:cost}, each recording the impulse response with independent $N(0, \sigma^2)$ noise."""

SEP_THM_OLD = r"""\begin{theorem}[The supervisory separation]\label{n:separation}
\begin{enumerate}
  \item[(i)] \emph{Uniform cuts need only the aggregate.} Whether scaling all feedback by $\theta \in [0, 1]$ meets $\bar s$ depends on the population only through the budget $S$. For every $\epsilon \in (0, 1)$ and $\beta \in (0, 1)$, $S$ is estimated to accuracy $\epsilon$ with probability at least $1 - \beta$ from $N = O(\sigma^2 \kappa^2 \epsilon^{-2} \log(1/\epsilon) \log(1/\beta))$ records at tap depth $O(\log(1/\epsilon))$, with constants depending only on $(\kappa, \bar r, \bar W)$ and not on the number of groups or the spacing of their memory rates; if $S \le 1 - m$ for a fixed margin $m$, one passive price record of length $O(\epsilon^{-2}\log^2(1/\epsilon))$ suffices as well. Without tags, for convex prudential loss and continuous, convex, label-symmetric cost, uniform scaling is minimax over labelings.
  \item[(ii)] \emph{Targeted restrictions need composition.} For halting the largest group, and for halting every group whose memory lies below a cutoff, there are pairs of $K$-group economies with memory rates in an interval of length $3\Delta\eta$ on which, over a nonempty interval of ceilings, the restriction meets $\bar s$ in one economy and breaches it in the other; deciding which, with both error probabilities at most $1/4$, requires $N \ge c\, \sigma^2 (\Delta\eta)^{-(4K-2)}$ records.
  \item[(iii)] \emph{Verified tags remove the spacing penalty for weights.} If each class's flow is also recorded at the first two response dates, then over the families of Theorem~\ref{n:disc} recovering class weights to a fixed accuracy below half the weight gap of the hard pair requires a number of experiments that does not grow as $\Delta\eta \to 0$; recovering memory rates to accuracy $c_0 \Delta\eta$ still requires order $(\Delta\eta)^{-2}$.
\end{enumerate}
\end{theorem}

Part~(i) is a statement about the aggregate alone; parts~(ii) and~(iii) say that composition is what a targeted rule needs and what tags supply."""

SEP_THM_NEW = r"""\begin{theorem}[The supervisory separation]\label{n:separation}
\emph{In one passive record of length $T$:}
\begin{enumerate}
  \item[(i)] \emph{Uniform cuts need only the aggregate.} With impact and persistence held fixed, whether scaling all feedback by $\theta \in [0, 1]$ meets $\bar s$ depends on the population only through the budget $S$. If $S \le 1 - m$ for a fixed margin $m$, the record estimates $S$ to accuracy $\epsilon$ with probability at least $1 - 3\beta$ once $T \ge C\epsilon^{-2}\beta^{-1}\log^2(1/(\epsilon\beta))$, with $C$ depending only on $(\kappa, m, \bar r, \bar W)$ and not on the number of groups or the spacing of their memory rates. Without tags, for convex prudential loss and continuous, convex, label-symmetric cost, uniform scaling is minimax over labelings.
  \item[(ii)] \emph{Targeted restrictions need composition.} For halting the largest group, and for halting every group whose memory lies below a cutoff, there are pairs of $K$-group economies with memory rates in an interval of length $3\Delta\eta$ on which, over a nonempty interval of ceilings, the restriction meets $\bar s$ in one economy and breaches it in the other; deciding which, with both error probabilities at most $1/4$, requires $T \ge c\,(\Delta\eta)^{-(4K-2)}$, and on the compact classes of Theorem~\ref{n:cost}(iii) a record of that length up to a logarithm suffices.
\end{enumerate}
\emph{In $N$ reset records:}
\begin{enumerate}
  \item[(iii)] \emph{The same separation.} If $S \le 1 - m$, the summed impulse response estimates $S$ to accuracy $\epsilon$ with probability at least $1 - \beta$ from $N = O(\sigma^2 \kappa^{-2} \epsilon^{-2} \log(1/\epsilon) \log(1/\beta))$ records at depth $O(\log(1/\epsilon))$, with constants depending only on $(a, \kappa, m, \bar r, \bar W)$, while the targeted decisions of~(ii) require $N \ge c\, \sigma^2 (\Delta\eta)^{-(4K-2)}$ records.
  \item[(iv)] \emph{Verified tags remove the spacing penalty for weights.} If each class's flow is also recorded at the first two response dates, then over the families of Theorem~\ref{n:disc} recovering class weights to a fixed accuracy below half the weight gap of the hard pair requires a number of experiments that does not grow as $\Delta\eta \to 0$; recovering memory rates to accuracy $c_0 \Delta\eta$ still requires order $(\Delta\eta)^{-2}$.
\end{enumerate}
\end{theorem}

Parts~(i) and~(iii) are statements about the aggregate alone; parts~(ii)--(iv) say that composition is what a targeted rule needs and what tags supply. With impact and persistence endogenous, the uniform cut needs more than the budget; Theorem~\ref{n:eqcut} gives what it needs and shows that one passive record still supplies it without the spacing penalty."""

TARGET_PRE_OLD = r"""For the post-policy calculation, hold dealers, price impact, persistence and the remaining rules fixed. Suppose a supervisor must keep the feedback budget $S = a + \kappa \sum_i q_i$ below a prudential ceiling $\bar{s} \in (a, 1)$ in a positive, stable market with known $(a, \kappa)$."""

TARGET_PRE_NEW = r"""For the post-policy calculation in Proposition~\ref{n:target}, hold dealers, price impact, persistence and the remaining rules fixed; Theorem~\ref{n:eqcut} below drops this assumption for the uniform cut. Suppose a supervisor must keep the feedback budget $S = a + \kappa \sum_i q_i$ below a prudential ceiling $\bar{s} \in (a, 1)$ in a positive, stable market with known $(a, \kappa)$. With a contrarian class ($q_i < 0$) a uniform cut also scales the negative contributions, so it lowers $S$ only when net feedback is positive; the ceiling bounds the budget, not any class's activity."""

TARGET_II_OLD = r"""deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$ under the reset contract of Theorem~\ref{n:cost}.
  \item[(iii)]"""

TARGET_II_NEW = r"""deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$ under the reset contract of Theorem~\ref{n:cost}, and from one passive record requires $T \ge c (\Delta\eta)^{-(4K-2)}$.
  \item[(iii)]"""

TARGET_III_OLD = r"""deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$.
\end{enumerate}
\end{proposition}"""

TARGET_III_NEW = r"""deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$, and from one passive record requires $T \ge c (\Delta\eta)^{-(4K-2)}$.
\end{enumerate}
\end{proposition}"""

INFO_UNIFORM_OLD = r"""summing noisy kernel-tap measurements at logarithmic depth estimates $S$ to accuracy $\epsilon$ in $O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments (Theorem~\ref{n:separation}(i)); one passive price record suffices at rate $O(\epsilon^{-2}\log^2(1/\epsilon))$ (Theorem~\ref{n:passiveupper}(i))."""

EQCUT_BLOCK = r"""summing the impulse response of reset records at logarithmic depth estimates $S$ to accuracy $\epsilon$ in $O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments (Theorem~\ref{n:separation}(iii)); one passive pricing-error record suffices at rate $O(\epsilon^{-2}\log^2(1/\epsilon))$ (Theorem~\ref{n:separation}(i)).

\textbf{The uniform cut in equilibrium.} Proposition~\ref{n:target}(i) holds dealers, impact and persistence fixed. In the inventory equilibrium of Section~\ref{sec:equilibrium} they move with the cut. Scale every group's feedback weight by $\theta \in [0, 1]$. With $\kappa_-(D) = D\{(D - \bar a) - [(D - \bar a)^2 - 4A^2\sigma_F^2\sigma_\xi^2]^{1/2}\}/(2A\sigma_\xi^2)$ the low-impact dealer root at a given $D$, Theorem~\ref{n:thm_inventory}(i) makes the post-cut equilibria the roots of
\begin{equation}\label{eq:Fcut}
  F(D; \theta) = D - 1 + \theta\, \kappa_-(D)\, S_M(D), \qquad D \in (\max(D_{\min}, \max_i r_i), 1].
\end{equation}
The largest root is the principal equilibrium $D_\theta$ (Section~\ref{sec:equilibrium}). Since $F(1; \theta) > 0$, $\partial_D F \ge 0$ there, with equality only at a fold. Write $S^*_\theta$ for the effective budget of a post-cut equilibrium, the budget of its reduced form in Theorem~\ref{n:thm_eqreduced}(i).

\begin{theorem}[The uniform cut in equilibrium]\label{n:eqcut}
Fix the dealer primitives $(\bar a, A, \sigma_F^2, \sigma_\xi^2)$ with $\Lambda_0 > 0$ and a positive population ($w_i > 0$) with memory rates at most $\bar r < 1$.
\begin{enumerate}
  \item[(i)] \emph{The post-cut budget.} At every root $D$ of~\eqref{eq:Fcut},
  \[
    S^*_\theta = 1 - \Bigl(1 - \frac{\bar a}{D}\Bigr)\frac{S_M(1)}{S_M(D)}.
  \]
  The cut enters only through the dealer root, and the population through the Stieltjes transform $S_M$ rather than the pre-cut budget: two populations can share every pre-cut equilibrium object $(D, \kappa, a^*, \kappa^*, S^*)$ and differ after the cut.
  \item[(ii)] \emph{Direction.} The right side of~(i) is strictly decreasing in $D$. Where $\partial_D F > 0$, the root decreases in $\theta$, so on the principal equilibrium a cut lowers $S^*_\theta$; where $\partial_D F < 0$, a cut raises it.
  \item[(iii)] \emph{Prices-indistinguishable populations end close.} Let $M_A = g\,Q_A$ and $M_B = g\,Q_B$, where $g$ is positive and analytic near $r_c + \Delta\eta[-1, 1] \subset [0, \bar r]$, and $Q_A, Q_B$ are positive measures on that window with masses in $[W_{\min}, \bar W]$, $W_{\min} > 0$, whose difference annihilates every polynomial of degree at most $2K - 2$ (the hard pairs of Theorems~\ref{n:cost} and~\ref{n:thm_eqreduced}(iv) are of this form). If, for both, $\partial_D F \ge \nu > 0$ on an interval $[D_\theta - \delta_1, 1]$ with $D_\theta - \delta_1 \ge \max(D_{\min}, \bar r) + \mu$, where $\delta_1, \mu > 0$, then $|S^*_\theta(M_A) - S^*_\theta(M_B)| \le C (\Delta\eta)^{2K-1}$, where $C$ depends only on $(\nu, \delta_1, \mu, W_{\min}, \bar W, K, g)$ and the dealer primitives.
  \item[(iv)] \emph{One passive record learns it, at a rate free of the spacing.} Observe one stationary record $x_1, \dots, x_T$ of the pre-cut principal equilibrium's pricing error with Gaussian news, effective budget at most $1 - m$, primitive weight in $[W_{\min}, \bar W]$, and $\partial_D F \ge \nu$ on an interval $[D_\theta - \delta_1, 1]$ with $D_\theta - \delta_1 \ge \max(D_{\min}, \bar r) + \mu$. The record's first autoregressive coefficient is $\phi_0 = 1 + \bar a - D$. Let $\hat\phi$ be the least-squares coefficients of $x_t$ on $L = \lceil \log T / (2\log(1/\bar r)) \rceil$ own lags, $\hat D = 1 + \bar a - \hat\phi_0$, and, with $a^* = \bar a/\hat D$, $\kappa^* = \kappa_-(\hat D)/\hat D$ and $\hat\Psi(z) = \sum_{j < L} \hat\phi_j z^{-(j+1)}$,
  \[
    \hat S_M(z) = \frac{\hat\phi_0 - a^* + (\hat D - z)\{\hat\Psi(z) - a^*/z\}}{\kappa^*(\hat D - \bar a)}, \qquad z \in [\bar r + \mu, 1].
  \]
  Take the largest root of~\eqref{eq:Fcut} with $\hat S_M$ in place of $S_M$ and evaluate~(i). Then with probability at least $1 - 3\beta$,
  \[
    |\hat S^*_\theta - S^*_\theta| \le C\, (\log T)\, T^{-\gamma/2}, \qquad \gamma = \frac{\log\{(\bar r + \mu)/\bar r\}}{\log(1/\bar r)} \in (0, 1),
  \]
  with $C$ depending only on $(\beta, m, \mu, \nu, \delta_1, \bar r, W_{\min}, \bar W)$ and the dealer primitives, not on the number of groups or the spacing of their memories. The rate is not parametric in general: $S_M(z)$ at $z < 1$ has tap coefficients $z^{-(t+1)}$, which are not square-summable, so by Theorem~\ref{n:questions}(ii) it is not a cheap question even with direct tap measurements.
\end{enumerate}
\end{theorem}

Appendix~\ref{app:proofs} proves~(i) and~(ii); Supplement Section~\ref{S-sec:eqcut} proves~(iii) and~(iv). Part~(i) replaces the fixed-impact formula $a + \theta(S - a)$, which is wrong in equilibrium in size and, on a lower root, in sign. With the primitives of Supplement Theorem~\ref{S-thm:eqreduced}(iv) ($\bar a = 0.4$, $A = 0.188$, $\sigma_F^2 = 1$, $\sigma_\xi^2 = 0.25$, Gauss economy), a $50\%$ cut takes the effective budget from $0.650$ to $0.487$ on the principal equilibrium ($D = 0.862$, $\partial_D F = 0.29$), where the fixed-impact formula predicts $0.557$; on the lower root ($D = 0.80$, $\partial_D F = -0.41$) it raises the budget from $0.755$ to $0.913$. With the primitives of Supplement Section~\ref{S-sec:mixed_sign} ($\bar a = 0.6$, $A = 0.2$), one group at memory $0.7$ and two groups at $0$ and $0.93$ share every pre-cut equilibrium object ($D = 0.953$, $S^* = 0.687$) and end at $0.638$ and $0.629$ after a $50\%$ cut, a gap of $16\%$ of the pre-cut feedback part. Part~(iii) is why the separation survives: the compositions prices cannot tell apart have post-cut budgets within $(\Delta\eta)^{2K-1}$ of each other (fitted slopes $2.94$ for $K = 2$ and $4.98$ for $K = 3$ on the realization above). Part~(iv) is the cost: the post-cut budget needs the Stieltjes transform below one, which a record reveals at a polynomial rather than parametric rate. In a simulation of the principal equilibrium above ($40$ replications; replication archive), the error of the estimator in~(iv) for a $50\%$ cut falls with fitted slopes $-0.30$ to $-0.35$ in $\log T$ over $T \in [2{,}000, 32{,}000]$ at $\Delta\eta = 0.1$, $0.05$ and $0.025$, against $\gamma/2 \approx 0.32$ at $\Delta\eta = 0.1$ (with $\mu$ the margin of the pre-cut root above the largest memory), and does not grow as the spacing shrinks.

\textbf{Which ceiling.} In equilibrium the binding stability limit as feedback grows is the fold of Theorem~\ref{thm:fragility}, at which the principal equilibrium disappears while $S^* < 1$. A ceiling stated in terms of $S^*$ must therefore sit below $S^*(\lambda_{\mathrm{crit}})$. Both $\lambda_{\mathrm{crit}}$ and $S^*(\lambda_{\mathrm{crit}})$ depend on the population only through $S_M$ on $[\max(D_{\min}, \bar r), 1]$ and the dealer primitives, so the plug-in of part~(iv) estimates them as well; we do not state that rate."""

PILOT_OLD = r"""\begin{theorem}[A pilot learns what prediction cannot]\label{n:pilot}
Fix known $(a, \kappa)$, a memory bound $\bar r < 1$ and total merged weight at most $\bar W$. A restriction removes a set $R$ of groups---every group with memory below a cutoff $\hat r$, or a class---and leaves the other rules, impact and persistence unchanged."""

PILOT_NEW = r"""\begin{theorem}[A pilot learns what prediction cannot]\label{n:pilot}
Fix known $(a, \kappa)$, a memory bound $\bar r < 1$ and total merged weight at most $\bar W$. A restriction removes a set $R$ of groups---every group with memory below a cutoff $\hat r$, or a class whose accounts the supervisor can identify when it acts---and leaves the other rules unchanged; in parts~(i)--(iii) it also leaves impact and persistence unchanged."""

PILOT_III_OLD = r"""by $\hat w = \hat k_0$ and $\hat r = \hat k_1 / \hat k_0$ on each side.
\end{enumerate}
\end{theorem}"""

PILOT_III_NEW = r"""by $\hat w = \hat k_0$ and $\hat r = \hat k_1 / \hat k_0$ on each side.
  \item[(iv)] \emph{In the dealer equilibrium.} Let impact and persistence be the equilibrium objects of Theorem~\ref{n:thm_inventory}, with principal roots $D$ before and $D'$ during a pilot long enough to reach the post-restriction equilibrium. The pilot record is a record of that equilibrium, so it estimates the post-restriction effective budget directly, by the sum of its autoregressive coefficients at the rate of Theorem~\ref{n:passiveupper}(i), whatever the composition. The difference of effective taps $\tilde k_m - \tilde k'_m$ is no longer the removed groups' kernel, because the retained groups enter through $h_D - h_{D'}$ ($h_D(r) = (D - \bar a)/(D - r)$). The removed groups' effective moments are
  \[
    \int r^m h_D\, dM_R = \tilde k_m - \frac{D - \bar a}{D' - \bar a}\Bigl\{\tilde k'_m + (D' - D) \sum_{n \ge 0} \frac{\tilde k'_{m+n}}{D^{n+1}}\Bigr\},
  \]
  with $D$ and $D'$ read off each record's first autoregressive coefficient (Theorem~\ref{n:eqcut}(iv)). The correction's weights grow like $D^{-n}$, so the rate is that of Theorem~\ref{n:eqcut}(iv) rather than parametric, but it does not depend on the spacing.
\end{enumerate}
\end{theorem}"""

PILOT_DISC_OLD = r"""What a pilot cannot supply is the first decision: the restriction is imposed once without the information. In equilibrium a restriction also moves impact and persistence (Theorem~\ref{n:thm_inventory}), and the statement takes them as known in both regimes."""

PILOT_DISC_NEW = r"""What a pilot cannot supply is the first decision: the restriction is imposed once without the information. Part~(iv) shows what survives when the restriction moves impact and persistence: the decision-relevant post-restriction budget is read from the pilot record alone, and the removed groups' composition after a correction that the two dealer roots fix. The analogy with the Tick Size Pilot is loose, since that pilot varied a market rule across stocks rather than removing trader classes within a market."""

PILOT_TICK_OLD = r"""so phased or temporary restrictions are informative in a way that forecasts are not; randomized market-structure pilots such as the SEC's 2016--2018 Tick Size Pilot are the institutional form, and Supplement Proposition~\ref{S-prop:natural_exp} gives the cross-sectional design for a class ban."""

PILOT_TICK_NEW = r"""so phased or temporary restrictions are informative in a way that forecasts are not; randomized market-structure pilots such as the SEC's 2016--2018 Tick Size Pilot are the nearest institutional form, and Supplement Proposition~\ref{S-prop:natural_exp} gives the cross-sectional design for a class ban."""

LEMMA_OLD = r"""Before solving the strategic relabeling and surveillance-crowding games, the next lemma anchors their reduced-form payoffs directly in the inventory equilibrium of Section~\ref{sec:equilibrium} and the steady-state Kalman trading desk of Section~\ref{sec:model}.

\begin{lemma}[Equilibrium microfoundation of disclosure and crowding payoffs]\label{lem:micro}"""

LEMMA_NEW = r"""Before solving the strategic relabeling and surveillance-crowding games, the next lemma relates their reduced-form payoffs to the inventory equilibrium of Section~\ref{sec:equilibrium} and to the steady-state Kalman trading desk of Section~\ref{sec:model}. Its welfare weight $\lambda_{\mathrm{ext}}$ is a parameter of the supervisor's criterion, not an equilibrium object, so the lemma motivates the payoffs rather than deriving them.

\begin{lemma}[Payoff foundations for disclosure and crowding]\label{lem:micro}"""

PARADOX_OLD = r"""Suppose the Kullback--Leibler divergence from the economy at distance $\delta$ to the closest null economy satisfies $J = c N \delta^n$ on $[0, \delta_0]$ with $c > 0$ and $n > 2$, and the test has continuous power $P_{\mathrm{d}}(J) \ge \alpha$ with $P_{\mathrm{d}}(0) = \alpha$."""

PARADOX_NEW = r"""Suppose the Kullback--Leibler divergence from the economy at distance $\delta$ to the closest null economy satisfies $J = c N \delta^n$ on $[0, \delta_0]$ with $c > 0$ and $n > 2$, and the test's power depends on the alternative only through $J$, through a continuous function $P_{\mathrm{d}}(J) \ge \alpha$ with $P_{\mathrm{d}}(0) = \alpha$. Every level-$\alpha$ test satisfies the Pinsker envelope $P_{\mathrm{d}}(J) - \alpha \le \sqrt{J/2}$, which part~(i) uses."""

RECORDVALUE_OLD = r"""and for general $n > 2$, $V_P(N) \le V^* \{c N B_N^{n/(n-2)}/2\}^{1/2}$ with $B_N = 4k^2\delta_0^2/(L^2\beta^2 cN)$, which is of order $N^{-1/(n-2)}$."""

RECORDVALUE_NEW = r"""and for general $n > 2$, $V_P(N) \le V^* \{c N B_N^{n/(n-2)}/2\}^{1/2}$ with $B_N = 4k^2\delta_0^2/(L^2\beta^2 cN)$, which is of order $N^{-1/(n-2)}$. If the test is instead two-sided, with $P_{\mathrm{d}}(J) - \alpha \ge \beta_2 \min\{J, \bar J\}$ and $L\beta_2 \bar J > k\delta_0^2$, then $(\delta^*)^{n-1} \le 2k\delta_0/(L\beta_2 cN)$ and
  \[
    V_P(N) \le \frac{V^*}{\sqrt 2}\Bigl(\frac{2k\delta_0}{L\beta_2}\Bigr)^{n/(2(n-1))} (cN)^{-1/(2(n-1))},
  \]
  of order $N^{-1/6}$ at $n = 4$."""

RECORDVALUE_DISC_OLD = r"""Because the group crowds as the record grows, the value of price surveillance falls like $N^{-1/2}$, so a longer price record never substitutes for an owner-linked one, and the record length beyond which a trail of cost $F_A$ pays is explicit."""

RECORDVALUE_DISC_NEW = r"""Because the group crowds as the record grows, the value of price surveillance is at most of order $N^{-1/2}$ against a one-sided test and $N^{-1/6}$ against a two-sided one, so a longer price record does not substitute for an owner-linked one, and the record length beyond which a trail of cost $F_A$ pays is explicit. The statement is about the group's best response to a fixed test, not an equilibrium with an optimizing supervisor (for that, see Supplement Proposition~\ref{S-prop:endogenous_supervisor})."""

RECORDVALUE_FIT_OLD = r"""the bound in~(ii) holds at every $N$ from $10$ to $10^8$, and the exact total variation falls with fitted slope $-0.48$ in $\log N$."""

RECORDVALUE_FIT_NEW = r"""the bound in~(ii) holds at every $N$ from $10$ to $10^8$, and the exact total variation falls with fitted slope $-0.48$ in $\log N$ for $N \ge 10^4$ ($-0.37$ over the whole range, before the asymptotic regime sets in)."""

CONCL_OLD = r"""Three policy conclusions follow. First, a market-wide cut is the safe default. Without tags it is minimax over labelings, and given persistence, impact and a memory bound its effect can be calibrated from the aggregate response, or from one passive price record, at a cost that does not depend on how close the traders' memories are (Theorems~\ref{n:separation} and~\ref{n:passiveupper})."""

CONCL_NEW = r"""Three policy conclusions follow. First, a market-wide cut is the natural default when targeting cannot be verified. Without tags it is minimax over labelings. With persistence, impact and a memory bound given, its effect is learned from one passive pricing-error record at a cost that does not depend on how close the traders' memories are (Theorems~\ref{n:separation} and~\ref{n:passiveupper}). In the dealer equilibrium, on the principal branch, a cut still lowers the budget and its effect is learned without the spacing penalty, though more slowly (Theorem~\ref{n:eqcut}); on a lower branch a uniform cut raises the budget, so the default needs the market to sit on the principal equilibrium."""

CONCL_LIMITS_OLD = r"""The Taiwan calibration holds persistence and impact fixed and relies on asymptotic rate proxies, so pure causal feedback and cross-stock independence remain open, and discrete time abstracts from continuous-book cancellations and sub-millisecond races"""

CONCL_LIMITS_NEW = r"""The Taiwan illustration holds persistence and impact fixed, its persistence is largely produced by detrending, and it relies on asymptotic rate proxies, so pure causal feedback and cross-stock independence remain open, and discrete time abstracts from continuous-book cancellations and sub-millisecond races"""

APPX_SEP_OLD = r"""\begin{proof}[Proof of Theorem~\ref{n:separation}]
\emph{(i)} The first claim is Proposition~\ref{n:target}(i). For the rate, write $S = a + \kappa \sum_{m \ge 0} k_m$ and estimate $\sum_{m < L} k_m$ by the sum of the $L$ tap averages. Because $|k_m| \le \bar W \bar r^m$, the omitted tail is at most $\bar W \bar r^L / (1 - \bar r)$, which is below $\epsilon / (2\kappa)$ once $L \ge \log(2\kappa \bar W / (\epsilon(1 - \bar r))) / \log(1/\bar r)$. The sum of $L$ independent tap averages has Gaussian error with variance $L \sigma^2 / N$, so it is within $\epsilon / (2\kappa)$ with probability at least $1 - \beta$ once $N \ge 8 \kappa^2 \sigma^2 L \log(2/\beta) / \epsilon^2$. Neither bound involves $K$ or the memory spacing. The passive version is Theorem~\ref{n:passiveupper}(i). Minimax optimality is Theorem~\ref{n:minimax}(i). \emph{(ii)} Proposition~\ref{n:target}(ii) for the largest group (memories in $r_c + \Delta\eta[-1, 1]$) and Proposition~\ref{n:target}(iii) for the cutoff (memories in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$). \emph{(iii)} Theorem~\ref{n:disc}.
\end{proof}"""

APPX_SEP_NEW = r"""\begin{proof}[Proof of Theorem~\ref{n:separation}]
\emph{(i)} The first claim is Proposition~\ref{n:target}(i); the rate is Theorem~\ref{n:passiveupper}(i); minimax optimality is Theorem~\ref{n:minimax}(i). \emph{(ii)} Proposition~\ref{n:target}(ii) for the largest group (memories in $r_c + \Delta\eta[-1, 1]$) and Proposition~\ref{n:target}(iii) for the cutoff (memories in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$). Both pairs have merged measures matching moments $0, \dots, 2K-2$ on a window of length $3\Delta\eta$, so $\|\Delta k\|_1 = O((\Delta\eta)^{2K-1})$, and the finite-record bound in the proof of Theorem~\ref{n:cost} gives $\KL \le C T (\Delta\eta)^{4K-2}$ for $T$ passive observations under uniform stability; both errors at most $1/4$ force $\KL \ge 1/2$ by Pinsker's inequality. The matching upper bound is Theorem~\ref{n:passiveupper}(ii).

\emph{(iii)} Write $\Phi(z) = a z + \kappa z \sum_{m \ge 0} k_m z^m = a z + \kappa \sum_i w_i z/(1 - r_i z)$, which has nonnegative coefficients and $\Phi(1) = S \le 1 - m$. The reset response is $h = \kappa B$ with $B(z) = \{1 - \Phi(z)\}^{-1}$, so $h_0 = \kappa$ and $H = \sum_t h_t = \kappa/(1 - S) \in [\kappa, \kappa/m]$, and $S = 1 - \kappa/H$. Let $z_1 = (1 + \bar r^{-1})/2$. On $[1, z_1]$, $1 - r_i z \ge (1 - \bar r)/2$, so $\Phi' \le \Lambda \equiv a + 4\kappa\bar W/(1 - \bar r)^2$ and, with $\rho_0 = 1 + \min\{m/(2\Lambda), z_1 - 1\}$, $\Phi(\rho_0) \le 1 - m/2$. For $|z| \le \rho_0$ nonnegative coefficients give $|\Phi(z)| \le \Phi(|z|) \le 1 - m/2$, so $|B(z)| \le 2/m$, and Cauchy's estimate gives $0 \le h_t \le (2\kappa/m)\rho_0^{-t}$. The tail beyond depth $L$ is therefore at most $(2\kappa/m)\rho_0^{-L}/(1 - \rho_0^{-1})$, below $\kappa\epsilon/8$ for $L = O(\log(1/\epsilon))$. The average of $N$ reset records has, at each date, Gaussian error of variance $\sigma^2/N$, so $\hat H_L = \sum_{t < L} \bar h_t$ has error at most $\kappa\epsilon/8$ with probability at least $1 - \beta$ once $N \ge 128 L \sigma^2 \log(2/\beta)/(\kappa^2 \epsilon^2)$. On that event $|\hat H_L - H| \le \kappa\epsilon/4 \le \kappa/2$, so $\hat H_L \ge \kappa/2$ and $|\hat S - S| = \kappa|\hat H_L^{-1} - H^{-1}| \le 2|\hat H_L - H|/\kappa \le \epsilon$ for $\hat S = 1 - \kappa/\hat H_L$. No bound involves $K$ or the memory spacing. The targeted lower bounds are Proposition~\ref{n:target}(ii)--(iii). \emph{(iv)} Theorem~\ref{n:disc}.
\end{proof}

\begin{proof}[Proof of Theorem~\ref{n:eqcut}(i)--(ii)]
\emph{(i)} At a root $D$ of~\eqref{eq:Fcut}, Theorem~\ref{n:thm_inventory}(i) gives $\kappa = \kappa_-(D)$ with $1 - D = \kappa\theta S_M(D)$, and Theorem~\ref{n:thm_eqreduced}(i) gives the reduced form $a^* = \bar a/D$, $\kappa^* = \kappa/D$ and $\tilde w_i = \theta w_i (D - \bar a)/(D - r_i)$. Its budget~\eqref{eq:budget} is $S^* = a^* + \kappa^* \sum_i \tilde w_i/(1 - r_i)$. By partial fractions, $\{(D - r)(1 - r)\}^{-1} = \{(D - r)^{-1} - (1 - r)^{-1}\}/(1 - D)$, so
\[
  \kappa\theta \sum_i \frac{w_i}{(D - r_i)(1 - r_i)} = \frac{\kappa\theta\{S_M(D) - S_M(1)\}}{1 - D} = 1 - \frac{S_M(1)}{S_M(D)},
\]
and $S^* = \bar a/D + (1 - \bar a/D)\{1 - S_M(1)/S_M(D)\}$, the displayed formula; $\theta$ cancels. The example in the text, computed from~\eqref{eq:Fcut} (replication archive), shows that $S^*_\theta$ is not a function of the pre-cut equilibrium objects. \emph{(ii)} On $(\bar r, 1]$, $S_M$ is positive and strictly decreasing, so $\psi(D) = S_M(1)/S_M(D) \in (0, 1]$ is strictly increasing, and $1 - \bar a/D$ is positive (as $D > D_{\min} > \bar a$) and nondecreasing; their product strictly increases, so $S^*$ strictly decreases in $D$. Where $\partial_D F \ne 0$, the implicit function theorem gives $dD_\theta/d\theta = -\kappa_-(D)S_M(D)/\partial_D F$, of the sign opposite to $\partial_D F$ because $\kappa_-(D)S_M(D) > 0$. Hence $dS^*_\theta/d\theta$ has the sign of $\partial_D F$: a cut lowers $S^*_\theta$ where $\partial_D F > 0$ and raises it where $\partial_D F < 0$.
\end{proof}"""

APPX_PILOT_OLD = r"""With one atom $w\delta_r$ on a side, $k_0 = w$ and $k_1 = w r$; if the tap errors satisfy $|e_0| \le w/2$, then $|\hat w - w| = |e_0|$ and $|\hat r - r| \le 2(|e_1| + r|e_0|)/w$ (machine-checked), which is $O(\sigma/(w_{\min}\sqrt N))$ and does not involve $\Delta\eta$.
\end{proof}"""

APPX_PILOT_NEW = r"""With one atom $w\delta_r$ on a side, $k_0 = w$ and $k_1 = w r$; if the tap errors satisfy $|e_0| \le w/2$, then $|\hat w - w| = |e_0|$ and $|\hat r - r| \le 2(|e_1| + r|e_0|)/w$ (machine-checked), which is $O(\sigma/(w_{\min}\sqrt N))$ and does not involve $\Delta\eta$. \emph{(iv)} The pilot equilibrium is a stationary equilibrium of Theorem~\ref{n:thm_inventory} with population $M_{\bar R}$; its record is the reduced form of Theorem~\ref{n:thm_eqreduced}(i), whose budget is the sum of its autoregressive coefficients, so the argument of Theorem~\ref{n:passiveupper}(i) applies with $a = 0$ and those coefficients. Before the restriction the effective taps are $\tilde k_m = \int r^m h_D\, d(M_R + M_{\bar R})$; during the pilot, $\tilde k'_m = \int r^m h_{D'}\, dM_{\bar R}$. Since $h_D/h_{D'} = \{(D - \bar a)/(D' - \bar a)\}(D' - r)/(D - r)$ and $(D' - r)/(D - r) = 1 + (D' - D)\sum_{n \ge 0} r^n D^{-(n+1)}$ for $r \le \bar r < D$, $\int r^m h_D\, dM_{\bar R} = \int r^m (h_D/h_{D'})\, d(h_{D'} M_{\bar R})$ is the displayed correction, and subtracting it from $\tilde k_m$ gives the removed groups' effective moments. The rate follows as in the proof of Theorem~\ref{n:eqcut}(iv) (Supplement Section~\ref{S-sec:eqcut}).
\end{proof}"""


# ------------------------------------------------------------- Taiwan section (Section 7.5) --------------------

def _f(x, d=4):
    return f'{x:.{d}f}'


def taiwan_holdout_paragraph():
    p = HOLDOUT['primary_file']['primary']
    g = HOLDOUT['diagnostics']
    rc = g['reverse_causality']
    return (
        r"Second, the registered 2019--2023 out-of-sample holdout (spec P1T; Supplement Section~\ref{S-sec:p1t}) asks whether the price deviation improves out-of-sample forecasts of a class's own tagged flow beyond the flow's two lags; $\hat D_{\mathrm{OOS}}$ is the mean across stocks of the proportional MSE reduction. "
        r"In the words fixed before the holdout was opened: ``$D = " + _f(p['D']) + r"$ $[" + _f(p['ci95'][0]) + r", " + _f(p['ci95'][1]) + r"]$, $p = 0.000$, meets the registered supportive criterion. The pre-specified reverse-causality check gives $D = " + _f(rc['D']) + r"$ $[" + _f(rc['ci95'][0]) + r", " + _f(rc['ci95'][1]) + r"]$, which does not meet it. The registered verdict is `supportive'. Read with its pre-specified diagnostic, the test does not provide evidence of feedback beyond prices revealing past flow.'' "
        r"The reported $p = 0.000$ is rounded: no centred bootstrap resample out of $9{,}999$ reached $D$, so $p < 10^{-4}$. The check replaces $x_t$ by its residual from a fit-period regression on $x_{t-1}$ and lagged reported flows. "
        r"Supplement Table~\ref{S-tab:p1t_all} reports every registered outcome. Among them, the price deviation worsens out-of-sample forecasts of investment-trust flow ($D = " + _f(g['S1']['by_class']['Trust']['D']) + r"$, $[" + _f(g['S1']['by_class']['Trust']['ci95'][0]) + r", " + _f(g['S1']['by_class']['Trust']['ci95'][1]) + r"]$) and does not improve those of dealers' own flow ($D = " + _f(g['S1']['by_class']['DealerOwn']['D']) + r"$), so the trust response in Table~\ref{tab:taiwan} has no out-of-sample support; and the per-stock tagged instrumental-variable estimates of the foreign flow memory lie outside $(-1, 1)$ for " + str(g['S3']['n_excluded_abs_r_ge_1']) + r" of " + str(g['S2']['Foreign']['eval']['n_stocks']) + r" stocks (median $" + _f(g['S2']['Foreign']['fit']['r_median'], 2) + r"$ in the fit period), so they do not measure memory stock by stock. "
        r"Two later analyses were not registered: masking price-limit and post-halt days gives $0.0410$ $[0.0197, 0.0623]$ with reverse-causality check $-0.0083$ $[-0.0332, 0.0150]$, and splitting at the 23~March~2020 switch to continuous matching, which coincided with the COVID-19 sell-off, gives $0.0319$ before and $0.0421$ after. "
        r"In the words fixed before the holdout was opened: ``We do not claim that tagged flow in Taiwan responds to price deviations. The registered test is supportive, but its pre-specified diagnostic attributes the gain to reverse causality.''"
    )


TAIWAN_HOLDOUT_OLD_START = r"Second, in the registered 2019--2023 out-of-sample holdout (Figure~\ref{fig:twse_sensitivity}; Supplement Sections~\ref{S-sec:scope} and~\ref{S-app:barrier}),"
TAIWAN_HOLDOUT_OLD_END = r"We do not claim that tagged flow in Taiwan responds causally to price deviations."

TAIWAN_INTRO_OLD = r"""\footnote{Trailing-mean detrending induces AR(1) persistence near $0.975$; Figure~\ref{fig:twse_sensitivity}B and Supplement Table~\ref{S-tab:p1m_sensitivity} confirm that first-differencing $\Delta x_t$ and excluding price-limit days leave the class persistence estimates intact.}"""

TAIWAN_INTRO_NEW = r"""\footnote{Trailing 60-day demeaning of a random walk alone produces first-order persistence $118/121 = 0.975$, and the estimated $\sum_j \hat a_j = 0.972$ is close to that value, so the price persistence in Table~\ref{tab:taiwan} is largely a property of the filter, not evidence about how pricing errors decay. First-differencing $\Delta x_t$ and excluding price-limit days leave the class flow persistences $\hat r_c$ nearly unchanged (Figure~\ref{fig:twse_sensitivity}B; Supplement Table~\ref{S-tab:p1m_sensitivity}), but not the responses: under first differencing $\hat w_F = -1.82$ and $\hat w_D = -0.55$, so the sign of foreign feedback depends on the specification.}"""

TAIWAN_TABLE_CAPTION_OLD = r"""\caption{Estimated tagged trading rules in Taiwan, 2013--2016 (300 stocks, 270,060 stock-days; stock fixed effects with 95\% date-block bootstrap intervals).}"""

TAIWAN_TABLE_CAPTION_NEW = r"""\caption{Estimated tagged trading rules in Taiwan, 2013--2016 (300 stocks, 270,060 stock-days; stock fixed effects with 95\% date-block bootstrap intervals, mean block 20). The rules assume that each class's feedback decays at its own flow persistence and a common impact $\kappa$ for all classes.}"""

TAIWAN_PERSIST_ROW_OLD = r"""\multicolumn{4}{@{}l}{\footnotesize Lagged-flow price impact $\kappa = 0.0038 \; [0.0032, 0.0044]$; aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\"""

TAIWAN_PERSIST_ROW_NEW = r"""\multicolumn{4}{@{}p{0.97\linewidth}}{\footnotesize Lagged-flow price impact $\kappa = 0.0038 \; [0.0032, 0.0044]$; aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$, about what the detrending filter alone implies.} \\"""

FIG3_CAPTION_OLD = r"""Rows marked ``registered'' are the registered holdout (pooled $0.0426$, annual subsamples, reverse-causality placebo $-0.0065$); rows marked ``post hoc'' were run after the holdout was opened (limit and post-halt days masked, $0.0410$; split at the 23~March~2020 switch to continuous matching, $0.0319 \to 0.0421$)."""

FIG3_CAPTION_NEW = r"""Rows marked ``registered'' are the registered holdout (pooled $0.0426$, annual subsamples, pre-specified reverse-causality check $-0.0065$); rows marked ``post hoc'' were run after the holdout was opened and are not registered (limit and post-halt days masked, $0.0410$; split at the 23~March~2020 switch to continuous matching, which coincided with the COVID-19 sell-off, $0.0319$ and $0.0421$)."""

TAIWAN_GRANT_OLD = r"""Granting a price-only supervisor full knowledge of the impact function $\kappa$ and the law of non-feedback order flow (so only class composition is unknown) yields three quantitative contrasts (Supplement Section~\ref{S-app:barrier}). Price and tagged records are compared against separately optimized single-memory candidates with non-feedback flow held at its estimated law."""

TAIWAN_GRANT_NEW = r"""Granting a price-only supervisor full knowledge of the impact function $\kappa$ and the law of non-feedback order flow (so only class composition is unknown) yields three quantitative contrasts (Supplement Section~\ref{S-app:barrier}, which specifies the search). Price and tagged records are compared against separately optimized single-memory candidates with non-feedback flow held at its estimated law; the ranges below are endpoints of local searches, not certified extrema."""

TAIWAN_ITEMS_OLD = r"""  \item \emph{Information gap.} Against their respective fitted single-memory alternatives, one stock-day of prices has an estimated divergence of $1.7 \times 10^{-12}$~nats about class composition, whereas one stock-day of tagged flows carries $8.0 \times 10^{-7}$~nats---a factor of $4.7 \times 10^5$ more information. Substituting the asymptotic KL rate per stock-day yields a horizon benchmark of $2.7 \times 10^9$ years for one stock at $80\%$ power and $5\%$ size, or $9.1 \times 10^6$ years across 300 independent stocks.
  \item \emph{Targeted halt is unidentified from prices.} With tags, halting foreign feedback lowers the feedback budget by $0.0014$ ($95\%$ CI $[0.0012, 0.0016]$). Among candidates found using the panel-length spectral-rate proxy and the $0.10$ power-gap calibration, the effect of halting one class spans $[-0.028, 0.028]$ (and $[-0.0027, 0.0027]$ even if each class is capped at twice the largest estimated contribution). Even with an infinite price record, permutation relabeling alone leaves $0.0014$, $4.2 \times 10^{-4}$, and $-1.3 \times 10^{-4}$ observationally equivalent.
  \item \emph{Uniform feedback reduction.} Across all price-consistent candidates found by the spectral search, setting total feedback to zero lowers the budget within $[0.0014, 0.0019]$.
\end{enumerate}"""

TAIWAN_ITEMS_NEW = r"""  \item \emph{Information.} Against their respective fitted single-memory alternatives, one stock-day of prices carries an estimated $1.7 \times 10^{-12}$~nats about class composition and one stock-day of tagged flows $8.0 \times 10^{-7}$~nats. Both are small in absolute terms. The whole 2013--2016 tagged panel carries $270{,}060 \times 8.0 \times 10^{-7} = 0.22$~nats, so by Pinsker's inequality any tagged-flow test of memory composition has power minus size at most $0.33$; for prices the bound is $4.8 \times 10^{-4}$. Power minus size $0.75$ ($80\%$ power at $5\%$ size) needs $1.125$~nats by the same inequality: $2.7 \times 10^9$ years of prices for one stock ($9.1 \times 10^6$ years for 300 independent stocks) at the panel's $245.5$ trading days a year, against $5{,}700$ years of tags for one stock ($19$ years for 300 stocks). Table~\ref{tab:years} uses a different conversion (the Bretagnolle--Huber bound $\ln 5/D$ at $252$ days), so the two sets of years are not comparable. In Taiwan, then, the tags identify class contributions only under the maintained restriction that feedback memory equals flow persistence; they do not identify the feedback memories themselves.
  \item \emph{Targeted halt.} With tags, halting foreign feedback lowers the feedback budget by $0.0014$ ($95\%$ CI $[0.0012, 0.0016]$). On the class the lower bounds cover (every weight nonnegative, memories in $[0, 0.99]$), the compositions the panel cannot tell apart imply contributions of foreign feedback from $0$ to $0.0018$, against a uniform cut between $0.0016$ and $0.0018$ on the same class, so prices leave foreign feedback anywhere between none and all of the total. For one stock the ranges are $[0, 0.0035]$ and $[1.3 \times 10^{-4}, 0.0046]$ and overlap. Holding each class's weight to the sign of its tagged estimate, so that the contrarian dealers can offset the others at nearby memories, gives $[0, 0.028]$, which fills the cap on each class's contribution; allowing weights of either sign gives $[-0.028, 0.028]$, attained only at negative memory rates, outside the model's $r \in (0, 1)$. Permutation relabeling alone leaves $0.0014$, $4.2 \times 10^{-4}$ and $-1.3 \times 10^{-4}$ observationally equivalent at every record length.
  \item \emph{Uniform feedback reduction.} On the nonnegative class, setting total feedback to zero lowers the budget by $0.0016$ to $0.0018$ across the price-consistent candidates.
\end{enumerate}"""

TAIWAN_QUAL_OLD_START = r"""Four qualifications apply. First, the range $[-0.028, 0.028]$ in item~2 fills the cap by construction:"""
TAIWAN_QUAL_OLD_END = r"""and dealers' negative $w_D$ lies outside the positive class (though Whittle rates, Pinsker's inequality, and relabeling invariance still apply)."""

TAIWAN_QUAL_NEW = r"""Four qualifications apply. First, the tagged intervals in Table~\ref{tab:taiwan} assume a common impact and that each class's feedback decays at its own flow persistence. With the class-specific impacts the price equation estimates as a diagnostic ($0.0035$, $0.012$ and $-0.0004$; Supplement Section~\ref{S-app:barrier}), the point contributions become $0.0013$ (foreign), $0.0013$ (trusts) and $1.4 \times 10^{-5}$ (dealers), so which class is largest depends on that restriction; we have not tested equal impacts. With feedback decoupled from each class's flow persistence (a free ten-day distributed lag of $x$, with second-order autoregressive non-feedback flow), foreign feedback contributes $0.0013$ ($95\%$ interval $[0.0011, 0.0015]$). Second, item~3 rests on the grant: the price-only supervisor is given the persistences $a_j$, the impact $\kappa$ and the non-feedback law, all estimated with the tagged flows; with feedback contributing $0.0017$ to a budget of $0.97$, separating the two from prices alone is the problem that Proposition~\ref{n:target} assumes away. Third, we have not recomputed the information measures and ranges under the first-differenced and limit-excluded specifications, where the responses change sign (footnote~\ref{fn:persist}). Fourth, the calendar-year conversions assume cross-stock independence (whereas the common-date bootstrap accommodates cross-stock dependence), and dealers' negative $w_D$ lies outside the positive class (though Whittle rates, Pinsker's inequality, and relabeling invariance still apply)."""


# ------------------------------------------------------------------------- Declarations ------------------------

TWSE_AUCTION_OLD = r"""Market structure shapes these daily series: TWSE shortened its 5-second periodic call auction ($20\text{s}\to 5\text{s}$, 2013--2016), expanded day trading in 2014,"""

TWSE_AUCTION_NEW = r"""Market structure shapes these daily series: TWSE had reduced its periodic call-auction interval in four steps from 25 to 5 seconds between 2010 and 2014 (Twu and Wang, 2018), expanded day trading in 2014,"""

CAT_OLD = r"""In practice, natural-person reporting exemptions and litigation over Consolidated Audit Trail funding highlight both the governance costs $F_A$ and the institutional boundaries of owner-level linkage (Securities and Exchange Commission, 2025; Eleventh Circuit July 2025 decision in \emph{ASA v.\ SEC}; Supplement Section~\ref{S-app:relabel}),"""

CAT_NEW = r"""In practice, the Consolidated Audit Trail shows both the governance costs $F_A$ and what owner-level linkage needs. In 2025 the SEC exempted the reporting of names, addresses and years of birth of U.S.\ natural persons, and CAT LLC proposed removing all personally identifying information; regulators would still be able to tell whether trading in several accounts belongs to the same customer, which is the linkage the model needs, without knowing who the customer is (Securities and Exchange Commission, 2025; FINRA, 2025). The SEC's 2023 funding order was vacated in \emph{American Securities Association v.\ SEC}, No.~23-13396 (11th Cir.\ July 25, 2025) (Supplement Section~\ref{S-app:relabel}),"""

DECL_AUTHORS_OLD = r"""\textbf{Author contributions.} Pratik Niroula: conceptualization, methodology, formal analysis, software, investigation, data curation, writing (original draft). Prashant Niroula: validation (proofs, Lean~4 formalizations, and empirical calculations), writing (review and editing). Sujan Khatiwada: validation (proofs, Lean~4 formalizations, and empirical calculations), writing (review and editing). All authors approved the final manuscript."""

DECL_AUTHORS_NEW = r"""\textbf{Author contributions (CRediT).} Pratik Niroula: conceptualization, methodology, formal analysis, software (numerical scripts, empirical executors and Lean~4 files, written with the AI assistance described below), investigation, data curation, writing (original draft). Prashant Niroula: validation (proofs, Lean~4 formalizations, and empirical calculations), writing (review and editing). Sujan Khatiwada: validation (proofs, Lean~4 formalizations, and empirical calculations), writing (review and editing). All authors approved the final manuscript."""

DECL_RELATED_OLD = r"""\textbf{Related manuscripts.} An earlier working paper of the same authors (Niroula et al., 2026a, dated 5 November 2026) studied the same model; this article supersedes it. The earlier paper, the companion note (Niroula et al., 2026c) and the full working paper (Niroula et al., 2026d) are in the repository cited below.\par\medskip"""

DECL_RELATED_NEW = r"""\textbf{Related manuscripts.} An earlier working paper of the same authors (Niroula et al., 2026a, dated 5 November 2026) studied the same model; this article supersedes it. Niroula et al.\ (2026b), with a different author list (P.~Niroula, S.~Alkhushayni, Y.~Chen, M.~Bhavsar and P.~Niroula), studies transient amplification and pre-trade guards; it is cited once, for a fact no result here uses. The companion note (Niroula et al., 2026c) and the full working paper (Niroula et al., 2026d) collect results this article does not use. All four are unpublished working papers in the repository cited below, and none is under consideration at a journal or conference.\par\medskip"""

DECL_DATA_OLD = r"""\textbf{Data and code availability.} All empirical data are publicly available from the Taiwan Stock Exchange (\url{https://www.twse.com.tw}). Empirical protocols, replication scripts, numerical checks, and Lean~4 formalization files are archived at \url{https://github.com/Pratikn03/Fianince}."""

DECL_DATA_NEW = r"""\textbf{Data and code availability.} The empirical data are public. Taiwan Stock Exchange daily reports T86, MI\_INDEX, FMTQIK and TWT49U (\url{https://www.twse.com.tw}) were downloaded on 7--8 November 2026; the download manifest with the SHA-256 of every response is in the replication archive (Supplement Section~\ref{S-sec:p1t}). Supplement Section~\ref{S-sec:scope} also cites tests on Binance public futures data (\url{https://data.binance.vision}) and CFTC Commitments of Traders reports (\url{https://www.cftc.gov}); their specifications and results files are in the archive. Empirical protocols, executors, results files, numerical checks and Lean~4 files are at \url{https://github.com/Pratikn03/Fianince}."""


def decl_ai_new():
    checked = (r"After using these tools, the authors reviewed, verified and edited all mathematical proofs, calculations and prose, including the revision of 28 November 2026, and take full responsibility for the content of the publication."
               if AUTHORS_CHECKED_1128 else
               r"After using these tools, the authors reviewed, verified and edited all mathematical proofs, calculations and prose through 27 November 2026 and take full responsibility for the content of the publication. The revision of 28 November 2026, which responds to AI-generated referee reports, is being checked by the authors; until they finish, its new statements have been checked numerically (replication archive) but not yet by the authors.")
    return (r"\textbf{Declaration of generative AI and AI-assisted technologies in the research and writing process.} The authors used Claude (Anthropic; Claude Opus 5.5 and Claude Fable 5.2, the versions recorded in the repository's commit history), ChatGPT/Codex (OpenAI) and Gemini (Google; versions not recorded). In the research process these tools wrote, at the authors' direction, the numerical verification scripts, the empirical executors and notebooks, and the Lean~4 files, and checked literature (Supplement Section~\ref{S-app:verification}); the authors ran every empirical notebook, and each registered test was run once by the first author. In writing, they were used for drafting and language editing. " + checked +
            r" Lean~4 checks certify the formal statements listed in Supplement Table~\ref{S-tab:claims}, not their correspondence with the prose, empirical validity, or novelty.")


DECL_AI_OLD_START = r"""\textbf{Declaration of generative AI and AI-assisted technologies.}"""
DECL_AI_OLD_END = r"""not probabilistic steps, empirical validity, or novelty."""


# ------------------------------------------------------------------------- References --------------------------

NEW_REFS = [
    r"Chan, N.H., Wei, C.Z., 1988. Limiting distributions of least squares estimates of unstable autoregressive processes. \emph{Annals of Statistics} 16(1), 367--401.",
    r"Leipus, R., Oppenheim, G., Philippe, A., Viano, M.-C., 2006. Orthogonal series density estimation in a disaggregation scheme. \emph{Journal of Statistical Planning and Inference} 136(8), 2547--2571.",
    r"Oymak, S., Ozay, N., 2019. Non-asymptotic identification of LTI systems from a single trajectory. In: \emph{Proceedings of the 2019 American Control Conference}, pp.\ 5655--5661.",
    r"Sarkar, T., Rakhlin, A., Dahleh, M.A., 2021. Finite time LTI system identification. \emph{Journal of Machine Learning Research} 22(26), 1--61.",
    r"Simchowitz, M., Mania, H., Tu, S., Jordan, M.I., Recht, B., 2018. Learning without mixing: Towards a sharp analysis of linear system identification. In: \emph{Proceedings of the 31st Conference on Learning Theory}, PMLR 75, 439--473.",
    r"Twu, M., Wang, J., 2018. Call auction frequency and market quality: Evidence from the Taiwan Stock Exchange. \emph{Journal of Asian Economics} 57, 53--62.",
    r"FINRA, 2025. Eliminating all PII from CAT. Blog post, 19 March 2025. \url{https://www.finra.org/media-center/blog/eliminating-all-pii-from-cat}.",
    r"Sims, C.A., Stock, J.H., Watson, M.W., 1990. Inference in linear time series models with some unit roots. \emph{Econometrica} 58(1), 113--144.",
]


def _key(item):
    import re
    s = re.sub(r'\\[a-zA-Z]+\s*', '', item)
    s = s.replace('\\"', '').replace("\\'", '').replace('{', '').replace('}', '').replace('\\', '')
    return s.lower()


def add_references(t):
    import re
    a = t.index(r"\begin{list}{}")
    a = t.index('\n', a) + 1
    b = t.index(r"\end{list}", a)
    body = t[a:b]
    items = [s.strip() for s in re.split(r'\n\s*\\item ', '\n' + body) if s.strip()]
    have = {_key(i)[:40] for i in items}
    items += [r for r in NEW_REFS if _key(r)[:40] not in have]
    items.sort(key=_key)
    return t[:a] + '\n' + '\n\n'.join(r'\item ' + s for s in items) + '\n\n' + t[b:]


def _span(t, start, end):
    a = t.index(start)
    b = t.index(end, a) + len(end)
    assert t.count(start) == 1, start[:80]
    return a, b


def main_text(t):
    for old, new in [
        (ABSTRACT_OLD, ABSTRACT_NEW), (FRONT_OLD, FRONT_NEW), (EXAMPLE_OLD, EXAMPLE_NEW), (MODEL_OLD, MODEL_NEW),
        (MAIN_RESULT_OLD, MAIN_RESULT_NEW), (LIMITS_OLD, LIMITS_NEW), (NOVELTY_OLD, NOVELTY_NEW),
        (ILLUSTRATION_OLD, ILLUSTRATION_NEW), (ROADMAP_OLD, ROADMAP_NEW), (MARKET_MAKER_OLD, MARKET_MAKER_NEW),
        (HORIZON_OLD, HORIZON_NEW), (FOLD_OLD, FOLD_NEW), (BRANCH_OLD, BRANCH_NEW), (PART_IV_OLD, PART_IV_NEW),
        (PASSIVE_TITLE_OLD, PASSIVE_TITLE_NEW), (PASSIVE_THM_OLD, PASSIVE_THM_NEW),
        (PASSIVE_CONST_OLD, PASSIVE_CONST_NEW), (SIM_OLD, SIM_NEW), (OPPOSITE_OLD, OPPOSITE_NEW),
        (OPPOSITE2_OLD, OPPOSITE2_NEW), (TABLE2_NOTE_OLD, TABLE2_NOTE_NEW), (QUESTIONS_PRE_OLD, QUESTIONS_PRE_NEW),
        (MODULUS_OLD, MODULUS_NEW), (MODULUS2_OLD, MODULUS2_NEW), (BOUNDARY_OLD, BOUNDARY_NEW),
        (SEP_COR_OLD, SEP_COR_NEW), (INSTRUMENTS_OLD, INSTRUMENTS_NEW), (SEP_SETUP_OLD, SEP_SETUP_NEW),
        (SEP_THM_OLD, SEP_THM_NEW), (TARGET_PRE_OLD, TARGET_PRE_NEW), (TARGET_II_OLD, TARGET_II_NEW),
        (TARGET_III_OLD, TARGET_III_NEW), (INFO_UNIFORM_OLD, EQCUT_BLOCK), (PILOT_OLD, PILOT_NEW),
        (PILOT_III_OLD, PILOT_III_NEW), (PILOT_DISC_OLD, PILOT_DISC_NEW), (PILOT_TICK_OLD, PILOT_TICK_NEW),
        (LEMMA_OLD, LEMMA_NEW), (PARADOX_OLD, PARADOX_NEW), (RECORDVALUE_OLD, RECORDVALUE_NEW),
        (RECORDVALUE_DISC_OLD, RECORDVALUE_DISC_NEW), (RECORDVALUE_FIT_OLD, RECORDVALUE_FIT_NEW),
        (CONCL_OLD, CONCL_NEW), (CONCL_LIMITS_OLD, CONCL_LIMITS_NEW), (APPX_SEP_OLD, APPX_SEP_NEW),
        (APPX_PILOT_OLD, APPX_PILOT_NEW),
        (TAIWAN_INTRO_OLD, TAIWAN_INTRO_NEW.replace(r'\footnote{', r'\footnote{\label{fn:persist}', 1)),
        (TAIWAN_TABLE_CAPTION_OLD, TAIWAN_TABLE_CAPTION_NEW), (TAIWAN_PERSIST_ROW_OLD, TAIWAN_PERSIST_ROW_NEW),
        (FIG3_CAPTION_OLD, FIG3_CAPTION_NEW), (TAIWAN_GRANT_OLD, TAIWAN_GRANT_NEW), (TAIWAN_ITEMS_OLD, TAIWAN_ITEMS_NEW),
        (TWSE_AUCTION_OLD, TWSE_AUCTION_NEW), (CAT_OLD, CAT_NEW),
        (DECL_AUTHORS_OLD, DECL_AUTHORS_NEW), (DECL_RELATED_OLD, DECL_RELATED_NEW), (DECL_DATA_OLD, DECL_DATA_NEW),
    ]:
        t = rep(t, old, new)
    a, b = _span(t, TAIWAN_QUAL_OLD_START, TAIWAN_QUAL_OLD_END)
    t = t[:a] + TAIWAN_QUAL_NEW + t[b:]
    a, b = _span(t, TAIWAN_HOLDOUT_OLD_START, TAIWAN_HOLDOUT_OLD_END)
    t = t[:a] + taiwan_holdout_paragraph() + t[b:]
    a, b = _span(t, DECL_AI_OLD_START, DECL_AI_OLD_END)
    t = t[:a] + decl_ai_new() + t[b:]
    t = add_references(t)
    return t
