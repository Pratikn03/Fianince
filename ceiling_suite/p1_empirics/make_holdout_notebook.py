"""Builds P1T_Holdout_Colab.ipynb: the one registered holdout run (2019-01-02 to 2023-12-29).

The download part is the validation notebook's (same fetch, pacing, Drive cache and SHA-256 manifest), extended to
2023-12-29 with a hard stop before 2024-01-01. The analysis part is the string ANALYSIS below, which
test_holdout_notebook.py executes on simulated TWSE responses before the notebook is used.

Order inside the notebook:
  1-3. download (resumable), 4. integrity gate (no statistic until it passes), 5. primary, saved to Drive at once,
  6. everything else. A rerun loads the stored primary and never recomputes it.
Fit window (author approval 2026-11-08): the 1,000 trading-day forecast origins ending 2018-12-27, so every fitted
target u_{t+1} falls before 2019-01-02.
"""
import hashlib
import json

KNOWN_T86_SCHEMAS = None   # filled from validate_executor.ERA_FIELDS (the three census eras, verbatim)

ANALYSIS = r'''
# 4. integrity gate: no statistic is computed until every check passes ------------------------------------------
BURNED = {"20240102", "20240103", "20261106"}
assert days[-1] <= END and all(d < "20240101" for d in days) and not (set(days) & BURNED), "date outside the registered range"
hold_days = [d for d in days if d >= HOLDOUT_START]
gate = {"n_days_total": len(days), "n_days_holdout": len(hold_days), "holdout_first": hold_days[0], "holdout_last": hold_days[-1],
        "unknown_t86_schema_days": [], "t86_empty_days": [], "mi_bad_days": [], "identity_failures": []}
known = {tuple(f) for f in KNOWN_T86_SCHEMAS}
for d in days:
    t86, mi = load("T86", d), load("MI", d)
    if tuple(t86.get("fields") or ()) not in known:
        gate["unknown_t86_schema_days"].append(d)
    elif not t86.get("data"):
        gate["t86_empty_days"].append(d)
    q, idx = ex.parse_mi_index(mi)
    if len(q) < MIN_QUOTES or not np.isfinite(idx):
        gate["mi_bad_days"].append(d)
eras = ex.t86_diagnostics((d, load("T86", d), None) for d in days if d not in gate["unknown_t86_schema_days"])
for e in eras:
    tot = max(e["share_total_eq_parts_with_foreign_dealers"], e["share_total_eq_parts_without_foreign_dealers"])
    dl = e["share_dealer_total_eq_own_plus_hedge"]
    if tot < 0.99 or (dl is not None and dl < 0.99):
        gate["identity_failures"].append({k: v for k, v in e.items() if k != "fields"})
gate["t86_eras"] = [{k: v for k, v in e.items() if k != "fields"} for e in eras]
gate["passed"] = not (gate["unknown_t86_schema_days"] or gate["t86_empty_days"] or gate["mi_bad_days"] or gate["identity_failures"]
                      or not (HOLD_MIN <= len(hold_days) <= HOLD_MAX))
json.dump(gate, open(os.path.join(ROOT, "p1t_holdout_gate.json"), "w"), indent=1, ensure_ascii=False, default=float)
if not gate["passed"]:
    print(json.dumps({k: (v[:20] if isinstance(v, list) else v) for k, v in gate.items() if k != "t86_eras"}, indent=1))
    raise SystemExit("Integrity gate failed BEFORE any statistic was computed. Holdout counter unchanged. "
                     "Send p1t_holdout_gate.json (on Drive in P1T_raw); do not change anything and do not rerun.")
print("integrity gate passed:", len(days), "days,", len(hold_days), "holdout days", hold_days[0], hold_days[-1], flush=True)

# 5. panel, masks and the registered primary ----------------------------------------------------------------------
P = ex.build_panel(((d, load("T86", d), load("MI", d)) for d in days), ev)
dates = np.array(P.dates); assert list(dates) == list(days)
dev = dates <= DEV_END                       # universe, scale constants, beta (spec section 2)
hold = dates >= HOLDOUT_START
pre = np.where(dates < HOLDOUT_START)[0]
fit_idx = pre[:-1][-1000:]                   # origins whose target day t+1 is before the holdout (approved 2026-11-08)
fit = np.zeros(len(dates), bool); fit[fit_idx] = True
assert fit.sum() == 1000 and not (fit & hold).any() and dates[fit_idx[-1] + 1] < HOLDOUT_START
prep = ex.prepare(P, dev)
PRIM = os.path.join(ROOT, "p1t_holdout_primary.json")
if os.path.exists(PRIM):
    primary = json.load(open(PRIM))
    print("The primary was already computed on", primary["computed_utc"], "- loaded from Drive, NOT recomputed.")
else:
    MARK = os.path.join(ROOT, "p1t_holdout_OPENED.json")
    crashed_before = os.path.exists(MARK)
    if not crashed_before:
        json.dump({"utc": now(), "executor_sha256": EXECUTOR_SHA256}, open(MARK, "w"))
    r = ex.run_period(prep, fit, hold, "Foreign")
    primary = {"spec": "P1T", "period": "holdout", "executor_sha256": EXECUTOR_SHA256, "computed_utc": now(),
               "recomputed_after_interruption_before_any_output": crashed_before, "primary": r,
               "fit_window": [str(dates[fit_idx[0]]), str(dates[fit_idx[-1]])],
               "holdout_window": [str(dates[hold][0]), str(dates[hold][-1])]}
    json.dump(primary, open(PRIM, "w"), indent=1, ensure_ascii=False, default=float)
print("REGISTERED PRIMARY (holdout, Foreign):", json.dumps(primary["primary"], indent=1), flush=True)

# 6. robustness, diagnostics and secondary outcomes (spec 7-8, amendments A2-A3); none changes the verdict --------
res = {"spec": "P1T", "period": "holdout", "executor_sha256": EXECUTOR_SHA256, "run_utc": now(),
       "primary_file": primary, "gate": gate,
       "n_days": {"development": int(dev.sum()), "fit_origins": int(fit.sum()), "holdout": int(hold.sum())},
       "event_counts": P.event_counts, "twt49u_events_parsed": len(ev), "universe_size": len(prep["universe_codes"]),
       "universe_codes": prep["universe_codes"],
       "beta_summary": [float(np.nanpercentile(prep["beta"][prep["U"]], q)) for q in (5, 50, 95)]}
res["robustness_blocks"] = {str(b): ex.run_period(prep, fit, hold, "Foreign", mean_block=b) for b in (10, 60)}
print("robustness blocks:", json.dumps(res["robustness_blocks"], indent=1), flush=True)
res["diagnostics"] = ex.diagnostics(prep, P.dates, fit, hold)
OUT = "p1t_holdout_results"
json.dump(res, open(OUT + ".json", "w"), indent=1, ensure_ascii=False, default=float)
with zipfile.ZipFile(OUT + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(OUT + ".json")
    if os.path.exists(MAN): z.write(MAN, "manifest.jsonl")
import shutil; shutil.copy(OUT + ".zip", os.path.join(ROOT, OUT + ".zip"))
dg = res["diagnostics"]
print("reverse causality:", json.dumps(dg["reverse_causality"], indent=1))
print("stability:", json.dumps({k: [v.get("D"), v.get("ci95"), v.get("verdict")] for k, v in dg["stability"].items()}, indent=1))
print("S1:", json.dumps(dg["S1"]["holm_adjusted_p"]), "S3:", json.dumps(dg["S3"]))
try:
    from google.colab import files; files.download(OUT + ".zip")
except Exception: print("saved", OUT + ".zip (also on Drive in P1T_raw)")
'''


def build():
    import validate_executor as v
    known = json.dumps(v.ERA_FIELDS, ensure_ascii=False)
    src = open("p1t_executor.py").read()
    sha = hashlib.sha256(src.encode()).hexdigest()
    nb = json.load(open("P1T_Validation_A1_Colab.ipynb"))
    cell = "".join(nb["cells"][1]["source"])
    i = cell.index("EXECUTOR_SHA256 = "); j = cell.index("\n", i)
    cell = cell[:i] + f'EXECUTOR_SHA256 = "{sha}"' + cell[j:]
    i = cell.index("EXECUTOR_SRC = "); j = cell.index("\n", i)
    cell = cell[:i] + "EXECUTOR_SRC = " + json.dumps(src, ensure_ascii=False) + cell[j:]
    rep = [
        ('START, END, DEV_END = "20130102", "20181228", "20161230"',
         'START, END, DEV_END = "20130102", "20231229", "20161230"\n'
         'MIN_QUOTES, HOLD_MIN, HOLD_MAX = 500, 1150, 1300\n'
         'KNOWN_T86_SCHEMAS = ' + known),
        ('def fetch(path, url, params, want_date=None):\n',
         'def fetch(path, url, params, want_date=None):\n'
         '    assert all(str(v) < "20240101" for v in params.values() if str(v)[:2] == "20"), "request at or after 2024-01-01"\n'),
        ('for y in range(2013, 2019):', 'for y in range(2013, 2024):'),
        ('days = sorted(set(days)); assert days[-1] <= END and all(d < HOLDOUT_START for d in days)',
         'days = sorted(set(days)); assert days[-1] <= END and all(d < "20240101" for d in days)'),
    ]
    for a, b in rep:
        n = cell.count(a)
        assert n >= 1, a
        cell = cell.replace(a, b)
    k = cell.index("# 4. run the registered executor once on the validation period")
    cell = cell[:k] + "def load(sub, d): return json.loads(gzip.open(os.path.join(ROOT, sub, d + \".json.gz\")).read())\n" + ANALYSIS
    compile(cell, "cell", "exec")
    nb["cells"][1]["source"] = cell
    nb["cells"][0]["source"] = (
        "# P1T holdout run (TWSE, 2019-01-02 to 2023-12-29): opened once\n\n"
        "Registered spec `P1T_taiwan_spec.md`, amendments A1-A3, readout `P1T_HOLDOUT_READOUT.md` (fixed before this run).\n\n"
        "- Downloads 2019-01-02 to 2023-12-29 (about 2,500 requests, roughly 2.5 hours at one every 3.5 s). The 2013-2018 files "
        "already on Drive are reused. Nothing at or after 2024-01-01 is requested.\n"
        "- **Integrity gate.** Before any statistic, it checks every day's T86 column layout against the three known eras, "
        "the price files and the accounting identities. If anything fails it stops and writes `p1t_holdout_gate.json`; "
        "the holdout counter is then unchanged.\n"
        "- **The registered primary** is computed once and saved to Drive at once. A rerun loads it and never recomputes it.\n"
        "- Fit window: the 1,000 forecast origins ending 2018-12-27, so every fitted target is before the holdout.\n\n"
        "**Run the single code cell once.** If the download is interrupted, run it again: it resumes and repeats nothing. "
        "Return `p1t_holdout_results.zip` and paste the printed output.")
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []; c["execution_count"] = None
    json.dump(nb, open("P1T_Holdout_Colab.ipynb", "w"), ensure_ascii=False, indent=1)
    return sha


if __name__ == "__main__":
    print(build())
