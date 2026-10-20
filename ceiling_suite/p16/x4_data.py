# ============================================================================
# CELL X4 — DATA (step 1: training days of all 30 candidates -> thin classification; step 2: test and guard days of the
# thin symbols). Cached in Drive; about 2-3 hours in total; safe to rerun after a disconnect.
# ============================================================================
assert os.path.exists(p16_path) and hashlib.sha256(open(p16_path).read().encode()).hexdigest() == P16_HASH, "run X3 first"
PANEL, VST = {}, []
def fetch_all(jobs, label):
    print(f"{label}: {len(jobs)} symbol-days")
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
fetch_all([(s, d) for s in CAND16 for d in FC_TRAIN], "step 1 (training days)")
def ok_set():
    v = pd.DataFrame(VST)
    v["depth_day_ok"] = v.get("depth_day_ok", pd.Series(False, index=v.index)).fillna(False).astype(bool)
    return {(r.symbol, r.date) for r in v.itertuples() if r.depth_day_ok and (r.symbol, r.date) in PANEL}
OK16 = ok_set()
FLOW_SCALE, DEPTH_TR = {}, {}
for s in CAND16:
    tr_days = [d for d in FC_TRAIN if (s, d) in OK16]
    v = [np.nanmedian(np.abs(PANEL[(s, d)]["flow"].to_numpy())) for d in tr_days]
    FLOW_SCALE[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
    dep = [np.nanmedian((PANEL[(s, d)]["bid1"] + PANEL[(s, d)]["ask1"]).to_numpy()) for d in tr_days]
    DEPTH_TR[s] = float(np.nanmedian(dep)) if dep else np.nan
THIN16 = sorted([s for s in CAND16 if np.isfinite(DEPTH_TR[s]) and DEPTH_TR[s] < THIN_DEPTH_MUSD
                 and sum((s, d) in OK16 for d in FC_TRAIN) >= 15])
print("thin new symbols:", THIN16)
fetch_all([(s, d) for s in THIN16 for d in FC_TEST + G_DAYS], "step 2 (test and guard days)")
OK16 = ok_set()
THIN16 = [s for s in THIN16 if sum((s, d) in OK16 for d in FC_TEST) >= 15]
GROUP = {s: "thin" for s in THIN16}
pd.DataFrame(DL_LOG).to_csv(os.path.join(RESULTS, "p16_manifest_sha256.csv"), index=False)
record("X4_build", None, "audit", {"valid": len(OK16), "depth_train_musd": DEPTH_TR, "thin": THIN16, "flow_scale": FLOW_SCALE})
print("thin symbols entering the tests:", len(THIN16), THIN16)
