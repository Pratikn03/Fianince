"""Compare two results folders key by key (ignoring runtime and metadata). Exit 1 on any difference."""
import json, math, os, sys
A, B = sys.argv[1], sys.argv[2]
SKIP = {"runtime_seconds", "meta", "timestamp_utc", "interval_evaluations"}


def diff(a, b, p=""):
    out = []
    if isinstance(a, dict):
        for k in a:
            if k in SKIP:
                continue
            if not isinstance(b, dict) or k not in b:
                out.append(p + "/" + k + " missing"); continue
            out += diff(a[k], b[k], p + "/" + k)
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            return [p + " length"]
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{p}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        if not (a == b or (a is not None and b is not None and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12))):
            out.append(f"{p}: {a} vs {b}")
    elif a != b:
        out.append(f"{p}: {a} vs {b}")
    return out


bad = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".json"):
        continue
    d = diff(json.load(open(os.path.join(A, f))), json.load(open(os.path.join(B, f))))
    print(("IDENTICAL " if not d else "DIFFERENT ") + f + ("" if not d else "  " + "; ".join(d[:3])))
    bad += bool(d)
sys.exit(1 if bad else 0)
