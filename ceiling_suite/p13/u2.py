# ============================================================================
# CELL U2 — SYMBOLS (fixed from Parts 4-5; nothing new is chosen)
#   thin: the 10 Part 4 thin-tercile symbols + the 10 Part 5 thin symbols (20)
#   mid:  the 10 Part 4 mid-tercile symbols (negative control: theory and Parts 4-5 predict no effect)
# ============================================================================
X3 = json.load(open(os.path.join(RESULTS, "X3_T6_cross_section.json")))["metrics"]["by_symbol"]
Y3 = json.load(open(os.path.join(RESULTS, "Y3_groups.json")))["metrics"]["group"]
THIN = sorted([s for s, v in X3.items() if v["tercile"] == "thin"] + [s for s, g in Y3.items() if g == "thin"])
MID = sorted([s for s, v in X3.items() if v["tercile"] == "mid"])
GROUP = {**{s: "thin" for s in THIN}, **{s: "mid" for s in MID}}
SYMBOLS = THIN + MID
assert len(THIN) == 20 and len(MID) == 10, (len(THIN), len(MID))
print("thin (20):", THIN); print("mid (10):", MID)
record("U1_universe", None, "audit", {"thin": THIN, "mid": MID})
