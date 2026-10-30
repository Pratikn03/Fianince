"""Producer for the quadratic column of Table 5 (creq / lambda_max on flat probes) at every horizon, including
L = 320 and 480, which previously existed only in R_P1_cquadL.json without a script. Same model and constants as
rh_bound.py. Writes R_P1_cquadL_reproduced.json and prints the comparison with the archived values."""
import json
import numpy as np
from scipy.linalg import eigh, toeplitz
import rh_bound as rb

def quad(L, d=0.05):
    taps = L + 1200
    h0 = rb.imp(np.array([rb.q]), np.array([rb.eta]), L=taps)
    h1 = rb.imp(np.array([rb.q / 2, rb.q / 2]), np.array([rb.eta - d, rb.eta + d]), L=taps)
    n = L + 600
    Q = 0.5 * toeplitz(h0[:L])
    Hd = np.array([np.r_[np.zeros(j), (h1 - h0)[:n - j]] for j in range(L)]).T
    E = np.eye(L)[:, :-1] - np.eye(L)[:, 1:]
    lam = eigh(E.T @ (Hd.T @ Hd) @ E, E.T @ Q @ E, eigvals_only=True)
    return float(rb.creq / lam[-1])

out = {str(L): quad(L) for L in (80, 120, 160, 240, 320, 480)}
old = json.load(open("../recomputed/R_P1_cquadL.json"))
json.dump(out, open("R_P1_cquadL_reproduced.json", "w"), indent=1)
for k, v in out.items():
    print(k, round(v, 4), "archived", round(old[k], 4), "diff", f"{v - old[k]:.2e}")
