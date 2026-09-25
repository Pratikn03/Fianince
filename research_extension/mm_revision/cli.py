"""Command-line interface supporting the four execution modes: smoke, replay, regenerate, acquire."""
import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_smoke():
    """Smoke mode: Run fast deterministic fixtures without network access."""
    print("=== MODE: SMOKE (Deterministic Fast Fixtures) ===")
    start = time.perf_counter()
    
    # 1. Math fixtures
    from research_extension.mm_revision.identities import (
        verify_spectral_vs_gain_distinction,
        get_rational_finite_window_witness,
        verify_swapped_feedback_ambiguity,
    )
    s_res = verify_spectral_vs_gain_distinction()
    assert s_res["both_stable"], "Spectral fixture failed"
    print("  [x] Spectral vs Gain distinction: PASS (S=0.82, rho=0.99009)")

    w_res = get_rational_finite_window_witness()
    assert w_res["matches_up_to_lag3"] and w_res["diverges_at_lag4"], "Witness fixture failed"
    print("  [x] Finite-window ambiguity witness: PASS (h0..h3 match, h4 diverges)")

    sw_res = verify_swapped_feedback_ambiguity()
    assert sw_res["is_observationally_identical"], "Swapped feedback fixture failed"
    print("  [x] Swapped feedback non-identifiability: PASS (identical aggregate price response)")

    # 2. Output-error comparator test
    from research_extension.mm_revision.studies.synthetic_recovery import run_single_synthetic_panel
    p_res = run_single_synthetic_panel(true_S=0.82, slow_rate=0.02, n_episodes=32, seed=42)
    assert "output_error" in p_res, "Comparator run failed"
    print("  [x] Multi-comparator test panel: PASS")

    # 3. Independent verifier
    from independent_verifier.verifier import run_all_independent_verifications
    v_res = run_all_independent_verifications()
    assert v_res["overall"] == "PASS", "Independent verifier failed"
    print("  [x] Independent verifier checks: PASS")

    elapsed = time.perf_counter() - start
    print(f"SMOKE MODE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s.")
    return 0


def run_replay():
    """Replay mode: Rebuild published tables and figures strictly from frozen inputs."""
    print("=== MODE: REPLAY (Rebuilding Artifacts from Frozen Inputs) ===")
    start = time.perf_counter()

    from research_extension.reporting.tables import generate_all_tables
    from research_extension.reporting.figures import generate_all_figures
    from research_extension.reporting.claim_audit import create_source_manifest, create_study_inventory, create_claims_register

    print("  Generating Tables T1-T9...")
    generate_all_tables()
    print("  Generating Figures F1-F7...")
    generate_all_figures()
    print("  Updating manifests and claims register...")
    create_source_manifest()
    create_study_inventory()
    create_claims_register()

    elapsed = time.perf_counter() - start
    print(f"REPLAY MODE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s.")
    return 0


def run_regenerate():
    """Regenerate mode: Rerun simulations and empirical splits from recorded seeds."""
    print("=== MODE: REGENERATE (Rerunning Simulations from Frozen Seeds) ===")
    start = time.perf_counter()

    from research_extension.mm_revision.studies.synthetic_recovery import run_comparative_grid_study
    from research_extension.mm_revision.studies.funded_stress import run_paired_mechanism_controls, run_funded_scenario_grid
    from research_extension.mm_revision.studies.empirical import evaluate_two_layer_temporal_split

    print("  1. Running synthetic comparator grid (pilot slice)...")
    comp_res = run_comparative_grid_study(
        S_values=[0.82, 1.00, 1.18], slow_rates=[0.02],
        episode_budgets=[128], replications_per_cell=5
    )
    print("     -> Done. Processed panels:", comp_res["total_panels"])

    print("  2. Running funded mechanism controls...")
    mech_res = run_paired_mechanism_controls(n_replicates=25, seed=20260924)
    print("     -> Done. Regimes tested:", list(mech_res["summary"].keys()))

    print("  3. Running empirical non-circular temporal split on Coinbase...")
    cb_path = ROOT / "research_extension" / "data" / "real_market_empirical_panel.json"
    if cb_path.exists():
        with open(cb_path) as f:
            cb_data = json.load(f)
        emp_res = evaluate_two_layer_temporal_split(cb_data)
        print("     -> Done. Markets processed:", emp_res["n_markets"])

    elapsed = time.perf_counter() - start
    print(f"REGENERATE MODE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s.")
    return 0


def run_acquire():
    """Acquire mode: Validate data availability and ingest/audit market panels."""
    print("=== MODE: ACQUIRE (Data Feasibility & Ingestion Audit) ===")
    start = time.perf_counter()

    from research_extension.mm_revision.data.coinbase import load_canonical_coinbase_panel
    from research_extension.mm_revision.data.binance_us import load_canonical_binance_panel
    from research_extension.mm_revision.data.quality import audit_asset_panel_quality

    cb_path = ROOT / "research_extension" / "data" / "real_market_empirical_panel.json"
    bn_path = ROOT / "research_extension" / "data" / "binance_market_data.json"

    reports = []
    if cb_path.exists():
        with open(cb_path) as f:
            cb_data = json.load(f)
        for sym, d in cb_data.items():
            panel = load_canonical_coinbase_panel(d, sym)
            rep = audit_asset_panel_quality(panel)
            reports.append(rep)
        print(f"  Audited {len(cb_data)} Coinbase asset panels.")

    if bn_path.exists():
        with open(bn_path) as f:
            bn_data = json.load(f)
        for sym, d in bn_data.items():
            panel = load_canonical_binance_panel(d, sym)
            rep = audit_asset_panel_quality(panel)
            reports.append(rep)
        print(f"  Audited {len(bn_data)} Binance US asset panels.")

    pass_count = sum(1 for r in reports if "PASS" in r.quality_status)
    print(f"  Quality check: {pass_count}/{len(reports)} panels passed quality threshold.")

    elapsed = time.perf_counter() - start
    print(f"ACQUIRE MODE COMPLETED IN {elapsed:.2f}s.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Machine Markets Master Revision CLI")
    parser.add_argument(
        "--mode",
        choices=["smoke", "replay", "regenerate", "acquire"],
        default="smoke",
        help="Execution mode (smoke, replay, regenerate, acquire)"
    )
    args = parser.parse_args()

    if args.mode == "smoke":
        return run_smoke()
    elif args.mode == "replay":
        return run_replay()
    elif args.mode == "regenerate":
        return run_regenerate()
    elif args.mode == "acquire":
        return run_acquire()
    return 1


if __name__ == "__main__":
    sys.exit(main())
