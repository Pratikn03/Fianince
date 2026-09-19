# From Human Markets to Machine Markets
## Master research release 1.0 | 18 September 2026

**Start with [the integrated research paper](paper/Machine_Markets_Final_Integrated_Paper.pdf).**
The self-contained [LaTeX source](paper/Machine_Markets_Final_Integrated_Paper.tex) is beside it.
This package consolidates the original framework, all four complete computational study releases,
all their saved results and data, test suites, failure controls, and reproduction instructions.

**Scientific status:** model-conditioned mathematics and synthetic experiments. This is a final
consolidated package of the work currently available, not a claim that the research program is
finished, publication-ready, externally replicated, or a new finance paradigm. No additional
scientific experiment is introduced by this packaging edition.

## Read in this order
1. [Main paper](paper/Machine_Markets_Final_Integrated_Paper.pdf): framework, related work,
   proofs, all companion findings, measurement protocol, financial constraints, limitations,
   references, and a master-release appendix.
2. [Results and claim map](docs/RESULTS_AND_CLAIMS.md): what each result supports and where its
   exact data and code live. Do not pool different observation laws or repeated rows.
3. [Reproduction guide](docs/REPRODUCTION_GUIDE.md): verify files, run tests, rebuild a PDF,
   or reproduce complete studies in fresh copies.
4. [Requirements for the final scientific contribution](docs/FINAL_RESEARCH_REQUIREMENTS.md):
   evidence still needed before stronger claims are justified.

## Folder map
```text
Machine_Markets_Master_Release/
  README.md                         Start here
  START_HERE.html                   Offline clickable project index
  paper/                           Main PDF, self-contained TeX, edition notes
  studies/
    audited_constraints/           Current v0.5: full unmodified study
    observable_stress_tests/        v0.4: full unmodified study
    full_horizon_audit/             Full conventional-estimator comparison
    hidden_slow_learners/           Original exact construction and experiments
  original_framework/               Original 24-page framework, TeX, concept, roadmap
  docs/                            Result map, research gates, reproduction, prior reports
  verification/                    Fresh checks, source-file preservation, inventory
  tools/                           Portable verifier, test launcher, PDF build helper
  requirements-runtime.txt          Exact versions used for scientific verification
  requirements-artifacts.txt        Optional report/figure-building dependencies
  SHA256SUMS.txt                    Checksums for every other distributed file
```

Each study retains its original `src/`, `scripts/`, `tests/`, `configs/`, `data/`, `results/`,
`paper/`, or corresponding original structure. **Do not combine the different `src` packages.**
Run commands from the relevant study root; the master test launcher isolates them automatically.
The earlier scripts use `results/` for some measured data, so those files have not been moved.

## Quick checks (from this folder)
```bash
python tools/verify_master.py --strict
python -m pip install -r requirements-runtime.txt
python tools/run_all_tests.py
```
The checksum verifier requires only Python's standard library. The test suite requires the listed
packages; installing them may require network access. Experiments themselves require no API key,
financial account, GPU, live trade, or external market-data feed.

## Important preserved findings
The stronger conventional full-moment method resolves more cases than the original diagnostic,
with four high-noise confident errors retained. Observable order/price inference can remain mostly
inconclusive. An invalid hidden-memory assumption can defeat accurate measurement. The audited
endpoint design helps at smaller budgets but not the largest tested budget. Binding dealer and
funding constraints can cause operational failures even when isolated signal feedback is locally
stable. These findings are not silently replaced by the original broader vision.

## What “all results and data” means here
All files actually released in the four source archives are included, with member-level hashes.
This includes complete saved decision tables, released measurements, configurations, seeds,
selected full trajectories, ledgers and failure controls. Some earlier studies did not save every
raw trajectory: those remain regenerable from the released code and seeds, not falsely described
as newly stored raw data. No missing external market data or trained-agent experiment is implied.

The current study preserves an older ZIP under `provenance/`; it remains intact even though that
older study is also unpacked here for convenience. This deliberate duplication protects provenance.

## Checks performed for this master release
See [the fresh test report](verification/fresh_tests/test_report.json),
[standalone numerical checks](verification/fresh_verifiers/current_standalone_verification.json),
and [source preservation record](verification/SOURCE_ARCHIVES.json).
All 98 native scientific tests and 6 new packaging tests were run. The original 875 algebra checks
and the latest standalone verifier were rerun. Historical full-experiment rerun records are
preserved, but the large simulations were **not** repeated merely to consolidate this ZIP.

An internal alternate implementation and a fresh folder are not outside replication.
No author identity, institutional affiliation, endorsement, DOI or publication acceptance is implied.
See [authorship and reuse](docs/AUTHORSHIP_AND_REUSE.md).
