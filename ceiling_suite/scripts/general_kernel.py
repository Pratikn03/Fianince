"""Paper 1, general completely monotone memory: k_m = int r^m dmu(r), mu on [0, rho].
Two n-atom measures (Gauss and Gauss-Radau rules mapped to [0, rho]) match moments 0..2n-2.
Prices see k_m for all m, so the identifying signal is ||k^A - k^B||_2 over m >= 0. Shows it decays geometrically
in n while the Wasserstein-1 distance between the measures decays only like 1/n. Hence N >= sigma^2 theta^{-n} = exp(c/W1)."""
import numpy as np, json
from numpy.polynomial import legendre
from scipy.stats import wasserstein_distance
def radau(n):
    # Gauss-Radau nodes on [-1,1] with fixed node -1: roots of (P_{n-1}(x) + P_n(x)) / (1 + x)
    c = np.zeros(n + 1); c[n - 1] = 1; c[n] = 1
    x = np.sort(np.real(legendre.legroots(c)))
    V = np.vstack([x ** k for k in range(n)]); mom = np.array([(1 - (-1) ** (k + 1)) / (k + 1) for k in range(n)])
    w = np.linalg.solve(V, mom); return x, w
out = {}
for rho in [0.9, 0.99]:
    rows = []
    for n in range(2, 11):
        xa, wa = legendre.leggauss(n); xb, wb = radau(n)
        ra, rb = rho * (xa + 1) / 2, rho * (xb + 1) / 2; wa, wb = wa / wa.sum(), wb / wb.sum()
        M = 5000; m = np.arange(M)[:, None]
        dk = (wa * ra ** m).sum(1) - (wb * rb ** m).sum(1)
        low = max(abs(np.sum(wa * ra ** j) - np.sum(wb * rb ** j)) for j in range(2 * n - 1))
        rows.append({"n": n, "l2_kernel_diff": float(np.sqrt(dk @ dk)), "W1": float(wasserstein_distance(ra, rb, wa, wb)),
                     "max_low_moment_gap": float(low), "min_radau_weight": float(wb.min())})
    th = np.exp(np.polyfit([r["n"] for r in rows], np.log([r["l2_kernel_diff"] for r in rows]), 1)[0])
    out[str(rho)] = {"rows": rows, "theta_per_atom": float(th)}
    print(f"rho={rho}: ||dk||_2 shrinks by a factor {th:.3f} per extra atom")
    for r in rows: print("   ", {k: f"{v:.3g}" for k, v in r.items()})
json.dump(out, open("R_P1_general_kernel.json", "w"), indent=1)
