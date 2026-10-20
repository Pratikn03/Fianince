# ============================================================================
# CELL W4 — DATA (downloads the 12th-15th of each month; cached in Drive; about 1-2 hours; safe to rerun)
# ============================================================================
assert os.path.exists(p15_path) and hashlib.sha256(open(p15_path).read().encode()).hexdigest() == P15_HASH, "run W3 first"
jobs = [(s, d) for s in THIN for d in P15_DAYS]
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
OK15 = {(r.symbol, r.date) for r in vst.itertuples() if r.depth_day_ok and (r.symbol, r.date) in PANEL}
# Flow scale: frozen at the Part 9 training values (results/U2_build.json), so C3_hat is on the scale of the frozen model
U2B = json.load(open(os.path.join(RESULTS, "U2_build.json")))["metrics"]["flow_scale"]
FLOW_SCALE = {s: float(U2B[s]) for s in THIN}
pd.DataFrame(DL_LOG).to_csv(os.path.join(RESULTS, "p15_manifest_sha256.csv"), index=False)
record("W4_build", None, "audit", {"requested": len(jobs), "valid": len(OK15), "flow_scale": FLOW_SCALE})
print("valid symbol-days:", len(OK15), "of", len(jobs))
