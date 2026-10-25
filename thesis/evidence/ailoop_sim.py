"""A market of learning trading agents and a vendor model, for Paper B ("supervising the loop, not the agents").

The market is the closed loop of the thesis on five-minute bars:
    x_{t+1} = a x_t + kappa (U_t + w_{t+1}) + eps_{t+1},   f_{t+1} = U_t + w_{t+1}   (observed flow),
with U_t the agents' total order flow. Agents trade on an exponential-memory signal y_i = EMA_{r_i}(x) through a
saturating rule u_i = L tanh(theta_i y_i / L). Two kinds of agent:
* independent learners: each has its own memory r_i and learns its response theta_i online (normalized LMS forecast of
  the next change in x, scaled by an aggressiveness lambda); with reverting prices they learn to trade against moves;
* vendor-model users: every user runs the same model, with memory r_D and a fixed momentum response theta_D (a
  pre-trained trend-following product). Users of one model act identically: they are one cohort.
Adoption: agents switch from their own learner to the vendor model at random times so that the adopted share ramps from
0 to s_max over the run (or stays at 0 in the control).
True linearized margin at time t: M(t) = 1 - a - kappa sum_i theta_i(t) (the small-signal slope of each rule; each
signal has unit DC gain). The observer sees only x and f and runs the thesis's pooled estimator on a rolling window of
W days: price equation (x_{t+1} - x_t on f_{t+1}, x_t) and flow equation (f_{t+1} on x_t..x_{t-11}), margin decided
safe if its 95% day-bootstrap interval lies above zero. The disclosure-augmented estimator adds to the flow equation the
signal EMA_{rbar}(x) at a disclosed memory bound rbar, whose coefficient enters the total feedback.
"""
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

BARS = 288


@dataclass
class Config:
    days: int = 120
    n_agents: int = 50
    a: float = 0.9
    kappa: float = 1.0
    s_eps: float = 0.5
    L: float = 2.0                 # flow limit per agent (saturation)
    lam: float = 1.0               # learners' aggressiveness: theta = lam * beta / n_agents_scale
    eta: float = 0.002             # learners' learning rate
    r_lo: float = 0.3              # learners' memory rates drawn uniformly in [r_lo, r_hi]
    r_hi: float = 0.95
    theta_D: float = 0.007         # vendor model's per-user response (momentum)
    r_D: float = 0.9               # vendor model's memory
    s_max: float = 0.8             # final adopted share (0: control)
    ramp_start: float = 0.2        # fraction of the run before adoption starts
    ramp_end: float = 0.8          # fraction of the run when s_max is reached
    window: int = 20               # estimator window, days
    lags: int = 12
    boot: int = 100
    seed: int = 0


def ema_coef(r):
    return 1.0 - r


def simulate(cfg: Config):
    rng = np.random.default_rng(cfg.seed)
    T = cfg.days * BARS; N = cfg.n_agents
    r = rng.uniform(cfg.r_lo, cfg.r_hi, N)
    beta = np.full(N, -0.1)                       # learners start mildly contrarian
    v = np.full(N, 1.0)
    y = np.zeros(N)
    # adoption times: agent j adopts at a uniform time within the ramp, for the first s_max*N agents in a random order
    order = rng.permutation(N); n_adopt = int(round(cfg.s_max * N))
    t_adopt = np.full(N, np.inf)
    t0, t1 = cfg.ramp_start * T, cfg.ramp_end * T
    t_adopt[order[:n_adopt]] = np.sort(rng.uniform(t0, t1, n_adopt))
    x = np.zeros(T + 1); f = np.zeros(T + 1); M_true = np.zeros(T); share = np.zeros(T)
    yD = 0.0; theta_at_ramp = None
    for t in range(T):
        adopted = t >= t_adopt
        theta = np.where(adopted, cfg.theta_D, cfg.lam * beta / N)
        if theta_at_ramp is None and t >= t0:
            theta_at_ramp = theta.copy()
        sig = np.where(adopted, yD, y)
        u = cfg.L * np.tanh(theta * sig / cfg.L)
        U = u.sum()
        M_true[t] = 1 - cfg.a - cfg.kappa * theta.sum(); share[t] = adopted.mean()
        w = rng.normal(); e = cfg.s_eps * rng.normal()
        f[t + 1] = U + w
        x[t + 1] = cfg.a * x[t] + cfg.kappa * f[t + 1] + e
        dx = x[t + 1] - x[t]
        # learners update their forecast of dx from their signal (normalized LMS), then their signals
        v = 0.999 * v + 0.001 * y ** 2
        beta = beta + cfg.eta * (dx - beta * y) * y / (v + 1e-6)
        beta = np.clip(beta, -5, 5)
        y = r * y + (1 - r) * x[t + 1]
        yD = cfg.r_D * yD + (1 - cfg.r_D) * x[t + 1]
    simulate.theta_at_ramp = theta_at_ramp
    return x, f, M_true, share


def static_threshold(cfg, theta_at_ramp):
    """Proposition prop:monoculture with the learners frozen at the start of adoption: s* = M(0) / (kappa N (q_D - qbar))."""
    if theta_at_ramp is None:
        return None
    N = cfg.n_agents; qbar = float(np.mean(theta_at_ramp)); M0 = 1 - cfg.a - cfg.kappa * N * qbar
    c = cfg.kappa * N * (cfg.theta_D - qbar)
    return float(M0 / c) if c > 0 else None


def day_stats(x, f, d, lags, rbar=None):
    """Sufficient statistics of the two regressions for day d (bars within the day only)."""
    lo, hi = d * BARS, (d + 1) * BARS
    t = np.arange(max(lo, lags), hi - 1)
    one = np.ones(len(t))
    Xp = np.column_stack([f[t + 1], x[t], one]); yp = x[t + 1] - x[t]       # day intercepts in both equations
    cols = [x[t - j] for j in range(lags)]
    if rbar is not None:
        cols.append(rbar[t])
    cols.append(one)
    Xf = np.column_stack(cols); yf = f[t + 1]
    return (Xp.T @ Xp, Xp.T @ yp), (Xf.T @ Xf, Xf.T @ yf)


def rolling_margin(x, f, cfg: Config, rbar_series=None, seed=0):
    """Daily rolling estimate of the margin with a day-bootstrap interval, over windows of cfg.window days."""
    D = len(x) // BARS
    st = [day_stats(x, f, d, cfg.lags, rbar_series) for d in range(D)]
    Ap = np.stack([s[0][0] for s in st]); bp = np.stack([s[0][1] for s in st])
    Af = np.stack([s[1][0] for s in st]); bf = np.stack([s[1][1] for s in st])
    rng = np.random.default_rng(seed + 7)
    out = []
    for d in range(cfg.window, D + 1):
        idx = np.arange(d - cfg.window, d)
        W = np.vstack([np.ones(cfg.window)] + [np.bincount(rng.integers(0, cfg.window, cfg.window), minlength=cfg.window)
                                               for _ in range(cfg.boot)]).astype(float)
        Ms = []
        for wts in W:
            try:
                pr = np.linalg.solve(np.tensordot(wts, Ap[idx], 1), np.tensordot(wts, bp[idx], 1))
                kf = np.linalg.solve(np.tensordot(wts, Af[idx], 1), np.tensordot(wts, bf[idx], 1))
                Ms.append(-pr[1] - pr[0] * kf[:-1].sum())          # drop the intercept
            except np.linalg.LinAlgError:
                Ms.append(np.nan)
        Ms = np.array(Ms); lo, hi = np.nanpercentile(Ms[1:], [2.5, 97.5])
        out.append({"day": d, "M_hat": float(Ms[0]), "lo": float(lo), "hi": float(hi)})
    return out


def ema_series(x, r):
    out = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = r * s + (1 - r) * v; out[i] = s
    return out


def summarize(cfg, x, f, M_true, share, est, est_disc=None):
    D = cfg.days
    Mday = M_true.reshape(D, BARS).mean(1); sday = share.reshape(D, BARS).mean(1)
    rv = np.array([np.sum(np.diff(x[d * BARS:(d + 1) * BARS + 1]) ** 2) for d in range(D)])
    mx = np.array([np.abs(x[d * BARS:(d + 1) * BARS]).max() for d in range(D)])
    nb = max(int(cfg.ramp_start * D), cfg.window)
    base = np.median(rv[:nb]); sd0 = np.std(x[:nb * BARS])
    crisis = next((d for d in range(D) if mx[d] > 10 * sd0), None)
    true_cross = next((d for d in range(D) if Mday[d] <= 0), None)

    def warn(e, buf=0.0):
        # first day the certificate of a margin above `buf` is lost (interval's lower end at or below buf)
        return next((r["day"] - 1 for r in e if r["lo"] <= buf), None) if e else None
    res = {"config": asdict(cfg), "crisis_day": crisis, "true_margin_cross_day": true_cross,
           "share_at_crisis": float(sday[crisis]) if crisis is not None else None,
           "s_star_static": static_threshold(cfg, getattr(simulate, "theta_at_ramp", None)),
           "warn_day": {str(b): warn(est, b) for b in (0.0, 0.05, 0.1, 0.2)},
           "warn_day_disclosed": {str(b): warn(est_disc, b) for b in (0.0, 0.05, 0.1, 0.2)} if est_disc else None,
           "M_true_start": float(Mday[cfg.window]), "M_true_end": float(Mday[-1]), "share_end": float(sday[-1]),
           "rv_base": float(base), "rv_max_ratio": float(rv.max() / base),
           "track": [{"day": r["day"] - 1, "M_true": float(Mday[r["day"] - 1]), "share": float(sday[r["day"] - 1]),
                      "M_hat": r["M_hat"], "lo": r["lo"], "hi": r["hi"],
                      **({"M_hat_disc": est_disc[i]["M_hat"], "lo_disc": est_disc[i]["lo"]} if est_disc else {})}
                     for i, r in enumerate(est)]}
    return res


def run(cfg, rbar=None):
    x, f, M_true, share = simulate(cfg)
    est = rolling_margin(x, f, cfg, seed=cfg.seed)
    est_d = rolling_margin(x, f, cfg, rbar_series=ema_series(x, rbar), seed=cfg.seed) if rbar else None
    return summarize(cfg, x, f, M_true, share, est, est_d)


if __name__ == "__main__":
    import sys
    cfg = Config(days=60, seed=1)
    r = run(cfg)
    print(json.dumps({k: v for k, v in r.items() if k != "track"}, indent=1))
