# P1T holdout: metadata-only diagnosis of the one day that failed the integrity gate (2019-04-29).
# Prints response status, table titles and row COUNTS only. It prints no price, volume, flow or index value.
# Computes no statistic. Run in any Colab session with the same Drive.
import json, gzip, os
from google.colab import drive
drive.mount("/content/drive")
ROOT = "/content/drive/MyDrive/P1T_raw"
SUFFIX, INDEX_NAME = "權證、牛熊證、可展延牛熊證))", "發行量加權股價指數"
def meta(sub, d):
    fn = os.path.join(ROOT, sub, d + ".json.gz")
    if not os.path.exists(fn):
        return {"file": "missing"}
    j = json.loads(gzip.open(fn).read())
    out = {"stat": j.get("stat"), "date": j.get("date"), "keys": sorted(j.keys()), "bytes": os.path.getsize(fn)}
    if sub == "MI":
        tabs = []
        for t in j.get("tables", []):
            fields = t.get("fields") or []; data = t.get("data") or []
            tabs.append({"title": (t.get("title") or "")[:60], "n_fields": len(fields), "n_rows": len(data),
                         "is_quote_table": (t.get("title") or "").endswith(SUFFIX) and "證券代號" in fields,
                         "has_index_row": any(str(r[0]).strip() == INDEX_NAME for r in data) if data else False})
        out["tables"] = tabs
    else:
        out["n_rows"] = len(j.get("data") or []); out["n_fields"] = len(j.get("fields") or [])
    return out
report = {d: {"MI": meta("MI", d), "T86": meta("T86", d)} for d in ("20190426", "20190429", "20190430")}
man = [json.loads(l) for l in open(os.path.join(ROOT, "manifest.jsonl")) if "20190429" in l]
report["manifest_entries_20190429"] = [{"path": m["path"], "utc": m["utc"], "sha256": m["sha256"][:16]} for m in man]
print(json.dumps(report, indent=1, ensure_ascii=False))
json.dump(report, open("p1t_gate_diagnosis.json", "w"), indent=1, ensure_ascii=False)
