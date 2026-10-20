# ============================================================================
# CELL W7 — ZIP THE RESULTS (send p15_results.zip to Claude)
# ============================================================================
zp = os.path.join(BASE, "p15_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in glob.glob(os.path.join(RESULTS, "W*.json")) + [os.path.join(RESULTS, "p15_manifest_sha256.csv")]:
        if os.path.exists(f):
            z.write(f, "results/" + os.path.basename(f))
    for f in [p15_path, os.path.join(PREREG, "test_set_unlocks_p15.json")]:
        if os.path.exists(f):
            z.write(f, "prereg/" + os.path.basename(f))
print("wrote", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)
