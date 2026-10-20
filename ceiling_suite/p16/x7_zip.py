# ============================================================================
# CELL X7 — ZIP THE RESULTS (send p16_results.zip to Claude)
# ============================================================================
zp = os.path.join(BASE, "p16_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in [os.path.join(RESULTS, f + ".json") for f in ("X2_new_universe", "X4_build", "X5_blocks", "X6_untouched_symbols_test")] + [os.path.join(RESULTS, "p16_manifest_sha256.csv")]:
        if os.path.exists(f):
            z.write(f, "results/" + os.path.basename(f))
    for f in [p16_path, os.path.join(PREREG, "test_set_unlocks_p16.json")]:
        if os.path.exists(f):
            z.write(f, "prereg/" + os.path.basename(f))
print("wrote", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)
