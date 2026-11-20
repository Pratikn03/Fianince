"""Make the base of the canonical Paper 1 revision (20 November 2026).

Applies the 15 November SSRN blocks (base_ssrn_parts_20261115.tex, the version the referee report reviewed) to the
current ceiling_suite/papers/paper1_note/paper1_focus.tex (built by build_note.py, which carries the 18 November
equilibrium section), and writes source/ceiling_suite/papers/paper1_note/paper1_ssrn.tex. build_revision.py then
applies the scoped revision and integrate_incoming.py the later 15 November results."""
import re
from pathlib import Path
HERE = Path(__file__).resolve().parent
NOTE = HERE.parents[1] / "ceiling_suite/papers/paper1_note"
src = (NOTE / "paper1_focus.tex").read_text(encoding="utf-8")
parts = dict(re.findall(r"%%BEGIN (\w+)\n(.*?)\n%%END \1", (HERE / "base_ssrn_parts_20261115.tex").read_text(encoding="utf-8"), flags=re.S))

def rep(text, old, new):
    assert text.count(old) == 1, ("anchor not unique or missing", old[:80], text.count(old))
    return text.replace(old, new)

t = src
a = t.index("\\begin{abstract}\n") + len("\\begin{abstract}\n"); b = t.index("\\end{abstract}")
t = t[:a] + parts["abstract"] + "\n" + t[b:]
a = t.index("\\paragraph{The answer.}"); b = t.index("\\paragraph{What is known.}")
t = t[:a] + parts["intro"] + "\n\n" + t[b:]
if "this note answers:" in t: t = rep(t, "Behind these choices is a question this note answers:", "Behind these choices is a question this paper answers:")
t = rep(t, "\\citep{sussmann1992}. We do not claim these.", "\\citep{sussmann1992}." + parts["known_add"] + " We do not claim these.")
t = rep(t, "With position limits, calm prices carry exactly no information about how close traders are to their limits.\n",
        "With position limits, calm prices carry exactly no information about how close traders are to their limits." + parts["new_add"] + "\n")
t = rep(t, "\\section{Who needs composition, and what disclosure buys}\\label{n:sup}",
        parts["univ"] + "\n\n" + parts["irr"] + "\n\n\\section{Who needs composition, and what disclosure buys}\\label{n:sup}")
t = rep(t, parts["scope_old"], parts["scope_new"])
ev_old = t[t.index("\\paragraph{Evidence.} The contribution is theoretical"):t.index("The sufficiency results hold whenever")]
t = rep(t, ev_old, parts["evidence"] + "\n\n")
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
(HERE / "source/ceiling_suite/papers/paper1_note/paper1_ssrn.tex").write_text(t, encoding="utf-8")
print("written paper1_ssrn.tex", len(t.splitlines()), "lines; abstract words:", len(re.sub(r"\$[^$]*\$", "x", parts["abstract"]).split()))
