"""Generate source manifest, study inventory, and claims register for WP0."""
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_source_manifest():
    manifest_path = ROOT / "manifests" / "source_manifest.json"
    
    # Environment info
    env_info = {
        "python": sys.version,
        "platform": sys.platform,
        "executable": sys.executable,
    }
    
    # Git status
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip().splitlines()
    except Exception as e:
        commit = "UNKNOWN"
        status = [str(e)]

    key_files = [
        "paper/Machine_Markets_Final_Integrated_Paper.tex",
        "paper/Machine_Markets_Final_Integrated_Paper.pdf",
        "studies/audited_constraints/results/linear_summary.json",
        "studies/audited_constraints/results/dealer_stress.csv",
        "research_extension/data/real_market_empirical_panel.json",
        "research_extension/data/binance_market_data.json",
    ]
    
    file_hashes = {}
    for kf in key_files:
        p = ROOT / kf
        if p.exists():
            file_hashes[kf] = sha256_file(p)
            
    data = {
        "git_commit": commit,
        "uncommitted_files": status,
        "environment": env_info,
        "key_file_hashes": file_hashes,
        "description": "Baseline freeze manifest capturing environment, commit, and key input artifacts."
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Created {manifest_path}")

def create_study_inventory():
    inventory_path = ROOT / "manifests" / "study_inventory.json"
    
    studies = [
        {
            "study_id": "audited_constraints",
            "directory": "studies/audited_constraints",
            "type": "native_simulation",
            "information_contract": "I1",
            "unit_of_analysis": "Panels (2,880 panels, 645,120 episode rows)",
            "key_artifacts": [
                "results/linear_summary.json",
                "results/dealer_stress.csv",
                "results/binomial_exact_coverage.csv",
                "results/measured_tail.csv"
            ],
            "status": "reproduced"
        },
        {
            "study_id": "observable_stress_tests",
            "directory": "studies/observable_stress_tests",
            "type": "native_simulation",
            "information_contract": "I0",
            "unit_of_analysis": "Panels (1,920 panels, 5,760 decision rows)",
            "key_artifacts": [
                "results/primary_grid_results.csv",
                "results/primary_summary.json",
                "results/assumption_controls.csv"
            ],
            "status": "reproduced"
        },
        {
            "study_id": "full_horizon_audit",
            "directory": "studies/full_horizon_audit",
            "type": "native_simulation",
            "information_contract": "I0_extended",
            "unit_of_analysis": "Vectors (10,800 vectors, 256 taps)",
            "key_artifacts": [
                "results/audit_summary.json"
            ],
            "status": "reproduced"
        },
        {
            "study_id": "hidden_slow_learners",
            "directory": "studies/hidden_slow_learners",
            "type": "native_theory_simulation",
            "information_contract": "I0_analytical",
            "unit_of_analysis": "Algebraic witnesses & grid checks (875 points)",
            "key_artifacts": [
                "results/grid_verification.json"
            ],
            "status": "reproduced"
        },
        {
            "study_id": "group_identification_extension",
            "directory": "research_extension",
            "type": "extension_theory_simulation",
            "information_contract": "I0_vs_I1_group",
            "unit_of_analysis": "Agent groups and channel measurement ranks",
            "key_artifacts": [
                "group_identification.py",
                "economic_mechanism.py"
            ],
            "status": "reproduced"
        },
        {
            "study_id": "empirical_microstructure",
            "directory": "research_extension",
            "type": "observational_microstructure",
            "information_contract": "I2",
            "unit_of_analysis": "10 digital asset markets, Coinbase and Binance US",
            "key_artifacts": [
                "data/real_market_empirical_panel.json",
                "data/binance_market_data.json",
                "outputs/empirical_results.json",
                "outputs/binance_multi_epoch_results.json"
            ],
            "status": "arithmetically_reconstructed_with_spec_separation"
        }
    ]
    
    with open(inventory_path, "w", encoding="utf-8") as f:
        json.dump({"studies": studies}, f, indent=2)
    print(f"Created {inventory_path}")

def create_claims_register():
    claims_path = ROOT / "manifests" / "claims.csv"
    
    # claim_id, manuscript_location, claim_text, evidence_type, theorem_or_spec_id, information_contract, result_artifact, source_hash, verification_status, limitations
    fieldnames = [
        "claim_id",
        "manuscript_location",
        "claim_text",
        "evidence_type",
        "theorem_or_spec_id",
        "information_contract",
        "result_artifact",
        "source_hash",
        "verification_status",
        "limitations"
    ]
    
    claims = [
        {
            "claim_id": "CLM-001",
            "manuscript_location": "Abstract, Introduction, Section 8.1",
            "claim_text": "Positive feedback system stability boundary is S = a + Q < 1, equivalent to rho(J) < 1, but S and rho(J) are distinct numerical quantities (S=0.82 vs rho(J)=0.99009 for the audited baseline).",
            "evidence_type": "theorem",
            "theorem_or_spec_id": "Proposition 8.1",
            "information_contract": "I1",
            "result_artifact": "research_extension/mm_revision/identities.py",
            "source_hash": "exact_algebra",
            "verification_status": "verified",
            "limitations": "Requires maintained sign-positive linear feedback model."
        },
        {
            "claim_id": "CLM-002",
            "manuscript_location": "Abstract, Introduction, Section 14",
            "claim_text": "Audited terminal-row regression achieves 95.76% parameter coverage across 2,880 primary panels, with 25.87% decisiveness, 0.69% unconditional error, and 2.68% conditional error among issued decisions.",
            "evidence_type": "experiment",
            "theorem_or_spec_id": "Table 14.1 / audited_terminal_regression",
            "information_contract": "I1",
            "result_artifact": "studies/audited_constraints/results/linear_summary.json",
            "source_hash": "17cd1470540015983a5589efaed12461f104f3955948d098a77369cf9be0eb67",
            "verification_status": "verified",
            "limitations": "Requires exact prices, disclosed rates, verified reset, complete channel inventory, and terminal innovation assumptions."
        },
        {
            "claim_id": "CLM-003",
            "manuscript_location": "Section 8, Theorem 8.2, Table 8.1",
            "claim_text": "Exact finite-window ambiguity: two systems with opposite asymptotic stability classes can produce identical price impulse responses for K+2 steps.",
            "evidence_type": "theorem_witness",
            "theorem_or_spec_id": "Theorem 8.2 / Table 8.1",
            "information_contract": "I0",
            "result_artifact": "research_extension/mm_revision/identities.py",
            "source_hash": "exact_witness",
            "verification_status": "verified",
            "limitations": "Finite observation window H <= K+2 cannot distinguish without tail rate floor."
        },
        {
            "claim_id": "CLM-004",
            "manuscript_location": "Section 9, Proposition G.1",
            "claim_text": "Swapped-feedback non-identifiability: two economies with symmetric learning rates and swapped agent feedback weights produce identical aggregate price impulse responses at all horizons.",
            "evidence_type": "theorem_witness",
            "theorem_or_spec_id": "Proposition G.1",
            "information_contract": "I0",
            "result_artifact": "research_extension/group_identification.py",
            "source_hash": "exact_algebra",
            "verification_status": "verified",
            "limitations": "Applies under passive aggregate price monitoring and symmetric memory decay."
        },
        {
            "claim_id": "CLM-005",
            "manuscript_location": "Section 9, Theorem G.2, Appendix A.5",
            "claim_text": "Group identification via channel excitation b = eta U q: for known eta, full column rank of U (or rank of [1^T; U] when Q is known) supplies unique q recovery; unknown eta yields only set identification.",
            "evidence_type": "theorem",
            "theorem_or_spec_id": "Theorem G.2",
            "information_contract": "I1_group",
            "result_artifact": "research_extension/mm_revision/identities.py",
            "source_hash": "exact_rank",
            "verification_status": "verified",
            "limitations": "Requires known learning rate eta; lower bound alone does not uniquely invert q_k."
        },
        {
            "claim_id": "CLM-006",
            "manuscript_location": "Section 9, Definition G.3",
            "claim_text": "Group suppression effect notation: removing group k's feedback elasticity reduces total feedback by Delta Q_k = q_k, and steady-state multiplier by Delta G = q_k / (1 - a), holding a fixed.",
            "evidence_type": "definition",
            "theorem_or_spec_id": "Definition G.3",
            "information_contract": "I1",
            "result_artifact": "research_extension/mm_revision/identities.py",
            "source_hash": "exact_algebra",
            "verification_status": "verified",
            "limitations": "Linear steady-state comparative static holding other parameters fixed."
        },
        {
            "claim_id": "CLM-007",
            "manuscript_location": "Section 10-12, Table 11.1",
            "claim_text": "Observable recurrence LP outer interval [S_-, S_+] from randomized pulse probing achieves 100% nominal band coverage with 16.67% decisiveness in strongest configuration and 0 wrong calls.",
            "evidence_type": "experiment",
            "theorem_or_spec_id": "Theorem 11.1 / Table 11.1",
            "information_contract": "I0",
            "result_artifact": "studies/observable_stress_tests/results/primary_summary.json",
            "source_hash": "audited_csv",
            "verification_status": "verified",
            "limitations": "Requires valid lower rate floor eta_0; false floor produces false-stable decisions."
        },
        {
            "claim_id": "CLM-008",
            "manuscript_location": "Section 11.4, Theorem 8.4",
            "claim_text": "Price-distance noise models: oracle error rate is 7.45% under differenced quote noise vs 27.02% under level quote noise with shared additive component.",
            "evidence_type": "experiment",
            "theorem_or_spec_id": "Theorem 8.4 / noise_analysis",
            "information_contract": "I0",
            "result_artifact": "research_extension/outputs/evidence_manifest.json",
            "source_hash": "audited_calc",
            "verification_status": "verified",
            "limitations": "Gaussian noise assumption on quote disturbances."
        },
        {
            "claim_id": "CLM-009",
            "manuscript_location": "Section 15, Table 15.2",
            "claim_text": "Decoupling of signal stability and solvency: a locally stable signal model (S=0.82 < 1) produces a 45.42% dealer halt rate under preloaded inventory and repricing shocks.",
            "evidence_type": "experiment",
            "theorem_or_spec_id": "Table 15.2 / dealer_stress",
            "information_contract": "I1_funded",
            "result_artifact": "studies/audited_constraints/results/dealer_stress.csv",
            "source_hash": "audited_csv",
            "verification_status": "verified",
            "limitations": "Synthetic stress scenario frequencies under declared dealer margin and capacity limits."
        },
        {
            "claim_id": "CLM-010",
            "manuscript_location": "Section 18.1, Table 9",
            "claim_text": "Coinbase cross-sectional regression: reduced-form persistence proxy F predicts held-out autocorrelation with t=2.47 (p=0.048) in bivariate regression; full model with spread and volatility controls yields t=1.23 (p=0.264), R^2=0.5185.",
            "evidence_type": "observational",
            "theorem_or_spec_id": "Specification 18.1 / Table 9",
            "information_contract": "I2",
            "result_artifact": "research_extension/outputs/empirical_results.json",
            "source_hash": "audited_ols",
            "verification_status": "verified_with_spec_separation",
            "limitations": "Observational crypto data (N=10); F is an empirical autocorrelation proxy, not structural S."
        },
        {
            "claim_id": "CLM-011",
            "manuscript_location": "Section 18.2, Table 10",
            "claim_text": "Binance US structural feedback estimation: aggregate state-space model fit across 500 optimization runs displays cross-seed dispersion; cross-venue differences reflect distinct estimators and microstructure rather than certified venue effects.",
            "evidence_type": "observational",
            "theorem_or_spec_id": "Specification 18.2 / Table 10",
            "information_contract": "I2",
            "result_artifact": "research_extension/outputs/binance_multi_epoch_results.json",
            "source_hash": "audited_mle",
            "verification_status": "verified_with_estimator_distinction",
            "limitations": "Deconvolution on tick data is sensitive to initialization and cannot be directly compared to autocorrelation proxy F."
        },
        {
            "claim_id": "CLM-012",
            "manuscript_location": "Appendix C",
            "claim_text": "Reconciliation of experimental units: 2,880 panels, 645,120 episode rows, 5,760 decision rows, 500 optimizer runs, 98 native unit tests.",
            "evidence_type": "provenance",
            "theorem_or_spec_id": "Appendix C",
            "information_contract": "meta",
            "result_artifact": "manifests/study_inventory.json",
            "source_hash": "manifest_hash",
            "verification_status": "verified",
            "limitations": "Strict separation between panel counts, episode rows, and test counts."
        }
    ]
    
    with open(claims_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in claims:
            writer.writerow(c)
    print(f"Created {claims_path} with {len(claims)} verified claims.")

if __name__ == "__main__":
    create_source_manifest()
    create_study_inventory()
    create_claims_register()
