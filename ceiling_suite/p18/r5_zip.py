# ============================================================================
# CELL R5 — ZIP THE RESULTS (send p18_results.zip to Claude)
# ============================================================================
zp = os.path.join(BASE, "p18_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in [os.path.join(RESULTS, f + ".json") for f in ("R3_placebo_binance", "R4_guard_baselines")]:
        if os.path.exists(f):
            z.write(f, "results/" + os.path.basename(f))
    if os.path.exists(p18_path):
        z.write(p18_path, "prereg/" + os.path.basename(p18_path))
print("wrote", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)
