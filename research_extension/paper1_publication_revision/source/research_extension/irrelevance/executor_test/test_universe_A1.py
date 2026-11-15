"""Offline tests of amendment A1: universe rule with the field check, listing months and volume month; date guard."""
import importlib.util, io, zipfile, datetime as dt
spec = importlib.util.spec_from_file_location("ex", "/home/claude/fianince/ceiling_suite/p1_empirics/p1f_executor_A1.py")
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)

# date guard: with the real fetcher and today's date before EARLIEST_RUN, run_all must stop before any download
try:
    ex.run_all("/tmp/claude-0/p1fA1_guard")
    raise AssertionError("guard did not stop the run")
except SystemExit as e:
    print("date guard ok:", e)

syms = [f"A{i:02d}USDT" for i in range(40)] + ["NOTOPUSDT", "NEWUSDT"]
first, last = ex.WINDOW_START.isoformat(), (ex.WINDOW_START + dt.timedelta(ex.NDAYS - 1)).isoformat()
F = {}
def z(txt):
    b = io.BytesIO(); zz = zipfile.ZipFile(b, "w"); zz.writestr("x.csv", txt); zz.close(); return b.getvalue()
hdr = "create_time,symbol,sum_open_interest,sum_open_interest_value,count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
F[f"{ex.S3_LIST}?delimiter=/&prefix=data/futures/um/daily/metrics/"] = "".join(f"<Prefix>data/futures/um/daily/metrics/{s}/</Prefix>" for s in syms).encode()
for i, s in enumerate(syms):
    for d in (first, last):
        F[f"{ex.BASE}/data/futures/um/daily/metrics/{s}/{s}-metrics-{d}.zip"] = b"x"
        F[f"{ex.BASE}/data/futures/um/daily/klines/{s}/5m/{s}-5m-{d}.zip"] = b"x"
    for mo in ex.LISTING_MONTHS:
        if s != "NEWUSDT":                                  # recently listed: must be excluded
            F[f"{ex.BASE}/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{mo}.zip"] = b"x"
    top = '"",""' if s == "NOTOPUSDT" else "1.1,1.2"        # empty top-trader fields: must be excluded
    rows = "".join(f"2026-11-14 00:{j:02d}:00,{s},1,1,{top},1.3,\"\"\n" for j in range(0, 60, 5))
    F[f"{ex.BASE}/data/futures/um/daily/metrics/{s}/{s}-metrics-{ex.STRUCTURE_DAY.isoformat()}.zip"] = z(hdr + rows)
    vol = "\n".join(f"{1790000000000+86400000*j},1,1,1,1,1,0,{(i+1)*1000.0 + (1e9 if s in ('NOTOPUSDT','NEWUSDT') else 0)},1,0,0,0" for j in range(31))
    F[f"{ex.BASE}/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{ex.VOLUME_MONTH}.zip"] = z(vol)
ex.FETCH = lambda url: F.get(url)
chosen, vols = ex.universe()
assert "NOTOPUSDT" not in chosen and "NEWUSDT" not in chosen and len(chosen) == 30 and chosen[0] == "A39USDT", chosen
print("universe A1 test passed:", chosen[:3], "...", len(chosen))
