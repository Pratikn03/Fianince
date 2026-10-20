# ============================================================================
# CELL C4 — DATA (trades -> minute bars). Cached in Drive per pair-day; SAFE TO RERUN after a disconnect: it resumes.
# Expect roughly 2-3 hours at Coinbase's public rate limit. Progress is printed every 50 pair-days.
# ============================================================================
assert os.path.exists(p17_path) and hashlib.sha256(open(p17_path).read().encode()).hexdigest() == P17_HASH, "run C3 first"
jobs = [(s, d) for s in THIN17 + MID17 for d in TRAIN_DAYS + TEST_DAYS]
PANEL, VST = {}, []
t_start = time.time()
with ThreadPoolExecutor(4) as ex:                       # the shared rate limiter keeps the total at 7 requests/s
    futs = {ex.submit(get_day, s, d): (s, d) for s, d in jobs}
    for i, f in enumerate(as_completed(futs), 1):
        s, d = futs[f]
        try:
            df, st = f.result(); VST.append(st)
            if df is not None and st.get("day_ok"):
                PANEL[(s, d)] = df
        except Exception as e:
            VST.append({"symbol": s, "date": d, "reason": f"error: {e}"})
        if i % 50 == 0:
            el = (time.time() - t_start) / 60
            print(f"   {i}/{len(jobs)} pair-days, {el:.0f} min, about {el / i * (len(jobs) - i):.0f} min left, {N_REQ[0]} requests")
V = pd.DataFrame(VST)
FLOW_SCALE17 = {}
for s in THIN17 + MID17:
    tr = [PANEL[(s, d)] for d in TRAIN_DAYS if (s, d) in PANEL]
    v = np.concatenate([np.abs(x["flow"].to_numpy()[x["ntr"].to_numpy() > 0]) for x in tr]) if tr else np.array([])
    FLOW_SCALE17[s] = float(np.median(v)) if len(v) else np.nan
ntr = {s: sum((s, d) in PANEL for d in TRAIN_DAYS) for s in THIN17 + MID17}
nte = {s: sum((s, d) in PANEL for d in TEST_DAYS) for s in THIN17 + MID17}
IN_THIN = [s for s in THIN17 if ntr[s] >= 15 and nte[s] >= 25 and np.isfinite(FLOW_SCALE17[s]) and FLOW_SCALE17[s] > 0]
IN_MID = [s for s in MID17 if ntr[s] >= 15 and nte[s] >= 25 and np.isfinite(FLOW_SCALE17[s]) and FLOW_SCALE17[s] > 0]
man = V[[c for c in ["symbol", "date", "trades", "pages", "minute_coverage", "day_ok", "first_id", "last_id", "sha256", "reason"] if c in V.columns]]
man.to_csv(os.path.join(RESULTS, "p17_manifest.csv"), index=False)
print("thin pairs entering:", IN_THIN); print("mid pairs entering:", IN_MID)
record("C4_build", None, "audit", {"requested": len(jobs), "valid": len(PANEL), "train_days": ntr, "test_days": nte,
       "flow_scale": FLOW_SCALE17, "in_thin": IN_THIN, "in_mid": IN_MID, "requests": N_REQ[0],
       "reasons": V["reason"].value_counts().to_dict() if "reason" in V.columns else {}})
