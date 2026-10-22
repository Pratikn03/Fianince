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
    tex = re.sub(r"\\citep\[([^\]]*)\]\{" + re.escape(companion_key) + r"\}", "(" + other + ", \\1)", tex)
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


def main():
    for d, sub in (("ch3figs", "paper1"), ("ch4figs", "paper2")):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
        for f in os.listdir(os.path.join(REPO, sub, "figs")):
            shutil.copy(os.path.join(REPO, sub, "figs", f), os.path.join(HERE, d, f))
    pre1 = ("This chapter reproduces the paper \\emph{Auditable Memory and Financial Identification Limits in Electronic Limit Order Books}, "
            "joint with Prashant Niroula. It establishes the identification half of the thesis: what prices reveal about the agents of a closed-loop market, "
            "and what it costs to learn more. Its notation is its own; Appendix~\\ref{app:status} maps it to the notation of Chapter~\\ref{ch:framework}.")
    pre2 = ("This chapter reproduces the paper \\emph{From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard}, "
            "joint with Suboh Alkhushayni, Yuhao Chen, Mansi Bhavsar and Prashant Niroula. It establishes the safety half of the thesis: "
            "what certifies a safe trading decision when the agents cannot be identified, and what that certificate costs.")
    rep1 = [("which the companion paper analyses \\citep{niroula2026b}", "which Chapter~\\ref{ch:p2} analyses"),
            ("a decision value of disclosure \\citep{niroula2026b}", "a decision value of disclosure (Chapter~\\ref{ch:p2})")]
    rep2 = [("which the companion paper \\citep{niroula2026} shows", "which Chapter~\\ref{ch:p1} shows"),
            ("as the companion paper shows \\citep{niroula2026}", "as Chapter~\\ref{ch:p1} shows")]
    ch3 = chapterize(os.path.join(REPO, "paper1", "paper1.tex"), "p1:", "ch:p1",
                     "Auditable memory and identification limits", pre1, "ch3figs", "niroula2026b", "ch:p2", rep1)
    ch4 = chapterize(os.path.join(REPO, "paper2", "paper2.tex"), "p2:", "ch:p2",
                     "Safety without identification: transient amplification and a maximal pre-trade guard", pre2, "ch4figs", "niroula2026", "ch:p1", rep2)
    open(os.path.join(HERE, "ch3_paper1.tex"), "w").write(ch3)
    open(os.path.join(HERE, "ch4_paper2.tex"), "w").write(ch4)
    for name, t in (("ch3", ch3), ("ch4", ch4)):
        left = re.findall(r"niroula2026b?|companion", t)
        print(name, len(t) // 1000, "k chars; leftover companion refs:", len(left))


if __name__ == "__main__":
    main()
