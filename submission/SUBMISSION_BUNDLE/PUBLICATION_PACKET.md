# Publication Packet & Master Submission Checklist

**Manuscript Title:** *From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints*  
**Authors:** Pratik Niroula and Prashant Niroula  
**Canonical Master Artifact:** `Machine_Markets_Combined_Master.pdf` (124 pages total)  
**Main Manuscript:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (80 pages)  
**Mathematical Supplement:** `paper/Machine_Markets_Mathematical_Supplement.pdf` (44 pages)  
**Formal Verification:** 216 Lean 4 Theorems verified with 0 `sorry` (`lean_proofs/AxiomAudit.lean`)  
**Provenance Ledger:** 80 / 80 Claims Verified (`scripts/provenance_ledger.py`)  
**Test Suite:** 622 / 622 Tests Passing (`pytest tests/`)  
**Canonical Benchmark Data:** FI-2010 NASDAQ Nordic L2 (`empirical_pipeline/fi2010/data/data.csv`, SHA-256: `0fac513a408b4dd803373860831874d3423a89f41fbaf13323f8a25a3019f3eb`, CC0 1.0)  

---

## 1. Submission Artifact Inventory

| Artifact | File Path | Format / Size | Status |
| :--- | :--- | :--- | :--- |
| **Combined Master Volume** | `Machine_Markets_Combined_Master.pdf` | PDF (124 pp.) | Verified (0 warnings) |
| **Main Manuscript** | `paper/Machine_Markets_Final_Integrated_Paper.pdf` | PDF (80 pp.) | Verified (0 undefined refs) |
| **Online Mathematical Supplement** | `paper/Machine_Markets_Mathematical_Supplement.pdf` | PDF (44 pp.) | Verified (0 undefined refs) |
| **Formal Lean 4 Suite** | `lean_proofs/Proofs/` | 11 submodules | 216 Theorems, 0 sorry |
| **Lean 4 Axiom Audit** | `lean_proofs/AxiomAudit.lean` | Lean 4 script | 100% sound (0 axioms) |
| **Theorem-Code Bridge** | `scripts/verify_theorem_code_bridge.py` | Python 3.11 | 36 / 36 Environments Mapped |
| **Provenance Claims Ledger** | `scripts/provenance_ledger.py` | Python 3.11 | 80 / 80 Claims Verified |
| **Hardware Core (C++20 SIMD)** | `agentic_guard/hardware/amip_fast_kernel.hpp` | C++20 Header | 7.7 ns mean latency |
| **Hardware Core (FPGA RTL)** | `agentic_guard/hardware/amip_fpga_pipeline.v` | Verilog RTL | 20.0 ns, 400 MHz, 4 stages |
| **Cover Letter** | `submission/COVER_LETTER.md` | Markdown / Text | Submission Ready |
| **Authorship & Disclosures** | `submission/DISCLOSURES.md` | Markdown / Text | Submission Ready |
| **Replication Guide** | `README.md` & `reproduce.py` | Python CLI | One-Click Reproducible |

---

## 2. Epistemic & Methodological Integrity Checklist

- [x] **Canonical Dataset Provenance:** FI-2010 NASDAQ Nordic benchmark dataset explicitly distinguished from earlier withdrawn synthetic 2SLS analyses (`archive/withdrawn_20261003/`). File hash SHA-256 `0fac513a408b4dd803373860831874d3423a89f41fbaf13323f8a25a3019f3eb` and CC0 1.0 license cited directly.
- [x] **Disciplined Epistemics:** All universal/unhedged causal claims replaced with precise, qualified mechanism statements (e.g., state-dependent persistence across regimes; passive touch-pegged limit orders; simulated multi-clearinghouse contraction).
- [x] **Active Literature Lineage:** Table 2 (`tab:lineage`) and text actively link all classical foundations: Kalman (1960), Gilbert (1963), Ho & Kalman (1966), Le Cam (1973), Chen (1995), Heinrich & Kahn (2018), Wu & Yang (2020), Chow (1970), Herbei & Wegkamp (2006), Geifman & El-Yaniv (2017), Milanese & Vicino (1991), Calafiore & Campi (2005), Kreiss (1962), Spijker (1991), Trefethen & Embree (2005), Hasbrouck (1991), Cont et al. (2010, 2014), Eisenberg & Noe (2001), and Glasserman & Young (2015).
- [x] **Zero Undefined Citations / References:** Both `Machine_Markets_Final_Integrated_Paper.tex` and `Machine_Markets_Mathematical_Supplement.tex` compile cleanly with 0 undefined citations and 0 undefined cross-references.
- [x] **Full Lean 4 Mechanization:** All 216 theorems in `lean_proofs/Proofs/` verified with 0 `sorry` and audited via `lean_proofs/AxiomAudit.lean`.
- [x] **100% Passing Test Suite:** Full pytest suite (622/622 tests) passes in ~60 seconds.

---

## 3. Venue Decision & Submission Record

```text
Target Journal:       The Review of Financial Studies / Journal of Financial Economics
Manuscript Type:      Research Article + Online Mathematical Appendix
Version Submitted:    v1.0-master-release
Submission Date:      October 2026
Combined Master:      Machine_Markets_Combined_Master.pdf (124 pages)
Main Paper:           paper/Machine_Markets_Final_Integrated_Paper.pdf (80 pages)
Supplement:           paper/Machine_Markets_Mathematical_Supplement.pdf (44 pages)
Reproducibility:      One-Click Verified (scripts/regenerate_all.py --no-recompute)
Formal Proofs:        Lean 4 (216 Theorems, 0 sorry)
Review Status:        SUBMISSION_READY; FORMALLY_VERIFIED
```
