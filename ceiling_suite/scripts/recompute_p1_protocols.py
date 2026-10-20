"""Paper 1: recompute the remaining 'earlier scripts' numbers. Calibration: a=0.5, kappa=0.8, q=0.2, eta=0.4, sigma=0.01,
V_eff=6.25, P*=100, fee 4bp, initial margin 0.5% of notional, alpha=beta=0.05, symmetric split H1: (q/2, eta+-delta)."""
import numpy as np, json
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.linalg import eigh
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
V = 6.25; za = norm.ppf(0.95); out = {}
pulse_cost = lambda v: 0.5 * k * v ** 2 + phi * P * v                 # one-leg benchmark cost per pulse
margin0 = lambda v: mu * P * v
def dT(dl, T):
    h0, h1 = pair(dl, 400); return (h1 - h0)[:T]
# 1) resolution floors: V_eff ||d_T(delta)|| = 2 sigma z
out["floors"] = {}
for T in [3, 4, 10, 20, 100]:
    out["floors"][T] = brentq(lambda d: V * np.linalg.norm(dT(d, T)) - 2 * sig * za, 1e-3, 0.45)
print("floors:", {T: round(v, 4) for T, v in out["floors"].items()})
# 2) disclosure contracts (closed forms)
dl = 0.05; dE = lambda v: k ** 2 * q * dl ** 2 * v ** 2
v_round = np.sqrt(0.01 / (k ** 2 * q * dl ** 2))
out["contracts"] = {"I3_exact_V5": pulse_cost(5) + margin0(5), "I3_round_V": v_round, "I3_round": pulse_cost(v_round) + margin0(v_round)}
for T in [3, 4, 20, 100]:
    n = int(np.ceil(4 * sig ** 2 * za ** 2 / (V ** 2 * np.linalg.norm(dT(dl, T)) ** 2)))
    out["contracts"][f"I0_T{T}"] = {"pulses": n, "capital": n * pulse_cost(V) + margin0(V) / 2 if False else n * pulse_cost(V) + 3.125}
print("contracts:", out["contracts"])
# 3) protocols at T = 4 per cycle (2,000 replications each)
rng = np.random.default_rng(20261019); REPS = 2000; T = 4
A_, B_ = np.log(0.95 / 0.05), np.log(0.05 / 0.95)
prot = {}
for dl in [0.03, 0.05, 0.08, 0.12]:
    d = dT(dl, T); nd = np.linalg.norm(d)
    def run_fixed(v_unit, n_rep):
        # n_rep cycles of a probe with response difference v_unit * d; Gaussian likelihood-ratio test at threshold 0
        errs = []
        for truth in (0, 1):
            mean = (truth - 0.5) * v_unit ** 2 * nd ** 2 / sig ** 2 * n_rep
            sd = abs(v_unit) * nd / sig * np.sqrt(n_rep)
            llr = rng.normal(mean, sd, REPS); errs.append(np.mean(llr < 0) if truth == 1 else np.mean(llr > 0))
        return float(np.mean(errs))
    # A: one unconstrained pulse
    vA = 2 * sig * za / nd; eA = run_fixed(vA, 1)
    # B: repeated capped pulses
    nB = int(np.ceil(4 * sig ** 2 * za ** 2 / (V ** 2 * nd ** 2))); eB = run_fixed(V, nB)
    # C: sequential probability-ratio test with capped pulses
    nC, errC = [], []
    for truth in (0, 1):
        for _ in range(REPS):
            llr, n = 0.0, 0
            while B_ < llr < A_:
                n += 1; mean = (truth - 0.5) * V ** 2 * nd ** 2 / sig ** 2
                llr += rng.normal(mean, V * nd / sig)
            nC.append(n); errC.append((llr >= A_) if truth == 0 else (llr <= B_))
    # D: generalized-eigenvector cycle (flat, length T+1, max |trade| capped at V), repeated until the KL target is met
    L = T + 1; h0, h1 = pair(dl, 400)
    Hd = np.array([np.r_[np.zeros(j), (h1 - h0)[:L + T - j]] for j in range(L)]).T
    E = np.eye(L)[:, :-1] - np.eye(L)[:, 1:]; from scipy.linalg import toeplitz
    G = toeplitz(h0[:L]); G = 0.5 * (G + G.T)
    w_, Vv = eigh(E.T @ Hd.T @ Hd @ E, E.T @ G @ E); vD = E @ Vv[:, -1]; vD *= V / np.abs(vD).max() * 0.6
    infoD = (Hd @ vD) @ (Hd @ vD); nD = int(np.ceil(4 * sig ** 2 * za ** 2 / infoD))
    lossD = 0.5 * vD @ (toeplitz(h0[:L]) @ vD)
    eD = run_fixed(1.0, 1) if False else float(norm.cdf(-np.sqrt(nD * infoD) / (2 * sig)))
    prot[dl] = {"A": {"volume": vA, "max_trade": vA, "error": eA, "capital": pulse_cost(vA) + margin0(vA)},
                "B": {"volume": nB * V, "max_trade": V, "error": eB, "capital": nB * pulse_cost(V) + 3.125},
                "C": {"volume": float(np.mean(nC)) * V, "max_trade": V, "error": float(np.mean(errC)),
                      "capital": float(np.mean(nC)) * pulse_cost(V) + 3.125, "mean_pulses": float(np.mean(nC))},
                "D": {"volume": nD * np.abs(vD).sum(), "max_trade": float(np.abs(vD).max()), "error": eD,
                      "capital": nD * (lossD + phi * P * np.abs(vD).sum()) + margin0(np.abs(np.cumsum(vD)).max())}}
    print(dl, {p: {kk: round(vv, 3) for kk, vv in x.items()} for p, x in prot[dl].items()})
dls = np.log([0.03, 0.05, 0.08, 0.12])
out["protocol_slopes"] = {p: float(np.polyfit(dls, np.log([prot[d][p]["capital"] for d in [0.03, 0.05, 0.08, 0.12]]), 1)[0]) for p in "ABCD"}
out["protocols"] = {str(k_): v for k_, v in prot.items()}
print("capital slopes:", {p: round(s, 2) for p, s in out["protocol_slopes"].items()})
json.dump(out, open("recomputed/R_P1_protocols.json", "w"), indent=1, default=float)
