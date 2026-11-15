"""P7S pipeline, amendment A1: the development stage and the evaluation stage.

run_development : draws the universe by rule from development data, fits every threshold on development data,
                  and returns a blinded precision check (standard errors and event counts only).
run_evaluation  : the single evaluation run. It downloads first, applies a gate that uses event counts only,
                  and only then computes the statistics with p7s_executor_A1.
Both take an `arch` object with get_many(urls) -> {url: bytes or None}, so they can be tested without a network.
"""
from __future__ import annotations

import numpy as np

import p7s_data as pdz
import p7s_executor_A1 as ex

BPD = ex.BARS_PER_DAY
HISTORY_DAYS = 30            # days of history before the first development or evaluation day (for Pi)
MIN_SYMBOLS_GATE = 20        # the evaluation stops before any statistic if fewer symbols have 20 events per cell
SENS_B = 999                 # bootstrap draws for the descriptive sensitivity checks

CFG_PRIMARY = {"name": "primary_retrospective", "warmup_start": "2023-12-04", "dev_start": "2024-01-03",
               "dev_end": "2024-06-30", "eval_start": "2024-07-01", "eval_end": "2026-10-28",
               "shift_step_days": 5, "n_universe": 30}
CFG_REPLICATION = {"name": "prospective_replication", "warmup_start": "2026-07-02", "dev_start": "2026-08-01",
                   "dev_end": "2026-10-31", "eval_start": "2026-11-16", "eval_end": "2027-02-14",
                   "shift_step_days": 1, "n_universe": 30}


def _fetch(arch, sym: str, day_list: list[str], metrics: bool = True):
    ku = [pdz.kline_url(sym, d) for d in day_list]
    mu = [pdz.metrics_url(sym, d) for d in day_list] if metrics else []
    got = arch.get_many(ku + mu)
    return ({d: got[u] for d, u in zip(day_list, ku)}, {d: got[u] for d, u in zip(day_list, mu)})


def _states(arr: dict) -> tuple[np.ndarray, np.ndarray]:
    """(Pi, top-trader state). The top-trader state is |ln(top-trader long/short ratio)|."""
    pi = ex.proximity(arr["oi_value"])
    with np.errstate(invalid="ignore", divide="ignore"):
        top = np.abs(np.log(arr["top_ratio"]))
    return pi, top


def _volume_tercile(qv: np.ndarray, cuts: list[float]) -> np.ndarray:
    """0, 1, 2 for the development terciles of 5-minute quote volume; -1 where volume is missing."""
    t = np.full(len(qv), -1, dtype=np.int8)
    ok = np.isfinite(qv)
    t[ok & (qv <= cuts[0])] = 0
    t[ok & (qv > cuts[0]) & (qv <= cuts[1])] = 1
    t[ok & (qv > cuts[1])] = 2
    return t


def run_development(cfg: dict, arch, folders: list[str], log=print, B: int = SENS_B) -> dict:
    warm = pdz.days(cfg["warmup_start"], pdz.shift_day(cfg["dev_start"], -1))
    dev = pdz.days(cfg["dev_start"], cfg["dev_end"])
    assert len(warm) == HISTORY_DAYS, f"warm-up must be {HISTORY_DAYS} days, got {len(warm)}"
    all_days = warm + dev
    cands = pdz.candidate_symbols(folders)
    log(f"{len(folders)} folders listed; {len(cands)} candidate USDT perpetuals after the exclusions by name")

    # 1. screen: both files on the first warm-up day and on the last development day
    probe = [warm[0], dev[-1]]
    urls = [f(s, d) for s in cands for d in probe for f in (pdz.kline_url, pdz.metrics_url)]
    got = arch.get_many(urls)
    screened = [s for s in cands if all(got[f(s, d)] is not None for d in probe for f in (pdz.kline_url, pdz.metrics_url))]
    del got
    log(f"{len(screened)} candidates have both files on {probe[0]} and {probe[1]}")

    # 2. development quote volume; a candidate with a missing development kline file is dropped
    vol, dropped_kline = {}, []
    for i, s in enumerate(screened):
        kl, _ = _fetch(arch, s, dev, metrics=False)
        if any(v is None for v in kl.values()):
            dropped_kline.append(s)
            continue
        vol[s] = float(sum(np.nansum(pdz.parse_klines(v)["quote_volume"].to_numpy()) for v in kl.values()))
        if (i + 1) % 25 == 0:
            log(f"  development volume: {i + 1}/{len(screened)} candidates")
    ranking = sorted(vol, key=lambda s: (-vol[s], s))
    log(f"{len(ranking)} candidates have every development kline file; {len(dropped_kline)} dropped")

    # 3. walk down the ranking; a symbol enters only if every warm-up and development file exists
    universe, skipped, data = [], {}, {}
    for s in ranking:
        kl, mt = _fetch(arch, s, all_days)
        mk = sum(v is None for v in kl.values()); mm = sum(v is None for v in mt.values())
        if mk or mm:
            skipped[s] = {"missing_kline_files": mk, "missing_metrics_files": mm}
            continue
        universe.append(s); data[s] = pdz.assemble(all_days, kl, mt)
        if len(universe) == cfg["n_universe"]:
            break
    if len(universe) < cfg["n_universe"]:
        raise SystemExit(f"Only {len(universe)} symbols have complete files; the universe rule cannot be met. Stop.")
    log(f"universe of {len(universe)} fixed; {len(skipped)} higher-ranked symbols skipped for missing files")

    # 4. thresholds from development bars only
    n = len(all_days) * BPD
    dev_mask = np.zeros(n, dtype=bool); dev_mask[len(warm) * BPD:] = True
    day_id = np.clip(np.arange(n) // BPD - len(warm), 0, len(dev) - 1)
    thresholds, coverage = {}, {}
    S = np.zeros((len(universe), len(dev), 4)); N = np.zeros_like(S)
    for i, s in enumerate(universe):
        a = data[s]
        pi, top = _states(a)
        for name, sv in (("Pi", pi), ("top-trader state", top)):
            if np.isfinite(sv[dev_mask]).mean() < 0.5:
                raise SystemExit(f"{s}: {name} is defined on fewer than half of the development bars. Stop.")
        qv = a["quote_volume"][dev_mask]; qv = qv[np.isfinite(qv)]
        thresholds[s] = {"primary": ex.fit_thresholds(a["close"], pi, dev_mask),
                         "rv": ex.fit_thresholds(a["close"], pi, dev_mask, rv_normalize=True),
                         "top": ex.fit_thresholds(a["close"], top, dev_mask),
                         "volume_terciles": [float(x) for x in np.percentile(qv, [100 / 3, 200 / 3])]}
        coverage[s] = {"kline_bar_coverage": a["kline_bar_coverage"], "metrics_bar_coverage": a["metrics_bar_coverage"],
                       "pi_defined_share_dev": float(np.isfinite(pi[dev_mask]).mean())}
        S[i], N[i] = ex.symbol_cells(a["close"], pi, day_id, dev_mask, thresholds[s]["primary"], len(dev))
    precision = ex.blinded_precision(S, N, universe, B=B)
    return {"spec": "P7S", "amendment": "A1", "stage": "development", "cfg": cfg, "universe": universe,
            "development_quote_volume": {s: vol[s] for s in ranking[: max(60, cfg["n_universe"])]},
            "skipped_for_missing_files": skipped, "dropped_missing_development_kline": dropped_kline,
            "n_candidates": len(cands), "n_screened": len(screened), "thresholds": thresholds, "coverage": coverage,
            "blinded_precision_development": precision}


def run_evaluation(cfg: dict, arch, dev_out: dict, log=print, B: int = ex.B_DEFAULT) -> dict:
    universe, thresholds = dev_out["universe"], dev_out["thresholds"]
    assert dev_out["cfg"] == cfg, "development outputs belong to another configuration"
    ev = pdz.days(cfg["eval_start"], cfg["eval_end"]); n_days = len(ev); step = cfg["shift_step_days"]
    if n_days % step != 0:
        raise SystemExit(f"{n_days} evaluation days is not a multiple of the shift step {step}. Stop.")
    hist = pdz.days(pdz.shift_day(cfg["eval_start"], -HISTORY_DAYS), pdz.shift_day(cfg["eval_start"], -1))
    all_days = hist + ev
    n = len(all_days) * BPD
    eval_mask = np.zeros(n, dtype=bool); eval_mask[len(hist) * BPD:] = True
    day_id = np.clip(np.arange(n) // BPD - len(hist), 0, n_days - 1)

    # 1. download everything first; a failed download raises here, before anything is computed
    for i, s in enumerate(universe):
        _fetch(arch, s, all_days)
        if (i + 1) % 5 == 0:
            log(f"  downloaded {i + 1}/{len(universe)} symbols")

    # 2. cells and bars for every variant
    names = ("primary", "rv", "top", "volume_low", "volume_mid", "volume_high")
    S = {v: np.zeros((len(universe), n_days, 4)) for v in names}
    N = {v: np.zeros((len(universe), n_days, 4)) for v in names}
    bars = {v: [] for v in names}
    coverage = {}
    for i, s in enumerate(universe):
        kl, mt = _fetch(arch, s, all_days)
        a = pdz.assemble(all_days, kl, mt)
        del kl, mt
        pi, top = _states(a)
        thr = thresholds[s]
        coverage[s] = {"missing_kline_files": a["missing_kline_files"], "missing_metrics_files": a["missing_metrics_files"],
                       "kline_bar_coverage_eval": float(np.isfinite(a["close"][eval_mask]).mean()),
                       "pi_defined_share_eval": float(np.isfinite(pi[eval_mask]).mean())}
        for v, sv, key in (("primary", pi, "primary"), ("rv", pi, "rv"), ("top", top, "top")):
            S[v][i], N[v][i] = ex.symbol_cells(a["close"], sv, day_id, eval_mask, thr[key], n_days)
            bars[v].append(ex.symbol_bars(a["close"], sv, eval_mask, thr[key]))
        terc = _volume_tercile(a["quote_volume"], thr["volume_terciles"])
        base = bars["primary"][-1]
        for k, v in enumerate(("volume_low", "volume_mid", "volume_high")):
            S[v][i], N[v][i] = ex.symbol_cells(a["close"], pi, day_id, eval_mask & (terc == k), thr["primary"], n_days)
            bars[v].append({"resp": base["resp"], "state": base["state"],
                            "move": np.where(terc[eval_mask] == k, base["move"], 0).astype(np.int8)})

    # 3. gate on event counts only
    tot = N["primary"].sum(1)
    n_ok = int((tot >= ex.MIN_EVENTS).all(1).sum())
    out = {"spec": "P7S", "amendment": "A1", "stage": "evaluation", "cfg": cfg, "n_days": n_days,
           "coverage": coverage, "symbols_with_enough_events": n_ok,
           "events_per_symbol": {s: {c: int(x) for c, x in zip(ex.CELLS, tot[i])} for i, s in enumerate(universe)}}
    if n_ok < MIN_SYMBOLS_GATE:
        out.update({"status": "not_evaluable", "reason": f"only {n_ok} symbols have {ex.MIN_EVENTS} events in every "
                    f"cell; the gate needs {MIN_SYMBOLS_GATE}. No statistic was computed."})
        return out
    log(f"gate passed: {n_ok} symbols have at least {ex.MIN_EVENTS} events in every cell")

    # 4. statistics
    primary = ex.evaluate(S["primary"], N["primary"], universe, bars=bars["primary"], B=B, shift_step_days=step)
    sens = {}
    for v in names[1:]:
        if int((N[v].sum(1) >= ex.MIN_EVENTS).all(1).sum()) < 2:
            sens[v] = {"status": "too few symbols with enough events"}
            continue
        r = ex.evaluate(S[v], N[v], universe, bars=bars[v], B=SENS_B, shift_step_days=step)
        sens[v] = {k: r[k] for k in ("n_symbols_used", "events_per_cell_total", "beta_calm_mean", "beta_calm_ci90",
                                     "beta_stress_mean", "did", "p_h2_stress_reveals", "verdict")}
    st = primary["shift_test"]
    by = dict(zip(st["shift_days"], st["did_by_shift"]))
    out.update({"status": "evaluated", "primary": primary, "sensitivity": sens,
                "placebo_30_days": {"state_lagged_30_days": by.get(30), "state_led_30_days": by.get(n_days - 30)},
                "readout": readout(primary)})
    return out


def readout(r: dict) -> str:
    """The fixed text of amendment A1, section 6, with numbers from the results."""
    x, (a, b), d, p, e = r["beta_calm_mean"], r["beta_calm_ci90"], r["did"], r["p_h2_stress_reveals"], r["E_margin"]
    if r["verdict"] == "supportive":
        return ("In a pre-specified test on Binance perpetual futures, the response to ordinary price moves did not "
                "depend on how close open interest was to its 30-day maximum (difference "
                f"{x:.3f} standard deviations, 90% interval [{a:.3f}, {b:.3f}], inside the margin of ±{e:.2f}), and "
                f"the response to large moves did (difference-in-differences {d:.3f}, p = {p:.3f}). This is the "
                "pattern Section 7 predicts. Open interest is a proxy for proximity to position limits. The test does "
                "not identify the mechanism, and it does not test the identification theorem.")
    if r["verdict"] == "inconsistent":
        return ("In a pre-specified test on Binance perpetual futures, the response to ordinary price moves depended "
                f"on how close open interest was to its 30-day maximum (difference {x:.3f} standard deviations, at or "
                f"beyond the margin of {e:.2f}). This is against the calm-silence prediction of Section 7.")
    return ("A pre-specified test on Binance perpetual futures was inconclusive (calm difference "
            f"{x:.3f}, 90% interval [{a:.3f}, {b:.3f}]; difference-in-differences {d:.3f}, p = {p:.3f}). It neither "
            "supports nor contradicts the prediction of Section 7.")
