# ============================================================================
# CELL V3 — CONVERT UPLOADED ZIPS (run after EVERY batch you upload; safe to rerun)
# Put Bybit .zip files in /content/bybit_ob (Colab Files panel) or in Drive MyDrive/ceiling_suite/bybit_ob.
# Each zip becomes a small summary saved in Drive, then the zip is deleted to free space.
# ============================================================================
assert os.path.exists(p10_path) and hashlib.sha256(open(p10_path).read().encode()).hexdigest() == P10_HASH, "run V2 first"
zips = sorted(set(sum([glob.glob(os.path.join(u, "**", "*.zip"), recursive=True) +
                      glob.glob(os.path.join(u, "**", "*.data"), recursive=True) for u in UPLOAD_DIRS], [])))
print(f"{len(zips)} files found")
written, bad = [], []
for i, zp in enumerate(zips, 1):
    try:
        got = convert_zip(zp); written += got
        if got:
            os.remove(zp)
        else:
            bad.append((os.path.basename(zp), "no ob .data file inside"))
    except Exception as e:
        bad.append((os.path.basename(zp), repr(e)[:200]))
    if i % 10 == 0:
        print(f"   {i}/{len(zips)}")
print(f"converted {len(written)} coin-days; problems: {len(bad)}")
for b in bad:
    print("   PROBLEM:", b)
# What is still missing, batch by batch (this is your download checklist)
WANT = TRAIN_D + TEST_D
for bname, coins in BATCHES.items():
    miss = {c: [d for d in WANT if not have_book(c, d)] for c in coins}
    n = sum(len(v) for v in miss.values())
    print(f"\nBatch {bname} {coins}: {len(coins) * len(WANT) - n}/{len(coins) * len(WANT)} coin-days present")
    for c, v in miss.items():
        if v:
            wins = sorted({d[:7] for d in v})
            print(f"   {c}: missing {len(v)} days, in windows {wins}")
off = [(c, d) for c in COINS for d in WANT if have_book(c, d) and
       json.load(open(os.path.join(OBMIN, c, f"{d}.json"))).get("u_gaps", 0) > 5]
if off:
    print("\nDays with broken update sequences (will be dropped):", off)
if IN_COLAB:
    print("\nIf you used the Drive folder: empty the Google Drive trash now to get the space back.")
