#!/usr/bin/env python3
"""
Audit name mappings for current numbered mathematical environments.
Missing and revised statements are explicitly reported; --require-complete
fails when those obligations remain. This script does not rebuild Lean.
A mapping is not semantic equivalence: what each declaration proves (full / conditional / arithmetic) is in COVERAGE.md.
A label may map to several declarations; all must exist and pass the axiom audit.

Checks both:
1. Mathlib real-analysis formalization (`research_extension/current_manuscript_lean_20261008/CurrentProofs/`)
2. Core Lean 4 constructive/rational formalization (`lean_proofs/Proofs/`)
"""

from pathlib import Path
import json
import re
import hashlib
import sys

# A retained label does not transfer semantic coverage to a revised statement.
REVISED_LABELS = {"prop:driftguard", "thm:forward", "prop:inventory_S", "thm:minphase",
                  "thm:window", "thm:certcost", "prop:esprit"}


def unmapped_record(idx, paper, env):
    return {"index": idx, "paper": paper, **env, "formalization_status": "UNMAPPED",
            "mathlib_theorem": "UNMAPPED", "mathlib_file": "", "mathlib_line": None,
            "axioms": [], "core_lean_theorem": "UNMAPPED", "core_lean_file": "",
            "core_lean_line": None}

SUITE_DIR = Path(__file__).resolve().parent
ROOT_DIR = SUITE_DIR.parent
MATHLIB_DIR = ROOT_DIR / "research_extension" / "current_manuscript_lean_20261008"
CORE_LEAN_DIR = ROOT_DIR / "lean_proofs"

PAPER1_FILES = [
    "p1_front.tex",
    "p1_ident.tex",
    "p1_account.tex",
    "p1_mixture.tex",
    "p1_disclosure.tex",
    "p1_empirics.tex",
    "p1_appendix.tex",
]

PAPER2_FILES = [
    "p2_front.tex",
    "p2_theory1.tex",
    "p2_t6.tex",
    "p2_infosafety.tex",
    "p2_guard.tex",
    "p2_disclosure.tex",
    "p2_equil.tex",
    "p2_evidence.tex",
    "p2_thin.tex",
    "p2_istests.tex",
    "p2_close.tex",
    "p2_appendix.tex",
]

PAPER1_MAP = {
    "lem:micro": (["p1_prop_kalman_memory", "p1_prop_ogd_memory"], ["p1_prop_kalman_memory", "p1_prop_ogd_memory"]),
    "lem:cm": ("p1_lem_cm_positive_response", "p1_lem_cm_positive_geometry"),
    "thm:merged": ("p1_thm_merged_equivalence_and_resolvent", "p1_thm_merged_equivalence"),
    "thm:quantity": ("p1_thm_quantity_sharp_orders", "p1_thm_quantity_orders"),
    "lem:toeplitz": ("p1_lem_toeplitz_fair_execution", "p1_lem_toeplitz_fair_execution"),
    "thm:cap": ("p1_thm_cap_counterparty_margin", "p1_thm_cap_robust_quantity"),
    "prop:disclosure": ("p1_prop_disclosure_third_mark", "p1_prop_disclosure_changes_experiment"),
    "thm:capital": ("p1_thm_capital_funded_probes", "p1_thm_capital_order"),
    "prop:passive0": ("p1_prop_passive0_three_step_blocks", "p1_prop_passive0_distinction"),
    "prop:tri": ("p1_prop_tri_region_partition", "p1_prop_tri_region_floor"),
    "thm:spectral": ("p1_thm_spectral_dissipation_bound", "p1_thm_spectral_dissipation"),
    "thm:adaptive": ("p1_thm_adaptive_sequential_bound", "p1_thm_adaptive_sequential"),
    "thm:rh": (["p1_thm_rh_duality", "is_rh_radius_bound", "is_rh_chain"], "p1_thm_rayleigh_holder_duality"),
    "cor:garch": ("p1_cor_garch_heteroskedastic_invariance", "p1_cor_garch_invariance"),
    "prop:crb": ("p1_prop_crb_benchmark", "p1_prop_crb_benchmark"),
    "thm:twocohort": ("p1_thm_twocohort_hankel_and_moment_gap", "p1_thm_twocohort_hankel"),
    "thm:kcohort": ("p1_thm_kcohort_lower_bound", "p1_thm_kcohort_lower_bound"),
    "prop:esprit": ("p1_thm_esprit_matching_upper_bound", "p1_prop_esprit_upper_bound"),
    "lem:altpair": ("p1_lem_altpair_moment_matched_wasserstein", "p1_lem_altpair_moment_matched"),
    "thm:general": ("p1_thm_general_memory_minimax", "p1_thm_general_memory_minimax"),
    "thm:minphase": ("p1_thm_minphase_passive_identification", "p1_thm_minphase_identification"),
    "prop:passive": ("p1_thm_passive_cost", "p1_prop_passive_cost"),
    "prop:tagged": (["p1_prop_tagged_flow_removes_barrier", "is_iv_det_pos"], "p1_prop_tagged_flow_ident"),
    "thm:discvalue": ("p1_thm_discvalue_ratio", "p1_thm_disclosure_value"),
    "thm:blind": ("p1_thm_blind_spectral_blindness", "p1_thm_spectral_blindness"),
    "thm:abstain": ("p1_thm_abstain_finite_window", "p1_thm_abstain_finite_window"),
}

PAPER2_MAP = {
    "prop:jury": ("p2_prop_jury_one_cohort", "p2_prop_jury_one_cohort"),
    "prop:invariance": ("p2_prop_input_output_invariance", "p2_prop_input_output_invariance"),
    "prop:inventory_S": ("p2_prop_inventory_S", "p2_prop_inventory_S"),
    "prop:ambig": ("p2_prop_ambig_quote_cost", "p2_prop_ambig_quote_cost"),
    "thm:radius": ("p2_thm_radius_kreiss", "p2_thm_radius_kreiss"),
    "prop:multi": ("p2_prop_multi_venue_cross_impact", "p2_prop_multi_venue_cross_impact"),
    "thm:peak": (["p2_thm_t6_amplification_condition", "p2_prop_shape_overshoot", "is_confluent_stationary",
                  "p2_prop_t6m_one_period_margin", "p2_thm_nomom_no_overshoot", "is_momentum_residues",
                  "p2_thm_noover_sufficient_condition"],
                 ["p2_thm_t6_amplification_condition", "p2_prop_shape_overshoot", "p2_prop_t6m_one_period_margin",
                  "p2_thm_nomom_no_overshoot", "p2_thm_noover_sufficient_condition"]),
    "thm:sum": (["p2_prop_sum_closed_form", "is_summed_response_closed_form"], "p2_prop_sum_closed_form"),
    "thm:guard": (["p2_thm_guard_maximal", "is_per_period_upper", "is_per_period_attained", "is_budget_upper",
                   "is_budget_attained"], "p2_thm_guard_maximal"),
    "lem:tail": ("p2_lem_tail_contraction", "p2_lem_tail_contraction"),
    "thm:robust": ("p2_thm_robust_gain", "p2_thm_robust_gain"),
    "thm:forward": (["p2_thm_forward_solvency", "is_buffer_after_step", "is_scenario"], "p2_thm_forward_solvency"),
    "prop:driftguard": ("p2_prop_driftguard", "p2_prop_driftguard"),
    "prop:dominance": ("p2_prop_dominance_guard_vs_eigenvalue", "p2_prop_dominance_guard_vs_eigenvalue"),
    "prop:lucas": ("p2_prop_lucas_reinforces_guard", "p2_prop_lucas_reinforces_guard"),
    "prop:equil": (["p2_prop_equil_transient_risk", "is_depth_solution_increasing", "is_depth_eq_lt_sp",
                    "is_depth_rebate_identified"], "p2_prop_equil_transient_risk"),
    "ex:witness": ("p2_ex_witness", "p2_ex_witness"),
    "prop:twoworld": (["p2_prop_twoworld", "is_two_world_capacity_loss", "is_two_world_attained"], "p2_prop_twoworld"),
    "thm:window": ("p2_thm_window", "p2_thm_window"),
    "thm:certcost": (["p2_thm_certcost", "is_iter_bound", "is_tail_bound"], "p2_thm_certcost"),
    "lem:sound": ("p2_lem_sound", "p2_lem_sound"),
    "thm:robustguard": (["p2_thm_robustguard", "is_robust_safe_set_eq", "is_alphaStar_isGreatest",
                         "is_infeasible_of_cI_neg"], "p2_thm_robustguard"),
    "thm:disclosure": (["p2_thm_disclosure", "is_disclosure_monotone", "is_disclosure_strict",
                        "is_intersection_admits_more"], "p2_thm_disclosure"),
    "lem:certnum": (["is_upper_bound", "is_lower_bound"], "p2_lem_certnum"),
    "prop:hotelling": (["is_corrSum_ge", "is_o1_margin_too_small"], "p2_prop_hotelling"),
    "prop:venue": (["is_unsafe_between", "is_worst_corner", "is_venue_example"], "p2_prop_venue"),
    "thm:venuebb": (["is_classify_safe_sound", "is_classify_unsafe_sound", "is_largest_safe_exists"], "p2_thm_venuebb"),
    "prop:probe": (["is_sequential_rule_correct"], "p2_prop_probe"),
}


def as_list(x):
    return list(x) if isinstance(x, (list, tuple)) else [x]


ENV_PATTERN = re.compile(
    r"\\begin\{(theorem|proposition|lemma|corollary|example)\}(?:\[([^\]]*)\])?\s*\\label\{([^}]+)\}",
    re.S,
)


def extract_envs(paper_dir: Path, files: list[str]) -> list[dict]:
    found = []
    for fname in files:
        fpath = paper_dir / fname
        text = fpath.read_text()
        for m in ENV_PATTERN.finditer(text):
            line = text[: m.start()].count("\n") + 1
            found.append(
                {
                    "env": m.group(1),
                    "title": (m.group(2) or "").strip(),
                    "label": m.group(3).strip(),
                    "file": fname,
                    "line": line,
                }
            )
    return found


def parse_lean_theorems(lean_path: Path) -> dict[str, int]:
    text = lean_path.read_text()
    assert not re.search(r"\b(sorry|admit|native_decide)\b", text), f"Forbidden token in {lean_path}"
    assert not re.search(r"^\s*(axiom|constant)\s", text, re.M), f"Forbidden axiom in {lean_path}"
    out = {}
    for m in re.finditer(r"^theorem\s+([A-Za-z0-9_]+)", text, re.M):
        out[m.group(1)] = text[: m.start()].count("\n") + 1
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p1_envs = extract_envs(SUITE_DIR / "paper1", PAPER1_FILES)
    p2_envs = extract_envs(SUITE_DIR / "paper2", PAPER2_FILES)

    assert p1_envs and p2_envs, "No manuscript environments extracted"

    mathlib_p1_path = MATHLIB_DIR / "CurrentProofs" / "CeilingSuitePaper1.lean"
    mathlib_p2_path = MATHLIB_DIR / "CurrentProofs" / "CeilingSuitePaper2.lean"
    core_p1_path = CORE_LEAN_DIR / "Proofs" / "CeilingSuitePaper1.lean"
    core_p2_path = CORE_LEAN_DIR / "Proofs" / "CeilingSuitePaper2.lean"

    mathlib_p1 = parse_lean_theorems(mathlib_p1_path)
    mathlib_p2 = parse_lean_theorems(mathlib_p2_path)
    ext_path = MATHLIB_DIR / "CurrentProofs" / "InfoSafetyExtensions.lean"
    ext_thms = parse_lean_theorems(ext_path)
    for k, v in ext_thms.items():
        mathlib_p2.setdefault(k, v)
        mathlib_p1.setdefault(k, v)
    core_p1 = parse_lean_theorems(core_p1_path)
    core_p2 = parse_lean_theorems(core_p2_path)

    checked_types = json.loads((MATHLIB_DIR / "checked_theorem_types.json").read_text())
    checked_by_name = {row["name"]: row for row in checked_types}

    records_p1 = []
    for idx, env in enumerate(p1_envs, 1):
        label = env["label"]
        if label not in PAPER1_MAP:
            records_p1.append(unmapped_record(idx, "Paper 1 (QE)", env))
            continue
        m_list, c_list = (as_list(x) for x in PAPER1_MAP[label])
        for m_thm in m_list:
            assert m_thm in mathlib_p1, f"Missing {m_thm} in {mathlib_p1_path} or {ext_path}"
            assert f"CurrentMM.{m_thm}" in checked_by_name, f"Missing CurrentMM.{m_thm} in checked_theorem_types.json"
        for c_thm in c_list:
            assert c_thm in core_p1, f"Missing {c_thm} in {core_p1_path}"
        records_p1.append(
            {
                "index": idx,
                "paper": "Paper 1 (QE)",
                **env,
                "formalization_status": "REQUIRES_SEMANTIC_REVIEW" if label in REVISED_LABELS else "NAME_MAPPING_ONLY",
                "mathlib_theorem": ", ".join(f"CurrentMM.{m}" for m in m_list),
                "mathlib_file": ", ".join(sorted({"CurrentProofs/InfoSafetyExtensions.lean" if m in ext_thms else "CurrentProofs/CeilingSuitePaper1.lean" for m in m_list})),
                "mathlib_line": mathlib_p1[m_list[0]],
                "axioms": sorted(set().union(*(checked_by_name[f"CurrentMM.{m}"]["axioms"] for m in m_list))),
                "core_lean_theorem": ", ".join(f"MachineMarkets.{c}" for c in c_list),
                "core_lean_file": "Proofs/CeilingSuitePaper1.lean",
                "core_lean_line": core_p1[c_list[0]],
            }
        )

    records_p2 = []
    for idx, env in enumerate(p2_envs, 1):
        label = env["label"]
        if label not in PAPER2_MAP:
            records_p2.append(unmapped_record(idx, "Paper 2 (JF)", env))
            continue
        m_list, c_list = (as_list(x) for x in PAPER2_MAP[label])
        for m_thm in m_list:
            assert m_thm in mathlib_p2, f"Missing {m_thm} in {mathlib_p2_path} or {ext_path}"
            assert f"CurrentMM.{m_thm}" in checked_by_name, f"Missing CurrentMM.{m_thm} in checked_theorem_types.json"
        for c_thm in c_list:
            assert c_thm in core_p2, f"Missing {c_thm} in {core_p2_path}"
        records_p2.append(
            {
                "index": idx,
                "paper": "Paper 2 (JF)",
                **env,
                "formalization_status": "REQUIRES_SEMANTIC_REVIEW" if label in REVISED_LABELS else "NAME_MAPPING_ONLY",
                "mathlib_theorem": ", ".join(f"CurrentMM.{m}" for m in m_list),
                "mathlib_file": ", ".join(sorted({"CurrentProofs/InfoSafetyExtensions.lean" if m in ext_thms else "CurrentProofs/CeilingSuitePaper2.lean" for m in m_list})),
                "mathlib_line": mathlib_p2[m_list[0]],
                "axioms": sorted(set().union(*(checked_by_name[f"CurrentMM.{m}"]["axioms"] for m in m_list))),
                "core_lean_theorem": ", ".join(f"MachineMarkets.{c}" for c in c_list),
                "core_lean_file": "Proofs/CeilingSuitePaper2.lean",
                "core_lean_line": core_p2[c_list[0]],
            }
        )

    bridge_defs = [
        ("foundational_result_A_impossibility", "Result A: Impossibility of Cohort-Specific Risk Control from Public Data"),
        ("foundational_result_B_disclosure_control", "Result B: Disclosure-Enabled Control Improvement"),
        ("foundational_result_C_probing_control_tradeoff", "Result C: Active Probing vs. Transient Excursion Tradeoff"),
    ]
    records_bridge = []
    for idx, (b_thm, b_title) in enumerate(bridge_defs, 1):
        assert b_thm in mathlib_p2, f"Missing {b_thm} in {mathlib_p2_path}"
        assert b_thm in core_p2, f"Missing {b_thm} in {core_p2_path}"
        full_m_name = f"CurrentMM.{b_thm}"
        assert full_m_name in checked_by_name, f"Missing {full_m_name} in checked_theorem_types.json"
        records_bridge.append(
            {
                "index": idx,
                "paper": "Phase 7 Foundational Bridge",
                "title": b_title,
                "mathlib_theorem": full_m_name,
                "mathlib_file": "CurrentProofs/CeilingSuitePaper2.lean",
                "mathlib_line": mathlib_p2[b_thm],
                "axioms": checked_by_name[full_m_name]["axioms"],
                "core_lean_theorem": f"MachineMarkets.{b_thm}",
                "core_lean_file": "Proofs/CeilingSuitePaper2.lean",
                "core_lean_line": core_p2[b_thm],
            }
        )

    current = records_p1 + records_p2
    missing = [r["label"] for r in current if r["formalization_status"] == "UNMAPPED"]
    revised = [r["label"] for r in current if r["formalization_status"] == "REQUIRES_SEMANTIC_REVIEW"]
    mapped_p1 = sum(r["formalization_status"] != "UNMAPPED" for r in records_p1)
    mapped_p2 = sum(r["formalization_status"] != "UNMAPPED" for r in records_p2)
    manifest = {
        "status": "MAPPING_AUDIT_INCOMPLETE" if missing or revised else "NAME_MAPS_CHECKED_SEE_SEMANTIC_COVERAGE",
        "unmapped_labels": missing,
        "revised_labels_requiring_semantic_review": revised,
        "fresh_lean_build_performed": False,
        "lean_toolchain": "leanprover/lean4:v4.34.1",
        "paper1_total_environments": len(records_p1),
        "paper2_total_environments": len(records_p2),
        "foundational_bridge_theorems": len(records_bridge),
        "total_ceiling_suite_environments": len(records_p1) + len(records_p2),
        "total_existing_name_mappings": mapped_p1 + mapped_p2,
        "sha256": {
            "CurrentProofs/CeilingSuitePaper1.lean": sha256(mathlib_p1_path),
            "CurrentProofs/CeilingSuitePaper2.lean": sha256(mathlib_p2_path),
            "CurrentProofs/InfoSafetyExtensions.lean": sha256(ext_path),
            "Proofs/CeilingSuitePaper1.lean": sha256(core_p1_path),
            "Proofs/CeilingSuitePaper2.lean": sha256(core_p2_path),
        },
        "paper1": records_p1,
        "paper2": records_p2,
        "foundational_bridge": records_bridge,
    }

    manifest_path = SUITE_DIR / "CEILING_SUITE_LEAN_PROOF_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    md_lines = [
        "# Ceiling Suite — Lean declaration mapping audit",
        "",
        f"- **Status**: {manifest['status']}. Existing declaration references checked; no fresh Lean build or full semantic equivalence is claimed.",
        f"- **Unmapped labels**: {', '.join(missing) or 'none'}",
        f"- **Revised statements requiring semantic review**: {', '.join(revised) or 'none'}",
        "- **Lean Toolchain**: `leanprover/lean4:v4.34.1`",
        f"- **Paper 1**: {mapped_p1} / {len(records_p1)} current formal environments have an existing name mapping.",
        f"- **Paper 2**: {mapped_p2} / {len(records_p2)} current formal environments have an existing name mapping.",
        "- Run with `--require-complete` to fail if unmapped or revised statements remain. A successful default run means the audit was generated, not that manuscript formalization is complete.",
        "",
        "## Paper 1 — Auditable Memory and Financial Identification Limits (`paper1/`)",
        "",
        "| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records_p1:
        md_lines.append(
            f"| {r['index']} | `{r['env']}` | `{r['label']}` | {r['title']} | `{r['file']}:{r['line']}` | `{r['mathlib_theorem']}` (L{r['mathlib_line']}) | `{r['core_lean_theorem']}` (L{r['core_lean_line']}) |"
        )

    md_lines.extend(
        [
            "",
            "## Paper 2 — Transient Amplification & Summed-Gain Guard (`paper2/`)",
            "",
            "| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for r in records_p2:
        md_lines.append(
            f"| {r['index']} | `{r['env']}` | `{r['label']}` | {r['title']} | `{r['file']}:{r['line']}` | `{r['mathlib_theorem']}` (L{r['mathlib_line']}) | `{r['core_lean_theorem']}` (L{r['core_lean_line']}) |"
        )

    md_lines.extend(
        [
            "",
            "## Phase 7 — Unified Foundational Bridge Theorems (Paper 1 ↔ Paper 2)",
            "",
            "| # | Result | Title | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |",
            "|---|---|---|---|---|",
        ]
    )
    for r in records_bridge:
        md_lines.append(
            f"| {r['index']} | `Result {chr(64+r['index'])}` | {r['title']} | `{r['mathlib_theorem']}` (L{r['mathlib_line']}) | `{r['core_lean_theorem']}` (L{r['core_lean_line']}) |"
        )

    report_path = SUITE_DIR / "CEILING_SUITE_LEAN_PROOF_REPORT.md"
    report_path.write_text("\n".join(md_lines) + "\n")
    print(f"[AUDIT] {mapped_p1 + mapped_p2}/{len(current)} existing name mappings; "
          f"{len(missing)} unmapped; {len(revised)} revised statements require semantic review. No fresh Lean build.")
    if "--require-complete" in sys.argv and (missing or revised):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
