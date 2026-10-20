"""Paper 1: recompute the capital numbers that were 'earlier scripts' (Tables capbounds, ledger).
Model and calibration as in recompute_theory.py: a=0.5, kappa=0.8, q=0.2, eta=0.4, sigma=0.01,
P*=100, taker fee phi=4bp, maintenance margin mu=0.5%, alpha=beta=0.05."""
import numpy as np, json
from scipy.stats import norm
from scipy.linalg import eigh, toeplitz
from scipy.optimize import minimize
a, k, q, eta, sig, P, phi, mu = 0.5, 0.8, 0.2, 0.4, 0.01, 100.0, 4e-4, 0.005
z = norm.ppf(0.95); KL_T = 0.5 * (2 * z) ** 2; creq = 4 * sig ** 2 * z ** 2
kl = 0.05 * np.log(0.05 / 0.95) + 0.95 * np.log(0.95 / 0.05)
def imp(ws, rs, L=600):
    y = np.zeros(len(ws)); h = []; xp = 0.0
    for t in range(L):
        xt = a * xp + k * np.dot(ws, y) + (k if t == 0 else 0.0); y = (1 - rs) * y + rs * xt; h.append(xt); xp = xt
    return np.array(h)
def pair(d, L=600):
    return imp(np.array([q]), np.array([eta]), L), imp(np.array([q / 2, q / 2]), np.array([eta - d, eta + d]), L)
def Hh(h, om):
    return np.exp(-1j * np.outer(om, np.arange(len(h)))) @ h
def conv(h, v, n):
    return np.convolve(h[:n], v)[:n]
def err_of(dp):
    return float(norm.cdf(-np.sqrt((dp @ dp) / (2 * sig ** 2) / 2)))
def ledger(v, h, tail=200):
    """Synthetic account: fills at the average linear-book price, marks at the prevailing price, taker fee phi,
    maintenance margin mu*mark*|I|. Returns C0 = max_t(margin_t - equity_t), peak margin, end inventory."""
    n = len(v) + tail; vv = np.r_[v, np.zeros(tail)]
    disp = conv(h, vv, n)                                 # displacement after each trade
    pre = disp - h[0] * vv                                # displacement before the trade at t
    fill = P + pre + 0.5 * h[0] * vv
    cash = -np.cumsum(vv * fill + phi * P * np.abs(vv)); I = np.cumsum(vv); mark = P + disp
    equity = cash + I * mark; margin = mu * mark * np.abs(I)
    return float(np.max(margin - equity)), float(margin.max()), float(I[-1])
out = {"capbounds": {}, "ledger": {}}
om = np.linspace(1e-4, np.pi, 40001)
for d in [0.02, 0.03, 0.05, 0.08, 0.10, 0.15]:
    h0, h1 = pair(d); H0, dH = Hh(h0, om), Hh(h1, om) - Hh(h0, om)
    ratio = (H0.real - k / 2) / np.abs(dH) ** 2; i = np.argmin(ratio)
    Cq = creq * ratio[i]
    fee_lb = phi * P * 2 * sig * z / np.abs(dH).max()     # ||v||_1 >= ||v||_2 >= 2 sigma z / sup|dH|
    # feasible upper bound: flat probes on horizon L, start from the top generalized eigenvector, refine
    best = None
    for L in [120, 160, 240]:
        n = L + 200
        T0 = toeplitz(h0[:L]); G = 0.5 * (T0 + T0.T)
        Dm = toeplitz(np.r_[h1[0] - h0[0], np.zeros(L - 1)], (h1 - h0)[:n])  # placeholder (unused)
        Hd = np.array([np.r_[np.zeros(j), (h1 - h0)[:n - j]] for j in range(L)]).T   # n x L
        E = np.eye(L)[:, :-1] - np.eye(L)[:, 1:]                                  # flat (zero-sum) basis
        Gr = E.T @ G @ E; Mr = E.T @ (Hd.T @ Hd) @ E
        w, V = eigh(Mr, Gr); x = V[:, -1]; v = E @ x
        v *= np.sqrt(creq / ((Hd @ v) @ (Hd @ v)))
        def cost(vf):
            c0 = max(ledger(vf, h0)[0], ledger(vf, h1)[0]); return c0
        def cons(xr):
            vf = E @ xr; return (Hd @ vf) @ (Hd @ vf) - creq
        x0 = np.linalg.lstsq(E, v, rcond=None)[0]
        if d == 0.05 or L == 240:
            res = minimize(lambda xr: cost(E @ xr), x0, constraints=[{"type": "ineq", "fun": cons}], method="SLSQP",
                           options={"maxiter": 300, "ftol": 1e-9})
            vf = E @ res.x if res.success or cons(res.x) >= -1e-12 else v
        else:
            vf = v
        c_eig = cost(v); c_opt = cost(vf)
        rec = {"L": L, "C0_eigvec": c_eig, "C0_refined": c_opt, "maxtrade_eig": float(np.abs(v).max()),
               "maxtrade_ref": float(np.abs(vf).max()), "gross_ref": float(np.abs(vf).sum()), "err_ref": err_of(Hd @ vf)}
        if best is None or c_opt < best["C0_refined"]:
            best = rec
        if d == 0.05:
            out["ledger"][f"eigvec_L{L}"] = rec
    out["capbounds"][str(d)] = {"omega_star": float(om[i]), "C_quad": float(Cq), "fee_lb": float(fee_lb),
                                "C_certified": float(Cq + fee_lb), "adaptive_LB": float(2 * sig ** 2 * kl * ratio[i] + fee_lb),
                                "adaptive_LB_feefree": float(2 * sig ** 2 * kl * ratio[i]), "feasible_UB": best}
    print(d, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in out["capbounds"][str(d)].items() if kk != "feasible_UB"},
          "UB", round(best["C0_refined"], 3), "L", best["L"])
# pulse designs at delta = 0.05 (T = 20 spacing, V_eff = 6.25)
h0, h1 = pair(0.05); V = 6.25
def design(spec):
    # spacing recovered from the earlier version: pulses every 40 steps, each sold 20 steps later
    if spec == "12 buys never unwound":
        v = np.zeros(240); v[::20] = V
    elif spec.endswith("round trips"):
        n = int(spec.split()[0]); v = np.zeros(40 * n + 20); v[0:40 * n:40] = V; v[20:40 * n + 20:40] -= V
    elif spec == "12 buys each unwound after 20 steps":
        v = np.zeros(40 * 12 + 20); v[0:480:40] += V; v[20:500:40] -= V
    return v
for spec in ["12 buys never unwound", "6 round trips", "5 round trips", "12 buys each unwound after 20 steps"]:
    v = design(spec); n = len(v) + 200
    dp = conv(h1, np.r_[v, np.zeros(200)], n) - conv(h0, np.r_[v, np.zeros(200)], n)
    c = [ledger(v, h) for h in (h0, h1)]
    out["ledger"][spec] = {"C0": max(c[0][0], c[1][0]), "error": err_of(dp), "KL": float(dp @ dp / (2 * sig ** 2)),
                           "end_inventory": c[0][2], "peak_margin": max(c[0][1], c[1][1]), "trades": int((v != 0).sum())}
    print(spec, {kk: round(vv, 4) for kk, vv in out["ledger"][spec].items()})
json.dump(out, open("recomputed/R_P1_capital_ledger.json", "w"), indent=1, default=float)
