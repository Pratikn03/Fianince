"""Paper 1: value of class-tagged disclosure. Same noise and the same lags for both observers:
 price-only observes the merged kernel k_m = sum_i w_i r_i^m + e;  tagged observes each class kernel w_i r_i^m + e_i.
 Cramer-Rao: N days needed so that sd(r_i) <= Delta/4 (rates resolved) and sd(w_i) <= w_i/10 (weights)."""
import numpy as np, json
def jac_merged(w, r, L):
    m = np.arange(L)[:, None]
    return np.hstack([r[None, :] ** m, w[None, :] * m * r[None, :] ** np.maximum(m - 1, 0)])   # d/dw, d/dr
def crb(Jm, sig):
    F = Jm.T @ Jm / sig ** 2; return np.linalg.inv(F)
L, sig = 288, 1.0; out = {}
for rc in [0.95, 0.99]:
    rows = []
    for D in [0.002, 0.004, 0.008, 0.016, 0.032]:
        r = np.array([rc - D / 2, rc + D / 2]); w = np.array([0.5, 0.5])
        Cp = crb(jac_merged(w, r, L), sig)
        Ct = np.zeros((4, 4))
        for i in range(2):                                    # tagged: two separate single-class kernels
            Ci = crb(jac_merged(w[i:i + 1], r[i:i + 1], L), sig); Ct[np.ix_([i, 2 + i], [i, 2 + i])] = Ci
        need = lambda C: max(max(C[2 + i, 2 + i] / (D / 4) ** 2 for i in range(2)), max(C[i, i] / (w[i] / 10) ** 2 for i in range(2)))
        Np, Nt = need(Cp), need(Ct)
        rows.append({"Delta": D, "N_price_days": Np, "N_tagged_days": Nt, "ratio": Np / Nt})
    sl = np.polyfit(np.log([x["Delta"] for x in rows]), np.log([x["ratio"] for x in rows]), 1)[0]
    slp = np.polyfit(np.log([x["Delta"] for x in rows]), np.log([x["N_price_days"] for x in rows]), 1)[0]
    slt = np.polyfit(np.log([x["Delta"] for x in rows]), np.log([x["N_tagged_days"] for x in rows]), 1)[0]
    out[str(rc)] = {"rows": rows, "slope_ratio": sl, "slope_price": slp, "slope_tagged": slt}
    print(f"r_c={rc}: slopes  price {slp:.2f}  tagged {slt:.2f}  ratio {sl:.2f}")
    for x in rows: print("   ", {k: f"{v:.3g}" for k, v in x.items()})
json.dump(out, open("R_P1_disclosure_value.json", "w"), indent=1)
