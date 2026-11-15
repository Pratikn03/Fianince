"""Tests for the P7S data layer and pipeline (amendment A1) on simulated markets served by a fake archive.
No network and no market data."""
import datetime as dt
import io
import zipfile

import numpy as np
import pytest

import p7s_data as pdz
import p7s_executor_A1 as ex
import p7s_pipeline_A1 as pl
import validate_p7s_A1 as sim

BPD = pdz.BARS_PER_DAY
CFG = {"name": "test", "warmup_start": "2024-01-01", "dev_start": "2024-01-31", "dev_end": "2024-02-29",
       "eval_start": "2024-03-01", "eval_end": "2024-04-09", "shift_step_days": 5, "n_universe": 5}
NAMES = ["AAAUSDT", "BBBUSDT", "CCCUSDT", "DDDUSDT", "EEEUSDT", "FFFUSDT", "GGGUSDT", "HHHUSDT"]
FOLDERS = NAMES + ["USDCUSDT", "BTCDOMUSDT", "BTCUSDT_240329", "BTCBUSD", "币安人生USDT"]


def _zip(name: str, text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(name, text)
    return buf.getvalue()


def kline_zip(day: str, close: np.ndarray, qv: float, header: bool, micro: bool = False) -> bytes:
    t0 = pdz.day_start_ms(day)
    rows = [",".join(pdz.KL_COLS)] if header else []
    qv = float(qv)
    for k, c in enumerate(close):
        c = float(c)
        o = t0 + k * pdz.BAR_MS
        stamp = o * 1000 if micro else o
        rows.append(f"{stamp},{c!r},{c!r},{c!r},{c!r},1.0,{stamp + 299999},{qv!r},10,0.5,1.0,0")
    return _zip("k.csv", "\n".join(rows) + "\n")


def metrics_zip(day: str, sym: str, oi: np.ndarray, top: np.ndarray, offset_s: int = 0) -> bytes:
    base = dt.datetime.fromisoformat(day)
    rows = ["create_time,symbol,sum_open_interest,sum_open_interest_value,count_toptrader_long_short_ratio,"
            "sum_toptrader_long_short_ratio,count_long_short_ratio,sum_taker_long_short_vol_ratio"]
    for k in range(len(oi)):
        ts = (base + dt.timedelta(minutes=5 * k, seconds=offset_s)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append(f"{ts},{sym},1.0,{float(oi[k])!r},1.0,{float(top[k])!r},1.0,1.0")
    return _zip("m.csv", "\n".join(rows) + "\n")


class FakeArchive:
    def __init__(self, files):
        self.files = files
        self.requests = 0

    def get_many(self, urls):
        self.requests += len(urls)
        return {u: self.files.get(u) for u in urls}


@pytest.fixture(scope="module")
def world():
    sim.N_SYM, sim.WARM, sim.DEV, sim.HOLD = 8, 30, 30, 40
    close, oi = sim.simulate(77, "two_layer")
    rng = np.random.default_rng(5)
    top = np.exp(0.3 * rng.standard_normal(close.shape))
    all_days = pdz.days("2024-01-01", "2024-04-09")
    assert close.shape[0] == len(all_days) * BPD
    files = {}
    for i, s in enumerate(NAMES):
        for j, d in enumerate(all_days):
            sl = slice(j * BPD, (j + 1) * BPD)
            files[pdz.kline_url(s, d)] = kline_zip(d, close[sl, i], (i + 1) * 1e6, header=(j % 2 == 0), micro=(j % 7 == 3))
            files[pdz.metrics_url(s, d)] = metrics_zip(d, s, oi[sl, i], top[sl, i], offset_s=(7 if j % 5 == 1 else 0))
    del files[pdz.metrics_url("HHHUSDT", "2024-01-10")]         # highest volume, one warm-up metrics file missing
    del files[pdz.kline_url("GGGUSDT", "2024-02-11")]           # one development kline file missing
    return {"arch": FakeArchive(files), "close": close, "oi": oi, "top": top, "days": all_days}


def test_candidate_symbols_exclusions():
    assert pdz.candidate_symbols(FOLDERS) == NAMES


def test_listing_helpers():
    key = "data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-2024-01-03.zip"
    page = ('<?xml version="1.0"?><ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
            f"<Contents><Key>{key}</Key></Contents><Contents><Key>{key}.CHECKSUM</Key></Contents></ListBucketResult>")
    assert pdz.listing_has_key(page, key) and not pdz.listing_has_key(page, key.replace("03", "04"))
    empty = '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"></ListBucketResult>'
    assert not pdz.listing_has_key(empty, key)
    assert pdz.metrics_url("BTCUSDT", "2024-01-03").endswith(key)


def test_parsers_round_trip():
    c = np.linspace(100.0, 101.0, BPD)
    k = pdz.parse_klines(kline_zip("2024-01-02", c, 5.0, header=False, micro=True))
    assert k["open_ms"].iloc[0] == pdz.day_start_ms("2024-01-02") and np.array_equal(k["close"].to_numpy(), c)
    m = pdz.parse_metrics(metrics_zip("2024-01-02", "X", c * 2, c * 0 + 1.5, offset_s=7))
    assert m["ts_ms"].iloc[1] == pdz.day_start_ms("2024-01-02") + pdz.BAR_MS
    assert np.array_equal(m["oi_value"].to_numpy(), c * 2)


def test_assemble_missing_files_and_forward_fill():
    d = ["2024-01-02", "2024-01-03"]
    c = np.linspace(100.0, 101.0, BPD)
    oi = np.full(BPD, 5.0)
    kl = {d[0]: kline_zip(d[0], c, 1.0, True), d[1]: None}
    mt = {d[0]: metrics_zip(d[0], "X", oi, oi), d[1]: None}
    a = pdz.assemble(d, kl, mt)
    assert a["missing_kline_files"] == 1 and a["missing_metrics_files"] == 1
    assert np.isfinite(a["close"][:BPD]).all() and np.isnan(a["close"][BPD:]).all()
    filled = np.isfinite(a["oi_value"][BPD:])
    assert filled[: pdz.FFILL_BARS].all() and not filled[pdz.FFILL_BARS:].any()     # filled for 30 minutes only


def test_development_universe_and_thresholds(world):
    out = pl.run_development(CFG, world["arch"], FOLDERS, log=lambda *a: None, B=99)
    assert out["universe"] == ["FFFUSDT", "EEEUSDT", "DDDUSDT", "CCCUSDT", "BBBUSDT"]
    assert out["dropped_missing_development_kline"] == ["GGGUSDT"]
    assert out["skipped_for_missing_files"] == {"HHHUSDT": {"missing_kline_files": 0, "missing_metrics_files": 1}}
    # thresholds equal a direct computation on the simulated arrays
    n = 60 * BPD
    dev_mask = np.zeros(n, dtype=bool); dev_mask[30 * BPD:] = True
    i = NAMES.index("DDDUSDT")
    direct = ex.fit_thresholds(world["close"][:n, i], ex.proximity(world["oi"][:n, i]), dev_mask)
    got = out["thresholds"]["DDDUSDT"]["primary"]
    for k in ("sigma", "sigma60", "q50", "q80", "q99", "state_lo", "state_hi"):
        assert got[k] == pytest.approx(direct[k], rel=1e-12)
    bp = out["blinded_precision_development"]
    assert not any(k in bp for k in ("did", "beta_calm_mean", "verdict", "p_h2_stress_reveals"))
    world["dev_out"] = out


def test_evaluation_matches_direct_computation(world):
    dev_out = world["dev_out"]
    res = pl.run_evaluation(CFG, world["arch"], dev_out, log=lambda *a: None, B=199)
    assert res["n_days"] == 40
    # the gate needs 20 symbols; this small universe has 5, so no statistic may be computed
    assert res["status"] == "not_evaluable" and "primary" not in res and "readout" not in res
    old = pl.MIN_SYMBOLS_GATE
    pl.MIN_SYMBOLS_GATE = 3
    try:
        res = pl.run_evaluation(CFG, world["arch"], dev_out, log=lambda *a: None, B=199)
    finally:
        pl.MIN_SYMBOLS_GATE = old
    assert res["status"] == "evaluated" and res["primary"]["verdict"] in ("supportive", "inconclusive", "inconsistent")
    assert res["readout"] == pl.readout(res["primary"])
    # direct computation from the simulated arrays: history = the 30 days before the evaluation window
    a0, n = 30 * BPD, 70 * BPD
    eval_mask = np.zeros(n, dtype=bool); eval_mask[30 * BPD:] = True
    day_id = np.clip(np.arange(n) // BPD - 30, 0, 39)
    S = np.zeros((5, 40, 4)); N = np.zeros_like(S); bars = []
    for j, s in enumerate(dev_out["universe"]):
        i = NAMES.index(s)
        close = world["close"][a0:a0 + n, i]; pi = ex.proximity(world["oi"][a0:a0 + n, i])
        thr = dev_out["thresholds"][s]["primary"]
        S[j], N[j] = ex.symbol_cells(close, pi, day_id, eval_mask, thr, 40)
        bars.append(ex.symbol_bars(close, pi, eval_mask, thr))
    direct = ex.evaluate(S, N, dev_out["universe"], bars=bars, B=199, shift_step_days=5)
    for k in ("beta_calm_mean", "beta_stress_mean", "did", "p_h2_stress_reveals"):
        assert res["primary"][k] == pytest.approx(direct[k], rel=1e-9, abs=1e-12)
    assert res["primary"]["events_per_cell_total"] == direct["events_per_cell_total"]
    assert set(res["sensitivity"]) == {"rv", "top", "volume_low", "volume_mid", "volume_high"}
    assert set(res["placebo_30_days"]) == {"state_lagged_30_days", "state_led_30_days"}


def test_evaluation_refuses_other_configuration(world):
    other = dict(CFG, eval_end="2024-04-08")
    with pytest.raises(AssertionError):
        pl.run_evaluation(other, world["arch"], world["dev_out"], log=lambda *a: None, B=99)


def test_registered_windows():
    for cfg in (pl.CFG_PRIMARY, pl.CFG_REPLICATION):
        warm = pdz.days(cfg["warmup_start"], pdz.shift_day(cfg["dev_start"], -1))
        ev = pdz.days(cfg["eval_start"], cfg["eval_end"])
        assert len(warm) == 30 and len(ev) % cfg["shift_step_days"] == 0
        assert cfg["dev_end"] < cfg["eval_start"]
    assert len(pdz.days(pl.CFG_PRIMARY["eval_start"], pl.CFG_PRIMARY["eval_end"])) == 850
    assert len(pdz.days(pl.CFG_PRIMARY["dev_start"], pl.CFG_PRIMARY["dev_end"])) == 180


def test_readout_texts():
    base = {"beta_calm_mean": 0.01, "beta_calm_ci90": [-0.02, 0.04], "did": -0.15, "p_h2_stress_reveals": 0.006, "E_margin": 0.10}
    assert "This is the pattern Section 7 predicts." in pl.readout(dict(base, verdict="supportive"))
    assert "against the calm-silence prediction" in pl.readout(dict(base, verdict="inconsistent"))
    assert "neither supports nor contradicts" in pl.readout(dict(base, verdict="inconclusive"))
