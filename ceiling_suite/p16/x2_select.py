# ============================================================================
# CELL X2 — CHOOSE ENTIRELY NEW SYMBOLS (never used in Parts 4-15), FIXED BEFORE ANY ANALYSIS
# Candidates: USD-M perpetuals with depth in both 2023 and 2026, not among Part 4's 30 symbols or Part 5's new symbols,
# with quote volume on the Part 4 ranking day at most 1.5x the largest among Part 4's thin symbols. 30 are drawn with a
# fixed seed. Thin status is decided from training depth (cell X4), with Part 5's rule (median depth within 1% < $0.39M).
# ============================================================================
NEW_MAX16, THIN_DEPTH_MUSD = 30, 0.39
P4 = json.load(open(os.path.join(RESULTS, "X1_universe.json")))["metrics"]
P4_SYMBOLS = P4["symbols"]
P4_TERC = {s: v["tercile"] for s, v in json.load(open(os.path.join(RESULTS, "X3_T6_cross_section.json")))["metrics"]["by_symbol"].items()}
P5_SYMBOLS = json.load(open(os.path.join(RESULTS, "Y1_new_universe.json")))["metrics"]["symbols"]
USED = set(P4_SYMBOLS) | set(P5_SYMBOLS)
qv4 = P4["quote_volume_musd_on_rank_date"]
thin_vol_max = max(qv4[s] for s in P4_SYMBOLS if P4_TERC.get(s) == "thin")
try:
    listed = list_bucket_symbols()
except Exception as e:
    print("bucket listing failed:", e); listed = []
assert listed, "could not list Binance symbols; rerun this cell"
cands = [s for s in listed if re.fullmatch(r"[A-Z0-9]+USDT", s) and s not in USED]
with ThreadPoolExecutor(THREADS) as ex:
    keep = [s for s, ok in zip(cands, ex.map(span_ok, cands)) if ok]
with ThreadPoolExecutor(THREADS) as ex:
    qv = dict(zip(keep, ex.map(day_quote_volume, keep)))
pool = sorted([s for s in keep if np.isfinite(qv[s]) and qv[s] / 1e6 <= 1.5 * thin_vol_max])
CAND16 = sorted(rng(16).choice(pool, size=min(NEW_MAX16, len(pool)), replace=False).tolist()) if pool else []
print(f"new candidates: {len(cands)}; with depth span: {len(keep)}; thin-volume pool: {len(pool)}; drawn: {len(CAND16)}")
print(CAND16)
record("X2_new_universe", None, "audit", {"excluded_parts_4_5": sorted(USED), "thin_volume_cap_musd": 1.5 * thin_vol_max,
       "pool": pool, "drawn": CAND16, "quote_volume_musd": {s: qv[s] / 1e6 for s in CAND16}, "seed": SEED},
       note="New symbols fixed before any estimation; none was used in Parts 4-15.")
# Calendars: forecasting = Part 9 calendar (train 10th/24th 2023-24, test 6th/20th 2025-01..2026-09);
# guard = Part 15 calendar (evaluation 15th, certification window 12th-14th; train 2024, test 2025-01..2026-09)
FC_TRAIN, FC_TEST = train_dates(), fresh_dates()
TRAIN_M = [str(p) for p in pd.period_range("2024-01", "2024-12", freq="M")]
TEST_M = [str(p) for p in pd.period_range("2025-01", "2026-09", freq="M")]
EVAL_TR = [f"{m}-15" for m in TRAIN_M]; EVAL_TE = [f"{m}-15" for m in TEST_M]
WIN = {e: [e[:8] + f"{d:02d}" for d in (12, 13, 14)] for e in EVAL_TR + EVAL_TE}
G_DAYS = sorted(set(EVAL_TR + EVAL_TE + [d for e in WIN for d in WIN[e]]))
B_BOOT, Q_UP, BLOCK_MIN = 100, 0.90, 60
print(f"forecast calendar: {len(FC_TRAIN)} train, {len(FC_TEST)} test days; guard calendar: {len(G_DAYS)} days")
