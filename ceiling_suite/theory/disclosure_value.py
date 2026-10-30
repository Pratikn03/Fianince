"""Paper 1: value of class-tagged disclosure. Same noise and the same lags for both observers:
 price-only observes the merged kernel k_m = sum_i w_i r_i^m + e;  tagged observes each class kernel w_i r_i^m + e_i.
 Cramer-Rao: N days needed so that sd(r_i) <= Delta/4 (rates resolved) and sd(w_i) <= w_i/10 (weights).
 Also computes the calibrated BTCUSDT and ETHUSDT two-class disclosure ratios from Table 8."""
import os, json
import numpy as np

def jac_merged(w, r, L):
    m = np.arange(L)[:, None]
    return np.hstack([r[None, :] ** m, w[None, :] * m * r[None, :] ** np.maximum(m - 1, 0)])   # d/dw, d/dr

def crb(Jm, sig):
    F = Jm.T @ Jm / sig ** 2
    return np.linalg.inv(F)

def compute_days(w, r, D, L=288, sig=1.0):
    Cp = crb(jac_merged(w, r, L), sig)
    Ct = np.zeros((4, 4))
    for i in range(2):
        Ci = crb(jac_merged(w[i:i + 1], r[i:i + 1], L), sig)
        Ct[np.ix_([i, 2 + i], [i, 2 + i])] = Ci
    need = lambda C: float(max(
        max(C[2 + i, 2 + i] / (D / 4) ** 2 for i in range(2)),
        max(C[i, i] / (w[i] / 10) ** 2 for i in range(2)),
    ))
    Np, Nt = need(Cp), need(Ct)
    return Np, Nt, Np / Nt

if __name__ == "__main__":
    L, sig = 288, 1.0
    out = {}
    for rc in [0.95, 0.99]:
        rows = []
        # memory rates must stay inside (0, 1): drop spacings that would push rc + D/2 to 1 or above
        for D in [x for x in [0.002, 0.004, 0.008, 0.016, 0.032] if rc + x / 2 < 1]:
            r = np.array([rc - D / 2, rc + D / 2])
            assert 0 < r.min() and r.max() < 1
            w = np.array([0.5, 0.5])
            Np, Nt, ratio = compute_days(w, r, D, L=L, sig=sig)
            rows.append({"Delta": D, "N_price_days": Np, "N_tagged_days": Nt, "ratio": ratio})
        sl = float(np.polyfit(np.log([x["Delta"] for x in rows]), np.log([x["ratio"] for x in rows]), 1)[0])
        slp = float(np.polyfit(np.log([x["Delta"] for x in rows]), np.log([x["N_price_days"] for x in rows]), 1)[0])
        slt = float(np.polyfit(np.log([x["Delta"] for x in rows]), np.log([x["N_tagged_days"] for x in rows]), 1)[0])
        out[str(rc)] = {"rows": rows, "slope_ratio": sl, "slope_price": slp, "slope_tagged": slt}
        print(f"r_c={rc}: slopes  price {slp:.2f}  tagged {slt:.2f}  ratio {sl:.2f}")

    # Calibrated stage from Binance 5-minute trader-position persistence estimates (P1.4-R2):
    # BTCUSDT: top_pos r = 0.9889, all_accts r = 0.9986; ETHUSDT: top_pos r = 0.9793, all_accts r = 0.9972
    calib = {}
    for sym, r_top, r_all in [("BTCUSDT", 0.9889, 0.9986), ("ETHUSDT", 0.9793, 0.9972)]:
        D = float(r_all - r_top)
        r = np.array([r_top, r_all])
        w = np.array([0.5, 0.5])
        Np, Nt, ratio = compute_days(w, r, D, L=L, sig=sig)
        calib[sym] = {
            "r_top_pos": r_top,
            "r_all": r_all,
            "Delta": D,
            "N_price_days": Np,
            "N_tagged_days": Nt,
            "ratio": ratio,
        }
    out["calibrated"] = calib
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "R_P1_disclosure_value.json"), "w"), indent=1)
