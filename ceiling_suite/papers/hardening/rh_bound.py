"""Paper 1, Theorem thm:rh: explicit finite-horizon Rayleigh--Holder bound with the closed-form
F_dom(theta), W_perp(theta), gamma(theta) of the revised statement. Calibration as in recompute_p1_capital.py."""
import numpy as np, json, sys
from scipy.stats import norm
from scipy.linalg import eigh, toeplitz
a, k, q, eta, sig, P, phi = 0.5, 0.8, 0.2, 0.4, 0.01, 100.0, 4e-4
z = norm.ppf(0.95); creq = 4 * sig ** 2 * z ** 2; cfee = phi * P
def imp(ws, rs, L=900):
    y = np.zeros(len(ws)); h = []; xp = 0.0
    for t in range(L):
        xt = a * xp + k * np.dot(ws, y) + (k if t == 0 else 0.0); y = (1 - rs) * y + rs * xt; h.append(xt); xp = xt
    return np.array(h)
def psi(F, W, g):
    """min_{x>=0} x^2 + max(0, F(1-g x^2)_+ - sqrt(W) x), evaluated exactly on a fine x grid plus stationary points."""
    sw = np.sqrt(W); xs = [0.0]
    xb = 1 / np.sqrt(g) if g > 0 else np.inf
    c1 = 1 - g * F
    if c1 > 0: xs.append(min(sw / (2 * c1), xb))
    if np.isfinite(xb): xs.append(xb); xs.append(max(xb, sw / 2))
    # piece where F(1-gx^2)-sqrt(W)x changes sign: root of F - g F x^2 - sw x = 0
    if g * F > 0:
        r = (-sw + np.sqrt(sw ** 2 + 4 * g * F * F)) / (2 * g * F); xs.append(r)
    elif sw > 0: xs.append(F / sw)
    xs += list(np.linspace(0, max(xs[1:] + [1.0]) * 2, 4001))
    f = lambda x: x * x + max(0.0, F * max(0.0, 1 - g * x * x) - sw * x)
    return min(f(x) for x in xs)
def crh(L, d=0.05, nth=3600):
    h0 = imp(np.array([q]), np.array([eta])); h1 = imp(np.array([q / 2, q / 2]), np.array([eta - d, eta + d]))
    n = L + 600
    Q = 0.5 * toeplitz(h0[:L])
    Hd = np.array([np.r_[np.zeros(j), (h1 - h0)[:n - j]] for j in range(L)]).T
    E = np.eye(L)[:, :-1] - np.eye(L)[:, 1:]
    G = E.T @ Q @ E; M = E.T @ (Hd.T @ Hd) @ E
    lam, V = eigh(M, G)            # G-orthonormal: V^T G V = I
    lL, lL1 = lam[-1], lam[-2]
    EV = E @ V                     # columns E e_j
    best = np.inf; arg = None
    for th in np.linspace(0, np.pi, nth, endpoint=False):
        lt = lL1 * np.cos(th) ** 2 + lL * np.sin(th) ** 2
        dvec = np.cos(th) * EV[:, -2] + np.sin(th) * EV[:, -1]
        s = np.sign(dvec); L0 = creq / lt
        F = cfee * np.sqrt(L0) * np.abs(dvec).sum()
        wts = 1 - lam[:-2] / lt
        W = cfee ** 2 * np.sum((s @ EV[:, :-2]) ** 2 / wts)
        g = lam[-3] / ((lt - lam[-3]) * L0)
        val = L0 + psi(F, W, g)
        if val < best: best, arg = val, (th, F, W, g, L0)
    return dict(L=L, quad=float(creq / lL), C_RH=float(best), theta=float(arg[0]), F=float(arg[1]), W=float(arg[2]), gamma=float(arg[3]))
if __name__ == "__main__":
    out = [crh(L, nth=int(sys.argv[1]) if len(sys.argv) > 1 else 3600) for L in (80, 120, 160, 240)]
    for o in out: print(o)
    json.dump(out, open("R_P1_rh_explicit.json", "w"), indent=1)
