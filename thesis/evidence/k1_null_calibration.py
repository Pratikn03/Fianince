"""Null and power calibration of Test K1 on synthetic panels (no market data): writes K1_null_calibration.json."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import k1_letf as K  # noqa: E402

res = K.calibrate()
summ = {"null_pass1": sum(r["pass1"] for r in res["null"]), "null_pass2": sum(r["pass2"] for r in res["null"]),
        "null_rank_test_below_05": sum(r["p_rank"] < 0.05 for r in res["null"]),
        "null_runs": len(res["null"]),
        "power": {s: {"pass1": sum(r["pass1"] for r in v), "pass2": sum(r["pass2"] for r in v), "runs": len(v),
                      "rank_test_below_05": sum(r["p_rank"] < 0.05 for r in v),
                      "median_S1_share": sorted(r["S1_median_share"] for r in v)[len(v) // 2]} for s, v in res["power"].items()}}
(HERE / "K1_null_calibration.json").write_text(json.dumps({"summary": summ, "runs": res}, indent=1) + "\n")
print(json.dumps(summ, indent=1))
