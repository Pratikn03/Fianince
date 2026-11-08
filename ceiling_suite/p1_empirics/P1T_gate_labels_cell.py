# P1T holdout: print ONLY the row labels (first column) of the price-index table for 2019-04-26 and 2019-04-29.
# No index levels, prices, volumes or flows are printed. Computes no statistic.
import json, gzip, os
ROOT = "/content/drive/MyDrive/P1T_raw"
for d in ("20190426", "20190429"):
    j = json.loads(gzip.open(os.path.join(ROOT, "MI", d + ".json.gz")).read())
    t = j["tables"][0]
    print(d, "|", t.get("title"), "| fields:", t.get("fields"))
    for k, row in enumerate(t.get("data") or []):
        lab = str(row[0])
        print(f"  {k:2d} {lab!r}  codepoints={[hex(ord(ch)) for ch in lab] if '加權' in lab else ''}")
