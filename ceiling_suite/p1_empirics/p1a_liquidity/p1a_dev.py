"""P1A development window: extraction and calibration for the draft liquidity test (not registered).

Runs in Google Colab under the first author's Google account; the free BigQuery sandbox is enough. It reads only the
development window, 2024-01-01 to 2024-06-30. Every query and every download is checked against that window, and
anything later is refused. It computes what the power simulation needs (step 2 of section 7 in
P1A_liquidity_spec_DRAFT.md). On purpose, it computes no estimate of composition's effect on depth, so the test's
outcome is not previewed.

Stages. Each writes to OUT and is skipped when its output exists, so a disconnected session resumes where it stopped.
  candidate_pools()       Uniswap v3 pool addresses for the candidate pairs, by CREATE2 (no query)
  estimate(client, ...)   dry runs: the bytes each query would scan (no cost)
  extract(client, ...)    block timestamps, then the Swap/Mint/Burn logs of the candidate pools with each transaction's
                          sender, month by month; each query is capped by maximum_bytes_billed; decoded at once
  needed_symbols(...)     the Binance symbols of the pools that pass the swap-count floor
  binance(...)            one-second klines of those symbols from data.binance.vision
  build_panel(...)        pool-week measures: response halves R1 and R2, composition C, depth D, controls, instrument Z
  calibrate(...)          the power simulation's inputs, written to calibration.json
"""
import hashlib
import io
import json
import math
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------
# The window. 2024-01-01 is a Monday, so the window is 26 whole weeks.
DEV_START, DEV_END = "2024-01-01", "2024-07-01"          # end exclusive
T0, T1 = 1704067200, 1719792000                           # the same instants in Unix seconds
NSEC, WEEK, WEEKS = T1 - T0, 7 * 86400, 26
MONTHS = [("2024-01-01", "2024-02-01"), ("2024-02-01", "2024-03-01"), ("2024-03-01", "2024-04-01"),
          ("2024-04-01", "2024-05-01"), ("2024-05-01", "2024-06-01"), ("2024-06-01", "2024-07-01")]
EXPOSURE_WEEKS = 13            # instrument exposures from weeks 1-13; its first stage is measured on weeks 14-26

# Provisional floors for the exploration. The registered values are fixed after it.
MIN_SWAPS_WEEK = 100           # swaps in every one of the 26 weeks
MIN_ACTIVE_SHARE = 0.90        # share of seconds in which each Binance leg trades (the spec's floor)
MAX_MEDIAN_BASIS_BPS = 50.0    # data check: a token or decimals mismatch shows up as a huge constant basis
VOLUME_FLOORS_USD = (1e6, 5e6, 20e6)   # median weekly volume; counts reported at each, the first one used
WINSOR = (1.0, 99.0)           # the basis is winsorized at these percentiles within each pool-week-half
N_BOTS = 50                    # senders used in the shift-share instrument
DEPTH_BAND = 0.01              # depth within +-1% of the pool price

# Uniswap v3 on Ethereum mainnet
FACTORY = "1f98431c8ad98523631ae4a59f267346ea31f984"
INIT_CODE_HASH = "e34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54"
FEES = (100, 500, 3000, 10000)
TOPIC_SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"  # Swap(address,address,int256,int256,uint160,uint128,int24)
TOPIC_MINT = "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"  # Mint(address,address,int24,int24,uint128,uint256,uint256)
TOPIC_BURN = "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"  # Burn(address,int24,int24,uint128,uint256,uint256)
KNOWN_POOLS = {("USDC", "WETH", 500): "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
               ("USDC", "WETH", 3000): "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",
               ("WBTC", "WETH", 3000): "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed",
               ("WETH", "USDT", 500): "0x11b815efb8f581194ae79006d24e0d814b7697f6",
               ("WBTC", "WETH", 500): "0x4585fe77225b41b697c938b018e2ac67ac5a20c0"}
DATASET = "bigquery-public-data.crypto_ethereum"
BUDGET_BYTES = 950 * 10 ** 9   # below the sandbox's free 1 TB a month
BINANCE_URL = "https://data.binance.vision/data/spot/monthly/klines/{s}/1s/{s}-1s-{m}.zip"
BINANCE_DAILY_URL = "https://data.binance.vision/data/spot/daily/klines/{s}/1s/{s}-1s-{d}.zip"

# Candidate tokens: symbol -> (mainnet address, decimals, Binance spot symbol; None means USDT itself, price 1).
# Tokens that migrated or merged during 2024-2026 (MATIC, RNDR, OCEAN, AGIX) are left out so the pool list can be
# reused on the test window. A wrong address only yields pools without events; a wrong decimals value is caught by
# the median-basis check.
QUOTES = ("WETH", "USDC", "USDT", "WBTC")
TOKENS = {
    "WETH": ("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", 18, "ETHUSDT"),
    "USDC": ("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 6, "USDCUSDT"),
    "USDT": ("0xdac17f958d2ee523a2206206994597c13d831ec7", 6, None),
    "WBTC": ("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", 8, "BTCUSDT"),
    "LINK": ("0x514910771af9ca656af840dff83e8264ecf986ca", 18, "LINKUSDT"),
    "UNI": ("0x1f9840a85d5af5bf1d1762f925bdaddc4201f984", 18, "UNIUSDT"),
    "AAVE": ("0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9", 18, "AAVEUSDT"),
    "MKR": ("0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2", 18, "MKRUSDT"),
    "LDO": ("0x5a98fcbea516cf06857215779fd812ca3bef1b32", 18, "LDOUSDT"),
    "PEPE": ("0x6982508145454ce325ddbe47a25d4ec3d2311933", 18, "PEPEUSDT"),
    "SHIB": ("0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce", 18, "SHIBUSDT"),
    "CRV": ("0xd533a949740bb3306d119cc777fa900ba034cd52", 18, "CRVUSDT"),
    "SNX": ("0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f", 18, "SNXUSDT"),
    "COMP": ("0xc00e94cb662c3520282e6f5717214004a7f26888", 18, "COMPUSDT"),
    "ENS": ("0xc18360217d8f7ab5e7c516566761ea12ce7f9d72", 18, "ENSUSDT"),
    "GRT": ("0xc944e90c64b2c07662a292be6244bdf05cda44a7", 18, "GRTUSDT"),
    "1INCH": ("0x111111111117dc0aa78b770fa6a738034120c302", 18, "1INCHUSDT"),
    "APE": ("0x4d224452801aced8b2f0aebe155379bb5d594381", 18, "APEUSDT"),
    "SUSHI": ("0x6b3595068778dd592e39a122f4f5a5cf09c90fe2", 18, "SUSHIUSDT"),
    "FET": ("0xaea46a60368a7bd060eec7df8cba43b7ef41ad85", 18, "FETUSDT"),
    "IMX": ("0xf57e7e7c23978c3caec3c3548e3d615c346e79ff", 18, "IMXUSDT"),
    "BLUR": ("0x5283d291dbcf85356a21ba090e6db59121208b44", 18, "BLURUSDT"),
    "WLD": ("0x163f8c2467924be0ae7b5347228cabf260318753", 18, "WLDUSDT"),
    "ARB": ("0xb50721bcf8d664c30412cfbc6cf7a15145234ad1", 18, "ARBUSDT"),
    "ENA": ("0x57e114b691db790c35207b2e685d4a43181e6061", 18, "ENAUSDT"),
    "ETHFI": ("0xfe0c30065b384f05761f15d0cc899d4f9f9cc0eb", 18, "ETHFIUSDT"),
    "STRK": ("0xca14007eff0db1f8135f4c25b34de49ab0d42766", 18, "STRKUSDT"),
    "PENDLE": ("0x808507121b80c02388fad14726482e061b8da827", 18, "PENDLEUSDT"),
    "FLOKI": ("0xcf0c122c6b73ff809c693db761e7baebe62b6a2e", 9, "FLOKIUSDT"),
    "INJ": ("0xe28b3b32b6c345a34ff64674606124dd5aceca30", 18, "INJUSDT"),
    "MANA": ("0x0f5d2fb29fb7d3cfee444a200298f468908cc942", 18, "MANAUSDT"),
    "SAND": ("0x3845badade8e6dff049820680d1f14bd3903a5d0", 18, "SANDUSDT"),
    "AXS": ("0xbb0e17ef65f82ab018d8edd776e8dd940327b28b", 18, "AXSUSDT"),
    "CHZ": ("0x3506424f91fd33084466f402d5d97f05f8e3b4af", 18, "CHZUSDT"),
    "LRC": ("0xbbbbca6a901c926f240b89eacb641d8aec7aeafd", 18, "LRCUSDT"),
    "BAT": ("0x0d8775f648430679a709e98d2b0cb6250d2887ef", 18, "BATUSDT"),
    "YFI": ("0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e", 18, "YFIUSDT"),
    "SSV": ("0x9d65ff81a3c488d585bbfb0bfe3c7707c7917f54", 18, "SSVUSDT"),
    "ZRX": ("0xe41d2489571d322189246dafa5ebde1f4699f498", 18, "ZRXUSDT"),
    "BAL": ("0xba100000625a3754423978a60c9317c58a424e3d", 18, "BALUSDT"),
    "KNC": ("0xdefa4e8a7bcba345f687a2f1456f5edd9ce97202", 18, "KNCUSDT"),
    "STG": ("0xaf5191b0de278c7286d6c7cc6ab6bb8a73ba2cd6", 18, "STGUSDT"),
    "GALA": ("0xd1d2eb1b1e90b638588728b4130137d262c87cae", 8, "GALAUSDT"),
    "MASK": ("0x69af81e73a73b40adf4f3d4223cd9b1ece623074", 18, "MASKUSDT"),
    "ILV": ("0x767fe9edc9e0df98e07454847909b5e959d7ca0e", 18, "ILVUSDT"),
    "RSR": ("0x320623b8e4ff03373931769a31fc52a4e78b5d70", 18, "RSRUSDT"),
    "CVX": ("0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b", 18, "CVXUSDT"),
    "LPT": ("0x58b6a8a3302369daec383334672404ee733ab239", 18, "LPTUSDT"),
    "API3": ("0x0b38210ea11411557c13457d4da7dc6ea731b88a", 18, "API3USDT"),
    "UMA": ("0x04fa0d235c4abf4bcf4787af4cf447de572ef828", 18, "UMAUSDT"),
    "PAXG": ("0x45804880de22913dafe09f4980848ece6ecbaf78", 18, "PAXGUSDT"),
    "WOO": ("0x4691937a7508860f876c9c0a2a617e7d9e945d4b", 18, "WOOUSDT"),
    "ANKR": ("0x8290333cef9e6d528dd5618fb97a76f268f3edd4", 18, "ANKRUSDT"),
    "ENJ": ("0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c", 18, "ENJUSDT"),
    "MEME": ("0xb131f4a55907b10d1f0a50d8ab8fa09ec342cd74", 18, "MEMEUSDT"),
}


def in_dev(a, b):
    """Refuse any interval outside the development window."""
    if not (DEV_START <= a < b <= DEV_END):
        raise ValueError(f"refused: {a} to {b} is outside the development window {DEV_START} to {DEV_END}")


# ----------------------------------------------------------------------------------------------------------------------
# Pools, by CREATE2

def _keccak(b):
    from Crypto.Hash import keccak  # pycryptodome
    h = keccak.new(digest_bits=256)
    h.update(b)
    return h.digest()


def pool_address(addr_a, addr_b, fee):
    a, b = sorted([addr_a.lower()[2:], addr_b.lower()[2:]])
    salt = _keccak(bytes(12) + bytes.fromhex(a) + bytes(12) + bytes.fromhex(b) + int(fee).to_bytes(32, "big"))
    return "0x" + _keccak(b"\xff" + bytes.fromhex(FACTORY) + salt + bytes.fromhex(INIT_CODE_HASH))[12:].hex()


def candidate_pools():
    """Every candidate token against each quote token, and the quote tokens against each other, at every fee tier."""
    pairs = set()
    for s in TOKENS:
        for q in QUOTES:
            if s != q:
                pairs.add(tuple(sorted((s, q))))
    rows = []
    for s, q in sorted(pairs):
        (aa, da, ba), (ab, db, bb) = TOKENS[s], TOKENS[q]
        (s0, a0, d0, b0), (s1, a1, d1, b1) = sorted([(s, aa, da, ba), (q, ab, db, bb)], key=lambda t: t[1])
        for fee in FEES:
            rows.append({"pool": pool_address(a0, a1, fee), "sym0": s0, "sym1": s1, "fee": fee, "dec0": d0,
                         "dec1": d1, "bin0": b0, "bin1": b1, "pair": f"{s0}/{s1}"})
    df = pd.DataFrame(rows)
    for (x, y, fee), addr in KNOWN_POOLS.items():   # self-test of the CREATE2 computation
        got = df[(df.fee == fee) & (df.pair.isin([f"{x}/{y}", f"{y}/{x}"]))].pool.tolist()
        assert got == [addr], (x, y, fee, got)
    return df


# ----------------------------------------------------------------------------------------------------------------------
# BigQuery

def sql_blocks(a, b):
    in_dev(a, b)
    return (f"SELECT number, UNIX_SECONDS(timestamp) AS ts, base_fee_per_gas\n"
            f"FROM `{DATASET}.blocks`\n"
            f"WHERE timestamp >= TIMESTAMP '{a}' AND timestamp < TIMESTAMP '{b}'")


def sql_logs(a, b, pools):
    in_dev(a, b)
    plist = ", ".join(f"'{p}'" for p in pools)
    swap = f"l.topics[SAFE_OFFSET(0)] = '{TOPIC_SWAP}'"
    return (f"SELECT l.block_number, l.log_index, l.address, l.topics[SAFE_OFFSET(0)] AS t0,\n"
            f"  IF({swap}, NULL, l.topics[SAFE_OFFSET(2)]) AS t2, IF({swap}, NULL, l.topics[SAFE_OFFSET(3)]) AS t3,\n"
            f"  l.data, IF({swap}, t.from_address, NULL) AS from_address\n"
            f"FROM `{DATASET}.logs` AS l\n"
            f"JOIN `{DATASET}.transactions` AS t ON t.hash = l.transaction_hash\n"
            f"WHERE l.block_timestamp >= TIMESTAMP '{a}' AND l.block_timestamp < TIMESTAMP '{b}'\n"
            f"  AND t.block_timestamp >= TIMESTAMP '{a}' AND t.block_timestamp < TIMESTAMP '{b}'\n"
            f"  AND l.address IN ({plist})\n"
            f"  AND l.topics[SAFE_OFFSET(0)] IN ('{TOPIC_SWAP}', '{TOPIC_MINT}', '{TOPIC_BURN}')")


def sql_tokens():
    alist = ", ".join(f"'{a}'" for a, _, _ in TOKENS.values())
    return f"SELECT address, symbol, decimals FROM `{DATASET}.tokens` WHERE address IN ({alist})"


def queries(pools):
    q = [("tokens", sql_tokens()), ("blocks", sql_blocks(DEV_START, DEV_END))]
    q += [(f"logs {a[:7]}", sql_logs(a, b, pools)) for a, b in MONTHS]
    return q


def estimate(client, pools):
    """Dry runs. Returns [(name, bytes)]; costs nothing."""
    from google.cloud import bigquery
    out = []
    for name, sql in queries(pools):
        job = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
        out.append((name, int(job.total_bytes_processed)))
    return out


def _run(client, sql, est_bytes):
    from google.cloud import bigquery
    cap = int(est_bytes * 1.05) + 10 ** 9           # fails without charge if BigQuery would bill more
    job = client.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=cap))
    try:
        return job.result().to_dataframe(create_bqstorage_client=True)
    except Exception:                               # the Storage Read API may be off in a sandbox project
        return job.result().to_dataframe(create_bqstorage_client=False)


def _word(h, i):
    return int(h[2 + 64 * i: 66 + 64 * i], 16)


def _signed(v):
    return v - (1 << 256) if v >= (1 << 255) else v


def decode(df):
    """Raw logs -> one compact row per event. kind: 0 swap, 1 mint, 2 burn."""
    n = len(df)
    kind = np.empty(n, np.int8)
    a0 = np.zeros(n)
    a1 = np.zeros(n)
    sp = np.full(n, np.nan)
    liq = np.full(n, np.nan)
    amt = np.zeros(n)
    tick = np.zeros(n, np.int64)
    tl = np.zeros(n, np.int64)
    tu = np.zeros(n, np.int64)
    for j, (t0, t2, t3, data) in enumerate(zip(df["t0"].tolist(), df["t2"].tolist(), df["t3"].tolist(),
                                               df["data"].tolist())):
        if t0 == TOPIC_SWAP:
            kind[j] = 0
            a0[j], a1[j] = float(_signed(_word(data, 0))), float(_signed(_word(data, 1)))
            sp[j], liq[j] = float(_word(data, 2)), float(_word(data, 3))
            tick[j] = _signed(_word(data, 4))
        else:
            kind[j] = 1 if t0 == TOPIC_MINT else 2
            tl[j], tu[j] = _signed(int(t2, 16)), _signed(int(t3, 16))
            amt[j] = float(_word(data, 1) if t0 == TOPIC_MINT else _word(data, 0))
    return pd.DataFrame({"block_number": df["block_number"].to_numpy(np.int64), "log_index": df["log_index"].to_numpy(np.int64),
                         "pool": df["address"].str.lower().astype("category"), "kind": kind,
                         "sender": df["from_address"].fillna("").str.lower().astype("category"),
                         "a0": a0, "a1": a1, "sqrtp": sp, "liq": liq, "amount": amt, "tick": tick,
                         "tick_lower": tl, "tick_upper": tu})


def extract(client, out, pools, estimates, log=print):
    """Runs the queries whose outputs are missing; each is capped at its dry-run estimate."""
    out = Path(out)
    (out / "events").mkdir(parents=True, exist_ok=True)
    est = dict(estimates)
    q = dict(queries(pools))
    if not (out / "tokens.csv").exists():
        _run(client, q["tokens"], est["tokens"]).to_csv(out / "tokens.csv", index=False)
    if not (out / "blocks.parquet").exists():
        b = _run(client, q["blocks"], est["blocks"])
        b = b.astype({"number": "int64", "ts": "int64"}).sort_values("number").reset_index(drop=True)
        b["base_fee_per_gas"] = pd.to_numeric(b["base_fee_per_gas"], errors="coerce").astype("float64")
        b.to_parquet(out / "blocks.parquet")
        log(f"blocks: {len(b):,}")
    for a, _ in MONTHS:
        f = out / "events" / f"{a[:7]}.parquet"
        if f.exists():
            continue
        t = time.time()
        raw = _run(client, q[f"logs {a[:7]}"], est[f"logs {a[:7]}"])
        ev = decode(raw)
        del raw
        ev.to_parquet(f)
        log(f"{a[:7]}: {len(ev):,} events ({time.time() - t:.0f}s)")


def check_tokens(out):
    """Symbols and decimals in BigQuery's token table against the list above; mismatches are printed."""
    t = pd.read_csv(Path(out) / "tokens.csv", dtype=str)
    by = {r.address.lower(): r for r in t.itertuples()}
    bad = []
    for s, (a, d, _) in TOKENS.items():
        r = by.get(a)
        if r is None:
            bad.append(f"{s}: address not in the token table")
        elif str(r.decimals).strip() not in (str(d), "nan", "None", ""):
            bad.append(f"{s}: decimals {r.decimals} in BigQuery, {d} here")
    return bad


def load_events(out):
    ev = pd.concat([pd.read_parquet(f) for f in sorted((Path(out) / "events").glob("*.parquet"))], ignore_index=True)
    for k in ("pool", "sender"):
        ev[k] = ev[k].astype(str).astype("category")
    return ev


def swap_counts(out):
    """Swaps per pool and week (pools x 26), cached in swaps_per_week.csv."""
    f = Path(out) / "swaps_per_week.csv"
    if f.exists():
        return pd.read_csv(f, index_col=0).rename(columns=int)
    blocks = pd.read_parquet(Path(out) / "blocks.parquet", columns=["number", "ts"])
    wk = (blocks.ts.to_numpy() - T0) // WEEK
    spw = []
    for g in sorted((Path(out) / "events").glob("*.parquet")):
        e = pd.read_parquet(g, columns=["block_number", "pool", "kind"])
        e = e[e.kind == 0]
        spw.append(pd.crosstab(e.pool.astype(str), wk[e.block_number.to_numpy() - blocks.number.iloc[0]]))
    spw = pd.concat(spw).groupby(level=0).sum().reindex(columns=range(WEEKS), fill_value=0)
    spw.to_csv(f)
    return spw


# ----------------------------------------------------------------------------------------------------------------------
# Binance one-second klines

def _download(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "p1a-dev"}), timeout=300).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if k == tries - 1:
                raise
        except Exception:
            if k == tries - 1:
                raise
        time.sleep(5 * (k + 1))


def parse_klines(raw):
    """(seconds since T0, close, quote volume, trade count) from one monthly zip; ms or us timestamps."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        k = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4, 7, 8])
    k = k.apply(pd.to_numeric, errors="coerce").dropna()           # drops a header row if a file has one
    t = k[0].to_numpy(np.int64)
    t = t // 1_000_000 if t.max() > 10 ** 14 else t // 1_000
    return t - T0, k[4].to_numpy(np.float64), k[7].to_numpy(np.float64), k[8].to_numpy(np.int64)


def needed_symbols(pools_df, swaps_per_week):
    """Binance symbols of the pools with at least MIN_SWAPS_WEEK swaps in every week."""
    ok = swaps_per_week.index[(swaps_per_week >= MIN_SWAPS_WEEK).all(axis=1)]
    p = pools_df[pools_df.pool.isin(ok)]
    return sorted({s for s in pd.concat([p.bin0, p.bin1]).dropna()})


def binance(symbols, out, log=print):
    """Dense per-second closes (forward-filled) and weekly activity, one file per symbol."""
    d = Path(out) / "binance"
    d.mkdir(parents=True, exist_ok=True)
    for s in symbols:
        f = d / f"{s}.npz"
        if f.exists():
            continue
        t = time.time()
        close = np.full(NSEC, np.nan, np.float32)
        count = np.zeros(NSEC, np.int32)
        qv = np.zeros(NSEC, np.float32)
        missing = []
        for a, b in MONTHS:
            in_dev(a, b)
            raw = _download(BINANCE_URL.format(s=s, m=a[:7]))
            parts = [raw] if raw is not None else []
            if raw is None:                       # monthly file missing: try the daily files of that month
                for day in pd.date_range(a, b, freq="D", inclusive="left"):
                    r = _download(BINANCE_DAILY_URL.format(s=s, d=day.strftime("%Y-%m-%d")))
                    if r is not None:
                        parts.append(r)
            if not parts:
                missing.append(a[:7])
                continue
            for raw in parts:
                i, c, v, n = parse_klines(raw)
                keep = (i >= 0) & (i < NSEC)
                close[i[keep]], qv[i[keep]], count[i[keep]] = c[keep], v[keep], n[keep]
        idx = np.where(np.isnan(close), 0, np.arange(NSEC))
        np.maximum.accumulate(idx, out=idx)
        close = close[idx]
        wk = np.arange(NSEC) // WEEK
        active = np.bincount(wk, weights=(count > 0).astype(float), minlength=WEEKS) / np.bincount(wk, minlength=WEEKS)
        qv_w = np.bincount(wk, weights=qv, minlength=WEEKS)
        np.savez_compressed(f, close=close, active=active, qv=qv_w, missing=np.array(missing))
        log(f"{s}: {'missing ' + ','.join(missing) + '; ' if missing else ''}{time.time() - t:.0f}s")


def load_binance(out, s):
    if s is None or (isinstance(s, float) and math.isnan(s)):     # USDT itself
        return {"close": np.ones(NSEC, np.float32), "active": np.ones(WEEKS), "qv": np.full(WEEKS, np.inf)}
    z = np.load(Path(out) / "binance" / f"{s}.npz")
    return {k: z[k] for k in ("close", "active", "qv")}


# ----------------------------------------------------------------------------------------------------------------------
# Pool-week measures

LN2_96 = 96 * math.log(2.0)
DEPTH_FACTOR = math.sqrt(1 + DEPTH_BAND) - 1 / math.sqrt(1 + DEPTH_BAND)


def pool_state(ev, nblocks, bn0):
    """Replays one pool's events in order. In-range liquidity is set by each swap and moved by mints and burns whose
    range contains the current tick. Returns per-event and per-block (state after the block's last event) arrays."""
    kind = ev.kind.to_numpy().tolist()
    sp, L, tick = ev.sqrtp.to_numpy().tolist(), ev.liq.to_numpy().tolist(), ev.tick.to_numpy().tolist()
    tl, tu, amt = ev.tick_lower.to_numpy().tolist(), ev.tick_upper.to_numpy().tolist(), ev.amount.to_numpy().tolist()
    n = len(kind)
    pre_sp, post_sp, post_L = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    cs, cl, ct = math.nan, math.nan, None
    for j in range(n):
        k = kind[j]
        if k == 0:
            pre_sp[j] = cs
            cs, cl, ct = sp[j], L[j], tick[j]
        elif ct is not None and tl[j] <= ct < tu[j]:
            cl = cl + amt[j] if k == 1 else max(cl - amt[j], 0.0)
        post_sp[j], post_L[j] = cs, cl
    bi = ev.block_number.to_numpy() - bn0
    last = np.searchsorted(bi, np.arange(nblocks), side="right") - 1       # last event at or before each block
    ok = last >= 0
    blk_sp, blk_L = np.full(nblocks, np.nan), np.full(nblocks, np.nan)
    blk_sp[ok], blk_L[ok] = post_sp[last[ok]], post_L[last[ok]]
    return pre_sp, post_sp, post_L, blk_sp, blk_L


def _slopes(x, y, g, ngroups):
    """OLS slope of y on x within each group, from sums."""
    n = np.bincount(g, minlength=ngroups).astype(float)
    sx, sy = np.bincount(g, x, ngroups), np.bincount(g, y, ngroups)
    sxx, sxy = np.bincount(g, x * x, ngroups), np.bincount(g, x * y, ngroups)
    with np.errstate(invalid="ignore", divide="ignore"):
        vx = sxx - sx * sx / n
        return np.where((n > 2) & (vx > 0), (sxy - sx * sy / n) / vx, np.nan), n


def _winsorize_by_group(x, g, ngroups):
    x = x.copy()
    for k in range(ngroups):
        m = g == k
        if m.sum() > 10:
            lo, hi = np.percentile(x[m], WINSOR)
            x[m] = np.clip(x[m], lo, hi)
    return x


def pool_weeks(ev, meta, blocks, px0, px1):
    """One pool: 26 rows of measures, and the week x sender table of arbitrage volume in USD."""
    bn, ts = blocks["number"].to_numpy(), blocks["ts"].to_numpy()
    nb = len(bn)
    pre_sp, post_sp, post_L, blk_sp, blk_L = pool_state(ev, nb, bn[0])
    dln = (meta.dec0 - meta.dec1) * math.log(10.0)
    sec = np.clip(ts - 1 - T0, 0, NSEC - 1)                                 # the second just before each block
    c0, c1 = px0["close"][sec].astype(float), px1["close"][sec].astype(float)
    ref = np.log(c0) - np.log(c1)
    usd1 = c1                                                               # USD (USDT) price of token1
    wk = (ts - T0) // WEEK
    # per block: pool log price after the block, basis in bps, depth in USD
    logp = 2 * (np.log(blk_sp) - LN2_96) + dln
    x = (logp - ref) * 1e4
    depth = blk_L * (blk_sp / 2 ** 96) * DEPTH_FACTOR / 10 ** meta.dec1 * usd1
    valid = np.isfinite(x) & np.isfinite(depth)
    # per swap: flow in bps of log price, the swap's move, the basis before it, USD volume
    sw = ev.kind.to_numpy() == 0
    bi = (ev.block_number.to_numpy() - bn[0])[sw]
    a1 = ev.a1.to_numpy()[sw]
    psp, qsp, pl = post_sp[sw], pre_sp[sw], post_L[sw]
    with np.errstate(divide="ignore", invalid="ignore"):
        f = np.where(pl > 0, 2 * a1 / (pl * psp / 2 ** 96) * 1e4, 0.0)
        move = 2 * (np.log(psp) - np.log(qsp))
        xpre = (2 * (np.log(qsp) - LN2_96) + dln - ref[bi]) * 1e4
    vol = np.abs(a1) / 10 ** meta.dec1 * usd1[bi]
    arb = np.isfinite(move) & np.isfinite(xpre) & (move * xpre < 0)
    flow = np.bincount(bi, weights=f, minlength=nb)
    # aggregate response: flow over blocks b+1..b+3 on the basis at b, separately in odd and even UTC hours;
    # a basis observation whose window reaches into the next hour is dropped, so the halves share no flows
    hour = ts // 3600
    b = np.arange(nb - 3)
    same = (hour[b] == hour[b + 3]) & valid[b]
    y = flow[b + 1] + flow[b + 2] + flow[b + 3]
    rows = []
    g = np.where(same, wk[b] * 2 + (hour[b] % 2), -1)
    m = g >= 0
    xw = _winsorize_by_group(x[b][m], g[m], 2 * WEEKS)
    s_half, n_half = _slopes(xw, y[m], g[m], 2 * WEEKS)
    gl = np.where(same, wk[b], -1)
    ml = gl >= 0
    xl = _winsorize_by_group(x[b][ml], gl[ml], WEEKS)
    lag = [_slopes(xl, flow[b + k][ml], gl[ml], WEEKS)[0] for k in (1, 2, 3)]
    # depth: time-weighted mean over blocks, the state taken after each block's last event, which leaves out
    # liquidity minted and burned within one block (JIT)
    dt = np.diff(ts, append=ts[-1] + 12).astype(float)
    wv = np.where(valid, dt, 0.0)
    dep = np.bincount(wk, wv * np.nan_to_num(depth), WEEKS) / np.bincount(wk, wv, WEEKS)
    # Binance controls
    r = np.diff(np.log(px0["close"].astype(float)) - np.log(px1["close"].astype(float)), prepend=np.nan)
    r = np.nan_to_num(r)
    rv = np.bincount(np.arange(NSEC) // WEEK, r * r, WEEKS)
    legs = [p["qv"] for p in (px0, px1) if np.isfinite(p["qv"]).all()]
    qv = np.min(legs, axis=0) if legs else np.full(WEEKS, np.nan)
    swk = wk[bi]
    nsw = np.bincount(swk, minlength=WEEKS)
    vusd = np.bincount(swk, vol, WEEKS)
    for w in range(WEEKS):
        rows.append({"pool": meta.pool, "pair": meta.pair, "fee": meta.fee, "week": w,
                     "R1": -s_half[2 * w + 1], "R2": -s_half[2 * w], "n1": n_half[2 * w + 1], "n2": n_half[2 * w],
                     "R_lag1": -lag[0][w], "R_lag2": -lag[1][w], "R_lag3": -lag[2][w],
                     "D": math.log(dep[w]) if dep[w] > 0 else np.nan, "swaps": int(nsw[w]), "volume_usd": vusd[w],
                     "log_rv": math.log(rv[w]) if rv[w] > 0 else np.nan,
                     "log_cex_volume": math.log(qv[w]) if qv[w] > 0 else np.nan,
                     "active0": px0["active"][w], "active1": px1["active"][w]})
    pw = pd.DataFrame(rows)
    pw.attrs["median_abs_basis_bps"] = float(np.nanmedian(np.abs(x[valid]))) if valid.any() else np.nan
    pw.attrs["median_basis_bps"] = float(np.nanmedian(x[valid])) if valid.any() else np.nan
    sender = ev.sender.to_numpy()[sw]
    arbv = pd.DataFrame({"week": swk[arb], "sender": sender[arb], "usd": vol[arb]})
    arbv = arbv.groupby(["week", "sender"], observed=True).usd.sum().reset_index()
    arbv["pool"] = meta.pool
    return pw, arbv


def composition(arbv):
    """Per pool-week: Herfindahl index of arbitrage volume across senders, top share, senders with >= 1%, top change."""
    rows = []
    for (p, w), g in arbv.groupby(["pool", "week"]):
        s = g.usd.to_numpy() / g.usd.sum()
        o = np.argsort(-s)
        rows.append({"pool": p, "week": w, "C": float((s * s).sum()), "top_share": float(s[o[0]]),
                     "n_1pct": int((s >= 0.01).sum()), "top_sender": g.sender.to_numpy()[o[0]]})
    c = pd.DataFrame(rows).sort_values(["pool", "week"])
    c["top_changed"] = (c.groupby("pool").top_sender.shift() != c.top_sender) & c.groupby("pool").week.diff().eq(1)
    return c


def instrument(arbv, pools):
    """Leave-one-out shift-share Z on weeks 14-26: exposures are each bot's share of the pool's arbitrage volume in
    weeks 1-13; shifts are the bot's standardized log arbitrage volume in all other eligible pools."""
    a = arbv[arbv.pool.isin(pools)]
    pre, post = a[a.week < EXPOSURE_WEEKS], a[a.week >= EXPOSURE_WEEKS]
    bots = pre.groupby("sender", observed=True).usd.sum().sort_values(ascending=False).index[:N_BOTS]
    expo = pre[pre.sender.isin(bots)].groupby(["pool", "sender"], observed=True).usd.sum()
    expo = (expo / pre.groupby("pool").usd.sum().reindex(expo.index.get_level_values(0)).to_numpy()).unstack(fill_value=0.0)
    weeks = np.arange(EXPOSURE_WEEKS, WEEKS)
    tot = post[post.sender.isin(bots)].pivot_table(index="sender", columns="week", values="usd", aggfunc="sum",
                                                   fill_value=0.0, observed=True).reindex(index=bots, columns=weeks, fill_value=0.0)
    own = post[post.sender.isin(bots)].groupby(["pool", "sender", "week"], observed=True).usd.sum()
    rows = []
    for p in pools:
        z = np.zeros(len(weeks))
        if p in expo.index:
            for bname, s in expo.loc[p].items():
                if s <= 0:
                    continue
                v = tot.loc[bname].to_numpy() - np.array([own.get((p, bname, w), 0.0) for w in weeks])
                A = np.log1p(np.maximum(v, 0.0))
                sd = A.std()
                z += s * ((A - A.mean()) / sd if sd > 0 else 0.0)
        rows += [{"pool": p, "week": int(w), "Z": float(zz)} for w, zz in zip(weeks, z)]
    return pd.DataFrame(rows)


def build_panel(out, pools_df, log=print):
    """All pool-weeks of the pools that pass the swap-count floor, with the floors' inputs; saved to panel.parquet."""
    out = Path(out)
    f = out / "panel.parquet"
    if f.exists():
        return pd.read_parquet(f), pd.read_parquet(out / "arb_volume.parquet")
    blocks = pd.read_parquet(out / "blocks.parquet")
    assert np.all(np.diff(blocks.number.to_numpy()) == 1), "block numbers are not contiguous"
    spw = swap_counts(out)
    keep = spw.index[(spw >= MIN_SWAPS_WEEK).all(axis=1)]
    ev = load_events(out)
    ev = ev[ev.pool.isin(keep)].sort_values(["block_number", "log_index"]).reset_index(drop=True)
    log(f"pools with events: {spw.shape[0]}; with >= {MIN_SWAPS_WEEK} swaps in every week: {len(keep)}")
    cache, panels, arbs = {}, [], []
    for meta in pools_df[pools_df.pool.isin(keep)].itertuples():
        for s in (meta.bin0, meta.bin1):
            if s not in cache:
                cache[s] = load_binance(out, s)
        t = time.time()
        pw, arbv = pool_weeks(ev[ev.pool == meta.pool], meta, blocks, cache[meta.bin0], cache[meta.bin1])
        pw["median_basis_bps"] = pw.attrs["median_basis_bps"]
        panels.append(pw)
        arbs.append(arbv)
        log(f"{meta.pair} {meta.fee}: median basis {pw.attrs['median_basis_bps']:+.1f} bps ({time.time() - t:.0f}s)")
    panel = pd.concat(panels, ignore_index=True)
    arbv = pd.concat(arbs, ignore_index=True)
    panel = panel.merge(composition(arbv), on=["pool", "week"], how="left")
    panel.to_parquet(f)
    arbv.to_parquet(out / "arb_volume.parquet")
    return panel, arbv


# ----------------------------------------------------------------------------------------------------------------------
# Calibration

def demean2(df, col):
    """Two-way within transformation on a balanced pool x week panel."""
    m = df.pivot(index="pool", columns="week", values=col).to_numpy(float)
    return (m - m.mean(1, keepdims=True) - m.mean(0, keepdims=True) + m.mean()).ravel()


def eligible(panel, volume_floor):
    g = panel.groupby("pool")
    ok = (g.swaps.min() >= MIN_SWAPS_WEEK) & (g.median_basis_bps.first().abs() <= MAX_MEDIAN_BASIS_BPS) \
        & (g.active0.mean() >= MIN_ACTIVE_SHARE) & (g.active1.mean() >= MIN_ACTIVE_SHARE) \
        & (g.volume_usd.median() >= volume_floor)
    full = g.apply(lambda d: d[["R1", "R2", "D", "C"]].notna().all().all() and len(d) == WEEKS)
    return ok.index[ok & full]


def _cluster_t(y, X, cl):
    """OLS with cluster-robust (CR1) standard errors; returns coefficients and t statistics."""
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ b
    A = np.linalg.inv(X.T @ X)
    G = np.unique(cl)
    meat = sum(np.outer(X[cl == c].T @ u[cl == c], X[cl == c].T @ u[cl == c]) for c in G)
    n, k = X.shape
    V = len(G) / (len(G) - 1) * (n - 1) / (n - k) * A @ meat @ A
    return b, b / np.sqrt(np.diag(V))


def calibrate(out, panel, arbv, log=print):
    out = Path(out)
    res = {"window": [DEV_START, DEV_END], "floors": {"min_swaps_week": MIN_SWAPS_WEEK, "min_active_share": MIN_ACTIVE_SHARE,
                                                      "max_median_basis_bps": MAX_MEDIAN_BASIS_BPS, "winsor": WINSOR},
           "counts": {}, "note": "No estimate of composition's effect on depth is computed here, on purpose.",
           "module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for vf in VOLUME_FLOORS_USD:
        e = eligible(panel, vf)
        res["counts"][f"volume_floor_{int(vf):d}"] = {"pools": int(len(e)),
                                                      "pairs": int(panel[panel.pool.isin(e)].pair.nunique())}
    vf = VOLUME_FLOORS_USD[0]
    e = list(eligible(panel, vf))
    res["volume_floor_used"] = vf
    if len(e) < 3:
        res["error"] = "fewer than 3 eligible pools; nothing to calibrate"
        (out / "calibration.json").write_text(json.dumps(res, indent=1))
        return res
    p = panel[panel.pool.isin(e)].sort_values(["pool", "week"]).reset_index(drop=True)
    p["Rbar"] = (p.R1 + p.R2) / 2
    r1, r2, rb, c, d = (demean2(p, k) for k in ("R1", "R2", "Rbar", "C", "D"))
    rho_half = float(np.corrcoef(r1, r2)[0, 1])
    rel_avg = 2 * rho_half / (1 + rho_half) if rho_half > 0 else float("nan")
    psi = float(np.corrcoef(c, rb)[0, 1])
    bR = float(np.dot(rb, d) / np.dot(rb, rb))
    eps = (d - bR * rb).reshape(len(e), WEEKS)
    phi = float(np.corrcoef(eps[:, 1:].ravel(), eps[:, :-1].ravel())[0, 1])
    z = instrument(arbv, e)
    q = p[p.week >= EXPOSURE_WEEKS].merge(z, on=["pool", "week"], how="left")
    cz, zz, r2z = demean2(q, "C"), demean2(q, "Z"), demean2(q, "R2")
    pairs = q.pivot(index="pool", columns="week", values="pair").to_numpy().ravel()
    tz = _cluster_t(cz, np.column_stack([zz, r2z]), pairs)[1] if len(set(pairs)) > 1 else [float("nan")]
    res.update({
        "pools": e, "n_pools": len(e), "n_pairs": int(p.pair.nunique()),
        "reliability": {"half_correlation_within": rho_half, "average_within_spearman_brown": rel_avg},
        "composition": {"sd_within": float(c.std()), "corr_with_response_within": psi,
                        "corr_with_true_response_disattenuated": psi / math.sqrt(rel_avg) if rel_avg > 0 else None},
        "response": {"sd_within": float(rb.std()), "depth_slope_per_unit": bR, "depth_effect_per_sd": bR * float(rb.std())},
        "depth": {"residual_sd_within": float(eps.std()), "residual_ar1_within_pool": phi},
        "instrument": {"weeks": [EXPOSURE_WEEKS + 1, WEEKS], "corr_with_composition_within": float(np.corrcoef(cz, zz)[0, 1]),
                       "first_stage_t_clustered_by_pair": float(tz[0]), "first_stage_F": float(tz[0] ** 2)},
    })
    (out / "calibration.json").write_text(json.dumps(res, indent=1))
    return res


def summary_for_chat(res):
    """The aggregate numbers only, to paste back into the conversation."""
    keep = ("window", "module_sha256", "volume_floor_used", "counts", "n_pools", "n_pairs", "reliability", "composition", "response",
            "depth", "instrument", "error")
    return json.dumps({k: res[k] for k in keep if k in res}, indent=1)
