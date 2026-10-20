# ============================================================================
# CELL V3A — AUTOMATIC DOWNLOAD (replaces manual downloading; safe to rerun, finished days are skipped)
# Fetches every coin-day of the pre-registered design straight from Bybit's file server, converts it, deletes the zip.
# Takes about 1-2 hours. If Colab disconnects: run V0, V1, V2, then this cell again; it continues where it stopped.
# ============================================================================
assert os.path.exists(p10_path) and hashlib.sha256(open(p10_path).read().encode()).hexdigest() == P10_HASH, "run V2 first"
OBURL = "https://quote-saver.bycsi.com/orderbook/linear/{s}/{d}_{s}_ob{n}.data.zip"
AUTO = "/content/bybit_ob_auto" if IN_COLAB else os.path.abspath("bybit_ob_auto")
os.makedirs(AUTO, exist_ok=True)
OB_LOG = []
def fetch_ob(coin, date):
    if have_book(coin, date):
        return "already converted"
    s = f"{coin}USDT"
    for n in ((500, 200) if date < "2025" else (200, 500)):
        url = OBURL.format(s=s, d=date, n=n)
        try:
            code, raw = _http(url, timeout=600)
        except Exception as e:
            return f"network error: {e!s:.120}"
        if code == 200 and raw:
            path = os.path.join(AUTO, f"{date}_{s}_ob{n}.data.zip")
            open(path, "wb").write(raw)
            OB_LOG.append({"coin": coin, "date": date, "url": url, "zip_sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
            try:
                got = convert_zip(path)
            finally:
                os.remove(path)
            return f"ok ob{n}" if got else "zip had no order-book file"
    return "not on Bybit"
# 1) probe with the link you copied from Chrome
code, _ = _http(OBURL.format(s="ALICEUSDT", d="2024-03-12", n=500), timeout=300)
print("Bybit order-book server reachable from Colab:", code == 200, f"(HTTP {code})")
assert code == 200, "Colab cannot reach quote-saver.bycsi.com; use manual downloads + V3, and tell Claude."
# 2) everything else
jobs = [(c, d) for c in COINS for d in TRAIN_D + TEST_D]
res = {}
t_start = time.time()
with ThreadPoolExecutor(4) as ex:
    futs = {ex.submit(fetch_ob, c, d): (c, d) for c, d in jobs}
    for i, f in enumerate(as_completed(futs), 1):
        res[futs[f]] = f.result()
        if i % 20 == 0:
            el = (time.time() - t_start) / 60
            print(f"   {i}/{len(jobs)} coin-days, {el:.0f} min elapsed, about {el / i * (len(jobs) - i):.0f} min left")
summ = pd.Series(res).value_counts()
print("\n", summ.to_string())
for bname, coins in BATCHES.items():
    for c in coins:
        miss = [d for d in TRAIN_D + TEST_D if not have_book(c, d)]
        if miss:
            print(f"   {c}: {len(miss)} days not available -> {sorted({d[:7] for d in miss})}")
pd.DataFrame(OB_LOG).to_csv(os.path.join(RESULTS, "p10_orderbook_manifest_sha256.csv"),
                            mode="a", header=not os.path.exists(os.path.join(RESULTS, "p10_orderbook_manifest_sha256.csv")), index=False)
record("V3A_orderbook_download", None, "audit", {"status_counts": summ.to_dict(),
       "missing": {c: [d for d in TRAIN_D + TEST_D if not have_book(c, d)] for c in COINS}})
print("\nDone. Next: run V4 (you can skip V3).")
