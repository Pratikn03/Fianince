"""Simulation validation of the P7S executor, amendment A1. Simulated markets only; no market data.

Each simulated data set has 30 symbols on a 5-minute grid: 30 days of warm-up, 92 development days and an evaluation
window (90 days by default; the third argument changes it).
Returns have a common factor and common jumps (market-wide stress), and open interest has a common slow component,
so symbols and days are dependent, as in real crypto data.

Cases:
  two_layer : feedback flow is capped when open interest is near its 30-day maximum; the cap binds only after large
              moves. Expected: calm silent, stress differs -> 'supportive'.
  linear    : no cap. Expected: H2 rejects in about 5% of data sets at most; never 'supportive' beyond that rate.
  cap_flat  : a cap that does not depend on open interest. Expected: as 'linear' (a null for the DiD).
  calm_leak : a cap so tight when open interest is high that it binds in ordinary moves. Expected: H1 fails.
Usage: python3 validate_p7s_A1.py [n_null] [n_alt] [holdout_days] [shift_step_days]
       -> validate_p7s_A1_results_hold{holdout_days}.json
"""
import json, sys, time
import numpy as np
import p7s_executor_A1 as ex

N_SYM, WARM, DEV, HOLD = 30, 30, 92, 90
STEP = 5
CAP = 0.0015   # binds only after moves several times the usual size
BPD = ex.BARS_PER_DAY


def simulate(seed: int, case: str):
    rng = np.random.default_rng(seed)
    T = (WARM + DEV + HOLD) * BPD
    # open-interest value: slow log AR(1) with a common component
    phi = 0.9995
    gc = rng.standard_normal(T) * 0.004; gi = rng.standard_normal((T, N_SYM)) * 0.004
    lv = np.zeros((T, N_SYM)); c = 0.0; x = np.zeros(N_SYM)
    for t in range(1, T):
        c = phi * c + gc[t]; x = phi * x + gi[t]; lv[t] = 0.7 * c + x
    oi = 1e9 * np.exp(lv)
    pi = np.column_stack([ex.proximity(oi[:, i].copy()) for i in range(N_SYM)])
    # returns: common factor, idiosyncratic noise, common jumps
    sig = 0.001
    innov = sig * (0.6 * rng.standard_normal(T)[:, None] + 0.8 * rng.standard_normal((T, N_SYM)))
    jump_t = np.where(rng.random(T) < 0.003)[0]
    for t in jump_t:
        innov[t] += rng.choice([-1.0, 1.0]) * rng.uniform(8, 15) * sig * (0.7 + 0.6 * rng.random(N_SYM))
    a, rho, w = 0.2, 0.7, 0.2
    r = np.zeros((T, N_SYM)); mem = np.zeros(N_SYM)
    near = np.nan_to_num(pi, nan=0.0) >= 0.93
    for t in range(1, T):
        mem = rho * mem + r[t - 1]
        flow = w * mem
        if case == "two_layer":
            flow = np.where(near[t], np.clip(flow, -CAP, CAP), flow)
        elif case == "cap_flat":
            flow = np.clip(flow, -CAP, CAP)
        elif case == "calm_leak":
            flow = np.where(near[t], np.clip(flow, -0.00002, 0.00002), flow)
        r[t] = a * r[t - 1] + flow + innov[t]
    close = 100 * np.exp(np.cumsum(r, axis=0))
    return close, oi


def run_case(seed: int, case: str, B: int = 999) -> dict:
    close, oi = simulate(seed, case)
    T = close.shape[0]
    day = np.arange(T) // BPD
    dev_mask = (day >= WARM) & (day < WARM + DEV)
    eval_mask = day >= WARM + DEV
    day_id = np.clip(day - (WARM + DEV), 0, HOLD - 1)
    S = np.zeros((N_SYM, HOLD, 4)); N = np.zeros((N_SYM, HOLD, 4)); bars = []
    for i in range(N_SYM):
        pi = ex.proximity(oi[:, i].copy())
        thr = ex.fit_thresholds(close[:, i], pi, dev_mask)
        S[i], N[i] = ex.symbol_cells(close[:, i], pi, day_id, eval_mask, thr, HOLD)
        bars.append(ex.symbol_bars(close[:, i], pi, eval_mask, thr))
    res = ex.evaluate(S, N, [f"S{i}" for i in range(N_SYM)], bars=bars, B=B, seed=ex.SEED, shift_step_days=STEP)
    res["boot_reject"] = bool(res["p_did_percentile_bootstrap_descriptive"] < 0.05)
    return {k: res[k] for k in ("verdict", "beta_calm_mean", "beta_calm_ci90", "beta_stress_mean", "did", "did_ci95",
                                "p_h2_stress_reveals", "h1_calm_silence", "h2_stress_reveals", "se_beta_calm", "se_did",
                                "n_symbols_used", "events_per_cell_total", "boot_reject")}


if __name__ == "__main__":
    n_null = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    n_alt = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    if len(sys.argv) > 3: HOLD = int(sys.argv[3])
    if len(sys.argv) > 4: STEP = int(sys.argv[4])
    out = {"design": {"symbols": N_SYM, "warmup_days": WARM, "development_days": DEV, "holdout_days": HOLD, "B": 999,
                      "E_margin": ex.E_MARGIN}, "cases": {}}
    t0 = time.time()
    for case, n, base in (("two_layer", n_alt, 1000), ("linear", n_null, 2000), ("cap_flat", n_alt, 3000), ("calm_leak", n_alt, 4000)):
        runs = [run_case(base + k, case) for k in range(n)]
        verd = [r["verdict"] for r in runs]
        out["cases"][case] = {
            "n": n, "verdicts": {v: verd.count(v) for v in sorted(set(verd))},
            "h2_reject_rate": float(np.mean([r["h2_stress_reveals"] for r in runs])),
            "percentile_bootstrap_reject_rate_descriptive": float(np.mean([r["boot_reject"] for r in runs])),
            "h1_pass_rate": float(np.mean([r["h1_calm_silence"] for r in runs])),
            "did_mean": float(np.mean([r["did"] for r in runs])), "did_sd_across_runs": float(np.std([r["did"] for r in runs])),
            "se_did_mean_reported": float(np.mean([r["se_did"] for r in runs])),
            "beta_calm_mean": float(np.mean([r["beta_calm_mean"] for r in runs])),
            "beta_calm_sd_across_runs": float(np.std([r["beta_calm_mean"] for r in runs])),
            "se_beta_calm_mean_reported": float(np.mean([r["se_beta_calm"] for r in runs])),
            "p_h2_all": [r["p_h2_stress_reveals"] for r in runs],
            "h2_reject_rate_at_0.025": float(np.mean([r["p_h2_stress_reveals"] < 0.025 for r in runs])),
            "h2_reject_rate_at_0.01": float(np.mean([r["p_h2_stress_reveals"] < 0.01 for r in runs])),
            "first_run": runs[0]}
        print(case, json.dumps({k: v for k, v in out["cases"][case].items() if k not in ("first_run", "p_h2_all")}), f"[{time.time() - t0:.0f}s]", flush=True)
    out["design"]["holdout_days"] = HOLD; out["design"]["shift_step_days"] = STEP
    json.dump(out, open(f"validate_p7s_A1_results_hold{HOLD}.json", "w"), indent=1)
