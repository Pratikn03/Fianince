# Complete End-to-End Reproduction Guide
## Machine Markets & The Agentic Market Invariant Protocol (AMIP RFC-001)

This repository provides an institutional-grade, zero-trust reproduction harness designed to verify all theoretical theorems, mechanized Lean 4 formal proofs, empirical microstructure calculations, and publication PDF artifacts with 100% reproducibility.

---

### Quickstart (3 Commands)

To run the complete audit, formal verification, test suite, and paper build:

```bash
# 1. Clone repository
git clone https://github.com/machine-markets/master-release.git && cd master-release

# 2. Setup Python environment
pip install -r requirements-runtime.txt -r requirements-artifacts.txt pypdf

# 3. Execute master reproduction
python reproduce.py --mode all
```

Or using `make`:
```bash
make reproduce
```

---

### System Requirements

| Component | Minimum | Recommended | Notes |
| :--- | :--- | :--- | :--- |
| **Operating System** | macOS 12+, Ubuntu 20.04+, Debian 11+, Windows WSL2 | Ubuntu 22.04 LTS or macOS Sonoma/Sequoia | Fully POSIX compatible |
| **CPU Architecture** | x86_64 or Apple Silicon (arm64) | 8+ CPU cores | Multi-core acceleration enabled |
| **RAM** | 8 GB | 16+ GB | Required for Level-3 LOB replay |
| **Disk Space** | 10 GB free | 25 GB free | Includes empirical CSV datasets |
| **Python** | 3.9, 3.10, 3.11, 3.12 | 3.11 or 3.12 | Tested across all minor versions |
| **Lean Toolchain** | Lean 4 (v4.14.0) via `elan` | Lean 4 (v4.14.0) | Automated via `lake` |
| **LaTeX Engine** | TeX Live 2022+ (`pdflatex`) | TeX Live Full | Required for PDF compilation |

---

### Three Ways to Reproduce

#### Option A: Native Python & Make (Recommended)

1. **Verify or install dependencies:**
   ```bash
   make setup
   ```
2. **Execute specific stages:**
   ```bash
   # Run all 170 mechanized Lean 4 formal proofs:
   make lean

   # Run all 548 automated pytest tests:
   make test

   # Run theorem-to-code mathematical bridge:
   make bridge

   # Run data integrity SHA-256 validation:
   make data

   # Benchmark AMIP RFC-001 AgenticGuard:
   make benchmark

   # Compile the 95-page publication volume:
   make paper
   ```

#### Option B: Containerized Docker Reproduction (Zero Setup)

If you do not have LaTeX or Lean 4 installed locally, you can run the entire pipeline inside an isolated Ubuntu OCI container:

```bash
# Build the container
docker compose build

# Execute fast verification:
docker compose up reproduce

# Execute full end-to-end audit:
docker compose up reproduce-all
```

#### Option C: Standalone Lean 4 Formal Proof Audit

To verify the mathematical proofs without running any Python code:

```bash
cd lean_proofs
lake build
lake env lean AxiomAudit.lean
```

**Expected Output:**
```
Audited 170 theorems in namespace MachineMarkets.
SUCCESS: ALL THEOREMS FULLY VERIFIED WITHOUT SORRY!
```

---

### The Eight Verification Stages

```mermaid
flowchart LR
    S1["1. Toolchain Audit"] --> S2["2. Data SHA-256 Check"]
    S2 --> S3["3. Lean 4 Formal Audit"]
    S3 --> S4["4. Theorem Bridge Map"]
    S4 --> S5["5. Provenance Ledger"]
    S5 --> S6["6. 548 Pytest Tests"]
    S6 --> S7["7. AMIP Benchmarks"]
    S7 --> S8["8. 95-Page Master PDF"]
```

1. **Stage 1: Toolchain Audit**  
   Detects host CPU architecture, Python version, Lean 4 / Lake compiler, and pdflatex binaries.
2. **Stage 2: Data SHA-256 Check**  
   Audits over 6.3 GB of real-world Level-3 order book and continuous 1-second bar datasets (`empirical_pipeline/data/`) against `empirical_pipeline/data_manifest.json`.
3. **Stage 3: Lean 4 Formal Audit**  
   Compiles and audits 170 mechanized theorems in namespace `MachineMarkets` across 9 formal modules (`Proofs/*.lean`), ensuring zero dependencies on `sorryAx`.
4. **Stage 4: Mathematical Bridge Verification**  
   Links every mathematical environment in the manuscript (Theorems 2.1–M5, Propositions 2.1–8.2) to corresponding Python test functions and Lean formal theorems.
5. **Stage 5: Provenance Claims Ledger**  
   Validates 63 empirical and structural numbers reported in the paper against raw numerical outputs in `results/provenance/`.
6. **Stage 6: Pytest Suite**  
   Executes 548 unit, integration, and stress tests spanning microfoundations, multi-dealer clearing, Hawkes processes, and the FIX 5.0 drop-copy supervisor.
7. **Stage 7: AMIP RFC-001 Benchmarking**  
   Measures `agentic_guard` interception latency (mean $< 45~\mu\text{s}$, P99 $< 200~\mu\text{s}$) and runs the 10-agent financial society crash test ($34.5\times$ drawdown reduction).
8. **Stage 8: Master PDF Compilation**  
   Runs two passes of `pdflatex` to build:
   - `paper/Machine_Markets_Final_Integrated_Paper.pdf` (64 pages)
   - `paper/Machine_Markets_Mathematical_Supplement.pdf` (31 pages)
   - `paper/Machine_Markets_Combined_Master.pdf` (95 pages)

---

### Generated Verification Artifacts

Upon completion of `python reproduce.py`, the following audit artifacts are written:

| Artifact Path | Format | Description |
| :--- | :--- | :--- |
| `results/provenance/reproduction_audit_report.json` | JSON | Machine-readable cryptographic audit log with timestamps, hardware specs, and stage statuses |
| `paper/generated/claim_to_code_map.tex` | LaTeX | Auto-generated table mapping all 26 paper theorems + 13 empirical systems to code |
| `results/provenance/ledger.md` | Markdown | Master provenance ledger tracking all 63 empirical paper claims |
| `paper/Machine_Markets_Combined_Master.pdf` | PDF | 95-page publication master volume uniting paper and mathematical supplement |

---

### Troubleshooting

- **LaTeX `pgfplots` / font error:** Ensure `cm-super` and `texlive-fonts-recommended` are installed (`sudo apt-get install cm-super texlive-latex-extra`).
- **Lean 4 version mismatch:** Install the exact pinned toolchain via `elan default leanprover/lean4:v4.14.0`.
- **Out of Memory on large CSVs:** All data loaders in `empirical_pipeline/` and `agentic_guard/` use streaming chunking (`chunk_size=65536` or iterator-based reading), maintaining peak memory $< 2~\text{GB}$.
