"""Reproduce the bounded empirical audit from frozen local inputs, without network.

Run from repository root:
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3.11 -m research_extension.evidence_repair.empirical_report --output-dir \
  research_extension/outputs/evidence_repair_20260926/empirical/fresh-run
Only the empirical evidence-repair output directory is written.
"""
import argparse
import hashlib
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import scipy
from scipy import stats

from research_extension.binance_multi_epoch_study import run_binance_study
from research_extension.mm_revision.studies.empirical import (
    evaluate_explanatory_records, evaluate_two_layer_temporal_split,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research_extension/outputs/evidence_repair_20260926/empirical"
INPUT_HASHES = {
    "research_extension/data/real_market_empirical_panel.json": "3debb9fef83865b8709ace147852b7915e6b95931393e561750f86aaa524af20",
    "research_extension/data/binance_market_data.json": "cce41e2e53d894c88c2a4f6137d7ce072d56bb801587e281d42c76f23600b5b0",
    "research_extension/outputs/empirical_results.json": "30a9847fa6747d8dd517ee27cecbd172211718e027524fe485fdb3d86ec3a731",
    "research_extension/outputs/binance_multi_epoch_results.json": "4c6f3196ebd9844f7b3648d6ae89f0a2472618d5466b8154f17e32a5ee3f35f9",
}
SOURCE_PATHS = [
    "research_extension/binance_multi_epoch_study.py",
    "research_extension/mm_revision/studies/empirical.py",
    "research_extension/mm_revision/inference/observational.py",
    "research_extension/mm_revision/inference/diagnostics.py",
    "research_extension/real_data_study.py",
    "research_extension/evidence_repair/empirical_report.py",
    "tests/test_empirical_evidence_repairs.py",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def verify_frozen_inputs():
    for path, expected in INPUT_HASHES.items():
        if sha256(ROOT / path) != expected:
            raise RuntimeError(f"Frozen input changed: {path}; audit aborted, do not substitute a new sample.")


def independent_cache_rows(panel):
    """Reconstruct historical F from prices, independently of estimator helpers.

    Preserve the legacy .95 AR clamp, covariance denominator (m-2), population
    variance denominator (m-1), autocovariance denominator (m-lag), and lags 1,2,5.
    The current proxy's .99 clamp is checked against these actual rows below.
    """
    rows = []
    for symbol, data in panel.items():
        returns = np.diff(np.log(np.asarray(data["closes"], dtype=float)))
        cut = int(.7 * len(returns))
        a, b = returns[:cut], returns[cut:]

        def rho(x, lag):
            centered = x - x.mean()
            return float(np.dot(centered[:-lag], centered[lag:]) / (len(x) - lag) / np.mean(centered**2))

        left, right = a[:-1] - a[:-1].mean(), a[1:] - a[1:].mean()
        ar = float(np.dot(left, right) / (len(left) - 1) / np.mean(left**2))
        ar = float(np.clip(ar, -.95, .95))
        rows.append({
            "symbol": symbol, "F": abs(ar) + sum(abs(rho(a, lag)) for lag in (1, 2, 5)),
            "rho1_A": rho(a, 1), "rho1_B": rho(b, 1),
            "spread_bps": data["rel_spread_bps"], "vol_bps": float(np.std(a) * 10000),
            "S_model": None, "S_model_status": "unavailable_unaligned_tick_flow",
            "a_ar1_legacy": ar,
            "temporal_split": {"n_closes": len(data["closes"]), "n_returns": len(returns),
                               "period_A_return_indices": [0, cut], "period_B_return_indices": [cut, len(returns)]},
        })
    return rows


def regression_crosscheck(rows, results):
    """Check bivariate via scipy.linregress; full OLS via independent QR solve."""
    x = np.array([r["F"] for r in rows])
    y = np.array([r["rho1_B"] for r in rows])
    direct = stats.linregress(x, y)
    x_full = np.array([[1, r["F"], r["spread_bps"], r["vol_bps"]] for r in rows])
    q, r = np.linalg.qr(x_full)
    beta = np.linalg.solve(r, q.T @ y)
    residuals = y - x_full @ beta
    df = len(rows) - x_full.shape[1]
    inv_r = np.linalg.solve(r, np.eye(r.shape[0]))
    se = np.sqrt(np.diag(inv_r @ inv_r.T) * (residuals @ residuals / df))
    t = beta / se
    p = 2 * stats.t.sf(abs(t), df)
    biv = results["specifications"]["bivariate_F"]
    full = results["specifications"]["full_model_F"]
    np.testing.assert_allclose([biv["F_beta"], biv["F_tstat"], biv["F_pvalue"], biv["r2"]],
                               [direct.slope, direct.slope / direct.stderr, direct.pvalue, direct.rvalue**2], rtol=1e-10, atol=1e-12)
    for key, values in (("beta", beta), ("se", se), ("t_stats", t), ("p_values", p)):
        np.testing.assert_allclose(full[key], values, rtol=1e-10, atol=1e-12)
    return {"status": "passed", "bivariate_method": "scipy.stats.linregress",
            "full_model_method": "unscaled_QR_solve", "relative_tolerance": 1e-10, "absolute_tolerance": 1e-12}


def build_coinbase_audit(panel, legacy):
    rows = [{"symbol": r["product_id"], "F": r["s_hat_A"], "rho1_A": r["rho1_A"],
             "rho1_B": r["rho1_B"], "spread_bps": r["rel_spread_bps"], "vol_bps": r["vol_bps_A"],
             "S_model": None, "S_model_status": "not_a_structural_estimate"} for r in legacy["asset_table"]]
    reconstructed = independent_cache_rows(panel)
    serialized = evaluate_explanatory_records(rows)
    cached = evaluate_two_layer_temporal_split(panel)
    for independent, actual in zip(reconstructed, cached["records"]):
        assert independent["symbol"] == actual["symbol"]
        for key in ("F", "rho1_A", "rho1_B", "vol_bps", "spread_bps"):
            np.testing.assert_allclose(independent[key], actual[key], rtol=1e-12, atol=1e-14)
    checks = {"serialized": regression_crosscheck(rows, serialized), "cached": regression_crosscheck(reconstructed, cached)}
    differences = [
        {"symbol": old["symbol"], "cache_minus_serialized": {key: new[key] - old[key]
         for key in ("F", "rho1_A", "rho1_B", "spread_bps", "vol_bps")}}
        for old, new in zip(rows, reconstructed)
    ]
    full = serialized["specifications"]["full_model_F"]
    np.testing.assert_allclose(full["r2"], legacy["r_squared"], atol=1e-12)
    np.testing.assert_allclose(full["beta"], [c["estimate"] for c in legacy["coefficients"].values()], atol=1e-12)
    return {
        "historical_claims_not_reproduced": {
            "source": "User-specified legacy claim; also observed in paper source (left untouched)",
            "bivariate": {"slope": .6866, "se": .2778, "t": 2.47, "p": .039, "r2": .4330, "df": 8},
            "older_generated_table_p": .048,
            "interpretation": "Neither saved rows nor frozen cache reproduce this joint specification; no preferred sample selected.",
        },
        "legacy_saved_result_verbatim": legacy,
        "serialized_rows": serialized, "frozen_cache": cached,
        "independent_cache_reconstruction": reconstructed, "independent_checks": checks,
        "cache_minus_serialized_by_asset": differences,
        "lineage": "Different saved rows and cache values; original acquisition timestamps and historical row price windows unavailable. Cause cannot be recovered from these artifacts.",
        "proxy_definition": "F = abs(clipped_AR1) + abs(rho1) + abs(rho2) + abs(rho5); .95 legacy and .99 current AR clamps give identical values for this cache.",
        "selection_policy": "Report both fixed samples and every declared specification; no favorable-sample selection.",
    }


def write_locked_text(path, text):
    """Exclusive creation; never replace a differing prior artifact."""
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"Locked evidence differs: {path}. Choose a fresh --output-dir.") from None


def write_json(name, value, output_dir=None):
    write_locked_text((output_dir or OUTPUT) / name, json.dumps(value, indent=2, allow_nan=False) + "\n")


def render_report(audit, binance):
    lines = ["# Bounded empirical evidence repair — 2026-09-26", "",
             "All inputs are frozen local artifacts. No new data, paper edits, or historical result replacements.", "",
             "## Coinbase evidence reconciliation", "",
             "| Evidence and specification | n / df | F coefficient | SE | t | p (two sided) | R² |",
             "|---|---:|---:|---:|---:|---:|---:|",
             "| Legacy paper bivariate (unreproduced) | 10 / 8 | 0.6866 | 0.2778 | 2.47 | 0.039 | 0.4330 |"]
    for label, key in (("Serialized rows", "serialized_rows"), ("Frozen cache", "frozen_cache")):
        for spec, description in (("bivariate_F", "bivariate"), ("full_model_F", "with spread + volatility")):
            r = audit[key]["specifications"][spec]
            lines.append(f"| {label}, {description} | {r['n_obs']} / {r['df']} | {r['beta'][1]:.12f} | {r['se'][1]:.12f} | {r['t_stats'][1]:.12f} | {r['p_values'][1]:.12f} | {r['r2']:.12f} |")
    lines += ["", "The saved full-model coefficients and R² reproduce from the serialized rows. The claimed historical bivariate combination does not. The cached full-model t=2.470662 and p=0.048414 belong to its controlled specification (6 df), not its bivariate specification (8 df). This numerical resemblance does not establish the origin of the legacy claim.", "",
              "Each cached Coinbase asset has 350 closes and 349 returns: A=[0,244), B=[244,349). The ten symbols and exact row order are serialized in coinbase_audit.json. Historical serialized rows lack recoverable source-window indices. All ten cache rows differ from their saved counterparts. No sample is selected on significance.", "",
              "Period B does not enter F, but it does enter the cross-sectional slope estimates. The fitted residual comparisons are descriptive in-sample reductions; adding regressors mechanically reduces training SSE. These results do not establish forecast performance. Conventional standard errors assume homoskedastic, independent cross-asset residuals and are exploratory with n=10.", "",
              "The Coinbase cache has 1,000 tick flows versus 350 candle closes per asset, with no alignment timestamps. All ten S_model estimates are explicitly unavailable. Snapshot spread timing is also unverified. No F-for-S fallback or invented flow is used.", "",
              "## Corrected chronological Binance run", "",
              "All ten fixed markets and all five seeds (42, 101, 777, 1234, 2026), ten fixed epochs each. Each 500-price tick path has 499 transitions: training=[0,349), validation=[349,499). Every epoch uses the entire ordered training prefix. Exact two-state recursion retains all memory and carries state into validation. The zero initial state, original positive parameter bounds, absolute price-change target, and Q² penalty (0.01) are maintained assumptions; no validation-based tuning or seed selection.", "",
              "| Asset | Status | Mean S | Seed SD | Mean conditional validation R² | Failed seeds |",
              "|---|---|---:|---:|---:|---:|"]
    for asset in binance["asset_results"]:
        fmt = lambda v: "unavailable" if v is None else f"{v:.12g}"
        failures = sum(r["status"] != "ok" for r in asset["seed_runs"])
        lines.append(f"| {asset['symbol']} | {asset['status']} | {fmt(asset['mean_s_hat'])} | {fmt(asset['std_s_hat'])} | {fmt(asset['mean_oos_r2'])} | {failures} |")
    reg = binance["cross_sectional_regression"]
    if reg["status"] == "ok":
        lines += ["", f"Corrected cross-asset S coefficient={reg['beta'][1]:.12f}, SE={reg['se'][1]:.12f}, t={reg['t_stats'][1]:.12f}, p={reg['p_values'][1]:.12f}, R²={reg['r2']:.12f}, df={reg['df']}. This regression is in-sample explanatory."]
    else:
        lines += ["", f"Corrected cross-asset regression unavailable: {reg['reason']}"]
    lines += ["", "Conditional validation R² uses realized validation flow and the validation-mean denominator; negative values are not clipped. Seed SD measures initialization sensitivity, not sampling uncertainty. Optimizer success is not identification, causal validity, or a market-stability certificate. Boundary hits, spectral radii, losses, parameters, predictions and optimizer diagnostics are saved for every accepted seed; failures stay in the requested panel and suppress aggregate claims.", "",
              "The cache preserves array order but omits tick/candle timestamps and IDs. Chronology is conditional on the stored order; alignment of tick Period A to candle Period B cannot be verified. The repaired fit therefore cannot support a cross-window forecast claim. The legacy Binance result is retained in legacy_binance.json and superseded only as an implementation result, not overwritten.", "",
              "## Safe manuscript wording", "",
              '> “Reanalysis distinguishes two frozen empirical samples. The ten serialized Coinbase rows yield an exploratory bivariate association between the Period-A persistence proxy and Period-B autocorrelation (t=1.901588, p=0.093738, R²=0.311297); adding spread and volatility gives t=1.232835, p=0.263747, R²=0.518494. Independently reconstructing the frozen price cache gives bivariate t=2.426069, p=0.041456, R²=0.423872 and controlled-model t=2.470662, p=0.048414, R²=0.549208. These samples differ, and neither reproduces the historical bivariate claim t=2.47, p=0.039, R²=0.4330. Regression slopes are estimated using the same assets’ Period-B outcomes, so results are in-sample explanatory associations rather than out-of-sample forecast evidence. The corrected Binance fits preserve chronological state recursion and report all requested seeds; timestamp limitations and initialization sensitivity preclude a claim of identified market feedback or certified stability.”', "",
              "## Reproduction and provenance", "",
              "Run from the repository root with Python 3.11:", "",
              "```sh", "PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.11 -m research_extension.evidence_repair.empirical_report --output-dir research_extension/outputs/evidence_repair_20260926/empirical/fresh-run", "```", "",
              "The generator refuses an existing output directory and exclusively creates each artifact, blocking differing overwrites. Choose a fresh --output-dir under the authorized empirical directory for each rerun. It blocks network connections and verifies fixed input and source hashes before sealing. samples.json preserves exact input arrays/rows and canonical per-asset hashes. manifest.json binds source files, inputs, generated artifacts and available test receipts. OLS is checked independently with scipy.linregress and QR; cache features are independently reconstructed from prices. tests_red.txt records the pre-fix failures; subsequent test receipts report verification separately from empirical validity.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT,
                        help="A NEW directory under the empirical evidence-repair scope; never reused.")
    output_dir = parser.parse_args(argv).output_dir.resolve()
    if not output_dir.is_relative_to(OUTPUT.resolve()):
        raise ValueError(f"Output directory is outside authorized empirical scope: {OUTPUT}")
    if output_dir.exists():
        raise FileExistsError(f"Evidence directory already exists: {output_dir}. Choose a fresh --output-dir.")
    verify_frozen_inputs()
    source_hashes = {p: sha256(ROOT / p) for p in SOURCE_PATHS}
    output_dir.mkdir(parents=True, exist_ok=False)
    with patch.object(socket.socket, "connect", side_effect=RuntimeError("Network disabled for frozen empirical audit")), \
         patch.object(socket, "create_connection", side_effect=RuntimeError("Network disabled for frozen empirical audit")):
        panel = json.loads((ROOT / "research_extension/data/real_market_empirical_panel.json").read_text())
        legacy = json.loads((ROOT / "research_extension/outputs/empirical_results.json").read_text())
        raw_binance = json.loads((ROOT / "research_extension/data/binance_market_data.json").read_text())
        audit = build_coinbase_audit(panel, legacy)
        write_json("coinbase_audit.json", audit, output_dir)
        write_json("samples.json", {
            "hash_convention": "SHA256 of sorted-key compact JSON, UTF-8, allow_nan=False",
            "coinbase_cache": panel, "coinbase_serialized_rows": legacy["asset_table"], "binance_cache": raw_binance,
            "canonical_asset_hashes": {"coinbase_cache": {k: canonical_hash(v) for k, v in panel.items()},
                                       "binance_cache": {k: canonical_hash(v) for k, v in raw_binance.items()}},
            "serialized_rows_sha256": canonical_hash(legacy["asset_table"]),
        }, output_dir)
        write_json("legacy_binance.json", json.loads((ROOT / "research_extension/outputs/binance_multi_epoch_results.json").read_text()), output_dir)
        print("Saved Coinbase row-versus-cache audit, exact samples, and legacy values.", flush=True)
        binance = run_binance_study()
        write_json("binance_chronological_results.json", binance, output_dir)
        write_locked_text(output_dir / "report.md", render_report(audit, binance))
    verify_frozen_inputs()
    if source_hashes != {p: sha256(ROOT / p) for p in SOURCE_PATHS}:
        raise RuntimeError("Source changed during generation; this partial output is not sealed.")
    write_json("manifest.json", {
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "base_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "workspace": str(ROOT), "python": sys.version, "executable": sys.executable,
        "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__,
        "network": "blocked", "input_sha256": INPUT_HASHES, "source_sha256": source_hashes,
        "output_directory": str(output_dir), "overwrite_policy": "new directory only; exclusive artifact creation",
        "output_sha256": {p.name: sha256(p) for p in sorted(output_dir.iterdir()) if p.is_file() and p.name != "manifest.json"},
        "test_receipt_sha256": {
            str(p.relative_to(ROOT)): sha256(p)
            for p in sorted(set(OUTPUT.glob("tests_*.txt")) | set((OUTPUT / "native_tests").glob("*"))) if p.is_file()
        },
        "source_note": "Shared dirty checkout; hashes bind the actual edited source, not just base HEAD. No commits made.",
    }, output_dir)
    reg = binance["cross_sectional_regression"]
    print(json.dumps({"binance_status": binance["status"], "regression": reg, "report": str(output_dir / "report.md")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
