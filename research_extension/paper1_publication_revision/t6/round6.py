"""Sixth round: "The barrier in a real market" (measurement P1M, protocol
ceiling_suite/p1_empirics/P1M_measurement_protocol.md). The paragraph is the protocol's section-7 template, filled
mechanically from p1m_results.json. Written before the run; applied by build_revision.py only once the results exist.
If an outcome goes the other way, the protocol says the paragraph says so: `apply` checks the three directions and
switches the corresponding sentence."""
import json
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[3] / "ceiling_suite/p1_empirics/results/p1m_results.json"


def sig(x, d=2):
    """Two significant digits in LaTeX math."""
    if x is None or not math.isfinite(x):
        return r"$\infty$"
    if x == 0:
        return "$0$"
    e = int(math.floor(math.log10(abs(x))))
    if -3 <= e <= 4:
        dec = max(d - 1 - e, 0)
        return f"${x:,.{dec}f}$".replace(",", "{,}")
    m = x / 10 ** e
    m = float(f"{m:.{d - 1}f}")
    if abs(m) >= 10:
        m /= 10; e += 1
    return f"${m:g}\\times10^{{{e}}}$"


def years(x):
    if x is None or not math.isfinite(x):
        return r"$\infty$"
    if x > 10 and x < 1e6:
        return f"${x:,.0f}$".replace(",", "{,}")
    return sig(x)


def fill(R):
    P = R["runs"]["primary"]
    ci, q1 = P["bootstrap"]["ci"], P["Q1"]
    g, gt = P["Q2Q3_whole_panel"], P["Q2Q3_whole_panel_tight_box"]
    H = P["effects"]["H"]
    v = {
        "N": f"{P['records']['n_stocks']}", "n": f"{P['records']['pooled_stock_days']:,.0f}".replace(",", "{,}"),
        "rate_p": sig(q1["price_rate_per_stock_day"]), "rate_t": sig(q1["tag_rate_per_stock_day"]),
        "ratio": sig(q1["information_ratio_tags_to_prices"]),
        "yrs_stock": years(q1["years_prices_one_stock_at_least"]),
        "yrs_panel": years(q1["years_prices_whole_panel_at_least"]),
        "yrs_tag": years(q1["years_tags_one_stock_at_least"]),
        "H": sig(ci["H_Foreign"]["est"]), "lo": sig(ci["H_Foreign"]["ci95"][0]), "hi": sig(ci["H_Foreign"]["ci95"][1]),
        "Hmin": sig(g["H_Foreign"]["min"]), "Hmax": sig(g["H_Foreign"]["max"]),
        "Hmin_t": sig(gt["H_Foreign"]["min"]), "Hmax_t": sig(gt["H_Foreign"]["max"]),
        "H_F": sig(H[0]), "H_T": sig(H[1]), "H_D": sig(H[2]),
        "Umin": sig(g["U"]["min"]), "Umax": sig(g["U"]["max"]),
        "U": sig(ci["U"]["est"]), "Ulo": sig(ci["U"]["ci95"][0]), "Uhi": sig(ci["U"]["ci95"][1]),
    }
    dirs = {
        "tags_faster": q1["tag_rate_per_stock_day"] > q1["price_rate_per_stock_day"],
        "targeted_wider_than_tags": (g["H_Foreign"]["max"] - g["H_Foreign"]["min"]) >
                                    (ci["H_Foreign"]["ci95"][1] - ci["H_Foreign"]["ci95"][0]),
        "uniform_narrower": (g["U"]["max"] - g["U"]["min"]) < (g["H_Foreign"]["max"] - g["H_Foreign"]["min"]),
    }
    return v, dirs, P


def table(P):
    ci = P["bootstrap"]["ci"]
    rows = []
    for c, name in (("Foreign", "Foreign investors"), ("Trust", "Investment trusts"), ("Dealers", "Dealers")):
        cell = lambda k: f"{sig(ci[k]['est'])} [{sig(ci[k]['ci95'][0])}, {sig(ci[k]['ci95'][1])}]"
        rows.append(f"{name} & {cell('r_' + c)} & {cell('w_' + c)} & {cell('H_' + c)}\\\\")
    k, a = ci["kappa"], ci["sum_a"]
    return (r'''\begin{table}[t]\centering\small
\caption{Tagged rules in Taiwan, 2013--2016 (stock fixed effects; 95\% date-block bootstrap intervals). $r_c$: persistence; $w_c$: response to the previous day's price deviation; $H_c=\kappa w_c/(1-r_c)$: the fall in the feedback budget if class $c$'s feedback is halted.}\label{tab:barrier}
\begin{tabular}{lccc}\toprule
Class & $r_c$ & $w_c$ & $H_c$\\\midrule
''' + "\n".join(rows) + f'''
\\midrule
\\multicolumn{{4}}{{l}}{{Impact of lagged flow $\\kappa$: {sig(k['est'])} [{sig(k['ci95'][0])}, {sig(k['ci95'][1])}]; price persistence $\\sum_ja_j$: {sig(a['est'])}.}}\\\\
\\bottomrule\\end{{tabular}}\\end{{table}}
''')


def paragraph(v, dirs):
    s1 = (r"\emph{First, prices separate the classes slowly.} Against the closest single-memory population, in which "
          r"the three classes share one decay, a stock-day of prices carries {rate_p} nats and a stock-day of tagged "
          r"flows {rate_t}, {ratio} times more. Before any 5\% test could reach 80\% power, prices alone need, to leading order, at least "
          r"{yrs_stock} years of one stock, or {yrs_panel} years of all {N} stocks treated as independent; the tagged "
          r"record needs at least {yrs_tag} years of one stock.")
    if not dirs["tags_faster"]:
        s1 = (r"\emph{First, against the closest single-memory population, prices carry {rate_p} nats per stock-day and "
              r"tagged flows {rate_t}: in this market the tags do not separate the classes faster than prices.} Before any "
              r"5\% test could reach 80\% power, prices alone need, to leading order, at least {yrs_stock} years of one stock, or {yrs_panel} "
              r"years of all {N} stocks treated as independent.")
    s2 = (r"\emph{Second, prices cannot fix a targeted halt.} With tags, foreign feedback contributes {H} to the "
          r"feedback budget (95\% interval [{lo}, {hi}]), so halting it changes the budget by minus that amount. The compositions that the whole panel record cannot tell apart, in "
          r"the sense that, to leading order (record length times the asymptotic divergence rate at most 0.02), no test exceeds its size by more than 0.10, imply contributions from {Hmin} to {Hmax}; even with each "
          r"class's contribution capped at twice the largest estimated one, from {Hmin_t} to {Hmax_t}. However long the "
          r"record, relabeling alone leaves {H_F}, {H_T} and {H_D} all possible.")
    if not dirs["targeted_wider_than_tags"]:
        s2 = (r"\emph{Second, in this market prices pin the targeted halt about as well as tags.} With tags, foreign "
              r"feedback contributes {H} to the feedback budget (95\% interval [{lo}, {hi}]); the compositions that the whole "
              r"panel record cannot tell apart imply contributions from {Hmin} to {Hmax}. Relabeling alone still leaves {H_F}, "
              r"{H_T} and {H_D} possible, however long the record.")
    s3 = (r"\emph{Third, the uniform cut is fixed by prices.} Over the same compositions, the effect of cutting all "
          r"feedback lies between {Umin} and {Umax}.")
    if not dirs["uniform_narrower"]:
        s3 = (r"\emph{Third, in this market the uniform cut is not fixed more tightly than the targeted halt:} over the same "
              r"compositions its effect lies between {Umin} and {Umax}.")
    body = (r"\paragraph{The barrier in a real market.} Taiwan's exchange reports each day's net buying in every listed "
            r"stock by three classes: foreign investors, investment trusts and dealers. Over 2013--2016 ({N} stocks, {n} "
            r"stock-days) we estimate each class's rule from its own flow and the market's response to flow from prices "
            r"(Table~\ref{tab:barrier}). We then ask what a supervisor who sees only prices could learn, granting that "
            r"supervisor the market's impact function and the law of non-feedback order flow, so that only the "
            r"composition is unknown. " + s1 + " " + s2 + " " + s3 + " "
            r"These are calibrations of Theorems~\ref{n:cost} and~\ref{n:dual} at the tagged responses, not tests. The "
            r"registered Taiwan test (Supplement Section~\ref{sec:scope}) did not establish that those responses are "
            r"feedback rather than prices revealing past flow. The protocol was fixed before the run "
            r"(\nolinkurl{P1M_measurement_protocol.md}); its deterministic steps are checked in Lean~4 "
            r"(\nolinkurl{PublicationRevision7.lean}) and the pre-specified sensitivity runs are in Supplement "
            r"Section~\ref{app:barrier}.")
    for k, val in v.items():
        body = body.replace("{" + k + "}", val)
    assert "{" + "rate_p}" not in body
    return body + "\n\n"


def supp(R):
    lines = []
    for name, lab in (("primary", "Primary"), ("dealer_own_account", "Dealers' own account"),
                      ("same_day_timing", "Same day ($d=0$)"), ("one_price_lag", "One price lag ($p=1$)")):
        P = R["runs"][name]
        q1, g = P["Q1"], P["Q2Q3_whole_panel"]
        ci = P["bootstrap"]["ci"]
        lines.append(f"{lab} & {sig(ci['H_Foreign']['est'])} & [{sig(g['H_Foreign']['min'])}, {sig(g['H_Foreign']['max'])}] & "
                     f"[{sig(g['U']['min'])}, {sig(g['U']['max'])}] & {years(q1['years_prices_one_stock_at_least'])} & "
                     f"{sig(q1['information_ratio_tags_to_prices'])}\\\\")
    P = R["runs"]["primary"]
    one = P["Q2Q3_one_stock"]
    return (r'''\subsection{The barrier in a real market: protocol and sensitivity}\label{app:barrier}

The measurement follows \nolinkurl{P1M_measurement_protocol.md}, fixed before the run, on the P1T development period (2013-01-02 to 2016-12-30, designated for exploration; no later date is loaded). Rules $u_{c,t}=r_cu_{c,t-1}+w_cx_{t-1}+\eta_{c,t}$ and the price equation $x_t=\sum_{j=1}^5a_jx_{t-j}+\kappa U_{t-1}+\varepsilon_t$ are estimated with stock fixed effects; intervals use a stationary date-block bootstrap (mean block 20, $B=999$). With the impact function and non-feedback flow held fixed, the spectral density of $x$ is $g/|A|^2$ with $A(z)=1-\sum_ja_jz^j-\kappa z^{2}\sum_cw_c/(1-r_cz)$, so the Whittle divergence rate between compositions depends on $A$ alone (\nolinkurl{spectral_ratio}); its integrand is nonnegative (\nolinkurl{whittle_integrand_nonneg}). Halting class $c$ lowers the budget by $\kappa w_c/(1-r_c)$ (\nolinkurl{halt_geometric}, \nolinkurl{budget_of_rules}, \nolinkurl{halt_effect}); relabeling leaves the kernel unchanged but moves the halt effect (\nolinkurl{relabel_kernel}, \nolinkurl{relabel_halt}); a uniform cut depends on the kernel alone (\nolinkurl{uniform_cut_effect}). The indistinguishable set uses $n\cdot\mathrm{rate}\le0.02$, so by Pinsker no test exceeds its size by more than $0.10$ (\nolinkurl{pinsker_indistinguishable}); the record lengths are Pinsker's necessary lengths (\nolinkurl{pinsker_record_length}). Ranges are the extremes found by SLSQP from the estimate, its five relabelings and 40 random starts, so the true ranges contain them. For a single stock's record the targeted range is ''' +
            f"[{sig(one['H_Foreign']['min'])}, {sig(one['H_Foreign']['max'])}] and the uniform range [{sig(one['U']['min'])}, {sig(one['U']['max'])}]." +
            r'''

\begin{center}\footnotesize\setlength{\tabcolsep}{4pt}
\begin{tabular}{lccccc}\toprule
Run & $\hat H_{\mathrm{F}}$ & targeted range & uniform range & years, 1 stock & tags/prices\\\midrule
''' + "\n".join(lines) + r'''
\bottomrule\end{tabular}
\end{center}

\nolinkurl{p1m_core.py} is checked on simulated markets (\nolinkurl{test_p1m_core.py}: parameter recovery, the Whittle rate against the exact finite-record divergence, zero rate at relabelings, the data-processing inequality between the tagged and price records) and the notebook end to end on simulated exchange files (\nolinkurl{test_p1m_notebook.py}).

''')


LEAN_ROW_ANCHOR = r'Theorem~\ref{n:uniformlog} & omitted coefficients'
LEAN_ROW = (r'The barrier in a real market & halt effect of a geometric rule, relabeling, uniform cut, Whittle integrand, '
            r'Pinsker record length (\texttt{halt\_geometric} and twelve others) & Whittle' + "'" + r's formula and Pinsker' +
            "'" + r's inequality (hypotheses)\\' + '\n')


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:80], t.count(old))
    return t.replace(old, new)


def apply(t):
    R = json.load(open(RESULTS))
    v, dirs, P = fill(R)
    t = _rep(t, r'\section{Scope and conclusion}\label{n:concl}',
             table(P) + paragraph(v, dirs) + r'\section{Scope and conclusion}\label{n:concl}')
    t = _rep(t, r'\paragraph{Machine check.} The divergence of a moving window', supp(R) + r'\paragraph{Machine check.} The divergence of a moving window')
    t = _rep(t, LEAN_ROW_ANCHOR, LEAN_ROW + LEAN_ROW_ANCHOR)
    t = _rep(t, r'six Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision6.lean}',
             r'seven Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision7.lean}')
    return t
