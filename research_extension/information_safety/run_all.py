"""Information-safety extension of Paper 2: all data-free tests. Writes results/<test>.json (one per test, with metadata) and
results/IS_results.json (all tests). Run: python3 run_all.py [TEST ...]   (deterministic seeds; about 6-10 minutes in total).

Test map (Paper 2 section 12 and Internet Appendix):
  T01 exact two-market witness               exact_rational_witness.run_witness        Example ex:witness
  T02 two-world capacity-loss bound          exact_rational_witness.run_two_world      Proposition prop:twoworld
  ThmB finite-window certification           data_compatibility.run_window_checks      Theorem thm:window
  T03 certification vs identification       uncertainty_calibration.run_sample_complexity   Theorem thm:certcost, Table tab:certvsid
  T04 coverage, width, abstention            monte_carlo_coverage.run_coverage         Theorem thm:certcost (i)
  T05 exact worst case (sign enumeration)    adversarial_paths.run_sign_enumeration    corrected gate (Section 6)
  T05b joint support function vs LP          adversarial_paths.run_lp_support          corrected gate, joint constraints
  T06 optimal guard vs brute force           robust_admission.run_optimizer_check      Theorem thm:robustguard
  T07 value of disclosure                    disclosure_experiment.run_disclosure      Theorem thm:disclosure
  T08 mechanism controls                     price_response.run_mechanisms             Section 12
  T09 misspecification                       monte_carlo_coverage.run_misspecification Section 12
  T10 certified numerical endpoints          data_compatibility.run_certified_numerics Lemma lem:certnum
  T11 unknown-covariance certificates        uncertainty_calibration.run_unknown_covariance_coverage  Proposition prop:hotelling
  T12 equilibrium rebate                     economic_ledger.run_rebate                Proposition prop:equil
  T12b balance-sheet step                    economic_ledger.run_balance_sheet         Theorem thm:forward
  T13 venue mode, interval branch and bound  robust_admission.run_venue_mode           Proposition prop:venue, Theorem thm:venuebb
  T14 anytime-valid probing                  adaptive_probing.run_probing              Proposition prop:probe
  T15 noisy-proxy disclosure, intersection   disclosure_experiment.run_disclosure_intersection  Theorem thm:disclosure (v)
"""
import hashlib, json, os, platform, sys, time
import numpy as np
import scipy, mpmath

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import exact_rational_witness as erw, data_compatibility as dc, uncertainty_calibration as uc, monte_carlo_coverage as mc
import adversarial_paths as ap, robust_admission as ra, disclosure_experiment as de, price_response as pr, economic_ledger as el
import adaptive_probing as prb
from model_contracts import CONTRACTS

OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
SRC = sorted(f for f in os.listdir(HERE) if f.endswith(".py"))
SRC_HASH = hashlib.sha256(b"".join(open(os.path.join(HERE, f), "rb").read() for f in SRC)).hexdigest()
META = {"code_sha256": SRC_HASH, "files": SRC, "python": platform.python_version(), "numpy": np.__version__,
        "scipy": scipy.__version__, "mpmath": mpmath.__version__, "data": "none (simulation and exact arithmetic only)"}

TESTS = [("T01_witness", None, "Example ex:witness", "D2/E01", "exact"),
         ("T02_two_world", None, "Proposition prop:twoworld", "D4/E02", "simulation, seed 2"),
         ("ThmB_window", dc.run_window_checks, "Theorem thm:window", "D6", "exact (60-digit)"),
         ("T03_sample_complexity", uc.run_sample_complexity, "Theorem thm:certcost; Table tab:certvsid", "D5", "computation"),
         ("T04_coverage", mc.run_coverage, "Theorem thm:certcost (i)", "D3/E03", "simulation, seed 4"),
         ("T05_exact_worst_case", ap.run_sign_enumeration, "corrected gate", "D1/E04", "exact enumeration, seed 5"),
         ("T05b_joint_support_lp", ap.run_lp_support, "corrected gate, joint constraints", "D1/E04", "LP, seed 51"),
         ("T06_optimizer", ra.run_optimizer_check, "Theorem thm:robustguard", "D7/E07", "brute force, seed 6"),
         ("T07_disclosure", de.run_disclosure, "Theorem thm:disclosure", "D9/E06", "simulation, seed 7"),
         ("T08_mechanisms", pr.run_mechanisms, "Section sec:simtests", "E08", "exact"),
         ("T09_misspecification", mc.run_misspecification, "Section sec:simtests", "E09", "simulation, seed 9"),
         ("T10_certified_numerics", dc.run_certified_numerics, "Lemma lem:certnum", "D8/E05", "outward-rounded interval arithmetic"),
         ("T11_unknown_covariance", uc.run_unknown_covariance_coverage, "Proposition prop:hotelling", "D8/E03", "simulation, seeds 20/60/200"),
         ("T12_equilibrium_rebate", el.run_rebate, "Proposition prop:equil", "E14", "computation"),
         ("T12b_balance_sheet", el.run_balance_sheet, "Theorem thm:forward", "D1", "simulation, seed 12"),
         ("T13_venue_mode", ra.run_venue_mode, "Proposition prop:venue; Theorem thm:venuebb", "D7/E05", "interval branch and bound, seed 13"),
         ("T14_probing", prb.run_probing, "Proposition prop:probe", "D10", "simulation"),
         ("T15_disclosure_intersection", de.run_disclosure_intersection, "Theorem thm:disclosure (v)", "hardening item 9", "simulation, seed 15")]


def main(only=None):
    R = {}; t_all = time.time(); SA = SB = None
    for name, fn, claim, blueprint, kind in TESTS:
        if only and name not in only and not (name == "T01_witness" and "T02_two_world" in only):
            continue
        t0 = time.time()
        if name == "T01_witness":
            res, SA, SB = erw.run_witness()
        elif name == "T02_two_world":
            if SA is None:
                _, SA, SB = erw.run_witness()
            res = erw.run_two_world(SA, SB)
        else:
            res = fn()
        R[name] = res
        status = ("PASS" if res["pass"] else "FAIL") if isinstance(res, dict) and "pass" in res else "REPORT"
        rec = {"test_id": name, "status": status, "paper_claim": claim, "blueprint": blueprint, "kind": kind,
               "runtime_seconds": round(time.time() - t0, 2), "meta": META, "result": res}
        json.dump(rec, open(os.path.join(OUT, f"{name}.json"), "w"), indent=2, default=float)
        print(f"[{status:6s}] {name:28s} {time.time() - t0:7.1f}s  {claim}")
    if not only:
        R["runtime_seconds"] = time.time() - t_all; R["meta"] = META; R["contracts"] = CONTRACTS
        json.dump(R, open(os.path.join(OUT, "IS_results.json"), "w"), indent=2, default=float)
    return R


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
