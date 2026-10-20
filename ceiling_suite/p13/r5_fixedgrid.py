# ============================================================================
# CELL R5 — DEPLETION ON A FIXED PRICE GRID (post hoc; Bybit order-book files, the six Part 10 coins)
# Binance's bookDepth bands are re-centred on the current mid, so a price move also moves the band. Bybit's order-book
# files contain every level, so depth can be measured in a band fixed at the previous mid. For 30-second intervals we
# regress the change in depth imbalance on signed taker flow, with the band (a) fixed at the start-of-interval mid and
# (b) re-centred at the end-of-interval mid (Binance's construction).
# ============================================================================
import gzip
R5_COINS = ["ACH", "ALICE", "API3", "LIT", "WOO", "ZEN"]
R5_DAYS = ["2025-05-11", "2025-05-12", "2025-09-11", "2025-09-12"]
OBURL = "https://quote-saver.bycsi.com/orderbook/linear/{s}/{d}_{s}_ob{n}.data.zip"
def bybit_trades(sym, date):
    code, raw = _http(f"https://public.bybit.com/trading/{sym}/{sym}{date}.csv.gz", timeout=180)
    if code != 200 or not raw:
        return None
    tr = pd.read_csv(io.BytesIO(gzip.decompress(raw))); tr.columns = [c.strip().lower() for c in tr.columns]
    ts = pd.to_numeric(tr["timestamp"], errors="coerce").to_numpy(); ts = np.where(ts > 1e11, ts / 1000.0, ts)
    px = pd.to_numeric(tr["price"], errors="coerce").to_numpy(); sz = pd.to_numeric(tr["size"], errors="coerce").to_numpy()
    sg = np.where(tr["side"].astype(str).str.lower().str.startswith("b"), 1.0, -1.0)
    return pd.DataFrame({"ts": ts, "f": sg * px * sz})
def band_imb(bids, asks, mid, band=0.01):
    B = sum(p * q for p, q in bids.items() if p >= mid * (1 - band)); A = sum(p * q for p, q in asks.items() if p <= mid * (1 + band))
    return (B - A) / (B + A) if B + A > 0 else np.nan
def depletion_day(coin, date, step=30):
    sym = f"{coin}USDT"; raw = None
    for n in (200, 500):
        code, raw = _http(OBURL.format(s=sym, d=date, n=n), timeout=600)
        if code == 200 and raw:
            break
    T = bybit_trades(sym, date)
    if not raw or T is None:
        return None
    t0 = pd.Timestamp(date, tz="UTC").timestamp(); nint = 86400 // step
    flow = np.zeros(nint); k = ((T["ts"].to_numpy() - t0) // step).astype(int); ok = (k >= 0) & (k < nint)
    np.add.at(flow, k[ok], T["f"].to_numpy()[ok])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = [n for n in z.namelist() if n.endswith(".data")][0]; lines = z.read(name).decode().splitlines()
    bids, asks = {}, {}; cur = None; rows = []; prev = None
    def snap(i):
        nonlocal prev
        if not bids or not asks:
            return
        bb, ba = max(bids), min(asks)
        if bb >= ba:
            return
        mid = 0.5 * (bb + ba)
        bl = dict(sorted(bids.items(), reverse=True)[:200]); al = dict(sorted(asks.items())[:200])
        if prev is not None and prev[0] == i - 1:
            m0 = prev[1]
            rows.append({"i": i, "d_fixed_end": band_imb(bl, al, m0), "d_fixed_start": prev[2],
                         "d_moving_end": band_imb(bl, al, mid), "d_moving_start": prev[3], "ret_bp": 1e4 * np.log(mid / m0)})
        prev = (i, mid, band_imb(bl, al, mid), band_imb(bl, al, mid))
    for line in lines:
        r = json.loads(line); i = int((r["ts"] / 1000 - t0) // step)
        if cur is not None and i != cur:
            snap(cur)
        cur = i; d = r["data"]
        if r["type"] == "snapshot":
            bids = {float(p): float(q) for p, q in d["b"]}; asks = {float(p): float(q) for p, q in d["a"]}
        else:
            for side, book in (("b", bids), ("a", asks)):
                for p, q in d[side]:
                    p = float(p); q = float(q)
                    if q == 0:
                        book.pop(p, None)
                    else:
                        book[p] = q
    D = pd.DataFrame(rows)
    D = D[(D["i"] >= 1) & (D["i"] < nint)]
    D["flow"] = flow[D["i"].to_numpy()] / max(np.median(np.abs(flow[flow != 0])), 1e-9)
    D["coin"], D["date"] = coin, date
    return D
parts = []
for c in R5_COINS:
    for d in R5_DAYS:
        try:
            X = depletion_day(c, d)
            if X is not None and len(X) > 500:
                parts.append(X); print(c, d, len(X))
        except Exception as e:
            print("skip", c, d, e)
DP = pd.concat(parts)
r5 = {}
for kind in ("fixed", "moving"):
    y = (DP[f"d_{kind}_end"] - DP[f"d_{kind}_start"]).to_numpy(); X = DP["flow"].to_numpy()
    ok = np.isfinite(y) & np.isfinite(X)
    by = []
    for (c, d), G in DP[ok].groupby(["coin", "date"]):
        yy = (G[f"d_{kind}_end"] - G[f"d_{kind}_start"]).to_numpy(); xx = G["flow"].to_numpy()
        by.append(float(np.polyfit(xx, yy, 1)[0]))
    b = np.array(by); Rb = rng(135)
    r5[kind] = {"eps30_mean_over_coin_days": float(b.mean()), "ci": boot_ci(b, Rb), "share_positive": float((b > 0).mean()), "coin_days": len(b)}
print(json.dumps(r5, indent=1))
record("R5_fixed_grid_depletion", None, "real-data", r5, note="post hoc; Bybit order books, six coins, four days each")
