"""Checks of two elementary facts used in the upper-bound proof of the general-memory theorem."""
import numpy as np
from numpy.polynomial import chebyshev as C, polynomial as P
# (a) sum of |monomial coefficients| of T_j(alpha r - 1) <= ((1+sqrt2)(1+alpha))^j
worst = 0
for alpha in (2/0.5, 2/0.9, 2/0.99, 2.0):
    for j in range(0, 25):
        Tj = C.cheb2poly(np.eye(j + 1)[j])                  # T_j in y
        comp = P.polycompose = None
        # substitute y = alpha r - 1
        coef = np.zeros(1)
        for k, a in enumerate(Tj):
            coef = P.polyadd(coef, a * P.polypow([-1.0, alpha], k))
        ratio = np.abs(coef).sum() / (((1 + np.sqrt(2)) * (1 + alpha)) ** j)
        worst = max(worst, ratio)
print("max ratio sum|coef T_j(alpha r-1)| / ((1+sqrt2)(1+alpha))^j over j<=24:", worst)
# (b) kernel recovery K = (1 - a z - kappa/H)/(kappa z) from the closed-loop response
rng = np.random.default_rng(0); a, kappa = 0.5, 0.8
r = rng.uniform(0, 0.9, 5); w = rng.dirichlet(np.ones(5)) * 0.05
T = 40; k = np.array([np.sum(w * r ** m) for m in range(T)])
h = np.zeros(T); h[0] = kappa
for t in range(1, T):
    h[t] = a * h[t - 1] + kappa * np.sum(k[:t] * h[t - 1::-1][:t])
# series reciprocal of h mod z^T
inv = np.zeros(T); inv[0] = 1 / h[0]
for t in range(1, T):
    inv[t] = -np.sum(h[1:t + 1] * inv[t - 1::-1][:t]) / h[0]
num = -kappa * inv; num[0] += 1; num[1] -= a
k_rec = num[1:] / kappa
print("max |k_rec - k| over 39 lags:", np.max(np.abs(k_rec - k[:T - 1])))
s = a + kappa * w.sum() / (1 - 0.9)
print("||1/H||_1 =", np.abs(inv).sum(), "<= (1+s)/kappa =", (1 + s) / kappa)
