"""Forest plot of every thin-book out-of-sample evaluation (Parts 4 and 5). Reads result JSONs only."""
import json, sys, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
X, R, Y, K, Z, U, W, V, A, out = sys.argv[1:11]
x6 = json.load(open(f"{X}/X6_xsec_test_G2.json"))["metrics"]
xr = json.load(open(f"{R}/X6r_robustness_posthoc.json"))["metrics"]["checks"]
y6 = json.load(open(f"{Y}/Y6_replication_G2.json"))["metrics"]
y8 = json.load(open(f"{K}/Y8_kappa_control_posthoc.json"))["metrics"]["checks"]
z6 = json.load(open(f"{Z}/Z6_A_replication3.json"))["metrics"]["result"]
z6s = json.load(open(f"{Z}/Z6_secondary.json"))["metrics"]["paper2"]
u9 = json.load(open(f"{U}/U6_volbench_test.json"))["metrics"]
byb = json.load(open(f"{W}/W6_bybit_test.json"))["metrics"]["primary"]
v6 = json.load(open(f"{V}/V6_bybit_ob_test.json"))["metrics"]
a5 = json.load(open(f"{A}/A5_us_equity_test.json"))["metrics"]
rows = [("Part 4, pre-registered", None),
        ("Thin, $\\hat C_3$ (primary)", x6["primary"]),
        ("Mid, $\\hat C_3$", x6["secondary"]["mid: MAE_60 | C3_hat"]),
        ("Thick, $\\hat C_3$", x6["secondary"]["thick: MAE_60 | C3_hat"]),
        ("Part 4, post hoc (tick size)", None),
        ("+ relative tick controls", xr["R1_tick_controls"]),
        ("Drop tick-change symbols (4 left)", xr["R2_drop_tick_change_symbols"]),
        ("Same tick as training only", xr["R3_same_tick_as_train_only"]),
        ("Outcome in ticks", xr["R4_outcome_in_ticks"]),
        ("$\\hat C_3$ percentile within symbol", xr["R5_C3_percentile_within_symbol"]),
        ("Part 5, pre-registered (new symbols)", None),
        ("Thin, $\\hat C_3$ (primary)", y6["primary"]),
        ("Momentum term $\\kappa^2\\eta q$", y6["secondary"]["thin: MAE_60 | term_momentum"]),
        ("Reversion term $(1-a)\\kappa$", y6["secondary"]["thin: MAE_60 | term_reversion"]),
        ("Depth term $\\varphi\\varepsilon$", y6["secondary"]["thin: MAE_60 | term_depth"]),
        ("Unit-free ratio", y6["secondary"]["thin: MAE_60 | A_ratio"]),
        ("Not thin, $\\hat C_3$", y6["secondary"]["not_thin: MAE_60 | C3_hat"]),
        ("Part 5, post hoc (price impact)", None),
        ("$\\hat C_3$ + four impact controls", y8["K3_C3_plus_all_impact"]),
        ("$\\hat\\kappa$ alone", y8["K6_kappa_alone"]),
        ("Part 6, pre-registered (fresh days)", None),
        ("Thin, $\\hat C_3$ + impact controls (primary)", z6),
        ("Gain multiple (unit-free)", z6s["thin: MAE | gain_multiple"]),
        ("Log reversion half-life (unit-free)", z6s["thin: MAE | log_halflife"]),
        ("$\\hat C_3$ without depth", z6s["thin: MAE | C3_flow"]),
        ("Mid, $\\hat C_3$", z6s["mid: MAE | C3_hat"]),
        ("Part 9, pre-registered (beyond volatility forecasts)", None),
        ("Thin, $\\hat C_3$ (primary)", u9["primary"]),
        ("Summed response $S_{60}$", u9["secondary"]["thin: MAE | S60"]),
        ("Gain multiple (unit-free)", u9["secondary"]["thin: MAE | gain_multiple"]),
        ("Mid, $\\hat C_3$", u9["secondary"]["mid: MAE | C3_hat"]),
        ("Part 7, pre-registered (Bybit)", None),
        ("$\\hat C_3$ without depth", byb),
        ("Part 10, pre-registered (Bybit, order-book depth)", None),
        ("$\\hat C_3$ (primary)", v6["primary"]),
        ("$\\hat C_3$ without depth", v6["secondary"]["MAE | C3_flow"]),
        ("Summed response $S_{60}$", v6["secondary"]["MAE | S60"]),
        ("Part 14, pre-registered (thin US stocks)", None),
        ("Thin, $\\hat C_3$ without depth (primary)", a5["primary"]),
        ("Summed response $S_{60}$", a5["secondary"]["thin: MAE | S60"]),
        ("Reversion term", a5["secondary"]["thin: MAE | term_reversion"]),
        ("Momentum term", a5["secondary"]["thin: MAE | term_momentum"]),
        ("Mid control, $\\hat C_3$ without depth", a5["secondary"]["mid: MAE | C3_flow"])]
fig, ax = plt.subplots(figsize=(6.6, 12.0)); yy = len(rows)
labels, ticks = [], []
for name, v in rows:
    yy -= 1; ticks.append(yy)
    if v is None:
        labels.append(r"$\bf{" + name.replace(" ", r"\ ").replace(",", ",") + "}$" if False else name); continue
    lo, hi = [100 * c for c in v["delta_r2_ci"]]; m = 100 * v["delta_r2"]
    col = "#1f5fa8" if lo > 0 else "#888888"
    ax.plot([lo, hi], [yy, yy], color=col, lw=1.6); ax.plot(m, yy, "o", color=col, ms=4.5)
    labels.append("   " + name)
ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8)
for t, (n, v) in zip(ticks, rows):
    if v is None:
        ax.get_yticklabels()[ticks.index(t)].set_fontweight("bold")
ax.axvline(0, color="k", lw=0.8); ax.set_xscale("symlog", linthresh=1); ax.set_xlim(-1.2, 12)
ax.set_xlabel(r"Out-of-sample $\Delta R^2$ (percentage points), 95% date-block CI")
for s in ["top", "right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(out); print("saved", out)
