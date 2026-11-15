"""Amendment A1 extra check: a class that schema era E1 does not report (dealers' own account) runs end to end,
with E1 days NaN and fitting on the reported days only. Simulated data: the class copies a flow with no price
feedback, so its verdict must not be 'supportive'."""
import json
import numpy as np
import validate_executor as v
import p1t_executor as ex

days = v.fake_days(30, 1475, 0.1, 11)
for t, (d, t86, mi) in enumerate(days):
    f = t86["fields"]
    if "自營商買賣超股數(自行買賣)" in f:
        io, it, idt = f.index("自營商買賣超股數(自行買賣)"), f.index("投信買賣超股數"), f.index("自營商買賣超股數")
        for row in t86["data"]:
            row[io] = row[it]; row[idt] = row[it]
P = ex.build_panel(days); T = len(P.dates); dev = np.zeros(T, bool); dev[:985] = True
prep = ex.prepare(P, dev)
uo = prep["u"]["DealerOwn"][prep["U"]]
res = {"nan_share_E1": float(np.isnan(uo[:, :491]).mean()), "nan_share_E2_E3": float(np.isnan(uo[:, 492:]).mean()),
       "DealerOwn": ex.run_period(prep, dev, ~dev, "DealerOwn", B=199),
       "Foreign": ex.run_period(prep, dev, ~dev, "Foreign", B=199)}
res["passed"] = (res["nan_share_E1"] == 1.0 and res["nan_share_E2_E3"] == 0.0
                 and res["DealerOwn"]["verdict"] != "supportive" and res["Foreign"]["verdict"] == "supportive")
json.dump(res, open("validate_executor_A1_extra_results.json", "w"), indent=1)
print(json.dumps(res, indent=1))
