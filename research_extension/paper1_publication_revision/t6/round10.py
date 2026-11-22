"""Tenth round: the P1M-A1 results in the Taiwan section (protocol ceiling_suite/p1_empirics/P1M_A1_protocol.md,
section 5). The passages are the protocol's templates, filled mechanically from the result files. Part A replaces the
sentence saying that the sign-restricted range was not computed; part B adds the decoupled estimate after the second
qualification. Each part is applied only once its result file exists. Written before either result existed.

The same functions fill the 31-page main text (ceiling_suite/papers/paper1_jedc_short/make_short.py)."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RES_A = ROOT / "ceiling_suite/p1_empirics/results/p1m_a1_partA_results.json"
RES_B = ROOT / "ceiling_suite/p1_empirics/results/p1m_a1_partB_results.json"
H_FOREIGN_TABLE = 0.0013716649609925174     # P1M primary estimate of H_Foreign (Table 3 / tab:barrier)

NOT_COMPUTED = (r"Weights restricted to one sign would exclude these compositions; we have not computed the range under "
                r"that restriction.")


def sig(x, d=2):
    """Two significant digits in LaTeX math (as in round6)."""
    if x is None or not math.isfinite(x):
        return r"$\infty$"
    if abs(x) < 1e-10:          # numerical zero (an effect is of order 1e-3; a weight on its bound gives exactly 0)
        return "$0$"
    e = int(math.floor(math.log10(abs(x))))
    if -3 <= e <= 4:
        dec = max(d - 1 - e, 0)
        return f"${x:,.{dec}f}$".replace(",", "{,}")
    m = x / 10 ** e
    m = float(f"{m:.{d - 1}f}")
    if abs(m) >= 10:
        m /= 10
        e += 1
    return f"${m:g}\\times10^{{{e}}}$"


def _cell(RA, variant, gamma, box="primary", record="panel"):
    return RA["configs"][f"{variant}_g{gamma:.2f}_{box}_{record}"]


def _range(c):
    return None if c["empty"] else (c["H_Foreign"]["min"], c["H_Foreign"]["max"])


def _phrase(c, lead="from"):
    if c["empty"]:
        return "no composition in that class lies within the panel's reach"
    lo, hi = _range(c)
    return f"{lead} {sig(lo)} to {sig(hi)}"


def part_a_passage(RA):
    """Protocol section 5, part A: the passage and its conditional clauses (primary box, whole-panel record)."""
    P0, P5 = _cell(RA, "P", 0.0), _cell(RA, "P", 0.05)
    T0, T5 = _cell(RA, "T", 0.0), _cell(RA, "T", 0.05)
    if P0["empty"]:
        first = (r"On the class the lower bounds cover, with every weight nonnegative and memories in $[0, 0.99]$, no "
                 r"composition in that class lies within the panel's reach")
    else:
        first = (r"On the class the lower bounds cover, with every weight nonnegative and memories in $[0, 0.99]$, the "
                 r"compositions the panel cannot tell apart imply contributions " + _phrase(P0) +
                 r", against a uniform cut between " + sig(P0["U"]["min"]) + r" and " + sig(P0["U"]["max"]))
    s = first + r"; with memories at least $0.05$ apart, " + (
        "the range is " + _phrase(P5, lead="").strip() if not P5["empty"] else _phrase(P5)) + ". "
    t0 = (f"{sig(T0['H_Foreign']['min'])} to {sig(T0['H_Foreign']['max'])}" if not T0["empty"] else
          "a set in which no composition lies within the panel's reach")
    t5 = (f", and {sig(T5['H_Foreign']['min'])} to {sig(T5['H_Foreign']['max'])} at spacing $0.05$." if not T5["empty"]
          else r"; at spacing $0.05$, no composition in that class lies within the panel's reach.")
    s += r"Holding each class's weight to the sign of its tagged estimate gives " + t0 + t5
    clauses = []
    if not P0["empty"] and (P0["H_Foreign"]["max"] - P0["H_Foreign"]["min"]) >= 0.9 * P0["U"]["max"]:
        clauses.append("So even on that class, prices leave foreign feedback anywhere between none and nearly all of "
                       "the total.")
    if not T0["empty"] and T0["H_Foreign"]["max"] >= 0.99 * T0["hbar"]:
        clauses.append("Where weights of opposite sign may sit at equal memories, the cap again sets the range.")
    if not (P0["empty"] or P5["empty"]):
        w0 = P0["H_Foreign"]["max"] - P0["H_Foreign"]["min"]
        w5 = P5["H_Foreign"]["max"] - P5["H_Foreign"]["min"]
        if w5 < 0.5 * w0:
            clauses.append("Requiring the classes' memories to be apart narrows it, as the composition barrier predicts.")
    return s + ("" if not clauses else " " + " ".join(clauses))


def _box_label(box):
    if box == "primary":
        return r"$1-\sum_j\hat a_j$"
    if box == "tight":
        return r"$2\max_c|\hat H_c|$"
    return "$" + box.replace("xmaxH", "") + r"\max_c|\hat H_c|$"


def post_run_main(RA):
    """Added after the run (protocol section 6): the variant-P range does not narrow with the required spacing."""
    w = [_cell(RA, "P", g)["H_Foreign"]["max"] - _cell(RA, "P", g)["H_Foreign"]["min"] for g in (0.0, 0.01, 0.02, 0.05, 0.10)]
    if max(w) - min(w) <= 0.01 * max(w):
        return r" With every weight nonnegative, the reported search range is the same for memories up to $0.10$ apart."
    return ""


def post_run_supp(RA):
    """Added after the run (protocol section 6): under the tagged signs, the maximum is the cap in the box scan."""
    keys = [k for k in RA["configs"] if k.startswith("T_g") and "_x" in k]
    if keys and all(abs(RA["configs"][k]["H_Foreign"]["max"] - RA["configs"][k]["hbar"]) <= 0.01 * RA["configs"][k]["hbar"]
                    for k in keys):
        return (r" Under the tagged signs the maximum equals the cap at one, five and ten times the largest estimated "
                r"contribution, at spacing $0$ and $0.05$, so there the cap, not the record, sets the range; with all "
                r"weights nonnegative the range is the same at every spacing and both caps.")
    return ""


def part_a_table(RA):
    rows = []
    for key, c in RA["configs"].items():
        rng = "empty" if c["empty"] else f"[{sig(c['H_Foreign']['min'])}, {sig(c['H_Foreign']['max'])}]"
        urng = "" if c["empty"] else f"[{sig(c['U']['min'])}, {sig(c['U']['max'])}]"
        rel = ", ".join(sig(v) for v in c["relabeling_values_H_Foreign_in_class"]) or "none"
        rec = "panel" if c["record"] == "whole_panel" else "one stock"
        box = _box_label(c["box"])
        rows.append(f"{c['variant']} & ${c['gamma']:.2f}$ & {box} & {rec} & {rng} & {urng} & "
                    f"{c['n_feasible_starts']}/{c['n_starts']} & {rel}\\\\")
    return (r'''

\paragraph{The ranges on the theory's class (P1M-A1, part A).} Protocol \nolinkurl{P1M_A1_protocol.md}, fixed before the run, recomputes the targeted and uniform ranges above with the alternative compositions restricted to memories in $[0,0.99]$, weights either all nonnegative (P, the class of the lower bounds) or with the signs of the tagged estimates (T), and memories at least $\gamma$ apart. The spectral-rate constraint, boxes and starts are P1M's. The reported endpoints come from feasible points visited by the search. Global extrema are unknown. The last column lists the halt effects of the estimate's relabelings that lie in the class, which every record length leaves possible.''' + post_run_supp(RA) + r'''

\begin{center}\footnotesize\setlength{\tabcolsep}{3pt}
\begin{tabular}{cclcccc>{\raggedright\arraybackslash}p{0.17\textwidth}}\toprule
Class & $\gamma$ & box $\bar h$ & record & targeted range & uniform range & starts & relabelings in class\\\midrule
''' + "\n".join(rows) + r'''
\bottomrule\end{tabular}
\end{center}
''')


def part_b_sentence(RB, table_ref):
    ci = RB["runs"]["primary"]["bootstrap"]["ci"]["H_Foreign"]
    lo, hi = ci["ci95"]
    s = (r"With feedback decoupled from each class's flow persistence (a free ten-day distributed lag of $x$, with "
         r"second-order autoregressive non-feedback flow), foreign feedback contributes " + sig(ci["est"]) +
         r" (95\% interval [" + sig(lo) + ", " + sig(hi) + "]), ")
    if lo <= H_FOREIGN_TABLE <= hi:
        s += "which contains the estimate of " + table_ref + "."
    else:
        s += "which does not contain the estimate of " + table_ref + "; that estimate rests on tying feedback to flow persistence."
    return s


def _two(v):
    """Two significant digits as a plain number (effects in units of 1e-4)."""
    if abs(v) < 1e-12:
        return "0"
    d = max(1 - int(math.floor(math.log10(abs(v)))), 0)
    return f"{round(v, d):.{d}f}".replace("-", "$-$")


def part_b_table(RB):
    rows = []
    names = {"primary": r"$J=10$, AR(2)", "J5": r"$J=5$, AR(2)", "J20": r"$J=20$, AR(2)", "AR1": r"$J=10$, AR(1)"}
    for label, R in RB["runs"].items():
        ci = R["bootstrap"]["ci"]
        cells = [f"{_two(1e4 * ci[k]['est'])} [{_two(1e4 * ci[k]['ci95'][0])}, {_two(1e4 * ci[k]['ci95'][1])}]"
                 for k in ("H_Foreign", "H_Trust", "H_Dealers", "U")]
        phis = ", ".join(_two(R["rules"][c]["phi"][0]) for c in ("Foreign", "Trust", "Dealers"))
        rows.append(f"{names.get(label, label)} & " + " & ".join(cells) + f" & {phis}\\\\")
    kap = RB.get("kappa_matches_P1M")
    rp = RB.get("restricted_P1M")
    restricted = ("" if not rp else " The restricted estimates of the table above are " +
                  ", ".join(_two(1e4 * v) for v in rp["H"]) + " and " + _two(1e4 * rp["U"]) + ".")
    return (r"""

\paragraph{Rules with feedback decoupled from flow persistence (P1M-A1, part B).} Under the same protocol, each class's flow is $u_{c,t}=\alpha_{c,s}+\sum_{j=1}^{J}\beta_{c,j}x_{t-j}+e_{c,t}$ with autoregressive non-feedback flow $e_{c,t}$, estimated by iterated Cochrane--Orcutt with stock fixed effects; $H_c=\kappa\sum_j\beta_{c,j}$, with P1M's price equation and date bootstrap. """ +
            ("The price equation's $\\kappa$ equals P1M's. " if kap else "") + r"""Effects are in units of $10^{-4}$, with 95\% intervals; the last column gives $\phi_1$ for Foreign, Trust and Dealers.""" + restricted + r"""

\begin{center}\footnotesize\setlength{\tabcolsep}{4pt}
\begin{tabular}{lccccc}\toprule
Run & $H_{\mathrm F}$ & $H_{\mathrm T}$ & $H_{\mathrm D}$ & $U$ & $\phi_1$ (F, T, D)\\\midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}
\end{center}
""")


LONG_SECOND_END = r"tagged flows carry little information about feedback memory (the $5{,}738$ years above)."
SUPP_ANCHOR = r"and the notebook end to end on simulated exchange files (\nolinkurl{test_p1m_notebook.py})."


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:80], t.count(old))
    return t.replace(old, new)


def apply(t):
    """The long version (applied by build_revision.py after round9)."""
    if RES_A.exists():
        RA = json.loads(RES_A.read_text())
        t = _rep(t, NOT_COMPUTED, part_a_passage(RA) + post_run_main(RA))
        t = _rep(t, SUPP_ANCHOR, SUPP_ANCHOR + part_a_table(RA))
    if RES_B.exists():
        RB = json.loads(RES_B.read_text())
        t = _rep(t, LONG_SECOND_END, LONG_SECOND_END + " " + part_b_sentence(RB, r"Table~\ref{tab:barrier}"))
        anchor = SUPP_ANCHOR + (part_a_table(json.loads(RES_A.read_text())) if RES_A.exists() else "")
        t = _rep(t, anchor, anchor + part_b_table(RB))
    return t
