# ============================================================================
# CELL Q4 — DATA (downloads the 25th-28th of each month; cached in Drive; about 1-2 hours; safe to rerun)
# ============================================================================
assert os.path.exists(p12_path) and hashlib.sha256(open(p12_path).read().encode()).hexdigest() == P12_HASH, "run Q3 first"
jobs = [(s, d) for s in THIN for d in P12_DAYS]
print(f"{len(jobs)} symbol-days")
PANEL, VST = {}, []
with ThreadPoolExecutor(THREADS) as ex:
    futs = {ex.submit(get_day, s, d): (s, d) for s, d in jobs}
    for i, f in enumerate(as_completed(futs), 1):
        s, d = futs[f]
        try:
            df, st = f.result(); VST.append(st)
            if df is not None:
                PANEL[(s, d)] = df
        except Exception as e:
            VST.append({"symbol": s, "date": d, "reason": f"error: {e}"})
        if i % 300 == 0:
            print(f"   {i}/{len(jobs)}")
vst = pd.DataFrame(VST)
vst["depth_day_ok"] = vst.get("depth_day_ok", pd.Series(False, index=vst.index)).fillna(False).astype(bool)
OK12 = {(r.symbol, r.date) for r in vst.itertuples() if r.depth_day_ok and (r.symbol, r.date) in PANEL}
FLOW_SCALE = {}
for s in THIN:
    v = [np.nanmedian(np.abs(PANEL[(s, d)]["flow"].to_numpy())) for d in P12_DAYS if d <= TRAIN_END and (s, d) in OK12]
    FLOW_SCALE[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
pd.DataFrame(DL_LOG).to_csv(os.path.join(RESULTS, "p12_manifest_sha256.csv"), index=False)
record("Q4_build", None, "audit", {"requested": len(jobs), "valid": len(OK12), "flow_scale": FLOW_SCALE})
print("valid symbol-days:", len(OK12), "of", len(jobs))
