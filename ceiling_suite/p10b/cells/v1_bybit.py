
# ---------------------------------------------------------------------------------------------
# Part 10: Bybit order-book files -> 1-minute depth; Bybit trades -> 1-minute price, flow, volume
# ---------------------------------------------------------------------------------------------
OB_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})_([A-Z0-9]+)USDT_ob(\d+)\.data$")

DEPTH_LEVELS = 200          # the pre-registered book is the top 200 levels; 2024 files carry 500, so only the best 200 are used
def book_minutes(fh, date, band=0.01, levels=DEPTH_LEVELS):
    """Rebuild the book from one day's messages (a 'snapshot' resets it; a 'delta' sets levels, size 0 deletes).
    Returns the book at the END of each UTC minute: best bid/ask and $ notional within 1% of mid ($M),
    counting only the best `levels` price levels on each side (identical for ob200 and ob500 files)."""
    t0 = int(pd.Timestamp(date, tz="UTC").timestamp() * 1000)
    bids, asks = {}, {}
    out = np.full((1440, 4), np.nan); cur = None; last_u = None; gaps = 0; n_msg = 0; n_snap = 0; crossed = 0
    def rec(m):
        nonlocal crossed
        if not (0 <= m < 1440) or not bids or not asks:
            return
        bb, ba = max(bids), min(asks)
        if bb >= ba:
            crossed += 1; return
        mid = 0.5 * (bb + ba)
        bl = sorted(bids, reverse=True)[:levels]; al = sorted(asks)[:levels]
        out[m] = (bb, ba, sum(p * bids[p] for p in bl if p >= mid * (1 - band)) / 1e6,
                  sum(p * asks[p] for p in al if p <= mid * (1 + band)) / 1e6)
    for line in fh:
        if not line.strip():
            continue
        r = json.loads(line); n_msg += 1
        m = (r["ts"] - t0) // 60000
        if cur is not None and m != cur:
            rec(cur)
        cur = m; d = r["data"]
        if r["type"] == "snapshot":
            n_snap += 1
            bids = {float(p): float(q) for p, q in d["b"]}; asks = {float(p): float(q) for p, q in d["a"]}
        else:
            if last_u is not None and d["u"] != last_u + 1:
                gaps += 1
            for side, book in (("b", bids), ("a", asks)):
                for p, q in d[side]:
                    p = float(p); q = float(q)
                    if q == 0:
                        book.pop(p, None)
                    else:
                        book[p] = q
        last_u = d.get("u", last_u)
    if cur is not None:
        rec(cur)
    df = pd.DataFrame(out, columns=["best_bid", "best_ask", "bid1", "ask1"])
    st = {"messages": n_msg, "snapshots": n_snap, "u_gaps": gaps, "crossed_minutes": crossed,
          "depth_rule": f"top{levels}_within_{band:g}",
          "book_minute_coverage": float(df["bid1"].notna().mean())}
    return df, st

def _convert_member(name, raw, source):
    mt = OB_NAME.search(os.path.basename(name))
    if not mt:
        return None
    date, coin = mt.group(1), mt.group(2)
    df, st = book_minutes(io.StringIO(raw.decode()), date)
    st.update({"coin": coin, "date": date, "depth_levels": int(mt.group(3)), "source_file": source,
               "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    d_ = os.path.join(OBMIN, coin); os.makedirs(d_, exist_ok=True)
    df.to_parquet(os.path.join(d_, f"{date}.parquet"))
    json.dump(_clean(st), open(os.path.join(d_, f"{date}.json"), "w"))
    return (coin, date)

def convert_zip(path):
    """Turn one uploaded Bybit file into small per-day book summaries; returns the (coin, date) pairs written.
    Accepts a daily .zip, a bundle .zip holding daily .zip files (one Bybit date-range download), or a loose .data file."""
    done = []
    if path.endswith(".data"):
        got = _convert_member(path, open(path, "rb").read(), os.path.basename(path))
        return [got] if got else []
    def walk(zf, src):
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            if name.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(zf.read(name))) as inner:
                    walk(inner, src)
            else:
                got = _convert_member(name, zf.read(name), src)
                if got:
                    done.append(got)
    with zipfile.ZipFile(path) as z:
        walk(z, os.path.basename(path))
    return done

def have_book(coin, date):
    js = os.path.join(OBMIN, coin, f"{date}.json")
    return os.path.exists(js) and json.load(open(js)).get("depth_rule", "").startswith(f"top{DEPTH_LEVELS}_")

def trade_minutes(coin, date):
    """Minute bars from Bybit trades (same code as Part 7): last price, signed taker notional and volume ($M)."""
    sym = f"{coin}USDT"
    d_ = os.path.join(TRMIN, coin); os.makedirs(d_, exist_ok=True)
    pq, js = os.path.join(d_, f"{date}.parquet"), os.path.join(d_, f"{date}.json")
    if os.path.exists(js):
        st = json.load(open(js)); return (pd.read_parquet(pq) if os.path.exists(pq) else None), st
    code, raw = _http(bb_url(sym, date), timeout=180)
    if code != 200 or not raw:
        st = {"coin": coin, "date": date, "reason": f"http {code}", "day_ok": False}
        json.dump(st, open(js, "w")); return None, st
    DL_LOG.append({"symbol": sym, "date": date, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    tr = pd.read_csv(io.BytesIO(gzip.decompress(raw)))
    tr.columns = [c.strip().lower() for c in tr.columns]
    ts = pd.to_numeric(tr["timestamp"], errors="coerce").to_numpy()
    ts = np.where(ts > 1e11, ts / 1000.0, ts)
    m = ((ts - pd.Timestamp(date, tz="UTC").timestamp()) // 60).astype("int64")
    px = pd.to_numeric(tr["price"], errors="coerce").to_numpy(); sz = pd.to_numeric(tr["size"], errors="coerce").to_numpy()
    notional = px * sz / 1e6; sign = np.where(tr["side"].astype(str).str.lower().str.startswith("b"), 1.0, -1.0)
    ok = (m >= 0) & (m < 1440) & np.isfinite(px) & np.isfinite(notional)
    T = pd.DataFrame({"m": m[ok], "ts": ts[ok], "px": px[ok], "flow": (sign * notional)[ok], "vol": notional[ok]}).sort_values("ts")
    idx = np.arange(1440); g = T.groupby("m")
    out = pd.DataFrame(index=idx)
    out["close"] = g["px"].last().reindex(idx).ffill().bfill()
    out["flow"] = g["flow"].sum().reindex(idx).fillna(0.0)
    out["vol"] = g["vol"].sum().reindex(idx).fillna(0.0)
    cover = float(g.size().reindex(idx).notna().mean())
    st = {"coin": coin, "date": date, "n_trades": int(ok.sum()), "trade_minute_coverage": cover,
          "day_ok": bool(cover >= 0.80 and out["close"].notna().all())}
    out.to_parquet(pq); json.dump(_clean(st), open(js, "w"))
    return out, st

def build_day_bybit_ob(coin, date):
    """Merge: price, flow and volume from trades (as Binance klines in Parts 4-9); depth within 1% from the book."""
    tr, st_t = trade_minutes(coin, date)
    st_b = json.load(open(os.path.join(OBMIN, coin, f"{date}.json")))
    st = {"symbol": coin, "date": date, **{k: v for k, v in st_t.items() if k not in ("coin", "date")},
          **{k: v for k, v in st_b.items() if k not in ("coin", "date")}}
    if tr is None or not st_t.get("day_ok"):
        st["depth_day_ok"] = False; return None, st
    bk = pd.read_parquet(os.path.join(OBMIN, coin, f"{date}.parquet"))
    out = tr.copy()
    mid = 0.5 * (bk["best_bid"] + bk["best_ask"])
    far = (np.abs(mid / out["close"] - 1) > 0.03).to_numpy()      # book far from traded price: treat as missing
    for c in ["bid1", "ask1"]:
        v = bk[c].to_numpy().copy(); v[far] = np.nan
        out[c] = pd.Series(v).ffill(limit=2).to_numpy()
    for c in ["oi", "top_pos_ratio", "top_acc_ratio", "acc_ratio", "taker_ratio"]:
        out[c] = np.nan
    cov = float(pd.Series(out["bid1"]).notna().mean())
    st.update({"merged_depth_coverage": cov, "book_far_from_trades": int(far.sum()),
               "depth_day_ok": bool(cov >= 0.80 and st_b.get("u_gaps", 99) <= 5 and st_b.get("snapshots", 0) >= 1)})
    out["symbol"], out["date"] = coin, date
    return out, st
