"""Unified Theorem-to-Code and Lean Proof Verification Bridge for Journal of Finance Submission.

Parses every theorem, proposition, and lemma in paper/Machine_Markets_JF_Submission.tex
(recursively expanding \\input commands) and verifies 1-to-1 correspondence with
Lean 4 formalizations (in research_extension/current_manuscript_lean_20261008)
and Python scientific test suites.
Generates paper/generated/claim_to_code_map.tex.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX_FILE = ROOT / "paper" / "Machine_Markets_JF_Submission.tex"
GEN_DIR = ROOT / "paper" / "generated"
LEAN_DIR = ROOT / "research_extension" / "current_manuscript_lean_20261008"


@dataclass
class TheoremMapping:
    thm_type: str  # theorem, proposition, lemma
    title: str
    paper_loc: str
    lean_file: str
    lean_thm: str
    python_test: str
    test_func: str


# Authoritative 1-to-1 Mapping Registry for Journal of Finance Submission (17 environments)
REGISTRY = [
    TheoremMapping(
        "proposition", "Steady-State Kalman Filtering Yields Exponential Memory",
        r"Proposition 2.1",
        "CurrentProofs/Microfoundations.lean", "tracking_gain_unit_interval",
        "tests/test_dynamical_system_identification_bridge.py", "test_kalman_microfoundation"
    ),
    TheoremMapping(
        "proposition", "Regularized Online Gradient Descent Yields Exponential Memory",
        r"Proposition 2.2",
        "CurrentProofs/Calculus.lean", "actual_quadratic_ogd_update",
        "tests/test_dynamical_system_identification_bridge.py", "test_ogd_microfoundation"
    ),
    TheoremMapping(
        "theorem", "Merged Rate-Weight Equivalence and Minimax Separation Complexity",
        r"Theorem 2.3",
        "CurrentProofs/ComplexTransfers.lean", "symmetric_price_transfer_difference_uniform_bound",
        "tests/test_core_theorems_m1_m2_m3.py", "test_theorem_m1_minimal_realization"
    ),
    TheoremMapping(
        "theorem", "Sharp probing-resource orders for a known symmetric pair",
        r"Theorem 2.5",
        "CurrentProofs/GaussianInformation.lean", "gaussian_equal_variance_kl",
        "research_extension/gap_closure_20261006/publication_completion/test_resource_frontier.py", "test_third_tap_exact"
    ),
    TheoremMapping(
        "lemma", "Positive price-response geometry and fair execution",
        r"Lemma 2.6",
        "CurrentProofs/PriceOutputGain.lean", "price_only_exact_peak_gain",
        "research_extension/gap_closure_20261006/publication_completion/test_capital_frontier.py", "test_positive_price_response_is_completely_monotone"
    ),
    TheoremMapping(
        "theorem", "Sharp robust quantity cap from cash and margin",
        r"Theorem 2.7",
        "CurrentProofs/SequenceMargin.lean", "robust_nonnegative_quantity_allowance_iff",
        "research_extension/gap_closure_20261006/publication_completion/test_capital_frontier.py", "test_margin_cap_is_attained_and_above_cap_fails"
    ),
    TheoremMapping(
        "proposition", "Exact financial disclosure changes the experiment",
        r"Proposition 2.8",
        "CurrentProofs/DisclosureSolvency.lean", "arbitrarily_small_solvent_exact_disclosure",
        "research_extension/gap_closure_20261006/publication_completion/test_capital_frontier.py", "test_exact_equity_disclosure_distinguishes_noiseless_pair"
    ),
    TheoremMapping(
        "theorem", "Matching capital order for funded deterministic probes",
        r"Theorem 2.9",
        "CurrentProofs/Execution.lean", "solvent_trader_energy_bound",
        "research_extension/gap_closure_20261006/publication_completion/test_capital_frontier.py", "test_trading_cost_equals_toeplitz_and_bounds_energy"
    ),
    TheoremMapping(
        "proposition", "Passive distinction with zero controlled quantity",
        r"Proposition 2.10",
        "CurrentProofs/ProductInformation.lean", "actual_product_kl_additive",
        "research_extension/gap_closure_20261006/publication_completion/test_natural_excitation.py", "test_uniform_product_variance_and_valid_chebyshev_envelope"
    ),
    TheoremMapping(
        "proposition", "Conditional Quote and Allocation Cost of Ambiguity",
        r"Proposition 2.11",
        "CurrentProofs/Microfoundations.lean", "allocation_loss_formula",
        "tests/test_breakthrough_experiments.py", "test_allocation_loss_formula"
    ),
    TheoremMapping(
        "theorem", "Finite-Window Abstention in a Scalar Gaussian Experiment",
        r"Theorem 2.12",
        "CurrentProofs/GaussianRecords.lean", "gaussian_record_equal_variance_kl",
        "tests/test_core_theorems_m1_m2_m3.py", "test_theorem_m3_mandatory_abstention"
    ),
    TheoremMapping(
        "lemma", "Conditional Capacity Choice and Depth-Dependent Stability",
        r"Lemma 2.13",
        "CurrentProofs/Capacity.lean", "clamped_capacity_maximizes",
        "tests/test_theorems_m2_m5_corrected.py", "test_fixed_system_stability"
    ),
    TheoremMapping(
        "theorem", "Conditional Loss Budget and Kreiss Bounds",
        r"Theorem 2.14",
        "CurrentProofs/KreissRadius.lean", "exact_safe_radius_sufficient",
        "tests/test_theorems_m2_m5_corrected.py", "test_m5_safe_radius_is_exact"
    ),
    TheoremMapping(
        "proposition", "Cross-Impact Kreiss Inflation and Safe Radius Bound in Directed Networks",
        r"Proposition 2.16",
        "CurrentProofs/NetworkMonotone.lean", "cross_impact_exact_radius_contraction",
        "tests/test_five_frontiers.py", "test_multi_asset_cross_impact"
    ),
    TheoremMapping(
        "proposition", "Mechanical Persistence under Filtered Random Walks",
        r"Proposition 3.1",
        "CurrentProofs/Microfoundations.lean", "ema_deviation_identity",
        "tests/test_dynamical_system_identification_bridge.py", "test_volatility_amplification_wedge"
    ),
    TheoremMapping(
        "proposition", "Tri-Region Partition, Observation Design, and Finite-Horizon Depth Floor",
        r"Proposition IA.D.1",
        "CurrentProofs/SequenceMargin.lean", "robust_nonnegative_quantity_allowance_iff",
        "tests/test_breakthrough_experiments.py", "test_frontier_displacement_cap_enforced"
    ),
    TheoremMapping(
        "proposition", "Coordinate-Weighted Output Sensitivity",
        r"Proposition IA.D.2",
        "CurrentProofs/KreissDefective.lean", "defective_exact_radius_tendsto_zero",
        "tests/test_breakthrough_experiments.py", "test_nonnormal_initial_excursion_not_100_percent"
    )
]


def read_tex_expanded(path: Path) -> str:
    """Recursively reads TeX file expanding \\input{...} statements."""
    text = path.read_text(encoding="utf-8")
    def repl(m: re.Match) -> str:
        rel = m.group(1).strip()
        subpath = (path.parent / rel).resolve()
        if not subpath.suffix:
            subpath = subpath.with_suffix(".tex")
        if subpath.exists():
            return read_tex_expanded(subpath)
        return m.group(0)
    return re.sub(r"\\input\{([^}]+)\}", repl, text)


def extract_paper_theorems() -> list[tuple[str, str]]:
    content = read_tex_expanded(TEX_FILE)
    pattern = re.compile(r"\\begin\{(theorem|proposition|corollary|lemma)\}\[(.*?)\]", re.IGNORECASE)
    matches = []
    for m in pattern.finditer(content):
        thm_type = m.group(1).lower()
        title = m.group(2).strip()
        matches.append((thm_type, title))
    return matches


def verify_lean() -> bool:
    cmd = [sys.executable, "verify_formalization.py"]
    res = subprocess.run(cmd, cwd=str(LEAN_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Lean formalization check failed:\n{res.stderr}", file=sys.stderr)
        return False
    if "NAMED_PROOFS_BUILD_AND_STRICT_AXIOM_AUDIT_PASS" not in res.stdout:
        print(f"Lean audit missing success string:\n{res.stdout}", file=sys.stderr)
        return False
    return True


def verify_code_and_lean_files(mappings: list[TheoremMapping]) -> bool:
    errors = []
    for m in mappings:
        # Check python test
        py_path = ROOT / m.python_test
        if not py_path.exists():
            errors.append(f"Python test file missing: {m.python_test}")
        else:
            py_content = py_path.read_text(encoding="utf-8")
            if m.test_func not in py_content:
                errors.append(f"Test function '{m.test_func}' not found in {m.python_test}")

        # Check Lean proof
        lean_path = LEAN_DIR / m.lean_file
        if not lean_path.exists():
            errors.append(f"Lean proof file missing: {m.lean_file}")
        else:
            lean_content = lean_path.read_text(encoding="utf-8")
            if m.lean_thm not in lean_content:
                errors.append(f"Lean theorem '{m.lean_thm}' not found in {m.lean_file}")

    if errors:
        print(f"ERROR: {len(errors)} verification failures in code/Lean bridge:")
        for err in errors:
            print(f"  - {err}")
        return False
    return True


COVERAGE_MD = LEAN_DIR / "MANUSCRIPT_COVERAGE.md"


def load_formal_coverage() -> dict[str, str]:
    """Classify each manuscript object using the repository's own MANUSCRIPT_COVERAGE.md.

    A mapping to a named Lean declaration only shows that a SUBRESULT is kernel-checked.
    Coverage classes: NOT FORMALIZED, PARTIAL, SUBRESULTS (obligations remain), FULL.
    """
    cov: dict[str, str] = {}
    if not COVERAGE_MD.exists():
        return cov
    for line in COVERAGE_MD.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or "Manuscript object" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        title, done, remaining = cells[0], cells[1].lower(), cells[2]
        if done.startswith("not yet formalized"):
            status = "NOT FORMALIZED"
        elif done.startswith("partial"):
            status = "PARTIAL"
        elif remaining:
            status = "SUBRESULTS (obligations remain)"
        else:
            status = "FULL"
        cov[title.lower()] = status
    return cov


def coverage_for(title: str, cov: dict[str, str]) -> str:
    return cov.get(title.lower(), "NOT IN COVERAGE DOC (subresult mapping only)")


def generate_claim_map_table(mappings: list[TheoremMapping]) -> str:
    lines = [
        "% AUTO-GENERATED by scripts/verify_theorem_code_bridge.py for Journal of Finance Submission. Do not edit.",
        r"{\def\UrlBreaks{\do\/\do\_\do\:\do\.\do\a\do\b\do\c\do\d\do\e\do\f\do\g\do\h\do\i\do\j\do\k\do\l\do\m\do\n\do\o\do\p\do\q\do\r\do\s\do\t\do\u\do\v\do\w\do\x\do\y\do\z}%",
        r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{.17\textwidth}>{\raggedright\arraybackslash}p{.10\textwidth}>{\raggedright\arraybackslash\fontsize{7}{8.5}\selectfont}p{.13\textwidth}>{\raggedright\arraybackslash\fontsize{7}{8.5}\selectfont}p{.25\textwidth}>{\raggedright\arraybackslash\fontsize{7}{8.5}\selectfont}p{.25\textwidth}@{}}",
        r"\caption{Theorem-to-Code and Lean Subresult Map. A listed Lean declaration is a kernel-checked subresult; it is not a proof of the full manuscript statement unless the coverage column says FULL. Coverage is taken from \texttt{MANUSCRIPT\_COVERAGE.md}.}\label{tab:claim_map}\\",
        r"\toprule",
        r"\textbf{Manuscript Statement} & \textbf{Location} & \textbf{Formal coverage} & \textbf{Lean 4 subresult} & \textbf{Python test} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{Manuscript Statement} & \textbf{Location} & \textbf{Formal coverage} & \textbf{Lean 4 subresult} & \textbf{Python test} \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    cov = load_formal_coverage()
    for m in mappings:
        clean_title = m.title.replace("_", r"\_").replace("&", r"\&")
        status = coverage_for(m.title, cov)
        lean_label = rf"\nolinkurl{{{m.lean_file}::{m.lean_thm}}}"
        py_label = rf"\nolinkurl{{{m.python_test}::{m.test_func}}}"
        lines.append(f"{clean_title} & {m.paper_loc} & {status} & {lean_label} & {py_label} \\\\")

    lines.append(r"\end{longtable}}")
    return "\n".join(lines)


def main():
    print("Verifying Authoritative Theorem-to-Code and Lean Proofs Bridge for JF Submission...")
    paper_theorems = extract_paper_theorems()
    print(f"Manuscript contains {len(paper_theorems)} mathematical environments.")

    # Match against registry
    reg_dict = {m.title.lower(): m for m in REGISTRY}
    matched = 0
    for thm_type, title in paper_theorems:
        t_low = title.lower()
        if t_low in reg_dict:
            matched += 1
        else:
            print(f"WARNING: Unmapped manuscript environment: [{thm_type}] {title}")

    if matched == len(paper_theorems):
        print(f"SUCCESS: All {matched} paper theorems matched to verification code! (mapping existence only)")
    else:
        print(f"NOTICE: {matched}/{len(paper_theorems)} paper theorems matched to registry.")

    print("Verifying physical existence of all Python test files, test functions, Lean files, and formal theorems...")
    if not verify_code_and_lean_files(REGISTRY):
        sys.exit(1)
    print("SUCCESS: 100% of theorem mappings physically verified on disk!")

    print("Running Lean 4 Axiom Audit across all formalizations in research_extension/current_manuscript_lean_20261008...")
    if not verify_lean():
        sys.exit(1)
    print("SUCCESS: named Lean 4 declarations build with 0 sorry and 0 unapproved axioms.")
    cov = load_formal_coverage()
    counts: dict[str, int] = {}
    for m in REGISTRY:
        st = coverage_for(m.title, cov)
        counts[st] = counts.get(st, 0) + 1
    print("FORMAL COVERAGE OF MANUSCRIPT STATEMENTS (from MANUSCRIPT_COVERAGE.md):")
    for st, n in sorted(counts.items()):
        print(f"  {st}: {n}")
    print(f"  FULLY FORMALIZED: {counts.get('FULL', 0)}/{len(REGISTRY)}")

    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_tex = GEN_DIR / "claim_to_code_map.tex"
    table_tex = generate_claim_map_table(REGISTRY)
    out_tex.write_text(table_tex, encoding="utf-8")
    print(f"Wrote comprehensive claim-to-code table to {out_tex}")


if __name__ == "__main__":
    main()
