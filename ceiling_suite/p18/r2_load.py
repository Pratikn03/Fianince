# ============================================================================
# CELL R2 — LOAD THE CACHED SAMPLES (blocks from Parts 9, 15 and 16; minute data from the Drive cache)
# ============================================================================
assert hashlib.sha256(open(p18_path).read().encode()).hexdigest() == P18_HASH, "run R1 first"
BASE9 = CTRL + IMPACT + VOLBENCH
WCOLS = IMPACT + ["rv_15", "rv_day", "ewma_vol", "mae_lag60"]
def _need(fn):
    fp = os.path.join(XDATA, fn)
    if not os.path.exists(fp):
        raise FileNotFoundError(f"{fp} is missing: this notebook needs the Drive folder used by Parts 9, 15 and 16")
    return pd.read_parquet(fp)
UB9 = _need("blocks_p9_30sym.parquet")
UB9["group"] = UB9["symbol"].map(GROUP); UB9["split"] = np.where(UB9["date"] <= TRAIN_END, "train", "test")
UB9["kappa_sq"] = UB9["kappa_hat"] ** 2
UB9 = winsor_train(UB9[UB9["group"] == "thin"].copy(), WCOLS)                 # as in Part 9 (U5), thin symbols only
FB16 = _need("blocks_p16_forecast.parquet"); FB16["kappa_sq"] = FB16["kappa_hat"] ** 2
FB16 = winsor_train(FB16, WCOLS)                                                 # as in Part 16 (X6)
GB15 = _need("blocks_p15.parquet"); GB16 = _need("blocks_p16_guard.parquet")
FS9 = json.load(open(os.path.join(RESULTS, "U2_build.json")))["metrics"]["flow_scale"]
FS16 = json.load(open(os.path.join(RESULTS, "X4_build.json")))["metrics"]["flow_scale"]
FS15 = {s: float(FS9[s]) for s in GB15["symbol"].unique()}                     # Part 15 froze the Part 9 flow scales
MCACHE = {}
def minute(s, d):
    if (s, d) not in MCACHE:
        df, st = get_day(s, d)
        MCACHE[(s, d)] = (df, bool(st.get("depth_day_ok", False)) and df is not None)
    return MCACHE[(s, d)]
print("Part 9 thin rows:", UB9.groupby("split").size().to_dict(), "| Part 16 forecast rows:", FB16.groupby("split").size().to_dict())
print("Part 15 guard rows:", GB15.groupby("split").size().to_dict(), "| Part 16 guard rows:", GB16.groupby("split").size().to_dict())
