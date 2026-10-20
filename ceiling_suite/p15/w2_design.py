# ============================================================================
# CELL W2 — DESIGN (fixed before any Part 15 day is downloaded)
# Evaluation day: the 15th of each month. Certification window: the 12th, 13th and 14th (the three days before).
# On Binance none of the 12th-15th was used in Parts 1-14 (Binance test days were the 3rd, 6th, 10th, 17th, 20th, 24th and
# the 25th-28th; the 11th-16th were used only on Bybit, Part 10). Training: 2024. Test: 2025-01 to 2026-09.
# ============================================================================
def _mdays(months, days):
    return [f"{m}-{d:02d}" for m in months for d in days]
TRAIN_M = [str(p) for p in pd.period_range("2024-01", "2024-12", freq="M")]
TEST_M = [str(p) for p in pd.period_range("2025-01", "2026-09", freq="M")]
EVAL_TR, EVAL_TE = _mdays(TRAIN_M, [15]), _mdays(TEST_M, [15])
WIN = {e: [e[:8] + f"{d:02d}" for d in (12, 13, 14)] for e in EVAL_TR + EVAL_TE}
USED_BEFORE_BINANCE = {3, 6, 10, 17, 20, 24, 25, 26, 27, 28}
assert not any(int(d[-2:]) in USED_BEFORE_BINANCE for e in WIN for d in WIN[e] + [e])
P15_DAYS = sorted(set(EVAL_TR + EVAL_TE + [d for e in WIN for d in WIN[e]]))
B_BOOT, Q_UP, BLOCK_MIN = 100, 0.90, 60          # bootstrap draws, upper quantile of S60, block length (minutes)
print(f"{len(EVAL_TR)} training and {len(EVAL_TE)} test evaluation days; {len(P15_DAYS)} days to download per symbol")
