# ============================================================================
# CELL Q2 — DESIGN (fixed before any Part 12 day is downloaded)
# Evaluation day: the 28th of each month. Certification window: the 25th, 26th and 27th (the three days before).
# None of the 25th-28th was used in Parts 1-11 on Binance. Training: 2024. Test: 2025-01 to 2026-09.
# ============================================================================
def _mdays(months, days):
    return [f"{m}-{d:02d}" for m in months for d in days]
TRAIN_M = [str(p) for p in pd.period_range("2024-01", "2024-12", freq="M")]
TEST_M = [str(p) for p in pd.period_range("2025-01", "2026-09", freq="M")]
EVAL_TR, EVAL_TE = _mdays(TRAIN_M, [28]), _mdays(TEST_M, [28])
WIN = {e: [e[:8] + f"{d:02d}" for d in (25, 26, 27)] for e in EVAL_TR + EVAL_TE}
USED_BEFORE = {3, 6, 10, 17, 20, 24}
assert not any(int(d[-2:]) in USED_BEFORE for e in WIN for d in WIN[e] + [e])
P12_DAYS = sorted(set(EVAL_TR + EVAL_TE + [d for e in WIN for d in WIN[e]]))
print(f"{len(EVAL_TR)} training and {len(EVAL_TE)} test evaluation days; {len(P12_DAYS)} days to download per symbol")
