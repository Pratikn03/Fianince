"""Tests for the A2 descriptive split on the simulated markets of test_p7s_pipeline_A1 (no network, no data)."""
import numpy as np
import pytest

import p7s_executor_A1 as ex
import p7s_pipeline_A1 as pl
import p7s_split_A2 as sp
from test_p7s_pipeline_A1 import CFG, FOLDERS, world  # noqa: F401  (fixture)


def test_groups_partition_the_registered_universe():
    uni = ("BTCUSDT, ETHUSDT, SNDKUSDT, SOLUSDT, ZECUSDT, XAUUSDT, SOXLUSDT, XRPUSDT, SKHYNIXUSDT, SPCXUSDT, CLUSDT, "
           "HYPEUSDT, XAGUSDT, KORUUSDT, MUUSDT, NEARUSDT, DOGEUSDT, BZUSDT, BNBUSDT, ENAUSDT, SUIUSDT, 1000PEPEUSDT, "
           "UNIUSDT, PUMPUSDT, WLDUSDT, ADAUSDT, CRCLUSDT, MSTRUSDT, TRUMPUSDT, LINKUSDT").split(", ")
    g = sp.groups(uni)
    assert len(g["crypto"]) == 18 and len(g["non_crypto"]) == 12
    assert sorted(g["crypto"] + g["non_crypto"]) == sorted(uni) and set(g["non_crypto"]) == set(sp.NON_CRYPTO)


def test_split_matches_direct_evaluation_on_each_group(world):  # noqa: F811
    dev_out = pl.run_development(CFG, world["arch"], FOLDERS, log=lambda *a: None, B=99)
    uni = dev_out["universe"]
    old_nc, old_min = sp.NON_CRYPTO, sp.MIN_GROUP_SYMBOLS
    sp.NON_CRYPTO, sp.MIN_GROUP_SYMBOLS = uni[:2], 2
    try:
        res = sp.run_split(CFG, world["arch"], dev_out, B=199, log=lambda *a: None)
    finally:
        sp.NON_CRYPTO, sp.MIN_GROUP_SYMBOLS = old_nc, old_min
    assert res["groups"]["non_crypto"] == uni[:2] and res["groups"]["crypto"] == uni[2:]
    # recompute the crypto group directly from the simulated arrays, as test_p7s_pipeline_A1 does for all symbols
    from test_p7s_pipeline_A1 import NAMES, BPD
    a0, n = 30 * BPD, 70 * BPD
    eval_mask = np.zeros(n, dtype=bool); eval_mask[30 * BPD:] = True
    day_id = np.clip(np.arange(n) // BPD - 30, 0, 39)
    mem = uni[2:]
    S = np.zeros((len(mem), 40, 4)); N = np.zeros_like(S); bars = []
    for j, s in enumerate(mem):
        i = NAMES.index(s)
        close = world["close"][a0:a0 + n, i]; pi = ex.proximity(world["oi"][a0:a0 + n, i])
        thr = dev_out["thresholds"][s]["primary"]
        S[j], N[j] = ex.symbol_cells(close, pi, day_id, eval_mask, thr, 40)
        bars.append(ex.symbol_bars(close, pi, eval_mask, thr))
    direct = ex.evaluate(S, N, mem, bars=bars, B=199, shift_step_days=5)
    for k in ("beta_calm_mean", "beta_stress_mean", "did", "p_h2_stress_reveals"):
        assert res["crypto"][k] == pytest.approx(direct[k], rel=1e-9, abs=1e-12)
