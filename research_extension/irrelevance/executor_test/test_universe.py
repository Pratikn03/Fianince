"""Offline test of the universe rule: fake S3 listing (two pages), monthly 1d klines, missing files."""
import importlib.util, io, zipfile, datetime as dt
spec = importlib.util.spec_from_file_location("ex", "/home/claude/fianince/ceiling_suite/p1_empirics/p1f_executor.py")
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
syms = [f"A{i:02d}USDT" for i in range(40)] + ["XBUSD", "B99USDT"]
first, last = ex.WINDOW_START.isoformat(), (ex.WINDOW_START + dt.timedelta(ex.NDAYS - 1)).isoformat()
F = {}
def z(txt):
    b = io.BytesIO(); zz = zipfile.ZipFile(b, "w"); zz.writestr("x.csv", txt); zz.close(); return b.getvalue()
page1 = "".join(f"<Prefix>data/futures/um/daily/metrics/{s}/</Prefix>" for s in syms[:20]) + "<NextMarker>m1</NextMarker>"
page2 = "".join(f"<Prefix>data/futures/um/daily/metrics/{s}/</Prefix>" for s in syms[20:])
F[f"{ex.S3_LIST}?delimiter=/&prefix=data/futures/um/daily/metrics/"] = page1.encode()
F[f"{ex.S3_LIST}?delimiter=/&prefix=data/futures/um/daily/metrics/&marker=m1"] = page2.encode()
for i, s in enumerate(syms):
    if s == "B99USDT": continue                       # no files in window: must be excluded
    for d in (first, last):
        if not (s == "A05USDT" and d == last):        # missing last-day metrics: must be excluded
            F[f"{ex.BASE}/data/futures/um/daily/metrics/{s}/{s}-metrics-{d}.zip"] = b"x"
        F[f"{ex.BASE}/data/futures/um/daily/klines/{s}/5m/{s}-5m-{d}.zip"] = b"x"
    rows = "\n".join(f"{1643673600000+86400000*j},1,1,1,1,1,0,{(i+1)*1000.0},1,0,0,0" for j in range(28))
    F[f"{ex.BASE}/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{ex.VOLUME_MONTH}.zip"] = z(rows)
ex.FETCH = lambda url: F.get(url)
chosen, vols = ex.universe()
assert "XBUSD" not in vols and "B99USDT" not in vols and "A05USDT" not in vols, vols.keys()
assert chosen[0] == "A39USDT" and len(chosen) == 30 and "A05USDT" not in chosen
print("universe test passed:", chosen[:5], "...", len(chosen))
