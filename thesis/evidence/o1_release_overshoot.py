"""Test O1 (DRAFT, NOT REGISTERED): do small perpetuals overshoot after scheduled US macro releases?

Designed after the exploratory Pilot 2b (Chapter 5, Exploration after the tests): on the 56 CPI, Employment Situation and
FOMC releases of January 2025 to October 2026, 30 small USD-M perpetuals absorbed a median 94% of bitcoin's release-second
move within ten seconds, and the point estimates of the 120-second area A_120 were negative (the response above its
long-run level) in 26 of 30 symbols, though individually significant in only 2. All symbols share the same releases, so
those 26 are not independent findings. O1 asks the question once, pooled across symbols with the releases resampled
jointly, on the 2022-2024 releases, which the pilot did not use. It will be registered only after the author approves
the specification; until then gate() refuses to run.

Releases (95 dates, 96 events): every CPI and Employment Situation release (8:30 ET) and every FOMC statement (2:00 ET)
in 2022, 2023 and 2024, from the BLS release calendars (https://www.bls.gov/schedule/2022/home.htm, .../2023/...,
.../2024/...) and the Federal Reserve's FOMC calendar (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm;
no unscheduled meetings or notation votes in these years). On 2024-06-12 CPI and the FOMC statement are both events.
Symbols: the 30 perpetuals of the pilot (the design was fixed on them); a symbol is evaluable with at least 40 usable
releases (bitcoin one-second klines and the perpetual's aggTrades in the +-30-minute window). Void if fewer than 15.

Per symbol s (the pilot's estimator, unchanged): shock e_k = p^B(tau_k + 10 s) - p^B(tau_k - 1 s); response
p^A(tau_k + j) - p^A(tau_k - 1) = c_j + b_j e_k + d_j [p^B(tau_k + j) - p^B(tau_k + 10)] + error, j = 0..900 s;
beta_s = mean b_j over [600, 900]; G_j = 1 - b_j / beta_s; A_H(s) = sum_{j=10}^{10+H-1} G_j (seconds).
Pooled: Abar_H = mean over evaluable symbols of A_H(s). Joint event bootstrap: each draw resamples the release list with
replacement and applies the same draw to every symbol (2,000 draws, seed 20261102), so the shared releases are respected.

Validity conditions (registered; the test is void if either fails):
    V1 the pooled pre-release drift, mean over symbols of slope(p^A(tau-1) - p^A(tau-301) on e_k) / beta_s, has a 95%
       joint-bootstrap interval covering zero;
    V2 at pseudo-events 20 minutes before each release, the standard deviation of bitcoin's 11-second move is below half
       of that at the releases (median over symbols).
Primary: the response overshoots its long-run level: the one-sided upper 95% joint-bootstrap bound of Abar_120 is below
    zero (equivalently p < 0.05).
Secondary: Abar_30, Abar_60, Abar_300 with intervals; Abar_120 by release type (CPI, Employment Situation, FOMC);
    per-symbol counts with A_120 < 0 and with interval below zero; the two-sided certification count |A_120| < 60 s;
    median share through at 10 s and median beta; the number of symbols whose memories are identified (pilot rule).
What is not shown: an overshoot measured from last-trade prices could partly reflect aggressive trading at the ask or bid
right after the release; a pass establishes a pooled transient response above the long-run level, not its mechanism.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot2b_announcements as P  # noqa: E402  (download and estimator of the pilot, unchanged)

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/O1_release_overshoot.json"
COUNTER = THESIS / "checks/prereg/O1_unlock.json"
RESULT = HERE / "O1_results.json"
NUMBERS = THESIS / "checks/O1_numbers.tex"
DLLOG = HERE / "O1_download_log.json"

CPI = ["2022-01-12", "2022-02-10", "2022-03-10", "2022-04-12", "2022-05-11", "2022-06-10", "2022-07-13", "2022-08-10",
       "2022-09-13", "2022-10-13", "2022-11-10", "2022-12-13",
       "2023-01-12", "2023-02-14", "2023-03-14", "2023-04-12", "2023-05-10", "2023-06-13", "2023-07-12", "2023-08-10",
       "2023-09-13", "2023-10-12", "2023-11-14", "2023-12-12",
       "2024-01-11", "2024-02-13", "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12", "2024-07-11", "2024-08-14",
       "2024-09-11", "2024-10-10", "2024-11-13", "2024-12-11"]
NFP = ["2022-01-07", "2022-02-04", "2022-03-04", "2022-04-01", "2022-05-06", "2022-06-03", "2022-07-08", "2022-08-05",
       "2022-09-02", "2022-10-07", "2022-11-04", "2022-12-02",
       "2023-01-06", "2023-02-03", "2023-03-10", "2023-04-07", "2023-05-05", "2023-06-02", "2023-07-07", "2023-08-04",
       "2023-09-01", "2023-10-06", "2023-11-03", "2023-12-08",
       "2024-01-05", "2024-02-02", "2024-03-08", "2024-04-05", "2024-05-03", "2024-06-07", "2024-07-05", "2024-08-02",
       "2024-09-06", "2024-10-04", "2024-11-01", "2024-12-06"]
FOMC = ["2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
        "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
        "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18"]
SOURCES = {"CPI and Employment Situation": "https://www.bls.gov/schedule/2022/home.htm, https://www.bls.gov/schedule/2023/home.htm, "
           "https://www.bls.gov/schedule/2024/home.htm (8:30 a.m. ET)",
           "FOMC": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (statement at 2:00 p.m. ET)"}
SYMBOLS = list(P.SYMBOLS)
SEED, B_JOINT, MIN_EVENTS, MIN_SYMBOLS, ALPHA = 20261102, 2000, 40, 15, 0.05
H_MAIN, AREA_H = 120, (30, 60, 120, 300)


def use_o1_events():
    P.CPI, P.NFP, P.FOMC = CPI, NFP, FOMC
    P.SOURCES = SOURCES
    return P.events()


def design_ts(evs, btc, alt, at=0):
    """The pilot's design arrays, with the release timestamps kept so that a joint bootstrap can align symbols."""
    out = {"E": [], "Y": [], "F": [], "PRE": [], "kind": [], "ts": []}
    c = P.WIN + at
    for e in evs:
        if e["ts"] not in btc or e["ts"] not in alt:
            continue
        pb = np.log(btc[e["ts"]]) * 1e4; pa = np.log(alt[e["ts"]][0]) * 1e4
        if c + P.J >= len(pb) or c - 301 < 0:
            continue
        f = pb[c:c + P.J + 1] - pb[c + P.SHOCK]; f[:P.SHOCK + 1] = 0.0
        out["E"].append(pb[c + P.SHOCK] - pb[c - 1]); out["Y"].append(pa[c:c + P.J + 1] - pa[c - 1]); out["F"].append(f)
        out["PRE"].append(pa[c - 1] - pa[c - 301]); out["kind"].append(e["kind"]); out["ts"].append(e["ts"])
    return {k: (np.array(v) if k not in ("kind",) else v) for k, v in out.items()}


def areas(b):
    beta = b[P.PLATEAU[0]:P.PLATEAU[1] + 1].mean(); G = 1 - b / beta
    return beta, G, {H: float(G[P.SHOCK:P.SHOCK + H].sum()) for H in AREA_H}


def wslope(x, y, w):
    if w.sum() < 3:
        return np.nan
    xm, ym = (w @ x) / w.sum(), (w @ y) / w.sum()
    d = w @ ((x - xm) ** 2)
    return float(w @ ((x - xm) * (y - ym)) / d) if d > 0 else np.nan


def evaluate(evs, btc, alts, nb=B_JOINT):
    D = {s: design_ts(evs, btc, alts[s]) for s in alts}
    ev_syms = [s for s in alts if len(D[s]["E"]) >= MIN_EVENTS]
    out = {"n_events_listed": len(evs), "n_btc_windows": len(btc),
           "usable_events": {s: int(len(D[s]["E"])) for s in alts}, "evaluable": ev_syms,
           "void_symbols": len(ev_syms) < MIN_SYMBOLS}
    if out["void_symbols"]:
        return out
    ts_all = np.array(sorted({t for s in ev_syms for t in D[s]["ts"]})); n = len(ts_all)
    pos = {s: np.searchsorted(ts_all, D[s]["ts"]) for s in ev_syms}
    kinds = {e["ts"]: e["kind"] for e in evs}
    per = {}
    for s in ev_syms:
        d = D[s]; b = P.lp(d["E"], d["Y"], d["F"]); beta, G, A = areas(b)
        per[s] = {"n_events": int(len(d["E"])), "beta": float(beta), "p0": float(b[P.SHOCK] / beta), "A": A,
                  "pre_over_beta": wslope(d["E"], d["PRE"], np.ones(len(d["E"]))) / beta,
                  "by_kind": {}}
        for k in ("CPI", "NFP", "FOMC"):
            m = np.array([x == k for x in d["kind"]])
            if m.sum() >= 10:
                bk = P.lp(d["E"][m], d["Y"][m], d["F"][m]); per[s]["by_kind"][k] = areas(bk)[2][H_MAIN]
        Dp = design_ts(evs, btc, alts[s], at=-P.PSEUDO)
        per[s]["pseudo_shock_sd_ratio"] = float(np.std(Dp["E"]) / np.std(d["E"])) if len(Dp["E"]) > 5 else np.nan
    pooled = {H: float(np.mean([per[s]["A"][H] for s in ev_syms])) for H in AREA_H}
    pre_pool = float(np.nanmean([per[s]["pre_over_beta"] for s in ev_syms]))
    rng = np.random.default_rng(SEED)
    draws = {H: [] for H in AREA_H}; draws["pre"] = []; per_draw_A = {s: [] for s in ev_syms}
    kind_draws = {k: [] for k in ("CPI", "NFP", "FOMC")}
    for _ in range(nb):
        cnt = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        As, pres, kk = {H: [] for H in AREA_H}, [], {k: [] for k in kind_draws}
        for s in ev_syms:
            d = D[s]; w = cnt[pos[s]]
            if w.sum() < 10:
                continue
            bb = P.lp(d["E"], d["Y"], d["F"], w); be, _, Ab = areas(bb)
            for H in AREA_H:
                As[H].append(Ab[H])
            per_draw_A[s].append(Ab[H_MAIN])
            pres.append(wslope(d["E"], d["PRE"], w) / be)
            for k in kk:
                m = np.array([x == k for x in d["kind"]]) & (w > 0)
                if m.sum() >= 10:
                    kk[k].append(areas(P.lp(d["E"][m], d["Y"][m], d["F"][m], w[m]))[2][H_MAIN])
        for H in AREA_H:
            draws[H].append(np.mean(As[H]))
        draws["pre"].append(np.nanmean(pres))
        for k in kk:
            if kk[k]:
                kind_draws[k].append(np.mean(kk[k]))
    q = lambda v, a, b_: [float(np.quantile(v, a)), float(np.quantile(v, b_))]
    upper = float(np.quantile(draws[H_MAIN], 1 - ALPHA)); p_one = float(np.mean(np.array(draws[H_MAIN]) >= 0))
    v1 = q(draws["pre"], 0.025, 0.975); v1_ok = bool(v1[0] <= 0 <= v1[1])
    v2_val = float(np.nanmedian([per[s]["pseudo_shock_sd_ratio"] for s in ev_syms])); v2_ok = bool(v2_val < 0.5)
    sym_ci = {s: q(per_draw_A[s], 0.025, 0.975) for s in ev_syms}
    out.update({
        "n_symbols": len(ev_syms), "n_releases_used": int(n),
        "validity": {"V1_pooled_pre_over_beta": pre_pool, "V1_ci": v1, "V1_ok": v1_ok,
                     "V2_median_pseudo_shock_sd_ratio": v2_val, "V2_ok": v2_ok},
        "void": not (v1_ok and v2_ok),
        "pooled_A": pooled, "pooled_A_ci": {str(H): q(draws[H], 0.025, 0.975) for H in AREA_H},
        "primary": {"Abar_120": pooled[H_MAIN], "upper95_one_sided": upper, "p_one_sided": p_one,
                    "pass": bool(v1_ok and v2_ok and upper < 0)},
        "secondary": {
            "by_kind_Abar_120": {k: {"point": float(np.mean([per[s]["by_kind"][k] for s in ev_syms if k in per[s]["by_kind"]]))
                                     if any(k in per[s]["by_kind"] for s in ev_syms) else None,
                                     "ci": q(kind_draws[k], 0.025, 0.975) if len(kind_draws[k]) > 20 else None}
                              for k in kind_draws},
            "symbols_A120_negative": int(sum(per[s]["A"][H_MAIN] < 0 for s in ev_syms)),
            "symbols_A120_ci_below_zero": int(sum(sym_ci[s][1] < 0 for s in ev_syms)),
            "symbols_two_sided_certified_60s": int(sum(-60 < sym_ci[s][0] and sym_ci[s][1] < 60 for s in ev_syms)),
            "median_share_at_10s": float(np.median([per[s]["p0"] for s in ev_syms])),
            "median_beta": float(np.median([per[s]["beta"] for s in ev_syms]))},
        "per_symbol": {s: {**per[s], "A120_ci": sym_ci[s], "A": {str(H): v for H, v in per[s]["A"].items()}} for s in ev_syms}})
    return out


def identified_count(evs, btc, alts, ev_syms):
    """Pilot identification rule per symbol (secondary; per-symbol bootstrap as in the pilot)."""
    c = 0
    for j, s in enumerate(ev_syms):
        r = P.symbol_pilot(evs, btc, alts[s], j, nb=300)
        c += bool(r.get("identification", {}).get("identified"))
    return c


def numbers_tex(r):
    if r.get("void_symbols") or r.get("void"):
        return "% generated by o1_release_overshoot.py\n\\newcommand{\\OoneVoid}{void}\n"
    p = r["primary"]
    L = ["% generated by o1_release_overshoot.py; do not edit",
         f"\\newcommand{{\\OoneSymbols}}{{{r['n_symbols']}}}\\newcommand{{\\OoneReleases}}{{{r['n_releases_used']}}}",
         f"\\newcommand{{\\OoneAbar}}{{{p['Abar_120']:.1f}}}\\newcommand{{\\OoneUpper}}{{{p['upper95_one_sided']:.1f}}}",
         f"\\newcommand{{\\OoneP}}{{{p['p_one_sided']:.3f}}}",
         f"\\newcommand{{\\OoneVerdict}}{{{'passed' if p['pass'] else 'failed'}}}"]
    return "\n".join(L) + "\n"


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test O1 is a draft and is not registered; it cannot be run"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in (("o1_sha256", "o1_release_overshoot.py"), ("pilot2b_sha256", "pilot2b_announcements.py"),
                   ("binance_vision_sha256", "binance_vision.py")):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(cache_dir, threads=8, resume=False, skip_gate=False):
    spec, sha, reg = gate(skip_gate)
    if not skip_gate:
        c = json.loads(COUNTER.read_text())
        if resume:
            assert c["opens"] == 1, "nothing to resume"
        else:
            assert c["opens"] == 0, "Test O1 was already opened; it runs once"
            COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                           "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    use_o1_events()
    evs, btc, alts = P.download(cache_dir, SYMBOLS, threads)
    res = evaluate(evs, btc, alts)
    if not res.get("void_symbols"):
        res["secondary"]["identified"] = identified_count(evs, btc, alts, res["evaluable"])
    res = {"test": "O1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "events": evs, **res}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res))
    DLLOG.write_text(json.dumps(P.DL_LOG, indent=0) + "\n")
    print(json.dumps({k: res[k] for k in ("n_symbols", "validity", "void", "pooled_A", "primary", "secondary") if k in res},
                     indent=1, default=float))
    return res


def selftest():
    """Synthetic releases: an overshoot must pass, a monotone catch-up must fail, and the gate must refuse."""
    evs = use_o1_events(); rng = np.random.default_rng(5)
    T = 2 * P.WIN + 1; c = P.WIN; j = np.arange(T) - c

    def world(overshoot):
        btc, alts = {}, {s: {} for s in SYMBOLS[:16]}
        for e in evs:
            jump = rng.normal(0, 25); pb = np.cumsum(rng.normal(0, 0.5, T)); pb[c:] += jump
            btc[e["ts"]] = 1e4 * np.exp(pb / 1e4)
            for s in alts:
                beta = 1.4
                resp = np.where(j < 0, 0.0, 1 - np.exp(-np.maximum(j, 0) / 3.0))
                if overshoot:
                    resp = resp + 0.35 * np.where(j < 0, 0.0, np.exp(-np.maximum(j, 0) / 120.0) - np.exp(-np.maximum(j, 0) / 3.0))
                pa = np.cumsum(rng.normal(0, 1.0, T)) + beta * jump * resp
                alts[s][e["ts"]] = (100 * np.exp(pa / 1e4), np.ones(T))
        return btc, alts
    for ov, expect in ((True, True), (False, False)):
        btc, alts = world(ov)
        r = evaluate(evs, btc, alts, nb=200)
        print(json.dumps({"overshoot": ov, "n_symbols": r["n_symbols"], "validity": r["validity"], "primary": r["primary"],
                          "neg": r["secondary"]["symbols_A120_negative"]}, default=float))
        assert r["n_symbols"] == 16 and r["primary"]["pass"] is expect, ("selftest", ov, r["primary"])
    assert numbers_tex(r).startswith("%")
    try:
        gate()
        raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
