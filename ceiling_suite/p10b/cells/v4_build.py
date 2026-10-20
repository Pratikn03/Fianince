# ============================================================================
# CELL V4 — TRADES + MERGE (downloads Bybit trades for every converted day; cached in Drive)
# ============================================================================
assert os.path.exists(p10_path) and hashlib.sha256(open(p10_path).read().encode()).hexdigest() == P10_HASH, "run V2 first"
jobs = [(c, d) for c in COINS for d in TRAIN_D + TEST_D if have_book(c, d)]
print(f"{len(jobs)} coin-days with a book file")
PANEL, VST = {}, []
with ThreadPoolExecutor(THREADS) as ex:
    futs = {ex.submit(build_day_bybit_ob, c, d): (c, d) for c, d in jobs}
    for i, f in enumerate(as_completed(futs), 1):
        c, d = futs[f]
        try:
            df, st = f.result(); VST.append(st)
            if df is not None and st.get("depth_day_ok"):
                PANEL[(c, d)] = df
        except Exception as e:
            VST.append({"symbol": c, "date": d, "reason": f"error: {e}"})
        if i % 100 == 0:
            print(f"   {i}/{len(jobs)}")
vst = pd.DataFrame(VST)
ntr = {c: sum(1 for (s, d) in PANEL if s == c and d <= TRAIN_END) for c in COINS}
nte = {c: sum(1 for (s, d) in PANEL if s == c and d > TRAIN_END) for c in COINS}
SYMBOLS = sorted(c for c in COINS if ntr[c] >= 8 and nte[c] >= 24)
GROUP = {s: "thin" for s in SYMBOLS}
OK = sorted((s, d) for (s, d) in PANEL if s in SYMBOLS)
FLOW_SCALE = {}
for s in SYMBOLS:
    v = [np.nanmedian(np.abs(PANEL[(s, d)]["flow"].to_numpy())) for d in TRAIN_D if (s, d) in PANEL]
    v = [x for x in v if np.isfinite(x) and x > 0]
    FLOW_SCALE[s] = float(np.median(v)) if v else 1.0
print("valid days (train / test):", {c: (ntr[c], nte[c]) for c in COINS})
print(f"included coins: {len(SYMBOLS)}", SYMBOLS)
med_depth = {s: float(np.nanmedian([np.nanmedian((PANEL[(s, d)]["bid1"] + PANEL[(s, d)]["ask1"]).to_numpy())
                                     for d in TRAIN_D if (s, d) in PANEL])) for s in SYMBOLS}
print("median depth within 1% on training days ($M):", {k: round(v, 3) for k, v in med_depth.items()})
vst.to_csv(os.path.join(RESULTS, "p10_day_status.csv"), index=False)
pd.DataFrame(DL_LOG).to_csv(os.path.join(RESULTS, "p10_trades_manifest_sha256.csv"), index=False)
record("V4_build", None, "audit", {"requested": len(jobs), "valid": len(PANEL), "train_days": ntr, "test_days": nte,
       "included": SYMBOLS, "flow_scale": FLOW_SCALE, "median_depth1_musd": med_depth})
