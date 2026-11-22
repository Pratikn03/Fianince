"""Tests for p1a_dev.py on synthetic data (no BigQuery, no Binance). Run: python test_p1a_dev.py

The end-to-end test builds four synthetic pools whose arbitrageurs close a known fraction k of the pool-CEX basis in
every block, so the three-block response is 1 - (1 - k)^3, and checks that the pipeline recovers it in both halves,
that depth matches its closed form with same-block (JIT) liquidity left out, and that the calibration runs.
"""
import io
import json
import math
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import lfilter

import p1a_dev as M


def test_pools_and_guard():
    df = M.candidate_pools()                      # asserts the five known pool addresses
    assert df.pool.is_unique and len(df) == len(df.pair.unique()) * len(M.FEES)
    for a, b in [("2024-06-01", "2024-07-02"), ("2024-07-01", "2024-08-01"), ("2023-12-31", "2024-01-02")]:
        try:
            M.sql_logs(a, b, df.pool[:3])
            raise AssertionError("window guard failed")
        except ValueError:
            pass
    try:
        M.in_dev("2025-01-01", "2025-02-01")
        raise AssertionError("window guard failed")
    except ValueError:
        pass
    return df


def test_sql_parses(df):
    import sqlglot
    for name, sql in M.queries(df.pool.tolist()):
        sqlglot.parse_one(sql, read="bigquery")
        assert "2024-07-02" not in sql and "2024-08" not in sql and "2025" not in sql, name


def _hex_words(*vals):
    return "0x" + "".join(format(v % (1 << 256), "064x") for v in vals)


def _topic(v):
    return "0x" + format(v % (1 << 256), "064x")


def test_decode():
    raw = pd.DataFrame({
        "block_number": [1, 1, 2], "log_index": [0, 1, 0], "address": ["0xABC", "0xabc", "0xabc"],
        "from_address": ["0xbot", None, None],
        "t0": [M.TOPIC_SWAP, M.TOPIC_MINT, M.TOPIC_BURN], "t2": [None, _topic(-887220), _topic(-60)],
        "t3": [None, _topic(887220), _topic(120)],
        "data": [_hex_words(-5 * 10 ** 18, 123 * 10 ** 6, 2 ** 96 * 3, 10 ** 20, -201234),
                 _hex_words(0xdead, 555, 1, 2),
                 _hex_words(444, 3, 4)]})
    ev = M.decode(raw)
    s, m, b = ev.iloc[0], ev.iloc[1], ev.iloc[2]
    assert (s.kind, s.a0, s.a1, s.sqrtp, s.liq, s.tick) == (0, -5e18, 123e6, float(2 ** 96 * 3), 1e20, -201234)
    assert (m.kind, m.amount, m.tick_lower, m.tick_upper) == (1, 555.0, -887220, 887220)
    assert (b.kind, b.amount, b.tick_lower, b.tick_upper) == (2, 444.0, -60, 120)
    assert ev.pool.tolist() == ["0xabc"] * 3


def test_pool_state():
    ev = pd.DataFrame({"block_number": [10, 10, 11, 12, 12, 12, 13], "log_index": [0, 1, 0, 0, 1, 2, 0],
                       "kind": [1, 0, 1, 1, 0, 2, 2], "sqrtp": [np.nan, 4.0, np.nan, np.nan, 5.0, np.nan, np.nan],
                       "liq": [np.nan, 100.0, np.nan, np.nan, 130.0, np.nan, np.nan],
                       "tick": [0, 5, 0, 0, 6, 0, 0], "tick_lower": [0, 0, 0, 0, 0, 0, 10],
                       "tick_upper": [10, 0, 10, 10, 0, 10, 20], "amount": [50.0, 0, 20.0, 10.0, 0, 10.0, 99.0]})
    pre, post, L, bsp, bL = M.pool_state(ev, 5, 10)
    # mint before the first swap is ignored; the mint at block 11 is in range (+20); JIT at block 12 (+10, swap
    # reports 130, then -10); the burn at block 13 is out of range (tick 6 not in [10, 20))
    assert list(bL) == [100.0, 120.0, 120.0, 120.0, 120.0], bL
    assert list(bsp) == [4.0, 4.0, 5.0, 5.0, 5.0] and np.isnan(pre[1]) and pre[4] == 4.0


def _synthetic(out, ks=(0.2, 0.3, 0.4, 0.5), seed=7):
    rng = np.random.default_rng(seed)
    n = M.WEEKS * M.WEEK // 12
    i = np.arange(n)
    ts = M.T0 + 12 * i + 6
    bn = 19_000_000 + i
    pd.DataFrame({"number": bn, "ts": ts, "base_fee_per_gas": 2e10}).to_parquet(out / "blocks.parquet")
    (out / "binance").mkdir()
    (out / "events").mkdir()
    sec = ts - 1 - M.T0
    L, B = 5e23, 5
    g = np.cumsum(rng.standard_normal((B, M.WEEKS)) * 0.5, axis=1)          # bots' activity by week
    noise_senders = np.array([f"0xnoise{j:04d}" for j in range(500)])
    rows, truth = [], {}
    pools = []
    for q, k in enumerate(ks):
        sym = f"T{q}USDT"
        c_sec = math.log(2000.0) + np.cumsum(rng.standard_normal(M.NSEC) * 1e-4)
        np.savez_compressed(out / "binance" / f"{sym}.npz", close=np.exp(c_sec).astype(np.float32),
                            active=np.ones(M.WEEKS), qv=np.full(M.WEEKS, 1e9))
        c = np.log(np.exp(c_sec[sec]).astype(np.float32).astype(float))     # what the pipeline will read
        eps = rng.standard_normal(n) * 2e-4
        p = lfilter([1.0], [1.0, -(1 - k)], k * c + eps, zi=[(1 - k) * c[0]])[0]
        prev = np.concatenate([[c[0]], p[:-1]])
        gap = c - prev
        sqrtp = np.exp(p / 2) * 2 ** 96
        a1 = L * (np.exp(p / 2) - np.exp(prev / 2))
        tick = np.floor(p / math.log(1.0001)).astype(np.int64)
        expo = rng.dirichlet(np.ones(B))
        sender = noise_senders[rng.integers(0, 500, n)].astype(object)
        arbish = np.abs(k * gap) > np.abs(eps)
        wk = (ts - M.T0) // M.WEEK
        for w in range(M.WEEKS):
            m = arbish & (wk == w)
            pr = expo * np.exp(g[:, w])
            sender[m] = np.array([f"0xbot{b}" for b in range(B)])[rng.choice(B, m.sum(), p=pr / pr.sum())]
        pool = f"0x{q + 1:040x}"
        liq = np.full(n, L)
        jit = (i % 100 == 0) if q == 0 else np.zeros(n, bool)               # JIT mint and burn around the swap
        liq[jit] += 1e23
        a1[jit] = liq[jit] * (np.exp(p[jit] / 2) - np.exp(prev[jit] / 2))
        sw = pd.DataFrame({"block_number": bn, "log_index": np.where(jit, 1, 0), "pool": pool, "kind": 0,
                           "sender": sender, "a0": -a1 / 2000.0, "a1": a1, "sqrtp": sqrtp, "liq": liq, "amount": 0.0,
                           "tick": tick, "tick_lower": 0, "tick_upper": 0})
        jm = pd.DataFrame({"block_number": bn[jit], "log_index": 0, "pool": pool, "kind": 1, "sender": "0xjit",
                           "a0": 0.0, "a1": 0.0, "sqrtp": np.nan, "liq": np.nan, "amount": 1e23, "tick": 0,
                           "tick_lower": tick[jit] - 600, "tick_upper": tick[jit] + 600})
        jb = jm.assign(log_index=2, kind=2)
        rows.append(pd.concat([sw, jm, jb]))
        truth[pool] = {"R": 1 - (1 - k) ** 3,
                       "D": [math.log(np.mean(L * np.exp(p[wk == w] / 2) * M.DEPTH_FACTOR / 1e18)) for w in range(M.WEEKS)]}
        pools.append({"pool": pool, "sym0": f"T{q}", "sym1": "USDT", "fee": 3000, "dec0": 18, "dec1": 18,
                      "bin0": sym, "bin1": None, "pair": f"T{q}/USDT"})
    ev = pd.concat(rows, ignore_index=True)
    month = pd.to_datetime(M.T0 + 12 * (ev.block_number - 19_000_000) + 6, unit="s").dt.strftime("%Y-%m")
    for mth, e in ev.groupby(month):
        e.to_parquet(out / "events" / f"{mth}.parquet")
    return pd.DataFrame(pools), truth


def test_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        pools_df, truth = _synthetic(out)
        spw = M.swap_counts(out)
        assert (spw.min(axis=1) > 50_000 - 1000).all() and M.needed_symbols(pools_df, spw) == sorted(pools_df.bin0)
        panel, arbv = M.build_panel(out, pools_df, log=lambda *a: None)
        for pool, t in truth.items():
            q = panel[panel.pool == pool]
            for col in ("R1", "R2"):
                assert abs(q[col].mean() / t["R"] - 1) < 0.05, (pool, col, q[col].mean(), t["R"])
            assert np.allclose(q.D.to_numpy(), t["D"], atol=2e-3), (pool, q.D.to_numpy()[:3], t["D"][:3])
        assert panel.C.between(0, 1).all() and (panel.median_basis_bps.abs() < 5).all()
        res = M.calibrate(out, panel, arbv)
        assert res["n_pools"] == 4 and res["n_pairs"] == 4, res
        assert res["instrument"]["corr_with_composition_within"] > 0.2, res["instrument"]
        assert "gamma" not in str(res).lower()
        return res


class _FakeJob:
    def __init__(self, sql, dry):
        self.sql, self.total_bytes_processed = sql, 123 * 10 ** 9 if dry else 0

    def result(self):
        return self

    def to_dataframe(self, create_bqstorage_client=True):
        if create_bqstorage_client:
            raise RuntimeError("storage API off")       # exercises the fallback
        if "crypto_ethereum.tokens" in self.sql:
            return pd.DataFrame({"address": [M.TOKENS["WETH"][0], M.TOKENS["USDC"][0]], "symbol": ["WETH", "USDC"],
                                 "decimals": ["18", "7"]})
        if "crypto_ethereum.blocks" in self.sql:
            return pd.DataFrame({"number": pd.array([3, 1, 2], dtype="Int64"), "ts": pd.array([30, 10, 20], dtype="Int64"),
                                 "base_fee_per_gas": pd.array([1, 2, None], dtype="Int64")})
        return pd.DataFrame({"block_number": [5], "log_index": [0], "address": ["0xPOOL"], "t0": [M.TOPIC_SWAP],
                             "t2": [None], "t3": [None], "data": [_hex_words(1, -1, 2 ** 96, 10, 0)],
                             "from_address": ["0xBOT"]})


class _FakeClient:
    def __init__(self):
        self.caps = []

    def query(self, sql, job_config=None):
        dry = bool(getattr(job_config, "dry_run", False))
        if not dry:
            self.caps.append(job_config.maximum_bytes_billed)
        return _FakeJob(sql, dry)


def test_extract_mocked():
    try:
        import google.cloud.bigquery  # noqa: F401
    except ImportError:
        print("  (google-cloud-bigquery not installed here; extract test skipped)")
        return
    with tempfile.TemporaryDirectory() as d:
        pools = M.candidate_pools().pool.tolist()[:5]
        cl = _FakeClient()
        est = json.loads(json.dumps(M.estimate(cl, pools)))        # as the notebook stores it
        M.extract(cl, d, pools, est, log=lambda *a: None)
        assert all(c == int(123e9 * 1.05) + 10 ** 9 for c in cl.caps) and len(cl.caps) == 8
        b = pd.read_parquet(Path(d) / "blocks.parquet")
        assert b.number.tolist() == [1, 2, 3] and b.ts.dtype == np.int64
        ev = M.load_events(d)
        assert len(ev) == 6 and set(ev.sender.astype(str)) == {"0xbot"} and set(ev.pool.astype(str)) == {"0xpool"}
        bad = M.check_tokens(d)
        assert "USDC: decimals 7 in BigQuery, 6 here" in bad and not any(x.startswith("WETH") for x in bad), bad
        assert sum("not in the token table" in x for x in bad) == len(M.TOKENS) - 2
        print("  mocked BigQuery extraction: ok")


def _zip_csv(rows, name="X-1s.csv"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, "\n".join(",".join(str(v) for v in r) for r in rows))
    return buf.getvalue()


def test_binance_mocked():
    calls = []

    def fake(url, tries=4):
        calls.append(url)
        if "/monthly/" in url and "2024-02" in url:
            return None                                           # forces the daily fallback for February
        if "/daily/" in url:
            day = url.rsplit("-1s-", 1)[1][:10]
            t = int(pd.Timestamp(day, tz="UTC").timestamp())
            return _zip_csv([[t * 1000, 1, 1, 1, 5.0, 1, 0, 7.0, 3, 0, 0, 0]]) if day == "2024-02-10" else None
        m = url.rsplit("-1s-", 1)[1][:7]
        t = int(pd.Timestamp(m + "-01", tz="UTC").timestamp())
        unit = 1_000_000 if m == "2024-06" else 1000              # a file in microseconds is handled too
        return _zip_csv([["open_time", "o", "h", "l", "c", "v", "ct", "qv", "n", "a", "b", "i"],
                         [t * unit, 1, 1, 1, 2.0, 1, 0, 10.0, 4, 0, 0, 0],
                         [(t + 2) * unit, 1, 1, 1, 3.0, 1, 0, 10.0, 0, 0, 0, 0]])

    orig = M._download
    M._download = fake
    try:
        with tempfile.TemporaryDirectory() as d:
            M.binance(["XUSDT"], d, log=lambda *a: None)
            z = M.load_binance(d, "XUSDT")
            c = z["close"]
            assert c[0] == 2.0 and c[1] == 2.0 and c[2] == 3.0 and c[3] == 3.0              # forward fill
            feb10 = int(pd.Timestamp("2024-02-10", tz="UTC").timestamp()) - M.T0
            jun1 = int(pd.Timestamp("2024-06-01", tz="UTC").timestamp()) - M.T0
            assert c[feb10] == 5.0 and c[jun1] == 2.0 and c[jun1 + 2] == 3.0
            assert sum("/daily/" in u for u in calls) == 29 and all("2024-07" not in u for u in calls)
            print("  mocked Binance download: ok")
    finally:
        M._download = orig


if __name__ == "__main__":
    df = test_pools_and_guard()
    test_sql_parses(df)
    test_decode()
    test_pool_state()
    test_extract_mocked()
    test_binance_mocked()
    res = test_end_to_end()
    print("all tests passed")
    print({k: res[k] for k in ("n_pools", "n_pairs", "reliability", "instrument", "depth")})
