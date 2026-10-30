"""Turn the two working papers into thesis chapters.

Reads the assembled working versions of Paper 1 and Paper 2 from the repository, keeps every section,
table, figure, proof and appendix, and rewrites only what a thesis chapter needs:
labels and citation keys get a chapter prefix (p1:, p2:), references to the companion paper become
references to the other chapter, figure paths point to per-chapter folders, the paper's appendices
become sections at the end of the chapter, and its reference list becomes a section of the chapter.
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "ceiling_suite", "papers")

REF_CMDS = r"(label|ref|eqref|pageref|autoref|cref|Cref|nameref)"


def prefix_refs(tex, p):
    def fix(m):
        keys = ",".join(k.strip() if k.strip().startswith(("ch:", "app:status")) else p + k.strip() for k in m.group(2).split(","))
        return "\\" + m.group(1) + "{" + keys + "}"
    return re.sub(r"\\" + REF_CMDS + r"\{([^}]*)\}", fix, tex)


def prefix_cites(tex, p):
    def fix(m):
        keys = ",".join(p + k.strip() for k in m.group(3).split(","))
        return "\\" + m.group(1) + (m.group(2) or "") + "{" + keys + "}"
    tex = re.sub(r"\\(cite[a-zA-Z]*)((?:\[[^\]]*\])*)\{([^}]*)\}", fix, tex)
    tex = re.sub(r"\\bibitem(\[[^\]]*\])\{([^}]*)\}", lambda m: "\\bibitem" + m.group(1) + "{" + p + m.group(2) + "}", tex)
    return tex


def chapterize(src, prefix, chap_label, title, preface, figdir, companion_key, other_label, replacements):
    s = open(src).read()
    # The thesis carries one common development appendix, not duplicate paper notes.
    s = re.sub(r"% BEGIN ECONOMIC REVIEW 20261029.*?% END ECONOMIC REVIEW 20261029", "", s, flags=re.S)
    s = re.sub(r"% BEGIN INFORMATION DECISION REVISION 20261029.*?% END INFORMATION DECISION REVISION 20261029", "", s, flags=re.S)
    s = re.sub(r"% BEGIN FINITE HORIZON COST 20261029.*?% END FINITE HORIZON COST 20261029", "", s, flags=re.S)
    s = re.sub(r"% BEGIN ADVANCED RETURN STATUS 20261030.*?% END ADVANCED RETURN STATUS 20261030", "", s, flags=re.S)
    body = s[s.index("\\begin{document}") + len("\\begin{document}"):s.rindex("\\end{document}")]
    abstract = body[body.index("\\begin{abstract}") + len("\\begin{abstract}"):body.index("\\end{abstract}")]
    abstract = abstract.replace("\\noindent", "").strip()
    after_abs = body[body.index("\\end{abstract}") + len("\\end{abstract}"):body.index("\\section{Introduction}")]
    repro = ""
    m = re.search(r"\\paragraph\{Reproducibility\.\}(.*?)\n\n", after_abs, re.S)
    if m:
        repro = "\\paragraph{Reproducibility.}" + m.group(1).strip() + "\n\n"
    main = body[body.index("\\section{Introduction}"):body.index("\\begin{thebibliography}")]
    bib = body[body.index("\\begin{thebibliography}"):body.index("\\end{thebibliography}") + len("\\end{thebibliography}")]
    app = body[body.index("\\appendix") + len("\\appendix"):]
    app = re.sub(r"\\section\{", r"\\section{Appendix: ", app)
    app = app.replace("\\section{Appendix: Internet appendix}", "\\section{Appendix: Further results}")
    app = app.replace("\\section{Appendix: Additional material}", "\\section{Appendix: Further results}")
    tex = main + "\n" + bib + "\n" + app
    # the other paper becomes the other chapter
    other = "Chapter~\\ref{" + other_label + "}"
    for a, b in replacements:
        tex = tex.replace(a, b)
    tex = tex.replace("\\citealp{" + companion_key + "}", other)
    # a function replacement: in a string replacement re.sub would turn the "\\r" of "\\ref" into a carriage return
    tex = re.sub(r"\\citep\[([^\]]*)\]\{" + re.escape(companion_key) + r"\}", lambda m: "(" + other + ", " + m.group(1) + ")", tex)
    tex = tex.replace("\\citep{" + companion_key + "}", "(" + other + ")")
    tex = tex.replace("\\citet{" + companion_key + "}", other)
    tex = tex.replace("the companion paper's", other + "'s").replace("The companion paper's", other + "'s")
    tex = tex.replace("the companion paper", other).replace("The companion paper", other)
    tex = tex.replace("companion paper", other)
    tex = re.sub(r"\bThis paper\b", "This chapter", tex)
    tex = re.sub(r"\bthis paper\b", "this chapter", tex)
    tex = re.sub(r"\bthis paper's\b", "this chapter's", tex)
    # prefixes
    tex = prefix_refs(tex, prefix)
    tex = prefix_cites(tex, prefix)
    tex = tex.replace("{figs/", "{" + figdir + "/")
    abstract = prefix_cites(prefix_refs(abstract, prefix), prefix)
    # layout: long "map of results" tables become longtables; the forest plot is height-limited
    mm = re.search(r"\\begin\{table\}\[[a-z!]*\]\\centering\\(?:footnotesize|small)\n\\begin\{threeparttable\}\n\\caption\{Map of results\}(\\label\{[^}]*\})\n\\begin\{tabular\}\{([^\n]*)\}\n", tex)
    if mm:
        i0 = mm.start(); i1 = tex.index("\\end{tabular}", i0)
        j1 = tex.index("\\end{table}", i1) + len("\\end{table}")
        rows = tex[mm.end():i1]
        notes = ""
        nm = re.search(r"\\begin\{tablenotes\}(.*?)\\end\{tablenotes\}", tex[i1:j1], re.S)
        if nm:
            notes = "\\par\\noindent{\\footnotesize " + nm.group(1).replace("\\footnotesize", "").replace("\\item", "") + "}\n"
        tex = (tex[:i0] + "{\\footnotesize\\begin{longtable}{" + mm.group(2) + "}\n\\caption{Map of results}" + mm.group(1) + "\\\\\n" + rows
               + "\\end{longtable}}\n" + notes + tex[j1:])
    tex = tex.replace("\\includegraphics[width=0.78\\textwidth]{" + figdir + "/fig_forest.pdf}",
                      "\\includegraphics[height=0.6\\textheight,width=0.95\\textwidth,keepaspectratio]{" + figdir + "/fig_forest.pdf}")
    head = ("\\chapter{" + title + "}\\label{" + chap_label + "}\n\n" + preface + "\n\n"
            "\\begin{quote}\\small\\textbf{Summary.} " + abstract + "\\end{quote}\n\n" + prefix_refs(repro, prefix))
    return head + tex


P1_EMPIRICS = r"""\section{Empirical feedback and its measurement}\label{p1:sec:empirics}

The theory says what prices can reveal. The empirical work has two roles, and neither is a test of the identification bounds themselves, which concern controlled experiments no outside researcher can run. Section~\ref{p1:sec:disc_data} tests the theory's policy prediction, that class-tagged data pin down memories that prices leave unrestricted. This section asks what the reduced-form feedback indices a supervisor would compute from public data actually measure; the full tables are in the published version of the paper.

Empirical work replaces the unobserved fundamental by a trailing exponential moving average. Under a martingale price the filtered state $x^{\rm EMA}$ is then an AR(1) with mechanical persistence $1-\alpha$, equal to $29/31\approx0.9355$ for a 300-second filter on ten-second bars, so measured persistence must be compared with that value, not with zero. With a VAR(1) in $(x^{\rm EMA},f)$, $f$ the signed flow, the loop gain is $\hat Q=\hat J_{12}\hat J_{21}/(1-\hat J_{22})$. Five findings follow, on a Binance spot panel of eight pairs on 96 dates in 2021--2024 (6.6 million ten-second transitions), on 72 days of one-second BTCUSDT data and on the 30 perpetuals of Chapter~\ref{ch:p2}. First, timing dominates: pairing the state with next-bar flow, a look-ahead, gives $\hat Q=0.0081$; aligning flow with the bar in which it is observed lowers it by more than an order of magnitude, to $0.00037$; raw returns give an interval that includes zero; and a placebo random walk reproduces the mechanical persistence ($0.9351$) with $\hat Q$ indistinguishable from zero. Second, feedback that the filter cannot produce is detectable but small: in BTCUSDT $\hat Q=0.0045$ [$0.0034$, $0.0056$] against a placebo of zero, while price persistence ($0.9364$) is almost entirely mechanical. Third, order splitting biases lagged-flow regressions (in simulation OLS never covers the truth, while Cochrane--Orcutt with the true autocorrelation, 2SLS and LIML have correct size), although at ten-second bars the residual serial correlation is negligible and controlling for 30 lags of flow lowers $\hat Q$ further. Fourth, measured feedback rises with depth across the 30 perpetuals (Spearman correlation with log depth $+0.70$). Fifth, when Binance set BTC spot fees to zero and later reinstated them, BTCUSDT volume rose by a factor of $2.6$ and then fell by a factor of $4.9$ relative to seven control pairs, while $\hat Q$ did not move (pooled effect $-0.00016$, interval $[-0.00087,0.00055]$). Measured feedback in crypto markets is real but small, is a feature of deep books, does not track trading activity, and is easily confused with filtering and timing artefacts.

"""


def condense_ch2(tex):
    """Paper 1 enters the thesis whole except its section on reduced-form feedback indices, condensed to one page."""
    a = tex.index("\\section{Empirical feedback and its measurement}\\label{p1:sec:empirics}")
    b = tex.index("\\section{Implications for supervision and market design}")
    tex = tex[:a] + P1_EMPIRICS + tex[b:]
    for old in ("Tables~\\ref{p1:tab:panel}, \\ref{p1:tab:feedback}", "Table~\\ref{p1:tab:fee2}",
                "Tables~\\ref{p1:tab:panel}, \\ref{p1:tab:assets}, \\ref{p1:tab:fee2}", "(Table~\\ref{p1:tab:feedback})",
                "(Table~\\ref{p1:tab:iv})"):
        assert old in tex, old
        tex = tex.replace(old, "(Section~\\ref{p1:sec:empirics})" if old.startswith("(") else "Section~\\ref{p1:sec:empirics}")
    return tex


def main():
    for d, sub in (("p1figs", "paper1"), ("p2figs", "paper2")):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
        for f in os.listdir(os.path.join(REPO, sub, "figs")):
            shutil.copy(os.path.join(REPO, sub, "figs", f), os.path.join(HERE, d, f))
    pre1 = ("This chapter, the first paper of the thesis, reproduces the paper \\emph{Auditable Memory and Financial Identification Limits in Electronic Limit Order Books}, "
            "joint with Prashant Niroula. It establishes the identification half of the thesis: what prices reveal about the agents of a closed-loop market, "
            "and what it costs to learn more. Its notation is its own; Appendix~\\ref{app:status} maps it to the notation of Chapter~\\ref{ch:p3}.")
    pre2 = ("This chapter, the second paper of the thesis, reproduces the paper \\emph{From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard}, "
            "joint with Suboh Alkhushayni, Yuhao Chen, Mansi Bhavsar and Prashant Niroula. It establishes the safety half of the thesis: "
            "what certifies a safe trading decision when the agents cannot be identified, and what that certificate costs.")
    rep1 = [("which the companion paper analyses \\citep{niroula2026b}", "which Chapter~\\ref{ch:p2} analyses"),
            ("a decision value of disclosure \\citep{niroula2026b}", "a decision value of disclosure (Chapter~\\ref{ch:p2})")]
    rep2 = [("which the companion paper \\citep{niroula2026} shows", "which Chapter~\\ref{ch:p1} shows"),
            ("as the companion paper shows \\citep{niroula2026}", "as Chapter~\\ref{ch:p1} shows")]
    ch3 = chapterize(os.path.join(REPO, "paper1", "paper1.tex"), "p1:", "ch:p1",
                     "Auditable memory and identification limits", pre1, "p1figs", "niroula2026b", "ch:p2", rep1)
    ch4 = chapterize(os.path.join(REPO, "paper2", "paper2.tex"), "p2:", "ch:p2",
                     "Safety without identification: transient amplification and a maximal pre-trade guard", pre2, "p2figs", "niroula2026", "ch:p1", rep2)
    open(os.path.join(HERE, "ch2_paper1.tex"), "w").write(condense_ch2(ch3).rstrip() + "\n")
    # Paper 2 enters the thesis condensed: the full chapter is kept (not compiled) and condense_ch3.py builds
    # ch3_paper2.tex from it, copying theorems, proofs and tables verbatim and replacing the rest by shorter text.
    open(os.path.join(HERE, "ch3_paper2_full.tex"), "w").write(ch4.rstrip() + "\n")
    import condense_ch3
    condense_ch3.main(HERE)
    for name, t in (("paper1", ch3), ("paper2", ch4)):
        left = re.findall(r"niroula2026b?|companion", t)
        print(name, len(t) // 1000, "k chars; leftover companion refs:", len(left))


if __name__ == "__main__":
    main()
