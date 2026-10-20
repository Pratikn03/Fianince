# Machine Markets & AMIP RFC-001: Master Engineering Makefile
# ==============================================================
# Top-tier institutional build and reproduction harness.

PYTHON ?= python3
PYTEST ?= pytest
LAKE ?= lake

.PHONY: all help setup test test-fast lean bridge provenance benchmark data paper reproduce paper-suite docker-build docker-run clean

all: reproduce

help:
	@echo "================================================================================"
	@echo " Machine Markets & AMIP RFC-001: Master Engineering Harness"
	@echo "================================================================================"
	@echo "Available Targets:"
	@echo "  make reproduce      One-click end-to-end master reproduction and audit"
	@echo "  make paper-suite    Clean end-to-end reproduction of the Oct 2026 papers (tests, results, LaTeX, ledger, Lean)"
	@echo "  make test           Run complete pytest suite (548 tests)"
	@echo "  make test-fast      Fast verification of theorem bridge and tests"
	@echo "  make lean           Compile and audit all 170 Lean 4 formal proofs (0 sorry)"
	@echo "  make bridge         Verify mathematical theorem-to-code bridge"
	@echo "  make provenance     Audit 63/63 empirical and structural provenance claims"
	@echo "  make benchmark      Benchmark AMIP RFC-001 agentic_guard latency and sandbox"
	@echo "  make data           Verify SHA-256 cryptographic hashes for empirical datasets"
	@echo "  make paper          Compile LaTeX manuscripts and 95-page master volume"
	@echo "  make docker-build   Build isolated Ubuntu OCI container image"
	@echo "  make docker-run     Execute reproduction inside Docker container"
	@echo "  make clean          Remove caches, pyc, and compilation artifacts"
	@echo "================================================================================"

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-runtime.txt -r requirements-artifacts.txt
	@echo "Environment setup complete."

test:
	PYTHONPATH=. $(PYTEST) tests/ -v

test-fast:
	PYTHONPATH=. $(PYTHON) reproduce.py --mode fast

lean:
	@echo "Building Lean 4 formal proofs package..."
	cd lean_proofs && $(LAKE) build
	@echo "Running Lean 4 Axiom Audit across all formalizations..."
	cd lean_proofs && $(LAKE) env lean AxiomAudit.lean

bridge:
	$(PYTHON) scripts/verify_theorem_code_bridge.py

provenance:
	$(PYTHON) scripts/provenance_ledger.py --check

benchmark:
	$(PYTHON) reproduce.py --mode benchmark

data:
	$(PYTHON) scripts/verify_data_integrity.py

paper:
	$(PYTHON) scripts/regenerate_all.py --no-recompute

reproduce:
	$(PYTHON) reproduce.py --mode all

docker-build:
	docker build -t machine-markets:latest .

docker-run:
	docker run --rm -v $$(pwd)/results:/workspace/results machine-markets:latest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf paper/*.aux paper/*.log paper/*.out paper/*.bbl paper/*.blg paper/*.toc paper/*.fls paper/*.fdb_latexmk

paper-suite:
	sh reproduce_paper_suite.sh
