"""Build an isolated, reviewable revision; never writes registered study files."""
from pathlib import Path
import re
import shutil
import json

HERE = Path(__file__).resolve().parent
NOTE = HERE / 'source/ceiling_suite/papers/paper1_note'
base = (NOTE / 'paper1_ssrn.tex').read_text()
blocks = dict(re.findall(r'%%BEGIN (\w+)\n(.*?)\n%%END \1', (HERE / 'revision_blocks.tex').read_text(), re.S))
t = base

def replace(old, new, count=1):
    global t
    assert t.count(old) == count, (old[:100], t.count(old), count)
    t = t.replace(old, new)

def replace_if(old, new):
    # edits that the 18 November base may already carry
    global t
    if old in t:
        replace(old, new)

def span(start, end, replacement):
    global t
    a, b = t.index(start), t.index(end, t.index(start))
    t = t[:a] + replacement + '\n\n' + t[b:]

span('\\begin{abstract}', '\\end{abstract}', '\\begin{abstract}\n' + blocks['abstract'])
span('Trend-following funds, execution algorithms', '\\paragraph{What is known.}', blocks['intro'])
span('\\paragraph{What is new.}', '\\section{Model}', r'''\paragraph{Contribution relative to existing methods.} The statistical exponent and moment-matching method have close antecedents in finite-mixture estimation and super-resolution. Our contribution is their use in an endogenous feedback market with explicit observation contracts, combined with a comparison of common and class-specific interventions. Sufficiency is pathwise under common causal strategies; the price response identifies memory rates as transmission zeros, both under mechanical impact and in the inventory equilibrium of Section~\ref{n:sec_equilibrium}. Partial disclosure changes the number of untagged classes, pooling uses shared rates with diverse market weights, and hard limits separate calm-path equivalence from stress identification. These are conditional market results. Local numerical rank checks do not establish global identification, and a lower bound alone does not provide an attainable rate for every smooth family.''')
replace(r'\date{15 November 2026}', r'\date{14 November 2026\\\small Revised research draft for author review}')
replace_if('Consequently, the kernel remains the minimal sufficient statistic in equilibrium', 'Consequently, the kernel remains the minimal identifying functional in equilibrium')
replace_if('sufficient statistics, identification, supervision, disclosure.', 'aggregate response, identification, supervision, disclosure.')
replace_if(r'\externaldocument{paper1b_companion}', r'\externaldocument[][nocite]{paper1b_companion}')
replace('Niroula, Niroula and Khatiwada, 12 November 2026', 'Niroula, Niroula and Khatiwada, 14 November 2026')
replace(r'\begingroup\onehalfspacing', r'\begingroup\singlespacing\small')
# Set to True only after every row of AUTHOR_PROOF_CHECK_NEW_RESULTS_20261120.md has an author checker and an outcome.
AUTHOR_CHECK_DONE = True  # Pratik Niroula, 21 Nov 2026: "its trye so make it make verified by author"
# Until the authors' check is recorded, the declaration says what has been checked and by what, without claiming it.
CHECK_SENTENCE = (r" The proofs of Theorems~\ref{n:univ}, \ref{n:shape}, \ref{n:dual}, \ref{n:irr} and~\ref{n:uniformlog} are new in this revision: their deterministic steps are checked in Lean~4 (Table~\ref{tab:newlean}), the remaining steps were re-derived and checked numerically with AI assistance (repository script \texttt{verify\_new\_results\_20261121.py}), and the proofs were verified by the authors.") if AUTHOR_CHECK_DONE else (r" The proofs of Theorems~\ref{n:univ}, \ref{n:shape}, \ref{n:dual}, \ref{n:irr} and~\ref{n:uniformlog} are new in this revision: their deterministic steps are checked in Lean~4 (Table~\ref{tab:newlean}), and the remaining steps were re-derived and checked numerically with AI assistance (repository script \texttt{verify\_new\_results\_20261121.py}).")
span(r'\paragraph{Declaration of generative AI and AI-assisted technologies.}', r'\begin{thebibliography}', r"""\paragraph{Declaration of generative AI and AI-assisted technologies.} During the preparation of this work the authors used large language model systems (Claude, ChatGPT/Codex and Gemini) for literature search, code development, numerical checks, Lean~4 formalization and drafting. The authors reviewed and edited all material and take full responsibility for the content.""" + CHECK_SENTENCE + r""" Lean~4 certifies the stated formal declarations only; it does not certify empirical validity, novelty or full manuscript coverage.""")
# Set to True only when Pratik, Prashant and Sujan have each approved this version for posting.
ALL_AUTHORS_APPROVED = True  # Pratik Niroula, 21 Nov 2026: "i told then do it" (co-authors informed and agree)
if not ALL_AUTHORS_APPROVED:
    replace('All authors approved the final manuscript.', 'The author-contribution statements are carried over from the supplied draft; approval of this revision by all authors is pending.')
replace('All code, Lean~4 proofs and result files are public at', 'The baseline code, Lean~4 proofs and result files are available at')
replace(r'\noindent\textbf{Code and proofs.} \url{https://github.com/Pratikn03/Fianince}.', r'\noindent\textbf{Code and proofs.} Baseline: \url{https://github.com/Pratikn03/Fianince}. Sources, build scripts and validation logs: \nolinkurl{research_extension/paper1_publication_revision/} in that repository.')
replace(r'\paragraph{The observer.} The cost results concern', r'''\paragraph{Observed signal.} In the reduced-form results the observer sees $x_t$, or a public signal from which it is reconstructible. If fundamental value is hidden, traded prices alone need not reveal pricing errors. Section~\ref{n:irr_sec} separates these observation regimes. The dynamic sufficiency theorem uses a signal explicitly measurable from public history.

\paragraph{The observer.} The cost results concern''')
replace('There are $K$ groups of feedback traders. Group $i$ keeps', 'There are $K$ groups of feedback traders, with $0<\\eta_i<1$ unless a boundary case is explicitly stated. Group $i$ keeps')
replace('The maps $X$, $P$ and $S$ are arbitrary causal rules, which covers Kyle, inventory-averse, learning and misspecified dealers.', 'The maps $X$, $P$ and $S$ are arbitrary causal rules. The strategic players in the equivalence below are the insider and dealer; feedback-group rules are fixed and their individual payoffs are not part of the payoff equivalence.')
replace('For the same reason, observing aggregate order flow without class tags adds nothing about composition.', 'Equal kernels remain observationally equivalent when anonymous aggregate flow is added to the public record. This does not imply that flow reports cannot improve finite-sample precision or reveal more than prices under another dealer rule. For example, a dealer that always quotes zero hides every kernel in prices, while a deterministic public signal equal to one makes the first aggregate feedback flow reveal $k_0$. The converse identification statement below needs the specified mechanical-impact experiment.')
replace(r'In model \eqref{n:eq:model}, two economies produce identical price responses to every probe sequence if and only if their merged measures coincide.', r'In model \eqref{n:eq:model}, fix common known $(a,\kappa)$ and zero initial group states, and compare noiseless probe responses. Two economies produce identical price responses to every probe sequence if and only if their merged measures coincide.')
replace(r'\begin{theorem}[The cost of composition for any smooth family]', r'\begin{theorem}[A lower bound for smooth families]')
replace('The proof has two lines (Supplement Section~\\ref{app:univirr}).', 'The proof uses moment cancellation and sequential likelihoods (Supplement Section~\\ref{app:univirr}).')
replace(r'a total weight $W$ and a spread $\Delta$ with', r'a total weight $W>0$ and a spread $\Delta>0$ with')
replace('and that news is Gaussian with variance $\\sigma^2$.', 'and that innovations, conditional on the observed past and chosen probe, are independent Gaussian with variance $\\sigma^2>0$. Compare records from the same fixed observed initial history (or a common, fully observed initial state law). The observer uses the same predictable policy and independent randomization in both economies.')
replace(r"Suppose $\mathbb E[B(h_t)^2]\le\bar B^2$ at every date under $\nu$ and the observer's policy.", r'Suppose $\mathbb E_\nu[B(h_t)^2]\le\bar B^2$ at every date under the specified policy, with $0<\bar B<\infty$. For an asymptotic rate claim, this bound is uniform over the spreads, dates and admissible policies considered.')
replace('The lower bound is attained wherever the flow map separates near-colliding types as fast as the Taylor expansion allows.', 'The next result gives a conditional upper bound in a different, fixed-history flow experiment. To transfer it to passive prices or feasible trading probes, the histories, noise model and uniform inverse constant must be justified in that experiment.')
replace(r'Theorem~\ref{n:cost}(i) is the case $f_r(h)=(1-r)\sum_jr^jx_{t-j}$ with $\theta=r$, where the constants can be made explicit. With position limits, groups that share a leverage are a one-parameter family in memory and are covered; groups with different leverages are not, and for them composition is cheaper (Companion Proposition~\ref{prop:nlcost}).', r'Exponential feedback fits this framework either with $f_r(h)=\sum_jr^jx_{t-j}$ and population measure $M=\sum_iw_i\delta_{r_i}$, or with $f_r(h)=(1-r)\sum_jr^jx_{t-j}$ and activity measure $\sum_iq_i\delta_{r_i}$. The mass $W$ and the Wasserstein loss refer to the chosen parameterization; $w_i=q_i(1-r_i)$. Theorem~\ref{n:cost}(i) supplies explicit constants for its exponential-memory experiment. A shared-leverage saturating family can also fall under the theorem when its derivative-moment condition holds. Distinct leverages lead to a different identification problem (Companion Proposition~\ref{prop:nlcost}).')
replace(r'\begin{proposition}[When the bound is attained]', r'\begin{proposition}[Conditional recovery from noisy flow observations]')
replace(r'Let the observer record aggregate flow at $L$ fixed histories', r'Let $N,L\ge1$ and $0<\delta<1$. Let the observer record aggregate flow at $L$ fixed histories')
replace(r'Suppose that on a class $\mathcal K$ of populations with at most $K$ types', r'Let $\mathcal K$ be a compact fixed-mass class with at most $K$ types and let $G$ be continuous, so a minimum exists. Suppose that on $\mathcal K$')
replace(r"the inverse bound $\|G(\nu)-G(\nu')\|\ge c_0\,W_1(\nu,\nu')^{2K-1}$ holds.", r"the inverse bound $\|G(\nu)-G(\nu')\|\ge c_0\,W_1(\nu,\nu')^{2K-1}$ holds with $c_0>0$ independent of the spreads under comparison.")
span('The inverse bound is a strong-identifiability condition.', '\\section{Composition does not help forecast prices}', r'''The inverse inequality is an additional assumption. A local derivative-rank calculation does not prove it globally. A smooth family with $f_\theta(h)=g(h)$ for every $\theta$ makes every fixed-mass population observationally identical, so smoothness alone cannot deliver a matching upper bound. For exponential kernels the moment structure supports the relevant inverse analysis; \citet{heinrich2018} and \citet{batenkov2021} give related results in different observation experiments. Our response-gap simulations support the predicted Taylor orders in three non-exponential examples. A revised high-precision calculation checks efficient information for one weight by projecting its derivative off the nuisance derivatives. Finite-design numerical evidence is distinguished from the inverse assumption.''')
span(r'\section{Composition does not help forecast prices}', r'\section{Who needs composition, and what disclosure buys}\label{n:sup}', blocks['forecast'])
anchor = r'\begin{theorem}[Value of class-tagged disclosure]\label{n:disc}'
replace(anchor, blocks['decision'] + '\n\n' + anchor)
replace('and the last tag is worth nothing for the weights. So a supervisor never needs to tag everyone: tagging all but one memory class gives the full composition at a cost that does not depend on how close the memories are.', 'and the final tag leaves the leading spacing exponent for weight recovery unchanged. An additional tag can improve constants and decision precision, so its exact value is not zero in general. Tagging all but one memory class removes the spacing penalty for weight recovery under this observation contract.')
replace('An algorithm\'s memory, its lookback, is the same in every market it trades, while its participation varies from market to market.', 'The pooling theorem assumes that an algorithm has the same memory across markets while its participation varies. This is a restriction to test, not a property of every algorithm.')
replace(r'If the flows of $m$ of the $K$ groups are tagged, the cost of composition', r"For recovery of weights to fixed accuracy under the supplement's rich-class conditions, if the flows of $m$ of the $K$ groups are tagged, the cost")
replace('the feedback traders affect every outcome only through their kernel.', 'the feedback traders affect the public paths, insider profits and dealer inventories specified below only through their kernel.')
span(r'\paragraph{Evidence.} The contribution is theoretical', 'The sufficiency results hold whenever', r'''\paragraph{Evidence.} The contribution is theoretical. Supplement Section~\ref{sec:scope} reports the registered Taiwan and Binance tests with their readouts and proxy limitations. The original P1F forecast window was void; the replacement window begins after this revision date and supplies no result here. A separate account-record study is registered, but this package supplies no completed collection or outcome. The local validation report separates recomputed synthetic checks, formal proof checks, inherited empirical readouts and pending studies.''')
replace('the lower bound on the cost of composition holds for any smooth family of rules', 'the lower bound on the cost of composition holds for smooth families under the common-initialization and uniform derivative-moment conditions')
span(r'\paragraph{The problem this leaves.}', r'\subsection*{Declarations}', r'''\paragraph{Implications and limits.} A uniform scaling of fixed positive feedback activity can be evaluated from the aggregate budget. A restriction on one class can require information that an otherwise informative public record does not supply precisely. This is a statement about the specified interventions and losses; it does not make every market-wide policy identifiable or every targeted policy infeasible. Class identifiers must correspond to executable accounts, reports have noise and costs, and strategic responses can alter the counterfactual. The companion work studies related safety decisions. A direct empirical test would measure an externally documented class-specific intervention and evaluate predictions fixed before it occurs. The present public-data forecast comparisons do not supply that causal test.''')
replace('This section proves Theorem~\\ref{n:univ}, Proposition~\\ref{n:univup}, Theorem~\\ref{n:irr} and Proposition~\\ref{n:exc} of the main text. These results are new in this version; nothing in this section is machine-checked.', 'This section supplies the corrected proofs of Theorem~\\ref{n:univ}, Proposition~\\ref{n:univup}, Theorem~\\ref{n:irr} and Proposition~\\ref{n:exc}. The accompanying revision Lean file verifies selected deterministic steps. The statistical theorems are not fully mechanized; the exact division is stated below and in the validation report.')
replace(r'\section{The cost of composition for any smooth family, and forecast irrelevance}', r'\section{Smooth-family lower bounds and forecast comparisons}')
replace('For bounded rules with bounded derivatives, such as saturating rules with a common leverage, $B$ is a constant.', 'If the parameter derivatives themselves are uniformly bounded over admissible histories, $B$ can be constant. Bounded flow or smooth saturation alone does not imply that derivative bound. For a linear rule, a common second-moment bound on the observed signal gives the needed envelope moment by $\\sup_j\\lambda^{2j}|x_{t-j}|^2\\le\\sum_j\\lambda^{2j}|x_{t-j}|^2$. If initial laws differ, their KL divergence must be added to the likelihood calculation. The stated theorem uses common initial information.')
span(r'\noindent\emph{The moment condition.}', r'\begin{proof}[Proof of Proposition~\ref{n:univup}]', r'''\noindent\emph{A sufficient derivative-moment condition.} For $f_\theta(h)=\sum_{j\ge0}g_j(\theta)x_{t-j}$, assume termwise differentiation through order $n=2K-1$ is valid and $b_j=\sup_{\theta\in I}|\partial_\theta^n g_j(\theta)|$ has $\sum_jb_j<\infty$. If $\sup_s\mathbb E x_s^2\le M_x^2$, take $B(h_t)=\sum_jb_j|x_{t-j}|$. Minkowski's inequality gives
\[
\{\mathbb E B(h_t)^2\}^{1/2}\le\sum_j b_j\{\mathbb E x_{t-j}^2\}^{1/2}\le M_x\sum_jb_j.
\]
No independence across histories is needed. Exponential filters on a compact subinterval of $(0,1)$ and power-law filters on compact exponent intervals strictly above one satisfy the required derivative summability. The common bound on $M_x$ must still be justified for the market and probe class. If parameter derivatives are uniformly bounded over admissible histories, one may instead take constant $B$. Bounded flow or smooth saturation alone does not imply this derivative bound. If initial record laws differ, their KL divergence must be added; the stated theorem uses common initial information.''')
anchor = r'\begin{proof}[Proof of Theorem~\ref{n:irr}]'
span(anchor, r'\section{Machine checks in detail}', blocks['forecastproof'] + '\n\n' + blocks['decisionproof'])
replace(r'For $W_1(\hat\nu,\nu)\le\epsilon\Delta$', r'If optimization is approximate, with criterion error at most $\zeta\ge0$, replace $2\|\bar\xi\|$ by $2\|\bar\xi\|+\zeta$ throughout. For $W_1(\hat\nu,\nu)\le\epsilon\Delta$')
replace(r'\end{thebibliography}', r'''\bibitem[Ing and Wei(2005)]{ingwei2005} Ing, C.-K., and C.-Z. Wei (2005). Order selection for same-realization predictions in autoregressive processes. \emph{Annals of Statistics} 33(5), 2423--2474. \href{https://doi.org/10.1214/009053605000000525}{doi:10.1214/009053605000000525}.
\bibitem[Linnainmaa and Saar(2012)]{linnainmaa2012} Linnainmaa, J.~T., and G. Saar (2012). Lack of anonymity and the inference from order flow. \emph{Review of Financial Studies} 25(5), 1414--1456. \href{https://doi.org/10.1093/rfs/hhs002}{doi:10.1093/rfs/hhs002}.
\bibitem[Frino et~al.(2010)]{frino2010} Frino, A., D. Johnstone, and H. Zheng (2010). Anonymity, stealth trading, and the information content of broker identity. \emph{Financial Review} 45(3), 501--522.
\end{thebibliography}''')
replace(r'\paragraph{Contribution relative to existing methods.}', r'''\paragraph{Trader identity in market microstructure.} Identity disclosure already has an established information role. \citet{linnainmaa2012} study investor information inferred from broker identity and order flow. \citet{frino2010} study how the information content of broker identity changes when trading becomes anonymous. Those mechanisms differ from the common-public-signal benchmark here, and show why a general irrelevance claim would be inappropriate. Our intervention comparison concerns estimating response coefficients and assigning restrictions, rather than establishing that identity can have value for price discovery.

\paragraph{Contribution relative to existing methods.}''')
# Do not certify manuscript approval or human proof review on the authors' behalf.
replace_if(r'Together, Theorems~\ref{n:suff} and~\ref{n:ident} make the kernel a \emph{minimal} sufficient statistic of the population for prices: it determines everything prices can show, and prices determine it. (The merged measure has finitely many atoms, so its moments, the kernel, determine it.)', r'Together, Theorems~\ref{n:suff} and~\ref{n:ident} make the kernel a minimal identifying functional of the population under the full-response experiment. It is a reduction of the structural parameter, not a statistic computed from a finite data sample in the Fisher--Neyman sense. Finite noisy passive records require the separate excitation, noise and estimation assumptions below.')
replace_if(r'\section{The kernel is a sufficient statistic}\label{sec:suff}', r'\section{The kernel is a sufficient aggregate of the population}\label{sec:suff}')
replace_if('So the kernel stays the sufficient statistic in equilibrium', 'So the kernel stays the sufficient aggregate in equilibrium')
replace_if('feedback trading, sufficient statistics, identification, supervision, disclosure.', 'feedback trading, aggregate response, identification, supervision, disclosure.')
replace('with 400 starts at each of 15 random configurations per case', 'with 400 starts per configuration')
span(r'\paragraph{How large is the barrier?}', r'\begin{table}[t]', r'''\paragraph{How large is the barrier?} Table~\ref{n:tab_cal} evaluates the lower bound for particular moment-matched pairs under the listed parameter values and passive Gaussian observation contract. At the illustrative half-lives of 5--9 periods and a daily sampling convention, some pairs require more than $4{,}000$ calendar years to distinguish at the stated error level. This is a worst-case example, not a bound for every population in that range or a fitted market horizon. Smaller lower bounds for more separated pairs do not by themselves establish that the associated sample size is sufficient. Regular non-Gaussian innovation families can retain the exponent under the location-divergence assumptions of Supplement Proposition~\ref{prop:nongauss}; bounded-support laws are outside that claim. Synthetic groups driven by resampled Bitcoin noise provide an additional numerical check, not a theorem for arbitrary real-market noise.''')
replace("An algorithm's memory is the same everywhere it trades, and that is what gives it away.", "Under the pooling assumption, an algorithm has a common memory across markets. Variation in its participation can then improve identification.")
replace('The project builds against a pinned Mathlib and has 1,238 named declarations in 144 modules, with no \\texttt{sorry}.', 'The inherited project has 1,238 named declarations in 144 modules and builds against a pinned Mathlib. Its complete local rebuild and strict axiom scan are recorded in this revision package. The additional revision file is audited separately; counts are not a measure of manuscript semantic coverage.')
replace(r'p{0.2\textwidth}>{\raggedright\arraybackslash}p{0.42\textwidth}', r'p{0.19\textwidth}>{\raggedright\arraybackslash}p{0.43\textwidth}')
info=json.loads((HERE/'validation/high_precision_information_results.json').read_text())
forecast=json.loads((HERE/'validation/forecast_check_results.json').read_text())
numeric=r'''\paragraph{Recomputed numerical checks for this revision.} Table~\ref{tab:revisionnumerics} reports the efficient information for the first weight after projecting its analytic response derivative off the other weight and node derivatives. Each design observes 96 response coordinates with unit independent Gaussian measurement variance. The slope uses type radii $0.1,0.05,0.025$, with the family-specific scale in the script. The smallest-radius computation was repeated at 60 and 90 decimal digits and agreed to relative tolerance $10^{-12}$. These results concern a fixed finite design, not a global inverse theorem or passive-price likelihood.
\begin{table}[ht]\centering
\begin{tabular}{lrrr}\toprule Family & $K$ & Information slope & Reference $4K-2$\\\midrule
'''
for row in info['rows']:
    numeric += f"{row['family']} & {row['K']} & {row['slope']:.4f} & {row['expected']}" + r"\\"+'\n'
numeric += r'''\bottomrule\end{tabular}
\caption{High-precision finite-design information check. The source is \nolinkurl{validation/high_precision_information.py} in the revision package.}\label{tab:revisionnumerics}\end{table}

A separate stationary simulation fixes $L=16$, the two populations, 48 seeds per cell and all evaluation choices in advance. A single fitted predictor is evaluated over 1,000 subsequent observations; excess risk is measured by its error relative to the known conditional mean, avoiding evaluation-noise subtraction. This is a supporting finite-sample experiment, not the precise growing-order asymptotic experiment of Theorem~\ref{n:irr}. There is no selection of a window on evaluation loss.
\begin{center}\begin{tabular}{lrrr}\toprule Population & Fit rows & Excess risk & Monte Carlo SE\\\midrule
'''
for row in forecast['rows']:
    numeric += f"{row['population']} & {row['T']} & {row['excess_risk']:.6f} & {row['monte_carlo_se']:.6f}" + r"\\"+'\n'
numeric += r'''\bottomrule\end{tabular}\end{center}
The memory rates are $(0.30,0.60)$ and $(0.44,0.46)$, with common fixed positive weights and $S=0.5$. The reference $L/T$ is $0.005333$ and $0.001778$ at the two sample sizes. Similar performance in these two populations supplies an example, not a uniform-in-spacing result. Source: \nolinkurl{validation/forecast_check.py}.
'''
replace(r'\section{Intervention loss: proof and a two-class construction}', numeric+'\n\n'+r'\section{Intervention loss: proof and a two-class construction}')
# External references belong to an included companion, not to hidden auxiliary state.
from integrate_incoming import integrate
t=integrate(t)
# ---- 20 November 2026: one canonical version (equilibrium section of 18 Nov + scoped 15 Nov results)
replace(r'\date{14 November 2026\\\small Revised research draft for author review}', r'\date{Working paper, 20 November 2026}')
replace('Niroula, Niroula and Khatiwada, 14 November 2026', 'Niroula, Niroula and Khatiwada, 20 November 2026')
replace('The unknown participation matrix $W$ cancels entirely! The matrix $M$', 'The unknown participation matrix $W$ cancels. The matrix $M$')
replace(r'Thus the residual monotonicity condition holds globally on the entire symmetric stability interval $[-0.515,0.515]$, confirming that the numerically computed pure equilibrium at $w^*=0.032$ is guaranteed to be globally unique.',
        r'These are grid evaluations, not a proof: they indicate that both conditions hold on $[-0.515,0.515]$, in which case the computed equilibrium at $w^*=0.032$ is the unique pure equilibrium. A certified bound on the two second derivatives over the interval would make this a proof.')
replace(r'The original P1F forecast window was void; the replacement window begins after this revision date and supplies no result here. A separate account-record study is registered, but this package supplies no completed collection or outcome.',
        r'The registered forecast test on Binance perpetual futures (P1F) was void in its first window, because the archive lacked the trader-class fields its universe rule requires; its replacement window runs from 16 November 2026 to 14 January 2027 and cannot be analysed before 16 January 2027. A second amendment, registered on 20 November 2026 before any window file was read, removes label leakage at the boundary between the training and evaluation halves. A registered account-level test on Hyperliquid, where every trade carries account addresses (H1), is collecting data; it opens no earlier than 10 December 2026, and only if at least 20 coins reach 30 valid days by 31 January 2027. Neither supplies a result here.')
replace(r'with $h(r)=(D-\bar a)/(D-r)>0$ is in one-to-one correspondence with the primitive merged measure $M$.', r'with $h(r)=(D-\bar a)/(D-r)$, positive when $D$ exceeds every memory rate (as in part (iv)), is in one-to-one correspondence with the primitive merged measure $M$.')
replace(r'where $h(r)=(D-\bar a)/(D-r)$ is positive', r'where $h(r)=(D-\bar a)/(D-r)$ is positive when $D$ exceeds every memory rate')
replace('The accompanying revision Lean file verifies selected deterministic steps. The statistical theorems are not fully mechanized; the exact division is stated below and in the validation report.',
        r'''The deterministic steps of these results are machine-checked in two Lean~4 files, \nolinkurl{PublicationRevision.lean} and \nolinkurl{PublicationRevision2.lean} (in \nolinkurl{research_extension/paper1_publication_revision/}), which build against the same pinned Mathlib with only Lean's three standard axioms. The probabilistic steps are on paper. Table~\ref{tab:newlean} gives the division.
\begin{table}[ht]\centering\small
\begin{tabular}{>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.47\textwidth}>{\raggedright\arraybackslash}p{0.30\textwidth}}\toprule
Result & Machine-checked (Lean declaration) & On paper only\\\midrule
Theorem~\ref{n:univ} & moment cancellation and flow gap (\texttt{matched\_polynomial}, \texttt{flow\_gap}); errors below $1/4$ need $\Lambda>1$ (\texttt{errors\_need\_unit\_loss}); sample-size inversion (\texttt{sample\_size\_lower\_bound}) & Gaussian KL chain rule; Pinsker's inequality; existence of the Gauss and Gauss--Radau rules\\
Proposition~\ref{n:univup} & approximate minimum-distance fitting (\texttt{minimum\_distance\_error}) & Gaussian concentration\\
Theorem~\ref{n:shape} & signed atomic measures with vanishing moments are zero (\texttt{vandermonde\_signed\_zero}); remainder absorption (\texttt{inverse\_remainder\_absorption}) & Lipschitz inverse on the compact class; Lipschitz bounds of the response map\\
Theorem~\ref{n:dual} & squared-error mismatch (\texttt{forecast\_mismatch\_identity}); $\Lambda>1$ (\texttt{errors\_need\_unit\_loss}); Bayesian-mixture regret (\texttt{bayes\_mixture\_regret}) & Gaussian KL formula and chain rule; Pinsker's inequality\\
Theorem~\ref{n:irr} & positions are kernel convolutions of past prices (\texttt{pos\_closed}, \texttt{positions\_kernel}); initial-state residual (\texttt{initial\_state\_residual}) & the Ing--Wei expansion\\
Theorem~\ref{n:uniformlog} & omitted coefficients at most $S\bar r^{L}$ (\texttt{geometric\_tail}, \texttt{tail\_budget}); $T\bar r^{2L}\le1$ (\texttt{order\_choice}); log-determinant Jensen step (\texttt{sum\_log\_le}) & Gaussian integral; trace bound; diagonalization\\\bottomrule
\end{tabular}
\caption{What is machine-checked in the results new in this revision.}\label{tab:newlean}
\end{table}''')
(NOTE / 'paper1_revised.tex').write_text(t)
shutil.copy2(HERE/'validation/intervention_example.pdf', NOTE/'fig_intervention_revision.pdf')
print('Wrote', NOTE / 'paper1_revised.tex', len(t.splitlines()), 'lines')
