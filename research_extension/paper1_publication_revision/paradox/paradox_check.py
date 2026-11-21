"""Numerical check of Theorem n:paradox (surveillance paradox).

A group chooses its memory distance D in [0, D0] to its neighbour, paying k(D0-D)^2 + L*pi(c N D^n), where pi is the
power of the supervisor's level-alpha test as a function of the divergence J = c N D^n. Here pi is the exact power of
the Neyman-Pearson test in a Gaussian shift experiment with divergence J: Phi(sqrt(2J) - z_alpha). The script finds the
optimal D on a fine grid for N over twelve decades, and checks the two-sided bounds of the theorem and the rates.
"""
import numpy as np
from scipy.stats import norm

alpha = 0.05
z = norm.ppf(1 - alpha)
pi = lambda J: norm.cdf(np.sqrt(2 * J) - z)
beta = np.sqrt(2) * norm.pdf(z)            # pi(J) - alpha >= beta sqrt(J) for J <= Jbar (convex region)
Jbar = z ** 2 / 2
k, D0, L, c = 1.0, 1.0, 50.0, 1.0
assert L * beta * np.sqrt(Jbar) > k * D0 ** 2   # high stakes: condition of part (ii)
# check the lower power envelope on [0, Jbar] and beyond
Js = np.linspace(1e-12, 20, 200000)
assert np.all(pi(Js) - alpha >= beta * np.minimum(np.sqrt(Js), np.sqrt(Jbar)) - 1e-12)
assert np.all(pi(Js) - alpha <= np.sqrt(Js / 2) + 1e-12)   # Pinsker: power - size <= TV <= sqrt(KL/2)

for n in (6, 10):
    rows = []
    for N in np.logspace(2, 14, 13):
        # optimum on a log-spaced grid refined around the best point
        D = np.concatenate([np.logspace(-8, 0, 200001) * D0])
        obj = k * (D0 - D) ** 2 + L * pi(c * N * D ** n)
        i = int(np.argmin(obj)); Ds = D[i]
        Dg = np.linspace(D[max(i - 2, 0)], D[min(i + 2, len(D) - 1)], 20001)
        obj = k * (D0 - Dg) ** 2 + L * pi(c * N * Dg ** n)
        Ds = Dg[int(np.argmin(obj))]
        Js_ = c * N * Ds ** n
        up = (2 * k * D0 / (L * beta)) ** 2 / (c * N)                    # D^{n-2} upper bound (squared form)
        lo = 2 * k ** 2 * D0 ** 2 / (2 ** n * L ** 2 * c * N)            # D^{n-2} lower bound
        ok_up = Ds ** (n - 2) <= up * (1 + 1e-6)
        ok_lo = (Ds > D0 / 3) or (Ds ** (n - 2) >= lo * (1 - 1e-6))
        rows.append((N, Ds, Js_, pi(Js_), ok_up, ok_lo))
    Ns = np.array([r[0] for r in rows]); Js_all = np.array([r[2] for r in rows]); Ds_all = np.array([r[1] for r in rows])
    big = Ns >= 1e6
    sJ = np.polyfit(np.log(Ns[big]), np.log(Js_all[big]), 1)[0]
    sD = np.polyfit(np.log(Ns[big]), np.log(Ds_all[big]), 1)[0]
    assert all(r[4] and r[5] for r in rows), rows
    print(f"n={n}: bounds hold for N=1e2..1e14; fitted slope of log J* on log N = {sJ:.3f} "
          f"(theory {-2/(n-2):.3f}); of log D* = {sD:.3f} (theory {-1/(n-2):.3f}); "
          f"detection at N=1e14: {rows[-1][3]:.4f} (alpha {alpha})")
    for r in rows[::3]:
        print(f"   N={r[0]:.0e}  D*={r[1]:.3e}  J*={r[2]:.3e}  power={r[3]:.4f}")
