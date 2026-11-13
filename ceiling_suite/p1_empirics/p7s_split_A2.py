"""P7S amendment A2: a descriptive split of the prospective replication by underlying asset (crypto vs non-crypto).

Registered before the replication's evaluation window opens (16 November 2026). Descriptive only: the
replication's verdict is the A1 verdict on all 30 symbols, unchanged. This module computes the A1 primary
statistic (same cells, bars, bootstrap and shift test) on each group separately. It reuses the frozen A1 code and
changes none of it; downloads come from the same archive cache as the evaluation.

The groups are fixed by name from the replication universe printed by the development stage
(results/p7s_rep_dev_printed_output.txt). NON_CRYPTO: perpetuals whose underlying is an equity, an exchange-traded
fund or a commodity, including equities of crypto-related firms (CRCL, MSTR).
"""
from __future__ import annotations

import numpy as np

import p7s_data as pdz
import p7s_executor_A1 as ex
import p7s_pipeline_A1 as pl

NON_CRYPTO = ["SNDKUSDT", "XAUUSDT", "SOXLUSDT", "SKHYNIXUSDT", "SPCXUSDT", "CLUSDT", "XAGUSDT", "KORUUSDT",
              "MUUSDT", "BZUSDT", "CRCLUSDT", "MSTRUSDT"]
REP_DEV_OUTPUTS_SHA256 = "f8a453ca1a196c6f18cc60df6f2cf85b505531fdbb9462b637266216855f8587"
MIN_GROUP_SYMBOLS = 5        # a group with fewer symbols with 20 events per cell is reported as too small


def groups(universe: list[str]) -> dict:
    nc = [s for s in universe if s in NON_CRYPTO]
    return {"crypto": [s for s in universe if s not in NON_CRYPTO], "non_crypto": nc}


def run_split(cfg: dict, arch, dev_out: dict, B: int = pl.SENS_B, log=print) -> dict:
    universe, thresholds = dev_out["universe"], dev_out["thresholds"]
    assert dev_out["cfg"] == cfg, "development outputs belong to another configuration"
    ev = pdz.days(cfg["eval_start"], cfg["eval_end"]); n_days = len(ev); step = cfg["shift_step_days"]
    hist = pdz.days(pdz.shift_day(cfg["eval_start"], -pl.HISTORY_DAYS), pdz.shift_day(cfg["eval_start"], -1))
    all_days = hist + ev
    n = len(all_days) * pl.BPD
    eval_mask = np.zeros(n, dtype=bool); eval_mask[len(hist) * pl.BPD:] = True
    day_id = np.clip(np.arange(n) // pl.BPD - len(hist), 0, n_days - 1)
    S = np.zeros((len(universe), n_days, 4)); N = np.zeros_like(S); bars = []
    for i, s in enumerate(universe):                         # the A1 primary variant, exactly as in run_evaluation
        kl, mt = pl._fetch(arch, s, all_days)
        a = pdz.assemble(all_days, kl, mt)
        pi, _ = pl._states(a)
        thr = thresholds[s]["primary"]
        S[i], N[i] = ex.symbol_cells(a["close"], pi, day_id, eval_mask, thr, n_days)
        bars.append(ex.symbol_bars(a["close"], pi, eval_mask, thr))
    out = {"spec": "P7S", "amendment": "A2", "stage": "replication_split_descriptive", "cfg": cfg,
           "groups": groups(universe), "note": "Descriptive. The replication verdict is the A1 verdict on all symbols."}
    for g, members in out["groups"].items():
        idx = [universe.index(s) for s in members]
        n_ok = int((N[idx].sum(1) >= ex.MIN_EVENTS).all(1).sum()) if idx else 0
        if n_ok < MIN_GROUP_SYMBOLS:
            out[g] = {"status": f"too small: {n_ok} symbols with {ex.MIN_EVENTS} events in every cell"}
            continue
        r = ex.evaluate(S[idx], N[idx], members, bars=[bars[k] for k in idx], B=B, shift_step_days=step)
        out[g] = {k: r[k] for k in ("n_symbols_used", "symbols_excluded", "events_per_cell_total", "beta_calm_mean",
                                    "beta_calm_ci90", "beta_calm_ci95", "beta_stress_mean", "did", "did_ci95",
                                    "p_h2_stress_reveals")}
        log(f"{g}: {r['n_symbols_used']} symbols | calm {r['beta_calm_mean']:.4f} | DiD {r['did']:.4f} "
            f"[{r['did_ci95'][0]:.4f}, {r['did_ci95'][1]:.4f}] | shift-test p {r['p_h2_stress_reveals']:.3f}")
    return out
