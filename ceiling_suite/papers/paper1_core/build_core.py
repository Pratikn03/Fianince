"""Assembles the core version of Paper 1 (paper1_core.tex) from the SSRN source of the full working paper.

Theorem statements and proofs are copied verbatim by line range from ../paper1/paper1_ssrn.tex; the new framing text
lives in src/. Run from this folder: python3 build_core.py && pdflatex paper1_core.tex (x3).
Line ranges are checked against the first characters of each block, so a change in the source stops the build.
"""
import re

SRC = open("src/ssrn_source_20261108.tex", encoding="utf-8").read().split("\n")  # frozen SSRN source, 8 Nov 2026, before the Taiwan section


def L(a, b, starts=None):
    """Lines a..b (1-based, inclusive) of the SSRN source."""
    block = SRC[a - 1:b]
    if starts is not None:
        assert block[0].startswith(starts), (a, block[0][:60])
    return "\n".join(block) + "\n"


def F(name):
    return open(f"src/{name}.tex", encoding="utf-8").read() + "\n"


def para(start, label_like):
    """A one-line \\paragraph proof in the SSRN proofs section, found by its header."""
    for i, line in enumerate(SRC):
        if line.startswith(start) and label_like in line[:120]:
            j = i + 1
            while j < len(SRC) and not SRC[j].startswith("\\paragraph") and not SRC[j].startswith("\\section"):
                j += 1
            return "\n".join(SRC[i:j]) + "\n"
    raise KeyError(label_like)


preamble = L(1, 33, "\\documentclass").replace("What Prices Cannot Tell a Supervisor", "A Sufficient Statistic for Algorithmic Feedback")

main = []
main.append(preamble)
main.append(F("front"))
main.append(F("intro"))
# Section 2: model (verbatim), new tail
main.append(L(150, 188, "\\section{Model"))
main.append(F("model_tail"))
# Section 3: sufficiency
main.append(F("suff_head"))
main.append(L(401, 418, "\\begin{theorem}[Equilibrium invariance]"))
main.append(F("suff_mid"))
main.append(L(227, 246, "\\begin{theorem}[Merged rate"))
main.append(L(248, 250, "\\begin{remark}[Scope]"))
# Section 4: equilibrium
main.append(F("eq_head"))
main.append(L(277, 309, "\\paragraph{An inventory equilibrium.}"))
main.append("\\paragraph{Machine check.} See Supplement~\\ref{app:mc}.\n\n")
main.append(L(318, 350, "\\paragraph{The identification results hold in equilibrium.}"))
main.append(F("eq_tail"))
# Section 5: the price of composition
main.append(F("cost_head"))
main.append(L(518, 533, "\\subsection{Many unknown cohorts}"))
main.append(L(542, 548, "\\begin{theorem}[Matching upper bound"))
main.append(L(554, 555, "\\paragraph{In words.}"))
main.append(L(587, 596, "\\subsection{Passive data}"))
main.append(L(598, 610))
main.append(L(612, 613))
main.append("\\paragraph{Machine checks.} The machine checks of Theorems~\\ref{thm:kcohort}--\\ref{prop:passive} are described in Supplement~\\ref{app:mc}.\n\n")
main.append(F("cost_tail"))
# Section 6: supervision and disclosure
main.append(F("sup_head"))
main.append(L(714, 727, "\\begin{proposition}[Supervisory separation"))
main.append(F("sup_mid"))
main.append(L(657, 672, "\\begin{proposition}[Tagged flow"))
main.append(L(676, 684, "Proposition~\\ref{prop:tagged} says"))
main.append(L(690, 693, "\\paragraph{In words.} This is the value"))
main.append(F("sup_tail"))
# Sections 7-8
main.append(F("sat"))
main.append(F("scope"))
main.append(F("conclusion"))
main.append(F("declarations"))
BIB_AT = len("".join(main))

supp = []
supp.append(F("supp_front"))
supp.append("\\section{Proofs of the main results}\\label{app:proofs}\n\n")
supp.append("\\paragraph{A lemma used in the proofs.}\n" + L(198, 204, "\\begin{lemma}[Positive price-response geometry]") + "\n")
supp.append(para("\\paragraph{Lemma", "lem:cm") + "\n")
for start, lab in [("\\paragraph{Lemma", "lem:micro"), ("\\paragraph{Theorem", "thm:merged"),
                   ("\\paragraph{Theorem", "thm:kcohort"), ("\\paragraph{Theorem", "prop:passive"),
                   ("\\paragraph{Theorem", "thm:minphase"), ("\\paragraph{Proposition", "prop:tagged")]:
    supp.append(para(start, lab) + "\n")
supp.append("\\paragraph{Theorem~\\ref{prop:esprit}.}\n" + L(550, 552, "\\begin{proof}"))
supp.append("\\paragraph{Theorem~\\ref{thm:discvalue}.}\n" + L(686, 688, "\\begin{proof}"))
supp.append("\n\\paragraph{Unknown primitives.}\n" + L(558, 576, "\\begin{corollary}[Unknown primitives"))
supp.append("\\paragraph{Proposition~\\ref{prop:anylinear}.} The proof is given after the statement in the main text.\n\n")
# S2: further equilibrium results, statements then the proofs block of the SSRN supplement
supp.append("\\section{Equilibrium: further results and proofs}\\label{app:eqinv}\n\n")
supp.append(L(352, 360, "\\begin{corollary}[Disclosure in equilibrium]"))
supp.append(L(362, 397, "\\begin{theorem}[Fragility"))
supp.append(L(420, 458, "\\begin{theorem}[A strategic insider"))
supp.append(L(2350, 2708, "\\paragraph{A misjudged dealer and a targeted halt.}"))
# S3: execution cost and capital (quantity theorem first)
supp.append("\\section{Execution cost and capital}\\label{app:capital}\n\n")
supp.append(L(472, 494, "\\begin{theorem}[Sharp probing-resource"))
supp.append(L(2203, 2261))
for start, lab in [("\\paragraph{Theorem", "thm:quantity"), ("\\paragraph{Lemma", "lem:toeplitz"),
                   ("\\paragraph{Theorem", "thm:cap"), ("\\paragraph{Proposition", "prop:disclosure"),
                   ("\\paragraph{Lemma", "thm:capital")]:
    supp.append(para(start, lab) + "\n")
# two unknown cohorts (used by Theorem prop:passive(ii))
supp.append(L(2262, 2324, "\\section{Two unknown cohorts"))
# S4: supervisory decision in detail
supp.append(L(2709, 2772, "\\section{The supervisory decision in detail}"))
supp.append(L(2776, 2786, "\\begin{proposition}[No-data action"))
supp.append(F("supp_everyK"))
supp.append(F("supp_nearcrit"))
supp.append(F("supp_noisystress"))
supp.append(F("supp_sat"))
# Results restored from the full working paper (12 November 2026), verbatim by line range, with their proofs.
supp.append(L(1936, 2005, "\\section{General memory: the minimax rate is logarithmic}"))
supp.append("\\paragraph{Full proofs.}\n\n")
for start, lab in [("\\paragraph{Lemma", "lem:altpair"), ("\\paragraph{Theorem", "thm:general")]:
    supp.append(para(start, lab) + "\n")
supp.append(L(1624, 1643, "\\section{Near-colliding rates"))
supp.append(L(1700, 1717, "\\section{A spectral blind spot}"))
supp.append("\\paragraph{Proof of Theorem~\\ref{thm:blind}.}\n" + para("\\paragraph{Theorem", "thm:blind").split("}", 2)[-1] + "\n")
supp.append(L(1265, 1310, "\\section{What prices hide, in economic terms}"))
supp.append(L(1311, 1349, "\\section{Local information: the Cram"))
supp.append("\\paragraph{Proof of Proposition~\\ref{prop:crb}.}\n" + para("\\paragraph{Proposition", "prop:crb").split("}", 2)[-1] + "\n")
supp.append("\\section{Pricing, evasion and the choice of an audit trail}\\label{app:restored_policy}\n\n")
supp.append(L(252, 264, "\\begin{proposition}[Conditional endogenous-pricing invariance]"))
supp.append("\\paragraph{Proof of Proposition~\\ref{prop:endogenous_kappa}.}\n" + para("\\paragraph{Proposition", "prop:endogenous_kappa").split("}", 2)[-1] + "\n")
supp.append(L(695, 705, "\\begin{proposition}[Conditional limits of three evasion arguments]"))
supp.append("\\paragraph{Proof of Proposition~\\ref{prop:strategic}.}\n" + para("\\paragraph{Proposition", "prop:strategic").split("}", 2)[-1] + "\n")
supp.append(L(2335, 2347))
supp.append("\\paragraph{Proof of Proposition~\\ref{prop:choice}.}\n" + para("\\paragraph{Proposition", "prop:choice").split("}", 2)[-1] + "\n")
supp.append("\\section{Finite-sample surveillance bounds}\\label{app:restored_finite}\n\n")
supp.append(L(1015, 1045, "\\subsection{A finite-window price-surveillance bound}"))
supp.append(L(1389, 1623, "\\section{Account-level capital}"))
supp.append("\\paragraph{Proofs.}\n\n")
for start, lab in [("\\paragraph{Proposition", "prop:tri"), ("\\paragraph{Theorems", "thm:spectral"),
                   ("\\paragraph{Theorem", "thm:rh"), ("\\paragraph{Corollary", "cor:garch")]:
    supp.append(para(start, lab) + "\n")
supp.append(L(1350, 1388, "\\section{A hypothetical scale illustration"))
supp.append(L(1644, 1699, "\\section{Robustness to nonlinear and adaptive trading rules}"))
supp.append(L(1904, 1935, "\\section{A worked example: two Kalman desks}"))
supp.append("\\section{Machine checks in detail}\\label{app:mc}\n\n")
supp.append("\\paragraph{Theorem~\\ref{thm:inventory}.}\n" + L(310, 316, "\\paragraph{Machine check.}").replace("\\paragraph{Machine check.} ", "", 1))
supp.append("\\paragraph{Theorem~\\ref{thm:kcohort}.}\n" + L(534, 534, "\\paragraph{Machine check.}").replace("\\paragraph{Machine check.} ", "", 1) + "\n")
supp.append("\\paragraph{Theorem~\\ref{prop:esprit}.}\n" + L(556, 556, "\\paragraph{Machine check.}").replace("\\paragraph{Machine check.} ", "", 1) + "\n")
supp.append("\\paragraph{Theorem~\\ref{thm:minphase}.}\n" + L(597, 597, "\\paragraph{Machine check.}").replace("\\paragraph{Machine check.} ", "", 1) + "\n")
supp.append("\\paragraph{Theorem~\\ref{prop:passive}.}\n" + L(611, 611, "\\paragraph{Machine check.}").replace("\\paragraph{Machine check.} ", "", 1) + "\n")
supp.append(F("supp_verification"))
supp.append(L(984, 1012, "\\section{Notation}"))

body = "".join(main) + "%%BIB%%\n" + "".join(supp) + "\\end{document}\n"

# bibliography: SSRN entries plus the new ones, pruned to cited keys
bib_old = L(779, 877, "\\begin{thebibliography}")
items = re.findall(r"(\\bibitem\[.*?\]\{(.*?)\}.*?)(?=\n\\bibitem|\n\\end\{thebibliography\})", bib_old, re.S)
new = open("src/bib_new.tex", encoding="utf-8").read()
items += re.findall(r"(\\bibitem\[.*?\]\{(.*?)\}.*?)(?=\n\\bibitem|\Z)", new.strip(), re.S)
cited = set()
for m in re.finditer(r"\\cite(?:t|p|alp|alt|author|year)?\*?(?:\[[^\]]*\])*\{([^}]*)\}", body):
    cited |= {k.strip() for k in m.group(1).split(",")}
keep = sorted([(k, t) for t, k in items if k in cited], key=lambda kt: re.sub(r"[^a-z]", "", kt[1].split("]")[0].lower()))
missing = cited - {k for k, _ in keep}
assert not missing, f"cited but no bibitem: {missing}"
bib = "\\begin{thebibliography}{99}\\setlength{\\itemsep}{2pt}\\small\n" + "\n".join(t.strip() for _, t in keep) + "\n\\end{thebibliography}\n"
body = body.replace("%%BIB%%\n", bib)

# cross-reference cleanups for material not carried over (applied to the whole file; each must match)
FIX = [x for x in open("src/fixes.txt", encoding="utf-8").read().split("\n====\n") if x.strip()]
for f in FIX:
    old, new_ = f.split("\n----\n")
    old, new_ = old.strip("\n"), new_.strip("\n")
    n = body.count(old)
    assert n >= 1, f"fix not found: {old[:80]}"
    body = body.replace(old, "" if new_ == "<DELETE>" else new_)

# terminology: this version says "group" throughout; the copied text says "cohort". Labels, file names, Lean names,
# citations and the bibliography are left alone.
PROTECT = re.compile(r"\\(?:label|ref|eqref|texttt|nolinkurl|url|includegraphics|bibitem|cite[a-z]*\*?)(?:\[[^\]]*\])*\{[^{}]*\}")
def _swap(seg):
    seg = re.sub(r"\bCohort(s?)\b", r"Group\1", seg)
    return re.sub(r"\bcohort(s?)\b", r"group\1", seg)
_head, _bibpart, _tail = body.partition("\\begin{thebibliography}")
_bib, _endb, _rest = _tail.partition("\\end{thebibliography}")
def _unify(text):
    out, pos = [], 0
    for m in PROTECT.finditer(text):
        out.append(_swap(text[pos:m.start()])); out.append(m.group(0)); pos = m.end()
    out.append(_swap(text[pos:]))
    return "".join(out)
body = _unify(_head) + _bibpart + _bib + _endb + _unify(_rest)

open("paper1_core.tex", "w", encoding="utf-8").write(body)
print("written paper1_core.tex,", len(body.split("\n")), "lines;", len(keep), "references")
