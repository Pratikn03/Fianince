# ============================================================================
# CELL C7 — ZIP THE RESULTS (send p17_results.zip to Claude)
# ============================================================================
zp = os.path.join(BASE, "p17_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in [os.path.join(RESULTS, f + ".json") for f in ("C2_universe", "C4_build", "C5_blocks", "C6_new_venue_test")] + [os.path.join(RESULTS, "p17_manifest.csv")]:
        if os.path.exists(f):
            z.write(f, "results/" + os.path.basename(f))
    for f in [p17_path, os.path.join(PREREG, "test_set_unlocks_p17.json")]:
        if os.path.exists(f):
            z.write(f, "prereg/" + os.path.basename(f))
print("wrote", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)
