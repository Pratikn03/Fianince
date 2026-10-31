"""Power check for the October 2026 tests, on SYNTHETIC data only (no market data are read).
Writes prereg/P1O_power_check.json, which the specification cites. Run before registration."""
import json, os, numpy as np
from oct_core import feedback_oos, combined_response
HERE = os.path.dirname(os.path.abspath(__file__))
R = np.random.default_rng(20261031)
T = 30 * 288                                    # 30 days of 5-minute bars
day = np.arange(T) // 288
train, test = day < 20, day >= 20
out = {"n2_feedback": {}, "n3_combined": {}, "design": {"bars": T, "train_days": 20, "test_days": 10, "reps": 300}}
# N2: dy_t = 0.1 dy_{t-1} + b * sum_{j<6} 0.7^j r_{t-j} + e, unit-variance e, r with fat tails (t5);
# b chosen so the population R^2 gain of the return terms equals g.
for g in [0.0, 0.001, 0.002, 0.004, 0.008, 0.016]:
    rej = []
    for rep in range(300):
        r = R.standard_t(5, T) / np.sqrt(5 / 3)
        w = 0.7 ** np.arange(6); s2 = (w @ w)
        b = np.sqrt(g / (1 - g) / s2) if g > 0 else 0.0
        e = R.standard_normal(T); dy = np.zeros(T)
        conv = np.convolve(r, w)[:T]
        for t in range(1, T):
            dy[t] = 0.1 * dy[t - 1] + b * conv[t] + e[t]
        rej.append(feedback_oos(dy, r, train, test)["dm_p"] < 0.05)
    out["n2_feedback"][f"r2_gain_{g}"] = float(np.mean(rej))
# N3: x_t = Psi/12 * sum_{m=1..12} r_{t-m} + AR(1) noise (rho 0.3); signal-to-noise set by the population R^2 q.
for q in [0.0005, 0.001, 0.002, 0.004, 0.008]:
    hits = []
    for rep in range(300):
        r = R.standard_t(5, T) / np.sqrt(5 / 3)
        k = np.sqrt(q / (1 - q) / 12)
        u = np.zeros(T); eps = R.standard_normal(T) * np.sqrt(1 - 0.09)
        for t in range(1, T):
            u[t] = 0.3 * u[t - 1] + eps[t]
        x = k * np.r_[np.zeros(1), np.convolve(r, np.ones(12))[:T - 1]] + u
        res = combined_response(x, r, np.ones(T, bool))
        hits.append(res["ci"][0] > 0 and res["rel_halfwidth"] < 0.5)
    out["n3_combined"][f"r2_{q}"] = float(np.mean(hits))
json.dump(out, open(os.path.join(HERE, "prereg", "P1O_power_check.json"), "w"), indent=2)
print(json.dumps(out, indent=1))
