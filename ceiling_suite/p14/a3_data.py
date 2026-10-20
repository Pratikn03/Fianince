# ============================================================================
# CELL A3 — INTRADAY DATA (consolidated trades -> minute bars; cached in Drive; about 1-2 hours; safe to rerun)
# ============================================================================
assert os.path.exists(p14_path) and hashlib.sha256(open(p14_path).read().encode()).hexdigest() == P14_HASH, "run A2 first"
NY = "America/New_York"
def us_day(sym, date):
    d_ = os.path.join(UDIR, sym); os.makedirs(d_, exist_ok=True)
    pq, js = os.path.join(d_, f"{date}.parquet"), os.path.join(d_, f"{date}.json")
    if os.path.exists(js):
        st = json.load(open(js)); return (pd.read_parquet(pq) if os.path.exists(pq) else None), st
    t_open = pd.Timestamp(f"{date} 09:30", tz=NY).tz_convert("UTC"); t_close = t_open + pd.Timedelta(minutes=390)
    rows, tok, pages = [], None, 0
    while True:
        p = {"symbols": sym, "start": t_open.isoformat().replace("+00:00", "Z"), "end": t_close.isoformat().replace("+00:00", "Z"),
             "feed": "sip", "limit": 10000}
        if tok:
            p["page_token"] = tok
        r = aget(f"{DATA}/stocks/trades", p); pages += 1
        if "_error" in r:
            st = {"symbol": sym, "date": date, "reason": str(r)[:200], "day_ok": False}; json.dump(st, open(js, "w")); return None, st
        for tr in (r.get("trades") or {}).get(sym, []):
            rows.append((tr["t"], tr["p"], tr["s"]))
        tok = r.get("next_page_token")
        if not tok:
            break
    if not rows:
        st = {"symbol": sym, "date": date, "reason": "no trades", "day_ok": False}; json.dump(st, open(js, "w")); return None, st
    T = pd.DataFrame(rows, columns=["t", "p", "s"]); T["t"] = pd.to_datetime(T["t"], utc=True, format="ISO8601")
    T = T.sort_values("t"); px = T["p"].to_numpy(float); sz = T["s"].to_numpy(float)
    dp = np.diff(px, prepend=np.nan); sign = np.sign(dp); sign[~np.isfinite(sign)] = 0
    sign = pd.Series(np.where(sign == 0, np.nan, sign)).ffill().fillna(0).to_numpy()        # tick rule
    m = ((T["t"] - t_open).dt.total_seconds() // 60).astype(int).to_numpy(); ok = (m >= 0) & (m < 390)
    D = pd.DataFrame({"m": m[ok], "px": px[ok], "f": (sign * px * sz)[ok] / 1e6, "v": (px * sz)[ok] / 1e6}); g = D.groupby("m"); idx = np.arange(390)
    out = pd.DataFrame({"close": g["px"].last().reindex(idx).ffill().bfill(), "flow": g["f"].sum().reindex(idx).fillna(0.0),
                        "vol": g["v"].sum().reindex(idx).fillna(0.0)})
    cover = float(g.size().reindex(idx).notna().mean())
    st = {"symbol": sym, "date": date, "n_trades": len(T), "pages": pages, "minute_coverage": cover, "day_ok": bool(cover >= 0.80)}
    out.to_parquet(pq); json.dump(_clean(st), open(js, "w"))
    return out, st
jobs = [(s, d) for s in US_THIN + US_THICK for d in US_TRAIN + US_TEST]
UPAN, UST = {}, []
t0 = time.time()
for i, (s, d) in enumerate(jobs, 1):
    df, st = us_day(s, d); UST.append(st)
    if df is not None and st.get("day_ok"):
        UPAN[(s, d)] = df
    if i % 100 == 0:
        el = (time.time() - t0) / 60; print(f"   {i}/{len(jobs)}  {el:.0f} min, about {el / i * (len(jobs) - i):.0f} min left")
ntr = {s: sum(1 for d in US_TRAIN if (s, d) in UPAN) for s in US_THIN + US_THICK}
nte = {s: sum(1 for d in US_TEST if (s, d) in UPAN) for s in US_THIN + US_THICK}
IN_THIN = [s for s in US_THIN if ntr[s] >= 30 and nte[s] >= 25]; IN_MID = [s for s in US_THICK if ntr[s] >= 30 and nte[s] >= 25]
UFS = {s: float(np.median([np.median(np.abs(UPAN[(s, d)]["flow"].to_numpy())) for d in US_TRAIN if (s, d) in UPAN]) or 1.0) for s in IN_THIN + IN_MID}
UFS = {s: (v if v > 0 else float(np.median([np.mean(np.abs(UPAN[(s, d)]["flow"].to_numpy())) for d in US_TRAIN if (s, d) in UPAN]))) for s, v in UFS.items()}
print("included thin:", len(IN_THIN), "| included mid:", len(IN_MID))
record("A3_us_build", None, "audit", {"requested": len(jobs), "valid": len(UPAN), "train_days": ntr, "test_days": nte,
       "included_thin": IN_THIN, "included_mid": IN_MID})
