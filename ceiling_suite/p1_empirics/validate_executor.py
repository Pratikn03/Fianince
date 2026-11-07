"""Simulation validation of the P1T executor, required before the validation period is downloaded.

Builds fake TWSE T86 and MI_INDEX responses in the exact probed schema from the paper's recursion, runs the full
executor (parsing, universe, beta, market-reference basis, forecasts, bootstrap, verdict) and checks:
  (a) w = 0   (no price feedback into Foreign flow)  -> verdict is not 'supportive'
  (b) w = 0.1 (feedback)                             -> verdict is 'supportive'
"""
import json
import sys
import numpy as np

import p1t_executor as ex

FIELDS_T86 = ["證券代號", "證券名稱", "外陸資買進股數(不含外資自營商)", "外陸資賣出股數(不含外資自營商)",
              ex.T86_FIELDS["foreign_ex"], "外資自營商買進股數", "外資自營商賣出股數", ex.T86_FIELDS["foreign_dealer"],
              "投信買進股數", "投信賣出股數", ex.T86_FIELDS["trust"], "自營商買賣超股數",
              "自營商買進股數(自行買賣)", "自營商賣出股數(自行買賣)", ex.T86_FIELDS["dealer_own"],
              "自營商買進股數(避險)", "自營商賣出股數(避險)", ex.T86_FIELDS["dealer_hedge"], "三大法人買賣超股數"]
FIELDS_Q = ["證券代號", "證券名稱", "成交股數", "成交筆數", "成交金額", "開盤價", "最高價", "最低價", "收盤價",
            "漲跌(+/-)", "漲跌價差", "最後揭示買價", "最後揭示買量", "最後揭示賣價", "最後揭示賣量", "本益比"]


def simulate_market(N, T, w, seed, a=0.6, kappa=-0.6, r=0.8, shock=0.5, burn=300):
    rng = np.random.default_rng(seed)
    n = T + burn
    mkt = np.cumsum(0.01 * rng.standard_normal(n))
    x = np.zeros((N, n)); uF = np.zeros((N, n)); uO = np.zeros((N, n))
    for t in range(1, n):
        x[:, t] = a * x[:, t - 1] + kappa * 0.01 * (uF[:, t - 1] + uO[:, t - 1]) + 0.01 * rng.standard_normal(N)
        uF[:, t] = r * uF[:, t - 1] + w * 100 * x[:, t] + shock * rng.standard_normal(N)
        uO[:, t] = 0.5 * uO[:, t - 1] + 0.3 * rng.standard_normal(N)
    x, uF, uO, mkt = x[:, burn:], uF[:, burn:], uO[:, burn:], mkt[burn:]
    beta = rng.uniform(0.7, 1.3, N)
    logp = np.log(50) + beta[:, None] * mkt[None, :] + x
    vol = rng.uniform(5e5, 5e6, N)[:, None] * np.exp(0.2 * rng.standard_normal((N, T)))
    return logp, mkt, uF, uO, vol


def fake_days(N, T, w, seed):
    logp, mkt, uF, uO, vol = simulate_market(N, T, w, seed)
    codes = [f"{1101 + i}" for i in range(N)]
    days = []
    close = np.round(np.exp(logp), 2)
    for t in range(T):
        d = f"D{t:05d}"
        t86 = {"fields": FIELDS_T86, "data": []}
        q = {"fields": FIELDS_Q, "data": []}
        for i, c in enumerate(codes):
            fF = int(round(uF[i, t] * vol[i, t] / 10)); fO = int(round(uO[i, t] * vol[i, t] / 10))
            row = [c, "x"] + ["0"] * (len(FIELDS_T86) - 2)
            row[FIELDS_T86.index(ex.T86_FIELDS["foreign_ex"])] = f"{fF:,}"
            row[FIELDS_T86.index(ex.T86_FIELDS["trust"])] = f"{fO:,}"
            t86["data"].append(row)
            prev = close[i, t - 1] if t > 0 else close[i, t]
            sign = "<p style= color:red>+</p>" if close[i, t] >= prev else "<p style= color:green>-</p>"
            qr = [c, "x", f"{int(vol[i, t]):,}", "1", f"{int(vol[i, t] * close[i, t]):,}", "0", "0", "0",
                  f"{close[i, t]:.2f}", sign, "0", "0", "0", "0", "0", "0"]
            q["data"].append(qr)
        mi = {"tables": [{"title": "價格指數(臺灣證券交易所)", "fields": ["指數", "收盤指數"],
                          "data": [[ex.INDEX_NAME, f"{10000 * np.exp(mkt[t]):.2f}"]]},
                         {"title": "每日收盤行情(全部(不含權證、牛熊證、可展延牛熊證))", "fields": FIELDS_Q,
                          "data": q["data"]}]}
        days.append((d, t86, mi))
    return days


def one(w, seed, N=40, T_dev=985, T_eval=490, B=499):
    days = fake_days(N, T_dev + T_eval, w, seed)
    P = ex.build_panel(days)
    T = len(P.dates)
    dev = np.zeros(T, bool); dev[:T_dev] = True
    prep = ex.prepare(P, dev, top_n=300)
    return ex.run_period(prep, dev, ~dev, B=B, mean_block=20)


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    res = {"w0": [], "w01": []}
    for k in range(reps):
        res["w0"].append(one(0.0, 100 + k)); print("w=0  ", res["w0"][-1], flush=True)
        res["w01"].append(one(0.1, 200 + k)); print("w=0.1", res["w01"][-1], flush=True)
    ok = all(r["verdict"] != "supportive" for r in res["w0"]) and all(r["verdict"] == "supportive" for r in res["w01"])
    res["passed"] = ok
    json.dump(res, open("validate_executor_results.json", "w"), indent=1, ensure_ascii=False)
    print("VALIDATION", "PASSED" if ok else "FAILED")
