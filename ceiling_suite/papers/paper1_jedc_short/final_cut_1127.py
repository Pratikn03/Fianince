"""Final restructuring of 27 November 2026 (author request): a shorter main text and a plainer introduction and
conclusion. Applied last in the build, after sharpen_1127.main_text and sharpen_1127.supplement.

Main text: the introduction and conclusion are rewritten (same results, same numbers, plainer and shorter); the
instrument proposition, the single-halt corollary and the partial-tags theorem move to the supplement with one-sentence
summaries; Appendix A keeps the proofs of Theorems 3.1, 3.2, 5.2, 7.1 and 7.3, and the other proofs move to Supplement
Section S7. Supplement: receives the moved material; references are rewritten from labels, not by hand.
"""
import re

KEEP_PROOFS = ('n:suff', 'thm:what-id', 'n:passiveupper', 'n:separation', 'n:pilot')


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:140], n, count)
    return t.replace(old, new)


def cut_between(t, start, end, include_end=True):
    a = t.index(start)
    assert t.count(start) == 1, start[:80]
    b = t.index(end, a) + (len(end) if include_end else 0)
    return t[:a] + t[b:], t[a:b]


INTRO = r"""\section{Introduction}

A market supervisor can often measure how strongly a market reacts to its own past prices long before it can say which traders produce that reaction. The two are different objects. If a policy scales every trader group's feedback by the same factor, the aggregate response is all the supervisor needs to evaluate it. If the policy halts one class of traders, the supervisor needs that class's own contribution. This paper asks where the line between the two falls, and what it costs a supervisor to cross it.

The mechanism is easiest to see with two algorithms. Suppose each trades on an exponentially weighted average of past pricing errors, one with memory rate $0.49$ and the other with $0.51$, in equal size. Prices clear only aggregate order flow, so the two blend: together they produce nearly the same flow as a single group at $0.50$. The first- and second-order differences cancel, the remaining difference in lag curvature is of order $\Delta^3$ with $\Delta = 0.01$, and detecting it takes of order $\Delta^{-6}$ noisy observations; with $K$ nearby groups it takes $\Delta^{-(4K-2)}$. A uniform cut does not care about this blending. A targeted halt does.

\textbf{The model.} We put heterogeneous feedback-trading algorithms into a linear market and into an inventory-dealer equilibrium. With a common public signal and fixed causal rules, the trader population enters every public outcome---prices, total order flow, insider profits and dealer inventories---only through its aggregate flow map (Theorem~\ref{n:suff}). For linear rules this map is the \emph{feedback kernel}, the moment sequence of the population's merged memory-rate measure. In Section~\ref{sec:equilibrium}, price impact and the persistence of pricing errors come from competitive, risk-averse dealers who carry inventory, and equilibrium prices follow the same closed-loop recursion with unchanged memory rates (Theorems~\ref{n:thm_inventory} and~\ref{n:thm_eqreduced}). The barriers below are therefore equilibrium properties, not artifacts of mechanical price impact.

\textbf{The main result.} Theorem~\ref{n:separation} is a supervisory separation. Given persistence, impact and a memory bound, whether a uniform feedback cut meets a stability ceiling depends on the population only through the aggregate budget. Kernel-tap records, or one passive price record, estimate that budget at a near-parametric rate however close the traders' memories are (Theorem~\ref{n:passiveupper}), and without tags the uniform cut is minimax over labelings (Theorem~\ref{n:minimax}). Whether a targeted restriction meets the same ceiling can require $c\sigma^2(\Delta\eta)^{-(4K-2)}$ records (Proposition~\ref{n:target}). There are two ways around this. Verified class tags remove the spacing penalty for class weights (Theorem~\ref{n:disc}). A pilot of the restriction does the same after the fact: once a restriction is in force, the change in the price response is the removed groups' own kernel, so prices alone learn the restriction's effect at a near-parametric rate (Theorem~\ref{n:pilot}).

\textbf{The limits of tags.} Tags work only as long as traders cannot game them. If restricted traders can route activity through accounts carrying another label at convex cost $\gamma$, the optimal restriction is partial and class tags lose all value as $\gamma \to 0$ (Proposition~\ref{n:relabel}). Records that link accounts to beneficial owners keep their value only to the extent that they make such routing visible; the model takes this as a property of the audit trail, not as a result. Without tags, surveillance invites a different response. Against a fixed-level test whose power grows at least like the square root of the divergence, a high-stakes untagged algorithm moves its memory toward its neighbor as the supervisor's record $N$ grows. Divergence scales as $N\delta^4$ in the memory distance $\delta$, so the supervisor's information falls at rate $N^{-1}$ and detection collapses toward the false-alarm rate (Theorem~\ref{n:paradox}). A longer price record therefore never substitutes for an owner-linked one: in equilibrium its value falls like $N^{-1/2}$ (Theorem~\ref{n:recordvalue}).

\textbf{Supporting results.} Theorem~\ref{n:cost} proves the barrier for passive observation and for active impulse probes. It extends to smooth causal rule families and is matched by Prony and minimum-distance recovery (Supplement Theorems~\ref{S-n:univ} and~\ref{S-n:shape}), and it does not vanish as the market approaches instability (Supplement Proposition~\ref{S-prop:nearcrit}; Figure~\ref{fig:near-instability}). Market-wide linear functionals of the merged measure, such as discounted feedback or single-lag taps, are estimated at the parametric rate $\sigma^2\epsilon^{-2}$ whatever the spacing (Theorem~\ref{n:questions} and Corollary~\ref{n:sep}). In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess forecast MSE divided by the innovation variance (Theorem~\ref{n:dual}): composition does not matter for forecasting prices, only for attributing them. Smooth quadratic trading charges can be evaluated from passive pricing-error records, while proportional taxes, exit thresholds and binding turnover caps cannot (Supplement Proposition~\ref{S-thm:instruments}), and with verified partial tags, policies uniform within each tagged group are minimax (Supplement Theorem~\ref{S-n:minimaxtags}).

\textbf{What is new, and what is not.} The minimax rate $\Delta^{-(4K-2)}$ is the known rate for finite mixtures with near-colliding components (Heinrich and Kahn, 2018; Wu and Yang, 2020) and for super-resolution of point sources (Batenkov et al., 2021), and the modulus characterization of linear functionals builds on Donoho (1994). We do not claim those results as new. Three statistical results here have no counterpart in that literature, because they use features a mixture lacks: a single closed-loop price record attains the rate (Theorem~\ref{n:passiveupper}), the barrier survives the approach to instability (Supplement Proposition~\ref{S-prop:nearcrit}), and a restriction deletes part of the population, so a pilot collapses the exponent (Theorem~\ref{n:pilot}). That market-wide policies need only a reduced-form aggregate while targeted ones need structure is Marschak's maxim and the logic of sufficient statistics for policy (Marschak, 1953; Chetty, 2009). What we add is the informational price of that structure in a feedback market: kernel sufficiency survives inventory-equilibrium pricing, in which dealer anticipation over-weights slow memories; uniform rules are minimax over labelings and separate cleanly from targeted ones; and tags have strategic limits, both from relabeling and from crowding.

\textbf{Empirical illustration.} Using daily class-tagged institutional order flows from the Taiwan Stock Exchange (300 stocks, 2013--2016, 270,060 stock-days), we calibrate the bounds to observed institutional rules (foreign investors, investment trusts and dealers). Granting a price-only supervisor the market's persistence, impact and non-feedback flow law, tagged flows carry, at leading order, $4.7 \times 10^5$ times more information per stock-day about composition than prices. On the same grant, a spectral-rate search pins market-wide cut effects to $[0.0014, 0.0019]$, whereas the price-consistent effect of halting foreign feedback spans $[0, 0.0018]$ under nonnegative weights---from zero to nearly the entire aggregate effect (Section~\ref{sec:taiwan}).

"""

CONCLUSION = r"""\section{Scope and Conclusion}\label{sec:conclusion}

Prices tell a supervisor how much feedback a market carries, not who carries it. Under mechanical price impact and in an inventory-dealer equilibrium, the pricing-error response identifies the aggregate kernel under the observation conditions of Sections~\ref{sec:equilibrium} and~\ref{sec:cost}, while separating closely spaced trader classes costs of order $\Delta^{-(4K-2)}$ observations, and that cost does not fall as the market nears instability.

Three policy conclusions follow. First, a market-wide cut is the safe default. Without tags it is minimax over labelings, and given persistence, impact and a memory bound its effect can be calibrated from the aggregate response, or from one passive price record, at a cost that does not depend on how close the traders' memories are (Theorems~\ref{n:separation} and~\ref{n:passiveupper}). Smooth quadratic charges can likewise be evaluated from pricing errors alone, unlike proportional taxes and binding caps (Supplement Proposition~\ref{S-thm:instruments}). Second, a class-specific restriction needs attribution, and there are two ways to obtain it: verified flow tags remove the spacing penalty for weights, and a pilot of the restriction reveals its effect from prices after the fact (Theorem~\ref{n:pilot}). Third, tags are fragile when traders respond to them. Routing orders across labels erodes them, and untagged surveillance invites crowding that no longer record undoes (Theorems~\ref{n:paradox} and~\ref{n:recordvalue}). Records linked to beneficial owners, such as the cross-venue customer linkage in consolidated audit trails, can support targeted supervision to the extent that those links hold.

The results have limits. The explicit identification and upper-bound theorems use linear causal rules with exponential or smooth memory; drifting populations, hard position limits, breach cascades, and saturating or learning algorithms are analyzed in the companion working papers (Niroula et al., 2026c, 2026d). The passive bounds require Gaussian (or quadratically regular) innovations and exclude bounded-support laws. Theorem~\ref{n:paradox} fixes the test; when the supervisor also chooses how hard to monitor, high stakes give either Stackelberg collapse or mixed-strategy auditing (Supplement Proposition~\ref{S-prop:endogenous_supervisor}), and repeated reputation is left out. The Taiwan calibration holds persistence and impact fixed and relies on asymptotic rate proxies, so pure causal feedback and cross-stock independence remain open, and discrete time abstracts from continuous-book cancellations and sub-millisecond races (Supplement Sections~\ref{S-sec:scope} and~\ref{S-sec:natural_experiments}, Proposition~\ref{S-prop:natural_exp}). A direct causal test of the separation would evaluate an exogenous, externally documented class-specific restriction against pre-specified predictions; Theorem~\ref{n:pilot} states the prediction such a test would check.

"""

INSTR_STUB = (r"\textbf{Price and quantity instruments.} The same logic sorts real instruments by the shape of their incidence "
              r"across memories. A small quadratic trading charge reduces the budget through a smooth function of memory, so "
              r"its effect can be estimated from a passive pricing-error record. A proportional tax can break that smoothness "
              r"even when no desk exits, and a tax that drives desks to exit, or a binding turnover cap, puts a kink in the "
              r"incidence, so evaluating it inherits the $(\Delta\eta)^{-(4K-2)}$ lower bound (Supplement "
              r"Proposition~\ref{S-thm:instruments})." + "\n\n")

MINIMAX_PARA_NEW = (r"The proof (Supplement Section~\ref{S-app:proofs}; formalized in Supplement Table~\ref{S-tab:newlean}) "
                    r"specializes the finite-group Hunt--Stein theorem (Lehmann and Romano, 2005, Chapter~8). Integrating the "
                    r"permutation-average inequality over the common price law extends minimax dominance to price-contingent "
                    r"policy rules. Halting a single unverified label guarantees a budget reduction of only the smallest class "
                    r"contribution, and with verified partial tags, policies uniform within each tagged group are minimax, the "
                    r"value of tags being the gain from tailoring intensities across groups (Supplement "
                    r"Corollary~\ref{S-cor:robustuniform} and Theorem~\ref{S-n:minimaxtags}).")


def _labels(text):
    return set(re.findall(r'\\label\{([^}]+)\}', text))


def main_text(t, moved):
    # 1. Introduction and conclusion
    a = t.index(r"\section{Introduction}")
    b = t.index(r"\subsection{Related literature}", a)
    t = t[:a] + INTRO + t[b:]
    a = t.index(r"\section{Scope and Conclusion}\label{sec:conclusion}")
    b = t.index(r"\section*{Declarations}", a)
    t = t[:a] + CONCLUSION + t[b:]
    t = rep(t, r"Appendix~\ref{app:proofs} collects self-contained proofs of the main economic theorems.",
            r"Appendix~\ref{app:proofs} proves the headline results (Theorems~\ref{n:suff}, \ref{thm:what-id}, "
            r"\ref{n:passiveupper}, \ref{n:separation} and~\ref{n:pilot}); the other proofs are in Supplement "
            r"Section~\ref{S-app:proofs}.")
    # 2. Side results to the supplement
    t, moved['f_instr'] = cut_between(t, r"\textbf{Endogenous desk adjustments to taxes, holding schedules, and caps.}",
                                      r"raising net $S$ (Supplement Section~\ref{S-sec:margin_scaling}).")
    t = rep(t, r"\begin{corollary}[Expected loss from weakly identified targeting]",
            INSTR_STUB + r"\begin{corollary}[Expected loss from weakly identified targeting]")
    t, moved['f_robust'] = cut_between(t, r"\begin{corollary}[Guarantee of a single halt]", "\\end{corollary}\n")
    t, moved['f_tags'] = cut_between(t, r"Verified partial tags break permutation symmetry across tagged groups while "
                                        r"preserving it within each group:", "\\end{theorem}\n")
    m = re.search(r"The proofs of Theorems~\\ref\{n:minimax\} and~\\ref\{n:minimaxtags\}.*?price-contingent policy rules\.", t, re.S)
    assert m
    t = t[:m.start()] + MINIMAX_PARA_NEW + t[m.end():]
    # 3. Proofs: keep the headline ones in Appendix A
    a = t.index(r"\label{app:proofs}")
    b = t.index(r"\bibliography" if r"\bibliography" in t[a:] else r"\begin{thebibliography}", a) if (r"\bibliography" in t[a:] or r"\begin{thebibliography}" in t[a:]) else len(t)
    app = t[a:b]
    proofs = list(re.finditer(r"\\begin\{proof\}\[Proof of (.*?)\]\n?.*?\\end\{proof\}\n?", app, re.S))
    keep_app, moved_proofs, last = [], [], 0
    for p in proofs:
        head = p.group(1)
        keep_app.append(app[last:p.start()])
        if any('{' + k + '}' in head for k in KEEP_PROOFS):
            keep_app.append(p.group(0))
        else:
            moved_proofs.append(p.group(0))
        last = p.end()
    keep_app.append(app[last:])
    t = t[:a] + ''.join(keep_app) + t[b:]
    moved['f_proofs'] = '\n'.join(moved_proofs)
    t = rep(t, r"Extended derivations and the exact mapping between deterministic proof steps and Lean~4 formalizations "
               r"appear in the Online Supplement",
            r"This appendix proves the headline results. The proofs of the other main-text results, extended derivations, "
            r"and the exact mapping between deterministic proof steps and Lean~4 formalizations appear in the Online "
            r"Supplement")
    # 4. Body pointers to proofs that moved
    for old, new in [
        (r"are given in Appendix~\ref{app:proofs}. Economically,", r"are given in Supplement Section~\ref{S-app:proofs}. Economically,"),
        (r"Appendix~\ref{app:proofs} gives the argument.", r"Supplement Section~\ref{S-app:proofs} gives the argument."),
        (r"The proof is given in Appendix~\ref{app:proofs} (combining", r"The proof is given in Supplement Section~\ref{S-app:incoming} (combining"),
        (r"The proof (Appendix~\ref{app:proofs}) yields three sharp economic takeaways.", r"The proof (Supplement Section~\ref{S-app:proofs}) yields three economic consequences."),
    ]:
        t = rep(t, old, new)
    # 5. References from the main text to labels that now live in the supplement
    gone = set()
    for k in ('f_instr', 'f_robust', 'f_tags', 'f_proofs'):
        gone |= _labels(moved[k])
    gone -= _labels(t)
    for lab in sorted(gone, key=len, reverse=True):
        e = re.escape(lab)
        t = re.sub(r"(?<!Supplement )(Theorems?|Propositions?|Corollary|Corollaries|Lemma|Section)~\\ref\{" + e + r"\}",
                   r"Supplement \1~\\ref{S-" + lab.replace('\\', '\\\\') + "}", t)
        t = t.replace(r"\ref{" + lab + "}", r"\ref{S-" + lab + "}").replace(r"\eqref{" + lab + "}", r"\eqref{S-" + lab + "}")
    moved['f_gone'] = gone
    return t


def _to_supp(block, main_labels):
    def fix(mo):
        cmd, lab = mo.group(1), mo.group(2)
        if lab.startswith('S-'):
            return '\\' + cmd + '{' + lab[2:] + '}'
        if lab in main_labels:
            return '\\' + cmd + '{M-' + lab + '}'
        return mo.group(0)
    block = re.sub(r'\\(ref|eqref)\{([^}]+)\}', fix, block)
    block = re.sub(r"Supplement (Sections?|Propositions?|Theorems?|Tables?|Lemma|Corollary|Figure)~\\ref\{", r"\1~\\ref{", block)
    block = re.sub(r"(?<!Main )Appendix~\\ref\{M-app:proofs\}", r"Main Appendix~\\ref{M-app:proofs}", block)
    block = re.sub(r"equation~\\eqref\{M-", r"main-text equation~\\eqref{M-", block)
    block = re.sub(r"(?<!equation~)(?<!main-text~)\\eqref\{M-", r"main-text~\\eqref{M-", block)
    block = block.replace("System~main-text~\\eqref{M-", "The main-text system~\\eqref{M-")
    return block


def supplement(doc, moved, main_tex):
    main_labels = _labels(main_tex)
    doc = rep(doc, "\\begin{document}", "\\providecommand{\\TV}{\\mathrm{TV}}\\providecommand{\\Var}{\\mathrm{Var}}"
              "\\providecommand{\\supp}{\\mathrm{supp}}\n\\begin{document}")
    for lab in moved['f_gone']:
        doc = doc.replace('{M-' + lab + '}', '{' + lab + '}')
    note = r"\noindent The next results were moved from the main text (Section~\ref{M-sec:supervision})."
    instr = _to_supp(moved['f_instr'], main_labels)
    head = r"\section{Derived incidence of price and quantity instruments}\label{app:instruments}" + "\n"
    doc = rep(doc, head, head + "\n" + note + "\n\n" + instr + "\n\n")
    tags = _to_supp(moved['f_robust'] + "\n" + moved['f_tags'], main_labels)
    head = r"\section{The supervisory decision in detail}\label{app:decisionfull}" + "\n"
    doc = rep(doc, head, head + "\n" + note + "\n\n" + tags + "\n\n")
    # The supplement already proves Theorem 6.1 (Section app:incoming); drop the moved duplicate.
    fp = re.sub(r"\\begin\{proof\}\[Proof of Theorem~\\ref\{n:dual\}\].*?\\end\{proof\}\n?", "", moved['f_proofs'], flags=re.S)
    assert fp != moved['f_proofs']
    proofs = _to_supp(fp, main_labels)
    head = r"\section{Proofs of the main results}\label{app:proofs}" + "\n"
    doc = rep(doc, head, head + "\n" + r"\noindent The proofs of main-text results other than Theorems~\ref{M-n:suff}, "
              r"\ref{M-thm:what-id}, \ref{M-n:passiveupper}, \ref{M-n:separation} and~\ref{M-n:pilot}, which Main "
              r"Appendix~\ref{M-app:proofs} proves, are given first." + "\n\n" + proofs + "\n\n")
    # A section nothing cites: the notation table (the market-noise check, Table S1, is kept as evidence).
    for start in (r"\section{Notation}\label{app:notation}",):
        a = doc.index(start)
        b = doc.find(r"\section", a + 10)
        if b < 0:
            b = doc.index(r"\begin{thebibliography}", a)
        doc = doc[:a] + doc[b:]
    # Result-to-declaration table: kept in the replication archive; the section keeps its opening paragraph.
    v = doc.index(r"\section{Machine-checked declarations}\label{app:verification}")
    e = doc.find(r"\section", v + 10)
    sec = doc[v:e]
    lt = sec.index(r"\begin{longtable}")
    end_lt = sec.index(r"\end{longtable}") + len(r"\end{longtable}")
    from pathlib import Path
    Path(__file__).with_name('lean_mapping_table.tex').write_text(sec[lt:end_lt] + "\n")
    sec = sec[:lt] + (r"The full table, mapping each earlier result to the Lean~4 declarations that check it and to what is proved "
                      r"only on paper, is in the replication archive (\nolinkurl{ceiling_suite/papers/paper1_jedc_short/"
                      r"lean_mapping_table.tex}); Table~\ref{tab:newlean} covers the results added in this revision.") + sec[end_lt:]
    doc = doc[:v] + sec + doc[e:]
    return doc
