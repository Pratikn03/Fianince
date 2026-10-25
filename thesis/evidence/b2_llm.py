"""Test B2: language-model trading desks in Test B1's market, supervised from public data.

Market, vendor model, estimators and warning rules: Test B1 (ailoop_sim.py, b1_ailoop.py). Desks and the shared
language-model product: llm_ailoop.py. Designed after three exploratory pilots (B2_pilot_*.json), reported as such:
pilot 1 (Qwen2.5-1.5B, prompt v1) copied its stated stance in every decision; pilot 2 screened 1.5B/3B/7B with prompts v1
and v2 under a fixed rule and nothing passed; pilot 3 screened Qwen3-8B (failed) and Qwen2.5-14B-Instruct (passed) and
reran the pilot with 14B desks on seeds 301-302.

Registered run (once): Qwen/Qwen2.5-14B-Instruct, prompt v2, temperature 0.7, 16-bit weights, transformers backend on
a GPU with at least 39 GB; seeds 2001-2015 for each scenario control, fast (r_D 0.9), slow (r_D 0.995) and llmvendor
(one shared language-model product, r_D 0.9); 60 markets of 120 days with 50 desks; window 10 days, 12 lags.
Frozen twins: the same 60 markets with every desk held at its starting stance and the vendor at its starting stance
(no model calls), run by the same code.

Primaries (Holm across P2-P4 at 0.05; P1 pass/fail):
  P1  specificity: the standard estimator's time-to-zero rule fires in at most 2 of the 15 control markets;
  P2  early warning: over the fast and slow markets with a crisis, the standard time-to-zero rule fires before the crisis
      in at least 80% (one-sided binomial p against 1/2) and the median lead is at least 5 days (B1's thresholds);
  P3  language-model desks delay the crisis: over the 30 fast and slow markets, the crisis day with language-model desks
      is later than with frozen desks on the same seed (no crisis counts as day 120; ties dropped; exact one-sided sign
      test), and the median paired delay is at least 3 days;
  P4  a shared language-model product causes fewer crises than the fixed momentum product: over the 15 seeds, markets
      where the fixed product ('fast') has a crisis and the language-model product ('llmvendor') has none outnumber the
      reverse (exact one-sided McNemar test).
Validity: if more than 5% of model replies cannot be read as a stance, every primary is reported as failed.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import llm_ailoop as L  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/B2_llm.json"
COUNTER = THESIS / "checks/prereg/B2_unlock.json"
RESULT = HERE / "B2_results.json"
NUMBERS = THESIS / "checks/B2_numbers.tex"
MODEL = "Qwen/Qwen2.5-14B-Instruct"
PROMPT = "v2"
SEEDS = range(2001, 2016)
SCEN = ("control", "fast", "slow", "llmvendor")
ALPHA, DAYS = 0.05, 120
PIPELINE = (("b2_sha256", "b2_llm.py"), ("llm_sha256", "llm_ailoop.py"), ("sim_sha256", "ailoop_sim.py"),
            ("b1_sha256", "b1_ailoop.py"))


class FrozenBackend:
    """Every desk and the vendor keep their stance: the frozen twin."""
    name = "frozen"

    def decide(self, reqs):
        return [str(q["obs"]["k"]) for q in reqs]


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test B2 is a draft and is not registered"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def _holm(p):
    order = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i])); adj[i] = run
    return adj.tolist()


def evaluate(runs, twins, parse_rate_bad):
    by = {(r["scenario"], r["seed"]): r for r in runs}
    tw = {(r["scenario"], r["seed"]): r for r in twins}
    ctrl = [r for r in runs if r["scenario"] == "control"]
    ramp_all = [r for r in runs if r["scenario"] in ("fast", "slow")]
    ramp = [r for r in ramp_all if r["crisis"] is not None]
    lead = lambda r, e, k: L.B.lead(r, e, k)
    fa = sum(r["std"]["t2z"] is not None for r in ctrl)
    early = [lead(r, "std", "t2z") for r in ramp]; n_early = sum(x > 0 for x in early)
    p2 = float(stats.binom.sf(n_early - 1, len(ramp), 0.5)) if ramp else 1.0
    cday = lambda r: r["crisis"] if r["crisis"] is not None else DAYS
    delay = [cday(r) - cday(tw[(r["scenario"], r["seed"])]) for r in ramp_all]
    pos, neg = sum(d > 0 for d in delay), sum(d < 0 for d in delay)
    p3 = float(stats.binom.sf(pos - 1, pos + neg, 0.5)) if pos + neg else 1.0
    seeds = sorted({r["seed"] for r in runs})
    b = sum(by[("fast", s)]["crisis"] is not None and by[("llmvendor", s)]["crisis"] is None for s in seeds)
    c = sum(by[("fast", s)]["crisis"] is None and by[("llmvendor", s)]["crisis"] is not None for s in seeds)
    p4 = float(stats.binom.sf(b - 1, b + c, 0.5)) if b + c else 1.0
    adj = dict(zip(("P2", "P3", "P4"), _holm([p2, p3, p4])))
    valid = not parse_rate_bad
    out = {"valid": valid, "n_control": len(ctrl), "n_ramp": len(ramp_all), "n_ramp_with_crisis": len(ramp),
           "P1": {"false_alarms": fa, "pass": bool(valid and fa <= 2)},
           "P2": {"early": n_early, "n": len(ramp), "share": n_early / len(ramp) if ramp else None,
                  "median_lead": float(np.median(early)) if early else None, "p": p2, "p_holm": adj["P2"],
                  "pass": bool(valid and ramp and n_early >= math.ceil(0.8 * len(ramp)) and adj["P2"] < ALPHA
                               and np.median(early) >= 5)},
           "P3": {"later": pos, "earlier": neg, "ties": len(delay) - pos - neg, "median_delay": float(np.median(delay)),
                  "delays": delay, "p": p3, "p_holm": adj["P3"],
                  "pass": bool(valid and adj["P3"] < ALPHA and np.median(delay) >= 3)},
           "P4": {"fixed_only": b, "llm_only": c, "crises_fast": sum(by[("fast", s)]["crisis"] is not None for s in seeds),
                  "crises_llmvendor": sum(r["crisis"] is not None for r in runs if r["scenario"] == "llmvendor"),
                  "p": p4, "p_holm": adj["P4"], "pass": bool(valid and b > c and adj["P4"] < ALPHA)}}
    llmv = [r for r in runs if r["scenario"] == "llmvendor"]
    below = [r for r in ramp if r["s_star_static"] is not None and r["share_at_crisis"] is not None]
    tw_cr = [t for t in twins if t["scenario"] in ("fast", "slow") and t["crisis"] is not None and t["s_star_static"]]

    def first_switch(r):
        v = r["llm"]["vendor_stance_by_day"] or []
        return next((d for d, k in enumerate(v) if k != v[0]), None)
    out["secondary"] = {
        "false_alarms_controls": {f"{e}_{k}": sum(r[e][k] is not None for r in ctrl) for e in ("std", "disc") for k in ("lost", "buffer", "t2z")},
        "alarms_llmvendor_without_crisis": {f"{e}_{k}": sum(r[e][k] is not None for r in llmv if r["crisis"] is None)
                                            for e in ("std", "disc") for k in ("lost", "buffer", "t2z")},
        "n_llmvendor_without_crisis": sum(r["crisis"] is None for r in llmv),
        "median_leads": {f"{s}_{e}_{k}": float(np.median([lead(r, e, k) for r in ramp if r["scenario"] == s]))
                         for s in ("fast", "slow") for e in ("std", "disc") for k in ("lost", "buffer", "t2z")
                         if any(r["scenario"] == s for r in ramp)},
        "share_vs_static": {"below": sum(r["share_at_crisis"] < r["s_star_static"] for r in below),
                            "above": sum(r["share_at_crisis"] >= r["s_star_static"] for r in below),
                            "median_share": float(np.median([r["share_at_crisis"] for r in below])) if below else None,
                            "median_static": float(np.median([r["s_star_static"] for r in below])) if below else None},
        "twins_share_vs_static": {"below": sum(t["share_at_crisis"] < t["s_star_static"] for t in tw_cr),
                                  "above": sum(t["share_at_crisis"] >= t["s_star_static"] for t in tw_cr)},
        "twins_crises": {s: sum(t["crisis"] is not None for t in twins if t["scenario"] == s) for s in SCEN},
        "twins_std_t2z_false_alarms_controls": sum(t["std"]["t2z"] is not None for t in twins if t["scenario"] == "control"),
        "vendor_first_switch_day": [first_switch(r) for r in llmv],
        "vendor_final_stance": [(r["llm"]["vendor_stance_by_day"] or [None])[-1] for r in llmv],
        "desk_abs_change_after_loss": L._nanmean([r["llm"]["abs_stance_change_after_loss"] for r in runs]),
        "desk_abs_change_after_profit": L._nanmean([r["llm"]["abs_stance_change_after_profit"] for r in runs]),
        "desk_stance_change_rate": L._nanmean([r["llm"]["stance_change_rate"] for r in runs]),
        "median_tracking_error": float(np.median([r["tracking_error_median"] for r in runs if r["tracking_error_median"] is not None]))}
    return out


def numbers_tex(e, meta):
    v = lambda k: "passed" if e[k]["pass"] else "failed"
    s = e["secondary"]
    lines = ["% generated by b2_llm.py; do not edit",
             f"\\newcommand{{\\BtwoControl}}{{{e['n_control']}}}\\newcommand{{\\BtwoRamp}}{{{e['n_ramp']}}}"
             f"\\newcommand{{\\BtwoRampCrisis}}{{{e['n_ramp_with_crisis']}}}",
             f"\\newcommand{{\\BtwoFA}}{{{e['P1']['false_alarms']}}}",
             "\\newcommand{\\BtwoEarly}{%d}\\newcommand{\\BtwoLead}{%s}" % (
                 e["P2"]["early"], "--" if e["P2"]["median_lead"] is None else "%.1f" % e["P2"]["median_lead"]),
             "\\newcommand{\\BtwoLater}{%d}\\newcommand{\\BtwoEarlier}{%d}\\newcommand{\\BtwoTies}{%d}\\newcommand{\\BtwoDelay}{%.1f}" % (
                 e["P3"]["later"], e["P3"]["earlier"], e["P3"]["ties"], e["P3"]["median_delay"]),
             "\\newcommand{\\BtwoFixedOnly}{%d}\\newcommand{\\BtwoLLMOnly}{%d}\\newcommand{\\BtwoCrisesFast}{%d}\\newcommand{\\BtwoCrisesLLMV}{%d}" % (
                 e["P4"]["fixed_only"], e["P4"]["llm_only"], e["P4"]["crises_fast"], e["P4"]["crises_llmvendor"]),
             "\\newcommand{\\BtwoBelow}{%d}\\newcommand{\\BtwoAbove}{%d}" % (s["share_vs_static"]["below"], s["share_vs_static"]["above"]),
             "\\newcommand{\\BtwoDiscFA}{%d}\\newcommand{\\BtwoCalls}{%s}\\newcommand{\\BtwoParseFail}{%s}" % (
                 s["false_alarms_controls"]["disc_buffer"], f"{meta['llm_calls']:,}".replace(",", "{,}"), meta["parse_failures"]),
             f"\\newcommand{{\\BtwoPone}}{{{v('P1')}}}\\newcommand{{\\BtwoPtwo}}{{{v('P2')}}}"
             f"\\newcommand{{\\BtwoPthree}}{{{v('P3')}}}\\newcommand{{\\BtwoPfour}}{{{v('P4')}}}"]
    return "\n".join(lines) + "\n"


def open_counter(counter, sha, reg):
    c = json.loads(Path(counter).read_text()); assert c["opens"] == 0, "Test B2 was already opened; it runs once"
    Path(counter).write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                         "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")


def run(backend, out_dir, counter=COUNTER, resume=False, skip_gate=False, seeds=SEEDS, days=DAYS, cfg_kw=None,
        meta=None, log=print):
    spec, sha, reg = gate(skip_gate)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    ck = out_dir / "B2_checkpoint.pkl"
    cfg_kw = {"prompt": PROMPT, **(cfg_kw or {})}
    if resume:
        assert skip_gate or json.loads(Path(counter).read_text())["opens"] == 1, "nothing to resume: the test was not opened"
        assert ck.exists(), "no checkpoint to resume from"
        sim = L.load(ck); log(f"resumed at day {sim.day}")
    else:
        if not skip_gate:
            open_counter(counter, sha, reg)
        sim = L.Sim(L.LConfig(days=days, **cfg_kw), L.make_markets(SCEN, seeds))
    sim.run(backend, checkpoint=ck, every=4, log=log)
    log("language-model markets done; frozen twins and evaluation (about 10 minutes)")
    twin = L.Sim(L.LConfig(days=days, **cfg_kw), L.make_markets(SCEN, seeds)).run(FrozenBackend(), log=lambda s: None)
    runs = [L.summarize_market(sim, j) for j in range(sim.K)]
    twins = [L.summarize_market(twin, j) for j in range(twin.K)]
    for r in runs + twins:
        r.pop("track"); r.pop("M_true_by_day", None)
    bad = sim.parse_fail > 0.05 * max(sim.calls, 1)
    tm = np.array(sim.timing)
    meta = {**(meta or {}), "llm_calls": sim.calls, "parse_failures": sim.parse_fail, "unparsed_examples": sim.raw_examples,
            "seconds_model": float(tm[:, 1].sum()), "calls_per_second": float(tm[:, 2].sum() / max(tm[:, 1].sum(), 1e-9))}
    res = {"test": "B2", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "model": MODEL, "prompt": PROMPT, "seeds": [min(seeds), max(seeds)], "meta": meta,
           "evaluation": evaluate(runs, twins, bad), "runs": runs, "twins": twins}
    for path in ([out_dir / RESULT.name, out_dir / NUMBERS.name] + ([] if skip_gate else [RESULT, NUMBERS])):
        path.write_text(json.dumps(res, indent=1, default=float) + "\n" if path.suffix == ".json" else numbers_tex(res["evaluation"], meta))
    log(json.dumps({k: v for k, v in res["evaluation"].items() if k != "secondary"}, indent=1, default=float))
    return res


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        res = run(L.MockBackend(), td, skip_gate=True, seeds=range(1, 3), days=30, cfg_kw={"window": 5}, log=lambda s: None)
        e = res["evaluation"]
        assert e["n_control"] == 2 and e["n_ramp"] == 4 and len(e["P3"]["delays"]) == 4
        assert numbers_tex(e, res["meta"]).startswith("%")
        json.dumps(res, default=float)
        # resume from the checkpoint gives the same evaluation
        res2 = run(L.MockBackend(), td, skip_gate=True, resume=True, seeds=range(1, 3), days=30, cfg_kw={"window": 5}, log=lambda s: None)
        assert res2["evaluation"]["P3"]["delays"] == e["P3"]["delays"]
        print(json.dumps({k: v for k, v in e.items() if k != "secondary"}, default=float)[:800])
    try:
        gate(); raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("b2 selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
