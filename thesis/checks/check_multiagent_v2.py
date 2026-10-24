"""Registered simulation B3v2: learning agents, certificate lifetime and realized loss.

Replaces the withdrawn B3 simulation, whose weight updates were monotone by construction, so that
its "realized lifetime" could not fall below the bound and measured only the construction.

Here each cohort's rule is the saturating momentum rule phi(y) = tanh(y) (sector bound s = 1), and
each cohort learns its weight online by a clipped gradient step on its own trading profit,

    q_i(t+1) = clip( q_i(t) + clip(eta * phi(y_i,t) * (x_{t+1} - x_t), -gamma, gamma), 0, q_cap ),

so weights can rise or fall and |q_i(t+1) - q_i(t)| <= gamma at every step. Shocks are bounded by
wbar: in the adversarial regime the shock pushes in the direction of the current state with
probability p_adv and is uniform otherwise; in the random regime it is uniform on [-wbar, wbar].

Outcomes per run:
  * peak_pre      max |x_t| for t <= T_valid, against the budget Z* = kappa wbar / (1 - |a| - kappa Phi_max);
  * Phi_pre       max total sensitivity sum_i |q_i(t)| s_i for t <= T_valid;
  * T_cross       first t with total sensitivity above Phi_max (None if never within the horizon);
  * T_breach      first t with |x_t| > Z* (None if never within the horizon).
P1 (implementation check of Corollary thm:lifetime; guaranteed by the theorem): peak_pre <= Z* and
Phi_pre <= Phi_max in every run. P2 (informative; can fail): in the adversarial regime, pooled over
learning rates, T_cross <= 3 T_valid in at least half of the runs, i.e. the lifetime bound is
within a factor of three of when the certificate's sensitivity budget is actually exhausted.

Usage:  python check_multiagent_v2.py --run    (once, after the specification is public)
        python check_multiagent_v2.py --check  (verify the committed result; no reopening)
        python check_multiagent_v2.py --dev    (smoke test on a development seed; prints no outcome)
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC = HERE / "prereg/multiagent_v2.json"
COUNTER = HERE / "prereg/multiagent_v2_unlock.json"
RESULT = HERE / "R_multiagent_v2.json"
NUMBERS = HERE / "multiagent_v2_numbers.tex"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def t_valid(spec, gamma):
    s = np.array(spec["s"], float)
    margin = spec["Phi_max"] - float(np.sum(np.array(spec["q0"], float) * s))
    return int(np.floor(margin / float(np.sum(gamma * s))))


def simulate(spec, regime, gamma, seed):
    a, kappa, wbar = spec["a"], spec["kappa"], spec["wbar"]
    r = np.array(spec["r"], float); s = np.array(spec["s"], float)
    q = np.array(spec["q0"], float).copy()
    eta, qcap, padv = spec["eta"], spec["q_cap"], spec["p_adv"]
    Phi_max = spec["Phi_max"]
    Z = kappa * wbar / (1 - abs(a) - kappa * Phi_max)
    T = t_valid(spec, gamma)
    H = spec["horizon_multiple"] * T
    rng = np.random.default_rng(seed)
    x = 0.0; y = np.zeros_like(r)
    peak_pre, phi_pre = 0.0, float(np.sum(np.abs(q) * s))
    t_cross = t_breach = None
    max_step = 0.0
    xs_peak = 0.0
    for t in range(H):
        phi = np.tanh(y)
        u = float(np.sum(q * phi))
        if regime == "adversarial" and rng.random() < padv:
            w = wbar * (1.0 if x >= 0 else -1.0)
        else:
            w = rng.uniform(-wbar, wbar)
        x_new = a * x + kappa * (u + w)
        grad = phi * (x_new - x)
        step = np.clip(eta * grad, -gamma, gamma)
        q_new = np.clip(q + step, 0.0, qcap)
        max_step = max(max_step, float(np.max(np.abs(q_new - q))))
        q = q_new
        y = r * y + (1 - r) * x_new
        x = x_new
        tt = t + 1
        sens = float(np.sum(np.abs(q) * s))
        xs_peak = max(xs_peak, abs(x))
        if tt <= T:
            peak_pre = max(peak_pre, abs(x))
            phi_pre = max(phi_pre, sens)
        if t_cross is None and sens > Phi_max:
            t_cross = tt
        if t_breach is None and abs(x) > Z:
            t_breach = tt
    return {"regime": regime, "gamma": gamma, "seed": seed, "T_valid": T, "horizon": H, "Z_budget": Z,
            "peak_pre": peak_pre, "Phi_pre": phi_pre, "T_cross": t_cross, "T_breach": t_breach,
            "peak_all": xs_peak, "max_weight_step": max_step,
            "conservativeness": Z / peak_pre if peak_pre > 0 else None,
            "final_Phi": float(np.sum(np.abs(q) * s))}


def run_all(spec, seed0, reps):
    runs = []
    for ri, regime in enumerate(spec["regimes"]):
        for gi, gamma in enumerate(spec["gammas"]):
            for rep in range(reps):
                runs.append(simulate(spec, regime, float(gamma), seed0 + 10000 * ri + 100 * gi + rep))
    return runs


def summarize(spec, runs):
    tol = spec["tolerance"]
    p1 = [r["peak_pre"] <= r["Z_budget"] * (1 + tol) and r["Phi_pre"] <= spec["Phi_max"] + tol
          and r["max_weight_step"] <= r["gamma"] + tol for r in runs]
    adv = [r for r in runs if r["regime"] == "adversarial"]
    p2_hits = [r["T_cross"] is not None and r["T_cross"] <= 3 * r["T_valid"] for r in adv]
    by = {}
    for regime in spec["regimes"]:
        for gamma in spec["gammas"]:
            sel = [r for r in runs if r["regime"] == regime and r["gamma"] == float(gamma)]
            tc = [r["T_cross"] / r["T_valid"] for r in sel if r["T_cross"] is not None]
            tb = [r["T_breach"] / r["T_valid"] for r in sel if r["T_breach"] is not None]
            cons = [r["conservativeness"] for r in sel if r["conservativeness"] is not None]
            by[f"{regime}|{gamma}"] = {
                "T_valid": sel[0]["T_valid"], "runs": len(sel),
                "crossed": len(tc), "median_cross_over_Tvalid": float(np.median(tc)) if tc else None,
                "breached": len(tb), "median_breach_over_Tvalid": float(np.median(tb)) if tb else None,
                "median_conservativeness": float(np.median(cons)) if cons else None,
                "median_peak_pre": float(np.median([r["peak_pre"] for r in sel])),
                "median_final_Phi": float(np.median([r["final_Phi"] for r in sel]))}
    return {"total_runs": len(runs), "p1_passes": int(sum(p1)), "p1_pass": bool(all(p1)),
            "p2_adversarial_runs": len(adv), "p2_hits": int(sum(p2_hits)),
            "p2_rate": float(np.mean(p2_hits)) if adv else None,
            "p2_pass": bool(adv and np.mean(p2_hits) >= spec["p2_threshold"]), "by_cell": by}


def write_numbers(res):
    lines = ["% generated by check_multiagent_v2.py; do not edit",
             f"\\newcommand{{\\MAvTwoRuns}}{{{res['total_runs']}}}",
             f"\\newcommand{{\\MAvTwoPonePasses}}{{{res['p1_passes']}}}",
             f"\\newcommand{{\\MAvTwoAdvRuns}}{{{res['p2_adversarial_runs']}}}",
             f"\\newcommand{{\\MAvTwoPtwoHits}}{{{res['p2_hits']}}}",
             f"\\newcommand{{\\MAvTwoPtwoRate}}{{{100 * res['p2_rate']:.1f}\\%}}",
             f"\\newcommand{{\\MAvTwoPtwoVerdict}}{{{'passed' if res['p2_pass'] else 'failed'}}}"]
    NUMBERS.write_text("\n".join(lines) + "\n")


def run():
    spec = json.loads(SPEC.read_text())
    sha = digest(SPEC)
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "spec hash mismatch"
    assert digest(Path(__file__)) == spec["runner_sha256"], "runner changed after registration"
    rel = str(SPEC.relative_to(ROOT))
    subprocess.run(["git", "fetch", "origin", "main"], cwd=ROOT, check=True, capture_output=True)
    registered = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, text=True).strip()
    assert registered, "specification is not committed"
    subprocess.run(["git", "merge-base", "--is-ancestor", registered, "origin/main"], cwd=ROOT, check=True)
    assert SPEC.read_bytes() == subprocess.check_output(["git", "show", f"origin/main:{rel}"], cwd=ROOT)
    assert json.loads(COUNTER.read_text())["opens"] == 0, "already opened"
    COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": registered,
                                   "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    runs = run_all(spec, spec["seed"], spec["reps"])
    res = summarize(spec, runs)
    res.update({"spec_sha256": sha, "runner_sha256": spec["runner_sha256"], "registration_commit": registered,
                "runs": runs})
    RESULT.write_text(json.dumps(res, indent=1) + "\n")
    write_numbers(res)
    print(json.dumps({k: v for k, v in res.items() if k not in ("runs", "by_cell")}, indent=1))


def check():
    spec = json.loads(SPEC.read_text())
    res = json.loads(RESULT.read_text())
    assert res["spec_sha256"] == digest(SPEC) == SPEC.with_suffix(".sha256").read_text().strip()
    assert res["runner_sha256"] == spec["runner_sha256"] == digest(Path(__file__))
    assert json.loads(COUNTER.read_text())["opens"] == 1
    runs = run_all(spec, spec["seed"], spec["reps"])        # deterministic re-run, same seeds
    again = summarize(spec, runs)
    for k in ("total_runs", "p1_passes", "p1_pass", "p2_hits", "p2_pass", "by_cell"):
        assert again[k] == res[k], k
    old = NUMBERS.read_text(); write_numbers(res); assert NUMBERS.read_text() == old
    print(f"B3v2 check: P1 {res['p1_passes']}/{res['total_runs']}; P2 {res['p2_hits']}/{res['p2_adversarial_runs']} "
          f"({'pass' if res['p2_pass'] else 'fail'}) — PASS (reproduced)")


def dev():
    spec = json.loads(SPEC.read_text()) if SPEC.exists() else json.loads((HERE / "prereg/multiagent_v2.draft.json").read_text())
    small = dict(spec, horizon_multiple=1)
    runs = run_all(small, 1, 1)
    assert all(r["max_weight_step"] <= r["gamma"] + 1e-12 for r in runs)
    print(f"dev smoke test ran {len(runs)} runs on seed 1; outcomes not printed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true"); g.add_argument("--check", action="store_true")
    g.add_argument("--dev", action="store_true")
    a = ap.parse_args()
    run() if a.run else check() if a.check else dev()
