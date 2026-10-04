#!/usr/bin/env python3
"""Provenance ledger: every retained headline number in the paper, tied to the artifact that produces it.

Each claim has
  * ``tex``     – a string that must appear verbatim in the manuscript;
  * ``value``   – a function that recomputes the printed value from a result artifact
                  (or from a closed-form formula, for ANALYTIC claims);
  * ``printed`` – the string the paper prints, which ``value()`` must reproduce exactly.

``python scripts/provenance_ledger.py`` checks all claims, then writes
``results/provenance/ledger.md`` and ``paper/generated/provenance_ledger.tex``.
``tests/test_provenance_ledger.py`` runs the same checks, so any edit to the paper or an
artifact that breaks the correspondence fails the test suite.

Rounding convention: accounting residuals in Sections 4 and 6 are printed rounded *up*
to three significant figures (they are upper bounds); everything else is rounded to nearest.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "Machine_Markets_Final_Integrated_Paper.tex"

OBS = "studies/observable_stress_tests/results"
AUD = "studies/audited_constraints/results"
FHA = "studies/full_horizon_audit/results"
STAT = "research_extension/outputs/statistical_repair_20260926/verified"
EVID = "research_extension/outputs/evidence_repair_20260926"
FUND = "research_extension/outputs/funded_mechanism_results.json"
SURF = "research_extension/outputs/funded_smooth_surface_results.json"
PROV = "results/provenance"


# --------------------------------------------------------------------------- helpers
@lru_cache(maxsize=None)
def J(rel: str):
    return json.loads((ROOT / rel).read_text())


@lru_cache(maxsize=None)
def C(rel: str) -> tuple:
    with open(ROOT / rel, newline="") as fh:
        return tuple(csv.DictReader(fh))


def f(x: float, d: int) -> str:
    return f"{x:.{d}f}"


def pct(num: float, den: float, d: int = 2) -> str:
    return f"{100.0 * num / den:.{d}f}"


def com(n: int) -> str:
    return f"{int(n):,}"


def sci_up(x: float, sig: int = 3) -> str:
    """Round a positive residual *up* to `sig` significant figures, LaTeX mantissa/exponent."""
    e = math.floor(math.log10(x))
    m = math.ceil(x / 10 ** e * 10 ** (sig - 1) - 1e-9) / 10 ** (sig - 1)
    return f"{m:.{sig - 1}f}\\times10^{{{e}}}"


def sci_near(x: float, sig: int = 2) -> str:
    m, e = f"{x:.{sig - 1}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def rows(rel: str, **eq) -> list:
    out = []
    for r in C(rel):
        if all(abs(float(r[k]) - v) < 1e-12 if isinstance(v, float) else r[k] == str(v) for k, v in eq.items()):
            out.append(r)
    return out


def isum(rs, key) -> int:
    return sum(int(float(r[key])) for r in rs)


# --------------------------------------------------------------------------- analytic helpers
def witness():
    """Retained rational witness (Theorem retained_pair): impulse responses and gains."""
    rates = [Fraction(1), Fraction(1, 2), Fraction(1, 20)]

    def h(a, w, T=9):
        x, y = [Fraction(1)], [Fraction(0)] * 3
        for _ in range(T - 1):
            xn = a * x[-1] + sum(y)
            y = [(1 - e) * yi + e * q * x[-1] for e, q, yi in zip(rates, w, y)]
            x.append(xn)
        return x

    a = Fraction(2, 5)
    w0, w1 = [0, Fraction(12, 65), 0], [Fraction(54, 1235), 0, Fraction(240, 247)]
    return h(a, w0), h(a, w1), float(a + sum(w0)), float(a + sum(w1))


def minimal_rho(a, rates, w):
    import numpy as np

    act = [(e, q) for e, q in zip(rates, w) if q != 0]
    n = len(act)
    M = np.zeros((n + 1, n + 1))
    M[0, 0] = float(a)
    M[0, 1:] = 1.0
    for i, (e, q) in enumerate(act):
        M[i + 1, 0] = float(e * q)
        M[i + 1, i + 1] = float(1 - e)
    return float(max(abs(np.linalg.eigvals(M))))


def price_law(eta: float, level: bool):
    """Oracle error for the Section 4 price-observation pair (difference or level errors)."""
    import numpy as np
    from scipy.stats import norm

    def beta(q, a=0.4, k=0.02, H=64):
        r = [0.5, eta]
        M = np.zeros((3, 3))
        M[0, 0] = a
        M[0, 1:] = 1
        for i in range(2):
            M[i + 1, 0] = r[i] * q[i]
            M[i + 1, i + 1] = 1 - r[i]
        v, out = np.array([1.0, 0, 0]), []
        for _ in range(H + 1):
            out.append(k * v[0])
            v = M @ v
        return np.array(out)

    R, d, s, H = 1024, 4.0, 0.002, 64
    db = beta(0.6 * np.array([0.7, 0.4])) - beta(0.6 * np.array([0.7, 0.2]))
    if level:
        P = np.eye(H + 1) - np.ones((H + 1, H + 1)) / (H + 2)
        D2 = R * d * d / s / s * db @ P @ db
    else:
        D2 = R * d * d / s / s * float(db @ db)
    return float(norm.cdf(-math.sqrt(D2) / 2))


# --------------------------------------------------------------------------- claims
@dataclass(frozen=True)
class Claim:
    cid: str
    where: str
    what: str
    tex: str
    printed: str
    value: Callable[[], str]
    source: str
    kind: str = "ARTIFACT"  # or ANALYTIC


def _dealer(i, key):
    return pct(float(C(f"{AUD}/dealer_stress.csv")[i][key]), 1)


def _qpol(i):
    v = J(f"{EVID}/learned_agents/results.json")["policies"][i]["active_minus_frozen"]
    return f"{v:+.6f}"


def _lin(steps, design, episodes, key):
    return isum(rows(f"{AUD}/linear_by_rate.csv", steps="%d" % steps, design=design, episodes="%d" % episodes), key)


def _end(design, ep, key):
    return int(rows(f"{AUD}/endpoint_summary.csv", design=design, episodes=str(ep))[0][key])


def _tail(slow, ep):
    r = [x for x in C(f"{AUD}/measured_tail_summary.csv") if x["steps"] == "64" and x["design"] == "impulse"
         and abs(float(x["slow"]) - slow) < 1e-12 and x["episodes"] == str(ep)][0]
    return f(float(r["median_upper"]), 6)


def _primary(ep, sh, key):
    r = [x for x in C(f"{OBS}/design_summary.csv") if x["episodes"] == str(ep) and float(x["probe_shares"]) == sh
         and x["horizon"] == "64"][0]
    return int(r[key])


W = witness()

CLAIMS: list[Claim] = [
    # ---------------- Section 3
    Claim("S3-wit-S", "Tab. retained witness", "S of stable/unstable member", r"$S=a+Q$ & 0.584615 & 1.415385",
          "0.584615/1.415385", lambda: f"{f(W[2], 6)}/{f(W[3], 6)}", "exact rational recursion", "ANALYTIC"),
    Claim("S3-wit-rho", "Tab. retained witness", "rho(J) of minimal realizations", r"$\rho(J)$ & 0.757909 & 1.032345",
          "0.757909/1.032345",
          lambda: f"{f(minimal_rho(Fraction(2,5),[1,Fraction(1,2),Fraction(1,20)],[0,Fraction(12,65),0]),6)}/"
                  f"{f(minimal_rho(Fraction(2,5),[1,Fraction(1,2),Fraction(1,20)],[Fraction(54,1235),0,Fraction(240,247)]),6)}",
          "eigenvalues of minimal realization", "ANALYTIC"),
    Claim("S3-wit-h4", "Tab. retained witness", "h_4 diverges", r"$h_4$ & 0.138428 & 0.159198",
          "0.138428/0.159198", lambda: f"{f(float(W[0][4]),6)}/{f(float(W[1][4]),6)}",
          f"{EVID}/paper_artifacts.json (witness) and exact recursion", "ANALYTIC"),
    Claim("S3-kernel-oracle", "Sec. 3 full-horizon audit", "kernel-law oracle error / coverage bound",
          r"the oracle error is 49.6394\%. An unconditional error target of 5\% permits at most 10.7212\%",
          "49.6394/10.7212",
          lambda: f"{100*J(f'{FHA}/testing_limits_summary.json')['example']['oracle_error']:.4f}/"
                  f"{100*J(f'{FHA}/testing_limits_summary.json')['example']['coverage_upper_bound_at_5pct_error']:.4f}",
          f"{FHA}/testing_limits_summary.json"),
    # ---------------- Section 4: comparator grid and calibration
    Claim("S4-grid-oe", "Tab. comparator", "output-error covered/issued/wrong", r"Output-error & 193/600 & 438/600 & 204 & 34.00 & 46.58 & 31",
          "193/438/204/34.00/46.58/31",
          lambda: _grid_oe(), f"{STAT}/artifacts/paper_artifacts.json (grid_summary)"),
    Claim("S4-grid-widths", "Tab. widths", "recurrence finite mean / p90 width", r"Recurrence LP & 596 & 1 & 3 & 51.190 & 105.066",
          "596/1/3/51.190/105.066",
          lambda: (lambda g: f"{g['finite_intervals']}/{g['unbounded_intervals']}/{g['invalid_intervals']}/"
                             f"{f(g['finite_mean_interval_width'],3)}/{f(g['finite_p90_interval_width'],3)}")(
              J(f"{STAT}/artifacts/paper_artifacts.json")["grid_summary"]["recurrence_lp"]),
          f"{STAT}/artifacts/paper_artifacts.json (grid_summary)"),
    Claim("S4-calib", "Tab. pivot calibration", "known/estimated coverage", r"Known & $\chi^2$ & 18975/20000 & 94.875 & [94.460, 95.268] \\ Estimated & $F$ & 19000/20000", "18975/19000",
          lambda: f"{J(f'{STAT}/calibration/results.json')['known']['covered']}/{J(f'{STAT}/calibration/results.json')['estimated']['covered']}",
          f"{STAT}/calibration/results.json"),
    # ---------------- Section 4: primary price-only panel
    Claim("S4-cover", "Sec. 4 primary panel", "simultaneous response coverage", r"in 1,895 of 1,920 panels, or 98.70\%",
          "1,895/1,920/98.70",
          lambda: (lambda s: f"{com(s['response_coverage_count'])}/{com(s['panels'])}/{pct(s['response_coverage_count'], s['panels'])}")(J(f"{OBS}/summary.json")),
          f"{OBS}/summary.json"),
    Claim("S4-adjcorr", "Sec. 4 primary panel", "mean |adjacent correlation|", r"adjacent correlation was 0.8497", "0.8497",
          lambda: f(J(f"{OBS}/summary.json")["mean_abs_adjacent_correlation"], 4), f"{OBS}/summary.json"),
    Claim("S4-tab-128x4", "Tab. observable primary", "R=128, pulse 4: recurrence / point wrong",
          r"128 & 4 & 28/480 (0) & 0/480 (0) & 480/480 (56)", "28/56",
          lambda: f"{_primary(128, 4.0, 'recurrence_definite')}/{_primary(128, 4.0, 'point_wrong')}", f"{OBS}/design_summary.csv"),
    Claim("S4-tab-1024x4", "Tab. observable primary", "R=1024, pulse 4: recurrence / point wrong",
          r"1,024 & 4 & 80/480 (0) & 0/480 (0) & 480/480 (37)", "80/37",
          lambda: f"{_primary(1024, 4.0, 'recurrence_definite')}/{_primary(1024, 4.0, 'point_wrong')}", f"{OBS}/design_summary.csv"),
    Claim("S4-decisions", "Sec. 4 primary panel", "recurrence decisions / inconclusive rows",
          r"the recurrence method makes 256 decisions (176 stable and 80 unstable) and leaves 5,504 rows inconclusive",
          "256/5,504",
          lambda: (lambda n: f"{n}/{com(J(f'{OBS}/summary.json')['comparison_rows'] - n)}")(isum(C(f"{OBS}/design_summary.csv"), "recurrence_definite")),
          f"{OBS}/design_summary.csv, summary.json"),
    Claim("S4-pointwrong", "Sec. 4 primary panel", "point-fit wrong labels", r"The point estimator makes 1,191 wrong labels", "1,191",
          lambda: com(J(f"{OBS}/summary.json")["point_wrong"]), f"{OBS}/summary.json"),
    Claim("S4-budget-ext", "Sec. 4 budget extension", "simulated episodes", r"The extension contributes 2,457,600 simulated episodes",
          "2,457,600", lambda: com(J(f"{OBS}/extension_summary.json")["budget_episodes"]), f"{OBS}/extension_summary.json"),
    Claim("S4-pricelaw-diff", "Sec. 4 price-law example", "oracle errors, difference model",
          r"the exact oracle errors are 49.94\%, 49.42\%, 44.27\%, and 7.45\%", "49.94/49.42/44.27/7.45",
          lambda: "/".join(f"{100*r['oracle_error']:.2f}" for r in J(f"{OBS}/price_observation_limits.json")[:4]),
          f"{OBS}/price_observation_limits.json"),
    Claim("S4-pricelaw-cov", "Sec. 4 price-law example", "max coverage at 5% error (difference)",
          r"permits at most 21.46\% balanced decision coverage", "21.46",
          lambda: f"{100*J(f'{OBS}/price_observation_limits.json')[2]['max_coverage_at_5pct_unconditional_error']:.2f}",
          f"{OBS}/price_observation_limits.json"),
    Claim("S4-pricelaw-level", "Sec. 4 price-law example", "oracle errors, level-error model",
          r"the corresponding oracle errors are 49.98\%, 49.76\%, 47.56\%, and 27.02\%", "49.98/49.76/47.56/27.02",
          lambda: "/".join(f"{100*price_law(e, True):.2f}" for e in (1e-7, 1e-6, 1e-5, 1e-4)),
          "eq. (price_distance_level), recomputed", "ANALYTIC"),
    Claim("S4-pricelaw-diff-recompute", "Sec. 4 price-law example", "difference-model errors recomputed from formula",
          r"the exact oracle errors are 49.94\%, 49.42\%, 44.27\%, and 7.45\%", "49.94/49.42/44.27/7.45",
          lambda: "/".join(f"{100*price_law(e, False):.2f}" for e in (1e-7, 1e-6, 1e-5, 1e-4)),
          "eq. (price_distance), recomputed", "ANALYTIC"),
    Claim("S4-nonlin", "Sec. 4 controls", "initial impact per share (nonlinear control)",
          r"initial price response per share is 0.0195935, 0.0152319 and 0.00499665", "0.0195935/0.0152319/0.00499665",
          lambda: "/".join(f"{r['initial_impact']:.6g}" for r in J(f"{OBS}/nonlinear_scaling.json")), f"{OBS}/nonlinear_scaling.json"),
    Claim("S4-acct", "Sec. 4 accounting", "max conservation residuals (rounded up)",
          r"$3.37\times10^{-11}$ dollars in cash transfers, $3.52\times10^{-13}$ shares and $4.61\times10^{-11}$",
          r"3.37\times10^{-11}/3.52\times10^{-13}/4.61\times10^{-11}",
          lambda: (lambda s: f"{sci_up(s['max_cash_error'])}/{sci_up(s['max_share_error'])}/{sci_up(s['max_marked_wealth_error'])}")(J(f"{OBS}/summary.json")),
          f"{OBS}/summary.json"),
    # ---------------- Section 5: audited terminal-row study
    Claim("S5-primary", "Sec. 5 primary budget experiment", "coverage / decisions / wrong",
          r"2,758 of 2,880 gain intervals cover the true gain, establishing a parameter coverage of 95.76\%", "2,758/2,880/95.76",
          lambda: (lambda s: f"{com(s['covered'])}/{com(s['panels'])}/{pct(s['covered'], s['panels'])}")(J(f"{AUD}/linear_summary.json")),
          f"{AUD}/linear_summary.json"),
    Claim("S5-dec", "Sec. 5 primary budget experiment", "decisiveness and conditional error",
          r"745 produce definite classification decisions (a decisiveness rate of 25.87\%), while 2,135 abstain. Among all 2,880 panels, twenty result in confident errors (an unconditional error rate of 0.69\%). Crucially, evaluated among the 745 issued decisions, the conditional error rate is $20 / 745 = \mathbf{2.68\%}$",
          "745/25.87/2.68",
          lambda: (lambda s: f"{s['definite']}/{pct(s['definite'], s['panels'])}/{pct(s['wrong'], s['definite'])}")(J(f"{AUD}/linear_summary.json")),
          f"{AUD}/linear_summary.json"),
    Claim("S5-design", "Sec. 5 primary budget experiment", "impulse vs round trips, T=64",
          r"At $T=64,n=128$, the impulse resolves 86/240 panels, versus 46/240 for the round trips. At $n=512$, those counts are 158/240 and 80/240.",
          "86/46/158/80",
          lambda: f"{_lin(64,'impulse',128,'definite')}/{_lin(64,'roundtrips',128,'definite')}/{_lin(64,'impulse',512,'definite')}/{_lin(64,'roundtrips',512,'definite')}",
          f"{AUD}/linear_by_rate.csv"),
    Claim("S5-endpoint", "Tab. endpoint results", "definite counts fixed vs diversified",
          r"32 & 26 (10.83\%) & 0 & 75 (31.25\%) & 2\\ 128 & 86 (35.83\%) & 0 & 112 (46.67\%) & 1\\ 512 & 159 (66.25\%) & 1 & 144 (60.00\%) & 0",
          "26/75/86/112/159/144",
          lambda: "/".join(str(_end(d, e, "definite")) for e in (32, 128, 512) for d in ("fixed64", "diversified")),
          f"{AUD}/endpoint_summary.csv"),
    Claim("S5-paired", "Sec. 5 endpoint comparison", "paired gains/losses",
          r"At 32 episodes, 56 previously unresolved paired cases become definite and seven go the opposite way: 49 net additional decisions.",
          "56/7/49", lambda: (lambda r: f"{r['new_definite']}/{r['lost_definite']}/{r['net_additional']}")(C(f"{AUD}/endpoint_paired_comparison.csv")[0]),
          f"{AUD}/endpoint_paired_comparison.csv"),
    Claim("S5-slowest", "Sec. 5 endpoint comparison", "slowest rate resolved, fixed 64",
          r"the slowest rate resolves only 4/80 panels at 128 episodes and 15/80 at 512", "4/15",
          lambda: "/".join(rows(f"{AUD}/linear_by_rate.csv", slow=0.002, steps="64", design="impulse", episodes=str(e))[0]["definite"] for e in (128, 512)),
          f"{AUD}/linear_by_rate.csv"),
    Claim("S5-joint", "Sec. 5 measured tail", "joint gain+tail coverage, conflicts",
          r"the joint event holds in 2,796/2,880 panels (97.08\%). There are nine model conflicts.", "2,796/97.08/9",
          lambda: (lambda rs: f"{com(isum(rs,'joint_covered'))}/{pct(isum(rs,'joint_covered'), isum(rs,'panels'))}/{isum(rs,'conflicts')}")(C(f"{AUD}/measured_tail_summary.csv")),
          f"{AUD}/measured_tail_summary.csv"),
    Claim("S5-tail-tab", "Tab. audited tail", "median measured tail upper endpoints",
          r"0.002 & 0.879741 & 0.788458 & 0.490520", "0.879741/0.788458/0.490520",
          lambda: f"{f((1-0.002)**64,6)}/{_tail(0.002,128)}/{_tail(0.002,512)}", f"{AUD}/measured_tail_summary.csv"),
    Claim("S5-controls", "Sec. 5 controls", "omitted channel false stable labels",
          r"Omitting a positive inventory-feedback channel produces three false stable classifications in eighty panels", "3",
          lambda: [r for r in C(f"{AUD}/assumption_control_summary.csv") if r["control"] == "omitted_inventory_channel"][0]["wrong"],
          f"{AUD}/assumption_control_summary.csv"),
    # ---------------- Section 6: funded engine
    Claim("S6-episodes", "Sec. 6 design", "episodes and quote observations",
          r"There are 1,105,920 episodes and 72,990,720 quoted-price observations", "1,105,920/72,990,720",
          lambda: f"{com(J(f'{OBS}/summary.json')['episodes'])}/{com(J(f'{OBS}/summary.json')['price_observations'])}", f"{OBS}/summary.json"),
    Claim("S6-tapes", "Sec. 6 funded panel", "setting-trajectories vs unique tapes",
          r"Therefore 491,520 setting-trajectories use 163,840 unique exogenous episode tapes", "491,520/163,840",
          lambda: f"{com(J(f'{AUD}/financial_summary.json')['simulated_setting_episodes'])}/{com(J(f'{AUD}/financial_summary.json')['unique_exogenous_episode_tapes'])}",
          f"{AUD}/financial_summary.json"),
    Claim("S6-clips", "Sec. 6 funded panel", "clipped orders and margin calls",
          r"The execution engine modifies 12,388,550 order requests and records 2,240,614 account-step margin calls", "12,388,550/2,240,614",
          lambda: f"{com(J(f'{AUD}/financial_summary.json')['clipped_orders'])}/{com(J(f'{AUD}/financial_summary.json')['margin_calls'])}",
          f"{AUD}/financial_summary.json"),
    Claim("S6-acct", "Sec. 6 funded panel", "max residuals (rounded up)",
          r"Maximum cash-conservation error is $2.41\times10^{-10}$ dollars, maximum share error $2.34\times10^{-12}$ shares, and maximum fresh-trade constraint residual $3.19\times10^{-12}$",
          r"2.41\times10^{-10}/2.34\times10^{-12}/3.19\times10^{-12}",
          lambda: (lambda s: f"{sci_up(s['max_cash_error'])}/{sci_up(s['max_share_error'])}/{sci_up(s['max_fresh_trade_violation'])}")(J(f"{AUD}/financial_summary.json")),
          f"{AUD}/financial_summary.json"),
    Claim("S6-binom", "Sec. 6 risk coverage", "exact coverage grid points", r"Exact coverage is separately enumerated on 3,003 $(n,p)$ grid points",
          "3,003", lambda: com(J(f"{AUD}/control_summary.json")["binomial_p_grid_checks"]), f"{AUD}/control_summary.json"),
    Claim("S6-stress-1", "Tab. dealer stress", "G=0.7, slow 0.02, -2: event/halt",
          r"0.7 & 0.02 & $-2$ & 45.42\% & 45.42\%", "45.42/45.42", lambda: f"{_dealer(0,'event_rate')}/{_dealer(0,'halt_rate')}",
          f"{AUD}/dealer_stress.csv"),
    Claim("S6-stress-2", "Tab. dealer stress", "G=0.7, slow 0.02, -10: event/halt",
          r"0.7 & 0.02 & $-10$ & 85.16\% & 82.59\%", "85.16/82.59", lambda: f"{_dealer(1,'event_rate')}/{_dealer(1,'halt_rate')}",
          f"{AUD}/dealer_stress.csv"),
    Claim("S6-stress-8", "Tab. dealer stress", "G=1.3, slow 0.10, -10: event/halt",
          r"1.3 & 0.10 & $-10$ & 77.04\% & 51.75\%", "77.04/51.75", lambda: f"{_dealer(7,'event_rate')}/{_dealer(7,'halt_rate')}",
          f"{AUD}/dealer_stress.csv"),
    Claim("S6-stress-eps", "Sec. 6 dealer stress", "episodes", r"Eight settings each contain 8,192 fresh episodes, totaling 65,536.",
          "8,192/65,536", lambda: f"{com(C(f'{AUD}/dealer_stress.csv')[0]['episodes'])}/{com(J(f'{AUD}/followup_summary.json')['dealer_stress_episodes'])}",
          f"{AUD}/dealer_stress.csv, followup_summary.json"),
    Claim("S6-surface", "Tab. capacity surface", "intermediate cell 13/30", r"The $43.3\%$ cell is 13 hits in 30 repetitions.", "43.3",
          lambda: f([c for c in J(SURF)["grid_cells"] if c["S"] == 0.82 and c["capital_multiplier"] == 1.0 and abs(c["shock_mu"] + 0.6) < 1e-9][0]["halt_rate_pct"], 1),
          SURF),
    Claim("S6-paired", "Tab. funded controls", "mean dislocation by regime",
          r"Active memory & 100.0 & 100.0 & 1.76570 & 9999.06 \\ Frozen memory & 100.0 & 100.0 & 1.15086 & 9999.06 \\ Zero feedback & 100.0 & 100.0 & 1.12686 & 9997.99 \\ Inventory limit removed & 0.0 & 100.0 & 5.06952 & -122.03",
          "1.76570/1.15086/1.12686/5.06952",
          lambda: "/".join(f(J(FUND)["paired_controls"]["summary"][k]["mean_dislocation"], 5) for k in ("adaptive", "frozen", "zero_feedback", "unlimited_funding")),
          FUND),
    Claim("S6-contrast", "Tab. paired contrasts", "active minus frozen [CI]",
          r"Active minus frozen & 0.61484 & [0.61477, 0.61490]", "0.61484/0.61477/0.61490",
          lambda: (lambda c: f"{f(c['dislocation_diff_mean'],5)}/{f(c['dislocation_diff_ci_95'][0],5)}/{f(c['dislocation_diff_ci_95'][1],5)}")(J(FUND)["paired_controls"]["paired_contrasts"]["adaptive_minus_frozen"]),
          FUND),
    Claim("S6-q-mean", "Sec. 6 Q-learning", "active minus frozen mean and CI",
          r"The active-minus-frozen mean is $-0.000227$ with a 95\% population-level Student interval $[-0.000659,0.000204]$",
          "-0.000227/-0.000659/0.000204",
          lambda: (lambda c: f"{f(c['mean'],6)}/{f(c['ci95'][0],6)}/{f(c['ci95'][1],6)}")(J(f"{EVID}/learned_agents/results.json")["contrasts"]["active_minus_frozen"]),
          f"{EVID}/learned_agents/results.json"),
    Claim("S6-q-pol4", "Tab. Q-learning", "policy 04 contrast", r"04 & 28.2 & 0.029856 & 0.028068 & -0.001788", "-0.001788",
          lambda: _qpol(3).replace("+", ""), f"{EVID}/learned_agents/results.json"),
    Claim("S6-q-chartist", "Sec. 6 Q-learning", "chartist displacement", r"its displacement over the corrected common horizon is $0.032783$",
          "0.032783", lambda: f(J(f"{EVID}/learned_agents/results.json")["baselines"]["chartist"]["mean_dislocation"], 6),
          f"{EVID}/learned_agents/results.json"),
    # ---------------- Section 7 (first three subsections): rendered tables are compared verbatim
    Claim("S7-coinbase", "Tab. Coinbase regression", "bivariate row rendered from audit", r"Frozen cache, bivariate & 8 & 0.686639 & 2.426069 & 0.041456 & 0.423872",
          "present", lambda: "present" if "0.686639 & 2.426069 & 0.041456 & 0.423872" in J(f"{EVID}/paper_artifacts.json")["empirical_table_tex"] else "absent",
          f"{EVID}/paper_artifacts.json (empirical_table_tex)"),
    Claim("S7-binance", "Sec. 7 negative control", "BTC mean validation R^2", r"BTC $-0.0683$", "-0.0683",
          lambda: _num_in(f"{EVID}/empirical/binance_chronological_results.json", "-0.0683"),
          f"{EVID}/empirical/binance_chronological_results.json"),
    Claim("S7-gate24", "Tab. gate24 proxies", "BTC row rendered", r"BTC & 2.62007 & 0.2556 & 1.5288 & 0.960785", "present",
          lambda: "present" if "2.62007" in J(f"{EVID}/paper_artifacts.json")["gate_table_tex"] and "0.960785" in J(f"{EVID}/paper_artifacts.json")["gate_table_tex"] else "absent",
          f"{EVID}/paper_artifacts.json (gate_table_tex)"),
    Claim("S7-halts", "Tab. gate4 halts", "BTC 0% shock final equity", r"BTC & $0\%$ & 0/50 & $[0.0\%,7.1\%]$ & 257345.52", "present",
          lambda: "present" if "257345.52" in J(f"{EVID}/paper_artifacts.json")["halt_table_tex"] else "absent",
          f"{EVID}/paper_artifacts.json (halt_table_tex)"),
    Claim("S7-bytes", "Sec. 7 gate24", "bytes consumed", r"totaling 18,445,389 bytes", "18,445,389",
          lambda: _num_in(f"{EVID}/gate24/gate24_summary.json", "18445389", fmt=lambda s: com(int(s))),
          f"{EVID}/gate24/gate24_summary.json"),
    # ---------------- Section 7 (Systematic panel, cross-venue, holdout, structural identification)
    Claim("S7-binance-btc", "Sec. 7 cross-venue", "Binance BTC Q and 95% CI",
          r"On Binance, BTC yields $\hat Q = 0.0102$ [0.0079, 0.0126]", "0.0102/0.0079/0.0126",
          lambda: (lambda b: f"{f(b['Q'], 4)}/{f(b['Q_ci'][0], 4)}/{f(b['Q_ci'][1], 4)}")(J(f"{PROV}/cross_venue_summary.json")["BTC"]["binance"]),
          f"{PROV}/cross_venue_summary.json"),
    Claim("S7-binance-eth", "Sec. 7 cross-venue", "Binance ETH Q and 95% CI",
          r"ETH yields $\hat Q = 0.0069$ [0.0044, 0.0095]", "0.0069/0.0044/0.0095",
          lambda: (lambda b: f"{f(b['Q'], 4)}/{f(b['Q_ci'][0], 4)}/{f(b['Q_ci'][1], 4)}")(J(f"{PROV}/cross_venue_summary.json")["ETH"]["binance"]),
          f"{PROV}/cross_venue_summary.json"),
    Claim("S7-binance-ada", "Sec. 7 cross-venue", "Binance ADA Q and 95% CI",
          r"ADA yields $\hat Q = 0.0108$ [0.0075, 0.0142]", "0.0108/0.0075/0.0142",
          lambda: (lambda b: f"{f(b['Q'], 4)}/{f(b['Q_ci'][0], 4)}/{f(b['Q_ci'][1], 4)}")(J(f"{PROV}/cross_venue_summary.json")["ADA"]["binance"]),
          f"{PROV}/cross_venue_summary.json"),
    Claim("S7-holdout-btc", "Sec. 7 holdout", "Jan 2023 BTC holdout Q, Q30, S, pos share",
          r"(\texttt{1-09-1-20.csv}, covering BTCUSDT in January 2023; $N=11$ days) yields $\hat Q = 0.0149$ [0.0095, 0.0204], $\hat Q_{30} = 0.0128$, and $\hat S = 0.932 < 1$ with $90.9\%$ of days positive",
          "0.0149/0.0095/0.0204/0.0128/0.932/90.9",
          lambda: (lambda h: f"{f(h['Q']['mean'], 4)}/{f(h['Q']['ci95'][0], 4)}/{f(h['Q']['ci95'][1], 4)}/{f(h['Q30']['mean'], 4)}/{f(h['S']['mean'], 3)}/{f(h['share_Q_pos']*100, 1)}")(J(f"{PROV}/binance_panel_summary.json")["holdout_jan2023"]),
          f"{PROV}/binance_panel_summary.json"),
    Claim("S7-panel-regimes", "Sec. 7 Binance panel", "epoch mean Q and positive day shares",
          r"expansion ($\hat Q = 0.0091$, 91.1\% positive days), the 2022 crypto winter ($\hat Q = 0.0068$, 82.8\% positive), the 2023 consolidation ($\hat Q = 0.0078$, 86.5\% positive), and the 2024 institutional/ETF era ($\hat Q = 0.0090$, 87.0\% positive)",
          "0.0091/91.1/0.0068/82.8/0.0078/86.5/0.0090/87.0",
          lambda: (lambda r: f"{f(r['2021']['Q']['mean'], 4)}/{f(r['2021']['share_Q_pos']*100, 1)}/{f(r['2022']['Q']['mean'], 4)}/{f(r['2022']['share_Q_pos']*100, 1)}/{f(r['2023']['Q']['mean'], 4)}/{f(r['2023']['share_Q_pos']*100, 1)}/{f(r['2024']['Q']['mean'], 4)}/{f(r['2024']['share_Q_pos']*100, 1)}")(J(f"{PROV}/binance_panel_summary.json")["by_year"]),
          f"{PROV}/binance_panel_summary.json"),
    Claim("S7-flow-gamma", "Sec. 7 flow memory", "order-splitting memory exponent range",
          r"order-splitting sign-memory exponent yields $\gamma \in [0.22, 0.35]$", "0.22/0.35",
          lambda: (lambda fm: f"{f(min(v['gamma'] for v in fm.values()), 2)}/{f(max(v['gamma'] for v in fm.values()), 2)}")(J(f"{PROV}/flow_memory_bias_correction.json")),
          f"{PROV}/flow_memory_bias_correction.json"),
    Claim("S7-flow-set-btc", "Sec. 7 flow memory", "BTC robust identified set and max loop ratio",
          r"establishing a robust identified set of $[0.015, 0.028]$ for BTC ($[0.008, 0.028]$ across assets) with $\mathcal L_{\max} \le 0.405 < 1$",
          "0.015/0.028/0.008/0.405",
          lambda: (lambda fm: f"{f(fm['BTC']['identified_set'][0], 3)}/{f(fm['BTC']['identified_set'][1], 3)}/{f(min(v['identified_set'][0] for v in fm.values()), 3)}/{f(fm['BTC']['L_max'], 3)}")(J(f"{PROV}/flow_memory_bias_correction.json")),
          f"{PROV}/flow_memory_bias_correction.json"),
    # ---------------- Appendix: standalone verifier
    Claim("App-verifier", "App. replication", "standalone verifier counts and max regression difference",
          r"recomputes the 4,320 terminal-row regression decisions with an SVD solver (all labels match; maximum difference $4.4\times10^{-14}$)",
          r"4,320/4.4\times10^{-14}",
          lambda: (lambda v: f"{com(v['regression_rows_recomputed'])}/{sci_near(v['max_regression_difference'], 2)}" if v["matching_labels"] == v["regression_rows_recomputed"] else "mismatch")(J(f"{AUD}/standalone_verification.json")),
          f"{AUD}/standalone_verification.json"),
]


def _grid_oe() -> str:
    m = J(f"{STAT}/artifacts/paper_artifacts.json")["grid_summary"]["output_error"]
    mm = m["metrics"]
    return (f"{mm['covered_panels']}/{mm['issued_decisions']}/{mm['wrong_decisions']}/"
            f"{f(mm['unconditional_error_pct'],2)}/{f(mm['conditional_error_pct'],2)}/{m['invalid_intervals']}")


def _num_in(rel: str, printed: str, fmt=None) -> str:
    """Return `printed` if some number in the artifact rounds to it at printed precision."""
    txt = (ROOT / rel).read_text()
    d = len(printed.split(".")[1]) if "." in printed else 0
    target = float(printed)
    for m in re.finditer(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", txt):
        try:
            if round(float(m.group()), d) == round(target, d):
                return fmt(printed) if fmt else printed
        except ValueError:
            pass
    return "absent"


WITHDRAWN = [
    ("2SLS / FI-2010 instrumental-variable estimates", "no FI-2010 data or 2SLS output exists in the repository"),
    ("Crypto panel regressions and sub-sample splits", "numbers not produced by any script"),
    ("Former Table 24 (dynamic Hankel empirics)", "no producing code or data"),
    ("Cross-simulator validation", "simulators did not implement the stated model"),
    ("Decisiveness trade-off frontier and eta-frontier figure", "schematic values, not computed"),
    ("Original solvency phase diagram", "feedback parameter did not enter the price process; replaced by Sec. 9 rebuild"),
    ("DQN and continuous-action RL audits", "no executed runs found"),
    ("Constrained robustness example (19/200, 15/200, 78.95%)", "no source artifact; replaced by comparator-grid example"),
    ("Model-class screen calibration (5 x 250 reps)", "no source artifact"),
    ("Standalone verifier '24 gates' and 7.2e-14", "not produced by the verifier; real figures reported instead"),
    ("'7.2/10' self-assessed rating and similar quality scores", "not a result"),
]


# --------------------------------------------------------------------------- checking and rendering
def check(tex_text: str | None = None) -> list[tuple[Claim, str, str]]:
    """Return a list of (claim, problem, computed) for every failing claim."""
    tex_text = tex_text if tex_text is not None else TEX.read_text()
    tex_flat = re.sub(r"\s+", " ", tex_text)
    bad = []
    for c in CLAIMS:
        if re.sub(r"\s+", " ", c.tex) not in tex_flat:
            bad.append((c, "string not in paper", ""))
            continue
        try:
            got = c.value()
        except Exception as exc:  # pragma: no cover - reported, not hidden
            bad.append((c, f"error: {exc!r}", ""))
            continue
        if got != c.printed:
            bad.append((c, "value mismatch", got))
    return bad


def _tex_escape(s: str) -> str:
    return (s.replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")
             .replace("#", r"\#").replace("$", r"\$").replace("{", r"\{").replace("}", r"\}")
             .replace(r"\textbackslash\{\}", r"\textbackslash{}").replace("^", r"\^{}").replace("~", r"\~{}"))


def _src(source: str) -> str:
    """Typeset a source description: path-like tokens as breakable \\path, the rest escaped."""
    out = []
    for tok in source.split(" "):
        core, tail = (tok[:-1], ",") if tok.endswith(",") else (tok, "")
        if "/" in core or core.endswith((".json", ".csv")):
            out.append(f"\\path{{{core}}}{tail}")
        else:
            out.append(_tex_escape(tok))
    return " ".join(out)


def render() -> None:
    gen = ROOT / "paper" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    prov = ROOT / "results" / "provenance"
    prov.mkdir(parents=True, exist_ok=True)

    lines = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{.11\textwidth}>{\raggedright\arraybackslash}p{.16\textwidth}"
             r">{\raggedright\arraybackslash}p{.22\textwidth}>{\raggedright\arraybackslash}p{.38\textwidth}p{.07\textwidth}@{}}",
             r"\caption{Provenance ledger for retained numbers outside the generated tables. Every row is re-checked by \texttt{tests/test\_provenance\_ledger.py}.}\label{tab:provenance_ledger}\\",
             r"\toprule ID & Location & Quantity & Source & Kind\\\midrule\endfirsthead",
             r"\toprule ID & Location & Quantity & Source & Kind\\\midrule\endhead"]
    for c in CLAIMS:
        lines.append(f"{_tex_escape(c.cid)} & {_tex_escape(c.where)} & {_tex_escape(c.what)} & "
                     f"{{\\footnotesize {_src(c.source)}}} & {c.kind.lower()}\\\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (gen / "provenance_ledger.tex").write_text("\n".join(lines) + "\n")

    wl = [r"\begin{itemize}\setlength\itemsep{0pt}"]
    wl += [f"\\item {_tex_escape(a)}: {_tex_escape(b)}." for a, b in WITHDRAWN]
    wl += [r"\end{itemize}"]
    (gen / "provenance_withdrawn.tex").write_text("\n".join(wl) + "\n")

    md = ["# Provenance ledger", "",
          "Generated by `scripts/provenance_ledger.py`; checked by `tests/test_provenance_ledger.py`.", "",
          "Numbers in `paper/generated/*.tex` (empirical feedback, estimator validation, feedback-dealer solvency) are",
          "written directly from `results/provenance/*.json` and are not repeated here.", "",
          "| ID | Location | Quantity | Printed | Source | Kind |", "|---|---|---|---|---|---|"]
    for c in CLAIMS:
        md.append(f"| {c.cid} | {c.where} | {c.what} | `{c.printed}` | `{c.source}` | {c.kind} |")
    md += ["", "## Withdrawn", ""] + [f"- **{a}** — {b}" for a, b in WITHDRAWN]
    (prov / "ledger.md").write_text("\n".join(md) + "\n")


def main() -> int:
    bad = check()
    for c, why, got in bad:
        print(f"FAIL {c.cid}: {why} (printed {c.printed!r}, computed {got!r})")
    render()
    print(f"{len(CLAIMS) - len(bad)}/{len(CLAIMS)} claims verified; ledger written.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
