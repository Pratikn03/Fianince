"""Builds paper1_ssrn.tex, the SSRN version (15 November 2026), from paper1_focus.tex (run build_note.py first) and the
blocks in ssrn_parts.tex. Adds Theorems n:univ and n:shape (the cost of composition for any smooth family and any memory shape),
Section n:irr_sec (detection equals forecast loss; forecast irrelevance), a rewritten abstract and introduction, and the supplement section with proofs.
Compile paper1_ssrn.tex three times (after paper1b_companion.aux exists); split with
python3 split_note.py paper1_ssrn.pdf Paper1_ssrn_main.pdf Paper1_ssrn_supplement.pdf"""
import re
src = open("paper1_focus.tex", encoding="utf-8").read()
parts = dict(re.findall(r"%%BEGIN (\w+)\n(.*?)\n%%END \1", open("ssrn_parts.tex", encoding="utf-8").read(), flags=re.S))

def rep(text, old, new):
    assert text.count(old) == 1, ("anchor not unique or missing", old[:80], text.count(old))
    return text.replace(old, new)

t = src
a = t.index("\\begin{abstract}\n") + len("\\begin{abstract}\n"); b = t.index("\\end{abstract}")
t = t[:a] + parts["abstract"] + "\n" + t[b:]
a = t.index("\\paragraph{The answer.}"); b = t.index("\\paragraph{What is known.}")
t = t[:a] + parts["intro"] + "\n\n" + t[b:]
t = rep(t, "Behind these choices is a question this note answers:", "Behind these choices is a question this paper answers:")
t = rep(t, "\\citep{sussmann1992}. We do not claim these.", "\\citep{sussmann1992}." + parts["known_add"] + " We do not claim these.")
t = rep(t, "With position limits, calm prices carry exactly no information about how close traders are to their limits.\n",
        "With position limits, calm prices carry exactly no information about how close traders are to their limits." + parts["new_add"] + "\n")
t = rep(t, "\\section{Who needs composition, and what disclosure buys}\\label{n:sup}",
        parts["univ"] + "\n\n" + parts["irr"] + "\n\n\\section{Who needs composition, and what disclosure buys}\\label{n:sup}")
t = rep(t, parts["scope_old"], parts["scope_new"])
ev_old = t[t.index("\\paragraph{Evidence.} The contribution is theoretical"):t.index("The sufficiency results hold whenever")]
t = rep(t, ev_old, parts["evidence"] + "\n\n")
t = rep(t, "The authors have verified all mathematical proofs, Lean~4 formalizations and empirical calculations, and take full responsibility for the content of the manuscript.",
        "The authors have verified the mathematical proofs, Lean~4 formalizations and empirical calculations of the results carried over from the version of 13 November 2026, and take full responsibility for the content of the manuscript. "
        "The proofs of Theorems~\\ref{n:univ}, \\ref{n:shape}, \\ref{n:dual} and~\\ref{n:irr} and Proposition~\\ref{n:exc}, new in this version, are being checked by the authors.")
t = rep(t, "\\date{13 November 2026}", "\\date{15 November 2026}")
t = rep(t, "\\section{Machine checks in detail}\\label{app:mc}", parts["supp"] + "\n\n\\section{Machine checks in detail}\\label{app:mc}")
i = t.index("\\end{thebibliography}")
t = t[:i] + parts["bib"] + "\n" + t[i:]
# bibliography: every cited key present
body = t[:t.index("\\begin{thebibliography}")] + t[t.index("\\end{thebibliography}"):]
cited = set(k.strip() for g in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", body) for k in g.split(","))
have = set(re.findall(r"\\bibitem\[[^\]]*\]\{([^}]*)\}", t))
assert not (cited - have), cited - have
assert "Taiwan" not in parts["abstract"] + parts["intro"]
open("paper1_ssrn.tex", "w", encoding="utf-8").write(t)
print("written paper1_ssrn.tex", len(t.splitlines()), "lines; abstract words:", len(re.sub(r"\$[^$]*\$", "x", parts["abstract"]).split()))
